# Limitations and the next session

Snapshot date: **2026-09-26**. This is a static verified list, not a live station log. GitHub Pages cannot watch the stations. A person still has to re-fetch sources when times move.

The calendar answers: “which verified live games are on the six stations that day?” It does not answer “what is KNBR saying at 11:14 AM?” unless that minute is inside a verified game window.

## Why 10 AM–10 PM is not filled

Checked, and not turned into fake games:

| What you might hear | What the source actually says | In the calendar? |
| --- | --- | --- |
| KNBR 680 / 104.5 late morning | Week of Aug 31–Sep 7 grid is sports talk (Fair & Biased), then a Giants block when they play. Grid is stale as of Sep 26. | Talk: no. Giants: yes, from the Stats API. |
| 1050 AM daytime | ESPN Radio pass-through and The Jim Rome Show. No 2026 per-game clearance list for this affiliate. | No |
| 960 AM daytime | Fox Sports Radio talk lineup announced by iHeart. Athletics games are the verified play-by-play. | Athletics only |
| 107.7 FM | Classic rock except 49ers games, which 49ers.com lists on KSAN every regular-season week in this snapshot. | 49ers only |
| Westwood One national games | Schedule page lists them. Station finder lists KNBR-AM, KNBR-FM, KTCT-AM for NFL, and warns that not every affiliate airs every game. | Yes, marked **indicated** |

On a stacked Saturday the estimated union can be a majority of 10 AM–10 PM. That is not the weekday pattern. The day view says which one it is.

## Irregularities already flagged

Open the site’s flag list, or `docs/LINE_BY_LINE.md`. The ones that can change a listening plan:

1. **Nov 21 Big Game** — Stanford’s July 30 release says 1050 AM. Cal’s schedule index says KNBR 104.5 / 680. Both are shown. Check both frequencies that day.
2. **Oct 17 Cal vs Wake Forest** — date is on the scoreboard. The KSFO line was not in the excerpt captured here. Badge is review.
3. **Stanford vs Elon, Oct 17** — 4:30 PM PT is ESPN’s 7:30 PM ET, not a kickoff copied from gostanford.com.
4. **Earthquakes times** — official radio table is Feb 16, 2026, and it says times can change. The live schedule widget did not render in a text fetch.
5. **Westwood One listed start** — printed Eastern time, converted by subtracting 3 hours. Event pages use placeholder end times (11:59 PM, 6:59 PM). 49ers kickoffs that Westwood One also lists are 45–75 minutes later. Club time is used for 49ers games.
6. **Eight international games vs seven on the page.** The eighth was not added.
7. **NFL postseason** except Super Bowl LXI’s date is not on the schedule page. Not placed.
8. **49ers Week 18** has stations and no date. Not placed on Jan 9 or 10.
9. **Nov 22 venue** — Estadio Banorte on 49ers.com, Estadio Azteca on Westwood One.
10. **Week 1–3 listen articles** say “all games” are on KSFO. The schedule page switches to KNBR in October. The schedule page wins.

## Work for the next session

Do these in order. Do not add a league until a radio row is on a page you opened.

1. Re-fetch `https://www.westwoodonesports.com/nfl-schedule/` from the top of the page. The opening chunk was not returned on 2026-09-26, so national games that appear only there are absent. Add a row only when the line is on the page. Do not restore a game from memory. Re-check event 548539 (Cowboys at Eagles, Oct 26), which was split across two fetches.
2. Re-fetch `https://www.49ers.com/schedule/` and place Week 18 only if a date is printed.
3. Re-fetch `https://www.westwoodonesports.com/nfl-schedule/` when postseason games get dates. Add only dated rows. Keep the preemption caveat.
4. Open the NCAA Football tab of the station finder and confirm or remove 680 / 104.5 / 1050 on college games. Right now those rows are marked indicated because only the NFL tab was extracted.
5. Open `https://calbears.com/sports/football/schedule` in a browser and quote the Radio column for every remaining game, especially Oct 17 Wake Forest and Nov 21.
6. Open the Stanford schedule page (it is JavaScript-rendered; a plain fetch returned the 2025 scoreboard) and confirm the Oct 17 Elon kickoff.
7. Re-check the Earthquakes live schedule against the Feb 16 radio table. If a kickoff moved, update the row and keep the source.
8. Pull the current KNBR weekly grid from `https://www.thesportsleader.com/shows/`. The copy fetched Sep 26 still showed Aug 31–Sep 7. A current grid is the only way to see which national games actually cleared that week.
9. Do not add Cal or Stanford basketball unless the 2026-27 schedule page prints a radio row. The Cal page fetched Sep 26 did not.
10. Do not add Warriors, Valkyries, or Sharks. Their flagships are 95.7 The Game and the Sharks Audio Network, not these six stations.
11. If a refresh script is added, it has to tolerate TLS failures. `curl` to statsapi.mlb.com failed in the build environment; the MLB API was readable through a separate fetch. A GitHub Action that only re-validates the committed file is already in `.github/workflows/verify.yml`. A network cron is not, because a failed fetch must not overwrite good data with an empty file.

## What “up to date” can mean here

The useful everyday object is the calendar plus the source link. It removes the need to open six station sites for the games that are already verified. It cannot stay current by itself. The next session’s job is a re-fetch, not a redesign, unless a source has moved.
