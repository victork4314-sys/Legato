"use strict";
(function (root, factory) {
  const language = root && root.LegatoVoiceLanguage
    ? root.LegatoVoiceLanguage
    : (typeof require === "function" ? require("./legato-voice-language.js") : null);
  const localSpeech = root && root.LegatoLocalSpeechEngine
    ? root.LegatoLocalSpeechEngine
    : (typeof require === "function" ? require("./legato-local-speech-engine.js") : null);
  const api = factory(root, language, localSpeech);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.LegatoVoiceControl = api;
  if (root && root.document) api.install();
})(typeof globalThis !== "undefined" ? globalThis : this, function (root, VoiceLanguage, LocalSpeech) {
  const VERSION = "20260806-continuous-direct-1";
  const STORAGE_ALIASES = "legato.voice.aliases.v1";
  const STORAGE_CALIBRATION = "legato.voice.calibration.v2";
  const CALIBRATION_PROMPTS = Object.freeze([
    "Add a quarter note C sharp five",
    "Place staccato then move right",
    "Set tempo to one hundred twenty",
    "Add a fermata then play",
    "Go to bar three beat two"
  ]);

  const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
  const normalize = value => VoiceLanguage ? VoiceLanguage.normalize(value) : String(value || "").toLowerCase().trim();

  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function loadJSON(key, fallback) {
    try {
      const value = root.localStorage && root.localStorage.getItem(key);
      return value ? JSON.parse(value) : clone(fallback);
    } catch (_) { return clone(fallback); }
  }
  function saveJSON(key, value) {
    try { if (root.localStorage) root.localStorage.setItem(key, JSON.stringify(value)); } catch (_) {}
  }

  function setStateAsync(owner, patch) {
    return new Promise((resolve, reject) => {
      try { owner.setState(patch, resolve); }
      catch (error) { reject(error); }
    });
  }

  function pitchBase(value) {
    const match = String(value || "")
      .toUpperCase()
      .replace(/[♯♭♮#]/g, "")
      .replace(/SHARP|FLAT|NATURAL/g, "")
      .replace(/\s+/g, "")
      .match(/[A-G]-?\d/);
    return match ? match[0] : "";
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
      if (command.type === "voice-run" || command.type === "voice-clear") {
        command = Object.assign({}, command, { type: "invalid" });
        errors.push("Voice commands execute immediately. There is no pending command plan to run or clear.");
      }
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

  function accidentalID(name) { return name === "sharp" ? "sh" : name === "flat" ? "f" : "n"; }

  async function enterPitches(owner, command) {
    const basePos = Number(owner.state.pos) || 0;
    const pitches = command.preparedPitches || command.pitches || [];
    for (let index = 0; index < pitches.length; index++) {
      const pitch = pitches[index];
      if (pitch.step == null) throw new Error("Pitch " + pitch.label + " is outside the current staff range.");
      await setStateAsync(owner, {
        zone: 3, pos: basePos, step: pitch.step, dur: command.durationIndex,
        acc: accidentalID(pitch.accidental), entry: "note", selId: null, scoreObjectId: null
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
      case "duration": owner.setDur(command.durationIndex); return;
      case "accidental": owner.setAcc(command.accidental); return;
      case "tempo": await setStateAsync(owner, { tempo: command.bpm, spoken: "Tempo " + command.bpm }); return;
      case "mode": await setStateAsync(owner, { mode: command.mode, spoken: command.label }); return;
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
      case "chord": return enterPitches(owner, command);
      case "catalog":
        if (!command.glyph) throw new Error("Notation symbol was not resolved.");
        owner.applyCatalogCommand(command.glyph, command.glyph.label, command.glyph.glyph);
        await wait(80);
        return;
      default: throw new Error("Unsupported voice command: " + command.type);
    }
  }

  async function executePlan(owner, plan) {
    if (!plan || !plan.valid) throw new Error((plan && plan.errors && plan.errors.join(" ")) || "The spoken command is not safe to run.");
    for (const command of plan.commands) await executeCommand(owner, command);
    return true;
  }

  async function processTranscript(owner, text, options) {
    const o = options || {};
    if (!VoiceLanguage) throw new Error("The Legato voice language is unavailable.");
    const parsed = VoiceLanguage.parsePlan(text, { aliases: o.aliases || {} });
    const prepared = preparePlan(owner, parsed, o.catalog || { glyphs: [] });
    if (!prepared.valid) return { executed: false, plan: prepared, errors: prepared.errors.slice() };
    await executePlan(owner, prepared);
    return { executed: true, plan: prepared, labels: prepared.commands.map(command => command.label) };
  }

  function isServiceRefusalError(error) {
    const value = typeof error === "string" ? error : error && (error.error || error.message);
    return /service-not-allowed|language-not-supported|service unavailable/i.test(String(value || ""));
  }

  function shouldUseLocalEngine(scope) {
    const s = scope || root || {};
    const nav = s.navigator || {};
    return !!(LocalSpeech && LocalSpeech.isIPadLike(nav)) || !(LocalSpeech && LocalSpeech.hasNativeSpeechRecognition(s));
  }

  const state = {
    installed: false,
    panelOpen: false,
    desiredListening: false,
    listening: false,
    engineKind: "none",
    recognition: null,
    localEngine: null,
    transcript: "",
    status: "Voice control is ready.",
    history: [],
    aliases: loadJSON(STORAGE_ALIASES, {}),
    calibration: loadJSON(STORAGE_CALIBRATION, { completed: 0 }),
    calibrationExpected: null,
    observer: null,
    restartTimer: null,
    lastFinal: "",
    lastFinalAt: 0,
    executionQueue: Promise.resolve()
  };

  function owner() { return root.__legatoOwner || null; }
  function catalog() { return root.LEGATO_SMUFL_CATALOG || { glyphs: [] }; }
  function panelElement() { return root.document && root.document.getElementById("legato-voice-panel"); }

  function addHistory(text, result, error) {
    state.history.unshift({
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      text: String(text || ""),
      result: result || "",
      error: error || ""
    });
    state.history = state.history.slice(0, 16);
  }

  function button(label, action, primary) {
    const el = root.document.createElement("button");
    el.type = "button";
    el.textContent = label;
    el.setAttribute("data-ptr", label);
    el.style.cssText = "border:1px solid " + (primary ? "var(--accent)" : "var(--border-strong)") + ";background:" + (primary ? "var(--accent)" : "var(--control)") + ";color:" + (primary ? "var(--bg)" : "var(--text)") + ";padding:8px 11px;border-radius:5px;font:600 12px var(--ui-font);cursor:pointer;";
    el.addEventListener("click", action);
    return el;
  }

  function render() {
    const panel = panelElement();
    if (!panel) return;
    panel.style.display = state.panelOpen ? "flex" : "none";
    const status = panel.querySelector("[data-voice-status]");
    const transcript = panel.querySelector("[data-voice-transcript]");
    const engine = panel.querySelector("[data-voice-engine]");
    const start = panel.querySelector("[data-voice-start]");
    const calibration = panel.querySelector("[data-voice-calibration]");
    const history = panel.querySelector("[data-voice-history]");
    if (status) status.textContent = state.status;
    if (transcript) transcript.textContent = state.transcript || "Listening has not heard a complete command yet.";
    if (engine) engine.textContent = "ENGINE  " + (state.engineKind === "local" ? "ON-DEVICE" : state.engineKind === "native" ? "SYSTEM" : "OFF");
    if (start) start.textContent = state.desiredListening ? "Stop voice control" : "Start voice control";
    if (calibration) {
      calibration.textContent = state.calibrationExpected
        ? "Read this phrase: “" + state.calibrationExpected + "”"
        : "Voice setup: " + Math.min(state.calibration.completed || 0, CALIBRATION_PROMPTS.length) + "/" + CALIBRATION_PROMPTS.length + " phrases";
    }
    if (history) {
      history.replaceChildren();
      if (!state.history.length) {
        const empty = root.document.createElement("div");
        empty.textContent = "No spoken commands yet.";
        empty.style.color = "var(--muted)";
        history.appendChild(empty);
      } else {
        state.history.forEach(item => {
          const row = root.document.createElement("div");
          row.style.cssText = "display:grid;grid-template-columns:52px minmax(140px,1fr) minmax(160px,1fr);gap:10px;padding:7px 0;border-bottom:1px solid var(--border);align-items:start;";
          const time = root.document.createElement("span"); time.textContent = item.time; time.style.cssText = "font-family:'IBM Plex Mono',monospace;color:var(--muted);font-size:10px;";
          const heard = root.document.createElement("span"); heard.textContent = item.text;
          const result = root.document.createElement("span"); result.textContent = item.error || item.result; result.style.color = item.error ? "#e58f82" : "var(--accent)";
          row.append(time, heard, result); history.appendChild(row);
        });
      }
    }
  }

  function acceptFinalTranscript(text) {
    const clean = String(text || "").trim();
    if (!clean) return false;
    const now = Date.now();
    if (normalize(clean) === normalize(state.lastFinal) && now - state.lastFinalAt < 1800) return false;
    state.lastFinal = clean;
    state.lastFinalAt = now;
    handleFinalTranscript(clean);
    return true;
  }

  function handleFinalTranscript(text) {
    state.transcript = String(text || "").trim();
    if (state.calibrationExpected) {
      const expected = state.calibrationExpected;
      if (state.transcript && normalize(state.transcript) !== normalize(expected)) state.aliases[state.transcript] = expected;
      state.calibration.completed = Math.min(CALIBRATION_PROMPTS.length, (state.calibration.completed || 0) + 1);
      saveJSON(STORAGE_ALIASES, state.aliases);
      saveJSON(STORAGE_CALIBRATION, state.calibration);
      state.calibrationExpected = null;
      state.status = "Voice setup phrase saved. Listening for commands.";
      addHistory(state.transcript, "Voice setup phrase saved", "");
      render();
      return;
    }

    state.status = "Executing: “" + state.transcript + "”";
    render();
    state.executionQueue = state.executionQueue.then(async () => {
      try {
        const result = await processTranscript(owner(), text, { aliases: state.aliases, catalog: catalog() });
        if (!result.executed) {
          const message = result.errors.join(" ") || "Command not recognized.";
          state.status = "Not executed: " + message;
          addHistory(text, "", message);
        } else {
          const completed = result.labels.join(" → ");
          state.status = "Completed: " + completed;
          addHistory(text, completed, "");
          const o = owner();
          if (o && typeof o.setState === "function") o.setState({ spoken: "Voice command completed: " + completed });
        }
      } catch (error) {
        const message = error && error.message ? error.message : String(error);
        state.status = "Voice command stopped: " + message;
        addHistory(text, "", message);
      }
      render();
    });
  }

  function nativeConstructor() { return root.SpeechRecognition || root.webkitSpeechRecognition || null; }

  function startNativeEngine() {
    const SpeechRecognition = nativeConstructor();
    if (!SpeechRecognition) return startLocalEngine();
    let recognition;
    try {
      recognition = new SpeechRecognition();
      recognition.lang = root.navigator && root.navigator.language ? root.navigator.language : "en-US";
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;
      recognition.onstart = () => {
        state.listening = true;
        state.engineKind = "native";
        state.status = "Listening continuously. Speak a Legato command.";
        render();
      };
      recognition.onresult = event => {
        let interim = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const alternative = event.results[i][0];
          const spoken = alternative && alternative.transcript ? alternative.transcript.trim() : "";
          if (!spoken) continue;
          if (event.results[i].isFinal) acceptFinalTranscript(spoken);
          else interim += (interim ? " " : "") + spoken;
        }
        if (interim) { state.transcript = interim; render(); }
      };
      recognition.onerror = event => {
        if (isServiceRefusalError(event)) {
          state.status = "The system speech service refused this session. Switching to Legato’s on-device voice engine…";
          render();
          state.engineKind = "switching";
          try { recognition.abort(); } catch (_) {}
          state.recognition = null;
          startLocalEngine();
          return;
        }
        const code = event && event.error ? event.error : "unknown error";
        if (code === "no-speech" || code === "aborted") return;
        state.status = code === "not-allowed"
          ? "Microphone access was denied for Legato."
          : "System voice recognition error: " + code + ".";
        if (code === "not-allowed") state.desiredListening = false;
        render();
      };
      recognition.onend = () => {
        state.listening = false;
        state.recognition = null;
        if (state.desiredListening && state.engineKind === "native") {
          if (state.restartTimer) root.clearTimeout(state.restartTimer);
          state.restartTimer = root.setTimeout(() => startNativeEngine(), 250);
        } else render();
      };
      state.recognition = recognition;
      state.engineKind = "native";
      recognition.start();
    } catch (error) {
      if (isServiceRefusalError(error)) return startLocalEngine();
      state.status = "System voice recognition could not start. Switching to the on-device engine…";
      render();
      return startLocalEngine();
    }
  }

  async function startLocalEngine() {
    if (!LocalSpeech || !LocalSpeech.LocalWhisperEngine) {
      state.desiredListening = false;
      state.status = "The on-device voice engine is unavailable in this build.";
      render();
      return;
    }
    if (state.localEngine) await state.localEngine.stop();
    state.engineKind = "local";
    state.localEngine = new LocalSpeech.LocalWhisperEngine({
      scope: root,
      onStatus: message => { state.status = message; render(); },
      onInterim: text => { state.transcript = text; render(); },
      onTranscript: text => acceptFinalTranscript(text)
    });
    try {
      await state.localEngine.start();
      state.listening = !!state.localEngine.running;
      render();
    } catch (error) {
      state.listening = false;
      state.desiredListening = false;
      state.status = "On-device voice control could not start: " + (error && error.message ? error.message : String(error));
      render();
    }
  }

  async function startListening() {
    if (state.desiredListening) return stopListening();
    state.desiredListening = true;
    state.status = "Starting continuous voice control…";
    render();
    if (shouldUseLocalEngine(root)) await startLocalEngine();
    else startNativeEngine();
  }

  async function stopListening() {
    state.desiredListening = false;
    state.listening = false;
    if (state.restartTimer) root.clearTimeout(state.restartTimer);
    state.restartTimer = null;
    if (state.recognition) { try { state.recognition.abort(); } catch (_) {} }
    state.recognition = null;
    if (state.localEngine) { await state.localEngine.stop(); state.localEngine = null; }
    state.engineKind = "none";
    state.status = "Voice control stopped.";
    render();
  }

  function startCalibration() {
    const completed = Number(state.calibration.completed || 0);
    if (completed >= CALIBRATION_PROMPTS.length) state.calibration = { completed: 0 };
    state.calibrationExpected = CALIBRATION_PROMPTS[state.calibration.completed || 0] || CALIBRATION_PROMPTS[0];
    state.status = "Read the displayed phrase. Legato will save the pronunciation and continue listening.";
    render();
    if (!state.desiredListening) startListening();
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

    const header = root.document.createElement("div"); header.style.cssText = "display:flex;align-items:flex-start;gap:12px;";
    const titleWrap = root.document.createElement("div"); titleWrap.style.flex = "1";
    const title = root.document.createElement("h2"); title.textContent = "Voice control"; title.style.cssText = "margin:0 0 4px;font-size:22px;";
    const subtitle = root.document.createElement("div"); subtitle.textContent = "Start once, then speak naturally. Complete commands execute immediately."; subtitle.style.color = "var(--muted)";
    titleWrap.append(title, subtitle);
    const close = button("Close voice control", () => { state.panelOpen = false; render(); }, false);
    header.append(titleWrap, close);

    const statusRow = root.document.createElement("div"); statusRow.style.cssText = "display:flex;gap:8px;align-items:center;";
    const status = root.document.createElement("div"); status.setAttribute("data-voice-status", ""); status.style.cssText = "flex:1;padding:9px 11px;background:var(--raised);border:1px solid var(--border);border-radius:5px;";
    const engine = root.document.createElement("div"); engine.setAttribute("data-voice-engine", ""); engine.style.cssText = "font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.08em;padding:9px;border:1px solid var(--border);border-radius:5px;color:var(--muted);";
    statusRow.append(status, engine);

    const calibration = root.document.createElement("div"); calibration.setAttribute("data-voice-calibration", ""); calibration.style.cssText = "font-size:12px;color:var(--text-2);";
    const controls = root.document.createElement("div"); controls.style.cssText = "display:flex;flex-wrap:wrap;gap:8px;";
    const start = button("Start voice control", startListening, true); start.setAttribute("data-voice-start", "");
    controls.append(start, button("Set up my voice", startCalibration, false), button("Reset voice setup", resetVoiceSetup, false));

    const transcriptTitle = root.document.createElement("h3"); transcriptTitle.textContent = "Live speech"; transcriptTitle.style.cssText = "margin:4px 0 0;font-size:14px;";
    const transcript = root.document.createElement("div"); transcript.setAttribute("data-voice-transcript", ""); transcript.style.cssText = "min-height:48px;padding:10px;background:var(--input-bg);border:1px solid var(--border);border-radius:5px;white-space:pre-wrap;";
    const historyTitle = root.document.createElement("h3"); historyTitle.textContent = "Recent commands"; historyTitle.style.cssText = "margin:4px 0 0;font-size:14px;";
    const history = root.document.createElement("div"); history.setAttribute("data-voice-history", ""); history.style.cssText = "padding:10px;background:var(--raised);border:1px solid var(--border);border-radius:5px;";
    const help = root.document.createElement("div"); help.textContent = "Examples: “add C sharp five quarter note”, “place staccato”, “move right four times”, “tempo 120 then play”."; help.style.cssText = "font-size:11px;color:var(--muted);";

    panel.append(header, statusRow, calibration, controls, transcriptTitle, transcript, historyTitle, history, help);
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
    const stale = root.document.getElementById("legato-ipad-dictation-fallback");
    if (stale) stale.remove();
    createPanel();
    attachLauncher();
    state.observer = new root.MutationObserver(() => attachLauncher());
    state.observer.observe(root.document.documentElement, { childList: true, subtree: true });
    render();
    root.__LEGATO_VOICE_CONTROL__ = {
      version: VERSION,
      open: () => { state.panelOpen = true; render(); },
      close: () => { state.panelOpen = false; render(); },
      start: startListening,
      stop: stopListening,
      state
    };
    return true;
  }

  async function destroy() {
    await stopListening();
    if (state.observer) state.observer.disconnect();
    state.observer = null;
    const panel = panelElement(); if (panel) panel.remove();
    const launcher = root.document && root.document.getElementById("legato-voice-launcher"); if (launcher) launcher.remove();
    state.installed = false;
  }

  return {
    VERSION, CALIBRATION_PROMPTS,
    pitchBase, pitchStep, resolveCatalogCommand, preparePlan,
    executeCommand, executePlan, processTranscript, setStateAsync,
    isServiceRefusalError, shouldUseLocalEngine,
    acceptFinalTranscript, handleFinalTranscript,
    startListening, stopListening, install, destroy, state
  };
});
