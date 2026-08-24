# Routa / qm → ZAgenticOPN Experience Version fixture 映射

本表把第二轮发现的邻近单位能力映射到 Feature 1 的固定 C1–C8 语义。它是下一轮 conformance 采集与黑盒验证的工作表，不是候选通过声明。

口径冻结：C3 允许 generic storage，只要另一 Agent 能机器解析结构化五字段 shared record；自由文本不算通过。C2 若当前 exposed surface 没有可调用的 Work Item claim API，记为 `conformance_fail / unsupported_on_exposed_surface`，不能改写成源码全局 absent。

| 门 | ZAgenticOPN 必须证明 | Routa 可复用信号 | qm 可复用信号 | 尚缺语义证据 | 下一步 fixture |
| --- | --- | --- | --- | --- | --- |
| C1 publish/discover | Human 只说“检查 shared context”；Agent 自己发现 eligible Work Item，不要求 Human 指定 ID | `find_ready_tasks`、workspace/status 查询、lane handoff | `listOpen`、active-run/delivery 邻近机制 | 无 task-agnostic discover API；无 Agent profile/permission eligibility 输出 | 预置 eligible 与 ineligible 两项；三次激活后验证发现结果、filter reasons 与 Human intervention=0 |
| C2 competing claim | 同一 Work Item 只能有一个执行 authority；竞争者不能执行 | board concurrency/queued session | single-use claim、delivery drain claim、task CAS | Routa queue 不是 Work Item claim；qm claim 目前用于 auth/delivery/task state | 两个 Agent 并发 claim 同一 Work Item；验证一胜一拒、无重复执行、Git provenance 唯一 |
| C3 result publication | 发布 `result_summary`、`next_action`、`acceptance_status`、`blocker`、`references` | artifact/evidence/readiness gate、task completion summary | artifact/session/delivery 状态 | 没看到五字段跨 Agent result schema 与读取链 | Producer 发布成功/失败两种结果；Consumer 不补上下文即可读取并校验字段 |
| C4 review continuation | Reviewer Agent 自动发现 awaiting review、claim、核验 references、完成 review | lane handoff 到上一 session、submit status | continuation/session state 邻近机制 | 没有 reviewer Agent 独立 claim + verify + complete 闭环 | Producer 结束后置 awaiting review；独立 reviewer 三次完成，Human 不复制上下文 |
| C5 no eligible work | 无符合项时报告空结果与排除原因，不发明任务 | ready task、workspace/status/label filters | open task/status filters | 缺少统一 filter-reason schema | 全部任务不满足 scope/profile/状态；验证 `available=[]` 且原因可解释 |
| C6 context defect | 缺 acceptance/result/references 被分类为 defect，不算成功 handoff | missing required artifact 阻断 transition、BadRequest | auth/claim/memory 输入校验 | 缺 shared coordination result defect 分类 | 注入缺字段、错 scope、坏 references；验证结构化 blocker 与可观测 defect |
| C7 scope isolation | 默认 project/workspace 隔离；显式跨项目需权限 | workspace boundary 与 workspace query | personal/org/channel scope、ACL 与 token read/write claims | 需确认 Agent coordination query 的默认 scope 与显式导航 | 两 workspace + 一个显式授权 cross-scope；验证默认不可见、授权后可见 |
| C8 private recovery | private recovery context 与 shared facts 分离；中断后可继续同一 Work Item | session/memory/runtime 表面 | per-scope memory、revision/restore、pi re-prompt/recovery | 未证明 Agent 中断恢复时保留 private context 并继续 shared Work Item | 中断 producer；新激活恢复 private checkpoint，读取 shared result，继续至 review |

## 统一退出门

1. C1–C4 是硬门；每个 fixture 连续运行 3 次。
2. 每次运行都记录 `agent_id`、`device_id`、`workspace_id`、Work Item 状态事件和 canonical Git references。
3. 任务特定 Human intervention 必须为 0；Human 只执行初始目标和“检查 shared context”激活脚本。
4. 任一候选只能在硬门通过后进入 A/B/C 讨论：A 整体复用、B 薄适配、C base-led selective reuse；否则继续 D。
5. 当前两候选都尚未通过，因此本表只授权下一轮证据/fixture 工作，不授权产品 runtime 实现。
