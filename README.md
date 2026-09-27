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

Snapshot date: **2026-09-27**. Window: **2026-09-27 through 2027-02-28**, America/Los_Angeles (155 calendar days). The snapshot contains **147 date-level schedule entries**: 136 rows include at least one non-conditional listing and 11 rows are entirely if-necessary, plus 30 flags. Two of the 136 rows are mixed postseason rows and also carry three if-necessary game possibilities. In total, 21 possible postseason games are represented across 13 dates. 146 entries have a date; one 49ers Week 18 row remains deliberately unplaced. The snapshot is not a live station log; see [docs/VERIFICATION.md](docs/VERIFICATION.md).

| Confidence | Meaning | Entries |
| --- | --- | ---: |
| official | A club, school, league API or rights holder printed both the event and station, or an explicit TBD. | 37 |
| indicated | A network or rights-holder lists the event, and a separate source establishes a Bay Area affiliate relationship. This is **not** per-game clearance; local programming may preempt it. | 108 |
| review | Sources disagree, or the station line is not stated for that exact event. Shown for review, not silently resolved. | 2 |

The 11 fully conditional rows are among the indicated entries; together they account for 18 possible games. Two other postseason date-rows mix three if-necessary games with non-conditional games. The row badges and source notes show that split. Conditional games are never treated as confirmed; any grouped postseason row containing a conditional game is conservatively excluded from duration and conflict calculations. A mixed row still counts as a non-conditional listing day because it also represents games not marked if-necessary. Past dates and elapsed estimated windows are labelled unchecked. Even a final game result does not prove that a local radio station carried it.

## Stations

| Frequency | Call | Snapshot scope | Entries / dates |
| --- | --- | --- | ---: |
| 680 AM | KNBR | Giants (season ends Sep 27); 49ers from Week 4; Westwood One NFL and college football; Cal only for the Big Game. | 91 / 64 |
| 104.5 FM | KNBR-FM | Full-time simulcast of 680. Same events whenever a source lists both. Never Stanford. | 91 / 64 |
| 810 AM | KSFO | 49ers Week 3 only; Cal football except the Big Game; Earthquakes English flagship. | 15 / 11 |
| 960 AM | KNEW | Athletics through the last day of the regular season. Fox Sports Radio talk is not a game listing. | 1 / 1 |
| 1050 AM | KTCT | Stanford football; Westwood One NFL, college football and U.S. Soccer; MLB postseason is indicated via ESPN Radio affiliation, not per-game clearance. | 116 / 74, including 11 if-necessary-only rows |
| 107.7 FM | KSAN | 49ers, every regular-season week listed here. | 15 / 14 |

“Entries / dates” counts rows assigned to each station; one row may count on more than one station. The 1050 count includes 11 fully conditional postseason rows plus two mixed rows that also contain if-necessary games. Spanish calls (1370, 1510, 93.7, Univision Radio, the 49ers app) are not on these six frequencies and are omitted. HD subchannels (KNBR-F2, KSAN HD3) are omitted. Warriors, Valkyries (95.7) and Sharks (98.5) are out of scope, not missing.

## The 10 AM–10 PM observation — measured, not assumed

For each of the 155 dates, the page takes the union of estimated windows for **non-conditional** rows inside 10 AM–10 PM, counting overlaps once. If-necessary placeholders are excluded. Rows without a listed start time contribute zero estimated minutes. The measure is an estimate from a schedule snapshot—not measured airtime, a live station log or proof of affiliate clearance.

| Measure | Result |
| --- | ---: |
| Dates in the snapshot | 155 |
| Dates with at least one non-conditional schedule listing | 74 |
| Dates with any if-necessary possibility | 13 |
| If-necessary postseason game possibilities | 21 |
| Conditional-only dates (no non-conditional listing) | 3 |
| Dates where estimated windows cover **more than half** of 10 AM–10 PM | **18** |
| Average estimated coverage, all dates | 1h 47m of 12h (15%) |
| Average estimated coverage, the 74 listing dates | 3h 45m of 12h |
| Busiest dates | Thanksgiving Nov 26, Christmas Dec 25 and Week 18 Saturday Jan 9 — 9h 15m each |

Average estimated coverage by weekday across **all** dates: **Sunday 3h 40m · Saturday 2h 56m · Thursday 2h 20m · Monday 2h 13m · Friday 41m · Wednesday 20m · Tuesday 16m.** Weekends are busier, but this snapshot does not show a 10-to-10 live-game pattern on most dates. Talk programming is not counted as a game.

### Sensitivity to estimated game lengths

No source publishes when each radio broadcast actually ends. The default lengths (MLB 2h 45m, MLB postseason 3h 30m, NFL 3h 15m, college football 3h 24m, soccer 2h) are assumptions; the page exposes editable controls. These scenarios change duration assumptions while continuing to exclude conditional listings and count overlaps once:

| Scenario | Dates with non-conditional listings | Dates over half the band | Mean across all dates | Mean on listing dates |
| --- | ---: | ---: | ---: | ---: |
| Uniform 90-minute estimate for timed listings | 74 | 0 | 52m | 1h 49m |
| Defaults minus 30 minutes | 74 | 5 | 1h 31m | 3h 10m |
| **Defaults** | **74** | **18** | **1h 47m** | **3h 45m** |
| Defaults plus 60 minutes | 74 | 18 | 2h 17m | 4h 47m |
| Uniform 240-minute windows | 74 | 18 | 2h 13m | 4h 39m |

Even assigning a generous four-hour estimate to every timed non-conditional listing yields a 2h 13m mean across the 12-hour band, and only 18 of 155 dates over half. This is a sensitivity check on the snapshot—not a prediction of airtime or station clearance.

## Monitoring, rebuild and tests

A scheduled, read-only GitHub Action checks **one** machine-readable source: MLB's 2026 postseason Stats API schedule. It compares future dates, game descriptions and TBD starts against the checked-in postseason rows. A detected difference or failed fetch opens or refreshes a review issue. The monitor **never** edits `data/broadcasts.json` or publishes a new GitHub Pages snapshot; it also does not check the other station, club, school or network pages, and it cannot establish per-game clearance. The static snapshot must still be reviewed and rebuilt before changes appear on the site.

```bash
python3 scripts/build_feed.py       # regenerates data/broadcasts.json + docs/LINE_BY_LINE.md
python3 scripts/source_watch_test.py # offline regression tests for the read-only monitor
node scripts/ui_logic_test.js       # date, conditional, band-math and feed invariants
node scripts/render_smoke_test.js   # real inline page script over all 155 dates
python3 scripts/source_watch.py     # optional live API check; exit 2=drift, 3=unavailable
```

Do not add a row to the JSON by hand. Add it in `scripts/build_feed.py` only after a fresh source check, then rebuild. The `verify` GitHub Action regenerates the curated feed and rejects drift, runs the offline source-watch, UI and page-render tests. The separate scheduled watcher is **not** an auto-publisher; it is a narrow early-warning check, not automatic maintenance of the full feed.

## Docs

- [docs/LINE_BY_LINE.md](docs/LINE_BY_LINE.md) — every schedule entry, conditional status and source link, generated
- [docs/VERIFICATION.md](docs/VERIFICATION.md) — which pages were fetched on 2026-09-27, what they settled, and what the source monitor can and cannot see
- [docs/LIMITATIONS.md](docs/LIMITATIONS.md) — what is still missing, limitations of automation and prioritized follow-up
- [docs/PROJECT_PROMPT.md](docs/PROJECT_PROMPT.md) — the charter, same text as the top of this file
