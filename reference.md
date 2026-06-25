# API 参考

本文档列出 AutoGen 的所有 API 模块和类。

---

## AutoGen AgentChat

### autogen_agentchat

核心模块

| API | 说明 |
|-----|------|
| `TRACE_LOGGER_NAME` | 追踪日志记录器名称 |
| `EVENT_LOGGER_NAME` | 事件日志记录器名称 |

---

### autogen_agentchat.agents

智能体模块

#### 基础智能体

| API | 说明 |
|-----|------|
| `BaseChatAgent` | 聊天智能体基类 |
| `AssistantAgent` | 助手智能体（常用） |
| `CodeExecutorAgent` | 代码执行智能体 |
| `SocietyOfMindAgent` | 心智社会智能体 |
| `UserProxyAgent` | 用户代理智能体 |

#### 消息过滤

| API | 说明 |
|-----|------|
| `MessageFilterAgent` | 消息过滤智能体 |
| `MessageFilterConfig` | 消息过滤配置 |
| `PerSourceFilter` | 按来源过滤 |

#### 审批请求

| API | 说明 |
|-----|------|
| `ApprovalRequest` | 审批请求 |
| `ApprovalResponse` | 审批响应 |

---

### autogen_agentchat.base

基础模块

| API | 说明 |
|-----|------|
| `ChatAgent` | 聊天智能体接口 |
| `Response` | 响应对象 |
| `Team` | 团队接口 |
| `TaskResult` | 任务结果 |
| `TaskRunner` | 任务运行器 |
| `Handoff` | 任务移交 |

#### 终止条件基础

| API | 说明 |
|-----|------|
| `TerminatedException` | 终止异常 |
| `TerminationCondition` | 终止条件基类 |
| `AndTerminationCondition` | AND 终止条件 |
| `OrTerminationCondition` | OR 终止条件 |

---

### autogen_agentchat.conditions

终止条件模块

| API | 说明 |
|-----|------|
| `MaxMessageTermination` | 最大消息数终止 |
| `TextMentionTermination` | 文本提及终止（如检测到 "APPROVE"） |
| `StopMessageTermination` | 停止消息终止 |
| `TokenUsageTermination` | Token 使用量终止 |
| `HandoffTermination` | 移交终止 |
| `TimeoutTermination` | 超时终止 |
| `ExternalTermination` | 外部终止 |
| `SourceMatchTermination` | 来源匹配终止 |
| `TextMessageTermination` | 文本消息终止 |
| `FunctionCallTermination` | 函数调用终止 |
| `FunctionalTermination` | 函数式终止 |

---

### autogen_agentchat.messages

消息模块

#### 基础消息

| API | 说明 |
|-----|------|
| `BaseMessage` | 消息基类 |
| `ChatMessage` | 聊天消息 |
| `BaseChatMessage` | 聊天消息基类 |
| `BaseTextChatMessage` | 文本聊天消息基类 |
| `TextMessage` | 文本消息（常用） |
| `StopMessage` | 停止消息 |
| `HandoffMessage` | 移交消息 |
| `MultiModalMessage` | 多模态消息 |
| `StructuredMessage` | 结构化消息 |
| `StructuredContentType` | 结构化内容类型 |

#### 事件消息

| API | 说明 |
|-----|------|
| `AgentEvent` | 智能体事件基类 |
| `BaseAgentEvent` | 基础智能体事件 |
| `ToolCallRequestEvent` | 工具调用请求事件 |
| `ToolCallExecutionEvent` | 工具调用执行事件 |
| `ToolCallSummaryMessage` | 工具调用摘要消息 |
| `MemoryQueryEvent` | 记忆查询事件 |
| `UserInputRequestedEvent` | 用户输入请求事件 |
| `ModelClientStreamingChunkEvent` | 模型客户端流式块事件 |
| `ThoughtEvent` | 思考事件 |
| `SelectSpeakerEvent` | 选择发言者事件 |
| `CodeGenerationEvent` | 代码生成事件 |
| `CodeExecutionEvent` | 代码执行事件 |

---

### autogen_agentchat.teams

团队模块

| API | 说明 |
|-----|------|
| `BaseGroupChat` | 群聊基类 |
| `RoundRobinGroupChat` | 轮流发言群聊（常用） |
| `SelectorGroupChat` | 选择器群聊 |
| `Swarm` | 群体智能 |
| `MagenticOneGroupChat` | Magentic-One 群聊 |
| `GraphFlow` | 图工作流 |
| `DiGraphBuilder` | 有向图构建器 |
| `DiGraph` | 有向图 |
| `DiGraphNode` | 有向图节点 |
| `DiGraphEdge` | 有向图边 |

---

### autogen_agentchat.tools

工具模块

| API | 说明 |
|-----|------|
| `AgentTool` | 智能体工具 |
| `TeamTool` | 团队工具 |

---

### autogen_agentchat.ui

UI 模块

| API | 说明 |
|-----|------|
| `Console()` | 控制台输出函数（常用） |
| `UserInputManager` | 用户输入管理器 |

---

### autogen_agentchat.state

状态模块

| API | 说明 |
|-----|------|
| `BaseState` | 状态基类 |
| `AssistantAgentState` | 助手智能体状态 |
| `TeamState` | 团队状态 |
| `RoundRobinManagerState` | 轮流管理器状态 |
| `SelectorManagerState` | 选择器管理器状态 |
| `SwarmManagerState` | 群体智能管理器状态 |
| `MagenticOneOrchestratorState` | Magentic-One 编排器状态 |
| 其他状态类... | |

---

## AutoGen Core

### autogen_core

核心模块

#### 智能体相关

| API | 说明 |
|-----|------|
| `Agent` | 智能体接口 |
| `AgentId` | 智能体 ID |
| `AgentProxy` | 智能体代理 |
| `AgentMetadata` | 智能体元数据 |
| `AgentRuntime` | 智能体运行时 |
| `BaseAgent` | 智能体基类 |
| `RoutedAgent` | 路由智能体（常用） |
| `ClosureAgent` | 闭包智能体 |
| `AgentType` | 智能体类型 |

#### 消息相关

| API | 说明 |
|-----|------|
| `TopicId` | 主题 ID |
| `Subscription` | 订阅 |
| `MessageContext` | 消息上下文 |
| `MessageHandlerContext` | 消息处理器上下文 |
| `MessageSerializer` | 消息序列化器 |
| `TypeSubscription` | 类型订阅 |
| `DefaultSubscription` | 默认订阅 |
| `DefaultTopicId` | 默认主题 ID |

#### 运行时

| API | 说明 |
|-----|------|
| `SingleThreadedAgentRuntime` | 单线程智能体运行时 |

#### 组件

| API | 说明 |
|-----|------|
| `Component` | 组件接口 |
| `ComponentBase` | 组件基类 |
| `ComponentModel` | 组件模型 |

#### 其他

| API | 说明 |
|-----|------|
| `CancellationToken` | 取消令牌 |
| `CacheStore` | 缓存存储 |
| `InMemoryStore` | 内存存储 |
| `Image` | 图像 |
| `FunctionCall` | 函数调用 |

---

### autogen_core.tools

工具模块

| API | 说明 |
|-----|------|
| `Tool` | 工具接口 |
| `StreamTool` | 流式工具 |
| `BaseTool` | 工具基类 |
| `BaseToolWithState` | 带状态的工具基类 |
| `BaseStreamTool` | 流式工具基类 |
| `FunctionTool` | 函数工具（常用） |
| `Workbench` | 工作台 |
| `StaticWorkbench` | 静态工作台 |
| `ToolResult` | 工具结果 |
| `ToolOverride` | 工具覆盖 |

---

### autogen_core.models

模型模块

| API | 说明 |
|-----|------|
| `ChatCompletionClient` | 聊天补全客户端接口 |
| `ModelCapabilities` | 模型能力 |
| `ModelInfo` | 模型信息 |
| `ModelFamily` | 模型家族 |
| `SystemMessage` | 系统消息 |
| `UserMessage` | 用户消息 |
| `AssistantMessage` | 助手消息 |
| `FunctionExecutionResult` | 函数执行结果 |
| `FunctionExecutionResultMessage` | 函数执行结果消息 |
| `RequestUsage` | 请求使用量 |
| `CreateResult` | 创建结果 |

---

### autogen_core.memory

记忆模块

| API | 说明 |
|-----|------|
| `Memory` | 记忆接口 |
| `MemoryContent` | 记忆内容 |
| `MemoryQueryResult` | 记忆查询结果 |
| `UpdateContextResult` | 更新上下文结果 |
| `ListMemory` | 列表记忆 |

---

### autogen_core.code_executor

代码执行器模块

| API | 说明 |
|-----|------|
| `CodeBlock` | 代码块 |
| `CodeExecutor` | 代码执行器 |
| `CodeResult` | 代码执行结果 |

---

## AutoGen Extensions

### 模型扩展

| 模块 | 说明 |
|------|------|
| `autogen_ext.models.openai` | OpenAI 模型客户端 |
| `autogen_ext.models.anthropic` | Anthropic 模型客户端 |
| `autogen_ext.models.azure` | Azure AI 模型客户端 |
| `autogen_ext.models.ollama` | Ollama 模型客户端 |
| `autogen_ext.models.llama_cpp` | LlamaCpp 模型客户端 |
| `autogen_ext.models.cache` | 模型缓存 |
| `autogen_ext.models.replay` | 重放客户端（测试用） |

#### OpenAI 客户端

| API | 说明 |
|-----|------|
| `OpenAIChatCompletionClient` | OpenAI 聊天客户端（常用） |
| `AzureOpenAIChatCompletionClient` | Azure OpenAI 客户端 |
| `BaseOpenAIChatCompletionClient` | 基础 OpenAI 客户端 |

#### Anthropic 客户端

| API | 说明 |
|-----|------|
| `AnthropicChatCompletionClient` | Anthropic 聊天客户端 |
| `AnthropicBedrockChatCompletionClient` | Bedrock Anthropic 客户端 |

---

### 智能体扩展

| 模块 | 说明 |
|------|------|
| `autogen_ext.agents.openai` | OpenAI 智能体 |
| `autogen_ext.agents.azure` | Azure AI 智能体 |
| `autogen_ext.agents.web_surfer` | Web 浏览智能体 |
| `autogen_ext.agents.file_surfer` | 文件浏览智能体 |
| `autogen_ext.agents.video_surfer` | 视频浏览智能体 |
| `autogen_ext.agents.magentic_one` | Magentic-One 智能体 |

---

### 代码执行器扩展

| 模块 | 说明 |
|------|------|
| `autogen_ext.code_executors.local` | 本地代码执行器 |
| `autogen_ext.code_executors.docker` | Docker 代码执行器 |
| `autogen_ext.code_executors.jupyter` | Jupyter 代码执行器 |
| `autogen_ext.code_executors.docker_jupyter` | Docker Jupyter 执行器 |
| `autogen_ext.code_executors.azure` | Azure 代码执行器 |

---

### 工具扩展

| 模块 | 说明 |
|------|------|
| `autogen_ext.tools.mcp` | MCP 工具（Model Context Protocol） |
| `autogen_ext.tools.http` | HTTP 工具 |
| `autogen_ext.tools.langchain` | LangChain 工具适配器 |
| `autogen_ext.tools.azure` | Azure AI 搜索工具 |
| `autogen_ext.tools.code_execution` | 代码执行工具 |
| `autogen_ext.tools.graphrag` | GraphRAG 工具 |

#### MCP 工具

| API | 说明 |
|-----|------|
| `McpWorkbench` | MCP 工作台 |
| `StdioMcpToolAdapter` | 标准输入输出 MCP 适配器 |
| `SseMcpToolAdapter` | SSE MCP 适配器 |
| `StreamableHttpMcpToolAdapter` | 流式 HTTP MCP 适配器 |

---

### 记忆扩展

| 模块 | 说明 |
|------|------|
| `autogen_ext.memory.chromadb` | ChromaDB 记忆 |
| `autogen_ext.memory.redis` | Redis 记忆 |
| `autogen_ext.memory.mem0` | Mem0 记忆 |
| `autogen_ext.memory.canvas` | Canvas 记忆 |

---

### 运行时扩展

| 模块 | 说明 |
|------|------|
| `autogen_ext.runtimes.grpc` | gRPC 运行时 |
| `GrpcWorkerAgentRuntime` | gRPC Worker 运行时（分布式） |
| `GrpcWorkerAgentRuntimeHost` | gRPC 运行时主机 |

---

### 缓存扩展

| 模块 | 说明 |
|------|------|
| `autogen_ext.cache_store.diskcache` | DiskCache 缓存 |
| `autogen_ext.cache_store.redis` | Redis 缓存 |

---

## 常用 API 速查

### 创建智能体
```python
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(model="gpt-4o")
agent = AssistantAgent("assistant", model_client=model_client)
```

### 创建团队
```python
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

team = RoundRobinGroupChat([agent1, agent2], termination_condition=TextMentionTermination("APPROVE"))
```

### 运行任务
```python
result = await team.run(task="你的任务")
# 或流式输出
await Console(team.run_stream(task="你的任务"))
```

---

## 相关链接

- [完整 API 文档](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.html)
- [GitHub 仓库](https://github.com/microsoft/autogen)
- [示例代码](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/examples/index.html)
