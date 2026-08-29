<!-- ROADMAP_SECTION_START -->
## ZJ Roadmap

> 数据文件: `agent-self-service-collaboration-roadmap.json` | 最后更新: 2026-08-29 14:00:19

[~][X+] 1. ZAgenticOPN Agent 自服务协作
├── [x][Y+] 1-1. 阶段 0：问题发现与候选方案选择
│   ├── [x][Y+] 1-1-1. 形成目标、需求与产品假设基线
│   ├── [x][Y+] 1-1-2. 完成候选无关 Spec 与技术设计
│   ├── [x][X+] 1-1-3. 对比新开源方案与当前候选基线
│   ├── [x][X+] 1-1-4. Human 确认 A/B/C/D 技术决策
│   ├── [x][Y+] 1-1-5. Feature 1 对齐契约：冻结 Q1–Q6
│   ├── [x][Y+] 1-1-6. 将 Feature 1 对齐草案转为 Experience Version Spec
│   ├── [x][X+] 1-1-7. 下一轮最多 3 个 ext 候选筛选与 C1–C4 黑盒复验
│   └── [x][Y+] 1-1-8. C 路线选择性复用能力地图与实施准入
├── [~][Y+] 1-2. 阶段 1：Agent 自服务协作体验版
│   ├── [~][Y+] 1-2-1. 同设备 Codex → WorkBuddy → Codex 闭环
│   └── [ ][X+] 1-2-4. Agent private context 中断恢复
├── [x][X+] 1-3. 阶段 2：协作价值重复验证
│   ├── [x][X+] 1-3-1. 运行人工方案 A 对照实验
│   ├── [x][X+] 1-3-2. 每道协作门连续通过 3 次
│   └── [x][X+] 1-3-3. 基于产品健康指标判定有用性
└── [ ][X+] 1-4. Deferred：后续生命周期能力
    ├── [ ][X+] 1-4-1. 评估自动发现、通知与设备唤醒
    ├── [ ][X+] 1-4-2. 按真实失败建设生产可靠性
    └── [ ][X+] 1-4-3. 个人闭环有效后评估团队治理

### 当前施工：1-2-1-5-2. 真实 WorkBuddy 用户级安装与 owner canary

**决策：**
- Q: 真实 WorkBuddy 用户级插件如何注册？ → 通过 host 官方 CLI 的用户级路径注册 release 自带的 directory marketplace：先将 host-integration 目录作为不可变 release marketplace 加入用户 host，再以 --scope user 安装匹配插件；host registry 的 installPath 必须解析到用户侧 versions/<release-id>，不能指向仓库 checkout，也不能手写 host registry。 (已通过 WorkBuddy app 内置 codebuddy CLI 的临时 CODEBUDDY_CONFIG_DIR 探针确认 add/install/list 流程。正式 installer 将校验 host CLI、传入对应配置目录，并在版本化 release 目录执行 marketplace 注册；不执行真实用户配置切换，直到 clean RC 产生。)
- Q: 版本化 marketplace 升级时如何避免重复 hook？ → 每个 release 保留自己的不可变 marketplace 以支持回滚，但 host user scope 同时只能启用当前 release 的 ZAgenticOPN plugin；安装或 rollback 新 pair 成功后，通过官方 host CLI disable 其它 zagenticopn-release-* plugin，不卸载其 marketplace。 (directory marketplace 的 source path 必须保留用于回滚；只禁用旧 plugin 可避免重复 UserPromptSubmit hook，也不破坏已安装 release。doctor 要验证当前 plugin enabled 且 host CLI 可读。)
<!-- ROADMAP_SECTION_END -->
