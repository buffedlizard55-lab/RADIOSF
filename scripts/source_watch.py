#!/usr/bin/env python3
"""Read-only monitor for the official MLB postseason schedule source.

The monitor compares today's MLB Stats API response with the MLB postseason
rows already in the static snapshot. It never edits broadcasts.json, publishes a
new snapshot, or treats a source change as an approved radio clearance.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
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
DESCRIPTION_RE = re.compile(r"Stats API descriptions for this date: (.*?)\. First pitch", re.DOTALL)
COUNT_RE = re.compile(r":\s*(\d+)\s+game\(s\),\s*startTimeTBD\s+(true|false)\b", re.I)


class MonitorError(Exception):
    """The source could not be checked safely."""


def api_url(feed: dict[str, Any]) -> str:
    for row in feed.get("broadcasts", []):
        if not str(row.get("id", "")).startswith("mlb-post-"):
            continue
        for source in row.get("sources", []):
            if "MLB Stats API postseason endpoint" in source.get("label", ""):
                return source["url"]
    raise MonitorError("The feed has no MLB postseason Stats API source URL.")


def expected_schedule(feed: dict[str, Any], today: str) -> dict[str, dict[str, Any]]:
    expected: dict[str, dict[str, Any]] = {}
    for row in feed.get("broadcasts", []):
        if not str(row.get("id", "")).startswith("mlb-post-") or not row.get("date"):
            continue
        if row["date"] < today:
            continue
        if row["date"] in expected:
            raise MonitorError(f"The snapshot has duplicate MLB postseason rows for {row['date']}.")

        api_source = next((
            source for source in row.get("sources", [])
            if "MLB Stats API postseason endpoint" in source.get("label", "")
        ), None)
        if not api_source:
            raise MonitorError(f"The snapshot row {row.get('id')} is missing its Stats API source label.")
        count_match = COUNT_RE.search(api_source.get("label", ""))
        description_match = DESCRIPTION_RE.search(row.get("notes", ""))
        if not count_match or not description_match:
            raise MonitorError(f"Could not read the recorded MLB baseline for {row.get('id')}.")
        descriptions = [part.strip() for part in description_match.group(1).split("; ") if part.strip()]
        count = int(count_match.group(1))
        if len(descriptions) != count:
            raise MonitorError(f"Recorded game count and descriptions disagree for {row['date']}.")
        expected[row["date"]] = {
            "count": count,
            "descriptions": Counter(descriptions),
            "all_start_times_tbd": count_match.group(2).lower() == "true",
            "row_id": row["id"],
        }
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
            if game_date < today:
                continue
            description = game.get("description")
            if not isinstance(description, str) or not description.strip():
                raise MonitorError(f"The MLB Stats API returned no description for {game_date}.")
            if not isinstance(game.get("startTimeTBD"), bool):
                raise MonitorError(f"The MLB Stats API returned no boolean startTimeTBD for {game_date}.")
            item = observed.setdefault(game_date, {
                "count": 0,
                "descriptions": Counter(),
                "start_time_tbd": [],
            })
            item["count"] += 1
            item["descriptions"][description.strip()] += 1
            item["start_time_tbd"].append(game["startTimeTBD"])
    return observed


def compare(
    expected: dict[str, dict[str, Any]], observed: dict[str, dict[str, Any]]
) -> list[str]:
    differences: list[str] = []
    for game_date in sorted(set(expected) | set(observed)):
        before = expected.get(game_date)
        after = observed.get(game_date)
        if before is None:
            differences.append(
                f"- **{game_date}**: the API now lists {after['count']} game(s), but this snapshot has no row."
            )
            continue
        if after is None:
            differences.append(
                f"- **{game_date}**: the snapshot records {before['count']} game(s), but the API now has none."
            )
            continue
        if before["count"] != after["count"]:
            differences.append(
                f"- **{game_date}**: game count changed from {before['count']} in the snapshot to {after['count']} in the API."
            )
        if before["descriptions"] != after["descriptions"]:
            removed = list((before["descriptions"] - after["descriptions"]).elements())
            added = list((after["descriptions"] - before["descriptions"]).elements())
            if removed:
                differences.append(f"  - No longer returned: {'; '.join(removed)}.")
            if added:
                differences.append(f"  - Newly returned or renamed: {'; '.join(added)}.")
        if before["all_start_times_tbd"] and not all(after["start_time_tbd"]):
            newly_timed = sum(1 for value in after["start_time_tbd"] if not value)
            differences.append(
                f"- **{game_date}**: the API now supplies a start time for {newly_timed} game(s); the snapshot still shows TBD."
            )
        elif not before["all_start_times_tbd"] and any(after["start_time_tbd"]):
            differences.append(
                f"- **{game_date}**: the API now marks at least one start time TBD; compare with the snapshot."
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
        "This is a read-only monitor of one machine-readable schedule source. It does not confirm a "
        "Bay Area station's per-game clearance, check all six stations, change `data/broadcasts.json`, "
        "or publish a new GitHub Pages snapshot. Open the source and review affected rows and radio "
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
