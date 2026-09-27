#!/usr/bin/env python3
"""Offline tests for the NBA ESPN Radio schedule monitor.

The fixture at scripts/fixtures/espn_radio_nba_2026-08-13.txt is the printed
content of the NBA's own "2026-27 NBA SEASON: ESPN RADIO BROADCAST SCHEDULE"
PDF, read on 2026-09-27. These tests never touch the network; they check that a
complete read is clear, that every kind of drift is reported, and that a read
which cannot be parsed is never mistaken for "no drift".
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import espn_watch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FEED_PATH = ROOT / "data" / "broadcasts.json"
FIXTURE = ROOT / "scripts" / "fixtures" / "espn_radio_nba_2026-08-13.txt"


def feed() -> dict:
    return json.loads(FEED_PATH.read_text(encoding="utf-8"))


def fixture_text() -> str:
    return FIXTURE.read_text(encoding="utf-8")


class ParseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parsed = espn_watch.parse_rows(fixture_text())

    def test_every_printed_row_is_parsed(self) -> None:
        games = [row for row in self.parsed["rows"] if row["kind"] == "game"]
        tbd_dated = [row for row in self.parsed["rows"] if row["kind"] == "tbd-dated"]
        self.assertEqual(len(games), 26, "the PDF prints 26 dated games with a matchup and a time")
        self.assertEqual(len(tbd_dated), 1, "the December 11 championship is dated but has no matchup")
        self.assertEqual(tbd_dated[0]["date"], "2026-12-11")
        self.assertEqual(len(games) + len(tbd_dated), espn_watch.EXPECTED_DATED_ROWS)

    def test_cup_markers_and_footnotes_are_seen(self) -> None:
        self.assertEqual(self.parsed["markers"]["*"], 10, "two semifinal lines, five marked cells each")
        self.assertEqual(self.parsed["markers"]["^"], 3, "one championship line, three marked cells")
        self.assertEqual(self.parsed["footnotes"], {"semifinals": True, "championship": True})

    def test_printed_weekday_matches_the_calendar(self) -> None:
        for row in self.parsed["rows"]:
            self.assertIn(row["date"][:4], ("2026", "2027"), row["date"])

    def test_wrong_printed_weekday_is_refused(self) -> None:
        broken = fixture_text().replace("Tue. 10/20/26", "Wed. 10/20/26", 1)
        with self.assertRaises(espn_watch.MonitorError):
            espn_watch.parse_rows(broken)

    def test_empty_text_parses_to_nothing(self) -> None:
        parsed = espn_watch.parse_rows("")
        self.assertEqual(parsed["rows"], [])

    def test_unrelated_text_parses_to_nothing(self) -> None:
        parsed = espn_watch.parse_rows("This is not a schedule. Nothing to see here.")
        self.assertEqual(parsed["rows"], [])
        self.assertEqual(parsed["markers"], {"*": 0, "^": 0})

    def test_layout_independent_of_newlines(self) -> None:
        """A column-wise extractor must not silently drop rows."""
        flat = " ".join(fixture_text().split())
        parsed = espn_watch.parse_rows(flat)
        self.assertEqual(len(parsed["rows"]), espn_watch.EXPECTED_DATED_ROWS)


class CompareTests(unittest.TestCase):
    def setUp(self) -> None:
        self.feed = feed()
        self.parsed = espn_watch.parse_rows(fixture_text())

    def test_the_shipped_snapshot_matches_the_pdf(self) -> None:
        self.assertEqual(espn_watch.compare(self.feed, self.parsed), [])

    def test_every_snapshot_row_cites_the_pdf_it_came_from(self) -> None:
        rows = espn_watch.snapshot_rows(self.feed)
        self.assertEqual(len(rows), 20)
        for row in rows:
            self.assertTrue(
                row["sources"][0]["url"].endswith("2026-27-ESPN-Radio-Schedule.pdf"),
                f"{row['id']} must lead with the PDF that printed it",
            )

    def test_pacific_times_are_the_printed_eastern_times_minus_three_hours(self) -> None:
        printed = {(row["date"], f"{row['away']} at {row['home']}"): row["et"]
                   for row in self.parsed["rows"] if row["kind"] == "game"}
        for row in espn_watch.snapshot_rows(self.feed):
            if not row.get("start_pt"):
                continue
            matchup = row["title"].replace("NBA on ESPN Radio: ", "")
            self.assertEqual(
                row["start_pt"], espn_watch.et_to_pt(printed[(row["date"], matchup)]),
                f"{row['id']} does not match the printed ET time",
            )

    def test_changed_time_is_reported(self) -> None:
        broken = fixture_text().replace("Sun. 2/28/27 LA Lakers Dallas 3:30 PM",
                                       "Sun. 2/28/27 LA Lakers Dallas 4:00 PM", 1)
        differences = espn_watch.compare(self.feed, espn_watch.parse_rows(broken))
        self.assertTrue(any("printed ET time for" in item for item in differences), differences)

    def test_changed_matchup_is_reported(self) -> None:
        broken = fixture_text().replace("Fri. 11/13/26 Golden State San Antonio 9:30 PM",
                                        "Fri. 11/13/26 Golden State Denver 9:30 PM", 1)
        differences = espn_watch.compare(self.feed, espn_watch.parse_rows(broken))
        self.assertTrue(any("now prints" in item for item in differences), differences)

    def test_removed_game_is_reported(self) -> None:
        broken = fixture_text().replace("Thu. 1/7/27 Boston LA Lakers 10:00 PM\n", "", 1)
        differences = espn_watch.compare(self.feed, espn_watch.parse_rows(broken))
        self.assertTrue(any("no longer prints a game on that date" in item for item in differences),
                        differences)

    def test_added_game_is_reported(self) -> None:
        broken = fixture_text().replace(
            "Thu. 1/7/27 Boston LA Lakers 10:00 PM",
            "Thu. 1/7/27 Boston LA Lakers 10:00 PM\nWed. 1/13/27 Miami Boston 7:00 PM",
            1,
        )
        differences = espn_watch.compare(self.feed, espn_watch.parse_rows(broken))
        self.assertTrue(any("no row for it" in item for item in differences), differences)

    def test_missing_cup_markers_are_reported(self) -> None:
        broken = fixture_text().replace("TBD* TBD* TBD* TBD* TBD*\n", "")
        differences = espn_watch.compare(self.feed, espn_watch.parse_rows(broken))
        self.assertTrue(any("'*' TBD marker" in item for item in differences), differences)

    def test_snapshot_row_title_drift_is_reported(self) -> None:
        """The comparison reads the matchup back out of the row title, so a
        title that no longer matches the PDF fails instead of passing."""
        broken = feed()
        row = espn_watch.snapshot_rows(broken)[0]
        row["title"] = "NBA on ESPN Radio: Philadelphia at Brooklyn"
        differences = espn_watch.compare(broken, self.parsed)
        self.assertTrue(any("no row for it" in item or "no longer prints" in item for item in differences),
                        differences)

    def test_unparseable_text_is_unavailable_not_clear(self) -> None:
        parsed = espn_watch.parse_rows("garbled output from a broken extractor")
        with self.assertRaises(espn_watch.MonitorError):
            espn_watch.compare(self.feed, parsed)


class EtConversionTests(unittest.TestCase):
    def test_printed_eastern_times_convert_to_pacific(self) -> None:
        self.assertEqual(espn_watch.et_to_pt("7:00 PM"), "16:00")
        self.assertEqual(espn_watch.et_to_pt("12:00 PM"), "09:00")
        self.assertEqual(espn_watch.et_to_pt("3:00 AM"), "00:00")
        self.assertEqual(espn_watch.et_to_pt("10:00 PM"), "19:00")

    def test_a_time_that_would_wrap_the_day_is_refused(self) -> None:
        """A printed ET time before 3:00 a.m. would land on the previous Pacific
        date, which no row may silently do."""
        for et in ("12:30 AM", "1:00 AM", "2:59 AM"):
            with self.assertRaises(espn_watch.MonitorError):
                espn_watch.et_to_pt(et)


class ReportTests(unittest.TestCase):
    def test_clear_report_names_the_source_and_the_bounds(self) -> None:
        parsed = espn_watch.parse_rows(fixture_text())
        report = espn_watch.make_report(
            "clear", espn_watch.DEFAULT_PDF, [], "2026-09-27",
            {"dated": 26, "games": 25, "tbd_dated": 1, "in_window": 17,
             "markers": {"*": 10, "^": 3}, "snapshot": 20, "snapshot_dated": 17, "snapshot_tbd": 3},
        )
        self.assertIn("2026-27-ESPN-Radio-Schedule.pdf", report)
        self.assertIn("outside this snapshot's window", report)
        self.assertIn("does not confirm that KTCT 1050", report)
        self.assertEqual(parsed["markers"], {"*": 10, "^": 3})

    def test_unavailable_report_never_reads_as_clear(self) -> None:
        report = espn_watch.make_report("unavailable", espn_watch.DEFAULT_PDF,
                                        ["- the fetch failed"], "2026-09-27", {})
        self.assertIn("could not be completed", report)
        self.assertNotIn("No differences found", report)


class CliTests(unittest.TestCase):
    def test_unparseable_input_is_unavailable_and_quotes_the_extracted_text(self) -> None:
        """A parse failure is the one moment a reader needs to see what the PDF text
        extractor actually produced, so the report has to carry a short excerpt."""
        import tempfile
        from unittest import mock

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "not-a-schedule.txt"
            source.write_text("this is not the schedule at all\njust some prose\n", encoding="utf-8")
            report = Path(tmp) / "report.md"
            argv = ["espn_watch.py", "--input", str(source), "--report", str(report)]
            with mock.patch.object(sys, "argv", argv):
                code = espn_watch.main()
            body = report.read_text(encoding="utf-8")
            self.assertEqual(code, 3, "an unparseable read is unavailable, never clear")
            self.assertIn("could not be completed", body)
            self.assertIn("Extracted text begins", body)
            self.assertIn("this is not the schedule at all", body)
            self.assertNotIn("No differences found", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
