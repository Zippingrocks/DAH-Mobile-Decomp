# Integration pass 018 — native AOT build automation

This pass removes manual native-image command/configuration work from the eventual
Windows AOT build.

## Direct entry point

The desktop builder now generates `DesktopLauncher` in the default package.
Its normal path directly executes:

`new GameMidlet().startApp()`

This avoids reflective discovery of the game entry point and gives static native
analysis a direct root into the recovered game.

A separate `--native-smoke` path intentionally uses reflection to initialize the
controller, run five ticks and paint a frame. That path is for GraalVM's tracing
agent so required reflection metadata can be collected automatically.

## Native build wrapper

The new `tools/native_build.py` performs:

- desktop JAR build/inspection,
- toolchain discovery,
- Graal tracing-agent metadata collection,
- all-resource inclusion,
- `native-image --no-fallback` invocation,
- output existence/hash/size reporting.

The wrapper can also operate in `--prepare-only` mode without a native compiler.

## Actual packaged-game validation

The generated direct launcher was compiled against the accepted desktop game
package, added as the JAR main class, and executed with `--native-smoke`.

Result: **successful clean exit** after real game initialization/ticks/paint.

The native-ready local validation JAR SHA-256 is:

`97bf61e562d1802a700e3fa1fe52121b5465cea67ae125193622f7e42e5e52a3`

It also retained the four automatically converted AMR WAV companions from pass
016.

## Native executable status

The current worker does not provide GraalVM's `native-image` binary and is not a
Windows native build environment. Therefore this pass **does not claim a Windows
EXE**.

The build procedure is automated; the remaining blocker is executing it on a
Windows host with the GraalVM/MSVC/Windows-SDK prerequisites and then running the
resulting executable through the same regression/playtest gates.
