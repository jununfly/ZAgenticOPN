"""The narrow JSON contract for Human-triggered activation.

The contract is intentionally smaller than the coordination protocol.  Hosts
resolve a Human alias before calling the runner; the runner accepts only the
versioned intent id and explicit session/profile data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .coordination import AgentProfile


ACTIVATION_SCHEMA_VERSION = "zagenticopn.activation.v1"
RECEIPT_SCHEMA_VERSION = "zagenticopn.activation.receipt.v1"
INTENT_CHECK_SHARED_CONTEXT = "zagenticopn.activation.check_shared_context.v1"
SHARED_CONTEXT_ALIAS = "检查 shared context"
PRE_MODEL_HANDOFF_INJECTION = "pre_model_handoff_injection"
KNOWN_HOST_CAPABILITIES = frozenset({PRE_MODEL_HANDOFF_INJECTION})

_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "intent_id",
        "activation_id",
        "scope",
        "agent_profile",
        "host_capabilities",
    }
)
_PROFILE_FIELDS = frozenset(
    {"agent_id", "device_id", "capabilities", "permissions", "can_review"}
)


class ContractError(ValueError):
    """A JSON-Call is not the registered activation contract."""

    def __init__(self, message: str, *, field: str | None = None) -> None:
        super().__init__(message)
        self.field = field


@dataclass(frozen=True)
class ActivationCall:
    """Validated input accepted by the activation runner."""

    intent_id: str
    activation_id: str
    scope: str
    agent: AgentProfile
    host_capabilities: frozenset[str]


def resolve_intent(text: str) -> str | None:
    """Resolve one exact Human alias without side effects or model judgment."""

    if not isinstance(text, str):
        return None
    return INTENT_CHECK_SHARED_CONTEXT if text.strip() == SHARED_CONTEXT_ALIAS else None


def parse_activation_call(payload: Any) -> ActivationCall:
    """Strictly validate one JSON-Call and return its typed projection."""

    if not isinstance(payload, dict):
        raise ContractError("request must be a JSON object")
    keys = frozenset(payload)
    if keys != _REQUEST_FIELDS:
        missing = sorted(_REQUEST_FIELDS - keys)
        extra = sorted(keys - _REQUEST_FIELDS)
        details = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("extra=" + ",".join(extra))
        raise ContractError("invalid activation request fields: " + "; ".join(details))
    if payload["schema_version"] != ACTIVATION_SCHEMA_VERSION:
        raise ContractError("unsupported schema_version", field="schema_version")
    if payload["intent_id"] != INTENT_CHECK_SHARED_CONTEXT:
        raise ContractError("unsupported intent_id", field="intent_id")

    activation_id = _text(payload["activation_id"], "activation_id")
    scope = _text(payload["scope"], "scope")
    profile = payload["agent_profile"]
    if not isinstance(profile, dict):
        raise ContractError("agent_profile must be an object", field="agent_profile")
    if frozenset(profile) != _PROFILE_FIELDS:
        raise ContractError("agent_profile fields must be exactly the registered profile")
    agent = AgentProfile(
        _text(profile["agent_id"], "agent_profile.agent_id"),
        _text(profile["device_id"], "agent_profile.device_id"),
        frozenset(_string_list(profile["capabilities"], "agent_profile.capabilities")),
        frozenset(_string_list(profile["permissions"], "agent_profile.permissions")),
        _bool(profile["can_review"], "agent_profile.can_review"),
    )
    host_capabilities = frozenset(
        _string_list(payload["host_capabilities"], "host_capabilities")
    )
    unknown = sorted(host_capabilities - KNOWN_HOST_CAPABILITIES)
    if unknown:
        raise ContractError("unknown host_capabilities: " + ",".join(unknown), field="host_capabilities")
    return ActivationCall(
        INTENT_CHECK_SHARED_CONTEXT,
        activation_id,
        scope,
        agent,
        host_capabilities,
    )


def handoff_context(receipt: dict[str, Any]) -> str:
    """Render the only handoff a host may inject for a claimed receipt."""

    if receipt.get("status") != "claimed":
        raise ContractError("only a claimed receipt can be delivered")
    handoff = receipt.get("handoff")
    if not isinstance(handoff, dict):
        raise ContractError("claimed receipt has no handoff")
    required = {"work_id", "scope", "objective", "acceptance", "state", "next_action", "references"}
    if not required.issubset(handoff):
        raise ContractError("claimed receipt handoff is incomplete")
    return (
        "You have claimed this ZAgenticOPN Work Item. Continue execution using only "
        "the shared handoff below; publish a result with canonical Git references.\n"
        + json.dumps(handoff, ensure_ascii=False, sort_keys=True)
    )


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string", field=field)
    return value


def _bool(value: Any, field: str) -> bool:
    if type(value) is not bool:
        raise ContractError(f"{field} must be a boolean", field=field)
    return value


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ContractError(f"{field} must be a list of non-empty strings", field=field)
    if len(set(value)) != len(value):
        raise ContractError(f"{field} must not contain duplicates", field=field)
    return value


__all__ = [
    "ACTIVATION_SCHEMA_VERSION",
    "ActivationCall",
    "ContractError",
    "INTENT_CHECK_SHARED_CONTEXT",
    "KNOWN_HOST_CAPABILITIES",
    "PRE_MODEL_HANDOFF_INJECTION",
    "RECEIPT_SCHEMA_VERSION",
    "SHARED_CONTEXT_ALIAS",
    "handoff_context",
    "parse_activation_call",
    "resolve_intent",
]
