# 方案 A Human action log — 2026-08-28

## 状态

**未执行。** 这是方案 A 的现场记录模板，不是已发生的 Human 行动证据。没有根据 Agent 事件、Git 时间或编译耗时反推任何 Human action、activation 或介入时间。

方案 A 必须在与 Experience Version 相同的真实任务和 acceptance 下，由 Human 手动完成上下文搬运、任务派发、review 安排和结果缝合；每一项都要在发生时记录开始/结束时间。Agent 执行、测试、编译和 review 的耗时不计入 Human intervention，除非 Human 实际在该时间段执行了上述动作。

**审计指针（2026-08-29）：** 本表在 2026-08-29 的全量只读核对后**仍未填写**。核对发现固定实验输入完好，但同一真实任务已由 Experience Version 臂交付、运行副本漂移已消除，方案 A 的源码变更集归零。详见 [`2026-08-29-solution-a-window-audit.md`](2026-08-29-solution-a-window-audit.md)。该审计不构成本表任何一行的记录，也不替代 Human 现场填写。

**任务 B 指针（2026-08-29）：** Human 选 B 后改用新任务（KEP-753 step 4 → 机器可核验 `riskRegister`）。任务定义见 [`2026-08-29-solution-a-task-b-kit.md`](2026-08-29-solution-a-task-b-kit.md)；Agent 侧实现与编译已完成，机器可复核事实见 [`2026-08-29-solution-a-task-b-agent-record.md`](2026-08-29-solution-a-task-b-agent-record.md)。**本表依旧空白** —— review 搬运、review 安排、结果缝合及全部时间戳仍只能由 Human 现场记录。

## 固定实验输入

- 初始目标：找一份优秀的技术方案分析报告，改进 `zj-research-report` 这个 skill 的效果。
- 任务范围：ZAgentic 的 `skills/research/zj-tech-research-report/` 源 skill、必要 reference/validation 输入，以及不改名的 `/Users/bilibili/.codex/skills/zj-research-report/` 运行副本；不得修改 ZAgenticOPN 产品 runtime 或启动 Feature 1 runtime PoC。
- 标杆：固定 commit `fc09a26d4236305d3f282377ca92bdfb2b1fb03c` 的 Kubernetes KEP-753。
- acceptance：更新源 skill 与运行副本；技术 IR 输出 Key-Value、C4 全景图和子主题图、候选卡片、指标矩阵、风险/验证链路和建议；同一真实报告重新编译成功；skill 校验通过；发布 receipt 的 `healthy` 为 `true`。
- 必须执行的验证：`quick_validate.py`；使用同一真实 Report IR 执行 `publish_report.py`，不得覆盖已有输出；记录 commit SHA、changed files、测试命令和结果。
- 协作约束：不依赖 shared context 的 Agent 自主发现；Human 可以把 objective、acceptance 和前序结果复制给下一个 Agent，并手动指定任务、安排 review、拼装最终结果。

## 现场记录表

只在动作真实发生后填写；`—` 表示该动作没有发生，不能填写为估算值。

| # | Human action（具体动作） | 开始时间（含时区） | 结束时间（含时区） | Human 用时（秒） | 任务特定 prompt 原文/摘要 | 复制了哪些上下文或结果 | 手动派发/指定 | 手动安排 review | 结果 stitching | 异常/重试/方向决策 |
|---:|---|---|---|---:|---|---|---|---|---|---|
| 1 | 待现场填写 | — | — | — | — | — | — | — | — | — |
| 2 | 待现场填写 | — | — | — | — | — | — | — | — | — |
| 3 | 待现场填写 | — | — | — | — | — | — | — | — | — |

如发生额外搬运、派发、review loop、request-changes、权限处理或结果拼接，继续追加行；不得把重试压缩为一次成功。

## 汇总字段

- 实验开始时间：未记录
- 实验结束时间：未记录
- Agent activation 次数：未记录
- 任务特定 prompt 次数：未记录
- 上下文复制次数：未记录
- 人工派发/Work Item 指定次数：未记录
- 人工 review 安排次数：未记录
- 结果 stitching 次数：未记录
- 异常处理次数：未记录
- Human intervention 总时间：未记录
- Agent runtime（单独观察，不计入上项）：未记录
- 最终 Git commit：未记录
- changed files：未记录
- 测试命令与结果：未记录
- 最终 acceptance：未验证

## 记录规则

Human intervention 总时间只汇总 Human 实际执行任务特定提示、上下文复制、人工派发/指定、review 安排、结果 stitching 和异常处理的时间；不包含 Agent 自主执行、Git 操作、测试、编译或等待时间。若一个时间段同时包含 Human action 和 Agent 等待，只计 Human 实际 action 的可观察时段，并在备注中说明测量方式。
