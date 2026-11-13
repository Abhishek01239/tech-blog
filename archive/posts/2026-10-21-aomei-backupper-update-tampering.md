---
title: "AOMEI Backupper Update Tampering Hid in Brief Bursts"
date: 2026-10-21
draft: false
description: "Google and Mandiant say UNC7017 tampered with AOMEI Backupper updates in brief bursts, directing update clients to CROSSROAD and SHINYROAD malware."
image: "/images/2026-10-21-aomei-backupper-update-tampering.jpg"
tags: [AOMEI Backupper, supply-chain security, UNC7017, CROSSROAD, SHINYROAD]
categories: [Cybersecurity, Software]
author: "TechPulse"
---
Google Threat Intelligence Group and Mandiant say they investigated a campaign that tampered with AOMEI Technology’s update infrastructure from April through July 2026. The actor, tracked as UNC7017, changed update configuration files for brief periods and then restored legitimate versions. Investigators observed windows lasting 10 minutes on May 28, six minutes on July 16 and five minutes on July 20. [1]

## Malicious changes blended into normal updates

A device checking for updates during one of those periods could be directed to an attacker-controlled ZIP instead of the expected package. Google says the associated chain included CROSSROAD, a downloader that checked its environment before staging additional components, and SHINYROAD, a modular backdoor. The configuration changes also used AOMEI’s notification service to initiate execution of downloaded files. [1]

The short-lived changes meant a later inspection could see authentic configuration again. SecurityWeek reports the campaign was opportunistic: devices that contacted the update infrastructure during an active window could receive the altered package. Its reporting also describes later delivery of Radmin Server and Adaptix components. The public research does not establish how many machines were successfully infected. [1] [2]

## Exposure spans several sectors

Google’s researchers identified affected organizations in IT services, telecommunications and higher education across multiple countries, including Australia, Brazil, India, Pakistan, Portugal, Singapore, South Africa, Spain, Switzerland, Türkiye and the United States. The researchers cautioned that the observed footprint may not represent the full scope because systems checking outside the brief tampering windows would appear normal. [1]

The Record reported that AOMEI had not yet identified or notified customers known to have been infected. The company said it had updated its servers, would assess potentially affected users and released a free detection tool. Those statements describe the vendor’s reported response; they do not confirm that every affected customer has been found or contacted. [3]

Organizations that used Backupper during the reported exposure period may want to review endpoint telemetry, apply available updates and investigate suspicious downloads or outbound connections. Server-side remediation alone does not establish that any affected endpoint is clean. The sources do not provide a verified infection total, so a definitive victim count remains unknown. [1] [3]

## Why It Matters

The campaign's defining feature is timing: tampering that lasted minutes and was then reverted defeats the assumption that inspecting an update server later will reveal what happened. Trust in a routine, signed update channel is precisely what made the payloads effective, and the affected organisations span IT services, telecommunications and higher education across many countries. With no verified infection total, the practical burden falls on defenders reviewing endpoint telemetry for the downloader, backdoor and outbound connections.

### Sources
[1] [Google Cloud: Investigating ephemeral supply-chain tampering](https://cloud.google.com/blog/topics/threat-intelligence/investigating-ephemeral-supply-chain-tampering)
[2] [SecurityWeek: AOMEI Backupper compromised in short-burst campaign](https://www.securityweek.com/aomei-backupper-compromised-in-short-burst-supply-chain-campaign/)
[3] [The Record: AOMEI yet to notify customers after update hijack](https://therecord.media/aomei-yet-to-notify-customers-hijack-software)
