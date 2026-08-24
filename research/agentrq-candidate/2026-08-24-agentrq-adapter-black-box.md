# AgentRQ adapter C1/C2/C4 black-box validation

- Candidate: `agentrq/agentrq`
- Fixed commit: `45c87390fdb535066a05c0592e8183b1b461689b`
- Fixture boundary: exposed `createTask/getTask/updateTaskStatus/reply` only
- Product semantic owner: ZAgenticOPN `CoordinationProtocol`

## Gate results

| Gate | Result | Evidence |
| --- | --- | --- |
| C1 | **PASS** | work_id=c1-work, discovery_status=eligible_work, human_supplied_work_id=False, task_agnostic_getTask_calls=1, filter_reasons={} |
| C2 | **PASS** | work_id=c2-work, effective_claimants=1, claim_conflicts=1, transport_ongoing_updates=1, duplicate_execution=0 |
| C4 | **PASS** | work_id=c4-work, review_task_id=c4-work:review, reviewer_supplied_work_id=False, review_discovery_status=eligible_work, final_state=completed |

## Native surface boundary

- C1 is an adapted pass: AgentRQ supplies task-agnostic queue transport; ZAgenticOPN applies eligibility.
- C2 is not a native AgentRQ pass: the wrapper owns atomic claim; AgentRQ status is updated only after success.
- C4 is not a native AgentRQ pass: the wrapper projects a generic review task; ZAgenticOPN owns review state and provenance.
