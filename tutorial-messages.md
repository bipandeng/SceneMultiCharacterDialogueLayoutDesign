[跳到主要内容](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/messages.html#main-content)

回到顶部`Ctrl` + `K`

浅色深色系统设置

- [GitHub](https://github.com/microsoft/autogen)
- [Discord](https://aka.ms/autogen-discord)
- [Twitter](https://twitter.com/pyautogen)

# 消息 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/messages.html\#messages "链接到此标题")

在 AutoGen AgentChat 中，_消息_促进了与其他代理、协调器和应用程序之间的通信和信息交换。AgentChat 支持多种消息类型，每种类型都针对特定用途而设计。

## 消息类型 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/messages.html\#types-of-messages "链接到此标题")

从高层来看，AgentChat 中的消息可以分为两类：代理间消息和代理的内部事件及消息。

### 代理间消息 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/messages.html\#agent-agent-messages "链接到此标题")

AgentChat 支持多种用于代理间通信的消息类型。它们属于基类 [`BaseChatMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage") 的子类。具体子类涵盖了基本文本和多模态通信，如 [`TextMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.TextMessage "autogen_agentchat.messages.TextMessage") 和 [`MultiModalMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.MultiModalMessage "autogen_agentchat.messages.MultiModalMessage")。

例如，以下代码片段演示了如何创建文本消息，它接受字符串内容和字符串来源：

```
from autogen_agentchat.messages import TextMessage

text_message = TextMessage(content="Hello, world!", source="User")
```

复制到剪贴板

类似地，以下代码片段演示了如何创建多模态消息，它接受字符串或 [`Image`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.html#autogen_core.Image "autogen_core.Image") 对象的列表：

```
from io import BytesIO

import requests
from autogen_agentchat.messages import MultiModalMessage
from autogen_core import Image as AGImage
from PIL import Image

pil_image = Image.open(BytesIO(requests.get("https://picsum.photos/300/200").content))
img = AGImage(pil_image)
multi_modal_message = MultiModalMessage(content=["Can you describe the content of this image?", img], source="User")
img
```

复制到剪贴板

![](<Base64-Image-Removed>)

我们创建的 [`TextMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.TextMessage "autogen_agentchat.messages.TextMessage") 和 [`MultiModalMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.MultiModalMessage "autogen_agentchat.messages.MultiModalMessage") 可以通过 [`on_messages`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.ChatAgent.on_messages "autogen_agentchat.base.ChatAgent.on_messages") 方法直接传递给代理，或者作为任务传递给团队的 [`run()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run "autogen_agentchat.teams.BaseGroupChat.run") 方法。消息也用于代理的响应中。我们将在[代理](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html)和[团队](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html)中更详细地解释这些内容。

### 内部事件 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/messages.html\#internal-events "链接到此标题")

AgentChat 还支持 `events` 的概念——代理内部的消息。这些消息用于在代理_内部_通信事件和操作信息，属于基类 [`BaseAgentEvent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseAgentEvent "autogen_agentchat.messages.BaseAgentEvent") 的子类。

这些示例包括 [`ToolCallRequestEvent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallRequestEvent "autogen_agentchat.messages.ToolCallRequestEvent")，表示发出了调用工具的请求，以及 [`ToolCallExecutionEvent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallExecutionEvent "autogen_agentchat.messages.ToolCallExecutionEvent")，包含工具调用的结果。

通常，事件由代理本身创建，并包含在 [`on_messages`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.ChatAgent.on_messages "autogen_agentchat.base.ChatAgent.on_messages") 返回的 [`Response`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.Response "autogen_agentchat.base.Response") 的 [`inner_messages`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.Response.inner_messages "autogen_agentchat.base.Response.inner_messages") 字段中。如果你正在构建自定义代理，并且有想要传达给其他实体（例如 UI）的事件，你可以将它们包含在 [`Response`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.Response "autogen_agentchat.base.Response") 的 [`inner_messages`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.Response.inner_messages "autogen_agentchat.base.Response.inner_messages") 字段中。我们将在[自定义代理](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/custom-agents.html)中展示这方面的示例。

你可以在 AgentChat 的 [`messages`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#module-autogen_agentchat.messages "autogen_agentchat.messages") 模块中阅读 AgentChat 支持的全部消息集。

## 自定义消息类型 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/messages.html\#custom-message-types "链接到此标题")

你可以通过子类化基类 [`BaseChatMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage") 或 [`BaseAgentEvent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseAgentEvent "autogen_agentchat.messages.BaseAgentEvent") 来创建自定义消息类型。这允许你定义自己的消息格式和行为，以适应你的应用程序。自定义消息类型在编写自定义代理时非常有用。

在此页面上


[在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/tutorial/messages.ipynb)

[显示源代码](https://microsoft.github.io/autogen/stable/_sources/user-guide/agentchat-user-guide/tutorial/messages.ipynb.txt)
