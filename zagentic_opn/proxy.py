"""Local Agent Integration Proxy for the fixed activation phrase."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from .activation import ActivationAdapter, ActivationRequest
from .activation_contract import SHARED_CONTEXT_ALIAS, resolve_intent
from .coordination import AgentProfile, CoordinationProtocol


SHARED_CONTEXT_PHRASE = SHARED_CONTEXT_ALIAS


class ModelRuntime(Protocol):
    """The model boundary that receives one assembled request."""

    def complete(self, messages: tuple[dict[str, str], ...]) -> str:
        """Complete one model request and return the assistant text."""


@dataclass(frozen=True)
class ProxyRequest:
    """Input from a local Agent runtime for one Human-triggered request."""

    message: str
    scope: str
    agent: AgentProfile
    activation_id: str


class AgentIntegrationProxy:
    """Route one local Agent request into coordination when explicitly triggered.

    The proxy owns only the integration boundary.  Work Item eligibility,
    atomic claim, review state, and provenance remain in
    :class:`CoordinationProtocol`.
    """

    def __init__(self, protocol: CoordinationProtocol) -> None:
        self._activation = ActivationAdapter(protocol)

    def prepare(self, request: ProxyRequest) -> dict[str, Any]:
        """Prepare one host-consumable model request without calling a model."""
        if resolve_intent(request.message) is None:
            messages = ({"role": "user", "content": request.message},)
            return {
                "status": "pass_through",
                "messages": list(messages),
            }

        activation = self._activation.activate(
            ActivationRequest(request.scope, request.agent, request.activation_id)
        )
        if activation["status"] != "claimed":
            return {
                "status": activation["status"],
                "activation": activation,
                "messages": [],
            }

        messages = (
            {"role": "system", "content": _handoff_message(activation["work"])},
            {"role": "user", "content": request.message},
        )
        return {
            "status": "handoff_injected",
            "activation": activation,
            "messages": list(messages),
        }

    def handle(self, request: ProxyRequest, runtime: ModelRuntime) -> dict[str, Any]:
        """Handle one request without polling or implicit task selection."""

        prepared = self.prepare(request)
        messages = tuple(prepared["messages"])
        if not messages:
            return prepared
        prepared["model_response"] = runtime.complete(messages)
        return prepared


def _handoff_message(work: dict[str, Any]) -> str:
    """Serialize only the claimed shared Work Item into the model request."""

    payload = {
        "work_id": work["id"],
        "scope": work["scope"],
        "objective": work["objective"],
        "acceptance": work["acceptance"],
        "state": work["state"],
        "claimant": work.get("claimant"),
        "next_action": work.get("next_action"),
        "references": work.get("references", []),
    }
    return (
        "You have claimed this ZAgenticOPN Work Item. Continue execution using only "
        "the shared handoff below; publish a result with canonical Git references.\n"
        + json.dumps(payload, ensure_ascii=False, sort_keys=True)
    )


__all__ = [
    "AgentIntegrationProxy",
    "ModelRuntime",
    "ProxyRequest",
    "SHARED_CONTEXT_PHRASE",
]
