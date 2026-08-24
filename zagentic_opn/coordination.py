"""Persistent coordination protocol for the Experience Version.

The public :class:`CoordinationProtocol` interface is the only seam used by
agents and fixtures. SQLite is an implementation detail that provides one
transactional shared context for the local vertical slice.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Literal


WorkState = Literal[
    "available",
    "claimed",
    "blocked",
    "awaiting_agent_review",
    "completed",
    "cancelled",
]
ClaimKind = Literal["execution", "review"]


class CoordinationError(RuntimeError):
    """Base error for a rejected coordination operation."""


class ValidationError(CoordinationError):
    """Raised when a request does not satisfy the public interface."""


class NotFoundError(CoordinationError):
    """Raised when a referenced shared object does not exist."""


class EligibilityError(CoordinationError):
    """Raised when an agent cannot perform the requested operation."""


@dataclass(frozen=True)
class AgentProfile:
    """Stable agent identity and fixed Experience Version eligibility data."""

    agent_id: str
    device_id: str
    capabilities: frozenset[str] = field(default_factory=frozenset)
    permissions: frozenset[str] = field(default_factory=frozenset)
    can_review: bool = False

    def __post_init__(self) -> None:
        if not self.agent_id or not self.device_id:
            raise ValidationError("agent_id and device_id are required")


@dataclass(frozen=True)
class PublishRequest:
    """Fields required to publish an independently claimable Work Item."""

    scope: str
    objective: str
    acceptance: str
    creator: AgentProfile
    required_capabilities: frozenset[str] = field(default_factory=frozenset)
    required_permissions: frozenset[str] = field(default_factory=frozenset)
    work_id: str | None = None


@dataclass(frozen=True)
class DiscoverRequest:
    """Request to inspect one shared scope during one agent activation."""

    scope: str
    agent: AgentProfile
    activation_id: str


@dataclass(frozen=True)
class ClaimRequest:
    """Request to atomically claim execution work."""

    scope: str
    work_id: str
    agent: AgentProfile
    activation_id: str


@dataclass(frozen=True)
class PublishResultRequest:
    """Result summary and provenance published by the execution claimant."""

    scope: str
    work_id: str
    agent: AgentProfile
    result_summary: str
    next_action: str
    acceptance_status: Literal["met", "not_met", "partial"]
    references: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class BlockRequest:
    """Structured blocker for work that cannot safely continue."""

    scope: str
    work_id: str
    agent: AgentProfile
    category: str
    observed_facts: str
    attempted_actions: str
    required_decision: str
    next_action: str


@dataclass(frozen=True)
class ReopenRequest:
    """Human exception request for releasing a stale or blocked Work Item."""

    scope: str
    work_id: str
    operator_id: str
    reason: str


@dataclass(frozen=True)
class ClaimReviewRequest:
    """Request to atomically claim an awaiting-agent-review Work Item."""

    scope: str
    work_id: str
    reviewer: AgentProfile
    activation_id: str


@dataclass(frozen=True)
class ReviewRequest:
    """Reviewer decision for a claimed result."""

    scope: str
    work_id: str
    reviewer: AgentProfile
    decision: Literal["accept", "request_changes", "escalate"]
    note: str = ""


class CoordinationProtocol:
    """Deep coordination module behind the Agent integration seam.

    Each method returns JSON-compatible dictionaries so the same interface can
    be projected through a CLI, MCP adapter, or HTTP adapter without changing
    Work Item semantics.
    """

    def __init__(self, database: str | Path) -> None:
        self.database = str(database)
        if self.database != ":memory:":
            Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._initialize()

    def publish(self, request: PublishRequest) -> dict[str, Any]:
        """Create an available Work Item and emit a publish event."""

        _require_text(request.scope, "scope")
        _require_text(request.objective, "objective")
        _require_text(request.acceptance, "acceptance")
        work_id = request.work_id or f"work-{uuid.uuid4().hex[:12]}"
        now = _now()
        with self._connection() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO work_items (
                      id, scope, objective, acceptance, required_capabilities,
                      required_permissions, state, creator, revision, created_at,
                      updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 'available', ?, 0, ?, ?)
                    """,
                    (
                        work_id,
                        request.scope,
                        request.objective,
                        request.acceptance,
                        _json(sorted(request.required_capabilities)),
                        _json(sorted(request.required_permissions)),
                        request.creator.agent_id,
                        now,
                        now,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise ValidationError(f"work item already exists: {work_id}") from exc
            self._event(
                conn,
                "publish",
                request.scope,
                work_id,
                request.creator,
                None,
                {"objective": request.objective, "acceptance": request.acceptance},
            )
        return self.inspect(request.scope, work_id)

    def discover(self, request: DiscoverRequest) -> dict[str, Any]:
        """Return eligible frontier and observable reasons for exclusions."""

        _require_text(request.scope, "scope")
        _require_text(request.activation_id, "activation_id")
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM work_items WHERE scope = ? ORDER BY created_at, id",
                (request.scope,),
            ).fetchall()
            items: list[dict[str, Any]] = []
            reasons: dict[str, int] = {}
            for row in rows:
                eligible, reason = self._eligible_for_discovery(row, request.agent)
                if eligible:
                    items.append(_work_row(row))
                else:
                    reasons[reason] = reasons.get(reason, 0) + 1
            result = {
                "scope": request.scope,
                "agent_id": request.agent.agent_id,
                "activation_id": request.activation_id,
                "items": items,
                "status": "eligible_work" if items else "no_eligible_work",
                "filter_reasons": reasons,
            }
            self._event(
                conn,
                "discover",
                request.scope,
                None,
                request.agent,
                request.activation_id,
                {"eligible_count": len(items), "filter_reasons": reasons},
            )
            return result

    def claim(self, request: ClaimRequest) -> dict[str, Any]:
        """Atomically claim one available Work Item for one activation."""

        return self._claim(request, "execution", request.agent)

    def publish_result(self, request: PublishResultRequest) -> dict[str, Any]:
        """Publish execution result and required Git provenance."""

        _require_result(request)
        with self._connection() as conn:
            row = self._get_row(conn, request.scope, request.work_id)
            self._require_execution_claim(conn, request.work_id, request.agent.agent_id)
            if row["state"] != "claimed":
                raise ValidationError(f"work item is not claimed: {row['state']}")
            conn.execute(
                """
                UPDATE work_items
                SET result_summary = ?, next_action = ?, acceptance_status = ?,
                    references_json = ?, updated_at = ?, revision = revision + 1
                WHERE id = ?
                """,
                (
                    request.result_summary,
                    request.next_action,
                    request.acceptance_status,
                    _json(list(request.references)),
                    _now(),
                    request.work_id,
                ),
            )
            self._event(
                conn,
                "publish_result",
                request.scope,
                request.work_id,
                request.agent,
                None,
                {
                    "acceptance_status": request.acceptance_status,
                    "references": list(request.references),
                },
            )
            return self.inspect(request.scope, request.work_id, conn=conn)

    def submit(self, scope: str, work_id: str, agent: AgentProfile) -> dict[str, Any]:
        """Move a claimed result to the reviewer frontier."""

        with self._connection() as conn:
            row = self._get_row(conn, scope, work_id)
            self._require_execution_claim(conn, work_id, agent.agent_id)
            if row["state"] != "claimed" or not row["result_summary"]:
                raise ValidationError("submit requires a claimed work item with a result")
            conn.execute(
                "UPDATE work_items SET state = 'awaiting_agent_review', updated_at = ?, revision = revision + 1 WHERE id = ?",
                (_now(), work_id),
            )
            conn.execute(
                "UPDATE claims SET active = 0 WHERE work_id = ? AND kind = 'execution' AND active = 1",
                (work_id,),
            )
            self._event(conn, "submit", scope, work_id, agent, None, {})
            return self.inspect(scope, work_id, conn=conn)

    def block(self, request: BlockRequest) -> dict[str, Any]:
        """Publish a structured blocker and make the Work Item blocked."""

        for value, name in (
            (request.category, "category"),
            (request.observed_facts, "observed_facts"),
            (request.attempted_actions, "attempted_actions"),
            (request.required_decision, "required_decision"),
            (request.next_action, "next_action"),
        ):
            _require_text(value, name)
        with self._connection() as conn:
            row = self._get_row(conn, request.scope, request.work_id)
            self._require_execution_claim(conn, request.work_id, request.agent.agent_id)
            if row["state"] != "claimed":
                raise ValidationError(f"work item is not claimed: {row['state']}")
            blocker = {
                "category": request.category,
                "observed_facts": request.observed_facts,
                "attempted_actions": request.attempted_actions,
                "required_decision": request.required_decision,
                "next_action": request.next_action,
            }
            conn.execute(
                "UPDATE work_items SET state = 'blocked', blocker_json = ?, next_action = ?, updated_at = ?, revision = revision + 1 WHERE id = ?",
                (_json(blocker), request.next_action, _now(), request.work_id),
            )
            conn.execute(
                "UPDATE claims SET active = 0 WHERE work_id = ? AND active = 1",
                (request.work_id,),
            )
            self._event(conn, "block", request.scope, request.work_id, request.agent, None, blocker)
            return self.inspect(request.scope, request.work_id, conn=conn)

    def reopen(self, request: ReopenRequest) -> dict[str, Any]:
        """Explicitly return a stale or blocked Work Item to the frontier.

        This is a Human exception path, not automatic recovery. It clears
        execution/review ownership and records the operator's reason while
        preserving the Work Item and its event history.
        """

        for value, name in (
            (request.scope, "scope"),
            (request.work_id, "work_id"),
            (request.operator_id, "operator_id"),
            (request.reason, "reason"),
        ):
            _require_text(value, name)
        with self._connection() as conn:
            row = self._get_row(conn, request.scope, request.work_id)
            if row["state"] not in {"claimed", "blocked"}:
                raise ValidationError(
                    f"only claimed or blocked work items can be reopened: {row['state']}"
                )
            previous_state = row["state"]
            previous_claimant = row["claimant"]
            conn.execute(
                """
                UPDATE work_items
                SET state = 'available', claimant = NULL, result_summary = NULL,
                    next_action = NULL, acceptance_status = NULL,
                    references_json = NULL, blocker_json = NULL,
                    updated_at = ?, revision = revision + 1
                WHERE id = ?
                """,
                (_now(), request.work_id),
            )
            conn.execute(
                "UPDATE claims SET active = 0 WHERE work_id = ? AND active = 1",
                (request.work_id,),
            )
            self._event(
                conn,
                "human_reopened",
                request.scope,
                request.work_id,
                None,
                None,
                {
                    "operator_id": request.operator_id,
                    "reason": request.reason,
                    "previous_state": previous_state,
                    "previous_claimant": previous_claimant,
                },
            )
            return self.inspect(request.scope, request.work_id, conn=conn)

    def claim_review(self, request: ClaimReviewRequest) -> dict[str, Any]:
        """Atomically claim one awaiting-agent-review Work Item."""

        if not request.reviewer.can_review:
            raise EligibilityError("agent profile cannot review work")
        return self._claim(request, "review", request.reviewer)

    def review(self, request: ReviewRequest) -> dict[str, Any]:
        """Accept, return, or escalate a claimed review."""

        if request.decision not in {"accept", "request_changes", "escalate"}:
            raise ValidationError("invalid review decision")
        with self._connection() as conn:
            row = self._get_row(conn, request.scope, request.work_id)
            self._require_active_claim(conn, request.work_id, request.reviewer.agent_id, "review")
            if row["state"] != "awaiting_agent_review":
                raise ValidationError(f"work item is not awaiting review: {row['state']}")
            if request.decision == "accept":
                new_state: WorkState = "completed"
                event_type = "review_completed"
            elif request.decision == "request_changes":
                new_state = "available"
                event_type = "review_changes_requested"
            else:
                new_state = "blocked"
                event_type = "review_escalated"
            conn.execute(
                "UPDATE work_items SET state = ?, claimant = CASE WHEN ? = 'available' THEN NULL ELSE claimant END, updated_at = ?, revision = revision + 1 WHERE id = ?",
                (new_state, new_state, _now(), request.work_id),
            )
            conn.execute(
                "UPDATE claims SET active = 0 WHERE work_id = ? AND kind = 'review' AND active = 1",
                (request.work_id,),
            )
            self._event(
                conn,
                event_type,
                request.scope,
                request.work_id,
                request.reviewer,
                None,
                {"decision": request.decision, "note": request.note},
            )
            return self.inspect(request.scope, request.work_id, conn=conn)

    def inspect(self, scope: str, work_id: str, conn: sqlite3.Connection | None = None) -> dict[str, Any]:
        """Read one Work Item and its shared facts."""

        if conn is not None:
            return _work_row(self._get_row(conn, scope, work_id))
        with self._connection() as own_conn:
            return _work_row(self._get_row(own_conn, scope, work_id))

    def scorecard(self, scope: str) -> str:
        """Render an auditable Markdown health scorecard for one scope."""

        with self._connection() as conn:
            events = conn.execute(
                "SELECT * FROM events WHERE scope = ? ORDER BY sequence", (scope,)
            ).fetchall()
            works = conn.execute(
                "SELECT * FROM work_items WHERE scope = ? ORDER BY created_at, id", (scope,)
            ).fetchall()
        counts: dict[str, int] = {}
        for event in events:
            counts[event["type"]] = counts.get(event["type"], 0) + 1
        publish_count = counts.get("publish", 0)
        discover_events = [e for e in events if e["type"] == "discover"]
        discover_success = sum(
            1 for e in discover_events if json.loads(e["payload_json"]).get("eligible_count", 0) > 0
        )
        claim_attempts = counts.get("claim_succeeded", 0) + counts.get("claim_conflict", 0)
        completed = sum(1 for work in works if work["state"] == "completed")
        review_success = counts.get("claim_review_succeeded", 0)
        lines = [
            "# Experience Version collaboration scorecard",
            "",
            f"- Scope: `{scope}`",
            f"- Generated at: `{_now()}`",
            "",
            "## Health metrics",
            "",
            f"- Eligible discovery rate: {discover_success}/{len(discover_events)}",
            f"- Claim success/conflict: {counts.get('claim_succeeded', 0)}/{counts.get('claim_conflict', 0)}",
            f"- Work completion rate: {completed}/{publish_count}",
            f"- Handoff continuation (review claims): {review_success}",
            f"- Context defects: {counts.get('context_defect', 0)}",
            f"- Activations observed: {len({e['activation_id'] for e in discover_events if e['activation_id']})}",
            "",
            "## Hard gates",
            "",
            f"- C1 publish/discover: {'PASS' if publish_count and discover_success else 'PENDING'}",
            f"- C2 competing claim: {'PASS' if counts.get('claim_conflict', 0) and counts.get('claim_succeeded', 0) else 'PENDING'}",
            f"- C3 result publication: {'PASS' if counts.get('publish_result', 0) else 'PENDING'}",
            f"- C4 review continuation: {'PASS' if counts.get('review_completed', 0) else 'PENDING'}",
            "",
            "## Work Items",
            "",
            "| id | state | claimant | acceptance | references |",
            "| --- | --- | --- | --- | --- |",
        ]
        for work in works:
            refs = json.loads(work["references_json"] or "[]")
            lines.append(
                f"| `{work['id']}` | `{work['state']}` | `{work['claimant'] or ''}` | "
                f"`{work['acceptance_status'] or ''}` | {len(refs)} |"
            )
        return "\n".join(lines) + "\n"

    def _claim(self, request: ClaimRequest | ClaimReviewRequest, kind: ClaimKind, agent: AgentProfile) -> dict[str, Any]:
        scope = request.scope
        work_id = request.work_id
        activation_id = request.activation_id
        with self._connection() as conn:
            row = self._get_row(conn, scope, work_id)
            if kind == "execution":
                eligible, reason = self._eligible_for_discovery(row, agent, execution=True)
            else:
                eligible, reason = self._eligible_for_discovery(row, agent, review=True)
            if not eligible:
                conn.rollback()
                self._record_event("claim_conflict", scope, work_id, agent, activation_id, {"reason": reason})
                raise EligibilityError(reason)
            try:
                conn.execute(
                    "INSERT INTO activation_claims (activation_id, work_id, agent_id, kind, created_at) VALUES (?, ?, ?, ?, ?)",
                    (activation_id, work_id, agent.agent_id, kind, _now()),
                )
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                self._record_event(
                    "claim_conflict",
                    scope,
                    work_id,
                    agent,
                    activation_id,
                    {"reason": "activation_already_claimed"},
                )
                raise CoordinationError("activation already claimed a Work Item") from exc
            try:
                conn.execute(
                    "INSERT INTO claims (work_id, agent_id, kind, active, created_at) VALUES (?, ?, ?, 1, ?)",
                    (work_id, agent.agent_id, kind, _now()),
                )
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                self._record_event(
                    "claim_conflict",
                    scope,
                    work_id,
                    agent,
                    activation_id,
                    {"reason": "work_item_already_claimed"},
                )
                raise CoordinationError("work item is already claimed") from exc
            new_state: WorkState = "claimed" if kind == "execution" else "awaiting_agent_review"
            claimant = agent.agent_id if kind == "execution" else row["claimant"]
            conn.execute(
                "UPDATE work_items SET state = ?, claimant = ?, updated_at = ?, revision = revision + 1 WHERE id = ?",
                (new_state, claimant, _now(), work_id),
            )
            self._event(conn, "claim_succeeded" if kind == "execution" else "claim_review_succeeded", scope, work_id, agent, activation_id, {"kind": kind})
            result = self.inspect(scope, work_id, conn=conn)
            result["claim"] = {"agent_id": agent.agent_id, "kind": kind, "activation_id": activation_id}
            return result

    def _initialize(self) -> None:
        with self._connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS work_items (
                  id TEXT PRIMARY KEY,
                  scope TEXT NOT NULL,
                  objective TEXT NOT NULL,
                  acceptance TEXT NOT NULL,
                  required_capabilities TEXT NOT NULL,
                  required_permissions TEXT NOT NULL,
                  state TEXT NOT NULL,
                  creator TEXT NOT NULL,
                  claimant TEXT,
                  result_summary TEXT,
                  next_action TEXT,
                  acceptance_status TEXT,
                  references_json TEXT,
                  blocker_json TEXT,
                  revision INTEGER NOT NULL,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS claims (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  work_id TEXT NOT NULL REFERENCES work_items(id),
                  agent_id TEXT NOT NULL,
                  kind TEXT NOT NULL,
                  active INTEGER NOT NULL,
                  created_at TEXT NOT NULL
                );
                CREATE UNIQUE INDEX IF NOT EXISTS active_work_claim
                  ON claims(work_id, kind) WHERE active = 1;
                CREATE TABLE IF NOT EXISTS activation_claims (
                  activation_id TEXT PRIMARY KEY,
                  work_id TEXT NOT NULL,
                  agent_id TEXT NOT NULL,
                  kind TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                  type TEXT NOT NULL,
                  scope TEXT NOT NULL,
                  work_id TEXT,
                  agent_id TEXT,
                  activation_id TEXT,
                  payload_json TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                """
            )

    @contextmanager
    def _connection(self) -> Iterable[sqlite3.Connection]:
        """Open one transaction-scoped connection and always close it."""

        conn = sqlite3.connect(self.database, timeout=10, isolation_level="IMMEDIATE", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _get_row(self, conn: sqlite3.Connection, scope: str, work_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM work_items WHERE id = ? AND scope = ?", (work_id, scope)).fetchone()
        if row is None:
            raise NotFoundError(f"work item not found in scope: {work_id}")
        return row

    def _eligible_for_discovery(
        self,
        row: sqlite3.Row,
        agent: AgentProfile,
        *,
        execution: bool = False,
        review: bool = False,
    ) -> tuple[bool, str]:
        state: WorkState = row["state"]
        required_capabilities = set(json.loads(row["required_capabilities"]))
        required_permissions = set(json.loads(row["required_permissions"]))
        if execution and state != "available":
            return False, f"state_{state}"
        if review and (state != "awaiting_agent_review" or not agent.can_review):
            return False, "review_not_eligible"
        if not execution and not review:
            if state == "available":
                execution = True
            elif state == "awaiting_agent_review" and agent.can_review:
                review = True
            else:
                return False, f"state_{state}"
        if execution and not required_capabilities.issubset(agent.capabilities):
            return False, "missing_capability"
        if execution and not required_permissions.issubset(agent.permissions):
            return False, "missing_permission"
        if review and row["claimant"] == agent.agent_id:
            return False, "claimant_not_reviewer"
        return True, "eligible"

    def _require_execution_claim(self, conn: sqlite3.Connection, work_id: str, agent_id: str) -> None:
        self._require_active_claim(conn, work_id, agent_id, "execution")

    def _require_active_claim(self, conn: sqlite3.Connection, work_id: str, agent_id: str, kind: ClaimKind) -> None:
        row = conn.execute(
            "SELECT 1 FROM claims WHERE work_id = ? AND agent_id = ? AND kind = ? AND active = 1",
            (work_id, agent_id, kind),
        ).fetchone()
        if row is None:
            raise EligibilityError(f"agent does not own active {kind} claim")

    def _event(
        self,
        conn: sqlite3.Connection,
        event_type: str,
        scope: str,
        work_id: str | None,
        agent: AgentProfile | None,
        activation_id: str | None,
        payload: dict[str, Any],
    ) -> None:
        event_payload = dict(payload)
        if agent is not None:
            event_payload.setdefault("device_id", agent.device_id)
        conn.execute(
            "INSERT INTO events (type, scope, work_id, agent_id, activation_id, payload_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (event_type, scope, work_id, agent.agent_id if agent else None, activation_id, _json(event_payload), _now()),
        )

    def _record_event(
        self,
        event_type: str,
        scope: str,
        work_id: str | None,
        agent: AgentProfile | None,
        activation_id: str | None,
        payload: dict[str, Any],
    ) -> None:
        """Persist an event after an operation transaction was rolled back."""

        with self._connection() as conn:
            self._event(conn, event_type, scope, work_id, agent, activation_id, payload)


def _work_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "scope": row["scope"],
        "objective": row["objective"],
        "acceptance": row["acceptance"],
        "required_capabilities": json.loads(row["required_capabilities"]),
        "required_permissions": json.loads(row["required_permissions"]),
        "state": row["state"],
        "creator": row["creator"],
        "claimant": row["claimant"],
        "result_summary": row["result_summary"],
        "next_action": row["next_action"],
        "acceptance_status": row["acceptance_status"],
        "references": json.loads(row["references_json"] or "[]"),
        "blocker": json.loads(row["blocker_json"] or "null"),
        "revision": row["revision"],
    }


def _require_result(request: PublishResultRequest) -> None:
    _require_text(request.result_summary, "result_summary")
    _require_text(request.next_action, "next_action")
    if request.acceptance_status not in {"met", "not_met", "partial"}:
        raise ValidationError("invalid acceptance_status")
    if not request.references:
        raise ValidationError("at least one Git evidence reference is required")
    required = {"commit", "files", "tests"}
    if not required.issubset(request.references[0]):
        raise ValidationError("reference must include commit, files and tests")


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} is required")


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


__all__ = [
    "AgentProfile",
    "BlockRequest",
    "ClaimRequest",
    "ClaimReviewRequest",
    "CoordinationError",
    "CoordinationProtocol",
    "DiscoverRequest",
    "EligibilityError",
    "NotFoundError",
    "PublishRequest",
    "PublishResultRequest",
    "ReopenRequest",
    "ReviewRequest",
    "ValidationError",
]
