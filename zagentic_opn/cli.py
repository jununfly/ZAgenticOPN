"""JSON CLI projection of the Experience Version coordination seam."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .coordination import (
    AgentProfile,
    BlockRequest,
    ClaimRequest,
    ClaimReviewRequest,
    CoordinationProtocol,
    DiscoverRequest,
    PublishRequest,
    PublishResultRequest,
    ReopenRequest,
    ReviewRequest,
)


def main(argv: list[str] | None = None) -> int:
    """Run one coordination operation and print JSON or Markdown."""

    parser = argparse.ArgumentParser(prog="zagentic-opn")
    parser.add_argument("--db", required=True, help="SQLite shared-context path")
    subparsers = parser.add_subparsers(dest="command", required=True)
    _publish_parser(subparsers)
    _discover_parser(subparsers)
    _claim_parser(subparsers)
    _result_parser(subparsers)
    _submit_parser(subparsers)
    _review_parser(subparsers)
    _block_parser(subparsers)
    _reopen_parser(subparsers)
    scorecard = subparsers.add_parser("scorecard")
    scorecard.add_argument("--scope", required=True)
    scorecard.add_argument("--out")
    args = parser.parse_args(argv)
    protocol = CoordinationProtocol(Path(args.db))
    try:
        output = _dispatch(protocol, args)
    except Exception as error:  # CLI converts typed seam errors into a stable wire result.
        print(json.dumps({"error": type(error).__name__, "message": str(error)}, ensure_ascii=False))
        return 2
    if isinstance(output, str):
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        else:
            print(output, end="")
    else:
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0


def _publish_parser(subparsers: Any) -> None:
    parser = subparsers.add_parser("publish")
    parser.add_argument("--scope", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--acceptance", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--capabilities", default="")
    parser.add_argument("--permissions", default="")
    parser.add_argument("--work-id")


def _discover_parser(subparsers: Any) -> None:
    parser = subparsers.add_parser("discover")
    parser.add_argument("--scope", required=True)
    _agent_args(parser)
    parser.add_argument("--activation-id", required=True)


def _claim_parser(subparsers: Any) -> None:
    parser = subparsers.add_parser("claim")
    parser.add_argument("--scope", required=True)
    parser.add_argument("--work-id", required=True)
    _agent_args(parser)
    parser.add_argument("--activation-id", required=True)


def _result_parser(subparsers: Any) -> None:
    parser = subparsers.add_parser("publish-result")
    parser.add_argument("--scope", required=True)
    parser.add_argument("--work-id", required=True)
    _agent_args(parser)
    parser.add_argument("--result-summary", required=True)
    parser.add_argument("--next-action", required=True)
    parser.add_argument("--acceptance-status", choices=("met", "not_met", "partial"), required=True)
    parser.add_argument("--references", required=True, help="JSON array containing commit, files and tests")


def _submit_parser(subparsers: Any) -> None:
    parser = subparsers.add_parser("submit")
    parser.add_argument("--scope", required=True)
    parser.add_argument("--work-id", required=True)
    _agent_args(parser)


def _review_parser(subparsers: Any) -> None:
    parser = subparsers.add_parser("claim-review")
    parser.add_argument("--scope", required=True)
    parser.add_argument("--work-id", required=True)
    _agent_args(parser, review=True)
    parser.add_argument("--activation-id", required=True)
    review = subparsers.add_parser("review")
    review.add_argument("--scope", required=True)
    review.add_argument("--work-id", required=True)
    _agent_args(review, review=True)
    review.add_argument("--decision", choices=("accept", "request_changes", "escalate"), required=True)
    review.add_argument("--note", default="")


def _block_parser(subparsers: Any) -> None:
    parser = subparsers.add_parser("block")
    parser.add_argument("--scope", required=True)
    parser.add_argument("--work-id", required=True)
    _agent_args(parser)
    parser.add_argument("--category", required=True)
    parser.add_argument("--observed-facts", required=True)
    parser.add_argument("--attempted-actions", required=True)
    parser.add_argument("--required-decision", required=True)
    parser.add_argument("--next-action", required=True)


def _reopen_parser(subparsers: Any) -> None:
    parser = subparsers.add_parser("reopen")
    parser.add_argument("--scope", required=True)
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--operator-id", required=True)
    parser.add_argument("--reason", required=True)


def _agent_args(parser: Any, *, review: bool = False) -> None:
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--capabilities", default="")
    parser.add_argument("--permissions", default="")
    if review:
        parser.set_defaults(can_review=True)
    else:
        parser.add_argument("--can-review", action="store_true")


def _dispatch(protocol: CoordinationProtocol, args: argparse.Namespace) -> dict[str, Any] | str:
    if args.command == "publish":
        return protocol.publish(PublishRequest(args.scope, args.objective, args.acceptance, _agent(args), _set(args.capabilities), _set(args.permissions), args.work_id))
    if args.command == "discover":
        return protocol.discover(DiscoverRequest(args.scope, _agent(args), args.activation_id))
    if args.command == "claim":
        return protocol.claim(ClaimRequest(args.scope, args.work_id, _agent(args), args.activation_id))
    if args.command == "publish-result":
        return protocol.publish_result(PublishResultRequest(args.scope, args.work_id, _agent(args), args.result_summary, args.next_action, args.acceptance_status, tuple(json.loads(args.references))))
    if args.command == "submit":
        return protocol.submit(args.scope, args.work_id, _agent(args))
    if args.command == "claim-review":
        return protocol.claim_review(ClaimReviewRequest(args.scope, args.work_id, _agent(args), args.activation_id))
    if args.command == "review":
        return protocol.review(ReviewRequest(args.scope, args.work_id, _agent(args), args.decision, args.note))
    if args.command == "block":
        return protocol.block(BlockRequest(args.scope, args.work_id, _agent(args), args.category, args.observed_facts, args.attempted_actions, args.required_decision, args.next_action))
    if args.command == "reopen":
        return protocol.reopen(ReopenRequest(args.scope, args.work_id, args.operator_id, args.reason))
    if args.command == "scorecard":
        return protocol.scorecard(args.scope)
    raise ValueError(f"unknown command: {args.command}")


def _agent(args: argparse.Namespace) -> AgentProfile:
    return AgentProfile(
        args.agent_id,
        args.device_id,
        _set(args.capabilities),
        _set(args.permissions),
        getattr(args, "can_review", False),
    )


def _set(value: str) -> frozenset[str]:
    return frozenset(item for item in (part.strip() for part in value.split(",")) if item)


if __name__ == "__main__":
    sys.exit(main())
