import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
const page = await context.newPage();
await page.goto('http://127.0.0.1:4173/index.html', { waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => window.__legatoOwner && document.querySelector('[data-legato-root="true"]'), null, { timeout: 30000 });

await page.evaluate(() => {
  try { localStorage.setItem('legato.tour.v1', '1'); } catch (e) {}
  const o = window.__legatoOwner;
  o.setState({
    tour: false, recovery: null, zone: 3, staff: 0, pos: 0, step: 6,
    scoreEvents: [], scoreSpans: [], scoreObjectId: null, spanDraft: null,
    selId: null, panel: null, halo: false
  });
});
await page.waitForTimeout(180);

const state = () => page.evaluate(() => {
  const o = window.__legatoOwner;
  return {
    events: o.state.scoreEvents,
    spans: o.state.scoreSpans,
    object: o.state.scoreObjectId,
    draft: o.state.spanDraft,
    spoken: o.state.spoken,
    doc: o.doc()
  };
});

// Arbitrary-position point events.
await page.evaluate(() => window.__legatoOwner.placeScoreEvent('clef', 'Bass clef', '\uE062', 'bass', { system: false }));
await page.waitForTimeout(80);
assert.equal(await page.evaluate(() => window.__legatoOwner.clefAt(0, 0)), 'bass', 'clef change should be active at its position');

await page.evaluate(() => {
  const o = window.__legatoOwner;
  o.setState({ pos: 1 }, () => o.placeScoreEvent('key', 'G major key signature', '', 1, { system: true }));
});
await page.waitForTimeout(100);
assert.equal(await page.evaluate(() => window.__legatoOwner.keyAt(1.5).name), 'G major', 'key event should be position-aware');

await page.evaluate(() => {
  const o = window.__legatoOwner;
  o.setState({ pos: 2 }, () => o.placeScoreEvent('meter', '3/4 time signature', '', '3/4', { system: true }));
});
await page.waitForTimeout(100);
assert.equal(await page.evaluate(() => window.__legatoOwner.meterAt(2.25)), '3/4', 'meter event should be position-aware');

await page.evaluate(() => {
  const o = window.__legatoOwner;
  o.setState({ pos: 2 }, () => o.placeScoreEvent('tempo', '120 BPM', '', 120, { system: true }));
});
await page.waitForTimeout(100);
assert.equal(Math.round(await page.evaluate(() => window.__legatoOwner.tempoAt(2.5))), 120, 'tempo event should be active after its point');
const sec = await page.evaluate(() => window.__legatoOwner.secondsBetween(0, 4));
assert.ok(sec > 1.9 && sec < 2.5, 'tempo integration should use both tempo regions');

await page.evaluate(() => {
  const o = window.__legatoOwner;
  o.setState({ pos: 1.5, staff: 0 }, () => o.placeScoreEvent('dynamic', 'mf', '\uE52D', '\uE52D', { system: false }));
});
await page.waitForTimeout(100);
assert.equal(await page.evaluate(() => window.__legatoOwner.effectiveScoreEvent('dynamic', 0, 2).name), 'mf', 'dynamic should apply from its exact position');

// Point one / point two spans.
await page.evaluate(() => {
  const o = window.__legatoOwner;
  o.setState({ pos: 0.5, staff: 0, step: 7 }, () => o.beginScoreSpan('slur', 'Slur', '\uE1FD'));
});
await page.waitForTimeout(80);
assert.ok((await state()).draft, 'slur point one should create a draft');
await page.evaluate(() => window.__legatoOwner.setState({ pos: 3, staff: 0, step: 10 }, () => window.__legatoOwner.finishScoreSpan()));
await page.waitForTimeout(100);
let snap = await state();
assert.equal(snap.spans.length, 1, 'slur should finish as one saved span');
assert.equal(snap.spans[0].p1, 0.5);
assert.equal(snap.spans[0].p2, 3);

await page.evaluate(() => {
  const o = window.__legatoOwner;
  o.setState({ pos: 1, staff: 0, step: 5 }, () => o.beginScoreSpan('pedal', 'Sustain pedal', '\uE650'));
});
await page.waitForTimeout(60);
await page.evaluate(() => window.__legatoOwner.setState({ pos: 4, staff: 0, step: 5 }, () => window.__legatoOwner.finishScoreSpan()));
await page.waitForTimeout(100);
assert.ok(await page.evaluate(() => window.__legatoOwner.activeScoreSpan('pedal', 0, 2.5)), 'pedal should be active between point one and point two');

await page.evaluate(() => {
  const o = window.__legatoOwner;
  o.setState({ pos: 0, staff: 1, step: 6 }, () => o.beginScoreSpan('hairpin-up', 'Crescendo', '\uE53E'));
});
await page.waitForTimeout(60);
await page.evaluate(() => window.__legatoOwner.setState({ pos: 2, staff: 1, step: 6 }, () => window.__legatoOwner.finishScoreSpan()));
await page.waitForTimeout(100);
assert.ok(await page.evaluate(() => window.__legatoOwner.activeScoreSpan('hairpin-up', 1, 1)), 'hairpin should be active inside its range');

// The command catalog must start a real two-point object, not decorate one note.
await page.evaluate(() => {
  const o = window.__legatoOwner;
  const ci = window.CAT ? window.CAT.findIndex(c => c[0] === 'Lines') : -1;
  const cat = ci >= 0 ? ci : 6;
  const idx = o.constructor ? 1 : 1;
  o.setState({ halo: true, haloCat: cat, haloIdx: idx, pos: 5, staff: 0, spanDraft: null }, () => o.haloApply());
});
await page.waitForTimeout(100);
assert.ok((await state()).draft, 'choosing Slur in commands should set point one');
await page.evaluate(() => window.__legatoOwner.cancelScoreSpan());

// Select, move, edit endpoint, and delete a real object.
snap = await state();
const slurId = snap.spans.find(x => x.type === 'slur').id;
await page.evaluate(id => window.__legatoOwner.selectScoreObject(id), slurId);
await page.waitForTimeout(50);
await page.evaluate(() => window.__legatoOwner.moveScoreObject(0.5, 0));
await page.waitForTimeout(80);
assert.equal(await page.evaluate(id => window.__legatoOwner.scoreObjectById(id).p1, slurId), 1, 'selected span should move with arrows/model movement');
await page.evaluate(() => window.__legatoOwner.editSelectedScoreObject());
await page.waitForTimeout(50);
assert.ok((await state()).draft, 'A/edit should reopen a span endpoint');
await page.evaluate(() => window.__legatoOwner.setState({ pos: 4.5, staff: 0, step: 11 }, () => window.__legatoOwner.finishScoreSpan()));
await page.waitForTimeout(80);
assert.equal(await page.evaluate(id => window.__legatoOwner.scoreObjectById(id).p2, slurId), 4.5, 'span endpoint should be replaceable');

const dynamicId = (await state()).events.find(x => x.type === 'dynamic').id;
await page.evaluate(id => window.__legatoOwner.selectScoreObject(id), dynamicId);
await page.waitForTimeout(40);
await page.evaluate(() => window.__legatoOwner.deleteScoreObject());
await page.waitForTimeout(80);
assert.equal(await page.evaluate(() => window.__legatoOwner.state.scoreEvents.some(x => x.type === 'dynamic')), false, 'selected point event should delete');

// DOM and persistence.
await page.waitForFunction(() => document.querySelectorAll('[data-score-object="true"]').length >= 5, null, { timeout: 10000 });
const rendered = await page.locator('[data-score-object="true"]').count();
assert.ok(rendered >= 5, 'point events and spans should render as score objects');
snap = await state();
assert.ok(Array.isArray(snap.doc.scoreEvents) && Array.isArray(snap.doc.scoreSpans), 'events and spans should be saved in project documents');
assert.ok(snap.doc.scoreEvents.length >= 4 && snap.doc.scoreSpans.length >= 3, 'saved document should contain placed notation');

console.log('Live notation object checks passed', JSON.stringify({ events: snap.doc.scoreEvents.length, spans: snap.doc.scoreSpans.length, rendered }));
await browser.close();
