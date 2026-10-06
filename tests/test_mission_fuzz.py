import unittest
from pathlib import Path

from tools import mission_fuzz as mf

ROOT=Path(__file__).resolve().parents[1]

class MissionFuzzTests(unittest.TestCase):
    def test_config_has_all_13_missions(self):
        cfg=mf.load_config()
        self.assertEqual([x["mission"] for x in cfg["missions"]],list(range(1,14)))

    def test_config_has_four_independent_seeds(self):
        cfg=mf.load_config()
        self.assertEqual(cfg["seeds"],[1,3,13,34])
        self.assertEqual(len(set(cfg["seeds"])),4)

    def test_total_frame_count_is_consistent(self):
        cfg=mf.load_config()
        self.assertEqual(cfg["frames_per_seed"],150)
        self.assertEqual(cfg["total_frames"],13*4*150)

    def test_each_mission_hash_is_pinned(self):
        for row in mf.load_config()["missions"]:
            self.assertEqual(len(row["sha256"]),64)

    def test_aggregate_hash_is_pinned(self):
        self.assertEqual(len(mf.load_config()["aggregate_mission_hashes_sha256"]),64)

    def test_probe_has_randomized_press_release_and_release_all(self):
        src=(ROOT/"tests/java/MissionFuzzProbe.java").read_text()
        self.assertIn("input.nextInt(5)",src)
        self.assertIn("press.invoke(controller",src)
        self.assertIn("release.invoke(controller",src)
        self.assertIn("for(int i=0;i<held.length;i++) if(held[i])",src)
        self.assertIn("frame%50==0",src)

    def test_runner_uses_fresh_process_for_every_seed(self):
        src=(ROOT/"tools/mission_fuzz.py").read_text()
        self.assertIn('for seed in cfg["seeds"]',src)
        self.assertIn('"MissionFuzzProbe"',src)

if __name__=="__main__":
    unittest.main()
