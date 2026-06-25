<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/models.html -->

# 模型#

在许多情况下，代理需要访问 LLM 模型服务，如 OpenAI、Azure OpenAI 或本地模型。由于有许多不同的提供商和不同的 API，`autogen-core` 为模型客户端实现了协议，`autogen-ext` 为流行的模型服务实现了一组模型客户端。AgentChat 可以使用这些模型客户端与模型服务交互。

本节提供可用模型客户端的快速概述。有关如何直接使用它们的更多详细信息，请参阅核心 API 文档中的 [模型客户端](../../core-user-guide/components/model-clients.html)。

注意

请参阅 [`ChatCompletionCache`](../../../reference/python/autogen_ext.models.cache.html#autogen_ext.models.cache.ChatCompletionCache "autogen_ext.models.cache.ChatCompletionCache") 了解可与以下客户端一起使用的缓存包装器。

## 记录模型调用#

AutoGen 使用标准 Python 日志模块记录事件，如模型调用和响应。日志器名称为 [`autogen_core.EVENT_LOGGER_NAME`](../../../reference/python/autogen_core.html#autogen_core.EVENT_LOGGER_NAME "autogen_core.EVENT_LOGGER_NAME")，事件类型为 `LLMCall`。
    
    
    import logging
    
    from autogen_core import EVENT_LOGGER_NAME
    
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    

## OpenAI#

要访问 OpenAI 模型，请安装 `openai` 扩展，它允许您使用 [`OpenAIChatCompletionClient`](../../../reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.OpenAIChatCompletionClient "autogen_ext.models.openai.OpenAIChatCompletionClient")。
    
    
    pip install "autogen-ext[openai]"
    

您还需要从 OpenAI 获取 [API 密钥](https://platform.openai.com/account/api-keys)。
    
    
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    openai_model_client = OpenAIChatCompletionClient(
        model="gpt-4o-2024-08-06",
        # api_key="sk-...", # 如果设置了 OPENAI_API_KEY 环境变量则可选。
    )
    

要测试模型客户端，您可以使用以下代码：
    
    
    from autogen_core.models import UserMessage
    
    result = await openai_model_client.create([UserMessage(content="What is the capital of France?", source="user")])
    print(result)
    await openai_model_client.close()
    
    
    
    CreateResult(finish_reason='stop', content='The capital of France is Paris.', usage=RequestUsage(prompt_tokens=15, completion_tokens=7), cached=False, logprobs=None)
    

注意

您可以将此客户端与托管在 OpenAI 兼容端点上的模型一起使用，但是，我们尚未测试此功能。有关更多信息，请参阅 [`OpenAIChatCompletionClient`](../../../reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.OpenAIChatCompletionClient "autogen_ext.models.openai.OpenAIChatCompletionClient")。

## Azure OpenAI#

同样，安装 `azure` 和 `openai` 扩展以使用 [`AzureOpenAIChatCompletionClient`](../../../reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.AzureOpenAIChatCompletionClient "autogen_ext.models.openai.AzureOpenAIChatCompletionClient")。
    
    
    pip install "autogen-ext[openai,azure]"
    

要使用此客户端，您需要提供部署 ID、Azure Cognitive Services 端点、API 版本和模型功能。对于身份验证，您可以提供 API 密钥或 Azure Active Directory (AAD) 令牌凭据。

以下代码片段演示如何使用 AAD 身份验证。使用的身份必须分配 [Cognitive Services OpenAI User](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/role-based-access-control#cognitive-services-openai-user) 角色。
    
    
    from autogen_core.models import UserMessage
    from autogen_ext.auth.azure import AzureTokenProvider
    from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
    from azure.identity import DefaultAzureCredential
    
    # 创建令牌提供者
    token_provider = AzureTokenProvider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    
    az_model_client = AzureOpenAIChatCompletionClient(
        azure_deployment="{your-azure-deployment}",
        model="{model-name, such as gpt-4o}",
        api_version="2024-06-01",
        azure_endpoint="https://{your-custom-endpoint}.openai.azure.com/",
        azure_ad_token_provider=token_provider,  # 如果选择基于密钥的身份验证则可选。
        # api_key="sk-...", # 用于基于密钥的身份验证。
    )
    
    result = await az_model_client.create([UserMessage(content="What is the capital of France?", source="user")])
    print(result)
    await az_model_client.close()
    

有关如何直接使用 Azure 客户端的更多信息，请参阅 [此处](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/managed-identity#chat-completions)。

## Azure AI Foundry#

[Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-studio/)（以前称为 Azure AI Studio）提供托管在 Azure 上的模型。要使用这些模型，请使用 [`AzureAIChatCompletionClient`](../../../reference/python/autogen_ext.models.azure.html#autogen_ext.models.azure.AzureAIChatCompletionClient "autogen_ext.models.azure.AzureAIChatCompletionClient")。

您需要安装 `azure` 扩展才能使用此客户端。
    
    
    pip install "autogen-ext[azure]"
    

以下是使用 [GitHub Marketplace](https://github.com/marketplace/models) 中 Phi-4 模型的示例。
    
    
    import os
    
    from autogen_core.models import UserMessage
    from autogen_ext.models.azure import AzureAIChatCompletionClient
    from azure.core.credentials import AzureKeyCredential
    
    client = AzureAIChatCompletionClient(
        model="Phi-4",
        endpoint="https://models.github.ai/inference",
        # 要向模型进行身份验证，您需要在 GitHub 设置中生成个人访问令牌 (PAT)。
        # 按照此处说明创建您的 PAT 令牌：https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
        credential=AzureKeyCredential(os.environ["GITHUB_TOKEN"]),
        model_info={
            "json_output": False,
            "function_calling": False,
            "vision": False,
            "family": "unknown",
            "structured_output": False,
        },
    )
    
    result = await client.create([UserMessage(content="What is the capital of France?", source="user")])
    print(result)
    await client.close()
    
    
    
    finish_reason='stop' content='The capital of France is Paris.' usage=RequestUsage(prompt_tokens=14, completion_tokens=8) cached=False logprobs=None
    

## Anthropic（实验性）#

要使用 [`AnthropicChatCompletionClient`](../../../reference/python/autogen_ext.models.anthropic.html#autogen_ext.models.anthropic.AnthropicChatCompletionClient "autogen_ext.models.anthropic.AnthropicChatCompletionClient")，您需要安装 `anthropic` 扩展。底层使用 `anthropic` Python SDK 来访问模型。您还需要从 Anthropic 获取 [API 密钥](https://console.anthropic.com)。
    
    
    # !pip install -U "autogen-ext[anthropic]"
    
    
    
    from autogen_core.models import UserMessage
    from autogen_ext.models.anthropic import AnthropicChatCompletionClient
    
    anthropic_client = AnthropicChatCompletionClient(model="claude-3-7-sonnet-20250219")
    result = await anthropic_client.create([UserMessage(content="What is the capital of France?", source="user")])
    print(result)
    await anthropic_client.close()
    
    
    
    finish_reason='stop' content="The capital of France is Paris. It's not only the political and administrative capital but also a major global center for art, fashion, gastronomy, and culture. Paris is known for landmarks such as the Eiffel Tower, the Louvre Museum, Notre-Dame Cathedral, and the Champs-Élysées." usage=RequestUsage(prompt_tokens=14, completion_tokens=73) cached=False logprobs=None thought=None
    

## Ollama（实验性）#

[Ollama](https://ollama.com/) 是一个本地模型服务器，可以在您的机器上本地运行模型。

注意

小型本地模型通常不如云端模型强大。对于某些任务，它们可能表现不佳，输出可能出人意料。

要使用 Ollama，请安装 `ollama` 扩展并使用 `OllamaChatCompletionClient`。
    
    
    pip install -U "autogen-ext[ollama]"
    
    
    
    from autogen_core.models import UserMessage
    from autogen_ext.models.ollama import OllamaChatCompletionClient
    
    # 假设您的 Ollama 服务器在本地端口 11434 上运行。
    ollama_model_client = OllamaChatCompletionClient(model="llama3.2")
    
    response = await ollama_model_client.create([UserMessage(content="What is the capital of France?", source="user")])
    print(response)
    await ollama_model_client.close()
    
    
    
    finish_reason='unknown' content='The capital of France is Paris.' usage=RequestUsage(prompt_tokens=32, completion_tokens=8) cached=False logprobs=None thought=None
    

## Gemini（实验性）#

Gemini 目前提供 [OpenAI 兼容 API（测试版）](https://ai.google.dev/gemini-api/docs/openai)。因此，您可以将 [`OpenAIChatCompletionClient`](../../../reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.OpenAIChatCompletionClient "autogen_ext.models.openai.OpenAIChatCompletionClient") 与 Gemini API 配合使用。

注意

虽然某些模型提供商可能提供 OpenAI 兼容 API，但他们仍可能存在细微差异。例如，`finish_reason` 字段在响应中可能不同。
    
    
    from autogen_core.models import UserMessage
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    model_client = OpenAIChatCompletionClient(
        model="gemini-1.5-flash-8b",
        # api_key="GEMINI_API_KEY",
    )
    
    response = await model_client.create([UserMessage(content="What is the capital of France?", source="user")])
    print(response)
    await model_client.close()
    
    
    
    finish_reason='stop' content='Paris\n' usage=RequestUsage(prompt_tokens=7, completion_tokens=2) cached=False logprobs=None thought=None
    

此外，随着 Gemini 添加新模型，您可能需要通过 model_info 字段定义模型功能。例如，要使用 `gemini-2.0-flash-lite` 或类似的新模型，您可以使用以下代码：
    
    
    from autogen_core.models import UserMessage
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_core.models import ModelInfo
    
    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash-lite",
        model_info=ModelInfo(vision=True, function_calling=True, json_output=True, family="unknown", structured_output=True)
        # api_key="GEMINI_API_KEY",
    )
    
    response = await model_client.create([UserMessage(content="What is the capital of France?", source="user")])
    print(response)
    await model_client.close()
    

## Llama API（实验性）#

[Llama API](https://llama.developer.meta.com?utm_source=partner-autogen&utm_medium=readme) 是 Meta 的第一方 API 产品。它目前提供 [OpenAI 兼容端点](https://llama.developer.meta.com/docs/features/compatibility)。因此，您可以将 [`OpenAIChatCompletionClient`](../../../reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.OpenAIChatCompletionClient "autogen_ext.models.openai.OpenAIChatCompletionClient") 与 Llama API 配合使用。

此端点完全支持以下 OpenAI 客户端库功能：

  * 聊天补全

  * 模型选择

  * 温度/采样

  * 流式传输

  * 图像理解

  * 结构化输出（JSON 模式）

  * 函数调用（工具）

    
    
    from pathlib import Path
    
    from autogen_core import Image
    from autogen_core.models import UserMessage
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    # 文本
    model_client = OpenAIChatCompletionClient(
        model="Llama-4-Scout-17B-16E-Instruct-FP8",
        # api_key="LLAMA_API_KEY"
    )
    
    response = await model_client.create([UserMessage(content="Write me a poem", source="user")])
    print(response)
    await model_client.close()
    
    # 图像
    model_client = OpenAIChatCompletionClient(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        # api_key="LLAMA_API_KEY"
    )
    image = Image.from_file(Path("test.png"))
    
    response = await model_client.create([UserMessage(content=["What is in this image", image], source="user")])
    print(response)
    await model_client.close()
    

## Semantic Kernel 适配器#

`SKChatCompletionAdapter` 允许您通过将 Semantic Kernel 模型客户端适配到所需接口来将其用作 [`ChatCompletionClient`](../../../reference/python/autogen_core.models.html#autogen_core.models.ChatCompletionClient "autogen_core.models.ChatCompletionClient")。

您需要安装相关的提供商扩展才能使用此适配器。

可安装的扩展列表：

  * `semantic-kernel-anthropic`：安装此扩展以使用 Anthropic 模型。

  * `semantic-kernel-google`：安装此扩展以使用 Google Gemini 模型。

  * `semantic-kernel-ollama`：安装此扩展以使用 Ollama 模型。

  * `semantic-kernel-mistralai`：安装此扩展以使用 MistralAI 模型。

  * `semantic-kernel-aws`：安装此扩展以使用 AWS 模型。

  * `semantic-kernel-hugging-face`：安装此扩展以使用 Hugging Face 模型。

例如，要使用 Anthropic 模型，您需要安装 `semantic-kernel-anthropic`。
    
    
    # pip install "autogen-ext[semantic-kernel-anthropic]"
    

要使用此适配器，您需要创建 Semantic Kernel 模型客户端并将其传递给适配器。

例如，要使用 Anthropic 模型：
    
    
    import os
    
    from autogen_core.models import UserMessage
    from autogen_ext.models.semantic_kernel import SKChatCompletionAdapter
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.anthropic import AnthropicChatCompletion, AnthropicChatPromptExecutionSettings
    from semantic_kernel.memory.null_memory import NullMemory
    
    sk_client = AnthropicChatCompletion(
        ai_model_id="claude-3-5-sonnet-20241022",
        api_key=os.environ["ANTHROPIC_API_KEY"],
        service_id="my-service-id",  # 可选；用于在 Semantic Kernel 中定位特定服务
    )
    settings = AnthropicChatPromptExecutionSettings(
        temperature=0.2,
    )
    
    anthropic_model_client = SKChatCompletionAdapter(
        sk_client, kernel=Kernel(memory=NullMemory()), prompt_settings=settings
    )
    
    # 直接调用模型。
    model_result = await anthropic_model_client.create(
        messages=[UserMessage(content="What is the capital of France?", source="User")]
    )
    print(model_result)
    await anthropic_model_client.close()
    
    
    
    finish_reason='stop' content='The capital of France is Paris. It is also the largest city in France and one of the most populous metropolitan areas in Europe.' usage=RequestUsage(prompt_tokens=0, completion_tokens=0) cached=False logprobs=None
    

阅读更多关于 [Semantic Kernel 适配器](../../../reference/python/autogen_ext.models.semantic_kernel.html)的信息。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/tutorial/models.ipynb)

[ __Show Source](../../../_sources/user-guide/agentchat-user-guide/tutorial/models.ipynb.txt)
