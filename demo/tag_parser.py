"""
Tag 解析器 — 从 NPC 输出中提取 Director Mode 标签

支持的标签:
  [CALL:ColleagueName] reason      → 调用同事
  [CALL:ColleagueName]             → 调用同事 (无原因)

后续可扩展:
  [EMOTE:smile]                    → 表情提示
  [GUIDE:topic]                    → 引导用户进入某话题
  [DONE]                           → 结束当前 beat
"""

import re

# 匹配 [CALL:Name] 或 [CALL:Name] reason
CALL_PATTERN = re.compile(r'\[CALL:([A-Za-z_][A-Za-z0-9_]*)\]\s*([^\n\r\[\]]*)', re.IGNORECASE)


def parse_directive_tags(content: str) -> tuple[str, list[dict]]:
    """
    解析 NPC 回复中的 Director Mode 标签。

    Args:
        content: NPC 的完整原始输出 (含 thinking + tags)

    Returns:
        (clean_content, directives)
        - clean_content: 去掉所有 [CALL:X] 标签后的内容
        - directives: 解析出的指令列表
          [{"type": "call", "target": "Antonio", "reason": "user ordered osso buco"}]
    """
    directives = []
    for match in CALL_PATTERN.finditer(content):
        target = match.group(1).strip()
        reason = match.group(2).strip()
        directives.append({
            "type": "call",
            "target": target,
            "reason": reason,
        })

    # 从显示内容中移除所有 [CALL:X] 行
    clean = CALL_PATTERN.sub('', content)

    # 清理可能残留的空行
    clean = re.sub(r'\n{3,}', '\n\n', clean).strip()

    return clean, directives


def has_call_directive(directives: list[dict]) -> bool:
    """检查是否有 [CALL] 指令"""
    return any(d["type"] == "call" for d in directives)


def get_call_target(directives: list[dict]) -> str | None:
    """获取第一个 [CALL] 指令的目标 NPC 名字"""
    for d in directives:
        if d["type"] == "call":
            return d["target"]
    return None