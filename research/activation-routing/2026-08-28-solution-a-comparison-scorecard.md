# 方案 A / Experience Version 对照 scorecard — 2026-08-28

## 当前结论

**未完成对照；继续停留在 Experience Version。** 方案 A 的同输入编译 baseline 已通过可复核发布，但真实 Human 手动路径尚未执行或没有逐次 action log，因此不能判断 Human intervention 是否不明显劣于方案 A，也不能关闭 roadmap 节点 `1-3-1`。

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
| 同 acceptance 的最终 Git artifact | NOT RECORDED | 三个独立 Work Item 均有 artifact；C1–C4 通过 |

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

Experience Version 侧的既有证据仍以 [`2026-08-28-experience-version-scorecard.md`](2026-08-28-experience-version-scorecard.md) 为准；其中记录的严格 activation 观察为 `2/9/4`，且已明确方案 A 和完整 Human action log 缺失。

## 退出判断

| 条件 | 当前判断 |
|---|---|
| C1–C4 与最终 Git artifact | Experience Version 已通过 |
| 方案 A 同 acceptance 对照 | 仅 baseline projection 已通过，人工路径未证明 |
| Human task-specific intervention=0（Experience Version） | 未证明 |
| Experience Version 每次恰好 3 次 activation | 未证明，既有观察为 `2/9/4` |
| Human intervention 不明显劣于方案 A | 未证明 |
| 连续 3 次真实任务实验 | 交付证据部分通过，但价值门未同时满足 |
| `1-3-1` | 保持 `in_progress` |

## 下一步

Human 按 action-log 模板现场运行一次完整方案 A；任何额外 retry、request-changes、权限或方向处理都单独记录。回填真实 Git references 和时间戳后，再更新本 scorecard；没有这些事实，不得将节点置为 `completed`，也不得推进 `1-3-2` 或 `1-3-3`。
