#!/usr/bin/env python3
"""Build seventeen source components and compare weapon/saucer/lifecycle behavior.

Original JAR appears only in a reference JVM. Test support is not recovered AI.
"""
from __future__ import annotations
import argparse
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.component_recovery import (RecoveryError, require, sha, json_text,
    pinned_input, source_files, write_jar, compare_traces)
from tools.subsystem_recovery import alias_test_fields, normalized_inventory

ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'config/weapon_recovery.json'
CLASSES = {'a','e','g','h','i','l','m','o','n','d','r','q','s','t','c','f','GameMidlet'}
MODES = ('weapon-selection','weapon-aiming','weapon-firing','weapon-update','weapon-drawing',
         'saucer-motion','saucer-reticle','saucer-targeting','saucer-update-draw','midlet-lifecycle')


def alias_lines(config: dict) -> str:
    lines=[]
    for kind in ('field','method'):
        seen=set()
        for r in config[kind+'_renames']:
            key=(r['owner'],r['original'],r['descriptor'])
            require(key not in seen,'Duplicate alias');seen.add(key)
            require(all(isinstance(v,str) and not any(c in v for c in '\t\r\n') for v in (*key,r['source_name'])),'Bad alias')
            lines.append('\t'.join((kind,*key,r['source_name'])))
    return '\n'.join(lines)+'\n'



def outcome_counts(text: str, expected_calls: int) -> dict:
    """Parse target-only direct-call observations, not bytecode or branch coverage."""
    lines=text.splitlines();require(bool(lines),'Missing method outcomes')
    header=re.fullmatch(r'successful=(\d+) expected-or-recorded-exceptions=(\d+) fixture_calls=(\d+)',lines[0])
    require(header is not None,'Malformed outcome header')
    result={}
    for line in lines[1:]:
        parts=line.split('\t');require(len(parts)==4 and parts[0]=='METHOD','Bad method outcome')
        key=parts[1];require(key not in result and re.fullmatch(r'(?:c|f|GameMidlet)\.[^\s]+',key) is not None,'Bad/duplicate target method')
        require(parts[2].isdecimal() and parts[3].isdecimal(),'Bad outcome count')
        passed,failed=int(parts[2]),int(parts[3]);require(passed+failed>0,'Empty outcome')
        result[key]={'returned':passed,'threw':failed}
    require(sum(v['returned']+v['threw'] for v in result.values())==expected_calls,'Outcome total differs from trace')
    good,bad,fixture=map(int,header.groups())
    require(good+bad==fixture+expected_calls,'Fixture count mismatch')
    return {'fixture_calls_excluded':fixture,'methods':result}


def split_outputs(classes: Path, support: Path, expected: set[str]) -> dict[str,bytes]:
    """Compile cyclic signatures together, then strictly separate game and test outputs."""
    game={}
    for p in sorted(classes.rglob('*.class')):
        name=p.relative_to(classes).as_posix()
        if name in expected:game[name]=p.read_bytes()
        else:
            target=support/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
    require(set(game)==expected,'Missing/extra recovered class output')
    require(not any((support/n).exists() for n in expected),'Support shadows game class')
    return game


def run(root: Path, output: Path) -> dict:
    config=json.loads((root/CONFIG).read_text(encoding='utf-8'))
    target=json.loads((root/'config/target.json').read_text(encoding='utf-8'))
    require(config['target_id']==target['id'],'Target mismatch')
    original=root/'inputs/original'/target['filename'];pinned_input(original,target)
    sources=source_files(root,config)
    require({p.stem for p in sources}==CLASSES,'Unexpected recovery selection')
    support=[]
    for name in config['support_sources']:
        p=root/name
        require(p.resolve().is_relative_to(root.resolve()) and not p.is_symlink() and p.is_file(),'Unsafe/missing support source')
        support.append(p)
    for tool in ('java','javac','javap'):require(shutil.which(tool) is not None,'JDK required')
    require(not output.exists(),'Use a fresh run directory')
    for sub in ('logs','compiled','support','empty','resources'):(output/sub).mkdir(parents=True,exist_ok=True)
    commands=[];env=os.environ.copy()
    for key in ('CLASSPATH','JAVA_TOOL_OPTIONS','_JAVA_OPTIONS','JDK_JAVA_OPTIONS'):env.pop(key,None)
    def command(args,label,timeout=90):
        commands.append(args)
        p=subprocess.run(args,capture_output=True,text=True,timeout=timeout,env=env)
        for suffix,text in (('stdout',p.stdout),('stderr',p.stderr)):
            (output/'logs'/(label+'.'+suffix)).write_text(text,encoding='utf-8')
        (output/'commands.json').write_text(json_text(commands),encoding='utf-8')
        require(p.returncode==0,label+' failed; inspect logs');return p.stdout
    command(['java','-version'],'java-version');jdk=command(['javac','-version'],'javac-version').strip()
    # The recovered c/f/GameMidlet and authored world/actor/controller signatures are cyclic.
    # Classpath and sourcepath are empty: no original binary is a compiler dependency.
    command(['javac','--release','8','-g:none','-implicit:none','-sourcepath',str(output/'empty'),
        '-classpath',str(output/'empty'),'-d',str(output/'compiled'),*map(str,sources),*map(str,support)],'compile')
    expected={n+'.class' for n in CLASSES}
    actual={p.relative_to(output/'compiled').as_posix() for p in (output/'compiled').rglob('*.class')}
    require(actual==expected|set(config['support_classes']),'Unexpected generated game or test-support class')
    game=split_outputs(output/'compiled',output/'support',expected)
    write_jar(output/'rebuilt-components.jar',game)
    with zipfile.ZipFile(original) as z:
        originals={n:z.read(n) for n in expected}
        for name,digest in config['resource_hashes'].items():
            p=output/'resources'/name
            require(p.resolve().is_relative_to((output/'resources').resolve()),'Unsafe resource path')
            data=z.read(name);require(sha(data)==digest,'Changed resource')
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    for r in config['components']:require(sha(originals[r['original']+'.class'])==r['original_class_sha256'],'Changed original class')
    write_jar(output/'reference-only.jar',originals)
    shutil.copytree(output/'support',output/'reference-support')
    for name,aliases in config['test_aliases'].items():
        require(name in {'b.class','j.class','k.class'},'Refusing non-test alias target')
        p=output/'reference-support'/name;p.write_bytes(alias_test_fields(p.read_bytes(),aliases))
    (output/'resources'/'aliases.tsv').write_text(alias_lines(config),encoding='utf-8')
    inventory={}
    for r in config['components']:
        name=r['original'];counts=[]
        for candidate,jar in ((False,'reference-only.jar'),(True,'rebuilt-components.jar')):
            text=command(['javap','-p','-s','-classpath',str(output/jar),name],f'signatures-{name}-{candidate}')
            counts.append(normalized_inventory(text,name,config['method_renames'],candidate))
        require(counts[0]==counts[1] and len(counts[0])==r['method_entries'],'Method inventory mismatch: '+name)
        inventory[name]=len(counts[0])
    observations={};coverage={}
    for mode in MODES:
        traces=[]
        for candidate in (False,True):
            paths=('support','resources','rebuilt-components.jar') if candidate else ('reference-support','resources','reference-only.jar')
            cp=os.pathsep.join(str(output/p) for p in paths)
            traces.append(command(['java','-Xmx256m','-Djava.awt.headless=true','-cp',cp,'WeaponProbe',str(candidate).lower(),mode],mode+'-'+str(candidate)))
        groups=compare_traces(*traces)
        counts=[outcome_counts((output/'logs'/(mode+'-'+str(side)+'.stderr')).read_text(encoding='utf-8'),groups[mode]['calls_per_side']) for side in (False,True)]
        require(counts[0]==counts[1],'Method outcome counts differ');coverage[mode]=counts[0]
        require(not(set(groups)&set(observations)),'Duplicate observation group');observations.update(groups)
    report={'schema_version':1,'scope':'seventeen-class component build; weapon/saucer/lifecycle integration with base-actor/world/controller/platform test support, not whole game',
        'target_id':target['id'],'original_sha256':target['sha256'],'javac':jdk,
        'candidate_sha256':sha((output/'rebuilt-components.jar').read_bytes()),'method_entries':inventory,
        'source_hashes':{p.name:sha(p.read_bytes()) for p in sources},
        'support_hashes':{p.relative_to(root).as_posix():sha(p.read_bytes()) for p in support},
        'tool_hashes':{n:sha((root/n).read_bytes()) for n in (CONFIG,'tools/weapon_recovery.py','tools/component_recovery.py','tools/subsystem_recovery.py')},
        'groups':observations,'direct_call_outcomes':coverage,'call_scope':'explicit calls to newly recovered c/f/GameMidlet only; fixture calls and nested calls excluded; not branch coverage','calls_per_side':sum(g['calls_per_side'] for g in observations.values())}
    (output/'observations.json').write_text(json_text(report),encoding='utf-8');return report


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-dir',type=Path,required=True);args=p.parse_args(argv)
    try:
        result=run(ROOT,args.run_dir.resolve());print(f"Matched {result['calls_per_side']} component calls per side; not a full-game test.");return 0
    except (RecoveryError,OSError,ValueError,KeyError,zipfile.BadZipFile,subprocess.SubprocessError) as exc:
        print('ERROR: '+str(exc),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
