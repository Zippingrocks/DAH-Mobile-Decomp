import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools import desktop_build
from tools import native_build

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "desktop"

class NativeBuildTests(unittest.TestCase):
    def test_generated_launcher_uses_direct_game_entry(self):
        src = desktop_build.desktop_launcher_source()
        self.assertIn("GameMidlet midlet = new GameMidlet()", src)
        self.assertIn("midlet.startApp()", src)
        self.assertNotIn('Class.forName("GameMidlet")', src)

    def test_generated_launcher_has_native_smoke_mode(self):
        src = desktop_build.desktop_launcher_source()
        self.assertIn('"--native-smoke"', src)
        self.assertIn('method(type, "i")', src)
        self.assertIn('method(type, "j")', src)
        self.assertIn('method(type, "paint"', src)

    def test_generated_launcher_compiles_with_public_runtime_and_stub_game(self):
        if not shutil.which("javac"):
            self.skipTest("javac unavailable")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            classes = root / "classes"
            classes.mkdir()
            stub = root / "GameMidlet.java"
            stub.write_text(
                "public class GameMidlet {"
                " public GameMidlet(){}"
                " public void startApp(){}"
                " public void destroyApp(boolean value){}"
                "}"
            )
            launcher = root / "DesktopLauncher.java"
            launcher.write_text(desktop_build.desktop_launcher_source())
            sources = [str(path) for path in sorted(RUNTIME.rglob("*.java"))]
            subprocess.run(
                ["javac", "--release", "8", "-g:none", "-d", str(classes), *sources, str(stub), str(launcher)],
                cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )

    def test_native_preflight_recognizes_direct_launcher(self):
        with tempfile.TemporaryDirectory() as td:
            jar = Path(td) / "desktop.jar"
            with zipfile.ZipFile(jar, "w") as out:
                out.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\nMain-Class: DesktopLauncher\n\n")
                out.writestr("DesktopLauncher.class", b"fixture")
            info = native_build.inspect_desktop_jar(jar)
            self.assertTrue(info["direct_launcher"])
            self.assertEqual(info["main_class"], "DesktopLauncher")

    def test_native_build_automates_agent_and_native_image(self):
        src = (ROOT / "tools/native_build.py").read_text()
        self.assertIn("native-image-agent=config-output-dir=", src)
        self.assertIn("--no-fallback", src)
        self.assertIn("-H:IncludeResources=.*", src)
        self.assertIn("DesktopLauncher", src)

    def test_native_image_explicit_path_wins(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "native-image"
            self.assertEqual(native_build.find_native_image(str(path)), str(path.resolve()))

if __name__ == "__main__":
    unittest.main()
