import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 创建一个模型客户端（使用 MiniMax）
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

# 创建主智能体
primary_agent = AssistantAgent(
    "primary",
    model_client=model_client,
    system_message="You are a helpful AI assistant.",
)

# 创建评论智能体
critic_agent = AssistantAgent(
    "critic",
    model_client=model_client,
    system_message="Provide constructive feedback. Respond with 'APPROVE' to when your feedbacks are addressed.",
)

# 定义终止条件：当评论智能体回复 "APPROVE" 时停止任务
text_termination = TextMentionTermination("APPROVE")

# 创建一个团队，包含主智能体和评论智能体
team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=text_termination)


async def main():
    # 特点：阻塞等待，直到任务完成才返回完整结果。
    # result = await team.run(task="...")
    # print(result)  # 等所有智能体执行完毕，一次性返回最终结果


    # 特点：实时流式输出，每产生一条消息就立即处理。
    # await team.reset()  # 重置团队状态，准备执行新任务
    # async for message in team.run_stream(task="Write a short poem about the fall season."): # ② 异步迭代消息流
    #     if isinstance(message, TaskResult): # ③ 判断消息类型
    #         print("Stop Reason:", message.stop_reason)
    #     else:
    #         print(message)
    await Console(team.run_stream(task="将这首诗用中文唐诗风格写一遍。"))

asyncio.run(main())

