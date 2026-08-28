# Experience Version 三次实验 scorecard — 2026-08-28

## 结论

**Experience Version 退出：未通过；继续停留在当前阶段。**

三个独立真实 Work Item 的最终交付都已完成并经过另一 Agent review，证明了同设备、单项目路径能够产出可追溯 Git artifact。但这还不足以证明产品价值已经满足退出条件：严格事件窗口没有形成每次恰好三次 activation 的证据，当前 shared context 没有完整的 Human 介入记录，也没有方案 A 的对照基线。

本记录分类为 `stage-critical`。它只聚合已有 shared SQLite、roadmap 决策和 canonical Git references；不修改 ZAgenticOPN runtime，不展开跨设备、自动发现、恢复或生产运维。

## Evidence boundary

- Product scope: `jununfly/ZAgentic/zj-research-report`
- Shared store: `.zagenticopn/shared.sqlite3`
- Event source: events sequence 105–156，以及 C2 竞争事件 sequence 22–25
- 三个最终 Work Item 均为独立对象，并且各自有独立 Git artifact；blocked 的 preflight/configuration Work Item 不计入三次最终交付
- 当前 ZAgenticOPN seam regression: `python -m unittest discover -s tests -v` → **28 passed / 0 failed / 0 errors**

## 三次真实实验

| 实验 | 最终 Work Item | 事件窗口 | 最终 Git artifact | 交付/审阅 | activation 观察 |
| --- | --- | --- | --- | --- | --- |
| 1 | `work-value-experiment-1-zj-research-report-20260828-rerun` | 105–112 | `5a4279079f7d2ac05cffbb60d1d6055c913c9845`；3 个 source/validation/output 文件 | `completed/met`；Codex review accept | 2 个与该 Work Item 关联的 activation：WorkBuddy execution、Codex review |
| 2 | `work-value-experiment-2-zj-tech-research-report-20260828` | 113–137 | `f3622df1cbaf09f20569a5fd5f1635098b553363`；doc-only `technical-decision-brief.md` 及四处 runtime mirror | `completed/met`；两次 request_changes 后 Codex review accept | 窗口内 9 个 distinct activation；3 次 execution claim、3 次 review claim；另有 no-eligible 探活 |
| 3 | `work-value-experiment-3-technical-proposal-exemplar-20260828-rerun` | 142–156 | `f01fa1bb1abfab576e6de457d0bc7f5e2aa19f76`；`technical-proposal-exemplar.md` | `completed/met`；一次 request_changes 后 Codex review accept | 4 个 distinct activation；2 次 execution claim、2 次 review claim |

实验一最终 artifact 的 receipt 记录 `healthy=true` 和 `reportHash=016376572170293bf9fa058d076dac68dea3d525ef01f91467ff1bfa150857e6`；实验二四处 brief 的 SHA-256 为 `e219439c019e4d6d40a476f8ffe19ee98f68896061214f0efca1cff7a900e9f2`；实验三四处 runtime copy 的 SHA-256 为 `d32020b1c67420851c2c5b86e7e717af883b51029cf1857394d72f2fd488282c`。

## Hard gates

| Gate | 判断 | 证据 |
| --- | --- | --- |
| C1 publish/discover | PASS | 三个最终 Work Item 都有 publish、task-agnostic discover 和 execution claim；协议 scorecard 的 C1 也为 PASS |
| C2 competing claim，无重复执行 | PASS | 竞争窗口 sequence 22–25 产生一个 `claim_succeeded` 和一个 `claim_conflict`；当前黑盒测试全通过 |
| C3 readable result/provenance | PASS | 三个最终 Work Item 均为 `acceptance_status=met`，并发布 commit、changed files、tests 引用 |
| C4 review continuation | PASS | 三个最终 Work Item 都由 Codex 从 shared context 发现并 claim review；request_changes 后的修订链最终均被 accept |
| Final Git artifact | PASS（逐项） | 三个独立 commit、独立 changed files 和对应验证结果均已记录；没有把 activation-routing 结果 markdown 当作实验交付物 |

## Value gates

| Value condition | 判断 | 结论依据 |
| --- | --- | --- |
| 任务特定 prompt、上下文复制、人工派发、结果缝合为 0 | NOT PROVEN | 事件 payload 能证明 activation/claim/result/review，但不保存 Human prompt、复制、派发或缝合行为；roadmap 有流程约束，却没有三次实验的逐次 action log |
| 每次恰好 3 次任务无关 activation | FAIL / NOT PROVEN | 最终事件窗口观察到 2、9、4 个 distinct activation；实验二的修订链明确产生额外 execution/review activation，不能按一次最终 accept 折算为三次 |
| Human 总介入时间不明显劣于方案 A | NOT PROVEN | 仓库和 shared context 未找到方案 A baseline 的同任务计时、介入分类或对照 scorecard |
| 连续 3 次真实任务实验 | PARTIAL | 三个独立 Work Item 均完成并有真实 artifact，但上面三个价值条件未同时通过，因此不能升级为 Experience Version 退出通过 |

## Product health snapshot

由产品 scorecard 对该 scope 生成的全量快照（包含支撑任务和 blocked 历史项，不只包含三次最终实验）：

- Eligible discovery rate: `25/35`
- Claim success/conflict: `16/1`
- Work completion rate: `6/9`
- Handoff continuation（review claims）: `12`
- Context defects: `0`
- Activations observed: `35`
- C1/C2/C3/C4: `PASS/PASS/PASS/PASS`

该快照说明协议和结果 provenance 健康，不等于价值门或阶段退出门已通过。

## Exit decision and next action

当前判断是 **stay in Experience Version**，不是回退，也不是进入后续阶段。已完成的三次交付保留为价值候选证据；阶段退出暂不宣称。

下一步只应补齐退出所缺的可复核证据：建立同 acceptance 的方案 A 对照记录，明确记录每次 Human action、activation 数量和总介入时间；若仍需修订 Work Item，应把额外 activation 与 request_changes 作为正式失败/重跑事实保留，而不是压缩成一次成功。跨设备、自动发现、恢复和生产运维继续 Deferred。

## Source pointers

- `docs/prds/agent-self-service-collaboration.md`
- `docs/prds/agent-self-service-collaboration-experience-version.md`
- `docs/designs/agent-self-service-collaboration-experience-version-alignment.md`
- `docs/plans/agent-self-service-collaboration-roadmap.json`（通过 `zj-roadmap-driven` 读取）
- `.zagenticopn/shared.sqlite3`（只读事件核对）
