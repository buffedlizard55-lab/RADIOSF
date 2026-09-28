#!/usr/bin/env python3
"""Offline tests for the read-only MLB postseason source monitor.

The monitor's contract is the thing under test: games are matched on the API's
own gamePk, a date may be carried by one grouped row or several per-game rows,
and a first pitch is compared as an instant rather than as a yes/no. Every test
here runs against saved or synthetic responses, never the network.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import source_watch  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
REAL_FIXTURE = FIXTURES / "mlb_postseason_2026-09-28.json"
TODAY = "2026-09-28"


class SourceWatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.feed = json.loads((ROOT / "data" / "broadcasts.json").read_text(encoding="utf-8"))
        cls.expected = source_watch.expected_schedule(cls.feed, TODAY)
        cls.real = json.loads(REAL_FIXTURE.read_text(encoding="utf-8"))

    # -- helpers -------------------------------------------------------------
    def api_from_snapshot(self) -> dict:
        """An API response that agrees with the snapshot exactly."""
        dates = []
        for game_date, bucket in sorted(self.expected.items()):
            games = []
            for pk, item in sorted(bucket["games"].items()):
                games.append({
                    "gamePk": pk,
                    "officialDate": game_date,
                    "gameDate": item["first_pitch"] or f"{game_date}T07:33:00Z",
                    "description": item["description"],
                    "venue": {"name": item["venue"]},
                    "teams": {"away": {"team": {"name": item["away"]}},
                              "home": {"team": {"name": item["home"]}}},
                    "ifNecessary": "Y" if item["conditional"] else "N",
                    # Real API shape: startTimeTBD lives inside "status".
                    "status": {"detailedState": "Scheduled",
                               "startTimeTBD": item["first_pitch"] is None},
                })
            dates.append({"date": game_date, "games": games})
        return {"dates": dates}

    def find_game(self, api: dict, pk: int) -> dict:
        for block in api["dates"]:
            for game in block["games"]:
                if game["gamePk"] == pk:
                    return game
        raise AssertionError(f"test helper could not find gamePk {pk}")

    def diff(self, api: dict) -> list[str]:
        return source_watch.compare(self.expected, source_watch.observed_schedule(api, TODAY))

    # -- the shipped state ---------------------------------------------------
    def test_snapshot_matches_the_real_api_response(self):
        """The published feed agrees with the response fetched on 2026-09-28."""
        self.assertEqual(self.diff(self.real), [])
        self.assertEqual(len(self.expected), 28, "the API's 28 postseason dates")
        self.assertEqual(sum(b["count"] for b in self.expected.values()), 53,
                         "the API's 53 postseason games")
        self.assertEqual(sum(len(b["row_ids"]) for b in self.expected.values()), 37,
                         "twelve per-game Wild Card rows plus twenty-five grouped dates")

    def test_a_scheduled_date_is_carried_by_several_rows(self):
        """September 29 is four per-game rows, and they aggregate into one date."""
        bucket = self.expected["2026-09-29"]
        self.assertEqual(len(bucket["row_ids"]), 4)
        self.assertEqual(bucket["count"], 4)
        self.assertEqual(
            {pk: item["first_pitch"] for pk, item in bucket["games"].items()},
            {849845: "2026-09-29T18:00:00Z", 849849: "2026-09-29T21:00:00Z",
             849851: "2026-09-30T00:00:00Z", 849843: "2026-09-30T02:00:00Z"},
            "each per-game row records the API instant its clock time came from")

    def test_an_unscheduled_date_is_one_grouped_row_with_no_time(self):
        bucket = self.expected["2026-10-03"]
        self.assertEqual(len(bucket["row_ids"]), 1)
        self.assertEqual(bucket["count"], 4)
        for item in bucket["games"].values():
            self.assertIsNone(item["first_pitch"])
            self.assertIsNone(item["start_pt"])

    def test_the_api_placeholder_never_becomes_a_clock_time(self):
        """The API fills an unpublished first pitch with 07:33Z, 08:33Z or
        10:33Z. Those instants convert into plausible-looking early-morning
        Pacific times, so the invariant that matters is that no game the API
        marks TBD is carried in the snapshot with a start time at all."""
        observed = source_watch.observed_schedule(self.real, TODAY)
        placeholders = {"07:33:00Z", "08:33:00Z", "10:33:00Z"}
        tbd = 0
        for game_date, bucket in observed.items():
            for pk, game in bucket["games"].items():
                if not game["start_time_tbd"]:
                    continue
                tbd += 1
                self.assertIn(game["game_date_utc"][11:], placeholders,
                              f"gamePk {pk} is TBD but carries an unusual instant")
                self.assertIsNone(self.expected[game_date]["games"][pk]["start_pt"],
                                  f"gamePk {pk} is TBD in the API but timed in the snapshot")
        self.assertEqual(tbd, 41, "41 of the 53 postseason games are still unscheduled")
        # The conversion itself is still exact, which is why the guard above matters.
        self.assertEqual(source_watch.utc_to_pt("2026-10-03T07:33:00Z"), "2026-10-03 12:33 AM PT")

    def test_snapshot_response_rebuilt_from_the_feed_is_clear(self):
        self.assertEqual(self.diff(self.api_from_snapshot()), [])

    # -- drift detection -----------------------------------------------------
    def test_newly_published_first_pitch_is_reported_with_its_pacific_time(self):
        api = self.api_from_snapshot()
        game = self.find_game(api, 849835)          # ALDS 'A' Game 1, still TBD in the snapshot
        game["gameDate"] = "2026-10-03T20:00:00Z"
        game["status"]["startTimeTBD"] = False
        differences = self.diff(api)
        self.assertTrue(any("2026-10-03" in d and "now supplies a start time" in d
                            for d in differences), differences)
        self.assertTrue(any("1:00 PM PT" in d and "gamePk 849835" in d for d in differences),
                        "the report gives the Pacific time a human would transcribe")

    def test_a_resolved_placeholder_is_a_change_to_a_known_game(self):
        """NL Wild Card #3 -> PHI/ARI must not read as one game lost and one found."""
        api = self.api_from_snapshot()
        self.find_game(api, 849845)["teams"]["away"]["team"]["name"] = "Philadelphia Phillies"
        differences = self.diff(api)
        joined = "\n".join(differences)
        self.assertIn("away team changed for gamePk 849845", joined)
        self.assertIn("'PHI/ARI'", joined)
        self.assertIn("'Philadelphia Phillies'", joined)
        self.assertNotIn("no longer returns", joined)
        self.assertNotIn("now returns gamePk", joined)

    def test_venue_change_is_reported(self):
        api = self.api_from_snapshot()
        self.find_game(api, 849809)["venue"]["name"] = "Truist Park"
        self.assertTrue(any("venue changed for gamePk 849809" in d for d in self.diff(api)))

    def test_if_necessary_change_is_reported(self):
        api = self.api_from_snapshot()
        self.find_game(api, 849844)["ifNecessary"] = "N"
        self.assertTrue(any("if-necessary marker changed for gamePk 849844" in d
                            for d in self.diff(api)))

    def test_withdrawn_start_time_is_reported(self):
        api = self.api_from_snapshot()
        game = self.find_game(api, 849845)
        game["status"]["startTimeTBD"] = True
        game["gameDate"] = "2026-09-29T07:33:00Z"
        differences = self.diff(api)
        self.assertTrue(any("withdrawn a start time" in d and "gamePk 849845" in d
                            for d in differences), differences)

    def test_a_moved_start_time_is_reported(self):
        api = self.api_from_snapshot()
        self.find_game(api, 849845)["gameDate"] = "2026-09-29T20:00:00Z"
        differences = self.diff(api)
        self.assertTrue(any("first pitch changed for gamePk 849845" in d for d in differences))
        self.assertTrue(any("1:00 PM PT" in d for d in differences),
                        "the report shows the new Pacific time as well as the old one")

    def test_a_new_game_is_reported(self):
        api = self.api_from_snapshot()
        api["dates"][0]["games"].append({
            "gamePk": 999999, "officialDate": "2026-09-29",
            "gameDate": "2026-09-29T23:00:00Z", "description": "Extra game",
            "venue": {"name": "Somewhere"},
            "teams": {"away": {"team": {"name": "Away"}}, "home": {"team": {"name": "Home"}}},
            "ifNecessary": "N", "status": {"startTimeTBD": False},
        })
        differences = self.diff(api)
        self.assertTrue(any("now returns gamePk 999999" in d for d in differences), differences)
        self.assertTrue(any("game count changed from 4 in the snapshot to 5" in d
                            for d in differences))

    def test_a_removed_game_is_reported(self):
        api = self.api_from_snapshot()
        block = next(b for b in api["dates"] if b["date"] == "2026-09-29")
        block["games"] = [g for g in block["games"] if g["gamePk"] != 849843]
        differences = self.diff(api)
        self.assertTrue(any("no longer returns gamePk 849843" in d for d in differences), differences)

    def test_a_new_date_is_reported(self):
        api = self.api_from_snapshot()
        api["dates"].append({"date": "2026-11-01", "games": [{
            "gamePk": 999998, "officialDate": "2026-11-01",
            "gameDate": "2026-11-01T20:00:00Z", "description": "New postseason game",
            "venue": {"name": "Somewhere"},
            "teams": {"away": {"team": {"name": "Away"}}, "home": {"team": {"name": "Home"}}},
            "ifNecessary": "N", "status": {"startTimeTBD": False},
        }]})
        self.assertTrue(any("2026-11-01" in d and "no row" in d for d in self.diff(api)))

    def test_a_missing_date_is_reported(self):
        api = self.api_from_snapshot()
        removed = api["dates"].pop(0)["date"]
        self.assertTrue(any(removed in d and "API now has none" in d for d in self.diff(api)))

    def test_past_dates_are_ignored(self):
        api = {"dates": [{"date": "2026-09-26", "games": [{
            "gamePk": 1, "officialDate": "2026-09-26", "gameDate": "2026-09-26T20:00:00Z",
            "description": "Already played", "venue": {"name": "Somewhere"},
            "teams": {"away": {"team": {"name": "A"}}, "home": {"team": {"name": "B"}}},
            "ifNecessary": "N", "status": {"startTimeTBD": False},
        }]}]}
        self.assertEqual(source_watch.observed_schedule(api, TODAY), {})

    def test_the_pre_split_state_differs_from_the_snapshot_on_exactly_the_moved_fields(self):
        """Regression: the drift that opened issue #13, rebuilt field by field.

        The snapshot as published on 2026-09-27 had one grouped row per Wild Card
        date, no clock times, and the API's older placeholders. Feeding that
        older state back through the monitor must name every field that moved —
        the twelve published first pitches and the four renamed bracket slots —
        and nothing else.
        """
        api = copy.deepcopy(self.real)
        old_placeholders = {
            849845: ("NL Wild Card #3", None), 849841: ("NL Wild Card #3", None),
            849844: ("NL Wild Card #3", None),
            849849: (None, "HOU/TEX"), 849846: (None, "HOU/TEX"), 849850: (None, "HOU/TEX"),
            849835: ("AL 4/5 Winner", None), 849839: ("AL 4/5 Winner", None),
            849836: ("AL 4/5 Winner", None),
        }
        for block in api["dates"]:
            for game in block["games"]:
                pk = game["gamePk"]
                if pk in old_placeholders:
                    away, home = old_placeholders[pk]
                    if away:
                        game["teams"]["away"]["team"]["name"] = away
                    if home:
                        game["teams"]["home"]["team"]["name"] = home
                if block["date"] in ("2026-09-29", "2026-09-30", "2026-10-01"):
                    game["gameDate"] = block["date"] + "T07:33:00Z"
                    game["status"]["startTimeTBD"] = True
        differences = self.diff(api)
        joined = "\n".join(differences)
        for date in ("2026-09-29", "2026-09-30", "2026-10-01"):
            self.assertIn(f"**{date}**", joined)
            self.assertIn("the API has withdrawn a start time the snapshot shows", joined,
                          f"{date} published four first pitches this snapshot now carries")
        self.assertIn("away team changed for gamePk 849845", joined)
        self.assertIn("'NL Wild Card #3'", joined)
        self.assertIn("'HOU/TEX'", joined)
        self.assertIn("'AL 4/5 Winner'", joined)
        self.assertEqual(
            sorted(d.split("**")[1] for d in differences),
            ["2026-09-29", "2026-09-30", "2026-10-01", "2026-10-03", "2026-10-05", "2026-10-10"],
            "only the dates whose bracket slots or first pitches moved are reported")

    # -- fail closed on the source -------------------------------------------
    def test_a_source_field_the_monitor_needs_is_never_optional(self):
        for field in ("gamePk", "gameDate", "venue", "description", "teams", "ifNecessary", "status"):
            api = self.api_from_snapshot()
            del self.find_game(api, 849845)[field]
            with self.assertRaises(source_watch.MonitorError, msg=field):
                source_watch.observed_schedule(api, TODAY)

    def test_malformed_responses_fail_closed(self):
        bad = [
            [],
            {},
            {"dates": [{"date": "2026-02-30", "games": [{
                "gamePk": 1, "officialDate": "2026-02-30", "gameDate": "2026-02-30T07:33:00Z",
                "description": "Invalid date", "venue": {"name": "x"},
                "teams": {"away": {"team": {"name": "A"}}, "home": {"team": {"name": "B"}}},
                "ifNecessary": "N", "status": {"startTimeTBD": True}}]}]},
            {"dates": [{"date": "2026-09-29", "games": [{
                "gamePk": 1, "officialDate": "2026-09-29", "description": "No instant",
                "venue": {"name": "x"},
                "teams": {"away": {"team": {"name": "A"}}, "home": {"team": {"name": "B"}}},
                "ifNecessary": "N", "status": {"startTimeTBD": True}}]}]},
            {"dates": [{"date": "2026-09-29", "games": [{
                "gamePk": 1, "officialDate": "2026-09-29", "gameDate": "2026-09-29T07:33:00Z",
                "description": "No startTimeTBD", "venue": {"name": "x"},
                "teams": {"away": {"team": {"name": "A"}}, "home": {"team": {"name": "B"}}},
                "ifNecessary": "N", "status": {}}]}]},
            {"dates": [{"date": "2026-09-29", "games": [{
                "gamePk": 1, "officialDate": "2026-09-29", "gameDate": "2026-09-29T07:33:00Z",
                "description": "Bad marker", "venue": {"name": "x"},
                "teams": {"away": {"team": {"name": "A"}}, "home": {"team": {"name": "B"}}},
                "ifNecessary": "maybe", "status": {"startTimeTBD": True}}]}]},
            {"dates": [{"date": "2026-09-29", "games": "not a list"}]},
        ]
        for document in bad:
            with self.assertRaises(source_watch.MonitorError):
                source_watch.observed_schedule(document, TODAY)

    def test_a_duplicated_game_fails_closed(self):
        api = self.api_from_snapshot()
        block = next(b for b in api["dates"] if b["date"] == "2026-09-29")
        block["games"].append(copy.deepcopy(block["games"][0]))
        with self.assertRaises(source_watch.MonitorError):
            source_watch.observed_schedule(api, TODAY)

    # -- fail closed on the snapshot -----------------------------------------
    def snapshot_with(self, mutate) -> dict:
        """A copy of the shipped feed with the MLB rows edited by `mutate`.

        `mutate` receives the live `broadcasts` list, so appending or removing a
        row actually changes the feed the monitor is given.
        """
        feed = copy.deepcopy(self.feed)
        mutate(feed["broadcasts"])
        return feed

    def test_a_slot_without_a_gamepk_fails_closed(self):
        def drop_pk(broadcasts):
            rows = [r for r in broadcasts if str(r['id']).startswith('mlb-post-')]
            del rows[0]["game_details"][0]["game_pk"]
        with self.assertRaises(source_watch.MonitorError):
            source_watch.expected_schedule(self.snapshot_with(drop_pk), TODAY)

    def test_a_grouped_row_may_not_cite_a_first_pitch(self):
        def add_pitch(broadcasts):
            rows = [r for r in broadcasts if str(r['id']).startswith('mlb-post-')]
            grouped = next(r for r in rows if r["date"] == "2026-10-03")
            grouped["sources"].append({"label": "first pitch 2026-10-03T20:00:00Z",
                                       "url": "https://example.com"})
        with self.assertRaises(source_watch.MonitorError):
            source_watch.expected_schedule(self.snapshot_with(add_pitch), TODAY)

    def test_a_clock_time_without_a_cited_instant_fails_closed(self):
        def strip_pitch(broadcasts):
            rows = [r for r in broadcasts if str(r['id']).startswith('mlb-post-')]
            per_game = next(r for r in rows if r["id"] == "mlb-post-849845")
            per_game["sources"] = [s for s in per_game["sources"] if "first pitch" not in s["label"]]
        with self.assertRaises(source_watch.MonitorError):
            source_watch.expected_schedule(self.snapshot_with(strip_pitch), TODAY)

    def test_the_same_game_in_two_rows_fails_closed(self):
        def duplicate(broadcasts):
            per_game = next(r for r in broadcasts if r["id"] == "mlb-post-849845")
            clone = copy.deepcopy(per_game)
            clone["id"] = "mlb-post-849845-copy"
            broadcasts.append(clone)
        with self.assertRaises(source_watch.MonitorError):
            source_watch.expected_schedule(self.snapshot_with(duplicate), TODAY)

    # -- the three outcomes stay apart ---------------------------------------
    def run_cli(self, payload: str | dict) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            api_path = directory / "api.json"
            report_path = directory / "report.md"
            output_path = directory / "github-output.txt"
            api_path.write_text(payload if isinstance(payload, str) else json.dumps(payload),
                                encoding="utf-8")
            result = subprocess.run([
                sys.executable, str(Path(__file__).with_name("source_watch.py")),
                "--today", TODAY, "--input", str(api_path),
                "--report", str(report_path), "--github-output", str(output_path),
            ], check=False, capture_output=True, text=True)
            result.report_text = report_path.read_text(encoding="utf-8")
            result.output_text = output_path.read_text(encoding="utf-8")
            return result

    def test_cli_reports_clear_offline(self):
        result = self.run_cli(self.real)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("status=clear", result.output_text)
        self.assertIn("No differences found", result.report_text)

    def test_cli_reports_drift_with_exit_two(self):
        api = self.api_from_snapshot()
        self.find_game(api, 849845)["venue"]["name"] = "Citizens Bank Park"
        result = self.run_cli(api)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("status=changed", result.output_text)
        self.assertIn("Schedule drift detected", result.report_text)
        self.assertIn("venue changed for gamePk 849845", result.report_text)

    def test_an_unreadable_source_is_never_reported_as_drift(self):
        result = self.run_cli("not json")
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn("status=unavailable", result.output_text)
        self.assertIn("not evidence that the source or snapshot changed", result.report_text)
        self.assertNotIn("Schedule drift detected", result.report_text)

    def test_the_report_disclaims_automatic_publication(self):
        report = source_watch.make_report("changed", TODAY, "https://example.com",
                                          ["- schedule drift"], "2026-09-28")
        self.assertIn("Published snapshot date: 2026-09-28", report)
        self.assertIn("matched on the API's own `gamePk`", report)
        self.assertIn("does not confirm a Bay Area station's per-game clearance", report)
        self.assertIn("change `data/broadcasts.json`", report)
        self.assertIn("or publish a new GitHub Pages snapshot", report)


if __name__ == "__main__":
    unittest.main()
