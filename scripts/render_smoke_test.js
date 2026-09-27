#!/usr/bin/env node
/*
 * Runs the real inline script out of index.html against the real data/broadcasts.json
 * in a tiny DOM shim. It catches the failures a static check cannot: a getElementById
 * for an id that is not in the markup, a renderer that throws on a row shape, a filter
 * handler that breaks, a day with no broadcasts, the first and last day of the window.
 */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var root = path.join(__dirname, "..");
var html = fs.readFileSync(path.join(root, "index.html"), "utf8");
var logicSrc = fs.readFileSync(path.join(root, "scripts", "logic.js"), "utf8");
var feed = JSON.parse(fs.readFileSync(path.join(root, "data", "broadcasts.json"), "utf8"));
/* Give one mixed aggregate row a synthetic time in this in-memory fixture only.
   The UI must still omit it from estimates, conflicts, and the timeline. */
var mixedTestRow = feed.broadcasts.find(function (row) {
  return row.game_count > 0 && row.conditional_game_count > 0 &&
    row.conditional_game_count < row.game_count;
});
assert.ok(mixedTestRow, "feed has a mixed postseason group to exercise");
mixedTestRow.start_pt = "12:00";

var inlineMatch = html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(inlineMatch, "index.html must carry the inline page script");
var inline = inlineMatch[1];

/* every id that actually exists in the markup */
var markupIds = {};
var idRe = /\sid="([^"]+)"/g;
var m;
while ((m = idRe.exec(html))) markupIds[m[1]] = true;

var listeners = {};
function makeEl(id) {
  return {
    id: id,
    innerHTML: "",
    textContent: "",
    className: "",
    value: "",
    disabled: false,
    min: "",
    max: "",
    addEventListener: function (type, fn) {
      listeners[id + ":" + type] = fn;
    },
    focus: function () {},
    scrollIntoView: function () {}
  };
}
var els = {};
var missing = [];
var document = {
  getElementById: function (id) {
    if (!markupIds[id]) {
      if (missing.indexOf(id) === -1) missing.push(id);
      return makeEl(id);
    }
    if (!els[id]) els[id] = makeEl(id);
    return els[id];
  },
  addEventListener: function (type, fn) { listeners["document:" + type] = fn; },
  querySelector: function () { return null; }
};

/* Freeze the browser clock so the stale-snapshot warning is exercised on every run. */
var fixedNow = "2026-10-01T20:00:00Z";
function TestDate() {
  var args = Array.prototype.slice.call(arguments);
  if (args.length) return new (Function.prototype.bind.apply(Date, [null].concat(args)))();
  return new Date(fixedNow);
}
TestDate.prototype = Date.prototype;
TestDate.now = function () { return new Date(fixedNow).getTime(); };
TestDate.parse = Date.parse;
TestDate.UTC = Date.UTC;

var fetchCalls = [];
function fakeFetch(url) {
  fetchCalls.push(url);
  return Promise.resolve({ ok: true, status: 200, json: function () { return Promise.resolve(feed); } });
}

var sandbox = {
  window: {},
  self: {},
  document: document,
  history: { replaceState: function () {} },
  location: { hash: "" },
  fetch: fakeFetch,
  Intl: Intl,
  Date: TestDate,
  Math: Math,
  JSON: JSON,
  console: console,
  Promise: Promise,
  setTimeout: setTimeout
};
sandbox.self = sandbox.window;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(logicSrc, sandbox, { filename: "scripts/logic.js" });
assert.ok(sandbox.window.RadioLogic, "logic.js must expose window.RadioLogic in a browser");
vm.runInContext(inline, sandbox, { filename: "index.html (inline)" });

function fakeEvent(attrName, attrValue, extra) {
  var node = {
    id: (extra && extra.id) || "",
    getAttribute: function (n) { return n === attrName ? attrValue : null; },
    matches: function () { return false; }
  };
  return { target: { closest: function () { return node; }, matches: function () { return false; }, value: extra && extra.value } };
}

function durEvent(key, value) {
  return {
    target: {
      getAttribute: function (n) { return n === "data-dur" ? key : null; },
      value: String(value),
      matches: function () { return false; },
      closest: function () { return null; }
    }
  };
}

function fire(key, ev) {
  var fn = listeners[key];
  assert.ok(fn, "no handler bound for " + key);
  fn(ev);
}

Promise.resolve().then(function () {
  return new Promise(function (r) { setTimeout(r, 0); });
}).then(function () {
  assert.deepStrictEqual(fetchCalls, ["data/broadcasts.json"], "page loads the generated feed");
  assert.deepStrictEqual(missing, [], "index.html is missing elements the script asks for: " + missing.join(", "));

  var rendered = ["verified", "filters", "leagues", "stations", "legend", "cal", "log", "answer",
    "band-stats", "band-bars", "band-note", "flags-limitation", "flags-review", "flags-note", "upnext"];
  rendered.forEach(function (id) {
    var el = els[id];
    assert.ok(el, "#" + id + " was never rendered");
    assert.ok((el.innerHTML + el.textContent).length > 0, "#" + id + " rendered empty");
  });
  assert.ok(/snapshot date/i.test(els.verified.textContent), "snapshot date and age line");
  assert.ok(/STALE · 4 days since the snapshot date 2026-09-27/.test(els.verified.textContent),
    "an old snapshot is dated and warned about");
  assert.ok(els.verified.className.indexOf("stale") !== -1, "stale snapshot uses warning styling");
  assert.ok(/21 if-necessary game possibilities across 13 dates/.test(els.verified.textContent),
    "the snapshot banner summarizes conditional games separately");
  assert.ok(els["flags-limitation"].innerHTML.indexOf("<details") !== -1, "known gaps render as disclosures");
  assert.ok(els["flags-review"].innerHTML.indexOf("<details") !== -1, "review flags render as disclosures");

  /* walk every single day in the window through the day renderer */
  var L = sandbox.window.RadioLogic;
  var days = L.eachDate(feed.meta.window_start, feed.meta.window_end);
  var withTable = 0;
  days.forEach(function (iso) {
    fire("cal:click", fakeEvent("data-date", iso));
    assert.ok(els["day-title"].textContent.indexOf(String(L.parseISO(iso).y)) !== -1, "day title for " + iso);
    if (els.log.innerHTML.indexOf("<table") !== -1) withTable++;
  });
  assert.strictEqual(withTable, 77, "every day with a listing or conditional possibility shows a table");

  /* Conditional-only postseason dates stay visible, but neither get counted as
     scheduled days nor contribute estimated broadcast minutes. */
  ["2026-10-09", "2026-10-20", "2026-10-30"].forEach(function (iso) {
    fire("cal:click", fakeEvent("data-date", iso));
    assert.ok(/No non-conditional listing/.test(els.answer.innerHTML), iso + " is a possibility, not a non-conditional listing");
    assert.ok(/estimated broadcast time.*0m of 12h/i.test(els.answer.innerHTML), iso + " contributes no minutes");
    assert.ok(/games? only if necessary/.test(els.log.innerHTML), iso + " carries a count-aware conditional badge");
    assert.ok(els.cal.innerHTML.indexOf("if-necessary game possibility") !== -1, iso + " is named in calendar accessibility text");
  });
  [["2026-10-07", "2 of 4 games only if necessary"], ["2026-10-16", "1 of 2 games only if necessary"]].forEach(function (item) {
    fire("cal:click", fakeEvent("data-date", item[0]));
    assert.ok(els.answer.innerHTML.indexOf("postseason game") !== -1, item[0] + " exposes mixed conditional possibilities");
    assert.ok(els.log.innerHTML.indexOf(item[1]) !== -1, item[0] + " keeps the confirmed/if-necessary game counts distinct");
    assert.ok(els.cal.innerHTML.indexOf("if-necessary game possibilit") !== -1, item[0] + " is named accessibly in the calendar");
    if (item[0] === mixedTestRow.date) {
      assert.ok(els.log.innerHTML.indexOf("Mixed listing · estimate omitted") !== -1,
        "a mixed aggregate is not presented as one current/finished game");
      assert.ok(/estimated broadcast time.*0m of 12h/i.test(els.answer.innerHTML),
        "even a synthetic time on a mixed group does not add estimated minutes");
      assert.ok(els.timeline.innerHTML.indexOf("title=\"" + mixedTestRow.title + "\"") === -1,
        "mixed group is omitted from the timeline until per-game times are known");
      assert.ok(els.conflicts.innerHTML.indexOf(mixedTestRow.title) === -1,
        "mixed group does not create a conflict warning");
    }
  });

  /* days either side of the window must not throw and must say so */
  fire("cal:click", fakeEvent("data-date", L.addDays(feed.meta.window_start, -1)));
  assert.ok(/Outside this snapshot/.test(els.answer.innerHTML), "day before the window");
  fire("cal:click", fakeEvent("data-date", L.addDays(feed.meta.window_end, 1)));
  assert.ok(/Outside this snapshot/.test(els.answer.innerHTML), "day after the window");

  /* filters */
  fire("filters:click", fakeEvent("data-station", "960"));
  fire("cal:click", fakeEvent("data-date", "2026-09-27"));
  assert.ok(els.log.innerHTML.indexOf("Athletics") !== -1, "960 filter keeps the A's");
  assert.ok(els.log.innerHTML.indexOf("Westwood One") === -1, "960 filter drops the national NFL rows");
  fire("filters:click", fakeEvent("data-station", null, { id: "all-stations" }));

  fire("leagues:click", fakeEvent("data-league", "MLS"));
  fire("cal:click", fakeEvent("data-date", "2026-10-17"));
  assert.ok(els.log.innerHTML.indexOf("Nashville") !== -1, "MLS filter keeps the Earthquakes");
  assert.ok(els.log.innerHTML.indexOf("Elon") === -1, "MLS filter drops college football");
  fire("leagues:click", fakeEvent("data-league", null, { id: "all-leagues" }));

  /* navigation */
  fire("cal:click", fakeEvent("data-date", "2026-10-15"));
  fire("next:click", {});
  assert.ok(els["day-title"].textContent.indexOf("October 16") !== -1, "next day");
  fire("prev:click", {});
  assert.ok(els["day-title"].textContent.indexOf("October 15") !== -1, "previous day");
  fire("jump:change", { target: { value: "2026-12-25", matches: function () { return false; } } });
  assert.ok(els["day-title"].textContent.indexOf("December 25") !== -1, "date picker jump");
  fire("jump:change", { target: { value: "2026-02-30", matches: function () { return false; } } });
  assert.ok(els["day-title"].textContent.indexOf("December 25") !== -1, "invalid calendar date is ignored");
  fire("prev-month:click", {});
  assert.ok(els["month-label"].textContent.indexOf("November") !== -1, "month back");
  fire("next-month:click", {});
  assert.ok(els["month-label"].textContent.indexOf("December") !== -1, "month forward");

  /* Regression: a date far outside the snapshot used to push the calendar grid
     out of bounds, and shiftMonth then refused to move in either direction, so
     the user was stranded on an empty month with two dead arrows. */
  fire("cal:click", fakeEvent("data-date", "2030-06-15"));
  assert.ok(/Outside this snapshot/.test(els.answer.innerHTML), "far future day still answers honestly");
  assert.ok(els["month-label"].textContent.indexOf("February 2027") !== -1,
    "calendar clamps to the last month of the window, got: " + els["month-label"].textContent);
  fire("prev-month:click", {});
  assert.ok(els["month-label"].textContent.indexOf("January 2027") !== -1,
    "month arrows still work after a far-future date");

  fire("cal:click", fakeEvent("data-date", "2020-01-01"));
  assert.ok(/Outside this snapshot/.test(els.answer.innerHTML), "far past day still answers honestly");
  assert.ok(els["month-label"].textContent.indexOf("September 2026") !== -1,
    "calendar clamps to the first month of the window, got: " + els["month-label"].textContent);
  fire("next-month:click", {});
  assert.ok(els["month-label"].textContent.indexOf("October 2026") !== -1,
    "month arrows still work after a far-past date");
  fire("cal:click", fakeEvent("data-date", "2026-10-15"));

  /* Duration estimates are the assumption the whole band answer rests on, so the
     control has to actually move the number, and reset has to actually reset. */
  assert.ok(els.durations.innerHTML.indexOf('data-dur="NFL"') !== -1, "duration controls render");
  assert.ok(els.durations.innerHTML.indexOf("default 195 min") !== -1, "the shipped default is printed");
  var bandBefore = els["band-stats"].innerHTML;
  var dayBefore = els.log.innerHTML;
  fire("durations:input", durEvent("NFL", 360));
  assert.notStrictEqual(els["band-stats"].innerHTML, bandBefore, "a longer NFL estimate recomputes the band");
  fire("durations:input", durEvent("NFL", 5));
  assert.notStrictEqual(els["band-stats"].innerHTML, bandBefore, "out-of-range input is ignored, last good value kept");
  fire("dur-reset:click", {});
  assert.strictEqual(els["band-stats"].innerHTML, bandBefore, "reset restores the shipped defaults");
  fire("cal:click", fakeEvent("data-date", "2026-10-15"));
  assert.strictEqual(els.log.innerHTML, dayBefore, "the day view comes back unchanged after a reset");

  /* search */
  fire("q:input", { target: { value: "stanford", matches: function () { return false; } } });
  assert.ok(els.results.innerHTML.indexOf("data-jump") !== -1, "search finds Stanford");
  fire("q:input", { target: { value: "zzzznothing", matches: function () { return false; } } });
  assert.ok(/No match/.test(els.results.innerHTML), "search reports an empty result honestly");

  /* the unplaced Week 18 row has to stay visible somewhere */
  assert.ok(/Week 18/.test(els.unplaced.innerHTML), "the undated 49ers game is surfaced, not hidden");

  console.log("render smoke test passed — " + days.length + " days walked, " + withTable + " with a table");
}).catch(function (err) {
  console.error(err && err.stack ? err.stack : err);
  process.exit(1);
});
