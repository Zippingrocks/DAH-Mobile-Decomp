#!/usr/bin/env python3
"""Compare a supplied rebuilt JAR with the pinned original; never execute either.

Outputs hashes, counts and status metadata only. A match is not source provenance,
behavioral coverage, native-port validation, or an unconditional accuracy claim.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.classfile import ClassFile, POLICY
from tools.dah1 import AuditError, audit_jar, check_baseline, verify_input, MAX_JAR_BYTES
from tools import source_map as sm

ROOT = Path(__file__).resolve().parents[1]
STATES = ("exact_byte_match", "normalized_match", "differences", "unverified")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_digest(value) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def context(root: Path, manifest: dict, target: dict) -> str:
    """Bind reports to progress/evidence and comparator code, not generated images."""
    paths = {"tools/byte_match.py", "tools/classfile.py", "tools/dah1.py"}
    for cls in manifest["classes"]:
        for stage in sm.STATES:
            paths.update(e["path"] for e in cls[stage]["evidence"])
    for p in paths:
        if not sm.safe_path(p) or not (root / p).resolve().is_relative_to(root.resolve()):
            raise AuditError("Unsafe comparison-context path")
    return json_digest({"target": target, "classes": manifest["classes"],
                        "files": {p: digest((root/p).read_bytes()) for p in sorted(paths)}})


def compare_class(original: bytes, rebuilt: bytes | None) -> dict:
    result = {"state": "unverified", "original_sha256": digest(original),
              "rebuilt_sha256": digest(rebuilt) if rebuilt is not None else None,
              "reason": "No rebuilt class", "methods": []}
    if rebuilt is None:
        return result
    # Byte equality has a deliberately strict scope: the ENTIRE class file.
    if original == rebuilt:
        result.update(state="exact_byte_match", reason="Entire class file is byte-for-byte identical")
        return result
    try:
        a, b = ClassFile(original), ClassFile(rebuilt)
        ca, cb = a.normalized(), b.normalized()
        result.update(state="normalized_match" if ca == cb else "differences",
                      reason="Declared normalized class representations match" if ca == cb
                      else "Declared normalized class representations differ; not necessarily a gameplay defect")
        bm = {m.key: m for m in b.methods}
        for method in a.methods:
            other = bm.get(method.key)
            state = "unverified" if other is None else "normalized_match" if a.normalized_member(method) == b.normalized_member(other) else "differences"
            result["methods"].append({"id": method.key, "state": state})
        result["added_methods"] = sorted(set(bm) - {m.key for m in a.methods})
    except (AuditError, ValueError, IndexError, RecursionError) as exc:
        result["reason"] = "Normalization unavailable: " + str(exc)
    return result


def compare_jars(original: bytes, rebuilt: bytes) -> dict:
    oa, ba = audit_jar(original), audit_jar(rebuilt)
    with zipfile.ZipFile(io.BytesIO(original)) as a, zipfile.ZipFile(io.BytesIO(rebuilt)) as b:
        bn = set(b.namelist())
        rows = []
        for cls in oa["classes"]:
            name = cls["class"] + ".class"
            row = compare_class(a.read(name), b.read(name) if name in bn else None)
            row.update(original=cls["class"], method_entries=cls["method_entries"])
            rows.append(row)
        original_names = {c["class"] for c in oa["classes"]}
        added = sorted(c["class"] for c in ba["classes"] if c["class"] not in original_names)
    return {"schema_version": 1, "policy": POLICY,
            "original_sha256": digest(original), "rebuilt_sha256": digest(rebuilt),
            "whole_jar_exact": original == rebuilt, "classes": rows,
            "class_counts": {s: sum(c["state"] == s for c in rows) for s in STATES},
            "added_classes": added,
            "scope": "Class-file bytes and conservative normalized structure; not execution or source provenance. Assets and phone APIs are outside the class comparison."}


def validate_report(report: dict, manifest: dict, target: dict) -> None:
    if report.get("schema_version") != 1 or report.get("policy") != POLICY:
        raise AuditError("Unsupported byte-match report")
    if report.get("original_sha256") != target["sha256"]:
        raise AuditError("Comparison uses a different original input")
    for key in ("rebuilt_sha256", "context_sha256"):
        value = report.get(key)
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise AuditError("Missing/invalid report hash: " + key)
    expected = {c["original"]: c["method_entries"] for c in manifest["classes"]}
    actual = {}
    for c in report["classes"]:
        name = c["original"]
        if name in actual or c["state"] not in STATES:
            raise AuditError("Duplicate class or invalid match state")
        if type(c["method_entries"]) is not int or c["method_entries"] <= 0:
            raise AuditError("Invalid comparison method count")
        for key in ("original_sha256", "rebuilt_sha256"):
            value = c.get(key)
            if key == "rebuilt_sha256" and value is None and c["state"] == "unverified":
                continue
            if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
                raise AuditError("Invalid class artifact hash")
        actual[name] = c["method_entries"]
        if c["state"] == "exact_byte_match" and c["original_sha256"] != c["rebuilt_sha256"]:
            raise AuditError("Exact-match claim contradicts hashes")
    if actual != expected:
        raise AuditError("Comparison class inventory differs from target")
    counts = {s: sum(c["state"] == s for c in report["classes"]) for s in STATES}
    if report.get("class_counts") != counts:
        raise AuditError("Inconsistent comparison totals")


def dashboard_states(root: Path, manifest: dict, target: dict):
    """Absent, stale, or source-unsubstantiated reports never paint green tiles."""
    config = sm.read_json(root / "config/byte_match.json")
    if config.get("schema_version") != 1:
        raise AuditError("Unsupported comparison configuration")
    states = {c["original"]: "unverified" for c in manifest["classes"]}
    path = config.get("report")
    if path is None:
        return states, "No rebuilt-game comparison report has been recorded."
    mapped = {f["path"] for f in manifest["files"]}
    if not sm.safe_path(path) or path not in mapped:
        raise AuditError("Comparison report must be an explicitly tracked, safe metadata path")
    report = sm.read_json(root/path)
    validate_report(report, manifest, target)
    if report["context_sha256"] != context(root, manifest, target):
        return states, "STALE report: comparison tools, progress records or evidence changed; rerun comparison."
    source_ready = {c["original"] for c in manifest["classes"]
                    if c["recovery"]["state"] == "repaired" and c["build"]["state"] == "passed"}
    blocked = 0
    for c in report["classes"]:
        state = c["state"]
        if state in ("exact_byte_match", "normalized_match") and c["original"] not in source_ready:
            blocked += 1
        else:
            states[c["original"]] = state
    return states, (f"Artifact snapshot {report['rebuilt_sha256'][:12]}; {blocked} match claims withheld without source-only build evidence. "
                    "Not a live build or behavior test; see the comparison report.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path)
    parser.add_argument("--rebuilt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="New metadata report; never overwrite")
    args = parser.parse_args(argv)
    try:
        target = sm.read_json(ROOT / "config/target.json")
        manifest = sm.read_json(ROOT / sm.MANIFEST)
        sm.validate(manifest, target, ROOT, sm.tracked_files(ROOT))
        original = verify_input(args.original or ROOT/"inputs/original"/target["filename"], target)
        check_baseline(audit_jar(original), target)
        if args.rebuilt.stat().st_size > MAX_JAR_BYTES:
            raise AuditError("Rebuilt archive is over the size limit")
        report = compare_jars(original, args.rebuilt.read_bytes())
        report["context_sha256"] = context(ROOT, manifest, target)
        validate_report(report, manifest, target)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8", newline="\n") as out:
            json.dump(report, out, indent=2, sort_keys=True); out.write("\n")
        print(f"Wrote {args.output}: {report['class_counts']}. Binary comparison only; no gameplay tested.")
        return 0
    except (AuditError, OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
