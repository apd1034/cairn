---
type: schemas/concept.md
title: Validator
description: Per-concept validation for Cairn schemas, relation resolution, aliases, and optional hashes.
status: active
tags: [tools, validation]
timestamp: 2026-06-20T00:00:00-05:00
relations:
  - type: references
    target: ../../SPECIFICATION.md
    confidence: declared
---

# Validator

Run:

```sh
python tools/validate/validate.py .
```

The validator emits one result per concept. It does not produce a whole-bundle compliance score.
