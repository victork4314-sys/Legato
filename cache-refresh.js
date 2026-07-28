"use strict";
(() => {
  const CHECK_EVERY_MS = 30000;
  const FALLBACK_BUILD = "20260728-musicxml-1";
  const currentScript = document.currentScript;
  let LOADER_BUILD = FALLBACK_BUILD;
  try {
    if (currentScript && currentScript.src) LOADER_BUILD = new URL(currentScript.src, location.href).searchParams.get('v') || FALLBACK_BUILD;
  } catch (_) {}

  if (window.__legatoLoaderBuild === LOADER_BUILD) return;
  window.__legatoLoaderBuild = LOADER_BUILD;

  function loadScript(src, marker, onload, build) {
    const version = build || LOADER_BUILD;
    if (document.querySelector('script[' + marker + '="' + version + '"]')) {
      if (onload) onload();
      return;
    }
    const script = document.createElement('script');
    script.src = src + '?v=' + encodeURIComponent(version);
    script.async = false;
    script.setAttribute(marker, version);
    script.onerror = () => console.error('[Legato placement] failed to load ' + src);
    if (onload) script.onload = onload;
    document.head.appendChild(script);
  }

  function loadPlacementFixes() {
    loadScript('./notation-placement-fix.js', 'data-legato-placement-fix', () => {
      loadScript('./notation-placement-priority-fix.js', 'data-legato-placement-priority', () => {
        loadScript('./notation-semantic-fix.js', 'data-legato-semantic-fix', () => {
          loadScript('./notation-catalog-core.js', 'data-legato-catalog-core', () => {
            loadScript('./notation-catalog-metadata-corrections.js', 'data-legato-catalog-metadata', () => {
              loadScript('./notation-catalog-placement.js', 'data-legato-catalog-placement', () => {
                loadScript('./notation-catalog-render-audio.js', 'data-legato-catalog-render-audio', () => {
                  loadScript('./notation-theory-playback-fix.js', 'data-legato-theory-playback', () => {
                    loadScript('./musicxml-export-fix.js', 'data-legato-musicxml-export');
                  });
                });
              });
            });
          });
        });
      });
    });
  }

  function loadNewLoader(version) {
    if (!version || version === window.__legatoLoaderBuild) return false;
    loadScript('./cache-refresh.js', 'data-legato-build-loader', null, version);
    return true;
  }

  async function manifestBuild() {
    const probe = new URL('legato-build.json', location.href);
    probe.searchParams.set('_legato_build_check', String(Date.now()));
    const response = await fetch(probe.href, {
      cache: 'no-store',
      credentials: 'same-origin',
      headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
    });
    if (!response.ok) return '';
    const manifest = await response.json();
    return String(manifest && manifest.version || '');
  }

  function buildFromHtml(html) {
    const meta = html.match(/<meta\s+name=["']legato-build["']\s+content=["']([^"']+)["']/i);
    if (meta) return meta[1];
    const runtime = html.match(/support\.js\?v=([^"'&<>\s]+)/i);
    return runtime ? runtime[1] : '';
  }

  async function legacyIndexBuild() {
    const probe = new URL('index.html', location.href);
    probe.searchParams.set('_legato_refresh_check', String(Date.now()));
    const response = await fetch(probe.href, {
      cache: 'no-store',
      credentials: 'same-origin',
      headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
    });
    return response.ok ? buildFromHtml(await response.text()) : '';
  }

  async function checkForNewBuild() {
    if (document.hidden || !navigator.onLine || window.__legatoLoaderBuild !== LOADER_BUILD) return;
    try {
      const nextBuild = await manifestBuild() || await legacyIndexBuild();
      loadNewLoader(nextBuild);
    } catch (_) {
      // Being offline or temporarily unable to reach the deployment must never interrupt editing.
    }
  }

  loadPlacementFixes();
  addEventListener('focus', checkForNewBuild);
  addEventListener('online', checkForNewBuild);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) checkForNewBuild();
  });
  setTimeout(checkForNewBuild, 1200);
  setInterval(checkForNewBuild, CHECK_EVERY_MS);
})();
