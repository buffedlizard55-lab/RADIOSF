# Limitations, and the work that is still open

Snapshot 2026-09-27. 153 schedule entries: 142 rows with at least one non-conditional listing (2 are mixed) and 11 wholly if-necessary rows; 31 flags. The flags themselves live in `data/broadcasts.json` under `flags` and are rendered on the site under **Known gaps**, **Irregularities flagged for review** and **Notes**. This file is the human summary plus the to-do list.

## Closed since the previous pass

| Was | Now |
| --- | --- |
| `WWO_CHUNK_MISSING` — the opening chunk of the Westwood One NFL schedule was never returned, so 16 national games were knowingly absent | The page was read end to end in four chunks. All 16 are in. 47 → **63** standalone rows. |
| `WWO_SPLIT_LINE` — Oct 26 Cowboys at Eagles straddled two fetches | Confirmed on a clean read. Row is now plain `indicated`. |
| `CAL_RADIO_INDEX` / `CAL_WAKE_ROW` — the Cal radio column had been read from a rendered index, and the Oct 17 row was missing entirely | The Radio column was read directly from the official schedule. Oct 17 vs Wake Forest is added, and all seven non-Big-Game rows are `official` on KSFO 810. |
| `NCAAF_FINDER_TAB` — college football clearance borrowed the NFL affiliate row | The NCAA Football tab was extracted. Same four San Francisco affiliates. |
| `STANFORD_OCT17_TIME` — the Elon kickoff came from ESPN, not the school | Superseded by `GOSTANFORD_2025`: the school site serves 2025, so **every** Stanford time is from ESPN and that is now stated once, on every row. |
| Nothing for the MLB postseason | 28 dates added on 1050 as `indicated`, sourced to MLB's own release naming ESPN Radio plus KTCT's ESPN Radio affiliation. |
| Nothing for U.S. national teams | 5 Westwood One matches added on 1050, from the Soccer tab of the station finder. |

## Found and fixed during the second pass

The second pass re-read the shipped code and the shipped data looking for defects rather than
for missing games. Five things were wrong.

| Defect | Why it mattered | Fix |
| --- | --- | --- |
| **Venue strings written from memory.** The 16 newly added Westwood One NFL rows, three Stanford away rows and four Earthquakes away rows carried stadium names that had not been transcribed from any page opened this session — they were recalled, then typed. | This is the one rule the project does not get to break. A recalled stadium name is indistinguishable, on the page, from a verified one. | The Westwood One NFL grid was re-read in full and every venue is now the exact printed string, including its inconsistencies. Stanford away rows are back to the city the earlier pass verified. Earthquakes away rows carry no venue, because the club's radio release does not print one. New flag `WWO_VENUE_STRINGS` records the source page's own contradictions. |
| **The calendar could strand the user.** A URL hash outside the snapshot — a stale bookmark, a hand-typed date — put `state.year`/`state.month` out of bounds, and the month arrows then refused to move in either direction. | A blank grid with two dead arrows and no way back. | `setDate` now clamps the *grid* into the window while the day panel still answers honestly for the out-of-window date. Covered by two new cases in `scripts/render_smoke_test.js`. |
| **The conflict panel flooded.** TBD warnings were emitted once per *pair*, so Oct 31 — three undated listings on 1050 — produced three near-identical warnings, and a four-listing day produced six. | The real overlap warnings were buried in duplicates, which is how a reader learns to ignore a warning panel. | TBD warnings collapse to one per station and name every listing involved. Overlap warnings stay pairwise and now name both games. Window-wide warning count fell from 47 to 34; the worst day, Oct 10, fell from 7 warnings to 3. |
| **Wrong DST changeover date.** The timezone label used 2027-03-08; US daylight time in 2027 begins March 14. | Harmless today, because the window ends 2027-02-28. It would have mislabelled the clock the first time anyone extended the window. | Corrected. |
| **A dead form label.** `index.html` carried a `visually-hidden` label pointing at an input that no longer existed. | Nothing visible, but it is the kind of leftover that makes a later reader distrust the markup. | Removed. |

## Found and fixed during the third pass

The third pass re-read the original request clause by clause and compared the result against the
site it was asked to copy.

| Finding | Fix |
| --- | --- |
| **The site being copied had an interactive control this one lacked.** ScheduleFreeTime lets the reader change each sport's average game length and recomputes every day instantly. RADIOSF baked its estimates into the JSON where nobody could see or challenge them — and the whole 10-to-10 answer is built on them. | Every row now declares a duration bucket, `meta.durations` ships the defaults, and the band section renders an editable box per sport with a reset. Changing one recomputes the day view, the timeline, the calendar dots and the headline statistics. The measured sensitivity is in the README: the conclusion holds even at a flat four hours per broadcast. |
| **A flag claimed three checks and linked one page.** `MBB_NO_RADIO_ROWS` describes negative results from Westwood One, calbears.com and usfdons.com but offered a single link, so a reader could not repeat two of the three checks. | Flags may now carry a `sources` list; the page renders all of them. The builder rejects a flag whose primary `url` is not the first of its sources, and rejects any non-https flag link. |
| **A limitation flag cited Wikipedia as its source.** `WWO_POSTSEASON_UNDATED` linked the 2026 NFL season Wikipedia article — in a project whose rule is official links. | It now leads with nfl.com/schedules (the official page whose POST tab still redirects), then the Cumulus release, and keeps the secondary write-up last, explicitly labelled as not official and not used. |
| **Dead code.** `logic.js` exported three helpers nothing called — `clip`, `filterBroadcasts` and `shareStation`, the last one orphaned by the second pass's own conflict rewrite. `index.html` carried two CSS rules for classes never applied. | Removed. |
| **49ers rows had not been re-verified this session.** They are the most load-bearing official rows in the feed. | All fifteen re-read against 49ers.com: date, Pacific kickoff, radio line, venue, the Week 8 bye and the Week 18 TBD all match. The only character that differs anywhere in the set is the ® in "Levi's® Stadium", now documented in `VERIFICATION.md` as the single normalisation in the feed. |

## Found and fixed during the fourth pass

The fourth pass re-fetched the load-bearing sources on the same snapshot date, then read the shipped
data looking for transcription that had drifted from what the pages actually print.

| Finding | Fix |
| --- | --- |
| **Eleven college football venues had been shortened.** The second pass re-read the Westwood One NFL grid and restored every venue to the exact printed string, but the eleven NCAA Football rows were not re-read at the same time. All eleven had lost their state suffix — "Kenan Stadium, Chapel Hill" instead of "Kenan Stadium, Chapel Hill, NC" — and Army vs Navy printed only "MetLife Stadium" where the grid says "MetLife Stadium, East Rutherford, NJ". A shortened venue reads as tidy rather than as unverified, which is why it survived two review passes. | The NCAA Football grid was read end to end again, including the offset 10 page that carries Army vs Navy, and all eleven venues are now the exact printed strings. Nothing else on those rows moved. New note flag `NCAAF_VENUE_REREAD`. |
| **A source label described the wrong page.** Every college football row cited the offset 10 paging endpoint as `returns "No more events"`. Offset 10 is the page that *carries* Army vs Navy; the grid says "No more events" at offset 20. The label asserted the grid was exhausted one page earlier than it is. | Corrected, and the offset 20 page is now cited separately as the exhaustion proof. |
| **Official information was filed as unofficial.** The `WWO_POSTSEASON_UNDATED` flag said the playoff round dates came from "secondary write-ups" and were "not official". The league's own 2026-2027 important-dates announcement names every round. | Replaced by `NFL_POSTSEASON_WINDOWS`, which cites the league announcement first, keeps nfl.com's still-redirecting POST tab as the reason no per-game row exists, and demotes the secondary write-up to a corroborating link. Six window rows added, one per officially dated day. |
| **Automation covered 28 of 147 rows.** Only the MLB postseason API was watched, so the 79 Westwood One rows — the largest block in the feed — could change silently, and the empty college basketball grid that is the biggest winter hole was not watched at all. | `scripts/wwo_watch.py` polls all four Westwood One grids daily and compares event ids and printed titles with the snapshot. Coverage is 107 of 153 rows. A grid that cannot be read is reported as unknown, never as "no drift". See the automation boundary in `VERIFICATION.md`. |

## Open limitations, worst first

1. **No basketball rows for the 2026-27 season, November through February.** Westwood One's NCAA Basketball page says "No upcoming events"; the Cal 2026-27 schedule has no radio column; and the USF 2026-27 text schedule has no Radio/Listen field. An official USF preview for a 2025-26 game did say "Listen: KNBR 1050", but that prior-season clearance does not establish the station for the current season; KTCT's affiliate record alone is not a schedule. This is the largest hole in the winter half of the window. **It is now watched automatically**: the daily Action polls Westwood One's NCAA Basketball grid, which the snapshot records as empty, so the first event the network publishes raises a review issue without anyone having to remember to look. *Next: check current-season USF/Cal/Stanford previews and official WCC broadcast pages as they publish, and act on the issue the moment it opens.*
2. **NFL postseason has round dates but no per-game detail.** This was understated before. The league's own 2026-2027 important-dates announcement names Wild Card Weekend January 16-18, the Divisional Playoffs January 23-24, the AFC and NFC Championship Games January 31 and Super Bowl LXI February 14, 2027 at SoFi Stadium; an earlier pass filed those dates under “secondary write-ups, not official”. Cumulus separately guarantees every playoff game on Westwood One. Six window rows are now placed, one per officially dated day. What is still missing is which game is on which day, how many games a day carries, the matchups and the kickoffs — `nfl.com/schedules/2026/POST` still redirects to the regular season. *Next session: re-check nfl.com once the regular season ends on January 10; each wild-card and divisional game would then become its own dated row, and a 49ers playoff game would add 107.7 FM on sourced authority.*
3. **MLS Cup Playoffs have no radio plan.** The Earthquakes' radio table stops at Decision Day, Nov 7. If San Jose qualifies, November and December matches would be missing. *Next session: check the club newsroom after Nov 7.*
4. **MLB postseason is a network inference, not a clearance.** ESPN Radio carries every game and 1050 is an ESPN Radio affiliate; no page confirms an individual game on 1050, and there is only one ESPN Radio feed, so on a four-game day at most one can be on the air. Start times are TBD in MLB's own API. *The daily watcher flags future date/count/description/start-time differences from MLB's API. Monitoring beyond that single endpoint is now done — four Westwood One grids are watched alongside it. Next: re-check once brackets are set, and split dates into per-game rows only when a source supports the matchups and radio assignment.*
5. **Both KNBR weekly grids are frozen on the week of Aug 31 – Sep 7.** That is the only station-side programming evidence available, so the 10-to-10 finding is tested against a four-week-old format snapshot rather than a live log. *Next session: re-check; if the grids ever refresh, the talk-versus-games split can be measured properly.*
6. **Station-finder tables are all labelled "(2025)".** They are the lists linked from the live 2026 pages and no 2026 list exists, but every `indicated` row ultimately rests on them.
7. **Start times are listed starts, not kickoffs.** Westwood One prints a network join time and a placeholder 11:59 PM end. Where the same game also has a club row, the club time is 45–75 minutes later. All end times are estimates.
8. **Fifty-two placed rows have no clock time at all** — 41 TBD rows that are not wholly conditional (2 contain mixed possibilities, 6 are the new NFL playoff windows) and 11 wholly if-necessary rows. They appear in the day list and calendar; both contribute zero estimated minutes, but the 11 conditional rows are separately excluded from the non-conditional listing-day counts. Because duration and affiliate carriage are estimates, the total is not a measured floor or ceiling.
9. **Nothing before Sep 27, 2026.** Days earlier than the window read "before this snapshot", not "no game".
10. **This is a snapshot, not an automatically refreshed feed.** A daily read-only GitHub Action now compares **107 of the 153 rows** against five machine-readable sources: the MLB postseason Stats API (28 rows) and Westwood One's NFL, college football, college basketball and U.S. Soccer grids (63, 11, 0 and 5 rows). Drift or a failed check opens or refreshes one review issue. It does not update the feed or Pages, establish station clearance, or monitor the 46 club, school and station rows — the 49ers, Giants, Athletics, Cal, Stanford and Earthquakes listings still need a human re-read. Postponements, flexes and station changes remain absent from the published snapshot until a fresh line-by-line review and rebuild.
11. **KNBR 680 carries unidentified national baseball** on idle Giants days, per the stale grid. No 2026 source names the network or the games, so none were added.

## Suggested order of work for the next session

1. Re-run every fetch in `docs/VERIFICATION.md` and diff against the current feed. Anything that moved becomes a flag, not a silent edit.
2. Chase basketball on 1050 and 680 — USF Dons, Cal, Stanford, WCC — that is the biggest coverage win available.
3. Split the six NFL playoff window rows into per-game rows the moment nfl.com publishes the postseason grid; the round dates are already placed.
4. Split the MLB postseason date-rows into per-game rows once MLB assigns first pitches, and drop the "if necessary" dates that the brackets eliminate.
5. Check whether the Earthquakes publish a playoff radio plan.
6. Consider extending the window backwards to the start of the 2026 seasons, which needs another line-by-line pass over already-played games.
7. Extend the watcher to the club, school and station pages. Those are HTML, not endpoints, so the honest next step is a fetch-and-hash check that reports “this page changed, go look” rather than an attempt to parse a clearance out of them. The four Westwood One grids added this pass are the last of the sources that publish a machine-readable event list. Preserve the read-only boundary throughout: a detected change should prompt source review, never silently rewrite and publish an inferred station listing.

## Things that will not be fixed by more fetching

- Per-game affiliate clearance is simply not published by Cumulus or ESPN. "Indicated" is the honest ceiling for a network row, and preemption by a local game is real and frequent on 680 and 1050.
- Radio sign-off times are not published by anyone. Durations will stay estimates.
- Spanish-language and HD-subchannel broadcasts are out of scope by definition, because they are not on the six frequencies.
