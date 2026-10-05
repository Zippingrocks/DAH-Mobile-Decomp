# Integration pass 013 checkpoint — campaign matrix and desktop runtime

This checkpoint preserves verified work completed after integration pass 012 before
the workstation run was interrupted. It is intentionally conservative: it records
the campaign-matrix result and the reconstruction defect that was found and fixed,
while leaving the broader 300/500-frame regression rerun marked pending.

## Production-style desktop runtime milestone

The repaired 21-class game was compiled against a production-style desktop runtime
boundary rather than the earlier deterministic test-only adapters. The runtime
provided real window/input/rendering plumbing, file-backed RMS storage, and desktop
audio plumbing sufficient for a smoke run.

Verified before interruption:

- all 21 repaired game classes compiled against the desktop runtime,
- the game initialized and advanced controller ticks,
- a real 176×208 framebuffer was rendered,
- file-backed RMS created a real save file,
- original retail classes and rebuilt classes matched through a controlled
  300-frame gameplay run on the same desktop runtime,
- the framebuffer result and file-backed save result matched for that scope.

This is not yet a released desktop port. The production runtime still needs longer
campaign validation, packaging, audio verification, and Windows-native compilation.

## Full 13-mission campaign matrix

A direct-load campaign matrix was used to exercise all thirteen mission definitions
against original and rebuilt code. The initial matrix matched every mission except
8, 9 and 13.

Those three failures were not timing noise. They exposed a real reconstruction
defect in the world objective counter.

### Reconstruction defect caught

The repaired source had resolved an obfuscated field access to inherited static
`o.n`. The original bytecode explicitly reads the actor byte field **`j.n:B`**.

Because both names were legal after source reconstruction, Java compiled the wrong
binding without an error. The mismatch surfaced specifically in Blisk-heavy mission
objective accounting.

The source correction is therefore:

- **wrong reconstructed binding:** inherited/static `o.n`
- **original binding:** actor byte field `j.n:B`

After correcting that binding, the campaign matrix matched for all thirteen
missions.

## Verified campaign-matrix result

For **all 13 missions**, original and rebuilt code now agree on the matrix scope:

- direct mission/map load state,
- mission objective metadata,
- initial completion gate,
- completion state once the mission's real runtime goal is fulfilled.

Two missions use dynamic kill totals rather than a fixed authored count:

- **Mission 7:** dynamic total = **29**
- **Mission 12:** dynamic total = **30**

The formerly failing Blisk missions 8, 9 and 13 match after the `j.n:B` correction.

This matrix is stronger than a file inventory because it exercises mission
initialization and objective-completion logic. It is still not a complete
start-to-finish human playthrough of every mission.

## Interrupted regression point

The next step had already been identified when the run was interrupted: rerun the
previous accepted integration regressions with the corrected source, specifically:

1. 300-frame production-desktop original-vs-rebuilt run,
2. 500-frame deterministic integration stress run,
3. RMS save/load round-trip,
4. startup/menu→gameplay probes,
5. final all-repaired 21-class build repeatability.

Until those reruns complete, this checkpoint should not be interpreted as a new
gold/full-campaign claim.

## Resume point

Resume from the corrected world objective-counter binding (`j.n:B`), rebuild the
final repaired source tree, run the five regressions above, then continue into
longer mission progression and production desktop packaging. No gameplay redesign
is required by this checkpoint.
