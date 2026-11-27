---
title: "CVSS Scores Explained: What Critical, High, Medium and Low Actually Mean"
date: 2026-11-27T07:00:00+05:30
draft: false
description: "A practical guide to CVSS: how the 0–10 score is calculated, what each base metric means, why a 9.8 is not always your top priority, and how to combine CVSS with EPSS and CISA's KEV list."
categories: ["Cybersecurity"]
image: "/images/covers/cvss-scores-explained-v2.jpg"
author: "Jaiswar Abhishek"
---

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

## Calculate a score yourself

The base score is not a judgement call. Once the eight metrics are chosen, the number comes from a fixed formula in the [CVSS v3.1 specification](https://www.first.org/cvss/v3.1/specification-document). Writing it out in code is the quickest way to see how each metric moves the result. This is a complete base-score calculator in plain Python, following section 7 of the specification:

```python
import math

W = {
    "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},
    "AC": {"L": 0.77, "H": 0.44},
    "UI": {"N": 0.85, "R": 0.62},
    "C": {"H": 0.56, "L": 0.22, "N": 0.0},
}
PR_U = {"N": 0.85, "L": 0.62, "H": 0.27}
PR_C = {"N": 0.85, "L": 0.68, "H": 0.5}


def roundup(x):
    # CVSS v3.1 Roundup: smallest number, to 1 decimal, >= x
    i = round(x * 100000)
    if i % 10000 == 0:
        return i / 100000.0
    return (math.floor(i / 10000) + 1) / 10.0


def base_score(vector):
    parts = dict(p.split(":") for p in vector.split("/")[1:])
    changed = parts["S"] == "C"
    iss = 1 - (1 - W["C"][parts["C"]]) * (1 - W["C"][parts["I"]]) * (1 - W["C"][parts["A"]])
    if changed:
        impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15
    else:
        impact = 6.42 * iss
    pr = (PR_C if changed else PR_U)[parts["PR"]]
    exploit = 8.22 * W["AV"][parts["AV"]] * W["AC"][parts["AC"]] * pr * W["UI"][parts["UI"]]
    if impact <= 0:
        return 0.0
    if changed:
        return roundup(min(1.08 * (impact + exploit), 10))
    return roundup(min(impact + exploit, 10))


def rating(s):
    if s == 0: return "None"
    if s < 4: return "Low"
    if s < 7: return "Medium"
    if s < 9: return "High"
    return "Critical"

```

Running it on a few common vectors gives the same results as FIRST's official calculator:

```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H  ->  9.8 Critical
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H  ->  10.0 Critical
CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H  ->  8.8 High
CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H  ->  7.8 High
CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N  ->  6.1 Medium
CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N  ->  5.9 Medium
CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N  ->  5.4 Medium
```

A few things become obvious once you play with it:

- **Requiring a login costs a full point.** Changing only `PR:N` to `PR:L` takes the classic 9.8 down to 8.8, from Critical to High. That single difference is often what separates "patch tonight" from "patch this week".
- **Network versus local access matters just as much.** The same full-impact flaw scores 7.8 when the attacker must already be on the machine.
- **Scope change can push a score to the maximum.** With `S:C`, the impact formula is different and the total is multiplied by 1.08, which is how a 9.8 becomes a 10.0.
- **Rounding always goes up.** The specification's `Roundup` function rounds to one decimal place, never down, and is written with integer arithmetic so that floating-point errors can't produce results like 4.000001 rounding to 4.1.

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
