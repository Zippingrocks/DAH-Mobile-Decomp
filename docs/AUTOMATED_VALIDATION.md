# Automated validation gate

`tools/full_validation.py` is the project's "do everything a machine can do"
entry point.

Given the exact retail JAR plus the reviewed local recovered source tree, it can
automatically:

1. run the complete public unit/tooling suite,
2. build the desktop candidate,
3. verify the four original AMR resources and four converted WAV companions,
4. run packaged-audio sanity checks for PCM shape, signal level and clipping,
5. run the direct launcher's headless native-smoke path,
6. compare all 13 mission objective/completion rows against retail,
7. run the fixed-pattern 13-mission simulation stress suite,
8. run the four-seed differential mission-fuzz suite,
9. run the 5,000-frame-per-mission soak suite,
10. run the mission 1→13 save/progression chain with byte-identical file-backed RMS,
11. perform the GraalVM/native-image preflight,
12. emit one machine-readable report.

Example:

```console
python tools/full_validation.py \
  --input inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar \
  --source-dir src/game \
  --report local/full-validation.json
```

An already-built desktop candidate can be supplied with `--candidate`.

## Repository-only readiness audit

`tools/release_readiness.py --check` does not need the private retail/game source
inputs. It verifies the tracked source-map/evidence contract and now runs in
GitHub Actions on pushes and pull requests. If an evidence file disappears or the
recorded 21-class / 313-entry machine gates regress, CI fails.

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
