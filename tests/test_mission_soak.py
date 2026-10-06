import unittest
from tools import mission_soak as soak

class MissionSoakTests(unittest.TestCase):
    def test_config_has_13_missions(self):
        cfg=soak.load_config()
        self.assertEqual([x["mission"] for x in cfg["missions"]],list(range(1,14)))

    def test_soak_frame_count(self):
        cfg=soak.load_config()
        self.assertEqual(cfg["frames_per_mission"],5000)
        self.assertEqual(cfg["total_frames"],65000)

    def test_hashes_are_pinned(self):
        cfg=soak.load_config()
        self.assertEqual(len(cfg["aggregate_stdout_sha256"]),64)
        for row in cfg["missions"]:
            self.assertEqual(len(row["sha256"]),64)

if __name__=="__main__":
    unittest.main()
