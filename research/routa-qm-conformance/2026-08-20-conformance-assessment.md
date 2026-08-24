# Routa / qm：C1–C8 第三轮 conformance assessment

本评估基于固定 commit 的源码与测试链接，使用 `native / partial / unknown` 三态；`partial` 表示存在可抽取单位能力但语义未完全匹配，`unknown` 表示当前证据不足，不能解释为 absent。

本文前两张候选表保留源码/测试阶段的邻近能力判断；若与后续重放结果出现粒度差异，以“第五轮 C1–C4 黑盒 fixture 补充”中的最终 scorecard 为准。特别是 C2 的 `conformance_fail / unsupported_on_exposed_surface` 只描述当前 Agent 可调用 surface，不推出源码全局 absent。

## phodal/routa（ext）

| 门 | 状态 | 证据与判定 | ZAgenticOPN 仍需拥有的语义 |
| --- | --- | --- | --- |
| C1 publish/discover | partial | `find_ready_tasks` 能按依赖返回 ready task；lane handoff 能在已有 task 的 session 之间传递请求，但没有 task-agnostic Human trigger 后按 Agent eligibility 发布/发现 Work Item：[task_store.rs](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-core/src/store/task_store.rs#L261-L276)、[handoffs.rs](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-core/src/rpc/methods/kanban/handoffs.rs#L51-L160) | CollaborationScope、Agent profile/权限匹配、空结果及 filter reasons |
| C2 competing claim | partial | board queue 将并发 session 限制为 1，但这是调度容量，不是同一 Work Item 的原子执行 authority：[kanban-session-queue.feature](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/docs/bdd/kanban-session-queue.feature#L1-L20) | 原子 claim、竞争者拒绝、唯一执行 provenance |
| C3 result publication | partial | task evidence serializer 与 artifact gate 能表达 artifact、verification、completion 和 runs；没有固定的五字段跨 Agent result schema：[evidence.rs](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-server/src/api/tasks/evidence.rs#L140-L212)、[rust_api_task_artifacts.rs](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-server/tests/rust_api_task_artifacts.rs#L263-L486) | `result_summary`、`next_action`、`acceptance_status`、`blocker`、`references` 的发布/读取契约 |
| C4 review continuation | partial | `submit_lane_handoff` 校验目标 session 并接受 completed/blocked/failed，但它是已有 lane session 的回退交接，不是 reviewer Agent 自动发现、claim、验证、完成：[handoffs.rs](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-core/src/rpc/methods/kanban/handoffs.rs#L167-L230) | awaiting review 状态、review claim、references 核验与独立 reviewer provenance |
| C5 no eligible work | partial | workspace、board、column、status、priority、label filters 与 ready task 查询存在：[queries.rs](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-core/src/rpc/methods/kanban/queries.rs#L17-L220) | 以 Agent eligibility 过滤并返回可解释的排除原因 |
| C6 context defect | partial | 缺少 required artifacts 会以 BadRequest 阻断 transition，artifact 补齐后才 ready：[rust_api_task_artifacts.rs](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-server/tests/rust_api_task_artifacts.rs#L348-L486) | 缺少 acceptance/result/references 的结构化 coordination defect |
| C7 scope isolation | partial | TaskStore 与 Kanban API 以 workspace_id 为查询边界，架构 ADR 将 workspace 设为协调边界：[task_store.rs](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-core/src/store/task_store.rs#L166-L181)、[ADR 0003](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/docs/adr/0003-workspace-first-scope.md) | 默认 project/workspace isolation 与显式 cross-project permission |
| C8 private recovery | unknown | session/memory/store 表面存在，但本轮没有看到 Agent-private checkpoint 与 shared Work Item interruption recovery 的可重放测试 | private context、shared facts、恢复后的 claim/review continuation |

### Routa 的可抽取单位能力

- `ready task + workspace/status filtering`：可作为 eligibility 查询适配器候选，但必须补 Agent profile/permission 语义。
- `lane handoff state machine`：可作为 result/review transition 参考，但不能直接当作 Work Item claim。
- `artifact/evidence/readiness gate`：可作为 C3/C6 的交付门参考。
- `board queue concurrency`：可作为执行容量控制参考，不承担 claim authority。

## yc-software/qm（ref）

| 门 | 状态 | 证据与判定 | ZAgenticOPN 仍需拥有的语义 |
| --- | --- | --- | --- |
| C1 publish/discover | unknown | `listOpen` 与 active-run/delivery 相关测试能提供任务/投递视图，但没有证明 Agent 在 task-agnostic trigger 后发现 eligible shared Work Item：[task-store.test.ts](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/task-store.test.ts#L29-L49) | shared coordination query、eligibility、filter reasons |
| C2 competing claim | partial | `ClaimStore`、delivery drain claim 和 task compare-and-set 都有真实并发/冲突测试：[claims.ts](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/plugins/chassis/src/claims.ts#L1-L52)、[auth-broker-claim.test.ts](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/auth-broker-claim.test.ts#L65-L129)、[task-store.test.ts](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/task-store.test.ts#L54-L76)；但对象分别是 auth/delivery/task 状态，不是 Work Item execution authority | Work Item claim 与 review claim 的统一状态模型 |
| C3 result publication | unknown | artifact/session/delivery 路径存在，但本轮没有五字段结果发布与另一 Agent 读取的测试 | 结构化结果、失败 blocker、canonical Git references |
| C4 review continuation | unknown | session state、continuable 与 recovery 机制存在，但没有 reviewer Agent 独立发现/claim/verify/complete 的测试 | reviewer Agent 身份、awaiting review claim、验收发布 |
| C5 no eligible work | partial | task store 支持 open/status/session/origin 过滤：[task-store.ts](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/src/tasks/task-store.ts#L45-L58)、[task-store.test.ts](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/task-store.test.ts#L29-L49)；尚无 Agent eligibility/filter reason 输出 | 无 eligible Work Item 的结构化报告 |
| C6 context defect | partial | auth claim、memory API、scope 输入和错误状态有较多校验测试，但没有 shared coordination result defect 分类：[memory-agent-routes.test.ts](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/memory-agent-routes.test.ts#L184-L229) | 缺字段、坏 references、错 scope 的统一 blocker 类型 |
| C7 scope isolation | native-adjacent | memory routes 与 resource authz 测试覆盖 personal/org/channel scope、read/write claims、跨 scope 不可见和 private channel 限制：[memory-agent-routes.test.ts](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/memory-agent-routes.test.ts#L62-L120)、[scope-resources-authz.test.ts](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/scope-resources-authz.test.ts#L199-L239) | 将 coordination scope 与 memory scope 对齐，并保留显式 cross-project permission |
| C8 private recovery | partial | MemoryService 提供 per-scope queue、revision、compare-and-set replace、history/restore；pi harness 有空响应 re-prompt/recoveryDead 路径：[memory-service.ts](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/src/memory/memory-service.ts#L29-L39)、[memory-service.ts](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/src/memory/memory-service.ts#L108-L162)、[pi-harness.ts](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/src/harness/pi-harness.ts#L1888-L1931)；没有 shared Work Item interruption recovery | private checkpoint 必须能恢复并继续 claim/result/review |

### qm 的可抽取单位能力

- `ClaimStore + delivery drain claim`：高价值并发/去重单位能力，但必须重命名并重建 Work Item authority 语义。
- `TaskStore compare-and-set transition`：可作为状态转移原语，不等于 claim lifecycle。
- `scope-authorized memory + revision/restore`：最接近 private/shared context 单位能力。
- `session state/recovery`：可作为中断恢复适配器候选，但需绑定 Work Item continuation。

## 决策结果

1. Routa 和 qm 都不满足 A（整体复用）或 B（薄适配）的当前证据门。
2. 两者都出现可抽取单位能力，方向上更接近 C（ZAgenticOPN base-led selective reuse），但 C 仍需至少完成 C1–C4 fixture 的三次验证。
3. 当前 roadmap 仍保持 D 施工状态：先补 conformance fixture；未完成前不做 Human 的最终 A/B/C 复核，不开始产品 runtime。

## 第四轮 runtime/test 重放补充

固定 commit 上的邻近测试已完成连续三次重放，详细命令、环境、结果与语义边界见 [`2026-08-20-runtime-rerun.md`](2026-08-20-runtime-rerun.md)：qm 的 5 组测试每次 46 pass；Routa Kanban focused suite 每次 26 pass，artifact suite 每次 8 pass。结果提高了候选单位能力的运行稳定性证据，但没有新增 C1–C4 conformance 通过项：C1、C3、C4 仍 `unverified`，C2 仍只是邻近 `partial`。因此 D 不变，且本轮没有启动 ZAgenticOPN 产品 runtime。

## 第五轮 C1–C4 黑盒 fixture 补充

候选中立的黑盒 runner、协议和完整 HTTP transcript 已落盘：[`2026-08-20-black-box-fixture-protocol.md`](2026-08-20-black-box-fixture-protocol.md)、[`run_c1_c4_black_box.py`](run_c1_c4_black_box.py)、[`2026-08-20-black-box-routa.json`](2026-08-20-black-box-routa.json)、[`2026-08-20-black-box-qm.json`](2026-08-20-black-box-qm.json) 与结果汇总 [`2026-08-20-black-box-fixture-results.md`](2026-08-20-black-box-fixture-results.md)。Routa 与 qm 各连续运行 3 次；每次都固定 producer/discoverer-reviewer、两个 device id、workspace、Human 的唯一通用激活和 canonical Git references。

黑盒结果仍不等于候选通过：

- Routa：C1 三次都能通过 `/api/tasks/ready` 看到 task，C3 三次都能从 generic artifact 完整解析五字段 JSON，C4 三次都能看到 review column；但没有 Agent eligibility/filter reasons、Work Item claim transaction 或 reviewer claim/verify/complete，因此为 `partial / conformance_fail / pass / partial`。
- qm：C1 三次都能通过 shared `org:fixture` memory fact publish/search 发现 Work Item，C3 三次都能读取并解析含五字段的结构化 memory fact，C4 三次都能发现 `awaiting_review` fact；`/v1/apis` 没有 Work Item、claim 或 review endpoint，因此为 `partial / conformance_fail / pass / partial`。

两候选的 C3 均为 `strict_pass=3/3`，但 C1/C2/C4 仍未形成闭环，故没有候选通过核心硬门。C2 的结论使用 `conformance_fail / unsupported_on_exposed_surface` 双层标签；它描述当前 Agent 可调用 surface，不扩大为源码全局 absent。D 继续有效；不做 A/B/C 采用决策，不启动 ZAgenticOPN 产品 runtime。下一轮 ext 搜索最多 3 个候选，全部失败后转 C。
