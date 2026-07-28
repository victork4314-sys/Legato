# Legato

**Legato is a controller-first, browser-based music notation, engraving, playback, rehearsal, and accessibility studio.**

It is designed around direct score work on iPad and desktop browsers, with an Xbox-style controller as a primary input method rather than an afterthought. The interface is original to Legato: it is not intended to copy another notation program’s visual design, mode system, panels, terminology, or workflow.

## Open Legato

**Live web app:** [victork4314-sys.github.io/Legato](https://victork4314-sys.github.io/Legato/)

Legato is currently developed primarily for:

1. iPad and current iPadOS Safari.
2. macOS and current Safari.
3. iPhone and other iOS devices as secondary targets.

Other modern browsers may work, but controller behavior, browser audio, storage, and layout can differ between platforms.

## Start here

The full guided walkthrough is in **[TUTORIAL.md](TUTORIAL.md)**.

The tutorial covers:

- Connecting and navigating with a controller.
- Adding players and selecting instruments.
- Entering notes, rests, chords, and multiple voices.
- Using durations, accidentals, staffs, and cursor steps.
- Opening the complete notation catalog with **Y** or **MUSIC**.
- Placing, stacking, moving, flipping, selecting, and deleting symbols individually.
- Slurs, ties, dynamics, articulations, ornaments, grace marks, noteheads, percussion, and structural symbols.
- Playback, repeats, codas, segnos, browser audio, saving, and troubleshooting.

## Core goals

Legato is built around a few non-negotiable principles.

### Complete controller access

Every visible and interactive area must be reachable without requiring a mouse or keyboard. Directional navigation should follow the physical layout of the program and must not trap the user inside one list, panel, toolbar, or score region.

The live **Controller map** changes by layer and context. It is the authoritative description of the controls currently available.

### Music-theory correctness

Notation must behave according to its musical role rather than being treated as decorative text.

Examples:

- Accidentals belong to notes.
- Chord tones share a rhythmic position and use correct stem behavior.
- Slurs and phrase marks can curve above or below.
- Ties connect matching pitches rather than acting as generic curves.
- Notehead commands replace a notehead role instead of covering the original note with a loose glyph.
- Articulations, dynamics, ornaments, holds, techniques, and tremolos attach to the affected event.
- Codas, segnos, repeats, and related symbols are structural score objects and participate in playback logic.

### No dead commands

A command must not report success while doing nothing.

Every catalog entry needs:

- A placement role.
- A visible result.
- A selectable score object when it creates an object.
- Correct movement and deletion behavior.
- A playback route when the instruction is musically audible.

### Individual objects, not flattened decoration

Several symbols can be attached to the same note, chord, rest, beat, or measure. Each mark remains individually selectable so one mark can be moved, flipped, or deleted without destroying the others.

### Real interaction rather than mock controls

Legato does not intentionally ship placeholder buttons, decorative menus, fake success messages, or controls that merely look functional. Work that is not implemented should not be presented as complete.

## Current workspace

The main interface contains:

### Players

The Players panel manages performers, instruments, staffs, and the currently active player. It includes controls to add a player, change an instrument, and remove a player.

### Flows

Flows represent separate musical sections or movements within a project.

### Score

The score is the central notation area. The insertion cursor moves rhythmically and vertically across staff positions. The selector can also move out of the score into nearby interface regions instead of being locked inside notation entry.

### Entry toolbar

The entry toolbar provides:

- Note durations.
- Accidentals.
- Note or rest entry.
- Cursor step.
- Voice selection.
- Staff selection.
- **MUSIC** for the notation catalog.
- **SELECT** for score-object selection.

### Transport

The transport includes rewind, measure loop, play/stop, and tempo information.

### Controller and accessibility panel

The controller panel includes the current control map and settings such as:

- One-handed profile.
- Note audition.
- Haptics where the browser and controller support them.
- Context-sensitive layer information.

## Notation catalog

Legato uses a large SMuFL-backed notation catalog. The current audited catalog contains **3,451 entries**.

The catalog includes common and specialist families such as:

- Accidentals and microtonal accidentals.
- Articulations.
- Dynamics and accented dynamics.
- Holds, pauses, breath marks, and caesuras.
- Ornaments, trills, mordents, and turns.
- Tremolos.
- Grace-note signs.
- Standard, harmonic, dead, cluster, slash, and specialist noteheads.
- Percussion notation.
- Guitar, string, brass, wind, keyboard, harp, and other instrumental techniques.
- Slurs, ties, phrase marks, and related spans.
- Repeats, segnos, codas, and other structural instructions.
- Textual and specialist SMuFL symbols.

Catalog classification is semantic. It determines whether a command replaces a notehead, attaches a mark, creates a span, creates a structural event, affects playback, or belongs to another score role.

## Symbol placement and editing

The notation pipeline supports:

- Attaching symbols to notes, chords, rests, beats, measures, staffs, and structural positions.
- Stacking several symbols on one event.
- Selecting each stacked symbol separately.
- Moving marks up, down, left, or right.
- Flipping supported marks above or below.
- Changing slur and phrase-curve direction.
- Deleting only the selected mark.
- Synchronizing visible structural events with playback structure data.

The **SELECT** control is intended to reach every score object, including individually placed catalog marks.

## Note, chord, voice, and rhythmic entry

Legato supports direct note and rest entry through the score cursor and toolbar.

The intended behavior includes:

- Notes can be entered at available rhythmic positions without a completed measure permanently blocking further editing.
- Chords are created by adding several pitches at the same rhythmic position.
- Individual chord notes remain selectable.
- Voices preserve independent rhythms and stem behavior.
- Rests complete voice durations.
- Accidentals are applied to the intended notes.
- Ledger lines and stems are part of actual notation rendering rather than detached approximations.

## Playback

Legato connects visible notation to playback behavior.

Supported playback interpretation includes, where applicable:

- Dynamics and accented dynamics such as `sfz`.
- Articulation length and emphasis.
- Holds and pauses.
- Ornaments and trills.
- Tremolos.
- Pitch effects.
- Instrument and technique changes.
- Grace-note treatment.
- Harmonic, muted, dead, cluster, and specialist noteheads.
- Percussion sample-family routing.
- Repeats and structural playback instructions.

Browser audio may require a direct press, click, or tap before sound can begin. Sample availability can also vary by browser session and network state.

## Accessibility and text input

Legato is controller-first but also supports visible controls through touch and mouse.

The on-screen text keyboard includes the Norwegian letters:

- `æ`
- `ø`
- `å`

Accessibility work is treated as application behavior, not a separate reduced version of the program. Controller users should be able to access the same score, notation, playback, file, and editing functions.

## Repository structure

Important files in the current build include:

| File | Purpose |
| --- | --- |
| `index.html` | Main Legato interface and application logic. |
| `support.js` | Generated document-component runtime. Do not edit directly unless rebuilding its source runtime. |
| `smufl-catalog.js` | Complete notation catalog data. |
| `notation-placement-fix.js` | Broad notation placement behavior. |
| `notation-placement-priority-fix.js` | Placement-priority corrections. |
| `notation-semantic-fix.js` | Semantic notation, playback, structure, controller, and selection behavior. |
| `notation-catalog-core.js` | Catalog classification, placement profiles, audio routes, Norwegian keyboard data, and runtime audit. |
| `notation-catalog-placement.js` | Placement, stacking, selection, movement, deletion, spans, and structural synchronization. |
| `notation-catalog-render-audio.js` | Rendering and audible catalog interpretation. |
| `notation-theory-playback-fix.js` | Grace-note, notehead, percussion, and specialist theory/playback behavior. |
| `cache-refresh.js` | Audited manifest-aware module loader and cache refresh. |
| `legato-build.json` | Published audited build version. |
| `tests/catalog-audit.test.js` | Exhaustive catalog classification and routing audit. |
| `.github/workflows/catalog-audit-and-build.yml` | Syntax checks, exhaustive audit, artifact preservation, and audited manifest publication. |
| `TUTORIAL.md` | Complete user tutorial. |

## Current audited build

The published manifest currently identifies:

```json
{
  "version": "20260728-theory-playback-1",
  "audited": true
}
```

The manifest is updated only after the catalog audit succeeds. The loader reads that independent manifest so a validated build can replace older cached modules without requiring every reference in the large main HTML file to change first.

## Run Legato locally

Legato is a static browser application. Clone or download the repository, then serve the directory over HTTP.

Using Python:

```bash
python3 -m http.server 8080
```

Then open:

```text
http://localhost:8080
```

Serving over HTTP is preferable to opening `index.html` directly because browser security rules can restrict audio, storage, module loading, and fetch behavior for local files.

## Validation

The repository uses plain Node.js syntax checks and an exhaustive catalog audit.

Run the catalog audit:

```bash
node tests/catalog-audit.test.js
```

Check the active JavaScript modules:

```bash
node --check notation-placement-fix.js
node --check notation-placement-priority-fix.js
node --check notation-semantic-fix.js
node --check notation-catalog-core.js
node --check notation-catalog-placement.js
node --check notation-catalog-render-audio.js
node --check notation-theory-playback-fix.js
node --check cache-refresh.js
node --check tests/catalog-audit.test.js
```

The automated audit is expected to inspect every catalog entry, verify placement classification, and verify explicit audio routing for entries classified as audible.

### What the audit proves

A passing audit proves that the catalog data can be classified and routed by the committed runtime rules.

### What the audit does not prove

A passing audit is not the same as physically selecting all 3,451 cards in Safari on every device. Browser rendering, touch behavior, controller behavior, audio permissions, and sample loading still require real-device testing.

Both kinds of verification matter. Automated routing coverage must not be described as manual device verification.

## Continuous integration

The GitHub Actions workflow:

1. Checks the syntax of the active JavaScript files.
2. Runs the exhaustive catalog audit.
3. Preserves the complete audit output as a workflow artifact, even when the audit fails.
4. Fails the workflow when the audit fails.
5. Publishes the tested build manifest only after a successful push audit.

This prevents an unaudited notation build from being marked as the current validated build.

## Development rules

Changes to Legato should follow these rules:

1. Preserve approved and working design unless a design change is explicitly requested.
2. Make the smallest change that fully fixes the requested behavior.
3. Do not remove unrelated functions while fixing one area.
4. Do not replace requested functionality with a simplified substitute.
5. Do not convert semantic notation objects into decorative text.
6. Keep every function controller-accessible.
7. Keep every created score object selectable.
8. Give every musically audible command an explicit playback route.
9. Test exact changed paths and the exhaustive catalog before calling the work complete.
10. State clearly which checks were automated and which were performed manually on a real browser or device.

## Reporting bugs

A precise report should include:

- Complete symbol or command name.
- Player and instrument.
- Measure and beat.
- Expected placement or behavior.
- Actual placement or behavior.
- Whether the issue is visual, selectable, audible, structural, controller-related, or file-related.
- Device, operating system, browser, and controller.
- Whether it happens in a new score and an existing saved score.

For placement bugs, include whether the mark should be above, below, attached to a note, attached to a chord, attached to a measure, or free-positioned.

For playback bugs, include whether the symbol is silent, uses the wrong sound, uses the wrong duration, or changes the wrong notes.

## Project status

Legato is under active development. The current repository contains a functioning notation interface, controller navigation, a large audited symbol catalog, selection and placement layers, structural score events, and notation-aware playback patches.

That does not mean every possible engraving, import/export, browser, controller, instrument sample, and specialist notation case is finished. Missing or incorrect behavior should be fixed in the actual architecture rather than hidden behind a placeholder or described as complete before verification.
