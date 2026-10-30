---
title: "OpenAI and Anthropic Claim AI Models Refuted the Exponential Time Hypothesis"
date: 2026-10-30
draft: false
description: "On October 26, 2026, OpenAI and Anthropic announced that internal AI models independently produced proofs refuting the Exponential Time Hypothesis, a 27-year-old cornerstone of theoretical computer science. Expert review is underway."
image: "https://res.cloudinary.com/csacimzi/image/upload/v1793331402/techpulse/articles/openai-anthropic-eth-refutation.jpg"
tags: [OpenAI, Anthropic, AI, computer science, Exponential Time Hypothesis, ETH, Lean, complexity theory]
categories: [Artificial Intelligence, Tech News]
author: "TechPulse"
---

On October 26, 2026, OpenAI announced that an internal AI model had produced a claimed disproof of the Exponential Time Hypothesis (ETH), a foundational conjecture in theoretical computer science proposed in 1999. Hours later, Anthropic published its own paper, credited to an internal Claude model, reaching the same conclusion via a different method. Both labs say their systems found the core results on October 16, and both released Lean formalizations. Independent experts, including two of the hypothesis’s original proposers, are examining the claims.

## What the Exponential Time Hypothesis Is

The Exponential Time Hypothesis, introduced by Russell Impagliazzo and Ramamohan Paturi (with Francis Zane), asserts that there is no subexponential-time algorithm for 3-SAT. In plain terms, for the classic satisfiability problem—deciding whether a Boolean formula in conjunctive normal form with clauses of width three can be satisfied—there is some constant δ > 0 such that every correct algorithm requires at least roughly 2^(δn) time in the worst case on n variables.

ETH underpins hundreds of conditional hardness results across graph algorithms, fine-grained complexity, databases, and other fields. If it is false, many of those conditional lower bounds collapse or must be rebuilt on different assumptions. It is strictly stronger than P ≠ NP; refuting ETH does not settle P versus NP, but it removes a widely used barrier.

## OpenAI’s Claimed Result

OpenAI released a preprint titled “The Exponential Time Hypothesis is False.” According to the company, an unreleased internal model found a natural-language argument on October 16 that was formalized in Lean the following day. The claimed algorithm is deterministic, uses polynomial space, and counts the number of satisfying assignments of any fixed-width k-CNF formula in time roughly (n + m)^O(1) · 2^(n / (log n)^(1/2 + o(1))).

Because 3-SAT is a special case, this would refute ETH. The materials, including the Lean development, were placed in OpenAI’s public mathematics repository. OpenAI asked Russell Impagliazzo, Ramamohan Paturi, and MIT’s Ryan Williams to organize an open examination of the claim. The group has stated that its involvement should not be read as certification.

## Anthropic’s Concurrent Claim

Anthropic published “A 2^o(n) Time Algorithm for 3-SAT,” listed as authored by Claude (Anthropic). The paper states that an internal research model discovered the core algorithm on October 16 “with 14M output tokens and no human input.” Anthropic notes that the result is independent and concurrent with OpenAI’s and that Claude’s literature search identified more than 800 papers whose results rest only on ETH or a stronger hypothesis.

Anthropic’s approach is described as different from OpenAI’s. Like OpenAI, Anthropic supplied a Lean 4 formalization. The paper emphasizes that the improvement is asymptotic and does not yield practical algorithms for realistic formula sizes; one analysis suggests the new method only outperforms exhaustive search on inputs with more than roughly 10 million variables.

## Verification Status and Expert Response

Both claims are accompanied by machine-checked Lean proofs, but Lean verifies only that the formal statements follow from the formal premises. It does not automatically confirm that those statements accurately capture the informal claims, nor that the underlying machine models and complexity measures are the intended ones. As of late October 2026, no independent human verification of either full proof has been published.

Impagliazzo has described the situation as not yet 100 percent certain. Williams and others note that many ETH-based papers are not immediately invalidated, but researchers will need to re-examine which results survive under weaker assumptions. Some early commentary has highlighted possible gaps between the Lean bounds and the natural-language papers, and one technical note has argued that the concrete algorithm only becomes faster than brute force for astronomically large inputs.

OpenAI also announced two additional results the same day—one in harmonic analysis related to the Kakeya problem and one in physics concerning Yang–Mills and QCD existence. Those are being handled under separate expert processes.

## Practical Implications

For theoretical computer scientists, the claims, if upheld, would force a broad reassessment of conditional hardness results that have shaped the field for more than two decades. Developers and engineers working on exact solvers or fine-grained algorithms would gain new asymptotic tools, though the results do not immediately change the practical difficulty of SAT for current instance sizes.

More broadly, the episode illustrates both the accelerating capability of frontier models on formal reasoning tasks and the still-open questions around how AI-generated mathematics should be released, reviewed, and credited. The fact that two competing labs produced closely related results on the same day, each with machine-checked formalizations, has intensified discussion about independent discovery, verification pipelines, and the role of human experts as “shepherds.”

## Why This Matters

Whether or not the proofs ultimately survive scrutiny, the announcements mark a notable moment in the intersection of artificial intelligence and pure theoretical computer science. A conjecture that has organized research for 27 years is now under active expert review because of work attributed to internal AI systems. The outcome will influence both the mathematical foundations of complexity and the evolving norms for publishing AI-assisted scientific results.

### Sources
- [Science: AI cracks a 27-year-old pillar of computer science, OpenAI and Anthropic claim](https://www.science.org/content/article/ai-cracks-27-year-old-pillar-computer-science-openai-and-anthropic-claim)
- [TechCrunch: Frontier AI labs say their models refuted the Exponential Time Hypothesis](https://techcrunch.com/2026/10/27/frontier-ai-labs-say-their-models-refuted-the-exponential-time-hypothesis-what-does-that-mean/)
- [Wikipedia: Exponential time hypothesis (updated October 2026)](https://en.wikipedia.org/wiki/Exponential_time_hypothesis)
- OpenAI public mathematics repository and Anthropic GitHub formalization (as referenced in contemporaneous reporting)
