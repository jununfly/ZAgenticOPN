---
name: zj-opn-activation
description: Route a Human-triggered ZAgenticOPN activation through the local JSON-Call runner and continue a claimed Work Item from its receipt. Use when a Human asks to check shared context, activate ZAgenticOPN collaboration, or continue shared coordination work; ordinary project-context lookup stays outside this skill.
---

# ZAgenticOPN activation

Use this skill for the one supported Human alias: `检查 shared context`.
Treat the alias as a trigger only. The machine contract is the versioned intent
`zagenticopn.activation.check_shared_context.v1`.

## Activation

1. Obtain the host/session values explicitly: `scope`, fresh `activation_id`,
   stable `agent_profile`, and `host_capabilities`. A WorkBuddy host may
   resolve `scope` from its host-level workspace binding; an unbound workspace
   is a `scope_unbound` stop, never a default-scope activation.
2. Send one JSON object to the canonical runner:
   `python -m zagentic_opn.activation_runner`.
3. Parse its one JSON receipt. The request contains the intent id and profile,
   never a Work Item id or a local store path. The host runtime configuration
   supplies the store.
4. Use the receipt as the runtime fact. A `claimed` receipt carries the full
   handoff; continue its objective and acceptance, then publish result, Git
   references, and review transitions through the coordination seam.
5. For `no_eligible_work`, `claim_conflict`, `unsupported_host`, `scope_unbound`,
   `handoff_delivery_failed`, `invalid_contract`, or `invalid_runtime_config`,
   report the receipt status and its `next_action`/`repair_action`. Let Human
   decide exceptions such as repair, reopen, or escalation.

The runner performs one discover and at most one claim. Keep the activation
bounded to that receipt: no polling, retry, Work Item guessing, scope search,
or model-based alias interpretation.

## Human summary

Generate the summary deterministically from receipt fields:

`status=<status>; activation_id=<activation_id>; scope=<scope>; work_id=<work_id>; next_action=<next_action>; evidence=<evidence>`

Include `event_recorded=false` when the receipt says the shared store could not
record an event. Do not add conclusions that are absent from the receipt.

See [activation-state-machine.md](references/activation-state-machine.md) for
the maintenance diagram and the boundary between activation routing and the
coordination lifecycle.
