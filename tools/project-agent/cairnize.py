#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.project_agent.cairnize import run  # noqa: E402


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stage a read-only Cairn migration for any project.")
    parser.add_argument("target", help="Project directory to scan")
    parser.add_argument("--output", help="Directory for staged concepts and reports")
    parser.add_argument("--write-into-target", action="store_true", help="Write cairn-proposed/ and reports/ inside the target project")
    run(parser.parse_args())
