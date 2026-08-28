# 方案 A / Experience Version 对照 scorecard — 2026-08-28

## 当前结论

**未完成对照；继续停留在 Experience Version。** 截至 2026-08-29，方案 A 侧新增了一块证据：任务 B（KEP-753 step 4 → 机器可核验 `riskRegister`）产出同 acceptance 的 Git artifact `93c17b7`，同输入 baseline projection 与真实编译双 gate 健康。**但 Human action log 仍一行未填**，方案 A 的逐次时间戳、派发次数、review 安排与总介入时间全部缺失，因此仍不能判断 Human intervention 是否不明显劣于方案 A，`1-3-1` 不能关闭。

## 输出与验收对照

| 维度 | 方案 A：人工路径 + `zj-draft/v1` baseline | Experience Version：`technical-c4/v1` |
|---|---|---|
| 同一 Report IR 编译 | PASS；report hash `64b61f0e…ad1bb` | PASS；report hash `01637657…857e6` |
| 编译发布健康 | PASS；receipt `healthy=true` | PASS；compiler 与 technical quality gate 均 `healthy=true` |
| C4 landscape/container | 0 个已渲染 | 2 个已渲染 |
| 候选卡片 | 0 张已渲染 | 3 张 |
| 指标矩阵 | 0 个已渲染 | 6 个 |
| Graduation criteria | 未渲染 | 3 条已进入 IR/质量 gate |
| Human task-specific prompts | NOT RECORDED | 退出条件要求 0；既有 scorecard 未形成逐次 action log |
| 上下文复制 | NOT RECORDED | 退出条件要求 0；既有 scorecard 未形成逐次 action log |
| 人工派发 / Work Item 指定 | NOT RECORDED | 退出条件要求 0；shared event 不能证明 Human 未做此动作 |
| review 安排 | NOT RECORDED | 退出条件要求 0；既有事件只证明 Agent review continuation |
| 结果 stitching | NOT RECORDED | 退出条件要求 0；shared event 不能证明 Human 未做此动作 |
| Human intervention 总时间 | NOT RECORDED | NOT PROVEN；Agent runtime 不计入该指标 |
| 同 acceptance 的最终 Git artifact | 任务 B：`93c17b7`（分支 `solution-a/kep753-risk-register`，未合并 main）；r1/r2 输出目录未跟踪、留在工作区 | 三个独立 Work Item 均有 artifact；C1–C4 通过 |

## Baseline artifact

- [`2026-08-28-solution-a-baseline.md`](2026-08-28-solution-a-baseline.md)
- [`2026-08-28-solution-a-baseline.html`](2026-08-28-solution-a-baseline.html)
- [`2026-08-28-solution-a-baseline-receipt.json`](2026-08-28-solution-a-baseline-receipt.json)
- 编译器：`zj-research-cli/v1` / `research/v1`
- report hash：`64b61f0eef37682371b0dd5d7d32ec67975dfc2ff7220afe9c4f1dad909ad1bb`
- receipt correctness：`revisionPinned`, `provenanceComplete`, `criticalClaimsEvidence`, `scoringAxesSeparated`, `publishExactlyOnce`, `receiptConsistent` 全部为 `true`

## Human action evidence

现场模板：[`2026-08-28-solution-a-human-action-log.md`](2026-08-28-solution-a-human-action-log.md)。在 Human 真实执行并填写之前，以下价值门保持未证明：

1. 方案 A 的任务特定 prompt、上下文复制、人工派发、review 安排、结果 stitching 和异常处理的逐次数量。
2. 方案 A activation count 与 Human intervention total time。
3. 同 acceptance 的方案 A Git commit、changed files、测试命令/结果及 review provenance。

第 3 项自 2026-08-29 起**部分补齐**：任务 B 的 Git artifact 已存在（`93c17b7`，见 [`2026-08-29-solution-a-task-b-agent-record.md`](2026-08-29-solution-a-task-b-agent-record.md)），changed files 与测试命令/结果均已记录。**但第 1、2 项仍全空** —— action log 表格一行未填。

**有 artifact 不等于价值门过了。** artifact 只证明方案 A 臂能产出同 acceptance 的可复核交付；Human intervention 对照要靠逐次时间戳，而时间戳只能由 Human 现场记录，不能由 commit、事件窗口或 Agent runtime 反推。因此本 scorecard 的价值门判断维持不变。

Experience Version 侧的既有证据仍以 [`2026-08-28-experience-version-scorecard.md`](2026-08-28-experience-version-scorecard.md) 为准；其中记录的严格 activation 观察为 `2/9/4`，且已明确方案 A 和完整 Human action log 缺失。

## 退出判断

| 条件 | 当前判断 |
|---|---|
| C1–C4 与最终 Git artifact | Experience Version 已通过 |
| 方案 A 同 acceptance 对照 | 任务 B 的 Git artifact 已产出（`93c17b7`）+ baseline projection 已通过；**action log 仍全空**，人工路径未证明 |
| Human 手动路径逐次 action log | **未填写** —— 方案 A 唯一的剩余阻塞项 |
| Human task-specific intervention=0（Experience Version） | 未证明 |
| Experience Version 每次恰好 3 次 activation | 未证明，既有观察为 `2/9/4` |
| Human intervention 不明显劣于方案 A | 未证明 |
| 连续 3 次真实任务实验 | 交付证据部分通过，但价值门未同时满足 |
| `1-3-1` | 保持 `in_progress` |

## 下一步

Human 按 action-log 模板现场记录**已经发生**的动作 —— 方案 A 的任务 B 实际上已经跑完三轮 review（r2 占位符漏检、r3 词汇未同步、r4 测试去重）并提交，但这些时间戳**过去没有记录，现在也不能补记**。

两条路，二选一：

1. **承认本轮时间戳已不可得**，把方案 A 的对照重跑一次：从零开始、每次动作现场记时间。代价是任务 B 已有 artifact，重跑会产生第二个 artifact（可用新分支 + 新输出目录隔离，不覆盖）。
2. **改用下一轮任务**（任务 C）从第一行开始就现场记录。任务 B 的 artifact 退化为「方案 A 能产出同 acceptance 交付」的能力证明，不参与 Human intervention 对照。

无论哪条，action log 都必须逐次填，retry/request-changes 单独成行，不得压缩成一次成功。没有这些事实，不得将 `1-3-1` 置为 `completed`，也不得推进 `1-3-2` 或 `1-3-3`。
