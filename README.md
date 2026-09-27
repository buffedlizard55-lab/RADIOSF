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

A calendar of **live game broadcasts** on the six Bay Area stations above. Click a day. The program log shows the game, the station, the Pacific time, and a link to the page the row came from.

It is the radio-only cousin of [ScheduleFreeTime](https://buffedlizard55-lab.github.io/ScheduleFreeTime/). That site asks when you are free. This one asks when a game is on a radio you can actually receive.

Snapshot: **2026-09-27**, through **2027-02-28**, America/Los_Angeles. **147 broadcasts** across 155 days, **30 flagged irregularities**. Not a live scrape. Everything was transcribed from a page opened on the snapshot date; see [docs/VERIFICATION.md](docs/VERIFICATION.md).

| Badge | Meaning | Rows |
| --- | --- | --- |
| official | A club, school, league API or rights holder printed both the game and the station (or printed an explicit TBD). | 37 |
| indicated | A network lists the game and its station finder lists a Bay Area affiliate. A network row, **not** a per-game clearance — affiliates get preempted. | 108 |
| review | Two sources disagree, or the radio line was not quoted for that exact row. Shown anyway so it can be checked. | 2 |

## Stations

| Frequency | Call | Live games in this snapshot | Rows / days |
| --- | --- | --- | --- |
| 680 AM | KNBR | Giants (season ends Sep 27). 49ers from Week 4. Westwood One NFL and college football. Cal only for the Big Game. | 91 / 64 |
| 104.5 FM | KNBR-FM | Full-time simulcast of 680. Same games whenever a source lists both. Never Stanford. | 91 / 64 |
| 810 AM | KSFO | 49ers Week 3 only. Every Cal football game except the Big Game. Earthquakes English flagship. | 15 / 11 |
| 960 AM | KNEW | Athletics, through the last day of the regular season. Fox Sports Radio talk after that, which is not a game. | 1 / 1 |
| 1050 AM | KTCT | Stanford football. Westwood One NFL, college football and U.S. Soccer. Full-time ESPN Radio affiliate, which is how the MLB postseason reaches the Bay Area. | 116 / 74 |
| 107.7 FM | KSAN | 49ers, every regular-season week listed here. | 15 / 14 |

Spanish calls (1370, 1510, 93.7, Univision Radio, the 49ers app) are not on these six frequencies and are omitted. HD subchannels (KNBR-F2, KSAN HD3) are omitted. Warriors, Valkyries (95.7) and Sharks (98.5) are out of scope, not missing.

## The 10 AM–10 PM observation — measured, not assumed

You said live sport looked like it filled most of 10 AM to 10 PM. The site now computes it instead of repeating it. For every day in the window it takes the union of estimated game windows inside the band, counting overlaps once:

| Measure | Result |
| --- | --- |
| Days in the snapshot | 155 |
| Days with at least one verified game | 77 |
| Days where games cover **more than half** of 10 AM–10 PM | **18** |
| Average band coverage, all days | 1h 47m of 12h (15%) |
| Average band coverage, days that do have a game | 3h 36m of 12h |
| Busiest days | Thanksgiving Nov 26, Christmas Dec 25 and Week 18 Saturday Jan 9 — 9h 15m each |

Average coverage by weekday: **Sunday 3h 40m · Saturday 2h 56m · Thursday 2h 20m · Monday 2h 13m · Friday 41m · Wednesday 20m · Tuesday 16m.**

So the hunch holds on an autumn Sunday, Saturday or Thursday and is clearly wrong on a Tuesday or Wednesday. The rest of the weekday band is talk — Murph & Markus, Fair & Biased and Dirty Work on 680, the ESPN Radio network on 1050, Fox Sports Radio on 960 — and talk is not listed here as a game. End times are estimates (MLB 2:45, MLB postseason 3:30, NFL 3:15, college football 3:24, soccer 2:00) and are labelled as estimates everywhere they appear.

## Rebuild and test

```bash
python3 scripts/build_feed.py      # regenerates data/broadcasts.json + docs/LINE_BY_LINE.md
node scripts/ui_logic_test.js      # calendar maths + invariants on the shipped feed
node scripts/render_smoke_test.js  # runs index.html's own script over all 155 days
```

Do not add a row to the JSON by hand. Add it in `scripts/build_feed.py`, and only after the source page has actually been opened, then rebuild. The GitHub Action rebuilds the feed, refuses any JSON that does not match the script, and runs both tests.

## Docs

- [docs/LINE_BY_LINE.md](docs/LINE_BY_LINE.md) — every broadcast, every source link, generated
- [docs/VERIFICATION.md](docs/VERIFICATION.md) — exactly which pages were fetched on 2026-09-27 and what each one settled
- [docs/LIMITATIONS.md](docs/LIMITATIONS.md) — what is still missing and what the next session should do
- [docs/PROJECT_PROMPT.md](docs/PROJECT_PROMPT.md) — the charter, same text as the top of this file
