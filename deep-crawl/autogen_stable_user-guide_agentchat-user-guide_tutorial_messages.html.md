<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/messages.html -->

# 消息#

在 AutoGen AgentChat 中，_消息_ 促进与其他代理、编排器和应用程序之间的通信和信息交换。AgentChat 支持多种消息类型，每种类型都为特定目的而设计。

## 消息类型#

从高层次来看，AgentChat 中的消息可以分为两类：代理间消息和代理内部事件与消息。

### 代理间消息#

AgentChat 支持多种用于代理间通信的消息类型。它们属于基类 [`BaseChatMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage") 的子类。具体子类涵盖基本文本和多模态通信，如 [`TextMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.TextMessage "autogen_agentchat.messages.TextMessage") 和 [`MultiModalMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.MultiModalMessage "autogen_agentchat.messages.MultiModalMessage")。

例如，以下代码片段演示如何创建文本消息，该消息接受字符串内容和字符串来源：
    
    
    from autogen_agentchat.messages import TextMessage
    
    text_message = TextMessage(content="Hello, world!", source="User")
    

同样，以下代码片段演示如何创建多模态消息，该消息接受字符串列表或 [`Image`](../../../reference/python/autogen_core.html#autogen_core.Image "autogen_core.Image") 对象：
    
    
    from io import BytesIO
    
    import requests
    from autogen_agentchat.messages import MultiModalMessage
    from autogen_core import Image as AGImage
    from PIL import Image
    
    pil_image = Image.open(BytesIO(requests.get("https://picsum.photos/300/200").content))
    img = AGImage(pil_image)
    multi_modal_message = MultiModalMessage(content=["Can you describe the content of this image?", img], source="User")
    img
    


我们创建的 [`TextMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.TextMessage "autogen_agentchat.messages.TextMessage") 和 [`MultiModalMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.MultiModalMessage "autogen_agentchat.messages.MultiModalMessage") 可以通过 [`on_messages`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.ChatAgent.on_messages "autogen_agentchat.base.ChatAgent.on_messages") 方法直接传递给代理，或者作为任务提供给团队的 [`run()`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run "autogen_agentchat.teams.BaseGroupChat.run") 方法。消息也用于代理的响应中。我们将在 [代理](agents.html) 和 [团队](teams.html) 中更详细地解释这些内容。

### 内部事件#

AgentChat 还支持 `事件` 的概念——代理内部的消息。这些消息用于在代理本身内部通信事件和操作信息，并属于基类 [`BaseAgentEvent`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseAgentEvent "autogen_agentchat.messages.BaseAgentEvent") 的子类。

示例包括 [`ToolCallRequestEvent`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallRequestEvent "autogen_agentchat.messages.ToolCallRequestEvent")，表示请求调用工具，以及 [`ToolCallExecutionEvent`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallExecutionEvent "autogen_agentchat.messages.ToolCallExecutionEvent")，包含工具调用的结果。

通常，事件由代理自身创建，并包含在从 [`on_messages`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.ChatAgent.on_messages "autogen_agentchat.base.ChatAgent.on_messages") 返回的 [`Response`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.Response "autogen_agentchat.base.Response") 的 [`inner_messages`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.Response.inner_messages "autogen_agentchat.base.Response.inner_messages") 字段中。如果您正在构建自定义代理并且有需要与其他实体（例如 UI）通信的事件，可以将这些事件包含在 [`Response`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.Response "autogen_agentchat.base.Response") 的 [`inner_messages`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.Response.inner_messages "autogen_agentchat.base.Response.inner_messages") 字段中。我们将在 [自定义代理](../custom-agents.html) 中展示这方面的示例。

您可以在 AgentChat 的 [`messages`](../../../reference/python/autogen_agentchat.messages.html#module-autogen_agentchat.messages "autogen_agentchat.messages") 模块中阅读支持的全部消息类型。

## 自定义消息类型#

您可以通过继承基类 [`BaseChatMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage") 或 [`BaseAgentEvent`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseAgentEvent "autogen_agentchat.messages.BaseAgentEvent") 来创建自定义消息类型。这允许您定义自己的消息格式和行为，以满足您的应用程序需求。自定义消息类型在编写自定义代理时很有用。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/tutorial/messages.ipynb)

[ __Show Source](../../../_sources/user-guide/agentchat-user-guide/tutorial/messages.ipynb.txt)
