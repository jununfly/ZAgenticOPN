# Agent 自服务协作 Experience Version Spec

状态：Implementation authorized — Experience Version

上位 Spec：[Agent 自服务协作](agent-self-service-collaboration.md)

来源：[Feature 1 Experience Version 对齐契约](../designs/agent-self-service-collaboration-experience-version-alignment.md)

生命周期分类：`stage-critical`。本 Spec 冻结首个 Experience Version 的产品语义和外部验收；开源 comparison gate 已完成，Human 已授权实现同设备单项目最小纵向切片。产品 owner 的 owner-only 用户侧正式发布路径属于当前纵向切片的交付准备；公开部署、多用户发布和生产级运行能力仍不在本阶段范围内。

## Problem Statement

方案 A 依赖 Human 在多个设备和多个 Agent 对话之间搬运上下文、派发任务、安排接续和缝合结果。Human 充当隐藏的协调控制面；Agent 不能仅凭共享事实判断有什么工作、自己是否 eligible、谁拥有执行权、结果在哪里以及下一步是什么。

第一位用户是一位在多台设备上使用多个异构 Agent，跨多个项目进行 co-design 与 co-work 的 Human。Feature 1 的产品假设是：Human 只负责激活 Agent 和处理例外，Agent 仅凭 shared coordination context 自行发现、认领、执行和接续工作，可以显著减少 Human 的搬运、派发、编排和缝合。

首个真实任务是：找一份优秀的技术方案分析报告，改进 `zj-research-report` skill 的效果。该任务用固定 commit 的 Kubernetes KEP-753 作为技术方案标杆，要求真实修改、测试和可追溯 Git artifact，不是演示性对话。

## Solution

提供一个窄职责的 collaboration control plane，通过一个 Agent integration / coordination protocol seam，为 Codex、WorkBuddy 及其他异构 Agent 提供以下领域操作：发布 available Work Item、发现 eligible frontier、原子 claim、发布结果、提交 review 和完成接续。

Human 仍然选择何时激活哪个 Agent，但每次只说“检查 shared context”。Agent 根据固定的 CollaborationScope、Work Item 状态和 Agent profile/权限匹配判断 eligibility；不存在 eligible work 时返回 `no eligible work` 及过滤原因，不要求 Human 指定任务。

Experience Version 只保留 private collaboration context、shared coordination context 和 canonical Git facts 的最小关系。shared context 保存结构化工作事实和引用，不复制完整对话、代码副本或大文件；Git 保存 durable engineering facts。

首条路径是同设备 Codex → WorkBuddy → Codex、单项目、隔离实验分支。Codex 发布工作，WorkBuddy 发现并 claim 后修改、测试和提交 Git 结果，Codex 仅凭 shared context 与 Git references 发现并完成 review。

## User Stories

1. As a Human, I want to submit one initial objective, so that the collaboration starts without repeatedly explaining the task.
2. As a Human, I want to activate an Agent with only “检查 shared context”, so that the prompt does not hide manual orchestration.
3. As a Human, I want to activate Codex, WorkBuddy and Codex in sequence, so that one real task can traverse publish, execution and review.
4. As a Human, I want to avoid naming a Work Item to the next Agent, so that the Agent proves it can discover the shared frontier itself.
5. As a Human, I want to avoid copying previous Agent output into the next conversation, so that context transport is measured rather than assumed away.
6. As a Human, I want to avoid manually arranging review or the next step, so that review continuation is an Agent capability.
7. As a Human, I want to avoid manually stitching the final result, so that Git and shared facts remain the durable result sources.
8. As an Agent, I want a stable AgentInstance identity scoped to a device and runtime, so that claims and events are attributable to the correct participant.
9. As an Agent, I want to query one CollaborationScope, so that unrelated project work does not enter my default frontier.
10. As an Agent, I want to discover only Work Items whose state and required profile/permissions match me, so that I do not claim work I cannot execute.
11. As an Agent, I want `no eligible work` to include filter reasons, so that an empty frontier is observable and does not trigger invented work.
12. As an Agent, I want to claim at most one Work Item per activation, so that one activation has a bounded and auditable execution scope.
13. As an Agent, I want claim to be atomic, so that concurrent Agents cannot both execute the same Work Item.
14. As an Agent, I want to publish an objective and acceptance before execution, so that another Agent can understand the work without receiving the original conversation.
15. As an Agent, I want to publish a result summary, acceptance status, next action and references, so that another Agent can continue from durable facts.
16. As an Agent, I want to publish a structured blocker when acceptance cannot be met, so that a Human can decide from observed facts instead of a vague failure message.
17. As a reviewer Agent, I want to atomically claim `awaiting_agent_review`, so that only one reviewer owns the review at a time.
18. As a reviewer Agent, I want to accept or return a result using shared facts and canonical Git references, so that review does not require Human context transfer.
19. As a Human, I want to handle permission, conflict, direction and inability-to-continue exceptions, so that the system escalates only decisions that require Human judgment.
20. As a Human, I want an interrupted Work Item to be explicitly blocked or reopened by me, so that the Experience Version does not hide retry, lease or recovery semantics behind automation.
21. As a Human, I want shared context to contain only structured facts and references, so that private observations and sensitive or large artifacts are not unintentionally shared.
22. As a Human, I want each result to reference a commit, changed files and test outcomes, so that a reviewer can verify the result in Git.
23. As a Human, I want a Markdown scorecard of events and outcomes, so that I can sweep and maintain collaboration health without a real-time dashboard.
24. As a Human, I want to compare the Experience Version with the manual方案 A, so that reduced intervention is measured rather than inferred.
25. As a Human, I want the first task to pass three consecutive real experiments, so that one lucky handoff is not mistaken for product value.
26. As a maintainer, I want C1–C4 and the final Git artifact to be hard gates, so that a superficially useful report cannot hide a broken collaboration loop.
27. As a maintainer, I want R5, R6 and R8 to remain open-source selection gates, so that a candidate cannot redefine the product semantics before comparison.
28. As a maintainer, I want automatic discovery, wake-up, HA, RBAC and dashboard work to remain deferred, so that the first useful path does not accumulate unobserved platform scope.

## Implementation Decisions

### Product boundary and seam

- The primary integration seam is the Agent integration / coordination protocol boundary. Agent runtimes call domain operations through this seam; the coordination service and store remain behind it.
- The protocol expresses `discover`, `inspect`, `publish`, `claim`, `publish_result`, `block`, `submit`, `claim_review` and `review` semantics. The first implementation may project these operations through MCP, CLI or HTTP, but the projection must not change the product semantics.
- ZAgenticOPN owns Work Item, eligibility, Claim, review, acceptance and lifecycle semantics. A candidate supplies infrastructure or a unit capability only after the comparison gate proves the composition feasible.

### Human action script

- Human submits one initial objective.
- Human performs exactly three task-agnostic activations: Codex → WorkBuddy → Codex.
- Each activation uses “检查 shared context”.
- Human handles only permission, conflict, direction and inability-to-continue exceptions.
- Human does not name a Work Item, repeat prior results, copy context, schedule review, or stitch results.

### Identity and scope

- An AgentInstance is stable across sessions and is distinguished through its device and Agent runtime identity.
- A CollaborationScope isolates one Initiative/project collaboration context for the first experiment.
- A session is a run of an AgentInstance, not a new collaboration principal.

### Eligibility and discovery

- An eligible Work Item must belong to the current CollaborationScope.
- Its state must be `available` or `awaiting_agent_review` when the Agent is eligible to review it.
- Its required minimum capability and permissions must match the Agent profile.
- Capability discovery is not automatic in this Experience Version; fixed Agent profiles or experiment configuration express eligibility.
- An empty frontier returns `no eligible work` with filter reasons and never invents or requests a Human-selected Work Item.

### Work Item state and claim

- The normal state path is `available → claimed → awaiting_agent_review → completed`.
- A blocked execution enters `blocked`; a Human may explicitly reopen it to `available`.
- A Human may cancel an available or claimed Work Item as an exception decision.
- One activation can successfully claim at most one Work Item.
- Claim is atomic. Concurrent claim attempts produce exactly one winner and explicit conflicts for the other Agents.
- A reviewer must atomically claim `awaiting_agent_review` before reviewing it.
- The Experience Version has no claim TTL, automatic retry, preemption or background recovery.

### Result publication and provenance

- Submit requires `result_summary`, `next_action`, `acceptance_status` and `references`.
- A blocked or incomplete result requires a structured blocker with category, observed facts, attempted actions, required decision and next action.
- Git references include commit SHA, changed files, test commands and outcomes; branch or diff status may supplement the reference when needed.
- Shared context stores structured facts and canonical references only. It does not store complete conversations, code copies or large files.
- A reviewer continues from shared context and canonical Git facts without Human context supplementation.

### Observability and exit evidence

- Every experiment exports observable publish, discover, claim, conflict, block, submit, review and complete events with AgentInstance and CollaborationScope attribution.
- The first scorecard is Markdown; a metrics backend and real-time dashboard are deferred.
- Hard exit gates are C1 Publish and discover, C2 competing claim without duplicate execution, C3 readable result publication, C4 review continuation without Human context supplementation, and a final Git artifact satisfying acceptance.
- Value evidence requires zero task-specific prompts, context copies, manual dispatch and result stitching; exactly three activations; Human intervention time not materially worse than方案 A; and three consecutive real task experiments.
- Agent total runtime is an observation metric, not a standalone product success gate.

### Lifecycle and adoption

- This Spec freezes the Experience Version contract. The comparison gate is complete and Human has authorized implementation of the narrow local vertical slice. The product owner may receive that slice through an owner-only user-side release artifact; public deployment, multi-user support and production-grade operation remain deferred.
- The owner-only release must install a versioned runtime and matching host integration outside consuming project worktrees. A consuming project supplies only its task workspace and Git artifact; it must not import ZAgenticOPN source or provide the product runtime through `PYTHONPATH`.
- Candidate comparison uses fixed revisions and primary evidence, marks capabilities `native`, `adapted`, `absent` or `unknown`, and keeps product semantics separate from unit-capability reuse.
- The next technical activity is the minimum coordination seam and its C1–C4 black-box fixtures. The implementation must keep C5–C8, automatic discovery, recovery and production operations outside the first slice unless new evidence changes the stage decision.

## Testing Decisions

- Tests observe external behavior at the Agent integration / coordination protocol seam. They do not assert database tables, internal classes, prompt wording beyond the fixed activation, or implementation-specific call order.
- C1 Publish and discover verifies that WorkBuddy discovers Codex's available Work Item from a task-agnostic activation.
- C2 Competing claim runs concurrent claim attempts and verifies one winner, one claimant and no duplicate execution.
- C3 Result publication verifies that summary, acceptance status, next action and Git references become readable to another Agent.
- C4 Agent review continuation verifies that Codex discovers and atomically claims review work, verifies the referenced Git artifact and completes without Human context supplementation.
- C5 No eligible work verifies filter reasons and the absence of invented work or Human task selection.
- C6 Context defect verifies that missing acceptance or references produces a classified defect rather than a false success.
- C7 Scope isolation verifies that a default query cannot mix another project’s Work Items while explicit global navigation remains distinguishable.
- C8 Private recovery remains a deferred-stage scenario until the Experience Version proves the first four scenarios; when enabled, private recovery must be visible only to the owning AgentInstance.
- The first fixture uses the real `zj-research-report` improvement task on an isolated branch and requires a commit, changed-file references and test results.
- The manual方案 A comparison records Human task-specific prompts, context copies, dispatch, result stitching, exception handling and total intervention time using the same acceptance criteria.
- Each collaboration gate runs three consecutive reproducible experiments. A hard-gate failure blocks the run; value evidence determines continue, revise or stop.
- Prior art for these tests is the candidate-neutral C1–C8 conformance matrix, the Markdown scorecard projection and the existing `AgentInstance`, `CollaborationScope`, `WorkItem`, `Claim`, `CoordinationEvent` and `EvidenceReference` vocabulary in the technical design.

## Out of Scope

- Public deployment, multi-user release, external support or production operation of the product runtime.
- Agent automatic discovery, polling, notifications, device wake-up or background execution.
- Generic Agent Memory, a personal knowledge base, full conversation synchronization or large-file storage in shared context.
- Automatic planning across projects, automatic merge, push, release, retry, preemption, claim TTL or crash recovery.
- Production authentication, credential management, fine-grained ACL, HA, backup, disaster recovery, SLOs and organization-level RBAC.
- Real-time dashboards, a metrics backend and team governance.
- Reuse of ZAgenticLoop code or continuation of the ZAgenticLoop legacy product.

## Further Notes

- This Spec is the normalized result of the accepted Q1–Q6 alignment decisions. The alignment document remains the decision record; this Spec is the executable product input for comparison and later prototype planning.
- The first task is intentionally a real cross-repository skill/document maintenance task. Its acceptance is the improved skill source, validated technical report projection and canonical Git artifact, not a new ZAgenticOPN runtime.
-方案 A remains the baseline. A reduction in Human context transport and stitching is the primary value hypothesis; Agent latency is secondary.
- The current lifecycle stage is Experience Version. C-route comparison is complete and implementation is authorized for the same-device, single-project slice only. The delivery form for the product owner is a user-side formal release; this does not authorize cross-device, multi-project or public deployment.
