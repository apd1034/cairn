---
type: schemas/schema.md
title: Audit Rubric
description: The published methodology for assigning per-concept Cairn compliance levels.
status: active
tags: [schema, audit, rubric]
timestamp: 2026-06-20T00:00:00-05:00
relations:
  - type: references
    target: SPECIFICATION.md
    confidence: declared
    note: Compliance levels are defined by the core specification.
---

# Audit Rubric

This concept is the inspectable scoring methodology for Cairn audits. Tools must read or mirror this rubric rather than hide the methodology only in source code.

## Levels

| Level | Requirement |
|---|---|
| 1 | `type` and `title` are present. |
| 2 | Level 1 plus `description`, `status`, and `tags` are present. |
| 3 | Level 2 plus at least one typed `relations` entry where relevant. If no relation is relevant, the concept may remain at Level 2 until reviewed. |
| 4 | Level 3 plus `type` resolves to an existing schema concept. |
| 5 | Level 4 plus every relation carries `confidence`, all local relation targets resolve, and all aliases resolve uniquely. |
| 6 | Level 5 plus `hash` is present and verified against the current canonical body. |

## Reporting Rule

Compliance is reported per concept only. A Cairn tool must not compute or display a whole-bundle compliance score.
