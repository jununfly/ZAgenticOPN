"""Canonical one-request JSON runner for ZAgenticOPN activation."""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

from .activation import ActivationAdapter, ActivationRequest
from .activation_contract import (
    ACTIVATION_SCHEMA_VERSION,
    RECEIPT_SCHEMA_VERSION,
    PRE_MODEL_HANDOFF_INJECTION,
    ActivationCall,
    ContractError,
    parse_activation_call,
)
from .coordination import AgentProfile, CoordinationProtocol
from .runtime_config import RuntimeConfig, RuntimeConfigError, load_runtime_config


def run_json_call(payload: Any) -> dict[str, Any]:
    """Execute exactly one validated activation request and return one receipt."""

    try:
        call = parse_activation_call(payload)
    except ContractError as error:
        config = _try_load_config()
        receipt = _base_receipt("invalid_contract", config=config)
        receipt["error"] = {"type": type(error).__name__, "message": str(error)}
        receipt["required_fields"] = [
            "schema_version",
            "intent_id",
            "activation_id",
            "scope",
            "agent_profile",
            "host_capabilities",
        ]
        receipt["repair_action"] = "Send one strict zagenticopn.activation.v1 JSON-Call."
        receipt["event_recorded"] = _record_rejection_if_possible(
            config,
            _safe_text(payload.get("scope")) if isinstance(payload, dict) else None,
            _safe_text(payload.get("activation_id")) if isinstance(payload, dict) else None,
            "invalid_contract",
            _safe_agent(payload.get("agent_profile")) if isinstance(payload, dict) else None,
            {"error": str(error)},
        )
        return receipt

    try:
        config = load_runtime_config()
    except RuntimeConfigError as error:
        receipt = _base_receipt("invalid_runtime_config", call=None)
        receipt.update(
            {
                "intent_id": call.intent_id,
                "activation_id": call.activation_id,
                "scope": call.scope,
                "agent_id": call.agent.agent_id,
                "device_id": call.agent.device_id,
                "error": {"type": type(error).__name__, "message": str(error)},
                "required_fields": ["shared_store_path", "config_updated_at"],
                "repair_action": "python -m zagentic_opn.runtime_config configure",
                "event_recorded": False,
            }
        )
        return receipt

    store_error = _store_error(config.shared_store_path)
    if store_error is not None:
        receipt = _base_receipt("invalid_runtime_config", call=call, config=config)
        receipt.update(
            {
                "error": {"type": "RuntimeConfigError", "message": store_error},
                "required_fields": ["shared_store_path", "config_updated_at"],
                "repair_action": "python -m zagentic_opn.runtime_config configure",
                "event_recorded": False,
            }
        )
        return receipt

    if PRE_MODEL_HANDOFF_INJECTION not in call.host_capabilities:
        recorded = _record_rejection_if_possible(
            config,
            call.scope,
            call.activation_id,
            "unsupported_host",
            call.agent,
            {
                "intent_id": call.intent_id,
                "host_capabilities": sorted(call.host_capabilities),
                "required_host_capability": PRE_MODEL_HANDOFF_INJECTION,
            },
        )
        receipt = _base_receipt("unsupported_host", call=call, config=config)
        receipt.update(
            {
                "error": {
                    "type": "UnsupportedHost",
                    "message": "host_capabilities must include pre_model_handoff_injection",
                },
                "required_host_capabilities": [PRE_MODEL_HANDOFF_INJECTION],
                "repair_action": "Use a host adapter that can inject the receipt handoff before model execution.",
                "event_recorded": recorded,
            }
        )
        return receipt

    try:
        protocol = CoordinationProtocol(config.shared_store_path)
        activation = ActivationAdapter(protocol).activate(
            ActivationRequest(call.scope, call.agent, call.activation_id)
        )
    except Exception as error:  # A host still receives a structured receipt.
        receipt = _base_receipt("invalid_runtime_config", call=call, config=config)
        receipt.update(
            {
                "error": {"type": type(error).__name__, "message": str(error)},
                "required_fields": ["shared_store_path", "config_updated_at"],
                "repair_action": "Check that the configured shared store is readable and writable.",
                "event_recorded": False,
            }
        )
        return receipt

    receipt = _base_receipt(activation["status"], call=call, config=config)
    receipt["event_recorded"] = True
    receipt["discovery"] = activation.get("discovery")
    if activation["status"] == "claimed":
        work = activation["work"]
        receipt.update(
            {
                "kind": activation["kind"],
                "work_id": work["id"],
                "next_action": work.get("next_action"),
                "handoff": _handoff(work),
                "evidence": work.get("references", []),
            }
        )
    else:
        receipt["error"] = activation.get("error")
        receipt["next_action"] = "Wait for or publish an eligible Work Item in this scope."
    return receipt


def record_handoff_delivery_failure(receipt: dict[str, Any], reason: str) -> dict[str, Any]:
    """Record a host failure that occurs after an execution claim."""

    status = "handoff_delivery_failed"
    try:
        scope = _required_receipt_text(receipt, "scope")
        work_id = _required_receipt_text(receipt, "work_id")
        activation_id = _required_receipt_text(receipt, "activation_id")
        agent = AgentProfile(
            _required_receipt_text(receipt, "agent_id"),
            _required_receipt_text(receipt, "device_id"),
        )
        config = load_runtime_config()
        store_error = _store_error(config.shared_store_path)
        if store_error is not None:
            return {
                "status": status,
                "scope": scope,
                "work_id": work_id,
                "activation_id": activation_id,
                "error": {"type": "RuntimeConfigError", "message": store_error},
                "event_recorded": False,
            }
        CoordinationProtocol(config.shared_store_path).record_handoff_delivery_failed(
            scope, work_id, activation_id, agent, reason
        )
        return {
            "status": status,
            "scope": scope,
            "work_id": work_id,
            "activation_id": activation_id,
            "error": {"type": "HandoffDeliveryError", "message": reason},
            "event_recorded": True,
        }
    except Exception as error:
        return {
            "status": status,
            "error": {"type": type(error).__name__, "message": str(error)},
            "event_recorded": False,
        }


def main() -> int:
    """Read one JSON value from stdin and print one JSON receipt to stdout."""

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as error:
        payload = None
        receipt = _base_receipt("invalid_contract")
        receipt.update(
            {
                "error": {"type": type(error).__name__, "message": str(error)},
                "required_fields": [
                    "schema_version",
                    "intent_id",
                    "activation_id",
                    "scope",
                    "agent_profile",
                    "host_capabilities",
                ],
                "repair_action": "Send exactly one JSON object on stdin.",
                "event_recorded": False,
            }
        )
    else:
        receipt = run_json_call(payload)
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


def _base_receipt(
    status: str,
    *,
    call: ActivationCall | None = None,
    config: RuntimeConfig | None = None,
) -> dict[str, Any]:
    return {
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "activation_schema_version": ACTIVATION_SCHEMA_VERSION,
        "status": status,
        "intent_id": call.intent_id if call else None,
        "activation_id": call.activation_id if call else None,
        "scope": call.scope if call else None,
        "agent_id": call.agent.agent_id if call else None,
        "device_id": call.agent.device_id if call else None,
        "work_id": None,
        "kind": None,
        "next_action": None,
        "config_loaded_at": config.config_loaded_at if config else None,
        "config_updated_at": config.config_updated_at if config else None,
        "event_recorded": False,
    }


def _handoff(work: dict[str, Any]) -> dict[str, Any]:
    return {
        "work_id": work["id"],
        "scope": work["scope"],
        "objective": work["objective"],
        "acceptance": work["acceptance"],
        "state": work["state"],
        "claimant": work.get("claimant"),
        "next_action": work.get("next_action"),
        "references": work.get("references", []),
    }


def _try_load_config() -> RuntimeConfig | None:
    try:
        return load_runtime_config()
    except RuntimeConfigError:
        return None


def _store_error(path: Path) -> str | None:
    if not path.is_file():
        return f"configured shared store does not exist: {path}"
    if not os.access(path, os.R_OK | os.W_OK):
        return f"configured shared store is not readable and writable: {path}"
    try:
        with sqlite3.connect(path) as connection:
            connection.execute("PRAGMA user_version").fetchone()
    except (OSError, sqlite3.Error) as error:
        return f"configured shared store is not usable: {path} ({error})"
    return None


def _record_rejection_if_possible(
    config: RuntimeConfig | None,
    scope: str | None,
    activation_id: str | None,
    reason: str,
    agent: AgentProfile | None,
    payload: dict[str, Any],
) -> bool:
    if config is None or scope is None or activation_id is None:
        return False
    if _store_error(config.shared_store_path) is not None:
        return False
    try:
        CoordinationProtocol(config.shared_store_path).record_activation_rejected(
            scope, activation_id, reason, agent, payload
        )
    except Exception:
        return False
    return True


def _safe_text(value: Any) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _safe_agent(value: Any) -> AgentProfile | None:
    if not isinstance(value, dict):
        return None
    agent_id = _safe_text(value.get("agent_id"))
    device_id = _safe_text(value.get("device_id"))
    if agent_id is None or device_id is None:
        return None
    return AgentProfile(agent_id, device_id)


def _required_receipt_text(receipt: dict[str, Any], field: str) -> str:
    value = _safe_text(receipt.get(field))
    if value is None:
        raise ContractError(f"receipt.{field} is required")
    return value


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["main", "record_handoff_delivery_failure", "run_json_call"]
