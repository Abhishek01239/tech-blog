---
title: "Strange Bedfellows: Samsung Turns to TSMC to Build Nvidia's Custom NVHBM Memory"
date: 2026-10-20
draft: false
description: "Samsung Electronics will reportedly use rival TSMC's 3nm process for the base dies of Nvidia's next-generation custom HBM memory. The unprecedented tie-up between two decades-long foundry rivals signals how much power Nvidia now wields over the entire AI chip supply chain."
tags: [AI, Semiconductors, Nvidia, Samsung, TSMC, HBM, Hardware]
categories: ["Tech News"]
author: "TechPulse"
---

# Strange Bedfellows: Samsung Turns to TSMC to Build Nvidia's Custom NVHBM Memory

In an industry defined by fierce rivalry, one of the most unexpected partnerships in recent memory is taking shape. According to a report by the Seoul Economic Daily published on October 18, Samsung Electronics will use Taiwan Semiconductor Manufacturing Company's 3-nanometer process to produce base dies for Nvidia's next-generation custom high-bandwidth memory, known as NVHBM. If confirmed, the arrangement would mark the first time the two companies — which have spent more than two decades locked in cutthroat competition for contract chipmaking supremacy — have ever worked together at the HBM manufacturing stage.

## Why the Base Die Matters

To understand why this is such a big deal, it helps to look at how HBM is built. High-bandwidth memory chips are vertical stacks of DRAM dies connected through silicon vias, all sitting on top of a logic layer called the base die. That base die handles the interface between the memory stack and the processor it feeds — routing signals and managing power delivery. In Nvidia's NVHBM design, unveiled in August 2026, the base die plays an even more aggressive role: it absorbs the memory controller that traditionally sat on the GPU itself, freeing precious space on the processor for more compute circuits.

That architectural shift is what pulls TSMC into the picture. To make room for the on-package controller, Nvidia shrank the physical layer — the circuitry that exchanges electrical signals with external chips — by roughly 60% compared with standard HBM. The result, according to reports, is a memory system offering up to 30% more bandwidth and 15% lower power consumption than standard seventh-generation HBM4E. But the denser logic design demands an advanced process node with high manufacturing yields — something Nvidia believes only TSMC's 3nm technology can reliably deliver at scale.

## Nvidia Calls the Shots

The deeper story here is about power dynamics in the AI hardware ecosystem. Nvidia has reportedly asked all three of its major memory suppliers — Samsung, SK hynix, and Micron Technology — to build NVHBM base dies on TSMC's 3nm process, while standardizing the core DRAM dies on sixth-generation (1c) technology. The goal is consistency: by forcing every supplier onto the same foundry process for the same critical component, Nvidia can ensure uniform performance across vendors and dramatically simplify product validation.

Samsung's agreement reportedly came only after an internal review — a telling detail, given that the decision touches not just its memory division's relationship with its biggest customer, but its foundry division's positioning as TSMC's leading alternative. Industry estimates cited in Korean media put TSMC's 3nm yields above 90%, compared with roughly 60% for Samsung Foundry's comparable 2nm process. For a component as complex as the NVHBM base die, that yield gap translates directly into cost and supply reliability.

Notably, Samsung isn't abandoning its in-house approach entirely. The company plans to keep its "turnkey" model — where both the memory and the base die come from its own fabs — for standard HBM4 and HBM4E products, and for custom HBM it builds for other clients, including AMD. It is also quietly validating NVHBM base die production on its own 2nm process as a hedge, preparing for the possibility that demand outstrips TSMC's capacity. Volume production of NVHBM is expected to begin in 2027.

## Supply Chain Meets Demand Shock

The timing is no accident. HBM demand is forecast to jump around 90% next year as AI accelerator production scales relentlessly, and TSMC is racing to add capacity — with new 3nm lines planned at Fab 18 in Tainan, additional fabs in Arizona and Kumamoto, and a new Tainan facility slated for mass production in the first half of 2028. Even so, analysts question whether supply can keep pace with the AI buildout, and this week's trillion-dollar selloff in AI and semiconductor stocks — partly driven by Broadcom CEO Hock Tan's warnings about financing constraints — has only sharpened scrutiny of how the industry's enormous capital commitments will pay off.

Against that backdrop, the Samsung–TSMC arrangement reads as pragmatism winning over pride. If the memory chips feeding Nvidia's next-generation AI platforms need the best logic process available, then rivalry takes a back seat — at least for this one component. It also underscores a broader trend: the biggest AI chip designers increasingly dictate terms across the entire supply chain, reshaping relationships between suppliers that once competed purely on their own terms.

Neither Samsung nor TSMC has publicly confirmed the arrangement, so some details may shift. But if the reports hold, the era of strictly partitioned foundry loyalty is over — and Nvidia just redrew the map of the semiconductor industry's alliances.
