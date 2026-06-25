<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/core-concepts/architecture.html -->

# 智能体运行时环境#

在最基础的层面上,该框架提供了一个 _运行时环境_(runtime environment),它负责促进智能体之间的通信、管理智能体的身份与生命周期,并强制实施安全和隐私边界。

它支持两种类型的运行时环境:_standalone_(独立)和 _distributed_(分布式)。这两种类型都提供了一组用于构建多智能体应用的通用 API,因此你可以在不修改智能体实现的前提下,在它们之间进行切换。每种类型也可以有多种实现。

## 独立智能体运行时#

独立运行时(Standalone runtime)适用于单进程应用,所有智能体均使用相同的编程语言实现,并运行在同一个进程中。在 Python API 中,独立运行时的一个示例是 [`SingleThreadedAgentRuntime`](../../../reference/python/autogen_core.html#autogen_core.SingleThreadedAgentRuntime "autogen_core.SingleThreadedAgentRuntime")。

下图展示了框架中的独立运行时。

![Standalone Runtime](../../../_images/architecture-standalone.svg)

在此,智能体通过运行时通过消息进行通信,运行时负责管理智能体的 _生命周期_(lifecycle)。

开发者可以使用框架提供的组件快速构建智能体,这些组件包括 _routed agent_(路由智能体)、AI 模型 _clients_(客户端)、AI 模型的工具、代码执行沙箱、模型上下文存储等等。他们也可以从零开始实现自己的智能体,或使用其他库。

## 分布式智能体运行时#

分布式运行时(Distributed runtime)适用于多进程应用,智能体可能使用不同的编程语言实现,并运行在不同的机器上。

![Distributed Runtime](../../../_images/architecture-distributed.svg)

如上图所示,分布式运行时由一个 _host servicer_(宿主服务)和多个 _workers_(工作节点)组成。宿主服务促进跨工作节点的智能体之间的通信,并维护连接的状态。工作节点运行智能体,并通过 _gateways_(网关)与宿主服务进行通信。它们向宿主服务通告(advertise)其所运行的智能体,并管理这些智能体的生命周期。

在分布式运行时中,智能体的工作方式与独立运行时中相同,因此开发者可以在两种运行时类型之间进行切换,而无需对其智能体实现做任何修改。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/core-concepts/architecture.md)

[ __Show Source](../../../_sources/user-guide/core-user-guide/core-concepts/architecture.md.txt)