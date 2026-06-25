<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/serialize-components.html -->

# 序列化组件#

AutoGen 提供了一个 [`Component`](../../reference/python/autogen_core.html#autogen_core.Component "autogen_core.Component") 配置类，它定义了将组件序列化/反序列化为声明式规范的行为。我们可以分别通过调用 `.dump_component()` 和 `.load_component()` 来实现这一点。这对于调试、可视化以及与他人分享你的工作非常有用。在本笔记中，我们将演示如何将多个组件序列化为像 JSON 文件这样的声明式规范。

警告

仅从可信来源加载组件。

通过序列化组件，每个组件都实现了其序列化和反序列化的逻辑——即如何生成声明式规范以及如何将其转换回对象。

在某些情况下，创建对象可能涉及执行代码（例如，一个被序列化的函数）。仅从可信来源加载组件。

注意

`selector_func` 不可序列化，在序列化和反序列化过程中将被忽略。

## 终止条件示例#

在下面的示例中，我们将在 Python 中定义终止条件（智能体团队的一部分），将其导出为字典/JSON，并演示如何从字典/JSON 加载终止条件对象。
    
    
    from autogen_agentchat.conditions import MaxMessageTermination, StopMessageTermination
    
    max_termination = MaxMessageTermination(5)
    stop_termination = StopMessageTermination()
    
    or_termination = max_termination | stop_termination
    
    or_term_config = or_termination.dump_component()
    print("Config: ", or_term_config.model_dump_json())
    
    new_or_termination = or_termination.load_component(or_term_config)
    
    
    
    Config:  {"provider":"autogen_agentchat.base.OrTerminationCondition","component_type":"termination","version":1,"component_version":1,"description":null,"config":{"conditions":[{"provider":"autogen_agentchat.conditions.MaxMessageTermination","component_type":"termination","version":1,"component_version":1,"config":{"max_messages":5}},{"provider":"autogen_agentchat.conditions.StopMessageTermination","component_type":"termination","version":1,"component_version":1,"config":{}}]}}
    

## 智能体示例#

在下面的示例中，我们将在 Python 中定义一个智能体，将其导出为字典/JSON，并演示如何从字典/JSON 加载智能体对象。
    
    
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    # 创建一个使用 OpenAI GPT-4o 模型的智能体。
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        # api_key="YOUR_API_KEY",
    )
    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        handoffs=["flights_refunder", "user"],
        # tools=[], # 暂不支持工具的序列化
        system_message="Use tools to solve tasks.",
    )
    user_proxy = UserProxyAgent(name="user")
    
    
    
    user_proxy_config = user_proxy.dump_component()  # 转储组件
    print(user_proxy_config.model_dump_json())
    up_new = user_proxy.load_component(user_proxy_config)  # 加载组件
    
    
    
    {"provider":"autogen_agentchat.agents.UserProxyAgent","component_type":"agent","version":1,"component_version":1,"description":null,"config":{"name":"user","description":"A human user"}}
    
    
    
    agent_config = agent.dump_component()  # 转储组件
    print(agent_config.model_dump_json())
    agent_new = agent.load_component(agent_config)  # 加载组件
    
    
    
    {"provider":"autogen_agentchat.agents.AssistantAgent","component_type":"agent","version":1,"component_version":1,"description":null,"config":{"name":"assistant","model_client":{"provider":"autogen_ext.models.openai.OpenAIChatCompletionClient","component_type":"model","version":1,"component_version":1,"config":{"model":"gpt-4o"}},"handoffs":[{"target":"flights_refunder","description":"Handoff to flights_refunder.","name":"transfer_to_flights_refunder","message":"Transferred to flights_refunder, adopting the role of flights_refunder immediately."},{"target":"user","description":"Handoff to user.","name":"transfer_to_user","message":"Transferred to user, adopting the role of user immediately."}],"model_context":{"provider":"autogen_core.model_context.UnboundedChatCompletionContext","component_type":"chat_completion_context","version":1,"component_version":1,"config":{}},"description":"An agent that provides assistance with ability to use tools.","system_message":"Use tools to solve tasks.","reflect_on_tool_use":false,"tool_call_summary_format":"{result}"}}
    

类似的方法也可用于序列化 `MultiModalWebSurfer` 智能体。
    
    
    from autogen_ext.agents.web_surfer import MultimodalWebSurfer
    
    agent = MultimodalWebSurfer(
        name="web_surfer",
        model_client=model_client,
        headless=False,
    )
    
    web_surfer_config = agent.dump_component()  # 转储组件
    print(web_surfer_config.model_dump_json())
    
    

## 团队示例#

在下面的示例中，我们将在 Python 中定义一个团队，将其导出为字典/JSON，并演示如何从字典/JSON 加载团队对象。
    
    
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
    from autogen_agentchat.conditions import MaxMessageTermination
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    # 创建一个使用 OpenAI GPT-4o 模型的智能体。
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        # api_key="YOUR_API_KEY",
    )
    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        handoffs=["flights_refunder", "user"],
        # tools=[], # 暂不支持工具的序列化
        system_message="Use tools to solve tasks.",
    )
    
    team = RoundRobinGroupChat(participants=[agent], termination_condition=MaxMessageTermination(2))
    
    team_config = team.dump_component()  # 转储组件
    print(team_config.model_dump_json())
    
    await model_client.close()
    
    
    
    {"provider":"autogen_agentchat.teams.RoundRobinGroupChat","component_type":"team","version":1,"component_version":1,"description":null,"config":{"participants":[{"provider":"autogen_agentchat.agents.AssistantAgent","component_type":"agent","version":1,"component_version":1,"config":{"name":"assistant","model_client":{"provider":"autogen_ext.models.openai.OpenAIChatCompletionClient","component_type":"model","version":1,"component_version":1,"config":{"model":"gpt-4o"}},"handoffs":[{"target":"flights_refunder","description":"Handoff to flights_refunder.","name":"transfer_to_flights_refunder","message":"Transferred to flights_refunder, adopting the role of flights_refunder immediately."},{"target":"user","description":"Handoff to user.","name":"transfer_to_user","message":"Transferred to user, adopting the role of user immediately."}],"model_context":{"provider":"autogen_core.model_context.UnboundedChatCompletionContext","component_type":"chat_completion_context","version":1,"component_version":1,"config":{}},"description":"An agent that provides assistance with ability to use tools.","system_message":"Use tools to solve tasks.","reflect_on_tool_use":false,"tool_call_summary_format":"{result}"}}],"termination_condition":{"provider":"autogen_agentchat.conditions.MaxMessageTermination","component_type":"termination","version":1,"component_version":1,"config":{"max_messages":2}}}}
    

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/serialize-components.ipynb)

[ __Show Source](../../_sources/user-guide/agentchat-user-guide/serialize-components.ipynb.txt)
