"""Run AgentRQ adapter C1/C2/C4 black-box validation and export evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.agentrq_blackbox import run_black_box


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    args = parser.parse_args()
    report = run_black_box()
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(_markdown(report), encoding="utf-8")
    return 0 if all(item["status"] == "PASS" for item in report["scenarios"]) else 1


def _markdown(report: dict[str, object]) -> str:
    scenarios = report["scenarios"]
    lines = [
        "# AgentRQ adapter C1/C2/C4 black-box validation",
        "",
        f"- Candidate: `{report['candidate']}`",
        f"- Fixed commit: `{report['commit']}`",
        "- Fixture boundary: exposed `createTask/getTask/updateTaskStatus/reply` only",
        "- Product semantic owner: ZAgenticOPN `CoordinationProtocol`",
        "",
        "## Gate results",
        "",
        "| Gate | Result | Evidence |",
        "| --- | --- | --- |",
    ]
    for scenario in scenarios:  # type: ignore[union-attr]
        evidence = ", ".join(f"{key}={value}" for key, value in scenario.items() if key not in {"gate", "status", "structured_reply", "outcomes"})
        lines.append(f"| {scenario['gate']} | **{scenario['status']}** | {evidence} |")
    lines.extend(
        [
            "",
            "## Native surface boundary",
            "",
            "- C1 is an adapted pass: AgentRQ supplies task-agnostic queue transport; ZAgenticOPN applies eligibility.",
            "- C2 is not a native AgentRQ pass: the wrapper owns atomic claim; AgentRQ status is updated only after success.",
            "- C4 is not a native AgentRQ pass: the wrapper projects a generic review task; ZAgenticOPN owns review state and provenance.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
