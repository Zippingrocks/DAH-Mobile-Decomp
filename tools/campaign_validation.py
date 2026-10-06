#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "campaign_matrix.json"
PROBE = ROOT / "tests" / "java" / "CampaignMatrixProbe.java"
RUNTIME = ROOT / "runtime" / "desktop"

def run(cmd, cwd=ROOT):
    result = subprocess.run([str(x) for x in cmd], cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError("command failed: " + " ".join(map(str, cmd)) + "\nSTDOUT:\n" + result.stdout + "\nSTDERR:\n" + result.stderr)
    return result.stdout

def load_config():
    return json.loads(CONFIG.read_text())

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

def compile_probe(work: Path):
    runtime_classes = work / "runtime"
    probe_classes = work / "probe"
    runtime_classes.mkdir()
    probe_classes.mkdir()
    runtime_sources = sorted(RUNTIME.rglob("*.java"))
    run(["javac", "--release", "8", "-g:none", "-d", runtime_classes, *runtime_sources])
    run(["javac", "--release", "8", "-g:none", "-cp", runtime_classes, "-d", probe_classes, PROBE])
    return runtime_classes, probe_classes

def parse_state(output: str):
    lines = output.strip().splitlines()
    if len(lines) != 2 or not lines[1].startswith("sha="):
        raise RuntimeError("unexpected campaign probe output: " + repr(output))
    values = {}
    for part in lines[0].split(","):
        key, value = part.split("=", 1)
        if value in ("true", "false"):
            values[key] = value == "true"
        else:
            values[key] = int(value)
    values["sha256"] = lines[1][4:]
    if values["sha256"] != sha256_text(lines[0]):
        raise RuntimeError("campaign probe self-hash mismatch")
    return values

def run_one(runtime_classes: Path, probe_classes: Path, game_jar: Path, mission: int, bundled_runtime: bool):
    if bundled_runtime:
        cp = os.pathsep.join([str(probe_classes), str(game_jar)])
    else:
        cp = os.pathsep.join([str(runtime_classes), str(probe_classes), str(game_jar)])
    return run(["java", "-Djava.awt.headless=true", "-cp", cp, "CampaignMatrixProbe", str(mission)])

def build_candidate(args, work: Path):
    if args.candidate:
        return args.candidate.resolve()
    output = work / "candidate-desktop.jar"
    report = work / "desktop-build.json"
    cmd = [
        sys.executable, ROOT / "tools" / "desktop_build.py",
        "--input", args.input,
        "--source-dir", args.source_dir,
        "--output", output,
        "--report", report,
    ]
    if args.ffmpeg:
        cmd += ["--ffmpeg", args.ffmpeg]
    run(cmd)
    return output

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar")
    parser.add_argument("--source-dir", type=Path, default=ROOT / "src/game")
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)

    cfg = load_config()
    with tempfile.TemporaryDirectory(prefix="dah-campaign-") as td:
        work = Path(td)
        runtime_classes, probe_classes = compile_probe(work)
        candidate = build_candidate(args, work)
        rows = []
        for expected in cfg["missions"]:
            mission = expected["mission"]
            original_out = run_one(runtime_classes, probe_classes, args.input.resolve(), mission, False)
            candidate_out = run_one(runtime_classes, probe_classes, candidate, mission, True)
            if original_out != candidate_out:
                raise RuntimeError("mission %d retail/rebuilt mismatch\nRETAIL:\n%s\nREBUILT:\n%s" % (mission, original_out, candidate_out))
            actual = parse_state(original_out)
            for key in ("m","kind","authored","mode","map","target","dynamic","initial","complete","progress","sha256"):
                expected_key = "mission" if key == "m" else key
                if actual[key] != expected[expected_key]:
                    raise RuntimeError("mission %d expected %s=%r but got %r" % (mission, key, expected[expected_key], actual[key]))
            rows.append(actual)

        report = {
            "schema_version": 1,
            "target_id": cfg["target_id"],
            "missions": len(rows),
            "all_original_rebuilt_outputs_identical": True,
            "all_expected_matrix_rows_match": True,
            "rows": rows,
        }
        text = json.dumps(report, indent=2) + "\n"
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(text)
        print(text, end="")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("campaign_validation:", exc, file=sys.stderr)
        raise SystemExit(1)
