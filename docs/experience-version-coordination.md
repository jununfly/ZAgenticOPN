# Experience Version coordination seam

The first implementation is a small Python module with a SQLite shared context. Agents use the public `CoordinationProtocol` interface directly in-process or through the canonical `python -m zagentic_opn.activation_runner` JSON-Call, while SQLite, event projection, and scorecard formatting remain implementation details.

The task-agnostic activation alias is resolved by the ZAgenticOPN-owned
`zj-opn-activation` Skill/host adapter. The runner accepts only the versioned
intent `zagenticopn.activation.check_shared_context.v1`; it performs one
discover and at most one claim, then returns one structured receipt. Runtime
configuration is host-level and is reloaded for every call from
`zagenticopn/runtime.json` under the system user config directory. See
`skills/zj-opn-activation/references/activation-state-machine.md` for the
activation-only maintenance diagram.

The store is intentionally local and durable enough for the same-device smoke test. It is not a production memory service, scheduler, lease manager, notification system, or recovery system.

## Human exception: reopen a stale claim

If an Agent runtime activates the wrong project scope or disappears after a
claim, do not fabricate a result and do not edit SQLite directly. Human may
explicitly reopen only a `claimed` or `blocked` Work Item:

```sh
python -m zagentic_opn --db "$DB" reopen \
  --scope "$SCOPE" \
  --work-id "$WORK_ID" \
  --operator-id human-zj \
  --reason "The owning Agent runtime did not receive the handoff in this project scope."
```

The operation clears active claims, returns the item to `available`, and emits
`human_reopened` with the operator, reason, previous state, and previous
claimant. It is an explicit exception path: there is no claim TTL, automatic
retry, background recovery, or cross-scope search. After reopening, the next
Agent must activate from the Work Item's owning project scope; a
`no_eligible_work` result from another scope is not evidence that this item is
complete or absent.

## Agent activation flow

Each activation receives a stable `agent_id`, `device_id`, an experiment `scope`, and a fresh `activation_id`. The human-facing prompt remains only “检查 shared context”. The agent performs `discover`; if an eligible item exists, it performs one `claim` and then executes the work outside the coordination module.

The host owns the scope handoff. A WorkBuddy adapter may use an explicit
`ZAGENTICOPN_SCOPE`, or match the event workspace `cwd` against host-level
`scope_bindings` in `zagenticopn/runtime.json`; the most-specific binding wins.
If neither is available, the adapter returns `scope_unbound` and does not call
the runner. The runner never derives scope from cwd, Git remotes, project
files, or Work Items, and it never searches another scope.

The project-local activation entrypoint makes that route executable from an
external Agent runtime:

```sh
python scripts/activate_agent.py \
  --scope jununfly/ZAgentic/zj-research-report \
  --agent-id workbuddy-01 \
  --device-id device-a \
  --capabilities technical-writing \
  --permissions zagentic-skill-write
```

It does not accept a Work Item id. It performs one discovery and claims at
most the first eligible execution or review item, returning a structured JSON
handoff. The activation id is generated for the session unless supplied by
the runtime environment.

The canonical host contract is instead a single JSON object on stdin to
`python -m zagentic_opn.activation_runner`. It requires `schema_version`,
`intent_id`, `activation_id`, `scope`, `agent_profile`, and the controlled
`host_capabilities` list. The request never carries a local database path.
The runner returns `claimed`, `no_eligible_work`, `claim_conflict`,
`unsupported_host`, `invalid_contract`, or `invalid_runtime_config` as a
structured receipt; a host handoff failure is reported as
`handoff_delivery_failed` and recorded when the store is available.

```sh
DB=.zagenticopn/shared.sqlite3
SCOPE=zagenticopn/experience-version

python -m zagentic_opn --db "$DB" publish \
  --scope "$SCOPE" \
  --objective "Improve the zj-research-report skill" \
  --acceptance "Updated source skill and verifiable Git artifact" \
  --agent-id codex-01 --device-id device-a \
  --capabilities technical-writing --permissions zagentic-skill-write

python -m zagentic_opn --db "$DB" discover \
  --scope "$SCOPE" --agent-id workbuddy-01 --device-id device-a \
  --capabilities technical-writing --permissions zagentic-skill-write \
  --activation-id activation-workbuddy-1
```

The result reference must include a commit, changed files, and test outcomes. A reviewer then discovers the `awaiting_agent_review` item, claims review, verifies the Git reference, and accepts or returns the result. A `request_changes` decision returns the item to `available`, clears the prior result fields, and releases both the review claim and the old execution claim so a later task-agnostic activation can retry cleanly; the review event retains the reason. The store never receives the conversation or a code copy.

## AgentRQ adapter validation boundary

The AgentRQ adapter is a removable transport projection. Its black-box seam is
limited to `createTask`, task-agnostic `getTask`, `updateTaskStatus`, and
`reply`, matching the fixed candidate surface at commit
`45c87390fdb535066a05c0592e8183b1b461689b`. ZAgenticOPN remains authoritative
for scope and eligibility, atomic execution/review claims, result state and
Git references.

The adapter fixture therefore reports two layers of evidence: C1/C2/C4 may
pass at the adapter level when the wrapper owns the missing semantics, while
the same result is not reported as native AgentRQ conformance. In particular,
AgentRQ status updates occur only after a product-owned claim succeeds, and a
generic review task is projected only after the product enters
`awaiting_agent_review`. The reproducible report is generated by
`scripts/run_agentrq_adapter_black_box.py`.

## Verification

Run the public-seam black-box fixtures with:

```sh
python -m unittest discover -s tests -v
```

Export the first health view with `scorecard --scope "$SCOPE" --out scorecard.md`. The scorecard is an experiment artifact; real-time telemetry and dashboards are deferred.
