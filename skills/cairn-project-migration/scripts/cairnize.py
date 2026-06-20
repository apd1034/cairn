#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import shutil


IGNORE = {".git", "node_modules", ".venv", "venv", "dist", "build", "target", ".next"}
TEXT_EXT = {".md", ".txt", ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb", ".php", ".sql", ".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".xml"}
MANIFESTS = {"package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "Dockerfile", "docker-compose.yml", "docker-compose.yaml"}
WORKFLOWS = {".github/workflows", ".gitlab-ci.yml", "Jenkinsfile", "Makefile"}
API_HINTS = {"openapi.yaml", "openapi.yml", "swagger.yaml", "swagger.yml", "openapi.json", "swagger.json"}
DATA_DIRS = {"migrations", "schemas", "models", "db", "database", "warehouse"}


def slug(text):
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return text or "concept"


def yq(value):
    return json.dumps(str(value))


def parent_or_name(rel, name):
    parent = rel.parent.as_posix()
    return name if parent in {"", "."} else parent


def safe_read(path, limit=12000):
    try:
        if path.suffix and path.suffix not in TEXT_EXT and path.name not in MANIFESTS and path.name not in WORKFLOWS:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def walk(root):
    for path in root.rglob("*"):
        rel_parts = path.relative_to(root).parts
        if any(part in IGNORE for part in rel_parts):
            continue
        yield path


def line_of(path, pattern):
    for idx, line in enumerate(safe_read(path, 60000).splitlines(), 1):
        if pattern in line:
            return idx
    return 1


def first_doc_summary(path):
    text = safe_read(path)
    if not text:
        return None
    for block in re.split(r"\n\s*\n", text):
        cleaned = " ".join(line.strip("#- *` ") for line in block.splitlines()).strip()
        if 40 <= len(cleaned) <= 240 and not cleaned.lower().startswith(("install", "usage", "license")):
            return cleaned
    return None


def add_candidate(candidates, key, kind, source, title=None, description=None, evidence=None):
    if key not in candidates:
        candidates[key] = {
            "key": key,
            "kind": kind,
            "title": title or key.replace("-", " ").title(),
            "description": description or "<needs author input>",
            "sources": [],
            "relations": [],
        }
    candidates[key]["sources"].append({"path": source.as_posix(), "evidence": evidence or "detected file"})
    if description and candidates[key]["description"] == "<needs author input>":
        candidates[key]["description"] = description
    return candidates[key]


def detect(root):
    candidates = {}
    files = [p for p in walk(root) if p.is_file()]
    rels = {p: p.relative_to(root) for p in files}

    for path in files:
        rel = rels[path]
        rel_s = rel.as_posix()
        name = path.name
        parent_names = set(rel.parts[:-1])
        summary = first_doc_summary(path) if name.lower().startswith("readme") or path.suffix == ".md" else None

        if name in MANIFESTS or name in {"requirements.txt", "Gemfile"}:
            add_candidate(candidates, f"modules/{slug(parent_or_name(rel, name))}", "module", rel, rel.parent.name if rel.parent.as_posix() not in {"", "."} else name, summary, f"manifest {rel_s}")
        if name in API_HINTS or "routes" in parent_names or "controllers" in parent_names:
            add_candidate(candidates, f"apis/{slug(parent_or_name(rel, path.stem))}", "api", rel, rel.parent.name if rel.parent.as_posix() not in {"", "."} else path.stem, summary, f"API evidence {rel_s}")
        if DATA_DIRS & parent_names or path.suffix == ".sql":
            add_candidate(candidates, f"data/{slug(path.stem)}", "data", rel, path.stem.replace("_", " ").title(), summary, f"data evidence {rel_s}")
        if rel_s.startswith(".github/workflows/") or name in WORKFLOWS:
            add_candidate(candidates, f"workflows/{slug(path.stem)}", "workflow", rel, path.stem.replace("_", " ").title(), summary, f"workflow evidence {rel_s}")
        if name == "CODEOWNERS":
            add_candidate(candidates, "ownership/codeowners", "ownership", rel, "CODEOWNERS", summary, f"ownership evidence {rel_s}")
        if path.suffix == ".md" and ("docs" in parent_names or name.lower().startswith("readme")):
            add_candidate(candidates, f"docs/{slug(rel.with_suffix('').as_posix())}", "documentation", rel, path.stem.replace("_", " ").title(), summary, f"documentation evidence {rel_s}")

    by_source = {}
    for candidate in candidates.values():
        for source in candidate["sources"]:
            by_source.setdefault(source["path"], []).append(candidate)

    for path in files:
        rel = rels[path]
        text = safe_read(path, 60000)
        if not text:
            continue
        imports = re.findall(r"(?:from\s+([\w./-]+)\s+import|import\s+([\w./-]+)|require\(['\"]([^'\"]+)['\"]\))", text)
        fks = re.findall(r"foreign\s+key\s*\(([^)]+)\)\s+references\s+([a-zA-Z0-9_.-]+)", text, re.I)
        for owners in by_source.get(rel.as_posix(), []):
            for groups in imports[:20]:
                target_name = next((g for g in groups if g), "")
                if not target_name or target_name.startswith((".", "/", "@")):
                    continue
                owners["relations"].append({
                    "type": "references",
                    "target": "<needs author mapping>",
                    "confidence": "inferred",
                    "note": f"Inferred from import '{target_name}' in {rel.as_posix()}:{line_of(path, target_name)}.",
                })
            for column, table in fks[:20]:
                target_key = f"data/{slug(table)}"
                add_candidate(candidates, target_key, "data", rel, table.replace("_", " ").title(), None, f"referenced by foreign key in {rel.as_posix()}:{line_of(path, table)}")
                owners["relations"].append({
                    "type": "joins",
                    "target": f"{slug(table)}.md",
                    "confidence": "inferred",
                    "note": f"Inferred from foreign key {column.strip()} references {table} in {rel.as_posix()}:{line_of(path, table)}.",
                })
    return list(candidates.values())


def concept_path(candidate):
    return Path(candidate["key"] + ".md")


def concept_body(candidate, timestamp):
    tags = [candidate["kind"], "cairn-proposed"]
    sources = "\n".join(f"- `{s['path']}`: {s['evidence']}" for s in candidate["sources"])
    relations = candidate["relations"]
    rel_yaml = ""
    if relations:
        rel_yaml = "relations:\n" + "\n".join(
            f"  - type: {r['type']}\n    target: {yq(r['target'])}\n    confidence: {r['confidence']}\n    note: {yq(r['note'])}"
            for r in relations
        )
    frontmatter = [
        "---",
        "type: schemas/concept.md",
        f"title: {yq(candidate['title'])}",
        f"description: {yq(candidate['description'])}",
        "status: draft",
        f"tags: [{', '.join(tags)}]",
        f"timestamp: {timestamp}",
    ]
    if rel_yaml:
        frontmatter.append(rel_yaml)
    frontmatter.append("---")
    body = f"# {candidate['title']}\n\n## Source Evidence\n\n{sources or '- <needs author input>'}\n\n## Author Review Needed\n\nConfirm title, description, ownership, and any `<needs author mapping>` relation targets before merging this staged concept.\n"
    return "\n".join(frontmatter) + "\n\n" + body


def score(candidate):
    level = 1
    notes = []
    if candidate["description"] != "<needs author input>":
        level = 2
    else:
        notes.append("Description needs author input.")
    if candidate["relations"]:
        level = max(level, 3)
    else:
        notes.append("No relations inferred; review whether relations are relevant.")
    notes.append("Type resolves after proposed concepts are merged into a Cairn bundle with schemas/concept.md.")
    notes.append("Hash is not added during staging; verify after author review.")
    return level, notes


def write_report(root, out_root, candidates, timestamp, stamp):
    report_dir = out_root / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = report_dir / f"CAIRN_MIGRATION_{stamp}.md"
    inventory = "\n".join(f"- `{concept_path(c)}`: {c['title']} ({c['kind']})" for c in candidates) or "- No candidates detected."
    declared = "- None. This agent only stages inferred relations."
    inferred_items = []
    for c in candidates:
        for r in c["relations"]:
            inferred_items.append(f"- `{concept_path(c)}` {r['type']} `{r['target']}`: {r['note']}")
    inferred = "\n".join(inferred_items) or "- No inferred relations detected."
    scores = "\n".join(f"- `{concept_path(c)}`: Level {score(c)[0]} - {'; '.join(score(c)[1])}" for c in candidates)
    body = f"""---
type: schemas/migration-report.md
title: Cairn Migration Report for {root.name}
description: Read-only Cairn migration analysis for {root}.
status: active
tags: [migration, report, cairn-proposed]
timestamp: {timestamp}
---

# Cairn Migration Report for {root.name}

## Current State

Scanned `{root}` read-only. Generated staged Cairn concepts in `{out_root / 'cairn-proposed'}`.

## Knowledge Inventory

{inventory}

## Relationship Inventory

### Declared

{declared}

### Inferred

{inferred}

## Per-Concept Compliance Levels

{scores or "- No concepts scored."}

## Gaps

- Descriptions marked `<needs author input>` require source-backed author review.
- Relation targets marked `<needs author mapping>` require mapping to concrete Cairn concept paths.
- Ownership needs confirmation unless a CODEOWNERS concept was detected.
- Hashes should be added after staged concepts are reviewed and stable.

## Migration Roadmap

- Review staged concept titles and descriptions. Rationale: prevent fabricated knowledge. Benefit: trustworthy concepts. Risk: low. Complexity: low.
- Resolve inferred relation targets. Rationale: relation evidence exists but Cairn targets need stable paths. Benefit: queryable graph. Risk: medium. Complexity: medium.
- Add missing schema-specific contracts if the project needs specialized concept types. Rationale: keep core minimal while making validation sharper. Benefit: better per-concept checks. Risk: low. Complexity: medium.
- Run `tools/validate/validate.py` and `tools/auditor/audit.py` after merging approved concepts. Rationale: verify conformance per concept. Benefit: measurable Cairn maturity. Risk: low. Complexity: low.
"""
    report.write_text(body, encoding="utf-8")
    return report


def schema_dir():
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "schemas"
        if (candidate / "concept.md").exists() and (candidate / "schema.md").exists():
            return candidate
        bundled = parent / "assets" / "schemas"
        if (bundled / "concept.md").exists() and (bundled / "schema.md").exists():
            return bundled
    raise SystemExit("could not locate Cairn schema files")


def run(args):
    target = Path(args.target).resolve()
    if not target.exists():
        raise SystemExit(f"target does not exist: {target}")
    timestamp = datetime.now(timezone.utc).isoformat()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_root = target if args.write_into_target else Path(args.output or f"cairn-runs/{target.name}-{stamp}").resolve()
    proposed = out_root / "cairn-proposed"
    proposed.mkdir(parents=True, exist_ok=True)
    candidates = detect(target)
    for candidate in candidates:
        path = proposed / concept_path(candidate)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(concept_body(candidate, timestamp), encoding="utf-8")
    source_schema_dir = schema_dir()
    for schema_root in (proposed / "schemas", out_root / "schemas"):
        schema_root.mkdir(exist_ok=True)
        for schema_name in ("schema.md", "concept.md", "migration-report.md"):
            destination = schema_root / schema_name
            if not destination.exists():
                shutil.copyfile(source_schema_dir / schema_name, destination)
    report = write_report(target, out_root, candidates, timestamp, stamp)
    summary = {
        "target": str(target),
        "output": str(out_root),
        "proposed": str(proposed),
        "report": str(report),
        "concepts": len(candidates),
        "relations": sum(len(c["relations"]) for c in candidates),
        "source_modified": bool(args.write_into_target),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage a read-only Cairn migration for any project.")
    parser.add_argument("target", help="Project directory to scan")
    parser.add_argument("--output", help="Directory for staged concepts and reports")
    parser.add_argument("--write-into-target", action="store_true", help="Write cairn-proposed/ and reports/ inside the target project")
    run(parser.parse_args())
