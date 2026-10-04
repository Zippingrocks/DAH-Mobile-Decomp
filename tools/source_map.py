#!/usr/bin/env python3
"""Generate/check the source-tree map. Status records are claims, not fidelity proof."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "config/source_map.json"
OUTPUT = "docs/SOURCE_TREE.md"
KINDS = {"tool", "tests", "config", "docs", "generated", "policy"}
STATES = {
    "recovery": {"not_started", "raw_output", "repaired"},
    "build": {"not_tested", "failed", "passed"},
    "behavior": {"not_tested", "differences", "passed_scoped"},
}


class MapError(ValueError):
    """The map is incomplete, unsafe, or contradicts its declared evidence."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MapError(message)


def text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and not any(
        c in value for c in "\r\n\t|`<>"
    )


def safe_path(value: object) -> bool:
    if not text(value) or not re.fullmatch(r"[A-Za-z0-9_. /-]+", value):
        return False
    path = PurePosixPath(value)
    return (bool(path.parts) and not path.is_absolute() and str(path) == value
            and all(p not in {".", "..", ".git"} for p in path.parts))


def read_json(path: Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def tracked_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=True, capture_output=True, timeout=20,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise MapError("A Git checkout with Git installed is required for file coverage") from exc
    return sorted(set(p for p in result.stdout.decode("utf-8").split("\0") if p))


def validate(data: dict, target: dict, root: Path, tracked: list[str], audit: dict | None = None) -> None:
    require(isinstance(data, dict) and data.get("schema_version") == 1, "Unsupported map schema")
    require(data.get("target_id") == target["id"], "Map target differs from target.json")
    require(data.get("input_sha256") == target["sha256"], "Map input hash differs from target.json")
    entries = data["files"]
    require(isinstance(entries, list) and bool(entries), "No mapped files")
    mapped = []
    for entry in entries:
        p = entry["path"]
        require(safe_path(p), f"Unsafe mapped path: {p!r}")
        require(entry["kind"] in KINDS and text(entry["purpose"]), f"Invalid file metadata: {p}")
        absolute = root / p
        require(absolute.resolve().is_relative_to(root.resolve()), f"Path escapes repository: {p}")
        require(absolute.is_file() and not absolute.is_symlink(), f"Missing/nonregular mapped file: {p}")
        mapped.append(p)
    require(len(mapped) == len(set(mapped)), "Duplicate mapped file")
    require(set(mapped) == set(tracked),
            f"Map/index mismatch. Unmapped: {sorted(set(tracked)-set(mapped))}; "
            f"not tracked: {sorted(set(mapped)-set(tracked))}. Stage new files before checking.")

    def evidence(items: object) -> None:
        require(isinstance(items, list), "Evidence must be a list")
        for item in items:
            require(isinstance(item, dict), "Evidence must contain path/scope records")
            require(item.get("path") in mapped and text(item.get("scope")),
                    "Evidence must name a mapped file and a nonempty test/review scope")

    classes = data["classes"]
    require(isinstance(classes, list), "Classes must be a list")
    require(len(classes) == target["expected_static_counts"]["class_count"], "Class count mismatch")
    names = set()
    methods = 0
    for cls in classes:
        name = cls["original"]
        require(isinstance(name, str) and bool(re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", name)),
                "Invalid original class name")
        require(name not in names, f"Duplicate original class: {name}")
        names.add(name)
        n = cls["method_entries"]
        require(type(n) is int and n > 0, f"Invalid method count: {name}")
        methods += n
        source = cls["source_path"]
        require(source is None or safe_path(source), f"Unsafe source path: {name}")
        for stage, states in STATES.items():
            record = cls[stage]
            require(record["state"] in states, f"Unknown {stage} state: {name}")
            evidence(record["evidence"])
            default = "not_started" if stage == "recovery" else "not_tested"
            if record["state"] != default:
                require(bool(record["evidence"]), f"{stage} change needs scoped evidence: {name}")
        recovered = cls["recovery"]["state"] != "not_started"
        require(recovered == (source is not None), f"Recovery/source-path disagreement: {name}")
        if cls["build"]["state"] != "not_tested":
            require(recovered, f"Build attempted without source recovery: {name}")
        if cls["build"]["state"] == "passed":
            require(cls["recovery"]["state"] == "repaired", f"Successful build needs repaired source: {name}")
        if cls["behavior"]["state"] != "not_tested":
            require(cls["build"]["state"] == "passed", f"Behavior test needs source-only build: {name}")
    require(target["entry_class"] in names, "Entry class missing")
    require(methods == target["expected_static_counts"]["method_entries"], "Method total mismatch")
    planned_ids = set()
    for stage in data["planned"]:
        require(text(stage["area"]) and stage["area"] not in planned_ids, "Invalid/duplicate planned area")
        planned_ids.add(stage["area"])
        require(text(stage["purpose"]), "Missing planned purpose")
        require(stage["state"] == "not_started", "Move started work out of the planned-only list")
    if audit is not None:
        require(audit["input_sha256"] == data["input_sha256"], "Audit hash mismatch")
        require(audit["input_size_bytes"] == target["size_bytes"], "Audit size mismatch")
        audited = {c["class"]: c["method_entries"] for c in audit["classes"]}
        require(len(audited) == len(audit["classes"]), "Duplicate audit class")
        require(audited == {c["original"]: c["method_entries"] for c in classes},
                "Class inventory differs from the supplied static audit")


def tree_lines(entries: list[dict]) -> list[str]:
    tree: dict = {}
    for entry in sorted(entries, key=lambda e: e["path"]):
        parts = entry["path"].split("/")
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = entry
    lines = ["DAH-Mobile-Decomp/"]

    def walk(node: dict, prefix: str) -> None:
        for i, (name, child) in enumerate(sorted(node.items())):
            last = i == len(node) - 1
            branch = "`-- " if last else "|-- "
            if "path" in child and isinstance(child["path"], str):
                lines.append(f"{prefix}{branch}{name} [{child['kind'].upper()}]")
            else:
                lines.append(f"{prefix}{branch}{name}/")
                walk(child, prefix + ("    " if last else "|   "))
    walk(tree, "")
    return lines


def link(path: str) -> str:
    return f"[`{path}`](../{quote(path, safe='/')})"


def render(data: dict) -> str:
    classes = sorted(data["classes"], key=lambda c: c["original"])
    count = len(classes)
    totals = {stage: Counter(c[stage]["state"] for c in classes) for stage in STATES}
    lines = [
        "<!-- Generated by tools/source_map.py; edit config/source_map.json, not this file. -->",
        "# Source tree and implementation map", "",
        "[Repository home](../README.md) | [Status](STATUS.md) | [Maintenance guide](SOURCE_MAP_GUIDE.md)", "",
        "**Scope: first mobile game, English v1.2.0. Inventory is not implementation; "
        "a successful build is not verified game accuracy.**", "",
        "## Progress at a glance", "",
        "| Measure | Recorded result |", "| --- | --- |",
        f"| Original classes inventoried | {count} |",
        f"| Original method entries inventoried (including initialization) | {sum(c['method_entries'] for c in classes)} |",
        f"| Classes with source recovery recorded (raw or repaired) | {count-totals['recovery']['not_started']} / {count} |",
        f"| Classes with repaired source recorded | {totals['recovery']['repaired']} / {count} |",
        f"| Classes included in a successful source-only build | {totals['build']['passed']} / {count} |",
        f"| Classes with behavior comparisons passed in a documented scope | {totals['behavior']['passed_scoped']} / {count} |", "",
        "These are class-level records, not a percentage complete or method-level proof. "
        "A stage changes only when its evidence is recorded; the generator does not run "
        "a decompiler, compile the game, or verify behavioral equivalence.", "",
        "## Actual tracked tree", "",
        "TOOL = implemented project tool; TESTS = test code, not a pass result; "
        "CONFIG/POLICY/DOCS = supporting files; GENERATED = generated documentation. "
        "No planned directory is displayed as existing source.", "", "```text",
        *tree_lines(data["files"]), "```", "",
        "### What the existing files do", "",
        "| File | Kind | Implemented purpose / documented responsibility |", "| --- | --- | --- |",
    ]
    for entry in sorted(data["files"], key=lambda e: e["path"]):
        lines.append(f"| {link(entry['path'])} | {entry['kind']} | {entry['purpose']} |")
    lines += ["", "## Original-class recovery register", "",
              "Original identifiers are preserved until readable names are established. "
              "Single-letter classes are not assigned guessed gameplay responsibilities. "
              "Source paths are pointers only and may remain private; this report never reads or publishes their contents.", "",
              "| Original class | Method entries | Source path | Recovery | Source-only build | Behavior |",
              "| --- | ---: | --- | --- | --- | --- |"]
    for cls in classes:
        source = f"`{cls['source_path']}`" if cls["source_path"] else "Not recovered"
        states = " | ".join(cls[s]["state"] for s in STATES)
        lines.append(f"| `{cls['original']}` | {cls['method_entries']} | {source} | {states} |")
    records = [(c, s, e) for c in classes for s in STATES for e in c[s]["evidence"]]
    lines += ["", "### Recovery/build/behavior evidence", ""]
    if not records:
        lines.append("None recorded. The structural inventory alone does not qualify as recovery evidence.")
    for cls, stage, entry in records:
        lines.append(f"- `{cls['original']}` / {stage}: {link(entry['path'])} — {entry['scope']}")
    lines += ["", "## Planned work — not implemented", "",
              "These are future work areas, not existing source folders or completed systems.", "",
              "| Area | State | Work remaining |", "| --- | --- | --- |"]
    for stage in data["planned"]:
        lines.append(f"| {stage['area']} | {stage['state']} | {stage['purpose']} |")
    lines += ["", "## Input provenance and refresh", "",
              f"Target: `{data['target_id']}`. Original SHA-256:", "",
              f"`{data['input_sha256']}`", "",
              "The inventory was checked against a local hash-verified structural audit. "
              "The original JAR, assets, disassembly, and recovered game source are not included in this map.", "",
              "```console", "python tools/source_map.py", "python tools/source_map.py --check", "```", "",
              "With a locally generated audit, also use "
              "`python tools/source_map.py --check --audit local/audit-source-map.json`. "
              "New tracked files need manifest entries. See the maintenance guide for staging order and evidence rules.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail instead of writing when the map is stale")
    parser.add_argument("--audit", type=Path, help="Optional local dah1.py audit for class-inventory comparison")
    args = parser.parse_args(argv)
    try:
        data = read_json(ROOT / MANIFEST)
        target = read_json(ROOT / "config/target.json")
        audit = read_json(args.audit) if args.audit else None
        validate(data, target, ROOT, tracked_files(ROOT), audit)
        expected = render(data)
        path = ROOT / OUTPUT
        if args.check:
            require(path.read_text(encoding="utf-8") == expected,
                    "Source map is stale; run python tools/source_map.py and commit the result")
            print("Source map is current; metadata checks passed (not a game-fidelity test)")
        else:
            path.write_text(expected, encoding="utf-8", newline="\n")
            print(f"Generated {OUTPUT}; no game progress was inferred")
        return 0
    except (MapError, OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
