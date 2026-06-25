"""
NPC 工具集 — AutoGen 工具调用机制

将"呼叫同事"做成 tool, 让 LLM 通过结构化调用表达意图。
比 [CALL:X] 文本 tag 可靠得多 (LLM 必须显式决策, 不能"忘记")。
"""

from typing import Annotated


# ─── 主角色使用的工具 ────────────────────────────────────────


async def call_colleague(
    colleague_name: Annotated[str, "The name of the colleague NPC to call (e.g., 'Antonio')"],
    reason: Annotated[str, "Brief reason why this colleague's expertise adds value to the conversation"],
) -> str:
    """
    Call a colleague NPC to interject with their expertise.

    Use this tool when another character in the scene would add genuine value:
    - User mentions specific food or drink names
    - User asks for recommendations
    - User asks about cooking, ingredients, or flavors
    - You are about to recommend a specific dish (chef can elaborate)
    - The user is asking about something outside your role

    DO NOT use this for:
    - Basic greetings or seating
    - Bill, payment, or reservation requests
    - Clarifying questions (how many people, ready to order?)
    - Routine conversation flow

    The system will ask the user to confirm before the colleague speaks.
    Calling this tool is a STRONG signal, not optional decoration.
    """
    # 工具本身不做实际工作 — 它的"被调用"事件就是信号
    # 外层 engine.py 监听 ToolCallRequestEvent 来触发插话
    return f"Colleague '{colleague_name}' has been called. They will speak next. Reason: {reason}"