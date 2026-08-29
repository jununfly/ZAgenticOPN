# 用户侧正式发布与部署设计评审

## One-page overview

### Decision

Decision: accepted for owner-only private dogfood；持续观察。

推荐采用“版本化、不可变的用户侧发布物 + 独立 runtime + host-level
WorkBuddy 插件 + 用户数据目录”的部署形态。`0.1.0-rc.4` 已从 clean commit
构建，并在真实用户 WorkBuddy 配置中完成 marketplace 注册、user-scope 安装、
启用、doctor、workspace binding、任务无关 activation、结果 review 和 rc.4↔rc.3
回滚往返。正式安装链路的 blocking 验证已闭合；三项日常真实任务的长期可用性观察
仍待 Human 继续积累。active Spec 的 owner-only formal release 边界已完成同步。
当前 owner 分发渠道冻结为“解压 release bundle 后双击或执行顶层
`Install.command`”；signed `.pkg`/`.dmg` 和更长期的数据保留仍是 non-blocking
open decisions，可在不改变产品部署契约的前提下后续选择。

### Summary

产品 owner 的 private dogfood 也必须像正式产品一样安装到用户侧：WorkBuddy
通过用户级安装的 host plugin 调用已发布的 runtime，不从消费项目或
ZAgenticOPN 工作树导入 Python 包。消费项目只作为 Agent 修改目标和显式
`CollaborationScope` 绑定的来源；产品配置、shared context、事件和安装版本均
由用户侧产品目录管理。

### Platforms and scope

- 当前目标平台：产品 owner 使用的 macOS 用户账户；首个发布只覆盖已验证的
  WorkBuddy/CodeBuddy host 和同设备、单项目、多 Agent 场景。
- 发布物包含：ZAgenticOPN runtime、稳定启动入口、版本 manifest、WorkBuddy
  host integration、顶层 `Install.command`/`Uninstall.command` 和安装/升级/回滚/
  卸载工具。
- 用户数据包括 host runtime 配置、同设备 shared SQLite、事件和本地备份；不
  放入消费项目仓库。
- 受影响的现有表面：
  [WorkBuddy integration](../../integrations/workbuddy/README.md)、
  [WorkBuddy hook](../../integrations/workbuddy/hooks/user-prompt-submit.py)、
  [runtime config](../../zagentic_opn/runtime_config.py) 和
  [activation runner](../../zagentic_opn/activation_runner.py)。
- 明确排除：跨设备/多项目能力、自动发现/唤醒、后台 daemon、公共多用户发布、
  HA、生产级认证与 ACL、团队治理，以及 ZAgenticLoop 代码复用。

### Ownership and tracking

- 决策 owner：Human / 产品 owner。
- 产品与协议 owner：ZAgenticOPN；WorkBuddy host integration 也由本仓库的
  release 维护，不由消费项目 `AGENTS.md` 维护。
- 安装、用户数据、备份和回滚责任：产品 owner 的用户账户；首版不承诺外部
  用户支持或自动更新。
- 跟踪：roadmap `1-2-1-5-4`；上位节点为
  `1-2-1-5`「同设备多 Agent 个人重度使用与正式使用准备」。
- 证据入口：
  [active Experience Version Spec](../prds/agent-self-service-collaboration-experience-version.md)、
  [current repository README](../../README.md) 和
  [current coordination seam](../../docs/experience-version-coordination.md)。

## Problem and goals

### User/job and current baseline

此前 hook 由 `${CODEBUDDY_PLUGIN_ROOT}/hooks/user-prompt-submit.py` 启动，再以
`ZAGENTICOPN_SOURCE_ROOT`、`PYTHONPATH` 和 `python -m zagentic_opn.activation_runner`
找到源码。当前分支已将 hook 收窄为标准库桥接，并把这些路径从 runtime 子进程中
清除；临时 RC 证明了新路径可工作，但正式 release 仍需 clean tag、真实 host
注册和 owner canary。

### Goals

- 用户从一个版本化 release artifact 安装产品，激活任意已配置的消费项目时不
  需要 checkout、import 或 `PYTHONPATH` 指向 ZAgenticOPN 源码。
- WorkBuddy host plugin 与 runtime 版本可识别、可校验、可一起升级或回滚。
- 产品配置、shared context、事件、日志和备份有稳定的用户侧位置；消费项目不
  持有产品数据库或产品代码。
- 保持现有产品语义：Human 任务无关激活，Agent 自行 discover/claim/review，
  scope 显式绑定，结果引用 canonical Git facts。
- 用户可以在不依赖开发者现场救火的情况下完成安装、配置、健康检查、升级、
  回滚和卸载。

### Non-goals

- 不把 private dogfood 变成公开发布、多用户 SaaS 或生产级运行承诺。
- 不为跨设备或多项目提前引入远程协调服务、全局调度、自动发现或自动唤醒。
- 不把消费项目的源码、`AGENTS.md`、Git remote 或 cwd 变成产品 runtime 的
  代码来源；cwd 只允许参与用户已配置的显式 workspace-to-scope binding。
- 不在本评审中决定单文件打包工具、签名服务供应商或未来跨平台发行策略。

### Assumptions and constraints

- 同设备 shared context 继续使用本地 SQLite；短生命周期 activation 进程仍可按
  请求启动，不需要 daemon。
- Host 能够安装用户级 plugin，并在提交模型请求前注入结构化 handoff；不满足该
  host capability 时必须 fail closed。
- 发布物由 Git tag/commit 构建，包含可验证的版本和 checksum；安装器不执行
  来自消费项目的安装脚本。
- active Spec 现已允许 owner-only 用户侧正式发布，同时继续把公开部署、多用户
  支持和生产级运行列为 deferred；在 release candidate 通过前，本文的部署设计
  仍是 proposed，而不是已发布能力。

### Success definition

产品 owner 在一个没有 ZAgenticOPN checkout、没有项目级 `PYTHONPATH` 的干净用户
环境中安装一个 release，配置一个消费项目后，仅通过 WorkBuddy 的任务无关激活
完成同设备 publish → discover → claim → result → review 闭环；升级、失败回滚
和卸载均有可复核结果，且产品数据不落入消费项目仓库。

## Design

### Alternatives considered

| 方案 | 结论 | 原因 |
| --- | --- | --- |
| 消费项目 checkout + `PYTHONPATH`/`python -m` | reject | 版本和代码来源依赖工作树，无法作为用户侧正式 release；当前 hook 正是此形态。 |
| 每个消费项目复制一份 runtime 或加入项目脚本 | reject | 产生多份产品事实源和升级漂移，重新引入 Human/项目维护负担。 |
| 直接 `pip install -e` 或系统 Python 安装 | reject | 仍依赖开发环境和宿主 Python，不能可靠表达 runtime/plugin 的成对版本，也难以原子回滚。 |
| 用户侧版本化 release bundle + stable launcher | recommend | 与同设备、短生命周期、无 daemon 的当前语义匹配；可隔离版本、数据和插件，支持升级/回滚。 |
| 常驻本地服务或远程 coordination service | defer | 解决的是后台运行、远程共享和多设备问题，超出当前 private dogfood 的最小证据。 |

### Chosen deployment shape

一个 release artifact 内含两个必须成对校验的部分：

1. **Runtime**：发布版 coordination/activation runtime、稳定启动入口、配置/健康
   检查/备份/迁移命令。runtime 可以先使用发布物内的隔离 Python 环境，或在
   clean-room spike 通过后改为 self-contained executable；这不改变安装契约。
2. **Host integration**：版本匹配的 WorkBuddy plugin manifest、hook 和 host
   适配配置。hook 只调用已安装 runtime 的稳定入口，不插入源码目录、不设置
   项目级 `PYTHONPATH`，也不从消费项目加载 Python 模块。

用户级安装目录建议如下；最终目录名由安装器实现，但所有权和分层必须保持：

```text
~/Library/Application Support/zagenticopn/
├── versions/<release-id>/       # 不可变的 runtime + host integration payload
├── current                     # 原子切换的当前 release 指针
├── runtime.json                # 用户级配置：store 与显式 workspace/scope binding
├── data/shared.sqlite3         # shared context、claims、events
├── backups/                    # 升级前的可恢复副本
├── logs/                       # 本地诊断，不含完整对话
└── install-manifest.json       # release、contract、路径与 checksum
```

WorkBuddy plugin 通过官方 host CLI 的 user scope 注册；release installer 先把
release 内的 `host-integration` 作为 directory marketplace 加入 host，再调用
`plugin install <plugin>@<release-marketplace> --scope user` 并显式执行
`plugin enable <plugin>@<release-marketplace> --scope user`。directory marketplace
的实际 source path 因而仍位于用户侧不可变的 `versions/<release-id>`，而不是
仓库 checkout；installer 不手写 `installed_plugins.json`。WorkBuddy CLI 当前可
从 `/Applications/WorkBuddy.app/Contents/Resources/app.asar.unpacked/cli/dist/codebuddy.js`
调用，且使用 `CODEBUDDY_CONFIG_DIR=$HOME/.workbuddy` 指向 WorkBuddy 用户配置。
CodeBuddy 可传入其对应的用户配置目录；具体 host 安装命令属于外层分发说明，
不进入消费项目。

`Install.command` 是正式 release 的开箱即用入口：它自动探测支持的 host
CLI/Node，调用同一 `install_release.py setup` 流程，初始化用户级目录，接受
显式的 workspace/scope 首次绑定，并在最后运行 `doctor`。高级 `install`、
`doctor` 和 `rollback` 命令仍保留给自动化、诊断和回滚；安装入口不推断 scope，
也不修改消费项目。

### Install and activation flow

```text
Human installs release artifact
  → installer verifies manifest/checksum and activates versions/<release-id>
  → installer registers matching host plugin and creates user data/config directories
  → Human configures explicit workspace_root → CollaborationScope binding
  → WorkBuddy prompt “检查 shared context”
  → user-level plugin → stable installed runtime launcher
  → runtime reads user config/data, discover/claim, returns receipt
  → host injects handoff; Agent works in the consumer repo
  → installed runtime receives result/review events; Git remains canonical artifact
```

产品 runtime 与消费项目的边界是：消费项目只提供任务 workspace 和 Git artifact；
产品 runtime 提供 identity/scope、eligibility、Work Item lifecycle、claim、result/
review 和 scorecard。Agent 可以修改消费项目文件，但 activation、shared context
和事件不能通过消费项目里的产品源码完成。

### Configuration and data

- 首次安装生成最小用户级配置；`shared_store_path` 指向产品 data 目录内的
  SQLite，不默认写入任何消费项目的 `.zagenticopn`。
- workspace-to-scope binding 是用户配置，不是消费项目代码；绑定必须是显式、
  可审计、可删除的绝对 workspace root 和 scope 对。
- 配置写入继续使用原子替换和严格 schema；新旧 runtime/plugin 的 contract
  version 必须在启动前校验，不能静默接受混用版本。
- shared context 只保存结构化工作事实、事件和 Git references；不保存完整对话、
  代码副本或大文件。
- 用户可用 `doctor`/`status` 查看当前 release、config、store、plugin 和 scope
  binding；诊断输出不得泄露凭证或完整任务内容。

### Upgrade, rollback, and uninstall

1. **Upgrade**：下载/获取新 release → 校验 manifest/checksum → 安装到新的
   `versions/<release-id>` → 备份 SQLite 和 runtime config → 通过 host CLI 注册
   release-local marketplace 和匹配 user-scope plugin → 校验 plugin/runtime
   contract → 原子切换 `current` → 执行 clean activation smoke。
2. **Pause conditions**：manifest/checksum 不匹配、plugin/runtime contract 不兼容、
   store backup 失败、scope binding 有歧义、clean activation 没有 receipt，均不
   切换 current。
3. **Rollback**：切回上一个已知 release 指针；若 schema migration 已发生，使用
   对应备份恢复或执行已验证的向后迁移。不得只回滚 hook 而保留不兼容的 runtime
   或数据库。
4. **Uninstall**：顶层 `Uninstall.command` 要求 Human 确认，读取 install marker
   和每个 release manifest，通过官方 host CLI 停用/卸载对应 user-scope plugin
   并移除对应 marketplace；默认移除整个用户产品目录，也可用 `--keep-data`
   保留 runtime config、shared context、backups 和 logs。卸载不能删除消费项目
   源码或 Git artifact。

### Ownership and compatibility

- ZAgenticOPN release 维护 runtime、plugin、manifest、storage schema migration
  和 doctor/rollback 命令。
- WorkBuddy 只提供 host hook 生命周期和 handoff injection；它不拥有产品的
  scope、claim 或结果语义。
- 消费项目 owner 只负责项目本身的 Git、任务 acceptance 和 workspace 路径；不
  负责安装产品 runtime，也不需要修改项目 `AGENTS.md`。
- manifest 至少声明 product release、runtime/plugin build、activation contract、
  runtime-config contract、storage schema 和支持的 host capability。任一必须匹配
  的字段不兼容时，结果是结构化 `invalid_runtime_config`/`unsupported_host`，而非
  猜测或降级执行。

## Metrics and experiments

| 指标 | baseline | unit | method | target/threshold | owner |
| --- | --- | --- | --- | --- | --- |
| clean-room install pass | `0.1.0-rc.4`：1/1；临时 clean-room 与真实用户目录均通过 | 安装次数 | 在无 checkout、无项目 `PYTHONPATH` 的用户目录记录 installer + doctor receipt | 首个发布候选 1/1 通过 | Agent；Human 复核 |
| source-tree coupling | rc.4 owner canary：0 次读取产品源码树 | activation 次数 | 记录 installed hook 子进程 argv/env/path，并在消费项目外启动 | 正式发布激活中 0 次读取产品源码树 | Agent |
| activation receipt success | owner canary：1/1 | 有效 activation | 从 host plugin 输出与 product shared event 对账 | 连续 3 个真实日常任务无安装/runner 路径失败 | Human |
| upgrade/rollback pass | rc.3→rc.4→rc.3→rc.4：1/1 | 发布切换次数 | 新旧 release、备份和回滚的固定 fixture 与真实用户目录往返 | 1/1 升级通过；故障演练 1/1 可回滚 | Agent |
| product-caused Human intervention | 尚未测量 | 每个真实任务的动作/分钟 | 单独记录安装、配置、runner 修复和恢复动作，不混入任务特定操作 | 稳定使用后不需要每任务手工修复；异常按事件归因 | Human |
| data leakage to consumer repo | owner canary：0 个产品文件进入消费项目 repo | 任务/安装次数 | 检查 repo diff、未跟踪文件、产品目录和 shared event references | 产品数据库、日志和 plugin payload 不出现在消费项目 repo | Agent |

实验不比较 Agent 总耗时；首先验证“正式安装确实是产品路径”，再观察日常使用
中的有效 activation、接续、失败和 Human 成本。所有 baseline 未测量的项目必须在
clean-room 阶段补齐，不能把当前源码运行结果当作安装结果。

当前 RC 观察结果（2026-08-29）：`0.1.0-rc.4` 从 commit
`0f4d29bfeb60e61505dcdc3e5e5db863a8669568` 构建为 macOS arm64 bundle，manifest
标记 `source_tree_dirty=false`。真实用户目录安装后，官方 WorkBuddy CLI 显示
rc.4 为 user-scope enabled，rc.3 与旧 `zagenticopn-local` 为 disabled；doctor
healthy。owner canary 在真实 `ZAgentic` workspace binding 上完成
publish→claim→publish_result→review→completed，7 条关联事件可对账，消费项目无
产品 runtime/data 文件。全量仓库测试现为 31/31 通过。

## Rollout, recovery, and lifecycle

### Rollout

1. **Release candidate**：`0.1.0-rc.4` 已从固定 clean commit 构建，生成 manifest
   和 checksum；临时 clean-room、真实用户级 host registration、doctor 与
   rc.4↔rc.3 rollback 往返均通过。
2. **Owner canary**：已在产品 owner 的真实同设备 scope 中执行一个可回滚的低风险
   Work Item；对账 receipt、events、Git reference 和 repo diff，结果已由 reviewer
   Agent 接受。日常三任务的长期观察仍由 Human 继续记录。
3. **Private dogfood**：current release 指向通过 canary 的版本，产品 owner 在
   日常工作中持续使用；按周记录安装/activation 错误、恢复动作、完成率和效率
   缺口，不自动扩大到跨设备、多项目或其他用户。

### Pause and rollback

发布必须暂停的条件：runtime 从消费项目加载代码、plugin/runtime 版本不匹配、
scope 未显式绑定、shared store 不可读写、activation 没有结构化 receipt、结果
provenance 丢失、升级后事件或 Git artifact 无法对账。回滚使用上一份 immutable
release 和升级前 data backup；回滚后重新执行最小 activation smoke，再恢复日常
使用。

### Lifecycle

本设计服务当前 `1-2-1-5` 的个人正式使用目标，但不自行把 Experience Version
晋级为 Dogfood 或公开发布阶段。用户侧正式安装是 owner-only private dogfood 的
交付方式；公开发行、多人支持、生产 SLO、远程共享、HA、自动更新和团队治理仍
保持 deferred，除非 Human 另行改变 active Spec。

## Principle considerations

### Performance

同设备 runtime 仍为按请求启动的短生命周期进程，SQLite 保持本地；正式发布新增的
启动开销、hook timeout 和磁盘占用必须通过 clean activation benchmark 测量。目标是
单次 activation 在当前用户可接受的交互窗口内完成，具体阈值在首个 release candidate
上以现有 WorkBuddy hook timeout 为上限冻结。不会为尚未观察到的规模问题引入 daemon
或远程服务。

### Simplicity and accessibility

用户只需要运行 release 顶层 `Install.command`，按向导配置一次 workspace/scope
binding；入口自动完成 host plugin 安装和 doctor，日常仍只输入“检查 shared context”。
安装器必须提供清晰的当前版本、
失败原因、修复动作和回滚入口；不要要求用户理解 Python、`PYTHONPATH` 或仓库
内部布局。CLI 文案和诊断输出应支持复制、键盘操作和纯文本审阅。

### Security and privacy

信任边界是 release artifact、用户级 host plugin、已安装 runtime、用户配置/data
目录和消费项目 Agent workspace。安装器验证 release checksum/签名，hook 严格解析
host payload，不拼接 shell 命令，不从消费项目导入代码。runtime 不读取完整对话，
不把 shared context 上传远端；配置、SQLite、备份和日志使用用户账户权限，敏感
路径和内容不写入 scorecard。Agent 在消费项目执行的 Git/文件操作继续受 host
审批和现有安全边界约束；本产品不借安装过程提升权限。

## Testing and validation

| 场景 | 环境/行为 | 预期观察 | 阈值 | owner |
| --- | --- | --- | --- | --- |
| clean-room install | 临时用户目录；产品 checkout 不在 `PATH`/`PYTHONPATH`；安装 release | manifest、current pointer、runtime、plugin 和 user data 创建成功 | 1/1；0 个源码树 import | Agent |
| consumer isolation | 任意临时消费 repo 只配置 workspace/scope binding | hook 从 user-level plugin 调用 installed launcher；repo 无产品代码/数据库 | 0 个产品文件进入 repo | Agent |
| task-agnostic activation | WorkBuddy 提交精确 alias；host capability 已声明 | shared event 出现 discover→claim，receipt 可注入 handoff | 连续 3 个真实任务均可对账 | Human |
| invalid configuration | 删除/篡改 runtime config、scope binding 歧义、store 不可写 | 返回结构化 failure，不 claim、不创建替代 Work Item | 100% fail closed | Agent |
| version skew | plugin 与 runtime 使用不匹配版本 | 在 claim 前返回兼容性错误并给出 repair action | 100% reject mixed pair | Agent |
| upgrade | 安装新版本，运行 storage/config migration 和 smoke | backup、migration、current switch、receipt 均可追踪 | 1/1 成功 | Agent |
| rollback | 故意让新版本 smoke 失败，回到上一版本 | current、plugin、store 恢复到一致组合，旧事件仍可读 | 1/1 成功，无数据丢失 | Agent/Human |
| uninstall | `Uninstall.command` 经确认后卸载所有 manifest 声明的 release；可选择保留数据 | host plugin/marketplace 清理完成，consumer repo/Git artifact 不受影响，产品数据按选择处置 | 1/1；无越界删除 | Human |

可复现命令与 fixture 必须在实现阶段固定；当前仓库的
`python -m unittest discover -s tests -v` 只能证明源码层行为，不能替代 clean-room
安装、版本切换和 host plugin 验收。

已执行的正式命令链为：clean build `0.1.0-rc.4` → 真实 user-root install → 官方
WorkBuddy CLI marketplace add/install/enable → runtime configure → `doctor` →
installed hook 在真实 consumer workspace 完成 task-agnostic activation →
publish-result → submit → review → completed → rollback to `0.1.0-rc.3` → `doctor`
→ rollback back to `0.1.0-rc.4` → `doctor`。旧开发 plugin 保留但 disabled；产品
SQLite 位于用户侧 data 目录，未写入消费项目。

## Open decisions

| Question | Evidence needed | Owner | Due/exit condition |
|---|---|---|---|
| Runtime 首版使用 self-contained executable 还是发布物内隔离 Python 环境？ | 两种 spike 的安装体积、启动时间、macOS 架构兼容和 hook 调用结果 | Agent + Human | 首个 release candidate 构建前冻结；两者均不得读取源码树 |
| macOS 外层分发是否升级为 signed `.pkg` 或 `.dmg`？ | 签名服务、权限模型和卸载体验 | Human | 当前 release bundle + `Install.command` 已满足 owner-only；只有进入更广发布范围才重开 |
| WorkBuddy 用户级 plugin 的注册 API/目录是什么？ | 干净 host 上的官方 CLI marketplace add/install/enable 和 plugin reload 行为 | Human + Agent | 已由真实用户配置 rc.4 验证；后续仅跟踪 host 版本兼容 |
| `runtime.json` 与 storage schema 如何携带 release/contract 版本？ | migration fixture、混用版本负向测试和备份恢复结果 | Agent | version-skew 与 rollback gate 全通过 |
| 个人数据的备份、保留和删除默认值是什么？ | owner 对 shared context、events、logs、backups 的处置选择 | Human | 首次真实日常使用前书面确认 |

## Review record

| Reviewer | Date | Concern | Response or decision | Remaining risk |
|---|---|---|---|---|
| Codex | 2026-08-29 | 当前方案把源码工作树当作 runtime，不能作为正式用户侧产品路径。 | 建议版本化 release bundle、user-level runtime、host-level plugin、独立 data/config 和原子升级/回滚。 | 等待 clean-tag release、host CLI registration 和 owner canary。 |
| Human | 2026-08-29 | private dogfood 不能通过跨项目直接调用本仓库代码，必须按正式产品发布到用户侧。 | 本评审已将该要求提升为 `1-2-1-5-1` 的 deployment contract；active Spec、README 和 integration 说明已同步。 | 等待 clean-tag release、真实 host registration 和 owner canary。 |
| Codex | 2026-08-29 | RC 是否真的脱离源码树？ | `0.1.0-rc.2` clean-room fixture 通过，30/30 自动化测试通过，rollback 与版本配对通过；manifest 如实标记 dirty working tree。官方 host CLI 的用户级 marketplace add/install 已由隔离配置探针确认，尚未在真实用户配置执行。 | clean-tag 构建、真实 WorkBuddy host 用户级注册和 owner canary 仍未完成。 |
| Codex | 2026-08-29 | clean release 与真实用户安装是否闭合？ | `0.1.0-rc.4` 从 clean commit 构建，真实 WorkBuddy user-scope plugin registration/enable、workspace-bound owner canary、事件/Git/repo 对账和 rc.4↔rc.3 rollback 往返均通过；31/31 全量测试通过。 | 仍需 Human 在日常使用中积累 3 个真实任务的 activation/失败与效率观察；不阻塞本安装节点。 |
| Codex | 2026-08-29 | 用户仍需理解 Python、host CLI 路径和多段安装命令，是否算正式开箱即用？ | release bundle 新增顶层 `Install.command`，自动探测 WorkBuddy/CodeBuddy 与 Node，执行用户级安装、最小配置初始化、显式首次绑定和 doctor；新增 clean-room black-box 覆盖双击/终端入口。 | 解压仍是当前分发前提；signed `.pkg`/`.dmg` 继续 deferred。 |

### Short-read acceptance

当前 decision 已接受为 owner-only private dogfood 交付方式。正式安装节点的阻断项
已闭合：clean release、真实 user-scope registration、0 次源码树耦合、一次真实
workspace-bound canary 和 1/1 rollback 往返均有证据。后续仅保留 Human 的长期观察：
连续 3 个真实日常任务 activation 可对账，并记录安装/runner 失败、Human 介入与效率
缺口；该观察不阻塞本节点完成，也不触发 Experience Version 阶段晋级。
