# RADIOSF

## Project charter — read this first

Read this before changing the feed. The same text is in [docs/PROJECT_PROMPT.md](docs/PROJECT_PROMPT.md); the start-of-session checklist is [AGENTS.md](AGENTS.md).

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
- **see what is on now and what is next** in the strip at the top of the page — estimated from the listed windows, never a live station check;
- **filter to a station** or sport, and search for a team, venue or date across the snapshot;
- **change each sport's estimated duration** and see the window coverage recomputed;
- **download the selected day as a calendar file** (`.ics`) that carries each row's source link and confidence;
- **open a source for every row** and inspect its confidence and irregularity notes.

Snapshot date: **2026-09-27**. Window: **2026-09-27 through 2027-02-28**, America/Los_Angeles (155 calendar days). The snapshot contains **173 date-level schedule entries**: 162 rows include at least one non-conditional listing and 11 rows are entirely if-necessary, plus 34 flags. Two of the 162 rows are mixed postseason rows and also carry three if-necessary game possibilities. In total, 21 possible postseason games are represented across 13 dates. 172 entries have a date; one 49ers Week 18 row remains deliberately unplaced. The snapshot is not a live station log; see [docs/VERIFICATION.md](docs/VERIFICATION.md).

| Confidence | Meaning | Entries |
| --- | --- | ---: |
| official | A club, school, league API or rights holder printed both the event and station, or an explicit TBD. | 37 |
| indicated | A network or rights-holder lists the event, and a separate source establishes a Bay Area affiliate relationship. This is **not** per-game clearance; local programming may preempt it. | 134 |
| review | Sources disagree, or the station line is not stated for that exact event. Shown for review, not silently resolved. | 2 |

The 11 fully conditional rows are among the indicated entries; together they account for 18 possible games. Two other postseason date-rows mix three if-necessary games with non-conditional games. The row badges and source notes show that split. Conditional games are never treated as confirmed; any grouped postseason row containing a conditional game is conservatively excluded from duration and conflict calculations. A mixed row still counts as a non-conditional listing day because it also represents games not marked if-necessary. Past dates and elapsed estimated windows are labelled unchecked. Even a final game result does not prove that a local radio station carried it.

## Stations

| Frequency | Call | Snapshot scope | Entries / dates |
| --- | --- | --- | ---: |
| 680 AM | KNBR | Giants (season ends Sep 27); 49ers from Week 4; Westwood One NFL, college football and the dated playoff windows; Cal only for the Big Game. | 97 / 70 |
| 104.5 FM | KNBR-FM | Full-time simulcast of 680. Same events whenever a source lists both. Never Stanford. | 97 / 70 |
| 810 AM | KSFO | 49ers Week 3 only; Cal football except the Big Game; Earthquakes English flagship. | 15 / 11 |
| 960 AM | KNEW | Athletics through the last day of the regular season. Fox Sports Radio talk is not a game listing. | 1 / 1 |
| 1050 AM | KTCT | Stanford football; Westwood One NFL, college football and U.S. Soccer; MLB postseason and the NBA's ESPN Radio schedule indicated via the affiliation, not a per-game clearance. | 142 / 96, including 11 if-necessary-only rows and the 20 NBA/Cup rows |
| 107.7 FM | KSAN | 49ers, every regular-season week listed here. | 15 / 14 |

“Entries / dates” counts rows assigned to each station; one row may count on more than one station. The 1050 count includes 11 fully conditional postseason rows, two mixed rows that also contain if-necessary games, and the 20 NBA rows from the league's own ESPN Radio schedule — 17 games with a printed time and three Cup dates with none. Spanish calls (1370, 1510, 93.7, Univision Radio, the 49ers app) are not on these six frequencies and are omitted. HD subchannels (KNBR-F2, KSAN HD3) are omitted. Warriors, Valkyries (95.7) and Sharks (98.5) are out of scope, not missing.

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

## MLB postseason: published matchups, start times still TBD

The MLB Stats API currently lists all 53 postseason game slots across 28 dates, with away/home labels and `ifNecessary` status. The site now shows those API-printed matchup labels on each date, including unresolved placeholders such as “AL 4/5 Winner”; it does not guess the teams behind a placeholder. The API still marks every first pitch TBD, so no MLB postseason clock time is displayed. Games marked if necessary remain possibilities, not confirmed games. This is the MLB schedule—not a per-game 1050 clearance: ESPN's national radio coverage plus KTCT's ESPN affiliate relationship only supports an **indicated** listing, and local preemption remains possible.

The original watch only compared dates, counts, descriptions and TBD status. It could miss a changed opponent or conditional marker while still reporting “clear.” The monitor now compares each game's description, away/home labels and if-necessary status too. Its saved real-response fixture includes those fields; changes open a review issue and never auto-publish.

## NBA on ESPN Radio: the first basketball rows, from the league's own schedule

The winter half of the window had no basketball at all, because Westwood One's college basketball grid is empty, Cal's and Stanford's 2026-27 schedules print no radio column and USF's prints no station. The NBA does publish one, and it was found this pass: the league's [2026-27 schedule release](https://www.nba.com/news/2026-27-nba-regular-season-schedule) links a dated, per-game [**2026-27 ESPN Radio broadcast schedule**](https://ak-static.cms.nba.com/wp-content/uploads/sites/46/2026/08/2026-27-ESPN-Radio-Schedule.pdf) — weekday, date, away, home and tip-off in ET, stamped “AS OF AUG. 13, 2026 | SUBJECT TO CHANGE”. Every `nba-espn-` row is transcribed from that one document, and the row title keeps the PDF's own strings.

| What the PDF prints | Rows here |
| --- | ---: |
| Dated games with a matchup and an ET time | 26 |
| Dated but with the matchup and time still TBD (Cup championship, Dec 11) | 1 |
| Undated TBD lines (the two Emirates NBA Cup semifinals) | 2 |
| **Inside this window** | **20** |
| Outside this window (Mar 6 – Apr 8, 2027) | 9 |

The 17 in-window games with a time become rows on **1050** with the printed ET time converted to Pacific (for example Philadelphia at New York, Tue 7:00 PM ET → 4:00 PM PT on Oct 20), and they are `indicated`, not `official`: ESPN Radio carries them nationally and KTCT is a full-time ESPN Radio affiliate, but no Cumulus or ESPN page publishes a Bay Area per-game clearance, so Stanford football, Earthquakes soccer or other local programming can take the station instead. The three Cup slots become one row per officially named date — Dec 8, Dec 9 and Dec 11 — asserting the date and the network and nothing else, with no matchup, no tip-off time, and no claim about which of the two semifinal days carries which game. All three contribute zero estimated minutes to the band maths.

Two checks keep a transcription from drifting silently:

- the PDF prints a weekday beside every date, and the builder refuses any row whose printed weekday does not match the real calendar for that date;
- `scripts/espn_watch.py` (22 offline tests) re-reads the PDF daily, requires it to parse into the same shape (27 dated rows, ten `*` and three `^` Cup markers, both Cup footnotes present) and re-derives the ET time from each row's stored Pacific start, so a title that no longer matches the document fails the check instead of passing it.

## The 10 AM–10 PM observation — measured, not assumed

For each of the 155 dates, the page takes the union of estimated windows for **non-conditional** rows inside 10 AM–10 PM, counting overlaps once. If-necessary placeholders are excluded. Rows without a listed start time contribute zero estimated minutes. The measure is an estimate from a schedule snapshot—not measured airtime, a live station log or proof of affiliate clearance.

| Measure | Result |
| --- | ---: |
| Dates in the snapshot | 155 |
| Dates with at least one non-conditional schedule listing | 97 |
| Dates with any if-necessary possibility | 13 |
| If-necessary postseason game possibilities | 21 |
| Conditional-only dates (no non-conditional listing) | 2 |
| Dates where estimated windows cover **more than half** of 10 AM–10 PM | **18** |
| Average estimated coverage, all dates | 2h 2m of 12h (17%) |
| Average estimated coverage, the 97 listing dates | 3h 15m of 12h |
| Busiest date | Christmas Day, Dec 25 — 9h 45m |

Average estimated coverage by weekday across **all** dates: **Sunday 3h 53m · Saturday 3h 24m · Friday 1h 3m · Thursday 2h 48m · Monday 2h 20m · Wednesday 20m · Tuesday 23m.** Weekends are busier, but this snapshot does not show a 10-to-10 live-game pattern on most dates. Talk programming is not counted as a game.

Adding the 20 NBA rows moved both averages in opposite directions, which is worth seeing plainly: the mean across **all** dates rose from 1h 47m to 2h 2m because 17 previously empty dates now carry a listed game, while the mean on **listing days** fell from 3h 28m to 3h 15m because those new days carry one 150-minute evening game each rather than a full afternoon. Oct 20 is the clearest example: it had only if-necessary postseason possibilities before, and now has the NBA's opening-night game plus that possibility.

### Sensitivity to estimated game lengths

No source publishes when each radio broadcast actually ends. The default lengths (MLB 2h 45m, MLB postseason 3h 30m, NFL 3h 15m, college football 3h 24m, soccer 2h) are assumptions; the page exposes editable controls. These scenarios change duration assumptions while continuing to exclude conditional listings and count overlaps once:

| Scenario | Dates with non-conditional listings | Dates over half the band | Mean across all dates | Mean on listing dates |
| --- | ---: | ---: | ---: | ---: |
| Uniform 90-minute estimate for timed listings | 97 | 0 | 1h 1m | 1h 38m |
| Defaults minus 30 minutes | 97 | 5 | 1h 43m | 2h 44m |
| **Defaults** | **97** | **18** | **2h 2m** | **3h 15m** |
| Defaults plus 60 minutes | 97 | 18 | 2h 37m | 4h 11m |
| Uniform 240-minute windows | 97 | 18 | 2h 35m | 4h 8m |

Even assigning a generous four-hour estimate to every timed non-conditional listing yields a 2h 35m mean across the 12-hour band, and only 18 of 155 dates over half. The count of dates over half the band has not moved from 18 through four successive additions of rows, which is the useful part: the finding is stable against how the snapshot is filled in, not an artifact of one pass. Rows with no published time — the six NFL playoff windows, the three NBA Cup slots and the 11 wholly if-necessary rows — contribute zero estimated minutes, the honest treatment rather than a flattering one. This is a sensitivity check on the snapshot—not a prediction of airtime or station clearance.

## Monitoring, rebuild and tests

A scheduled, read-only GitHub Action (`source watch`, daily) runs **six** monitors and opens or refreshes one review issue when anything moves:

| Monitor | Source | What it watches | Rows covered |
| --- | --- | --- | ---: |
| `source_watch.py` | MLB 2026 postseason Stats API | future dates, counts, descriptions, away/home matchup labels, if-necessary markers and TBD start times | 28 |
| `espn_watch.py` | NBA 2026-27 ESPN Radio schedule PDF | the parsed shape (27 dated rows, 10 `*` and 3 `^` Cup markers, both footnotes) plus every in-window date, matchup and printed ET time, re-derived from the snapshot rows | 20 |
| `wwo_watch.py` | Westwood One NFL grid | event ids and printed titles the network advertises | 63 |
| `wwo_watch.py` | Westwood One college football grid | same, including the SEC Championship and Army–Navy | 11 |
| `wwo_watch.py` | Westwood One college basketball grid | currently empty — any event appearing is reported as drift | 0 |
| `wwo_watch.py` | Westwood One U.S. Soccer grid | same | 5 |
| `page_watch.py` | 49ers.com, calbears.com, ESPN's Stanford feed, KNBR's Stanford page, the Earthquakes radio release | the exact radio/venue/opponent strings the rows were transcribed from | 37 |
| `page_watch.py` | NFL important-dates article and the nfl.com POST schedule URL | round-date text; alert when a postseason grid is published | 7 |
| `page_watch.py` | KNBR 1050 weekly grid, USF 2026-27 basketball schedule | alert when the frozen grid refreshes or a station name appears on the USF schedule | 0 (gap watch) |
| `espn_radio_week_watch.py` | espn.com/espnradio/schedule weekly grid | dates the undated week from ESPN's scoreboard, then reports any future in-window game the snapshot does not name | 0 (gap watch) |
| `tbd_time_watch.py` | Cal's football schedule in its text view, 49ers.com | the eight rows whose kickoff is still TBD, and nothing else: it reports the first clock time that appears where the snapshot has none | 8 |

That is **171 of the 173 rows** under a daily watch, plus one gap-watch on the weekly ESPN Radio grid — a source of games the snapshot does not yet list, not extra coverage of existing rows. The other two rows are the Giants and Athletics finales on the snapshot date itself. The TBD-kickoff watch adds no row to that count, because every row it watches is already watched by another monitor; what it adds is the thing none of the others can see. A page watcher can tell that a string moved, and the MLB monitor can tell that `startTimeTBD` flipped, but nothing could tell that Cal or the 49ers had *published a kickoff* for a game the snapshot lists without one. It reads the one row it was given — matched on the date cell **and** the opponent column, or on the anchor plus the row's own identity strings, with the search ending at the next game's printed date so a kickoff published for the following game is never read as this one's — and reports one of three things: still TBD, **published**, or unknown. A row it cannot locate is `unavailable`, never "still TBD", and an unreadable row is never reported as a change. Its eight watch entries cover eight rows across two pages, including the 49ers' Week 18 row, whose date and kickoff no other monitor can see at all. **Confirmed live on 2026-09-27** from GitHub's runners (the development sandbox cannot reach these hosts): MLB clear, all four Westwood One grids clear, all nine pages clear, NBA PDF clear, weekly grid `unavailable` because ESPN answers automation with HTTP 202, TBD-kickoff watch clear on both of its pages. The TBD-kickoff monitor is new this pass; its first live run is the source watch preview on this pull request, and it is that run which showed gostanford.com builds its ticker in the browser. A week it cannot date reports `unavailable`, never `clear`, and never produces a date. Every pull request also runs the `source watch preview` workflow, which runs all six monitors live and keeps one sticky PR comment with the reports, so a reviewer sees the current source state before merging.

**Monitor fixes:** the MLB monitor first read `startTimeTBD` from the top level of each game, but the API nests it inside `status`; that was fixed and covered by a real-response regression fixture. This pass found another blind spot: the monitor compared dates/counts/descriptions/time-TBD but not opponent labels or `ifNecessary`, so it could report clear while the matchups changed. The monitor now validates and compares all four game identity/status fields: description, away team, home team and conditional status. The feed and UI expose the verified API matchup labels while preserving unresolved seed placeholders and TBD starts. Regression tests cover matchup and conditional drift.

The page watcher does **not** parse schedules. Each `expect` string in `data/page_watch.json` was read on the live page; if one disappears, the page changed and the listed rows need a human re-read. Each `alert_if_present` string was absent; if it appears, new information may have been published. A page that cannot be fetched is **unavailable**, never "unchanged". ESPN's HTML schedule answers automated requests with HTTP 202, so the watcher reads ESPN's schedule feed for the same data. **gostanford.com's football schedule builds its 2026 ticker in the browser**, so a plain request receives a page without it: the first live run of an entry for it reported every expected string missing, and the entry was removed. The school page stays cited on every Stanford row for a human to open, and Stanford dates, opponents and kickoffs stay watched through ESPN's feed.

Two failure modes are kept strictly apart throughout: **changed** (a real difference) and **unavailable** (state unknown). A parser that silently matched nothing must never look like a source that had not changed.

The monitors **never** edit `data/broadcasts.json` or publish a new GitHub Pages snapshot, and they cannot establish per-game affiliate clearance. The snapshot is still reviewed and rebuilt by hand before a change appears on the site.

```bash
python3 scripts/build_feed.py        # regenerates data/broadcasts.json + docs/LINE_BY_LINE.md
python3 scripts/source_watch_test.py # offline tests for the MLB monitor (incl. real-response fixture)
python3 scripts/espn_watch_test.py   # offline tests for the NBA ESPN Radio monitor (incl. real-PDF text fixture)
python3 scripts/espn_radio_week_watch_test.py  # offline tests for the weekly ESPN Radio grid monitor
python3 scripts/wwo_watch_test.py    # offline tests for the Westwood One grid monitor
python3 scripts/page_watch_test.py   # offline tests for the page watcher
python3 scripts/tbd_time_watch_test.py # offline tests for the TBD-kickoff watcher (51 tests, incl. three saved pages)
node scripts/ui_logic_test.js        # date, conditional, band-math and feed invariants
node scripts/render_smoke_test.js    # real inline page script over all 155 dates
python3 scripts/source_watch.py      # live MLB check; exit 0=clear, 2=drift, 3=unavailable
python3 scripts/espn_watch.py        # live NBA PDF check; same exit codes (needs pypdf)
python3 scripts/espn_radio_week_watch.py  # live weekly-grid check; same exit codes
python3 scripts/wwo_watch.py         # live grid check; same exit codes
python3 scripts/page_watch.py        # live page check; same exit codes
python3 scripts/tbd_time_watch.py    # live TBD-kickoff check; same exit codes
```

All six watchers take `--input` so they can run against saved responses without a network. Do not add a row to the JSON by hand: add it in `scripts/build_feed.py` after a fresh source check, then rebuild. The `verify` Action regenerates the feed, rejects drift, and runs all offline suites plus the UI and page-render tests.

## Docs

- [docs/LINE_BY_LINE.md](docs/LINE_BY_LINE.md) — every schedule entry, conditional status and source link, generated
- [docs/VERIFICATION.md](docs/VERIFICATION.md) — which pages were fetched on 2026-09-27, what they settled, and what the source monitor can and cannot see
- [docs/LIMITATIONS.md](docs/LIMITATIONS.md) — what is still missing, limitations of automation and prioritized follow-up
- [docs/PROJECT_PROMPT.md](docs/PROJECT_PROMPT.md) — the charter, same text as the top of this file
- [AGENTS.md](AGENTS.md) — the start-of-session checklist: charter, open watch issues, the PR preview comment, the rules
- [data/page_watch.json](data/page_watch.json) — the pages and exact strings the page watcher checks
