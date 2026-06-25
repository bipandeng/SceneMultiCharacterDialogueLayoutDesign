[跳过主要内容](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html#main-content)

回到顶部`Ctrl` + `K`

浅色深色系统设置

- [GitHub](https://github.com/microsoft/autogen)
- [Discord](https://aka.ms/autogen-discord)
- [Twitter](https://twitter.com/pyautogen)

# 快速入门 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html\#quickstart "链接到此标题")

通过 AgentChat，你可以使用预设代理快速构建应用程序。
为了说明这一点，我们首先创建一个可以使用工具的单个代理。

首先，我们需要安装 AgentChat 和扩展包。

```
pip install -U "autogen-agentchat" "autogen-ext[openai,azure]"
```

复制到剪贴板

此示例使用 OpenAI 模型，但是，你也可以使用其他模型。
只需使用所需的模型或模型客户端类更新 `model_client`。

要使用 Azure OpenAI 模型和 AAD 身份验证，
你可以按照[此处](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/models.html#azure-openai)的说明进行操作。
要使用其他模型，请参阅[模型](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/models.html)。

```
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 定义一个模型客户端。你可以使用其他实现了
# `ChatCompletionClient` 接口的模型客户端。
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    # api_key="YOUR_API_KEY",
)

# 定义一个简单的函数工具供代理使用。
# 在此示例中，我们使用一个模拟的天气工具进行演示。
async def get_weather(city: str) -> str:
    """获取给定城市的天气。"""
    return f"The weather in {city} is 73 degrees and Sunny."

# 定义一个 AssistantAgent，包含模型、工具、系统消息，并启用反思功能。
# 系统消息通过自然语言指导代理。
agent = AssistantAgent(
    name="weather_agent",
    model_client=model_client,
    tools=[get_weather],
    system_message="You are a helpful assistant.",
    reflect_on_tool_use=True,
    model_client_stream=True,  # 启用从模型客户端流式传输令牌。
)

# 运行代理并将消息流式输出到控制台。
async def main() -> None:
    await Console(agent.run_stream(task="What is the weather in New York?"))
    # 关闭与模型客户端的连接。
    await model_client.close()

# 注意：如果在 Python 脚本中运行此代码，你需要使用 asyncio.run(main())。
await main()
```

复制到剪贴板

```
---------- user ----------
What is the weather in New York?
---------- weather_agent ----------
[FunctionCall(id='call_bE5CYAwB7OlOdNAyPjwOkej1', arguments='{"city":"New York"}', name='get_weather')]
---------- weather_agent ----------
[FunctionExecutionResult(content='The weather in New York is 73 degrees and Sunny.', call_id='call_bE5CYAwB7OlOdNAyPjwOkej1', is_error=False)]
---------- weather_agent ----------
The current weather in New York is 73 degrees and sunny.
```

复制到剪贴板

## 接下来是什么？ [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html\#what-s-next "链接到此标题")

现在你已经对如何使用单个代理有了基本了解，请考虑跟随[教程](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/index.html)来逐步了解 AgentChat 的其他功能。

在此页面上


[在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/quickstart.ipynb)

[显示源代码](https://microsoft.github.io/autogen/stable/_sources/user-guide/agentchat-user-guide/quickstart.ipynb.txt)
