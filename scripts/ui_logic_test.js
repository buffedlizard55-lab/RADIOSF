#!/usr/bin/env node
"use strict";
var assert = require("assert");
var L = require("./logic.js");

assert.strictEqual(L.etToPt("19:30").hhmm, "16:30");
assert.strictEqual(L.etToPt("19:30").dayShift, 0);
assert.strictEqual(L.etToPt("09:15").hhmm, "06:15");
assert.strictEqual(L.etToPt("14:30").hhmm, "11:30");
assert.strictEqual(L.etToPt("02:00").hhmm, "23:00");
assert.strictEqual(L.etToPt("02:00").dayShift, -1);
assert.strictEqual(L.label12("13:05"), "1:05 PM PT");
assert.strictEqual(L.label12("00:05"), "12:05 AM PT");
assert.strictEqual(L.label12("12:00"), "12:00 PM PT");
assert.strictEqual(L.addDays("2026-09-26", 1), "2026-09-27");
assert.strictEqual(L.addDays("2026-11-01", -1), "2026-10-31");
assert.strictEqual(L.weekdayIndex("2026-09-26"), 6);
assert.strictEqual(L.formatLong("2026-09-26"), "Saturday, September 26, 2026");

var a = { id: "a", start_pt: "12:00", duration_est_min: 180, stations: ["680"] };
var b = { id: "b", start_pt: "13:05", duration_est_min: 165, stations: ["680", "104.5"] };
var c = { id: "c", start_pt: "19:30", duration_est_min: 120, stations: ["810"] };
var d = { id: "d", start_pt: null, duration_est_min: 204, stations: ["1050"] };
var e = { id: "e", start_pt: "16:00", duration_est_min: 204, stations: ["1050"] };
var conflicts = L.sameDayConflicts([a, b, c, d, e]);
assert.ok(conflicts.some(function (x) { return x.kind === "overlap" && x.ids.indexOf("a") !== -1 && x.ids.indexOf("b") !== -1; }));
assert.ok(!conflicts.some(function (x) { return x.ids.indexOf("c") !== -1 && x.ids.indexOf("a") !== -1; }));
assert.ok(conflicts.some(function (x) { return x.kind === "tbd" && x.ids.indexOf("d") !== -1; }));

var covered = L.unionMinutes([a, b, c], 10 * 60, 22 * 60);
assert.strictEqual(covered, 180 + (13 * 60 + 5 + 165 - 15 * 60) + 120);

var cells = L.monthCells(2026, 9);
assert.strictEqual(L.weekdayIndex("2026-09-01"), 2);
assert.strictEqual(cells[2], "2026-09-01");
assert.strictEqual(cells[6], "2026-09-05");
assert.strictEqual(cells.filter(Boolean).length, 30);

console.log("ui logic tests passed");
