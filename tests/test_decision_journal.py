import json
import tempfile
import unittest
from pathlib import Path

from scripts.decision_journal import append_record


class DecisionJournalTests(unittest.TestCase):
    def test_appends_structured_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "journal.jsonl"
            record = append_record(path, {
                "question": "Compare two contribution options",
                "decision": "Continue reviewing both scenarios",
                "rationale": "No target allocation has been approved.",
                "snapshot_ref": "snapshot-2026-11-27",
            })
            stored = json.loads(path.read_text(encoding="utf-8").strip())
            self.assertEqual(stored["record_id"], record["record_id"])
            self.assertEqual(stored["snapshot_ref"], "snapshot-2026-11-27")

    def test_requires_rationale(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                append_record(Path(temp_dir) / "journal.jsonl", {"question": "Q", "decision": "D"})


if __name__ == "__main__":
    unittest.main()
