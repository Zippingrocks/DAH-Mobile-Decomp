import tempfile
import unittest
import zipfile
from pathlib import Path

from tools import full_validation as fv

ROOT = Path(__file__).resolve().parents[1]

class FullValidationTests(unittest.TestCase):
    def test_audio_inventory_requires_four_amr_and_wav_companions(self):
        with tempfile.TemporaryDirectory() as td:
            jar=Path(td)/"fixture.jar"
            with zipfile.ZipFile(jar,"w") as z:
                z.writestr("DesktopLauncher.class",b"x")
                for i in range(4):
                    z.writestr("Sound/%d.amr"%i,b"a")
                    z.writestr("META-INF/dah-audio/%064d.wav"%i,b"RIFF")
            inv=fv.audio_companions(jar)
            self.assertEqual(len(inv["amr"]),4)
            self.assertEqual(len(inv["wav"]),4)
            self.assertTrue(inv["direct_launcher"])

    def test_human_only_list_is_subjective_not_build_work(self):
        text=" ".join(fv.HUMAN_ONLY_REMAINING).lower()
        self.assertIn("playtest",text)
        self.assertIn("subjective",text)
        self.assertNotIn("compile recovered source",text)
        self.assertNotIn("convert amr",text)

    def test_windows_native_build_is_environment_not_human_judgment(self):
        self.assertEqual(len(fv.ENVIRONMENT_REMAINING),1)
        self.assertIn("windows",fv.ENVIRONMENT_REMAINING[0].lower())
        self.assertIn("graalvm",fv.ENVIRONMENT_REMAINING[0].lower())

    def test_gate_orchestrates_campaign_matrix_and_progression(self):
        src=(ROOT/"tools/full_validation.py").read_text()
        self.assertIn("campaign_validation.py",src)
        self.assertIn("campaign_progression.py",src)\n        self.assertIn("mission_stress.py",src)
        self.assertIn("native_build.py",src)
        self.assertIn("DesktopLauncher",src)
        self.assertIn("--native-smoke",src)

    def test_gate_cannot_report_gold(self):
        src=(ROOT/"tools/full_validation.py").read_text()
        self.assertIn('"gold": False',src)

    def test_candidate_mode_avoids_rebuilding_when_supplied(self):
        src=(ROOT/"tools/full_validation.py").read_text()
        self.assertIn("if args.candidate:",src)
        self.assertIn("return args.candidate.resolve(), None",src)

if __name__=="__main__":
    unittest.main()
