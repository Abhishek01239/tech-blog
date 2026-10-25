---
title: "Moonshot Removes Cyber Training Data From Kimi K3.1 Pro"
date: 2026-10-25
draft: false
description: "Moonshot says it removed cyber-related data from Kimi K3.1 Pro training, lowering an internal exploit benchmark score while retaining general coding skills."
image: "/images/2026-10-25-moonshot-kimi-cyber-safety.jpg"
tags: [Moonshot AI, Kimi, AI safety, Cybersecurity, Open-weight models]
categories: [Artificial Intelligence, Security]
author: "TechPulse"
---
Moonshot AI says it removed cyber-related material from the training and reinforcement-learning stages for Kimi K3.1 Pro, aiming to reduce vulnerability-exploitation performance while retaining general coding skills. Reuters reported the change on Oct. 24 as the Beijing-based company announced the model and plans to publish its full weights by Nov. 4. [1] [3]

## A training-stage intervention

Moonshot says cyber content was present in its mid-training corpus and vulnerability-research tasks appeared in its reinforcement-learning environment. For the open-weight version, it says it identified and removed cyber-related data from both stages while keeping general coding tasks. The intervention is a training-level measure, not a promise that users will be blocked from misusing weights after downloading them. [1] [3]

The company reported that K3.1 Pro scored 81.0% pass@3 on its internal xdev-bench-hard evaluation. A comparison checkpoint trained without the risk-reduction measures scored 90.5%. Moonshot describes the benchmark as testing source-code vulnerability discovery and exploitation in sandboxed environments. Reuters noted that the results had not been independently verified, so the figures should be read as the company’s own comparison rather than an external safety assessment. [1] [3]

The News also reported the same benchmark scores and training changes. [2]

## Open weights leave a harder control problem

Open weights give outside developers more ability to run and modify a model than a hosted service generally allows. Reuters reports that Moonshot argues open models can help organizations inspect and secure software, including older code, while saying it does not want to release weights that extend the absolute frontier of cyber capability. [1]

Moonshot frames the change as a trade-off between limiting offensive cyber performance and preserving dual-use coding capabilities for defensive work. Whether removing selected training data reliably reduces harmful capability after release, or how downstream users may adapt the model, remains uncertain. The company’s planned Nov. 4 release date is a future target, not confirmation that the weights are already public. [1] [3]

### Sources
[1] [Reuters: Moonshot curbs hacking ability in new Kimi model](https://www.reuters.com/technology/moonshot-curbs-hacking-ability-new-kimi-model-fears-grow-over-ai-powered-2026-10-24/)
[2] [The News: Moonshot AI restricts open-weight hacking ability in Kimi](https://www.thenews.com.pk/latest/1421096-moonshot-ai-restricts-open-weight-hacking-ability-in-new-kimi-model-as-fears-grow-over-ai-powered-cyberattacks)
[3] [Moonshot AI: Introducing Kimi K3.1 Pro](https://www.kimi.ai/blog/kimi-k3-1-pro)
