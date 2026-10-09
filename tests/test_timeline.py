import json
import unittest
from pathlib import Path

from hearing_timeline.engine import cluster_entities, parse_turns, render_timeline

TEXT = Path("samples/hearing.txt").read_text()

class TimelineTests(unittest.TestCase):
    def test_forty_lines(self):
        self.assertEqual(len([line for line in TEXT.splitlines() if line.strip()]), 40)

    def test_motion_vote_objection_date(self):
        turns = parse_turns(TEXT)
        labels = {label for turn in turns for label in turn.labels}
        self.assertTrue({"motion", "objection", "vote", "date"} <= labels)
        self.assertIn("4 to 0", " ".join(turn.text for turn in turns if "vote" in turn.labels))

    def test_entities_cluster(self):
        clusters = cluster_entities(TEXT)
        self.assertIn("Northline Data Limited", clusters["applicant"])
        self.assertIn("Planning Committee", clusters["committee"])
        self.assertIn("Elena Voss", clusters["officer"])

    def test_committed_outputs(self):
        turns = parse_turns(TEXT)
        self.assertEqual(render_timeline(turns), Path("samples/timeline.md").read_text())
        self.assertEqual(cluster_entities(TEXT), json.loads(Path("samples/entities.json").read_text()))

if __name__ == "__main__":
    unittest.main()
