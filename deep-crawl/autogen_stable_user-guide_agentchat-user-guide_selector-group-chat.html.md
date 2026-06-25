<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/selector-group-chat.html -->

# 选择器群聊#

[`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 实现了一个团队，其中参与者轮流向所有其他成员广播消息。生成模型（例如 LLM）根据共享上下文选择下一个发言者，从而实现动态的、上下文感知的协作。

主要特性包括：

  * 基于模型的发言者选择

  * 可配置的参与者角色和描述

  * 防止同一发言者连续发言（可选）

  * 可自定义的选择提示词

  * 可自定义的选择函数以覆盖默认的基于模型的选择

  * 可自定义的候选函数以缩小模型选择的代理范围

注意

[`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 是一个高级 API。如需更多控制和定制，请参考核心 API 文档中的 [群聊模式](../core-user-guide/design-patterns/group-chat.html) 来实现您自己的群聊逻辑。

## 工作原理#

[`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 是一种群聊，类似于 [`RoundRobinGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat")，但具有基于模型的下一位发言者选择机制。当团队通过 [`run()`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run "autogen_agentchat.teams.BaseGroupChat.run") 或 [`run_stream()`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run_stream "autogen_agentchat.teams.BaseGroupChat.run_stream") 接收任务时，将执行以下步骤：

  1. 团队分析当前对话上下文，包括对话历史以及参与者的 [`name`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.ChatAgent.name "autogen_agentchat.base.ChatAgent.name") 和 [`description`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.ChatAgent.description "autogen_agentchat.base.ChatAgent.description") 属性，使用模型确定下一个发言者。默认情况下，团队不会连续选择同一个发言者，除非它是唯一可用的代理。可以通过设置 `allow_repeated_speaker=True` 来更改此行为。您还可以通过提供自定义选择函数来覆盖模型。

  2. 团队提示被选中的发言者代理提供响应，然后将其 **广播** 给所有其他参与者。

  3. 检查终止条件以确定对话是否应该结束，如果未结束，则从步骤 1 重新开始该过程。

  4. 当对话结束时，团队返回包含此次任务对话历史的 [`TaskResult`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult")。

一旦团队完成任务，对话上下文就会保留在团队和所有参与者中，因此下一个任务可以从之前的对话上下文继续。您可以通过调用 [`reset()`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.reset "autogen_agentchat.teams.BaseGroupChat.reset") 来重置对话上下文。

在本节中，我们将通过一个简单的 Web 搜索和数据分析任务示例来演示如何使用 [`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat")。

## 示例：Web 搜索/分析#
    
    
    from typing import List, Sequence
    
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
    from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
    from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
    from autogen_agentchat.teams import SelectorGroupChat
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    

### 代理#

![选择器群聊](../../_images/selector-group-chat.svg)

该系统使用了三个专业化代理：

  * **规划代理 (Planning Agent)** ：战略协调员，负责将复杂任务分解为可管理的子任务。

  * **Web 搜索代理 (Web Search Agent)** ：信息检索专家，与 `search_web_tool` 交互。

  * **数据分析代理 (Data Analyst Agent)** ：专攻计算的代理，配备 `percentage_change_tool`。

工具 `search_web_tool` 和 `percentage_change_tool` 是代理可用于执行其任务的外部工具。
    
    
    # 注意：此示例使用模拟工具而非真实 API 进行演示
    def search_web_tool(query: str) -> str:
        if "2006-2007" in query:
            return """以下是迈阿密热火队球员在 2006-2007 赛季的总得分：
            Udonis Haslem：844 分
            Dwayne Wade：1397 分
            James Posey：550 分
            ...
            """
        elif "2007-2008" in query:
            return "Dwayne Wade 在迈阿密热火队 2007-2008 赛季的总篮板数为 214。"
        elif "2008-2009" in query:
            return "Dwayne Wade 在迈阿密热火队 2008-2009 赛季的总篮板数为 398。"
        return "未找到数据。"
    
    
    def percentage_change_tool(start: float, end: float) -> float:
        return ((end - start) / start) * 100
    

让我们使用 [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 类创建专业代理。需要注意的是，代理的 [`name`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.ChatAgent.name "autogen_agentchat.base.ChatAgent.name") 和 [`description`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.ChatAgent.description "autogen_agentchat.base.ChatAgent.description") 属性由模型用来确定下一个发言者，因此建议提供有意义的名称和描述。
    
    
    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    
    planning_agent = AssistantAgent(
        "PlanningAgent",
        description="用于规划任务的代理。当给定新任务时，此代理应首先参与。",
        model_client=model_client,
        system_message="""
您是规划代理。
您的工作是将复杂任务分解为更小的、可管理的子任务。
您的团队成员包括：
    WebSearchAgent：搜索信息
    DataAnalystAgent：执行计算

您只负责规划和分配任务 - 不亲自执行它们。

分配任务时，请使用以下格式：
1. <agent> : <task>

所有任务完成后，总结发现并以 "TERMINATE" 结尾。
""",
    )
    
    web_search_agent = AssistantAgent(
        "WebSearchAgent",
        description="用于在 Web 上搜索信息的代理。",
        tools=[search_web_tool],
        model_client=model_client,
        system_message="""
您是 Web 搜索代理。
您唯一的工具是 search_tool - 使用它来查找信息。
您每次只进行一次搜索调用。
获得结果后，您永远不会基于结果进行计算。
""",
    )
    
    data_analyst_agent = AssistantAgent(
        "DataAnalystAgent",
        description="用于执行计算的代理。",
        model_client=model_client,
        tools=[percentage_change_tool],
        system_message="""
您是数据分析代理。
根据分配给您的任务，您应该使用提供的工具分析数据并提供结果。
如果您尚未看到数据，请索取数据。
""",
    )
    

注意

默认情况下，[`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 将工具输出作为响应返回。如果您的工具未以自然语言格式返回格式良好的字符串，您可能需要在创建代理时通过设置 `reflect_on_tool_use=True` 在代理内添加一个反思步骤。这将允许代理反思工具输出并提供自然语言响应。

### 工作流程#

  1. 任务由 [`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 接收，后者根据代理描述选择最合适的代理来处理初始任务（通常是规划代理）。

  2. **规划代理 (Planning Agent)** 分析任务并将其分解为子任务，使用以下格式将每个子任务分配给最合适的代理：`<agent> : <task>`

  3. 基于对话上下文和代理描述，`SelectorGroupChat` 管理器动态选择下一个代理来处理其分配的子任务。

  4. **Web 搜索代理 (Web Search Agent)** 一次执行一次搜索，将结果存储在共享对话历史中。

  5. **数据分析代理 (Data Analyst Agent)** 在被选中时使用可用的计算工具处理收集的信息。

  6. 工作流继续进行，代理被动态选择，直到以下任一情况：

     * 规划代理确定所有子任务已完成并发送 "TERMINATE"

     * 满足替代终止条件（例如，最大消息数）

定义代理时，请确保包含有用的 [`description`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.ChatAgent.description "autogen_agentchat.base.ChatAgent.description")，因为这用于决定接下来选择哪个代理。

### 终止条件#

让我们使用两个终止条件：[`TextMentionTermination`](../../reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TextMentionTermination "autogen_agentchat.conditions.TextMentionTermination") 在规划代理发送 "TERMINATE" 时结束对话，以及 [`MaxMessageTermination`](../../reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.MaxMessageTermination "autogen_agentchat.conditions.MaxMessageTermination") 将对话限制为 25 条消息以避免无限循环。
    
    
    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = text_mention_termination | max_messages_termination
    

### 选择器提示词#

[`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 使用模型根据对话上下文选择下一个发言者。我们将使用自定义选择器提示词以正确对齐工作流程。
    
    
    selector_prompt = """选择一个代理来执行任务。

{roles}

当前对话上下文：
{history}

阅读以上对话，然后从 {participants} 中选择一个代理来执行下一个任务。
确保在其它代理开始工作之前，规划代理已经分配了任务。
只选择一个代理。
"""
    

选择器提示词中可用的字符串变量有：

  * `{participants}`：候选选择的名称列表。格式为 `["<name1>", "<name2>", ...]`。

  * `{roles}`：候选代理的名称和描述的换行分隔列表。每行的格式为：`"<name> : <description>"`。

  * `{history}`：对话历史，格式化为名称和消息内容的双换行分隔。每条消息的格式为：`"<name> : <message content>"`。

提示

尽量不要在选择器提示词中给模型过多的指令。

多少算过多？这取决于您使用的模型的能力。对于 GPT-4o 及同等模型，您可以使用带有每个发言者应选择条件的选择器提示词。对于较小的模型（如 Phi-4），您应该保持选择器提示词尽可能简单，如此示例中使用的提示词。

通常，如果您发现自己在为每个代理编写多个条件，这表明您应该考虑使用自定义选择函数，或将任务分解为由单独的代理或团队处理的更小的顺序任务。

### 运行团队#

让我们使用代理、终止条件和自定义选择器提示词创建团队。
    
    
    team = SelectorGroupChat(
        [planning_agent, web_search_agent, data_analyst_agent],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True,  # 允许代理连续多次发言。
    )
    

现在我们运行团队，执行查找有关 NBA 球员信息的任务。
    
    
    task = "谁是迈阿密热火队在 2006-2007 赛季得分最高的球员，以及他在 2007-2008 和 2008-2009 赛季之间的总篮板百分比变化是多少？"
    
    
    
    # 如果在脚本中运行，请使用 asyncio.run(...)。
    await Console(team.run_stream(task=task))
    
    
    
    ---------- user ----------
    Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
    ---------- PlanningAgent ----------
    To complete this task, we need to perform the following subtasks:
    
    1. Find out which Miami Heat player had the highest points in the 2006-2007 season.
    2. Gather data on this player's total rebounds for the 2007-2008 season.
    3. Gather data on this player's total rebounds for the 2008-2009 season.
    4. Calculate the percentage change in the player's total rebounds between the 2007-2008 and 2008-2009 seasons.
    
    I'll assign these tasks accordingly:
    
    1. WebSearchAgent: Search for the Miami Heat player with the highest points in the 2006-2007 NBA season.
    2. WebSearchAgent: Find the total rebounds for this player in the 2007-2008 NBA season.
    3. WebSearchAgent: Find the total rebounds for this player in the 2008-2009 NBA season.
    4. DataAnalystAgent: Calculate the percentage change in total rebounds from the 2007-2008 season to the 2008-2009 season for this player.
    ---------- WebSearchAgent ----------
    [FunctionCall(id='call_89tUNHaAM0kKQYPJLleGUKK7', arguments='{"query":"Miami Heat player highest points 2006-2007 season"}', name='search_web_tool')]
    ---------- WebSearchAgent ----------
    [FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', name='search_web_tool', call_id='call_89tUNHaAM0kKQYPJLleGUKK7', is_error=False)]
    ---------- WebSearchAgent ----------
    Here are the total points scored by Miami Heat players in the 2006-2007 season:
            Udonis Haslem: 844 points
            Dwayne Wade: 1397 points
            James Posey: 550 points
            ...
            
    ---------- WebSearchAgent ----------
    The Miami Heat player with the highest points in the 2006-2007 season was Dwyane Wade, with 1,397 points.
    
    Next, I will search for Dwyane Wade's total rebounds for the 2007-2008 season.
    ---------- WebSearchAgent ----------
    [FunctionCall(id='call_RC55TkSjG3JXRuVOTPrcE1RL', arguments='{"query":"Dwyane Wade total rebounds 2007-2008 season"}', name='search_web_tool')]
    ---------- WebSearchAgent ----------
    [FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', name='search_web_tool', call_id='call_RC55TkSjG3JXRuVOTPrcE1RL', is_error=False)]
    ---------- WebSearchAgent ----------
    The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.
    ---------- WebSearchAgent ----------
    [FunctionCall(id='call_pBXoABrErDow0rZjw3tjOZol', arguments='{"query":"Dwyane Wade total rebounds 2008-2009 season"}', name='search_web_tool')]
    ---------- WebSearchAgent ----------
    [FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', name='search_web_tool', call_id='call_pBXoABrErDow0rZjw3tjOZol', is_error=False)]
    ---------- WebSearchAgent ----------
    The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.
    ---------- DataAnalystAgent ----------
    [FunctionCall(id='call_qMxxXtcJsiK8KFSSCx3zm0is', arguments='{"start":214,"end":398}', name='percentage_change_tool')]
    ---------- DataAnalystAgent ----------
    [FunctionExecutionResult(content='85.98130841121495', name='percentage_change_tool', call_id='call_qMxxXtcJsiK8KFSSCx3zm0is', is_error=False)]
    ---------- DataAnalystAgent ----------
    85.98130841121495
    ---------- PlanningAgent ----------
    The player with the highest points for the Miami Heat in the 2006-2007 NBA season was Dwyane Wade, who scored 1,397 points. The percentage change in Dwyane Wade's total rebounds from 214 in the 2007-2008 season to 398 in the 2008-2009 season is approximately 85.98%.
    
    TERMINATE
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?', type='TextMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=161, completion_tokens=220), metadata={}, content="To complete this task, we need to perform the following subtasks:\n\n1. Find out which Miami Heat player had the highest points in the 2006-2007 season.\n2. Gather data on this player's total rebounds for the 2007-2008 season.\n3. Gather data on this player's total rebounds for the 2008-2009 season.\n4. Calculate the percentage change in the player's total rebounds between the 2007-2008 and 2008-2009 seasons.\n\nI'll assign these tasks accordingly:\n\n1. WebSearchAgent: Search for the Miami Heat player with the highest points in the 2006-2007 NBA season.\n2. WebSearchAgent: Find the total rebounds for this player in the 2007-2008 NBA season.\n3. WebSearchAgent: Find the total rebounds for this player in the 2008-2009 NBA season.\n4. DataAnalystAgent: Calculate the percentage change in total rebounds from the 2007-2008 season to the 2008-2009 season for this player.", type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=368, completion_tokens=27), metadata={}, content=[FunctionCall(id='call_89tUNHaAM0kKQYPJLleGUKK7', arguments='{"query":"Miami Heat player highest points 2006-2007 season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', name='search_web_tool', call_id='call_89tUNHaAM0kKQYPJLleGUKK7', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, metadata={}, content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', type='ToolCallSummaryMessage'), ThoughtEvent(source='WebSearchAgent', models_usage=None, metadata={}, content="The Miami Heat player with the highest points in the 2006-2007 season was Dwyane Wade, with 1,397 points.\n\nNext, I will search for Dwyane Wade's total rebounds for the 2007-2008 season.", type='ThoughtEvent'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=460, completion_tokens=83), metadata={}, content=[FunctionCall(id='call_RC55TkSjG3JXRuVOTPrcE1RL', arguments='{"query":"Dwyane Wade total rebounds 2007-2008 season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', name='search_web_tool', call_id='call_RC55TkSjG3JXRuVOTPrcE1RL', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, metadata={}, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=585, completion_tokens=28), metadata={}, content=[FunctionCall(id='call_pBXoABrErDow0rZjw3tjOZol', arguments='{"query":"Dwyane Wade total rebounds 2008-2009 season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', name='search_web_tool', call_id='call_pBXoABrErDow0rZjw3tjOZol', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, metadata={}, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=496, completion_tokens=21), metadata={}, content=[FunctionCall(id='call_qMxxXtcJsiK8KFSSCx3zm0is', arguments='{"start":214,"end":398}', name='percentage_change_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='DataAnalystAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='85.98130841121495', name='percentage_change_tool', call_id='call_qMxxXtcJsiK8KFSSCx3zm0is', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='DataAnalystAgent', models_usage=None, metadata={}, content='85.98130841121495', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=528, completion_tokens=80), metadata={}, content="The player with the highest points for the Miami Heat in the 2006-2007 NBA season was Dwyane Wade, who scored 1,397 points. The percentage change in Dwyane Wade's total rebounds from 214 in the 2007-2008 season to 398 in the 2008-2009 season is approximately 85.98%.\n\nTERMINATE", type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
    

如我们所见，在 Web 搜索代理完成必要的搜索且数据分析代理完成必要的计算之后，我们发现 Dwayne Wade 是迈阿密热火队在 2006-2007 赛季得分最高的球员，并且他在 2007-2008 和 2008-2009 赛季之间的总篮板百分比变化为 85.98%！

## 自定义选择函数#

很多时候，我们希望对选择过程有更好的控制。为此，我们可以使用自定义选择函数设置 `selector_func` 参数，以覆盖默认的基于模型的选择。这允许我们实现更复杂的选择逻辑和基于状态的转换。

例如，我们希望规划代理在任何专业代理发言后立即发言以检查进度。

注意

从自定义选择函数返回 `None` 将使用默认的基于模型的选择。

注意

当对 SelectorGroupChat 团队调用 `.dump_component()` 时，自定义选择函数不会被 [序列化](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/serialize-components.html)。如果您需要序列化带有自定义选择函数的团队配置，请考虑实现自定义工作流和序列化逻辑。
    
    
    def selector_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
        if messages[-1].source != planning_agent.name:
            return planning_agent.name
        return None
    
    
    # 重置之前的团队并使用选择函数再次运行聊天。
    await team.reset()
    team = SelectorGroupChat(
        [planning_agent, web_search_agent, data_analyst_agent],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True,
        selector_func=selector_func,
    )
    
    await Console(team.run_stream(task=task))
    
    
    
    ---------- user ----------
    Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
    ---------- PlanningAgent ----------
    To answer this question, we need to follow these steps: 
    
    1. Identify the Miami Heat player with the highest points in the 2006-2007 season.
    2. Retrieve the total rebounds of that player for the 2007-2008 and 2008-2009 seasons.
    3. Calculate the percentage change in his total rebounds between the two seasons.
    
    Let's delegate these tasks:
    
    1. WebSearchAgent: Find the Miami Heat player with the highest points in the 2006-2007 NBA season.
    2. WebSearchAgent: Retrieve the total rebounds for the identified player during the 2007-2008 NBA season.
    3. WebSearchAgent: Retrieve the total rebounds for the identified player during the 2008-2009 NBA season.
    4. DataAnalystAgent: Calculate the percentage change in total rebounds between the 2007-2008 and 2008-2009 seasons for the player found.
    ---------- WebSearchAgent ----------
    [FunctionCall(id='call_Pz82ndNLSV4cH0Sg6g7ArP4L', arguments='{"query":"Miami Heat player highest points 2006-2007 season"}', name='search_web_tool')]
    ---------- WebSearchAgent ----------
    [FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', call_id='call_Pz82ndNLSV4cH0Sg6g7ArP4L')]
    ---------- WebSearchAgent ----------
    Here are the total points scored by Miami Heat players in the 2006-2007 season:
            Udonis Haslem: 844 points
            Dwayne Wade: 1397 points
            James Posey: 550 points
            ...
            
    ---------- PlanningAgent ----------
    Great! Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season. Now, let's continue with the next tasks:
    
    2. WebSearchAgent: Retrieve the total rebounds for Dwyane Wade during the 2007-2008 NBA season.
    3. WebSearchAgent: Retrieve the total rebounds for Dwyane Wade during the 2008-2009 NBA season.
    ---------- WebSearchAgent ----------
    [FunctionCall(id='call_3qv9so2DXFZIHtzqDIfXoFID', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 season"}', name='search_web_tool'), FunctionCall(id='call_Vh7zzzWUeiUAvaYjP0If0k1k', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 season"}', name='search_web_tool')]
    ---------- WebSearchAgent ----------
    [FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_3qv9so2DXFZIHtzqDIfXoFID'), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_Vh7zzzWUeiUAvaYjP0If0k1k')]
    ---------- WebSearchAgent ----------
    The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.
    The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.
    ---------- PlanningAgent ----------
    Now let's calculate the percentage change in total rebounds between the 2007-2008 and 2008-2009 seasons for Dwyane Wade.
    
    4. DataAnalystAgent: Calculate the percentage change in total rebounds for Dwyane Wade between the 2007-2008 and 2008-2009 seasons.
    ---------- DataAnalystAgent ----------
    [FunctionCall(id='call_FXnPSr6JVGfAWs3StIizbt2V', arguments='{"start":214,"end":398}', name='percentage_change_tool')]
    ---------- DataAnalystAgent ----------
    [FunctionExecutionResult(content='85.98130841121495', call_id='call_FXnPSr6JVGfAWs3StIizbt2V')]
    ---------- DataAnalystAgent ----------
    85.98130841121495
    ---------- PlanningAgent ----------
    Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring a total of 1397 points. The percentage change in his total rebounds from the 2007-2008 season (214 rebounds) to the 2008-2009 season (398 rebounds) is approximately 86.0%.
    
    TERMINATE
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?', type='TextMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=161, completion_tokens=192), content="To answer this question, we need to follow these steps: \n\n1. Identify the Miami Heat player with the highest points in the 2006-2007 season.\n2. Retrieve the total rebounds of that player for the 2007-2008 and 2008-2009 seasons.\n3. Calculate the percentage change in his total rebounds between the two seasons.\n\nLet's delegate these tasks:\n\n1. WebSearchAgent: Find the Miami Heat player with the highest points in the 2006-2007 NBA season.\n2. WebSearchAgent: Retrieve the total rebounds for the identified player during the 2007-2008 NBA season.\n3. WebSearchAgent: Retrieve the total rebounds for the identified player during the 2008-2009 NBA season.\n4. DataAnalystAgent: Calculate the percentage change in total rebounds between the 2007-2008 and 2008-2009 seasons for the player found.", type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=340, completion_tokens=27), content=[FunctionCall(id='call_Pz82ndNLSV4cH0Sg6g7ArP4L', arguments='{"query":"Miami Heat player highest points 2006-2007 season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, content=[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', call_id='call_Pz82ndNLSV4cH0Sg6g7ArP4L')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=420, completion_tokens=87), content="Great! Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season. Now, let's continue with the next tasks:\n\n2. WebSearchAgent: Retrieve the total rebounds for Dwyane Wade during the 2007-2008 NBA season.\n3. WebSearchAgent: Retrieve the total rebounds for Dwyane Wade during the 2008-2009 NBA season.", type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=525, completion_tokens=71), content=[FunctionCall(id='call_3qv9so2DXFZIHtzqDIfXoFID', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 season"}', name='search_web_tool'), FunctionCall(id='call_Vh7zzzWUeiUAvaYjP0If0k1k', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, content=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_3qv9so2DXFZIHtzqDIfXoFID'), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_Vh7zzzWUeiUAvaYjP0If0k1k')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.\nThe number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=569, completion_tokens=68), content="Now let's calculate the percentage change in total rebounds between the 2007-2008 and 2008-2009 seasons for Dwyane Wade.\n\n4. DataAnalystAgent: Calculate the percentage change in total rebounds for Dwyane Wade between the 2007-2008 and 2008-2009 seasons.", type='TextMessage'), ToolCallRequestEvent(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=627, completion_tokens=21), content=[FunctionCall(id='call_FXnPSr6JVGfAWs3StIizbt2V', arguments='{"start":214,"end":398}', name='percentage_change_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='DataAnalystAgent', models_usage=None, content=[FunctionExecutionResult(content='85.98130841121495', call_id='call_FXnPSr6JVGfAWs3StIizbt2V')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='DataAnalystAgent', models_usage=None, content='85.98130841121495', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=659, completion_tokens=76), content='Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring a total of 1397 points. The percentage change in his total rebounds from the 2007-2008 season (214 rebounds) to the 2008-2009 season (398 rebounds) is approximately 86.0%.\n\nTERMINATE', type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
    

您可以从对话日志中看到，规划代理总是在专业代理之后立即发言。

提示

每个参与代理每轮只执行一步（执行工具、生成响应等）。如果您希望 [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 重复执行直到停止返回 [`ToolCallSummaryMessage`](../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallSummaryMessage "autogen_agentchat.messages.ToolCallSummaryMessage")（当它完成运行所需的所有工具时），您可以通过检查最后一条消息并在其为 [`ToolCallSummaryMessage`](../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallSummaryMessage "autogen_agentchat.messages.ToolCallSummaryMessage") 时返回该代理来实现。

## 自定义候选函数#

另一个可能的需求是从过滤后的代理列表中自动选择下一个发言者。为此，我们可以设置 `candidate_func` 参数，使用自定义候选函数来过滤每一轮群聊中用于发言者选择的潜在代理列表。

这允许我们在给定代理之后将发言者选择限制为一组特定的代理。

注意

仅当未设置 `selector_func` 时，`candidate_func` 才有效。从自定义候选函数返回 `None` 或空列表 `[]` 将引发 `ValueError`。
    
    
    def candidate_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> List[str]:
        # 保持 planning_agent 首先规划任务
        if messages[-1].source == "user":
            return [planning_agent.name]
    
        # 如果上一个代理是 planning_agent，并且它明确要求 web_search_agent
        # 或 data_analyst_agent 或两者（在重新规划或重新分配任务的情况下）
        # 则返回这些特定的代理
        last_message = messages[-1]
        if last_message.source == planning_agent.name:
            participants = []
            if web_search_agent.name in last_message.to_text():
                participants.append(web_search_agent.name)
            if data_analyst_agent.name in last_message.to_text():
                participants.append(data_analyst_agent.name)
            if participants:
                return participants  # SelectorGroupChat 将从剩余的两个代理中选择。
    
        # 我们可以假设一旦 web_search_agent
        # 和 data_analyst_agent 已经轮流发言过，任务就完成了，因此我们发送
        # planning_agent 来终止聊天
        previous_set_of_agents = set(message.source for message in messages)
        if web_search_agent.name in previous_set_of_agents and data_analyst_agent.name in previous_set_of_agents:
            return [planning_agent.name]
    
        # 如果没有满足的条件，则返回所有代理
        return [planning_agent.name, web_search_agent.name, data_analyst_agent.name]
    
    
    # 重置之前的团队并使用选择函数再次运行聊天。
    await team.reset()
    team = SelectorGroupChat(
        [planning_agent, web_search_agent, data_analyst_agent],
        model_client=model_client,
        termination_condition=termination,
        candidate_func=candidate_func,
    )
    
    await Console(team.run_stream(task=task))
    
    
    
    ---------- user ----------
    Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
    ---------- PlanningAgent ----------
    To answer this question, we'll break it down into two main subtasks:
    
    1. Identify the Miami Heat player with the highest points in the 2006-2007 season.
    2. Calculate the percentage change in that player's total rebounds between the 2007-2008 and 2008-2009 seasons.
    
    Let's assign these tasks:
    
    1. WebSearchAgent: Search for the Miami Heat player with the highest points in the 2006-2007 NBA season.
    2. WebSearchAgent: Find the total rebound statistics for that identified player for both the 2007-2008 and 2008-2009 NBA seasons.
    3. DataAnalystAgent: Calculate the percentage change in the player's total rebounds between the 2007-2008 and 2008-2009 seasons once the data is retrieved.
    ---------- WebSearchAgent ----------
    [FunctionCall(id='call_WtR5KTfEIxs3jIO25gjAw7dF', arguments='{"query":"Miami Heat highest points scorer 2006-2007 NBA season"}', name='search_web_tool')]
    ---------- WebSearchAgent ----------
    [FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', name='search_web_tool', call_id='call_WtR5KTfEIxs3jIO25gjAw7dF', is_error=False)]
    ---------- WebSearchAgent ----------
    Here are the total points scored by Miami Heat players in the 2006-2007 season:
            Udonis Haslem: 844 points
            Dwayne Wade: 1397 points
            James Posey: 550 points
            ...
            
    ---------- DataAnalystAgent ----------
    [FunctionCall(id='call_9HA3DEacUl4WuG2G2PtRkXAO', arguments='{"start": 432, "end": 527}', name='percentage_change_tool')]
    ---------- DataAnalystAgent ----------
    [FunctionExecutionResult(content='21.99074074074074', name='percentage_change_tool', call_id='call_9HA3DEacUl4WuG2G2PtRkXAO', is_error=False)]
    ---------- DataAnalystAgent ----------
    21.99074074074074
    ---------- PlanningAgent ----------
    It seems we've missed some context there, so let's assign the subtasks again for clarity:
    
    Based on the search results, Dwyane Wade had the highest points for the Miami Heat in the 2006-2007 season with 1397 points.
    
    Now, let's find the necessary rebound statistics:
    
    2. WebSearchAgent: Find Dwyane Wade's total rebound statistics for both the 2007-2008 and 2008-2009 NBA seasons.
    3. DataAnalystAgent: Once the data is retrieved, calculate the percentage change in Dwyane Wade's total rebounds between the 2007-2008 and 2008-2009 seasons.
    ---------- WebSearchAgent ----------
    [FunctionCall(id='call_3i1wTDSjkGg6Ev8YKYWkZK55', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 NBA season"}', name='search_web_tool'), FunctionCall(id='call_NRAs6jHxXRi8zsvpW5WlHAaU', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 NBA season"}', name='search_web_tool')]
    ---------- WebSearchAgent ----------
    [FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', name='search_web_tool', call_id='call_3i1wTDSjkGg6Ev8YKYWkZK55', is_error=False), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', name='search_web_tool', call_id='call_NRAs6jHxXRi8zsvpW5WlHAaU', is_error=False)]
    ---------- WebSearchAgent ----------
    The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.
    The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.
    ---------- PlanningAgent ----------
    The total rebounds for Dwyane Wade in the 2007-2008 season were 214, and in the 2008-2009 season, they were 398.
    
    Now, let's calculate the percentage change.
    
    3. DataAnalystAgent: Calculate the percentage change in Dwyane Wade's total rebounds from the 2007-2008 season to the 2008-2009 season.
    ---------- DataAnalystAgent ----------
    [FunctionCall(id='call_XECA7ezz7VIKbf8IbZYSCSpI', arguments='{"start":214,"end":398}', name='percentage_change_tool')]
    ---------- DataAnalystAgent ----------
    [FunctionExecutionResult(content='85.98130841121495', name='percentage_change_tool', call_id='call_XECA7ezz7VIKbf8IbZYSCSpI', is_error=False)]
    ---------- DataAnalystAgent ----------
    85.98130841121495
    ---------- PlanningAgent ----------
    The Miami Heat player with the highest points in the 2006-2007 season was Dwyane Wade, with 1397 points. The percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons was approximately 85.98%.
    
    TERMINATE
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?', type='TextMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=161, completion_tokens=169), metadata={}, content="To answer this question, we'll break it down into two main subtasks:\n\n1. Identify the Miami Heat player with the highest points in the 2006-2007 season.\n2. Calculate the percentage change in that player's total rebounds between the 2007-2008 and 2008-2009 seasons.\n\nLet's assign these tasks:\n\n1. WebSearchAgent: Search for the Miami Heat player with the highest points in the 2006-2007 NBA season.\n2. WebSearchAgent: Find the total rebound statistics for that identified player for both the 2007-2008 and 2008-2009 NBA seasons.\n3. DataAnalystAgent: Calculate the percentage change in the player's total rebounds between the 2007-2008 and 2008-2009 seasons once the data is retrieved.", type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=324, completion_tokens=28), metadata={}, content=[FunctionCall(id='call_WtR5KTfEIxs3jIO25gjAw7dF', arguments='{"query":"Miami Heat highest points scorer 2006-2007 NBA season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', name='search_web_tool', call_id='call_WtR5KTfEIxs3jIO25gjAw7dF', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, metadata={}, content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=390, completion_tokens=37), metadata={}, content=[FunctionCall(id='call_9HA3DEacUl4WuG2G2PtRkXAO', arguments='{"start": 432, "end": 527}', name='percentage_change_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='DataAnalystAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='21.99074074074074', name='percentage_change_tool', call_id='call_9HA3DEacUl4WuG2G2PtRkXAO', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='DataAnalystAgent', models_usage=None, metadata={}, content='21.99074074074074', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=413, completion_tokens=137), metadata={}, content="It seems we've missed some context there, so let's assign the subtasks again for clarity:\n\nBased on the search results, Dwyane Wade had the highest points for the Miami Heat in the 2006-2007 season with 1397 points.\n\nNow, let's find the necessary rebound statistics:\n\n2. WebSearchAgent: Find Dwyane Wade's total rebound statistics for both the 2007-2008 and 2008-2009 NBA seasons.\n3. DataAnalystAgent: Once the data is retrieved, calculate the percentage change in Dwyane Wade's total rebounds between the 2007-2008 and 2008-2009 seasons.", type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=576, completion_tokens=73), metadata={}, content=[FunctionCall(id='call_3i1wTDSjkGg6Ev8YKYWkZK55', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 NBA season"}', name='search_web_tool'), FunctionCall(id='call_NRAs6jHxXRi8zsvpW5WlHAaU', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 NBA season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', name='search_web_tool', call_id='call_3i1wTDSjkGg6Ev8YKYWkZK55', is_error=False), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', name='search_web_tool', call_id='call_NRAs6jHxXRi8zsvpW5WlHAaU', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, metadata={}, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.\nThe number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=612, completion_tokens=84), metadata={}, content="The total rebounds for Dwyane Wade in the 2007-2008 season were 214, and in the 2008-2009 season, they were 398.\n\nNow, let's calculate the percentage change.\n\n3. DataAnalystAgent: Calculate the percentage change in Dwyane Wade's total rebounds from the 2007-2008 season to the 2008-2009 season.", type='TextMessage'), ToolCallRequestEvent(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=720, completion_tokens=21), metadata={}, content=[FunctionCall(id='call_XECA7ezz7VIKbf8IbZYSCSpI', arguments='{"start":214,"end":398}', name='percentage_change_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='DataAnalystAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='85.98130841121495', name='percentage_change_tool', call_id='call_XECA7ezz7VIKbf8IbZYSCSpI', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='DataAnalystAgent', models_usage=None, metadata={}, content='85.98130841121495', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=718, completion_tokens=63), metadata={}, content='The Miami Heat player with the highest points in the 2006-2007 season was Dwyane Wade, with 1397 points. The percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons was approximately 85.98%.\n\nTERMINATE', type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
    

您可以从对话日志中看到，一旦 Web 搜索代理和数据分析代理轮流发言后，规划代理会回到对话中，如果发现任务未按预期完成，它会再次调用 WebSearchAgent 获取篮板值，然后调用 DataAnalystAgent 获取百分比变化。

## 用户反馈#

我们可以将 [`UserProxyAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent") 添加到团队中，以便在运行期间提供用户反馈。有关 [`UserProxyAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent") 的更多详细信息，请参阅 [人机协同](tutorial/human-in-the-loop.html)。

要在 Web 搜索示例中使用 [`UserProxyAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent")，我们只需将其添加到团队中，并更新选择函数以在规划代理发言后始终检查用户反馈。如果用户响应 `"APPROVE"`，对话继续；否则，规划代理重试，直到用户批准。
    
    
    user_proxy_agent = UserProxyAgent("UserProxyAgent", description="用于批准或拒绝任务的用户的代理。")
    
    
    def selector_func_with_user_proxy(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
        if messages[-1].source != planning_agent.name and messages[-1].source != user_proxy_agent.name:
            # 当给定新任务或检查进度时，规划代理应首先参与。
            return planning_agent.name
        if messages[-1].source == planning_agent.name:
            if messages[-2].source == user_proxy_agent.name and "APPROVE" in messages[-1].content.upper():  # type: ignore
                # 用户已批准计划，继续到下一个代理。
                return None
            # 使用用户代理获取用户的批准以继续。
            return user_proxy_agent.name
        if messages[-1].source == user_proxy_agent.name:
            # 如果用户不批准，则返回规划代理。
            if "APPROVE" not in messages[-1].content.upper():  # type: ignore
                return planning_agent.name
        return None
    
    
    # 重置之前的代理并使用用户代理和选择函数再次运行聊天。
    await team.reset()
    team = SelectorGroupChat(
        [planning_agent, web_search_agent, data_analyst_agent, user_proxy_agent],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        selector_func=selector_func_with_user_proxy,
        allow_repeated_speaker=True,
    )
    
    await Console(team.run_stream(task=task))
    
    
    
    ---------- user ----------
    Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
    
    
    
    ---------- PlanningAgent ----------
    To address the user's query, we will need to perform the following tasks:
    
    1. Identify the Miami Heat player with the highest points in the 2006-2007 season.
    2. Find the total rebounds for that player in the 2007-2008 season.
    3. Find the total rebounds for that player in the 2008-2009 season.
    4. Calculate the percentage change in the total rebounds between the 2007-2008 and 2008-2009 seasons.
    
    Let's assign these tasks:
    
    1. **WebSearchAgent**: Identify the Miami Heat player with the highest points in the 2006-2007 season.
       
    (Task 2 and 3 depend on the result of Task 1. We'll proceed with Tasks 2 and 3 once Task 1 is complete.)
    ---------- UserProxyAgent ----------
    approve
    ---------- WebSearchAgent ----------
    [FunctionCall(id='call_0prr3fUnG5CtisUG7QeygW0w', arguments='{"query":"Miami Heat highest points scorer 2006-2007 NBA season"}', name='search_web_tool')]
    ---------- WebSearchAgent ----------
    [FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', call_id='call_0prr3fUnG5CtisUG7QeygW0w')]
    ---------- WebSearchAgent ----------
    Here are the total points scored by Miami Heat players in the 2006-2007 season:
            Udonis Haslem: 844 points
            Dwayne Wade: 1397 points
            James Posey: 550 points
            ...
            
    ---------- PlanningAgent ----------
    Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring 1397 points.
    
    Next, we need to find Dwyane Wade's total rebounds for the 2007-2008 and 2008-2009 seasons:
    
    2. **WebSearchAgent**: Find Dwyane Wade's total rebounds for the 2007-2008 season.
    3. **WebSearchAgent**: Find Dwyane Wade's total rebounds for the 2008-2009 season.
    ---------- UserProxyAgent ----------
    approve
    ---------- WebSearchAgent ----------
    [FunctionCall(id='call_fBZe80NaBfruOVGwRWbhXyRm', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 NBA season"}', name='search_web_tool'), FunctionCall(id='call_cURYibna4fGxySiL7IYt0c3s', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 NBA season"}', name='search_web_tool')]
    ---------- WebSearchAgent ----------
    [FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_fBZe80NaBfruOVGwRWbhXyRm'), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_cURYibna4fGxySiL7IYt0c3s')]
    ---------- WebSearchAgent ----------
    The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.
    The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.
    ---------- PlanningAgent ----------
    Now that we have Dwyane Wade's total rebounds for both seasons, we can calculate the percentage change:
    
    4. **DataAnalystAgent**: Calculate the percentage change in Dwyane Wade's total rebounds from the 2007-2008 season (214 rebounds) to the 2008-2009 season (398 rebounds).
    ---------- UserProxyAgent ----------
    approve
    ---------- DataAnalystAgent ----------
    [FunctionCall(id='call_z3uog7t2x0z1Suzl5hACF9hY', arguments='{"start":214,"end":398}', name='percentage_change_tool')]
    ---------- DataAnalystAgent ----------
    [FunctionExecutionResult(content='85.98130841121495', call_id='call_z3uog7t2x0z1Suzl5hACF9hY')]
    ---------- DataAnalystAgent ----------
    85.98130841121495
    ---------- PlanningAgent ----------
    Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring 1397 points. His total rebounds increased from 214 in the 2007-2008 season to 398 in the 2008-2009 season, which is a percentage change of approximately 85.98%.
    
    TERMINATE
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?', type='TextMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=161, completion_tokens=166), content="To address the user's query, we will need to perform the following tasks:\n\n1. Identify the Miami Heat player with the highest points in the 2006-2007 season.\n2. Find the total rebounds for that player in the 2007-2008 season.\n3. Find the total rebounds for that player in the 2008-2009 season.\n4. Calculate the percentage change in the total rebounds between the 2007-2008 and 2008-2009 seasons.\n\nLet's assign these tasks:\n\n1. **WebSearchAgent**: Identify the Miami Heat player with the highest points in the 2006-2007 season.\n   \n(Task 2 and 3 depend on the result of Task 1. We'll proceed with Tasks 2 and 3 once Task 1 is complete.)", type='TextMessage'), UserInputRequestedEvent(source='UserProxyAgent', models_usage=None, request_id='2a433f88-f886-4b39-a078-ea1acdcb2f9d', content='', type='UserInputRequestedEvent'), TextMessage(source='UserProxyAgent', models_usage=None, content='approve', type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=323, completion_tokens=28), content=[FunctionCall(id='call_0prr3fUnG5CtisUG7QeygW0w', arguments='{"query":"Miami Heat highest points scorer 2006-2007 NBA season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, content=[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', call_id='call_0prr3fUnG5CtisUG7QeygW0w')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=403, completion_tokens=112), content="Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring 1397 points.\n\nNext, we need to find Dwyane Wade's total rebounds for the 2007-2008 and 2008-2009 seasons:\n\n2. **WebSearchAgent**: Find Dwyane Wade's total rebounds for the 2007-2008 season.\n3. **WebSearchAgent**: Find Dwyane Wade's total rebounds for the 2008-2009 season.", type='TextMessage'), UserInputRequestedEvent(source='UserProxyAgent', models_usage=None, request_id='23dd4570-2391-41e9-aeea-86598499792c', content='', type='UserInputRequestedEvent'), TextMessage(source='UserProxyAgent', models_usage=None, content='approve', type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=543, completion_tokens=73), content=[FunctionCall(id='call_fBZe80NaBfruOVGwRWbhXyRm', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 NBA season"}', name='search_web_tool'), FunctionCall(id='call_cURYibna4fGxySiL7IYt0c3s', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 NBA season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, content=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_fBZe80NaBfruOVGwRWbhXyRm'), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_cURYibna4fGxySiL7IYt0c3s')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.\nThe number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=586, completion_tokens=70), content="Now that we have Dwyane Wade's total rebounds for both seasons, we can calculate the percentage change:\n\n4. **DataAnalystAgent**: Calculate the percentage change in Dwyane Wade's total rebounds from the 2007-2008 season (214 rebounds) to the 2008-2009 season (398 rebounds).", type='TextMessage'), UserInputRequestedEvent(source='UserProxyAgent', models_usage=None, request_id='e849d193-4ab3-4558-8560-7dbc062a0aee', content='', type='UserInputRequestedEvent'), TextMessage(source='UserProxyAgent', models_usage=None, content='approve', type='TextMessage'), ToolCallRequestEvent(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=655, completion_tokens=21), content=[FunctionCall(id='call_z3uog7t2x0z1Suzl5hACF9hY', arguments='{"start":214,"end":398}', name='percentage_change_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='DataAnalystAgent', models_usage=None, content=[FunctionExecutionResult(content='85.98130841121495', call_id='call_z3uog7t2x0z1Suzl5hACF9hY')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='DataAnalystAgent', models_usage=None, content='85.98130841121495', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=687, completion_tokens=74), content='Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring 1397 points. His total rebounds increased from 214 in the 2007-2008 season to 398 in the 2008-2009 season, which is a percentage change of approximately 85.98%.\n\nTERMINATE', type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
    

现在，用户的反馈已纳入对话流程，用户可以批准或拒绝规划代理的决策。

## 使用推理模型#

到目前为止，在示例中，我们使用了 `gpt-4o` 模型。像 `gpt-4o` 和 `gemini-1.5-flash` 这样的模型非常擅长遵循指令，因此您可以在团队的选择器提示词和每个代理的系统消息中包含相对详细的指令，以指导其行为。

但是，如果您使用的是像 `o3-mini` 这样的推理模型，则需要使选择器提示词和系统消息尽可能简单明了。这是因为推理模型已经擅长根据提供给它们的上下文自行制定指令。

这也意味着我们不再需要规划代理来分解任务，因为使用推理模型的 [`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 可以自行完成。

在以下示例中，我们将使用 `o3-mini` 作为代理和团队的模型，并且不使用规划代理。此外，我们保持选择器提示词和系统消息尽可能简单。
    
    
    model_client = OpenAIChatCompletionClient(model="o3-mini")
    
    web_search_agent = AssistantAgent(
        "WebSearchAgent",
        description="用于在 Web 上搜索信息的代理。",
        tools=[search_web_tool],
        model_client=model_client,
        system_message="""使用 Web 搜索工具查找信息。""",
    )
    
    data_analyst_agent = AssistantAgent(
        "DataAnalystAgent",
        description="用于执行计算的代理。",
        model_client=model_client,
        tools=[percentage_change_tool],
        system_message="""使用工具进行计算。如果您尚未看到数据，请索取数据。""",
    )
    
    user_proxy_agent = UserProxyAgent(
        "UserProxyAgent",
        description="用于批准或拒绝任务的用户。",
    )
    
    selector_prompt = """选择一个代理来执行任务。

{roles}

当前对话上下文：
{history}

阅读以上对话，然后从 {participants} 中选择一个代理来执行下一个任务。
当任务完成时，让用户批准或拒绝任务。
"""
    
    team = SelectorGroupChat(
        [web_search_agent, data_analyst_agent, user_proxy_agent],
        model_client=model_client,
        termination_condition=termination,  # 使用与之前相同的终止条件。
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True,
    )
    
    
    
    await Console(team.run_stream(task=task))
    
    
    
    ---------- user ----------
    Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
    ---------- WebSearchAgent ----------
    [FunctionCall(id='call_hl7EP6Lp5jj5wEdxeNHTwUVG', arguments='{"query": "Who was the Miami Heat player with the highest points in the 2006-2007 season Miami Heat statistics Dwyane Wade rebounds percentage change 2007-2008 2008-2009 seasons"}', name='search_web_tool')]
    ---------- WebSearchAgent ----------
    [FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', call_id='call_hl7EP6Lp5jj5wEdxeNHTwUVG', is_error=False)]
    ---------- WebSearchAgent ----------
    Here are the total points scored by Miami Heat players in the 2006-2007 season:
            Udonis Haslem: 844 points
            Dwayne Wade: 1397 points
            James Posey: 550 points
            ...
            
    ---------- DataAnalystAgent ----------
    I found that in the 2006–2007 season the player with the highest points was Dwyane Wade (with 1,397 points). Could you please provide Dwyane Wade's total rebounds for the 2007–2008 and the 2008–2009 seasons so I can calculate the percentage change?
    ---------- WebSearchAgent ----------
    [FunctionCall(id='call_lppGTILXDvO9waPwKO66ehK6', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 and 2008-2009 seasons for Miami Heat"}', name='search_web_tool')]
    ---------- WebSearchAgent ----------
    [FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_lppGTILXDvO9waPwKO66ehK6', is_error=False)]
    ---------- WebSearchAgent ----------
    The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.
    ---------- DataAnalystAgent ----------
    Could you please provide Dwyane Wade's total rebounds in the 2008-2009 season?
    ---------- WebSearchAgent ----------
    [FunctionCall(id='call_r8DBcbJtQfdtugLtyTrqOvoK', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 season Miami Heat"}', name='search_web_tool')]
    ---------- WebSearchAgent ----------
    [FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_r8DBcbJtQfdtugLtyTrqOvoK', is_error=False)]
    ---------- WebSearchAgent ----------
    The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.
    ---------- DataAnalystAgent ----------
    [FunctionCall(id='call_4jejv1wM7V1osbBCxJze8aQM', arguments='{"start": 214, "end": 398}', name='percentage_change_tool')]
    ---------- DataAnalystAgent ----------
    [FunctionExecutionResult(content='85.98130841121495', call_id='call_4jejv1wM7V1osbBCxJze8aQM', is_error=False)]
    ---------- DataAnalystAgent ----------
    85.98130841121495
    ---------- DataAnalystAgent ----------
    Dwyane Wade was the Miami Heat player with the highest total points (1,397) during the 2006-2007 season. His total rebounds increased by approximately 86% from 214 in the 2007-2008 season to 398 in the 2008-2009 season.
    ---------- UserProxyAgent ----------
    Approve. TERMINATE
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?', type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=103, completion_tokens=384), content=[FunctionCall(id='call_hl7EP6Lp5jj5wEdxeNHTwUVG', arguments='{"query": "Who was the Miami Heat player with the highest points in the 2006-2007 season Miami Heat statistics Dwyane Wade rebounds percentage change 2007-2008 2008-2009 seasons"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, content=[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', call_id='call_hl7EP6Lp5jj5wEdxeNHTwUVG', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', type='ToolCallSummaryMessage'), TextMessage(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=183, completion_tokens=1038), content='I found that in the 2006–2007 season the player with the highest points was Dwyane Wade (with 1,397 points). Could you please provide Dwyane Wade's total rebounds for the 2007–2008 and the 2008–2009 seasons so I can calculate the percentage change?', type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=299, completion_tokens=109), content=[FunctionCall(id='call_lppGTILXDvO9waPwKO66ehK6', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 and 2008-2009 seasons for Miami Heat"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, content=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_lppGTILXDvO9waPwKO66ehK6', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', type='ToolCallSummaryMessage'), TextMessage(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=291, completion_tokens=224), content='Could you please provide Dwyane Wade's total rebounds in the 2008-2009 season?', type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=401, completion_tokens=37), content=[FunctionCall(id='call_r8DBcbJtQfdtugLtyTrqOvoK', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 season Miami Heat"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, content=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_r8DBcbJtQfdtugLtyTrqOvoK', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=353, completion_tokens=158), content=[FunctionCall(id='call_4jejv1wM7V1osbBCxJze8aQM', arguments='{"start": 214, "end": 398}', name='percentage_change_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='DataAnalystAgent', models_usage=None, content=[FunctionExecutionResult(content='85.98130841121495', call_id='call_4jejv1wM7V1osbBCxJze8aQM', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='DataAnalystAgent', models_usage=None, content='85.98130841121495', type='ToolCallSummaryMessage'), TextMessage(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=394, completion_tokens=138), content='Dwyane Wade was the Miami Heat player with the highest total points (1,397) during the 2006-2007 season. His total rebounds increased by approximately 86% from 214 in the 2007-2008 season to 398 in the 2008-2009 season.', type='TextMessage'), UserInputRequestedEvent(source='UserProxyAgent', models_usage=None, request_id='b3b05408-73fc-47d4-b832-16c9f447cd6e', content='', type='UserInputRequestedEvent'), TextMessage(source='UserProxyAgent', models_usage=None, content='Approve. TERMINATE', type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
    

提示

有关如何提示推理模型的更多指导，请参阅 Azure AI 服务博客关于 [OpenAI O1 和 O3-mini 推理模型的提示工程](https://techcommunity.microsoft.com/blog/azure-ai-services-blog/prompt-engineering-for-openai%E2%80%99s-o1-and-o3-mini-reasoning-models/4374010)

__本页内容

[ __在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/selector-group-chat.ipynb)

[ __显示源代码](../../_sources/user-guide/agentchat-user-guide/selector-group-chat.ipynb.txt)
