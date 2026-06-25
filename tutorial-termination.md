[跳到主要内容](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html#main-content)

回到顶部`Ctrl` + `K`

浅色深色系统设置

- [GitHub](https://github.com/microsoft/autogen)
- [Discord](https://aka.ms/autogen-discord)
- [Twitter](https://twitter.com/pyautogen)

# 终止条件 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html\#termination "链接到此标题")

在上一节中，我们探索了如何定义代理并将它们组织成可以解决任务的团队。然而，运行可能会无限期地持续下去，在许多情况下，我们需要知道_何时_停止它们。这就是终止条件的作用。

AgentChat 通过提供基础 [`TerminationCondition`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TerminationCondition "autogen_agentchat.base.TerminationCondition") 类和多个继承自它的实现来支持多种终止条件。

终止条件是一个可调用对象，它接收自上次调用条件以来的一系列 [`BaseAgentEvent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseAgentEvent "autogen_agentchat.messages.BaseAgentEvent") 或 [`BaseChatMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.BaseChatMessage "autogen_agentchat.messages.BaseChatMessage") 对象，如果应该终止对话则返回 [`StopMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.StopMessage "autogen_agentchat.messages.StopMessage")，否则返回 `None`。
一旦达到终止条件，必须通过调用 [`reset()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TerminationCondition.reset "autogen_agentchat.base.TerminationCondition.reset") 重置后才能再次使用。

关于终止条件的一些重要事项：

- 它们是有状态的，但在每次运行（[`run()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskRunner.run "autogen_agentchat.base.TaskRunner.run") 或 [`run_stream()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskRunner.run_stream "autogen_agentchat.base.TaskRunner.run_stream")）完成后会自动重置。

- 它们可以使用 AND 和 OR 运算符进行组合。


注意

对于群组聊天团队（即 [`RoundRobinGroupChat`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat")、
[`SelectorGroupChat`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 和 [`Swarm`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm")），
终止条件在每个代理响应后调用。
虽然响应可能包含多个内部消息，但团队会针对单个响应中的所有消息仅调用一次终止条件。
因此，条件会使用自上次调用以来的"增量序列"消息进行调用。

内置终止条件：

01. [`MaxMessageTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.MaxMessageTermination "autogen_agentchat.conditions.MaxMessageTermination")：在生成指定数量的消息后停止，包括代理和任务消息。

02. [`TextMentionTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TextMentionTermination "autogen_agentchat.conditions.TextMentionTermination")：当消息中提到特定文本或字符串时停止（例如，"TERMINATE"）。

03. [`TokenUsageTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TokenUsageTermination "autogen_agentchat.conditions.TokenUsageTermination")：当使用了指定数量的提示或完成令牌时停止。这需要代理在其消息中报告令牌使用情况。

04. [`TimeoutTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TimeoutTermination "autogen_agentchat.conditions.TimeoutTermination")：在指定的持续时间（秒）后停止。

05. [`HandoffTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.HandoffTermination "autogen_agentchat.conditions.HandoffTermination")：当请求移交到特定目标时停止。移交消息可用于构建诸如 [`Swarm`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm") 等模式。当你希望暂停运行并允许应用程序或用户在代理移交时提供输入时，这非常有用。

06. [`SourceMatchTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.SourceMatchTermination "autogen_agentchat.conditions.SourceMatchTermination")：在特定代理响应后停止。

07. [`ExternalTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.ExternalTermination "autogen_agentchat.conditions.ExternalTermination")：启用从运行外部以编程方式控制终止。这对于 UI 集成（例如，聊天界面中的"停止"按钮）非常有用。

08. [`StopMessageTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.StopMessageTermination "autogen_agentchat.conditions.StopMessageTermination")：在代理生成 [`StopMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.StopMessage "autogen_agentchat.messages.StopMessage") 时停止。

09. [`TextMessageTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TextMessageTermination "autogen_agentchat.conditions.TextMessageTermination")：在代理生成 [`TextMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.TextMessage "autogen_agentchat.messages.TextMessage") 时停止。

10. [`FunctionCallTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.FunctionCallTermination "autogen_agentchat.conditions.FunctionCallTermination")：在代理生成包含具有匹配名称的 [`FunctionExecutionResult`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.models.html#autogen_core.models.FunctionExecutionResult "autogen_core.models.FunctionExecutionResult") 的 [`ToolCallExecutionEvent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallExecutionEvent "autogen_agentchat.messages.ToolCallExecutionEvent") 时停止。

11. [`FunctionalTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.FunctionalTermination "autogen_agentchat.conditions.FunctionalTermination")：当函数表达式在最后一条增量序列消息上评估为 `True` 时停止。这对于快速创建内置条件未涵盖的自定义终止条件非常有用。


## 基本用法 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html\#basic-usage "链接到此标题")

为了演示终止条件的特性，我们将创建一个由两个代理组成的团队：一个负责文本生成的主要代理和一个审查并提供生成文本反馈的评论代理。

```
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    temperature=1,
    # api_key="sk-...", # 如果设置了 OPENAI_API_KEY 环境变量则可选。
)

# 创建主要代理。
primary_agent = AssistantAgent(
    "primary",
    model_client=model_client,
    system_message="You are a helpful AI assistant.",
)

# 创建评论代理。
critic_agent = AssistantAgent(
    "critic",
    model_client=model_client,
    system_message="Provide constructive feedback for every message. Respond with 'APPROVE' to when your feedbacks are addressed.",
)
```

复制到剪贴板

让我们探讨终止条件如何在每次 `run` 或 `run_stream` 调用后自动重置，使团队能够从中断处继续对话。

```
max_msg_termination = MaxMessageTermination(max_messages=3)
round_robin_team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=max_msg_termination)

# 如果作为独立脚本运行此脚本，请使用 asyncio.run(...)。
await Console(round_robin_team.run_stream(task="Write a unique, Haiku about the weather in Paris"))
```

复制到剪贴板

```
---------- user ----------
Write a unique, Haiku about the weather in Paris
---------- primary ----------
Gentle rain whispers,
Cobblestones glisten softly—
Paris dreams in gray.
[Prompt tokens: 30, Completion tokens: 19]
---------- critic ----------
The Haiku captures the essence of a rainy day in Paris beautifully, and the imagery is vivid. However, it's important to ensure the use of the traditional 5-7-5 syllable structure for Haikus. Your current Haiku lines are composed of 4-7-5 syllables, which slightly deviates from the form. Consider revising the first line to fit the structure.

For example:
Soft rain whispers down,
Cobblestones glisten softly —
Paris dreams in gray.

This revision maintains the essence of your original lines while adhering to the traditional Haiku structure.
[Prompt tokens: 70, Completion tokens: 120]
---------- Summary ----------
Number of messages: 3
Finish reason: Maximum number of messages 3 reached, current message count: 3
Total prompt tokens: 100
Total completion tokens: 139
Duration: 3.34 seconds
```

复制到剪贴板

```
TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Write a unique, Haiku about the weather in Paris'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=30, completion_tokens=19), content='Gentle rain whispers,  \nCobblestones glisten softly—  \nParis dreams in gray.'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=70, completion_tokens=120), content="The Haiku captures the essence of a rainy day in Paris beautifully, and the imagery is vivid. However, it's important to ensure the use of the traditional 5-7-5 syllable structure for Haikus. Your current Haiku lines are composed of 4-7-5 syllables, which slightly deviates from the form. Consider revising the first line to fit the structure.\n\nFor example:\nSoft rain whispers down,  \nCobblestones glisten softly —  \nParis dreams in gray.\n\nThis revision maintains the essence of your original lines while adhering to the traditional Haiku structure.")], stop_reason='Maximum number of messages 3 reached, current message count: 3')
```

复制到剪贴板

对话在达到最大消息限制后停止。由于主要代理未能回应反馈，让我们继续对话。

```
# 如果作为独立脚本运行此脚本，请使用 asyncio.run(...)。
await Console(round_robin_team.run_stream())
```

复制到剪贴板

```
---------- primary ----------
Thank you for your feedback. Here is the revised Haiku:

Soft rain whispers down,
Cobblestones glisten softly —
Paris dreams in gray.
[Prompt tokens: 181, Completion tokens: 32]
---------- critic ----------
The revised Haiku now follows the traditional 5-7-5 syllable pattern, and it still beautifully captures the atmospheric mood of Paris in the rain. The imagery and flow are both clear and evocative. Well done on making the adjustment!

APPROVE
[Prompt tokens: 234, Completion tokens: 54]
---------- primary ----------
Thank you for your kind words and approval. I'm glad the revision meets your expectations and captures the essence of Paris. If you have any more requests or need further assistance, feel free to ask!
[Prompt tokens: 279, Completion tokens: 39]
---------- Summary ----------
Number of messages: 3
Finish reason: Maximum number of messages 3 reached, current message count: 3
Total prompt tokens: 694
Total completion tokens: 125
Duration: 6.43 seconds
```

复制到剪贴板

```
TaskResult(messages=[TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=181, completion_tokens=32), content='Thank you for your feedback. Here is the revised Haiku:\n\nSoft rain whispers down,  \nCobblestones glisten softly —  \nParis dreams in gray.'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=234, completion_tokens=54), content='The revised Haiku now follows the traditional 5-7-5 syllable pattern, and it still beautifully captures the atmospheric mood of Paris in the rain. The imagery and flow are both clear and evocative. Well done on making the adjustment! \n\nAPPROVE'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=279, completion_tokens=39), content="Thank you for your kind words and approval. I'm glad the revision meets your expectations and captures the essence of Paris. If you have any more requests or need further assistance, feel free to ask!")], stop_reason='Maximum number of messages 3 reached, current message count: 3')
```

复制到剪贴板

团队从中断处继续，使主要代理能够回应反馈。

## 组合终止条件 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html\#combining-termination-conditions "链接到此标题")

让我们展示如何使用 AND (`&`) 和 OR (`|`) 运算符组合终止条件来创建更复杂的终止逻辑。例如，我们将创建一个团队，在生成 10 条消息或评论代理批准消息时停止。

```
max_msg_termination = MaxMessageTermination(max_messages=10)
text_termination = TextMentionTermination("APPROVE")
combined_termination = max_msg_termination | text_termination

round_robin_team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=combined_termination)

# 如果作为独立脚本运行此脚本，请使用 asyncio.run(...)。
await Console(round_robin_team.run_stream(task="Write a unique, Haiku about the weather in Paris"))
```

复制到剪贴板

```
---------- user ----------
Write a unique, Haiku about the weather in Paris
---------- primary ----------
Spring breeze gently hums,
Cherry blossoms in full bloom—
Paris wakes to life.
[Prompt tokens: 467, Completion tokens: 19]
---------- critic ----------
The Haiku beautifully captures the awakening of Paris in the spring. The imagery of a gentle spring breeze and cherry blossoms in full bloom effectively conveys the rejuvenating feel of the season. The final line, "Paris wakes to life," encapsulates the renewed energy and vibrancy of the city. The Haiku adheres to the 5-7-5 syllable structure and portrays a vivid seasonal transformation in a concise and poetic manner. Excellent work!

APPROVE
[Prompt tokens: 746, Completion tokens: 93]
---------- Summary ----------
Number of messages: 3
Finish reason: Text 'APPROVE' mentioned
Total prompt tokens: 1213
Total completion tokens: 112
Duration: 2.75 seconds
```

复制到剪贴板

```
TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Write a unique, Haiku about the weather in Paris'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=467, completion_tokens=19), content='Spring breeze gently hums,  \nCherry blossoms in full bloom—  \nParis wakes to life.'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=746, completion_tokens=93), content='The Haiku beautifully captures the awakening of Paris in the spring. The imagery of a gentle spring breeze and cherry blossoms in full bloom effectively conveys the rejuvenating feel of the season. The final line, "Paris wakes to life," encapsulates the renewed energy and vibrancy of the city. The Haiku adheres to the 5-7-5 syllable structure and portrays a vivid seasonal transformation in a concise and poetic manner. Excellent work!\n\nAPPROVE')], stop_reason="Text 'APPROVE' mentioned")
```

复制到剪贴板

对话在评论代理批准消息后停止，尽管它也可能在生成 10 条消息后停止。

或者，如果我们希望仅在满足两个条件时才停止运行，我们可以使用 AND (`&`) 运算符。

```
combined_termination = max_msg_termination & text_termination
```

复制到剪贴板

## 自定义终止条件 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html\#custom-termination-condition "链接到此标题")

内置终止条件足以满足大多数用例。
但是，可能存在需要实现不符合现有条件的自定义终止条件的情况。
你可以通过子类化 [`TerminationCondition`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TerminationCondition "autogen_agentchat.base.TerminationCondition") 类来实现。

在此示例中，我们创建了一个自定义终止条件，在进行特定函数调用时停止对话。

```
from typing import Sequence

from autogen_agentchat.base import TerminatedException, TerminationCondition
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage, StopMessage, ToolCallExecutionEvent
from autogen_core import Component
from pydantic import BaseModel
from typing_extensions import Self

class FunctionCallTerminationConfig(BaseModel):
    """终止条件的配置，以允许组件的序列化和反序列化。"""

    function_name: str

class FunctionCallTermination(TerminationCondition, Component[FunctionCallTerminationConfig]):
    """如果在收到具有特定名称的 FunctionExecutionResult 时终止对话。"""

    component_config_schema = FunctionCallTerminationConfig
    component_provider_override = "autogen_agentchat.conditions.FunctionCallTermination"
    """组件配置的架构。"""

    def __init__(self, function_name: str) -> None:
        self._terminated = False
        self._function_name = function_name

    @property
    def terminated(self) -> bool:
        return self._terminated

    async def __call__(self, messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> StopMessage | None:
        if self._terminated:
            raise TerminatedException("Termination condition has already been reached")
        for message in messages:
            if isinstance(message, ToolCallExecutionEvent):
                for execution in message.content:
                    if execution.name == self._function_name:
                        self._terminated = True
                        return StopMessage(
                            content=f"Function '{self._function_name}' was executed.",
                            source="FunctionCallTermination",
                        )
        return None

    async def reset(self) -> None:
        self._terminated = False

    def _to_config(self) -> FunctionCallTerminationConfig:
        return FunctionCallTerminationConfig(
            function_name=self._function_name,
        )

    @classmethod
    def _from_config(cls, config: FunctionCallTerminationConfig) -> Self:
        return cls(
            function_name=config.function_name,
        )
```

复制到剪贴板

让我们使用这个新的终止条件，在评论代理使用 `approve` 函数调用批准消息时停止对话。

首先，我们创建一个简单的函数，当评论代理批准消息时将调用该函数。

```
def approve() -> None:
    """在处理完所有反馈后批准消息。"""
    pass
```

复制到剪贴板

然后我们创建代理。评论代理配备了 `approve` 工具。

```
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    temperature=1,
    # api_key="sk-...", # 如果设置了 OPENAI_API_KEY 环境变量则可选。
)

# 创建主要代理。
primary_agent = AssistantAgent(
    "primary",
    model_client=model_client,
    system_message="You are a helpful AI assistant.",
)

# 创建配备 approve 函数作为工具的评论代理。
critic_agent = AssistantAgent(
    "critic",
    model_client=model_client,
    tools=[approve],  # 将 approve 函数注册为工具。
    system_message="Provide constructive feedback. Use the approve tool to approve when all feedbacks are addressed.",
)
```

复制到剪贴板

现在，我们创建终止条件和团队。
我们使用写诗任务运行团队。

```
function_call_termination = FunctionCallTermination(function_name="approve")
round_robin_team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=function_call_termination)

# 如果作为独立脚本运行此脚本，请使用 asyncio.run(...)。
await Console(round_robin_team.run_stream(task="Write a unique, Haiku about the weather in Paris"))
await model_client.close()
```

复制到剪贴板

```
---------- user ----------
Write a unique, Haiku about the weather in Paris
---------- primary ----------
Raindrops gently fall,
Cobblestones shine in dim light—
Paris dreams in grey.
---------- critic ----------
This Haiku beautifully captures a melancholic yet romantic image of Paris in the rain. The use of sensory imagery like "Raindrops gently fall" and "Cobblestones shine" effectively paints a vivid picture. It could be interesting to experiment with more distinct seasonal elements of Paris, such as incorporating the Seine River or iconic landmarks in the context of the weather. Overall, it successfully conveys the atmosphere of Paris in subtle, poetic imagery.
---------- primary ----------
Thank you for your feedback! I'm glad you enjoyed the imagery. Here's another Haiku that incorporates iconic Parisian elements:

Eiffel stands in mist,
Seine's ripple mirrors the sky—
Spring whispers anew.
---------- critic ----------
[FunctionCall(id='call_QEWJZ873EG4UIEpsQHi1HsAu', arguments='{}', name='approve')]
---------- critic ----------
[FunctionExecutionResult(content='None', name='approve', call_id='call_QEWJZ873EG4UIEpsQHi1HsAu', is_error=False)]
---------- critic ----------
None
```

复制到剪贴板

```
TaskResult(messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Write a unique, Haiku about the weather in Paris', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=30, completion_tokens=23), metadata={}, content='Raindrops gently fall,  \nCobblestones shine in dim light—  \nParis dreams in grey.  ', type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=99, completion_tokens=90), metadata={}, content='This Haiku beautifully captures a melancholic yet romantic image of Paris in the rain. The use of sensory imagery like "Raindrops gently fall" and "Cobblestones shine" effectively paints a vivid picture. It could be interesting to experiment with more distinct seasonal elements of Paris, such as incorporating the Seine River or iconic landmarks in the context of the weather. Overall, it successfully conveys the atmosphere of Paris in subtle, poetic imagery.', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=152, completion_tokens=48), metadata={}, content="Thank you for your feedback! I'm glad you enjoyed the imagery. Here's another Haiku that incorporates iconic Parisian elements:\n\nEiffel stands in mist,  \nSeine's ripple mirrors the sky—  \nSpring whispers anew.  ", type='TextMessage'), ToolCallRequestEvent(source='critic', models_usage=RequestUsage(prompt_tokens=246, completion_tokens=11), metadata={}, content=[FunctionCall(id='call_QEWJZ873EG4UIEpsQHi1HsAu', arguments='{}', name='approve')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='critic', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='None', name='approve', call_id='call_QEWJZ873EG4UIEpsQHi1HsAu', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='critic', models_usage=None, metadata={}, content='None', type='ToolCallSummaryMessage')], stop_reason="Function 'approve' was executed.")
```

复制到剪贴板

你可以看到，当评论代理使用 `approve` 函数调用批准消息时，对话停止。

在此页面上


[在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/tutorial/termination.ipynb)

[显示源代码](https://microsoft.github.io/autogen/stable/_sources/user-guide/agentchat-user-guide/tutorial/termination.ipynb.txt)
