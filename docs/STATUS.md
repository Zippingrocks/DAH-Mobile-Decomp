# Project status

## Current stage: first recovered components compile and pass scoped comparisons

See [recovery pass 001](evidence/RECOVERY_PASS_001.md) for the exact boundary and
[machine-readable evidence](evidence/component-pass-001.json) for artifact hashes
and observation digests. This is no longer inspection-only work, but it is not
a complete game build.

| Measure | Established result |
| --- | --- |
| Hash-pinned original | English v1.2.0; 201,816 bytes |
| Original inventory | 21 classes / 313 method entries |
| Complete local source components recovered | e, s, t: 3 classes / 19 method entries |
| Component compilation | e/s/t compile from recovered Java with explicit test-only dependencies |
| Scoped differential observations | 299,377 calls per side; all recorded counts and digests matched |
| Fresh-run reproducibility | Two clean builds produced identical JARs and observation reports |
| Negative controls | Three intentional defects were detected |
| New public tooling tests | 15 passed locally; not gameplay tests |
| Remaining original components | 18 classes / 294 method entries |
| Full game / native Windows port | Neither built nor verified |

The recovery was manual from original bytecode. A third-party decompiler download
is still blocked in this workstation; no automated decompiler pass is claimed.
Source snapshots and the original input remain local and are backed up in the
conversation's recovery checkpoint. This public repository contains tooling,
hashes, identifier mappings, evidence summaries and progress records, not game
source or assets. Publication/visibility must be addressed before committing
recovered source.

## What the component passes do and do not mean

The candidate artifact contains only the three rebuilt classes. Test doubles for
Image and a three-field entity record live outside it. They enable isolated tests
without pretending to implement graphics, entities, or the Windows port. The
original JAR is never on the candidate's compilation or execution classpath.
The original classes are used only in the separate reference process.

All three class files differ from the original binaries. No exact/normalized
match or unconditional accuracy guarantee is claimed. The global byte-match
report remains unselected. Class-level build and behavior passes refer to the
component scopes in the evidence report, not to all gameplay or all handsets.

## Run the local component checks

Requires the pinned original under inputs/original, the three private source
snapshots under src/game, Python 3.10+ and a JDK supporting --release 8. The
recorded compiler/runtime was OpenJDK 21.0.11. Choose a fresh evidence directory:

```console
python tools/component_recovery.py --run-dir local/component-next-run
```

The runner does not download, decompile or upload any files. Missing or changed
inputs fail explicitly. The public-only tooling suite needs no game files:

```console
python -m unittest discover -s tests -v
```

## Existing foundation

Input auditing, the source-tree generator, four visual treemaps, conservative
byte comparison and the GitHub Actions refresh workflow were established in
earlier commits. The previous 68 tooling tests and initial successful hosted
refresh are historical evidence; consult Actions for the current commit's run.
The newly added 15 tests are a separate addition, not 15 recovered game methods.

## Not established / next concrete work

- Complete decompiler output for all 21 classes, or complete recovered game source.
- Real implementations of the Image/Java ME/Nokia platform services and class o.
- A full source-only game JAR, interactive gameplay, missions, save/load or audio.
- Controlled full-game clock/randomness/scheduling comparisons.
- A native Windows compiler proof, Windows executable, Windows playtest or gold release.

Obtain the decompiler for a complete automated pass when tool access permits;
manual bytecode-backed recovery can continue meanwhile. Preserve the e/s/t
regressions, recover additional dependencies, and never hide missing classes with
copied originals or pretend gameplay implementations.
