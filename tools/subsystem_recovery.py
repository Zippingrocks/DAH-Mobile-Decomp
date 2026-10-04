#!/usr/bin/env python3
"""Rebuild six local components and run scoped audio/font/navigation comparisons.

No game inputs or recovered game source are downloaded, uploaded, or hidden in
support. Public support is authored test code, NOT missing gameplay. Results
are observations under explicit doubles/adapters, not whole-game accuracy.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import zipfile

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.component_recovery import (
    RecoveryError, require, sha, json_text, pinned_input, source_files,
    write_jar, method_inventory, compare_traces,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = "config/subsystem_recovery.json"
RESOURCES = ("fnt1.font", "fnt1.def", "pics/fnt1.png", "en.bin", "de.bin",
             "fr.bin", "it.bin", "es.bin", "common.bin", "Sound/theme.mid", "Sound/select.amr")
TEST_ALIASES = {"b.class": {"primary": "a", "fallback": "a"},
                "k.class": {"width": "a", "height": "b", "rng": "a"}}


def alias_test_fields(data: bytes, aliases: dict[str, str]) -> bytes:
    """Rename ONLY UTF8 field-name entries in our authored b/k test doubles.

    Original game binaries are NEVER passed to this function. Reference doubles
    need two fields called a with different descriptors (not legal Java source).
    Only name strings are changed; class bodies/values are otherwise untouched.
    """
    require(data[:4] == b"\xca\xfe\xba\xbe" and len(data) >= 10, "Bad test class")
    count = struct.unpack_from(">H", data, 8)[0]
    out = bytearray(data[:10]); pos = 10; index = 1; seen = set()
    def take(n):
        nonlocal pos
        require(pos+n <= len(data), "Truncated test class")
        result = data[pos:pos+n]; pos += n; return result
    while index < count:
        tag = take(1)[0]; out.append(tag)
        if tag == 1:
            n = int.from_bytes(take(2), "big"); raw = take(n)
            name = raw.decode("utf-8")
            if name in aliases:
                require(name not in seen, "Ambiguous test-name constant")
                seen.add(name); raw = aliases[name].encode("utf-8")
            out.extend(struct.pack(">H", len(raw))); out.extend(raw)
        else:
            widths = {3:4, 4:4, 5:8, 6:8, 7:2, 8:2, 9:4, 10:4, 11:4, 12:4, 15:3, 16:2, 18:4}
            require(tag in widths, "Unsupported test constant")
            out.extend(take(widths[tag]))
            if tag in (5,6): index += 1
        index += 1
    require(seen == set(aliases), "Test alias not found")
    out.extend(data[pos:]); return bytes(out)


def normalized_inventory(text: str, owner: str, renames: list[dict], candidate: bool) -> list:
    rows = method_inventory(text)
    if not candidate: return rows
    inverse = {(r["source_name"], r["descriptor"]): r["original"]
               for r in renames if r["owner"] == owner}
    return [(inverse.get((name, desc), name), desc) for name, desc in rows]


def resource_fixtures(root: Path, data: dict[str, bytes]) -> None:
    """Use allowlisted original resources locally plus independently authored corruptions."""
    require(set(data) == set(RESOURCES), "Resource allowlist mismatch")
    for name, raw in data.items():
        path = root/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    def save(name, raw):
        path=root/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(raw)
    font, text = data["fnt1.font"], data["en.bin"]
    require(len(font)==356, "Unexpected font fixture length")
    for i in range(357): save(f"font-cuts/{i}", font[:i])
    for i in range(65): save(f"text-cuts/{i}", text[:i])
    save("font-alias", bytes([2,0,2,12,0,3,26,0])+struct.pack(">hh",0,10)+bytes([5,6]))
    save("font-negative",bytes([128])); save("text-negative",b"TXT\x01"+struct.pack(">hh",-1,2))
    save("chars-empty",b""); save("chars-255",bytes([255])); save("chars-long",b"A"*253)
    for name,raw in {"all.amr":b"amr", "all.wav":b"wave", "all.mid":b"midi", "wave.wav":b"wave",
                     "wave.mid":b"midi", "midi.mid":b"midi", "empty.mid":b""}.items(): save("audio/"+name,raw)


def run(root: Path, run_dir: Path) -> dict:
    target=json.loads((root/"config/target.json").read_text())
    config=json.loads((root/CONFIG).read_text())
    require(config["target_id"]==target["id"], "Wrong component target")
    original=root/"inputs/original"/target["filename"]
    pinned_input(original,target); sources=source_files(root,config)
    require({p.stem for p in sources}=={"e","s","t","g","l","q"}, "Unexpected recovery scope")
    support_paths=[root/name for name in config["support_sources"]]
    for path in support_paths:
        require(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()) and path.is_file(), "Unsafe/missing support")
    for tool in ("java","javac","javap"): require(shutil.which(tool) is not None, f"JDK {tool} required")
    require(not run_dir.exists(), "Choose a fresh run directory")
    for sub in ("logs","support","classes","empty","resources"):
        (run_dir/sub).mkdir(parents=True,exist_ok=True)
    env=os.environ.copy()
    for key in ("CLASSPATH","JAVA_TOOL_OPTIONS","_JAVA_OPTIONS","JDK_JAVA_OPTIONS"):env.pop(key,None)
    commands=[]
    def command(args, label, timeout=45):
        commands.append(args)
        p=subprocess.run(args,capture_output=True,text=True,env=env,timeout=timeout)
        for suffix,content in (("stdout",p.stdout),("stderr",p.stderr)):
            (run_dir/"logs"/(label+"."+suffix)).write_text(content,encoding="utf-8")
        (run_dir/"commands.json").write_text(json_text(commands),encoding="utf-8")
        require(p.returncode==0, f"{label} failed; inspect logs")
        return p.stdout
    command(["java","-version"],"java-version")
    jdk=command(["javac","-version"],"javac-version").strip()
    command(["javac","--release","8","-g:none","-d",str(run_dir/"support"),*map(str,support_paths)],"compile-test-support")
    expected={p.stem+".class" for p in sources}
    require(not any((run_dir/"support"/name).exists() for name in expected),"Support cannot contain recovered classes")
    command(["javac","--release","8","-g:none","-implicit:none","-sourcepath",str(run_dir/"empty"),
             "-classpath",str(run_dir/"support"),"-d",str(run_dir/"classes"),*map(str,sources)],"compile-recovered-source")
    actual={p.relative_to(run_dir/"classes").as_posix() for p in (run_dir/"classes").rglob("*") if p.is_file()}
    require(actual==expected,"Unexpected compiler output")
    write_jar(run_dir/"rebuilt-components.jar",{n:(run_dir/"classes"/n).read_bytes() for n in expected})
    with zipfile.ZipFile(original) as z:
        originals={n:z.read(n) for n in expected}; assets={n:z.read(n) for n in RESOURCES}
    for c in config["components"]:
        require(sha(originals[c["original"]+".class"])==c["original_class_sha256"],"Original class mismatch")
    require({n:sha(b) for n,b in assets.items()}==config["resource_hashes"],"Original resource mismatch")
    write_jar(run_dir/"reference-only.jar",originals)
    resource_fixtures(run_dir/"resources",assets)
    shutil.copytree(run_dir/"support",run_dir/"support-reference")
    for name,aliases in TEST_ALIASES.items():
        path=run_dir/"support-reference"/name; path.write_bytes(alias_test_fields(path.read_bytes(),aliases))
    inventory={}
    for c in config["components"]:
        name=c["original"]; rows=[]
        for side,artifact in ((False,"reference-only.jar"),(True,"rebuilt-components.jar")):
            text=command(["javap","-p","-s","-classpath",str(run_dir/artifact),name],f"members-{name}-{side}")
            rows.append(normalized_inventory(text,name,config["method_renames"],side))
        require(rows[0]==rows[1] and len(rows[0])==c["method_entries"],f"Incomplete method inventory for {name}")
        inventory[name]=len(rows[0])
    groups={}
    for probe,mode in (("SubsystemProbe","audio"),("SubsystemProbe","font"),("NavigationProbe","navigation")):
        logs=[]
        for side in (False,True):
            support="support" if side else "support-reference"
            artifact="rebuilt-components.jar" if side else "reference-only.jar"
            cp=os.pathsep.join(str(run_dir/p) for p in (support,"resources",artifact))
            args=["java","-Xmx256m","-Djava.awt.headless=true","-cp",cp,probe,str(side).lower()]
            if probe=="SubsystemProbe":args.append(mode)
            logs.append(command(args,f"probe-{mode}-{side}"))
        for key,value in compare_traces(*logs).items():
            require(key not in groups,"Repeated observation group");groups[key]=value
    result={"schema_version":1,"scope":"six-class component artifact; audio/font/navigation observations under test support, not full game fidelity",
            "target_id":target["id"],"original_sha256":target["sha256"],"javac":jdk,
            "candidate_sha256":sha((run_dir/"rebuilt-components.jar").read_bytes()),
            "source_hashes":{p.name:sha(p.read_bytes()) for p in sources},
            "support_hashes":{p.relative_to(root).as_posix():sha(p.read_bytes()) for p in support_paths},
            "runner_sha256":sha((root/"tools/subsystem_recovery.py").read_bytes()),
            "method_entries":inventory,"groups":groups,"calls_per_side":sum(v["calls_per_side"] for v in groups.values())}
    (run_dir/"observations.json").write_text(json_text(result),encoding="utf-8")
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--run-dir",type=Path,required=True);args=p.parse_args(argv)
    try:
        report=run(ROOT,args.run_dir.resolve());print(f"Scoped probes matched: {report['calls_per_side']} calls per side. NOT a whole-game pass.");return 0
    except (RecoveryError,OSError,ValueError,KeyError,zipfile.BadZipFile,subprocess.SubprocessError) as ex:
        print(f"ERROR: {ex}",file=sys.stderr);return 1

if __name__=="__main__":raise SystemExit(main())
