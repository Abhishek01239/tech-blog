// Rebuilds static/data/vuln-snapshot.json from the NVD public API.
// Run weekly: node scripts/refresh-vuln-snapshot.mjs
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const DAYS = 14;
const SEVERITIES = ['CRITICAL', 'HIGH'];
const OUT = join(dirname(fileURLToPath(import.meta.url)), '..', 'static', 'data', 'vuln-snapshot.json');

const iso = (d) => d.toISOString().replace(/\.\d{3}Z$/, '.000Z');
const end = new Date();
const start = new Date(end.getTime() - DAYS * 24 * 60 * 60 * 1000);

function severityOf(cve) {
  const metrics = cve.metrics || {};
  for (const key of ['cvssMetricV31', 'cvssMetricV40', 'cvssMetricV30', 'cvssMetricV2']) {
    const list = metrics[key];
    if (list?.length) {
      const data = list[0].cvssData || {};
      if (data.baseScore != null) {
        return { score: Number(data.baseScore), label: (data.baseSeverity || list[0].baseSeverity || '').toUpperCase() };
      }
    }
  }
  return { score: 0, label: '' };
}

async function fetchSeverity(severity) {
  const url = 'https://services.nvd.nist.gov/rest/json/cves/2.0' +
    `?pubStartDate=${iso(start)}&pubEndDate=${iso(end)}` +
    `&cvssV3Severity=${severity}&resultsPerPage=100`;
  const response = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!response.ok) throw new Error(`NVD ${severity}: ${response.status}`);
  const payload = await response.json();
  return (payload.vulnerabilities || []).map(({ cve }) => {
    const sev = severityOf(cve);
    const descriptions = cve.descriptions || [];
    const english = descriptions.find((d) => d.lang === 'en') || descriptions[0] || {};
    let description = (english.value || '').replace(/\s+/g, ' ').trim();
    if (description.length > 300) description = description.slice(0, 300).replace(/\s+\S*$/, '') + '…';
    return {
      id: cve.id || '',
      description,
      score: sev.score,
      severity: sev.label || severity,
      published: cve.published || ''
    };
  });
}

const rows = [];
const seen = new Set();
for (const severity of SEVERITIES) {
  for (const row of await fetchSeverity(severity)) {
    if (row.id && !seen.has(row.id)) {
      seen.add(row.id);
      rows.push(row);
    }
  }
  await new Promise((r) => setTimeout(r, 1500));
}
rows.sort((a, b) => b.score - a.score || (b.published || '').localeCompare(a.published || ''));

await writeFile(OUT, JSON.stringify({ generated: new Date().toISOString(), windowDays: DAYS, rows }));

// Bump the tool page's lastmod so the sitemap reflects the refresh.
const page = join(dirname(fileURLToPath(import.meta.url)), '..', 'content', 'vuln-watch.md');
const today = new Date().toISOString().slice(0, 10);
const front = (await readFile(page, 'utf8')).replace(/^lastmod: .*$/m, `lastmod: ${today}`);
await writeFile(page, front);

console.log(`Wrote ${rows.length} CVEs to ${OUT} (lastmod ${today})`);
