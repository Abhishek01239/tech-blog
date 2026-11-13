/* TechPulse Vulnerability Watch
   Charts critical and high CVEs from the NVD public API in the browser.
   A build-time snapshot renders instantly; live NVD data replaces it when
   reachable. No backend, no API key, no tracking. */
(function () {
    'use strict';

    var DAYS = 14;
    var CACHE_KEY = 'tp-vuln-watch-v2';
    var CACHE_TTL = 15 * 60 * 1000;
    var SNAPSHOT_URL = '/data/vuln-snapshot.json';
    var SEVERITIES = ['CRITICAL', 'HIGH'];

    var table = document.getElementById('vw-table');
    var tbody = document.getElementById('vw-body');
    var statusEl = document.getElementById('vw-status');
    var severitySel = document.getElementById('vw-severity');
    var searchInput = document.getElementById('vw-search');
    var refreshBtn = document.getElementById('vw-refresh');
    if (!table || !tbody || !statusEl) return;

    var rows = [];
    var note = '';

    function setStatus(text) { statusEl.textContent = text; }

    function isoString(date) {
        return date.toISOString().replace(/\.\d{3}Z$/, '.000Z');
    }

    function nvdUrl(severity, start, end) {
        return 'https://services.nvd.nist.gov/rest/json/cves/2.0' +
            '?pubStartDate=' + start +
            '&pubEndDate=' + end +
            '&cvssV3Severity=' + severity +
            '&resultsPerPage=100';
    }

    function severityOf(cve) {
        var metrics = cve.metrics || {};
        var keys = ['cvssMetricV31', 'cvssMetricV40', 'cvssMetricV30', 'cvssMetricV2'];
        for (var i = 0; i < keys.length; i++) {
            var list = metrics[keys[i]];
            if (list && list.length) {
                var data = list[0].cvssData || {};
                var label = (data.baseSeverity || list[0].baseSeverity || '').toUpperCase();
                if (data.baseScore != null) {
                    return { score: Number(data.baseScore), label: label };
                }
            }
        }
        return { score: 0, label: '' };
    }

    function descriptionOf(cve) {
        var list = cve.descriptions || [];
        for (var i = 0; i < list.length; i++) {
            if (list[i].lang === 'en') return list[i].value;
        }
        return list.length ? list[0].value : '';
    }

    function normalise(payload, severity) {
        var out = [];
        var items = (payload && payload.vulnerabilities) || [];
        for (var i = 0; i < items.length; i++) {
            var cve = items[i].cve || {};
            var sev = severityOf(cve);
            out.push({
                id: cve.id || '',
                description: descriptionOf(cve),
                score: sev.score,
                severity: sev.label || severity,
                published: cve.published || ''
            });
        }
        return out;
    }

    function readCache() {
        try {
            var raw = sessionStorage.getItem(CACHE_KEY);
            if (!raw) return null;
            var parsed = JSON.parse(raw);
            if (!parsed || !parsed.at || Date.now() - parsed.at > CACHE_TTL) return null;
            return parsed.rows;
        } catch (err) { return null; }
    }

    function writeCache(data) {
        try {
            sessionStorage.setItem(CACHE_KEY, JSON.stringify({ at: Date.now(), rows: data }));
        } catch (err) { /* storage full or blocked; caching is optional */ }
    }

    function fetchSeverity(severity, start, end) {
        return fetch(nvdUrl(severity, start, end), { headers: { 'Accept': 'application/json' } })
            .then(function (response) {
                if (!response.ok) throw new Error('NVD responded ' + response.status);
                return response.json();
            })
            .then(function (payload) { return normalise(payload, severity); });
    }

    function loadSnapshot() {
        return fetch(SNAPSHOT_URL, { cache: 'no-cache' })
            .then(function (response) {
                if (!response.ok) throw new Error('snapshot ' + response.status);
                return response.json();
            });
    }

    function load(force) {
        var cached = force ? null : readCache();
        if (cached && cached.length) {
            rows = cached;
            note = '(cached, refreshes every 15 minutes)';
            render();
            return;
        }

        setStatus('Loading recent CVEs…');
        loadSnapshot()
            .then(function (snap) {
                if (snap && snap.rows && snap.rows.length && !rows.length) {
                    rows = snap.rows;
                    note = 'Snapshot from ' + formatDate(snap.generated) + '; checking the NVD for newer advisories…';
                    render();
                }
                liveRefresh();
            })
            .catch(function () { liveRefresh(); });
    }

    function liveRefresh() {
        var end = new Date();
        var start = new Date(end.getTime() - DAYS * 24 * 60 * 60 * 1000);
        var startIso = isoString(start);
        var endIso = isoString(end);

        fetchSeverity(SEVERITIES[0], startIso, endIso)
            .then(function (first) {
                // The NVD often takes 30s per call, so publish the critical set now.
                commit(first, 'Live critical advisories loaded; fetching high-severity ones…', false);
                return new Promise(function (resolve) {
                    setTimeout(function () {
                        fetchSeverity(SEVERITIES[1], startIso, endIso)
                            .then(function (second) { resolve(first.concat(second)); })
                            .catch(function () { resolve(first); });
                    }, 1500);
                });
            })
            .then(function (all) {
                commit(all, '', true);
            })
            .catch(function (err) {
                if (rows.length) {
                    note = 'Live refresh failed (' + err.message + '); using the most recent data we have.';
                    render();
                    return;
                }
                setStatus('Could not reach the NVD API (' + err.message + '). The NVD limits anonymous requests to five every 30 seconds — wait a moment and press Refresh, or browse nvd.nist.gov directly.');
                table.hidden = true;
            });
    }

    function commit(list, statusNote, complete) {
        rows = dedupe(list).sort(function (a, b) {
            if (b.score !== a.score) return b.score - a.score;
            return (b.published || '').localeCompare(a.published || '');
        });
        note = statusNote;
        if (complete) writeCache(rows);
        render();
    }

    function dedupe(list) {
        var seen = {};
        return list.filter(function (item) {
            if (!item.id || seen[item.id]) return false;
            seen[item.id] = true;
            return true;
        });
    }

    function matches(row, severity, query) {
        if (severity !== 'all' && row.severity !== severity) return false;
        if (!query) return true;
        return (row.id + ' ' + row.description).toLowerCase().indexOf(query) !== -1;
    }

    function render() {
        var severity = severitySel.value;
        var query = searchInput.value.trim().toLowerCase();
        var filtered = rows.filter(function (row) { return matches(row, severity, query); });

        tbody.textContent = '';
        filtered.forEach(function (row) {
            var tr = document.createElement('tr');

            var idCell = document.createElement('td');
            var link = document.createElement('a');
            link.href = 'https://nvd.nist.gov/vuln/detail/' + encodeURIComponent(row.id);
            link.textContent = row.id;
            link.rel = 'noopener';
            link.className = 'vuln-cve';
            idCell.appendChild(link);
            tr.appendChild(idCell);

            var sevCell = document.createElement('td');
            var badge = document.createElement('span');
            badge.className = 'vuln-badge vuln-' + (row.severity || '').toLowerCase();
            badge.textContent = row.severity || '—';
            sevCell.appendChild(badge);
            tr.appendChild(sevCell);

            var scoreCell = document.createElement('td');
            scoreCell.textContent = row.score ? row.score.toFixed(1) : '—';
            scoreCell.className = 'vuln-score';
            tr.appendChild(scoreCell);

            var dateCell = document.createElement('td');
            dateCell.className = 'vuln-date';
            dateCell.textContent = formatDate(row.published);
            tr.appendChild(dateCell);

            var descCell = document.createElement('td');
            descCell.className = 'vuln-desc';
            descCell.textContent = truncate(row.description, 190);
            tr.appendChild(descCell);

            tbody.appendChild(tr);
        });

        table.hidden = filtered.length === 0;
        if (!filtered.length) {
            setStatus(rows.length
                ? 'No CVEs match that filter. Try “all severities” or a shorter search term.'
                : 'The NVD returned no critical or high CVEs for this window.');
        } else {
            var text = 'Showing ' + filtered.length + ' of ' + rows.length +
                ' CVEs from the last ' + DAYS + ' days.';
            setStatus(note ? text + ' ' + note : text);
        }
    }

    function formatDate(value) {
        if (!value) return '—';
        var date = new Date(value);
        if (isNaN(date.getTime())) return '—';
        return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    }

    function truncate(text, limit) {
        if (!text) return '';
        return text.length > limit ? text.slice(0, limit).replace(/\s+\S*$/, '') + '…' : text;
    }

    var debounce;
    searchInput.addEventListener('input', function () {
        clearTimeout(debounce);
        debounce = setTimeout(render, 150);
    });
    severitySel.addEventListener('change', render);
    refreshBtn.addEventListener('click', function () {
        refreshBtn.disabled = true;
        note = '';
        load(true);
        setTimeout(function () { refreshBtn.disabled = false; }, 4000);
    });

    load(false);
})();
