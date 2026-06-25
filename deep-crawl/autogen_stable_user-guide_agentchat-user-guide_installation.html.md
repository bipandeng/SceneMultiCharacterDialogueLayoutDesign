<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/installation.html -->

# Installation#

## Create a Virtual Environment (optional)#

在本地安装 AgentChat 时，我们建议使用虚拟环境进行安装。这将确保 AgentChat 的依赖与系统的其余部分隔离开来。

venv

创建并激活：

Linux/Mac:
    
    
    python3 -m venv .venv
    source .venv/bin/activate
    

Windows command-line:
    
    
    # The command may be `python3` instead of `python` depending on your setup
    python -m venv .venv
    .venv\Scripts\activate.bat
    

稍后要停用，请运行：
    
    
    deactivate
    

conda

如果你还没有安装，请 [安装 Conda](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html)。

创建并激活：
    
    
    conda create -n autogen python=3.12
    conda activate autogen
    

稍后要停用，请运行：
    
    
    conda deactivate
    

## Install Using pip#

使用 pip 安装 `autogen-agentchat` 包：
    
    
    pip install -U "autogen-agentchat"
    

Note

需要 Python 3.10 或更高版本。

## Install OpenAI for Model Client#

要使用 OpenAI 和 Azure OpenAI 模型，你需要安装以下扩展：
    
    
    pip install "autogen-ext[openai]"
    

如果你使用 Azure OpenAI 的 AAD 身份验证，则需要安装以下内容：
    
    
    pip install "autogen-ext[azure]"
    

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/installation.md)

[ __Show Source](../../_sources/user-guide/agentchat-user-guide/installation.md.txt)