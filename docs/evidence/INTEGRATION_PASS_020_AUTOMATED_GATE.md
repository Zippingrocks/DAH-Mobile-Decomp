# Integration pass 020 — unified automated validation gate

The project's machine-checkable validation steps are now orchestrated by one
public command: `tools/full_validation.py`.

The gate composes the previously independent desktop build, public tests, AMR
packaging checks, direct native-smoke launch, 13-mission matrix, mission-to-mission
RMS progression chain and native-image preflight.

This does not add a new gameplay-fidelity claim by itself; those claims remain
grounded in their individual evidence passes. The value of pass 020 is operational:
future changes can no longer accidentally skip one of the established machine
checks merely because the developer forgot which scripts to run.

## Automated gates covered

- public repository tests
- desktop build/package
- direct `DesktopLauncher --native-smoke`
- four-AMR/four-WAV packaging invariant
- 13/13 mission matrix retail comparison
- 1→13 mission save/progression retail comparison
- native-image preparation/preflight

## Explicit finish-line separation

The unified report always emits `gold: false`. Remaining human judgments and
Windows-host requirements are listed separately in the report.

The human-only list is now intentionally small:

- interactive campaign playtest / unscripted control feel,
- subjective audio mix/timing,
- subjective desktop presentation/scaling.

The native Windows executable is not classified as subjective human work: its
commands are automated, but they still have to execute on a Windows GraalVM/MSVC
build environment before an EXE can be claimed.
