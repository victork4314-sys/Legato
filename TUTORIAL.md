# Legato Tutorial

This tutorial walks through the current Legato workflow from an empty score to a playable, edited passage. It is written for controller users first, with touch, mouse, and keyboard notes where useful.

> **Important:** Legato changes the controller map by layer and context. The **Controller map** shown inside the app is the authoritative guide for the controls available at that moment.

## 1. Open Legato and connect your controller

1. Open the Legato web app.
2. Connect or wake the controller before entering notes.
3. Press a controller button once so the browser recognizes it.
4. Look at the **Controller map** in the left panel.
5. Confirm that the highlighted selector can move between the top controls, player list, score, toolbar, transport, and other visible areas.

Legato is designed so controller navigation is not trapped inside one list or panel. Directional movement should follow the physical position of items on screen.

### Useful accessibility settings

The controller panel includes:

- **One-handed profile** for a reduced-input control scheme.
- **Audition notes** to hear notes while entering or selecting them.
- **Haptics** for supported controllers and browsers.
- Controller sensitivity and related settings shown in the live map.

## 2. Understand the main workspace

The workspace is divided into a few practical areas:

- **Players** — the instruments and performers in the score.
- **Flows** — separate musical sections or movements.
- **Score** — the notation page and current insertion point.
- **Entry toolbar** — durations, accidentals, note/rest mode, cursor step, voice, and staff.
- **MUSIC** — the complete notation and symbol catalog.
- **SELECT** — a list of selectable score objects, including individually placed symbols.
- **Transport** — rewind, loop, play, and tempo information.
- **FILE** — project and file operations available in the current build.

The top mode strip changes the working area without replacing the score. Use **SCORE** to return to the notation page from another area.

## 3. Add and configure a player

1. Move to **Add a player** in the Players panel.
2. Activate it.
3. Choose the required instrument.
4. Select the player in the Players list.
5. Use **Change this player’s instrument** when the instrument needs to be replaced.
6. Use **Remove** only when the complete player should be deleted.

Each player can contain one or more staves depending on the instrument and score setup.

## 4. Enter the first note

1. Return to **SCORE**.
2. Select a duration from the entry toolbar.
3. Confirm that the entry mode says **Note entry** rather than rest entry.
4. Choose the required voice.
5. Choose the required staff.
6. Move the score cursor to the intended rhythmic position.
7. Move vertically to the intended staff position.
8. Place the note.

With **Audition notes** enabled, Legato plays the pitch when it is entered or selected.

### Choose a duration before placement

The duration controls define the rhythmic value of the next note or rest. Change the duration whenever the next event has a different value.

### Add an accidental

1. Select the accidental in the toolbar.
2. Move to the intended note position.
3. Place the note.

Accidentals are attached to the note rather than placed as unrelated floating text.

## 5. Enter rests

1. Activate **Note or rest entry** until rest entry is selected.
2. Choose the rest duration.
3. Move to the intended rhythmic position.
4. Place the rest.
5. Switch back to note entry before entering pitches again.

Use rests to preserve the correct duration of every voice. Do not leave an incomplete voice merely because another voice contains notes at the same time.

## 6. Create a chord

A chord is made by placing multiple pitches at the same rhythmic position in the same voice.

1. Enter the first note of the chord.
2. Keep the score cursor at the same beat.
3. Move vertically to the next pitch.
4. Add the next note.
5. Repeat for every chord tone.

The noteheads should share the correct rhythmic position and use one chord stem where notation rules require it. Use **SELECT** when an individual chord note needs to be selected or edited.

## 7. Work with multiple voices

1. Select a voice number in the toolbar.
2. Enter the notes or rests belonging to that voice.
3. Change to another voice.
4. Enter the independent rhythm for that voice.

Keep each voice rhythmically complete. Voice direction and stem behavior should follow normal notation rules unless deliberately overridden.

## 8. Change the cursor step

The **STEP** control changes how far the insertion point moves through the score.

Use a smaller step for precise rhythmic positioning and a larger step for faster movement across empty or completed areas. Cursor movement should remain free between score elements and surrounding interface controls.

## 9. Open the complete notation catalog

Press **Y** on the controller or activate **MUSIC** in the toolbar.

The catalog contains the full available SMuFL-backed command collection, including common and specialist notation. It is organized so symbols can be chosen individually rather than inserted as a fixed group.

Typical families include:

- Articulations
- Accidentals and microtonal accidentals
- Dynamics and dynamic combinations
- Holds, pauses, and breath marks
- Ornaments
- Tremolos
- Grace-note signs
- Noteheads
- Percussion notation
- Guitar and string techniques
- Keyboard, harp, wind, and brass techniques
- Repeats, codas, segnos, and other score structures
- Slurs, ties, phrase marks, and other spans
- Text and specialist symbols

## 10. Place a symbol exactly where it belongs

1. Open **MUSIC**.
2. Find the symbol or command.
3. Select or hold the command as indicated by the active controller layer.
4. Move to the intended note, rest, beat, measure, staff, or page position.
5. Place the symbol.

Legato classifies symbols by musical role. For example:

- An articulation attaches to a note or chord.
- A dynamic belongs below or above the staff according to the chosen placement.
- A coda or segno belongs at a structural score position.
- An accidental replaces or modifies the note accidental role.
- A notehead command changes the notehead rather than creating detached text.
- A technique mark remains attached to the affected musical event.

Several marks can be stacked on the same event. Each stacked mark remains a separate selectable object.

## 11. Add a dynamic

1. Place the cursor at the required note or beat.
2. Open **MUSIC**.
3. Choose a dynamic such as `p`, `mf`, `f`, `sfz`, or another available marking.
4. Place it.
5. Use **SELECT** to move it vertically or horizontally when required.

Dynamics affect playback when the selected marking has an audible route. Combined and accented dynamics are interpreted separately rather than displayed as meaningless text.

## 12. Add articulations and ornaments

1. Select the note or chord.
2. Open **MUSIC**.
3. Choose the articulation or ornament.
4. Place it on the event.
5. Add another mark if the event requires a stack.

Articulations, ornaments, tremolos, holds, pitch effects, and supported techniques influence playback. Their exact audible result depends on the musical family, selected instrument, and available sample route.

## 13. Add a slur or phrase mark

1. Choose the slur or phrase command from **MUSIC**.
2. Set the start event.
3. Set the end event.
4. Confirm the span.
5. Open **SELECT** and choose the curve when its direction needs adjustment.
6. Flip the curve above or below the notes.

Slurs and phrase marks can curve upward or downward. The direction is not permanently locked to one side.

## 14. Add a tie

A tie joins two notes of the same written pitch across rhythmic positions.

1. Select the first note.
2. Choose the tie command.
3. Select the second note of the same pitch.
4. Confirm the tie.

Do not use a tie as a substitute for a slur. A slur groups phrasing or articulation; a tie extends the duration of one pitch.

## 15. Add grace-note notation

1. Select the main note.
2. Open the grace-note family in **MUSIC**.
3. Choose the required grace form, such as an acciaccatura or appoggiatura sign.
4. Place it at the main note.

The current attached grace notation uses a short neighboring-pitch playback interpretation. It is distinct from trill playback.

## 16. Change a notehead

1. Select the note.
2. Open the notehead family.
3. Choose the required notehead.
4. Apply it to the note.

Notehead commands replace the visual notehead role. They do not create a second loose symbol over the original notehead.

Some noteheads also alter playback behavior. Examples include muted or dead notes, harmonics, clusters, and specialist percussion noteheads.

## 17. Add percussion and specialist techniques

1. Select the target note or event.
2. Open the relevant family in **MUSIC**.
3. Choose the required percussion, string, guitar, brass, keyboard, or other technique.
4. Place it.

Where an audible route exists, Legato chooses an appropriate sample family or playback treatment. The mark remains visible and independently selectable even when it also changes playback.

## 18. Add repeats, segnos, codas, and structural marks

1. Move to the correct measure or structural position.
2. Open **MUSIC**.
3. Choose the required structure.
4. Place it.
5. Use **SELECT** to move or remove it.

Structural symbols are stored as score events and synchronized with playback structure data. A visible coda, segno, or repeat should not be a dead decorative glyph.

## 19. Select and edit any score object

Activate **SELECT** to open the score-object selector.

The selector includes notes, rests, spans, structural marks, and individually stacked catalog symbols. After selecting an object, use the available controls to:

- Move it up or down.
- Move it left or right.
- Flip placement above or below where supported.
- Change a curve direction.
- Delete only that object.

Deleting one stacked mark should not remove every other mark attached to the same note.

## 20. Play the score

Use the transport controls to:

- **Rewind** to the start.
- **Loop** the current measure when practicing or checking engraving.
- **Play/stop** the score.
- Read the current tempo in BPM.

Playback should continue beyond the first few measures. Repeats and supported structural marks are followed by the playback scheduler.

### Browser audio note

Some browsers require a direct button press or tap before audio can begin. When the score is silent, activate a note or the Play control once to unlock browser audio.

## 21. Use touch, mouse, or keyboard

Legato is controller-first, but the visible controls can also be activated with touch or a mouse.

For text entry, use the on-screen keyboard or the hardware keyboard. The current on-screen keyboard includes the Norwegian letters:

- `æ`
- `ø`
- `å`

## 22. Save and reopen work

Open **FILE** and use the project operations available in the current build. After reopening or refreshing the app, confirm that the intended score or project is still selected before continuing.

Because browser storage can be cleared by private browsing, browser cleanup, or device settings, keep an exported or downloaded copy whenever the file menu provides that option.

## 23. Suggested first practice score

Create a short eight-measure exercise containing:

1. One treble-clef player.
2. A melody using quarter notes, eighth notes, and rests.
3. One accidental.
4. One two-note chord.
5. A second voice in one measure.
6. A slur that curves downward.
7. `p`, `sfz`, and `f` dynamics.
8. One staccato and one accent.
9. One ornament or tremolo.
10. A repeat and a final coda or segno mark.

Then use **SELECT** to move every added symbol individually and play the complete passage from the beginning.

## 24. Troubleshooting

### The controller does not respond

- Press a controller button after the page loads.
- Confirm that the browser and operating system can see the controller.
- Check the live Controller map.
- Reconnect the controller and reload the page if the browser lost the gamepad session.

### Navigation feels trapped

Move toward the visible neighboring area rather than continuing through the current list. Navigation is intended to follow the physical layout of the program. Report any element that cannot be reached from its visible neighbor.

### A symbol appears in the wrong place

Open **SELECT**, choose that exact symbol, and move or flip it. If the symbol is classified under the wrong musical role, report the complete command name so its catalog classification can be corrected.

### A symbol is visible but silent

Confirm that the score is playing, audio has been unlocked by a direct interaction, and the selected instrument sample loaded. Not every visual instruction produces sound, but every musically audible command should have an explicit playback route.

### A coda, repeat, or segno does not affect playback

Confirm that it was inserted as a structural command at the correct measure rather than as unrelated text. Select and re-place the structural object if necessary.

### The latest build does not appear

Reload the page. Legato uses an audited build manifest and cache-refresh loader so validated modules can replace older cached files.

## 25. Reporting a precise problem

A useful report contains:

- The complete command or symbol name.
- The player and instrument.
- The measure and beat.
- The expected placement.
- The actual placement.
- Whether the problem is visual, selectable, audible, or structural.
- The browser, device, and controller.

That information makes it possible to fix the exact catalog route without altering unrelated, already working parts of the app.
