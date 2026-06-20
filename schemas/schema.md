---
type: schemas/concept.md
title: Schema
description: A Cairn concept that documents field contracts for another concept type.
status: active
tags: [schema, core]
timestamp: 2026-06-20T00:00:00-05:00
relations:
  - type: implements
    target: schemas/concept.md
    confidence: declared
---

# Schema Schema

## Required Fields

- `type`
- `title`

## Optional Fields

- `description`
- `status`
- `tags`
- `timestamp`
- `aliases`
- `relations`

## Contract Body

A schema body documents required, optional, and forbidden fields in markdown. Tooling may parse these sections, but the contract remains human-readable without a runtime.
