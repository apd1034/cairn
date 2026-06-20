---
type: schemas/concept.md
title: Reference Parser
description: Proof artifacts showing Cairn core parsing in under 60 lines per language.
status: active
tags: [tools, parser, minimalism]
timestamp: 2026-06-20T00:00:00-05:00
relations:
  - type: references
    target: ../../SPECIFICATION.md
    confidence: declared
---

# Reference Parser

`parser.py` and `parser.ts` parse Cairn frontmatter, aliases, relations, and markdown body. Each file is under 60 lines and has no dependency beyond a YAML library.

Python:

```sh
python tools/reference-parser/parser.py SPECIFICATION.md
```

TypeScript:

```sh
npx tsx tools/reference-parser/parser.ts SPECIFICATION.md
```
