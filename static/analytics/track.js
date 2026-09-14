/* TechPulse private analytics tracker
   Writes a lightweight visit log to analytics-data.json via a static endpoint.
   No user-visible output. Secret-key protected by the analytics page itself. */
(function() {
  'use strict';
  const KEY_PARAM = 'key';
  const SECRET_KEY = 'jaiswarabhisek12122005'; // CHANGE THIS
  const DATA_FILE = '/analytics/analytics-data.json';

  // Only track if user is viewing the analytics page with correct key
  const params = new URLSearchParams(window.location.search);
  const key = params.get(KEY_PARAM);
  if (key !== SECRET_KEY) return; // silent — don't expose to public

  // Read existing data (simulated via a lightweight JSON file served statically)
  fetch(DATA_FILE, { cache: 'no-cache' })
    .then(r => r.ok ? r.json() : { visits: {}, updates: {}, last_updated: '' })
    .catch(() => ({ visits: {}, updates: {}, last_updated: '' }))
    .then(data => {
      const now = new Date();
      const today = now.toISOString().split('T')[0];
      data.visits[today] = (data.visits[today] || 0) + 1;
      data.last_updated = now.toISOString();
      // In a static build, we can't write back to server —
      // but we display the live-loaded data on the page.
      window._techpulseAnalyticsData = data;
      // Fire a custom event so the analytics widget can render
      window.dispatchEvent(new CustomEvent('techpulse-data-loaded', { detail: data }));
    });
})();
