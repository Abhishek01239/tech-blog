---
title: "Anthropic rolls out 3-tier access for cyber models"
date: 2026-10-08
draft: false
description: "Anthropic merged its cyber verification and Glasswing programs into three access tiers for Claude Opus 5.5, Sonnet 5.5, and Mythos 5.1."
tags: ["anthropic", "ai", "cybersecurity", "claude"]
categories: ["Artificial Intelligence"]
author: "TechPulse"
image: ""
---

Anthropic is folding its Cyber Verification Program and Project Glasswing into one offering, with three tiers of access to its most capable models for security teams that can prove who they are.

## What Happened

The company updated the program in October 2026 and said the change is live for Claude Opus 5.5, Claude Sonnet 5.5, Claude Mythos 5.1, and new models going forward. Until now the two programs ran separately. Glasswing gave organizations securing critical software access to Claude Mythos. The original Cyber Verification Program loosened safeguards on Opus and Sonnet for approved teams.

Under the new structure every tier includes those frontier models, but verification requirements and security controls differ. Defense Access covers security operations, incident response, malware reverse engineering, and vulnerability analysis. Eligible applicants include teams defending their own systems, critical-infrastructure operators, small security firms, open-source maintainers, and individual researchers with a history of reported bugs. Anthropic says it aims to answer those applications within a few days.

Red Team Access adds authorized penetration testing, limited to systems the organization is allowed to test. Actions that could cause physical harm or mass disruption, including ransomware deployment, stay blocked in real time. A webinar on the program is scheduled for October 14 at 9 a.m. PT. First-party access runs through Claude.ai, Claude Code, and the Anthropic API. Amazon Bedrock availability is limited to customers with Enterprise Frontier Safeguards.

## Why It Matters

Frontier labs have spent two years tightening classifiers that stop models from helping with intrusion. Those same classifiers block defenders who need the model to read malware, trace an exploit, or draft a detection rule. Anthropic's answer is not to drop the guardrails. It is to identify the user and then relax them.

The three-tier design is an attempt to match capability to trust. A SOC analyst reversing a sample is a different risk from a contractor running an offensive engagement. Putting both behind one checkbox made the program either too loose or too slow. Splitting them is how the company tries to keep defensive use available without handing the same model, unrestricted, to anyone with an API key.

## Industry Impact

Security vendors that wrap Claude for detection and response now have a formal path instead of informal exceptions. Open-source maintainers, a group Google just made harder to pay through its OSS bounty, get a named lane into Anthropic's strongest models. That is a small but real shift in who can use frontier systems for defense.

Rivals will be pushed to publish similar programs. OpenAI and Google already gate some cyber capabilities. Enterprises buying model access will start asking which tier they are on, what is still blocked, and whether logs stay in their cloud. Anthropic's Enterprise Frontier Safeguards, which let regulated customers keep Claude logs in AWS, Azure, or GCP under their own keys, is the storage half of the same pitch.

## What's Next

The October 14 webinar should clarify evidence requirements and how fast Red Team Access is approved. The practical test is whether incident responders get through in days, not weeks, when a live case is underway. If the queue slips, teams will keep using weaker, less restricted models for the work that matters most.

Watch also for whether the real-time blocks on mass-disruption tasks hold once red teams are inside the program. A verification badge is only useful if the remaining limits are specific and enforced.
