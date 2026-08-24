# Routa / qm：固定版本 runtime/test 重放记录

本记录只报告固定 commit 的真实测试重放，不把候选测试套件改写成 ZAgenticOPN Experience Version 的 C1–C4 fixture。候选仓库均在临时目录 checkout，未修改候选源码，也未启动 ZAgenticOPN 产品 runtime。

## 固定版本与环境

| 候选 | commit | 重放环境 |
| --- | --- | --- |
| `phodal/routa` | [`e48861ab81e2b30378fd32f05204a3ab424c4fec`](https://github.com/phodal/routa/tree/e48861ab81e2b30378fd32f05204a3ab424c4fec) | macOS，Rust workspace；`cargo test` |
| `yc-software/qm` | [`568252bd4e6da5288b239573abef972f3e16b3f9`](https://github.com/yc-software/qm/tree/568252bd4e6da5288b239573abef972f3e16b3f9) | Node `v22.23.1`；仓库声明 Node `>=24.15.0`，因此本结果是低于声明版本的可重复观察，不是 release-环境兼容承诺 |

## 重放命令与结果

### qm

```sh
node --experimental-test-module-mocks --test \
  test/task-store.test.ts \
  test/auth-broker-claim.test.ts \
  test/delivery-drain-claim.test.ts \
  test/memory-agent-routes.test.ts \
  test/scope-resources-authz.test.ts
```

连续 3 次均通过：每次 `46 tests / 3 suites / 46 pass / 0 fail`。

覆盖的固定源码/测试入口包括：

- [`TaskStore` compare-and-set 与 open-task filter](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/task-store.test.ts#L29-L76)
- [`ClaimStore` 一次性 claim 与输入校验](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/auth-broker-claim.test.ts#L65-L129)
- [delivery drain 并发 claim、过期 claim 重现](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/delivery-drain-claim.test.ts#L40-L88)
- [memory API 的 scope read/write、CAS rewrite、跨 scope 拒绝](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/memory-agent-routes.test.ts#L62-L229)
- [personal/org/channel context 与资源授权隔离](https://github.com/yc-software/qm/blob/568252bd4e6da5288b239573abef972f3e16b3f9/test/scope-resources-authz.test.ts#L152-L275)

### Routa

```sh
cargo test -p routa-core --lib 'rpc::methods::kanban::tests::' -- --quiet
cargo test -p routa-server --test rust_api_task_artifacts -- --quiet
```

上述两条命令各连续 3 次均通过：

- `routa-core` Kanban focused suite：每次 `26 passed / 0 failed`；
- `rust_api_task_artifacts`：每次 `8 passed / 0 failed`。

覆盖的固定源码/测试入口包括：

- Kanban 查询与 board 状态：[queries.rs](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-core/src/rpc/methods/kanban/queries.rs#L328-L432)
- lane handoff 请求/提交：[handoffs.rs](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-core/src/rpc/methods/kanban/handoffs.rs#L51-L230)
- 卡片转移与 gate：[cards.rs](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-core/src/rpc/methods/kanban/cards.rs#L129-L240)、[automation.rs](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-core/src/rpc/methods/kanban/automation.rs#L1064-L1150)
- artifact/evidence gate 与缺字段阻断：[rust_api_task_artifacts.rs](https://github.com/phodal/routa/blob/e48861ab81e2b30378fd32f05204a3ab424c4fec/crates/routa-server/tests/rust_api_task_artifacts.rs#L263-L548)

完整 `routa-core --lib` 首次重放为 `222 passed / 1 failed`。唯一失败是 `create_issue_from_card_links_existing_task`，失败路径依赖测试中的 GitHub authorization mock，断言收到 `authorization: token test-token`，随后得到 `502 Bad Gateway`；它不属于本轮 C1–C4 focused suites，不能解释为协作语义失败，也不能从中推导候选通过。

## 与 C1–C4 的语义判定

| 门 | 重放增强了什么 | 仍缺什么 | 本轮状态 |
| --- | --- | --- | --- |
| C1 publish/discover | qm 有 open-task filter；Routa 有 Kanban query 与 ready-task 邻近机制 | 没有 task-agnostic Human trigger 后按 Agent eligibility 自动发现 eligible Work Item 的 API/test | `unverified` |
| C2 competing claim | qm 的 auth/delivery claim 与 task CAS 具有可重复冲突测试；Routa focused Kanban suite 可重复 | qm claim 对象不是 Work Item execution authority；Routa board queue/handoff 不是原子 Work Item claim，也没有唯一 Git provenance 证明 | `unverified`（邻近能力 `partial`） |
| C3 result publication | Routa artifact/evidence gate 与 task run 测试可重复；qm task/delivery/memory 测试可重复 | 没有另一 Agent 可直接读取的五字段 `result_summary`、`next_action`、`acceptance_status`、`blocker`、`references` 发布契约 | `unverified` |
| C4 review continuation | Routa lane handoff 与状态转移测试可重复；qm session/recovery 邻近测试已通过 | 没有 reviewer Agent 自主发现 awaiting review、claim、核验 references、完成 review 的跨 Agent 测试 | `unverified` |

因此，三次重放证明的是候选邻近机制具有运行稳定性，不是 C1–C4 conformance 通过。统一退出门仍未满足：没有一个候选能在不改写其产品语义的前提下运行完整 C1–C4 fixture，更没有完成“每个 fixture 连续 3 次且 Human 任务特定介入为 0”的硬门。

## 本轮决策影响

- `A` 整体复用：继续不成立。
- `B` 薄适配：继续没有证据支持；适配层无法替代缺失的 C1、C3、C4 语义。
- `C` base-led selective reuse：仍是方向性候选。qm 的 claim/CAS/scope-memory 与 Routa 的 query/handoff/artifact gate 可进入单位能力候选清单，但必须由 ZAgenticOPN 重新拥有 Work Item、Agent eligibility、result schema 与 reviewer continuation 语义。
- `D` 继续有效：当时下一步是补齐同一 C1–C4 fixture 的可执行验证协议，或在证据边界明确后由 Human 决定停止候选深读；不开始产品 runtime。

## 第五轮黑盒 fixture 重放

上述“下一步”已完成。候选中立 runner 与协议见 [`2026-08-20-black-box-fixture-protocol.md`](2026-08-20-black-box-fixture-protocol.md)，完整 transcript 见 [`2026-08-20-black-box-routa.json`](2026-08-20-black-box-routa.json) 与 [`2026-08-20-black-box-qm.json`](2026-08-20-black-box-qm.json)，汇总见 [`2026-08-20-black-box-fixture-results.md`](2026-08-20-black-box-fixture-results.md)。Routa 与 qm 各连续三次真实 HTTP 重放，C3 均完成结构化五字段 parse 并为 `pass`；C1/C4 仍为邻近 `partial`，C2 为 `conformance_fail / unsupported_on_exposed_surface`。因此本记录中的 D 决策保持不变，但 C1–C4 的证据层级已从“仅源码/测试间接信号”升级为“真实 runtime 黑盒 transcript + 明确 strict gap”。
