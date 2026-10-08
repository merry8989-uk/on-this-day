#!/usr/bin/env python3
"""Safety-net generator: if no bilingual briefing exists for today, build an
English briefing for today's date from the Wikimedia "On this day" API.

This runs from the GitHub Actions workflow so the site still gets a post even
if the primary (bilingual) publisher did not run. It never overwrites an
existing data/<date>.json.

Run from the repository root:  python scripts/fetch_wikipedia.py [YYYY-MM-DD]
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")

API = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all/{mm}/{dd}"
UA = "on-this-day-briefing/1.0 (https://github.com/merry8989-uk/on-this-day)"


def today_ist():
    return datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d")


def fetch(mm, dd):
    req = urllib.request.Request(API.format(mm=mm, dd=dd), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def build_events(payload):
    items = []
    seen = set()

    def add(entry):
        year = str(entry.get("year", "")).strip()
        text = (entry.get("text") or "").strip()
        if not year or not text:
            return
        key = (year, text)
        if key in seen:
            return
        seen.add(key)
        items.append({"year": year, "en": text})

    # Curated "selected" entries first, then the broader "events" list.
    for e in payload.get("selected", []):
        add(e)
    for e in payload.get("events", []):
        add(e)

    # A few notable births/deaths round out the day.
    for e in payload.get("births", [])[:3]:
        add(e)
    for e in payload.get("deaths", [])[:3]:
        add(e)

    def year_key(ev):
        try:
            return int(ev["year"])
        except ValueError:
            return 9999

    items.sort(key=year_key)
    return items[:25]


def main():
    date = sys.argv[1] if len(sys.argv) > 1 else today_ist()
    out_path = os.path.join(DATA_DIR, date + ".json")
    if os.path.exists(out_path):
        print(f"{out_path} already exists — primary publisher ran, nothing to do.")
        return

    d = datetime.strptime(date, "%Y-%m-%d")
    payload = fetch(d.strftime("%m"), d.strftime("%d"))
    events = build_events(payload)
    if not events:
        print("No events returned by the API; not writing a file.")
        return

    os.makedirs(DATA_DIR, exist_ok=True)
    data = {
        "date": date,
        "events": [
            {"year": e["year"], "en": e["en"], "source": "Wikipedia (Wikimedia On this day)"}
            for e in events
        ],
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path} with {len(events)} events (English fallback).")


if __name__ == "__main__":
    main()
