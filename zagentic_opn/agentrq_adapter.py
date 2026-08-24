"""Thin AgentRQ transport adapter for the Experience Version slice.

AgentRQ's exposed task surface is deliberately treated as transport only.  It
can create/read/update a task and carry a reply, but it is not the authority
for ZAgenticOPN eligibility, claims, review state, or Git provenance.  The
local :class:`CoordinationProtocol` remains that authority so the adapter can
be removed without changing product semantics.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from .coordination import (
    AgentProfile,
    ClaimRequest,
    ClaimReviewRequest,
    CoordinationProtocol,
    DiscoverRequest,
    PublishRequest,
    PublishResultRequest,
    ReviewRequest,
)


class AgentRQTransport(Protocol):
    """The narrow exposed AgentRQ surface used by this adapter.

    These operations correspond to the candidate's createTask/getTask,
    updateTaskStatus and reply tools.  In particular, there is intentionally
    no claim or reviewer-specific operation here.
    """

    def create_task(
        self,
        *,
        task_id: str,
        title: str,
        description: str,
        assignee: str,
        metadata: Mapping[str, Any],
    ) -> Mapping[str, Any]: ...

    def get_task(
        self,
        *,
        task_id: str | None = None,
        include_conversation: bool = False,
    ) -> Mapping[str, Any] | None: ...

    def update_task_status(self, *, task_id: str, status: str) -> Mapping[str, Any]: ...

    def reply(self, *, task_id: str, message: str) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class AdapterTaskRef:
    """Mapping between an AgentRQ task and a ZAgenticOPN Work Item."""

    task_id: str
    work_id: str
    kind: str


class AgentRQAdapter:
    """Expose the product protocol through a removable AgentRQ transport.

    The adapter intentionally performs one task-agnostic ``get_task`` call on
    every discovery activation.  It then asks ZAgenticOPN to apply scope and
    eligibility rules.  The transport's status update happens only after a
    product-owned atomic claim succeeds.
    """

    def __init__(self, coordination: CoordinationProtocol, transport: AgentRQTransport) -> None:
        self._coordination = coordination
        self._transport = transport
        self._task_refs: dict[str, AdapterTaskRef] = {}

    def publish(self, request: PublishRequest) -> dict[str, Any]:
        """Publish a Work Item and project it into the AgentRQ queue."""

        work = self._coordination.publish(request)
        self._transport.create_task(
            task_id=work["id"],
            title=work["objective"],
            description=work["acceptance"],
            assignee="agent",
            metadata={
                "adapter": "zagenticopn-agentrq",
                "kind": "execution",
                "scope": request.scope,
                "work_id": work["id"],
            },
        )
        self._task_refs[work["id"]] = AdapterTaskRef(work["id"], work["id"], "execution")
        return work

    def discover(self, request: DiscoverRequest) -> dict[str, Any]:
        """Discover one AgentRQ task, then apply ZAgenticOPN eligibility."""

        raw_task = self._transport.get_task(task_id=None, include_conversation=True)
        if raw_task is None:
            return {
                "scope": request.scope,
                "agent_id": request.agent.agent_id,
                "activation_id": request.activation_id,
                "items": [],
                "status": "no_eligible_work",
                "filter_reasons": {"agentrq_no_task": 1},
            }

        ref = _task_ref(raw_task)
        self._task_refs[ref.work_id] = ref
        discovered = self._coordination.discover(request)
        items = [item for item in discovered["items"] if item["id"] == ref.work_id]
        if not items:
            reasons = dict(discovered["filter_reasons"])
            reasons["agentrq_task_not_eligible"] = reasons.get("agentrq_task_not_eligible", 0) + 1
            return {**discovered, "items": [], "status": "no_eligible_work", "filter_reasons": reasons, "transport_task": dict(raw_task)}
        return {**discovered, "items": items, "transport_task": dict(raw_task)}

    def claim(self, request: ClaimRequest) -> dict[str, Any]:
        """Atomically claim in ZAgenticOPN before updating AgentRQ status."""

        result = self._coordination.claim(request)
        ref = self._task_refs.get(request.work_id, AdapterTaskRef(request.work_id, request.work_id, "execution"))
        self._transport.update_task_status(task_id=ref.task_id, status="ongoing")
        return result

    def publish_result(self, request: PublishResultRequest) -> dict[str, Any]:
        """Persist structured result locally and carry it through AgentRQ reply."""

        result = self._coordination.publish_result(request)
        ref = self._task_refs.get(request.work_id, AdapterTaskRef(request.work_id, request.work_id, "execution"))
        self._transport.reply(
            task_id=ref.task_id,
            message=json.dumps(
                {
                    "work_id": request.work_id,
                    "result_summary": request.result_summary,
                    "next_action": request.next_action,
                    "acceptance_status": request.acceptance_status,
                    "references": list(request.references),
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
        )
        return result

    def submit(self, scope: str, work_id: str, agent: AgentProfile) -> dict[str, Any]:
        """Create a generic AgentRQ review task for the product review state."""

        result = self._coordination.submit(scope, work_id, agent)
        execution_ref = self._task_refs.get(work_id, AdapterTaskRef(work_id, work_id, "execution"))
        self._transport.update_task_status(task_id=execution_ref.task_id, status="completed")
        review_task_id = f"{work_id}:review"
        self._transport.create_task(
            task_id=review_task_id,
            title=f"Review {work_id}",
            description=result["next_action"] or result["acceptance"],
            assignee="agent",
            metadata={
                "adapter": "zagenticopn-agentrq",
                "kind": "review",
                "scope": scope,
                "work_id": work_id,
            },
        )
        self._task_refs[work_id] = AdapterTaskRef(review_task_id, work_id, "review")
        return {**result, "review_task_id": review_task_id}

    def claim_review(self, request: ClaimReviewRequest) -> dict[str, Any]:
        """Use the product-owned review claim, then mark the transport task ongoing."""

        result = self._coordination.claim_review(request)
        ref = self._task_refs.get(request.work_id, AdapterTaskRef(f"{request.work_id}:review", request.work_id, "review"))
        self._transport.update_task_status(task_id=ref.task_id, status="ongoing")
        return result

    def review(self, request: ReviewRequest) -> dict[str, Any]:
        """Complete the product review and close or reopen the transport task."""

        result = self._coordination.review(request)
        ref = self._task_refs.get(request.work_id, AdapterTaskRef(f"{request.work_id}:review", request.work_id, "review"))
        transport_status = "completed" if result["state"] in {"completed", "blocked"} else "notstarted"
        self._transport.update_task_status(task_id=ref.task_id, status=transport_status)
        return result

    def inspect(self, scope: str, work_id: str) -> dict[str, Any]:
        """Read the authoritative product record through the adapter."""

        return self._coordination.inspect(scope, work_id)

    def scorecard(self, scope: str) -> str:
        """Read the authoritative product scorecard through the adapter."""

        return self._coordination.scorecard(scope)


def _task_ref(raw_task: Mapping[str, Any]) -> AdapterTaskRef:
    task_id = str(raw_task.get("id") or raw_task.get("task_id") or "")
    metadata = raw_task.get("metadata") or {}
    if not task_id or not isinstance(metadata, Mapping):
        raise ValueError("AgentRQ task must expose id and metadata")
    work_id = str(metadata.get("work_id") or task_id)
    kind = str(metadata.get("kind") or "execution")
    return AdapterTaskRef(task_id, work_id, kind)


__all__ = ["AdapterTaskRef", "AgentRQAdapter", "AgentRQTransport"]
