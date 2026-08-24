#!/usr/bin/env python3
"""Replay the candidate-neutral C1-C4 black-box fixtures over HTTP.

The runner deliberately treats a candidate's existing task, artifact, or
memory APIs as observations. It never invents a Work Item claim transition
when the candidate does not expose one. Each run records the HTTP transcript,
the Human activation events, and a strict conformance result for every gate.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass, field
from typing import Any, Iterable


PROTOCOL = "zagenticopn-c1-c4-black-box/v1"
DEFAULT_WORKSPACE = "default"
GIT_REFERENCES = {
    "repository": "https://github.com/jununfly/ZAgenticOPN",
    "fixture_protocol": "research/routa-qm-conformance/2026-08-20-conformance-fixture-mapping.md",
}


def candidate_git_references(candidate: str) -> dict[str, str]:
    refs = dict(GIT_REFERENCES)
    refs["candidate_evidence"] = (
        "https://github.com/phodal/routa/tree/e48861ab81e2b30378fd32f05204a3ab424c4fec"
        if candidate == "routa"
        else "https://github.com/yc-software/qm/tree/568252bd4e6da5288b239573abef972f3e16b3f9"
    )
    return refs


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compact(value: Any, limit: int = 4096) -> Any:
    """Keep evidence readable while preserving structured JSON when possible."""

    if isinstance(value, str):
        return value if len(value) <= limit else f"{value[:limit]}…"
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        encoded = repr(value)
    if len(encoded) <= limit:
        return value
    return f"{encoded[:limit]}…"


def json_object(raw: bytes) -> Any:
    if not raw:
        return None
    text = raw.decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


@dataclass
class HttpCall:
    method: str
    path: str
    actor_id: str | None
    status: int | None
    response: Any
    request_body: Any = None
    error: str | None = None


@dataclass
class HttpClient:
    base_url: str
    token_by_actor: dict[str, str] = field(default_factory=dict)
    calls: list[HttpCall] = field(default_factory=list)

    def request(self, method: str, path: str, actor_id: str | None = None, body: Any = None) -> Any:
        url = self.base_url.rstrip("/") + path
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers = {"accept": "application/json"}
        if data is not None:
            headers["content-type"] = "application/json"
        token = self.token_by_actor.get(actor_id or "")
        if token:
            headers["x-agent-capability"] = token
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                raw = response.read()
                status = response.status
                parsed = json_object(raw)
                self.calls.append(HttpCall(method, path, actor_id, status, compact(parsed), compact(body)))
                return parsed
        except urllib.error.HTTPError as error:
            raw = error.read()
            parsed = json_object(raw)
            self.calls.append(HttpCall(method, path, actor_id, error.code, compact(parsed), compact(body)))
            return parsed
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            message = f"{type(error).__name__}: {error}"
            self.calls.append(HttpCall(method, path, actor_id, None, None, compact(body), message))
            return None


def call_dict(call: HttpCall) -> dict[str, Any]:
    result: dict[str, Any] = {
        "method": call.method,
        "path": call.path,
        "actor_id": call.actor_id,
        "status": call.status,
        "response": call.response,
    }
    if call.request_body is not None:
        result["request_body"] = call.request_body
    if call.error is not None:
        result["error"] = call.error
    return result


def status_code(response: Any, client: HttpClient, offset: int) -> int | None:
    """Return the status of the last request in a small operation."""

    del response
    if len(client.calls) <= offset:
        return None
    return client.calls[-1].status


def last_call(client: HttpClient) -> HttpCall:
    return client.calls[-1]


def has_endpoint(api_catalog: Any, method: str, path_fragment: str) -> bool:
    if not isinstance(api_catalog, dict):
        return False
    endpoints = api_catalog.get("endpoints")
    return isinstance(endpoints, list) and any(
        isinstance(item, dict)
        and method in str(item.get("method", ""))
        and path_fragment in str(item.get("path", ""))
        for item in endpoints
    )


def canonical_work_item(run_id: str, candidate: str) -> dict[str, Any]:
    return {
        "work_item_id": f"fixture-{candidate}-{run_id}",
        "title": "C1-C4 candidate-neutral black-box fixture",
        "workspace_id": DEFAULT_WORKSPACE,
        "eligibility": {"role": "producer", "scope": DEFAULT_WORKSPACE},
        "status": "available",
        "references": [
            {
                "repository": "https://github.com/jununfly/ZAgenticOPN",
                "commit": "fixture-canonical-reference",
                "path": "research/routa-qm-conformance/",
            }
        ],
    }


def result_record(run_id: str) -> dict[str, Any]:
    return {
        "work_item_id": f"fixture-result-{run_id}",
        "result_summary": "The producer completed the black-box probe.",
        "next_action": "A reviewer Agent should inspect the recorded evidence.",
        "acceptance_status": "ready_for_review",
        "blocker": None,
        "references": [
            {
                "repository": "https://github.com/jununfly/ZAgenticOPN",
                "commit": "fixture-canonical-reference",
                "path": "research/routa-qm-conformance/",
            }
        ],
    }


def gate(
    status: str,
    strict_pass: bool,
    observations: dict[str, Any],
    calls: Iterable[HttpCall],
) -> dict[str, Any]:
    return {
        "status": status,
        "strict_pass": strict_pass,
        "observations": observations,
        "request_descriptors": [
            {"method": call.method, "path": call.path, "actor_id": call.actor_id, "status": call.status}
            for call in calls
        ],
    }


def routa_run(client: HttpClient, run_id: str) -> dict[str, Any]:
    """Exercise Routa's real task, ready, artifact, and review surfaces."""

    human_events = [{"event": "human.activate", "text": "检查 shared context", "agent_id": "agent-b"}]
    client.request("GET", "/api/health")
    boards = client.request("GET", "/api/kanban/boards?workspaceId=default")
    board_id = None
    if isinstance(boards, dict) and isinstance(boards.get("boards"), list) and boards["boards"]:
        board_id = boards["boards"][0].get("id")

    task_body = {
        "title": f"C1-C4 fixture {run_id}",
        "objective": "Discover, compete, publish structured evidence, and continue review without task-specific Human context",
        "workspaceId": DEFAULT_WORKSPACE,
        "boardId": board_id,
        "columnId": "todo",
        "scope": "The fixed C1-C4 black-box fixture for this run.",
        "acceptanceCriteria": ["The producer result is readable by another Agent."],
        "verificationCommands": ["black-box-fixture --candidate routa"],
        "testCases": ["C1", "C2", "C3", "C4"],
    }
    created = client.request("POST", "/api/tasks", body=task_body)
    task = created.get("task") if isinstance(created, dict) else None
    task_id = task.get("id") if isinstance(task, dict) else None

    ready = client.request("GET", "/api/tasks/ready?workspaceId=default")
    ready_tasks = ready.get("tasks", []) if isinstance(ready, dict) else []
    discovered = next((item for item in ready_tasks if isinstance(item, dict) and item.get("id") == task_id), None)
    c1_calls = client.calls[-3:]
    c1 = gate(
        "partial" if discovered else "unverified",
        False,
        {
            "human_work_item_id": None,
            "discovered_by_agent": "agent-b",
            "task_id": task_id,
            "discovered": discovered is not None,
            "ready_query_has_filter_reasons": bool(
                isinstance(discovered, dict) and "filterReasons" in discovered
            ),
            "strict_gap": "ready task is not Agent-eligibility-aware Work Item discovery",
        },
        c1_calls,
    )

    claim_path = f"/api/tasks/{task_id}/claim" if task_id else "/api/tasks/missing/claim"
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(client.request, "POST", claim_path, actor_id=actor, body={"agentId": actor})
            for actor in ("agent-a", "agent-b")
        ]
        for future in futures:
            future.result()
    claim_calls: list[HttpCall] = client.calls[-2:]
    for path in (
        f"/api/tasks/{task_id}/claims" if task_id else "/api/tasks/missing/claims",
        "/api/work-items",
        "/api/coordination/work-items",
    ):
        client.request("POST", path, actor_id="agent-b", body={"agentId": "agent-b"})
    c2 = gate(
        "conformance_fail",
        False,
        {
            "candidate_claim_endpoint_exposed": any(call.status not in (404, 405) for call in claim_calls),
            "evidence_status": "unsupported_on_exposed_surface",
            "winner": None,
            "loser": None,
            "duplicate_execution": None,
            "strict_gap": "no Work Item claim transaction was exposed by the HTTP surface",
        },
        claim_calls,
    )

    result = result_record(run_id)
    result_artifact = client.request(
        "POST",
        f"/api/tasks/{task_id}/artifacts" if task_id else "/api/tasks/missing/artifacts",
        actor_id="agent-a",
        body={
            "agentId": "agent-a",
            "type": "logs",
            "content": json.dumps(result, ensure_ascii=False, sort_keys=True),
            "context": "C3 structured result fixture",
            "metadata": {"run_id": run_id, "canonical_commit": "fixture-canonical-reference"},
        },
    )
    artifacts = client.request(
        "GET",
        f"/api/tasks/{task_id}/artifacts" if task_id else "/api/tasks/missing/artifacts",
        actor_id="agent-b",
    )
    artifact_rows = artifacts.get("artifacts", []) if isinstance(artifacts, dict) else []
    structured_result = None
    for item in artifact_rows:
        content = item.get("content") if isinstance(item, dict) else None
        if not isinstance(content, str):
            continue
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and all(
            key in parsed for key in ("result_summary", "next_action", "acceptance_status", "blocker", "references")
        ):
            structured_result = parsed
            break
    visible_result = structured_result is not None
    c3 = gate(
        "pass" if visible_result else ("partial" if artifact_rows else "unverified"),
        visible_result,
        {
            "producer_artifact_status": result_artifact is not None,
            "consumer_can_read_artifact": visible_result,
            "required_fields": ["result_summary", "next_action", "acceptance_status", "blocker", "references"],
            "required_fields_in_generic_artifact": visible_result,
            "strict_gap": None if visible_result else "artifact content was not a machine-parseable five-field record",
        },
        client.calls[-2:],
    )

    for artifact_type, content in (
        ("screenshot", "fixture screenshot placeholder"),
        ("test_results", "fixture test results: C1-C4 black-box"),
    ):
        client.request(
            "POST",
            f"/api/tasks/{task_id}/artifacts" if task_id else "/api/tasks/missing/artifacts",
            actor_id="agent-a",
            body={
                "agentId": "agent-a",
                "type": artifact_type,
                "content": content,
                "context": "C4 review gate fixture",
            },
        )
    if task_id:
        client.request(
            "PATCH",
            f"/api/tasks/{task_id}",
            actor_id="agent-a",
            body={
                "completionSummary": result["result_summary"],
                "verificationVerdict": "APPROVED",
                "verificationReport": "C3 generic artifact is readable; typed result schema remains absent.",
                "columnId": "review",
            },
        )
    review_tasks = client.request("GET", "/api/tasks?workspaceId=default", actor_id="agent-b")
    rows = review_tasks.get("tasks", []) if isinstance(review_tasks, dict) else []
    awaiting = next((item for item in rows if isinstance(item, dict) and item.get("id") == task_id), None)
    review_calls = client.calls[-5:]
    review_probe_calls: list[HttpCall] = []
    for path in (
        f"/api/tasks/{task_id}/review/claim" if task_id else "/api/tasks/missing/review/claim",
        f"/api/tasks/{task_id}/review/complete" if task_id else "/api/tasks/missing/review/complete",
        "/api/reviews",
    ):
        before = len(client.calls)
        client.request("POST", path, actor_id="agent-b", body={"agentId": "agent-b"})
        review_probe_calls.append(client.calls[before])
    c4 = gate(
        "partial" if isinstance(awaiting, dict) and awaiting.get("columnId") == "review" else "unverified",
        False,
        {
            "reviewer_activation": "agent-b",
            "awaiting_review_visible": isinstance(awaiting, dict) and awaiting.get("columnId") == "review",
            "review_claim_endpoint_exposed": any(call.status not in (404, 405) for call in review_probe_calls),
            "review_completed": False,
            "strict_gap": "review column visibility is not reviewer Agent claim/verify/complete continuation",
        },
        review_calls + review_probe_calls,
    )

    return {
        "run_id": run_id,
        "candidate": "phodal/routa",
        "candidate_class": "ext",
        "candidate_commit": "e48861ab81e2b30378fd32f05204a3ab424c4fec",
        "base_url": client.base_url,
        "agent_ids": {"producer": "agent-a", "discoverer_reviewer": "agent-b"},
        "device_ids": {"agent-a": "fixture-device-a", "agent-b": "fixture-device-b"},
        "workspace_id": DEFAULT_WORKSPACE,
        "human_events": human_events,
        "canonical_git_references": candidate_git_references("routa"),
        "fixtures": {"C1": c1, "C2": c2, "C3": c3, "C4": c4},
        "task_id": task_id,
        "http_transcript": [call_dict(call) for call in client.calls],
    }


def qm_run(client: HttpClient, run_id: str) -> dict[str, Any]:
    """Exercise qm's real capability catalog and shared-memory surfaces."""

    human_events = [{"event": "human.activate", "text": "检查 shared context", "agent_id": "agent-b"}]
    health = client.request("GET", "/healthz")
    api_catalog = client.request("GET", "/v1/apis", actor_id="agent-a")
    work_item = canonical_work_item(run_id, "qm")
    work_fact = json.dumps(work_item, ensure_ascii=False, sort_keys=True)
    before = len(client.calls)
    publish = client.request("POST", "/v1/memory/facts", actor_id="agent-a", body={"facts": [work_fact]})
    publish_call = client.calls[before]
    before = len(client.calls)
    discovered = client.request(
        "POST", "/v1/memory/search", actor_id="agent-b", body={"query": work_item["work_item_id"], "limit": 10}
    )
    discover_call = client.calls[before]
    found = any(
        isinstance(item, dict) and work_item["work_item_id"] in str(item.get("fact", ""))
        for item in (discovered.get("results", []) if isinstance(discovered, dict) else [])
    )
    canonical_probe_calls: list[HttpCall] = []
    for path in ("/v1/work-items", "/v1/coordination/work-items"):
        before = len(client.calls)
        client.request("GET", path, actor_id="agent-b")
        canonical_probe_calls.append(client.calls[before])
    c1 = gate(
        "partial" if found and publish_call.status == 200 and discover_call.status == 200 else "unverified",
        False,
        {
            "human_work_item_id": None,
            "shared_memory_publish": publish_call.status == 200,
            "shared_memory_discover": found,
            "api_catalog_has_work_item_route": has_endpoint(api_catalog, "GET", "/v1/work-items"),
            "strict_gap": "shared memory fact discovery is not a typed eligible Work Item API",
        },
        [publish_call, discover_call] + canonical_probe_calls,
    )

    claim_calls: list[HttpCall] = []
    claim_path = f"/v1/work-items/{work_item['work_item_id']}/claim"
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(client.request, "POST", claim_path, actor_id=actor, body={"agentId": actor})
            for actor in ("agent-a", "agent-b")
        ]
        for future in futures:
            future.result()
    claim_calls = client.calls[-2:]
    c2 = gate(
        "conformance_fail",
        False,
        {
            "concurrent_claim_responses": [call.status for call in claim_calls],
            "evidence_status": "unsupported_on_exposed_surface",
            "winner": None,
            "loser": None,
            "duplicate_execution": None,
            "strict_gap": "no Work Item claim endpoint is exposed; memory writes do not establish execution authority",
        },
        claim_calls,
    )

    result = result_record(run_id)
    result_fact = json.dumps(result, ensure_ascii=False, sort_keys=True)
    before = len(client.calls)
    result_publish = client.request("POST", "/v1/memory/facts", actor_id="agent-a", body={"facts": [result_fact]})
    result_publish_call = client.calls[before]
    before = len(client.calls)
    result_read = client.request(
        "POST", "/v1/memory/search", actor_id="agent-b", body={"query": result["work_item_id"], "limit": 10}
    )
    result_read_call = client.calls[before]
    result_facts = result_read.get("results", []) if isinstance(result_read, dict) else []
    result_text = next(
        (item.get("fact") for item in result_facts if isinstance(item, dict) and result["work_item_id"] in str(item.get("fact", ""))),
        "",
    )
    result_fields = {}
    try:
        decoded = json.loads(result_text.split(") ", 1)[1] if ") " in result_text else result_text)
        result_fields = {key: key in decoded for key in ("result_summary", "next_action", "acceptance_status", "blocker", "references")}
    except (TypeError, json.JSONDecodeError):
        result_fields = {key: False for key in ("result_summary", "next_action", "acceptance_status", "blocker", "references")}
    c3 = gate(
        "pass" if all(result_fields.values()) and result_publish_call.status == 200 and result_read_call.status == 200 else "unverified",
        all(result_fields.values()) and result_publish_call.status == 200 and result_read_call.status == 200,
        {
            "shared_memory_publish": result_publish_call.status == 200,
            "consumer_can_read_result": result_text != "",
            "required_fields": result_fields,
            "strict_gap": None if all(result_fields.values()) else "memory fact was not a machine-parseable five-field record",
        },
        [result_publish_call, result_read_call],
    )

    review = {**result, "status": "awaiting_review", "reviewer_role": "reviewer"}
    review_fact = json.dumps(review, ensure_ascii=False, sort_keys=True)
    before = len(client.calls)
    review_publish = client.request("POST", "/v1/memory/facts", actor_id="agent-a", body={"facts": [review_fact]})
    review_publish_call = client.calls[before]
    before = len(client.calls)
    review_read = client.request(
        "POST", "/v1/memory/search", actor_id="agent-b", body={"query": review["work_item_id"], "limit": 10}
    )
    review_read_call = client.calls[before]
    review_probe_calls: list[HttpCall] = []
    for path in (
        f"/v1/work-items/{review['work_item_id']}/review/claim",
        f"/v1/work-items/{review['work_item_id']}/review/complete",
        "/v1/reviews",
    ):
        before = len(client.calls)
        client.request("POST", path, actor_id="agent-b", body={"agentId": "agent-b"})
        review_probe_calls.append(client.calls[before])
    review_found = any(
        isinstance(item, dict) and review["work_item_id"] in str(item.get("fact", ""))
        for item in (review_read.get("results", []) if isinstance(review_read, dict) else [])
    )
    c4 = gate(
        "partial" if review_found and review_publish_call.status == 200 and review_read_call.status == 200 else "unverified",
        False,
        {
            "reviewer_activation": "agent-b",
            "shared_memory_review_discover": review_found,
            "review_claim_endpoint_exposed": has_endpoint(api_catalog, "POST", "/v1/work-items")
            or has_endpoint(api_catalog, "POST", "/v1/reviews"),
            "review_completed": False,
            "strict_gap": "shared memory discovery has no reviewer claim, reference verification, or completion transition",
        },
        [review_publish_call, review_read_call] + review_probe_calls,
    )

    return {
        "run_id": run_id,
        "candidate": "yc-software/qm",
        "candidate_class": "ref",
        "candidate_commit": "568252bd4e6da5288b239573abef972f3e16b3f9",
        "base_url": client.base_url,
        "agent_ids": {"producer": "agent-a", "discoverer_reviewer": "agent-b"},
        "device_ids": {"agent-a": "fixture-device-a", "agent-b": "fixture-device-b"},
        "workspace_id": "org:fixture",
        "human_events": human_events,
        "canonical_git_references": candidate_git_references("qm"),
        "fixtures": {"C1": c1, "C2": c2, "C3": c3, "C4": c4},
        "health_ok": isinstance(health, dict) and health.get("ok") is True,
        "http_transcript": [call_dict(call) for call in client.calls],
    }


def run_candidate(candidate: str, base_url: str, runs: int, tokens: dict[str, str], output: str) -> None:
    all_runs: list[dict[str, Any]] = []
    for index in range(1, runs + 1):
        run_id = f"{candidate}-run-{index}-{uuid.uuid4().hex[:8]}"
        client = HttpClient(base_url, tokens)
        all_runs.append(routa_run(client, run_id) if candidate == "routa" else qm_run(client, run_id))
    result = {
        "protocol": PROTOCOL,
        "generated_at": utc_now(),
        "candidate": candidate,
        "runs_requested": runs,
        "runs": all_runs,
        "strict_gate_summary": {
            gate_name: {
                "pass_count": sum(1 for run in all_runs if run["fixtures"][gate_name]["strict_pass"]),
                "statuses": [run["fixtures"][gate_name]["status"] for run in all_runs],
            }
            for gate_name in ("C1", "C2", "C3", "C4")
        },
    }
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", choices=("routa", "qm"), required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--output", required=True)
    parser.add_argument("--token-a", default=os.environ.get("QM_AGENT_A_TOKEN", ""))
    parser.add_argument("--token-b", default=os.environ.get("QM_AGENT_B_TOKEN", ""))
    args = parser.parse_args(argv)
    if args.runs < 1:
        parser.error("--runs must be at least 1")
    if args.candidate == "qm" and (not args.token_a or not args.token_b):
        parser.error("qm requires --token-a/--token-b or QM_AGENT_A_TOKEN/QM_AGENT_B_TOKEN")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    tokens = {"agent-a": args.token_a, "agent-b": args.token_b} if args.candidate == "qm" else {}
    run_candidate(args.candidate, args.base_url, args.runs, tokens, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
