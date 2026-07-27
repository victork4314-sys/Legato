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
    selId: null, panel: null, halo: false, hub: false, kb: null, ptrOn: false
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

// Editable rehearsal/technique text. State settles before DONE, matching real controller use.
await page.evaluate(() => {
  const o = window.__legatoOwner;
  o.setState({ pos: 2.5, staff: 0 }, () => o.placeScoreEvent('technique', 'Playing technique', '', 'pizz.', { system: false, text: 'pizz.' }));
});
await page.waitForTimeout(80);
let techniqueId = (await state()).events.find(x => x.type === 'technique').id;
await page.evaluate(id => window.__legatoOwner.selectScoreObject(id), techniqueId);
await page.evaluate(() => window.__legatoOwner.editSelectedScoreObject());
await page.waitForTimeout(40);
assert.equal(await page.evaluate(() => window.__legatoOwner.state.kb), 'scoreText', 'text object should open the score text keyboard field');
await page.evaluate(() => window.__legatoOwner.setState({ scoreText: 'arco' }));
await page.waitForTimeout(40);
await page.evaluate(() => window.__legatoOwner.finishScoreObjectText());
await page.waitForTimeout(80);
assert.equal(await page.evaluate(id => window.__legatoOwner.scoreObjectById(id).text, techniqueId), 'arco', 'edited technique text should save');
assert.equal(await page.evaluate(() => window.__legatoOwner.state.kb), null, 'saving score text should close the keyboard');

// Point one / point two spans. The cursor settles before the controller A press.
await page.evaluate(() => {
  const o = window.__legatoOwner;
  o.setState({ pos: 0.5, staff: 0, step: 7 }, () => o.beginScoreSpan('slur', 'Slur', '\uE1FD'));
});
await page.waitForTimeout(80);
assert.ok((await state()).draft, 'slur point one should create a draft');
await page.evaluate(() => window.__legatoOwner.setState({ pos: 3, staff: 0, step: 10 }));
await page.waitForTimeout(40);
const beforeConfirm = await page.evaluate(() => {
  const o = window.__legatoOwner;
  return { draft: !!o.state.spanDraft, zone: o.state.zone, ptrOn: o.state.ptrOn, kb: o.state.kb, panel: o.state.panel, hub: o.state.hub, halo: o.state.halo };
});
assert.deepEqual(beforeConfirm, { draft: true, zone: 3, ptrOn: false, kb: null, panel: null, hub: false, halo: false }, 'controller span confirmation should begin from a clean score-editing state');
await page.evaluate(() => {
  const o = window.__legatoOwner;
  const original = o.finishScoreSpan.bind(o);
  window.__spanFinishTrace = { calls: 0, before: null, afterSync: null, result: null };
  o.finishScoreSpan = (...args) => {
    window.__spanFinishTrace.calls += 1;
    window.__spanFinishTrace.before = {
      draft: o.state.spanDraft ? { id: o.state.spanDraft.id, p1: o.state.spanDraft.p1, s1: o.state.spanDraft.s1 } : null,
      spans: (o.state.scoreSpans || []).length,
      pos: o.state.pos,
      staff: o.state.staff,
      step: o.state.step
    };
    const result = original(...args);
    window.__spanFinishTrace.result = result;
    window.__spanFinishTrace.afterSync = {
      draft: o.state.spanDraft ? { id: o.state.spanDraft.id, p1: o.state.spanDraft.p1, s1: o.state.spanDraft.s1 } : null,
      spans: (o.state.scoreSpans || []).length,
      object: o.state.scoreObjectId,
      spoken: o.state.spoken
    };
    return result;
  };
  window.__restoreFinishScoreSpan = () => { o.finishScoreSpan = original; };
});
await page.evaluate(() => window.__legatoOwner.dispatch('confirm', 'press'));
await page.waitForTimeout(160);
let snap = await state();
const spanTrace = await page.evaluate(() => ({ trace: window.__spanFinishTrace, state: { draft: window.__legatoOwner.state.spanDraft, spans: window.__legatoOwner.state.scoreSpans, object: window.__legatoOwner.state.scoreObjectId, spoken: window.__legatoOwner.state.spoken, mod: !!window.__legatoOwner._mod } }));
console.log('Span confirm trace', JSON.stringify(spanTrace));
await page.evaluate(() => window.__restoreFinishScoreSpan());
assert.equal(spanTrace.trace.calls, 1, 'controller A should call finishScoreSpan exactly once');
assert.equal(spanTrace.trace.result, true, 'finishScoreSpan should accept the live draft');
assert.equal(snap.spans.length, 1, 'controller A should finish a saved slur span');
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
  o.setState({ halo: true, haloCat: 6, haloIdx: 1, pos: 5, staff: 0, spanDraft: null }, () => o.haloApply());
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
await page.evaluate(() => window.__legatoOwner.dispatch('delete', 'press'));
await page.waitForTimeout(80);
assert.equal(await page.evaluate(() => window.__legatoOwner.state.scoreEvents.some(x => x.type === 'dynamic')), false, 'controller B should delete a selected point event');

// DOM and persistence.
await page.waitForFunction(() => document.querySelectorAll('[data-score-object="true"]').length >= 5, null, { timeout: 10000 });
const rendered = await page.locator('[data-score-object="true"]').count();
assert.ok(rendered >= 5, 'point events and spans should render as score objects');
snap = await state();
assert.ok(Array.isArray(snap.doc.scoreEvents) && Array.isArray(snap.doc.scoreSpans), 'events and spans should be saved in project documents');
assert.ok(snap.doc.scoreEvents.length >= 5 && snap.doc.scoreSpans.length >= 3, 'saved document should contain placed notation');

// MIDI should include a header and use the new tempo-event path without downloading.
await page.evaluate(() => {
  const o = window.__legatoOwner;
  o.download = (name, mime, data) => { window.__midiCapture = { name, mime, length: data.length, head: Array.from(data.slice(0, 4)) }; };
  o.exportMidi();
});
await page.waitForTimeout(80);
const midi = await page.evaluate(() => window.__midiCapture);
assert.ok(midi && midi.name.endsWith('.mid') && midi.length > 30, 'MIDI export should produce a non-empty file');
assert.deepEqual(midi.head, [77, 84, 104, 100], 'MIDI should begin with MThd');

// Removing a player must remove/shift its notation ownership.
await page.evaluate(() => {
  const o = window.__legatoOwner;
  const last = o.state.players.length - 1;
  o.setState({ staff: last, pos: 1 }, () => {
    o.placeScoreEvent('technique', 'Last staff technique', '', 'mute', { system: false, text: 'mute' });
    o.setState({ pos: 1.5 }, () => o.beginScoreSpan('pedal', 'Last staff pedal', '\uE650'));
  });
});
await page.waitForTimeout(100);
await page.evaluate(() => window.__legatoOwner.setState({ pos: 2.5 }, () => window.__legatoOwner.finishScoreSpan()));
await page.waitForTimeout(80);
const beforePlayers = await page.evaluate(() => window.__legatoOwner.state.players.length);
await page.evaluate(() => window.__legatoOwner.removePlayer(window.__legatoOwner.state.players.length - 1));
await page.waitForTimeout(100);
assert.equal(await page.evaluate(() => window.__legatoOwner.state.players.length), beforePlayers - 1, 'player removal should complete');
assert.equal(await page.evaluate(() => {
  const o = window.__legatoOwner, max = o.state.players.length - 1;
  return o.state.scoreEvents.some(x => !x.system && x.s > max) || o.state.scoreSpans.some(x => !x.system && (x.s1 > max || x.s2 > max));
}), false, 'removed-player notation must not become orphaned');

// Removing the final measure clips/removes objects beyond the new end.
await page.evaluate(() => {
  const o = window.__legatoOwner;
  o.setState({ bars: 4, staff: 0, pos: 15 }, () => o.placeScoreEvent('text', 'late', '', 'late', { system: false, text: 'late' }));
});
await page.waitForTimeout(60);
await page.evaluate(() => {
  const o = window.__legatoOwner;
  o.setState({ pos: 14 }, () => o.beginScoreSpan('line', 'Late line', '—'));
});
await page.waitForTimeout(50);
await page.evaluate(() => window.__legatoOwner.setState({ pos: 15.5 }, () => window.__legatoOwner.finishScoreSpan()));
await page.waitForTimeout(60);
await page.evaluate(() => window.__legatoOwner.runOp('Remove last measure'));
await page.waitForTimeout(100);
assert.equal(await page.evaluate(() => window.__legatoOwner.state.bars), 3, 'last measure should be removed');
assert.equal(await page.evaluate(() => {
  const o = window.__legatoOwner, end = o.state.bars * o.barCapacity();
  return o.state.scoreEvents.some(x => x.p >= end) || o.state.scoreSpans.some(x => x.p1 >= end || x.p2 >= end);
}), false, 'notation beyond the removed measure must be removed or clipped');

// A new project must be genuinely empty.
await page.evaluate(() => window.__legatoOwner.newProject());
await page.waitForTimeout(100);
assert.equal(await page.evaluate(() => window.__legatoOwner.state.scoreEvents.length), 0, 'new project should clear point events');
assert.equal(await page.evaluate(() => window.__legatoOwner.state.scoreSpans.length), 0, 'new project should clear spans');

console.log('Live notation object checks passed', JSON.stringify({ rendered, midiBytes: midi.length, playerCleanup: true, measureCleanup: true }));
await browser.close();
