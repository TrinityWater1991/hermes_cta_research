"""
Substack文章爬虫

从Substack网站抓取文章并保存为Markdown文件到raw/articles/目录。

用法：
    # 列出文章
    python scripts/fetch_articles.py --url https://www.quantitativo.com/ --list

    # 下载所有免费文章
    python scripts/fetch_articles.py --url https://www.quantitativo.com/ --download all-free

    # 下载指定文章（按序号）
    python scripts/fetch_articles.py --url https://www.quantitativo.com/ --download 1,3,5-8

    # 下载全部（含付费文章截断版本）
    python scripts/fetch_articles.py --url https://www.quantitativo.com/ --download all --include-paid
"""
import argparse
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "raw" / "articles"
PAGE_SIZE = 12
DEFAULT_DELAY = 1.5
MAX_RETRIES = 3


def parse_publication_url(url: str) -> str:
    """从URL提取publication域名"""
    if not url.startswith("http"):
        return f"{url}.substack.com"
    parsed = urlparse(url.rstrip("/"))
    return parsed.hostname


def fetch_posts(domain: str, limit: int = PAGE_SIZE, offset: int = 0) -> list[dict] | None:
    """获取单页文章列表，带重试"""
    url = f"https://{domain}/api/v1/posts"
    params = {"limit": limit, "offset": offset}

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 429:
                wait = 2 ** (attempt + 2)
                print(f"  触发限流，等待{wait}秒后重试...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  请求失败: {e}")
                return None
    return None


def fetch_all_posts(domain: str, delay: float = DEFAULT_DELAY, max_posts: int = 0) -> list[dict]:
    """分页获取所有文章"""
    all_posts = []
    offset = 0

    while True:
        posts = fetch_posts(domain, limit=PAGE_SIZE, offset=offset)
        if not posts:
            break
        all_posts.extend(posts)
        print(f"  已获取 {len(all_posts)} 篇文章...")
        if max_posts and len(all_posts) >= max_posts:
            all_posts = all_posts[:max_posts]
            break
        offset += PAGE_SIZE
        time.sleep(delay)

    return all_posts


def html_to_markdown(html: str) -> str:
    """将Substack文章HTML转换为Markdown"""
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(class_=lambda c: c and any(
        x in c for x in ["subscription-widget", "subscribe-widget",
                         "share-button", "captioned-button", "button-wrapper"]
    )):
        tag.decompose()

    for p in soup.find_all("p"):
        if not p.get_text(strip=True) and not p.find("img"):
            p.decompose()

    text = md(
        str(soup),
        heading_style="ATX",
        bullets="-",
        strip=["script", "style"],
    )

    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build_frontmatter(post: dict) -> str:
    """构建YAML frontmatter"""
    post_date = datetime.fromisoformat(post["post_date"].replace("Z", "+00:00"))
    tags = [t["name"] for t in post.get("postTags", [])] if post.get("postTags") else []
    authors = [b.get("name", "") for b in post.get("publishedBylines", [])]
    author = authors[0] if authors else "Unknown"

    title_escaped = post["title"].replace('"', '\\"')
    lines = ["---", f'title: "{title_escaped}"']

    if post.get("subtitle"):
        subtitle_escaped = post["subtitle"].replace('"', '\\"')
        lines.append(f'subtitle: "{subtitle_escaped}"')

    lines.extend([
        f"date: {post_date.strftime('%Y-%m-%d')}",
        f"author: {author}",
        f"source_url: {post['canonical_url']}",
    ])

    if tags:
        lines.append("tags:")
        for tag in tags:
            lines.append(f"  - {tag}")

    lines.extend([
        f"audience: {post['audience']}",
        f"wordcount: {post.get('wordcount', 0)}",
        f"fetched_at: {datetime.now().strftime('%Y-%m-%d')}",
        "---",
    ])
    return "\n".join(lines)


def article_filename(post: dict) -> str:
    """生成文章文件名: YYYY-MM-DD_slug.md"""
    post_date = datetime.fromisoformat(post["post_date"].replace("Z", "+00:00"))
    return f"{post_date.strftime('%Y-%m-%d')}_{post['slug']}.md"


def save_article(post: dict, output_dir: Path) -> Path | None:
    """保存文章为Markdown文件，返回文件路径"""
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = article_filename(post)
    filepath = output_dir / filename

    if filepath.exists():
        return None

    frontmatter = build_frontmatter(post)
    body_html = post.get("body_html", "")

    if not body_html:
        content = f"{frontmatter}\n\n# {post['title']}\n\n> 内容为空（可能为付费文章）\n"
    else:
        body_md = html_to_markdown(body_html)
        content = f"{frontmatter}\n\n# {post['title']}\n\n{body_md}\n"

    filepath.write_text(content, encoding="utf-8")
    return filepath


def parse_selection(selection: str, total: int) -> list[int]:
    """解析用户选择字符串，返回0-based索引列表"""
    if selection == "all":
        return list(range(total))
    if selection == "all-free":
        return None

    indices = []
    for part in selection.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            start_idx = int(start) - 1
            end_idx = int(end) - 1
            indices.extend(range(start_idx, end_idx + 1))
        else:
            indices.append(int(part) - 1)

    return [i for i in indices if 0 <= i < total]


def list_articles(posts: list[dict]):
    """打印文章列表"""
    print(f"\n共 {len(posts)} 篇文章:\n")
    print(f"{'序号':>4}  {'日期':<12} {'状态':<6} {'字数':>6}  标题")
    print("-" * 80)
    for i, post in enumerate(posts, 1):
        post_date = datetime.fromisoformat(post["post_date"].replace("Z", "+00:00"))
        date_str = post_date.strftime("%Y-%m-%d")
        audience = "免费" if post["audience"] == "everyone" else "付费"
        wordcount = post.get("wordcount", 0)
        title = post["title"][:50]
        print(f"{i:>4}  {date_str:<12} {audience:<6} {wordcount:>6}  {title}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Substack文章爬虫")
    parser.add_argument("--url", required=True, help="Substack网站URL")
    parser.add_argument("--list", action="store_true", dest="list_only", help="仅列出文章")
    parser.add_argument("--download", help="下载选择: all, all-free, 或序号如 1,3,5-8")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR, help="输出目录")
    parser.add_argument("--limit", type=int, default=0, help="最多获取文章数（0=全部）")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="请求间隔秒数")
    parser.add_argument("--include-paid", action="store_true", help="包含付费文章（截断版本）")
    args = parser.parse_args()

    if not args.list_only and not args.download:
        parser.error("请指定 --list 或 --download")

    domain = parse_publication_url(args.url)
    print(f"正在获取 {domain} 的文章列表...")

    posts = fetch_all_posts(domain, delay=args.delay, max_posts=args.limit)
    if not posts:
        print("错误：未获取到任何文章，请检查URL是否正确")
        return

    if args.list_only:
        list_articles(posts)
        return

    selection = args.download
    indices = parse_selection(selection, len(posts))

    if indices is None:
        selected = [p for p in posts if p["audience"] == "everyone"]
    else:
        selected = [posts[i] for i in indices]

    if not args.include_paid:
        paid_count = sum(1 for p in selected if p["audience"] != "everyone")
        selected = [p for p in selected if p["audience"] == "everyone"]
        if paid_count:
            print(f"  跳过 {paid_count} 篇付费文章（使用 --include-paid 包含）")

    print(f"\n准备下载 {len(selected)} 篇文章到 {args.output}/\n")

    downloaded = 0
    skipped = 0
    for i, post in enumerate(selected, 1):
        title = post["title"][:40]
        filepath = save_article(post, args.output)
        if filepath:
            print(f"  [{i}/{len(selected)}] 已保存: {filepath.name}")
            downloaded += 1
        else:
            print(f"  [{i}/{len(selected)}] 已跳过（文件已存在）: {title}")
            skipped += 1

        if i < len(selected):
            time.sleep(0.1)

    print(f"\n完成: 下载 {downloaded} 篇, 跳过 {skipped} 篇")


if __name__ == "__main__":
    main()
