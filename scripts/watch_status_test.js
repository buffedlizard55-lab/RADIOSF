"use strict";
const assert = require('assert');
const vm = require('vm');
const fs = require('fs');
const source = fs.readFileSync(__dirname + '/watch_status.js', 'utf8');
async function run(payload, ok = true) {
  const els = {'watch-status': {}, 'watch-report': {}};
  vm.runInNewContext(source, {document: {getElementById: id => els[id]},
    AbortController, setTimeout, clearTimeout, Date,
    fetch: async () => ({ok, status: 403, json: async () => payload})});
  await new Promise(resolve => setImmediate(resolve));
  return els;
}
function issue(when, body='') {
  return {title:'[Source watch status] Latest scheduled check', user:{login:'github-actions[bot]'},
    body:'Checked: '+when+'\n'+body};
}
(async () => {
  for (const payload of [[], {}, [issue('bad')], [issue('2099-01-01')],
    [{...issue(new Date().toISOString()), user:{login:'stranger'}}]]) {
    assert.match((await run(payload))['watch-status'].textContent, /unavailable/);
  }
  assert.match((await run([], false))['watch-status'].textContent, /HTTP 403/);
  assert.match((await run([issue('2020-01-01')]))['watch-status'].textContent, /STALE/);
  const result = await run([issue(new Date().toISOString(), '<script>alert(1)</script>')]);
  assert.match(result['watch-report'].textContent, /<script>/);
  assert.equal(result['watch-report'].innerHTML, undefined);
  console.log('monitor status tests passed: missing, malformed, unauthorized, future, stale, HTTP error, safe text');
})().catch(e => {console.error(e); process.exitCode=1;});
