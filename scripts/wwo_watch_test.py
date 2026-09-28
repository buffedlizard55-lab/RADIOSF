#!/usr/bin/env python3
"""Offline regression tests for scripts/wwo_watch.py.

No network access. The fixture HTML below is built from the structure and the
exact event ids, titles and venues printed on the live Westwood One grids when
they were read on 2026-09-27, so the parser is exercised against the markup it
will actually meet rather than against an idealised page.
"""
from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import wwo_watch  # noqa: E402

FEED = json.loads((ROOT / "data" / "broadcasts.json").read_text(encoding="utf-8"))
TODAY = "2026-09-27"


def card(event_id: int, title: str, venue: str, when: str) -> str:
    """One grid card: artwork anchor, title anchor, venue, time, Full Details."""
    href = f"https://www.westwoodonesports.com/events/{event_id}"
    return (
        f'<div class="event"><a href="{href}">'
        f'<img src="https://media-cdn.socastsrm.com/x/{event_id}.jpg" alt="event image"></a>'
        f'<a href="{href}">{title}</a>'
        f'<div class="venue">{venue}</div><div class="time">{when}</div>'
        f'<a href="{href}">Full Details</a></div>'
    )


def grid(heading: str, cards: list[str], generic: list[str] | None = None) -> str:
    body = "".join(cards) or '<p>No upcoming events</p>'
    tail = ""
    if generic:
        tail = '<h2>Upcoming Broadcasts</h2>' + "".join(generic)
    return f"<html><body><h1>{heading}</h1>{body}{tail}</body></html>"


NFL_HEADING = "Upcoming NFL Broadcasts"
NCAAF_HEADING = "Upcoming NCAA Football Broadcasts"
NCAAB_HEADING = "Upcoming NCAA Basketball Broadcasts"
SOCCER_HEADING = "Upcoming U.S. Soccer Broadcasts"

# Real rows from the live grids, read 2026-09-27.
NFL_CARDS = [
    card(548494, "Los Angeles Rams at Denver Broncos",
         "Empower Field at Mile High, Denver, CO", "7:30pm ET // Sunday Night Football"),
    card(548532, "Philadelphia Eagles at Chicago Bears",
         "Soldier Field, Chicago, IL", "7pm ET // Monday Night Football"),
    card(548485, "Indianapolis Colts vs Washington Commanders",
         "Tottenham Hotspur Stadium, London, UK", "9:15am ET // 2026 NFL London Games"),
]
NCAAF_CARDS = [
    card(557137, "Notre Dame at North Carolina", "Kenan Stadium, Chapel Hill, NC", "Air time TBD"),
    card(557146, "SEC Championship Game", "Mercedes-Benz Stadium, Atlanta, GA",
         "3:30pm ET // SEC Championship Game"),
    card(557132, "Army vs Navy", "MetLife Stadium, East Rutherford, NJ", "2:00pm ET"),
]
SOCCER_CARDS = [
    card(570239, "USMNT vs. Chile", "Energizer Park, St. Louis, MO", "7:45 PM ET"),
    card(570247, "USWNT vs. Spain", "Audi Field, Washington, DC",
         "2:30 PM ET // TNT Sports Broadcast - Audio Only Simulcast"),
]
# The generic strip below the sport grid mixes sports on purpose.
GENERIC = [
    card(570239, "USMNT vs. Chile", "Energizer Park, St. Louis, MO", "7:45 PM ET"),
    card(548494, "Los Angeles Rams at Denver Broncos", "Empower Field at Mile High, Denver, CO",
         "7:30pm ET"),
]


def widget(sport: str, widget_id: str, prefix: str, title: str) -> dict:
    return {"widget": widget_id, "prefix": prefix, "sport": sport, "title": title}


NFL_WIDGET = widget("NFL", "47029", "wwo-nfl-", "Upcoming+NFL+Broadcasts")
NCAAF_WIDGET = widget("NCAA Football", "47030", "wwo-ncaaf-", "Upcoming+NCAA+Football+Broadcasts")
NCAAB_WIDGET = widget("NCAA Basketball", "47031", "wwo-ncaab-", "Upcoming+NCAA+Basketball+Broadcasts")
SOCCER_WIDGET = widget("U.S. Soccer", "47032", "wwo-soccer-", "Upcoming+U.S.+Soccer+Broadcasts")


class ParserTests(unittest.TestCase):
    def test_extracts_ids_and_printed_titles(self):
        observed = wwo_watch.parse_grid(grid(NFL_HEADING, NFL_CARDS), NFL_WIDGET)
        self.assertEqual(
            observed,
            {
                "548494": "Los Angeles Rams at Denver Broncos",
                "548532": "Philadelphia Eagles at Chicago Bears",
                "548485": "Indianapolis Colts vs Washington Commanders",
            },
        )

    def test_artwork_and_full_details_do_not_become_the_title(self):
        # Three anchors share one href. Only the title string may survive.
        observed = wwo_watch.parse_grid(grid(NFL_HEADING, NFL_CARDS[:1]), NFL_WIDGET)
        self.assertEqual(observed["548494"], "Los Angeles Rams at Denver Broncos")
        self.assertNotIn("Full Details", observed["548494"])
        self.assertNotIn("event image", observed["548494"])

    def test_generic_strip_below_the_grid_is_ignored(self):
        # The soccer match in the NFL page's generic widget must not read as a
        # new NFL event.
        page = grid(NFL_HEADING, NFL_CARDS, generic=GENERIC)
        observed = wwo_watch.parse_grid(page, NFL_WIDGET)
        self.assertNotIn("570239", observed)
        self.assertEqual(len(observed), 3)

    def test_missing_heading_is_a_failure_not_an_empty_grid(self):
        with self.assertRaises(wwo_watch.WidgetError):
            wwo_watch.parse_grid(grid("Upcoming Broadcasts", NFL_CARDS), NFL_WIDGET)

    def test_empty_grid_parses_to_nothing(self):
        observed = wwo_watch.parse_grid(grid(NCAAB_HEADING, []), NCAAB_WIDGET)
        self.assertEqual(observed, {})

    def test_truncated_page_cannot_locate_the_grid(self):
        # A partial download leaves the heading unclosed, so the grid cannot be
        # located. That must be a failure, never an empty result.
        with self.assertRaises(wwo_watch.WidgetError):
            wwo_watch.parse_grid("<h1>Upcoming NFL Broadcasts" + "<a href='x'" * 50, NFL_WIDGET)


class FeedBaselineTests(unittest.TestCase):
    def test_expected_events_strips_the_title_prefix(self):
        expected = wwo_watch.expected_events(FEED, "wwo-ncaaf-")
        self.assertEqual(len(expected), 11)
        self.assertEqual(expected["557146"]["title"], "SEC Championship Game")
        self.assertEqual(expected["557146"]["date"], "2026-12-05")

    def test_basketball_prefix_has_no_rows_yet(self):
        self.assertEqual(wwo_watch.expected_events(FEED, "wwo-ncaab-"), {})

    def test_config_comes_from_the_feed(self):
        endpoint, widgets, merged = wwo_watch.load_config(FEED)
        self.assertTrue(endpoint.startswith("https://"))
        self.assertEqual([w["widget"] for w in widgets], ["47029", "47030", "47031", "47032"])
        self.assertEqual(merged, {"548538", "548491", "548568", "548509"})

    def test_grid_url_requests_the_whole_grid_in_one_page(self):
        url = wwo_watch.grid_url("https://www.westwoodonesports.com/more/eventGrid", NFL_WIDGET)
        self.assertIn("id=47029", url)
        self.assertIn("limit=100", url)
        self.assertIn("widgetTitle=Upcoming+NFL+Broadcasts", url)


class CompareTests(unittest.TestCase):
    def compare(self, widget, expected, observed, merged=frozenset(), today=TODAY,
                now=None, skipped=None):
        return wwo_watch.compare_widget(widget, expected, observed, set(merged), today,
                                        now, skipped)

    def test_matching_grid_is_clear(self):
        expected = {"557146": {"title": "SEC Championship Game", "date": "2026-12-05"}}
        self.assertEqual(self.compare(NCAAF_WIDGET, expected, {"557146": "SEC Championship Game"}), [])

    def test_new_event_is_reported(self):
        diffs = self.compare(NCAAF_WIDGET, {}, {"557999": "Texas at Oklahoma"})
        self.assertEqual(len(diffs), 1)
        self.assertIn("557999", diffs[0])
        self.assertIn("Texas at Oklahoma", diffs[0])

    def test_merged_49ers_event_is_not_reported_as_new(self):
        diffs = self.compare(
            NFL_WIDGET, {}, {"548538": "Washington Commanders at San Francisco 49ers"},
            merged={"548538"},
        )
        self.assertEqual(diffs, [])

    def test_future_row_missing_from_grid_is_reported(self):
        expected = {"557132": {"title": "Army vs Navy", "date": "2026-12-12"}}
        diffs = self.compare(NCAAF_WIDGET, expected, {})
        self.assertEqual(len(diffs), 1)
        self.assertIn("Army vs Navy", diffs[0])

    def test_past_row_missing_from_grid_is_not_drift(self):
        expected = {"548494": {"title": "Los Angeles Rams at Denver Broncos", "date": "2026-09-20"}}
        self.assertEqual(self.compare(NFL_WIDGET, expected, {}), [])

    def test_undated_row_missing_from_grid_is_reported(self):
        expected = {"548000": {"title": "Some TBA placeholder", "date": ""}}
        diffs = self.compare(NFL_WIDGET, expected, {})
        self.assertEqual(len(diffs), 1)
        self.assertIn("undated row", diffs[0])

    # The grid advertises *upcoming* broadcasts, so a same-day event that has
    # already started is legitimately gone. Regression for the 2026-09-28 live
    # preview: the Rams at Broncos row (listed 16:30 PT) dropped off the grid
    # at 22:34 PT on its own game day and was first reported as drift.
    def started_row(self, start="16:30", now="22:34", skipped=None):
        expected = {
            "548494": {
                "title": "Los Angeles Rams at Denver Broncos",
                "date": TODAY,
                "start": start,
            }
        }
        return self.compare(NFL_WIDGET, expected, {}, now=now, skipped=skipped)

    def test_same_day_row_missing_after_its_start_is_not_drift(self):
        skipped = []
        self.assertEqual(self.started_row(skipped=skipped), [])
        self.assertEqual(len(skipped), 1)
        self.assertIn("started 16:30 PT", skipped[0])

    def test_same_day_row_missing_before_its_start_is_still_reported(self):
        diffs = self.started_row(start="16:30", now="15:00")
        self.assertEqual(len(diffs), 1)
        self.assertIn("no longer lists event 548494", diffs[0])

    def test_same_day_row_without_a_listed_start_is_still_reported(self):
        diffs = self.started_row(start="", now="22:34")
        self.assertEqual(len(diffs), 1)

    def test_same_day_row_without_a_known_clock_is_still_reported(self):
        diffs = self.started_row(start="16:30", now=None)
        self.assertEqual(len(diffs), 1)

    def test_future_date_is_not_excused_by_the_clock(self):
        expected = {"548494": {"title": "Rams at Broncos", "date": "2026-10-04", "start": "10:00"}}
        diffs = self.compare(NFL_WIDGET, expected, {}, now="22:34")
        self.assertEqual(len(diffs), 1)

    def test_renamed_event_is_reported(self):
        expected = {"557146": {"title": "SEC Championship", "date": "2026-12-05"}}
        diffs = self.compare(NCAAF_WIDGET, expected, {"557146": "SEC Championship Game"})
        self.assertEqual(len(diffs), 1)
        self.assertIn("SEC Championship Game", diffs[0])

    def test_unparsed_title_is_not_reported_as_a_rename(self):
        expected = {"557146": {"title": "SEC Championship Game", "date": "2026-12-05"}}
        self.assertEqual(self.compare(NCAAF_WIDGET, expected, {"557146": ""}), [])


def mirror_pages(ncaab_cards: list[str] | None = None) -> dict[str, str]:
    """Fixtures that match the shipped feed exactly, so a test can change one thing."""
    pages = {}
    for widget_id, prefix, heading in (
        ("47029", "wwo-nfl-", NFL_HEADING),
        ("47030", "wwo-ncaaf-", NCAAF_HEADING),
        ("47032", "wwo-soccer-", SOCCER_HEADING),
    ):
        expected = wwo_watch.expected_events(FEED, prefix)
        cards = [
            card(int(event_id), row["title"], "", "")
            for event_id, row in sorted(expected.items())
        ]
        pages[widget_id] = grid(heading, cards, generic=GENERIC)
    pages["47031"] = grid(NCAAB_HEADING, ncaab_cards or [])
    return pages


class RunTests(unittest.TestCase):
    def test_real_feed_against_matching_grids_is_clear(self):
        status, differences, details = wwo_watch.run(FEED, TODAY, mirror_pages())
        self.assertEqual(status, "clear", differences)
        self.assertEqual(differences, [])
        self.assertEqual(len(details), 4)
        self.assertTrue(all("checked" in line for line in details))

    def test_started_event_dropping_off_the_grid_is_clear_with_a_note(self):
        # Replay of the live 2026-09-28 preview: event 548494 (Rams at Broncos,
        # listed start 16:30 PT) left the upcoming grid at 22:34 PT on game day.
        pages = mirror_pages()
        nfl_expected = wwo_watch.expected_events(FEED, "wwo-nfl-")
        cards = [
            card(int(eid), row["title"], "", "")
            for eid, row in sorted(nfl_expected.items())
            if eid != "548494"
        ]
        pages["47029"] = grid(NFL_HEADING, cards, generic=GENERIC)
        status, differences, details = wwo_watch.run(FEED, TODAY, pages, now_hhmm="22:34")
        self.assertEqual(status, "clear", differences)
        self.assertTrue(any("started 16:30 PT" in line for line in details), details)

    def test_same_day_event_missing_before_its_start_is_still_drift(self):
        pages = mirror_pages()
        nfl_expected = wwo_watch.expected_events(FEED, "wwo-nfl-")
        cards = [
            card(int(eid), row["title"], "", "")
            for eid, row in sorted(nfl_expected.items())
            if eid != "548494"
        ]
        pages["47029"] = grid(NFL_HEADING, cards, generic=GENERIC)
        status, differences, _ = wwo_watch.run(FEED, TODAY, pages, now_hhmm="15:00")
        self.assertEqual(status, "changed")
        self.assertTrue(any("548494" in line for line in differences))

    def test_basketball_grid_publishing_events_is_drift(self):
        # The largest open limitation is an empty college basketball grid. The
        # moment Westwood One populates it, the watcher must say so.
        pages = mirror_pages(ncaab_cards=[
            card(559001, "Gonzaga at Saint Mary's", "The Pavilion, Moraga, CA", "9:00pm ET"),
        ])
        status, differences, _ = wwo_watch.run(FEED, TODAY, pages)
        self.assertEqual(status, "changed")
        self.assertTrue(any("NCAA Basketball" in line and "559001" in line for line in differences))

    def test_empty_grid_where_rows_exist_is_unavailable(self):
        pages = mirror_pages()
        pages["47029"] = grid(NFL_HEADING, [])
        status, differences, details = wwo_watch.run(FEED, TODAY, pages)
        self.assertEqual(status, "unavailable")
        self.assertEqual(differences, [])
        self.assertTrue(any("not checked" in line for line in details))

    def test_new_event_on_a_matching_grid_is_changed(self):
        pages = mirror_pages()
        pages["47030"] = grid(NCAAF_HEADING, NCAAF_CARDS + [
            card(int(eid), row["title"], "", "")
            for eid, row in sorted(wwo_watch.expected_events(FEED, "wwo-ncaaf-").items())
        ] + [card(559100, "Big Ten Championship Game", "", "")])
        status, differences, _ = wwo_watch.run(FEED, TODAY, pages)
        self.assertEqual(status, "changed")
        self.assertTrue(any("559100" in line for line in differences))

    def test_unfetchable_widget_does_not_mask_real_drift(self):
        pages = mirror_pages(ncaab_cards=[card(559002, "Duke at North Carolina", "", "")])
        pages["47030"] = "<html><body><h1>Some other page</h1></body></html>"
        status, differences, details = wwo_watch.run(FEED, TODAY, pages)
        self.assertEqual(status, "changed")
        self.assertTrue(any("559002" in line for line in differences))
        self.assertTrue(any("NCAA Football" in line and "not checked" in line for line in details))

    def test_missing_config_block_raises_for_the_caller_to_report(self):
        with self.assertRaises(wwo_watch.MonitorError):
            wwo_watch.run({"meta": {}, "broadcasts": []}, TODAY, {})


class ReportAndExitCodeTests(unittest.TestCase):
    def test_report_states_its_own_limits(self):
        report = wwo_watch.make_report("clear", TODAY, ["- **NFL**: checked"], [], "2026-09-27")
        self.assertIn("read-only", report)
        self.assertIn("does not confirm", report)
        self.assertNotIn("published a new snapshot", report)
        self.assertNotIn("Pacific clock used for comparison", report)

    def test_report_states_the_clock_when_one_is_known(self):
        report = wwo_watch.make_report(
            "clear", TODAY, ["- **NFL**: checked"], [], "2026-09-27", "22:34"
        )
        self.assertIn("Pacific clock used for comparison: 22:34", report)

    def test_changed_report_lists_every_difference(self):
        report = wwo_watch.make_report(
            "changed", TODAY, ["- **NFL**: checked"], ["- **NFL**: event 1 moved."], "2026-09-27"
        )
        self.assertIn("Grid drift detected", report)
        self.assertIn("event 1 moved", report)

    def test_exit_codes(self):
        pages = mirror_pages()
        with tempfile.TemporaryDirectory() as tmp:
            saved = Path(tmp) / "pages.json"
            saved.write_text(json.dumps(pages), encoding="utf-8")
            out = Path(tmp) / "gh.txt"
            report = Path(tmp) / "report.md"
            code = self.invoke(saved, out, report)
            written = out.read_text(encoding="utf-8")
            body = report.read_text(encoding="utf-8")
        self.assertEqual(code, 0)
        self.assertIn("wwo_status=clear", written)
        self.assertIn("Status: **clear**", body)
        # The feed itself must never be written to by the watcher.
        self.assertEqual(
            json.loads((ROOT / "data" / "broadcasts.json").read_text(encoding="utf-8")), FEED
        )

    def test_drift_exits_two(self):
        pages = mirror_pages(ncaab_cards=[card(559003, "Kentucky at Duke", "", "")])
        with tempfile.TemporaryDirectory() as tmp:
            saved = Path(tmp) / "pages.json"
            saved.write_text(json.dumps(pages), encoding="utf-8")
            out = Path(tmp) / "gh.txt"
            code = self.invoke(saved, out, Path(tmp) / "report.md")
            written = out.read_text(encoding="utf-8")
        self.assertEqual(code, 2)
        self.assertIn("wwo_status=changed", written)

    def test_unavailable_exits_three(self):
        pages = mirror_pages()
        pages["47029"] = "<html><body><h1>Some other page</h1></body></html>"
        with tempfile.TemporaryDirectory() as tmp:
            saved = Path(tmp) / "pages.json"
            saved.write_text(json.dumps(pages), encoding="utf-8")
            out = Path(tmp) / "gh.txt"
            code = self.invoke(saved, out, Path(tmp) / "report.md")
            written = out.read_text(encoding="utf-8")
        self.assertEqual(code, 3)
        self.assertIn("wwo_status=unavailable", written)

    def invoke(self, saved: Path, out: Path, report: Path) -> int:
        argv, stdout = sys.argv, sys.stdout
        try:
            sys.argv = [
                "wwo_watch.py", "--today", TODAY, "--input", str(saved),
                "--report", str(report), "--github-output", str(out),
            ]
            sys.stdout = io.StringIO()
            return wwo_watch.main()
        finally:
            sys.argv, sys.stdout = argv, stdout


if __name__ == "__main__":
    unittest.main(verbosity=2)
