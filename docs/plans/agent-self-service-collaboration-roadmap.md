<!-- ROADMAP_SECTION_START -->
## ZJ Roadmap

> 数据文件: `agent-self-service-collaboration-roadmap.json` | 最后更新: 2026-08-28 12:05:46

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

### 当前施工：1-2-1-3-3-3. 价值实验二：独立技术文档维护任务

实验二已选定独立技术文档维护任务：更新 skills/research/zj-tech-research-report/references/technical-decision-brief.md，准确记录 KEP-753 steps 7–8 与 technical-c4/v1 Report IR 的字段映射和阶段条件。验收要求新的隔离 Git commit、changed files、文档/技能校验结果和 Codex review；不得复用实验一 Work Item 或 artifact。

**决策：**
- Q: 价值实验二选择哪一个独立技术文档维护任务？ → 维护 ZAgentic 的 skills/research/zj-tech-research-report/references/technical-decision-brief.md，补充 KEP-753 steps 7–8 到 Report IR 的准确映射与生命周期条件：graduationCriteria 是 list，versionSkew 只在 dogfood/release 阶段出现；不修改产品运行时。 (该任务与实验一的 SKILL.md、validator、fixture 和 compiler-backed report 改动文件不同；它将复现的报告说明/契约误读沉淀为 source-owned 技术文档，形成独立可审计 commit 和文档校验结果。)
- Q: 价值实验二 Codex review 是否通过？ → request_changes：目标提交相对实验一基座仅修改指定 technical-decision-brief.md，Standards review 通过；但独立复核发现两个阻断项：文档声称 versionSkew 在 experience-version 等早期阶段的省略由 validator 强制，而当前 gate 只对 dogfood/release 要求该对象，携带 versionSkew 的 experience-version 报告仍会通过；WorkBuddy 声称 runtime alias brief 已同步，但 ~/.codex/skills/zj-research-report/ 与 ~/.workbuddy/skills/zj-research-report/ 仍为旧 34 行副本。退回后需修正文档与实际 legacy alias，同步后重跑验证并发布新结果。 (目标分支 e166484 相对 5a42790 的 diff 仅 1 个 reference 文件、33 行新增；Python 3.12 下 verify_technical_report.py 通过，Python 3.9 环境错误属于既有运行时兼容问题。探针：experience-version 携带 versionSkew 返回 success/counts.versionSkew=true；source/canonical brief 为 67 行，两个实际 legacy alias 仍为 34 行。Work Item 已 request_changes 回 available，实验二保持 in_progress，不启动第四次 activation。)
<!-- ROADMAP_SECTION_END -->
