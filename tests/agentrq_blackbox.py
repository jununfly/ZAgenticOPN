"""Exposed-surface AgentRQ fake and black-box adapter scenarios.

The fake intentionally has only create_task/get_task/update_task_status/reply.
It does not provide claim or reviewer APIs, matching the fixed research
surface.  Scenarios interact with :class:`AgentRQAdapter` only.
"""

from __future__ import annotations

import json
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Mapping

from zagentic_opn import (
    AgentProfile,
    AgentRQAdapter,
    ClaimRequest,
    ClaimReviewRequest,
    CoordinationError,
    CoordinationProtocol,
    DiscoverRequest,
    PublishRequest,
    PublishResultRequest,
    ReviewRequest,
)


class FakeAgentRQSurface:
    """A deliberately weak black-box model of AgentRQ's exposed task tools."""

    def __init__(self) -> None:
        self.tasks: dict[str, dict[str, Any]] = {}
        self.calls: list[dict[str, Any]] = []
        self.conversations: dict[str, list[str]] = {}
        self._lock = threading.RLock()

    def create_task(
        self,
        *,
        task_id: str,
        title: str,
        description: str,
        assignee: str,
        metadata: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        with self._lock:
            self.calls.append({"method": "createTask", "task_id": task_id})
            if task_id in self.tasks:
                raise ValueError(f"task already exists: {task_id}")
            self.tasks[task_id] = {
                "id": task_id,
                "title": title,
                "description": description,
                "assignee": assignee,
                "status": "notstarted",
                "metadata": dict(metadata),
            }
            return dict(self.tasks[task_id])

    def get_task(
        self,
        *,
        task_id: str | None = None,
        include_conversation: bool = False,
    ) -> Mapping[str, Any] | None:
        with self._lock:
            self.calls.append(
                {
                    "method": "getTask",
                    "task_id": task_id,
                    "include_conversation": include_conversation,
                }
            )
            if task_id is not None:
                task = self.tasks.get(task_id)
                return self._copy_task(task, include_conversation) if task else None
            for task in self.tasks.values():
                if task["assignee"] == "agent" and task["status"] == "notstarted":
                    return self._copy_task(task, include_conversation)
            return None

    def update_task_status(self, *, task_id: str, status: str) -> Mapping[str, Any]:
        with self._lock:
            self.calls.append({"method": "updateTaskStatus", "task_id": task_id, "status": status})
            self.tasks[task_id]["status"] = status
            return dict(self.tasks[task_id])

    def reply(self, *, task_id: str, message: str) -> Mapping[str, Any]:
        with self._lock:
            self.calls.append({"method": "reply", "task_id": task_id})
            self.conversations.setdefault(task_id, []).append(message)
            return {"task_id": task_id, "message": message}

    def _copy_task(self, task: dict[str, Any] | None, include_conversation: bool) -> dict[str, Any] | None:
        if task is None:
            return None
        result = dict(task)
        result["metadata"] = dict(task["metadata"])
        if include_conversation:
            result["conversation"] = list(self.conversations.get(task["id"], []))
        return result


def run_black_box() -> dict[str, Any]:
    """Run C1, C2 and C4 as adapter-level black-box scenarios."""

    return {
        "candidate": "agentrq/agentrq",
        "commit": "45c87390fdb535066a05c0592e8183b1b461689b",
        "surface": ["createTask", "getTask", "updateTaskStatus", "reply"],
        "scenarios": [_run_c1(), _run_c2(), _run_c4()],
        "native_surface_boundary": {
            "c1": "adapted_pass: getTask supplies a task-agnostic queue; ZAgenticOPN applies eligibility",
            "c2": "not_native: no AgentRQ claim operation; wrapper-owned CoordinationProtocol claim passes",
            "c4": "not_native: no AgentRQ reviewer state; wrapper projects a generic review task and owns review state",
        },
    }


def _run_c1() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="agentrq-c1-") as directory:
        adapter, transport = _adapter(Path(directory) / "shared.sqlite3")
        work_id = _publish(adapter, "c1-work")
        discovery = adapter.discover(DiscoverRequest(SCOPE, WORKBUDDY, "activation-c1"))
        get_calls = [call for call in transport.calls if call["method"] == "getTask"]
        passed = (
            discovery["status"] == "eligible_work"
            and [item["id"] for item in discovery["items"]] == [work_id]
            and len(get_calls) == 1
            and get_calls[0]["task_id"] is None
        )
        return {
            "gate": "C1",
            "status": "PASS" if passed else "FAIL",
            "work_id": work_id,
            "discovery_status": discovery["status"],
            "human_supplied_work_id": False,
            "task_agnostic_getTask_calls": len(get_calls),
            "filter_reasons": discovery["filter_reasons"],
        }


def _run_c2() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="agentrq-c2-") as directory:
        database = Path(directory) / "shared.sqlite3"
        protocol = CoordinationProtocol(database)
        transport = FakeAgentRQSurface()
        publisher = AgentRQAdapter(protocol, transport)
        work_id = _publish(publisher, "c2-work")
        adapter_a = AgentRQAdapter(protocol, transport)
        adapter_b = AgentRQAdapter(protocol, transport)
        adapter_a.discover(DiscoverRequest(SCOPE, WORKBUDDY, "activation-c2-a"))
        adapter_b.discover(DiscoverRequest(SCOPE, RIVAL, "activation-c2-b"))

        def claim(adapter: AgentRQAdapter, agent: AgentProfile, activation_id: str) -> dict[str, Any]:
            try:
                adapter.claim(ClaimRequest(SCOPE, work_id, agent, activation_id))
                return {"outcome": "won", "agent_id": agent.agent_id}
            except CoordinationError as error:
                return {"outcome": "lost", "agent_id": agent.agent_id, "error": str(error)}

        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(
                executor.map(
                    lambda arguments: claim(*arguments),
                    [
                        (adapter_a, WORKBUDDY, "activation-c2-a"),
                        (adapter_b, RIVAL, "activation-c2-b"),
                    ],
                )
            )
        updates = [call for call in transport.calls if call["method"] == "updateTaskStatus" and call["status"] == "ongoing"]
        winner_count = sum(outcome["outcome"] == "won" for outcome in outcomes)
        loser_count = sum(outcome["outcome"] == "lost" for outcome in outcomes)
        passed = winner_count == 1 and loser_count == 1 and len(updates) == 1
        return {
            "gate": "C2",
            "status": "PASS" if passed else "FAIL",
            "work_id": work_id,
            "outcomes": outcomes,
            "effective_claimants": winner_count,
            "claim_conflicts": loser_count,
            "transport_ongoing_updates": len(updates),
            "duplicate_execution": 0 if passed else "unknown",
        }


def _run_c4() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="agentrq-c4-") as directory:
        database = Path(directory) / "shared.sqlite3"
        protocol = CoordinationProtocol(database)
        transport = FakeAgentRQSurface()
        executor_adapter = AgentRQAdapter(protocol, transport)
        reviewer_adapter = AgentRQAdapter(protocol, transport)
        work_id = _publish(executor_adapter, "c4-work")
        executor_adapter.discover(DiscoverRequest(SCOPE, WORKBUDDY, "activation-c4-executor"))
        executor_adapter.claim(ClaimRequest(SCOPE, work_id, WORKBUDDY, "activation-c4-executor"))
        executor_adapter.publish_result(
            PublishResultRequest(
                SCOPE,
                work_id,
                WORKBUDDY,
                "Created the reviewed artifact.",
                "Reviewer verifies the pinned commit and test result.",
                "met",
                ({"commit": "45c8739", "files": ["artifact.md"], "tests": ["black-box: pass"]},),
            )
        )
        submitted = executor_adapter.submit(SCOPE, work_id, WORKBUDDY)
        review_discovery = reviewer_adapter.discover(DiscoverRequest(SCOPE, CODEX, "activation-c4-reviewer"))
        reviewer_item = review_discovery["items"][0] if review_discovery["items"] else {}
        reviewer_adapter.claim_review(ClaimReviewRequest(SCOPE, work_id, CODEX, "activation-c4-reviewer"))
        completed = reviewer_adapter.review(
            ReviewRequest(SCOPE, work_id, CODEX, "accept", "Pinned commit and test reference verified.")
        )
        reply = json.loads(transport.conversations[work_id][0])
        passed = (
            review_discovery["status"] == "eligible_work"
            and reviewer_item.get("next_action") == "Reviewer verifies the pinned commit and test result."
            and completed["state"] == "completed"
            and reply["references"][0]["commit"] == "45c8739"
            and submitted["review_task_id"] == f"{work_id}:review"
        )
        return {
            "gate": "C4",
            "status": "PASS" if passed else "FAIL",
            "work_id": work_id,
            "review_task_id": submitted["review_task_id"],
            "reviewer_supplied_work_id": False,
            "review_discovery_status": review_discovery["status"],
            "final_state": completed["state"],
            "structured_reply": reply,
        }


def _adapter(database: Path) -> tuple[AgentRQAdapter, FakeAgentRQSurface]:
    transport = FakeAgentRQSurface()
    return AgentRQAdapter(CoordinationProtocol(database), transport), transport


def _publish(adapter: AgentRQAdapter, work_id: str) -> str:
    return adapter.publish(
        PublishRequest(
            SCOPE,
            "Improve the zj-research-report skill with a technical proposal exemplar.",
            "A committed artifact is reviewed and accepted.",
            CODEX,
            frozenset({"technical-writing"}),
            frozenset({"zagentic-skill-write"}),
            work_id,
        )
    )["id"]


SCOPE = "zagenticopn/experience-version"
CODEX = AgentProfile(
    "codex-01", "device-a", frozenset({"technical-writing"}), frozenset({"zagentic-skill-write"}), True
)
WORKBUDDY = AgentProfile(
    "workbuddy-01", "device-a", frozenset({"technical-writing"}), frozenset({"zagentic-skill-write"}), True
)
RIVAL = AgentProfile(
    "workbuddy-02", "device-a", frozenset({"technical-writing"}), frozenset({"zagentic-skill-write"}), True
)
