"""
场景实例生成器 — 模板 → 实例

在 scene_template 上，由 LLM (或随机) 实例化生成 scene_instance。
实例化内容:
  - instance_setting: 填充模板变量后的场景设定
  - selected_vocabulary: 从 vocab_pool 选出 ~5 个目标词
  - selected_patterns: 从 pattern_pool 选出 ~3 个目标句型
"""

import json
import random


def generate_instance(
    template: dict,
    cefr_level: str = "B1",
    use_llm: bool = False,
    model_client=None,
) -> dict:
    """
    在模板上生成一个场景实例。

    Args:
        template: 从 JSON 加载的场景模板
        cefr_level: 用户 CEFR 等级
        use_llm: 是否用 LLM 做智能选词 (默认 False, 用随机选择)
        model_client: AutoGen model client (use_llm=True 时必须)

    Returns:
        scene_instance dict
    """
    # 1. 生成场景设定 (填充模板变量)
    setting_template = template["setting_template"]
    defaults = template.get("setting_defaults", {})
    setting = setting_template.format(**defaults)

    # 2. 选择目标词汇 (~5 个)
    vocab_pool = template["vocab_pool"]
    if use_llm and model_client:
        selected_vocab = _llm_select_vocab(vocab_pool, cefr_level, template, model_client)
    else:
        selected_vocab = _random_select_vocab(vocab_pool, count=5)

    # 3. 选择目标句型 (~3 个)
    pattern_pool = template["pattern_pool"]
    selected_patterns = _random_select_patterns(pattern_pool, count=3)

    # 4. 组装实例
    instance = {
        "template_id": template["id"],
        "setting": setting,
        "selected_vocab": selected_vocab,
        "selected_patterns": selected_patterns,
        "required_beats": template["required_beats"],
        "optional_beats": template.get("optional_beats", []),
        "scene_flow_key": template["id"],  # 用于 prompt_factory 选择 scene flow 模板
        "npc_configs": template["npc_roles"],
    }

    return instance


def _random_select_vocab(vocab_pool: list[dict], count: int = 5) -> list[str]:
    """随机选择目标词 (demo 用, 保证覆盖多个 beat)"""
    # 确保覆盖不同类别
    by_category: dict[str, list[str]] = {}
    for item in vocab_pool:
        cat = item.get("category", "other")
        by_category.setdefault(cat, []).append(item["word"])

    selected = []
    # 每个类别至少选 1 个
    for cat, words in by_category.items():
        if words and len(selected) < count:
            selected.append(random.choice(words))

    # 剩余的随机补
    all_words = [item["word"] for item in vocab_pool]
    remaining = [w for w in all_words if w not in selected]
    while len(selected) < count and remaining:
        selected.append(remaining.pop(random.randrange(len(remaining))))

    return selected[:count]


def _random_select_patterns(pattern_pool: list[dict], count: int = 3) -> list[str]:
    """随机选择目标句型"""
    patterns = [item["pattern"] for item in pattern_pool]
    if len(patterns) <= count:
        return patterns
    return random.sample(patterns, count)


def _llm_select_vocab(
    vocab_pool: list[dict],
    cefr_level: str,
    template: dict,
    model_client,
) -> list[str]:
    """
    用 LLM 智能选词 (V2 功能, 暂时不用)。
    可以根据 CEFR 等级、词汇难度、场景适配度来选词。
    """
    # TODO: 实现 LLM 选词
    return _random_select_vocab(vocab_pool)


def print_instance_report(instance: dict) -> None:
    """打印实例化报告 (用于 debug)"""
    print(f"\n{'='*60}")
    print(f"  🍽️  Scene Instance: {instance['template_id']}")
    print(f"{'='*60}")
    print(f"  Setting: {instance['setting']}")
    print(f"\n  📝 Target Words ({len(instance['selected_vocab'])}):")
    for w in instance["selected_vocab"]:
        print(f"     • {w}")
    print(f"\n  📐 Target Patterns ({len(instance['selected_patterns'])}):")
    for p in instance["selected_patterns"]:
        print(f"     • {p}")
    print(f"\n  🎯 Required Beats: {', '.join(instance['required_beats'])}")
    print(f"{'='*60}\n")
