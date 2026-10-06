import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools import campaign_validation as cv

ROOT = Path(__file__).resolve().parents[1]

class CampaignValidationTests(unittest.TestCase):
    def test_matrix_has_all_13_missions_once(self):
        cfg = cv.load_config()
        missions = [row["mission"] for row in cfg["missions"]]
        self.assertEqual(missions, list(range(1, 14)))

    def test_dynamic_kill_totals_are_pinned(self):
        rows = {row["mission"]: row for row in cv.load_config()["missions"]}
        self.assertEqual(rows[7]["target"], 29)
        self.assertEqual(rows[7]["dynamic"], 29)
        self.assertEqual(rows[12]["target"], 30)
        self.assertEqual(rows[12]["dynamic"], 30)

    def test_blisk_regression_rows_are_pinned(self):
        rows = {row["mission"]: row for row in cv.load_config()["missions"]}
        self.assertEqual(rows[8]["kind"], 8)
        self.assertEqual(rows[9]["kind"], 8)
        self.assertEqual(rows[13]["kind"], 3)

    def test_mission_four_initial_gate_is_preserved(self):
        row = cv.load_config()["missions"][3]
        self.assertTrue(row["initial"])
        self.assertTrue(row["complete"])

    def test_probe_compiles_against_public_runtime_only(self):
        if not shutil.which("javac"):
            self.skipTest("javac unavailable")
        with tempfile.TemporaryDirectory() as td:
            cv.compile_probe(Path(td))

    def test_parse_state_checks_embedded_hash(self):
        state = "m=1,kind=4,authored=10,mode=0,map=4,target=10,dynamic=17,initial=false,complete=true,progress=10"
        output = state + "\nsha=" + cv.sha256_text(state) + "\n"
        parsed = cv.parse_state(output)
        self.assertEqual(parsed["m"], 1)
        self.assertTrue(parsed["complete"])

    def test_each_mission_runs_in_a_separate_java_process(self):
        src = (ROOT / "tools/campaign_validation.py").read_text()
        self.assertIn('for expected in cfg["missions"]', src)
        self.assertIn('"CampaignMatrixProbe", str(mission)', src)

    def test_candidate_can_be_built_or_supplied(self):
        src = (ROOT / "tools/campaign_validation.py").read_text()
        self.assertIn("--candidate", src)
        self.assertIn("desktop_build.py", src)

if __name__ == "__main__":
    unittest.main()
