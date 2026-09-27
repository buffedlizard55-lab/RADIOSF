#!/usr/bin/env python3
"""Read-only monitor for the NBA's official 2026-27 ESPN Radio schedule PDF.

The PDF at `meta.espn_watch.pdf` is the source of every `nba-espn-` row in the
snapshot. This monitor re-reads it every day and compares the printed rows with
what the snapshot claims. It never edits broadcasts.json, never publishes a
snapshot, and never treats "ESPN Radio carries it" as a Bay Area clearance.

Three outcomes, kept strictly apart:

* **clear** — the PDF parsed into the expected shape and every in-window row
  matches the snapshot's date, matchup and printed ET time.
* **changed** — the PDF parsed, but a date, matchup, printed time, row count or
  Cup marker differs from what the snapshot was built from. A human re-reads the
  PDF and rebuilds.
* **unavailable** — the PDF could not be fetched, or its text parsed to no rows
  at all. The state is unknown. That is never reported as "no drift", because a
  text extractor that silently returns nothing would otherwise look like a
  source that had not changed.

Usage:
    python3 scripts/espn_watch.py --input scripts/fixtures/espn_radio_nba_2026-08-13.txt
    python3 scripts/espn_watch.py --report "$RUNNER_TEMP/espn.md"
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from datetime import datetime
from http.client import HTTPException
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
FEED_PATH = ROOT / "data" / "broadcasts.json"
USER_AGENT = "RADIOSF-source-watch/1.0 (+https://github.com/buffedlizard55-lab/RADIOSF)"
DEFAULT_PDF = (
    "https://ak-static.cms.nba.com/wp-content/uploads/sites/46/2026/08/"
    "2026-27-ESPN-Radio-Schedule.pdf"
)

DAY_RE = re.compile(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\.$")
DATE_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{2})$")
CLOCK_RE = re.compile(r"^(\d{1,2}):(\d{2})$")
MERIDIEM_RE = re.compile(r"^(AM|PM)$")
TBD_RE = re.compile(r"^TBD([*^])?$")

# Every franchise string the PDF prints, longest first, so "LA Lakers" and
# "Oklahoma City" are matched whole rather than one word at a time. A string
# outside this list is a parse failure, not a silent skip: an unknown team
# reports the check as changed or unavailable and a human reads the PDF.
NBA_NAMES = sorted(
    [
        "Philadelphia", "New York", "Cleveland", "Golden State", "San Antonio",
        "Houston", "Denver", "Miami", "Boston", "LA Lakers", "Minnesota",
        "Milwaukee", "Oklahoma City", "Dallas", "Detroit", "Indiana",
    ],
    key=len,
    reverse=True,
)

# What the PDF printed when it was read on 2026-09-27. A different shape is a
# change to report, never a number to quietly move.
EXPECTED_DATED_ROWS = 27          # 26 dated games plus the dated Cup championship line
EXPECTED_IN_WINDOW_ROWS = 17      # of those, the ones this snapshot has rows for
# The PDF repeats its marker in every cell of a TBD line: five "*" cells on each
# of the two semifinal lines, three "^" cells on the championship line. Exact
# counts, because a layout that merges cells is itself something to re-read.
EXPECTED_MARKERS = {"*": 10, "^": 3}
CUP_FOOTNOTES = ("semifinals", "championship")

OUT_OF_WINDOW_NOTE = (
    "The PDF prints nine further dated games from 2027-03-06 to 2027-04-08. They fall outside "
    "this snapshot's window, so they are reported here for information and no rows were made from "
    "them."
)


class MonitorError(Exception):
    """The source could not be checked safely."""


def et_to_pt(et: str) -> str:
    """Convert a printed ET clock to 24-hour Pacific. Refuses to wrap a day."""
    hhmm, meridiem = et.split()
    hour, minute = (int(part) for part in hhmm.split(":"))
    if meridiem == "PM" and hour != 12:
        hour += 12
    if meridiem == "AM" and hour == 12:
        hour = 0
    total = hour * 60 + minute - 180
    if total < 0 or total >= 24 * 60:
        raise MonitorError(f"Printed ET time {et} crosses midnight; handle it explicitly.")
    return f"{total // 60:02d}:{total % 60:02d}"


def _name_at(tokens: list[str], index: int) -> str | None:
    """Longest printed franchise string starting at `index`, or None."""
    for candidate in NBA_NAMES:
        words = candidate.split()
        if tokens[index:index + len(words)] == words:
            return candidate
    return None


def parse_rows(text: str) -> dict[str, Any]:
    """Parse the PDF's own row grammar out of extracted text.

    Tokens are read in stream order: a PDF text extractor may lay a table out
    row by row or column by column, so this does not depend on newlines. A dated
    row is the token sequence weekday, US date, away, home, and then either a
    clock time plus AM/PM or TBD markers. A dated row whose names are both TBD
    markers is the Cup championship line; the two undated TBD lines are counted
    by marker instead of by row, because a table extractor may repeat a marker
    once per cell.
    """
    tokens = [token for token in re.split(r"\s+", text) if token]
    rows: list[dict[str, Any]] = []
    index = 0
    while index < len(tokens):
        day_match = DAY_RE.match(tokens[index])
        if not day_match or index + 1 >= len(tokens):
            index += 1
            continue
        date_match = DATE_RE.match(tokens[index + 1])
        away = _name_at(tokens, index + 2)
        tbd_away = TBD_RE.match(tokens[index + 2]) if index + 2 < len(tokens) else None
        if not date_match or not (away or tbd_away):
            index += 1
            continue
        cursor = index + 2
        if away:
            # Both cells can be multi-word ("LA Lakers", "Oklahoma City"), so
            # advance by the words actually consumed rather than by cells.
            away_words = len(away.split())
            home = _name_at(tokens, cursor + away_words)
            if not home:
                index += 1
                continue
            cursor += away_words + len(home.split())
        else:
            home_match = TBD_RE.match(tokens[cursor + 1]) if cursor + 1 < len(tokens) else None
            if not home_match:
                index += 1
                continue
            away, home = tbd_away.group(0), home_match.group(0)
            cursor += 2
        month, day_of_month, year = (int(part) for part in date_match.groups())
        iso = f"{2000 + year:04d}-{month:02d}-{day_of_month:02d}"
        if datetime.fromisoformat(iso).strftime("%a") != day_match.group(1):
            raise MonitorError(
                f"The PDF row {iso} prints {day_match.group(1)} but the calendar says "
                f"{datetime.fromisoformat(iso).strftime('%a')}."
            )
        clock_match = CLOCK_RE.match(tokens[cursor]) if cursor < len(tokens) else None
        meridiem_match = MERIDIEM_RE.match(tokens[cursor + 1]) if cursor + 1 < len(tokens) else None
        if clock_match and meridiem_match:
            et = f"{int(clock_match.group(1))}:{clock_match.group(2)} {meridiem_match.group(1)}"
            rows.append({"kind": "game", "date": iso, "away": away, "home": home, "et": et})
            index = cursor + 2
            continue
        if TBD_RE.match(away) and TBD_RE.match(home):
            rows.append({"kind": "tbd-dated", "date": iso, "away": away, "home": home, "et": None})
            index = cursor
            continue
        index += 1

    markers = {"*": len(re.findall(r"TBD\*", text)), "^": len(re.findall(r"TBD\^", text))}
    lowered = text.lower()
    footnotes = {name: name in lowered for name in CUP_FOOTNOTES}
    return {"rows": rows, "markers": markers, "footnotes": footnotes}


def fetch_pdf_text(url: str, timeout: int = 45) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf"})
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise MonitorError(f"The NBA PDF returned HTTP {response.status}.")
            payload = response.read()
    except (HTTPError, URLError, TimeoutError, OSError, HTTPException) as exc:
        raise MonitorError(f"Could not fetch the NBA ESPN Radio schedule PDF: {exc}") from exc
    if not payload:
        raise MonitorError("The NBA ESPN Radio schedule PDF came back empty.")
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError as exc:
            raise MonitorError(
                "No PDF text extractor is installed (pypdf or PyPDF2), so the fetched PDF could not "
                "be read. That is a failed check, not 'no drift'."
            ) from exc
    try:
        reader = PdfReader(io.BytesIO(payload))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:  # noqa: BLE001 - any extractor failure is unknown state
        raise MonitorError(f"The NBA ESPN Radio schedule PDF could not be parsed: {exc}") from exc
    if not text.strip():
        raise MonitorError("The PDF parsed to no text at all; the extractor returned nothing.")
    return text


def snapshot_rows(feed: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [row for row in feed.get("broadcasts", [])
            if str(row.get("id", "")).startswith("nba-espn-")]
    if not rows:
        raise MonitorError("The snapshot has no nba-espn- rows to compare against.")
    return rows


def expected_from_snapshot(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    """Rebuild what the PDF should print from the snapshot rows themselves.

    The away and home strings are read back out of each row title, so a title
    that has drifted from the PDF fails this check instead of passing it, and
    the ET time is recomputed from the stored Pacific start.
    """
    games: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        if row.get("start_pt") is None:
            continue
        match = re.match(r"^NBA on ESPN Radio: (.+) at (.+)$", str(row.get("title", "")))
        if not match:
            raise MonitorError(f"{row.get('id')}: title is not 'NBA on ESPN Radio: A at B'.")
        away, home = match.group(1), match.group(2)
        hours, minutes = (int(part) for part in str(row["start_pt"]).split(":"))
        total = hours * 60 + minutes + 180
        meridiem = "AM" if total < 12 * 60 else "PM"
        hour12 = total % (12 * 60) // 60
        hour12 = 12 if hour12 == 0 else hour12
        games[(str(row.get("date")), f"{away} at {home}")] = {
            "id": row.get("id"), "date": str(row.get("date")), "away": away, "home": home,
            "et": f"{hour12}:{total % 60:02d} {meridiem}",
        }
    return games


def compare(feed: dict[str, Any], parsed: dict[str, Any]) -> list[str]:
    meta = feed.get("meta", {}).get("espn_watch", {})
    window_start = str(feed.get("meta", {}).get("window_start", ""))
    window_end = str(feed.get("meta", {}).get("window_end", ""))
    expected = expected_from_snapshot(snapshot_rows(feed))
    rows = parsed["rows"]
    games = [row for row in rows if row["kind"] == "game"]
    tbd_dated = [row for row in rows if row["kind"] == "tbd-dated"]
    differences: list[str] = []

    if not games and not tbd_dated:
        raise MonitorError(
            "The PDF text parsed to zero dated rows, so the schedule state is unknown. The "
            "extractor or the PDF layout changed; this is not 'no drift'."
        )
    if len(games) + len(tbd_dated) != EXPECTED_DATED_ROWS:
        differences.append(
            f"- The PDF now parses to **{len(games) + len(tbd_dated)} dated rows**; the snapshot was "
            f"built from {EXPECTED_DATED_ROWS}. Re-read the PDF and rebuild."
        )
    # Two games can share a date (Christmas Day), so index the observed rows as a
    # list per date rather than letting one row overwrite the other.
    in_window = [row for row in games if window_start <= row["date"] <= window_end]
    by_date: dict[str, list[dict[str, Any]]] = {}
    for row in in_window:
        by_date.setdefault(row["date"], []).append(row)
    if len(in_window) != EXPECTED_IN_WINDOW_ROWS:
        differences.append(
            f"- The PDF now has **{len(in_window)} dated games inside the window**; the snapshot has "
            f"{EXPECTED_IN_WINDOW_ROWS}. Re-read the PDF and rebuild."
        )
    for marker, label in (("*", "Cup semifinal"), ("^", "Cup championship")):
        observed = parsed["markers"].get(marker, 0)
        if observed != EXPECTED_MARKERS[marker]:
            differences.append(
                f"- The PDF now carries {observed} '{marker}' TBD marker(s) for the {label} line; the "
                f"snapshot was built from {EXPECTED_MARKERS[marker]}."
            )
    for name in CUP_FOOTNOTES:
        if not parsed["footnotes"].get(name):
            differences.append(f"- The PDF no longer prints its '{name}' footnote text.")

    for (date, label), want in sorted(expected.items()):
        printed = by_date.get(date, [])
        match = next((row for row in printed if f"{row['away']} at {row['home']}" == label), None)
        if match is None:
            if printed:
                others = "; ".join(f"{row['away']} at {row['home']} ({row['et']} ET)" for row in printed)
                differences.append(
                    f"- **{date}**: the snapshot has `{want['id']}` ({label}, {want['et']} ET) but the "
                    f"PDF now prints {others}."
                )
            else:
                differences.append(
                    f"- **{date}**: the snapshot has `{want['id']}` ({label}, {want['et']} ET) but the "
                    "PDF no longer prints a game on that date."
                )
            continue
        if match["et"] != want["et"]:
            differences.append(
                f"- **{date}**: printed ET time for {label} changed from {want['et']} to "
                f"{match['et']}."
            )
    expected_pairs = set(expected)
    for row in in_window:
        if (row["date"], f"{row['away']} at {row['home']}") not in expected_pairs:
            differences.append(
                f"- **{row['date']}**: the PDF prints {row['away']} at {row['home']} ({row['et']} ET) "
                "and the snapshot has no row for it."
            )
    if len(expected) != int(meta.get("in_window_dated_rows", len(expected))):
        differences.append(
            f"- meta.espn_watch.in_window_dated_rows says {meta.get('in_window_dated_rows')} but the "
            f"snapshot has {len(expected)} dated NBA rows."
        )
    if meta.get("cup_tbd_rows") not in (None, 3):
        differences.append(
            f"- meta.espn_watch.cup_tbd_rows says {meta.get('cup_tbd_rows')}; the PDF has two Cup "
            "semifinal lines and one championship line, which is three rows."
        )
    return differences


def make_report(status: str, url: str, details: list[str], snapshot_date: str,
                counts: dict[str, Any]) -> str:
    checked_at = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M UTC")
    if status == "clear":
        body = (
            f"No differences found. The PDF parsed to **{counts.get('dated', 0)} dated rows** "
            f"({counts.get('games', 0)} with a printed matchup and time) plus "
            f"**{counts.get('tbd_dated', 0)} dated Cup TBD line(s)**, and all "
            f"**{counts.get('in_window', 0)} in-window games** match the snapshot's date, matchup and "
            "printed ET time. Cup markers: "
            + ", ".join(f"{marker} × {value}" for marker, value in sorted(counts.get("markers", {}).items()))
            + "."
        )
    elif status == "changed":
        body = (
            "**Schedule drift detected.** These differences between the PDF and the published "
            "snapshot need line-by-line review before any row is changed:\n\n" + "\n".join(details)
        )
    else:
        body = (
            "**The check could not be completed.** The state of the ESPN Radio schedule is unknown; "
            "this is not evidence that the PDF changed.\n\n" + "\n".join(details)
        )
    return (
        "# Automated source watch — NBA on ESPN Radio\n\n"
        f"- Checked: {checked_at}\n"
        f"- Source: [{url}]({url})\n"
        f"- Published snapshot date: {snapshot_date}\n"
        f"- Rows in this snapshot: {counts.get('snapshot', 0)} "
        f"({counts.get('snapshot_dated', 0)} dated, {counts.get('snapshot_tbd', 0)} Cup TBD)\n\n"
        f"{body}\n\n"
        f"{OUT_OF_WINDOW_NOTE}\n\n"
        "This is a read-only monitor of one rights-holder document. It does not confirm that KTCT 1050 "
        "aired any game, does not check the other five stations, does not edit `data/broadcasts.json` "
        "and does not publish a GitHub Pages snapshot. Open the PDF and review before rebuilding the "
        "feed.\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="write the human-readable report to this path")
    parser.add_argument("--github-output", type=Path, help="write status/report path as GitHub Actions outputs")
    parser.add_argument("--input", type=Path,
                        help="read saved PDF text instead of fetching (used by the offline tests)")
    args = parser.parse_args()

    snapshot_date = "unknown"
    url = DEFAULT_PDF
    counts: dict[str, Any] = {}
    extracted: str | None = None
    try:
        feed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
        snapshot_date = str(feed.get("meta", {}).get("snapshot_date", "unknown"))
        url = str(feed.get("meta", {}).get("espn_watch", {}).get("pdf", DEFAULT_PDF))
        rows = snapshot_rows(feed)
        counts["snapshot"] = len(rows)
        counts["snapshot_dated"] = sum(1 for row in rows if row.get("start_pt"))
        counts["snapshot_tbd"] = counts["snapshot"] - counts["snapshot_dated"]
        text = args.input.read_text(encoding="utf-8") if args.input else fetch_pdf_text(url)
        extracted = text
        parsed = parse_rows(text)
        window_start = str(feed.get("meta", {}).get("window_start", ""))
        window_end = str(feed.get("meta", {}).get("window_end", ""))
        counts["games"] = sum(1 for row in parsed["rows"] if row["kind"] == "game")
        counts["tbd_dated"] = sum(1 for row in parsed["rows"] if row["kind"] == "tbd-dated")
        counts["dated"] = counts["games"] + counts["tbd_dated"]
        counts["in_window"] = sum(
            1 for row in parsed["rows"]
            if row["kind"] == "game" and window_start <= row["date"] <= window_end
        )
        counts["markers"] = parsed["markers"]
        details = compare(feed, parsed)
        status = "changed" if details else "clear"
    except (MonitorError, OSError, json.JSONDecodeError, ValueError) as exc:
        status = "unavailable"
        details = [f"- {exc}"]
        # A failed parse is the moment a human most needs to see what the extractor
        # actually produced. Quote a short, whitespace-collapsed excerpt so the next
        # reader can fix the grammar or the extractor without another CI round trip.
        if extracted and extracted.strip():
            excerpt = re.sub(r"\s+", " ", extracted).strip()
            details.append(
                f"- Extracted text begins: `{excerpt[:400]}`"
                + (" …" if len(excerpt) > 400 else "")
            )
        try:
            feed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
            snapshot_date = str(feed.get("meta", {}).get("snapshot_date", "unknown"))
            url = str(feed.get("meta", {}).get("espn_watch", {}).get("pdf", DEFAULT_PDF))
            counts["snapshot"] = len(snapshot_rows(feed))
        except Exception:  # noqa: BLE001 - a report still has to be written
            pass

    report = make_report(status, url, details, snapshot_date, counts)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as output:
            output.write(f"espn_status={status}\n")
            if args.report:
                output.write(f"espn_report={args.report}\n")
    return 0 if status == "clear" else 2 if status == "changed" else 3


if __name__ == "__main__":
    raise SystemExit(main())
