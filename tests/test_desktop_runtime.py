import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "desktop"

class DesktopRuntimeTests(unittest.TestCase):
    def test_runtime_source_roster(self):
        sources = sorted(RUNTIME.rglob("*.java"))
        self.assertEqual(len(sources), 18)

    def test_runtime_compiles_without_game_source(self):
        if not shutil.which("javac"):
            self.skipTest("javac unavailable")
        with tempfile.TemporaryDirectory() as td:
            sources = [str(path) for path in sorted(RUNTIME.rglob("*.java"))]
            subprocess.run(
                ["javac", "--release", "8", "-g:none", "-d", td, *sources],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

    def test_runtime_contains_no_recovered_game_classes(self):
        stems = {path.stem for path in RUNTIME.rglob("*.java")}
        self.assertFalse(stems.intersection({"GameMidlet", *list("abcdefghijklmnopqrst")}))

    def test_rms_is_file_backed(self):
        src = (RUNTIME / "javax/microedition/rms/RecordStore.java").read_text()
        self.assertIn('System.getProperty("dah.rms.dir"', src)
        self.assertIn("Files.newOutputStream", src)

    def test_graphics_uses_real_buffered_image(self):
        src = (RUNTIME / "javax/microedition/lcdui/Graphics.java").read_text()
        self.assertIn("BufferedImage", src)
        self.assertIn("pixelSha256", src)

    def test_launcher_uses_reflection_not_game_compile_dependency(self):
        src = (RUNTIME / "dah/desktop/Launcher.java").read_text()
        self.assertIn('Class.forName("GameMidlet")', src)

    def test_media_has_midi_backend(self):
        src = (RUNTIME / "javax/microedition/media/Manager.java").read_text()
        self.assertIn("MidiSystem", src)
        self.assertIn("Sequencer", src)

    def test_media_has_hash_addressed_amr_wav_backend(self):
        src = (RUNTIME / "javax/microedition/media/Manager.java").read_text()
        self.assertIn("META-INF/dah-audio/", src)
        self.assertIn('MessageDigest.getInstance("SHA-256")', src)
        self.assertIn("AudioSystem.getAudioInputStream", src)
        self.assertIn("AudioSystem.getClip", src)

    def test_desktop_builder_refuses_original_class_fallback(self):
        src = (ROOT / "tools/desktop_build.py").read_text()
        self.assertIn('info.filename.endswith(".class")', src)
        self.assertIn('"original_class_fallback": False', src)

    def test_desktop_builder_transcodes_amr_automatically(self):
        src = (ROOT / "tools/desktop_build.py").read_text()
        self.assertIn("def transcode_amr(", src)
        self.assertIn('shutil.which("ffmpeg")', src)
        self.assertIn('"META-INF/dah-audio/" + digest + ".wav"', src)
        self.assertIn('"amr_converted": len(converted_audio)', src)

if __name__ == "__main__":
    unittest.main()
