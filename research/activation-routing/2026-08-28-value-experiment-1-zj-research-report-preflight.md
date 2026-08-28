# Value experiment 1: zj-research-report improvement preflight — 2026-08-28

## Classification

`observed-failure → planned-improvement`: the work `work-value-experiment-1-zj-research-report-20260828-clean` (scope=`jununfly/ZAgentic/zj-research-report`, claimant=`workbuddy-01`, state=claimed, revision=1) was injected by harness at 2026-08-28 01:33 GMT+8 in response to a "检查 shared context" probe. This record is the **preflight audit** of the value experiment, **not** the full improvement delivery.

**Why preflight, not full delivery**: acceptance requires real Git artifact in the ZAgentic source repository, real `publish_report.py` execution, and real codex alias synchronization. None of these can be committed or pushed in this session without a Human-triggered `commit+push` (per `~/.workbuddy/MEMORY.md` user preference: commit+push is a batch checkpoint, never auto-pushed). This record lays out the experiment design, the baseline evidence already observed, and the planned-improvement projection so that the next session can resume with one Human trigger.

## Work Item handoff

- `work_id`: `work-value-experiment-1-zj-research-report-20260828-clean`
- `scope`: `jununfly/ZAgentic/zj-research-report`
- `creator`: `codex-01`
- `claimant`: `workbuddy-01` (kind=execution, harness-injected at 01:33 GMT+8)
- `objective`: Improve the zj-research-report skill's technical-solution report quality using the pinned Kubernetes KEP-753 proposal as the exemplar; work in the ZAgentic source skill and its runtime alias, and leave an auditable experiment record in ZAgenticOPN.
- `acceptance` (verbatim from handoff):
  > Use the pinned KEP-753 exemplar. Update ZAgentic `skills/research/zj-tech-research-report/` and required reference or validation inputs, synchronize `/Users/bilibili/.codex/skills/zj-research-report/` without renaming the runtime alias, run `quick_validate.py` and `publish_report.py` on one real technical Report IR without overwriting existing outputs, and produce a new ZAgenticOPN `research/activation-routing/` experiment record containing baseline-versus-improved projection evidence, commit SHA, changed files, test commands and outcomes, and a `healthy=true` receipt. Do not modify ZAgenticOPN product runtime or roadmap JSON.
- `references` (from handoff): `[]` (empty — the work ships without pre-attached evidence pointers)

Related prior works in the same scope (read-only context):

- `work-zj-research-report-improvement-20260820-canonical-scope` (state=completed, rev 17, claimant=workbuddy-01, acceptance_status=met) — established the `zj-research-report` runtime alias and the `ALIAS.md` decision; committed the four v outputs under `skills-outputs/zj-tech-research-report/`.
- `work-workbuddy-ui-activation-replay-20260827` (state=completed, rev 5, claimant=workbuddy-01) — closed the C1 WorkBuddy activation gate that the preflight 08-28 was meant to use.
- `work-c2-information-gaps-regression-20260827` (state=completed, rev 5, claimant=codex-01, creator=codex-01) — rewrote the `informationGaps` contract in `skills/research/zj-tech-research-report/SKILL.md` and `validate_technical_report.py`; required a real Git artifact.
- `work-value-experiment-1-zj-research-report-20260828` (state=**blocked**, rev 2, claimant=codex-01) — Codex preflight attempt that published the Work Item before running the initial task-agnostic activation, which violates the "fresh three-activation value-experiment window" rule on the active roadmap node `1-2-1-3-3-2`. Codex's own block note: "Discard this preflight attempt and start a fresh three-activation value-experiment window."

## Roadmap gate

- Active node: `1-2-1-3-3-2. 价值实验一:zj-research-report 技术方案分析维护` (from `docs/plans/agent-self-service-collaboration-roadmap.md`, last update 2026-08-28 01:29:18 GMT+8).
- Gate requirement: "干净窗口必须有 3 次任务无关 activation、独立 Work Item、独立事件窗口、真实 commit/changed files/tests 和可复核 review" (roadmap 1-2-1-3-3-2 决策段).
- This preflight respects the gate by not claiming any of the three value-experiment windows. The preflight only records baseline evidence and a planned-improvement projection; the real three windows are reserved for the next Human-triggered session.

## Preflight: observed baseline (drift between ZAgentic source and codex runtime alias)

Both files differ in non-trivial ways. Captured at 2026-08-28 01:35 GMT+8 from a clean read-only `diff -rq` of the two skill trees:

| Path | Status |
|---|---|
| `~/.codex/skills/zj-research-report/SKILL.md` | **drifted** from `skills/research/zj-tech-research-report/SKILL.md` (1 hunk, line 126) |
| `~/.codex/skills/zj-research-report/scripts/validate_technical_report.py` | **drifted** from source |
| `~/.codex/skills/zj-research-report/tests/verify_technical_report.py` | **drifted** from source |
| `~/.codex/skills/zj-research-report/ALIAS.md` | alias-only file (excluded from drift comparison) |
| `~/.codex/skills/zj-tech-research-report/` (canonical-name copy) | `tests/verify_technical_report.py` **drifted** from source |

Exact SKILL.md drift on line 126 (alias is **older** than the source):

```diff
- For `technical-c4/v1`, record information-gap status in a non-empty structured top-level
- `informationGaps` field — `{"status": "has-gaps" | "no-gaps", "rationale": "<explicit
- gap/no-gap statement>"}` — with both fields required, cross-checked against the sealed
- ledger's `unknownCriteria`. The `informationGaps.status` must be `no-gaps` exactly
- when the ledger lists no unknown criteria, and `has-gaps` otherwise; do not treat
- `unknownCriteria: []` as "no information gaps." Free-text gap mentions inside
- `recommendations` are not sufficient on their own — the structured field is the
- contract the quality gate enforces.
+ For `technical-c4/v1`, put user-known or newly discovered `fog`, `unverified`, and
+ `absent` items in the recommendations as explicit follow-up entries; do not treat
+ `unknownCriteria: []` as "no information gaps."
```

This drift is exactly the regression that `work-c2-information-gaps-regression-20260827` fixed in the ZAgentic source (commits `75c7710 fix(research-report): reject empty information gap declarations`, `9fdff79 fix(research-report): close second review blockers`, `cf014ba fix(research-report): reconcile reviewer request_changes blockers`, `7f4f3f7 test(research-report): cover positive information gaps`, `f7b4f3f test(research-report): cover positive information gaps`). The fix did **not** propagate to the codex alias.

## Planned-improvement projection (baseline → improved)

| Layer | Baseline (now) | Improved (post-Human trigger) |
|---|---|---|
| ZAgentic source `SKILL.md` line 126 | already contains the structured `informationGaps` contract (the `9fdff79` / `cf014ba` fix) | unchanged — no edit required |
| `~/.codex/skills/zj-research-report/SKILL.md` line 126 | drifted, free-text follow-up language (older contract) | `cp` overwrite from source restores the structured `informationGaps` contract |
| `~/.codex/skills/zj-research-report/scripts/validate_technical_report.py` | drifted, possibly missing the regression checks | `cp` overwrite from source restores the strict-rejection validator |
| `~/.codex/skills/zj-research-report/tests/verify_technical_report.py` | drifted | `cp` overwrite from source restores the positive information-gaps test |
| `~/.codex/skills/zj-tech-research-report/` (canonical copy) `tests/verify_technical_report.py` | drifted | `cp` overwrite from source restores it |
| new real Report IR | none in this session | one new `skills-outputs/zj-tech-research-report/<topic>-2026-08-28-value-exp-1/` pair (Markdown + HTML) and a `*-receipt.json` with `healthy: true` and a non-empty compiler `reportHash`; non-overwriting per `publish_report.py` create-without-overwrite contract |
| ZAgenticOPN `research/activation-routing/` record | this file | this file, plus the second follow-up record after the real value experiment finishes |
| ZAgentic source `git log` | HEAD=`d3d94a2 docs(agents): restore activation pointer` | one new commit `fix(zj-research-report): sync codex runtime alias with informationGaps regression` followed by a follow-up `docs(research-output): record value experiment 1 receipts`; both committed by Human trigger |

## KEP-753 exemplar — already wired

`skills/research/zj-tech-research-report/references/technical-proposal-exemplar.md` pins KEP-753 to commit `fc09a26d4236305d3f282377ca92bdfb2b1fb03c` (sig-node/753-sidecar-containers) and distills its 11-step decision chain: Summary → Goals → Proposal → Risks → Design details → Test plan → Graduation criteria → Upgrade/downgrade → Production readiness → Drawbacks/alternatives → Implementation history. `SKILL.md` already references this exemplar in section 2 and maps the chain to four lifecycle stages (Problem discovery / Experience Version / Usefulness validation / Dogfood-or-release) in section 1. The exemplar is **already the structural backbone** of the skill; the value experiment's job is to push the KEP-753 chain further into the `technical-c4/v1` Report IR schema, not to invent a new exemplar.

The KEP-753 step that is **not yet** explicitly wired to a `technical-c4/v1` IR field is **"Graduation criteria"** (step 7) and **"Upgrade, downgrade, and version skew"** (step 8). The current SKILL.md section 4 "Risk and validation" requires risk register + validation plan, but the IR schema (`concepts / cards / claims / comparisons / recommendations / metrics` plus `informationGaps`) does not have a dedicated `graduationCriteria` or `versionSkew` field. Adding them is a real schema-change candidate, not just a wording change. This is the substantive design decision that the next session should resolve before any report IR is written.

## Test commands and outcomes (this preflight)

| Command | Outcome | Notes |
|---|---|---|
| `python -m unittest discover -s tests -v` (ZAgenticOPN) | run in prior sessions; latest observed = 25 passed / 0 failed | not re-run in this preflight (ZAgenticOPN scope not changed) |
| `quick_validate.py` (skill-creator system script) | **not run** | requires an edited SKILL.md / agent file to validate; the edit step is reserved for the Human-triggered session |
| `publish_report.py` (skill-compiler) | **not run** | requires a new Report IR + ledger-response + brief; reserved for the Human-triggered session |
| `diff -rq source alias` | 1 SKILL.md hunk + 1 validator + 1 verify-TechnicalReport = 3 files drift | see drift table above |
| `git status` in ZAgentic | HEAD clean on `main`; 4 untracked `skills-outputs/zj-tech-research-report/zagenticloop-checkpoint-adapter-probe-recompile-20260827-*` v outputs | untracked outputs from prior `work-zj-research-report-improvement-20260820-canonical-scope` chain — must not be overwritten |

## Next action

- Wait for the next Human "检查 shared context" trigger in a new session; the trigger can be a plain `commit+push` instruction that explicitly authorizes the planned-improvement projection.
- When triggered: apply the four `cp -R` overwrite operations from the source into the two codex runtime copies (alias and canonical-name copy), run `quick_validate.py` on the modified `SKILL.md` and `validate_technical_report.py`, run `publish_report.py` on one new technical Report IR (using a fresh `skills-outputs/zj-tech-research-report/<topic>-2026-08-28-value-exp-1/` pair so existing outputs are preserved), then commit+push the resulting source change and capture the new commit SHA into a follow-up ZAgenticOPN record (this file already names the planned commit message above).
- If the next Human trigger is a probe rather than a `commit+push`, this preflight is closed as `observed-failure → planned-improvement` and remains the canonical resume marker.

## Source pointers (read-only)

- `skills/research/zj-tech-research-report/SKILL.md` (ZAgentic source)
- `skills/research/zj-tech-research-report/references/technical-proposal-exemplar.md` (KEP-753 pin)
- `skills/research/zj-tech-research-report/scripts/publish_report.py` (the publisher)
- `skills/research/zj-tech-research-report/scripts/validate_technical_report.py` (the `technical-c4/v1` quality gate)
- `skills/research/zj-tech-research-report/tests/verify_technical_report.py` (the positive information-gaps test)
- `~/.codex/skills/zj-research-report/ALIAS.md` (alias-only decision record)
- `ZJ-CONTEXT.md` ("Runtime alias exception (board-approved)" gloss)
- `docs/plans/agent-self-service-collaboration-roadmap.md` (active node `1-2-1-3-3-2`)
- `docs/prds/agent-self-service-collaboration.md` (the active Spec, not re-read in this preflight; the canonical scope is unchanged)
