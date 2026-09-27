#!/usr/bin/env python3
"""Read-only monitor for the four Westwood One upcoming-broadcast grids.

Westwood One is the rights holder behind most of this snapshot's `indicated`
rows: 63 NFL rows, 11 college football rows and 5 U.S. Soccer rows, plus the
college basketball grid that is currently empty and is the largest hole in the
winter half of the window. Each sport's grid is served from one machine-readable
widget, so the whole block can be watched for drift instead of being re-read by
hand.

Like the MLB monitor, this script never edits data/broadcasts.json, never
publishes a new GitHub Pages snapshot, and never treats a grid change as an
approved Bay Area clearance. It answers one question: does the list of events the
rights holder is currently advertising still match the list this snapshot was
built from?

Two failure modes are deliberately kept apart:

  * A widget that should have events and returns none, or a page whose expected
    heading cannot be found, is reported as **unavailable**. The state of the
    schedule is then unknown. It is never reported as "no drift", because a
    parser that silently matches nothing would look exactly like a source that
    had not changed.
  * A real difference is reported as **changed**, split into events the grid now
    lists that the snapshot lacks, snapshot rows for future dates the grid no
    longer lists, and events whose printed title differs.

The grid pages carry a second, generic "Upcoming Broadcasts" widget below the
sport-specific one. Only anchors under the heading named by the widget are
counted, so a U.S. Soccer match appearing in the NFL page's generic strip cannot
be mistaken for a new NFL row.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from html.parser import HTMLParser
from http.client import HTTPException
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
FEED_PATH = ROOT / "data" / "broadcasts.json"
USER_AGENT = "RADIOSF-source-watch/1.0 (+https://github.com/buffedlizard55-lab/RADIOSF)"
EVENT_HREF_RE = re.compile(r"/events/(\d+)")
TITLE_PREFIX = "Westwood One: "
# Per request, so one fetch per widget returns the whole grid instead of a page.
GRID_LIMIT = 100
# UI chrome that links to an event page but is not the event's printed title.
CHROME_TEXT = {"full details", "full details arrow upright", "tickets", "watch"}


class MonitorError(Exception):
    """The source could not be checked safely."""


class WidgetError(MonitorError):
    """One widget could not be checked safely; the others may still be fine."""


def normalise(text: str) -> str:
    return " ".join(str(text).split())


class GridParser(HTMLParser):
    """Collect event ids and their printed titles, grouped by the heading above them.

    Each event is linked twice on a grid page — once around its artwork and once
    around its title, with a "Full Details" link after that — and all three
    anchors share one href. Every candidate string seen for an event id is kept,
    the known chrome is dropped, and the longest survivor is taken as the title.
    An event whose only strings are chrome yields an empty title, which is
    reported as such rather than guessed at.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sections: dict[str, list[str]] = {}
        self.candidates: dict[str, list[str]] = {}
        self._heading_depth = 0
        self._heading_parts: list[str] = []
        self._anchor_stack: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._heading_depth += 1
            self._heading_parts = []
            return
        if tag != "a":
            return
        href = ""
        for name, value in attrs:
            if name == "href" and value:
                href = value
                break
        match = EVENT_HREF_RE.search(href)
        if not match:
            return
        event_id = match.group(1)
        heading = normalise("".join(self._heading_parts))
        self._anchor_stack.append((event_id, heading))
        self.sections.setdefault(heading, [])
        if event_id not in self.sections[heading]:
            self.sections[heading].append(event_id)
        self.candidates.setdefault(event_id, [])

    def handle_endtag(self, tag: str) -> None:
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._heading_depth:
            self._heading_depth -= 1
            # Register the heading even when its section holds no anchors, so an
            # empty grid ("No upcoming events") is distinguishable from a page
            # whose grid could not be found at all.
            heading = normalise("".join(self._heading_parts))
            if heading:
                self.sections.setdefault(heading, [])
        elif tag == "a" and self._anchor_stack:
            self._anchor_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._heading_depth:
            self._heading_parts.append(data)
        for event_id, heading in self._anchor_stack:
            chunk = normalise(data)
            if chunk:
                self.candidates.setdefault(event_id, []).append(chunk)
                self.sections.setdefault(heading, [])

    def events(self, heading: str) -> dict[str, str]:
        wanted = normalise(heading)
        if wanted not in self.sections:
            raise WidgetError(
                f"the page has no \u201c{wanted}\u201d heading, so its grid could not be located"
            )
        out: dict[str, str] = {}
        for event_id in self.sections[wanted]:
            strings = [
                text for text in self.candidates.get(event_id, [])
                if text.lower() not in CHROME_TEXT
            ]
            out[event_id] = max(strings, key=len) if strings else ""
        return out


def grid_url(endpoint: str, widget: dict[str, Any]) -> str:
    return (
        f"{endpoint}?id={widget['widget']}&range=current&offset=0&limit={GRID_LIMIT}"
        f"&timezone=America/New_York&widgetTitle={widget['title']}"
    )


def fetch_html(url: str, timeout: int = 25) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise WidgetError(f"returned HTTP {response.status}")
            return response.read().decode("utf-8", errors="replace")
    except WidgetError:
        raise
    except (HTTPError, URLError, TimeoutError, OSError, HTTPException, UnicodeDecodeError) as exc:
        raise WidgetError(f"could not be fetched: {exc}") from exc


def parse_grid(html: str, widget: dict[str, Any]) -> dict[str, str]:
    parser = GridParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:  # a malformed page must not read as an empty grid
        raise WidgetError(f"could not be parsed: {exc}") from exc
    heading = normalise(widget["title"]).replace("+", " ")
    return parser.events(heading)


def expected_events(feed: dict[str, Any], prefix: str) -> dict[str, dict[str, str]]:
    expected: dict[str, dict[str, str]] = {}
    for row in feed.get("broadcasts", []):
        row_id = str(row.get("id", ""))
        if not row_id.startswith(prefix):
            continue
        event_id = row_id[len(prefix):]
        if not event_id.isdigit():
            raise MonitorError(f"{row_id} does not end in a Westwood One event id.")
        if event_id in expected:
            raise MonitorError(f"The snapshot has duplicate rows for Westwood One event {event_id}.")
        title = str(row.get("title", ""))
        if title.startswith(TITLE_PREFIX):
            title = title[len(TITLE_PREFIX):]
        expected[event_id] = {"title": normalise(title), "date": row.get("date") or ""}
    return expected


def compare_widget(
    widget: dict[str, Any],
    expected: dict[str, dict[str, str]],
    observed: dict[str, str],
    merged: set[str],
    today: str,
) -> list[str]:
    differences: list[str] = []
    sport = widget["sport"]

    for event_id in sorted(set(observed) - set(expected) - merged):
        title = observed[event_id] or "(the grid printed no title this run)"
        differences.append(
            f"- **{sport}**: the grid now lists event {event_id}, \u201c{title}\u201d, "
            f"but this snapshot has no row for it."
        )

    for event_id in sorted(set(expected) - set(observed)):
        row = expected[event_id]
        # A grid only advertises upcoming events, so a past row dropping off is
        # expected and is not drift.
        if row["date"] and row["date"] < today:
            continue
        when = row["date"] or "an undated row"
        differences.append(
            f"- **{sport}**: the snapshot has \u201c{row['title']}\u201d on {when}, "
            f"but the grid no longer lists event {event_id}."
        )

    for event_id in sorted(set(expected) & set(observed)):
        before = expected[event_id]["title"]
        after = observed[event_id]
        if not after or not before or before == after:
            continue
        differences.append(
            f"- **{sport}**: event {event_id} is printed as \u201c{after}\u201d on the grid "
            f"but as \u201c{before}\u201d in the snapshot."
        )
    return differences


def load_config(feed: dict[str, Any]) -> tuple[str, list[dict[str, Any]], set[str]]:
    watch = feed.get("meta", {}).get("wwo_watch")
    if not isinstance(watch, dict):
        raise MonitorError("The feed has no meta.wwo_watch block; rebuild it with build_feed.py.")
    endpoint = watch.get("endpoint")
    widgets = watch.get("widgets")
    if not isinstance(endpoint, str) or not endpoint.startswith("https://"):
        raise MonitorError("meta.wwo_watch.endpoint is missing or is not an https URL.")
    if not isinstance(widgets, list) or not widgets:
        raise MonitorError("meta.wwo_watch.widgets is missing or empty.")
    for widget in widgets:
        for key in ("widget", "prefix", "sport", "title"):
            if not widget.get(key):
                raise MonitorError(f"A Westwood One widget entry is missing {key!r}.")
    merged = {str(value) for value in watch.get("merged_nfl_event_ids", [])}
    return endpoint, widgets, merged


def run(feed: dict[str, Any], today: str, pages: dict[str, str] | None) -> tuple[str, list[str], list[str]]:
    """Return (status, difference lines, detail lines)."""
    endpoint, widgets, merged = load_config(feed)
    differences: list[str] = []
    details: list[str] = []
    failures: list[str] = []

    for widget in widgets:
        expected = expected_events(feed, widget["prefix"])
        url = grid_url(endpoint, widget)
        try:
            html = pages[widget["widget"]] if pages is not None else fetch_html(url)
            observed = parse_grid(html, widget)
        except WidgetError as exc:
            failures.append(widget["sport"])
            details.append(
                f"- **{widget['sport']}** ([grid]({url})): not checked, {exc}. "
                f"Its {len(expected)} snapshot row(s) are unverified this run."
            )
            continue

        if not observed and expected:
            # A grid that advertises events cannot legitimately come back empty.
            # Treat it as a failed check rather than as a source that deleted
            # every game.
            failures.append(widget["sport"])
            details.append(
                f"- **{widget['sport']}** ([grid]({url})): not checked. The grid returned no "
                f"events at all, which contradicts the {len(expected)} snapshot row(s) built "
                f"from it."
            )
            continue

        differences.extend(compare_widget(widget, expected, observed, merged, today))
        state = "empty, as the snapshot expects" if not observed else f"{len(observed)} event(s)"
        details.append(
            f"- **{widget['sport']}** ([grid]({url})): checked, {state}; "
            f"{len(expected)} snapshot row(s) compared."
        )

    # A difference outranks a failed check: something concrete needs review.
    if differences:
        status = "changed"
    elif failures:
        status = "unavailable"
    else:
        status = "clear"
    return status, differences, details


def make_report(
    status: str, today: str, details: list[str], differences: list[str], snapshot_date: str
) -> str:
    checked_at = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M UTC")
    if status == "clear":
        body = (
            "Every checked Westwood One grid still lists the same events as this snapshot, "
            "with the same printed titles.\n\n" + "\n".join(details)
        )
    elif status == "changed":
        body = (
            "**Grid drift detected.** These differences need line-by-line review against the "
            "source before any change is made to the published snapshot:\n\n"
            + "\n".join(differences)
            + ("\n\nChecks that did not complete:\n\n" + "\n".join(details) if any(
                "not checked" in line for line in details) else "")
        )
    else:
        body = (
            "**The check could not be completed for at least one grid.** The schedule state is "
            "unknown for those rows; this is not evidence that the source or the snapshot "
            "changed.\n\n" + "\n".join(details)
        )
    return (
        "# Automated source watch — Westwood One grids\n\n"
        f"- Checked: {checked_at}\n"
        f"- Pacific date used for comparison: {today}\n"
        f"- Published snapshot date: {snapshot_date}\n"
        f"- Status: **{status}**\n\n"
        f"{body}\n\n"
        "This is a read-only monitor of the rights holder's own upcoming-broadcast grids. It does "
        "not confirm a Bay Area station's per-game clearance, check the six stations' own pages, "
        "change `data/broadcasts.json`, or publish a new GitHub Pages snapshot. Open the grid, "
        "re-read the affected rows, and rebuild the curated feed by hand.\n"
    )


def local_today() -> str:
    return datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="write the human-readable report to this path")
    parser.add_argument("--github-output", type=Path, help="write status as a GitHub Actions output")
    parser.add_argument("--today", help="override the Pacific date (intended for tests)")
    parser.add_argument("--input", type=Path,
                        help="read saved grid HTML from this JSON file instead of fetching")
    args = parser.parse_args()

    today = args.today or local_today()
    snapshot_date = "unknown"
    try:
        if date.fromisoformat(today).isoformat() != today:
            raise ValueError(f"Date must use YYYY-MM-DD, got {today!r}.")
        feed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
        snapshot_date = str(feed.get("meta", {}).get("snapshot_date", "unknown"))
        pages = json.loads(args.input.read_text(encoding="utf-8")) if args.input else None
        if pages is not None and not isinstance(pages, dict):
            raise MonitorError("--input must be a JSON object keyed by widget id.")
        status, differences, details = run(feed, today, pages)
    except (MonitorError, OSError, json.JSONDecodeError, ValueError) as exc:
        status = "unavailable"
        differences = []
        details = [f"- {exc}"]

    report = make_report(status, today, details, differences, snapshot_date)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as output:
            output.write(f"wwo_status={status}\n")
    return 0 if status == "clear" else 2 if status == "changed" else 3


if __name__ == "__main__":
    raise SystemExit(main())
