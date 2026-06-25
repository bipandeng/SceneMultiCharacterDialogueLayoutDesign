[跳到主要内容](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/intro.html#main-content)

回到顶部`Ctrl` + `K`

浅色深色系统设置

- [GitHub](https://github.com/microsoft/autogen)
- [Discord](https://aka.ms/autogen-discord)
- [Twitter](https://twitter.com/pyautogen)

# 简介 [\#](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/intro.html\#intro "链接到此标题")

代理可以通过多种方式协同工作来解决问题。
[AutoGen](https://aka.ms/autogen-paper)、
[MetaGPT](https://arxiv.org/abs/2308.00352)
和 [ChatDev](https://arxiv.org/abs/2307.07924) 等研究工作表明，
多代理系统在软件开发等复杂任务中优于单代理系统。

多代理设计模式是从消息协议中涌现的结构：
它描述了代理如何相互交互以解决问题。
例如，上一节中的[配备工具的代理](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/components/tools.html#tool-equipped-agent)采用了一种称为 ReAct 的设计模式，
其中涉及代理与工具进行交互。

你可以使用 AutoGen 代理实现任何多代理设计模式。
在接下来的两节中，我们将讨论两种常见的设计模式：
用于任务分解的群组聊天，以及用于增强鲁棒性的反思模式。

[在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/design-patterns/intro.md)

[显示源代码](https://microsoft.github.io/autogen/stable/_sources/user-guide/core-user-guide/design-patterns/intro.md.txt)
