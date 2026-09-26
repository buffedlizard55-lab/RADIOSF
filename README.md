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

It is the radio-only cousin of [ScheduleFreeTime](https://buffedlizard55-lab.github.io/ScheduleFreeTime/). That site asks when you are free. This one asks when a game is on the radio you can actually receive.

Snapshot: **2026-09-26**, through **2027-02-28**, America/Los_Angeles. 103 broadcasts. Not a live scrape. The opening chunk of the Westwood One NFL schedule was not returned, so some national games before November are absent on purpose. See [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

| Badge | Meaning |
| --- | --- |
| official | Club, league, or MLB API names the station and the time, or prints TBD. |
| indicated | Westwood One lists the game, and the station finder lists the Bay Area affiliates. Not a per-game clearance. Affiliates can be preempted. |
| review | Sources disagree, or a radio row was not individually quoted. Still shown so it can be checked. |

## Stations

| Frequency | Call | Live games in this snapshot |
| --- | --- | --- |
| 680 AM | KNBR | Giants. 49ers from Week 4 (Oct 4). Westwood One NFL, clearance indicated. |
| 104.5 FM | KNBR-FM | Same as 680 when a source lists both. Simulcast of 680. Not Stanford. |
| 810 AM | KSFO | 49ers Week 3. Cal football. Earthquakes English. |
| 960 AM | KNEW | Athletics. Talk the rest of the day, not listed as games. |
| 1050 AM | KTCT | Stanford football. Westwood One NFL affiliate. |
| 107.7 FM | KSAN | 49ers, every regular-season week listed here. |

Spanish calls (1370, 1510, 93.7, the 49ers app) are not on these stations and are omitted. HD subchannels are omitted.

## The 10 AM–10 PM observation

It is not a standing live-game block. KNBR’s own grid for the week of Aug 31–Sep 7 fills late morning with talk. 960’s weekday lineup is Fox Sports Radio talk. 1050 is mostly ESPN Radio talk. Those shows are not games, and no affiliate published a per-game national clearance list, so they are not on the calendar.

A Saturday with a college game, a Giants game, and a night game can cover a majority of that window. The day view computes the estimated union and says so. End times are estimates (MLB 2:45, NFL 3:15, college 3:24, MLS 2:00), labeled as estimates.

## Rebuild

```bash
python3 scripts/build_feed.py
node scripts/ui_logic_test.js
```

Do not add a row in the JSON by hand. Add it in `scripts/build_feed.py` only after the source page has been opened, then rebuild. The GitHub Action refuses a JSON file that does not match the script.

## Docs

- [docs/LINE_BY_LINE.md](docs/LINE_BY_LINE.md) — every broadcast and its links
- [docs/VERIFICATION.md](docs/VERIFICATION.md) — what was fetched on 2026-09-26
- [docs/LIMITATIONS.md](docs/LIMITATIONS.md) — what the next session should re-check
