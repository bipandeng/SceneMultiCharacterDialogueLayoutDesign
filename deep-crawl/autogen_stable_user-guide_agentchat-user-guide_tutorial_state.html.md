<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/state.html -->

# 管理状态#

到目前为止，我们已经讨论了如何在多代理应用程序中构建组件——代理、团队、终止条件。在许多情况下，将这些组件的状态保存到磁盘并在以后重新加载是很有用的。这在 Web 应用程序中特别有用，因为无状态端点需要响应请求并从持久存储中加载应用程序状态。

在本笔记本中，我们将讨论如何保存和加载代理、团队和终止条件的状态。

## 保存和加载代理#

我们可以通过调用 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 上的 [`save_state()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent.save_state "autogen_agentchat.agents.AssistantAgent.save_state") 方法来获取代理的状态。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import MaxMessageTermination
    from autogen_agentchat.messages import TextMessage
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.ui import Console
    from autogen_core import CancellationToken
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    model_client = OpenAIChatCompletionClient(model="gpt-4o-2024-08-06")
    
    assistant_agent = AssistantAgent(
        name="assistant_agent",
        system_message="You are a helpful assistant",
        model_client=model_client,
    )
    
    # 在脚本中运行时使用 asyncio.run(...)。
    response = await assistant_agent.on_messages(
        [TextMessage(content="Write a 3 line poem on lake tangayika", source="user")], CancellationToken()
    )
    print(response.chat_message)
    await model_client.close()
    
    
    
    In Tanganyika's embrace so wide and deep,  
    Ancient waters cradle secrets they keep,  
    Echoes of time where horizons sleep.  
    
    
    
    agent_state = await assistant_agent.save_state()
    print(agent_state)
    
    
    
    {'type': 'AssistantAgentState', 'version': '1.0.0', 'llm_messages': [{'content': 'Write a 3 line poem on lake tangayika', 'source': 'user', 'type': 'UserMessage'}, {'content': "In Tanganyika's embrace so wide and deep,  \nAncient waters cradle secrets they keep,  \nEchoes of time where horizons sleep.  ", 'source': 'assistant_agent', 'type': 'AssistantMessage'}]}
    
    
    
    model_client = OpenAIChatCompletionClient(model="gpt-4o-2024-08-06")
    
    new_assistant_agent = AssistantAgent(
        name="assistant_agent",
        system_message="You are a helpful assistant",
        model_client=model_client,
    )
    await new_assistant_agent.load_state(agent_state)
    
    # 在脚本中运行时使用 asyncio.run(...)。
    response = await new_assistant_agent.on_messages(
        [TextMessage(content="What was the last line of the previous poem you wrote", source="user")], CancellationToken()
    )
    print(response.chat_message)
    await model_client.close()
    
    
    
    The last line of the poem was: "Echoes of time where horizons sleep."
    

注意

对于 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent")，其状态由 model_context 组成。如果您编写自己的自定义代理，可以考虑重写 [`save_state()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.save_state "autogen_agentchat.agents.BaseChatAgent.save_state") 和 [`load_state()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.load_state "autogen_agentchat.agents.BaseChatAgent.load_state") 方法以自定义行为。默认实现保存和加载空状态。

## 保存和加载团队#

我们可以通过调用团队上的 `save_state` 方法来获取团队的状态，并通过调用团队上的 `load_state` 方法重新加载它。

当我们调用团队上的 `save_state` 时，它会保存团队中所有代理的状态。

我们将首先创建一个简单的 [`RoundRobinGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 团队，其中包含一个代理，并要求其写一首诗。
    
    
    model_client = OpenAIChatCompletionClient(model="gpt-4o-2024-08-06")
    
    # 定义一个团队。
    assistant_agent = AssistantAgent(
        name="assistant_agent",
        system_message="You are a helpful assistant",
        model_client=model_client,
    )
    agent_team = RoundRobinGroupChat([assistant_agent], termination_condition=MaxMessageTermination(max_messages=2))
    
    # 运行团队并将消息流式传输到控制台。
    stream = agent_team.run_stream(task="Write a beautiful poem 3-line about lake tangayika")
    
    # 在脚本中运行时使用 asyncio.run(...)。
    await Console(stream)
    
    # 保存代理团队的状态。
    team_state = await agent_team.save_state()
    
    
    
    ---------- user ----------
    Write a beautiful poem 3-line about lake tangayika
    ---------- assistant_agent ----------
    In Tanganyika's gleam, beneath the azure skies,  
    Whispers of ancient waters, in tranquil guise,  
    Nature's mirror, where dreams and serenity lie.
    [Prompt tokens: 29, Completion tokens: 34]
    ---------- Summary ----------
    Number of messages: 2
    Finish reason: Maximum number of messages 2 reached, current message count: 2
    Total prompt tokens: 29
    Total completion tokens: 34
    Duration: 0.71 seconds
    

如果我们重置团队（模拟实例化团队），并提问 `What was the last line of the poem you wrote?`，我们会发现团队无法完成此任务，因为没有对先前运行的引用。
    
    
    await agent_team.reset()
    stream = agent_team.run_stream(task="What was the last line of the poem you wrote?")
    await Console(stream)
    
    
    
    ---------- user ----------
    What was the last line of the poem you wrote?
    ---------- assistant_agent ----------
    I'm sorry, but I am unable to recall or access previous interactions, including any specific poem I may have composed in our past conversations. If you like, I can write a new poem for you.
    [Prompt tokens: 28, Completion tokens: 40]
    ---------- Summary ----------
    Number of messages: 2
    Finish reason: Maximum number of messages 2 reached, current message count: 2
    Total prompt tokens: 28
    Total completion tokens: 40
    Duration: 0.70 seconds
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='What was the last line of the poem you wrote?', type='TextMessage'), TextMessage(source='assistant_agent', models_usage=RequestUsage(prompt_tokens=28, completion_tokens=40), content="I'm sorry, but I am unable to recall or access previous interactions, including any specific poem I may have composed in our past conversations. If you like, I can write a new poem for you.", type='TextMessage')], stop_reason='Maximum number of messages 2 reached, current message count: 2')
    

接下来，我们加载团队的状态并提出相同的问题。我们会发现团队能够准确返回其写的诗的最后一行。
    
    
    print(team_state)
    
    # 加载团队状态。
    await agent_team.load_state(team_state)
    stream = agent_team.run_stream(task="What was the last line of the poem you wrote?")
    await Console(stream)
    
    
    
    {'type': 'TeamState', 'version': '1.0.0', 'agent_states': {'group_chat_manager/a55364ad-86fd-46ab-9449-dcb5260b1e06': {'type': 'RoundRobinManagerState', 'version': '1.0.0', 'message_thread': [{'source': 'user', 'models_usage': None, 'content': 'Write a beautiful poem 3-line about lake tangayika', 'type': 'TextMessage'}, {'source': 'assistant_agent', 'models_usage': {'prompt_tokens': 29, 'completion_tokens': 34}, 'content': "In Tanganyika's gleam, beneath the azure skies,  \nWhispers of ancient waters, in tranquil guise,  \nNature's mirror, where dreams and serenity lie.", 'type': 'TextMessage'}], 'current_turn': 0, 'next_speaker_index': 0}, 'collect_output_messages/a55364ad-86fd-46ab-9449-dcb5260b1e06': {}, 'assistant_agent/a55364ad-86fd-46ab-9449-dcb5260b1e06': {'type': 'ChatAgentContainerState', 'version': '1.0.0', 'agent_state': {'type': 'AssistantAgentState', 'version': '1.0.0', 'llm_messages': [{'content': 'Write a beautiful poem 3-line about lake tangayika', 'source': 'user', 'type': 'UserMessage'}, {'content': "In Tanganyika's gleam, beneath the azure skies,  \nWhispers of ancient waters, in tranquil guise,  \nNature's mirror, where dreams and serenity lie.", 'source': 'assistant_agent', 'type': 'AssistantMessage'}]}, 'message_buffer': []}}, 'team_id': 'a55364ad-86fd-46ab-9449-dcb5260b1e06'}
    ---------- user ----------
    What was the last line of the poem you wrote?
    ---------- assistant_agent ----------
    The last line of the poem I wrote is:  
    "Nature's mirror, where dreams and serenity lie."
    [Prompt tokens: 86, Completion tokens: 22]
    ---------- Summary ----------
    Number of messages: 2
    Finish reason: Maximum number of messages 2 reached, current message count: 2
    Total prompt tokens: 86
    Total completion tokens: 22
    Duration: 0.96 seconds
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='What was the last line of the poem you wrote?', type='TextMessage'), TextMessage(source='assistant_agent', models_usage=RequestUsage(prompt_tokens=86, completion_tokens=22), content='The last line of the poem I wrote is:  \n"Nature\'s mirror, where dreams and serenity lie."', type='TextMessage')], stop_reason='Maximum number of messages 2 reached, current message count: 2')
    

## 持久化状态（文件或数据库）#

在许多情况下，我们可能希望将团队的状态持久化到磁盘（或数据库）并在以后重新加载。状态是一个字典，可以序列化到文件或写入数据库。
    
    
    import json
    
    ## 保存状态到磁盘
    
    with open("coding/team_state.json", "w") as f:
        json.dump(team_state, f)
    
    ## 从磁盘加载状态
    with open("coding/team_state.json", "r") as f:
        team_state = json.load(f)
    
    new_agent_team = RoundRobinGroupChat([assistant_agent], termination_condition=MaxMessageTermination(max_messages=2))
    await new_agent_team.load_state(team_state)
    stream = new_agent_team.run_stream(task="What was the last line of the poem you wrote?")
    await Console(stream)
    await model_client.close()
    
    
    
    ---------- user ----------
    What was the last line of the poem you wrote?
    ---------- assistant_agent ----------
    The last line of the poem I wrote is:  
    "Nature's mirror, where dreams and serenity lie."
    [Prompt tokens: 86, Completion tokens: 22]
    ---------- Summary ----------
    Number of messages: 2
    Finish reason: Maximum number of messages 2 reached, current message count: 2
    Total prompt tokens: 86
    Total completion tokens: 22
    Duration: 0.72 seconds
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='What was the last line of the poem you wrote?', type='TextMessage'), TextMessage(source='assistant_agent', models_usage=RequestUsage(prompt_tokens=86, completion_tokens=22), content='The last line of the poem I wrote is:  \n"Nature\'s mirror, where dreams and serenity lie."', type='TextMessage')], stop_reason='Maximum number of messages 2 reached, current message count: 2')
    

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/tutorial/state.ipynb)

[ __Show Source](../../../_sources/user-guide/agentchat-user-guide/tutorial/state.ipynb.txt)
