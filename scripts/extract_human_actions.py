#!/usr/bin/env python3
"""Extract Human actions from WorkBuddy session operation logs.

Two arms of the same experiment must be measured by one implementation, or the
comparison drifts. This is that implementation.

Definitions (identical for every arm):

- a `role=user` message is a Human action; a `role=assistant` message is an
  Agent turn output
- Human-side interval = previous `assistant` timestamp -> this `user` timestamp
- two totals are always reported:
    * upper bound  — every interval
    * filtered     — intervals over `AWAY_THRESHOLD_S` excluded
- an interval over the threshold is flagged, never silently dropped

Three caveats travel with every number this script prints:

1. the interval is an UPPER BOUND on Human active time; it may include time the
   Human was away
2. it may contain a third-party Agent's runtime (e.g. a Codex review running
   between two turns) that this log cannot separate
3. only the Human *send* moment is known; there is no Human-side start time

Usage:

    python scripts/extract_human_actions.py <session.jsonl> [<session.jsonl> ...]
    python scripts/extract_human_actions.py --json <session.jsonl> [...]

Exit code is 0 when at least one Human action was found, 1 otherwise.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

TZ = datetime.timezone(datetime.timedelta(hours=8))  # GMT+8
AWAY_THRESHOLD_S = 900.0  # 15 min — an interval longer than this is "away", not "working"


def load_messages(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") != "message":
                continue
            if entry.get("role") not in ("user", "assistant"):
                continue
            text = "".join(
                block.get("text", "") or ""
                for block in (entry.get("content") or [])
                if isinstance(block, dict)
            )
            rows.append({"role": entry["role"], "ts": entry["timestamp"], "text": text})
    rows.sort(key=lambda row: row["ts"])
    return rows


def human_text(raw: str) -> str:
    """Strip the injected context blocks; keep only what the Human actually typed."""
    stripped = re.sub(r"<system-reminder.*?</system-reminder>", "", raw, flags=re.S)
    match = re.search(r"<user_query>(.*?)</user_query>", stripped, flags=re.S)
    if match:
        return match.group(1).strip()
    return " ".join(re.sub(r"<[^>]+>", "", stripped).split()).strip()


def analyse(path: Path) -> dict:
    rows = load_messages(path)
    actions = []
    for index, row in enumerate(rows):
        if row["role"] != "user":
            continue
        previous = next(
            (item for item in reversed(rows[:index]) if item["role"] == "assistant"),
            None,
        )
        following = next(
            (item for item in rows[index + 1:] if item["role"] == "assistant"),
            None,
        )
        interval = None if previous is None else (row["ts"] - previous["ts"]) / 1000
        agent_turn = None if following is None else (following["ts"] - row["ts"]) / 1000
        actions.append(
            {
                "sent": _fmt(row["ts"]),
                "text": human_text(row["text"]),
                "chars": len(human_text(row["text"])),
                "interval_s": interval,
                "away": interval is not None and interval > AWAY_THRESHOLD_S,
                "agent_turn_s": agent_turn,
            }
        )
    upper = sum(a["interval_s"] for a in actions if a["interval_s"] is not None)
    filtered = sum(
        a["interval_s"] for a in actions if a["interval_s"] is not None and not a["away"]
    )
    agent = sum(a["agent_turn_s"] for a in actions if a["agent_turn_s"] is not None)
    span = (rows[-1]["ts"] - rows[0]["ts"]) / 1000 if rows else 0.0
    return {
        "session": path.stem,
        "file": str(path),
        "actions": actions,
        "count": len(actions),
        "upper_bound_s": upper,
        "filtered_s": filtered,
        "agent_runtime_s": agent,
        "wall_clock_s": span,
    }


def _fmt(ts: int) -> str:
    return datetime.datetime.fromtimestamp(ts / 1000, TZ).strftime("%Y-%m-%d %H:%M:%S")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sessions", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = parser.parse_args()

    reports = [analyse(path) for path in args.sessions]
    reports = [report for report in reports if report["count"]]

    if args.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
        return 0 if reports else 1

    total_upper = total_filtered = total_agent = 0.0
    for report in reports:
        print(f"===== {report['session']} =====")
        for action in report["actions"]:
            if action["interval_s"] is None:
                gap = "首条"
            else:
                gap = f"{action['interval_s']:.1f}s" + ("  <- away" if action["away"] else "")
            preview = " ".join(action["text"].split())[:64]
            print(f"  {action['sent']} | {gap:>14} | {action['chars']:>4} | {preview}")
        print(
            f"  -- {report['count']} actions | upper {report['upper_bound_s']:.1f}s"
            f"={report['upper_bound_s']/60:.1f}min | filtered {report['filtered_s']:.1f}s"
            f"={report['filtered_s']/60:.1f}min | agent {report['agent_runtime_s']/60:.1f}min"
            f" | wall {report['wall_clock_s']/60:.1f}min"
        )
        print()
        total_upper += report["upper_bound_s"]
        total_filtered += report["filtered_s"]
        total_agent += report["agent_runtime_s"]

    print(
        f"TOTAL: {sum(r['count'] for r in reports)} actions | "
        f"upper bound {total_upper:.1f}s={total_upper/60:.1f}min | "
        f"filtered (>{AWAY_THRESHOLD_S/60:.0f}min excluded) {total_filtered:.1f}s"
        f"={total_filtered/60:.1f}min | agent {total_agent/60:.1f}min"
    )
    print("Caveats: upper bound (may include away time); may embed third-party Agent")
    print("runtime; only Human send moments are known, no Human-side start times.")
    return 0 if reports else 1


if __name__ == "__main__":
    raise SystemExit(main())
