#!/usr/bin/env python3
"""Build the verified radio feed. Source of truth for data/broadcasts.json.

Every row below was transcribed from a page fetched on 2026-09-26.
Do not add a game that is not in this file. Re-fetch before editing.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "broadcasts.json"
LINE = ROOT / "docs" / "LINE_BY_LINE.md"

ALLOWED = ["680", "810", "960", "1050", "104.5", "107.7"]
WINDOW_START = "2026-09-26"
WINDOW_END = "2027-02-28"
SNAPSHOT = "2026-09-26"

WWO_NFL_STATIONS = ["680", "104.5", "1050"]
WWO_NFL_URL = "https://www.westwoodonesports.com/nfl-schedule/"
WWO_NCAAF_URL = "https://www.westwoodonesports.com/ncaa-football/"
WWO_FINDER = "https://www.westwoodonesports.com/station-finder/"
PRESS = (
    "https://www.globenewswire.com/news-release/2026/09/09/3358684/9032/en/"
    "cumulus-media-s-westwood-one-official-network-audio-partner-of-the-nfl-"
    "celebrates-40th-consecutive-season-and-reveals-2026-nfl-lineup-and-"
    "programming-highlights-from-nfl-kickoff-to.html"
)
NINERS = "https://www.49ers.com/schedule/"
GIANTS_RADIO = "https://www.mlb.com/giants/schedule/tv"
ATH_RADIO = "https://www.mlb.com/athletics/schedule/affiliates"
QUAKES = "https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season"
STANFORD_RADIO = "https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced"
STANFORD_DATES = "https://gostanford.com/news/2026/1/26/complete-2026-schedule-unveiled"
STANFORD_ESPN = "https://www.espn.com/college-football/team/schedule/_/id/24/stanford-cardinal"
CAL = "https://calbears.com/sports/football/schedule"
CAL_ESPN = "https://www.espn.com/college-football/team/schedule/_/id/25/california-golden-bears"
KNBR_SHOWS = "https://www.thesportsleader.com/shows/"
KNBR_FM = "https://en.wikipedia.org/wiki/KNBR-FM"

DUR = {"MLB": 165, "NFL": 195, "NCAAF": 204, "MLS": 120, "NFL-TBD": 195}


def et_to_pt(hhmm: str) -> str:
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
        "venue": kw.get("venue") or "",
        "status": kw.get("status", "scheduled"),
        "result": kw.get("result"),
        "stations": kw["stations"],
        "confidence": kw["confidence"],
        "duration_est_min": kw.get("duration_est_min") or DUR[kw["league"]],
        "sources": kw["sources"],
        "notes": kw.get("notes") or "",
        "flag_ids": kw.get("flag_ids") or [],
    }
    bad = [s for s in row["stations"] if s not in ALLOWED]
    if bad:
        raise SystemExit(f"{row['id']} bad station {bad}")
    if not row["sources"]:
        raise SystemExit(f"{row['id']} needs a source")
    if row["date"] and not (WINDOW_START <= row["date"] <= WINDOW_END):
        raise SystemExit(f"{row['id']} date {row['date']} outside window")
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
            "KNBR's own weekly grid (thesportsleader.com/shows, week of Aug 31–Sep 7, 2026) "
            "fills late morning with sports talk (Fair & Biased), not play-by-play. "
            "KNEW 960's published weekday lineup is Fox Sports Radio talk, and KTCT 1050 "
            "is an ESPN Radio pass-through plus The Jim Rome Show. Those are not games. "
            "No official source lists a standing live-game feed from 10 AM to 10 PM on these stations."
        ),
        "url": KNBR_SHOWS,
    },
    {
        "id": "KNBR_GRID_STALE",
        "severity": "review",
        "title": "KNBR weekly grid on the site is not the current week",
        "detail": (
            "Fetched 2026-09-26, thesportsleader.com/shows still prints Monday 8-31 through "
            "Monday 9-7. It is evidence of the format (talk vs Giants vs Westwood One), not "
            "a current-day clearance log. Do not treat those clock times as this week's schedule."
        ),
        "url": KNBR_SHOWS,
    },
    {
        "id": "WWO_PREEMPTION",
        "severity": "review",
        "title": "Westwood One affiliates do not air every game",
        "detail": (
            "Station finder, fetched 2026-09-26: \"Because of local blackouts and/or programming "
            "conflicts, not every affiliate can air every Westwood One Sports broadcast.\" "
            "San Francisco NFL affiliates on that page: KNBR-AM, KNBR-FM, KTCT-AM, and KNBR-F2. "
            "KNBR-F2 is an HD subchannel and is not counted. A local Giants, 49ers, or Stanford "
            "broadcast can preempt the national feed on the station it occupies."
        ),
        "url": WWO_FINDER,
    },
    {
        "id": "WWO_LISTED_START",
        "severity": "review",
        "title": "Westwood One printed time is a listed start, not a confirmed kickoff",
        "detail": (
            "Event 548494 prints \"Sun Sep 27, 2026 7:30 PM – 11:59 PM (EDT).\" "
            "11:59 PM is a placeholder end, not a real ending. 49ers.com kickoffs for the four "
            "49ers games that Westwood One also lists are 45 to 75 minutes later than the "
            "Westwood One printed start. This feed converts the printed Eastern time to Pacific "
            "and labels it a listed start. It does not invent a kickoff."
        ),
        "url": "https://www.westwoodonesports.com/events/548494",
    },
    {
        "id": "WWO_EIGHT_VS_SEVEN",
        "severity": "review",
        "title": "Press release says eight international games; the schedule page lists seven",
        "detail": (
            "Cumulus release 2026-09-09 says the package includes eight International Games. "
            "The nfl-schedule page fetched 2026-09-26 lists seven: London Oct 4, Oct 11, Oct 18; "
            "Paris Oct 25; Madrid Nov 8; Munich Nov 15; Mexico City Nov 22. The eighth was not "
            "on that page. It is not added here."
        ),
        "url": PRESS,
    },
    {
        "id": "WWO_POSTSEASON_UNDATED",
        "severity": "limitation",
        "title": "NFL postseason games are promised but not dated on the schedule page",
        "detail": (
            "The same release says Westwood One carries every NFL postseason game through "
            "Super Bowl LXI on February 14, 2027 at SoFi Stadium. The nfl-schedule page fetched "
            "2026-09-26 ends at Week 18 TBA windows. Wild-card, divisional, and conference "
            "championship dates are not on that page, so they are not placed on the calendar. "
            "Only Super Bowl LXI is placed, and only as date / stadium / time TBD."
        ),
        "url": PRESS,
    },
    {
        "id": "NCAAF_FINDER_TAB",
        "severity": "review",
        "title": "NCAA football clearance uses the NFL affiliate row, not a separate tab extract",
        "detail": (
            "The station-finder NFL table, fetched 2026-09-26, lists San Francisco as "
            "KNBR-AM, KNBR-FM, KTCT-AM. The NCAA Football tab of that page was not separately "
            "extracted in this session. NCAA games are marked indicated, not per-game confirmed. "
            "KNBR's own grid does list a daypart called Westwood One Sports."
        ),
        "url": WWO_FINDER,
    },
    {
        "id": "BIG_GAME_STATIONS",
        "severity": "review",
        "title": "Nov 21 Big Game station claims disagree",
        "detail": (
            "gostanford.com on 2026-07-30 says the football radio team is on KNBR/KTCT 1050 AM. "
            "calbears.com/sports/football/schedule prints \"Radio: KNBR 104.5 FM / 680 AM\" on the "
            "Nov 21 Stanford row, and does not print KSFO on that row in the rendered index. "
            "Both claims are shown. Neither is dropped."
        ),
        "url": CAL,
    },
    {
        "id": "CAL_RADIO_INDEX",
        "severity": "review",
        "title": "Cal radio column was read from the rendered schedule index",
        "detail": (
            "A non-JavaScript fetch of calbears.com/sports/football/schedule on 2026-09-26 "
            "returned the scoreboard, not the radio table. Radio rows used here are the ones "
            "present in the rendered index of that same official URL (page index dated 2026-09-25). "
            "Open the schedule page and check the Radio column before relying on a row."
        ),
        "url": CAL,
    },
        {
            "id": "SFT_RADIO_DIFF",
            "severity": "review",
            "title": "This site and ScheduleFreeTime do not list the same radio games",
            "detail": "On 2026-09-26 ScheduleFreeTime did not put a radio icon on Athletics games. The club affiliates page lists 960 AM KNEW, Bay Area, with no home-only asterisk, so those two games are here. ScheduleFreeTime also lists KZSF 1370 AM on Earthquakes broadcasts. 1370 is not one of the six stations, so it is omitted. Oklahoma at Georgia is 12:00 PM PT here because Westwood One lists 3:00 PM ET. ScheduleFreeTime's table showed 12:30 PM PT, which is the 3:30 PM ET kickoff.",
            "url": "https://www.mlb.com/athletics/schedule/affiliates",
        },
        {
            "id": "CAL_WAKE_ROW",
        "severity": "review",
        "title": "Oct 17 Cal vs Wake Forest radio row was not in the captured excerpt",
        "detail": (
            "The scoreboard fetch shows Oct 17 vs Wake Forest in Berkeley with no time. "
            "ESPN also has the date and kickoff TBD. The rendered-index excerpts quoted KSFO 810 AM "
            "on the other 2026 rows and KNBR on the Big Game, but did not quote the Wake Forest row. "
            "810 AM is shown with a review badge, not as a fully quoted row."
        ),
        "url": CAL,
    },
    {
        "id": "STANFORD_OCT17_TIME",
        "severity": "review",
        "title": "Stanford vs Elon kickoff is from ESPN, not the school excerpt",
        "detail": (
            "ESPN's Stanford schedule prints Sat Oct 17, 7:30 PM, which is 4:30 PM PT. "
            "The gostanford.com news release lists Elon on Oct 17 with no kickoff. "
            "The rendered schedule index excerpt captured this session did not include that kickoff. "
            "Station 1050 AM is from the July 30 school release, not from ESPN."
        ),
        "url": STANFORD_ESPN,
    },
    {
        "id": "QUAKES_SUBJECT_TO_CHANGE",
        "severity": "review",
        "title": "Earthquakes radio table is dated Feb 16, 2026 and says times can change",
        "detail": (
            "The club's radio release is the only per-game English-station table found. "
            "It says \"All times and dates are subject to change.\" The live schedule widget "
            "did not render in a text fetch on 2026-09-26, so later kickoff moves would not "
            "be visible here until the next verification pass. Spanish 1370 AM is not one of "
            "the six stations and is not listed as a station you get."
        ),
        "url": QUAKES,
    },
    {
        "id": "WEEK18_UNPLACED",
        "severity": "review",
        "title": "49ers Week 18 has stations but no date",
        "detail": (
            "49ers.com/schedule prints Week 18 at Arizona Cardinals, State Farm Stadium, "
            "TV TBD, radio KSAN 107.7 / KNBR 104.5 / 680, and no date. It is not placed on "
            "Jan 9 or Jan 10. Those days have separate Westwood One \"teams TBA\" windows."
        ),
        "url": NINERS,
    },
    {
        "id": "MEXICO_VENUE_NAMES",
        "severity": "review",
        "title": "Nov 22 venue name disagrees",
        "detail": (
            "49ers.com prints Estadio Banorte. Westwood One event 548491 prints Estadio Azteca. "
            "Both names are kept. Kickoff used here is the club time, 5:20 PM PT."
        ),
        "url": NINERS,
    },
    {
        "id": "NINERS_BOILERPLATE",
        "severity": "review",
        "title": "Week 1–3 listen articles say \"all games\" are on KSFO; the schedule page switches in October",
        "detail": (
            "Ways-to-listen articles for Weeks 1–3 (latest fetched: Week 3, published Sep 23, 2026) "
            "say all games can be heard on KSFO 810 / KSAN 107.7. The live schedule page, fetched "
            "2026-09-26, prints KSFO/KSAN for Week 3 and KSAN plus KNBR 104.5/680 from Week 4 on. "
            "This feed follows the per-game line on the schedule page."
        ),
        "url": "https://www.49ers.com/news/ways-to-watch-and-listen-cardinals-vs-49ers-week-3-x8427",
    },
    {
        "id": "HD_NOT_COUNTED",
        "severity": "limitation",
        "title": "HD subchannels are not counted as the stations you get",
        "detail": (
            "Westwood One lists KNBR-F2. KSAN's HD3 simulcasts KTCT. A standard AM/FM radio "
            "does not decode those. Only 680, 810, 960, 1050, 104.5, and 107.7 are listed."
        ),
        "url": WWO_FINDER,
    },
    {
        "id": "TALK_NOT_GAMES",
        "severity": "limitation",
        "title": "ESPN Radio and Fox Sports Radio game clearances are not published per affiliate",
        "detail": (
            "KTCT is mainly ESPN Radio. KNEW's weekday daypart is Fox Sports Radio talk "
            "(Dan Patrick, Colin Cowherd, and the rest of that announced lineup), then Premiere talk. "
            "No 2026 per-game list was found that says which national play-by-play, if any, "
            "clears on 1050 or 960 besides Athletics baseball on 960. Those games are not invented."
        ),
        "url": "https://en.wikipedia.org/wiki/KNEW_(AM)",
    },
    {
        "id": "MBB_NO_RADIO_ROWS",
        "severity": "limitation",
        "title": "2026-27 Cal men's basketball page has no radio rows in the fetch",
        "detail": (
            "calbears.com/sports/mens-basketball/schedule fetched 2026-09-26 is the 2026-27 "
            "schedule. The scoreboard lists games from Nov 2 with TBD times and no radio column. "
            "Basketball is not added. Stanford basketball was not re-verified onto 1050 this session "
            "and is not added."
        ),
        "url": "https://calbears.com/sports/mens-basketball/schedule",
    },
    {
        "id": "ATHLETICS_SACRAMENTO",
        "severity": "note",
        "title": "Athletics home games are in Sacramento; 960 AM still carries them",
        "detail": (
            "mlb.com/athletics/schedule/affiliates lists 960 AM KNEW, Bay Area, with no "
            "home-only asterisk. Flagship is 650 AM KSTE in Sacramento. Home venue in the "
            "Stats API is Sutter Health Park."
        ),
        "url": ATH_RADIO,
    },
    {
        "id": "SPANISH_EXCLUDED",
        "severity": "note",
        "title": "Spanish calls are not on the six stations",
        "detail": (
            "Giants Spanish is KSFN 1510 / KXZM 93.7. Earthquakes Spanish is KZSF 1370. "
            "49ers Spanish in the Week 3 listen article is the 49ers app and 49ers.com/esp, "
            "not these six stations. Those calls are omitted."
        ),
        "url": GIANTS_RADIO,
    },
    {
        "id": "WWO_CHUNK_MISSING",
        "severity": "review",
        "title": "The opening chunk of the Westwood One NFL schedule was not returned",
        "detail": (
            "On 2026-09-26 the nfl-schedule page was fetched from the middle of the list forward. "
            "Rows that appeared only in the unread opening chunk are not in this file. "
            "A thin Thursday, Sunday night, or Monday before November is a fetch gap, not a verified quiet night. "
            "Re-fetch https://www.westwoodonesports.com/nfl-schedule/ and add a game only if the line is on the page."
        ),
        "url": "https://www.westwoodonesports.com/nfl-schedule/",
    },
    {
        "id": "WWO_SPLIT_LINE",
        "severity": "review",
        "title": "Oct 26 Cowboys at Eagles was split across two fetches",
        "detail": (
            "The first fetched chunk ended on Dallas at Philadelphia, Oct 26, 7:00 PM ET. "
            "The next chunk opened on event 548539. The row is kept because both fragments match, and marked review."
        ),
        "url": "https://www.westwoodonesports.com/events/548539/",
    },
    {
        "id": "SNAPSHOT_START",
        "severity": "limitation",
        "title": "This snapshot starts September 26, 2026",
        "detail": (
            "Earlier September games were on these stations. They are not in this file, "
            "so days before Sep 26 are marked \"before this snapshot\" instead of \"no game.\" "
            "Extending backward needs another line-by-line pass."
        ),
        "url": GIANTS_RADIO,
    },
    {
        "id": "DURATION_ESTIMATE",
        "severity": "note",
        "title": "End times are estimates",
        "detail": (
            "No source publishes a per-game radio sign-off. The timeline uses typical lengths "
            "(MLB 2:45, NFL 3:15, college football 3:24, MLS 2:00) and labels them estimates. "
            "They are not official endings. Pregame length is not added; the Sep 1–6 KNBR grid "
            "started some Giants blocks an hour before first pitch, but that was one stale week."
        ),
        "url": KNBR_SHOWS,
    },
]


def wwo_nfl_rows() -> list[dict]:
    """Schedule-grid rows fetched from westwoodonesports.com/nfl-schedule on 2026-09-26.
    Four 49ers games are omitted here and attached to the club rows instead. Sixteen lines that were not on a returned page chunk are not included.
    """
    # event_id, date, et 24h or None, title, venue, extra note
    raw = [
        ("548494", "2026-09-27", "19:30", "Los Angeles Rams at Denver Broncos", "Empower Field at Mile High", "Sunday Night Football"),
        ("548532", "2026-09-28", "19:00", "Philadelphia Eagles at Chicago Bears", "Soldier Field", "Monday Night Football"),
        ("548485", "2026-10-04", "09:15", "Indianapolis Colts vs Washington Commanders", "Tottenham Hotspur Stadium, London", "International"),
        ("548535", "2026-10-05", "19:00", "Atlanta Falcons at New Orleans Saints", "Caesars Superdome", "Monday Night Football"),
        ("548486", "2026-10-11", "09:15", "Philadelphia Eagles vs Jacksonville Jaguars", "Tottenham Hotspur Stadium, London", "International"),
        ("548537", "2026-10-12", "19:00", "Buffalo Bills at Los Angeles Rams", "SoFi Stadium", "Monday Night Football"),
        ("548487", "2026-10-18", "09:15", "Houston Texans vs Jacksonville Jaguars", "Wembley Stadium, London", "International"),
        ("548488", "2026-10-25", "09:15", "Pittsburgh Steelers vs New Orleans Saints", "Stade de France, Paris", "International"),
        ("548539", "2026-10-26", "19:00", "Dallas Cowboys at Philadelphia Eagles", "Lincoln Financial Field", "Monday Night Football"),
        ("548499", "2026-11-01", "19:30", "Philadelphia Eagles at Washington Commanders", "Northwest Stadium", "Sunday Night Football"),
        ("548561", "2026-11-05", "19:30", "Jacksonville Jaguars at Baltimore Ravens", "M&T Bank Stadium", "Thursday Night Football"),
        ("548500", "2026-11-08", "19:30", "Tampa Bay Buccaneers at Chicago Bears", "Soldier Field", "Sunday Night Football"),
        ("548562", "2026-11-12", "19:30", "Washington Commanders at New York Giants", "MetLife Stadium", "Thursday Night Football"),
        ("548501", "2026-11-15", "19:30", "Pittsburgh Steelers at Cincinnati Bengals", "Paycor Stadium", "Sunday Night Football"),
        ("548564", "2026-11-19", "19:30", "Indianapolis Colts at Houston Texans", "NRG Stadium", "Thursday Night Football"),
        ("548543", "2026-11-23", "19:00", "Cincinnati Bengals at Washington Commanders", "Northwest Stadium", "Monday Night Football"),
        ("548512", "2026-11-26", "12:30", "Chicago Bears at Detroit Lions", "Ford Field", "Thanksgiving"),
        ("548514", "2026-11-26", "20:00", "Kansas City Chiefs at Buffalo Bills", "New Highmark Stadium", "Thanksgiving"),
        ("548515", "2026-11-27", "14:30", "Denver Broncos at Pittsburgh Steelers", "Acrisure Stadium", "Black Friday"),
        ("548502", "2026-11-29", "19:30", "New England Patriots at Los Angeles Chargers", "SoFi Stadium", "Sunday Night Football"),
        ("548544", "2026-11-30", "19:00", "Carolina Panthers at Tampa Bay Buccaneers", "Raymond James Stadium", "Monday Night Football"),
        ("548566", "2026-12-03", "19:30", "Kansas City Chiefs at Los Angeles Rams", "SoFi Stadium", "Thursday Night Football"),
        ("548503", "2026-12-06", "19:30", "Houston Texans at Pittsburgh Steelers", "Acrisure Stadium", "Sunday Night Football"),
        ("548545", "2026-12-07", "19:00", "Dallas Cowboys at Seattle Seahawks", "Lumen Field", "Monday Night Football"),
        ("548567", "2026-12-10", "19:30", "Minnesota Vikings at New England Patriots", "Gillette Stadium", "Thursday Night Football"),
        ("548505", "2026-12-13", "19:30", "Buffalo Bills at Green Bay Packers", "Lambeau Field", "Sunday Night Football"),
        ("548546", "2026-12-14", "19:00", "Pittsburgh Steelers at Jacksonville Jaguars", "EverBank Stadium", "Monday Night Football"),
        ("548517", "2026-12-19", "16:30", "Seattle Seahawks at Philadelphia Eagles", "Lincoln Financial Field", "Week 15 Saturday"),
        ("548518", "2026-12-19", "20:00", "Chicago Bears at Buffalo Bills", "New Highmark Stadium", "Week 15 Saturday"),
        ("548506", "2026-12-20", "19:30", "Detroit Lions at Minnesota Vikings", "U.S. Bank Stadium", "Sunday Night Football"),
        ("548548", "2026-12-21", "19:00", "New England Patriots at Kansas City Chiefs", "GEHA Field at Arrowhead Stadium", "Monday Night Football"),
        ("548569", "2026-12-24", "19:30", "Houston Texans at Philadelphia Eagles", "Lincoln Financial Field", "Thursday Night Football"),
        ("548528", "2026-12-25", "12:30", "Green Bay Packers at Chicago Bears", "Soldier Field", "Christmas"),
        ("548531", "2026-12-25", "16:15", "Buffalo Bills at Denver Broncos", "Empower Field at Mile High", "Christmas"),
        ("548534", "2026-12-25", "20:00", "Los Angeles Rams at Seattle Seahawks", "Lumen Field", "Christmas"),
        ("548519", "2026-12-26", "16:00", "Week 16 Saturday game — teams TBA", "", "Teams TBA"),
        ("548520", "2026-12-26", "20:00", "Week 16 Saturday game — teams TBA", "", "Teams TBA"),
        ("548507", "2026-12-27", "19:30", "Jacksonville Jaguars at Dallas Cowboys", "AT&T Stadium", "Sunday Night Football"),
        ("548550", "2026-12-28", "19:00", "New York Giants at Detroit Lions", "Ford Field", "Monday Night Football"),
        ("548570", "2026-12-31", "19:30", "Baltimore Ravens at Cincinnati Bengals", "Paycor Stadium", "Thursday Night Football"),
        ("548521", "2027-01-02", "16:00", "Week 17 Saturday game — teams TBA", "", "Teams TBA"),
        ("548522", "2027-01-02", "20:00", "Week 17 Saturday game — teams TBA", "", "Teams TBA"),
        ("548552", "2027-01-04", "19:00", "Houston Texans at Green Bay Packers", "Lambeau Field", "Monday Night Football"),
        ("548523", "2027-01-09", "12:30", "Week 18 Saturday game — teams TBA", "", "Teams TBA"),
        ("548524", "2027-01-09", "16:15", "Week 18 Saturday game — teams TBA", "", "Teams TBA"),
        ("548526", "2027-01-09", "20:00", "Week 18 Saturday game — teams TBA", "", "Teams TBA"),
        ("548510", "2027-01-10", "19:30", "Week 18 Sunday Night Football — teams TBA", "", "Teams TBA"),
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
            venue=venue,
            status="tba" if tba else "scheduled",
            stations=WWO_NFL_STATIONS[:],
            confidence="review" if event_id == "548539" else "indicated",
            sources=[
                src(f"Westwood One event {event_id}", wwo_event(event_id)),
                src("Westwood One NFL schedule", WWO_NFL_URL),
                src("Station finder: San Francisco KNBR-AM, KNBR-FM, KTCT-AM", WWO_FINDER),
            ],
            notes=(
                f"{slot}. Listed start {et_to_pt(et)} PT, converted from {et} ET printed on the "
                "schedule grid. Not a confirmed kickoff. Clearance on 680 / 104.5 / 1050 is the "
                "NFL affiliate row plus the station-finder preemption caveat, not a per-game confirmation."
                + (" This line was split across two fetches: chunk 1 ended on Dallas at Philadelphia, Oct 26, 7:00 PM ET, and the next chunk opened on this event URL. Re-check the schedule page." if event_id == "548539" else "")
            ),
            flag_ids=["WWO_PREEMPTION", "WWO_LISTED_START"] + (["WWO_SPLIT_LINE"] if event_id == "548539" else []),
        ))
    return rows


def wwo_ncaaf_rows() -> list[dict]:
    raw = [
        ("557136", "2026-09-26", "15:00", "Oklahoma at Georgia", "Sanford Stadium, Athens"),
        ("557137", "2026-10-03", None, "Notre Dame at North Carolina", "Kenan Stadium, Chapel Hill"),
        ("557139", "2026-10-10", None, "Indiana at Nebraska", "Memorial Stadium, Lincoln"),
        ("557140", "2026-10-17", None, "Penn State at Michigan", "Michigan Stadium, Ann Arbor"),
        ("557141", "2026-10-24", None, "Ole Miss at Texas", "Darrell K Royal–Texas Memorial Stadium, Austin"),
        ("557129", "2026-10-31", "15:00", "Florida at Georgia", "Mercedes-Benz Stadium, Atlanta"),
        ("557143", "2026-11-07", None, "Oregon at Ohio State", "Ohio Stadium, Columbus"),
        ("557144", "2026-11-14", None, "Michigan at Oregon", "Autzen Stadium, Eugene"),
        ("557145", "2026-11-21", None, "LSU at Tennessee", "Neyland Stadium, Knoxville"),
        ("557131", "2026-11-28", "11:30", "Michigan at Ohio State", "Ohio Stadium, Columbus"),
        ("557146", "2026-12-05", "15:30", "SEC Championship Game", "Mercedes-Benz Stadium, Atlanta"),
        ("557132", "2026-12-12", "14:00", "Army vs Navy", "MetLife Stadium"),
    ]
    more = (
        "https://www.westwoodonesports.com/more/eventGrid?id=47030&range=current&offset=0&limit=20"
        "&timezone=America/New_York&widgetTitle=Upcoming+NCAA+Football+Broadcasts"
    )
    rows = []
    for event_id, date, et, title, venue in raw:
        rows.append(game(
            id=f"wwo-ncaaf-{event_id}",
            date=date,
            start_pt=et_to_pt(et) if et else None,
            title=f"Westwood One: {title}",
            league="NCAAF",
            venue=venue,
            status="scheduled" if et else "tba",
            stations=WWO_NFL_STATIONS[:],
            confidence="indicated",
            sources=[
                src(f"Westwood One event {event_id}", wwo_event(event_id)),
                src("NCAA football grid, including the More endpoint (ends \"No more events\")", more),
            ],
            notes=(
                ("Air time TBD on the Westwood One grid." if not et else
                f"Listed start {et_to_pt(et)} PT from {et} ET on the grid. "
                "NCAA station-finder tab was not separately extracted; stations are the confirmed NFL affiliate row.")
                + (" ScheduleFreeTime's public table showed 12:30 PM PT on 2026-09-26, which matches the 3:30 PM ET kickoff, not this 3:00 PM ET listed start." if event_id == "557136" else "")
            ),
            flag_ids=["WWO_PREEMPTION", "WWO_LISTED_START", "NCAAF_FINDER_TAB"] + (["SFT_RADIO_DIFF"] if event_id == "557136" else []),
        ))
    return rows


def local_rows() -> list[dict]:
    rows = []
    rows.append(game(
        id="giants-2026-09-26",
        date="2026-09-26",
        start_pt="13:05",
        title="Los Angeles Dodgers at San Francisco Giants",
        league="MLB",
        venue="Oracle Park",
        status="final",
        result="Dodgers 4, Giants 3",
        stations=["680", "104.5"],
        confidence="official",
        sources=[
            src("MLB Stats API gamePk 823165, first pitch 2026-09-26T20:05:00Z", mlb_game(823165)),
            src("Giants English radio: KNBR 680 AM & 104.5 FM", GIANTS_RADIO),
        ],
        notes="Final when fetched. 20:05 UTC is 1:05 PM PDT. English call only.",
        flag_ids=["SPANISH_EXCLUDED", "DURATION_ESTIMATE"],
    ))
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
        notes="Last Giants game returned by the Stats API through 2026-10-02. No later Giants game is added.",
        flag_ids=["SPANISH_EXCLUDED", "DURATION_ESTIMATE"],
    ))
    rows.append(game(
        id="athletics-2026-09-26",
        date="2026-09-26",
        start_pt="18:40",
        title="Houston Astros at Athletics",
        league="MLB",
        venue="Sutter Health Park, Sacramento",
        status="pregame",
        stations=["960"],
        confidence="official",
        sources=[
            src("MLB Stats API gamePk 824949, first pitch 2026-09-27T01:40:00Z", mlb_game(824949)),
            src("A's Radio Network: 960 AM KNEW, Bay Area", ATH_RADIO),
        ],
        notes="Status was Pre-Game when fetched. Home games are in Sacramento. 960 has no home-only asterisk on the affiliate page. ScheduleFreeTime did not mark this game as Bay Area radio; this row follows the club affiliates page.",
        flag_ids=["ATHLETICS_SACRAMENTO", "SFT_RADIO_DIFF", "DURATION_ESTIMATE"],
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
        notes="Last Athletics game returned by the Stats API through 2026-10-05. No postseason Athletics game is added. ScheduleFreeTime did not mark Athletics games as Bay Area radio; this row follows the club affiliates page.",
        flag_ids=["ATHLETICS_SACRAMENTO", "SFT_RADIO_DIFF", "DURATION_ESTIMATE"],
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
        "2026-10-19": "Westwood One event 548538 prints 7:00 PM ET (4:00 PM PT) for this game. Club kickoff is 5:15 PM PT. Local call is the one on the stations below.",
        "2026-11-22": "Westwood One event 548491 prints 7:30 PM ET (4:30 PM PT) and Estadio Azteca. Club kickoff is 5:20 PM PT at Estadio Banorte.",
        "2026-12-17": "Westwood One event 548568 prints 7:30 PM ET (4:30 PM PT). Club kickoff is 5:15 PM PT.",
        "2027-01-03": "Westwood One event 548509 prints 7:30 PM ET (4:30 PM PT). Club kickoff is 5:20 PM PT.",
    }
    week3 = "https://www.49ers.com/news/ways-to-watch-and-listen-cardinals-vs-49ers-week-3-x8427"
    for date, start, title, venue, stations, week, tv, extra_flags in niners:
        sources = [
            src(f"49ers.com schedule, {week}, radio line as printed", NINERS),
        ]
        if date == "2026-09-27":
            sources.append(src("Week 3 ways to listen, 1:05 PM PT, KSFO 810 / KSAN 107.7", week3))
        notes = f"{week}. TV on the schedule page: {tv}. Times are the PT clock printed by 49ers.com."
        if date in wwo_same:
            notes += " " + wwo_same[date]
        rows.append(game(
            id=f"niners-{date}",
            date=date,
            start_pt=start,
            title=title,
            league="NFL",
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

    stanford = [
        ("2026-09-26", "19:30", "Georgia Tech at Stanford", "Stanford Stadium", "official",
         "7:30 PM PDT on the rendered gostanford schedule index; ESPN prints 10:30 PM ET.",
         [src("ESPN Stanford schedule, 10:30 PM ET = 7:30 PM PT", STANFORD_ESPN),
          src("2026 dates, Georgia Tech on Sep 26", STANFORD_DATES),
          src("Radio team on KNBR/KTCT 1050 AM", STANFORD_RADIO)],
         []),
        ("2026-10-03", "09:00", "Stanford at Wake Forest", "Winston-Salem", "official",
         "9:00 AM PDT on the rendered schedule index; ESPN prints 12:00 PM ET.",
         [src("ESPN Stanford schedule, 12:00 PM ET = 9:00 AM PT", STANFORD_ESPN),
          src("Radio team on KNBR/KTCT 1050 AM", STANFORD_RADIO)],
         []),
        ("2026-10-10", "12:30", "Stanford at Notre Dame", "Notre Dame Stadium", "official",
         "12:30 PM on the rendered schedule index; ESPN prints 3:30 PM ET on NBC.",
         [src("ESPN Stanford schedule, 3:30 PM ET = 12:30 PM PT", STANFORD_ESPN),
          src("2026 dates, at Notre Dame on Oct 10", STANFORD_DATES),
          src("Radio team on KNBR/KTCT 1050 AM", STANFORD_RADIO)],
         []),
        ("2026-10-17", "16:30", "Elon at Stanford", "Stanford Stadium", "review",
         "Kickoff is ESPN's 7:30 PM ET converted to 4:30 PM PT. School excerpt did not include this kickoff.",
         [src("ESPN Stanford schedule, Oct 17, 7:30 PM", STANFORD_ESPN),
          src("School release lists Elon on Oct 17, no kickoff", STANFORD_DATES),
          src("Radio team on KNBR/KTCT 1050 AM", STANFORD_RADIO)],
         ["STANFORD_OCT17_TIME"]),
        ("2026-10-23", "19:30", "NC State at Stanford", "Stanford Stadium", "official",
         "Friday 7:30 PM PDT on the rendered schedule index; ESPN prints 10:30 PM ET.",
         [src("ESPN Stanford schedule, 10:30 PM ET = 7:30 PM PT", STANFORD_ESPN),
          src("Radio team on KNBR/KTCT 1050 AM", STANFORD_RADIO)],
         []),
        ("2026-10-31", None, "Stanford at Louisville", "Louisville", "official",
         "Date is on the school release and ESPN. Kickoff TBD on ESPN.",
         [src("ESPN Stanford schedule, Oct 31 TBD", STANFORD_ESPN),
          src("School release, at Louisville Oct 31", STANFORD_DATES),
          src("Radio team on KNBR/KTCT 1050 AM", STANFORD_RADIO)],
         []),
        ("2026-11-14", None, "Stanford at Virginia Tech", "Blacksburg", "official",
         "Date is on the school release and ESPN. Kickoff TBD.",
         [src("ESPN Stanford schedule, Nov 14 TBD", STANFORD_ESPN),
          src("School release, at Virginia Tech Nov 14", STANFORD_DATES),
          src("Radio team on KNBR/KTCT 1050 AM", STANFORD_RADIO)],
         []),
        ("2026-11-28", None, "SMU at Stanford", "Stanford Stadium", "official",
         "Date is on the school release and ESPN. Kickoff TBD.",
         [src("ESPN Stanford schedule, Nov 28 TBD", STANFORD_ESPN),
          src("School release, SMU on Nov 28", STANFORD_DATES),
          src("Radio team on KNBR/KTCT 1050 AM", STANFORD_RADIO)],
         []),
    ]
    for date, start, title, venue, confidence, notes, sources, flags in stanford:
        rows.append(game(
            id=f"stanford-{date}",
            date=date,
            start_pt=start,
            title=title,
            league="NCAAF",
            venue=venue,
            status="scheduled" if start else "tba",
            stations=["1050"],
            confidence=confidence,
            sources=sources,
            notes=notes + " \"KNBR/KTCT 1050 AM\" is the 1050 station, not 680.",
            flag_ids=flags + ["DURATION_ESTIMATE"],
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
            src("Cal schedule index: Radio KNBR 104.5 FM / 680 AM on the Nov 21 row", CAL),
            src("Stanford radio release: KNBR/KTCT 1050 AM for the football season", STANFORD_RADIO),
            src("Both schools list Nov 21; ESPN kickoff TBD", STANFORD_ESPN),
        ],
        notes="One game, two station claims. 810 AM is not printed on the Cal Big Game row in the captured index. Kickoff TBD.",
        flag_ids=["BIG_GAME_STATIONS", "CAL_RADIO_INDEX", "DURATION_ESTIMATE"],
    ))

    cal = [
        ("2026-10-03", "12:30", "California at UNLV", "Allegiant Stadium, Las Vegas", "official",
         "Scoreboard fetch prints Oct 3, 12:30 PM at UNLV. ESPN prints 3:30 PM ET on CBSSN, which is 12:30 PM PT. Radio KSFO quoted in the rendered index."),
        ("2026-10-10", None, "Virginia Tech at California", "California Memorial Stadium", "official",
         "Radio KSFO quoted in the rendered index. Kickoff not on the scoreboard fetch. ESPN TBD."),
        ("2026-10-24", None, "California at SMU", "Gerald J. Ford Stadium, Dallas", "official",
         "Radio KSFO quoted in the rendered index. Kickoff TBD on ESPN."),
        ("2026-10-31", None, "California at NC State", "Carter-Finley Stadium, Raleigh", "official",
         "Radio KSFO quoted in the rendered index. Kickoff TBD on ESPN."),
        ("2026-11-14", None, "California at Virginia", "Scott Stadium, Charlottesville", "official",
         "Radio KSFO quoted in the rendered index. Kickoff TBD on ESPN."),
        ("2026-11-28", None, "Pittsburgh at California", "California Memorial Stadium", "official",
         "Radio KSFO quoted in the rendered index. Kickoff TBD on ESPN."),
    ]
    for date, start, title, venue, confidence, notes in cal:
        rows.append(game(
            id=f"cal-{date}",
            date=date,
            start_pt=start,
            title=title,
            league="NCAAF",
            venue=venue,
            status="scheduled" if start else "tba",
            stations=["810"],
            confidence=confidence,
            sources=[
                src("Cal football schedule, radio column in the rendered index", CAL),
                src("ESPN Cal schedule, time cross-check", CAL_ESPN),
            ],
            notes=notes,
            flag_ids=["CAL_RADIO_INDEX", "DURATION_ESTIMATE"],
        ))
    rows.append(game(
        id="cal-2026-10-17",
        date="2026-10-17",
        start_pt=None,
        title="Wake Forest at California",
        league="NCAAF",
        venue="California Memorial Stadium",
        status="tba",
        stations=["810"],
        confidence="review",
        sources=[
            src("Cal scoreboard fetch: Oct 17 vs Wake Forest, Berkeley, no time", CAL),
            src("ESPN Cal schedule: Oct 17, kickoff TBD", CAL_ESPN),
        ],
        notes="Date is official. 810 AM is the pattern of the other quoted rows, not a quoted Wake Forest row. Review the Radio column.",
        flag_ids=["CAL_WAKE_ROW", "CAL_RADIO_INDEX", "DURATION_ESTIMATE"],
    ))

    quakes = [
        ("2026-09-26", "19:30", "Portland Timbers at San Jose Earthquakes", "PayPal Park", "Home"),
        ("2026-10-10", "18:30", "San Jose Earthquakes at Colorado Rapids", "", "Away"),
        ("2026-10-14", "18:30", "San Jose Earthquakes at Real Salt Lake", "", "Away"),
        ("2026-10-17", "19:30", "Nashville SC at San Jose Earthquakes", "PayPal Park", "Home"),
        ("2026-10-24", "17:30", "San Jose Earthquakes at FC Dallas", "", "Away"),
        ("2026-10-28", "19:30", "Colorado Rapids at San Jose Earthquakes", "PayPal Park", "Home"),
        ("2026-10-31", "14:00", "Real Salt Lake at San Jose Earthquakes", "PayPal Park", "Home"),
        ("2026-11-07", "16:00", "San Jose Earthquakes at Minnesota United FC", "", "Away"),
    ]
    for date, start, title, venue, ha in quakes:
        rows.append(game(
            id=f"quakes-{date}",
            date=date,
            start_pt=start,
            title=title,
            league="MLS",
            venue=venue,
            stations=["810"],
            confidence="official",
            sources=[src(f"Club radio release 2026-02-16, {ha}, 810 / 1370", QUAKES)],
            notes="English station in the table is 810. Spanish 1370 is not one of the six stations. Release says times can change. No playoff radio table was published in that release.",
            flag_ids=["QUAKES_SUBJECT_TO_CHANGE", "SPANISH_EXCLUDED", "DURATION_ESTIMATE"],
        ))

    rows.append(game(
        id="super-bowl-lxi",
        date="2027-02-14",
        start_pt=None,
        title="Super Bowl LXI — teams not announced on the Westwood One schedule page",
        league="NFL",
        venue="SoFi Stadium, Inglewood",
        status="tba",
        stations=WWO_NFL_STATIONS[:],
        confidence="indicated",
        sources=[
            src("Cumulus release 2026-09-09: Super Bowl LXI, February 14, 2027, SoFi Stadium", PRESS),
            src("NFL affiliate row: KNBR-AM, KNBR-FM, KTCT-AM", WWO_FINDER),
        ],
        notes="Date and stadium are from the release. Kickoff is not on the schedule page. Teams are not announced there. Not a confirmed clock time.",
        flag_ids=["WWO_POSTSEASON_UNDATED", "WWO_PREEMPTION", "WWO_LISTED_START"],
    ))
    return rows


def validate(rows: list[dict]) -> None:
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate ids")
    wwo = [r for r in rows if r["id"].startswith("wwo-nfl-")]
    if len(wwo) != 47:
        raise SystemExit(f"expected 47 standalone WWO NFL rows, got {len(wwo)}")
    ncaaf = [r for r in rows if r["id"].startswith("wwo-ncaaf-")]
    if len(ncaaf) != 12:
        raise SystemExit(f"expected 12 WWO NCAAF rows, got {len(ncaaf)}")
    banned = {
        "548554", "548495", "548556", "548496", "548557", "548497", "548558", "548498",
        "548560", "548540", "548489", "548541", "548490", "548542", "548491", "548511", "548513",
    }
    merged = {"548538", "548491", "548568", "548509"}
    present = {r["id"].split("-")[-1] for r in wwo}
    if present & banned:
        raise SystemExit(f"unfetched WWO events must not ship: {present & banned}")
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
    giants = [r for r in rows if r["id"].startswith("giants-")]
    for r in giants:
        if r["stations"] != ["680", "104.5"]:
            raise SystemExit("giants stations")
    for r in rows:
        if r["id"].startswith("athletics-") and r["stations"] != ["960"]:
            raise SystemExit("athletics station")
        if r["id"].startswith("quakes-") and r["stations"] != ["810"]:
            raise SystemExit("quakes station")
        if r["id"].startswith("stanford-") and r["stations"] != ["1050"]:
            raise SystemExit("stanford station")
    if any(r["id"] == "big-game-2026-11-21" and "810" in r["stations"] for r in rows):
        raise SystemExit("do not put 810 on the Big Game without a quoted row")
    unplaced = [r for r in rows if r["date"] is None]
    if len(unplaced) != 1 or unplaced[0]["id"] != "niners-week-18":
        raise SystemExit("unexpected unplaced rows")


def line_markdown(rows: list[dict], flags: list[dict]) -> str:
    lines = [
        "# Line-by-line broadcast list",
        "",
        f"Snapshot {SNAPSHOT}. Window {WINDOW_START} through {WINDOW_END}, America/Los_Angeles.",
        "Every row is generated from `scripts/build_feed.py`. Open the source link before treating a row as settled.",
        "",
        "| Date | PT listed start | Stations | Confidence | Game | Sources |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    def sort_key(r):
        return (r["date"] or "9999", r["start_pt"] or "99:99", r["title"])
    for r in sorted(rows, key=sort_key):
        start = r["start_pt"] or "TBD"
        stations = ", ".join(r["stations"])
        links = ", ".join(f"[{s['label']}]({s['url']})" for s in r["sources"])
        date = r["date"] or "DATE TBD"
        title = r["title"].replace("|", "/")
        lines.append(f"| {date} | {start} | {stations} | {r['confidence']} | {title} | {links} |")
    lines += ["", "## Flags", ""]
    for f in flags:
        lines.append(f"- **{f['id']}** ({f['severity']}): {f['title']} — {f['detail']} [link]({f['url']})")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    rows = local_rows() + wwo_nfl_rows() + wwo_ncaaf_rows()
    validate(rows)
    payload = {
        "meta": {
            "name": "RADIOSF",
            "snapshot_date": SNAPSHOT,
            "window_start": WINDOW_START,
            "window_end": WINDOW_END,
            "timezone": "America/Los_Angeles",
            "verified_note": "Line-checked against pages fetched 2026-09-26. Not a live scrape. National NFL games that were only on the unread opening chunk of the Westwood One schedule are omitted.",
            "duration_estimates_min": {"MLB": 165, "NFL": 195, "NCAAF": 204, "MLS": 120},
            "band": {"start": "10:00", "end": "22:00", "label": "10 AM–10 PM, the window you asked about"},
            "stations": [
                {"id": "680", "label": "680 AM", "call": "KNBR", "brand": "KNBR 680", "role": "Giants flagship. 49ers from Week 4. Westwood One NFL affiliate.", "listen": "https://www.thesportsleader.com/"},
                {"id": "104.5", "label": "104.5 FM", "call": "KNBR-FM", "brand": "KNBR 104.5", "role": "Full-time simulcast of 680 since 2019. Same games as 680 when a source lists both.", "listen": "https://www.thesportsleader.com/"},
                {"id": "810", "label": "810 AM", "call": "KSFO", "brand": "810 KSFO", "role": "49ers Weeks 1–3. Cal football. Earthquakes English.", "listen": "https://www.ksfo.com/"},
                {"id": "960", "label": "960 AM", "call": "KNEW", "brand": "960 KNEW", "role": "Athletics baseball. Otherwise Fox Sports Radio talk, not listed as games.", "listen": "https://www.mlb.com/athletics/schedule/affiliates"},
                {"id": "1050", "label": "1050 AM", "call": "KTCT", "brand": "KNBR 1050", "role": "Stanford football. Westwood One NFL affiliate. ESPN Radio talk otherwise.", "listen": "https://www.thesportsleader.com/knbr1050shows"},
                {"id": "107.7", "label": "107.7 FM", "call": "KSAN", "brand": "107.7 The Bone", "role": "49ers FM flagship, every listed regular-season game. Classic rock otherwise.", "listen": "https://www.49ers.com/schedule/"},
            ],
            "counts": {
                "broadcasts": len(rows),
                "placed": sum(1 for r in rows if r["date"]),
                "unplaced": sum(1 for r in rows if not r["date"]),
                "official": sum(1 for r in rows if r["confidence"] == "official"),
                "indicated": sum(1 for r in rows if r["confidence"] == "indicated"),
                "review": sum(1 for r in rows if r["confidence"] == "review"),
            },
        },
        "flags": FLAGS,
        "broadcasts": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    LINE.write_text(line_markdown(rows, FLAGS), encoding="utf-8")
    print(f"wrote {OUT} ({len(rows)} broadcasts) and {LINE}")


if __name__ == "__main__":
    main()
