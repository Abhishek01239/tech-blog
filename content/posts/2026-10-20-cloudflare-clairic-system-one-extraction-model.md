---
title: "Cloudflare Launches Clairic, a Fast System One Extraction Model for Typed Values"
date: 2026-10-20
draft: false
description: "Cloudflare previewed Clairic on Workers AI, a non-generative extraction model that returns typed values, estimates and forecasts from unstructured text or images in a single forward pass, claiming major speed and cost gains."
image: "https://res.cloudinary.com/csacimzi/image/upload/v1792467362/techpulse/articles/cloudflare-clairic-system-one-extraction.png"
tags: [Cloudflare, Clairic, System One, Workers AI, extraction models, AI infrastructure]
categories: [Artificial Intelligence, Software]
author: "TechPulse"
---
Cloudflare on October 19, 2026, announced a preview of Clairic, its first System One extraction model, now available on Workers AI as `@cf/cloudflare/clairic`. Unlike conventional large language models that generate text token by token, Clairic processes inputs in a single forward pass and returns structured, typed values such as numbers, dates, lists, estimates and forecasts, each with confidence scores. The company says the approach delivers higher accuracy, lower latency and lower cost for extraction-heavy tasks, and it plans to release open weights later. [1] [2]

## What Clairic does differently

System One models, inspired by Daniel Kahneman’s distinction between fast intuitive thinking and slow deliberate reasoning, prioritize speed and precision over open-ended generation. Clairic sits alongside Cloudflare’s earlier decision model Clef. Where Clef chooses among predefined options and returns probabilities, Clairic extracts or computes values that cannot be listed in advance—an invoice total, a delivery date, the number of days a shipment is late, or a repair-cost estimate. [1]

A request consists of a state (text, optionally plus up to four images) and a schema of typed fields. Supported types include text spans with character offsets, numbers (with decimal control), dates/times/datetimes, durations, lists, estimates (with median and 80% interval) and forecasts (up to 64 future steps). Every scalar answer includes a `p_null` probability that the input does not determine the value; when that probability is high the model returns null rather than guessing. Field count is effectively unlimited because the service splits large schemas across parallel passes. [2]

Pricing is $0.10 per million input tokens with no output-token charge, reflecting the single-pass design. Context window is 65,536 tokens and vision support is included. Cloudflare documents that one- and two-step arithmetic (totals, differences, date math) is reliable, while long chains of dependent calculations are better handled by extracting inputs with Clairic and finishing the math in code. [2]

## Early results and cascade potential

In a 21-day TSA checkpoint travel-volume forecast that used the prior 90 days of data, Clairic’s median predictions showed an average absolute error of 3.3 percent; 17 of the 21 actual daily counts fell inside the model’s 80 percent prediction interval. The model recovered the weekly pattern (quieter Tuesdays and Saturdays, busier Thursdays–Sundays) without explicit calendar features. [1]

Cloudflare also published an internal damage-claim pipeline comparison. A cascade of Clairic (extraction) → Clef (decision) → GLM-5.3 (reply writing) finished in 19.3 seconds end-to-end versus 61.7 seconds when every step used GLM-5.3 alone—roughly 3.2× faster and 49 percent cheaper ($6,032 versus $11,740 per million claims). Extraction and decision together took under a second with the specialized models versus 38 seconds with the LLM. These figures are Cloudflare’s own measurements; independent third-party evaluations have not yet been published. [1] [2]

## Practical implications

For developers building document-processing, claims, logistics or forecasting workflows, Clairic offers a way to replace expensive, high-latency LLM calls for the structured portion of the pipeline. Because answers are typed and carry explicit confidence and null probabilities, downstream code can route low-confidence results to human review without additional parsing. The ability to chain Clairic with Clef and a conventional LLM creates a clean extract-decide-write pattern that can be cheaper and more consistent run-to-run than an all-LLM stack. [1]

Limitations remain: multi-step arithmetic and complex aggregations are weak, forecasting is described as basic, and confidence intervals can be miscalibrated on data far from the training distribution. The model is still in preview and open weights are not yet available. Organizations evaluating it should therefore test on their own schemas and data distributions before relying on the published cascade numbers. [2]

Clairic illustrates a broader shift toward specialized, non-generative models for the high-volume structured tasks that currently dominate enterprise LLM spend. If the preview performance holds under independent scrutiny and open weights appear, it could accelerate the adoption of hybrid pipelines that reserve large language models for the open-ended reasoning and writing steps where they remain strongest.

## Why It Matters

Clairic targets the part of enterprise AI spending that involves pulling structured values out of documents rather than generating prose, and Cloudflare prices it without an output-token charge. The published cascade comparison, measured by Cloudflare and not independently verified, suggests that routing extraction and decisions to specialized models can cut both latency and cost in high-volume pipelines. The practical question for buyers is whether typed outputs and confidence scores stay calibrated on their own schemas, particularly where dependent calculations are involved.

### Sources
[1] [Cloudflare Blog: Introducing Clairic, a new System One class of extraction models](https://blog.cloudflare.com/clairic-extraction-model/)
[2] [Cloudflare Workers AI documentation: clairic](https://developers.cloudflare.com/workers-ai/models/clairic/)
