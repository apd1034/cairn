---
type: schemas/schema.md
title: Agent Skill
description: A schema for Cairn concepts that document Agent Skills-compatible skill packages.
status: active
tags: [schema, agent-skills, companion]
timestamp: 2026-06-20T10:00:00-05:00
relations:
  - type: references
    target: ../RFC/0002-agent-skills-companion.md
    confidence: declared
    note: Companion layer for agent instructions without adding agent runtime fields to Cairn core.
---

# Agent Skill Schema

## Required Fields

- `type`
- `title`

## Optional Fields

- `description`
- `status`
- `tags`
- `timestamp`
- `relations`

## Body Contract

The body documents the Agent Skills package path, trigger intent, bundled scripts, references, and validation notes.

The actual Agent Skills package uses `SKILL.md` frontmatter defined by the Agent Skills standard, not Cairn concept frontmatter.
