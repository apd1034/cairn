---
type: schemas/rfc.md
title: URI Resolution Security Model
description: Defines trust boundaries for local paths, aliases, and future cairn:// remote resolution.
status: active
tags: [rfc, security, uri-resolution]
timestamp: 2026-06-20T16:42:00Z
relations:
  - type: references
    target: ../docs/security/THREAT_MODEL.md
    confidence: declared
    note: The threat model gives implementation guidance for this RFC.
---

# RFC 0005: URI Resolution Security Model

Cairn core validates local relative paths and accepts `cairn://` URIs as external references, but it does not fetch remote bundles.

Any future remote resolver must be opt-in, must separate local filesystem resolution from network resolution, must avoid executing content, and should verify signed or pinned bundle identities before using remote concept data in automation.

Implementations must use safe YAML parsing and treat untrusted concept bundles as data, not executable configuration.
