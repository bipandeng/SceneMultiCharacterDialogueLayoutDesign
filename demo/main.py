#!/usr/bin/env python3
"""
LinguaScene Demo — CLI 入口

场景化多角色编排系统验证 Demo
验证: AutoGen SelectorGroupChat + Prompt 工厂 + Beat 状态机 + 目标词高亮

使用方法:
    python main.py              # 默认: B1 等级, 餐厅场景
    python main.py --cefr A2    # 指定 CEFR 等级
    python main.py --debug      # 显示 debug 信息 (prompt 报告等)
"""

import argparse
import asyncio
import json
import os
import sys
import random

from config import create_model_client
from instance_generator import generate_instance, print_instance_report
from prompt_factory import build_system_message, print_prompt_report
from beat_manager import BeatManager
from engine import SceneEngine
from llm_detector import LLMDetector
from cli_format import (
    print_scene_header,
    print_npc_bubble,
    print_ding,
    print_user_message,
    print_beat_advance,
    print_beat_done,
    print_guide_hint,
    print_vocab_used,
    print_session_summary,
    StreamingPrinter,
    BOLD,
    RESET,
    DIM,
    AMBER,
    GREEN,
    CYAN,
)


def load_template(template_path: str) -> dict:
    """加载场景模板 JSON"""
    with open(template_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_user_input() -> str:
    """获取用户输入 (带提示符)"""
    try:
        text = input(f"  {GREEN}{BOLD}You>{RESET} ").strip()
        return text
    except (EOFError, KeyboardInterrupt):
        print(f"\n\n  {DIM}Bye! 👋{RESET}\n")
        sys.exit(0)


def handle_special_commands(
    text: str,
    engine: SceneEngine,
    seen_vocab: set,
    target_vocab: list[str],
    total_beats: int,
) -> bool:
    """
    处理特殊命令。返回 True 表示已处理, 不发送给 NPC。
    """
    cmd = text.lower().strip()

    if cmd in ("/quit", "/exit", "/q"):
        print(f"\n  {DIM}Ending scene... 👋{RESET}\n")
        print_session_summary(
            seen_vocab=seen_vocab,
            target_vocab=target_vocab,
            collected_vocab=engine.collected_vocab,
            total_turns=engine.total_turns,
            beat_history=engine.beat_manager.beat_history,
            total_beats=total_beats,
        )
        sys.exit(0)

    if cmd == "/status":
        bm = engine.beat_manager
        print(f"\n  {DIM}Beat: {bm.progress_display} ({bm.current_beat_id}){RESET}")
        print(f"  {DIM}Turns in beat: {bm.turns_in_beat}{RESET}")
        print(f"  {DIM}Seen words: {seen_vocab}{RESET}")
        print(f"  {DIM}Total turns: {engine.total_turns}{RESET}\n")
        return True

    if cmd == "/words":
        print(f"\n  {AMBER}Target words:{RESET}")
        for w in target_vocab:
            status = "✅" if w in seen_vocab else "○"
            print(f"    {status} {w}")
        print()
        return True

    if cmd.startswith("/collect "):
        word = text[9:].strip()
        if word in target_vocab:
            engine.collect_word(word)
            print(f"  {GREEN}📌 Collected: {word}{RESET}\n")
        else:
            print(f"  {DIM}Not a target word.{RESET}\n")
        return True

    if cmd == "/help":
        print(f"\n  {BOLD}Commands:{RESET}")
        print(f"    /quit or /q   — End scene")
        print(f"    /status       — Show beat progress")
        print(f"    /words        — Show target word status")
        print(f"    /collect WORD — Collect a word to your vocabulary")
        print(f"    /help         — Show this help")
        print()
        return True

    return False


async def run_scene(
    template_path: str,
    cefr_level: str = "B1",
    debug: bool = False,
) -> None:
    """运行一个场景"""

    # ─── 1. 加载模板 ───
    print(f"\n  {DIM}Loading template...{RESET}")
    template = load_template(template_path)

    # ─── 2. 生成实例 ───
    print(f"  {DIM}Generating scene instance...{RESET}")
    instance = generate_instance(template, cefr_level)

    if debug:
        print_instance_report(instance)

    # ─── 3. 创建 BeatManager ───
    all_beats = template["beats"]
    beat_mgr = BeatManager(all_beats, instance["required_beats"])

    # ─── 4. 创建引擎 ───
    print(f"  {DIM}Setting up AutoGen engine...{RESET}")
    model_client = create_model_client()

    engine = SceneEngine(
        model_client=model_client,
        npc_configs=instance["npc_configs"],
        scene_instance=instance,
        beat_manager=beat_mgr,
        cefr_level=cefr_level,
    )

    # LLM 检测器 — 用模型判断是否应该插话 (语义级, 不依赖关键词)
    detector = LLMDetector(model_client)

    # 设置词汇池数据 (用于翻译)
    engine.set_vocab_pool_data(template["vocab_pool"])

    # Debug: 打印 prompt 报告
    if debug:
        for npc in instance["npc_configs"]:
            sys_msg = build_system_message(
                character=npc,
                scene_instance=instance,
                cefr_level=cefr_level,
            )
            print(f"\n  {BOLD}── {npc['name']}'s system_message ──{RESET}")
            print(sys_msg)
            print_prompt_report(sys_msg)

    # ─── 5. 打印场景头部 ───
    target_vocab = instance["selected_vocab"]
    seen_vocab: set[str] = set()

    print_scene_header(
        scene_name=f"{template['name_zh']} ({template['name_en']})",
        target_vocab=target_vocab,
        beat_progress=beat_mgr.progress_display,
        current_beat_name=beat_mgr.current_beat_id if not beat_mgr.is_done else "done",
    )

    # ─── 6. NPC 开场白 ───
    npc_name, greeting = engine.get_opening_message()
    new_words = print_npc_bubble(
        npc_name, greeting,
        role=engine.npc_role_map.get(npc_name, ""),
        target_vocab=target_vocab,
        seen_vocab=seen_vocab,
    )
    for w in new_words:
        trans = engine.vocab_translation_map.get(w, "")
        print_ding(w, trans)

    # ─── 7. 对话主循环 ───
    print(f"  {DIM}Type your message (or /help for commands, /quit to end){RESET}\n")

    while not beat_mgr.is_done:
        # 获取用户输入
        user_text = get_user_input()
        if not user_text:
            continue

        # 处理特殊命令
        if handle_special_commands(user_text, engine, seen_vocab, target_vocab, len(template['beats'])):
            continue

        # 打印用户消息
        print_user_message(user_text)

        # 检查用户是否使用了目标词
        used_words = engine.check_user_vocab_usage(user_text)
        for w in used_words:
            print_vocab_used(w)

        # 检查 beat 推进
        beat_result = beat_mgr.process_user_message(user_text)
        if beat_result["advanced"]:
            if beat_result["to_beat"] and beat_result["to_beat"] != "done":
                print_beat_advance(beat_result["from_beat"], beat_result["to_beat"])
            elif beat_result["to_beat"] == "done":
                print_beat_done()
                break

        if beat_result["needs_guide"]:
            print_guide_hint(beat_result.get("guide_hint", ""))

        # 更新头部信息
        print_scene_header(
            scene_name=f"{template['name_zh']} ({template['name_en']})",
            target_vocab=target_vocab,
            beat_progress=beat_mgr.progress_display,
            current_beat_name=beat_mgr.current_beat_id if not beat_mgr.is_done else "done",
        )

        # 获取 NPC 回复 (流式)
        printer = StreamingPrinter()
        directives = []
        try:
            npc_name, npc_content, directives = await engine.stream_npc_response(
                user_text,
                on_start=lambda name: printer.start(
                    name, role=engine.npc_role_map.get(name, "")
                ),
                on_chunk=lambda text: printer.chunk(text),
                on_complete=lambda name, content, dirs: printer.finish(),
            )
        except Exception as e:
            print(f"  {DIM}⚠️  Error getting NPC response: {e}{RESET}")
            print(f"  {DIM}Retrying...{RESET}")
            try:
                npc_name, npc_content, directives = await engine.stream_npc_response(
                    user_text,
                    on_start=lambda name: printer.start(
                        name, role=engine.npc_role_map.get(name, "")
                    ),
                    on_chunk=lambda text: printer.chunk(text),
                    on_complete=lambda name, content, dirs: printer.finish(),
                )
            except Exception as e2:
                print(f"  {DIM}⚠️  Failed again: {e2}{RESET}")
                continue

        # 流结束后打印格式化气泡 (含目标词高亮 + "叮")
        if npc_name != "System":
            new_words = print_npc_bubble(
                npc_name, npc_content,
                role=engine.npc_role_map.get(npc_name, ""),
                target_vocab=target_vocab,
                seen_vocab=seen_vocab,
            )
            for w in new_words:
                trans = engine.vocab_translation_map.get(w, "")
                print_ding(w, trans)

            # ─── L4-006 多人插话检测 (Tool Calling) ───
            # 主 NPC 通过工具 call_colleague() 显式呼叫同事
            # 这是结构化调用, 100% 可靠 (LLM 必须显式决策)
            call_target = None
            call_reason = ""
            call_source = ""
            if directives:
                for d in directives:
                    if d["type"] == "call":
                        call_target = d["target"]
                        call_reason = d["reason"]
                        call_source = d.get("source", "tag")
                        break

            if call_target and call_target != npc_name:
                # 显示来源 (tool call / tag) — 调试用
                source_tag = f" [{call_source}]" if call_source else ""
                interruption_npc = call_target
                reason_text = f" ({call_reason})" if call_reason else ""
                print(f"  {AMBER}💬 {interruption_npc} wants to speak{reason_text}{RESET}")
                user_choice = input(f"  {DIM}[Enter] to hear / [s] to skip: {RESET}").strip().lower()

                if user_choice in ("", "y", "yes"):
                    # 用户允许: 强制让指定 NPC 说话
                    engine.force_next_speaker(interruption_npc)

                    interruption_printer = StreamingPrinter()
                    int_directives = []
                    try:
                        # 用原 user_text 让 NPC 看到完整上下文
                        int_name, int_content, int_directives = await engine.stream_npc_response(
                            user_text,
                            on_start=lambda name: interruption_printer.start(
                                name, role=engine.npc_role_map.get(name, "")
                            ),
                            on_chunk=lambda text: interruption_printer.chunk(text),
                            on_complete=lambda name, content, dirs: interruption_printer.finish(),
                        )
                    except Exception as e:
                        print(f"  {DIM}⚠️  Interruption failed: {e}{RESET}")
                        int_name, int_content = "System", "..."
                elif user_choice in ("s", "skip"):
                    print(f"  {DIM}Skipped.{RESET}\n")
                    int_name, int_content = None, None
                else:
                    # 未知输入, 当作 skip
                    int_name, int_content = None, None

                # 打印插话 NPC 的格式化气泡 (含高亮 + 叮)
                if int_name and int_name != "System":
                    new_words2 = print_npc_bubble(
                        int_name, int_content,
                        role=engine.npc_role_map.get(int_name, ""),
                        target_vocab=target_vocab,
                        seen_vocab=seen_vocab,
                    )
                    for w in new_words2:
                        trans = engine.vocab_translation_map.get(w, "")
                        print_ding(w, trans)

    # ─── 8. 场景结束 ───
    print_session_summary(
        seen_vocab=seen_vocab,
        target_vocab=target_vocab,
        collected_vocab=engine.collected_vocab,
        total_turns=engine.total_turns,
        beat_history=beat_mgr.beat_history,
        total_beats=len(template['beats']),
    )

    # 关闭模型客户端
    await model_client.close()


def main():
    parser = argparse.ArgumentParser(description="LinguaScene Demo — 场景化多角色编排验证")
    parser.add_argument(
        "--cefr",
        type=str,
        default="B1",
        choices=["A1", "A2", "B1", "B2", "C1", "C2"],
        help="用户 CEFR 等级 (默认: B1)",
    )
    parser.add_argument(
        "--template",
        type=str,
        default=None,
        help="场景模板路径 (默认: templates/restaurant.json)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="显示 debug 信息 (prompt 报告、实例化报告等)",
    )
    args = parser.parse_args()

    # 确定模板路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = args.template or os.path.join(script_dir, "templates", "restaurant.json")

    if not os.path.exists(template_path):
        print(f"Error: Template not found: {template_path}")
        sys.exit(1)

    # 打印启动信息
    print(f"""
{BOLD}╔══════════════════════════════════════════════╗
║   🍽️  LinguaScene Demo v0.1                     ║
║   Scene-based Multi-role Orchestration           ║
╚══════════════════════════════════════════════╝{RESET}
    """)
    print(f"  CEFR Level: {args.cefr}")
    print(f"  Template:   {template_path}")
    print(f"  Debug:      {'ON' if args.debug else 'OFF'}")

    # 运行场景
    asyncio.run(run_scene(
        template_path=template_path,
        cefr_level=args.cefr,
        debug=args.debug,
    ))


if __name__ == "__main__":
    main()
