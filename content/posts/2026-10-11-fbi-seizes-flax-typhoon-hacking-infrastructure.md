---
title: "Flax Typhoon Unmasked: Inside the FBI's Global Takedown of China's Hacking-for-Hire Empire"
date: 2026-10-11
draft: false
description: "On October 8, the FBI and seven international partners seized the tools and domains of Beijing-based Integrity Technology Group, exposing a commercial hacking operation that stole email from governments, hospitals, and law enforcement worldwide. The joint advisory reveals an alarming new twist: a portal that let third parties browse stolen inboxes."
tags: [Cybersecurity, China, FBI, Espionage, Cloud Security]
categories: ["Tech News"]
author: "TechPulse"
---

# Flax Typhoon Unmasked: Inside the FBI's Global Takedown of China's Hacking-for-Hire Empire

In one of the most significant cyber-espionage disruptions in years, the FBI, the U.S. Justice Department, and cybersecurity agencies from seven allied nations announced on October 8 that they had seized the infrastructure of Beijing-based Integrity Technology Group — a Shanghai Stock Exchange-listed company that Western officials say operated as a commercial front for Chinese state-sponsored hacking. The operation dismantled two of the firm's core platforms and exposed a sprawling, years-long campaign to steal email from governments, hospitals, law enforcement agencies, and religious institutions around the world.

## What Happened

At the center of the takedown were two tools the FBI says Integrity Technology Group built and operated: **MicroScan**, a vulnerability scanner that probed networks for weak spots using a botnet of hijacked IoT devices infected with a variant of the notorious Mirai malware, and **FishHub**, a spear-phishing and data-theft platform. The FBI seized seven internet domains supporting both tools, including c0cc[.]cc, which served as MicroScan's front door and was confirmed still online in September 2026.

The Justice Department said MicroScan's scanning targets included a U.S. power company in South Carolina, a multinational NGO, Japanese and Polish airports, Taiwanese natural gas and power companies, and roughly twenty Taiwanese universities. FishHub, meanwhile, was used to support spear-phishing and intrusion activity against many of those same victims.

The most startling revelation, however, came in the joint advisory (AA26-281A) issued by the FBI, CISA, and NSA alongside agencies from the UK, Australia, Canada, Japan, New Zealand, and Spain: the hackers ran a **web application that provided third-party access to stolen email content**. In other words, compromised inboxes weren't just harvested for intelligence — they were effectively catalogued and made browsable to outside parties. The FBI also recovered an archived email database the threat actors used to track their targets.

## A Multi-Year, Multi-Continent Campaign

According to the advisory, the campaign dates back to at least 2021 and relied on a hybrid of automated and hands-on techniques. The actors used automated scanners armed with more than 1,300 penetration-testing scripts to find vulnerable web applications, exploited known CVEs, and conducted password-spraying attacks against Microsoft 365 and Exchange accounts. Once inside, they deployed custom email-harvesting tools — including a PHP bot that pulled mail through Exchange Web Services — and established persistence using SoftEther VPN clients disguised as legitimate Windows processes.

Observed victims of email theft spanned government organizations, law enforcement agencies, healthcare systems, and religious institutions in Southeast Asia, with additional targets across Africa, North America, and the United States itself. The activity overlaps with threat clusters tracked by security vendors under the names Flax Typhoon, Ethereal Panda, and RedJuliett.

Integrity Technology Group is no stranger to U.S. law enforcement. Treasury sanctioned the firm in January 2025 for its role in computer intrusions, and the FBI previously disrupted its Raptor Train botnet — a network of more than 200,000 compromised routers, IP cameras, and NAS devices — in September 2024. The company, which holds contracts with the Chinese government, rejected the earlier U.S. accusations as baseless. The EU added it to its own sanctions list in March 2026.

## Why This Matters

The case is a vivid illustration of how Beijing increasingly outsources cyber operations to commercial contractors. As FBI Cyber Division Assistant Director Brett Leatherman noted, the Chinese government relies on such companies to expand the reach of its operations — blending for-profit revenue with state-aligned espionage.

It also sends an urgent message to every organization running Microsoft Exchange or Microsoft 365: if your mail environment is internet-reachable and multi-factor authentication isn't universally enforced, you may already be a victim. The security recommendations are familiar but bear repeating — patch aggressively, enforce MFA everywhere, monitor for anomalous Exchange Web Services traffic, and assume credential attacks are ongoing.

Officials caution that the seizure is a temporary degradation, not an all-kill. The advisory explicitly warns that Integrity Tech retains the capability to rebuild its infrastructure. For defenders, that means this week's victory is a window to harden systems — not an excuse to stand down.
