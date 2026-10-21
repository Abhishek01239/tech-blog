---
title: "AMD, Intel Align PyTorch CPU Work Around oneDNN"
date: 2026-10-21
draft: false
description: "AMD and Intel will combine x86 PyTorch CPU optimizations in oneDNN, with ZenDNN moving into the shared open-source path to reduce software fragmentation."
image: "/images/2026-10-21-amd-intel-pytorch-onednn.jpg"
tags: [AMD, Intel, PyTorch, oneDNN, ZenDNN, x86 CPUs, AI software]
categories: [Artificial Intelligence, Developer Tools]
author: "TechPulse"
---
AMD and Intel announced on Oct. 20 that they plan to combine their x86 CPU optimization work for PyTorch in oneDNN, an open-source deep-learning library. The companies say a shared software path should reduce vendor-specific fragmentation for developers building AI workloads on AMD and Intel processors. [1] [2]

## AMD’s ZenDNN work moves into oneDNN

AMD plans to integrate its ZenDNN optimizations into oneDNN while continuing to tune the library for its processors. The companies also say they have aligned on oneDNN as the default open-source library for x86 acceleration within PyTorch, following a recommendation from the x86 Ecosystem Advisory Group. [1] [2]

For developers, the intended benefit is a common integration point across two processor vendors. The announcement does not promise identical performance on AMD and Intel hardware, nor does it include benchmark results for the planned work. Actual effects will depend on implementation and future software releases. [1] [2]

## Additional work remains planned

AMD also said it has joined the Unified Acceleration Foundation as a Steering Member. The companies identify oneDNN as a project governed by the foundation, giving AMD a formal role in its open-source work. [1] [2]

A separate collaboration concerns AI Compute Extensions, or ACE, a planned x86 instruction-set architecture intended to accelerate matrix multiplication. AMD and Intel say support is planned for future integration into PyTorch through oneDNN updates. The announcements did not specify a release date, so ACE support should be treated as future work rather than a feature available now. [1] [2]

The immediate news is software alignment: AMD’s ZenDNN work is slated to join the oneDNN ecosystem, while both vendors back that library as PyTorch’s default x86 acceleration path. Whether the move simplifies deployments or changes workload performance will become clearer as code lands and users test it across systems. [1] [3]

### Sources
[1] [AMD: Collaborating with Intel to simplify AI development on x86 CPUs with PyTorch](https://newsroom.amd.com/news/amd-intel-collaborate-simplify-ai-development-on-x86-cpus-pytorch/)
[2] [Intel: AMD and Intel collaborate to simplify AI development on x86 CPUs using PyTorch](https://www.intel.com/content/www/us/en/newsroom/news/data-center/amd-intel-simplify-x86-ai-development-with-pytorch.html)
[3] [Wccftech: AMD folds ZenDNN optimizations into oneDNN](https://wccftech.com/intel-amd-onednn-x86-cpu-ai-development-pytorch/amp/)
