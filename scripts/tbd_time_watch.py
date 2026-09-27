#!/usr/bin/env python3
"""Read-only watch for schedule entries whose kickoff is still TBD.

Five monitors already compare machine-readable sources event by event (the MLB
postseason API, four Westwood One grids, the NBA ESPN Radio PDF, the weekly ESPN
Radio grid) and one compares the exact text on the club, school and station
pages. None of them can see the thing a reader most wants next: a kickoff time
that has just been published for a game the snapshot lists without one.

This monitor closes that gap for the pages that publish those times **and that
render them into the HTML a plain request receives**. A page that builds its
schedule in the browser - gostanford.com does - carries nothing for this monitor
to read, so its target reports `unavailable` and is held out of the shipped
config until that changes; see `docs/LIMITATIONS.md`. As shipped it watches two
pages:

  * Cal's football schedule in its text view, where seven rows print an empty
    Time cell (calbears.com/sports/football/schedule/text);
  * 49ers.com's schedule page, where the Week 18 row still prints TBD for the
    date and the network.

It does not parse a schedule into rows and it never invents a time. For each
entry in data/tbd_watch.json it locates the one row that was read on
2026-09-27 and reports one of three things:

  * **still TBD** - the row prints no kickoff, exactly as when it was read;
  * **published** - a clock time is now printed there. That is a change a human
    must transcribe into scripts/build_feed.py and rebuild; and
  * **unknown** - the row could not be located, or its time cell holds something
    that is neither empty/TBD nor a clock time. The state is unknown, which is
    never reported as "no change".

It never edits data/broadcasts.json and never publishes GitHub Pages.
"""
from __future__ import annotations

import argparse
import html
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
CONFIG_PATH = ROOT / "data" / "tbd_watch.json"
FEED_PATH = ROOT / "data" / "broadcasts.json"
USER_AGENT = "Mozilla/5.0 (compatible; RADIOSF-tbd-watch/1.0; +https://github.com/buffedlizard55-lab/RADIOSF)"

TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
CELL_RE = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S | re.I)
PIPE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
# A printed kickoff: 7:30 PM, 12:05 pm, 4:30 p.m. Text is normalised to lower
# case first, so the pattern is written in lower case. No trailing word
# boundary: "p.m." ends in a full stop, which has none.
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}\s*(?:a\.?m\.?|p\.?m\.?)", re.I)
# Where the next game starts. A schedule prints each game as a weekday and a date,
# so a segment that runs past the next weekday belongs to the next game, not to
# this one. Without this cut, a kickoff published for the following game would be
# read as this game's kickoff.
NEXT_GAME_RE = re.compile(
    r"\b(?:Mon|Tues?|Wed|Thur?s?|Fri|Sat|Sun)[a-z]*\.?\s*,?\s*"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}\b")
# Cells that mean "no kickoff yet", as opposed to a time or to something else.
TBD_MARKERS = {"", "tbd", "tba", "-", "--", "n/a", "tbd (et)", "tba (et)", "tbd et", "tba et"}

FOLD = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u00a0": " ", "\u00ae": "",
})


class WatchError(Exception):
    """A target could not be checked; its state is unknown."""


def cell_text(fragment: str) -> str:
    """One fragment as visible text: tags stripped, entities resolved, whitespace collapsed.

    Case is preserved so a printed kickoff can be quoted back exactly as the page
    prints it; comparisons case-fold through normalise().
    """
    return SPACE_RE.sub(" ", html.unescape(TAG_RE.sub(" ", fragment))).strip()


def normalise(text: str) -> str:
    """Case-folded, whitespace-collapsed, typography-folded text."""
    return SPACE_RE.sub(" ", html.unescape(text).translate(FOLD)).strip().casefold()


def visible_text(document: str) -> str:
    """The page as visible text, with the case the page prints.

    Comparisons fold through normalise(), but a printed kickoff is quoted back
    exactly as it appears, so "7:00 PM" is reported as "7:00 PM".
    """
    return cell_text(document)


def cell_list(document: str) -> list[str]:
    """Every table cell on the page, in document order, as visible text.

    An HTML schedule page is read through its `<td>`/`<th>` cells. A saved copy
    that was rendered as a markdown pipe table (what `--input` accepts, and what
    a human gets when they copy the table out of a browser) is read through its
    pipe-delimited rows instead, so the same row-matching code serves both.
    """
    cells = [cell_text(cell) for cell in CELL_RE.findall(document)]
    if cells:
        return cells
    pipe_cells: list[str] = []
    for line in document.splitlines():
        if PIPE_ROW_RE.match(line):
            pipe_cells.extend(cell_text(cell) for cell in line.strip().strip("|").split("|"))
    return pipe_cells


def feed_rows() -> dict[str, dict[str, Any]]:
    """The snapshot's rows by id, so a stale watch entry can be detected."""
    try:
        feed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WatchError(f"data/broadcasts.json could not be read: {exc}") from exc
    rows = feed.get("broadcasts")
    if not isinstance(rows, list):
        raise WatchError("data/broadcasts.json has no 'broadcasts' list.")
    return {str(row.get("id")): row for row in rows if isinstance(row, dict)}


def check_table_row(entry: dict[str, Any], cells: list[str]) -> dict[str, Any]:
    """Locate one schedule row and report what its time cell holds.

    The row is matched on two things at once: the date cell, and the opponent in
    the column the schedule prints it in. A loose "somewhere in the row" match
    would keep reporting "still TBD" after the opponent changed, which is exactly
    the drift this monitor exists to notice.
    """
    key = normalise(entry["date_cell"])
    opponent = normalise(entry["opponent"])
    offset = int(entry.get("opponent_offset", 3))
    for index, cell in enumerate(cells):
        if normalise(cell) != key or index + offset >= len(cells):
            continue
        if normalise(cells[index + offset]) != opponent:
            continue
        printed = cells[index + 1]
        folded = normalise(printed)
        if TIME_RE.search(folded):
            return {"state": "published", "printed": printed, "row": entry["row"]}
        if folded in TBD_MARKERS:
            return {"state": "tbd", "printed": printed, "row": entry["row"]}
        return {"state": "unknown", "printed": printed, "row": entry["row"],
                "reason": f"the time cell holds {printed!r}, which is neither empty nor a kickoff"}
    return {"state": "unknown", "row": entry["row"],
            "reason": f"no row for {entry['date_cell']} vs {entry['opponent']} was found on the page"}


def cut_at_next_game(segment: str) -> str:
    """One game's slice of the page: everything up to the next game's date.

    The `window` size is a safety net, not the boundary. If the page prints a
    weekday and a date further along, that is the next game, and everything from
    there on belongs to it.
    """
    following = NEXT_GAME_RE.search(segment)
    return segment[:following.start()] if following else segment


def check_after_anchor(target: dict[str, Any], entry: dict[str, Any], text: str) -> dict[str, Any]:
    """Read the characters after an anchor and report whether a time appeared.

    The anchor is matched case-insensitively over the raw visible text, so the
    slice that is searched for a kickoff keeps the page's own capitalisation.

    The search is a regular expression with IGNORECASE rather than a
    `casefold()`ed copy of the page. Casefolding can change a string's length -
    "I" with a dot above folds to two characters - and a single such character
    anywhere on a page would shift every offset and make the whole target
    unreadable. Matching on the original text keeps the offsets true by
    construction.
    """
    anchor = (entry.get("anchor") or target.get("anchor") or "").strip()
    window = int(target.get("window", 400))
    wanted = [item for item in entry.get("expect_in_segment", target.get("expect_in_segment", []))]
    # `text` has already been through cell_text(), so it is typography-folded;
    # the anchor gets the same treatment before it is matched against it.
    needle = SPACE_RE.sub(" ", html.unescape(anchor).translate(FOLD)).strip()
    if not needle:
        return {"state": "unknown", "row": entry["row"], "reason": "the entry has no anchor text"}
    pattern = re.compile(re.escape(needle), re.IGNORECASE)
    segments: list[str] = []
    for match in pattern.finditer(text):
        segment = text[match.end():match.end() + window]
        folded_segment = normalise(segment)
        if any(normalise(item) not in folded_segment for item in wanted):
            continue
        segments.append(cut_at_next_game(segment))
    if not segments:
        wanted_text = " and ".join(wanted) if wanted else "the row"
        return {"state": "unknown", "row": entry["row"],
                "reason": f"no {anchor!r} block carrying {wanted_text} was found"}
    times = [TIME_RE.search(segment).group(0) for segment in segments if TIME_RE.search(segment)]
    if times and len(times) != len(segments):
        # Some blocks that carry this date and this opponent print a kickoff and
        # some do not. A page that shows two seasons on one screen does exactly
        # this, so the answer is "unknown", never a time picked off one of them.
        return {"state": "unknown", "row": entry["row"],
                "reason": (f"{len(segments)} blocks print {anchor!r} with "
                           f"{' and '.join(wanted) if wanted else 'the row'}, and only {len(times)} "
                           "of them print a kickoff - the page carries two seasons")}
    if times:
        return {"state": "published", "printed": times[0], "row": entry["row"]}
    return {"state": "tbd", "printed": "", "row": entry["row"]}


def check_target(target: dict[str, Any], document: str, rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Check one target's entries against one fetched document."""
    text = visible_text(document)
    cells: list[str] = []
    if target.get("kind") == "table-row":
        cells = cell_list(document)
        if not cells:
            raise WatchError("no table cells were found, so no row could be located")
        page_anchor = normalise(target.get("anchor", ""))
        if page_anchor and page_anchor not in text.casefold():
            raise WatchError(f"the page anchor {target['anchor']!r} was not found")
    results = []
    for entry in target["entries"]:
        row_id = str(entry["row"])
        row = rows.get(row_id)
        if row is None:
            results.append({"state": "unknown", "row": row_id,
                            "reason": "no row with this id exists in data/broadcasts.json"})
            continue
        if row.get("start_pt"):
            results.append({"state": "stale", "row": row_id, "printed": row.get("start_pt"),
                            "reason": "the snapshot already carries this start time"})
            continue
        if target.get("kind") == "table-row":
            results.append(check_table_row(entry, cells))
        else:
            results.append(check_after_anchor(target, entry, text))
    return {"target": target, "results": results}


def validate_config(config: Any) -> list[dict[str, Any]]:
    if not isinstance(config, dict) or not isinstance(config.get("targets"), list) or not config["targets"]:
        raise WatchError("data/tbd_watch.json must contain a non-empty 'targets' list.")
    seen_targets: set[str] = set()
    # (target, row) pairs: the same row may be watched from two pages - a kickoff
    # published on either one is worth reporting - but never twice on one page.
    seen_rows: set[tuple[str, str]] = set()
    for target in config["targets"]:
        for key in ("id", "label", "url", "kind", "rows"):
            if not isinstance(target.get(key), str) or not target[key].strip():
                raise WatchError(f"A TBD-watch target is missing '{key}'.")
        if target["id"] in seen_targets:
            raise WatchError(f"Duplicate TBD-watch target {target['id']}.")
        seen_targets.add(target["id"])
        if not target["url"].startswith("https://"):
            raise WatchError(f"{target['id']} must use an https URL.")
        if target["kind"] not in ("table-row", "after-anchor"):
            raise WatchError(f"{target['id']} has an unknown kind {target['kind']!r}.")
        if not target.get("entries"):
            raise WatchError(f"{target['id']} needs at least one entry.")
        for entry in target["entries"]:
            if not isinstance(entry.get("row"), str) or not entry["row"].strip():
                raise WatchError(f"{target['id']} has an entry without a 'row' id.")
            if not isinstance(entry.get("why"), str) or not entry["why"].strip():
                raise WatchError(f"{target['id']} entry {entry['row']} has no 'why'.")
            pair = (target["id"], entry["row"])
            if pair in seen_rows:
                raise WatchError(f"Duplicate TBD-watch row {entry['row']} on {target['id']}.")
            seen_rows.add(pair)
            if target["kind"] == "table-row":
                for key in ("date_cell", "opponent"):
                    if not isinstance(entry.get(key), str) or not entry[key].strip():
                        raise WatchError(f"{target['id']} entry {entry['row']} needs '{key}'.")
            else:
                if not isinstance(entry.get("anchor", target.get("anchor")), str):
                    raise WatchError(f"{target['id']} entry {entry['row']} needs an 'anchor'.")
    return config["targets"]


def fetch_html(url: str, timeout: int = 25) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise WatchError(f"returned HTTP {response.status}")
            return response.read().decode("utf-8", errors="replace")
    except WatchError:
        raise
    except (HTTPError, URLError, TimeoutError, OSError, HTTPException, UnicodeDecodeError) as exc:
        raise WatchError(f"could not be fetched: {exc}") from exc


def run(config: Any, documents: dict[str, str] | None = None) -> tuple[str, list[str], list[str]]:
    """Check every target. Returns (status, changes, unreadable, details).

    A row that could not be read is never folded into `changes`: an unreadable
    page is not evidence that a kickoff appeared, and a kickoff that appeared is
    not evidence that another row moved. They are reported apart, and either one
    keeps the status away from "clear".
    """
    targets = validate_config(config)
    rows = feed_rows()
    changes: list[str] = []
    unreadable: list[str] = []
    details: list[str] = []
    failures = 0
    for target in targets:
        try:
            if documents is not None:
                if target["id"] not in documents:
                    raise WatchError("no saved copy was supplied")
                document = documents[target["id"]]
            else:
                document = fetch_html(target["url"])
            if len(document.strip()) < 200:
                raise WatchError("returned an almost empty body")
            outcome = check_target(target, document, rows)
        except WatchError as exc:
            failures += 1
            details.append(f"- **{target['label']}** ([page]({target['url']})): not checked, {exc}. "
                           f"Rows it supports are unverified this run: {target['rows']}.")
            continue
        for result in outcome["results"]:
            row_id = result["row"]
            if result["state"] == "tbd":
                details.append(f"- `{row_id}`: kickoff still TBD on {target['label']}.")
            elif result["state"] == "published":
                printed = result["printed"]
                changes.append(
                    f"- **{target['label']}** ([page]({target['url']})): `{row_id}` now prints a "
                    f"start time ({printed}). Transcribe it into `scripts/build_feed.py`, rebuild, "
                    f"and remove the entry from `data/tbd_watch.json`."
                )
                details.append(f"- `{row_id}`: **kickoff now published ({printed})**.")
            elif result["state"] == "stale":
                changes.append(
                    f"- `data/tbd_watch.json`: the entry for `{row_id}` is stale - the snapshot "
                    f"already carries {result['printed']}. Remove the entry so the watch stays honest."
                )
            else:
                failures += 1
                unreadable.append(
                    f"- **{target['label']}** ([page]({target['url']})): `{row_id}` could not be "
                    f"read ({result['reason']}). Its state is unknown, which is not evidence that "
                    f"nothing changed. Re-read rows: {target['rows']}."
                )
                details.append(f"- `{row_id}`: not checked ({result['reason']}).")
    if changes:
        status = "changed"
    elif failures:
        status = "unavailable"
    else:
        status = "clear"
    return status, changes, unreadable, details


def make_report(status: str, details: list[str], changes: list[str], unreadable: list[str],
                checked: str) -> str:
    checked_at = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M UTC")
    if status == "clear":
        body = ("Every watched row still prints no kickoff, exactly as when it was read.\n\n"
                + "\n".join(details))
    elif status == "changed":
        sections = ["**A watched row changed.** Re-read it before changing the feed:\n\n"
                    + "\n".join(changes)]
        if unreadable:
            sections.append("**A watched row could not be read as well.** Its state is unknown, which "
                            "is not evidence that it changed:\n\n" + "\n".join(unreadable))
        sections.append("All watched rows:\n\n" + "\n".join(details))
        body = "\n\n".join(sections)
    else:
        sections = ["**At least one row could not be checked.** Its state is unknown; this is not "
                    "evidence that it changed."]
        if unreadable:
            sections.append("\n".join(unreadable))
        sections.append("All watched rows:\n\n" + "\n".join(details))
        body = "\n\n".join(sections)
    return (
        "# Automated source watch - kickoffs still listed as TBD\n\n"
        f"- Checked: {checked_at}\n"
        f"- Entries last read by hand: {checked}\n"
        f"- Status: **{status}**\n\n"
        f"{body}\n\n"
        "This monitor reports that a kickoff appeared, or that a row could not be read. It does not "
        "parse a schedule into the feed, confirm a station clearance, change `data/broadcasts.json`, "
        "or publish GitHub Pages.\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="write the human-readable report to this path")
    parser.add_argument("--github-output", type=Path, help="write status as a GitHub Actions output")
    parser.add_argument("--input", type=Path, help="read saved pages from a JSON object keyed by target id")
    args = parser.parse_args()

    checked = "unknown"
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        checked = str(config.get("checked", "unknown")) if isinstance(config, dict) else "unknown"
        documents = json.loads(args.input.read_text(encoding="utf-8")) if args.input else None
        if documents is not None and not isinstance(documents, dict):
            raise WatchError("--input must be a JSON object keyed by target id.")
        status, changes, unreadable, details = run(config, documents)
    except (WatchError, OSError, json.JSONDecodeError) as exc:
        status, changes, unreadable, details = "unavailable", [], [], [f"- {exc}"]

    report = make_report(status, details, changes, unreadable, checked)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as output:
            output.write(f"tbd_status={status}\n")
    return 0 if status == "clear" else 2 if status == "changed" else 3


if __name__ == "__main__":
    raise SystemExit(main())
