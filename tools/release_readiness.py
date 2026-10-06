#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

REQUIRED_EVIDENCE={
    "source_recovery":"docs/evidence/RECOVERY_PASS_010.md",
    "whole_tree_build":"docs/evidence/INTEGRATION_PASS_011.md",
    "desktop_runtime":"docs/evidence/INTEGRATION_PASS_014_DESKTOP_RUNTIME.md",
    "desktop_build":"docs/evidence/INTEGRATION_PASS_015_DESKTOP_BUILD.md",
    "amr_audio":"docs/evidence/INTEGRATION_PASS_016_AMR_AUDIO.md",
    "campaign_matrix":"docs/evidence/INTEGRATION_PASS_017_CAMPAIGN_AUTOMATION.md",
    "native_aot_prep":"docs/evidence/INTEGRATION_PASS_018_NATIVE_AOT_PREP.md",
    "campaign_progression":"docs/evidence/INTEGRATION_PASS_019_CAMPAIGN_PROGRESSION.md",
    "automated_gate":"docs/evidence/INTEGRATION_PASS_020_AUTOMATED_GATE.md",
    "mission_stress":"docs/evidence/INTEGRATION_PASS_021_MISSION_STRESS.md",
    "mission_fuzz":"docs/evidence/INTEGRATION_PASS_022_MISSION_FUZZ.md",
    "desktop_polish":"docs/evidence/INTEGRATION_PASS_023_DESKTOP_POLISH.md",
    "audio_sanity":"docs/evidence/INTEGRATION_PASS_024_AUDIO_SANITY.md",
    "mission_soak":"docs/evidence/INTEGRATION_PASS_025_MISSION_SOAK.md",
}

HUMAN_ONLY=[
    "interactive full-campaign playtest for control feel and unscripted edge cases",
    "subjective audio loudness/mix/timing judgment on a real audio device",
    "subjective desktop presentation/window-scaling judgment",
]

ENVIRONMENT_ONLY=[
    "produce and validate a Windows native executable on a Windows GraalVM/MSVC/Windows-SDK host",
]

def load_json(path:Path):
    return json.loads(path.read_text())

def source_map_summary():
    data=load_json(ROOT/"config/source_map.json")
    classes=data["classes"]
    repaired=sum(1 for row in classes if row["recovery"]["state"]=="repaired")
    built=sum(1 for row in classes if row["build"]["state"]=="passed")
    behavior=sum(1 for row in classes if row["behavior"]["state"]=="passed_scoped")
    methods=sum(row["method_entries"] for row in classes)
    return {
        "classes":len(classes),
        "method_entries":methods,
        "repaired":repaired,
        "build_passed":built,
        "behavior_scoped_passed":behavior,
    }

def inspect():
    missing=[path for path in REQUIRED_EVIDENCE.values() if not (ROOT/path).is_file()]
    summary=source_map_summary()
    machine_gates={
        "all_21_classes_repaired":summary["classes"]==21 and summary["repaired"]==21,
        "all_313_method_entries_accounted":summary["method_entries"]==313,
        "all_21_classes_built_in_documented_scope":summary["build_passed"]==21,
        "all_21_classes_behavior_compared_in_documented_scope":summary["behavior_scoped_passed"]==21,
        "required_evidence_present":not missing,
    }
    machine_ready=all(machine_gates.values())

    native_evidence=ROOT/"docs/evidence/integration-pass-018-native-aot-prep.json"
    native_built=False
    if native_evidence.is_file():
        native_built=bool(load_json(native_evidence).get("windows_executable_built",False))

    result={
        "schema_version":1,
        "target_id":"dah1-j2me-en-v1.2.0",
        "source_map":summary,
        "machine_gates":machine_gates,
        "missing_evidence":missing,
        "machine_release_readiness":machine_ready,
        "human_only_remaining":HUMAN_ONLY,
        "environment_only_remaining":[] if native_built else ENVIRONMENT_ONLY,
        "native_windows_executable_built":native_built,
        "gold":False,
        "gold_reason":"Gold requires human subjective playtest/judgment and a validated native Windows executable in addition to machine gates.",
    }
    return result

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path)
    ap.add_argument("--check",action="store_true",help="Exit nonzero unless all machine-checkable gates pass.")
    args=ap.parse_args(argv)
    result=inspect()
    text=json.dumps(result,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text)
    print(text,end="")
    if args.check and not result["machine_release_readiness"]:
        return 1
    return 0

if __name__=="__main__":
    raise SystemExit(main())
