# Routa 与 qm：第二轮固定源码/测试证据补充

本文件记录第二轮对固定 commit 的直接 GitHub canonical source/test 读取。它补充 sealed ledger 的路径导航缺口；ledger 与正式 technical-c4 报告仍是事实发布入口，本文件不把未完成的邻近机制升级为 Feature 1 conformance 结论。

## 固定版本

- Routa：[`phodal/routa@e48861ab81e2b30378fd32f05204a3ab424c4fec`](https://github.com/phodal/routa/tree/e48861ab81e2b30378fd32f05204a3ab424c4fec)
- qm：[`yc-software/qm@568252bd4e6da5288b239573abef972f3e16b3f9`](https://github.com/yc-software/qm/tree/568252bd4e6da5288b239573abef972f3e16b3f9)

## Routa：最接近 Feature 1 的机制

### Lane handoff 是任务内的会话转移，不是通用 Work Item claim

`request_previous_lane_handoff` 会加载 task、寻找上一 lane 的 session，创建带 `from_session_id`、`to_session_id`、列和状态的 `TaskLaneHandoff`，写回 task，并尝试把 handoff 投递到目标 session；投递后状态变为 `Delivered`，失败变为 `Failed`：[handoffs.rs#L51-L160](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-core/src/rpc/methods/kanban/handoffs.rs#L51-L160)。

`submit_lane_handoff` 会确认 handoff 存在且目标 session 与调用 session 相同，然后接受 `completed`、`blocked`、`failed` 状态，持久化并广播 workspace event：[handoffs.rs#L167-L230](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-core/src/rpc/methods/kanban/handoffs.rs#L167-L230)。

这证明 Routa 有任务内 session-to-session handoff 状态机；尚未证明 task-agnostic Human trigger 后任一合格 Agent 可以发现 available Work Item，也没有看到与 ZAgenticOPN `available → claimed` 等价的原子 claim 门。

### Ready task、workspace scope 与过滤机制已存在

`TaskStore` 按 workspace、session、status、assignee 查询，并提供 `find_ready_tasks`：只返回 pending 且依赖已完成的 task：[task_store.rs#L166-L276](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-core/src/store/task_store.rs#L166-L276)。Kanban 查询 API 也按 workspace、board、column、status、priority 和 label 过滤：[queries.rs#L17-L220](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-core/src/rpc/methods/kanban/queries.rs#L17-L220)。

这些是 C5/C7 的强邻近证据，但还没有显示 eligibility 是否按 Agent profile/权限匹配，并在无 eligible work 时返回结构化 filter reasons。

### Artifact/evidence gate 比结构化跨 Agent 结果更具体

任务序列化会附加 `artifactSummary`、`evidenceSummary`、story readiness 和 INVEST validation；evidence summary 还包含 artifact、verification、completion 与 runs：[evidence.rs#L17-L75](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-server/src/api/tasks/evidence.rs#L17-L75)、[evidence.rs#L140-L212](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-server/src/api/tasks/evidence.rs#L140-L212)。

真实 API test 验证缺少 required screenshot 会阻止进入 review，创建 artifact 后 task 变为 ready，`/api/tasks/ready` 可返回该 task：[rust_api_task_artifacts.rs#L263-L486](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-server/tests/rust_api_task_artifacts.rs#L263-L486)。这支持 C3/C6 的“交付门”方向，但仍不是 `result_summary`、`next_action`、`acceptance_status`、`blocker`、`references` 五字段的跨 Agent 发布/读取协议。

### Queue concurrency 不是 competing claim

BDD 场景规定 board concurrency limit 为 1：第二张 card 保持 queued，第一张 session 完成后第二张才获得自己的 trigger session：[kanban-session-queue.feature#L1-L20](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/docs/bdd/kanban-session-queue.feature#L1-L20)。这证明 per-board session scheduling；尚未证明两个 Agent 对同一 Work Item 的原子执行权竞争。

## qm：邻近的 claim、CAS、scope 与 memory 机制

### Claim 是有真实并发测试的，但当前用途不是 Work Item

`ClaimStore.claimFirst(ids, expiresAtMs)` 通过 `/v1/auth/broker/claim` 获取一个 single-use id，`claimOnce` 和窗口 claim 都复用该接口：[claims.ts#L1-L52](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/plugins/chassis/src/claims.ts#L1-L52)。

auth broker 测试验证每个 id 只发放一次、批量 claim 返回第一个 free slot、RAM-only replay store 被拒绝、过期和输入校验：[auth-broker-claim.test.ts#L65-L129](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/auth-broker-claim.test.ts#L65-L129)。delivery drain 测试进一步验证两个重叠 poller 不能同时收到同一 delivery，过期 claim 会重新出现：[delivery-drain-claim.test.ts#L40-L88](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/delivery-drain-claim.test.ts#L40-L88)。

这是 C2 的可复用单位能力候选，但当前证据指向认证 nonce、rate slot 和 delivery row，不是 Agent Work Item 的执行权、review claim 或 Git provenance。

### Task store 有 compare-and-set 状态转移

`TaskStore.transitionStatus` 要求调用者提供 expected status；内存实现发现当前状态不匹配时返回 null：[task-store.ts#L45-L58](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/src/tasks/task-store.ts#L45-L58)、[memory-task-store.ts#L79-L96](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/src/tasks/memory-task-store.ts#L79-L96)。测试用两个 worker 并发从 pending 转移，只有一个成功，并只追加成功事件：[task-store.test.ts#L54-L76](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/task-store.test.ts#L54-L76)。

这比单纯文档更接近 C2，但它仍是 session/origin task 状态 CAS；下一步必须确认 task 是否是跨 Agent shared Work Item，以及 transition 是否覆盖 claim/review authority。

### Memory scope 与 private/shared 隔离证据较强，恢复闭环仍不足

Memory API 测试验证 personal/org scope 的读写授权、跨 scope 搜索过滤、伪造 body scope 被 token 覆盖、org write 权限和 private channel 来源限制：[memory-agent-routes.test.ts#L62-L120](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/memory-agent-routes.test.ts#L62-L120)、[memory-agent-routes.test.ts#L135-L181](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/memory-agent-routes.test.ts#L135-L181)、[memory-agent-routes.test.ts#L323-L374](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/memory-agent-routes.test.ts#L323-L374)。Memory service 还提供 per-scope queue、revision head、compare-and-set replace 与 restore：[memory-service.ts#L29-L39](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/src/memory/memory-service.ts#L29-L39)、[memory-service.ts#L108-L162](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/src/memory/memory-service.ts#L108-L162)。

这些证据支持 C7/C8 的 memory isolation 单位能力；仍没有证明 Agent 中断后从 private context 恢复并继续同一 shared Work Item，也没有 C1/C3/C4 的跨 Agent continuation。

## Conformance 更新

| 门 | Routa | qm | 当前判断 |
| --- | --- | --- | --- |
| C1 publish/discover | task/queue/handoff 有邻近机制 | delivery/active-run 邻近机制 | 两者均未验证 |
| C2 competing claim | board queue，未见 Work Item claim | delivery claim + task CAS，有并发测试 | 可抽取候选，语义仍未验证 |
| C3 result publication | artifact/evidence/readiness gate | artifact/session 相关能力，未见五字段 handoff | 两者均未验证 |
| C4 review continuation | lane handoff 可返回上一 session | continuation/session 状态材料 | reviewer Agent 闭环未验证 |
| C5 no eligible work | ready task + workspace/status filters | open task/CAS filters | 需补 filter reasons 证据 |
| C7 scope isolation | workspace boundary + query filters | scope/ACL tests较强 | 邻近能力，需对齐语义 |
| C8 private recovery | session/memory 表面 | personal/org memory + revision/restore | shared Work Item recovery 未验证 |

当前仍不改变 D：下一步不是选型或实现，而是把这些邻近机制映射到 Experience Version fixture，明确每个机制还缺哪一条跨 Agent 语义证据。
