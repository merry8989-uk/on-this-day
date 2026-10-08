#!/usr/bin/env python3
"""Build the On This Day static site from data/*.json.

Generates:
  - index.html          (homepage: latest day + archive list)
  - days/<date>.html    (one page per day)

Run from the repository root:  python scripts/build.py
"""
import html
import json
import os
import re
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
DAYS_DIR = os.path.join(ROOT, "days")

SITE_NAME = "On This Day in History"
SITE_NAME_HI = "आज का इतिहास"


def esc(s):
    return html.escape(s or "", quote=True)


def fmt_display(date_str):
    """2026-10-08 -> 08/10/2026"""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%d/%m/%Y")
    except ValueError:
        return date_str


def load_days():
    days = []
    if not os.path.isdir(DATA_DIR):
        return days
    for name in sorted(os.listdir(DATA_DIR)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
            try:
                d = json.load(f)
            except json.JSONDecodeError:
                continue
        d.setdefault("date", name[:-5])
        days.append(d)
    days.sort(key=lambda d: d["date"], reverse=True)
    return days


def render_event(ev):
    year = esc(str(ev.get("year", "")))
    hi = ev.get("hi", "").strip()
    en = ev.get("en", "").strip()
    src = ev.get("source", "").strip()
    parts = [f'<li><span class="yr">{year}</span><div class="body">']
    if hi:
        parts.append(f'<div class="hi">{esc(hi)}</div>')
    if en:
        cls = "en" if hi else "en en-only"
        parts.append(f'<div class="{cls}">{esc(en)}</div>')
    if src:
        parts.append(f'<div class="src">Source: {esc(src)}</div>')
    parts.append("</div></li>")
    return "".join(parts)


def render_picks(picks):
    if not picks:
        return ""
    items = []
    for p in picks:
        hi = esc(p.get("hi", ""))
        en = esc(p.get("en", ""))
        block = ""
        if hi:
            block += f'<div class="hi">{hi}</div>'
        if en:
            block += f'<div class="en">{en}</div>'
        items.append(f"<li>{block}</li>")
    return (
        '<section class="picks"><h2>Exam picks / परीक्षा चयन</h2>'
        f'<ul>{"".join(items)}</ul></section>'
    )


def page_shell(title, body, depth=0):
    """depth: 0 for root pages, 1 for pages inside /days/."""
    prefix = "../" if depth else ""
    return f"""<!doctype html>
<html lang="hi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{SITE_NAME} — daily bilingual history briefing (Hindi + English).">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<header class="site"><div class="wrap">
  <a class="brand" href="{prefix}index.html"><span>{SITE_NAME}</span><span class="hi">{SITE_NAME_HI}</span></a>
  <nav class="site"><a href="{prefix}index.html">Home / मुखपृष्ठ</a></nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site"><div class="wrap">
  <p>Bilingual history briefing — Hindi first, then English. Facts cross-checked against
  Wikipedia, Britannica, Library of Congress, HISTORY and other public sources.
  Compiled daily.</p>
</div></footer>
</body>
</html>
"""


def render_day_body(d):
    date = d["date"]
    display = fmt_display(date)
    events = d.get("events", [])
    ev_html = "".join(render_event(e) for e in events)
    body = f"""
<div class="dayhead">
  <div class="date">{esc(display)}</div>
  <div class="sub">{SITE_NAME} / {SITE_NAME_HI}</div>
</div>
<ol class="events">{ev_html}</ol>
{render_picks(d.get("exam_picks"))}
<p class="note"><a href="../index.html">&larr; All days / सभी दिन</a></p>
"""
    return body


def render_day_page(d):
    display = fmt_display(d["date"])
    return page_shell(f"{display} — {SITE_NAME}", render_day_body(d), depth=1)


def render_index(days):
    if not days:
        return page_shell(SITE_NAME, "<p>No briefings yet.</p>", depth=0)

    latest = days[0]
    display = fmt_display(latest["date"])

    archive_items = []
    for d in days:
        dd = fmt_display(d["date"])
        n = len(d.get("events", []))
        archive_items.append(
            f'<li><a href="days/{esc(d["date"])}.html">'
            f'<span>{esc(dd)}</span><span class="t">{n} events</span></a></li>'
        )

    body = f"""
<section class="hero">
  <h1>{SITE_NAME}</h1>
  <p class="lede">A daily bilingual briefing — what happened on this date in history.
  हिंदी में पहले, फिर अंग्रेज़ी में।</p>
</section>
<div class="dayhead">
  <div class="date">{esc(display)}</div>
  <div class="sub">Latest briefing / नवीनतम ब्रीफिंग</div>
</div>
<ol class="events">{"".join(render_event(e) for e in latest.get("events", []))}</ol>
{render_picks(latest.get("exam_picks"))}
<section class="archive">
  <h2>Archive / संग्रह</h2>
  <ul>{"".join(archive_items)}</ul>
</section>
"""
    return page_shell(SITE_NAME, body, depth=0)


def main():
    os.makedirs(DAYS_DIR, exist_ok=True)
    days = load_days()
    for d in days:
        with open(os.path.join(DAYS_DIR, f'{d["date"]}.html'), "w", encoding="utf-8") as f:
            f.write(render_day_page(d))
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_index(days))
    print(f"Built {len(days)} day page(s) + index.html")


if __name__ == "__main__":
    main()
