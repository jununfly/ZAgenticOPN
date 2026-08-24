<!-- ROADMAP_SECTION_START -->
## ZJ Roadmap

> 数据文件: `agent-self-service-collaboration-roadmap.json` | 最后更新: 2026-08-24 22:22:02

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

### 当前施工：1-2-1-3-3-1-1. Human 显式 reopen 与真实 Agent scope 接续修复

**决策：**
- Q: 这次 observed-failure 的最小修复是什么？ → 增加 Human 显式 reopen seam：在明确 operator、scope、Work Item 和 reason 后，将陈旧 claimed 或已阻塞 Work Item 安全回到 available，停用旧 execution claim 并记录 human_reopened 事件；同时明确 Agent 必须在 Work Item 所属项目 scope 中运行 activation，不能把默认 zagenticopn/experience-version 的 no_eligible_work 当作跨项目任务接续。 (不提供自动恢复、claim TTL、后台轮询、跨 scope 自动搜索或重试；修复服务当前已复现的陈旧 claim 与错误 scope 接线，三次价值实验继续暂停。)
- Q: 修复完成的验收证据是什么？ → 黑盒测试证明 Human reopen 不会伪造结果、清理 active claim、保留 operator/reason 事件且不能重开 completed/awaiting-review；真实 DB 对当前 work-zj-research-report-improvement-20260820 只在修复后执行一次显式 reopen，再由正确项目 scope 的真实 Agent 重新竞争并继续。 (在真实 Agent 重新接续前，不把 C2 或价值实验记为通过；旧 C4 scope 的 no_eligible_work 继续作为无关历史探活记录。)
- Q: 当前修复已完成到什么程度？ → 最小 Human reopen seam 已实现并通过 11/11 黑盒测试；真实陈旧 Work Item 已执行一次显式 reopen，revision=2、state=available、claimant 为空、旧 execution claim inactive，events sequence 28 记录 operator/reason/previous_claimant。 (真实 Agent 仍需在 Work Item 所属的 junjunfly/ZAgentic/zj-research-report scope 重新激活并直接接续执行；在此之前，三次价值实验保持暂停，不能把 C2 记为完整真实实验通过。)
- Q: ZAgentic WorkBuddy activation routing 修复结果是什么？ → 根因是 ZAgentic/AGENTS.md 未指向 ZAgenticOPN activation seam，WorkBuddy 因此只输出仓库摘要；已在 commit f04f856 增加当前 owning scope、sibling entrypoint、无 Work Item id 和 claimed 后同 activation 执行规则。隔离 SQLite 项目级 smoke 已通过，事件为 publish→discover→claim_succeeded。 (真实 WorkBuddy UI/runtime 仍需在 ZAgentic 项目重放并核对 shared.sqlite3 新 activation 事件；若仍只输出摘要，继续记为 observed-failure。三次价值实验保持暂停。)
<!-- ROADMAP_SECTION_END -->
