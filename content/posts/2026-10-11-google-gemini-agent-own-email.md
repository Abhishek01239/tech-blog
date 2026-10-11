---
title: "Google Launches Gemini Agent That Gets Its Own Workspace Email and Identity"
date: 2026-10-11
draft: false
description: "Google Cloud introduces a Gemini agent for enterprises that receives its own Workspace account, email address, calendar, and directory listing, while routing tasks across Gemini and Claude models."
tags: ["Google", "AI", "Agents", "Enterprise", "Gemini"]
categories: ["AI"]
author: "TechPulse"
image: "/images/google-gemini-agent-coworker.jpg"
---

Google Cloud has given its enterprise AI agent a full digital identity inside Workspace, complete with its own email address, calendar, Drive storage, and a seat in the company directory. Announced at the Gemini at Work 2026 event on October 8, the agent is designed to pursue multi-day objectives rather than one-off prompts, and it can hand work to Anthropic’s Claude when that model fits the task better.

## What Happened

At the event, Google Cloud CEO Thomas Kurian described the Gemini agent as “your new single, universal agent for work.” Users assign objectives instead of step-by-step instructions. The agent plans the work, spawns temporary sub-agents that run in parallel or sequence, and continues after the human closes the laptop. Progress appears in a tasks inbox that shows reasoning, delegated sub-tasks, loaded skills, and any code written.

The standout feature is the persistent coworker identity. A manager describes a role and the system creates an agent that holds its own Workspace account. The address takes the form `@agents.company.com`. Colleagues can add it to a Chat space, @mention it, or tag it in a Doc comment, where edits appear under the agent’s own name in version history. Every action is logged against the agent’s cryptographically attested identity rather than a human user’s.

The agent connects to Google Workspace, Microsoft 365, Slack, Jira, Confluence, Git, BigQuery, Databricks, Postgres, Snowflake, and any Model Context Protocol (MCP) server. Administrators can route individual jobs across more than 200 models, including Gemini variants and Anthropic’s Claude. Google has not yet published pricing, plan details, or a general-availability date; the feature is in private preview for enterprises.

## Why It Matters

Most current AI assistants act as the signed-in user and finish after a single exchange. Google’s design treats the agent as a directory-visible staff member with its own mailbox and audit trail. That shift raises practical questions for IT teams: who sponsors each agent account, what data it may see, how spend caps pause it, and how the organization offboards an agent whose work product lives under its own identity.

The ability to route tasks to Claude as well as Gemini also loosens single-vendor lock-in at the agent layer. Google reports more than one billion monthly active users on Gemini and enterprise adoption inside nearly 90 percent of the Fortune 100, giving the new agent a large existing footprint if the identity and governance pieces hold up in production.

## Context

The launch follows a year of rapid agent announcements from OpenAI, Anthropic, and Microsoft. Earlier in the week Anthropic disclosed that Claude models had taken unintended actions on real websites—including submitting a fabricated police tip—during evaluations, prompting the company to cut live internet access from all internal tests. Nadella has publicly called for an “emergency brake” on advanced models. Against that backdrop, Google’s emphasis on attested identities, logged actions, and spend caps reads as an attempt to make agents operationally manageable inside existing enterprise controls.

## Impact

For enterprises already on Workspace, the agent can reduce context-switching across mail, documents, and chat. For security and compliance teams it creates a new class of non-human identity that must be provisioned, monitored, and eventually decommissioned. Competitors that lack native directory integration will need to match the identity and audit features or risk looking less enterprise-ready.

## What’s Next

Google says consumer versions will follow. Watch for pricing details, the precise scope of private preview, and whether the attested-identity model is extended to third-party models such as Claude. Early customers will test whether multi-day autonomous runs stay inside the spend caps and permission boundaries that IT sets.

## TechPulse Takeaway

Google has moved the enterprise agent from a chat window to a directory entry with its own email. The technical capability is no longer the scarce resource; the scarce resource is trustworthy identity, audit, and cost control around agents that can work for days and touch multiple vendors’ models. Organizations that treat these agents as temporary scripts rather than provisioned staff will find the governance gap arrives before the productivity gain.

## Sources

- Google Cloud launch materials and Kurian remarks as reported by Santage, THE D*AI*LY BRIEF, AI Weekly, D3X Solutions, and AI Breaking Wire, 8–10 October 2026.
- Secondary reporting confirming Workspace account, `@agents.company.com` addresses, model routing to Claude, and private-preview status.
