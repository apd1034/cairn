from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from tools.index.index import main as write_index
from tools.validate.validate import validate


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


class CairnToolTests(unittest.TestCase):
    def test_valid_bundle_passes_validation(self):
        results = validate(FIXTURES / "valid-bundle")
        self.assertTrue(results)
        self.assertTrue(all(item["valid"] for item in results), results)

    def test_invalid_bundle_reports_expected_failures(self):
        results = {item["path"]: item for item in validate(FIXTURES / "invalid-bundle")}
        self.assertIn("missing-title.md", results)
        self.assertIn("missing title", results["missing-title.md"]["errors"])
        self.assertIn("broken relation target: missing.md", results["broken-relation.md"]["errors"])
        self.assertIn("relation missing valid confidence: schemas/concept.md", results["bad-confidence.md"]["errors"])
        self.assertIn("hash mismatch", results["hash-mismatch.md"]["errors"])
        self.assertIn("ambiguous alias: shared-old.md", results["alias-a.md"]["errors"])
        self.assertIn("ambiguous alias: shared-old.md", results["alias-b.md"]["errors"])

    def test_index_writes_concepts_and_backlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            subprocess.run(["cp", "-R", str(FIXTURES / "valid-bundle") + "/.", str(target)], check=True)
            index = write_index(target)
            self.assertIn("service.md", index["concepts"])
            self.assertIn("database.md", index["backlinks"])
            written = json.loads((target / "_index.json").read_text(encoding="utf-8"))
            self.assertEqual(written["concepts"]["service.md"]["title"], "Service")

    def test_cli_validate_and_audit_json_only(self):
        validate_cmd = [sys.executable, str(ROOT / "cairn_cli.py"), "validate", str(FIXTURES / "valid-bundle")]
        self.assertEqual(subprocess.run(validate_cmd, cwd=ROOT, capture_output=True).returncode, 0)

        audit_cmd = [sys.executable, str(ROOT / "cairn_cli.py"), "audit", str(FIXTURES / "valid-bundle"), "--json-only"]
        completed = subprocess.run(audit_cmd, cwd=ROOT, text=True, capture_output=True, check=True)
        payload = json.loads(completed.stdout)
        self.assertIsNone(payload["report"])
        self.assertGreaterEqual(len(payload["results"]), 1)

    def test_migration_scanner_stages_report_without_touching_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "run"
            cmd = [
                sys.executable,
                str(ROOT / "cairn_cli.py"),
                "migrate",
                str(FIXTURES / "sample-project"),
                "--output",
                str(output),
            ]
            completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
            summary = json.loads(completed.stdout)
            self.assertFalse(summary["source_modified"])
            self.assertTrue(Path(summary["report"]).exists())
            self.assertTrue((output / "cairn-proposed").exists())


if __name__ == "__main__":
    unittest.main()
