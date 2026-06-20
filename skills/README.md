---
type: schemas/concept.md
title: Agent Skills Directory
description: Contains Agent Skills-compatible packages for agents that work with Cairn.
status: active
tags: [agent-skills, skills, agents]
timestamp: 2026-06-20T10:00:00-05:00
relations:
  - type: references
    target: ../schemas/agent-skill.md
    confidence: declared
    note: Documents how Agent Skills packages are represented alongside Cairn concepts.
---

# Agent Skills Directory

This directory contains Agent Skills-compatible packages. Each skill lives in its own directory with a required `SKILL.md` file.

Agent Skills are not Cairn core concepts. They are companion agent instructions that can reference Cairn concepts and tooling.
