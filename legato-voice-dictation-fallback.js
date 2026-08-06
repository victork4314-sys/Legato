"use strict";
(function (root, factory) {
  const language = root && root.LegatoVoiceLanguage
    ? root.LegatoVoiceLanguage
    : (typeof require === "function" ? require("./legato-voice-language.js") : null);
  const control = root && root.LegatoVoiceControl
    ? root.LegatoVoiceControl
    : (typeof require === "function" ? require("./legato-voice-control.js") : null);
  const api = factory(root, language, control);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.LegatoVoiceDictationFallback = api;
  if (root && root.document) api.install();
})(typeof globalThis !== "undefined" ? globalThis : this, function (root, VoiceLanguage, VoiceControl) {
  const VERSION = "20260806-ipad-dictation-fallback-1";
  const FRIENDLY_SERVICE_MESSAGE = "Safari's speech-recognition service is unavailable here. Use iPad Dictation below, then preview the dictated command.";

  function isIPadLike(navigatorObject) {
    const nav = navigatorObject || {};
    const ua = String(nav.userAgent || "");
    return /iPad/i.test(ua) || (/Macintosh/i.test(ua) && Number(nav.maxTouchPoints || 0) > 1);
  }

  function isServiceRefusal(message) {
    return /service-not-allowed|speech recognition is not available|voice recognition is not available/i.test(String(message || ""));
  }

  function shouldShowFallback(message, navigatorObject) {
    return isIPadLike(navigatorObject) || isServiceRefusal(message);
  }

  function buildDictationPlan(text, owner, catalog, aliases) {
    if (!VoiceLanguage || !VoiceControl) throw new Error("Legato voice control is not ready.");
    const transcript = String(text || "").trim();
    if (!transcript) {
      return {
        transcript,
        normalized: "",
        commands: [],
        valid: false,
        errors: ["Dictate or type a Legato command first."]
      };
    }
    const parsed = VoiceLanguage.parsePlan(transcript, { aliases: aliases || {} });
    if (parsed.commands.length === 1 && /^(voice-run|voice-clear)$/.test(parsed.commands[0].type)) {
      return Object.assign({}, parsed, {
        valid: false,
        errors: ["Use the Run commands or Clear preview button after previewing dictated text."]
      });
    }
    return VoiceControl.preparePlan(owner, parsed, catalog || { glyphs: [] });
  }

  function applyPlanToState(controlState, plan, transcript) {
    if (!controlState) throw new Error("Voice-control state is unavailable.");
    controlState.pending = plan;
    controlState.transcript = String(transcript || "").trim();
    controlState.status = plan && plan.valid
      ? "Review the dictated command plan, then run it."
      : ((plan && plan.errors && plan.errors.join(" ")) || "The dictated command was blocked.");
    return controlState;
  }

  function createButton(documentObject, label, primary, handler) {
    const button = documentObject.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.setAttribute("data-ptr", label);
    button.style.cssText = "border:1px solid " + (primary ? "var(--accent)" : "var(--border-strong)") + ";background:" + (primary ? "var(--accent)" : "var(--control)") + ";color:" + (primary ? "var(--bg)" : "var(--text)") + ";padding:8px 11px;border-radius:5px;font:600 12px var(--ui-font);cursor:pointer;";
    button.addEventListener("click", handler);
    return button;
  }

  function renderExistingPreview(documentObject, controlState) {
    const status = documentObject.querySelector("[data-voice-status]");
    const transcript = documentObject.querySelector("[data-voice-transcript]");
    const preview = documentObject.querySelector("[data-voice-preview]");
    const run = documentObject.querySelector("[data-voice-run]");
    if (status) status.textContent = controlState.status;
    if (transcript) transcript.textContent = controlState.transcript || "Your speech will appear here.";
    if (run) run.disabled = !controlState.pending || !controlState.pending.valid;
    if (!preview) return;

    preview.replaceChildren();
    const plan = controlState.pending;
    if (!plan || !Array.isArray(plan.commands) || !plan.commands.length) {
      const empty = documentObject.createElement("div");
      empty.textContent = "Nothing is queued.";
      empty.style.color = "var(--muted)";
      preview.appendChild(empty);
      return;
    }

    plan.commands.forEach((command, index) => {
      const row = documentObject.createElement("div");
      row.style.cssText = "display:flex;gap:9px;padding:7px 0;border-bottom:1px solid var(--border);align-items:flex-start;";
      const number = documentObject.createElement("span");
      number.textContent = String(index + 1);
      number.style.cssText = "font-family:'IBM Plex Mono',monospace;color:var(--muted);";
      const label = documentObject.createElement("span");
      label.textContent = command.label;
      label.style.flex = "1";
      row.append(number, label);
      preview.appendChild(row);
    });

    if (Array.isArray(plan.errors) && plan.errors.length) {
      const error = documentObject.createElement("div");
      error.textContent = plan.errors.join(" ");
      error.style.cssText = "padding-top:8px;color:#e58f82;";
      preview.appendChild(error);
    }
  }

  function installPanelFallback(documentObject, navigatorObject) {
    const panel = documentObject.getElementById("legato-voice-panel");
    if (!panel || documentObject.getElementById("legato-ipad-dictation-fallback")) return false;

    const section = documentObject.createElement("section");
    section.id = "legato-ipad-dictation-fallback";
    section.setAttribute("aria-label", "iPad Dictation fallback");
    section.style.cssText = "display:none;flex-direction:column;gap:8px;padding:12px;background:var(--raised);border:1px solid var(--border-strong);border-radius:6px;";

    const title = documentObject.createElement("h3");
    title.textContent = "iPad Dictation";
    title.style.cssText = "margin:0;font-size:14px;";
    const explanation = documentObject.createElement("div");
    explanation.textContent = "Tap the field, use the microphone key on the iPad keyboard, then preview the dictated command. Nothing changes in the score until Run commands is pressed.";
    explanation.style.cssText = "font-size:12px;color:var(--text-2);";

    const input = documentObject.createElement("textarea");
    input.id = "legato-dictation-command";
    input.rows = 3;
    input.placeholder = "Dictate or type a command, for example: add C sharp five quarter note";
    input.setAttribute("aria-label", "Dictated Legato command");
    input.setAttribute("data-ptr", "Dictated Legato command");
    input.setAttribute("enterkeyhint", "done");
    input.setAttribute("autocapitalize", "sentences");
    input.setAttribute("autocomplete", "off");
    input.setAttribute("spellcheck", "true");
    input.style.cssText = "width:100%;min-height:76px;box-sizing:border-box;resize:vertical;padding:10px;background:var(--input-bg);color:var(--text);border:1px solid var(--border);border-radius:5px;font:14px var(--ui-font);";

    const controls = documentObject.createElement("div");
    controls.style.cssText = "display:flex;flex-wrap:wrap;gap:8px;";
    const focusButton = createButton(documentObject, "Use iPad dictation", false, () => {
      section.style.display = "flex";
      input.focus();
      try { input.setSelectionRange(input.value.length, input.value.length); } catch (_) {}
    });
    const previewButton = createButton(documentObject, "Preview dictated command", true, () => {
      try {
        const owner = root.__legatoOwner || null;
        const catalog = root.LEGATO_SMUFL_CATALOG || { glyphs: [] };
        const aliases = VoiceControl.state && VoiceControl.state.aliases || {};
        const plan = buildDictationPlan(input.value, owner, catalog, aliases);
        applyPlanToState(VoiceControl.state, plan, input.value);
        renderExistingPreview(documentObject, VoiceControl.state);
      } catch (error) {
        VoiceControl.state.status = "Dictation preview failed: " + (error && error.message ? error.message : String(error));
        renderExistingPreview(documentObject, VoiceControl.state);
      }
    });
    controls.append(focusButton, previewButton);
    section.append(title, explanation, input, controls);

    const transcriptTitle = panel.querySelector("h3");
    panel.insertBefore(section, transcriptTitle || panel.children[3] || null);

    const updateVisibility = () => {
      const status = documentObject.querySelector("[data-voice-status]");
      const text = status ? status.textContent : "";
      const show = shouldShowFallback(text, navigatorObject);
      section.style.display = show ? "flex" : "none";
      if (isServiceRefusal(text) && status && status.textContent !== FRIENDLY_SERVICE_MESSAGE) {
        VoiceControl.state.status = FRIENDLY_SERVICE_MESSAGE;
        status.textContent = FRIENDLY_SERVICE_MESSAGE;
      }
    };

    const observer = new MutationObserver(updateVisibility);
    observer.observe(panel, { childList: true, subtree: true, characterData: true });
    updateVisibility();
    root.__LEGATO_IPAD_DICTATION_FALLBACK__ = { version: VERSION, observer, section, input };
    return true;
  }

  function install() {
    if (!root || !root.document || !VoiceLanguage || !VoiceControl) return false;
    if (root.__LEGATO_IPAD_DICTATION_FALLBACK__ && root.__LEGATO_IPAD_DICTATION_FALLBACK__.version === VERSION) return true;
    if (installPanelFallback(root.document, root.navigator)) return true;
    let attempts = 0;
    const timer = root.setInterval(() => {
      if (installPanelFallback(root.document, root.navigator) || ++attempts > 240) root.clearInterval(timer);
    }, 50);
    return true;
  }

  return {
    VERSION,
    FRIENDLY_SERVICE_MESSAGE,
    isIPadLike,
    isServiceRefusal,
    shouldShowFallback,
    buildDictationPlan,
    applyPlanToState,
    renderExistingPreview,
    installPanelFallback,
    install
  };
});
