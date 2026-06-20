#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import yaml


def split_doc(path):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return yaml.safe_load(text[4:end]) or {}, True
    return {}, False


def md_files(root):
    ignored = {"node_modules", ".git", "cairn-runs"}
    return [p for p in root.rglob("*.md") if not ignored & set(p.parts)]


def main(root):
    concepts = {}
    backlinks = {}
    for path in md_files(root):
        key = path.relative_to(root).as_posix()
        meta, is_concept = split_doc(path)
        if not is_concept or not (meta.get("type") and meta.get("title")):
            continue
        concepts[key] = meta
        for relation in meta.get("relations", []) or []:
            target = relation.get("target")
            if target:
                backlinks.setdefault(target, []).append({
                    "source": key,
                    "type": relation.get("type"),
                    "confidence": relation.get("confidence"),
                })
    index = {"concepts": concepts, "backlinks": backlinks}
    (root / "_index.json").write_text(json.dumps(index, indent=2, sort_keys=True, default=str) + "\n")
    return index


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    main(Path(ap.parse_args().root))
