<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/quickstart.html -->

# 快速入门#

注意

请参阅 [此处](installation.html) 获取安装说明。

在深入研究核心 API 之前，让我们从一个简单的示例开始，即两个代理从 10 倒数到 1。

我们首先定义代理类及其各自的消息处理过程。我们创建两个代理类：`Modifier` 和 `Checker`。`Modifier` 代理修改给定的数字，`Check` 代理根据条件检查该值。我们还创建了一个 `Message` 数据类，它定义了代理之间传递的消息。
    
    
    from dataclasses import dataclass
    from typing import Callable
    
    from autogen_core import DefaultTopicId, MessageContext, RoutedAgent, default_subscription, message_handler
    
    
    @dataclass
    class Message:
        content: int
    
    
    @default_subscription
    class Modifier(RoutedAgent):
        def __init__(self, modify_val: Callable[[int], int]) -> None:
            super().__init__("A modifier agent.")
            self._modify_val = modify_val
    
        @message_handler
        async def handle_message(self, message: Message, ctx: MessageContext) -> None:
            val = self._modify_val(message.content)
            print(f"{'-'*80}\nModifier:\nModified {message.content} to {val}")
            await self.publish_message(Message(content=val), DefaultTopicId())  # type: ignore
    
    
    @default_subscription
    class Checker(RoutedAgent):
        def __init__(self, run_until: Callable[[int], bool]) -> None:
            super().__init__("A checker agent.")
            self._run_until = run_until
    
        @message_handler
        async def handle_message(self, message: Message, ctx: MessageContext) -> None:
            if not self._run_until(message.content):
                print(f"{'-'*80}\nChecker:\n{message.content} passed the check, continue.")
                await self.publish_message(Message(content=message.content), DefaultTopicId())
            else:
                print(f"{'-'*80}\nChecker:\n{message.content} failed the check, stopping.")
    

您可能已经注意到，代理的逻辑（无论是使用模型还是代码执行器）完全与消息的传递方式解耦。这就是核心思想：框架提供通信基础设施，代理负责自己的逻辑。我们将通信基础设施称为 **代理运行时（Agent Runtime）**。

代理运行时是此框架的一个关键概念。除了传递消息外，它还管理代理的生命周期。因此，代理的创建由运行时处理。

以下代码展示了如何使用 [`SingleThreadedAgentRuntime`](../../reference/python/autogen_core.html#autogen_core.SingleThreadedAgentRuntime "autogen_core.SingleThreadedAgentRuntime")（一个本地嵌入式代理运行时实现）注册和运行代理。

注意

如果您使用的是 VSCode 或其他编辑器，请记得导入 asyncio 并将代码包装在 `async def main() -> None:` 中，然后使用 `asyncio.run(main())` 函数运行代码。
    
    
    from autogen_core import AgentId, SingleThreadedAgentRuntime
    
    # Create a local embedded runtime.
    runtime = SingleThreadedAgentRuntime()
    
    # Register the modifier and checker agents by providing
    # their agent types, the factory functions for creating instance and subscriptions.
    await Modifier.register(
        runtime,
        "modifier",
        # Modify the value by subtracting 1
        lambda: Modifier(modify_val=lambda x: x - 1),
    )
    
    await Checker.register(
        runtime,
        "checker",
        # Run until the value is less than or equal to 1
        lambda: Checker(run_until=lambda x: x <= 1),
    )
    
    # Start the runtime and send a direct message to the checker.
    runtime.start()
    await runtime.send_message(Message(10), AgentId("checker", "default"))
    await runtime.stop_when_idle()
    
    
    
    --------------------------------------------------------------------------------
    Checker:
    10 passed the check, continue.
    --------------------------------------------------------------------------------
    Modifier:
    Modified 10 to 9
    --------------------------------------------------------------------------------
    Checker:
    9 passed the check, continue.
    --------------------------------------------------------------------------------
    Modifier:
    Modified 9 to 8
    --------------------------------------------------------------------------------
    Checker:
    8 passed the check, continue.
    --------------------------------------------------------------------------------
    Modifier:
    Modified 8 to 7
    --------------------------------------------------------------------------------
    Checker:
    7 passed the check, continue.
    --------------------------------------------------------------------------------
    Modifier:
    Modified 7 to 6
    --------------------------------------------------------------------------------
    Checker:
    6 passed the check, continue.
    --------------------------------------------------------------------------------
    Modifier:
    Modified 6 to 5
    --------------------------------------------------------------------------------
    Checker:
    5 passed the check, continue.
    --------------------------------------------------------------------------------
    Modifier:
    Modified 5 to 4
    --------------------------------------------------------------------------------
    Checker:
    4 passed the check, continue.
    --------------------------------------------------------------------------------
    Modifier:
    Modified 4 to 3
    --------------------------------------------------------------------------------
    Checker:
    3 passed the check, continue.
    --------------------------------------------------------------------------------
    Modifier:
    Modified 3 to 2
    --------------------------------------------------------------------------------
    Checker:
    2 passed the check, continue.
    --------------------------------------------------------------------------------
    Modifier:
    Modified 2 to 1
    --------------------------------------------------------------------------------
    Checker:
    1 failed the check, stopping.
    

从代理的输出中，我们可以看到该值已按照 modifier 和 checker 条件从 10 成功递减到 1。

AutoGen 还支持分布式代理运行时，它可以在不同进程或机器上运行具有不同身份、语言和依赖关系的代理。

要了解如何使用代理运行时、通信、消息处理和订阅，请继续阅读本快速入门之后的章节。

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/quickstart.ipynb)

[ __Show Source](../../_sources/user-guide/core-user-guide/quickstart.ipynb.txt)
