# Routa / qm：C1–C4 黑盒 fixture 结果

运行器：[`run_c1_c4_black_box.py`](run_c1_c4_black_box.py)。协议：[`2026-08-20-black-box-fixture-protocol.md`](2026-08-20-black-box-fixture-protocol.md)。两个候选均在固定 commit 的临时 checkout 中运行，ZAgenticOPN 产品 runtime 未启动。

## 固定版本与运行产物

| 候选 | 类别 | commit | 黑盒产物 |
| --- | --- | --- | --- |
| `phodal/routa` | ext | [`e48861a`](https://github.com/phodal/routa/tree/e48861ab81e2b30378fd32f05204a3ab424c4fec) | [`2026-08-20-black-box-routa.json`](2026-08-20-black-box-routa.json) |
| `yc-software/qm` | ref | [`568252b`](https://github.com/yc-software/qm/tree/568252bd4e6da5288b239573abef972f3e16b3f9) | [`2026-08-20-black-box-qm.json`](2026-08-20-black-box-qm.json) |

每个候选均完成 3 次运行；每次记录 `agent_id`、`device_id`、`workspace_id`、Human activation、HTTP transcript、candidate commit 与 canonical references。

## 严格门结果

| 候选 | C1 | C2 | C3 | C4 | 结论 |
| --- | --- | --- | --- | --- | --- |
| Routa | 0/3 strict pass；3/3 partial | 0/3；3/3 conformance fail / unsupported on exposed surface | 3/3 pass | 0/3 strict pass；3/3 partial | 未通过 C1/C2/C4 硬门 |
| qm | 0/3 strict pass；3/3 partial | 0/3；3/3 conformance fail / unsupported on exposed surface | 3/3 pass | 0/3 strict pass；3/3 partial | 未通过 C1/C2/C4 硬门 |

## Routa 黑盒观察

- C1：Agent B 不携带 task ID 调用 `/api/tasks/ready?workspaceId=default`，三次都能看到 producer 创建的 task；但响应没有 Agent eligibility 或 filter reasons，因此只能记为 `partial`。
- C2：两个 Agent 并发探测 task claim 入口，候选 HTTP surface 得到 `404`；没有可执行的原子 Work Item claim、winner/loser 或唯一执行 provenance，因此记为 `conformance_fail / unsupported_on_exposed_surface`，不推出源码全局 absent。
- C3：producer 通过 `/api/tasks/{id}/artifacts` 发布 JSON，Agent B 从 artifact list 读取并完成 JSON parse 与五字段校验，三次均通过；generic storage 在结构化记录口径下满足 C3。
- C4：producer 能把 task 推到 `review` 列，Agent B 能从 task list 看到它；review claim/complete 入口均得到 `404`，没有 reviewer verify/complete transition，因此记为 `partial`。

## qm 黑盒观察

- C1：Agent A 通过 `/v1/memory/facts` 写入共享 scope `org:fixture`，Agent B 通过 `/v1/memory/search` 找到同一 Work Item fact，三次均成功；`/v1/apis` 没有 Work Item endpoint，故这是 shared-memory 邻近能力而不是 typed eligible Work Item discovery，记为 `partial`。
- C2：两个 Agent 并发探测 Work Item claim，响应均为受保护 surface 的 `403`；`/v1/apis` 没有 claim endpoint，不能得到 winner/loser 或 execution authority，记为 `conformance_fail / unsupported_on_exposed_surface`。未知路径的 `403` 不被解读为 endpoint 存在。
- C3：Agent A 写入包含 `result_summary`、`next_action`、`acceptance_status`、`blocker`、`references` 的 memory fact，Agent B 三次均能读取并解析五字段；按“结构化 shared record、generic storage 可接受”的口径，C3 为 `pass`。
- C4：Agent B 三次都能搜索到 `awaiting_review` fact；`/v1/apis` 没有 review/claim/complete surface，不能证明 reviewer Agent 的 claim、reference verification 或完成转移，记为 `partial`。

## 决策影响

黑盒重放把前一轮的 `unverified` 进一步拆成了可验证的邻近事实：Routa 的 ready task、结构化 artifact 与 review-column 表面稳定；qm 的 shared memory publish/search 与结构化五字段 fact 读取稳定。两者 C3 均通过，但 C1 为 `partial`、C2 为 `conformance_fail / unsupported_on_exposed_surface`、C4 为 `partial`，所以仍没有候选通过 C1/C2/C4 硬门。D 继续有效；不进入 A/B/C 采用决策，不开始 ZAgenticOPN 产品 runtime。
