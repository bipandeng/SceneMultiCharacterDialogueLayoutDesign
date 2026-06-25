<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/framework/message-and-communication.html -->

# 消息与通信#

AutoGen core 中的代理可以对消息做出反应、发送和发布消息，并且消息是代理之间相互通信的唯一方式。

## 消息#

消息是可序列化的对象，可以使用以下方式定义：

  * Pydantic 的 `pydantic.BaseModel` 的子类，或

  * 一个 dataclass

例如：
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class TextMessage:
        content: str
        source: str
    
    
    @dataclass
    class ImageMessage:
        url: str
        source: str
    

注意

消息是纯粹的数据，不应包含任何逻辑。

## 消息处理程序#

当代理收到消息时，运行时将调用代理的消息处理程序（[`on_message()`](../../../reference/python/autogen_core.html#autogen_core.Agent.on_message "autogen_core.Agent.on_message")），该处理程序应实现代理的消息处理逻辑。如果此消息无法被代理处理，代理应抛出 [`CantHandleException`](../../../reference/python/autogen_core.exceptions.html#autogen_core.exceptions.CantHandleException "autogen_core.exceptions.CantHandleException")。

基类 [`BaseAgent`](../../../reference/python/autogen_core.html#autogen_core.BaseAgent "autogen_core.BaseAgent") 不提供任何消息处理逻辑，除非是高级用例，否则不建议直接实现 [`on_message()`](../../../reference/python/autogen_core.html#autogen_core.Agent.on_message "autogen_core.Agent.on_message") 方法。

开发人员应从实现 [`RoutedAgent`](../../../reference/python/autogen_core.html#autogen_core.RoutedAgent "autogen_core.RoutedAgent") 基类开始，它提供内置的消息路由功能。

### 按类型路由消息#

[`RoutedAgent`](../../../reference/python/autogen_core.html#autogen_core.RoutedAgent "autogen_core.RoutedAgent") 基类提供了一种使用 `message_handler()` 装饰器将消息类型与消息处理程序相关联的机制，因此开发人员无需实现 [`on_message()`](../../../reference/python/autogen_core.html#autogen_core.Agent.on_message "autogen_core.Agent.on_message") 方法。

例如，以下类型路由的代理使用不同的消息处理程序来响应 `TextMessage` 和 `ImageMessage`：
    
    
    from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler
    
    
    class MyAgent(RoutedAgent):
        @message_handler
        async def on_text_message(self, message: TextMessage, ctx: MessageContext) -> None:
            print(f"Hello, {message.source}, you said {message.content}!")
    
        @message_handler
        async def on_image_message(self, message: ImageMessage, ctx: MessageContext) -> None:
            print(f"Hello, {message.source}, you sent me {message.url}!")
    

创建代理运行时并注册代理类型（请参阅 [代理与代理运行时](agent-and-agent-runtime.html)）：
    
    
    runtime = SingleThreadedAgentRuntime()
    await MyAgent.register(runtime, "my_agent", lambda: MyAgent("My Agent"))
    
    
    
    AgentType(type='my_agent')
    

使用 `TextMessage` 和 `ImageMessage` 测试此代理。
    
    
    runtime.start()
    agent_id = AgentId("my_agent", "default")
    await runtime.send_message(TextMessage(content="Hello, World!", source="User"), agent_id)
    await runtime.send_message(ImageMessage(url="https://example.com/image.jpg", source="User"), agent_id)
    await runtime.stop_when_idle()
    
    
    
    Hello, User, you said Hello, World!!
    Hello, User, you sent me https://example.com/image.jpg!
    

运行时在传递第一条消息时会自动创建带有代理 ID `AgentId("my_agent", "default")` 的 `MyAgent` 实例。

### 路由相同类型的消息#

在某些场景中，将相同类型的消息路由到不同的处理程序很有用。例如，来自不同发送方代理的消息应以不同方式处理。您可以使用 `message_handler()` 装饰器的 `match` 参数。

`match` 参数将相同消息类型的处理程序与特定消息相关联——它次于消息类型路由。它接受一个可调用对象，该可调用对象接受消息和 [`MessageContext`](../../../reference/python/autogen_core.html#autogen_core.MessageContext "autogen_core.MessageContext") 作为参数，并返回一个布尔值，指示是否应由装饰的处理程序处理该消息。可调用对象按处理程序的字母顺序进行检查。

下面是使用 `match` 参数根据发送方代理路由消息的代理示例：
    
    
    class RoutedBySenderAgent(RoutedAgent):
        @message_handler(match=lambda msg, ctx: msg.source.startswith("user1"))  # type: ignore
        async def on_user1_message(self, message: TextMessage, ctx: MessageContext) -> None:
            print(f"Hello from user 1 handler, {message.source}, you said {message.content}!")
    
        @message_handler(match=lambda msg, ctx: msg.source.startswith("user2"))  # type: ignore
        async def on_user2_message(self, message: TextMessage, ctx: MessageContext) -> None:
            print(f"Hello from user 2 handler, {message.source}, you said {message.content}!")
    
        @message_handler(match=lambda msg, ctx: msg.source.startswith("user2"))  # type: ignore
        async def on_image_message(self, message: ImageMessage, ctx: MessageContext) -> None:
            print(f"Hello, {message.source}, you sent me {message.url}!")
    

上述代理使用消息的 `source` 字段来确定发送方代理。如果可用，您还可以使用 [`MessageContext`](../../../reference/python/autogen_core.html#autogen_core.MessageContext "autogen_core.MessageContext") 的 `sender` 字段通过代理 ID 来确定发送方代理。

让我们使用具有不同 `source` 值的消息测试此代理：
    
    
    runtime = SingleThreadedAgentRuntime()
    await RoutedBySenderAgent.register(runtime, "my_agent", lambda: RoutedBySenderAgent("Routed by sender agent"))
    runtime.start()
    agent_id = AgentId("my_agent", "default")
    await runtime.send_message(TextMessage(content="Hello, World!", source="user1-test"), agent_id)
    await runtime.send_message(TextMessage(content="Hello, World!", source="user2-test"), agent_id)
    await runtime.send_message(ImageMessage(url="https://example.com/image.jpg", source="user1-test"), agent_id)
    await runtime.send_message(ImageMessage(url="https://example.com/image.jpg", source="user2-test"), agent_id)
    await runtime.stop_when_idle()
    
    
    
    Hello from user 1 handler, user1-test, you said Hello, World!!
    Hello from user 2 handler, user2-test, you said Hello, World!!
    Hello, user2-test, you sent me https://example.com/image.jpg!
    

在上面的示例中，第一个 `ImageMessage` 未被处理，因为消息的 `source` 字段与处理程序的 `match` 条件不匹配。

## 直接消息传递#

AutoGen core 中有两种类型的通信：

  * **直接消息传递（Direct Messaging）** ：将直接消息发送给另一个代理。

  * **广播（Broadcast）** ：将消息发布到主题。

让我们先看看直接消息传递。要向另一个代理发送直接消息，请在消息处理程序中使用 [`autogen_core.BaseAgent.send_message()`](../../../reference/python/autogen_core.html#autogen_core.BaseAgent.send_message "autogen_core.BaseAgent.send_message") 方法，在运行时中使用 [`autogen_core.AgentRuntime.send_message()`](../../../reference/python/autogen_core.html#autogen_core.AgentRuntime.send_message "autogen_core.AgentRuntime.send_message") 方法。等待这些方法的调用将返回接收代理的消息处理程序的返回值。当接收代理的处理程序返回 `None` 时，将返回 `None`。

注意

如果在发送方等待时调用的代理抛出异常，该异常将被传播回发送方。

### 请求/响应#

直接消息传递可用于请求/响应场景，其中发送方期望从接收方获得响应。接收方可以通过从其消息处理程序返回值来响应消息。您可以将其视为代理之间的函数调用。

例如，考虑以下代理：
    
    
    from dataclasses import dataclass
    
    from autogen_core import MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler
    
    
    @dataclass
    class Message:
        content: str
    
    
    class InnerAgent(RoutedAgent):
        @message_handler
        async def on_my_message(self, message: Message, ctx: MessageContext) -> Message:
            return Message(content=f"Hello from inner, {message.content}")
    
    
    class OuterAgent(RoutedAgent):
        def __init__(self, description: str, inner_agent_type: str):
            super().__init__(description)
            self.inner_agent_id = AgentId(inner_agent_type, self.id.key)
    
        @message_handler
        async def on_my_message(self, message: Message, ctx: MessageContext) -> None:
            print(f"Received message: {message.content}")
            # Send a direct message to the inner agent and receives a response.
            response = await self.send_message(Message(f"Hello from outer, {message.content}"), self.inner_agent_id)
            print(f"Received inner response: {response.content}")
    

收到消息后，`OuterAgent` 向 `InnerAgent` 发送直接消息并接收响应消息。

我们可以通过向 `OuterAgent` 发送 `Message` 来测试这些代理。
    
    
    runtime = SingleThreadedAgentRuntime()
    await InnerAgent.register(runtime, "inner_agent", lambda: InnerAgent("InnerAgent"))
    await OuterAgent.register(runtime, "outer_agent", lambda: OuterAgent("OuterAgent", "inner_agent"))
    runtime.start()
    outer_agent_id = AgentId("outer_agent", "default")
    await runtime.send_message(Message(content="Hello, World!"), outer_agent_id)
    await runtime.stop_when_idle()
    
    
    
    Received message: Hello, World!
    Received inner response: Hello from inner, Hello from outer, Hello, World!
    

两个输出都由 `OuterAgent` 的消息处理程序产生，但第二个输出基于来自 `InnerAgent` 的响应。

一般来说，当发送方和接收方紧密耦合时（它们是一起创建的，并且发送方链接到接收方的特定实例），直接消息传递适用于这些场景。例如，代理通过向 [`ToolAgent`](../../../reference/python/autogen_core.tool_agent.html#autogen_core.tool_agent.ToolAgent "autogen_core.tool_agent.ToolAgent") 的实例发送直接消息来执行工具调用，并使用响应形成一个动作-观察循环。

## 广播#

广播实际上是带有主题和订阅的发布/订阅模型。阅读 [主题和订阅](../core-concepts/topic-and-subscription.html) 以了解核心概念。

直接消息传递和广播之间的关键区别在于广播不能用于请求/响应场景。当代理发布消息时，它是单向的，它不能从任何其他代理接收响应，即使接收代理的处理程序返回一个值。

注意

如果对已发布的消息提供了响应，它将被丢弃。

注意

如果代理发布它订阅的消息类型，它将不会收到它发布的消息。这是为了防止无限循环。

### 订阅和发布主题#

[基于类型的订阅](../core-concepts/topic-and-subscription.html#type-based-subscription) 将发布到给定主题类型的主题的消息映射到给定代理类型的代理。要使继承自 [`RoutedAgent`](../../../reference/python/autogen_core.html#autogen_core.RoutedAgent "autogen_core.RoutedAgent") 的代理订阅给定主题类型的主题，您可以使用 `type_subscription()` 类装饰器。

以下示例展示了一个 `ReceiverAgent` 类，它使用 `type_subscription()` 装饰器订阅 `"default"` 主题类型的主题，并打印接收到的消息。
    
    
    from autogen_core import RoutedAgent, message_handler, type_subscription
    
    
    @type_subscription(topic_type="default")
    class ReceivingAgent(RoutedAgent):
        @message_handler
        async def on_my_message(self, message: Message, ctx: MessageContext) -> None:
            print(f"Received a message: {message.content}")
    

要从代理的处理程序发布消息，请使用 [`publish_message()`](../../../reference/python/autogen_core.html#autogen_core.BaseAgent.publish_message "autogen_core.BaseAgent.publish_message") 方法并指定 [`TopicId`](../../../reference/python/autogen_core.html#autogen_core.TopicId "autogen_core.TopicId")。此调用仍必须等待以允许运行时安排将消息传递给所有订阅者，但它将始终返回 `None`。如果代理在处理已发布消息时抛出异常，则将记录此异常，但不会传播回发布代理。

以下示例展示了一个 `BroadcastingAgent`，它在收到消息时向主题发布消息。
    
    
    from autogen_core import TopicId
    
    
    class BroadcastingAgent(RoutedAgent):
        @message_handler
        async def on_my_message(self, message: Message, ctx: MessageContext) -> None:
            await self.publish_message(
                Message("Publishing a message from broadcasting agent!"),
                topic_id=TopicId(type="default", source=self.id.key),
            )
    

`BroadcastingAgent` 将消息发布到类型为 `"default"` 且来源分配给代理实例的代理键的主题。

订阅在代理运行时中注册，可以作为代理类型注册的一部分，也可以通过单独的 API 方法进行注册。下面是我们如何使用 `type_subscription()` 装饰器为接收代理注册 `TypeSubscription`，以及如何在没有装饰器的情况下为广播代理注册 `TypeSubscription`。
    
    
    from autogen_core import TypeSubscription
    
    runtime = SingleThreadedAgentRuntime()
    
    # Option 1: with type_subscription decorator
    # The type_subscription class decorator automatically adds a TypeSubscription to
    # the runtime when the agent is registered.
    await ReceivingAgent.register(runtime, "receiving_agent", lambda: ReceivingAgent("Receiving Agent"))
    
    # Option 2: with TypeSubscription
    await BroadcastingAgent.register(runtime, "broadcasting_agent", lambda: BroadcastingAgent("Broadcasting Agent"))
    await runtime.add_subscription(TypeSubscription(topic_type="default", agent_type="broadcasting_agent"))
    
    # Start the runtime and publish a message.
    runtime.start()
    await runtime.publish_message(
        Message("Hello, World! From the runtime!"), topic_id=TopicId(type="default", source="default")
    )
    await runtime.stop_when_idle()
    
    
    
    Received a message: Hello, World! From the runtime!
    Received a message: Publishing a message from broadcasting agent!
    

如上面的示例所示，您还可以通过运行时的 [`publish_message()`](../../../reference/python/autogen_core.html#autogen_core.AgentRuntime.publish_message "autogen_core.AgentRuntime.publish_message") 方法直接发布到主题，而无需创建代理实例。

从输出中，您可以看到接收代理收到了两条消息：一条是通过运行时发布的，另一条是由广播代理发布的。

### 默认主题和订阅#

在上面的示例中，我们使用 [`TopicId`](../../../reference/python/autogen_core.html#autogen_core.TopicId "autogen_core.TopicId") 和 `TypeSubscription` 来分别指定主题和订阅。这对于许多场景是适当的方式。但是，当只有一个发布范围时，即所有代理都发布和订阅所有广播消息，我们可以使用便利类 `DefaultTopicId` 和 `default_subscription()` 来简化我们的代码。

`DefaultTopicId` 用于创建使用 `"default"` 作为主题类型的默认值以及使用发布代理的键作为主题来源的默认值的主题。`default_subscription()` 用于创建订阅默认主题的类型订阅。我们可以通过使用 `DefaultTopicId` 和 `default_subscription()` 来简化 `BroadcastingAgent`。
    
    
    from autogen_core import DefaultTopicId, default_subscription
    
    
    @default_subscription
    class BroadcastingAgentDefaultTopic(RoutedAgent):
        @message_handler
        async def on_my_message(self, message: Message, ctx: MessageContext) -> None:
            # Publish a message to all agents in the same namespace.
            await self.publish_message(
                Message("Publishing a message from broadcasting agent!"),
                topic_id=DefaultTopicId(),
            )
    

当运行时调用 [`register()`](../../../reference/python/autogen_core.html#autogen_core.BaseAgent.register "autogen_core.BaseAgent.register") 来注册代理类型时，它会创建一个 `TypeSubscription`，其主题类型使用 `"default"` 作为默认值，代理类型使用在同一上下文中正在注册的相同代理类型。
    
    
    runtime = SingleThreadedAgentRuntime()
    await BroadcastingAgentDefaultTopic.register(
        runtime, "broadcasting_agent", lambda: BroadcastingAgentDefaultTopic("Broadcasting Agent")
    )
    await ReceivingAgent.register(runtime, "receiving_agent", lambda: ReceivingAgent("Receiving Agent"))
    runtime.start()
    await runtime.publish_message(Message("Hello, World! From the runtime!"), topic_id=DefaultTopicId())
    await runtime.stop_when_idle()
    
    
    
    Received a message: Hello, World! From the runtime!
    Received a message: Publishing a message from broadcasting agent!
    

注意

如果您的场景允许所有代理发布和订阅所有广播消息，请使用 `DefaultTopicId` 和 `default_subscription()` 来装饰您的代理类。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/framework/message-and-communication.ipynb)

[ __Show Source](../../../_sources/user-guide/core-user-guide/framework/message-and-communication.ipynb.txt)
