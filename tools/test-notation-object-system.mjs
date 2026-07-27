import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
await context.addInitScript(() => {
  try { localStorage.setItem('legato.tour.v1', '1'); } catch (e) {}
});
const page = await context.newPage();
await page.goto('http://127.0.0.1:4173/index.html', { waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => window.__legatoOwner && document.querySelector('[data-legato-root="true"]'), null, { timeout: 30000 });

const pause = ms => page.waitForTimeout(ms);
const setOwnerState = async patch => {
  await page.evaluate(value => window.__legatoOwner.setState(value), patch);
  await pause(70);
};
const invoke = async (method, ...args) => {
  const result = await page.evaluate(({ method, args }) => {
    const owner = window.__legatoOwner;
    return owner[method].apply(owner, args);
  }, { method, args });
  await pause(80);
  return result;
};
const snapshot = () => page.evaluate(() => {
  const owner = window.__legatoOwner;
  return {
    events: owner.state.scoreEvents || [],
    spans: owner.state.scoreSpans || [],
    object: owner.state.scoreObjectId,
    draft: owner.state.spanDraft,
    spoken: owner.state.spoken,
    doc: owner.doc()
  };
});

await setOwnerState({
  tour: false, recovery: null, zone: 3, staff: 0, pos: 0, step: 6,
  scoreEvents: [], scoreSpans: [], scoreObjectId: null, spanDraft: null,
  selId: null, panel: null, halo: false, hub: false, menu: false,
  kb: null, ptrOn: false, radial: false, picker: false
});

// Point events must apply from their exact score positions.
await invoke('placeScoreEvent', 'clef', 'Bass clef', '\uE062', 'bass', { system: false });
assert.equal(await page.evaluate(() => window.__legatoOwner.clefAt(0, 0)), 'bass', 'clef change should be active at its position');

await setOwnerState({ pos: 1 });
await invoke('placeScoreEvent', 'key', 'G major key signature', '', 1, { system: true });
assert.equal(await page.evaluate(() => window.__legatoOwner.keyAt(1.5).name), 'G major', 'key event should be position-aware');

await setOwnerState({ pos: 2 });
await invoke('placeScoreEvent', 'meter', '3/4 time signature', '', '3/4', { system: true });
assert.equal(await page.evaluate(() => window.__legatoOwner.meterAt(2.25)), '3/4', 'meter event should be position-aware');

await setOwnerState({ pos: 2 });
await invoke('placeScoreEvent', 'tempo', '120 BPM', '', 120, { system: true });
assert.equal(Math.round(await page.evaluate(() => window.__legatoOwner.tempoAt(2.5))), 120, 'tempo event should be active after its point');
const seconds = await page.evaluate(() => window.__legatoOwner.secondsBetween(0, 4));
assert.ok(seconds > 1.9 && seconds < 2.5, 'tempo integration should use both tempo regions');

await setOwnerState({ pos: 1.5, staff: 0 });
await invoke('placeScoreEvent', 'dynamic', 'mf', '\uE52D', '\uE52D', { system: false });
assert.equal(await page.evaluate(() => window.__legatoOwner.effectiveScoreEvent('dynamic', 0, 2).name), 'mf', 'dynamic should apply from its exact position');

// Editable score text must save and close its keyboard cleanly.
await setOwnerState({ pos: 2.5, staff: 0 });
await invoke('placeScoreEvent', 'technique', 'Playing technique', '', 'pizz.', { system: false, text: 'pizz.' });
let snap = await snapshot();
const techniqueId = snap.events.find(item => item.type === 'technique').id;
await invoke('selectScoreObject', techniqueId);
await invoke('editSelectedScoreObject');
assert.equal(await page.evaluate(() => window.__legatoOwner.state.kb), 'scoreText', 'text object should open the score text keyboard field');
await setOwnerState({ scoreText: 'arco' });
await invoke('finishScoreObjectText');
assert.equal(await page.evaluate(id => window.__legatoOwner.scoreObjectById(id).text, techniqueId), 'arco', 'edited technique text should save');
assert.equal(await page.evaluate(() => window.__legatoOwner.state.kb), null, 'saving score text should close the keyboard');

// A two-point span must finish with controller A even if another overlay appears.
await setOwnerState({ pos: 0.5, staff: 0, step: 7 });
await invoke('beginScoreSpan', 'slur', 'Slur', '\uE1FD');
assert.ok((await snapshot()).draft, 'slur point one should create a draft');
await setOwnerState({ pos: 3, staff: 0, step: 10, tour: true });
const confirmResult = await invoke('dispatch', 'confirm', 'press');
assert.equal(confirmResult, true, 'controller A should call the span finisher');
snap = await snapshot();
assert.equal(snap.spans.length, 1, 'controller A should finish a saved slur span');
assert.equal(snap.spans[0].p1, 0.5);
assert.equal(snap.spans[0].p2, 3);
assert.equal(snap.draft, null, 'finished slur must clear point-two mode');
await setOwnerState({ tour: false });

await setOwnerState({ pos: 1, staff: 0, step: 5 });
await invoke('beginScoreSpan', 'pedal', 'Sustain pedal', '\uE650');
await setOwnerState({ pos: 4, staff: 0, step: 5 });
await invoke('finishScoreSpan');
assert.ok(await page.evaluate(() => window.__legatoOwner.activeScoreSpan('pedal', 0, 2.5)), 'pedal should be active between point one and point two');

await setOwnerState({ pos: 0, staff: 1, step: 6 });
await invoke('beginScoreSpan', 'hairpin-up', 'Crescendo', '\uE53E');
await setOwnerState({ pos: 2, staff: 1, step: 6 });
await invoke('finishScoreSpan');
assert.ok(await page.evaluate(() => window.__legatoOwner.activeScoreSpan('hairpin-up', 1, 1)), 'hairpin should be active inside its range');

// The command catalog must create a real two-point object rather than decorating one note.
const linesCategory = await page.evaluate(() => CAT.findIndex(category => category[0] === 'Lines'));
assert.ok(linesCategory >= 0, 'Lines category should exist');
await setOwnerState({ halo: true, haloCat: linesCategory, haloIdx: 1, pos: 5, staff: 0, spanDraft: null });
await invoke('haloApply');
assert.ok((await snapshot()).draft, 'choosing Slur in commands should set point one');
await invoke('cancelScoreSpan');

// Saved objects must be selectable, movable, editable, and deletable by controller.
snap = await snapshot();
const slurId = snap.spans.find(item => item.type === 'slur').id;
await invoke('selectScoreObject', slurId);
await invoke('moveScoreObject', 0.5, 0);
assert.equal(await page.evaluate(id => window.__legatoOwner.scoreObjectById(id).p1, slurId), 1, 'selected span should move');
await invoke('editSelectedScoreObject');
assert.ok((await snapshot()).draft, 'A/edit should reopen a span endpoint');
await setOwnerState({ pos: 4.5, staff: 0, step: 11 });
await invoke('finishScoreSpan');
assert.equal((await snapshot()).draft, null, 'edited span should leave no stale draft');
assert.equal(await page.evaluate(id => window.__legatoOwner.scoreObjectById(id).p2, slurId), 4.5, 'span endpoint should be replaceable');

const dynamicId = (await snapshot()).events.find(item => item.type === 'dynamic').id;
await invoke('selectScoreObject', dynamicId);
const beforeDelete = await page.evaluate(id => {
  const owner = window.__legatoOwner;
  return { selected: owner.state.scoreObjectId, draft: owner.state.spanDraft, exists: !!owner.scoreObjectById(id) };
}, dynamicId);
assert.deepEqual(beforeDelete, { selected: dynamicId, draft: null, exists: true }, 'dynamic should be the only active notation selection');
await setOwnerState({ tour: true });
await invoke('dispatch', 'delete', 'press');
assert.equal(await page.evaluate(() => window.__legatoOwner.state.scoreEvents.some(item => item.type === 'dynamic')), false, 'controller B should delete a selected point event before an overlay can intercept it');
await setOwnerState({ tour: false });

// Point events and spans must render and persist in project documents.
await page.waitForFunction(() => document.querySelectorAll('[data-score-object="true"]').length >= 5, null, { timeout: 10000 });
const rendered = await page.locator('[data-score-object="true"]').count();
assert.ok(rendered >= 5, 'point events and spans should render as score objects');
snap = await snapshot();
assert.ok(Array.isArray(snap.doc.scoreEvents) && Array.isArray(snap.doc.scoreSpans), 'events and spans should be saved in project documents');
assert.ok(snap.doc.scoreEvents.length >= 5 && snap.doc.scoreSpans.length >= 3, 'saved document should contain placed notation');

// MIDI must be structurally valid and use the new tempo/pitch path.
await page.evaluate(() => {
  const owner = window.__legatoOwner;
  owner.download = (name, mime, data) => {
    window.__midiCapture = { name, mime, length: data.length, head: Array.from(data.slice(0, 4)) };
  };
  owner.exportMidi();
});
await pause(90);
const midi = await page.evaluate(() => window.__midiCapture);
assert.ok(midi && midi.name.endsWith('.mid') && midi.length > 30, 'MIDI export should produce a non-empty file');
assert.deepEqual(midi.head, [77, 84, 104, 100], 'MIDI should begin with MThd');

// Removing a player must remove its objects and shift remaining ownership safely.
const lastStaff = await page.evaluate(() => window.__legatoOwner.state.players.length - 1);
await setOwnerState({ staff: lastStaff, pos: 1 });
await invoke('placeScoreEvent', 'technique', 'Last staff technique', '', 'mute', { system: false, text: 'mute' });
await setOwnerState({ pos: 1.5, staff: lastStaff });
await invoke('beginScoreSpan', 'pedal', 'Last staff pedal', '\uE650');
await setOwnerState({ pos: 2.5, staff: lastStaff });
await invoke('finishScoreSpan');
const playersBefore = await page.evaluate(() => window.__legatoOwner.state.players.length);
await invoke('removePlayer', lastStaff);
assert.equal(await page.evaluate(() => window.__legatoOwner.state.players.length), playersBefore - 1, 'player removal should complete');
assert.equal(await page.evaluate(() => {
  const owner = window.__legatoOwner;
  const max = owner.state.players.length - 1;
  return owner.state.scoreEvents.some(item => !item.system && item.s > max)
    || owner.state.scoreSpans.some(item => !item.system && (item.s1 > max || item.s2 > max));
}), false, 'removed-player notation must not become orphaned');

// Removing the last measure must remove or clip every object beyond the new end.
await setOwnerState({ bars: 4, staff: 0, pos: 15 });
await invoke('placeScoreEvent', 'text', 'late', '', 'late', { system: false, text: 'late' });
await setOwnerState({ pos: 14, staff: 0 });
await invoke('beginScoreSpan', 'line', 'Late line', '—');
await setOwnerState({ pos: 15.5, staff: 0 });
await invoke('finishScoreSpan');
await invoke('runOp', 'Remove last measure');
assert.equal(await page.evaluate(() => window.__legatoOwner.state.bars), 3, 'last measure should be removed');
assert.equal(await page.evaluate(() => {
  const owner = window.__legatoOwner;
  const end = owner.state.bars * owner.barCapacity();
  return owner.state.scoreEvents.some(item => item.p >= end)
    || owner.state.scoreSpans.some(item => item.p1 >= end || item.p2 >= end);
}), false, 'notation beyond the removed measure must be removed or clipped');

// Legacy recovery snapshots without notation arrays must reopen safely.
await page.evaluate(() => {
  const owner = window.__legatoOwner;
  localStorage.setItem('legato.recovery.v1', JSON.stringify({
    at: Date.now(),
    doc: { notes: [], title: 'Legacy score' }
  }));
  owner._loadedRecovery = false;
  owner.loadRecovery();
});
await pause(140);
assert.equal(await page.evaluate(() => window.__legatoOwner.state.title), 'Legacy score', 'legacy recovery should reopen its score');
assert.ok(await page.evaluate(() => Array.isArray(window.__legatoOwner.state.scoreEvents) && Array.isArray(window.__legatoOwner.state.scoreSpans)), 'legacy recovery should create empty notation arrays');

// A new project must be genuinely empty.
await invoke('newProject');
assert.equal(await page.evaluate(() => window.__legatoOwner.state.scoreEvents.length), 0, 'new project should clear point events');
assert.equal(await page.evaluate(() => window.__legatoOwner.state.scoreSpans.length), 0, 'new project should clear spans');

console.log('Live notation object checks passed', JSON.stringify({
  rendered,
  midiBytes: midi.length,
  controllerPriority: true,
  playerCleanup: true,
  measureCleanup: true,
  legacyRecovery: true
}));
await browser.close();
