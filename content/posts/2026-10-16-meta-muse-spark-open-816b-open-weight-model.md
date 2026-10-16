---
title: "Meta Releases Muse Spark Open: 816B Open-Weight Model for Agentic Coding"
date: 2026-10-16
draft: false
description: "Meta has released open weights for Muse Spark Open, an 816-billion-parameter mixture-of-experts model with 42B active parameters and a 1M-token context window, optimized for coding agents and capable of running on two Apple Mac Studios."
image: "https://res.cloudinary.com/csacimzi/image/upload/v1792121799/techpulse/articles/meta-muse-spark-open-816b-open-weight-model.jpg"
tags: [Meta, Muse Spark Open, Open Weight Models, AI Agents, Coding]
categories: ["AI"]
author: "TechPulse"
---

Meta has released the weights for Muse Spark Open, describing it as the most capable open-weight model from a US lab to date. The natively multimodal model features 816 billion total parameters with only 42 billion active per token, a 1-million-token context window, and is built specifically for coding and long-horizon agentic tasks. It is available now on Hugging Face and multiple cloud platforms, with a notable optimization for running locally on two Apple M5 Ultra Mac Studios.

## Architecture and Capabilities

Muse Spark Open is a sparse mixture-of-experts transformer. For each token, only a subset of experts activates, keeping inference compute closer to a 42B dense model while providing the capacity of a much larger network. It accepts text, images, documents, audio, and audio-video as input and produces text output. Meta trained it on real developer workflows, including multi-file refactors and extended debugging sessions, so it can plan, act, observe results, and self-correct over long horizons.

The model includes a separate commentary channel that lets it state intent before acting, improving transparency in agent workflows. It also supports coordinating sub-agents for complex tasks. Additional safety post-training was applied so the open-weight version remains more robust when used without Meta’s hosted guardrails.

## Desktop-Scale Deployment

One of the most distinctive claims is that Muse Spark Open is the first model in its class that can run on a desktop. Meta worked with Apple to optimize it for two M5 Ultra Mac Studios using the MLX framework. Together the machines provide roughly a terabyte of unified memory. Meta demonstrated fully on-device agentic workflows, including shipping real code changes to an open-source iOS app and reviewing video footage frame-by-frame in DaVinci Resolve.

Weights are available in BF16 and NVFP4 quantized formats. The model card indicates that NVFP4 requires at least 700 GB of GPU memory while BF16 needs around 2 TB. It runs on common inference engines including SGLang, vLLM, and others, with support for NVIDIA, AMD, and Intel hardware in addition to Apple silicon.

## Benchmarks and Positioning

Meta positions Muse Spark Open as leading on certain agentic evaluations. On JobBench it scored 61.8, and on MCP-Atlas (tool use across many servers) it scored 89.2, the highest in Meta’s comparison table. On other measures such as the Artificial Analysis Intelligence Index it trails some Chinese open models including GLM 5.3 and Kimi K3. Coding benchmarks such as Terminal-Bench 2.1 show solid but not leading results relative to the strongest open competitors.

The release continues Meta’s open-weight strategy after earlier Muse Spark closed releases and the smaller Muse Glimmer model. It is licensed under the Muse Model License with limited commercial terms that allow many developers to use and adapt it without a fee.

## Availability

Weights can be downloaded from Hugging Face (meta-models/Muse-Spark-Open-816B-A42B), Amazon SageMaker, Google Cloud Model Garden, and Microsoft Foundry. Hosted API access is available through Baseten, Fireworks AI, Groq, Modal, Nebius, OpenRouter, Together AI, and others. PyTorch’s TorchTitan now includes a model definition so developers can fine-tune it with SFT, LoRA, or reinforcement learning.

## Why It Matters

Open-weight frontier-class models remain rare from major US labs. Muse Spark Open gives developers and enterprises the ability to run, customize, and deploy a highly capable agentic coding model on their own infrastructure or even on high-end consumer hardware. The combination of a million-token context, strong tool use, multimodal perception, and desktop viability lowers the barrier for organizations that prefer not to rely solely on closed API providers. At the same time, the hardware requirements and mixed benchmark results mean it will not replace every existing option overnight, but it meaningfully expands the choices available for building long-running AI coding agents.

## Sources

- Meta AI Research: [Introducing Muse Spark Open](https://research.meta.ai/blog/muse-spark-open)
- PyTorch Blog: [Muse Spark Is Now an Open-Weights Model](https://pytorch.org/blog/muse-spark-open/)
- AWS: [Muse Spark Open model now available on Amazon SageMaker JumpStart](https://aws.amazon.com/about-aws/whats-new/2026/01/muse-spark-open-on-sagemaker-jumpstart/)
- SiliconANGLE: [Meta releases 816B-parameter Muse Spark Open](https://siliconangle.com/2026/10/15/meta-releases-816b-parameter-muse-spark-open-for-coding-and-agent-work/)
