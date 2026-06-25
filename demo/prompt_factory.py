"""
Prompt 工厂 — 7 模块拼装 system_message

基于 CAMEL Inception Prompting 思想，为每个 NPC agent 组装 system_message。

模块结构:
  ① Identity — 角色名 + persona + "NOT an AI"
  ② Scene Context — 场景设定 + 氛围
  ③ Mission — 目标词 + 目标句型 + "自然嵌入"
  ④ Old Friends — 用户收藏的相关词 + "自然 revisit"
  ⑤ CEFR Constraint — 难度约束
  ⑥ Interaction Rules — 短句/不教学/不打破角色
  ⑦ Scene Flow — 全流程 beat 概览
"""

import json

# ─── 固定模板 (不随场景变化) ───────────────────────────────────────

CEFR_TEMPLATES = {
    "A1": "Use very simple English. Short sentences. Basic words only. Speak slowly and clearly.",
    "A2": "Use simple English. Short sentences. Everyday vocabulary. Avoid complex grammar.",
    "B1": "Use intermediate English. Mix of simple and compound sentences. Everyday vocabulary + some topic-specific words.",
    "B2": "Use upper-intermediate English. Varied sentence structures. Can include idiomatic expressions.",
    "C1": "Use advanced English. Complex structures. Nuanced vocabulary. Natural idioms and phrasal verbs.",
    "C2": "Use near-native English. Sophisticated vocabulary. Subtle nuances. Academic or literary expressions when appropriate.",
}

INTERACTION_RULES = """1. Keep responses SHORT: 1-2 sentences max per turn.
2. Be natural. No "Great job!", no "That's correct!", no teacher-like praise.
3. End with a question or conversational opening when possible.
4. Don't correct mistakes directly — restate the correct version naturally.
5. Never break character. You are NOT an AI. You are a real person in this scene."""

SCENE_FLOWS = {
    "restaurant": """This conversation has phases:
1. Greeting: Welcome the guest, seat them.
2. Ordering: Help them choose food and drinks.
3. During meal: Check if they enjoy the food.
4. Payment: Handle the bill.
5. Farewell: Say goodbye warmly.
Follow the user's lead. Focus on the current phase naturally.""",
}

# ─── Token 估算 ────────────────────────────────────────────────────


def estimate_tokens(text: str) -> int:
    """粗略估算 token 数 (英文 ~4 字符/token)"""
    return len(text) // 4


# ─── 核心: 组装 system_message ────────────────────────────────────


def build_system_message(
    character: dict,
    scene_instance: dict,
    cefr_level: str = "B1",
    old_friend_words: list[str] | None = None,
    colleagues: list[dict] | None = None,
) -> str:
    """
    为单个 NPC 角色组装完整的 system_message。

    Args:
        character: NPC 角色信息 {name, persona, bio, template_role}
        scene_instance: 场景实例 {setting, selected_vocab, selected_patterns, scene_flow_key}
        cefr_level: 用户 CEFR 等级 (A1-C2)
        old_friend_words: 用户之前收藏的相关词 (可为空)
        colleagues: 其他 NPC 信息 [{name, template_role, persona}], 用于 Director Mode

    Returns:
        完整的 system_message string
    """
    modules = []

    # ① Identity (~150 tok)
    identity = f"You are {character['name']}.\n\n{character['persona']}"
    if character.get("bio"):
        identity += f"\n\nBackground: {character['bio']}"
    identity += "\n\nYou are NOT an AI assistant. You are a real person in this scene. Stay in character at all times."
    modules.append(("Identity", identity))

    # ② Scene Context (~50 tok)
    context = f"You are currently at: {scene_instance['setting']}"
    modules.append(("Scene Context", context))

    # ③ Mission (~100 tok)
    vocab_list = ", ".join(scene_instance["selected_vocab"])
    pattern_list = "; ".join(scene_instance["selected_patterns"])
    mission = f"""Target words to naturally weave into your speech:
{vocab_list}

Target phrases to model:
{pattern_list}

IMPORTANT: Use these words NATURALLY in conversation. Do NOT list them. Do NOT say "here's a useful word". Do NOT teach."""
    modules.append(("Mission", mission))

    # ④ Old Friends (~50 tok, 可空)
    if old_friend_words:
        words_str = ", ".join(old_friend_words[:5])
        old_friends = f"""The user has learned these words/phrases before.
If it feels natural, try to revisit 1-2 of them. Do NOT force them.

Words: {words_str}"""
        modules.append(("Old Friends", old_friends))

    # ⑤ CEFR Constraint (~40 tok)
    cefr_text = CEFR_TEMPLATES.get(cefr_level, CEFR_TEMPLATES["B1"])
    modules.append(("CEFR", cefr_text))

    # ⑥ Interaction Rules (~100 tok)
    modules.append(("Rules", INTERACTION_RULES))

    # ⑦ Scene Flow (~80 tok)
    flow_key = scene_instance.get("scene_flow_key", "restaurant")
    flow_text = SCENE_FLOWS.get(flow_key, SCENE_FLOWS["restaurant"])
    modules.append(("Scene Flow", flow_text))

    # ⑧ Tool Usage (工具调用) — 主角色通过 tool 呼叫同事 (L4-006)
    if colleagues:
        colleague_lines = []
        for c in colleagues:
            colleague_lines.append(
                f"- {c['name']} ({c.get('template_role', 'staff')}) — {c.get('persona', '')[:80]}"
            )
        colleague_block = "\n".join(colleague_lines)

        tool_guidance = f"""[TOOL USAGE — colleague coordination]

You have a tool `call_colleague(colleague_name, reason)`.
This lets you bring in another character in the scene.

Available colleagues:
{colleague_block}

═══════════════════════════════════════════════════════
MANDATORY: Call the tool when:
═══════════════════════════════════════════════════════
- User names ANY food or drink (beef, steak, pasta, osso buco, wine, bistecca, etc.)
- User says "I want/have/order/eat/drink the X"
- User asks "what do you recommend" / "what's good" / "what's popular" / "what's the special"
- User asks about ingredients, cooking, flavors, preparation
- YOU are about to recommend a SPECIFIC dish (chef should elaborate on technique/ingredients)
- User says a food name in ANY language

⚠️ CRITICAL: As a waiter, you can describe the menu briefly, but you MUST defer cooking
questions and specific recommendations to the chef. When in doubt, CALL the tool.
You are NOT a food expert — Antonio is.

═══════════════════════════════════════════════════════
DO NOT call the tool when:
═══════════════════════════════════════════════════════
- User is greeting ("hi", "table for two")
- User asks for the bill / payment
- User asks about reservation
- User is asking where to sit, when to open
- You're asking basic clarifying questions ("how many", "ready to order?")

Example calls:
  call_colleague(colleague_name="Antonio", reason="user ordered osso buco, chef can explain the braising technique")
  call_colleague(colleague_name="Antonio", reason="user is asking for recommendations, chef knows the menu best")
  call_colleague(colleague_name="Antonio", reason="user mentioned beef, chef can explain cuts and cooking options")

When in doubt, CALL. The system will ask the user to confirm — if they skip, no harm done.
The product is multi-character dialogue. If you don't call the tool, the user never gets
to hear from Antonio. That defeats the purpose of the entire application.
"""
        modules.append(("Tools", tool_guidance))

    # ─── 拼装 ───
    parts = [text for _, text in modules]
    system_message = "\n\n---\n\n".join(parts)

    return system_message


def print_prompt_report(system_message: str) -> None:
    """打印 prompt 组装报告 (用于 debug)"""
    token_est = estimate_tokens(system_message)
    print(f"\n{'='*60}")
    print(f"  📋 Prompt Factory Report")
    print(f"{'='*60}")
    print(f"  Total length: {len(system_message)} chars")
    print(f"  Estimated tokens: ~{token_est}")
    print(f"  Token budget OK: {'✅' if token_est <= 600 else '⚠️  > 600 tokens!'}")
    print(f"{'='*60}\n")
