"""Black-box tests for the local Agent Integration Proxy."""

from __future__ import annotations

import tempfile
import unittest
import json
import os
import subprocess
import sys
from pathlib import Path

from zagentic_opn import (
    AgentIntegrationProxy,
    AgentProfile,
    CoordinationProtocol,
    ModelRuntime,
    ProxyRequest,
    PublishRequest,
)
from zagentic_opn.runtime_config import RUNTIME_CONFIG_SCHEMA_VERSION, configure_runtime


class RecordingRuntime(ModelRuntime):
    def __init__(self) -> None:
        self.requests: list[tuple[dict[str, str], ...]] = []

    def complete(self, messages: tuple[dict[str, str], ...]) -> str:
        self.requests.append(messages)
        return "model continued from the claimed handoff"


class AgentIntegrationProxyBlackBoxTests(unittest.TestCase):
    scope = "zagenticopn/experience-version"
    root = Path(__file__).resolve().parents[1]

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "shared.sqlite3"
        self.runtime_config = Path(self.temp_dir.name) / "runtime.json"
        self.protocol = CoordinationProtocol(self.database)
        self._old_runtime_config = os.environ.get("ZAGENTICOPN_RUNTIME_CONFIG")
        os.environ["ZAGENTICOPN_RUNTIME_CONFIG"] = str(self.runtime_config)
        configure_runtime(
            {
                "schema_version": RUNTIME_CONFIG_SCHEMA_VERSION,
                "shared_store_path": str(self.database),
            },
            self.runtime_config,
        )
        self.agent = AgentProfile(
            "workbuddy-01",
            "device-a",
            frozenset({"technical-writing"}),
            frozenset({"zagentic-skill-write"}),
        )

    def tearDown(self) -> None:
        if self._old_runtime_config is None:
            os.environ.pop("ZAGENTICOPN_RUNTIME_CONFIG", None)
        else:
            os.environ["ZAGENTICOPN_RUNTIME_CONFIG"] = self._old_runtime_config
        self.temp_dir.cleanup()

    def test_shared_context_phrase_claims_and_injects_handoff_into_one_model_request(self) -> None:
        self.protocol.publish(
            PublishRequest(
                self.scope,
                "Improve the research report skill.",
                "Commit the improvement and report commit, files, and tests.",
                AgentProfile("codex-01", "device-a", can_review=True),
                frozenset({"technical-writing"}),
                frozenset({"zagentic-skill-write"}),
                "proxy-main-path",
            )
        )
        runtime = RecordingRuntime()

        result = AgentIntegrationProxy(self.protocol).handle(
            ProxyRequest(
                message="检查 shared context",
                scope=self.scope,
                agent=self.agent,
                activation_id="activation-proxy-main-path",
            ),
            runtime,
        )

        self.assertEqual(result["status"], "handoff_injected")
        self.assertEqual(result["activation"]["status"], "claimed")
        self.assertEqual(result["activation"]["work"]["id"], "proxy-main-path")
        self.assertEqual(len(runtime.requests), 1)
        messages = runtime.requests[0]
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("Improve the research report skill.", messages[0]["content"])
        self.assertIn("Commit the improvement and report commit, files, and tests.", messages[0]["content"])
        self.assertEqual(messages[1], {"role": "user", "content": "检查 shared context"})

    def test_external_proxy_host_receives_claimed_single_request_without_work_item_id(self) -> None:
        self.protocol.publish(
            PublishRequest(
                self.scope,
                "Run the next shared-context Work Item.",
                "Return a real Git commit, changed files, and test outcome.",
                AgentProfile("codex-01", "device-a"),
                frozenset(),
                frozenset(),
                "proxy-host-path",
            )
        )
        command = [
            sys.executable,
            str(self.root / "scripts" / "agent_integration_proxy.py"),
            "--db",
            str(self.database),
            "--scope",
            self.scope,
            "--agent-id",
            self.agent.agent_id,
            "--device-id",
            self.agent.device_id,
            "--activation-id",
            "activation-proxy-host-path",
        ]
        completed = subprocess.run(
            command,
            cwd=self.root,
            input=json.dumps({"message": "检查 shared context"}),
            check=True,
            capture_output=True,
            text=True,
        )

        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "handoff_injected")
        self.assertEqual(result["activation"]["work"]["id"], "proxy-host-path")
        self.assertNotIn("--work-id", command)
        self.assertEqual(result["messages"][1], {"role": "user", "content": "检查 shared context"})

    def test_no_eligible_work_returns_without_model_call_or_fabricated_handoff(self) -> None:
        runtime = RecordingRuntime()

        result = AgentIntegrationProxy(self.protocol).handle(
            ProxyRequest(
                message="检查 shared context",
                scope=self.scope,
                agent=self.agent,
                activation_id="activation-proxy-no-work",
            ),
            runtime,
        )

        self.assertEqual(result["status"], "no_eligible_work")
        self.assertEqual(result["activation"]["discovery"]["items"], [])
        self.assertEqual(result["messages"], [])
        self.assertEqual(runtime.requests, [])

    def test_workbuddy_prompt_hook_injects_only_claimed_handoff(self) -> None:
        self.protocol.publish(
            PublishRequest(
                self.scope,
                "Execute the WorkBuddy integration path.",
                "Produce a real commit and test result.",
                AgentProfile("codex-01", "device-a"),
                frozenset(),
                frozenset(),
                "proxy-hook-path",
            )
        )
        hook = self.root / "integrations" / "workbuddy" / "hooks" / "user-prompt-submit.py"
        completed = subprocess.run(
            [sys.executable, str(hook)],
            cwd=self.root,
            env={
                **os.environ,
                "ZAGENTICOPN_RUNTIME_CONFIG": str(self.runtime_config),
                "ZAGENTICOPN_SCOPE": self.scope,
                "ZAGENTICOPN_AGENT_ID": self.agent.agent_id,
                "ZAGENTICOPN_DEVICE_ID": self.agent.device_id,
                "ZAGENTICOPN_ACTIVATION_ID": "activation-proxy-hook-path",
            },
            input=json.dumps({"prompt": "检查 shared context"}),
            check=True,
            capture_output=True,
            text=True,
        )

        output = json.loads(completed.stdout)
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Execute the WorkBuddy integration path.", context)

    def test_workbuddy_hook_uses_explicit_host_runtime_store(self) -> None:
        workspace = Path(self.temp_dir.name) / "consumer-workspace"
        workspace.mkdir()
        database = workspace / ".zagenticopn" / "shared.sqlite3"
        CoordinationProtocol(database).publish(
            PublishRequest(
                self.scope,
                "Use the active workspace shared store.",
                "Return a real Git commit and test result.",
                AgentProfile("codex-01", "device-a"),
                frozenset(),
                frozenset(),
                "proxy-hook-default-store",
            )
        )
        workspace_config = Path(self.temp_dir.name) / "workspace-runtime.json"
        configure_runtime(
            {
                "schema_version": RUNTIME_CONFIG_SCHEMA_VERSION,
                "shared_store_path": str(database),
            },
            workspace_config,
        )
        hook = self.root / "integrations" / "workbuddy" / "hooks" / "user-prompt-submit.py"
        environment = {**os.environ}
        environment.pop("ZAGENTICOPN_DB", None)
        environment.update(
            {
                "ZAGENTICOPN_SOURCE_ROOT": str(self.root),
                "ZAGENTICOPN_RUNTIME_CONFIG": str(workspace_config),
                "ZAGENTICOPN_SCOPE": self.scope,
                "ZAGENTICOPN_AGENT_ID": self.agent.agent_id,
                "ZAGENTICOPN_DEVICE_ID": self.agent.device_id,
                "ZAGENTICOPN_ACTIVATION_ID": "activation-proxy-hook-default-store",
            }
        )
        completed = subprocess.run(
            [sys.executable, str(hook)],
            cwd=workspace,
            env=environment,
            input=json.dumps({"prompt": "检查 shared context"}),
            check=True,
            capture_output=True,
            text=True,
        )

        output = json.loads(completed.stdout)
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Use the active workspace shared store.", context)

    def test_workbuddy_hook_binds_event_cwd_to_host_scope_without_scope_env(self) -> None:
        target_scope = "jununfly/ZAgentic/zj-research-report"
        workspace = Path(self.temp_dir.name) / "ZAgentic"
        workspace.mkdir()
        self.protocol.publish(
            PublishRequest(
                target_scope,
                "Continue the research report improvement.",
                "Return a real Git commit and test result.",
                AgentProfile("codex-01", "device-a"),
                frozenset({"technical-writing"}),
                frozenset({"zagentic-skill-write"}),
                "proxy-hook-bound-scope",
            )
        )
        configure_runtime(
            {
                "schema_version": RUNTIME_CONFIG_SCHEMA_VERSION,
                "shared_store_path": str(self.database),
                "scope_bindings": [
                    {"workspace_root": str(workspace), "scope": target_scope}
                ],
            },
            self.runtime_config,
        )
        hook = self.root / "integrations" / "workbuddy" / "hooks" / "user-prompt-submit.py"
        environment = {**os.environ}
        environment.pop("ZAGENTICOPN_SCOPE", None)
        environment.update(
            {
                "ZAGENTICOPN_SOURCE_ROOT": str(self.root),
                "ZAGENTICOPN_RUNTIME_CONFIG": str(self.runtime_config),
                "ZAGENTICOPN_AGENT_ID": self.agent.agent_id,
                "ZAGENTICOPN_DEVICE_ID": self.agent.device_id,
                "ZAGENTICOPN_ACTIVATION_ID": "activation-proxy-bound-scope",
            }
        )
        completed = subprocess.run(
            [sys.executable, str(hook)],
            cwd=workspace,
            env=environment,
            input=json.dumps({"prompt": "检查 shared context", "cwd": str(workspace)}),
            check=True,
            capture_output=True,
            text=True,
        )

        output = json.loads(completed.stdout)
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Continue the research report improvement.", context)
        claimed = self.protocol.inspect(target_scope, "proxy-hook-bound-scope")
        self.assertEqual(claimed["state"], "claimed")
        self.assertEqual(claimed["claimant"], "workbuddy-01")

    def test_workbuddy_hook_fails_closed_when_workspace_scope_is_unbound(self) -> None:
        default_scope_work = "default-scope-must-not-be-guessed"
        self.protocol.publish(
            PublishRequest(
                "zagenticopn/experience-version",
                "This item must not be claimed by an unbound workspace.",
                "Return a real Git commit and test result.",
                AgentProfile("codex-01", "device-a"),
                frozenset(),
                frozenset(),
                default_scope_work,
            )
        )
        hook = self.root / "integrations" / "workbuddy" / "hooks" / "user-prompt-submit.py"
        environment = {**os.environ}
        environment.pop("ZAGENTICOPN_SCOPE", None)
        environment.update(
            {
                "ZAGENTICOPN_SOURCE_ROOT": str(self.root),
                "ZAGENTICOPN_RUNTIME_CONFIG": str(self.runtime_config),
                "ZAGENTICOPN_AGENT_ID": self.agent.agent_id,
                "ZAGENTICOPN_DEVICE_ID": self.agent.device_id,
                "ZAGENTICOPN_ACTIVATION_ID": "activation-proxy-unbound-scope",
            }
        )
        completed = subprocess.run(
            [sys.executable, str(hook)],
            cwd=self.temp_dir.name,
            env=environment,
            input=json.dumps({"prompt": "检查 shared context", "cwd": self.temp_dir.name}),
            check=True,
            capture_output=True,
            text=True,
        )

        output = json.loads(completed.stdout)
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("status=scope_unbound", context)
        self.assertEqual(
            self.protocol.inspect("zagenticopn/experience-version", default_scope_work)["state"],
            "available",
        )


if __name__ == "__main__":
    unittest.main()
