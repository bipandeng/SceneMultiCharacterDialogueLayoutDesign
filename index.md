# AutoGen

## 构建 AI 智能体和应用的框架

---

## 组件概览

### Studio（工作室）

[![PyPi autogenstudio](https://img.shields.io/badge/PyPi-autogenstudio-blue?logo=pypi)](https://pypi.org/project/autogenstudio/)

一个基于 Web 的 UI，无需编写代码即可使用智能体进行原型设计。
基于 AgentChat 构建。

```bash
pip install -U autogenstudio
autogenstudio ui --port 8080 --appdir ./myapp
```

*如果你是 AutoGen 新手，想要无需编写代码即可进行智能体原型设计，从这里开始。*

[开始使用](https://microsoft.github.io/autogen/stable/user-guide/autogenstudio-user-guide/index.html)

---

### AgentChat（智能体聊天）

[![PyPi autogen-agentchat](https://img.shimgields.io/badge/PyPi-autogen--agentchat-blue?logo=pypi)](https://pypi.org/project/autogen-agentchat/)

一个用于构建对话式单智能体和多智能体应用的编程框架。
基于 Core 构建。需要 Python 3.10+。

```python
# pip install -U "autogen-agentchat" "autogen-ext[openai]"
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    agent = AssistantAgent("assistant", OpenAIChatCompletionClient(model="gpt-4o"))
    print(await agent.run(task="Say 'Hello World!'"))

asyncio.run(main())
```

*如果你使用 Python 进行智能体原型设计，从这里开始。[从 AutoGen 0.2 迁移？](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/migration-guide.html)*

[开始使用](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html)

---

### Core（核心）

[![PyPi autogen-core](https://img.shields.io/badge/PyPi-autogen--core-blue?logo=pypi)](https://pypi.org/project/autogen-core/)

一个事件驱动的编程框架，用于构建可扩展的多智能体 AI 系统。示例场景：

- 业务流程的确定性和动态智能体工作流
- 多智能体协作研究
- 多语言应用的分布式智能体

*如果你认真要构建多智能体系统，从这里开始。*

[开始使用](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/quickstart.html)

---

### Extensions（扩展）

[![PyPi autogen-ext](https://img.shields.io/badge/PyPi-autogen--ext-blue?logo=pypi)](https://pypi.org/project/autogen-ext/)

Core 和 AgentChat 组件的实现，用于与外部服务或其他库交互。
你可以找到并使用社区扩展，或创建自己的扩展。内置扩展示例：

- [`McpWorkbench`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.tools.mcp.html#autogen_ext.tools.mcp.McpWorkbench) - 用于使用模型上下文协议（MCP）服务器
- [`OpenAIAssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.agents.openai.html#autogen_ext.agents.openai.OpenAIAssistantAgent) - 用于使用 Assistant API
- [`DockerCommandLineCodeExecutor`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.code_executors.docker.html#autogen_ext.code_executors.docker.DockerCommandLineCodeExecutor) - 用于在 Docker 容器中运行模型生成的代码
- [`GrpcWorkerAgentRuntime`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.runtimes.grpc.html#autogen_ext.runtimes.grpc.GrpcWorkerAgentRuntime) - 用于分布式智能体

[发现社区扩展](https://microsoft.github.io/autogen/stable/user-guide/extensions-user-guide/discover.html) | [创建新扩展](https://microsoft.github.io/autogen/stable/user-guide/extensions-user-guide/create-your-own.html)

---

## 学习路径建议

| 你的目标 | 推荐起点 |
|---------|---------|
| 不想写代码，想用 UI 原型设计 | **Studio** |
| 用 Python 快速构建智能体应用 | **AgentChat** |
| 构建复杂的多智能体系统 | **Core** |
| 需要连接外部服务或自定义功能 | **Extensions** |

---

## 相关链接

- [GitHub 仓库](https://github.com/microsoft/autogen)
- [Discord 社区](https://aka.ms/autogen-discord)
- [Twitter](https://twitter.com/pyautogen)
