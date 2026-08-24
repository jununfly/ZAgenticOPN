"""Task-agnostic Agent activation adapter for the Experience Version slice."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .coordination import (
    AgentProfile,
    ClaimRequest,
    ClaimReviewRequest,
    CoordinationError,
    CoordinationProtocol,
    DiscoverRequest,
)


@dataclass(frozen=True)
class ActivationRequest:
    """Stable agent identity and session data for one Human-triggered run."""

    scope: str
    agent: AgentProfile
    activation_id: str


class ActivationAdapter:
    """Bridge one generic activation into discover plus one product claim.

    The caller never supplies a Work Item id.  The adapter asks the product
    protocol for the eligible frontier and claims only its first item.  It has
    no polling, retry, wake-up, or scheduler behavior.
    """

    def __init__(self, protocol: CoordinationProtocol) -> None:
        self._protocol = protocol

    def activate(self, request: ActivationRequest) -> dict[str, Any]:
        discovery = self._protocol.discover(
            DiscoverRequest(request.scope, request.agent, request.activation_id)
        )
        if discovery["status"] != "eligible_work":
            return {
                "status": "no_eligible_work",
                "scope": request.scope,
                "agent_id": request.agent.agent_id,
                "activation_id": request.activation_id,
                "discovery": discovery,
            }

        item = discovery["items"][0]
        try:
            if item["state"] == "awaiting_agent_review":
                claimed = self._protocol.claim_review(
                    ClaimReviewRequest(request.scope, item["id"], request.agent, request.activation_id)
                )
                kind = "review"
            else:
                claimed = self._protocol.claim(
                    ClaimRequest(request.scope, item["id"], request.agent, request.activation_id)
                )
                kind = "execution"
        except CoordinationError as error:
            return {
                "status": "claim_conflict",
                "scope": request.scope,
                "agent_id": request.agent.agent_id,
                "activation_id": request.activation_id,
                "discovery": discovery,
                "error": {"type": type(error).__name__, "message": str(error)},
            }

        return {
            "status": "claimed",
            "kind": kind,
            "scope": request.scope,
            "agent_id": request.agent.agent_id,
            "activation_id": request.activation_id,
            "discovery": discovery,
            "work": claimed,
        }


__all__ = ["ActivationAdapter", "ActivationRequest"]
