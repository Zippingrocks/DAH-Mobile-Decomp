# Integration pass 029 — Windows native input and audio startup

Date: 2026-10-13

## Scope

This pass uses the exact English v1.2.0 retail JAR (201,816 bytes; SHA-256
`2e03916ea4a5260960e5e57e4dbe0778fb9b577439eac0ce94a685cfecdaaf5f`),
the independently reconstructed 21-class private source tree, the authored
desktop runtime, Liberica NIK 25.0.4.1 and MSVC x64 on Windows.

No recovered source, original binary, executable or third-party toolchain is
committed. The local build/report directories and distribution binary remain
ignored.

## Failures found by hands-on testing

The first ordinary native launch exposed an AWT reachability failure that the
headless smoke did not exercise. After enabling non-headless AWT at image-build
time, a second launch exposed missing Direct3D JNI callbacks. Selecting the
language then exposed a third native-only failure: Java Sound attempted to read
`java.home`, which Native Image leaves unset, and the uncaught `Error` killed the
game thread.

The desktop control layer also mapped Enter to mobile center key 5 even though
the language and menu SELECT action is mobile left soft key -6. It had no mouse
listener.

## Repairs

- Enter maps to left soft/SELECT; Space remains center/action.
- Mouse clicks map the lower-left and lower-right regions to the two visible
  soft keys and the remaining game area to center/action; mouse press restores
  keyboard focus.
- The native image explicitly enables non-headless AWT and disables the unstable
  Direct3D path in favor of Windows software/GDI rendering.
- The launcher supplies a self-contained `java.home` fallback before Java Sound
  initializes.
- Audio failures are crash-safe in normal play and fatal in strict native smoke,
  so acceptance cannot silently pass with a broken MIDI/sample backend.
- Native acceptance now includes normal-window stderr/liveness and a second GUI
  path that selects the language, initializes MIDI in strict mode and observes
  the game thread.

## Accepted outputs and tests

- Desktop JAR SHA-256:
  `0b25b93896f12974b16f3bf7bf9bb11200966dd41bb5f42ec2a84777770ff098`.
- Game classes: 21; ordered method entries: 313; original-class fallback: false.
- Windows executable: x64 PE32+, 280,420,352 bytes, SHA-256
  `eada1c8280fb68f8888b245af58b6a85a831d66e89255447ebe428efbcfccd64`.
- Native headless smoke: passed.
- Ordinary native GUI startup: four seconds, empty stdout/stderr, passed.
- Native GUI interaction: language selected, strict MIDI startup passed, game
  thread remained alive, empty stdout/stderr.
- Interactive final run: title, save and main-menu screens rendered; SELECT
  interactions advanced two menu levels; captured stderr remained empty.
- Public tests: 244 passed, zero skipped.
- Differential/automated gate: 13 missions, 3,900 stress frames, 7,800 fuzz
  frames, 65,000 soak frames, mission 1→13 RMS progression and four audio
  effects all passed on the exact desktop payload compiled into the EXE.

Machine-readable evidence is in
[integration-pass-029-windows-native-input.json](integration-pass-029-windows-native-input.json).

## Claim boundary

This establishes a real Windows native developer-host executable and closes the
specific Enter, mouse, AWT, Direct3D and post-language MIDI startup defects. It
does not establish gold status. Still required: a human full-campaign playthrough
for control feel and unscripted cases; subjective listening for music/effect
mix, loudness and timing; subjective presentation/scaling review; and a clean
Windows machine test without the development toolchain. Direct imports include
the Visual C++ runtime DLLs and no adjacent runtime DLLs are currently packaged.
