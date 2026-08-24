# ext 候选轮次预筛：Routa、MCP Agent Mail Rust、Avernet

状态：`prescreen_only`。本文件记录已 sealed 的候选背景与路径信号，不是 C1–C4 通过结论，也不授权 ZAgenticOPN 产品 runtime。

## 轮次范围

本轮沿用 `zagenticopn-experience-version-ext-round/v1` 的 C1–C8 口径，候选上限为 3 个：

| 候选 | 角色 | 固定 commit | Stars | Topic match | 当前证据层级 |
| --- | --- | --- | ---: | ---: | --- |
| [phodal/routa](https://github.com/phodal/routa/tree/e48861ab81e2b30378fd32f05204a3ab424c4fec) | ext | `e48861ab81e2b30378fd32f05204a3ab424c4fec` | 1,796 | 8 | 已有 runtime/API/test 与 C1–C4 黑盒三次重放 |
| [Dicklesworthstone/mcp_agent_mail_rust](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/tree/43a2e4bb12c47d08b3db363f1e72a8aaf7bb0a56) | ext | `43a2e4bb12c47d08b3db363f1e72a8aaf7bb0a56` | 130 | 6 | 本轮 sealed 源码路径与 conformance 规则；尚无本轮 runtime 重放 |
| [inclusionAI/Avernet](https://github.com/inclusionAI/Avernet/tree/39f482fd551f8ef506447042b55231e7d134bbf1) | ext | `39f482fd551f8ef506447042b55231e7d134bbf1` | 502 | 2 | sealed 架构规则与 bot 接入路径；尚无本轮 runtime 重放 |

Stars 与 topic match 只用于候选背景排序，不作为能力分数。三份固定 commit、Stars、topicMatch 和 Evidence ID 来自本轮 sealed ledger [`2026-08-20-ext-round-ledger-response.json`](2026-08-20-ext-round-ledger-response.json)，其 brief fingerprint 为 `9056a917064ef6813bbbb6ba69bbaab200a15938de559bebcdb2b69aaa922885`；本轮读取 220 个文件、2,224,046 bytes，采集耗时 287,212 ms。

## 预筛信号

### Routa

- 已有 workspace-first、多 runtime surface、task/Kanban/queue 和多协议集成表面，适合继续按候选中立 fixture 做运行验证（Evidence `14c2641f93a68d845626987c`、`a7bfbf014a952100eeb1c4b7`、`04870f0cd9fe2641b42ba8f6`）。
- 已完成固定 commit 的 HTTP 黑盒三次重放；结果是 C1 `partial`、C2 `conformance_fail / unsupported_on_exposed_surface`、C3 `strict_pass=3/3`、C4 `partial`。详见 [`2026-08-20-black-box-fixture-results.md`](2026-08-20-black-box-fixture-results.md)。
- 由于 C1/C2/C4 未同时通过，Routa 不能进入 A/B 采用讨论；它保留为可抽取的 task filtering、artifact/evidence gate、lane handoff 和 queue concurrency 单位能力候选。

### MCP Agent Mail Rust

- 固定版本包含独立的 agent-detect、CLI 和 conformance crate，且 conformance fixtures 以工具/资源输入输出及错误分支为核心（Evidence `12edeb6f1e466b387e73e4cb`、`550fc8197c3f3de72f3fc54d`、`dc36f2537f8b385010e57032`、`b24f74b12b0e8c026daf7fad`）。
- 当前证据更像 Agent 间消息、工具和占用/保留能力，不足以证明 `available → claimed → awaiting_agent_review → completed` 的 Work Item 状态链。
- 需直接确认可运行入口是 MCP stdio、HTTP/SSE 还是其他 transport；在 transport 未确认前，不把消息发送或 reservation API 映射为 C1/C2/C4。

### Avernet

- 架构规则要求 contracts、依赖方向、配置驱动组装、兼容性审查和 conformance tests（Evidence `9eff2958d033b4c594ba2859`、`a4c88576a1f302d76d890225`、`7eee59fabe5856ed29cc6815`）。
- 当前 sealed evidence 没有提供足够的可运行入口、shared Work Item frontier、原子 claim 或 reviewer continuation 证据；架构治理成熟度不能替代 C1/C2/C4 证据。

## 统一判定表（当前）

| 候选 | C1 publish/discover | C2 competing claim | C3 result publication | C4 review continuation | 结论 |
| --- | --- | --- | --- | --- | --- |
| Routa | `partial` | `conformance_fail / unsupported_on_exposed_surface` | `strict_pass=3/3` | `partial` | 未通过硬门 |
| MCP Agent Mail Rust | `unknown` | `unknown` | `unknown` | `unknown` | 尚未 runtime 验证 |
| Avernet | `unknown` | `unknown` | `unknown` | `unknown` | 尚未 runtime 验证 |

`unknown` 只表示当前没有足够的 exposed runtime/API/test 证据，不表示源码全局 absent。C3 只有在另一 Agent 能机器解析五字段 shared record 时才可标记 `pass`；自由文本中的字段名不算通过。

## 下一步与退出条件

1. 已用同一 `zagenticopn-experience-version-ext-round/v1` brief 完成三候选固定 commit 与 sealed source/path 采集；采集文件为 [`2026-08-20-ext-round-brief.request.json`](2026-08-20-ext-round-brief.request.json)，runtime 深读见 [`2026-08-20-ext-runtime-findings.md`](2026-08-20-ext-runtime-findings.md)。
2. 对 MCP Agent Mail Rust 和 Avernet 继续确认真实 transport 与最小可运行入口，再决定能否将候选中立 C1–C4 fixture 投影到其 exposed surface；当前 runtime 深读结果见 [`2026-08-20-ext-runtime-findings.md`](2026-08-20-ext-runtime-findings.md)，不可投影时记录 `unverified`，不改写协议以迎合候选。
3. 每个可运行候选都必须使用同一 C1–C4 fixture 连续 3 次，并记录 Agent、device、workspace、候选 commit 和 canonical Git references。
4. 任一候选通过 C1/C2/C4 后停止 D，交给 Human 重新选择 A/B/C；三个候选全部未通过则 D 耗尽，转 C，但仍需 Human 明确授权产品 runtime。

## 采集异常

本轮第一次 collect 因未传 `GITHUB_TOKEN` 触发 GitHub API rate limit；随后使用本机已认证 GitHub token 重跑同一 request，已生成 sealed ledger。DeepWiki 导航未作为事实来源，本轮 navigation 记录均为 heuristic fallback；这只影响路径导航，不把 heuristic 结果提升为能力结论。针对 Avernet 的后续 source-path 请求解析到更新的默认分支 commit `c63759fb2a52876830bf046cbd6f0af2b66fbcaf`，与本轮固定 commit `39f482fd551f8ef506447042b55231e7d134bbf1` 不同；该请求结果不纳入本轮结论，避免混用 revisions。
