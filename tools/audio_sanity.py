#!/usr/bin/env python3
from __future__ import annotations
import argparse, io, json, math, struct, sys, wave, zipfile
from pathlib import Path

EXPECTED_AMR_HASHES = {
    "5fdad79f7f4001deab559b240a808e134578bb80640ca5876dea3b5f575f0690",
    "94bb3ab8ae3f01c4f6fc2a780630082b25b8ba68ca0a5edf9e05f8ebb0b1be18",
    "ab2e745f7c47589645ffecac648369b06bd165398fac2d18d319beebc5554273",
    "aa8f4a0c0e0504314da5229a2e3d2b6d784830b2f2f6a166b08f375d72224700",
}

def metrics(data: bytes):
    with wave.open(io.BytesIO(data), "rb") as w:
        channels = w.getnchannels()
        rate = w.getframerate()
        width = w.getsampwidth()
        frames = w.getnframes()
        raw = w.readframes(frames)
    if width != 2:
        raise RuntimeError("expected 16-bit PCM WAV")
    samples = struct.unpack("<%dh" % (len(raw)//2), raw) if raw else ()
    peak = max((abs(v) for v in samples), default=0)
    rms = math.sqrt(sum(v*v for v in samples)/len(samples)) if samples else 0.0
    clipped = sum(1 for v in samples if abs(v) >= 32767)
    return {
        "channels": channels,
        "sample_rate": rate,
        "sample_width_bytes": width,
        "frames": frames,
        "duration_seconds": frames / float(rate) if rate else 0.0,
        "peak": peak,
        "rms": rms,
        "clipped_samples": clipped,
    }

def validate(row):
    if row["channels"] != 1:
        raise RuntimeError("converted effect is not mono")
    if row["sample_rate"] != 8000:
        raise RuntimeError("converted effect is not 8 kHz")
    if row["sample_width_bytes"] != 2:
        raise RuntimeError("converted effect is not 16-bit PCM")
    if not (0.03 <= row["duration_seconds"] <= 2.0):
        raise RuntimeError("converted effect duration outside expected sanity range")
    if row["peak"] < 500 or row["rms"] < 100:
        raise RuntimeError("converted effect is effectively silent")
    if row["clipped_samples"] != 0:
        raise RuntimeError("converted effect contains clipped samples")

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate",type=Path,required=True)
    ap.add_argument("--report",type=Path)
    args=ap.parse_args(argv)
    rows=[]
    with zipfile.ZipFile(args.candidate) as jar:
        names=set(jar.namelist())
        found=set()
        for digest in sorted(EXPECTED_AMR_HASHES):
            name="META-INF/dah-audio/"+digest+".wav"
            if name not in names:
                raise RuntimeError("missing converted companion: "+name)
            row={"amr_sha256":digest,**metrics(jar.read(name))}
            validate(row);rows.append(row);found.add(digest)
        extras=[n for n in names if n.startswith("META-INF/dah-audio/") and n.endswith(".wav") and Path(n).stem not in EXPECTED_AMR_HASHES]
        if extras:
            raise RuntimeError("unexpected converted audio companions: "+repr(sorted(extras)))
    report={"schema_version":1,"candidate":str(args.candidate),"effects":len(rows),"all_sane":True,"rows":rows}
    text=json.dumps(report,indent=2)+"\n"
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(text)
    print(text,end="")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:print("audio_sanity:",exc,file=sys.stderr);raise SystemExit(1)
