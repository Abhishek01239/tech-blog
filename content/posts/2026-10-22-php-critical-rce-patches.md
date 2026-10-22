---
title: "PHP Ships Fixes for Two Critical Unauthenticated-RCE Flaws"
date: 2026-10-22
draft: false
description: "PHP fixed two critical unauthenticated remote-code-execution flaws after AI-assisted discovery, as operators took public websites offline and raced to patch."
image: "/images/2026-10-22-php-critical-rce-patches.jpg"
tags: [PHP, cybersecurity, remote code execution, CVE-2026-109618, CVE-2026-109619, AI-assisted security]
categories: [Cybersecurity, Software]
author: "TechPulse"
---
The PHP project released versions 8.5.12, 8.4.27, 8.3.36 and 8.2.35 on Oct. 21 to address CVE-2026-109618 and CVE-2026-109619. PHP rates both flaws CVSS v4.0 9.2 and says they can allow unauthenticated remote code execution. The project warns that PHP installations serving web requests may be affected, with the highest risk in Apache’s mod_php configuration. [1]

The first issue is an out-of-memory handling flaw that can leave request data partially initialized for cleanup code to misread. The second involves request-owned global state remaining after its memory has been freed. PHP says an unauthenticated request can reach the first path before application code runs under mod_php; the PHP Foundation says remote execution was also confirmed through PHP-FPM application-level paths. [1] [2]

## AI-assisted discovery, human-reviewed fixes

The PHP Foundation says an external audit and later work by Calif, OpenAI and Wiz clarified the impact of the out-of-memory flaw. It describes AI-assisted scanning and validation, while saying people made final decisions and patches. Reuters also reports that researchers attributed discovery to AI systems, including Wiz Atlas and other models. The sources do not establish that an AI system produced a working exploit. [2] [3]

The PHP Foundation said it had not identified a functional exploit at release. Reuters separately reported that Amazon detected attempted exploitation against a honeypot on Oct. 17 and later observed broader attempts, while remaining unsure whether they would work against real sites. These reports describe attempted activity, not confirmed compromise of the affected public websites. [2] [3]

## Organizations chose precautionary downtime

Reuters reported that public-facing services in the Netherlands, Finland, Denmark and France were taken offline or put into preventive maintenance. The article also cited a Censys estimate that about 1.5 million of 2.6 million hosts reported versions without a fix. That is a snapshot of reported versions, not a count of confirmed vulnerable or compromised servers. [3]

PHP’s advisory says updating is the only complete solution. Versions 8.1 and older no longer receive updates from the project, though some vendors may backport fixes. Operators should check their distribution’s package status and upgrade supported branches; a configuration workaround can reduce exposure but is not a substitute for patching. [1]

### Sources
[1] [PHP: Critical remote code execution vulnerabilities, update now](https://www.php.net/archive/2026.php)
[2] [PHP Foundation: Today’s PHP security release and strengthening security](https://thephp.foundation/blog/2026/10/21/todays-php-security-release-and-how-were-strengthening-php-security/)
[3] [Reuters: Government websites go offline as PHP vulnerabilities trigger patch scramble](https://www.reuters.com/world/asia-pacific/eu-agency-warns-websites-may-need-be-taken-offline-php-prepares-patches-2026-10-21/)
