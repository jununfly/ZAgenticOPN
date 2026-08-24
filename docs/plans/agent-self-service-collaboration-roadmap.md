<!-- ROADMAP_SECTION_START -->
## ZJ Roadmap

> 数据文件: `agent-self-service-collaboration-roadmap.json` | 最后更新: 2026-08-24 21:40:37

[~][X+] 1. ZAgenticOPN Agent 自服务协作
├── [x][Y+] 1-1. 阶段 0：问题发现与候选方案选择
│   ├── [x][Y+] 1-1-1. 形成目标、需求与产品假设基线
│   ├── [x][Y+] 1-1-2. 完成候选无关 Spec 与技术设计
│   ├── [x][X+] 1-1-3. 对比新开源方案与当前候选基线
│   ├── [x][X+] 1-1-4. Human 确认 A/B/C/D 技术决策
│   ├── [x][Y+] 1-1-5. Feature 1 对齐契约：冻结 Q1–Q6
│   ├── [x][Y+] 1-1-6. 将 Feature 1 对齐草案转为 Experience Version Spec
│   ├── [x][X+] 1-1-7. 下一轮最多 3 个 ext 候选筛选与 C1–C4 黑盒复验
│   └── [x][Y+] 1-1-8. C 路线选择性复用能力地图与实施准入
├── [~][Y+] 1-2. 阶段 1：Agent 自服务协作体验版
│   ├── [~][Y+] 1-2-1. 同设备 Codex → WorkBuddy → Codex 闭环
│   ├── [ ][X+] 1-2-2. 跨设备双 Agent 单项目闭环
│   ├── [ ][X+] 1-2-3. 多设备多 Agent 多项目闭环
│   └── [ ][X+] 1-2-4. Agent private context 中断恢复
├── [ ][X+] 1-3. 阶段 2：协作价值重复验证
│   ├── [ ][X+] 1-3-1. 运行人工方案 A 对照实验
│   ├── [ ][X+] 1-3-2. 每道协作门连续通过 3 次
│   └── [ ][X+] 1-3-3. 基于产品健康指标判定有用性
└── [ ][X+] 1-4. Deferred：后续生命周期能力
    ├── [ ][X+] 1-4-1. 评估自动发现、通知与设备唤醒
    ├── [ ][X+] 1-4-2. 按真实失败建设生产可靠性
    └── [ ][X+] 1-4-3. 个人闭环有效后评估团队治理

### 当前施工：1-2-1-3-2. WorkBuddy task-agnostic activation routing failure follow-up

真实 WorkBuddy routing 已完成 no_eligible_work discover、C1 discover→claim execution，并通过真实产物型 Work Item 完成 C4：R1 commit 023ead9 首审 request_changes（缺少本 work discover），R2 由 scripts/activate_agent.py 无 Work Item ID 产生 activation-ee2fbd368a8f 的 discover→claim_succeeded，追加 commit 89d6043，publish-result 携带真实 commit/files/tests；Codex 二次 claim-review 独立复跑 9/9 tests 后 accept，Work Item c4-workbuddy-result-artifact-20260824 已 completed。上一条 routing-only Work Item 仍按 creator 裁决 blocked。节点继续 in_progress：C2 competing real activation、三次真实价值实验及后续 C-route closeout 尚未完成。

**决策：**
- Q: AgentRQ adapter验证完成后真实 smoke 的当前焦点是什么？ → 继续处理已观察到的 WorkBuddy activation routing failure：让任务无关的检查 shared context 激活真正进入 ZAgenticOPN coordination seam；AgentRQ adapter 结果只作为可选 transport，不替代 WorkBuddy 接线验证。 (本轮不展开该 follow-up；WorkBuddy 仍未产生 discover/claim 事件，属于 observed-failure。)
- Q: WorkBuddy activation routing 如何最小修复？ → 增加一个显式的 task-agnostic activation entrypoint：Agent 只提供自己的稳定 profile、scope 和 activation session，不提供 Work Item id；entrypoint 调用 discover，并在有 frontier 时只 claim 一个 execution 或 review Work Item，返回结构化 handoff。 (这是 activation adapter seam，不是自动发现/后台轮询；ZAgenticOPN 继续拥有 eligibility、claim、review 和 scope。通过项目内脚本与 AGENTS.md 记录 WorkBuddy 应进入该 seam，避免把 ZInitiatives 导航 context 当作产品 shared context。)
- Q: activation routing 最小修复的黑盒结果是什么？ → 项目内 activation entrypoint 已通过：WorkBuddy 无 Work Item id 的外部子进程激活能 discover 并 claim execution；Codex 无 Work Item id 激活能 discover 并 claim awaiting_agent_review；run_same_device_smoke 已改为实际调用该入口并完成到 completed。 (9/9 tests 通过。该证据只证明 project-local activation seam 和同设备可复现 smoke；真实 WorkBuddy UI/runtime 尚未由 Human 重放，也未计入三次真实价值实验。)
- Q: 真实 WorkBuddy UI/runtime 重放结果是什么？ → 未通过：WorkBuddy v5.3.14 已切到本地 ZAgenticOPN 文件夹并进入新建任务，但发送固定的检查 shared context 请求未产生消息或运行；项目 shared store 目标 scope 没有 discover/claim 事件。 (分类：observed-failure。可见请求可填入，但无障碍点击、坐标点击、Return/Cmd+Return/Ctrl+Return 均未提交；点击 Agent 应用快捷场景还触发 removeChild UI 错误。证据 research/activation-routing/2026-08-24-workbuddy-runtime-replay.md。)
- Q: WorkBuddy CLI 激活返回 no_eligible_work 说明什么？ → 部分通过：真实 WorkBuddy 已执行项目内 activation seam，并在目标 scope 产生 discover 事件；但该 scope 当时没有可声明 Work Item，因此没有 claim，C1 execution claim 仍未通过。 (已由 .workbuddy/memory/2026-08-24.md 与 .zagenticopn/shared.sqlite3 独立核对：activation-a40f6da3210b、eligible_count=0、无目标 scope Work Item。下一步由 Codex 发布一个同 scope 的窄任务，再由 Human 触发一次检查 shared context；证据 research/activation-routing/2026-08-24-workbuddy-cli-replay.md。)
- Q: WorkBuddy 二轮 claim 后 block 的 creator 裁决是什么？ → 保留 Git provenance 硬约束：不放行空 references，不使用伪造 N/A commit；将本 Work Item 的 block 作为 C1 路由通过但 acceptance 不具备可交付结果证据的观察记录。未来执行任务必须带真实 commit/files/tests，若要支持纯证据任务需另行做显式产品契约决策。 (真实事件已核对：discover eligible_count=1 → claim_succeeded execution → block，Work Item revision=2/state=blocked；WorkBuddy 未编造 commit。证据 research/activation-routing/2026-08-24-workbuddy-claim-block.md。)
- Q: C4 如何在不放宽 Git provenance 的前提下继续？ → 发布一个真实产物型 Work Item：WorkBuddy 通过任务无关 activation claim 后，新增一份 C4 结果文档，运行现有测试，提交真实 Git commit，并以真实 commit/files/tests 引用 publish-result + submit；随后 Codex 任务无关 review activation claim-review 并验收。 (这是对上一轮契约冲突的修正：不使用空 references 或 N/A commit，不修改 coordination.py 或路线图 JSON；Work Item acceptance 显式要求可审计 Git artifact。)
- Q: C4 首次 Codex review 应如何裁决？ → request_changes：commit 023ead9 与 9/9 测试证据有效，但当前结果文件与事件账本显示本 Work Item 走了显式 claim、没有对应 discover 事件，未满足 acceptance 的每轮 task-agnostic activation。要求 WorkBuddy 重新执行 scripts/activate_agent.py 无 Work Item ID discover→claim，修正结果文档并以新真实 commit/files/tests 重新 publish-result + submit。 (独立证据：该 Work Item 只有 claim_succeeded(activation-workbuddy-3)、publish_result、submit，没有同 Work Item 前的 discover；结果文件第 3 步自述显式 claim。先 request_changes，不能 accept 不完整的 C4。)
- Q: C4 二次 Codex review 的裁决是什么？ → accept：R2 已按 request_changes 严格使用 scripts/activate_agent.py 无 Work Item ID，activation-ee2fbd368a8f 下同一 Work Item 产生 discover→claim_succeeded；R2 commit 89d6043 只追加结果文件，publish-result 携带真实 commit/files/tests，测试 9/9 通过。 (独立核验通过：events row 15 discover 与 row 16 claim_succeeded 紧邻；git show 89d6043 --stat 为 1 file/36 insertions，R1 commit 023ead9 字节未变；本地复跑 python -m unittest discover -s tests -v 为 9/9。可执行 review claim 后 accept。)
<!-- ROADMAP_SECTION_END -->
