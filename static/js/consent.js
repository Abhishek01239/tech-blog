/* TechPulse consent gate — loads AdSense only after the visitor opts in. */
(function () {
    'use strict';

    var KEY = 'tp-consent-v1';
    var meta = document.querySelector('meta[name="adsense-client"]');
    var client = meta ? (meta.getAttribute('content') || '') : '';
    var adsLoaded = false;

    function read() {
        try { return window.localStorage.getItem(KEY); } catch (e) { return null; }
    }

    function store(value) {
        try { window.localStorage.setItem(KEY, value); } catch (e) {}
    }

    function clear() {
        try { window.localStorage.removeItem(KEY); } catch (e) {}
    }

    function fillSlots() {
        var units = document.querySelectorAll('ins.adsbygoogle');
        for (var i = 0; i < units.length; i++) {
            if (units[i].getAttribute('data-adsbygoogle-status')) continue;
            try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) {}
        }
    }

    function loadAds() {
        if (adsLoaded || !client) return;
        adsLoaded = true;
        var s = document.createElement('script');
        s.async = true;
        s.crossOrigin = 'anonymous';
        s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + encodeURIComponent(client);
        s.addEventListener('load', fillSlots);
        document.head.appendChild(s);
    }

    function showBanner(show) {
        var el = document.getElementById('tp-consent');
        if (el) el.hidden = !show;
    }

    function decide(value) {
        store(value);
        showBanner(false);
        if (value === 'granted') loadAds();
    }

    function init() {
        var saved = read();
        showBanner(!saved);
        if (saved === 'granted') loadAds();

        var buttons = document.querySelectorAll('[data-consent]');
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].addEventListener('click', function () {
                decide(this.getAttribute('data-consent'));
            });
        }

        var resets = document.querySelectorAll('[data-consent-reset]');
        for (var j = 0; j < resets.length; j++) {
            resets[j].addEventListener('click', function (e) {
                e.preventDefault();
                clear();
                showBanner(true);
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
