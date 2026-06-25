<!-- 来源: https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.runtimes.grpc.html -->

# autogen_ext.runtimes.grpc#

_class _GrpcWorkerAgentRuntime(_host_address : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _tracer_provider : TracerProvider | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _extra_grpc_config : [Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence "\(in Python v3.14\)")[[Tuple](https://docs.python.org/3/library/typing.html#typing.Tuple "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _payload_serialization_format : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") = JSON_DATA_CONTENT_TYPE_)[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime)#
    

Bases: [`AgentRuntime`](autogen_core.html#autogen_core.AgentRuntime "autogen_core._agent_runtime.AgentRuntime")

用于运行远程或跨语言智能体的智能体运行时。

智能体消息传递使用来自 [agent_worker.proto](https://github.com/microsoft/autogen/blob/main/protos/agent_worker.proto) 的 protobuf 和来自 [cloudevent.proto](https://github.com/microsoft/autogen/blob/main/protos/cloudevent.proto) 的 `CloudEvent`。

跨语言智能体还需要所有智能体对在智能体之间发送的任何消息类型使用共享的 protobuf 模式。

_async _start() → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.start)#
    

在后台任务中启动运行时。

_async _stop() → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.stop)#
    

立即停止运行时。

_async _stop_when_signal(_signals : [Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence "\(in Python v3.14\)")[[Signals](https://docs.python.org/3/library/signal.html#signal.Signals "\(in Python v3.14\)")] = (signal.SIGTERM, signal.SIGINT)_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.stop_when_signal)#
    

在收到信号时停止运行时。

_async _send_message(_message : [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")_, _recipient : [AgentId](autogen_core.html#autogen_core.AgentId "autogen_core._agent_id.AgentId")_, _*_ , _sender : [AgentId](autogen_core.html#autogen_core.AgentId "autogen_core._agent_id.AgentId") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _message_id : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_) → [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.send_message)#
    

向智能体发送消息并获取响应。

参数：
    

  * **message** (_Any_) – 要发送的消息。

  * **recipient** ([_AgentId_](autogen_core.html#autogen_core.AgentId "autogen_core.AgentId")) – 要将消息发送到的智能体。

  * **sender** ([_AgentId_](autogen_core.html#autogen_core.AgentId "autogen_core.AgentId") _|__None_ _,__optional_) – 发送消息的智能体。如果这是从外部直接发送到运行时的，则**只能**为 None。默认为 None。

  * **cancellation_token** ([_CancellationToken_](autogen_core.html#autogen_core.CancellationToken "autogen_core.CancellationToken") _|__None_ _,__optional_) – 用于取消正在进行的操作的令牌。默认为 None。

引发：
    

  * [**CantHandleException**](autogen_core.exceptions.html#autogen_core.exceptions.CantHandleException "autogen_core.exceptions.CantHandleException") – 如果接收方无法处理该消息。

  * [**UndeliverableException**](autogen_core.exceptions.html#autogen_core.exceptions.UndeliverableException "autogen_core.exceptions.UndeliverableException") – 如果消息无法传递。

  * **Other** – 接收方引发的任何其他异常。

返回：
    

**Any** – 来自智能体的响应。

_async _publish_message(_message : [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")_, _topic_id : [TopicId](autogen_core.html#autogen_core.TopicId "autogen_core._topic.TopicId")_, _*_ , _sender : [AgentId](autogen_core.html#autogen_core.AgentId "autogen_core._agent_id.AgentId") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _message_id : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.publish_message)#
    

将消息发布到给定命名空间中的所有智能体，如果未提供命名空间，则发布到发送方的命名空间。

不期望从发布中获得响应。

参数：
    

  * **message** (_Any_) – 要发布的消息。

  * **topic_id** ([_TopicId_](autogen_core.html#autogen_core.TopicId "autogen_core.TopicId")) – 要将消息发布到的主题。

  * **sender** ([_AgentId_](autogen_core.html#autogen_core.AgentId "autogen_core.AgentId") _|__None_ _,__optional_) – 发送消息的智能体。默认为 None。

  * **cancellation_token** ([_CancellationToken_](autogen_core.html#autogen_core.CancellationToken "autogen_core.CancellationToken") _|__None_ _,__optional_) – 用于取消正在进行的操作的令牌。默认为 None。

  * **message_id** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _|__None_ _,__optional_) – 消息 ID。如果为 None，将生成新的消息 ID。默认为 None。此消息 ID 必须唯一，建议使用 UUID。

引发：
    

[**UndeliverableException**](autogen_core.exceptions.html#autogen_core.exceptions.UndeliverableException "autogen_core.exceptions.UndeliverableException") – 如果消息无法传递。

_async _save_state() → [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")][[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.save_state)#
    

保存整个运行时的状态，包括所有托管的智能体。恢复状态的唯一方法是将其传递给 `load_state()`。

状态的结构由实现定义，可以是任何 JSON 可序列化对象。

返回：
    

**Mapping[str, Any]** – 保存的状态。

_async _load_state(_state : [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.load_state)#
    

加载整个运行时的状态，包括所有托管的智能体。该状态应与 `save_state()` 返回的状态相同。

参数：
    

**state** (_Mapping_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__Any_ _]_) – 保存的状态。

_async _agent_metadata(_agent : [AgentId](autogen_core.html#autogen_core.AgentId "autogen_core._agent_id.AgentId")_) → [AgentMetadata](autogen_core.html#autogen_core.AgentMetadata "autogen_core._agent_metadata.AgentMetadata")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.agent_metadata)#
    

获取智能体的元数据。

参数：
    

**agent** ([_AgentId_](autogen_core.html#autogen_core.AgentId "autogen_core.AgentId")) – 智能体 ID。

返回：
    

**AgentMetadata** – 智能体元数据。

_async _agent_save_state(_agent : [AgentId](autogen_core.html#autogen_core.AgentId "autogen_core._agent_id.AgentId")_) → [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")][[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.agent_save_state)#
    

保存单个智能体的状态。

状态的结构由实现定义，可以是任何 JSON 可序列化对象。

参数：
    

**agent** ([_AgentId_](autogen_core.html#autogen_core.AgentId "autogen_core.AgentId")) – 智能体 ID。

返回：
    

**Mapping[str, Any]** – 保存的状态。

_async _agent_load_state(_agent : [AgentId](autogen_core.html#autogen_core.AgentId "autogen_core._agent_id.AgentId")_, _state : [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.agent_load_state)#
    

加载单个智能体的状态。

参数：
    

  * **agent** ([_AgentId_](autogen_core.html#autogen_core.AgentId "autogen_core.AgentId")) – 智能体 ID。

  * **state** (_Mapping_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__Any_ _]_) – 保存的状态。

_async _register_factory(_type : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [AgentType](autogen_core.html#autogen_core.AgentType "autogen_core._agent_type.AgentType")_, _agent_factory : [Callable](https://docs.python.org/3/library/typing.html#typing.Callable "\(in Python v3.14\)")[[], T | [Awaitable](https://docs.python.org/3/library/typing.html#typing.Awaitable "\(in Python v3.14\)")[T]]_, _*_ , _expected_class : [type](https://docs.python.org/3/library/functions.html#type "\(in Python v3.14\)")[T] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_) → [AgentType](autogen_core.html#autogen_core.AgentType "autogen_core._agent_type.AgentType")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.register_factory)#
    

使用与特定类型关联的智能体工厂注册到运行时。该类型必须是唯一的。此 API 不会添加任何订阅。

注意

这是一个低级 API，通常应使用智能体类的 register 方法，因为它也会自动处理订阅。

示例：
    
    
    from dataclasses import dataclass
    
    from autogen_core import AgentRuntime, MessageContext, RoutedAgent, event
    from autogen_core.models import UserMessage
    
    
    @dataclass
    class MyMessage:
        content: str
    
    
    class MyAgent(RoutedAgent):
        def __init__(self) -> None:
            super().__init__("My core agent")
    
        @event
        async def handler(self, message: UserMessage, context: MessageContext) -> None:
            print("Event received: ", message.content)
    
    
    async def my_agent_factory():
        return MyAgent()
    
    
    async def main() -> None:
        runtime: AgentRuntime = ...  # type: ignore
        await runtime.register_factory("my_agent", lambda: MyAgent())
    
    
    import asyncio
    
    asyncio.run(main())
    

参数：
    

  * **type** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – 此工厂创建的智能体类型。它与智能体类名不同。type 参数用于区分不同的工厂函数，而不是智能体类。

  * **agent_factory** (_Callable_ _[__[__]__,__T_ _]_) – 创建智能体的工厂，其中 T 是具体的智能体类型。在工厂内部，使用 autogen_core.AgentInstantiationContext 访问变量，如当前运行时和智能体 ID。

  * **expected_class** ([_type_](https://docs.python.org/3/library/functions.html#type "\(in Python v3.14\)") _[__T_ _]__|__None_ _,__optional_) – 智能体的预期类，用于运行时对工厂进行验证。默认为 None。如果为 None，则不执行验证。

_async _register_agent_instance(_agent_instance : [Agent](autogen_core.html#autogen_core.Agent "autogen_core._agent.Agent")_, _agent_id : [AgentId](autogen_core.html#autogen_core.AgentId "autogen_core._agent_id.AgentId")_) → [AgentId](autogen_core.html#autogen_core.AgentId "autogen_core._agent_id.AgentId")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.register_agent_instance)#
    

将智能体实例注册到运行时。该类型可以被重用，但每个 agent_id 必须唯一。同一类型内的所有智能体实例必须是相同的对象类型。此 API 不会添加任何订阅。

注意

这是一个低级 API，通常应使用智能体类的 register_instance 方法，因为它也会自动处理订阅。

示例：
    
    
    from dataclasses import dataclass
    
    from autogen_core import AgentId, AgentRuntime, MessageContext, RoutedAgent, event
    from autogen_core.models import UserMessage
    
    
    @dataclass
    class MyMessage:
        content: str
    
    
    class MyAgent(RoutedAgent):
        def __init__(self) -> None:
            super().__init__("My core agent")
    
        @event
        async def handler(self, message: UserMessage, context: MessageContext) -> None:
            print("Event received: ", message.content)
    
    
    async def main() -> None:
        runtime: AgentRuntime = ...  # type: ignore
        agent = MyAgent()
        await runtime.register_agent_instance(
            agent_instance=agent, agent_id=AgentId(type="my_agent", key="default")
        )
    
    
    import asyncio
    
    asyncio.run(main())
    

参数：
    

  * **agent_instance** ([_Agent_](autogen_core.html#autogen_core.Agent "autogen_core.Agent")) – 智能体的具体实例。

  * **agent_id** ([_AgentId_](autogen_core.html#autogen_core.AgentId "autogen_core.AgentId")) – 智能体的标识符。智能体的类型是 agent_id.type。

_async _try_get_underlying_agent_instance(_id : [AgentId](autogen_core.html#autogen_core.AgentId "autogen_core._agent_id.AgentId")_, _type : [Type](https://docs.python.org/3/library/typing.html#typing.Type "\(in Python v3.14\)")[T] = Agent_) → T[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.try_get_underlying_agent_instance)#
    

尝试通过名称和命名空间获取底层智能体实例。这通常是不被鼓励的（因此名称很长），但在某些情况下可能有用。

如果底层智能体不可访问，这将引发异常。

参数：
    

  * **id** ([_AgentId_](autogen_core.html#autogen_core.AgentId "autogen_core.AgentId")) – 智能体 ID。

  * **type** (_Type_ _[__T_ _]__,__optional_) – 智能体的预期类型。默认为 Agent。

返回：
    

**T** – 具体的智能体实例。

引发：
    

  * [**LookupError**](https://docs.python.org/3/library/exceptions.html#LookupError "\(in Python v3.14\)") – 如果未找到智能体。

  * [**NotAccessibleError**](autogen_core.exceptions.html#autogen_core.exceptions.NotAccessibleError "autogen_core.exceptions.NotAccessibleError") – 如果智能体不可访问，例如它位于远程。

  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError "\(in Python v3.14\)") – 如果智能体不是预期的类型。

_async _add_subscription(_subscription : [Subscription](autogen_core.html#autogen_core.Subscription "autogen_core._subscription.Subscription")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.add_subscription)#
    

添加一个运行时在处理已发布消息时应满足的新订阅。

参数：
    

**subscription** ([_Subscription_](autogen_core.html#autogen_core.Subscription "autogen_core.Subscription")) – 要添加的订阅。

_async _remove_subscription(_id : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.remove_subscription)#
    

从运行时中删除订阅。

参数：
    

**id** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – 要删除的订阅的 ID。

引发：
    

[**LookupError**](https://docs.python.org/3/library/exceptions.html#LookupError "\(in Python v3.14\)") – 如果订阅不存在。

_async _get(_id_or_type : [AgentId](autogen_core.html#autogen_core.AgentId "autogen_core._agent_id.AgentId") | [AgentType](autogen_core.html#autogen_core.AgentType "autogen_core._agent_type.AgentType") | [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _/_ , _key : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") = 'default'_, _*_ , _lazy : [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") = True_) → [AgentId](autogen_core.html#autogen_core.AgentId "autogen_core._agent_id.AgentId")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.get)#
    

add_message_serializer(_serializer : [MessageSerializer](autogen_core.html#autogen_core.MessageSerializer "autogen_core._serialization.MessageSerializer")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")] | [Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence "\(in Python v3.14\)")[[MessageSerializer](autogen_core.html#autogen_core.MessageSerializer "autogen_core._serialization.MessageSerializer")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]]_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime.html#GrpcWorkerAgentRuntime.add_message_serializer)#
    

向运行时添加新的消息序列化器。

注意：这将根据 type_name 和 data_content_type 属性对序列化器进行去重。

参数：
    

**serializer** ([_MessageSerializer_](autogen_core.html#autogen_core.MessageSerializer "autogen_core.MessageSerializer") _[__Any_ _]__|__Sequence_ _[_[_MessageSerializer_](autogen_core.html#autogen_core.MessageSerializer "autogen_core.MessageSerializer") _[__Any_ _]__]_) – 要添加的序列化器。

_class _GrpcWorkerAgentRuntimeHost(_address : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _extra_grpc_config : [Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence "\(in Python v3.14\)")[[Tuple](https://docs.python.org/3/library/typing.html#typing.Tuple "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")]] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_)[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime_host.html#GrpcWorkerAgentRuntimeHost)#
    

Bases: [`object`](https://docs.python.org/3/library/functions.html#object "\(in Python v3.14\)")

start() → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime_host.html#GrpcWorkerAgentRuntimeHost.start)#
    

在后台任务中启动服务器。

_async _stop(_grace : [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") = 5_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime_host.html#GrpcWorkerAgentRuntimeHost.stop)#
    

停止服务器。

_async _stop_when_signal(_grace : [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") = 5_, _signals : [Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence "\(in Python v3.14\)")[[Signals](https://docs.python.org/3/library/signal.html#signal.Signals "\(in Python v3.14\)")] = (signal.SIGTERM, signal.SIGINT)_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime_host.html#GrpcWorkerAgentRuntimeHost.stop_when_signal)#
    

在收到信号时停止服务器。

_class _GrpcWorkerAgentRuntimeHostServicer[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime_host_servicer.html#GrpcWorkerAgentRuntimeHostServicer)#
    

Bases: [`AgentRpcServicer`](autogen_ext.runtimes.grpc.protos.agent_worker_pb2_grpc.html#autogen_ext.runtimes.grpc.protos.agent_worker_pb2_grpc.AgentRpcServicer "autogen_ext.runtimes.grpc.protos.agent_worker_pb2_grpc.AgentRpcServicer")

一个为智能体托管消息传递服务的 gRPC servicer。

_async _OpenChannel(_request_iterator : [AsyncIterator](https://docs.python.org/3/library/typing.html#typing.AsyncIterator "\(in Python v3.14\)")[Message]_, _context : ServicerContext[Message, Message]_) → [AsyncIterator](https://docs.python.org/3/library/typing.html#typing.AsyncIterator "\(in Python v3.14\)")[Message][[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime_host_servicer.html#GrpcWorkerAgentRuntimeHostServicer.OpenChannel)#
    

.proto 文件中缺少关联的文档注释。

_async _OpenControlChannel(_request_iterator : [AsyncIterator](https://docs.python.org/3/library/typing.html#typing.AsyncIterator "\(in Python v3.14\)")[ControlMessage]_, _context : ServicerContext[ControlMessage, ControlMessage]_) → [AsyncIterator](https://docs.python.org/3/library/typing.html#typing.AsyncIterator "\(in Python v3.14\)")[ControlMessage][[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime_host_servicer.html#GrpcWorkerAgentRuntimeHostServicer.OpenControlChannel)#
    

.proto 文件中缺少关联的文档注释。

_async _RegisterAgent(_request : RegisterAgentTypeRequest_, _context : ServicerContext[RegisterAgentTypeRequest, RegisterAgentTypeResponse]_) → RegisterAgentTypeResponse[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime_host_servicer.html#GrpcWorkerAgentRuntimeHostServicer.RegisterAgent)#
    

.proto 文件中缺少关联的文档注释。

_async _AddSubscription(_request : AddSubscriptionRequest_, _context : ServicerContext[AddSubscriptionRequest, AddSubscriptionResponse]_) → AddSubscriptionResponse[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime_host_servicer.html#GrpcWorkerAgentRuntimeHostServicer.AddSubscription)#
    

.proto 文件中缺少关联的文档注释。

_async _RemoveSubscription(_request : RemoveSubscriptionRequest_, _context : ServicerContext[RemoveSubscriptionRequest, RemoveSubscriptionResponse]_) → RemoveSubscriptionResponse[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime_host_servicer.html#GrpcWorkerAgentRuntimeHostServicer.RemoveSubscription)#
    

.proto 文件中缺少关联的文档注释。

_async _GetSubscriptions(_request : GetSubscriptionsRequest_, _context : ServicerContext[GetSubscriptionsRequest, GetSubscriptionsResponse]_) → GetSubscriptionsResponse[[source]](../../_modules/autogen_ext/runtimes/grpc/_worker_runtime_host_servicer.html#GrpcWorkerAgentRuntimeHostServicer.GetSubscriptions)#
    

.proto 文件中缺少关联的文档注释。

__本页内容

[ __在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/reference/python/autogen_ext.runtimes.grpc.rst)

[ __查看源文件](../../_sources/reference/python/autogen_ext.runtimes.grpc.rst.txt)