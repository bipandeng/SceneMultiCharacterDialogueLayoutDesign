<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/group-chat.html -->

# 群聊#

群聊(Group chat)是一种设计模式,其中一组智能体共享同一消息流:它们都订阅并发布到同一主题。每个参与的智能体都专注于一项特定任务,例如在协同写作任务中担任作者(writer)、插画师(illustrator)或编辑(editor)。你也可以引入一个代表人类用户的智能体,以便在需要时引导其他智能体。

在群聊中,参与者轮流发布消息,过程是顺序进行的——同一时刻只有一个智能体在工作。在底层,发言的轮次顺序由一个 Group Chat Manager(群聊管理器)智能体来维护,该管理器在收到消息后选择下一个发言的智能体。选择下一个智能体的具体算法可以根据你的应用需求而变化。通常,会使用轮询(round-robin)算法或带有 LLM 模型的选择器(selector)。

群聊对于将复杂任务动态地分解为可由角色定义明确的专业智能体处理的小任务非常有用。你还可以将群聊嵌套成层次结构,其中每个参与者本身可以是一个递归的群聊。

在本例中,我们使用 AutoGen 的 Core API 通过事件驱动的智能体来实现群聊模式。请先阅读 [Topics and Subscriptions](../core-concepts/topic-and-subscription.html) 以理解相关概念,然后阅读 [Messages and Communication](../framework/message-and-communication.html) 以了解发布-订阅(pub-sub)的 API 用法。我们将演示一个群聊的简单示例,该示例使用基于 LLM 的选择器作为群聊管理器,用于创作一本儿童故事书的内容。

Note

虽然这个示例说明了群聊机制,但它比较复杂,代表了一个起点,你可以在此基础上使用自定义的智能体和发言者选择算法来构建自己的群聊系统。[AgentChat API](../../agentchat-user-guide/index.html) 内置了 selector group chat 的实现。如果你不想使用 Core API,可以直接使用该实现。

我们将使用 [rich](https://github.com/Textualize/rich) 库以更友好的格式显示消息。
    
    
    # ! pip install rich
    
    
    
    import json
    import string
    import uuid
    from typing import List
    
    import openai
    from autogen_core import (
        DefaultTopicId,
        FunctionCall,
        Image,
        MessageContext,
        RoutedAgent,
        SingleThreadedAgentRuntime,
        TopicId,
        TypeSubscription,
        message_handler,
    )
    from autogen_core.models import (
        AssistantMessage,
        ChatCompletionClient,
        LLMMessage,
        SystemMessage,
        UserMessage,
    )
    from autogen_core.tools import FunctionTool
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from IPython.display import display  # type: ignore
    from pydantic import BaseModel
    from rich.console import Console
    from rich.markdown import Markdown
    

## 消息协议#

群聊模式的消息协议非常简单。

  1. 首先,用户或外部智能体向所有参与者共同的主题发布一条 `GroupChatMessage` 消息。

  2. 群聊管理器选择下一个发言者,并向该智能体发送一条 `RequestToSpeak` 消息。

  3. 该智能体在收到 `RequestToSpeak` 消息后,会向共同主题发布一条 `GroupChatMessage` 消息。

  4. 该过程持续进行,直到群聊管理器达到某个终止条件,此时它将停止发出 `RequestToSpeak` 消息,群聊结束。

下图展示了上述步骤 2 到 4 的过程。

![Group chat message protocol](../../../_images/groupchat.svg)
    
    
    class GroupChatMessage(BaseModel):
        body: UserMessage
    
    
    class RequestToSpeak(BaseModel):
        pass
    

## 基础群聊智能体#

让我们首先定义一个仅使用 LLM 模型生成文本的智能体类。它将作为群聊中所有 AI 智能体的基类。
    
    
    class BaseGroupChatAgent(RoutedAgent):
        """A group chat participant using an LLM."""
    
        def __init__(
            self,
            description: str,
            group_chat_topic_type: str,
            model_client: ChatCompletionClient,
            system_message: str,
        ) -> None:
            super().__init__(description=description)
            self._group_chat_topic_type = group_chat_topic_type
            self._model_client = model_client
            self._system_message = SystemMessage(content=system_message)
            self._chat_history: List[LLMMessage] = []
    
        @message_handler
        async def handle_message(self, message: GroupChatMessage, ctx: MessageContext) -> None:
            self._chat_history.extend(
                [
                    UserMessage(content=f"Transferred to {message.body.source}", source="system"),
                    message.body,
                ]
            )
    
        @message_handler
        async def handle_request_to_speak(self, message: RequestToSpeak, ctx: MessageContext) -> None:
            # print(f"\n{'-'*80}\n{self.id.type}:", flush=True)
            Console().print(Markdown(f"### {self.id.type}: "))
            self._chat_history.append(
                UserMessage(content=f"Transferred to {self.id.type}, adopt the persona immediately.", source="system")
            )
            completion = await self._model_client.create([self._system_message] + self._chat_history)
            assert isinstance(completion.content, str)
            self._chat_history.append(AssistantMessage(content=completion.content, source=self.id.type))
            Console().print(Markdown(completion.content))
            # print(completion.content, flush=True)
            await self.publish_message(
                GroupChatMessage(body=UserMessage(content=completion.content, source=self.id.type)),
                topic_id=DefaultTopicId(type=self._group_chat_topic_type),
            )
    

## Writer 和 Editor 智能体#

使用基类,我们可以通过设置不同的系统消息来定义 Writer 和 Editor 智能体。
    
    
    class WriterAgent(BaseGroupChatAgent):
        def __init__(self, description: str, group_chat_topic_type: str, model_client: ChatCompletionClient) -> None:
            super().__init__(
                description=description,
                group_chat_topic_type=group_chat_topic_type,
                model_client=model_client,
                system_message="You are a Writer. You produce good work.",
            )
    
    
    class EditorAgent(BaseGroupChatAgent):
        def __init__(self, description: str, group_chat_topic_type: str, model_client: ChatCompletionClient) -> None:
            super().__init__(
                description=description,
                group_chat_topic_type=group_chat_topic_type,
                model_client=model_client,
                system_message="You are an Editor. Plan and guide the task given by the user. Provide critical feedbacks to the draft and illustration produced by Writer and Illustrator. "
                "Approve if the task is completed and the draft and illustration meets user's requirements.",
            )
    

## 带有图像生成功能的 Illustrator 智能体#

现在让我们定义 `IllustratorAgent`,它使用 DALL-E 模型根据提供的描述生成插图。我们使用 [`FunctionTool`](../../../reference/python/autogen_core.tools.html#autogen_core.tools.FunctionTool "autogen_core.tools.FunctionTool") 包装器将图像生成器设置为工具,并使用模型客户端发起工具调用。
    
    
    class IllustratorAgent(BaseGroupChatAgent):
        def __init__(
            self,
            description: str,
            group_chat_topic_type: str,
            model_client: ChatCompletionClient,
            image_client: openai.AsyncClient,
        ) -> None:
            super().__init__(
                description=description,
                group_chat_topic_type=group_chat_topic_type,
                model_client=model_client,
                system_message="You are an Illustrator. You use the generate_image tool to create images given user's requirement. "
                "Make sure the images have consistent characters and style.",
            )
            self._image_client = image_client
            self._image_gen_tool = FunctionTool(
                self._image_gen, name="generate_image", description="Call this to generate an image. "
            )
    
        async def _image_gen(
            self, character_appearence: str, style_attributes: str, worn_and_carried: str, scenario: str
        ) -> str:
            prompt = f"Digital painting of a {character_appearence} character with {style_attributes}. Wearing {worn_and_carried}, {scenario}."
            response = await self._image_client.images.generate(
                prompt=prompt, model="dall-e-3", response_format="b64_json", size="1024x1024"
            )
            return response.data[0].b64_json  # type: ignore
    
        @message_handler
        async def handle_request_to_speak(self, message: RequestToSpeak, ctx: MessageContext) -> None:  # type: ignore
            Console().print(Markdown(f"### {self.id.type}: "))
            self._chat_history.append(
                UserMessage(content=f"Transferred to {self.id.type}, adopt the persona immediately.", source="system")
            )
            # Ensure that the image generation tool is used.
            completion = await self._model_client.create(
                [self._system_message] + self._chat_history,
                tools=[self._image_gen_tool],
                extra_create_args={"tool_choice": "required"},
                cancellation_token=ctx.cancellation_token,
            )
            assert isinstance(completion.content, list) and all(
                isinstance(item, FunctionCall) for item in completion.content
            )
            images: List[str | Image] = []
            for tool_call in completion.content:
                arguments = json.loads(tool_call.arguments)
                Console().print(arguments)
                result = await self._image_gen_tool.run_json(arguments, ctx.cancellation_token)
                image = Image.from_base64(self._image_gen_tool.return_value_as_string(result))
                image = Image.from_pil(image.image.resize((256, 256)))
                display(image.image)  # type: ignore
                images.append(image)
            await self.publish_message(
                GroupChatMessage(body=UserMessage(content=images, source=self.id.type)),
                DefaultTopicId(type=self._group_chat_topic_type),
            )
    

## 用户智能体#

在所有 AI 智能体都定义好之后,我们现在可以定义用户智能体,它将在群聊中扮演人类用户的角色。

`UserAgent` 的实现通过控制台输入来获取用户的输入。在真实场景中,你可以将其替换为与前端的通信,并订阅来自前端的响应。
    
    
    class UserAgent(RoutedAgent):
        def __init__(self, description: str, group_chat_topic_type: str) -> None:
            super().__init__(description=description)
            self._group_chat_topic_type = group_chat_topic_type
    
        @message_handler
        async def handle_message(self, message: GroupChatMessage, ctx: MessageContext) -> None:
            # When integrating with a frontend, this is where group chat message would be sent to the frontend.
            pass
    
        @message_handler
        async def handle_request_to_speak(self, message: RequestToSpeak, ctx: MessageContext) -> None:
            user_input = input("Enter your message, type 'APPROVE' to conclude the task: ")
            Console().print(Markdown(f"### User: \n{user_input}"))
            await self.publish_message(
                GroupChatMessage(body=UserMessage(content=user_input, source=self.id.type)),
                DefaultTopicId(type=self._group_chat_topic_type),
            )
    

## 群聊管理器#

最后,我们定义 `GroupChatManager` 智能体,它负责管理群聊并使用 LLM 选择下一个发言的智能体。群聊管理器通过在消息中查找 `"APPORVED"` 关键字来判断编辑是否已批准草稿。如果编辑批准了草稿,群聊管理器将停止选择下一个发言者,群聊结束。

群聊管理器的构造函数接受一个参与者主题类型的列表作为参数。为了提示下一个发言者发言,`GroupChatManager` 智能体会向下一个参与者的主题发布一条 `RequestToSpeak` 消息。

在本例中,我们还通过记录上一个发言者,确保群聊管理器始终选择不同的参与者作为下一个发言者。这有助于确保群聊不会被单一参与者主导。
    
    
    class GroupChatManager(RoutedAgent):
        def __init__(
            self,
            participant_topic_types: List[str],
            model_client: ChatCompletionClient,
            participant_descriptions: List[str],
        ) -> None:
            super().__init__("Group chat manager")
            self._participant_topic_types = participant_topic_types
            self._model_client = model_client
            self._chat_history: List[UserMessage] = []
            self._participant_descriptions = participant_descriptions
            self._previous_participant_topic_type: str | None = None
    
        @message_handler
        async def handle_message(self, message: GroupChatMessage, ctx: MessageContext) -> None:
            assert isinstance(message.body, UserMessage)
            self._chat_history.append(message.body)
            # If the message is an approval message from the user, stop the chat.
            if message.body.source == "User":
                assert isinstance(message.body.content, str)
                if message.body.content.lower().strip(string.punctuation).endswith("approve"):
                    return
            # Format message history.
            messages: List[str] = []
            for msg in self._chat_history:
                if isinstance(msg.content, str):
                    messages.append(f"{msg.source}: {msg.content}")
                elif isinstance(msg.content, list):
                    line: List[str] = []
                    for item in msg.content:
                        if isinstance(item, str):
                            line.append(item)
                        else:
                            line.append("[Image]")
                    messages.append(f"{msg.source}: {', '.join(line)}")
            history = "\n".join(messages)
            # Format roles.
            roles = "\n".join(
                [
                    f"{topic_type}: {description}".strip()
                    for topic_type, description in zip(
                        self._participant_topic_types, self._participant_descriptions, strict=True
                    )
                    if topic_type != self._previous_participant_topic_type
                ]
            )
            selector_prompt = """You are in a role play game. The following roles are available:
    {roles}.
    Read the following conversation. Then select the next role from {participants} to play. Only return the role.
    
    {history}
    
    Read the above conversation. Then select the next role from {participants} to play. Only return the role.
    """
            system_message = SystemMessage(
                content=selector_prompt.format(
                    roles=roles,
                    history=history,
                    participants=str(
                        [
                            topic_type
                            for topic_type in self._participant_topic_types
                            if topic_type != self._previous_participant_topic_type
                        ]
                    ),
                )
            )
            completion = await self._model_client.create([system_message], cancellation_token=ctx.cancellation_token)
            assert isinstance(completion.content, str)
            selected_topic_type: str
            for topic_type in self._participant_topic_types:
                if topic_type.lower() in completion.content.lower():
                    selected_topic_type = topic_type
                    self._previous_participant_topic_type = selected_topic_type
                    await self.publish_message(RequestToSpeak(), DefaultTopicId(type=selected_topic_type))
                    return
            raise ValueError(f"Invalid role selected: {completion.content}")
    

## 创建群聊#

为了搭建群聊,我们创建一个 [`SingleThreadedAgentRuntime`](../../../reference/python/autogen_core.html#autogen_core.SingleThreadedAgentRuntime "autogen_core.SingleThreadedAgentRuntime") 并注册智能体的工厂函数与订阅。

每个参与者智能体既订阅群聊主题,也订阅其自身的主题,以便接收 `RequestToSpeak` 消息;而群聊管理器智能体只订阅群聊主题。
    
    
    runtime = SingleThreadedAgentRuntime()
    
    editor_topic_type = "Editor"
    writer_topic_type = "Writer"
    illustrator_topic_type = "Illustrator"
    user_topic_type = "User"
    group_chat_topic_type = "group_chat"
    
    editor_description = "Editor for planning and reviewing the content."
    writer_description = "Writer for creating any text content."
    user_description = "User for providing final approval."
    illustrator_description = "An illustrator for creating images."
    
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-2024-08-06",
        # api_key="YOUR_API_KEY",
    )
    
    editor_agent_type = await EditorAgent.register(
        runtime,
        editor_topic_type,  # Using topic type as the agent type.
        lambda: EditorAgent(
            description=editor_description,
            group_chat_topic_type=group_chat_topic_type,
            model_client=model_client,
        ),
    )
    await runtime.add_subscription(TypeSubscription(topic_type=editor_topic_type, agent_type=editor_agent_type.type))
    await runtime.add_subscription(TypeSubscription(topic_type=group_chat_topic_type, agent_type=editor_agent_type.type))
    
    writer_agent_type = await WriterAgent.register(
        runtime,
        writer_topic_type,  # Using topic type as the agent type.
        lambda: WriterAgent(
            description=writer_description,
            group_chat_topic_type=group_chat_topic_type,
            model_client=model_client,
        ),
    )
    await runtime.add_subscription(TypeSubscription(topic_type=writer_topic_type, agent_type=writer_agent_type.type))
    await runtime.add_subscription(TypeSubscription(topic_type=group_chat_topic_type, agent_type=writer_agent_type.type))
    
    illustrator_agent_type = await IllustratorAgent.register(
        runtime,
        illustrator_topic_type,
        lambda: IllustratorAgent(
            description=illustrator_description,
            group_chat_topic_type=group_chat_topic_type,
            model_client=model_client,
            image_client=openai.AsyncClient(
                # api_key="YOUR_API_KEY",
            ),
        ),
    )
    await runtime.add_subscription(
        TypeSubscription(topic_type=illustrator_topic_type, agent_type=illustrator_agent_type.type)
    )
    await runtime.add_subscription(
        TypeSubscription(topic_type=group_chat_topic_type, agent_type=illustrator_agent_type.type)
    )
    
    user_agent_type = await UserAgent.register(
        runtime,
        user_topic_type,
        lambda: UserAgent(description=user_description, group_chat_topic_type=group_chat_topic_type),
    )
    await runtime.add_subscription(TypeSubscription(topic_type=user_topic_type, agent_type=user_agent_type.type))
    await runtime.add_subscription(TypeSubscription(topic_type=group_chat_topic_type, agent_type=user_agent_type.type))
    
    group_chat_manager_type = await GroupChatManager.register(
        runtime,
        "group_chat_manager",
        lambda: GroupChatManager(
            participant_topic_types=[writer_topic_type, illustrator_topic_type, editor_topic_type, user_topic_type],
            model_client=model_client,
            participant_descriptions=[writer_description, illustrator_description, editor_description, user_description],
        ),
    )
    await runtime.add_subscription(
        TypeSubscription(topic_type=group_chat_topic_type, agent_type=group_chat_manager_type.type)
    )
    

## 运行群聊#

我们启动运行时,并为任务发布一条 `GroupChatMessage`,从而开启群聊。
    
    
    runtime.start()
    session_id = str(uuid.uuid4())
    await runtime.publish_message(
        GroupChatMessage(
            body=UserMessage(
                content="Please write a short story about the gingerbread man with up to 3 photo-realistic illustrations.",
                source="User",
            )
        ),
        TopicId(type=group_chat_topic_type, source=session_id),
    )
    await runtime.stop_when_idle()
    await model_client.close()
    
    
    
                                                          Writer:                                                      
    
    
    
    Title: The Escape of the Gingerbread Man                                                                           
    
    Illustration 1: A Rustic Kitchen Scene In a quaint little cottage at the edge of an enchanted forest, an elderly   
    woman, with flour-dusted hands, carefully shapes gingerbread dough on a wooden counter. The aroma of ginger,       
    cinnamon, and cloves wafts through the air as a warm breeze from the open window dances with fluttering curtains.  
    The sunlight gently permeates the cozy kitchen, casting a golden hue over the flour-dusted surfaces and the rolling
    pin. Heartfelt trinkets and rustic decorations adorn the shelves - signs of a lived-in, lovingly nurtured home.    
    
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    Story:                                                                                                             
    
    Once there was an old woman who lived alone in a charming cottage, her days filled with the joyful art of baking.  
    One sunny afternoon, she decided to make a special gingerbread man to keep her company. As she shaped him tenderly 
    and placed him in the oven, she couldn't help but smile at the delight he might bring.                             
    
    But to her astonishment, once she opened the oven door to check on her creation, the gingerbread man leapt out,    
    suddenly alive. His eyes were bright as beads, and his smile cheeky and wide. "Run, run, as fast as you can! You   
    can't catch me, I'm the Gingerbread Man!" he laughed, darting towards the door.                                    
    
    The old woman, chuckling at the unexpected mischief, gave chase, but her footsteps were slow with the weight of    
    age. The Gingerbread Man raced out of the door and into the sunny afternoon.                                       
    
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    Illustration 2: A Frolic Through the Meadow The Gingerbread Man darts through a vibrant meadow, his arms swinging  
    joyously by his sides. Behind him trails the old woman, her apron flapping in the wind as she gently tries to catch
    up. Wildflowers of every color bloom vividly under the radiant sky, painting the scene with shades of nature's     
    brilliance. Birds flit through the sky and a stream babbles nearby, oblivious to the chase taking place below.     
    
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    Continuing his sprint, the Gingerbread Man encountered a cow grazing peacefully. Intrigued, the cow trotted        
    forward. "Stop, Gingerbread Man! I wish to eat you!" she called, but the Gingerbread Man only twirled in a teasing 
    jig, flashing his icing smile before darting off again.                                                            
    
    "Run, run, as fast as you can! You can't catch me, I'm the Gingerbread Man!" he taunted, leaving the cow in his    
    spicy wake.                                                                                                        
    
    As he zoomed across the meadow, he spied a cautious horse in a nearby paddock, who neighed, "Oh! You look          
    delicious! I want to eat you!" But the Gingerbread Man only laughed, his feet barely touching the earth. The horse 
    joined the trail, hooves pounding, but even he couldn't match the Gingerbread Man's pace.                          
    
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    Illustration 3: A Bridge Over a Sparkling River Arriving at a wooden bridge across a shimmering river, the         
    Gingerbread Man pauses momentarily, his silhouette against the glistening water. Sunlight sparkles off the water's 
    soft ripples casting reflections that dance like small constellations. A sly fox emerges from the shadows of a     
    blooming willow on the riverbank, his eyes alight with cunning and curiosity.                                      
    
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    The Gingerbread Man bounded onto the bridge and skirted past a sly, watching fox. "Foolish Gingerbread Man," the   
    fox mused aloud, "you might have outrun them all, but you can't possibly swim across that river."                  
    
    Pausing, the Gingerbread Man considered this dilemma. But the fox, oh so clever, offered a dangerous solution.     
    "Climb on my back, and I'll carry you across safely," he suggested with a sly smile.                               
    
    Gingerbread thought himself smarter than that but hesitated, fearing the water or being pursued by the tired,      
    hungry crowd now gathering. "Promise you won't eat me?" he ventured.                                               
    
    "Of course," the fox reassured, a gleam in his eyes that the others pondered from a distance.                      
    
    As they crossed the river, the gingerbread man confident on his ride, the old woman, cow, and horse hoped for his  
    safety. Yet, nearing the middle, the crafty fox tilted his chin and swiftly snapped, swallowing the gingerbread man
    whole.                                                                                                             
    
    Bewildered but awed by the clever twist they had witnessed, the old woman hung her head while the cow and horse    
    ambled away, pondering the fate of the boisterous Gingerbread Man.                                                 
    
    The fox, licking his lips, ambled along the river, savoring his victory, leaving an air of mystery hovering above  
    the shimmering waters, where the memory of the Gingerbread Man's spirited run lingered long after.                 
    
    
    
                                                           User:                                                       
    
    
    
                                                          Editor:                                                      
    
    
    
    Thank you for submitting the draft and illustrations for the short story, "The Escape of the Gingerbread Man."     
    Let's go through the story and illustrations critically:                                                           
    
                                                      Story Feedback:                                                  
    
     1 Plot & Structure:                                                                                               
        • The story follows the traditional gingerbread man tale closely, which might appeal to readers looking for a  
          classic retelling. Consider adding a unique twist or additional layer to make it stand out.                  
     2 Character Development:                                                                                          
        • The gingerbread man is depicted with a cheeky personality, which is consistent throughout. However, for the  
          old woman, cow, horse, and fox, incorporating a bit more personality might enrich the narrative.             
     3 Pacing:                                                                                                         
        • The story moves at a brisk pace, fitting for the short story format. Ensure that each scene provides enough  
          space to breathe, especially during the climactic encounter with the fox.                                    
     4 Tone & Language:                                                                                                
        • The tone is playful and suitable for a fairy-tale audience. The language is accessible, though some richer   
          descriptive elements could enhance the overall atmosphere.                                                   
     5 Moral/Lesson:                                                                                                   
        • The ending carries the traditional moral of caution against naivety. Consider if there are other themes you  
          wish to explore or highlight within the story.                                                               
    
                                                  Illustration Feedback:                                               
    
     1 Illustration 1: A Rustic Kitchen Scene                                                                          
        • The visual captures the essence of a cozy, magical kitchen well. Adding small whimsical elements that hint at
          the gingerbread man’s impending animation might spark more curiosity.                                        
     2 Illustration 2: A Frolic Through the Meadow                                                                     
        • The vibrant colors and dynamic composition effectively convey the chase scene. Make sure the sense of speed  
          and energy of the Gingerbread Man is accentuated, possibly with more expressive motion lines or postures.    
     3 Illustration 3: A Bridge Over a Sparkling River                                                                 
        • The river and reflection are beautifully rendered. The fox, however, could benefit from a more cunning       
          appearance, with sharper features that emphasize its sly nature.                                             
    
                                                        Conclusion:                                                    
    
    Overall, the draft is well-structured, and the illustrations complement the story effectively. With slight         
    enhancements in the narrative's depth and character detail, along with minor adjustments to the illustrations, the 
    project will meet the user's requirements admirably.                                                               
    
    Please make the suggested revisions, and once those are implemented, the story should be ready for approval. Let me
    know if you have any questions or need further guidance!                                                           
    
    
    
                                                       Illustrator:                                                    
    
    
    
    {
        'character_appearence': 'An elderly woman with flour-dusted hands shaping gingerbread dough. Sunlight casts a 
    golden hue in the cozy kitchen, with rustic decorations and trinkets on shelves.',
        'style_attributes': 'Photo-realistic with warm and golden hues.',
        'worn_and_carried': 'The woman wears a flour-covered apron and a gentle smile.',
        'scenario': 'An old woman baking gingerbread in a warm, rustic cottage kitchen.'
    }
    

![../../../_images/44233632b6aae6dcc27b84f8a8c4ee6d99a46bdb26fb92135954f5599a27606e.png](../../../_images/44233632b6aae6dcc27b84f8a8c4ee6d99a46bdb26fb92135954f5599a27606e.png)
    
    
    {
        'character_appearence': 'A gingerbread man with bright bead-like eyes and a wide smile, running joyfully.',
        'style_attributes': 'Photo-realistic with vibrant and lively colors.',
        'worn_and_carried': 'The gingerbread man has white icing features and a cheeky appearance.',
        'scenario': 'The gingerbread man running through a colorful meadow, followed by an old woman, cow, and horse.'
    }
    

![../../../_images/6712bbca303e1defbca5cbcf1a63dfcbc84a747ea3f65913e3b9cdc1e8dd1d38.png](../../../_images/6712bbca303e1defbca5cbcf1a63dfcbc84a747ea3f65913e3b9cdc1e8dd1d38.png)
    
    
    {
        'character_appearence': 'A sly fox with cunning eyes, engaging with the gingerbread man.',
        'style_attributes': 'Photo-realistic with a focus on sly and clever features.',
        'worn_and_carried': 'The fox has sharp features and a lolled tail.',
        'scenario': 'The gingerbread man on a wooden bridge, facing a sly fox by a sparkling river under sunlight.'
    }
    

![../../../_images/5613e43a3461bcbe4b9ac91fd240aeefabcbbf97cc1cb54127bc19a1736b082f.png](../../../_images/5613e43a3461bcbe4b9ac91fd240aeefabcbbf97cc1cb54127bc19a1736b082f.png)
    
    
                                                          Writer:                                                      
    
    
    
    Certainly! Here’s the final version of the short story with the enhanced illustrations for "The Escape of the      
    Gingerbread Man."                                                                                                  
    
    Title: The Escape of the Gingerbread Man                                                                           
    
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    Illustration 1: A Rustic Kitchen Scene In a quaint little cottage at the edge of an enchanted forest, an elderly   
    woman, with flour-dusted hands, carefully shapes gingerbread dough on a wooden counter. The aroma of ginger,       
    cinnamon, and cloves wafts through the air as a warm breeze from the open window dances with fluttering curtains.  
    The sunlight gently permeates the cozy kitchen, casting a golden hue over the flour-dusted surfaces and the rolling
    pin. Heartfelt trinkets and rustic decorations adorn the shelves—a sign of a lived-in, lovingly nurtured home.     
    
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    Story:                                                                                                             
    
    Once there was an old woman who lived alone in a charming cottage, her days filled with the joyful art of baking.  
    One sunny afternoon, she decided to make a special gingerbread man to keep her company. As she shaped him tenderly 
    and placed him in the oven, she couldn't help but smile at the delight he might bring.                             
    
    But to her astonishment, once she opened the oven door to check on her creation, the gingerbread man leapt out,    
    suddenly alive. His eyes were bright as beads, and his smile cheeky and wide. "Run, run, as fast as you can! You   
    can't catch me, I'm the Gingerbread Man!" he laughed, darting towards the door.                                    
    
    The old woman, chuckling at the unexpected mischief, gave chase, but her footsteps were slow with the weight of    
    age. The Gingerbread Man raced out of the door and into the sunny afternoon.                                       
    
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    Illustration 2: A Frolic Through the Meadow The Gingerbread Man darts through a vibrant meadow, his arms swinging  
    joyously by his sides. Behind him trails the old woman, her apron flapping in the wind as she gently tries to catch
    up. Wildflowers of every color bloom vividly under the radiant sky, painting the scene with shades of nature's     
    brilliance. Birds flit through the sky and a stream babbles nearby, oblivious to the chase taking place below.     
    
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    Continuing his sprint, the Gingerbread Man encountered a cow grazing peacefully. Intrigued, the cow trotted        
    forward. "Stop, Gingerbread Man! I wish to eat you!" she called, but the Gingerbread Man only twirled in a teasing 
    jig, flashing his icing smile before darting off again.                                                            
    
    "Run, run, as fast as you can! You can't catch me, I'm the Gingerbread Man!" he taunted, leaving the cow in his    
    spicy wake.                                                                                                        
    
    As he zoomed across the meadow, he spied a cautious horse in a nearby paddock, who neighed, "Oh! You look          
    delicious! I want to eat you!" But the Gingerbread Man only laughed, his feet barely touching the earth. The horse 
    joined the trail, hooves pounding, but even he couldn't match the Gingerbread Man's pace.                          
    
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    Illustration 3: A Bridge Over a Sparkling River Arriving at a wooden bridge across a shimmering river, the         
    Gingerbread Man pauses momentarily, his silhouette against the glistening water. Sunlight sparkles off the water's 
    soft ripples casting reflections that dance like small constellations. A sly fox emerges from the shadows of a     
    blooming willow on the riverbank, his eyes alight with cunning and curiosity.                                      
    
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    The Gingerbread Man bounded onto the bridge and skirted past a sly, watching fox. "Foolish Gingerbread Man," the   
    fox mused aloud, "you might have outrun them all, but you can't possibly swim across that river."                  
    
    Pausing, the Gingerbread Man considered this dilemma. But the fox, oh so clever, offered a dangerous solution.     
    "Climb on my back, and I'll carry you across safely," he suggested with a sly smile.                               
    
    Gingerbread thought himself smarter than that but hesitated, fearing the water or being pursued by the tired,      
    hungry crowd now gathering. "Promise you won't eat me?" he ventured.                                               
    
    "Of course," the fox reassured, a gleam in his eyes that the others pondered from a distance.                      
    
    As they crossed the river, the gingerbread man confident on his ride, the old woman, cow, and horse hoped for his  
    safety. Yet, nearing the middle, the crafty fox tilted his chin and swiftly snapped, swallowing the gingerbread man
    whole.                                                                                                             
    
    Bewildered but awed by the clever twist they had witnessed, the old woman hung her head while the cow and horse    
    ambled away, pondering the fate of the boisterous Gingerbread Man.                                                 
    
    The fox, licking his lips, ambled along the river, savoring his victory, leaving an air of mystery hovering above  
    the shimmering waters, where the memory of the Gingerbread Man's spirited run lingered long after.                 
    
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    I hope you enjoy the enhanced version of the tale!                                                                 
    
    
    
                                                           User:                                                       
    
    approve                                                                                                            
    

从输出中,你可以看到 Writer、Illustrator 与 Editor 智能体轮流发言并协作生成了一本图画书,然后再向用户请求最终批准。

## 下一步#

本示例展示了群聊模式的一种简单实现——**它并不打算在真实应用中使用**。你可以改进发言者选择算法。例如,当简单的规则已经足够且更可靠时,可以避免使用 LLM:你可以使用一条规则,例如让 Editor 始终在 Writer 之后发言。

[AgentChat API](../../agentchat-user-guide/index.html) 为 selector group chat 提供了更高级的 API。它具有更多特性,但整体设计与本实现大致相同。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/design-patterns/group-chat.ipynb)

[ __Show Source](../../../_sources/user-guide/core-user-guide/design-patterns/group-chat.ipynb.txt)