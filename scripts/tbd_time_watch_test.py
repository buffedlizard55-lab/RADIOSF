#!/usr/bin/env python3
"""Offline tests for scripts/tbd_time_watch.py. No network access.

Two fixtures are used:

  * scripts/fixtures/cal_text_schedule_2026-09-27.md - the live response from
    calbears.com/sports/football/schedule/text as returned on 2026-09-27. The
    trailing cookie-consent paragraph is omitted because it carries no schedule
    data; every date, time cell, opponent and venue is exactly as printed.
  * scripts/fixtures/niners_schedule_2026-09-27.html - a structural stand-in for
    https://www.49ers.com/schedule/. The session fetch tool returns rendered
    markdown rather than raw HTML, so the fixture reproduces the page's visible
    text verbatim inside a minimal table. The after-anchor parser reads visible
    text only, so the tag structure carries no meaning here.
  * scripts/fixtures/stanford_schedule_2026-09-27.html - a structural stand-in
    for https://gostanford.com/sports/football/schedule, which opens with the
    completed 2025 results and then shows the 2026 ticker. Both seasons are
    reproduced deliberately, so the tests can prove the 2025 rows never read as
    a published 2026 kickoff.
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tbd_time_watch as watch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CAL_FIXTURE = (FIXTURES / "cal_text_schedule_2026-09-27.md").read_text(encoding="utf-8")
NINERS_FIXTURE = (FIXTURES / "niners_schedule_2026-09-27.html").read_text(encoding="utf-8")
STANFORD_FIXTURE = (FIXTURES / "stanford_schedule_2026-09-27.html").read_text(encoding="utf-8")
CONFIG = json.loads((ROOT / "data/tbd_watch.json").read_text(encoding="utf-8"))
DOCUMENTS = {
    "cal-football-kickoffs": CAL_FIXTURE,
    "niners-week-18-kickoff": NINERS_FIXTURE,
    "stanford-football-kickoffs": STANFORD_FIXTURE,
}
SHIPPED_DOCUMENTS = {k: v for k, v in DOCUMENTS.items()
                     if k in {t["id"] for t in CONFIG["targets"]}}
# The Stanford target is deliberately NOT in data/tbd_watch.json. The school's
# 2026 ticker is built in the browser, so a plain request receives a page without
# it - the source watch preview on pull request 12 found none of the page-watch
# strings and could not match a single anchor. It is kept here, exercised against
# a saved rendering, so the parser that would read it stays covered and so moving
# it into the shipped config is a one-line change if the school ever renders the
# schedule into the HTML it serves.
STANFORD_TARGET = {
    "id": "stanford-football-kickoffs",
    "label": "gostanford.com football schedule - four kickoffs still TBA",
    "url": "https://gostanford.com/sports/football/schedule",
    "kind": "after-anchor",
    "anchor": "Sat, Oct 31",
    "window": 220,
    "rows": "stanford-2026-10-31, stanford-2026-11-14, big-game-2026-11-21, stanford-2026-11-28",
    "entries": [
        {"anchor": "Sat, Oct 31", "row": "stanford-2026-10-31",
         "expect_in_segment": ["Louisville"],
         "why": "the school's 2026 ticker prints TBA for the Louisville game"},
        {"anchor": "Sat, Nov 14", "row": "stanford-2026-11-14",
         "expect_in_segment": ["Virginia Tech"],
         "why": "the school's 2026 ticker prints TBA for the Virginia Tech game"},
        {"anchor": "Sat, Nov 21", "row": "big-game-2026-11-21",
         "expect_in_segment": ["California"],
         "why": "the Big Game; the school's 2026 ticker prints TBA"},
        {"anchor": "Sat, Nov 28", "row": "stanford-2026-11-28",
         "expect_in_segment": ["SMU"],
         "why": "the school's 2026 ticker prints TBA for the SMU game"},
    ],
}
STANFORD_CONFIG = {"targets": [STANFORD_TARGET]}
CAL_TARGET = next(t for t in CONFIG["targets"] if t["id"] == "cal-football-kickoffs")
NINERS_TARGET = next(t for t in CONFIG["targets"] if t["id"] == "niners-week-18-kickoff")
WEEK18_ROW = (
    '<tr><td>WEEK 18</td><td>TBD</td><td>AT Arizona Cardinals</td><td>TBD</td>'
    '<td>KSAN 107.7 FM / KNBR 104.5 FM / 680 AM</td><td>State Farm Stadium</td></tr>')


def one_target(config: dict, target_id: str) -> dict:
    """The config with one target in it, so a single page can be exercised."""
    return {"targets": [t for t in config["targets"] if t["id"] == target_id]}


def one_entry(target: dict, row_id: str) -> dict:
    """The config with one target holding one entry.

    The anchor windows overlap on a real page, so a test about one row has to
    read one row: otherwise a time printed after the next game's anchor would
    show up as this row's kickoff.
    """
    entries = [entry for entry in target["entries"] if entry["row"] == row_id]
    assert len(entries) == 1, row_id
    return {"targets": [dict(target, entries=entries)]}


def cal_rows() -> list[str]:
    return [line for line in CAL_FIXTURE.splitlines() if line.strip().startswith("| ")]


def cal_with_time(date_cell: str, time_text: str) -> str:
    """Cal's text schedule with the Time cell of one row set to `time_text`."""
    out = []
    replaced = 0
    for line in CAL_FIXTURE.splitlines():
        if line.strip().startswith(f"| {date_cell} |"):
            cells = line.strip().strip("|").split("|")
            cells[1] = f" {time_text} "
            line = "|" + "|".join(cells) + "|"
            replaced += 1
        out.append(line)
    assert replaced == 1, f"expected one row for {date_cell!r}, found {replaced}"
    return "\n".join(out) + "\n"


def cal_with_row(date_cell: str, row_text: str) -> str:
    """Cal's text schedule with one whole row replaced by `row_text`."""
    out = []
    replaced = 0
    for line in CAL_FIXTURE.splitlines():
        if line.strip().startswith(f"| {date_cell} |"):
            line = row_text
            replaced += 1
        out.append(line)
    assert replaced == 1, f"expected one row for {date_cell!r}, found {replaced}"
    return "\n".join(out) + "\n"


def niners_week18_published() -> str:
    """The 49ers page with Week 18 dated and given a kickoff."""
    published = (WEEK18_ROW
                 .replace("<td>TBD</td><td>AT", "<td>Jan 3, 2027</td><td>AT", 1)
                 .replace("<td>TBD</td><td>KSAN", "<td>1:05 PM</td><td>KSAN", 1))
    assert published != WEEK18_ROW and published.count("1:05 PM") == 1
    return NINERS_FIXTURE.replace(WEEK18_ROW, published, 1)


def niners_without_week18() -> str:
    """The 49ers page with the Week 18 row gone."""
    assert NINERS_FIXTURE.count(WEEK18_ROW) == 1
    return NINERS_FIXTURE.replace(WEEK18_ROW + "\n", "", 1)


def with_duplicate_louisville_block(page: str, time_text: str) -> str:
    """The Stanford page with the Oct 31 game printed a second time, inside the
    2026 ticker, carrying `time_text`."""
    block = (
        '  <div class="game"><span class="date">Sat, Oct 31</span>'
        f'<span class="time">{time_text}</span>'
        '<span class="opp">Stanford</span><span class="opp">Louisville</span>'
        '<span class="loc">away</span></div>\n')
    marker = ('    <a href="https://tickets.gostanford.com/p/football">Tickets</a></div>\n'
              '</div>')
    assert page.count(marker) == 1, "the Stanford fixture's ticker changed shape"
    return page.replace(marker,
                        marker.replace('</div>\n', block + '</div>\n', 1), 1)


class TimePatternTest(unittest.TestCase):
    def test_recognises_printed_kickoffs(self) -> None:
        for printed in ("7:30 pm", "12:05 pm", "4:30 p.m.", "10:00 am", "1:05 p.m."):
            self.assertRegex(printed, watch.TIME_RE, printed)

    def test_rejects_frequencies_and_numbers(self) -> None:
        for not_a_time in ("680 am", "107.7 fm", "104.5 fm", "810 am", "w 27 - 7", "levi's stadium"):
            self.assertIsNone(watch.TIME_RE.search(not_a_time), not_a_time)


class CellListTest(unittest.TestCase):
    def test_html_cells_are_read_in_document_order(self) -> None:
        cells = watch.cell_list("<table><tr><td>Oct 17 (Sat)</td><td> </td><td>Home</td></tr></table>")
        self.assertEqual(cells, ["Oct 17 (Sat)", "", "Home"])

    def test_a_cell_keeps_the_case_the_page_prints(self) -> None:
        cells = watch.cell_list("<table><tr><td>Oct 17 (Sat)</td><td>7:00 PM</td><td>Home</td>"
                                "<td>Wake Forest</td></tr></table>")
        self.assertEqual(cells[1], "7:00 PM")

    def test_markdown_pipe_rows_are_read_as_cells(self) -> None:
        cells = watch.cell_list("| Oct 17 (Sat) |  | Home | Wake Forest |\n| --- | --- | --- | --- |")
        self.assertEqual(cells, ["Oct 17 (Sat)", "", "Home", "Wake Forest", "---", "---", "---", "---"])

    def test_both_shapes_agree_on_the_row_under_test(self) -> None:
        html_row = "<table><tr><td>Oct 17 (Sat)</td><td></td><td>Home</td><td>Wake Forest</td></tr></table>"
        markdown_row = "| Oct 17 (Sat) |  | Home | Wake Forest |"
        for document in (html_row, markdown_row):
            result = watch.check_table_row(
                {"row": "cal-2026-10-17", "date_cell": "Oct 17 (Sat)", "opponent": "Wake Forest"},
                watch.cell_list(document))
            self.assertEqual(result["state"], "tbd", document)


class LiveFixturesTest(unittest.TestCase):
    def test_the_real_cal_page_reports_every_row_still_tbd(self) -> None:
        status, changes, unreadable, details = watch.run(one_target(CONFIG, "cal-football-kickoffs"),
                                                         {"cal-football-kickoffs": CAL_FIXTURE})
        self.assertEqual(status, "clear")
        self.assertEqual((changes, unreadable), ([], []))
        self.assertEqual(len(details), 6)
        self.assertTrue(all("kickoff still TBD" in line for line in details))

    def test_the_real_niners_page_reports_week_18_still_tbd(self) -> None:
        status, changes, unreadable, details = watch.run(one_target(CONFIG, "niners-week-18-kickoff"),
                                                         {"niners-week-18-kickoff": NINERS_FIXTURE})
        self.assertEqual(status, "clear")
        self.assertEqual((changes, unreadable), ([], []))
        self.assertEqual(len(details), 1)
        self.assertIn("niners-week-18", details[0])

    def test_both_real_targets_are_clear_together(self) -> None:
        status, changes, unreadable, _ = watch.run(CONFIG, DOCUMENTS)
        self.assertEqual((status, changes, unreadable), ("clear", [], []))

    def test_every_configured_row_exists_in_the_feed(self) -> None:
        feed = json.loads((ROOT / "data" / "broadcasts.json").read_text(encoding="utf-8"))
        rows = {row["id"] for row in feed["broadcasts"]}
        for target in CONFIG["targets"]:
            for entry in target["entries"]:
                self.assertIn(entry["row"], rows, entry["row"])

    def test_every_cal_entry_matches_the_opponent_column_of_the_live_page(self) -> None:
        cells = [watch.normalise(cell) for cell in watch.cell_list(CAL_FIXTURE)]
        for entry in CAL_TARGET["entries"]:
            index = cells.index(watch.normalise(entry["date_cell"]))
            self.assertEqual(cells[index + int(entry.get("opponent_offset", 3))],
                             watch.normalise(entry["opponent"]), entry["row"])

    def test_a_row_whose_opponent_moved_column_is_unavailable(self) -> None:
        page = CAL_FIXTURE.replace(
            "| Oct 17 (Sat) |  | Home | Wake Forest |",
            "| Oct 17 (Sat) |  | Wake Forest | Home |", 1)
        status, _, _, _ = watch.run(one_target(CONFIG, "cal-football-kickoffs"),
                                    {"cal-football-kickoffs": page})
        self.assertEqual(status, "unavailable")

    def test_the_six_cal_rows_carry_no_start_time_in_the_feed(self) -> None:
        feed = {row["id"]: row for row in
                json.loads((ROOT / "data" / "broadcasts.json").read_text(encoding="utf-8"))["broadcasts"]}
        for entry in json.loads((ROOT / "data/tbd_watch.json").read_text())["targets"][0]["entries"]:
            self.assertIsNone(feed[entry["row"]].get("start_pt"), entry["row"])


class StanfordTargetTest(unittest.TestCase):
    """The school page opens with the 2025 results, so the matcher has to find the
    2026 ticker rows and nothing else."""

    def test_the_real_page_reports_all_four_rows_still_tba(self) -> None:
        status, changes, unreadable, details = watch.run(
            STANFORD_CONFIG,
            {"stanford-football-kickoffs": STANFORD_FIXTURE})
        self.assertEqual(status, "clear")
        self.assertEqual((changes, unreadable), ([], []))
        self.assertEqual(len(details), 4)
        self.assertTrue(all("still TBD" in line for line in details))

    def test_a_2025_row_never_reads_as_a_published_kickoff(self) -> None:
        # The 2025 list carries Oct 25, Nov 22 and Nov 29 with times nowhere; the
        # four watched anchors are Oct 31, Nov 14, Nov 21 and Nov 28.
        for anchor in ("Oct 31", "Nov 14", "Nov 21", "Nov 28"):
            self.assertNotIn(anchor, STANFORD_FIXTURE.split("2025 Results")[1], anchor)

    def test_a_published_louisville_kickoff_is_reported_as_changed(self) -> None:
        page = STANFORD_FIXTURE.replace(
            '<span class="date">Sat, Oct 31</span><span class="time">TBA</span>',
            '<span class="date">Sat, Oct 31</span><span class="time">7:30 PM PDT</span>', 1)
        status, changes, unreadable, details = watch.run(
            STANFORD_CONFIG,
            {"stanford-football-kickoffs": page})
        self.assertEqual(status, "changed")
        self.assertEqual((len(changes), unreadable), (1, []))
        self.assertIn("stanford-2026-10-31", changes[0])
        self.assertIn("7:30 PM", changes[0])

    def test_a_removed_ticker_row_is_unavailable(self) -> None:
        page = STANFORD_FIXTURE.replace('<span class="opp">SMU</span>', '<span class="opp">Oregon</span>', 1)
        status, changes, unreadable, _ = watch.run(
            STANFORD_CONFIG,
            {"stanford-football-kickoffs": page})
        self.assertEqual(status, "unavailable")
        self.assertEqual(changes, [])
        self.assertTrue(any("stanford-2026-11-28" in line for line in unreadable))

    def test_the_big_game_is_watched_from_cal_and_would_be_from_stanford_too(self) -> None:
        watched = {entry["row"] for target in CONFIG["targets"] for entry in target["entries"]}
        self.assertIn("big-game-2026-11-21", watched)
        both = [target["id"] for target in CONFIG["targets"] + STANFORD_CONFIG["targets"]
                for entry in target["entries"] if entry["row"] == "big-game-2026-11-21"]
        self.assertEqual(sorted(both), ["cal-football-kickoffs", "stanford-football-kickoffs"])

    def test_two_blocks_answering_the_same_anchor_is_unknown_not_published(self) -> None:
        # The school page opens with the 2025 results above the 2026 ticker, so a
        # page that ever prints the same date and opponent twice - two seasons,
        # or the same game in two blocks - must be reported as unknown rather
        # than have a time read off whichever block happens to carry one.
        page = with_duplicate_louisville_block(STANFORD_FIXTURE, "7:30 PM PDT")
        self.assertIn("Sat, Oct 31", page.split("<h2>2025 Results</h2>")[0])
        status, changes, unreadable, _ = watch.run(
            one_entry(STANFORD_TARGET, "stanford-2026-10-31"),
            {"stanford-football-kickoffs": page})
        self.assertEqual(status, "unavailable")
        self.assertEqual(changes, [])
        self.assertTrue(any("two seasons" in line for line in unreadable))

    def test_two_blocks_that_agree_on_a_kickoff_is_published(self) -> None:
        # Two blocks carrying the same date and opponent, both printing a time, is
        # not ambiguous: the kickoff is out, and both blocks say the same thing.
        page = STANFORD_FIXTURE.replace(
            '<span class="time">TBA</span>\n    <span class="opp">Stanford</span>'
            '<span class="opp">Louisville</span>',
            '<span class="time">7:30 PM PDT</span>\n    <span class="opp">Stanford</span>'
            '<span class="opp">Louisville</span>', 1)
        page = with_duplicate_louisville_block(page, "7:30 PM PDT")
        status, changes, unreadable, _ = watch.run(
            one_entry(STANFORD_TARGET, "stanford-2026-10-31"),
            {"stanford-football-kickoffs": page})
        self.assertEqual(status, "changed")
        self.assertEqual((len(changes), unreadable), (1, []))
        self.assertIn("7:30 PM", changes[0])

    def test_the_next_game_s_kickoff_is_not_read_as_this_one_s(self) -> None:
        # The Stanford window is 220 characters and the next game starts about
        # 56 characters in, so a kickoff published for Nov 14 must not be read
        # as Oct 31's.
        page = STANFORD_FIXTURE.replace(
            '<span class="time">TBA</span>\n    <span class="opp">Stanford</span>'
            '<span class="opp">Virginia Tech</span>',
            '<span class="time">7:00 PM PDT</span>\n    <span class="opp">Stanford</span>'
            '<span class="opp">Virginia Tech</span>', 1)
        status, changes, unreadable, _ = watch.run(
            one_entry(STANFORD_TARGET, "stanford-2026-10-31"),
            {"stanford-football-kickoffs": page})
        self.assertEqual((status, changes, unreadable), ("clear", [], []))
        self.assertEqual(
            watch.cut_at_next_game(" TBA Stanford Louisville away Fly SJC Sat, Nov 14 TBA"),
            " TBA Stanford Louisville away Fly SJC ")

    def test_the_held_out_target_is_clear_against_a_saved_rendering(self) -> None:
        status, changes, unreadable, _ = watch.run(STANFORD_CONFIG, DOCUMENTS)
        self.assertEqual((status, changes, unreadable), ("clear", [], []))

    def test_the_two_shipped_targets_are_clear_together(self) -> None:
        status, changes, unreadable, _ = watch.run(CONFIG, SHIPPED_DOCUMENTS)
        self.assertEqual((status, changes, unreadable), ("clear", [], []))

    def test_a_stray_casefold_length_character_does_not_blind_the_target(self) -> None:
        # U+0130 casefolds to two characters. A guard that casefolded the whole
        # page to find the anchor used to make every row unreadable.
        page = STANFORD_FIXTURE.replace("<h2>2025 Results</h2>",
                                        "<h2>2025 Results İ</h2>", 1)
        status, changes, unreadable, _ = watch.run(
            one_entry(STANFORD_TARGET, "stanford-2026-10-31"),
            {"stanford-football-kickoffs": page})
        self.assertEqual((status, changes, unreadable), ("clear", [], []))


class PublishedKickoffTest(unittest.TestCase):
    def test_a_new_cal_kickoff_is_reported_as_changed(self) -> None:
        status, changes, unreadable, details = watch.run(
            one_target(CONFIG, "cal-football-kickoffs"),
            {"cal-football-kickoffs": cal_with_time("Oct 17 (Sat)", "7:00 PM")})
        self.assertEqual(status, "changed")
        self.assertEqual((len(changes), unreadable), (1, []))
        self.assertIn("cal-2026-10-17", changes[0])
        self.assertIn("7:00 PM", changes[0])
        self.assertIn("build_feed.py", changes[0])
        self.assertTrue(any("now published" in line for line in details))

    def test_a_new_week_18_kickoff_is_reported_as_changed(self) -> None:
        status, changes, unreadable, _ = watch.run(
            one_target(CONFIG, "niners-week-18-kickoff"),
            {"niners-week-18-kickoff": niners_week18_published()})
        self.assertEqual(status, "changed")
        self.assertEqual((len(changes), unreadable), (1, []))
        self.assertIn("niners-week-18", changes[0])
        self.assertIn("1:05 PM", changes[0])

    def test_one_published_row_does_not_hide_the_others(self) -> None:
        status, changes, unreadable, details = watch.run(
            one_target(CONFIG, "cal-football-kickoffs"),
            {"cal-football-kickoffs": cal_with_time("Nov 28 (Sat)", "1:00 PM")})
        self.assertEqual(status, "changed")
        self.assertEqual((len(changes), unreadable), (1, []))
        self.assertEqual(sum("still TBD" in line for line in details), 5)


class FailClosedTest(unittest.TestCase):
    def test_a_missing_table_is_unavailable_never_clear(self) -> None:
        status, changes, unreadable, details = watch.run(
            one_target(CONFIG, "cal-football-kickoffs"),
            {"cal-football-kickoffs": "<html><body>no schedule here</body></html>"})
        self.assertEqual(status, "unavailable")
        self.assertEqual((changes, unreadable), ([], []))
        self.assertTrue(details)

    def test_a_missing_page_anchor_is_unavailable(self) -> None:
        page = CAL_FIXTURE.replace("## 2026 Football Schedule", "## Schedule")
        status, _, _, _ = watch.run(one_target(CONFIG, "cal-football-kickoffs"),
                                 {"cal-football-kickoffs": page})
        self.assertEqual(status, "unavailable")

    def test_a_changed_opponent_is_unavailable_not_clear(self) -> None:
        page = cal_with_row("Oct 17 (Sat)", "| Oct 17 (Sat) |  | Home | San Diego State |")
        status, _, _, _ = watch.run(one_target(CONFIG, "cal-football-kickoffs"),
                                 {"cal-football-kickoffs": page})
        self.assertEqual(status, "unavailable")

    def test_an_unreadable_time_cell_is_unavailable(self) -> None:
        status, _, unreadable, details = watch.run(
            one_target(CONFIG, "cal-football-kickoffs"),
            {"cal-football-kickoffs": cal_with_time("Oct 17 (Sat)", "Postponed")})
        self.assertEqual(status, "unavailable")
        self.assertTrue(any("Postponed" in line for line in unreadable), unreadable)

    def test_a_missing_week_18_row_is_unavailable(self) -> None:
        status, _, _, _ = watch.run(one_target(CONFIG, "niners-week-18-kickoff"),
                                 {"niners-week-18-kickoff": niners_without_week18()})
        self.assertEqual(status, "unavailable")

    def test_a_changed_week_18_opponent_is_unavailable(self) -> None:
        page = NINERS_FIXTURE.replace("AT Arizona Cardinals", "AT Seattle Seahawks")
        status, _, _, _ = watch.run(one_target(CONFIG, "niners-week-18-kickoff"),
                                 {"niners-week-18-kickoff": page})
        self.assertEqual(status, "unavailable")

    def test_a_missing_saved_copy_is_unavailable(self) -> None:
        status, _, _, _ = watch.run(CONFIG, {})
        self.assertEqual(status, "unavailable")

    def test_an_unknown_row_id_is_unavailable(self) -> None:
        config = copy.deepcopy(CONFIG)
        config["targets"] = [dict(CAL_TARGET, entries=[dict(CAL_TARGET["entries"][0], row="no-such-row")])]
        status, changes, unreadable, _ = watch.run(config, DOCUMENTS)
        self.assertEqual(status, "unavailable")
        self.assertEqual(changes, [])
        self.assertTrue(any("no-such-row" in line for line in unreadable))

    def test_a_stale_entry_is_reported_as_changed(self) -> None:
        config = copy.deepcopy(CONFIG)
        config["targets"] = [dict(CAL_TARGET, entries=[dict(CAL_TARGET["entries"][0], row="niners-2026-10-04")])]
        status, changes, _, _ = watch.run(config, DOCUMENTS)
        self.assertEqual(status, "changed")
        self.assertTrue(any("stale" in line for line in changes))

    def test_a_published_row_beats_an_unreadable_one(self) -> None:
        config = copy.deepcopy(CONFIG)
        entries = [CAL_TARGET["entries"][0],
                   dict(CAL_TARGET["entries"][1], date_cell="Oct 31 (Sat)", opponent="Virginia Tech")]
        config["targets"] = [dict(CAL_TARGET, entries=entries)]
        status, changes, unreadable, _ = watch.run(
            config, {"cal-football-kickoffs": cal_with_time("Oct 17 (Sat)", "7:00 PM")})
        self.assertEqual(status, "changed")
        self.assertEqual(len(changes), 1)
        self.assertTrue(any("could not be read" in line for line in unreadable))


class ConfigValidationTest(unittest.TestCase):
    def test_the_shipped_config_is_valid(self) -> None:
        self.assertEqual(len(watch.validate_config(CONFIG)), 2)

    def test_missing_target_keys_are_rejected(self) -> None:
        for key in ("id", "label", "url", "kind", "rows"):
            broken = copy.deepcopy(CONFIG)
            del broken["targets"][0][key]
            with self.assertRaises(watch.WatchError):
                watch.validate_config(broken)

    def test_a_non_https_url_is_rejected(self) -> None:
        broken = copy.deepcopy(CONFIG)
        broken["targets"][0]["url"] = "http://calbears.com/sports/football/schedule/text"
        with self.assertRaises(watch.WatchError):
            watch.validate_config(broken)

    def test_an_unknown_kind_is_rejected(self) -> None:
        broken = copy.deepcopy(CONFIG)
        broken["targets"][0]["kind"] = "telepathy"
        with self.assertRaises(watch.WatchError):
            watch.validate_config(broken)

    def test_duplicate_ids_are_rejected(self) -> None:
        broken = copy.deepcopy(CONFIG)
        broken["targets"][1]["id"] = broken["targets"][0]["id"]
        with self.assertRaises(watch.WatchError):
            watch.validate_config(broken)

    def test_the_shipped_config_watches_seven_entries_over_seven_rows(self) -> None:
        entries = [entry for target in CONFIG["targets"] for entry in target["entries"]]
        rows = {entry["row"] for entry in entries}
        self.assertEqual(len(CONFIG["targets"]), 2)
        self.assertEqual(len(entries), 7)
        self.assertEqual(len(rows), 7)

    def test_the_stanford_target_is_held_out_and_stays_valid(self) -> None:
        # Held out because the school page renders in the browser; if it ever
        # ships the schedule in the HTML, this is the target to move across.
        self.assertNotIn("stanford-football-kickoffs", {t["id"] for t in CONFIG["targets"]})
        self.assertEqual(len(watch.validate_config(STANFORD_CONFIG)), 1)

    def test_each_target_s_rows_string_matches_its_entries(self) -> None:
        # The report names the rows a page supports, so the list has to be the
        # list the entries actually watch.
        for target in CONFIG["targets"]:
            listed = [part.strip() for part in target["rows"].split(",")]
            watched = [entry["row"] for entry in target["entries"]]
            for row in watched:
                self.assertTrue(any(row in part for part in listed),
                                f"{target['id']}: {row} is not named in rows")

    def test_a_row_repeated_on_one_target_is_rejected(self) -> None:
        broken = copy.deepcopy(CONFIG)
        broken["targets"][0]["entries"].append(copy.deepcopy(broken["targets"][0]["entries"][0]))
        with self.assertRaises(watch.WatchError):
            watch.validate_config(broken)

    def test_the_same_row_on_two_pages_is_allowed(self) -> None:
        config = copy.deepcopy(CONFIG)
        config["targets"].append(copy.deepcopy(config["targets"][0]))
        config["targets"][-1]["id"] = "another-page"
        self.assertEqual(len(watch.validate_config(config)), 3)

    def test_an_entry_without_a_why_is_rejected(self) -> None:
        broken = copy.deepcopy(CONFIG)
        del broken["targets"][0]["entries"][0]["why"]
        with self.assertRaises(watch.WatchError):
            watch.validate_config(broken)

    def test_a_table_row_entry_without_an_opponent_is_rejected(self) -> None:
        broken = copy.deepcopy(CONFIG)
        del broken["targets"][0]["entries"][0]["opponent"]
        with self.assertRaises(watch.WatchError):
            watch.validate_config(broken)

    def test_an_empty_targets_list_is_rejected(self) -> None:
        with self.assertRaises(watch.WatchError):
            watch.validate_config({"targets": []})


class ReportTest(unittest.TestCase):
    def test_the_clear_report_says_still_tbd_and_never_unchanged(self) -> None:
        status, changes, unreadable, details = watch.run(CONFIG, DOCUMENTS)
        report = watch.make_report(status, details, changes, unreadable, CONFIG["checked"])
        self.assertIn("Status: **clear**", report)
        self.assertIn("still prints no kickoff", report)
        self.assertIn("2026-09-27", report)
        self.assertNotIn("unchanged", report)

    def test_the_changed_report_names_the_row_and_the_action(self) -> None:
        status, changes, unreadable, details = watch.run(
            one_target(CONFIG, "cal-football-kickoffs"),
            {"cal-football-kickoffs": cal_with_time("Oct 17 (Sat)", "4:00 PM")})
        report = watch.make_report(status, details, changes, unreadable, CONFIG["checked"])
        self.assertIn("Status: **changed**", report)
        self.assertIn("cal-2026-10-17", report)
        self.assertIn("4:00 PM", report)
        self.assertIn("does not", report)
        self.assertIn("publish GitHub Pages", report)

    def test_a_changed_report_also_lists_the_rows_it_could_not_read(self) -> None:
        config = copy.deepcopy(CONFIG)
        entries = [CAL_TARGET["entries"][0],
                   dict(CAL_TARGET["entries"][1], date_cell="Oct 31 (Sat)", opponent="Virginia Tech")]
        config["targets"] = [dict(CAL_TARGET, entries=entries)]
        status, changes, unreadable, details = watch.run(
            config, {"cal-football-kickoffs": cal_with_time("Oct 17 (Sat)", "7:00 PM")})
        report = watch.make_report(status, details, changes, unreadable, CONFIG["checked"])
        self.assertIn("A watched row changed", report)
        self.assertIn("could not be read", report)

    def test_the_unavailable_report_never_claims_no_change(self) -> None:
        status, changes, unreadable, details = watch.run(CONFIG, {})
        report = watch.make_report(status, details, changes, unreadable, CONFIG["checked"])
        self.assertIn("Status: **unavailable**", report)
        self.assertIn("not evidence that it changed", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
