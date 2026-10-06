#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/"config/mission_fuzz.json"
TARGET=ROOT/"config/target.json"
SUPPORT=ROOT/"tests/java/integration_support"
STATE_PROBE=ROOT/"tests/java/StateProbe.java"
FUZZ_PROBE=ROOT/"tests/java/MissionFuzzProbe.java"

def run(cmd,cwd=ROOT):
    p=subprocess.run([str(x) for x in cmd],cwd=cwd,text=True,capture_output=True)
    if p.returncode:
        raise RuntimeError("command failed: "+" ".join(map(str,cmd))+"\nSTDOUT:\n"+p.stdout+"\nSTDERR:\n"+p.stderr)
    return p.stdout

def sha256(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_config():
    return json.loads(CONFIG.read_text())

def verify_input(path:Path):
    target=json.loads(TARGET.read_text())
    if not path.is_file() or path.stat().st_size!=target["size_bytes"] or sha256(path)!=target["sha256"]:
        raise RuntimeError("wrong original input")

def compile_probes(work:Path,original:Path):
    support=work/"support";probes=work/"probes";support.mkdir();probes.mkdir()
    sources=sorted(SUPPORT.rglob("*.java"))
    run(["javac","--release","8","-g:none","-implicit:none","-d",support,*sources])
    cp=os.pathsep.join([str(support),str(original)])
    run(["javac","--release","8","-g:none","-implicit:none","-cp",cp,"-d",probes,STATE_PROBE,FUZZ_PROBE])
    return support,probes

def build_candidate(args,work:Path):
    if args.candidate:return args.candidate.resolve()
    out=work/"candidate.jar"
    cmd=[sys.executable,ROOT/"tools/desktop_build.py","--input",args.input,"--source-dir",args.source_dir,"--output",out]
    if args.ffmpeg:cmd+=["--ffmpeg",args.ffmpeg]
    run(cmd)
    return out

def run_case(support:Path,probes:Path,game:Path,mission:int,frames:int,seed:int):
    cp=os.pathsep.join([str(support),str(probes),str(game)])
    return run(["java","-Djava.awt.headless=true","-cp",cp,"MissionFuzzProbe",str(mission),str(frames),str(seed)])

def parse_self_hash(output:str):
    lines=output.strip().splitlines()
    if len(lines)!=2 or not lines[1].startswith("sha="):
        raise RuntimeError("unexpected fuzz output: "+repr(output))
    digest=hashlib.sha256(lines[0].encode()).hexdigest()
    if digest!=lines[1][4:]:
        raise RuntimeError("fuzz output self-hash mismatch")
    return digest

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,default=ROOT/"inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar")
    ap.add_argument("--source-dir",type=Path,default=ROOT/"src/game")
    ap.add_argument("--candidate",type=Path)
    ap.add_argument("--ffmpeg")
    ap.add_argument("--report",type=Path)
    args=ap.parse_args(argv)

    original=args.input.resolve();verify_input(original);cfg=load_config()
    with tempfile.TemporaryDirectory(prefix="dah-mission-fuzz-") as td:
        work=Path(td);support,probes=compile_probes(work,original);candidate=build_candidate(args,work)
        rows=[];mission_hashes=[]
        for expected in cfg["missions"]:
            mission=expected["mission"];outputs=[]
            for seed in cfg["seeds"]:
                retail=run_case(support,probes,original,mission,cfg["frames_per_seed"],seed)
                rebuilt=run_case(support,probes,candidate,mission,cfg["frames_per_seed"],seed)
                if retail!=rebuilt:
                    raise RuntimeError("mission %d seed %d fuzz mismatch"%(mission,seed))
                parse_self_hash(retail)
                outputs.append(retail)
            digest=hashlib.sha256("".join(outputs).encode()).hexdigest()
            if digest!=expected["sha256"]:
                raise RuntimeError("mission %d expected fuzz hash mismatch"%mission)
            rows.append({"mission":mission,"sha256":digest})
            mission_hashes.append(digest)
        aggregate=hashlib.sha256("".join(mission_hashes).encode()).hexdigest()
        if aggregate!=cfg["aggregate_mission_hashes_sha256"]:
            raise RuntimeError("aggregate mission fuzz hash mismatch")
        report={"schema_version":1,"target_id":cfg["target_id"],"missions":13,"seeds":cfg["seeds"],"frames_per_seed":cfg["frames_per_seed"],"total_frames":cfg["total_frames"],"retail_rebuilt_outputs_identical":True,"aggregate_mission_hashes_sha256":aggregate,"rows":rows}
        text=json.dumps(report,indent=2)+"\n"
        if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(text)
        print(text,end="")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:print("mission_fuzz:",exc,file=sys.stderr);raise SystemExit(1)
