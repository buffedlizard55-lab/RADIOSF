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

Snapshot date: **2026-09-28**. Window: **2026-09-27 through 2027-02-28**, America/Los_Angeles (155 calendar days). The snapshot contains **182 date-level schedule entries**: 168 rows include at least one non-conditional listing and 14 rows are entirely if-necessary, plus 35 flags. Two of the 168 rows are mixed postseason rows and also carry three if-necessary game possibilities. In total, 21 possible postseason games are represented across 13 dates. 181 entries have a date; one 49ers Week 18 row remains deliberately unplaced. Everything except the MLB postseason rows was last line-checked on 2026-09-27; the MLB rows were re-read on 2026-09-28, when the Stats API published the first Wild Card first pitches. The snapshot is not a live station log; see [docs/VERIFICATION.md](docs/VERIFICATION.md).

| Confidence | Meaning | Entries |
| --- | --- | ---: |
| official | A club, school, league API or rights holder printed both the event and station, or an explicit TBD. | 37 |
| indicated | A network or rights-holder lists the event, and a separate source establishes a Bay Area affiliate relationship. This is **not** per-game clearance; local programming may preempt it. | 143 |
| review | Sources disagree, or the station line is not stated for that exact event. Shown for review, not silently resolved. | 2 |

The 14 fully conditional rows are among the indicated entries; together they account for 18 possible games. Two other postseason date-rows mix three if-necessary games with non-conditional games. The row badges and source notes show that split. Conditional games are never treated as confirmed; any grouped postseason row containing a conditional game is conservatively excluded from duration and conflict calculations. A mixed row still counts as a non-conditional listing day because it also represents games not marked if-necessary. Past dates and elapsed estimated windows are labelled unchecked. Even a final game result does not prove that a local radio station carried it.

## Stations

| Frequency | Call | Snapshot scope | Entries / dates |
| --- | --- | --- | ---: |
| 680 AM | KNBR | Giants (season ends Sep 27); 49ers from Week 4; Westwood One NFL, college football and the dated playoff windows; Cal only for the Big Game. | 97 / 70 |
| 104.5 FM | KNBR-FM | Full-time simulcast of 680. Same events whenever a source lists both. Never Stanford. | 97 / 70 |
| 810 AM | KSFO | 49ers Week 3 only; Cal football except the Big Game; Earthquakes English flagship. | 15 / 11 |
| 960 AM | KNEW | Athletics through the last day of the regular season. Fox Sports Radio talk is not a game listing. | 1 / 1 |
| 1050 AM | KTCT | Stanford football; Westwood One NFL, college football and U.S. Soccer; MLB postseason and the NBA's ESPN Radio schedule indicated via the affiliation, not a per-game clearance. | 151 / 96, including 14 if-necessary-only rows and the 20 NBA/Cup rows |
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

## MLB postseason: the Wild Card round now has clock times

Re-read 2026-09-28. The MLB Stats API lists all 53 postseason game slots across 28 dates and, as of this pass, has published a real first pitch for the twelve Wild Card games. Those three dates are now **one row per game with a Pacific clock time** instead of one grouped row with none. Every other postseason date still carries `startTimeTBD` true with the API's 07:33/08:33/10:33 UTC placeholder, so those dates stay grouped and show no time — a placeholder instant is never displayed as a clock time.

**What can be verified for San Francisco?** MLB confirms that ESPN Radio will carry every 2026 postseason game nationally. The local KNBR/KTCT 1050 AM schedule we could verify is stale (it covers Aug. 31–Sep. 6), and neither it nor the station-affiliation evidence establishes that KTCT will carry any specific postseason game. Accordingly these are **indicated possibilities, not confirmed local broadcasts**; check a current station announcement or schedule before tuning in. The national schedule and first-pitch times below are source-backed, but local carriage is not. Each first pitch is the MLB Stats API's UTC instant converted to Pacific and cross-checked against MLB.com's official Wild Card schedule in Eastern time:

| PT first pitch | Game (API's own labels) | API instant | MLB.com's printed time | Venue |
| --- | --- | --- | --- | --- |
| Tue Sep 29, 11:00 AM | NL Wild Card 'A' Game 1: Philadelphia Phillies at Atlanta Braves | 2026-09-29T18:00:00Z | 2 p.m. ET | Truist Park |
| Tue Sep 29, 2:00 PM | AL Wild Card 'A' Game 1: Chicago White Sox at Houston Astros | 2026-09-29T21:00:00Z | 5 p.m. ET | Daikin Park |
| Tue Sep 29, 5:00 PM | AL Wild Card 'B' Game 1: Boston Red Sox at New York Yankees | 2026-09-30T00:00:00Z | 8 p.m. ET | Yankee Stadium |
| Tue Sep 29, 7:00 PM | NL Wild Card 'B' Game 1: Chicago Cubs at San Diego Padres | 2026-09-30T02:00:00Z | 10 p.m. ET/7 p.m. PT | Petco Park |
| Wed Sep 30, 11:00 AM | NL Wild Card 'A' Game 2: Philadelphia Phillies at Atlanta Braves | 2026-09-30T18:00:00Z | 2 p.m. ET | Truist Park |
| Wed Sep 30, 2:00 PM | AL Wild Card 'A' Game 2: Chicago White Sox at Houston Astros | 2026-09-30T21:00:00Z | 5 p.m. ET | Daikin Park |
| Wed Sep 30, 5:00 PM | AL Wild Card 'B' Game 2: Boston Red Sox at New York Yankees | 2026-10-01T00:00:00Z | 8 p.m. ET | Yankee Stadium |
| Wed Sep 30, 7:00 PM | NL Wild Card 'B' Game 2: Chicago Cubs at San Diego Padres | 2026-10-01T02:00:00Z | 10 p.m. ET/7 p.m. PT | Petco Park |
| Thu Oct 1, 11:00 AM | NL Wild Card 'A' Game 3: Philadelphia Phillies at Atlanta Braves *(if necessary)* | 2026-10-01T18:00:00Z | “Thursday”, no time | Truist Park |
| Thu Oct 1, 2:00 PM | AL Wild Card 'A' Game 3: Chicago White Sox at Houston Astros *(if necessary)* | 2026-10-01T21:00:00Z | “Thursday”, no time | Daikin Park |
| Thu Oct 1, 5:00 PM | AL Wild Card 'B' Game 3: Boston Red Sox at New York Yankees *(if necessary)* | 2026-10-02T00:00:00Z | “Thursday”, no time | Yankee Stadium |
| Thu Oct 1, 7:00 PM | NL Wild Card 'B' Game 3: Chicago Cubs at San Diego Padres *(if necessary)* | 2026-10-02T02:00:00Z | “Thursday”, no time | Petco Park |

The four Thursday games are all `ifNecessary` in the API, so they stay conditional: they are excluded from the coverage maths and the conflict panel, and they export to `.ics` as `STATUS:TENTATIVE` rather than as bookings.

Three conversions are worth seeing stated, because they are the kind of thing that goes wrong silently. The API's `gameDate` is an absolute UTC instant, so the 8 p.m. ET game on September 29 is `2026-09-30T00:00:00Z` — the *next* day in UTC but still September 29 in Pacific. `build_feed.py` converts through the IANA zone, checks the resulting Pacific date against the API's `officialDate`, and refuses the row if they disagree. It then re-derives each row's clock time from the instant its own source label cites, so a typed time cannot survive a rebuild. The third check is that all 53 gamePks appear exactly once across the 37 rows and all 28 dates are covered.

### What is still unknown, and flagged rather than smoothed over

- **The Thursday times are not final.** The API returns `startTimeTBD false` with real instants for all four October 1 games; MLB.com's own article prints “Game 3 (if necessary): Thursday” with no time and says “Thursday's game times and TV networks are subject to change depending on which series remain ongoing.” Both are official, they disagree about how settled it is, and flag `MLB_WC_THURSDAY_PROVISIONAL` carries the whole caveat on the page.
- **Bracket placeholders move mid-pass.** The API printed the NL Wild Card 'A' away slot as `PHI/ARI` at 03:00 UTC on 2026-09-28 and as `Philadelphia Phillies` by 03:20 — the source watch preview on the pull request caught the twenty-minute window. The resolved label now ships, each of the three rows records that its away label *was* a placeholder, and the monitor reports every future resolution. The remaining Division Series slots (`NYY/BOS`, `HOU/CWS`, `SD/CHC`, `ATL/PHI`, `NL Lower Seed`) and venues (`NL Stadium`, `AL Stadium`, `TBD`) are still the API's own strings, shown as printed.
- **The API's own typo ships too.** Its description for gamePk 849827 is `NLDS 'A' Game 4 ` with a trailing space.
- **The Division Series bracket slots are placeholders** — `NYY/BOS`, `HOU/CWS`, `SD/CHC`, `ATL/PHI`, `NL Lower Seed` — and the venues for the later rounds are `NL Stadium`, `AL Stadium` and `TBD`. All are the API's strings, shown as printed.
- **This is the MLB schedule, not a 1050 clearance.** ESPN Radio carries every postseason game nationally and KTCT is a full-time ESPN Radio affiliate, which supports an **indicated** listing and no more. There is one national feed, so only one game can be on 1050 at a time, and local programming can take the station.

### The monitor now checks first pitches, not just dates

The original watch compared dates, counts, descriptions and TBD status. A second version added away/home labels and `ifNecessary`. Both could still report “clear” while a game's clock time moved, and neither could tell a renamed placeholder from a game that had vanished. The monitor now matches games on the API's permanent **`gamePk`** and compares each game's description, away and home labels, venue, if-necessary marker **and first pitch**; when a first pitch is newly published the report prints the Pacific time a human would transcribe. It aggregates a date carried by several per-game rows instead of assuming one row per date, and its fail-closed cases now include a snapshot row with a clock time but no cited instant. 28 offline tests, including one that replays the pre-split state and asserts the report names exactly the fields that moved.

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
| Dates where estimated windows cover **more than half** of 10 AM–10 PM | **20** |
| Average estimated coverage, all dates | 2h 10m of 12h (18%) |
| Average estimated coverage, the 97 listing dates | 3h 28m of 12h |
| Busiest date | **Tue Sep 29 — 11h (92% of the band)** |

Average estimated coverage by weekday across **all** dates: **Sunday 3h 53m · Saturday 3h 24m · Friday 1h 3m · Thursday 2h 48m · Monday 2h 20m · Wednesday 50m · Tuesday 48m.** Weekends are busier, but this snapshot does not show a 10-to-10 live-game pattern on most dates. Talk programming is not counted as a game.

**Publishing the twelve Wild Card first pitches displaced Christmas Day as the busiest date in the snapshot.** September 29 now carries four timed postseason games plus a Westwood One USMNT match, and September 30 four more; each day's estimated windows run from 11:00 AM to 10:30 PM, which is 11 of the 12 band hours. Those are the only two dates this snapshot can describe as near-continuously covered, and they are the first real evidence for the 10-to-10 hunch in the charter — on a postseason weekday, not on a weekend. Both means moved up (2h 2m → 2h 10m across all dates, 3h 15m → 3h 28m on listing dates) and the weekday means for Tuesday and Wednesday more than doubled, because those were the emptiest weekdays in the window.

The earlier passes each moved these numbers a little. This pass moved them for a different reason: not by adding rows, but by giving existing rows a clock time. A row with no published start contributes zero minutes no matter how many games it groups, so the same 97 listing dates were measured before and after — only the twelve Wild Card rows changed what they contribute.

### Sensitivity to estimated game lengths

No source publishes when each radio broadcast actually ends. The default lengths (MLB 2h 45m, MLB postseason 3h 30m, NFL 3h 15m, college football 3h 24m, soccer 2h) are assumptions; the page exposes editable controls. These scenarios change duration assumptions while continuing to exclude conditional listings and count overlaps once:

| Scenario | Dates with non-conditional listings | Dates over half the band | Mean across all dates | Mean on listing dates |
| --- | ---: | ---: | ---: | ---: |
| Uniform 90-minute estimate for timed listings | 97 | 1 | 1h 6m | 1h 45m |
| Defaults minus 30 minutes | 97 | 7 | 1h 51m | 2h 57m |
| **Defaults** | **97** | **20** | **2h 10m** | **3h 28m** |
| Defaults plus 60 minutes | 97 | 20 | 2h 44m | 4h 23m |
| Uniform 240-minute windows | 97 | 20 | 2h 42m | 4h 19m |

A correction to a claim the previous passes made: they reported that the count of dates over half the band “has not moved from 18 through four successive additions of rows,” and read that as evidence the finding was stable. It was stable against *adding rows*, and this pass shows why that was the wrong test — it moved to 20 as soon as twelve existing rows were given clock times. The honest statement is narrower: the 10-to-10 pattern is not visible across the window as a whole, and whether a given date approaches it depends on how many of its listings have a published start. Even a uniform four-hour estimate for every timed listing yields a 2h 42m mean across the 12-hour band.

Rows with no published time — the six NFL playoff windows, the three NBA Cup slots, the 25 grouped MLB postseason dates and the 14 wholly if-necessary rows — contribute zero estimated minutes, the honest treatment rather than a flattering one. This is a sensitivity check on the snapshot—not a prediction of airtime or station clearance.

## Monitoring, rebuild and tests

A scheduled, read-only GitHub Action (`source watch`, daily) runs **six** monitors and opens or refreshes one review issue when anything moves:

| Monitor | Source | What it watches | Rows covered |
| --- | --- | --- | ---: |
| `source_watch.py` | MLB 2026 postseason Stats API | every game matched on its permanent `gamePk`: description, away/home labels, venue, if-necessary marker **and first pitch**, aggregated across the per-game rows that now share a date | 37 |
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

That is **180 of the 182 rows** under a daily watch, plus one gap-watch on the weekly ESPN Radio grid — a source of games the snapshot does not yet list, not extra coverage of existing rows. The other two rows are the Giants and Athletics finales of 2026-09-27, now in the past. The TBD-kickoff watch adds no row to that count, because every row it watches is already watched by another monitor; what it adds is the thing none of the others can see. A page watcher can tell that a string moved, and the MLB monitor can tell that `startTimeTBD` flipped, but nothing could tell that Cal or the 49ers had *published a kickoff* for a game the snapshot lists without one. It reads the one row it was given — matched on the date cell **and** the opponent column, or on the anchor plus the row's own identity strings, with the search ending at the next game's printed date so a kickoff published for the following game is never read as this one's — and reports one of three things: still TBD, **published**, or unknown. A row it cannot locate is `unavailable`, never "still TBD", and an unreadable row is never reported as a change. Its eight watch entries cover eight rows across two pages, including the 49ers' Week 18 row, whose date and kickoff no other monitor can see at all. **Live status: 2026-09-28 05:42 UTC, on this pull request** (tenth pass): MLB postseason **clear**, all four Westwood One grids **clear**, all nine watched pages **clear**, NBA PDF **clear**, TBD-kickoff watch **clear**, and the weekly ESPN Radio grid **unavailable** — ESPN answers scripted clients with HTTP 202, which is a pre-existing limitation and never reported as unchanged. That is five of six monitors clear against this snapshot. The first run of the preview on this pull request, eight minutes earlier at 05:34 UTC, is the one that caught a Westwood One difference this session's own hand re-read had missed: the NFL grid no longer listed the Rams at Broncos broadcast of 2026-09-27, because its 16:30 PT start had passed hours before and an upcoming-only grid drops what has started. The snapshot row was right; the monitor's same-day rule was not, and the fix — skip a started same-day broadcast, name it in the report, still report anything whose start is unknown — is covered by eight new offline tests. The ninth pass's own run, 2026-09-28 03:25 UTC on PR #14, was also five of six clear; the run before it, 2026-09-27 18:29 UTC, is what opened issue #13 and started the ninth pass; the run between them caught two further drifts, both fixed. Re-checked by hand in this session through the fetch tool, because the development sandbox has no outbound network at all: the Stats API (53 games, 28 dates, twelve published first pitches), MLB.com's postseason release and its Wild Card Series matchups article, 49ers.com's schedule, the KNBR 1050 weekly grid (still the week of Aug 31 – Sep 6) and ESPN's weekly radio grid (still the week of Sep 21–27, so nothing new to add). **The source watch preview on this pull request then ran all six monitors live and found two things this session's hand re-read had missed**, both acted on before merging: the Stats API had resolved `PHI/ARI` to the Philadelphia Phillies twenty minutes after it was transcribed, and 49ers.com had dropped the broadcast line from the completed Week 3 game, which made one page-watch string permanently unfound. That is the preview workflow earning its place — see [docs/LIMITATIONS.md](docs/LIMITATIONS.md). A week it cannot date reports `unavailable`, never `clear`, and never produces a date. Every pull request also runs the `source watch preview` workflow, which runs all six monitors live and keeps one sticky PR comment with the reports, so a reviewer sees the current source state before merging.

**Monitor fixes:** the MLB monitor first read `startTimeTBD` from the top level of each game, but the API nests it inside `status`; that was fixed and covered by a real-response regression fixture. The sixth pass found a second blind spot — it compared dates, counts, descriptions and time-TBD but not opponent labels or `ifNecessary`. This pass found a third and fixed all three at once: matching games on a description string means a renamed placeholder reads as one game vanishing and another appearing, and a yes/no time-TBD comparison cannot see a *moved* clock time. The monitor now keys on the API's permanent `gamePk` and compares five fields plus the first pitch itself, reports a newly published instant as the Pacific time a human would transcribe, aggregates a date carried by several per-game rows, and fails closed on a snapshot row whose clock time has no cited instant behind it. Its saved real-response fixture is `scripts/fixtures/mlb_postseason_2026-09-28.json`.

The page watcher does **not** parse schedules. Each `expect` string in `data/page_watch.json` was read on the live page; if one disappears, the page changed and the listed rows need a human re-read. Each `alert_if_present` string was absent; if it appears, new information may have been published. A page that cannot be fetched is **unavailable**, never "unchanged". ESPN's HTML schedule answers automated requests with HTTP 202, so the watcher reads ESPN's schedule feed for the same data. **gostanford.com's football schedule builds its 2026 ticker in the browser**, so a plain request receives a page without it: the first live run of an entry for it reported every expected string missing, and the entry was removed. The school page stays cited on every Stanford row for a human to open, and Stanford dates, opponents and kickoffs stay watched through ESPN's feed.

Two failure modes are kept strictly apart throughout: **changed** (a real difference) and **unavailable** (state unknown). A parser that silently matched nothing must never look like a source that had not changed.

The monitors **never** edit `data/broadcasts.json` or publish a new GitHub Pages snapshot, and they cannot establish per-game affiliate clearance. The snapshot is still reviewed and rebuilt by hand before a change appears on the site.

```bash
python3 scripts/build_feed.py        # regenerates data/broadcasts.json + docs/LINE_BY_LINE.md
python3 scripts/source_watch_test.py # offline tests for the MLB monitor (28 tests, real-response fixture)
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
