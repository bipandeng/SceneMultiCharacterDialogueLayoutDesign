<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html -->

# 群组（Swarm）#

[`Swarm`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm") 实现了一种智能体团队，其中智能体可以根据自身能力将任务交接给其他智能体。这是一种多智能体设计模式，最初由 OpenAI 在 [Swarm](https://github.com/openai/swarm) 中提出。其核心思想是让智能体使用特殊的工具调用将任务委托给其他智能体，同时所有智能体共享相同的消息上下文。这使得智能体能够就任务规划做出本地决策，而不是依赖于像 [`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 那样的中央协调器。

注意

[`Swarm`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm") 是一个高级 API。如果你需要此 API 不支持的更多控制和定制，可以查看 Core API 文档中的 [Handoff 模式](../core-user-guide/design-patterns/handoffs.html)，并实现你自己的 Swarm 模式版本。

## 它是如何工作的？#

[`Swarm`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm") 团队的核心是一个群组聊天，智能体轮流生成响应。类似于 [`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 和 [`RoundRobinGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat")，参与的智能体会广播它们的响应，因此所有智能体共享相同的消息上下文。

与其他两种群组聊天团队不同的是，在每一轮中，**发言智能体是根据上下文中最近的 [`HandoffMessage`](../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage") 消息来选择的。** 这自然要求团队中的每个智能体都能够生成 [`HandoffMessage`](../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage") 来表示它要将任务交接给哪些其他智能体。

对于 [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent")，你可以设置 `handoffs` 参数来指定它可以交接给哪些智能体。你可以使用 [`Handoff`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.Handoff "autogen_agentchat.base.Handoff") 来定制消息内容和交接行为。

整个过程可以总结如下：

  1. 每个智能体都有能力生成 [`HandoffMessage`](../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage") 来表示它可以将任务交接给哪些其他智能体。对于 [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent")，这意味着设置 `handoffs` 参数。

  2. 当团队开始处理任务时，首个发言的智能体对任务进行操作，并就是否交接以及交接给谁做出本地化决策。

  3. 当智能体生成 [`HandoffMessage`](../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage") 时，接收智能体将在相同的消息上下文下接管任务。

  4. 该过程持续进行，直到满足终止条件。

注意

[`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 使用模型的工具调用能力来生成交接。这意味着模型必须支持工具调用。如果模型支持并行工具调用，则可能同时生成多个交接，这可能导致意外行为。为了避免这种情况，你可以通过配置模型客户端来禁用并行工具调用。对于 [`OpenAIChatCompletionClient`](../../reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.OpenAIChatCompletionClient "autogen_ext.models.openai.OpenAIChatCompletionClient") 和 [`AzureOpenAIChatCompletionClient`](../../reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.AzureOpenAIChatCompletionClient "autogen_ext.models.openai.AzureOpenAIChatCompletionClient")，你可以在配置中设置 `parallel_tool_calls=False`。

在本节中，我们将向你展示两个如何使用 [`Swarm`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm") 团队的示例：

  1. 一个具有人在回路（human-in-the-loop）交接的客服团队。

  2. 一个用于内容生成的自动化团队。

## 客户支持示例#

![Customer Support](../../_images/swarm_customer_support.svg)

该系统通过两个智能体实现航班退款场景：

  * **旅行代理（Travel Agent）**：处理一般的旅行和退款协调。

  * **航班退款专员（Flights Refunder）**：使用 `refund_flight` 工具专门处理航班退款。

此外，我们让用户可以与智能体进行交互，当智能体交接给 `"user"` 时。

### 工作流程#

  1. **旅行代理** 发起对话并评估用户的请求。

  2. 根据请求：

     * 对于与退款相关的任务，旅行代理将任务交接给 **航班退款专员**。

     * 如果需要从客户那里获取信息，任何一个智能体都可以将任务交接给 `"user"`。

  3. **航班退款专员** 在适当的时候使用 `refund_flight` 工具处理退款。

  4. 如果智能体将任务交接给 `"user"`，团队执行将停止并等待用户输入响应。

  5. 当用户提供输入时，它会作为 [`HandoffMessage`](../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage") 发送回团队。此消息将定向到最初请求用户输入的智能体。

  6. 该过程持续进行，直到旅行代理确定任务已完成并终止工作流。
    
    
    from typing import Any, Dict, List
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
    from autogen_agentchat.messages import HandoffMessage
    from autogen_agentchat.teams import Swarm
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    

### 工具#
    
    
    def refund_flight(flight_id: str) -> str:
        """Refund a flight"""
        return f"Flight {flight_id} refunded"
    

### 智能体#
    
    
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
    
    
    
    termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")
    team = Swarm([travel_agent, flights_refunder], termination_condition=termination)
    
    
    
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
    
    
    # Use asyncio.run(...) if you are running this in a script.
    await run_team_stream()
    await model_client.close()
    
    
    
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
    

## 股票研究示例#

![Stock Research](../../_images/swarm_stock_research.svg)

该系统旨在通过利用四个智能体来执行股票研究任务：

  * **规划者（Planner）**：中央协调器，根据各个智能体的专长将特定任务委派给专门的智能体。规划者确保高效利用每个智能体并监督整个工作流。

  * **金融分析师（Financial Analyst）**：专门负责使用 `get_stock_data` 等工具分析金融指标和股票数据的智能体。

  * **新闻分析师（News Analyst）**：专注于使用 `get_news` 等工具收集和总结与该股票相关的近期新闻文章的智能体。

  * **撰稿人（Writer）**：负责将股票和新闻分析的结果编制成一份连贯的最终报告的智能体。

### 工作流程#

  1. **规划者** 通过以循序渐进的方式将任务委派给合适的智能体来启动研究过程。

  2. 每个智能体独立执行其任务，并将其工作附加到共享的 **消息线程/历史记录** 中。智能体并不是直接将结果返回给规划者，而是所有智能体都对此共享消息历史进行贡献和读取。当智能体使用 LLM 生成其工作时，它们可以访问此共享消息历史，这提供了上下文并有助于跟踪任务的整体进度。

  3. 一旦智能体完成其任务，它会将控制权交回给规划者。

  4. 该过程持续进行，直到规划者确定所有必要的任务都已完成，并决定终止工作流。

### 工具#
    
    
    async def get_stock_data(symbol: str) -> Dict[str, Any]:
        """Get stock market data for a given symbol"""
        return {"price": 180.25, "volume": 1000000, "pe_ratio": 65.4, "market_cap": "700B"}
    
    
    async def get_news(query: str) -> List[Dict[str, str]]:
        """Get recent news articles about a company"""
        return [
            {
                "title": "Tesla Expands Cybertruck Production",
                "date": "2024-03-20",
                "summary": "Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.",
            },
            {
                "title": "Tesla FSD Beta Shows Promise",
                "date": "2024-03-19",
                "summary": "Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.",
            },
            {
                "title": "Model Y Dominates Global EV Sales",
                "date": "2024-03-18",
                "summary": "Tesla's Model Y becomes best-selling electric vehicle worldwide, capturing significant market share.",
            },
        ]
    
    
    
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
    
    
    
    # Define termination condition
    text_termination = TextMentionTermination("TERMINATE")
    termination = text_termination
    
    research_team = Swarm(
        participants=[planner, financial_analyst, news_analyst, writer], termination_condition=termination
    )
    
    task = "Conduct market research for TSLA stock"
    await Console(research_team.run_stream(task=task))
    await model_client.close()
    
    
    
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
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Conduct market research for TSLA stock', type='TextMessage'), ToolCallRequestEvent(source='planner', models_usage=RequestUsage(prompt_tokens=169, completion_tokens=166), content=[FunctionCall(id='call_BX5QaRuhmB8CxTsBlqCUIXPb', arguments='{}', name='transfer_to_financial_analyst')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='planner', models_usage=None, content=[FunctionExecutionResult(content='Transferred to financial_analyst, adopting the role of financial_analyst immediately.', call_id='call_BX5QaRuhmB8CxTsBlqCUIXPb')], type='ToolCallExecutionEvent'), HandoffMessage(source='planner', models_usage=None, target='financial_analyst', content='Transferred to financial_analyst, adopting the role of financial_analyst immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='financial_analyst', models_usage=RequestUsage(prompt_tokens=136, completion_tokens=16), content=[FunctionCall(id='call_SAXy1ebtA9mnaZo4ztpD2xHA', arguments='{"symbol":"TSLA"}', name='get_stock_data')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='financial_analyst', models_usage=None, content=[FunctionExecutionResult(content="{'price': 180.25, 'volume': 1000000, 'pe_ratio': 65.4, 'market_cap': '700B'}", call_id='call_SAXy1ebtA9mnaZo4ztpD2xHA')], type='ToolCallExecutionEvent'), TextMessage(source='financial_analyst', models_usage=None, content='Tool calls:\nget_stock_data({"symbol":"TSLA"}) = {\'price\': 180.25, \'volume\': 1000000, \'pe_ratio\': 65.4, \'market_cap\': \'700B\'}', type='TextMessage'), ToolCallRequestEvent(source='financial_analyst', models_usage=RequestUsage(prompt_tokens=199, completion_tokens=337), content=[FunctionCall(id='call_IsdcFUfBVmtcVzfSuwQpeAwl', arguments='{}', name='transfer_to_planner')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='financial_analyst', models_usage=None, content=[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_IsdcFUfBVmtcVzfSuwQpeAwl')], type='ToolCallExecutionEvent'), HandoffMessage(source='financial_analyst', models_usage=None, target='planner', content='Transferred to planner, adopting the role of planner immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='planner', models_usage=RequestUsage(prompt_tokens=291, completion_tokens=14), content=[FunctionCall(id='call_tN5goNFahrdcSfKnQqT0RONN', arguments='{}', name='transfer_to_news_analyst')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='planner', models_usage=None, content=[FunctionExecutionResult(content='Transferred to news_analyst, adopting the role of news_analyst immediately.', call_id='call_tN5goNFahrdcSfKnQqT0RONN')], type='ToolCallExecutionEvent'), HandoffMessage(source='planner', models_usage=None, target='news_analyst', content='Transferred to news_analyst, adopting the role of news_analyst immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='news_analyst', models_usage=RequestUsage(prompt_tokens=235, completion_tokens=16), content=[FunctionCall(id='call_Owjw6ZbiPdJgNWMHWxhCKgsp', arguments='{"query":"Tesla market news"}', name='get_news')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='news_analyst', models_usage=None, content=[FunctionExecutionResult(content='[{\'title\': \'Tesla Expands Cybertruck Production\', \'date\': \'2024-03-20\', \'summary\': \'Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.\'}, {\'title\': \'Tesla FSD Beta Shows Promise\', \'date\': \'2024-03-19\', \'summary\': \'Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.\'}, {\'title\': \'Model Y Dominates Global EV Sales\', \'date\': \'2024-03-18\', \'summary\': "Tesla\'s Model Y becomes best-selling electric vehicle worldwide, capturing significant market share."}]', call_id='call_Owjw6ZbiPdJgNWMHWxhCKgsp')], type='ToolCallExecutionEvent'), TextMessage(source='news_analyst', models_usage=None, content='Tool calls:\nget_news({"query":"Tesla market news"}) = [{\'title\': \'Tesla Expands Cybertruck Production\', \'date\': \'2024-03-20\', \'summary\': \'Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.\'}, {\'title\': \'Tesla FSD Beta Shows Promise\', \'date\': \'2024-03-19\', \'summary\': \'Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.\'}, {\'title\': \'Model Y Dominates Global EV Sales\', \'date\': \'2024-03-18\', \'summary\': "Tesla\'s Model Y becomes best-selling electric vehicle worldwide, capturing significant market share."}]', type='TextMessage'), TextMessage(source='news_analyst', models_usage=RequestUsage(prompt_tokens=398, completion_tokens=203), content="Here are some of the key market insights regarding Tesla (TSLA):\n\n1. **Expansion in Cybertruck Production**: Tesla has increased its Cybertruck production capacity at the Gigafactory in Texas to meet the high demand. This move might positively impact Tesla's revenues if the demand for the Cybertruck continues to grow.\n\n2. **Advancements in Full Self-Driving (FSD) Technology**: The recent beta release of Tesla's Full Self-Driving software shows significant advancements, particularly in urban navigation and safety. Progress in this area could enhance Tesla's competitive edge in the autonomous driving sector.\n\n3. **Dominance of Model Y in EV Sales**: Tesla's Model Y has become the best-selling electric vehicle globally, capturing a substantial market share. Such strong sales performance reinforces Tesla's leadership in the electric vehicle market.\n\nThese developments reflect Tesla's ongoing innovation and ability to capture market demand, which could positively influence its stock performance and market position. \n\nI will now hand off back to the planner.", type='TextMessage'), ToolCallRequestEvent(source='news_analyst', models_usage=RequestUsage(prompt_tokens=609, completion_tokens=12), content=[FunctionCall(id='call_pn7y6PKsBspWA17uOh3AKNMT', arguments='{}', name='transfer_to_planner')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='news_analyst', models_usage=None, content=[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_pn7y6PKsBspWA17uOh3AKNMT')], type='ToolCallExecutionEvent'), HandoffMessage(source='news_analyst', models_usage=None, target='planner', content='Transferred to planner, adopting the role of planner immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='planner', models_usage=RequestUsage(prompt_tokens=722, completion_tokens=11), content=[FunctionCall(id='call_MmXyWuD2uJT64ZdVI5NfhYdX', arguments='{}', name='transfer_to_writer')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='planner', models_usage=None, content=[FunctionExecutionResult(content='Transferred to writer, adopting the role of writer immediately.', call_id='call_MmXyWuD2uJT64ZdVI5NfhYdX')], type='ToolCallExecutionEvent'), HandoffMessage(source='planner', models_usage=None, target='writer', content='Transferred to writer, adopting the role of writer immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='writer', models_usage=RequestUsage(prompt_tokens=599, completion_tokens=323), content=[FunctionCall(id='call_Pdgu39O6GMYplBiB8jp3uyN3', arguments='{}', name='transfer_to_planner')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='writer', models_usage=None, content=[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_Pdgu39O6GMYplBiB8jp3uyN3')], type='ToolCallExecutionEvent'), HandoffMessage(source='writer', models_usage=None, target='planner', content='Transferred to planner, adopting the role of planner immediately.', type='HandoffMessage'), TextMessage(source='planner', models_usage=RequestUsage(prompt_tokens=772, completion_tokens=4), content='TERMINATE', type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
    

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/swarm.ipynb)

[ __Show Source](../../_sources/user-guide/agentchat-user-guide/swarm.ipynb.txt)
