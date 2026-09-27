#!/usr/bin/env python3
"""Offline tests for the read-only MLB source monitor."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source_watch  # noqa: E402


class SourceWatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        feed_path = Path(__file__).resolve().parents[1] / "data" / "broadcasts.json"
        cls.feed = json.loads(feed_path.read_text(encoding="utf-8"))
        cls.today = "2026-09-27"
        cls.expected = source_watch.expected_schedule(cls.feed, cls.today)

    def api_fixture(self):
        dates = []
        for game_date, expected in sorted(self.expected.items()):
            games = []
            for description, away, home, conditional in expected["games"].elements():
                games.append({
                    "officialDate": game_date,
                    "description": description,
                    "teams": {"away": {"team": {"name": away}},
                              "home": {"team": {"name": home}}},
                    "ifNecessary": "Y" if conditional else "N",
                    # Real API shape: startTimeTBD lives inside "status".
                    "status": {"detailedState": "Scheduled", "startTimeTBD": True},
                })
            dates.append({"date": game_date, "games": games})
        return {"dates": dates}

    def test_snapshot_baseline_matches_synthetic_api_response(self):
        observed = source_watch.observed_schedule(self.api_fixture(), self.today)
        self.assertEqual(source_watch.compare(self.expected, observed), [])
        self.assertEqual(len(self.expected), 28)
        self.assertEqual(sum(item["count"] for item in self.expected.values()), 53)

    def test_real_api_response_shape_matches_snapshot(self):
        # Regression: the live API nests startTimeTBD under "status". The fixture
        # is the full response fetched 2026-09-27, enriched with the matchups
        # transcribed from the API's compact fields response on the same date.
        fixture = Path(__file__).resolve().parent / "fixtures" / "mlb_postseason_2026-09-27.json"
        document = json.loads(fixture.read_text(encoding="utf-8"))
        for block in document["dates"]:
            for game in block["games"]:
                self.assertNotIn("startTimeTBD", game)
        observed = source_watch.observed_schedule(document, self.today)
        self.assertEqual(source_watch.compare(self.expected, observed), [])

    def test_new_game_date_is_reported(self):
        api = self.api_fixture()
        api["dates"].append({"date": "2026-11-01", "games": [{
            "officialDate": "2026-11-01", "description": "New postseason game",
            "teams": {"away": {"team": {"name": "Away Team"}},
                      "home": {"team": {"name": "Home Team"}}},
            "ifNecessary": "N", "status": {"startTimeTBD": True},
        }]})
        observed = source_watch.observed_schedule(api, self.today)
        self.assertTrue(any("2026-11-01" in item and "no row" in item for item in
                            source_watch.compare(self.expected, observed)))

    def test_changed_description_and_new_start_time_are_reported(self):
        api = self.api_fixture()
        game = api["dates"][0]["games"][0]
        game["description"] = "Renamed postseason game"
        game["status"]["startTimeTBD"] = False
        observed = source_watch.observed_schedule(api, self.today)
        differences = source_watch.compare(self.expected, observed)
        self.assertTrue(any("Newly returned or renamed" in item for item in differences))
        self.assertTrue(any("now supplies a start time" in item for item in differences))

    def test_changed_matchup_or_if_necessary_marker_is_reported(self):
        api = self.api_fixture()
        game = api["dates"][0]["games"][0]
        game["teams"]["away"]["team"]["name"] = "Newly Qualified Team"
        game["ifNecessary"] = "Y"
        differences = source_watch.compare(self.expected,
            source_watch.observed_schedule(api, self.today))
        self.assertTrue(any("Matchup or conditional marker now returned" in item and
                            "Newly Qualified Team" in item for item in differences))
        self.assertTrue(any("Matchup or conditional marker no longer returned" in item and
                            "Chicago White Sox" in item for item in differences))

    def test_missing_matchup_fields_fail_closed(self):
        api = self.api_fixture()
        del api["dates"][0]["games"][0]["teams"]
        with self.assertRaises(source_watch.MonitorError):
            source_watch.observed_schedule(api, self.today)

    def test_past_dates_are_ignored(self):
        api = {"dates": [{"date": "2026-09-26", "games": [{
            "officialDate": "2026-09-26", "description": "Already played",
            "status": {"startTimeTBD": False},
        }]}]}
        self.assertEqual(source_watch.observed_schedule(api, self.today), {})

    def test_missing_future_date_is_reported(self):
        api = self.api_fixture()
        removed_date = api["dates"].pop(0)["date"]
        observed = source_watch.observed_schedule(api, self.today)
        self.assertTrue(any(removed_date in item and "API now has none" in item for item in
                            source_watch.compare(self.expected, observed)))

    def test_malformed_api_fails_closed(self):
        with self.assertRaises(source_watch.MonitorError):
            source_watch.observed_schedule([], self.today)
        with self.assertRaises(source_watch.MonitorError):
            source_watch.observed_schedule({}, self.today)
        with self.assertRaises(source_watch.MonitorError):
            source_watch.observed_schedule({"dates": [{"date": "2026-02-30", "games": [{
                "officialDate": "2026-02-30", "description": "Invalid date", "startTimeTBD": True,
            }]}]}, self.today)
        with self.assertRaises(source_watch.MonitorError):
            source_watch.observed_schedule({"dates": [{"date": "2026-09-27", "games": [{
                "officialDate": "2026-09-27", "startTimeTBD": True,
            }]}]}, self.today)

    def test_cli_can_run_offline_and_write_github_action_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            api_path = directory / "api.json"
            report_path = directory / "report.md"
            output_path = directory / "github-output.txt"
            api_path.write_text(json.dumps(self.api_fixture()), encoding="utf-8")
            result = subprocess.run([
                sys.executable, str(Path(__file__).with_name("source_watch.py")),
                "--today", self.today, "--input", str(api_path),
                "--report", str(report_path), "--github-output", str(output_path),
            ], check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=clear", output_path.read_text(encoding="utf-8"))
            self.assertIn("No differences found", report_path.read_text(encoding="utf-8"))

    def test_unavailable_source_is_not_reported_as_schedule_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            api_path = directory / "bad-api.json"
            report_path = directory / "report.md"
            output_path = directory / "github-output.txt"
            api_path.write_text("not json", encoding="utf-8")
            result = subprocess.run([
                sys.executable, str(Path(__file__).with_name("source_watch.py")),
                "--today", self.today, "--input", str(api_path),
                "--report", str(report_path), "--github-output", str(output_path),
            ], check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertIn("status=unavailable", output_path.read_text(encoding="utf-8"))
            report = report_path.read_text(encoding="utf-8")
            self.assertIn("not evidence that the source or snapshot changed", report)
            self.assertNotIn("Schedule drift detected", report)

    def test_issue_report_disclaims_automatic_publication(self):
        report = source_watch.make_report(
            "changed", self.today, "https://example.com", ["- schedule drift"], "2026-09-27"
        )
        self.assertIn("Published snapshot date: 2026-09-27", report)
        self.assertIn("does not confirm a Bay Area station's per-game clearance", report)
        self.assertIn("does not", report)
        self.assertIn("change `data/broadcasts.json`", report)
        self.assertIn("or publish a new GitHub Pages snapshot", report)


if __name__ == "__main__":
    unittest.main()
