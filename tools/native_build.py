#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, platform, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(cmd, cwd=ROOT):
    result = subprocess.run([str(x) for x in cmd], cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError("command failed: " + " ".join(map(str, cmd)) + "\nSTDOUT:\n" + result.stdout + "\nSTDERR:\n" + result.stderr)
    return result.stdout

def inspect_desktop_jar(path: Path):
    with zipfile.ZipFile(path) as jar:
        names = set(jar.namelist())
        manifest = jar.read("META-INF/MANIFEST.MF").decode("utf-8", "replace")
    return {
        "direct_launcher": "DesktopLauncher.class" in names,
        "main_class": "DesktopLauncher" if "Main-Class: DesktopLauncher" in manifest else None,
        "entries": len(names),
    }

def find_native_image(explicit=None):
    if explicit:
        return str(Path(explicit).resolve())
    return shutil.which("native-image") or shutil.which("native-image.cmd")

def java_for_native_image(native_image, explicit=None):
    if explicit:
        return str(Path(explicit).resolve())
    if native_image:
        base = Path(native_image).resolve().parent
        candidate = base / ("java.exe" if os.name == "nt" else "java")
        if candidate.is_file():
            return str(candidate)
    return shutil.which("java")

def build_desktop(args, work: Path):
    if args.desktop_jar:
        return args.desktop_jar.resolve()
    output = work / "DAH-Mobile-Desktop.jar"
    cmd = [
        sys.executable, ROOT / "tools" / "desktop_build.py",
        "--input", args.input,
        "--source-dir", args.source_dir,
        "--output", output,
    ]
    if args.ffmpeg:
        cmd += ["--ffmpeg", args.ffmpeg]
    run(cmd)
    return output

def collect_metadata(java, jar: Path, metadata: Path):
    if metadata.exists() and any(metadata.iterdir()):
        raise RuntimeError("metadata directory is not empty: " + str(metadata))
    metadata.mkdir(parents=True, exist_ok=True)
    run([
        java,
        "-agentlib:native-image-agent=config-output-dir=" + str(metadata),
        "-Djava.awt.headless=true",
        "-cp", jar,
        "DesktopLauncher",
        "--native-smoke",
    ])

def native_compile(native_image, jar: Path, metadata: Path, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    base = output.with_suffix("") if output.suffix.lower() == ".exe" else output
    run([
        native_image,
        "--no-fallback",
        "-H:+ReportExceptionStackTraces",
        "-H:ConfigurationFileDirectories=" + str(metadata),
        "-H:IncludeResources=.*",
        "-cp", jar,
        "DesktopLauncher",
        "-o", base,
    ])
    expected = Path(str(base) + ".exe") if os.name == "nt" else base
    if not expected.is_file():
        raise RuntimeError("native-image completed but output was not found: " + str(expected))
    if output != expected:
        if output.exists():
            output.unlink()
        expected.replace(output)
    return output

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--desktop-jar", type=Path)
    parser.add_argument("--input", type=Path, default=ROOT / "inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar")
    parser.add_argument("--source-dir", type=Path, default=ROOT / "src/game")
    parser.add_argument("--ffmpeg")
    parser.add_argument("--native-image")
    parser.add_argument("--java")
    parser.add_argument("--metadata-dir", type=Path, default=ROOT / "local/native-image-metadata")
    parser.add_argument("--output", type=Path, default=ROOT / "dist/DAH-Mobile-Windows.exe")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--skip-agent", action="store_true")
    args = parser.parse_args(argv)

    native_image = find_native_image(args.native_image)
    java = java_for_native_image(native_image, args.java)

    with tempfile.TemporaryDirectory(prefix="dah-native-") as td:
        jar = build_desktop(args, Path(td))
        info = inspect_desktop_jar(jar)
        if not info["direct_launcher"] or info["main_class"] != "DesktopLauncher":
            raise RuntimeError("desktop JAR is not native-ready: direct DesktopLauncher missing")

        report = {
            "schema_version": 1,
            "platform": platform.platform(),
            "desktop_jar": str(jar),
            "desktop_jar_sha256": sha(jar),
            "direct_launcher": True,
            "native_image": native_image,
            "java": java,
            "metadata_dir": str(args.metadata_dir),
            "prepare_only": args.prepare_only,
            "native_built": False,
        }

        if args.prepare_only:
            text = json.dumps(report, indent=2) + "\n"
            if args.report:
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(text)
            print(text, end="")
            return 0

        if not native_image:
            raise RuntimeError("native-image not found; install GraalVM Native Image or pass --native-image")
        if not java:
            raise RuntimeError("Java executable for the GraalVM installation was not found")

        metadata = args.metadata_dir.resolve()
        if not args.skip_agent:
            collect_metadata(java, jar, metadata)
        elif not metadata.is_dir():
            raise RuntimeError("--skip-agent requires an existing metadata directory")

        output = native_compile(native_image, jar, metadata, args.output.resolve())
        report.update({
            "native_built": True,
            "native_output": str(output),
            "native_sha256": sha(output),
            "native_bytes": output.stat().st_size,
        })
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
        print("native_build:", exc, file=sys.stderr)
        raise SystemExit(1)
