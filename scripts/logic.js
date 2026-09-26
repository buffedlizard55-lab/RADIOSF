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

  function shareStation(a, b) {
    var shared = sharedStations(a, b);
    return shared.length ? shared.join(", ") : null;
  }

  function sameDayConflicts(list) {
    var out = [];
    var i, j, a, b, station, aEnd, bEnd;
    for (i = 0; i < list.length; i++) {
      for (j = i + 1; j < list.length; j++) {
        a = list[i];
        b = list[j];
        station = shareStation(a, b);
        if (!station) continue;
        if (!a.start_pt || !b.start_pt) {
          out.push({
            kind: "tbd",
            station: station,
            ids: [a.id, b.id],
            text: "Both are listed on " + station + " and at least one kickoff is still TBD, so a conflict cannot be ruled out."
          });
          continue;
        }
        aEnd = endMinutes(a);
        bEnd = endMinutes(b);
        if (aEnd == null || bEnd == null) continue;
        if (rangesOverlap(minutes(a.start_pt), aEnd, minutes(b.start_pt), bEnd)) {
          out.push({
            kind: "overlap",
            station: station,
            ids: [a.id, b.id],
            text: "Estimated windows overlap on " + station + ". A local game usually keeps the station; Westwood One says not every affiliate airs every broadcast."
          });
        }
      }
    }
    return out;
  }

  function clip(start, end, lo, hi) {
    return Math.max(0, Math.min(end, hi) - Math.max(start, lo));
  }

  function unionMinutes(list, lo, hi) {
    var spans = [];
    var i, s, e, merged, cur, out, k;
    for (i = 0; i < list.length; i++) {
      if (!list[i].start_pt || !list[i].duration_est_min) continue;
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

  function filterBroadcasts(list, stationId) {
    if (!stationId || stationId === "all") return list.slice();
    return list.filter(function (b) { return b.stations.indexOf(stationId) !== -1; });
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

  return {
    WEEKDAYS: WEEKDAYS,
    MONTHS: MONTHS,
    parseISO: parseISO,
    toISO: toISO,
    addDays: addDays,
    weekdayIndex: weekdayIndex,
    formatLong: formatLong,
    formatMonth: formatMonth,
    minutes: minutes,
    fromMinutes: fromMinutes,
    label12: label12,
    etToPt: etToPt,
    endMinutes: endMinutes,
    rangesOverlap: rangesOverlap,
    sharedStations: sharedStations,
    shareStation: shareStation,
    sameDayConflicts: sameDayConflicts,
    clip: clip,
    unionMinutes: unionMinutes,
    monthCells: monthCells,
    inWindow: inWindow,
    filterBroadcasts: filterBroadcasts,
    byDate: byDate,
    sortBroadcasts: sortBroadcasts,
    formatDuration: formatDuration
  };
});
