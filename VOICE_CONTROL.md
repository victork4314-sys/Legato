# Legato voice control

Legato voice control is built into the application. It does not install a native helper, open macOS Settings, use iPad keyboard Dictation, or send keyboard events to another program.

## How it behaves

1. Open **Voice control** in the right-side properties area.
2. Choose **Start voice control** once.
3. Speak normal music and Legato commands.
4. Legato executes each complete recognized command immediately.
5. Choose **Stop voice control** when you want listening to end.

Closing the Voice control window does not stop listening. The status and recent-command history are available when the window is opened again.

There is no command preview, no Accept button, no Run commands button, and no text or Dictation field.

## Recognition engines

Legato selects the recognition engine automatically:

- On a Mac browser with a working system speech-recognition service, Legato uses that continuous recognizer.
- On iPad, when no system recognizer exists, or when Safari returns `service-not-allowed`, Legato uses its own on-device WebAssembly speech engine.

The on-device engine is compiled from a pinned whisper.cpp release by Legato's own GitHub Actions pipeline. Its generated files and checksums are committed and audited with the application.

The first on-device start downloads the pinned English model, approximately 31 MB, verifies its SHA-256 digest, and caches it in the browser. Audio remains in the browser and is passed to the local WebAssembly engine.

The on-device engine requires cross-origin isolation. On GitHub Pages, Legato installs its bundled isolation service worker. The page may reload once during that one-time setup. If browser microphone permission has not been granted yet, the browser will ask when voice control starts.

## Examples

- `Add C sharp five quarter note.`
- `Add C four E four G four chord.`
- `Add a half note rest.`
- `Place staccato.`
- `Place fermata then move right.`
- `Tempo one hundred twenty then play.`
- `Go to bar three beat two.`
- `Move right four times.`
- `Select staff two.`
- `Undo then save project.`

## Supported command families

Voice control routes into Legato's existing application methods for:

- notes, rests, and chords
- whole, half, quarter, eighth, sixteenth, and thirty-second durations
- sharp, flat, and natural accidentals
- notation entries available through Legato's 3,451-entry SMuFL catalog
- cursor, bar, beat, and staff navigation
- tempo
- Setup, Write, Engrave, Play, Print, and Controller modes
- playback
- undo, redo, copy, paste, delete, pointer, MUSIC, and project menu actions
- new, open, and save project actions
- ordered multi-command phrases and bounded repeated actions

Voice-created notation uses the same score objects, placement rules, selection behavior, undo history, and playback paths as controller-created notation.

## Direct-execution safeguards

Valid complete commands execute immediately. The safeguards are applied before execution, without asking for confirmation:

- Unknown phrases change nothing.
- Ambiguous notation names change nothing and appear as an error in recent-command history.
- A spoken phrase may contain at most eight ordered commands.
- A repeated action may run at most sixteen times.
- Notes outside the currently available staff and clef range are blocked.
- Duplicate recognition results within a short interval are suppressed.
- Commands are serialized so a second recognized phrase cannot interleave halfway through the first command.

## Set up my voice

Choose **Set up my voice** and read the five displayed music phrases. If the recognizer consistently hears a phrase differently, Legato stores that heard phrase as a local correction for the intended command.

Voice setup and pronunciation corrections are stored only in that browser's local storage. **Reset voice setup** removes them.

## Automated validation

The voice test suite covers:

- language parsing and catalog matching
- existing Legato command execution methods
- immediate execution with no pending preview state
- invalid-command blocking
- iPad and native-engine selection
- system-service refusal fallback
- microphone and Web Audio lifecycle cleanup
- 48 kHz to 16 kHz downsampling
- bounded rolling audio
- transcript stability and duplicate suppression
- model SHA-256 verification and rejection
- generated WebAssembly build checksums

Automated tests cannot prove microphone recognition speed or accuracy on a particular physical iPad or Mac. Those are verified only by speaking into the deployed build on that device.
