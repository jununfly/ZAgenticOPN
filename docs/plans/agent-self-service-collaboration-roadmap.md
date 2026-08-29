<!-- ROADMAP_SECTION_START -->
## ZJ Roadmap

> 数据文件: `agent-self-service-collaboration-roadmap.json` | 最后更新: 2026-08-29 11:45:11

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

### 当前施工：1-2-1-5. 同设备多 Agent 个人重度使用与正式使用准备

**决策：**
- Q: 同设备多 Agent 个人正式使用准备的范围是什么？ → 围绕现有同设备、多 Agent、单项目最小闭环，补齐产品 owner 日常重度使用所需的可用性、稳定性、可回滚发布和持续观察；Human 以真实日常工作使用，不再扩展跨设备、多项目或自动化能力。 (分类：stage-critical，服务当前个人使用目标；产物必须来自真实使用和 canonical Git facts。private dogfood 不等于公开生产发布，不自动改变 active Spec 的 Experience Version 阶段；认证、HA、灾难恢复、自动发现、完整 Dashboard 和团队治理继续 Deferred。)
<!-- ROADMAP_SECTION_END -->
