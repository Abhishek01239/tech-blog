---
title: "CVSS Scores Explained: What Critical, High, Medium and Low Actually Mean"
date: 2026-11-15
draft: true
review_status: needs-review
description: "A practical guide to CVSS: how the 0–10 score is calculated, what each base metric means, why a 9.8 is not always your top priority, and how to combine CVSS with EPSS and CISA's KEV list."
categories: ["Cybersecurity"]
author: "Abhishek Jaiswar"
---

<!-- OWNER REVIEW CHECKLIST (delete this comment before publishing)
1. Read every section and rewrite anything that doesn't sound like you.
2. Add at least one screenshot of your own: e.g. the NVD page for a real CVE with the vector string highlighted, or Vulnerability Watch filtered to one vendor. Save it in static/images/ and reference it below.
3. Add one example from your own experience (a CVE you patched, a scanner report you triaged, etc.).
4. Check each link opens and says what the article claims.
5. Then set draft: false and review_status: approved.
-->

If you have ever opened a vulnerability scanner report, you have seen it: hundreds of findings, each tagged **Critical**, **High**, **Medium** or **Low**, each with a number like 9.8 or 5.3. That number is a CVSS score, and almost every security tool, advisory and patch policy uses it.

It is also widely misunderstood. A CVSS score measures how *severe* a flaw could be in the worst case. It does not measure how *likely* you are to be attacked through it, and it knows nothing about your systems. This guide explains what the score actually contains, how to read the vector string behind it, and how to use it to decide what to patch first.

## What CVSS is

The **Common Vulnerability Scoring System** is an open standard maintained by [FIRST](https://www.first.org/cvss/), the Forum of Incident Response and Security Teams. It gives every vulnerability a score from 0.0 to 10.0 based on a fixed set of questions about how the flaw can be exploited and what an attacker gains.

Two versions are in common use:

- **CVSS v3.1** (2019) is still the version you will see most often in the National Vulnerability Database (NVD), scanners and vendor advisories.
- **CVSS v4.0** (released November 2023) refines the metrics and is gradually being adopted. Many records now carry both a v3.1 and a v4.0 score.

The examples below use v3.1 because it is what most tools still display. The ideas carry over to v4.0.

## The severity bands

The 0–10 score is mapped to a qualitative rating:

| Rating   | CVSS v3.x score |
|----------|-----------------|
| None     | 0.0             |
| Low      | 0.1 – 3.9       |
| Medium   | 4.0 – 6.9       |
| High     | 7.0 – 8.9       |
| Critical | 9.0 – 10.0      |

When a tool says "Critical", it simply means the base score is 9.0 or above. The label adds no information beyond the number.

## Reading the vector string

Every CVSS score comes with a **vector string** that records the answer to each question. It looks like this:

```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
```

That particular vector scores **9.8 Critical**, and it is the most common Critical vector you will see. Here is what each part means.

### Exploitability: how hard is it to attack?

- **AV – Attack Vector.** Where the attacker has to be. `N` (Network) means anywhere on the internet; `A` (Adjacent) means the same local network; `L` (Local) means already on the machine; `P` (Physical) means physically touching it. Network is the worst case.
- **AC – Attack Complexity.** `L` (Low) means the attack works reliably; `H` (High) means it depends on conditions outside the attacker's control, such as winning a race condition.
- **PR – Privileges Required.** `N` (None) means no login is needed; `L` means a normal user account; `H` means an administrator account.
- **UI – User Interaction.** `N` means the attack works without anyone clicking anything; `R` (Required) means a victim must do something, like open a file.

### Scope

- **S – Scope.** `U` (Unchanged) means the impact stays within the vulnerable component. `C` (Changed) means the attacker can break out into other components, for example escaping a browser sandbox or a virtual machine. A changed scope pushes the score up.

### Impact: what does the attacker get?

- **C – Confidentiality**, **I – Integrity**, **A – Availability.** Each is rated `H` (High), `L` (Low) or `N` (None). `C:H/I:H/A:H` means the attacker can read everything, change everything, and take the system down: effectively full control.

So `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` reads as: *"Anyone on the internet can reliably take full control of this component without logging in and without anyone's help."* That is why it scores 9.8.

Compare it with:

```
CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N
```

This is a typical stored cross-site scripting bug. The attacker needs an account (`PR:L`) and a victim must view the page (`UI:R`), but the script runs in the victim's browser (`S:C`) and can read or change a limited amount of data. It scores **5.4 Medium**.

<!-- OWNER: add a screenshot here of a real NVD CVE page showing the vector string, e.g. one from Vulnerability Watch. -->

## Base, temporal and environmental scores

The number you usually see is the **base score**: the properties of the flaw itself, which do not change over time or between organisations. CVSS also defines two optional groups that almost nobody publishes but that you can calculate yourself:

- **Temporal** (called *Threat* in v4.0): whether working exploit code exists and whether an official fix is available. A flaw with a public exploit and no patch is more urgent than the same flaw with no known exploit.
- **Environmental**: how the flaw applies to *your* setup. A Critical bug in a service that is only reachable from an isolated internal network may be much less urgent for you than its base score suggests.

FIRST's [online calculators](https://www.first.org/cvss/calculator/3.1) let you enter a vector and adjust these groups to see how the score changes.

## Why a 9.8 is not always your top priority

CVSS answers "how bad could this be?" It does not answer "is anyone exploiting it?" or "does it affect me?". Treating every Critical as an emergency leads to two problems: teams get buried in alerts, and genuinely dangerous High-rated flaws that are being exploited get ignored.

Two free data sources fill the gap:

1. **CISA's [Known Exploited Vulnerabilities (KEV) catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)** lists CVEs that are confirmed to be exploited in real attacks. If a CVE is on the KEV list and you run the affected software, it should go to the top of your queue whatever its CVSS score.
2. **[EPSS](https://www.first.org/epss/)** (Exploit Prediction Scoring System), also from FIRST, estimates the probability that a CVE will be exploited in the next 30 days. A CVE with a high EPSS score is far more likely to be used against you than one with a low score.

## A simple prioritisation order

A practical order that many teams use:

1. **On the KEV list and present in your environment.** Patch now, starting with systems exposed to the internet.
2. **High EPSS and internet-facing.** Patch within days.
3. **Critical or High CVSS, internal only, no known exploitation.** Patch in your normal cycle.
4. **Medium and Low.** Batch them into routine updates.

Always confirm that your installed version actually falls in the affected range on the CVE record before you spend time on it. Scanners regularly flag software that has already been patched or is not configured in a vulnerable way.

## Common mistakes

- **Treating the score as a risk rating.** It measures severity, not likelihood or business impact.
- **Ignoring Medium flaws that chain together.** Several low-privilege bugs combined can produce full compromise.
- **Comparing v3.1 and v4.0 scores directly.** The formulas differ, so the same flaw can score differently under each version. Compare like with like.
- **Trusting a single source.** NVD scores, vendor scores and scanner scores sometimes disagree. When they do, read the vendor's advisory; the vendor usually knows best which configurations are affected.

## Try it yourself

[Vulnerability Watch](/vuln-watch/) lists every High and Critical CVE published in the last 14 days. Search for a product you use, open a few CVE records, and read their vector strings using the breakdown above. After a handful you will be able to read a vector at a glance and tell a real emergency from noise.

## Sources

- [FIRST — Common Vulnerability Scoring System v3.1 Specification](https://www.first.org/cvss/v3.1/specification-document)
- [FIRST — CVSS v4.0](https://www.first.org/cvss/v4-0/)
- [FIRST — CVSS v3.1 Calculator](https://www.first.org/cvss/calculator/3.1)
- [FIRST — Exploit Prediction Scoring System (EPSS)](https://www.first.org/epss/)
- [CISA — Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [NIST — National Vulnerability Database](https://nvd.nist.gov/vuln)
