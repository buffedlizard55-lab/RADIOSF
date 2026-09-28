# Start here — every session

1. **Read the project charter first**: the top of [README.md](README.md) (identical copy in
   [docs/PROJECT_PROMPT.md](docs/PROJECT_PROMPT.md)). It is the definition of done.
2. Read [docs/LIMITATIONS.md](docs/LIMITATIONS.md) → "Suggested order of work for the next session".
3. Check open issues titled `[Automated source watch]` — they are the daily monitors telling you
   which sources moved. Act on those before anything else.
4. Look at the latest **source watch preview** run on your pull request: it runs all six live
   monitors (MLB postseason API, NBA ESPN Radio PDF, Westwood One grids, club/school/station
   pages, ESPN Radio weekly grid, TBD kickoffs) on GitHub's runners.
5. Read `data/tbd_watch.json` next. It lists the rows whose kickoff is still unpublished, the page
   each one is watched on, and the anchor it is matched by. An entry that has flipped to
   **published** is a kickoff a human must transcribe; an entry that reports `unavailable` is a
   page that changed shape, not a kickoff that stayed hidden.

## Rules that do not bend

- Every row needs a link a human can open. Nothing typed from memory — venues, times and station
  lines are transcribed from a page fetched in the same session.
- Anything uncertain becomes a flag (`review` confidence or a `flags` entry), never a silent edit.
- Monitors are read-only. They never edit `data/broadcasts.json` or publish Pages.
- Edit `scripts/build_feed.py`, then run it; never hand-edit `data/broadcasts.json` or
  `docs/LINE_BY_LINE.md` (CI rejects drift).
- When a page watch `expect` string is changed in `data/page_watch.json`, re-read the page and
  update the `checked` date. The same rule covers a changed `anchor` or `rows` string in
  `data/tbd_watch.json`, and covers the school pages that show two seasons at once: gostanford.com
  opens with the completed 2025 results above the 2026 ticker, so an anchor matched on a date
  alone is not enough — match the opponent too.
- An MLB postseason date splits into per-game rows when, and only when, the Stats API has published a real
  first pitch for **every** game on it. That rule lives in `mlb_postseason_rows()` as the per-date
  `start_time_tbd` flag; flipping it and transcribing the instants is how a Division Series date gets clock
  times. A placeholder instant (07:33Z, 08:33Z, 10:33Z) is never a time, and `validate()` refuses a row
  whose displayed clock time does not re-derive from the instant its own source label cites.
- A page that builds its schedule in the browser cannot be watched at all. gostanford.com serves
  its 2026 ticker to a browser, not to a plain request, so no `expect` string from it can ever be
  found — an entry for it reported every string missing on its first live run and was removed.
  Check a new page against what a plain request actually returns before adding a watch entry, and
  prefer a machine-readable source for the same data (that is why Stanford is watched through
  ESPN's schedule feed).

## Local checks (same as CI)

```sh
python3 scripts/build_feed.py && git diff --exit-code -- data/broadcasts.json docs/LINE_BY_LINE.md
python3 scripts/source_watch_test.py
python3 scripts/espn_watch_test.py
python3 scripts/espn_radio_week_watch_test.py
python3 scripts/wwo_watch_test.py
python3 scripts/page_watch_test.py
python3 scripts/tbd_time_watch_test.py
node scripts/ui_logic_test.js
node scripts/render_smoke_test.js
```
