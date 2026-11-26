/* Mobile QA add-on (2026-11-26). Created by Rohan Kells. Registers the site service worker. */
(function () {
  if (!('serviceWorker' in navigator)) return;
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js').catch(function () {});
  });
})();
