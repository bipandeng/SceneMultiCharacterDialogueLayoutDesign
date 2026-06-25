<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html -->

# 团队#

在本节中，您将学习如何使用 AutoGen 创建 _多代理团队_（或简称团队）。团队是一组协同工作以实现共同目标的代理。

我们将首先向您展示如何创建和运行团队。然后，我们将解释如何观察团队的行为，这对于调试和理解团队性能至关重要，以及控制团队行为的常见操作。

AgentChat 支持以下团队预设：

  * [`RoundRobinGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat")：以轮询方式让参与者轮流运行的群聊团队（在本页介绍）。[教程](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat)

  * [`SelectorGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat")：在每条消息后使用 ChatCompletion 模型选择下一个发言者的团队。[教程](../selector-group-chat.html)

  * [`MagenticOneGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.MagenticOneGroupChat "autogen_agentchat.teams.MagenticOneGroupChat")：用于解决跨多种领域的开放式 Web 和基于文件的任务的通用多代理系统。[教程](../magentic-one.html)

  * [`Swarm`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.Swarm "autogen_agentchat.teams.Swarm")：使用 [`HandoffMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.HandoffMessage "autogen_agentchat.messages.HandoffMessage") 来信号代理之间转换的团队。[教程](../swarm.html)

注意

**何时应该使用团队？**

团队适用于需要协作和多样化知识的复杂任务。然而，与单个代理相比，它们也需要更多的引导工作。虽然 AutoGen 简化了使用团队的过程，但对于较简单的任务，还是从单个代理开始，当单个代理不足以完成任务时再过渡到多代理团队。确保在转向基于团队的方法之前，您已经使用适当的工具和指令优化了单个代理。

## 创建团队#

[`RoundRobinGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 是一种简单而有效的团队配置，其中所有代理共享相同的上下文并以轮询方式轮流响应。每个代理在其轮次期间将其响应广播给所有其他代理，确保整个团队保持一致的上下文。

我们将首先创建一个包含两个 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 和一个 [`TextMentionTermination`](../../../reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TextMentionTermination "autogen_agentchat.conditions.TextMentionTermination") 条件的团队，该条件在代理响应中检测到特定单词时停止团队。

双代理团队实现了 _反射_ 模式，这是一种多代理设计模式，其中一个评论代理评估主要代理的响应。使用 [核心 API](../../core-user-guide/design-patterns/reflection.html) 了解更多关于反射模式的信息。
    
    
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
        system_message="Provide constructive feedback. Respond with 'APPROVE' to when your feedbacks are addressed.",
    )
    
    # 定义一个终止条件，当评论者批准时停止任务。
    text_termination = TextMentionTermination("APPROVE")
    
    # 创建包含主要和评论代理的团队。
    team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=text_termination)
    

## 运行团队#

让我们调用 [`run()`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run "autogen_agentchat.teams.BaseGroupChat.run") 方法来启动团队并执行任务。
    
    
    # 在脚本中运行时使用 `asyncio.run(...)`。
    result = await team.run(task="Write a short poem about the fall season.")
    print(result)
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Write a short poem about the fall season.', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=28, completion_tokens=109), content="Leaves of amber, gold, and rust,  \nDance upon the gentle gust.  \nCrisp air whispers tales of old,  \nAs daylight wanes, the night grows bold.  \n\nPumpkin patch and apple treats,  \nLaughter in the street repeats.  \nSweaters warm and fires aglow,  \nIt's time for nature's vibrant show.  \n\nThe harvest moon ascends the sky,  \nWhile geese in formation start to fly.  \nAutumn speaks in colors bright,  \nA fleeting grace, a pure delight.  ", type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=154, completion_tokens=200), content='Your poem beautifully captures the essence of the fall season with vivid imagery and a rhythmic flow. The use of descriptive language like "amber, gold, and rust" effectively paints a visual picture of the changing leaves. Phrases such as "crisp air whispers tales of old" and "daylight wanes, the night grows bold" add a poetic touch by incorporating seasonal characteristics.\n\nHowever, you might consider exploring other sensory details to deepen the reader\'s immersion. For example, mentioning the sound of crunching leaves underfoot or the scent of cinnamon and spices in the air could enhance the sensory experience.\n\nAdditionally, while the mention of "pumpkin patch and apple treats" is evocative of fall, expanding on these elements or including more personal experiences or emotions associated with the season might make the poem more relatable and engaging.\n\nOverall, you\'ve crafted a lovely poem that celebrates the beauty and traditions of autumn with grace and warmth. A few tweaks to include multisensory details could elevate it even further.', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=347, completion_tokens=178), content="Thank you for the thoughtful feedback. Here's a revised version of the poem with additional sensory details:\n\nLeaves of amber, gold, and rust,  \nDance upon the gentle gust.  \nCrisp air whispers tales of old,  \nAs daylight wanes, the night grows bold.  \n\nCrunch beneath the wandering feet,  \nA melody of autumn's beat.  \nCinnamon and spices blend,  \nIn every breeze, nostalgia sends.  \n\nPumpkin patch and apple treats,  \nLaughter in the street repeats.  \nSweaters warm and fires aglow,  \nIt's time for nature's vibrant show.  \n\nThe harvest moon ascends the sky,  \nWhile geese in formation start to fly.  \nAutumn speaks in colors bright,  \nA fleeting grace, a pure delight.  \n\nI hope this version resonates even more with the spirit of fall. Thank you again for your suggestions!", type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=542, completion_tokens=3), content='APPROVE', type='TextMessage')], stop_reason="Text 'APPROVE' mentioned")
    

团队运行代理直到满足终止条件。在此例中，团队以轮询顺序运行代理，直到在代理响应中检测到单词 "APPROVE" 时满足终止条件。当团队停止时，它返回一个 [`TaskResult`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult") 对象，其中包含团队中代理生成的所有消息。

## 观察团队#

类似于代理的 [`on_messages_stream()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.on_messages_stream "autogen_agentchat.agents.BaseChatAgent.on_messages_stream") 方法，您可以通过调用 [`run_stream()`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run_stream "autogen_agentchat.teams.BaseGroupChat.run_stream") 方法来在团队运行时流式传输其消息。此方法返回一个生成器，它在代理生成消息时生成团队产生的消息，最后一项是 [`TaskResult`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult") 对象。
    
    
    # 在脚本中运行时，使用异步主函数并从 `asyncio.run(...)` 调用它。
    await team.reset()  # 重置团队以执行新任务。
    async for message in team.run_stream(task="Write a short poem about the fall season."):  # type: ignore
        if isinstance(message, TaskResult):
            print("Stop Reason:", message.stop_reason)
        else:
            print(message)
    
    
    
    source='user' models_usage=None content='Write a short poem about the fall season.' type='TextMessage'
    source='primary' models_usage=RequestUsage(prompt_tokens=28, completion_tokens=105) content="Leaves descend in golden dance,  \nWhispering secrets as they fall,  \nCrisp air brings a gentle trance,  \nHeralding Autumn's call.  \n\nPumpkins glow with orange light,  \nFields wear a cloak of amber hue,  \nDays retreat to longer night,  \nSkies shift to deeper blue.  \n\nWinds carry scents of earth and pine,  \nSweaters wrap us, warm and tight,  \nNature's canvas, bold design,  \nIn Fall's embrace, we find delight.  " type='TextMessage'
    source='critic' models_usage=RequestUsage(prompt_tokens=150, completion_tokens=226) content='Your poem beautifully captures the essence of fall with vivid imagery and a soothing rhythm. The imagery of leaves descending, pumpkins glowing, and fields cloaked in amber hues effectively paints a picture of the autumn season. The use of contrasting elements like "Days retreat to longer night" and "Sweaters wrap us, warm and tight" provides a nice balance between the cold and warmth associated with the season. Additionally, the personification of autumn through phrases like "Autumn\'s call" and "Nature\'s canvas, bold design" adds depth to the depiction of fall.\n\nTo enhance the poem further, you might consider focusing on the soundscape of fall, such as the rustling of leaves or the distant call of migrating birds, to engage readers\' auditory senses. Also, varying the line lengths slightly could add a dynamic flow to the reading experience.\n\nOverall, your poem is engaging and effectively encapsulates the beauty and transition of fall. With a few adjustments to explore other sensory details, it could become even more immersive. \n\nIf you incorporate some of these suggestions or find another way to expand the sensory experience, please share your update!' type='TextMessage'
    source='primary' models_usage=RequestUsage(prompt_tokens=369, completion_tokens=143) content="Thank you for the thoughtful critique and suggestions. Here's a revised version of the poem with added attention to auditory senses and varied line lengths:\n\nLeaves descend in golden dance,  \nWhisper secrets in their fall,  \nBreezes hum a gentle trance,  \nHeralding Autumn's call.  \n\nPumpkins glow with orange light,  \nAmber fields beneath wide skies,  \nDays retreat to longer night,  \nChill winds and distant cries.  \n\nRustling whispers of the trees,  \nSweaters wrap us, snug and tight,  \nNature's canvas, bold and free,  \nIn Fall's embrace, pure delight.  \n\nI appreciate your feedback and hope this version better captures the sensory richness of the season!" type='TextMessage'
    source='critic' models_usage=RequestUsage(prompt_tokens=529, completion_tokens=160) content='Your revised poem is a beautiful enhancement of the original. By incorporating auditory elements such as "Breezes hum" and "Rustling whispers of the trees," you\'ve added an engaging soundscape that draws the reader deeper into the experience of fall. The varied line lengths work well to create a more dynamic rhythm throughout the poem, adding interest and variety to each stanza.\n\nThe succinct, yet vivid, lines of "Chill winds and distant cries" wonderfully evoke the atmosphere of the season, adding a touch of mystery and depth. The final stanza wraps up the poem nicely, celebrating the complete sensory embrace of fall with lines like "Nature\'s canvas, bold and free."\n\nYou\'ve successfully infused more sensory richness into the poem, enhancing its overall emotional and atmospheric impact. Great job on the revisions!\n\nAPPROVE' type='TextMessage'
    Stop Reason: Text 'APPROVE' mentioned
    

如上例所示，您可以通过检查 [`stop_reason`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult.stop_reason "autogen_agentchat.base.TaskResult.stop_reason") 属性来确定团队停止的原因。

[`Console()`](../../../reference/python/autogen_agentchat.ui.html#autogen_agentchat.ui.Console "autogen_agentchat.ui.Console") 方法提供了一种方便的方式，以适当的格式将消息打印到控制台。
    
    
    await team.reset()  # 重置团队以执行新任务。
    await Console(team.run_stream(task="Write a short poem about the fall season."))  # 将消息流式传输到控制台。
    
    
    
    ---------- user ----------
    Write a short poem about the fall season.
    ---------- primary ----------
    Golden leaves in crisp air dance,  
    Whispering tales as they prance.  
    Amber hues paint the ground,  
    Nature's symphony all around.  
    
    Sweaters hug with tender grace,  
    While pumpkins smile, a warm embrace.  
    Chill winds hum through towering trees,  
    A vibrant tapestry in the breeze.  
    
    Harvest moons in twilight glow,  
    Casting magic on fields below.  
    Fall's embrace, a gentle call,  
    To savor beauty before snowfalls.  
    [Prompt tokens: 28, Completion tokens: 99]
    ---------- critic ----------
    Your poem beautifully captures the essence of the fall season, creating a vivid and cozy atmosphere. The imagery of golden leaves and amber hues paints a picturesque scene that many can easily relate to. I particularly appreciate the personification of pumpkins and the gentle embrace of sweaters, which adds warmth to your verses. 
    
    To enhance the poem further, you might consider adding more sensory details to make the reader feel even more immersed in the experience. For example, including specific sounds, scents, or textures could deepen the connection to autumn's ambiance. Additionally, you could explore the emotional transitions as the season prepares for winter to provide a reflective element to the piece.
    
    Overall, it's a lovely and evocative depiction of fall, evoking feelings of comfort and appreciation for nature's changing beauty. Great work!
    [Prompt tokens: 144, Completion tokens: 157]
    ---------- primary ----------
    Thank you for your thoughtful feedback! I'm glad you enjoyed the imagery and warmth in the poem. To enhance the sensory experience and emotional depth, here's a revised version incorporating your suggestions:
    
    ---
    
    Golden leaves in crisp air dance,  
    Whispering tales as they prance.  
    Amber hues paint the crunchy ground,  
    Nature's symphony all around.  
    
    Sweaters hug with tender grace,  
    While pumpkins grin, a warm embrace.  
    Chill winds hum through towering trees,  
    Crackling fires warm the breeze.  
    
    Apples in the orchard's glow,  
    Sweet cider scents that overflow.  
    Crunch of paths beneath our feet,  
    Cinnamon spice and toasty heat.  
    
    Harvest moons in twilight's glow,  
    Casting magic on fields below.  
    Fall's embrace, a gentle call,  
    Reflects on life's inevitable thaw.  
    
    --- 
    
    I hope this version enhances the sensory and emotional elements of the season. Thank you again for your insights!
    [Prompt tokens: 294, Completion tokens: 195]
    ---------- critic ----------
    APPROVE
    [Prompt tokens: 506, Completion tokens: 4]
    ---------- Summary ----------
    Number of messages: 5
    Finish reason: Text 'APPROVE' mentioned
    Total prompt tokens: 972
    Total completion tokens: 455
    Duration: 11.78 seconds
    
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Write a short poem about the fall season.', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=28, completion_tokens=99), content="Golden leaves in crisp air dance,  \nWhispering tales as they prance.  \nAmber hues paint the ground,  \nNature's symphony all around.  \n\nSweaters hug with tender grace,  \nWhile pumpkins smile, a warm embrace.  \nChill winds hum through towering trees,  \nA vibrant tapestry in the breeze.  \n\nHarvest moons in twilight glow,  \nCasting magic on fields below.  \nFall's embrace, a gentle call,  \nTo savor beauty before snowfalls.  ", type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=144, completion_tokens=157), content="Your poem beautifully captures the essence of the fall season, creating a vivid and cozy atmosphere. The imagery of golden leaves and amber hues paints a picturesque scene that many can easily relate to. I particularly appreciate the personification of pumpkins and the gentle embrace of sweaters, which adds warmth to your verses. \n\nTo enhance the poem further, you might consider adding more sensory details to make the reader feel even more immersed in the experience. For example, including specific sounds, scents, or textures could deepen the connection to autumn's ambiance. Additionally, you could explore the emotional transitions as the season prepares for winter to provide a reflective element to the piece.\n\nOverall, it's a lovely and evocative depiction of fall, evoking feelings of comfort and appreciation for nature's changing beauty. Great work!", type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=294, completion_tokens=195), content="Thank you for your thoughtful feedback! I'm glad you enjoyed the imagery and warmth in the poem. To enhance the sensory experience and emotional depth, here's a revised version incorporating your suggestions:\n\n---\n\nGolden leaves in crisp air dance,  \nWhispering tales as they prance.  \nAmber hues paint the crunchy ground,  \nNature's symphony all around.  \n\nSweaters hug with tender grace,  \nWhile pumpkins grin, a warm embrace.  \nChill winds hum through towering trees,  \nCrackling fires warm the breeze.  \n\nApples in the orchard's glow,  \nSweet cider scents that overflow.  \nCrunch of paths beneath our feet,  \nCinnamon spice and toasty heat.  \n\nHarvest moons in twilight's glow,  \nCasting magic on fields below.  \nFall's embrace, a gentle call,  \nReflects on life's inevitable thaw.  \n\n--- \n\nI hope this version enhances the sensory and emotional elements of the season. Thank you again for your insights!", type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=506, completion_tokens=4), content='APPROVE', type='TextMessage')], stop_reason="Text 'APPROVE' mentioned")
    

## 重置团队#

您可以通过调用 [`reset()`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.reset "autogen_agentchat.teams.BaseGroupChat.reset") 方法来重置团队。此方法将清除团队的状态，包括所有代理。它将调用每个代理的 [`on_reset()`](../../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.ChatAgent.on_reset "autogen_agentchat.base.ChatAgent.on_reset") 方法来清除代理的状态。
    
    
    await team.reset()  # 重置团队以进行下一次运行。
    

通常，如果下一个任务与上一个任务无关，重置团队是个好主意。但是，如果下一个任务与上一个任务相关，您不需要重置，而是可以继续团队。

## 停止团队#

除了基于团队内部状态的自动终止条件（如 [`TextMentionTermination`](../../../reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TextMentionTermination "autogen_agentchat.conditions.TextMentionTermination")）之外，您还可以使用 [`ExternalTermination`](../../../reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.ExternalTermination "autogen_agentchat.conditions.ExternalTermination") 从外部停止团队。

在 [`ExternalTermination`](../../../reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.ExternalTermination "autogen_agentchat.conditions.ExternalTermination") 上调用 [`set()`](../../../reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.ExternalTermination.set "autogen_agentchat.conditions.ExternalTermination.set") 将在当前代理轮次结束时停止团队。因此，团队可能不会立即停止。这允许当前代理在完成其轮次并在团队停止之前将最终消息广播给团队，保持团队状态一致。
    
    
    # 创建带有外部终止条件的新团队。
    external_termination = ExternalTermination()
    team = RoundRobinGroupChat(
        [primary_agent, critic_agent],
        termination_condition=external_termination | text_termination,  # 使用按位 OR 运算符组合条件。
    )
    
    # 在后台任务中运行团队。
    run = asyncio.create_task(Console(team.run_stream(task="Write a short poem about the fall season.")))
    
    # 等待一段时间。
    await asyncio.sleep(0.1)
    
    # 停止团队。
    external_termination.set()
    
    # 等待团队完成。
    await run
    
    
    
    
    ---------- user ----------
    Write a short poem about the fall season.
    ---------- primary ----------
    Leaves of amber, gold, and red,  
    Gently drifting from trees overhead.  
    Whispers of wind through the crisp, cool air,  
    Nature's canvas painted with care.  
    
    Harvest moons and evenings that chill,  
    Fields of plenty on every hill.  
    Sweaters wrapped tight as twilight nears,  
    Fall's charming embrace, as warm as it appears.  
    
    Pumpkins aglow with autumn's light,  
    Harvest feasts and stars so bright.  
    In every leaf and breeze that calls,  
    We find the magic of glorious fall.  
    [Prompt tokens: 28, Completion tokens: 114]
    ---------- Summary ----------
    Number of messages: 2
    Finish reason: External termination requested
    Total prompt tokens: 28
    Total completion tokens: 114
    Duration: 1.71 seconds
    
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Write a short poem about the fall season.', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=28, completion_tokens=114), content="Leaves of amber, gold, and red,  \nGently drifting from trees overhead.  \nWhispers of wind through the crisp, cool air,  \nNature's canvas painted with care.  \n\nHarvest moons and evenings that chill,  \nFields of plenty on every hill.  \nSweaters wrapped tight as twilight nears,  \nFall's charming embrace, as warm as it appears.  \n\nPumpkins aglow with autumn's light,  \nHarvest feasts and stars so bright.  \nIn every leaf and breeze that calls,  \nWe find the magic of glorious fall.  ", type='TextMessage')], stop_reason='External termination requested')
    

从上面的输出中，您可以看到团队因满足外部终止条件而停止，但发言代理能够在团队停止之前完成其轮次。

## 继续团队#

团队是有状态的，并在每次运行后保持对话历史和上下文，除非您重置团队。

您可以通过再次调用 [`run()`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run "autogen_agentchat.teams.BaseGroupChat.run") 或 [`run_stream()`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run_stream "autogen_agentchat.teams.BaseGroupChat.run_stream") 方法而不提供新任务来继续团队从上次离开的地方继续。[`RoundRobinGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 将以轮询顺序从下一个代理继续。
    
    
    await Console(team.run_stream())  # 继续团队以继续上一个任务。
    
    
    
    ---------- critic ----------
    This poem beautifully captures the essence of the fall season with vivid imagery and a soothing rhythm. The descriptions of the changing leaves, cool air, and various autumn traditions make it easy for readers to envision and feel the charm of fall. Here are a few suggestions to enhance its impact:
    
    1. **Structure Variation**: Consider breaking some lines with a hyphen or ellipsis for dramatic effect or emphasis. For instance, "Sweaters wrapped tight as twilight nears— / Fall's charming embrace, as warm as it appears."
    
    2. **Sensory Details**: While the poem already evokes visual and tactile senses, incorporating other senses such as sound or smell could deepen the immersion. For example, include the scent of wood smoke or the crunch of leaves underfoot.
    
    3. **Metaphorical Language**: Adding metaphors or similes can further enrich the imagery. For example, you might compare the leaves falling to a golden rain or the chill in the air to a gentle whisper.
    
    Overall, it's a lovely depiction of fall. These suggestions are minor tweaks that might elevate the reader's experience even further. Nice work!
    
    Let me know if these feedbacks are addressed.
    [Prompt tokens: 159, Completion tokens: 237]
    ---------- primary ----------
    Thank you for the thoughtful feedback! Here's a revised version, incorporating your suggestions:  
    
    Leaves of amber, gold—drifting like dreams,  
    A golden rain from trees' canopies.  
    Whispers of wind—a gentle breath,  
    Nature's scented tapestry embracing earth.  
    
    Harvest moons rise as evenings chill,  
    Fields of plenty paint every hill.  
    Sweaters wrapped tight as twilight nears—  
    Fall's embrace, warm as whispered years.  
    
    Pumpkins aglow with autumn's light,  
    Crackling leaves underfoot in flight.  
    In every leaf and breeze that calls,  
    We find the magic of glorious fall.
    
    I hope these changes enhance the imagery and sensory experience. Thank you again for your feedback!
    [Prompt tokens: 389, Completion tokens: 150]
    ---------- critic ----------
    Your revisions have made the poem even more evocative and immersive. The use of sensory details, such as "whispers of wind" and "crackling leaves," beautifully enriches the poem, engaging multiple senses. The metaphorical language, like "a golden rain from trees' canopies" and "Fall's embrace, warm as whispered years," adds depth and enhances the emotional warmth of the poem. The structural variation with the inclusion of dashes effectively adds emphasis and flow. 
    
    Overall, these changes bring greater vibrancy and life to the poem, allowing readers to truly experience the wonders of fall. Excellent work on the revisions!
    
    APPROVE
    [Prompt tokens: 556, Completion tokens: 132]
    ---------- Summary ----------
    Number of messages: 3
    Finish reason: Text 'APPROVE' mentioned
    Total prompt tokens: 1104
    Total completion tokens: 519
    Duration: 9.79 seconds
    
    
    
    
    TaskResult(messages=[TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=159, completion_tokens=237), content='This poem beautifully captures the essence of the fall season with vivid imagery and a soothing rhythm. The descriptions of the changing leaves, cool air, and various autumn traditions make it easy for readers to envision and feel the charm of fall. Here are a few suggestions to enhance its impact:\n\n1. **Structure Variation**: Consider breaking some lines with a hyphen or ellipsis for dramatic effect or emphasis. For instance, "Sweaters wrapped tight as twilight nears— / Fall's charming embrace, as warm as it appears."\n\n2. **Sensory Details**: While the poem already evokes visual and tactile senses, incorporating other senses such as sound or smell could deepen the immersion. For example, include the scent of wood smoke or the crunch of leaves underfoot.\n\n3. **Metaphorical Language**: Adding metaphors or similes can further enrich the imagery. For example, you might compare the leaves falling to a golden rain or the chill in the air to a gentle whisper.\n\nOverall, it's a lovely depiction of fall. These suggestions are minor tweaks that might elevate the reader\'s experience even further. Nice work!\n\nLet me know if these feedbacks are addressed.', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=389, completion_tokens=150), content='Thank you for the thoughtful feedback! Here's a revised version, incorporating your suggestions:  \n\nLeaves of amber, gold—drifting like dreams,  \nA golden rain from trees' canopies.  \nWhispers of wind—a gentle breath,  \nNature's scented tapestry embracing earth.  \n\nHarvest moons rise as evenings chill,  \nFields of plenty paint every hill.  \nSweaters wrapped tight as twilight nears—  \nFall's embrace, warm as whispered years.  \n\nPumpkins aglow with autumn's light,  \nCrackling leaves underfoot in flight.  \nIn every leaf and breeze that calls,  \nWe find the magic of glorious fall.  \n\nI hope these changes enhance the imagery and sensory experience. Thank you again for your feedback!', type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=556, completion_tokens=132), content='Your revisions have made the poem even more evocative and immersive. The use of sensory details, such as "whispers of wind" and "crackling leaves," beautifully enriches the poem, engaging multiple senses. The metaphorical language, like "a golden rain from trees' canopies" and "Fall's embrace, warm as whispered years," adds depth and enhances the emotional warmth of the poem. The structural variation with the inclusion of dashes effectively adds emphasis and flow. \n\nOverall, these changes bring greater vibrancy and life to the poem, allowing readers to truly experience the wonders of fall. Excellent work on the revisions!\n\nAPPROVE', type='TextMessage')], stop_reason="Text 'APPROVE' mentioned")
    

您可以从上面的输出中看到团队从上次离开的地方继续，第一条消息来自上次发言代理之后的下一个代理。

让我们用新任务继续团队，同时保留有关上一个任务的上下文。
    
    
    # 新任务是将同一首诗翻译成中文唐诗风格。
    await Console(team.run_stream(task="将这首诗用中文唐诗风格写一遍。"))
    
    
    
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
    [Prompt tokens: 700, Completion tokens: 77]
    ---------- critic ----------
    这首改编的唐诗风格诗作成功地保留了原诗的意境与情感，体现出秋季特有的氛围和美感。通过"朔风轻拂叶飘金"、"枝上斜阳染秋林"等意象，生动地描绘出了秋天的景色，与唐诗中的自然意境相呼应。且"月明归途衣渐紧"、"落叶沙沙伴归程"让人感受到秋天的安宁与温暖。
    
    通过这些诗句，读者能够感受到秋天的惬意与宁静，勾起丰收与团圆的画面，是一次成功的翻译改编。
    
    APPROVE
    [Prompt tokens: 794, Completion tokens: 161]
    ---------- Summary ----------
    Number of messages: 3
    Finish reason: Text 'APPROVE' mentioned
    Total prompt tokens: 1494
    Total completion tokens: 238
    Duration: 3.89 seconds
    
    
    
    
    TaskResult(messages=[TextMessage(source='user', models_usage=None, content='将这首诗用中文唐诗风格写一遍。', type='TextMessage'), TextMessage(source='primary', models_usage=RequestUsage(prompt_tokens=700, completion_tokens=77), content='朔风轻拂叶飘金，  \n枝上斜阳染秋林。  \n满山丰收人欢喜，  \n月明归途衣渐紧。  \n\n南瓜影映灯火中，  \n落叶沙沙伴归程。  \n片片秋意随风起，  \n秋韵悠悠心自明。  ', type='TextMessage'), TextMessage(source='critic', models_usage=RequestUsage(prompt_tokens=794, completion_tokens=161), content='这首改编的唐诗风格诗作成功地保留了原诗的意境与情感，体现出秋季特有的氛围和美感。通过"朔风轻拂叶飘金"、"枝上斜阳染秋林"等意象，生动地描绘出了秋天的景色，与唐诗中的自然意境相呼应。且"月明归途衣渐紧"、"落叶沙沙伴归程"让人感受到秋天的安宁与温暖。\n\n通过这些诗句，读者能够感受到秋天的惬意与宁静，勾起丰收与团圆的画面，是一次成功的翻译改编。\n\nAPPROVE', type='TextMessage')], stop_reason="Text 'APPROVE' mentioned")
    

## 中止团队#

您可以通过设置传递给 `cancellation_token` 参数的 [`CancellationToken`](../../../reference/python/autogen_core.html#autogen_core.CancellationToken "autogen_core.CancellationToken") 来在执行期间中止对 [`run()`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run "autogen_agentchat.teams.BaseGroupChat.run") 或 [`run_stream()`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.BaseGroupChat.run_stream "autogen_agentchat.teams.BaseGroupChat.run_stream") 的调用。

与停止团队不同，中止团队将立即停止团队并引发 [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError "\(in Python v3.14\)") 异常。

注意

当中止团队时，调用者将收到 [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError "\(in Python v3.14\)") 异常。
    
    
    # 创建取消令牌。
    cancellation_token = CancellationToken()
    
    # 使用另一个协程运行团队。
    run = asyncio.create_task(
        team.run(
            task="Translate the poem to Spanish.",
            cancellation_token=cancellation_token,
        )
    )
    
    # 取消运行。
    cancellation_token.cancel()
    
    try:
        result = await run  # 这将引发 CancelledError。
    except asyncio.CancelledError:
        print("Task was cancelled.")
    
    
    
    Task was cancelled.
    

## 单代理团队#

注意

从版本 0.6.2 开始，您可以将 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 与 `max_tool_iterations` 一起使用，以运行多次工具调用的代理。因此，如果您只想在工具调用循环中运行代理，可能不需要使用单代理团队。

通常，您可能希望在团队配置中运行单个代理。这对于在满足终止条件之前在循环中运行 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 很有用。

这与使用代理的 [`run()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run "autogen_agentchat.agents.BaseChatAgent.run") 或 [`run_stream()`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.BaseChatAgent.run_stream "autogen_agentchat.agents.BaseChatAgent.run_stream") 方法不同，后者只运行代理一步并返回结果。有关单步的更多详细信息，请参阅 [`AssistantAgent`](../../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent")。

以下是使用 [`TextMessageTermination`](../../../reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TextMessageTermination "autogen_agentchat.conditions.TextMessageTermination") 条件在 [`RoundRobinGroupChat`](../../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 团队配置中运行单个代理的示例。任务是使用工具将数字递增直到达到 10。代理将不断调用工具直到数字达到 10，然后返回最终的 [`TextMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.TextMessage "autogen_agentchat.messages.TextMessage")，这将停止运行。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import TextMessageTermination
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        # api_key="sk-...", # 如果设置了 OPENAI_API_KEY 环境变量则可选。
        # 为此示例禁用并行工具调用。
        parallel_tool_calls=False,  # type: ignore
    )
    
    
    # 创建递增数字的工具。
    def increment_number(number: int) -> int:
        """Increment a number by 1."""
        return number + 1
    
    
    # 创建使用 increment_number 函数的工具代理。
    looped_assistant = AssistantAgent(
        "looped_assistant",
        model_client=model_client,
        tools=[increment_number],  # 注册工具。
        system_message="You are a helpful AI assistant, use the tool to increment the number.",
    )
    
    # 终止条件，当代理响应文本消息时停止任务。
    termination_condition = TextMessageTermination("looped_assistant")
    
    # 创建包含循环助手代理和终止条件的团队。
    team = RoundRobinGroupChat(
        [looped_assistant],
        termination_condition=termination_condition,
    )
    
    # 运行团队并将消息打印到控制台。
    async for message in team.run_stream(task="Increment the number 5 to 10."):  # type: ignore
        print(type(message).__name__, message)
    
    await model_client.close()
    
    
    
    TextMessage source='user' models_usage=None metadata={} content='Increment the number 5 to 10.' type='TextMessage'
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
    TextMessage source='looped_assistant' models_usage=RequestUsage(prompt_tokens=215, completion_tokens=15) metadata={} content='The number 5 incremented to 10 is 10.' type='TextMessage'
    TaskResult TaskResult(messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Increment the number 5 to 10.', type='TextMessage'), ToolCallRequestEvent(source='looped_assistant', models_usage=RequestUsage(prompt_tokens=75, completion_tokens=15), metadata={}, content=[FunctionCall(id='call_qTDXSouN3MtGDqa8l0DM1ciD', arguments='{"number":5}', name='increment_number')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='looped_assistant', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='6', name='increment_number', call_id='call_qTDXSouN3MtGDqa8l0DM1ciD', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='looped_assistant', models_usage=None, metadata={}, content='6', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='looped_assistant', models_usage=RequestUsage(prompt_tokens=103, completion_tokens=15), metadata={}, content=[FunctionCall(id='call_VGZPlsFVVdyxutR63Yr087pt', arguments='{"number":6}', name='increment_number')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='looped_assistant', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='7', name='increment_number', call_id='call_VGZPlsFVVdyxutR63Yr087pt', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='looped_assistant', models_usage=None, metadata={}, content='7', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='looped_assistant', models_usage=RequestUsage(prompt_tokens=131, completion_tokens=15), metadata={}, content=[FunctionCall(id='call_VRKGPqPM9AHoef2g2kgsKwZe', arguments='{"number":7}', name='increment_number')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='looped_assistant', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='8', name='increment_number', call_id='call_VRKGPqPM9AHoef2g2kgsKwZe', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='looped_assistant', models_usage=None, metadata={}, content='8', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='looped_assistant', models_usage=RequestUsage(prompt_tokens=159, completion_tokens=15), metadata={}, content=[FunctionCall(id='call_TOUMjSCG2kVdFcw2CMeb5DYX', arguments='{"number":8}', name='increment_number')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='looped_assistant', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='9', name='increment_number', call_id='call_TOUMjSCG2kVdFcw2CMeb5DYX', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='looped_assistant', models_usage=None, metadata={}, content='9', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='looped_assistant', models_usage=RequestUsage(prompt_tokens=187, completion_tokens=15), metadata={}, content=[FunctionCall(id='call_wjq7OO9Kf5YYurWGc5lsqttJ', arguments='{"number":9}', name='increment_number')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='looped_assistant', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='10', name='increment_number', call_id='call_wjq7OO9Kf5YYurWGc5lsqttJ', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='looped_assistant', models_usage=None, metadata={}, content='10', type='ToolCallSummaryMessage'), TextMessage(source='looped_assistant', models_usage=RequestUsage(prompt_tokens=215, completion_tokens=15), metadata={}, content='The number 5 incremented to 10 is 10.', type='TextMessage')], stop_reason="Text message received from 'looped_assistant'")
    

关键在于终止条件。在此示例中，我们使用 [`TextMessageTermination`](../../../reference/python/autogen_agentchat.conditions.html#autogen_agentchat.conditions.TextMessageTermination "autogen_agentchat.conditions.TextMessageTermination") 条件，当代理停止生成 [`ToolCallSummaryMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.ToolCallSummaryMessage "autogen_agentchat.messages.ToolCallSummaryMessage") 时停止团队。团队将继续运行，直到代理生成包含最终结果的 [`TextMessage`](../../../reference/python/autogen_agentchat.messages.html#autogen_agentchat.messages.TextMessage "autogen_agentchat.messages.TextMessage")。

您还可以使用其他终止条件来控制代理。有关更多详细信息，请参阅 [终止条件](termination.html)。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/tutorial/teams.ipynb)

[ __Show Source](../../../_sources/user-guide/agentchat-user-guide/tutorial/teams.ipynb.txt)
