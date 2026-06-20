---
type: schemas/concept.md
title: Auditor
description: Reports Cairn compliance levels per concept using the published audit rubric.
status: active
tags: [tools, audit]
timestamp: 2026-06-20T00:00:00-05:00
relations:
  - type: references
    target: ../../schemas/audit-rubric.md
    confidence: declared
---

# Auditor

Run:

```sh
python tools/auditor/audit.py .
```

The methodology is published in `schemas/audit-rubric.md`. Reports are per concept only and never aggregate to a bundle-wide score.
