# WorkBuddy CLI activation replay — 2026-08-24

## Classification

`observed-failure` with partial routing progress: WorkBuddy now invoked the
project-local activation seam, but the shared scope had no eligible frontier,
so no Work Item was claimed.

## Verified facts

- WorkBuddy wrote `.workbuddy/memory/2026-08-24.md` describing the run.
- The profile was `workbuddy-01` on `device-a`, with capability
  `technical-writing` and permission `zagentic-skill-write`.
- The invocation supplied no Work Item id.
- The result was `status=no_eligible_work`, `items=[]`, exit code `0`.
- The result is independently confirmed by the local store: one new
  `discover` event exists for `zagenticopn/experience-version`, with
  `activation_id=activation-a40f6da3210b` and `eligible_count=0`.
- The target scope contains no Work Item, so there is no `claim` event to
  observe yet.

## Interpretation

This is stronger than the earlier UI-only replay: the real WorkBuddy session
did reach and execute `scripts/activate_agent.py`. It is not C1 execution
claim success because Codex had not published an eligible Work Item before the
activation. The adapter correctly stopped at discovery and did not invent
work or claim an unrelated scope.

## Next gate

Codex must publish one narrow, eligible Work Item in the same scope. Human can
then trigger `检查 shared context` once more. A passing replay requires a new
`claim_succeeded` event for `workbuddy-01` and a structured `claimed` handoff;
the WorkBuddy process must still provide no Work Item id.
