# Desktop runtime

The project now contains an authored Java desktop compatibility layer for the
Java ME/Nokia APIs used by Destroy All Humans! Mobile. It is separate from the
recovered game source.

## Current services

- Swing/AWT window and keyboard input path
- 176×208 BufferedImage renderer
- PNG loading with ImageIO
- file-backed RMS save storage
- MIDI playback through Java Sound when supported
- MIDlet / Display / Canvas / Nokia FullCanvas compatibility

AMR playback is not yet implemented by the standard Java Sound backend, so the
audio layer is not considered complete.

## Build a desktop JAR

The public repository does not contain recovered game source or original assets.
With the reviewed private source snapshots restored under `src/game/` and the
exact original JAR supplied locally:

```console
python tools/desktop_build.py \
  --input inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar \
  --source-dir src/game \
  --output dist/DAH-Mobile-Desktop.jar \
  --report local/desktop-build.json
```

The builder:

1. verifies the exact original JAR hash,
2. compiles the authored desktop runtime,
3. compiles all 21 recovered game classes from source,
4. compares ordered JVM descriptor sequences against retail,
5. requires all 313 original method entries,
6. copies only the original **non-class** resources,
7. packages the rebuilt game + desktop runtime with `dah.desktop.Launcher` as
   the main class.

It never copies an original game class into the desktop JAR.

Run the result with:

```console
java -jar dist/DAH-Mobile-Desktop.jar
```

The default save directory is `~/.dah-mobile`. Override it with:

```console
java -Ddah.rms.dir=/path/to/saves -jar dist/DAH-Mobile-Desktop.jar
```

## Validation boundary

Integration pass 014 compares original retail classes and rebuilt classes on the
same production runtime for 300 gameplay frames. Normalized game state,
framebuffer output, and the file-backed save file match in that scope.

This does not yet make the desktop runtime a gold release. Interactive human
playtesting, AMR audio support, longer campaign execution and native Windows AOT
remain ahead.
