"use strict";
(function (root, factory) {
  const api = factory(root, root && root.LegatoVoiceLanguage);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.LegatoVoiceControl = api;
  if (root && root.document) api.install();
})(typeof globalThis !== "undefined" ? globalThis : this, function (root, VoiceLanguage) {
  const VERSION = "20260806-legato-voice-1";
  const STORAGE_ALIASES = "legato.voice.aliases.v1";
  const STORAGE_CALIBRATION = "legato.voice.calibration.v1";
  const CALIBRATION_PROMPTS = Object.freeze([
    "Add a quarter note C sharp five",
    "Place staccato then move right",
    "Set tempo to one hundred twenty",
    "Add a fermata then play",
    "Go to bar three beat two"
  ]);

  const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
  const normalize = value => VoiceLanguage ? VoiceLanguage.normalize(value) : String(value || "").toLowerCase().trim();

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function loadJSON(key, fallback) {
    try {
      const value = root.localStorage && root.localStorage.getItem(key);
      return value ? JSON.parse(value) : clone(fallback);
    } catch (_) {
      return clone(fallback);
    }
  }

  function saveJSON(key, value) {
    try {
      if (root.localStorage) root.localStorage.setItem(key, JSON.stringify(value));
    } catch (_) {}
  }

  function setStateAsync(owner, patch) {
    return new Promise((resolve, reject) => {
      try {
        owner.setState(patch, resolve);
      } catch (error) {
        reject(error);
      }
    });
  }

  function pitchBase(value) {
    return String(value || "")
      .toUpperCase()
      .replace(/[♯♭♮#]/g, "")
      .replace(/SHARP|FLAT|NATURAL/g, "")
      .replace(/\s+/g, "")
      .match(/[A-G]-?\d/)?.[0] || "";
  }

  function pitchStep(owner, pitch, staff, pos) {
    const target = pitch.letter + String(pitch.octave);
    if (!owner || typeof owner.pitchName !== "function") return null;
    for (let step = -2; step <= 22; step++) {
      let name = "";
      try { name = owner.pitchName(step, staff, null, pos); } catch (_) {}
      if (pitchBase(name) === target) return step;
    }
    return null;
  }

  function resolveCatalogCommand(command, glyphs) {
    const result = VoiceLanguage.bestCatalogMatch(command.query, glyphs);
    if (result.ambiguous) {
      return {
        command: Object.assign({}, command, { type: "invalid", label: "Ambiguous symbol: " + command.query }),
        error: "“" + command.query + "” matches more than one notation symbol. Be more specific."
      };
    }
    if (!result.match) {
      return {
        command: Object.assign({}, command, { type: "invalid", label: "Unknown symbol: " + command.query }),
        error: "No notation symbol matched “" + command.query + "”."
      };
    }
    return {
      command: Object.assign({}, command, {
        glyph: result.match,
        confidence: Math.min(command.confidence || 0.9, result.score || 0.9),
        label: "Place " + result.match.label
      }),
      error: null
    };
  }

  function preparePlan(owner, plan, catalog) {
    const glyphs = catalog && Array.isArray(catalog.glyphs) ? catalog.glyphs : [];
    const prepared = [];
    const errors = Array.isArray(plan && plan.errors) ? plan.errors.slice() : [];
    let staff = Math.max(0, Number(owner && owner.state && owner.state.staff) || 0);
    let pos = Math.max(0, Number(owner && owner.state && owner.state.pos) || 0);

    for (const sourceCommand of (plan && plan.commands) || []) {
      let command = Object.assign({}, sourceCommand);
      if (command.type === "catalog") {
        const resolved = resolveCatalogCommand(command, glyphs);
        command = resolved.command;
        if (resolved.error) errors.push(resolved.error);
      }
      if (command.type === "staff") staff = Math.max(0, command.staff - 1);
      if (command.type === "goto") {
        const cap = owner && typeof owner.barCapacity === "function" ? Number(owner.barCapacity()) || 4 : 4;
        pos = Math.max(0, (command.bar - 1) * cap + (command.beat - 1));
      }
      if (command.type === "note" || command.type === "chord") {
        command.preparedPitches = command.pitches.map(pitch => Object.assign({}, pitch, { step: pitchStep(owner, pitch, staff, pos) }));
        const missing = command.preparedPitches.filter(pitch => pitch.step == null);
        if (missing.length) errors.push("The current clef cannot place " + missing.map(pitch => pitch.label).join(", ") + " on the visible staff range.");
      }
      prepared.push(command);
    }

    const valid = !!(plan && plan.valid) && errors.length === 0 && prepared.every(command => command.type !== "unknown" && command.type !== "invalid");
    return Object.assign({}, plan, { commands: prepared, errors, valid });
  }

  function accidentalID(name) {
    return name === "sharp" ? "sh" : name === "flat" ? "f" : "n";
  }

  async function enterPitches(owner, command) {
    const basePos = Number(owner.state.pos) || 0;
    const pitches = command.preparedPitches || command.pitches || [];
    for (let index = 0; index < pitches.length; index++) {
      const pitch = pitches[index];
      if (pitch.step == null) throw new Error("Pitch " + pitch.label + " is outside the current staff range.");
      await setStateAsync(owner, {
        zone: 3,
        pos: basePos,
        step: pitch.step,
        dur: command.durationIndex,
        acc: accidentalID(pitch.accidental),
        entry: "note",
        selId: null,
        scoreObjectId: null
      });
      owner._lastEntry = 0;
      owner.enterNote();
      await wait(120);
    }
  }

  async function executeCommand(owner, command) {
    if (!owner) throw new Error("Legato is not ready.");
    switch (command.type) {
      case "action":
        for (let i = 0; i < Number(command.count || 1); i++) {
          owner.dispatch(command.action, "press");
          if (command.action === "select-modifier") owner.dispatch(command.action, "release");
          if (i + 1 < Number(command.count || 1)) await wait(80);
        }
        return;
      case "duration":
        owner.setDur(command.durationIndex);
        return;
      case "accidental":
        owner.setAcc(command.accidental);
        return;
      case "tempo":
        await setStateAsync(owner, { tempo: command.bpm, spoken: "Tempo " + command.bpm });
        return;
      case "mode":
        await setStateAsync(owner, { mode: command.mode, spoken: command.label });
        return;
      case "goto": {
        const cap = Number(owner.barCapacity()) || 4;
        const maxPos = Math.max(0, (Number(owner.state.bars) || 1) * cap - 0.001);
        const pos = Math.max(0, Math.min(maxPos, (command.bar - 1) * cap + (command.beat - 1)));
        await setStateAsync(owner, { zone: 3, pos, selId: null, scoreObjectId: null, spoken: command.label });
        return;
      }
      case "staff": {
        const count = Array.isArray(owner.state.players) ? owner.state.players.length : 1;
        const staff = Math.max(0, Math.min(count - 1, command.staff - 1));
        await setStateAsync(owner, { zone: 3, staff, selId: null, scoreObjectId: null, spoken: "Staff " + (staff + 1) });
        return;
      }
      case "project":
        if (command.operation === "save" && typeof owner.saveProject === "function") return owner.saveProject();
        if (command.operation === "new" && typeof owner.newProject === "function") return owner.newProject();
        if (command.operation === "open") {
          const input = root.document && root.document.getElementById("legato-open");
          if (input) return input.click();
        }
        throw new Error("That project operation is unavailable.");
      case "rest":
        await setStateAsync(owner, { zone: 3, dur: command.durationIndex, entry: "rest", selId: null, scoreObjectId: null });
        owner._lastEntry = 0;
        owner.enterNote();
        await wait(120);
        return;
      case "note":
      case "chord":
        return enterPitches(owner, command);
      case "catalog":
        if (!command.glyph) throw new Error("Notation symbol was not resolved.");
        owner.applyCatalogCommand(command.glyph, command.glyph.label, command.glyph.glyph);
        await wait(80);
        return;
      default:
        throw new Error("Unsupported voice command: " + command.type);
    }
  }

  async function executePlan(owner, plan) {
    if (!plan || !plan.valid) throw new Error((plan && plan.errors && plan.errors.join(" ")) || "The voice plan is not safe to run.");
    for (const command of plan.commands) await executeCommand(owner, command);
    return true;
  }

  const state = {
    installed: false,
    panelOpen: false,
    listening: false,
    recognition: null,
    pending: null,
    transcript: "",
    status: "Voice control is ready.",
    aliases: loadJSON(STORAGE_ALIASES, {}),
    calibration: loadJSON(STORAGE_CALIBRATION, { completed: 0 }),
    calibrationExpected: null,
    observer: null
  };

  function owner() { return root.__legatoOwner || null; }
  function catalog() { return root.LEGATO_SMUFL_CATALOG || { glyphs: [] }; }
  function recognitionConstructor() { return root.SpeechRecognition || root.webkitSpeechRecognition || null; }

  function button(label, action, primary) {
    const el = root.document.createElement("button");
    el.type = "button";
    el.textContent = label;
    el.setAttribute("data-ptr", label);
    el.style.cssText = "border:1px solid " + (primary ? "var(--accent)" : "var(--border-strong)") + ";background:" + (primary ? "var(--accent)" : "var(--control)") + ";color:" + (primary ? "var(--bg)" : "var(--text)") + ";padding:8px 11px;border-radius:5px;font:600 12px var(--ui-font);cursor:pointer;";
    el.addEventListener("click", action);
    return el;
  }

  function panelElement() { return root.document.getElementById("legato-voice-panel"); }

  function render() {
    const panel = panelElement();
    if (!panel) return;
    panel.style.display = state.panelOpen ? "flex" : "none";
    const status = panel.querySelector("[data-voice-status]");
    const transcript = panel.querySelector("[data-voice-transcript]");
    const preview = panel.querySelector("[data-voice-preview]");
    const prompt = panel.querySelector("[data-voice-calibration]");
    const start = panel.querySelector("[data-voice-start]");
    if (status) status.textContent = state.status;
    if (transcript) transcript.textContent = state.transcript || "Your speech will appear here.";
    if (start) start.textContent = state.listening ? "Stop listening" : "Start listening";
    if (prompt) {
      prompt.textContent = state.calibrationExpected
        ? "Read this phrase: “" + state.calibrationExpected + "”"
        : "Voice setup: " + Math.min(state.calibration.completed || 0, CALIBRATION_PROMPTS.length) + "/" + CALIBRATION_PROMPTS.length + " phrases";
    }
    if (preview) {
      preview.replaceChildren();
      if (!state.pending || !state.pending.commands.length) {
        const empty = root.document.createElement("div");
        empty.textContent = "Nothing is queued.";
        empty.style.color = "var(--muted)";
        preview.appendChild(empty);
      } else {
        state.pending.commands.forEach((command, index) => {
          const row = root.document.createElement("div");
          row.style.cssText = "display:flex;gap:9px;padding:7px 0;border-bottom:1px solid var(--border);align-items:flex-start;";
          const n = root.document.createElement("span"); n.textContent = String(index + 1); n.style.cssText = "font-family:'IBM Plex Mono',monospace;color:var(--muted);";
          const text = root.document.createElement("span"); text.textContent = command.label; text.style.flex = "1";
          row.append(n, text); preview.appendChild(row);
        });
        if (state.pending.errors.length) {
          const err = root.document.createElement("div");
          err.textContent = state.pending.errors.join(" ");
          err.style.cssText = "padding-top:8px;color:#e58f82;";
          preview.appendChild(err);
        }
      }
    }
    const run = panel.querySelector("[data-voice-run]");
    if (run) run.disabled = !state.pending || !state.pending.valid;
  }

  function clearPreview(message) {
    state.pending = null;
    state.transcript = "";
    state.status = message || "Voice command preview cleared.";
    render();
  }

  async function runPending() {
    if (!state.pending || !state.pending.valid) {
      state.status = "There is no complete safe plan to run.";
      render();
      return;
    }
    try {
      state.status = "Running " + state.pending.commands.length + " voice command" + (state.pending.commands.length === 1 ? "" : "s") + "…";
      render();
      await executePlan(owner(), state.pending);
      const labels = state.pending.commands.map(command => command.label).join(" → ");
      state.pending = null;
      state.status = "Completed: " + labels;
      const o = owner();
      if (o && typeof o.setState === "function") o.setState({ spoken: "Voice commands completed" });
    } catch (error) {
      state.status = "Voice commands stopped: " + (error && error.message ? error.message : String(error));
    }
    render();
  }

  function resolveTranscript(text) {
    state.transcript = String(text || "").trim();
    if (state.calibrationExpected) {
      const expected = state.calibrationExpected;
      const heard = state.transcript;
      if (heard && normalize(heard) !== normalize(expected)) {
        state.aliases[heard] = expected;
        saveJSON(STORAGE_ALIASES, state.aliases);
      }
      state.calibration.completed = Math.min(CALIBRATION_PROMPTS.length, (state.calibration.completed || 0) + 1);
      saveJSON(STORAGE_CALIBRATION, state.calibration);
      state.calibrationExpected = null;
      state.status = "Voice setup phrase saved.";
      render();
      return;
    }

    const parsed = VoiceLanguage.parsePlan(state.transcript, { aliases: state.aliases });
    if (parsed.commands.length === 1 && parsed.commands[0].type === "voice-run") {
      runPending();
      return;
    }
    if (parsed.commands.length === 1 && parsed.commands[0].type === "voice-clear") {
      clearPreview();
      return;
    }
    state.pending = preparePlan(owner(), parsed, catalog());
    state.status = state.pending.valid
      ? "Review the ordered command plan, then run it."
      : (state.pending.errors.join(" ") || "The spoken command was blocked.");
    render();
  }

  function stopListening() {
    const recognition = state.recognition;
    state.recognition = null;
    state.listening = false;
    try { if (recognition) recognition.stop(); } catch (_) {}
    render();
  }

  function startListening() {
    if (state.listening) return stopListening();
    const SpeechRecognition = recognitionConstructor();
    if (!SpeechRecognition) {
      state.status = "Voice recognition is not available in this browser. Open Legato in current Safari, Chrome, or Edge over HTTPS.";
      render();
      return;
    }
    let recognition;
    try {
      recognition = new SpeechRecognition();
      recognition.lang = root.navigator && root.navigator.language ? root.navigator.language : "en-US";
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;
      recognition.onstart = () => { state.listening = true; state.status = state.calibrationExpected ? "Listening for the setup phrase…" : "Listening for a Legato command…"; render(); };
      recognition.onresult = event => {
        try {
          let combined = "";
          let finalText = "";
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const text = event.results[i][0] && event.results[i][0].transcript || "";
            combined += text;
            if (event.results[i].isFinal) finalText += text;
          }
          state.transcript = combined.trim();
          render();
          if (finalText.trim()) resolveTranscript(finalText.trim());
        } catch (error) {
          state.status = "Voice result could not be read: " + error.message;
          render();
        }
      };
      recognition.onerror = event => {
        state.status = event && event.error === "not-allowed"
          ? "Microphone access was not allowed. Safari controls this permission for the Legato website."
          : "Voice recognition stopped: " + ((event && event.error) || "unknown error") + ".";
        state.listening = false;
        state.recognition = null;
        render();
      };
      recognition.onend = () => {
        state.listening = false;
        state.recognition = null;
        render();
      };
      state.recognition = recognition;
      recognition.start();
    } catch (error) {
      state.recognition = null;
      state.listening = false;
      state.status = "Voice recognition could not start: " + (error && error.message ? error.message : String(error));
      render();
    }
  }

  function startCalibration() {
    const index = Math.min(state.calibration.completed || 0, CALIBRATION_PROMPTS.length - 1);
    if ((state.calibration.completed || 0) >= CALIBRATION_PROMPTS.length) {
      state.calibration = { completed: 0 };
      saveJSON(STORAGE_CALIBRATION, state.calibration);
    }
    state.calibrationExpected = CALIBRATION_PROMPTS[index] || CALIBRATION_PROMPTS[0];
    state.status = "Read the displayed setup phrase, then press Start listening.";
    render();
  }

  function resetVoiceSetup() {
    state.aliases = {};
    state.calibration = { completed: 0 };
    state.calibrationExpected = null;
    saveJSON(STORAGE_ALIASES, state.aliases);
    saveJSON(STORAGE_CALIBRATION, state.calibration);
    state.status = "Voice setup and pronunciation corrections were reset.";
    render();
  }

  function createPanel() {
    if (panelElement()) return;
    const panel = root.document.createElement("section");
    panel.id = "legato-voice-panel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Legato voice control");
    panel.setAttribute("data-scroll", "props");
    panel.style.cssText = "display:none;position:fixed;inset:7vh max(18px,8vw);z-index:100000;flex-direction:column;gap:14px;padding:20px;overflow:auto;background:var(--panel);color:var(--text);border:1px solid var(--border-strong);border-radius:8px;box-shadow:0 18px 70px rgba(0,0,0,.55);font-family:var(--ui-font);";

    const header = root.document.createElement("div");
    header.style.cssText = "display:flex;align-items:flex-start;gap:12px;";
    const titleWrap = root.document.createElement("div"); titleWrap.style.flex = "1";
    const title = root.document.createElement("h2"); title.textContent = "Voice control"; title.style.cssText = "margin:0 0 4px;font-size:22px;";
    const subtitle = root.document.createElement("div"); subtitle.textContent = "Speech becomes a visible command plan before Legato changes the score."; subtitle.style.color = "var(--muted)";
    titleWrap.append(title, subtitle);
    const close = button("Close voice control", () => { stopListening(); state.panelOpen = false; render(); }, false);
    header.append(titleWrap, close);

    const status = root.document.createElement("div"); status.setAttribute("data-voice-status", ""); status.style.cssText = "padding:9px 11px;background:var(--raised);border:1px solid var(--border);border-radius:5px;";
    const calibration = root.document.createElement("div"); calibration.setAttribute("data-voice-calibration", ""); calibration.style.cssText = "font-size:12px;color:var(--text-2);";

    const controls = root.document.createElement("div"); controls.style.cssText = "display:flex;flex-wrap:wrap;gap:8px;";
    const start = button("Start listening", startListening, true); start.setAttribute("data-voice-start", "");
    const setup = button("Set up my voice", startCalibration, false);
    const reset = button("Reset voice setup", resetVoiceSetup, false);
    controls.append(start, setup, reset);

    const transcriptTitle = root.document.createElement("h3"); transcriptTitle.textContent = "Transcript"; transcriptTitle.style.cssText = "margin:4px 0 0;font-size:14px;";
    const transcript = root.document.createElement("div"); transcript.setAttribute("data-voice-transcript", ""); transcript.style.cssText = "min-height:48px;padding:10px;background:var(--input-bg);border:1px solid var(--border);border-radius:5px;white-space:pre-wrap;";
    const previewTitle = root.document.createElement("h3"); previewTitle.textContent = "Command preview"; previewTitle.style.cssText = "margin:4px 0 0;font-size:14px;";
    const preview = root.document.createElement("div"); preview.setAttribute("data-voice-preview", ""); preview.style.cssText = "padding:10px;background:var(--raised);border:1px solid var(--border);border-radius:5px;";

    const actions = root.document.createElement("div"); actions.style.cssText = "display:flex;gap:8px;align-items:center;";
    const run = button("Run commands", runPending, true); run.setAttribute("data-voice-run", "");
    const clear = button("Clear preview", () => clearPreview(), false);
    const help = root.document.createElement("span"); help.textContent = "Examples: “add C sharp five quarter note”, “place staccato”, “move right four times”, “tempo 120 then play”."; help.style.cssText = "font-size:11px;color:var(--muted);margin-left:auto;max-width:440px;";
    actions.append(run, clear, help);

    panel.append(header, status, calibration, controls, transcriptTitle, transcript, previewTitle, preview, actions);
    root.document.body.appendChild(panel);
  }

  function attachLauncher() {
    if (root.document.getElementById("legato-voice-launcher")) return;
    const props = root.document.querySelector('[data-scroll="props"]');
    if (!props) return;
    const launcher = button("Voice control", () => { state.panelOpen = true; render(); }, false);
    launcher.id = "legato-voice-launcher";
    launcher.style.cssText += "width:calc(100% - 18px);margin:9px;display:block;";
    props.appendChild(launcher);
  }

  function install() {
    if (state.installed || !root.document || !VoiceLanguage) return false;
    state.installed = true;
    createPanel();
    attachLauncher();
    state.observer = new MutationObserver(() => attachLauncher());
    state.observer.observe(root.document.documentElement, { childList: true, subtree: true });
    render();
    root.__LEGATO_VOICE_CONTROL__ = { version: VERSION, open: () => { state.panelOpen = true; render(); }, close: () => { state.panelOpen = false; render(); }, state };
    return true;
  }

  return {
    VERSION, CALIBRATION_PROMPTS,
    pitchBase, pitchStep, resolveCatalogCommand, preparePlan,
    executeCommand, executePlan, setStateAsync,
    install, state
  };
});
