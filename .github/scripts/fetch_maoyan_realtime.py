#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
猫眼实时票房抓取（box-office 页面版）
从 box-office?ver=normal 页面提取 AppData JSON，输出结构化数据：
{
  "fetch_time": "2026-08-11 20:00:00",
  "summary": {...},
  "daily": {...},
  "hourly": {...},
  "prediction": {...}
}
用法: python3 fetch_maoyan_realtime.py
输出: 仓库根目录 maoyan-realtime.json
"""
import json
import re
import sys
import datetime
import urllib.request

MOVIE_ID = "1462628"
BOX_URL = "https://piaofang.maoyan.com/box-office?ver=normal"
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
OUTPUT = "maoyan-realtime.json"


def http_get(url: str, headers: dict = None, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Referer": "https://piaofang.maoyan.com/",
        **(headers or {}),
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_appdata(html: str) -> dict:
    """从 HTML 中提取 var AppData = {...} JSON"""
    marker = "var AppData = "
    start = html.find(marker)
    if start < 0:
        raise ValueError("页面中未找到 AppData")
    src = html[start + len(marker):]
    # 逐字符配平 JSON（处理嵌套大括号和字符串转义）
    depth = 0
    in_str = False
    esc = False
    end = -1
    for i, ch in enumerate(src):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
    if end < 0:
        raise ValueError("AppData JSON 解析失败")
    return json.loads(src[:end])


def main():
    try:
        html = http_get(BOX_URL, timeout=25)
        app_data = extract_appdata(html)
        box = app_data["pageData"]["boxOffice"]

        # list: 当日各影片排行（首位 = 欢迎来龙餐馆）
        movies = []
        for item in box.get("list", []):
            info = item.get("movieInfo", {})
            movies.append({
                "movieName": info.get("movieName"),
                "releaseInfo": info.get("releaseInfo"),
                "boxDesc": item.get("boxDesc"),          # 今日综合票房（万）
                "boxRate": item.get("boxRate"),          # 大盘占比
                "showCountRate": item.get("showCountRate"),  # 排片占比
                "seatCountRate": item.get("seatCountRate"),  # 排座占比
                "sumBoxDesc": item.get("sumBoxDesc"),    # 累计票房
            })

        national = box.get("nationalBox", {})
        update = box.get("updateInfo", {})

        result = {
            "fetch_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "movie_id": MOVIE_ID,
            "source": "box-office?ver=normal",
            "update_time": f"{update.get('date', '')} {update.get('time', '')}" if update else None,
            "national_box_wan": float(national.get("num")) if national.get("num") else None,
            "movies": movies,
            "my_movie": movies[0] if movies else None,  # 首位即欢迎来龙餐馆
        }

        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"[OK] 猫眼实时数据已写入 {OUTPUT}")
        if result["my_movie"]:
            m = result["my_movie"]
            print(f"     {m['movieName']}: {m['boxDesc']}万 占比{m['boxRate']} 累计{m['sumBoxDesc']}")
            print(f"     更新时间: {result['update_time']}")

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
