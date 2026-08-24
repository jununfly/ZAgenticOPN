# Feature 1 C 路线：选择性复用单位能力地图

状态：Experience Version 实施基线；C 路线已获授权，当前不依赖候选运行时。

上位 Spec：[Agent 自服务协作 Experience Version](../prds/agent-self-service-collaboration-experience-version.md)

证据汇总：[ext 轮次最终筛选结果](../../research/routa-qm-conformance/2026-08-20-ext-round-results.md)

## C 路线的含义

C 不是把某个候选项目改造成 ZAgenticOPN，也不是把多个项目拼成一个隐式平台。C 表示：ZAgenticOPN 继续拥有 Feature 1 的产品语义和组合边界，只从候选中抽取经过证据支持的窄单位能力；每个单位能力都必须有明确输入、输出、所有权、替换方式和当前阶段使用理由。

## 语义所有权

以下语义必须由 ZAgenticOPN 自有，不能委托给候选项目：

| ZAgenticOPN 语义 | 必须保持的事实 |
| --- | --- |
| `AgentInstance` 与 `device_id` | 同一设备上的 Codex、WorkBuddy 等 runtime 是可区分的稳定参与者；session 不是新主体。 |
| `CollaborationScope` | 默认按 Initiative/project 隔离；显式跨项目导航必须可见并受授权。 |
| Work Item eligibility | scope、状态和固定 Agent profile/权限三项过滤；不做 Agent 自动能力发现。 |
| Work Item lifecycle | `available → claimed → awaiting_agent_review → completed`，以及 blocked/cancelled/reopen 的显式转移。 |
| Claim authority | 同一 Work Item 只有一个执行 claimant；竞争 claim 必须原子失败；首版不引入 TTL、抢占和后台恢复。 |
| Result/review semantics | 五字段结果、结构化 blocker、Git provenance、reviewer re-claim、references 核验和完成条件。 |
| Human action script | 一次初始目标 + 三次“检查 shared context”激活；Human 只处理例外。 |
| Health scorecard | C1–C4、Human intervention、context defects、Git acceptance 和三次复验的统一统计口径。 |

## 可抽取单位能力

| 来源 | 可抽取单位能力 | 允许的组合位置 | 明确不能承担 |
| --- | --- | --- | --- |
| Routa | workspace/status/task filtering；artifact/evidence/readiness gate；lane handoff 状态参考；board queue concurrency | `CoordinationStore` 查询适配器、artifact readiness 适配器、执行容量控制 | Agent eligibility 的完整语义、Work Item 原子 claim、reviewer claim/verify/complete |
| MCP Agent Mail Rust | Agent identity/detection；message/inbox/delivery receipt；file reservation/conflict check；message search | Agent integration 适配器、异常通知、资源冲突提示和可观测事件输入 | Work Item frontier、执行 authority、结果五字段协议、review 状态链 |
| Avernet | vendor-neutral Work Item DTO/port/router 的接口分层参考 | 只可作为协议/接口设计参考；community profile 的 no-op 不可作为运行时依赖 | 实际 publish/discover、claim、result、review；不把 no-op port 当作可用能力 |
| qm（ref） | ClaimStore/delivery drain claim；TaskStore CAS；scope-authorized memory；revision/restore；session recovery | 后续在统一 semantic adapter 中评估，先写黑盒/契约 fixture 再决定是否抽取 | 直接替代 ZAgenticOPN Work Item authority 或 shared coordination schema |
| ZAgenticLoop（legacy） | 本轮不预设任何代码复用；只在当前证据要求时重新评估单一能力 | 不进入默认依赖和基础架构 | 不复活项目、不复制其过度治理和未验证 runtime |

## 组合原则

1. 每个单位能力只能通过明确 adapter seam 进入；候选的状态名、数据库表和身份模型不得渗透到产品语义层。
2. 任何抽取都必须保留可替换实现：ZAgenticOPN 的最小内存/文件 fixture 可以替代候选实现，避免被候选运行时锁定。
3. 先用同一 C1–C4 fixture 验证组合后的语义，再讨论性能、HA、完整 ACL 或平台化；邻近单元测试不能替代黑盒闭环。
4. shared coordination context 只保存结构化事实和 canonical Git references；message、memory 或 artifact 单位能力不得把完整对话、大文件或 private context 变成共享事实。
5. 每个单位能力必须记录 `source_commit`、许可证、升级责任、删除/替换路径和观测事件；没有这些信息的能力只保留为研究参考。

## 实施准入门（已通过）

以下条件已全部满足，Human 已授权进入 Experience Version runtime：

- Human 明确接受 C 路线，并确认 ZAgenticOPN 继续拥有上表的全部产品语义；
- 首个切片选择不引入候选运行时；Python stdlib + SQLite 是可替换的本地实现，候选单位能力留到真实证据要求时再评估；
- 为 C1–C4 建立候选中立的 integration fixture、竞争 claim fixture、结果 schema fixture 和 review continuation fixture；
- 明确首个纵向切片的最小部署方式、Git provenance 和 Markdown scorecard；
- Human 明确授权产品 runtime/PoC，或明确继续停留在 Problem Discovery。

当前只实现同设备单项目最小纵向切片；部署、自动发现、自动唤醒、后台恢复、生产治理和从 ZAgenticLoop 抽取代码仍然 Deferred。
