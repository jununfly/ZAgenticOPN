# ext 候选 runtime/API/test 深读发现

状态：候选筛选证据，非产品 runtime 验收。

## MCP Agent Mail Rust

固定版本：`43a2e4bb12c47d08b3db363f1e72a8aaf7bb0a56`。

### Exposed API 信号

固定版本 README 的工具目录把能力分成 identity、messaging、contacts、file reservations、search 和 macros：

- Identity：`register_agent`、`create_agent_identity`、`whois`、`resolve_pane_identity`、`list_agents`；
- Messaging：`send_message`、`reply_message`、`fetch_inbox`、`fetch_inbox_events`、delivery receipt、acknowledge/read；
- File reservations：冲突检查、路径保留、续租、释放和强制释放。

证据：[README.md](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/blob/43a2e4bb12c47d08b3db363f1e72a8aaf7bb0a56/README.md)（Evidence `c0dbc43fc86e04b8e4a59d3a`）。

这说明它具备 Agent 身份、消息收发和资源占用的单位能力，但工具目录没有 `publish_work_item`、按 Agent eligibility 的 frontier 查询、Work Item execution claim、review claim 或 review completion。不能把 `file_reservation_paths` 当成 C2：文件占用与 Work Item 执行 authority 不是同一语义。

### 运行入口与测试证据边界

固定树包含 `mcp-agent-mail-server` crate、HTTP/stdio help fixture、HTTP transport harness 以及 `fetch_inbox_events` 和 reservation fixtures；本轮 heuristic collector 没有把这些具体 help/transport 文件读入 sealed evidence，因此没有把“存在这些路径”升级为已运行的 HTTP/MCP transcript。当前只保留可核验的 README 工具目录和已有 conformance fixture 路径证据：[conformance README](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/blob/43a2e4bb12c47d08b3db363f1e72a8aaf7bb0a56/crates/mcp-agent-mail-conformance/tests/conformance/README.md)（Evidence `12edeb6f1e466b387e73e4cb`、`550fc8197c3f3de72f3fc54d`）。

因此当前 C1–C4 标签为：

| 门 | 标签 | 原因 |
| --- | --- | --- |
| C1 | `partial` | message/inbox 可以承载共享通知，但没有 task-agnostic eligible Work Item discover 语义 |
| C2 | `conformance_fail / unsupported_on_exposed_surface` | 工具目录没有 Work Item claim；file reservation 不能替代执行 authority |
| C3 | `unknown` | 没有五字段 result record 的跨 Agent 发布/读取证据 |
| C4 | `unknown` | 没有 awaiting-review 的 reviewer discover/claim/verify/complete 链 |

这不是源码全局 absent 声明；它是当前固定版本可核验 API surface 的 conformance 判定。若要推翻 C1/C2/C4，候选必须提供能投影到同一 fixture 的真实 exposed runtime。

## Avernet

固定版本：`39f482fd551f8ef506447042b55231e7d134bbf1`。

固定版本的 Bot Provider 文档只说明：本地 OpenClaw gateway 优先走 Quick Start，已经托管的 bot 可采用 Bot Provider 模式（Evidence `7a9ad4b99b2e083244e63799`）。架构文档要求 protocol contract tests，但本轮没有拿到可调用 Work Item、claim 或 reviewer API；对应的 runtime/transport 证据仍为 unknown。

因此当前 C1–C4 全部保持 `unknown`，而不是 `absent`：

| 门 | 标签 | 原因 |
| --- | --- | --- |
| C1 | `unknown` | Bot 接入说明不等于 shared Work Item frontier |
| C2 | `unknown` | 没有 exposed Work Item claim 或并发冲突测试 |
| C3 | `unknown` | 没有结构化五字段结果跨 Agent 读写证据 |
| C4 | `unknown` | 没有 reviewer Agent 接续状态链 |

协议测试规则本身只能证明项目要求为插件协议建立测试，不能证明 Feature 1 的协作语义已经存在（Evidence `9e90fd7cea9a35d6e0a2ed5b`）。

后续尝试按 `work_item` 文件名补采时，GitHub 默认分支已经解析到 `c63759fb2a52876830bf046cbd6f0af2b66fbcaf`，而本轮候选固定 commit 是 `39f482fd551f8ef506447042b55231e7d134bbf1`；该新分支结果不纳入本评估，避免把不同 revision 的 source/test 混在一起。

## 对 D 轮次的影响

1. Routa 已完成三次 HTTP 黑盒重放且未过 C1/C2/C4。
2. MCP Agent Mail Rust 的 canonical API inventory 显示高价值消息/身份/资源 reservation 单位能力，但没有 Feature 1 的 Work Item claim/review surface；它目前是 selective-reuse 候选，不是 A/B 候选。
3. Avernet 证据不足以判断是否值得 runtime 投入；不能用“架构规则成熟”替代黑盒证据。
4. D 仍未自动耗尽：Avernet 仍需 Human 是否继续补采 runtime 的判断；在没有 exposed surface 时，继续实现产品 runtime 仍不被授权。

本轮 sealed inputs：

- [`2026-08-20-ext-round-ledger-response.json`](2026-08-20-ext-round-ledger-response.json)，fingerprint `9056a917064ef6813bbbb6ba69bbaab200a15938de559bebcdb2b69aaa922885`；
- [`2026-08-20-ext-runtime-source-ledger-response.json`](2026-08-20-ext-runtime-source-ledger-response.json)，fingerprint `ccc1c462772975b4fcdf25e5cb77adef6c2bd5417fd70f1715fbe2acb5f55cf1`；
- [`2026-08-20-ext-runtime-surface-ledger-response.json`](2026-08-20-ext-runtime-surface-ledger-response.json)，fingerprint `fb2e5a25ba1fa003b4576578bde44170d18344e04c9598be01d2db440c94b033`。
