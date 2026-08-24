# WorkBuddy claim and blocker replay — 2026-08-24

## Classification

`observed-failure` after a real C1 routing pass: WorkBuddy discovered and
claimed the published execution item, then correctly blocked it when the
creator's acceptance could not be completed under the result-reference
contract.

## Store evidence

The target scope contains these verified events:

- `discover`, activation `activation-e56fd1670b77`, `eligible_count=1`.
- `claim_succeeded`, work item
  `activation-routing-workbuddy-20260824`, agent `workbuddy-01`, kind
  `execution`.
- `block`, same Work Item, with category
  `seam_contract_vs_acceptance_text`.

The Work Item is now `blocked`, revision `2`. The blocker reports the exact
conflict:

- acceptance says the routing verification requires no source change;
- `CoordinationProtocol._require_result` requires at least one result
  reference containing `commit`, `files`, and `tests`.

WorkBuddy did not fabricate a commit or publish a false result. The block
operation deactivates the execution claim, so it does not leave an orphaned
claim.

## Creator decision

Preserve the Git provenance contract. Do not weaken `_require_result` just for
this fixture, and do not use an `N/A` commit as if it were provenance. Keep
this routing-only Work Item's block as the observed evidence that C1 routing
worked but the Work Item was not a valid result-bearing execution task.

The next executable Work Item must either have a real committed artifact and
test evidence, or be introduced through an explicit product-contract change
for evidence-only work. That is a separate decision; it is not silently
inferred from this replay.
