<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/intro.html -->

# 介绍#

智能体可以以多种方式协同工作来解决问题。研究工作如 [AutoGen](https://aka.ms/autogen-paper)、[MetaGPT](https://arxiv.org/abs/2308.00352) 和 [ChatDev](https://arxiv.org/abs/2307.07924) 已经表明,在软件开发等复杂任务上,多智能体系统的表现优于单智能体系统。

多智能体设计模式是一种从消息协议中涌现出来的结构:它描述了智能体之间如何相互作用以解决问题。例如,上一节中介绍的[配备工具的智能体](../components/tools.html#tool-equipped-agent)采用了一种被称为 ReAct 的设计模式,该模式涉及智能体与工具的交互。

你可以使用 AutoGen 智能体实现任何多智能体设计模式。在接下来的两节中,我们将讨论两种常见的设计模式:用于任务分解的群聊,以及用于提升鲁棒性的反思(reflection)。

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/design-patterns/intro.md)

[ __Show Source](../../../_sources/user-guide/core-user-guide/design-patterns/intro.md.txt)