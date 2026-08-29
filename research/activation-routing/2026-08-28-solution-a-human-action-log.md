# 方案 A Human action log — 2026-08-28（2026-08-29 补全）

## 状态

**已补全，来源为操作日志，不是手工现场记录。**

Human 于 2026-08-29 02:27 GMT+8 决定改变测量方法：**正常工作场景不会让人逐环节手工记起止时间，但会用代码/日志记录必要操作**。因此本表改为从会话操作日志中提取，而不是要求 Human 现场填写。

### 数据来源

| 项 | 值 |
|---|---|
| 日志文件 | `~/.workbuddy/projects/Users-bilibili-Documents-workspace-github-jununfly-ZAgenticOPN/d3b414ac-e89c-4f3e-a079-f951b8464e0e.jsonl` |
| 结构 | 每行一条 `type=message`，含 `role`（`user` / `assistant`）与 `timestamp`（epoch ms） |
| 提取规则 | `role=user` 即 Human 动作（Human 主动输入）；`role=assistant` 即 Agent 轮次产出 |
| Human 侧用时定义 | **上一条 Agent 完成 → 本条 Human 发送** 的间隔 |
| 时区 | GMT+8（Asia/Shanghai） |
| 提取脚本（两臂共用） | `scripts/extract_human_actions.py`（`python3 scripts/extract_human_actions.py <session.jsonl> [...]`） |
| **测量窗口** | **00:23:03 → 02:27:05**，即任务 B 交付与证据闭合为止 |

⚠️ **窗口之后的动作不计入本表。** 会话在 02:27:05 之后仍继续（如 02:33:14「现在就去提取 EV 侧」属于**测量活动本身**，不是任务 B 的交付动作）。若对整段会话无窗口地跑脚本，会得到 16 条 / 65.4 min / 26.2 min —— 该数字包含测量活动，**不可与 EV 臂对照**。两臂必须以「任务交付完成」为窗口终点，否则 EV 侧也会被后续无关议题污染。

### 这条定义的三个必须知道的偏差

1. **它是上界，不是 Human 实际动手时间。** 间隔里包含 Human 读输出、判断、打字，也**可能包含 Human 离开**的时间，两者无法从该日志分离。
2. **它可能包含第三方 Agent 的 runtime。** 例如 01:07:14 → 01:27:06 这 19.9 分钟里，Codex 执行 review 的耗时也在内 —— 那是另一个 Agent 的运行时间，不是 Human 时间，但本日志无法拆分。
3. **Human 侧没有"开始/结束"两个时刻**，只有发送时刻。所以表里「开始时间」= 上一条 Agent 完成时刻（Human 侧窗口的起点），「结束时间」= Human 发送时刻；这不等于 Human 全程在动手。

按排除规则给出两个口径，都列出来，不替读者选：

| 口径 | 计算 | 结果 |
|---|---|---|
| A：全部 Human 动作（按 log 规则剔除 Git 操作） | 3862.0 − 63.0 − 76.4 | **3722.6 s = 62.0 min** |
| B：在 A 基础上再剔除两段 >15 min 的可疑离开窗口 | 3722.6 − 1157.9 − 1192.2 | **1372.5 s = 22.9 min** |

**与 Experience Version 对照时，两臂必须用同一口径、同一提取脚本。** 绝对值不准不要紧，方法一致才要紧 —— 而手工时间戳在两臂都拿不到，操作日志在两臂都能提取。

## 固定实验输入

- 初始目标：找一份优秀的技术方案分析报告，改进 `zj-research-report` 这个 skill 的效果。
- 任务范围：ZAgentic 的 `skills/research/zj-tech-research-report/` 源 skill、必要 reference/validation 输入，以及不改名的 `/Users/bilibili/.codex/skills/zj-research-report/` 运行副本；不得修改 ZAgenticOPN 产品 runtime 或启动 Feature 1 runtime PoC。
- 标杆：固定 commit `fc09a26d4236305d3f282377ca92bdfb2b1fb03c` 的 Kubernetes KEP-753。
- acceptance：更新源 skill 与运行副本；技术 IR 输出 Key-Value、C4 全景图和子主题图、候选卡片、指标矩阵、风险/验证链路和建议；同一真实报告重新编译成功；skill 校验通过；发布 receipt 的 `healthy` 为 `true`。
- 必须执行的验证：`quick_validate.py`；使用同一真实 Report IR 执行 `publish_report.py`，不得覆盖已有输出；记录 commit SHA、changed files、测试命令和结果。
- 协作约束：不依赖 shared context 的 Agent 自主发现；Human 可以把 objective、acceptance 和前序结果复制给下一个 Agent，并手动指定任务、安排 review、拼装最终结果。

实际执行的新任务（原任务已被 Experience Version 臂抢占）：**KEP-753 step 4 → 机器可核验的 `riskRegister`**，见 [`2026-08-29-solution-a-task-b-kit.md`](2026-08-29-solution-a-task-b-kit.md) 与 [`2026-08-29-solution-a-window-audit.md`](2026-08-29-solution-a-window-audit.md)。

## 现场记录表

全部时间 GMT+8。数据来自上述操作日志；「Human 用时（秒）」为口径定义下的间隔，非手工计时。

| # | Human action（具体动作） | 开始时间 | 结束时间 | Human 用时（秒） | 任务特定 prompt 原文/摘要 | 复制了哪些上下文或结果 | 手动派发/指定 | 手动安排 review | 结果 stitching | 异常/重试/方向决策 |
|---:|---|---|---|---:|---|---|---|---|---|---|
| 1 | 派发：给出 action log 路径，要求处理任务 | 2026-08-29 00:23:03 | 2026-08-29 00:23:03 | —（无前序 Agent） | `处理任务： research/activation-routing/2026-08-28-solution-a-human-action-log.md` | — | ✅ 派发 | — | — | — |
| 2 | 决策：选择方案 B（换新任务 + 两臂独立分支重跑） | 00:30:32 | 00:49:50 | 1157.9 | `b` | — | ✅ 指定新任务 | — | — | ✅ 方向决策 |
| 3 | 搬运 Codex review 硬违规 #1 给 WorkBuddy | 01:07:14 | 01:27:06 | 1192.2 | `Standards - 硬违规：owner: "TBD" 仍会通过 validator；但契约明确禁止 TBD` | Standards finding 全文 + SKILL.md:125 / validate:223 定位 | — | ✅（来自 Codex review） | — | — |
| 4 | 搬运硬违规 #2（词汇未同步 ZJ-CONTEXT.md） | 01:31:45 | 01:33:37 | 112.1 | `- 硬违规：新增 riskRegister / riskRegisterCoverage 未同步到 ZJ-CONTEXT.md` | AGENTS.md:79 规则引用 | — | ✅ | — | — |
| 5 | 搬运判断项（测试重复代码抽取） | 01:36:44 | 01:38:56 | 132.3 | `- 判断项：测试中三段拒绝发布流程重复，可抽取辅助函数` | verify_technical_report.py:297 定位 | — | ✅ | — | — |
| 6 | 搬运 Spec P1（acceptance 7 未闭合） | 01:42:59 | 01:43:34 | 35.4 | `Spec - [P1] Acceptance 7 尚未闭合：当前仍无 commit SHA` | — | — | ✅ | — | — |
| 7 | 触发 `commit+push`（ZAgentic 侧） | 01:45:33 | 01:46:36 | 63.0 | `commit+push，acceptance 7 当场闭合` | — | — | — | — | Git gate（按记录规则不计入 Human intervention） |
| 8 | 搬运 P1（TBD 未实现）—— 事后证伪 | 01:50:28 | 01:54:08 | 219.9 | `[P1] owner 的 TBD 禁止未被实现或测试覆盖。` | — | — | ✅ | — | ✅ 异常：review 读到未合并的 `main`，非漏做 |
| 9 | 搬运 P2（复述判定只比完全相等） | 01:56:15 | 01:58:11 | 115.6 | `[P2] mitigation 仅拒绝完全相等文本；增加句号或少量文字即可绕过“不得复述 risk”要求。` | — | — | ✅ | — | — |
| 10 | 搬运 P1/部分（gate 通过 ≠ 读者可见）第 1 次 | 02:02:25 | 02:03:46 | 81.1 | `[P1/部分] IR 中有 4 条风险且 quality gate 通过，但生成的 report.md 和 HTML 不展示风险登记` | report.md 路径 | — | ✅ | — | — |
| 11 | 同一 finding 第 2 次投递 | 02:05:35 | 02:05:48 | 12.8 | 同上（重复） | — | — | ✅ | — | ✅ 重复投递 1/3 |
| 12 | 同一 finding 第 3 次投递 | 02:05:50 | 02:05:56 | 5.9 | 同上（重复） | — | — | ✅ | — | ✅ 重复投递 2/3 |
| 13 | 回报 review 结果 + 追加提交信息（结果缝合） | 02:09:53 | 02:16:26 | 392.1 | `已经交给codex review了：已完成追加提交并 push。分支/Commit/远端/验证/未跟踪目录状态` | 分支名、commit `5942550`、验证结论 | — | ✅ 已安排 Codex review | ✅ 拼装最终状态 | — |
| 14 | 触发 `commit+push`（OPN 记录侧） | 02:18:48 | 02:20:04 | 76.4 | `commit+push` | — | — | — | — | Git gate（不计入） |
| 15 | 决策：改用操作日志补全，放弃手工时间戳 | 02:22:39 | 02:27:05 | 265.3 | `这里不用Human action log 的时间戳…你可以替我从操作日志中补全。` | — | — | — | — | ✅ 方向决策（测量方法变更） |

如发生额外搬运、派发、review loop、request-changes、权限处理或结果拼接，继续追加行；不得把重试压缩为一次成功。（#10–#12 是同一 finding 的三次投递，已逐条保留，未压缩。）

## 汇总字段

| 字段 | 值 |
|---|---|
| 实验开始时间 | 2026-08-29 00:23:03 GMT+8 |
| 实验结束时间 | 2026-08-29 02:27:05 GMT+8（最后一条 Human 动作；其 Agent 轮次仍在进行） |
| Agent activation 次数 | **15**（= Human 发起的 Agent 轮次）。⚠️ 方案 A 是人工路径，**不使用 OPN 的 activation 机制**，这里的 15 是等价物，**不能与 Experience Version 臂的 activation 计数直接比较** |
| 任务特定 prompt 次数 | 15 |
| 上下文复制次数 | 9（#3–#6、#8–#12 均为把 review finding 原文搬给 WorkBuddy） |
| 人工派发/Work Item 指定次数 | 2（#1 派发、#2 指定新任务） |
| 人工 review 安排次数 | 1（#13 回报已交 Codex review）+ 9 次 review 意见回搬（#3–#6、#8–#12） |
| 结果 stitching 次数 | 1（#13） |
| 异常处理次数 | 3（#10–#12 重复投递；另 #8 为误报：review 读错 ref） |
| Human intervention 总时间 | **口径 A 3722.6 s = 62.0 min**（剔除 Git 操作）；**口径 B 1372.5 s = 22.9 min**（再剔除两段 >15 min 可疑离开窗口）。两者均为**上界** |
| Agent runtime（单独观察，不计入上项） | 3579.2 s = 59.7 min（14 个 Agent 轮次合计） |
| 全程墙钟 | 7441.2 s = 124.0 min |
| 最终 Git commit | ZAgentic `93c17b78591a101450f270a35e2da5eed4d02611` + `5942550e928dd97d887bdff35ad07d79f22e404b`；记录侧 ZAgenticOPN `250aa0a…` + `4574b821c0e328e58364c6021ac8f97a979eaa17` |
| changed files | 见 [`2026-08-29-solution-a-task-b-agent-record.md`](2026-08-29-solution-a-task-b-agent-record.md)（提交 1：5 文件 +152/−75；提交 2：4 文件 +55/−8） |
| 测试命令与结果 | 同上（skill 契约测试、`quick_validate.py`、三次不覆盖的真实编译全部通过） |
| 最终 acceptance | **6/7 达成**。未达成项：技术 IR 输出中的「风险/验证链路」**读者不可见** —— 渲染器是 ZHarness 的锁定产物（`9172aa0`），不解 `riskRegister`。详见 r7，属上游依赖，不阻塞本节点 |

## 记录规则

Human intervention 总时间只汇总 Human 实际执行任务特定提示、上下文复制、人工派发/指定、review 安排、结果 stitching 和异常处理的时间；不包含 Agent 自主执行、Git 操作、测试、编译或等待时间。若一个时间段同时包含 Human action 和 Agent 等待，只计 Human 实际 action 的可观察时段，并在备注中说明测量方式。

**2026-08-29 方法变更：** 上述时间不再要求 Human 手工记录，改由操作日志提取（见文首「数据来源」）。三条限制必须随数字一起引用，缺一条都会让这个数字被误读为「Human 实际动手时间」：

1. 是上界，含可能的离开时间；
2. 可能混入第三方 Agent（Codex）的 review runtime；
3. 只有 Human 发送时刻，没有 Human 侧起止双时刻。
