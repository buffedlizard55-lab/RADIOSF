#!/usr/bin/env python3
"""Build the curated, source-backed schedule snapshot. Source of truth for data/broadcasts.json.

Every row below was transcribed from a page fetched on 2026-09-27.
Do not add a game that is not in this file. Re-fetch before editing.

Rules this file enforces:
  * only the six receivable stations may appear;
  * every row carries at least one source link that a person can open;
  * a row is only "official" when a club, school, league API or rights holder
    printed both the game and the station;
  * anything a source did not print is a flag, not a guess.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "broadcasts.json"
LINE = ROOT / "docs" / "LINE_BY_LINE.md"

ALLOWED = ["680", "810", "960", "1050", "104.5", "107.7"]
WINDOW_START = "2026-09-27"
WINDOW_END = "2027-02-28"
SNAPSHOT = "2026-09-27"

WWO_NFL_STATIONS = ["680", "104.5", "1050"]
WWO_NCAAF_STATIONS = ["680", "104.5", "1050"]
WWO_SOCCER_STATIONS = ["1050"]

# --- sources -----------------------------------------------------------------
WWO_NFL_URL = "https://www.westwoodonesports.com/nfl-schedule/"
WWO_NCAAF_URL = "https://www.westwoodonesports.com/ncaa-football/"
WWO_NCAAB_URL = "https://www.westwoodonesports.com/ncaa-basketball/"
WWO_SOCCER_URL = "https://www.westwoodonesports.com/us-soccer/"
WWO_FINDER = "https://www.westwoodonesports.com/station-finder/"
# Westwood One serves every sport's upcoming grid from one widget id. These are
# the machine-readable pages the automated watcher polls. The four ids were read
# off the live "More" links on each sport page on 2026-09-27.
WWO_GRID_ENDPOINT = "https://www.westwoodonesports.com/more/eventGrid"
WWO_WIDGETS = [
    {"widget": "47029", "prefix": "wwo-nfl-", "sport": "NFL",
     "page": WWO_NFL_URL, "title": "Upcoming+NFL+Broadcasts"},
    {"widget": "47030", "prefix": "wwo-ncaaf-", "sport": "NCAA Football",
     "page": WWO_NCAAF_URL, "title": "Upcoming+NCAA+Football+Broadcasts"},
    {"widget": "47031", "prefix": "wwo-ncaab-", "sport": "NCAA Basketball",
     "page": WWO_NCAAB_URL, "title": "Upcoming+NCAA+Basketball+Broadcasts"},
    {"widget": "47032", "prefix": "wwo-soccer-", "sport": "U.S. Soccer",
     "page": WWO_SOCCER_URL, "title": "Upcoming+U.S.+Soccer+Broadcasts"},
]
# Westwood One NFL listings folded into an official 49ers club row instead of being
# duplicated. validate() refuses to let them reappear as separate rows, and the
# watcher must not report them as missing from the snapshot.
WWO_MERGED_NFL_EVENTS = {"548538", "548491", "548568", "548509"}
# Paging endpoint that carries the eleventh college football row (Army vs Navy).
WWO_NCAAF_MORE = (
    "https://www.westwoodonesports.com/more/eventGrid?id=47030&range=current&offset=10&limit=10"
    "&timezone=America/New_York&widgetTitle=Upcoming+NCAA+Football+Broadcasts"
)
# The page after it, which is where the grid actually says "No more events".
WWO_NCAAF_MORE_END = (
    "https://www.westwoodonesports.com/more/eventGrid?id=47030&range=current&offset=20&limit=10"
    "&timezone=America/New_York&widgetTitle=Upcoming+NCAA+Football+Broadcasts"
)
PRESS = (
    "https://www.globenewswire.com/news-release/2026/09/09/3358684/9032/en/"
    "cumulus-media-s-westwood-one-official-network-audio-partner-of-the-nfl-"
    "celebrates-40th-consecutive-season-and-reveals-2026-nfl-lineup-and-"
    "programming-highlights-from-nfl-kickoff-to.html"
)
NINERS = "https://www.49ers.com/schedule/"
GIANTS_RADIO = "https://www.mlb.com/giants/schedule/tv"
ATH_RADIO = "https://www.mlb.com/athletics/schedule/affiliates"
MLB_POST_PRESS = "https://www.mlb.com/news/press-release-mlb-announces-2026-postseason-schedule"
MLB_POST_API = "https://statsapi.mlb.com/api/v1/schedule/postseason?season=2026&sportId=1"
QUAKES = "https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season"
QUAKES_PDF = "https://images.mlssoccer.com/image/upload/v1766018474/assets/sje/schedule/2026%20Schedule.pdf"
STANFORD_RADIO = "https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced"
STANFORD_TSL = "https://www.thesportsleader.com/stanfordfootball/"
STANFORD_ESPN = "https://www.espn.com/college-football/team/schedule/_/id/24/stanford-cardinal"
GOSTANFORD_SCHED = "https://gostanford.com/sports/football/schedule"
CAL = "https://calbears.com/sports/football/schedule"
CAL_ESPN = "https://www.espn.com/college-football/team/schedule/_/id/25/california-golden-bears"
CAL_MBB = "https://calbears.com/sports/mens-basketball/schedule"
USF_MBB = "https://usfdons.com/sports/mens-basketball/schedule"
USF_MBB_TEXT = "https://usfdons.com/sports/mens-basketball/schedule/text"
USF_MBB_2026_PREVIEW = "https://usfdons.com/news/2026/1/27/mens-basketball-san-francisco-heads-to-santa-clara-for-late-night-showdown"
KNBR_SHOWS = "https://www.thesportsleader.com/shows/"
KNBR_1050_SHOWS = "https://www.thesportsleader.com/knbr1050shows/"
KTCT_WIKI = "https://en.wikipedia.org/wiki/KTCT"
KNEW_WIKI = "https://en.wikipedia.org/wiki/KNEW_(AM)"
NFL_SEASON_WIKI = "https://en.wikipedia.org/wiki/2026_NFL_season"
NFL_SCHEDULES = "https://www.nfl.com/schedules/"
# The league's own 2026-2027 important-dates announcement, republished verbatim by
# an NFL club. This is where the postseason round dates come from; nfl.com/schedules/2026/POST
# still redirects to the regular season and prints no round dates.
NFL_IMPORTANT_DATES = "https://www.seahawks.com/news/nfl-announces-important-dates-for-2026-2027"

# Every row belongs to a duration bucket. The minutes are estimates, not measured
# broadcast lengths, so the page lets the reader change them and recompute; these
# are only the starting values.
DURATIONS = [
    {"id": "MLB", "label": "MLB regular season", "minutes": 165},
    {"id": "MLB-POST", "label": "MLB postseason", "minutes": 210},
    {"id": "NFL", "label": "NFL", "minutes": 195},
    {"id": "NCAAF", "label": "College football", "minutes": 204},
    {"id": "MLS", "label": "MLS", "minutes": 120},
    {"id": "SOCCER", "label": "International soccer", "minutes": 120},
]
DUR = {d["id"]: d["minutes"] for d in DURATIONS}
LEAGUE_DUR = {"MLB": 165, "NFL": 195, "NCAAF": 204, "MLS": 120, "SOCCER": 120}


def et_to_pt(hhmm: str) -> str:
    """Convert a printed Eastern clock time to Pacific. Refuses to wrap a day."""
    h, m = (int(x) for x in hhmm.split(":"))
    total = h * 60 + m - 180
    if total < 0 or total >= 24 * 60:
        raise SystemExit(f"ET time {hhmm} crosses midnight; handle explicitly")
    return f"{total // 60:02d}:{total % 60:02d}"


def src(label: str, url: str) -> dict:
    if not url.startswith("https://"):
        raise SystemExit(f"bad url {url}")
    return {"label": label, "url": url}


def game(**kw) -> dict:
    row = {
        "id": kw["id"],
        "date": kw.get("date"),
        "start_pt": kw.get("start_pt"),
        "title": kw["title"],
        "league": kw["league"],
        "network": kw.get("network") or "",
        "venue": kw.get("venue") or "",
        "status": kw.get("status", "scheduled"),
        "conditional": bool(kw.get("conditional")),
        "result": kw.get("result"),
        "stations": kw["stations"],
        "confidence": kw["confidence"],
        "duration_key": kw.get("duration_key") or kw["league"],
        "duration_est_min": kw.get("duration_est_min") or LEAGUE_DUR[kw["league"]],
        "sources": kw["sources"],
        "notes": kw.get("notes") or "",
        "flag_ids": kw.get("flag_ids") or [],
    }
    if "game_count" in kw:
        row["game_count"] = int(kw["game_count"])
    if "conditional_game_count" in kw:
        row["conditional_game_count"] = int(kw["conditional_game_count"])
    bad = [s for s in row["stations"] if s not in ALLOWED]
    if bad:
        raise SystemExit(f"{row['id']} bad station {bad}")
    if not row["stations"]:
        raise SystemExit(f"{row['id']} has no station")
    if not row["sources"]:
        raise SystemExit(f"{row['id']} needs a source")
    if row["confidence"] not in ("official", "indicated", "review"):
        raise SystemExit(f"{row['id']} bad confidence {row['confidence']}")
    if row["status"] not in ("scheduled", "tba", "final", "pregame", "if-necessary"):
        raise SystemExit(f"{row['id']} bad status {row['status']}")
    if "game_count" in row and row["game_count"] <= 0:
        raise SystemExit(f"{row['id']} game_count must be positive")
    if row["status"] == "if-necessary" and not row["conditional"]:
        raise SystemExit(f"{row['id']} must mark an if-necessary row as conditional")
    if (row["status"] == "if-necessary" and "game_count" in row and
            row.get("conditional_game_count", row["game_count"]) != row["game_count"]):
        raise SystemExit(f"{row['id']} wholly conditional row must count all its games as conditional")
    if "conditional_game_count" in row and (
        "game_count" not in row or row["conditional_game_count"] < 0 or
        row["conditional_game_count"] > row["game_count"]
    ):
        raise SystemExit(f"{row['id']} has an invalid conditional_game_count")
    if row["date"] and not (WINDOW_START <= row["date"] <= WINDOW_END):
        raise SystemExit(f"{row['id']} date {row['date']} outside window")
    if row["start_pt"] and not row["date"]:
        raise SystemExit(f"{row['id']} has a time but no date")
    if row["duration_key"] not in DUR:
        raise SystemExit(f"{row['id']} duration_key {row['duration_key']} is not a known bucket")
    if row["duration_est_min"] != DUR[row["duration_key"]]:
        raise SystemExit(
            f"{row['id']} duration {row['duration_est_min']} does not match bucket "
            f"{row['duration_key']} ({DUR[row['duration_key']]}); the page recomputes by bucket"
        )
    return row


def wwo_event(event_id: str) -> str:
    return f"https://www.westwoodonesports.com/events/{event_id}"


def mlb_game(pk: int) -> str:
    return f"https://statsapi.mlb.com/api/v1.1/game/{pk}/feed/live"


FLAGS = [
    {
        "id": "NO_STANDING_10_TO_10",
        "severity": "limitation",
        "title": "10 AM–10 PM is not a verified live-game block",
        "detail": (
            "Re-checked 2026-09-27. KNBR's own weekly grid (thesportsleader.com/shows) fills "
            "6 AM to 6 PM with local talk — Murph & Markus, Fair & Biased, Dirty Work — and adds one "
            "three-to-four-hour game block on most days, not a continuous one. The KNBR 1050 grid "
            "(thesportsleader.com/knbr1050shows) is the ESPN Radio network schedule on weekdays "
            "with game blocks mainly Friday, Saturday and Sunday. KNEW 960's weekday daypart is "
            "Fox Sports Radio talk. So the 10-to-10 band is mostly talk on a weekday and mostly "
            "games on an autumn weekend. The day view measures that instead of assuming it."
        ),
        "url": KNBR_SHOWS,
    },
    {
        "id": "KNBR_GRID_STALE",
        "severity": "review",
        "title": "Both KNBR weekly grids are frozen on the week of Aug 31 – Sep 7",
        "detail": (
            "Re-fetched 2026-09-27: thesportsleader.com/shows and thesportsleader.com/knbr1050shows "
            "both still print Monday 8-31 through Monday 9-7, about four weeks stale. They are "
            "evidence of format (which dayparts are talk and which are play-by-play), not a "
            "current-week clearance log. No clock time on those grids is used as a broadcast row here."
        ),
        "url": KNBR_1050_SHOWS,
    },
    {
        "id": "WWO_PREEMPTION",
        "severity": "review",
        "title": "Westwood One affiliates do not air every game",
        "detail": (
            "Station finder, re-fetched 2026-09-27: \"Because of local blackouts and/or programming "
            "conflicts, not every affiliate can air every Westwood One Sports broadcast.\" "
            "San Francisco rows: NFL — KNBR-AM, KNBR-F2, KNBR-FM, KTCT-AM. NCAA Football — the same "
            "four. Soccer — KTCT-AM only. KNBR-F2 is an HD subchannel and is not counted. A local "
            "Giants, 49ers, Stanford or Earthquakes broadcast can preempt the national feed on the "
            "station it occupies, which is why these rows are \"indicated\" and never \"official\"."
        ),
        "url": WWO_FINDER,
    },
    {
        "id": "FINDER_2025_LABEL",
        "severity": "review",
        "title": "Station-finder tables are labelled \"(2025)\" on the live 2026 pages",
        "detail": (
            "Every affiliate table on westwoodonesports.com/station-finder carries a season label in "
            "its footer: \"NFL Regular Season (2025)\", \"NCAA Football Season (2025)\", "
            "\"USA Soccer (2025)\". The pages are the ones linked from the live 2026 schedule, and "
            "no 2026-labelled list exists on the site, so they are used as the best available "
            "affiliate list. Treat any single call sign as last season's line-up until Cumulus "
            "re-publishes. NCAA Basketball, Baseball, Softball, Lacrosse, Hockey and Golf tabs are "
            "placeholder \"check back\" text with no stations at all."
        ),
        "url": WWO_FINDER,
    },
    {
        "id": "WWO_LISTED_START",
        "severity": "review",
        "title": "Westwood One printed time is a listed start, not a confirmed kickoff",
        "detail": (
            "Event 548494 prints \"Sun Sep 27, 2026 7:30 PM – 11:59 PM (EDT).\" 11:59 PM is a "
            "placeholder end, not a real ending. 49ers.com kickoffs for the four 49ers games that "
            "Westwood One also lists are 45 to 75 minutes later than the Westwood One printed start. "
            "This feed converts the printed Eastern time to Pacific and labels it a listed start. "
            "It does not invent a kickoff."
        ),
        "url": "https://www.westwoodonesports.com/events/548494",
    },
    {
        "id": "WWO_EIGHT_VS_SEVEN",
        "severity": "note",
        "title": "Press release counts eight international games; seven are still ahead",
        "detail": (
            "The Cumulus release of 2026-09-09 says the package includes eight International Games "
            "for the whole season. The Upcoming list on the schedule page, fully read in four chunks "
            "on 2026-09-27, holds seven: London Oct 4, Oct 11 and Oct 18; Paris Oct 25; Madrid Nov 8; "
            "Munich Nov 15; Mexico City Nov 22. The NFL's 2026 international slate began in September, "
            "before this snapshot opens, so the eighth is a game that has already been played. "
            "Nothing is missing from the forward-looking list."
        ),
        "url": PRESS,
    },
    {
        "id": "NFL_POSTSEASON_WINDOWS",
        "severity": "review",
        "title": "NFL playoff rounds are officially dated, but not per game",
        "detail": (
            "The league's own 2026-2027 important-dates announcement names the rounds: "
            "Week 18 January 9-10, Wild Card Weekend January 16-18, Divisional Playoffs "
            "January 23-24, the AFC and NFC Championship Games January 31, and Super Bowl LXI "
            "February 14, 2027 at SoFi Stadium. The Cumulus release of September 9, 2026 says "
            "Westwood One carries every postseason game, and the station finder puts Westwood One "
            "on KNBR-AM, KNBR-FM and KTCT-AM in San Francisco. So the rounds are dated and the "
            "network is known, but no official source says which game falls on which day, how many "
            "games each day carries, who plays, or when it kicks off \u2014 nfl.com/schedules/2026/POST "
            "still redirected to the regular season when fetched on 2026-09-27, and the Westwood One "
            "grid ends at the Week 18 TBA windows. Each day of an officially named window therefore "
            "carries one row, with no game count and no clock time, rather than leaving those five "
            "days blank. An earlier version of this flag called these dates unofficial; they are the "
            "league's own announcement and that was wrong. What is still missing is the per-game "
            "detail. If the 49ers reach the postseason their games would also be expected on the club "
            "flagship, but no source publishes a postseason 49ers radio line, so 107.7 FM is not "
            "claimed on any playoff row."
        ),
        "url": NFL_IMPORTANT_DATES,
        "sources": [
            src("League important dates for 2026-2027, republished by an NFL club \u2014 the round dates", NFL_IMPORTANT_DATES),
            src("Cumulus release: Westwood One carries every playoff game and Super Bowl LXI", PRESS),
            src("NFL.com schedules \u2014 the 2026 POST tab still redirects and prints no round dates", NFL_SCHEDULES),
            src("Secondary write-up \u2014 agrees on the dates, not official and not relied on", NFL_SEASON_WIKI),
        ],
    },
    {
        "id": "MLB_POSTSEASON_ESPN",
        "severity": "review",
        "title": "MLB postseason is an ESPN Radio network row, not a Bay Area per-game clearance",
        "detail": (
            "MLB's own postseason release says \"ESPN Radio will provide live national coverage of "
            "all 2026 MLB Postseason games.\" KTCT 1050 AM is a full-time ESPN Radio affiliate: its "
            "published weekly grid is the ESPN Radio network schedule, and its station record lists "
            "ESPN Radio as the network. No Cumulus or ESPN page publishes a game-by-game Bay Area "
            "clearance list, so these rows are \"indicated\". Three further caveats. There is one "
            "ESPN Radio feed, so on a day with two or four scheduled games only one of them can be "
            "on 1050 at a time. Start times were still TBD in the Stats API on 2026-09-27 — every "
            "game carries a placeholder 07:33 UTC with startTimeTBD true — so no clock time is shown. "
            "And Stanford football, Earthquakes soccer and Westwood One college football all preempt "
            "1050 on autumn weekends. Neither the Giants nor the Athletics are in this field."
        ),
        "url": MLB_POST_PRESS,
    },
    {
        "id": "NO_LOCAL_MLB_AFTER_0927",
        "severity": "note",
        "title": "Local baseball ends September 27",
        "detail": (
            "The MLB Stats API returned exactly one remaining Giants game and one remaining "
            "Athletics game when queried on 2026-09-27 for 2026-09-27 through 2026-11-15. Both clubs "
            "finish that afternoon and neither appears in the postseason bracket. After September 27 "
            "there is no Giants call on 680/104.5 and no Athletics call on 960 in this window."
        ),
        "url": MLB_POST_API,
    },
    {
        "id": "KNBR_MLB_FILLER",
        "severity": "review",
        "title": "KNBR 680 carries national baseball on idle Giants days, with no published list",
        "detail": (
            "The stale KNBR grid shows blocks such as \"Sun 9-6 3:20–6:00p JIP @ first pitch – MLB: "
            "TWINS @ WHITE SOX\" and \"Mon 9-7 9:30a–1:00p MLB: BRAVES @ PHILLIES\" on days the Giants "
            "were not playing. That proves 680 fills with somebody's national baseball feed, but no "
            "2026 source names the network or lists which games clear. No such row is invented here."
        ),
        "url": KNBR_SHOWS,
    },
    {
        "id": "BIG_GAME_STATIONS",
        "severity": "review",
        "title": "Nov 21 Big Game station claims disagree",
        "detail": (
            "calbears.com/sports/football/schedule, re-read 2026-09-27, prints "
            "\"KNBR 104.5 FM / 680 AM\" in the Radio column of the Nov 21 Stanford row — the only "
            "2026 Cal row that is not KSFO 810. Stanford's own football radio release puts the "
            "Cardinal broadcast on KNBR/KTCT 1050 AM all season. One game, two station claims, and "
            "both are shown. Neither is dropped and 810 is not assumed."
        ),
        "url": CAL,
    },
    {
        "id": "GOSTANFORD_2025",
        "severity": "review",
        "title": "gostanford.com serves last season's football schedule",
        "detail": (
            "Fetched 2026-09-27, gostanford.com/sports/football/schedule returns 2025 rows and "
            "/schedule/2026 returns 404. Stanford dates and kickoffs in this feed therefore come from "
            "ESPN's 2026 Stanford schedule, converted from Eastern to Pacific. The station, 1050 AM, "
            "comes from Stanford's own radio release and from the KNBR 1050 weekly grid, which shows "
            "\"Stanford Pre-Game with Jack Loder\" followed by a \"STANFORD FOOTBALL\" block. "
            "Re-check the school site once it rolls over to 2026."
        ),
        "url": GOSTANFORD_SCHED,
    },
    {
        "id": "SFT_RADIO_DIFF",
        "severity": "review",
        "title": "This site and ScheduleFreeTime do not list the same radio games",
        "detail": (
            "ScheduleFreeTime does not put a radio icon on Athletics games. The club affiliates page "
            "lists 960 AM KNEW, Bay Area, with no home-only asterisk, so the remaining A's game is "
            "here. ScheduleFreeTime also lists KZSF 1370 AM on Earthquakes broadcasts; 1370 is not "
            "one of the six stations, so it is omitted. ScheduleFreeTime carries no Westwood One "
            "national rows and no ESPN Radio postseason rows at all."
        ),
        "url": ATH_RADIO,
    },
    {
        "id": "QUAKES_SUBJECT_TO_CHANGE",
        "severity": "review",
        "title": "Earthquakes radio table is dated Feb 16, 2026 and says times can change",
        "detail": (
            "The club's radio release is the only per-game English-station table published. It says "
            "\"All times and dates are subject to change.\" The live schedule widget at "
            "sjearthquakes.com/schedule renders client-side and returned no match data on "
            "2026-09-27, so a later kickoff move would not be visible here until the next pass. "
            "The release names KSFO 810 AM as the English flagship and KZSF 1370 AM as the Spanish "
            "flagship; 1370 is not one of the six stations."
        ),
        "url": QUAKES,
    },
    {
        "id": "QUAKES_OCT31_TIME",
        "severity": "review",
        "title": "Oct 31 Earthquakes kickoff: the club's two documents disagree",
        "detail": (
            "The February radio release prints 2:00 PM for Real Salt Lake at San Jose on Saturday "
            "October 31. The club's own printable 2026 schedule PDF prints TBD for the same match. "
            "2:00 PM is used because it is the only stated time, the row is marked review, and both "
            "documents are linked. Check the club schedule before planning around it."
        ),
        "url": QUAKES_PDF,
    },
    {
        "id": "QUAKES_ALT_STATION",
        "severity": "review",
        "title": "Some Earthquakes matches move to 1050 instead of 810",
        "detail": (
            "The radio release says \"Select games may appear on alternative stations for English "
            "radio\" and its legend covers KNBR 680, KTCT 1050, KSFO 810 and KZSF 1370. The KNBR 1050 "
            "weekly grid independently shows a \"SAN JOSE EARTHQUAKES @ AUSTIN FC\" block on 1050. "
            "This feed lists the station printed in the per-game table, which is 810 for every "
            "remaining match, but a move to 1050 or 680 is possible and would not be announced here."
        ),
        "url": QUAKES,
    },
    {
        "id": "QUAKES_PLAYOFFS",
        "severity": "limitation",
        "title": "MLS Cup Playoff radio plans are not published",
        "detail": (
            "The Earthquakes radio release covers the 34-match regular season and stops at Decision "
            "Day, November 7. No fetched page says which station would carry an Audi MLS Cup Playoffs "
            "match in November or December 2026. Nothing is placed for the playoffs."
        ),
        "url": QUAKES,
    },
    {
        "id": "SOCCER_FINDER_ONLY",
        "severity": "review",
        "title": "U.S. Soccer clearance on 1050 is a station-finder row, not a per-match confirmation",
        "detail": (
            "Westwood One's U.S. Soccer page lists five upcoming national-team broadcasts with times "
            "and announcers. The Soccer tab of the station finder lists exactly one Bay Area "
            "affiliate — San Francisco, CA, KTCT-AM — under a footer reading \"USA Soccer (2025)\". "
            "Two of the five matches are labelled \"TNT Sports Broadcast - Audio Only Simulcast\" "
            "rather than an original Westwood One call. No Cumulus page confirms these specific "
            "matches on 1050, so all five are indicated, not official."
        ),
        "url": WWO_FINDER,
    },
    {
        "id": "WEEK18_UNPLACED",
        "severity": "review",
        "title": "49ers Week 18 has stations but no date",
        "detail": (
            "49ers.com/schedule prints Week 18 at Arizona Cardinals, State Farm Stadium, TV TBD, "
            "radio KSAN 107.7 / KNBR 104.5 / 680, and no date. It is not placed on Jan 9 or Jan 10. "
            "Those days already carry separate Westwood One \"teams TBA\" windows."
        ),
        "url": NINERS,
    },
    {
        "id": "MEXICO_VENUE_NAMES",
        "severity": "review",
        "title": "Nov 22 venue name disagrees",
        "detail": (
            "49ers.com prints Estadio Banorte. Westwood One event 548491 prints \u201cEst\u00e1dio Azteca, "
            "Mexico City, Mexico\u201d, transcribed here exactly as printed, accent and all. "
            "Both names are kept. Kickoff used here is the club time, 5:20 PM PT. The national "
            "Westwood One listing for the same game is merged into this row rather than duplicated."
        ),
        "url": NINERS,
    },
    {
        "id": "WWO_VENUE_STRINGS",
        "severity": "note",
        "title": "Westwood One prints the same stadium two different ways",
        "detail": (
            "Venues on the NFL grid are copied character for character, so the inconsistencies on "
            "the source page survive into this feed. Denver is \u201cEmpower Field at Mile High, "
            "Denver, CO\u201d on Sep 27 and Dec 25 but \u201cMile High Stadium, Denver, CO\u201d on Oct 15. "
            "Detroit is \u201cFord Field, Detroit, MI, USA\u201d on Nov 26 and \u201cFord Field, Detroit, "
            "Michigan\u201d on Dec 28. Charlotte carries a trailing \u201c, USA\u201d that no other domestic "
            "row has. The four Saturday and Sunday \u201cTBA\u201d placeholders print no venue at all, so "
            "their venue is empty here rather than guessed. Nothing was normalised, because "
            "normalising is how a wrong venue would get laundered into a confident one."
        ),
        "url": WWO_NFL_URL,
    },
    {
        "id": "NCAAF_VENUE_REREAD",
        "severity": "note",
        "title": "College football venues were re-read and now carry the full printed string",
        "detail": (
            "The second pass re-read the Westwood One NFL grid and restored every venue to the exact "
            "printed string, but the eleven college football rows were not re-read at the same time and "
            "kept a shortened venue: the state suffix had been dropped from all eleven, and Army vs Navy "
            "printed only \u201cMetLife Stadium\u201d where the grid says \u201cMetLife Stadium, East Rutherford, "
            "NJ\u201d. A shortened venue is not a wrong venue, which is why it survived review \u2014 it reads "
            "as tidy rather than as unverified. The NCAA Football grid was read end to end again on "
            "2026-09-27, including the offset 10 page that carries Army vs Navy, and all eleven venues "
            "are now the exact printed strings. No other field on those rows changed: every date, event "
            "id, listed start time and title still matches."
        ),
        "url": WWO_NCAAF_URL,
        "sources": [
            {"label": "Westwood One NCAA football grid, read end to end 2026-09-27", "url": WWO_NCAAF_URL},
            {"label": "Offset 10 page carrying Army vs Navy and its full venue", "url": WWO_NCAAF_MORE},
        ],
    },
    {
        "id": "NINERS_BOILERPLATE",
        "severity": "review",
        "title": "Week 1–3 listen articles say \"all games\" are on KSFO; the schedule page switches in October",
        "detail": (
            "Ways-to-listen articles for Weeks 1–3 say all games can be heard on KSFO 810 / "
            "KSAN 107.7. The live schedule page, re-read 2026-09-27, prints KSFO/KSAN for Week 3 and "
            "KSAN plus KNBR 104.5 / 680 from Week 4 on. This feed follows the per-game line on the "
            "schedule page, which is why 810 appears once and then stops."
        ),
        "url": "https://www.49ers.com/news/ways-to-watch-and-listen-cardinals-vs-49ers-week-3-x8427",
    },
    {
        "id": "HD_NOT_COUNTED",
        "severity": "limitation",
        "title": "HD subchannels are not counted as the stations you get",
        "detail": (
            "Westwood One lists KNBR-F2. KSAN's HD3 simulcasts KTCT. A standard AM/FM radio does not "
            "decode those. Only 680, 810, 960, 1050, 104.5 and 107.7 are listed."
        ),
        "url": WWO_FINDER,
    },
    {
        "id": "TALK_NOT_GAMES",
        "severity": "limitation",
        "title": "Network talk fills most of the weekday; only rights-holder rows are listed as games",
        "detail": (
            "KTCT 1050 is mainly an ESPN Radio pass-through plus The Jim Rome Show. KNEW 960's "
            "weekday daypart is Fox Sports Radio talk. Those are not games. The one network-wide "
            "clearance this feed does assert is MLB postseason on 1050, because MLB itself names "
            "ESPN Radio as the carrier of every postseason game and 1050 is an ESPN Radio affiliate. "
            "No equivalent statement exists for NBA, NHL, golf or NASCAR on these stations in this "
            "window, so none of those are listed."
        ),
        "url": KNEW_WIKI,
    },
    {
        "id": "MBB_NO_RADIO_ROWS",
        "severity": "limitation",
        "title": "No basketball rows could be verified for the 2026-27 season",
        "detail": (
            "Current-season checks on 2026-09-27 found no 2026-27 radio listing. Westwood One's NCAA Basketball page says "
            "\"No upcoming events\", so there is no national college hoops grid to transcribe. "
            "calbears.com men's basketball lists games from Nov 2 with TBD times and no radio column. "
            "The USF Dons 2026-27 text schedule lists dates, times, opponents, locations, tournament "
            "and results but no Radio/Listen field; the live schedule displays TV logos for some "
            "games. An official 2025-26 preview did say \"Listen: KNBR 1050\", but that is prior-season "
            "evidence, not confirmation of a 2026-27 station assignment. KTCT's station record also "
            "names the Dons as an affiliate, which is not a season schedule. Stanford basketball: "
            "KNBR's site has a Stanford Football page, but thesportsleader.com/stanfordbasketball "
            "returned \"Page Not Found\" on 2026-09-27, and the gostanford pages naming KNBR 1050 for "
            "men's basketball date from 2013 and 2017, so nothing is placed on 1050 for 2026-27. "
            "Re-checked 2026-09-27: the USF 2026-27 text schedule now lists 34 dates, still with no "
            "station and mostly blank times. The daily page watch alerts when \"KNBR\" appears on it, "
            "and the Westwood One watch alerts when its basketball grid gains an event. "
            "Basketball is therefore absent from "
            "November to February, which is a gap in this feed, not a quiet radio dial."
        ),
        "url": WWO_NCAAB_URL,
        "sources": [
            src("Westwood One NCAA Basketball: \u201cNo upcoming events\u201d", WWO_NCAAB_URL),
            src("Cal men's basketball schedule: no radio column", CAL_MBB),
            src("USF Dons 2026-27 men's basketball schedule", USF_MBB),
            src("USF Dons 2026-27 schedule text table: no Radio/Listen field", USF_MBB_TEXT),
            src("USF Dons Jan 28, 2026 preview: KNBR 1050 listen line, prior season only", USF_MBB_2026_PREVIEW),
        ],
    },
    {
        "id": "ATHLETICS_SACRAMENTO",
        "severity": "note",
        "title": "Athletics home games are in Sacramento; 960 AM still carries them",
        "detail": (
            "mlb.com/athletics/schedule/affiliates, re-read 2026-09-27, lists 960 AM KNEW, Bay Area, "
            "with no home-only asterisk — the asterisks on that table mark the Spanish and Las Vegas "
            "outlets. Flagship is 650 AM KSTE in Sacramento. Home venue in the Stats API is "
            "Sutter Health Park."
        ),
        "url": ATH_RADIO,
    },
    {
        "id": "SPANISH_EXCLUDED",
        "severity": "note",
        "title": "Spanish calls are not on the six stations",
        "detail": (
            "Giants Spanish is KSFN 1510 / KXZM 93.7. Earthquakes Spanish is KZSF 1370. 49ers Spanish "
            "is the club app and 49ers.com/esp. MLB's postseason Spanish audio is Univision Radio. "
            "None of those are among the six stations, so those calls are omitted."
        ),
        "url": GIANTS_RADIO,
    },
    {
        "id": "OTHER_TEAMS_EXCLUDED",
        "severity": "note",
        "title": "Warriors, Valkyries and Sharks are deliberately absent",
        "detail": (
            "Golden State Warriors and Valkyries broadcasts are on 95.7 FM and San Jose Sharks games "
            "are on 98.5 FM. Neither frequency is one of the six you asked about, so those teams are "
            "out of scope rather than missing. KTCT carried Warriors overflow until 2016 and no "
            "longer does."
        ),
        "url": KTCT_WIKI,
    },
    {
        "id": "SNAPSHOT_START",
        "severity": "limitation",
        "title": "This snapshot starts September 27, 2026",
        "detail": (
            "Earlier September games were on these stations. They are not in this file, so days "
            "before Sep 27 are marked \"before this snapshot\" instead of \"no game.\" Extending "
            "backward needs another line-by-line pass."
        ),
        "url": GIANTS_RADIO,
    },
    {
        "id": "DURATION_ESTIMATE",
        "severity": "note",
        "title": "End times are estimates",
        "detail": (
            "No source publishes a per-game radio sign-off. The timeline uses typical lengths — "
            "MLB 2:45, MLB postseason 3:30, NFL 3:15, college football 3:24, soccer 2:00 — and labels "
            "them estimates. They are not official endings. Pregame length is not added, even though "
            "the KNBR grids show a one-hour pregame before Giants and Stanford blocks."
        ),
        "url": KNBR_SHOWS,
    },
]


# --- Westwood One NFL ---------------------------------------------------------
def wwo_nfl_rows() -> list[dict]:
    """Every Upcoming row on westwoodonesports.com/nfl-schedule, read in four chunks
    on 2026-09-27. Four games the 49ers also play are omitted here and attached to the
    club rows instead, so the national feed is never double counted.
    """
    # Transcribed verbatim from the Upcoming list: event id, date, printed ET,
    # printed title, printed venue string, printed slot label after the "//".
    raw = [
        ("548494", "2026-09-27", "19:30", "Los Angeles Rams at Denver Broncos", "Empower Field at Mile High, Denver, CO", "Sunday Night Football"),
        ("548532", "2026-09-28", "19:00", "Philadelphia Eagles at Chicago Bears", "Soldier Field, Chicago, IL", "Monday Night Football"),
        ("548554", "2026-10-01", "19:30", "Pittsburgh Steelers at Cleveland Browns", "Huntington Bank Field, Cleveland, OH", "Thursday Night Football"),
        ("548485", "2026-10-04", "09:15", "Indianapolis Colts vs Washington Commanders", "Tottenham Hotspur Stadium, London, UK", "2026 NFL London Games"),
        ("548495", "2026-10-04", "19:30", "Detroit Lions at Carolina Panthers", "Bank of America Stadium, Charlotte, NC, USA", "Sunday Night Football"),
        ("548535", "2026-10-05", "19:00", "Atlanta Falcons at New Orleans Saints", "Caesars Superdome, New Orleans, LA", "Monday Night Football"),
        ("548556", "2026-10-08", "19:30", "Tampa Bay Buccaneers at Dallas Cowboys", "AT&T Stadium, Arlington, TX", "Thursday Night Football"),
        ("548486", "2026-10-11", "09:15", "Philadelphia Eagles vs Jacksonville Jaguars", "Tottenham Hotspur Stadium, London, UK", "2026 NFL London Games"),
        ("548496", "2026-10-11", "19:30", "Baltimore Ravens at Atlanta Falcons", "Mercedes-Benz Stadium, Atlanta, GA", "Sunday Night Football"),
        ("548537", "2026-10-12", "19:00", "Buffalo Bills at Los Angeles Rams", "SoFi Stadium, Inglewood, CA", "Monday Night Football"),
        ("548557", "2026-10-15", "19:30", "Seattle Seahawks at Denver Broncos", "Mile High Stadium, Denver, CO", "Thursday Night Football"),
        ("548487", "2026-10-18", "09:15", "Houston Texans vs Jacksonville Jaguars", "Wembley Stadium, London, UK", "2026 NFL London Games"),
        ("548497", "2026-10-18", "19:30", "Dallas Cowboys at Green Bay Packers", "Lambeau Field, Green Bay, WI", "Sunday Night Football"),
        ("548558", "2026-10-22", "19:30", "New England Patriots at Chicago Bears", "Soldier Field, Chicago, IL", "Thursday Night Football"),
        ("548488", "2026-10-25", "09:15", "Pittsburgh Steelers vs New Orleans Saints", "Stade de France, Paris, France", "2026 NFL Paris Game"),
        ("548498", "2026-10-25", "19:30", "Kansas City Chiefs at Seattle Seahawks", "Lumen Field, Seattle, WA", "Sunday Night Football"),
        ("548539", "2026-10-26", "19:00", "Dallas Cowboys at Philadelphia Eagles", "Lincoln Financial Field, Philadelphia, PA", "Monday Night Football"),
        ("548560", "2026-10-29", "19:30", "Carolina Panthers at Green Bay Packers", "Lambeau Field, Green Bay, WI", "Thursday Night Football"),
        ("548499", "2026-11-01", "19:30", "Philadelphia Eagles at Washington Commanders", "Northwest Stadium, Landover, MD", "Sunday Night Football"),
        ("548540", "2026-11-02", "19:00", "Chicago Bears at Seattle Seahawks", "Lumen Field, Seattle, WA", "Monday Night Football"),
        ("548561", "2026-11-05", "19:30", "Jacksonville Jaguars at Baltimore Ravens", "M&T Bank Stadium, Baltimore, MD", "Thursday Night Football"),
        ("548489", "2026-11-08", "09:15", "Cincinnati Bengals vs Atlanta Falcons", "Bernab\u00e9u, Madrid, Spain", "2026 NFL Madrid Game"),
        ("548500", "2026-11-08", "19:30", "Tampa Bay Buccaneers at Chicago Bears", "Soldier Field, Chicago, IL", "Sunday Night Football"),
        ("548541", "2026-11-09", "19:00", "Buffalo Bills at Minnesota Vikings", "U.S. Bank Stadium, Minneapolis, MN", "Monday Night Football"),
        ("548562", "2026-11-12", "19:30", "Washington Commanders at New York Giants", "MetLife Stadium, East Rutherford, NJ", "Thursday Night Football"),
        ("548490", "2026-11-15", "09:15", "New England Patriots vs Detroit Lions", "Allianz Arena, Munich, Germany", "2026 NFL Munich Game"),
        ("548501", "2026-11-15", "19:30", "Pittsburgh Steelers at Cincinnati Bengals", "Paycor Stadium, Cincinnati, OH", "Sunday Night Football"),
        ("548542", "2026-11-16", "19:00", "Los Angeles Chargers at Baltimore Ravens", "M&T Bank Stadium, Baltimore, MD", "Monday Night Football"),
        ("548564", "2026-11-19", "19:30", "Indianapolis Colts at Houston Texans", "NRG Stadium, Houston, TX", "Thursday Night Football"),
        ("548543", "2026-11-23", "19:00", "Cincinnati Bengals at Washington Commanders", "Northwest Stadium, Landover, MD", "Monday Night Football"),
        ("548511", "2026-11-25", "19:30", "Green Bay Packers at Los Angeles Rams", "SoFi Stadium, Inglewood, CA", "Thanksgiving Wednesday"),
        ("548512", "2026-11-26", "12:30", "Chicago Bears at Detroit Lions", "Ford Field, Detroit, MI, USA", "NFL Thanksgiving Day Tripleheader"),
        ("548513", "2026-11-26", "16:15", "Philadelphia Eagles at Dallas Cowboys", "AT&T Stadium, Arlington, TX", "NFL Thanksgiving Day Tripleheader"),
        ("548514", "2026-11-26", "20:00", "Kansas City Chiefs at Buffalo Bills", "New Highmark Stadium, Orchard Park, NY", "NFL Thanksgiving Day Tripleheader"),
        ("548515", "2026-11-27", "14:30", "Denver Broncos at Pittsburgh Steelers", "Acrisure Stadium, Pittsburgh, PA", "NFL Black Friday Game"),
        ("548502", "2026-11-29", "19:30", "New England Patriots at Los Angeles Chargers", "SoFi Stadium, Inglewood, CA", "Sunday Night Football"),
        ("548544", "2026-11-30", "19:00", "Carolina Panthers at Tampa Bay Buccaneers", "Raymond James Stadium, Tampa, FL", "Monday Night Football"),
        ("548566", "2026-12-03", "19:30", "Kansas City Chiefs at Los Angeles Rams", "SoFi Stadium, Inglewood, CA", "Thursday Night Football"),
        ("548503", "2026-12-06", "19:30", "Houston Texans at Pittsburgh Steelers", "Acrisure Stadium, Pittsburgh, PA", "Sunday Night Football"),
        ("548545", "2026-12-07", "19:00", "Dallas Cowboys at Seattle Seahawks", "Lumen Field, Seattle, WA", "Monday Night Football"),
        ("548567", "2026-12-10", "19:30", "Minnesota Vikings at New England Patriots", "Gillette Stadium, Foxborough, MA", "Thursday Night Football"),
        ("548505", "2026-12-13", "19:30", "Buffalo Bills at Green Bay Packers", "Lambeau Field, Green Bay, WI", "Sunday Night Football"),
        ("548546", "2026-12-14", "19:00", "Pittsburgh Steelers at Jacksonville Jaguars", "EverBank Stadium, Jacksonville, FL", "Monday Night Football"),
        ("548517", "2026-12-19", "16:30", "Seattle Seahawks at Philadelphia Eagles", "Lincoln Financial Field, Philadelphia, PA", "Week 15 Saturday NFL Doubleheader"),
        ("548518", "2026-12-19", "20:00", "Chicago Bears at Buffalo Bills", "New Highmark Stadium, Orchard Park, NY", "Week 15 Saturday NFL Doubleheader"),
        ("548506", "2026-12-20", "19:30", "Detroit Lions at Minnesota Vikings", "U.S. Bank Stadium, Minneapolis, MN", "Sunday Night Football"),
        ("548548", "2026-12-21", "19:00", "New England Patriots at Kansas City Chiefs", "GEHA Field at Arrowhead Stadium, Kansas City, MO", "Monday Night Football"),
        ("548569", "2026-12-24", "19:30", "Houston Texans at Philadelphia Eagles", "Lincoln Financial Field, Philadelphia, PA", "Thursday Night Football"),
        ("548528", "2026-12-25", "12:30", "Green Bay Packers at Chicago Bears", "Soldier Field, Chicago, IL", "Christmas Day NFL Tripleheader"),
        ("548531", "2026-12-25", "16:15", "Buffalo Bills at Denver Broncos", "Empower Field at Mile High, Denver, CO", "Christmas Day NFL Tripleheader"),
        ("548534", "2026-12-25", "20:00", "Los Angeles Rams at Seattle Seahawks", "Lumen Field, Seattle, WA", "Christmas Day NFL Tripleheader"),
        ("548519", "2026-12-26", "16:00", "Week 16 Saturday Doubleheader TBA", "", "Week 16 Saturday NFL Doubleheader"),
        ("548520", "2026-12-26", "20:00", "Week 16 Saturday Doubleheader TBA", "", "Week 16 Saturday NFL Doubleheader"),
        ("548507", "2026-12-27", "19:30", "Jacksonville Jaguars at Dallas Cowboys", "AT&T Stadium, Arlington, TX", "Sunday Night Football"),
        ("548550", "2026-12-28", "19:00", "New York Giants at Detroit Lions", "Ford Field, Detroit, Michigan", "Monday Night Football"),
        ("548570", "2026-12-31", "19:30", "Baltimore Ravens at Cincinnati Bengals", "Paycor Stadium, Cincinnati, OH", "Thursday Night Football"),
        ("548521", "2027-01-02", "16:00", "Week 17 Saturday Doubleheader TBA", "", "Week 17 Saturday NFL Doubleheader"),
        ("548522", "2027-01-02", "20:00", "Week 17 Saturday NFL Doubleheader TBA", "", "Week 17 Saturday NFL Doubleheader"),
        ("548552", "2027-01-04", "19:00", "Houston Texans at Green Bay Packers", "Lambeau Field, Green Bay, WI", "Monday Night Football"),
        ("548523", "2027-01-09", "12:30", "Week 18 Saturday Tripleheader TBA", "", "Week 18 Saturday NFL Tripleheader"),
        ("548524", "2027-01-09", "16:15", "Week 18 Saturday Tripleheader TBA", "", "Week 18 Saturday NFL Tripleheader"),
        ("548526", "2027-01-09", "20:00", "Week 18 Saturday Tripleheader TBA", "", "Week 18 Saturday NFL Tripleheader"),
        ("548510", "2027-01-10", "19:30", "Week 18 Sunday Night Football - Teams TBA", "", "Sunday Night Football"),
    ]
    rows = []
    for event_id, date, et, title, venue, slot in raw:
        tba = "TBA" in title
        rows.append(game(
            id=f"wwo-nfl-{event_id}",
            date=date,
            start_pt=et_to_pt(et),
            title=f"Westwood One: {title}",
            league="NFL",
            network="Westwood One",
            venue=venue,
            status="tba" if tba else "scheduled",
            stations=WWO_NFL_STATIONS[:],
            confidence="indicated",
            sources=[
                src(f"Westwood One event {event_id}", wwo_event(event_id)),
                src("Westwood One NFL schedule", WWO_NFL_URL),
                src("Station finder, NFL tab: San Francisco KNBR-AM, KNBR-FM, KTCT-AM", WWO_FINDER),
            ],
            notes=(
                f"{slot}. Listed start {et_to_pt(et)} PT, converted from {et} ET printed on the "
                "schedule grid. Not a confirmed kickoff. Clearance on 680 / 104.5 / 1050 is the "
                "NFL affiliate row plus the station-finder preemption caveat, not a per-game "
                "confirmation."
            ),
            flag_ids=["WWO_PREEMPTION", "WWO_LISTED_START", "FINDER_2025_LABEL", "WWO_VENUE_STRINGS"],
        ))
    return rows


# --- Westwood One college football -------------------------------------------
def wwo_ncaaf_rows() -> list[dict]:
    raw = [
        ("557137", "2026-10-03", None, "Notre Dame at North Carolina", "Kenan Stadium, Chapel Hill, NC"),
        ("557139", "2026-10-10", None, "Indiana at Nebraska", "Memorial Stadium, Lincoln, NE"),
        ("557140", "2026-10-17", None, "Penn State at Michigan", "Michigan Stadium, Ann Arbor, MI"),
        ("557141", "2026-10-24", None, "Ole Miss at Texas", "Darrell K Royal–Texas Memorial Stadium, Austin, TX"),
        ("557129", "2026-10-31", "15:00", "Florida at Georgia", "Mercedes-Benz Stadium, Atlanta, GA"),
        ("557143", "2026-11-07", None, "Oregon at Ohio State", "Ohio Stadium, Columbus, OH"),
        ("557144", "2026-11-14", None, "Michigan at Oregon", "Autzen Stadium, Eugene, OR"),
        ("557145", "2026-11-21", None, "LSU at Tennessee", "Neyland Stadium, Knoxville, TN"),
        ("557131", "2026-11-28", "11:30", "Michigan at Ohio State", "Ohio Stadium, Columbus, OH"),
        ("557146", "2026-12-05", "15:30", "SEC Championship Game", "Mercedes-Benz Stadium, Atlanta, GA"),
        ("557132", "2026-12-12", "14:00", "Army vs Navy", "MetLife Stadium, East Rutherford, NJ"),
    ]
    more = WWO_NCAAF_MORE
    rows = []
    for event_id, date, et, title, venue in raw:
        rows.append(game(
            id=f"wwo-ncaaf-{event_id}",
            date=date,
            start_pt=et_to_pt(et) if et else None,
            title=f"Westwood One: {title}",
            league="NCAAF",
            network="Westwood One",
            venue=venue,
            status="scheduled" if et else "tba",
            stations=WWO_NCAAF_STATIONS[:],
            confidence="indicated",
            sources=[
                src(f"Westwood One event {event_id}", wwo_event(event_id)),
                src("Westwood One NCAA football schedule", WWO_NCAAF_URL),
                src("More endpoint, offset 10 — carries the eleventh row, Army vs Navy", more),
                src("More endpoint, offset 20 — returns \"No more events\", so the grid is exhausted", WWO_NCAAF_MORE_END),
                src("Station finder, NCAA Football tab: San Francisco KNBR-AM, KNBR-FM, KTCT-AM", WWO_FINDER),
            ],
            notes=(
                ("Air time TBD on the Westwood One grid." if not et else
                 f"Listed start {et_to_pt(et)} PT, converted from {et} ET on the grid.")
                + " The NCAA Football tab of the station finder was read on 2026-09-27 and lists the "
                "same San Francisco affiliates as the NFL tab. The KNBR 1050 weekly grid independently "
                "shows a \"WW1 CFB\" college football block, which is what this row would occupy."
            ),
            flag_ids=["WWO_PREEMPTION", "WWO_LISTED_START", "FINDER_2025_LABEL", "NCAAF_VENUE_REREAD"],
        ))
    return rows


# --- Westwood One U.S. Soccer -------------------------------------------------
def wwo_soccer_rows() -> list[dict]:
    raw = [
        ("570239", "2026-09-29", "19:45", "USMNT vs. Chile", "Energizer Park, St. Louis, MO",
         "Announcers: Callum Williams and Cobi Jones."),
        ("570240", "2026-10-03", "22:00", "USMNT vs. Mexico", "State Farm Stadium, Glendale, AZ",
         "Listed as \"TNT Sports Broadcast - Audio Only Simulcast\", not an original Westwood One call."),
        ("570241", "2026-10-06", "19:45", "USMNT vs. Canada", "Allianz Field, Saint Paul, MN",
         "Announcers: Callum Williams and Jamie Watson."),
        ("570247", "2026-10-10", "14:30", "USWNT vs. Spain", "Audi Field, Washington, DC",
         "Listed as \"TNT Sports Broadcast - Audio Only Simulcast\", not an original Westwood One call."),
        ("570250", "2026-10-13", "18:45", "USWNT vs. Spain", "Subaru Park, Chester, PA",
         "Announcers: Mark Rogondino and Saskia Webber."),
    ]
    rows = []
    for event_id, date, et, title, venue, extra in raw:
        rows.append(game(
            id=f"wwo-soccer-{event_id}",
            date=date,
            start_pt=et_to_pt(et),
            title=f"Westwood One: {title}",
            league="SOCCER",
            network="Westwood One",
            venue=venue,
            stations=WWO_SOCCER_STATIONS[:],
            confidence="indicated",
            sources=[
                src(f"Westwood One event {event_id}", wwo_event(event_id)),
                src("Westwood One U.S. Soccer schedule", WWO_SOCCER_URL),
                src("Station finder, Soccer tab: San Francisco, CA — KTCT-AM", WWO_FINDER),
            ],
            notes=(
                f"Listed start {et_to_pt(et)} PT, converted from the {et} ET printed on the U.S. Soccer "
                f"page. {extra} The Soccer tab of the station finder lists exactly one Bay Area "
                "affiliate, KTCT-AM, so 1050 is the only station shown."
            ),
            flag_ids=["SOCCER_FINDER_ONLY", "WWO_PREEMPTION", "WWO_LISTED_START", "FINDER_2025_LABEL"],
        ))
    return rows


# --- MLB postseason on ESPN Radio --------------------------------------------
def mlb_postseason_rows() -> list[dict]:
    """One row per scheduled postseason date from the MLB Stats API postseason endpoint,
    fetched 2026-09-27. Every game on that endpoint carries startTimeTBD true, so no row
    gets a clock time. MLB's own release puts every game on ESPN Radio; KTCT 1050 is a
    full-time ESPN Radio affiliate. That is a network row, not a per-game clearance.
    """
    # date, round label for the title, list of exact Stats API descriptions, if-necessary count
    raw = [
        ("2026-09-29", "Wild Card Series, Game 1",
         ["AL Wild Card 'A' Game 1", "AL Wild Card 'B' Game 1", "NL Wild Card 'A' Game 1", "NL Wild Card 'B' Game 1"], 0),
        ("2026-09-30", "Wild Card Series, Game 2",
         ["AL Wild Card 'A' Game 2", "AL Wild Card 'B' Game 2", "NL Wild Card 'A' Game 2", "NL Wild Card 'B' Game 2"], 0),
        ("2026-10-01", "Wild Card Series, Game 3",
         ["AL Wild Card 'A' Game 3", "AL Wild Card 'B' Game 3", "NL Wild Card 'A' Game 3", "NL Wild Card 'B' Game 3"], 4),
        ("2026-10-03", "Division Series, Game 1",
         ["ALDS 'A' Game 1", "ALDS 'B' Game 1", "NLDS 'A' Game 1", "NLDS 'B' Game 1"], 0),
        ("2026-10-04", "NL Division Series, Game 2",
         ["NLDS 'A' Game 2", "NLDS 'B' Game 2"], 0),
        ("2026-10-05", "AL Division Series, Game 2",
         ["ALDS 'A' Game 2", "ALDS 'B' Game 2"], 0),
        ("2026-10-06", "NL Division Series, Game 3",
         ["NLDS 'A' Game 3", "NLDS 'B' Game 3"], 0),
        ("2026-10-07", "AL Division Series Game 3, NL Division Series Game 4",
         ["ALDS 'A' Game 3", "ALDS 'B' Game 3", "NLDS 'A' Game 4", "NLDS 'B' Game 4"], 2),
        ("2026-10-08", "AL Division Series, Game 4",
         ["ALDS 'A' Game 4", "ALDS 'B' Game 4"], 2),
        ("2026-10-09", "NL Division Series, Game 5",
         ["NLDS 'A' Game 5", "NLDS 'B' Game 5"], 2),
        ("2026-10-10", "AL Division Series, Game 5",
         ["ALDS 'A' Game 5", "ALDS 'B' Game 5"], 2),
        ("2026-10-11", "NLCS Game 1", ["NLCS Game 1"], 0),
        ("2026-10-12", "ALCS Game 1, NLCS Game 2", ["ALCS Game 1", "NLCS Game 2"], 0),
        ("2026-10-13", "ALCS Game 2", ["ALCS Game 2"], 0),
        ("2026-10-14", "NLCS Game 3", ["NLCS Game 3"], 0),
        ("2026-10-15", "ALCS Game 3, NLCS Game 4", ["ALCS Game 3", "NLCS Game 4"], 0),
        ("2026-10-16", "ALCS Game 4, NLCS Game 5", ["ALCS Game 4", "NLCS Game 5"], 1),
        ("2026-10-17", "ALCS Game 5", ["ALCS Game 5"], 1),
        ("2026-10-18", "NLCS Game 6", ["NLCS Game 6"], 1),
        ("2026-10-19", "ALCS Game 6, NLCS Game 7", ["ALCS Game 6", "NLCS Game 7"], 2),
        ("2026-10-20", "ALCS Game 7", ["ALCS Game 7"], 1),
        ("2026-10-23", "World Series Game 1", ["World Series Game 1"], 0),
        ("2026-10-24", "World Series Game 2", ["World Series Game 2"], 0),
        ("2026-10-26", "World Series Game 3", ["World Series Game 3"], 0),
        ("2026-10-27", "World Series Game 4", ["World Series Game 4"], 0),
        ("2026-10-28", "World Series Game 5", ["World Series Game 5"], 1),
        ("2026-10-30", "World Series Game 6", ["World Series Game 6"], 1),
        ("2026-10-31", "World Series Game 7", ["World Series Game 7"], 1),
    ]
    rows = []
    for date, label, descriptions, if_nec in raw:
        n = len(descriptions)
        all_conditional = if_nec == n
        suffix = " (if necessary)" if all_conditional else (f" — {if_nec} of them if necessary" if if_nec else "")
        rows.append(game(
            id=f"mlb-post-{date}",
            date=date,
            start_pt=None,
            title=f"MLB Postseason on ESPN Radio — {label}{suffix}",
            league="MLB",
            network="ESPN Radio",
            venue="",
            status="if-necessary" if all_conditional else "tba",
            conditional=all_conditional,
            game_count=n,
            conditional_game_count=if_nec,
            stations=["1050"],
            confidence="indicated",
            duration_key="MLB-POST",
            duration_est_min=DUR["MLB-POST"],
            sources=[
                src("MLB: \"ESPN Radio will provide live national coverage of all 2026 MLB Postseason games\"", MLB_POST_PRESS),
                src(f"MLB Stats API postseason endpoint, {date}: {n} game(s), startTimeTBD true", MLB_POST_API),
                src("KNBR 1050 weekly grid — the ESPN Radio network schedule", KNBR_1050_SHOWS),
                src("KTCT station record: network ESPN Radio", KTCT_WIKI),
            ],
            notes=(
                f"Stats API descriptions for this date: {'; '.join(descriptions)}. "
                "First pitch was still TBD on every postseason game when the endpoint was read on "
                "2026-09-27, so no clock time is shown. ESPN Radio runs one national feed, so on a "
                f"{n}-game day at most one of these can be on 1050 at a time"
                + (", and Stanford football, the Earthquakes or Westwood One college football can take the station instead. "
                   if date <= "2026-11-07" else ". ")
                + "Neither the Giants nor the Athletics are in this field."
            ),
            flag_ids=["MLB_POSTSEASON_ESPN", "TALK_NOT_GAMES", "SPANISH_EXCLUDED", "DURATION_ESTIMATE"],
        ))
    return rows


# --- local clubs and schools --------------------------------------------------
def local_rows() -> list[dict]:
    rows = []

    rows.append(game(
        id="giants-2026-09-27",
        date="2026-09-27",
        start_pt="12:05",
        title="Los Angeles Dodgers at San Francisco Giants",
        league="MLB",
        venue="Oracle Park",
        status="scheduled",
        stations=["680", "104.5"],
        confidence="official",
        sources=[
            src("MLB Stats API gamePk 823164, first pitch 2026-09-27T19:05:00Z", mlb_game(823164)),
            src("Giants English radio: KNBR 680 AM & 104.5 FM", GIANTS_RADIO),
        ],
        notes=(
            "Season finale. The Stats API returned no Giants game after this one when queried on "
            "2026-09-27 through 2026-11-15, and the club is not in the postseason field. "
            "19:05 UTC is 12:05 PM PDT. English call only."
        ),
        flag_ids=["NO_LOCAL_MLB_AFTER_0927", "SPANISH_EXCLUDED", "DURATION_ESTIMATE"],
    ))
    rows.append(game(
        id="athletics-2026-09-27",
        date="2026-09-27",
        start_pt="12:05",
        title="Houston Astros at Athletics",
        league="MLB",
        venue="Sutter Health Park, Sacramento",
        status="scheduled",
        stations=["960"],
        confidence="official",
        sources=[
            src("MLB Stats API gamePk 824948, first pitch 2026-09-27T19:05:00Z", mlb_game(824948)),
            src("A's Radio Network: 960 AM KNEW, Bay Area", ATH_RADIO),
        ],
        notes=(
            "Season finale. No later Athletics game was returned by the Stats API and the club is not "
            "in the postseason field. ScheduleFreeTime does not mark Athletics games as Bay Area "
            "radio; this row follows the club affiliates page."
        ),
        flag_ids=["NO_LOCAL_MLB_AFTER_0927", "ATHLETICS_SACRAMENTO", "SFT_RADIO_DIFF", "DURATION_ESTIMATE"],
    ))

    niners = [
        ("2026-09-27", "13:05", "Arizona Cardinals at San Francisco 49ers", "Levi's Stadium", ["810", "107.7"], "Week 3", "FOX", ["NINERS_BOILERPLATE"]),
        ("2026-10-04", "13:25", "Denver Broncos at San Francisco 49ers", "Levi's Stadium", ["107.7", "104.5", "680"], "Week 4", "CBS", ["NINERS_BOILERPLATE"]),
        ("2026-10-11", "13:25", "San Francisco 49ers at Seattle Seahawks", "Lumen Field", ["107.7", "104.5", "680"], "Week 5", "FOX", []),
        ("2026-10-19", "17:15", "Washington Commanders at San Francisco 49ers", "Levi's Stadium", ["107.7", "104.5", "680"], "Week 6", "ESPN & ABC", []),
        ("2026-10-25", "10:00", "San Francisco 49ers at Atlanta Falcons", "Mercedes-Benz Stadium", ["107.7", "104.5", "680"], "Week 7", "FOX", []),
        ("2026-11-08", "13:05", "Las Vegas Raiders at San Francisco 49ers", "Levi's Stadium", ["107.7", "104.5", "680"], "Week 9", "CBS", []),
        ("2026-11-15", "13:25", "San Francisco 49ers at Dallas Cowboys", "AT&T Stadium", ["107.7", "104.5", "680"], "Week 10", "FOX", []),
        ("2026-11-22", "17:20", "Minnesota Vikings vs San Francisco 49ers", "Estadio Banorte (49ers.com); Estadio Azteca (Westwood One)", ["107.7", "104.5", "680"], "Week 11", "NBC", ["MEXICO_VENUE_NAMES"]),
        ("2026-11-29", "13:25", "Seattle Seahawks at San Francisco 49ers", "Levi's Stadium", ["107.7", "104.5", "680"], "Week 12", "FOX", []),
        ("2026-12-06", "10:00", "San Francisco 49ers at New York Giants", "MetLife Stadium", ["107.7", "104.5", "680"], "Week 13", "FOX", []),
        ("2026-12-13", "13:25", "Los Angeles Rams at San Francisco 49ers", "Levi's Stadium", ["107.7", "104.5", "680"], "Week 14", "FOX", []),
        ("2026-12-17", "17:15", "San Francisco 49ers at Los Angeles Chargers", "SoFi Stadium", ["107.7", "104.5", "680"], "Week 15", "Prime Video", []),
        ("2026-12-27", "13:25", "San Francisco 49ers at Kansas City Chiefs", "Arrowhead Stadium", ["107.7", "104.5", "680"], "Week 16", "CBS", []),
        ("2027-01-03", "17:20", "Philadelphia Eagles at San Francisco 49ers", "Levi's Stadium", ["107.7", "104.5", "680"], "Week 17", "NBC", []),
    ]
    wwo_same = {
        "2026-10-19": ("548538", "Westwood One event 548538 prints 7:00 PM ET (4:00 PM PT) for this game. "
                                 "Club kickoff is 5:15 PM PT. The national listing is merged into this row, not duplicated."),
        "2026-11-22": ("548491", "Westwood One event 548491 prints 7:30 PM ET (4:30 PM PT) and Estadio Azteca. "
                                 "Club kickoff is 5:20 PM PT at Estadio Banorte. Merged, not duplicated."),
        "2026-12-17": ("548568", "Westwood One event 548568 prints 7:30 PM ET (4:30 PM PT). Club kickoff is "
                                 "5:15 PM PT. Merged, not duplicated."),
        "2027-01-03": ("548509", "Westwood One event 548509 prints 7:30 PM ET (4:30 PM PT). Club kickoff is "
                                 "5:20 PM PT. Merged, not duplicated."),
    }
    week3 = "https://www.49ers.com/news/ways-to-watch-and-listen-cardinals-vs-49ers-week-3-x8427"
    for date, start, title, venue, stations, week, tv, extra_flags in niners:
        sources = [src(f"49ers.com schedule, {week}, radio line as printed", NINERS)]
        if date == "2026-09-27":
            sources.append(src("Week 3 ways to listen, 1:05 PM PT, KSFO 810 / KSAN 107.7", week3))
        notes = f"{week}. TV on the schedule page: {tv}. Times are the PT clock printed by 49ers.com."
        network = ""
        if date in wwo_same:
            event_id, text = wwo_same[date]
            notes += " " + text
            network = "Westwood One also carries it nationally"
            sources.append(src(f"Westwood One event {event_id} (same game, national feed)", wwo_event(event_id)))
        rows.append(game(
            id=f"niners-{date}",
            date=date,
            start_pt=start,
            title=title,
            league="NFL",
            network=network,
            venue=venue,
            stations=stations,
            confidence="official",
            sources=sources,
            notes=notes,
            flag_ids=extra_flags + ["DURATION_ESTIMATE"],
        ))
    rows.append(game(
        id="niners-week-18",
        date=None,
        start_pt=None,
        title="San Francisco 49ers at Arizona Cardinals (Week 18)",
        league="NFL",
        venue="State Farm Stadium",
        status="tba",
        stations=["107.7", "104.5", "680"],
        confidence="official",
        sources=[src("49ers.com schedule, Week 18, date TBD, radio line printed", NINERS)],
        notes="Date and kickoff are TBD on the club page. Not placed on a guessed day.",
        flag_ids=["WEEK18_UNPLACED"],
    ))

    # Stanford: dates and kickoffs from ESPN because the school site still serves 2025.
    stanford = [
        ("2026-10-03", "09:00", "Stanford at Wake Forest", "Winston-Salem",
         "ESPN prints Sat Oct 3, 12:00 PM ET, which is 9:00 AM PT."),
        ("2026-10-10", "12:30", "Stanford at Notre Dame", "Notre Dame Stadium",
         "ESPN prints Sat Oct 10, 3:30 PM ET on NBC, which is 12:30 PM PT."),
        ("2026-10-17", "16:30", "Elon at Stanford", "Stanford Stadium",
         "ESPN prints Sat Oct 17, 7:30 PM ET, which is 4:30 PM PT."),
        ("2026-10-23", "19:30", "NC State at Stanford", "Stanford Stadium",
         "ESPN prints Fri Oct 23, 10:30 PM ET, which is 7:30 PM PT. This is the Friday night game."),
        ("2026-10-31", None, "Stanford at Louisville", "Louisville",
         "ESPN prints Sat Oct 31 with kickoff TBD."),
        ("2026-11-14", None, "Stanford at Virginia Tech", "Blacksburg",
         "ESPN prints Sat Nov 14 with kickoff TBD."),
        ("2026-11-28", None, "SMU at Stanford", "Stanford Stadium",
         "ESPN prints Sat Nov 28 with kickoff TBD."),
    ]
    for date, start, title, venue, notes in stanford:
        rows.append(game(
            id=f"stanford-{date}",
            date=date,
            start_pt=start,
            title=title,
            league="NCAAF",
            venue=venue,
            status="scheduled" if start else "tba",
            stations=["1050"],
            confidence="official",
            sources=[
                src("ESPN 2026 Stanford schedule (dates and kickoffs, Eastern)", STANFORD_ESPN),
                src("Stanford radio release: the broadcast is on KNBR/KTCT 1050 AM", STANFORD_RADIO),
                src("Stanford football on The Sports Leader (KNBR/KTCT)", STANFORD_TSL),
                src("KNBR 1050 weekly grid: Stanford pre-game then STANFORD FOOTBALL block", KNBR_1050_SHOWS),
            ],
            notes=(
                notes + " \"KNBR/KTCT 1050 AM\" is the 1050 station, not 680. The school's own "
                "schedule page was serving 2025 rows when checked, so the date and time come from ESPN."
            ),
            flag_ids=["GOSTANFORD_2025", "DURATION_ESTIMATE"],
        ))

    rows.append(game(
        id="big-game-2026-11-21",
        date="2026-11-21",
        start_pt=None,
        title="Stanford at California (129th Big Game)",
        league="NCAAF",
        venue="California Memorial Stadium, Berkeley",
        status="tba",
        stations=["1050", "680", "104.5"],
        confidence="review",
        sources=[
            src("Cal schedule: Radio \"KNBR 104.5 FM / 680 AM\" on the Nov 21 row", CAL),
            src("Stanford radio release: KNBR/KTCT 1050 AM for the football season", STANFORD_RADIO),
            src("ESPN Stanford schedule: Nov 21 at California, kickoff TBD", STANFORD_ESPN),
        ],
        notes=(
            "One game, two station claims, both shown. Cal's Radio column prints KNBR 104.5 FM / 680 AM "
            "for this row and KSFO 810 AM for every other 2026 row, so 810 is not assumed here. "
            "Kickoff TBD on both schedules."
        ),
        flag_ids=["BIG_GAME_STATIONS", "DURATION_ESTIMATE"],
    ))

    # Cal: full Radio column re-read from the official schedule on 2026-09-27.
    cal = [
        ("2026-10-03", "12:30", "California at UNLV", "Allegiant Stadium, Las Vegas",
         "Cal's schedule prints Oct 3, 12:30 PM PT at UNLV on CBSSN — the only 2026 row with a kickoff. Radio column: KSFO 810."),
        ("2026-10-10", None, "Virginia Tech at California", "California Memorial Stadium",
         "Radio column: KSFO 810. Kickoff not yet set on the schedule or on ESPN."),
        ("2026-10-17", None, "Wake Forest at California", "California Memorial Stadium",
         "Radio column: KSFO 810. Kickoff not yet set. This row was missing from the previous snapshot and is now read directly from the Radio column."),
        ("2026-10-24", None, "California at SMU", "Gerald J. Ford Stadium, Dallas",
         "Radio column: KSFO 810. Kickoff not yet set."),
        ("2026-10-31", None, "California at NC State", "Carter-Finley Stadium, Raleigh",
         "Radio column: KSFO 810. Kickoff not yet set."),
        ("2026-11-14", None, "California at Virginia", "Scott Stadium, Charlottesville",
         "Radio column: KSFO 810. Kickoff not yet set. Cal's bye week is Nov 7."),
        ("2026-11-28", None, "Pittsburgh at California", "California Memorial Stadium",
         "Radio column: KSFO 810. Kickoff not yet set. Season finale."),
    ]
    for date, start, title, venue, notes in cal:
        rows.append(game(
            id=f"cal-{date}",
            date=date,
            start_pt=start,
            title=title,
            league="NCAAF",
            venue=venue,
            status="scheduled" if start else "tba",
            stations=["810"],
            confidence="official",
            sources=[
                src("Cal football schedule, Radio column", CAL),
                src("ESPN Cal schedule, date and time cross-check", CAL_ESPN),
            ],
            notes=notes,
            flag_ids=["DURATION_ESTIMATE"],
        ))

    quakes = [
        ("2026-10-10", "18:30", "San Jose Earthquakes at Colorado Rapids", "", "Away", "official", []),
        ("2026-10-14", "18:30", "San Jose Earthquakes at Real Salt Lake", "", "Away", "official", []),
        ("2026-10-17", "19:30", "Nashville SC at San Jose Earthquakes", "PayPal Park", "Home", "official", []),
        ("2026-10-24", "17:30", "San Jose Earthquakes at FC Dallas", "", "Away", "official", []),
        ("2026-10-28", "19:30", "Colorado Rapids at San Jose Earthquakes", "PayPal Park", "Home", "official", []),
        ("2026-10-31", "14:00", "Real Salt Lake at San Jose Earthquakes", "PayPal Park", "Home", "review", ["QUAKES_OCT31_TIME"]),
        ("2026-11-07", "16:00", "San Jose Earthquakes at Minnesota United FC", "", "Away", "official", []),
    ]
    for date, start, title, venue, ha, confidence, extra in quakes:
        sources = [src(f"Club radio release 2026-02-16, {ha} match, KSFO 810 English / KZSF 1370 Spanish", QUAKES)]
        notes = (
            "English station in the club's per-game table is 810. Spanish 1370 is not one of the six "
            "stations. The release says all times and dates are subject to change."
        )
        if date == "2026-10-31":
            sources.append(src("Club printable 2026 schedule PDF: same match printed TBD", QUAKES_PDF))
            notes += (
                " The February release prints 2:00 PM for this match and the club's printable PDF "
                "prints TBD. 2:00 PM is used because it is the only stated time, and the row is "
                "marked review."
            )
        if date == "2026-11-07":
            notes += " Decision Day. The release's table ends here; no playoff radio plan is published."
        rows.append(game(
            id=f"quakes-{date}",
            date=date,
            start_pt=start,
            title=title,
            league="MLS",
            venue=venue,
            stations=["810"],
            confidence=confidence,
            sources=sources,
            notes=notes,
            flag_ids=extra + ["QUAKES_SUBJECT_TO_CHANGE", "QUAKES_ALT_STATION", "SPANISH_EXCLUDED", "DURATION_ESTIMATE"],
        ))

    rows.append(game(
        id="super-bowl-lxi",
        date="2027-02-14",
        start_pt=None,
        title="Super Bowl LXI — teams not announced on the Westwood One schedule page",
        league="NFL",
        network="Westwood One",
        venue="SoFi Stadium, Inglewood",
        status="tba",
        stations=WWO_NFL_STATIONS[:],
        confidence="indicated",
        sources=[
            src("Cumulus release 2026-09-09: Super Bowl LXI, February 14, 2027, SoFi Stadium", PRESS),
            src("League important dates: \u201cFebruary 14 - Super Bowl LXI at SoFi Stadium (Inglewood, California)\u201d", NFL_IMPORTANT_DATES),
            src("Station finder, NFL tab: KNBR-AM, KNBR-FM, KTCT-AM", WWO_FINDER),
        ],
        notes=(
            "Date and stadium are from the rights-holder release, and the league's important-dates "
            "announcement independently names February 14 at SoFi Stadium. Kickoff is not published "
            "and the teams are not known, so this row carries no clock time. Unlike the earlier "
            "rounds, this is a single officially named day for a single game."
        ),
        flag_ids=["NFL_POSTSEASON_WINDOWS", "WWO_PREEMPTION", "WWO_LISTED_START"],
    ))
    return rows


# --- NFL postseason round windows ---------------------------------------------
def nfl_postseason_rows() -> list[dict]:
    """One row per day of an officially named playoff window.

    The league's important-dates announcement names the round windows, and the
    Cumulus release puts every postseason game on Westwood One, whose San
    Francisco affiliates are already established for the 63 regular-season rows.
    Nothing publishes which game falls on which day, how many games a day
    carries, the matchups or the kickoffs, so these rows assert a date and a
    network and nothing else: no game_count, no clock time, no venue.

    Every day of a multi-day window carries a row. Leaving January 17, 18, 23 and
    24 blank would read as "no live sports radio", which is the one wrong answer
    this page must not give on the busiest radio weekends of the year.
    """
    windows = [
        ("2027-01-16", "wild-card-1", "NFL Wild Card Weekend on Westwood One — day 1 of the official January 16–18 window"),
        ("2027-01-17", "wild-card-2", "NFL Wild Card Weekend on Westwood One — day 2 of the official January 16–18 window"),
        ("2027-01-18", "wild-card-3", "NFL Wild Card Weekend on Westwood One — day 3 of the official January 16–18 window"),
        ("2027-01-23", "divisional-1", "NFL Divisional Playoffs on Westwood One — day 1 of the official January 23–24 window"),
        ("2027-01-24", "divisional-2", "NFL Divisional Playoffs on Westwood One — day 2 of the official January 23–24 window"),
        ("2027-01-31", "championships", "AFC and NFC Championship Games on Westwood One — both games officially dated January 31"),
    ]
    rows = []
    for date, slug, title in windows:
        if slug == "championships":
            dated = (
                "The league names January 31 as the single day for both the AFC and NFC "
                "Championship Games, so this is not a window day: both games are dated here."
            )
        else:
            dated = (
                "The league dates this round as a window, not game by game, so which games fall on "
                "this particular day is not published. The row asserts only that the round is being "
                "played across these dates and that Westwood One carries it."
            )
        rows.append(game(
            id=f"nfl-post-{slug}",
            date=date,
            start_pt=None,
            title=title,
            league="NFL",
            network="Westwood One",
            venue="",
            status="tba",
            stations=WWO_NFL_STATIONS[:],
            confidence="indicated",
            sources=[
                src("League important dates for 2026-2027: the round windows as announced", NFL_IMPORTANT_DATES),
                src("Cumulus release 2026-09-09: Westwood One carries every NFL postseason game", PRESS),
                src("Station finder, NFL tab: San Francisco KNBR-AM, KNBR-FM, KTCT-AM", WWO_FINDER),
                src("Westwood One NFL grid — ends at the Week 18 TBA windows, no playoff rows", WWO_NFL_URL),
            ],
            notes=(
                dated
                + " No game count, kickoff time, matchup or venue is asserted, because no official "
                "source publishes one for this date; nfl.com/schedules/2026/POST still redirected to "
                "the regular season when fetched on 2026-09-27. With no clock time this row "
                "contributes zero estimated minutes to the 10 AM–10 PM band maths, so it does not "
                "inflate the coverage figures. If the 49ers reach the postseason their games would "
                "also be expected on the club flagship, but no source publishes a postseason 49ers "
                "radio line, so 107.7 FM is not claimed here."
            ),
            flag_ids=["NFL_POSTSEASON_WINDOWS", "WWO_PREEMPTION", "FINDER_2025_LABEL", "DURATION_ESTIMATE"],
        ))
    return rows


# --- checks -------------------------------------------------------------------
def validate_flags() -> None:
    """Flags carry links a human is expected to click, so hold them to the row rules."""
    seen = set()
    for f in FLAGS:
        if f["id"] in seen:
            raise SystemExit(f"duplicate flag id {f['id']}")
        seen.add(f["id"])
        if f["severity"] not in ("limitation", "review", "note"):
            raise SystemExit(f"{f['id']} bad severity {f['severity']}")
        links = [f["url"]] + [x["url"] for x in f.get("sources", [])]
        for url in links:
            if not url.startswith("https://"):
                raise SystemExit(f"{f['id']} link is not https: {url}")
        if f.get("sources") and f["sources"][0]["url"] != f["url"]:
            raise SystemExit(f"{f['id']} primary url must be the first of its sources")


def validate(rows: list[dict]) -> None:
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate ids")

    flag_ids = {f["id"] for f in FLAGS}
    if len(flag_ids) != len(FLAGS):
        raise SystemExit("duplicate flag ids")
    used = {fid for r in rows for fid in r["flag_ids"]}
    unknown = used - flag_ids
    if unknown:
        raise SystemExit(f"rows reference undefined flags: {sorted(unknown)}")
    for f in FLAGS:
        if f["severity"] not in ("limitation", "review", "note"):
            raise SystemExit(f"bad severity on {f['id']}")
        if not f["url"].startswith("https://"):
            raise SystemExit(f"bad flag url on {f['id']}")

    def count(prefix: str) -> int:
        return sum(1 for r in rows if r["id"].startswith(prefix))

    expected = {
        "wwo-nfl-": 63,
        "wwo-ncaaf-": 11,
        "wwo-soccer-": 5,
        "nfl-post-": 6,
        "mlb-post-": 28,
        "stanford-": 7,
        "cal-": 7,
        "quakes-": 7,
        "giants-": 1,
        "athletics-": 1,
    }
    for prefix, n in expected.items():
        got = count(prefix)
        if got != n:
            raise SystemExit(f"expected {n} rows for {prefix}, got {got}")

    # 49ers national duplicates must stay merged into the club row.
    merged = WWO_MERGED_NFL_EVENTS
    present = {r["id"].split("-")[-1] for r in rows if r["id"].startswith("wwo-nfl-")}
    if present & merged:
        raise SystemExit(f"49ers WWO events duplicated: {present & merged}")

    niners = [r for r in rows if r["id"].startswith("niners-") and r["date"]]
    if len(niners) != 14:
        raise SystemExit("49ers dated count")
    for r in niners:
        if r["date"] < "2026-10-01" and "680" in r["stations"]:
            raise SystemExit(f"week 3 should not be on 680: {r['id']}")
        if r["date"] >= "2026-10-01" and "680" not in r["stations"]:
            raise SystemExit(f"week 4+ missing 680: {r['id']}")
        if "107.7" not in r["stations"]:
            raise SystemExit(f"every listed 49ers game is on 107.7: {r['id']}")

    for r in rows:
        rid = r["id"]
        if rid.startswith("giants-") and r["stations"] != ["680", "104.5"]:
            raise SystemExit("giants stations")
        if rid.startswith("athletics-") and r["stations"] != ["960"]:
            raise SystemExit("athletics station")
        if rid.startswith("quakes-") and r["stations"] != ["810"]:
            raise SystemExit("quakes station")
        if rid.startswith("stanford-") and r["stations"] != ["1050"]:
            raise SystemExit("stanford station")
        if rid.startswith("cal-") and r["stations"] != ["810"]:
            raise SystemExit("cal station")
        if rid.startswith("mlb-post-"):
            if r["stations"] != ["1050"]:
                raise SystemExit("mlb postseason station")
            if r["start_pt"] is not None:
                raise SystemExit("mlb postseason times were TBD; do not invent one")
            if r["confidence"] != "indicated":
                raise SystemExit("mlb postseason rows are network-level, not official")
        if rid.startswith("wwo-soccer-") and r["stations"] != ["1050"]:
            raise SystemExit("soccer station is the finder's only Bay Area row")
        if rid.startswith("nfl-post-"):
            if r["stations"] != WWO_NFL_STATIONS:
                raise SystemExit(
                    f"{rid}: a playoff window row is a Westwood One row; no source puts 107.7 on it"
                )
            if r["start_pt"] is not None:
                raise SystemExit(f"{rid}: no source publishes a playoff kickoff time; do not invent one")
            if r["venue"]:
                raise SystemExit(f"{rid}: no source publishes a playoff venue except the Super Bowl")
            if "game_count" in r:
                raise SystemExit(f"{rid}: no source publishes a per-day playoff game count")
            if r["confidence"] != "indicated":
                raise SystemExit(f"{rid}: a network guarantee plus an affiliate list is indicated, not official")
        if r["confidence"] == "official" and r["network"]:
            # a club/school row may note a national simulcast, but must not claim it as its network
            if r["network"] == "Westwood One":
                raise SystemExit(f"{rid} cannot be both official-local and a Westwood One row")

    if any(r["id"] == "big-game-2026-11-21" and "810" in r["stations"] for r in rows):
        raise SystemExit("do not put 810 on the Big Game without a quoted row")

    unplaced = [r for r in rows if r["date"] is None]
    if len(unplaced) != 1 or unplaced[0]["id"] != "niners-week-18":
        raise SystemExit("unexpected unplaced rows")

    # No station may be double-booked by two rows that both claim "official".
    for r in rows:
        for s in rows:
            if r["id"] >= s["id"] or not r["date"] or r["date"] != s["date"]:
                continue
            if r["confidence"] != "official" or s["confidence"] != "official":
                continue
            if not (set(r["stations"]) & set(s["stations"])):
                continue
            if not r["start_pt"] or not s["start_pt"]:
                continue
            a0 = int(r["start_pt"][:2]) * 60 + int(r["start_pt"][3:])
            b0 = int(s["start_pt"][:2]) * 60 + int(s["start_pt"][3:])
            if a0 < b0 + s["duration_est_min"] and b0 < a0 + r["duration_est_min"]:
                raise SystemExit(f"two official rows collide on a station: {r['id']} / {s['id']}")


def sort_key(r: dict):
    return (r["date"] or "9999-99-99", r["start_pt"] or "99:99", r["id"])


def line_markdown(rows: list[dict], flags: list[dict]) -> str:
    lines = [
        "# Line-by-line schedule list",
        "",
        f"Snapshot {SNAPSHOT}. Window {WINDOW_START} through {WINDOW_END}, America/Los_Angeles.",
        "Every row is generated from `scripts/build_feed.py`. Open the source link before treating a row as settled.",
        "",
        "| Date | PT listed start | Stations | Confidence | Status | Game | Sources |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in sorted(rows, key=sort_key):
        start = r["start_pt"] or "TBD"
        stations = ", ".join(r["stations"])
        links = ", ".join(f"[{s['label']}]({s['url']})" for s in r["sources"])
        date = r["date"] or "DATE TBD"
        title = r["title"].replace("|", "/")
        status = r["status"]
        lines.append(f"| {date} | {start} | {stations} | {r['confidence']} | {status} | {title} | {links} |")
    lines += ["", "## Flags", ""]
    for f in flags:
        lines.append(f"- **{f['id']}** ({f['severity']}): {f['title']} — {f['detail']} [link]({f['url']})")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    rows = (
        local_rows()
        + wwo_nfl_rows()
        + wwo_ncaaf_rows()
        + wwo_soccer_rows()
        + nfl_postseason_rows()
        + mlb_postseason_rows()
    )
    validate_flags()
    validate(rows)
    rows.sort(key=sort_key)
    payload = {
        "meta": {
            "name": "RADIOSF",
            "snapshot_date": SNAPSHOT,
            "window_start": WINDOW_START,
            "window_end": WINDOW_END,
            "timezone": "America/Los_Angeles",
            "verified_note": (
                "Line-checked against pages fetched 2026-09-27. Not a live scrape. The Westwood One "
                "NFL list was read end to end this pass, so there is no longer a missing-chunk gap."
            ),
            "durations": DURATIONS,
            "band": {"start": "10:00", "end": "22:00", "label": "10 AM–10 PM, the window you asked about"},
            "confidence_legend": [
                {"id": "official", "label": "Official",
                 "detail": "A club, school, league API or rights holder printed both the game and the station."},
                {"id": "indicated", "label": "Indicated",
                 "detail": "A network or rights-holder lists the event, and another source establishes a Bay Area affiliate relationship. This is not per-game clearance."},
                {"id": "review", "label": "Needs review",
                 "detail": "Two sources disagree, or the radio line was not quoted for that exact row. Open the links."},
            ],
            "stations": [
                {"id": "680", "label": "680 AM", "call": "KNBR", "brand": "KNBR 680",
                 "role": "Giants flagship. 49ers from Week 4. Westwood One NFL and college football affiliate. Cal only for the Big Game.",
                 "listen": KNBR_SHOWS},
                {"id": "104.5", "label": "104.5 FM", "call": "KNBR-FM", "brand": "KNBR 104.5",
                 "role": "Full-time simulcast of 680 since 2019. Same games as 680 whenever a source lists both.",
                 "listen": KNBR_SHOWS},
                {"id": "810", "label": "810 AM", "call": "KSFO", "brand": "810 KSFO",
                 "role": "49ers Weeks 1–3 only. Every Cal football game except the Big Game. Earthquakes English flagship, plus The Soccer Hour Wednesdays 7–8 PM.",
                 "listen": QUAKES},
                {"id": "960", "label": "960 AM", "call": "KNEW", "brand": "960 KNEW",
                 "role": "Athletics baseball through the end of the regular season. Fox Sports Radio talk otherwise, which is not listed as games.",
                 "listen": ATH_RADIO},
                {"id": "1050", "label": "1050 AM", "call": "KTCT", "brand": "KNBR 1050",
                 "role": "Stanford football. Westwood One NFL, college football and U.S. Soccer affiliate. Full-time ESPN Radio affiliate, which is how the MLB postseason reaches the Bay Area.",
                 "listen": KNBR_1050_SHOWS},
                {"id": "107.7", "label": "107.7 FM", "call": "KSAN", "brand": "107.7 The Bone",
                 "role": "49ers FM flagship, every listed regular-season game. Classic rock otherwise.",
                 "listen": NINERS},
            ],
            "counts": {
                "broadcasts": len(rows),
                "conditional": sum(1 for r in rows if r["conditional"]),
                "conditional_games": sum(r.get("conditional_game_count", 0) for r in rows),
                "placed": sum(1 for r in rows if r["date"]),
                "unplaced": sum(1 for r in rows if not r["date"]),
                "official": sum(1 for r in rows if r["confidence"] == "official"),
                "indicated": sum(1 for r in rows if r["confidence"] == "indicated"),
                "review": sum(1 for r in rows if r["confidence"] == "review"),
                "flags": len(FLAGS),
            },
            # Single source of truth for scripts/wwo_watch.py, so the watcher and the
            # feed can never disagree about which grid belongs to which rows.
            "wwo_watch": {
                "endpoint": WWO_GRID_ENDPOINT,
                "widgets": WWO_WIDGETS,
                "merged_nfl_event_ids": sorted(WWO_MERGED_NFL_EVENTS),
                "note": (
                    "Read-only. A widget that returns no events at all is reported as a failed "
                    "check, never as no drift."
                ),
            },
        },
        "flags": FLAGS,
        "broadcasts": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    LINE.write_text(line_markdown(rows, FLAGS), encoding="utf-8")
    print(f"wrote {OUT} ({len(rows)} schedule entries, {len(FLAGS)} flags) and {LINE}")


if __name__ == "__main__":
    main()
