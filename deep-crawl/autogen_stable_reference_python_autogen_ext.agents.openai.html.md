<!-- 来源: https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.agents.openai.html -->

# autogen_ext.agents.openai#

_class _OpenAIAgent(_name : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _description : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _client : AsyncOpenAI | AsyncAzureOpenAI_, _model : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _instructions : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _tools : [Iterable](https://docs.python.org/3/library/typing.html#typing.Iterable "\(in Python v3.14\)")[[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['web_search_preview', 'image_generation', 'local_shell'] | FileSearchToolConfig | WebSearchToolConfig | ComputerUseToolConfig | MCPToolConfig | CodeInterpreterToolConfig | ImageGenerationToolConfig | LocalShellToolConfig] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _temperature : [float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = 1_, _max_output_tokens : [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _json_mode : [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") = False_, _store : [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") = True_, _truncation : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") = 'disabled'_)[[source]](../../_modules/autogen_ext/agents/openai/_openai_agent.html#OpenAIAgent)#
    

Bases: [`BaseChatAgent`](autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent "autogen_agentchat.agents._base_chat_agent.BaseChatAgent"), [`Component`](autogen_core.html#autogen_core.Component "autogen_core._component_config.Component")[`OpenAIAgentConfig`]

一个使用 OpenAI Responses API 生成响应的智能体实现。

安装：
    
    
    pip install "autogen-ext[openai]"
    # pip install "autogen-ext[openai,azure]"  # 适用于 Azure OpenAI Assistant
    

该智能体利用 Responses API 生成响应，具有以下能力：

  * 多轮对话

  * 内置工具支持（file_search、code_interpreter、web_search_preview 等）

目前不支持自定义工具。

Changed in version v0.7.0: 添加了对内置工具类型（如 file_search、web_search_preview、code_interpreter、computer_use_preview、image_generation 和 mcp）的支持。添加了对带有必需和可选参数的工具配置的支持。

内置工具分为两类：

**可以使用字符串格式的工具**（无必需参数）：

>   * web_search_preview：可以用作 "web_search_preview" 或带有可选配置（user_location、search_context_size）
> 
>   * image_generation：可以用作 "image_generation" 或带有可选配置（background、input_image_mask）
> 
>   * local_shell：可以用作 "local_shell"（警告：仅适用于 codex-mini-latest 模型）
> 
> 

**需要字典配置的工具**（具有必需参数）：

>   * file_search：必须使用带有 vector_store_ids (List[str]) 的字典
> 
>   * computer_use_preview：必须使用带有 display_height (int)、display_width (int)、environment (str) 的字典
> 
>   * code_interpreter：必须使用带有 container (str) 的字典
> 
>   * mcp：必须使用带有 server_label (str)、server_url (str) 的字典
> 
> 

> 
> 以字符串格式使用需要参数的工具将引发 ValueError 并显示有用的错误消息。tools 参数的类型注解仅对不需要参数的工具接受字符串值。

注意

该智能体不支持自定义工具（autogen FunctionTool 或其他用户定义的工具）。仅支持通过 Responses API 提供的 OpenAI 内置工具。

参数：
    

  * **name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – 智能体名称

  * **description** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – 智能体用途的描述

  * **client** (_Union_ _[__AsyncOpenAI_ _,__AsyncAzureOpenAI_ _]_) – OpenAI 客户端实例

  * **model** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – 使用的模型（例如 "gpt-4.1"）

  * **instructions** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – 智能体的系统指令

  * **tools** (_Optional_ _[__Iterable_ _[__Union_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__BuiltinToolConfig_ _]__]__]_) – 智能体可以使用的工具。支持的无参数字符串值："web_search_preview"、"image_generation"、"local_shell"。字典值可以为具有参数的内置工具提供配置。内置工具的必需参数：- file_search：vector_store_ids (List[str]) - computer_use_preview：display_height (int)、display_width (int)、environment (str) - code_interpreter：container (str) - mcp：server_label (str)、server_url (str) 内置工具的可选参数：- file_search：max_num_results (int)、ranking_options (dict)、filters (dict) - web_search_preview：user_location (str 或 dict)、search_context_size (int) - image_generation：background (str)、input_image_mask (str) - mcp：allowed_tools (List[str])、headers (dict)、require_approval (bool) 具有模型限制的特殊工具：- local_shell：仅适用于 "codex-mini-latest" 模型（警告：支持非常有限）不支持自定义工具。

  * **temperature** (_Optional_ _[_[_float_](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)") _]_) – 响应生成的温度（默认：1）

  * **max_output_tokens** (_Optional_ _[_[_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _]_) – 最大输出令牌数

  * **json_mode** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")) – 是否使用 JSON 模式（默认：False）

  * **store** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")) – 是否存储对话（默认：True）

  * **truncation** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – 截断策略（默认："disabled"）

示例

带有内置工具的基本用法：
    
    
    import asyncio
    
    from autogen_agentchat.ui import Console
    from autogen_ext.agents.openai import OpenAIAgent
    from openai import AsyncOpenAI
    
    
    async def example():
        client = AsyncOpenAI()
        agent = OpenAIAgent(
            name="SimpleAgent",
            description="一个使用 Responses API 的简单 OpenAI 智能体",
            client=client,
            model="gpt-4.1",
            instructions="你是一个乐于助人的助手。",
            tools=["web_search_preview"],  # 仅使用不需要参数的工具
        )
        await Console(agent.run_stream(task="搜索最近的 AI 发展动态"))
    
    
    asyncio.run(example())
    

使用配置的内置工具：
    
    
    import asyncio
    
    from autogen_agentchat.ui import Console
    from autogen_ext.agents.openai import OpenAIAgent
    from openai import AsyncOpenAI
    
    
    async def example_with_configs():
        client = AsyncOpenAI()
        # 使用必需和可选参数配置工具
        tools = [
            # {
            #     "type": "file_search",
            #     "vector_store_ids": ["vs_abc123"],  # 必需
            #     "max_num_results": 10,  # 可选
            # },
            # {
            #     "type": "computer_use_preview",
            #     "display_height": 1024,  # 必需
            #     "display_width": 1280,  # 必需
            #     "environment": "linux",  # 必需
            # },
            {
                "type": "code_interpreter",
                "container": {"type": "auto"},  # 必需
            },
            # {
            #     "type": "mcp",
            #     "server_label": "my-mcp-server",  # 必需
            #     "server_url": "http://localhost:3000",  # 必需
            # },
            {
                "type": "web_search_preview",
                "user_location": {  # 可选 - 结构化位置
                    "type": "approximate",  # 必需: "approximate" 或 "exact"
                    "country": "US",  # 可选
                    "region": "CA",  # 可选
                    "city": "San Francisco",  # 可选
                },
                "search_context_size": "low",  # 可选
            },
            # "image_generation",  # 简单工具仍可以使用字符串格式
        ]
    
        agent = OpenAIAgent(
            name="ConfiguredAgent",
            description="一个带有配置工具的智能体",
            client=client,
            model="gpt-4.1",
            instructions="你是一个拥有专业工具的乐于助人的助手。",
            tools=tools,  # type: ignore
        )
        await Console(agent.run_stream(task="搜索最近的 AI 发展动态"))
    
    
    asyncio.run(example_with_configs())
    

注意：
    

OpenAIAgent 不支持自定义工具。仅使用来自 Responses API 的内置工具。

component_config_schema#
    

alias of `OpenAIAgentConfig`

component_provider_override _: ClassVar[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")]__ = 'autogen_ext.agents.openai.OpenAIAgent'_#
    

覆盖组件的 provider 字符串。这应该用于防止内部模块名称成为模块名称的一部分。

_property _produced_message_types _: [Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence "\(in Python v3.14\)")[[Type](https://docs.python.org/3/library/typing.html#typing.Type "\(in Python v3.14\)")[[TextMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.TextMessage "autogen_agentchat.messages.TextMessage")] | [Type](https://docs.python.org/3/library/typing.html#typing.Type "\(in Python v3.14\)")[[MultiModalMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.MultiModalMessage "autogen_agentchat.messages.MultiModalMessage")] | [Type](https://docs.python.org/3/library/typing.html#typing.Type "\(in Python v3.14\)")[[StopMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.StopMessage "autogen_agentchat.messages.StopMessage")] | [Type](https://docs.python.org/3/library/typing.html#typing.Type "\(in Python v3.14\)")[[ToolCallSummaryMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallSummaryMessage "autogen_agentchat.messages.ToolCallSummaryMessage")] | [Type](https://docs.python.org/3/library/typing.html#typing.Type "\(in Python v3.14\)")[[HandoffMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage")]]_#
    

返回此智能体可以生成的消息类型。

_async _on_messages(_messages : [Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence "\(in Python v3.14\)")[[BaseChatMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage")]_, _cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken")_) → [Response](autogen_agentchat.base.html#autogen_agentchat.base.Response "autogen_agentchat.base._chat_agent.Response")[[source]](../../_modules/autogen_ext/agents/openai/_openai_agent.html#OpenAIAgent.on_messages)#
    

处理传入的消息并返回响应。

注意

智能体是有状态的，传递给此方法的消息应该是自上次调用此方法以来的新消息。智能体应在此方法的调用之间维护其状态。例如，如果智能体需要记住先前的消息以响应当前消息，则应将先前的消息存储在智能体状态中。

_async _on_messages_stream(_messages : [Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence "\(in Python v3.14\)")[[BaseChatMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage")]_, _cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken")_) → [AsyncGenerator](https://docs.python.org/3/library/typing.html#typing.AsyncGenerator "\(in Python v3.14\)")[Annotated[[ToolCallRequestEvent](autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallRequestEvent "autogen_agentchat.messages.ToolCallRequestEvent") | [ToolCallExecutionEvent](autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallExecutionEvent "autogen_agentchat.messages.ToolCallExecutionEvent") | [MemoryQueryEvent](autogen_agentchat.messages.html#autogen_agentchat.messages.MemoryQueryEvent "autogen_agentchat.messages.MemoryQueryEvent") | [UserInputRequestedEvent](autogen_agentchat.messages.html#autogen_agentchat.messages.UserInputRequestedEvent "autogen_agentchat.messages.UserInputRequestedEvent") | [ModelClientStreamingChunkEvent](autogen_agentchat.messages.html#autogen_agentchat.messages.ModelClientStreamingChunkEvent "autogen_agentchat.messages.ModelClientStreamingChunkEvent") | [ThoughtEvent](autogen_agentchat.messages.html#autogen_agentchat.messages.ThoughtEvent "autogen_agentchat.messages.ThoughtEvent") | [SelectSpeakerEvent](autogen_agentchat.messages.html#autogen_agentchat.messages.SelectSpeakerEvent "autogen_agentchat.messages.SelectSpeakerEvent") | [CodeGenerationEvent](autogen_agentchat.messages.html#autogen_agentchat.messages.CodeGenerationEvent "autogen_agentchat.messages.CodeGenerationEvent") | [CodeExecutionEvent](autogen_agentchat.messages.html#autogen_agentchat.messages.CodeExecutionEvent "autogen_agentchat.messages.CodeExecutionEvent"), FieldInfo(annotation=NoneType, required=True, discriminator='type')] | [TextMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.TextMessage "autogen_agentchat.messages.TextMessage") | [MultiModalMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.MultiModalMessage "autogen_agentchat.messages.MultiModalMessage") | [StopMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.StopMessage "autogen_agentchat.messages.StopMessage") | [ToolCallSummaryMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallSummaryMessage "autogen_agentchat.messages.ToolCallSummaryMessage") | [HandoffMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage") | [Response](autogen_agentchat.base.html#autogen_agentchat.base.Response "autogen_agentchat.base._chat_agent.Response"), [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")][[source]](../../_modules/autogen_ext/agents/openai/_openai_agent.html#OpenAIAgent.on_messages_stream)#
    

处理传入的消息并返回消息流，最后一项是响应。`BaseChatAgent` 中的基础实现只是调用 `on_messages()` 并产生响应中的消息。

注意

智能体是有状态的，传递给此方法的消息应该是自上次调用此方法以来的新消息。智能体应在此方法的调用之间维护其状态。例如，如果智能体需要记住先前的消息以响应当前消息，则应将先前的消息存储在智能体状态中。

_async _on_reset(_cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/agents/openai/_openai_agent.html#OpenAIAgent.on_reset)#
    

将智能体重置为其初始化状态。

_async _save_state() → [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")][[source]](../../_modules/autogen_ext/agents/openai/_openai_agent.html#OpenAIAgent.save_state)#
    

导出状态。无状态智能体的默认实现。

_async _load_state(_state : [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/agents/openai/_openai_agent.html#OpenAIAgent.load_state)#
    

从保存的状态恢复智能体。无状态智能体的默认实现。

to_config() → OpenAIAgentConfig[[source]](../../_modules/autogen_ext/agents/openai/_openai_agent.html#OpenAIAgent.to_config)#
    

私有 _to_config 方法的公共包装器。

_classmethod _from_config(_config : OpenAIAgentConfig_) → OpenAIAgent[[source]](../../_modules/autogen_ext/agents/openai/_openai_agent.html#OpenAIAgent.from_config)#
    

私有 _from_config 类方法的公共包装器。

_property _tools _: [list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_#
    

对智能体工具的公共访问。

_property _model _: [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_#
    

对智能体模型的公共访问。

_class _OpenAIAssistantAgent(_name : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _description : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _client : AsyncOpenAI | AsyncAzureOpenAI_, _model : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _instructions : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _tools : [Iterable](https://docs.python.org/3/library/typing.html#typing.Iterable "\(in Python v3.14\)")[[Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['code_interpreter', 'file_search'] | [Tool](autogen_core.tools.html#autogen_core.tools.Tool "autogen_core.tools._base.Tool") | [Callable](https://docs.python.org/3/library/typing.html#typing.Callable "\(in Python v3.14\)")[[...], [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")] | [Callable](https://docs.python.org/3/library/typing.html#typing.Callable "\(in Python v3.14\)")[[...], [Awaitable](https://docs.python.org/3/library/typing.html#typing.Awaitable "\(in Python v3.14\)")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]]] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _assistant_id : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _thread_id : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _metadata : [Dict](https://docs.python.org/3/library/typing.html#typing.Dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _response_format : [Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['auto'] | ResponseFormatText | ResponseFormatJSONObject | ResponseFormatJSONSchema | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _temperature : [float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _tool_resources : ToolResources | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _top_p : [float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_)[[source]](../../_modules/autogen_ext/agents/openai/_openai_assistant_agent.html#OpenAIAssistantAgent)#
    

Bases: [`BaseChatAgent`](autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent "autogen_agentchat.agents._base_chat_agent.BaseChatAgent")

一个使用 Assistant API 生成响应的智能体实现。

安装：
    
    
    pip install "autogen-ext[openai]"  # 适用于 OpenAI Assistant
    # pip install "autogen-ext[openai,azure]"  # 适用于 Azure OpenAI Assistant
    

该智能体利用 Assistant API 创建具有以下能力的 AI 助手：

  * 代码解释和执行

  * 文件处理和搜索

  * 自定义函数调用

  * 多轮对话

智能体维护对话线程，并可以使用各种工具，包括

  * 代码解释器：用于执行代码和处理文件

  * 文件搜索：用于搜索上传的文档

  * 自定义函数：用于通过用户定义的工具扩展能力

主要特性：

  * 支持多种文件格式，包括代码、文档、图像

  * 每个助手最多可处理 128 个工具

  * 在线程中维护对话上下文

  * 支持为代码解释器和搜索上传文件

  * 向量存储集成以实现高效的文件搜索

  * 自动文件解析和嵌入

你可以通过提供 thread_id 或 assistant_id 参数来使用现有的线程或助手。

示例

使用助手分析 CSV 文件中的数据：
    
    
    from openai import AsyncOpenAI
    from autogen_core import CancellationToken
    import asyncio
    from autogen_ext.agents.openai import OpenAIAssistantAgent
    from autogen_agentchat.messages import TextMessage
    
    
    async def example():
        cancellation_token = CancellationToken()
    
        # 创建一个 OpenAI 客户端
        client = AsyncOpenAI(api_key="your-api-key", base_url="your-base-url")
    
        # 创建一个带有代码解释器的助手
        assistant = OpenAIAssistantAgent(
            name="PythonHelper",
            description="协助 Python 编程",
            client=client,
            model="gpt-4",
            instructions="你是一个乐于助人的 Python 编程助手。",
            tools=["code_interpreter"],
        )
    
        # 上传文件供助手使用
        await assistant.on_upload_for_code_interpreter("data.csv", cancellation_token)
    
        # 从助手获取响应
        response = await assistant.on_messages(
            [TextMessage(source="user", content="分析 data.csv 中的数据")], cancellation_token
        )
    
        print(response)
    
        # 清理资源
        await assistant.delete_uploaded_files(cancellation_token)
        await assistant.delete_assistant(cancellation_token)
    
    
    asyncio.run(example())
    

使用带 AAD 身份验证的 Azure OpenAI Assistant：
    
    
    from openai import AsyncAzureOpenAI
    import asyncio
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    from autogen_core import CancellationToken
    from autogen_ext.agents.openai import OpenAIAssistantAgent
    from autogen_agentchat.messages import TextMessage
    
    
    async def example():
        cancellation_token = CancellationToken()
    
        # 创建 Azure OpenAI 客户端
        token_provider = get_bearer_token_provider(DefaultAzureCredential())
        client = AsyncAzureOpenAI(
            azure_deployment="YOUR_AZURE_DEPLOYMENT",
            api_version="YOUR_API_VERSION",
            azure_endpoint="YOUR_AZURE_ENDPOINT",
            azure_ad_token_provider=token_provider,
        )
    
        # 创建一个带有代码解释器的助手
        assistant = OpenAIAssistantAgent(
            name="PythonHelper",
            description="协助 Python 编程",
            client=client,
            model="gpt-4o",
            instructions="你是一个乐于助人的 Python 编程助手。",
            tools=["code_interpreter"],
        )
    
        # 从助手获取响应
        response = await assistant.on_messages([TextMessage(source="user", content="你好。")], cancellation_token)
    
        print(response)
    
        # 清理资源
        await assistant.delete_assistant(cancellation_token)
    
    
    asyncio.run(example())
    

参数：
    

  * **name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – 助手的名称

  * **description** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – 助手用途的描述

  * **client** (_AsyncOpenAI_ _|__AsyncAzureOpenAI_) – OpenAI 客户端或 Azure OpenAI 客户端实例

  * **model** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – 使用的模型（例如 "gpt-4"）

  * **instructions** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – 助手的系统指令

  * **tools** (_Optional_ _[__Iterable_ _[__Union_ _[__Literal_ _[__"code_interpreter"__,__"file_search"__]__,__Tool_ _|__Callable_ _[__...__,__Any_ _]__|__Callable_ _[__...__,__Awaitable_ _[__Any_ _]__]__]__]__]_) – 助手可以使用的工具

  * **assistant_id** (_Optional_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]_) – 要使用的现有助手的 ID

  * **thread_id** (_Optional_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]_) – 要使用的现有线程的 ID

  * **metadata** (_Optional_ _[__Dict_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]__]_) – 助手的附加元数据。

  * **response_format** (_Optional_ _[__AssistantResponseFormatOptionParam_ _]_) – 响应格式设置

  * **temperature** (_Optional_ _[_[_float_](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)") _]_) – 响应生成的温度

  * **tool_resources** (_Optional_ _[__ToolResources_ _]_) – 附加工具配置

  * **top_p** (_Optional_ _[_[_float_](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)") _]_) – Top p 采样参数

_property _produced_message_types _: [Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence "\(in Python v3.14\)")[[type](https://docs.python.org/3/library/functions.html#type "\(in Python v3.14\)")[[BaseChatMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage")]]_#
    

助手智能体生成的消息类型。

_property _threads _: AsyncThreads_#
    

_property _runs _: AsyncRuns_#
    

_property _messages _: AsyncMessages_#
    

_async _on_messages(_messages : [Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence "\(in Python v3.14\)")[[BaseChatMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage")]_, _cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken")_) → [Response](autogen_agentchat.base.html#autogen_agentchat.base.Response "autogen_agentchat.base._chat_agent.Response")[[source]](../../_modules/autogen_ext/agents/openai/_openai_assistant_agent.html#OpenAIAssistantAgent.on_messages)#
    

处理传入的消息并返回响应。

_async _on_messages_stream(_messages : [Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence "\(in Python v3.14\)")[[BaseChatMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage")]_, _cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken")_) → [AsyncGenerator](https://docs.python.org/3/library/typing.html#typing.AsyncGenerator "\(in Python v3.14\)")[[BaseAgentEvent](autogen_agentchat.messages.html#autogen_agentchat.messages.BaseAgentEvent "autogen_agentchat.messages.BaseAgentEvent") | [BaseChatMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage") | [Response](autogen_agentchat.base.html#autogen_agentchat.base.Response "autogen_agentchat.base._chat_agent.Response"), [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")][[source]](../../_modules/autogen_ext/agents/openai/_openai_assistant_agent.html#OpenAIAssistantAgent.on_messages_stream)#
    

处理传入的消息并返回响应。

_async _handle_incoming_message(_message : [BaseChatMessage](autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage")_, _cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/agents/openai/_openai_assistant_agent.html#OpenAIAssistantAgent.handle_incoming_message)#
    

通过将常规文本消息添加到线程来处理它们。

_async _on_reset(_cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/agents/openai/_openai_assistant_agent.html#OpenAIAssistantAgent.on_reset)#
    

通过删除自初始化以来的新消息和运行来处理重置命令。

_async _on_upload_for_code_interpreter(_file_paths : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [Iterable](https://docs.python.org/3/library/typing.html#typing.Iterable "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_, _cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/agents/openai/_openai_assistant_agent.html#OpenAIAssistantAgent.on_upload_for_code_interpreter)#
    

处理代码解释器的文件上传。

_async _on_upload_for_file_search(_file_paths : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [Iterable](https://docs.python.org/3/library/typing.html#typing.Iterable "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_, _cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/agents/openai/_openai_assistant_agent.html#OpenAIAssistantAgent.on_upload_for_file_search)#
    

处理文件搜索的文件上传。

_async _delete_uploaded_files(_cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/agents/openai/_openai_assistant_agent.html#OpenAIAssistantAgent.delete_uploaded_files)#
    

删除此智能体实例上传的所有文件。

_async _delete_assistant(_cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/agents/openai/_openai_assistant_agent.html#OpenAIAssistantAgent.delete_assistant)#
    

如果助手是由此实例创建的，则删除它。

_async _delete_vector_store(_cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/agents/openai/_openai_assistant_agent.html#OpenAIAssistantAgent.delete_vector_store)#
    

如果向量存储是由此实例创建的，则删除它。

_async _save_state() → [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")][[source]](../../_modules/autogen_ext/agents/openai/_openai_assistant_agent.html#OpenAIAssistantAgent.save_state)#
    

导出状态。无状态智能体的默认实现。

_async _load_state(_state : [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/agents/openai/_openai_assistant_agent.html#OpenAIAssistantAgent.load_state)#
    

从保存的状态恢复智能体。无状态智能体的默认实现。

__本页内容

[ __在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/reference/python/autogen_ext.agents.openai.rst)

[ __查看源文件](../../_sources/reference/python/autogen_ext.agents.openai.rst.txt)