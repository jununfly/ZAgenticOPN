<!-- ROADMAP_SECTION_START -->
## ZJ Roadmap

> 数据文件: `agent-self-service-collaboration-roadmap.json` | 最后更新: 2026-08-28 01:54:04

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

### 当前施工：1-2-1-3-3-2. 价值实验一：zj-research-report 技术方案分析维护

C2 真实竞争 claim 已完成，Human 已恢复三次独立价值实验。下一步创建新的真实 Work Item，执行价值实验一：维护并改进 zj-research-report 技术方案分析能力；必须产出独立事件窗口、真实 Git artifact 与可复核收益证据。

**决策：**
- Q: 价值实验一的首次启动顺序如何处理？ → 将 preflight 的错误顺序标记为 observed-failure：Codex 在 Work Item 已预发布后 claim 了本应由 WorkBuddy 执行的任务；该尝试不计入价值实验窗口。阻断该 preflight Work Item 后，重新执行干净窗口：Codex 先检查空 frontier，随后发布初始 Work Item，WorkBuddy claim/执行，Codex review。 (preflight 未执行代码、未产生 Git artifact；干净窗口必须有 3 次任务无关 activation、独立 Work Item、独立事件窗口、真实 commit/changed files/tests 和可复核 review。)
- Q: 价值实验一首个干净窗口的实际结果是什么？ → 窗口未通过：Codex 空 frontier → 发布新 Work Item → WorkBuddy 真实 UI discover/claim → Codex review 的事件链已形成，但 WorkBuddy 只提交了 partial 前置 audit，未完成 ZAgentic source skill 修改、运行 quick_validate.py / publish_report.py 或 healthy=true receipt；Codex 已 request_changes，Work Item 回到 available，节点保持 in_progress。 (分类为 observed-failure：WorkBuddy 将本地跨仓库 commit 误判为必须等待新的 Human commit+push 指令，尽管当前 Work Item acceptance 已明确授权实际 source update。保留 preflight commit 与完整事件证据；不追加第四次 activation，不把 partial 当作价值实验通过。后续需重新开启独立窗口。)
- Q: 旧 partial Work Item 与价值实验一的新窗口如何处理？ → 按 Human 指令将旧 Work Item work-value-experiment-1-zj-research-report-20260828-clean 阻断为 blocked/observed-failure，保留完整审计记录；新建独立 Work Item work-value-experiment-1-zj-research-report-20260828-rerun，重新开始价值实验一窗口。 (旧项因 block seam 要求由 cleanup identity 领取后立即阻断，未执行目标任务；新项 acceptance 明确 KEP-753 steps 7/8 的 bounded improvement、source/runtime alias 同步、quick_validate.py、publish_report.py、真实 commit 和 healthy=true receipt。恰好三次正式任务无关 activation 尚未开始；此前 inspect discover 事件不计入正式窗口。)
<!-- ROADMAP_SECTION_END -->
