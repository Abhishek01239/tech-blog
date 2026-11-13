---
title: "Microsoft Launches Decision-1: Fast Decision-Scoring Model Built on Qwen3.5-9B"
date: 2026-10-11
draft: false
description: "Microsoft introduced Microsoft-Decision-1 on October 9, 2026, a specialized decision-scoring model post-trained from Alibaba’s Qwen3.5-9B. It returns calibrated probabilities for fixed answer options and is available in Microsoft Foundry and OpenRouter."
tags: ["Microsoft", "AI", "Machine Learning", "Decision Models", "Qwen", "Azure"]
categories: ["AI"]
author: "TechPulse"
image: "https://res.cloudinary.com/muc9b5sj/image/upload/v1791737362/techpulse/articles/microsoft-decision-1-model.jpg"
---

Microsoft has released Microsoft-Decision-1, a purpose-built decision-scoring model designed for routing, classification, prioritization, verification, and workflow control. Announced on October 9, 2026, by Achint Srivastava, VP of Software Engineering in the Office of the CTO, the model is available in public preview through Microsoft Foundry and via OpenRouter.

Unlike general-purpose large language models that generate free-form text, Decision-1 takes a state description and a fixed set of answer options and returns a calibrated probability for each option. This structured output is intended for software systems that need to act immediately on the result.

## How the Model Works

Microsoft post-trained Alibaba’s open-weight Qwen3.5-9B for single-pass decision scoring. The company plans to rebase the model on other foundations, including Microsoft AI (MAI) and OpenAI models, in the future. The current version supports yes/no questions, multiple-choice selections, ratings, and rubric-based grading of AI responses or agent actions.

It accepts text input with a 32,768-token context window and returns JSON. Pricing is $0.042 per million input tokens, with output tokens free. The weights are not released; the model is offered only as a hosted API.

Microsoft emphasized five design goals: low latency (P50 around 85 ms in its tests), generalization across held-out benchmarks, robustness to paraphrasing and reordering of options, well-calibrated probabilities, and safety filtering that refuses harmful requests while preserving utility.

## Benchmark Results

In Microsoft’s internal evaluation across 36 benchmarks covering nearly 150,000 questions kept blind from training, Decision-1 achieved the highest average accuracy at 83.5%. It outperformed Jev 1.13.0 (82.3%), Quyet-1.0-Large (81.9%), GPT-6 Luna Decisions (79.4%), and several other specialized decision models.

Latency was a standout: the model was reported as approximately 2.5 times faster than the next-best decision model and roughly 35 times faster than GPT-6 Sol on the same tasks. Calibration scored 92.2 (where 100 is perfect). Robustness testing showed decisions changed on only 1.3% of perturbations on average, with zero flips when option descriptions were paraphrased or options were reordered.

These figures come from Microsoft’s own reporting. Independent third-party benchmarks were not available at the time of the announcement.

## Internal Use Cases at Microsoft

Microsoft has already deployed Decision-1 internally in several places:

- Xbox Research used it to classify more than 10,000 pieces of open-ended feedback into researcher-defined themes, finding it competitive with GPT-6 Sol while running more than 14 times faster and 200 times less expensive.
- The Copilot team applied it to quality measurement of chat and agent responses, describing performance as competitive with GPT-5.6 Luna at roughly 100 times the speed.
- On-call engineers tested it for retrieving relevant knowledge during live incidents.
- Microsoft Discovery used it for adaptive replanning in scientific experiments, reporting greater consistency and nearly four times the overall speed compared with an LLM-based approach.

These examples illustrate the intended role: a fast, reliable decision layer inside larger agentic or workflow systems rather than a replacement for generative models.

## Implications for Developers and Enterprises

Decision models like this one reflect a broader shift toward modular AI architectures. Not every step in an agent or application requires open-ended generation. Routing a request to the right tool, classifying user intent, verifying an intermediate result, or grading an agent action can often be handled more efficiently by a specialized scorer.

For developers building on Microsoft Foundry or using OpenRouter, Decision-1 offers a low-cost, low-latency option for these structured tasks. Because output is free and latency is low, it can be inserted into multi-step pipelines without dominating the cost or delay budget. The closed weights and Azure-hosted nature may appeal to organizations that prefer managed models over self-hosting open-weight alternatives.

At the same time, the reliance on Microsoft’s own benchmarks means teams should validate performance on their specific decision distributions before production use. The lack of multimodal support (text only) also limits applicability compared with some competing decision APIs that accept images.

## Why It Matters

The release of Microsoft-Decision-1 underscores that frontier AI progress is no longer solely about larger generative models. Specialized architectures optimized for speed, calibration, and structured output are becoming practical building blocks. For organizations already invested in the Microsoft ecosystem, it provides an immediately available tool for making agent workflows faster and more reliable. For the wider industry, it signals that decision-scoring models are maturing into a distinct, commercially relevant category alongside traditional LLMs.

## Sources

- Microsoft Command Line, "Introducing Microsoft-Decision-1, our model for fast decision-making," October 9, 2026: https://commandline.microsoft.com/microsoft-decision-1-model-foundry/
- Microsoft Tech Community, "Introducing Microsoft-Decision-1 in Microsoft Foundry," October 9, 2026: https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-microsoft-decision-1-in-microsoft-foundry-for-decision-and-classific/4562742
- MarkTechPost, "Microsoft AI Releases Microsoft-Decision-1: A Qwen3.5-9B Decision-Scoring Model," October 9, 2026: https://www.marktechpost.com/2026/10/09/microsoft-ai-releases-microsoft-decision-1-a-qwen3-5-9b-decision-scoring-model/
- OpenRouter model listing for microsoft/microsoft-decision-1
