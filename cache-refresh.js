"use strict";
(() => {
  const CHECK_EVERY_MS = 30000;
  const PLACEMENT_FIX_VERSION = "20260728-catalog-audit-3";

  function loadScript(src, marker, onload) {
    if (document.querySelector('script[' + marker + '="' + PLACEMENT_FIX_VERSION + '"]')) {
      if (onload) onload();
      return;
    }
    const script = document.createElement('script');
    script.src = src + '?v=' + encodeURIComponent(PLACEMENT_FIX_VERSION);
    script.async = false;
    script.setAttribute(marker, PLACEMENT_FIX_VERSION);
    script.onerror = () => console.error('[Legato placement] failed to load ' + src);
    if (onload) script.onload = onload;
    document.head.appendChild(script);
  }

  function loadPlacementFixes() {
    loadScript('./notation-placement-fix.js', 'data-legato-placement-fix', () => {
      loadScript('./notation-placement-priority-fix.js', 'data-legato-placement-priority', () => {
        loadScript('./notation-semantic-fix.js', 'data-legato-semantic-fix', () => {
          loadScript('./notation-catalog-core.js', 'data-legato-catalog-core', () => {
            loadScript('./notation-catalog-placement.js', 'data-legato-catalog-placement', () => {
              loadScript('./notation-catalog-render-audio.js', 'data-legato-catalog-render-audio', () => {
                loadScript('./notation-catalog-hotfix-bridge.js', 'data-legato-catalog-bridge', () => {
                  loadScript('./notation-catalog-audit-hotfix.js', 'data-legato-catalog-hotfix');
                });
              });
            });
          });
        });
      });
    });
  }

  function currentBuild() {
    const meta = document.querySelector('meta[name="legato-build"]');
    if (meta && meta.content) return meta.content;
    const runtime = document.querySelector('script[src*="support.js"]');
    if (!runtime) return '';
    try { return new URL(runtime.src, location.href).searchParams.get('v') || ''; }
    catch (_) { return ''; }
  }

  function buildFromHtml(html) {
    const meta = html.match(/<meta\s+name=["']legato-build["']\s+content=["']([^"']+)["']/i);
    if (meta) return meta[1];
    const runtime = html.match(/support\.js\?v=([^"'&<>\s]+)/i);
    return runtime ? runtime[1] : '';
  }

  async function checkForNewBuild() {
    if (document.hidden || !navigator.onLine) return;
    try {
      const probe = new URL('index.html', location.href);
      probe.searchParams.set('_legato_refresh_check', String(Date.now()));
      const response = await fetch(probe.href, {
        cache: 'no-store',
        credentials: 'same-origin',
        headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
      });
      if (!response.ok) return;
      const nextBuild = buildFromHtml(await response.text());
      const activeBuild = currentBuild();
      if (!nextBuild || !activeBuild || nextBuild === activeBuild) return;
      const target = new URL(location.href);
      target.searchParams.set('legato-build', nextBuild);
      location.replace(target.href);
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
  setTimeout(checkForNewBuild, 4000);
  setInterval(checkForNewBuild, CHECK_EVERY_MS);
})();
