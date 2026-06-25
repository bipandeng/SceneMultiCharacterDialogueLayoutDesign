from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 定义一个模型客户端。你可以使用其他实现了 `ChatCompletionClient` 接口的模型客户端。
model_client = OpenAIChatCompletionClient(
    base_url="https://api.minimaxi.com/v1",
    model="MiniMax-M3",
    api_key="sk-cp-2G0ldj2nR8RU0tkjdyGYbxNyx-smYuBPsz3pTbz5k_WD8Xur0Li1dYUBPNQmP1G7mfgIJkY91jPHXpFA7DqlwoqUeeTcOtB3ndK_CYhuI5QroXXaG5Qfz7Q",
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": "unknown",
        "structured_output": True,
        "multiple_system_messages": True,
    },
)


# 定义一个简单的函数工具供智能体使用。
# 在这个示例中，我们使用一个模拟的天气工具用于演示。
async def get_weather(city: str) -> str:
    """获取指定城市的天气。"""
    return f"The weather in {city} is 73 degrees and Sunny."


# 定义一个 AssistantAgent，配置模型、工具、系统消息，并启用反思功能。
# 系统消息通过自然语言对智能体进行指导。
agent = AssistantAgent(
    name="weather_agent",
    model_client=model_client,
    tools=[get_weather],
    system_message="You are a helpful assistant.",
    reflect_on_tool_use=True,
    model_client_stream=True,  # 启用从模型客户端流式传输 token。
)


# 运行智能体并将消息流式输出到控制台。
async def main() -> None:
    await Console(agent.run_stream(task="What is the weather in New York?"))
    # 关闭与模型客户端的连接。
    await model_client.close()


# 注意：如果在 Python 脚本中运行，需要使用 asyncio.run(main())。
import asyncio
asyncio.run(main())
