<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/framework/logging.html -->

# 日志#

AutoGen 使用 Python 内置的 [`logging`](https://docs.python.org/3/library/logging.html) 模块。

有两种日志记录：

  * **跟踪日志（Trace logging）** ：用于调试，是人类可读的消息，用于指示正在发生的事情。这是为了让开发人员了解代码中正在发生的情况。其他系统不应依赖于这些日志的内容和格式。

    * 名称：[`TRACE_LOGGER_NAME`](../../../reference/python/autogen_core.html#autogen_core.TRACE_LOGGER_NAME "autogen_core.TRACE_LOGGER_NAME")。

  * **结构化日志（Structured logging）** ：此记录器发出可被其他系统使用的结构化事件。其他系统可以依赖于这些日志的内容和格式。

    * 名称：[`EVENT_LOGGER_NAME`](../../../reference/python/autogen_core.html#autogen_core.EVENT_LOGGER_NAME "autogen_core.EVENT_LOGGER_NAME")。

    * 请参阅模块 [`autogen_core.logging`](../../../reference/python/autogen_core.logging.html#module-autogen_core.logging "autogen_core.logging") 以查看可用事件。

  * [`ROOT_LOGGER_NAME`](../../../reference/python/autogen_core.html#autogen_core.ROOT_LOGGER_NAME "autogen_core.ROOT_LOGGER_NAME") 可用于启用或禁用所有日志。

## 启用日志输出#

要启用跟踪日志记录，您可以使用以下代码：
    
    
    import logging
    
    from autogen_core import TRACE_LOGGER_NAME
    
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(TRACE_LOGGER_NAME)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
    

要启用结构化日志记录，您可以使用以下代码：
    
    
    import logging
    
    from autogen_core import EVENT_LOGGER_NAME
    
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    

### 结构化日志#

结构化日志允许您编写处理逻辑来处理实际事件（包括所有字段）而不仅仅是格式化字符串。

例如，如果您定义了此自定义事件并正在发出它，那么您可以编写以下处理程序来接收它。
    
    
    import logging
    from dataclasses import dataclass
    
    @dataclass
    class MyEvent:
        timestamp: str
        message: str
    
    class MyHandler(logging.Handler):
        def __init__(self) -> None:
            super().__init__()
    
        def emit(self, record: logging.LogRecord) -> None:
            try:
                # Use the StructuredMessage if the message is an instance of it
                if isinstance(record.msg, MyEvent):
                    print(f"Timestamp: {record.msg.timestamp}, Message: {record.msg.message}")
            except Exception:
                self.handleError(record)
    

这是您可以使用它的方式：
    
    
    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    my_handler = MyHandler()
    logger.handlers = [my_handler]
    

## 发出日志#

这两个名称是这些类型的根记录器。发出日志的代码应使用这些记录器的子记录器。例如，如果您正在编写模块 `my_module` 并希望发出跟踪日志，则应使用以下名称的记录器：
    
    
    import logging
    
    from autogen_core import TRACE_LOGGER_NAME
    logger = logging.getLogger(f"{TRACE_LOGGER_NAME}.my_module")
    

### 发出结构化日志#

如果您的事件是 dataclass，那么它可以在代码中这样发出：
    
    
    import logging
    from dataclasses import dataclass
    from autogen_core import EVENT_LOGGER_NAME
    
    @dataclass
    class MyEvent:
        timestamp: str
        message: str
    
    logger = logging.getLogger(EVENT_LOGGER_NAME + ".my_module")
    logger.info(MyEvent("timestamp", "message"))
    

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/framework/logging.md)

[ __Show Source](../../../_sources/user-guide/core-user-guide/framework/logging.md.txt)
