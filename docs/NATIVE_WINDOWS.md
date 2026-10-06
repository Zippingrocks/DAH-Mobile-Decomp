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

```console
python tools/native_build.py \
  --input inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar \
  --source-dir src/game \
  --output dist/DAH-Mobile-Windows.exe \
  --report local/native-build.json
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
