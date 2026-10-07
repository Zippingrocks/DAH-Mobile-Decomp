#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys, tempfile
from pathlib import Path
if __package__:
    from . import mission_stress as ms
else:
    import mission_stress as ms

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/"config/mission_soak.json"

def load_config():
    return json.loads(CONFIG.read_text())

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,default=ROOT/"inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar")
    ap.add_argument("--source-dir",type=Path,default=ROOT/"src/game")
    ap.add_argument("--candidate",type=Path)
    ap.add_argument("--ffmpeg")
    ap.add_argument("--report",type=Path)
    args=ap.parse_args(argv)

    original=args.input.resolve();ms.verify_input(original);cfg=load_config()
    with tempfile.TemporaryDirectory(prefix="dah-mission-soak-") as td:
        work=Path(td);support,probes=ms.compile_probes(work,original);candidate=ms.build_candidate(args,work)
        rows=[];outputs=[]
        for expected in cfg["missions"]:
            mission=expected["mission"]
            retail=ms.run_mission(support,probes,original,mission,cfg["frames_per_mission"])
            rebuilt=ms.run_mission(support,probes,candidate,mission,cfg["frames_per_mission"])
            if retail!=rebuilt:
                raise RuntimeError("mission %d soak mismatch"%mission)
            digest=hashlib.sha256(retail.encode()).hexdigest()
            if digest!=expected["sha256"]:
                raise RuntimeError("mission %d expected soak hash mismatch"%mission)
            rows.append({"mission":mission,"sha256":digest});outputs.append(retail)
        aggregate=hashlib.sha256("".join(outputs).encode()).hexdigest()
        if aggregate!=cfg["aggregate_stdout_sha256"]:
            raise RuntimeError("aggregate soak hash mismatch")
        report={"schema_version":1,"target_id":cfg["target_id"],"missions":13,"frames_per_mission":cfg["frames_per_mission"],"total_frames":cfg["total_frames"],"retail_rebuilt_outputs_identical":True,"aggregate_stdout_sha256":aggregate,"rows":rows}
        text=json.dumps(report,indent=2)+"\n"
        if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(text)
        print(text,end="")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:print("mission_soak:",exc,file=sys.stderr);raise SystemExit(1)
