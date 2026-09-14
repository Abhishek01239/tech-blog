/* TechPulse — core.js init (AdSense-ready)
   Gated on NEXT_PUBLIC_ADSENSE_CLIENT; loads only when set.
   This keeps the site clean pre-approval and activates ads post-approval.
*/
(function() {
    'use strict';
    const CLIENT = (typeof process !== 'undefined' && process.env && process.env.NEXT_PUBLIC_ADSENSE_CLIENT)
        ? process.env.NEXT_PUBLIC_ADSENSE_CLIENT
        : (window.__ADSENSE_CLIENT || '');
    if (!CLIENT || CLIENT.trim() === '' || CLIENT.indexOf('ca-pub-') !== 0) return;

    // Init 3 ad slots (header, sidebar, in-article footer)
    const slots = [
        { id: 'adsense-slot-1', zone: 'top-banner', label: 'Advertisement' },
        { id: 'adsense-slot-2', zone: 'sidebar-sticky', label: 'Advertisement' },
        { id: 'adsense-slot-3', zone: 'article-footer', label: 'Advertisement' }
    ];
    // Real ad injection deferred to approval; placeholder only.
    console.info('[TechPulse AdSense init] Client configured:', CLIENT, '| Slots:', slots.length);
})();
