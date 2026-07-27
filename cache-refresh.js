"use strict";
(() => {
  const CHECK_EVERY_MS = 30000;

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

  addEventListener('focus', checkForNewBuild);
  addEventListener('online', checkForNewBuild);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) checkForNewBuild();
  });
  setTimeout(checkForNewBuild, 4000);
  setInterval(checkForNewBuild, CHECK_EVERY_MS);
})();
