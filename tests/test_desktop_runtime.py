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
        self.assertIn('Boolean.getBoolean("dah.audio.strict")', src)
        self.assertIn("catch (Throwable failure)", src)

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

    def test_canvas_has_configurable_integer_scale(self):
        src = (RUNTIME / "javax/microedition/lcdui/Canvas.java").read_text()
        self.assertIn('System.getProperty("dah.scale", "3")', src)
        self.assertIn("Math.max(1, Math.min(8, value))", src)
        self.assertIn("VALUE_INTERPOLATION_NEAREST_NEIGHBOR", src)

    def test_canvas_maps_desktop_controls(self):
        src = (RUNTIME / "javax/microedition/lcdui/Canvas.java").read_text()
        self.assertIn("KeyEvent.VK_A", src)
        self.assertIn("KeyEvent.VK_D", src)
        self.assertIn("KeyEvent.VK_W", src)
        self.assertIn("KeyEvent.VK_S", src)
        self.assertIn("KeyEvent.VK_SPACE", src)
        self.assertIn("KeyEvent.VK_Z", src)
        self.assertIn("KeyEvent.VK_X", src)
        self.assertIn("return -6", src)
        self.assertIn("return -7", src)
        self.assertIn("desktopKeyPressed", src)
        self.assertIn("desktopKeyReleased", src)

    def test_canvas_control_mapping_executes(self):
        if not shutil.which("javac") or not shutil.which("java"):
            self.skipTest("Java toolchain unavailable")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            probe = root / "CanvasControlProbe.java"
            probe.write_text(
                "package javax.microedition.lcdui;"
                "import java.awt.event.KeyEvent;"
                "public final class CanvasControlProbe {"
                " public static void main(String[] args) {"
                "  System.out.println(Canvas.mapDesktopKey(KeyEvent.VK_ENTER, '\\n'));"
                "  System.out.println(Canvas.mapDesktopKey(KeyEvent.VK_SPACE, ' '));"
                "  System.out.println(Canvas.mapDesktopClick(100, 100, 528, 624));"
                "  System.out.println(Canvas.mapDesktopClick(100, 600, 528, 624));"
                "  System.out.println(Canvas.mapDesktopClick(500, 600, 528, 624));"
                " }"
                "}"
            )
            classes = root / "classes"
            sources = [str(path) for path in sorted(RUNTIME.rglob("*.java"))]
            subprocess.run(
                ["javac", "--release", "8", "-g:none", "-d", str(classes), *sources, str(probe)],
                cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            result = subprocess.run(
                ["java", "-cp", str(classes), "javax.microedition.lcdui.CanvasControlProbe"],
                cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            self.assertEqual(result.stdout.splitlines(), ["-6", "53", "53", "-6", "-7"])

    def test_canvas_ignores_unmapped_zero_key(self):
        src = (RUNTIME / "javax/microedition/lcdui/Canvas.java").read_text()
        self.assertIn("if (key != 0) Canvas.this.keyPressed(key)", src)
        self.assertIn("if (key != 0) Canvas.this.keyReleased(key)", src)


if __name__ == "__main__":
    unittest.main()
