#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib
import json
from datetime import datetime, timezone
import yaml


def split_doc(path):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return yaml.safe_load(text[4:end]) or {}, text[end + 5 :], True
    return {}, text, False


def md_files(root):
    ignored = {"node_modules", ".git", "cairn-runs", "fixtures"}
    return [p for p in root.rglob("*.md") if not ignored & set(p.relative_to(root).parts)]


def resolves(root, current, target, docs, aliases):
    if not target or str(target).startswith("cairn://"):
        return True
    for candidate in ((current.parent / target).resolve(), (root / target).resolve()):
        try:
            key = candidate.relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
        if key in docs or key in aliases:
            return True
    return target in docs or target in aliases


def has_relations(meta):
    return any(r.get("type") and r.get("target") for r in meta.get("relations", []) or [])


def score(root, key, docs, aliases):
    path, meta, body = docs[key]
    level = 0
    notes = []
    if meta.get("type") and meta.get("title"):
        level = 1
    else:
        return level, ["missing type or title"]
    if all(meta.get(k) for k in ("description", "status", "tags")):
        level = 2
    else:
        notes.append("Level 2 requires description, status, and tags")
    if level == 2 and has_relations(meta):
        level = 3
    elif level >= 2:
        notes.append("Level 3 requires typed relations where relevant")
    if level == 3 and meta.get("type") in docs:
        level = 4
    elif level >= 3:
        notes.append("Level 4 requires type to resolve to a schema concept")
    relation_errors = []
    for rel in meta.get("relations", []) or []:
        target = rel.get("target")
        if rel.get("confidence") not in {"declared", "inferred"}:
            relation_errors.append(f"missing confidence: {target}")
        if target and not resolves(root, path, target, docs, aliases):
            relation_errors.append(f"broken relation: {target}")
    alias_errors = [a for a, owners in aliases.items() if key in owners and len(owners) > 1]
    if level == 4 and not relation_errors and not alias_errors:
        level = 5
    elif level >= 4:
        notes.extend(relation_errors + [f"ambiguous alias: {a}" for a in alias_errors])
    if level == 5 and meta.get("hash"):
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        if digest == meta["hash"]:
            level = 6
        else:
            notes.append("hash mismatch")
    elif level >= 5:
        notes.append("Level 6 requires verified hash")
    return level, notes


def audit(root):
    rubric = root / "schemas" / "audit-rubric.md"
    if not rubric.exists():
        raise SystemExit("missing published rubric: schemas/audit-rubric.md")
    docs, aliases = {}, {}
    for path in md_files(root):
        key = path.relative_to(root).as_posix()
        meta, body, is_concept = split_doc(path)
        if not is_concept or not (meta.get("type") and meta.get("title")):
            continue
        docs[key] = (path, meta, body)
        for alias in meta.get("aliases", []) or []:
            aliases.setdefault(alias, []).append(key)
    return [{"path": key, "level": score(root, key, docs, aliases)[0],
             "notes": score(root, key, docs, aliases)[1]} for key in sorted(docs)]


def write_report(root, results):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    reports = root / "reports"
    reports.mkdir(exist_ok=True)
    path = reports / f"CAIRN_AUDIT_{stamp}.md"
    rows = "\n".join(
        f"| {item['path']} | {item['level']} | {'; '.join(item['notes']) or 'No notes'} |"
        for item in results
    )
    body = f"""---
type: schemas/audit-report.md
title: Cairn Audit {stamp}
description: Timestamped per-concept Cairn compliance audit.
status: active
tags: [audit, report]
timestamp: {datetime.now(timezone.utc).isoformat()}
relations:
  - type: references
    target: schemas/audit-rubric.md
    confidence: declared
---

# Cairn Audit {stamp}

| Concept | Level | Notes |
|---|---:|---|
{rows}

Compliance is reported per concept only. No bundle-wide score is computed.
"""
    path.write_text(body, encoding="utf-8")
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()
    root = Path(args.root)
    results = audit(root)
    report = None if args.json_only else write_report(root, results)
    print(json.dumps({"report": str(report) if report else None, "results": results}, indent=2))
