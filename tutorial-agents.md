[跳过到主要内容](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html#main-content)

返回顶部 `Ctrl` + `K`

浅色 深色 系统设置

- [GitHub](https://github.com/microsoft/autogen)
- [Discord](https://aka.ms/autogen-discord)
- [Twitter](https://twitter.com/pyautogen)

# 智能体 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#agents "链接到此标题")

AutoGen AgentChat 提供了一组预设的智能体，每个智能体在响应消息的方式上各有不同。
所有智能体共享以下属性和方法：

- [`name`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.name "autogen_agentchat.agents.BaseChatAgent.name")：智能体的唯一名称。

- [`description`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.description "autogen_agentchat.agents.BaseChatAgent.description")：智能体的文本描述。

- [`run`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run")：该方法接收一个字符串任务或消息列表作为输入，运行智能体并返回 [`TaskResult`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult")。**智能体应该是有状态的，此方法期望通过新消息调用，而不是完整的历史记录**。

- [`run_stream`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run_stream "autogen_agentchat.agents.BaseChatAgent.run_stream")：与 [`run()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run") 相同，但返回一个迭代器，包含继承自 [`BaseAgentEvent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseAgentEvent "autogen_agentchat.messages.BaseAgentEvent") 或 [`BaseChatMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage") 的消息，最后一个是 [`TaskResult`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult")。


更多 AgentChat 消息类型请参考 [`autogen_agentchat.messages`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#module-autogen_agentchat.messages "autogen_agentchat.messages")。

## 助手智能体 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#assistant-agent "链接到此标题")

[`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 是一个内置智能体，
使用语言模型并具有使用工具的能力。

警告

[`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 是一个"大杂烩"智能体，
用于原型设计和教育目的——它非常通用。
请确保您阅读了文档和实现以了解设计选择。
一旦您完全理解了设计，您可能想要实现自己的智能体。
参见 [自定义智能体](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/custom-agents.html)。

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import StructuredMessage
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
```

复制到剪贴板

```python
# 定义一个从网络搜索信息的工具。
# 为简单起见，我们在这里使用一个返回静态字符串的模拟函数。
async def web_search(query: str) -> str:
    """在网上查找信息"""
    return "AutoGen 是一个用于构建多智能体应用程序的编程框架。"

# 创建一个使用 OpenAI GPT-4o 模型的智能体。
model_client = OpenAIChatCompletionClient(
    model="gpt-4.1-nano",
    # api_key="YOUR_API_KEY",
)
agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[web_search],
    system_message="使用工具来解决任务。",
)
```

复制到剪贴板

## 获取结果 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#getting-result "链接到此标题")

我们可以使用 [`run()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run") 方法来让智能体执行给定任务。

```python
# 在脚本中运行时使用 asyncio.run(agent.run(...))。
result = await agent.run(task="查找有关 AutoGen 的信息")
print(result.messages)
```

复制到剪贴板

```
[TextMessage(source='user', models_usage=None, metadata={}, content='查找有关 AutoGen 的信息', type='TextMessage'), ToolCallRequestEvent(source='assistant', models_usage=RequestUsage(prompt_tokens=61, completion_tokens=16), metadata={}, content=[FunctionCall(id='call_703i17OLXfztkuioUbkESnea', arguments='{"query":"AutoGen"}', name='web_search')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='assistant', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='AutoGen 是一个用于构建多智能体应用程序的编程框架。', name='web_search', call_id='call_703i17OLXfztkuioUbkESnea', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='assistant', models_usage=None, metadata={}, content='AutoGen 是一个用于构建多智能体应用程序的编程框架。', type='ToolCallSummaryMessage')]
```

复制到剪贴板

对 [`run()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run") 方法的调用
返回一个 [`TaskResult`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult")，
其中 [`messages`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult.messages "autogen_agentchat.base.TaskResult.messages") 属性包含消息列表，
存储了智能体的"思考过程"以及最终响应。

注意

重要的是要注意 [`run()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run")
会更新智能体的内部状态——它会将消息添加到智能体的消息历史中。您也可以在没有任务的情况下调用 [`run()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run")，
让智能体根据当前状态生成响应。

注意

与 v0.2 AgentChat 不同，工具由同一个智能体直接在对 [`run()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run") 的同一次调用中执行。
默认情况下，智能体会将工具调用的结果作为最终响应返回。

## 多模态输入 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#multi-modal-input "链接到此标题")

[`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 可以通过提供 [`MultiModalMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.MultiModalMessage "autogen_agentchat.messages.MultiModalMessage") 来处理多模态输入。

```python
from io import BytesIO

import PIL
import requests
from autogen_agentchat.messages import MultiModalMessage
from autogen_core import Image

# 使用随机图像和文本创建多模态消息。
pil_image = PIL.Image.open(BytesIO(requests.get("https://picsum.photos/300/200").content))
img = Image(pil_image)
multi_modal_message = MultiModalMessage(content=["你能描述这张图片的内容吗？", img], source="user")
img
```

复制到剪贴板

![](<Base64-Image-Removed>)

```python
# 在脚本中运行时使用 asyncio.run(...)。
result = await agent.run(task=multi_modal_message)
print(result.messages[-1].content)  # type: ignore
```

复制到剪贴板

```
这张图片描绘了一幅风景优美的山地景观，天空湛蓝清澈。背景中有几座崎岖的山峰，天空中散布着一些云朵。下方的山谷中有一片水域，可能是湖泊或河流，周围环绕着绿色植被。整体场景传达出一种自然之美和宁静之感。
```

复制到剪贴板

## 流式传输消息 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#streaming-messages "链接到此标题")

我们还可以使用 [`run_stream()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run_stream "autogen_agentchat.agents.BaseChatAgent.run_stream") 方法流式传输智能体生成的每条消息，
并使用 [`Console`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.ui.html#autogen_agentchat.ui.Console "autogen_agentchat.ui.Console") 在消息出现时将其打印到控制台。

```python
async def assistant_run_stream() -> None:
    # 选项 1：从流中读取每条消息（如前面示例所示）。
    # async for message in agent.run_stream(task="查找有关 AutoGen 的信息"):
    #     print(message)

    # 选项 2：使用 Console 按出现顺序打印所有消息。
    await Console(
        agent.run_stream(task="查找有关 AutoGen 的信息"),
        output_stats=True,  # 启用统计信息打印。
    )

# 在脚本中运行时使用 asyncio.run(assistant_run_stream())。
await assistant_run_stream()
```

复制到剪贴板

```
---------- TextMessage (user) ----------
查找有关 AutoGen 的信息
---------- ToolCallRequestEvent (assistant) ----------
[FunctionCall(id='call_HOTRhOzXCBm0zSqZCFbHD7YP', arguments='{"query":"AutoGen"}', name='web_search')]
[提示令牌数: 61, 完成令牌数: 16]
---------- ToolCallExecutionEvent (assistant) ----------
[FunctionExecutionResult(content='AutoGen 是一个用于构建多智能体应用程序的编程框架。', name='web_search', call_id='call_HOTRhOzXCBm0zSqZCFbHD7YP', is_error=False)]
---------- ToolCallSummaryMessage (assistant) ----------
AutoGen 是一个用于构建多智能体应用程序的编程框架。
---------- 摘要 ----------
消息数量: 4
结束原因: None
总提示令牌数: 61
总完成令牌数: 16
耗时: 0.52 秒
```

复制到剪贴板

[`run_stream()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run_stream "autogen_agentchat.agents.BaseChatAgent.run_stream") 方法
返回一个异步生成器，依次产出智能体生成的每条消息，
最后一个是 [`TaskResult`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult")。

从这些消息中，您可以观察到助手智能体使用了 `web_search` 工具来
收集信息，并根据搜索结果进行了响应。

## 使用工具和工作台 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#using-tools-and-workbench "链接到此标题")

大型语言模型（LLMs）通常仅限于生成文本或代码响应。
然而，许多复杂任务受益于使用执行特定操作的外部工具的能力，
例如从 API 或数据库获取数据。

为解决这一限制，现代 LLM 现在可以接受可用工具模式列表
（工具及其参数的描述）并生成工具调用消息。
这种能力被称为**工具调用**或**函数调用**，
正在成为构建智能智能体应用程序的流行模式。
请参阅 [OpenAI](https://platform.openai.com/docs/guides/function-calling)
和 [Anthropic](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) 的文档，了解更多关于 LLM 工具调用的信息。

在 AgentChat 中，[`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 可以使用工具来执行特定操作。
`web_search` 工具就是这样一个工具，允许助手智能体在网上搜索信息。
单个自定义工具可以是 Python 函数或 [`BaseTool`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.tools.html#autogen_core.tools.BaseTool "autogen_core.tools.BaseTool") 的子类。

另一方面，[`Workbench`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.tools.html#autogen_core.tools.Workbench "autogen_core.tools.Workbench") 是共享状态和资源的工具集合。

注意

有关如何直接在模型客户端上使用工具和工作台的说明，请参考核心用户指南中的 [工具](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/components/tools.html)
和 [工作台](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/components/workbench.html) 部分。

默认情况下，当 [`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 执行工具时，
它会在响应的 [`ToolCallSummaryMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallSummaryMessage "autogen_agentchat.messages.ToolCallSummaryMessage") 中以字符串形式返回工具的输出。
如果您的工具没有以自然语言返回格式良好的字符串，您可以
添加一个反思步骤来让模型总结工具的输出，
方法是在 [`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 构造函数中设置 `reflect_on_tool_use=True` 参数。

### 内置工具和工作台 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#built-in-tools-and-workbench "链接到此标题")

AutoGen Extension 提供了一组可与助手智能体一起使用的内置工具。
请前往 [API 文档](https://microsoft.github.io/autogen/stable/reference/index.html) 查看 `autogen_ext.tools` 命名空间下所有可用工具。例如，您可以找到以下工具：

- `graphrag`：用于使用 GraphRAG 索引的工具。

- `http`：用于发出 HTTP 请求的工具。

- [`langchain`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.tools.langchain.html#module-autogen_ext.tools.langchain "autogen_ext.tools.langchain")：用于适配 LangChain 工具的适配器。

- [`mcp`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.tools.mcp.html#module-autogen_ext.tools.mcp "autogen_ext.tools.mcp")：用于使用模型聊天协议（MCP）服务器的工具和工作台。


### 函数工具 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#function-tool "链接到此标题")

[`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 会自动
将 Python 函数转换为 [`FunctionTool`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.tools.html#autogen_core.tools.FunctionTool "autogen_core.tools.FunctionTool")，
智能体可以将其用作工具，并从函数签名和文档字符串自动生成工具模式。

`web_search_func` 工具就是一个函数工具的示例。
模式是自动生成的。

```python
from autogen_core.tools import FunctionTool

# 使用 Python 函数定义一个工具。
async def web_search_func(query: str) -> str:
    """在网上查找信息"""
    return "AutoGen 是一个用于构建多智能体应用程序的编程框架。"

# 如果工具是 Python 函数，这一步会在 AssistantAgent 内部自动执行。
web_search_function_tool = FunctionTool(web_search_func, description="在网上查找信息")
# 在 AssistantAgent 的 on_messages 调用期间，模式会被提供给模型。
web_search_function_tool.schema
```

复制到剪贴板

```
{'name': 'web_search_func',
 'description': '在网上查找信息',
 'parameters': {'type': 'object',
  'properties': {'query': {'description': '查询',
    'title': 'Query',
    'type': 'string'}},
  'required': ['query'],
  'additionalProperties': False},
 'strict': False}
```

复制到剪贴板

### 模型上下文协议（MCP）工作台 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#model-context-protocol-mcp-workbench "链接到此标题")

[`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 还可以使用
通过 [`McpWorkbench()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.tools.mcp.html#autogen_ext.tools.mcp.McpWorkbench "autogen_ext.tools.mcp.McpWorkbench") 从模型上下文协议（MCP）服务器提供的工具。

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams

# 从 mcp-server-fetch 获取 fetch 工具。
fetch_mcp_server = StdioServerParams(command="uvx", args=["mcp-server-fetch"])

# 创建一个 MCP 工作台，提供到 mcp 服务器的会话。
async with McpWorkbench(fetch_mcp_server) as workbench:  # type: ignore
    # 创建一个可以使用 fetch 工具的智能体。
    model_client = OpenAIChatCompletionClient(model="gpt-4.1-nano")
    fetch_agent = AssistantAgent(
        name="fetcher", model_client=model_client, workbench=workbench, reflect_on_tool_use=True
    )

    # 让智能体获取 URL 的内容并进行总结。
    result = await fetch_agent.run(task="总结 https://en.wikipedia.org/wiki/Seattle 的内容")
    assert isinstance(result.messages[-1], TextMessage)
    print(result.messages[-1].content)

    # 关闭模型客户端的连接。
    await model_client.close()
```

复制到剪贴板

```
西雅图是美国华盛顿州的一座主要城市。它成立于 1851 年 11 月 13 日，于 1865 年 1 月 14 日注册为城镇，后于 1869 年 12 月 2 日注册为城市。该市以西雅图酋长的名字命名。面积约为 142 平方英里，截至 2020 年人口普查，人口约为 737,000，预计 2023 年居民人数为 755,078。西雅图被称为翡翠之城、喷气机之城和雨城等昵称，座右铭包括鲜花之城和善意之城。该市实行市长-市政府制度，布鲁斯·哈雷尔担任市长。主要地标包括太空针塔、派克市场、亚马逊球体和西雅图摩天轮。它位于美国西海岸，拥有多元化的城市和都会区，大都会区人口超过 400 万。
```

复制到剪贴板

### 智能体作为工具 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#agent-as-a-tool "链接到此标题")

任何 [`BaseChatAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent "autogen_agentchat.agents.BaseChatAgent") 都可以通过包装在 [`AgentTool`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.tools.html#autogen_agentchat.tools.AgentTool "autogen_agentchat.tools.AgentTool") 中用作工具。
这允许动态的、模型驱动的多智能体工作流，
其中智能体可以调用其他智能体作为工具来解决任务。

### 并行工具调用 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#parallel-tool-calls "链接到此标题")

某些模型支持并行工具调用，这对于需要同时调用多个工具的任务很有用。
默认情况下，如果模型客户端产生多个工具调用，[`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent")
会并行调用这些工具。

当工具具有可能相互干扰的副作用时，或者当智能体行为需要在不同模型之间保持一致时，您可能希望禁用并行工具调用。
这应该在模型客户端级别完成。

重要

使用 [`AgentTool`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.tools.html#autogen_agentchat.tools.AgentTool "autogen_agentchat.tools.AgentTool") 或 [`TeamTool`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.tools.html#autogen_agentchat.tools.TeamTool "autogen_agentchat.tools.TeamTool") 时，
您**必须**禁用并行工具调用以避免并发问题。这些工具和团队无法并发运行，因为智能体和团队维护的内部状态会与并行执行冲突。

对于 [`OpenAIChatCompletionClient`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.OpenAIChatCompletionClient "autogen_ext.models.openai.OpenAIChatCompletionClient") 和 [`AzureOpenAIChatCompletionClient`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.AzureOpenAIChatCompletionClient "autogen_ext.models.openai.AzureOpenAIChatCompletionClient")，
设置 `parallel_tool_calls=False` 来禁用并行工具调用。

```python
model_client_no_parallel_tool_call = OpenAIChatCompletionClient(
    model="gpt-4o",
    parallel_tool_calls=False,  # type: ignore
)
agent_no_parallel_tool_call = AssistantAgent(
    name="assistant",
    model_client=model_client_no_parallel_tool_call,
    tools=[web_search],
    system_message="使用工具来解决任务。",
)
```

复制到剪贴板

### 工具迭代 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#tool-iterations "链接到此标题")

一次模型调用后跟一次工具调用或并行工具调用称为一次工具迭代。
默认情况下，[`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 最多执行一次迭代。

智能体可以配置为执行多次迭代，直到模型停止生成工具调用或达到最大迭代次数。
您可以通过在 [`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 构造函数中设置 `max_tool_iterations` 参数来控制最大迭代次数。

```python
agent_loop = AssistantAgent(
    name="assistant_loop",
    model_client=model_client_no_parallel_tool_call,
    tools=[web_search],
    system_message="使用工具来解决任务。",
    max_tool_iterations=10,  # 在停止循环之前最多进行 10 次工具调用迭代。
)
```

复制到剪贴板

## 结构化输出 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#structured-output "链接到此标题")

结构化输出允许模型返回由应用程序提供的预定义模式的 JSON 文本。
与 JSON 模式不同，模式可以作为 [Pydantic BaseModel](https://docs.pydantic.dev/latest/concepts/models/) 类提供，该类也可用于验证输出。

一旦您在 [`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 构造函数的 `output_content_type` 参数中指定了基础模型类，
智能体将使用 [`StructuredMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.StructuredMessage "autogen_agentchat.messages.StructuredMessage") 进行响应，
其 `content` 的类型是基础模型类的类型。

这样，您可以将智能体的响应直接集成到您的应用程序中，
并将模型的输出用作结构化对象。

注意

设置 `output_content_type` 时，默认要求智能体反思工具使用
并根据工具调用结果返回结构化输出消息。
您可以通过显式设置 `reflect_on_tool_use=False` 来禁用此行为。

结构化输出还有助于在智能体的响应中加入思维链推理。
请参阅下面的示例，了解如何在助手智能体中使用结构化输出。

```python
from typing import Literal

from pydantic import BaseModel

# 作为 Pydantic 基础模型的智能体响应格式。
class AgentResponse(BaseModel):
    thoughts: str
    response: Literal["happy", "sad", "neutral"]

# 创建一个使用 OpenAI GPT-4o 模型的智能体。
model_client = OpenAIChatCompletionClient(model="gpt-4o")
agent = AssistantAgent(
    "assistant",
    model_client=model_client,
    system_message="按照 JSON 格式将输入分类为 happy、sad 或 neutral。",
    # 定义智能体的输出内容类型。
    output_content_type=AgentResponse,
)

result = await Console(agent.run_stream(task="我很开心。"))

# 检查结果中的最后一条消息，验证其类型，并打印思考和响应。
assert isinstance(result.messages[-1], StructuredMessage)
assert isinstance(result.messages[-1].content, AgentResponse)
print("思考: ", result.messages[-1].content.thoughts)
print("响应: ", result.messages[-1].content.response)
await model_client.close()
```

复制到剪贴板

```
---------- user ----------
我很开心。
```

复制到剪贴板

```
---------- assistant ----------
{
  "thoughts": "用户明确表示他们很开心。",
  "response": "happy"
}
思考:  用户明确表示他们很开心。
响应:  happy
```

复制到剪贴板

## 流式传输令牌 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#streaming-tokens "链接到此标题")

您可以通过设置 `model_client_stream=True` 来流式传输模型客户端生成的令牌。
这将导致智能体在 [`run_stream()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run_stream "autogen_agentchat.agents.BaseChatAgent.run_stream") 中产出 [`ModelClientStreamingChunkEvent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.ModelClientStreamingChunkEvent "autogen_agentchat.messages.ModelClientStreamingChunkEvent") 消息。

底层的模型 API 必须支持流式传输令牌才能生效。
请咨询您的模型提供商以确认是否支持此功能。

```python
model_client = OpenAIChatCompletionClient(model="gpt-4o")

streaming_assistant = AssistantAgent(
    name="assistant",
    model_client=model_client,
    system_message="你是一个有帮助的助手。",
    model_client_stream=True,  # 启用流式传输令牌。
)

# 在脚本中使用异步函数和 asyncio.run()。
async for message in streaming_assistant.run_stream(task="说出南美洲的两个城市"):  # type: ignore
    print(message)
```

复制到剪贴板

```
source='user' models_usage=None metadata={} content='说出南美洲的两个城市' type='TextMessage'
source='assistant' models_usage=None metadata={} content='Two' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' cities' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' in' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' South' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' America' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' are' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' Buenos' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' Aires' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' in' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' Argentina' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' and' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' São' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' Paulo' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' in' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' Brazil' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content='.' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=RequestUsage(prompt_tokens=0, completion_tokens=0) metadata={} content='南美洲的两个城市是阿根廷的布宜诺斯艾利斯和巴西的圣保罗。' type='TextMessage'
messages=[TextMessage(source='user', models_usage=None, metadata={}, content='说出南美洲的两个城市', type='TextMessage'), TextMessage(source='assistant', models_usage=RequestUsage(prompt_tokens=0, completion_tokens=0), metadata={}, content='南美洲的两个城市是阿根廷的布宜诺斯艾利斯和巴西的圣保罗。', type='TextMessage')] stop_reason=None
```

复制到剪贴板

您可以在上面的输出中看到流式传输的代码块。
这些代码块由模型客户端生成，并在接收时由智能体产出。
最终响应（所有代码块的拼接）在最后一条代码块之后产出。

## 使用模型上下文 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#using-model-context "链接到此标题")

[`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 有一个 `model_context`
参数，可用于传入 [`ChatCompletionContext`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.model_context.html#autogen_core.model_context.ChatCompletionContext "autogen_core.model_context.ChatCompletionContext")
对象。这允许智能体使用不同的模型上下文，例如
[`BufferedChatCompletionContext`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.model_context.html#autogen_core.model_context.BufferedChatCompletionContext "autogen_core.model_context.BufferedChatCompletionContext") 来
限制发送给模型的上下文。

默认情况下，[`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 使用
[`UnboundedChatCompletionContext`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.model_context.html#autogen_core.model_context.UnboundedChatCompletionContext "autogen_core.model_context.UnboundedChatCompletionContext")，
它将完整的对话历史记录发送给模型。要将上下文限制为最近 `n` 条消息，您可以使用 [`BufferedChatCompletionContext`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.model_context.html#autogen_core.model_context.BufferedChatCompletionContext "autogen_core.model_context.BufferedChatCompletionContext")。
要按令牌计数限制上下文，您可以使用
[`TokenLimitedChatCompletionContext`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.model_context.html#autogen_core.model_context.TokenLimitedChatCompletionContext "autogen_core.model_context.TokenLimitedChatCompletionContext")。

```python
from autogen_core.model_context import BufferedChatCompletionContext

# 创建一个仅使用上下文中最近 5 条消息生成响应的智能体。
agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[web_search],
    system_message="使用工具来解决任务。",
    model_context=BufferedChatCompletionContext(buffer_size=5),  # 仅使用上下文中最近 5 条消息。
)
```

复制到剪贴板

## 其他预设智能体 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#other-preset-agents "链接到此标题")

以下预设智能体可用：

- [`UserProxyAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent")：接受用户输入并将其作为响应返回的智能体。

- [`CodeExecutorAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.CodeExecutorAgent "autogen_agentchat.agents.CodeExecutorAgent")：可以执行代码的智能体。

- [`OpenAIAssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.agents.openai.html#autogen_ext.agents.openai.OpenAIAssistantAgent "autogen_ext.agents.openai.OpenAIAssistantAgent")：由 OpenAI Assistant 支持的智能体，能够使用自定义工具。

- [`MultimodalWebSurfer`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.agents.web_surfer.html#autogen_ext.agents.web_surfer.MultimodalWebSurfer "autogen_ext.agents.web_surfer.MultimodalWebSurfer")：多模态智能体，可以搜索网络并访问网页获取信息。

- [`FileSurfer`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.agents.file_surfer.html#autogen_ext.agents.file_surfer.FileSurfer "autogen_ext.agents.file_surfer.FileSurfer")：可以搜索和浏览本地文件获取信息的智能体。

- `VideoSurfer`：可以观看视频获取信息的智能体。


## 下一步 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html\#next-step "链接到此标题")

在了解了 [`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 的用法之后，我们现在可以继续学习下一节，了解 AgentChat 中的团队功能。

在本页


[在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/tutorial/agents.ipynb)

[显示源代码](https://microsoft.github.io/autogen/stable/_sources/user-guide/agentchat-user-guide/tutorial/agents.ipynb.txt)
