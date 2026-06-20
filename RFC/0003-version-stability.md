---
type: schemas/rfc.md
title: Version Stability Policy
description: Aligns Cairn format and tooling versions and defines pre-1.0 compatibility guarantees.
status: active
tags: [rfc, versioning, governance]
timestamp: 2026-06-20T16:40:00Z
relations:
  - type: references
    target: ../SPECIFICATION.md
    confidence: declared
    note: Establishes the versioning policy for the published specification.
---

# RFC 0003: Version Stability Policy

Cairn uses one semantic version for the published format specification and reference tooling. The visible specification title, Python package version, npm package version, release tag, and changelog entry should match.

Before `1.0.0`, Cairn releases are standard-candidate releases. Markdown bodies remain ordinary Markdown, but frontmatter fields, compliance scoring, merge behavior, and URI resolution rules may change through accepted RFCs. Breaking format changes require a minor version bump before `1.0.0`.

After `1.0.0`, breaking format changes require a major version bump and a documented migration path. Deprecated frontmatter fields should remain readable for at least one major release unless they create a security issue.
