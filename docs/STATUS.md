# Project status

## Integration pass 014 — recreated production desktop runtime

- Recreated the authored production-style desktop runtime after the interrupted workstation.
- Original retail and rebuilt game classes now match through a fresh **300-frame gameplay run** on that runtime.
- Matching observations include normalized game state, real 176×208 desktop framebuffer, and the file-backed RMS save result.
- The produced RMS save file is 90 bytes and byte-identical on both sides.
- This closes the final pending post-campaign regression from pass 013; all five interrupted rerun categories are re-established.
- The separate campaign checkpoint still records **13/13 missions matching** for direct-load state/objective/completion semantics after the `j.n:B` correction.
- The desktop runtime is not yet a finished release: AMR audio support, human interactive playtesting, longer end-to-end mission scripts, desktop packaging and native Windows AOT remain.

See [desktop runtime evidence](evidence/INTEGRATION_PASS_014_DESKTOP_RUNTIME.md) and
[machine-readable results](evidence/integration-pass-014-desktop-runtime.json).

## Prior status

## Integration pass 013 — restored regression replay

- Reconstructed an independent private verification tree from the exact retail JAR and pinned CFR/Vineflower toolchain after the workstation interruption.
- All **21 classes / 313 method entries** compile source-only again; ordered descriptor sequences match the retail classes.
- Two clean compiles reproduce every rebuilt class byte-for-byte.
- Original vs rebuilt outputs match again for startup/lifecycle, deterministic state/input/render, menu→gameplay, RMS save/load and the 500-frame gameplay stress probe.
- This restored verification tree is semantic evidence; its Java text is not claimed to be byte-identical to the interrupted renamed private source snapshot.
- The **13/13 mission matrix** remains separately preserved by the pass-013 campaign checkpoint after the corrected `j.n:B` objective-counter binding.
- Of the five interrupted reruns, only the **300-frame production desktop runtime rerun** remains to be recreated and repeated.

See [restored regression evidence](evidence/INTEGRATION_PASS_013_REGRESSION_RESTORE.md) and
[machine-readable results](evidence/integration-pass-013-regression-restore.json).

## Prior status

## Integration pass 013 checkpoint — campaign matrix and desktop runtime

- Preserved verified work from the interrupted post-pass-012 integration run.
- A production-style desktop runtime compiled and ran all 21 repaired classes, rendered a real 176×208 framebuffer, and wrote a file-backed RMS save.
- Original retail and rebuilt classes matched through a controlled 300-frame desktop-runtime comparison in the recorded scope.
- A direct-load matrix now matches **all 13 missions** for load state, objective metadata, initial completion gate and completion state.
- The initial mission 8/9/13 mismatches exposed a real reconstruction bug: the rebuilt objective counter was reading inherited static `o.n` instead of the original actor byte field **`j.n:B`**.
- Correcting that field binding closes the Blisk-mission mismatches. Missions 7 and 12 correctly use dynamic kill totals of **29** and **30**.
- The interruption happened before rerunning all prior 300/500-frame, save/load, startup/menu and clean-build regressions against the corrected source.
- Therefore this checkpoint is **not** a gold or complete-campaign claim.

See [the checkpoint report](evidence/INTEGRATION_PASS_013_CHECKPOINT.md) and
[machine-readable checkpoint](evidence/integration-pass-013-checkpoint.json).

## Prior status

## Integration pass 012 — persistence and 500-frame gameplay stress

- Original and rebuilt RMS save/load behavior matches for an 82-byte save buffer, including representative bytes, call ordering and no-save defaults.
- The authored RMS adapter is now stateful enough to exercise the game's real record-store path, but remains deterministic test infrastructure rather than production persistence.
- A controlled **500-frame gameplay run** after the established default menu→world path matches at gameplay start and at frames 100, 200, 300, 400 and 500.
- Final render, image/resource trace, media call/state trace and RMS trace also match.
- Candidate JAR remains the same final all-repaired 21-class build from pass 011; no recovered game logic changed in this pass.
- Local public recovery/integration tooling tests passed before publication.
- This is not a complete campaign playthrough, real audio implementation, production RMS backend, handset-fidelity claim or native Windows port.

See [integration pass 012](evidence/INTEGRATION_PASS_012.md) and
[machine-readable evidence](evidence/integration-pass-012.json).

## Prior status

## Integration runner publication — controlled menu to gameplay

- Published a reproducible `tools/integration_recovery.py` runner for the final repaired 21-class source tree.
- The runner verifies the pinned original, all private source hashes, exact 21-class output roster, 313 method entries, descriptor-sequence preservation, byte-exact non-class resources, and repeatable candidate builds.
- Public authored adapters model the Java ME/Nokia API signatures needed by original and rebuilt classes; they remain deterministic test infrastructure, not production platform services.
- Published startup/lifecycle, state-graph, and deep controlled integration probes.
- The deeper private integration script follows the default UI path into real world/gameplay mode, then exercises recovered movement/weapon input and rendering; original and rebuilt results matched in two clean runs.
- This expands integration evidence beyond startup, but does not establish complete missions, unrestricted frame scheduling, real RMS/audio/handset behavior, or native Windows support.

## Prior status

## Integration pass 011 — final all-repaired whole-tree build

- The **final repaired 21-class / 313-entry source set compiles together** with no copied original game classes.
- Two clean builds reproduced every rebuilt class byte-for-byte; candidate JAR SHA-256 is `b3e5466c3cb7e0f3e4d3264d612d37cb56418efb4dff745e7bc6f06bad10a381`.
- Candidate packaging contains 21 rebuilt classes plus **122 byte-identical original non-class entries**.
- Ordered field/method descriptor sequences match the original for all 21 classes; method total remains 313.
- Original and rebuilt startup/init/five-tick/lifecycle support traces match.
- Deterministically seeded integrated state hashes match after initialization, after five ticks, after a multi-key sequence, and for the tested rendered frame.
- The first integrated paint caught and corrected a real `k.paint(Graphics)` field-shadowing/linkage error before acceptance.
- These checks use deterministic authored Java ME/Nokia adapters, not a production platform; complete missions, unrestricted main-loop scheduling, persistence, real audio, handset fidelity and native Windows remain unverified.
- No exact/normalized whole-class byte match or unconditional full-game equivalence claim is made.

See [integration pass 011](evidence/INTEGRATION_PASS_011.md) and
[machine-readable evidence](evidence/integration-pass-011.json).

## Prior status

## Pass 010 — final class p repaired

- Repaired private sources: **21/21 classes, 313/313 original method entries**.
- p contributes the final 54 entries and 46 fields.
- CFR 0.152 output was cross-checked against Vineflower 1.12.0 and original javap; source-only identifier collisions/shadowing were repaired without gameplay redesign.
- Repaired p compiles in an isolated candidate runtime with authored support and no original p.class fallback.
- **10,906 observation records per side** matched across five scoped groups; seven deliberate defects were detected.
- Pass 007 already established a mechanical 21-class source-only compile; a fresh integration compile from the final all-repaired snapshots is still required.
- No exact/normalized whole-class match, complete playable game, production platform or native port is claimed.

See [pass 010](evidence/RECOVERY_PASS_010.md) and
[machine-readable evidence](evidence/ui-pass-010.json).

## Prior status

## Pass 009 — controller k repaired

- Repaired private sources: 20/21 classes, 259/313 original method entries.
- k contributes 31 entries and 44 fields; only p remains raw-output.
- k compiles in the complete source-only tree with no copied original class files.
- 434,002 scoped observations per side matched for input masks, edge transitions, save helpers and drawing helper.
- Four deliberate defects in tested paths were detected.
- Full run-loop/menu/RMS/timing behavior is not yet claimed.
- No exact/normalized match, complete playable game or native port is claimed.

See [pass 009](evidence/RECOVERY_PASS_009.md) and
[machine-readable evidence](evidence/controller-pass-009.json).

## Prior status

## Pass 008 — world manager b repaired

- Repaired private sources: 19/21 classes, 228/313 original method entries.
- b contributes 46 entries and 93 fields; k/p remain raw-output only.
- CFR's duplicated actor-construction defect was corrected against original bytecode and Vineflower.
- b compiles in the 21-class source-only tree with no copied original class files.
- Two clean compiles reproduced identical rebuilt classes.
- 400,002 scoped observations per side matched across mission state, alert transitions, viewport bounds and grid/collision lookup.
- Three deliberate defects in tested paths were detected; one ineffective mission mutation is explicitly not counted.
- No full-level/main-loop equivalence, exact/normalized match, playable game or native port is claimed.

See [pass 008](evidence/RECOVERY_PASS_008.md) and
[machine-readable evidence](evidence/world-pass-008.json).

## Prior status

## Pass 007 — automated raw decompiler inventory and all-class source compile

- CFR 0.152 and Vineflower 1.12.0 are locally available and hash-pinned.
- All 21 original classes have some local source recovery: 18 repaired/reviewed, b/k/p raw.
- A repaired-for-compilation raw tree builds all 21 classes from Java source with no copied original class files.
- Per-class method entries total 313/313; ordered method descriptors match every class.
- Ordered field descriptors match every class, 378 fields total.
- Two clean compiles produced byte-identical rebuilt class files.
- A local candidate JAR has 21 rebuilt classes plus 122 byte-identical non-class resources and zero original class entries.
- This is a mechanical source/build milestone, not playable-game or behavior-equivalence proof.

See [decompiler pass 007](evidence/DECOMPILER_PASS_007.md) and
[its machine-readable record](evidence/decompiler-pass-007.json).

## Pass 006 — shared actor recovery

- Repaired/reviewed private sources: 18/21 classes, 182/313 original method entries.
- Newly repaired j contains 31 entries; seventeen prior source hashes remained unchanged.
- 25,818 direct actor calls per side matched across ten scoped groups.
- A wrong overloaded collection call was detected and corrected before acceptance.
- Two clean final runs reproduced identical component JARs and reports.
- Seven deliberate actor defects were detected; all five historical suites passed again.
- 91 local recovery-tool tests passed; this is separate from hosted repository tooling.
- No complete playable game, platform implementation, exact/normalized match or native port is claimed.

See [pass 006](evidence/RECOVERY_PASS_006.md).

## Historical status

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
