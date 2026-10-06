#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

GAME_CLASSES = ["GameMidlet"] + list("abcdefghijklmnopqrst")
TARGET_SHA = "2e03916ea4a5260960e5e57e4dbe0778fb9b577439eac0ce94a685cfecdaaf5f"
TARGET_SIZE = 201816

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(cmd):
    result = subprocess.run([str(x) for x in cmd], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError("command failed: " + " ".join(map(str, cmd)) + "\n" + result.stdout + "\n" + result.stderr)
    return result.stdout

def descriptors(classpath: Path, cls: str):
    out = run(["javap", "-p", "-s", "-classpath", classpath, cls])
    result = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("descriptor:"):
            result.append(line.split(":", 1)[1].strip())
    return result

def javac(output: Path, sources, classpath=None):
    cmd = ["javac", "--release", "8", "-g:none", "-implicit:none", "-sourcepath", "", "-d", output]
    if classpath is not None:
        cmd += ["-cp", classpath]
    cmd += list(sources)
    run(cmd)

def transcode_amr(ffmpeg: str, name: str, data: bytes, work: Path):
    digest = hashlib.sha256(data).hexdigest()
    source = work / (digest + ".amr")
    target = work / (digest + ".wav")
    source.write_bytes(data)
    run([ffmpeg, "-nostdin", "-loglevel", "error", "-y", "-i", source, "-ac", "1", "-ar", "8000", target])
    if not target.is_file() or target.stat().st_size <= 44:
        raise RuntimeError("AMR transcode failed: " + name)
    return digest, target.read_bytes()

def desktop_launcher_source() -> str:
    return """public final class DesktopLauncher {
    private static java.lang.reflect.Field controllerField() {
        for (java.lang.reflect.Field field : GameMidlet.class.getDeclaredFields()) {
            if (java.lang.reflect.Modifier.isStatic(field.getModifiers()) && field.getType().getName().equals("k")) {
                field.setAccessible(true);
                return field;
            }
        }
        throw new IllegalStateException("controller field");
    }
    private static java.lang.reflect.Method method(Class<?> type, String name, Class<?>... params) throws Exception {
        java.lang.reflect.Method method = type.getDeclaredMethod(name, params);
        method.setAccessible(true);
        return method;
    }
    private static void nativeSmoke(GameMidlet midlet) throws Exception {
        Object controller = controllerField().get(null);
        Class<?> type = controller.getClass();
        method(type, "i").invoke(controller);
        java.lang.reflect.Method tick = method(type, "j");
        for (int i = 0; i < 5; ++i) tick.invoke(controller);
        javax.microedition.lcdui.Graphics graphics = new javax.microedition.lcdui.Graphics();
        method(type, "paint", javax.microedition.lcdui.Graphics.class).invoke(controller, graphics);
        midlet.destroyApp(true);
    }
    public static void main(String[] args) throws Exception {
        GameMidlet midlet = new GameMidlet();
        if (args.length > 0 && "--native-smoke".equals(args[0])) {
            nativeSmoke(midlet);
            return;
        }
        midlet.startApp();
    }
}
"""

def build(args):
    original = args.input.resolve()
    source_dir = args.source_dir.resolve()
    runtime_dir = args.runtime_src.resolve()
    output = args.output.resolve()

    if not original.is_file() or original.stat().st_size != TARGET_SIZE or sha(original) != TARGET_SHA:
        raise RuntimeError("wrong original input")

    game_sources = [source_dir / (cls + ".java") for cls in GAME_CLASSES]
    missing = [str(path) for path in game_sources if not path.is_file()]
    if missing:
        raise RuntimeError("missing recovered game sources: " + ", ".join(missing))

    runtime_sources = sorted(runtime_dir.rglob("*.java"))
    if not runtime_sources:
        raise RuntimeError("no desktop runtime sources found")

    ffmpeg = args.ffmpeg or shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to package the game's AMR audio; install ffmpeg or pass --ffmpeg")

    with tempfile.TemporaryDirectory(prefix="dah-desktop-build-") as td:
        work = Path(td)
        runtime_classes = work / "runtime"
        game_classes = work / "game"
        audio_work = work / "audio"
        runtime_classes.mkdir()
        game_classes.mkdir()
        audio_work.mkdir()

        javac(runtime_classes, runtime_sources)
        javac(game_classes, game_sources, runtime_classes)

        roster = sorted(path.stem for path in game_classes.glob("*.class"))
        if roster != sorted(GAME_CLASSES):
            raise RuntimeError("unexpected game class roster: " + repr(roster))

        method_total = 0
        for cls in GAME_CLASSES:
            original_desc = descriptors(original, cls)
            rebuilt_desc = descriptors(game_classes, cls)
            if original_desc != rebuilt_desc:
                raise RuntimeError("descriptor sequence mismatch: " + cls)
            method_total += sum(desc.startswith("(") for desc in original_desc)
        if method_total != 313:
            raise RuntimeError("method count mismatch")

        launcher_source = work / "DesktopLauncher.java"
        launcher_source.write_text(desktop_launcher_source())
        launcher_cp = os.pathsep.join([str(runtime_classes), str(game_classes)])
        javac(game_classes, [launcher_source], launcher_cp)
        if not (game_classes / "DesktopLauncher.class").is_file():
            raise RuntimeError("direct desktop launcher did not compile")

        output.parent.mkdir(parents=True, exist_ok=True)
        manifest = "Manifest-Version: 1.0\nMain-Class: DesktopLauncher\n\n"
        converted_audio = {}
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as outjar:
            outjar.writestr("META-INF/MANIFEST.MF", manifest)
            with zipfile.ZipFile(original) as sourcejar:
                for info in sourcejar.infolist():
                    if info.filename.upper() == "META-INF/MANIFEST.MF" or info.filename.endswith(".class"):
                        continue
                    data = sourcejar.read(info.filename)
                    outjar.writestr(info.filename, data)
                    if info.filename.lower().endswith(".amr"):
                        digest, wav = transcode_amr(ffmpeg, info.filename, data, audio_work)
                        outjar.writestr("META-INF/dah-audio/" + digest + ".wav", wav)
                        converted_audio[info.filename] = {
                            "sha256": digest,
                            "wav_bytes": len(wav),
                            "wav_sha256": hashlib.sha256(wav).hexdigest(),
                        }
            for root in (runtime_classes, game_classes):
                for path in sorted(root.rglob("*.class")):
                    outjar.write(path, path.relative_to(root).as_posix())

        report = {
            "schema_version": 1,
            "input_sha256": TARGET_SHA,
            "desktop_jar": str(output),
            "desktop_jar_sha256": sha(output),
            "game_classes": 21,
            "method_entries": 313,
            "runtime_java_sources": len(runtime_sources),
            "original_class_fallback": False,
            "main_class": "DesktopLauncher",
            "direct_game_entry": True,
            "native_smoke_mode": True,
            "ffmpeg": ffmpeg,
            "amr_converted": len(converted_audio),
            "amr_audio": converted_audio,
        }
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar"))
    parser.add_argument("--source-dir", type=Path, default=Path("src/game"))
    parser.add_argument("--runtime-src", type=Path, default=Path("runtime/desktop"))
    parser.add_argument("--output", type=Path, default=Path("dist/DAH-Mobile-Desktop.jar"))
    parser.add_argument("--report", type=Path)
    parser.add_argument("--ffmpeg")
    args = parser.parse_args()
    try:
        build(args)
    except Exception as exc:
        print("desktop_build:", exc, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
