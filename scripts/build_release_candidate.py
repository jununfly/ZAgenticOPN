#!/usr/bin/env python3
"""Build a versioned, source-independent ZAgenticOPN release candidate.

The output is intentionally a plain release directory plus a tarball. The
runtime is a stdlib zipapp so this first RC can be built on the current macOS
host without adding a package-build dependency.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipapp
from pathlib import Path
from typing import Any


VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
MANIFEST_SCHEMA = "zagenticopn.release-manifest.v1"
ACTIVATION_SCHEMA = "zagenticopn.activation.v1"
RECEIPT_SCHEMA = "zagenticopn.activation.receipt.v1"
RUNTIME_CONFIG_SCHEMA = "zagenticopn.runtime-config.v1"
STORAGE_SCHEMA = "sqlite-v1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="release id, for example 0.1.0-rc.1")
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="directory that will receive the release directory and tarball",
    )
    args = parser.parse_args(argv)
    if not VERSION_RE.fullmatch(args.version):
        parser.error("--version must contain only letters, numbers, dot, underscore, or hyphen")

    repo_root = Path(__file__).resolve().parents[1]
    output_root = args.output.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    release_name = f"ZAgenticOPN-{args.version}-{_platform_tag()}"
    release_dir = output_root / release_name
    if release_dir.exists():
        raise SystemExit(f"release directory already exists: {release_dir}")
    release_dir.mkdir()

    with tempfile.TemporaryDirectory(prefix="zagenticopn-release-") as temp_name:
        staging = Path(temp_name)
        runtime_stage = staging / "runtime"
        package_stage = runtime_stage / "zagentic_opn"
        _copy_tree(repo_root / "zagentic_opn", package_stage)
        _set_release_version(package_stage / "release_info.py", args.version)
        (runtime_stage / "__main__.py").write_text(
            "from zagentic_opn.__main__ import _main\n\n"
            "raise SystemExit(_main())\n",
            encoding="utf-8",
        )

        runtime_dir = release_dir / "runtime"
        runtime_dir.mkdir()
        runtime_path = runtime_dir / "zagenticopn.pyz"
        zipapp.create_archive(
            str(runtime_stage),
            str(runtime_path),
            interpreter="/usr/bin/env python3",
            compressed=True,
        )
        runtime_path.chmod(0o755)

    plugin_source = repo_root / "integrations" / "workbuddy"
    plugin_destination = release_dir / "host-integration" / "workbuddy"
    _copy_tree(plugin_source, plugin_destination)
    _set_plugin_version(plugin_destination / ".codebuddy-plugin" / "plugin.json", args.version)
    marketplace_name = f"zagenticopn-release-{args.version}"
    marketplace_manifest = release_dir / "host-integration" / ".codebuddy-plugin" / "marketplace.json"
    marketplace_manifest.parent.mkdir(parents=True, exist_ok=True)
    marketplace_manifest.write_text(
        json.dumps(
            {
                "name": marketplace_name,
                "description": f"ZAgenticOPN {args.version} host integration release.",
                "owner": {"name": "ZAgenticOPN"},
                "plugins": [
                    {
                        "name": "zagenticopn-agent-integration",
                        "description": "Version-matched WorkBuddy activation integration.",
                        "version": args.version,
                        "source": "./workbuddy",
                        "license": "MIT",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    shutil.copy2(repo_root / "scripts" / "install_release.py", release_dir / "install_release.py")
    (release_dir / "INSTALL.md").write_text(_install_notes(args.version), encoding="utf-8")

    source_commit, source_tree_dirty = _git_state(repo_root)
    manifest: dict[str, Any] = {
        "manifest_schema": MANIFEST_SCHEMA,
        "product": "ZAgenticOPN",
        "release_id": args.version,
        "platform": _platform_tag(),
        "source_commit": source_commit,
        "source_tree_dirty": source_tree_dirty,
        "runtime": {
            "path": "runtime/zagenticopn.pyz",
            "launcher": "bin/zagenticopn",
            "interpreter": "/usr/bin/env python3",
            "requires_python": ">=3.9",
        },
        "host_integration": {
            "path": "host-integration/workbuddy",
            "plugin_name": "zagenticopn-agent-integration",
            "version": args.version,
            "marketplace_name": marketplace_name,
            "marketplace_path": "host-integration",
        },
        "contracts": {
            "activation": ACTIVATION_SCHEMA,
            "receipt": RECEIPT_SCHEMA,
            "runtime_config": RUNTIME_CONFIG_SCHEMA,
            "storage": STORAGE_SCHEMA,
        },
    }
    manifest["files"] = _file_hashes(release_dir)
    (release_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    archive_path = output_root / f"{release_name}.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(release_dir, arcname=release_dir.name)
    print(
        json.dumps(
            {
                "status": "built",
                "release_dir": str(release_dir),
                "archive": str(archive_path),
                "release_id": args.version,
                "platform": _platform_tag(),
                "source_commit": manifest["source_commit"],
                "source_tree_dirty": manifest["source_tree_dirty"],
                "file_count": len(manifest["files"]),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def _copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, ignore=_ignore_generated)


def _ignore_generated(directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name == "__pycache__" or name.endswith(".pyc") or name.endswith(".pyo")
    }


def _set_release_version(path: Path, version: str) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('PRODUCT_VERSION = "0.1.0-dev"', f'PRODUCT_VERSION = "{version}"'), encoding="utf-8")


def _set_plugin_version(path: Path, version: str) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["version"] = version
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _file_hashes(root: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative == "manifest.json":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append({"path": relative, "sha256": digest})
    return entries


def _git_state(repo_root: Path) -> tuple[str | None, bool]:
    try:
        commit_result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        status_result = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None, True
    return commit_result.stdout.strip() or None, bool(status_result.stdout.strip())


def _platform_tag() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "darwin":
        return f"macos-{machine}"
    return f"{system}-{machine}"


def _install_notes(version: str) -> str:
    return f"""# ZAgenticOPN {version} release candidate

This bundle is a user-side release candidate. It does not require a
ZAgenticOPN checkout in the consuming project.

Install into a clean user product root and register the host plugin through the
WorkBuddy/CodeBuddy host CLI with:

```sh
python3 install_release.py install \\
  --bundle . \\
  --product-root "$HOME/Library/Application Support/zagenticopn" \\
  --host-cli /Applications/WorkBuddy.app/Contents/Resources/app.asar.unpacked/cli/dist/codebuddy.js \\
  --host-config-dir "$HOME/.workbuddy" \\
  --host-cli-node node
```

The installer registers the release's directory marketplace at its immutable
user-side versions/<release-id> path, then installs the plugin at user scope.
It keeps runtime, config, SQLite data, backups and consuming projects separate.
"""


if __name__ == "__main__":
    raise SystemExit(main())
