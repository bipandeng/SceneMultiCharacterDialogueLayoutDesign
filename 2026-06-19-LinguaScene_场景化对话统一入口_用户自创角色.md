---
title: LinguaScene 场景化对话统一入口与用户自创角色
date: 2026-06-19
tags: [LinguaScene, 产品设计, plan-ceo-review, 场景对话, 角色系统]
status: 已批准,待实施
source: plan-ceo-review 输出
---

# 场景化对话 — 统一入口 + 用户自创角色

**状态**: 已批准,待实施
**日期**: 2026-06-19
**关联 spec**: `docs/superpowers/specs/2026-06-18-lingua-scene-backend-design.md`

---

## Context

**用户战略意图(2026-06-19 二次澄清)**:
> "是否将只跟单角色对话的功能删除掉,只进行对话,但是角色可以用户自定义创建删除,在场景当中可以选择 1-3 个多个角色进行场景化问答"

**核心结论**:
1. **"单角色对话"不是独立功能**,只是 ChatView 选 1 个角色 vs 选 N 个角色 — 删 ScenePreviewView 的 `startCTA` 独立按钮,统一为"场景 → 角色选择器 → 对话",**功能零损失**
2. **Characters tab 删除**(场景化后角色入口冗余,且当前是死路径)
3. **角色用户可自创 + 删除**(场景内 1-3 个槽位)
4. **群聊 V2 上线**(`conversation_participants` 表启用)

---

## 当前现状(摸到的证据)

### 数据模型
- `LearningScene.characterId: UUID`(单值推荐角色,`LearningScene.swift:60`)
- `AICharacter` 无 scene 引用(单向:Scene → Character)
- `Conversation.characterId: UUID`(单值,**未升级到 participants 数组**)
- `Message.characterId: UUID?`(群聊时标记是哪位 AI,已就位)
- 后端 `conversations.participant_count`、`conversation_participants` 已建表但 MVP 不启用

### UI 现状
- `ScenePreviewView.startCTA` → `Route.chat(scene, characters: [character])`(**单角色入口**)
- `ScenePreviewView.groupChatCTA` → `GroupChatPickerView` sheet → `Route.chat(scene, characters: [1-3])`(**多角色入口**)
- `CharacterDetailView` 的"开始对话"按钮**只 `dismiss()`**,是死路径(`CharacterBrowserView.swift:287-301`)

### 路由
`Route.chat(scene:characters:)` 已接 `[AICharacter]` 数组(`HomeView.swift:320`),支持任意角色数。

### ChatViewModel
已支持群聊(`ChatViewModel.swift:9`, `isGroupChat` 判断气泡样式),但 `consumeStream` 仍是单角色轮流逻辑,V2 需要扩展。

---

## 目标架构

```
用户操作路径(新):
  HomeView ─→ SceneCard ─→ ScenePreviewView
                                  │
                                  └─[开始对话]──→ CharacterSlotPickerView (新)
                                                      │
                                                      ├─ 槽位 1: [预设角色] / [+ 自创角色]
                                                      ├─ 槽位 2: [预设角色] / [+ 自创角色]
                                                      ├─ 槽位 3: [预设角色] / [+ 自创角色]
                                                      │
                                                      └─[开始对话]──→ ChatView (1-3 角色)

用户操作路径(Profile / 角色管理):
  ProfileView → [我的 AI 角色] → MyCharactersView (新)
      ├─ 列表:我创建的所有角色
      └─ [+ 创建新角色] → CharacterCreatorView (新,4 步表单)
```

### 关键决策

| 决策点 | 选择 | 理由 |
|---|---|---|
| Characters tab | ❌ **删除** | 场景化后冗余,且当前是死路径 |
| ScenePreviewView 的两个 CTA | ❌ 合并为 1 个 → `CharacterSlotPickerView` | 消除"单聊 vs 群聊"歧义 |
| `GroupChatPickerView`(sheet) | ❌ **删除** | 被内联 `CharacterSlotPickerView` 替代 |
| 角色选择器槽位数 | **1-3**(场景默认推荐角色填第 1 槽) | 后端 `max_participants=4` 时升级 |
| 用户自创角色入口 | Profile → "我的 AI 角色"(独立管理) + 场景选择器内"+ 自创角色"快捷入口 | 双路径,主路径在 Profile |
| 角色删除范围 | 仅用户自创角色;系统预设角色**不能删** | 系统角色是运营维护 |
| 群聊 LLM 行为 | V2:多角色轮流发言(每轮 1 个角色);V3:多角色同时发言 | 控制 prompt 复杂度 |
| `Conversation.characterId` | 升级为 `characterIds: [UUID]`(对齐后端) | 数据模型一致性 |

---

## 新增 / 修改文件清单

### iOS 端

| 文件 | 操作 | 说明 |
|---|---|---|
| `Views/ContentView.swift` | 修改 | 删 Characters tab(5 tabs → 4 tabs) |
| `Views/Home/HomeView.swift` | 不变 | 场景入口已就位 |
| `Views/Scenes/ScenePreviewView.swift` | **重写** | 删 `startCTA` + `groupChatCTA`,合并为 1 个 CTA → `CharacterSlotPickerView` |
| `Views/Scenes/GroupChatPickerView.swift` | **删除** | 被内联 picker 替代 |
| `Views/Scenes/CharacterSlotPickerView.swift` | **新建** | 1-3 槽位选择器,内嵌"+ 自创角色"快捷入口 |
| `Views/Characters/` | **整目录删** | `CharacterBrowserView` 改造为 `MyCharactersView` 后移到 Profile |
| `Views/Profile/MyCharactersView.swift` | **新建** | 用户自创角色列表 + 管理 |
| `Views/Profile/CharacterCreatorView.swift` | **新建** | 4 步表单:基础信息 → 出身口音 → 性格 → bio+greeting+system_prompt |
| `Views/Profile/ProfileView.swift` | 修改 | 新增入口 "我的 AI 角色" → `MyCharactersView` |
| `Models/Conversation.swift`(`Models/Message.swift` 同一文件) | 修改 | `Conversation.characterId` → `characterIds: [UUID]` |
| `Models/UserCharacter.swift` | **新建** | `UserCharacter` 模型(用户自创角色) |
| `ViewModels/ChatViewModel.swift` | 修改 | `Conversation.characterIds` 适配 + 多角色 stream 拼接 |
| `ViewModels/MyCharactersViewModel.swift` | **新建** | 加载 / 创建 / 删除用户角色 |
| `Networking/UserCharacterRepository.swift` | **新建** | 用户角色 CRUD 网络层 |
| `Networking/Endpoints.swift` | 修改 | 新增 `/me/characters` 相关端点 |
| `Data/SampleData.swift` | 修改 | `SampleData.allCharacters` 拆分为 `systemCharacters` + 用户自创从后端拉 |

### 后端(FastAPI)

| 文件 | 操作 | 说明 |
|---|---|---|
| `app/modules/user/models.py` | 修改 | 新增 `UserCharacter` SQLModel |
| `app/modules/user/schemas.py` | 修改 | `UserCharacterCreate` / `UserCharacterResponse` |
| `app/modules/user/routes.py` | 修改 | 新增 `/api/v1/me/characters` CRUD |
| `app/modules/content/models.py` | 修改 | `characters` 表新增 `is_user_creatable: bool` 字段(决定哪些预设角色可被用户用作模板) |
| `app/modules/chat/models.py` | 修改 | `conversations.character_id` 单值 → `character_ids: TEXT[]`;启用 `conversation_participants` |
| `app/modules/chat/service.py` | 修改 | 多角色 prompt 拼接逻辑 |
| `app/core/security.py` | 修改 | RLS:用户只能 CRUD 自己的角色 |
| `migrations/versions/xxx_add_user_characters.py` | **新建** | Alembic 迁移 |
| `data/characters.json` | 修改 | 新增 `is_user_creatable` 字段 |

---

## 关键 UI 设计要点

### CharacterSlotPickerView(场景内角色选择器)

```
┌────────────────────────────────────┐
│ 选择 AI 角色(1-3 个)              │
├────────────────────────────────────┤
│ 槽位 1 (推荐角色:Emma)            │
│   [Emma - 西雅图咖啡师]        ×  │
├────────────────────────────────────┤
│ + 添加角色                         │
│  ├─ 系统角色:James / Sofia / ...  │
│  └─ 我的角色:[Marcus 老友]       │
│  └─ [+ 创建新角色]               │
├────────────────────────────────────┤
│         [开始对话]                 │ ← 仅当 ≥1 槽位有角色时可点
└────────────────────────────────────┘
```

行为:
- 场景默认推荐角色(从 `scene.recommendedCharacterIds.first`)自动填入第 1 槽位
- 用户可删除槽位 / 添加槽位(最多 3)
- "+ 创建新角色"内联 sheet 弹出 `CharacterCreatorView`,创建成功后自动填入下一个空槽位

### CharacterCreatorView(4 步表单)

```
Step 1 - 基础:
  - 名字 (TextField)
  - emoji (EmojiPicker)
  - 头像色调 (3 选 1: terracotta / olive / stone)

Step 2 - 出身:
  - 出身地 (TextField)
  - 口音 (Picker: 美式 / 英式 / 澳式 / 其他)

Step 3 - 性格:
  - traits chips(从 12 个预设选 2-4 个:patient / warm / strict / humorous ...)

Step 4 - 详细:
  - bio (TextArea,默认折叠)
  - greeting (TextArea,必填)
  - system_prompt 高级编辑(默认折叠,只展示"使用默认模板")
```

提交: `POST /api/v1/me/characters` → 返回 `UserCharacter.id` → 立即可用

### MyCharactersView(Profile 下的角色管理)

```
┌────────────────────────────────────┐
│ 我的 AI 角色                       │
├────────────────────────────────────┤
│ [+] 创建新角色                     │
├────────────────────────────────────┤
│ ┌──────────────────────────────┐  │
│ │ 😊 Marcus 老友              │  │
│ │ 北京 / 美式英语             │  │
│ │ 性格:warm, humorous         │  │
│ │ [编辑]  [删除]              │  │
│ └──────────────────────────────┘  │
│ ┌──────────────────────────────┐  │
│ │ 🎓 Ms. Liu                  │  │
│ │ ...                          │  │
│ └──────────────────────────────┘  │
└────────────────────────────────────┘
```

---

## 后端数据模型

### 新增 `user_characters` 表

```sql
CREATE TABLE user_characters (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id        UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    avatar_emoji    VARCHAR(10),
    accent_color    VARCHAR(20) DEFAULT 'terracotta',
    origin          VARCHAR(100),
    accent          VARCHAR(100),
    traits          TEXT[] NOT NULL DEFAULT '{}',
    bio             TEXT,
    greeting        TEXT NOT NULL,
    system_prompt   TEXT,                       -- 用户自填,后端审核
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_chars_owner ON user_characters(owner_id);

-- RLS
ALTER TABLE user_characters ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_chars_isolation ON user_characters
USING (owner_id = current_setting('app.current_user_id')::UUID);
```

### `characters` 表新增字段

```sql
ALTER TABLE characters ADD COLUMN is_user_creatable BOOLEAN DEFAULT TRUE;
-- TRUE = 用户可以用作"创建新角色的模板",FALSE = 仅系统使用(如限定场景的"老板"等)
```

### `conversations` 表升级

```sql
-- 升级:character_id 单值 → character_ids 数组
ALTER TABLE conversations ADD COLUMN character_ids TEXT[] DEFAULT '{}';
UPDATE conversations SET character_ids = ARRAY[character_id::TEXT];
ALTER TABLE conversations ALTER COLUMN character_ids SET NOT NULL;

-- 启用 conversation_participants
-- (表已在 MVP 创建,现在业务层启用)
```

### API 新增

```
POST   /api/v1/me/characters                # 创建
GET    /api/v1/me/characters                # 列出我的
GET    /api/v1/me/characters/{id}           # 详情
PATCH  /api/v1/me/characters/{id}           # 编辑
DELETE /api/v1/me/characters/{id}           # 物理删除(仅 owner)
```

### LLM Prompt 升级(V2 群聊)

```python
SYSTEM_PROMPT_TEMPLATE = """
你是一个多角色对话协调器。当前场景:{scene_title}
场景目标:{scene_objectives}

## 参与角色
{character_blocks}

## 当前发言角色
{current_character}

## 对话规则
1. 仅以"当前发言角色"身份回复
2. 其他角色可简短插话(最多 1 句),但要标注 [{name}]: 前缀
3. 保持场景目标推进
4. 单次回复 1-3 句话
"""
```

实现:每轮 LLM 调用只让 1 个角色"主发言",其他角色用"interjection"提示词简短回应。V3 升级为多角色并行生成。

---

## 验证步骤(端到端)

### iOS 端
1. `xcodegen generate` 重生成工程
2. `xcodebuild -project LinguaScene.xcodeproj -scheme LinguaScene -destination 'platform=iOS Simulator,name=iPhone 15' build` 必须无 warning 通过
3. `xcrun simctl boot "iPhone 15"` → `install` → `launch`
4. 走查路径:
   - HomeView → 点场景卡 → ScenePreviewView
   - ScenePreviewView 点"开始对话" → CharacterSlotPickerView 显示(场景默认推荐 Emma 在槽位 1)
   - 加第 2 个槽位(选 James) → 开始对话 → ChatView 显示两人气泡
   - 退出回 Profile → 点"我的 AI 角色" → 创建新角色 → 填 4 步表单 → 创建成功
   - 回 CharacterSlotPickerView → "+ 创建新角色"快捷入口测通
   - 删除一个自创角色 → 列表消失
5. 检查:场景内不再有"群聊模式"按钮(已合并);Characters tab 消失(5→4 tabs)

### 后端
1. Alembic 迁移成功
2. `pytest tests/test_user_characters.py` 通过
3. `curl POST /api/v1/me/characters` 创建成功
4. `curl GET /api/v1/me/characters` 返回列表
5. `curl DELETE /api/v1/me/characters/{id}` 返回 204
6. RLS 测试:用户 A 不能删用户 B 的角色(返回 403)
7. 流式对话:`POST /api/v1/chat/send` with `character_ids: [id1, id2]` → 流式响应包含两个角色的消息

---

## 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| 自创角色 system_prompt 质量不可控 | LLM 输出混乱 | 模板填空为主,高级用户才开放编辑 |
| 内容审核缺失 | 用户输入违规 persona | MVP:基础违禁词列表 + 长度限制(≤2000字) |
| 删除用户角色时对话数据孤儿化 | 对话显示已删除角色 | conversation_participants 软引用,UI 显示"[已删除]" |
| 群聊 LLM 协调困难 | 多角色相互打断 | V2 严格单角色轮流;V3 引入并行 |
| iOS `Conversation.characterId` → `characterIds` 升级 | 旧对话数据兼容 | 读取时降级:`characterIds.first ?? characterId` |
| `GroupChatPickerView` 整文件删除 | 编译报错 | 同步删 `HomeView.swift:357-361` 的 `RouteScenePreviewCallbacks` 死代码 |
| 现有 `AutoTestRunner.swift:199` UI 测试依赖 group chat | 测试失败 | 同步更新测试,适配 CharacterSlotPickerView |
| `Route.chat(scene:, characters:)` 已接数组,签名无需变 | — | 0 改动,反而清爽 |

---

## 实施顺序(建议 5 个 PR)

| PR | 内容 | 估算(human / CC+gstack) |
|---|---|---|
| PR1 | 后端:`user_characters` 表 + CRUD API + Alembic + 测试 | 2 天 / 30 min |
| PR2 | iOS:Profile → MyCharactersView → CharacterCreatorView + 网络层 | 1.5 天 / 25 min |
| PR3 | iOS:删 Characters tab + 删 GroupChatPickerView + 重写 ScenePreviewView + 新建 CharacterSlotPickerView | 1.5 天 / 25 min |
| PR4 | 后端:启用 conversation_participants + 多角色 prompt 拼接 + 流式响应适配 | 1.5 天 / 25 min |
| PR5 | iOS:ChatViewModel 适配 character_ids 数组 + 流式多角色展示 + 端到端联调 | 1 天 / 20 min |
| **合计** | | **7.5 天 / 约 2 小时** |

---

## 不在本期范围

- V3 多角色同时发言
- 角色关系和记忆系统
- 社交分享(把自创角色分享给其他用户)
- 角色市场(浏览其他用户创建的角色)
- 语音输入/输出
- 订阅/付费

---

## 相关笔记

- [[LinguaScene_后端架构评审_第1节_问题清单_2026-06-19]] — 后端架构评审记录
- [[2026-06-19-假数据-后端填充-接口接入清单]] — 当前后端接入清单
- `docs/superpowers/specs/2026-06-18-lingua-scene-backend-design.md` — 后端设计 spec(V1.0 MVP)