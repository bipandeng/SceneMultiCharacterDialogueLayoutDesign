#!/usr/bin/env python3
"""
AutoGen 文档深度爬取脚本
- 从种子 URL 开始
- 发现并爬取所有内部链接
- 保存为 Markdown 文件
"""

import asyncio
import os
import re
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# 配置
BASE_URL = "https://microsoft.github.io/autogen/stable/"
OUTPUT_DIR = "/Users/panda/obsidian/firecrawler/autogen/deep-crawl"
MAX_PAGES = 100  # 最大爬取页面数
VISITED = set()  # 已访问的 URL

# 种子 URL
SEED_URLS = [
    "https://microsoft.github.io/autogen/stable/index.html",
    "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html",
    "https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/index.html",
    "https://microsoft.github.io/autogen/stable/reference/index.html",
]


def sanitize_filename(url: str) -> str:
    """将 URL 转换为文件名"""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path or path == "stable":
        return "index.md"
    # 替换特殊字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', path)
    filename = filename.replace("/", "_")
    return f"{filename}.md"


def is_valid_url(url: str) -> bool:
    """检查是否是有效的内部链接"""
    parsed = urlparse(url)
    # 只爬取同一域名下的页面
    if not parsed.netloc.endswith("microsoft.github.io"):
        return False
    # 只爬取 autogen 文档
    if "/autogen/stable/" not in url:
        return False
    # 排除某些路径
    exclude_patterns = [
        "_sources/", "_modules/", "search.html", ".ipynb",
        ".png", ".jpg", ".gif", ".pdf", ".zip"
    ]
    for pattern in exclude_patterns:
        if pattern in url:
            return False
    return True


async def crawl_page(crawler, url: str, depth: int = 0) -> list:
    """爬取单个页面并发现链接"""
    if url in VISITED or len(VISITED) >= MAX_PAGES:
        return []

    VISITED.add(url)
    print(f"[{len(VISITED)}/{MAX_PAGES}] 爬取: {url}")

    try:
        config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            excluded_tags=["nav", "footer", "aside", "script", "style"],
            remove_overlay_elements=True,
            page_timeout=30000,
        )

        result = await crawler.arun(url=url, config=config)

        if result.success:
            # 保存 Markdown
            filename = sanitize_filename(url)
            filepath = os.path.join(OUTPUT_DIR, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# 来源: {url}\n\n")
                f.write(result.markdown)

            print(f"  ✅ 保存: {filename} ({len(result.markdown)} 字符)")

            # 提取内部链接
            discovered_links = []
            if result.links and "internal" in result.links:
                for link in result.links["internal"]:
                    if isinstance(link, dict):
                        link_url = link.get("href", "")
                    else:
                        link_url = str(link)

                    # 转换为绝对 URL
                    full_url = urljoin(url, link_url)
                    if is_valid_url(full_url) and full_url not in VISITED:
                        discovered_links.append(full_url)

            return discovered_links
        else:
            print(f"  ❌ 失败: {result.error_message}")
            return []

    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
        return []


async def deep_crawl():
    """深度爬取主函数"""
    print("=" * 60)
    print("AutoGen 文档深度爬取")
    print("=" * 60)

    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 浏览器配置
    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1920,
        viewport_height=1080,
        use_managed_browser=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # 使用 BFS 进行深度爬取
        queue = list(SEED_URLS)
        all_discovered = []

        while queue and len(VISITED) < MAX_PAGES:
            # 取出一批 URL 进行爬取
            batch = queue[:5]  # 每批 5 个
            queue = queue[5:]

            # 爬取当前批次
            for url in batch:
                links = await crawl_page(crawler, url)
                all_discovered.extend(links)

            # 将新发现的链接加入队列
            for link in all_discovered:
                if link not in VISITED and link not in queue:
                    queue.append(link)
            all_discovered = []

            # 避免请求过快
            await asyncio.sleep(1)

    print("=" * 60)
    print(f"爬取完成！共爬取 {len(VISITED)} 个页面")
    print(f"文件保存在: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(deep_crawl())
