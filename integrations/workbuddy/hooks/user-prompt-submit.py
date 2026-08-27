"""Turn one WorkBuddy submission into the canonical activation JSON-Call."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any


source_root = Path(
    os.getenv("ZAGENTICOPN_SOURCE_ROOT", str(Path(__file__).resolve().parents[3]))
)
sys.path.insert(0, str(source_root))

from zagentic_opn.activation_contract import (  # noqa: E402
    ACTIVATION_SCHEMA_VERSION,
    PRE_MODEL_HANDOFF_INJECTION,
    handoff_context,
    resolve_intent,
)
from zagentic_opn.activation_runner import record_handoff_delivery_failure  # noqa: E402
from zagentic_opn.runtime_config import (  # noqa: E402
    RuntimeConfigError,
    load_runtime_config,
    resolve_scope_for_workspace,
)


def main() -> int:
    payload = _read_payload()
    prompt = _prompt(payload)
    intent_id = resolve_intent(prompt)
    if intent_id is None:
        _write({"hookSpecificOutput": {}})
        return 0

    activation_id = os.getenv("ZAGENTICOPN_ACTIVATION_ID") or f"activation-{uuid.uuid4().hex[:12]}"
    scope, scope_failure = _resolve_scope(payload)
    if scope_failure is not None:
        _write(_scope_failure_output(activation_id, scope_failure))
        return 0

    request = {
        "schema_version": ACTIVATION_SCHEMA_VERSION,
        "intent_id": intent_id,
        "activation_id": activation_id,
        "scope": scope,
        "agent_profile": {
            "agent_id": os.getenv("ZAGENTICOPN_AGENT_ID", "workbuddy-01"),
            "device_id": os.getenv("ZAGENTICOPN_DEVICE_ID", "device-a"),
            "capabilities": _split(os.getenv("ZAGENTICOPN_CAPABILITIES", "technical-writing")),
            "permissions": _split(os.getenv("ZAGENTICOPN_PERMISSIONS", "zagentic-skill-write")),
            "can_review": os.getenv("ZAGENTICOPN_CAN_REVIEW", "").lower() in {"1", "true", "yes"},
        },
        "host_capabilities": _split(
            os.getenv("ZAGENTICOPN_HOST_CAPABILITIES", PRE_MODEL_HANDOFF_INJECTION)
        ),
    }
    receipt = _run_json_call(request)
    _write(_hook_output(receipt))
    return 0


def _run_json_call(request: dict[str, Any]) -> dict[str, Any]:
    runner_python = os.getenv("ZAGENTICOPN_RUNNER_PYTHON", sys.executable)
    environment = dict(os.environ)
    existing_path = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = str(source_root) + (
        os.pathsep + existing_path if existing_path else ""
    )
    try:
        completed = subprocess.run(
            [runner_python, "-m", "zagentic_opn.activation_runner"],
            input=json.dumps(request, ensure_ascii=False),
            capture_output=True,
            text=True,
            env=environment,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return {
            "status": "runner_unavailable",
            "error": {"type": type(error).__name__, "message": str(error)},
        }
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {
            "status": "runner_unavailable",
            "error": {
                "type": "InvalidRunnerOutput",
                "message": completed.stderr.strip() or "runner did not return one JSON receipt",
            },
        }
    return result if isinstance(result, dict) else {"status": "runner_unavailable"}


def _hook_output(receipt: dict[str, Any]) -> dict[str, Any]:
    status = receipt.get("status")
    if status == "claimed":
        try:
            context = handoff_context(receipt)
        except Exception as error:
            failure = record_handoff_delivery_failure(receipt, str(error))
            return _context_output(
                "ZAgenticOPN activation: handoff_delivery_failed; "
                f"event_recorded={failure.get('event_recorded', False)}."
            )
        return _context_output(context)
    if status == "no_eligible_work":
        return _context_output(
            "ZAgenticOPN activation: status=no_eligible_work; "
            f"activation_id={receipt.get('activation_id')}; "
            f"scope={receipt.get('scope')}; "
            f"next_action={receipt.get('next_action')}"
        )
    if status in {"unsupported_host", "invalid_contract", "invalid_runtime_config", "claim_conflict"}:
        return _context_output(
            "ZAgenticOPN activation: "
            f"status={status}; activation_id={receipt.get('activation_id')}; "
            f"next_action={receipt.get('next_action') or receipt.get('repair_action')}"
        )
    return _context_output(
        "ZAgenticOPN activation: status=runner_unavailable; "
        f"error={receipt.get('error', {}).get('message', 'unknown runner error')}"
    )


def _resolve_scope(payload: dict[str, Any]) -> tuple[str | None, dict[str, str] | None]:
    """Resolve scope from an explicit host value or a host-level workspace binding."""

    configured_scope = os.getenv("ZAGENTICOPN_SCOPE")
    if configured_scope and configured_scope.strip():
        return configured_scope.strip(), None

    workspace = _workspace(payload)
    try:
        runtime = load_runtime_config()
        scope = resolve_scope_for_workspace(runtime.scope_bindings, workspace)
    except (RuntimeConfigError, OSError) as error:
        return None, {
            "status": "invalid_runtime_config",
            "workspace": workspace,
            "error": str(error),
            "next_action": "Repair the host runtime configuration, then submit the activation again.",
        }
    if scope is None:
        return None, {
            "status": "scope_unbound",
            "workspace": workspace,
            "error": "no host-level workspace-to-scope binding matched this workspace",
            "next_action": (
                "Set ZAGENTICOPN_SCOPE explicitly or add a scope_bindings entry for "
                f"workspace {workspace}; submit the activation again."
            ),
        }
    return scope, None


def _scope_failure_output(activation_id: str, failure: dict[str, str]) -> dict[str, Any]:
    return _context_output(
        "ZAgenticOPN activation: "
        f"status={failure['status']}; activation_id={activation_id}; "
        f"workspace={failure['workspace']}; next_action={failure['next_action']}; "
        f"error={failure['error']}"
    )


def _context_output(context: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }


def _prompt(payload: dict[str, Any]) -> str:
    data = payload.get("data")
    if isinstance(data, dict) and data.get("prompt"):
        return str(data["prompt"])
    return str(payload.get("prompt") or payload.get("text") or payload.get("userPrompt") or "")


def _workspace(payload: dict[str, Any]) -> str:
    data = payload.get("data")
    if isinstance(data, dict) and isinstance(data.get("cwd"), str) and data["cwd"].strip():
        return data["cwd"].strip()
    if isinstance(payload.get("cwd"), str) and payload["cwd"].strip():
        return payload["cwd"].strip()
    return str(Path.cwd())


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _split(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _write(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
