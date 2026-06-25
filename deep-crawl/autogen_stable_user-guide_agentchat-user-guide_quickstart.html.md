<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html -->

# Quickstart#

通过 AgentChat，你可以使用预定义的代理快速构建应用程序。为了说明这一点，我们将从一个可以工具的单一代理开始。

首先，我们需要安装 AgentChat 和扩展包。
    
    
    pip install -U "autogen-agentchat" "autogen-ext[openai,azure]"
    

此示例使用 OpenAI 模型，但也可以使用其他模型。只需使用所需的模型或模型客户端类更新 `model_client` 即可。

要使用 Azure OpenAI 模型和 AAD 身份验证，你可以按照 [此处](tutorial/models.html#azure-openai) 的说明进行操作。要使用其他模型，请参阅 [Models](tutorial/models.html)。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    # Define a model client. You can use other model client that implements
    # the `ChatCompletionClient` interface.
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        # api_key="YOUR_API_KEY",
    )
    
    
    # Define a simple function tool that the agent can use.
    # For this example, we use a fake weather tool for demonstration purposes.
    async def get_weather(city: str) -> str:
        """Get the weather for a given city."""
        return f"The weather in {city} is 73 degrees and Sunny."
    
    
    # Define an AssistantAgent with the model, tool, system message, and reflection enabled.
    # The system message instructs the agent via natural language.
    agent = AssistantAgent(
        name="weather_agent",
        model_client=model_client,
        tools=[get_weather],
        system_message="You are a helpful assistant.",
        reflect_on_tool_use=True,
        model_client_stream=True,  # Enable streaming tokens from the model client.
    )
    
    
    # Run the agent and stream the messages to the console.
    async def main() -> None:
        await Console(agent.run_stream(task="What is the weather in New York?"))
        # Close the connection to the model client.
        await model_client.close()
    
    
    # NOTE: if running this inside a Python script you'll need to use asyncio.run(main()).
    await main()
    
    
    
    ---------- user ----------
    What is the weather in New York?
    ---------- weather_agent ----------
    [FunctionCall(id='call_bE5CYAwB7OlOdNAyPjwOkej1', arguments='{"city":"New York"}', name='get_weather')]
    ---------- weather_agent ----------
    [FunctionExecutionResult(content='The weather in New York is 73 degrees and Sunny.', call_id='call_bE5CYAwB7OlOdNAyPjwOkej1', is_error=False)]
    ---------- weather_agent ----------
    The current weather in New York is 73 degrees and sunny.
    

## What's Next?#

现在你已经对如何使用单一代理有了基本的了解，请考虑遵循 [tutorial](tutorial/index.html) 来了解 AgentChat 其他功能的演练。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/quickstart.ipynb)

[ __Show Source](../../_sources/user-guide/agentchat-user-guide/quickstart.ipynb.txt)