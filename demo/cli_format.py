"""
CLI 格式化输出 — 终端里的"iMessage 风格"

功能:
  • NPC 气泡框 (角色名 + 内容)
  • 目标词高亮 (🌟word🌟)
  • Beat 进度条
  • "叮" 提示 (首次遇到目标词)
  • Beat 推进通知
  • 场景头部信息
"""

import shutil
import sys

# ANSI 颜色
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
AMBER = "\033[33m"      # 目标词高亮
GREEN = "\033[32m"      # 完成/收藏
BLUE = "\033[34m"       # 信息
CYAN = "\033[36m"       # 用户
MAGENTA = "\033[35m"    # beat 推进
RED = "\033[31m"        # 警告
WHITE = "\033[97m"


def get_terminal_width() -> int:
    """获取终端宽度, 默认 80"""
    try:
        return min(shutil.get_terminal_size().columns, 80)
    except Exception:
        return 80


def print_scene_header(
    scene_name: str,
    target_vocab: list[str],
    beat_progress: str,
    current_beat_name: str,
) -> None:
    """打印场景头部信息"""
    w = get_terminal_width()
    print()
    print(f"{BOLD}{'═' * w}{RESET}")
    print(f"{BOLD}  🍽️  {scene_name}{RESET}")
    print(f"  Beat: {beat_progress}  {DIM}({current_beat_name}){RESET}")
    print(f"  Target words: {'  '.join(f'{AMBER}{w}{RESET}' for w in target_vocab)}")
    print(f"{BOLD}{'═' * w}{RESET}")
    print()


def print_npc_bubble(
    npc_name: str,
    content: str,
    role: str = "",
    target_vocab: list[str] | None = None,
    seen_vocab: set | None = None,
) -> list[str]:
    """
    打印 NPC 消息气泡。

    Returns:
        新遇到的目标词列表 (用于触发 "叮")
    """
    w = get_terminal_width()
    target_vocab = target_vocab or []
    # ⚠️ 必须用 `is None` 判断,不能用 `or set()`
    # 空 set 在 Python 里是 falsy, `set() or set()` 会返回新空 set,
    # 导致 seen_vocab.add() 加到临时变量,主循环里的 set 永远是空的
    if seen_vocab is None:
        seen_vocab = set()

    # 高亮目标词 + 检测新词
    new_words = []
    highlighted_content = content
    for word in target_vocab:
        if word.lower() in content.lower():
            if word not in seen_vocab:
                new_words.append(word)
                seen_vocab.add(word)
            # 高亮替换 (大小写不敏感)
            import re
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            highlighted_content = pattern.sub(f"{AMBER}{BOLD}☞{word}☜{RESET}", highlighted_content)

    # 角色标签
    role_tag = f" {DIM}({role}){RESET}" if role else ""

    # 打印气泡
    print(f"  {BOLD}{CYAN}┌─ {npc_name}{role_tag} {'─' * max(0, w - len(npc_name) - len(role) - 6)}{RESET}")
    # 分行打印内容 (按终端宽度自动换行)
    for line in _wrap_text(highlighted_content, w - 6):
        print(f"  {CYAN}│{RESET} {line}")
    print(f"  {BOLD}{CYAN}└{'─' * (w - 2)}{RESET}")
    print()

    return new_words


def print_ding(word: str, translation_zh: str = "") -> None:
    """打印 "叮" — 首次遇到目标词"""
    trans = f" ({translation_zh})" if translation_zh else ""
    print(f"     {AMBER}✨ ✨ ✨{RESET}")
    print(f"     {AMBER}{BOLD}New word: {word}{trans}{RESET}")
    print()


def print_user_message(text: str) -> None:
    """打印用户消息"""
    w = get_terminal_width()
    print(f"  {BOLD}{GREEN}┌{'─' * (w - 2)}{RESET}")
    for line in _wrap_text(text, w - 6):
        print(f"  {GREEN}│{RESET}  {BOLD}{line}{RESET}")
    print(f"  {GREEN}└─ You {'─' * max(0, w - len('You') - 5)}{RESET}")
    print()


def print_beat_advance(from_beat: str, to_beat: str) -> None:
    """打印 beat 推进通知"""
    print(f"     {MAGENTA}▶▶▶ Beat: {from_beat} → {to_beat}{RESET}")
    print()


def print_beat_done() -> None:
    """打印所有 beat 完成"""
    print(f"     {GREEN}{BOLD}🎉 All beats completed!{RESET}")
    print()


def print_guide_hint(hint: str) -> None:
    """打印 NPC 引导提示 (debug 信息)"""
    print(f"  {DIM}💡 [guide: {hint}]{RESET}")
    print()


def print_vocab_used(word: str) -> None:
    """打印用户使用了目标词"""
    print(f"     {GREEN}✅ Nice use of '{word}'!{RESET}")
    print()


def print_session_summary(
    seen_vocab: set,
    target_vocab: list[str],
    collected_vocab: set,
    total_turns: int,
    beat_history: list[dict],
    total_beats: int,
) -> None:
    """打印场景结束总结"""
    w = get_terminal_width()
    print()
    print(f"{BOLD}{'═' * w}{RESET}")
    print(f"{BOLD}  📊 Session Summary{RESET}")
    print(f"{BOLD}{'═' * w}{RESET}")

    # Beat 完成情况
    print(f"  Beats completed: {len(beat_history)}/{total_beats}")
    for bh in beat_history:
        auto = " (auto)" if bh.get("auto_advanced") else ""
        print(f"    ✅ {bh['beat_id']} ({bh['turns_spent']} turns{auto})")

    # 目标词覆盖
    encountered = set(target_vocab) & seen_vocab
    print(f"\n  Target words encountered: {len(encountered)}/{len(target_vocab)}")
    for w_name in target_vocab:
        status = "✅" if w_name in encountered else "⬜"
        print(f"    {status} {w_name}")

    # 收藏
    print(f"\n  Words collected: {len(collected_vocab)}")
    for w_name in collected_vocab:
        print(f"    📌 {w_name}")

    # 总轮数
    print(f"\n  Total turns: {total_turns}")
    print(f"{BOLD}{'═' * w}{RESET}")
    print()


# ─── Streaming 工具 ──────────────────────────────────────────────


class StreamingPrinter:
    """
    实时流式打印助手 — 在终端里模拟"打字机"效果。

    工作流程:
      1. start(npc_name) → 打印 "[Name] is typing..." 占位符
      2. chunk(text)     → 实时输出 token, 替换占位符区域
      3. finish()        → 结束当前行,准备打印完整气泡
    """

    def __init__(self):
        self.npc_name: str | None = None
        self.role: str = ""
        self.started = False
        self.accumulated = ""

    def start(self, npc_name: str, role: str = "") -> None:
        """开始流式输出 — 打印 NPC 占位符"""
        self.npc_name = npc_name
        self.role = role
        self.accumulated = ""
        role_tag = f" {DIM}({role}){RESET}" if role else ""
        # 占位符: [Marco (waiter)] ✎
        sys.stdout.write(f"\n  {BOLD}{CYAN}[{npc_name}]{role_tag} {DIM}✎ typing...{RESET}")
        sys.stdout.flush()
        self.started = True

    def chunk(self, text: str) -> None:
        """输出一个 streaming chunk (直接 append 到当前行)"""
        if not self.started:
            return
        self.accumulated += text
        sys.stdout.write(f"{CYAN}{text}{RESET}")
        sys.stdout.flush()

    def finish(self) -> None:
        """流结束 — 换行,准备打印气泡"""
        if self.started:
            sys.stdout.write("\n")
            sys.stdout.flush()
            self.started = False

    @staticmethod
    def clear_line() -> None:
        """清空当前行 (ANSI)"""
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()


def _wrap_text(text: str, width: int) -> list[str]:
    """简单的文本换行"""
    if width <= 0:
        width = 40
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        # 粗略计算可见字符长度 (去掉 ANSI 转义)
        visible = _strip_ansi(current_line + " " + word).strip()
        if len(visible) > width and current_line:
            lines.append(current_line)
            current_line = word
        else:
            current_line = f"{current_line} {word}".strip()
    if current_line:
        lines.append(current_line)
    return lines or [""]


def _strip_ansi(text: str) -> str:
    """去掉 ANSI 转义序列"""
    import re
    return re.sub(r'\033\[[0-9;]*m', '', text)
