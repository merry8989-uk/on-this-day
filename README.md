# On This Day in History — आज का इतिहास

A daily, bilingual (Hindi + English) history briefing: what happened on this
date, across Indian and world history. Published as a static site on GitHub
Pages.

**Live site:** https://merry8989-uk.github.io/on-this-day/

## How it works

- Each day is one JSON file in `data/<YYYY-MM-DD>.json` with a list of events
  (`year`, `hi`, `en`, optional `source`).
- `scripts/build.py` reads every file in `data/` and generates:
  - `index.html` — homepage with the latest briefing and an archive list
  - `days/<YYYY-MM-DD>.html` — one page per day
- `scripts/fetch_wikipedia.py` is a **safety net**: if no briefing exists for
  today, it builds an English one from the Wikimedia "On this day" API so the
  site never goes a day without a post. It never overwrites an existing file.
- `.github/workflows/daily.yml` runs the safety net daily at 06:00 IST and
  commits any changes. The primary (bilingual) briefing is published by the
  scheduled agent job, which commits `data/<date>.json` and rebuilds.

## Adding a day manually

```bash
# 1. add data/YYYY-MM-DD.json
# 2. rebuild
python scripts/build.py
# 3. commit and push
```

## Sources

Facts are cross-checked against Wikipedia, Britannica, the Library of Congress,
HISTORY, the Wikimedia "On this day" API and other public references. Every
entry carries a short source note on the day page.
