<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/graph-flow.html -->

# GraphFlow (Workflows)#

在本节中，你将学习如何使用 [`GraphFlow`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.GraphFlow "autogen_agentchat.teams.GraphFlow") 创建 _多代理工作流_（简称"flow"）。它使用结构化执行并精确控制代理之间的交互以完成任务。

我们将首先向你展示如何创建和运行一个 flow。然后，我们将解释如何观察和调试 flow 行为，并讨论用于管理执行的重要操作。

AutoGen AgentChat 为有向图执行提供了一个团队：

  * [`GraphFlow`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.GraphFlow "autogen_agentchat.teams.GraphFlow")：遵循 [`DiGraph`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.DiGraph "autogen_agentchat.teams.DiGraph") 来控制代理之间执行流程的团队。支持顺序、并行、条件分支和循环行为。

Note

**什么时候应该使用[` GraphFlow`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.GraphFlow "autogen_agentchat.teams.GraphFlow")？**

当你需要对代理执行顺序进行严格控制，或者不同的结果必须导致不同的下一步时，请使用 Graph。如果临时对话流程足够，请从简单的团队开始，例如 [`RoundRobinGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 或 [`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat")。当你的任务需要确定性控制、条件分支或处理具有循环的复杂多步流程时，再过渡到结构化工作流。

> **Warning:** [`GraphFlow`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.GraphFlow "autogen_agentchat.teams.GraphFlow") 是一个 **实验性功能**。其 API、行为和功能在未来版本中 **可能会发生变化**。

## Creating and Running a Flow#

[`DiGraphBuilder`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.DiGraphBuilder "autogen_agentchat.teams.DiGraphBuilder") 是一个流畅的实用程序，可让你轻松构建工作流的执行图。它支持构建：

  * 顺序链

  * 并行扇出

  * 条件分支

  * 具有安全退出条件的循环

图中的每个节点代表一个代理，边定义允许的执行路径。边可以可选地具有基于代理消息的条件。

### Sequential Flow#

我们将首先创建一个简单的工作流，其中 **writer** 起草一个段落，**reviewer** 提供反馈。在 reviewer 评论完 writer 后，此图终止。

请注意，flow 会自动计算图的所有源节点和叶节点，执行从图中的所有源节点开始，当没有剩余节点可执行时完成执行。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    # Create an OpenAI model client
    client = OpenAIChatCompletionClient(model="gpt-4.1-nano")
    
    # Create the writer agent
    writer = AssistantAgent("writer", model_client=client, system_message="Draft a short paragraph on climate change.")
    
    # Create the reviewer agent
    reviewer = AssistantAgent("reviewer", model_client=client, system_message="Review the draft and suggest improvements.")
    
    # Build the graph
    builder = DiGraphBuilder()
    builder.add_node(writer).add_node(reviewer)
    builder.add_edge(writer, reviewer)
    
    # Build and validate the graph
    graph = builder.build()
    
    # Create the flow
    flow = GraphFlow([writer, reviewer], graph=graph)
    
    
    
    # Use `asyncio.run(...)` and wrap the below in a async function when running in a script.
    stream = flow.run_stream(task="Write a short paragraph about climate change.")
    async for event in stream:  # type: ignore
        print(event)
    # Use Console(flow.run_stream(...)) for better formatting in console.
    
    
    
    source='user' models_usage=None metadata={} content='Write a short paragraph about climate change.' type='TextMessage'
    source='writer' models_usage=RequestUsage(prompt_tokens=28, completion_tokens=95) metadata={} content='Climate change refers to long-term shifts in temperature, precipitation, and other atmospheric patterns, largely driven by human activities such as burning fossil fuels, deforestation, and industrial processes. These changes contribute to rising global temperatures, melting ice caps, more frequent and severe weather events, and adverse impacts on ecosystems and human communities. Addressing climate change requires global cooperation to reduce greenhouse gas emissions, transition to renewable energy sources, and implement sustainable practices to protect the planet for future generations.' type='TextMessage'
    source='reviewer' models_usage=RequestUsage(prompt_tokens=127, completion_tokens=144) metadata={} content="The paragraph provides a clear overview of climate change, its causes, and its impacts. To enhance clarity and engagement, consider adding specific examples or emphasizing the urgency of action. Here's a revised version:\n\nClimate change is a long-term alteration of Earth's climate patterns caused primarily by human activities such as burning fossil fuels, deforestation, and industrial emissions. These actions increase greenhouse gases in the atmosphere, leading to rising global temperatures, melting ice caps, and more frequent extreme weather events like hurricanes and droughts. The effects threaten ecosystems, disrupt agriculture, and endanger communities worldwide. Addressing this crisis requires urgent, coordinated global efforts to reduce emissions, adopt renewable energy, and promote sustainable practices to safeguard the planet for future generations." type='TextMessage'
    source='DiGraphStopAgent' models_usage=None metadata={} content='Digraph execution is complete' type='StopMessage'
    messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Write a short paragraph about climate change.', type='TextMessage'), TextMessage(source='writer', models_usage=RequestUsage(prompt_tokens=28, completion_tokens=95), metadata={}, content='Climate change refers to long-term shifts in temperature, precipitation, and other atmospheric patterns, largely driven by human activities such as burning fossil fuels, deforestation, and industrial processes. These changes contribute to rising global temperatures, melting ice caps, more frequent and severe weather events, and adverse impacts on ecosystems and human communities. Addressing climate change requires global cooperation to reduce greenhouse gas emissions, transition to renewable energy sources, and implement sustainable practices to protect the planet for future generations.', type='TextMessage'), TextMessage(source='reviewer', models_usage=RequestUsage(prompt_tokens=127, completion_tokens=144), metadata={}, content="The paragraph provides a clear overview of climate change, its causes, and its impacts. To enhance clarity and engagement, consider adding specific examples or emphasizing the urgency of action. Here's a revised version:\n\nClimate change is a long-term alteration of Earth's climate patterns caused primarily by human activities such as burning fossil fuels, deforestation, and industrial emissions. These actions increase greenhouse gases in the atmosphere, leading to rising global temperatures, melting ice caps, and more frequent extreme weather events like hurricanes and droughts. The effects threaten ecosystems, disrupt agriculture, and endanger communities worldwide. Addressing this crisis requires urgent, coordinated global efforts to reduce emissions, adopt renewable energy, and promote sustainable practices to safeguard the planet for future generations.", type='TextMessage'), StopMessage(source='DiGraphStopAgent', models_usage=None, metadata={}, content='Digraph execution is complete', type='StopMessage')] stop_reason='Stop message received'
    

### Parallel Flow with Join#

我们现在创建一个稍微复杂一点的 flow：

  * 一个 **writer** 起草一个段落。

  * 两个 **editors** 独立编辑语法和风格（并行扇出）。

  * 一个 **final reviewer** 整合他们的编辑（合并）。

执行从 **writer** 开始，同时扇出到 **editor1** 和 **editor2**，然后两者都输入到 **final reviewer**。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    # Create an OpenAI model client
    client = OpenAIChatCompletionClient(model="gpt-4.1-nano")
    
    # Create the writer agent
    writer = AssistantAgent("writer", model_client=client, system_message="Draft a short paragraph on climate change.")
    
    # Create two editor agents
    editor1 = AssistantAgent("editor1", model_client=client, system_message="Edit the paragraph for grammar.")
    
    editor2 = AssistantAgent("editor2", model_client=client, system_message="Edit the paragraph for style.")
    
    # Create the final reviewer agent
    final_reviewer = AssistantAgent(
        "final_reviewer",
        model_client=client,
        system_message="Consolidate the grammar and style edits into a final version.",
    )
    
    # Build the workflow graph
    builder = DiGraphBuilder()
    builder.add_node(writer).add_node(editor1).add_node(editor2).add_node(final_reviewer)
    
    # Fan-out from writer to editor1 and editor2
    builder.add_edge(writer, editor1)
    builder.add_edge(writer, editor2)
    
    # Fan-in both editors into final reviewer
    builder.add_edge(editor1, final_reviewer)
    builder.add_edge(editor2, final_reviewer)
    
    # Build and validate the graph
    graph = builder.build()
    
    # Create the flow
    flow = GraphFlow(
        participants=builder.get_participants(),
        graph=graph,
    )
    
    # Run the workflow
    await Console(flow.run_stream(task="Write a short paragraph about climate change."))
    
    
    
    ---------- TextMessage (user) ----------
    Write a short paragraph about climate change.
    ---------- TextMessage (writer) ----------
    Climate change refers to long-term shifts in weather patterns and global temperatures, largely driven by human activities such as burning fossil fuels, deforestation, and industrial processes. These activities increase concentrations of greenhouse gases like carbon dioxide and methane in the atmosphere, leading to global warming. The impacts of climate change include more frequent and severe weather events, rising sea levels, melting glaciers, and disruptions to ecosystems and agriculture. Addressing this urgent issue requires international cooperation, significant shifts toward renewable energy sources, and sustainable practices to reduce our carbon footprint and protect the planet for future generations.
    ---------- TextMessage (editor1) ----------
    Climate change refers to long-term shifts in weather patterns and global temperatures, largely driven by human activities such as burning fossil fuels, deforestation, and industrial processes. These activities increase concentrations of greenhouse gases like carbon dioxide and methane in the atmosphere, leading to global warming. The impacts of climate change include more frequent and severe weather events, rising sea levels, melting glaciers, and disruptions to ecosystems and agriculture. Addressing this urgent issue requires international cooperation, significant shifts toward renewable energy sources, and sustainable practices to reduce our carbon footprint and protect the planet for future generations.
    ---------- TextMessage (editor2) ----------
    Climate change involves long-term alterations in weather patterns and global temperatures, primarily caused by human activities like burning fossil fuels, deforestation, and industrial processes. These actions elevate levels of greenhouse gases such as carbon dioxide and methane, resulting in global warming. Its consequences are widespread, including more frequent and intense storms, rising sea levels, melting glaciers, and disturbances to ecosystems and agriculture. Combating this crisis demands international collaboration, a swift transition to renewable energy, and sustainable practices to cut carbon emissions, ensuring a healthier planet for future generations.
    ---------- TextMessage (final_reviewer) ----------
    Climate change involves long-term alterations in weather patterns and global temperatures, primarily caused by human activities such as burning fossil fuels, deforestation, and industrial processes. These actions increase levels of greenhouse gases like carbon dioxide and methane, leading to global warming. Its consequences include more frequent and intense storms, rising sea levels, melting glaciers, and disruptions to ecosystems and agriculture. Addressing this crisis requires international collaboration, a swift transition to renewable energy, and sustainable practices to reduce carbon emissions, ensuring a healthier planet for future generations.
    ---------- StopMessage (DiGraphStopAgent) ----------
    Digraph execution is complete
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Write a short paragraph about climate change.', type='TextMessage'), TextMessage(source='writer', models_usage=RequestUsage(prompt_tokens=28, completion_tokens=113), metadata={}, content='Climate change refers to long-term shifts in weather patterns and global temperatures, largely driven by human activities such as burning fossil fuels, deforestation, and industrial processes. These activities increase concentrations of greenhouse gases like carbon dioxide and methane in the atmosphere, leading to global warming. The impacts of climate change include more frequent and severe weather events, rising sea levels, melting glaciers, and disruptions to ecosystems and agriculture. Addressing this urgent issue requires international cooperation, significant shifts toward renewable energy sources, and sustainable practices to reduce our carbon footprint and protect the planet for future generations.', type='TextMessage'), TextMessage(source='editor1', models_usage=RequestUsage(prompt_tokens=144, completion_tokens=113), metadata={}, content='Climate change refers to long-term shifts in weather patterns and global temperatures, largely driven by human activities such as burning fossil fuels, deforestation, and industrial processes. These activities increase concentrations of greenhouse gases like carbon dioxide and methane in the atmosphere, leading to global warming. The impacts of climate change include more frequent and severe weather events, rising sea levels, melting glaciers, and disruptions to ecosystems and agriculture. Addressing this urgent issue requires international cooperation, significant shifts toward renewable energy sources, and sustainable practices to reduce our carbon footprint and protect the planet for future generations.', type='TextMessage'), TextMessage(source='editor2', models_usage=RequestUsage(prompt_tokens=263, completion_tokens=107), metadata={}, content='Climate change involves long-term alterations in weather patterns and global temperatures, primarily caused by human activities like burning fossil fuels, deforestation, and industrial processes. These actions elevate levels of greenhouse gases such as carbon dioxide and methane, resulting in global warming. Its consequences are widespread, including more frequent and intense storms, rising sea levels, melting glaciers, and disturbances to ecosystems and agriculture. Combating this crisis demands international collaboration, a swift transition to renewable energy, and sustainable practices to cut carbon emissions, ensuring a healthier planet for future generations.', type='TextMessage'), TextMessage(source='final_reviewer', models_usage=RequestUsage(prompt_tokens=383, completion_tokens=104), metadata={}, content='Climate change involves long-term alterations in weather patterns and global temperatures, primarily caused by human activities such as burning fossil fuels, deforestation, and industrial processes. These actions increase levels of greenhouse gases like carbon dioxide and methane, leading to global warming. Its consequences include more frequent and intense storms, rising sea levels, melting glaciers, and disruptions to ecosystems and agriculture. Addressing this crisis requires international collaboration, a swift transition to renewable energy, and sustainable practices to reduce carbon emissions, ensuring a healthier planet for future generations.', type='TextMessage'), StopMessage(source='DiGraphStopAgent', models_usage=None, metadata={}, content='Digraph execution is complete', type='StopMessage')], stop_reason='Stop message received')
    

## Message Filtering#

### Execution Graph vs. Message Graph#

在 [`GraphFlow`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.GraphFlow "autogen_agentchat.teams.GraphFlow") 中，**execution graph** 是使用 [`DiGraph`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.DiGraph "autogen_agentchat.teams.DiGraph") 定义的，它控制代理执行的顺序。但是，执行图不控制代理从其他代理接收哪些消息。默认情况下，所有消息都发送到图中的所有代理。

**Message filtering** 是一个单独的功能，它允许你过滤每个代理接收的消息，并将其模型上下文限制为仅相关信息。消息过滤器的集合定义了 flow 中的 **message graph**。

指定 message graph 有助于：

  * 减少幻觉

  * 控制内存负载

  * 关注代理仅相关信息

你可以将 [`MessageFilterAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.MessageFilterAgent "autogen_agentchat.agents.MessageFilterAgent") 与 [`MessageFilterConfig`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.MessageFilterConfig "autogen_agentchat.agents.MessageFilterConfig") 和 [`PerSourceFilter`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.PerSourceFilter "autogen_agentchat.agents.PerSourceFilter") 一起使用来定义这些规则。
    
    
    from autogen_agentchat.agents import AssistantAgent, MessageFilterAgent, MessageFilterConfig, PerSourceFilter
    from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    # Model client
    client = OpenAIChatCompletionClient(model="gpt-4.1-nano")
    
    # Create agents
    researcher = AssistantAgent(
        "researcher", model_client=client, system_message="Summarize key facts about climate change."
    )
    analyst = AssistantAgent("analyst", model_client=client, system_message="Review the summary and suggest improvements.")
    presenter = AssistantAgent(
        "presenter", model_client=client, system_message="Prepare a presentation slide based on the final summary."
    )
    
    # Apply message filtering
    filtered_analyst = MessageFilterAgent(
        name="analyst",
        wrapped_agent=analyst,
        filter=MessageFilterConfig(per_source=[PerSourceFilter(source="researcher", position="last", count=1)]),
    )
    
    filtered_presenter = MessageFilterAgent(
        name="presenter",
        wrapped_agent=presenter,
        filter=MessageFilterConfig(per_source=[PerSourceFilter(source="analyst", position="last", count=1)]),
    )
    
    # Build the flow
    builder = DiGraphBuilder()
    builder.add_node(researcher).add_node(filtered_analyst).add_node(filtered_presenter)
    builder.add_edge(researcher, filtered_analyst).add_edge(filtered_analyst, filtered_presenter)
    
    # Create the flow
    flow = GraphFlow(
        participants=builder.get_participants(),
        graph=builder.build(),
    )
    
    # Run the flow
    await Console(flow.run_stream(task="Summarize key facts about climate change."))
    
    
    
    ---------- TextMessage (user) ----------
    Summarize key facts about climate change.
    
    
    
    ---------- TextMessage (researcher) ----------
    Certainly! Here are some key facts about climate change:
    
    1. **Global Warming**: Earth's average surface temperature has increased significantly over the past century, primarily due to human activities.
    2. **Greenhouse Gas Emissions**: The main contributors are carbon dioxide (CO₂), methane (CH₄), and nitrous oxide (N₂O), resulting from burning fossil fuels, deforestation, and industrial processes.
    3. **Impacts on Weather and Climate**: Climate change leads to more frequent and severe heatwaves, storms, droughts, and heavy rainfall.
    4. **Rising Sea Levels**: Melting polar ice caps and glaciers, along with thermal expansion of seawater, are causing sea levels to rise.
    5. **Effects on Ecosystems**: Altered habitats threaten plant and animal species, leading to biodiversity loss.
    6. **Human Health and Societies**: Climate change contributes to health issues, food and water insecurity, and displacement of populations.
    7. **Global Response**: International efforts like the Paris Agreement aim to limit temperature rise, promote renewable energy, and reduce emissions.
    8. **Urgency**: Addressing climate change requires immediate, concerted actions to mitigate further damage and adapt to changes.
    
    Let me know if you want more detailed information on any of these points!
    ---------- TextMessage (analyst) ----------
    Your summary effectively covers the fundamental aspects of climate change and presents them clearly. Here are some suggestions to improve clarity, depth, and engagement:
    
    1. Enhance structure with subheadings: Organize points into thematic sections (e.g., Causes, Effects, Responses) for easier navigation.
    2. Add recent context or data: Incorporate the latest statistics or notable recent events to emphasize urgency.
    3. Emphasize solutions: Briefly mention specific mitigation and adaptation strategies beyond international agreements.
    4. Use more precise language: For example, specify the amount of temperature increase globally (~1.2°C since pre-industrial times).
    5. Incorporate the importance of individual actions: Highlight how personal choices contribute to climate efforts.
    6. Mention climate feedback loops: Briefly note how certain effects (like melting ice) can accelerate warming.
    
    **Improved Version:**
    
    ---
    
    **Overview of Climate Change**
    
    **Causes:**
    - Human activities, especially burning fossil fuels, deforestation, and industrial processes, have led to increased concentrations of greenhouse gases such as carbon dioxide (CO₂), methane (CH₄), and nitrous oxide (N₂O).
    - Since the late 19th century, Earth's average surface temperature has risen by approximately 1.2°C, with the past decade being the warmest on record.
    
    **Impacts:**
    - The changing climate causes more frequent and intense heatwaves, storms, droughts, and heavy rainfall events.
    - Melting polar ice caps and glaciers, along with thermal expansion, are raising sea levels, threatening coastal communities.
    - Ecosystems are shifting, leading to habitat loss and risking biodiversity, with some species facing extinction.
    - Human health and societies are affected through increased heat-related illnesses, food and water insecurity, and displacement due to extreme weather events.
    
    **Global Response and Solutions:**
    - International agreements like the Paris Agreement aim to limit global temperature rise well below 2°C.
    - Strategies include transitioning to renewable energy sources, increasing energy efficiency, reforestation, and sustainable land use.
    - Community and individual actions—reducing carbon footprints, supporting sustainable policies, and raising awareness—are essential components.
    
    **Urgency and Call to Action:**
    - Immediate, coordinated efforts are critical to mitigate irreversible damage and adapt to ongoing changes.
    - Every sector, from government to individual, has a role to play in creating a sustainable future.
    
    ---
    
    Let me know if you'd like a more detailed explanation of any section or additional statistical data!
    ---------- TextMessage (presenter) ----------
    **Slide Title:**  
    **Climate Change: Causes, Impacts & Solutions**
    
    **Causes:**  
    - Emissions from burning fossil fuels, deforestation, industrial activities  
    - Greenhouse gases (CO₂, CH₄, N₂O) have increased significantly  
    - Global temperature has risen by ~1.2°C since pre-industrial times  
    
    **Impacts:**  
    - More frequent heatwaves, storms, droughts, and heavy rainfall  
    - Melting ice caps and rising sea levels threaten coastal areas  
    - Habitat loss and decreased biodiversity  
    - Health risks and societal disruptions  
    
    **Responses & Solutions:**  
    - International efforts like the Paris Agreement aim to limit warming  
    - Transitioning to renewable energy, energy efficiency, reforestation  
    - Community and individual actions: reducing carbon footprints and raising awareness  
    
    **Urgency:**  
    - Immediate, coordinated action is essential to prevent irreversible damage  
    - Everyone has a role in building a sustainable future
    ---------- StopMessage (DiGraphStopAgent) ----------
    Digraph execution is complete
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Summarize key facts about climate change.', type='TextMessage'), TextMessage(source='researcher', models_usage=RequestUsage(prompt_tokens=30, completion_tokens=267), metadata={}, content="Certainly! Here are some key facts about climate change:\n\n1. **Global Warming**: Earth's average surface temperature has increased significantly over the past century, primarily due to human activities.\n2. **Greenhouse Gas Emissions**: The main contributors are carbon dioxide (CO₂), methane (CH₄), and nitrous oxide (N₂O), resulting from burning fossil fuels, deforestation, and industrial processes.\n3. **Impacts on Weather and Climate**: Climate change leads to more frequent and severe heatwaves, storms, droughts, and heavy rainfall.\n4. **Rising Sea Levels**: Melting polar ice caps and glaciers, along with thermal expansion of seawater, are causing sea levels to rise.\n5. **Effects on Ecosystems**: Altered habitats threaten plant and animal species, leading to biodiversity loss.\n6. **Human Health and Societies**: Climate change contributes to health issues, food and water insecurity, and displacement of populations.\n7. **Global Response**: International efforts like the Paris Agreement aim to limit temperature rise, promote renewable energy, and reduce emissions.\n8. **Urgency**: Addressing climate change requires immediate, concerted actions to mitigate further damage and adapt to changes.\n\nLet me know if you want more detailed information on any of these points!", type='TextMessage'), TextMessage(source='analyst', models_usage=RequestUsage(prompt_tokens=287, completion_tokens=498), metadata={}, content="Your summary effectively covers the fundamental aspects of climate change and presents them clearly. Here are some suggestions to improve clarity, depth, and engagement:\n\n1. Enhance structure with subheadings: Organize points into thematic sections (e.g., Causes, Effects, Responses) for easier navigation.\n2. Add recent context or data: Incorporate the latest statistics or notable recent events to emphasize urgency.\n3. Emphasize solutions: Briefly mention specific mitigation and adaptation strategies beyond international agreements.\n4. Use more precise language: For example, specify the amount of temperature increase globally (~1.2°C since pre-industrial times).\n5. Incorporate the importance of individual actions: Highlight how personal choices contribute to climate efforts.\n6. Mention climate feedback loops: Briefly note how certain effects (like melting ice) can accelerate warming.\n\n**Improved Version:**\n\n---\n\n**Overview of Climate Change**\n\n**Causes:**\n- Human activities, especially burning fossil fuels, deforestation, and industrial processes, have led to increased concentrations of greenhouse gases such as carbon dioxide (CO₂), methane (CH₄), and nitrous oxide (N₂O).\n- Since the late 19th century, Earth's average surface temperature has risen by approximately 1.2°C, with the past decade being the warmest on record.\n\n**Impacts:**\n- The changing climate causes more frequent and intense heatwaves, storms, droughts, and heavy rainfall events.\n- Melting polar ice caps and glaciers, along with thermal expansion, are raising sea levels, threatening coastal communities.\n- Ecosystems are shifting, leading to habitat loss and risking biodiversity, with some species facing extinction.\n- Human health and societies are affected through increased heat-related illnesses, food and water insecurity, and displacement due to extreme weather events.\n\n**Global Response and Solutions:**\n- International agreements like the Paris Agreement aim to limit global temperature rise well below 2°C.\n- Strategies include transitioning to renewable energy sources, increasing energy efficiency, reforestation, and sustainable land use.\n- Community and individual actions—reducing carbon footprints, supporting sustainable policies, and raising awareness—are essential components.\n\n**Urgency and Call to Action:**\n- Immediate, coordinated efforts are critical to mitigate irreversible damage and adapt to ongoing changes.\n- Every sector, from government to individual, has a role to play in creating a sustainable future.\n\n---\n\nLet me know if you'd like a more detailed explanation of any section or additional statistical data!", type='TextMessage'), TextMessage(source='presenter', models_usage=RequestUsage(prompt_tokens=521, completion_tokens=192), metadata={}, content='**Slide Title:**  \n**Climate Change: Causes, Impacts & Solutions**\n\n**Causes:**  \n- Emissions from burning fossil fuels, deforestation, industrial activities  \n- Greenhouse gases (CO₂, CH₄, N₂O) have increased significantly  \n- Global temperature has risen by ~1.2°C since pre-industrial times  \n\n**Impacts:**  \n- More frequent heatwaves, storms, droughts, and heavy rainfall  \n- Melting ice caps and rising sea levels threaten coastal areas  \n- Habitat loss and decreased biodiversity  \n- Health risks and societal disruptions  \n\n**Responses & Solutions:**  \n- International efforts like the Paris Agreement aim to limit warming  \n- Transitioning to renewable energy, energy efficiency, reforestation  \n- Community and individual actions: reducing carbon footprints and raising awareness  \n\n**Urgency:**  \n- Immediate, coordinated action is essential to prevent irreversible damage  \n- Everyone has a role in building a sustainable future', type='TextMessage'), StopMessage(source='DiGraphStopAgent', models_usage=None, metadata={}, content='Digraph execution is complete', type='StopMessage')], stop_reason='Stop message received')
    

## 🔁 Advanced Example: Conditional Loop + Filtered Summary#

此示例演示：

  * 生成器和审查器之间的循环（当审查器说"APPROVE"时退出）

  * 一个仅查看第一个用户输入和最后一条审查器消息的 summarizer 代理

    
    
    from autogen_agentchat.agents import AssistantAgent, MessageFilterAgent, MessageFilterConfig, PerSourceFilter
    from autogen_agentchat.teams import (
        DiGraphBuilder,
        GraphFlow,
    )
    from autogen_agentchat.conditions import MaxMessageTermination
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    
    # Agents
    generator = AssistantAgent("generator", model_client=model_client, system_message="Generate a list of creative ideas.")
    reviewer = AssistantAgent(
        "reviewer",
        model_client=model_client,
        system_message="Review ideas and provide feedbacks, or just 'APPROVE' for final approval.",
    )
    summarizer_core = AssistantAgent(
        "summary", model_client=model_client, system_message="Summarize the user request and the final feedback."
    )
    
    # Filtered summarizer
    filtered_summarizer = MessageFilterAgent(
        name="summary",
        wrapped_agent=summarizer_core,
        filter=MessageFilterConfig(
            per_source=[
                PerSourceFilter(source="user", position="first", count=1),
                PerSourceFilter(source="reviewer", position="last", count=1),
            ]
        ),
    )
    
    # Build graph with conditional loop
    builder = DiGraphBuilder()
    builder.add_node(generator).add_node(reviewer).add_node(filtered_summarizer)
    builder.add_edge(generator, reviewer)
    builder.add_edge(reviewer, filtered_summarizer, condition=lambda msg: "APPROVE" in msg.to_model_text())
    builder.add_edge(reviewer, generator, condition=lambda msg: "APPROVE" not in msg.to_model_text())
    builder.set_entry_point(generator)  # Set entry point to generator. Required if there are no source nodes.
    graph = builder.build()
    
    termination_condition = MaxMessageTermination(10)
    
    # Create the flow
    flow = GraphFlow(
        participants=builder.get_participants(),
        graph=graph,
        termination_condition=termination_condition
    )
    
    # Run the flow and pretty print the output in the console
    await Console(flow.run_stream(task="Brainstorm ways to reduce plastic waste."))
    
    
    
    ---------- TextMessage (user) ----------
    Brainstorm ways to reduce plastic waste.
    ---------- TextMessage (generator) ----------
    Here are some creative ideas to help reduce plastic waste:
    
    1. **Refill Stations**: Create refill stations for common household liquids (like soaps, shampoos, and detergents) where people can bring their own containers to fill up.
    
    2. **DIY Kits**: Offer DIY kits for making eco-friendly products, such as beeswax wraps, reusable bags, or natural cleaning solutions.
    
    3. **Community Swap Events**: Organize swap events where people can bring unwanted items, including clothing and household products, to exchange instead of purchasing new items.
    
    4. **Plastic-Free Challenge**: Launch a community-wide challenge encouraging residents to go plastic-free for a month, sharing tips and experiences on social media.
    
    5. **Incentivize Businesses**: Create incentives for local businesses that implement sustainable practices, like providing discounts to customers who bring their own containers or bags.
    
    6. **Educational Campaigns**: Partner with schools to educate children about the impact of plastic waste and encourage them to take home messages to their families.
    
    7. **Plastic-Free Shopping Zones**: Designate certain areas in town as plastic-free zones where businesses agree to eliminate single-use plastics.
    
    8. **Upcycling Workshops**: Host workshops teaching people how to upcycle plastic waste into art, furniture, or home decor.
    
    9. **Composting Competition**: Encourage households to compost food waste and offer a competition for the best composting garden to foster eco-awareness.
    
    10. **Zero-Waste Stores**: Support or start zero-waste stores that sell bulk goods, allowing customers to shop with their own containers.
    
    11. **Mobile Recycling Units**: Implement mobile recycling units that visit neighborhoods to educate residents on recycling properly and collect recyclables.
    
    12. **Plastic Offset Programs**: Create programs that allow individuals and companies to offset their plastic usage through donations to initiatives that remove plastic from oceans.
    
    13. **Collaboration with Influencers**: Partner with social media influencers to spread the message about reducing plastic waste and promote sustainable alternatives.
    
    14. **Sustainable Product Market**: Organize a market dedicated exclusively to sustainable products and services, showcasing local vendors who prioritize eco-friendly practices.
    
    15. **Plastic Waste Art Installations**: Collaborate with artists to create public installations made from recycled plastic, raising awareness of the plastic problem in a visually impactful way.
    
    16. **Interactive Apps**: Develop apps that track plastic usage and provide personalized tips for reducing plastic consumption based on user habits.
    
    17. **Corporate Partnerships**: Work with businesses to develop corporate responsibility programs focused on reducing plastic use in their operations and packaging.
    
    18. **Legislation Advocacy**: Promote local policies that restrict single-use plastics or support more effective recycling programs.
    
    19. **Public Transportation Awareness**: Encourage public transportation usage by providing eco-friendly incentives for those who walk, bike, or use buses instead of cars.
    
    20. **Create a Local Plastic Waste Repository**: Start a community hub where individuals and artists can drop off plastic waste for reuse in projects or art pieces.
    
    By implementing these ideas, communities can take significant steps toward reducing plastic waste and fostering a sustainable future.
    ---------- TextMessage (reviewer) ----------
    These ideas present a comprehensive and practical approach to reducing plastic waste within communities. Here's some feedback and considerations for each suggestion:
    
    1. **Refill Stations**: Great idea; consider partnering with local health and wellness shops for broader adoption.
       
    2. **DIY Kits**: Ensure kits include clear instructions and safety guidance to promote user-friendliness.
    
    3. **Community Swap Events**: Promote these as regular events to build a sense of community and reinforce sustainable habits.
    
    4. **Plastic-Free Challenge**: Consider creating a dedicated hashtag to track participants' journeys and foster engagement online.
    
    5. **Incentivize Businesses**: Work on a simple certification system for sustainable businesses to encourage participation and recognition.
    
    6. **Educational Campaigns**: Tailor content to different age groups to maximize impact across the community.
    
    7. **Plastic-Free Shopping Zones**: Consider involving local government for support and promotion, which can increase visibility and compliance.
    
    8. **Upcycling Workshops**: Source materials locally for workshops to decrease transportation emissions and support local businesses.
    
    9. **Composting Competition**: Collaborate with gardening clubs for expert insights and to broaden participation in community gardening.
    
    10. **Zero-Waste Stores**: Explore online sales options to enhance accessibility while retaining the focus on zero-waste practices.
    
    11. **Mobile Recycling Units**: Train volunteers for effective community engagement and education during visits.
    
    12. **Plastic Offset Programs**: Emphasize transparency in how donations are used to build trust within the community.
    
    13. **Collaboration with Influencers**: Ensure influencers have a genuine commitment to sustainability to ensure credible messaging.
    
    14. **Sustainable Product Market**: Regularly invite new vendors to keep the market fresh and encourage innovation in sustainable products.
    
    15. **Plastic Waste Art Installations**: Consider educational plaques accompanying installations that inform viewers about the issues of plastic waste.
    
    16. **Interactive Apps**: Include gamification elements to encourage increased user engagement and sharing among friends.
    
    17. **Corporate Partnerships**: Develop case studies or success stories to showcase the benefits of reduced plastic use for businesses.
    
    18. **Legislation Advocacy**: Mobilize community members to become advocates themselves, creating a grass-roots effort for policy change.
    
    19. **Public Transportation Awareness**: Explore partnerships with public transit systems for eco-friendly promotions.
    
    20. **Create a Local Plastic Waste Repository**: Establish partnerships with local craft schools or organizations to enhance creativity and use of the repository.
    
    Overall, these ideas have high potential for impactful implementation. Emphasizing community engagement, education, and ongoing support will help ensure their success. **APPROVE**.
    ---------- TextMessage (summary) ----------
    The user requested brainstorming ideas to reduce plastic waste, looking for practical and impactful solutions. The reviewer provided detailed feedback on each suggested idea, indicating strengths and considerations for improvement, such as involving local businesses, enhancing community engagement, and promoting educational initiatives. The final feedback indicates that the suggestions have great potential and emphasizes the importance of community involvement and education for successful implementation, culminating in an overall approval of the ideas presented.
    
    
    
    TaskResult(messages=[TextMessage(id='eca90b4f-a8cc-4f06-9b42-d8387caf338e', source='user', models_usage=None, metadata={}, created_at=datetime.datetime(2025, 7, 15, 1, 48, 51, 648989, tzinfo=datetime.timezone.utc), content='Brainstorm ways to reduce plastic waste.', type='TextMessage'), TextMessage(id='29767cbd-ae8d-4dfb-be57-7f982aaddc4b', source='generator', models_usage=RequestUsage(prompt_tokens=27, completion_tokens=627), metadata={}, created_at=datetime.datetime(2025, 7, 15, 1, 49, 6, 788238, tzinfo=datetime.timezone.utc), content='Here are some creative ideas to help reduce plastic waste:\n\n1. **Refill Stations**: Create refill stations for common household liquids (like soaps, shampoos, and detergents) where people can bring their own containers to fill up.\n\n2. **DIY Kits**: Offer DIY kits for making eco-friendly products, such as beeswax wraps, reusable bags, or natural cleaning solutions.\n\n3. **Community Swap Events**: Organize swap events where people can bring unwanted items, including clothing and household products, to exchange instead of purchasing new items.\n\n4. **Plastic-Free Challenge**: Launch a community-wide challenge encouraging residents to go plastic-free for a month, sharing tips and experiences on social media.\n\n5. **Incentivize Businesses**: Create incentives for local businesses that implement sustainable practices, like providing discounts to customers who bring their own containers or bags.\n\n6. **Educational Campaigns**: Partner with schools to educate children about the impact of plastic waste and encourage them to take home messages to their families.\n\n7. **Plastic-Free Shopping Zones**: Designate certain areas in town as plastic-free zones where businesses agree to eliminate single-use plastics.\n\n8. **Upcycling Workshops**: Host workshops teaching people how to upcycle plastic waste into art, furniture, or home decor.\n\n9. **Composting Competition**: Encourage households to compost food waste and offer a competition for the best composting garden to foster eco-awareness.\n\n10. **Zero-Waste Stores**: Support or start zero-waste stores that sell bulk goods, allowing customers to shop with their own containers.\n\n11. **Mobile Recycling Units**: Implement mobile recycling units that visit neighborhoods to educate residents on recycling properly and collect recyclables.\n\n12. **Plastic Offset Programs**: Create programs that allow individuals and companies to offset their plastic usage through donations to initiatives that remove plastic from oceans.\n\n13. **Collaboration with Influencers**: Partner with social media influencers to spread the message about reducing plastic waste and promote sustainable alternatives.\n\n14. **Sustainable Product Market**: Organize a market dedicated exclusively to sustainable products and services, showcasing local vendors who prioritize eco-friendly practices.\n\n15. **Plastic Waste Art Installations**: Collaborate with artists to create public installations made from recycled plastic, raising awareness of the plastic problem in a visually impactful way.\n\n16. **Interactive Apps**: Develop apps that track plastic usage and provide personalized tips for reducing plastic consumption based on user habits.\n\n17. **Corporate Partnerships**: Work with businesses to develop corporate responsibility programs focused on reducing plastic use in their operations and packaging.\n\n18. **Legislation Advocacy**: Promote local policies that restrict single-use plastics or support more effective recycling programs.\n\n19. **Public Transportation Awareness**: Encourage public transportation usage by providing eco-friendly incentives for those who walk, bike, or use buses instead of cars.\n\n20. **Create a Local Plastic Waste Repository**: Start a community hub where individuals and artists can drop off plastic waste for reuse in projects or art pieces.\n\nBy implementing these ideas, communities can take significant steps toward reducing plastic waste and fostering a sustainable future.', type='TextMessage'), TextMessage(id='54e02028-0239-4809-8163-af60745e6b9d', source='reviewer', models_usage=RequestUsage(prompt_tokens=671, completion_tokens=532), metadata={}, created_at=datetime.datetime(2025, 7, 15, 1, 49, 17, 327641, tzinfo=datetime.timezone.utc), content='These ideas present a comprehensive and practical approach to reducing plastic waste within communities. Here’s some feedback and considerations for each suggestion:\n\n1. **Refill Stations**: Great idea; consider partnering with local health and wellness shops for broader adoption.\n   \n2. **DIY Kits**: Ensure kits include clear instructions and safety guidance to promote user-friendliness.\n\n3. **Community Swap Events**: Promote these as regular events to build a sense of community and reinforce sustainable habits.\n\n4. **Plastic-Free Challenge**: Consider creating a dedicated hashtag to track participants’ journeys and foster engagement online.\n\n5. **Incentivize Businesses**: Work on a simple certification system for sustainable businesses to encourage participation and recognition.\n\n6. **Educational Campaigns**: Tailor content to different age groups to maximize impact across the community.\n\n7. **Plastic-Free Shopping Zones**: Consider involving local government for support and promotion, which can increase visibility and compliance.\n\n8. **Upcycling Workshops**: Source materials locally for workshops to decrease transportation emissions and support local businesses.\n\n9. **Composting Competition**: Collaborate with gardening clubs for expert insights and to broaden participation in community gardening.\n\n10. **Zero-Waste Stores**: Explore online sales options to enhance accessibility while retaining the focus on zero-waste practices.\n\n11. **Mobile Recycling Units**: Train volunteers for effective community engagement and education during visits.\n\n12. **Plastic Offset Programs**: Emphasize transparency in how donations are used to build trust within the community.\n\n13. **Collaboration with Influencers**: Ensure influencers have a genuine commitment to sustainability to ensure credible messaging.\n\n14. **Sustainable Product Market**: Regularly invite new vendors to keep the market fresh and encourage innovation in sustainable products.\n\n15. **Plastic Waste Art Installations**: Consider educational plaques accompanying installations that inform viewers about the issues of plastic waste.\n\n16. **Interactive Apps**: Include gamification elements to encourage increased user engagement and sharing among friends.\n\n17. **Corporate Partnerships**: Develop case studies or success stories to showcase the benefits of reduced plastic use for businesses.\n\n18. **Legislation Advocacy**: Mobilize community members to become advocates themselves, creating a grass-roots effort for policy change.\n\n19. **Public Transportation Awareness**: Explore partnerships with public transit systems for eco-friendly promotions.\n\n20. **Create a Local Plastic Waste Repository**: Establish partnerships with local craft schools or organizations to enhance creativity and use of the repository.\n\nOverall, these ideas have high potential for impactful implementation. Emphasizing community engagement, education, and ongoing support will help ensure their success. **APPROVE**.', type='TextMessage'), TextMessage(id='55409dc3-9766-4071-ab85-0b3125cb59c7', source='summary', models_usage=RequestUsage(prompt_tokens=570, completion_tokens=82), metadata={}, created_at=datetime.datetime(2025, 7, 15, 1, 49, 19, 442276, tzinfo=datetime.timezone.utc), content='The user requested brainstorming ideas to reduce plastic waste, looking for practical and impactful solutions. The reviewer provided detailed feedback on each suggested idea, indicating strengths and considerations for improvement, such as involving local businesses, enhancing community engagement, and promoting educational initiatives. The final feedback indicates that the suggestions have great potential and emphasizes the importance of community involvement and education for successful implementation, culminating in an overall approval of the ideas presented.', type='TextMessage')], stop_reason='Digraph execution is complete')
    

## 🔁 Advanced Example: Cycles With Activation Group Examples#

以下示例演示了如何使用 `activation_group` 和 `activation_condition` 来处理循环图中的复杂依赖模式，尤其是在多个路径通向同一目标节点时。

### Example 1: Loop with Multiple Paths - "All" Activation (A→B→C→B)#

在这种情况下，我们有 A → B → C → B，其中 B 有两条传入边（来自 A 和来自 C）。默认情况下，B 在执行之前需要 **所有** 其依赖项都满足。

此示例显示了一个 review 循环，其中初始输入 (A) 和反馈 (C) 都必须被处理，然后 B 才能再次执行。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
    from autogen_agentchat.conditions import MaxMessageTermination
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    # Model client
    client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    
    # Create agents for A→B→C→B→E scenario
    agent_a = AssistantAgent("A", model_client=client, system_message="Start the process and provide initial input.")
    agent_b = AssistantAgent(
        "B",
        model_client=client,
        system_message="Process input from A or feedback from C. Say 'CONTINUE' if it's from A or 'STOP' if it's from C.",
    )
    agent_c = AssistantAgent("C", model_client=client, system_message="Review B's output and provide feedback.")
    agent_e = AssistantAgent("E", model_client=client, system_message="Finalize the process.")
    
    # Build the graph with activation groups
    builder = DiGraphBuilder()
    builder.add_node(agent_a).add_node(agent_b).add_node(agent_c).add_node(agent_e)
    
    # A → B (initial path)
    builder.add_edge(agent_a, agent_b, activation_group="initial")
    
    # B → C
    builder.add_edge(agent_b, agent_c, condition="CONTINUE")
    
    # C → B (loop back - different activation group)
    builder.add_edge(agent_c, agent_b, activation_group="feedback")
    
    # B → E (exit condition)
    builder.add_edge(agent_b, agent_e, condition="STOP")
    
    termination_condition = MaxMessageTermination(10)
    # Build and create flow
    graph = builder.build()
    flow = GraphFlow(participants=[agent_a, agent_b, agent_c, agent_e], graph=graph, termination_condition=termination_condition)
    
    print("=== Example 1: A→B→C→B with 'All' Activation ===")
    print("B will exit when it receives a message from C")
    # await Console(flow.run_stream(task="Start a review process for a document."))
    

### Example 2: Loop with Multiple Paths - "Any" Activation (A→B→(C1,C2)→B)#

在这个更复杂的场景中，我们有 A → B → (C1, C2) → B，其中：

  * B 同时扇出到 C1 和 C2

  * C1 和 C2 都反馈给 B

  * B 使用 "any" 激活，这意味着只要 **任一** C1 或 C2 完成，它就会执行

这在希望最快响应触发下一步的场景中很有用。
    
    
    # Create agents for A→B→(C1,C2)→B scenario
    agent_a2 = AssistantAgent("A", model_client=client, system_message="Initiate a task that needs parallel processing.")
    agent_b2 = AssistantAgent(
        "B",
        model_client=client,
        system_message="Coordinate parallel tasks. Say 'PROCESS' to start parallel work or 'DONE' to finish.",
    )
    agent_c1 = AssistantAgent("C1", model_client=client, system_message="Handle task type 1. Say 'C1_COMPLETE' when done.")
    agent_c2 = AssistantAgent("C2", model_client=client, system_message="Handle task type 2. Say 'C2_COMPLETE' when done.")
    agent_e = AssistantAgent("E", model_client=client, system_message="Finalize the process.")
    
    # Build the graph with "any" activation
    builder2 = DiGraphBuilder()
    builder2.add_node(agent_a2).add_node(agent_b2).add_node(agent_c1).add_node(agent_c2).add_node(agent_e)
    
    # A → B (initial)
    builder2.add_edge(agent_a2, agent_b2)
    
    # B → C1 and B → C2 (parallel fan-out)
    builder2.add_edge(agent_b2, agent_c1, condition="PROCESS")
    builder2.add_edge(agent_b2, agent_c2, condition="PROCESS")
    
    # B → E (exit condition)
    builder2.add_edge(agent_b2, agent_e, condition=lambda msg: "DONE" in msg.to_model_text())
    
    # C1 → B and C2 → B (both in same activation group with "any" condition)
    builder2.add_edge(
        agent_c1, agent_b2, activation_group="loop_back_group", activation_condition="any", condition="C1_COMPLETE"
    )
    
    builder2.add_edge(
        agent_c2, agent_b2, activation_group="loop_back_group", activation_condition="any", condition="C2_COMPLETE"
    )
    
    # Build and create flow
    graph2 = builder2.build()
    flow2 = GraphFlow(participants=[agent_a2, agent_b2, agent_c1, agent_c2, agent_e], graph=graph2)
    
    print("=== Example 2: A→B→(C1,C2)→B with 'Any' Activation ===")
    print("B will execute as soon as EITHER C1 OR C2 completes (whichever finishes first)")
    # await Console(flow2.run_stream(task="Start a parallel processing task."))
    

### Example 3: Mixed Activation Groups#

此示例显示不同的激活组如何在同一图中共存。我们有一个场景：

  * 节点 D 接收来自多个源的输入，具有不同的激活要求

  * 一些依赖项使用 "all" 激活（必须等待所有输入）

  * 其他依赖项使用 "any" 激活（在第一个输入上继续）

此模式在复杂工作流中很有用，其中不同类型的依赖项具有不同的紧急程度。
    
    
    # Create agents for mixed activation scenario
    agent_a3 = AssistantAgent("A", model_client=client, system_message="Provide critical input that must be processed.")
    agent_b3 = AssistantAgent("B", model_client=client, system_message="Provide secondary critical input.")
    agent_c3 = AssistantAgent("C", model_client=client, system_message="Provide optional quick input.")
    agent_d3 = AssistantAgent("D", model_client=client, system_message="Process inputs based on different priority levels.")
    
    # Build graph with mixed activation groups
    builder3 = DiGraphBuilder()
    builder3.add_node(agent_a3).add_node(agent_b3).add_node(agent_c3).add_node(agent_d3)
    
    # Critical inputs that must ALL be present (activation_group="critical", activation_condition="all")
    builder3.add_edge(agent_a3, agent_d3, activation_group="critical", activation_condition="all")
    builder3.add_edge(agent_b3, agent_d3, activation_group="critical", activation_condition="all")
    
    # Optional input that can trigger execution on its own (activation_group="optional", activation_condition="any")
    builder3.add_edge(agent_c3, agent_d3, activation_group="optional", activation_condition="any")
    
    # Build and create flow
    graph3 = builder3.build()
    flow3 = GraphFlow(participants=[agent_a3, agent_b3, agent_c3, agent_d3], graph=graph3)
    
    print("=== Example 3: Mixed Activation Groups ===")
    print("D will execute when:")
    print("- BOTH A AND B complete (critical group with 'all' activation), OR")
    print("- C completes (optional group with 'any' activation)")
    print("This allows for both required dependencies and fast-path triggers.")
    # await Console(flow3.run_stream(task="Process inputs with mixed priority levels."))
    

### Key Takeaways for Activation Groups#

  1. **`activation_group`** ：对指向同一目标节点的边进行分组，允许你定义不同的依赖模式。

  2. **`activation_condition`** ：

     * `"all"`（默认）：目标节点等待组中的所有边都满足

     * `"any"`：目标节点在组中的任一边满足时立即执行

  3. **Use Cases** ：

     * **具有多个入口点的循环**：不同的激活组防止冲突

     * **基于优先级的执行**：为不同的紧急程度混合 "all" 和 "any" 条件

     * **具有早期终止的并行处理**：使用 "any" 以最快的速度继续进行

  4. **Best Practices** ：

     * 使用描述性组名称（`"critical"`, `"optional"`, `"feedback"` 等）

     * 保持同一组内的激活条件一致

     * 使用不同的执行路径测试你的图逻辑

这些模式实现了复杂的工作流控制，同时保持清晰、易于理解的执行语义。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/graph-flow.ipynb)

[ __Show Source](../../_sources/user-guide/agentchat-user-guide/graph-flow.ipynb.txt)