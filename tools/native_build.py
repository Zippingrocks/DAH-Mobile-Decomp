#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, platform, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def is_windows_host():
    return os.name == "nt"

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
        "-Ddah.rms.dir=" + str(metadata / "smoke-rms"),
        "-cp", jar,
        "DesktopLauncher",
        "--native-smoke",
    ])
    files = {path.name: sha(path) for path in sorted(metadata.glob("*.json"))}
    if not files:
        raise RuntimeError("tracing agent produced no JSON configuration")
    (metadata / "dah-provenance.json").write_text(json.dumps({
        "desktop_jar_sha256": sha(jar), "configuration_sha256": files,
    }, indent=2) + "\n")

def verify_metadata(jar: Path, metadata: Path):
    provenance = metadata / "dah-provenance.json"
    if not provenance.is_file():
        raise RuntimeError("metadata provenance missing; collect fresh tracing metadata")
    data = json.loads(provenance.read_text())
    files = {path.name: sha(path) for path in sorted(metadata.glob("*.json"))
             if path.name != provenance.name}
    if data.get("desktop_jar_sha256") != sha(jar) or not files or files != data.get("configuration_sha256"):
        raise RuntimeError("tracing metadata does not match this desktop JAR or was changed")

def tool_identity(executable, version_args):
    result = subprocess.run([str(executable), *version_args], text=True,
                            capture_output=True, timeout=30)
    if result.returncode:
        raise RuntimeError("cannot identify tool: " + str(executable))
    return {"path": str(executable), "sha256": sha(Path(executable)),
            "version": (result.stdout + result.stderr).strip()}

def dependency_inventory(output: Path):
    dumpbin = shutil.which("dumpbin")
    if not dumpbin:
        return {"recorded": False, "reason": "dumpbin not on PATH; use the x64 Native Tools prompt",
                "clean_machine_tested": False}
    listing = run([dumpbin, "/dependents", output])
    names = sorted({line.strip() for line in listing.splitlines()
                    if line.strip().lower().endswith(".dll") and " " not in line.strip()})
    siblings = {path.name.lower(): path for path in output.parent.glob("*") if path.is_file()}
    return {"recorded": True, "direct_imports": names,
            "adjacent_dlls": [{"name": name, "sha256": sha(siblings[name.lower()])}
                              for name in names if name.lower() in siblings],
            "dumpbin_output": listing, "clean_machine_tested": False}

def native_compile(native_image, jar: Path, metadata: Path, output: Path):
    if output.suffix.lower() == ".exe" and not is_windows_host():
        raise RuntimeError("Windows .exe builds require a Windows host; refusing to rename a host binary")
    output.parent.mkdir(parents=True, exist_ok=True)
    base = output.with_suffix("") if output.suffix.lower() == ".exe" else output
    run([
        native_image,
        "--no-fallback",
        # Liberica NIK's AWT reachability is selected at image-build time.
        # The tracing pass intentionally runs headless, so make the production
        # image's ordinary launcher path explicitly non-headless as documented
        # by BellSoft.  Without this, a PE can pass headless smoke yet fail on
        # first window creation because AWT event classes were omitted.
        "-Djava.awt.headless=false",
        # The D3D pipeline reaches anonymous JNI callbacks that are not present
        # in a headless tracing pass.  The launcher also sets this property at
        # runtime before AWT initializes so the native executable consistently
        # uses the Windows software/GDI path.
        "-Dsun.java2d.d3d=false",
        "-H:+ReportExceptionStackTraces",
        "-H:ConfigurationFileDirectories=" + str(metadata),
        "-H:IncludeResources=.*",
        "-cp", jar,
        "DesktopLauncher",
        "-o", base,
    ])
    expected = Path(str(base) + ".exe") if is_windows_host() else base
    if not expected.is_file():
        raise RuntimeError("native-image completed but output was not found: " + str(expected))
    if output != expected:
        if output.exists():
            output.unlink()
        expected.replace(output)
    return output

def inspect_windows_executable(path: Path):
    with path.open("rb") as stream:
        header = stream.read(64)
        if len(header) != 64 or header[:2] != b"MZ":
            raise RuntimeError("native output is not a Windows PE executable")
        offset = int.from_bytes(header[60:64], "little")
        if offset < 64 or offset > path.stat().st_size - 26:
            raise RuntimeError("invalid Windows PE header offset")
        stream.seek(offset)
        pe = stream.read(26)
    if pe[:4] != b"PE\0\0" or int.from_bytes(pe[4:6], "little") != 0x8664:
        raise RuntimeError("native output is not an x64 Windows PE executable")
    if int.from_bytes(pe[24:26], "little") != 0x20b or int.from_bytes(pe[22:24], "little") & 0x2000:
        raise RuntimeError("native output must be a PE32+ executable, not a DLL")
    return {"format": "PE32+", "machine": "x64"}

def native_smoke(output: Path):
    with tempfile.TemporaryDirectory(prefix="dah-native-smoke-") as td:
        # Native Image executables receive -D arguments as application arguments;
        # they are not parsed by a JVM launcher.  Keep the smoke selector first
        # and let DesktopLauncher establish its headless/RMS properties.
        result = subprocess.run([str(output), "--native-smoke"], cwd=td,
                                text=True, capture_output=True, timeout=120)
    if result.returncode:
        raise RuntimeError("native smoke failed\n" + result.stdout + "\n" + result.stderr)
    return {"passed": True, "stdout": result.stdout, "stderr": result.stderr}

def native_gui_startup_smoke(output: Path, timeout=4.0):
    with tempfile.TemporaryDirectory(prefix="dah-native-gui-") as td:
        process = subprocess.Popen([str(output)], cwd=td, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            returncode = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate(timeout=15)
            if stderr.strip():
                raise RuntimeError("native GUI emitted errors during startup\n" + stdout + "\n" + stderr)
            return {"passed": True, "observed_seconds": timeout,
                    "terminated_after_startup": True,
                    "stdout": stdout, "stderr": stderr}
        stdout, stderr = process.communicate()
    raise RuntimeError(
        "native GUI exited during startup with code " + str(returncode)
        + "\n" + stdout + "\n" + stderr
    )

def native_gui_interaction_smoke(output: Path):
    try:
        with tempfile.TemporaryDirectory(prefix="dah-native-gui-interaction-") as td:
            result = subprocess.run([str(output), "--native-gui-smoke"], cwd=td,
                                    text=True, capture_output=True, timeout=30)
    except subprocess.TimeoutExpired as failure:
        stdout = failure.stdout.decode(errors="replace") if isinstance(failure.stdout, bytes) else (failure.stdout or "")
        stderr = failure.stderr.decode(errors="replace") if isinstance(failure.stderr, bytes) else (failure.stderr or "")
        raise RuntimeError("native GUI interaction smoke timed out\n" + stdout + "\n" + stderr)
    if result.returncode or result.stderr.strip():
        raise RuntimeError(
            "native GUI interaction smoke failed with code " + str(result.returncode)
            + "\n" + result.stdout + "\n" + result.stderr
        )
    return {"passed": True, "language_selected": True,
            "strict_audio_startup": True,
            "stdout": result.stdout, "stderr": result.stderr}

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
            "windows_host": is_windows_host(),
            "native_windows_validated": False,
            "toolchain_present": bool(native_image and Path(native_image).is_file() and java and Path(java).is_file()),
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
        if args.output.suffix.lower() == ".exe" and not is_windows_host():
            raise RuntimeError("Windows .exe builds require a Windows host")
        report["toolchain"] = {
            "native_image": tool_identity(native_image, ["--version"]),
            "java": tool_identity(java, ["-version"]),
        }

        metadata = args.metadata_dir.resolve()
        if not args.skip_agent:
            collect_metadata(java, jar, metadata)
        elif not metadata.is_dir() or not any(metadata.glob("*.json")):
            raise RuntimeError("--skip-agent requires a metadata directory containing JSON configuration")
        verify_metadata(jar, metadata)

        output = native_compile(native_image, jar, metadata, args.output.resolve())
        binary = inspect_windows_executable(output) if is_windows_host() else {"format": "host-native"}
        smoke = native_smoke(output)
        gui_smoke = native_gui_startup_smoke(output)
        gui_interaction_smoke = native_gui_interaction_smoke(output)
        report.update({
            "native_built": True,
            "native_output": str(output),
            "native_sha256": sha(output),
            "native_bytes": output.stat().st_size,
            "binary": binary,
            "native_smoke": smoke,
            "native_gui_startup_smoke": gui_smoke,
            "native_gui_interaction_smoke": gui_interaction_smoke,
            "native_windows_validated": is_windows_host(),
            "dependencies": dependency_inventory(output) if is_windows_host() else None,
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
