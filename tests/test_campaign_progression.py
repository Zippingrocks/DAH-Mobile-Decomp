import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path

from tools import campaign_progression as cp

ROOT = Path(__file__).resolve().parents[1]

class CampaignProgressionTests(unittest.TestCase):
    def test_config_has_exact_13_step_chain(self):
        cfg = cp.load_config()
        self.assertEqual([x["mission"] for x in cfg["steps"]], list(range(1,14)))
        self.assertEqual([x["after"] for x in cfg["steps"][:-1]], list(range(2,14)))
        self.assertEqual(cfg["steps"][-1]["after"], 13)

    def test_dynamic_runtime_targets_are_preserved(self):
        rows = {x["mission"]: x for x in cp.load_config()["steps"]}
        self.assertEqual(rows[7]["target"], 29)
        self.assertEqual(rows[12]["target"], 30)

    def test_final_step_enters_ending_without_mission_14(self):
        row = cp.load_config()["steps"][-1]
        self.assertEqual(row["mission"], 13)
        self.assertEqual(row["after"], 13)
        self.assertEqual(row["save"], cp.load_config()["steps"][-2]["save"])

    def test_final_file_contract_is_pinned(self):
        cfg = cp.load_config()
        self.assertEqual(cfg["final_rms_file_bytes"], 90)
        self.assertEqual(len(cfg["final_rms_file_sha256"]), 64)

    def test_aggregate_stdout_hash_is_pinned(self):
        cfg = cp.load_config()
        self.assertEqual(len(cfg["aggregate_stdout_sha256"]), 64)

    def test_probe_compiles_against_public_runtime_only(self):
        if not shutil.which("javac"):
            self.skipTest("javac unavailable")
        with tempfile.TemporaryDirectory() as td:
            cp.compile_probe(Path(td))

    def test_runner_uses_fresh_processes_and_shared_rms(self):
        src=(ROOT/"tools/campaign_progression.py").read_text()
        self.assertIn('"CampaignProgressionStepProbe"', src)
        self.assertIn('"-Ddah.rms.dir="+str(rms)', src)
        self.assertIn('for expected in cfg["steps"]', src)

    def test_runner_compares_actual_rms_files_each_step(self):
        src=(ROOT/"tools/campaign_progression.py").read_text()
        self.assertIn('rfile.read_bytes()!=cfile.read_bytes()', src)
        self.assertIn('final_rms_file_sha256', src)

if __name__=="__main__":
    unittest.main()
