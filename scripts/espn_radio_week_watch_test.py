#!/usr/bin/env python3
"""Offline tests for the weekly ESPN Radio grid monitor.

No network. The shipped fixture (scripts/fixtures/espn_radio_week_2026-09-27.json)
replays the page as read on 2026-09-27 — four games, all of them already played
by the time the snapshot was refreshed — against dated scoreboard payloads
shaped from ESPN's live scoreboard JSON. The other cases build small grids and
scoreboards inline to prove the monitor's three hard rules:

  * a grid that cannot be parsed, dated, or that dates ambiguously is
    **unavailable** — never "clear";
  * no row of the snapshot is ever justified by the grid alone, so a future
    unlisted game is reported for review, never added;
  * a scoreboard that cannot be consulted makes its row "unknown", which never
    counts as a match and never counts as a contradiction.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import espn_radio_week_watch as watch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FEED_PATH = ROOT / "data" / "broadcasts.json"
FIXTURE = ROOT / "scripts" / "fixtures" / "espn_radio_week_2026-09-27.json"


def shipped_feed(broadcasts=None):
    feed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
    if broadcasts is not None:
        feed["broadcasts"] = broadcasts
    return feed


def team(location: str, name: str):
    return {"location": location, "name": name, "abbreviation": name[:3].upper(),
            "displayName": f"{location} {name}", "shortDisplayName": f"{location} {name}"}


def board(*pairs):
    """A scoreboard payload holding one event per (away, home) team-name pair."""
    events = []
    for away, home in pairs:
        events.append({"name": f"{away} at {home}", "competitions": [{"competitors": [
            {"homeAway": "away", "team": team(*away.split(" ", 1)) if " " in away else team(away, away)},
            {"homeAway": "home", "team": team(*home.split(" ", 1)) if " " in home else team(home, home)},
        ]}]})
    return {"events": events}


EMPTY = {"events": []}


def grid_html(day_rows):
    """day_rows: {"WEDNESDAY": [("MLB", "Mets @ Rangers", "7:30 p.m."), ...], ...}"""
    parts = ["<html><body>"]
    for day in ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"):
        parts.append(f"<table><thead><tr><th>{day}</th><th>Time (Eastern)</th></tr></thead><tbody>")
        for sport, matchup, time in day_rows.get(day, []):
            if sport is None:
                parts.append(f"<tr><td>{matchup}</td><td>{time}</td></tr>")
            else:
                parts.append(f"<tr><td><a href='#'>{sport}: {matchup}</a></td><td>{time}</td></tr>")
        parts.append("</tbody></table>")
    parts.append("</body></html>")
    return "".join(parts)


def fixed_scoreboards(boards):
    def scoreboard(sport, day):
        return boards.get(f"{sport}|{day}")
    return scoreboard


def run_fixture(broadcasts, boards, today, day_rows):
    feed = shipped_feed(broadcasts)
    return watch.run(feed, today, grid_html(day_rows), fixed_scoreboards(boards))


class ParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.supported = set(json.loads(FEED_PATH.read_text())["meta"]["espn_week_watch"]["sports"])

    def test_day_cells_become_dated_weekday_rows(self) -> None:
        html = grid_html({"WEDNESDAY": [("MLB", "Mets @ Rangers", "7:30 p.m.")],
                          "SATURDAY": [("CFB", "Wisconsin @ Penn State", "4:30 p.m.")]})
        parsed = watch.parse_grid(html, self.supported)
        self.assertEqual(len(parsed["games"]), 2)
        by_sport = {g["sport"]: g for g in parsed["games"]}
        self.assertEqual(by_sport["MLB"]["weekday"], "WEDNESDAY")
        self.assertEqual(by_sport["MLB"]["time_et"], "19:30")
        self.assertEqual(by_sport["CFB"]["away"], "Wisconsin")
        self.assertEqual(by_sport["CFB"]["home"], "Penn State")

    def test_inline_time_on_the_same_line_is_captured(self) -> None:
        html = grid_html({"SATURDAY": [("CFB", "Texas A&M @ LSU 8:00 p.m.", None)]})
        parsed = watch.parse_grid(html, self.supported)
        self.assertEqual(parsed["games"][0]["time_et"], "20:00")
        self.assertEqual(parsed["games"][0]["away"], "Texas A&M")
        self.assertEqual(parsed["games"][0]["home"], "LSU")

    def test_doubleheader_suffix_is_stripped(self) -> None:
        html = grid_html({"SUNDAY": [("MLB", "Cubs @ Reds (Game 1) 1:00 p.m.", None)]})
        parsed = watch.parse_grid(html, self.supported)
        self.assertEqual(parsed["games"][0]["away"], "Cubs")
        self.assertEqual(parsed["games"][0]["home"], "Reds")

    def test_show_lines_are_not_games(self) -> None:
        html = grid_html({"SUNDAY": [(None, "Sunday Morning", "10:00 a.m."),
                                     (None, "GameNight", "10:00 p.m."),
                                     ("NFL", " Packers @ Bears", "8:20 p.m.")]})
        parsed = watch.parse_grid(html, self.supported)
        self.assertEqual(len(parsed["games"]), 1)

    def test_unsupported_sport_never_parses_as_game_evidence(self) -> None:
        html = grid_html({"SATURDAY": [("BOXING", "Fury @ Usyk", "9:00 p.m.")]})
        with self.assertRaises(watch.MonitorError):
            watch.parse_grid(html, self.supported)

    def test_game_without_a_day_heading_is_refused(self) -> None:
        html = ("<html><body><a>MLB: Mets @ Rangers</a><td>7:30 p.m.</td></body></html>")
        with self.assertRaises(watch.MonitorError):
            watch.parse_grid(html, self.supported)

    def test_game_without_any_time_is_refused_not_quietly_dropped(self) -> None:
        html = grid_html({"WEDNESDAY": [("MLB", "Mets @ Rangers", None)],
                          "SATURDAY": [("CFB", "Gone @ Away", "4:30 p.m.")]})
        with self.assertRaises(watch.MonitorError):
            watch.parse_grid(html, self.supported)

    def test_duplicate_week_copy_is_ignored_not_treated_as_two_weeks(self) -> None:
        first = grid_html({"WEDNESDAY": [("MLB", "Mets @ Rangers", "7:30 p.m.")]})
        html = first + first  # a second MONDAY–SUNDAY copy, as a responsive layout would print
        parsed = watch.parse_grid(html, self.supported)
        self.assertEqual(len(parsed["games"]), 1)
        self.assertEqual(parsed["games"][0]["away"], "Mets")

    def test_page_without_weekday_headings_is_refused(self) -> None:
        with self.assertRaises(watch.MonitorError):
            watch.parse_grid("<html><body><p>ESPN Radio schedule coming soon</p></body></html>",
                             self.supported)

    def test_tbd_matchups_are_reported_not_dated(self) -> None:
        html = grid_html({"WEDNESDAY": [("MLB", "TBD @ TBD", "7:30 p.m."),
                                        ("MLB", "Mets @ Rangers", "8:00 p.m.")]})
        parsed = watch.parse_grid(html, self.supported)
        self.assertEqual(len(parsed["games"]), 1)
        self.assertEqual(len(parsed["unmatchable"]), 1)
        self.assertIn("TBD @ TBD", parsed["unmatchable"][0])

    def test_amp_entity_is_unescaped_before_matching(self) -> None:
        html = grid_html({"SATURDAY": [("CFB", "Texas A&amp;M @ LSU", "8:00 p.m.")]})
        parsed = watch.parse_grid(html, self.supported)
        self.assertEqual(parsed["games"][0]["away"], "Texas A&M")


class ScoreboardMatchTests(unittest.TestCase):
    def test_full_names_match_grid_nicknames(self) -> None:
        payload = board(("New York Mets", "Texas Rangers"))
        self.assertEqual(watch.scoreboard_match(payload, "Mets", "Rangers"), "match")

    def test_absent_game_is_no_match(self) -> None:
        payload = board(("Chicago Cubs", "St. Louis Cardinals"))
        self.assertIsNone(watch.scoreboard_match(payload, "Mets", "Rangers"))

    def test_flipped_orientation_is_detected(self) -> None:
        payload = board(("Texas Rangers", "New York Mets"))
        self.assertEqual(watch.scoreboard_match(payload, "Mets", "Rangers"), "flipped")

    def test_empty_scoreboard_is_silence_not_failure(self) -> None:
        self.assertIsNone(watch.scoreboard_match(EMPTY, "Mets", "Rangers"))


class DatingTests(unittest.TestCase):
    def test_replay_of_the_live_2026_09_27_state_is_clear(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        feed = shipped_feed()
        boards = fixture["scoreboards"]
        status, differences, info, counts = watch.run(
            feed, fixture["today"], fixture["grid_html"], fixed_scoreboards(boards)
        )
        self.assertEqual(status, "clear", differences)
        self.assertEqual(counts["week_monday"], "2026-09-21")
        self.assertEqual(counts["week_sunday"], "2026-09-27")
        self.assertEqual(counts["dated_matches"], 4)
        self.assertEqual(counts["unchecked"], 0)
        self.assertEqual(differences, [])
        self.assertTrue(any("4 of the grid's dated game lines are already in the past" in line
                           for line in info))

    def test_unvalidatable_week_is_unavailable_never_clear(self) -> None:
        boards = {"MLB|2026-09-23": EMPTY, "MLB|2026-09-25": EMPTY, "MLB|2026-09-16": EMPTY,
                  "MLB|2026-09-18": EMPTY, "MLB|2026-09-30": EMPTY, "MLB|2026-10-02": EMPTY}
        status, differences, info, _c = run_fixture(
            [], boards, "2026-09-27",
            {"WEDNESDAY": [("MLB", "Mets @ Rangers", "7:30 p.m.")],
             "FRIDAY": [("MLB", "Guardians @ Royals", "7:00 p.m.")]})
        self.assertEqual(status, "unavailable")
        self.assertEqual(differences, [])
        self.assertTrue(any("no candidate week" in line for line in info))

    def test_ambiguous_week_is_unavailable(self) -> None:
        both = board(("New York Mets", "Texas Rangers"))
        boards = {"MLB|2026-09-23": both, "MLB|2026-09-30": both}
        status, _d, info, _c = run_fixture(
            [], boards, "2026-09-27",
            {"WEDNESDAY": [("MLB", "Mets @ Rangers", "7:30 p.m.")]})
        self.assertEqual(status, "unavailable")
        self.assertTrue(any("more than one candidate week" in line for line in info))

    def test_grid_a_week_behind_still_dates_to_last_week_and_clears(self) -> None:
        # today is Monday 2026-09-28; the page still prints the finished week.
        boards = {"MLB|2026-09-23": board(("New York Mets", "Texas Rangers")),
                  "MLB|2026-09-16": EMPTY, "MLB|2026-09-30": EMPTY}
        status, differences, info, counts = run_fixture(
            [], boards, "2026-09-28",
            {"WEDNESDAY": [("MLB", "Mets @ Rangers", "7:30 p.m.")]})
        self.assertEqual(status, "clear", differences)
        self.assertEqual(counts["week_monday"], "2026-09-21")
        self.assertTrue(any("already in the past" in line for line in info))

    def test_shifted_weekday_breaks_every_candidate_and_refuses_to_date(self) -> None:
        # The grid prints the game on Friday; the dated source says it is played
        # Saturday of that week. Every candidate is contradicted: no dating.
        boards = {"MLB|2026-09-25": EMPTY, "MLB|2026-09-26": board(("New York Mets", "Texas Rangers")),
                  "MLB|2026-09-18": EMPTY, "MLB|2026-09-19": EMPTY, "MLB|2026-10-02": EMPTY}
        status, _d, info, _c = run_fixture(
            [], boards, "2026-09-27",
            {"FRIDAY": [("MLB", "Mets @ Rangers", "7:30 p.m.")]})
        self.assertEqual(status, "unavailable")
        self.assertTrue(any("no candidate week" in line for line in info))


class SnapshotComparisonTests(unittest.TestCase):
    def _boards(self, day="2026-10-01"):
        return {
            f"MLB|{day}": board(("Chicago Cubs", "Cincinnati Reds")),
            "MLB|2026-09-24": EMPTY, "MLB|2026-10-08": EMPTY,
        }

    def test_future_unlisted_game_becomes_changed_with_review_links(self) -> None:
        # Grid is validated for the week of Mon 2026-09-28; the Cubs @ Reds game
        # on Wed 2026-09-30 (a day the snapshot has 1050 rows for, but not this
        # matchup) must surface as changed with both links for manual review.
        boards = self._boards("2026-09-30")
        boards["MLB|2026-09-23"] = EMPTY
        rows = [{"id": "stanford-2026-09-30", "date": "2026-09-30", "stations": ["1050"],
                 "title": "Stanford vs Somebody"}]
        status, differences, _info, counts = run_fixture(
            rows, boards, "2026-09-28",
            {"WEDNESDAY": [("MLB", "Cubs @ Reds", "7:10 p.m.")]})
        self.assertEqual(status, "changed")
        self.assertEqual(len(differences), 1)
        self.assertIn("none names this matchup", differences[0])
        self.assertIn("2026-09-30", differences[0])
        self.assertIn("join 19:10 ET", differences[0].replace("19:10", "19:10"))
        self.assertIn("espnradio/schedule", differences[0])
        self.assertIn("scoreboard/_/date/20260930", differences[0])
        self.assertEqual(counts["week_monday"], "2026-09-28")

    def test_future_game_on_a_day_with_no_1050_row_is_flagged_as_candidate(self) -> None:
        boards = self._boards("2026-09-30")
        status, differences, _i, _c = run_fixture(
            [], boards, "2026-09-28",
            {"WEDNESDAY": [("MLB", "Cubs @ Reds", "7:10 p.m.")]})
        self.assertEqual(status, "changed")
        self.assertIn("no 1050 row at all that day", differences[0])

    def test_matchup_already_in_a_grouped_mlb_postseason_row_is_covered(self) -> None:
        # The snapshot lists postseason dates as grouped rows; the grid naming a
        # real matchup inside one of those rows is already represented.
        rows = [{
            "id": "mlb-post-2026-09-29", "date": "2026-09-29", "stations": ["1050"],
            "title": "MLB Postseason on ESPN Radio — Wild Card Series, Game 1",
            "game_details": [{"description": "AL Wild Card 'B' Game 1",
                              "away": "Boston Red Sox", "home": "New York Yankees"}],
        }]
        boards = {"MLB|2026-09-29": board(("Boston Red Sox", "New York Yankees")),
                  "MLB|2026-09-22": EMPTY, "MLB|2026-10-07": EMPTY}
        status, differences, info, _c = run_fixture(
            rows, boards, "2026-09-28",
            {"TUESDAY": [("MLB", "Red Sox @ Yankees", "4:00 p.m.")]})
        self.assertEqual(status, "clear", differences)
        self.assertEqual(differences, [])
        self.assertTrue(any("already represented in the snapshot (`mlb-post-2026-09-29`)" in line
                           for line in info))

    def test_future_nba_game_already_in_the_snapshot_is_covered(self) -> None:
        rows = [{
            "id": "nba-espn-2026-11-06-philadelphia-at-cleveland", "date": "2026-11-06",
            "stations": ["1050"], "title": "NBA on ESPN Radio: Philadelphia at Cleveland",
        }]
        boards = {"NBA|2026-11-06": board(("Philadelphia 76ers", "Cleveland Cavaliers")),
                  "NBA|2026-10-30": EMPTY, "NBA|2026-11-13": EMPTY}
        status, differences, _i, _c = run_fixture(
            rows, boards, "2026-11-02",
            {"FRIDAY": [("NBA", "Philadelphia @ Cleveland", "7:30 p.m.")]})
        self.assertEqual(status, "clear", differences)
        self.assertEqual(differences, [])

    def test_future_game_outside_the_window_is_informational_only(self) -> None:
        boards = {"NBA|2027-03-03": board(("Boston Celtics", "Denver Nuggets")),
                  "NBA|2027-02-24": EMPTY, "NBA|2027-03-10": EMPTY}
        status, differences, info, _c = run_fixture(
            [], boards, "2027-03-01",
            {"WEDNESDAY": [("NBA", "Celtics @ Nuggets", "7:00 p.m.")]})
        self.assertEqual(status, "clear", differences)
        self.assertEqual(differences, [])
        self.assertTrue(any("outside the snapshot window" in line for line in info))

    def test_uncheckable_future_row_is_reported_without_being_trusted(self) -> None:
        # The week validates on Wednesday's Cubs @ Reds, which the snapshot
        # already lists. Friday's Astros @ Angels has no dated scoreboard this
        # run (a failed fetch), so it cannot be trusted from the grid alone
        # and the run cannot claim "clear" while a row went unchecked.
        boards = {"MLB|2026-09-30": board(("Chicago Cubs", "Cincinnati Reds"))}
        rows = [{"id": "mlb-post-2026-09-30", "date": "2026-09-30", "stations": ["1050"],
                 "title": "MLB: Cubs at Reds"}]
        status, differences, _i, counts = run_fixture(
            rows, boards, "2026-09-28",
            {"WEDNESDAY": [("MLB", "Cubs @ Reds", "7:10 p.m.")],
             "FRIDAY": [("MLB", "Astros @ Angels", "9:38 p.m.")]})
        self.assertEqual(status, "changed")
        self.assertEqual(counts["unchecked"], 1)
        self.assertTrue(any("Astros @ Angels" in line and "dated re-check did not complete" in line
                           for line in differences))
        self.assertFalse(any("Cubs @ Reds" in line for line in differences))


class ReportTests(unittest.TestCase):
    def test_report_labels_and_disclaimers(self) -> None:
        config = shipped_feed()["meta"]["espn_week_watch"]
        report = watch.make_report(
            "clear", "2026-09-27", [], ["- detail"],
            {"week_monday": "2026-09-21", "week_sunday": "2026-09-27"}, config, "2026-09-27")
        self.assertIn("ESPN Radio weekly grid", report)
        self.assertIn("Derived grid week: **2026-09-21 to 2026-09-27**", report)
        self.assertIn("never edits `data/broadcasts.json`", report)
        self.assertIn("not a Bay Area per-game clearance", report)

    def test_unavailable_report_never_reads_as_clear(self) -> None:
        config = shipped_feed()["meta"]["espn_week_watch"]
        report = watch.make_report("unavailable", "2026-09-27", ["- fetch failed"], [], {}, config,
                                   "2026-09-27")
        self.assertIn("could not be fetched, parsed, or dated", report)
        self.assertNotIn("already represented in this snapshot", report)

    def test_changed_report_demands_line_by_line_review(self) -> None:
        config = shipped_feed()["meta"]["espn_week_watch"]
        report = watch.make_report("changed", "2026-09-28", ["- the grid prints **MLB: A @ B on "
                                   "2026-09-30**"], [], {}, config, "2026-09-27")
        self.assertIn("needs review", report)
        self.assertIn("open the links", report.lower())


class ConfigTests(unittest.TestCase):
    def test_shipped_feed_carries_the_grid_watcher_config(self) -> None:
        feed = shipped_feed()
        cfg = feed["meta"]["espn_week_watch"]
        self.assertEqual(cfg["grid"], "https://www.espn.com/espnradio/schedule")
        self.assertEqual(cfg["today_zone"], "America/New_York")
        self.assertIn("CFB", cfg["sports"])
        self.assertEqual(cfg["sports"]["CFB"]["league_path"], "football/college-football")
        watch.load_config(feed)  # must not raise

    def test_the_grid_note_flag_ships_with_the_feed(self) -> None:
        flags = {f["id"]: f for f in shipped_feed()["flags"]}
        self.assertIn("ESPN_WEEK_GRID", flags)
        self.assertEqual(flags["ESPN_WEEK_GRID"]["url"], "https://www.espn.com/espnradio/schedule")


class CliTests(unittest.TestCase):
    def test_fixture_replay_exits_clear_with_report_and_output(self) -> None:
        report = tempfile.mktemp(suffix=".md")
        output = tempfile.mktemp(suffix=".out")
        argv = ["espn_radio_week_watch.py", "--input", str(FIXTURE), "--today", "2026-09-27",
                "--report", report, "--github-output", output]
        from unittest import mock
        with mock.patch.object(sys, "argv", argv):
            code = watch.main()
        self.assertEqual(code, 0)
        body = Path(report).read_text(encoding="utf-8")
        self.assertIn("Status: **clear**", body)
        self.assertIn("2026-09-21 to 2026-09-27", body)
        self.assertEqual(Path(output).read_text(encoding="utf-8").strip(), "espn_week_status=clear")
        Path(report).unlink()
        Path(output).unlink()

    def test_unparseable_grid_is_unavailable_and_exits_3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "fixture.json"
            source.write_text(json.dumps({"grid_html": "<html><body>nothing to see</body></html>",
                                          "scoreboards": {}}), encoding="utf-8")
            report = Path(tmp) / "report.md"
            output = Path(tmp) / "status.out"
            argv = ["espn_radio_week_watch.py", "--input", str(source), "--today", "2026-09-27",
                    "--report", str(report), "--github-output", str(output)]
            from unittest import mock
            with mock.patch.object(sys, "argv", argv):
                code = watch.main()
            self.assertEqual(code, 3)
            body = report.read_text(encoding="utf-8")
            self.assertIn("Status: **unavailable**", body)
            self.assertIn("not the weekly grid", body)
            self.assertNotIn("Status: **clear**", body)
            self.assertEqual(output.read_text(encoding="utf-8").strip(), "espn_week_status=unavailable")

    def test_bad_today_argument_is_a_failed_check_not_a_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "fixture.json"
            source.write_text(json.dumps({"grid_html": "<html></html>", "scoreboards": {}}),
                              encoding="utf-8")
            report = Path(tmp) / "report.md"
            argv = ["espn_radio_week_watch.py", "--input", str(source), "--today", "last tuesday",
                    "--report", str(report)]
            from unittest import mock
            with mock.patch.object(sys, "argv", argv):
                code = watch.main()
            self.assertEqual(code, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
