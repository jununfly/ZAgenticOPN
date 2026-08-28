# 多设备多 Agent 协同开发的上下文与记忆层选型

## 1. Executive summary
对于 Human-led federation 场景，TencentDB-Agent-Memory 最适合作为共享记忆与协作元数据底座；MyContext 更适合作为个人工作上下文层，MineContext 更适合作为本地优先的个人上下文伙伴。三者都不能单独替代 Git、canonical roadmap、Work Packet、任务 claim、预算协调或发布治理，因此推荐将 TencentDB-Agent-Memory 接入现有 ZHarness/ZAgentic control plane，而不是让记忆系统承担控制面职责。

- 选择 TencentDB-Agent-Memory 作为共享 memory/metadata layer，并通过明确 adapter 接入 ZHarness/ZAgentic control plane；不要让它替代 Git、canonical roadmap、Work Packet、planned-cell claim、预算协调或发布门。本议题未发现未决信息缺口（ledger unknownCriteria 为空），信息完备。
- 如果第一阶段优先解决个人设备上的私有上下文捕获和检索，选择 MyContext；MineContext 作为本地优先个人 context companion 评估，不作为多人协作底座。

## 2. Key findings
- MineContext 将自己定位为主动的、上下文感知的个人 AI partner，并提供 context-source/捕获/处理结构。 [[2]](https://github.com/volcengine/MineContext/blob/171c7a9ea8091e326ddcf0f10718aa1b58c83c65/README.md) [[5]](https://github.com/volcengine/MineContext/blob/171c7a9ea8091e326ddcf0f10718aa1b58c83c65/README.md)
- MineContext 的 README 明确包含 Local-First 与 Privacy Protection 入口。 [[4]](https://github.com/volcengine/MineContext/blob/171c7a9ea8091e326ddcf0f10718aa1b58c83c65/README.md)
- 在本次固定 commit 的采集范围内，没有足够 canonical evidence 证明 MineContext 提供团队级 Agent/task ownership、跨设备 conflict protocol 或协作预算控制。 [[1]](https://github.com/volcengine/MineContext/blob/171c7a9ea8091e326ddcf0f10718aa1b58c83c65/README.md) [[3]](https://github.com/volcengine/MineContext/blob/171c7a9ea8091e326ddcf0f10718aa1b58c83c65/README.md)
- MyContext 将自己定位为每个人的持久个人工作 context layer，并强调个人数据控制和 consequential action approval。 [[7]](https://github.com/openTrinity/mycontext/blob/81b3c7ac178dbf141ca97cbe6b6682f73e3d3199/README.md) [[9]](https://github.com/openTrinity/mycontext/blob/81b3c7ac178dbf141ca97cbe6b6682f73e3d3199/README.md)
- MyContext 提供多来源增量 ingestion、本地 SQLite vault、知识图谱和持久 FastAPI retrieval 服务。 [[6]](https://github.com/openTrinity/mycontext/blob/81b3c7ac178dbf141ca97cbe6b6682f73e3d3199/README.md) [[10]](https://github.com/openTrinity/mycontext/blob/81b3c7ac178dbf141ca97cbe6b6682f73e3d3199/docs/design/persona-distill-forge.md) [[8]](https://github.com/openTrinity/mycontext/blob/81b3c7ac178dbf141ca97cbe6b6682f73e3d3199/README.md)
- MyContext 的个人定位和本地数据迁移约束意味着它不能直接被视为团队共享控制面；跨设备协作仍需外部 owner、版本和任务系统。 [[7]](https://github.com/openTrinity/mycontext/blob/81b3c7ac178dbf141ca97cbe6b6682f73e3d3199/README.md) [[8]](https://github.com/openTrinity/mycontext/blob/81b3c7ac178dbf141ca97cbe6b6682f73e3d3199/README.md)
- TencentDB-Agent-Memory 的 MemoryCore 显式管理 users、teams、Agents、tasks、Skills、knowledge assets、memberships、ownership 和 access relationships。 [[13]](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/97f94654280b2932c35ba4806a491999ed244cc9/MemoryCore/README.md)
- MemoryCore 作为独立 core 通过 HTTP Gateway、TypeScript/Python SDK 为 memory、knowledge metadata 和 asset metadata 提供统一访问。 [[15]](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/97f94654280b2932c35ba4806a491999ed244cc9/MemoryCore/README.md)
- TencentDB-Agent-Memory 的版本迁移、Docker/Kubernetes runtime 和 memory/metadata API 仍不等于 Git merge、roadmap decision、Work Packet claim 或实验预算协调。 [[14]](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/97f94654280b2932c35ba4806a491999ed244cc9/MemoryCore/README.md) [[11]](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/97f94654280b2932c35ba4806a491999ed244cc9/MemoryCore/Dockerfile) [[12]](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/97f94654280b2932c35ba4806a491999ed244cc9/MemoryCore/Dockerfile)

## 3. Analysis & synthesis
### comparison-context
个人上下文能力：MineContext 偏主动捕获和本地优先；MyContext 偏多源工作知识图谱和个人检索；TencentDB-Agent-Memory 偏多层 memory 与资产元数据服务。

### comparison-governance
针对 Human-led federation，TencentDB-Agent-Memory 的 teams/Agents/tasks/memberships/ownership 元数据最接近共享协作事实；但三者都需要外部 control plane 管理代码、决策、claim、预算和发布。

### comparison-deployment
MyContext 与 MineContext 的本地/个人取向更适合单人隐私边界；TencentDB-Agent-Memory 的独立 Gateway、容器和 API 更适合集中式共享服务，但会增加部署、权限和迁移治理。

### 3.7 Recommendation
- 选择 TencentDB-Agent-Memory 作为共享 memory/metadata layer，并通过明确 adapter 接入 ZHarness/ZAgentic control plane；不要让它替代 Git、canonical roadmap、Work Packet、planned-cell claim、预算协调或发布门。本议题未发现未决信息缺口（ledger unknownCriteria 为空），信息完备。
- 如果第一阶段优先解决个人设备上的私有上下文捕获和检索，选择 MyContext；MineContext 作为本地优先个人 context companion 评估，不作为多人协作底座。

## 4. Information gaps & next steps
| Gap | Nature | Next step |
|---|---|---|

## 6. Source list
1. [volcengine/MineContext@171c7a9ea8091e326ddcf0f10718aa1b58c83c65:README.md](https://github.com/volcengine/MineContext/blob/171c7a9ea8091e326ddcf0f10718aa1b58c83c65/README.md) — Evidence `80fab05c83d9214a24f7b9a8`
2. [volcengine/MineContext@171c7a9ea8091e326ddcf0f10718aa1b58c83c65:README.md](https://github.com/volcengine/MineContext/blob/171c7a9ea8091e326ddcf0f10718aa1b58c83c65/README.md) — Evidence `c1670d9d33d1395b02484b66`
3. [volcengine/MineContext@171c7a9ea8091e326ddcf0f10718aa1b58c83c65:README.md](https://github.com/volcengine/MineContext/blob/171c7a9ea8091e326ddcf0f10718aa1b58c83c65/README.md) — Evidence `4f94f3db9db3b45787bf3254`
4. [volcengine/MineContext@171c7a9ea8091e326ddcf0f10718aa1b58c83c65:README.md](https://github.com/volcengine/MineContext/blob/171c7a9ea8091e326ddcf0f10718aa1b58c83c65/README.md) — Evidence `46a23e06545555264946319f`
5. [volcengine/MineContext@171c7a9ea8091e326ddcf0f10718aa1b58c83c65:README.md](https://github.com/volcengine/MineContext/blob/171c7a9ea8091e326ddcf0f10718aa1b58c83c65/README.md) — Evidence `f5afc3d0b3536e1f3f9ad043`
6. [openTrinity/mycontext@81b3c7ac178dbf141ca97cbe6b6682f73e3d3199:README.md](https://github.com/openTrinity/mycontext/blob/81b3c7ac178dbf141ca97cbe6b6682f73e3d3199/README.md) — Evidence `b694a2b9b94a8ba7e6b47ef4`
7. [openTrinity/mycontext@81b3c7ac178dbf141ca97cbe6b6682f73e3d3199:README.md](https://github.com/openTrinity/mycontext/blob/81b3c7ac178dbf141ca97cbe6b6682f73e3d3199/README.md) — Evidence `6953f661bac7a6ee6f695ab3`
8. [openTrinity/mycontext@81b3c7ac178dbf141ca97cbe6b6682f73e3d3199:README.md](https://github.com/openTrinity/mycontext/blob/81b3c7ac178dbf141ca97cbe6b6682f73e3d3199/README.md) — Evidence `5d344f534037a88a2d0ae65d`
9. [openTrinity/mycontext@81b3c7ac178dbf141ca97cbe6b6682f73e3d3199:README.md](https://github.com/openTrinity/mycontext/blob/81b3c7ac178dbf141ca97cbe6b6682f73e3d3199/README.md) — Evidence `e1c77df9c8b21389e3d252f5`
10. [openTrinity/mycontext@81b3c7ac178dbf141ca97cbe6b6682f73e3d3199:docs/design/persona-distill-forge.md](https://github.com/openTrinity/mycontext/blob/81b3c7ac178dbf141ca97cbe6b6682f73e3d3199/docs/design/persona-distill-forge.md) — Evidence `78ba4d9be35e0241eb5f86a4`
11. [TencentCloud/TencentDB-Agent-Memory@97f94654280b2932c35ba4806a491999ed244cc9:MemoryCore/Dockerfile](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/97f94654280b2932c35ba4806a491999ed244cc9/MemoryCore/Dockerfile) — Evidence `1879da8cdc20aaea25ede65c`
12. [TencentCloud/TencentDB-Agent-Memory@97f94654280b2932c35ba4806a491999ed244cc9:MemoryCore/Dockerfile](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/97f94654280b2932c35ba4806a491999ed244cc9/MemoryCore/Dockerfile) — Evidence `6de50efd7dd6779d955d942a`
13. [TencentCloud/TencentDB-Agent-Memory@97f94654280b2932c35ba4806a491999ed244cc9:MemoryCore/README.md](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/97f94654280b2932c35ba4806a491999ed244cc9/MemoryCore/README.md) — Evidence `a53eaf05e9e36a79f063b7ea`
14. [TencentCloud/TencentDB-Agent-Memory@97f94654280b2932c35ba4806a491999ed244cc9:MemoryCore/README.md](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/97f94654280b2932c35ba4806a491999ed244cc9/MemoryCore/README.md) — Evidence `21caa43672cc9f52c6c746a1`
15. [TencentCloud/TencentDB-Agent-Memory@97f94654280b2932c35ba4806a491999ed244cc9:MemoryCore/README.md](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/97f94654280b2932c35ba4806a491999ed244cc9/MemoryCore/README.md) — Evidence `b7389632d90d5c3be6a231f3`
