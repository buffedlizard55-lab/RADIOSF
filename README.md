# RADIOSF

## Project charter — read this first

Read this before changing the feed. The same text is in [docs/PROJECT_PROMPT.md](docs/PROJECT_PROMPT.md).

Review the repo.

Put this prompt into the repo readme and read it every time we work on the project as a starting point to make sure we are building what we are aiming for and have a strong base to continue building and improving on making something useful for everyday use. It should solve the problem of having to manually check everything ourselves and having an up to date current feed.

Review the repo.

I want to create a copy of this website

https://buffedlizard55-lab.github.io/ScheduleFreeTime/

The only difference is that I want to know when is there a live sports over the radio in san Francisco bay area.

These are the only stations that I get reliably, 680 AM, 810 AM, 960 AM, 1050 AM. 104.5 FM and 107.7 FM.

I want to get verified official or unofficial but marked schedules for games that are scheduled to be broadcast over any given day from either social media, official verified sites, any other sources for radio broadcasts with live sports live over the radio in san Francisco given the above stations. I should be able to click any day on the calendar and view what games are scheduled to be broadcast. I can tell you that it seems there are live sports radio live over the air in san Francisco for a majority of the day between 10 AM and 10 PM.

Work line by line verifying from official verified trusted sources, provide links for manual review. There should be no manual input, work on your own to complete tasks. Flag any irregularities for review. No hallucinations.

Verify no hallucinations.

The goal of this project is to get a full list that follow our requirements. No hallucinations. Verify line by line.

Site creation

Create a github page for this repo that has clean ui, user friendly, simple and easy to use.

It should be organized and clean. It should include all relevant information in an easy to read format with official verified links as sources for review. Work line by line verify everything no hallucinations.

Go ahead and create a pull request and then merge the pull request onto the main. Make suggestions for what work still needs to be done and any limitations that is in the way of a successful project. It should be worked on in this next session or the next session. Work line by line verify everything no hallucinations.

Run this task through multiple passes.

Pass 1: Implement the task completely and verify the result.

Pass 2: Review your work for bugs, missing requirements, incorrect assumptions, and edge cases. Fix everything you find.

Pass 3: Re-check the entire implementation against the original request. Improve accuracy, reliability, completeness, and code quality. Fix any remaining issues.

Do not stop after the first pass. Each pass must build on the previous one. Before finishing, verify that the final result fully satisfies the original request. Work line by line verify everything no hallucinations.

## What this is

RADIOSF is a **static calendar snapshot of source-backed live-sports radio schedule listings** on the six Bay Area stations above. Click a day to see the listed event, station, Pacific time when known, confidence, caveats and source links. A schedule listing—especially one marked **indicated**—is not proof that a local affiliate actually carried a particular game or that it aired live.

It is the radio-only cousin of [ScheduleFreeTime](https://buffedlizard55-lab.github.io/ScheduleFreeTime/). That site asks when you are free. This one asks what live-sports listings are currently supported by sources for radios you can receive.

On the page you can:

- **click any day** in the calendar, or use the arrows, Today button, date picker, or left/right arrow keys;
- **filter to a station** or sport, and search for a team, venue or date across the snapshot;
- **change each sport's estimated duration** and see the window coverage recomputed;
- **open a source for every row** and inspect its confidence and irregularity notes.

Snapshot date: **2026-09-27**. Window: **2026-09-27 through 2027-02-28**, America/Los_Angeles (155 calendar days). The snapshot contains **153 date-level schedule entries**: 142 rows include at least one non-conditional listing and 11 rows are entirely if-necessary, plus 31 flags. Two of the 142 rows are mixed postseason rows and also carry three if-necessary game possibilities. In total, 21 possible postseason games are represented across 13 dates. 152 entries have a date; one 49ers Week 18 row remains deliberately unplaced. The snapshot is not a live station log; see [docs/VERIFICATION.md](docs/VERIFICATION.md).

| Confidence | Meaning | Entries |
| --- | --- | ---: |
| official | A club, school, league API or rights holder printed both the event and station, or an explicit TBD. | 37 |
| indicated | A network or rights-holder lists the event, and a separate source establishes a Bay Area affiliate relationship. This is **not** per-game clearance; local programming may preempt it. | 114 |
| review | Sources disagree, or the station line is not stated for that exact event. Shown for review, not silently resolved. | 2 |

The 11 fully conditional rows are among the indicated entries; together they account for 18 possible games. Two other postseason date-rows mix three if-necessary games with non-conditional games. The row badges and source notes show that split. Conditional games are never treated as confirmed; any grouped postseason row containing a conditional game is conservatively excluded from duration and conflict calculations. A mixed row still counts as a non-conditional listing day because it also represents games not marked if-necessary. Past dates and elapsed estimated windows are labelled unchecked. Even a final game result does not prove that a local radio station carried it.

## Stations

| Frequency | Call | Snapshot scope | Entries / dates |
| --- | --- | --- | ---: |
| 680 AM | KNBR | Giants (season ends Sep 27); 49ers from Week 4; Westwood One NFL, college football and the dated playoff windows; Cal only for the Big Game. | 97 / 70 |
| 104.5 FM | KNBR-FM | Full-time simulcast of 680. Same events whenever a source lists both. Never Stanford. | 97 / 70 |
| 810 AM | KSFO | 49ers Week 3 only; Cal football except the Big Game; Earthquakes English flagship. | 15 / 11 |
| 960 AM | KNEW | Athletics through the last day of the regular season. Fox Sports Radio talk is not a game listing. | 1 / 1 |
| 1050 AM | KTCT | Stanford football; Westwood One NFL, college football and U.S. Soccer; MLB postseason is indicated via ESPN Radio affiliation, not per-game clearance. | 122 / 80, including 11 if-necessary-only rows |
| 107.7 FM | KSAN | 49ers, every regular-season week listed here. | 15 / 14 |

“Entries / dates” counts rows assigned to each station; one row may count on more than one station. The 1050 count includes 11 fully conditional postseason rows plus two mixed rows that also contain if-necessary games. Spanish calls (1370, 1510, 93.7, Univision Radio, the 49ers app) are not on these six frequencies and are omitted. HD subchannels (KNBR-F2, KSAN HD3) are omitted. Warriors, Valkyries (95.7) and Sharks (98.5) are out of scope, not missing.

## NFL playoffs: dated rounds, undated games

The league's own 2026-2027 important-dates announcement names the rounds, and the Cumulus release of September 9, 2026 says Westwood One carries every postseason game. Both are official. What neither publishes is which game falls on which day, how many games a day carries, the matchups or the kickoffs — `nfl.com/schedules/2026/POST` still redirected to the regular season when fetched on 2026-09-27.

So each day of an officially named window carries one row, and that row claims nothing beyond the date and the network:

| Date(s) | Round | Row |
| --- | --- | --- |
| Jan 16, 17, 18, 2027 | Wild Card Weekend | one row per day of the window |
| Jan 23, 24, 2027 | Divisional Playoffs | one row per day of the window |
| Jan 31, 2027 | AFC and NFC Championship Games | one row; the league names a single day for both games |
| Feb 14, 2027 | Super Bowl LXI at SoFi Stadium | one row; date and stadium, kickoff not published |

Leaving January 17, 18, 23 and 24 blank would have read as "no live sports radio" on four of the busiest radio weekends of the year, which is the one wrong answer this page must not give. Filling them with a guessed number of games at guessed times would have been the other wrong answer. These rows carry **no** `start_pt`, **no** `game_count` and **no** venue, so they add six listing days while contributing zero estimated minutes to the band maths. `107.7 FM` is not claimed on any playoff row: if the 49ers reach the postseason their games would be expected on the club flagship, but no source publishes a postseason 49ers radio line. Flag `NFL_POSTSEASON_WINDOWS` carries the whole caveat on the page.

An earlier version of this feed called these dates "not official". They are the league's own announcement; that was wrong and it is corrected here.

## The 10 AM–10 PM observation — measured, not assumed

For each of the 155 dates, the page takes the union of estimated windows for **non-conditional** rows inside 10 AM–10 PM, counting overlaps once. If-necessary placeholders are excluded. Rows without a listed start time contribute zero estimated minutes. The measure is an estimate from a schedule snapshot—not measured airtime, a live station log or proof of affiliate clearance.

| Measure | Result |
| --- | ---: |
| Dates in the snapshot | 155 |
| Dates with at least one non-conditional schedule listing | 80 |
| Dates with any if-necessary possibility | 13 |
| If-necessary postseason game possibilities | 21 |
| Conditional-only dates (no non-conditional listing) | 3 |
| Dates where estimated windows cover **more than half** of 10 AM–10 PM | **18** |
| Average estimated coverage, all dates | 1h 47m of 12h (15%) |
| Average estimated coverage, the 80 listing dates | 3h 28m of 12h |
| Busiest dates | Thanksgiving Nov 26, Christmas Dec 25 and Week 18 Saturday Jan 9 — 9h 15m each |

Average estimated coverage by weekday across **all** dates: **Sunday 3h 40m · Saturday 2h 56m · Thursday 2h 20m · Monday 2h 13m · Friday 41m · Wednesday 20m · Tuesday 16m.** Weekends are busier, but this snapshot does not show a 10-to-10 live-game pattern on most dates. Talk programming is not counted as a game.

### Sensitivity to estimated game lengths

No source publishes when each radio broadcast actually ends. The default lengths (MLB 2h 45m, MLB postseason 3h 30m, NFL 3h 15m, college football 3h 24m, soccer 2h) are assumptions; the page exposes editable controls. These scenarios change duration assumptions while continuing to exclude conditional listings and count overlaps once:

| Scenario | Dates with non-conditional listings | Dates over half the band | Mean across all dates | Mean on listing dates |
| --- | ---: | ---: | ---: | ---: |
| Uniform 90-minute estimate for timed listings | 80 | 0 | 52m | 1h 41m |
| Defaults minus 30 minutes | 80 | 5 | 1h 31m | 2h 56m |
| **Defaults** | **80** | **18** | **1h 47m** | **3h 28m** |
| Defaults plus 60 minutes | 80 | 18 | 2h 17m | 4h 26m |
| Uniform 240-minute windows | 80 | 18 | 2h 13m | 4h 18m |

Even assigning a generous four-hour estimate to every timed non-conditional listing yields a 2h 13m mean across the 12-hour band, and only 18 of 155 dates over half. The mean on listing dates fell from 3h 45m to 3h 28m when six playoff-window dates were added, because those rows are officially dated but carry no kickoff time and so contribute zero estimated minutes — the honest treatment, not a flattering one. This is a sensitivity check on the snapshot—not a prediction of airtime or station clearance.

## Monitoring, rebuild and tests

A scheduled, read-only GitHub Action checks **five** machine-readable schedule sources every day:

| Source | What it watches | Rows covered |
| --- | --- | ---: |
| MLB 2026 postseason Stats API | future dates, game counts, descriptions and TBD start times | 28 |
| Westwood One NFL grid | the event ids and printed titles the network is advertising | 63 |
| Westwood One college football grid | same, including the SEC Championship and Army–Navy | 11 |
| Westwood One college basketball grid | currently empty — any event appearing is reported as drift | 0 |
| Westwood One U.S. Soccer grid | same | 5 |

That is **107 of the 153 rows** under automated watch, up from 28. A detected difference, or a check that cannot complete, opens or refreshes a single review issue. The college basketball grid is watched precisely because it is empty: it is the largest hole in the winter half of the window, and the monitor will report the moment Westwood One publishes it.

Two failure modes are kept strictly apart. A grid that should list events and returns none, or a page whose expected heading cannot be found, is reported as **unavailable** — the schedule state is unknown — and never as "no drift". A parser that silently matched nothing would otherwise look identical to a source that had not changed.

The monitors **never** edit `data/broadcasts.json` or publish a new GitHub Pages snapshot. They do not check the club, school or station pages, and they cannot establish per-game affiliate clearance. The static snapshot must still be reviewed and rebuilt by hand before a change appears on the site.

```bash
python3 scripts/build_feed.py        # regenerates data/broadcasts.json + docs/LINE_BY_LINE.md
python3 scripts/source_watch_test.py # offline tests for the MLB monitor
python3 scripts/wwo_watch_test.py    # offline tests for the Westwood One grid monitor
node scripts/ui_logic_test.js        # date, conditional, band-math and feed invariants
node scripts/render_smoke_test.js    # real inline page script over all 155 dates
python3 scripts/source_watch.py      # optional live MLB check; exit 2=drift, 3=unavailable
python3 scripts/wwo_watch.py         # optional live grid check; exit 2=drift, 3=unavailable
```

Both watchers take `--input <json>` so they can be run against saved responses without a network, and `--today` so the future/past split is testable. The Westwood One watcher reads its widget ids, row-id prefixes and merged 49ers event ids from `meta.wwo_watch` in the feed, so the watcher and the feed cannot disagree about which grid belongs to which rows.

Do not add a row to the JSON by hand. Add it in `scripts/build_feed.py` only after a fresh source check, then rebuild. The `verify` GitHub Action regenerates the curated feed and rejects drift, and runs both offline watcher suites plus the UI and page-render tests. The scheduled watcher is **not** an auto-publisher; it is an early-warning check over the machine-readable part of the feed, not automatic maintenance of all of it.

## Docs

- [docs/LINE_BY_LINE.md](docs/LINE_BY_LINE.md) — every schedule entry, conditional status and source link, generated
- [docs/VERIFICATION.md](docs/VERIFICATION.md) — which pages were fetched on 2026-09-27, what they settled, and what the source monitor can and cannot see
- [docs/LIMITATIONS.md](docs/LIMITATIONS.md) — what is still missing, limitations of automation and prioritized follow-up
- [docs/PROJECT_PROMPT.md](docs/PROJECT_PROMPT.md) — the charter, same text as the top of this file
