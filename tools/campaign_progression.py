#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/"config/campaign_progression.json"
PROBE=ROOT/"tests/java/CampaignProgressionStepProbe.java"
RUNTIME=ROOT/"runtime/desktop"

def run(cmd,cwd=ROOT):
    p=subprocess.run([str(x) for x in cmd],cwd=cwd,text=True,capture_output=True)
    if p.returncode:
        raise RuntimeError("command failed: "+" ".join(map(str,cmd))+"\nSTDOUT:\n"+p.stdout+"\nSTDERR:\n"+p.stderr)
    return p.stdout

def load_config():
    return json.loads(CONFIG.read_text())

def file_sha(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compile_probe(work:Path):
    runtime=work/"runtime";probe=work/"probe";runtime.mkdir();probe.mkdir()
    run(["javac","--release","8","-g:none","-d",runtime,*sorted(RUNTIME.rglob("*.java"))])
    run(["javac","--release","8","-g:none","-cp",runtime,"-d",probe,PROBE])
    return runtime,probe

def build_candidate(args,work:Path):
    if args.candidate:return args.candidate.resolve()
    out=work/"candidate.jar"
    cmd=[sys.executable,ROOT/"tools/desktop_build.py","--input",args.input,"--source-dir",args.source_dir,"--output",out]
    if args.ffmpeg:cmd += ["--ffmpeg",args.ffmpeg]
    run(cmd)
    return out

def parse(line:str):
    result={}
    for part in line.strip().split(","):
        k,v=part.split("=",1)
        result[k]=v if k=="save" else int(v)
    return result

def step(runtime,probe,game,mission,rms,bundled):
    cp=os.pathsep.join([str(probe),str(game)]) if bundled else os.pathsep.join([str(runtime),str(probe),str(game)])
    return run(["java","-Djava.awt.headless=true","-Ddah.rms.dir="+str(rms),"-cp",cp,"CampaignProgressionStepProbe",str(mission)])

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,default=ROOT/"inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar")
    ap.add_argument("--source-dir",type=Path,default=ROOT/"src/game")
    ap.add_argument("--candidate",type=Path)
    ap.add_argument("--ffmpeg")
    ap.add_argument("--report",type=Path)
    args=ap.parse_args(argv)
    cfg=load_config()
    with tempfile.TemporaryDirectory(prefix="dah-campaign-progression-") as td:
        work=Path(td);runtime,probe=compile_probe(work);candidate=build_candidate(args,work)
        original_rms=work/"retail-rms";rebuilt_rms=work/"rebuilt-rms";original_rms.mkdir();rebuilt_rms.mkdir()
        outputs=[];rows=[]
        for expected in cfg["steps"]:
            mission=expected["mission"]
            retail=step(runtime,probe,args.input.resolve(),mission,original_rms,False)
            rebuilt=step(runtime,probe,candidate,mission,rebuilt_rms,True)
            if retail!=rebuilt:raise RuntimeError("mission %d progression output mismatch"%mission)
            rfile=original_rms/"DAH.rms";cfile=rebuilt_rms/"DAH.rms"
            if not rfile.is_file() or not cfile.is_file() or rfile.read_bytes()!=cfile.read_bytes():
                raise RuntimeError("mission %d RMS files differ"%mission)
            actual=parse(retail)
            for key in ("mission","target","after","save"):
                if actual[key]!=expected[key]:raise RuntimeError("mission %d expected %s=%r got %r"%(mission,key,expected[key],actual[key]))
            outputs.append(retail);rows.append(actual)
        aggregate=hashlib.sha256("".join(outputs).encode()).hexdigest()
        if aggregate!=cfg["aggregate_stdout_sha256"]:raise RuntimeError("aggregate progression hash mismatch")
        final_file=original_rms/"DAH.rms"
        if final_file.stat().st_size!=cfg["final_rms_file_bytes"] or file_sha(final_file)!=cfg["final_rms_file_sha256"]:
            raise RuntimeError("final RMS file mismatch")
        report={"schema_version":1,"target_id":cfg["target_id"],"missions":13,"fresh_jvm_per_step":True,"shared_rms_across_steps":True,"retail_rebuilt_stdout_identical":True,"retail_rebuilt_rms_identical_each_step":True,"aggregate_stdout_sha256":aggregate,"final_rms_file_sha256":file_sha(final_file),"final_rms_file_bytes":final_file.stat().st_size,"rows":rows}
        text=json.dumps(report,indent=2)+"\n"
        if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(text)
        print(text,end="")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:print("campaign_progression:",exc,file=sys.stderr);raise SystemExit(1)
