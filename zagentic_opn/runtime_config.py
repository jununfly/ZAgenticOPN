"""Host-level runtime configuration with atomic writes and hot reads."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUNTIME_CONFIG_SCHEMA_VERSION = "zagenticopn.runtime-config.v1"
RUNTIME_CONFIG_ENV = "ZAGENTICOPN_RUNTIME_CONFIG"
RUNTIME_CONFIG_RELATIVE_PATH = Path("zagenticopn") / "runtime.json"
REQUIRED_RUNTIME_FIELDS = ("shared_store_path", "config_updated_at")
CONFIGURE_REQUIRED_FIELDS = frozenset({"schema_version", "shared_store_path"})
CONFIGURE_FIELDS = frozenset(CONFIGURE_REQUIRED_FIELDS | {"scope_bindings"})
SCOPE_BINDING_FIELDS = frozenset({"workspace_root", "scope"})
_TIMESTAMP_LENGTH = len("YYYYMMDDHHMMSS.SSSZ")


class RuntimeConfigError(ValueError):
    """A runtime configuration cannot safely be loaded or written."""


@dataclass(frozen=True)
class ScopeBinding:
    """An explicit host workspace-to-coordination-scope binding."""

    workspace_root: Path
    scope: str


@dataclass(frozen=True)
class RuntimeConfig:
    shared_store_path: Path
    scope_bindings: tuple[ScopeBinding, ...]
    config_updated_at: str
    config_path: Path
    config_loaded_at: str


def utc_timestamp() -> str:
    """Return a Human-readable UTC diagnostic timestamp."""

    now = datetime.now(timezone.utc)
    return now.strftime("%Y%m%d%H%M%S.%f")[:_TIMESTAMP_LENGTH - 1] + "Z"


def runtime_config_path() -> Path:
    """Find the host config file, using a system config-dir provider first."""

    override = os.getenv(RUNTIME_CONFIG_ENV)
    if override and override.strip():
        return Path(override).expanduser()
    return _system_config_dir() / RUNTIME_CONFIG_RELATIVE_PATH


def load_runtime_config(path: str | Path | None = None) -> RuntimeConfig:
    """Read and strictly validate a complete runtime snapshot."""

    config_path = Path(path) if path is not None else runtime_config_path()
    loaded_at = utc_timestamp()
    try:
        raw = config_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RuntimeConfigError(
            f"runtime config is not readable: {config_path}; repair with "
            "python -m zagentic_opn.runtime_config configure"
        ) from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeConfigError(f"runtime config is not valid JSON: {config_path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeConfigError("runtime config must be a JSON object")
    required = frozenset(REQUIRED_RUNTIME_FIELDS)
    unknown = frozenset(payload) - (required | {"scope_bindings"})
    if not required.issubset(payload) or unknown:
        raise RuntimeConfigError(
            "runtime config must contain shared_store_path and config_updated_at, "
            "with optional scope_bindings"
        )
    store_value = payload["shared_store_path"]
    if not isinstance(store_value, str) or not store_value.strip():
        raise RuntimeConfigError("shared_store_path must be a non-empty string")
    store_path = Path(store_value).expanduser()
    if not store_path.is_absolute():
        raise RuntimeConfigError("shared_store_path must be absolute")
    updated_at = payload["config_updated_at"]
    if not isinstance(updated_at, str) or not _valid_timestamp(updated_at):
        raise RuntimeConfigError("config_updated_at must use YYYYMMDDHHMMSS[.SSS]Z")
    bindings = _parse_scope_bindings(payload.get("scope_bindings", []))
    return RuntimeConfig(store_path, bindings, updated_at, config_path, loaded_at)


def configure_runtime(payload: Any, path: str | Path | None = None) -> dict[str, Any]:
    """Validate and atomically write one complete host configuration."""

    if not isinstance(payload, dict):
        raise RuntimeConfigError("configure request must be a JSON object")
    if not CONFIGURE_REQUIRED_FIELDS.issubset(payload) or frozenset(payload) - CONFIGURE_FIELDS:
        raise RuntimeConfigError(
            "configure request must contain schema_version and shared_store_path, "
            "with optional scope_bindings"
        )
    if payload["schema_version"] != RUNTIME_CONFIG_SCHEMA_VERSION:
        raise RuntimeConfigError("unsupported runtime config schema_version")
    store_value = payload["shared_store_path"]
    if not isinstance(store_value, str) or not store_value.strip():
        raise RuntimeConfigError("shared_store_path must be a non-empty string")
    store_path = Path(store_value).expanduser()
    if not store_path.is_absolute():
        raise RuntimeConfigError("shared_store_path must be absolute")
    bindings = _parse_scope_bindings(payload.get("scope_bindings", []))
    config_path = Path(path) if path is not None else runtime_config_path()
    updated_at = utc_timestamp()
    _atomic_write(
        config_path,
        {
            "shared_store_path": str(store_path),
            "scope_bindings": [
                {"workspace_root": str(item.workspace_root), "scope": item.scope}
                for item in bindings
            ],
            "config_updated_at": updated_at,
        },
    )
    loaded = load_runtime_config(config_path)
    return {
        "status": "configured",
        "config_path": str(loaded.config_path),
        "shared_store_path": str(loaded.shared_store_path),
        "scope_bindings": [
            {"workspace_root": str(item.workspace_root), "scope": item.scope}
            for item in loaded.scope_bindings
        ],
        "config_updated_at": loaded.config_updated_at,
        "config_loaded_at": loaded.config_loaded_at,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Configure the host-level ZAgenticOPN runtime.")
    parser.add_argument("operation", choices=("configure", "repair"))
    args = parser.parse_args(argv)
    try:
        payload = json.load(sys.stdin)
        result = configure_runtime(payload)
    except (RuntimeConfigError, json.JSONDecodeError, OSError) as exc:
        result = {
            "status": "invalid_runtime_config",
            "error": {"type": type(exc).__name__, "message": str(exc)},
            "required_fields": ["schema_version", "shared_store_path"],
            "repair_action": "python -m zagentic_opn.runtime_config configure",
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    lock = Path(str(path) + ".lock")
    acquired = False
    deadline = time.monotonic() + 2.0
    try:
        while not acquired:
            try:
                lock.mkdir()
                acquired = True
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise RuntimeConfigError(f"runtime config is locked: {path}")
                time.sleep(0.01)
        temporary_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=parent, prefix=".runtime-", delete=False
            ) as temporary:
                temporary_name = temporary.name
                json.dump(payload, temporary, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_name, path)
            try:
                os.chmod(path, 0o600)
            except OSError:
                pass
            _fsync_directory(parent)
        except BaseException:
            if temporary_name:
                try:
                    Path(temporary_name).unlink()
                except OSError:
                    pass
            raise
    finally:
        if acquired:
            try:
                lock.rmdir()
            except OSError:
                pass


def _system_config_dir() -> Path:
    """Use the cross-platform provider when present, with a native fallback."""

    try:
        from platformdirs import user_config_dir  # type: ignore[import-not-found]

        return Path(user_config_dir())
    except ImportError:
        pass
    if os.name == "nt":
        root = os.getenv("APPDATA")
        if root:
            return Path(root)
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    else:
        root = os.getenv("XDG_CONFIG_HOME")
        if root:
            return Path(root)
        return Path.home() / ".config"
    raise RuntimeConfigError("unable to locate the host user config directory")


def resolve_scope_for_workspace(
    bindings: tuple[ScopeBinding, ...], workspace: str | Path
) -> str | None:
    """Resolve an explicit workspace binding using the most-specific root."""

    candidate = _normalise_workspace(workspace)
    matches = []
    for item in bindings:
        root = _normalise_workspace(item.workspace_root)
        if root == candidate or root in candidate.parents:
            matches.append(ScopeBinding(root, item.scope))
    if not matches:
        return None
    deepest = max(len(item.workspace_root.parts) for item in matches)
    selected = [item for item in matches if len(item.workspace_root.parts) == deepest]
    scopes = {item.scope for item in selected}
    if len(scopes) != 1:
        raise RuntimeConfigError(f"workspace has ambiguous scope bindings: {candidate}")
    return selected[0].scope


def _parse_scope_bindings(value: Any) -> tuple[ScopeBinding, ...]:
    if not isinstance(value, list):
        raise RuntimeConfigError("scope_bindings must be a list")
    bindings: list[ScopeBinding] = []
    seen_roots: set[Path] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict) or frozenset(item) != SCOPE_BINDING_FIELDS:
            raise RuntimeConfigError(
                f"scope_bindings[{index}] must contain exactly workspace_root and scope"
            )
        root_value = item["workspace_root"]
        scope = item["scope"]
        if not isinstance(root_value, str) or not root_value.strip():
            raise RuntimeConfigError(
                f"scope_bindings[{index}].workspace_root must be non-empty"
            )
        if not isinstance(scope, str) or not scope.strip():
            raise RuntimeConfigError(f"scope_bindings[{index}].scope must be non-empty")
        root = Path(root_value).expanduser()
        if not root.is_absolute():
            raise RuntimeConfigError(
                f"scope_bindings[{index}].workspace_root must be absolute"
            )
        normalised_root = _normalise_workspace(root)
        if normalised_root in seen_roots:
            raise RuntimeConfigError(
                f"scope_bindings contains duplicate workspace_root: {normalised_root}"
            )
        seen_roots.add(normalised_root)
        bindings.append(ScopeBinding(normalised_root, scope.strip()))
    return tuple(bindings)


def _normalise_workspace(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise RuntimeConfigError("workspace path must be absolute")
    return path.resolve(strict=False)


def _valid_timestamp(value: str) -> bool:
    if len(value) == 15 and value.endswith("Z"):
        return value[:-1].isdigit()
    if len(value) == 19 and value[-5] == "." and value.endswith("Z"):
        return value[:14].isdigit() and value[-4:-1].isdigit()
    return False


def _fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CONFIGURE_FIELDS",
    "CONFIGURE_REQUIRED_FIELDS",
    "REQUIRED_RUNTIME_FIELDS",
    "RUNTIME_CONFIG_ENV",
    "RUNTIME_CONFIG_SCHEMA_VERSION",
    "RuntimeConfig",
    "RuntimeConfigError",
    "ScopeBinding",
    "configure_runtime",
    "load_runtime_config",
    "resolve_scope_for_workspace",
    "runtime_config_path",
    "utc_timestamp",
]
