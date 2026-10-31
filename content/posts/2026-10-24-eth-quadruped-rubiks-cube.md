---
title: "ETH Zurich Quadruped Solves Giant Rubik’s Cube With Its Feet"
date: 2026-10-24
draft: false
description: "ETH Zurich researchers report three autonomous cube solves by a quadruped, combining RGB-D perception, planning and learned foot-manipulation skills."
image: "/images/2026-10-24-eth-quadruped-rubiks-cube.jpg"
tags: [ETH Zurich, quadruped robots, robot manipulation, reinforcement learning, Rubik’s Cube]
categories: [Robotics, Research]
author: "TechPulse"
---
An ETH Zurich quadruped has autonomously solved a giant Rubik’s Cube by manipulating it with its feet. The robot scanned the cube, inferred its color state, planned a solution and executed the sequence using locomotion and foot-based skills. The research team reports three successful hardware solves, each involving about 30 steps and taking eight to nine minutes. [1] [2]

## Perception, planning and coordinated feet

The researchers describe the task as “pedipulation”: using a legged robot’s feet to interact with and control an object. An onboard RGB-D perception system estimates the cube’s position and orientation and reconstructs its full color state from partial views. A planner then converts a cube-solver sequence into actions the robot can execute. [1] [2]

For a layer turn, the quadruped pins the cube with one foot while pushing a layer with the other. Learned whole-body skills also let the robot tip and reorient the cube. The authors note that an unintended layer movement can invalidate subsequent turns, so the system must track both its own pose and the cube’s changing state. [1]

The team trained policies with reinforcement learning, first using privileged observations and then distilling behavior into policies driven by depth images and the robot’s motion sensing. The researchers say the deployed skills tolerate changes in robot-to-cube placement and can recover from external disturbances. [1] [2]

## A controlled research demonstration

The result tests whether a legged robot can chain perception, planning and contact-rich movement over a longer task. The authors argue that coordinated foot manipulation could help quadrupeds perform physical tasks involving objects whose internal configuration matters, rather than only pushing or carrying them. [1]

It remains a controlled research demonstration, not evidence that quadrupeds are ready for general household manipulation. Still, the cube forces the robot to make repeated precise contacts while tracking the object’s state. IEEE Spectrum highlighted the autonomous feet-only solve and linked to ETH’s project materials. [1] [3]

## Why It Matters

The demonstration matters less as a cube-solving stunt than as evidence that a legged robot can chain perception, planning and repeated precise foot contacts over a task lasting several minutes. Because the system must track both its own pose and the cube’s changing state, it tests capabilities that pushing or carrying objects does not. The researchers still describe a controlled setting, so the result sets a research benchmark rather than a near-term household application.

### Sources
[1] [ETH Zurich Robotics Systems Lab: Solving a giant Rubik’s Cube with a quadruped](https://leggedrobotics.github.io/rubik-skills/)
[2] [arXiv: Solving a Giant Rubik’s Cube with a Quadruped Robot](https://arxiv.org/abs/2610.24610)
[3] [IEEE Spectrum: Quadruped robot solves giant Rubik’s Cube by itself](https://spectrum.ieee.org/video-friday-rubiks-cube-robot)
