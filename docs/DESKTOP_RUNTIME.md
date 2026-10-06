# Desktop runtime

The project contains an authored Java desktop compatibility layer for the
Java ME/Nokia APIs used by Destroy All Humans! Mobile. It is separate from the
recovered game source.

## Current services

- Swing/AWT window and keyboard input path
- 176×208 BufferedImage renderer
- PNG loading with ImageIO
- file-backed RMS save storage
- MIDI playback through Java Sound
- AMR sound-effect playback through build-time FFmpeg conversion to embedded WAV companions
- MIDlet / Display / Canvas / Nokia FullCanvas compatibility

The retail game contains four AMR effects and three MIDI tracks. The desktop
builder preserves every original non-class resource and additionally converts each
AMR effect to a hash-addressed WAV resource under `META-INF/dah-audio/`. At
runtime the media layer hashes the AMR bytes supplied by the recovered game,
finds the corresponding WAV companion, and plays it through Java Sound. The
recovered game code does not need to know that conversion occurred.

FFmpeg is an external build dependency and is **not bundled** by this repository.

## Build a desktop JAR

The public repository does not contain recovered game source or original assets.
With the reviewed private source snapshots restored under `src/game/`, the
exact original JAR supplied locally, and FFmpeg installed:

```console
python tools/desktop_build.py \
  --input inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar \
  --source-dir src/game \
  --output dist/DAH-Mobile-Desktop.jar \
  --report local/desktop-build.json
```

Use `--ffmpeg /path/to/ffmpeg` when FFmpeg is not on PATH.

The builder:

1. verifies the exact original JAR hash,
2. requires FFmpeg for the retail AMR effects,
3. compiles the authored desktop runtime,
4. compiles all 21 recovered game classes from source,
5. compares ordered JVM descriptor sequences against retail,
6. requires all 313 original method entries,
7. copies only the original **non-class** resources,
8. preserves each original AMR and embeds a converted WAV companion keyed by its SHA-256,
9. packages the rebuilt game + desktop runtime with `dah.desktop.Launcher` as
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

Integration pass 016 validates all four actual retail AMR resources through the
automatic build-time conversion and runtime hash-resolution path. The converted
resources are playable Java Sound WAV files; this removes manual audio conversion
from the human checklist.

This still does not make the desktop runtime a gold release. Interactive human
playtesting, longer end-to-end campaign execution and native Windows AOT remain
ahead.
