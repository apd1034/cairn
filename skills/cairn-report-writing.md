---
type: schemas/agent-skill.md
title: Cairn Report Writing Skill
description: Agent Skills-compatible package for writing Cairn migration and audit reports.
status: active
tags: [agent-skills, reports, cairn]
timestamp: 2026-06-20T10:40:00-05:00
relations:
  - type: implements
    target: ../RFC/0002-agent-skills-companion.md
    confidence: declared
    note: Packages Cairn report writing behavior as an Agent Skill companion.
  - type: references
    target: ../tools/report-agent/AGENT.md
    confidence: declared
    note: Mirrors the Cairn report-writing agent operating contract.
---

# Cairn Report Writing Skill

Package path: `skills/cairn-report-writing/`

Primary file: `skills/cairn-report-writing/SKILL.md`

Bundled script: `skills/cairn-report-writing/scripts/write_cairn_report.py`

This skill standardizes migration and audit reports so future agents produce the same report shape as the Apify migration report.
