repo: victork4314-sys/Legato
branch: main

## Last sync
date: 2026-07-25T18:25:00Z

### Updated in this project
- Modes are real: Setup (new/open/save), Write (entry + editing), Engrave (staff size, spacing, bar numbers, bar count), Play (mixer, metronome, count-in), Print (paper, print/PDF, MusicXML, MIDI), Controller (profile, deadzone, repeat, pointer speed, haptics).
- Editing: note selection, ranges with LT/shift, copy/cut/paste/duplicate/delete, transpose, octave shift, rests, chords, ties, tuplets, four voices, undo/redo with autosave and crash recovery.
- Every catalog command now places something on the score; ornaments, dynamics and chords are realised in playback.
- Real sampled instruments (Salamander piano + tonejs-instruments orchestra), all 128 GM voices assignable per player.
- Cushioned haptics; speech synthesis removed in favour of the on-screen status line.

## Screen map
| Project screen | Repo files referenced |
| --- | --- |
| Notation Studio.dc.html | README.md; controller.js (bindings, deadzone, repeat, one-handed); controller-first.css (workspace, halo, focus lens); js/13-edit-nav.js (pitch, duration, selection); js/02–04 catalogs (commands); js/23-project-ops.js (project, layout, exchange, print); js/16-musicxml-export.js, js/18-midi.js (export shapes) |
| design/legato-notation-studio.html | Standalone bundle, Bravura embedded |
