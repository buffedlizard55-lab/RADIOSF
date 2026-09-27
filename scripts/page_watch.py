#!/usr/bin/env python3
"""Read-only page-change watch for club, school and station pages.

The MLB Stats API and the Westwood One grids are machine-readable, so
scripts/source_watch.py and scripts/wwo_watch.py can compare them event by event.
The remaining rows (49ers, Cal, Stanford, Earthquakes) and the station grids
rest on ordinary HTML pages. Parsing a station clearance out of those pages
would be guesswork, so this monitor does something narrower and honest:

  * every `expect` string in data/page_watch.json was read on the live page when
    the snapshot was built. If one is no longer found, the page changed and the
    rows it supports need a human re-read -> status **changed**;
  * every `alert_if_present` string was absent. If one appears, new schedule
    information (for example a basketball radio listing) may have been
    published -> status **changed**;
  * a page that cannot be fetched is **unavailable**: its state is unknown, and
    that is never reported as "no change".

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
CONFIG_PATH = ROOT / "data" / "page_watch.json"
USER_AGENT = "Mozilla/5.0 (compatible; RADIOSF-page-watch/1.0; +https://github.com/buffedlizard55-lab/RADIOSF)"

TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
# Typographic characters that pages swap freely for their ASCII forms.
FOLD = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u00a0": " ", "\u00ae": "",
})


class PageError(Exception):
    """One page could not be checked; its state is unknown."""


def normalise(text: str) -> str:
    """Case-folded, whitespace-collapsed, typography-folded text."""
    return SPACE_RE.sub(" ", html.unescape(text).translate(FOLD)).strip().casefold()


def searchable(document: str) -> str:
    """Return the page as visible text plus raw markup, both normalised.

    Some pages render the schedule into markup, others ship it inside a script
    blob; searching both avoids a false "string disappeared" on either kind.
    """
    visible = TAG_RE.sub(" ", document)
    return normalise(visible) + "\n" + normalise(document)


def check_page(page: dict[str, Any], document: str) -> list[str]:
    """Return human-readable differences for one page (empty when unchanged)."""
    haystack = searchable(document)
    differences = []
    for item in page.get("expect", []):
        if normalise(item["text"]) not in haystack:
            differences.append(
                f"- **{page['label']}** ([page]({page['url']})): expected text "
                f"\"{item['text']}\" is no longer found ({item['why']}). "
                f"Re-read rows: {page['rows']}."
            )
    for item in page.get("alert_if_present", []):
        if normalise(item["text"]) in haystack:
            differences.append(
                f"- **{page['label']}** ([page]({page['url']})): \"{item['text']}\" now appears "
                f"({item['why']}). Review before adding anything: {page['rows']}."
            )
    return differences


def validate_config(config: Any) -> list[dict[str, Any]]:
    if not isinstance(config, dict) or not isinstance(config.get("pages"), list) or not config["pages"]:
        raise PageError("data/page_watch.json must contain a non-empty 'pages' list.")
    seen = set()
    for page in config["pages"]:
        for key in ("id", "label", "url", "rows"):
            if not isinstance(page.get(key), str) or not page[key].strip():
                raise PageError(f"A page-watch entry is missing '{key}'.")
        if page["id"] in seen:
            raise PageError(f"Duplicate page-watch id {page['id']}.")
        seen.add(page["id"])
        if not page["url"].startswith("https://"):
            raise PageError(f"{page['id']} must use an https URL.")
        if not page.get("expect"):
            # Without at least one expected string a blank or error page would
            # read as "unchanged", which is exactly the failure to avoid.
            raise PageError(f"{page['id']} needs at least one 'expect' string.")
        for group in ("expect", "alert_if_present"):
            for item in page.get(group, []):
                if not isinstance(item, dict) or not str(item.get("text", "")).strip() or not item.get("why"):
                    raise PageError(f"{page['id']} has an invalid {group} entry.")
    return config["pages"]


def fetch_html(url: str, timeout: int = 25) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise PageError(f"returned HTTP {response.status}")
            return response.read().decode("utf-8", errors="replace")
    except PageError:
        raise
    except (HTTPError, URLError, TimeoutError, OSError, HTTPException, UnicodeDecodeError) as exc:
        raise PageError(f"could not be fetched: {exc}") from exc


def run(config: Any, documents: dict[str, str] | None = None) -> tuple[str, list[str], list[str]]:
    pages = validate_config(config)
    differences: list[str] = []
    details: list[str] = []
    failures = 0
    for page in pages:
        try:
            if documents is not None:
                if page["id"] not in documents:
                    raise PageError("no saved copy was supplied")
                document = documents[page["id"]]
            else:
                document = fetch_html(page["url"])
            if len(document.strip()) < 200:
                raise PageError("returned an almost empty body")
        except PageError as exc:
            failures += 1
            details.append(f"- **{page['label']}** ([page]({page['url']})): not checked, {exc}. "
                           f"Rows it supports are unverified this run: {page['rows']}.")
            continue
        found = check_page(page, document)
        differences.extend(found)
        details.append(f"- **{page['label']}**: {'changed' if found else 'unchanged'} "
                       f"({len(page.get('expect', []))} expected, "
                       f"{len(page.get('alert_if_present', []))} watched-for strings).")
    if differences:
        status = "changed"
    elif failures:
        status = "unavailable"
    else:
        status = "clear"
    return status, differences, details


def make_report(status: str, details: list[str], differences: list[str], checked: str) -> str:
    checked_at = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M UTC")
    if status == "clear":
        body = "Every watched page still carries the text the snapshot was built from.\n\n" + "\n".join(details)
    elif status == "changed":
        body = ("**A watched page changed.** Re-read it before changing the feed:\n\n"
                + "\n".join(differences) + "\n\nAll pages:\n\n" + "\n".join(details))
    else:
        body = ("**At least one page could not be checked.** Its state is unknown; this is not "
                "evidence that it changed.\n\n" + "\n".join(details))
    return (
        "# Automated source watch — club, school and station pages\n\n"
        f"- Checked: {checked_at}\n"
        f"- Expected text last verified by hand: {checked}\n"
        f"- Status: **{status}**\n\n"
        f"{body}\n\n"
        "This monitor only reports that a page's text moved. It does not parse schedules, "
        "confirm a station clearance, change `data/broadcasts.json`, or publish GitHub Pages.\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="write the human-readable report to this path")
    parser.add_argument("--github-output", type=Path, help="write status as a GitHub Actions output")
    parser.add_argument("--input", type=Path, help="read saved HTML from a JSON object keyed by page id")
    args = parser.parse_args()

    checked = "unknown"
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        checked = str(config.get("checked", "unknown")) if isinstance(config, dict) else "unknown"
        documents = json.loads(args.input.read_text(encoding="utf-8")) if args.input else None
        if documents is not None and not isinstance(documents, dict):
            raise PageError("--input must be a JSON object keyed by page id.")
        status, differences, details = run(config, documents)
    except (PageError, OSError, json.JSONDecodeError) as exc:
        status, differences, details = "unavailable", [], [f"- {exc}"]

    report = make_report(status, details, differences, checked)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as output:
            output.write(f"page_status={status}\n")
    return 0 if status == "clear" else 2 if status == "changed" else 3


if __name__ == "__main__":
    raise SystemExit(main())
