"""Black-box tests for the task-agnostic activation entrypoint."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from zagentic_opn import (
    AgentProfile,
    ClaimRequest,
    CoordinationProtocol,
    PublishRequest,
    PublishResultRequest,
)


class ActivationBlackBoxTests(unittest.TestCase):
    scope = "zagenticopn/experience-version"
    root = Path(__file__).resolve().parents[1]

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = Path(self.temp_dir.name) / "shared.sqlite3"
        self.codex = AgentProfile(
            "codex-01", "device-a", frozenset({"technical-writing"}), frozenset({"zagentic-skill-write"}), True
        )
        self.workbuddy = AgentProfile(
            "workbuddy-01", "device-a", frozenset({"technical-writing"}), frozenset({"zagentic-skill-write"})
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_external_activation_discovers_and_claims_without_work_item_id(self) -> None:
        self._publish("activation-c1")
        command = self._activation_command(self.workbuddy)
        self.assertNotIn("--work-id", command)
        result = self._run(command)
        self.assertEqual(result["status"], "claimed")
        self.assertEqual(result["kind"], "execution")
        self.assertEqual(result["work"]["id"], "activation-c1")
        self.assertEqual(result["discovery"]["status"], "eligible_work")

    def test_external_activation_claims_review_frontier_without_context_copy(self) -> None:
        protocol = CoordinationProtocol(self.db)
        work_id = self._publish("activation-c4")
        protocol.claim(ClaimRequest(self.scope, work_id, self.workbuddy, "seed-execution"))
        protocol.publish_result(
            PublishResultRequest(
                self.scope,
                work_id,
                self.workbuddy,
                "Result is ready for review.",
                "Codex verifies the pinned commit.",
                "met",
                ({"commit": "abc1234", "files": ["SKILL.md"], "tests": ["pass"]},),
            )
        )
        protocol.submit(self.scope, work_id, self.workbuddy)

        result = self._run(self._activation_command(self.codex, can_review=True))
        self.assertEqual(result["status"], "claimed")
        self.assertEqual(result["kind"], "review")
        self.assertEqual(result["work"]["id"], work_id)
        self.assertEqual(result["work"]["next_action"], "Codex verifies the pinned commit.")
        self.assertNotIn("result_summary", result["discovery"].get("prompt", ""))

    def _publish(self, work_id: str) -> str:
        return CoordinationProtocol(self.db).publish(
            PublishRequest(
                self.scope,
                "Improve the zj-research-report skill.",
                "A verifiable Git artifact is reviewed and accepted.",
                self.codex,
                frozenset({"technical-writing"}),
                frozenset({"zagentic-skill-write"}),
                work_id,
            )
        )["id"]

    def _activation_command(self, agent: AgentProfile, *, can_review: bool = False) -> list[str]:
        command = [
            sys.executable,
            str(self.root / "scripts" / "activate_agent.py"),
            "--db",
            str(self.db),
            "--scope",
            self.scope,
            "--agent-id",
            agent.agent_id,
            "--device-id",
            agent.device_id,
            "--capabilities",
            ",".join(sorted(agent.capabilities)),
            "--permissions",
            ",".join(sorted(agent.permissions)),
            "--activation-id",
            f"blackbox-{agent.agent_id}",
        ]
        if can_review:
            command.append("--can-review")
        return command

    def _run(self, command: list[str]) -> dict[str, object]:
        completed = subprocess.run(command, cwd=self.root, check=True, capture_output=True, text=True)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
