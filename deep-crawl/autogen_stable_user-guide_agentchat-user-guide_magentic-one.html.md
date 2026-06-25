<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html -->

# Magentic-One#

[Magentic-One](https://aka.ms/magentic-one-blog) 是一个通用的多代理系统，用于解决跨多个领域的开放式 web 和基于文件的任务。它代表了多代理系统的重大进步，在多个代理基准测试上取得了有竞争力的性能（有关完整详细信息，请参阅 [technical report](https://arxiv.org/abs/2411.04468)）。

Magentic-One 最初于 [2024 年 11 月](https://aka.ms/magentic-one-blog) 发布时，是 [直接基于 `autogen-core` 库实现的](https://github.com/microsoft/autogen/tree/v0.4.4/python/packages/autogen-magentic-one)。我们现在已将 Magentic-One 移植到使用 `autogen-agentchat`，提供更模块化、更易于使用的接口。

为此，Magentic-One orchestrator [`MagenticOneGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.MagenticOneGroupChat "autogen_agentchat.teams.MagenticOneGroupChat") 现在只是一个 AgentChat 团队，支持所有标准的 AgentChat 代理和功能。同样，Magentic-One 的 [`MultimodalWebSurfer`](../../reference/python/autogen_ext.agents.web_surfer.html#autogen_ext.agents.web_surfer.MultimodalWebSurfer "autogen_ext.agents.web_surfer.MultimodalWebSurfer")、[`FileSurfer`](../../reference/python/autogen_ext.agents.file_surfer.html#autogen_ext.agents.file_surfer.FileSurfer "autogen_ext.agents.file_surfer.FileSurfer") 和 [`MagenticOneCoderAgent`](../../reference/python/autogen_ext.agents.magentic_one.html#autogen_ext.agents.magentic_one.MagenticOneCoderAgent "autogen_ext.agents.magentic_one.MagenticOneCoderAgent") 代理现在作为 AgentChat 代理广泛可用，可用于任何 AgentChat 工作流中。

最后，还有一个辅助类 [`MagenticOne`](../../reference/python/autogen_ext.teams.magentic_one.html#autogen_ext.teams.magentic_one.MagenticOne "autogen_ext.teams.magentic_one.MagenticOne")，它将所有这些捆绑在一起，就像论文中那样，只需最少的配置。

在我们的 [博客文章](https://aka.ms/magentic-one-blog) 和 [技术报告](https://arxiv.org/abs/2411.04468) 中找到有关 Magentic-one 的更多信息。

![Autogen Magentic-One example](../../_images/autogen-magentic-one-example.png)

**Example** ：上图说明了 Magentic-One 多代理团队完成了 GAIA 基准测试中的一个复杂任务。Magentic-One 的 Orchestrator 代理创建一个计划，将任务委派给其他代理，并跟踪实现目标的进度，根据需要动态修订计划。Orchestrator 可以将任务委派给 FileSurfer 代理以读取和处理文件，委派给 WebSurfer 代理以操作 Web 浏览器，或委派给 Coder 或 Computer Terminal 代理以编写或执行代码。

Caution

使用 Magentic-One 涉及与为人类设计的数字世界交互，这存在固有的风险。为了将这些风险降至最低，请考虑以下预防措施：

  1. **使用容器** ：在 docker 容器中运行所有任务以隔离代理并防止直接的系统攻击。

  2. **虚拟环境** ：使用虚拟环境运行代理并防止它们访问敏感数据。

  3. **监控日志** ：在执行期间和执行后密切监控日志，以检测和减轻风险行为。

  4. **人工监督** ：使用 human-in-the-loop 运行示例以监督代理并防止意外后果。

  5. **限制访问** ：限制代理对互联网和其他资源的访问，以防止未经授权的操作。

  6. **保护数据** ：确保代理无法访问可能被泄露的敏感数据或资源。不要与代理共享敏感信息。请注意，代理偶尔可能会尝试有风险的操作，例如招募人类寻求帮助或在无人工介入的情况下接受 cookie 协议。始终确保代理受到监控并在受控环境中运行，以防止意外后果。此外，请注意 Magentic-One 可能容易受到来自网页的提示注入攻击。

## Getting started#

安装所需的包：
    
    
    pip install "autogen-agentchat" "autogen-ext[magentic-one,openai]"
    
    # If using the MultimodalWebSurfer, you also need to install playwright dependencies:
    playwright install --with-deps chromium
    

如果你还没有完成，请通读 AgentChat 教程以了解 AgentChat 的概念。

然后，你可以尝试将 [`autogen_agentchat.teams.SelectorGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.SelectorGroupChat "autogen_agentchat.teams.SelectorGroupChat") 替换为 [`MagenticOneGroupChat`](../../reference/python/autogen_agentchat.teams.html#autogen_agentchat.teams.MagenticOneGroupChat "autogen_agentchat.teams.MagenticOneGroupChat")。

例如：
    
    
    import asyncio
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import MagenticOneGroupChat
    from autogen_agentchat.ui import Console
    
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o")
    
        assistant = AssistantAgent(
            "Assistant",
            model_client=model_client,
        )
        team = MagenticOneGroupChat([assistant], model_client=model_client)
        await Console(team.run_stream(task="Provide a different proof for Fermat's Last Theorem"))
        await model_client.close()
    
    
    asyncio.run(main())
    

要使用不同的模型，请参阅 [Models](tutorial/models.html) 获取更多信息。

或者，在团队中使用 Magentic-One 代理：

Caution

示例代码可能会从互联网下载文件、执行代码并与网页交互。在运行示例代码之前，请确保你处于安全的环境中。
    
    
    import asyncio
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_agentchat.teams import MagenticOneGroupChat
    from autogen_agentchat.ui import Console
    from autogen_ext.agents.web_surfer import MultimodalWebSurfer
    # from autogen_ext.agents.file_surfer import FileSurfer
    # from autogen_ext.agents.magentic_one import MagenticOneCoderAgent
    # from autogen_agentchat.agents import CodeExecutorAgent
    # from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
    
    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o")
    
        surfer = MultimodalWebSurfer(
            "WebSurfer",
            model_client=model_client,
        )
    
        team = MagenticOneGroupChat([surfer], model_client=model_client)
        await Console(team.run_stream(task="What is the UV index in Melbourne today?"))
    
        # # Note: you can also use  other agents in the team
        # team = MagenticOneGroupChat([surfer, file_surfer, coder, terminal], model_client=model_client)
        # file_surfer = FileSurfer( "FileSurfer",model_client=model_client)
        # coder = MagenticOneCoderAgent("Coder",model_client=model_client)
        # terminal = CodeExecutorAgent("ComputerTerminal",code_executor=LocalCommandLineCodeExecutor())
    
    
    asyncio.run(main())
    

或者，使用 [`MagenticOne`](../../reference/python/autogen_ext.teams.magentic_one.html#autogen_ext.teams.magentic_one.MagenticOne "autogen_ext.teams.magentic_one.MagenticOne") 辅助类，将所有代理捆绑在一起：
    
    
    import asyncio
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_ext.teams.magentic_one import MagenticOne
    from autogen_agentchat.ui import Console
    from autogen_agentchat.agents import ApprovalRequest, ApprovalResponse
    
    
    def approval_func(request: ApprovalRequest) -> ApprovalResponse:
        """Simple approval function that requests user input before code execution."""
        print(f"Code to execute:\n{request.code}")
        user_input = input("Do you approve this code execution? (y/n): ").strip().lower()
        if user_input == 'y':
            return ApprovalResponse(approved=True, reason="User approved the code execution")
        else:
            return ApprovalResponse(approved=False, reason="User denied the code execution")
    
    
    async def example_usage():
        client = OpenAIChatCompletionClient(model="gpt-4o")
        # Enable code execution approval for security
        m1 = MagenticOne(client=client, approval_func=approval_func)
        task = "Write a Python script to fetch data from an API."
        result = await Console(m1.run_stream(task=task))
        print(result)
    
    
    if __name__ == "__main__":
        asyncio.run(example_usage())
    

## Architecture#

![Autogen Magentic-One architecture](../../_images/autogen-magentic-one-agents.png)

Magentic-One 的工作基于一种多代理架构，其中首席 Orchestrator 代理负责高级规划、指导其他代理并跟踪任务进度。Orchestrator 首先创建一个计划来完成任务，在维护的 Task Ledger 中收集所需的事实和有根据的猜测。在其计划的每个步骤中，Orchestrator 会创建一个 Progress Ledger，在其中进行自我反思以检查任务进度并检查任务是否完成。如果任务尚未完成，它会将其中一个 Magentic-One 其他代理分配一个子任务来完成。在分配的代理完成其子任务后，Orchestrator 会更新 Progress Ledger 并继续以这种方式进行，直到任务完成。如果 Orchestrator 发现足够多的步骤都没有取得进展，它可以更新 Task Ledger 并创建一个新计划。上图说明了这一点；因此，Orchestrator 的工作分为外部循环（更新 Task Ledger）和内部循环（更新 Progress Ledger）。

总体而言，Magentic-One 由以下代理组成：

  * Orchestrator：负责任务分解和规划的首席代理，指导其他代理执行子任务，跟踪整体进度，并根据需要采取纠正措施

  * WebSurfer：这是一个基于 LLM 的代理，擅长命令和管理基于 Chromium 的 Web 浏览器的状态。对于每个传入的请求，WebSurfer 在浏览器上执行一个操作，然后报告网页的新状态。WebSurfer 的操作空间包括导航（例如访问 URL、执行网页搜索）；网页操作（例如，单击和键入）；以及阅读操作（例如，总结或回答问题）。WebSurfer 依赖浏览器的可访问性树和 set-of-marks 提示来执行其操作。

  * FileSurfer：这是一个基于 LLM 的代理，它命令一个基于 markdown 的文件预览应用程序来读取大多数类型的本地文件。FileSurfer 还可以执行常见的导航任务，例如列出目录内容和导航文件夹结构。

  * Coder：这是一个基于 LLM 的代理，通过其系统提示专门用于编写代码、分析从其他代理收集的信息或创建新工件。

  * ComputerTerminal：最后，ComputerTerminal 为团队提供对控制台 shell 的访问，其中可以执行 Coder 的程序，并且可以安装新的编程库。

总体而言，Magentic-One 的代理为 Orchestrator 提供了解决各种开放性问题所需的工具和能力，以及在动态且不断变化的 Web 和文件系统环境中自主适应和行动的能力。

虽然我们用于所有代理的默认多模态 LLM 是 GPT-4o，但 Magentic-One 与模型无关，可以整合异构模型以支持不同的能力或满足完成任务时的不同成本要求。例如，它可以使用不同的 LLM 和 SLM 及其专门的版本来为不同的代理提供动力。我们建议为 Orchestrator 代理使用强大的推理模型，例如 GPT-4o。在 Magentic-One 的不同配置中，我们还尝试将 OpenAI o1-preview 用于 Orchestrator 的外部循环和 Coder，而其他代理继续使用 GPT-4o。

## Citation#
    
    
    @misc{fourney2024magenticonegeneralistmultiagentsolving,
          title={Magentic-One: A Generalist Multi-Agent System for Solving Complex Tasks},
          author={Adam Fourney and Gagan Bansal and Hussein Mozannar and Cheng Tan and Eduardo Salinas and Erkang and Zhu and Friederike Niedtner and Grace Proebsting and Griffin Bassman and Jack Gerrits and Jacob Alber and Peter Chang and Ricky Loynd and Robert West and Victor Dibia and Ahmed Awadallah and Ece Kamar and Rafah Hosn and Saleema Amershi},
          year={2024},
          eprint={2411.04468},
          archivePrefix={arXiv},
          primaryClass={cs.AI},
          url={https://arxiv.org/abs/2411.04468},
    }
    
    

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/agentchat-user-guide/magentic-one.md)

[ __Show Source](../../_sources/user-guide/agentchat-user-guide/magentic-one.md.txt)