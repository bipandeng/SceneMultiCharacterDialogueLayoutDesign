<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/core-concepts/agent-and-multi-agent-application.html -->

# 智能体与多智能体应用#

**智能体(Agent)** 是一个软件实体,它通过消息进行通信,维护自身的状态,并在收到消息或自身状态发生变化时执行动作。这些动作可能会修改智能体的状态,并产生外部效果,例如更新消息日志、发送新消息、执行代码或调用 API。

许多软件系统都可以被建模为一组相互作用的独立智能体。示例包括:

  * 工厂车间中的传感器

  * 为 Web 应用提供支持的分布式服务

  * 涉及多个相关方的业务流程

  * AI 智能体,例如由语言模型(例如 GPT-4)驱动的智能体,它们能够编写代码、与外部系统进行交互,并与其他智能体进行通信。

由多个相互作用的智能体所组成的这些系统,被称为**多智能体应用(multi-agent application)**。

> **注意:**  
>  AI 智能体通常在其软件栈中使用语言模型来解释消息、执行推理并执行动作。

## 多智能体应用的特性#

在多智能体应用中,智能体可以:

  * 运行于同一进程或同一台机器上

  * 跨不同的机器或组织边界进行运作

  * 使用不同的编程语言实现,并使用不同的 AI 模型或指令

  * 通过消息传递协调彼此的动作,以共同实现某个共享目标

每个智能体都是一个自包含(self-contained)的单元,可以独立开发、测试和部署。这种模块化设计使得智能体可以在不同的场景中复用,并组合成更复杂的系统。

智能体本质上是**可组合(composable)** 的:简单的智能体可以组合起来,形成复杂的、可适应的应用,其中每个智能体都为整个系统贡献特定的功能或服务。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/core-concepts/agent-and-multi-agent-application.md)

[ __Show Source](../../../_sources/user-guide/core-user-guide/core-concepts/agent-and-multi-agent-application.md.txt)