"""Tooling tests use authored fixtures; they do not require or verify game code."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

from tools.component_recovery import (
    ROOT, SUPPORT, RecoveryError, compare_traces, method_inventory,
    pinned_input, sha, source_files, traces, write_jar,
)


class ComponentRecoveryToolTests(unittest.TestCase):
    def test_parse_trace(self):
        value = traces("group-name\t12\t" + "ab" * 32 + "\n")
        self.assertEqual(value["group-name"]["calls_per_side"], 12)

    def test_bad_traces_fail(self):
        for text in ("", "nonsense", "a\t0\t" + "0" * 64, "a\t-1\t" + "0" * 64,
                     "a\t1\tnope", "BAD\t1\t" + "0" * 64):
            with self.subTest(text=text), self.assertRaises(RecoveryError):
                traces(text)

    def test_duplicate_trace_group_fails(self):
        row = "alpha\t1\t" + "0" * 64 + "\n"
        with self.assertRaises(RecoveryError): traces(row + row)

    def test_equal_traces(self):
        row = "alpha\t1\t" + "0" * 64 + "\n"
        self.assertEqual(compare_traces(row, row), traces(row))

    def test_changed_digest_detected(self):
        with self.assertRaises(RecoveryError):
            compare_traces("alpha\t1\t" + "0" * 64, "alpha\t1\t" + "1" * 64)

    def test_changed_call_count_detected(self):
        with self.assertRaises(RecoveryError):
            compare_traces("alpha\t1\t" + "0" * 64, "alpha\t2\t" + "0" * 64)

    def test_jar_deterministic_and_allowlisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / "a.jar", Path(tmp) / "b.jar"
            write_jar(first, {"Z.class": b"fixture-z", "A.class": b"fixture-a"})
            write_jar(second, {"A.class": b"fixture-a", "Z.class": b"fixture-z"})
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as z:
                self.assertEqual(z.namelist(), ["A.class", "Z.class"])
                self.assertEqual(z.read("A.class"), b"fixture-a")

    def test_jar_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.jar"
            write_jar(path, {"A.class": b"fixture"})
            original = path.read_bytes()
            with self.assertRaises(RecoveryError): write_jar(path, {"A.class": b"changed"})
            self.assertEqual(path.read_bytes(), original)

    def test_unsafe_jar_entry_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            for index, name in enumerate(("../A.class", "a/b.class", "assets.png", "A.java")):
                with self.subTest(name=name), self.assertRaises(RecoveryError):
                    write_jar(Path(tmp) / (str(index) + ".jar"), {name: b"fixture"})

    def test_input_hash_and_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.jar"
            path.write_bytes(b"authored fixture")
            target = {"size_bytes": path.stat().st_size, "sha256": sha(path.read_bytes())}
            self.assertEqual(pinned_input(path, target), b"authored fixture")
            path.write_bytes(b"Authored fixture")
            with self.assertRaises(RecoveryError): pinned_input(path, target)
            path.write_bytes(b"short")
            with self.assertRaises(RecoveryError): pinned_input(path, target)

    def test_source_hash_and_presence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src/game").mkdir(parents=True)
            path = root / "src/game/Sample.java"
            data = b"final class Sample {}\n"
            config = {"components": [{"original": "Sample", "source_sha256": sha(data)}]}
            with self.assertRaises(RecoveryError): source_files(root, config)
            path.write_bytes(data)
            self.assertEqual(source_files(root, config), [path])
            path.write_bytes(data + b"// change\n")
            with self.assertRaises(RecoveryError): source_files(root, config)

    def test_unsafe_or_empty_source_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            for names in ([], [{"original": "../Sample"}], [{"original": ""}]):
                with self.subTest(names=names), self.assertRaises(RecoveryError):
                    source_files(Path(tmp), {"components": names})

    def test_member_inventory_object_returns_regression(self):
        # Descriptor lines contain parentheses and can end in ';'. They are not declarations.
        text = """final class Sample {
  public java.lang.String field;
    descriptor: Ljava/lang/String;
  public Sample();
    descriptor: ()V
  public static final java.lang.Object read(java.lang.String);
    descriptor: (Ljava/lang/String;)Ljava/lang/Object;
  public static final int count();
    descriptor: ()I
  static {};
    descriptor: ()V
}
"""
        self.assertEqual(method_inventory(text), [
            ("Sample", "()V"), ("read", "(Ljava/lang/String;)Ljava/lang/Object;"),
            ("count", "()I"), ("<clinit>", "()V"),
        ])

    def test_empty_or_duplicate_inventory_fails(self):
        for data in ("", "public void a();\n descriptor: ()V\n" * 2):
            with self.subTest(data=data), self.assertRaises(RecoveryError): method_inventory(data)

    @unittest.skipUnless(shutil.which("javac"), "JDK not installed")
    def test_probe_compiles_without_game_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["javac", "--release", "8", "-g:none", "-d", tmp,
                 *[str(ROOT / path) for path in SUPPORT]],
                capture_output=True, text=True, timeout=40,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(tmp) / "ComponentProbe.class").is_file())
            for name in ("e", "s", "t"):
                self.assertFalse((Path(tmp) / (name + ".class")).exists())


if __name__ == "__main__":
    unittest.main()
