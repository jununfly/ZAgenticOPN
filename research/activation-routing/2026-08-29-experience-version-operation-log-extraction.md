# Experience Version 侧操作日志提取 — 2026-08-29

## 为什么有这份文件

方案 A 侧的 Human 计数与用时已由会话操作日志提取（`2026-08-28-solution-a-human-action-log.md`）。要让「Human intervention 不明显劣于方案 A」这个价值门可判，Experience Version 侧必须有**同口径**数字。本文件就是那一侧。

**方法完全一致**：`role=user` 条目 = Human 动作；Human 侧间隔 = 上一条 `assistant` 时间戳 → 本条 `user` 时间戳；两个口径都报（全量上界 / 剔除 >15 min 可疑离开窗口）。

**两臂共用同一个脚本**，避免口径漂移：

```sh
cd /Users/bilibili/Documents/workspace/github/jununfly/ZAgenticOPN
python3 scripts/extract_human_actions.py <session.jsonl> [<session.jsonl> ...]
# --json 输出结构化结果；阈值常量 AWAY_THRESHOLD_S = 900（15 min）
```

该脚本对方案 A 会话重跑可复现已记录数字（窗口内 15 条 / 3862.0s / 1372.5s），对本文件四个 EV 会话重跑得到 21 条 / 79032.4s / 1947.0s —— 与下文表格逐项一致。

## 数据源

四个会话文件，全部来自 ZAgentic 工作区（`~/.workbuddy/projects/Users-bilibili-Documents-workspace-github-jununfly-ZAgentic/`）：

| 会话 | 最后修改 | 承载内容 |
|---|---|---|
| `99eb643d-2eb6-49d2-8e40-bb95eab367e7` | 08-28 11:03 | 实验一 + 交付拒收 + 方向选择 |
| `0cf905ee-f158-4a81-a742-b46b6ca89609` | 08-28 16:08 | 实验二 request_changes 回搬 |
| `1558ad52-3fa4-46b6-91c3-8b5ea784dc34` | 08-28 17:16 | 实验二收尾 |
| `8a289503-5f82-434b-a60c-4a8370b07671` | 08-28 22:14 | 实验三 + PR 合并通知 |

归属依据：对 `work-value-experiment-1-zj-research-report-20260828-rerun` / `work-value-experiment-2-zj-tech-research-report-20260828` / `work-value-experiment-3-technical-proposal-exemplar-20260828` 三个 Work Item id 做命中统计（34/6/1、0/31/19、0/0/28 等分布），未命中任何 id 的会话不纳入。

## Human 动作清单（21 条，GMT+8，2026-08-28）

| # | 会话 | 时间 | 内容 | 类别 | 间隔（秒） |
|---:|---|---:|---|---|---:|
| 1 | 99eb643d | 01:57:39 | `检查 shared context` | activation | 首条 |
| 2 | 99eb643d | 02:10:23 | `确认移入回收站` | 短指令 | 177.9 |
| 3 | 99eb643d | 02:10:23 | `检查 shared context` | activation | 178.4 |
| 4 | 99eb643d | 09:23:46 | 实验一交付拒收结论（990 字符，含 commit `a09fc94` 核实、副本同步状态） | **上下文复制** | 25684.1 ⚠️ |
| 5 | 99eb643d | 10:58:39 | `选a` | 短指令 | 5159.0 ⚠️ |
| 6 | 99eb643d | 10:58:43 | `检查 shared context` | activation | 5162.8 ⚠️ |
| 7 | 99eb643d | 11:02:06 | `选 A1` | 短指令 | 91.7 |
| 8 | 0cf905ee | 11:39:25 | `检查 shared context` | activation | 首条 |
| 9 | 0cf905ee | 16:03:54 | 实验二 request_changes 回搬（548 字符，含 validator 与文档不符的具体问题） | **上下文复制** | 15312.3 ⚠️ |
| 10 | 0cf905ee | 16:03:57 | `检查 shared context` | activation | 15315.6 ⚠️ |
| 11 | 1558ad52 | 16:49:41 | `检查 shared context` | activation | 首条 |
| 12 | 1558ad52 | 17:00:55 | `选 A` | 短指令 | 283.3 |
| 13 | 1558ad52 | 17:10:37 | `请继续完成未完成的任务。` | 短指令 | 11.0 |
| 14 | 8a289503 | 18:05:08 | `检查 shared context` | activation | 首条 |
| 15 | 8a289503 | 18:12:14 | `检查 shared context` | activation | 234.6 |
| 16 | 8a289503 | 20:55:13 | `请继续完成未完成的任务。` | 短指令 | 9453.0 ⚠️ |
| 17 | 8a289503 | 21:31:57 | `检查 shared context` | activation | 998.6 ⚠️ |
| 18 | 8a289503 | 21:52:44 | `单独开一个切片处理` | 短指令 | 571.0 |
| 19 | 8a289503 | 21:58:43 | 实验三验收结论（184 字符，含 Work Item revision 10、commit `f01fa1b`、远程分支） | **上下文复制** | 49.0 |
| 20 | 8a289503 | 22:02:38 | `按 1→2→3→4 一次做完` | 短指令 | 105.6 |
| 21 | 8a289503 | 22:12:18 | `PR 16、17、18 都已经合并` | 通知 | 244.7 |

⚠️ = 间隔 >15 min，在口径 B 中剔除（视为可疑离开窗口，其中也可能包含 Codex 执行 review 的 runtime）。

## 汇总

| 指标 | 值 |
|---|---|
| Human 动作总数 | **21**（跨 4 个会话 / 3 个实验） |
| activation 触发（`检查 shared context`） | **9** |
| 短决策/指令 | **8** |
| **上下文复制**（review 结论搬运） | **3** |
| 通知类 | 1 |
| Git gate（`commit+push`） | **0**（这四个会话里 Human 没敲过；提交由 Agent 执行 + PR 合并） |
| Human 侧间隔上界 | **1317.2 min**（全量，含跨小时离开窗口） |
| 剔除 >15 min 后 | **32.5 min** |
| 四会话墙钟合计 | ≈ 1090.9 min（18.2 h，01:57 → 22:12） |

## 两臂同口径对照

| 维度 | 方案 A（任务 B，1 个任务，1 个会话） | Experience Version（3 个任务，4 个会话） | EV 归一化到单任务 |
|---|---:|---:|---:|
| Human 动作条数 | 15 | 21 | **7.0** |
| 上下文复制 | 9 | 3 | **1.0** |
| 人工派发/指定 | 2 | 0（activation 由 `检查 shared context` 触发） | **0** |
| 短指令/决策 | 2（方向决策） | 8 | **2.7** |
| Git gate | 2 | 0 | **0** |
| 异常处理 | 3（重复投递） | 0（未观察到） | **0** |
| Human 用时（剔 >15 min） | **22.9 min** | **32.5 min** | **10.8 min** |
| Human 用时（全量上界） | 62.0 min | 1317.2 min | 439.1 min |
| Agent runtime | 59.7 min | 未逐轮统计 | — |
| 墙钟 | 124.0 min | ≈1090.9 min | ≈363.6 min |

## 三个必须随数字引用的偏差

1. **EV 的四个会话里混着实验之外的工作**（`确认移入回收站`、PR 合并通知，以及长会话中的其他议题）。把所有 21 条都算到三次实验头上会**高估** EV 成本 —— 也就是说「EV 更省」这个结论在方向上偏保守。
2. **EV 侧 0 次 Git gate 只说明这四个会话里没有**。`commit+push` 有可能发生在其他会话、或其他 UI（GitHub 网页合并 PR）。这一点**低估** EV 成本，方向与上一条相反。两条不能互相抵消，只能并列声明。
3. **两臂的 gap 里都含第三方 Agent runtime**（方案 A 含 Codex review；EV 含 OPN seam 的 agent 执行与 Codex review）。这是同类名误差，不偏向任何一侧。

## 结论

1. **方法可行**：两臂都能从操作日志提取，且 `role` 标签让 Human / Agent 严格可分。手工时间戳两臂都拿不到 —— 这个方法变更是必要且有效的。
2. **「Human intervention 不明显劣于方案 A」：可判 PASS，但误差宽。** 归一化到单任务后 EV 是 7.0 次动作 / 10.8 min，方案 A 是 15 次 / 22.9 min —— EV 约为方案 A 的一半。考虑到上面三条偏差方向相反且无法量化，这个结论的强度是「倾向成立」，不是「确证」。
3. **最值得注意的产品发现：两臂都需要 Human 搬运 review 结论。** 方案 A 搬 9 次、EV 搬 3 次。OPN seam 自动化了 discover / claim / handoff，但**没有自动化跨厂商 Agent 之间的 review 结论往返** —— Human 仍然是 WorkBuddy ↔ Codex 之间的传输层。这是产品的真实缺口，与「有没有 shared context」无关，建议单独立项。
4. **roadmap 里「任务特定 prompt / 上下文复制 = 0」的期望未被满足**：EV 侧有 8 条短指令（`选a` / `选 A1` / `选 A` / `确认移入回收站` / `请继续完成未完成的任务。` ×2 / `单独开一个切片处理` / `按 1→2→3→4 一次做完`）和 3 条 review 结论搬运。这些不是 activation，是 Human 的实际介入。

## Source pointers

- [`2026-08-28-solution-a-human-action-log.md`](2026-08-28-solution-a-human-action-log.md)（方案 A 侧提取）
- [`2026-08-28-solution-a-comparison-scorecard.md`](2026-08-28-solution-a-comparison-scorecard.md)（两臂对照，已回填本文件数字）
- [`2026-08-28-experience-version-scorecard.md`](2026-08-28-experience-version-scorecard.md)（EV 三次实验的 C1–C4 与价值门既有判定）
