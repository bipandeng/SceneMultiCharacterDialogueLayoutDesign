# LinguaScene V1 范围定义

**日期**: 2026-06-25
**作者**: 通过 grill-me + 多轮对话形成
**状态**: 已对齐, 待 V1 实施

---

## V1 核心目标

验证 LinguaScene 的核心产品假设: **多角色场景化对话能提升口语学习效果**

## 核心效果 (必须达到)

1. 用户在一个完整场景里和 ≥2 个 NPC 对话
2. NPC 在对话中自然使用目标词,用户看到并能学习
3. 用户讲话 (打) 后, NPC 智能回应
4. 场景有清晰的开始/中段/结束, 完成后用户感到"完成了"

## V1 范围 (In-Scope)

| 维度 | 范围 |
|---|---|
| **场景数** | 1 个 (餐厅 SC-001) |
| **NPC 数** | 2 个 (Marco waiter + Antonio chef) |
| **Beat 数** | 3 个 (greeting → ordering → payment) |
| **目标词数** | 5 个 (从 vocab_pool 通过 trigger 匹配选) |
| **目标词覆盖率** | ≥80% |
| **交互方式** | 文字输入 (无语音) |
| **插话机制** | 工具调用 + L4-006 用户确认 |
| **场景完成** | 必选 beat 走完即过关 |
| **平台** | CLI demo (V1.5 升级到 Web) |
| **存储** | 本地 / 内存 (无账号系统) |
| **LLM** | MiniMax-M3 (单一模型) |

## V1 不做的事 (Out-of-Scope, 推到 V2/V3)

- ❌ TTS / ASR (语音)
- ❌ 发音评分
- ❌ 用户自定义场景 / 角色
- ❌ 复习系统 / 闪卡 / FSRS
- ❌ Checkpoint 测验
- ❌ 用户卡壳兜底
- ❌ 场景暂停 / 恢复 24h
- ❌ iOS / Android 客户端
- ❌ 用户账号系统
- ❌ 数据库 / Redis / 队列
- ❌ 商业模式 / 付费墙
- ❌ 多语言扩展

## V1 验收标准

1. ✅ 用户能在 10-15 分钟内完成一个餐厅场景
2. ✅ NPC 至少使用 4/5 的目标词 (80% 覆盖)
3. ✅ 用户报告"感觉跟真餐厅服务员/厨师对话" (qualitative)
4. ✅ 至少 1 次多角色对话发生 (Antonio 真的说了话)

## V1 范围决策记录

### 为什么从 50-100 词降到 5 词

- **Scope creep 警告**: 设计文档里有 36 个决策, 全做 V1 不可能
- **核心假设需要先验证**: 多角色对话 + 场景化是否真的有效
- **小步快跑**: 5 词场景能验证核心, 数据驱动后续决策

### 为什么不要 90% 强制覆盖

- 5 词场景下 80% 覆盖 = 4 个词命中, 通过 trigger 匹配选词即可达到
- 不需要运行时强制注入 (那是 V2 的事)
- 强行追求 100% 会破坏对话自然度

### 为什么不要 iOS 客户端

- iOS 开发周期长, 会拖慢核心假设验证
- CLI demo 可以收集核心 UX 反馈
- Web 版先行, iOS 是 V2/V3 阶段

## V1 实施路线图

```
Day 1-2:  触发器选词算法 (trigger 标签库 + 选词逻辑)
Day 3-4:  Web UI (HTML + JS + FastAPI 后端)
Day 5:    数据埋点 (会话开始/结束 + 词覆盖数据)
Day 6-7:  内部测试 + 调优
Day 8:    收集 10-20 个真人反馈
Day 9-10: 数据分析 + 决定 V2 方向
```

## 当前 Demo 状态 (已完成)

- ✅ `config.py` — MiniMax-M3 模型客户端 (含 thinking 关闭)
- ✅ `templates/restaurant.json` — 餐厅场景模板 (12 词, 3 beat, 2 NPC)
- ✅ `prompt_factory.py` — 7 模块 system_message 组装 (含 tool calling 指南)
- ✅ `instance_generator.py` — 场景实例化 (随机选词, 待升级 trigger 匹配)
- ✅ `beat_manager.py` — Beat 状态机 (含 max_turns 兜底)
- ✅ `engine.py` — AutoGen SelectorGroupChat 封装 (流式响应 + tool call 检测)
- ✅ `cli_format.py` — CLI 格式化输出 (气泡 + 流式 + 高亮)
- ✅ `tools.py` — call_colleague 工具 (L4-006 多角色协作)
- ✅ `tag_parser.py` — 备用 tag 解析器 (保留作 fallback)
- ✅ `llm_detector.py` — 备用 LLM 检测器 (保留作 V2 fallback)
- ✅ `main.py` — CLI 入口

## V1 待办 (按优先级)

1. **触发器选词算法** — 把 instance_generator 改成 trigger 匹配
2. **数据埋点** — 记录每场对话的词覆盖率、beat 完成情况
3. **Web UI** — 替代 CLI, 方便真人测试

## 下一个评审节点

V1 上线后, 收集 ≥20 场真实对话数据, 评估:

- 用户真的完成了场景吗? (完成率 >50%?)
- 80% 目标词覆盖达成吗?
- 用户报告"想继续"还是"够了"?
- Antonio 插话是加分还是打扰?

数据驱动 V2 方向决策。

---

**维护**: V1 范围变更需要在此文件标注, 避免范围蔓延。