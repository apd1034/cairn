---
type: schemas/schema.md
title: Audit Report
description: A schema for timestamped per-concept Cairn audit findings.
status: active
tags: [schema, audit, report]
timestamp: 2026-06-20T00:00:00-05:00
relations:
  - type: references
    target: schemas/audit-rubric.md
    confidence: declared
---

# Audit Report Schema

## Required Fields

- `type`
- `title`

## Optional Fields

- `description`
- `status`
- `tags`
- `timestamp`
- `relations`

## Required Sections

- Per-concept compliance levels
- Notes for missing requirements

Audit reports must not include a whole-bundle compliance score.
