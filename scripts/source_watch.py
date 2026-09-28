#!/usr/bin/env python3
"""Read-only monitor for the official MLB postseason schedule source.

The monitor compares today's MLB Stats API response with the MLB postseason
rows already in the static snapshot. It never edits broadcasts.json, publishes a
new snapshot, or treats a source change as an approved radio clearance.

Games are matched on the API's own permanent `gamePk`, not on a description
string, so a renamed placeholder ("NL Wild Card #3" -> "PHI/ARI") is reported as
a change to a known game rather than as one game disappearing and another
appearing. A date may be represented in the snapshot by one grouped row or by
several per-game rows; both are aggregated before comparison.

Three outcomes, kept strictly apart like the other monitors:

* **clear** — the response parsed and every future date matched the snapshot.
* **changed** — a real difference. The report names the gamePk, the field that
  moved, and, for a newly published first pitch, the Pacific clock time a human
  would transcribe.
* **unavailable** — the response could not be fetched, parsed or understood.
  Never "unchanged".
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from http.client import HTTPException
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
FEED_PATH = ROOT / "data" / "broadcasts.json"
USER_AGENT = "RADIOSF-source-watch/1.0 (+https://github.com/buffedlizard55-lab/RADIOSF)"
# The builder records the API instant a per-game row's clock time came from.
FIRST_PITCH_RE = re.compile(r"first pitch (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
PACIFIC = ZoneInfo("America/Los_Angeles")


class MonitorError(Exception):
    """The source could not be checked safely."""


def utc_to_pt(iso_utc: str) -> str:
    """Pacific wall clock for an API instant, as a human would transcribe it."""
    if not UTC_RE.fullmatch(iso_utc):
        raise MonitorError(f"The MLB Stats API returned an unparseable gameDate: {iso_utc!r}.")
    local = datetime.fromisoformat(iso_utc.replace("Z", "+00:00")).astimezone(PACIFIC)
    hours, minutes = local.hour, local.minute
    return f"{local.date().isoformat()} {hours % 12 or 12}:{minutes:02d} " \
           f"{'AM' if hours < 12 else 'PM'} PT"


def api_url(feed: dict[str, Any]) -> str:
    for row in feed.get("broadcasts", []):
        if not str(row.get("id", "")).startswith("mlb-post-"):
            continue
        for source in row.get("sources", []):
            if "MLB Stats API postseason endpoint" in source.get("label", ""):
                return source["url"]
    raise MonitorError("The feed has no MLB postseason Stats API source URL.")


def row_first_pitch(row: dict[str, Any]) -> str | None:
    for source in row.get("sources", []):
        match = FIRST_PITCH_RE.search(source.get("label", ""))
        if match:
            return match.group(1)
    return None


def expected_schedule(feed: dict[str, Any], today: str) -> dict[str, dict[str, Any]]:
    """Group the snapshot's MLB postseason rows by date, keyed on gamePk."""
    expected: dict[str, dict[str, Any]] = {}
    for row in feed.get("broadcasts", []):
        if not str(row.get("id", "")).startswith("mlb-post-") or not row.get("date"):
            continue
        if row["date"] < today:
            continue
        details = row.get("game_details")
        if not isinstance(details, list) or not details:
            raise MonitorError(f"The snapshot row {row.get('id')} has no MLB matchup baseline.")

        first_pitch = row_first_pitch(row)
        if first_pitch and len(details) != 1:
            raise MonitorError(
                f"The snapshot row {row.get('id')} cites a first pitch but groups "
                f"{len(details)} games; a clock time belongs to one game."
            )
        if bool(first_pitch) != bool(row.get("start_pt")):
            raise MonitorError(
                f"The snapshot row {row.get('id')} has a start time and a cited first pitch "
                "that do not agree about existing."
            )

        bucket = expected.setdefault(row["date"], {"row_ids": [], "games": {}, "count": 0})
        bucket["row_ids"].append(row["id"])
        for item in details:
            if not isinstance(item, dict):
                raise MonitorError(f"The snapshot row {row.get('id')} has a malformed game slot.")
            pk = item.get("game_pk")
            if not isinstance(pk, int):
                raise MonitorError(
                    f"The snapshot row {row.get('id')} has a game slot without the API's gamePk."
                )
            if pk in bucket["games"]:
                raise MonitorError(f"The snapshot lists gamePk {pk} twice on {row['date']}.")
            for key in ("description", "away", "home"):
                if not isinstance(item.get(key), str) or not item[key].strip():
                    raise MonitorError(
                        f"The snapshot row {row.get('id')} has an empty MLB {key} for gamePk {pk}."
                    )
            bucket["games"][pk] = {
                "description": item["description"].strip(),
                "away": item["away"].strip(),
                "home": item["home"].strip(),
                "venue": str(item.get("venue") or "").strip(),
                "conditional": bool(item.get("conditional")),
                "first_pitch": first_pitch,
                "start_pt": row.get("start_pt"),
                "row_id": row["id"],
            }
            bucket["count"] += 1
    return expected


def observed_schedule(document: dict[str, Any], today: str) -> dict[str, dict[str, Any]]:
    if not isinstance(document, dict):
        raise MonitorError("The MLB Stats API response is not a JSON object.")
    observed: dict[str, dict[str, Any]] = {}
    dates = document.get("dates")
    if not isinstance(dates, list):
        raise MonitorError("The MLB Stats API response has no dates list.")

    for date_block in dates:
        if not isinstance(date_block, dict):
            raise MonitorError("The MLB Stats API returned an invalid date block.")
        games = date_block.get("games")
        if not isinstance(games, list):
            raise MonitorError("The MLB Stats API returned an invalid games list.")
        for game in games:
            if not isinstance(game, dict):
                raise MonitorError("The MLB Stats API returned an invalid game entry.")
            game_date = game.get("officialDate") or date_block.get("date")
            if not isinstance(game_date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", game_date):
                raise MonitorError("The MLB Stats API returned a game without an ISO date.")
            try:
                if date.fromisoformat(game_date).isoformat() != game_date:
                    raise ValueError
            except ValueError as exc:
                raise MonitorError(f"The MLB Stats API returned an invalid date: {game_date}.") from exc
            pk = game.get("gamePk")
            if not isinstance(pk, int):
                raise MonitorError(f"The MLB Stats API returned no integer gamePk for {game_date}.")
            if game_date < today:
                continue
            description = game.get("description")
            if not isinstance(description, str) or not description.strip():
                raise MonitorError(f"The MLB Stats API returned no description for {game_date}.")
            game_date_utc = game.get("gameDate")
            if not isinstance(game_date_utc, str) or not UTC_RE.fullmatch(game_date_utc):
                raise MonitorError(f"The MLB Stats API returned no valid gameDate for gamePk {pk}.")
            # The live API nests startTimeTBD inside "status". A top-level value
            # remains a fallback for older saved API responses.
            status_block = game.get("status") if isinstance(game.get("status"), dict) else {}
            start_time_tbd = status_block.get("startTimeTBD", game.get("startTimeTBD"))
            if not isinstance(start_time_tbd, bool):
                raise MonitorError(f"The MLB Stats API returned no boolean startTimeTBD for {game_date}.")
            teams = game.get("teams")
            away = teams.get("away", {}).get("team", {}).get("name") if isinstance(teams, dict) else None
            home = teams.get("home", {}).get("team", {}).get("name") if isinstance(teams, dict) else None
            if not isinstance(away, str) or not away.strip() or not isinstance(home, str) or not home.strip():
                raise MonitorError(f"The MLB Stats API returned no away/home team names for {game_date}.")
            venue_block = game.get("venue") if isinstance(game.get("venue"), dict) else {}
            venue = venue_block.get("name")
            if not isinstance(venue, str) or not venue.strip():
                raise MonitorError(f"The MLB Stats API returned no venue for gamePk {pk}.")
            if_necessary = game.get("ifNecessary")
            if if_necessary not in ("Y", "N"):
                raise MonitorError(f"The MLB Stats API returned no valid ifNecessary marker for {game_date}.")

            bucket = observed.setdefault(game_date, {"count": 0, "games": {}})
            if pk in bucket["games"]:
                raise MonitorError(f"The MLB Stats API returned gamePk {pk} twice on {game_date}.")
            bucket["count"] += 1
            bucket["games"][pk] = {
                "description": description.strip(),
                "away": away.strip(),
                "home": home.strip(),
                "venue": venue.strip(),
                "conditional": if_necessary == "Y",
                "start_time_tbd": start_time_tbd,
                "game_date_utc": game_date_utc,
            }
    return observed


FIELDS = (
    ("description", "description"),
    ("away", "away team"),
    ("home", "home team"),
    ("venue", "venue"),
    ("conditional", "if-necessary marker"),
)


def show_game(pk: int, game: dict[str, Any]) -> str:
    status = " (if necessary)" if game.get("conditional") else ""
    return f"gamePk {pk}, {game.get('description')}: {game.get('away')} at {game.get('home')}{status}"


def compare(
    expected: dict[str, dict[str, Any]], observed: dict[str, dict[str, Any]]
) -> list[str]:
    differences: list[str] = []
    for game_date in sorted(set(expected) | set(observed)):
        before = expected.get(game_date)
        after = observed.get(game_date)
        if before is None:
            listed = "; ".join(
                f"{game['description']}: {game['away']} at {game['home']}"
                for game in after["games"].values()
            )
            differences.append(
                f"- **{game_date}**: the API now lists {after['count']} game(s) "
                f"({listed}), but this snapshot has no row."
            )
            continue
        if after is None:
            differences.append(
                f"- **{game_date}**: the snapshot records {before['count']} game(s) "
                f"in {len(before['row_ids'])} row(s), but the API now has none."
            )
            continue

        date_notes: list[str] = []
        if before["count"] != after["count"]:
            date_notes.append(
                f"game count changed from {before['count']} in the snapshot to {after['count']} in the API."
            )

        for pk in sorted(set(before["games"]) - set(after["games"])):
            date_notes.append(
                f"the API no longer returns {show_game(pk, before['games'][pk])}."
            )
        for pk in sorted(set(after["games"]) - set(before["games"])):
            date_notes.append(
                f"the API now returns {show_game(pk, after['games'][pk])}, which this snapshot "
                f"does not list (row would be `mlb-post-{pk}`)."
            )

        newly_timed: list[str] = []
        reverted: list[str] = []
        for pk in sorted(set(before["games"]) & set(after["games"])):
            was, now = before["games"][pk], after["games"][pk]
            for key, label in FIELDS:
                if was[key] != now[key]:
                    date_notes.append(
                        f"{label} changed for gamePk {pk} ({was['description']}): "
                        f"{was[key]!r} in the snapshot, {now[key]!r} in the API."
                    )
            if was["first_pitch"] is None:
                if not now["start_time_tbd"]:
                    newly_timed.append(
                        f"gamePk {pk} ({now['description']}) first pitch "
                        f"{utc_to_pt(now['game_date_utc'])} — API {now['game_date_utc']}"
                    )
            elif now["start_time_tbd"]:
                reverted.append(
                    f"gamePk {pk} ({now['description']}) was {was['first_pitch']} "
                    f"({was['start_pt']} PT in the snapshot) but the API now marks it TBD"
                )
            elif was["first_pitch"] != now["game_date_utc"]:
                date_notes.append(
                    f"first pitch changed for gamePk {pk} ({now['description']}): the snapshot "
                    f"was built from {was['first_pitch']} ({was['start_pt']} PT), the API now "
                    f"says {now['game_date_utc']} ({utc_to_pt(now['game_date_utc'])})."
                )

        if newly_timed:
            date_notes.append(
                f"the API now supplies a start time for {len(newly_timed)} game(s) the snapshot "
                "still shows as TBD: " + "; ".join(newly_timed) + "."
            )
        if reverted:
            date_notes.append(
                f"the API has withdrawn a start time the snapshot shows: " + "; ".join(reverted) + "."
            )

        if date_notes:
            differences.append(
                f"- **{game_date}** ({len(before['row_ids'])} snapshot row(s)):\n" +
                "\n".join(f"  - {note}" for note in date_notes)
            )
    return differences


def fetch_json(url: str, timeout: int = 25) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise MonitorError(f"MLB Stats API returned HTTP {response.status}.")
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, HTTPException, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MonitorError(f"Could not fetch or parse the MLB Stats API response: {exc}") from exc
    if not isinstance(payload, dict):
        raise MonitorError("The MLB Stats API response is not a JSON object.")
    return payload


def local_today() -> str:
    return datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()


def make_report(
    status: str, today: str, url: str, details: list[str], snapshot_date: str = "unknown"
) -> str:
    checked_at = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M UTC")
    if status == "clear":
        body = "No differences found for future postseason dates in the monitored MLB Stats API schedule."
    elif status == "changed":
        body = (
            "**Schedule drift detected.** These source differences need line-by-line review before "
            "any change is made to the published snapshot:\n\n" + "\n".join(details)
        )
    else:
        body = (
            "**The check could not be completed.** The schedule state is unknown; this is not evidence "
            "that the source or snapshot changed.\n\n" + "\n".join(details)
        )
    return (
        "# Automated source watch — MLB postseason\n\n"
        f"- Checked: {checked_at}\n"
        f"- Pacific date used for comparison: {today}\n"
        f"- Source: [{url}]({url})\n"
        f"- Published snapshot date: {snapshot_date}\n\n"
        f"{body}\n\n"
        "This is a read-only monitor of one machine-readable schedule source. Games are matched on "
        "the API's own `gamePk`, and the comparison covers each game's description, away and home "
        "labels, venue, if-necessary marker and first pitch. It does not confirm a Bay Area "
        "station's per-game clearance, check all six stations, change `data/broadcasts.json`, or "
        "publish a new GitHub Pages snapshot. Open the source and review affected rows and radio "
        "rights manually before updating the curated feed.\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="write the human-readable report to this path")
    parser.add_argument("--github-output", type=Path, help="write status/report path as GitHub Actions outputs")
    parser.add_argument("--today", help="override the Pacific date (intended for tests)")
    parser.add_argument("--input", type=Path, help="read a saved API response instead of fetching")
    args = parser.parse_args()

    today = args.today or local_today()
    snapshot_date = "unknown"
    try:
        if date.fromisoformat(today).isoformat() != today:
            raise ValueError(f"Date must use YYYY-MM-DD, got {today!r}.")
        feed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
        snapshot_date = str(feed.get("meta", {}).get("snapshot_date", "unknown"))
        url = api_url(feed)
        expected = expected_schedule(feed, today)
        payload = json.loads(args.input.read_text(encoding="utf-8")) if args.input else fetch_json(url)
        observed = observed_schedule(payload, today)
        details = compare(expected, observed)
        status = "changed" if details else "clear"
    except (MonitorError, OSError, json.JSONDecodeError, ValueError) as exc:
        status = "unavailable"
        details = [f"- {exc}"]
        try:
            feed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
            snapshot_date = str(feed.get("meta", {}).get("snapshot_date", "unknown"))
            url = api_url(feed)
        except Exception:
            url = "https://statsapi.mlb.com/api/v1/schedule/postseason?season=2026&sportId=1"

    report = make_report(status, today, url, details, snapshot_date)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as output:
            output.write(f"status={status}\n")
            if args.report:
                output.write(f"report={args.report}\n")
    return 0 if status == "clear" else 2 if status == "changed" else 3


if __name__ == "__main__":
    raise SystemExit(main())
