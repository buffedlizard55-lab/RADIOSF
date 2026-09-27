# Limitations, and the work that is still open

Snapshot 2026-09-27. 147 schedule entries: 136 rows with at least one non-conditional listing (2 are mixed) and 11 wholly if-necessary rows; 30 flags. The flags themselves live in `data/broadcasts.json` under `flags` and are rendered on the site under **Known gaps**, **Irregularities flagged for review** and **Notes**. This file is the human summary plus the to-do list.

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

## Open limitations, worst first

1. **No basketball rows for the 2026-27 season, November through February.** Westwood One's NCAA Basketball page says "No upcoming events"; the Cal 2026-27 schedule has no radio column; and the USF 2026-27 text schedule has no Radio/Listen field. An official USF preview for a 2025-26 game did say "Listen: KNBR 1050", but that prior-season clearance does not establish the station for the current season; KTCT's affiliate record alone is not a schedule. This is the largest hole in the winter half of the window. *Next: check current-season USF/Cal/Stanford previews and official WCC broadcast pages as they publish.*
2. **NFL postseason has no dates.** Cumulus guarantees every playoff game plus Super Bowl LXI on Westwood One, but `nfl.com/schedules/2026/POST` still redirects to the regular season, so only the Super Bowl is placed. Secondary write-ups say Jan 16–18 / Jan 23–24 / Jan 31; that is not official and is not used. *Next session: re-check nfl.com once the regular season ends; six wild-card games and four divisional games would each be a 1050/680/104.5 row.*
3. **MLS Cup Playoffs have no radio plan.** The Earthquakes' radio table stops at Decision Day, Nov 7. If San Jose qualifies, November and December matches would be missing. *Next session: check the club newsroom after Nov 7.*
4. **MLB postseason is a network inference, not a clearance.** ESPN Radio carries every game and 1050 is an ESPN Radio affiliate; no page confirms an individual game on 1050, and there is only one ESPN Radio feed, so on a four-game day at most one can be on the air. Start times are TBD in MLB's own API. *The daily watcher now flags future date/count/description/start-time differences from MLB's API. Next: re-check once brackets are set, split dates into per-game rows only when a source supports the matchups and radio assignment, and expand monitoring beyond this single endpoint.*
5. **Both KNBR weekly grids are frozen on the week of Aug 31 – Sep 7.** That is the only station-side programming evidence available, so the 10-to-10 finding is tested against a four-week-old format snapshot rather than a live log. *Next session: re-check; if the grids ever refresh, the talk-versus-games split can be measured properly.*
6. **Station-finder tables are all labelled "(2025)".** They are the lists linked from the live 2026 pages and no 2026 list exists, but every `indicated` row ultimately rests on them.
7. **Start times are listed starts, not kickoffs.** Westwood One prints a network join time and a placeholder 11:59 PM end. Where the same game also has a club row, the club time is 45–75 minutes later. All end times are estimates.
8. **Forty-six placed rows have no clock time at all** — 35 TBD rows that are not wholly conditional (2 contain mixed possibilities) and 11 wholly if-necessary rows. They appear in the day list and calendar; both contribute zero estimated minutes, but the 11 conditional rows are separately excluded from the non-conditional listing-day counts. Because duration and affiliate carriage are estimates, the total is not a measured floor or ceiling.
9. **Nothing before Sep 27, 2026.** Days earlier than the window read "before this snapshot", not "no game".
10. **This is a snapshot, not an automatically refreshed feed.** A daily read-only GitHub Action compares future dates, game descriptions and TBD starts from the MLB postseason Stats API with the committed MLB postseason rows; drift or a failed fetch opens or refreshes a review issue. It does not update the feed or Pages, establish station clearance, or monitor the other 2026 sources. Postponements, flexes, station changes and other source updates remain absent from the published snapshot until a fresh line-by-line review and rebuild.
11. **KNBR 680 carries unidentified national baseball** on idle Giants days, per the stale grid. No 2026 source names the network or the games, so none were added.

## Suggested order of work for the next session

1. Re-run every fetch in `docs/VERIFICATION.md` and diff against the current feed. Anything that moved becomes a flag, not a silent edit.
2. Chase basketball on 1050 and 680 — USF Dons, Cal, Stanford, WCC — that is the biggest coverage win available.
3. Add NFL playoff rounds the moment nfl.com publishes dates.
4. Split the MLB postseason date-rows into per-game rows once MLB assigns first pitches, and drop the "if necessary" dates that the brackets eliminate.
5. Check whether the Earthquakes publish a playoff radio plan.
6. Consider extending the window backwards to the start of the 2026 seasons, which needs another line-by-line pass over already-played games.
7. Expand the scheduled watcher to additional official machine-readable schedule endpoints (where available), and monitor the radio-clearance/affiliate sources separately. Preserve the read-only boundary: a detected change should prompt source review, not silently rewrite and publish an inferred station listing.

## Things that will not be fixed by more fetching

- Per-game affiliate clearance is simply not published by Cumulus or ESPN. "Indicated" is the honest ceiling for a network row, and preemption by a local game is real and frequent on 680 and 1050.
- Radio sign-off times are not published by anyone. Durations will stay estimates.
- Spanish-language and HD-subchannel broadcasts are out of scope by definition, because they are not on the six frequencies.
