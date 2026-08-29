"""Thin WorkBuddy bridge for the installed ZAgenticOPN runtime.

This file deliberately imports only the Python standard library. The product
runtime is selected from a user-side launcher and is never loaded from the
plugin checkout or a consuming project.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


SHARED_CONTEXT_ALIAS = "检查 shared context"
RUNTIME_LAUNCHER_ENV = "ZAGENTICOPN_RUNTIME_LAUNCHER"


def main() -> int:
    payload = _read_payload()
    if _prompt(payload).strip() != SHARED_CONTEXT_ALIAS:
        _write(_context_output(""))
        return 0

    launcher = _runtime_launcher()
    if launcher is None or not launcher.is_file():
        _write(
            _context_output(
                "ZAgenticOPN activation: status=runner_unavailable; "
                f"error=installed runtime launcher not found: {launcher}"
            )
        )
        return 0

    environment = dict(os.environ)
    # A formal release must never inherit source import paths from a host or project.
    environment.pop("ZAGENTICOPN_SOURCE_ROOT", None)
    environment.pop("PYTHONPATH", None)
    try:
        completed = subprocess.run(
            [str(launcher), "host-activate"],
            input=json.dumps(payload, ensure_ascii=False),
            capture_output=True,
            text=True,
            env=environment,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        _write(
            _context_output(
                "ZAgenticOPN activation: status=runner_unavailable; "
                f"error={type(error).__name__}: {error}"
            )
        )
        return 0

    try:
        output = json.loads(completed.stdout)
    except json.JSONDecodeError:
        output = _context_output(
            "ZAgenticOPN activation: status=runner_unavailable; "
            f"error={completed.stderr.strip() or 'installed runtime returned invalid JSON'}"
        )
    _write(output if isinstance(output, dict) else _context_output(""))
    return 0


def _runtime_launcher() -> Path | None:
    configured = os.getenv(RUNTIME_LAUNCHER_ENV)
    if configured and configured.strip():
        return Path(configured).expanduser()
    if sys.platform == "darwin":
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "zagenticopn"
            / "current"
            / "bin"
            / "zagenticopn"
        )
    return Path.home() / ".local" / "share" / "zagenticopn" / "current" / "bin" / "zagenticopn"


def _prompt(payload: dict[str, Any]) -> str:
    data = payload.get("data")
    if isinstance(data, dict) and data.get("prompt"):
        return str(data["prompt"])
    return str(payload.get("prompt") or payload.get("text") or payload.get("userPrompt") or "")


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _context_output(context: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }


def _write(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
