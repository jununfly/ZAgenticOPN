# 方案 A 对照实验 — 任务 B 定义与执行包 — 2026-08-29

## 决策

Human 选 **B**：另选一个与价值实验一工作量相当的真实任务，**先跑方案 A 人工路径**，再让 Experience Version 跑同一任务。

本文件是任务 B 的定义、执行包和 Human 记录协议。分类 `stage-critical`：它只补 `1-3-1` 缺失的对照证据，不修改 ZAgenticOPN runtime、不修改 roadmap JSON、不展开跨设备、自动发现、恢复或生产运维。

## 为什么是「两臂独立分支」

上一轮审计发现的退化对照根因是：**先跑的一臂会把任务做完，后跑的一臂无事可做**。因此两臂必须各自从同一基线出发、在互相独立的分支上完成同一任务，且**互不参考对方产物**。

| 项 | 方案 A（本轮，人工路径） | Experience Version（后续） |
|---|---|---|
| 基线 | `d1154ea3f4bcd0f5dcf2b0855ebc3ad735942f1d` | 同一 commit |
| 分支 | `solution-a/kep753-risk-register` | 独立分支，基线相同 |
| 上下文来源 | Human 手动搬运 | shared context 自主发现 |
| 产物 | 独立 commit + 独立输出目录 | 独立 commit + 独立输出目录 |
| 参考对方产物 | 禁止 | 禁止 |

评审时对照两份 diff 与两份 receipt，而不是让后跑的一臂去 review 先跑的一臂的结果。

## 任务 B：KEP-753 step 4 → 机器可核验的 `riskRegister`

### 选择理由

- **同类缺陷**：`SKILL.md` §4 已经用散文要求"risk register with trigger, impact, mitigation, residual risk, and owner"，但质量门里没有任何一项强制它 —— 与 `work-c2-information-gaps-regression-20260827` 修掉的「散文要求 ≠ 契约」是同一类缺陷。
- **未被抢占**：实测 report IR 顶层字段为 `schema/family/title/summary/ledgerFingerprint/informationGaps/concepts/diagrams/candidates/cards/claims/comparisons/recommendations/metrics/graduationCriteria`，**没有** `riskRegister`；质量门的 8 个 check 里没有风险项。
- **工作量对标**：价值实验一做的是「新增一个顶层 IR 字段 + SKILL.md 契约 + exemplar 标注 + 校验器检查 + 测试 + 真实重编译 + review 修订链」。任务 B 形状完全一致，量级相当。

### 排除的候选

| 候选 | 排除原因 |
|---|---|
| step 9 生产就绪 | 只在 `dogfood`/`release` 阶段生效，当前真实报告是 `experience-version`，无法在同一次真实编译里被验证 |
| step 10 缺点与替代方案 | `SKILL.md` §4 与 gate 的 `comparisonTraceability` 已部分覆盖，缺陷不如风险登记项明显 |
| step 11 实现历史 | 价值密度最低，且 exemplar 里 KEP-753 自身该节为空，作为机器契约的说服力弱 |

## Objective（Human 搬运给 Agent 的原文）

> 把 Kubernetes KEP-753 决策链第 4 步「Risks and mitigations」从散文要求升级为机器可核验的 `technical-c4/v1` Report IR 契约：新增顶层 `riskRegister` 字段，每一项必须携带 `risk`、`trigger`、`impact`、`mitigation`、`residualRisk`、`owner` 六个非空字段；在 `SKILL.md` §5 写明契约，在 §4 指向该契约；在 `references/technical-proposal-exemplar.md` 标注 step 4 为机器可核验；在 `scripts/validate_technical_report.py` 增加 `riskRegisterCoverage` 检查与计数；在 `tests/verify_technical_report.py` 增加正例与反例；同步两份 codex 运行副本；用同一份真实 Report IR 重新编译并通过两个 gate。

## Acceptance（原文）

> 1. 源 skill `skills/research/zj-tech-research-report/` 的 `SKILL.md`、`references/technical-proposal-exemplar.md`、`scripts/validate_technical_report.py`、`tests/verify_technical_report.py` 均已更新且相互一致。
> 2. `~/.codex/skills/zj-research-report/`（运行别名，**不得改名**）与 `~/.codex/skills/zj-tech-research-report/`（正名副本）均与源一致（`diff -rq` 只剩 `.pyc` 与 `ALIAS.md`）。
> 3. 同一份真实 Report IR（`research/multi-device-agent-context/report-ir.json`，SHA-256 `f9a6a3a18bc8040b5a28f90de304861e81da29ff9782cbc9a22824e9767d7de3`）派生出带 `riskRegister` 的副本；**原输入文件不被修改**。
> 4. `quick_validate.py` 对修改后的 `SKILL.md` 通过。
> 5. 使用派生 IR 执行 `publish_report.py`，输出到 `skills-outputs/zj-tech-research-report/kep753-risk-register-2026-08-29-solution-a/`（**新目录，不覆盖既有输出**）。
> 6. receipt 的 `healthy` 为 `true`，且 `qualityGate.counts.riskRegister` 为非空数字；编译器与质量门双重健康。
> 7. 记录 commit SHA、changed files、测试命令与结果。

## 范围与禁令

- 允许：`ZAgentic/skills/research/zj-tech-research-report/` 源 skill、其 reference/validation/test 输入、两份 codex 运行副本、`ZAgentic/skills-outputs/` 下的新目录。
- 禁止：修改 ZAgenticOPN 产品 runtime；启动 Feature 1 runtime PoC；修改 roadmap JSON（须走 `zj-roadmap-driven`）；改名运行别名；覆盖任何既有输出；使用 OPN shared context 或 activation runner（方案 A 的定义就是人工路径）。

## Human action log 记录协议

方案 A 的每一次 Human 动作都要在 [`2026-08-28-solution-a-human-action-log.md`](2026-08-28-solution-a-human-action-log.md) 现场记录**开始/结束时间**。Agent 只能记录机器可复核事实，**不得反推 Human 时间戳**。

需要 zj 自行填写的行（最少）：

| 行 | 动作 |
|---|---|
| 1 | 决定改走方案 B、选任务 |
| 2 | 把 objective/acceptance 复制给 WorkBuddy（本轮的 `b` + 本文件） |
| 3 | 把前序结果复制给 WorkBuddy（审计结论、哈希、分支名） |
| 4 | 人工指定任务/派发（本轮指令） |
| 5 | 结果出来后，人工把 objective/acceptance/结果复制给 Codex |
| 6 | 人工安排 Codex review |
| 7 | review 返回 request_changes 时，人工把意见搬回 WorkBuddy（每次一条，不得压缩） |
| 8 | 人工拼装最终结果 |
| 9 | 异常/权限/方向决策（如有） |

## 下一步

等待 Human 把 objective/acceptance 搬运给 Codex 安排 review；在此之前 Agent 侧先完成实现与编译，产出可复核事实。
