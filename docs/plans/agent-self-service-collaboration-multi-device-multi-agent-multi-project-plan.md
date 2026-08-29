# Plan：多设备多 Agent 多项目闭环

状态：`deferred`（独立后续 Plan，当前 roadmap 不施工）

来源：原路线图节点 `1-2-3`「多设备多 Agent 多项目闭环」

## 目的

在多个设备、多个异构 Agent 和至少两个相互隔离的项目之间，验证 Agent 能
根据明确的 `CollaborationScope` 发现自己 eligible 的 Work Item，并完成
跨项目但不串 scope 的协作。Human 只触发任务无关 activation，不能通过手工
选择项目、搬运上下文或缝合结果替系统完成路由。

这是跨设备单项目之后的扩展验证，不是当前同设备个人使用版本的默认架构目标。

## 当前边界

- 当前不执行本 Plan，也不在当前 roadmap 中继续保留该施工节点。
- 当前优先把同设备多 Agent 场景做成可供产品 owner 日常重度使用的版本。
- 本 Plan 重新进入前，必须先有跨设备单项目的稳定证据；不能直接用多项目
  实验掩盖单项目跨设备的基础问题。
- 生产级多租户治理、通用组织权限和自动化运维仍须另行决策，不由本 Plan 默认为
  已授权。

## 重入条件

1. Human 明确授权多设备、多 Agent、多项目实验，并冻结参与的项目 scope、
   Agent profile 和设备身份。
2. 跨设备双 Agent 单项目 Plan 已完成，至少有可复核的 claim、接续、失败和
   Human 介入基线。
3. 明确项目隔离的可观察契约：默认 activation 只能查询一个明确 scope；需要
   导航多个项目时必须有显式 Human 意图和可审计的 scope 选择。
4. 准备相互独立的真实任务和 Git 分支，避免一个项目的结果成为另一个项目的
   隐式上下文或验收依据。

## 计划工作包

### 1. Scope 隔离与 Agent eligibility

- 验证不同项目的 Work Item、事件、claim 和 Git references 不会串读或串写。
- 验证每个 Agent 的 capability/permission profile 只命中它当前 scope 中可
  执行的 Work Item。
- 对无 eligible work、scope 不匹配和权限不足分别保留结构化过滤原因；不得
  通过模糊匹配、默认项目或从 Work Item 反推 scope 来“修好”路由。

### 2. 多 Agent 并发与接续

- 在同一项目和不同项目同时有工作时，验证每次 activation 最多 claim 一个
  Work Item，且不会跨项目重复执行。
- 验证不同 Agent 可以分别完成执行和 review，结果 provenance 始终指向正确的
  项目、commit 和事件链。
- 验证一个项目阻塞或 review request changes 不会改变另一个项目的状态。

### 3. 多设备运行边界

- 记录设备离线、网络延迟、重复 activation、共享事实读取失败和 handoff 失败。
- 仅实现被真实实验阻断的最小处理；不把 HA、灾难恢复、后台调度、自动唤醒、
  自动 retry 或生产 SLO 带入当前 Plan。
- 说明本地日志、共享事件和 Git facts 的证据优先级，保证 scorecard 可复核。

### 4. 真实使用对照与收口

- 为至少两个项目准备互不污染的真实任务，沿用同设备个人使用中的 Human
  intervention、activation、完成率、接续率和 context defect 统计口径。
- 以独立端到端实验作为重复单位，明确 C1–C4 和项目隔离覆盖；不把多项目的
  工作数量误当成产品价值。
- 与此前同设备/跨设备基线比较新增的人力、等待、错误路由和恢复成本，并保留
  “可工作但不值得扩展”的结论出口。

## 完成标准

- 多个 Agent 在多个设备上能在正确 scope 内发现、claim、执行和 review。
- 任一项目的 claim、结果、blocker、review 和 Git provenance 不泄漏到其他项目。
- 并发 claim、scope 冲突、无 eligible work、设备离线和 handoff failure 均有
  可观察结果与可复核事件。
- 真实任务的最终 Git artifacts 满足各自 acceptance，Human 不承担任务特定的
  派发、上下文复制和结果缝合。
- 报告跨项目带来的额外复杂度和 Human 成本；只有证据支持时才建议继续扩展。

## 明确不做

自动项目发现、全局后台轮询、组织级 RBAC、生产级认证/审计、HA、备份恢复、
自动 merge/release、完整 Dashboard、通用 Agent Memory，以及 ZAgenticLoop
复活或代码抽取，均不因本 Plan 进入范围。

## 证据产物

重入后至少保存：参与项目和 Agent/device 映射、固定版本与输入、按 scope 分组的
事件导出、隔离性负向证据、失败分类、Human action log、对照 scorecard、各项目
Git commit 和验证命令结果。结论必须区分“多项目路由正确”与“扩展确实带来价值”。

