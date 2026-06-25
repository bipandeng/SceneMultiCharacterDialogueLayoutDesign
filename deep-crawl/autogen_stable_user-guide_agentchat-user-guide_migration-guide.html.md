<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/migration-guide.html -->

# Migration Guide for v0.2 to v0.4#

这是面向 `autogen-agentchat` 的 `v0.2.*` 版本用户的迁移指南，适用于引入了一套新 API 和功能的 `v0.4` 版本。`v0.4` 版本包含重大更改。请仔细阅读本指南。我们仍在 `0.2` 分支中维护 `v0.2` 版本；但是，我们强烈建议你升级到 `v0.4` 版本。

Note

我们不再拥有 `pyautogen` PyPI 包的管理员访问权限，并且自 0.2.34 版本以来，该包的版本不再来自 Microsoft。要继续使用 `v0.2` 版本的 AutoGen，请使用 `autogen-agentchat~=0.2` 安装。请阅读我们关于分叉的 [澄清声明](https://github.com/microsoft/autogen/discussions/4217)。

## What is `v0.4`?#

自 2023 年 AutoGen 发布以来，我们积极听取来自小型初创公司和大型企业的社区和用户的反馈，收集了大量反馈。基于这些反馈，我们构建了 AutoGen `v0.4`，这是一个从零开始的完全重写，采用异步、事件驱动的架构，以解决可观察性、灵活性、交互控制和可扩展性等问题。

`v0.4` API 是分层的：[Core API](../core-user-guide/index.html) 是基础层，提供可扩展的、事件驱动的 actor 框架，用于创建代理工作流；[AgentChat API](index.html) 构建在 Core 之上，提供任务驱动的高级框架，用于构建交互式代理应用程序。它是 AutoGen `v0.2` 的替代品。

本指南的大部分内容都侧重于 `v0.4` 的 AgentChat API；但是，你也可以仅使用 Core API 构建你自己的高级框架。

## New to AutoGen?#

直接跳转到 [AgentChat Tutorial](tutorial/models.html) 开始使用 `v0.4`。

## What's in this guide?#

我们提供了有关如何将现有代码库从 `v0.2` 迁移到 `v0.4` 的详细指南。

有关如何迁移的详细信息，请参阅下面的每个功能。

  * Migration Guide for v0.2 to v0.4

    * What is `v0.4`?

    * New to AutoGen?

    * What's in this guide?

    * Model Client

      * Use component config

      * Use model client class directly

    * Model Client for OpenAI-Compatible APIs

    * Model Client Cache

    * Assistant Agent

    * Multi-Modal Agent

    * User Proxy

    * RAG Agent

    * Conversable Agent and Register Reply

    * Save and Load Agent State

    * Two-Agent Chat

    * Tool Use

    * Chat Result

    * Conversion between v0.2 and v0.4 Messages

    * Group Chat

    * Group Chat with Resume

    * Save and Load Group Chat State

    * Group Chat with Tool Use

    * Group Chat with Custom Selector (Stateflow)

    * Nested Chat

    * Sequential Chat

    * GPTAssistantAgent

    * Long Context Handling

    * Observability and Control

    * Code Executors

以下目前在 `v0.2` 中的功能将在未来版本的 `v0.4.*` 中提供：

  * Model Client Cost [#4835](https://github.com/microsoft/autogen/issues/4835)

  * Teachable Agent

  * RAG Agent

当缺失功能可用时，我们将更新本指南。

## Model Client#

在 `v0.2` 中，你可以按如下方式配置模型客户端，并创建 `OpenAIWrapper` 对象。
    
    
    from autogen.oai import OpenAIWrapper
    
    config_list = [
        {"model": "gpt-4o", "api_key": "sk-xxx"},
        {"model": "gpt-4o-mini", "api_key": "sk-xxx"},
    ]
    
    model_client = OpenAIWrapper(config_list=config_list)
    

> **Note** ：在 AutoGen 0.2 中，OpenAI 客户端会尝试列表中的配置直到一个有效。0.4 则需要选择一个特定的模型配置。

在 `v0.4` 中，我们提供两种方法来创建模型客户端。

### Use component config#

AutoGen 0.4 具有一个 [通用组件配置系统](../core-user-guide/framework/component-config.html)。模型客户端是它的一个很好的用例。有关如何创建 OpenAI 聊天完成客户端的信息，请参阅下文。
    
    
    from autogen_core.models import ChatCompletionClient
    
    config = {
        "provider": "OpenAIChatCompletionClient",
        "config": {
            "model": "gpt-4o",
            "api_key": "sk-xxx" # os.environ["...']
        }
    }
    
    model_client = ChatCompletionClient.load_component(config)
    

### Use model client class directly#

Open AI:
    
    
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key="sk-xxx")
    

Azure OpenAI:
    
    
    from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
    
    model_client = AzureOpenAIChatCompletionClient(
        azure_deployment="gpt-4o",
        azure_endpoint="https://<your-endpoint>.openai.azure.com/",
        model="gpt-4o",
        api_version="2024-09-01-preview",
        api_key="sk-xxx",
    )
    

阅读更多关于 [`OpenAIChatCompletionClient`](../../reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.OpenAIChatCompletionClient "autogen_ext.models.openai.OpenAIChatCompletionClient") 的信息。

## Model Client for OpenAI-Compatible APIs#

你可以使用 `OpenAIChatCompletionClient` 连接到 OpenAI 兼容的 API，但你需要指定 `base_url` 和 `model_info`。
    
    
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    custom_model_client = OpenAIChatCompletionClient(
        model="custom-model-name",
        base_url="https://custom-model.com/reset/of/the/path",
        api_key="placeholder",
        model_info={
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": "unknown",
            "structured_output": True,
        },
    )
    

> **Note** ：我们不会测试所有 OpenAI 兼容的 API，其中许多 API 的行为与 OpenAI API 不同，即使它们声称支持。请在使用之前进行测试。

阅读 AgentChat 教程中的 [Model Clients](tutorial/models.html) 和 [Core API 文档](../core-user-guide/components/model-clients.html) 中更详细的信息。

未来将添加对其他托管模型的支持。

## Model Client Cache#

在 `v0.2` 中，你可以通过 LLM 配置中的 `cache_seed` 参数设置缓存种子。默认情况下启用缓存。
    
    
    llm_config = {
        "config_list": [{"model": "gpt-4o", "api_key": "sk-xxx"}],
        "seed": 42,
        "temperature": 0,
        "cache_seed": 42,
    }
    

在 `v0.4` 中，默认情况下不启用缓存，要使用它，你需要在模型客户端周围使用 [`ChatCompletionCache`](../../reference/python/autogen_ext.models.cache.html#autogen_ext.models.cache.ChatCompletionCache "autogen_ext.models.cache.ChatCompletionCache") 包装器。

你可以使用 [`DiskCacheStore`](../../reference/python/autogen_ext.cache_store.diskcache.html#autogen_ext.cache_store.diskcache.DiskCacheStore "autogen_ext.cache_store.diskcache.DiskCacheStore") 或 [`RedisStore`](../../reference/python/autogen_ext.cache_store.redis.html#autogen_ext.cache_store.redis.RedisStore "autogen_ext.cache_store.redis.RedisStore") 来存储缓存。
    
    
    pip install -U "autogen-ext[openai, diskcache, redis]"
    

以下是使用 `diskcache` 进行本地缓存的示例：
    
    
    import asyncio
    import tempfile
    
    from autogen_core.models import UserMessage
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_ext.models.cache import ChatCompletionCache, CHAT_CACHE_VALUE_TYPE
    from autogen_ext.cache_store.diskcache import DiskCacheStore
    from diskcache import Cache
    
    
    async def main():
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Initialize the original client
            openai_model_client = OpenAIChatCompletionClient(model="gpt-4o")
    
            # Then initialize the CacheStore, in this case with diskcache.Cache.
            # You can also use redis like:
            # from autogen_ext.cache_store.redis import RedisStore
            # import redis
            # redis_instance = redis.Redis()
            # cache_store = RedisCacheStore[CHAT_CACHE_VALUE_TYPE](redis_instance)
            cache_store = DiskCacheStore[CHAT_CACHE_VALUE_TYPE](Cache(tmpdirname))
            cache_client = ChatCompletionCache(openai_model_client, cache_store)
    
            response = await cache_client.create([UserMessage(content="Hello, how are you?", source="user")])
            print(response)  # Should print response from OpenAI
            response = await cache_client.create([UserMessage(content="Hello, how are you?", source="user")])
            print(response)  # Should print cached response
            await openai_model_client.close()
    
    
    asyncio.run(main())
    

## Assistant Agent#

在 `v0.2` 中，你可以按如下方式创建助手代理：
    
    
    from autogen.agentchat import AssistantAgent
    
    llm_config = {
        "config_list": [{"model": "gpt-4o", "api_key": "sk-xxx"}],
        "seed": 42,
        "temperature": 0,
    }
    
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        llm_config=llm_config,
    )
    

在 `v0.4` 中类似，但需要指定 `model_client` 而不是 `llm_config`。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key="sk-xxx", seed=42, temperature=0)
    
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        model_client=model_client,
    )
    

但是，用法有所不同。在 `v0.4` 中，你调用 `assistant.on_messages` 或 `assistant.on_messages_stream` 来处理传入消息，而不是调用 `assistant.send`。此外，`on_messages` 和 `on_messages_stream` 方法是异步的，后者返回异步生成器以流式传输代理的内部想法。

以下是如何在 `v0.4` 中直接调用助手代理，接上面的示例：
    
    
    import asyncio
    from autogen_agentchat.messages import TextMessage
    from autogen_agentchat.agents import AssistantAgent
    from autogen_core import CancellationToken
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
    
        assistant = AssistantAgent(
            name="assistant",
            system_message="You are a helpful assistant.",
            model_client=model_client,
        )
    
        cancellation_token = CancellationToken()
        response = await assistant.on_messages([TextMessage(content="Hello!", source="user")], cancellation_token)
        print(response)
    
        await model_client.close()
    
    asyncio.run(main())
    

[`CancellationToken`](../../reference/python/autogen_core.html#autogen_core.CancellationToken "autogen_core.CancellationToken") 可用于在调用 `cancellation_token.cancel()` 时异步取消请求，这将导致对 `on_messages` 调用的 `await` 引发 `CancelledError`。

阅读更多关于 [Agent Tutorial](tutorial/agents.html) 和 [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 的信息。

## Multi-Modal Agent#

如果模型客户端支持，`v0.4` 中的 [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 支持多模态输入。模型客户端的 `vision` 能力用于确定代理是否支持多模态输入。
    
    
    import asyncio
    from pathlib import Path
    from autogen_agentchat.messages import MultiModalMessage
    from autogen_agentchat.agents import AssistantAgent
    from autogen_core import CancellationToken, Image
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
    
        assistant = AssistantAgent(
            name="assistant",
            system_message="You are a helpful assistant.",
            model_client=model_client,
        )
    
        cancellation_token = CancellationToken()
        message = MultiModalMessage(
            content=["Here is an image:", Image.from_file(Path("test.png"))],
            source="user",
        )
        response = await assistant.on_messages([message], cancellation_token)
        print(response)
    
        await model_client.close()
    
    asyncio.run(main())
    

## User Proxy#

在 `v0.2` 中，你可以按如下方式创建用户代理：
    
    
    from autogen.agentchat import UserProxyAgent
    
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config=False,
        llm_config=False,
    )
    

该用户代理将通过控制台从用户那里获取输入，并在传入消息以"TERMINATE"结尾时终止。

在 `v0.4` 中，用户代理只是一个仅接受用户输入的代理，不需要其他特殊配置。你可以按如下方式创建用户代理：
    
    
    from autogen_agentchat.agents import UserProxyAgent
    
    user_proxy = UserProxyAgent("user_proxy")
    

请参阅 [`UserProxyAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.UserProxyAgent "autogen_agentchat.agents.UserProxyAgent") 了解更多详细信息以及如何使用超时自定义输入函数。

## RAG Agent#

在 `v0.2` 中，有可教代理的概念以及可以接受数据库配置的 RAG 代理。
    
    
    teachable_agent = ConversableAgent(
        name="teachable_agent",
        llm_config=llm_config
    )
    
    # Instantiate a Teachability object. Its parameters are all optional.
    teachability = Teachability(
        reset_db=False,
        path_to_db_dir="./tmp/interactive/teachability_db"
    )
    
    teachability.add_to_agent(teachable_agent)
    

在 `v0.4` 中，你可以使用 [`Memory`](../../reference/python/autogen_core.memory.html#autogen_core.memory.Memory "autogen_core.memory.Memory") 类来实现 RAG 代理。具体来说，你可以定义一个内存存储类，并将其作为参数传递给助手代理。有关更多详细信息，请参阅 [Memory](memory.html) 教程。

这种清晰的关注点分离允许你实现使用任何数据库或存储系统的内存存储（你必须从 `Memory` 类继承）并将其与助手代理一起使用。下面的示例显示了如何将 ChromaDB 向量内存存储与助手代理一起使用。此外，你的应用程序逻辑应确定如何以及何时向内存存储添加内容。例如，你可以选择为助手代理的每个响应调用 `memory.add`，或使用单独的 LLM 调用来确定是否应将内容添加到内存存储中。
    
    
    # ...
    # example of a ChromaDBVectorMemory class
    chroma_user_memory = ChromaDBVectorMemory(
        config=PersistentChromaDBVectorMemoryConfig(
            collection_name="preferences",
            persistence_path=os.path.join(str(Path.home()), ".chromadb_autogen"),
            k=2,  # Return top  k results
            score_threshold=0.4,  # Minimum similarity score
        )
    )
    
    # you can add logic such as a document indexer that adds content to the memory store
    
    assistant_agent = AssistantAgent(
        name="assistant_agent",
        model_client=OpenAIChatCompletionClient(
            model="gpt-4o",
        ),
        tools=[get_weather],
        memory=[chroma_user_memory],
    )
    

## Conversable Agent and Register Reply#

在 `v0.2` 中，你可以创建可对话代理并按如下方式注册回复函数：
    
    
    from typing import Any, Dict, List, Optional, Tuple, Union
    from autogen.agentchat import ConversableAgent
    
    llm_config = {
        "config_list": [{"model": "gpt-4o", "api_key": "sk-xxx"}],
        "seed": 42,
        "temperature": 0,
    }
    
    conversable_agent = ConversableAgent(
        name="conversable_agent",
        system_message="You are a helpful assistant.",
        llm_config=llm_config,
        code_execution_config={"work_dir": "coding"},
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
    )
    
    def reply_func(
        recipient: ConversableAgent,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        # Custom reply logic here
        return True, "Custom reply"
    
    # Register the reply function
    conversable_agent.register_reply([ConversableAgent], reply_func, position=0)
    
    # NOTE: An async reply function will only be invoked with async send.
    

在 `v0.4` 中，我们不是猜测 `reply_func` 的作用、其所有参数以及 `position` 应该是什么，而是可以简单地创建一个自定义代理并实现 `on_messages`、`on_reset` 和 `produced_message_types` 方法。
    
    
    from typing import Sequence
    from autogen_core import CancellationToken
    from autogen_agentchat.agents import BaseChatAgent
    from autogen_agentchat.messages import TextMessage, BaseChatMessage
    from autogen_agentchat.base import Response
    
    class CustomAgent(BaseChatAgent):
        async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
            return Response(chat_message=TextMessage(content="Custom reply", source=self.name))
    
        async def on_reset(self, cancellation_token: CancellationToken) -> None:
            pass
    
        @property
        def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
            return (TextMessage,)
    

然后，你可以像使用 [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 一样使用自定义代理。有关更多详细信息，请参阅 [Custom Agent Tutorial](custom-agents.html)。

## Save and Load Agent State#

在 `v0.2` 中，没有内置的方法来保存和加载代理的状态：你需要通过导出 `ConversableAgent` 的 `chat_messages` 属性并通过 `chat_messages` 参数将其导入回来来自行实现。

在 `v0.4` 中，你可以在代理上调用 `save_state` 和 `load_state` 方法来保存和加载其状态。
    
    
    import asyncio
    import json
    from autogen_agentchat.messages import TextMessage
    from autogen_agentchat.agents import AssistantAgent
    from autogen_core import CancellationToken
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
    
        assistant = AssistantAgent(
            name="assistant",
            system_message="You are a helpful assistant.",
            model_client=model_client,
        )
    
        cancellation_token = CancellationToken()
        response = await assistant.on_messages([TextMessage(content="Hello!", source="user")], cancellation_token)
        print(response)
    
        # Save the state.
        state = await assistant.save_state()
    
        # (Optional) Write state to disk.
        with open("assistant_state.json", "w") as f:
            json.dump(state, f)
    
        # (Optional) Load it back from disk.
        with open("assistant_state.json", "r") as f:
            state = json.load(f)
            print(state) # Inspect the state, which contains the chat history.
    
        # Carry on the chat.
        response = await assistant.on_messages([TextMessage(content="Tell me a joke.", source="user")], cancellation_token)
        print(response)
    
        # Load the state, resulting the agent to revert to the previous state before the last message.
        await assistant.load_state(state)
    
        # Carry on the same chat again.
        response = await assistant.on_messages([TextMessage(content="Tell me a joke.", source="user")], cancellation_token)
        # Close the connection to the model client.
        await model_client.close()
    
    asyncio.run(main())
    

你还可以在任何团队上调用 `save_state` 和 `load_state`，例如 [`RoundRobinGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat")，以保存和加载整个团队的状态。

## Two-Agent Chat#

在 `v0.2` 中，你可以按如下方式创建用于代码执行的双代理聊天：
    
    
    from autogen.coding import LocalCommandLineCodeExecutor
    from autogen.agentchat import AssistantAgent, UserProxyAgent
    
    llm_config = {
        "config_list": [{"model": "gpt-4o", "api_key": "sk-xxx"}],
        "seed": 42,
        "temperature": 0,
    }
    
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant. Write all code in python. Reply only 'TERMINATE' if the task is done.",
        llm_config=llm_config,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    )
    
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config={"code_executor": LocalCommandLineCodeExecutor(work_dir="coding")},
        llm_config=False,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    )
    
    chat_result = user_proxy.initiate_chat(assistant, message="Write a python script to print 'Hello, world!'")
    # Intermediate messages are printed to the console directly.
    print(chat_result)
    

要在 `v0.4` 中获得相同的行为，你可以将 [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 和 [`CodeExecutorAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.CodeExecutorAgent "autogen_agentchat.agents.CodeExecutorAgent") 一起用在 [`RoundRobinGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 中。
    
    
    import asyncio
    from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
    from autogen_agentchat.ui import Console
    from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
    
        assistant = AssistantAgent(
            name="assistant",
            system_message="You are a helpful assistant. Write all code in python. Reply only 'TERMINATE' if the task is done.",
            model_client=model_client,
        )
    
        code_executor = CodeExecutorAgent(
            name="code_executor",
            code_executor=LocalCommandLineCodeExecutor(work_dir="coding"),
        )
    
        # The termination condition is a combination of text termination and max message termination, either of which will cause the chat to terminate.
        termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)
    
        # The group chat will alternate between the assistant and the code executor.
        group_chat = RoundRobinGroupChat([assistant, code_executor], termination_condition=termination)
    
        # `run_stream` returns an async generator to stream the intermediate messages.
        stream = group_chat.run_stream(task="Write a python script to print 'Hello, world!'")
        # `Console` is a simple UI to display the stream.
        await Console(stream)
        
        # Close the connection to the model client.
        await model_client.close()
    
    asyncio.run(main())
    

## Tool Use#

在 `v0.2` 中，要创建使用工具的聊天机器人，你必须有两个代理，一个用于调用工具，一个用于执行工具。你需要为每个用户请求启动双代理聊天。
    
    
    from autogen.agentchat import AssistantAgent, UserProxyAgent, register_function
    
    llm_config = {
        "config_list": [{"model": "gpt-4o", "api_key": "sk-xxx"}],
        "seed": 42,
        "temperature": 0,
    }
    
    tool_caller = AssistantAgent(
        name="tool_caller",
        system_message="You are a helpful assistant. You can call tools to help user.",
        llm_config=llm_config,
        max_consecutive_auto_reply=1, # Set to 1 so that we return to the application after each assistant reply as we are building a chatbot.
    )
    
    tool_executor = UserProxyAgent(
        name="tool_executor",
        human_input_mode="NEVER",
        code_execution_config=False,
        llm_config=False,
    )
    
    def get_weather(city: str) -> str:
        return f"The weather in {city} is 72 degree and sunny."
    
    # Register the tool function to the tool caller and executor.
    register_function(get_weather, caller=tool_caller, executor=tool_executor)
    
    while True:
        user_input = input("User: ")
        if user_input == "exit":
            break
        chat_result = tool_executor.initiate_chat(
            tool_caller,
            message=user_input,
            summary_method="reflection_with_llm", # To let the model reflect on the tool use, set to "last_msg" to return the tool call result directly.
        )
        print("Assistant:", chat_result.summary)
    

在 `v0.4` 中，你实际上只需要一个代理 —— [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") —— 来处理工具调用和工具执行。
    
    
    import asyncio
    from autogen_core import CancellationToken
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.messages import TextMessage
    
    def get_weather(city: str) -> str: # Async tool is possible too.
        return f"The weather in {city} is 72 degree and sunny."
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
        assistant = AssistantAgent(
            name="assistant",
            system_message="You are a helpful assistant. You can call tools to help user.",
            model_client=model_client,
            tools=[get_weather],
            reflect_on_tool_use=True, # Set to True to have the model reflect on the tool use, set to False to return the tool call result directly.
        )
        while True:
            user_input = input("User: ")
            if user_input == "exit":
                break
            response = await assistant.on_messages([TextMessage(content=user_input, source="user")], CancellationToken())
            print("Assistant:", response.chat_message.to_text())
        await model_client.close()
    
    asyncio.run(main())
    

在诸如 [`RoundRobinGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 之类的群聊中使用配备工具的代理时，你只需按上述方式向代理添加工具，然后创建一个包含这些代理的群聊。

## Chat Result#

在 `v0.2` 中，你从 `initiate_chat` 方法获取 `ChatResult` 对象。例如：
    
    
    chat_result = tool_executor.initiate_chat(
        tool_caller,
        message=user_input,
        summary_method="reflection_with_llm",
    )
    print(chat_result.summary) # Get LLM-reflected summary of the chat.
    print(chat_result.chat_history) # Get the chat history.
    print(chat_result.cost) # Get the cost of the chat.
    print(chat_result.human_input) # Get the human input solicited by the chat.
    

有关更多详细信息，请参阅 [ChatResult Docs](https://microsoft.github.io/autogen/0.2/docs/reference/agentchat/chat#chatresult)。

在 `v0.4` 中，你从 `run` 或 `run_stream` 方法获取 [`TaskResult`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult") 对象。[`TaskResult`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult") 对象包含 `messages`，它是聊天的消息历史记录，包括代理的私有（工具调用等）和公共消息。

[`TaskResult`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult") 和 `ChatResult` 之间存在一些显著差异：

  * [`TaskResult`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult") 中的 `messages` 列表使用与 `ChatResult.chat_history` 列表不同的消息格式。

  * 没有 `summary` 字段。由应用程序决定如何使用 `messages` 列表对聊天进行总结。

  * `human_input` 不在 [`TaskResult`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult") 对象中提供，因为可以通过使用 `source` 字段过滤从 `messages` 列表中提取用户输入。

  * `cost` 不在 [`TaskResult`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult "autogen_agentchat.base.TaskResult") 对象中提供，但是，你可以根据 token 使用情况计算成本。这将是一个很好的社区扩展以添加成本计算。请参阅 [community extensions](../extensions-user-guide/discover.html)。

## Conversion between v0.2 and v0.4 Messages#

你可以使用以下转换函数在 v0.4 消息（位于 [`autogen_agentchat.base.TaskResult.messages`](../../reference/python/autogen_agentchat.base.html#autogen_agentchat.base.TaskResult.messages "autogen_agentchat.base.TaskResult.messages") 中）和 v0.2 消息（位于 `ChatResult.chat_history` 中）之间进行转换。
    
    
    from typing import Any, Dict, List, Literal
    
    from autogen_agentchat.messages import (
        BaseAgentEvent,
        BaseChatMessage,
        HandoffMessage,
        MultiModalMessage,
        StopMessage,
        TextMessage,
        ToolCallExecutionEvent,
        ToolCallRequestEvent,
        ToolCallSummaryMessage,
    )
    from autogen_core import FunctionCall, Image
    from autogen_core.models import FunctionExecutionResult
    
    
    def convert_to_v02_message(
        message: BaseAgentEvent | BaseChatMessage,
        role: Literal["assistant", "user", "tool"],
        image_detail: Literal["auto", "high", "low"] = "auto",
    ) -> Dict[str, Any]:
        """Convert a v0.4 AgentChat message to a v0.2 message.
    
        Args:
            message (BaseAgentEvent | BaseChatMessage): The message to convert.
            role (Literal["assistant", "user", "tool"]): The role of the message.
            image_detail (Literal["auto", "high", "low"], optional): The detail level of image content in multi-modal message. Defaults to "auto".
    
        Returns:
            Dict[str, Any]: The converted AutoGen v0.2 message.
        """
        v02_message: Dict[str, Any] = {}
        if isinstance(message, TextMessage | StopMessage | HandoffMessage | ToolCallSummaryMessage):
            v02_message = {"content": message.content, "role": role, "name": message.source}
        elif isinstance(message, MultiModalMessage):
            v02_message = {"content": [], "role": role, "name": message.source}
            for modal in message.content:
                if isinstance(modal, str):
                    v02_message["content"].append({"type": "text", "text": modal})
                elif isinstance(modal, Image):
                    v02_message["content"].append(modal.to_openai_format(detail=image_detail))
                else:
                    raise ValueError(f"Invalid multimodal message content: {modal}")
        elif isinstance(message, ToolCallRequestEvent):
            v02_message = {"tool_calls": [], "role": "assistant", "content": None, "name": message.source}
            for tool_call in message.content:
                v02_message["tool_calls"].append(
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {"name": tool_call.name, "args": tool_call.arguments},
                    }
                )
        elif isinstance(message, ToolCallExecutionEvent):
            tool_responses: List[Dict[str, str]] = []
            for tool_result in message.content:
                tool_responses.append(
                    {
                        "tool_call_id": tool_result.call_id,
                        "role": "tool",
                        "content": tool_result.content,
                    }
                )
            content = "\n\n".join([response["content"] for response in tool_responses])
            v02_message = {"tool_responses": tool_responses, "role": "tool", "content": content}
        else:
            raise ValueError(f"Invalid message type: {type(message)}")
        return v02_message
    
    
    def convert_to_v04_message(message: Dict[str, Any]) -> BaseAgentEvent | BaseChatMessage:
        """Convert a v0.2 message to a v0.4 AgentChat message."""
        if "tool_calls" in message:
            tool_calls: List[FunctionCall] = []
            for tool_call in message["tool_calls"]:
                tool_calls.append(
                    FunctionCall(
                        id=tool_call["id"],
                        name=tool_call["function"]["name"],
                        arguments=tool_call["function"]["args"],
                    )
                )
            return ToolCallRequestEvent(source=message["name"], content=tool_calls)
        elif "tool_responses" in message:
            tool_results: List[FunctionExecutionResult] = []
            for tool_response in message["tool_responses"]:
                tool_results.append(
                    FunctionExecutionResult(
                        call_id=tool_response["tool_call_id"],
                        content=tool_response["content"],
                        is_error=False,
                        name=tool_response["name"],
                    )
                )
            return ToolCallExecutionEvent(source="tools", content=tool_results)
        elif isinstance(message["content"], list):
            content: List[str | Image] = []
            for modal in message["content"]:  # type: ignore
                if modal["type"] == "text":  # type: ignore
                    content.append(modal["text"])  # type: ignore
                else:
                    content.append(Image.from_uri(modal["image_url"]["url"]))  # type: ignore
            return MultiModalMessage(content=content, source=message["name"])
        elif isinstance(message["content"], str):
            return TextMessage(content=message["content"], source=message["name"])
        else:
            raise ValueError(f"Unable to convert message: {message}")
    

## Group Chat#

在 `v0.2` 中，你需要创建一个 `GroupChat` 类并将其传递给 `GroupChatManager`，并有一个作为用户代理的参与者来发起聊天。对于 writer 和 critic 的简单场景，你可以执行以下操作：
    
    
    from autogen.agentchat import AssistantAgent, GroupChat, GroupChatManager
    
    llm_config = {
        "config_list": [{"model": "gpt-4o", "api_key": "sk-xxx"}],
        "seed": 42,
        "temperature": 0,
    }
    
    writer = AssistantAgent(
        name="writer",
        description="A writer.",
        system_message="You are a writer.",
        llm_config=llm_config,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("APPROVE"),
    )
    
    critic = AssistantAgent(
        name="critic",
        description="A critic.",
        system_message="You are a critic, provide feedback on the writing. Reply only 'APPROVE' if the task is done.",
        llm_config=llm_config,
    )
    
    # Create a group chat with the writer and critic.
    groupchat = GroupChat(agents=[writer, critic], messages=[], max_round=12)
    
    # Create a group chat manager to manage the group chat, use round-robin selection method.
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config, speaker_selection_method="round_robin")
    
    # Initiate the chat with the editor, intermediate messages are printed to the console directly.
    result = editor.initiate_chat(
        manager,
        message="Write a short story about a robot that discovers it has feelings.",
    )
    print(result.summary)
    

在 `v0.4` 中，你可以使用 [`RoundRobinGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.RoundRobinGroupChat "autogen_agentchat.teams.RoundRobinGroupChat") 来实现相同的行为。
    
    
    import asyncio
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
    
        writer = AssistantAgent(
            name="writer",
            description="A writer.",
            system_message="You are a writer.",
            model_client=model_client,
        )
    
        critic = AssistantAgent(
            name="critic",
            description="A critic.",
            system_message="You are a critic, provide feedback on the writing. Reply only 'APPROVE' if the task is done.",
            model_client=model_client,
        )
    
        # The termination condition is a text termination, which will cause the chat to terminate when the text "APPROVE" is received.
        termination = TextMentionTermination("APPROVE")
    
        # The group chat will alternate between the writer and the critic.
        group_chat = RoundRobinGroupChat([writer, critic], termination_condition=termination, max_turns=12)
    
        # `run_stream` returns an async generator to stream the intermediate messages.
        stream = group_chat.run_stream(task="Write a short story about a robot that discovers it has feelings.")
        # `Console` is a simple UI to display the stream.
        await Console(stream)
        # Close the connection to the model client.
        await model_client.close()
    
    asyncio.run(main())
    

对于基于 LLM 的发言者选择，你可以改用 [`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat")。有关更多详细信息，请参阅 [Selector Group Chat Tutorial](selector-group-chat.html) 和 [`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat")。

> **Note** ：在 `v0.4` 中，你无需在用户代理上注册函数即可在群聊中使用工具。如 Tool Use 部分所示，你可以简单地将工具函数传递给 [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent")。代理将在需要时自动调用工具。如果你的工具没有输出格式良好的响应，可以使用 `reflect_on_tool_use` 参数让模型反思工具使用情况。

## Group Chat with Resume#

在 `v0.2` 中，带恢复的群聊有点复杂。你需要显式保存群聊消息并在想要恢复聊天时将它们加载回来。有关更多详细信息，请参阅 [Resuming Group Chat in v0.2](https://microsoft.github.io/autogen/0.2/docs/topics/groupchat/resuming_groupchat)。

在 `v0.4` 中，你只需使用相同的群聊对象再次调用 `run` 或 `run_stream` 即可恢复聊天。要导出和加载状态，你可以使用 `save_state` 和 `load_state` 方法。
    
    
    import asyncio
    import json
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    def create_team(model_client : OpenAIChatCompletionClient) -> RoundRobinGroupChat:
        writer = AssistantAgent(
            name="writer",
            description="A writer.",
            system_message="You are a writer.",
            model_client=model_client,
        )
    
        critic = AssistantAgent(
            name="critic",
            description="A critic.",
            system_message="You are a critic, provide feedback on the writing. Reply only 'APPROVE' if the task is done.",
            model_client=model_client,
        )
    
        # The termination condition is a text termination, which will cause the chat to terminate when the text "APPROVE" is received.
        termination = TextMentionTermination("APPROVE")
    
        # The group chat will alternate between the writer and the critic.
        group_chat = RoundRobinGroupChat([writer, critic], termination_condition=termination)
    
        return group_chat
    
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
        # Create team.
        group_chat = create_team(model_client)
    
        # `run_stream` returns an async generator to stream the intermediate messages.
        stream = group_chat.run_stream(task="Write a short story about a robot that discovers it has feelings.")
        # `Console` is a simple UI to display the stream.
        await Console(stream)
    
        # Save the state of the group chat and all participants.
        state = await group_chat.save_state()
        with open("group_chat_state.json", "w") as f:
            json.dump(state, f)
    
        # Create a new team with the same participants configuration.
        group_chat = create_team(model_client)
    
        # Load the state of the group chat and all participants.
        with open("group_chat_state.json", "r") as f:
            state = json.load(f)
        await group_chat.load_state(state)
    
        # Resume the chat.
        stream = group_chat.run_stream(task="Translate the story into Chinese.")
        await Console(stream)
    
        # Close the connection to the model client.
        await model_client.close()
    
    asyncio.run(main())
    

## Save and Load Group Chat State#

在 `v0.2` 中，你需要显式保存群聊消息并在想要恢复聊天时将它们加载回来。

在 `v0.4` 中，你只需在群聊对象上调用 `save_state` 和 `load_state` 方法即可。请参阅 Group Chat with Resume 获取示例。

## Group Chat with Tool Use#

在 `v0.2` 群聊中，当涉及工具时，你需要在用户代理上注册工具函数，并将用户代理包含在群聊中。其他代理发出的工具调用将被路由到用户代理以执行。

我们已经观察到这种方法存在许多问题，例如工具调用路由未按预期工作，以及工具调用请求和结果无法被不支持函数调用的模型接受。

在 `v0.4` 中，无需在用户代理上注册工具函数，因为工具直接在 [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 中执行，它会将工具的响应发布到群聊中。因此，群聊管理器无需参与路由工具调用。

有关在群聊中使用工具的示例，请参阅 [Selector Group Chat Tutorial](selector-group-chat.html)。

## Group Chat with Custom Selector (Stateflow)#

在 `v0.2` 群聊中，当 `speaker_selection_method` 设置为自定义函数时，它可以覆盖默认的选择方法。这对于实现基于状态的选择方法很有用。有关更多详细信息，请参阅 [Custom Speaker Selection in v0.2](https://microsoft.github.io/autogen/0.2/docs/topics/groupchat/customized_speaker_selection)。

在 `v0.4` 中，你可以使用带有 `selector_func` 的 [`SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 来实现相同的行为。`selector_func` 是一个函数，它接受群聊的当前消息线程并返回下一个发言者的名称。如果返回 `None`，将使用基于 LLM 的选择方法。

以下是使用基于状态的选择方法实现 web 搜索/分析场景的示例。
    
    
    import asyncio
    from typing import Sequence
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
    from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
    from autogen_agentchat.teams import SelectorGroupChat
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    # Note: This example uses mock tools instead of real APIs for demonstration purposes
    def search_web_tool(query: str) -> str:
        if "2006-2007" in query:
            return """Here are the total points scored by Miami Heat players in the 2006-2007 season:
            Udonis Haslem: 844 points
            Dwayne Wade: 1397 points
            James Posey: 550 points
            ...
            """
        elif "2007-2008" in query:
            return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214."
        elif "2008-2009" in query:
            return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398."
        return "No data found."
    
    
    def percentage_change_tool(start: float, end: float) -> float:
        return ((end - start) / start) * 100
    
    def create_team(model_client : OpenAIChatCompletionClient) -> SelectorGroupChat:
        planning_agent = AssistantAgent(
            "PlanningAgent",
            description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
            model_client=model_client,
            system_message="""
            You are a planning agent.
            Your job is to break down complex tasks into smaller, manageable subtasks.
            Your team members are:
                Web search agent: Searches for information
                Data analyst: Performs calculations
    
            You only plan and delegate tasks - you do not execute them yourself.
    
            When assigning tasks, use this format:
            1. <agent> : <task>
    
            After all tasks are complete, summarize the findings and end with "TERMINATE".
            """,
        )
    
        web_search_agent = AssistantAgent(
            "WebSearchAgent",
            description="A web search agent.",
            tools=[search_web_tool],
            model_client=model_client,
            system_message="""
            You are a web search agent.
            Your only tool is search_tool - use it to find information.
            You make only one search call at a time.
            Once you have the results, you never do calculations based on them.
            """,
        )
    
        data_analyst_agent = AssistantAgent(
            "DataAnalystAgent",
            description="A data analyst agent. Useful for performing calculations.",
            model_client=model_client,
            tools=[percentage_change_tool],
            system_message="""
            You are a data analyst.
            Given the tasks you have been assigned, you should analyze the data and provide results using the tools provided.
            """,
        )
    
        # The termination condition is a combination of text mention termination and max message termination.
        text_mention_termination = TextMentionTermination("TERMINATE")
        max_messages_termination = MaxMessageTermination(max_messages=25)
        termination = text_mention_termination | max_messages_termination
    
        # The selector function is a function that takes the current message thread of the group chat
        # and returns the next speaker's name. If None is returned, the LLM-based selection method will be used.
        def selector_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
            if messages[-1].source != planning_agent.name:
                return planning_agent.name # Always return to the planning agent after the other agents have spoken.
            return None
    
        team = SelectorGroupChat(
            [planning_agent, web_search_agent, data_analyst_agent],
            model_client=OpenAIChatCompletionClient(model="gpt-4o-mini"), # Use a smaller model for the selector.
            termination_condition=termination,
            selector_func=selector_func,
        )
        return team
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o")
        team = create_team(model_client)
        task = "Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?"
        await Console(team.run_stream(task=task))
    
    asyncio.run(main())
    

## Nested Chat#

Nested chat 允许你在代理内嵌套整个团队或另一个代理。这对于创建代理的层次结构或"信息孤岛"很有用，因为嵌套代理无法直接与同一组之外的代理通信。

在 `v0.2` 中，通过使用 `ConversableAgent` 类上的 `register_nested_chats` 方法支持嵌套聊天。你需要使用字典指定嵌套的代理序列。有关更多详细信息，请参阅 [Nested Chat in v0.2](https://microsoft.github.io/autogen/0.2/docs/tutorial/conversation-patterns#nested-chats)。

在 `v0.4` 中，嵌套聊天是自定义代理的实现细节。你可以创建一个自定义代理，该代理将团队或另一个代理作为参数，并实现 `on_messages` 方法以触发嵌套团队或代理。由应用程序决定如何传递或转换来自和发往嵌套团队或代理的消息。

以下示例显示了一个计算数字的简单嵌套聊天。
    
    
    import asyncio
    from typing import Sequence
    from autogen_core import CancellationToken
    from autogen_agentchat.agents import BaseChatAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.messages import TextMessage, BaseChatMessage
    from autogen_agentchat.base import Response
    
    class CountingAgent(BaseChatAgent):
        """An agent that returns a new number by adding 1 to the last number in the input messages."""
        async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
            if len(messages) == 0:
                last_number = 0 # Start from 0 if no messages are given.
            else:
                assert isinstance(messages[-1], TextMessage)
                last_number = int(messages[-1].content) # Otherwise, start from the last number.
            return Response(chat_message=TextMessage(content=str(last_number + 1), source=self.name))
    
        async def on_reset(self, cancellation_token: CancellationToken) -> None:
            pass
    
        @property
        def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
            return (TextMessage,)
    
    class NestedCountingAgent(BaseChatAgent):
        """An agent that increments the last number in the input messages
        multiple times using a nested counting team."""
        def __init__(self, name: str, counting_team: RoundRobinGroupChat) -> None:
            super().__init__(name, description="An agent that counts numbers.")
            self._counting_team = counting_team
    
        async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
            # Run the inner team with the given messages and returns the last message produced by the team.
            result = await self._counting_team.run(task=messages, cancellation_token=cancellation_token)
            # To stream the inner messages, implement `on_messages_stream` and use that to implement `on_messages`.
            assert isinstance(result.messages[-1], TextMessage)
            return Response(chat_message=result.messages[-1], inner_messages=result.messages[len(messages):-1])
    
        async def on_reset(self, cancellation_token: CancellationToken) -> None:
            # Reset the inner team.
            await self._counting_team.reset()
    
        @property
        def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
            return (TextMessage,)
    
    async def main() -> None:
        # Create a team of two counting agents as the inner team.
        counting_agent_1 = CountingAgent("counting_agent_1", description="An agent that counts numbers.")
        counting_agent_2 = CountingAgent("counting_agent_2", description="An agent that counts numbers.")
        counting_team = RoundRobinGroupChat([counting_agent_1, counting_agent_2], max_turns=5)
        # Create a nested counting agent that takes the inner team as a parameter.
        nested_counting_agent = NestedCountingAgent("nested_counting_agent", counting_team)
        # Run the nested counting agent with a message starting from 1.
        response = await nested_counting_agent.on_messages([TextMessage(content="1", source="user")], CancellationToken())
        assert response.inner_messages is not None
        for message in response.inner_messages:
            print(message)
        print(response.chat_message)
    
    asyncio.run(main())
    

你应该看到以下输出：
    
    
    source='counting_agent_1' models_usage=None content='2' type='TextMessage'
    source='counting_agent_2' models_usage=None content='3' type='TextMessage'
    source='counting_agent_1' models_usage=None content='4' type='TextMessage'
    source='counting_agent_2' models_usage=None content='5' type='TextMessage'
    source='counting_agent_1' models_usage=None content='6' type='TextMessage'
    

你可以查看 [`SocietyOfMindAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.SocietyOfMindAgent "autogen_agentchat.agents.SocietyOfMindAgent") 以获取更复杂的实现。

## Sequential Chat#

在 `v0.2` 中，通过使用 `initiate_chats` 函数支持顺序聊天。它接受输入序列中每个步骤的字典配置列表。有关更多详细信息，请参阅 [Sequential Chat in v0.2](https://microsoft.github.io/autogen/0.2/docs/tutorial/conversation-patterns#sequential-chats)。

根据社区的反馈，`initiate_chats` 函数过于固执己见，不够灵活，无法支持用户想要实现的各种场景。我们经常发现用户难以让 `initiate_chats` 函数工作，但他们可以使用基本的 Python 代码轻松地将步骤粘合在一起。因此，在 `v0.4` 中，我们不在 AgentChat API 中提供用于顺序聊天的内置函数。

相反，你可以使用 Core API 创建事件驱动的顺序工作流，并使用 AgentChat API 提供的其他组件来实现工作流的每个步骤。有关顺序工作流的示例，请参阅 [Core API Tutorial](../core-user-guide/design-patterns/sequential-workflow.html)。

我们认识到工作流的概念是许多应用程序的核心，我们将在未来为工作流提供更多内置支持。

## GPTAssistantAgent#

在 `v0.2` 中，`GPTAssistantAgent` 是一个由 OpenAI Assistant API 支持的特殊代理类。

在 `v0.4` 中，相应的是 [`OpenAIAssistantAgent`](../../reference/python/autogen_ext.agents.openai.html#autogen_ext.agents.openai.OpenAIAssistantAgent "autogen_ext.agents.openai.OpenAIAssistantAgent") 类。它支持与 `v0.2` 中 `GPTAssistantAgent` 相同的功能集，并具有更多功能，例如可自定义的线程和文件上传。有关更多详细信息，请参阅 [`OpenAIAssistantAgent`](../../reference/python/autogen_ext.agents.openai.html#autogen_ext.agents.openai.OpenAIAssistantAgent "autogen_ext.agents.openai.OpenAIAssistantAgent")。

## Long Context Handling#

在 `v0.2` 中，可以通过使用在 `ConversableAgent` 构造后添加给它的 `transforms` 功能来处理溢出模型上下文窗口的长上下文。

社区的反馈使我们相信此功能是必需的，应该是 [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 的内置组件，并且可用于每个自定义代理。

在 `v0.4` 中，我们引入了 [`ChatCompletionContext`](../../reference/python/autogen_core.model_context.html#autogen_core.model_context.ChatCompletionContext "autogen_core.model_context.ChatCompletionContext") 基类，它管理消息历史记录并提供历史记录的虚拟视图。应用程序可以使用内置实现，例如 [`BufferedChatCompletionContext`](../../reference/python/autogen_core.model_context.html#autogen_core.model_context.BufferedChatCompletionContext "autogen_core.model_context.BufferedChatCompletionContext") 来限制发送给模型的消息历史记录，或提供自己的实现来创建不同的虚拟视图。

要在聊天机器人场景中的 [`AssistantAgent`](../../reference/python/autogen_agentchat.agents.html#autogen_agentchat.agents.AssistantAgent "autogen_agentchat.agents.AssistantAgent") 中使用 [`BufferedChatCompletionContext`](../../reference/python/autogen_core.model_context.html#autogen_core.model_context.BufferedChatCompletionContext "autogen_core.model_context.BufferedChatCompletionContext")。
    
    
    import asyncio
    from autogen_agentchat.messages import TextMessage
    from autogen_agentchat.agents import AssistantAgent
    from autogen_core import CancellationToken
    from autogen_core.model_context import BufferedChatCompletionContext
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
    
        assistant = AssistantAgent(
            name="assistant",
            system_message="You are a helpful assistant.",
            model_client=model_client,
            model_context=BufferedChatCompletionContext(buffer_size=10), # Model can only view the last 10 messages.
        )
        while True:
            user_input = input("User: ")
            if user_input == "exit":
                break
            response = await assistant.on_messages([TextMessage(content=user_input, source="user")], CancellationToken())
            print("Assistant:", response.chat_message.to_text())
        
        await model_client.close()
    
    asyncio.run(main())
    

在此示例中，聊天机器人只能读取历史记录中的最后 10 条消息。

## Observability and Control#

在 `v0.4` AgentChat 中，你可以通过使用 `on_messages_stream` 方法观察代理，该方法返回异步生成器以流式传输代理的内部想法和操作。对于团队，你可以使用 `run_stream` 方法流式传输团队中代理之间的内部对话。你的应用程序可以使用这些流实时观察代理和团队。

`on_messages_stream` 和 `run_stream` 方法都将 [`CancellationToken`](../../reference/python/autogen_core.html#autogen_core.CancellationToken "autogen_core.CancellationToken") 作为参数，可用于异步取消输出流并停止代理或团队。对于团队，你还可以使用终止条件在满足特定条件时停止团队。有关更多详细信息，请参阅 [Termination Condition Tutorial](tutorial/termination.html)。

与附带特殊日志记录模块的 `v0.2` 不同，`v0.4` API 仅使用 Python 的 `logging` 模块来记录诸如模型客户端调用之类的事件。有关更多详细信息，请参阅 Core API 文档中的 [Logging](../core-user-guide/framework/logging.html)。

## Code Executors#

`v0.2` 和 `v0.4` 中的代码执行器几乎相同，只是 `v0.4` 执行器支持异步 API。你还可以使用 [`CancellationToken`](../../reference/python/autogen_core.html#autogen_core.CancellationToken "autogen_core.CancellationToken") 来取消执行时间过长的代码执行。请参阅 Core API 文档中的 [Command Line Code Executors Tutorial](../core-user-guide/components/command-line-code-executors.html)。

我们还添加了 `ACADynamicSessionsCodeExecutor`，它可以使用 Azure Container Apps (ACA) dynamic sessions 进行代码执行。请参阅 [ACA Dynamic Sessions Code Executor Docs](../extensions-user-guide/azure-container-code-executor.html)。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/migration-guide.md)

[ __Show Source](../../_sources/user-guide/agentchat-user-guide/migration-guide.md.txt)