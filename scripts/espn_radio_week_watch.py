#!/usr/bin/env python3
"""Read-only monitor for the weekly ESPN Radio grid at espn.com/espnradio/schedule.

The page is the format schedule for the whole ESPN Radio network. On sports days
it prints real live games — on 2026-09-27 it carried "MLB: Mets @ Rangers" on
Wednesday, "MLB: Guardians @ Royals" on Friday, and "CFB: Wisconsin @ Penn State"
plus "CFB: Texas A&M @ LSU" on Saturday — each with a weekday label and an
Eastern join time, and with **no date anywhere on the page**. A row taken from it
blindly could be a week stale, attributed to the wrong days, with nothing on the
page to show it.

So this monitor does three things, and the order is the whole point:

1. **Parse** the grid into (weekday, sport, away, home, Eastern join time) rows.
   A page that parses to zero game rows is a failed check, never "no games".
2. **Date** the week. The grid covers exactly one Monday-to-Sunday week, so the
   monitor tests three candidates — last week, this week, next week, centred on
   today's date in the page's own Eastern zone. For each candidate every row's
   weekday is mapped to a real ISO date and checked against ESPN's dated
   scoreboard (site.api.espn.com, the feed the page watchers already use). A
   candidate validates when at least one row is confirmed on its derived day
   and no row is contradicted by it. Zero or several validating candidates mean
   the week cannot be dated: status **unavailable**. The monitor never lets an
   unvalidated week produce a date.
3. **Compare** each future row of the validated week with the snapshot. A game
   whose matchup appears in a snapshot row for that date is covered. A future
   in-window game no snapshot row names is reported as **changed**, with the
   derived date, the printed join time and links to the grid page and to the
   dated scoreboard for manual review, because it is a candidate listing for
   1050 — the same affiliate inference every ESPN Radio row in this feed
   already states out loud. Only a human re-read and rebuild turns it into a
   row, and a grid game is never a Bay Area clearance.

Three outcomes, kept strictly apart like the other monitors:

* **clear** — the week was validated, every row of it was checked against a
  dated source, and every future in-window grid game is already represented in
  the snapshot (a grid that has not rolled over yet, whose games are all past,
  is a clear run with a note, never an error).
* **changed** — the week was dated, and the grid prints a future in-window game
  the snapshot does not name.
* **unavailable** — the page could not be fetched or parsed, the week could not
  be dated (zero or multiple validating candidates, including a candidate the
  dated scoreboard contradicts), or rows stayed unchecked.

Usage:
    python3 scripts/espn_radio_week_watch.py \
        --input scripts/fixtures/espn_radio_week_2026-09-27.json
    python3 scripts/espn_radio_week_watch.py --report "$RUNNER_TEMP/espn-week.md"

--input reads a JSON save of {grid_html, scoreboards: {"SPORT|YYYY-MM-DD": ...}}
so the tests and any offline re-run need no network.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date, datetime, timedelta
from http.client import HTTPException
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
FEED_PATH = ROOT / "data" / "broadcasts.json"
GRID_URL = "https://www.espn.com/espnradio/schedule"
# espn.com answers bare scripted clients with HTTP 202 on many pages, so the
# grid is requested with an ordinary browser agent — the same convention
# page_watch.py uses for the club and school pages. The dated scoreboard lives
# on site.api.espn.com, which automation reaches normally.
USER_AGENT_HTML = ("Mozilla/5.0 (compatible; RADIOSF-source-watch/1.0; "
                   "+https://github.com/buffedlizard55-lab/RADIOSF)")
USER_AGENT_API = "RADIOSF-source-watch/1.0 (+https://github.com/buffedlizard55-lab/RADIOSF)"

TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
DAY_RE = re.compile(r"^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$", re.IGNORECASE)
# The grid prints "MLB: Mets @ Rangers". The sport token must be 2-6 uppercase
# letters or digits so ordinary show titles cannot look like game rows.
GAME_RE = re.compile(r"^(?P<sport>[A-Z][A-Z0-9]{1,5}):\s+(?P<rest>.*\S)\s*$")
MATCHUP_RE = re.compile(r"^(?P<away>.+?)\s*@\s*(?P<home>.+?)\s*$")
DOUBLEHEADER_RE = re.compile(r"\s*\((?:Game\s+[12I]+)\)\s*$", re.IGNORECASE)
TIME_RE = re.compile(
    r"^(?P<h>\d{1,2}):(?P<m>\d{2})\s*(?P<ap>[ap])\.?\s*m\.?\s*(?:ET|EST|EDT)?$", re.IGNORECASE
)
TIME_INLINE_RE = re.compile(
    r"\s+(?P<h>\d{1,2}):(?P<m>\d{2})\s*(?P<ap>[ap])\.?\s*m\.?(?:\s*(?:ET|EST|EDT))?\s*$",
    re.IGNORECASE,
)
WEEKDAY_INDEX = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}
# The grid covers exactly one week, so the only sane worlds are last week (it
# has not rolled over), this week, or next week (it rolled early). Anything else
# is a page that changed shape, and "unavailable" is the honest answer.
CANDIDATE_WEEK_OFFSETS = (-7, 0, 7)
# Tokens that look like matchups but name no game yet ("TBD @ TBD" style rows).
# They are reported for a human read and never used as dating evidence.
NULL_TOKENS = {"tbd", "tba", "n/a", "none", "nonesuch", "-", "--", "—"}


class MonitorError(Exception):
    """The source could not be checked safely; the state is unknown."""


def strip_to_lines(document: str) -> list[str]:
    """Page markup to normalised visible-text lines, in document order."""
    text = html.unescape(TAG_RE.sub("\n", document))
    lines = []
    for raw in text.split("\n"):
        line = SPACE_RE.sub(" ", raw).strip().strip("*").strip()
        if line:
            lines.append(line)
    return lines


def clock_24h(hour: int, minute: int, ampm: str) -> str:
    if not (1 <= hour <= 12 and 0 <= minute <= 59):
        raise MonitorError(f"the printed clock {hour}:{minute:02d} {ampm} is out of range")
    # The grid prints "7:30 p.m.", "7:30 pm" and "7:30 PM". The capture is the
    # letter; anything else in the token is punctuation.
    token = re.sub(r"[^ap]", "", ampm.lower())
    if token not in ("a", "p"):
        raise MonitorError(f"the printed clock {hour}:{minute:02d} {ampm} is not a.m. or p.m.")
    if token == "p" and hour != 12:
        hour += 12
    if token == "a" and hour == 12:
        hour = 0
    return f"{hour:02d}:{minute:02d}"


def parse_clock(line: str) -> str | None:
    match = TIME_RE.match(line)
    if not match:
        return None
    return clock_24h(int(match["h"]), int(match["m"]), match["ap"])


def parse_grid(document: str, supported_sports: set[str]) -> dict[str, Any]:
    """Turn the weekly page into game rows labelled by weekday.

    Every game-shaped line must sit under a weekday heading and carry a clock
    time before the next game or day. Each of the seven days may appear exactly
    once — a second MONDAY would make the week boundary ambiguous. A page whose
    table structure has changed fails loudly instead of returning a shorter,
    quieter list.
    """
    lines = strip_to_lines(document)
    games: list[dict[str, Any]] = []
    unmatchable: list[str] = []
    seen_days: set[str] = set()
    current_day: str | None = None
    for index, line in enumerate(lines):
        day = DAY_RE.match(line)
        if day:
            name = day.group(1).lower()
            if name in seen_days:
                # Responsive copies of the same week reprint MONDAY–SUNDAY. A
                # second copy is ignored rather than treated as a second week,
                # which would make every date ambiguous.
                current_day = None
                continue
            seen_days.add(name)
            current_day = name
            continue
        game = GAME_RE.match(line)
        if not game or game.group("sport") not in supported_sports:
            continue
        if current_day is None:
            if seen_days:
                continue
            raise MonitorError(f"the grid lists “{line}” before any weekday heading")
        rest = game.group("rest").strip()
        time_et = None
        # The join time may trail the matchup on the same line, or sit in the
        # next table cell, which arrives as the next stripped line. Strip the
        # clock first so a trailing "(Game 1)" can still be recognised.
        inline = TIME_INLINE_RE.search(rest)
        if inline:
            time_et = clock_24h(int(inline["h"]), int(inline["m"]), inline["ap"])
            rest = rest[: inline.start()].strip()
        else:
            for follow in lines[index + 1 : index + 8]:
                if GAME_RE.match(follow) or DAY_RE.match(follow):
                    break
                time_et = parse_clock(follow)
                if time_et:
                    break
        rest = DOUBLEHEADER_RE.sub("", rest).strip()
        matchup = MATCHUP_RE.match(rest)
        if not matchup or matchup.group("away").strip().lower() in NULL_TOKENS or \
                matchup.group("home").strip().lower() in NULL_TOKENS:
            unmatchable.append(f"{current_day.upper()}: {line}")
            continue
        if time_et is None:
            raise MonitorError(f"the grid lists “{line}” with no clock time beside it")
        games.append({
            "weekday": current_day.upper(),
            "sport": game.group("sport"),
            "away": matchup.group("away").strip(),
            "home": matchup.group("home").strip(),
            "time_et": time_et,
            "printed": line,
        })
    if not seen_days:
        raise MonitorError("the page has no MONDAY-through-SUNDAY headings; it is not the weekly grid")
    if not games and not unmatchable:
        raise MonitorError(
            "the weekly grid parsed to no game rows at all; that is either a genuinely gameless "
            "week or a page restructure, and this monitor does not tell the two apart on its own"
        )
    if not games and unmatchable:
        raise MonitorError(
            "every sport line on the grid lacked a matchup, so the week cannot be dated: "
            + "; ".join(unmatchable)
        )
    return {"games": games, "unmatchable": unmatchable, "days_seen": sorted(seen_days)}


def fetch(url: str, accept: str, agent: str, timeout: int = 30) -> str:
    request = Request(url, headers={"User-Agent": agent, "Accept": accept})
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise MonitorError(f"{url} returned HTTP {response.status}")
            body = response.read().decode("utf-8", errors="replace")
    except MonitorError:
        raise
    except (HTTPError, URLError, TimeoutError, OSError, HTTPException, UnicodeDecodeError) as exc:
        raise MonitorError(f"{url} could not be fetched ({exc})") from exc
    if len(body.strip()) < 200:
        raise MonitorError(f"{url} returned an almost-empty body, which is not evidence of anything")
    return body


def load_config(feed: dict[str, Any]) -> dict[str, Any]:
    watch = feed.get("meta", {}).get("espn_week_watch")
    if not isinstance(watch, dict):
        raise MonitorError("the feed has no meta.espn_week_watch block; rebuild it with build_feed.py")
    for key in ("grid", "scoreboard", "human_scoreboard", "sports", "today_zone"):
        if not watch.get(key):
            raise MonitorError(f"meta.espn_week_watch.{key} is missing")
    if not str(watch["grid"]).startswith("https://"):
        raise MonitorError("meta.espn_week_watch.grid must be an https URL")
    for sport, entry in watch["sports"].items():
        if not entry.get("league_path") or not entry.get("section"):
            raise MonitorError(f"meta.espn_week_watch.sports.{sport} needs league_path and section")
    return watch


def competitor_texts(team: dict[str, Any]) -> str:
    parts = [str(team.get(key, "")) for key in
             ("location", "name", "nickname", "displayName", "shortDisplayName", "abbreviation")]
    return " ".join(parts).casefold()


def scoreboard_match(payload: dict[str, Any], away: str, home: str) -> str | None:
    """'match', 'flipped' or None: does this dated scoreboard carry away @ home?"""
    wanted_away, wanted_home = away.casefold(), home.casefold()
    for event in payload.get("events", []) or []:
        competitions = event.get("competitions") or []
        if not competitions:
            continue
        texts: dict[str, str] = {}
        for competitor in competitions[0].get("competitors", []) or []:
            side = competitor.get("homeAway")
            if side in ("away", "home"):
                texts[side] = competitor_texts(competitor.get("team") or {})
        if len(texts) != 2:
            continue
        if wanted_away in texts.get("away", "") and wanted_home in texts.get("home", ""):
            return "match"
        if wanted_home in texts.get("away", "") and wanted_away in texts.get("home", ""):
            return "flipped"
    return None


def snapshot_row_text(row: dict[str, Any]) -> str:
    parts = [str(row.get("title", "")), str(row.get("venue", ""))]
    for game in row.get("game_details") or []:
        parts.append(f"{game.get('description', '')} {game.get('away', '')} at {game.get('home', '')}")
    return " ".join(parts).casefold()


def derive_rows(games: list[dict[str, Any]], config: dict[str, Any], monday: date,
                scoreboard: Callable[[str, str], dict[str, Any] | None],
                ) -> list[dict[str, Any]]:
    """Attach a real date to every row for one candidate week and check it.

    check is "match" | "flipped" (confirmed on the derived day), "absent" (the
    dated scoreboard contradicts this candidate) or "unknown" (the scoreboard
    could not be consulted; that row is evidence of nothing).
    """
    derived = []
    for game in games:
        entry = config["sports"].get(game["sport"])
        if entry is None:
            continue
        when = monday + timedelta(days=WEEKDAY_INDEX[game["weekday"].lower()])
        day = when.isoformat()
        row = dict(game)
        payload = scoreboard(game["sport"], day)
        if payload is None:
            row["check"] = "unknown"
        else:
            outcome = scoreboard_match(payload, game["away"], game["home"])
            row["check"] = outcome or "absent"
        row["derived_date"] = day
        row["section"] = entry["section"]
        derived.append(row)
    return derived


def week_verdict(derived: list[dict[str, Any]]) -> tuple[bool, dict[str, int]]:
    tallies = {
        "matched": sum(1 for r in derived if r["check"] in ("match", "flipped")),
        "absent": sum(1 for r in derived if r["check"] == "absent"),
        "unknown": sum(1 for r in derived if r["check"] == "unknown"),
    }
    return tallies["matched"] >= 1 and tallies["absent"] == 0, tallies


def compare_snapshot(by_date: dict[str, list[dict[str, Any]]], validated: list[dict[str, Any]],
                     today: str, window_start: str, window_end: str, config: dict[str, Any],
                     ) -> tuple[list[str], list[str]]:
    """Future rows of the validated week against the snapshot. (differences, info)."""
    differences: list[str] = []
    info: list[str] = []
    past = 0
    for game in validated:
        when = game["derived_date"]
        label = f"{game['sport']}: {game['away']} @ {game['home']} on {when}"
        human = config["human_scoreboard"].format(section=game["section"],
                                                   dates=when.replace("-", ""))
        if when < today:
            past += 1
            continue
        if not (window_start <= when <= window_end):
            info.append(f"- {game['weekday']} “{game['printed']}” → {when}: outside the snapshot "
                        "window; reported for information only.")
            continue
        covered = [
            row for row in by_date.get(when, [])
            if game["away"].casefold() in snapshot_row_text(row)
            and game["home"].casefold() in snapshot_row_text(row)
        ]
        if covered:
            ids = ", ".join(f"`{row['id']}`" for row in covered)
            note = "" if game["check"] in ("match", "flipped") else " (its dated re-check did not complete this run)"
            info.append(f"- {label}: already represented in the snapshot ({ids}){note}.")
            continue
        if game["check"] == "unknown":
            differences.append(
                f"- the grid prints **{label}** and the snapshot does not name it for that date; "
                f"its dated re-check did not complete this run, so review it first: "
                f"[grid]({config['grid']}), [dated check]({human})."
            )
            continue
        on_1050 = [row for row in by_date.get(when, []) if "1050" in row.get("stations", [])]
        if on_1050:
            differences.append(
                f"- the validated grid week prints **{label}** (join {game['time_et']} ET) and "
                f"that date has 1050 rows in the snapshot, but none names this matchup. Re-read "
                f"before changing anything: [grid]({config['grid']}), [dated check]({human})."
            )
        else:
            differences.append(
                f"- the validated grid week prints **{label}** (join {game['time_et']} ET) and the "
                f"snapshot has no 1050 row at all that day. Candidate for a new row after a "
                f"line-by-line read: [grid]({config['grid']}), [dated check]({human})."
            )
    if past:
        info.append(f"- {past} of the grid's dated game lines are already in the past; they are "
                    "ignored by design, because this page advertises its week without dating it.")
    return differences, info


def run(feed: dict[str, Any], today: str, grid_html: str,
        scoreboard: Callable[[str, str], dict[str, Any] | None],
        ) -> tuple[str, list[str], list[str], dict[str, Any]]:
    """Return (status, differences, info, summary). Source failures inside a
    candidate report themselves as "unknown" rows; a page whose shape is not
    the weekly grid raises MonitorError, which main renders as unavailable."""
    config = load_config(feed)
    supported = set(config["sports"])
    parsed = parse_grid(grid_html, supported)
    games = parsed["games"]
    info_all = [
        f"- the grid carries “{line}” without an away @ home matchup; it cannot be dated or "
        "compared by this monitor and needs a human read"
        for line in parsed["unmatchable"]
    ]

    today_date = date.fromisoformat(today)
    this_monday = today_date - timedelta(days=today_date.weekday())
    candidates = []
    for offset in CANDIDATE_WEEK_OFFSETS:
        monday = this_monday + timedelta(days=offset)
        derived = derive_rows(games, config, monday, scoreboard)
        ok, tallies = week_verdict(derived)
        candidates.append({"monday": monday, "derived": derived, "ok": ok, **tallies})

    accepted = [c for c in candidates if c["ok"]]
    if not accepted:
        details = [
            "- no candidate week (last week, this week, next week) is corroborated by ESPN's "
            "dated scoreboard, so the grid's week cannot be established and none of its rows may "
            "be given a date"
        ]
        for c in candidates:
            details.append(
                f"- candidate {c['monday'].isoformat()} → "
                f"{(c['monday'] + timedelta(days=6)).isoformat()}: {c['matched']} match(es), "
                f"{c['absent']} contradiction(s), {c['unknown']} unchecked"
            )
        return "unavailable", [], details + info_all, {}
    if len(accepted) > 1:
        weeks = ", ".join(c["monday"].isoformat() for c in accepted)
        return ("unavailable", [],
                [f"- more than one candidate week is corroborated ({weeks}); the grid cannot be "
                 "dated unambiguously from the dated sources, so no row of it is trusted this run"]
                + info_all, {})

    winner = accepted[0]
    monday = winner["monday"]
    counts = {
        "grid_games": len(games),
        "dated_matches": winner["matched"],
        "unchecked": winner["unknown"],
        "week_monday": monday.isoformat(),
        "week_sunday": (monday + timedelta(days=6)).isoformat(),
    }
    by_date: dict[str, list[dict[str, Any]]] = {}
    for row in feed.get("broadcasts", []):
        if row.get("date"):
            by_date.setdefault(row["date"], []).append(row)
    differences, info = compare_snapshot(by_date, winner["derived"], today,
                                         str(feed["meta"]["window_start"]),
                                         str(feed["meta"]["window_end"]), config)
    info.extend(info_all)
    if differences:
        status = "changed"
    elif winner["unknown"]:
        status = "unavailable"
    else:
        status = "clear"
    return status, differences, info, counts


def make_report(status: str, today: str, differences: list[str], info: list[str],
                counts: dict[str, Any], config: dict[str, Any], snapshot_date: str) -> str:
    checked_at = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M UTC")
    grid_url = config.get("grid", GRID_URL)
    week = ""
    if counts.get("week_monday"):
        week = f"- Derived grid week: **{counts['week_monday']} to {counts['week_sunday']}** (Monday to Sunday)\n"
    header = (
        "# Automated source watch — ESPN Radio weekly grid\n\n"
        f"- Checked: {checked_at}\n"
        f"- Grid page: [{grid_url}]({grid_url})\n"
        f"- Date used for comparison ({config.get('today_zone', 'America/New_York')}): {today}\n"
        f"{week}"
        f"- Published snapshot date: {snapshot_date}\n"
        f"- Status: **{status}**\n\n"
    )
    if status == "clear":
        body = (
            "The weekly grid was dated from its own rows and every future game it prints for "
            f"{counts.get('week_monday', 'the derived week')}–{counts.get('week_sunday', '')} is "
            "already represented in this snapshot. That is a statement about the listing, not "
            "about the air: it does not mean 1050 carried or will carry anything.\n"
        )
    elif status == "changed":
        body = (
            "**The weekly ESPN Radio grid needs review.** Each item below was printed by the grid, "
            "dated by cross-checking it against ESPN's own dated scoreboard, and compared with the "
            "snapshot. Nothing here is a row yet — open the links and re-read line by line:\n\n"
            + "\n".join(differences)
        )
    else:
        body = (
            "**The weekly grid could not be fetched, parsed, or dated this run.** Its state is "
            "unknown; that is not evidence that the schedule changed.\n\n"
            + "\n".join(differences + info)
        )
    tail = ("\n\nDetail:\n\n" + "\n".join(info)) if (info and status != "unavailable") else ""
    return (
        header
        + body
        + tail
        + "\n\nThis monitor is read-only. A grid listing is an ESPN Radio network slot, not a Bay "
        "Area per-game clearance: it does not prove KTCT 1050 carried or will carry a game, and "
        "preemption by a local Giants, 49ers, Stanford or Earthquakes broadcast is routine. It "
        "never edits `data/broadcasts.json`, never publishes GitHub Pages, and never adds a row: "
        "rows come from a human re-reading dated sources and rebuilding with build_feed.py.\n"
    )


def build_scoreboards(config: dict[str, Any],
                      boards: dict[str, Any] | None,
                      ) -> Callable[[str, str], dict[str, Any] | None]:
    """Return scoreboard(sport, day_iso) -> payload-or-None for one run.

    Fixture mode reads saved payloads keyed "SPORT|YYYY-MM-DD". Live mode fetches
    ESPN's dated scoreboard once per (sport, day) and turns any failure into
    None, which the caller counts as an unchecked row, never as a contradiction.
    """
    cache: dict[str, dict[str, Any] | None] = {}

    def scoreboard(sport: str, day: str) -> dict[str, Any] | None:
        key = f"{sport}|{day}"
        if key in cache:
            return cache[key]
        if boards is not None:
            payload = boards.get(key)
            cache[key] = payload if isinstance(payload, dict) else None
            return cache[key]
        entry = config["sports"].get(sport)
        if entry is None:
            cache[key] = None
            return None
        url = config["scoreboard"].format(league_path=entry["league_path"],
                                          dates=day.replace("-", ""))
        try:
            payload = json.loads(fetch(url, "application/json", USER_AGENT_API, timeout=25))
            cache[key] = payload if isinstance(payload, dict) and "events" in payload else None
        except (MonitorError, json.JSONDecodeError) as exc:
            print(f"note: dated scoreboard for {key} could not be read: {exc}", file=sys.stderr)
            cache[key] = None
        return cache[key]

    return scoreboard


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="write the human-readable report to this path")
    parser.add_argument("--github-output", type=Path, help="write status as a GitHub Actions output")
    parser.add_argument("--today", help="override the date used for comparison (intended for tests)")
    parser.add_argument("--input", type=Path,
                        help='JSON file: {"grid_html": ..., "scoreboards": {"SPORT|YYYY-MM-DD": ...}}')
    args = parser.parse_args()

    config: dict[str, Any] = {"grid": GRID_URL, "today_zone": "America/New_York"}
    snapshot_date = "unknown"
    today = args.today or "?"
    try:
        feed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
        snapshot_date = str(feed.get("meta", {}).get("snapshot_date", "unknown"))
        config = load_config(feed)
        if args.today:
            today = args.today
            if date.fromisoformat(today).isoformat() != today:
                raise ValueError("--today must be YYYY-MM-DD")
        else:
            today = datetime.now(ZoneInfo(str(config["today_zone"]))).date().isoformat()
        if args.input:
            fixture = json.loads(args.input.read_text(encoding="utf-8"))
            grid_html = str(fixture["grid_html"])
            boards = fixture.get("scoreboards") or {}
        else:
            grid_html = fetch(str(config["grid"]), "text/html", USER_AGENT_HTML)
            boards = None
        status, differences, info, counts = run(
            feed, today, grid_html, build_scoreboards(config, boards)
        )
    except (MonitorError, OSError, KeyError, json.JSONDecodeError, ValueError) as exc:
        status, differences, info, counts = "unavailable", [f"- {exc}"], [], {}

    report = make_report(status, today, differences, info, counts, config, snapshot_date)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as output:
            output.write(f"espn_week_status={status}\n")
    return 0 if status == "clear" else 2 if status == "changed" else 3


if __name__ == "__main__":
    raise SystemExit(main())
