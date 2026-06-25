[跳过主要内容](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html#main-content)

返回顶部`Ctrl` + `K`

浅色深色系统设置

- [GitHub](https://github.com/microsoft/autogen)
- [Discord](https://aka.ms/autogen-discord)
- [Twitter](https://twitter.com/pyautogen)

# 团队 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html\#teams "链接到此标题")

在本节中，您将学习如何使用 AutoGen 创建_多代理团队_（或简称团队）。团队是一组为实现共同目标而协作的代理。

我们将首先向您展示如何创建和运行团队。然后，我们将解释如何观察团队的行为，这对于调试和理解团队性能至关重要，以及控制团队行为的常见操作。

AgentChat 支持多种团队预设：

- [`RoundRobinGroupChat`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat")：一个以轮询方式让参与者轮流发言的群聊团队（在本页介绍）。[教程](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html#creating-a-team)

- [`SelectorGroupChat`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat")：一个在每条消息后使用 ChatCompletion 模型选择下一个发言者的团队。[教程](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/selector-group-chat.html)

- [`MagenticOneGroupChat`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.MagenticOneGroupChat "autogen_agentchat.teams.MagenticOneGroupChat")：一个通用的多代理系统，用于解决跨多个领域的开放式网络和基于文件的任务。[教程](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html)

- [`Swarm`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm")：一个使用 [`HandoffMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage") 来信号代理之间转换的团队。[教程](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html)


注意

**何时应该使用团队？**

团队适用于需要协作和多样化专业知识的复杂任务。
然而，与单代理相比，它们也需要更多的引导来控制。
虽然 AutoGen 简化了团队协作的流程，但对于简单任务，请从
单代理开始，并在单代理不足以完成任务时过渡到多代理团队。
在转向团队方法之前，请确保您已使用适当的工具和指令优化了单代理。

## 创建团队 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html\#creating-a-team "链接到此标题")

[`RoundRobinGroupChat`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 是一种简单有效的团队配置，其中所有代理共享相同的上下文，并以轮询方式轮流响应。每个代理在其轮次期间将其响应广播给所有其他代理，确保整个团队保持一致的上下文。

我们将首先创建一个包含两个 [`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 和一个 [`TextMentionTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TextMentionTermination "autogen_agentchat.conditions.TextMentionTermination") 条件的团队，该条件在检测到代理响应中的特定单词时停止团队。

这个双代理团队实现了_反射_模式，这是一种多代理设计模式，其中一个评论代理评估主要代理的响应。使用 [Core API](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/reflection.html) 了解更多关于反射模式的信息。

```python
import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 创建 OpenAI 模型客户端。
model_client = OpenAIChatCompletionClient(
    model="gpt-4o-2024-08-06",
    # api_key="sk-...", # 如果设置了 OPENAI_API_KEY 环境变量则为可选。
)

# 创建主要代理。
primary_agent = AssistantAgent(
    "primary",
    model_client=model_client,
    system_message="你是一个乐于助人的 AI 助手。",
)

# 创建评论代理。
critic_agent = AssistantAgent(
    "critic",
    model_client=model_client,
    system_message="提供建设性反馈。当你的反馈被采纳时，回复 'APPROVE'。",
)

# 定义一个终止条件，当评论者批准时停止任务。
text_termination = TextMentionTermination("APPROVE")

# 创建一个包含主要代理和评论代理的团队。
team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=text_termination)
```

复制到剪贴板

## 运行团队 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html\#running-a-team "链接到此标题")

让我们调用 [`run()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run "autogen_agentchat.teams.BaseGroupChat.run") 方法来启动团队并执行任务。

```python
# 在脚本中运行时使用 `asyncio.run(...)`。
result = await team.run(task="写一首关于秋天的短诗。")
print(result)
```

复制到剪贴板

```
TaskResult(messages=[TextMessage(source='user', models_usage=None, content='写一首关于秋天的短诗。', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=28, completion_tokens=109), content="琥珀色、金色和铁锈色的叶子，  \n在轻柔的风中翩翩起舞。  \n凉爽的空气低语着古老的故事，  \n白昼渐短，黑夜愈浓。  \n\n南瓜地和苹果美食，  \n街道上笑声不断。  \n温暖的毛衣和闪烁的炉火，  \n是大自然绚丽展演的时刻。  \n\n丰收之月升起在天际，  \n大雁排成队形开始飞翔。  \n秋天用明亮的色彩诉说，  \n短暂而优雅，纯粹的愉悦。  ", type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=154, completion_tokens=200), content='你的诗歌很好地捕捉了秋天的精髓，通过生动的意象和流畅的节奏。使用"琥珀色、金色和铁锈色"等描述性语言有效地描绘了树叶变化的视觉画面。"凉爽的空气低语着古老的故事"和"白昼渐短，黑夜愈浓"等短语通过融入季节特征增添了诗意。\n\n然而，你可以考虑探索其他感官细节以加深读者的沉浸感。例如，提到脚下踩碎树叶的声音或空气中肉桂和香料的香味可以增强感官体验。\n\n此外，虽然"南瓜地和苹果美食"令人联想到秋天，但扩展这些元素或包含更多与季节相关的个人经历或情感可能会使诗歌更具亲和力和吸引力。\n\n总的来说，你创作了一首优美的诗歌，优雅而温暖地庆祝了秋天的美丽和传统。进行一些调整以包含多感官细节可以进一步提升它。', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=347, completion_tokens=178), content="感谢你深思熟虑的反馈。以下是加入额外感官细节的修订版本：\n\n琥珀色、金色和铁锈色的叶子，  \n在轻柔的风中翩翩起舞。  \n凉爽的空气低语着古老的故事，  \n白昼渐短，黑夜愈浓。  \n\n脚下传来踩碎树叶的声响，  \n秋日节奏的旋律。  \n肉桂和香料的气息交融，  \n每阵微风都送来怀旧之情。  \n\n南瓜地和苹果美食，  \n街道上笑声不断。  \n温暖的毛衣和闪烁的炉火，  \n是大自然绚丽展演的时刻。  \n\n丰收之月升起在天际，  \n大雁排成队形开始飞翔。  \n秋天用明亮的色彩诉说，  \n短暂而优雅，纯粹的愉悦。  \n\n我希望这个版本能与秋天的精神产生更多共鸣。再次感谢你的建议！", type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=542, completion_tokens=3), content='APPROVE', type='TextMessage')], stop_reason="提到文本 'APPROVE'")
```

复制到剪贴板

团队运行代理直到满足终止条件。
在此情况下，团队按照轮询顺序运行代理，直到
在代理响应中检测到"APPROVE"一词时满足
终止条件。
当团队停止时，它返回一个 [`TaskResult`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult") 对象，其中包含团队中代理生成的所有消息。

## 观察团队 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html\#observing-a-team "链接到此标题")

类似于代理的 [`on_messages_stream()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.on_messages_stream "autogen_agentchat.agents.BaseChatAgent.on_messages_stream") 方法，你可以通过调用 [`run_stream()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run_stream "autogen_agentchat.teams.BaseGroupChat.run_stream") 方法在团队运行时流式传输其消息。此方法返回一个生成器，按生成顺序产出团队中代理产生的消息，最后一项是 [`TaskResult`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult") 对象。

```python
# 在脚本中运行时，使用异步主函数并从 `asyncio.run(...)` 调用它。
await team.reset()  # 重置团队以执行新任务。
async for message in team.run_stream(task="写一首关于秋天的短诗。"):  # type: ignore
    if isinstance(message, TaskResult):
        print("停止原因:", message.stop_reason)
    else:
        print(message)
```

复制到剪贴板

```
source='user' models_usage=None content='写一首关于秋天的短诗。' type='TextMessage'
source='primary' models_usage=RequestUsage(prompt_tokens=28, completion_tokens=105) content="叶子以金色的舞蹈飘落，  \n落下时低语着秘密，  \n凉爽的空气带来温柔的迷醉，  \n宣告着秋天的召唤。  \n\n南瓜散发着橙色的光芒，  \n田野披上琥珀色的外衣，  \n白昼退向更长的夜晚，  \n天空转向更深的蓝色。  \n\n风带着泥土和松树的气息，  \n毛衣将我们温暖包裹，  \n大自然的画布，大胆的设计，  \n在秋天的怀抱中，我们找到喜悦。  " type='TextMessage'
source='critic' models_usage=RequestUsage(prompt_tokens=150, completion_tokens=226) content='你的诗歌通过生动的意象和舒缓的节奏很好地捕捉了秋天的本质。叶子飘落、南瓜发光和田野披上琥珀色外衣的意象有效地描绘了秋季的景象。"白昼退向更长的夜晚"和"毛衣将我们温暖包裹"等对比元素的运用在寒冷与温暖之间提供了良好的平衡。此外，通过"秋天的召唤"和"大自然的画布，大胆的设计"等短语对秋天进行拟人化增加了描绘的深度。\n\n为了进一步增强诗歌效果，你可以考虑关注秋天的声音景观，如树叶的沙沙声或迁徙鸟类的遥远叫声，以调动读者的听觉感官。另外，稍微变化行长度可以增加阅读体验的动态流动。\n\n总的来说，你的诗歌引人入胜，有效地 encapsulate 了秋天的美丽和变迁。通过一些调整来探索其他感官细节，它可以变得更加沉浸式。\n\n如果你采纳其中一些建议或找到其他方式来扩展感官体验，请分享你的更新！' type='TextMessage'
source='primary' models_usage=RequestUsage(prompt_tokens=369, completion_tokens=143) content="感谢你深思熟虑的批评和建议。以下是加入对听觉感官关注和变化行长度的修订版本：\n\n叶子以金色的舞蹈飘落，  \n落下时低语着秘密，  \n微风哼唱着温柔的迷醉，  \n宣告着秋天的召唤。  \n\n南瓜散发着橙色的光芒，  \n广阔天空下的琥珀色田野，  \n白昼退向更长的夜晚，  \n寒风和遥远的哭声。  \n\n树叶的沙沙低语，  \n毛衣将我们 snug 包裹，  \n大自然的画布，大胆而自由，  \n在秋天的怀抱中，纯粹的喜悦。  \n\n感谢你的反馈，希望这个版本更好地捕捉了季节的感官丰富性！" type='TextMessage'
source='critic' models_usage=RequestUsage(prompt_tokens=529, completion_tokens=160) content='你修订后的诗歌是对原作的精美提升。通过融入"微风哼唱"和"树叶的沙沙低语"等听觉元素，你添加了引人入胜的声音景观，将读者更深入地吸引到秋天的体验中。变化的行长度很好地创造了更加动态的节奏，为每一节增加了兴趣和变化。\n\n简洁而生动的"寒风和遥远的哭声"精彩地唤起了季节的氛围，增添了一丝神秘和深度。最后一节以"大自然的画布，大胆而自由"这样的诗句很好地总结了诗歌，庆祝秋天完整的感官拥抱。\n\n你成功地将更多的感官丰富性注入诗歌，增强了其整体情感和氛围影响。修订工作做得出色！\n\nAPPROVE' type='TextMessage'
停止原因: 提到文本 'APPROVE'
```

复制到剪贴板

如上例所示，你可以通过检查 [`stop_reason`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult.stop_reason "autogen_agentchat.base.TaskResult.stop_reason") 属性来确定团队停止的原因。

[`Console()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.ui.html#autogen_agentchat.ui.Console "autogen_agentchat.ui.Console") 方法提供了一种便捷的方式，以适当的格式将消息打印到控制台。

```python
await team.reset()  # 重置团队以执行新任务。
await Console(team.run_stream(task="写一首关于秋天的短诗。"))  # 将消息流式传输到控制台。
```

复制到剪贴板

```
---------- user ----------
写一首关于秋天的短诗。
---------- primary ----------
凉爽空气中金色叶子翩翩起舞，
低语着故事四处漫步。
琥珀色调绘满地面，
大自然的交响乐环绕四周。

毛衣以温柔的优雅相拥，
南瓜微笑，温暖的怀抱。
寒风在高大的树木间哼唱，
微风中绚丽的织锦。

暮色光晕中的丰收之月，
在下方田野施下魔法。
秋天的拥抱，温柔的呼唤，
在冬雪降临前珍惜美景。
[提示令牌数: 28, 完成令牌数: 99]
---------- critic ----------
你的诗歌很好地捕捉了秋天的本质，营造出生动而舒适的氛围。金色叶子和琥珀色调的意象描绘了一幅如画的场景，许多人可以轻松产生共鸣。我特别欣赏你对南瓜的拟人化和毛衣的温柔拥抱，这为你的诗句增添了温暖。

为了进一步增强诗歌效果，你可以考虑添加更多感官细节，让读者感觉更加沉浸在体验中。例如，包含特定的声音、气味或纹理可以加深与秋天氛围的联系。此外，你可以探索季节为冬天做准备时的情感过渡，为作品提供反思元素。

总的来说，这是一首可爱而动人的秋天描写，唤起了舒适感和对自然变迁之美的欣赏。做得好！
[提示令牌数: 144, 完成令牌数: 157]
---------- primary ----------
感谢你深思熟虑的反馈！很高兴你喜欢诗歌中的意象和温暖。为了增强感官体验和情感深度，这里是结合你建议的修订版本：

---

凉爽空气中金色叶子翩翩起舞，
低语着故事四处漫步。
琥珀色调绘满酥脆的地面，
大自然的交响乐环绕四周。

毛衣以温柔的优雅相拥，
南瓜咧嘴笑，温暖的怀抱。
寒风在高大的树木间哼唱，
噼啪作响的火焰温暖微风。

果园光晕中的苹果，
溢出的甜苹果酒香气。
脚下小径的咔嚓声，
肉桂香料和烤热的温度。

暮色光晕中的丰收之月，
在下方田野施下魔法。
秋天的拥抱，温柔的呼唤，
反思生命必然的解冻。

---

我希望这个版本能增强季节的感官和情感元素。再次感谢你的见解！
[提示令牌数: 294, 完成令牌数: 195]
---------- critic ----------
APPROVE
[提示令牌数: 506, 完成令牌数: 4]
---------- 摘要 ----------
消息数量: 5
完成原因: 提到文本 'APPROVE'
总提示令牌数: 972
总完成令牌数: 455
持续时间: 11.78 秒
```

复制到剪贴板

```
TaskResult(messages=[TextMessage(source='user', models_usage=None, content='写一首关于秋天的短诗。', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=28, completion_tokens=99), content="凉爽空气中金色叶子翩翩起舞，  \n低语着故事四处漫步。  \n琥珀色调绘满地面，  \n大自然的交响乐环绕四周。  \n\n毛衣以温柔的优雅相拥，  \n南瓜微笑，温暖的怀抱。  \n寒风在高大的树木间哼唱，  \n微风中绚丽的织锦。  \n\n暮色光晕中的丰收之月，  \n在下方田野施下魔法。  \n秋天的拥抱，温柔的呼唤，  \n在冬雪降临前珍惜美景。  ", type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=144, completion_tokens=157), content="你的诗歌很好地捕捉了秋天的本质，营造出生动而舒适的氛围。金色叶子和琥珀色调的意象描绘了一幅如画的场景，许多人可以轻松产生共鸣。我特别欣赏你对南瓜的拟人化和毛衣的温柔拥抱，这为你的诗句增添了温暖。\n\n为了进一步增强诗歌效果，你可以考虑添加更多感官细节，让读者感觉更加沉浸在体验中。例如，包含特定的声音、气味或纹理可以加深与秋天氛围的联系。此外，你可以探索季节为冬天做准备时的情感过渡，为作品提供反思元素。\n\n总的来说，这是一首可爱而动人的秋天描写，唤起了舒适感和对自然变迁之美的欣赏。做得好！", type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=294, completion_tokens=195), content="感谢你深思熟虑的反馈！很高兴你喜欢诗歌中的意象和温暖。为了增强感官体验和情感深度，这里是结合你建议的修订版本：\n\n---\n\n凉爽空气中金色叶子翩翩起舞，  \n低语着故事四处漫步。  \n琥珀色调绘满酥脆的地面，  \n大自然的交响乐环绕四周。  \n\n毛衣以温柔的优雅相拥，  \n南瓜咧嘴笑，温暖的怀抱。  \n寒风在高大的树木间哼唱，  \n噼啪作响的火焰温暖微风。  \n\n果园光晕中的苹果，  \n溢出的甜苹果酒香气。  \n脚下小径的咔嚓声，  \n肉桂香料和烤热的温度。  \n\n暮色光晕中的丰收之月，  \n在下方田野施下魔法。  \n秋天的拥抱，温柔的呼唤，  \n反思生命必然的解冻。  \n\n--- \n\n我希望这个版本能增强季节的感官和情感元素。再次感谢你的见解！", type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=506, completion_tokens=4), content='APPROVE', type='TextMessage')], stop_reason="提到文本 'APPROVE'")
```

复制到剪贴板

## 重置团队 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html\#resetting-a-team "链接到此标题")

你可以通过调用 [`reset()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.reset "autogen_agentchat.teams.BaseGroupChat.reset") 方法来重置团队。此方法将清除团队的状态，包括所有代理。
它将调用每个代理的 [`on_reset()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.base.html#autogen_agentchat.base.ChatAgent.on_reset "autogen_agentchat.base.ChatAgent.on_reset") 方法来清除代理的状态。

```python
await team.reset()  # 重置团队以备下次运行。
```

复制到剪贴板

如果下一个任务与上一个任务无关，通常最好重置团队。
但是，如果下一个任务与上一个任务相关，则无需重置，而是可以
恢复团队。

## 停止团队 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html\#stopping-a-team "链接到此标题")

除了诸如 [`TextMentionTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TextMentionTermination "autogen_agentchat.conditions.TextMentionTermination") 这样根据团队内部状态停止团队的自动终止条件外，你还可以使用 [`ExternalTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.ExternalTermination "autogen_agentchat.conditions.ExternalTermination") 从外部停止团队。

在 [`ExternalTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.ExternalTermination "autogen_agentchat.conditions.ExternalTermination") 上调用 [`set()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.ExternalTermination.set "autogen_agentchat.conditions.ExternalTermination.set") 将在当前代理轮次结束时停止团队。
因此，团队可能不会立即停止。
这允许当前代理在完成其轮次后将最终消息广播给团队，
然后再停止团队，保持团队状态一致。

```python
# 创建一个带有外部终止条件的新团队。
external_termination = ExternalTermination()
team = RoundRobinGroupChat(
    [primary_agent, critic_agent],
    termination_condition=external_termination | text_termination,  # 使用按位 OR 运算符组合条件。
)

# 在后台任务中运行团队。
run = asyncio.create_task(Console(team.run_stream(task="写一首关于秋天的短诗。")))

# 等待一段时间。
await asyncio.sleep(0.1)

# 停止团队。
external_termination.set()

# 等待团队完成。
await run
```

复制到剪贴板

```
---------- user ----------
写一首关于秋天的短诗。
---------- primary ----------
琥珀色、金色和红色的叶子，
从头顶的树上轻轻飘落。
凉爽空气中的风低语，
大自然的画布精心绘制。

丰收之月和寒冷的夜晚，
山丘上的丰收田野。
黄昏降临时紧紧裹紧毛衣，
秋天迷人的拥抱，如其显现般温暖。

南瓜在秋光中闪烁，
丰收盛宴和明亮的星星。
在每片叶子和呼唤的微风中，
我们找到辉煌秋天的魔力。
[提示令牌数: 28, 完成令牌数: 114]
---------- 摘要 ----------
消息数量: 2
完成原因: 请求外部终止
总提示令牌数: 28
总完成令牌数: 114
持续时间: 1.71 秒
```

复制到剪贴板

```
TaskResult(messages=[TextMessage(source='user', models_usage=None, content='写一首关于秋天的短诗。', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=28, completion_tokens=114), content="琥珀色、金色和红色的叶子，  \n从头顶的树上轻轻飘落。  \n凉爽空气中的风低语，  \n大自然的画布精心绘制。  \n\n丰收之月和寒冷的夜晚，  \n山丘上的丰收田野。  \n黄昏降临时紧紧裹紧毛衣，  \n秋天迷人的拥抱，如其显现般温暖。  \n\n南瓜在秋光中闪烁，  \n丰收盛宴和明亮的星星。  \n在每片叶子和呼唤的微风中，  \n我们找到辉煌秋天的魔力。  ", type='TextMessage')], stop_reason='请求外部终止')
```

复制到剪贴板

从上面的输出中，你可以看到团队因为满足外部终止条件而停止，
但发言代理能够在团队停止之前完成其轮次。

## 恢复团队 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html\#resuming-a-team "链接到此标题")

团队是有状态的，在每次运行后会保留对话历史和上下文，
除非你重置团队。

你可以通过再次调用 [`run()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run "autogen_agentchat.teams.BaseGroupChat.run") 或 [`run_stream()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run_stream "autogen_agentchat.teams.BaseGroupChat.run_stream") 方法而不提供新任务来恢复团队，从上次离开的位置继续。
[`RoundRobinGroupChat`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 将从轮询顺序中的下一个代理继续。

```python
await Console(team.run_stream())  # 恢复团队以继续上一个任务。
```

复制到剪贴板

```
---------- critic ----------
这首诗通过生动的意象和舒缓的节奏很好地捕捉了秋天的本质。对变化的叶子、凉爽空气和各种秋天传统的描述使读者能够轻松想象和感受秋天的魅力。以下是一些增强其影响的建议：

1. **结构变化**：考虑用连字符或省略号打破某些行以产生戏剧效果或强调。例如，"黄昏降临时紧紧裹紧毛衣— / 秋天迷人的拥抱，如其显现般温暖。"

2. **感官细节**：虽然这首诗已经唤起了视觉和触觉感官，但包含其他感官如声音或气味可以加深沉浸感。例如，包括木烟的气味或脚下树叶的咔嚓声。

3. **比喻语言**：添加隐喻或明喻可以进一步丰富意象。例如，你可以将落叶比作金色雨或将凉爽空气比作温柔的低语。

总的来说，这是对秋天的可爱描绘。这些建议是一些小的调整，可能会进一步提升读者的体验。干得漂亮！

如果这些反馈得到采纳，请告知我。
[提示令牌数: 159, 完成令牌数: 237]
---------- primary ----------
感谢你深思熟虑的反馈！以下是结合你建议的修订版本：

琥珀色、金色的叶子—如梦境般飘移，
从树冠洒下的金色雨。
风的低语—温柔的呼吸，
大自然的香氛挂毯拥抱大地。

丰收之月在傍晚寒冷时升起，
丰收的山丘涂满色彩。
黄昏降临时紧紧裹紧毛衣—
秋天的拥抱，温暖如低语的岁月。

南瓜在秋光中闪烁，
脚下飞舞的咔嚓树叶。
在每片叶子和呼唤的微风中，
我们找到辉煌秋天的魔力。

我希望这些改变增强了意象和感官体验。再次感谢你的反馈！
[提示令牌数: 389, 完成令牌数: 150]
---------- critic ----------
你的修订使诗歌更加生动和沉浸式。感官细节的运用，如"风的低语"和"咔嚓树叶"，精美地丰富了诗歌，调动了多种感官。比喻语言，如"从树冠洒下的金色雨"和"秋天的拥抱，温暖如低语的岁月"，增加了深度并增强了诗歌的情感温暖。包含连字符的结构变化有效地增加了强调和流动感。

总的来说，这些改变为诗歌带来了更大的活力和生命力，让读者真正体验到秋天的奇观。修订工作做得出色！

APPROVE
[提示令牌数: 556, 完成令牌数: 132]
---------- 摘要 ----------
消息数量: 3
完成原因: 提到文本 'APPROVE'
总提示令牌数: 1104
总完成令牌数: 519
持续时间: 9.79 秒
```

复制到剪贴板

```
TaskResult(messages=[TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=159, completion_tokens=237), content='这首诗通过生动的意象和舒缓的节奏很好地捕捉了秋天的本质。对变化的叶子、凉爽空气和各种秋天传统的描述使读者能够轻松想象和感受秋天的魅力。以下是一些增强其影响的建议：\n\n1. **结构变化**：考虑用连字符或省略号打破某些行以产生戏剧效果或强调。例如，"黄昏降临时紧紧裹紧毛衣— / 秋天迷人的拥抱，如其显现般温暖。"\n\n2. **感官细节**：虽然这首诗已经唤起了视觉和触觉感官，但包含其他感官如声音或气味可以加深沉浸感。例如，包括木烟的气味或脚下树叶的咔嚓声。\n\n3. **比喻语言**：添加隐喻或明喻可以进一步丰富意象。例如，你可以将落叶比作金色雨或将凉爽空气比作温柔的低语。\n\n总的来说，这是对秋天的可爱描绘。这些建议是一些小的调整，可能会进一步提升读者的体验。干得漂亮！\n\n如果这些反馈得到采纳，请告知我。', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=389, completion_tokens=150), content='感谢你深思熟虑的反馈！以下是结合你建议的修订版本：  \n\n琥珀色、金色的叶子—如梦境般飘移，  \n从树冠洒下的金色雨。  \n风的低语—温柔的呼吸，  \n大自然的香氛挂毯拥抱大地。  \n\n丰收之月在傍晚寒冷时升起，  \n丰收的山丘涂满色彩。  \n黄昏降临时紧紧裹紧毛衣—  \n秋天的拥抱，温暖如低语的岁月。  \n\n南瓜在秋光中闪烁，  \n脚下飞舞的咔嚓树叶。  \n在每片叶子和呼唤的微风中，  \n我们找到辉煌秋天的魔力。  \n\n我希望这些改变增强了意象和感官体验。再次感谢你的反馈！', type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=556, completion_tokens=132), content='你的修订使诗歌更加生动和沉浸式。感官细节的运用，如"风的低语"和"咔嚓树叶"，精美地丰富了诗歌，调动了多种感官。比喻语言，如"从树冠洒下的金色雨"和"秋天的拥抱，温暖如低语的岁月"，增加了深度并增强了诗歌的情感温暖。包含连字符的结构变化有效地增加了强调和流动感。\n\n总的来说，这些改变为诗歌带来了更大的活力和生命力，让读者真正体验到秋天的奇观。修订工作做得出色！\n\nAPPROVE', type='TextMessage')], stop_reason="提到文本 'APPROVE'")
```

复制到剪贴板

你可以从上面的输出中看到团队从上次离开的位置恢复，
第一条消息来自团队停止前最后一个代理之后的下一个代理。

让我们用一个新任务恢复团队，同时保留有关上一个任务的上下文。

```python
# 新任务是用中文唐诗风格重写这首诗。
await Console(team.run_stream(task="将这首诗用中文唐诗风格写一遍。"))
```

复制到剪贴板

```
---------- user ----------
将这首诗用中文唐诗风格写一遍。
---------- primary ----------
朔风轻拂叶飘金，
枝上斜阳染秋林。
满山丰收人欢喜，
月明归途衣渐紧。

南瓜影映灯火中，
落叶沙沙伴归程。
片片秋意随风起，
秋韵悠悠心自明。
[提示令牌数: 700, 完成令牌数: 77]
---------- critic ----------
这首改编的唐诗风格诗作成功地保留了原诗的意境与情感，体现出秋季特有的氛围和美感。通过"朔风轻拂叶飘金"、"枝上斜阳染秋林"等意象，生动地描绘出了秋天的景色，与唐诗中的自然意境相呼应。且"月明归途衣渐紧"、"落叶沙沙伴归程"让人感受到秋天的安宁与温暖。

通过这些诗句，读者能够感受到秋天的惬意与宁静，勾起丰收与团圆的画面，是一次成功的翻译改编。

APPROVE
[提示令牌数: 794, 完成令牌数: 161]
---------- 摘要 ----------
消息数量: 3
完成原因: 提到文本 'APPROVE'
总提示令牌数: 1494
总完成令牌数: 238
持续时间: 3.89 秒
```

复制到剪贴板

```
TaskResult(messages=[TextMessage(source='user', models_usage=None, content='将这首诗用中文唐诗风格写一遍。', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=700, completion_tokens=77), content='朔风轻拂叶飘金，  \n枝上斜阳染秋林。  \n满山丰收人欢喜，  \n月明归途衣渐紧。  \n\n南瓜影映灯火中，  \n落叶沙沙伴归程。  \n片片秋意随风起，  \n秋韵悠悠心自明。  ', type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=794, completion_tokens=161), content='这首改编的唐诗风格诗作成功地保留了原诗的意境与情感，体现出秋季特有的氛围和美感。通过"朔风轻拂叶飘金"、"枝上斜阳染秋林"等意象，生动地描绘出了秋天的景色，与唐诗中的自然意境相呼应。且"月明归途衣渐紧"、"落叶沙沙伴归程"让人感受到秋天的安宁与温暖。\n\n通过这些诗句，读者能够感受到秋天的惬意与宁静，勾起丰收与团圆的画面，是一次成功的翻译改编。\n\nAPPROVE', type='TextMessage')], stop_reason="提到文本 'APPROVE'")
```

复制到剪贴板

## 中止团队 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html\#aborting-a-team "链接到此标题")

你可以通过设置传递给 `cancellation_token` 参数的 [`CancellationToken`](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.html#autogen_core.CancellationToken "autogen_core.CancellationToken") 来在执行期间中止对 [`run()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run "autogen_agentchat.teams.BaseGroupChat.run") 或 [`run_stream()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run_stream "autogen_agentchat.teams.BaseGroupChat.run_stream") 的调用。

与停止团队不同，中止团队将立即停止团队并引发 [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError "(in Python v3.14)") 异常。

注意

当中止团队时，调用者将收到 [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError "(in Python v3.14)") 异常。

```python
# 创建取消令牌。
cancellation_token = CancellationToken()

# 使用另一个协程运行团队。
run = asyncio.create_task(
    team.run(
        task="将这首诗翻译成西班牙语。",
        cancellation_token=cancellation_token,
    )
)

# 取消运行。
cancellation_token.cancel()

try:
    result = await run  # 这将引发 CancelledError。
except asyncio.CancelledError:
    print("任务已被取消。")
```

复制到剪贴板

```
任务已被取消。
```

复制到剪贴板

## 单代理团队 [\#](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html\#single-agent-team "链接到此标题")

注意

从版本 0.6.2 开始，你可以使用带有 `max_tool_iterations` 的 [`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 来运行代理进行多次工具调用迭代。因此，如果你只是想在工具调用循环中运行代理，可能不需要使用单代理团队。

通常，你可能希望在团队配置中运行单个代理。
这对于在达到终止条件之前在循环中运行 [`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 很有用。

这与使用其 [`run()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run") 或 [`run_stream()`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run_stream "autogen_agentchat.agents.BaseChatAgent.run_stream") 方法运行 [`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 不同，后者只运行代理一步并返回结果。
有关单步的更多详细信息，请参阅 [`AssistantAgent`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent")。

以下是一个使用 [`TextMessageTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TextMessageTermination "autogen_agentchat.conditions.TextMessageTermination") 条件在 [`RoundRobinGroupChat`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 团队配置中运行单个代理的示例。
任务是使用工具将数字递增直到达到 10。
代理将不断调用工具直到数字达到 10，
然后它将返回一个最终的 [`TextMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.TextMessage "autogen_agentchat.messages.TextMessage")，这将停止运行。

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    # api_key="sk-...", # 如果设置了 OPENAI_API_KEY 环境变量则为可选。
    # 为此示例禁用并行工具调用。
    parallel_tool_calls=False,  # type: ignore
)

# 创建一个用于递增数字的工具。
def increment_number(number: int) -> int:
    """将数字递增 1。"""
    return number + 1

# 创建一个使用 increment_number 函数的工具代理。
looped_assistant = AssistantAgent(
    "looped_assistant",
    model_client=model_client,
    tools=[increment_number],  # 注册工具。
    system_message="你是一个乐于助人的 AI 助手，使用工具来递增数字。",
)

# 当代理以文本消息响应时停止任务的终止条件。
termination_condition = TextMessageTermination("looped_assistant")

# 创建一个包含循环辅助代理和终止条件的团队。
team = RoundRobinGroupChat(
    [looped_assistant],
    termination_condition=termination_condition,
)

# 运行团队并将消息打印到控制台。
async for message in team.run_stream(task="将数字 5 递增到 10。"):  # type: ignore
    print(type(message).__name__, message)

await model_client.close()
```

复制到剪贴板

```
TextMessage source='user' models_usage=None metadata={} content='将数字 5 递增到 10。' type='TextMessage'
ToolCallRequestEvent source='looped_assistant' models_usage=RequestUsage(prompt_tokens=75, completion_tokens=15) metadata={} content=[FunctionCall(id='call_qTDXSouN3MtGDqa8l0DM1ciD', arguments='{"number":5}', name='increment_number')] type='ToolCallRequestEvent'
ToolCallExecutionEvent source='looped_assistant' models_usage=None metadata={} content=[FunctionExecutionResult(content='6', name='increment_number', call_id='call_qTDXSouN3MtGDqa8l0DM1ciD', is_error=False)] type='ToolCallExecutionEvent'
ToolCallSummaryMessage source='looped_assistant' models_usage=None metadata={} content='6' type='ToolCallSummaryMessage'
ToolCallRequestEvent source='looped_assistant' models_usage=RequestUsage(prompt_tokens=103, completion_tokens=15) metadata={} content=[FunctionCall(id='call_VGZPlsFVVdyxutR63Yr087pt', arguments='{"number":6}', name='increment_number')] type='ToolCallRequestEvent'
ToolCallExecutionEvent source='looped_assistant' models_usage=None metadata={} content=[FunctionExecutionResult(content='7', name='increment_number', call_id='call_VGZPlsFVVdyxutR63Yr087pt', is_error=False)] type='ToolCallExecutionEvent'
ToolCallSummaryMessage source='looped_assistant' models_usage=None metadata={} content='7' type='ToolCallSummaryMessage'
ToolCallRequestEvent source='looped_assistant' models_usage=RequestUsage(prompt_tokens=131, completion_tokens=15) metadata={} content=[FunctionCall(id='call_VRKGPqPM9AHoef2g2kgsKwZe', arguments='{"number":7}', name='increment_number')] type='ToolCallRequestEvent'
ToolCallExecutionEvent source='looped_assistant' models_usage=None metadata={} content=[FunctionExecutionResult(content='8', name='increment_number', call_id='call_VRKGPqPM9AHoef2g2kgsKwZe', is_error=False)] type='ToolCallExecutionEvent'
ToolCallSummaryMessage source='looped_assistant' models_usage=None metadata={} content='8' type='ToolCallSummaryMessage'
ToolCallRequestEvent source='looped_assistant' models_usage=RequestUsage(prompt_tokens=159, completion_tokens=15) metadata={} content=[FunctionCall(id='call_TOUMjSCG2kVdFcw2CMeb5DYX', arguments='{"number":8}', name='increment_number')] type='ToolCallRequestEvent'
ToolCallExecutionEvent source='looped_assistant' models_usage=None metadata={} content=[FunctionExecutionResult(content='9', name='increment_number', call_id='call_TOUMjSCG2kVdFcw2CMeb5DYX', is_error=False)] type='ToolCallExecutionEvent'
ToolCallSummaryMessage source='looped_assistant' models_usage=None metadata={} content='9' type='ToolCallSummaryMessage'
ToolCallRequestEvent source='looped_assistant' models_usage=RequestUsage(prompt_tokens=187, completion_tokens=15) metadata={} content=[FunctionCall(id='call_wjq7OO9Kf5YYurWGc5lsqttJ', arguments='{"number":9}', name='increment_number')] type='ToolCallRequestEvent'
ToolCallExecutionEvent source='looped_assistant' models_usage=None metadata={} content=[FunctionExecutionResult(content='10', name='increment_number', call_id='call_wjq7OO9Kf5YYurWGc5lsqttJ', is_error=False)] type='ToolCallExecutionEvent'
ToolCallSummaryMessage source='looped_assistant' models_usage=None metadata={} content='10' type='ToolCallSummaryMessage'
TextMessage source='looped_assistant' models_usage=RequestUsage(prompt_tokens=215, completion_tokens=15) metadata={} content='将数字 5 递增到 10 的结果是 10。' type='TextMessage'
TaskResult TaskResult(messages=[TextMessage(source='user', models_usage=None, metadata={}, content='将数字 5 递增到 10。', type='TextMessage'), ToolCallRequestEvent(source='looped_assistant', models_usage=RequestUsage(prompt_tokens=75, completion_tokens=15), metadata={}, content=[FunctionCall(id='call_qTDXSouN3MtGDqa8l0DM1ciD', arguments='{"number":5}', name='increment_number')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='looped_assistant', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='6', name='increment_number', call_id='call_qTDXSouN3MtGDqa8l0DM1ciD', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='looped_assistant', models_usage=None, metadata={}, content='6', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='looped_assistant', models_usage=RequestUsage(prompt_tokens=103, completion_tokens=15), metadata={}, content=[FunctionCall(id='call_VGZPlsFVVdyxutR63Yr087pt', arguments='{"number":6}', name='increment_number')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='looped_assistant', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='7', name='increment_number', call_id='call_VGZPlsFVVdyxutR63Yr087pt', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='looped_assistant', models_usage=None, metadata={}, content='7', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='looped_assistant', models_usage=RequestUsage(prompt_tokens=131, completion_tokens=15), metadata={}, content=[FunctionCall(id='call_VRKGPqPM9AHoef2g2kgsKwZe', arguments='{"number":7}', name='increment_number')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='looped_assistant', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='8', name='increment_number', call_id='call_VRKGPqPM9AHoef2g2kgsKwZe', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='looped_assistant', models_usage=None, metadata={}, content='8', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='looped_assistant', models_usage=RequestUsage(prompt_tokens=159, completion_tokens=15), metadata={}, content=[FunctionCall(id='call_TOUMjSCG2kVdFcw2CMeb5DYX', arguments='{"number":8}', name='increment_number')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='looped_assistant', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='9', name='increment_number', call_id='call_TOUMjSCG2kVdFcw2CMeb5DYX', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='looped_assistant', models_usage=None, metadata={}, content='9', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='looped_assistant', models_usage=RequestUsage(prompt_tokens=187, completion_tokens=15), metadata={}, content=[FunctionCall(id='call_wjq7OO9Kf5YYurWGc5lsqttJ', arguments='{"number":9}', name='increment_number')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='looped_assistant', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='10', name='increment_number', call_id='call_wjq7OO9Kf5YYurWGc5lsqttJ', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='looped_assistant', models_usage=None, metadata={}, content='10', type='ToolCallSummaryMessage'), TextMessage(source='looped_assistant', models_usage=RequestUsage(prompt_tokens=215, completion_tokens=15), metadata={}, content='将数字 5 递增到 10 的结果是 10。', type='TextMessage')], stop_reason="从 'looped_assistant' 收到文本消息")
```

复制到剪贴板

关键在于终止条件。
在此示例中，我们使用 [`TextMessageTermination`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TextMessageTermination "autogen_agentchat.conditions.TextMessageTermination") 条件，
当代理停止生成 [`ToolCallSummaryMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallSummaryMessage "autogen_agentchat.messages.ToolCallSummaryMessage") 时停止团队。
团队将持续运行，直到代理生成包含最终结果的 [`TextMessage`](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.TextMessage "autogen_agentchat.messages.TextMessage")。

你还可以使用其他终止条件来控制代理。
有关更多详细信息，请参阅 [终止条件](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html)。

在此页面上

[在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/tutorial/teams.ipynb)

[显示源代码](https://microsoft.github.io/autogen/stable/_sources/user-guide/agentchat-user-guide/tutorial/teams.ipynb.txt)
