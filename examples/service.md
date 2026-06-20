---
type: schemas/concept.md
title: Payment Service
description: Example service concept showing a declared dependency relation.
status: active
tags: [example, service]
timestamp: 2026-06-20T00:00:00-05:00
aliases:
  - examples/billing-service.md
relations:
  - type: depends_on
    target: examples/database.md
    confidence: declared
    note: Maintainer-declared dependency for payment persistence.
---

# Payment Service

This is an example Cairn concept for a service. Its relation is declared because a human intentionally asserted it.
