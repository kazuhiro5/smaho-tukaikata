#!/usr/bin/env python3
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

LINE_NOTIFY_TOKEN = os.environ["LINE_NOTIFY_TOKEN"]

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


def send_line_notify(message: str) -> None:
    data = urllib.parse.urlencode({"message": message}).encode()
    req = urllib.request.Request(
        "https://notify-api.line.me/api/notify",
        data=data,
        headers={"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status != 200:
            raise RuntimeError(f"LINE Notify error: {resp.status}")


def main() -> None:
    now = datetime.now(JST)
    lines = [f"\n🌍 {now.strftime('%Y年%m月%d日')} 朝の国際ニュース\n"]

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

    message = "\n".join(lines)
    send_line_notify(message)
    print("送信完了")


if __name__ == "__main__":
    main()
