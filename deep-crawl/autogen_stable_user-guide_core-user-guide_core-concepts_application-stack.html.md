<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/core-concepts/application-stack.html -->

# 应用栈#

AutoGen core 被设计成一个不固执己见的(unopinionated)框架,可用于构建各种类型的多智能体应用。它并不绑定于任何特定的智能体抽象或多智能体模式。

下图展示了应用栈的结构。

![Application Stack](../../../_images/application-stack.svg)

栈的底部是基础的 messaging 和 routing 设施,使得智能体之间能够彼此通信。这些由 agent runtime 管理,对于大多数应用,开发者只需与运行时提供的高级 API 交互(参见 [Agent and Agent Runtime](../framework/agent-and-agent-runtime.html))。

在栈的顶部,开发者需要定义智能体之间交换的消息类型。这一组消息类型构成了一份行为契约(behavior contract),智能体必须遵守该契约,而契约的具体实现决定了智能体如何处理消息。行为契约有时也被称为消息协议(message protocol)。实现该行为契约是开发者的责任。多智能体模式正是从这些行为契约中涌现出来的(参见 [Multi-Agent Design Patterns](../design-patterns/intro.html))。

## 一个应用示例#

考虑一个用于代码生成的多智能体应用的具体例子。该应用包含三个智能体:Coder Agent(编码智能体)、Executor Agent(执行智能体)与 Reviewer Agent(评审智能体)。下图展示了智能体之间的数据流以及它们之间交换的消息类型。

![Code Generation Example](../../../_images/code-gen-example.svg)

在该示例中,行为契约由以下几部分组成:

  * 从应用程序发送到 Coder Agent 的 `CodingTaskMsg` 消息

  * 从 Coder Agent 发送到 Executor Agent 的 `CodeGenMsg`

  * 从 Executor Agent 发送到 Reviewer Agent 的 `ExecutionResultMsg`

  * 从 Reviewer Agent 发送到 Coder Agent 的 `ReviewMsg`

  * 从 Reviewer Agent 发送到应用程序的 `CodingResultMsg`

行为契约由智能体对这些消息的处理方式来实现。例如,Reviewer Agent 监听 `ExecutionResultMsg`,并对代码执行结果进行评估以决定批准还是拒绝。如果批准,它会向应用程序发送一条 `CodingResultMsg`;否则,它会向 Coder Agent 发送一条 `ReviewMsg`,以开启新一轮的代码生成。

该行为契约是一种被称为 _reflection_(反思) 的多智能体模式的实例,其中一轮的生成结果会被另一轮生成所审视,以提升整体质量。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/core-concepts/application-stack.md)

[ __Show Source](../../../_sources/user-guide/core-user-guide/core-concepts/application-stack.md.txt)