---
type: schemas/concept.md
title: Cairn Threat Model
description: Security model for parsing, validating, migrating, and resolving Cairn concept bundles.
status: active
tags: [security, threat-model, cairn]
timestamp: 2026-06-20T16:43:00Z
relations:
  - type: implements
    target: ../../RFC/0005-uri-security-model.md
    confidence: declared
    note: Applies the URI resolution security RFC to implementation behavior.
---

# Cairn Threat Model

## Trust Boundaries

- A Cairn bundle may be untrusted input.
- YAML frontmatter is data only and must be parsed with safe loaders.
- Local path resolution must stay inside the bundle root unless a user explicitly configures another mount.
- `cairn://` references are external identifiers, not permission to fetch remote content.
- Migration reports may contain private project paths and should not be published without review.

## Required Controls

- Use safe YAML parsing. Python tooling uses `yaml.safe_load`.
- Do not execute frontmatter values, relation notes, schema content, or Markdown bodies.
- Treat unresolved local relations as validation errors rather than silently fetching remote content.
- Keep network resolution out of core tooling unless a resolver is explicitly enabled by the user.
- Keep source scanning read-only unless `--write-into-target` is explicitly provided.

## Future Remote Resolver Requirements

A future `cairn://` resolver must:

- separate local filesystem, configured mount, and network resolution modes
- reject path traversal and symlink escape from mounted bundles
- support pinned versions or signed bundle metadata before automation trusts remote concepts
- expose provenance for fetched data
- cache defensively and avoid executing package install scripts or repository hooks

## Current Non-Goals

Cairn core does not provide authentication, authorization, remote registry hosting, or signed bundle distribution. Those belong in companion specifications.
