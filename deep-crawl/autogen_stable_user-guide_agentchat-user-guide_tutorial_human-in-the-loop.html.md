<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/human-in-the-loop.html -->

# 人机协同#

在上一节 [团队](teams.html) 中，我们已经了解了如何创建、观察和控制代理团队。本节将重点介绍如何从您的应用程序与团队交互，并向团队提供人类反馈。

与团队交互的两种主要方式是：

  1. 在团队运行期间——执行 [`run()`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run "autogen_agentchat.teams.BaseGroupChat.run") 或 [`run_stream()`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run_stream "autogen_agentchat.teams.BaseGroupChat.run_stream") 时，通过 [`UserProxyAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent") 提供反馈。

  2. 一旦运行终止，通过向下一次调用 [`run()`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run "autogen_agentchat.teams.BaseGroupChat.run") 或 [`run_stream()`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run_stream "autogen_agentchat.teams.BaseGroupChat.run_stream") 提供输入来提供反馈。

我们将在本节中介绍这两种方法。

要直接查看与 Web 和 UI 框架集成的代码示例，请参阅以下链接：

  * [AgentChat + FastAPI](https://github.com/microsoft/autogen/tree/main/python/samples/agentchat_fastapi)

  * [AgentChat + ChainLit](https://github.com/microsoft/autogen/tree/main/python/samples/agentchat_chainlit)

  * [AgentChat + Streamlit](https://github.com/microsoft/autogen/tree/main/python/samples/agentchat_streamlit)

## 在运行期间提供反馈#

[`UserProxyAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent") 是一个特殊的内置代理，充当用户向团队提供反馈的代理。

要使用 [`UserProxyAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent")，您可以创建它的实例并在运行团队之前将其包含在团队中。团队将决定何时调用 [`UserProxyAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent") 以从用户那里获取反馈。

例如，在 [`RoundRobinGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 团队中，[`UserProxyAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent") 按照传递给团队的顺序被调用，而在 [`SelectorGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 团队中，选择器提示词或选择函数决定何时调用 [`UserProxyAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent")。

以下图表说明了如何在团队运行期间使用 [`UserProxyAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent") 从用户那里获取反馈：

![human-in-the-loop-user-proxy](../../../_images/human-in-the-loop-user-proxy.svg)

粗箭头表示团队运行期间的控制流：当团队调用 [`UserProxyAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent") 时，它将控制权转移给应用程序/用户，并等待反馈；一旦提供反馈，控制权就会转回团队，团队继续执行。

注意

当在运行期间调用 [`UserProxyAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent") 时，它会阻塞团队的执行，直到用户提供反馈或出错为止。这将耽误团队的进度，并使团队处于无法保存或恢复的不稳定状态。

由于这种方法的阻塞性质，建议仅将其用于需要用户即时反馈的短交互，例如通过点击按钮请求批准或拒绝，或需要注意否则会失败任务的警报。

以下是如何在 [`RoundRobinGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 中使用 [`UserProxyAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent") 进行诗歌生成任务的示例：
    
    
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    # 创建代理。
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    assistant = AssistantAgent("assistant", model_client=model_client)
    user_proxy = UserProxyAgent("user_proxy", input_func=input)  # 使用 input() 从控制台获取用户输入。
    
    # 创建终止条件，当用户说 "APPROVE" 时将结束对话。
    termination = TextMentionTermination("APPROVE")
    
    # 创建团队。
    team = RoundRobinGroupChat([assistant, user_proxy], termination_condition=termination)
    
    # 运行对话并流式传输到控制台。
    stream = team.run_stream(task="写一首关于海洋的 4 行诗。")
    # 在脚本中运行时使用 asyncio.run(...)。
    await Console(stream)
    await model_client.close()
    
    
    
    ---------- 用户 ----------
    写一首关于海洋的 4 行诗。
    ---------- assistant ----------
    In endless blue where whispers play,  
    The ocean's waves dance night and day.  
    A world of depths, both calm and wild,  
    Nature's heart, forever beguiled.  
    TERMINATE
    ---------- user_proxy ----------
    APPROVE
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, metadata={}, content='写一首关于海洋的 4 行诗。', type='TextMessage'), TextMessage(source='assistant', models_usage=RequestUsage(prompt_tokens=46, completion_tokens=43), metadata={}, content="In endless blue where whispers play,  \nThe ocean's waves dance night and day.  \nA world of depths, both calm and wild,  \nNature's heart, forever beguiled.  \nTERMINATE", type='TextMessage'), UserInputRequestedEvent(source='user_proxy', models_usage=None, metadata={}, request_id='2622a0aa-b776-4e54-9e8f-4ecbdf14b78d', content='', type='UserInputRequestedEvent'), TextMessage(source='user_proxy', models_usage=None, metadata={}, content='APPROVE', type='TextMessage')], stop_reason="检测到文本 'APPROVE'")
    

从控制台输出中，您可以看到团队通过 `user_proxy` 向用户征求反馈以批准生成的诗歌。

您可以提供自己的输入函数给 [`UserProxyAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent") 以自定义反馈过程。例如，当团队作为 Web 服务运行时，您可以使用自定义输入函数来等待来自 WebSocket 连接的消息。以下代码片段展示了使用 [FastAPI](https://fastapi.tiangolo.com/) Web 框架时的自定义输入函数示例：
    
    
    @app.websocket("/ws/chat")
    async def chat(websocket: WebSocket):
        await websocket.accept()
    
        async def _user_input(prompt: str, cancellation_token: CancellationToken | None) -> str:
            data = await websocket.receive_json() # 从 websocket 等待用户消息。
            message = TextMessage.model_validate(data) # 假设用户消息是 TextMessage。
            return message.content
        
        # 创建带有自定义输入函数的用户代理
        # 使用用户代理运行团队
        # ...
    

有关完整示例，请参阅 [AgentChat FastAPI 示例](https://github.com/microsoft/autogen/blob/main/python/samples/agentchat_fastapi)。

有关与 [`UserProxyAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent") 的 [ChainLit](https://github.com/Chainlit/chainlit) 集成，请参阅 [AgentChat ChainLit 示例](https://github.com/microsoft/autogen/blob/main/python/samples/agentchat_chainlit)。

## 向下次运行提供反馈#

通常情况下，应用程序或用户与代理团队以交互式循环方式交互：团队运行直到终止，应用程序或用户提供反馈，然后团队再次带着反馈运行。

这种方法在具有异步通信的持久会话中非常有用：一旦团队完成一次运行，应用程序就会保存团队的状态，将其放入持久存储中，并在反馈到达时恢复团队。

注意

有关如何保存和加载团队状态的信息，请参阅 [管理状态](state.html)。本节将重点关注反馈机制。

以下图表说明了这种方法中的控制流：

![human-in-the-loop-termination](../../../_images/human-in-the-loop-termination.svg)

有两种方法可以实现这种方法：

  * 设置最大轮数，以便团队总是在指定的轮数后停止。

  * 使用终止条件，如 [`TextMentionTermination`](../../../reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TextMentionTermination "autogen_agentchat.conditions.TextMentionTermination") 和 [`HandoffTermination`](../../../reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.HandoffTermination "autogen_agentchat.conditions.HandoffTermination")，允许团队根据团队的内部状态来决定何时停止并交回控制权。

您可以同时使用这两种方法来实现所需的行为。

### 使用最大轮数#

此方法允许您通过设置最大轮数来暂停团队以获取用户输入。例如，您可以通过将 `max_turns` 设置为 1 来配置团队在第一个代理响应后停止。这在需要持续用户参与的场景中非常有用，例如聊天机器人。

要实现此功能，请在 [`RoundRobinGroupChat()`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 构造函数中设置 `max_turns` 参数。
    
    
    team = RoundRobinGroupChat([...], max_turns=1)
    

一旦团队停止，轮数将被重置。当您恢复团队时，它将再次从 0 开始。但是，团队的内部状态将被保留，例如，[`RoundRobinGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 将从列表中的下一个代理以相同的对话历史恢复。

注意

`max_turn` 是特定于团队类的，目前仅在 [`RoundRobinGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat")、[`SelectorGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 和 [`Swarm`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm") 中支持。与终止条件一起使用时，团队将在任一条件满足时停止。

以下是如何在 [`RoundRobinGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 中使用 `max_turns` 进行诗歌生成任务（最多 1 轮）的示例：
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    # 创建代理。
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    assistant = AssistantAgent("assistant", model_client=model_client)
    
    # 创建团队，将最大轮数设置为 1。
    team = RoundRobinGroupChat([assistant], max_turns=1)
    
    task = "写一首关于海洋的 4 行诗。"
    while True:
        # 运行对话并流式传输到控制台。
        stream = team.run_stream(task=task)
        # 在脚本中运行时使用 asyncio.run(...)。
        await Console(stream)
        # 获取用户响应。
        task = input("输入您的反馈（输入 'exit' 离开）：")
        if task.lower().strip() == "exit":
            break
    await model_client.close()
    
    
    
    ---------- 用户 ----------
    写一首关于海洋的 4 行诗。
    ---------- assistant ----------
    Endless waves in a dance with the shore,  
    Whispers of secrets in tales from the roar,  
    Beneath the vast sky, where horizons blend,  
    The ocean's embrace is a timeless friend.  
    TERMINATE
    [Prompt tokens: 46, Completion tokens: 48]
    ---------- 摘要 ----------
    消息数量：2
    结束原因：已达到最大轮数 1。
    总提示 token 数：46
    总完成 token 数：48
    持续时间：1.63 秒
    ---------- 用户 ----------
    你能把它写成关于一个人及其与海洋的关系吗
    ---------- assistant ----------
    She walks along the tide, where dreams intertwine,  
    With every crashing wave, her heart feels aligned,  
    In the ocean's embrace, her worries dissolve,  
    A symphony of solace, where her spirit evolves.  
    TERMINATE
    [Prompt tokens: 117, Completion tokens: 49]
    ---------- 摘要 ----------
    消息数量：2
    结束原因：已达到最大轮数 1。
    总提示 token 数：117
    总完成 token 数：49
    持续时间：1.21 秒
    

您可以看到团队在一个代理响应后立即停止。

### 使用终止条件#

我们在前面的部分中已经看到了几个终止条件的示例。在本节中，我们重点关注 [`HandoffTermination`](../../../reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.HandoffTermination "autogen_agentchat.conditions.HandoffTermination")，它在代理发送 [`HandoffMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage") 消息时停止团队。

让我们创建一个团队，其中包含一个带有交接设置的 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent")，并使用一个需要用户额外输入的任务来运行团队，因为代理没有相关工具来继续处理任务。

注意

与 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 一起使用的模型必须支持工具调用才能使用交接功能。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.base import Handoff
    from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    # 创建 OpenAI 模型客户端。
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        # api_key="sk-...", # 如果您设置了 OPENAI_API_KEY 环境变量，此项可选。
    )
    
    # 创建一个总是交接给用户的懒惰助手代理。
    lazy_agent = AssistantAgent(
        "lazy_assistant",
        model_client=model_client,
        handoffs=[Handoff(target="user", message="移交给用户。")],
        system_message="如果您无法完成任务，请移交给用户。否则，完成后请回复 'TERMINATE'。",
    )
    
    # 定义一个检查交接消息的终止条件。
    handoff_termination = HandoffTermination(target="user")
    # 定义一个检查特定文本提及的终止条件。
    text_termination = TextMentionTermination("TERMINATE")
    
    # 创建一个带有懒惰助手和两个终止条件的单代理团队。
    lazy_agent_team = RoundRobinGroupChat([lazy_agent], termination_condition=handoff_termination | text_termination)
    
    # 运行团队并流式传输到控制台。
    task = "纽约的天气怎么样？"
    await Console(lazy_agent_team.run_stream(task=task), output_stats=True)
    
    
    
    ---------- 用户 ----------
    纽约的天气怎么样？
    ---------- lazy_assistant ----------
    [FunctionCall(id='call_EAcMgrLGHdLw0e7iJGoMgxuu', arguments='{}', name='transfer_to_user')]
    [Prompt tokens: 69, Completion tokens: 12]
    ---------- lazy_assistant ----------
    [FunctionExecutionResult(content='移交给用户。', call_id='call_EAcMgrLGHdLw0e7iJGoMgxuu')]
    ---------- lazy_assistant ----------
    移交给用户。
    ---------- 摘要 ----------
    消息数量：4
    结束原因：检测到从 lazy_assistant 移交给用户。
    总提示 token 数：69
    总完成 token 数：12
    持续时间：0.69 秒
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='纽约的天气怎么样？', type='TextMessage'), ToolCallRequestEvent(source='lazy_assistant', models_usage=RequestUsage(prompt_tokens=69, completion_tokens=12), content=[FunctionCall(id='call_EAcMgrLGHdLw0e7iJGoMgxuu', arguments='{}', name='transfer_to_user')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='lazy_assistant', models_usage=None, content=[FunctionExecutionResult(content='移交给用户。', call_id='call_EAcMgrLGHdLw0e7iJGoMgxuu')], type='ToolCallExecutionEvent'), HandoffMessage(source='lazy_assistant', models_usage=None, target='user', content='移交给用户。', context=[], type='HandoffMessage')], stop_reason='检测到从 lazy_assistant 移交给用户。')
    

您可以看到团队因为检测到交接消息而停止。让我们通过提供代理需要的信息来继续团队。
    
    
    await Console(lazy_agent_team.run_stream(task="纽约的天气是晴天。"))
    
    
    
    ---------- 用户 ----------
    纽约的天气是晴天。
    ---------- lazy_assistant ----------
    太好了！享受纽约的晴朗天气！还有什么想了解的吗？
    ---------- lazy_assistant ----------
    TERMINATE
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='纽约的天气是晴天。', type='TextMessage'), TextMessage(source='lazy_assistant', models_usage=RequestUsage(prompt_tokens=110, completion_tokens=21), content="太好了！享受纽约的晴朗天气！还有什么想了解的吗？", type='TextMessage'), TextMessage(source='lazy_assistant', models_usage=RequestUsage(prompt_tokens=137, completion_tokens=5), content='TERMINATE', type='TextMessage')], stop_reason="检测到文本 'TERMINATE'")
    

您可以看到团队在用户提供信息后继续。

注意

如果您使用带有 [`HandoffTermination`](../../../reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.HandoffTermination "autogen_agentchat.conditions.HandoffTermination")（目标为用户）的 [`Swarm`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm") 团队来恢复团队，您需要将 `task` 设置为 [`HandoffMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage")，并将 `target` 设置为您想要运行的下一个代理。有关更多详细信息，请参阅 [Swarm](../swarm.html)。

__本页内容

[ __在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/tutorial/human-in-the-loop.ipynb)

[ __显示源代码](../../../_sources/user-guide/agentchat-user-guide/tutorial/human-in-the-loop.ipynb.txt)
