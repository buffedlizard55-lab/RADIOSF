# Verification — 2026-09-27

No broadcast was added from memory. Every row in `data/broadcasts.json` was transcribed from a page opened on this date. The generator is `scripts/build_feed.py`; the review table it writes is `docs/LINE_BY_LINE.md`.

Window: **2026-09-27 through 2027-02-28**, America/Los_Angeles. Days before Sep 27 are labelled "before this snapshot", never "quiet".

Result: **173 date-level schedule entries**: 162 rows with at least one non-conditional listing (2 are mixed) and 11 entirely if-necessary rows. 172 entries have a date; 1 is deliberately unplaced. 37 official, 134 indicated, 2 review. 34 flags. The two mixed postseason rows also contain three if-necessary games; the feed records **21 possible games across 13 dates**. Two dates have only if-necessary possibilities and no non-conditional listing. No rows were added this pass; the weekly ESPN Radio grid was re-read and automated. The 20 `nba-espn-` rows remain `indicated`.

## Re-verified in the eighth pass, same snapshot date

Every source below was fetched again on 2026-09-27 through the session fetch tool and compared with the feed line by line. The sandbox has no outbound network, so nothing was checked from a cached copy or from the previous pass's notes.

| Source re-fetched | Result |
| --- | --- |
| `49ers.com/schedule/` | All 15 rows match: date, Pacific kickoff, radio line (Week 3 "KSFO 810 AM / KSAN 107.7 FM"; Week 4 onward "KSAN 107.7 FM / KNBR 104.5 FM / 680 AM"), venue, the Week 8 bye and the Week 18 TBD. Week 11 still prints **Estadio Banorte**, Week 18 still **State Farm Stadium**. No change. |
| `calbears.com/sports/football/schedule/text` | The whole 2026 table re-read. Oct 3 12:30 PM at UNLV; Oct 10, Oct 17, Oct 24, Oct 31, Nov 14, Nov 21 and Nov 28 all print an **empty** Time cell; opponents, home/away and venues match the feed exactly, including Gerald J. Ford Stadium in Dallas and Carter-Finley Stadium in Raleigh. No change. |
| `calbears.com/sports/football/schedule` | The rendered page shows the same dates and opponents. **Its Radio column is not reproduced in a rendered copy** — the column lives in the raw HTML, which is why `page_watch.py` reads the raw document and why the watcher's `expect` strings are quoted from it. The 2026-09-27 run from GitHub's runners found every one of them. |
| `espn.com/college-football/team/schedule/_/id/24/stanford-cardinal` | Oct 3 12:00 PM ET, Oct 10 3:30 PM ET (NBC), Oct 17 7:30 PM ET, Fri Oct 23 10:30 PM ET, and TBD for Oct 31, Nov 14, Nov 21 and Nov 28. Matches the feed. Sep 26 vs Georgia Tech is inside the day before the window and is correctly absent. |
| `gostanford.com/sports/football/schedule` | **A previous pass recorded this page as serving 2025 rows only. That was wrong and is corrected here.** The page opens with the completed 2025 results and then shows the 2026 schedule ticker, which prints the same eight dates as ESPN **and the Pacific kickoff for the four games that have one**: Oct 3 9:00 AM PDT, Oct 10 12:30 PM PDT, Oct 17 4:30 PM PDT and Fri Oct 23 7:30 PM PDT, with TBA for Oct 31, Nov 14, Nov 21 and Nov 28. The flag `GOSTANFORD_2025` is retired and replaced by `STANFORD_SCHEDULE_TWO_SEASONS`; every Stanford row now cites the school page beside ESPN, and the two agree. |
| `gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced` | "Kevin Richardson '88 and Jason Fisk '94 will comprise Stanford football's radio broadcast team on **KNBR/KTCT 1050 AM** when the 2026 campaign gets underway on Aug. 29 against Hawai'i." The station claim behind every Stanford row and the Big Game row. The same page carries the identical 2026 ticker. |
| `www.thesportsleader.com/stanfordfootball/` | "KNBR 1050 is your home for Stanford Cardinal football!" — the page-watch `expect` string is still present. |
| `www.thesportsleader.com/knbr1050shows/` | Still frozen on "MONDAY 8-31". Flag `KNBR_GRID_STALE` stands. The grid also shows, in the week of Aug 31 – Sep 7, a "STANFORD FOOTBALL vs MIAMI" block on 1050 on Friday 9-4, a "CFB: BOISE STATE @ OREGON (WW1 CFB Format A, WEG 2-A)" block and a "SAN JOSE EARTHQUAKES @ AUSTIN FC" block — station-side corroboration of the Stanford, Westwood One college football and `QUAKES_ALT_STATION` claims. |
| `sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season` | The full 34-match table unchanged: "810 / 1370" on every remaining row, Oct 10 Colorado 6:30 PM, Oct 14 Real Salt Lake 6:30 PM, Oct 17 Nashville 7:30 PM, Oct 24 FC Dallas 5:30 PM, Oct 28 Colorado 7:30 PM, Oct 31 Real Salt Lake 2:00 PM, Nov 7 Minnesota 4:00 PM, Decision Day. "Playoffs" is still absent, so the alert condition has not fired. |
| `mlb.com/giants/schedule/tv` | "English-language radio broadcasts: KNBR 680 AM & 104.5 FM." Spanish is KSFN 1510 / KXZM 93.7, which is out of scope and is why `SPANISH_EXCLUDED` exists. |
| `mlb.com/athletics/schedule/affiliates` (redirects to `/schedule/watch`) | The A's Radio Network table still lists "960 AM **KNEW** | Bay Area", with no home-only asterisk. |
| `statsapi.mlb.com/api/v1/schedule?teamId=137&date=2026-09-27` | Exactly one Giants game, gamePk 823164, first pitch 2026-09-27T19:05:00Z = 12:05 PM PDT, Dodgers at Giants at Oracle Park, game 3 of 3. Matches the row. |
| `statsapi.mlb.com/api/v1/schedule/postseason?season=2026` | Still 53 games over 28 dates. Sep 29 still prints four games with `startTimeTBD: true`, placeholder 07:33:00Z first pitches and placeholder team labels such as "HOU/TEX" and "NL Wild Card #3". No postseason clock time exists to transcribe. |
| `usfdons.com/sports/mens-basketball/schedule/text` | The 2026-27 table (Oct 13 exhibition at Arizona through Feb 27 vs Seattle U) prints no Radio or Listen column and no station anywhere. The basketball gap stands; `MBB_NO_RADIO_ROWS` is unchanged. |
| `seahawks.com/news/nfl-announces-important-dates-for-2026-2027` | "The NFL postseason begins with Wild Card weekend, January 16-18, and culminates with Super Bowl LXI in Los Angeles on February 14." Both page-watch `expect` strings present. |
| `nfl.com/schedules/2026/POST` | Still redirects to the regular-season schedule (Week 3). No postseason grid, so the six window rows stay as they are. |

**One new watch, built from what this pass found — and one source it had to give up.** Two of the sources above publish kickoffs only when they are ready, and no monitor could see the moment one appeared: Cal's text schedule (seven empty Time cells) and 49ers.com (Week 18 still TBD). `scripts/tbd_time_watch.py` now watches exactly those rows and nothing else — eight entries over two pages, including the Week 18 row that no other monitor can date. It reports the first printed clock time and never invents one; a row it cannot locate is `unavailable`, and an unreadable row is never reported as a change.

**What the first live run settled, and what it broke.** The source watch preview on this pull request ran all six monitors against the real sources. It reported the TBD watch **clear** on both pages (all eight rows still print no kickoff) and every page watch unchanged except one: the entry this pass had added for gostanford.com's schedule. All seven of its `expect` strings were missing. The cause is that the school builds its schedule ticker in the browser, so a plain HTTP request receives a page without it — the same behaviour as `sjearthquakes.com/schedule`, which is already recorded as unusable. The entry was removed, and the Stanford target was held out of `data/tbd_watch.json` (it is kept in `scripts/tbd_time_watch_test.py`, exercised against a saved rendering, ready to move across if the school ever renders the schedule server-side). Stanford dates, opponents and kickoffs stay watched through ESPN's machine-readable schedule feed. That run also exposed a bug in the new monitor: it casefolded the whole page to find an anchor, and one character whose casefold changes length ("İ") shifted every offset and made a whole target unreadable. It now matches with a case-insensitive regular expression on the original text, and a test pins that case down.

## Re-verified and added in this pass, same snapshot date

| Source fetched | Result |
| --- | --- |
| `statsapi.mlb.com/api/v1/schedule/postseason?season=2026&sportId=1` | Unchanged from the previous pass: 53 games over 28 dates, every first pitch still `startTimeTBD: true`, placeholders still printed verbatim, 21 games still marked if-necessary. No row changed. |
| `nba.com/news/2026-27-nba-regular-season-schedule` | **New source.** The league's own schedule release, which links the ESPN Radio schedule PDF and says ESPN Radio covers the NBA all season, naming 76ers at Knicks on opening night, the two Emirates NBA Cup semifinals, the Cup championship, and Spurs at Knicks and Heat at Celtics on Christmas Day. Read in chunk 0; the Christmas Day tip-off times (noon and 2:30 p.m. ET) and the Oct 20 opening-night tripleheader are printed on the same page. |
| `ak-static.cms.nba.com/.../2026-27-ESPN-Radio-Schedule.pdf` | **New source.** The NBA's dated ESPN Radio game list: 26 dated games with a matchup and an ET time, one dated championship line marked TBD, two undated semifinal TBD lines, stamped “AS OF AUG. 13, 2026 | SUBJECT TO CHANGE”. Read in full (one page). Every printed weekday was checked against the real calendar and every one matches. |
| `nba.com/news/emirates-nba-cup-key-dates-schedule` | Dates the Cup semifinals “December 8 and/or December 9” in team markets and the championship Friday, December 11 at Hinkle Fieldhouse, Indianapolis. Both facts are cited on the three Cup rows and in flag `NBA_CUP_TBD`. |
| `espn.com/espnradio/schedule` | Re-read 2026-09-27. Same four games: “MLB: Mets @ Rangers” Wednesday 7:30 p.m. ET, “MLB: Guardians @ Royals” Friday 7:00 p.m., “CFB: Wisconsin @ Penn State” Saturday 4:30 p.m., “CFB: Texas A&M @ LSU” Saturday 8:00 p.m. Still no date on the page. **Not used for any row** — `scripts/espn_radio_week_watch.py` now dates the week and would have reported these as past. Independent dated checks this session: MLB Stats API gamePk 822841 Mets at Rangers on 2026-09-23; gamePk 824058 Guardians at Royals on 2026-09-25; ESPN Texas A&M schedule “Sat, Sep 26 @ LSU”; ESPN Wisconsin schedule “Sat, Sep 26 @ Penn State”. |
| `westwoodonesports.com/more/eventGrid?id=47029` (offset 0) | The first ten NFL events match the snapshot on id, title, venue and Eastern time, including the Sep 29 USMNT vs. Chile soccer row that shares the widget. No drift. |
| `thesportsleader.com/shows/` and `/knbr1050shows/` | Both still frozen on the week of Monday 8-31 to Monday 9-7, four weeks stale. Flag `KNBR_GRID_STALE` stands. The 680 grid shows the station filling idle Giants days with national MLB (“JIP @ first pitch – MLB: TWINS @ WHITE SOX”) and the 1050 grid shows ESPN Radio college football, which is what flag `KNBR_MLB_FILLER` and the ESPN Radio affiliation describe — none of it is inside this window, so no row was made from it. |
| `gostanford.com/sports/mens-basketball/schedule` | Serves a schedule headed “2026-27” whose games are all completed 2026 results with TV labels only — no radio column. Nothing to transcribe. |
| `calbears.com/sports/mens-basketball/schedule` | 2026-27 opponents and dates print with “TBD” times and no radio column. Nothing to transcribe. |
| `49ers.com/schedule/` | Weeks 3 through 19 re-read. Week 3 still “KSFO 810 AM / KSAN 107.7 FM”, Week 4 onward still “KSAN 107.7 FM / KNBR 104.5 FM / 680 AM”, Week 8 still a bye, Week 18 still no date. All 15 rows match. |

## Re-verified in the fourth pass, same snapshot date

Every source below was fetched again on 2026-09-27 after the third pass shipped. Nothing in this
list was checked from memory or from the previous session's notes.

| Source re-fetched | Result |
| --- | --- |
| `49ers.com/schedule/` | All fifteen rows match on date, Pacific kickoff, radio line, venue, the Week 8 bye and the Week 18 TBD. Week 3 still prints "KSFO 810 AM / KSAN 107.7 FM"; Week 4 onward still prints "KSAN 107.7 FM / KNBR 104.5 FM / 680 AM". No change. |
| `westwoodonesports.com/nfl/` | The first ten events match on id, title, venue string and Eastern start time. Event 548538 is still merged into the club row. No change. |
| `westwoodonesports.com/ncaa-football/` + offsets 10 and 20 | Eleven events, grid exhausted at offset 20. Dates, ids, times and titles unchanged; **all eleven venue strings were short and are corrected**. |
| `westwoodonesports.com/us-soccer/` | All five events match on id, title, venue and Eastern start time, including both "TNT Sports Broadcast - Audio Only Simulcast" notes. No change. |
| `westwoodonesports.com/ncaa-basketball/` | Still "No upcoming events". Limitation stands, and is now watched automatically. |
| `nfl.com/schedules/2026/POST/` | Still redirects to the regular season, now showing Week 3. No postseason grid. |
| `seahawks.com` league important-dates announcement | **New source.** Supplies the official round dates behind the six new playoff window rows, and independently confirms Estadio Banorte for Nov 22. |
| `thesportsleader.com/shows/` and `/knbr1050shows/` | Both still frozen on the week of Monday 8-31 to Monday 9-7. Flag `KNBR_GRID_STALE` stands. |

## Stations, and only these

| You get | Call | What was verified on it this pass |
| --- | --- | --- |
| 680 AM | KNBR | Giants English flagship (`mlb.com/giants/schedule/tv`: "KNBR 680 AM & 104.5 FM"). 49ers from Week 4 on the club schedule. Westwood One NFL **and** NCAA Football affiliate on the station finder. Cal only on the Big Game row. |
| 104.5 FM | KNBR-FM | Printed alongside 680 on the Giants radio page and on 49ers.com from Week 4. Listed as KNBR-FM in the station finder. Never applied to Stanford, which the school specifies as 1050. |
| 810 AM | KSFO | 49ers Week 3 only, per the club schedule. Every 2026 Cal row's Radio column except the Big Game. Earthquakes English flagship in the club's February radio release. |
| 960 AM | KNEW | A's Radio Network table: "960 AM **KNEW** — Bay Area", with no home-only asterisk. |
| 1050 AM | KTCT | Stanford football. Westwood One NFL, NCAA Football and Soccer affiliate. Full-time ESPN Radio affiliate (its own published grid is the ESPN Radio schedule; its station record lists ESPN Radio as the network). |
| 107.7 FM | KSAN | 49ers.com prints KSAN on every regular-season week in this snapshot. |

HD subchannels (KNBR-F2, KSAN HD3) are not counted.

## Pages fetched this pass, and what each one settled

### Baseball
- **MLB Stats API, teams 137 and 133, 2026-09-27 → 2026-11-15** — exactly one Giants game (gamePk 823164) and one Athletics game (gamePk 824948) remain, both 12:05 PM PT on Sep 27. Nothing later exists to add.
- **MLB Stats API postseason endpoint, re-fetched 2026-09-27** — all 53 games on 28 dates were checked for description, away/home team labels, `ifNecessary` marker and `status.startTimeTBD`. The API prints matchups or unresolved placeholders (for example “AL 4/5 Winner”), explicitly marks 21 games “If Necessary Game”, and still marks every game's start time TBD. The site now exposes those source-printed matchups and conditional markers; no placeholder is resolved by inference. The [compact fields view](https://statsapi.mlb.com/api/v1/schedule/postseason?season=2026&sportId=1&fields=dates,date,games,officialDate,description,teams,away,team,name,home,status,startTimeTBD,ifNecessary,ifNecessaryDescription) was read in full; the saved fixture is `scripts/fixtures/mlb_postseason_2026-09-27.json`.
- **https://www.mlb.com/giants/schedule/tv** — "English-language radio broadcasts: KNBR 680 AM & 104.5 FM."
- **https://www.mlb.com/athletics/schedule/affiliates** — the A's Radio Network table, 960 AM KNEW, Bay Area.
- **https://www.mlb.com/news/press-release-mlb-announces-2026-postseason-schedule** — "ESPN Radio will provide live national coverage of **all** 2026 MLB Postseason games." Wild Card from Sep 29; World Series Game 1 Fri Oct 23; a Game 7 would be Sat Oct 31.
- **https://statsapi.mlb.com/api/v1/schedule/postseason?season=2026&sportId=1** — 53 games over 28 dates. Every one carries `startTimeTBD: true` and a placeholder 07:33 UTC, so **no postseason row here has a clock time**. `ifNecessary` is recorded per date. The grouped feed represents 21 if-necessary games across 13 dates: 18 games in 11 rows that are entirely conditional, plus 3 games inside two mixed rows. The mixed rows remain non-conditional listings because they also contain non-conditional games; their conditional portions are separately badged and excluded from duration/conflict calculations.
- **Search on national MLB radio rights** — ESPN Radio holds MLB national audio for 2026–2028; Westwood One does not. Univision Radio carries Spanish.

### Basketball
Until this pass the feed had no basketball at all. The three college sources were re-checked and still print no radio column or no station, so nothing was added from them. The NBA was checked because the league publishes its own radio schedule, and it does:

- **https://www.nba.com/news/2026-27-nba-regular-season-schedule** — “The NBA today released its complete game schedule for the 2026-27 regular season, along with the broadcast and streaming schedules for Disney (ABC/ESPN/**ESPN Radio**)…”. The same release links a PDF titled **2026-27 ESPN Radio Schedule**, says ESPN Radio “will provide national audio coverage of the NBA all season long”, and names the games it considers marquee: 76ers at Knicks on opening night, the two Emirates NBA Cup semifinals, the Cup championship, and Spurs at Knicks and Heat at Celtics on Christmas Day.
- **https://ak-static.cms.nba.com/wp-content/uploads/sites/46/2026/08/2026-27-ESPN-Radio-Schedule.pdf** — read in full. Columns as printed: DAY, DATE, AWAY, HOME, TIME (ET). 26 dated games with a matchup and a time, a dated Dec 11 championship line marked `TBD^`, two undated `TBD*` semifinal lines, and the footnotes that date the semifinals to Dec 8 and/or Dec 9 and the championship to Dec 11 at Hinkle Fieldhouse. Stamped **“AS OF AUG. 13, 2026 | SUBJECT TO CHANGE”**.
- **https://www.nba.com/news/emirates-nba-cup-key-dates-schedule** — the Cup dates restated independently: group play Oct 30 through Nov 27, quarterfinals Dec 4–5, semifinals Dec 8 and/or Dec 9, championship Dec 11 in Indianapolis.

**How the 20 rows were made.** The 17 in-window games with a printed time became one row each on 1050, with `start_pt` set to the printed ET time minus three hours. The three Cup slots became one row per officially named date (Dec 8, Dec 9, Dec 11) with **no** `start_pt`, no matchup and no game count, exactly the treatment the NFL playoff windows get. Nine further dated games in the PDF fall after Feb 28, 2027 and produced no rows; the feed's `meta.espn_watch` block records that so the monitor reports them as out-of-window rather than as missing.

**Three checks on that transcription.** The weekday printed beside every date was checked against the real calendar for all 27 dated rows and all 27 match. The ET→PT conversion is re-derived inside the build and again inside `node scripts/ui_logic_test.js`, which reads the printed ET time back out of each row's own note and fails if the stored Pacific time is not exactly three hours earlier. And `scripts/espn_watch.py` parses the PDF's row grammar directly, refusing to report `clear` unless it finds 27 dated rows, ten `*` markers, three `^` markers and both footnotes.

**What is still not known.** Whether KTCT 1050 aired any of these games. The rows are `indicated`, and flag `ESPN_RADIO_NBA` says why: the network carries them, the station is an ESPN Radio affiliate, and no source publishes a Bay Area per-game clearance. Flag `NBA_CUP_TBD` records that the semifinal days, matchups and tip-off times are unknown.

Because KTCT 1050 is a full-time ESPN Radio affiliate, the 28 postseason date-rows are listed on 1050 as **indicated**. That is an affiliate inference, not a per-game Bay Area clearance, and the `MLB_POSTSEASON_ESPN` flag says so in full.

### Pro football
- **https://www.49ers.com/schedule/** — read in three chunks. Per-game radio lines for Weeks 3–18. Week 3 is "KSFO 810 AM / KSAN 107.7 FM"; Week 4 onward is "KSAN 107.7 FM / KNBR 104.5 FM / 680 AM". Week 18 at Arizona still has no date.
- **https://www.westwoodonesports.com/nfl-schedule/** — read **end to end in four chunks** this time, which closes last pass's missing-chunk gap. 67 upcoming national games; 4 of them are 49ers games and are merged into the club rows rather than duplicated, leaving **63 standalone rows**.
- **https://www.westwoodonesports.com/station-finder/** — chunks 0–3 and 5. NFL tab, San Francisco: KNBR-AM, KNBR-F2, KNBR-FM, KTCT-AM. NCAA Football tab: the same four. Soccer tab: **KTCT-AM only**. Every table's footer is labelled "(2025)" — see flag `FINDER_2025_LABEL`. Disclaimer quoted verbatim in `WWO_PREEMPTION`.
- **Cumulus / GlobeNewswire release, Sep 9, 2026** — eight internationals for the full season, every postseason game, Super Bowl LXI on Feb 14, 2027 at SoFi. Seven internationals are still ahead of this snapshot; the eighth was played in September.
- **https://www.nfl.com/schedules/2026/POST/** — re-fetched this pass; still redirects to the regular-season page, which is on Week 3. The league has **not** published a postseason *grid*, so no playoff matchup, kickoff or per-day game count is placed.
- **https://www.seahawks.com/news/nfl-announces-important-dates-for-2026-2027** — the league's own 2026-2027 important-dates announcement, republished verbatim by an NFL club on Jul 07, 2026. Read in chunks 0–2. It prints **“January 9-10 - Week 18”, “January 16-18 - Wild Card Weekend powered by Verizon”, “January 23-24 - Divisional Playoffs presented by Intuit TurboTax”, “January 31 - AFC and NFC Championship Games presented by Intuit TurboTax” and “February 14 - Super Bowl LXI at SoFi Stadium (Inglewood, California)”**. These are the round dates behind the six new `nfl-post-` window rows. The same page independently confirms **“November 22 - NFL International Game at Estadio Banorte (Mexico City, Mexico): Minnesota Vikings vs. San Francisco 49ers”**, which is the venue 49ers.com prints and Westwood One does not — see flag `MEXICO_VENUE_NAMES`.

### College football
- **https://calbears.com/sports/football/schedule** — chunks 0, 4 and 5. The full Radio column was read this time, which retires last pass's `CAL_RADIO_INDEX` and `CAL_WAKE_ROW` flags. KSFO 810 on Oct 3, Oct 10, **Oct 17 (the row that was missing before)**, Oct 24, Oct 31, Nov 14, Nov 28; **KNBR 104.5 FM / 680 AM** on the Nov 21 Big Game. Only Oct 3 has a kickoff (12:30 PM at UNLV). Bye Nov 7.
- **https://gostanford.com/sports/football/schedule** — read in the seventh pass as **serving 2025 rows only**; `/schedule/2026` returns 404. Recorded then as flag `GOSTANFORD_2025`, and Stanford dates and kickoffs were taken from ESPN. **Corrected in the eighth pass:** the page opens with the 2025 results but does carry the 2026 ticker, with Pacific kickoffs for Oct 3, Oct 10, Oct 17 and Oct 23 and TBA for the rest. See the eighth-pass section above and flag `STANFORD_SCHEDULE_TWO_SEASONS`.
- **https://www.espn.com/college-football/team/schedule/_/id/24/stanford-cardinal** — the 2026 Stanford schedule in Eastern time. Oct 3 12:00 ET; Oct 10 3:30 ET (NBC); Oct 17 7:30 ET; Fri Oct 23 10:30 ET; Oct 31, Nov 14, Nov 21 and Nov 28 TBD. Pacific is Eastern minus three hours all year, because both zones change clocks together.
- **https://www.westwoodonesports.com/ncaa-football/** re-read end to end this pass, plus the `eventGrid` More endpoint at **offset 10, which carries the eleventh game, Army vs Navy**, and **offset 20, which is where the grid answers “No more events”** — **11** upcoming national games, and the list is exhausted. An earlier pass cited offset 10 as the “No more events” page, which understated the grid by one page; both labels are corrected in the row sources. Every venue is now the exact printed string, including the state suffix that eleven rows had lost and the full “MetLife Stadium, East Rutherford, NJ” — see flag `NCAAF_VENUE_REREAD`. All eleven dates, event ids, listed start times and titles were unchanged by the re-read.
- **https://www.westwoodonesports.com/nfl/** and **/us-soccer/** re-read this pass. The first ten NFL events and all five U.S. Soccer events match the snapshot on event id, printed title, venue string and listed Eastern start time, including “Energizer Park, St. Louis, MO” and the two “TNT Sports Broadcast - Audio Only Simulcast” notes. The NFL grid also still lists event **548538, Washington Commanders at San Francisco 49ers, “Levi's Stadium, Santa Clara, CA”, 7pm ET**, which stays merged into the official club row rather than duplicated.
- **https://www.westwoodonesports.com/ncaa-basketball/** re-fetched this pass — still **“No upcoming events”**, and the news strip below it is all April 2026. There is still no 2026-27 national college basketball grid to transcribe, which is why the automated watcher treats any event appearing there as drift.

### Soccer
- **https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season** — the club's full 34-match English/Spanish radio table, dated Feb 16, 2026, "All times and dates are subject to change." KSFO 810 English, KZSF 1370 Spanish. Seven matches remain.
- **https://images.mlssoccer.com/…/2026%20Schedule.pdf** — the club's printable schedule, used as a cross-check. It agrees with the release everywhere except **Oct 31, which it prints as TBD against the release's 2:00 PM** → flag `QUAKES_OCT31_TIME`, and that one row is marked review.
- **https://www.sjearthquakes.com/schedule** — renders client-side and returns no match data. Not usable; do not retry.
- **https://www.westwoodonesports.com/us-soccer/** plus `eventGrid` offset 5 ("No more events") — five upcoming national-team broadcasts with times and announcers, all inside the window. Bay Area affiliate is KTCT-AM from the Soccer tab of the station finder.

### Station programming
- **https://www.thesportsleader.com/shows/** (KNBR 680) and **https://www.thesportsleader.com/knbr1050shows/** (KNBR 1050) — both re-fetched this pass and **both still print the week of Monday 8-31 through Monday 9-7**, about four weeks stale. Used only as evidence of format, never as a clearance log. What they show: 680 is local talk 6 AM–6 PM with one game block most days; 1050 is the ESPN Radio network plus Jim Rome, with game blocks on Friday, Saturday and Sunday, including "STANFORD FOOTBALL", "CFB … (WW1 CFB Format A)" and "SAN JOSE EARTHQUAKES @ AUSTIN FC". The last of those is why `QUAKES_ALT_STATION` exists.

### Checked and deliberately not added
- **https://www.westwoodonesports.com/ncaa-basketball/** — "No upcoming events". There is no 2026-27 national college basketball grid to transcribe.
- **https://calbears.com/sports/mens-basketball/schedule** — 2026-27 games from Nov 2, TBD times, no radio column.
- **https://www.thesportsleader.com/stanfordbasketball/** — "Page Not Found" (2026-09-27). KNBR's site has a Stanford Football page and no basketball equivalent.
- **https://usfdons.com/sports/mens-basketball/schedule** and **https://usfdons.com/sports/mens-basketball/schedule/text** — current 2026-27 schedule. The text-table columns are Date, Time, At, Opponent, Location, Tournament and Result; no Radio/Listen field. The live page shows TV logos for some games, not a station assignment. A prior-season official preview, **https://usfdons.com/news/2026/1/27/mens-basketball-san-francisco-heads-to-santa-clara-for-late-night-showdown**, explicitly says "Listen: KNBR 1050" for the Jan 28, 2026 game. That is evidence for 2025-26 only, not a 2026-27 renewal, so it is linked in `MBB_NO_RADIO_ROWS` but no 2026-27 row is inferred from it.

## Automated monitoring boundary

`.github/workflows/source-watch.yml` runs daily and can also be dispatched manually. It runs **five** read-only monitors and opens or refreshes **one** combined review issue.

| Monitor | Source | Compares | Rows |
| --- | --- | --- | ---: |
| `scripts/source_watch.py` | MLB postseason Stats API | future dates, game counts, descriptions, away/home matchup labels, if-necessary markers and start-time TBD status | 28 |
| `scripts/espn_watch.py` | NBA 2026-27 ESPN Radio schedule PDF | parsed shape, in-window dates, matchups and printed ET times | 20 |
| `scripts/wwo_watch.py` | Westwood One NFL grid (widget 47029) | event ids and printed titles | 63 |
| `scripts/wwo_watch.py` | Westwood One college football grid (47030) | event ids and printed titles | 11 |
| `scripts/wwo_watch.py` | Westwood One college basketball grid (47031) | event ids — the snapshot expects none, so any event is drift | 0 |
| `scripts/wwo_watch.py` | Westwood One U.S. Soccer grid (47032) | event ids and printed titles | 5 |
| `scripts/page_watch.py` | 49ers.com schedule | radio lines, Week 11 and Week 18 venues | 15 |
| `scripts/page_watch.py` | calbears.com schedule; ESPN Stanford schedule feed; KNBR Stanford page | Radio column text; opponents; station statement | 15 |
| `scripts/page_watch.py` | Earthquakes 2026 radio release | radio column, Oct 31 and Nov 7 rows; alert on "Playoffs" | 7 |
| `scripts/page_watch.py` | NFL important dates (seahawks.com); nfl.com/schedules/2026/POST | round-date text; alert on "Wild Card Weekend" | 7 |
| `scripts/page_watch.py` | KNBR 1050 grid; USF 2026-27 men's basketball text schedule | frozen-week marker; alert on "KNBR" | gap watch |
| `scripts/espn_radio_week_watch.py` | espn.com/espnradio/schedule | dates the undated Monday–Sunday week from ESPN's scoreboard; reports future in-window games the snapshot does not name | gap watch |

That is **171 of the 173 rows** under a daily watch, plus the weekly-grid gap watch. The remaining two rows (Giants and Athletics finales) are dated 2026-09-27, the snapshot date. The Westwood One watcher reads its widget ids, row-id prefixes and merged 49ers event ids from `meta.wwo_watch` in the feed. The page watcher reads `data/page_watch.json`; every `expect` string there was read on the live page on 2026-09-27 and every `alert_if_present` string was absent.

All monitors are read-only: none edits the snapshot, publishes a Pages build, or verifies affiliate clearance. The page watcher reports that text moved; it does not parse a schedule. A monitor that cannot complete reports **unavailable** and never "no drift". Where one check fails and another shows real drift, the combined status is **changed**, so a failure cannot bury a difference.

### Live confirmation, 2026-09-27

The development sandbox still cannot open TLS connections to these hosts (`EOF`). The monitors were therefore confirmed live from GitHub's runners through the new `source watch preview` workflow on pull request #6. It runs on every PR and posts one sticky comment:

- MLB postseason API: **clear**, 28 dates and 53 games, all TBD, matching the snapshot. The same response was also read through the fetch tool, saved as `scripts/fixtures/mlb_postseason_2026-09-27.json` and compared offline: no differences.
- Westwood One: **clear** on all four grids — NFL 67 events listed (63 snapshot rows compared), college football 11, college basketball empty as expected, U.S. Soccer 5. This is the first live confirmation of the HTML parser.
- Pages: **clear** on all nine. ESPN's HTML schedule page returned HTTP 202 to automation on the first run; the watcher now reads ESPN's schedule feed (`site.api.espn.com/.../teams/24/schedule`), which carries the same games.

**Defect found by the live run:** the MLB monitor read `startTimeTBD` at the top level of each game, but the API nests it under `status`. Every scheduled run would have reported "unavailable" and opened a misleading issue. The synthetic test fixture had the same wrong shape. Both are fixed, and a regression test now runs against the real response.

**Another defect found during this review:** the MLB monitor compared dates, counts, API descriptions and TBD starts, but not participant labels or the if-necessary marker. The 2026-09-27 API now exposes away/home names, so a change to who is playing (or whether a game is conditional) could previously pass as clear. The feed, displayed rows, line-by-line review, saved fixture and monitor now include and compare exact API descriptions, away/home labels, `ifNecessary` and TBD status. Unresolved seed placeholders are copied exactly rather than guessed.

**Second defect:** the issue body de-duplication removed only the first "Checked:" timestamp line. With one line per report, the review issue would have been rewritten on every run even when nothing changed. The regular expression is now global.

### Hand re-verification, 2026-09-27 (fifth pass)

Re-read through the fetch tool and compared with the feed line by line. No discrepancies were found:

- **49ers.com/schedule/** — all 15 rows: date, Pacific kickoff, radio line (Week 3 "KSFO 810 AM / KSAN 107.7 FM"; Weeks 4–18 "KSAN 107.7 FM / KNBR 104.5 FM / 680 AM"), venue, Week 8 bye, Week 18 TBD.
- **calbears.com/sports/football/schedule/text** and the main schedule — Oct 3 12:30 PM at UNLV; every later game still has no time; "Radio: KSFO 810 AM" on the game rows.
- **ESPN Stanford schedule** — Oct 3 12:00 PM ET (9:00 PT), Oct 10 3:30 PM ET (12:30 PT), Oct 17 7:30 PM ET (4:30 PT), Oct 23 10:30 PM ET (7:30 PT); Oct 31, Nov 14, Nov 21 and Nov 28 TBD.
- **Earthquakes radio release** — Oct 10, 14, 17, 24, 28, 31 and Nov 7 times and "810 / 1370", unchanged.
- **nfl.com/schedules/2026/POST** — still redirects to the regular-season page, so there are still no per-game playoff rows.
- **KNBR 1050 grid** — still prints "MONDAY 8-31".

## Transcription rule, and where it was broken

Every field in `scripts/build_feed.py` has to be readable off a page that was opened during the
session that wrote it. Not remembered, not reconstructed, not tidied.

The second pass caught a violation. Sixteen newly added Westwood One NFL rows, three Stanford
away rows and four Earthquakes away rows had venue strings that were written from recall. None of
them were obviously wrong — that is precisely the problem, because a recalled stadium name renders
identically to a verified one. The fourth pass caught the milder cousin of the same fault: eleven college football venues
that had been transcribed correctly and then shortened, losing the state suffix the source
prints. A recalled venue looks confident and a truncated one looks tidy, and only a re-read
catches either. The Westwood One NFL grid was re-read end to end and every venue is
now the exact printed string; the Stanford away rows are back to the bare city the earlier pass had
verified; the Earthquakes away rows carry no venue at all, because the club's radio release prints
none.

The 49ers schedule was then re-read end to end as a third-pass spot check: all fifteen rows —
date, Pacific kickoff, radio line, venue, and the Week 8 bye and Week 18 TBD — match the feed
exactly. The single character that differs anywhere in that set is the registered-trademark sign
in the club's "Levi's® Stadium", dropped here to "Levi's Stadium". That is the only normalisation
applied to any venue string in the whole feed, and it is recorded here rather than left for a
reader to discover.

Nothing else is normalised on the way in, which is why the feed contains the source's own
inconsistencies: Denver is "Empower Field at Mile High, Denver, CO" on Sep 27 and Dec 25 but "Mile
High Stadium, Denver, CO" on Oct 15; Detroit is "Ford Field, Detroit, MI, USA" on Nov 26 and "Ford
Field, Detroit, Michigan" on Dec 28; Mexico City is spelled "Estádio Azteca". Those are recorded in
flag `WWO_VENUE_STRINGS` rather than smoothed over, because smoothing is how a wrong value would get
laundered into a confident one. The four Saturday and Sunday "TBA" placeholders print no venue, so
their venue field is empty.

## Confidence vocabulary

- **official** — a club, school, league API or rights holder printed both the game and the station, or printed an explicit TBD.
- **indicated** — a network or rights-holder lists the event, and a separate source establishes a Bay Area affiliate relationship, with the preemption caveat. Not a per-game clearance.
- **review** — two sources disagree, or the radio line was not quoted for that exact row. Shown, never hidden.

## What the builder enforces

`python3 scripts/build_feed.py` rewrites the JSON from the transcribed lists and exits non-zero on: a duplicate id, a station outside the six, a row with no source, an https-less source, a date outside the window, a time without a date, a Week 3 49ers game on 680, a Week 4+ 49ers game without 680, a 49ers game missing 107.7, a Stanford game on anything but 1050, a Cal game on anything but 810, 810 on the Big Game, a postseason row that acquired a clock time, a Westwood One event id that belongs to a merged 49ers row, a row pointing at a flag that does not exist, an unexpected per-source row count, any two **official** rows that collide on the same station at the same time, an NFL playoff window row that acquired a clock time, a venue, a per-day game count, a confidence above `indicated`, or a station outside the three Westwood One affiliates, and — new this pass — a printed weekday that disagrees with its own date, an NBA row that is not on 1050, not `indicated`, not on ESPN Radio, outside the window, or that lacks a time it should have or claims one it should not.

`validate_flags()` additionally rejects a duplicate flag id, a bad severity, a flag link that is not https, and a flag whose primary `url` is not the first entry of its `sources` list. Every row is also required to carry a known duration bucket whose minutes equal the bucket default, so that resetting the on-page duration controls always restores the shipped numbers.

`node scripts/ui_logic_test.js` checks the Pacific conversion, twelve-hour labels, ISO dates, past/elapsed status wording, conditional and mixed-row exclusion from estimated time and conflict calculations, Sunday-start calendar grids, the band maths, and the shipped JSON invariants — including conditional game counts and feed ordering.

`python3 scripts/source_watch_test.py` tests the read-only MLB monitor against synthetic API responses and the saved real response, without network access. `python3 scripts/espn_watch_test.py` covers the NBA PDF monitor in 22 cases against a fixture holding the document's printed content: that all 27 dated rows parse including a column-wise extraction, that a printed weekday which disagrees with its date is refused, that a changed time, a changed matchup, a removed game, an added game or a missing Cup marker is each reported, that a snapshot title that no longer matches the document fails the check, that text which parses to no rows raises rather than reading as clear, that a command-line run over unparseable text exits 3 and quotes what the extractor actually produced so the next reader can fix the grammar without another CI round trip, that ET→PT conversion is exact and refuses a time that would land on the previous Pacific date, and that an `unavailable` report never reads as `clear`. `python3 scripts/page_watch_test.py` covers the page watcher: tag-split strings, entity and typography folding, a vanished expected string, an appearing alert string, fetch failure and empty bodies reported as unavailable, change outranking unavailable, and config validation. `python3 scripts/espn_radio_week_watch_test.py` covers the weekly ESPN Radio grid monitor in 34 cases against a fixture that replays the 2026-09-27 page: that a week the dated scoreboard corroborates is `clear` when every future game is already in the snapshot, that an unvalidatable or ambiguous week is `unavailable` never `clear`, that a future unlisted game is `changed` with links to both the grid and the dated scoreboard, that a game without a clock or a day heading is refused rather than quietly dropped, that `p.m.` converts to 24-hour Eastern, and that an unparseable page exits 3. `python3 scripts/wwo_watch_test.py` does the same for the Westwood One grid monitor with 29 cases: it checks that the three anchors sharing one event href yield the printed title rather than the artwork or the “Full Details” chrome, that the generic “Upcoming Broadcasts” strip below a grid cannot inject another sport's events into it, that a missing heading or an empty grid where rows exist is a failure and not a clean result, that a past row dropping off the grid is not drift while a future or undated one is, that the four merged 49ers events are not reported as missing, that a populated college basketball grid is reported as drift, and that the exit codes are 0 clear / 2 changed / 3 unavailable. `node scripts/render_smoke_test.js` extracts the real inline script from `index.html`, runs it against the real feed in a DOM shim, walks **all 155 days**, exercises the filters, navigation, date picker, search and duration controls, and fails if the page asks for an element id that is not in the markup. Regression cases cover out-of-range and invalid dates, mixed/fully conditional postseason rows, and duration reset.

## What was deliberately left out

Warriors and Valkyries (95.7). Sharks (98.5). Spanish-language calls. NHL, NASCAR and college basketball on ESPN Radio or Fox Sports Radio, because no dated affiliate-level game list was found for them — the NBA is now in, from the league's own dated PDF. The weekly ESPN Radio grid is watched daily but still produces no snapshot rows: on 2026-09-27 every game it printed was already in the past. Golf: Westwood One's radio golf rights are the Masters, the PGA Championship and the Ryder Cup, and the Ryder Cup is biennial in odd years, so the 2026 edition was September 26-28, **2025** and there is no golf broadcast inside this window. NFL playoff matchups, kickoffs and per-day game counts, because the league has published round dates only. MLS Cup Playoff matches, because the club published no playoff radio plan. Anything before Sep 27, 2026.
