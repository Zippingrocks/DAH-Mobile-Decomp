# Native Windows AOT preparation

The desktop port now has a native-image-oriented build path in addition to the
regular runnable desktop JAR.

## What is automated

`tools/desktop_build.py` generates a default-package `DesktopLauncher` that
directly constructs `GameMidlet` and calls `startApp()`. Normal startup
therefore does **not** rely on reflective discovery of the game entry point.

The generated launcher also supports:

```console
java -cp dist/DAH-Mobile-Desktop.jar DesktopLauncher --native-smoke
```

That mode initializes the recovered game, advances controller ticks, paints a
frame and exits. It exists so GraalVM's tracing agent can collect reachability
metadata without human interaction.

`tools/native_build.py` automates the rest:

1. build (or accept) the desktop JAR,
2. verify the direct launcher is present,
3. locate the GraalVM `native-image` tool,
4. run `native-image-agent` through `--native-smoke`,
5. include all packaged resources,
6. invoke `native-image --no-fallback`,
7. hash and report the resulting native executable.

Example on a suitable Windows host:

```powershell
python tools/native_build.py --input inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar --source-dir src/game/verification-028 --metadata-dir local/native-windows-001 --output dist/DAH-Mobile-Windows.exe --report local/native-windows-001-report.json
```

Use `--prepare-only` to inspect the desktop JAR and toolchain without attempting
native compilation. Existing reachability metadata can be reused with
`--skip-agent`.

## Windows prerequisites

GraalVM Native Image's current Windows documentation requires a Windows GraalVM
installation plus Microsoft Visual C++/Visual Studio Build Tools and a Windows
SDK. See:

- https://www.graalvm.org/latest/getting-started/windows/
- https://www.graalvm.org/latest/reference-manual/native-image/

The project does not redistribute GraalVM, Visual Studio Build Tools, the Windows
SDK, or FFmpeg.

## Validation boundary

The generated direct launcher has been compiled against the actual packaged game
and its `--native-smoke` path has run successfully in headless mode. The current
worker does not have `native-image` installed and is not a Windows build host,
so a Windows native executable has **not** yet been produced or claimed.

The remaining native step is environmental compilation/validation, not recovery
of another game subsystem.

## Build acceptance checks (2026-10-07)

The builder refuses a Windows `.exe` output on a non-Windows host. A Windows
build must have an x64 PE32+ header and must successfully execute
`--native-smoke` in a fresh temporary working directory before the success
report is written. Smoke checks cover startup, five ticks and painting; they
do not establish interactive campaign, controls, audio or clean-machine DLL
packaging. Native Image's AWT dependencies must still be inventoried on the
Windows build host; an executable alone does not prove standalone packaging.

`--prepare-only` checks the desktop JAR and records `windows_host` and
`toolchain_present`; its successful exit does not mean a compiler is installed.
`--skip-agent` requires JSON configuration in the metadata directory.

The native executable is launched as `DAH-Mobile-Windows.exe --native-smoke`.
Unlike the `java` launcher, a Native Image executable does not interpret `-D`
arguments as JVM system properties. `DesktopLauncher` therefore establishes
headless mode and a temporary working-directory RMS root before it constructs
the game during native smoke. This ordering is part of the acceptance check;
putting `-D` arguments before `--native-smoke` would run the ordinary launcher
path instead of the intended smoke path.

Use the verified checkpoint-028 source root explicitly; older `src/game`
snapshots are incomplete on a restored workstation. A Windows checkout still
needs checkpoint 028 plus GraalVM Native Image, MSVC/Windows SDK, a release-8
Java compiler and FFmpeg before it can produce the candidate. The next concrete
step is that private build, followed by native smoke, DLL inventory and
interactive review. No build report may claim an executable from preflight
alone.

## Private Windows handoff

Restore checkpoint 028 into a checkout of the current tooling repository. Run
the command above from the repository root in an x64 Native Tools prompt, with
the installed GraalVM `bin` directory and FFmpeg on PATH. Choose a new metadata
directory for each fresh trace; do not overwrite a previous build report.

The report records executable hashes and installed Java/Native Image version
output. It records the hash of the Native Image launcher; that hash alone does
not fingerprint the entire GraalVM distribution. Retain the installer/archive
hash and its provenance separately before accepting a toolchain as pinned.
The project neither downloads nor redistributes these build dependencies.

Tracing configurations are bound to the exact desktop JAR and all generated
JSON configuration hashes in `dah-provenance.json`. Reuse with `--skip-agent`
rejects a different JAR, modified configuration, extra JSON files, or missing
provenance. Previously collected unbound metadata must be collected again.

On Windows, `dumpbin /dependents` records direct DLL imports and hashes matching
DLLs beside the executable. If dumpbin is absent, the report explicitly marks
the inventory unrecorded. This inventory does not resolve system DLLs,
transitive imports or libraries loaded dynamically (including AWT/JNI). Keep
all generated companion files together, check the distribution on a clean
Windows machine without Java or GraalVM, and exercise rendering, saving and
audio. `clean_machine_tested` stays false until separate evidence establishes
that test; this builder does not mark packaging or the game gold.
