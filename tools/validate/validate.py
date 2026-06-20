#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib
import json
import sys
import yaml


FORBIDDEN = {"memory", "embeddings", "workflow", "permissions"}


def split_doc(path):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return yaml.safe_load(text[4:end]) or {}, text[end + 5 :], True
    return {}, text, False


def files(root):
    ignored = {"node_modules", ".git", "cairn-runs", "fixtures"}
    return [p for p in root.rglob("*.md") if not ignored & set(p.relative_to(root).parts)]


def rel(root, path):
    return path.resolve().relative_to(root.resolve()).as_posix()


def local_target(root, current, target, aliases):
    if not target or str(target).startswith("cairn://"):
        return True
    candidates = [(current.parent / target).resolve(), (root / target).resolve()]
    root_resolved = root.resolve()
    for candidate in candidates:
        if root_resolved in candidate.parents or candidate == root_resolved:
            try:
                key = rel(root, candidate)
                if candidate.exists() or key in aliases:
                    return True
            except ValueError:
                pass
    return str(target) in aliases


def validate(root):
    docs = {}
    aliases = {}
    for path in files(root):
        meta, body, is_concept = split_doc(path)
        if not is_concept or not (meta.get("type") or meta.get("title")):
            continue
        key = rel(root, path)
        docs[key] = (path, meta, body)
        for alias in meta.get("aliases", []) or []:
            aliases.setdefault(alias, []).append(key)
    results = []
    for key, (path, meta, body) in sorted(docs.items()):
        errors, warnings = [], []
        if not meta.get("type"):
            errors.append("missing type")
        if not meta.get("title"):
            errors.append("missing title")
        if FORBIDDEN & set(meta):
            errors.append("contains forbidden core fields")
        schema = meta.get("type")
        if schema and not str(schema).startswith("cairn://") and schema not in docs:
            errors.append(f"type does not resolve: {schema}")
        for alias, owners in aliases.items():
            if len(owners) > 1 and key in owners:
                errors.append(f"ambiguous alias: {alias}")
        for relation in meta.get("relations", []) or []:
            if not relation.get("type") or not relation.get("target"):
                errors.append("relation missing type or target")
            if relation.get("confidence") not in {"declared", "inferred"}:
                errors.append(f"relation missing valid confidence: {relation.get('target')}")
            if not local_target(root, path, relation.get("target"), aliases):
                errors.append(f"broken relation target: {relation.get('target')}")
        if meta.get("hash"):
            digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
            if digest != meta["hash"]:
                errors.append("hash mismatch")
        results.append({"path": key, "valid": not errors, "errors": errors, "warnings": warnings})
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    args = ap.parse_args()
    output = validate(Path(args.root))
    print(json.dumps(output, indent=2))
    sys.exit(1 if any(not item["valid"] for item in output) else 0)
