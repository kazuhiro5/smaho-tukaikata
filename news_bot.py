#!/usr/bin/env python3
import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
USER_ID = os.environ["LINE_USER_ID"]

# NHK国際ニュース RSS
RSS_URLS = [
    ("NHK国際", "https://www3.nhk.or.jp/rss/news/cat6.xml"),
]

JST = timezone(timedelta(hours=9))


def fetch_rss(url: str, max_items: int = 5) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "NewsBot/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        tree = ET.parse(resp)
    root = tree.getroot()
    channel = root.find("channel")
    items = []
    for item in (channel or root).findall("item")[:max_items]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if title:
            items.append({"title": title, "link": link})
    return items


def send_line_message(text: str) -> None:
    payload = json.dumps({
        "to": USER_ID,
        "messages": [{"type": "text", "text": text}],
    }).encode()
    req = urllib.request.Request(
        "https://api.line.me/v2/bot/message/push",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Messaging API error: {resp.status}")


def main() -> None:
    now = datetime.now(JST)
    lines = [f"🌍 {now.strftime('%Y年%m月%d日')} 朝の国際ニュース\n"]

    for label, url in RSS_URLS:
        try:
            items = fetch_rss(url)
        except Exception as e:
            lines.append(f"[{label}] 取得失敗: {e}\n")
            continue

        lines.append(f"【{label}】")
        for i, item in enumerate(items, 1):
            lines.append(f"{i}. {item['title']}")
            if item["link"]:
                lines.append(f"   {item['link']}")
        lines.append("")

    send_line_message("\n".join(lines))
    print("送信完了")


if __name__ == "__main__":
    main()
