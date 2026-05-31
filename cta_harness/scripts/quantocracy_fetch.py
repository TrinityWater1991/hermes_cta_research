#!/usr/bin/env python3
"""Quantocracy RSS 每日研报拉取脚本。

通过 SOCKS5 代理拉取 Quantocracy RSS feed，检查是否有新的每日汇总，
输出新的汇总页 URL 列表，供 pipeline 的 web_extract 消费。

用法:
    python scripts/quantocracy_fetch.py              # 输出所有新汇总页 URL
    python scripts/quantocracy_fetch.py --mark-read  # 输出后标记为已读
    python scripts/quantocracy_fetch.py --json       # JSON 格式输出
"""

import json
import os
from pathlib import Path

import feedparser
import httpx
from httpx_socks import AsyncProxyTransport

FEED_URL = "https://feeds.feedburner.com/Quantocracy"
STATE_FILE = Path(__file__).parent.parent / "data" / "quantocracy_state.json"
PROXY_URL = "socks5://127.0.0.1:10080"


def load_state() -> dict[str, str]:
    """加载已处理状态: {date_str: summary_url, ...}."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict[str, str]) -> None:
    """保存已处理状态."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


async def fetch_feed() -> list[dict]:
    """通过 SOCKS5 代理拉取 RSS feed，返回新条目列表."""
    transport = AsyncProxyTransport.from_url(PROXY_URL)
    async with httpx.AsyncClient(transport=transport, timeout=30) as client:
        resp = await client.get(FEED_URL)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)

    entries = []
    for entry in feed.entries:
        # 提取发布日期 (published_parsed 是 9-tuple: (y,m,d,h,m,s,wday,yday,isdst))
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        if published and isinstance(published, tuple) and len(published) >= 6:
            date_str = f"{published[0]:04d}-{published[1]:02d}-{published[2]:02d}"
        else:
            date_str = "unknown"

        entries.append({
            "title": entry.title,
            "url": entry.link,
            "date": date_str,
            "summary": entry.get("summary", ""),
        })

    return entries


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Quantocracy RSS 拉取")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--mark-read", action="store_true", help="输出后标记为已读")
    args = parser.parse_args()

    import asyncio

    entries = asyncio.run(fetch_feed())
    state = load_state()

    new_entries = []
    for entry in entries:
        if entry["date"] not in state:
            new_entries.append(entry)

    if args.json:
        print(json.dumps(new_entries, indent=2, ensure_ascii=False))
    else:
        if not new_entries:
            print("[Quantocracy] 无新汇总")
            return

        print(f"[Quantocracy] {len(new_entries)} 个新汇总:\n")
        for entry in new_entries:
            print(f"  {entry['date']}  {entry['title']}")
            print(f"  → {entry['url']}\n")

    if args.mark_read and new_entries:
        for entry in new_entries:
            state[entry["date"]] = entry["url"]
        save_state(state)
        print(f"已标记 {len(new_entries)} 条为已读")


if __name__ == "__main__":
    main()
