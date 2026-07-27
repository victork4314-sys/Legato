import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 780 } });
await context.addInitScript(() => {
  try { localStorage.setItem('legato.tour.v1', '1'); } catch (_) {}
});
const page = await context.newPage();
await page.goto('http://127.0.0.1:4173/index.html', { waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => window.__legatoOwner && window.LEGATO_SMUFL_CATALOG && document.querySelector('[data-legato-root="true"]'), null, { timeout: 60000 });

const pause = ms => page.waitForTimeout(ms);
const setState = async patch => {
  await page.evaluate(value => new Promise(resolve => window.__legatoOwner.setState(value, resolve)), patch);
  await pause(60);
};

const catalogAudit = await page.evaluate(() => {
  const cat = window.LEGATO_SMUFL_CATALOG;
  const allowedPlacements = new Set(['note', 'event', 'span', 'structure']);
  const bad = cat.glyphs.filter(g => !g.id || !g.label || !g.range || !g.group || !allowedPlacements.has(g.placement) || !g.kind || (g.audible && !g.sound));
  const glyphGroups = Array.from(new Set(cat.glyphs.map(g => g.group)));
  const ranges = Array.from(new Set(cat.glyphs.map(g => g.range)));
  const audible = cat.glyphs.filter(g => g.audible);
  const specialist = cat.glyphs.filter(g => g.tier === 'specialist');
  return {
    glyphCount: cat.glyphCount,
    rangeCount: cat.rangeCount,
    declaredGroups: cat.groups || [],
    glyphGroups,
    ranges: ranges.length,
    audible: audible.length,
    specialist: specialist.length,
    bad: bad.slice(0, 5)
  };
});
assert.ok(catalogAudit.glyphCount > 2400, 'the complete library must contain the full SMuFL-scale glyph catalog');
assert.ok(catalogAudit.rangeCount > 100, 'the complete library must include all official SMuFL ranges');
assert.ok(catalogAudit.declaredGroups.includes('Popular'), 'the catalog must declare a Popular front layer');
assert.ok(catalogAudit.glyphGroups.includes('Specialist & optional'), 'specialist and optional notation must be separated but present');
assert.ok(catalogAudit.specialist > 100, 'specialist notation must not be a token handful');
assert.ok(catalogAudit.audible > 100, 'sound-affecting notation must have broad explicit playback coverage');
assert.deepEqual(catalogAudit.bad, [], 'every catalog entry must have a real placement route and every audible item a sound meaning');

await setState({
  tour: false, recovery: null, zone: 3, staff: 0, pos: 0, step: 6,
  halo: true, haloCat: 0, haloIdx: 0, panel: null, hub: false, menu: false,
  kb: null, picker: false, radial: false, scoreEvents: [], scoreSpans: [],
  scoreObjectId: null, spanDraft: null, selectedChordHead: null,
  notes: [{ id: 'n-main', s: 0, p: 0, d: 'q', step: 6, voice: 1, rest: false, chord: [2, 4] }],
  selId: 'n-main', measureMarks: {}
});

// The rendered Y library starts with Popular and expands to official ranges.
const renderedLibrary = await page.evaluate(() => {
  const categories = Array.from(document.querySelectorAll('[data-halo-category]')).map(el => (el.textContent || '').trim());
  return { count: categories.length, first: categories[0] || '', specialist: categories.some(x => /Specialist|Historical|Mensural|Chant/i.test(x)) };
});
assert.ok(renderedLibrary.count > 100, 'the Y library must expose expanded range categories, not a tiny curated list');
assert.ok(renderedLibrary.first.startsWith('Popular'), 'Popular must be first');
assert.equal(renderedLibrary.specialist, true, 'specialist ranges must be reachable in Y');

// A niche visual symbol must create a saved, selectable score event instead of a dead command.
const visualResult = await page.evaluate(async () => {
  const owner = window.__legatoOwner, cat = window.LEGATO_SMUFL_CATALOG;
  const item = cat.glyphs.find(g => g.tier === 'specialist' && g.placement === 'event' && !g.audible && g.glyph);
  if (!item) throw new Error('No specialist visual event was generated');
  await new Promise(resolve => owner.setState({ selId: null, halo: true }, () => {
    owner.applyCatalogCommand(item, item.label, item.glyph);
    setTimeout(resolve, 40);
  }));
  return { id: item.id, label: item.label };
});
await pause(100);
let state = await page.evaluate(() => window.__legatoOwner.state);
assert.ok(state.scoreEvents.some(e => e.smufl === visualResult.id), 'a specialist glyph must be saved as a real score object');
assert.ok(state.scoreObjectId, 'the newly placed specialist glyph must remain selected');

// A quarter-tone accidental stores cents and produces fractional live pitch.
const microResult = await page.evaluate(async () => {
  const owner = window.__legatoOwner, cat = window.LEGATO_SMUFL_CATALOG;
  const item = cat.glyphs.find(g => g.kind === 'accidental' && Math.abs(Number(g.cents)) === 50 && g.glyph);
  if (!item) throw new Error('No quarter-tone accidental was generated');
  await new Promise(resolve => owner.setState({ selId: 'n-main', scoreObjectId: null }, () => {
    owner.applyCatalogCommand(item, item.label, item.glyph);
    setTimeout(resolve, 40);
  }));
  return { id: item.id, cents: item.cents };
});
await pause(100);
const microPitch = await page.evaluate(() => {
  const owner = window.__legatoOwner, note = owner.state.notes.find(n => n.id === 'n-main');
  return { cents: note.accCents, smufl: note.accSmufl, midi: owner.noteMidi(note, owner.state) };
});
assert.equal(Math.abs(microPitch.cents), 50, 'quarter-tone cents must survive application');
assert.equal(microPitch.smufl, microResult.id, 'the exact accidental identity must survive');
assert.notEqual(microPitch.midi, Math.round(microPitch.midi), 'live playback pitch must remain fractional for microtones');

// Articulation playback profiles must audibly alter length/gain.
const articulationProfile = await page.evaluate(() => {
  const owner = window.__legatoOwner, cat = window.LEGATO_SMUFL_CATALOG;
  const item = cat.glyphs.find(g => g.kind === 'articulation' && g.profile === 'staccatissimo' && g.glyph);
  if (!item) throw new Error('No staccatissimo articulation was generated');
  const note = owner.state.notes.find(n => n.id === 'n-main');
  return owner.articulationPlayback(Object.assign({}, note, { artPlayback: item, art: item.glyph }));
});
assert.ok(articulationProfile.length < 0.4, 'staccatissimo must shorten the sounding note');

// Position-aware technique changes must become real events with playback semantics.
const techniqueResult = await page.evaluate(async () => {
  const owner = window.__legatoOwner, cat = window.LEGATO_SMUFL_CATALOG;
  const item = cat.glyphs.find(g => g.kind === 'technique' && g.placement === 'event' && /pizz/i.test((g.technique || '') + ' ' + g.label) && g.glyph);
  if (!item) throw new Error('No pizzicato technique event was generated');
  await new Promise(resolve => owner.setState({ selId: null, pos: 1 }, () => {
    owner.applyCatalogCommand(item, item.label, item.glyph);
    setTimeout(resolve, 40);
  }));
  return { id: item.id, technique: item.technique };
});
await pause(80);
state = await page.evaluate(() => window.__legatoOwner.state);
assert.ok(state.scoreEvents.some(e => e.smufl === techniqueResult.id && e.playback && e.playback.audible), 'pizzicato must be a saved audible technique event');

// Hairpins use point one/two and retain playback semantics.
const hairpinResult = await page.evaluate(async () => {
  const owner = window.__legatoOwner, cat = window.LEGATO_SMUFL_CATALOG;
  const item = cat.glyphs.find(g => g.kind === 'hairpin' && g.direction === 'up' && g.glyph);
  if (!item) throw new Error('No crescendo hairpin span was generated');
  await new Promise(resolve => owner.setState({ selId: null, pos: 0.5, staff: 0 }, () => {
    owner.applyCatalogCommand(item, item.label, item.glyph);
    setTimeout(resolve, 40);
  }));
  return { id: item.id };
});
await setState({ pos: 4.5, staff: 0 });
await page.evaluate(() => window.__legatoOwner.finishScoreSpan());
await pause(100);
state = await page.evaluate(() => window.__legatoOwner.state);
const hairpin = state.scoreSpans.find(s => s.smufl === hairpinResult.id);
assert.ok(hairpin && hairpin.playback && hairpin.playback.sound === 'hairpin', 'hairpin must retain audible span semantics');

// The logical selector reaches notes, rests, each chord head, events, whole spans and both handles.
const selectorKinds = await page.evaluate(async () => {
  const owner = window.__legatoOwner;
  await new Promise(resolve => owner.setState(s => ({ notes: s.notes.concat([{ id: 'r-one', s: 0, p: 2, d: 'q', step: 6, voice: 1, rest: true }]) }), resolve));
  const items = owner.scoreSelectableObjects();
  owner.openScoreObjectSelector();
  return { kinds: Array.from(new Set(items.map(x => x.kind))), count: items.length, chordHeads: items.filter(x => x.kind === 'chord-head').length };
});
await pause(100);
for (const kind of ['note','rest','chord-head','score-event','score-span','span-start','span-end']) assert.ok(selectorKinds.kinds.includes(kind), 'selector must include ' + kind);
assert.ok(selectorKinds.chordHeads >= 3, 'every chord head must be separately selectable');
state = await page.evaluate(() => window.__legatoOwner.state);
assert.equal(state.panel, 'score-object-selector', 'SELECT must open the dedicated logical score selector');

// Select and move one chord head without pixel hunting.
const chordMove = await page.evaluate(async () => {
  const owner = window.__legatoOwner;
  const item = owner.scoreSelectableObjects().find(x => x.kind === 'chord-head' && x.headIndex === 1);
  if (!item) throw new Error('No second chord head was selectable');
  const before = owner.chordHeadSteps(owner.state.notes.find(n => n.id === item.noteId));
  owner.selectLogicalScoreObject(item);
  await new Promise(resolve => setTimeout(resolve, 50));
  owner.moveSelectedChordHead(1);
  await new Promise(resolve => setTimeout(resolve, 50));
  const after = owner.chordHeadSteps(owner.state.notes.find(n => n.id === item.noteId));
  return { before, after, selected: owner.state.selectedChordHead };
});
assert.notDeepEqual(chordMove.after, chordMove.before, 'an individually selected chord head must move independently');
assert.ok(chordMove.selected, 'the moved chord head must remain selected');

console.log('Complete SMuFL library checks passed', JSON.stringify({ catalogAudit, renderedLibrary, selectorKinds, microPitch, articulationProfile }));
await browser.close();
