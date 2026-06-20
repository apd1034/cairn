---
type: schemas/rfc.md
title: Agent Skills Companion Layer
description: Defines how Cairn repositories may package Agent Skills-compatible instructions without expanding Cairn core.
status: active
tags: [rfc, agent-skills, companion]
timestamp: 2026-06-20T10:00:00-05:00
relations:
  - type: references
    target: SPECIFICATION.md
    confidence: declared
    note: Keeps agent workflows outside Cairn core as a companion layer.
---

# RFC 0002: Agent Skills Companion Layer

Cairn repositories may include Agent Skills-compatible packages under `skills/`. These packages help agents perform Cairn-related work consistently while preserving Cairn core's rule that workflows and agent behavior stay out of the required format.

An Agent Skills package must follow the external Agent Skills directory convention: a directory with a required `SKILL.md`, plus optional `scripts/`, `references/`, and `assets/`.

Cairn concept files may document the skill package, but `SKILL.md` itself is not a Cairn concept.
