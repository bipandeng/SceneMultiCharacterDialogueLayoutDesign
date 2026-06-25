<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/autogenstudio-user-guide/index.html -->

# AutoGen Studio#

[![PyPI version](https://badge.fury.io/py/autogenstudio.svg)](https://badge.fury.io/py/autogenstudio) [![Downloads](https://static.pepy.tech/badge/autogenstudio/week)](https://pepy.tech/project/autogenstudio)

AutoGen Studio 是一个低代码(low-code)界面,旨在帮助你快速搭建 AI 智能体的原型,为它们添加工具,将它们组合成团队,并与它们交互以完成任务。它构建于 [AutoGen AgentChat](https://microsoft.github.io/autogen) 之上,后者是一个用于构建多智能体应用的高级 API。

> 观看关于 AutoGen Studio v0.4 的视频教程(02/25) - <https://youtu.be/oum6EI7wohM>

[![A Friendly Introduction to AutoGen Studio v0.4](https://img.youtube.com/vi/oum6EI7wohM/maxresdefault.jpg)](https://www.youtube.com/watch?v=oum6EI7wohM)

AutoGen Studio 的代码位于 GitHub:[microsoft/autogen](https://github.com/microsoft/autogen/tree/main/python/packages/autogen-studio)

Caution

AutoGen Studio 旨在帮助你快速搭建多智能体工作流的原型,并展示使用 AutoGen 构建的最终用户界面示例。它并不意味着是一个生产就绪(production-ready)的应用。鼓励开发人员使用 AutoGen 框架来构建自己的应用程序,并实现身份验证、安全性以及部署应用所需的其他功能。

## 功能 - 使用 AutoGen Studio 你能做什么?#

AutoGen Studio 提供四个主要界面来帮助你构建和管理多智能体系统:

  1. **团队构建器(Team Builder)**

     * 通过声明式规范(JSON)或拖放方式创建智能体团队的可视化界面

     * 支持配置所有核心组件:团队、智能体、工具、模型以及终止条件

     * 完全兼容 AgentChat 的组件定义

  2. **演练场(Playground)**

     * 用于测试和运行智能体团队的交互式环境

     * 主要特性包括:

       * 智能体之间的实时消息流式传输

       * 通过控制转换图(control transition graph)对消息流进行可视化展示

       * 使用 UserProxyAgent 与团队进行交互式会话

       * 完整的运行控制,支持暂停或停止执行

  3. **资源库(Gallery)**

     * 用于发现和导入社区创建组件的中央枢纽

     * 便于第三方组件的集成

  4. **部署(Deployment)**

     * 导出团队并在 Python 代码中运行

     * 基于团队配置设置和测试端点

     * 在 Docker 容器中运行团队

### 路线图#

请在[此处](https://github.com/microsoft/autogen/issues/4006)查阅项目路线图和相关 issue。

## 贡献指南#

我们欢迎对 AutoGen Studio 的贡献。我们建议按以下常规步骤为项目做出贡献:

  * 阅读整个 AutoGen 项目的[贡献指南](https://github.com/microsoft/autogen/blob/main/CONTRIBUTING.md)

  * 请阅读 AutoGen Studio 的[路线图](https://github.com/microsoft/autogen/issues/4006)以了解项目当前的优先事项。尤其欢迎为带有 `help-wanted` 标签的 Studio 相关 issue 提供帮助

  * 对于任何与 Studio 相关的问题、疑问和 PR,请使用 [`proj-studio`](https://github.com/microsoft/autogen/issues?q=is%3Aissue%20state%3Aopen%20label%3Aproj-studio) 标签

  * 请在路线图 issue 或新的 issue 上发起讨论,以讨论你提议的贡献。

  * 提交包含你的贡献的拉取请求(Pull Request)!

  * 如果你正在修改 AutoGen Studio,它有自己的开发容器(DevContainer)。请参阅 `.devcontainer/README.md` 中的说明以使用它

## 关于安全性的一点说明#

AutoGen Studio 是一个研究原型,**不应**在生产环境中使用。鼓励采取一些基线实践,例如为你的智能体使用 Docker 代码执行环境。

然而,其他方面的考虑,例如与越狱相关的严格测试、确保大语言模型(LLM)仅能根据终端用户的权限访问正确的数据键等安全特性,尚未在 AutoGen Studio 中实现。

如果你正在构建生产应用,请使用 AutoGen 框架并实现必要的安全功能。

## 致谢与引用#

AutoGen Studio 基于 [AutoGen](https://microsoft.github.io/autogen) 项目。它改编自 2023 年 10 月构建的一个研究原型(原始致谢:Victor Dibia、Gagan Bansal、Adam Fourney、Piali Choudhury、Saleema Amershi、Ahmed Awadallah、Chi Wang)。

如果你的研究中使用了 AutoGen Studio,请引用以下论文:
    
    
    @inproceedings{autogenstudio,
      title={AUTOGEN STUDIO: A No-Code Developer Tool for Building and Debugging Multi-Agent Systems},
      author={Dibia, Victor and Chen, Jingya and Bansal, Gagan and Syed, Suff and Fourney, Adam and Zhu, Erkang and Wang, Chi and Amershi, Saleema},
      booktitle={Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing: System Demonstrations},
      pages={72--79},
      year={2024}
    }
    

## 下一步#

首先,请按照[安装说明](installation.html)安装 AutoGen Studio。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/autogenstudio-user-guide/index.md)

[ __Show Source](../../_sources/user-guide/autogenstudio-user-guide/index.md.txt)