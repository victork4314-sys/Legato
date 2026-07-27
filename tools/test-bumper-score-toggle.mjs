import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
await context.addInitScript(() => {
  const buttons = Array.from({ length: 16 }, () => ({ pressed: false, value: 0 }));
  const pad = { connected: true, buttons, axes: [0, 0, 0, 0], id: 'Legato test pad', index: 0, mapping: 'standard', timestamp: 0 };
  Object.defineProperty(navigator, 'getGamepads', { configurable: true, value: () => [pad] });
  window.__setPadButton = (index, pressed) => {
    buttons[index].pressed = pressed;
    buttons[index].value = pressed ? 1 : 0;
    pad.timestamp = performance.now();
  };
});

const page = await context.newPage();
await page.goto('http://127.0.0.1:4173/index.html', { waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => window.__legatoOwner && document.querySelector('[data-legato-root="true"]'), null, { timeout: 30000 });

const setButton = async (index, pressed) => {
  await page.evaluate(([i, p]) => window.__setPadButton(i, p), [index, pressed]);
};
const combo = async () => {
  await setButton(4, true);
  await setButton(5, true);
  await page.waitForTimeout(70);
  await setButton(4, false);
  await setButton(5, false);
  await page.waitForTimeout(100);
};
const single = async index => {
  await setButton(index, true);
  await page.waitForTimeout(180);
  await setButton(index, false);
  await page.waitForTimeout(80);
};

await page.evaluate(() => {
  const owner = window.__legatoOwner;
  owner.setState({ zone: 2, focus: 0, scoreHint: false });
  requestAnimationFrame(() => owner.syncGlobalSelection());
});
await page.waitForTimeout(100);

await combo();
assert.equal(await page.evaluate(() => window.__legatoOwner.state.zone), 3, 'LB+RB should enter the score');
assert.equal(await page.evaluate(() => window.__legatoOwner.state.scoreHint), true, 'entry hint should show immediately');
await page.waitForTimeout(1600);
assert.equal(await page.evaluate(() => window.__legatoOwner.state.scoreHint), false, 'entry hint should fade');

await page.evaluate(() => {
  const owner = window.__legatoOwner;
  const note = owner.state.notes[0];
  owner.selectNote(note);
  owner.editNote({ acc: null }, 'reset accidental for test');
});
await page.waitForTimeout(80);
await single(4);
const flatValue = await page.evaluate(() => window.__legatoOwner.selected().acc);
assert.ok(flatValue, 'LB alone should still apply an accidental');
assert.equal(await page.evaluate(() => window.__legatoOwner.state.zone), 3, 'LB alone should not leave the score');

await page.evaluate(() => window.__legatoOwner.editNote({ acc: null }, 'reset accidental for test'));
await single(5);
const sharpValue = await page.evaluate(() => window.__legatoOwner.selected().acc);
assert.ok(sharpValue, 'RB alone should still apply an accidental');
assert.notEqual(sharpValue, flatValue, 'LB and RB should apply different accidentals');

await page.evaluate(() => window.__legatoOwner.editNote({ acc: null }, 'reset accidental for combo test'));
await combo();
assert.equal(await page.evaluate(() => window.__legatoOwner.state.zone), 2, 'second LB+RB should leave the score');
assert.equal(await page.evaluate(() => window.__legatoOwner.selected().acc), null, 'LB+RB should not apply either accidental');

await combo();
assert.equal(await page.evaluate(() => window.__legatoOwner.state.zone), 3, 'LB+RB should return to the score from the interface');
await combo();
assert.equal(await page.evaluate(() => window.__legatoOwner.state.zone), 2, 'LB+RB should return to the prior interface zone');

console.log('Browser bumper toggle checks passed');
await browser.close();
