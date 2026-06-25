"""
引擎层 — EngineAdapter 封装 AutoGen SelectorGroupChat

核心职责:
  1. 创建 AutoGen agents (每个 NPC 一个 AssistantAgent)
  2. 创建 SelectorGroupChat + selector_func
  3. 管理对话循环 (NPC → User → NPC → ...)
  4. 追踪目标词高亮状态
"""

import json as _json

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.messages import (
    TextMessage,
    ModelClientStreamingChunkEvent,
    SelectSpeakerEvent,
    ToolCallRequestEvent,
    ToolCallSummaryMessage,
    ThoughtEvent,
)

from beat_manager import BeatManager
from prompt_factory import build_system_message
from tools import call_colleague
from tag_parser import parse_directive_tags, has_call_directive, get_call_target


def _extract_function_calls(content: str) -> tuple[str, list[dict]]:
    """
    从 AutoGen 序列化的 TextMessage.content 中提取 [FunctionCall(...)] 块。

    当 agent 调用工具时, AutoGen 把 FunctionCall 信息以字符串形式嵌入 content:
        [FunctionCall(id='...', arguments='{"colleague_name": "Antonio"}', name='call_colleague')]

    Returns:
        (clean_content, function_calls)
        - clean_content: 去掉所有 [FunctionCall(...)] 后的可读内容
        - function_calls: 解析出的调用列表 [{"name": ..., "arguments": {...}}, ...]
    """
    import re, json as _json
    pattern = re.compile(
        r"\[FunctionCall\([^)]*?name=['\"]([^'\"]+)['\"][^)]*?arguments=['\"]([^'\"]+)['\"][^)]*?\)\]"
    )

    fn_calls = []
    for match in pattern.finditer(content):
        name = match.group(1)
        args_raw = match.group(2)
        # arguments 可能是 JSON 字符串, 需要 unescape
        try:
            args = _json.loads(args_raw.replace('\\"', '"').replace("\\'", "'"))
        except (_json.JSONDecodeError, ValueError):
            args = {"raw": args_raw}
        fn_calls.append({"name": name, "arguments": args})

    clean = pattern.sub("", content)
    # 清理可能残留的空行
    clean = re.sub(r'\n{3,}', '\n\n', clean).strip()
    return clean, fn_calls


def _filter_thinking_chunk(
    chunk: str,
    in_thinking: bool,
    pending_buffer: str,
) -> tuple[str, bool, str]:
    """
    过滤 streaming chunk 中的 <think>...</think> 推理块。

    处理边界情况: <think> 标签可能跨 chunk 边界。

    Returns:
        (visible_text, new_in_thinking, new_pending_buffer)
    """
    # 把 chunk 接到 pending_buffer 上做完整标签检测
    combined = pending_buffer + chunk
    visible = ""
    new_in_thinking = in_thinking

    if in_thinking:
        # 等待 </think>
        if "</think>" in combined:
            idx = combined.index("</think>") + len("</think>")
            visible = combined[idx:]
            new_in_thinking = False
            new_pending = ""
        else:
            visible = ""
            new_pending = combined
    else:
        # 检查是否有 <think>
        if "<think>" in combined:
            idx = combined.index("<think>")
            visible = combined[:idx]
            new_in_thinking = True
            # 找到 <think> 之后, 检查是否在同一 chunk 里有 </think>
            after_think = combined[idx + len("<think>"):]
            if "</think>" in after_think:
                idx2 = after_think.index("</think>") + len("</think>")
                visible += after_think[idx2:]
                new_in_thinking = False
                new_pending = ""
            else:
                new_pending = after_think
        else:
            visible = combined
            new_pending = ""

    return visible, new_in_thinking, new_pending


class SceneEngine:
    """场景对话引擎 — 封装 AutoGen + 业务逻辑"""

    def __init__(
        self,
        model_client,
        npc_configs: list[dict],
        scene_instance: dict,
        beat_manager: BeatManager,
        cefr_level: str = "B1",
        old_friend_words: list[str] | None = None,
    ):
        self.model_client = model_client
        self.npc_configs = npc_configs
        self.scene_instance = scene_instance
        self.beat_manager = beat_manager
        self.cefr_level = cefr_level
        self.old_friend_words = old_friend_words

        # 状态追踪
        self.seen_vocab: set[str] = set()
        self.collected_vocab: set[str] = set()
        self.total_turns = 0
        # L4-006 多人插话机制: 外层可强制指定下一个说话者
        self._pending_speaker: str | None = None

        # 创建 agents 和 team
        self.agents: dict[str, AssistantAgent] = {}
        self.team: SelectorGroupChat | None = None
        self._setup()

    def _setup(self):
        """创建 AutoGen agents + SelectorGroupChat"""
        agents_list = []

        for npc in self.npc_configs:
            # 计算其他同事 (用于 Tool 描述)
            colleagues = [
                {
                    "name": c["name"],
                    "template_role": c.get("template_role", ""),
                    "persona": c.get("persona", ""),
                }
                for c in self.npc_configs
                if c["name"] != npc["name"]
            ]

            # 用 Prompt 工厂生成 system_message
            system_msg = build_system_message(
                character=npc,
                scene_instance=self.scene_instance,
                cefr_level=self.cefr_level,
                old_friend_words=self.old_friend_words,
                colleagues=colleagues if colleagues else None,
            )

            # 只给主发言 NPC (第一个) 注册 call_colleague 工具
            # 其他 NPC 也可以注册, 但 demo 阶段简化为主 NPC 呼叫
            tools = [call_colleague] if npc["name"] == self.npc_configs[0]["name"] else []

            agent = AssistantAgent(
                name=npc["name"],
                model_client=self.model_client,
                system_message=system_msg,
                tools=tools,  # 主 NPC 可以调用 call_colleague 工具
                reflect_on_tool_use=False,  # 工具调用后不反思, 直接给结果
                model_client_stream=True,  # 开启 streaming, run_stream 才能 yield chunks
            )
            self.agents[npc["name"]] = agent
            agents_list.append(agent)

        npc_names = list(self.agents.keys())

        # 创建 selector_func (闭包捕获 beat_manager 和 self)
        beat_mgr = self.beat_manager
        engine_ref = self  # 用于访问 _pending_speaker

        def selector_func(messages):
            # L4-006 优先返回 pending_speaker (插话机制)
            if engine_ref._pending_speaker is not None:
                pending = engine_ref._pending_speaker
                engine_ref._pending_speaker = None  # 用完即清
                if pending in engine_ref.agents:
                    return pending
            return beat_mgr.select_next_speaker(messages, npc_names)

        # 创建 SelectorGroupChat
        # MaxMessageTermination(max_messages=2): 用户消息(1) + NPC 回复(1) = 2 条
        # 如果设成 1, 会在用户消息加入后立刻终止, NPC 永远没机会说话
        # emit_team_events=True: 让 SelectSpeakerEvent 被 yield 出来,
        #                          这样我们能在 chunks 到达前知道是哪个 NPC 在说话
        self.team = SelectorGroupChat(
            agents_list,
            model_client=self.model_client,
            selector_func=selector_func,
            termination_condition=MaxMessageTermination(max_messages=2),
            allow_repeated_speaker=True,
            emit_team_events=True,
        )

    @property
    def npc_names(self) -> list[str]:
        return list(self.agents.keys())

    @property
    def npc_role_map(self) -> dict[str, str]:
        return {npc["name"]: npc.get("template_role", "") for npc in self.npc_configs}

    @property
    def vocab_translation_map(self) -> dict[str, str]:
        """目标词 → 中文翻译映射"""
        return {
            item["word"]: item.get("translation_zh", "")
            for item in self.scene_instance.get("_vocab_pool_data", [])
        }

    def set_vocab_pool_data(self, vocab_pool_data: list[dict]):
        """设置词汇池数据 (用于翻译查询)"""
        self.scene_instance["_vocab_pool_data"] = vocab_pool_data

    async def get_npc_response(self, user_message: str) -> tuple[str, str]:
        """
        非流式版本 — 用于测试或调试。
        用 team.run() 一次性拿到所有消息。
        """
        self.total_turns += 1

        result = await self.team.run(task=user_message)

        for msg in result.messages:
            if isinstance(msg, TextMessage) and msg.source in self.agents:
                clean_content = self.clean_thinking_blocks(msg.content)
                return msg.source, clean_content

        return "System", "..."

    async def stream_npc_response(
        self,
        user_message: str,
        on_chunk=None,
        on_start=None,
        on_complete=None,
    ):
        """
        流式获取 NPC 回复 — 用 team.run_stream() 实时输出 token。

        事件流 (按时间顺序):
          1. SelectSpeakerEvent             → 选角
          2. ModelClientStreamingChunkEvent → streaming tokens (如果 NPC 输出文本)
          3. ThoughtEvent                   → NPC 的思考
          4. ToolCallRequestEvent           → NPC 调用工具 (如 call_colleague) ⭐
          5. ToolCallExecutionEvent         → 工具执行结果
          6. ToolCallSummaryMessage         → 工具结果摘要
          7. TextMessage                    → NPC 最终文本 (无工具调用时)
          8. TaskResult                     → 流结束

        ⚠️ 关键: 必须完全耗尽 stream (不能提前 return),
                  否则下次 run_stream 会报 "team already running"

        Args:
            user_message: 用户输入
            on_chunk: 可选回调 fn(chunk_text) — 每个 token chunk 触发一次 (流式)
            on_start: 可选回调 fn(npc_name) — NPC 开始说话时触发 (流式)
            on_complete: 可选回调 fn(npc_name, full_content, directives) — 说完时触发
        """
        self.total_turns += 1

        npc_name = None
        npc_started = False
        full_content = ""
        tool_calls: list[dict] = []

        # 思考块过滤状态
        in_thinking = False
        pending_buffer = ""

        async for msg in self.team.run_stream(task=user_message):
            # 1. 选角事件 — 提前知道 NPC, 立即触发 on_start
            if isinstance(msg, SelectSpeakerEvent) and msg.content:
                npc_name = msg.content[0]
                if not npc_started and on_start:
                    on_start(npc_name)
                    npc_started = True

            # 2. Streaming chunks — 实时触发 on_chunk
            elif isinstance(msg, ModelClientStreamingChunkEvent):
                if not npc_name:
                    continue
                visible_text, in_thinking, pending_buffer = _filter_thinking_chunk(
                    msg.content, in_thinking, pending_buffer
                )
                if visible_text and on_chunk:
                    on_chunk(visible_text)

            # 3. 工具调用 — L4-006 多角色协作的关键信号 ⭐
            elif isinstance(msg, ToolCallRequestEvent):
                for tool_call in (msg.content or []):
                    raw_args = getattr(tool_call, "arguments", "{}")
                    # arguments 是 JSON 字符串, 需要解析
                    if isinstance(raw_args, str):
                        try:
                            args = _json.loads(raw_args)
                        except (_json.JSONDecodeError, ValueError):
                            args = {}
                    else:
                        args = raw_args or {}
                    tool_calls.append({
                        "name": getattr(tool_call, "name", ""),
                        "arguments": args,
                    })

            # 4. 工具执行摘要 (有内容时是 NPC 的"可见"输出)
            elif isinstance(msg, ToolCallSummaryMessage) and msg.source in self.agents:
                npc_name = msg.source
                clean = self.clean_thinking_blocks(str(msg.content))
                full_content, _ = parse_directive_tags(clean)

            # 5. 纯文本回复 (无工具调用时)
            elif isinstance(msg, TextMessage) and msg.source in self.agents:
                npc_name = msg.source
                clean = self.clean_thinking_blocks(str(msg.content))
                full_content, _ = parse_directive_tags(clean)

        # 流耗尽后构建 directives 并回调
        if npc_name:
            directives: list[dict] = []
            for tc in tool_calls:
                if tc["name"] == "call_colleague":
                    directives.append({
                        "type": "call",
                        "target": tc["arguments"].get("colleague_name", ""),
                        "reason": tc["arguments"].get("reason", ""),
                        "source": "tool_call",
                    })
                    break  # 只取第一个 call_colleague

            if on_complete:
                on_complete(npc_name, full_content, directives)
            return npc_name, full_content, directives

        return "System", "", []

    def get_opening_message(self) -> tuple[str, str]:
        """获取 NPC 开场白"""
        if self.npc_configs:
            first_npc = self.npc_configs[0]
            return first_npc["name"], first_npc.get("greeting", "Welcome!")
        return "System", "..."

    def force_next_speaker(self, npc_name: str) -> None:
        """
        L4-006 强制下一个说话者 — 由外层 main.py 在用户确认插话后调用。
        下次 selector_func 被触发时,会优先返回这个 NPC,然后清空。
        """
        if npc_name in self.agents:
            self._pending_speaker = npc_name

    @staticmethod
    def clean_thinking_blocks(text: str) -> str:
        """
        去掉 LLM 输出中的 <think>...</think> 推理块 (MiniMax 等模型会输出)
        """
        import re
        # 去掉成对的 <think>...</think>
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # 去掉单独的 <think> (开标签没闭合)
        cleaned = re.sub(r'<think>.*$', '', cleaned, flags=re.DOTALL)
        # 去掉开头/结尾的多余空白
        return cleaned.strip()

    def check_user_vocab_usage(self, user_text: str) -> list[str]:
        """检查用户消息中是否使用了目标词"""
        used = []
        user_lower = user_text.lower()
        for word in self.scene_instance["selected_vocab"]:
            if word.lower() in user_lower:
                used.append(word)
        return used

    def collect_word(self, word: str) -> None:
        """用户收藏一个词"""
        self.collected_vocab.add(word)
