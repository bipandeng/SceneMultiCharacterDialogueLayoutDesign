agentchat-user-guide/quickstart.html<!-- 来源: https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.tools.mcp.html -->

# autogen_ext.tools.mcp#

create_mcp_server_session(_server_params : Annotated[StdioServerParams | SseServerParams | StreamableHttpServerParams, FieldInfo(annotation=NoneType, required=True, discriminator='type')]_, _sampling_callback : SamplingFnT | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_) → [AsyncGenerator](https://docs.python.org/3/library/typing.html#typing.AsyncGenerator "\(in Python v3.14\)")[ClientSession, [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")][[source]](../../_modules/autogen_ext/tools/mcp/_session.html#create_mcp_server_session)#
    

为给定的服务器参数创建一个 MCP 客户端会话。

_class _McpSessionActor(_server_params : Annotated[StdioServerParams | SseServerParams | StreamableHttpServerParams, FieldInfo(annotation=NoneType, required=True, discriminator='type')]_, _model_client : [ChatCompletionClient](autogen_core.models.html#autogen_core.models.ChatCompletionClient "autogen_core.models._model_client.ChatCompletionClient") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_)[[source]](../../_modules/autogen_ext/tools/mcp/_actor.html#McpSessionActor)#
    

Bases: [`ComponentBase`](autogen_core.html#autogen_core.ComponentBase "autogen_core._component_config.ComponentBase")[`BaseModel`], [`Component`](autogen_core.html#autogen_core.Component "autogen_core._component_config.Component")[`McpSessionActorConfig`]

component_type _: ClassVar[ComponentType]__ = 'mcp_session_actor'_#
    

组件的逻辑类型。

component_config_schema#
    

alias of `McpSessionActorConfig`

component_provider_override _: ClassVar[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")]__ = 'autogen_ext.tools.mcp.McpSessionActor'_#
    

覆盖组件的 provider 字符串。这应该用于防止内部模块名称成为模块名称的一部分。

server_params _: Annotated[StdioServerParams | SseServerParams | StreamableHttpServerParams, FieldInfo(annotation=NoneType, required=True, discriminator='type')]_#
    

_property _initialize_result _: InitializeResult | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_#
    

_async _initialize() → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/tools/mcp/_actor.html#McpSessionActor.initialize)#
    

_async _call(_type : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _args : McpActorArgs | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_) → Future[[Coroutine](https://docs.python.org/3/library/typing.html#typing.Coroutine "\(in Python v3.14\)")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), ListToolsResult] | [Coroutine](https://docs.python.org/3/library/typing.html#typing.Coroutine "\(in Python v3.14\)")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), CallToolResult] | [Coroutine](https://docs.python.org/3/library/typing.html#typing.Coroutine "\(in Python v3.14\)")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), ListPromptsResult] | [Coroutine](https://docs.python.org/3/library/typing.html#typing.Coroutine "\(in Python v3.14\)")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), ListResourcesResult] | [Coroutine](https://docs.python.org/3/library/typing.html#typing.Coroutine "\(in Python v3.14\)")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), ListResourceTemplatesResult] | [Coroutine](https://docs.python.org/3/library/typing.html#typing.Coroutine "\(in Python v3.14\)")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), ReadResourceResult] | [Coroutine](https://docs.python.org/3/library/typing.html#typing.Coroutine "\(in Python v3.14\)")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), GetPromptResult]][[source]](../../_modules/autogen_ext/tools/mcp/_actor.html#McpSessionActor.call)#
    

_async _close() → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/tools/mcp/_actor.html#McpSessionActor.close)#
    

_class _StdioMcpToolAdapter(_server_params : StdioServerParams_, _tool : Tool_, _session : ClientSession | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_)[[source]](../../_modules/autogen_ext/tools/mcp/_stdio.html#StdioMcpToolAdapter)#
    

Bases: `McpToolAdapter`[`StdioServerParams`], [`Component`](autogen_core.html#autogen_core.Component "autogen_core._component_config.Component")[`StdioMcpToolAdapterConfig`]

允许你包装通过 STDIO 运行的 MCP 工具并使其可供 AutoGen 使用。

此适配器使得通过标准输入/输出与 AutoGen 智能体通信的 MCP 兼容工具能够被使用。常见用例包括包装实现模型上下文协议 (MCP) 的命令行工具和本地服务。

注意

要使用此类，你需要为 autogen-ext 包安装 mcp 扩展。
    
    
    pip install -U "autogen-ext[mcp]"
    

参数：
    

  * **server_params** (_StdioServerParams_) – MCP 服务器连接的参数，包括要运行的命令及其参数。

  * **tool** ([_Tool_](autogen_core.tools.html#autogen_core.tools.Tool "autogen_core.tools.Tool")) – 要包装的 MCP 工具。

  * **session** (_ClientSession_ _,__optional_) – 要使用的 MCP 客户端会话。如果未提供，将创建一个新会话。这对于测试或希望自行管理会话生命周期的情况很有用。

有关示例，请参见 `mcp_server_tools()`。

component_config_schema#
    

alias of `StdioMcpToolAdapterConfig`

component_provider_override _: ClassVar[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")]__ = 'autogen_ext.tools.mcp.StdioMcpToolAdapter'_#
    

覆盖组件的 provider 字符串。这应该用于防止内部模块名称成为模块名称的一部分。

_pydantic model _StdioServerParams[[source]](../../_modules/autogen_ext/tools/mcp/_config.html#StdioServerParams)#
    

Bases: `StdioServerParameters`

通过 STDIO 连接到 MCP 服务器的参数。

显示 JSON schema
    
    
    {
       "title": "StdioServerParams",
       "description": "通过 STDIO 连接到 MCP 服务器的参数。",
       "type": "object",
       "properties": {
          "command": {
             "title": "Command",
             "type": "string"
          },
          "args": {
             "items": {
                "type": "string"
             },
             "title": "Args",
             "type": "array"
          },
          "env": {
             "anyOf": [
                {
                   "additionalProperties": {
                      "type": "string"
                   },
                   "type": "object"
                },
                {
                   "type": "null"
                }
             ],
             "default": null,
             "title": "Env"
          },
          "cwd": {
             "anyOf": [
                {
                   "type": "string"
                },
                {
                   "format": "path",
                   "type": "string"
                },
                {
                   "type": "null"
                }
             ],
             "default": null,
             "title": "Cwd"
          },
          "encoding": {
             "default": "utf-8",
             "title": "Encoding",
             "type": "string"
          },
          "encoding_error_handler": {
             "default": "strict",
             "enum": [
                "strict",
                "ignore",
                "replace"
             ],
             "title": "Encoding Error Handler",
             "type": "string"
          },
          "type": {
             "const": "StdioServerParams",
             "default": "StdioServerParams",
             "title": "Type",
             "type": "string"
          },
          "read_timeout_seconds": {
             "default": 5,
             "title": "Read Timeout Seconds",
             "type": "number"
          }
       },
       "required": [
          "command"
       ]
    }
    

字段：
    

  * `read_timeout_seconds (float)`

  * `type (Literal['StdioServerParams'])`

_field _type _: [Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['StdioServerParams']__ = 'StdioServerParams'_#
    

_field _read_timeout_seconds _: [float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_ _ = 5_#
    

_class _SseMcpToolAdapter(_server_params : SseServerParams_, _tool : Tool_, _session : ClientSession | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_)[[source]](../../_modules/autogen_ext/tools/mcp/_sse.html#SseMcpToolAdapter)#
    

Bases: `McpToolAdapter`[`SseServerParams`], [`Component`](autogen_core.html#autogen_core.Component "autogen_core._component_config.Component")[`SseMcpToolAdapterConfig`]

允许你包装通过 Server-Sent Events (SSE) 运行的 MCP 工具并使其可供 AutoGen 使用。

此适配器使得通过带 SSE 的 HTTP 与 AutoGen 智能体通信的 MCP 兼容工具能够被使用。常见用例包括与远程 MCP 服务、基于云的工具以及实现模型上下文协议 (MCP) 的 Web API 集成。

注意

要使用此类，你需要为 autogen-ext 包安装 mcp 扩展。
    
    
    pip install -U "autogen-ext[mcp]"
    

参数：
    

  * **server_params** (_SseServerParameters_) – MCP 服务器连接的参数，包括 URL、headers 和超时。

  * **tool** ([_Tool_](autogen_core.tools.html#autogen_core.tools.Tool "autogen_core.tools.Tool")) – 要包装的 MCP 工具。

  * **session** (_ClientSession_ _,__optional_) – 要使用的 MCP 客户端会话。如果未提供，将创建一个新会话。这对于测试或希望自行管理会话生命周期的情况很有用。

示例

使用通过 SSE 实现 MCP 的远程翻译服务创建允许 AutoGen 智能体执行翻译的工具：
    
    
    import asyncio
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_ext.tools.mcp import SseMcpToolAdapter, SseServerParams
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.ui import Console
    from autogen_core import CancellationToken
    
    
    async def main() -> None:
        # 为远程 MCP 服务创建服务器参数
        server_params = SseServerParams(
            url="https://api.example.com/mcp",
            headers={"Authorization": "Bearer your-api-key", "Content-Type": "application/json"},
            timeout=30,  # 连接超时（秒）
        )
    
        # 从服务器获取翻译工具
        adapter = await SseMcpToolAdapter.from_server_params(server_params, "translate")
    
        # 创建一个可以使用翻译工具的智能体
        model_client = OpenAIChatCompletionClient(model="gpt-4")
        agent = AssistantAgent(
            name="translator",
            model_client=model_client,
            tools=[adapter],
            system_message="你是一个乐于助人的翻译助手。",
        )
    
        # 让智能体翻译一些文本
        await Console(
            agent.run_stream(task="将 'Hello, how are you?' 翻译成西班牙语", cancellation_token=CancellationToken())
        )
    
    
    if __name__ == "__main__":
        asyncio.run(main())
    

component_config_schema#
    

alias of `SseMcpToolAdapterConfig`

component_provider_override _: ClassVar[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")]__ = 'autogen_ext.tools.mcp.SseMcpToolAdapter'_#
    

覆盖组件的 provider 字符串。这应该用于防止内部模块名称成为模块名称的一部分。

_pydantic model _SseServerParams[[source]](../../_modules/autogen_ext/tools/mcp/_config.html#SseServerParams)#
    

Bases: `BaseModel`

通过 SSE 连接到 MCP 服务器的参数。

显示 JSON schema
    
    
    {
       "title": "SseServerParams",
       "description": "通过 SSE 连接到 MCP 服务器的参数。",
       "type": "object",
       "properties": {
          "type": {
             "const": "SseServerParams",
             "default": "SseServerParams",
             "title": "Type",
             "type": "string"
          },
          "url": {
             "title": "Url",
             "type": "string"
          },
          "headers": {
             "anyOf": [
                {
                   "type": "object"
                },
                {
                   "type": "null"
                }
             ],
             "default": null,
             "title": "Headers"
          },
          "timeout": {
             "default": 5,
             "title": "Timeout",
             "type": "number"
          },
          "sse_read_timeout": {
             "default": 300,
             "title": "Sse Read Timeout",
             "type": "number"
          }
       },
       "required": [
          "url"
       ]
    }
    

字段：
    

  * `headers (dict[str, Any] | None)`

  * `sse_read_timeout (float)`

  * `timeout (float)`

  * `type (Literal['SseServerParams'])`

  * `url (str)`

_field _type _: [Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['SseServerParams']__ = 'SseServerParams'_#
    

_field _url _: [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ _[Required]_#
    

_field _headers _: [dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ _ = None_#
    

_field _timeout _: [float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_ _ = 5_#
    

_field _sse_read_timeout _: [float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_ _ = 300_#
    

_class _StreamableHttpMcpToolAdapter(_server_params : StreamableHttpServerParams_, _tool : Tool_, _session : ClientSession | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_)[[source]](../../_modules/autogen_ext/tools/mcp/_streamable_http.html#StreamableHttpMcpToolAdapter)#
    

Bases: `McpToolAdapter`[`StreamableHttpServerParams`], [`Component`](autogen_core.html#autogen_core.Component "autogen_core._component_config.Component")[`StreamableHttpMcpToolAdapterConfig`]

允许你包装通过 Streamable HTTP 运行的 MCP 工具并使其可供 AutoGen 使用。

此适配器使得通过 Streamable HTTP 与 AutoGen 智能体通信的 MCP 兼容工具能够被使用。常见用例包括与远程 MCP 服务、基于云的工具以及实现模型上下文协议 (MCP) 的 Web API 集成。

注意

要使用此类，你需要为 autogen-ext 包安装 mcp 扩展。
    
    
    pip install -U "autogen-ext[mcp]"
    

参数：
    

  * **server_params** (_StreamableHttpServerParams_) – MCP 服务器连接的参数，包括 URL、headers 和超时。

  * **tool** ([_Tool_](autogen_core.tools.html#autogen_core.tools.Tool "autogen_core.tools.Tool")) – 要包装的 MCP 工具。

  * **session** (_ClientSession_ _,__optional_) – 要使用的 MCP 客户端会话。如果未提供，将创建一个新会话。这对于测试或希望自行管理会话生命周期的情况很有用。

示例

使用通过 Streamable HTTP 实现 MCP 的远程翻译服务创建允许 AutoGen 智能体执行翻译的工具：
    
    
    import asyncio
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_ext.tools.mcp import StreamableHttpMcpToolAdapter, StreamableHttpServerParams
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.ui import Console
    from autogen_core import CancellationToken
    
    
    async def main() -> None:
        # 为远程 MCP 服务创建服务器参数
        server_params = StreamableHttpServerParams(
            url="https://api.example.com/mcp",
            headers={"Authorization": "Bearer your-api-key", "Content-Type": "application/json"},
            timeout=30.0,  # HTTP 超时（秒）
            sse_read_timeout=300.0,  # SSE 读取超时（秒）（5 分钟）
            terminate_on_close=True,
        )
    
        # 从服务器获取翻译工具
        adapter = await StreamableHttpMcpToolAdapter.from_server_params(server_params, "translate")
    
        # 创建一个可以使用翻译工具的智能体
        model_client = OpenAIChatCompletionClient(model="gpt-4")
        agent = AssistantAgent(
            name="translator",
            model_client=model_client,
            tools=[adapter],
            system_message="你是一个乐于助人的翻译助手。",
        )
    
        # 让智能体翻译一些文本
        await Console(
            agent.run_stream(task="将 'Hello, how are you?' 翻译成西班牙语", cancellation_token=CancellationToken())
        )
    
    
    if __name__ == "__main__":
        asyncio.run(main())
    

component_config_schema#
    

alias of `StreamableHttpMcpToolAdapterConfig`

component_provider_override _: ClassVar[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")]__ = 'autogen_ext.tools.mcp.StreamableHttpMcpToolAdapter'_#
    

覆盖组件的 provider 字符串。这应该用于防止内部模块名称成为模块名称的一部分。

_pydantic model _StreamableHttpServerParams[[source]](../../_modules/autogen_ext/tools/mcp/_config.html#StreamableHttpServerParams)#
    

Bases: `BaseModel`

通过 Streamable HTTP 连接到 MCP 服务器的参数。

显示 JSON schema
    
    
    {
       "title": "StreamableHttpServerParams",
       "description": "通过 Streamable HTTP 连接到 MCP 服务器的参数。",
       "type": "object",
       "properties": {
          "type": {
             "const": "StreamableHttpServerParams",
             "default": "StreamableHttpServerParams",
             "title": "Type",
             "type": "string"
          },
          "url": {
             "title": "Url",
             "type": "string"
          },
          "headers": {
             "anyOf": [
                {
                   "type": "object"
                },
                {
                   "type": "null"
                }
             ],
             "default": null,
             "title": "Headers"
          },
          "timeout": {
             "default": 30.0,
             "title": "Timeout",
             "type": "number"
          },
          "sse_read_timeout": {
             "default": 300.0,
             "title": "Sse Read Timeout",
             "type": "number"
          },
          "terminate_on_close": {
             "default": true,
             "title": "Terminate On Close",
             "type": "boolean"
          }
       },
       "required": [
          "url"
       ]
    }
    

字段：
    

  * `headers (dict[str, Any] | None)`

  * `sse_read_timeout (float)`

  * `terminate_on_close (bool)`

  * `timeout (float)`

  * `type (Literal['StreamableHttpServerParams'])`

  * `url (str)`

_field _type _: [Literal](https://docs.python.org/3/library/typing.html#typing.Literal "\(in Python v3.14\)")['StreamableHttpServerParams']__ = 'StreamableHttpServerParams'_#
    

_field _url _: [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_ _[Required]_#
    

_field _headers _: [dict](https://docs.python.org/3/library/stdtypes.html#dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_ _ = None_#
    

_field _timeout _: [float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_ _ = 30.0_#
    

_field _sse_read_timeout _: [float](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")_ _ = 300.0_#
    

_field _terminate_on_close _: [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")_ _ = True_#
    

_async _mcp_server_tools(_server_params : Annotated[StdioServerParams | SseServerParams | StreamableHttpServerParams, FieldInfo(annotation=NoneType, required=True, discriminator='type')]_, _session : ClientSession | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_) → [list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[StdioMcpToolAdapter | SseMcpToolAdapter | StreamableHttpMcpToolAdapter][[source]](../../_modules/autogen_ext/tools/mcp/_factory.html#mcp_server_tools)#
    

创建一个可与 AutoGen 智能体一起使用的 MCP 工具适配器列表。

警告

仅连接到可信的 MCP 服务器，特别是在使用 StdioServerParams 时，因为它会在本地环境中执行命令。

此工厂函数连接到 MCP 服务器并返回所有可用工具的适配器。这些适配器可以直接分配给 AutoGen 智能体的工具列表。

注意

要使用此函数，你需要为 autogen-ext 包安装 mcp 扩展。
    
    
    pip install -U "autogen-ext[mcp]"
    

参数：
    

  * **server_params** (_McpServerParams_) – MCP 服务器的连接参数。可以是用于命令行工具的 StdioServerParams，也可以是用于 HTTP/SSE 服务的 SseServerParams 和 StreamableHttpServerParams。

  * **session** (_ClientSession_ _|__None_) – 可选的现有会话用于此。当你想要重用与 MCP 服务器的现有连接时使用。在创建 MCP 工具适配器时将重用该会话。

返回：
    

**list[StdioMcpToolAdapter | SseMcpToolAdapter | StreamableHttpMcpToolAdapter]** – 可与 AutoGen 智能体一起使用的工具适配器列表。

示例

**通过标准 I/O 的本地文件系统 MCP 服务示例：**

从 npm 安装文件系统服务器包（需要 Node.js 16+ 和 npm）。
    
    
    npm install -g @modelcontextprotocol/server-filesystem
    

创建一个可以使用本地文件系统 MCP 服务器所有工具的智能体。
    
    
    import asyncio
    from pathlib import Path
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
    from autogen_agentchat.agents import AssistantAgent
    from autogen_core import CancellationToken
    
    
    async def main() -> None:
        # 为本地文件系统访问设置服务器参数
        desktop = str(Path.home() / "Desktop")
        server_params = StdioServerParams(
            command="npx.cmd", args=["-y", "@modelcontextprotocol/server-filesystem", desktop]
        )
    
        # 从服务器获取所有可用工具
        tools = await mcp_server_tools(server_params)
    
        # 创建一个可以使用所有工具的智能体
        agent = AssistantAgent(
            name="file_manager",
            model_client=OpenAIChatCompletionClient(model="gpt-4"),
            tools=tools,  # type: ignore
        )
    
        # 该智能体现在可以使用任何文件系统工具
        await agent.run(task="创建一个名为 test.txt 的文件并写入一些内容", cancellation_token=CancellationToken())
    
    
    if __name__ == "__main__":
        asyncio.run(main())
    

**通过标准 I/O 的本地 fetch MCP 服务示例：**

安装 mcp-server-fetch 包。
    
    
    pip install mcp-server-fetch
    

创建一个可以使用本地 MCP 服务器的 fetch 工具的智能体。
    
    
    import asyncio
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
    
    
    async def main() -> None:
        # 从 mcp-server-fetch 获取 fetch 工具。
        fetch_mcp_server = StdioServerParams(command="uvx", args=["mcp-server-fetch"])
        tools = await mcp_server_tools(fetch_mcp_server)
    
        # 创建一个可以使用 fetch 工具的智能体。
        model_client = OpenAIChatCompletionClient(model="gpt-4o")
        agent = AssistantAgent(name="fetcher", model_client=model_client, tools=tools, reflect_on_tool_use=True)  # type: ignore
    
        # 让智能体获取 URL 的内容并对其进行总结。
        result = await agent.run(task="总结 https://en.wikipedia.org/wiki/Seattle 的内容")
        print(result.messages[-1])
    
    
    asyncio.run(main())
    

**在多个工具之间共享 MCP 客户端会话：**

你可以创建单个 MCP 客户端会话并在多个工具之间共享。当服务器维护应在多个请求中重用的会话状态（例如浏览器状态）时，这有时是必需的。

以下示例展示了如何创建到本地 [Playwright](https://github.com/microsoft/playwright-mcp) 服务器的单个 MCP 客户端会话并在多个工具之间共享。
    
    
    import asyncio
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_ext.tools.mcp import StdioServerParams, create_mcp_server_session, mcp_server_tools
    
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o", parallel_tool_calls=False)  # type: ignore
        params = StdioServerParams(
            command="npx",
            args=["@playwright/mcp@latest"],
            read_timeout_seconds=60,
        )
        async with create_mcp_server_session(params) as session:
            await session.initialize()
            tools = await mcp_server_tools(server_params=params, session=session)
            print(f"Tools: {[tool.name for tool in tools]}")
    
            agent = AssistantAgent(
                name="Assistant",
                model_client=model_client,
                tools=tools,  # type: ignore
            )
    
            termination = TextMentionTermination("TERMINATE")
            team = RoundRobinGroupChat([agent], termination_condition=termination)
            await Console(
                team.run_stream(
                    task="访问 https://ekzhu.com/，访问页面中的第一个链接，然后告诉我关于该链接页面的信息。"
                )
            )
    
    
    asyncio.run(main())
    

**通过 SSE 的远程 MCP 服务示例：**
    
    
    from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools
    
    
    async def main() -> None:
        # 为远程服务设置服务器参数
        server_params = SseServerParams(url="https://api.example.com/mcp", headers={"Authorization": "Bearer token"})
    
        # 获取所有可用工具
        tools = await mcp_server_tools(server_params)
    
        # 创建一个带有所有工具的智能体
        agent = AssistantAgent(name="tool_user", model_client=OpenAIChatCompletionClient(model="gpt-4"), tools=tools)  # type: ignore
    

有关更多示例和详细用法，请参见包仓库中的 samples 目录。

_class _McpWorkbench(_server_params : Annotated[StdioServerParams | SseServerParams | StreamableHttpServerParams, FieldInfo(annotation=NoneType, required=True, discriminator='type')]_, _tool_overrides : [Dict](https://docs.python.org/3/library/typing.html#typing.Dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [ToolOverride](autogen_core.tools.html#autogen_core.tools.ToolOverride "autogen_core.tools._base.ToolOverride")] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _model_client : [ChatCompletionClient](autogen_core.models.html#autogen_core.models.ChatCompletionClient "autogen_core.models._model_client.ChatCompletionClient") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_)[[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench)#
    

Bases: [`Workbench`](autogen_core.tools.html#autogen_core.tools.Workbench "autogen_core.tools._workbench.Workbench"), [`Component`](autogen_core.html#autogen_core.Component "autogen_core._component_config.Component")[`McpWorkbenchConfig`]

一个工作台，包装 MCP 服务器并提供用于列出和调用服务器提供的工具的接口。

警告

仅连接到可信的 MCP 服务器，特别是在使用 StdioServerParams 时，因为它会在本地环境中执行命令。

此工作应用作上下文管理器，以确保正确初始化和清理底层 MCP 会话。

MCP 支持# MCP 能力 | 支持的功能  
---|---  
工具 | list_tools, call_tool  
资源 | list_resources, read_resource  
资源模板 | list_resource_templates, read_resource_template  
提示 | list_prompts, get_prompt  
采样 | 通过 model_client 可选支持  
根 | 不支持  
启发 | 不支持  
  
参数：
    

  * **server_params** (_McpServerParams_) – 连接到 MCP 服务器的参数。这可以是 `StdioServerParams` 或 `SseServerParams`。

  * **tool_overrides** (_Optional_ _[__Dict_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,_[_ToolOverride_](autogen_core.tools.html#autogen_core.tools.ToolOverride "autogen_core.tools.ToolOverride") _]__]_) – 原始工具名称到用于名称和/或描述的覆盖配置的可选映射。这允许在保持底层工具功能的同时自定义服务器工具对消费者的显示方式。

  * **model_client** – 可选的聊天补全客户端，用于处理支持采样功能的 MCP 服务器的采样请求。这允许 MCP 服务器在工具执行期间从语言模型请求文本生成。如果未提供，采样请求将返回错误。

引发：
    

[**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError "\(in Python v3.14\)") – 如果工具覆盖名称存在冲突。

示例

以下是使用 mcp-server-fetch 服务器的工作台的简单示例：
    
    
    import asyncio
    
    from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
    
    
    async def main() -> None:
        params = StdioServerParams(
            command="uvx",
            args=["mcp-server-fetch"],
            read_timeout_seconds=60,
        )
    
        # 你还可以使用 `start()` 和 `stop()` 来管理会话。
        async with McpWorkbench(server_params=params) as workbench:
            tools = await workbench.list_tools()
            print(tools)
            result = await workbench.call_tool(tools[0]["name"], {"url": "https://github.com/"})
            print(result)
    
    
    asyncio.run(main())
    

使用工具覆盖的示例：
    
    
    import asyncio
    from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
    from autogen_core.tools import ToolOverride
    
    
    async def main() -> None:
        params = StdioServerParams(
            command="uvx",
            args=["mcp-server-fetch"],
            read_timeout_seconds=60,
        )
    
        # 覆盖 fetch 工具的名称和描述
        overrides = {
            "fetch": ToolOverride(name="web_fetch", description="具有更好错误处理能力的增强型 Web 获取工具")
        }
    
        async with McpWorkbench(server_params=params, tool_overrides=overrides) as workbench:
            tools = await workbench.list_tools()
            # 该工具现在将显示为 "web_fetch" 并带有新的描述
            print(tools)
            # 调用被覆盖的工具
            result = await workbench.call_tool("web_fetch", {"url": "https://github.com/"})
            print(result)
    
    
    asyncio.run(main())
    

使用 [GitHub MCP Server](https://github.com/github/github-mcp-server) 的工作台示例：
    
    
    import asyncio
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
    
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4.1-nano")
        server_params = StdioServerParams(
            command="docker",
            args=[
                "run",
                "-i",
                "--rm",
                "-e",
                "GITHUB_PERSONAL_ACCESS_TOKEN",
                "ghcr.io/github/github-mcp-server",
            ],
            env={
                "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            },
        )
        async with McpWorkbench(server_params) as mcp:
            agent = AssistantAgent(
                "github_assistant",
                model_client=model_client,
                workbench=mcp,
                reflect_on_tool_use=True,
                model_client_stream=True,
            )
            await Console(agent.run_stream(task="是否有一个名为 Autogen 的仓库"))
    
    
    asyncio.run(main())
    

使用 [Playwright MCP Server](https://github.com/microsoft/playwright-mcp) 的工作台示例：
    
    
    # 首先运行 `npm install -g @playwright/mcp@latest` 以安装 MCP 服务器。
    import asyncio
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import TextMessageTermination
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
    
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4.1-nano")
        server_params = StdioServerParams(
            command="npx",
            args=[
                "@playwright/mcp@latest",
                "--headless",
            ],
        )
        async with McpWorkbench(server_params) as mcp:
            agent = AssistantAgent(
                "web_browsing_assistant",
                model_client=model_client,
                workbench=mcp,
                model_client_stream=True,
            )
            team = RoundRobinGroupChat(
                [agent],
                termination_condition=TextMessageTermination(source="web_browsing_assistant"),
            )
            await Console(team.run_stream(task="查找 microsoft/autogen 仓库有多少贡献者"))
    
    
    asyncio.run(main())
    

component_provider_override _: ClassVar[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")]__ = 'autogen_ext.tools.mcp.McpWorkbench'_#
    

覆盖组件的 provider 字符串。这应该用于防止内部模块名称成为模块名称的一部分。

component_config_schema#
    

alias of `McpWorkbenchConfig`

_property _server_params _: Annotated[StdioServerParams | SseServerParams | StreamableHttpServerParams, FieldInfo(annotation=NoneType, required=True, discriminator='type')]_#
    

_async _list_tools() → [List](https://docs.python.org/3/library/typing.html#typing.List "\(in Python v3.14\)")[[ToolSchema](autogen_core.tools.html#autogen_core.tools.ToolSchema "autogen_core.tools._base.ToolSchema")][[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench.list_tools)#
    

将当前可用的工具在 workbench 中列为 `ToolSchema` 对象。

工具列表可能是动态的，并且它们的内容可能在工具执行后发生变化。

_async _call_tool(_name : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _arguments : [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _call_id : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_) → [ToolResult](autogen_core.tools.html#autogen_core.tools.ToolResult "autogen_core.tools._workbench.ToolResult")[[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench.call_tool)#
    

调用 workbench 中的工具。

参数：
    

  * **name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – 要调用的工具的名称。

  * **arguments** (_Mapping_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__Any_ _]__|__None_) – 传递给工具的参数。如果为 None，将使用无参数调用工具。

  * **cancellation_token** ([_CancellationToken_](autogen_core.html#autogen_core.CancellationToken "autogen_core.CancellationToken") _|__None_) – 用于取消工具执行的可选取消令牌。

  * **call_id** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _|__None_) – 用于跟踪的工具调用的可选标识符。

返回：
    

**ToolResult** – 工具执行的结果。

_property _initialize_result _: [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")_#
    

_async _list_prompts() → ListPromptsResult[[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench.list_prompts)#
    

列出 MCP 服务器上可用的提示。

_async _list_resources() → ListResourcesResult[[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench.list_resources)#
    

列出 MCP 服务器上可用的资源。

_async _list_resource_templates() → ListResourceTemplatesResult[[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench.list_resource_templates)#
    

列出 MCP 服务器上可用的资源模板。

_async _read_resource(_uri : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → ReadResourceResult[[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench.read_resource)#
    

从 MCP 服务器读取资源。

_async _get_prompt(_name : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _arguments : [Dict](https://docs.python.org/3/library/typing.html#typing.Dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_) → GetPromptResult[[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench.get_prompt)#
    

从 MCP 服务器获取提示。

_async _start() → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench.start)#
    

启动 workbench 并初始化任何资源。

在使用 workbench 之前应调用此方法。

_async _stop() → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench.stop)#
    

停止 workbench 并释放任何资源。

当不再需要 workbench 时应调用此方法。

_async _reset() → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench.reset)#
    

将 workbench 重置为其初始化、已启动的状态。

_async _save_state() → [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")][[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench.save_state)#
    

保存 workbench 的状态。

应调用此方法以持久化 workbench 的状态。

_async _load_state(_state : [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench.load_state)#
    

加载 workbench 的状态。

参数：
    

**state** (_Mapping_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__Any_ _]_) – 要加载到 workbench 中的状态。

_to_config() → McpWorkbenchConfig[[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench._to_config)#
    

转储创建与该实例配置匹配的新组件实例所需的配置。

返回：
    

**T** – 组件的配置。

_classmethod __from_config(_config : McpWorkbenchConfig_) → [Self](https://docs.python.org/3/library/typing.html#typing.Self "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/tools/mcp/_workbench.html#McpWorkbench._from_config)#
    

从配置对象创建组件的新实例。

参数：
    

**config** (_T_) – 配置对象。

返回：
    

**Self** – 组件的新实例。

__本页内容

[ __在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/reference/python/autogen_ext.tools.mcp.rst)

[ __查看源文件](../../_sources/reference/python/autogen_ext.tools.mcp.rst.txt)