---
title: "Pwn2Own Ireland: 32 zero-days, Galaxy S26 email hack"
date: 2026-10-08
draft: false
description: "Day one of Pwn2Own Ireland 2026 produced 32 zero-days and over $368,000 in prizes, including a single-email remote hack of the Galaxy S26."
tags: ["cybersecurity", "pwn2own", "samsung", "zero-day"]
categories: ["Cybersecurity"]
author: "TechPulse"
image: "/images/pwn2own-ireland-zero-days-galaxy-s26.jpg"
---

Ethical hackers opened Pwn2Own Ireland 2026 with 32 zero-day vulnerabilities and more than $368,000 in prize money on day one, including a remote compromise of Samsung's Galaxy S26 triggered by a single email.

## What Happened

The Zero Day Initiative's contest began October 6 in Cork. Teams targeted phones, smart-home gear, printers, and AI tools including OpenAI Codex and LiteLLM. Infosecurity Magazine reported the day-one haul at 32 zero-days plus Master of Pwn points that will be totaled at the end of the event.

Standout chains included an out-of-bounds write paired with a format-string bug against the Sonos Era 300, an input-validation and code-injection path to a reverse shell on LiteLLM, and seven zero-days in an exploit of the Philips Hue Bridge Pro by VinSOC researchers. Another VinSOC pair used five zero-days against Oracle Autonomous AI Database. A use-after-free took the Lexmark CX532adwe.

On phones, Japanese firm Ikotas remotely ran code on a Galaxy S26 with one email, chaining four flaws. Samsung already knew about one of them. The demonstration paid $11,000. Ikotas chief executive Satoki Tsuji said the underlying remote-code-execution issue also reaches current Google Pixel 10 builds and may affect the Pixel 11. Two further Galaxy S26 attacks at the event brought the phone's demonstrated flaw count to five apparently new issues, mixed with collisions on bugs Samsung had already seen.

## Why It Matters

Pwn2Own is a scheduled stress test, not a surprise breach. Vendors get the details, and patches usually follow. The shape of this year's targets is the news. Phones are still falling to email. Smart-home bridges are still falling to chains of small bugs. And AI infrastructure, LiteLLM and an Oracle autonomous database, is now on the same stage as printers.

A single-message remote compromise of a current flagship is the outcome mobile security teams least want to explain. Email remains a delivery path that does not require a malicious app install or a tap on a link the user understands. If the same bug class reaches Pixel 10, the patch window is industry-wide, not a Samsung-only note.

## Industry Impact

Samsung and Google will be expected to ship fixes before the technical write-ups circulate beyond ZDI's disclosure window. Enterprise mobile fleets that treat the S26 and Pixel 10 as current should assume the email attack is real until a bulletin says otherwise. Printer and lighting vendors in the day-one list have the same clock.

The AI targets matter for a different buyer. LiteLLM is glue in a lot of internal agent stacks. A reverse shell against that layer is a reminder that the proxy in front of a model is an application, with the same input bugs as any other service. Oracle's autonomous database showing up in a contest chain will land in cloud-security reviews this quarter.

## What's Next

ZDI will publish advisories on its usual timeline after vendors patch. The rest of the Cork schedule will add to the prize pool and the zero-day count. Teams that missed day one still have categories left, and collisions will decide how much of the phone work is truly new.

For defenders, the immediate move is narrower: watch Samsung and Google security bulletins, and treat inbound email rendering on the latest Android flagships as the exposure until those bulletins land.
