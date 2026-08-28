"""Black-box tests for the strict activation JSON-Call and host config."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from zagentic_opn import AgentProfile, CoordinationProtocol, PublishRequest
from zagentic_opn.activation_contract import (
    ACTIVATION_SCHEMA_VERSION,
    INTENT_CHECK_SHARED_CONTEXT,
    PRE_MODEL_HANDOFF_INJECTION,
    resolve_intent,
)
from zagentic_opn.activation_runner import record_handoff_delivery_failure
from zagentic_opn.runtime_config import (
    RUNTIME_CONFIG_SCHEMA_VERSION,
    ScopeBinding,
    configure_runtime,
    resolve_scope_for_workspace,
)


class ActivationRunnerBlackBoxTests(unittest.TestCase):
    scope = "zagenticopn/experience-version"
    root = Path(__file__).resolve().parents[1]

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name)
        self.database = self.root_path / "shared.sqlite3"
        self.config = self.root_path / "runtime.json"
        self.protocol = CoordinationProtocol(self.database)
        self._old_config = os.environ.get("ZAGENTICOPN_RUNTIME_CONFIG")
        os.environ["ZAGENTICOPN_RUNTIME_CONFIG"] = str(self.config)
        self._configure(self.database)
        self.agent = {
            "agent_id": "workbuddy-01",
            "device_id": "device-a",
            "capabilities": ["technical-writing"],
            "permissions": ["zagentic-skill-write"],
            "can_review": False,
        }

    def tearDown(self) -> None:
        if self._old_config is None:
            os.environ.pop("ZAGENTICOPN_RUNTIME_CONFIG", None)
        else:
            os.environ["ZAGENTICOPN_RUNTIME_CONFIG"] = self._old_config
        self.temp_dir.cleanup()

    def test_valid_call_claims_and_returns_complete_handoff(self) -> None:
        self._publish("runner-main")
        receipt = self._run(self._request("activation-runner-main"))

        self.assertEqual(receipt["status"], "claimed")
        self.assertEqual(receipt["work_id"], "runner-main")
        self.assertEqual(receipt["handoff"]["objective"], "Improve the research report skill.")
        self.assertEqual(receipt["handoff"]["acceptance"], "Return a real Git artifact.")
        self.assertTrue(receipt["event_recorded"])
        self.assertRegex(receipt["config_loaded_at"], r"^\d{14}\.\d{3}Z$")
        self.assertRegex(receipt["config_updated_at"], r"^\d{14}\.\d{3}Z$")

    def test_no_eligible_work_is_a_receipt_without_claim(self) -> None:
        receipt = self._run(self._request("activation-runner-empty"))

        self.assertEqual(receipt["status"], "no_eligible_work")
        self.assertIsNone(receipt["work_id"])
        self.assertTrue(receipt["event_recorded"])

    def test_unsupported_host_is_rejected_before_claim_and_recorded(self) -> None:
        self._publish("runner-unsupported")
        request = self._request("activation-runner-unsupported")
        request["host_capabilities"] = []
        receipt = self._run(request)

        self.assertEqual(receipt["status"], "unsupported_host")
        self.assertEqual(receipt["work_id"], None)
        self.assertTrue(receipt["event_recorded"])
        self.assertEqual(self.protocol.inspect(self.scope, "runner-unsupported")["state"], "available")
        self.assertEqual(self._event_types()[-1], "activation_rejected")

    def test_invalid_contract_is_rejected_and_does_not_discover(self) -> None:
        self._publish("runner-invalid")
        request = self._request("activation-runner-invalid")
        request["unexpected"] = True
        receipt = self._run(request)

        self.assertEqual(receipt["status"], "invalid_contract")
        self.assertTrue(receipt["event_recorded"])
        self.assertEqual(self._event_types()[-1], "activation_rejected")
        self.assertEqual(self.protocol.inspect(self.scope, "runner-invalid")["state"], "available")
        self.assertNotIn("discover", self._event_types())

    def test_missing_store_fails_closed_without_creating_a_database(self) -> None:
        missing = self.root_path / "missing" / "shared.sqlite3"
        self._configure(missing)
        receipt = self._run(self._request("activation-runner-missing-store"))

        self.assertEqual(receipt["status"], "invalid_runtime_config")
        self.assertFalse(receipt["event_recorded"])
        self.assertFalse(missing.exists())
        self.assertEqual(receipt["required_fields"], ["shared_store_path", "config_updated_at"])

    def test_handoff_delivery_failure_is_recorded_after_claim(self) -> None:
        self._publish("runner-handoff-failure")
        receipt = self._run(self._request("activation-runner-handoff-failure"))

        failure = record_handoff_delivery_failure(receipt, "host rejected additional context")

        self.assertEqual(failure["status"], "handoff_delivery_failed")
        self.assertTrue(failure["event_recorded"])
        self.assertEqual(self._event_types()[-1], "handoff_delivery_failed")

    def test_runner_hot_loads_the_store_after_atomic_reconfigure(self) -> None:
        first = self.root_path / "first.sqlite3"
        second = self.root_path / "second.sqlite3"
        first_protocol = CoordinationProtocol(first)
        second_protocol = CoordinationProtocol(second)
        first_protocol.publish(self._publish_request("hot-first"))
        second_protocol.publish(self._publish_request("hot-second"))

        self._configure(first)
        first_receipt = self._run(self._request("activation-hot-first"))
        self.assertEqual(first_receipt["work_id"], "hot-first")

        self._configure(second)
        second_receipt = self._run(self._request("activation-hot-second"))
        self.assertEqual(second_receipt["work_id"], "hot-second")
        self.assertEqual(second_receipt["config_updated_at"], json.loads(self.config.read_text())["config_updated_at"])

    def test_workspace_scope_binding_prefers_the_most_specific_root(self) -> None:
        parent = self.root_path / "workspace"
        child = parent / "ZAgentic"
        resolved = resolve_scope_for_workspace(
            (
                ScopeBinding(parent, "owner/parent"),
                ScopeBinding(child, "jununfly/ZAgentic/zj-research-report"),
            ),
            child / "skills",
        )

        self.assertEqual(resolved, "jununfly/ZAgentic/zj-research-report")

    def test_alias_resolution_is_exact_and_side_effect_free(self) -> None:
        self.assertEqual(resolve_intent("  检查 shared context  "), INTENT_CHECK_SHARED_CONTEXT)
        self.assertIsNone(resolve_intent("请检查 shared context"))
        self.assertIsNone(resolve_intent("检查 shared context now"))

    def _request(self, activation_id: str) -> dict[str, object]:
        return {
            "schema_version": ACTIVATION_SCHEMA_VERSION,
            "intent_id": INTENT_CHECK_SHARED_CONTEXT,
            "activation_id": activation_id,
            "scope": self.scope,
            "agent_profile": self.agent,
            "host_capabilities": [PRE_MODEL_HANDOFF_INJECTION],
        }

    def _publish(self, work_id: str) -> None:
        self.protocol.publish(self._publish_request(work_id))

    def _publish_request(self, work_id: str) -> PublishRequest:
        return PublishRequest(
            self.scope,
            "Improve the research report skill.",
            "Return a real Git artifact.",
            AgentProfile("codex-01", "device-a"),
            frozenset({"technical-writing"}),
            frozenset({"zagentic-skill-write"}),
            work_id,
        )

    def _configure(self, database: Path) -> None:
        configure_runtime(
            {
                "schema_version": RUNTIME_CONFIG_SCHEMA_VERSION,
                "shared_store_path": str(database),
            },
            self.config,
        )

    def _run(self, payload: dict[str, object]) -> dict[str, object]:
        completed = subprocess.run(
            [sys.executable, "-m", "zagentic_opn.activation_runner"],
            cwd=self.root,
            env={**os.environ, "ZAGENTICOPN_RUNTIME_CONFIG": str(self.config)},
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(len(completed.stdout.splitlines()), 1, completed.stdout)
        return json.loads(completed.stdout)

    def _event_types(self) -> list[str]:
        with sqlite3.connect(self.database) as connection:
            return [row[0] for row in connection.execute("SELECT type FROM events ORDER BY sequence")]


if __name__ == "__main__":
    unittest.main()
