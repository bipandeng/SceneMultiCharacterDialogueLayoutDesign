<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/core-concepts/agent-identity-and-lifecycle.html -->

# 智能体标识与生命周期#

智能体运行时(agent runtime)负责管理智能体的标识与生命周期。应用程序并不直接创建智能体,而是为智能体实例的工厂函数注册一个智能体类型(agent type)。在本节中,我们将解释运行时如何识别和创建智能体。

## 智能体 ID#

智能体 ID(Agent ID)在智能体运行时(包括分布式运行时)中唯一标识一个智能体实例。它是该智能体实例用于接收消息的"地址"。它由两个部分组成:智能体类型(agent type)和智能体键(agent key)。

Note

Agent ID = (Agent Type, Agent Key)

智能体类型并不是某个智能体类(agent class)。它将一个智能体与一个特定的工厂函数相关联,该工厂函数生成同一智能体类型的实例。例如,不同的工厂函数可以生成相同的智能体类,但使用不同的构造函数参数。智能体键是给定智能体类型的实例标识符。Agent ID 可以与字符串相互转换。该字符串的格式为:

Note

Agent_Type/Agent_Key

类型(Type)与键(Key)被视为有效的条件是:它们只包含字母数字字符 (a-z) 和 (0-9),或下划线 (_)。一个有效的标识符不能以数字开头,也不能包含任何空格。

在多智能体应用中,智能体类型通常由应用程序直接定义,即在应用程序代码中定义。另一方面,智能体键通常根据传递给智能体的消息生成,即它们由应用数据定义。

例如,某个运行时已经注册了智能体类型 `"code_reviewer"`,其工厂函数生成的智能体实例用于执行代码评审。每个代码评审请求都有一个唯一的 ID `review_request_id`,用于标记一个专用的会话。在这种情况下,每个请求可以由一个具有智能体 ID `("code_reviewer", review_request_id)` 的新实例来处理。

## 智能体生命周期#

当运行时根据 ID 将消息递送给某个智能体实例时,它要么取出该实例,要么在实例不存在时创建一个新的实例。

![Agent Lifecycle](../../../_images/agent-lifecycle.svg)

运行时还负责对智能体实例进行"换入"或"换出",以节省资源并平衡多台机器之间的负载。此功能尚未实现。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/core-concepts/agent-identity-and-lifecycle.md)

[ __Show Source](../../../_sources/user-guide/core-user-guide/core-concepts/agent-identity-and-lifecycle.md.txt)