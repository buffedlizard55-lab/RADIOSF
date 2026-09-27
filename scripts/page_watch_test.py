#!/usr/bin/env python3
"""Offline tests for scripts/page_watch.py. No network access."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import page_watch  # noqa: E402

PAD = "<p>" + "filler " * 60 + "</p>"


def page_with_all_expected(page: dict) -> str:
    """Synthetic HTML carrying every expected string, split across tags the way real pages are."""
    parts = []
    for item in page["expect"]:
        words = item["text"].split(" ")
        # Split each phrase over two elements to prove tag stripping works.
        half = max(1, len(words) // 2)
        parts.append(f"<span>{' '.join(words[:half])}</span>\n <b>{' '.join(words[half:])}</b>")
    return "<html><body>" + PAD + "<div>" + "</div><div>".join(parts) + "</div></body></html>"


class PageWatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(page_watch.CONFIG_PATH.read_text(encoding="utf-8"))

    def documents(self):
        return {page["id"]: page_with_all_expected(page) for page in self.config["pages"]}

    def test_config_is_valid(self):
        pages = page_watch.validate_config(self.config)
        self.assertGreaterEqual(len(pages), 7)
        for page in pages:
            self.assertTrue(page["url"].startswith("https://"))

    def test_unchanged_pages_are_clear(self):
        status, differences, _ = page_watch.run(self.config, self.documents())
        self.assertEqual((status, differences), ("clear", []))

    def test_missing_expected_text_is_changed(self):
        docs = self.documents()
        docs["49ers-schedule"] = "<html>" + PAD + "KSFO 810 AM / KSAN 107.7 FM</html>"
        status, differences, _ = page_watch.run(self.config, docs)
        self.assertEqual(status, "changed")
        self.assertTrue(any("KNBR 104.5 FM / 680 AM" in line for line in differences))

    def test_alert_string_appearing_is_changed(self):
        docs = self.documents()
        docs["usf-mbb-schedule"] += "<td>Radio: KNBR 1050</td>"
        status, differences, _ = page_watch.run(self.config, docs)
        self.assertEqual(status, "changed")
        self.assertTrue(any("KNBR" in line and "now appears" in line for line in differences))

    def test_entities_typography_and_case_are_folded(self):
        page = {"id": "x", "label": "x", "url": "https://example.com", "rows": "r",
                "expect": [{"text": "Levi's Stadium", "why": "w"}]}
        self.assertEqual(page_watch.check_page(page, PAD + "LEVI&#8217;S&reg;   Stadium"), [])

    def test_fetch_failure_is_unavailable_not_clear(self):
        docs = self.documents()
        del docs["cal-football-schedule"]
        status, differences, details = page_watch.run(self.config, docs)
        self.assertEqual((status, differences), ("unavailable", []))
        self.assertTrue(any("not checked" in line for line in details))

    def test_empty_body_is_unavailable(self):
        docs = self.documents()
        docs["knbr1050-grid"] = "<html></html>"
        status, _, _ = page_watch.run(self.config, docs)
        self.assertEqual(status, "unavailable")

    def test_change_outranks_unavailable(self):
        docs = self.documents()
        del docs["cal-football-schedule"]
        docs["knbr1050-grid"] = "<html>" + PAD + "MONDAY 9-28</html>"
        status, _, _ = page_watch.run(self.config, docs)
        self.assertEqual(status, "changed")

    def test_entry_without_expect_is_rejected(self):
        config = copy.deepcopy(self.config)
        config["pages"][0]["expect"] = []
        with self.assertRaises(page_watch.PageError):
            page_watch.validate_config(config)

    def test_non_https_entry_is_rejected(self):
        config = copy.deepcopy(self.config)
        config["pages"][0]["url"] = "http://www.49ers.com/schedule/"
        with self.assertRaises(page_watch.PageError):
            page_watch.validate_config(config)

    def test_report_never_claims_to_edit_the_feed(self):
        report = page_watch.make_report("clear", ["- a"], [], "2026-09-27")
        self.assertIn("does not parse schedules", report)


if __name__ == "__main__":
    unittest.main(verbosity=1)
