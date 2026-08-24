# Feature 1 Experience Version 对齐契约

状态：Q1–Q6 已确认；已转为 Experience Version Spec（历史对齐记录）

上位 Spec：[Agent 自服务协作](../prds/agent-self-service-collaboration.md)

生命周期分类：`stage-critical`。本文件记录 Problem Discovery 阶段冻结的可证伪产品假设、最小纵向切片和退出证据；当前实施授权以 Experience Version Spec 和 roadmap 为准。

## 目的

在开始原型搭建前，先对齐用户路径、Work Item 语义、Human 与 Agent 的责任、失败分类和价值验收口径。技术路线和开源单位能力只有在这些产品语义冻结后才进入决策。

## 建议先冻结的默认值

| 项目 | 建议默认值 | 原因 |
| --- | --- | --- |
| 参与者 | 同一设备上的 Codex → WorkBuddy → Codex | 先验证产品闭环，暂不把跨设备故障混入首个实验。 |
| 协作范围 | 一个真实项目、一个隔离实验分支 | Git 仍是工程事实源，实验结果可回滚。 |
| 任务 | 一个有明确 acceptance、需要真实修改和测试的窄任务 | 排除无效 demo，直接验证结果价值。 |
| Human 动作 | 3 次任务无关激活；只提供一次初始目标 | 测量搬运、派发和缝合是否归零。 |
| Agent 入口 | Human 只说“检查 shared context” | 固定产品交互，不让提示词承担隐藏编排。 |
| Work Item 状态 | `available → claimed → awaiting_agent_review → completed`，另有 `blocked` | 覆盖 C1–C4，避免提前设计完整工作流。 |
| 共享数据 | objective、acceptance、state、claimant、result_summary、next_action、references | 足以完成接续，不复制完整对话和大文件。 |
| 观察方式 | 事件导出 + Markdown scorecard | 先验证价值，不建设实时 Dashboard。 |

## 必须由 Human 确认的六项决策

### Q1：哪一个真实任务作为首个纵向切片？

Human 已确认：**找一份优秀的技术方案分析报告，改进 `zj-research-report` 这个 skill 的效果。**

这次任务作为首个真实任务，验证的是 Agent 能否在不搬运完整上下文的情况下接续一项真实的跨仓库文档与技能维护工作；它不授权 ZAgenticOPN 产品代码、Experience Version runtime 或 PoC 实现。

#### Experiment brief

- **目标与基线**：以固定 commit 的 Kubernetes KEP-753 技术方案报告为标杆，改进 `zj-research-report` 的决策链、生命周期深度和技术报告投影；改进前的基线是技术比较仍使用 `zj-draft/v1`，C4 图、深读卡片和指标矩阵不能稳定进入最终报告。
- **允许修改的范围**：ZAgentic 中 `skills/engineering/zj-research-report/` 的源 skill、参考文件和验证脚本；当前设备的 `/Users/bilibili/.codex/skills/zj-research-report/` 运行副本可同步更新。不得修改 ZAgenticOPN 产品代码或启动 Feature 1 runtime PoC。
- **最终 Git artifact**：ZAgentic 源 skill 的变更与 `references/technical-proposal-exemplar.md`；运行副本是本设备的生效安装物，不是 durable source of truth。
- **方案 A 基线**：对同一份真实技术比较 Report IR 使用改进前的 `zj-draft/v1` 编译，并记录其缺少技术结构投影的结果；改进后使用 `technical-c4/v1` 重新编译对照。

必须冻结：

- 初始目标文本：找一份优秀的技术方案分析报告，改进 `zj-research-report` 这个 skill 的效果；
- acceptance：固定并引用标杆报告；更新源 skill 与运行副本；技术 IR 能输出 Key-Value、C4 全景图和子主题图、候选卡片、指标矩阵、风险/验证链路和建议；同一真实报告重新编译成功；skill 校验通过；发布 receipt 的 `healthy` 为 `true`；
- 允许修改的文件或目录：以上 Experiment brief 所列范围；
- 最终 Git artifact 和测试命令：ZAgentic skill 源文件与参考文件，运行 `quick_validate.py`，并通过 `publish_report.py` 完成一次不覆盖已有文件的编译/发布验证；
- 方案 A 基线的同类任务：同一份真实技术比较 Report IR 在改进前后的 `zj-draft/v1` 与 `technical-c4/v1` 投影对照。

产物：一份可重复的 experiment brief。没有真实 acceptance 的任务不进入原型。

### Q2：Human 在闭环中允许做什么？

Human 已确认，直接采用：只提交一次初始目标，执行三次任务无关激活（Codex → WorkBuddy → Codex），并处理权限、冲突、方向和无法继续的异常。

三次激活统一使用“检查 shared context”，不把任务特定提示放入后续激活。

明确禁止：

- 指定 Work Item id；
- 把前序 Agent 的结果转述给后续 Agent；
- 复制任务上下文；
- 手工安排 review 或下一步；
- 手工拼装最终结果。

产物：Human action script。任何未列出的 Human 动作都计入 `task-specific Human intervention`。

### Q3：什么使 Work Item 对 Agent eligible？

Human 已确认，直接采用三个过滤条件：

1. AgentInstance 属于当前 CollaborationScope；
2. Work Item 状态是 `available` 或当前 Agent 可处理的 `awaiting_agent_review`；
3. Work Item 所需的最小能力和权限与 Agent 匹配。

首版不建设 Agent 自动能力发现。能力由固定的 Agent profile 或实验配置表达；没有 eligible work 时返回过滤原因。

产物：一条可执行的 eligibility 规则，以及 `no_eligible_work` 的过滤原因分类。

### Q4：claim、执行和 review 如何转移？

Human 已确认，直接采用：

```text
available
  → claimed              atomic claim
  → awaiting_agent_review submit result
  → completed            reviewer accepts
```

异常分支：

```text
claimed → blocked
available → cancelled
awaiting_agent_review → claimed  reviewer requests changes
```

补充约束：

- 一次激活最多成功 claim 一个 Work Item；
- 同时竞争时只有一个 Agent 成功；
- reviewer 必须重新 atomic claim `awaiting_agent_review` 后才能 review；
- 首版不设置 claim TTL；
- Agent 中断由 Human 显式标记 `blocked` 或重新开放，不自动恢复；
- review 请求修改时保留结构化结果和引用，按明确状态转移重新进入执行，不引入自动 retry、抢占或后台恢复。

产物：状态转移表和 C1–C4 黑盒测试夹具。

### Q5：结果发布和 Git provenance 的最低契约是什么？

Human 已确认，直接采用。WorkBuddy 只有在完成以下事项后才能 submit：

- 发布 result summary；
- 发布 next action；
- 引用 commit、文件和测试结果；
- 明确 acceptance 是否满足；
- 若不能完成，发布结构化 blocker，而不是模糊说明；blocker 需要包含阻塞类别、已观察事实、已尝试动作、需要的决策和 next action。

Git references 必须包含 commit SHA、变更文件、测试命令及结果，必要时补充 branch 或 diff 状态。首版不把完整对话、代码副本或大文件写入 shared context。Reviewer 只能依据 shared context 和 canonical Git facts 继续工作。

产物：一个成功结果样例和一个 blocker 样例。

### Q6：什么结果才算“有用”？

Human 已确认，直接采用两层退出证据：

硬条件：

- C1 Publish and discover 通过；
- C2 competing claim 没有重复执行；
- C3 result publication 可被另一 Agent 读取；
- C4 review continuation 不需要 Human 补充上下文；
- 最终 Git artifact 满足 acceptance。

价值条件：

- 任务特定提示、上下文复制、人工派发和结果缝合为 0；
- Human 激活次数固定为 3 次；
- 与方案 A 对比，Human 总介入时间不明显劣化；
- 连续 3 次真实任务实验通过。

Agent 总耗时只作为观察指标，不单独决定产品成败。

产物：方案 A / Feature 1 对照 scorecard，以及预先接受的通过阈值。

## Experience Version 最小契约

首个原型只需要：

- 两个稳定可区分的 AgentInstance；
- 一个 CollaborationScope；
- 一个 shared coordination store；
- `publish`、`discover`、`claim`、`publish_result`、`submit`、`review`；
- Git references；
- 事件导出和 Markdown scorecard。

以下内容不进入首个原型：

- Agent 自动发现、轮询、通知和设备唤醒；
- 生产级认证、细粒度 ACL、HA、灾备和 SLO；
- 通用 Memory、知识库和完整原始对话同步；
- 自动 merge、push、release；
- 完整 Dashboard、团队治理和组织级 RBAC。

## 技术路线进入条件

产品语义确认后，才按以下顺序做技术决策：

1. 用 C1–C4 以及 R5/R6/R8 淘汰不具备闭环的候选；
2. 将能力标记为 `native / adapted / absent / unknown`；
3. 把 Work Item、eligibility、claim、review 和验收协议保留为 ZAgenticOPN 自有责任；
4. 只对 shared store、事件、MCP/CLI/HTTP 接入、checkpoint 或 sandbox 等单位能力评估选择性复用；
5. 若适配层开始复制候选的主体状态机、权限模型或部署平台，决策降级为 C，不判定为直接复用。

## 下一步

Q1–Q6 已完成对齐。本文件已转为 Experience Version Spec；当前只按 roadmap 实现同设备单项目最小纵向切片，后续范围仍由阶段退出证据决定。
