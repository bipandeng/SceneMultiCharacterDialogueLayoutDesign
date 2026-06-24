# LinguaScene 后端架构评审 — 第 1 节：问题清单

> **项目**：lingua-scene-backend
> **日期**：2026-06-19
> **评审范围**：现有 FastAPI + SQLModel + DeepSeek 后端的全部 39 个 Python 文件
> **评审维度**：正确性 / 并发安全、可维护性 / 模块边界、生产就绪度、性能 / 可扩展性
> **重构范围**：全面体检 + 分阶段实施（P0 → P1 → P2）

---

## 1. 用户决策摘要（已确认）

| 议题 | 决策 |
|---|---|
| #3 / #4 并发方案 | **采用 upsert**（依赖 DB 唯一约束，SQLite/PG 都支持） |
| #10 stats 模块 | **补齐为每日目标 / 学习统计 API**（非删除，合并到 Phase 1） |
| #33 SQLite pool_size | **降级为 P3**（单机 SQLite 收益太小，未来切 PG 时再启用） |
| #41 GZip | **保持 P2**（iOS 端实测后再评估收益） |

---

## 2. 实施组织方式

**P0 地基先行**（已确认）：

```
Phase 0 (P0 地基, 3-5 天)
  ├─ Alembic 迁移体系          ← #1
  ├─ Auth 依赖统一到 core/      ← #9（顺便解 P0 根基）
  ├─ SSE session 抽象           ← #2
  ├─ 错误中间件 + 链路追踪      ← #8
  └─ upsert 改造（注册 + 生词）  ← #3, #4

Phase 1 (P1 模块边界, 4-6 天)
  ├─ learned_words_routes 合并到 user/routes
  ├─ Repository 拆分 + 抽象
  ├─ stats 模块补齐（每日目标 / 学习统计）  ← #10
  └─ DictionaryRepository 抽象

Phase 2 (P2 性能与生产化, 3-4 天)
  ├─ Redis 限流 + DeepSeek 超时
  ├─ N+1 消除 + 索引规划
  ├─ Sentry + 结构化日志 + request_id
  ├─ 健康检查深化（live / ready）
  └─ GZip 中间件
```

---

## 3. P0 - 必须立即修复（8 项，~10 天）

### 3.1 正确性 / 并发（5 项）

#### #1 完全缺 Alembic — 必修
- **位置**：`database.py` + `migrations/`
- **现象**：仅有 `migrations/versions/__init__.py`，无 `alembic.ini` / `env.py` / 任何迁移文件
- **后果**：开发期靠 `create_db_and_tables()` 自动建表，**任何 schema 修改都需要手动 SQL 或丢数据**
- **建议**：初始化 Alembic + 生成首个初始迁移覆盖全部现有表（users / refresh_tokens / learned_words / characters / scenes / conversations / conversation_participants / messages / user_stats / daily_goals）
- **验收**：删除 `create_db_and_tables()` 后 `uv run alembic upgrade head` 能完整建出全部表

#### #2 SSE 流式 session 无抽象 — 必修
- **位置**：`app/modules/chat/routes.py:48-78`
- **现象**：`/chat/send` 内手动 `async_session_factory()` 创建独立 session（必要且正确），但**无复用抽象**
- **后果**：未来任何新增流式 endpoint（如实时翻译、AI 语音）都会重新踩这个坑
- **建议**：抽 `app/core/db.py::stream_with_session()` context manager / 装饰器；所有流式 route 共用
- **验收**：chat SSE 改用新抽象后行为不变；新增一个流式 endpoint 测试能直接复用

#### #3 注册并发竞态 → upsert 改造（已决策）
- **位置**：`app/modules/user/service.py:51-62`
- **现象**：两个并发请求同 email 注册，都查到 empty，都尝试 create → 重复 user 或软删除恢复竞态
- **已选方案**：`INSERT ... ON CONFLICT (email) DO UPDATE`（`users.email` 已有 `unique=True` 约束）
- **SQL 草案**：
  ```sql
  INSERT INTO users (id, email, password_hash, display_name, ...)
  VALUES (...)
  ON CONFLICT (email) DO UPDATE
  SET password_hash = EXCLUDED.password_hash,
      display_name = EXCLUDED.display_name,
      del_flag = 0,
      deleted_at = NULL,
      updated_at = NOW()
  RETURNING *;
  -- 应用层判断：active → ConflictError，deleted → 继续登录
  ```
- **验收**：并发 100 请求同一 email 注册，仅产生 1 个 user（或 1 个 active user + 1 个 deleted 旧记录）

#### #4 生词 5 分钟去重 TOCTOU → upsert 改造（已决策）
- **位置**：`app/modules/user/learned_words_routes.py:50-108`
- **现象**：「先查后写」两个并发请求都查到 empty，都 insert
- **已选方案**：`INSERT ... ON CONFLICT (user_id, word) DO UPDATE`（需新建复合唯一索引）
- **迁移**：`add_unique_index_to_learned_words_user_word`（`(user_id, word)`）
- **SQL 草案**：
  ```sql
  INSERT INTO learned_words (id, user_id, word, translation, mastery_level, learned_at)
  VALUES (?, ?, ?, ?, 0, NOW())
  ON CONFLICT (user_id, word) DO UPDATE
  SET mastery_level = MIN(100, learned_words.mastery_level + 5),
      learned_at = CASE
          WHEN learned_words.learned_at > NOW() - INTERVAL '5 minutes'
          THEN learned_words.learned_at
          ELSE NOW()
      END,
      translation = COALESCE(EXCLUDED.translation, learned_words.translation)
  RETURNING *;
  ```
- **代码简化**：路由 80 行 → 20 行（5 分钟去重、mastery 累加、translation 覆盖全部下沉到 SQL）
- **验收**：并发 100 请求同一 (user, word) 仅产生 1 条记录；5 分钟内重复请求不增加 mastery；超过 5 分钟 +5

#### #5 AI 流式中断时 conversation 状态不一致 — 必修
- **位置**：`app/modules/chat/service.py:138-149`
- **现象**：AI 流式中断时仅保存 AI 部分内容 + 标 `[stream interrupted]`，但**用户消息已落库后 conversation.updated_at 未刷新**——前端拉取对话列表时排序异常
- **建议**：整个 `try` 块改为 `try/except/finally`，`finally` 中无条件 `conv.updated_at = now_naive()` + `await session.commit()`
- **验收**：手动模拟 DeepSeek 超时，对话在 `/api/v1/chat/conversations` 列表中位置正确更新

### 3.2 安全（3 项）

#### #6 JWT secret 默认值不安全 — 必修
- **位置**：`config.py:29`
- **现象**：`jwt_secret_key: str = "dev-only-secret-change-in-production"` 在生产环境**启动不会报错**
- **建议**：启动时校验 `if settings.is_production and settings.jwt_secret_key == "dev-only-secret-change-in-production": raise RuntimeError(...)`
- **验收**：生产 env 用默认值启动时，进程立即退出并打印明确错误

#### #7 密码 min_length=8 偏低 — 必修
- **位置**：`schemas.py:14`
- **现象**：OWASP 2024 推荐 ≥12；当前 8 容易被离线爆破
- **建议**：min_length=12；迁移期：旧用户登录不受影响，新注册/改密必须 12+；加 deprecation log 提示旧密码用户
- **验收**：注册 8 位密码返回 422；12 位密码通过

#### #8 无统一异常处理中间件 — 必修
- **位置**：`exceptions.py` + `main.py`
- **现象**：除 `AppError` 子类外，所有未捕获异常会返回 FastAPI 默认 500，**泄露堆栈与 SQL 语句**
- **建议**：
  - 加 `@app.exception_handler(Exception)` 兜底，输出 `{code: "INTERNAL", message: "服务异常", request_id}`
  - Sentry 集成时一并上报（详见 #25）
- **验收**：手动 raise `RuntimeError("DB conn leaked: SELECT * FROM users WHERE password='xxx'")`，客户端只看到 `"服务异常"` + request_id，堆栈进 Sentry

---

## 4. P1 - 模块边界 / 可维护性（13 项，~8 天）

#### #9 `current_user_id` 依赖 3 处重复
- **位置**：`user/routes.py:27-34` + `learned_words_routes.py:22-28` + `chat/routes.py:26-32`
- **建议**：抽到 `app/core/auth.py`，统一签名 + 类型；chat 需要的 user object 加 `current_user` 依赖返回 ORM User
- **验收**：3 处 `async def current_user_id(...)` 删除，仅 `from app.core.auth import current_user_id`

#### #10 stats 模块补齐 → 每日目标 / 学习统计 API（已决策）
- **位置**：`modules/stats/`（当前只有 `models.py`，无 routes / service / repository）
- **新增 endpoints**：
  - `GET /api/v1/me/stats` — 总览（连续天数、累计对话、累计分钟、累计新词、流利度评分）
  - `GET /api/v1/me/goals/today` — 当日目标（默认 15 分钟 + 3 段对话）
  - `POST /api/v1/me/goals/today/complete` — 完成当日目标（手动标记）
  - `GET /api/v1/me/streak` — 当前连续学习天数
- **触发更新点**：
  - `chat/service.py::send_message_stream` 成功 commit 后 → 累加 `conversations + 1`，更新 `last_active_date`、连续天数、`minutes_spent`
  - `learned_words_routes` 新增 → 累加 `words_learned`
- **验收**：连续 3 天每天 1 段对话，第 4 天 `/me/stats` 返回 `current_streak=3`；当日完成 15 分钟目标 `/me/goals/today` 返回 `completed=true`

#### #11 `learned_words_routes.py` 与 `user/routes.py` 合并
- **现象**：同属 user 模块却拆两文件，逻辑分散
- **建议**：合并到 `user/routes.py`（单文件 ~250 行仍可读）
- **验收**：删除 `learned_words_routes.py`，路由仍正常注册

#### #12 Repository 一个文件两个类
- **位置**：`modules/user/repository.py`（`UserRepository` + `RefreshTokenRepository`）
- **建议**：拆 `user/repository/user_repo.py` + `refresh_token_repo.py`；或保持现状（YAGNI）
- **决策**：暂不拆，标注为「如 user 模块继续膨胀则拆」

#### #13 core/ 命名扁平 — 保留现状
- 4 个文件（security / apple_auth / password / datetime_utils）数量不构成问题，**不动**

#### #14 config.py 60 行单类 — 保留现状
- 涵盖 7 个领域但都是简单字段；**嵌套 dataclass 是 over-engineering，不做**

#### #15 缺少类型化 DBSession 别名
- **建议**：在 `app/database.py` 末尾加 `DBSession = Annotated[AsyncSession, Depends(get_session)]`，所有 route 改用
- **验收**：route 文件 import 行减少，`session: DBSession` 类型明确

#### #16 Dictionary 缺少 repository 层
- **位置**：`modules/dictionary/service.py` 直接调 `httpx` + `redis`
- **建议**：抽 `DictionaryRepository` 包 Redis 操作（dict 是缓存层，逻辑上不算 DB，但保持三层对称）
- **决策**：暂不做（service 已经清晰，加一层意义不大）

#### #17 schemas.py 命名 — 保留现状 + 顶部加注释
- 命名合理，仅补一行文件级 docstring 说明「Request/Response DTOs」

#### #18 Repository / Service 事务边界模糊
- **建议**：Repository 负责 `commit()`；Service 只编排，不直接 commit；统一规范
- **当前现状**：部分已遵守（user_repo.create 内部 commit），部分没遵守（service.refresh 内部 commit）
- **验收**：grep `service.py` 内 `commit` 调用 → 0

#### #19 `__init__.py` 空文件 — 不动
- Python 项目惯例

#### #20 AI service 单例化
- **位置**：`ai/service.py` 每次 `AIService()` 都重建对象（虽然 `_sync_client = deepseek_client` 仅引用赋值不重建，但 `_async_client = None` 重复初始化会导致每次都走 `_get_async_client` 分支）
- **建议**：模块级单例 `ai_service = AIService()`；路由 / service 直接 `from app.modules.ai.service import ai_service`
- **验收**：deepseek_client 与 ai_service._async_client 引用稳定；多次 `AIService()` 调用 _async_client 引用同一对象

#### #21 WAL PRAGMA 在 PG 下「假装工作」
- **位置**：`database.py:43-49` SQLite event listener
- **建议**：加注释明确「SQLite-only」+ if 块包裹 `_set_sqlite_pragma`（如果将来切 PG 不需删除）
- **验收**：PG 启动时 event listener 完全不触发

#### #22 `now_naive()` 区域假设未文档化
- **建议**：在 `core/datetime_utils.py` 顶部 docstring 加 "**Single-region assumption (UTC+8)**"；考虑给 `User.timezone` 字段预留（不在本评审实施）
- **验收**：docstring 完整

---

## 5. P1 - 生产就绪（7 项，~5 天）

#### #23 lifespan 启动 dev/prod 分支不彻底
- **位置**：`main.py:19-27`
- **建议**：启动时 `await run_alembic_upgrade_head()` + 健康检查所有外部依赖（DB / Redis / DeepSeek 简单 ping）
- **验收**：DB 不可达时启动失败 + 明确错误

#### #24 `/health` 端点不深入
- **位置**：`main.py:47-54`
- **建议**：
  - `/health/live` — 进程存活（始终 200）
  - `/health/ready` — DB / Redis / DeepSeek 全部可达（任一失败 → 503）
- **验收**：手动停 Redis → `/health/ready` 返回 503 + `redis: unreachable`

#### #25 Sentry 未初始化
- **位置**：`main.py`（`sentry-sdk[fastapi]` 已装但未 `init`）
- **建议**：`if settings.sentry_dsn: sentry_sdk.init(dsn=..., traces_sample_rate=0.1)`
- **验收**：触发未捕获异常，Sentry dashboard 收到事件

#### #26 loguru 未配置结构化输出
- **建议**：加 JSON sink（生产）+ stderr（dev）；contextvars 绑定 request_id
- **验收**：单次请求的所有 log 行带相同 `request_id`

#### #27 缺 request_id 中间件
- **建议**：`RequestIDMiddleware`（读 `X-Request-ID` header，无则生成 uuid4），写入响应头 + contextvars
- **验收**：响应 header 含 `X-Request-ID`；log 输出含 request_id

#### #28 `create_db_and_tables` 幂等但慢
- **位置**：`database.py:64-66`
- **建议**：dev 启动时跳过（生产用 Alembic）
- **决策**：保留（dev 体验优先，启动 +0.5s 可接受）

#### #29 无优雅关闭
- **建议**：lifespan shutdown 阶段等待 inflight SSE 流 30s（用 asyncio.shield + event）
- **验收**：手动 kill -TERM，SSE 客户端收到 SSE `event: shutdown` 或完整收到当前 chunk

---

## 6. P2 - 性能 / 可扩展性（11 项，~5 天）

#### #30 chat 列表 N+1 查询
- **位置**：`chat/routes.py:94-97`
- **建议**：改为单查询 `select(Message.conversation_id, func.count()) group_by(Conversation.id)`
- **验收**：100 条对话的列表响应从 ~100 queries 降到 1 query

#### #31 Redis 不可用时熔断缺失
- **位置**：`dictionary/service.py:45-66`
- **建议**：连续失败 5 次 → 熔断 1 分钟，直接返回 None（避免打爆 Free Dictionary）
- **验收**：Redis 挂掉时 dictionary 接口响应时间从 5s+ 降到 50ms

#### #32 DeepSeek 流式无超时
- **位置**：`ai/service.py:128-134`
- **建议**：`asyncio.timeout(60)` 包裹 + `AsyncOpenAI(timeout=30, max_retries=2)`
- **验收**：模拟 DeepSeek 不响应，60s 后客户端收到 SSE `event: error`

#### #33 ~~SQLite pool_size~~ → **降级 P3**（已决策）
- 跳过；未来切 PG 时启用

#### #34 缓存键无版本前缀
- **位置**：`dictionary/service.py:42`
- **建议**：`dict:v2:{word}:{lang}`
- **验收**：旧键 7 天自然过期失效

#### #35 无限流中间件
- **建议**：slowapi / Redis 滑动窗口限流（每用户 10 req/min for `/chat/send`）
- **验收**：同用户 1 分钟内 11 次 chat send → 第 11 次返回 429

#### #36 LearnedWord 索引不全
- **位置**：`user/models.py:64-67`
- **建议**：(user_id, word) 复合索引（同时解决 #4 upsert 的 unique 约束）
- **验收**：按 word 查全表扫描消除

#### #37 缺慢查询日志
- **建议**：`event.listens_for` 拦截 >200ms 查询，记录到 loguru warning
- **验收**：手动跑一个慢查询，log 输出含 duration + SQL

#### #38 content 端点无 HTTP 缓存
- **建议**：`Cache-Control: public, max-age=3600`（characters/scenes 几乎不变）
- **验收**：第二次 GET /characters 304 / from cache

#### #39 AI prompt 模板无缓存
- **位置**：`ai/prompts.py`
- **建议**：`@functools.lru_cache(maxsize=128)` 缓存 `build_character_system_prompt`
- **验收**：同一 (character, scene) 第二次调用 prompt 构建耗时 → ~0

#### #40 AsyncOpenAI 缺 max_retries / timeout
- **位置**：`ai/service.py:74-80`
- **建议**：构造时 `timeout=30, max_retries=2`
- **验收**：网络抖动时自动重试

#### #41 缺 GZip 中间件（已确认 P2）
- **建议**：`app.add_middleware(GZipMiddleware, minimum_size=1000)`
- **附注**：iOS 实测后若 <10% 收益降级 P3

---

## 7. 统计

| 优先级 | 数量 | 估时 |
|---|---|---|
| **P0** | 8 项 | ~10 天 |
| **P1** | 21 项 | ~8 天（其中 #10 stats 补齐 3 天） |
| **P2** | 11 项 | ~5 天 |
| **P3**（暂缓）| 1 项（#33 pool_size） | — |
| **合计** | 41 项 | ~23 天 |

---

## 8. 下一步

- **第 2 节：目标架构蓝图** — 模块重组、依赖注入规范、Repository / Service 分层契约、错误处理统一格式
- **第 3 节：Phase 0 详细方案** — Alembic 迁移体系、upsert 实施、auth 依赖抽象、SSE 抽象、错误中间件
- **第 4 节：Phase 1 详细方案** — Repository 重构、stats 模块补齐、模块边界统一
- **第 5 节：Phase 2 详细方案** — 性能优化、监控、健康检查
- **第 6 节：验证策略与风险评估**

请确认本节无异议后，进入第 2 节。