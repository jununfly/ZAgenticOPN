# 方案 A 对照窗口审计 — 2026-08-29

## 结论

**方案 A 的对照窗口已被 Experience Version 抢占：同一真实任务已由 OPN 臂交付，计划中的剩余改进动作已归零。** 因此 [`2026-08-28-solution-a-human-action-log.md`](2026-08-28-solution-a-human-action-log.md) 保持未填写，roadmap 节点 `1-3-1` 不能靠现有任务关闭。

分类：`stage-critical`。本次只做只读核对与证据记录，不修改 ZAgenticOPN runtime、不修改 roadmap JSON、不修改 ZAgentic 源 skill 或运行副本、不编译任何新输出。

**本次没有做的事（防止证据污染）**：没有填写 action log 表格的任何一行；没有用 Agent 事件、Git 时间或编译耗时反推 Human action 时间戳；没有把已完成的改进重跑一遍冒充方案 A 的交付。

## 审计触发

Human 指令：`处理任务： research/activation-routing/2026-08-28-solution-a-human-action-log.md`（2026-08-29 00:23 GMT+8）。

审计时间：2026-08-29 00:28 GMT+8。

## 证据

### 1. 固定实验输入仍然存在且未变

| 输入 | 路径 | SHA-256 | 与 preflight 记录是否一致 |
|---|---|---|---|
| Report IR | `ZAgentic/research/multi-device-agent-context/report-ir.json` | `f9a6a3a18bc8040b5a28f90de304861e81da29ff9782cbc9a22824e9767d7de3` | 一致 |
| Sealed ledger | `…/ledger-response-v2.json` | `aa834ce12d3aba534a80b958e4955421aa7b23438106194d7819e56ffec60792` | 一致 |
| Brief | `…/brief.json` | `7cee9195c68dbeb67e151e86c5bd79066c125ad265f2ddd980914b4ba586a7f5` | 一致 |
| Compiler lock | `ZAgentic/skills/research/zj-research/artifacts/compiler-lock.json` | `bcd2c0c87146a17f7e7e650695bd2b23d113029bcd61da230e5562a20a54e091` | 一致 |

四个哈希与 `2026-08-28-solution-a-baseline-record.md` 记录的完全一致，说明"同一真实报告"这个对照输入仍然可用。

### 2. 方案 A 的目标任务已被 Experience Version 交付

| 事实 | 证据 |
|---|---|
| 价值实验一（KEP-753 → `zj-research-report` 改进）已完成并合并 | ZAgentic commit `5a42790 feat(skills): align zj-tech-research-report with KEP-753 steps 7-8 (graduationCriteria + versionSkew)`，经 PR #16 合并入 `main` |
| 后续 review 修订链已闭合 | `e166484`、`325b2d9`、`f3622df`、`b5b0a40 docs(zj-tech-research-report): align graduationCriteria field contract with the gate` |
| 同输入的编译产物与 receipt 已存在 | `ZAgentic/skills-outputs/zj-tech-research-report/kep753-graduation-criteria-2026-08-28-value-exp-1/{report.md,report.html,brief.json,report-receipt.json}` |
| receipt 健康 | `healthy=true`，`reportHash=016376572170293bf9fa058d076dac68dea3d525ef01f91467ff1bfa150857e6`，compiler+quality gate 双 healthy |
| acceptance 列出的 IR 要素均已产出 | `concepts=5, candidates=3, cards=3, claims=9, comparisons=3, recommendations=2, metrics=6, graduationCriteria=3, ledgerEvidence=18` |

也就是说，action log 里写的 acceptance（更新源 skill 与运行副本、IR 输出 Key-Value/C4/卡片/指标矩阵/风险验证链路/建议、同报告重新编译成功、skill 校验通过、receipt healthy）**在 Experience Version 臂已经全部满足**。

### 3. preflight 计划中的"剩余改进"已归零

`2026-08-28-value-experiment-1-zj-research-report-preflight.md`（01:35 GMT+8 快照）把方案 A 的落地动作定为四次 `cp -R` 覆盖 + 一次新编译，其前提是运行副本仍漂移。当前实测：

```
$ diff -rq ZAgentic/skills/research/zj-tech-research-report ~/.codex/skills/zj-research-report
Only in ~/.codex/skills/zj-research-report: ALIAS.md
Only in source/scripts/__pycache__: validate_technical_report.cpython-312.pyc
Files …/validate_technical_report.cpython-313.pyc differ
Only in source/tests/__pycache__: verify_technical_report.cpython-312.pyc
Files …/verify_technical_report.cpython-313.pyc differ
```

- `SKILL.md`：**无差异**。preflight 记录的 line 126 漂移已消失；源与别名两侧第 125/126/128 行均含 `graduationCriteria`、`versionSkew`、结构化 `informationGaps` 契约（grep 双向核对一致）。
- `scripts/validate_technical_report.py`、`tests/verify_technical_report.py`：**无差异**。
- 仅剩 `.pyc` 字节码与 `ALIAS.md`（别名专属文件）差异，均非源码漂移。
- `~/.codex/skills/zj-tech-research-report/`（正名副本）同样只剩 `.pyc` 差异。

结论：方案 A 若现在按原计划执行，源码变更集为空，`changed files` 只会是新建输出目录 —— 这是一次**退化的对照**，不是 preflight 设想的那次改进。

### 4. ZAgentic 仓库状态（只读）

- HEAD：`d1154ea`（= `origin/main`），工作区除 `skills-outputs/zj-tech-research-report/` 下 5 个未跟踪输出目录外干净。
- 未跟踪输出中包含 `kep753-graduation-criteria-2026-08-28-value-exp-1/`（价值实验一产物，尚未 commit）。
- ZAgenticOPN 当前分支：`codex/manual-baseline-a`，HEAD `b640c58 docs(roadmap): record solution A baseline`。

### 5. 既有对照证据盘点

| 项 | 状态 |
|---|---|
| 同输入 `zj-draft/v1` baseline projection | 已产出，`healthy=true`，report hash `64b61f0e…ad1bb` |
| 方案 A Human action log | **未填写（本次仍不填写）** |
| 方案 A 同 acceptance 的 Git artifact | **不存在，且现有任务已无法产生非空源码变更** |
| Experience Version 三次实验 | C1–C4 PASS，三个独立 commit；价值门中"每次恰好 3 次 activation"观察为 `2/9/4`，Human intervention 未证明 |

## 为什么不能"现在补跑一次"就算方案 A

价值门是「Experience Version 的 Human 总介入时间不明显劣于方案 A」。对照要成立，两臂必须跑**同一个、工作量相当的真实任务**。

现状是：Experience Version 臂跑的是完整的 KEP-753 改进（含设计决策、多轮 request_changes、review 修订链）；方案 A 臂现在能跑的只剩"验证已同步 + 重编译一次"。两者工作量不对等，方案 A 的 Human 时间会被系统性低估，从而让 Experience Version 在一个不公平的对照上被判负。

把这次退化的重跑记进 scorecard，会制造一个**看起来通过、实际无效**的价值门证据 —— 这正是该实验设计要防的那类污染。

## 可选路径

| 选项 | 做法 | 代价 | 证据效力 |
|---|---|---|---|
| **B（推荐）** | 另选一个与 KEP-753 改进工作量相当的真实任务，**先跑方案 A 人工路径**，再让 Experience Version 跑同一任务，两臂用同一份 acceptance 与同一批输入 | 最高：需要一个新的真实任务 + 两轮完整执行 | 有效，可关闭 `1-3-1` 的价值门 |
| **A** | 立即用现有任务跑退化版方案 A：verify sync → `quick_validate.py` → `publish_report.py` 新目录不覆盖 → Human 手工搬运 Codex review → 手工缝合 | 最低，可立刻执行 | 无效对照；只能证明"流程跑通"，不能支撑价值门 |
| **C** | 判定 `1-3-1` 对照窗口已失效，把「Human intervention 不明显劣于方案 A」从 `NOT PROVEN` 转为 `deferred`，节点保持 `in_progress` 并写明阻断原因 | 低 | 诚实，但价值门继续悬空，后续阶段不能推进 |

`quick_validate.py`（skill-creator 系统脚本）与 `publish_report.py` 的路径已定位完毕，选 A 或 B 都可直接执行：

- `~/.workbuddy/plugins/cache/workbuddy-builtin/skill-skill-creator/0.1.0/scripts/quick_validate.py`
- `ZAgentic/skills/research/zj-tech-research-report/scripts/publish_report.py`

## 下一步

等待 Human 在 A / B / C 中决策。选定后：

- 若选 A 或 B：Human 在 action log 现场逐行记录开始/结束时间，我执行 agent 侧命令并回传可复核输出（commit SHA、changed files、测试命令与结果）；review 由 Human 手工搬运给 Codex，结果由 Human 手工缝合。
- 任何选项确定后，再通过 `zj-roadmap-driven` 把结论写入 roadmap JSON 并渲染，不直接编辑 JSON 或渲染后的 Markdown。

## Source pointers（只读）

- `research/activation-routing/2026-08-28-solution-a-human-action-log.md`
- `research/activation-routing/2026-08-28-solution-a-comparison-scorecard.md`
- `research/activation-routing/2026-08-28-experience-version-scorecard.md`
- `research/activation-routing/2026-08-28-value-experiment-1-zj-research-report-preflight.md`
- `docs/plans/agent-self-service-collaboration-roadmap.md`（节点 `1-3-1`）
