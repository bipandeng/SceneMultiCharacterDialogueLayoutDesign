<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/framework/agent-and-agent-runtime.html -->

# 代理与代理运行时#

在本节和接下来的小节中，我们将重点关注 AutoGen 的核心概念：代理、代理运行时、消息和通信——这些是多代理应用程序的基础构建块。

注意

Core API 旨在保持无意见且灵活。因此，有时您可能会觉得它有挑战性。如果您正在构建交互式、可扩展和分布式的多代理系统，并希望完全控制所有工作流，请继续阅读。如果您只想快速运行某些东西，可以查看 [AgentChat API](../../agentchat-user-guide/index.html)。

AutoGen 中的代理是由基接口 [`Agent`](../../../reference/python/autogen_core.html#autogen_core.Agent "autogen_core.Agent") 定义的实体。它具有 [`AgentId`](../../../reference/python/autogen_core.html#autogen_core.AgentId "autogen_core.AgentId") 类型的唯一标识符，以及 [`AgentMetadata`](../../../reference/python/autogen_core.html#autogen_core.AgentMetadata "autogen_core.AgentMetadata") 类型的元数据字典。

在大多数情况下，您可以从更高级的类 [`RoutedAgent`](../../../reference/python/autogen_core.html#autogen_core.RoutedAgent "autogen_core.RoutedAgent") 派生子类，这使您能够使用 [`message_handler()`](../../../reference/python/autogen_core.html#autogen_core.message_handler "autogen_core.message_handler") 装饰器以及对 `message` 变量的正确类型提示，将消息路由到相应的消息处理程序。代理运行时是 AutoGen 中代理的执行环境。

类似于编程语言的运行时环境，代理运行时提供了必要的基础设施，以促进代理之间的通信、管理代理生命周期、强制安全边界，并支持监控和调试。

对于本地开发，开发人员可以使用 [`SingleThreadedAgentRuntime`](../../../reference/python/autogen_core.html#autogen_core.SingleThreadedAgentRuntime "autogen_core.SingleThreadedAgentRuntime")，它可以嵌入到 Python 应用程序中。

注意

代理不是由应用程序代码直接实例化和管理。相反，它们在需要时由运行时创建并由运行时管理。

如果您已经熟悉 [AgentChat](../../agentchat-user-guide/index.html)，请务必注意，AgentChat 的代理（如 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent")）由应用程序创建，因此不直接由运行时管理。要在 Core 中使用 AgentChat 代理，您需要创建一个包装 Core 代理，将消息委托给 AgentChat 代理，并让运行时管理包装器代理。

## 实现一个代理#

要实现一个代理，开发人员必须派生子类 [`RoutedAgent`](../../../reference/python/autogen_core.html#autogen_core.RoutedAgent "autogen_core.RoutedAgent") 类，并使用 [`message_handler()`](../../../reference/python/autogen_core.html#autogen_core.message_handler "autogen_core.message_handler") 装饰器为代理预期处理的每种消息类型实现一个消息处理程序方法。例如，以下代理处理一个简单的消息类型 `MyMessageType` 并打印它接收到的消息：
    
    
    from dataclasses import dataclass
    
    from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
    
    
    @dataclass
    class MyMessageType:
        content: str
    
    
    class MyAgent(RoutedAgent):
        def __init__(self) -> None:
            super().__init__("MyAgent")
    
        @message_handler
        async def handle_my_message_type(self, message: MyMessageType, ctx: MessageContext) -> None:
            print(f"{self.id.type} received message: {message.content}")
    

此代理仅处理 `MyMessageType`，消息将被传递到 `handle_my_message_type` 方法。开发人员可以通过使用 [`message_handler()`](../../../reference/python/autogen_core.html#autogen_core.message_handler "autogen_core.message_handler") 装饰器并为处理程序函数中的 `message` 变量设置类型提示来为不同的消息类型拥有多个消息处理程序。如果更适合代理的逻辑，您还可以在一个消息处理程序函数中利用 [python typing union](https://docs.python.org/3/library/typing.html#typing.Union) 作为 `message` 变量。请参阅下一节关于 [消息和通信](message-and-communication.html) 的内容。

## 使用 AgentChat 代理#

如果您有 [AgentChat](../../agentchat-user-guide/index.html) 代理并希望在 Core API 中使用它，您可以创建一个包装 [`RoutedAgent`](../../../reference/python/autogen_core.html#autogen_core.RoutedAgent "autogen_core.RoutedAgent")，将消息委托给 AgentChat 代理。以下示例展示了如何为 AgentChat 中的 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 创建包装器代理。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.messages import TextMessage
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    
    class MyAssistant(RoutedAgent):
        def __init__(self, name: str) -> None:
            super().__init__(name)
            model_client = OpenAIChatCompletionClient(model="gpt-4o")
            self._delegate = AssistantAgent(name, model_client=model_client)
    
        @message_handler
        async def handle_my_message_type(self, message: MyMessageType, ctx: MessageContext) -> None:
            print(f"{self.id.type} received message: {message.content}")
            response = await self._delegate.on_messages(
                [TextMessage(content=message.content, source="user")], ctx.cancellation_token
            )
            print(f"{self.id.type} responded: {response.chat_message}")
    

有关如何使用模型客户端的信息，请参阅 [Model Client](../components/model-clients.html) 一节。

由于 Core API 是不带意见的，您不需要使用 AgentChat API 来使用 Core API。您可以实现自己的代理或使用另一个代理框架。

## 注册代理类型#

要使代理对运行时可用，开发人员可以使用 [`BaseAgent`](../../../reference/python/autogen_core.html#autogen_core.BaseAgent "autogen_core.BaseAgent") 类的 [`register()`](../../../reference/python/autogen_core.html#autogen_core.BaseAgent.register "autogen_core.BaseAgent.register") 类方法。注册过程关联了一个代理类型（由字符串唯一标识）和一个用于创建给定类的代理类型实例的工厂函数。工厂函数用于在需要时自动创建代理实例。

代理类型（[`AgentType`](../../../reference/python/autogen_core.html#autogen_core.AgentType "autogen_core.AgentType")）与代理类不同。在此示例中，代理类型是 `AgentType("my_agent")` 或 `AgentType("my_assistant")`，而代理类是 Python 类 `MyAgent` 或 `MyAssistantAgent`。工厂函数应返回调用 [`register()`](../../../reference/python/autogen_core.html#autogen_core.BaseAgent.register "autogen_core.BaseAgent.register") 类方法的代理类的实例。阅读 [代理身份和生命周期](../core-concepts/agent-identity-and-lifecycle.html) 以了解有关代理类型和身份的更多信息。

注意

不同的代理类型可以使用返回相同代理类的工厂函数进行注册。例如，在工厂函数中，可以使用构造函数参数的变化来创建同一代理类的不同实例。

要使用 [`SingleThreadedAgentRuntime`](../../../reference/python/autogen_core.html#autogen_core.SingleThreadedAgentRuntime "autogen_core.SingleThreadedAgentRuntime") 注册我们的代理类型，可以使用以下代码：
    
    
    from autogen_core import SingleThreadedAgentRuntime
    
    runtime = SingleThreadedAgentRuntime()
    await MyAgent.register(runtime, "my_agent", lambda: MyAgent())
    await MyAssistant.register(runtime, "my_assistant", lambda: MyAssistant("my_assistant"))
    
    
    
    AgentType(type='my_assistant')
    

注册代理类型后，我们可以使用 [`AgentId`](../../../reference/python/autogen_core.html#autogen_core.AgentId "autogen_core.AgentId") 向代理实例发送直接消息。运行时将在第一次向此实例传递消息时创建该实例。
    
    
    runtime.start()  # Start processing messages in the background.
    await runtime.send_message(MyMessageType("Hello, World!"), AgentId("my_agent", "default"))
    await runtime.send_message(MyMessageType("Hello, World!"), AgentId("my_assistant", "default"))
    await runtime.stop()  # Stop processing messages in the background.
    
    
    
    my_agent received message: Hello, World!
    my_assistant received message: Hello, World!
    my_assistant responded: Hello! How can I assist you today?
    

注意

由于运行时管理代理的生命周期，因此 [`AgentId`](../../../reference/python/autogen_core.html#autogen_core.AgentId "autogen_core.AgentId") 仅用于与代理通信或检索其元数据（例如描述）。

## 运行单线程代理运行时#

上面的代码片段使用 [`start()`](../../../reference/python/autogen_core.html#autogen_core.SingleThreadedAgentRuntime.start "autogen_core.SingleThreadedAgentRuntime.start") 启动一个后台任务来处理和传递消息给接收方的消息处理程序。这是本地嵌入式运行时 [`SingleThreadedAgentRuntime`](../../../reference/python/autogen_core.html#autogen_core.SingleThreadedAgentRuntime "autogen_core.SingleThreadedAgentRuntime") 的一个功能。

要立即停止后台任务，请使用 [`stop()`](../../../reference/python/autogen_core.html#autogen_core.SingleThreadedAgentRuntime.stop "autogen_core.SingleThreadedAgentRuntime.stop") 方法：
    
    
    runtime.start()
    # ... Send messages, publish messages, etc.
    await runtime.stop()  # This will return immediately but will not cancel
    # any in-progress message handling.
    

您可以通过再次调用 [`start()`](../../../reference/python/autogen_core.html#autogen_core.SingleThreadedAgentRuntime.start "autogen_core.SingleThreadedAgentRuntime.start") 来恢复后台任务。

对于批处理场景（例如运行评估代理的基准测试），您可能希望在没有未处理消息且没有代理正在处理消息时自动停止后台任务——此时可以认为批处理已完成。您可以通过使用 [`stop_when_idle()`](../../../reference/python/autogen_core.html#autogen_core.SingleThreadedAgentRuntime.stop_when_idle "autogen_core.SingleThreadedAgentRuntime.stop_when_idle") 方法来实现此目的：
    
    
    runtime.start()
    # ... Send messages, publish messages, etc.
    await runtime.stop_when_idle()  # This will block until the runtime is idle.
    

要关闭运行时并释放资源，请使用 [`close()`](../../../reference/python/autogen_core.html#autogen_core.SingleThreadedAgentRuntime.close "autogen_core.SingleThreadedAgentRuntime.close") 方法：
    
    
    await runtime.close()
    

其他运行时实现将有自己运行运行时的方式。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/framework/agent-and-agent-runtime.ipynb)

[ __Show Source](../../../_sources/user-guide/core-user-guide/framework/agent-and-agent-runtime.ipynb.txt)
