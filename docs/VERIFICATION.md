# Verification — 2026-09-26

No broadcast was added from memory. Each row in `data/broadcasts.json` was transcribed from a page fetched the same day. The generator is `scripts/build_feed.py`. The review table is `docs/LINE_BY_LINE.md`.

Window: **2026-09-26 through 2027-02-28**, America/Los_Angeles. Days before Sep 26 are labeled “before this snapshot,” not “quiet.”

## Stations, and only these

| You get | Call | What was verified on it |
| --- | --- | --- |
| 680 AM | KNBR | Giants English flagship. 49ers from Week 4. Westwood One NFL affiliate. |
| 104.5 FM | KNBR-FM | Listed with 680 on the Giants listen page and on 49ers.com from Week 4. Station finder lists KNBR-FM. Full-time simulcast of 680 is the standing format (KNBR-FM Wikipedia, page dated 2026-08-06). Not applied to Stanford, which is specified as 1050. |
| 810 AM | KSFO | 49ers Week 3 (schedule page and the Sep 23 ways-to-listen article). Cal football radio column. Earthquakes English column. |
| 960 AM | KNEW | Athletics affiliate page: “960 AM KNEW, Bay Area,” no home-only asterisk. |
| 1050 AM | KTCT | Stanford football, “KNBR/KTCT 1050 AM,” July 30, 2026 school release. Westwood One NFL affiliate. |
| 107.7 FM | KSAN | 49ers.com prints KSAN on every regular-season week in this snapshot. |

HD subchannels (KNBR-F2, KSAN HD3) are not counted.

## Pages fetched this session

- MLB Stats API, Giants team 137 and Athletics team 133, September 2026 through Oct 5. Giants end Sep 27 (gamePk 823164). Athletics end Sep 27 (gamePk 824948). No later games were returned, so none were invented.
- https://www.mlb.com/giants/schedule/tv — “KNBR 680 AM & 104.5 FM.”
- https://www.mlb.com/athletics/schedule/affiliates — 960 AM KNEW, Bay Area.
- https://www.49ers.com/schedule/ — per-game radio lines, Weeks 3–18. Week 18 date TBD.
- https://www.49ers.com/news/ways-to-watch-and-listen-cardinals-vs-49ers-week-3-x8427 — 1:05 PM PT, KSFO / KSAN. Published Sep 23, 2026.
- https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced — 1050 AM.
- https://gostanford.com/news/2026/1/26/complete-2026-schedule-unveiled — dates.
- ESPN Stanford and Cal schedule pages — kickoff cross-check. ESPN times are Eastern. 7:30 PM ET is 4:30 PM PT. Eastern is always 3 hours ahead of Pacific, including after the Nov 1 clock change, because both zones move together.
- https://calbears.com/sports/football/schedule — scoreboard fetch plus the rendered index of the radio column. See flag `CAL_RADIO_INDEX`.
- https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season — full English/Spanish table. Feb 16, 2026. Times “subject to change.”
- https://www.westwoodonesports.com/nfl-schedule/ — four chunks. 63 standalone national games plus 4 that are the same 49ers games, kept as club rows.
- https://www.westwoodonesports.com/events/548494 and https://www.westwoodonesports.com/events/548515 — listed-start and placeholder-end check.
- https://www.westwoodonesports.com/ncaa-football/ and the eventGrid More endpoint. Offset 20 returned “No more events.” 12 games.
- https://www.westwoodonesports.com/station-finder/ — NFL table, San Francisco: KNBR-AM, KNBR-FM, KTCT-AM, KNBR-F2. NCAA tab not separately extracted.
- Cumulus / GlobeNewswire release, Sep 9, 2026 — eight internationals, every postseason game, Super Bowl LXI on Feb 14, 2027 at SoFi. Schedule page lists seven internationals and no dated playoff rounds.
- https://www.thesportsleader.com/shows/ — grid still showed Aug 31–Sep 7. Used as format evidence, not as this week’s log.
- https://calbears.com/sports/mens-basketball/schedule — 2026-27 scoreboard, no radio rows. Not added.

## Confidence

- **official** — station and time (or an explicit TBD) come from the club, league, or MLB API, and the radio page names the station.
- **indicated** — the national game is on Westwood One’s own schedule, and the station finder names the Bay Area affiliates, with the preemption caveat. Not a per-game clearance.
- **review** — a source disagrees, or a row was not individually quoted. Still shown, so it can be checked. Not hidden.

## Counts from the builder

103 broadcasts after 16 Westwood One NFL lines were removed because they were not on a returned page chunk. 102 placed. 1 unplaced (49ers Week 18). Counts of official, indicated, and review are in `data/broadcasts.json` under `meta.counts` and are regenerated with the feed.

`python3 scripts/build_feed.py` rewrites the JSON from the transcribed list and refuses duplicate ids, stations outside the six, a Week 3 49ers game on 680, or a Stanford game on anything but 1050 (the Big Game is a separate row). `node scripts/ui_logic_test.js` checks the Pacific conversion, the Sunday-start calendar, and overlap detection.

## What was deliberately left out

Warriors and Valkyries (95.7). Sharks (not on these six). Spanish Giants, Earthquakes, and 49ers. ESPN Radio and Fox Sports Radio play-by-play without an affiliate game list. College basketball. NFL playoff rounds without dates. The eighth international game, because it was not on the schedule page. Any game before Sep 26, 2026.
