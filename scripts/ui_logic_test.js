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
assert.strictEqual(summary.daysWithGames, 1);
assert.strictEqual(summary.daysEmpty, 2);
assert.strictEqual(summary.busiest.date, "2026-10-01");
assert.strictEqual(summary.days[0].tbd, 1, "a kickoff-TBD row is counted, not silently dropped");
assert.strictEqual(summary.days[1].covered, 0);
assert.ok(summary.daysMajority <= summary.dayCount);

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
assert.ok(Array.isArray(feed.broadcasts) && feed.broadcasts.length > 0, "feed has broadcasts");
assert.ok(Array.isArray(feed.flags) && feed.flags.length > 0, "feed has flags");
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
  (row.flag_ids || []).forEach(function (id) {
    assert.ok(flagIds.indexOf(id) !== -1, row.id + " points at unknown flag " + id);
  });
  if (row.date) {
    assert.ok(/^\d{4}-\d{2}-\d{2}$/.test(row.date), row.id + " date format");
    assert.ok(L.inWindow(row.date, feed.meta.window_start, feed.meta.window_end), row.id + " outside the window");
  } else {
    assert.strictEqual(row.start_pt, null, row.id + " cannot have a time without a date");
  }
  if (row.start_pt) assert.ok(/^\d{2}:\d{2}$/.test(row.start_pt), row.id + " time format");
  assert.ok(row.duration_est_min > 0, row.id + " duration estimate");
});
assert.strictEqual(feed.meta.counts.broadcasts, feed.broadcasts.length);
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
assert.ok(real.daysMajority < real.dayCount / 2,
  "if most days ever do fill 10-10, update the README finding instead of this assertion");

console.log("ui logic tests passed — " + feed.broadcasts.length + " broadcasts, " +
  feed.flags.length + " flags, " + real.daysWithGames + "/" + real.dayCount +
  " days carry a verified game, " + real.daysMajority + " fill more than half of 10 AM–10 PM");
