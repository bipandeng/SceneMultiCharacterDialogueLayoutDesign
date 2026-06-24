---
title: LinguaScene Grill 完整设计全景 Q1-Q20
date: 2026-06-23
tags: [LinguaScene, 产品设计, grill-me, 场景对话, 角色系统, 学习系统, 未来功能]
status: 已对齐,待实施
source: grill-me skill 输出
related:
  - 2026-06-19-LinguaScene_场景化对话统一入口_用户自创角色.md
  - 2026-06-19-假数据-后端填充-接口接入清单.md
---

# LinguaScene — Grill 完整设计全景（Q1-Q20）

**状态**: Q1-Q20 已对齐;L1 引擎层升级为 AutoGen+CAMEL 混合架构;L4 新增场景生命周期管理
**日期**: 2026-06-23 (初始) / 2026-06-24 (引擎选型 + 场景生命周期)
**驱动**: grill-me skill,基于 PDF 论文 CAMEL (arXiv:2303.17760v2, NeurIPS 2023)

---

## 1. 用户战略意图

> 用户从论文 CAMEL 的多 AI 角色对话出发,转向 C 端英文学习 App:
> - **App 本质**: 场景化口语练习工具(买菜/买衣服/面试等)
> - **核心定位**: 用户**必须讲出来**(speaking 为主,typing 辅助)
> - **核心差异化**: NPC 可**主动插话**;记忆归场景、角色无状态
> - **教学闭环**: 收藏 → 复习 → 场景化老朋友重逢
> - **拒绝**: 纯模板驱动导致的"教学感太重"

## 2. 核心结论摘要

```
┌──────────────────────────────────────────┐
│  L4 交互层                                  │
│  • 模式 D:自然 + Checkpoint 渐进式          │
│  • 输入:实时转写 + 可编辑 + 语音           │
│  • 浮动 UI:右侧集合卡 + 高亮 + 首次叮       │
│  • 卡壳:D "怎么说?"按钮 + F NPC 自然接话  │
│  • 多人:插话提示 + 用户点播放              │
│  • NPC 输出:TTS 调度 + 用户可关           │
│  • 插话机制:C 触发 + D 推进                │
│  • 场景暂停/恢复:suspended + 24h 超时     │
│  • 已完成场景:看历史/再来一次/接着聊      │
├──────────────────────────────────────────┤
│  L3 学习层                                  │
│  • 收藏:点击 NPC 词/句 → 收藏              │
│  • 复习 C:场景化老朋友重逢                 │
│  • 复习 D:每日/进 App 闪卡                 │
│  • 分层:用户报目标 → CEFR 映射             │
├──────────────────────────────────────────┤
│  L2 内容层                                  │
│  • Schema C 分层(模板 + 实例)              │
│  • 15 场景类型骨架(MVP 先 5 个)            │
│  • 角色:模板预设 + 用户自定义 + 取消       │
│  • NPC 数量:按场景动态 1-4 个              │
│  • 完成度:必选 beat + Checkpoint 60% +      │
│    失败 2 次自动跳过                        │
├──────────────────────────────────────────┤
│  L1 引擎层                                  │
│  • AutoGen 骨架 + CAMEL 思想(混合架构)    │
│  • 角色无记忆,会话 = 场景 + 角色组合      │
│  • 多 NPC 扇出,TTS 调度避免冲突           │
│  • selector_func 实现 beat 状态机 + 插话   │
│  • EngineAdapter 隔离层,不直接依赖 AutoGen│
└──────────────────────────────────────────┘
```

---

## 3. 已锁定决策（按层 ID 化）

### L1 对话引擎层

| ID | 决策 | 来源 Q | 状态 |
|---|---|---|---|
| L1-001 | 对话引擎采用 **AutoGen(CAMEL 思想混合)**: AutoGen 提供多 agent 编排骨架,`system_message` 注入 CAMEL Inception Prompting,`selector_func` 实现 Critic 双重判定 | Q1 + 2026-06-24 引擎选型 | 已锁 |
| L1-002 | **角色无记忆**: 角色是无状态 persona,每次 `scene_session` 重建 agent 实例,不携带历史 | Q3 修正 | 已锁 |
| L1-003 | **记忆归场景 + 场景可暂停/恢复**: 对话历史 `Mt` 归属 SceneSession,永久存储;场景支持 `suspended` 状态,用户可随时恢复;恢复时仅加载当前 beat 内的 Mt 到 agent context | Q3 + 2026-06-24 生命周期 | 已锁 |
| L1-004 | **会话实例 = 场景 + 角色组合**: 不存在跨 session 的角色记忆 | Q3 + 论文 3.1 兼容 | 已锁 |
| L1-005 | 多 NPC 扇出结构(场景模板 NpcCount 字段定义 1-4 个) | Q18 | 已锁 |
| L1-006 | TTS 智能调度: 同一时刻仅 1 个 NPC 在说,其他 NPC 通过"💬 想说话"提示待用户点播 | Q9 | 已锁 |
| L1-007 | 角色翻转(role flipping)从"被消灭的异常"重新定义为"被编排的插话功能" | Q10 | 已锁 |
| L1-008 | Critic 角色改造: 不只评回复质量,还判"插话时机"和"教学覆盖率" | Q10 + Q14 衍生 | 已锁 |

### L2 内容层

| ID | 决策 | 来源 Q | 状态 |
|---|---|---|---|
| L2-001 | **C 混合分层**: 官方模板(15 个场景类型骨架) + 用户/系统实例化 | Q5 | 已锁 |
| L2-002 | **错题本系统不做** | Q5 用户明确 | 已锁 |
| L2-003 | **Schema C 分层**: 模板层(`vocabulary_pool`、`patterns_pool`、`beats_template`) + 实例层(`selected_vocabulary`、`selected_patterns`、`current_beat`、`user_progress`) | Q14 | 已锁 |
| L2-004 | **NPC 数量按场景动态**: 每场景类型有 `npc_count: { min, max }` 字段,LLM 实例化时按此生成 | Q18 | 已锁 |
| L2-005 | **场景完成度**: 必选 beat 必走完 + Checkpoint 通过率 ≥ 60% + 失败 2 次自动跳过 | Q19 (D + E) | 已锁 |
| L2-006 | **角色支持用户自定义**: 用户可取消模板预设角色 + 加入自创角色,LLM 实例化按用户选择生成最终角色列表 | Q18 用户追加 | 已锁 |
| L2-007 | **MVP 5 场景**: 餐厅 / 机场 / 面试 / 购物 / 社交聚会 | Q20 | 已锁 |
| L2-008 | **Schema 实例可继承老朋友**: NPC 台词生成从 `selected_vocabulary` ∩ `user_collected_words` 选词,实现场景化复习 | Q13 (C) | 已锁 |

### L3 学习层

| ID | 决策 | 来源 Q | 状态 |
|---|---|---|---|
| L3-001 | **收藏系统**: 点击 NPC 消息中的单词/句型 → 弹出详情卡(释义+例句) → 用户点"收藏"入库 | Q5 用户追加 | 已锁 |
| L3-002 | **不自动校准**: 取消嵌入式动态校准,用户冷启动时直接报目标即可 | Q17 用户修正 | 已锁 |
| L3-003 | **用户分层 = 目标考试 → CEFR 映射**: 雅思 5-6/托福 60-90 → B1;雅思 7+/托福 100+ → C1;四六级 425/日常口语 → A2 | Q17 简化版 | 已锁 |
| L3-004 | **用户可在设置手动改层级**,但不自动升降级 | Q17 | 已锁 |
| L3-005 | **复习 C: 场景化老朋友重逢**: 用户进新场景,NPC 台词自然埋入之前收藏的词 | Q13 | 已锁 |
| L3-006 | **复习 D: 每日/进 App 闪卡**: 3-5 张快速过,FSRS 间隔重复算法 | Q13 | 已锁 |
| L3-007 | **发音反馈时机**: 日常对话不评分;用户主动"听我发音" → 系统回放用户原始语音(自评);场景结束统一评分 | Q8 (H 调整) | 已锁 |
| L3-008 | **发音评分场景**: Checkpoint 测验中可用之前对话中的语音做评分 | Q8 | 已锁 |

### L4 交互层

| ID | 决策 | 来源 Q | 状态 |
|---|---|---|---|
| L4-001 | **模式 D = C 自然模式 + Checkpoint 渐进式**: 默认自然模式,节拍完成后 Checkpoint 渐进式评估(填空→选择→造句) | Q6 (D) | 已锁 |
| L4-002 | **Checkpoint 渐进式**: 按用户层级自适应,低层从填空开始,高层直接造句 | Q7 (E) | 已锁 |
| L4-003 | **Checkpoint 失败兜底**: 失败 1 次给同义例句示范,失败 2 次自动跳过 + 目标句型推复习队列 | Q10 + Q19 | 已锁 |
| L4-004 | **输入 UX = D**: 实时转写 + 可编辑 + 可发原始语音 | Q8 (D) | 已锁 |
| L4-005 | **NPC 输出 = C + D**: TTS + 智能调度 + 用户设置可关 | Q9 | 已锁 |
| L4-006 | **多人插话 UX**: "💬 B 想说话..."提示,用户点才播放 | Q9 | 已锁 |
| L4-007 | **NPC 插话机制 = C + D**: 卡壳触发(C)+ 状态机推进(D);D 优先 | Q10 (E) | 已锁 |
| L4-008 | **浮动 UI = E**: 右侧集合卡 + NPC 消息目标词高亮 + 首次出现"叮"一下 | Q6 + Q11 | 已锁 |
| L4-009 | **卡壳兜底 = D + F**: 用户主动"怎么说?"按钮(D) + NPC 自然接话(F,被动) | Q12 | 已锁 |
| L4-010 | **NPC 自然接话**: 不用教学腔,只接住对话给用户开口空间 | Q12 (F) | 已锁 |
| L4-011 | **场景暂停与恢复**: 点返回 = `suspended`(不是 abandon),AutoGen agent 销毁但数据全存 DB;恢复时重建 agent + 注入当前 beat 的 Mt;超时 24h 自动 abandoned;最多 3 个并行 suspended | 2026-06-24 生命周期 | 已锁 |
| L4-012 | **已完成场景三种入口**: ① 查看历史对话(纯 DB 回放,零 LLM 成本) ② 再来一次(新 session) ③ 接着聊(`free_talk` 模式,关闭 beat 状态机 + checkpoint,NPC 纯角色扮演) | 2026-06-24 生命周期 | 已锁 |
| L4-013 | **历史对话永久存储 + Agent Context 按需加载**: DB 全存(用户说的每句话永久保留,可回看);Agent 只加载当前需要的上下文(当前 beat 的 Mt / free_talk 模式下的滚动摘要);存储 ≠ Agent 上下文 | 2026-06-24 生命周期 | 已锁 |

### L5 语音技术层

| ID | 决策 | 来源 Q | 状态 |
|---|---|---|---|
| L5-001 | ASR 实时转写(Whisper Large-v3 / OpenAI Realtime API / Azure Speech) | Q8 | 待选型 |
| L5-002 | 发音评分 Azure Speech Pronunciation Assessment(仅 Checkpoint 触发) | Q8 | 待选型 |
| L5-003 | TTS ElevenLabs(多音色,质量最优)/ OpenAI TTS / Azure Speech | Q9 | 待选型 |
| L5-004 | VAD 卡壳判定(停顿检测) | Q10 (C) | 待选型 |

---

## 4. 15 场景列表

### Phase 1: MVP 5 场景(SC-001 ~ SC-005,~10 周交付)

| ID | 类型 | npc_count | 必选 beat | 学习目标 | 说明 |
|---|---|---|---|---|---|
| SC-001 | 餐厅 (restaurant) | 1-2 | greeting / ordering | 礼貌点餐、请求替换食材 | 高频,覆盖"餐饮"刚需 |
| SC-002 | 机场 (airport) | 1-2 | check_in / security / boarding | 登机口查询、过海关、登机 | 出境/旅行刚需 |
| SC-003 | 面试 (interview) | 1-2 | greeting / self_intro / qa | 自我介绍、回答行为面试问题 | 求职刚需,痛点强 |
| SC-004 | 购物 (shopping) | 2-3 | browse / try / pay / bargain | 询问款式、试穿、砍价、付款 | 生活必备 |
| SC-005 | 社交聚会 (party) | 3-4 | arrive / mingling / farewell | 自我介绍、闲聊、告别 | 社交场景 |

### Phase 2: V2 5 场景(SC-006 ~ SC-010)

| ID | 类型 | npc_count | 必选 beat | 学习目标 | 说明 |
|---|---|---|---|---|---|
| SC-006 | 酒店 (hotel) | 1-2 | check_in / request_service / check_out | 入住、退房、叫醒服务 | 旅行住宿 |
| SC-007 | 就医 (clinic) | 1-2 | describe_symptom / understand_diagnosis / get_prescription | 描述症状、听懂诊断、取药 | 健康场景,覆盖 AE 词汇 |
| SC-008 | 银行 (bank) | 1-2 | open_account / deposit / transfer / complaint | 开户、存款、转账、投诉 | 金融场景 |
| SC-009 | 酒店/餐厅电话预订 (phone) | 0-1 (电话另一端) | greeting / request / confirm / close | 电话礼仪、预订确认 | 电话英语独立场景 |
| SC-010 | 租房 (rental) | 1-2 | inquiry / tour / negotiate / sign | 询问租金、看房、谈判、签约 | 生活刚需 |

### Phase 3: V3 5 场景(SC-011 ~ SC-015)

| ID | 类型 | npc_count | 必选 beat | 学习目标 | 说明 |
|---|---|---|---|---|---|
| SC-011 | 交通 (transit) | 1-2 | ask_directions / buy_ticket / report_lost | 问路、买票、报失 | 打车、地铁 |
| SC-012 | 社交媒体 (social_media) | 1 | reply / send_message / unsubscribe | 文字沟通、礼貌拒绝 | 现代刚需 |
| SC-013 | 维修 (maintenance) | 1 | describe_problem / accept_quote / schedule | 描述故障、议价、预约 | 生活应急 |
| SC-014 | 办公 (office) | 2-4 | standup / request / meeting / email | 会议、汇报、邮件、请假 | 商务英语入门 |
| SC-015 | 其他 (other / 自定义类型) | 用户定义 | 用户定义 | 用户定义 | 长尾兜底 |

---

## 5. 待 grill 方向(TG-001+)

| ID | 主题 | 优先级 | 备注 |
|---|---|---|---|
| TG-001 | **商业模式**: 订阅?一次性付费?免费增值?B2B2C? | 高 | 影响定价、付费墙设计、转化漏斗 |
| TG-002 | **技术栈选型**: Swift(iOS)/ Flutter(跨平台)/ RN?后端 Python / Node / Go?LLM API(OpenAI / Claude / 自托管?) | 高 | 影响开发周期、招聘、维护成本 |
| TG-003 | **Checkpoint 评分 Prompt 工程**: 渐进式(填空/选择/造句)的具体评分标准 prompt 设计,语音造句的语义相似度阈值 | 高 | 决定 Checkpoint 通过/失败准确性 |
| TG-004 | **发音评分触发与报告**: 场景结束后统一报告的呈现样式(雷达图?分项评分?),用户是否能"分享"报告 | 中 | 影响 L4 用户价值感 |
| TG-005 | **场景库扩展机制**: 用户能否提交"我想加的场景",官方审核流程 | 中 | 长尾覆盖 |
| TG-006 | **NPC 人设模板市场**: 用户能否"分享"自己创建的角色,形成生态 | 中 | 长期增长飞轮 |
| TG-007 | **数据隐私与合规**: 语音数据存储、GDPR/中国数据法合规 | 高 | 影响基础设施选型 |
| TG-008 | **离线/弱网支持**: 用户在地铁里能否用?降级方案? | 中 | 影响可用场景 |
| TG-009 | **多语言扩展**: 同一框架支持学日语/法语?角色 prompt 多语言? | 低 | 长期扩展 |
| TG-010 | **AI 对手难度**: NPC 能不能根据用户水平**主动调整**英语复杂度 | 中 | 与 Q17 已简化方案冲突,但可作 V2 重新评估 |

---

## 6. 未来叠加功能(FF-001+)

| ID | 功能 | 来源 | 优先级 | 说明 |
|---|---|---|---|---|
| FF-001 | **用户自定义场景**: 用户可创建自己的场景,设定背景/NPC/教学目标 | 用户追加 | V2 | 与 SC-015 联动 |
| FF-002 | **场景中的巨型单词(高级词汇扩展库)**: 用户在掌握基础词汇后,可解锁"巨型词包"(学术、商务、技术等),NPC 台词自动嵌入高级词汇 | 用户追加 | V2 | 让用户从"日常英语"过渡到"专业英语" |
| FF-003 | **自定义场景时从复习本选词**: 用户创建自定义场景时,可从自己收藏的词/句型里选,作为该场景的目标词汇 | 用户追加 | V2 | 形成"学 → 用 → 复习 → 创造"的闭环 |
| FF-004 | **角色编辑升级**: 用户自定义角色时,可配置声音(从 TTS 音色库选)、性格、知识背景、bio、greeting、system_prompt | 衍生 | V1.5 | 与现有 CharacterCreatorView 对齐 |
| FF-005 | **多人协作场景**: 多个真实用户(非 AI)同场景对话 | 衍生 | V3 | 社交属性 |
| FF-006 | **AI 评分老师**: 场景中可"召唤"AI 老师点评用户最近表现 | 衍生 | V2 | 增强反馈 |
| FF-007 | **场景主题包**: "商务英语包"(面试+办公+电话),"旅行英语包"(机场+酒店+交通),用户订阅主题包解锁 | 衍生 | V2 | 商业化路径 |
| FF-008 | **成就与勋章系统**: 完成 N 个场景、收藏 N 个词、连续 N 天打卡 → 解锁勋章 | 衍生 | V2 | 留存 |
| FF-009 | **排行榜**: 用户匿名对比"本周场景完成数"、"本周词汇量增长" | 衍生 | V3 | 竞争动力,但避免焦虑 |
| FF-010 | **AI 模拟真实对话纠错**: 用户口语错误时,NPC 用"自然方式"重述正确版本(不直接纠正) | 衍生 | V1.5 | 隐性纠错 |

---

## 7. Q 决策索引(Q1-Q20)

| Q | 主题 | 用户选择 | 决策 ID |
|---|---|---|---|
| Q1 | C 端/B 端定位 | C 端英文学习 App | L4-001 |
| Q2 | NPC 插话触发逻辑 | C(语义+情绪)+ D(状态机) | L1-007, L4-007 |
| Q3 | 记忆维度 | 角色无记忆,记忆归场景 | L1-002, L1-003, L1-004 |
| Q4 | 场景剧本来源 | B 半自动 + Critic | L2-001, L2-003 |
| Q5 | 场景自定义策略 | C 混合分层 | L2-001 |
| Q6 | 场景内交互模式 | D = C 自然模式 + Checkpoint | L4-001 |
| Q7 | Checkpoint 形态 | E 渐进式 | L4-002 |
| Q8 | 语音输入处理 | D 实时转写+可编辑+语音消息;评分场景结束统一 | L4-004, L3-007, L3-008 |
| Q9 | NPC 是否 TTS | C + D(智能调度+用户可关) | L1-006, L4-005, L4-006 |
| Q10 | NPC 插话机制 | C + D | L4-007 |
| Q11 | NPC 消息词汇提示 | E 右侧集合卡+高亮+首次叮 | L4-008 |
| Q12 | 用户卡壳兜底 | D + F(按钮+NPC自然接话) | L4-009, L4-010 |
| Q13 | 复习系统 | C + D(场景化+闪卡) | L3-005, L3-006 |
| Q14 | 场景剧本 schema | C 分层 | L2-003 |
| Q15 | 模板作者 | (跳过,默认官方模板+LLM 实例化) | L2-001 |
| Q16 | NPC 数量 | D 按场景动态 | L2-004, L1-005 |
| Q17 | 用户校准 | 简化:用户报目标→映射CEFR(无自动调整) | L3-002, L3-003, L3-004 |
| Q18 | NPC 角色自定义 | D + 用户可取消/自定义 | L2-006 |
| Q19 | 场景完成度 | D + E | L2-005 |
| Q20 | MVP 范围 | A 5 场景 | L2-007, SC-001 ~ SC-005 |

---

## 8. 论文 CAMEL 复用与偏离

| 论文部分 | 复用 | 偏离 |
|---|---|---|
| Role-playing 框架 | 全部(L1-001) | - |
| Inception Prompting | 全部 | 增加"NPC 自然接话"槽位(L4-010) |
| Task Specifier | 部分(改名为场景模板生成器) | 用户只输入 idea,LLM 在模板上实例化,不直接生成新场景 |
| Critic-In-The-Loop | 全部(L1-008) | Critic 关注教学覆盖率 + 插话时机,不只是回复质量 |
| Embodied Agent | 部分(L5-* 语音技术) | 仅用于 ASR/TTS,Agent 不调工具 |
| Misalignment 数据 | 不复用 | 我们走另一条对齐路径(系统 prompt 强制角色 + Critic 把关) |
| AI Society / Code 数据集 | 不复用 | 我们用场景模板而非 LLM 生成所有内容 |

---

## 9. 风险与缓解

| 风险 | 严重度 | 缓解 |
|---|---|---|
| TTS 成本高 | 高 | ElevenLabs 按字符计费,需要按场景预估成本;NPC 短句优先 |
| ASR 在嘈杂环境不准 | 中 | 提供"可编辑"作为兜底;环境噪音检测 |
| LLM 生成场景模板耗时 | 中 | 模板预生成缓存;用户首次进入 < 2 秒 |
| 用户卡壳判定误判 | 中 | 不主动评分,只用时长启发式,不打断对话 |
| 多 NPC 同时插话混乱 | 低 | 已用 TTS 调度 + 插话提示解决 |
| 用户付费意愿未验证 | 高 | 商业模式(TG-001)待 grill |

---

## 10. 下一步行动

1. **立即**: 决定 MVP 5 场景的 templates 内容撰写负责人(L2-001)
2. **本周**: grill TG-001 商业模式 + TG-002 技术栈
3. **下周**: grill TG-003 Checkpoint 评分 prompt 细节,产出可执行的 prompt 模板
4. **本月**: 开始 SC-001 餐厅场景开发,与现有 ChatView/ChatViewModel 对齐
5. **持续**: 用户自定义角色 + 自定义场景(FF-001/003)进入 V2 路线图

---

## 11. 数据模型（Database Schema）

### 11.1 表关系概览

```
                    ┌──────────┐
                    │  users   │
                    └─────┬────┘
                          │1:1
                    ┌─────▼────────┐
                    │user_profiles │
                    └─────┬────────┘
                          │1:N
       ┌──────────────────┼──────────────────────────┐
       │1:N                │1:N                       │1:N
┌──────▼────────┐   ┌─────▼─────────────┐   ┌──────▼──────────────┐
│scene_instances│   │user_collections   │   │pronunciation_reports│
└──────┬────────┘   └─────┬─────────────┘   └─────────────────────┘
       │1:N                 │1:N
┌──────▼────────┐   ┌──────▼──────────┐
│scene_sessions │   │review_schedules │
└─┬───────┬─────┘   └─────────────────┘
  │1:N    │1:N
  ▼       ▼
┌──────────────┐  ┌─────────────────────┐
│scene_session│  │    messages         │
│_characters  │  │ (归属 scene_session)│
└──────────────┘  └─────────────────────┘
                        │N:1
                   ┌────▼────────┐
                   │ characters  │ (系统预设 + 用户自定义)
                   └─────────────┘

静态资产 (template 层):
┌──────────────────┐    ┌───────────────────────┐
│ scene_templates  │1:N─▶│scene_template_vocab    │
│ (15 个类型骨架)  │1:N─▶│scene_template_patterns │
│                  │1:N─▶│scene_template_beats    │
└──────────────────┘    └───────────────────────┘
```

### 11.2 核心表设计

#### 11.2.1 `users` — 用户基本信息

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| id | UUID | PK | gen_random_uuid() | |
| email | VARCHAR(255) | UNIQUE, NOT NULL | | 登录主键 |
| phone | VARCHAR(20) | UNIQUE, NULL | | 二选一 |
| name | VARCHAR(100) | NOT NULL | | 显示名 |
| avatar_url | VARCHAR(500) | NULL | | 头像 |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | |
| last_login_at | TIMESTAMPTZ | NULL | | 用于留存分析 |

**索引**: `(email)`, `(phone)`, `(last_login_at DESC)`

---

#### 11.2.2 `user_profiles` — 用户学习画像

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| user_id | UUID | PK, FK→users(id) ON DELETE CASCADE | | |
| target_exam | VARCHAR(20) | NOT NULL, CHECK IN | | 'ielts'/'toefl'/'cet4'/'cet6'/'cet8'/'daily'/'other' |
| cefr_level | VARCHAR(2) | NOT NULL, CHECK IN | 'A2' | 'A1'/'A2'/'B1'/'B2'/'C1'/'C2' |
| preferred_language | VARCHAR(10) | NOT NULL | 'en' | UI 语言（系统语言，非学习语言） |
| tts_enabled | BOOLEAN | NOT NULL | TRUE | 用户可关 TTS(L4-005) |
| show_vocab_card | BOOLEAN | NOT NULL | TRUE | 用户可关浮动 UI(L4-008) |
| daily_review_enabled | BOOLEAN | NOT NULL | TRUE | 复习 D 提醒开关 |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | |

---

#### 11.2.3 `characters` — 角色(系统预设 + 用户自定义)

**核心约束**: 角色**无记忆**（L1-002），所有对话历史归属 `scene_sessions`，不存于此表。

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| id | UUID | PK | gen_random_uuid() | |
| owner_user_id | UUID | FK→users(id) ON DELETE CASCADE, NULL | NULL | **NULL=系统预设;非 NULL=用户自定义** |
| name | VARCHAR(100) | NOT NULL | | |
| avatar_url | VARCHAR(500) | NULL | | |
| voice_id | VARCHAR(100) | NULL | | TTS 音色 ID (ElevenLabs voice_id) |
| persona_prompt | TEXT | NOT NULL | | 性格/知识背景描述 |
| system_prompt | TEXT | NOT NULL | | 完整 system_prompt（含 Inception Prompting 的角色约束） |
| bio | TEXT | NULL | | 角色简介（Profile 展示用） |
| greeting | TEXT | NULL | | 角色默认开场白 |
| is_template | BOOLEAN | NOT NULL | FALSE | 是否系统预设 |
| template_role | VARCHAR(50) | NULL | | 系统预设时标识: waiter/chef/interviewer/customer 等 |
| template_scene_type | VARCHAR(50) | NULL, FK→scene_templates(id) | | 系统预设属于哪类场景: restaurant/airport 等 |
| is_active | BOOLEAN | NOT NULL | TRUE | 用户可"软删除"自己的角色 |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | |

**索引**:
- `(owner_user_id)` — 查询用户的角色库
- `(is_template, template_scene_type, template_role)` — 查询某场景的预设角色
- `UNIQUE (owner_user_id, name)` — 用户内角色名不重

**约束补充**:
- CHECK: `(is_template = FALSE AND owner_user_id IS NOT NULL) OR (is_template = TRUE AND owner_user_id IS NULL)` — 二选一

---

#### 11.2.4 `scene_templates` — 场景模板(15 个类型骨架)

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| id | VARCHAR(50) | PK | | 'restaurant'/'airport' 等英文 slug |
| name_zh | VARCHAR(100) | NOT NULL | | '餐厅点餐' |
| name_en | VARCHAR(100) | NOT NULL | | 'Restaurant' |
| description | TEXT | NULL | | 场景简介 |
| setting_template | TEXT | NOT NULL | | 场景设定的模板字符串（带占位符如 {cuisine}） |
| npc_count_min | INT | NOT NULL | 1 | L2-004: 场景动态 |
| npc_count_max | INT | NOT NULL | 2 | |
| required_beats | TEXT[] | NOT NULL | | 必选 beat ID 列表(L2-005) |
| optional_beats | TEXT[] | NOT NULL | '{}' | 可选 beat |
| checkpoint_pass_rate | DECIMAL(3,2) | NOT NULL, CHECK IN [0,1] | 0.6 | L2-005: Checkpoint 通过率阈值 |
| checkpoint_max_retry | INT | NOT NULL | 2 | 失败自动跳过次数 |
| icon_url | VARCHAR(500) | NULL | | 场景卡片图标 |
| is_active | BOOLEAN | NOT NULL | TRUE | |
| version | INT | NOT NULL | 1 | 模板迭代用 |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | |

**索引**: `(is_active)`, `(id, version)`

---

#### 11.2.5 `scene_template_vocabularies` — 模板词汇池

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | | |
| template_id | VARCHAR(50) | FK→scene_templates(id) ON DELETE CASCADE | | |
| word | VARCHAR(100) | NOT NULL | | |
| translation_zh | VARCHAR(200) | NOT NULL | | |
| category | VARCHAR(50) | NULL | | 'cooking'/'request'/'social' 等 |
| difficulty | VARCHAR(2) | NULL, CHECK IN | | 'A1'~'C2' |
| example_sentence | TEXT | NULL | | 标准用法例句 |
| audio_url | VARCHAR(500) | NULL | | 标准发音音频 |
| sort_order | INT | NOT NULL | 0 | UI 排序 |

**约束**: `UNIQUE (template_id, word)`

**索引**: `(template_id, category)`, `(template_id, difficulty)`

---

#### 11.2.6 `scene_template_patterns` — 模板句型池

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | | |
| template_id | VARCHAR(50) | FK→scene_templates(id) ON DELETE CASCADE | | |
| pattern | VARCHAR(500) | NOT NULL | | 'I\\'d like to order ___' 含占位符 |
| use_case | VARCHAR(100) | NOT NULL | | 'ordering'/'requesting_change'/'payment' 等 beat 名 |
| example | TEXT | NOT NULL | | 完整例句 |
| translation_zh | TEXT | NULL | | |
| difficulty | VARCHAR(2) | NULL | | |
| sort_order | INT | NOT NULL | 0 | |

**索引**: `(template_id, use_case)`

---

#### 11.2.7 `scene_template_beats` — 模板节拍

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | | |
| template_id | VARCHAR(50) | FK→scene_templates(id) ON DELETE CASCADE | | |
| beat_id | VARCHAR(50) | NOT NULL | | 模板内唯一: greeting/ordering |
| beat_name | VARCHAR(100) | NOT NULL | | '问候'/'点餐' |
| learning_goal | VARCHAR(200) | NOT NULL | | 学习目标描述 |
| checkpoint_type | VARCHAR(20) | NULL | | 'fill_blank'/'choice'/'sentence_construction'/NULL(此拍不考) |
| difficulty_progression | VARCHAR(10) | NULL | | 'low'/'mid'/'high'(L4-002 渐进式) |
| max_retries | INT | NOT NULL | 2 | |
| sort_order | INT | NOT NULL | 0 | |

**约束**: `UNIQUE (template_id, beat_id)`

**索引**: `(template_id, beat_id)`

---

#### 11.2.8 `scene_instances` — 场景实例

**生命周期**: 用户进入场景时由 LLM 在 `scene_templates` 上实例化生成一次。

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| id | UUID | PK | gen_random_uuid() | |
| template_id | VARCHAR(50) | FK→scene_templates(id) | | |
| user_id | UUID | FK→users(id) ON DELETE CASCADE | | |
| instance_setting | TEXT | NOT NULL | | LLM 生成的实例化场景设定 |
| selected_vocabulary | TEXT[] | NOT NULL | | LLM 从 pool 选出的 ~5 个目标词 |
| selected_patterns | TEXT[] | NOT NULL | | LLM 从 pool 选出的 ~3 个目标句型 |
| characters_config | JSONB | NOT NULL | | `[{source: 'template'/'user_created', char_id, enabled, role_override}]` |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL | NOW() | |

**索引**: `(user_id, template_id, created_at DESC)`

**示例** (`characters_config` JSONB):
```json
[
  {"source": "template", "char_id": "uuid-of-waiter", "enabled": true},
  {"source": "template", "char_id": "uuid-of-chef", "enabled": false},
  {"source": "user_created", "char_id": "uuid-of-my-friend-john", "enabled": true}
]
```

---

#### 11.2.9 `scene_sessions` — 场景会话(记忆归属这里, **核心表**)

**核心约束**: 对话历史 `Mt` 归属于 session 生命周期,角色不持有记忆(L1-003)。永久存储,用户可随时回看。

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| id | UUID | PK | gen_random_uuid() | |
| instance_id | UUID | FK→scene_instances(id) ON DELETE CASCADE | | |
| user_id | UUID | FK→users(id) ON DELETE CASCADE | | |
| status | VARCHAR(20) | NOT NULL, CHECK IN | 'active' | 'active'/'suspended'/'completed'/'free_talk'/'abandoned' |
| current_beat | VARCHAR(50) | NULL | | 状态机当前位置(L2-005) |
| beat_progress | JSONB | NOT NULL | '{}' | 见下方结构 |
| user_vocab_seen | TEXT[] | NOT NULL | '{}' | session 内见过但未收藏的词 |
| user_vocab_mastered | TEXT[] | NOT NULL | '{}' | session 内收藏的词 |
| user_pattern_seen | TEXT[] | NOT NULL | '{}' | |
| user_pattern_mastered | TEXT[] | NOT NULL | '{}' | |
| completed_required_beats | BOOLEAN | NOT NULL | FALSE | L2-005 场景完成判定 |
| checkpoint_pass_rate_actual | DECIMAL(3,2) | NULL | | session 实际通过率 |
| suspended_at | TIMESTAMPTZ | NULL | | 暂停时间(L4-011) |
| suspended_msg_count | INT | NOT NULL | 0 | 暂停时已说消息数 |
| resume_count | INT | NOT NULL | 0 | 恢复次数(分析用) |
| context_summary | TEXT | NULL | | free_talk 模式下的滚动摘要(L4-012) |
| free_talk_started_at | TIMESTAMPTZ | NULL | | 进入自由对话时间(L4-012) |
| total_message_count | INT | NOT NULL | 0 | 总消息数 |
| started_at | TIMESTAMPTZ | NOT NULL | NOW() | |
| last_active_at | TIMESTAMPTZ | NOT NULL | NOW() | |
| ended_at | TIMESTAMPTZ | NULL | | 场景完成/放弃时填 |

**status 状态流转**:
```
            ┌──────────┐
   创建     │          │  完成所有 beats
  ─────────→│  active  │──────────────┐
            │          │              │
            └────┬─────┘              ▼
                 │              ┌──────────┐
     用户点返回  │              │          │ 用户选择:
                 ▼              │completed │ ┌────────────────┐
            ┌──────────┐       │          │ │                │
            │          │       └────┬─────┘ │  [查看历史]    │
            │suspended │            │       │  [再来一次]    │
            │          │            │       │  [接着聊]      │
            └────┬─────┘            │       └───┬─────┬─────┘
                 │                  │           │     │
       ┌────────┤                  │           │     ▼
       │        │                  │           │  ┌──────────┐
       │   ┌────▼─────┐           │           │  │          │
       │   │ 超时>24h  │           │           │  │free_talk │
       │   └────┬─────┘           │           │  │          │
       │        │                 │           │  └────┬─────┘
       │        ▼                 │           │       │
       └───→┌──────────┐         │           │       │ 用户点返回
            │          │←────────┘           └───────┤
            │abandoned │                            ▼
            └──────────┘                       ┌──────────┐
                                               │suspended │
                                               └──────────┘
```

**约束**: active 最多 1 个;suspended 最多 3 个并行;free_talk 最多 1 个;completed/abandoned 无限(历史记录)

**beat_progress JSONB 结构**:
```json
{
  "beats": [
    {
      "beat_id": "greeting",
      "status": "passed",
      "attempted": 1,
      "passed": true,
      "last_attempt_at": "2026-06-23T10:00:00Z"
    },
    {
      "beat_id": "ordering",
      "status": "in_progress",
      "attempted": 1,
      "passed": false,
      "last_attempt_at": "2026-06-23T10:05:00Z"
    }
  ]
}
```

**索引**:
- `(user_id, status, last_active_at DESC)` — 用户 session 列表
- `(instance_id)`
- `(status)` — 用于清理过期 session
- `(status, suspended_at)` — 定时清理 suspended > 24h → abandoned(L4-011)

---

#### 11.2.10 `scene_session_characters` — 会话参与角色(L2-006 多对多)

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| session_id | UUID | FK→scene_sessions(id) ON DELETE CASCADE | | |
| character_id | UUID | FK→characters(id) ON DELETE CASCADE | | |
| is_active | BOOLEAN | NOT NULL | TRUE | 用户是否保留此角色参与本场对话(L2-006 取消功能) |
| role_override | JSONB | NULL | | 用户临时修改的角色配置(覆盖 characters 表的默认) |
| joined_at | TIMESTAMPTZ | NOT NULL | NOW() | |

**主键**: `(session_id, character_id)`

**索引**: `(session_id)`, `(character_id)`

---

#### 11.2.11 `messages` — 对话消息

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| id | UUID | PK | gen_random_uuid() | |
| session_id | UUID | FK→scene_sessions(id) ON DELETE CASCADE | | |
| character_id | UUID | FK→characters(id), NULL | NULL | **NULL = 用户消息;非 NULL = NPC 消息** |
| sender_type | VARCHAR(10) | NOT NULL, CHECK IN | | 'user'/'npc'/'system' |
| content_text | TEXT | NOT NULL | | 主要内容(转写后文本或 NPC 台词) |
| content_audio_url | VARCHAR(500) | NULL | | **用户原始语音消息**(L4-004 可发语音) |
| content_audio_duration_ms | INT | NULL | | 语音时长 |
| tts_audio_url | VARCHAR(500) | NULL | | **NPC TTS 音频**(L4-005) |
| asr_transcription | TEXT | NULL | | 用户语音 ASR 转写(L4-004) |
| asr_user_edited | BOOLEAN | NOT NULL | FALSE | 用户是否编辑了 ASR 结果 |
| asr_confidence | DECIMAL(3,2) | NULL | | ASR 置信度 |
| sequence_no | INT | NOT NULL | | session 内消息序号(从 1 开始) |
| beat_at_time | VARCHAR(50) | NULL | | 消息发出时所在 beat |
| contains_target_vocab | TEXT[] | NULL | | 消息里包含的目标词(用于 L4-008 高亮) |
| is_carded | BOOLEAN | NOT NULL | FALSE | 是否已被触发"叮"过 |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | |

**索引**:
- `(session_id, sequence_no)` — 主查询路径
- `(character_id)`
- `(sender_type, created_at DESC)` — 分析查询
- `(session_id, is_carded)` — L4-008 浮动 UI"首次叮"判定

---

#### 11.2.12 `user_collections` — 用户收藏(L3-001)

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| id | UUID | PK | gen_random_uuid() | |
| user_id | UUID | FK→users(id) ON DELETE CASCADE | | |
| item_type | VARCHAR(10) | NOT NULL, CHECK IN | | 'word'/'sentence' |
| item_content | TEXT | NOT NULL | | 'substitute' 或 'Can I substitute ___ for ___?' |
| item_translation | TEXT | NULL | | |
| item_context | TEXT | NULL | | NPC 原话上下文 |
| item_audio_url | VARCHAR(500) | NULL | | 标准发音 |
| source_message_id | UUID | FK→messages(id), NULL | | 从哪条消息收藏的(可追溯) |
| source_session_id | UUID | FK→scene_sessions(id), NULL | | |
| source_scene_type | VARCHAR(50) | NULL | | 用于 FF-003 复习本选词关联场景 |
| ease_factor | DECIMAL(4,2) | NOT NULL | 2.5 | FSRS 算法 |
| interval_days | INT | NOT NULL | 0 | 下次复习间隔(天) |
| repetitions | INT | NOT NULL | 0 | 已复习次数 |
| last_reviewed_at | TIMESTAMPTZ | NULL | | |
| next_review_at | TIMESTAMPTZ | NOT NULL | NOW() | FSRS 计算(L3-006) |
| collected_at | TIMESTAMPTZ | NOT NULL | NOW() | |

**约束**: `UNIQUE (user_id, item_type, item_content)`

**索引**:
- `(user_id, next_review_at)` — 复习调度主查询(L3-006 闪卡)
- `(user_id, item_type)`
- `(user_id, source_scene_type)` — FF-003 关联

---

#### 11.2.13 `review_schedules` — 复习记录(L3-006)

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| id | BIGSERIAL | PK | | |
| collection_id | UUID | FK→user_collections(id) ON DELETE CASCADE | | |
| scheduled_at | TIMESTAMPTZ | NOT NULL | | 计划复习时间 |
| reviewed_at | TIMESTAMPTZ | NULL | | 实际复习时间 |
| recall_grade | SMALLINT | NULL, CHECK IN 0..3 | NULL | FSRS 4 档:0=忘了,1=困难,2=记得,3=轻松 |
| review_mode | VARCHAR(20) | NOT NULL | | 'flashcard_daily'/'flashcard_session'/'context_scene' |
| session_id | UUID | FK→scene_sessions(id), NULL | | 复习发生的会话(L3-005 场景化复习) |

**索引**: `(collection_id)`, `(scheduled_at)`, `(reviewed_at)`

---

#### 11.2.14 `checkpoint_results` — Checkpoint 结果(L4-002 / L4-003)

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| id | UUID | PK | gen_random_uuid() | |
| session_id | UUID | FK→scene_sessions(id) ON DELETE CASCADE | | |
| beat_id | VARCHAR(50) | NOT NULL | | |
| checkpoint_type | VARCHAR(20) | NOT NULL | | 'fill_blank'/'choice'/'sentence_construction' |
| difficulty_level | VARCHAR(10) | NOT NULL | | 'low'/'mid'/'high'(用户层级) |
| prompt | TEXT | NOT NULL | | 题目 |
| expected_answer | TEXT | NOT NULL | | 标准答案 |
| user_response | TEXT | NULL | | |
| passed | BOOLEAN | NOT NULL | | |
| score | DECIMAL(3,2) | NULL | | 0.0-1.0 |
| attempt_no | INT | NOT NULL | 1 | 1 或 2(L4-003 失败兜底) |
| auto_skipped | BOOLEAN | NOT NULL | FALSE | 是否因失败 2 次自动跳过 |
| graded_at | TIMESTAMPTZ | NOT NULL | NOW() | |
| grader_model | VARCHAR(50) | NULL | | 用于分析的评分模型标识 |

**索引**: `(session_id, beat_id)`, `(passed, graded_at DESC)`

---

#### 11.2.15 `pronunciation_reports` — 发音评分报告(L3-007)

| 字段 | 类型 | 约束 | 默认 | 说明 |
|---|---|---|---|---|
| id | UUID | PK | gen_random_uuid() | |
| user_id | UUID | FK→users(id) ON DELETE CASCADE | | |
| session_id | UUID | FK→scene_sessions(id) ON DELETE CASCADE | | |
| overall_score | DECIMAL(5,2) | NOT NULL, CHECK 0..100 | | 总分 |
| accuracy_score | DECIMAL(5,2) | NULL | | 准确度 |
| fluency_score | DECIMAL(5,2) | NULL | | 流利度 |
| completeness_score | DECIMAL(5,2) | NULL | | 完整度 |
| prosody_score | DECIMAL(5,2) | NULL | | 韵律 |
| word_level_scores | JSONB | NULL | | `[{word, score, phoneme_scores: [{phoneme, score}]}]` |
| message_ids | UUID[] | NOT NULL | | 评分覆盖的消息 ID 列表 |
| audio_url | VARCHAR(500) | NULL | | 完整报告音频 |
| created_at | TIMESTAMPTZ | NOT NULL | NOW() | |

**索引**: `(user_id, created_at DESC)`, `(session_id)`

---

### 11.3 关键索引摘要

| 索引 | 用途 | 性能影响 |
|---|---|---|
| `messages(session_id, sequence_no)` | 加载会话消息流 | 主路径,必须 |
| `scene_sessions(user_id, status, last_active_at DESC)` | 用户 session 列表 | 主路径 |
| `user_collections(user_id, next_review_at)` | 复习调度(FSRS) | 每天定时任务 |
| `scene_session_characters(session_id, character_id)` PK | 角色查找 | 必须 |
| `messages(session_id, is_carded)` | L4-008 浮动 UI "首次叮"判定 | 高频读 |
| `user_collections(user_id, source_scene_type)` | FF-003 复习本→自定义场景 | V2 启用 |
| `pronunciation_reports(user_id, created_at DESC)` | 用户发音报告时间线 | 报告页 |

### 11.4 数据生命周期

| 表 | 创建时机 | 清理策略 |
|---|---|---|
| `users` | 注册 | 永不删(合规保留) |
| `characters` (用户自定义) | 用户创建 | 用户可软删除(`is_active=false`) |
| `scene_instances` | 用户进入场景 | 永不删(可回顾) |
| `scene_sessions` | 用户开始对话 | `status='suspended'` 且 > 24h → 自动 abandoned(L4-011);`status='abandoned'` 且 30 天未活动可归档 |
| `messages` | 消息发出时 | **永不删**(L4-013 用户可随时回看历史对话) |
| `user_collections` | 用户点收藏 | 永不删 |
| `review_schedules` | FSRS 触发 | 已 `reviewed_at` 的可保留 90 天后清理 |
| `checkpoint_results` | Checkpoint 评分 | 永不删 |
| `pronunciation_reports` | 场景结束统一评分 | 永不删 |
| `audio_url` 关联文件 | 消息发出 | 90 天后可清理冷数据(S3 lifecycle) |

### 11.5 数据规模估算（MVP 5 场景 1 万 DAU）

| 表 | 单用户规模 | 1 万 DAU 总量 | 备注 |
|---|---|---|---|
| `messages` | 200-500 条/天 | ~200-500 万/天 | 含 free_talk 模式延长对话;3 个月前可归档冷存储 |
| `scene_sessions` | 5 个 active + 3 个 suspended | 5 万 active + 3 万 suspended | 并行约束: active ≤ 1, suspended ≤ 3 |
| `user_collections` | 50 个词 | 50 万 | |
| `pronunciation_reports` | 1 个/场景 | 5 万/天 | 音频文件存储压力大 |
| `checkpoint_results` | 3 个/场景 | 15 万/天 | |
| `characters` (用户) | 2 个 | 2 万 | 增长慢 |
| `scene_templates` (静态) | 5 个 | 5 | 静态资产 |

### 11.6 与现有后端架构的对齐点

参考文档: `2026-06-19-LinguaScene_场景化对话统一入口_用户自创角色.md`

| 现有 | 本设计 | 对齐 |
|---|---|---|
| `LearningScene.characterId: UUID` | `scene_templates` + `scene_instances` + `scene_sessions` 三层 | 重构 |
| `AICharacter` (无 scene 引用) | `characters` 表加 `template_scene_type` 字段 | 增强 |
| `Conversation.characterId: UUID` | `scene_sessions` + `scene_session_characters` 多对多 | 升级 |
| `Message.characterId: UUID?` | `messages.character_id` + `sender_type` | 保持 |
| `conversation_participants` (已建表) | `scene_session_characters` | 直接复用,无需迁移 |

### 11.7 Schema 与 Q 决策的对应

每个表的设计直接对应一个或多个 Q 决策:

| 表 | 对应决策 |
|---|---|
| `characters` | L1-002(角色无记忆), L1-005, L2-006(用户自定义) |
| `scene_templates` + 词汇/句型/节拍 3 表 | L2-001, L2-003(C 分层), L2-004 |
| `scene_instances` | L2-006(用户角色配置), L2-008(老朋友重逢数据基础) |
| `scene_sessions` | L1-002, L1-003(记忆归属+暂停恢复), L1-004(会话实例), L2-005(完成度), L4-009, L4-011(暂停恢复), L4-012(三种入口), L4-013(存储≠上下文) |
| `scene_session_characters` | L2-006(取消预设/自定义) |
| `messages` | L4-004(语音), L4-005(TTS), L4-008(高亮) |
| `user_collections` + `review_schedules` | L3-001, L3-005, L3-006 |
| `checkpoint_results` | L4-002, L4-003 |
| `pronunciation_reports` | L3-007, L3-008 |
| `user_profiles` | L3-003, L3-004 |

---

**文档维护**: 每次 grill 新一轮后,在本文件追加新 Q 行,新增/更新决策 ID
**Schema 维护**: 表结构变更必须同步更新本文件 + 数据库迁移脚本 + 与现有后端架构评审同步

---

## 13. 引擎架构: AutoGen + CAMEL 混合设计

**日期**: 2026-06-24
**决策 ID**: L1-001 (升级)

### 13.1 选型结论

AutoGen v0.4+ 作为多 agent 编排骨架,CAMEL 思想作为角色定义方法论,自建业务逻辑填充教学血肉。

```
┌──────────────────────────────────────────────────────────────────────┐
│               AutoGen 是骨架,CAMEL 是灵魂,LinguaScene 是血肉       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  AutoGen 提供:                    (机械结构)                         │
│  • 多 agent 组队 (SelectorGroupChat)                                │
│  • 选角钩子 (selector_func / candidate_func)                        │
│  • 共享消息 (broadcast model)                                       │
│  • 终止条件 (TerminationCondition)                                  │
│  • Agent 生命周期 (create / destroy)                                │
│                                                                      │
│  CAMEL 提供:                      (思想指导)                         │
│  • 角色定义范式 (Inception Prompting → system_message)              │
│  • 角色-任务绑定 (Role + Task = Scene)                              │
│  • 质量评估思想 (Critic → 教学覆盖率 + 插话时机)                    │
│  • 对话历史 Mt 的概念 (→ shared context)                            │
│                                                                      │
│  LinguaScene 自建:              (业务血肉)                           │
│  • selector_func 内部逻辑 (beat 状态机 + 插话判定)                  │
│  • Prompt 工厂 (角色 + 场景 + 目标词 + 老朋友词 组装)              │
│  • SceneSession 生命周期管理 (active → suspended → completed)       │
│  • TTS 调度器                                                       │
│  • 收藏 + 复习系统 (FSRS)                                          │
│  • 老朋友重逢注入                                                    │
│  • Checkpoint 评分引擎                                               │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 13.2 CAMEL 概念 → AutoGen 组件映射

| CAMEL 原始概念 | AutoGen 中的落地位置 |
|---|---|
| RolePlaying (核心框架) | `SelectorGroupChat` — 多 agent 组队 + shared context |
| Inception Prompting (角色初始化) | 每个 `AssistantAgent.system_message` — 由 Prompt 工厂组装 |
| TaskSpecifier (任务定义) | L2 内容层的"场景模板实例化器" — template + LLM → instance |
| Critic (质量评估) | `selector_func` 内部(实时) + 场景结束后处理(Checkpoint) |
| Mt (消息历史) | `SelectorGroupChat.shared_context` — 归属 scene_session |
| Role Flipping (角色翻转) | `selector_func` 的插话逻辑 — 从 bug 变 feature |

### 13.3 分层架构图

```
┌──────────────────────────────────────────────────────────────────────┐
│  L4 交互层 (iOS Client)                                             │
│  浮动 UI / 实时转写 / 词汇高亮 / Checkpoint 渐进式                  │
├──────────────────────────────────────────────────────────────────────┤
│  L5 语音技术层                                                       │
│  ASR (Whisper) / TTS (ElevenLabs) / VAD / 发音评分 (Azure)         │
├──────────────────────────────────────────────────────────────────────┤
│  L3 学习层 (自建)                                                    │
│  收藏系统 / FSRS 复习 / 老朋友重逢注入 / CEFR 映射                 │
├──────────────────────────────────────────────────────────────────────┤
│  L2 内容层 (CAMEL 思想 + 自建)                                      │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │  CAMEL TaskSpecifier → 场景模板实例化器                  │       │
│  │  Template + user_collections + user_profiles             │       │
│  │  → LLM 实例化 → scene_instance                          │       │
│  ├──────────────────────────────────────────────────────────┤       │
│  │  CAMEL Inception Prompting → Prompt 工厂                │       │
│  │  character + scene + vocab + old_friend + beat + CEFR    │       │
│  │  → system_message (给 AutoGen agent)                    │       │
│  └──────────────────────────────────────────────────────────┘       │
├──────────────────────────────────────────────────────────────────────┤
│  L1 引擎层 (AutoGen 骨架 + CAMEL 灵魂)                             │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │           AutoGen SelectorGroupChat                       │       │
│  │  ┌────────┐  ┌────────┐  ┌────────┐                     │       │
│  │  │NPC-A   │  │NPC-B   │  │NPC-C   │  ← AutoGen 骨架   │       │
│  │  │Agent   │  │Agent   │  │Agent   │                     │       │
│  │  └───┬────┘  └───┬────┘  └───┬────┘                     │       │
│  │      └───────────┼───────────┘                          │       │
│  │                  ▼                                      │       │
│  │         shared Msg[]  ← CAMEL Mt (场景记忆)             │       │
│  │                                                           │       │
│  │  selector_func  ← CAMEL Critic 思想                     │       │
│  │  ├── Beat 状态机 (当前到哪个节拍)                       │       │
│  │  ├── 插话判定 (语义+情绪+进度)                          │       │
│  │  └── 教学覆盖率检查                                     │       │
│  │                                                           │       │
│  │  candidate_func ← TTS 调度器                            │       │
│  │  ├── 过滤正在说话的 NPC                                 │       │
│  │  └── "💬 想说话" → 移出候选池                          │       │
│  └──────────────────────────────────────────────────────────┘       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │  EngineAdapter (隔离层)                                  │       │
│  │  LinguaScene 业务代码不直接 import AutoGen              │       │
│  │  通过 DialogueEngine Protocol 接口调用                  │       │
│  └──────────────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────────────┘
```

### 13.4 Scene Session 生命周期

```
            ┌──────────┐
   创建     │          │  完成所有 beats
  ─────────→│  active  │──────────────┐
            │          │              │
            └────┬─────┘              ▼
                 │              ┌──────────┐
     用户点返回  │              │          │ 用户选择:
                 ▼              │completed │ ┌────────────────┐
            ┌──────────┐       │          │ │                │
            │          │       └────┬─────┘ │  [查看历史]    │
            │suspended │            │       │  [再来一次]    │
            │          │            │       │  [接着聊]      │
            └────┬─────┘            │       └───┬─────┬─────┘
                 │                  │           │     │
       ┌────────┤                  │           │     ▼
       │        │                  │           │  ┌──────────┐
       │   ┌────▼─────┐           │           │  │          │
       │   │ 超时>24h  │           │           │  │free_talk │
       │   └────┬─────┘           │           │  │          │
       │        │                 │           │  └────┬─────┘
       │        ▼                 │           │       │
       └───→┌──────────┐         │           │       │ 用户点返回
            │          │←────────┘           └───────┤
            │abandoned │                            ▼
            └──────────┘                       ┌──────────┐
                                               │suspended │
                                               └──────────┘

约束: active ≤ 1 | suspended ≤ 3 | free_talk ≤ 1 | completed/abandoned 无限
```

- **active → suspended**: 用户点返回,AutoGen agent 销毁,数据全存 DB
- **suspended → active**: 用户点"继续",重建 agent + 注入当前 beat 内的 Mt
- **completed → free_talk**: 用户点"接着聊",关闭 beat 状态机,NPC 纯角色扮演
- **suspended → abandoned**: 超时 24h 自动清理
- **abandoned → suspended → active**: 用户回来,复活场景

### 13.5 存储 vs Agent 上下文

核心原则: **DB 全存 ≠ Agent 全看**

| 层 | 存什么 | 给谁看 | 成本 |
|---|---|---|---|
| DB (messages 表) | 完整对话,一条不丢 | 用户回看历史 | 存储成本(低) |
| Agent context | system_prompt + 当前 beat 的 Mt | LLM 每次 call | Token 成本(高) |
| free_talk context | system_prompt + 滚动摘要 + 最近 N 轮 | LLM 每次 call | 可控 |

- 用户查看历史对话: 纯 DB 查询,零 LLM 成本,1000 轮也流畅
- Agent 恢复对话: 只注入当前 beat 内的 Mt (通常 < 10 轮)
- free_talk 模式: 每超 30 轮 → 自动压缩最老的消息为摘要,摘要存 `context_summary`

### 13.6 关键风险

| 风险 | 严重度 | 缓解 |
|---|---|---|
| AutoGen v0.4 API breaking change | 高 | EngineAdapter 隔离层,业务代码不直接 import AutoGen |
| selector_func 复杂度膨胀 | 中 | 拆分子模块: BeatManager / InterruptionDetector / CoverageTracker |
| AutoGen agent 创建开销 | 低 | 纯 Python 对象,< 10ms,主要开销在 LLM call |
| 广播模型 NPC 看到不该看的 | 低 | 同一场景 = "桌上对话",广播 = 正确 |
| selector_func 纯 Python 逻辑 vs LLM 语义 | 中 | 混合模式: 常规 → 规则;模糊 → LLM 辅助(接受延迟) |

### 13.7 Prompt 工厂设计

CAMEL Inception Prompting 在 AutoGen `system_message` 中的具体组装方式。

#### 13.7.1 七个模块拼装

```
system_message = ① Identity + ② Scene Context + ③ Mission + ④ Old Friends
               + ⑤ CEFR Constraint + ⑥ Interaction Rules + ⑦ Scene Flow
```

| 模块 | 内容 | 来源 | 动态/固定 |
|---|---|---|---|
| ① Identity | 角色名 + persona + bio + "NOT an AI" | `characters` 表 | 动态(DB) |
| ② Scene Context | 场景设定 + 氛围描写 | `scene_instances.instance_setting` | 动态(DB) |
| ③ Mission | 目标词 + 目标句型 + "自然嵌入,不要列" | `scene_instances.selected_vocab/patterns` | 动态(DB) |
| ④ Old Friends | 用户之前收藏的相关词 + "自然 revisit" | `user_collections` 查询 | 动态(DB),可空 |
| ⑤ CEFR | 难度约束(句长/词频/语法) | `user_profiles.cefr_level` → 6 个固定模板 | 固定(按 level 选) |
| ⑥ Rules | 短句/不教学/不打破角色/留开口空间 | 1 份固定文本 | 固定 |
| ⑦ Scene Flow | 全流程 beat 概览 + "Focus on current phase" | 按 `scene_template` 预写 | 固定(按场景类型选) |

#### 13.7.2 完整示例 — 餐厅 Marco (ordering beat, B1)

```
You are Marco.

You are a waiter at Bella Vita, an upscale Italian restaurant
in downtown. You've been working here for 5 years. You're
passionate about Italian cuisine and love recommending dishes.

Background: 28 years old, from Naples. Moved to the city 3
years ago. Knows the menu inside out.

You are NOT an AI assistant. You are a real person in this
scene. Stay in character at all times.

---

You are currently at: Bella Vita, an upscale Italian restaurant.
It's Friday evening, warm and busy. Soft jazz in the background.

---

Target words to naturally weave into your speech:
substitute, appetizer, medium rare, bill, tip

Target phrases to model:
I'd like to order...; Can I substitute ___ for ___?;
Would you like an appetizer first?

IMPORTANT: Use these words NATURALLY in conversation.
Do NOT list them. Do NOT say "here's a useful word".

---

The user has learned these words/phrases before.
If it feels natural, try to revisit 1-2 of them.
Do NOT force them.

Words: reservation, wine list

---

Use intermediate English. Mix of simple and compound sentences.
Everyday vocabulary + some topic-specific words.

---

1. Keep responses SHORT: 1-2 sentences max per turn.
2. Be natural. No "Great job!", no "That's correct!".
3. End with a question or conversational opening.
4. Don't correct mistakes directly — restate naturally.
5. Never break character.

---

This conversation has phases. Focus on the current phase:
1. Greeting: Welcome the user.
2. Ordering: Help them choose food/drinks.
3. During meal: Check if they enjoy it.
4. Payment: Handle the bill.
5. Farewell: Say goodbye warmly.
Follow the user's lead.
```

Token 估算: ~465 tokens

#### 13.7.3 模块 ④ 空值处理

`old_friend_words` 为空时,模块 ④ 整块不生成(节省 token,避免空指令干扰 LLM)。

#### 13.7.4 Beat 切换不重建 Prompt

模块 ⑦ 使用**全流程概览**而非 per-beat 指引,beat 切换时不需要重建 `system_message`:
- NPC 不知道 beat 切换(它只管说话)
- beat 状态机在 `selector_func` 内部推进
- 只在 `scene_session` 开始时创建一次 prompt

#### 13.7.5 Free Talk 模式 Prompt 变化

`completed → free_talk` 时:
- 删除模块 ③ Mission(不再有教学目标)
- 删除模块 ④ Old Friends(不再有复习目标)
- 简化模块 ⑦ → "Just continue naturally, no goals"
- 新增模块 ⑧ Context Summary(滚动摘要,控制 context 长度)
- 总 token ~300(比教学模式少 ~150)

#### 13.7.6 Token 预算

| 模块 | 预算 | 说明 |
|---|---|---|
| ① Identity | ~150 tok | persona_prompt DB CHECK ≤ 200 字 |
| ② Scene Context | ~50 tok | instance_setting |
| ③ Mission | ~100 tok | 固定 5 个目标词 + 3 个句型 |
| ④ Old Friends | ~50 tok | 最多 5 个词,可空 |
| ⑤ CEFR | ~40 tok | 固定模板 |
| ⑥ Rules | ~100 tok | 固定文本 |
| ⑦ Scene Flow | ~80 tok | 按场景类型预写 |
| **总计** | **~570 tok** | **实际 ~465 tok** |

加上每轮 NPC 回复(~30-80 tok) + Mt(~200-500 tok) = 单次 LLM call ~700-1050 tokens

控制手段:
- `persona_prompt` ≤ 200 字(DB CHECK)
- `selected_vocabulary` 固定 5 个(L2 层)
- `old_friend_words` 最多 5 个(超过随机选)
- 固定模块不动态生成,零 LLM 成本

#### 13.7.7 质量保障

```
验证层 1: 单元测试 (零 LLM 成本)
├── system_message 包含角色名
├── 包含所有 selected_vocabulary
├── old_friend_words 为空时模块 ④ 不出现
├── CEFR 层级正确 (B1 ≠ C1)
├── token 总数 < 600
└── 包含 "NOT an AI" / "Stay in character"

验证层 2: LLM 行为测试 (低成本)
├── 每个场景跑 100 轮模拟对话
├── 检查: NPC 是否使用了目标词?
├── 检查: 回复 ≤ 2 句?
├── 检查: 是否打破角色?
├── 检查: 是否有教学腔?
└── 违规率 < 5% 为通过

验证层 3: A/B 对比 (调优期)
├── 同一场景,两种 prompt 结构
├── 真实用户 / 评测员打分
├── 维度: 自然度 / 教学有效性 / 角色一致性
└── 选出最优结构后锁定
```

常见失败模式 + 加固策略:

| 失败 | 表现 | 加固 |
|---|---|---|
| 列词 | "Here are useful words: ..." | "Do NOT list words. Use in sentences." |
| 教学腔 | "Great job!" | "Never praise. Never evaluate." |
| 太长 | 5+ 句 | "1-2 sentences MAX. This is speech." |
| 打破角色 | "As an AI..." | "NEVER say you are an AI." |
| 忽略目标词 | 10 轮不用 substitute | "Use at least 2 target words per 5 turns." |
| 强行用词 | 每句都塞 | "Use naturally. Don't force." |

---

## 12. Session Log

### 12.1 2026-06-23 第 1 轮 Grill

**范围**: Q1-Q20(20 轮访谈) + 15 场景分类 + 15 张核心表 schema + 36 个决策 ID

**产出统计**:

| 模块 | ID 数量 | 说明 |
|---|---|---|
| 决策(L1-L5) | 36 | 已锁,逐条可追溯 |
| 场景(SC-001~SC-015) | 15 | MVP 5 + V2 5 + V3 5 |
| 待 grill(TG-001~TG-010) | 10 | 商业模式/技术栈/Checkpoint prompt 等 |
| 未来功能(FF-001~FF-010) | 10 | 用户自定义场景/巨型词库/复习本选词等 |
| 数据库表 | 15 | 完整 schema 字段/索引/约束 |

**关键里程碑**:

| Q | 锁定内容 | 意义 |
|---|---|---|
| Q1 | C 端英文学习 App | 从论文场景转向口语学习产品 |
| Q3 | 角色无记忆 + 记忆归场景 | **突破论文隐含假设**,C 端规模化关键 |
| Q6 | 模式 D = 自然模式 + Checkpoint 渐进式 | 拒绝纯模板驱动的"教学感" |
| Q9 | NPC TTS + 智能调度 + 用户可关 | 完整口语训练(speaking + listening) |
| Q10 | NPC 插话 = C 触发 + D 推进 | 把论文视为 bug 的 role flipping 变 feature |
| Q13 | 复习 = C 场景化老朋友重逢 + D 每日闪卡 | 收藏闭环,产品留存关键 |
| Q14 | Schema C 分层(模板 + 实例) | 15 模板覆盖 ~80% 场景 |
| Q17 | 简化:用户报目标 → 映射 CEFR | 去嵌入式校准,降低工程量 |
| Q18 | NPC 角色用户自定义 + 取消预设 | L2-006 |
| Q19 | 完成度 = 必选 beat + Checkpoint 60% + 失败 2 次跳过 | 灵活 + 不卡死 |
| Q20 | MVP 5 场景(餐厅/机场/面试/购物/社交) | 10 周交付起点 |

**与论文 CAMEL 的关键偏离**:

| 论文设计 | 本设计 | 理由 |
|---|---|---|
| 角色隐含有状态 | **角色无记忆** | 规模化 + 用户隐私 + 论文未解决 |
| 1v1 串行 Mt | **会话 = 场景 + 角色组合** | 用户体验 + 多人 NPC |
| 任务 = 自由 idea | **任务 = 场景教学目标** | 学习产品必须有目标 |
| Role flipping = bug | **Role flipping = 插话 feature** | 反转论文认知 |
| 单一 user/assistant | **用户 + N NPC 扇出** | 场景化对话需要多人 |
| 无用户自定义角色 | **角色用户可自定义 + 取消** | C 端必须 |
| Critic 评质量 | **Critic 评插话时机 + 教学覆盖率** | 双重判定 |
| 无发音反馈 | **发音评分(checkpoint 触发 + 场景结束统一)** | Speaking 是核心定位 |

### 12.2 2026-06-24 第 2 轮: 引擎选型 + 场景生命周期

**范围**: AutoGen vs CAMEL 对比 → 混合架构设计 → 场景生命周期管理

**产出统计**:

| 模块 | 变化 | 说明 |
|---|---|---|
| 决策升级 | L1-001, L1-003 | 引擎从纯 CAMEL 升级为 AutoGen+CAMEL 混合;记忆归场景增加暂停/恢复 |
| 新增决策 | L4-011, L4-012, L4-013 | 场景暂停恢复 / 已完成场景三种入口 / 存储≠上下文 |
| Schema 变更 | scene_sessions | status 新增 suspended/free_talk;新增 6 个字段;新增索引 |
| 新增章节 | §13 | 引擎架构完整设计(分层图 + 映射 + 生命周期) |
| 总决策数 | 36 → 39 | 新增 3 条,升级 2 条 |

**关键决策**:

| 决策 | 内容 | 意义 |
|---|---|---|
| 引擎选型 | AutoGen 骨架 + CAMEL 思想 | AutoGen 解决多 NPC 编排(CAMEL 1v1 做不到);CAMEL 解决角色定义方法论 |
| 角色记忆隔离 | 每次 session 重建 agent,不跨场景 | 避免"串戏"+ 控制 token 成本 + 符合 L1-002 |
| 场景暂停/恢复 | 点返回 = suspended,不是 abandon | 不丢用户进度,AutoGen agent 销毁但数据全存 |
| 已完成场景三种入口 | 看历史 / 再来一次 / 接着聊 | free_talk 模式让用户聊嗨了不用走 |
| 存储 ≠ 上下文 | DB 全存,Agent 按需加载 | 用户回看零成本,LLM 成本可控 |

**适配度对比 (AutoGen vs CAMEL)**:

```
                    CAMEL    AutoGen
① 多 NPC 扇出        ✖        ✅     ← AutoGen 杀手级优势
② 角色无记忆          ✅        ⚠️
③ 记忆归场景          ⚠️        ⚠️
④ NPC 插话 feature   ✖        ✅     ← AutoGen selector_func 天然支持
⑤ TTS 调度           ✖        ✅     ← candidate_func 动态过滤
⑥ Critic 双重判定     ✅        ⚠️
⑦ Beat 状态机        ⚠️        ⚠️
⑧ 用户自定义角色      ⚠️        ✅
⑨ 场景模板实例化      ✅        ✖
⑩ 老朋友重逢          ⚠️        ⚠️
总分                 4.5/10   6.5/10
```

### 12.3 下次 Grill 方向(优先级排序)

| 序号 | 方向 | ID | 说明 | 预计 grill 轮次 |
|---|---|---|---|---|
| **1** | **商业模式** | TG-001 | 订阅/一次性/免费增值/B2B2C,影响定价/付费墙/转化漏斗 | 2-3 轮 |
| **2** | **技术栈选型** | TG-002 | iOS Swift vs Flutter vs RN;Python/Node/Go;LLM API | 2 轮 |
| **3** | **Checkpoint 评分 prompt 工程** | TG-003 | 渐进式三档题型(填空/选择/造句)的具体评分标准 prompt | 3-4 轮 |
| **4** | **SC-001 餐厅场景模板撰写** | L2-007 | MVP 第一站,直接进入实施 | (非 grill) |
| 5 | **数据隐私与合规** | TG-007 | 语音数据存储/GDPR/中国数据法 | 2 轮 |
| 6 | **发音评分报告呈现样式** | TG-004 | 雷达图/分项评分/分享功能 | 1-2 轮 |
| 7 | **V2 自定义场景 + 巨型词库** | FF-001/002/003 | 长尾扩展 | 3-4 轮 |

**推荐下次入口**: **TG-001 商业模式** —— 影响整个产品的商业化路径,定价/付费墙/转化漏斗需要在 MVP 之前决定,否则 SC-001 餐厅场景开发完了再去定会推倒一些架构决策。

**推荐 grind 路径**:
```
TG-001 商业模式
  ↓ (决定变现路径)
TG-002 技术栈
  ↓ (决定开发工具)
SC-001 餐厅场景模板撰写(进入实施)
  ↓ (开发到 Checkpoint 时)
TG-003 Checkpoint 评分 prompt 工程
```

### 12.4 待 grill 议题清单(下次会话优先处理)

- [ ] 商业模式:订阅 / 一次性 / 免费增值 / B2B2C
- [x] ~~引擎选型: AutoGen + CAMEL 混合架构~~ (已在 §13 锁定)
- [ ] iOS 原生 vs 跨平台(iOS 优先还是 Android 同步)
- [ ] 后端语言选型 (Python/Node/Go) + LLM API 选型
- [ ] Checkpoint 三档题型(填空/选择/造句)的具体评分 prompt
- [ ] SC-001 餐厅场景 templates 具体内容(词汇池/句型池/节拍)
- [ ] LLM 实例化场景的具体 prompt 工程
- [ ] TTS 音色库选型(ElevenLabs vs OpenAI vs Azure)
- [ ] 语音数据隐私合规策略
- [ ] 发音评分报告 UI 样式
- [ ] selector_func 详细伪代码 (beat 状态机 + 插话逻辑)
- [ ] Prompt 工厂详细设计 (CAMEL Inception → AutoGen system_message)
- [ ] EngineAdapter 接口定义 (Protocol 级)

### 12.5 历史会话

| 日期 | 轮次 | 主要产出 | 文档节 |
|---|---|---|---|
| 2026-06-23 | 1 | Q1-Q20 + 15 表 schema + Session Log 框架 | §1-§12 |
| 2026-06-24 | 2 | AutoGen vs CAMEL 对比 + 混合架构 + 场景生命周期 + L4-011~013 | §13, §12.2 |
| 2026-06-24 | 2+ | Prompt 工厂设计: 7 模块拼装 + Token 预算 + 质量保障 | §13.7 |