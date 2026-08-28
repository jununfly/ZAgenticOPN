# 方案 A baseline 记录 — 2026-08-28

## 结论

**部分完成：baseline projection 已完成；真实 Human 手动路径未执行/未记录。** `1-3-1` 保持 `in_progress`。本记录不把编译投影当作方案 A 的完整对照实验。

分类：`stage-critical`。该记录只补 Experience Version 退出所缺的方案 A 对照证据，不修改 ZAgenticOPN runtime，也不展开跨设备、自动发现、恢复或生产运维。

## 1. 可复核的 baseline projection

方案 A 的编译基线复用同一份真实 Report IR、sealed ledger 和 brief，仅在隔离临时目录把 `family` 从 `technical-c4/v1` 投影为 `zj-draft/v1`。原始输入、ZAgentic 源 skill、Codex 运行副本和 sibling repo 的既有输出均未修改。

输入：

- Report IR：`/Users/bilibili/Documents/workspace/github/jununfly/ZAgentic/research/multi-device-agent-context/report-ir.json`
- Sealed ledger：`/Users/bilibili/Documents/workspace/github/jununfly/ZAgentic/research/multi-device-agent-context/ledger-response-v2.json`
- Brief：`/Users/bilibili/Documents/workspace/github/jununfly/ZAgentic/research/multi-device-agent-context/brief.json`
- Compiler lock：`/Users/bilibili/Documents/workspace/github/jununfly/ZAgentic/skills/research/zj-research/artifacts/compiler-lock.json`

输入 SHA-256：

| 输入 | SHA-256 |
|---|---|
| `report-ir.json` | `f9a6a3a18bc8040b5a28f90de304861e81da29ff9782cbc9a22824e9767d7de3` |
| `ledger-response-v2.json` | `aa834ce12d3aba534a80b958e4955421aa7b23438106194d7819e56ffec60792` |
| `brief.json` | `7cee9195c68dbeb67e151e86c5bd79066c125ad265f2ddd980914b4ba586a7f5` |
| `compiler-lock.json` | `bcd2c0c87146a17f7e7e650695bd2b23d113029bcd61da230e5562a20a54e091` |

执行方法：

```sh
baseline_dir=$(mktemp -d /tmp/zagenticopn-solution-a-baseline.XXXXXX)
jq '.family = "zj-draft/v1"' \
  /Users/bilibili/Documents/workspace/github/jununfly/ZAgentic/research/multi-device-agent-context/report-ir.json \
  > "$baseline_dir/report-ir-zj-draft.json"
python /Users/bilibili/Documents/workspace/github/jununfly/ZAgentic/skills/research/zj-tech-research-report/scripts/publish_report.py \
  "$baseline_dir/report-ir-zj-draft.json" \
  /Users/bilibili/Documents/workspace/github/jununfly/ZAgentic/research/multi-device-agent-context/ledger-response-v2.json \
  research/activation-routing/2026-08-28-solution-a-baseline.md \
  --receipt research/activation-routing/2026-08-28-solution-a-baseline-receipt.json
```

结果：

| 项目 | 结果 |
|---|---|
| Report family | `zj-draft/v1` |
| Compiler | `zj-research-cli/v1`, `research/v1` |
| Report hash | `64b61f0eef37682371b0dd5d7d32ec67975dfc2ff7220afe9c4f1dad909ad1bb` |
| Compiler evaluation | `healthy=true` |
| Correctness | `revisionPinned/provenanceComplete/criticalClaimsEvidence/scoringAxesSeparated/publishExactlyOnce/receiptConsistent` 全部 `true` |
| Evidence / unknowns | `18 / 0` |
| 生成文件 | [`2026-08-28-solution-a-baseline.md`](2026-08-28-solution-a-baseline.md)、[`2026-08-28-solution-a-baseline.html`](2026-08-28-solution-a-baseline.html)、[`2026-08-28-solution-a-baseline-receipt.json`](2026-08-28-solution-a-baseline-receipt.json) |

生成文件 SHA-256：

| 文件 | SHA-256 |
|---|---|
| `2026-08-28-solution-a-baseline.md` | `64b61f0eef37682371b0dd5d7d32ec67975dfc2ff7220afe9c4f1dad909ad1bb` |
| `2026-08-28-solution-a-baseline.html` | `c6725bc57943c8eac6c5ddbbe26eef4dfc0dee7112725e7ce8bbd323e385e3b1` |
| `2026-08-28-solution-a-baseline-receipt.json` | `5a1e62b795734aeb70791ba609f67783f831aa2bc393a11895f149310761a78d` |

这里的 `healthy=true` 是旧 `zj-draft/v1` 编译器的发布健康结果；它没有运行 `technical-c4/v1` 专用质量门，也不能证明方案 A 的人工 action log 或最终 Git acceptance。

## 2. 同输入的输出形态差异

Experience Version 的已存 improved projection receipt 为 `healthy=true`，report hash 为 `016376572170293bf9fa058d076dac68dea3d525ef01f91467ff1bfa150857e6`；其结果来自同一 Report IR 的 `technical-c4/v1` 发布。

| 观察项 | 方案 A baseline：`zj-draft/v1` | Experience Version：`technical-c4/v1` |
|---|---|---|
| C4 landscape / container 图 | 未渲染 | 2 个图均已渲染 |
| 候选项目表 | 未渲染为结构化表 | 已渲染 |
| 深读项目卡片 | 未渲染 | 3 张卡片 |
| 指标矩阵 | 未渲染 | 6 个 metric |
| graduation criteria | 未渲染 | 3 条机器可核验退出条件已进入 IR/质量 gate |
| 证据与来源 | 18 条 evidence，来源清单可读 | 18 条 evidence，来源清单可读 |
| 编译发布 | `healthy=true` | `healthy=true`，另有 technical quality gate `healthy=true` |

这说明改进前编译器仍能发布可读报告，但没有把同一结构化 IR 稳定投影成技术方案分析所需的 C4、卡片、指标和退出条件；差异是可复核的输出差异，不是对 Human 时间的推定。

## 3. Human 手动路径状态

真实方案 A 必须由 Human 在 Agent 对话之间手动搬运 objective、acceptance 和前序结果，手动派发 WorkBuddy，手动安排 Codex review，并手动拼装最终结果。当前没有可验证的现场时间戳、动作数量、任务特定 prompt、复制内容、dispatch、review 安排、stitching 或异常处理记录。

现场记录模板：[`2026-08-28-solution-a-human-action-log.md`](2026-08-28-solution-a-human-action-log.md)。在模板填实以前，以下指标均为 `NOT RECORDED`：

- Human task-specific prompt / context copy / manual dispatch / review scheduling / result stitching / exception count；
- activation count 和 Human intervention total time；
- 同 acceptance 的方案 A 最终 Git commit、changed files、测试结果和 review 结果。

不能使用 Experience Version 的 activation 事件、Agent runtime 或既有 Git commit 反推出这些字段。

## 4. 当前验收判断

| 验收项 | 判断 |
|---|---|
| 同一真实输入的 `zj-draft/v1` baseline projection | PASS |
| baseline Markdown/HTML/receipt 不覆盖已有输出 | PASS |
| baseline 编译 receipt `healthy=true` | PASS |
| 真实 Human 手动 action log | NOT PROVEN |
| 同 acceptance 的方案 A Git artifact | NOT PROVEN |
| A / Experience Version Human intervention 对照 | NOT PROVEN |
| `1-3-1` 节点 | `in_progress` |

下一步不是修改产品 runtime，而是由 Human 按模板实际运行方案 A 并回填现场记录；发生异常或 review 重试时逐项保留。完成后再更新本记录和对照 scorecard，并通过 roadmap CLI 记录结果。
