<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/reflection.html -->

# 反思#

反思是一种设计模式，其中 LLM 生成之后会进行一次反思，而反思本身又是基于第一次输出进行的另一次 LLM 生成。例如，给定一个编写代码的任务，第一个 LLM 可以生成一个代码片段，第二个 LLM 可以生成对该代码片段的批评。

在 AutoGen 和代理的上下文中，反思可以实现为一对代理，其中第一个代理生成消息，第二个代理生成对该消息的响应。两个代理继续交互，直到达到停止条件，例如最大迭代次数或第二个代理的批准。

让我们使用 AutoGen 代理实现一个简单的反思设计模式。这里将有两个代理：一个编码员代理和一个审查员代理，编码员代理将生成代码片段，审查员代理将生成对该代码片段的批评。

## 消息协议#

在定义代理之前，我们需要先为代理定义消息协议。
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class CodeWritingTask:
        task: str
    
    
    @dataclass
    class CodeWritingResult:
        task: str
        code: str
        review: str
    
    
    @dataclass
    class CodeReviewTask:
        session_id: str
        code_writing_task: str
        code_writing_scratchpad: str
        code: str
    
    
    @dataclass
    class CodeReviewResult:
        review: str
        session_id: str
        approved: bool
    

上述消息集合定义了我们的示例反思设计模式的协议：

  * 应用程序向编码员代理发送 `CodeWritingTask` 消息

  * 编码员代理生成 `CodeReviewTask` 消息，该消息被发送到审查员代理

  * 审查员代理生成 `CodeReviewResult` 消息，该消息被发送回编码员代理

  * 根据 `CodeReviewResult` 消息，如果代码被批准，编码员代理将 `CodeWritingResult` 消息发送回应用程序，否则，编码员代理将另一个 `CodeReviewTask` 消息发送给审查员代理，然后该过程继续进行。

我们可以使用数据流图来可视化消息协议：

![coder-reviewer data flow](../../../_images/coder-reviewer-data-flow.svg)

## 代理#

现在，让我们为反思设计模式定义代理。
    
    
    import json
    import re
    import uuid
    from typing import Dict, List, Union
    
    from autogen_core import MessageContext, RoutedAgent, TopicId, default_subscription, message_handler
    from autogen_core.models import (
        AssistantMessage,
        ChatCompletionClient,
        LLMMessage,
        SystemMessage,
        UserMessage,
    )
    

我们使用 [Broadcast](../framework/message-and-communication.html#broadcast) API 来实现设计模式。代理实现发布/订阅模型。编码员代理订阅 `CodeWritingTask` 和 `CodeReviewResult` 消息，并发布 `CodeReviewTask` 和 `CodeWritingResult` 消息。
    
    
    @default_subscription
    class CoderAgent(RoutedAgent):
        """An agent that performs code writing tasks."""
    
        def __init__(self, model_client: ChatCompletionClient) -> None:
            super().__init__("A code writing agent.")
            self._system_messages: List[LLMMessage] = [
                SystemMessage(
                    content="""You are a proficient coder. You write code to solve problems.
    Work with the reviewer to improve your code.
    Always put all finished code in a single Markdown code block.
    For example:
    ```python
    def hello_world():
        print("Hello, World!")
    ```
    
    Respond using the following format:
    
    Thoughts: <Your comments>
    Code: <Your code>
    """,
                )
            ]
            self._model_client = model_client
            self._session_memory: Dict[str, List[CodeWritingTask | CodeReviewTask | CodeReviewResult]] = {}
    
        @message_handler
        async def handle_code_writing_task(self, message: CodeWritingTask, ctx: MessageContext) -> None:
            # Store the messages in a temporary memory for this request only.
            session_id = str(uuid.uuid4())
            self._session_memory.setdefault(session_id, []).append(message)
            # Generate a response using the chat completion API.
            response = await self._model_client.create(
                self._system_messages + [UserMessage(content=message.task, source=self.metadata["type"])],
                cancellation_token=ctx.cancellation_token,
            )
            assert isinstance(response.content, str)
            # Extract the code block from the response.
            code_block = self._extract_code_block(response.content)
            if code_block is None:
                raise ValueError("Code block not found.")
            # Create a code review task.
            code_review_task = CodeReviewTask(
                session_id=session_id,
                code_writing_task=message.task,
                code_writing_scratchpad=response.content,
                code=code_block,
            )
            # Store the code review task in the session memory.
            self._session_memory[session_id].append(code_review_task)
            # Publish a code review task.
            await self.publish_message(code_review_task, topic_id=TopicId("default", self.id.key))
    
        @message_handler
        async def handle_code_review_result(self, message: CodeReviewResult, ctx: MessageContext) -> None:
            # Store the review result in the session memory.
            self._session_memory[message.session_id].append(message)
            # Obtain the request from previous messages.
            review_request = next(
                m for m in reversed(self._session_memory[message.session_id]) if isinstance(m, CodeReviewTask)
            )
            assert review_request is not None
            # Check if the code is approved.
            if message.approved:
                # Publish the code writing result.
                await self.publish_message(
                    CodeWritingResult(
                        code=review_request.code,
                        task=review_request.code_writing_task,
                        review=message.review,
                    ),
                    topic_id=TopicId("default", self.id.key),
                )
                print("Code Writing Result:")
                print("-" * 80)
                print(f"Task:\n{review_request.code_writing_task}")
                print("-" * 80)
                print(f"Code:\n{review_request.code}")
                print("-" * 80)
                print(f"Review:\n{message.review}")
                print("-" * 80)
            else:
                # Create a list of LLM messages to send to the model.
                messages: List[LLMMessage] = [*self._system_messages]
                for m in self._session_memory[message.session_id]:
                    if isinstance(m, CodeReviewResult):
                        messages.append(UserMessage(content=m.review, source="Reviewer"))
                    elif isinstance(m, CodeReviewTask):
                        messages.append(AssistantMessage(content=m.code_writing_scratchpad, source="Coder"))
                    elif isinstance(m, CodeWritingTask):
                        messages.append(UserMessage(content=m.task, source="User"))
                    else:
                        raise ValueError(f"Unexpected message type: {m}")
                # Generate a revision using the chat completion API.
                response = await self._model_client.create(messages, cancellation_token=ctx.cancellation_token)
                assert isinstance(response.content, str)
                # Extract the code block from the response.
                code_block = self._extract_code_block(response.content)
                if code_block is None:
                    raise ValueError("Code block not found.")
                # Create a new code review task.
                code_review_task = CodeReviewTask(
                    session_id=message.session_id,
                    code_writing_task=review_request.code_writing_task,
                    code_writing_scratchpad=response.content,
                    code=code_block,
                )
                # Store the code review task in the session memory.
                self._session_memory[message.session_id].append(code_review_task)
                # Publish a new code review task.
                await self.publish_message(code_review_task, topic_id=TopicId("default", self.id.key))
    
        def _extract_code_block(self, markdown_text: str) -> Union[str, None]:
            pattern = r"```(\w+)\n(.*?)\n```"
            # Search for the pattern in the markdown text
            match = re.search(pattern, markdown_text, re.DOTALL)
            # Extract the language and code block if a match is found
            if match:
                return match.group(2)
            return None
    

关于 `CoderAgent` 有几点需要注意：

  * 它在其系统消息中使用了思维链提示。

  * 它在字典中存储不同 `CodeWritingTask` 的消息历史记录，因此每个任务都有自己的历史记录。

  * 当使用其模型客户端发出 LLM 推理请求时，它会将消息历史记录转换为 `autogen_core.models.LLMMessage` 对象列表以传递给模型客户端。

审查员代理订阅 `CodeReviewTask` 消息并发布 `CodeReviewResult` 消息。
    
    
    @default_subscription
    class ReviewerAgent(RoutedAgent):
        """An agent that performs code review tasks."""
    
        def __init__(self, model_client: ChatCompletionClient) -> None:
            super().__init__("A code reviewer agent.")
            self._system_messages: List[LLMMessage] = [
                SystemMessage(
                    content="""You are a code reviewer. You focus on correctness, efficiency and safety of the code.
    Respond using the following JSON format:
    {
        "correctness": "<Your comments>",
        "efficiency": "<Your comments>",
        "safety": "<Your comments>",
        "approval": "<APPROVE or REVISE>",
        "suggested_changes": "<Your comments>"
    }
    """,
                )
            ]
            self._session_memory: Dict[str, List[CodeReviewTask | CodeReviewResult]] = {}
            self._model_client = model_client
    
        @message_handler
        async def handle_code_review_task(self, message: CodeReviewTask, ctx: MessageContext) -> None:
            # Format the prompt for the code review.
            # Gather the previous feedback if available.
            previous_feedback = ""
            if message.session_id in self._session_memory:
                previous_review = next(
                    (m for m in reversed(self._session_memory[message.session_id]) if isinstance(m, CodeReviewResult)),
                    None,
                )
                if previous_review is not None:
                    previous_feedback = previous_review.review
            # Store the messages in a temporary memory for this request only.
            self._session_memory.setdefault(message.session_id, []).append(message)
            prompt = f"""The problem statement is: {message.code_writing_task}
    The code is:
    ```
    {message.code}
    ```
    
    Previous feedback:
    {previous_feedback}
    
    Please review the code. If previous feedback was provided, see if it was addressed.
    """
            # Generate a response using the chat completion API.
            response = await self._model_client.create(
                self._system_messages + [UserMessage(content=prompt, source=self.metadata["type"])],
                cancellation_token=ctx.cancellation_token,
                json_output=True,
            )
            assert isinstance(response.content, str)
            # TODO: use structured generation library e.g. guidance to ensure the response is in the expected format.
            # Parse the response JSON.
            review = json.loads(response.content)
            # Construct the review text.
            review_text = "Code review:\n" + "\n".join([f"{k}: {v}" for k, v in review.items()])
            approved = review["approval"].lower().strip() == "approve"
            result = CodeReviewResult(
                review=review_text,
                session_id=message.session_id,
                approved=approved,
            )
            # Store the review result in the session memory.
            self._session_memory[message.session_id].append(result)
            # Publish the review result.
            await self.publish_message(result, topic_id=TopicId("default", self.id.key))
    

`ReviewerAgent` 在发出 LLM 推理请求时使用 JSON 模式，并且在其系统消息中也使用了思维链提示。

## 日志#

开启日志记录以查看代理之间交换的消息。
    
    
    import logging
    
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("autogen_core").setLevel(logging.DEBUG)
    

## 运行设计模式#

让我们用一个编码任务测试设计模式。由于所有代理都使用 `default_subscription()` 类装饰器进行了装饰，因此在创建代理时它们将自动订阅默认主题。我们向默认主题发布 `CodeWritingTask` 消息以启动反思过程。
    
    
    from autogen_core import DefaultTopicId, SingleThreadedAgentRuntime
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    runtime = SingleThreadedAgentRuntime()
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    await ReviewerAgent.register(runtime, "ReviewerAgent", lambda: ReviewerAgent(model_client=model_client))
    await CoderAgent.register(runtime, "CoderAgent", lambda: CoderAgent(model_client=model_client))
    runtime.start()
    await runtime.publish_message(
        message=CodeWritingTask(task="Write a function to find the sum of all even numbers in a list."),
        topic_id=DefaultTopicId(),
    )
    
    # Keep processing messages until idle.
    await runtime.stop_when_idle()
    # Close the model client.
    await model_client.close()
    
    
    
    INFO:autogen_core:Publishing message of type CodeWritingTask to all subscribers: {'task': 'Write a function to find the sum of all even numbers in a list.'}
    INFO:autogen_core:Calling message handler for ReviewerAgent with message type CodeWritingTask published by Unknown
    INFO:autogen_core:Calling message handler for CoderAgent with message type CodeWritingTask published by Unknown
    INFO:autogen_core:Unhandled message: CodeWritingTask(task='Write a function to find the sum of all even numbers in a list.')
    INFO:autogen_core.events:{"prompt_tokens": 101, "completion_tokens": 88, "type": "LLMCall"}
    INFO:autogen_core:Publishing message of type CodeReviewTask to all subscribers: {'session_id': '51db93d5-3e29-4b7f-9f96-77be7bb02a5e', 'code_writing_task': 'Write a function to find the sum of all even numbers in a list.', 'code_writing_scratchpad': 'Thoughts: To find the sum of all even numbers in a list, we can use a list comprehension to filter out the even numbers and then use the `sum()` function to calculate their total. The implementation should handle edge cases like an empty list or a list with no even numbers.\n\nCode:\n```python\ndef sum_of_even_numbers(numbers):\n    return sum(num for num in numbers if num % 2 == 0)\n```', 'code': 'def sum_of_even_numbers(numbers):\n    return sum(num for num in numbers if num % 2 == 0)'}
    INFO:autogen_core:Calling message handler for ReviewerAgent with message type CodeReviewTask published by CoderAgent:default
    INFO:autogen_core.events:{"prompt_tokens": 163, "completion_tokens": 235, "type": "LLMCall"}
    INFO:autogen_core:Publishing message of type CodeReviewResult to all subscribers: {'review': "Code review:\ncorrectness: The function correctly identifies and sums all even numbers in the provided list. The use of a generator expression ensures that only even numbers are processed, which is correct.\nefficiency: The function is efficient as it utilizes a generator expression that avoids creating an intermediate list, therefore using less memory. The time complexity is O(n) where n is the number of elements in the input list, which is optimal for this task.\nsafety: The function does not include checks for input types. If a non-iterable or a list containing non-integer types is passed, it could lead to unexpected behavior or errors. It’s advisable to handle such cases.\napproval: REVISE\nsuggested_changes: Consider adding input validation to ensure that 'numbers' is a list and contains only integers. You could raise a ValueError if the input is invalid. Example: 'if not isinstance(numbers, list) or not all(isinstance(num, int) for num in numbers): raise ValueError('Input must be a list of integers')'. This will make the function more robust.", 'session_id': '51db93d5-3e29-4b7f-9f96-77be7bb02a5e', 'approved': False}
    INFO:autogen_core:Calling message handler for CoderAgent with message type CodeReviewResult published by ReviewerAgent:default
    INFO:autogen_core.events:{"prompt_tokens": 421, "completion_tokens": 119, "type": "LLMCall"}
    INFO:autogen_core:Publishing message of type CodeReviewTask to all subscribers: {'session_id': '51db93d5-3e29-4b7f-9f96-77be7bb02a5e', 'code_writing_task': 'Write a function to find the sum of all even numbers in a list.', 'code_writing_scratchpad': "Thoughts: I appreciate the reviewer's feedback on input validation. Adding type checks ensures that the function can handle unexpected inputs gracefully. I will implement the suggested changes and include checks for both the input type and the elements within the list to confirm that they are integers.\n\nCode:\n```python\ndef sum_of_even_numbers(numbers):\n    if not isinstance(numbers, list) or not all(isinstance(num, int) for num in numbers):\n        raise ValueError('Input must be a list of integers')\n    \n    return sum(num for num in numbers if num % 2 == 0)\n```", 'code': "def sum_of_even_numbers(numbers):\n    if not isinstance(numbers, list) or not all(isinstance(num, int) for num in numbers):\n        raise ValueError('Input must be a list of integers')\n    \n    return sum(num for num in numbers if num % 2 == 0)"}
    INFO:autogen_core:Calling message handler for ReviewerAgent with message type CodeReviewTask published by CoderAgent:default
    INFO:autogen_core.events:{"prompt_tokens": 420, "completion_tokens": 153, "type": "LLMCall"}
    INFO:autogen_core:Publishing message of type CodeReviewResult to all subscribers: {'review': 'Code review:\ncorrectness: The function correctly sums all even numbers in the provided list. It raises a ValueError if the input is not a list of integers, which is a necessary check for correctness.\nefficiency: The function remains efficient with a time complexity of O(n) due to the use of a generator expression. There are no unnecessary intermediate lists created, so memory usage is optimal.\nsafety: The function includes input validation, which enhances safety by preventing incorrect input types. It raises a ValueError for invalid inputs, making the function more robust against unexpected data.\napproval: APPROVE\nsuggested_changes: No further changes are necessary as the previous feedback has been adequately addressed.', 'session_id': '51db93d5-3e29-4b7f-9f96-77be7bb02a5e', 'approved': True}
    INFO:autogen_core:Calling message handler for CoderAgent with message type CodeReviewResult published by ReviewerAgent:default
    INFO:autogen_core:Publishing message of type CodeWritingResult to all subscribers: {'task': 'Write a function to find the sum of all even numbers in a list.', 'code': "def sum_of_even_numbers(numbers):\n    if not isinstance(numbers, list) or not all(isinstance(num, int) for num in numbers):\n        raise ValueError('Input must be a list of integers')\n    \n    return sum(num for num in numbers if num % 2 == 0)", 'review': 'Code review:\ncorrectness: The function correctly sums all even numbers in the provided list. It raises a ValueError if the input is not a list of integers, which is a necessary check for correctness.\nefficiency: The function remains efficient with a time complexity of O(n) due to the use of a generator expression. There are no unnecessary intermediate lists created, so memory usage is optimal.\nsafety: The function includes input validation, which enhances safety by preventing incorrect input types. It raises a ValueError for invalid inputs, making the function more robust against unexpected data.\napproval: APPROVE\nsuggested_changes: No further changes are necessary as the previous feedback has been adequately addressed.'}
    INFO:autogen_core:Calling message handler for ReviewerAgent with message type CodeWritingResult published by CoderAgent:default
    INFO:autogen_core:Unhandled message: CodeWritingResult(task='Write a function to find the sum of all even numbers in a list.', code="def sum_of_even_numbers(numbers):\n    if not isinstance(numbers, list) or not all(isinstance(num, int) for num in numbers):\n        raise ValueError('Input must be a list of integers')\n    \n    return sum(num for num in numbers if num % 2 == 0)", review='Code review:\ncorrectness: The function correctly sums all even numbers in the provided list. It raises a ValueError if the input is not a list of integers, which is a necessary check for correctness.\nefficiency: The function remains efficient with a time complexity of O(n) due to the use of a generator expression. There are no unnecessary intermediate lists created, so memory usage is optimal.\nsafety: The function includes input validation, which enhances safety by preventing incorrect input types. It raises a ValueError for invalid inputs, making the function more robust against unexpected data.\napproval: APPROVE\nsuggested_changes: No further changes are necessary as the previous feedback has been adequately addressed.')
    
    
    
    Code Writing Result:
    --------------------------------------------------------------------------------
    Task:
    Write a function to find the sum of all even numbers in a list.
    --------------------------------------------------------------------------------
    Code:
    def sum_of_even_numbers(numbers):
        if not isinstance(numbers, list) or not all(isinstance(num, int) for num in numbers):
            raise ValueError('Input must be a list of integers')
        
        return sum(num for num in numbers if num % 2 == 0)
    --------------------------------------------------------------------------------
    Review:
    Code review:
    correctness: The function correctly sums all even numbers in the provided list. It raises a ValueError if the input is not a list of integers, which is a necessary check for correctness.
    efficiency: The function remains efficient with a time complexity of O(n) due to the use of a generator expression. There are no unnecessary intermediate lists created, so memory usage is optimal.
    safety: The function includes input validation, which enhances safety by preventing incorrect input types. It raises a ValueError for invalid inputs, making the function more robust against unexpected data.
    approval: APPROVE
    suggested_changes: No further changes are necessary as the previous feedback has been adequately addressed.
    --------------------------------------------------------------------------------
    

日志消息显示了编码员和审查员代理之间的交互。最终输出显示了编码员代理生成的代码片段以及审查员代理生成的批评。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/core-user-guide/design-patterns/reflection.ipynb)

[ __Show Source](../../../_sources/user-guide/core-user-guide/design-patterns/reflection.ipynb.txt)
