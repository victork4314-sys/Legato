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
  window.__setBothBumpers = pressed => {
    [4, 5].forEach(index => {
      buttons[index].pressed = pressed;
      buttons[index].value = pressed ? 1 : 0;
    });
    pad.timestamp = performance.now();
  };
});

const page = await context.newPage();
await page.goto('http://127.0.0.1:4173/index.html', { waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => window.__legatoOwner && document.querySelector('[data-legato-root="true"]'), null, { timeout: 30000 });

const setButton = async (index, pressed) => {
  await page.evaluate(([i, p]) => window.__setPadButton(i, p), [index, pressed]);
};
const snapshot = async label => {
  const state = await page.evaluate(() => {
    const owner = window.__legatoOwner;
    const selected = owner.selected();
    return {
      zone: owner.state.zone,
      selId: owner.state.selId,
      accidental: selected ? selected.acc ?? null : 'NO_SELECTION',
      comboLatched: !!owner._bumperCombo,
      pending4: owner._bumperPending && owner._bumperPending[4] ? { ...owner._bumperPending[4] } : null,
      pending5: owner._bumperPending && owner._bumperPending[5] ? { ...owner._bumperPending[5] } : null,
      previous: owner._prev ? owner._prev.slice(4, 6) : null,
      spoken: owner.state.spoken
    };
  });
  console.log(label, JSON.stringify(state));
  return state;
};
const combo = async () => {
  await page.evaluate(() => window.__setBothBumpers(true));
  await page.waitForTimeout(90);
  await page.evaluate(() => window.__setBothBumpers(false));
  await page.waitForTimeout(220);
};
const single = async (index, hold = 220) => {
  await setButton(index, true);
  await page.waitForTimeout(hold);
  await setButton(index, false);
  await page.waitForTimeout(140);
};

await page.evaluate(() => {
  const owner = window.__legatoOwner;
  owner.setState({ zone: 2, focus: 0, scoreHint: false });
  requestAnimationFrame(() => owner.syncGlobalSelection());
});
await page.waitForTimeout(120);

await combo();
assert.equal(await page.evaluate(() => window.__legatoOwner.state.zone), 3, 'LB+RB should enter the score');
assert.equal(await page.evaluate(() => window.__legatoOwner.state.scoreHint), true, 'entry hint should show immediately');
await page.waitForTimeout(1600);
assert.equal(await page.evaluate(() => window.__legatoOwner.state.scoreHint), false, 'entry hint should fade');

await page.evaluate(() => {
  const owner = window.__legatoOwner;
  owner.selectNote(owner.state.notes[0]);
});
await page.waitForTimeout(160);
assert.ok(await page.evaluate(() => window.__legatoOwner.selected()), 'test note should be selected');
await page.evaluate(() => window.__legatoOwner.editNote({ acc: null }, 'reset accidental for test'));
await page.waitForTimeout(80);
await snapshot('before LB');
await single(4);
await snapshot('after LB');
const flatValue = await page.evaluate(() => window.__legatoOwner.selected().acc);
assert.ok(flatValue, 'LB alone should still apply an accidental');
assert.equal(await page.evaluate(() => window.__legatoOwner.state.zone), 3, 'LB alone should not leave the score');

await page.evaluate(() => window.__legatoOwner.editNote({ acc: null }, 'reset accidental for test'));
await page.waitForTimeout(80);
await snapshot('before RB');
await single(5);
await snapshot('after RB');
const sharpValue = await page.evaluate(() => window.__legatoOwner.selected().acc);
assert.ok(sharpValue, 'RB alone should still apply an accidental');
assert.notEqual(sharpValue, flatValue, 'LB and RB should apply different accidentals');

await page.evaluate(() => window.__legatoOwner.editNote({ acc: null }, 'reset accidental for combo test'));
await page.waitForTimeout(80);
await combo();
assert.equal(await page.evaluate(() => window.__legatoOwner.state.zone), 2, 'second LB+RB should leave the score');
assert.equal(await page.evaluate(() => window.__legatoOwner.selected().acc), null, 'LB+RB should not apply either accidental');

await combo();
assert.equal(await page.evaluate(() => window.__legatoOwner.state.zone), 3, 'LB+RB should return to the score from the interface');
await combo();
assert.equal(await page.evaluate(() => window.__legatoOwner.state.zone), 2, 'LB+RB should return to the prior interface zone');

console.log('Browser bumper toggle checks passed');
await browser.close();
