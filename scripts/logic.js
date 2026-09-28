/* Pure calendar helpers. Used by index.html and scripts/ui_logic_test.js. */
(function (root, factory) {
  var api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.RadioLogic = api;
})(typeof self !== "undefined" ? self : this, function () {
  var WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

  function pad(n) {
    return String(n).padStart(2, "0");
  }

  function parseISO(iso) {
    var p = String(iso).split("-");
    return { y: +p[0], m: +p[1], d: +p[2] };
  }

  function isISODate(iso) {
    if (typeof iso !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(iso)) return false;
    var p = parseISO(iso);
    if (p.m < 1 || p.m > 12 || p.d < 1 || p.d > 31) return false;
    var date = new Date(0);
    date.setUTCHours(0, 0, 0, 0);
    date.setUTCFullYear(p.y, p.m - 1, p.d);
    return date.getUTCFullYear() === p.y && date.getUTCMonth() === p.m - 1 && date.getUTCDate() === p.d;
  }

  function isConditional(b) {
    return !!(b && (b.conditional || b.status === "if-necessary"));
  }

  function hasConditionalPossibility(b) {
    return isConditional(b) || !!(b && Number(b.conditional_game_count) > 0);
  }

  function conditionalGameCount(b) {
    if (!b) return 0;
    var count = Number(b.conditional_game_count) || 0;
    if (count > 0) return count;
    if (!isConditional(b)) return 0;
    return Number(b.game_count) || 1;
  }

  /* The snapshot is a schedule, not a radio log. An explicit final status proves
     the game ended, not that an affiliate carried it; a passed date or elapsed
     duration estimate proves neither. Conditional windows are possibilities. */
  function airState(b, now) {
    if (!b.date) return "unplaced";
    if (isConditional(b)) return "conditional";
    if (hasConditionalPossibility(b)) return "mixed";
    if (b.status === "final") return "final";
    if (b.date < now.iso) return "past-unchecked";
    if (!b.start_pt) return "tba";
    if (b.date > now.iso) return "upcoming";
    var start = minutes(b.start_pt);
    var end = start + (b.duration_est_min || 0);
    if (now.minutes < start) return b.status === "pregame" ? "pregame" : "upcoming";
    if (now.minutes < end) return "on";
    return "elapsed-unchecked";
  }

  function toISO(y, m, d) {
    return y + "-" + pad(m) + "-" + pad(d);
  }

  function toUTC(iso) {
    var p = parseISO(iso);
    return Date.UTC(p.y, p.m - 1, p.d);
  }

  function addDays(iso, n) {
    var t = new Date(toUTC(iso) + n * 86400000);
    return toISO(t.getUTCFullYear(), t.getUTCMonth() + 1, t.getUTCDate());
  }

  function weekdayIndex(iso) {
    return new Date(toUTC(iso)).getUTCDay();
  }

  function formatLong(iso) {
    var p = parseISO(iso);
    return WEEKDAYS[weekdayIndex(iso)] + ", " + MONTHS[p.m - 1] + " " + p.d + ", " + p.y;
  }

  function formatMonth(y, m) {
    return MONTHS[m - 1] + " " + y;
  }

  function minutes(hhmm) {
    if (!hhmm) return null;
    var p = String(hhmm).split(":");
    return (+p[0]) * 60 + (+p[1]);
  }

  function fromMinutes(min) {
    var wrapped = ((min % 1440) + 1440) % 1440;
    return pad(Math.floor(wrapped / 60)) + ":" + pad(wrapped % 60);
  }

  function label12(hhmm) {
    if (!hhmm) return "Time TBD";
    var m = minutes(hhmm);
    var h = Math.floor(m / 60);
    var min = m % 60;
    var ap = h >= 12 ? "PM" : "AM";
    var h12 = h % 12;
    if (h12 === 0) h12 = 12;
    return h12 + ":" + pad(min) + " " + ap + " PT";
  }

  function etToPt(etHHMM) {
    var m = minutes(etHHMM) - 180;
    var dayShift = 0;
    if (m < 0) {
      dayShift = -1;
      m += 1440;
    } else if (m >= 1440) {
      dayShift = 1;
      m -= 1440;
    }
    return { hhmm: fromMinutes(m), dayShift: dayShift };
  }

  function endMinutes(b) {
    if (!b.start_pt || !b.duration_est_min) return null;
    return minutes(b.start_pt) + b.duration_est_min;
  }

  /* Pacific wall clock for an absolute instant, so a conversion is verified by
     converting back rather than by trusting an offset table. */
  function pacificWallClock(date) {
    var fmt = new Intl.DateTimeFormat("en-US", {
      timeZone: "America/Los_Angeles",
      year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", hourCycle: "h23"
    });
    var parts = {};
    fmt.formatToParts(date).forEach(function (p) { parts[p.type] = p.value; });
    return { iso: parts.year + "-" + parts.month + "-" + parts.day, hhmm: parts.hour + ":" + parts.minute };
  }

  /* Every clock time in the feed is a Pacific wall clock. An .ics file needs an
     absolute instant, and Pacific is UTC-7 or UTC-8 depending on the date, so
     try both and keep whichever one reads back as the requested wall clock.
     Returns null rather than guessing a time that does not resolve. */
  function ptToUtcIso(iso, hhmm) {
    var base = Date.parse(iso + "T" + hhmm + ":00Z");
    if (isNaN(base)) return null;
    for (var offset = 7; offset <= 8; offset++) {
      var candidate = new Date(base + offset * 3600000);
      var wall = pacificWallClock(candidate);
      if (wall.iso === iso && wall.hhmm === hhmm) return candidate.toISOString();
    }
    return null;
  }

  function rangesOverlap(a0, a1, b0, b1) {
    return a0 < b1 && b0 < a1;
  }

  function sharedStations(a, b) {
    var out = [];
    a.stations.forEach(function (s) {
      if (b.stations.indexOf(s) !== -1 && out.indexOf(s) === -1) out.push(s);
    });
    return out;
  }

  function conflictTitle(b) {
    return b.title ? "\u201c" + b.title + "\u201d" : b.id;
  }

  function conflictEntry(b) {
    return conflictTitle(b) + (b.start_pt ? " at " + label12(b.start_pt) : " (start time TBD)");
  }

  /* Overlaps stay pairwise, because each pair is a different clash and the two
     titles are what the reader needs. TBD warnings are collapsed to one per
     station: a day with three TBD listings on 1050 produced three identical
     pairwise warnings before, which buried the real overlaps. */
  function sameDayConflicts(list) {
    /* An if-necessary game is a possible future slot, not a scheduled broadcast.
       Mixed date rows stay grouped until a source supplies per-game detail, so
       they are conservatively held out of conflicts too. */
    list = list.filter(function (b) { return !hasConditionalPossibility(b); });
    var out = [];
    var tbdOrder = [];
    var tbdByStation = {};
    var i, j, k, a, b, shared, station, group, aEnd, bEnd;

    function noteTbd(station, b) {
      var g = tbdByStation[station];
      if (g.ids.indexOf(b.id) !== -1) return;
      g.ids.push(b.id);
      g.entries.push(conflictEntry(b));
    }

    for (i = 0; i < list.length; i++) {
      for (j = i + 1; j < list.length; j++) {
        a = list[i];
        b = list[j];
        shared = sharedStations(a, b);
        if (!shared.length) continue;
        if (!a.start_pt || !b.start_pt) {
          for (k = 0; k < shared.length; k++) {
            station = shared[k];
            if (!tbdByStation[station]) {
              tbdByStation[station] = { ids: [], entries: [] };
              tbdOrder.push(station);
            }
            noteTbd(station, a);
            noteTbd(station, b);
          }
          continue;
        }
        aEnd = endMinutes(a);
        bEnd = endMinutes(b);
        if (aEnd == null || bEnd == null) continue;
        if (rangesOverlap(minutes(a.start_pt), aEnd, minutes(b.start_pt), bEnd)) {
          out.push({
            kind: "overlap",
            station: shared.join(", "),
            ids: [a.id, b.id],
            text: "Estimated windows overlap on " + shared.join(", ") + ": " +
              conflictEntry(a) + " and " + conflictEntry(b) +
              ". These are estimated windows, not a station log. The overlap does not establish " +
              "which game the station will carry, or when it will switch. Check the linked sources."
          });
        }
      }
    }

    for (i = 0; i < tbdOrder.length; i++) {
      station = tbdOrder[i];
      group = tbdByStation[station];
      out.push({
        kind: "tbd",
        station: station,
        ids: group.ids.slice(),
        text: group.ids.length + " listings share " + station +
          " this day and at least one start time is still TBD, so an overlap cannot be " +
          "ruled out: " + group.entries.join("; ") + "."
      });
    }
    return out;
  }

  function unionMinutes(list, lo, hi) {
    var spans = [];
    var i, s, e, merged, cur, out, k;
    for (i = 0; i < list.length; i++) {
      if (hasConditionalPossibility(list[i]) || !list[i].start_pt || !list[i].duration_est_min) continue;
      s = Math.max(lo, minutes(list[i].start_pt));
      e = Math.min(hi, endMinutes(list[i]));
      if (e > s) spans.push([s, e]);
    }
    spans.sort(function (a, b) { return a[0] - b[0]; });
    merged = [];
    for (i = 0; i < spans.length; i++) {
      if (!merged.length || spans[i][0] > merged[merged.length - 1][1]) merged.push(spans[i].slice());
      else merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], spans[i][1]);
    }
    out = 0;
    for (k = 0; k < merged.length; k++) out += merged[k][1] - merged[k][0];
    return out;
  }

  function monthCells(year, month) {
    var first = toISO(year, month, 1);
    var lead = weekdayIndex(first);
    var cells = [];
    var i, cursor;
    for (i = 0; i < lead; i++) cells.push(null);
    cursor = first;
    while (parseISO(cursor).m === month && parseISO(cursor).y === year) {
      cells.push(cursor);
      cursor = addDays(cursor, 1);
    }
    while (cells.length % 7 !== 0) cells.push(null);
    return cells;
  }

  function inWindow(iso, start, end) {
    return iso >= start && iso <= end;
  }

  function byDate(list, iso) {
    return list.filter(function (b) { return b.date === iso; });
  }

  function sortBroadcasts(list) {
    return list.slice().sort(function (a, b) {
      if (!a.start_pt && !b.start_pt) return a.title.localeCompare(b.title);
      if (!a.start_pt) return 1;
      if (!b.start_pt) return -1;
      if (a.start_pt === b.start_pt) return a.title.localeCompare(b.title);
      return a.start_pt < b.start_pt ? -1 : 1;
    });
  }

  function formatDuration(min) {
    var h = Math.floor(min / 60);
    var m = min % 60;
    if (h && m) return h + "h " + m + "m";
    if (h) return h + "h";
    return m + "m";
  }

  /* Every ISO date from start through end, inclusive. */
  function eachDate(start, end) {
    var out = [];
    var cursor = start;
    var guard = 0;
    while (cursor <= end && guard < 2000) {
      out.push(cursor);
      cursor = addDays(cursor, 1);
      guard++;
    }
    return out;
  }

  /* Minutes of the lo..hi band that a single station is estimated to be carrying a game. */
  function stationMinutes(list, stationId, lo, hi) {
    return unionMinutes(list.filter(function (b) {
      return b.stations.indexOf(stationId) !== -1;
    }), lo, hi);
  }

  /*
   * Measures the user's "10 AM to 10 PM is mostly live sports" hunch against the data
   * instead of assuming it. Returns per-day coverage plus aggregates, all in minutes.
   * If-necessary-only rows never count as scheduled listings or minutes. Mixed grouped
   * rows with conditional games are also excluded from minutes until per-game starts
   * are available, while their possible-game count remains visible. TBD-heavy dates
   * are reported separately rather than silently described as quiet.
   */
  function bandSummary(list, start, end, lo, hi) {
    var span = hi - lo;
    var dates = eachDate(start, end);
    var byWeekday = [];
    var i;
    for (i = 0; i < 7; i++) byWeekday.push({ days: 0, covered: 0, withListings: 0 });
    var days = dates.map(function (iso) {
      var allRows = byDate(list, iso);
      var possibilities = allRows.filter(hasConditionalPossibility);
      var rows = allRows.filter(function (b) { return !isConditional(b); });
      var covered = unionMinutes(rows, lo, hi);
      var timed = rows.filter(function (b) { return b.start_pt; }).length;
      var w = byWeekday[weekdayIndex(iso)];
      w.days++;
      w.covered += covered;
      if (rows.length) w.withListings++;
      return {
        date: iso,
        rows: rows.length,
        possibilities: possibilities.length,
        conditionalGames: possibilities.reduce(function (sum, b) { return sum + conditionalGameCount(b); }, 0),
        timed: timed,
        tbd: rows.length - timed,
        covered: covered,
        share: span ? covered / span : 0
      };
    });
    var withListings = days.filter(function (d) { return d.rows > 0; });
    var withPossibilities = days.filter(function (d) { return d.possibilities > 0; });
    var conditionalOnly = days.filter(function (d) { return d.rows === 0 && d.possibilities > 0; });
    var majority = days.filter(function (d) { return d.covered * 2 > span; });
    var totalCovered = days.reduce(function (acc, d) { return acc + d.covered; }, 0);
    var busiest = days.slice().sort(function (a, b) {
      return b.covered - a.covered || (a.date < b.date ? -1 : 1);
    })[0] || null;
    return {
      lo: lo,
      hi: hi,
      span: span,
      days: days,
      dayCount: days.length,
      daysWithListings: withListings.length,
      daysWithPossibilities: withPossibilities.length,
      conditionalGames: days.reduce(function (sum, d) { return sum + d.conditionalGames; }, 0),
      daysConditionalOnly: conditionalOnly.length,
      daysMajority: majority.length,
      daysEmpty: days.filter(function (d) { return d.rows === 0 && d.possibilities === 0; }).length,
      meanCovered: days.length ? Math.round(totalCovered / days.length) : 0,
      meanCoveredOnListingDays: withListings.length
        ? Math.round(withListings.reduce(function (acc, d) { return acc + d.covered; }, 0) / withListings.length)
        : 0,
      byWeekday: byWeekday,
      busiest: busiest
    };
  }

  return {
    eachDate: eachDate,
    stationMinutes: stationMinutes,
    bandSummary: bandSummary,
    WEEKDAYS: WEEKDAYS,
    MONTHS: MONTHS,
    parseISO: parseISO,
    isISODate: isISODate,
    isConditional: isConditional,
    hasConditionalPossibility: hasConditionalPossibility,
    conditionalGameCount: conditionalGameCount,
    airState: airState,
    toISO: toISO,
    addDays: addDays,
    weekdayIndex: weekdayIndex,
    formatLong: formatLong,
    formatMonth: formatMonth,
    minutes: minutes,
    fromMinutes: fromMinutes,
    label12: label12,
    etToPt: etToPt,
    pacificWallClock: pacificWallClock,
    ptToUtcIso: ptToUtcIso,
    endMinutes: endMinutes,
    rangesOverlap: rangesOverlap,
    sharedStations: sharedStations,
    sameDayConflicts: sameDayConflicts,
    unionMinutes: unionMinutes,
    monthCells: monthCells,
    inWindow: inWindow,
    byDate: byDate,
    sortBroadcasts: sortBroadcasts,
    formatDuration: formatDuration
  };
});
