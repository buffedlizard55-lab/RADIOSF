# Verification — 2026-09-27

No broadcast was added from memory. Every row in `data/broadcasts.json` was transcribed from a page opened on this date. The generator is `scripts/build_feed.py`; the review table it writes is `docs/LINE_BY_LINE.md`.

Window: **2026-09-27 through 2027-02-28**, America/Los_Angeles. Days before Sep 27 are labelled "before this snapshot", never "quiet".

Result: **147 broadcasts**, 146 placed on a day, 1 deliberately unplaced. 37 official, 108 indicated, 2 review. 30 flags.

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
- **https://www.mlb.com/giants/schedule/tv** — "English-language radio broadcasts: KNBR 680 AM & 104.5 FM."
- **https://www.mlb.com/athletics/schedule/affiliates** — the A's Radio Network table, 960 AM KNEW, Bay Area.
- **https://www.mlb.com/news/press-release-mlb-announces-2026-postseason-schedule** — "ESPN Radio will provide live national coverage of **all** 2026 MLB Postseason games." Wild Card from Sep 29; World Series Game 1 Fri Oct 23; a Game 7 would be Sat Oct 31.
- **https://statsapi.mlb.com/api/v1/schedule/postseason?season=2026&sportId=1** — 53 games over 28 dates. Every one carries `startTimeTBD: true` and a placeholder 07:33 UTC, so **no postseason row here has a clock time**. `ifNecessary` is recorded per date.
- **Search on national MLB radio rights** — ESPN Radio holds MLB national audio for 2026–2028; Westwood One does not. Univision Radio carries Spanish.

Because KTCT 1050 is a full-time ESPN Radio affiliate, the 28 postseason dates are listed on 1050 as **indicated**. That is a network row, not a per-game Bay Area clearance, and the `MLB_POSTSEASON_ESPN` flag says so in full.

### Pro football
- **https://www.49ers.com/schedule/** — read in three chunks. Per-game radio lines for Weeks 3–18. Week 3 is "KSFO 810 AM / KSAN 107.7 FM"; Week 4 onward is "KSAN 107.7 FM / KNBR 104.5 FM / 680 AM". Week 18 at Arizona still has no date.
- **https://www.westwoodonesports.com/nfl-schedule/** — read **end to end in four chunks** this time, which closes last pass's missing-chunk gap. 67 upcoming national games; 4 of them are 49ers games and are merged into the club rows rather than duplicated, leaving **63 standalone rows**.
- **https://www.westwoodonesports.com/station-finder/** — chunks 0–3 and 5. NFL tab, San Francisco: KNBR-AM, KNBR-F2, KNBR-FM, KTCT-AM. NCAA Football tab: the same four. Soccer tab: **KTCT-AM only**. Every table's footer is labelled "(2025)" — see flag `FINDER_2025_LABEL`. Disclaimer quoted verbatim in `WWO_PREEMPTION`.
- **Cumulus / GlobeNewswire release, Sep 9, 2026** — eight internationals for the full season, every postseason game, Super Bowl LXI on Feb 14, 2027 at SoFi. Seven internationals are still ahead of this snapshot; the eighth was played in September.
- **https://www.nfl.com/schedules/2026/POST/** — redirects to the regular-season page. The league has **not** published a postseason grid, so no playoff round is placed.

### College football
- **https://calbears.com/sports/football/schedule** — chunks 0, 4 and 5. The full Radio column was read this time, which retires last pass's `CAL_RADIO_INDEX` and `CAL_WAKE_ROW` flags. KSFO 810 on Oct 3, Oct 10, **Oct 17 (the row that was missing before)**, Oct 24, Oct 31, Nov 14, Nov 28; **KNBR 104.5 FM / 680 AM** on the Nov 21 Big Game. Only Oct 3 has a kickoff (12:30 PM at UNLV). Bye Nov 7.
- **https://gostanford.com/sports/football/schedule** — **serves 2025 rows**; `/schedule/2026` returns 404. Recorded as flag `GOSTANFORD_2025`. Stanford dates and kickoffs therefore come from ESPN.
- **https://www.espn.com/college-football/team/schedule/_/id/24/stanford-cardinal** — the 2026 Stanford schedule in Eastern time. Oct 3 12:00 ET; Oct 10 3:30 ET (NBC); Oct 17 7:30 ET; Fri Oct 23 10:30 ET; Oct 31, Nov 14, Nov 21 and Nov 28 TBD. Pacific is Eastern minus three hours all year, because both zones change clocks together.
- **https://www.westwoodonesports.com/ncaa-football/** plus the `eventGrid` More endpoint at offset 10, which answers "No more events" — **11** upcoming national games. Sep 26 Oklahoma at Georgia has dropped off the list and was removed.

### Soccer
- **https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season** — the club's full 34-match English/Spanish radio table, dated Feb 16, 2026, "All times and dates are subject to change." KSFO 810 English, KZSF 1370 Spanish. Seven matches remain.
- **https://images.mlssoccer.com/…/2026%20Schedule.pdf** — the club's printable schedule, used as a cross-check. It agrees with the release everywhere except **Oct 31, which it prints as TBD against the release's 2:00 PM** → flag `QUAKES_OCT31_TIME`, and that one row is marked review.
- **https://www.sjearthquakes.com/schedule** — renders client-side and returns no match data. Not usable; do not retry.
- **https://www.westwoodonesports.com/us-soccer/** plus `eventGrid` offset 5 ("No more events") — five upcoming national-team broadcasts with times and announcers, all inside the window. Bay Area affiliate is KTCT-AM from the Soccer tab of the station finder.

### Station programming
- **https://www.thesportsleader.com/shows/** (KNBR 680) and **https://www.thesportsleader.com/knbr1050shows/** (KNBR 1050) — **both still print the week of Monday 8-31 through Monday 9-7**, about four weeks stale. Used only as evidence of format, never as a clearance log. What they show: 680 is local talk 6 AM–6 PM with one game block most days; 1050 is the ESPN Radio network plus Jim Rome, with game blocks on Friday, Saturday and Sunday, including "STANFORD FOOTBALL", "CFB … (WW1 CFB Format A)" and "SAN JOSE EARTHQUAKES @ AUSTIN FC". The last of those is why `QUAKES_ALT_STATION` exists.

### Checked and deliberately not added
- **https://www.westwoodonesports.com/ncaa-basketball/** — "No upcoming events". There is no 2026-27 national college basketball grid to transcribe.
- **https://calbears.com/sports/mens-basketball/schedule** — 2026-27 games from Nov 2, TBD times, no radio column.
- **https://usfdons.com/sports/mens-basketball/schedule** — 2026-27 schedule with ESPN+ and CBS Sports Network logos and **no radio column**, even though KTCT's station record names the Dons as an affiliate.

## Transcription rule, and where it was broken

Every field in `scripts/build_feed.py` has to be readable off a page that was opened during the
session that wrote it. Not remembered, not reconstructed, not tidied.

The second pass caught a violation. Sixteen newly added Westwood One NFL rows, three Stanford
away rows and four Earthquakes away rows had venue strings that were written from recall. None of
them were obviously wrong — that is precisely the problem, because a recalled stadium name renders
identically to a verified one. The Westwood One NFL grid was re-read end to end and every venue is
now the exact printed string; the Stanford away rows are back to the bare city the earlier pass had
verified; the Earthquakes away rows carry no venue at all, because the club's radio release prints
none.

Nothing is normalised on the way in, which is why the feed contains the source's own
inconsistencies: Denver is "Empower Field at Mile High, Denver, CO" on Sep 27 and Dec 25 but "Mile
High Stadium, Denver, CO" on Oct 15; Detroit is "Ford Field, Detroit, MI, USA" on Nov 26 and "Ford
Field, Detroit, Michigan" on Dec 28; Mexico City is spelled "Estádio Azteca". Those are recorded in
flag `WWO_VENUE_STRINGS` rather than smoothed over, because smoothing is how a wrong value would get
laundered into a confident one. The four Saturday and Sunday "TBA" placeholders print no venue, so
their venue field is empty.

## Confidence vocabulary

- **official** — a club, school, league API or rights holder printed both the game and the station, or printed an explicit TBD.
- **indicated** — a network's own schedule lists the game and its station finder lists a Bay Area affiliate, with the preemption caveat. Not a per-game clearance.
- **review** — two sources disagree, or the radio line was not quoted for that exact row. Shown, never hidden.

## What the builder enforces

`python3 scripts/build_feed.py` rewrites the JSON from the transcribed lists and exits non-zero on: a duplicate id, a station outside the six, a row with no source, an https-less source, a date outside the window, a time without a date, a Week 3 49ers game on 680, a Week 4+ 49ers game without 680, a 49ers game missing 107.7, a Stanford game on anything but 1050, a Cal game on anything but 810, 810 on the Big Game, a postseason row that acquired a clock time, a Westwood One event id that belongs to a merged 49ers row, a row pointing at a flag that does not exist, an unexpected per-source row count, and any two **official** rows that collide on the same station at the same time.

`node scripts/ui_logic_test.js` checks the Pacific conversion, twelve-hour labels, Sunday-start calendar grids, overlap and TBD conflict detection, the band maths, and then re-validates the shipped JSON against the same invariants the page assumes — including that the file is already sorted.

`node scripts/render_smoke_test.js` extracts the real inline script from `index.html`, runs it against the real feed in a DOM shim, walks **all 155 days**, exercises the station filter, the sport filter, day and month navigation, the date picker and the search box, and fails if the page asks for an element id that is not in the markup.

## What was deliberately left out

Warriors and Valkyries (95.7). Sharks (98.5). Spanish-language calls. NBA, NHL, golf and NASCAR on ESPN Radio or Fox Sports Radio, because no affiliate-level game list was found. All basketball, for the same reason. NFL playoff rounds, because the league has published no dates. MLS Cup Playoff matches, because the club published no playoff radio plan. Anything before Sep 27, 2026.
