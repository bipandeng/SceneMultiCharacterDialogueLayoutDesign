<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tracing.html -->

# 跟踪和可观测性#

AutoGen 具有[内置的跟踪支持](https://microsoft.github.io/autogen/dev/user-guide/core-user-guide/framework/telemetry.html)以及可观测性功能，用于收集应用程序执行的综合记录。此功能对于调试、性能分析以及理解应用程序的流程非常有用。

此能力由 [OpenTelemetry](https://opentelemetry.io/) 库提供支持，这意味着你可以使用任何与 OpenTelemetry 兼容的后端来收集和分析跟踪。

AutoGen 在跟踪方面遵循针对智能体和工具的 [OpenTelemetry 语义约定](https://opentelemetry.io/docs/specs/semconv/)。它还遵循目前正在开发中的 [GenAI 系统的语义约定](https://opentelemetry.io/docs/specs/semconv/gen-ai/)。

## 设置#

首先，你需要安装 OpenTelemetry Python 包。可以使用 pip 进行安装：
    
    
    pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc opentelemetry-instrumentation-openai
    

一旦你安装了 SDK，在 AutoGen 中设置跟踪的最简单方法是：

  1. 配置一个 OpenTelemetry 跟踪器提供程序（tracer provider）

  2. 设置一个导出器以将跟踪发送到你的后端

  3. 将跟踪器提供程序连接到 AutoGen 运行时

## 遥测后端#

要收集和查看跟踪，你需要设置一个遥测后端。有几个开源选项可用，包括 Jaeger、Zipkin。在本例中，我们将使用 Jaeger 作为我们的遥测后端。

为了快速开始，你可以使用 Docker 在本地运行 Jaeger：
    
    
    docker run -d --name jaeger \
      -e COLLECTOR_OTLP_ENABLED=true \
      -p 16686:16686 \
      -p 4317:4317 \
      -p 4318:4318 \
      jaegertracing/all-in-one:latest
    

此命令启动一个 Jaeger 实例，它在端口 16686 上监听 Jaeger UI，并在端口 4317 上监听 OpenTelemetry 收集器。你可以通过 `http://localhost:16686` 访问 Jaeger UI。

## 跟踪 AgentChat 团队#

在接下来的部分中，我们将回顾如何对 AutoGen GroupChat 团队启用跟踪。AutoGen 运行时已经支持 OpenTelemetry（自动记录消息元数据）。首先，我们将创建一个跟踪服务，用于检测 AutoGen 运行时。
    
    
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.openai import OpenAIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    
    # Set up telemetry span exporter.
    otel_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    span_processor = BatchSpanProcessor(otel_exporter)
    
    # Set up telemetry trace provider.
    tracer_provider = TracerProvider(resource=Resource({"service.name": "autogen-test-agentchat"}))
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)
    
    # Instrument the OpenAI Python library
    OpenAIInstrumentor().instrument()
    
    # we will get reference this tracer later using its service name
    # tracer = trace.get_tracer("autogen-test-agentchat")
    
    
    
    Overriding of current TracerProvider is not allowed
    Attempting to instrument while already instrumented
    

用于创建[团队](tutorial/teams.html)的所有代码你应该已经很熟悉了。

注意

AgentChat 团队是使用 AutoGen Core 的智能体运行时运行的。反过来，该运行时已经被检测以进行日志记录，请参阅 [Core 遥测指南](../core-user-guide/framework/telemetry.html)。要禁用智能体运行时遥测，你可以在运行时构造函数中将 `trace_provider` 设置为 `opentelemetry.trace.NoOpTracerProvider`。

此外，你可以将环境变量 `AUTOGEN_DISABLE_RUNTIME_TRACING` 设置为 `true` 来禁用智能体运行时遥测，如果你无法访问运行时构造函数。例如，当你使用 `ComponentConfig` 时。
    
    
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
    from autogen_agentchat.teams import SelectorGroupChat
    from autogen_agentchat.ui import Console
    from autogen_core import SingleThreadedAgentRuntime
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    
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
    
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o")
    
        # Get a tracer with the default tracer provider.
        tracer = trace.get_tracer("tracing-autogen-agentchat")
    
        # Use the tracer to create a span for the main function.
        with tracer.start_as_current_span("run_team"):
            planning_agent = AssistantAgent(
                "PlanningAgent",
                description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
                model_client=model_client,
                system_message="""
                You are a planning agent.
                Your job is to break down complex tasks into smaller, manageable subtasks.
                Your team members are:
                    WebSearchAgent: Searches for information
                    DataAnalystAgent: Performs calculations
    
                You only plan and delegate tasks - you do not execute them yourself.
    
                When assigning tasks, use this format:
                1. <agent> : <task>
    
                After all tasks are complete, summarize the findings and end with "TERMINATE".
                """,
            )
    
            web_search_agent = AssistantAgent(
                "WebSearchAgent",
                description="An agent for searching information on the web.",
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
                description="An agent for performing calculations.",
                model_client=model_client,
                tools=[percentage_change_tool],
                system_message="""
                You are a data analyst.
                Given the tasks you have been assigned, you should analyze the data and provide results using the tools provided.
                If you have not seen the data, ask for it.
                """,
            )
    
            text_mention_termination = TextMentionTermination("TERMINATE")
            max_messages_termination = MaxMessageTermination(max_messages=25)
            termination = text_mention_termination | max_messages_termination
    
            selector_prompt = """Select an agent to perform task.
    
            {roles}
    
            Current conversation context:
            {history}
    
            Read the above conversation, then select an agent from {participants} to perform the next task.
            Make sure the planner agent has assigned tasks before other agents start working.
            Only select one agent.
            """
    
            task = "Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?"
    
            runtime = SingleThreadedAgentRuntime(
                tracer_provider=trace.NoOpTracerProvider(),  # Disable telemetry for runtime.
            )
            runtime.start()
    
            team = SelectorGroupChat(
                [planning_agent, web_search_agent, data_analyst_agent],
                model_client=model_client,
                termination_condition=termination,
                selector_prompt=selector_prompt,
                allow_repeated_speaker=True,
                runtime=runtime,
            )
            await Console(team.run_stream(task=task))
    
            await runtime.stop()
    
        await model_client.close()
    
    
    # asyncio.run(main())
    
    
    
    await main()
    
    
    
    ---------- TextMessage (user) ----------
    Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
    ---------- TextMessage (PlanningAgent) ----------
    To find the information requested, we need to follow these steps:
    
    1. Identify the Miami Heat player with the highest points during the 2006-2007 season.
    2. Get the total rebounds for that player in both the 2007-2008 and 2008-2009 seasons.
    3. Calculate the percentage change in total rebounds between these two seasons.
    
    Here are the tasks assigned to achieve this:
    
    1. WebSearchAgent: Find the Miami Heat player with the highest points during the 2006-2007 season.
    2. WebSearchAgent: After identifying the player, find the total rebounds for that player in the 2007-2008 and 2008-2009 seasons.
    3. DataAnalystAgent: Calculate the percentage change in the player's total rebounds between the 2007-2008 and 2008-2009 seasons.
    ---------- ToolCallRequestEvent (WebSearchAgent) ----------
    [FunctionCall(id='call_hS8yod9l6CYUllDveUffp58e', arguments='{"query":"Miami Heat leading scorer 2006-2007 season"}', name='search_web_tool')]
    ---------- ToolCallExecutionEvent (WebSearchAgent) ----------
    [FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n        Udonis Haslem: 844 points\n        Dwayne Wade: 1397 points\n        James Posey: 550 points\n        ...\n        ', name='search_web_tool', call_id='call_hS8yod9l6CYUllDveUffp58e', is_error=False)]
    ---------- ToolCallSummaryMessage (WebSearchAgent) ----------
    Here are the total points scored by Miami Heat players in the 2006-2007 season:
            Udonis Haslem: 844 points
            Dwayne Wade: 1397 points
            James Posey: 550 points
            ...
            
    ---------- ToolCallRequestEvent (WebSearchAgent) ----------
    [FunctionCall(id='call_bUJxtpxUXFSxECDogye9WL0g', arguments='{"query":"Dwyane Wade total rebounds in 2007-2008 season"}', name='search_web_tool')]
    ---------- ToolCallExecutionEvent (WebSearchAgent) ----------
    [FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', name='search_web_tool', call_id='call_bUJxtpxUXFSxECDogye9WL0g', is_error=False)]
    ---------- ToolCallSummaryMessage (WebSearchAgent) ----------
    The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.
    ---------- ToolCallRequestEvent (WebSearchAgent) ----------
    [FunctionCall(id='call_pgYNSDhhyodtteot56FRktxp', arguments='{"query":"Dwyane Wade total rebounds in 2008-2009 season"}', name='search_web_tool')]
    ---------- ToolCallExecutionEvent (WebSearchAgent) ----------
    [FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', name='search_web_tool', call_id='call_pgYNSDhhyodtteot56FRktxp', is_error=False)]
    ---------- ToolCallSummaryMessage (WebSearchAgent) ----------
    The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.
    ---------- ToolCallRequestEvent (DataAnalystAgent) ----------
    [FunctionCall(id='call_A89acjYHlNDLzG09rVNJ0J6H', arguments='{"start":214,"end":398}', name='percentage_change_tool')]
    ---------- ToolCallExecutionEvent (DataAnalystAgent) ----------
    [FunctionExecutionResult(content='85.98130841121495', name='percentage_change_tool', call_id='call_A89acjYHlNDLzG09rVNJ0J6H', is_error=False)]
    ---------- ToolCallSummaryMessage (DataAnalystAgent) ----------
    85.98130841121495
    ---------- TextMessage (PlanningAgent) ----------
    The Miami Heat player with the highest points during the 2006-2007 season was Dwyane Wade, who scored 1,397 points. 
    
    The total rebounds for Dwyane Wade in the 2007-2008 season were 214, and in the 2008-2009 season, they were 398.
    
    The percentage change in his total rebounds between these two seasons is approximately 86.0%.
    
    TERMINATE
    

然后你可以使用 Jaeger UI 查看从上述应用程序运行中收集的跟踪。

![Jaeger UI](../../_images/jaeger.png)

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/tracing.ipynb)

[ __Show Source](../../_sources/user-guide/agentchat-user-guide/tracing.ipynb.txt)
