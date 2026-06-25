<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/core-concepts/topic-and-subscription.html -->

# 主题与订阅#

运行时通过两种方式投递消息:直接消息(direct messaging)或广播(broadcast)。直接消息是一对一的:发送方必须提供接收方的智能体 ID。另一方面,广播是一对多的,发送方不需要提供接收方的智能体 ID。

许多场景适合使用广播。例如,在事件驱动的工作流中,智能体并不总是知道谁将处理它们的消息,而一个工作流可以由彼此之间没有相互依赖关系的智能体组成。本节聚焦于广播中的核心概念:主题(Topic)和订阅(Subscription)。

## 主题#

主题(Topic)定义了广播消息的范围。本质上,agent runtime 通过其广播 API 实现了一种发布-订阅模型:在发布消息时,必须指定主题。它是对智能体 ID 的一种间接(indirection)。

一个主题由两个部分组成:主题类型(topic type)和主题源(topic source)。

Note

Topic = (Topic Type, Topic Source)

类似于同样具有两个组成部分的 [agent ID](agent-identity-and-lifecycle.html#agent-id),主题类型通常由应用代码定义,用于标记该主题所针对的消息类型。例如,一个 GitHub 智能体在发布关于新 issue 的消息时,可能会使用 `"GitHub_Issues"` 作为主题类型。

主题源(topic source)是某个主题类型内主题的唯一标识符。它通常由应用数据定义。例如,GitHub 智能体可能会使用 `"github.com/{repo_name}/issues/{issue_number}"` 作为主题源,以唯一标识该主题。主题源允许发布方限定消息的范围,并创建隔离区(silo)。

Topic ID 可以与字符串相互转换。该字符串的格式为:

Note

Topic_Type/Topic_Source

当类型(Type)采用 UTF8 编码且只包含字母数字字符 (a-z) 和 (0-9) 或下划线 (_) 时,被视为有效。有效的标识符不能以数字开头,也不能包含任何空格。当源(Source)采用 UTF8 编码且只包含介于(含)ASCII 32(空格)和 126(~)之间的字符时,被视为有效。

## 订阅#

订阅(Subscription)将主题映射到智能体 ID。

![Subscription](../../../_images/subscription.svg)

上图展示了主题与订阅之间的关系。agent runtime 会记录这些订阅,并依据它们向智能体投递消息。

如果某个主题没有任何订阅,则发布到该主题的消息将不会被投递到任何智能体。如果某个主题有多个订阅,则消息将沿着所有订阅进行投递,每个接收方的智能体只会收到一次。应用程序可以通过 agent runtime 的 API 添加或删除订阅。

## 基于类型的订阅#

基于类型的订阅(Type-based subscription)将主题类型映射到智能体类型(参见 [agent ID](agent-identity-and-lifecycle.html#agent-id))。它在不了解具体的主题源与智能体键的情况下,声明了从主题到智能体 ID 的无界映射。该机制很简单:任何与基于类型的订阅的主题类型相匹配的主题,都将被映射到一个智能体 ID,该 ID 使用订阅中的智能体类型,并将智能体键分配为主题源的值。在 Python API 中,可以使用 `TypeSubscription`。

Note

Type-Based Subscription = Topic Type –> Agent Type

一般来说,基于类型的订阅是声明订阅的首选方式。它具有可移植性,并且不依赖于数据:开发者无需编写依赖于特定智能体 ID 的应用代码。

### 基于类型订阅的应用场景#

当具体的主题或智能体 ID 依赖于数据时,可以应用基于类型的订阅。这些场景可以根据两个维度进行划分:(1)单租户(single-tenant)还是多租户(multi-tenant);(2)每个租户是单个主题还是多个主题。一个租户(tenant)通常指处理特定用户会话或特定请求的一组智能体。

#### 单租户、单个主题#

在这种场景下,整个应用只有一个租户和一个主题。这是最简单的场景,可用于许多情况,例如命令行工具或单用户应用。

要为此场景应用基于类型的订阅,请为每种智能体类型创建一个基于类型的订阅,并对所有基于类型的订阅使用相同的主题类型。在发布时,始终使用相同的主题,即相同的主题类型和主题源。

例如,假设存在三种智能体类型:`"triage_agent"`、`"coder_agent"` 和 `"reviewer_agent"`,且主题类型为 `"default"`,那么应创建以下基于类型的订阅:
    
    
    # Type-based Subscriptions for single-tenant, single topic scenario
    TypeSubscription(topic_type="default", agent_type="triage_agent")
    TypeSubscription(topic_type="default", agent_type="coder_agent")
    TypeSubscription(topic_type="default", agent_type="reviewer_agent")
    

通过以上基于类型的订阅,在发布消息时,对所有消息都使用相同的主题源 `"default"`。因此,主题始终为 `("default", "default")`。发布到该主题的消息将被投递给上述所有类型的所有智能体。具体来说,该消息将被发送给以下智能体 ID:
    
    
    # The agent IDs created based on the topic source
    AgentID("triage_agent", "default")
    AgentID("coder_agent", "default")
    AgentID("reviewer_agent", "default")
    

下图展示了本例中基于类型的订阅的工作方式。

![Type-Based Subscription Single-Tenant, Single Topic Scenario Example](../../../_images/type-subscription-single-tenant-single-topic.svg)

如果具有该 ID 的智能体不存在,运行时将创建它。

#### 单租户、多个主题#

在这种场景下,只有一个租户,但你希望控制哪个智能体处理哪个主题。当你希望创建隔离区(silo),并让不同的智能体专门处理不同的主题时,这非常有用。

要为此场景应用基于类型的订阅,请为每种智能体类型创建一个基于类型的订阅,但使用不同的主题类型。如果希望这些智能体类型共享同一个主题,可以将相同的主题类型映射到多个智能体类型。对于主题源,在发布消息时,仍然对所有消息使用相同的值。

延续上述使用相同智能体类型的例子,创建以下基于类型的订阅:
    
    
    # Type-based Subscriptions for single-tenant, multiple topics scenario
    TypeSubscription(topic_type="triage", agent_type="triage_agent")
    TypeSubscription(topic_type="coding", agent_type="coder_agent")
    TypeSubscription(topic_type="coding", agent_type="reviewer_agent")
    

通过以上基于类型的订阅,任何发布到主题 `("triage", "default")` 的消息都将被投递给智能体类型为 `"triage_agent"` 的智能体;任何发布到主题 `("coding", "default")` 的消息都将被投递给智能体类型为 `"coder_agent"` 和 `"reviewer_agent"` 的智能体。

下图展示了本例中基于类型的订阅的工作方式。

![Type-Based Subscription Single-Tenant, Multiple Topics Scenario Example](../../../_images/type-subscription-single-tenant-multiple-topics.svg)

#### 多租户场景#

在单租户场景中,主题源始终相同(例如 `"default"`),它在应用代码中是被硬编码的。当过渡到多租户场景时,主题源变为数据相关(data-dependent)的。

Note

判断你是否处于多租户场景的一个很好的标志是:你需要同一智能体类型的多个实例。例如,你可能希望使用不同的智能体实例来处理不同的用户会话,以隔离私有数据;或者,你可能希望将繁重的工作负载分布到同一智能体类型的多个实例上,让它们并发地协作完成工作。

延续上述例子,如果你希望使用专用的智能体实例来处理某个特定的 GitHub issue,则需要将主题源设置为该 issue 的唯一标识符。

例如,假设存在针对智能体类型 `"triage_agent"` 的一个基于类型的订阅:
    
    
    TypeSubscription(topic_type="github_issues", agent_type="triage_agent")
    

当消息被发布到主题 `("github_issues", "github.com/microsoft/autogen/issues/1")` 时,运行时将把消息投递给 ID 为 `("triage_agent", "github.com/microsoft/autogen/issues/1")` 的智能体。当消息被发布到主题 `("github_issues", "github.com/microsoft/autogen/issues/9")` 时,运行时将把消息投递给 ID 为 `("triage_agent", "github.com/microsoft/autogen/issues/9")` 的智能体。

下图展示了本例中基于类型的订阅的工作方式。

![Type-Based Subscription Multi-Tenant Scenario Example](../../../_images/type-subscription-multi-tenant.svg)

请注意,智能体 ID 是数据相关的,如果对应的智能体实例不存在,运行时会创建一个新实例。

要支持每个租户的多个主题,你可以使用不同的主题类型,这与"单租户、多个主题"场景中的做法类似。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/core-concepts/topic-and-subscription.md)

[ __Show Source](../../../_sources/user-guide/core-user-guide/core-concepts/topic-and-subscription.md.txt)