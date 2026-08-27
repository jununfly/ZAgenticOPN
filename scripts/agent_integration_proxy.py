"""Expose the local Agent Integration Proxy as a one-request JSON host seam."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from zagentic_opn import (  # noqa: E402
    AgentIntegrationProxy,
    AgentProfile,
    CoordinationProtocol,
    ProxyRequest,
)


def main() -> int:
    configured_scope = os.getenv("ZAGENTICOPN_SCOPE")
    parser = argparse.ArgumentParser(
        description="Prepare one model request from a task-agnostic activation; do not provide a Work Item id."
    )
    parser.add_argument("--db", type=Path, default=Path(os.getenv("ZAGENTICOPN_DB", ".zagenticopn/shared.sqlite3")))
    parser.add_argument("--scope", default=configured_scope, required=not bool(configured_scope))
    parser.add_argument("--agent-id", default=os.getenv("ZAGENTICOPN_AGENT_ID"), required=not bool(os.getenv("ZAGENTICOPN_AGENT_ID")))
    parser.add_argument("--device-id", default=os.getenv("ZAGENTICOPN_DEVICE_ID"), required=not bool(os.getenv("ZAGENTICOPN_DEVICE_ID")))
    parser.add_argument("--capabilities", default=os.getenv("ZAGENTICOPN_CAPABILITIES", ""))
    parser.add_argument("--permissions", default=os.getenv("ZAGENTICOPN_PERMISSIONS", ""))
    parser.add_argument("--activation-id", default=os.getenv("ZAGENTICOPN_ACTIVATION_ID"))
    parser.add_argument("--can-review", action="store_true")
    args = parser.parse_args()

    payload = json.load(sys.stdin)
    agent = AgentProfile(
        args.agent_id,
        args.device_id,
        _split(args.capabilities),
        _split(args.permissions),
        args.can_review,
    )
    result = AgentIntegrationProxy(CoordinationProtocol(args.db)).prepare(
        ProxyRequest(
            message=payload["message"],
            scope=args.scope,
            agent=agent,
            activation_id=payload.get("activation_id") or args.activation_id or f"activation-{uuid.uuid4().hex[:12]}",
        )
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 2 if result["status"] == "claim_conflict" else 0


def _split(value: str) -> frozenset[str]:
    return frozenset(item.strip() for item in value.split(",") if item.strip())


if __name__ == "__main__":
    raise SystemExit(main())
