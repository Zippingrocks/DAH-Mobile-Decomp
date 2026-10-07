# Integration pass 028 — restored source and fresh verification

The available private checkpoint 006 contained only 18 recovered classes and
predated the final source snapshots. A broader saved-file search found no newer
checkpoint. This pass reconstructs a **separate complete verification tree** from
the exact retail JAR with pinned CFR 0.152 and Vineflower 1.12.0. It does not claim
to restore the exact text of the historical renamed sources.

The legacy manifest and 18 checkpoint-006 sources remain intact. The new
21-class tree lives privately under `src/game/verification-028` and has its own
hash manifest, `config/integration_restore_028.json`. Original owner/name/descriptor
identities map to the neutral source identifiers in the private `member-map.json`.
Raw decompiler output, repair diffs and logs remain separate from repaired source.

## Repairs and source-only build

- Repaired the documented j state-transition control flow, preserving switch
  fall-through and comparing it to the previous manual reconstruction and Vineflower.
- Repaired j drawing-offset and f cell-coordinate definite-assignment artifacts.
- Moved b's tile-loop local into the actual bytecode scope.
- Used the separate r.class decompile omitted by the whole-JAR passes.
- Corrected b's two duplicated actor constructions against original DUP/ASTORE/
  PUTFIELD behavior: the flag is set on the same instance inserted into the world.
- Objective counting binds the actor byte `j.n:B` (`var_byte_n`) rather than
  inherited `o.n:I`.

Two clean builds produce byte-identical class files for all **21 game classes**.
All **313 method entries** and all **366 field entries** preserve their original
ordered descriptor sequences. Direct class-file parsing confirms 366 fields;
the historical pass-007 prose count of 378 is not reproduced and is superseded
by this fresh count for the pinned input. No original game class is a compiler
input or a candidate fallback. All **122 non-code entries** are byte-identical
in the integration candidate.

## Fresh comparison results

All five unchanged authored integration probes match retail byte-for-byte:
startup/lifecycle, deterministic input/state/rendering, default menu-to-gameplay,
RMS save/load, and the 500-frame gameplay stress run. Their hashes reproduce the
accepted pass-013 regression outputs.

A separate 300-frame run on the production desktop runtime matches state and
real 176×208 framebuffer checkpoints at frames 100/200/300. The frame-300 state
and framebuffer hashes reproduce pass 014. Both file-backed `DAH.rms` files are
90 bytes and byte-identical, SHA-256
`8394bcc4de35787475f7455746806eeb4fdf6a45c77f96be6d102d596813aa22`.
The authored desktop replay probe and its exact compile/run recipe are preserved
in the private checkpoint.

The full automated gate passes again against the freshly source-built desktop JAR:

| Check | Fresh result |
| --- | --- |
| Mission objective/completion matrix | 13/13 missions match |
| Fixed-pattern mission stress | 3,900 frames per side match |
| Four-seed mission fuzz | 7,800 frames per side match |
| Long mission soak | 65,000 frames per side match |
| Fresh-JVM progression/save chain | Missions 1→13 and every RMS step match |
| AMR packaging/audio sanity | All four effects pass |
| Direct-launch native smoke and AOT preflight | Pass; no Windows EXE produced |

This replay exposed a real workstation portability defect:
`python tools/mission_soak.py` could not import `tools` without a PYTHONPATH
workaround. The runner now supports both standalone and package imports. A new
subprocess regression launches `--help` with PYTHONPATH removed and an unrelated
working directory. The full gate was rerun successfully after the fix.

The integration/readiness tools now accept an explicitly selected snapshot
manifest. Manifest selection cannot change the pinned input, omit classes,
change expected counts, or point the source tree outside `src/game`.

## Repeatable commands

From the restored repository root, with a Java compiler supporting release 8
and FFmpeg on PATH:

```console
python tools/workstation_check.py --config config/integration_restore_028.json
python tools/integration_recovery.py --config config/integration_restore_028.json --run-dir local/integration-next
python tools/desktop_build.py --source-dir src/game/verification-028 --output local/desktop-next.jar --report local/desktop-next.json
python tools/full_validation.py --candidate local/desktop-next.jar --report local/full-validation-next.json
```

Use unused integration-run/report paths. The old default integration manifest
still refers to the historical snapshots; select the new manifest explicitly.
A valid prerequisite report is separate from actual source-build and behavior
reports. Evidence and hashes are in
[integration-pass-028-restored-source.json](integration-pass-028-restored-source.json).

## Remaining limits

The restoration/reproducibility blocker is closed for this independent snapshot.
The new identifiers remain neutral decompiler aliases rather than the historical
semantic names. No exact/normalized whole-class match or unconditional fidelity
claim is made. Human full-campaign/control/audio/presentation review and a
validated Windows native executable remain open. Original resources, recovered
source, decompiler binaries and local products remain private and untracked.
