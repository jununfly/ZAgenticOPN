#!/usr/bin/env python3
"""Install, inspect, and roll back a ZAgenticOPN release bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA = "zagenticopn.release-manifest.v1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="operation", required=True)

    install = subparsers.add_parser("install")
    install.add_argument("--bundle", type=Path, required=True)
    install.add_argument("--product-root", type=Path, default=_default_product_root())
    _add_host_options(install)
    install.add_argument(
        "--allow-dirty",
        action="store_true",
        help="allow a dirty source-tree bundle for fixtures; formal installs reject it",
    )

    doctor = subparsers.add_parser("doctor")
    doctor.add_argument("--product-root", type=Path, default=_default_product_root())
    _add_host_options(doctor)

    rollback = subparsers.add_parser("rollback")
    rollback.add_argument("--product-root", type=Path, default=_default_product_root())
    _add_host_options(rollback)
    rollback.add_argument("--to", dest="release_id", required=True)

    args = parser.parse_args(argv)
    try:
        if args.operation == "install":
            result = _install(
                args.bundle,
                args.product_root,
                args.host_cli,
                args.host_cli_node,
                args.host_config_dir,
                args.host_plugin_root,
                args.allow_dirty,
            )
        elif args.operation == "doctor":
            result = _doctor(
                args.product_root,
                args.host_cli,
                args.host_cli_node,
                args.host_config_dir,
                args.host_plugin_root,
            )
        else:
            result = _rollback(
                args.product_root,
                args.host_cli,
                args.host_cli_node,
                args.host_config_dir,
                args.host_plugin_root,
                args.release_id,
            )
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(
            json.dumps(
                {"status": "invalid_release_operation", "error": {"type": type(error).__name__, "message": str(error)}},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


def _install(
    bundle: Path,
    product_root: Path,
    host_cli: str | None,
    host_cli_node: str,
    host_config_dir: Path | None,
    host_plugin_root: Path | None,
    allow_dirty: bool,
) -> dict[str, Any]:
    bundle = bundle.expanduser().resolve()
    product_root = product_root.expanduser().resolve()
    host_config_dir = _resolve_optional_path(host_config_dir)
    host_plugin_root = _resolve_optional_path(host_plugin_root)
    manifest = _load_and_verify_bundle(bundle, allow_dirty=allow_dirty)
    release_id = _safe_release_id(manifest["release_id"])
    versions = product_root / "versions"
    target = versions / release_id
    if target.exists():
        raise ValueError(f"release is already installed: {target}")
    product_root.mkdir(parents=True, exist_ok=True)
    for directory in (versions, product_root / "data", product_root / "backups", product_root / "logs"):
        directory.mkdir(parents=True, exist_ok=True)

    temporary = versions / f".{release_id}.installing-{os.getpid()}"
    if temporary.exists():
        raise ValueError(f"stale install directory exists: {temporary}")
    shutil.copytree(bundle / "runtime", temporary / "runtime")
    shutil.copytree(bundle / "host-integration", temporary / "host-integration")
    shutil.copy2(bundle / "manifest.json", temporary / "manifest.json")
    (temporary / "bin").mkdir()
    launcher = temporary / "bin" / "zagenticopn"
    launcher.symlink_to(Path("..") / "runtime" / "zagenticopn.pyz")
    os.replace(temporary, target)

    current = product_root / "current"
    if current.is_symlink():
        _backup_user_state(product_root)
    host_registration = _register_host(
        target,
        manifest,
        host_cli,
        host_cli_node,
        host_config_dir,
        host_plugin_root,
        product_root / "backups",
    )
    _switch_current(product_root, target)
    installed_record = {
        "manifest_schema": MANIFEST_SCHEMA,
        "active_release": release_id,
        "installed_release": release_id,
        "installed_at": str(time.time()),
        "product_root": str(product_root),
        "host_registration": host_registration,
    }
    (product_root / "install-manifest.json").write_text(
        json.dumps(installed_record, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "status": "installed",
        "release_id": release_id,
        "product_root": str(product_root),
        "current": str(product_root / "current"),
        "host_registration": host_registration,
    }


def _doctor(
    product_root: Path,
    host_cli: str | None,
    host_cli_node: str,
    host_config_dir: Path | None,
    host_plugin_root: Path | None,
) -> dict[str, Any]:
    product_root = product_root.expanduser().resolve()
    host_config_dir = _resolve_optional_path(host_config_dir)
    host_plugin_root = _resolve_optional_path(host_plugin_root)
    current = product_root / "current"
    if not current.is_symlink():
        raise ValueError(f"current release pointer is missing: {current}")
    target = current.resolve(strict=True)
    manifest = _load_manifest(target / "manifest.json")
    launcher = target / manifest["runtime"]["path"]
    if not launcher.is_file():
        raise ValueError(f"runtime is missing: {launcher}")
    if not os.access(launcher, os.X_OK):
        raise ValueError(f"runtime is not executable: {launcher}")
    version = subprocess.run(
        [str(launcher), "--version"], check=True, capture_output=True, text=True, timeout=10
    ).stdout.strip()
    if version != manifest["release_id"]:
        raise ValueError(f"runtime version mismatch: {version} != {manifest['release_id']}")
    host_registration: dict[str, Any] | None = None
    if host_cli is not None:
        host_registration = _verify_host_registration(
            target, manifest, host_cli, host_cli_node, host_config_dir
        )
    elif host_plugin_root is not None:
        plugin_manifest = _load_manifest(host_plugin_root / ".codebuddy-plugin" / "plugin.json")
        if plugin_manifest.get("version") != manifest["release_id"]:
            raise ValueError("host plugin and runtime release versions do not match")
    return {
        "status": "healthy",
        "release_id": manifest["release_id"],
        "runtime": str(launcher),
        "product_root": str(product_root),
        "host_plugin_root": str(host_plugin_root) if host_plugin_root is not None else None,
        "host_registration": host_registration,
    }


def _rollback(
    product_root: Path,
    host_cli: str | None,
    host_cli_node: str,
    host_config_dir: Path | None,
    host_plugin_root: Path | None,
    release_id: str,
) -> dict[str, Any]:
    product_root = product_root.expanduser().resolve()
    host_config_dir = _resolve_optional_path(host_config_dir)
    host_plugin_root = _resolve_optional_path(host_plugin_root)
    target = product_root / "versions" / _safe_release_id(release_id)
    if not target.is_dir():
        raise ValueError(f"installed release not found: {target}")
    manifest = _load_manifest(target / "manifest.json")
    host_registration = _register_host(
        target,
        manifest,
        host_cli,
        host_cli_node,
        host_config_dir,
        host_plugin_root,
        product_root / "backups",
    )
    _switch_current(product_root, target)
    return {
        "status": "rolled_back",
        "release_id": manifest["release_id"],
        "current": str(product_root / "current"),
        "host_registration": host_registration,
    }


def _load_and_verify_bundle(bundle: Path, *, allow_dirty: bool = False) -> dict[str, Any]:
    manifest = _load_manifest(bundle / "manifest.json")
    if manifest.get("manifest_schema") != MANIFEST_SCHEMA:
        raise ValueError("unsupported release manifest schema")
    if manifest.get("source_tree_dirty") is not False and not allow_dirty:
        raise ValueError("formal install requires a clean source tree")
    entries = manifest.get("files", [])
    if not isinstance(entries, list):
        raise ValueError("release manifest files must be a list")
    declared: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ValueError("release manifest contains an invalid file entry")
        relative = Path(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"unsafe release file path: {relative}")
        if relative.as_posix() in declared:
            raise ValueError(f"release manifest contains a duplicate file: {relative}")
        declared.add(relative.as_posix())
        path = bundle / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"release file is missing: {relative}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"release checksum mismatch: {relative}")
    actual = {
        path.relative_to(bundle).as_posix()
        for path in bundle.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    if actual != declared:
        raise ValueError("release file set does not match its manifest")
    return manifest


def _add_host_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--host-cli",
        help="official WorkBuddy/CodeBuddy CLI executable or JavaScript entrypoint",
    )
    parser.add_argument(
        "--host-cli-node",
        default="node",
        help="Node executable used when --host-cli points to a JavaScript entrypoint",
    )
    parser.add_argument(
        "--host-config-dir",
        type=Path,
        default=_default_host_config_dir(),
        help="host user config directory; WorkBuddy defaults to ~/.workbuddy",
    )
    parser.add_argument(
        "--host-plugin-root",
        type=Path,
        help="development/fixture fallback; formal installs should use --host-cli",
    )


def _resolve_optional_path(path: Path | None) -> Path | None:
    return path.expanduser().resolve() if path is not None else None


def _register_host(
    target: Path,
    manifest: dict[str, Any],
    host_cli: str | None,
    host_cli_node: str,
    host_config_dir: Path | None,
    host_plugin_root: Path | None,
    backup_root: Path,
) -> dict[str, Any]:
    plugin_source = target / manifest["host_integration"]["path"]
    if host_cli is None:
        if host_plugin_root is None:
            raise ValueError("formal install requires --host-cli; --host-plugin-root is fixture-only")
        _replace_directory(plugin_source, host_plugin_root, backup_root, "host-plugin")
        return {"mode": "fixture-plugin-root", "plugin_root": str(host_plugin_root)}

    registration = _host_registration_details(manifest, target)
    _ensure_host_marketplace(
        target / manifest["host_integration"]["marketplace_path"],
        registration["marketplace_name"],
        host_cli,
        host_cli_node,
        host_config_dir,
    )
    _run_host_cli(
        host_cli,
        host_cli_node,
        [
            "plugin",
            "install",
            f"{registration['plugin_name']}@{registration['marketplace_name']}",
            "--scope",
            "user",
        ],
        host_config_dir,
    )
    _run_host_cli(
        host_cli,
        host_cli_node,
        [
            "plugin",
            "enable",
            f"{registration['plugin_name']}@{registration['marketplace_name']}",
            "--scope",
            "user",
        ],
        host_config_dir,
    )
    _disable_other_product_plugins(
        registration["plugin_name"],
        registration["marketplace_name"],
        host_cli,
        host_cli_node,
        host_config_dir,
    )
    return {
        "mode": "host-cli-user",
        "marketplace_name": registration["marketplace_name"],
        "plugin_name": registration["plugin_name"],
        "host_config_dir": str(host_config_dir) if host_config_dir is not None else None,
    }


def _verify_host_registration(
    target: Path,
    manifest: dict[str, Any],
    host_cli: str,
    host_cli_node: str,
    host_config_dir: Path | None,
) -> dict[str, Any]:
    registration = _host_registration_details(manifest, target)
    marketplace_path = target / manifest["host_integration"]["marketplace_path"]
    if not _marketplace_matches(host_config_dir, registration["marketplace_name"], marketplace_path):
        raise ValueError("host marketplace is not registered from the active release path")
    settings_path = (host_config_dir or _default_host_config_dir()) / "settings.json"
    settings = _load_manifest(settings_path) if settings_path.is_file() else {}
    enabled = settings.get("enabledPlugins", {}).get(
        f"{registration['plugin_name']}@{registration['marketplace_name']}"
    )
    if enabled is not True:
        raise ValueError("release host plugin is not enabled at user scope")
    _run_host_cli(host_cli, host_cli_node, ["plugin", "list"], host_config_dir)
    return {
        "mode": "host-cli-user",
        "marketplace_name": registration["marketplace_name"],
        "plugin_name": registration["plugin_name"],
        "host_config_dir": str(host_config_dir) if host_config_dir is not None else None,
    }


def _host_registration_details(manifest: dict[str, Any], target: Path) -> dict[str, str]:
    integration = manifest["host_integration"]
    marketplace_path = target / integration["marketplace_path"]
    marketplace_manifest = _load_manifest(marketplace_path / ".codebuddy-plugin" / "marketplace.json")
    expected = {
        "marketplace_name": integration["marketplace_name"],
        "plugin_name": integration["plugin_name"],
    }
    if marketplace_manifest.get("name") != expected["marketplace_name"]:
        raise ValueError("release marketplace manifest name does not match the release manifest")
    plugins = marketplace_manifest.get("plugins", [])
    if not any(item.get("name") == expected["plugin_name"] for item in plugins if isinstance(item, dict)):
        raise ValueError("release marketplace does not contain the declared host plugin")
    return expected


def _ensure_host_marketplace(
    marketplace_path: Path,
    marketplace_name: str,
    host_cli: str,
    host_cli_node: str,
    host_config_dir: Path | None,
) -> None:
    if _marketplace_matches(host_config_dir, marketplace_name, marketplace_path):
        return
    if _marketplace_entry(host_config_dir, marketplace_name) is not None:
        raise ValueError(f"host marketplace is already registered from another path: {marketplace_name}")
    _run_host_cli(
        host_cli,
        host_cli_node,
        ["plugin", "marketplace", "add", str(marketplace_path), "--name", marketplace_name],
        host_config_dir,
    )
    if not _marketplace_matches(host_config_dir, marketplace_name, marketplace_path):
        raise ValueError("host CLI did not register the release marketplace at its immutable path")


def _run_host_cli(
    host_cli: str,
    host_cli_node: str,
    arguments: list[str],
    host_config_dir: Path | None,
) -> subprocess.CompletedProcess[str]:
    command = _host_command(host_cli, host_cli_node) + arguments
    environment = dict(os.environ)
    if host_config_dir is not None:
        environment["CODEBUDDY_CONFIG_DIR"] = str(host_config_dir)
        environment["WORKBUDDY_CONFIG_DIR"] = str(host_config_dir)
    completed = subprocess.run(
        command,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "no host CLI output"
        raise ValueError(f"host CLI failed ({' '.join(command[:2])}): {detail}")
    return completed


def _disable_other_product_plugins(
    plugin_name: str,
    active_marketplace: str,
    host_cli: str,
    host_cli_node: str,
    host_config_dir: Path | None,
) -> None:
    config_dir = host_config_dir or _default_host_config_dir()
    settings_path = config_dir / "settings.json"
    if not settings_path.is_file():
        return
    settings = _load_manifest(settings_path)
    enabled_plugins = settings.get("enabledPlugins", {})
    if not isinstance(enabled_plugins, dict):
        return
    prefix = f"{plugin_name}@"
    active_id = f"{plugin_name}@{active_marketplace}"
    for plugin_id, enabled in enabled_plugins.items():
        if (
            not isinstance(plugin_id, str)
            or plugin_id == active_id
            or not plugin_id.startswith(prefix)
            or enabled is not True
        ):
            continue
        _run_host_cli(
            host_cli,
            host_cli_node,
            ["plugin", "disable", plugin_id, "--scope", "user"],
            host_config_dir,
        )


def _host_command(host_cli: str, host_cli_node: str) -> list[str]:
    value = host_cli.strip()
    if not value:
        raise ValueError("--host-cli must not be empty")
    path = Path(value).expanduser()
    if path.suffix in {".js", ".mjs", ".cjs"}:
        if not path.is_file():
            raise ValueError(f"host CLI entrypoint is missing: {path}")
        return [_resolve_executable(host_cli_node), str(path)]
    return [_resolve_executable(value)]


def _resolve_executable(value: str) -> str:
    path = Path(value).expanduser()
    if path.is_file():
        return str(path.resolve())
    resolved = shutil.which(value)
    if resolved is None:
        raise ValueError(f"host CLI executable is not available: {value}")
    return resolved


def _marketplace_entry(host_config_dir: Path | None, marketplace_name: str) -> dict[str, Any] | None:
    if host_config_dir is None:
        return None
    path = host_config_dir / "plugins" / "known_marketplaces.json"
    if not path.is_file():
        return None
    payload = _load_manifest(path)
    entry = payload.get(marketplace_name)
    return entry if isinstance(entry, dict) else None


def _marketplace_matches(host_config_dir: Path | None, marketplace_name: str, expected: Path) -> bool:
    entry = _marketplace_entry(host_config_dir, marketplace_name)
    if entry is None:
        return False
    source = entry.get("source", {})
    actual = source.get("path") if isinstance(source, dict) else None
    if not isinstance(actual, str):
        actual = entry.get("installLocation")
    if not isinstance(actual, str):
        return False
    try:
        return Path(actual).expanduser().resolve() == expected.expanduser().resolve()
    except OSError:
        return False


def _backup_user_state(product_root: Path) -> None:
    state_paths = [product_root / "runtime.json", product_root / "data"]
    existing = [path for path in state_paths if path.exists()]
    if not existing:
        return
    destination = product_root / "backups" / f"state-{int(time.time())}"
    destination.mkdir(parents=True, exist_ok=False)
    for path in existing:
        target = destination / path.name
        if path.is_dir():
            shutil.copytree(path, target)
        else:
            shutil.copy2(path, target)


def _load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"manifest must be an object: {path}")
    return payload


def _switch_current(product_root: Path, target: Path) -> None:
    current = product_root / "current"
    temporary = product_root / f".current-{os.getpid()}"
    if temporary.exists() or temporary.is_symlink():
        temporary.unlink()
    temporary.symlink_to(target)
    os.replace(temporary, current)


def _replace_directory(source: Path, target: Path, backup_root: Path, label: str) -> None:
    if not source.is_dir():
        raise ValueError(f"release payload is missing: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    backup_root.mkdir(parents=True, exist_ok=True)
    temporary = target.parent / f".{target.name}.installing-{os.getpid()}"
    if temporary.exists():
        raise ValueError(f"stale host install directory exists: {temporary}")
    shutil.copytree(source, temporary)
    previous: Path | None = None
    if target.exists() or target.is_symlink():
        previous = backup_root / f"{label}-{target.name}-{int(time.time())}"
        shutil.move(str(target), str(previous))
    try:
        os.replace(temporary, target)
    except BaseException:
        if previous is not None and not target.exists():
            shutil.move(str(previous), str(target))
        raise


def _safe_release_id(value: Any) -> str:
    if not isinstance(value, str) or not value or value in {".", ".."} or "/" in value or "\\" in value:
        raise ValueError(f"unsafe release id: {value!r}")
    return value


def _default_product_root() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "zagenticopn"
    return Path.home() / ".local" / "share" / "zagenticopn"


def _default_host_config_dir() -> Path:
    """Use the user-level WorkBuddy config as the default host target."""

    return Path.home() / ".workbuddy"


if __name__ == "__main__":
    raise SystemExit(main())
