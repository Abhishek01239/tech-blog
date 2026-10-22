---
title: "One of the Web's Gatekeepers Used the Number 4 as a Private Key — and the Internet Is Scrambling"
date: 2026-10-22
draft: false
description: "Indian certificate authority eMudhra had the private keys of eight intermediate CA certificates compromised after a key-generation bug produced trivially weak keys, forcing emergency blocks across every major browser. The incident is a stark reminder of how fragile the web's chain of trust really is."
tags: [cybersecurity, certificates, PKI, web security, eMudhra, TLS]
categories: ["Tech News"]
author: "TechPulse"
---

# One of the Web's Gatekeepers Used the Number 4 as a Private Key — and the Internet Is Scrambling

When you visit a website and your browser shows that reassuring padlock icon, you are trusting a small, mostly invisible hierarchy of companies called certificate authorities (CAs) to vouch that the site is what it claims to be. Last week, one of those gatekeepers suffered an embarrassment of historic proportions: eMudhra, an India-based CA that has issued more than 60 million digital certificates, revealed that the private keys behind eight of its intermediate CA certificates had been compromised — and one of them, researchers found, was literally the number 4.

## How a single-digit disaster unfolded

On Saturday, October 17, 2026, a security researcher who goes by Wayne reported to the root programs operated by Mozilla, Google, Apple, and Microsoft that the private keys associated with eight eMudhra intermediate CA certificates had been compromised. To prove it, he did something only possible with total control of the keys: he signed the message "We have a problem here – Wayne" using all eight of them.

The technical explanation was almost comically mundane. The eight certificates used P-384 elliptic-curve keys that should have been generated with enormous, unpredictable 384-bit values. Instead, according to Google's Chrome Root Program, the keys were generated with insufficient randomness — some had values smaller than 256. Recovering them required nothing more sophisticated than testing a few hundred candidate numbers. Security researcher Flüpke drove the point home by publishing one of the private keys on GitHub: the private key for eMudhra's "EM OV TLS CA – G3C" certificate was the integer 4. Others, researchers said, were similarly tiny values like 56 and 237.

Six of the compromised certificates were authorized to issue TLS (HTTPS) certificates, and two were code-signing certificates — the kind that make software appear to come from a trusted publisher. In the wrong hands, those keys could have allowed an attacker to issue certificates that make a fraudulent website look legitimate to any browser that still trusted them, enabling interception of encrypted traffic, credential theft, or malware disguised as signed software.

## The fastest emergency response the web has seen in years

To its credit, the browser ecosystem moved with remarkable speed. Mozilla blocked the affected certificates through Firefox's OneCRL system on October 17 — no update or restart required for users. Google landed a CRLSet update the same day blocking the affected intermediates and went further, removing eMudhra's "emSign ECC Root CA – G3" from the Chrome Root Store entirely. Apple followed with protections on October 19, and Microsoft's arrived October 20. India's cybersecurity watchdog CERT-In issued an advisory on October 21, and numerous open-source projects shipped updates rejecting eMudhra-issued certificates.

eMudhra revoked the eight compromised certificates and stopped issuing new ones under the affected root. The company blamed a bug in a key-generation script from April 2025 that created a second set of weakly generated keys, which were mistakenly selected for signing because their labels resembled the legitimate ones. The company stressed that its root CA keys and other intermediates were unaffected, that only one of the compromised intermediates had been deployed in production, and that none had issued certificates to end users. Google confirmed that no TLS certificates from the six affected intermediates appeared in Certificate Transparency logs before the blocks landed — meaning the worst-case scenario appears to have been averted.

## Why "bigger than Heartbleed" isn't hyperbole

Security professionals have called the cleanup job "bigger than Heartbleed," and while no mass exploitation has been documented, the comparison captures the scope of the trust problem. CRLs and revocation checks are notoriously uneven: browsers now rely on streamlined mechanisms, but countless non-browser applications, IoT devices, APIs, and enterprise tools validate certificates without ever checking revocation status. Certificates signed with the weak keys can still be out there, and any client that still trusts the chain remains vulnerable to impersonation — no matter what the browsers do.

The incident also lands at an uncomfortable moment for the CA ecosystem, which has spent recent years arguing that hardware security modules, audits, and rigorous root programs make key compromise a vanishingly rare event. A script bug that produced the number 4 as a certificate-signing key undermines that narrative in the most vivid way possible. It was not a sophisticated nation-state attack; it was entropy failure — the cryptographic equivalent of leaving the vault door propped open with a folding chair.

## The takeaway

For organizations, the guidance is straightforward: update browsers and operating systems, audit anything that performs certificate validation outside a browser (embedded devices, middleware, CI/CD pipelines), and check whether any systems chain to the affected eMudhra roots. For the industry, the lesson is older still: randomness is not optional, key-generation code deserves the same scrutiny as the keys themselves, and the web's trust model is only as strong as its weakest integer.

The padlock still means something — but only because thousands of engineers spent a very bad weekend making sure it still does.
