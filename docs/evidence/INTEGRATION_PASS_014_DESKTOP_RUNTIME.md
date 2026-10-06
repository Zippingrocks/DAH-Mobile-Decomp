# Integration pass 014 — recreated production desktop runtime rerun

This pass recreates the production-style desktop runtime that was lost with the interrupted pass-013 workstation and closes the final pending regression from that checkpoint.

## Runtime boundary

The recreated runtime is authored desktop compatibility code rather than test doubles. It provides:

- a real 176×208 `BufferedImage` framebuffer and AWT/Swing presentation path,
- keyboard-to-mobile-key input translation,
- PNG resource loading through `ImageIO`,
- Java Sound/MIDI plumbing for supported MIDI resources,
- file-backed RMS record stores under a configurable desktop save directory,
- MIDlet/Display/Canvas/Nokia FullCanvas API compatibility needed by the recovered game.

The runtime was compiled separately from the game. Both the original retail game classes and the rebuilt 21-class Java source tree were then executed against the exact same runtime.

## 300-frame production-runtime comparison

The comparison performs deterministic game initialization, follows the established default menu-to-gameplay transition, runs **300 gameplay frames** with the same repeating movement/action input script, paints every frame through the production framebuffer, invokes the real game save helper, and hashes the resulting state/frame/save outputs.

Original and rebuilt output match exactly:

| Observation | Matching SHA-256 |
| --- | --- |
| Normalized game-state graph after 300 gameplay frames | `5e1d535ba2543a001fffe99bfd016575c646af71db09e46f2e4f71e55d25243f` |
| Production 176×208 framebuffer | `da363d6cf71085f0dda2533b8ffdc5b8709872eff001834c7b5ff031dbfd844a` |
| File-backed RMS save aggregation | `77d74229a27aef3940e715373b36cb0c7f9d2487cfe7830c31842be4e894698e` |
| Complete three-line comparison output | `b1a9f4098157251b806f20f9069a77aa61388046e0b4f1144e8c1b62ee3bb034` |

The concrete save file produced on both sides is 90 bytes and byte-identical; SHA-256:

`8394bcc4de35787475f7455746806eeb4fdf6a45c77f96be6d102d596813aa22`

## Interrupted pass-013 checklist

All five post-campaign regression categories that were pending at the interruption are now re-established:

1. 300-frame production desktop comparison — **passed**
2. 500-frame deterministic integration stress run — **passed**
3. RMS save/load round-trip — **passed**
4. startup/menu-to-gameplay probes — **passed**
5. final 21-class clean-build repeatability / 313 descriptors — **passed**

The separate pass-013 campaign checkpoint remains the evidence that all **13 missions** match in direct-load mission state/objective/completion behavior after correcting the `j.n:B` objective-counter binding.

## What this does and does not mean

This establishes that the recovered game can execute substantial real gameplay against desktop services while preserving observed retail behavior, including real raster output and disk persistence.

It is not yet the final desktop release. Audio playback still requires broader AMR support/verification, the interactive window/input path needs human playtesting, mission validation must move beyond direct-load completion matrices into longer end-to-end campaign scripts, and no native Windows executable has been produced yet.

The next milestone is to publish the authored desktop runtime/build path, then extend mission-by-mission runtime validation and package the first playable desktop JAR before native Windows AOT work.
