/* Public GitHub issue transport: scheduled checks update one bot-authored report.
   Separate from feed loading: errors cannot break the calendar or imply clear. */
(function () {
  "use strict";
  var status = document.getElementById("watch-status");
  var report = document.getElementById("watch-report");
  var controller = new AbortController();
  var timer = setTimeout(function () { controller.abort(); }, 10000);
  fetch("https://api.github.com/repos/buffedlizard55-lab/RADIOSF/issues?state=open&creator=github-actions%5Bbot%5D&per_page=100", {
    signal: controller.signal, cache: "no-store"
  }).then(function (r) {
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  }).then(function (issues) {
    if (!Array.isArray(issues)) throw new Error("Invalid response");
    var issue = issues.find(function (i) {
      return !i.pull_request && i.title === "[Source watch status] Latest scheduled check" &&
        i.user && i.user.login === "github-actions[bot]";
    });
    if (!issue || typeof issue.body !== "string") throw new Error("No scheduled report published yet");
    var match = /^Checked: (.+)$/m.exec(issue.body);
    var checked = match && Date.parse(match[1]);
    if (!Number.isFinite(checked) || checked > Date.now() + 300000) throw new Error("Invalid check timestamp");
    var stale = Date.now() - checked > 36 * 3600000;
    status.textContent = (stale ? "STALE — " : "") + "Scheduled check: " + match[1] +
      ". Expand the reports below for changes and unavailable sources. A successful workflow does not mean every source is clear. Checks do not update the calendar.";
    report.textContent = issue.body; // Never insert remote Markdown as HTML.
  }).catch(function (error) {
    status.textContent = "Latest scheduled check unavailable (" + error.message +
      "). Schedule freshness is unknown; use the run link below. The dated record is not a live status.";
  }).finally(function () { clearTimeout(timer); });
})();
