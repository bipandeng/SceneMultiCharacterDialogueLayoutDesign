<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/custom-agents.html -->

# 自定义智能体#

你可能拥有不属于任何预设行为的智能体。在这种情况下，你可以构建自定义智能体。

AgentChat 中的所有智能体都继承自 [`BaseChatAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent "autogen_agentchat.agents.BaseChatAgent") 类并实现以下抽象方法和属性：

  * [`on_messages()`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.on_messages "autogen_agentchat.agents.BaseChatAgent.on_messages")：定义智能体响应消息行为的抽象方法。在 [`run()`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run") 中要求智能体提供响应时调用此方法。它返回一个 [`Response`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.Response "autogen_agentchat.base.Response") 对象。

  * [`on_reset()`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.on_reset "autogen_agentchat.agents.BaseChatAgent.on_reset")：将智能体重置为其初始状态的抽象方法。当要求智能体重置自身时调用此方法。

  * [`produced_message_types`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.produced_message_types "autogen_agentchat.agents.BaseChatAgent.produced_message_types")：智能体在响应中可以产生的可能的 [`BaseChatMessage`](../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage") 消息类型列表。

可选地，你可以实现 [`on_messages_stream()`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.on_messages_stream "autogen_agentchat.agents.BaseChatAgent.on_messages_stream") 方法以在智能体生成消息时流式传输消息。`run_stream()`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run_stream "autogen_agentchat.agents.BaseChatAgent.run_stream") 调用此方法来流式传输消息。如果未实现此方法，则智能体使用 [`on_messages_stream()`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.on_messages_stream "autogen_agentchat.agents.BaseChatAgent.on_messages_stream") 的默认实现，该实现调用 [`on_messages()`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.on_messages "autogen_agentchat.agents.BaseChatAgent.on_messages") 方法并产生响应中的所有消息。

## CountDownAgent#

在此示例中，我们创建一个简单的智能体，它从给定数字倒数到零，并生成包含当前计数的消息流。
    
    
    from typing import AsyncGenerator, List, Sequence
    
    from autogen_agentchat.agents import BaseChatAgent
    from autogen_agentchat.base import Response
    from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage, TextMessage
    from autogen_core import CancellationToken
    
    
    class CountDownAgent(BaseChatAgent):
        def __init__(self, name: str, count: int = 3):
            super().__init__(name, "一个简单的倒计时智能体。")
            self._count = count
    
        @property
        def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
            return (TextMessage,)
    
        async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
            # 调用 on_messages_stream。
            response: Response | None = None
            async for message in self.on_messages_stream(messages, cancellation_token):
                if isinstance(message, Response):
                    response = message
            assert response is not None
            return response
    
        async def on_messages_stream(
            self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken
        ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:
            inner_messages: List[BaseAgentEvent | BaseChatMessage] = []
            for i in range(self._count, 0, -1):
                msg = TextMessage(content=f"{i}...", source=self.name)
                inner_messages.append(msg)
                yield msg
            # 响应在流的末尾返回。
            # 它包含最终消息和所有内部消息。
            yield Response(chat_message=TextMessage(content="完成！", source=self.name), inner_messages=inner_messages)
    
        async def on_reset(self, cancellation_token: CancellationToken) -> None:
            pass
    
    
    async def run_countdown_agent() -> None:
        # 创建一个倒计时智能体。
        countdown_agent = CountDownAgent("countdown")
    
        # 使用给定任务运行智能体并流式传输响应。
        async for message in countdown_agent.on_messages_stream([], CancellationToken()):
            if isinstance(message, Response):
                print(message.chat_message)
            else:
                print(message)
    
    
    # 在脚本中运行时使用 asyncio.run(run_countdown_agent())。
    await run_countdown_agent()
    
    
    
    3...
    2...
    1...
    Done!
    

## ArithmeticAgent#

在此示例中，我们创建一个智能体类，它可以对给定整数执行简单的算术运算。然后，我们将在 [`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 中使用此智能体类的不同实例，通过按顺序应用算术运算将给定整数转换为另一个整数。

`ArithmeticAgent` 类接受一个 `operator_func`，该函数接受一个整数并返回一个整数，对该整数应用算术运算后。在其 `on_messages` 方法中，它对输入消息中的整数应用 `operator_func`，并返回包含结果的响应。
    
    
    from typing import Callable, Sequence
    
    from autogen_agentchat.agents import BaseChatAgent
    from autogen_agentchat.base import Response
    from autogen_agentchat.conditions import MaxMessageTermination
    from autogen_agentchat.messages import BaseChatMessage
    from autogen_agentchat.teams import SelectorGroupChat
    from autogen_agentchat.ui import Console
    from autogen_core import CancellationToken
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    
    class ArithmeticAgent(BaseChatAgent):
        def __init__(self, name: str, description: str, operator_func: Callable[[int], int]) -> None:
            super().__init__(name, description=description)
            self._operator_func = operator_func
            self._message_history: List[BaseChatMessage] = []
    
        @property
        def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
            return (TextMessage,)
    
        async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
            # 更新消息历史。
            # 注意：消息可能为空列表，这意味着智能体之前已被选中。
            self._message_history.extend(messages)
            # 解析最后一条消息中的数字。
            assert isinstance(self._message_history[-1], TextMessage)
            number = int(self._message_history[-1].content)
            # 对数字应用运算符函数。
            result = self._operator_func(number)
            # 创建包含结果的新消息。
            response_message = TextMessage(content=str(result), source=self.name)
            # 更新消息历史。
            self._message_history.append(response_message)
            # 返回响应。
            return Response(chat_message=response_message)
    
        async def on_reset(self, cancellation_token: CancellationToken) -> None:
            pass
    

注意

`on_messages` 方法可能会使用空消息列表调用，在这种情况下，这意味着智能体之前已被调用，现在再次被调用，而没有任何来自调用方的新消息。因此，重要的是保留智能体接收到的先前消息的历史记录，并使用该历史记录来生成响应。

现在我们可以创建一个 [`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat")，其中包含 5 个 `ArithmeticAgent` 实例：

  * 一个将输入整数加 1，

  * 一个将输入整数减 1，

  * 一个将输入整数乘以 2，

  * 一个将输入整数除以 2 并向下舍入到最接近的整数，以及

  * 一个返回输入整数不变。

然后我们使用这些智能体创建一个 [`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat")，并设置适当的选择器设置：

  * 允许连续选择同一个智能体以允许重复操作，以及

  * 自定义选择器提示以使模型的响应适应特定任务。
    
    
    
    async def run_number_agents() -> None:
        # 创建用于数字运算的智能体。
        add_agent = ArithmeticAgent("add_agent", "将数字加 1。", lambda x: x + 1)
        multiply_agent = ArithmeticAgent("multiply_agent", "将数字乘以 2。", lambda x: x * 2)
        subtract_agent = ArithmeticAgent("subtract_agent", "将数字减 1。", lambda x: x - 1)
        divide_agent = ArithmeticAgent("divide_agent", "将数字除以 2 并向下舍入。", lambda x: x // 2)
        identity_agent = ArithmeticAgent("identity_agent", "按原样返回数字。", lambda x: x)
    
        # 终止条件是在 10 条消息后停止。
        termination_condition = MaxMessageTermination(10)
    
        # 创建一个选择器组聊天。
        selector_group_chat = SelectorGroupChat(
            [add_agent, multiply_agent, subtract_agent, divide_agent, identity_agent],
            model_client=OpenAIChatCompletionClient(model="gpt-4o"),
            termination_condition=termination_condition,
            allow_repeated_speaker=True,  # 允许同一个智能体多次发言，这是此任务所必需的。
            selector_prompt=(
                "可用角色：\n{roles}\n它们的职位描述：\n{participants}\n"
                "当前对话历史：\n{history}\n"
                "请为下一条消息选择最合适的角色，并且只返回角色名称。"
            ),
        )
    
        # 使用给定任务运行选择器组聊天并流式传输响应。
        task: List[BaseChatMessage] = [
            TextMessage(content="应用这些操作将给定数字转换为 25。", source="user"),
            TextMessage(content="10", source="user"),
        ]
        stream = selector_group_chat.run_stream(task=task)
        await Console(stream)
    
    
    # 在脚本中运行时使用 asyncio.run(run_number_agents())。
    await run_number_agents()
    
    
    
    ---------- user ----------
    应用这些操作将给定数字转换为 25。
    ---------- user ----------
    10
    ---------- multiply_agent ----------
    20
    ---------- add_agent ----------
    21
    ---------- multiply_agent ----------
    42
    ---------- divide_agent ----------
    21
    ---------- add_agent ----------
    22
    ---------- add_agent ----------
    23
    ---------- add_agent ----------
    24
    ---------- add_agent ----------
    25
    ---------- Summary ----------
    消息数量：10
    结束原因：已达到最大消息数 10，当前消息数：10
    总提示令牌：0
    总完成令牌：0
    持续时间：2.40 秒
    

从输出中，我们可以看到智能体通过按顺序选择应用算术运算的适当智能体，成功地将输入整数从 10 转换为 25。

## 在自定义智能体中使用自定义模型客户端#

[`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 预设的 AgentChat 的一个关键特性是它接受 `model_client` 参数并可在响应消息时使用它。但是，在某些情况下，你可能希望你的智能体使用当前不支持的自定义模型客户端（参见[支持的模型客户端](https://microsoft.github.io/autogen/dev/user-guide/core-user-guide/components/model-clients.html)）或自定义模型行为。

你可以通过实现 _你的自定义模型客户端_ 的自定义智能体来实现此目的。

在下面的示例中，我们将介绍一个使用 [Google Gemini SDK](https://github.com/googleapis/python-genai) 直接响应消息的自定义智能体的示例。

> **注意：** 你需要安装 [Google Gemini SDK](https://github.com/googleapis/python-genai) 才能运行此示例。你可以使用以下命令安装它：
    
    
    pip install google-genai
    
    
    
    # !pip install google-genai
    import os
    from typing import AsyncGenerator, Sequence
    
    from autogen_agentchat.agents import BaseChatAgent
    from autogen_agentchat.base import Response
    from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
    from autogen_core import CancellationToken
    from autogen_core.model_context import UnboundedChatCompletionContext
    from autogen_core.models import AssistantMessage, RequestUsage, UserMessage
    from google import genai
    from google.genai import types
    
    
    class GeminiAssistantAgent(BaseChatAgent):
        def __init__(
            self,
            name: str,
            description: str = "一个提供帮助并具有使用工具的能力的智能体。",
            model: str = "gemini-1.5-flash-002",
            api_key: str = os.environ["GEMINI_API_KEY"],
            system_message: str
            | None = "你是一个乐于助人的助手，可以响应消息。当任务完成时回复 TERMINATE。",
        ):
            super().__init__(name=name, description=description)
            self._model_context = UnboundedChatCompletionContext()
            self._model_client = genai.Client(api_key=api_key)
            self._system_message = system_message
            self._model = model
    
        @property
        def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
            return (TextMessage,)
    
        async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
            final_response = None
            async for message in self.on_messages_stream(messages, cancellation_token):
                if isinstance(message, Response):
                    final_response = message
    
            if final_response is None:
                raise AssertionError("流应返回最终结果。")
    
            return final_response
    
        async def on_messages_stream(
            self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken
        ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:
            # 将消息添加到模型上下文
            for msg in messages:
                await self._model_context.add_message(msg.to_model_message())
    
            # 获取对话历史
            history = [
                (msg.source if hasattr(msg, "source") else "system")
                + ": "
                + (msg.content if isinstance(msg.content, str) else "")
                + "\n"
                for msg in await self._model_context.get_messages()
            ]
            # 使用 Gemini 生成响应
            response = self._model_client.models.generate_content(
                model=self._model,
                contents=f"历史：{history}\n根据历史，请提供响应",
                config=types.GenerateContentConfig(
                    system_instruction=self._system_message,
                    temperature=0.3,
                ),
            )
    
            # 创建使用情况元数据
            usage = RequestUsage(
                prompt_tokens=response.usage_metadata.prompt_token_count,
                completion_tokens=response.usage_metadata.candidates_token_count,
            )
    
            # 将响应添加到模型上下文
            await self._model_context.add_message(AssistantMessage(content=response.text, source=self.name))
    
            # 生成最终响应
            yield Response(
                chat_message=TextMessage(content=response.text, source=self.name, models_usage=usage),
                inner_messages=[],
            )
    
        async def on_reset(self, cancellation_token: CancellationToken) -> None:
            """通过清除模型上下文来重置助手。"""
            await self._model_context.clear()
    
    
    
    gemini_assistant = GeminiAssistantAgent("gemini_assistant")
    await Console(gemini_assistant.run_stream(task="纽约的首都是什么？"))
    
    
    
    ---------- user ----------
    纽约的首都是什么？
    ---------- gemini_assistant ----------
    Albany
    TERMINATE
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='纽约的首都是什么？', type='TextMessage'), TextMessage(source='gemini_assistant', models_usage=RequestUsage(prompt_tokens=46, completion_tokens=5), content='Albany\nTERMINATE\n', type='TextMessage')], stop_reason=None)
    

在上面的示例中，我们选择提供 `model`、`api_key` 和 `system_message` 作为参数 - 你可以选择提供使用模型客户端所需的任何其他参数或适合你的应用程序设计的参数。

现在，让我们探索如何在 AgentChat 中将此自定义智能体用作团队的一部分。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.ui import Console
    
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    
    # 创建主智能体。
    primary_agent = AssistantAgent(
        "primary",
        model_client=model_client,
        system_message="你是一个乐于助人的 AI 助手。",
    )
    
    # 基于我们新的 GeminiAssistantAgent 创建一个评论员智能体。
    gemini_critic_agent = GeminiAssistantAgent(
        "gemini_critic",
        system_message="提供建设性的反馈。当你的反馈得到解决时回复 'APPROVE'。",
    )
    
    
    # 定义一个终止条件，如果评论员批准或经过 10 条消息后停止任务。
    termination = TextMentionTermination("APPROVE") | MaxMessageTermination(10)
    
    # 创建一个包含主智能体和评论员智能体的团队。
    team = RoundRobinGroupChat([primary_agent, gemini_critic_agent], termination_condition=termination)
    
    await Console(team.run_stream(task="写一首关于秋季的 4 行俳句诗。"))
    await model_client.close()
    
    
    
    ---------- user ----------
    写一首关于秋季的 4 行俳句诗。
    ---------- primary ----------
    Crimson leaves cascade,  
    Whispering winds sing of change,  
    Chill wraps the fading,  
    Nature's quilt, rich and warm.
    ---------- gemini_critic ----------
    这首诗不错，但是有四行而不是三行。俳句必须有 5-7-5 音节结构的三行。内容富有秋意，但形式不正确。请修改以遵守俳句的音节结构。
    
    ---------- primary ----------
    谢谢你的反馈！这是一首遵循 5-7-5 音节结构的修改后的俳句：
    
    Crimson leaves drift down,  
    Chill winds whisper through the gold,  
    Autumn's breath is near.
    ---------- gemini_critic ----------
    修改后的俳句有了很大的改进。它正确地遵循了 5-7-5 音节结构并保持了秋天的意象。APPROVE
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='写一首关于秋季的 4 行俳句诗。', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=33, completion_tokens=31), content="Crimson leaves cascade,  \nWhispering winds sing of change,  \nChill wraps the fading,  \nNature's quilt, rich and warm.", type='TextMessage'), TextMessage(source='gemini_critic', models_usage=RequestUsage(prompt_tokens=86, completion_tokens=60), content="这首诗不错，但是有四行而不是三行。俳句必须有 5-7-5 音节结构的三行。内容富有秋意，但形式不正确。请修改以遵守俳句的音节结构。\n", type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=141, completion_tokens=49), content='谢谢你的反馈！这是一首遵循 5-7-5 音节结构的修改后的俳句：\n\nCrimson leaves drift down,  \nChill winds whisper through the gold,  \nAutumn’s breath is near.', type='TextMessage'), TextMessage(source='gemini_critic', models_usage=RequestUsage(prompt_tokens=211, completion_tokens=32), content='修改后的俳句有了很大的改进。它正确地遵循了 5-7-5 音节结构并保持了秋天的意象。APPROVE\n', type='TextMessage')], stop_reason="Text 'APPROVE' mentioned")
    

在上面的部分中，我们展示了一些非常重要的概念：

  * 我们开发了一个使用 Google Gemini SDK 响应消息的自定义智能体。

  * 我们展示了此自定义智能体可以用作更广泛的 AgentChat 生态系统的一部分 - 在本例中是 [`RoundRobinGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 中的一个参与者，只要它继承自 [`BaseChatAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent "autogen_agentchat.agents.BaseChatAgent")。

## 使自定义智能体可声明化#

Autogen 提供了一个 [Component](https://microsoft.github.io/autogen/dev/user-guide/core-user-guide/framework/component-config.html) 接口，用于将组件的配置序列化为声明式格式。这对于保存和加载配置以及与他人共享配置很有用。

我们通过继承 `Component` 类并实现 `_from_config` 和 `_to_config` 方法来实现这一点。可以使用 `dump_component` 方法将声明式类序列化为 JSON 格式，并使用 `load_component` 方法从 JSON 格式反序列化。
    
    
    import os
    from typing import AsyncGenerator, Sequence
    
    from autogen_agentchat.agents import BaseChatAgent
    from autogen_agentchat.base import Response
    from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
    from autogen_core import CancellationToken, Component
    from pydantic import BaseModel
    from typing_extensions import Self
    
    
    class GeminiAssistantAgentConfig(BaseModel):
        name: str
        description: str = "一个提供帮助并具有使用工具的能力的智能体。"
        model: str = "gemini-1.5-flash-002"
        system_message: str | None = None
    
    
    class GeminiAssistantAgent(BaseChatAgent, Component[GeminiAssistantAgentConfig]):  # type: ignore[no-redef]
        component_config_schema = GeminiAssistantAgentConfig
        # component_provider_override = "mypackage.agents.GeminiAssistantAgent"
    
        def __init__(
            self,
            name: str,
            description: str = "一个提供帮助并具有使用工具的能力的智能体。",
            model: str = "gemini-1.5-flash-002",
            api_key: str = os.environ["GEMINI_API_KEY"],
            system_message: str
            | None = "你是一个乐于助人的助手，可以响应消息。当任务完成时回复 TERMINATE。",
        ):
            super().__init__(name=name, description=description)
            self._model_context = UnboundedChatCompletionContext()
            self._model_client = genai.Client(api_key=api_key)
            self._system_message = system_message
            self._model = model
    
        @property
        def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
            return (TextMessage,)
    
        async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
            final_response = None
            async for message in self.on_messages_stream(messages, cancellation_token):
                if isinstance(message, Response):
                    final_response = message
    
            if final_response is None:
                raise AssertionError("流应返回最终结果。")
    
            return final_response
    
        async def on_messages_stream(
            self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken
        ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:
            # 将消息添加到模型上下文
            for msg in messages:
                await self._model_context.add_message(msg.to_model_message())
    
            # 获取对话历史
            history = [
                (msg.source if hasattr(msg, "source") else "system")
                + ": "
                + (msg.content if isinstance(msg.content, str) else "")
                + "\n"
                for msg in await self._model_context.get_messages()
            ]
    
            # 使用 Gemini 生成响应
            response = self._model_client.models.generate_content(
                model=self._model,
                contents=f"历史：{history}\n根据历史，请提供响应",
                config=types.GenerateContentConfig(
                    system_instruction=self._system_message,
                    temperature=0.3,
                ),
            )
    
            # 创建使用情况元数据
            usage = RequestUsage(
                prompt_tokens=response.usage_metadata.prompt_token_count,
                completion_tokens=response.usage_metadata.candidates_token_count,
            )
    
            # 将响应添加到模型上下文
            await self._model_context.add_message(AssistantMessage(content=response.text, source=self.name))
    
            # 生成最终响应
            yield Response(
                chat_message=TextMessage(content=response.text, source=self.name, models_usage=usage),
                inner_messages=[],
            )
    
        async def on_reset(self, cancellation_token: CancellationToken) -> None:
            """通过清除模型上下文来重置助手。"""
            await self._model_context.clear()
    
        @classmethod
        def _from_config(cls, config: GeminiAssistantAgentConfig) -> Self:
            return cls(
                name=config.name, description=config.description, model=config.model, system_message=config.system_message
            )
    
        def _to_config(self) -> GeminiAssistantAgentConfig:
            return GeminiAssistantAgentConfig(
                name=self.name,
                description=self.description,
                model=self._model,
                system_message=self._system_message,
            )
    

现在我们已经实现了必需的方法，我们现在可以将自定义智能体加载和转储到 JSON 格式，然后从 JSON 格式加载智能体。

> 注意：你应该将 `component_provider_override` 类变量设置为包含自定义智能体类的模块的完整路径，例如（`mypackage.agents.GeminiAssistantAgent`）。这由 `load_component` 方法用于确定如何实例化该类。
    
    
    gemini_assistant = GeminiAssistantAgent("gemini_assistant")
    config = gemini_assistant.dump_component()
    print(config.model_dump_json(indent=2))
    loaded_agent = GeminiAssistantAgent.load_component(config)
    print(loaded_agent)
    
    
    
    {
      "provider": "__main__.GeminiAssistantAgent",
      "component_type": "agent",
      "version": 1,
      "component_version": 1,
      "description": null,
      "label": "GeminiAssistantAgent",
      "config": {
        "name": "gemini_assistant",
        "description": "一个提供帮助并具有使用工具的能力的智能体。",
        "model": "gemini-1.5-flash-002",
        "system_message": "你是一个乐于助人的助手，可以响应消息。当任务完成时回复 TERMINATE。"
      }
    }
    <__main__.GeminiAssistantAgent object at 0x11a5c5a90>
    

## 后续步骤#

到目前为止，我们已经了解了如何创建自定义智能体、将自定义模型客户端添加到智能体以及使自定义智能体可声明化。有几种方式可以扩展此基本示例：

  * 扩展 Gemini 模型客户端以处理类似于 [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 类的函数调用。<https://ai.google.dev/gemini-api/docs/function-calling>

  * 实现一个包含自定义智能体的包，并尝试在 [AutoGen Studio](https://microsoft.github.io/autogen/stable/user-guide/autogenstudio-user-guide/index.html) 等工具中使用其声明式格式。

__本页内容

[ __在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/custom-agents.ipynb)

[ __查看源文件](../../_sources/user-guide/agentchat-user-guide/custom-agents.ipynb.txt)