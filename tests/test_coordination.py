"""Black-box C1-C4 fixtures for the Experience Version seam."""

from __future__ import annotations

import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from zagentic_opn import (
    AgentProfile,
    ClaimRequest,
    ClaimReviewRequest,
    CoordinationError,
    CoordinationProtocol,
    DiscoverRequest,
    EligibilityError,
    PublishRequest,
    PublishResultRequest,
    ReopenRequest,
    ReviewRequest,
    ValidationError,
)


class CoordinationBlackBoxTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.protocol = CoordinationProtocol(Path(self.temp_dir.name) / "shared.sqlite3")
        self.codex = AgentProfile(
            agent_id="codex-01",
            device_id="device-a",
            capabilities=frozenset({"technical-writing"}),
            permissions=frozenset({"zagentic-skill-write"}),
            can_review=True,
        )
        self.workbuddy = AgentProfile(
            agent_id="workbuddy-01",
            device_id="device-a",
            capabilities=frozenset({"technical-writing"}),
            permissions=frozenset({"zagentic-skill-write"}),
            can_review=True,
        )
        self.scope = "zagenticopn/experience-version"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def publish_work(self) -> str:
        return self.protocol.publish(
            PublishRequest(
                scope=self.scope,
                objective="Improve the zj-research-report skill with a technical proposal exemplar.",
                acceptance="Update source skill and publish a verifiable Git artifact.",
                creator=self.codex,
                required_capabilities=frozenset({"technical-writing"}),
                required_permissions=frozenset({"zagentic-skill-write"}),
                work_id="work-skill-improvement",
            )
        )["id"]

    def test_c1_task_agnostic_agent_discovers_published_work(self) -> None:
        work_id = self.publish_work()

        discovery = self.protocol.discover(
            DiscoverRequest(self.scope, self.workbuddy, "activation-workbuddy-1")
        )

        self.assertEqual(discovery["status"], "eligible_work")
        self.assertEqual([item["id"] for item in discovery["items"]], [work_id])
        self.assertEqual(discovery["filter_reasons"], {})

    def test_c2_competing_claim_has_one_winner_and_no_duplicate_execution(self) -> None:
        work_id = self.publish_work()
        rival = AgentProfile(
            agent_id="workbuddy-02",
            device_id="device-a",
            capabilities=self.workbuddy.capabilities,
            permissions=self.workbuddy.permissions,
        )

        def claim(agent: AgentProfile, activation: str) -> str:
            return self.protocol.claim(
                ClaimRequest(self.scope, work_id, agent, activation)
            )["claim"]["agent_id"]

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(claim, self.workbuddy, "activation-b-1"),
                executor.submit(claim, rival, "activation-b-2"),
            ]
            outcomes = []
            for future in futures:
                try:
                    outcomes.append(("won", future.result()))
                except CoordinationError as error:
                    outcomes.append(("lost", str(error)))

        self.assertEqual(sum(outcome[0] == "won" for outcome in outcomes), 1)
        self.assertEqual(sum(outcome[0] == "lost" for outcome in outcomes), 1)
        self.assertEqual(self.protocol.inspect(self.scope, work_id)["state"], "claimed")
        self.assertIn("C2 competing claim: PASS", self.protocol.scorecard(self.scope))

    def test_c3_result_publication_exposes_summary_next_action_and_git_reference(self) -> None:
        work_id = self.publish_work()
        self.protocol.claim(
            ClaimRequest(self.scope, work_id, self.workbuddy, "activation-workbuddy-1")
        )

        result = self.protocol.publish_result(
            PublishResultRequest(
                scope=self.scope,
                work_id=work_id,
                agent=self.workbuddy,
                result_summary="Added a technical proposal exemplar and the C4 projection checklist.",
                next_action="Codex reviews the isolated branch and runs the receipt validation.",
                acceptance_status="met",
                references=(
                    {
                        "commit": "abc1234",
                        "files": ["skills/engineering/zj-research-report/SKILL.md"],
                        "tests": ["python quick_validate.py: pass"],
                    },
                ),
            )
        )

        self.assertEqual(result["result_summary"], "Added a technical proposal exemplar and the C4 projection checklist.")
        self.assertEqual(result["next_action"], "Codex reviews the isolated branch and runs the receipt validation.")
        self.assertEqual(result["references"][0]["commit"], "abc1234")

    def test_c4_reviewer_discovers_claims_and_completes_without_context_copy(self) -> None:
        work_id = self.publish_work()
        self.protocol.claim(
            ClaimRequest(self.scope, work_id, self.workbuddy, "activation-workbuddy-1")
        )
        self.protocol.publish_result(
            PublishResultRequest(
                self.scope,
                work_id,
                self.workbuddy,
                "Result is ready for review.",
                "Codex verifies the referenced commit.",
                "met",
                ({"commit": "abc1234", "files": ["SKILL.md"], "tests": ["pass"]},),
            )
        )
        self.protocol.submit(self.scope, work_id, self.workbuddy)

        discovery = self.protocol.discover(
            DiscoverRequest(self.scope, self.codex, "activation-codex-review-1")
        )
        self.assertEqual(discovery["status"], "eligible_work")
        self.assertEqual(discovery["items"][0]["next_action"], "Codex verifies the referenced commit.")

        self.protocol.claim_review(
            ClaimReviewRequest(self.scope, work_id, self.codex, "activation-codex-review-1")
        )
        completed = self.protocol.review(
            ReviewRequest(self.scope, work_id, self.codex, "accept", "Git artifact and tests verified.")
        )
        self.assertEqual(completed["state"], "completed")

    def test_review_request_changes_releases_execution_claim_for_retry(self) -> None:
        work_id = self.publish_work()
        self.protocol.claim(
            ClaimRequest(self.scope, work_id, self.workbuddy, "activation-workbuddy-1")
        )
        self.protocol.publish_result(
            PublishResultRequest(
                self.scope,
                work_id,
                self.workbuddy,
                "The first execution needs a corrected activation trace.",
                "WorkBuddy reruns the task-agnostic activation.",
                "partial",
                ({"commit": "abc1234", "files": ["result.md"], "tests": ["pass"]},),
            )
        )
        self.protocol.submit(self.scope, work_id, self.workbuddy)
        self.protocol.claim_review(
            ClaimReviewRequest(self.scope, work_id, self.codex, "activation-codex-review-1")
        )

        returned = self.protocol.review(
            ReviewRequest(
                self.scope,
                work_id,
                self.codex,
                "request_changes",
                "The activation trace needs a compliant discover before claim.",
            )
        )

        self.assertEqual(returned["state"], "available")
        self.assertIsNone(returned["claimant"])
        self.assertIsNone(returned["result_summary"])
        self.assertIsNone(returned["next_action"])
        self.assertIsNone(returned["acceptance_status"])
        self.assertEqual(returned["references"], [])

        discovery = self.protocol.discover(
            DiscoverRequest(self.scope, self.workbuddy, "activation-workbuddy-retry")
        )
        self.assertEqual(discovery["status"], "eligible_work")
        reclaimed = self.protocol.claim(
            ClaimRequest(self.scope, work_id, self.workbuddy, "activation-workbuddy-retry")
        )
        self.assertEqual(reclaimed["claim"]["agent_id"], "workbuddy-01")

    def test_no_eligible_work_is_observable_and_does_not_invent_work(self) -> None:
        work_id = self.publish_work()
        unqualified = AgentProfile("other", "device-a")

        discovery = self.protocol.discover(
            DiscoverRequest(self.scope, unqualified, "activation-other-1")
        )

        self.assertEqual(discovery["status"], "no_eligible_work")
        self.assertEqual(discovery["items"], [])
        self.assertIn("missing_capability", discovery["filter_reasons"])
        with self.assertRaises(EligibilityError):
            self.protocol.claim(
                ClaimRequest(self.scope, work_id, unqualified, "activation-other-2")
            )

    def test_one_activation_cannot_claim_a_second_work_item(self) -> None:
        first = self.publish_work()
        second = self.protocol.publish(
            PublishRequest(
                self.scope,
                "A second independent work item.",
                "A second result.",
                self.codex,
                frozenset({"technical-writing"}),
                frozenset({"zagentic-skill-write"}),
                "work-second",
            )
        )["id"]
        activation = "activation-workbuddy-single-claim"
        self.protocol.claim(ClaimRequest(self.scope, first, self.workbuddy, activation))
        with self.assertRaises(CoordinationError):
            self.protocol.claim(ClaimRequest(self.scope, second, self.workbuddy, activation))

    def test_human_reopen_releases_stale_claim_without_fabricating_result(self) -> None:
        work_id = self.publish_work()
        self.protocol.claim(
            ClaimRequest(self.scope, work_id, self.workbuddy, "activation-stale-claim")
        )

        reopened = self.protocol.reopen(
            ReopenRequest(
                self.scope,
                work_id,
                "human-zj",
                "WorkBuddy runtime activated the wrong project scope and did not receive the claimed handoff.",
            )
        )

        self.assertEqual(reopened["state"], "available")
        self.assertIsNone(reopened["claimant"])
        self.assertIsNone(reopened["result_summary"])
        self.assertEqual(reopened["references"], [])
        with self.assertRaises(EligibilityError):
            self.protocol.publish_result(
                PublishResultRequest(
                    self.scope,
                    work_id,
                    self.workbuddy,
                    "A stale claimant must not publish after Human reopen.",
                    "No next action.",
                    "not_met",
                    ({"commit": "never", "files": [], "tests": []},),
                )
            )

        reclaimed = self.protocol.claim(
            ClaimRequest(self.scope, work_id, self.codex, "activation-reopened-claim")
        )
        self.assertEqual(reclaimed["claim"]["agent_id"], "codex-01")

    def test_human_reopen_rejects_review_frontier_and_completed_work(self) -> None:
        work_id = self.publish_work()
        self.protocol.claim(
            ClaimRequest(self.scope, work_id, self.workbuddy, "activation-review-seed")
        )
        self.protocol.publish_result(
            PublishResultRequest(
                self.scope,
                work_id,
                self.workbuddy,
                "Result is ready for review.",
                "Codex verifies the referenced commit.",
                "met",
                ({"commit": "abc1234", "files": ["SKILL.md"], "tests": ["pass"]},),
            )
        )
        self.protocol.submit(self.scope, work_id, self.workbuddy)

        with self.assertRaises(ValidationError):
            self.protocol.reopen(
                ReopenRequest(self.scope, work_id, "human-zj", "Do not bypass reviewer frontier.")
            )

        self.protocol.claim_review(
            ClaimReviewRequest(self.scope, work_id, self.codex, "activation-review-claim")
        )
        self.protocol.review(
            ReviewRequest(self.scope, work_id, self.codex, "accept", "Verified.")
        )
        with self.assertRaises(ValidationError):
            self.protocol.reopen(
                ReopenRequest(self.scope, work_id, "human-zj", "Completed work stays immutable.")
            )


if __name__ == "__main__":
    unittest.main()
