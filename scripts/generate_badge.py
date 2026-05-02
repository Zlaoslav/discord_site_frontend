#!/usr/bin/env python3
"""Generate a dark SVG badge from the daily_ping API and write to daily_ping/badge.svg.

Runs in CI (GitHub Actions) or locally.
"""
import json
import os
import urllib.request
from datetime import datetime

API_URL = "https://pollpi.slavi.workers.dev/daily_ping"
OUT_PATH = os.path.join("daily_ping", "badge.svg")

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "daily-ping-badge/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

def to_int(v):
    try:
        return int(v)
    except Exception:
        return 0

def fmt_num(n):
    return f"{n:,}".replace(",", " ")

def generate_svg(data):
    ld = to_int(data.get("last_day", 0))
    lm = to_int(data.get("last_month", 0))
    ly = to_int(data.get("last_year", 0))
    at = to_int(data.get("all_time", 0))
    updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    width = 520
    height = 110
    pad = 16
    left_w = 160
    avail = width - pad * 2 - left_w
    cw = avail / 4
    x0 = pad + left_w

    svg = f"""<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="bg" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0" stop-color="#0f1724"/>
      <stop offset="1" stop-color="#07070a"/>
    </linearGradient>
  </defs>
  <rect rx="14" width="{width}" height="{height}" fill="url(#bg)"/>
  <g font-family="Inter, system-ui, -apple-system, 'Segoe UI', Roboto, Arial" fill="#fff">
    <g transform="translate({pad+12},28)">
      <text x="0" y="0" font-size="12" fill="#9aa0a6">Daily ping</text>
      <text x="0" y="28" font-size="20" font-weight="700">{fmt_num(ld)}</text>
    </g>
"""

    labels = [("Last day", ld), ("Last month", lm), ("Last year", ly), ("All time", at)]
    for i, (label, val) in enumerate(labels):
        x = x0 + i * cw
        svg += (
            f'  <g transform="translate({x:.1f},22)">\n'
            f'      <text x="0" y="0" font-size="16" font-weight="700">{fmt_num(val)}</text>\n'
            f'      <text x="0" y="22" font-size="10" fill="#9aa0a6">{label}</text>\n'
            '    </g>\n'
        )

    svg += f"  <text x=\"{pad}\" y=\"{height-12}\" font-size=\"10\" fill=\"#9aa0a6\">Updated: {updated}</text>\n"
    svg += "</g>\n</svg>\n"
    return svg

def main():
    try:
        data = fetch_json(API_URL)
    except Exception as e:
        print("Failed to fetch API:", e)
        data = {}

    svg = generate_svg(data)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print("Wrote", OUT_PATH)

if __name__ == '__main__':
    main()
