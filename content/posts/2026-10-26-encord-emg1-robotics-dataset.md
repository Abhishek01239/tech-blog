---
title: "Encord Introduces EMG-1 Dataset Pairing Muscle Signals With Video for Robot Training"
date: 2026-10-26
draft: false
description: "Encord’s EMG-1 pairs wrist muscle signals with first-person video in an open robotics dataset to test hand tracking when cameras miss fingers."
image: "/images/2026-10-26-encord-emg1-robotics-data.jpg"
tags: [Encord, robotics, Physical AI, EMG-1, datasets, computer vision]
categories: [Artificial Intelligence, Robotics]
author: "TechPulse"
---

Encord introduced EMG-1, an open dataset combining wrist electromyography (EMG) recordings with synchronized first-person video, at its Long Horizon Physical AI Summit in San Francisco on Oct. 20. The release was part of the company’s new Encord Data Labs research division, and the event included a Jenga demonstration of how muscle signals could complement camera views when hands are obscured by objects. [1] [2] [3]

## A dataset, not a deployed robot system

Encord’s announcement describes EMG-1 as a research dataset, not a ready-to-deploy robot-control product. The company said it was developed with Wearable Devices and made available through an access request, with a full collection exceeding 300 hours and an eight-channel sample available immediately. [1]

The release consists of two different collections. Its field portion includes 307 hours of real-world activity recorded with three-channel EMG on both wrists, head- and wrist-mounted video, depth and inertial measurements. A separate 10.4-hour laboratory set uses eight-channel EMG and optical motion capture to provide independently measured hand poses for evaluation. Those units matter: the 307 hours refer to field clip time, not a sum of each wristband’s individual recordings. [1]

## What the sensors add

EMG records electrical activity associated with muscle activation. Encord’s researchers argue that the signals can offer clues about finger movement and grip when fingers are hidden from a camera. The company also cautions in its technical account that EMG does not directly measure joint position, object contact or grip force. [1]

Encord reported that a combined EMG-and-camera model achieved 15.3 millimeters median fingertip error in its evaluation, about 25% lower than its camera/held-pose reference. It also reported improved estimates in intervals where the camera reference could not recover an acceptable pose. These are company-reported experimental results, not evidence that a robot has already learned or performed Jenga autonomously. [1]

## A task to illustrate the challenge

USA TODAY reported that Encord used a head-mounted camera and wrist sensors as a person handled Jenga blocks, while a robot appeared in a demonstration at the summit. Reuters likewise described the Oct. 20 unveiling as a program combining camera vision and muscle sensors for robot-training data. [2] [3] The task illustrates the potential value of synchronized signals, but the public materials frame broader use in robotics as a research direction—not a measured improvement in deployed robots.

### Sources

[1] [Introducing EMG-1: the largest open dataset of wrist EMG synchronized with egocentric video — Encord](https://encord.com/data-labs/introducing-emg-1/)
[2] [San Francisco startup uses Jenga sensors to train robots — USA TODAY](https://www.usatoday.com/story/news/state/california/2026/10/22/san-francisco-ai-company-turns-jenga-into-a-robot-training-tool/92387498007/)
[3] [AI company uses Jenga, cameras and muscle sensors to train robots — Reuters](https://www.reuters.com/video/watch/idRW263323102026RP1/)
