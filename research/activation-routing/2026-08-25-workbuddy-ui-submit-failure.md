# WorkBuddy UI submission failure — 2026-08-25

## Classification

`observed-failure`: the local Proxy and host hook pass isolated tests, but the
formal WorkBuddy v5.3.14 UI did not submit the fixed activation request.

## Setup

- WorkBuddy v5.3.14, same macOS device.
- Formal WorkBuddy conversation under the `ZAgenticOPN` workspace entry.
- Shared store: `.zagenticopn/shared.sqlite3`.
- Available Work Item: `workbuddy-ui-proxy-replay-20260825`.
- Work Item scope: `zagenticopn/experience-version`.
- Work Item state before and after replay: `available`, claimant `null`,
  revision `0`.

## Replay

The input editor was filled with the exact Human phrase `检查 shared context`.
The following UI submission attempts were made from the formal conversation:

1. Return.
2. Command-Return.
3. The visible send control, after restoring the exact phrase in the editor.

The conversation did not receive a new user message or assistant run. The
editor remained active; the existing prior response remained the only visible
assistant result.

## Independent shared-store check

The store contained only the publish event for this Work Item after the replay:

```text
workbuddy-ui-proxy-replay-20260825: available, claimant=null, revision=0
latest event for this item: publish
```

There was no new `discover`, `claim_succeeded`, `claim_conflict`, or
`handoff` evidence. Therefore this replay cannot be counted as C1 or as a
Proxy/UI pass.

## Plugin boundary check

The host CLI reports
`zagenticopn-agent-integration@zagenticopn-local` as enabled. The WorkBuddy
log also records that the plugin's `UserPromptSubmit` configuration loaded two
hooks. This proves plugin discovery/configuration, not invocation: the absent
new UI message explains why no hook-side activation event was produced.

## Conclusion and next action

The remaining failure is the WorkBuddy UI editor/submission path. It is not
evidence that the coordination claim or handoff assembly is incorrect. Keep
the value experiments paused. The next investigation must use a supported
WorkBuddy UI submission mechanism or a vendor/runtime fix, then repeat this
single narrow Work Item replay and independently check the shared store.
