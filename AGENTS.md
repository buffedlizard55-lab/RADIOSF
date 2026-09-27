# Start here — every session

1. **Read the project charter first**: the top of [README.md](README.md) (identical copy in
   [docs/PROJECT_PROMPT.md](docs/PROJECT_PROMPT.md)). It is the definition of done.
2. Read [docs/LIMITATIONS.md](docs/LIMITATIONS.md) → "Suggested order of work for the next session".
3. Check open issues titled `[Automated source watch]` — they are the daily monitors telling you
   which sources moved. Act on those before anything else.
4. Look at the latest **source watch preview** run on your pull request: it runs all three live
   monitors (MLB API, Westwood One grids, club/school/station pages) on GitHub's runners.

## Rules that do not bend

- Every row needs a link a human can open. Nothing typed from memory — venues, times and station
  lines are transcribed from a page fetched in the same session.
- Anything uncertain becomes a flag (`review` confidence or a `flags` entry), never a silent edit.
- Monitors are read-only. They never edit `data/broadcasts.json` or publish Pages.
- Edit `scripts/build_feed.py`, then run it; never hand-edit `data/broadcasts.json` or
  `docs/LINE_BY_LINE.md` (CI rejects drift).
- When a page watch `expect` string is changed in `data/page_watch.json`, re-read the page and
  update the `checked` date.

## Local checks (same as CI)

```sh
python3 scripts/build_feed.py && git diff --exit-code -- data/broadcasts.json docs/LINE_BY_LINE.md
python3 scripts/source_watch_test.py
python3 scripts/wwo_watch_test.py
python3 scripts/page_watch_test.py
node scripts/ui_logic_test.js
node scripts/render_smoke_test.js
```
