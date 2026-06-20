---
type: schemas/concept.md
title: Inferred Relation Example
description: Demonstrates how a tool-generated relation records its evidence.
status: draft
tags: [example, inferred]
timestamp: 2026-06-20T00:00:00-05:00
relations:
  - type: references
    target: examples/service.md
    confidence: inferred
    note: Inferred from import PaymentService in src/example.ts:12.
---

# Inferred Relation Example

An inferred relation must cite concrete evidence in `note` and must not be marked as declared.
