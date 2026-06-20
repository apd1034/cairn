---
name: cairn-project-migration
description: Use this skill when a user asks to scan, migrate, convert, cairnize, document, audit, or bring any software project up to the Cairn knowledge format. Stages Cairn concepts and migration reports without modifying source files by default.
license: MIT
compatibility: Requires Python 3.10+ and filesystem access to the target project. No network access required.
metadata:
  version: "1.0"
  standard: "Agent Skills"
---

# Cairn Project Migration

## When To Use

Use this skill when the user wants an agent to:

- scan an existing project for Cairn concepts
- bring a project up to Cairn standard
- generate `cairn-proposed/`
- write a Cairn migration report
- infer project knowledge relationships with evidence
- audit per-concept Cairn readiness

Do not use this skill for general README editing, unrelated documentation cleanup, or adding memory, embeddings, workflows, or permissions to Cairn core.

## Core Rule

Operate read-only against the source project by default. Stage all generated artifacts outside the source project unless the user explicitly asks to write into the target.

## Procedure

1. Identify the target project directory from the user's request.
2. Run the bundled scanner:

   ```sh
   python3 scripts/cairnize.py /path/to/project
   ```

3. If the user explicitly wants staging files inside the target project, run:

   ```sh
   python3 scripts/cairnize.py /path/to/project --write-into-target
   ```

4. Review the JSON summary printed by the script. It includes:

   - `proposed`: staged concept directory
   - `report`: timestamped migration report
   - `concepts`: number of concepts staged
   - `relations`: number of inferred relations
   - `source_modified`: whether output was written inside the source project

5. Present the staged directory and report path to the user. Stop there unless the user explicitly asks you to merge or edit the source project.

## Evidence Rules

- Descriptions must come from existing source text.
- Use `<needs author input>` when no source text supports a description.
- Mark generated relations as `confidence: inferred`.
- Every inferred relation must cite concrete evidence in `note`: file, line, import, foreign key, or config key.
- Never report a whole-bundle compliance score. Report per concept only.

## Reference

Read `references/CAIRN_MIGRATION_CONTRACT.md` when changing the scanner, reviewing staged output, or resolving edge cases.
