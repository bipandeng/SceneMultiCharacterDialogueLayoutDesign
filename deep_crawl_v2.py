#!/usr/bin/env python3
"""
AutoGen 文档深度爬取脚本（使用 httpx，无需浏览器）
"""

import asyncio
import os
import re
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
import html2text

# 配置
BASE_URL = "https://microsoft.github.io/autogen/stable/"
OUTPUT_DIR = "/Users/panda/obsidian/firecrawler/autogen/deep-crawl"
MAX_PAGES = 50
VISITED = set()

# 种子 URL
SEED_URLS = [
    "https://microsoft.github.io/autogen/stable/index.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html",
    "https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/index.html",
    "https://microsoft.github.io/autogen/stable/reference/index.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/installation.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/messages.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/models.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/human-in-the-loop.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/selector-group-chat.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/memory.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/logging.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/custom-agents.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/serialize-components.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/graph-flow.html",
    "https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/quickstart.html",
    "https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/intro.html",
    "https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/group-chat.html",
    "https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/reflection.html",
    "https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/multi-agent-debate.html",
    "https://microsoft.github.io/autogen/stable/user-guide/extensions-user-guide/index.html",
    "https://microsoft.github.io/autogen/stable/user-guide/extensions-user-guide/discover.html",
    "https://microsoft.github.io/autogen/stable/user-guide/extensions-user-guide/create-your-own.html",
    "https://microsoft.github.io/autogen/stable/user-guide/autogenstudio-user-guide/index.html",
]


def sanitize_filename(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path or path == "stable":
        return "index.md"
    filename = re.sub(r'[<>:"/\\|?*]', '_', path)
    filename = filename.replace("/", "_")
    return f"{filename}.md"


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    if not parsed.netloc.endswith("microsoft.github.io"):
        return False
    if "/autogen/stable/" not in url:
        return False
    exclude_patterns = [
        "_sources/", "_modules/", "search.html", ".ipynb",
        ".png", ".jpg", ".gif", ".pdf", ".zip", "#"
    ]
    for pattern in exclude_patterns:
        if pattern in url:
            return False
    return True


def html_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for elem in soup.find_all(["nav", "footer", "script", "style", "header"]):
        elem.decompose()

    main_content = soup.find("main") or soup.find("article") or soup.find("div", class_="content") or soup.body

    if main_content is None:
        main_content = soup

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0

    markdown = h.handle(str(main_content))
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    return markdown.strip()


async def crawl_page(client: httpx.AsyncClient, url: str) -> list:
    if url in VISITED or len(VISITED) >= MAX_PAGES:
        return []

    VISITED.add(url)
    print(f"[{len(VISITED)}/{MAX_PAGES}] 爬取: {url}", flush=True)

    try:
        response = await client.get(url, timeout=30.0, follow_redirects=True)
        response.raise_for_status()

        if "text/html" not in response.headers.get("content-type", ""):
            return []

        markdown = html_to_markdown(response.text)

        filename = sanitize_filename(url)
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"<!-- 来源: {url} -->\n\n")
            f.write(markdown)

        print(f"  ✅ 保存: {filename} ({len(markdown)} 字符)", flush=True)

        # 发现新链接
        soup = BeautifulSoup(response.text, "html.parser")
        discovered_links = []
        for link in soup.find_all("a", href=True):
            full_url = urljoin(url, link["href"])
            full_url = full_url.split("#")[0]
            if is_valid_url(full_url) and full_url not in VISITED:
                discovered_links.append(full_url)

        return discovered_links

    except Exception as e:
        print(f"  ❌ 错误: {str(e)[:100]}", flush=True)
        return []


async def deep_crawl():
    print("=" * 60)
    print("AutoGen 文档深度爬取")
    print("=" * 60, flush=True)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    async with httpx.AsyncClient(headers=headers) as client:
        queue = list(SEED_URLS)
        all_discovered = []

        while queue and len(VISITED) < MAX_PAGES:
            url = queue.pop(0)
            links = await crawl_page(client, url)
            all_discovered.extend(links)

            for link in all_discovered:
                if link not in VISITED and link not in queue:
                    queue.append(link)
            all_discovered = []

            await asyncio.sleep(0.5)

    print("=" * 60, flush=True)
    print(f"爬取完成！共爬取 {len(VISITED)} 个 URL", flush=True)
    print(f"文件保存在: {OUTPUT_DIR}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    asyncio.run(deep_crawl())
