import { chromium } from 'playwright';
import assert from 'node:assert/strict';

// Test the rendered Y command list exactly as a controller user sees it.
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1024, height: 640 } });
await context.addInitScript(() => {
  try { localStorage.setItem('legato.tour.v1', '1'); } catch (_) {}
});
const page = await context.newPage();
await page.goto('http://127.0.0.1:4173/index.html', { waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => window.__legatoOwner && document.querySelector('[data-legato-root="true"]'), null, { timeout: 30000 });

const pause = ms => page.waitForTimeout(ms);
const setState = async patch => {
  await page.evaluate(value => window.__legatoOwner.setState(value), patch);
  await pause(80);
};

await setState({
  tour: false, recovery: null, zone: 3, staff: 0, pos: 0, step: 6,
  halo: true, haloCat: 4, haloIdx: 0, panel: null, hub: false, menu: false,
  kb: null, picker: false, radial: false, scoreEvents: [], scoreSpans: [],
  scoreObjectId: null, spanDraft: null, selId: null
});

const categoryIndex = async name => {
  const labels = await page.locator('[data-halo-category]').allTextContents();
  const index = labels.findIndex(label => label.trim().startsWith(name));
  assert.ok(index >= 0, name + ' category should be rendered in the Y command list');
  return index;
};
const commandNames = async index => {
  await setState({ halo: true, haloCat: index, haloIdx: 0 });
  return (await page.locator('[data-halo-item]').allTextContents()).map(label => label.trim());
};

// Newly added point and span workflows must be visibly reachable in Y.
const textCategory = await categoryIndex('Text');
const structureCategory = await categoryIndex('Structure');
const linesCategory = await categoryIndex('Lines');
assert.ok((await commandNames(textCategory)).some(name => name.includes('Tempo change')), 'Tempo change must be visible in Y');
const structureNames = await commandNames(structureCategory);
assert.ok(structureNames.some(name => name.includes('Key signature change')), 'Key signature change must be visible in Y');
assert.ok(structureNames.some(name => name.includes('Time signature change')), 'Time signature change must be visible in Y');
assert.ok((await commandNames(linesCategory)).some(name => name.includes('Horizontal line')), 'Horizontal line must be visible in Y');

// Move through the long Ornaments list with controller-style navigation.
const ornaments = await categoryIndex('Ornaments');
await setState({ halo: true, haloCat: ornaments, haloIdx: 0 });
for (let i = 0; i < 13; i++) {
  await page.evaluate(() => window.__legatoOwner.haloMove(0, 1));
  await pause(35);
}
const scrollCheck = await page.evaluate(() => {
  const owner = window.__legatoOwner;
  const item = document.querySelector('[data-halo-item="' + owner.state.haloIdx + '"]');
  const scroller = document.querySelector('[data-scroll="halo"]');
  if (!item || !scroller) return null;
  const a = item.getBoundingClientRect(), b = scroller.getBoundingClientRect();
  return {
    index: owner.state.haloIdx,
    visible: a.top >= b.top - 1 && a.bottom <= b.bottom + 1,
    scrollTop: scroller.scrollTop
  };
});
assert.ok(scrollCheck && scrollCheck.index >= 45, 'controller navigation should reach the bottom of a long command category');
assert.equal(scrollCheck.visible, true, 'the selected command must scroll into view');
assert.ok(scrollCheck.scrollTop > 0, 'the command panel must actually scroll at compact screen height');

// A clicked tile must apply itself, not the previously selected command.
const dynamics = await categoryIndex('Dynamics');
await setState({ halo: true, haloCat: dynamics, haloIdx: 0, pos: 0.5, staff: 0, step: 7, spanDraft: null });
const crescendoTile = page.locator('[data-halo-item]').filter({ hasText: 'Crescendo' }).first();
await crescendoTile.click();
await pause(100);
let state = await page.evaluate(() => ({ draft: window.__legatoOwner.state.spanDraft, halo: window.__legatoOwner.state.halo }));
assert.ok(state.draft, 'Crescendo should begin a two-point span');
assert.equal(state.draft.type, 'hairpin-up', 'clicking Crescendo must apply Crescendo itself');
assert.equal(state.halo, false, 'the command list should close after setting point one');

// Extend it: only horizontal length may grow; the opening stays a normal fixed size.
await setState({ pos: 8.5, staff: 0, step: 7 });
await page.evaluate(() => window.__legatoOwner.finishScoreSpan());
await pause(120);
state = await page.evaluate(() => ({ spans: window.__legatoOwner.state.scoreSpans, selected: window.__legatoOwner.state.scoreObjectId }));
assert.equal(state.spans.length, 1, 'the crescendo should save');
const hairpinId = state.spans[0].id;

const hairpin = page.locator('[data-score-object="true"][data-ptr^="Crescendo"]').first();
await hairpin.waitFor({ state: 'visible' });
const geometry = await hairpin.evaluate(element => {
  const lines = element.children;
  const wrap = element.getBoundingClientRect();
  const outer = lines[0].getBoundingClientRect();
  const inner = lines[1].getBoundingClientRect();
  const style = getComputedStyle(lines[0]);
  return {
    width: wrap.width,
    hitHeight: wrap.height,
    outerHeight: outer.height,
    innerHeight: inner.height,
    clipPath: style.clipPath
  };
});
assert.ok(geometry.width > 250, 'the test crescendo should be long');
assert.ok(geometry.outerHeight <= 18 && geometry.innerHeight <= 18, 'extending a crescendo must not make it vertically fat');
assert.ok(geometry.hitHeight >= 28 && geometry.hitHeight <= 32, 'the invisible selection area should be easy to hit but not page-sized');
assert.notEqual(geometry.clipPath, 'none', 'hairpins should use fixed-opening triangular geometry');

// A saved object click must survive the underlying staff click layer.
await setState({ scoreObjectId: null, selId: null });
await hairpin.click({ position: { x: Math.max(8, geometry.width * 0.7), y: geometry.hitHeight / 2 } });
await pause(120);
const selected = await page.evaluate(() => window.__legatoOwner.state.scoreObjectId);
assert.equal(selected, hairpinId, 'clicking the saved crescendo should keep it selected');

console.log('Command list and hairpin checks passed', JSON.stringify({ scrollCheck, geometry, selected }));
await browser.close();
