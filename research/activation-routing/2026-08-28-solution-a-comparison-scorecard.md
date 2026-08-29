# 方案 A / Experience Version 对照 scorecard — 2026-08-28

## 当前结论

**两臂都已有同口径数字，对照可以判了 —— 但只能判到「倾向成立」，判不到「确证」。**

截至 2026-08-29：任务 B 产出 `93c17b7` + `5942550`，双 gate 健康；**两臂的 Human action 均已由会话操作日志提取**（方法完全一致）。归一化到单任务后 Experience Version 是 **7.0 次 Human 动作 / 10.8 min**，方案 A 是 **15 次 / 22.9 min** —— EV 约为方案 A 的一半，「Human intervention 不明显劣于方案 A」**倾向成立**。但两臂各有一条方向相反、无法量化的偏差（见下），且「每次恰好 3 次 activation」与「任务特定介入 = 0」两门仍未过，所以 `1-3-1` 保持 `in_progress`。

**最重要的产品发现**：两臂都需要 Human 搬运 review 结论（方案 A 9 次、EV 3 次）。OPN seam 自动化了 discover / claim / handoff，但**没有自动化跨厂商 Agent 之间的 review 结论往返** —— Human 仍然是 WorkBuddy ↔ Codex 的传输层。这与「有没有 shared context」无关，建议单独立项。

## 输出与验收对照

| 维度 | 方案 A：人工路径 + `zj-draft/v1` baseline | Experience Version：`technical-c4/v1` |
|---|---|---|
| 同一 Report IR 编译 | PASS；report hash `64b61f0e…ad1bb` | PASS；report hash `01637657…857e6` |
| 编译发布健康 | PASS；receipt `healthy=true` | PASS；compiler 与 technical quality gate 均 `healthy=true` |
| C4 landscape/container | 0 个已渲染 | 2 个已渲染 |
| 候选卡片 | 0 张已渲染 | 3 张 |
| 指标矩阵 | 0 个已渲染 | 6 个 |
| Graduation criteria | 未渲染 | 3 条已进入 IR/质量 gate |
| Human task-specific prompts | **15**（操作日志提取） | **21**（其中 9 条 `检查 shared context` + 8 条短指令 + 3 条结论搬运 + 1 条通知） |
| 上下文复制 | **9**（把 review finding 原文搬给 WorkBuddy） | **3**（把 Codex review 结论搬回；990 / 548 / 184 字符） |
| 人工派发 / Work Item 指定 | **2** | **0**（activation 由 `检查 shared context` 触发，不指定 Work Item） |
| review 安排 | **1**+ 9 次 review 意见回搬 | 0 次显式安排（review 经 OPN seam 自动 continuation），但 **3 次 review 结论回搬** |
| 结果 stitching | **1** | **0**（未观察到 Human 拼装动作） |
| 异常处理 | **3**（同一 finding 重复投递） | 0（未观察到） |
| Git gate（`commit+push`） | **2** | **0**（这四个会话内；提交由 Agent 执行 + PR 合并） |
| activation | 无此机制（人工路径） | **9** 次 `检查 shared context` |
| Human intervention 总时间 | **口径 A 62.0 min / 口径 B 22.9 min**（上界） | **口径 A 1317.2 min / 口径 B 32.5 min**（上界，跨 4 会话 / 3 实验） |
| Agent runtime（单独观察） | 59.7 min（14 个 Agent 轮次） | 未逐轮统计 |
| 墙钟 | 124.0 min | ≈1090.9 min（01:57 → 22:12） |
| 归一化到单任务 | 15 次动作 / 22.9 min | **7.0 次动作 / 10.8 min** |
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

1. 方案 A 的任务特定 prompt、上下文复制、人工派发、review 安排、结果 stitching 和异常处理的逐次数量。→ **已由操作日志提取**（15 / 9 / 2 / 1+9 / 1 / 3）。
2. 方案 A activation count 与 Human intervention total time。→ 已提取，但**两个口径都是上界**（62.0 min 全量 / 22.9 min 剔除可疑离开窗口），且**可能混入第三方 Agent（Codex）的 review runtime**。
3. 同 acceptance 的方案 A Git commit、changed files、测试命令/结果及 review provenance。→ **已补齐**（`93c17b7` + `5942550`）。

**2026-08-29 方法变更**：Human 判定「正常工作场景不会逐环节手工记起止时间，但会用日志记录必要操作」，因此上述数字改为从会话操作日志
`~/.workbuddy/projects/…/d3b414ac-e89c-4f3e-a079-f951b8464e0e.jsonl` 提取（`role=user` 条目即 Human 动作），不再要求现场手工填写。

⚠️ **对照仍需同口径的 Experience Version 数字才能判定。** 方案 A 已有数，Experience Version 侧还是空白 —— 手工时间戳两臂都拿不到，操作日志两臂都能提取，所以下一步是把同一提取脚本跑在 Experience Version 的会话日志上。在那之前，「Human intervention 不明显劣于方案 A」只能维持未证明。

Experience Version 侧的既有证据仍以 [`2026-08-28-experience-version-scorecard.md`](2026-08-28-experience-version-scorecard.md) 为准；其中记录的严格 activation 观察为 `2/9/4`，且已明确方案 A 和完整 Human action log 缺失。

## 退出判断

| 条件 | 当前判断 |
|---|---|
| C1–C4 与最终 Git artifact | Experience Version 已通过 |
| 方案 A 同 acceptance 对照 | 任务 B 的 Git artifact 已产出（`93c17b7` + `5942550`）+ baseline projection 已通过；action log 已由操作日志补全 |
| Experience Version 同口径 Human 数字 | **已测得**（21 条 / 32.5 min 剔 >15min 口径），见 [`2026-08-29-experience-version-operation-log-extraction.md`](2026-08-29-experience-version-operation-log-extraction.md) |
| **Human intervention 不明显劣于方案 A** | **倾向成立** —— 归一化单任务：EV 7.0 次 / 10.8 min vs 方案 A 15 次 / 22.9 min。误差宽，判不到确证 |
| Human task-specific intervention=0（Experience Version） | **未过** —— 实测 8 条短指令 + 3 条 review 结论搬运，不是 0 |
| Experience Version 每次恰好 3 次 activation | **未过** —— 操作日志实测共 9 次 `检查 shared context`，既有事件窗口观察为 `2/9/4` |
| 连续 3 次真实任务实验 | 交付证据通过（三个独立 Work Item + 三个 commit），但上面两个价值门未同时满足 |
| `1-3-1` | 保持 `in_progress` |

## 两臂各一条方向相反、无法量化的偏差

| 臂 | 偏差 | 方向 |
|---|---|---|
| EV | 四个会话里混有实验之外的议题（`确认移入回收站`、PR 合并通知等），全算到三次实验头上 | **高估** EV 成本 → 使「EV 更省」偏保守 |
| EV | `commit+push` 为 0 只说明这四个会话里没有，可能发生在其他会话或 GitHub 网页端 | **低估** EV 成本 |
| 两臂 | gap 中含第三方 Agent runtime（方案 A 含 Codex review；EV 含 OPN agent 执行 + Codex review） | 同类误差，不偏袒任何一侧 |

两条不能互相抵消，只能并列声明 —— 这是「倾向成立」而非「确证」的全部理由。

## 下一步

1. ~~沉淀方法：把「从会话操作日志提取 Human action」固化成脚本放进 `scripts/`。~~ **已完成**：`scripts/extract_human_actions.py`，两臂共用，已复算两臂数字逐项一致。
2. **窗口规则必须随方法一起固化**：两臂都以「任务交付完成」为窗口终点。方案 A 窗口 00:23:03→02:27:05；无窗口地跑整段会话会把测量活动算进去（方案 A 会变成 16 条 / 26.2 min），同样地 EV 侧也会被后续无关议题污染。
2. **关闭剩余两个价值门**，二者都需要产品改动而非更多测量：
   - 「每次恰好 3 次 activation」→ 需要约束 activation 语义（当前一次 `检查 shared context` 之后的 agent 内部轮次会派生额外 activation）
   - 「任务特定介入 = 0」→ 需要把 review 结论回搬也接入 seam；这正是上面那条产品发现
3. 在这两个门关闭前，不得将 `1-3-1` 置为 `completed`，也不得推进 `1-3-2` 或 `1-3-3`。
4. 若要落 roadmap `1-3-1` 决策段，须走 `zj-roadmap-driven`，不得直接编辑 JSON 或渲染后的 md。
