#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUMAN_ONLY_REMAINING = [
    "interactive full-campaign playtest for control feel and unscripted edge cases",
    "subjective audio loudness/mix/timing judgment on a real audio device",
    "subjective desktop presentation/window-scaling judgment",
]
ENVIRONMENT_REMAINING = [
    "produce and validate the Windows native executable on a Windows GraalVM/MSVC/Windows-SDK host",
]

def run(cmd, cwd=ROOT):
    p = subprocess.run([str(x) for x in cmd], cwd=cwd, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(
            "command failed: " + " ".join(map(str, cmd)) +
            "\nSTDOUT:\n" + p.stdout + "\nSTDERR:\n" + p.stderr
        )
    return p.stdout

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def audio_companions(jar: Path):
    with zipfile.ZipFile(jar) as z:
        amr = sorted(x for x in z.namelist() if x.lower().endswith(".amr"))
        wav = sorted(x for x in z.namelist() if x.startswith("META-INF/dah-audio/") and x.endswith(".wav"))
        classes = sorted(x for x in z.namelist() if x.endswith(".class"))
        launcher = "DesktopLauncher.class" in z.namelist()
    return {"amr": amr, "wav": wav, "classes": classes, "direct_launcher": launcher}

def build_candidate(args, work: Path):
    if args.candidate:
        return args.candidate.resolve(), None
    candidate = work / "DAH-Mobile-Desktop.jar"
    report = work / "desktop-build.json"
    cmd = [
        sys.executable, ROOT / "tools" / "desktop_build.py",
        "--input", args.input,
        "--source-dir", args.source_dir,
        "--output", candidate,
        "--report", report,
    ]
    if args.ffmpeg:
        cmd += ["--ffmpeg", args.ffmpeg]
    run(cmd)
    return candidate, json.loads(report.read_text())

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=ROOT / "inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar")
    ap.add_argument("--source-dir", type=Path, default=ROOT / "src/game")
    ap.add_argument("--candidate", type=Path)
    ap.add_argument("--ffmpeg")
    ap.add_argument("--report", type=Path)
    ap.add_argument("--skip-public-tests", action="store_true")
    args = ap.parse_args(argv)

    checks = {}
    with tempfile.TemporaryDirectory(prefix="dah-full-validation-") as td:
        work = Path(td)

        if not args.skip_public_tests:
            run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
            checks["public_tests"] = "passed"
        else:
            checks["public_tests"] = "skipped"

        candidate, build_report = build_candidate(args, work)
        if not candidate.is_file():
            raise RuntimeError("desktop candidate missing")
        checks["candidate_sha256"] = sha256(candidate)

        inventory = audio_companions(candidate)
        if len(inventory["amr"]) != 4 or len(inventory["wav"]) != 4:
            raise RuntimeError("desktop candidate must contain 4 retail AMRs and 4 converted WAV companions")
        if not inventory["direct_launcher"]:
            raise RuntimeError("DesktopLauncher.class missing")
        checks["audio_packaging"] = {"amr": 4, "wav": 4}
        checks["direct_launcher"] = True

        run([
            "java", "-Djava.awt.headless=true", "-cp", candidate,
            "DesktopLauncher", "--native-smoke",
        ])
        checks["native_smoke"] = "passed"

        campaign_report = work / "campaign-matrix.json"
        run([
            sys.executable, ROOT / "tools" / "campaign_validation.py",
            "--input", args.input,
            "--candidate", candidate,
            "--report", campaign_report,
        ])
        campaign = json.loads(campaign_report.read_text())
        if campaign.get("missions") != 13 or not campaign.get("all_original_rebuilt_outputs_identical"):
            raise RuntimeError("campaign matrix did not pass")
        checks["campaign_matrix"] = {
            "missions": 13,
            "passed": True,
        }

        stress_report = work / "mission-stress.json"
        run([
            sys.executable, ROOT / "tools" / "mission_stress.py",
            "--input", args.input,
            "--candidate", candidate,
            "--report", stress_report,
        ])
        stress = json.loads(stress_report.read_text())
        if stress.get("missions") != 13 or stress.get("total_frames") != 3900 or not stress.get("retail_rebuilt_outputs_identical"):
            raise RuntimeError("mission stress did not pass")
        checks["mission_stress"] = {
            "missions": 13,
            "total_frames": 3900,
            "passed": True,
            "aggregate_stdout_sha256": stress["aggregate_stdout_sha256"],
        }

        progression_report = work / "campaign-progression.json"
        run([
            sys.executable, ROOT / "tools" / "campaign_progression.py",
            "--input", args.input,
            "--candidate", candidate,
            "--report", progression_report,
        ])
        progression = json.loads(progression_report.read_text())
        if progression.get("missions") != 13 or not progression.get("retail_rebuilt_rms_identical_each_step"):
            raise RuntimeError("campaign progression did not pass")
        checks["campaign_progression"] = {
            "missions": 13,
            "passed": True,
            "final_rms_file_sha256": progression["final_rms_file_sha256"],
        }

        native_report = work / "native-preflight.json"
        run([
            sys.executable, ROOT / "tools" / "native_build.py",
            "--desktop-jar", candidate,
            "--prepare-only",
            "--report", native_report,
        ])
        native = json.loads(native_report.read_text())
        if not native.get("direct_launcher"):
            raise RuntimeError("native preflight did not recognize direct launcher")
        checks["native_preflight"] = "passed"

        result = {
            "schema_version": 1,
            "target_id": "dah1-j2me-en-v1.2.0",
            "automated_gate_passed": True,
            "checks": checks,
            "build_report": build_report,
            "human_only_remaining": HUMAN_ONLY_REMAINING,
            "environment_remaining": ENVIRONMENT_REMAINING,
            "gold": False,
        }
        text = json.dumps(result, indent=2) + "\n"
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(text)
        print(text, end="")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("full_validation:", exc, file=sys.stderr)
        raise SystemExit(1)
