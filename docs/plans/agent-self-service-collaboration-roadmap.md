<!-- ROADMAP_SECTION_START -->
## ZJ Roadmap

> 数据文件: `agent-self-service-collaboration-roadmap.json` | 最后更新: 2026-08-28 18:03:29

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

### 当前施工：1-2-1-3-3-4. 价值实验三：独立技术文档维护任务

已选择独立维护 technical-proposal-exemplar.md：补充 KEP-753 11 步决策链到 Problem discovery、Experience Version、Usefulness validation、Dogfood/release 四阶段的最小证据检查项；限定为文档及必要镜像同步，不改 SKILL.md、validator、Report IR 或产品运行时。下一步由 Codex 创建新的独立 Work Item，WorkBuddy 通过任务无关 activation 执行，随后 Codex review。

**决策：**
- Q: 价值实验三选择哪一个独立技术文档维护任务？ → 维护 ZAgentic 的 skills/research/zj-tech-research-report/references/technical-proposal-exemplar.md：将 KEP-753 的 11 步决策链与 Problem discovery、Experience Version、Usefulness validation、Dogfood/release 四阶段的最小证据整理为可执行检查项，同时保留 decision chain、候选语义和 ownership/risk 边界；不修改 SKILL.md、validator、Report IR 或产品运行时，不复用实验二 technical-decision-brief。 (stage-critical；验收以该 exemplar 的独立 Git artifact、必要 runtime 镜像同步、文档一致性检查和可复核 commit/files/tests 为准；使用独立 Work Item 与独立事件窗口。)
<!-- ROADMAP_SECTION_END -->
