"""Run a reproducible Codex -> WorkBuddy -> Codex local smoke experiment."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from zagentic_opn import (
    AgentProfile,
    CoordinationProtocol,
    PublishRequest,
    PublishResultRequest,
    ReviewRequest,
)


def main() -> int:
    """Execute the full protocol path against a temporary Git repository."""

    with tempfile.TemporaryDirectory(prefix="zagenticopn-smoke-") as directory:
        root = Path(directory)
        database = root / "shared.sqlite3"
        git_repo = root / "artifact"
        git_repo.mkdir()
        _run("git", "-C", str(git_repo), "init", "-q")
        _run("git", "-C", str(git_repo), "config", "user.name", "ZAgenticOPN smoke")
        _run("git", "-C", str(git_repo), "config", "user.email", "smoke@example.invalid")
        artifact = git_repo / "artifact.md"
        artifact.write_text("# Experience Version smoke artifact\n", encoding="utf-8")
        _run("git", "-C", str(git_repo), "add", "artifact.md")
        _run("git", "-C", str(git_repo), "commit", "-qm", "test: create smoke artifact")
        commit = _run("git", "-C", str(git_repo), "rev-parse", "HEAD").strip()

        codex = AgentProfile("codex-01", "device-a", frozenset({"technical-writing"}), frozenset({"git-write"}), True)
        workbuddy = AgentProfile("workbuddy-01", "device-a", frozenset({"technical-writing"}), frozenset({"git-write"}), True)
        scope = "zagenticopn/experience-version"
        protocol = CoordinationProtocol(database)
        work = protocol.publish(
            PublishRequest(scope, "Verify the same-device collaboration path.", "A committed artifact is reviewed and accepted.", codex, frozenset({"technical-writing"}), frozenset({"git-write"}), "smoke-work")
        )
        workbuddy_activation = _activate(
            database,
            scope,
            workbuddy,
            "activation-workbuddy",
        )
        if workbuddy_activation["status"] != "claimed":
            raise RuntimeError(f"WorkBuddy activation did not claim work: {workbuddy_activation}")
        claimed_work_id = workbuddy_activation["work"]["id"]
        protocol.publish_result(
            PublishResultRequest(scope, claimed_work_id, workbuddy, "Created and tested the smoke artifact.", "Codex verifies the commit.", "met", ({"commit": commit, "files": ["artifact.md"], "tests": ["git commit: pass"]},))
        )
        protocol.submit(scope, claimed_work_id, workbuddy)
        codex_activation = _activate(
            database,
            scope,
            codex,
            "activation-codex",
            can_review=True,
        )
        if codex_activation["status"] != "claimed" or codex_activation["kind"] != "review":
            raise RuntimeError(f"Codex review activation did not claim review: {codex_activation}")
        completed = protocol.review(ReviewRequest(scope, claimed_work_id, codex, "accept", "Commit is readable and attributable."))
        print(json.dumps({"c1_discover": workbuddy_activation["discovery"]["status"], "c2_claim": workbuddy_activation["status"], "c4_discover": codex_activation["discovery"]["status"], "c4_claim": codex_activation["status"], "final_state": completed["state"], "commit": commit}, ensure_ascii=False, sort_keys=True))
        print(protocol.scorecard(scope), end="")
    return 0


def _run(*command: str) -> str:
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


def _activate(database: Path, scope: str, agent: AgentProfile, activation_id: str, *, can_review: bool = False) -> dict[str, object]:
    command = [
        sys.executable,
        str(Path(__file__).resolve().with_name("activate_agent.py")),
        "--db",
        str(database),
        "--scope",
        scope,
        "--agent-id",
        agent.agent_id,
        "--device-id",
        agent.device_id,
        "--capabilities",
        ",".join(sorted(agent.capabilities)),
        "--permissions",
        ",".join(sorted(agent.permissions)),
        "--activation-id",
        activation_id,
    ]
    if can_review:
        command.append("--can-review")
    return json.loads(_run(*command))


if __name__ == "__main__":
    raise SystemExit(main())
