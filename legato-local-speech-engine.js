"use strict";
(function (root, factory) {
  const api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.LegatoLocalSpeechEngine = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (root) {
  const VERSION = "20260806-local-whisper-1";
  const TARGET_RATE = 16000;
  const MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en-q5_1.bin";
  const MODEL_NAME = "ggml-tiny.en-q5_1.bin";
  const MODEL_SHA256 = "c77c5766f1cef09b6b7d47f21b546cbddd4157886b3b5d6d4f709e91e66c7c2b";
  const CACHE_NAME = "legato-whisper-model-v1";
  const MAX_AUDIO_SECONDS = 30;

  function isIPadLike(nav) {
    const n = nav || {};
    const ua = String(n.userAgent || "");
    return /iPad/i.test(ua) || (/Macintosh/i.test(ua) && Number(n.maxTouchPoints || 0) > 1);
  }

  function hasNativeSpeechRecognition(scope) {
    const s = scope || {};
    return !!(s.SpeechRecognition || s.webkitSpeechRecognition);
  }

  function downsampleTo16k(input, inputRate) {
    const source = input instanceof Float32Array ? input : new Float32Array(input || []);
    const rate = Number(inputRate) || TARGET_RATE;
    if (!source.length) return new Float32Array(0);
    if (rate === TARGET_RATE) return new Float32Array(source);
    const ratio = rate / TARGET_RATE;
    const outputLength = Math.max(1, Math.floor(source.length / ratio));
    const output = new Float32Array(outputLength);
    for (let i = 0; i < outputLength; i++) {
      const start = Math.floor(i * ratio);
      const end = Math.min(source.length, Math.max(start + 1, Math.floor((i + 1) * ratio)));
      let sum = 0;
      for (let j = start; j < end; j++) sum += source[j];
      output[i] = sum / Math.max(1, end - start);
    }
    return output;
  }

  function appendRollingAudio(existing, chunk, maxSamples) {
    const oldData = existing instanceof Float32Array ? existing : new Float32Array(existing || []);
    const newData = chunk instanceof Float32Array ? chunk : new Float32Array(chunk || []);
    const limit = Math.max(1, Number(maxSamples) || TARGET_RATE * MAX_AUDIO_SECONDS);
    if (newData.length >= limit) return newData.slice(newData.length - limit);
    const keep = Math.min(oldData.length, limit - newData.length);
    const out = new Float32Array(keep + newData.length);
    if (keep) out.set(oldData.subarray(oldData.length - keep), 0);
    out.set(newData, keep);
    return out;
  }

  function normalizeTranscript(value) {
    return String(value || "").trim().replace(/\s+/g, " ");
  }

  function hexFromBuffer(buffer) {
    return Array.from(new Uint8Array(buffer)).map(value => value.toString(16).padStart(2, "0")).join("");
  }

  async function sha256Hex(buffer, cryptoObject) {
    const c = cryptoObject || (root && root.crypto);
    if (!c || !c.subtle || typeof c.subtle.digest !== "function") throw new Error("SHA-256 verification is unavailable in this browser.");
    return hexFromBuffer(await c.subtle.digest("SHA-256", buffer));
  }

  async function verifySHA256(buffer, expected, cryptoObject) {
    const actual = await sha256Hex(buffer, cryptoObject);
    if (actual !== String(expected || "").toLowerCase()) throw new Error("The on-device speech model failed its SHA-256 integrity check.");
    return true;
  }

  class TranscriptGate {
    constructor(options) {
      const o = options || {};
      this.stableMs = Number(o.stableMs) || 500;
      this.dedupeMs = Number(o.dedupeMs) || 2200;
      this.candidate = "";
      this.candidateAt = 0;
      this.lastEmitted = "";
      this.lastEmittedAt = 0;
    }
    resetCandidate() { this.candidate = ""; this.candidateAt = 0; }
    observe(value, now) {
      const text = normalizeTranscript(value);
      const time = Number(now == null ? Date.now() : now);
      if (!text) { this.resetCandidate(); return null; }
      if (text !== this.candidate) {
        this.candidate = text;
        this.candidateAt = time;
        return null;
      }
      if (time - this.candidateAt < this.stableMs) return null;
      if (text === this.lastEmitted && time - this.lastEmittedAt < this.dedupeMs) return null;
      this.lastEmitted = text;
      this.lastEmittedAt = time;
      this.resetCandidate();
      return text;
    }
  }

  function loadScript(documentObject, src, marker) {
    return new Promise((resolve, reject) => {
      const existing = documentObject.querySelector('script[' + marker + '="true"]');
      if (existing) {
        if (existing.getAttribute("data-loaded") === "true") return resolve();
        existing.addEventListener("load", resolve, { once: true });
        existing.addEventListener("error", () => reject(new Error("Could not load " + src)), { once: true });
        return;
      }
      const script = documentObject.createElement("script");
      script.src = src;
      script.async = true;
      script.setAttribute(marker, "true");
      script.addEventListener("load", () => { script.setAttribute("data-loaded", "true"); resolve(); }, { once: true });
      script.addEventListener("error", () => reject(new Error("Could not load " + src)), { once: true });
      documentObject.head.appendChild(script);
    });
  }

  async function fetchModelArrayBuffer(scope, onStatus) {
    const s = scope || root;
    const status = typeof onStatus === "function" ? onStatus : function () {};
    const request = new s.Request(MODEL_URL, { mode: "cors", credentials: "omit" });
    if (s.caches) {
      const cache = await s.caches.open(CACHE_NAME);
      const cached = await cache.match(request);
      if (cached) {
        status("Loading the cached on-device speech model…");
        const buffer = await cached.arrayBuffer();
        await verifySHA256(buffer, MODEL_SHA256, s.crypto);
        return buffer;
      }
    }
    status("Downloading the on-device speech model once, about 31 MB…");
    const response = await s.fetch(request);
    if (!response.ok) throw new Error("The on-device speech model download failed with HTTP " + response.status + ".");
    const clone = response.clone();
    const buffer = await response.arrayBuffer();
    await verifySHA256(buffer, MODEL_SHA256, s.crypto);
    if (s.caches) {
      const cache = await s.caches.open(CACHE_NAME);
      await cache.put(request, clone);
    }
    return buffer;
  }

  class LocalWhisperEngine {
    constructor(options) {
      const o = options || {};
      this.scope = o.scope || root;
      this.document = o.document || (this.scope && this.scope.document);
      this.navigator = o.navigator || (this.scope && this.scope.navigator);
      this.moduleURL = o.moduleURL || "./vendor/whisper-command/command.js";
      this.workerBase = o.workerBase || "./vendor/whisper-command/";
      this.module = o.module || null;
      this.audioContextFactory = o.audioContextFactory || null;
      this.getUserMedia = o.getUserMedia || null;
      this.modelLoader = o.modelLoader || null;
      this.clock = o.clock || (() => Date.now());
      this.onTranscript = o.onTranscript || function () {};
      this.onInterim = o.onInterim || function () {};
      this.onStatus = o.onStatus || function () {};
      this.running = false;
      this.starting = false;
      this.instance = null;
      this.stream = null;
      this.audioContext = null;
      this.sourceNode = null;
      this.processorNode = null;
      this.silentGain = null;
      this.audio = new Float32Array(0);
      this.feedTimer = null;
      this.pollTimer = null;
      this.gate = new TranscriptGate();
    }

    async ensureIsolation() {
      const s = this.scope;
      if (!s || s.crossOriginIsolated) return true;
      if (!this.navigator || !this.navigator.serviceWorker) throw new Error("This browser cannot enable the isolated audio engine required for on-device voice control.");
      this.onStatus("Preparing the on-device voice engine. Legato may reload once…");
      const registration = await this.navigator.serviceWorker.register("./coi-serviceworker.js", { scope: "./" });
      await this.navigator.serviceWorker.ready;
      if (!this.navigator.serviceWorker.controller) {
        const key = "legato.voice.coi.reload";
        let already = false;
        try { already = s.sessionStorage && s.sessionStorage.getItem(key) === "1"; } catch (_) {}
        if (!already) {
          try { if (s.sessionStorage) s.sessionStorage.setItem(key, "1"); } catch (_) {}
          s.location.reload();
          return false;
        }
      }
      if (!s.crossOriginIsolated) throw new Error("The on-device voice engine could not enable cross-origin isolation after its service-worker setup.");
      return !!registration;
    }

    async ensureModule() {
      if (this.module && typeof this.module.init === "function") return this.module;
      if (!this.document) throw new Error("The on-device voice engine requires a browser document.");
      const s = this.scope;
      this.onStatus("Loading the on-device speech engine…");
      let resolveRuntime;
      let rejectRuntime;
      const runtimeReady = new Promise((resolve, reject) => { resolveRuntime = resolve; rejectRuntime = reject; });
      const configured = {
        locateFile: path => this.workerBase + path,
        print: text => { if (/error/i.test(String(text || ""))) this.onStatus(String(text)); },
        printErr: text => { if (text) this.onStatus(String(text)); },
        onRuntimeInitialized: () => resolveRuntime(s.Module)
      };
      s.Module = configured;
      try {
        await loadScript(this.document, this.moduleURL, "data-legato-whisper-command");
        const timeout = new Promise((_, reject) => s.setTimeout(() => reject(new Error("The on-device speech engine timed out while loading.")), 30000));
        this.module = await Promise.race([runtimeReady, timeout]);
      } catch (error) {
        rejectRuntime(error);
        throw error;
      }
      if (!this.module || typeof this.module.init !== "function" || typeof this.module.set_audio !== "function" || typeof this.module.get_transcribed !== "function") {
        throw new Error("The generated on-device speech engine is missing its required command API.");
      }
      return this.module;
    }

    async installModel() {
      const loader = this.modelLoader || (() => fetchModelArrayBuffer(this.scope, message => this.onStatus(message)));
      const buffer = await loader();
      const bytes = new Uint8Array(buffer);
      try { this.module.FS_unlink("/" + MODEL_NAME); } catch (_) {}
      this.module.FS_createDataFile("/", MODEL_NAME, bytes, true, true);
      this.instance = this.module.init(MODEL_NAME);
      if (!this.instance) throw new Error("The on-device speech model could not initialize.");
    }

    async start() {
      if (this.running || this.starting) return;
      this.starting = true;
      try {
        const isolated = await this.ensureIsolation();
        if (!isolated) return;
        await this.ensureModule();
        await this.installModel();
        const gum = this.getUserMedia || (constraints => this.navigator.mediaDevices.getUserMedia(constraints));
        this.onStatus("Requesting microphone access for continuous voice control…");
        this.stream = await gum({ audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true, autoGainControl: true }, video: false });
        const AudioContextClass = this.audioContextFactory || this.scope.AudioContext || this.scope.webkitAudioContext;
        if (!AudioContextClass) throw new Error("Web Audio is unavailable in this browser.");
        this.audioContext = this.audioContextFactory ? this.audioContextFactory() : new AudioContextClass();
        if (this.audioContext.state === "suspended") await this.audioContext.resume();
        this.sourceNode = this.audioContext.createMediaStreamSource(this.stream);
        this.processorNode = this.audioContext.createScriptProcessor(4096, 1, 1);
        this.silentGain = this.audioContext.createGain();
        this.silentGain.gain.value = 0;
        this.processorNode.onaudioprocess = event => {
          if (!this.running) return;
          const channel = event.inputBuffer.getChannelData(0);
          const downsampled = downsampleTo16k(channel, this.audioContext.sampleRate);
          this.audio = appendRollingAudio(this.audio, downsampled, TARGET_RATE * MAX_AUDIO_SECONDS);
        };
        this.sourceNode.connect(this.processorNode);
        this.processorNode.connect(this.silentGain);
        this.silentGain.connect(this.audioContext.destination);
        this.running = true;
        this.feedTimer = this.scope.setInterval(() => this.feedAudio(), 250);
        this.pollTimer = this.scope.setInterval(() => this.pollTranscript(), 100);
        this.onStatus("Listening continuously with the on-device speech engine.");
      } catch (error) {
        await this.stop();
        throw error;
      } finally {
        this.starting = false;
      }
    }

    feedAudio() {
      if (!this.running || !this.instance || this.audio.length < TARGET_RATE / 2) return;
      this.module.set_audio(this.instance, this.audio);
    }

    pollTranscript() {
      if (!this.running || !this.instance) return;
      let raw = "";
      try { raw = normalizeTranscript(this.module.get_transcribed()); } catch (_) { return; }
      if (!raw) return;
      this.onInterim(raw);
      const finalText = this.gate.observe(raw, this.clock());
      if (!finalText) return;
      this.audio = new Float32Array(0);
      this.onTranscript(finalText);
    }

    async stop() {
      this.running = false;
      if (this.feedTimer != null) this.scope.clearInterval(this.feedTimer);
      if (this.pollTimer != null) this.scope.clearInterval(this.pollTimer);
      this.feedTimer = null;
      this.pollTimer = null;
      if (this.processorNode) { this.processorNode.onaudioprocess = null; try { this.processorNode.disconnect(); } catch (_) {} }
      if (this.sourceNode) { try { this.sourceNode.disconnect(); } catch (_) {} }
      if (this.silentGain) { try { this.silentGain.disconnect(); } catch (_) {} }
      if (this.stream) this.stream.getTracks().forEach(track => track.stop());
      if (this.audioContext && typeof this.audioContext.close === "function") { try { await this.audioContext.close(); } catch (_) {} }
      this.stream = null;
      this.audioContext = null;
      this.sourceNode = null;
      this.processorNode = null;
      this.silentGain = null;
      this.audio = new Float32Array(0);
      this.gate.resetCandidate();
      this.onStatus("Voice control stopped.");
    }
  }

  return {
    VERSION, TARGET_RATE, MODEL_URL, MODEL_NAME, MODEL_SHA256, CACHE_NAME, MAX_AUDIO_SECONDS,
    isIPadLike, hasNativeSpeechRecognition, downsampleTo16k, appendRollingAudio,
    normalizeTranscript, sha256Hex, verifySHA256, TranscriptGate, fetchModelArrayBuffer,
    LocalWhisperEngine
  };
});
