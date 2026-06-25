<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/installation.html -->

# 安装#

## 创建虚拟环境（可选）#

在本地安装 AgentChat 时，我们建议使用虚拟环境进行安装。这将确保 AgentChat 的依赖项与系统的其他部分隔离。

venv

创建并激活：

Linux/Mac：
    
    
    python3 -m venv .venv
    source .venv/bin/activate
    

Windows 命令行：
    
    
    python3 -m venv .venv
    .venv\Scripts\activate.bat
    

稍后要停用，请运行：
    
    
    deactivate
    

conda

如果您尚未安装，请先 [安装 Conda](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html)。

创建并激活：
    
    
    conda create -n autogen python=3.12
    conda activate autogen
    

稍后要停用，请运行：
    
    
    conda deactivate
    

## 使用 pip 安装#

使用 pip 安装 `autogen-core` 包：
    
    
    pip install "autogen-core"
    

注意

需要 Python 3.10 或更高版本。

## 为模型客户端安装 OpenAI#

要使用 OpenAI 和 Azure OpenAI 模型，您需要安装以下扩展：
    
    
    pip install "autogen-ext[openai]"
    

如果您将 Azure OpenAI 与 AAD 身份验证一起使用，则需要安装以下内容：
    
    
    pip install "autogen-ext[azure]"
    

## 为代码执行安装 Docker（可选）#

我们建议使用 Docker 来使用 [`DockerCommandLineCodeExecutor`](../../reference/python/autogen_ext.code_executors.docker.html#autogen_ext.code_executors.docker.DockerCommandLineCodeExecutor "autogen_ext.code_executors.docker.DockerCommandLineCodeExecutor") 执行模型生成的代码。要安装 Docker，请按照 [Docker 网站](https://docs.docker.com/get-docker/) 上针对您操作系统的说明进行操作。

要了解有关代码执行的更多信息，请参阅 [命令行代码执行器](components/command-line-code-executors.html) 和 [代码执行](design-patterns/code-execution-groupchat.html)。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/installation.md)

[ __Show Source](../../_sources/user-guide/core-user-guide/installation.md.txt)
