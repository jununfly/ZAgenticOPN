<!-- ROADMAP_SECTION_START -->
## ZJ Roadmap

> 数据文件: `agent-self-service-collaboration-roadmap.json` | 最后更新: 2026-08-28 23:38:46

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
│   ├── [x][Y+] 1-2-1. 同设备 Codex → WorkBuddy → Codex 闭环
│   ├── [ ][X+] 1-2-2. 跨设备双 Agent 单项目闭环
│   ├── [ ][X+] 1-2-3. 多设备多 Agent 多项目闭环
│   └── [ ][X+] 1-2-4. Agent private context 中断恢复
├── [ ][X+] 1-3. 阶段 2：协作价值重复验证
│   ├── [~][X+] 1-3-1. 运行人工方案 A 对照实验
│   ├── [ ][X+] 1-3-2. 每道协作门连续通过 3 次
│   └── [ ][X+] 1-3-3. 基于产品健康指标判定有用性
└── [ ][X+] 1-4. Deferred：后续生命周期能力
    ├── [ ][X+] 1-4-1. 评估自动发现、通知与设备唤醒
    ├── [ ][X+] 1-4-2. 按真实失败建设生产可靠性
    └── [ ][X+] 1-4-3. 个人闭环有效后评估团队治理

### 当前施工：1-3-1. 运行人工方案 A 对照实验

部分完成（2026-08-28）：已用同一份真实 Report IR 在隔离目录投影为 zj-draft/v1，并通过 publish_report.py 生成 OPN 内 baseline Markdown/HTML/receipt；reportHash=64b61f0eef37682371b0dd5d7d32ec67975dfc2ff7220afe9c4f1dad909ad1bb，receipt healthy=true。已记录 baseline record、A/Experience Version comparison scorecard 与未执行的 Human action log 模板。真实 Human 手动搬运 objective/acceptance/前序结果、派发 WorkBuddy、安排 Codex review、结果 stitching、时间戳、同 acceptance Git artifact 尚未执行或未记录；节点保持 in_progress。证据：research/activation-routing/2026-08-28-solution-a-baseline-record.md、2026-08-28-solution-a-comparison-scorecard.md、2026-08-28-solution-a-human-action-log.md。

**决策：**
- Q: 方案 A 对照实验的对象和记录边界是什么？ → 使用与 Experience Version 相同的真实技术方案任务与 acceptance，优先采用同一份 KEP-753-backed technical Report IR，运行不依赖 shared context 的人工路径：Human 手动搬运 objective/acceptance/前序结果，派发 WorkBuddy，安排 Codex review，并拼装最终结果。逐次记录 Human action 时间戳与数量、任务特定 prompt、上下文复制、人工 dispatch、review 安排、结果 stitching、异常处理和总介入时间；另行记录 Git artifact 与 Agent runtime，不把 Agent 总耗时混入 Human intervention。 (分类：stage-critical。该 baseline 直接补当前 Experience Version 退出判断缺失的对照证据；产物为可复核的 baseline action log、同 acceptance 的结果/Git references 和 A/Experience Version 对照 scorecard。不修改 ZAgenticOPN runtime，不提前开展跨设备、自动发现、恢复或生产运维。)
- Q: 方案 A 的可复核投影如何生成？ → 固定复用 ZAgentic/research/multi-device-agent-context/report-ir.json、ledger-response-v2.json 和 brief.json；仅在隔离临时目录将 Report IR family 投影为 zj-draft/v1，调用现有 publish_report.py 生成 Markdown/HTML/receipt，再把不可变运行结果和指标摘要纳入 OPN 对照记录，不修改 sibling repo 的源输入或既有输出。 (该投影验证同一真实输入在改进前编译器家族下的结果形态；Human 手动搬运、派发、review 与缝合的时间和动作必须另行由 Human 现场记录，不能由投影或 Agent 事件推定。)
- Q: 方案 A 当前是否可以判定完成？ → 不能。zj-draft/v1 的同输入 baseline projection 已成功并写入 OPN，但真实 Human 手动搬运、派发 WorkBuddy、安排 Codex review、结果缝合及其逐次时间戳尚未发生或未记录；1-3-1 保持 in_progress。 (baseline projection 只证明改进前输出形态和编译 receipt 可复核，不替代方案 A 的 Human action log、同 acceptance 的真实 Git artifact 或 A/Experience Version 时间对照。)
<!-- ROADMAP_SECTION_END -->
