#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import argparse
import contextlib
import io
import json

from tools.project_agent.cairnize import run as run_project_migration


def run_migration(target, output):
    args = argparse.Namespace(target=str(target), output=str(output), write_into_target=False)
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        run_project_migration(args)
    return json.loads(stdout.getvalue())


def summarize_run(summary):
    report = Path(summary["report"])
    text = report.read_text(encoding="utf-8") if report.exists() else ""
    return {
        "target": summary["target"],
        "concepts": summary["concepts"],
        "relations": summary["relations"],
        "source_modified": summary["source_modified"],
        "needs_author_mapping": text.count("<needs author mapping>"),
        "needs_author_input": text.count("<needs author input>"),
        "report": summary["report"],
    }


def evaluate(config_path, output_root):
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    results = []
    for item in config.get("projects", []):
        target = Path(item["path"]).resolve()
        run_output = output_root / target.name
        summary = run_migration(target, run_output)
        result = summarize_run(summary)
        result["label"] = item.get("label", target.name)
        result["ground_truth"] = item.get("ground_truth")
        results.append(result)
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "projects": results,
        "notes": [
            "Precision and recall require human-labeled ground truth.",
            "Unlabeled runs report scanner volume and unresolved-review counts only.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run Cairn migration scanner over a corpus config.")
    parser.add_argument("config", help="JSON config with projects[].path")
    parser.add_argument("--output", default="corpus-runs", help="Output directory for staged runs")
    parser.add_argument("--report", help="Write JSON summary to this path")
    args = parser.parse_args(argv)
    result = evaluate(args.config, args.output)
    payload = json.dumps(result, indent=2)
    if args.report:
        Path(args.report).write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
