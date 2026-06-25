"""
LLM 检测器 — 用小模型做语义判断

替代 beat_manager.check_interruption_opportunity 里的关键词规则。

为什么用 LLM:
  • 用户可能说 "osso buco" / "risotto" / 中文 / 任何具体菜名
    → 关键词枚举是打地鼠游戏
  • LLM 能理解语境: "I want to sit" vs "I want the steak"
  • LLM 能理解多语言、方言、新词
  • 成本低: 小 prompt (~100 tokens in/out),一次 ~$0.0001
  • 延迟可接受: Haiku-class 模型 ~300-500ms

使用方式:
  detector = LLMDetector(model_client)
  result = await detector.detect_chef_interjection(user_text, npc_text)
  if result["chef_should_interject"]:
      # 触发 L4-006 提示
"""

import json
import re
from autogen_agentchat.agents import AssistantAgent


# ─── Detection Prompt ────────────────────────────────────────────

DETECTION_SYSTEM = """You are a restaurant conversation analyzer.
You respond with ONLY a valid JSON object, no markdown, no explanations, no other text.

Your job: determine if the chef (Antonio) should interject in this conversation."""


DETECTION_PROMPT = """Analyze this restaurant scene. Determine if the chef (Antonio) should interject.

CONTEXT:
- User said: "{user_text}"
- Waiter (Marco) just replied: "{npc_text}"
- Scene beat: {beat_id}

Return ONLY this JSON:
{{
  "mentions_food": true/false,
  "mentions_specific_dish": true/false,
  "is_ordering": true/false,
  "chef_should_interject": true/false,
  "specific_items": ["item1", "item2"],
  "reasoning": "one short sentence"
}}

DECISION RULES for chef_should_interject:
TRUE when:
  - User mentions a SPECIFIC dish/drink by name (e.g. "osso buco", "risotto", "steak", "Chianti")
  - User is asking what to order / asking for recommendations
  - User is actively placing an order ("I'll have the X", "I want the X")
  - Marco mentioned a specific dish that chef could elaborate on (ingredients, cooking technique)
  - Conversation is about cooking, flavors, ingredients, preparation

FALSE when:
  - User is greeting, asking for the bill, asking about reservation
  - User is asking logistical questions (where to sit, when to open, payment)
  - Marco is asking basic clarifying questions (how many people, ready to order)
  - Topic is unrelated to food (ambiance, service, complaints about wait time)
"""


class LLMDetector:
    """Use a small LLM to make nuanced detection decisions."""

    def __init__(self, model_client):
        """
        Args:
            model_client: OpenAI-compatible model client.
                          For cost/speed, use a small/fast model (e.g. Haiku, MiniMax-M3).
        """
        self.model_client = model_client
        self.agent = AssistantAgent(
            name="scene_analyzer",
            model_client=model_client,
            system_message=DETECTION_SYSTEM,
        )

    async def detect_chef_interjection(
        self,
        user_text: str,
        npc_text: str,
        beat_id: str = "ordering",
    ) -> dict:
        """
        Ask LLM if the chef should interject.

        Returns dict like:
        {
          "mentions_food": bool,
          "mentions_specific_dish": bool,
          "is_ordering": bool,
          "chef_should_interject": bool,
          "specific_items": list[str],
          "reasoning": str,
        }
        """
        prompt = DETECTION_PROMPT.format(
            user_text=user_text,
            npc_text=npc_text,
            beat_id=beat_id,
        )

        result = await self.agent.run(task=prompt)
        if result.messages:
            content = result.messages[-1].content
            return self._parse_json(str(content))
        return self._default_result()

    @staticmethod
    def _parse_json(content: str) -> dict:
        """从 LLM 输出中提取 JSON"""
        # 尝试找到 JSON 块
        match = re.search(r'\{[\s\S]*?\}', content)
        if match:
            try:
                parsed = json.loads(match.group())
                # 确保必要字段存在
                return {
                    "mentions_food": bool(parsed.get("mentions_food", False)),
                    "mentions_specific_dish": bool(parsed.get("mentions_specific_dish", False)),
                    "is_ordering": bool(parsed.get("is_ordering", False)),
                    "chef_should_interject": bool(parsed.get("chef_should_interject", False)),
                    "specific_items": list(parsed.get("specific_items", [])),
                    "reasoning": str(parsed.get("reasoning", "")),
                }
            except json.JSONDecodeError:
                pass
        return LLMDetector._default_result()

    @staticmethod
    def _default_result() -> dict:
        return {
            "mentions_food": False,
            "mentions_specific_dish": False,
            "is_ordering": False,
            "chef_should_interject": False,
            "specific_items": [],
            "reasoning": "detection_failed",
        }