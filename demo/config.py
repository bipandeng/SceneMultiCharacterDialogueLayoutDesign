"""Demo 模型配置 — MiniMax-M3"""

from autogen_ext.models.openai import OpenAIChatCompletionClient


def create_model_client() -> OpenAIChatCompletionClient:
    """
    创建 LLM 客户端 (MiniMax-M3, OpenAI 兼容接口)

    关键配置:
      - max_tokens=2000: 留够 thinking + 实际回复 + tool call 的空间
      - extra_body={"thinking": "disabled"}: 尝试禁用 thinking 模式
        (MiniMax / DeepSeek 类模型支持, 如果不支持则忽略)
      - temperature=0.7: 适度随机, 不让 NPC 太死板

    如果 thinking 关闭失败, 还可以通过 prompt 强制:
      "Respond directly. Do NOT output thinking blocks."
    """
    return OpenAIChatCompletionClient(
        base_url="https://api.minimaxi.com/v1",
        model="MiniMax-M3",
        api_key="sk-cp-2G0ldj2nR8RU0tkjdyGYbxNyx-smYuBPsz3pTbz5k_WD8Xur0Li1dYUBPNQmP1G7mfgIJkY91jPHXpFA7DqlwoqUeeTcOtB3ndK_CYhuI5QroXXaG5Qfz7Q",
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "unknown",
            "structured_output": True,
            "multiple_system_messages": True,
        },
        # ─── 关键参数 ─────────────────────────────────────
        max_tokens=2000,                          # 给足空间
        temperature=0.7,
        # MiniMax 用 ThinkingConfig 对象, 不是 string
        extra_body={
            "thinking": {"type": "disabled"},     # MiniMax / Anthropic 格式
        },
    )