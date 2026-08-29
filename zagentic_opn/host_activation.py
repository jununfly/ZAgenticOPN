"""Host-facing bridge for the installed ZAgenticOPN runtime.

The WorkBuddy plugin is intentionally a standard-library-only transport shim.
It sends the raw host payload to this module through the installed runtime so
the plugin never imports a checkout or mutates ``PYTHONPATH``.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

from .activation_contract import (
    ACTIVATION_SCHEMA_VERSION,
    PRE_MODEL_HANDOFF_INJECTION,
    handoff_context,
    resolve_intent,
)
from .activation_runner import record_handoff_delivery_failure, run_json_call
from .runtime_config import RuntimeConfigError, load_runtime_config, resolve_scope_for_workspace


def run_hook_payload(payload: Any) -> dict[str, Any]:
    """Convert one host payload into one hook response."""

    if not isinstance(payload, dict):
        return _context_output("")
    prompt = _prompt(payload)
    if resolve_intent(prompt) is None:
        return _context_output("")

    activation_id = os.getenv("ZAGENTICOPN_ACTIVATION_ID") or f"activation-{uuid.uuid4().hex[:12]}"
    scope, scope_failure = _resolve_scope(payload)
    if scope_failure is not None:
        return _scope_failure_output(activation_id, scope_failure)

    request = {
        "schema_version": ACTIVATION_SCHEMA_VERSION,
        "intent_id": resolve_intent(prompt),
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
    return _hook_output(run_json_call(request))


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        payload: Any = {}
    else:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {}
    print(json.dumps(run_hook_payload(payload), ensure_ascii=False, sort_keys=True))
    return 0


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


def _split(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


__all__ = ["main", "run_hook_payload"]


if __name__ == "__main__":
    raise SystemExit(main())
