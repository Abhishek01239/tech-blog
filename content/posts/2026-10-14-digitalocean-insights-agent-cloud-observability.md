---
title: "DigitalOcean Puts Agent and Cloud Telemetry in One Insights Console"
date: 2026-10-14
draft: false
description: "DigitalOcean has opened Insights in public preview, bringing selected agent, application, and infrastructure metrics, logs, and traces into one OpenTelemetry-based service."
image: "/images/2026-10-14-digitalocean-insights-observability.jpg"
tags: [DigitalOcean, Observability, OpenTelemetry, AI Agents, Cloud]
categories: ["Cloud"]
author: "TechPulse"
---

DigitalOcean has opened Insights in public preview, giving teams a single place to inspect telemetry from selected AI-agent services, applications, and cloud infrastructure. The company says the service is built into supported DigitalOcean products, so users do not need to install a separate collector or instrument those products to begin viewing their signals. [1]

## One view across supported services

Insights collects metrics and logs for DigitalOcean's Serverless Inference, Batch Inference, Inference Router, Managed Agents, and Action Gateway products. Action Gateway also provides traces that can follow an agent turn across model calls and tool use. DigitalOcean Kubernetes (DOKS) and App Platform contribute metrics, while DOKS also provides logs. That is useful coverage for teams running an agent and its supporting services on DigitalOcean, but it is not a claim that every cloud resource or outside application is automatically monitored. [1]

The service is based on OpenTelemetry, an open standard for collecting and moving observability data. DigitalOcean's announcement lists dashboards, explorers for metrics, logs, and traces, visual queries or PromQL, metric alerts, an API, and role-based access controls. Developers can inspect signals such as token throughput, latency, errors, and estimated cost across supported inference and agent workflows. [1]

Developer-Tech's coverage likewise describes the preview as a unified control plane for agent and infrastructure telemetry, and notes that the service includes alerting and programmatic controls. [2]

## Preview means preview

DigitalOcean says Insights carries no additional charge during public preview, subject to usage and data-retention limits. The company expects to begin charging when the service reaches general availability and says it will announce pricing before billing starts. It also cautions that the preview is not guaranteed to perform for production-level workloads. [1]

The launch addresses a real operational gap: an agent failure can originate in a model call, a tool, a routing layer, or the infrastructure underneath, while each system may expose separate logs and metrics. Correlating those signals can shorten investigations. But teams should check which products and signals are supported today, and treat preview reliability and eventual pricing as unresolved until DigitalOcean publishes final terms.

## References

[1]: https://www.digitalocean.com/blog/introducing-insights "DigitalOcean: Introducing Insights"
[2]: https://www.developer-tech.com/news/digitalocean-launches-insights-to-unify-agent-and-infrastructure-observability/ "Developer-Tech: DigitalOcean launches Insights"

## Why It Matters

By building on OpenTelemetry and embedding collection in its own products, DigitalOcean is competing on convenience as much as on features: teams can start without installing a separate collector, but the signals they see are bounded by the products the service supports. The inclusion of dashboards, PromQL queries, alerts, an API, and role-based access suggests the preview is aimed at everyday operations rather than a narrow demo. Its value will hinge on whether those controls remain available once the service moves beyond preview and billing begins.

### Sources

[1] [DigitalOcean: Introducing Insights](https://www.digitalocean.com/blog/introducing-insights)
[2] [Developer-Tech: DigitalOcean launches Insights](https://www.developer-tech.com/news/digitalocean-launches-insights-to-unify-agent-and-infrastructure-observability/)
