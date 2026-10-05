"""Reproducible all-repaired source integration check for DAH Mobile v1.2.0.

Private game source and the original JAR are required locally. Public test support is
compiled separately and is never packaged into the candidate game JAR.
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'config/integration_recovery.json'
GAME=['GameMidlet']+list('abcdefghijklmnopqrst')

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def run(cmd, cwd=ROOT):
    p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True)
    if p.returncode:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(map(str,cmd))}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")
    return p.stdout,p.stderr

def config(): return json.loads(CFG.read_text())
def verify_private(cfg, jar):
    if not jar.is_file() or jar.stat().st_size!=cfg['input']['size'] or sha(jar)!=cfg['input']['sha256']:
        raise RuntimeError('original input identity mismatch')
    for row in cfg['classes']:
        p=ROOT/'src/game'/f"{row['class']}.java"
        if not p.is_file(): raise RuntimeError(f'missing private source: {p.relative_to(ROOT)}')
        if sha(p)!=row['sha256']: raise RuntimeError(f"private source hash mismatch: {row['class']}")

def compile_support(out):
    sources=sorted((ROOT/'tests/java/integration_support').rglob('*.java'))
    run(['javac','--release','8','-g:none','-implicit:none','-d',str(out),*[str(x) for x in sources]])

def compile_game(out,support):
    sources=[ROOT/'src/game'/f'{c}.java' for c in GAME]
    run(['javac','--release','8','-g:none','-implicit:none','-sourcepath','', '-cp',str(support),'-d',str(out),*[str(x) for x in sources]])
    actual=sorted(p.name for p in out.glob('*.class'))
    expect=sorted(f'{c}.class' for c in GAME)
    if actual!=expect: raise RuntimeError(f'game output roster mismatch: {actual}')

def build_candidate(original, game_classes, out):
    expected={f'{c}.class' for c in GAME}
    resources=[]
    with zipfile.ZipFile(original) as z:
        for info in z.infolist():
            if not info.filename.endswith('.class'): resources.append((info.filename,z.read(info.filename)))
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in resources:
            info=zipfile.ZipInfo(name,(2000,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
        for name in sorted(expected):
            info=zipfile.ZipInfo(name,(2000,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,(game_classes/name).read_bytes())
    with zipfile.ZipFile(out) as z:
        classes={n for n in z.namelist() if n.endswith('.class')}; non=[n for n in z.namelist() if not n.endswith('.class')]
        if classes!=expected: raise RuntimeError('candidate contains wrong class roster')
        with zipfile.ZipFile(original) as oz:
            orig={n:hashlib.sha256(oz.read(n)).hexdigest() for n in oz.namelist() if not n.endswith('.class')}
        cand={n:hashlib.sha256(z.read(n)).hexdigest() for n in non}
        if cand!=orig: raise RuntimeError('non-class resources differ from original')
    return len(resources)

def descriptors(cp, cls):
    out,_=run(['javap','-p','-s','-classpath',str(cp),cls])
    fields=[];methods=[];lines=out.splitlines()
    for i in range(len(lines)-1):
        nxt=lines[i+1].strip()
        if nxt.startswith('descriptor:'):
            d=nxt.split(':',1)[1].strip();(methods if d.startswith('(') else fields).append(d)
    return fields,methods

def compile_probes(out,support,candidate):
    probes=[ROOT/x for x in config()['probes']]
    run(['javac','--release','8','-g:none','-implicit:none','-cp',os.pathsep.join([str(support),str(candidate)]),'-d',str(out),*[str(x) for x in probes]])

def java_probe(name,support,probe_classes,gamejar):
    cp=os.pathsep.join([str(support),str(probe_classes),str(gamejar)])
    out,err=run(['java','-Djava.awt.headless=true','-cp',cp,name])
    return out

def main(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path);ap.add_argument('--run-dir',type=Path,required=True);args=ap.parse_args(argv)
    cfg=config(); original=(args.input or ROOT/cfg['input']['path']).resolve(); run_dir=(ROOT/args.run_dir).resolve() if not args.run_dir.is_absolute() else args.run_dir
    if run_dir.exists(): raise RuntimeError('run directory already exists')
    verify_private(cfg,original); run_dir.mkdir(parents=True)
    support=run_dir/'support';game1=run_dir/'game1';game2=run_dir/'game2';probes=run_dir/'probes'
    for p in (support,game1,game2,probes):p.mkdir()
    compile_support(support);compile_game(game1,support);compile_game(game2,support)
    repeat={c:sha(game1/f'{c}.class')==sha(game2/f'{c}.class') for c in GAME}
    if not all(repeat.values()):raise RuntimeError('clean source builds are not byte-repeatable')
    candidate=run_dir/'rebuilt-all-repaired.jar';resource_count=build_candidate(original,game1,candidate)
    if resource_count!=cfg['expected']['non_class_entries']:raise RuntimeError('resource count mismatch')
    desc={};method_total=0
    for c in GAME:
        of,om=descriptors(original,c);cf,cm=descriptors(game1,c);same=(of==cf and om==cm);desc[c]=same;method_total+=len(om)
        if not same:raise RuntimeError(f'descriptor sequence mismatch: {c}')
    if method_total!=cfg['expected']['method_entries']:raise RuntimeError('method total mismatch')
    compile_probes(probes,support,candidate)
    results={}
    for probe_path in cfg['probes']:
        probe=Path(probe_path).stem
        a=java_probe(probe,support,probes,original);b=java_probe(probe,support,probes,candidate)
        if a!=b:raise RuntimeError(f'{probe} original/rebuilt mismatch')
        results[probe]={'sha256':hashlib.sha256(a.encode()).hexdigest(),'lines':len(a.splitlines())}
    report={'schema_version':1,'target_id':cfg['target_id'],'original_sha256':sha(original),'candidate_sha256':sha(candidate),'classes':21,'method_entries':method_total,'resources_byte_exact':resource_count,'repeat_builds':all(repeat.values()),'descriptor_sequences_match':all(desc.values()),'probes':results,'candidate_class_sha256':{c:sha(game1/f'{c}.class') for c in GAME}}
    (run_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return 0
if __name__=='__main__':
    try:sys.exit(main())
    except Exception as e:print(f'integration_recovery: {e}',file=sys.stderr);sys.exit(1)
