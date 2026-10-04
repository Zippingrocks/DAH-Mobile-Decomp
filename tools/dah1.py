#!/usr/bin/env python3
"""Verify and structurally audit the single supported DAH1 JAR; never execute it."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TARGET_PATH = ROOT / "config" / "target.json"
MAX_JAR_BYTES = 8 * 1024 * 1024
MAX_ENTRIES = 2000
MAX_UNPACKED_BYTES = 64 * 1024 * 1024


class AuditError(ValueError):
    """An input was unsupported, malformed, or not the pinned game."""


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def take(self, size: int) -> bytes:
        if size < 0 or self.pos + size > len(self.data):
            raise AuditError("Truncated class-file structure")
        value = self.data[self.pos:self.pos + size]
        self.pos += size
        return value

    def u1(self) -> int:
        return self.take(1)[0]

    def u2(self) -> int:
        return struct.unpack(">H", self.take(2))[0]

    def u4(self) -> int:
        return struct.unpack(">I", self.take(4))[0]

    def finish(self) -> None:
        if self.pos != len(self.data):
            raise AuditError("Unexpected trailing bytes in class-file structure")


def class_summary(data: bytes) -> dict:
    """Read structural counts, not instructions; this is not a JVM verifier."""
    r = Reader(data)
    if r.take(4) != b"\xca\xfe\xba\xbe":
        raise AuditError("Not a Java class file")
    minor, major = r.u2(), r.u2()
    pool: list = [None] * r.u2()
    if not pool:
        raise AuditError("Empty constant pool")
    index = 1
    while index < len(pool):
        tag = r.u1()
        if tag == 1:
            # Preserve raw modified-UTF-8 bytes. Only structural ASCII names are decoded.
            pool[index] = (tag, r.take(r.u2()))
        elif tag in (7, 8, 16, 19, 20):
            pool[index] = (tag, r.u2())
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            pool[index] = (tag, r.take(4))
        elif tag in (5, 6):
            if index + 1 >= len(pool):
                raise AuditError("Wide constant lacks its reserved pool slot")
            pool[index] = (tag, r.take(8))
            index += 1
        elif tag == 15:
            pool[index] = (tag, r.take(3))
        else:
            raise AuditError(f"Unsupported constant-pool tag: {tag}")
        index += 1

    def item(i: int, tag: int):
        if not 0 < i < len(pool) or pool[i] is None or pool[i][0] != tag:
            raise AuditError(f"Invalid constant-pool reference: {i}")
        return pool[i][1]

    def text(i: int) -> bytes:
        return item(i, 1)

    def class_name(i: int) -> str:
        try:
            return text(item(i, 7)).decode("ascii")
        except UnicodeDecodeError as exc:
            raise AuditError("Non-ASCII class names are outside this audit's scope") from exc

    def attrs(reader: Reader) -> list[tuple[bytes, bytes]]:
        result = []
        for _ in range(reader.u2()):
            name = text(reader.u2())
            result.append((name, reader.take(reader.u4())))
        return result

    r.u2()  # Access flags.
    name = class_name(r.u2())
    parent = r.u2()
    superclass = class_name(parent) if parent else None
    for _ in range(r.u2()):
        class_name(r.u2())
    field_count = r.u2()
    for _ in range(field_count):
        r.u2()
        text(r.u2())
        text(r.u2())
        attrs(r)
    methods = r.u2()
    native = constructors = initializers = code_bytes = with_code = 0
    for _ in range(methods):
        flags = r.u2()
        method_name = text(r.u2())
        text(r.u2())  # Descriptor exists and is a UTF-8 pool entry.
        native += bool(flags & 0x0100)
        constructors += method_name == b"<init>"
        initializers += method_name == b"<clinit>"
        code_attributes = 0
        for attribute, payload in attrs(r):
            if attribute != b"Code":
                continue
            code_attributes += 1
            c = Reader(payload)
            c.u2()  # max_stack
            c.u2()  # max_locals
            size = c.u4()
            if not 0 < size < 65536:
                raise AuditError("Invalid method Code length")
            c.take(size)
            c.take(8 * c.u2())  # Exception table.
            attrs(c)
            c.finish()
            code_bytes += size
        if code_attributes > 1:
            raise AuditError("Duplicate Code attributes on one method")
        if bool(code_attributes) == bool(flags & (0x0100 | 0x0400)):
            raise AuditError("Code presence disagrees with native/abstract flags")
        with_code += code_attributes
    attrs(r)
    r.finish()
    return {
        "class": name, "superclass": superclass,
        "classfile_version": f"{major}.{minor}", "class_bytes": len(data),
        "fields": field_count, "method_entries": methods,
        "constructors": constructors, "class_initializers": initializers,
        "native_methods": native, "methods_with_code": with_code,
        "method_bytecode_bytes": code_bytes,
    }


def load_target(path: Path = TARGET_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_input(path: Path, target: dict) -> bytes:
    size = path.stat().st_size
    if size > MAX_JAR_BYTES or size != target["size_bytes"]:
        raise AuditError(f"Input size mismatch: expected {target['size_bytes']}, got {size}")
    data = path.read_bytes()
    if len(data) != size or hashlib.sha256(data).hexdigest() != target["sha256"]:
        raise AuditError("SHA-256 mismatch; refusing a different or changed game build")
    return data


def audit_jar(data: bytes) -> dict:
    if len(data) > MAX_JAR_BYTES:
        raise AuditError("Archive exceeds audit size limit")
    classes = []
    non_class = directories = 0
    with zipfile.ZipFile(io.BytesIO(data)) as jar:
        entries = jar.infolist()
        if len(entries) > MAX_ENTRIES or sum(e.file_size for e in entries) > MAX_UNPACKED_BYTES:
            raise AuditError("Archive exceeds entry or unpacked-size limit")
        seen = set()
        for entry in entries:
            name = entry.filename
            parts = PurePosixPath(name).parts
            if (name in seen or not parts or name.startswith("/") or ".." in parts
                    or "\\" in name or ":" in name or "\x00" in name):
                raise AuditError(f"Duplicate or unsafe archive path: {name!r}")
            seen.add(name)
            if entry.flag_bits & 1:
                raise AuditError("Encrypted ZIP entries are unsupported")
            content = jar.read(entry)  # Also checks CRCs; nothing is extracted or executed.
            if entry.is_dir():
                directories += 1
            elif name.endswith(".class"):
                summary = class_summary(content)
                if name != summary["class"] + ".class":
                    raise AuditError("Class name does not match its archive path")
                classes.append(summary)
            else:
                non_class += 1
    keys = ("class_bytes", "method_entries", "constructors", "class_initializers",
            "native_methods", "methods_with_code", "method_bytecode_bytes")
    return {
        "schema_version": 1,
        "scope": "static structure only; no decompilation, execution, or fidelity proof",
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "input_size_bytes": len(data), "class_count": len(classes),
        "non_class_file_count": non_class, "directory_entries": directories,
        "totals": {key: sum(c[key] for c in classes) for key in keys},
        "classes": sorted(classes, key=lambda c: c["class"]),
    }


def check_baseline(report: dict, target: dict) -> None:
    actual = {"class_count": report["class_count"], **report["totals"]}
    for key, expected in target["expected_static_counts"].items():
        if actual.get(key) != expected:
            raise AuditError(f"Audit baseline mismatch for {key}: {actual.get(key)} != {expected}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "audit"))
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path, help="Write audit JSON to a new file; never overwrite")
    args = parser.parse_args(argv)
    try:
        if args.output and args.command != "audit":
            raise AuditError("--output requires the audit command")
        target = load_target()
        path = args.input or ROOT / "inputs" / "original" / target["filename"]
        data = verify_input(path, target)
        if args.command == "verify":
            print(f"Verified exact input: {target['id']} ({len(data)} bytes)")
        else:
            report = audit_jar(data)
            check_baseline(report, target)
            rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                    stream.write(rendered)
                print(f"Static audit written to {args.output}; game behavior was NOT tested")
            else:
                print(rendered, end="")
        return 0
    except (AuditError, OSError, zipfile.BadZipFile, RuntimeError, KeyError,
            UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
