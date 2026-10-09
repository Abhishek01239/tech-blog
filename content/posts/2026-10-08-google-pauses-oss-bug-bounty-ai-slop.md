---
title: "Google pauses open-source bug bounty over AI slop"
date: 2026-10-08
draft: false
description: "Google paused new product reports to its open-source bug bounty after a surge of mostly invalid AI submissions overwhelmed human reviewers."
tags: ["cybersecurity", "google", "ai", "bug-bounty"]
categories: ["Cybersecurity"]
author: "TechPulse"
image: "/images/google-pauses-oss-bug-bounty-ai-slop.jpg"
---

Google has temporarily stopped accepting new product vulnerability reports through its Open Source Software Vulnerability Reward Program, citing a sharp rise in automated submissions that human reviewers say are mostly wrong.

## What Happened

The company announced the pause on October 1, 2026, in posts on X and on the program page. Google said the freeze was driven by a significant rise in automated submissions, the vast majority of which are not valid. Engineers described polished write-ups that still failed basic checks: wrong triggering conditions, exploit paths that do not exist, and claims that a weak function was reachable when it was not.

The pause is narrower than a full shutdown. Reports already in the queue continue to be reviewed. Supply-chain bug reports remain open, as does the Patch Rewards Program. Some product issues in Google Cloud repositories may still be filed through the Cloud VRP. Google said it will rework this part of the OSS VRP and commit to an update in the first quarter of 2027.

The program, introduced in 2022, pays researchers for flaws in public projects owned by Google organizations, including Go, Angular, Bazel, Protocol Buffers, and Fuchsia. It is one of the clearer routes for independent researchers to get paid for work on widely used open-source infrastructure.

## Why It Matters

Bug bounties were built on a bargain: skilled people find real flaws, vendors pay, and software gets safer. Generative tools have flooded that bargain with volume. A model can draft a convincing report in minutes. A maintainer still has to reproduce it. When most of those reports are hallucinations, the cost shifts onto the people who were supposed to be protected by the program.

Google is not alone. Maintainers of projects such as curl have described similar waves of machine-written reports that look complete and collapse under testing. Intel has faced the same pattern. The result is a triage problem that scales with model usage, not with the number of real bugs.

The company had already adjusted other programs. In May it cut standard Chrome payouts and began favoring short reports with concrete proof, a direct response to AI-assisted discovery. The OSS pause is the sharper version of that policy: stop intake until the filter works.

## Industry Impact

Security teams that rely on Google's open-source stack should not read the pause as a claim that those projects are suddenly safer. It is an admission that the reporting channel is broken. Independent researchers who were using the OSS VRP for product bugs now have fewer paid paths, at least until early 2027. Firms that productized AI vulnerability scanners will face more skepticism from the programs they were feeding.

Platforms such as HackerOne and vendor programs at Microsoft, Apple, and Meta are watching the same curve. If Google, with a large security organization, cannot absorb the noise, smaller maintainers have even less room. Expect more programs to demand proof-of-concept code, reject narrative-only reports, and rate-limit new accounts.

## What's Next

Google's Q1 2027 update will be the test. A useful redesign would separate machine-assisted discovery from machine-written claims, require reproducible evidence, and keep a lane open for supply-chain issues. Until then, researchers should route eligible Cloud findings through the Cloud VRP and treat the OSS product channel as closed.

The broader question is whether bounty economics survive a world where generating a report is cheap and verifying it is not. Programs that pay for verified fixes, rather than for plausible prose, are the ones likely to stay open.
