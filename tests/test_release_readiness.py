import unittest
from tools import release_readiness as rr

class ReleaseReadinessTests(unittest.TestCase):
    def test_required_evidence_set_covers_current_machine_passes(self):
        keys=set(rr.REQUIRED_EVIDENCE)
        for key in [
            "source_recovery","whole_tree_build","desktop_runtime","desktop_build",
            "amr_audio","campaign_matrix","native_aot_prep","campaign_progression",
            "automated_gate","mission_stress","mission_fuzz","desktop_polish",
            "audio_sanity","mission_soak"
        ]:
            self.assertIn(key,keys)

    def test_inspect_never_calls_project_gold(self):
        result=rr.inspect()
        self.assertFalse(result["gold"])
        self.assertIn("Gold requires",result["gold_reason"])

    def test_machine_readiness_is_independent_of_human_judgment(self):
        result=rr.inspect()
        self.assertIn("human_only_remaining",result)
        self.assertGreaterEqual(len(result["human_only_remaining"]),3)

    def test_windows_exe_remains_environment_gate_until_evidence_changes(self):
        result=rr.inspect()
        self.assertFalse(result["native_windows_executable_built"])
        self.assertEqual(len(result["environment_only_remaining"]),1)

    def test_source_map_counts_are_exact(self):
        summary=rr.source_map_summary()
        self.assertEqual(summary["classes"],21)
        self.assertEqual(summary["method_entries"],313)
        self.assertEqual(summary["repaired"],21)

if __name__=="__main__":
    unittest.main()
