import json
import unittest
from pathlib import Path

from tools import mission_stress as ms

ROOT=Path(__file__).resolve().parents[1]

class MissionStressTests(unittest.TestCase):
    def test_config_has_13_unique_missions(self):
        cfg=ms.load_config()
        missions=[x["mission"] for x in cfg["missions"]]
        self.assertEqual(missions,list(range(1,14)))
        self.assertEqual(len(set(missions)),13)

    def test_config_pins_300_frames_per_mission(self):
        self.assertEqual(ms.load_config()["frames_per_mission"],300)

    def test_every_mission_hash_is_sha256_shape(self):
        for row in ms.load_config()["missions"]:
            self.assertEqual(len(row["sha256"]),64)

    def test_aggregate_hash_is_pinned(self):
        self.assertEqual(len(ms.load_config()["aggregate_stdout_sha256"]),64)

    def test_probe_uses_real_controller_world_transition(self):
        src=(ROOT/"tests/java/MissionStressProbe.java").read_text()
        self.assertIn('method(k,"g").invoke(null)',src)
        self.assertIn('Method tick=method(k,"j")',src)
        self.assertIn("StateProbe.state()",src)

    def test_probe_intentionally_excludes_forced_direct_render(self):
        src=(ROOT/"tests/java/MissionStressProbe.java").read_text()
        self.assertNotIn('method(k,"paint"',src)

    def test_runner_uses_fresh_java_process_per_mission(self):
        src=(ROOT/"tools/mission_stress.py").read_text()
        self.assertIn('for expected in cfg["missions"]',src)
        self.assertIn('"MissionStressProbe"',src)

if __name__=="__main__":
    unittest.main()
