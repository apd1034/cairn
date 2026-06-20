#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import sys
import unicodedata
import yaml


SCALAR_FIELDS = ("title", "description", "status", "timestamp", "type")


def split_doc_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return yaml.safe_load(text[4:end]) or {}, text[end + 5 :]
    return {}, text


def split_doc(path):
    return split_doc_text(Path(path).read_text(encoding="utf-8"))


def canonical_body(text):
    _, body = split_doc_text(text)
    return body.replace("\r\n", "\n").replace("\r", "\n")


def body_hash(body):
    return hashlib.sha256(body.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")).hexdigest()


def parse_timestamp(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    raw = str(value)
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def later_side(ours_meta, theirs_meta):
    ours_ts = parse_timestamp(ours_meta.get("timestamp"))
    theirs_ts = parse_timestamp(theirs_meta.get("timestamp"))
    if ours_ts and theirs_ts:
        if ours_ts > theirs_ts:
            return "ours"
        if theirs_ts > ours_ts:
            return "theirs"
    return None


def norm(value):
    return unicodedata.normalize("NFC", str(value))


def conflict_value(field, ours, theirs):
    return f"<<<<<<< ours {field}\n{ours}\n=======\n{theirs}\n>>>>>>> theirs {field}"


def merge_scalar(field, base, ours, theirs, side, conflicts):
    base_value = base.get(field)
    ours_value = ours.get(field, base_value)
    theirs_value = theirs.get(field, base_value)
    if ours_value == theirs_value:
        return ours_value
    if ours_value == base_value:
        return theirs_value
    if theirs_value == base_value:
        return ours_value
    if side == "ours":
        return ours_value
    if side == "theirs":
        return theirs_value
    conflicts.append(f"scalar conflict: {field}")
    return conflict_value(field, ours_value, theirs_value)


def merge_unique_list(*values):
    merged = set()
    for value in values:
        for item in value or []:
            merged.add(norm(item))
    return sorted(merged)


def relation_key(relation):
    return (norm(relation.get("type", "")), norm(relation.get("target", "")))


def merge_relation(base_rel, ours_rel, theirs_rel, side, conflicts):
    if ours_rel == theirs_rel:
        return ours_rel
    if ours_rel == base_rel:
        return theirs_rel
    if theirs_rel == base_rel:
        return ours_rel
    if side == "ours":
        return ours_rel
    if side == "theirs":
        return theirs_rel
    merged = dict(base_rel or {})
    for rel in (ours_rel or {}, theirs_rel or {}):
        for key, value in rel.items():
            if key not in merged:
                merged[key] = value
            elif merged[key] != value:
                conflicts.append(f"relation conflict: {relation_key(rel)}.{key}")
                merged[key] = conflict_value(f"relation.{key}", merged[key], value)
    return merged


def relation_map(relations):
    mapped = {}
    for rel in relations or []:
        key = relation_key(rel)
        if key != ("", ""):
            mapped[key] = rel
    return mapped


def merge_relations(base, ours, theirs, side, conflicts):
    base_map = relation_map(base.get("relations"))
    ours_map = relation_map(ours.get("relations"))
    theirs_map = relation_map(theirs.get("relations"))
    output = []
    for key in sorted(set(base_map) | set(ours_map) | set(theirs_map)):
        rel = merge_relation(base_map.get(key), ours_map.get(key), theirs_map.get(key), side, conflicts)
        if rel:
            output.append(rel)
    return output


def merge_body(base_body, ours_body, theirs_body, conflicts):
    if ours_body == theirs_body:
        return ours_body
    if ours_body == base_body:
        return theirs_body
    if theirs_body == base_body:
        return ours_body
    conflicts.append("body conflict")
    return f"<<<<<<< ours\n{ours_body}\n=======\n{theirs_body}\n>>>>>>> theirs\n"


def merge_docs(base_text, ours_text, theirs_text):
    base_meta, base_body = split_doc_text(base_text)
    ours_meta, ours_body = split_doc_text(ours_text)
    theirs_meta, theirs_body = split_doc_text(theirs_text)
    conflicts = []
    side = later_side(ours_meta, theirs_meta)
    merged = {}
    for field in SCALAR_FIELDS:
        value = merge_scalar(field, base_meta, ours_meta, theirs_meta, side, conflicts)
        if value is not None:
            merged[field] = value
    tags = merge_unique_list(base_meta.get("tags"), ours_meta.get("tags"), theirs_meta.get("tags"))
    if tags:
        merged["tags"] = tags
    aliases = merge_unique_list(base_meta.get("aliases"), ours_meta.get("aliases"), theirs_meta.get("aliases"))
    if aliases:
        merged["aliases"] = aliases
    relations = merge_relations(base_meta, ours_meta, theirs_meta, side, conflicts)
    if relations:
        merged["relations"] = relations
    body = merge_body(base_body, ours_body, theirs_body, conflicts)
    if not conflicts:
        merged["hash"] = body_hash(body)
    elif "hash" in merged:
        merged.pop("hash", None)
    return merged, body, conflicts


def dump_doc(meta, body):
    frontmatter = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{frontmatter}\n---\n{body}"


def merge_files(base, ours, theirs):
    base_text = Path(base).read_text(encoding="utf-8")
    ours_text = Path(ours).read_text(encoding="utf-8")
    theirs_text = Path(theirs).read_text(encoding="utf-8")
    return merge_docs(base_text, ours_text, theirs_text)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Deterministically merge three Cairn concept versions.")
    parser.add_argument("base")
    parser.add_argument("ours")
    parser.add_argument("theirs")
    parser.add_argument("--output", help="Write merged concept to this file instead of stdout")
    parser.add_argument("--conflicts-json", help="Write merge conflicts to this JSON file")
    args = parser.parse_args(argv)
    meta, body, conflicts = merge_files(args.base, args.ours, args.theirs)
    merged = dump_doc(meta, body)
    if args.output:
        Path(args.output).write_text(merged, encoding="utf-8")
    else:
        print(merged)
    if args.conflicts_json:
        import json

        Path(args.conflicts_json).write_text(json.dumps(conflicts, indent=2) + "\n", encoding="utf-8")
    return 1 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
