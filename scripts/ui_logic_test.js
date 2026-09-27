#!/usr/bin/env node
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var L = require("./logic.js");

/* ---- clock and calendar ---- */
assert.strictEqual(L.etToPt("19:30").hhmm, "16:30");
assert.strictEqual(L.etToPt("19:30").dayShift, 0);
assert.strictEqual(L.etToPt("09:15").hhmm, "06:15");
assert.strictEqual(L.etToPt("14:30").hhmm, "11:30");
assert.strictEqual(L.etToPt("22:00").hhmm, "19:00");
assert.strictEqual(L.etToPt("02:00").hhmm, "23:00");
assert.strictEqual(L.etToPt("02:00").dayShift, -1);
assert.strictEqual(L.label12("13:05"), "1:05 PM PT");
assert.strictEqual(L.label12("00:05"), "12:05 AM PT");
assert.strictEqual(L.label12("12:00"), "12:00 PM PT");
assert.strictEqual(L.label12(null), "Time TBD");
assert.strictEqual(L.addDays("2026-09-26", 1), "2026-09-27");
assert.strictEqual(L.addDays("2026-11-01", -1), "2026-10-31");
assert.strictEqual(L.addDays("2026-12-31", 1), "2027-01-01");
assert.strictEqual(L.weekdayIndex("2026-09-26"), 6);
assert.strictEqual(L.weekdayIndex("2026-09-27"), 0);
assert.strictEqual(L.formatLong("2026-09-26"), "Saturday, September 26, 2026");
assert.strictEqual(L.formatDuration(204), "3h 24m");
assert.strictEqual(L.formatDuration(120), "2h");
assert.strictEqual(L.formatDuration(45), "45m");
assert.strictEqual(L.isISODate("2024-02-29"), true, "valid leap day");
assert.strictEqual(L.isISODate("2026-02-29"), false, "invalid leap day");
assert.strictEqual(L.isISODate("2026-13-01"), false, "invalid month");
assert.strictEqual(L.isISODate("2026-10-1"), false, "date must be zero-padded ISO");

var noon = { iso: "2026-10-02", minutes: 12 * 60 };
assert.strictEqual(L.airState({ date: null }, noon), "unplaced");
assert.strictEqual(L.airState({ date: "2026-10-01", start_pt: "12:00", status: "scheduled" }, noon),
  "past-unchecked", "a passed schedule date is not proof that a game aired");
assert.strictEqual(L.airState({ date: "2026-10-01", start_pt: null, status: "tba" }, noon),
  "past-unchecked", "a past TBD event is not silently called aired");
assert.strictEqual(L.airState({ date: "2026-10-01", status: "if-necessary", conditional: true }, noon),
  "conditional", "an if-necessary window remains a possibility, even after its date");
assert.strictEqual(L.airState({ date: "2026-10-01", start_pt: "12:00", status: "final" }, noon), "final",
  "a final game result does not imply radio carriage");
assert.strictEqual(L.airState({ date: "2026-10-02", start_pt: "11:00", duration_est_min: 60, status: "scheduled" },
  { iso: "2026-10-02", minutes: 11 * 60 + 30 }), "on");
assert.strictEqual(L.airState({ date: "2026-10-02", start_pt: "11:00", duration_est_min: 60, status: "scheduled" },
  { iso: "2026-10-02", minutes: 13 * 60 }), "elapsed-unchecked",
  "an elapsed estimate is not proof the broadcast ended");

/* ---- conflicts ---- */
var a = { id: "a", date: "2026-10-01", start_pt: "12:00", duration_est_min: 180, stations: ["680"] };
var b = { id: "b", date: "2026-10-01", start_pt: "13:05", duration_est_min: 165, stations: ["680", "104.5"] };
var c = { id: "c", date: "2026-10-01", start_pt: "19:30", duration_est_min: 120, stations: ["810"] };
var d = { id: "d", date: "2026-10-01", start_pt: null, duration_est_min: 204, stations: ["1050"] };
var e = { id: "e", date: "2026-10-01", start_pt: "16:00", duration_est_min: 204, stations: ["1050"] };
var conflicts = L.sameDayConflicts([a, b, c, d, e]);
assert.ok(conflicts.some(function (x) { return x.kind === "overlap" && x.ids.indexOf("a") !== -1 && x.ids.indexOf("b") !== -1; }));
assert.ok(!conflicts.some(function (x) { return x.ids.indexOf("c") !== -1 && x.ids.indexOf("a") !== -1; }));
assert.ok(conflicts.some(function (x) { return x.kind === "tbd" && x.ids.indexOf("d") !== -1; }));
var conditionalConflict = { id: "conditional", date: "2026-10-01", start_pt: "12:30",
  duration_est_min: 180, stations: ["680"], conditional: true, status: "if-necessary" };
assert.deepStrictEqual(L.sameDayConflicts([a, b, conditionalConflict]).map(function (x) { return x.ids; }),
  [["a", "b"]], "conditional possibilities do not create false overlap warnings");
assert.deepStrictEqual(L.sameDayConflicts([conditionalConflict]), [],
  "conditional-only windows do not create false TBD warnings");
var mixedPossibility = { id: "mixed", date: "2026-10-01", start_pt: "12:30", duration_est_min: 180,
  stations: ["680"], status: "tba", game_count: 4, conditional_game_count: 2 };
assert.strictEqual(L.isConditional(mixedPossibility), false, "a mixed date row still has non-conditional games");
assert.strictEqual(L.hasConditionalPossibility(mixedPossibility), true);
assert.strictEqual(L.conditionalGameCount(mixedPossibility), 2);
assert.strictEqual(L.airState(mixedPossibility, noon), "mixed",
  "a grouped row with conditional games must not look like a single game is on air");
assert.ok(!L.sameDayConflicts([a, mixedPossibility]).some(function (x) { return x.ids.indexOf("mixed") !== -1; }),
  "a grouped row containing conditional games does not produce a false clash");
assert.strictEqual(L.unionMinutes([mixedPossibility], 10 * 60, 22 * 60), 0,
  "a grouped mixed row is conservatively omitted from duration estimates");

/* TBD warnings collapse to one per station instead of one per pair, or a day with
   three undated listings on 1050 buries the real overlaps under six duplicates. */
var f = { id: "f", date: "2026-10-01", start_pt: null, duration_est_min: 204, stations: ["1050"] };
var g = { id: "g", date: "2026-10-01", start_pt: null, duration_est_min: 204, stations: ["1050"] };
var grouped = L.sameDayConflicts([d, e, f, g]).filter(function (x) { return x.kind === "tbd"; });
assert.strictEqual(grouped.length, 1, "one TBD warning per station, not one per pair");
assert.strictEqual(grouped[0].station, "1050");
assert.deepStrictEqual(grouped[0].ids.slice().sort(), ["d", "e", "f", "g"]);
assert.ok(grouped[0].text.indexOf("4 listings") === 0, "the warning counts the listings");

/* two stations shared by the same undated pair get one warning each */
var h = { id: "h", date: "2026-10-01", start_pt: null, duration_est_min: 180, stations: ["680", "104.5"] };
var i2 = { id: "i", date: "2026-10-01", start_pt: "12:00", duration_est_min: 180, stations: ["680", "104.5"] };
var twoStations = L.sameDayConflicts([h, i2]).filter(function (x) { return x.kind === "tbd"; });
assert.strictEqual(twoStations.length, 2);
assert.deepStrictEqual(twoStations.map(function (x) { return x.station; }), ["680", "104.5"]);

/* overlap warnings name the games, so the reader can pick */
var titled = L.sameDayConflicts([
  { id: "p", date: "2026-10-01", title: "Game One", start_pt: "12:00", duration_est_min: 180, stations: ["680"] },
  { id: "q", date: "2026-10-01", title: "Game Two", start_pt: "13:00", duration_est_min: 180, stations: ["680"] }
]);
assert.strictEqual(titled.length, 1);
assert.ok(titled[0].text.indexOf("Game One") !== -1 && titled[0].text.indexOf("Game Two") !== -1,
  "overlap text names both games");

/* ---- band maths ---- */
var covered = L.unionMinutes([a, b, c], 10 * 60, 22 * 60);
assert.strictEqual(covered, 180 + (13 * 60 + 5 + 165 - 15 * 60) + 120);
assert.strictEqual(L.stationMinutes([a, b, c], "810", 10 * 60, 22 * 60), 120);
assert.strictEqual(L.stationMinutes([a, b, c], "960", 10 * 60, 22 * 60), 0);

assert.deepStrictEqual(L.eachDate("2026-10-01", "2026-10-03"), ["2026-10-01", "2026-10-02", "2026-10-03"]);
assert.strictEqual(L.eachDate("2026-10-01", "2026-09-30").length, 0);

var summary = L.bandSummary([a, b, c, d, e], "2026-10-01", "2026-10-03", 10 * 60, 22 * 60);
assert.strictEqual(summary.dayCount, 3);
assert.strictEqual(summary.daysWithListings, 1);
assert.strictEqual(summary.daysEmpty, 2);
assert.strictEqual(summary.busiest.date, "2026-10-01");
assert.strictEqual(summary.days[0].tbd, 1, "a kickoff-TBD row is counted, not silently dropped");
assert.strictEqual(summary.days[1].covered, 0);
assert.ok(summary.daysMajority <= summary.dayCount);

var conditionalSummary = L.bandSummary([
  { id: "possible", date: "2026-10-02", start_pt: "12:00", duration_est_min: 240,
    stations: ["1050"], conditional: true, status: "if-necessary", game_count: 2, conditional_game_count: 2 }
], "2026-10-01", "2026-10-03", 10 * 60, 22 * 60);
assert.strictEqual(conditionalSummary.daysWithListings, 0, "conditional dates are not schedule days");
assert.strictEqual(conditionalSummary.daysWithPossibilities, 1);
assert.strictEqual(conditionalSummary.conditionalGames, 2);
assert.strictEqual(conditionalSummary.daysConditionalOnly, 1);
assert.strictEqual(conditionalSummary.daysEmpty, 2);
assert.strictEqual(conditionalSummary.meanCovered, 0, "conditional placeholders add no estimated broadcast minutes");
assert.strictEqual(conditionalSummary.days[1].rows, 0);
assert.strictEqual(conditionalSummary.days[1].possibilities, 1);
assert.strictEqual(L.unionMinutes([conditionalConflict], 10 * 60, 22 * 60), 0);
var mixedSummary = L.bandSummary([mixedPossibility], "2026-10-01", "2026-10-03", 10 * 60, 22 * 60);
assert.strictEqual(mixedSummary.daysWithListings, 1, "a mixed group includes non-conditional games");
assert.strictEqual(mixedSummary.daysWithPossibilities, 1, "mixed groups still expose conditional possibilities");
assert.strictEqual(mixedSummary.daysConditionalOnly, 0);
assert.strictEqual(mixedSummary.conditionalGames, 2);

/* ---- calendar grid ---- */
var cells = L.monthCells(2026, 9);
assert.strictEqual(L.weekdayIndex("2026-09-01"), 2);
assert.strictEqual(cells[2], "2026-09-01");
assert.strictEqual(cells[6], "2026-09-05");
assert.strictEqual(cells.filter(Boolean).length, 30);
assert.strictEqual(L.monthCells(2027, 2).filter(Boolean).length, 28);

/* ---- the shipped feed has to satisfy the same invariants the page assumes ---- */
var feed = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "data", "broadcasts.json"), "utf8"));
var ALLOWED = ["680", "810", "960", "1050", "104.5", "107.7"];
assert.ok(Array.isArray(feed.broadcasts) && feed.broadcasts.length > 0, "feed has schedule entries");
assert.ok(Array.isArray(feed.flags) && feed.flags.length > 0, "feed has flags");
assert.ok(L.isISODate(feed.meta.snapshot_date), "snapshot date is a real ISO date");
assert.ok(L.isISODate(feed.meta.window_start), "window start is a real ISO date");
assert.ok(L.isISODate(feed.meta.window_end), "window end is a real ISO date");
var flagIds = feed.flags.map(function (f) { return f.id; });
var seen = {};
feed.broadcasts.forEach(function (row) {
  assert.ok(!seen[row.id], "duplicate id " + row.id);
  seen[row.id] = true;
  assert.ok(row.stations.length > 0, row.id + " has a station");
  row.stations.forEach(function (s) {
    assert.ok(ALLOWED.indexOf(s) !== -1, row.id + " uses an off-dial station " + s);
    assert.ok(feed.meta.stations.some(function (m) { return m.id === s; }), row.id + " station missing from meta");
  });
  assert.ok(row.sources.length > 0, row.id + " has a source");
  row.sources.forEach(function (s) {
    assert.ok(/^https:\/\//.test(s.url), row.id + " source must be an https link");
    assert.ok(s.label && s.label.length > 3, row.id + " source needs a readable label");
  });
  assert.ok(["official", "indicated", "review"].indexOf(row.confidence) !== -1, row.id + " confidence");
  assert.ok(["scheduled", "tba", "final", "pregame", "if-necessary"].indexOf(row.status) !== -1, row.id + " status");
  if (row.game_count != null) {
    assert.ok(Number.isInteger(row.game_count) && row.game_count > 0, row.id + " game_count is a positive integer");
  }
  if (row.conditional_game_count != null) {
    assert.ok(Number.isInteger(row.conditional_game_count) && row.conditional_game_count >= 0,
      row.id + " conditional_game_count is a nonnegative integer");
    assert.ok(row.game_count != null && row.conditional_game_count <= row.game_count,
      row.id + " conditional count needs a total and cannot exceed it");
  }
  if (row.status === "if-necessary") {
    assert.ok(L.isConditional(row), row.id + " must identify conditional postseason listings");
    assert.strictEqual(row.conditional_game_count, row.game_count,
      row.id + " wholly conditional row must count all its games as conditional");
  }
  if (!row.id.startsWith("mlb-post-")) {
    assert.ok(!Object.prototype.hasOwnProperty.call(row, "game_count"),
      row.id + " must not carry an irrelevant grouped-game total");
    assert.ok(!Object.prototype.hasOwnProperty.call(row, "conditional_game_count"),
      row.id + " must not carry an irrelevant conditional-game count");
  }
  (row.flag_ids || []).forEach(function (id) {
    assert.ok(flagIds.indexOf(id) !== -1, row.id + " points at unknown flag " + id);
  });
  if (row.date) {
    assert.ok(L.isISODate(row.date), row.id + " must have a real ISO calendar date");
    assert.ok(L.inWindow(row.date, feed.meta.window_start, feed.meta.window_end), row.id + " outside the window");
  } else {
    assert.strictEqual(row.start_pt, null, row.id + " cannot have a time without a date");
  }
  if (row.start_pt) assert.ok(/^\d{2}:\d{2}$/.test(row.start_pt), row.id + " time format");
  assert.ok(row.duration_est_min > 0, row.id + " duration estimate");
});
/* Flags are the honesty mechanism, so their links have to work as hard as a row's.
   Every flag must be reachable, and a flag that cites several checks must link them all. */
var flagSeen = {};
feed.flags.forEach(function (f) {
  assert.ok(!flagSeen[f.id], "duplicate flag id " + f.id);
  flagSeen[f.id] = true;
  assert.ok(["limitation", "review", "note"].indexOf(f.severity) !== -1, f.id + " severity");
  assert.ok(f.title && f.title.length > 8, f.id + " needs a readable title");
  assert.ok(f.detail && f.detail.length > 40, f.id + " needs a detail a reader can act on");
  assert.ok(/^https:\/\//.test(f.url), f.id + " url must be https");
  (f.sources || []).forEach(function (x) {
    assert.ok(/^https:\/\//.test(x.url), f.id + " extra link must be https");
    assert.ok(x.label && x.label.length > 3, f.id + " extra link needs a label");
  });
  if (f.sources && f.sources.length) {
    assert.strictEqual(f.sources[0].url, f.url, f.id + " primary url must lead its sources");
  }
});

/* every duration bucket in the feed must be one the page can render a control for */
var bucketIds = (feed.meta.durations || []).map(function (d) { return d.id; });
assert.ok(bucketIds.length > 0, "meta.durations drives the duration controls");
feed.broadcasts.forEach(function (row) {
  assert.ok(bucketIds.indexOf(row.duration_key) !== -1, row.id + " has no duration bucket");
  var d = feed.meta.durations.find(function (x) { return x.id === row.duration_key; });
  assert.strictEqual(row.duration_est_min, d.minutes,
    row.id + " duration must equal its bucket default, or resetting the control would not restore it");
});

assert.strictEqual(feed.meta.counts.broadcasts, feed.broadcasts.length);
assert.strictEqual(feed.meta.counts.conditional,
  feed.broadcasts.filter(function (row) { return L.isConditional(row); }).length);
assert.strictEqual(feed.meta.counts.conditional, 11, "fully conditional date-level rows");
assert.strictEqual(feed.meta.counts.conditional_games, 21, "if-necessary postseason games across fully and partially conditional rows");
assert.strictEqual(feed.meta.counts.conditional_games,
  feed.broadcasts.reduce(function (sum, row) { return sum + (row.conditional_game_count || 0); }, 0),
  "metadata conditional-game count matches the rows");
assert.strictEqual(
  feed.meta.counts.official + feed.meta.counts.indicated + feed.meta.counts.review,
  feed.broadcasts.length
);
assert.strictEqual(feed.meta.counts.flags, feed.flags.length);

/* the page renders the feed in stored order, so it must already be sorted */
var prev = "";
feed.broadcasts.forEach(function (row) {
  var key = (row.date || "9999-99-99") + " " + (row.start_pt || "99:99") + " " + row.id;
  assert.ok(key >= prev, "feed is not sorted at " + row.id);
  prev = key;
});

/* the band claim in the README must match what the data actually says */
var real = L.bandSummary(feed.broadcasts, feed.meta.window_start, feed.meta.window_end, 10 * 60, 22 * 60);
assert.strictEqual(real.daysWithListings, 74, "non-conditional listing-day count");
assert.strictEqual(real.daysWithPossibilities, 13, "conditional possibility-day count, including mixed postseason rows");
assert.strictEqual(real.conditionalGames, 21, "conditional game count");
assert.strictEqual(real.daysConditionalOnly, 3, "conditional-only date count");
assert.strictEqual(real.daysMajority, 18, "non-conditional estimated-window majority count");
assert.strictEqual(L.formatDuration(real.meanCovered), "1h 47m");
assert.strictEqual(L.formatDuration(real.meanCoveredOnListingDays), "3h 45m");
assert.deepStrictEqual(real.byWeekday.map(function (day) {
  return day.days ? L.formatDuration(Math.round(day.covered / day.days)) : "0m";
}), ["3h 40m", "2h 13m", "16m", "20m", "2h 20m", "41m", "2h 56m"],
  "weekday coverage in the README matches the snapshot");

function scenario(durationFor) {
  var rows = feed.broadcasts.map(function (row) {
    var copy = {};
    Object.keys(row).forEach(function (key) { copy[key] = row[key]; });
    copy.duration_est_min = durationFor(row);
    return copy;
  });
  return L.bandSummary(rows, feed.meta.window_start, feed.meta.window_end, 10 * 60, 22 * 60);
}
var sensitivity = [
  scenario(function () { return 90; }),
  scenario(function (row) { return row.duration_est_min - 30; }),
  real,
  scenario(function (row) { return row.duration_est_min + 60; }),
  scenario(function () { return 240; })
];
assert.deepStrictEqual(sensitivity.map(function (s) {
  return [s.daysWithListings, s.daysMajority, L.formatDuration(s.meanCovered), L.formatDuration(s.meanCoveredOnListingDays)];
}), [
  [74, 0, "52m", "1h 49m"],
  [74, 5, "1h 31m", "3h 10m"],
  [74, 18, "1h 47m", "3h 45m"],
  [74, 18, "2h 17m", "4h 47m"],
  [74, 18, "2h 13m", "4h 39m"]
], "README sensitivity figures match the logic");
assert.ok(real.daysMajority < real.dayCount / 2,
  "if most days ever do fill 10-10, update the README finding instead of this assertion");

console.log("ui logic tests passed — " + feed.broadcasts.length + " schedule listings, " +
  feed.flags.length + " flags, " + real.daysWithListings + "/" + real.dayCount +
  " days have non-conditional listings, " + real.daysWithPossibilities +
  " have conditional possibilities (" + real.daysConditionalOnly + " conditional-only), and " +
  real.daysMajority + " fill more than half of 10 AM–10 PM");
