<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/logging.html -->

# Logging#

AutoGen 使用 Python 内置的 [`logging`](https://docs.python.org/3/library/logging.html) 模块。

要为 AgentChat 启用日志记录，你可以使用以下代码：
    
    
    import logging
    
    from autogen_agentchat import EVENT_LOGGER_NAME, TRACE_LOGGER_NAME
    
    logging.basicConfig(level=logging.WARNING)
    
    # For trace logging.
    trace_logger = logging.getLogger(TRACE_LOGGER_NAME)
    trace_logger.addHandler(logging.StreamHandler())
    trace_logger.setLevel(logging.DEBUG)
    
    # For structured message logging, such as low-level messages between agents.
    event_logger = logging.getLogger(EVENT_LOGGER_NAME)
    event_logger.addHandler(logging.StreamHandler())
    event_logger.setLevel(logging.DEBUG)
    

要启用其他日志，例如模型客户端调用和代理运行时事件，请参阅 [Core Logging Guide](../core-user-guide/framework/logging.html)。

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/logging.md)

[ __Show Source](../../_sources/user-guide/agentchat-user-guide/logging.md.txt)