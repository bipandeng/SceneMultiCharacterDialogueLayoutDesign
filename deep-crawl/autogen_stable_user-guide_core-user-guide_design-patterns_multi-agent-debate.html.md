<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/multi-agent-debate.html -->

# 多智能体辩论#

多智能体辩论(Multi-Agent Debate)是一种多智能体设计模式,它模拟了一种多轮交互,在每一轮中,智能体相互交换各自的回答,并根据其他智能体的回答对自己的回答进行迭代优化。

本示例展示了针对 [GSM8K 基准测试](https://huggingface.co/datasets/openai/gsm8k) 中数学问题的多智能体辩论模式的实现。

该模式包含两类智能体:solver(求解器)智能体和 aggregator(聚合器)智能体。Solver 智能体按照 [Improving Multi-Agent Debate with Sparse Communication Topology](https://arxiv.org/abs/2406.11776) 中所描述的技术,以稀疏方式相互连接。Solver 智能体负责求解数学问题,并相互交换回答。Aggregator 智能体负责将数学问题分发给 solver 智能体,等待它们的最终回答,并将这些回答聚合以得到最终答案。

该模式的工作方式如下:

  1. 用户将数学问题发送给 aggregator 智能体。

  2. Aggregator 智能体将该问题分发给 solver 智能体。

  3. 每个 solver 智能体处理该问题,并向其邻居发布一次回答。

  4. 每个 solver 智能体根据邻居的回答对自己的回答进行优化,并发布一条新的回答。

  5. 重复步骤 4 固定轮数。在最后一轮中,每个 solver 智能体发布最终回答。

  6. Aggregator 智能体通过多数投票(majority voting)对所有 solver 智能体的最终回答进行聚合,以得出最终答案,并发布该答案。

我们将使用广播 API,即 [`publish_message()`](../../../reference/python/autogen_core.html#autogen_core.BaseAgent.publish_message "autogen_core.BaseAgent.publish_message"),并使用 topic 和 subscription 来实现通信拓扑。请阅读 [Topics and Subscriptions](../core-concepts/topic-and-subscription.html) 以了解其工作原理。
    
    
    import re
    from dataclasses import dataclass
    from typing import Dict, List
    
    from autogen_core import (
        DefaultTopicId,
        MessageContext,
        RoutedAgent,
        SingleThreadedAgentRuntime,
        TypeSubscription,
        default_subscription,
        message_handler,
    )
    from autogen_core.models import (
        AssistantMessage,
        ChatCompletionClient,
        LLMMessage,
        SystemMessage,
        UserMessage,
    )
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    

## 消息协议#

首先,我们定义智能体所使用的消息。`IntermediateSolverResponse` 是 solver 智能体在每一轮中相互交换的消息,`FinalSolverResponse` 是 solver 智能体在最后一轮中发布的消息。
    
    
    @dataclass
    class Question:
        content: str
    
    
    @dataclass
    class Answer:
        content: str
    
    
    @dataclass
    class SolverRequest:
        content: str
        question: str
    
    
    @dataclass
    class IntermediateSolverResponse:
        content: str
        question: str
        answer: str
        round: int
    
    
    @dataclass
    class FinalSolverResponse:
        answer: str
    

## Solver 智能体#

Solver 智能体负责求解数学问题,并与其他 solver 智能体交换回答。在收到 `SolverRequest` 后,solver 智能体会使用 LLM 生成一个答案。然后,它会根据当前的轮次发布一条 `IntermediateSolverResponse` 或 `FinalSolverResponse`。

Solver 智能体会获得一个主题类型,该类型用于指明该智能体应将中间回答发布到哪个主题。Solver 的邻居会订阅该主题以接收来自该智能体的回答——我们稍后会展示如何完成这一设置。

我们使用 `default_subscription()` 让 solver 智能体订阅默认主题,该默认主题供 aggregator 智能体收集所有 solver 智能体的最终回答。
    
    
    @default_subscription
    class MathSolver(RoutedAgent):
        def __init__(self, model_client: ChatCompletionClient, topic_type: str, num_neighbors: int, max_round: int) -> None:
            super().__init__("A debator.")
            self._topic_type = topic_type
            self._model_client = model_client
            self._num_neighbors = num_neighbors
            self._history: List[LLMMessage] = []
            self._buffer: Dict[int, List[IntermediateSolverResponse]] = {}
            self._system_messages = [
                SystemMessage(
                    content=(
                        "You are a helpful assistant with expertise in mathematics and reasoning. "
                        "Your task is to assist in solving a math reasoning problem by providing "
                        "a clear and detailed solution. Limit your output within 100 words, "
                        "and your final answer should be a single numerical number, "
                        "in the form of {{answer}}, at the end of your response. "
                        "For example, 'The answer is {{42}}.'"
                    )
                )
            ]
            self._round = 0
            self._max_round = max_round
    
        @message_handler
        async def handle_request(self, message: SolverRequest, ctx: MessageContext) -> None:
            # Add the question to the memory.
            self._history.append(UserMessage(content=message.content, source="user"))
            # Make an inference using the model.
            model_result = await self._model_client.create(self._system_messages + self._history)
            assert isinstance(model_result.content, str)
            # Add the response to the memory.
            self._history.append(AssistantMessage(content=model_result.content, source=self.metadata["type"]))
            print(f"{'-'*80}\nSolver {self.id} round {self._round}:\n{model_result.content}")
            # Extract the answer from the response.
            match = re.search(r"\{\{(\-?\d+(\.\d+)?)\}\}", model_result.content)
            if match is None:
                raise ValueError("The model response does not contain the answer.")
            answer = match.group(1)
            # Increment the counter.
            self._round += 1
            if self._round == self._max_round:
                # If the counter reaches the maximum round, publishes a final response.
                await self.publish_message(FinalSolverResponse(answer=answer), topic_id=DefaultTopicId())
            else:
                # Publish intermediate response to the topic associated with this solver.
                await self.publish_message(
                    IntermediateSolverResponse(
                        content=model_result.content,
                        question=message.question,
                        answer=answer,
                        round=self._round,
                    ),
                    topic_id=DefaultTopicId(type=self._topic_type),
                )
    
        @message_handler
        async def handle_response(self, message: IntermediateSolverResponse, ctx: MessageContext) -> None:
            # Add neighbor's response to the buffer.
            self._buffer.setdefault(message.round, []).append(message)
            # Check if all neighbors have responded.
            if len(self._buffer[message.round]) == self._num_neighbors:
                print(
                    f"{'-'*80}\nSolver {self.id} round {message.round}:\nReceived all responses from {self._num_neighbors} neighbors."
                )
                # Prepare the prompt for the next question.
                prompt = "These are the solutions to the problem from other agents:\n"
                for resp in self._buffer[message.round]:
                    prompt += f"One agent solution: {resp.content}\n"
                prompt += (
                    "Using the solutions from other agents as additional information, "
                    "can you provide your answer to the math problem? "
                    f"The original math problem is {message.question}. "
                    "Your final answer should be a single numerical number, "
                    "in the form of {{answer}}, at the end of your response."
                )
                # Send the question to the agent itself to solve.
                await self.send_message(SolverRequest(content=prompt, question=message.question), self.id)
                # Clear the buffer.
                self._buffer.pop(message.round)
    

## Aggregator 智能体#

Aggregator 智能体负责处理用户的问题,并将数学问题分发给 solver 智能体。

Aggregator 使用 `default_subscription()` 订阅默认主题。默认主题用于接收用户的问题、接收来自 solver 智能体的最终回答,并将最终答案发布回用户。

在更复杂的应用中,当你希望将多智能体辩论隔离为一个子组件时,你应当使用 `type_subscription()` 为 aggregator-solver 之间的通信设置一个特定的主题类型,并让 solver 和 aggregator 都发布和订阅该主题类型。
    
    
    @default_subscription
    class MathAggregator(RoutedAgent):
        def __init__(self, num_solvers: int) -> None:
            super().__init__("Math Aggregator")
            self._num_solvers = num_solvers
            self._buffer: List[FinalSolverResponse] = []
    
        @message_handler
        async def handle_question(self, message: Question, ctx: MessageContext) -> None:
            print(f"{'-'*80}\nAggregator {self.id} received question:\n{message.content}")
            prompt = (
                f"Can you solve the following math problem?\n{message.content}\n"
                "Explain your reasoning. Your final answer should be a single numerical number, "
                "in the form of {{answer}}, at the end of your response."
            )
            print(f"{'-'*80}\nAggregator {self.id} publishes initial solver request.")
            await self.publish_message(SolverRequest(content=prompt, question=message.content), topic_id=DefaultTopicId())
    
        @message_handler
        async def handle_final_solver_response(self, message: FinalSolverResponse, ctx: MessageContext) -> None:
            self._buffer.append(message)
            if len(self._buffer) == self._num_solvers:
                print(f"{'-'*80}\nAggregator {self.id} received all final answers from {self._num_solvers} solvers.")
                # Find the majority answer.
                answers = [resp.answer for resp in self._buffer]
                majority_answer = max(set(answers), key=answers.count)
                # Publish the aggregated response.
                await self.publish_message(Answer(content=majority_answer), topic_id=DefaultTopicId())
                # Clear the responses.
                self._buffer.clear()
                print(f"{'-'*80}\nAggregator {self.id} publishes final answer:\n{majority_answer}")
    

## 搭建一场辩论#

现在我们将搭建一个由 4 个 solver 智能体和 1 个 aggregator 智能体组成的多智能体辩论。Solver 智能体将如下图所示以稀疏方式相互连接:
    
    
    A --- B
    |     |
    |     |
    D --- C
    

每个 solver 智能体都与其他两个 solver 智能体相连。例如,智能体 A 与智能体 B 和 C 相连。

我们首先创建一个 runtime 并注册智能体类型。
    
    
    runtime = SingleThreadedAgentRuntime()
    
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    
    await MathSolver.register(
        runtime,
        "MathSolverA",
        lambda: MathSolver(
            model_client=model_client,
            topic_type="MathSolverA",
            num_neighbors=2,
            max_round=3,
        ),
    )
    await MathSolver.register(
        runtime,
        "MathSolverB",
        lambda: MathSolver(
            model_client=model_client,
            topic_type="MathSolverB",
            num_neighbors=2,
            max_round=3,
        ),
    )
    await MathSolver.register(
        runtime,
        "MathSolverC",
        lambda: MathSolver(
            model_client=model_client,
            topic_type="MathSolverC",
            num_neighbors=2,
            max_round=3,
        ),
    )
    await MathSolver.register(
        runtime,
        "MathSolverD",
        lambda: MathSolver(
            model_client=model_client,
            topic_type="MathSolverD",
            num_neighbors=2,
            max_round=3,
        ),
    )
    await MathAggregator.register(runtime, "MathAggregator", lambda: MathAggregator(num_solvers=4))
    
    
    
    AgentType(type='MathAggregator')
    

现在我们将使用 `TypeSubscription` 创建 solver 智能体的拓扑结构,它将每个 solver 智能体的发布主题类型映射到其邻居的智能体类型。
    
    
    # Subscriptions for topic published to by MathSolverA.
    await runtime.add_subscription(TypeSubscription("MathSolverA", "MathSolverD"))
    await runtime.add_subscription(TypeSubscription("MathSolverA", "MathSolverB"))
    
    # Subscriptions for topic published to by MathSolverB.
    await runtime.add_subscription(TypeSubscription("MathSolverB", "MathSolverA"))
    await runtime.add_subscription(TypeSubscription("MathSolverB", "MathSolverC"))
    
    # Subscriptions for topic published to by MathSolverC.
    await runtime.add_subscription(TypeSubscription("MathSolverC", "MathSolverB"))
    await runtime.add_subscription(TypeSubscription("MathSolverC", "MathSolverD"))
    
    # Subscriptions for topic published to by MathSolverD.
    await runtime.add_subscription(TypeSubscription("MathSolverD", "MathSolverC"))
    await runtime.add_subscription(TypeSubscription("MathSolverD", "MathSolverA"))
    
    # All solvers and the aggregator subscribe to the default topic.
    

## 求解数学问题#

现在让我们运行辩论来求解一道数学题。我们将一条 `SolverRequest` 发布到默认主题,aggregator 智能体将开启这场辩论。
    
    
    question = "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"
    runtime.start()
    await runtime.publish_message(Question(content=question), DefaultTopicId())
    # Wait for the runtime to stop when idle.
    await runtime.stop_when_idle()
    # Close the connection to the model client.
    await model_client.close()
    
    
    
    --------------------------------------------------------------------------------
    Aggregator MathAggregator:default received question:
    Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
    --------------------------------------------------------------------------------
    Aggregator MathAggregator:default publishes initial solver request.
    --------------------------------------------------------------------------------
    Solver MathSolverC:default round 0:
    In April, Natalia sold 48 clips. In May, she sold half as many, which is 48 / 2 = 24 clips. To find the total number of clips sold in April and May, we add the amounts: 48 (April) + 24 (May) = 72 clips. 
    
    Thus, the total number of clips sold by Natalia is {{72}}.
    --------------------------------------------------------------------------------
    Solver MathSolverB:default round 0:
    In April, Natalia sold 48 clips. In May, she sold half as many clips, which is 48 / 2 = 24 clips. To find the total clips sold in April and May, we add both amounts: 
    
    48 (April) + 24 (May) = 72.
    
    Thus, the total number of clips sold altogether is {{72}}.
    --------------------------------------------------------------------------------
    Solver MathSolverD:default round 0:
    Natalia sold 48 clips in April. In May, she sold half as many, which is \( \frac{48}{2} = 24 \) clips. To find the total clips sold in both months, we add the clips sold in April and May together:
    
    \[ 48 + 24 = 72 \]
    
    Thus, Natalia sold a total of 72 clips.
    
    The answer is {{72}}.
    --------------------------------------------------------------------------------
    Solver MathSolverC:default round 1:
    Received all responses from 2 neighbors.
    --------------------------------------------------------------------------------
    Solver MathSolverA:default round 1:
    Received all responses from 2 neighbors.
    --------------------------------------------------------------------------------
    Solver MathSolverA:default round 0:
    In April, Natalia sold clips to 48 friends. In May, she sold half as many, which is calculated as follows:
    
    Half of 48 is \( 48 \div 2 = 24 \).
    
    Now, to find the total clips sold in April and May, we add the totals from both months:
    
    \( 48 + 24 = 72 \).
    
    Thus, the total number of clips Natalia sold altogether in April and May is {{72}}.
    --------------------------------------------------------------------------------
    Solver MathSolverD:default round 1:
    Received all responses from 2 neighbors.
    --------------------------------------------------------------------------------
    Solver MathSolverB:default round 1:
    Received all responses from 2 neighbors.
    --------------------------------------------------------------------------------
    Solver MathSolverC:default round 1:
    In April, Natalia sold 48 clips. In May, she sold half as many, which is 48 / 2 = 24 clips. The total number of clips sold in April and May is calculated by adding the two amounts: 48 (April) + 24 (May) = 72 clips. 
    
    Therefore, the answer is {{72}}.
    --------------------------------------------------------------------------------
    Solver MathSolverA:default round 1:
    In April, Natalia sold 48 clips. In May, she sold half of that amount, which is 48 / 2 = 24 clips. To find the total clips sold in both months, we sum the clips from April and May: 
    
    48 (April) + 24 (May) = 72.
    
    Thus, Natalia sold a total of {{72}} clips. 
    
    The answer is {{72}}.
    --------------------------------------------------------------------------------
    Solver MathSolverD:default round 2:
    Received all responses from 2 neighbors.
    --------------------------------------------------------------------------------
    Solver MathSolverB:default round 2:
    Received all responses from 2 neighbors.
    --------------------------------------------------------------------------------
    Solver MathSolverD:default round 1:
    Natalia sold 48 clips in April. In May, she sold half of that, which is \( 48 \div 2 = 24 \) clips. To find the total clips sold, we add the clips sold in both months:
    
    \[ 48 + 24 = 72 \]
    
    Therefore, the total number of clips sold by Natalia is {{72}}.
    --------------------------------------------------------------------------------
    Solver MathSolverB:default round 1:
    In April, Natalia sold 48 clips. In May, she sold half that amount, which is 48 / 2 = 24 clips. To find the total clips sold in both months, we add the amounts: 
    
    48 (April) + 24 (May) = 72.
    
    Therefore, the total number of clips sold altogether by Natalia is {{72}}.
    --------------------------------------------------------------------------------
    Solver MathSolverA:default round 2:
    Received all responses from 2 neighbors.
    --------------------------------------------------------------------------------
    Solver MathSolverC:default round 2:
    Received all responses from 2 neighbors.
    --------------------------------------------------------------------------------
    Solver MathSolverA:default round 2:
    In April, Natalia sold 48 clips. In May, she sold half of that amount, which is \( 48 \div 2 = 24 \) clips. To find the total clips sold in both months, we add the amounts from April and May:
    
    \( 48 + 24 = 72 \).
    
    Thus, the total number of clips sold by Natalia is {{72}}.
    --------------------------------------------------------------------------------
    Solver MathSolverC:default round 2:
    In April, Natalia sold 48 clips. In May, she sold half of that amount, which is \( 48 \div 2 = 24 \) clips. To find the total number of clips sold in both months, we add the clips sold in April and May: 
    
    48 (April) + 24 (May) = 72. 
    
    Thus, the total number of clips sold altogether by Natalia is {{72}}.
    --------------------------------------------------------------------------------
    Solver MathSolverB:default round 2:
    In April, Natalia sold 48 clips. In May, she sold half as many, calculated as \( 48 \div 2 = 24 \) clips. To find the total clips sold over both months, we sum the totals: 
    
    \( 48 (April) + 24 (May) = 72 \).
    
    Therefore, the total number of clips Natalia sold is {{72}}.
    --------------------------------------------------------------------------------
    Solver MathSolverD:default round 2:
    To solve the problem, we know that Natalia sold 48 clips in April. In May, she sold half that amount, which is calculated as \( 48 \div 2 = 24 \) clips. To find the total number of clips sold over both months, we add the two amounts together:
    
    \[ 48 + 24 = 72 \]
    
    Thus, the total number of clips sold by Natalia is {{72}}.
    --------------------------------------------------------------------------------
    Aggregator MathAggregator:default received all final answers from 4 solvers.
    --------------------------------------------------------------------------------
    Aggregator MathAggregator:default publishes final answer:
    72
    

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/design-patterns/multi-agent-debate.ipynb)

[ __Show Source](../../../_sources/user-guide/core-user-guide/design-patterns/multi-agent-debate.ipynb.txt)