<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html -->

# 代理#

AutoGen AgentChat 提供了一组预设代理，每个代理在代理如何响应消息方面都有所变化。所有代理共享以下属性和方法：

  * [`name`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.name "autogen_agentchat.agents.BaseChatAgent.name")：代理的唯一名称。

  * [`description`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.description "autogen_agentchat.agents.BaseChatAgent.description")：代理的文本描述。

  * [`run`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run")：该方法使代理根据作为字符串或消息列表的任务运行，并返回 [`TaskResult`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult")。**期望代理是有状态的，并且此方法应使用新消息调用，而不是完整历史**。

  * [`run_stream`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run_stream "autogen_agentchat.agents.BaseChatAgent.run_stream")：与 [`run()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run") 相同，但返回一个迭代器，其中包含继承自 [`BaseAgentEvent`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseAgentEvent "autogen_agentchat.messages.BaseAgentEvent") 或 [`BaseChatMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage") 的消息，最后是一个 [`TaskResult`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult")。

有关 AgentChat 消息类型的更多信息，请参见 [`autogen_agentchat.messages`](../../../reference/python/autogen_agentchat.messages.html#module-autogen_agentchat.messages "autogen_agentchat.messages")。

## 助手代理#

[`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 是一个内置代理，它使用语言模型并具有使用工具的能力。

警告

[`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 是一个用于原型设计和教育目的的"大杂烩"代理——它非常通用。确保您阅读文档和实现以了解设计选择。一旦您完全理解了设计，您可能想要实现自己的代理。请参阅 [自定义代理](../custom-agents.html)。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.messages import StructuredMessage
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    
    
    # 定义一个在 Web 上搜索信息的工具。
    # 为简单起见，我们将在此处使用返回静态字符串的模拟函数。
    async def web_search(query: str) -> str:
        """在 Web 上查找信息"""
        return "AutoGen 是一个用于构建多代理应用程序的编程框架。"
    
    
    # 创建一个使用 OpenAI GPT-4o 模型的代理。
    model_client = OpenAIChatCompletionClient(
        model="gpt-4.1-nano",
        # api_key="YOUR_API_KEY",
    )
    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        tools=[web_search],
        system_message="使用工具解决任务。",
    )
    

## 获取结果#

我们可以使用 [`run()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run") 方法让代理执行给定任务。
    
    
    # 在脚本中运行时使用 asyncio.run(agent.run(...))。
    result = await agent.run(task="查找有关 AutoGen 的信息")
    print(result.messages)
    
    
    
    [TextMessage(source='user', models_usage=None, metadata={}, content='Find information on AutoGen', type='TextMessage'), ToolCallRequestEvent(source='assistant', models_usage=RequestUsage(prompt_tokens=61, completion_tokens=16), metadata={}, content=[FunctionCall(id='call_703i17OLXfztkuioUbkESnea', arguments='{"query":"AutoGen"}', name='web_search')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='assistant', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='AutoGen is a programming framework for building multi-agent applications.', name='web_search', call_id='call_703i17OLXfztkuioUbkESnea', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='assistant', models_usage=None, metadata={}, content='AutoGen is a programming framework for building multi-agent applications.', type='ToolCallSummaryMessage')]
    

对 [`run()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run") 方法的调用返回一个 [`TaskResult`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult")，其中 [`messages`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult.messages "autogen_agentchat.base.TaskResult.messages") 属性中包含消息列表，该列表存储代理的"思维过程"以及最终响应。

注意

重要的是要注意 [`run()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run") 将更新代理的内部状态——它会将消息添加到代理的消息历史中。您也可以在没有任务的情况下调用 [`run()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run")，以使代理根据其当前状态生成响应。

注意

与 v0.2 AgentChat 不同，工具由同一个代理直接在对 [`run()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run") 的同一次调用中执行。默认情况下，代理将把工具调用的结果作为最终响应返回。

## 多模态输入#

[`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 可以通过将输入作为 [`MultiModalMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.MultiModalMessage "autogen_agentchat.messages.MultiModalMessage") 来处理多模态输入。
    
    
    from io import BytesIO
    
    import PIL
    import requests
    from autogen_agentchat.messages import MultiModalMessage
    from autogen_core import Image
    
    # 创建一个带有随机图像和文本的多模态消息。
    pil_image = PIL.Image.open(BytesIO(requests.get("https://picsum.photos/300/200").content))
    img = Image(pil_image)
    multi_modal_message = MultiModalMessage(content=["你能描述这张图片的内容吗？", img], source="user")
    img
    
    
    result = await agent.run(task=multi_modal_message)
    print(result.messages[-1].content)  # type: ignore
    
    
    
    The image depicts a scenic mountain landscape under a clear blue sky. There are several rugged mountain peaks in the background, with some clouds scattered across the sky. In the valley below, there is a body of water, possibly a lake or river, surrounded by greenery. The overall scene conveys a sense of natural beauty and tranquility.
    

## 流式消息#

我们还可以使用 [`run_stream()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run_stream "autogen_agentchat.agents.BaseChatAgent.run_stream") 方法流式传输代理生成的每条消息，并使用 [`Console`](../../../reference/python/autogen_agentchat.ui.html#autogen_agentchat.ui.Console "autogen_agentchat.ui.Console") 打印消息到控制台。
    
    
    async def assistant_run_stream() -> None:
        # 选项 1：从流中读取每条消息（如前面的示例所示）。
        # async for message in agent.run_stream(task="Find information on AutoGen"):
        #     print(message)
    
        # 选项 2：使用 Console 打印所有消息。
        await Console(
            agent.run_stream(task="Find information on AutoGen"),
            output_stats=True,  # 启用统计信息打印。
        )
    
    
    # 在脚本中运行时使用 asyncio.run(assistant_run_stream())。
    await assistant_run_stream()
    
    
    
    ---------- TextMessage (user) ----------
    Find information on AutoGen
    ---------- ToolCallRequestEvent (assistant) ----------
    [FunctionCall(id='call_HOTRhOzXCBm0zSqZCFbHD7YP', arguments='{"query":"AutoGen"}', name='web_search')]
    [Prompt tokens: 61, Completion tokens: 16]
    ---------- ToolCallExecutionEvent (assistant) ----------
    [FunctionExecutionResult(content='AutoGen is a programming framework for building multi-agent applications.', name='web_search', call_id='call_HOTRhOzXCBm0zSqZCFbHD7YP', is_error=False)]
    ---------- ToolCallSummaryMessage (assistant) ----------
    AutoGen is a programming framework for building multi-agent applications.
    ---------- Summary ----------
    Number of messages: 4
    Finish reason: None
    Total prompt tokens: 61
    Total completion tokens: 16
    Duration: 0.52 seconds
    

[`run_stream()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run_stream "autogen_agentchat.agents.BaseChatAgent.run_stream") 方法返回一个异步生成器，该生成器依次生成代理生成的每条消息，最后是一个 [`TaskResult`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult")。

从这些消息中，您可以观察到助手代理使用了 `web_search` 工具来获取信息并根据搜索结果进行响应。

## 使用工具和工作台#

大型语言模型 (LLM) 通常仅限于生成文本或代码响应。然而，许多复杂任务受益于使用能够执行特定操作的外部工具的能力，例如从 API 或数据库获取数据。

为了解决这个限制，现代 LLM 现在可以接受可用工具模式列表（工具及其参数的描述）并生成工具调用消息。此功能称为 **工具调用** 或 **函数调用**，正在成为构建基于代理的智能应用程序的流行模式。有关 LLM 工具调用的更多信息，请参阅 [OpenAI](https://platform.openai.com/docs/guides/function-calling) 和 [Anthropic](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) 的文档。

在 AgentChat 中，[`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 可以使用工具来执行特定操作。`web_search` 工具就是这样一个工具，它允许助手代理在 Web 上搜索信息。单个自定义工具可以是 Python 函数或 [`BaseTool`](../../../reference/python/autogen_core.tools.html#autogen_core.tools.BaseTool "autogen_core.tools.BaseTool") 的子类。

另一方面，[`Workbench`](../../../reference/python/autogen_core.tools.html#autogen_core.tools.Workbench "autogen_core.tools.Workbench") 是共享状态和资源的工具集合。

注意

有关如何直接在工具和台式机上使用模型客户端的信息，请参阅核心用户指南中的 [工具](../../core-user-guide/components/tools.html) 和 [工作台](../../core-user-guide/components/workbench.html) 部分。

默认情况下，当 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 执行工具时，它将返回工具的输出作为其响应中的 [`ToolCallSummaryMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallSummaryMessage "autogen_agentchat.messages.ToolCallSummaryMessage") 中的字符串。如果您的工具没有以自然语言返回格式良好的字符串，您可以通过在 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 构造函数中设置 `reflect_on_tool_use=True` 参数来添加一个反思步骤，让模型总结工具的输出。

### 内置工具和工作台#

AutoGen Extension 提供了一组可与助手代理一起使用的内置工具。浏览 `autogen_ext.tools` 命名空间下的所有可用工具的 [API 文档](../../../reference/index.html)。例如，您可以找到以下工具：

  * `graphrag`：用于使用 GraphRAG 索引的工具。

  * `http`：用于发出 HTTP 请求的工具。

  * [`langchain`](../../../reference/python/autogen_ext.tools.langchain.html#module-autogen_ext.tools.langchain "autogen_ext.tools.langchain")：LangChain 工具的适配器。

  * [`mcp`](../../../reference/python/autogen_ext.tools.mcp.html#module-autogen_ext.tools.mcp "autogen_ext.tools.mcp")：用于使用模型聊天协议 (MCP) 服务器的工具和工作台。

### 函数工具#

[`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 自动将 Python 函数转换为 [`FunctionTool`](../../../reference/python/autogen_core.tools.html#autogen_core.tools.FunctionTool "autogen_core.tools.FunctionTool")，该工具可被代理用作工具，并从函数签名和文档字符串自动生成工具模式。

`web_search_func` 工具是函数工具的一个示例。模式已自动生成。
    
    
    from autogen_core.tools import FunctionTool
    
    
    # 使用 Python 函数定义一个工具。
    async def web_search_func(query: str) -> str:
        """在 Web 上查找信息"""
        return "AutoGen 是一个用于构建多代理应用程序的编程框架。"
    
    
    # 此步骤在 AssistantAgent 内部自动执行（如果工具是 Python 函数）。
    web_search_function_tool = FunctionTool(web_search_func, description="在 Web 上查找信息")
    # 在 AssistantAgent 的 on_messages 调用期间，模式会提供给模型。
    web_search_function_tool.schema
    
    
    
    {'name': 'web_search_func',
     'description': '在 Web 上查找信息',
     'parameters': {'type': 'object',
      'properties': {'query': {'description': 'query',
        'title': 'Query',
        'type': 'string'}},
      'required': ['query'],
      'additionalProperties': False},
     'strict': False}
    

### 模型上下文协议 (MCP) 工作台#

[`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 还可以使用来自模型上下文协议 (MCP) 服务器的工具，通过 [`McpWorkbench()`](../../../reference/python/autogen_ext.tools.mcp.html#autogen_ext.tools.mcp.McpWorkbench "autogen_ext.tools.mcp.McpWorkbench") 来实现。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.messages import TextMessage
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
    
    # 从 mcp-server-fetch 获取 fetch 工具。
    fetch_mcp_server = StdioServerParams(command="uvx", args=["mcp-server-fetch"])
    
    # 创建一个 MCP 工作台，提供与 mcp 服务器的会话。
    async with McpWorkbench(fetch_mcp_server) as workbench:  # type: ignore
        # 创建一个可以使用 fetch 工具的代理。
        model_client = OpenAIChatCompletionClient(model="gpt-4.1-nano")
        fetch_agent = AssistantAgent(
            name="fetcher", model_client=model_client, workbench=workbench, reflect_on_tool_use=True
        )
    
        # 让代理获取 URL 的内容并总结。
        result = await fetch_agent.run(task="总结 https://en.wikipedia.org/wiki/Seattle 的内容")
        assert isinstance(result.messages[-1], TextMessage)
        print(result.messages[-1].content)
    
        # 关闭模型客户端的连接。
        await model_client.close()
    
    
    
    Seattle is a major city located in the state of Washington, United States. It was founded on November 13, 1851, and incorporated as a town on January 14, 1865, and later as a city on December 2, 1869. The city is named after Chief Seattle. It covers an area of approximately 142 square miles, with a population of around 737,000 as of the 2020 Census, and an estimated 755,078 residents in 2023. Seattle is known by nicknames such as The Emerald City, Jet City, and Rain City, and has mottos including The City of Flowers and The City of Goodwill. The city operates under a mayor–council government system, with Bruce Harrell serving as mayor. Key landmarks include the Space Needle, Pike Place Market, Amazon Spheres, and the Seattle Great Wheel. It is situated on the U.S. West Coast, with a diverse urban and metropolitan area that extends to a population of over 4 million in the greater metropolitan region.
    

### 代理作为工具#

任何 [`BaseChatAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent "autogen_agentchat.agents.BaseChatAgent") 都可以通过将其包装在 [`AgentTool`](../../../reference/python/autogen_agentchat.tools.html#autogen_agentchat.tools.AgentTool "autogen_agentchat.tools.AgentTool") 中被其他代理用作工具。这支持动态的、模型驱动的多代理工作流，其中代理可以调用其他代理作为工具来解决任务。

### 并行工具调用#

某些模型支持并行工具调用，这对于需要同时调用多个工具的任务很有用。默认情况下，如果模型客户端产生多个工具调用，[`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 将并行调用工具。

当工具具有可能相互干扰的副作用时，或者当需要在不同模型之间保持一致的代理行为时，您可能希望禁用并行工具调用。这应该在模型客户端级别完成。

重要提示

使用 [`AgentTool`](../../../reference/python/autogen_agentchat.tools.html#autogen_agentchat.tools.AgentTool "autogen_agentchat.tools.AgentTool") 或 [`TeamTool`](../../../reference/python/autogen_agentchat.tools.html#autogen_agentchat.tools.TeamTool "autogen_agentchat.tools.TeamTool") 时，**必须** 禁用并行工具调用以避免并发问题。这些工具无法并行运行，因为代理和团队维护的内部状态会与并行执行发生冲突。

对于 [`OpenAIChatCompletionClient`](../../../reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.OpenAIChatCompletionClient "autogen_ext.models.openai.OpenAIChatCompletionClient") 和 [`AzureOpenAIChatCompletionClient`](../../../reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.AzureOpenAIChatCompletionClient "autogen_ext.models.openai.AzureOpenAIChatCompletionClient")，设置 `parallel_tool_calls=False` 以禁用并行工具调用。
    
    
    model_client_no_parallel_tool_call = OpenAIChatCompletionClient(
        model="gpt-4o",
        parallel_tool_calls=False,  # type: ignore
    )
    agent_no_parallel_tool_call = AssistantAgent(
        name="assistant",
        model_client=model_client_no_parallel_tool_call,
        tools=[web_search],
        system_message="使用工具解决任务。",
    )
    

### 工具迭代#

一次模型调用后跟一次工具调用或并行工具调用是一次工具迭代。默认情况下，[`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 最多执行一次迭代。

可以将代理配置为执行多次迭代，直到模型停止生成工具调用或达到最大迭代次数。您可以通过在 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 构造函数中设置 `max_tool_iterations` 参数来控制最大迭代次数。
    
    
    agent_loop = AssistantAgent(
        name="assistant_loop",
        model_client=model_client_no_parallel_tool_call,
        tools=[web_search],
        system_message="使用工具解决任务。",
        max_tool_iterations=10,  # 在停止循环之前最多执行 10 次工具调用迭代。
    )
    

## 结构化输出#

结构化输出允许模型按照应用程序提供的预定义模式返回结构化 JSON 文本。与 JSON 模式不同，模式可以作为 [Pydantic BaseModel](https://docs.pydantic.dev/latest/concepts/models/) 类提供，该类也可用于验证输出。

一旦您在 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 构造函数的 `output_content_type` 参数中指定了基模型类，代理将返回一个 [`StructuredMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.StructuredMessage "autogen_agentchat.messages.StructuredMessage")，其 `content` 的类型是基模型类的类型。

这样，您可以将代理的响应直接集成到您的应用程序中，并将模型的输出用作结构化对象。

注意

当设置了 `output_content_type` 时，默认情况下要求代理反思工具使用并根据工具调用结果返回结构化输出消息。您可以通过显式设置 `reflect_on_tool_use=False` 来禁用此行为。

结构化输出还有助于在代理的响应中整合思维链推理。请参阅下面的示例，了解如何在助手代理中使用结构化输出。
    
    
    from typing import Literal
    
    from pydantic import BaseModel
    
    
    # 代理响应的格式化为 Pydantic 基模型。
    class AgentResponse(BaseModel):
        thoughts: str
        response: Literal["happy", "sad", "neutral"]
    
    
    # 创建一个使用 OpenAI GPT-4o 模型的代理。
    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    agent = AssistantAgent(
        "assistant",
        model_client=model_client,
        system_message="按照 JSON 格式将输入分类为 happy、sad 或 neutral。",
        # 定义代理的输出内容类型。
        output_content_type=AgentResponse,
    )
    
    result = await Console(agent.run_stream(task="我很开心。"))
    
    # 检查结果中的最后一条消息，验证其类型，并打印思想和响应。
    assert isinstance(result.messages[-1], StructuredMessage)
    assert isinstance(result.messages[-1].content, AgentResponse)
    print("Thought: ", result.messages[-1].content.thoughts)
    print("Response: ", result.messages[-1].content.response)
    await model_client.close()
    
    
    
    ---------- user ----------
    I am happy.
    
    
    
    ---------- assistant ----------
    {
      "thoughts": "The user explicitly states they are happy.",
      "response": "happy"
    }
    Thought:  The user explicitly states they are happy.
    Response:  happy
    

## 流式传输令牌#

您可以通过设置 `model_client_stream=True` 来流式传输模型客户端生成的令牌。这将导致代理在 [`run_stream()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run_stream "autogen_agentchat.agents.BaseChatAgent.run_stream") 中生成 [`ModelClientStreamingChunkEvent`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.ModelClientStreamingChunkEvent "autogen_agentchat.messages.ModelClientStreamingChunkEvent") 消息。

底层的模型 API 必须支持流式传输令牌才能实现此功能。请与您的模型提供商确认是否支持此功能。
    
    
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
    
    
    
    source='user' models_usage=None metadata={} content='Name two cities in South America' type='TextMessage'
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
    source='assistant' models_usage=RequestUsage(prompt_tokens=0, completion_tokens=0) metadata={} content='Two cities in South America are Buenos Aires in Argentina and São Paulo in Brazil.' type='TextMessage'
    messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Name two cities in South America', type='TextMessage'), TextMessage(source='assistant', models_usage=RequestUsage(prompt_tokens=0, completion_tokens=0), metadata={}, content='Two cities in South America are Buenos Aires in Argentina and São Paulo in Brazil.', type='TextMessage')] stop_reason=None
    

您可以在上面的输出中看到流式传输块。这些块由模型客户端生成，并在接收时由代理产生。在所有块之后立即产生最终响应（即所有块的拼接）。

## 使用模型上下文#

[`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 有一个 `model_context` 参数，可用于传入 [`ChatCompletionContext`](../../../reference/python/autogen_core.model_context.html#autogen_core.model_context.ChatCompletionContext "autogen_core.model_context.ChatCompletionContext") 对象。这允许代理使用不同的模型上下文，例如 [`BufferedChatCompletionContext`](../../../reference/python/autogen_core.model_context.html#autogen_core.model_context.BufferedChatCompletionContext "autogen_core.model_context.BufferedChatCompletionContext") 来限制发送给模型的上下文。

默认情况下，[`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 使用 [`UnboundedChatCompletionContext`](../../../reference/python/autogen_core.model_context.html#autogen_core.model_context.UnboundedChatCompletionContext "autogen_core.model_context.UnboundedChatCompletionContext")，它会发送完整的对话历史给模型。要将上下文限制为最后 `n` 条消息，您可以使用 [`BufferedChatCompletionContext`](../../../reference/python/autogen_core.model_context.html#autogen_core.model_context.BufferedChatCompletionContext "autogen_core.model_context.BufferedChatCompletionContext")。要按令牌计数限制上下文，您可以使用 [`TokenLimitedChatCompletionContext`](../../../reference/python/autogen_core.model_context.html#autogen_core.model_context.TokenLimitedChatCompletionContext "autogen_core.model_context.TokenLimitedChatCompletionContext")。
    
    
    from autogen_core.model_context import BufferedChatCompletionContext
    
    # 创建一个仅使用上下文中最后 5 条消息生成响应的代理。
    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        tools=[web_search],
        system_message="使用工具解决任务。",
        model_context=BufferedChatCompletionContext(buffer_size=5),  # 仅使用上下文中最后 5 条消息。
    )
    

## 其他预设代理#

以下预设代理可供使用：

  * [`UserProxyAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent")：一个接受用户输入并将其作为响应返回的代理。

  * [`CodeExecutorAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.CodeExecutorAgent "autogen_agentchat.agents.CodeExecutorAgent")：一个可以执行代码的代理。

  * [`OpenAIAssistantAgent`](../../../reference/python/autogen_ext.agents.openai.html#autogen_ext.agents.openai.OpenAIAssistantAgent "autogen_ext.agents.openai.OpenAIAssistantAgent")：一个由 OpenAI Assistant 支持的代理，可以使用自定义工具。

  * [`MultimodalWebSurfer`](../../../reference/python/autogen_ext.agents.web_surfer.html#autogen_ext.agents.web_surfer.MultimodalWebSurfer "autogen_ext.agents.web_surfer.MultimodalWebSurfer")：一个多模态代理，可以搜索 Web 并访问网页获取信息。

  * [`FileSurfer`](../../../reference/python/autogen_ext.agents.file_surfer.html#autogen_ext.agents.file_surfer.FileSurfer "autogen_ext.agents.file_surfer.FileSurfer")：一个可以搜索和浏览本地文件获取信息的代理。

  * `VideoSurfer`：一个可以观看视频获取信息的代理。

## 下一步#

在了解了 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 的用法之后，我们现在可以继续下一节，了解 AgentChat 中的团队功能。

__本页内容

[ __在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/tutorial/agents.ipynb)

[ __显示源代码](../../../_sources/user-guide/agentchat-user-guide/tutorial/agents.ipynb.txt)
