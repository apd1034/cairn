---
type: schemas/concept.md
title: Project Analysis Migration Guide
description: Describes the read-only workflow for bringing an existing project toward Cairn.
status: active
tags: [migration, analysis]
timestamp: 2026-06-20T00:00:00-05:00
relations:
  - type: references
    target: ../SPECIFICATION.md
    confidence: declared
---

# Project Analysis Migration Guide

## Operating Rule

Analyze source repositories read-only by default. Write generated concepts to `cairn-proposed/` and reports to `reports/`. Do not modify source files unless explicitly instructed.

## Scan

Detect candidate concepts from:

- services and modules: entrypoints, manifests, Dockerfiles, Kubernetes manifests
- APIs: OpenAPI, Swagger, routes, controllers
- data models: migrations, schema files, ORM models, warehouse table definitions
- workflows: CI/CD configs, DAGs, automation scripts
- ownership: CODEOWNERS, manifest maintainers, commit-frequency fallback
- documentation: README files, `docs/`, wikis

## Generate

Draft concept files into `cairn-proposed/`. Descriptions must come only from existing source text. Use `<needs author input>` when no source text supports a description.

Every inferred relation must include `confidence: inferred` and a `note` citing concrete evidence such as a file path, line number, import, foreign key, or config key.

## Score

Apply `schemas/audit-rubric.md` per concept. Never report a whole-project score.

## Report

Write `reports/CAIRN_MIGRATION_<timestamp>.md` as a Cairn concept with `type: schemas/migration-report.md`. Include:

- Current State
- Knowledge Inventory
- Relationship Inventory split by `confidence`
- Per-Concept Compliance Levels
- Gaps
- Migration Roadmap with rationale, benefit, risk, and rough implementation complexity

## Stop

Present the staged directory and report. A human decides what moves into the real project.
