[跳到主要内容](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html#main-content)

回到顶部`Ctrl` + `K`

浅色深色系统设置

- [GitHub](https://github.com/microsoft/autogen)
- [Discord](https://aka.ms/autogen-discord)
- [Twitter](https://twitter.com/pyautogen)

# 集群 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html\#swarm "链接到此标题")

[`Swarm`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm") 实现了一个团队，其中代理可以基于其能力将任务移交给其他代理。
这是一种多代理设计模式，最初由 OpenAI 在
[Swarm](https://github.com/openai/swarm) 中引入。
核心思想是让代理使用特殊的工具调用来委托任务给其他代理，同时
所有代理共享相同的消息上下文。
这使得代理能够对任务规划做出局部决策，而不是
依赖中央协调器，如 [`SelectorGroupChat`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 中那样。

注意

[`Swarm`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm") 是一个高级 API。如果你需要更多
不受此 API 支持的控制和自定义，你可以查看
核心 API 文档中的[移交模式](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/handoffs.html)
并实现你自己的 Swarm 模式版本。

## 工作原理 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html\#how-does-it-work "链接到此标题")

在其核心，[`Swarm`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm") 团队是一个群组聊天，
代理轮流生成响应。
与 [`SelectorGroupChat`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat")
和 [`RoundRobinGroupChat`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 类似，参与代理
广播他们的响应，以便所有代理共享相同的消息上下文。

与其他两个群组聊天团队不同，在每一轮中，
**发言代理是基于上下文中最近的**
**[`HandoffMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage") 消息选择的。**
这自然要求团队中的每个代理都能够生成
[`HandoffMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage") 以信号通知
它将移交给哪些其他代理。

对于 [`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent")，你可以设置
`handoffs` 参数来指定它可以移交给哪些代理。你可以
使用 [`Handoff`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.Handoff "autogen_agentchat.base.Handoff") 来自定义消息
内容和移交行为。

整体过程可以概括如下：

1. 每个代理都有能力生成 [`HandoffMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage")
以信号通知它可以移交给哪些其他代理。对于 [`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent")，这意味着设置 `handoffs` 参数。

2. 当团队开始处理任务时，第一批发言代理执行任务并就移交和移交给谁做出局部决策。

3. 当代理生成 [`HandoffMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage") 时，接收代理使用相同的消息上下文接管任务。

4. 该过程持续进行，直到满足终止条件。


注意

[`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 使用模型的
工具调用功能来生成移交。这意味着模型必须
支持工具调用。如果模型支持并行工具调用，则可能
同时生成多个移交。这可能导致意外行为。
为避免这种情况，你可以通过配置模型客户端来禁用并行工具调用。对于 [`OpenAIChatCompletionClient`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.OpenAIChatCompletionClient "autogen_ext.models.openai.OpenAIChatCompletionClient")
和 [`AzureOpenAIChatCompletionClient`](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.AzureOpenAIChatCompletionClient "autogen_ext.models.openai.AzureOpenAIChatCompletionClient")，
你可以在配置中设置 `parallel_tool_calls=False`。

在本节中，我们将向你展示两个如何使用 [`Swarm`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm") 团队的示例：

1. 带有人工环内移交的客户支持团队。

2. 用于内容生成的自主团队。


## 客户支持示例 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html\#customer-support-example "链接到此标题")

![客户支持](https://microsoft.github.io/autogen/stable/_images/swarm_customer_support.svg)

此系统实现了航班退款场景，包含两个代理：

- **旅行代理**：处理一般旅行协调和退款事宜。

- **航班退款代理**：专门使用 `refund_flight` 工具处理航班退款。


此外，我们让用户能够与代理交互，当代理移交给 `"user"` 时。

### 工作流程 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html\#workflow "链接到此标题")

1. **旅行代理**发起对话并评估用户的请求。

2. 基于请求：

   - 对于退款相关任务，旅行代理移交给**航班退款代理**。

   - 对于需要从客户获取的信息，任一代理都可以移交给 `"user"`。
3. **航班退款代理**在适当时使用 `refund_flight` 工具处理退款。

4. 如果代理移交给 `"user"`，团队执行将停止并等待用户输入响应。

5. 当用户提供输入时，它作为 [`HandoffMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage") 发送回团队。此消息定向到最初请求用户输入的代理。

6. 该过程持续进行，直到旅行代理确定任务完成并终止工作流。


```
from typing import Any, Dict, List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
```

复制到剪贴板

### 工具 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html\#tools "链接到此标题")

```
def refund_flight(flight_id: str) -> str:
    """Refund a flight"""
    return f"Flight {flight_id} refunded"
```

复制到剪贴板

### 代理 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html\#agents "链接到此标题")

```
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    # api_key="YOUR_API_KEY",
)

travel_agent = AssistantAgent(
    "travel_agent",
    model_client=model_client,
    handoffs=["flights_refunder", "user"],
    system_message="""You are a travel agent.
    The flights_refunder is in charge of refunding flights.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    Use TERMINATE when the travel planning is complete.""",
)

flights_refunder = AssistantAgent(
    "flights_refunder",
    model_client=model_client,
    handoffs=["travel_agent", "user"],
    tools=[refund_flight],
    system_message="""You are an agent specialized in refunding flights.
    You only need flight reference numbers to refund a flight.
    You have the ability to refund a flight using the refund_flight tool.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    When the transaction is complete, handoff to the travel agent to finalize.""",
)
```

复制到剪贴板

```
termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")
team = Swarm([travel_agent, flights_refunder], termination_condition=termination)
```

复制到剪贴板

```
task = "I need to refund my flight."

async def run_team_stream() -> None:
    task_result = await Console(team.run_stream(task=task))
    last_message = task_result.messages[-1]

    while isinstance(last_message, HandoffMessage) and last_message.target == "user":
        user_message = input("User: ")

        task_result = await Console(
            team.run_stream(task=HandoffMessage(source="user", target=last_message.source, content=user_message))
        )
        last_message = task_result.messages[-1]

# 如果在脚本中运行，请使用 asyncio.run(...)。
await run_team_stream()
await model_client.close()
```

复制到剪贴板

```
---------- user ----------
I need to refund my flight.
---------- travel_agent ----------
[FunctionCall(id='call_ZQ2rGjq4Z29pd0yP2sNcuyd2', arguments='{}', name='transfer_to_flights_refunder')]
[Prompt tokens: 119, Completion tokens: 14]
---------- travel_agent ----------
[FunctionExecutionResult(content='Transferred to flights_refunder, adopting the role of flights_refunder immediately.', call_id='call_ZQ2rGjq4Z29pd0yP2sNcuyd2')]
---------- travel_agent ----------
Transferred to flights_refunder, adopting the role of flights_refunder immediately.
---------- flights_refunder ----------
Could you please provide me with the flight reference number so I can process the refund for you?
[Prompt tokens: 191, Completion tokens: 20]
---------- flights_refunder ----------
[FunctionCall(id='call_1iRfzNpxTJhRTW2ww9aQJ8sK', arguments='{}', name='transfer_to_user')]
[Prompt tokens: 219, Completion tokens: 11]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Transferred to user, adopting the role of user immediately.', call_id='call_1iRfzNpxTJhRTW2ww9aQJ8sK')]
---------- flights_refunder ----------
Transferred to user, adopting the role of user immediately.
---------- Summary ----------
Number of messages: 8
Finish reason: Handoff to user from flights_refunder detected.
Total prompt tokens: 529
Total completion tokens: 45
Duration: 2.05 seconds
---------- user ----------
Sure, it's 507811
---------- flights_refunder ----------
[FunctionCall(id='call_UKCsoEBdflkvpuT9Bi2xlvTd', arguments='{"flight_id":"507811"}', name='refund_flight')]
[Prompt tokens: 266, Completion tokens: 18]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Flight 507811 refunded', call_id='call_UKCsoEBdflkvpuT9Bi2xlvTd')]
---------- flights_refunder ----------
Tool calls:
refund_flight({"flight_id":"507811"}) = Flight 507811 refunded
---------- flights_refunder ----------
[FunctionCall(id='call_MQ2CXR8UhVtjNc6jG3wSQp2W', arguments='{}', name='transfer_to_travel_agent')]
[Prompt tokens: 303, Completion tokens: 13]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Transferred to travel_agent, adopting the role of travel_agent immediately.', call_id='call_MQ2CXR8UhVtjNc6jG3wSQp2W')]
---------- flights_refunder ----------
Transferred to travel_agent, adopting the role of travel_agent immediately.
---------- travel_agent ----------
Your flight with reference number 507811 has been successfully refunded. If you need anything else, feel free to let me know. Safe travels! TERMINATE
[Prompt tokens: 272, Completion tokens: 32]
---------- Summary ----------
Number of messages: 8
Finish reason: Text 'TERMINATE' mentioned
Total prompt tokens: 841
Total completion tokens: 63
Duration: 1.64 seconds
```

复制到剪贴板

## 股票研究示例 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html\#stock-research-example "链接到此标题")

![股票研究](https://microsoft.github.io/autogen/stable/_images/swarm_stock_research.svg)

此系统旨在通过利用四个代理来执行股票研究任务：

- **规划者**：中央协调员，根据专业知识将特定任务委托给专门的代理。规划者确保每个代理得到有效利用，并监督整体工作流程。

- **财务分析师**：专门负责分析财务指标和股票数据的代理，使用诸如 `get_stock_data` 等工具。

- **新闻分析师**：专注于收集和使用诸如 `get_news` 等工具总结相关新闻文章的代理。

- **作家**：负责将股票和新闻分析的结果汇编成一份连贯的最终报告的代理。


### 工作流程 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html\#id1 "链接到此标题")

1. **规划者**以逐步方式将任务委派给适当的代理，从而启动研究过程。

2. 每个代理独立执行其任务，并将其工作附加到共享的**消息线程/历史**中。代理不是直接将结果返回给规划者，而是都贡献并从共享消息历史中读取。当代理使用 LLM 生成其工作时，他们可以访问此共享消息历史，这提供了上下文并有助于跟踪任务的整体进度。

3. 当代理完成任务时，它将控制权交还给规划者。

4. 该过程持续进行，直到规划者确定所有必要任务已完成并决定终止工作流。


### 工具 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html\#id2 "链接到此标题")

```
async def get_stock_data(symbol: str) -> Dict[str, Any]:
    """Get stock market data for a given symbol"""
    return {"price": 180.25, "volume": 1000000, "pe_ratio": 65.4, "market_cap": "700B"}

async def get_news(query: str) -> List[Dict[str, str]]:
    """Get recent news articles about a company"""
    return [\
        {\
            "title": "Tesla Expands Cybertruck Production",\
            "date": "2024-03-20",\
            "summary": "Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.",\
        },\
        {\
            "title": "Tesla FSD Beta Shows Promise",\
            "date": "2024-03-19",\
            "summary": "Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.",\
        },\
        {\
            "title": "Model Y Dominates Global EV Sales",\
            "date": "2024-03-18",\
            "summary": "Tesla's Model Y becomes best-selling electric vehicle worldwide, capturing significant market share.",\
        },\
    ]
```

复制到剪贴板

```
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    # api_key="YOUR_API_KEY",
)

planner = AssistantAgent(
    "planner",
    model_client=model_client,
    handoffs=["financial_analyst", "news_analyst", "writer"],
    system_message="""You are a research planning coordinator.
    Coordinate market research by delegating to specialized agents:
    - Financial Analyst: For stock data analysis
    - News Analyst: For news gathering and analysis
    - Writer: For compiling final report
    Always send your plan first, then handoff to appropriate agent.
    Always handoff to a single agent at a time.
    Use TERMINATE when research is complete.""",
)

financial_analyst = AssistantAgent(
    "financial_analyst",
    model_client=model_client,
    handoffs=["planner"],
    tools=[get_stock_data],
    system_message="""You are a financial analyst.
    Analyze stock market data using the get_stock_data tool.
    Provide insights on financial metrics.
    Always handoff back to planner when analysis is complete.""",
)

news_analyst = AssistantAgent(
    "news_analyst",
    model_client=model_client,
    handoffs=["planner"],
    tools=[get_news],
    system_message="""You are a news analyst.
    Gather and analyze relevant news using the get_news tool.
    Summarize key market insights from news.
    Always handoff back to planner when analysis is complete.""",
)

writer = AssistantAgent(
    "writer",
    model_client=model_client,
    handoffs=["planner"],
    system_message="""You are a financial report writer.
    Compile research findings into clear, concise reports.
    Always handoff back to planner when writing is complete.""",
)
```

复制到剪贴板

```
# 定义终止条件
text_termination = TextMentionTermination("TERMINATE")
termination = text_termination

research_team = Swarm(
    participants=[planner, financial_analyst, news_analyst, writer], termination_condition=termination
)

task = "Conduct market research for TSLA stock"
await Console(research_team.run_stream(task=task))
await model_client.close()
```

复制到剪贴板

```
---------- user ----------
Conduct market research for TSLA stock
---------- planner ----------
[FunctionCall(id='call_BX5QaRuhmB8CxTsBlqCUIXPb', arguments='{}', name='transfer_to_financial_analyst')]
[Prompt tokens: 169, Completion tokens: 166]
---------- planner ----------
[FunctionExecutionResult(content='Transferred to financial_analyst, adopting the role of financial_analyst immediately.', call_id='call_BX5QaRuhmB8CxTsBlqCUIXPb')]
---------- planner ----------
Transferred to financial_analyst, adopting the role of financial_analyst immediately.
---------- financial_analyst ----------
[FunctionCall(id='call_SAXy1ebtA9mnaZo4ztpD2xHA', arguments='{"symbol":"TSLA"}', name='get_stock_data')]
[Prompt tokens: 136, Completion tokens: 16]
---------- financial_analyst ----------
[FunctionExecutionResult(content="{'price': 180.25, 'volume': 1000000, 'pe_ratio': 65.4, 'market_cap': '700B'}", call_id='call_SAXy1ebtA9mnaZo4ztpD2xHA')]
---------- financial_analyst ----------
Tool calls:
get_stock_data({"symbol":"TSLA"}) = {'price': 180.25, 'volume': 1000000, 'pe_ratio': 65.4, 'market_cap': '700B'}
---------- financial_analyst ----------
[FunctionCall(id='call_IsdcFUfBVmtcVzfSuwQpeAwl', arguments='{}', name='transfer_to_planner')]
[Prompt tokens: 199, Completion tokens: 337]
---------- financial_analyst ----------
[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_IsdcFUfBVmtcVzfSuwQpeAwl')]
---------- financial_analyst ----------
Transferred to planner, adopting the role of planner immediately.
---------- planner ----------
[FunctionCall(id='call_tN5goNFahrdcSfKnQqT0RONN', arguments='{}', name='transfer_to_news_analyst')]
[Prompt tokens: 291, Completion tokens: 14]
---------- planner ----------
[FunctionExecutionResult(content='Transferred to news_analyst, adopting the role of news_analyst immediately.', call_id='call_tN5goNFahrdcSfKnQqT0RONN')]
---------- planner ----------
Transferred to news_analyst, adopting the role of news_analyst immediately.
---------- news_analyst ----------
[FunctionCall(id='call_Owjw6ZbiPdJgNWMHWxhCKgsp', arguments='{"query":"Tesla market news"}', name='get_news')]
[Prompt tokens: 235, Completion tokens: 16]
---------- news_analyst ----------
[FunctionExecutionResult(content='[{\'title\': \'Tesla Expands Cybertruck Production\', \'date\': \'2024-03-20\', \'summary\': \'Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.\'}, {\'title\': \'Tesla FSD Beta Shows Promise\', \'date\': \'2024-03-19\', \'summary\': \'Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.\'}, {\'title\': \'Model Y Dominates Global EV Sales\', \'date\': \'2024-03-18\', \'summary\': "Tesla\'s Model Y becomes best-selling electric vehicle worldwide, capturing significant market share."}]', call_id='call_Owjw6ZbiPdJgNWMHWxhCKgsp')]
---------- news_analyst ----------
Tool calls:
get_news({"query":"Tesla market news"}) = [{'title': 'Tesla Expands Cybertruck Production', 'date': '2024-03-20', 'summary': 'Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.'}, {'title': 'Tesla FSD Beta Shows Promise', 'date': '2024-03-19', 'summary': 'Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.'}, {'title': 'Model Y Dominates Global EV Sales', 'date': '2024-03-18', 'summary': "Tesla's Model Y becomes best-selling electric vehicle worldwide, capturing significant market share."}]
---------- news_analyst ----------
Here are some of the key market insights regarding Tesla (TSLA):

1. **Expansion in Cybertruck Production**: Tesla has increased its Cybertruck production capacity at the Gigafactory in Texas to meet the high demand. This move might positively impact Tesla's revenues if the demand for the Cybertruck continues to grow.

2. **Advancements in Full Self-Driving (FSD) Technology**: The recent beta release of Tesla's Full Self-Driving software shows significant advancements, particularly in urban navigation and safety. Progress in this area could enhance Tesla's competitive edge in the autonomous driving sector.

3. **Dominance of Model Y in EV Sales**: Tesla's Model Y has become the best-selling electric vehicle globally, capturing a substantial market share. Such strong sales performance reinforces Tesla's leadership in the electric vehicle market.

These developments reflect Tesla's ongoing innovation and ability to capture market demand, which could positively influence its stock performance and market position.

I will now hand off back to the planner.
[Prompt tokens: 398, Completion tokens: 203]
---------- news_analyst ----------
[FunctionCall(id='call_pn7y6PKsBspWA17uOh3AKNMT', arguments='{}', name='transfer_to_planner')]
[Prompt tokens: 609, Completion tokens: 12]
---------- news_analyst ----------
[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_pn7y6PKsBspWA17uOh3AKNMT')]
---------- news_analyst ----------
Transferred to planner, adopting the role of planner immediately.
---------- planner ----------
[FunctionCall(id='call_MmXyWuD2uJT64ZdVI5NfhYdX', arguments='{}', name='transfer_to_writer')]
[Prompt tokens: 722, Completion tokens: 11]
---------- planner ----------
[FunctionExecutionResult(content='Transferred to writer, adopting the role of writer immediately.', call_id='call_MmXyWuD2uJT64ZdVI5NfhYdX')]
---------- planner ----------
Transferred to writer, adopting the role of writer immediately.
---------- writer ----------
[FunctionCall(id='call_Pdgu39O6GMYplBiB8jp3uyN3', arguments='{}', name='transfer_to_planner')]
[Prompt tokens: 599, Completion tokens: 323]
---------- writer ----------
[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_Pdgu39O6GMYplBiB8jp3uyN3')]
---------- writer ----------
Transferred to planner, adopting the role of planner immediately.
---------- planner ----------
TERMINATE
[Prompt tokens: 772, Completion tokens: 4]
---------- Summary ----------
Number of messages: 27
Finish reason: Text 'TERMINATE' mentioned
Total prompt tokens: 4130
Total completion tokens: 1102
Duration: 17.74 seconds
```

复制到剪贴板

```
TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Conduct market research for TSLA stock', type='TextMessage'), ToolCallRequestEvent(source='planner', models_usage=RequestUsage(prompt_tokens=169, completion_tokens=166), content=[FunctionCall(id='call_BX5QaRuhmB8CxTsBlqCUIXPb', arguments='{}', name='transfer_to_financial_analyst')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='planner', models_usage=None, content=[FunctionExecutionResult(content='Transferred to financial_analyst, adopting the role of financial_analyst immediately.', call_id='call_BX5QaRuhmB8CxTsBlqCUIXPb')], type='ToolCallExecutionEvent'), HandoffMessage(source='planner', models_usage=None, target='financial_analyst', content='Transferred to financial_analyst, adopting the role of financial_analyst immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='financial_analyst', models_usage=RequestUsage(prompt_tokens=136, completion_tokens=16), content=[FunctionCall(id='call_SAXy1ebtA9mnaZo4ztpD2xHA', arguments='{"symbol":"TSLA"}', name='get_stock_data')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='financial_analyst', models_usage=None, content=[FunctionExecutionResult(content="{'price': 180.25, 'volume': 1000000, 'pe_ratio': 65.4, 'market_cap': '700B'}", call_id='call_SAXy1ebtA9mnaZo4ztpD2xHA')], type='ToolCallExecutionEvent'), TextMessage(source='financial_analyst', models_usage=None, content='Tool calls:\nget_stock_data({"symbol":"TSLA"}) = {\'price\': 180.25, \'volume\': 1000000, \'pe_ratio\': 65.4, \'market_cap\': \'700B\'}', type='TextMessage'), ToolCallRequestEvent(source='financial_analyst', models_usage=RequestUsage(prompt_tokens=199, completion_tokens=337), content=[FunctionCall(id='call_IsdcFUfBVmtcVzfSuwQpeAwl', arguments='{}', name='transfer_to_planner')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='financial_analyst', models_usage=None, content=[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_IsdcFUfBVmtcVzfSuwQpeAwl')], type='ToolCallExecutionEvent'), HandoffMessage(source='financial_analyst', models_usage=None, target='planner', content='Transferred to planner, adopting the role of planner immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='planner', models_usage=RequestUsage(prompt_tokens=291, completion_tokens=14), content=[FunctionCall(id='call_tN5goNFahrdcSfKnQqT0RONN', arguments='{}', name='transfer_to_news_analyst')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='planner', models_usage=None, content=[FunctionExecutionResult(content='Transferred to news_analyst, adopting the role of news_analyst immediately.', call_id='call_tN5goNFahrdcSfKnQqT0RONN')], type='ToolCallExecutionEvent'), HandoffMessage(source='planner', models_usage=None, target='news_analyst', content='Transferred to news_analyst, adopting the role of news_analyst immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='news_analyst', models_usage=RequestUsage(prompt_tokens=235, completion_tokens=16), content=[FunctionCall(id='call_Owjw6ZbiPdJgNWMHWxhCKgsp', arguments='{"query":"Tesla market news"}', name='get_news')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='news_analyst', models_usage=None, content=[FunctionExecutionResult(content='[{\'title\': \'Tesla Expands Cybertruck Production\', \'date\': \'2024-03-20\', \'summary\': \'Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.\'}, {\'title\': \'Tesla FSD Beta Shows Promise\', \'date\': \'2024-03-19\', \'summary\': \'Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.\'}, {\'title\': \'Model Y Dominates Global EV Sales\', \'date\': \'2024-03-18\', \'summary\': "Tesla\'s Model Y becomes best-selling electric vehicle worldwide, capturing significant market share."}]', call_id='call_Owjw6ZbiPdJgNWMHWxhCKgsp')], type='ToolCallExecutionEvent'), TextMessage(source='news_analyst', models_usage=None, content='Tool calls:\nget_news({"query":"Tesla market news"}) = [{\'title\': \'Tesla Expands Cybertruck Production\', \'date\': \'2024-03-20\', \'summary\': \'Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.\'}, {\'title\': \'Tesla FSD Beta Shows Promise\', \'date\': \'2024-03-19\', \'summary\': \'Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.\'}, {\'title\': \'Model Y Dominates Global EV Sales\', \'date\': \'2024-03-18\', \'summary\': "Tesla\'s Model Y becomes best-selling electric vehicle worldwide, capturing significant market share."}]', type='TextMessage'), TextMessage(source='news_analyst', models_usage=RequestUsage(prompt_tokens=398, completion_tokens=203), content="Here are some of the key market insights regarding Tesla (TSLA):\n\n1. **Expansion in Cybertruck Production**: Tesla has increased its Cybertruck production capacity at the Gigafactory in Texas to meet the high demand. This move might positively impact Tesla's revenues if the demand for the Cybertruck continues to grow.\n\n2. **Advancements in Full Self-Driving (FSD) Technology**: The recent beta release of Tesla's Full Self-Driving software shows significant advancements, particularly in urban navigation and safety. Progress in this area could enhance Tesla's competitive edge in the autonomous driving sector.\n\n3. **Dominance of Model Y in EV Sales**: Tesla's Model Y has become the best-selling electric vehicle globally, capturing a substantial market share. Such strong sales performance reinforces Tesla's leadership in the electric vehicle market.\n\nThese developments reflect Tesla's ongoing innovation and ability to capture market demand, which could positively influence its stock performance and market position. \n\nI will now hand off back to the planner.", type='TextMessage'), ToolCallRequestEvent(source='news_analyst', models_usage=RequestUsage(prompt_tokens=609, completion_tokens=12), content=[FunctionCall(id='call_pn7y6PKsBspWA17uOh3AKNMT', arguments='{}', name='transfer_to_planner')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='news_analyst', models_usage=None, content=[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_pn7y6PKsBspWA17uOh3AKNMT')], type='ToolCallExecutionEvent'), HandoffMessage(source='news_analyst', models_usage=None, target='planner', content='Transferred to planner, adopting the role of planner immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='planner', models_usage=RequestUsage(prompt_tokens=722, completion_tokens=11), content=[FunctionCall(id='call_MmXyWuD2uJT64ZdVI5NfhYdX', arguments='{}', name='transfer_to_writer')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='planner', models_usage=None, content=[FunctionExecutionResult(content='Transferred to writer, adopting the role of writer immediately.', call_id='call_MmXyWuD2uJT64ZdVI5NfhYdX')], type='ToolCallExecutionEvent'), HandoffMessage(source='planner', models_usage=None, target='writer', content='Transferred to writer, adopting the role of writer immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='writer', models_usage=RequestUsage(prompt_tokens=599, completion_tokens=323), content=[FunctionCall(id='call_Pdgu39O6GMYplBiB8jp3uyN3', arguments='{}', name='transfer_to_planner')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='writer', models_usage=None, content=[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_Pdgu39O6GMYplBiB8jp3uyN3')], type='ToolCallExecutionEvent'), HandoffMessage(source='writer', models_usage=None, target='planner', content='Transferred to planner, adopting the role of planner immediately.', type='HandoffMessage'), TextMessage(source='planner', models_usage=RequestUsage(prompt_tokens=772, completion_tokens=4), content='TERMINATE', type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
```

复制到剪贴板

在此页面上


[在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/swarm.ipynb)

[显示源代码](https://microsoft.github.io/autogen/stable/_sources/user-guide/agentchat-user-guide/swarm.ipynb.txt)
