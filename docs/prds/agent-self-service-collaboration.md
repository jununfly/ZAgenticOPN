# Agent 自服务协作 Spec

状态：Active

Current stage：Problem Discovery

产品所有者：ZAgenticOPN

## 阶段声明

```text
Current product hypothesis:
  Human 只负责激活 Agent 和处理例外；Agent 仅凭 shared context
  自行发现、认领、执行和接续工作，可以显著减少 Human 的搬运、派发和缝合。

Current vertical slice:
  Human 要求 Codex 检查 shared context；Codex 发布可执行工作；
  Human 要求 WorkBuddy 检查 shared context；WorkBuddy 自行 claim、执行并提交 Git 结果；
  Human 再要求 Codex 检查 shared context；Codex 自行发现 awaiting-review、验证并完成。

Stage exit evidence:
  候选无关方案完成；另一个开源方案接受同一 conformance comparison；
  Human 明确选择 A/B/C/D，并授权或否决 Experience Version。

Deferred decisions:
  自动发现、自动唤醒、生产级认证与 ACL、HA、灾难恢复、完整 Dashboard、
  离线多主协调、自动 merge/release、团队治理和通用个人知识库。
```

## 问题

当前方案 A 依赖 Human 在多个设备和多个 Agent 对话之间复制上下文、派发任务、安排接续并拼装结果。Human 是隐藏的协调控制面，Agent 无法仅凭共享事实判断“有什么工作、我能否执行、谁正在执行、结果在哪里、下一步是什么”。

ZAgenticLoop 的失败经验表明，在第一条有用路径完成前投入大量防错、运行和扩展设计，会持续扩大工作量，却不能证明产品价值。ZAgenticLoop 已进入 Legacy；ZAgenticOPN 从零开始，不继承其架构或实现。

## Feature 1 目标

第一位用户是一位 Human，使用多台设备上的多个异构 Agent 跨多个项目 co-design 与 co-work。Feature 1 最大化 Agent 自服务协作效率，使 Human 从 context mover、dispatcher、orchestrator 和 stitcher 转为 sweeper 与 maintainer。

Human 仍选择何时激活哪个 Agent，并给出任务无关的指令“检查 shared context”。Feature 1 不包含 Agent 自动发现、后台轮询或设备自动唤醒。

## 最小闭环

```text
Human 激活 Agent A 并要求检查 shared context
→ Agent A 发布可执行工作或结果
→ Human 激活 Agent B 并要求检查 shared context
→ Agent B 自行发现 eligible work 并原子 claim
→ Agent B 执行，发布结果、blocker 或 next action，并引用 canonical Git facts
→ Human 激活 Agent A 或另一 Agent 并要求检查 shared context
→ 该 Agent 自行发现 awaiting-review 或可接续工作并继续
→ 只有例外、冲突和方向决策升级给 Human
```

一次激活最多 claim 一个 Work Item。没有 eligible work 时，Agent 返回 `no eligible work` 和过滤原因，不创建替代工作，也不要求 Human 指定 Work Item。

## 需求

| ID | 需求 | Feature 1 口径 |
| --- | --- | --- |
| R1 | 稳定身份 | `Human → device → agent_instance`；session 是一次运行，不是新主体。 |
| R2 | Agent private context | 保存私有协作摘要、未发布观察和恢复引用；不等于完整对话或知识库。 |
| R3 | shared coordination context | 明确发布、按 Initiative/project 隔离；Git 保存 durable engineering facts。 |
| R4 | 发布 available work | Work Item 可独立 claim，具有 objective、acceptance 和 references。 |
| R5 | 发现 shared frontier | Human 触发后，Agent 查询并选择自己 eligible 的工作；不含自动发现。 |
| R6 | 原子 claim | 同一 Work Item 同时只有一个有效 claimant；并发竞争只能有一个成功。 |
| R7 | 发布结果 | 结果、blocker、next action 和 evidence references 可被另一 Agent读取。 |
| R8 | 跨 Agent 接续 | 另一 Agent 能发现 awaiting-review 或 next work，无需 Human 补充任务上下文。 |
| R9 | 例外升级 | 仅冲突、方向、权限或无法继续的异常需要 Human 决策。 |
| R10 | provenance | shared fact 可追溯到 Agent、事件和 canonical Git reference。 |
| R11 | 多设备 | 同一 shared context 可从多台设备访问；生产级 HA 当前 Deferred。 |
| R12 | 产品健康 | 能判断发现、claim、执行、接续和 Human 介入是否健康。 |

R5、R6 或 R8 任一缺失，都没有实现 Agent 自服务协作闭环。

## 最小共享对象

Experience Version 只要求：

- `objective`；
- `acceptance`；
- `state`；
- `claimant`；
- `result summary`；
- `next action`；
- `references`。

完整任务平台、任意工作流、原始对话同步和大文件存储均不属于该切片。

## Human 与 Agent 责任

Human 可以激活 Agent、提交初始目标、查看 scorecard，并处理方向、权限、冲突和高风险决策。Human 不向被激活 Agent 提供具体 Work Item、前序结果或接续说明。

Agent 负责查询 shared context、判断 eligibility、选择和 claim 一个 Work Item、执行 acceptance、发布可追溯结果，并在无法安全继续时形成结构化升级。

## 验证阶梯

1. 同设备 Codex → WorkBuddy → Codex，单项目。
2. 跨设备双 Agent，单项目。
3. 多设备、多 Agent、多项目。
4. Agent 中断后仅凭 private context 恢复，其他 Agent 不可见该 private context。

每道协作门至少连续通过 3 次可复现实验。除初始目标和“检查 shared context”外，任务特定提示、上下文复制、Work Item 指定和结果缝合均为 0；claim 无重复执行；最终 Git artifact 满足 acceptance。

## 产品健康指标

- `eligible-discovery rate`：存在 eligible work 时正确发现的比例；
- `claim success/conflict`：claim 成功、冲突和重复执行；
- `work completion rate`：claim 后完成、阻塞或放弃；
- `handoff continuation rate`：下一 Agent 仅凭 shared context 接续成功；
- `context defect rate`：因缺少目标、验收、结果、引用或 next action 请求 Human 补充；
- `task-specific Human intervention`：人工补充任务、上下文和结果；
- `activation count/time`：任务无关激活的次数和等待时间。

第一阶段以事件导出和 Markdown scorecard 观察这些指标，不建设实时 Dashboard。

## 方案 A 基线

用可比的真实仓库任务分别运行当前人工方案和实验方案。比较 Human 的任务特定提示、上下文复制、人工派发、结果缝合、异常处理和总介入时间。Agent 总耗时不是单独的成败标准。

## 非目标

- Agent 自动发现、常驻轮询或自动唤醒；
- 通用 Agent Memory 或完整个人知识库；
- 自动跨项目规划；
- 自动 merge、push、release；
- 完整团队治理和组织级 RBAC；
- 生产级安全、HA、备份恢复与运行 SLO；
- 复活或继续开发 ZAgenticLoop。

## 开源选择门

当前对 MineContext、MyContext 和 TencentDB-Agent-Memory 的固定版本审计表明，三者都没有原生形成 R5、R6、R8 闭环，因此当前决策为 D：等待另一个开源方案进入同一 comparison。

新候选先接受 R5、R6、R8 淘汰门，再比较 R1–R12、语义所有权、Experience Version 工作量、运行负担、许可和长期所有权成本。通过后按以下分类决策：

- A：直接采用；
- B：开源主体不变，以可移除薄层扩展；
- C：ZAgenticOPN 主导架构，只选择性复用单位能力；
- D：继续搜索。

完成比较并获得 Human 明确决策前，不创建产品实现或 PoC。
