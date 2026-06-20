---
type: schemas/concept.md
title: Indexer
description: Generates _index.json from Cairn frontmatter and computed backlinks.
status: active
tags: [tools, index]
timestamp: 2026-06-20T00:00:00-05:00
relations:
  - type: references
    target: ../../SPECIFICATION.md
    confidence: declared
---

# Indexer

Run:

```sh
python tools/index/index.py .
```

`_index.json` is generated from concept frontmatter and computed backlinks. Regenerate it; do not hand-edit it.
