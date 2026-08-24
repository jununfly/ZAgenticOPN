# Routa 与 qm：runtime/API/test 证据补采发现

本文件是 `2026-08-20-runtime-ledger-response.json` 的可读投影。GitHub 事实只使用固定 commit 的 sealed ledger；DeepWiki 只作路径导航，不能作为事实来源。

## 采集范围

| 角色 | 候选 | 固定 commit | Stars | Topic match |
| --- | --- | --- | ---: | ---: |
| ext | [phodal/routa](https://github.com/phodal/routa/tree/e48861ab81e2b30378fd32f05204a3ab424c4fec) | `e48861ab81e2b30378fd32f05204a3ab424c4fec` | 1,796 | 8 |
| ref | [yc-software/qm](https://github.com/yc-software/qm/tree/568252bd4e6da5288b239573abef972f3e16b3f9) | `568252bd4e6da5288b239573abef972f3e16b3f9` | 13,980 | 0 |

Ledger fingerprint：`fd607011d3a5c11868db69bad5868c0ba96faa71b26849ae9905d6cca43aa013`。本轮读取 109 个文件、665,833 bytes；DeepWiki 两次请求超时，compiler 按策略回退 heuristic，诊断已保留在 ledger。

## 新增可核验事实

- Routa 的 `docs/ARCHITECTURE.md` 说明 Tasks 是 durable work units，Kanban 驱动 lane automation/queueing；其 TypeScript queue 按 board 限制并发并防止 stale auto-run 重复触发（Evidence `a7bfbf014a952100eeb1c4b7`）。这是 C2 相关的候选机制信号，但不是跨 Agent Work Item 原子 claim 的充分证明。
- 同一架构文档列出 workspace、task、session、artifact 等 store/registry，以及 Postgres、SQLite、in-memory、JSONL traces、Docker 与 filesystem 等 runtime/persistence 选项（Evidence `dd9041dea1e3e5e9d1af040c`）。这支持 Routa 具备较宽的产品和运行时表面，不证明 C3 的五字段结果发布协议。
- Routa 的架构原则将 workspace 作为 sessions、tasks、boards、memories 等对象的协调边界，并要求 Web/desktop 双后端语义一致（Evidence `04870f0cd9fe2641b42ba8f6`、`9d2c7ce28c570504c510429f`）。这支持继续检查 C7，但本轮没有拿到默认过滤和显式跨 workspace 权限测试。
- qm 的 E2E README 说明测试驱动真实 `qm` binary，并验证文件、容器、`flyctl` 和部署 teardown 等客观结果，而非只检查输出文字（Evidence `e9620292ac1afb3908251092`、`a52ae49edc686dbcaf618f35`）。这提高了 qm 的运行证据强度，但这些场景不是 Agent 自服务协作闭环。
- qm 的 `plugins/chassis/src/claims.ts` 声明 `ClaimStore.claimFirst(ids, expiresAtMs)`，但固定路径是 `/v1/auth/broker/claim`；当前证据不足以把它解释成 Work Item claim 或执行权转移（Evidence `ba0dc47d5722293f8963155a`）。
- qm 的 E2E 场景包含 isolated pool store、identity 与 stale manifest 检查，说明有隔离和身份相关测试材料；仍需补采 Agent shared coordination scope 证据（Evidence `3a8a1dd70646dea905417b4d`、`723e2028610d53fdb9afebcd`）。
- qm onboarding 文档描述 memory-first onboarding，将 profile 持久化到 memory；这不是 Agent-private recovery context 与 shared coordination facts 的分层证明（Evidence `4a6967334c1f9ead174eff56`、`51cb2bc56f3b791c1d28d392`）。

## C1–C4 判断

- C1 publish/discover：Routa 有 durable task、Kanban/automation/queue 组合，qm 有真实 CLI/E2E 与 onboarding discovery，但没有证据证明 task-agnostic Human trigger 后另一 Agent 能发现可执行 Work Item；仍 `unverified`。
- C2 competing claim：Routa 有 per-board concurrency/stale auto-run 防护，qm 有 `claimFirst` 接口，但分别缺少跨 Agent Work Item 原子 claim 语义与对应并发测试；仍 `unverified`。
- C3 result publication：Routa 有 artifact/persistence store，qm E2E 验证客观产物；均未证明 `result_summary`、`next_action`、`acceptance_status`、`blocker`、`references` 五字段的跨 Agent发布/读取链；仍 `unverified`。
- C4 review continuation：qm E2E 有真实二进制验证，Routa 有 session/review/protocol 表面，但没有 reviewer Agent 发现、claim、验证、完成的闭环测试；仍 `unverified`。

## 下一步

本轮已经从“只有维护文档”推进到“架构、真实 E2E、候选 claim 接口”证据，但尚未越过 C1–C4 硬门。下一轮应绕过 DeepWiki 超时带来的导航缺口，直接针对固定 commit 的已知路径补采 canonical source/test：Routa 的 `kanban`、`handoffs`、`tasks`、`review` API 与 Rust/TypeScript integration tests；qm 的 `plugins/web-ui` 协作/active-run routes、`src/memory`、`plugins/chassis` claim 使用方和对应 tests。完成后再回到 roadmap `1-1-4` 进行 A/B/C/D 决策复核；期间不开始产品 runtime。
