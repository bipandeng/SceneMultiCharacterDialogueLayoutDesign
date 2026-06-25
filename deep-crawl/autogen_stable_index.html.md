<!-- 来源: https://microsoft.github.io/autogen/stable/index.html -->

# AutoGen#

#  AutoGen 

###  一个用于构建 AI 智能体和应用程序的框架 

Studio [![PyPi autogenstudio](https://img.shields.io/badge/PyPi-autogenstudio-blue?logo=pypi)](https://pypi.org/project/autogenstudio/)

一个基于 Web 的 UI，无需编写代码即可使用智能体进行原型设计。基于 AgentChat 构建。
    
    
    pip install -U autogenstudio
    autogenstudio ui --port 8080 --appdir ./myapp
    

_如果你是 AutoGen 新手，并且想要在不使用代码的情况下使用智能体进行原型设计，请从这里开始。_

[开始使用](user-guide/autogenstudio-user-guide/index.html)

AgentChat [![PyPi autogen-agentchat](https://img.shields.io/badge/PyPi-autogen--agentchat-blue?logo=pypi)](https://pypi.org/project/autogen-agentchat/)

一个用于构建对话式单智能体和多智能体应用程序的编程框架。基于 Core 构建。需要 Python 3.10+。 
    
    
    # pip install -U "autogen-agentchat" "autogen-ext[openai]"
    import asyncio
    from autogen_agentchat.agents import AssistantAgent
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    async def main() -> None:
        agent = AssistantAgent("assistant", OpenAIChatCompletionClient(model="gpt-4o"))
        print(await agent.run(task="Say 'Hello World!'"))
    
    asyncio.run(main())
    

_如果你正在使用 Python 对智能体进行原型设计，请从这里开始。[从 AutoGen 0.2 迁移？](user-guide/agentchat-user-guide/migration-guide.html)。_

[开始使用](user-guide/agentchat-user-guide/quickstart.html)

Core [![PyPi autogen-core](https://img.shields.io/badge/PyPi-autogen--core-blue?logo=pypi)](https://pypi.org/project/autogen-core/)

一个事件驱动的编程框架，用于构建可扩展的多智能体 AI 系统。示例场景：

  * 用于业务流程的确定性和动态智能体工作流。

  * 多智能体协作研究。

  * 用于多语言应用程序的分布式智能体。

_如果你正在认真构建多智能体系统，请从这里开始。_

[开始使用](user-guide/core-user-guide/quickstart.html)

Extensions [![PyPi autogen-ext](https://img.shields.io/badge/PyPi-autogen--ext-blue?logo=pypi)](https://pypi.org/project/autogen-ext/)

Core 和 AgentChat 组件的实现，可与外部服务或其他库对接。你可以查找并使用社区扩展或创建自己的扩展。内置扩展示例：

  * [`McpWorkbench`](reference/python/autogen_ext.tools.mcp.html#autogen_ext.tools.mcp.McpWorkbench "autogen_ext.tools.mcp.McpWorkbench") 用于使用模型上下文协议 (MCP) 服务器。

  * [`OpenAIAssistantAgent`](reference/python/autogen_ext.agents.openai.html#autogen_ext.agents.openai.OpenAIAssistantAgent "autogen_ext.agents.openai.OpenAIAssistantAgent") 用于使用 Assistant API。

  * [`DockerCommandLineCodeExecutor`](reference/python/autogen_ext.code_executors.docker.html#autogen_ext.code_executors.docker.DockerCommandLineCodeExecutor "autogen_ext.code_executors.docker.DockerCommandLineCodeExecutor") 用于在 Docker 容器中运行模型生成的代码。

  * [`GrpcWorkerAgentRuntime`](reference/python/autogen_ext.runtimes.grpc.html#autogen_ext.runtimes.grpc.GrpcWorkerAgentRuntime "autogen_ext.runtimes.grpc.GrpcWorkerAgentRuntime") 用于分布式智能体。

[发现社区扩展](user-guide/extensions-user-guide/discover.html) [创建新扩展](user-guide/extensions-user-guide/create-your-own.html)