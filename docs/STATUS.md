# Project status

## Pass 005 — component evidence and publication

- Complete recovered private sources: 17/21 classes, 151/313 original method entries.
- Newly recovered: c (11), f (11), GameMidlet (5), manually from the pinned bytecode.
- Fourteen earlier source snapshots are unchanged. b/j/k/p (162 entries) remain unrecovered.
- Two clean seventeen-class component builds produced identical JARs and observation reports.
- 24,657 direct calls per side matched across ten scoped weapon/saucer/lifecycle groups.
- Seven deliberately incorrect variants were detected; four historical suites matched again.
- 75 local recovery-tool tests passed (15 new). No full hosted run existed at initial recovery; publication results are in Actions.
- No complete playable game, production platform, exact/normalized match or native port is claimed.
- This repository update publishes the prepared pass-005 tooling and evidence, not recovered source bodies.

See [the full report](evidence/RECOVERY_PASS_005.md) and
[recorded observations](evidence/weapon-pass-005.json). The earlier publishing
block was a tool/transport limitation. This retry uses the GitHub write API;
repository visibility and game-material exclusions are unchanged. All 7,985
checkpoint file hashes and the seventeen prepared-file hashes were verified;
the 75 recovery-tool tests passed again before publication. The complete public
suite and automatic map regeneration run in Actions: consult the run attached
to this commit for their actual outcome, not the historical local subset.
Private recovery files remain preserved in checkpoint 005.

## Historical record below (superseded local counts)


## Recovery pass 004 (historical)

Fourteen original classes now have private compiling source snapshots, with
124 original method entries. New n/d/r contribute 33 entries; the seven remaining
classes contain 189 entries. There is no complete playable or native game build.

The component JAR now contains the actual recovered entity collection and
composite-building/section logic, integrated with the earlier base/pickup/effects
code. World selection, actor AI/weapon behavior and platform services still have
explicit test boundaries outside the game artifact. No original class is a
compiler input or candidate fallback.

All 68,152 explicit new-target calls per side matched; all 32 callable new entries
had normal-return observations, with one additional class initializer exercised
indirectly. Two fresh runs reproduced identical artifacts and observation reports.
Seven deliberately broken copies were detected. An inherited-field binding error
found in the first reconstruction was corrected before the accepted runs.

All three earlier suites passed again (107,750, 172,170 and 299,377 calls per side
under their own scopes). All 60 local recovery-tool tests passed, including 15
new tests. Full hosted tooling results are available in Actions; game comparisons
require the private inputs and are not performed by public CI.

See [pass 004](evidence/RECOVERY_PASS_004.md) and its machine-readable observations
for exact boundaries, hashes and limitations. Only n/d/r status records advance.
No exact/normalized whole-class match is claimed; the byte-match pointer stays
null. Recovered bodies, inputs, artifacts and logs remain in the private checkpoint.

## Prior: recovery pass 003

Eleven original classes now have private compiling source snapshots, containing
91 method entries. New a/o/h/i/m contribute 33 entries. The remaining 10 classes
and 222 entries, complete game integration and Windows port are still pending.

The source-only component JAR includes the real base entity and connects it to
recovered effects, pickups, object tables, arithmetic, font and audio code.
World/controller/actor/removal and platform dependencies remain explicit test
support outside that JAR. No original class is a candidate fallback.

All 107,750 directly invoked target calls per side matched. There are 31 directly
observed new methods/constructors and two static initializer entries; these are
not branch-coverage or game-accuracy scores. Two fresh runs reproduce the JAR
and report hashes. Five deliberately wrong source variants are detected. Both
previous regression suites also pass (299,377 and 172,170 calls per side in
their separate scopes). All 45 local recovery-tool tests passed, including 15
new tests; the full hosted suite is reported by Actions, not assumed here.

See [pass 003](evidence/RECOVERY_PASS_003.md) and its linked machine-readable
report for commands, hashes, scoped assumptions and excluded behaviors. Source
bodies and original inputs remain private in the workstation/checkpoint. No
exact or normalized whole-class match is claimed; byte-match tiles stay gray.


## Prior: recovery pass 002

Six original classes now have local, compiling source snapshots: e/s/t/g/l/q,
with 58 method entries. Newly recovered g/l/q add 39 entries. The remaining
15 classes / 255 entries are not recovered. Full-game rebuilding, platform
integration and native Windows compilation are still pending.

The new audio/font/navigation suite matched all 172,170 calls per side under
explicit test support. Two fresh runs reproduced identical six-class JAR and
observation JSON hashes. Three deliberately incorrect private variants were
detected. The unchanged e/s/t suite matched its 299,377 calls per side again.
The 30 component/subsystem tooling tests passed locally; consult Actions for
the complete hosted suite. No exact or normalized whole-class match is claimed.

Run `python tools/subsystem_recovery.py --run-dir local/<new-run-name>` with the
pinned private inputs and sources present. Read
[the complete pass-002 evidence](evidence/RECOVERY_PASS_002.md) before interpreting
recovery, component-build or scoped-behavior tiles. Test doubles are not recovered
classes; no game material has been published and byte-match reporting remains null.

## Prior checkpoint (historical, superseded counts)


### Pass 001: first recovered components compile and pass scoped comparisons

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

## Historical pass-001 component boundary

The candidate artifact contains only the three rebuilt classes. Test doubles for
Image and a three-field entity record live outside it. They enable isolated tests
without pretending to implement graphics, entities, or the Windows port. The
original JAR is never on the candidate's compilation or execution classpath.
The original classes are used only in the separate reference process.

All three class files differ from the original binaries. No exact/normalized
match or unconditional accuracy guarantee is claimed. The global byte-match
report remains unselected. Class-level build and behavior passes refer to the
component scopes in the evidence report, not to all gameplay or all handsets.

## Historical pass-001 component checks

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

## Current remaining work

- Complete decompiler output for all 21 classes, or complete recovered game source.
- Production Image/Java ME/Nokia services and the remaining b/j/k/p code.
- A full source-only game JAR, interactive gameplay, missions, save/load or audio.
- Controlled full-game clock/randomness/scheduling comparisons.
- A native Windows compiler proof, Windows executable, Windows playtest or gold release.

Obtain the decompiler for a complete automated pass when tool access permits;
manual bytecode-backed recovery can continue meanwhile. Preserve all seventeen
source snapshots and all five regression suites, recover additional dependencies,
and never hide missing classes with
copied originals or pretend gameplay implementations.
