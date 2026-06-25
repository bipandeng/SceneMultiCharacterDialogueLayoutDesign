"""
Beat 状态机 — 追踪场景进度

核心职责:
  1. 追踪当前 beat (greeting → ordering → payment)
  2. 检测用户消息是否满足 beat 推进条件 (关键词匹配)
  3. 为 selector_func 提供 beat 状态信息
  4. NPC 引导: 同一 beat 太久没推进 → NPC 主动引导
"""

import random
import time


class BeatManager:
    """管理场景内的 beat 状态机"""

    def __init__(self, beats: list[dict], required_beats: list[str]):
        """
        Args:
            beats: 模板中定义的 beat 列表 (含 beat_id, advance_keywords, min_turns, max_turns)
            required_beats: 必须完成的 beat ID 列表
        """
        self.beats = {b["beat_id"]: b for b in beats}
        self.required_beats = required_beats

        # 按 sort_order 排列的 beat 序列
        self.beat_order = [b["beat_id"] for b in sorted(beats, key=lambda x: x["sort_order"])]

        # 状态
        self.current_index = 0
        self.turns_in_beat = 0
        self.beat_history: list[dict] = []  # 记录每个 beat 的完成情况

        # 引导冷却: 避免 NPC 反复催
        self.last_guide_prompt_turn = -10

    @property
    def current_beat_id(self) -> str:
        if self.current_index < len(self.beat_order):
            return self.beat_order[self.current_index]
        return "done"

    @property
    def current_beat(self) -> dict | None:
        return self.beats.get(self.current_beat_id)

    @property
    def is_done(self) -> bool:
        return self.current_index >= len(self.beat_order)

    @property
    def progress_display(self) -> str:
        """生成 beat 进度展示: ●●○○○"""
        symbols = []
        for i, bid in enumerate(self.beat_order):
            if i < self.current_index:
                symbols.append("●")  # 已完成
            elif i == self.current_index:
                symbols.append("◉")  # 当前
            else:
                symbols.append("○")  # 未开始
        return " ".join(symbols)

    @property
    def all_required_done(self) -> bool:
        """检查是否所有必选 beat 都已完成"""
        completed = set(self.beat_history)
        return all(bid in completed for bid in self.required_beats)

    def process_user_message(self, user_text: str) -> dict:
        """
        处理用户消息, 检查是否可以推进 beat。

        Returns:
            {
                "advanced": bool,          # 是否发生了 beat 推进
                "from_beat": str | None,   # 从哪个 beat 推进
                "to_beat": str | None,     # 推进到哪个 beat
                "needs_guide": bool,       # 是否需要 NPC 引导用户
                "guide_hint": str | None,  # 引导提示
            }
        """
        result = {
            "advanced": False,
            "from_beat": None,
            "to_beat": None,
            "needs_guide": False,
            "guide_hint": None,
        }

        if self.is_done:
            return result

        beat = self.current_beat
        if beat is None:
            return result

        self.turns_in_beat += 1
        user_lower = user_text.lower().strip()

        # 检查 beat 推进条件
        can_advance = self._check_advance(beat, user_lower)

        if can_advance and self.turns_in_beat >= beat.get("min_turns", 1):
            # 主动推进 (用户说了关键词)
            result["advanced"] = True
            result["from_beat"] = self.current_beat_id
            self.beat_history.append({
                "beat_id": self.current_beat_id,
                "turns_spent": self.turns_in_beat,
                "completed_at": time.time(),
            })
            self.current_index += 1
            self.turns_in_beat = 0
            result["to_beat"] = self.current_beat_id

            if self.is_done:
                result["to_beat"] = "done"
        else:
            # can_advance=False — 检查 max_turns 兜底
            max_turns = beat.get("max_turns", 6)

            # ⚠️ 必须先判断强制推进, 再判断引导提示
            # 否则 max_turns-2 命中时 if/elif 永远进不去强制推进分支
            if self.turns_in_beat >= max_turns:
                # 超过最大轮数, 强制推进 (auto-advance)
                result["advanced"] = True
                result["from_beat"] = self.current_beat_id
                self.beat_history.append({
                    "beat_id": self.current_beat_id,
                    "turns_spent": self.turns_in_beat,
                    "completed_at": time.time(),
                    "auto_advanced": True,
                })
                self.current_index += 1
                self.turns_in_beat = 0
                result["to_beat"] = self.current_beat_id
            elif self.turns_in_beat >= max_turns - 2:
                # 接近最大轮数, NPC 应该引导 (每 2 轮提示一次)
                if self.turns_in_beat - self.last_guide_prompt_turn >= 2:
                    result["needs_guide"] = True
                    result["guide_hint"] = self._get_guide_hint(beat)
                    self.last_guide_prompt_turn = self.turns_in_beat

        return result

    def _check_advance(self, beat: dict, user_lower: str) -> bool:
        """检查用户消息是否包含 beat 推进关键词"""
        keywords = beat.get("advance_keywords", [])
        if not keywords:
            return False

        # 匹配任意一个关键词
        for kw in keywords:
            if kw.lower() in user_lower:
                return True
        return False

    def _get_guide_hint(self, beat: dict) -> str:
        """获取 NPC 引导提示 (给 selector 参考)"""
        beat_id = beat["beat_id"]
        hints = {
            "greeting": "Guide the user to greet or mention their reservation.",
            "ordering": "Guide the user to order food. Ask about starters, mains, or drinks.",
            "payment": "Guide the user toward wrapping up — mention the bill or ask if they need anything else.",
        }
        return hints.get(beat_id, "Gently guide the user toward the next natural step.")

    def select_next_speaker(
        self,
        messages: list,
        npc_names: list[str],
    ) -> str | None:
        """
        selector_func 的核心逻辑: 根据 beat 状态 + 消息历史选择下一个说话者。

        Args:
            messages: AutoGen 消息序列
            npc_names: 所有 NPC agent 的名字列表

        Returns:
            下一个说话者的名字, 或 None (需要用户输入)
        """
        # 没有消息 → 第一个 NPC 开场
        if not messages:
            return npc_names[0]

        # 获取最后一条有效消息的发送者
        last_speaker = None
        last_content = ""
        for msg in reversed(messages):
            if hasattr(msg, "source") and hasattr(msg, "content"):
                last_speaker = msg.source
                last_content = msg.content if isinstance(msg.content, str) else ""
                break

        # 最后一个说话的是 NPC → 该用户了
        if last_speaker in npc_names:
            return None  # 等待用户输入

        # 最后一个说话的是用户 → 选一个 NPC
        current_beat = self.current_beat_id
        user_lower = last_content.lower()

        # 基于 beat 和内容的 NPC 选择
        return self._select_npc_for_beat(current_beat, user_lower, npc_names)

    def _select_npc_for_beat(
        self,
        beat_id: str,
        user_text: str,
        npc_names: list[str],
    ) -> str:
        """
        根据当前 beat 和用户消息选择 NPC。

        ⚠️ 修复: 之前这里会"30% 概率自动让 Antonio 说话",违反 L4-006 设计
        (L4-006 要求: NPC 想插话 → 提示用户 → 用户决定 → 才让 NPC 说)。

        现在 selector 只负责"轮到谁主发言",插话机制由外层 main.py 控制
        (check_interruption_opportunity → 提示用户 → force_next_speaker)。
        """
        if len(npc_names) <= 1:
            return npc_names[0]

        primary = npc_names[0]  # Marco (waiter) — 主发言 NPC

        # 所有 beat 都默认返回 primary
        # 插话由外层强制设置 pending_speaker 处理
        return primary

    def check_interruption_opportunity(
        self,
        last_user_text: str,
        last_npc_text: str,
        primary_npc: str,
        npc_configs: list[dict],
        probability: float = 0.5,
    ) -> list[str]:
        """
        L4-006 多人插话检测 — 主发言后, 检查是否有其他 NPC 想插话。

        Demo 阶段用规则驱动:
          • 检测食物/烹饪关键词 + chef 角色 → Antonio 想补充
          • 按 probability 概率触发, 避免每次都打扰

        V2 可换成 LLM 判定: '当前上下文下, Antonio 是否应该插话?'

        Args:
            last_user_text: 用户最近的消息
            last_npc_text: 主 NPC 刚说的话
            primary_npc: 刚发言的主 NPC 名字
            npc_configs: 所有 NPC 配置 (含 template_role)
            probability: 触发插话提示的概率 (0-1)

        Returns:
            想插话的 NPC 名字列表 (通常 0 或 1 个)
        """
        npc_names = [npc["name"] for npc in npc_configs]
        if len(npc_names) <= 1:
            return []  # 只有一个 NPC, 没插话必要

        # 概率检查
        if random.random() > probability:
            return []

        # 检测可插话的 NPC
        wants_to_speak = []
        text = (last_user_text + " " + last_npc_text).lower()

        food_keywords = [
            "steak", "pasta", "salad", "soup", "dessert", "fish", "chicken",
            "sauce", "cook", "ingredient", "recipe", "chef", "kitchen",
            "appetizer", "entree", "wine", "drink", "menu", "dish", "food",
            "special", "recommend", "fresh", "homemade", "taste", "flavor",
            "seasoning", "roasted", "grilled",
        ]

        for npc in npc_configs:
            npc_name = npc["name"]
            if npc_name == primary_npc:
                continue  # 主发言 NPC 自己不会"插话"
            template_role = npc.get("template_role", "").lower()
            # chef / cook 类角色 + 检测到食物关键词 → 想插话
            if ("chef" in template_role or "cook" in template_role):
                if any(kw in text for kw in food_keywords):
                    wants_to_speak.append(npc_name)

        return wants_to_speak
