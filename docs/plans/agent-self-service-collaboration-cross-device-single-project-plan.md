# Plan：跨设备双 Agent 单项目闭环

状态：`deferred`（独立后续 Plan，当前 roadmap 不施工）

来源：原路线图节点 `1-2-2`「跨设备双 Agent 单项目闭环」

## 目的

在同一个 `CollaborationScope` 内，让两个设备上的两个异构
`AgentInstance` 完成一次真实的 publish → discover → atomic claim →
result → review continuation 闭环。Human 仍只负责激活 Agent 和处理例外，
不搬运任务上下文、不指定 Work Item、不安排接续。

本 Plan 只保留“单项目、跨设备”这个变量。它不与多项目路由、自动唤醒或
生产级运行能力绑定，避免一次实验同时改变过多条件。

## 当前边界

- 当前阶段仍以同设备单项目 Experience Version 和个人重度使用为焦点。
- 本 Plan 不属于当前路线图施工；不得因为文件已创建就开始实现或提前晋级。
- 重新进入前，Human 需要明确授权，并先确认同设备版本在个人日常使用中已有
  可复核的稳定基线。
- 重新进入时仍以现有 Spec、C1–C4、Git provenance 和产品健康指标为契约，
  不重新发明 Work Item、claim 或 review 语义。

## 重入条件

满足以下条件后，才把本 Plan 重新纳入执行路线：

1. Human 明确决定开始跨设备验证，并冻结实验目标、两个设备及两个 Agent
   runtime 的身份。
2. 同设备个人使用基线已经记录主要成功率、失败类型、Human 介入和恢复成本。
3. 明确跨设备 shared context 的托管位置、访问边界、备份/清理责任和测试数据
   处置方式；不以临时复制数据库作为产品语义。
4. 为网络不可用、重复提交、设备离线和错误 `CollaborationScope` 预先定义
   可观察的失败结果与停止条件。

## 计划工作包

### 1. 跨设备共享事实

- 让两个设备读写同一个项目 scope 的结构化 shared context。
- 保留 Agent、device、activation、事件序列和 canonical Git reference 的
  provenance。
- 验证另一设备不需要原始对话或人工复制就能理解 objective、acceptance、
  result summary 和 next action。

### 2. 跨设备 claim 与接续

- 在两个设备同时竞争同一个 Work Item 时，验证只有一个 claim 成功，且没有
  重复执行。
- 验证执行设备发布结果后，review 设备可以仅凭 shared context 和 Git facts
  接续 review。
- 验证 review `request_changes` 后，后续 activation 可以按既有状态机重新
  接续，而不遗留不可见的旧 claim。

### 3. 失败与恢复边界

- 记录网络不可用、共享事实暂时不可读、设备离线和 handoff delivery failure。
- 只实现当前实验确实需要的最小人工异常处理；不加入后台 retry、claim TTL、
  自动恢复、自动唤醒或跨 scope 搜索。
- 明确哪些事件由共享存储保证、哪些只代表设备本地观察，避免把本地日志冒充
  全局事实。

### 4. 独立实验与收口

- 使用同一 acceptance 的真实仓库任务，建立与同设备基线可比较的操作日志。
- 沿用“独立端到端实验”为重复单位；不把每道协作门机械拆成重复执行，但每次
  必须明确记录 C1–C4 覆盖，C2 必须实际存在竞争窗口。
- 输出事件导出、Markdown scorecard、Git artifact、失败分类和 Human 介入时间。

## 完成标准

- C1：跨设备 Agent 能发现当前 scope 的 eligible Work Item。
- C2：并发 claim 只有一个成功者，无重复执行，并且冲突可复核。
- C3：结果字段、acceptance status、next action 和 Git references 可被另一
  设备的 Agent 读取。
- C4：review Agent 无需 Human 补充任务上下文即可完成或结构化退回。
- 最终 Git artifact 满足任务 acceptance，事件可关联到正确的 Agent、device、
  activation 和 scope。
- 结果同时报告跨设备增加的 Human 操作、失败和等待成本；不以 Agent 总耗时单独
  判定价值。

## 明确不做

自动发现、轮询、通知、设备唤醒、生产级认证与 ACL、HA、灾难恢复、实时
Dashboard、自动 merge/release、跨项目规划，以及 ZAgenticLoop 代码复用，均不
因本 Plan 进入范围。

## 证据产物

重入后至少保存：固定输入与版本、两个设备/Agent 的身份映射、事件导出、失败
分类、Human action log、对照 scorecard、最终 Git commit 和验证命令结果。所有
结论区分“跨设备路径通过”与“产品价值已被证明”。

