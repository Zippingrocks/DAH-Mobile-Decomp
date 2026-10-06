# Automated validation gate

`tools/full_validation.py` is the project's "do everything a machine can do"
entry point.

Given the exact retail JAR plus the reviewed local recovered source tree, it can
automatically:

1. run the complete public unit/tooling suite,
2. build the desktop candidate,
3. verify the four original AMR resources and four converted WAV companions,
4. run the direct launcher's headless native-smoke path,
5. compare all 13 mission objective/completion rows against retail,
6. run the mission 1→13 save/progression chain with byte-identical file-backed RMS,
7. perform the GraalVM/native-image preflight,
8. emit one machine-readable report.

Example:

```console
python tools/full_validation.py \
  --input inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar \
  --source-dir src/game \
  --report local/full-validation.json
```

An already-built desktop candidate can be supplied with `--candidate`.

## Why it does not say "gold"

A successful automated gate deliberately reports `gold: false`. The remaining
items are qualitatively different:

- human full-campaign playtesting for control feel and unscripted edge cases,
- subjective audio loudness/mix/timing judgment,
- subjective desktop presentation/window-scaling judgment,
- building/validating the native Windows EXE on a suitable Windows
  GraalVM + MSVC + Windows SDK host.

The Windows build itself is automated by `tools/native_build.py`; it is listed
separately as an environment requirement rather than pretending a person must
manually port code.

This separation is intentional: automation should shrink the human checklist,
not redefine unfinished work as complete.
