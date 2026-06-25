<!-- 来源: https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.code_executors.docker.html -->

# autogen_ext.code_executors.docker#

_class _DockerCommandLineCodeExecutor(_image : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") = 'python:3-slim'_, _container_name : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _*_ , _timeout : [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") = 60_, _work_dir : [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path "\(in Python v3.14\)") | [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _bind_dir : [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path "\(in Python v3.14\)") | [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _auto_remove : [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") = True_, _stop_container : [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") = True_, _device_requests : [List](https://docs.python.org/3/library/typing.html#typing.List "\(in Python v3.14\)")[DeviceRequest] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _functions : [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence "\(in Python v3.14\)")[[FunctionWithRequirements](autogen_core.code_executor.html#autogen_core.code_executor.FunctionWithRequirements "autogen_core.code_executor._func_with_reqs.FunctionWithRequirements")[[Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)"), A] | [Callable](https://docs.python.org/3/library/typing.html#typing.Callable "\(in Python v3.14\)")[[...], [Any](https://docs.python.org/3/library/typing.html#typing.Any "\(in Python v3.14\)")] | [FunctionWithRequirementsStr](autogen_core.code_executor.html#autogen_core.code_executor.FunctionWithRequirementsStr "autogen_core.code_executor._func_with_reqs.FunctionWithRequirementsStr")] = []_, _functions_module : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") = 'functions'_, _extra_volumes : [Dict](https://docs.python.org/3/library/typing.html#typing.Dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [Dict](https://docs.python.org/3/library/typing.html#typing.Dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _extra_hosts : [Dict](https://docs.python.org/3/library/typing.html#typing.Dict "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"), [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")] | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _init_command : [str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)") = None_, _delete_tmp_files : [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") = False_)[[source]](../../_modules/autogen_ext/code_executors/docker/_docker_code_executor.html#DockerCommandLineCodeExecutor)#
    

Bases: [`CodeExecutor`](autogen_core.code_executor.html#autogen_core.code_executor.CodeExecutor "autogen_core.code_executor._base.CodeExecutor"), [`Component`](autogen_core.html#autogen_core.Component "autogen_core._component_config.Component")[`DockerCommandLineCodeExecutorConfig`]

通过 Docker 容器中的命令行环境执行代码。

注意

此类需要为 autogen-ext 包安装 docker 扩展：
    
    
    pip install "autogen-ext[docker]"
    

执行器首先将每个代码块保存在工作目录的一个文件中，然后在容器中执行该代码文件。执行器按接收顺序执行代码块。目前，执行器仅支持 Python 和 shell 脚本。对于 Python 代码，请在代码块中使用语言 "python"。对于 shell 脚本，请在代码块中使用语言 "bash"、"shell"、"sh"、"pwsh"、"powershell" 或 "ps1"。

参数：
    

  * **image** (__type___,__optional_) – 用于代码执行的 Docker 镜像。默认为 "python:3-slim"。

  * **container_name** (_Optional_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]__,__optional_) – 要创建的 Docker 容器的名称。如果为 None，将自动生成一个名称。默认为 None。

  * **timeout** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – 代码执行的超时时间。默认为 60。

  * **work_dir** (_Union_ _[__Path_ _,_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]__,__optional_) – 代码执行的工作目录。默认为临时目录。

  * **bind_dir** (_Union_ _[__Path_ _,_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]__,__optional_) – 将被绑定的目录

  * **spawn** (_到代码执行器容器。在你想_)

  * **work_dir.** (_从另一个容器内部生成容器时很有用。默认为_)

  * **auto_remove** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – 如果为 true，当 Docker 容器停止时将自动删除它。默认为 True。

  * **stop_container** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – 如果为 true，在调用 stop 时、上下文管理器退出时或 Python 进程以 atext 退出时，将自动停止容器。默认为 True。

  * **device_requests** (_Optional_ _[__List_ _[__DeviceRequest_ _]__]__,__optional_) – 要添加到容器中的设备请求实例列表，用于暴露 GPU（例如，[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])]）。默认为 None。

  * **functions** (_List_ _[__Union_ _[_[_FunctionWithRequirements_](autogen_core.code_executor.html#autogen_core.code_executor.FunctionWithRequirements "autogen_core.code_executor.FunctionWithRequirements") _[__Any_ _,__A_ _]__,__Callable_ _[__...__,__Any_ _]__]__]_) – 代码执行器可用的函数列表。默认为空列表。

  * **functions_module** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__optional_) – 将创建的用于存储函数的模块的名称。默认为 "functions"。

  * **extra_volumes** (_Optional_ _[__Dict_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__Dict_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]__]__]__,__optional_) – 要挂载到容器的额外卷（除了 work_dir）的字典；键是主机源路径，值 'bind' 是容器路径。参见默认为 None。示例：extra_volumes = {'/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'}, '/var/www': {'bind': '/mnt/vol1', 'mode': 'ro'}}

  * **extra_hosts** (_Optional_ _[__Dict_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]__]__,__optional_) – 要添加到容器的主机映射的字典。（参见 Docker 文档中关于 extra_hosts 的内容）默认为 None。示例：extra_hosts = {"kubernetes.docker.internal": "host-gateway"}

  * **init_command** (_Optional_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]__,__optional_) – 在每次 shell 操作执行之前运行的 shell 命令。默认为 None。示例：init_command="kubectl config use-context docker-hub"

  * **delete_tmp_files** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – 如果为 true，将在执行后删除临时文件。默认为 False。

注意

使用当前目录 (".") 作为工作目录已弃用。使用它将引发弃用警告。

component_config_schema#
    

alias of `DockerCommandLineCodeExecutorConfig`

component_provider_override _: ClassVar[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") | [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")]__ = 'autogen_ext.code_executors.docker.DockerCommandLineCodeExecutor'_#
    

覆盖组件的 provider 字符串。这应该用于防止内部模块名称成为模块名称的一部分。

SUPPORTED_LANGUAGES _: ClassVar[List[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]]__ = ['bash', 'shell', 'sh', 'pwsh', 'powershell', 'ps1', 'python']_#
    

FUNCTION_PROMPT_TEMPLATE _: ClassVar[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]__ = 'You have access to the following user defined functions. They can be accessed from the module called `$module_name` by their function names.\n\nFor example, if there was a function called `foo` you could import it by writing `from $module_name import foo`\n\n$functions'_#
    

_property _timeout _: [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")_#
    

（实验性）代码执行的超时时间。

_property _work_dir _: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path "\(in Python v3.14\)")_#
    

_property _bind_dir _: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path "\(in Python v3.14\)")_#
    

_async _execute_code_blocks(_code_blocks : [List](https://docs.python.org/3/library/typing.html#typing.List "\(in Python v3.14\)")[[CodeBlock](autogen_core.code_executor.html#autogen_core.code_executor.CodeBlock "autogen_core.code_executor._base.CodeBlock")]_, _cancellation_token : [CancellationToken](autogen_core.html#autogen_core.CancellationToken "autogen_core._cancellation_token.CancellationToken")_) → CommandLineCodeResult[[source]](../../_modules/autogen_ext/code_executors/docker/_docker_code_executor.html#DockerCommandLineCodeExecutor.execute_code_blocks)#
    

（实验性）执行代码块并返回结果。

参数：
    

**code_blocks** (_List_ _[_[_CodeBlock_](autogen_core.code_executor.html#autogen_core.code_executor.CodeBlock "autogen_core.code_executor.CodeBlock") _]_) – 要执行的代码块。

返回：
    

**CommandlineCodeResult** – 代码执行的结果。

_async _restart() → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/code_executors/docker/_docker_code_executor.html#DockerCommandLineCodeExecutor.restart)#
    

（实验性）重启 Docker 容器代码执行器。

_async _stop() → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/code_executors/docker/_docker_code_executor.html#DockerCommandLineCodeExecutor.stop)#
    

（实验性）停止代码执行器。

停止 Docker 容器并清理任何临时文件（如果已创建），以及临时目录。该方法首先等待所有取消任务完成后再停止容器。最后将执行器标记为未运行状态。如果容器未运行，则该方法不执行任何操作。

_async _start() → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[[source]](../../_modules/autogen_ext/code_executors/docker/_docker_code_executor.html#DockerCommandLineCodeExecutor.start)#
    

（实验性）启动代码执行器。

此方法设置工作环境变量，连接到 Docker 并启动代码执行器。如果没有为代码执行器提供工作目录，则创建一个临时目录并将其设置为代码执行器工作目录。

__本页内容

[ __在 GitHub 上编辑](https://github.com/microsoft/autogen/edit/main/python/docs/src/reference/python/autogen_ext.code_executors.docker.rst)

[ __查看源文件](../../_sources/reference/python/autogen_ext.code_executors.docker.rst.txt)