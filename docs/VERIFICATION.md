# Verification — 2026-09-27

No broadcast was added from memory. Every row in `data/broadcasts.json` was transcribed from a page opened on this date. The generator is `scripts/build_feed.py`; the review table it writes is `docs/LINE_BY_LINE.md`.

Window: **2026-09-27 through 2027-02-28**, America/Los_Angeles. Days before Sep 27 are labelled "before this snapshot", never "quiet".

Result: **153 date-level schedule entries**: 142 rows with at least one non-conditional listing (2 are mixed) and 11 entirely if-necessary rows. 152 entries have a date; 1 is deliberately unplaced. 37 official, 114 indicated, 2 review. 31 flags. The two mixed postseason rows also contain three if-necessary games; the feed records **21 possible games across 13 dates**. Three dates have only if-necessary possibilities and no non-conditional listing.

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
- **https://www.mlb.com/giants/schedule/tv** — "English-language radio broadcasts: KNBR 680 AM & 104.5 FM."
- **https://www.mlb.com/athletics/schedule/affiliates** — the A's Radio Network table, 960 AM KNEW, Bay Area.
- **https://www.mlb.com/news/press-release-mlb-announces-2026-postseason-schedule** — "ESPN Radio will provide live national coverage of **all** 2026 MLB Postseason games." Wild Card from Sep 29; World Series Game 1 Fri Oct 23; a Game 7 would be Sat Oct 31.
- **https://statsapi.mlb.com/api/v1/schedule/postseason?season=2026&sportId=1** — 53 games over 28 dates. Every one carries `startTimeTBD: true` and a placeholder 07:33 UTC, so **no postseason row here has a clock time**. `ifNecessary` is recorded per date. The grouped feed represents 21 if-necessary games across 13 dates: 18 games in 11 rows that are entirely conditional, plus 3 games inside two mixed rows. The mixed rows remain non-conditional listings because they also contain non-conditional games; their conditional portions are separately badged and excluded from duration/conflict calculations.
- **Search on national MLB radio rights** — ESPN Radio holds MLB national audio for 2026–2028; Westwood One does not. Univision Radio carries Spanish.

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
- **https://gostanford.com/sports/football/schedule** — **serves 2025 rows**; `/schedule/2026` returns 404. Recorded as flag `GOSTANFORD_2025`. Stanford dates and kickoffs therefore come from ESPN.
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
- **https://usfdons.com/sports/mens-basketball/schedule** and **https://usfdons.com/sports/mens-basketball/schedule/text** — current 2026-27 schedule. The text-table columns are Date, Time, At, Opponent, Location, Tournament and Result; no Radio/Listen field. The live page shows TV logos for some games, not a station assignment. A prior-season official preview, **https://usfdons.com/news/2026/1/27/mens-basketball-san-francisco-heads-to-santa-clara-for-late-night-showdown**, explicitly says "Listen: KNBR 1050" for the Jan 28, 2026 game. That is evidence for 2025-26 only, not a 2026-27 renewal, so it is linked in `MBB_NO_RADIO_ROWS` but no 2026-27 row is inferred from it.

## Automated monitoring boundary

`.github/workflows/source-watch.yml` runs daily and can also be dispatched manually. It now runs **two** read-only monitors and opens or refreshes **one** combined review issue.

| Monitor | Source | Compares | Rows |
| --- | --- | --- | ---: |
| `scripts/source_watch.py` | MLB postseason Stats API | future dates, game counts, descriptions and start-time TBD status | 28 |
| `scripts/wwo_watch.py` | Westwood One NFL grid (widget 47029) | event ids and printed titles | 63 |
| `scripts/wwo_watch.py` | Westwood One college football grid (47030) | event ids and printed titles | 11 |
| `scripts/wwo_watch.py` | Westwood One college basketball grid (47031) | event ids — the snapshot expects none, so any event is drift | 0 |
| `scripts/wwo_watch.py` | Westwood One U.S. Soccer grid (47032) | event ids and printed titles | 5 |

That is **107 of the 153 rows** under automated watch. The widget ids, the row-id prefixes and the four merged 49ers event ids are read from `meta.wwo_watch` in the feed itself, so the watcher and the snapshot cannot disagree about which grid belongs to which rows.

Both monitors are read-only: neither edits the snapshot, publishes a new Pages build, verifies affiliate clearances, nor monitors the club, school or station pages. The 46 rows built from 49ers.com, mlb.com, calbears.com, ESPN, sjearthquakes.com and the KNBR grids still need a human re-read. A monitor that cannot complete reports **unavailable** and never “no drift”: for the Westwood One watcher that includes a grid which returns no events at all when the snapshot has rows built from it, and a page whose expected heading cannot be found, because a parser that silently matched nothing would otherwise be indistinguishable from a source that had not changed. Where one widget fails and another shows real drift, the combined status is **changed**, so a failure cannot bury a difference.

Direct live runs of both scripts in this development sandbox on 2026-09-27 could not complete: outbound TLS from the sandbox is closed (`EOF`) for `statsapi.mlb.com` and `westwoodonesports.com` alike. Each monitor correctly reported **unavailable** with a per-widget line, not “no drift”, and exited 3. Their comparison and failure behavior is covered by the offline suites. **The Westwood One HTML parser has therefore not yet been confirmed against a live fetch from this sandbox**; it is tested against fixtures built from the exact event ids, titles and venues printed on the grids when they were read through the fetch tool today, and its first scheduled run in CI is the live confirmation. If the markup differs enough that no heading can be located, the watcher reports unavailable and opens an issue rather than passing silently.

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

`python3 scripts/build_feed.py` rewrites the JSON from the transcribed lists and exits non-zero on: a duplicate id, a station outside the six, a row with no source, an https-less source, a date outside the window, a time without a date, a Week 3 49ers game on 680, a Week 4+ 49ers game without 680, a 49ers game missing 107.7, a Stanford game on anything but 1050, a Cal game on anything but 810, 810 on the Big Game, a postseason row that acquired a clock time, a Westwood One event id that belongs to a merged 49ers row, a row pointing at a flag that does not exist, an unexpected per-source row count, any two **official** rows that collide on the same station at the same time, and — new this pass — an NFL playoff window row that acquired a clock time, a venue, a per-day game count, a confidence above `indicated`, or a station outside the three Westwood One affiliates.

`validate_flags()` additionally rejects a duplicate flag id, a bad severity, a flag link that is not https, and a flag whose primary `url` is not the first entry of its `sources` list. Every row is also required to carry a known duration bucket whose minutes equal the bucket default, so that resetting the on-page duration controls always restores the shipped numbers.

`node scripts/ui_logic_test.js` checks the Pacific conversion, twelve-hour labels, ISO dates, past/elapsed status wording, conditional and mixed-row exclusion from estimated time and conflict calculations, Sunday-start calendar grids, the band maths, and the shipped JSON invariants — including conditional game counts and feed ordering.

`python3 scripts/source_watch_test.py` tests the read-only MLB monitor against synthetic API responses without network access. `python3 scripts/wwo_watch_test.py` does the same for the Westwood One grid monitor with 29 cases: it checks that the three anchors sharing one event href yield the printed title rather than the artwork or the “Full Details” chrome, that the generic “Upcoming Broadcasts” strip below a grid cannot inject another sport's events into it, that a missing heading or an empty grid where rows exist is a failure and not a clean result, that a past row dropping off the grid is not drift while a future or undated one is, that the four merged 49ers events are not reported as missing, that a populated college basketball grid is reported as drift, and that the exit codes are 0 clear / 2 changed / 3 unavailable. `node scripts/render_smoke_test.js` extracts the real inline script from `index.html`, runs it against the real feed in a DOM shim, walks **all 155 days**, exercises the filters, navigation, date picker, search and duration controls, and fails if the page asks for an element id that is not in the markup. Regression cases cover out-of-range and invalid dates, mixed/fully conditional postseason rows, and duration reset.

## What was deliberately left out

Warriors and Valkyries (95.7). Sharks (98.5). Spanish-language calls. NBA, NHL and NASCAR on ESPN Radio or Fox Sports Radio, because no affiliate-level game list was found. All basketball, for the same reason. Golf: Westwood One's radio golf rights are the Masters, the PGA Championship and the Ryder Cup, and the Ryder Cup is biennial in odd years, so the 2026 edition was September 26-28, **2025** and there is no golf broadcast inside this window. NFL playoff matchups, kickoffs and per-day game counts, because the league has published round dates only. MLS Cup Playoff matches, because the club published no playoff radio plan. Anything before Sep 27, 2026.
