# C1–C4 黑盒 fixture protocol

这是候选中立的 `zagenticopn-c1-c4-black-box/v1` 重放协议。它只调用候选已经运行的 HTTP surface，不导入候选模块，不读取候选数据库，也不把候选源码中的邻近测试改写成 conformance 通过。

## Human 与 Agent 角色

每次运行固定两个逻辑 Agent：`agent-a` 是 producer，`agent-b` 是 discoverer/reviewer。它们分别绑定 `fixture-device-a` 与 `fixture-device-b`，共享一个候选 workspace。Human 只产生一次通用事件：`检查 shared context`；Human 不提供 Work Item ID、不复制上下文、不替代 claim 或 review。

每个候选运行三次。每次使用唯一 `run_id` 和唯一 Work Item ID，保存完整 HTTP transcript、请求 actor、workspace、候选 commit 与 canonical Git references。HTTP 响应中的 token 不写入产物；请求 body 只保存 fixture 数据。

## 四个黑盒场景

| 门 | 黑盒动作 | 严格通过条件 |
| --- | --- | --- |
| C1 publish/discover | producer 发布 eligible Work Item；Human 激活 reviewer；reviewer 只用 task-agnostic discover 入口查找它 | 另一 Agent 按自身 eligibility 发现正确 Work Item，Human intervention=0，并返回可解释的 scope/filter 结果 |
| C2 competing claim | 两个 Agent 并发 claim 同一 Work Item | 恰好一个成功、一个被拒绝，且没有重复执行或第二份 Git provenance |
| C3 result publication | producer 发布含五字段的结果，consumer 读取 | `result_summary`、`next_action`、`acceptance_status`、`blocker`、`references` 通过候选的跨 Agent result schema 读取 |
| C4 review continuation | producer 将 Work Item 置为 awaiting review；独立 reviewer 激活 | reviewer 自行发现、claim、核验 references、完成 review，Human 不补上下文 |

`partial` 只表示真实 HTTP 行为完成了邻近动作；`pass` 表示该门的最小结构化语义已被黑盒验证；`strict_pass=false` 表示它没有满足该门的完整语义。`conformance_fail / unsupported_on_exposed_surface` 表示当前候选可调用的产品 surface 不支持该门，不能扩大为源码全局 absent。`unverified` 表示没有足够的候选 runtime surface 可以完成该门。Generic artifact 或 memory fact 只要是可机器解析的五字段 shared record，就可以满足 C3；自由文本中恰好出现字段不算。Kanban review 列可见也不等于 C4 reviewer claim/verify/complete。

## Runner

```sh
python3 research/routa-qm-conformance/run_c1_c4_black_box.py \
  --candidate routa \
  --base-url http://127.0.0.1:3211 \
  --runs 3 \
  --output research/routa-qm-conformance/2026-08-20-black-box-routa.json
```

qm 需要两个短期 capability token。token 只通过环境变量传给 runner，不落盘：

```sh
export QM_AGENT_A_TOKEN='...'
export QM_AGENT_B_TOKEN='...'
python3 research/routa-qm-conformance/run_c1_c4_black_box.py \
  --candidate qm \
  --base-url http://127.0.0.1:18080 \
  --runs 3 \
  --output research/routa-qm-conformance/2026-08-20-black-box-qm.json
```

Routa fixture 使用真实 `/api/tasks`、`/api/tasks/ready`、`/api/tasks/{id}/artifacts` 和 task transition。qm fixture 使用真实 `/v1/apis`、`/v1/memory/facts`、`/v1/memory/search`，并将统一 Work Item/result/review 文档作为共享 memory fact；对 `/v1/work-items`、claim 与 review 路径做黑盒探测。qm 的 `/v1/apis` catalog 是 exposed-surface 判断依据；未知路径得到的 `403` 不能被误读为 endpoint 存在。

## 证据边界

本协议可以证明候选运行时能否重放固定交互，以及能否观察到邻近机制；它不能为候选补造缺失的 Work Item、claim、typed result 或 reviewer state machine。只有四个门的 `strict_pass` 全部为 `true`，且三次运行都满足，才允许回到 roadmap 的 A/B/C 采用讨论；否则继续保持 D，不启动 ZAgenticOPN 产品 runtime。
