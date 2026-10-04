#!/usr/bin/env python3
"""Build and compare the first locally recovered components; NOT a game build.

The public repository contains the probe and test doubles, not recovered game
source. Required local source snapshots are hash-pinned in component_recovery.json.
Original classes appear ONLY in the reference probe's isolated classpath.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CONFIG = "config/component_recovery.json"
SUPPORT = (
    "tests/java/component_support/o.java",
    "tests/java/component_support/javax/microedition/lcdui/Image.java",
    "tests/java/ComponentProbe.java",
)
TABLE_LENGTHS = (-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 31, 128, 1015, 1016)


class RecoveryError(ValueError):
    """A precondition, build or scoped comparison failed."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RecoveryError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_text(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def pinned_input(path: Path, target: dict) -> bytes:
    require(path.stat().st_size == target["size_bytes"], "Original input size mismatch")
    data = path.read_bytes()
    require(sha(data) == target["sha256"], "Original input SHA-256 mismatch")
    return data


def source_files(root: Path, config: dict) -> list[Path]:
    result, names = [], set()
    for item in config["components"]:
        name = item["original"]
        require(isinstance(name, str) and re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", name) is not None,
                "Unsafe component identifier")
        require(name not in names, "Duplicate component")
        names.add(name)
        path = root / "src" / "game" / (name + ".java")
        require(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()),
                "Source path must be a local regular file")
        require(path.is_file(), f"Missing private recovered source: src/game/{name}.java")
        require(sha(path.read_bytes()) == item["source_sha256"],
                f"Source snapshot changed for {name}; review and update its manifest before testing")
        result.append(path)
    require(bool(result), "No recovered components configured")
    return result


def write_jar(path: Path, entries: dict[str, bytes]) -> None:
    """Deterministic packaging of explicit entries; never auto-add dependencies."""
    require(not path.exists(), f"Refusing to overwrite {path}")
    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        for name, data in sorted(entries.items()):
            require(re.fullmatch(r"[A-Za-z0-9_$]+\.class", name) is not None, "Unexpected class entry")
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            out.writestr(info, data, compresslevel=9)


def traces(text: str) -> dict:
    parsed = {}
    for line in text.splitlines():
        parts = line.split("\t")
        require(len(parts) == 3, "Malformed probe output")
        group, count, digest = parts
        require(re.fullmatch(r"[a-z-]+", group) is not None and group not in parsed,
                "Invalid/duplicate probe group")
        require(count.isdecimal() and int(count) > 0, "Invalid probe call count")
        require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None, "Invalid probe digest")
        parsed[group] = {"calls_per_side": int(count), "trace_sha256": digest}
    require(bool(parsed), "Probe produced no result")
    return parsed


def compare_traces(reference: str, candidate: str) -> dict:
    left, right = traces(reference), traces(candidate)
    require(left == right, "Original/recovered observation traces differ; inspect the local logs")
    return left


def method_inventory(text: str) -> list[tuple[str, str]]:
    """Read javap -p -s signatures for this default-package, non-generic target."""
    result, pending = [], None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("descriptor:"):
            if pending is not None:
                result.append((pending, s.split(":", 1)[1].strip()))
                pending = None
        elif s == "static {};":
            pending = "<clinit>"
        elif "(" in s and s.endswith(";"):
            pending = s.split("(", 1)[0].split()[-1]
    require(bool(result) and len(set(result)) == len(result), "Cannot inventory method signatures")
    return result


def run(root: Path, run_dir: Path) -> dict:
    target = json.loads((root / "config/target.json").read_text(encoding="utf-8"))
    config = json.loads((root / SOURCE_CONFIG).read_text(encoding="utf-8"))
    require(config["target_id"] == target["id"], "Component target mismatch")
    original = root / "inputs/original" / target["filename"]
    input_data = pinned_input(original, target)
    sources = source_files(root, config)
    for tool in ("java", "javac", "javap"):
        require(shutil.which(tool) is not None, f"A JDK with {tool} is required")
    require(not run_dir.exists(), "Choose a new run directory; existing evidence is not overwritten")
    run_dir.mkdir(parents=True)
    for sub in ("logs", "support", "classes", "empty-sourcepath", "resources"):
        (run_dir / sub).mkdir()
    env = os.environ.copy()
    for key in ("JAVA_TOOL_OPTIONS", "_JAVA_OPTIONS", "JDK_JAVA_OPTIONS", "CLASSPATH"):
        env.pop(key, None)
    commands = []

    def command(args: list[str], label: str, timeout: int = 45) -> str:
        commands.append(args)
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, env=env)
        (run_dir / "logs" / (label + ".stdout")).write_text(p.stdout, encoding="utf-8")
        (run_dir / "logs" / (label + ".stderr")).write_text(p.stderr, encoding="utf-8")
        (run_dir / "commands.json").write_text(json_text(commands), encoding="utf-8")
        require(p.returncode == 0, f"{label} exited {p.returncode}; see local logs")
        return p.stdout

    java_version = command(["java", "-version"], "java-version")
    # java -version writes its version to stderr.
    java_version += (run_dir / "logs/java-version.stderr").read_text(encoding="utf-8")
    javac_version = command(["javac", "-version"], "javac-version")
    support_sources = [str(root / p) for p in SUPPORT]
    command(["javac", "--release", "8", "-g:none", "-d", str(run_dir / "support"),
             *support_sources], "compile-probe-and-test-doubles")
    require(not any((run_dir / "support" / (p.stem + ".class")).exists() for p in sources),
            "Test support must not provide recovered game classes")
    command(["javac", "--release", "8", "-g:none", "-implicit:none", "-sourcepath",
             str(run_dir / "empty-sourcepath"), "-classpath", str(run_dir / "support"),
             "-d", str(run_dir / "classes"), *map(str, sources)], "compile-recovered-components")
    expected = {p.stem + ".class" for p in sources}
    actual = {p.relative_to(run_dir / "classes").as_posix() for p in (run_dir / "classes").rglob("*") if p.is_file()}
    require(actual == expected, "Component compiler output differs from the exact source allowlist")
    rebuilt_entries = {name: (run_dir / "classes" / name).read_bytes() for name in expected}
    rebuilt = run_dir / "rebuilt-components.jar"
    write_jar(rebuilt, rebuilt_entries)
    # Deliberately separate reference-only artifact; NEVER on rebuilt compiler or probe classpaths.
    with zipfile.ZipFile(original) as archive:
        reference_entries = {name: archive.read(name) for name in expected}
        object_data = archive.read("data/objects.dat")
    require(sha(object_data) == config["object_resource_sha256"], "Object resource mismatch")
    reference = run_dir / "reference-only.jar"
    write_jar(reference, reference_entries)
    members, comparisons = {}, []
    for component in config["components"]:
        name = component["original"]
        require(sha(reference_entries[name + ".class"]) == component["original_class_sha256"],
                f"Original component snapshot mismatch in {name}")
        a = method_inventory(command(["javap", "-p", "-s", "-classpath", str(reference), name], name + "-reference-signatures"))
        b = method_inventory(command(["javap", "-p", "-s", "-classpath", str(rebuilt), name], name + "-rebuilt-signatures"))
        require(a == b and len(a) == component["method_entries"], f"Member signature inventory changed in {name}")
        raw_a, raw_b = reference_entries[name + ".class"], rebuilt_entries[name + ".class"]
        members[name] = {
            "method_entries": len(a), "method_signatures_identical": True,
            "original_class_sha256": sha(raw_a), "rebuilt_class_sha256": sha(raw_b),
            "exact_class_bytes": raw_a == raw_b,
            "original_class_version": [int.from_bytes(raw_a[6:8], "big"), int.from_bytes(raw_a[4:6], "big")],
            "rebuilt_class_version": [int.from_bytes(raw_b[6:8], "big"), int.from_bytes(raw_b[4:6], "big")],
        }

    def probe_pair(scenario: str, resources: Path | None = None) -> None:
        logs = []
        for side, artifact in (("original", reference), ("candidate", rebuilt)):
            paths = [run_dir / "support", artifact]
            if resources is not None: paths.append(resources)
            args = ["java", "-Xmx128m", "-cp", os.pathsep.join(map(str, paths)), "ComponentProbe", side]
            if resources is not None: args.append("tables")
            logs.append(command(args, scenario + "-" + side))
        comparisons.append({"scenario": scenario, "result": "passed_scoped",
                            "groups": compare_traces(*logs)})

    probe_pair("core")
    for length in TABLE_LENGTHS:
        resources = run_dir / "resources" / str(length)
        resources.mkdir()
        if length >= 0:
            (resources / "data").mkdir()
            (resources / "data/objects.dat").write_bytes(object_data[:length])
        probe_pair("table-" + str(length), resources)
    report = {
        "schema_version": 1, "scope": "component tests only; not a full game, handset test or native port",
        "recovery_method": "manual source reconstruction from pinned original javap bytecode",
        "target_id": target["id"], "original_sha256": sha(input_data),
        "source_snapshots": {str(p.relative_to(root)): sha(p.read_bytes()) for p in sources},
        "test_tool_snapshots": {p: sha((root / p).read_bytes()) for p in (*SUPPORT, "tools/component_recovery.py", SOURCE_CONFIG)},
        "java_version": java_version.strip(), "javac_version": javac_version.strip(),
        "rebuilt_components_sha256": sha(rebuilt.read_bytes()),
        "component_inventory": members, "comparisons": comparisons,
        "compared_calls_per_side": sum(g["calls_per_side"] for r in comparisons for g in r["groups"].values()),
        "has_gameplay_stubs_in_rebuilt_jar": False,
        "test_doubles": ["javax.microedition.lcdui.Image: scripted call recorder, no pixels",
                         "o: three-field test record, no entities or AI"],
        "limitations": ["18 game classes not recovered by this pass",
                        "No full-game source-only build or playtest",
                        "Not a handset or Windows native-port test",
                        "Observation digests cover only the explicitly authored cases",
                        "Exception types compared; messages, stack traces and GC timing not compared",
                        "Signature equality is not bytecode or behavioral equivalence",
                        "No exact/normalized whole-class match claimed"],
    }
    (run_dir / "report.json").write_text(json_text(report), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True, help="A NEW local evidence directory")
    args = parser.parse_args(argv)
    try:
        report = run(ROOT, args.run_dir.resolve())
        print(f"Compared {report['compared_calls_per_side']} calls per side in scoped component tests.")
        print(f"Report: {args.run_dir / 'report.json'}; no full game or native build is implied.")
        return 0
    except (RecoveryError, OSError, subprocess.SubprocessError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
