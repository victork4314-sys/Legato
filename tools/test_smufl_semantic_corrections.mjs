import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
await context.addInitScript(() => {
  try { localStorage.setItem('legato.tour.v1', '1'); } catch (_) {}
});
const page = await context.newPage();
await page.goto('http://127.0.0.1:4173/index.html', { waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => window.__legatoOwner && window.LEGATO_SMUFL_CATALOG && document.querySelector('[data-legato-root="true"]'), null, { timeout: 60000 });

const pause = ms => page.waitForTimeout(ms);
const setState = async patch => {
  await page.evaluate(value => new Promise(resolve => window.__legatoOwner.setState(value, resolve)), patch);
  await pause(50);
};

const audit = await page.evaluate(() => {
  const data = window.LEGATO_SMUFL_CATALOG;
  const byId = Object.fromEntries(data.glyphs.map(g => [g.id, g]));
  const controlsSounding = data.glyphs.filter(g => g.audible && /^(control|text)/.test(g.id));
  const graceAsTrill = data.glyphs.filter(g => g.kind === 'grace' && /trill|shake/.test(String(g.pattern || '')));
  const clusterHarmonics = data.glyphs.filter(g => /cluster/i.test(g.id + ' ' + g.label) && g.sound === 'harmonic');
  const audibleKinds = new Set(['dynamic','hold','grace','ornament','tremolo','pitch-effect','articulation','technique','bowing','percussion','electronic','hairpin']);
  const silentPerformanceKinds = data.glyphs.filter(g => audibleKinds.has(g.kind) && !g.audible);
  const techniqueRanges = /string techniques|wind techniques|brass techniques|guitar techniques|vocal techniques|handbells|percussion playing technique|beater pictograms/i;
  const visual = /component|combining|stem$|left$|right$|up$|down$|parenthes|bracket|placeholder|control/i;
  const silentTechniqueRange = data.glyphs.filter(g => techniqueRanges.test(g.range) && !g.audible && !visual.test(g.id + ' ' + g.label));
  return {
    glyphCount: data.glyphCount,
    rangeCount: data.rangeCount,
    controlsSounding: controlsSounding.slice(0, 10),
    graceAsTrill: graceAsTrill.slice(0, 10),
    clusterHarmonics: clusterHarmonics.slice(0, 10),
    silentPerformanceKinds: silentPerformanceKinds.slice(0, 10),
    silentTechniqueRange: silentTechniqueRange.slice(0, 10),
    checks: {
      controlBeginBeam: byId.controlBeginBeam,
      graceAcciaccatura: byId.graceNoteAcciaccaturaStemUp,
      graceSlash: byId.graceNoteSlashStemUp,
      breathComma: byId.breathMarkComma,
      forte: byId.dynamicForte,
      piano: byId.dynamicPiano,
      cluster: byId.noteheadDiamondClusterBlackBottom,
      harmonOpen: byId.brassHarmonMuteStemOpen,
      harmonClosed: byId.brassHarmonMuteStemClosed,
      bowChange: byId.stringsChangeBowDirectionImposed,
      electronicMute: data.glyphs.find(g => g.kind === 'electronic' && g.electronic === 'mute'),
      electronicUnmute: data.glyphs.find(g => g.kind === 'electronic' && g.electronic === 'unmute'),
      pedalOn: data.glyphs.find(g => g.kind === 'pedal' && g.placement === 'event' && g.state === 'on'),
      pedalOff: data.glyphs.find(g => g.kind === 'pedal' && g.placement === 'event' && g.state === 'off'),
      octaveClef: data.glyphs.find(g => g.kind === 'clef' && Number(g.semitones) === 12),
      harmonicHead: data.glyphs.find(g => g.kind === 'notehead' && g.sound === 'harmonic' && g.glyph),
      quarterTone: data.glyphs.find(g => g.kind === 'accidental' && Math.abs(Number(g.cents)) === 50 && g.glyph),
      specialistTechnique: data.glyphs.find(g => g.kind === 'technique' && g.audible && g.tier === 'specialist')
    }
  };
});

assert.equal(audit.glyphCount, 3451, 'the complete catalog must remain intact');
assert.equal(audit.rangeCount, 131, 'all official ranges must remain intact');
assert.deepEqual(audit.controlsSounding, [], 'font control/text glyphs must not make sound');
assert.deepEqual(audit.graceAsTrill, [], 'grace notes must not be realised as trills');
assert.deepEqual(audit.clusterHarmonics, [], 'cluster diamonds must not become harmonics');
assert.deepEqual(audit.silentPerformanceKinds, [], 'every explicitly performance-bearing semantic kind must be audible');
assert.deepEqual(audit.silentTechniqueRange, [], 'dedicated performance-technique ranges must not contain silent real techniques');
assert.equal(audit.checks.controlBeginBeam.audible, false);
assert.equal(audit.checks.graceAcciaccatura.kind, 'grace');
assert.equal(audit.checks.graceAcciaccatura.pattern, 'acciaccatura');
assert.equal(audit.checks.graceSlash.audible, false);
assert.equal(audit.checks.breathComma.sound, 'breath');
assert.equal(audit.checks.forte.velocity, 94);
assert.equal(audit.checks.piano.velocity, 52);
assert.notEqual(audit.checks.cluster.sound, 'harmonic');
assert.equal(audit.checks.harmonOpen.technique, 'harmon-open');
assert.equal(audit.checks.harmonClosed.technique, 'harmon-closed');
assert.equal(audit.checks.bowChange.audible, true);
for (const required of ['electronicMute','electronicUnmute','pedalOn','pedalOff','octaveClef','harmonicHead','quarterTone','specialistTechnique']) {
  assert.ok(audit.checks[required], required + ' semantic example must exist');
}

await setState({
  tour: false, recovery: null, zone: 3, staff: 0, pos: 0, step: 6,
  panel: null, halo: false, hub: false, menu: false, kb: null, picker: false,
  notes: [{ id: 'n0', s: 0, p: 0, d: 'q', step: 6, voice: 1, rest: false, chord: [] }],
  scoreEvents: [], scoreSpans: [], measureMarks: {}, selId: 'n0', scoreObjectId: null,
  selectedChordHead: null, spanDraft: null, bars: 4, tempo: 100, playing: false,
  instruments: ['violin','violin','violin','acoustic_grand_piano']
});

const applied = await page.evaluate(async checks => {
  const owner = window.__legatoOwner;
  const cat = window.LEGATO_SMUFL_CATALOG.glyphs;
  const byId = Object.fromEntries(cat.map(g => [g.id, g]));
  const apply = item => new Promise(resolve => owner.applyCatalogCommand(item, item.label, item.glyph) || setTimeout(resolve, 50));

  owner.setState({ selId: 'n0', pos: 0 });
  owner.applyCatalogCommand(byId.graceNoteAcciaccaturaStemUp, byId.graceNoteAcciaccaturaStemUp.label, byId.graceNoteAcciaccaturaStemUp.glyph);
  await new Promise(r => setTimeout(r, 80));
  const graceNote = owner.state.notes.find(n => n.id === 'n0');

  owner.setState({ selId: null, pos: 0 });
  owner.applyCatalogCommand(byId.dynamicForte, byId.dynamicForte.label, byId.dynamicForte.glyph);
  await new Promise(r => setTimeout(r, 60));
  owner.setState({ pos: 1 });
  owner.applyCatalogCommand(byId.breathMarkComma, byId.breathMarkComma.label, byId.breathMarkComma.glyph);
  await new Promise(r => setTimeout(r, 60));

  const octave = cat.find(g => g.kind === 'clef' && Number(g.semitones) === 12);
  const baseNote = owner.state.notes.find(n => n.id === 'n0');
  const beforeOctave = owner.noteMidi(baseNote, owner.state);
  owner.setState({ pos: 0 });
  owner.applyCatalogCommand(octave, octave.label, octave.glyph);
  await new Promise(r => setTimeout(r, 60));
  const afterOctave = owner.noteMidi(owner.state.notes.find(n => n.id === 'n0'), owner.state);

  owner.setState({ selId: 'n0', pos: 0 });
  const harmonic = cat.find(g => g.kind === 'notehead' && g.sound === 'harmonic' && g.glyph);
  owner.applyCatalogCommand(harmonic, harmonic.label, harmonic.glyph);
  await new Promise(r => setTimeout(r, 60));
  const harmonicNote = owner.state.notes.find(n => n.id === 'n0');
  const harmonicMidi = owner.noteMidi(harmonicNote, owner.state);

  const quarter = cat.find(g => g.kind === 'accidental' && Math.abs(Number(g.cents)) === 50 && g.glyph);
  owner.applyCatalogCommand(quarter, quarter.label, quarter.glyph);
  await new Promise(r => setTimeout(r, 60));
  const microNote = owner.state.notes.find(n => n.id === 'n0');

  const pedalOn = cat.find(g => g.kind === 'pedal' && g.placement === 'event' && g.state === 'on');
  const pedalOff = cat.find(g => g.kind === 'pedal' && g.placement === 'event' && g.state === 'off');
  owner.setState({ selId: null, pos: 0 }); owner.applyCatalogCommand(pedalOn, pedalOn.label, pedalOn.glyph);
  await new Promise(r => setTimeout(r, 50));
  owner.setState({ pos: 2 }); owner.applyCatalogCommand(pedalOff, pedalOff.label, pedalOff.glyph);
  await new Promise(r => setTimeout(r, 50));

  const mute = cat.find(g => g.kind === 'electronic' && g.electronic === 'mute');
  const unmute = cat.find(g => g.kind === 'electronic' && g.electronic === 'unmute');
  owner.setState({ pos: 0 }); owner.applyCatalogCommand(mute, mute.label, mute.glyph);
  await new Promise(r => setTimeout(r, 50));
  owner.setState({ pos: 3 }); owner.applyCatalogCommand(unmute, unmute.label, unmute.glyph);
  await new Promise(r => setTimeout(r, 50));

  return {
    grace: graceNote.ornPlayback,
    forte: owner.state.scoreEvents.find(e => e.smufl === 'dynamicForte'),
    breath: owner.state.scoreEvents.find(e => e.smufl === 'breathMarkComma'),
    octaveDifference: afterOctave - beforeOctave,
    harmonicDifference: harmonicMidi - afterOctave,
    microMidi: owner.noteMidi(microNote, owner.state),
    microCents: microNote.accCents,
    pedalAt1: owner.activePedalEvent(0, 1, owner.state),
    pedalAt3: owner.activePedalEvent(0, 3, owner.state),
    release: owner.nextPedalRelease(0, 0, owner.state),
    electronicAt1: owner.activeElectronic(1, owner.state),
    electronicAt3: owner.activeElectronic(3, owner.state),
    harmonOpenProfile: owner.techniquePlaybackProfile(0, 0, { techniquePlayback: checks.harmonOpen }, owner.state),
    harmonClosedProfile: owner.techniquePlaybackProfile(0, 0, { techniquePlayback: checks.harmonClosed }, owner.state),
    specialistProfile: owner.techniquePlaybackProfile(0, 0, { techniquePlayback: checks.specialistTechnique }, owner.state)
  };
}, audit.checks);

assert.equal(applied.grace.kind, 'grace');
assert.equal(applied.grace.pattern, 'acciaccatura');
assert.equal(applied.forte.playback.velocity, 94);
assert.equal(applied.breath.playback.sound, 'breath');
assert.equal(applied.octaveDifference, 12, 'octave clef must transpose playback by one octave');
assert.equal(applied.harmonicDifference, 12, 'harmonic notehead must use the audible harmonic default');
assert.equal(Math.abs(applied.microCents), 50);
assert.notEqual(applied.microMidi, Math.round(applied.microMidi));
assert.equal(applied.pedalAt1.playback.state, 'on');
assert.equal(applied.pedalAt3.playback.state, 'off');
assert.equal(applied.release, 2);
assert.equal(applied.electronicAt1.playback.electronic, 'mute');
assert.equal(applied.electronicAt3.playback.electronic, 'unmute');
assert.notDeepEqual(applied.harmonOpenProfile, applied.harmonClosedProfile, 'open and closed Harmon mute must differ');
assert.notDeepEqual(applied.specialistProfile, { length: 1, gain: 1 }, 'specialist techniques must audibly change playback');

// Capture real scheduler output for dynamics, pedal sustain, and electronic mute.
const scheduled = await page.evaluate(async () => {
  const owner = window.__legatoOwner;
  const cat = window.LEGATO_SMUFL_CATALOG.glyphs;
  const forte = cat.find(g => g.id === 'dynamicForte');
  const piano = cat.find(g => g.id === 'dynamicPiano');
  const pedalOn = cat.find(g => g.kind === 'pedal' && g.placement === 'event' && g.state === 'on');
  const pedalOff = cat.find(g => g.kind === 'pedal' && g.placement === 'event' && g.state === 'off');
  const mute = cat.find(g => g.kind === 'electronic' && g.electronic === 'mute');
  const unmute = cat.find(g => g.kind === 'electronic' && g.electronic === 'unmute');

  const run = async scoreEvents => {
    await new Promise(resolve => owner.setState({
      notes: [{ id: 'sched', s: 0, p: 0, d: 'q', step: 6, voice: 1, rest: false, chord: [] }],
      scoreEvents, scoreSpans: [], bars: 4, tempo: 100, playing: true, loop: false,
      instruments: ['violin','violin','violin','acoustic_grand_piano']
    }, resolve));
    const captured = [];
    const oldPlayTone = owner.playTone, oldRealise = owner.realise, oldAc = owner._ac;
    owner.playTone = (midi, when, dur, staff, vel) => captured.push({ midi, when, dur, staff, vel });
    owner.realise = () => {};
    owner._ac = { currentTime: .05 };
    owner._t0 = 0; owner._b0 = 0; owner._fired = {}; owner._clicked = {}; owner._order = null;
    owner.schedule();
    owner.playTone = oldPlayTone; owner.realise = oldRealise; owner._ac = oldAc;
    return captured;
  };

  const event = (type, id, playback, p=0) => ({ id, object:'event', type, name:id, glyph:'x', value:'x', s:0, p, step:6, system:type==='electronic', smufl:id, playback });
  const f = await run([event('dynamic','dynamicForte',forte.playback || forte)]);
  const p = await run([event('dynamic','dynamicPiano',piano.playback || piano)]);
  const pedal = await run([
    event('pedal-event','ped-on',pedalOn,0),
    event('pedal-event','ped-off',pedalOff,2)
  ]);
  const muted = await run([event('electronic','mute',mute,0)]);
  const unmuted = await run([event('electronic','mute',mute,0), event('electronic','unmute',unmute,0)]);
  return { forte:f, piano:p, pedal, muted, unmuted };
});

assert.ok(scheduled.forte.length > 0 && scheduled.piano.length > 0);
assert.ok(scheduled.forte[0].vel > scheduled.piano[0].vel, 'forte must schedule louder than piano');
assert.ok(scheduled.pedal[0].dur > scheduled.forte[0].dur, 'pedal-down/up events must lengthen the scheduled note');
assert.equal(scheduled.muted.length, 0, 'electronic mute must suppress scheduled sound');
assert.ok(scheduled.unmuted.length > 0, 'a later unmute must restore scheduled sound');

// Grace realisation should add one grace gesture rather than a repeated trill.
const graceCapture = await page.evaluate(() => {
  const owner = window.__legatoOwner;
  const grace = window.LEGATO_SMUFL_CATALOG.glyphs.find(g => g.id === 'graceNoteAcciaccaturaStemUp');
  const note = { id:'g', s:0, p:0, d:'q', step:6, voice:1, rest:false, orn:grace.glyph, ornPlayback:grace, chord:[] };
  const captured = [];
  const oldPlayTone = owner.playTone, oldAudio = owner.audio;
  owner.playTone = (midi, when, dur) => captured.push({midi,when,dur});
  owner.audio = () => ({ currentTime: 0 });
  owner.realise(note, 60, .2, .6, 90);
  owner.playTone = oldPlayTone; owner.audio = oldAudio;
  return captured;
});
assert.equal(graceCapture.length, 1, 'acciaccatura must add one grace attack, not a trill stream');

// The logical selector and controller safeguards remain intact.
const selector = await page.evaluate(async () => {
  const owner = window.__legatoOwner;
  await new Promise(resolve => owner.setState({
    notes: [{ id:'ch',s:0,p:0,d:'q',step:6,voice:1,rest:false,chord:[2,4] }, {id:'r',s:0,p:1,d:'q',step:6,voice:1,rest:true}],
    scoreEvents: owner.state.scoreEvents, scoreSpans: [{id:'sp',object:'span',type:'slur',name:'Slur',s1:0,p1:0,step1:6,s2:0,p2:2,step2:8}],
    selectedChordHead:null
  }, resolve));
  const items = owner.scoreSelectableObjects();
  return { kinds:[...new Set(items.map(x=>x.kind))], heads:items.filter(x=>x.kind==='chord-head').length };
});
for (const kind of ['note','rest','chord-head','score-event','score-span','span-start','span-end']) assert.ok(selector.kinds.includes(kind), 'selector must retain ' + kind);
assert.ok(selector.heads >= 3);

console.log('SMuFL semantic correction checks passed', JSON.stringify({ audit, applied, scheduled, graceCapture, selector }));
await browser.close();
