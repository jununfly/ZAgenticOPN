# ext 轮次最终筛选结果：C1–C4 硬门

本文件是 `1-1-7` 的退出 scorecard。它只回答候选是否值得进入 A/B/C 采用讨论，不授权 ZAgenticOPN 产品 runtime、PoC 或部署。

## 候选与固定版本

| 候选 | 固定版本 | 证据来源 | C1 | C2 | C3 | C4 |
| --- | --- | --- | --- | --- | --- | --- |
| phodal/routa | `e48861ab81e2b30378fd32f05204a3ab424c4fec` | HTTP fixture 连续 3 次：[`black-box-routa.json`](2026-08-20-black-box-routa.json) | `partial` | `conformance_fail / unsupported_on_exposed_surface` | `strict_pass=3/3` | `partial` |
| Dicklesworthstone/mcp_agent_mail_rust | `43a2e4bb12c47d08b3db363f1e72a8aaf7bb0a56` | API inventory：[`ext-runtime-surface-ledger-response.json`](2026-08-20-ext-runtime-surface-ledger-response.json)，Evidence `c0dbc43fc86e04b8e4a59d3a` | `partial` | `conformance_fail / unsupported_on_exposed_surface` | `unknown` | `unknown` |
| inclusionAI/Avernet（当前 profile 刷新） | `7c6518171cc9dac0b0139e4accb2bf6aa0780776` | sealed README：[`avernet-work-item-current-ledger-response.json`](2026-08-20-avernet-work-item-current-ledger-response.json)，Evidence `c8720b0f9d9e5df995ad3847`、`fb512dc58d7bab50e9d3fc9b` | `conformance_fail / unsupported_on_exposed_surface` | `conformance_fail / unsupported_on_exposed_surface` | `conformance_fail / unsupported_on_exposed_surface` | `conformance_fail / unsupported_on_exposed_surface` |

### Avernet 刷新版本的语义

该固定版本的 `engine.community.plugin_api.work_item/README.md` 明确说明：Work Item 是 vendor-neutral port，具体实现位于 `plugins/prod/dima/` 和 `plugins/community/work_item/`，其中 community 实现是 `no-op`（Evidence `c8720b0f9d9e5df995ad3847`、`fb512dc58d7bab50e9d3fc9b`）。因此社区 exposed profile 不能提供可执行的 publish/discover、claim、结果发布或 review continuation；不能把存在 neutral router/port 当成能力已实现。

## 退出判断

- 三个 ext 候选都没有通过 C1、C2、C4 三个核心硬门；Routa 的 C3 通过不足以抵消发现、唯一执行权和 review 接续失败。
- Routa 与 MCP Agent Mail Rust 仍保留可抽取单位能力：task/queue/artifact gate，或 identity/message/inbox/file reservation；这些能力不等于 Feature 1 语义。
- Avernet 的 neutral Work Item port 可作为接口设计参考，但 community no-op 使其不能成为直接复用或薄适配基础。
- 因此 D 轮次按已接受的封顶规则耗尽，下一路线是 C：ZAgenticOPN 主导架构，只选择性抽取单位能力；进入产品 runtime 仍需 Human 单独明确授权。

## 版本边界

最初预筛记录了 Avernet `39f482fd551f8ef506447042b55231e7d134bbf1`；后续确认该版本与默认分支发生漂移，故本退出 scorecard 对 Avernet 使用新的固定刷新 commit `7c6518171cc9dac0b0139e4accb2bf6aa0780776`，不混合两次 revision 的 source/test 事实。MCP 与 Routa 仍使用本轮既定固定版本。
