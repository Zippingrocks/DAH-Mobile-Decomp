# Integration pass 015 — reproducible desktop JAR build path

The production-style desktop runtime used by pass 014 is now represented as
tracked authored source in the public tooling repository. No recovered game
source or original asset has been published.

A new `tools/desktop_build.py` command builds the runtime, builds the local
recovered 21-class game tree, checks retail descriptor compatibility, copies only
the exact non-class resources from the user-supplied original JAR, and packages
a runnable desktop JAR.

## Local accepted build

Using the restored private semantic-verification source tree:

- desktop runtime Java sources: **18**
- rebuilt game classes: **21**
- original method entries preserved: **313**
- original game class fallback: **0**
- packaged main class: `dah.desktop.Launcher`
- packaged JAR entries: **166**
- accepted local desktop JAR SHA-256:
  `a483ce5124d9032c97aeb90edaa687f3bee59e2b06bb1454fc2b4092a9da83cc`

The desktop JAR itself is intentionally not committed because it contains
original non-code game resources copied from the user's local retail JAR.

## Runtime implementation

The tracked compatibility layer provides real BufferedImage rendering, Swing
window/input plumbing, ImageIO PNG resources, file-backed RMS storage, and a Java
Sound MIDI path. The game's AMR clips still need a desktop decoder/backend; audio
therefore remains an explicit release blocker.

Public tests compile the runtime independently of any recovered game source and
guard key properties such as file-backed saves, BufferedImage rendering, no
tracked game classes, and no original-class fallback in the builder.

## Relationship to fidelity evidence

Pass 014 established that original retail and rebuilt game classes produce the
same normalized state, 176×208 framebuffer and disk-backed save after a controlled
300-frame gameplay run on this runtime.

This pass makes the corresponding desktop build/runtime path reproducible. It
does not claim complete campaign playtesting, completed AMR audio, native Windows
AOT, or gold status.
