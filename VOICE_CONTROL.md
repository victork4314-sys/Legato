# Legato voice control

Legato voice control is built into the browser application. It does not install a native helper, run a separate background process, open macOS settings, or send keyboard events to another application.

Voice recognition produces a visible ordered command plan first. Legato changes the score only after you press **Run commands** or speak **Run commands** as a separate confirmation.

## Open voice control

1. Open the right-side properties area.
2. Choose **Voice control**.
3. Choose **Start listening**.
4. Allow microphone access for the Legato website if the browser asks.

Every voice-control button has a `data-ptr` label and is included in Legato's normal controller scanning system.

## Examples

- `Add C sharp five quarter note.`
- `Add C four, E four, G four chord.`
- `Add a half note rest.`
- `Place staccato.`
- `Place fermata then move right.`
- `Tempo one hundred twenty then play.`
- `Go to bar three beat two.`
- `Move right four times.`
- `Select staff two.`
- `Undo then save project.`

Speak **Run commands** to execute the currently previewed plan. Speak **Clear commands** to discard it.

## Supported command families

Voice control routes into Legato's existing application methods for:

- notes, rests, and chords
- whole, half, quarter, eighth, sixteenth, and thirty-second durations
- sharp, flat, and natural accidentals
- all notation entries available through Legato's 3,451-entry SMuFL catalog
- cursor and staff navigation
- tempo
- Setup, Write, Engrave, Play, Print, and Controller modes
- playback
- undo, redo, copy, paste, delete, pointer, MUSIC, and project menu actions
- new, open, and save project actions

Voice-created notation uses the same score objects, placement rules, selection behavior, undo history, and playback routes as controller-created notation.

## Safety rules

- The microphone never starts automatically.
- Recognition callbacks never execute score commands directly.
- A plan may contain at most eight commands.
- A repeated movement or action may run at most sixteen times.
- Unknown phrases block the entire plan.
- Ambiguous notation names block the entire plan and ask for a more specific name.
- Notes outside the currently visible staff and clef range are blocked before execution.
- Run or clear must be spoken by itself.

## Set up my voice

Choose **Set up my voice** and read each of the five displayed phrases. If the browser consistently hears a phrase differently, Legato stores that heard phrase as a local pronunciation correction for the expected command.

Voice setup and pronunciation corrections are stored only in that browser's local storage. **Reset voice setup** removes them.

## Browser behavior

Voice recognition is feature-detected at runtime. It is expected to work in browsers that expose `SpeechRecognition` or `webkitSpeechRecognition` on a secure HTTPS page.

Browser support and permission behavior can differ between normal Safari tabs and Home Screen web apps. When voice recognition is unavailable, Legato shows an unavailable message and leaves the score unchanged.

## Automated validation

The committed voice test suites cover:

- 64 language, parsing, catalog-matching, and safety cases
- 19 execution cases against a mocked Legato owner

These automated tests do not replace a real microphone test in Safari on each physical device.
