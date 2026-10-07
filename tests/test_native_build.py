import shutil
import json
import subprocess
import tempfile
import unittest
import zipfile
from unittest.mock import patch
from pathlib import Path

from tools import desktop_build
from tools import native_build

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "desktop"

class NativeBuildTests(unittest.TestCase):
    def test_reused_metadata_rejects_changed_jar_and_configuration(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            jar = root / "desktop.jar"
            jar.write_bytes(b"first candidate")
            metadata = root / "metadata"
            metadata.mkdir()
            config = metadata / "reflect-config.json"
            config.write_text("[]")
            (metadata / "dah-provenance.json").write_text(json.dumps({
                "desktop_jar_sha256": native_build.sha(jar),
                "configuration_sha256": {config.name: native_build.sha(config)},
            }))
            native_build.verify_metadata(jar, metadata)
            jar.write_bytes(b"second candidate")
            with self.assertRaisesRegex(RuntimeError, "does not match"):
                native_build.verify_metadata(jar, metadata)
            jar.write_bytes(b"first candidate")
            config.write_text('[{"name":"Changed"}]')
            with self.assertRaisesRegex(RuntimeError, "does not match"):
                native_build.verify_metadata(jar, metadata)

    def test_dependency_inventory_records_imports_and_adjacent_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "awt.dll").write_bytes(b"fixture")
            with patch.object(native_build.shutil, "which", return_value="dumpbin"), patch.object(native_build, "run", return_value="Dependencies:\n    awt.dll\n    KERNEL32.dll\n    awt.dll\n"):
                result = native_build.dependency_inventory(root / "game.exe")
            self.assertEqual(result["direct_imports"], ["KERNEL32.dll", "awt.dll"])
            self.assertEqual(result["adjacent_dlls"][0]["sha256"], native_build.sha(root / "awt.dll"))
            self.assertFalse(result["clean_machine_tested"])

    def test_missing_dumpbin_does_not_claim_packaging_validation(self):
        with patch.object(native_build.shutil, "which", return_value=None):
            result = native_build.dependency_inventory(Path("game.exe"))
            self.assertFalse(result["recorded"])
            self.assertFalse(result["clean_machine_tested"])

    def test_linux_cannot_produce_windows_named_output(self):
        with tempfile.TemporaryDirectory() as td, patch.object(native_build.os, "name", "posix"), patch.object(native_build, "run") as run:
            with self.assertRaisesRegex(RuntimeError, "Windows host"):
                native_build.native_compile("native-image", Path("game.jar"), Path("metadata"), Path(td) / "game.exe")
            run.assert_not_called()

    def test_windows_format_rejects_elf_truncation_and_dll(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "game.exe"
            pe = bytearray(90)
            pe[:2] = b"MZ"
            pe[60:64] = (64).to_bytes(4, "little")
            pe[64:68] = b"PE\0\0"
            pe[68:70] = (0x8664).to_bytes(2, "little")
            pe[88:90] = (0x20b).to_bytes(2, "little")
            output.write_bytes(pe)
            self.assertEqual(native_build.inspect_windows_executable(output)["machine"], "x64")
            for bad in (b"\x7fELF" + bytes(100), b"MZ", pe[:70]):
                output.write_bytes(bad)
                with self.assertRaises(RuntimeError):
                    native_build.inspect_windows_executable(output)
            pe[86:88] = (0x2000).to_bytes(2, "little")
            output.write_bytes(pe)
            with self.assertRaisesRegex(RuntimeError, "DLL"):
                native_build.inspect_windows_executable(output)

    def test_native_smoke_failure_is_not_success(self):
        with patch.object(native_build.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "missing dependency")):
            with self.assertRaisesRegex(RuntimeError, "missing dependency"):
                native_build.native_smoke(Path("game.exe"))

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
