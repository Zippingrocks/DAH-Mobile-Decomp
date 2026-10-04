"""Synthetic inputs test tooling, never game accuracy. No game files required."""
import hashlib
import io
from pathlib import Path
import struct
import tempfile
import unittest
import warnings
import zipfile
from tools.dah1 import AuditError, Reader, audit_jar, check_baseline, class_summary, verify_input


def u2(value):
    return struct.pack(">H", value)


def u4(value):
    return struct.pack(">I", value)


def utf8(text):
    data = text.encode("ascii")
    return b"\x01" + u2(len(data)) + data


def synthetic_class(native=False):
    # Independently authored structural fixture: Sample.ping() returns immediately.
    pool = [utf8("Sample"), b"\x07" + u2(1), utf8("java/lang/Object"),
            b"\x07" + u2(3), utf8("ping"), utf8("()V"), utf8("Code")]
    header = b"\xca\xfe\xba\xbe" + u2(0) + u2(49) + u2(len(pool) + 1) + b"".join(pool)
    body = u2(0x21) + u2(2) + u2(4) + u2(0) + u2(0) + u2(1)
    method = u2(0x109 if native else 0x9) + u2(5) + u2(6)
    if native:
        method += u2(0)
    else:
        code = u2(0) + u2(0) + u4(1) + b"\xb1" + u2(0) + u2(0)
        method += u2(1) + u2(7) + u4(len(code)) + code
    return header + body + method + u2(0)


def archive(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as jar:
        for name, content in entries:
            jar.writestr(name, content)
    return stream.getvalue()


class ToolingTests(unittest.TestCase):
    def test_class_counts(self):
        report = class_summary(synthetic_class())
        self.assertEqual(report["class"], "Sample")
        self.assertEqual(report["method_entries"], 1)
        self.assertEqual(report["methods_with_code"], 1)
        self.assertEqual(report["method_bytecode_bytes"], 1)
        self.assertEqual(report["native_methods"], 0)

    def test_native_count(self):
        report = class_summary(synthetic_class(native=True))
        self.assertEqual(report["native_methods"], 1)
        self.assertEqual(report["method_bytecode_bytes"], 0)

    def test_all_truncations_rejected(self):
        data = synthetic_class()
        for end in range(len(data)):
            with self.subTest(end=end), self.assertRaises(AuditError):
                class_summary(data[:end])

    def test_bad_magic_rejected(self):
        with self.assertRaises(AuditError):
            class_summary(b"NOPE" + synthetic_class()[4:])

    def test_unknown_pool_tag_rejected(self):
        data = bytearray(synthetic_class())
        data[10] = 255
        with self.assertRaises(AuditError):
            class_summary(bytes(data))

    def test_trailing_data_rejected(self):
        with self.assertRaises(AuditError):
            class_summary(synthetic_class() + b"x")

    def test_reader_negative_size(self):
        with self.assertRaises(AuditError):
            Reader(b"x").take(-1)

    def test_archive_counts_and_determinism(self):
        data = archive([("Sample.class", synthetic_class()), ("text.txt", b"fixture")])
        report = audit_jar(data)
        self.assertEqual(report["class_count"], 1)
        self.assertEqual(report["non_class_file_count"], 1)
        self.assertEqual(report["totals"]["method_entries"], 1)
        self.assertEqual(report, audit_jar(data))

    def test_duplicate_entries_rejected(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            data = archive([("x", b"a"), ("x", b"b")])
        with self.assertRaises(AuditError):
            audit_jar(data)

    def test_unsafe_paths_rejected(self):
        for name in ("../bad", "/bad", "a/../../bad", "a\\bad", "C:/bad"):
            with self.subTest(name=name), self.assertRaises(AuditError):
                audit_jar(archive([(name, b"fixture")]))

    def test_class_path_mismatch_rejected(self):
        with self.assertRaises(AuditError):
            audit_jar(archive([("Other.class", synthetic_class())]))

    def test_hash_and_size_checks(self):
        data = archive([("Sample.class", synthetic_class())])
        target = {"size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.jar"
            path.write_bytes(data)
            self.assertEqual(verify_input(path, target), data)
            path.write_bytes(b"!" + data[1:])
            with self.assertRaises(AuditError):
                verify_input(path, target)
            path.write_bytes(data[:-1])
            with self.assertRaises(AuditError):
                verify_input(path, target)

    def test_baseline(self):
        report = audit_jar(archive([("Sample.class", synthetic_class())]))
        check_baseline(report, {"expected_static_counts": {"class_count": 1}})
        with self.assertRaises(AuditError):
            check_baseline(report, {"expected_static_counts": {"method_entries": 2}})


if __name__ == "__main__":
    unittest.main()
