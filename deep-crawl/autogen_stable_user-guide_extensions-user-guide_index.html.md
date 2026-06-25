<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/extensions-user-guide/index.html -->

# 扩展#

AutoGen 被设计为可扩展的。`autogen-ext` 包包含由 AutoGen 项目维护的内置组件实现。

组件示例包括：

  * `autogen_ext.agents.*` 用于代理实现，如 [`MultimodalWebSurfer`](../../reference/python/autogen_ext.agents.web_surfer.html#autogen_ext.agents.web_surfer.MultimodalWebSurfer "autogen_ext.agents.web_surfer.MultimodalWebSurfer")

  * `autogen_ext.models.*` 用于模型客户端，如 [`OpenAIChatCompletionClient`](../../reference/python/autogen_ext.models.openai.html#autogen_ext.models.openai.OpenAIChatCompletionClient "autogen_ext.models.openai.OpenAIChatCompletionClient") 以及用于连接托管和本地模型的 `SKChatCompletionAdapter`。

  * `autogen_ext.tools.*` 用于工具，如 GraphRAG `LocalSearchTool` 和 [`mcp_server_tools()`](../../reference/python/autogen_ext.tools.mcp.html#autogen_ext.tools.mcp.mcp_server_tools "autogen_ext.tools.mcp.mcp_server_tools")。

  * `autogen_ext.executors.*` 用于执行器，如 [`DockerCommandLineCodeExecutor`](../../reference/python/autogen_ext.code_executors.docker.html#autogen_ext.code_executors.docker.DockerCommandLineCodeExecutor "autogen_ext.code_executors.docker.DockerCommandLineCodeExecutor") 和 [`ACADynamicSessionsCodeExecutor`](../../reference/python/autogen_ext.code_executors.azure.html#autogen_ext.code_executors.azure.ACADynamicSessionsCodeExecutor "autogen_ext.code_executors.azure.ACADynamicSessionsCodeExecutor")

  * `autogen_ext.runtimes.*` 用于代理运行时，如 [`GrpcWorkerAgentRuntime`](../../reference/python/autogen_ext.runtimes.grpc.html#autogen_ext.runtimes.grpc.GrpcWorkerAgentRuntime "autogen_ext.runtimes.grpc.GrpcWorkerAgentRuntime")

请参阅 [API 参考](../../reference/index.html) 以获取完整的组件及其 API 列表。

我们强烈鼓励开发人员构建自己的组件并将它们作为生态系统的一部分发布。

发现

发现社区扩展和示例

[Discover: Discover community extensions and samples](./discover.html)

创建您自己的

创建您自己的扩展

[Create your own: Create your own extension](./create-your-own.html)

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/extensions-user-guide/index.md)

[ __Show Source](../../_sources/user-guide/extensions-user-guide/index.md.txt)
