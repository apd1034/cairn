#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.reference_parser.parser import parse  # noqa: E402


if __name__ == "__main__":
    import yaml

    for file in sys.argv[1:]:
        concept = parse(file)
        print(yaml.safe_dump(concept, sort_keys=False))
