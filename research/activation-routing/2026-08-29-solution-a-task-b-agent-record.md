# 方案 A 任务 B — Agent 侧可复核记录 — 2026-08-29

## 结论

**Agent 侧实现与编译已完成并通过两个 gate；已经历两轮硬违规（r2 占位符漏检、r3 词汇未同步）与一轮判断项（r4 测试重复代码）并修复重验。方案 A 仍未闭合，等 Human 继续手工搬运与安排 review。** 本文件只记录机器可复核事实，**不包含任何 Human 时间戳** —— Human action 的时间戳只能由 zj 在 [`2026-08-28-solution-a-human-action-log.md`](2026-08-28-solution-a-human-action-log.md) 现场填写。

分类：`stage-critical`。任务定义与执行包见 [`2026-08-29-solution-a-task-b-kit.md`](2026-08-29-solution-a-task-b-kit.md)。

## 分支与基线

| 项 | 值 |
|---|---|
| 仓库 | `ZAgentic`（不是 ZAgenticOPN 产品仓库） |
| 基线 commit | `d1154ea3f4bcd0f5dcf2b0855ebc3ad735942f1d` |
| 方案 A 分支 | `solution-a/kep753-risk-register` |
| 提交 1 | `93c17b78591a101450f270a35e2da5eed4d02611`（短 `93c17b7`）— `feat(zj-tech-research-report): enforce machine-checked riskRegister contract (KEP-753 step 4)`；5 文件 +152/−75 |
| 提交 2 | `5942550e928dd97d887bdff35ad07d79f22e404b`（短 `5942550`）— `fix(zj-tech-research-report): close risk register review findings`；4 文件 +55/−8（r6 复述归一化 + r7 渲染限制契约文本） |
| 提交状态 | **两个 commit 均已推送**至 `origin/solution-a/kep753-risk-register`，**未合并 main**；提交 2 是**追加**提交，未改写已推历史 |
| 同步状态 | `## solution-a/kep753-risk-register...origin/solution-a/kep753-risk-register`（无 ahead/behind），tracked 工作区干净 |

## Changed files

```
 M ZJ-CONTEXT.md                                                                     |  19 +++-
 M skills/research/zj-tech-research-report/SKILL.md                                  |   3 +-
 M skills/research/zj-tech-research-report/references/technical-proposal-exemplar.md |   4 +-
 M skills/research/zj-tech-research-report/scripts/validate_technical_report.py      |  27 +++
 M skills/research/zj-tech-research-report/tests/verify_technical_report.py          | 174 +++++++++++------
 5 files changed, 152 insertions(+), 75 deletions(-)
```

（上表是**提交 1（`93c17b7`）**的变更集：r1 为 `18`/`85`，r2 为 `27`/`123`，r3 追加 `ZJ-CONTEXT.md`，r4 是测试重构去重。提交 2（`5942550`）另含 4 文件 +55/−8，对应 r6 与 r7。明细见文末 review rounds r2–r7。）

新增未跟踪输出目录两个：`kep753-risk-register-2026-08-29-solution-a/`（r1）与 `kep753-risk-register-2026-08-29-solution-a-r2/`（r2）。

## 实现内容

| 文件 | 改动 |
|---|---|
| `SKILL.md` §4 | 风险登记要求改为指向结构化字段：「Encode the risk register as the top-level `riskRegister` field … a risk described only in prose does not satisfy it」 |
| `SKILL.md` §5 | 新增 `riskRegister` 契约条目，位于 `metrics` 与 `graduationCriteria` 之间：`{risk, trigger, impact, mitigation, residualRisk, owner}` 六字段全必填非空；mitigation 复述 risk 会被拒；`owner` 必须是角色/责任方而非 TBD |
| `references/technical-proposal-exemplar.md` | step 4 行改为机器可核验描述；表头改为「Steps 4, 7, and 8 also have a machine-checked Report IR contract」 |
| `scripts/validate_technical_report.py` | 新增 `RISK_FIELDS` 常量、`riskRegister` 非空列表校验、逐项六字段校验、mitigation-restates-risk 拒绝；新增 `riskRegisterCoverage` check 与 `counts.riskRegister` |
| `tests/verify_technical_report.py` | fixture 注入 `valid_risk_register()`（2 条），新增正例断言（`counts.riskRegister == 2`、`riskRegisterCoverage is True`）与 3 个反例（空列表 / owner 为空 / mitigation 复述 risk），每个反例都断言未产生任何发布文件 |

## 测试命令与结果

| 命令 | 结果 |
|---|---|
| `python3 tests/verify_technical_report.py`（源 skill 目录） | **PASS**，`technical research-report contract passed`，2.6s |
| `python3 ~/.workbuddy/plugins/cache/workbuddy-builtin/skill-skill-creator/0.1.0/scripts/quick_validate.py skills/research/zj-tech-research-report` | **PASS**，`Skill is valid!` |
| 同上，对 `~/.codex/skills/zj-research-report` | **PASS**，`Skill is valid!` |

## 固定输入未被修改

| 输入 | SHA-256 | 是否变化 |
|---|---|---|
| `research/multi-device-agent-context/report-ir.json` | `f9a6a3a18bc8040b5a28f90de304861e81da29ff9782cbc9a22824e9767d7de3` | 未变 |
| `research/multi-device-agent-context/ledger-response-v2.json` | `aa834ce12d3aba534a80b958e4955421aa7b23438106194d7819e56ffec60792` | 未变 |
| `research/multi-device-agent-context/brief.json` | `7cee9195c68dbeb67e151e86c5bd79066c125ad265f2ddd980914b4ba586a7f5` | 未变 |
| `skills/research/zj-research/artifacts/compiler-lock.json` | `bcd2c0c87146a17f7e7e650695bd2b23d113029bcd61da230e5562a20a54e091` | 未变 |

派生 IR 写在输出目录内，原输入零改动。brief 取自源 skill 自带测试夹具的 `valid_brief()`（决策框架），不是取自 Experience Version 臂的产物。

## 运行副本同步

```
rsync -a --delete --exclude '__pycache__' --exclude 'ALIAS.md' \
  skills/research/zj-tech-research-report/ <dest>/
```

| 目标 | 同步后 `diff -rq` |
|---|---|
| `~/.codex/skills/zj-research-report/`（运行别名） | 只剩 `.pyc` 与 `ALIAS.md` |
| `~/.codex/skills/zj-tech-research-report/`（正名副本） | 只剩 `.pyc` |

运行别名目录名未改；`ALIAS.md` 保留。

## 编译发布

```sh
python3 skills/research/zj-tech-research-report/scripts/publish_report.py \
  skills-outputs/zj-tech-research-report/kep753-risk-register-2026-08-29-solution-a/report-ir-risk-register.json \
  research/multi-device-agent-context/ledger-response-v2.json \
  skills-outputs/zj-tech-research-report/kep753-risk-register-2026-08-29-solution-a/report.md \
  --receipt .../report-receipt.json --brief .../brief.json
```

| 项 | 结果 |
|---|---|
| report family | `technical-c4/v1` |
| compiler | `research/v1`，`publishCount=1`，`cacheHit=false` |
| `healthy` | `true`（编译器 evaluation 与 `technical-research-quality-gate/v1` 双健康） |
| correctness | `revisionPinned` / `provenanceComplete` / `criticalClaimsEvidence` / `scoringAxesSeparated` / `publishExactlyOnce` / `receiptConsistent` 全为 `true` |
| quality gate checks | 8 项原有 check + **`riskRegisterCoverage: true`** |
| counts | `concepts=5, candidates=3, cards=3, claims=9, comparisons=3, recommendations=2, metrics=6, riskRegister=4, ledgerEvidence=18, ledgerUnknownCriteria=0, graduationCriteria=3` |
| reportHash | `016376572170293bf9fa058d076dac68dea3d525ef01f91467ff1bfa150857e6` |

输出文件 SHA-256：

| 文件 | SHA-256 |
|---|---|
| `brief.json` | `72c769b35a8d1b37be383be93a25d60151ca780c3c0c4eb9ad877ef9bbff035b` |
| `report-ir-risk-register.json` | `3ad7b8a0227ba9b79bba7f424e9eeb9c9b180a0c9ae8555a90da451b916c0904` |
| `report.md` | `016376572170293bf9fa058d076dac68dea3d525ef01f91467ff1bfa150857e6` |
| `report.html` | `083318db48397da85d84d01311f17f28b1d3fba86410d5611fa08a2455c3fa24` |
| `report-receipt.json` | `67d16cf28cda36996cb29da4520964ee2b9050e14891a52d652d11ac09e5df39` |

既有输出未被覆盖（`skills-outputs/zj-tech-research-report/` 下 8 个目录全部保留，本次为新建第 9 个）。

## 必须隔离追踪的偏差（不静默接受）

**`riskRegister` 只进入质量门，没有进入渲染。** 编译器 `zj-research-cli/v1` 忽略未渲染的顶层 IR 字段，因此：

- 新报告 `report.md` 中 `risk` 出现次数 = 0，风险登记对报告读者不可见；
- `report.md` 与 `report.html` 与 Experience Version 臂 value-exp-1 的输出**逐字节相同**，reportHash 也因此相同。

这不是本次引入的新缺陷，而是既有形态：`graduationCriteria`（价值实验一的新增字段）同样只进质量门、不进渲染，且原报告本身完全没有风险内容（grep `risk` = 0）。但要让 acceptance 里写的「风险/验证链路」真正出现在报告里，必须改共享编译器 `skills/research/zj-research/` 的渲染层 —— **超出本任务范围**（任务范围只允许 `zj-tech-research-report/` 源 skill、必要输入和运行副本）。

Codex review 已就此提出 `[P1/部分]`：**gate 通过 ≠ 读者可见**。该判定成立，且比本段的原始表述更准。**完整诊断与处置见文末 review round r7**（含渲染器归属的硬证据：渲染器是 ZHarness 的固定产物，不在本任务范围内，因此不存在范围内修复路径）。

## Review round r2 — Standards 硬违规：`owner: "TBD"` 仍然通过

**违规成立。** review 指出 `owner: "TBD"` 能通过 validator，而契约明令禁止。根因：校验只调用了 `nonempty()`，`"TBD"` 是非空字符串，因此放行 —— 「非空」不等于「有内容」，和 `informationGaps` 那次是同一类漏洞。

修复（不缩小为只堵 owner，而是堵整个字段集）：

| 文件 | 改动 |
|---|---|
| `scripts/validate_technical_report.py` | 新增 `PLACEHOLDER_VALUES`（`tbd/tba/tbc/n-a/na/none/null/nil/unknown/?/-/--/待定/未定/未知/无/暂无/不清楚`）；六字段校验从「仅非空」升级为「非空 **且** 非占位符」，命中即报 `…is a placeholder, not real content` |
| `SKILL.md` §5 | 契约改为：`owner` 必须命名承担残余风险的角色或责任方，占位符在**六个字段全部**被拒 |
| `tests/verify_technical_report.py` | 新增 2 个反例：`owner="TBD"`、`mitigation="待定"`，均断言被拒且零发布文件 |

实测（对真实 IR 打探针，走固定输入）：

```
probe owner='TBD'      -> rc=1  report.riskRegister[0].owner is a placeholder, not real content
probe owner='待定'      -> rc=1  report.riskRegister[0].owner is a placeholder, not real content
probe mitigation='N/A' -> rc=1  report.riskRegister[0].mitigation is a placeholder, not real content
```

真实 fixture 的四个 owner 均为真实角色（`Human Lead（发布治理）`、`Pilot operator` ×3），不触发该规则。

### r2 重新验证

| 命令 | 结果 |
|---|---|
| `python3 tests/verify_technical_report.py` | **PASS** |
| `quick_validate.py`（源 + 别名） | **双 PASS** |
| 两份 codex 副本 rsync 后 `diff -rq` | 只剩 `.pyc` / `ALIAS.md` |
| `publish_report.py` → `kep753-risk-register-2026-08-29-solution-a-r2/` | 编译器 + 质量门**双 healthy**，`riskRegisterCoverage=true`，`counts.riskRegister=4`，reportHash `01637657…` |

r1 输出目录**未被覆盖**（`publishExactlyOnce`），r2 作为独立修订轮产物保留：

| 文件 | SHA-256 |
|---|---|
| `report.md` | `016376572170293bf9fa058d076dac68dea3d525ef01f91467ff1bfa150857e6`（与 r1 相同，因编译器不渲染该字段） |
| `report.html` | `083318db48397da85d84d01311f17f28b1d3fba86410d5611fa08a2455c3fa24` |
| `report-receipt.json` | `68b1786e33137b6ae4fd557c88b56ad86eb6b259470dc0bd12e74800e163a947` |

### 修订后变更集

```
 skills/research/zj-tech-research-report/SKILL.md                                  |   3 +-
 skills/research/zj-tech-research-report/references/technical-proposal-exemplar.md |   4 +-
 skills/research/zj-tech-research-report/scripts/validate_technical_report.py      |  27 +++
 skills/research/zj-tech-research-report/tests/verify_technical_report.py          | 123 ++++
 4 files changed, 154 insertions(+), 3 deletions(-)
```

反例总数：5 个（空列表 / owner 空白 / owner=`TBD` / mitigation=`待定` / mitigation 复述 risk）。

## Review round r3 — Standards 硬违规：新增词汇未同步 `ZJ-CONTEXT.md`

**违规成立。** `AGENTS.md` PR checklist 第 3 条（Vocabulary sync）：「any new domain term introduced in the PR must be added to `ZJ-CONTEXT.md` before merge」。本 PR 引入 `riskRegister` 与 `riskRegisterCoverage` 两个新领域词汇，r1/r2 都没有同步。

修复（`ZJ-CONTEXT.md`，Skills meta 段，紧邻 Technical Research Quality Gate）：

| 动作 | 内容 |
|---|---|
| 新增词条 **Risk Register** | `riskRegister` 字段定义、六必填字段、复述与占位符拒绝、KEP-753 step 4 归属；`_Avoid_`: risk prose / risk section / recommendation follow-up / risk table |
| 新增词条 **Risk-register coverage** | `riskRegisterCoverage` 检查定义、`counts.riskRegister` 计数，并**明写它不是渲染**——共享编译器不渲染该字段，通过检查不等于读者可见 |
| 修正已有词条 **Technical Research Quality Gate** | 校验项清单补入 **Risk Register**，否则该词条会因漏列新检查而变成过期描述（同一规则的二次违规） |

顺带核对 PR checklist 另两条，均无需动作：

| 条 | 判断 |
|---|---|
| 1 Plugin registration | **PASS** —— 本次只改已登记 skill 内部文件，未新增 skill；`zj-tech-research-report` 已在 `README.md:288` 与 `skills/research/README.md:9` 双向登记 |
| 2 Safe git operations | **N/A** —— 本次无破坏性 git 操作；分支创建走普通 git，未触发 Windows safe-delete shim 场景 |

`ZJ-CONTEXT.md` 是文档，不影响编译与 receipt，因此 **r2 的发布产物保持有效，未重新发布**。回归：`python3 tests/verify_technical_report.py` **PASS**。

## Review round r4 — 判断项：拒绝发布流程重复，抽取辅助函数

**判断成立，已采纳。** 每个反例都是同一段 15 行样板（deepcopy → write → run publisher → 查 stderr → 断言零发布文件），新增 5 个 riskRegister 反例后全文件有 **10 处**同构块。

修复：新增 `assert_rejected(root, stem, report_path, ledger_path, brief_path, expected_error)`，把「发布必须被拒 + 被拒后不留任何文件」收进一处；把 **全部 10 处**（含 5 处既有 informationGaps / brief / claim 反例）统一改为调用它。

| 项 | 结果 |
|---|---|
| 文件行数 | **402 → 310（−92）** |
| 反例调用点 | 10 处，每处 4 行 |
| 断言语义 | **未变** —— 同样的 stem、同样的期望错误子串、同样的零文件断言；失败信息改为 `publisher did not reject {stem} with: {expected_error}`，比原来更定位 |
| 回归 | `python3 tests/verify_technical_report.py` **PASS** |
| 副本同步 | 两份 codex 副本重新 rsync，只剩 `.pyc` / `ALIAS.md` |
| `quick_validate.py` | 源 + 别名**双 PASS** |

要不要扩到既有块：抽了只服务新块、却让文件一半新一半旧，比不改更糟；所以一次做到底。

**反向自检（证明重构没把测试变成空转）：** 临时把 `validate_technical_report.py` 里的 `risk_items = require_list(...)` 短路掉，测试必须失败 —— 实测 `rc=1`，`receipt did not count the machine-checked risk register`。源码已完整还原（`grep 'if False:'` 无残留）。

`tests/` 不参与发布路径，**r2 的发布产物保持有效，未重新发布**。

## Acceptance 7 状态：已闭合

Spec review 曾判定 **P1** 未闭合。Human 于 2026-08-29 01:46 GMT+8 触发 `commit+push` 后，三项全部齐备：

| 子项 | 状态 |
|---|---|
| changed files | **已记录**（本文件 Changed files 段），并与提交实际一致：5 文件 `+152/−75` |
| 测试命令与结果 | **已记录**（本文件测试命令与结果段 + r2/r3/r4 三轮回归） |
| commit SHA | **`93c17b78591a101450f270a35e2da5eed4d02611`**（短 `93c17b7`），已推送 `origin/solution-a/kep753-risk-register` |

**注意：有 artifact ≠ 价值门已过。** 本次提交只证明方案 A 臂产出了同 acceptance 的可复核 Git artifact；Human action log 仍然全空，Human intervention 对照依旧 `NOT PROVEN`。对照 scorecard 已同步该区分。

### 提交前预演（已完成）

| 检查项 | 结果 |
|---|---|
| 分支 | `solution-a/kep753-risk-register`，基线 `d1154ea` |
| 待提交文件 | 恰好 5 个 tracked 修改：`ZJ-CONTEXT.md`、`SKILL.md`、`technical-proposal-exemplar.md`、`validate_technical_report.py`、`verify_technical_report.py` |
| 未跟踪输出 | 7 个 `skills-outputs/` 目录 —— **不进本次提交**（含另一臂 `kep753-graduation-criteria-2026-08-28-value-exp-1/` 与 4 个 20260827 旧产物） |
| 残留临时文件 | 无（`git status --porcelain` 除 `M`/`??` 外无其他条目） |
| git 操作通道 | `./scripts/zj-git` 存在且可执行（AGENTS.md PR checklist 第 2 条） |
| 回归 | `python3 tests/verify_technical_report.py` PASS；`quick_validate.py` 源 + 别名双 PASS |
| 副本一致性 | 两份 codex 副本只剩 `.pyc` / `ALIAS.md` 差异 |

### 提交计划（已于 2026-08-29 01:46 GMT+8 执行完毕）

```sh
# 1) ZAgentic —— 先提交，拿到 SHA
cd /Users/bilibili/Documents/workspace/github/jununfly/ZAgentic
./scripts/zj-git add ZJ-CONTEXT.md \
  skills/research/zj-tech-research-report/SKILL.md \
  skills/research/zj-tech-research-report/references/technical-proposal-exemplar.md \
  skills/research/zj-tech-research-report/scripts/validate_technical_report.py \
  skills/research/zj-tech-research-report/tests/verify_technical_report.py
./scripts/zj-git commit -m "feat(zj-tech-research-report): enforce machine-checked riskRegister contract (KEP-753 step 4)"

# 2) 我拿 SHA 回填本文件与 2026-08-28-solution-a-comparison-scorecard.md

# 3) ZAgenticOPN —— 后提交记录
cd /Users/bilibili/Documents/workspace/github/jununfly/ZAgenticOPN
./scripts/zj-git add research/activation-routing/2026-08-28-solution-a-human-action-log.md \
  research/activation-routing/2026-08-29-solution-a-window-audit.md \
  research/activation-routing/2026-08-29-solution-a-task-b-kit.md \
  research/activation-routing/2026-08-29-solution-a-task-b-agent-record.md
./scripts/zj-git commit -m "docs(research-output): record solution A task B agent-side evidence"
```

顺序原因：记录文件要引用 ZAgentic 的 commit SHA，SHA 必须先存在；否则又会出现「文档引用不存在的 hash」这类自指问题。

## Review round r5 — P1「owner 的 TBD 禁止未实现/未覆盖」：证伪，根因是 ref 不一致

**判定：在方案 A 分支上该 P1 不成立；在 `main` 上它成立 —— 因为分支尚未合并。** review 读到的应当是不含本变更的 ref。

### 分支上已实现且已覆盖（可复核）

| 位置 | 证据 |
|---|---|
| 校验器 `scripts/validate_technical_report.py:22` | `PLACEHOLDER_VALUES = {...}`（`tbd/tba/tbc/n-a/na/none/null/nil/unknown/?/-/--/待定/未定/未知/无/暂无/不清楚`） |
| 校验器 `:233-234` | `elif str(value).strip().casefold() in PLACEHOLDER_VALUES:` → `…{field} is a placeholder, not real content`，对**全部六个字段**生效，含 `owner` |
| 测试 `tests/verify_technical_report.py:281-285` | `tbd_owner["riskRegister"][0]["owner"] = "TBD"` → `assert_rejected(..., "riskRegister[0].owner is a placeholder")` |
| 测试 `:287-291` | `mitigation = "待定"` → `assert_rejected(..., "riskRegister[1].mitigation is a placeholder")` |
| 契约 `SKILL.md:125` | 「`owner` must name the role or party that carries the residual risk, not "TBD"; placeholders (`TBD`, `N/A`, `unknown`, `待定`, and similar) are rejected in **all six** fields」 |
| 运行副本 | `~/.codex/skills/zj-research-report/` 与 `~/.codex/skills/zj-tech-research-report/` 两份均含该修复（`grep -c "is a placeholder"` = 1 / 1） |
| commit | `93c17b7` 已含上述全部内容，并推送至 `origin/solution-a/kep753-risk-register` |

### 定向变异测试（证明断言不是空转）

只把 `:233` 的 `elif str(value)... in PLACEHOLDER_VALUES:` 改成 `elif False:`，其余不动，测试**必须**失败。实测：

```
rc = 1
technical report contract: publisher did not reject tbd-owner with: riskRegister[0].owner is a placeholder
```

源码已完整还原，工作区 tracked 文件无改动。

### 根因：review 与实现不在同一个 ref

| ref | `PLACEHOLDER_VALUES` | 测试含 `TBD` | 合并进 `main` |
|---|---|---|---|
| `solution-a/kep753-risk-register` | 2 处 | 1 处 | — |
| `main` | **0** | **0** | **否** |

分支未合并进 `main`，所以任何按默认分支解析的读者都会正确报出「未实现」。

### 为什么现在不合并（这是设计约束，不是拖延）

两臂隔离是本实验的**根修复**：方案 A 与后续 Experience Version 臂各自从同一基线 `d1154ea` 出发、在独立分支上完成同一任务、互不参考对方产物。若现在把 `solution-a/kep753-risk-register` 合进 `main`，Experience Version 臂的基线就会包含方案 A 的实现，它再跑同一任务将无事可做 —— 正是本轮最初诊断出的「先跑臂抢占任务」退化对照。

因此该 P1 的正确处置是二者之一：

1. **把 review 指向分支** `solution-a/kep753-risk-register`（推荐，零风险）；
2. 若 review 必须基于 `main`，则把该项标为 `deferred-until-merge`，owner 记为方案 A，等两臂对照收口、选定落地臂后再合并。

## Review round r6 — P2「mitigation 仅拒绝完全相等文本」：成立，按"只做安全的一半"修

**判定成立，部分修复。** 原实现是 `str(mitigation).strip().casefold() == str(risk).strip().casefold()`，只比到 strip+忽略大小写。加个句号、改个空格就能绕过 —— 属实。

### 修了什么

| 文件 | 改动 |
|---|---|
| `validate_technical_report.py` | 新增 `content_key()`（`re.sub(r"\W", "", s.casefold())`）与 `_NON_CONTENT_RE`；复述判定改为 `content_key(mitigation) == content_key(risk)` —— **标点、空白、大小写全部不计**，"加句号"这条绕过路径关闭 |
| `tests/verify_technical_report.py` | 新增反例 `punctuated-restated-risk`（mitigation = risk + `"."`）必须被拒；新增**正例** `quoted-risk`（mitigation 先引用 risk、再写出机制与审计手段）必须**放行** |
| `SKILL.md` §5 | 契约写明：门只比内容，加句号/改空格仍算复述；**并且明确它是精确匹配而非模糊匹配** |
| `ZJ-CONTEXT.md` | Risk Register 词条同步（避免重蹈 r3 的词汇未同步） |

### 刻意没做的那一半，以及为什么

**没做**模糊相似度 / 包含判定。理由是不对称代价：

- 漏放（lazy mitigation 混过门）→ 到 review 层还能被发现，成本可接受；
- 误拒（合法 mitigation 被门拦下）→ **直接阻断发布**，而且拦的是已经写对了的报告。

而"引用 risk 原文再补机制"恰恰是合法 mitigation 的常见写法：risk `记忆层被当成控制面：…`，mitigation `…contained by read-only grants and a nightly bypass audit`。任何包含判定或相似度阈值都会先命中这一类。所以我把边界定死在**逐字复述**上，并把"换句话复述、但没写机制"明确划给 review 层 —— 那本来就是 review 存在的理由。

为此专门加了一个**正例测试**把这条边界钉住：将来谁想加包含/相似度规则，这个测试会先失败。

### 验证

| 项 | 结果 |
|---|---|
| 回归 | `python3 tests/verify_technical_report.py` **PASS** |
| 定向变异（把比较退回 `strip().casefold()`） | `rc=1`，`publisher did not reject punctuated-restated-risk with: mitigation restates the risk` —— 证明新测试精确守在新行为上；源码已还原 |
| 副本同步 | 两份 codex 副本只剩 `.pyc` / `ALIAS.md` |
| `quick_validate.py` | 源 + 别名双 PASS |
| r6 重新发布 | `kep753-risk-register-2026-08-29-solution-a-r6/`：编译器 + 质量门双 healthy，`riskRegister=4`，`riskRegisterCoverage=true`，reportHash `01637657…`，receipt SHA-256 `9fda5d54…` |

输出目录与 review 轮次对齐：**r1**（初版）/ **r2**（占位符修复）/ **r6**（复述归一化）。r3（文档）、r4（测试重构）未改变 gate 行为，故不产新 artifact。

## Review round r7 — P1/部分「IR 有 4 条风险且 gate 通过，但产物不展示风险登记」

**判定成立。** 而且 reviewer 的表述比我在 r1 埋的那段 open item 更准确：**healthy receipt 只证明门过了，不证明读者看得见**。这一条此前是「已知但表述偏软」，现在按 P1 处理。

### 硬证据：渲染器不在本任务范围内，甚至不在本仓库

| 事实 | 证据 |
|---|---|
| 编译器是**外部固定产物** | `skills/research/zj-research/artifacts/compiler-lock.json`：repository `github.com/jununfly/ZHarness`，commit `9172aa0`，artifact `dsh-research-cli-9172aa0.tgz`，sha256 `e5297042ca080e3489969999b5f7094c1867da646f1c91a0a971a35ce9ecd21d` |
| 渲染走 `zj-research-cli/v1` 协议的两个 operation | `publish_report.py:88` `compile-report` → `publish_report.py:94` `render-html` |
| **编译器完全不认识这两个字段** | 在该锁定产物（`~/.cache/zj-research/compiler/e5297042…/`）内 grep：`graduationCriteria` **0 次**，`riskRegister` **0 次** |
| 它渲染的是固定字段集 | 同一产物内仅出现 `concepts / diagrams / candidates / cards / claims / comparisons / recommendations / metrics`，**没有配置项可开** |

所以这不是「改 `skills/research/zj-research/` 就能解决」，而是需要 **ZHarness 上游改渲染 + 出包 + 抬锁版本**。跨仓库发布，远超本实验范围。

### 为什么没有范围内绕行方案

| 绕法 | 为什么不采用 |
|---|---|
| 编译后补写 Markdown/HTML | `SKILL.md` §6 明令禁止：「Never hand-author or edit a competing Markdown or HTML version」 |
| 把风险塞进 `concepts` / `claims` 让它被渲染 | 语义污染；且 `claims` 必须挂 ledger Evidence ID，风险条目没有证据来源，会反过来触发门自己的可追溯性检查 |
| 写进 `recommendations` 散文 | 正是 `informationGaps` 那次回归明确否掉的「散文不等于契约」 |

### 处置：拆成两件事，不混为一谈

1. **不阻塞 `1-3-1`。** 该节点测的是 **Human intervention**，不是报告信息丰富度。风险登记不可见是 skill 的渲染缺陷，与两臂对照正交，拿它卡住阶段退出属于把两个问题绑死。
2. **acceptance 的「风险/验证链路」这一项判为未达成**，作为 deferred 记录，并指定上游依赖：
   - 依赖：`ZHarness@9172aa0` → 渲染层支持 `riskRegister`（以及既有同样不渲染的 `graduationCriteria`）
   - 建议单独立 Work Item（仓库 `jununfly/ZHarness`），不在本实验内做

### 范围内已做的补救：把这个假设钉死在契约里

不能再让「gate 通过 = 报告里有」这个错误假设靠口头传递，所以写进了文本：

| 文件 | 内容 |
|---|---|
| `SKILL.md` §6 | 新增：「A healthy receipt is **not** proof that everything in the IR reached the reader」——点名渲染器是锁定产物（ZHarness `9172aa0`）、列出固定渲染字段集、`graduationCriteria` 与 `riskRegister` 属于「契约强制但不渲染」，并禁止用后处理补偿 |
| `ZJ-CONTEXT.md` | **Risk Register** 词条补交叉引用（「不渲染，见 Risk-register coverage」），并修正 r6 遗留的换行；**Risk-register coverage** 词条原本已写明该限制 |

### 验证

`quick_validate.py` 源 + 别名双 PASS；`tests/verify_technical_report.py` PASS；两份副本同步后只剩 `.pyc` / `ALIAS.md`。**gate 行为未变**（本次只动契约文本），故不产新 artifact。

**落地**：r6 + r7 的变更由 Human 于 2026-08-29 02:14 GMT+8 以追加提交 `5942550e928dd97d887bdff35ad07d79f22e404b` 推送，**未改写已推的 `93c17b7`**。已交 Codex review。

## 下一步（Human 动作，Agent 不得代填）

1. zj 把 objective / acceptance / 本记录的结果手工复制给 Codex；
2. zj 手工安排 Codex review；
3. review 若 request_changes，每条意见单独搬回 WorkBuddy，**每次一行，不得压缩成一次成功**；
4. zj 手工拼装最终结果；
5. 全程由 zj 在 action log 现场填写开始/结束时间；
6. ~~确认后由 zj 显式 `commit+push`，再把 commit SHA 回填本文件。~~ **已完成**（`93c17b7` + `5942550`），SHA 已回填本文件。

方案 A 全程未使用 OPN shared context，也未调用 activation runner —— 这是方案 A 的定义约束。

## Source pointers

- `2026-08-29-solution-a-task-b-kit.md`（任务定义与执行包）
- `2026-08-29-solution-a-window-audit.md`（为何换任务）
- `2026-08-28-solution-a-human-action-log.md`（Human 现场记录模板）
- `2026-08-28-solution-a-comparison-scorecard.md`（待回填的对照 scorecard）
