"""Run one task-agnostic Agent activation against the local shared context."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from zagentic_opn import ActivationAdapter, ActivationRequest, AgentProfile, CoordinationProtocol


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover and claim at most one eligible Work Item; do not provide a Work Item id."
    )
    parser.add_argument("--db", type=Path, default=Path(os.getenv("ZAGENTICOPN_DB", ".zagenticopn/shared.sqlite3")))
    parser.add_argument("--scope", default=os.getenv("ZAGENTICOPN_SCOPE", "zagenticopn/experience-version"))
    parser.add_argument("--agent-id", default=os.getenv("ZAGENTICOPN_AGENT_ID"), required=not bool(os.getenv("ZAGENTICOPN_AGENT_ID")))
    parser.add_argument("--device-id", default=os.getenv("ZAGENTICOPN_DEVICE_ID"), required=not bool(os.getenv("ZAGENTICOPN_DEVICE_ID")))
    parser.add_argument("--capabilities", default=os.getenv("ZAGENTICOPN_CAPABILITIES", ""))
    parser.add_argument("--permissions", default=os.getenv("ZAGENTICOPN_PERMISSIONS", ""))
    parser.add_argument("--activation-id", default=os.getenv("ZAGENTICOPN_ACTIVATION_ID"))
    parser.add_argument("--can-review", action="store_true")
    args = parser.parse_args()
    activation_id = args.activation_id or f"activation-{uuid.uuid4().hex[:12]}"
    agent = AgentProfile(
        args.agent_id,
        args.device_id,
        _split(args.capabilities),
        _split(args.permissions),
        args.can_review,
    )
    result = ActivationAdapter(CoordinationProtocol(args.db)).activate(
        ActivationRequest(args.scope, agent, activation_id)
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 2 if result["status"] == "claim_conflict" else 0


def _split(value: str) -> frozenset[str]:
    return frozenset(item.strip() for item in value.split(",") if item.strip())


if __name__ == "__main__":
    raise SystemExit(main())
