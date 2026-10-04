# Recovery pass 005 — weapons, saucer specialization and application lifecycle

Three more complete private Java sources were manually reconstructed from the
hash-pinned original bytecode: **c, f and GameMidlet**, adding **27 method entries**.
With the fourteen unchanged earlier source snapshots, the accepted local build
now contains **17 of 21 classes / 151 of 313 original method entries**. Remaining
classes **b, j, k and p contain 162 entries**. Counts are not an accuracy or
whole-game completion percentage.

**Publication note:** recovery was completed locally while the public branch
still recorded pass 004 at e44748c. This update publishes that prepared pass-005
tooling, identifier mappings and evidence. Recovered source bodies and original
game data remain private. Hosted checks are separate from the recovery results
below; consult the Actions run for this publication commit.

| Original | Established responsibility | Entries | Private source |
| --- | --- | ---: | --- |
| c | Weapon selection and setup, aiming, firing gates, ammunition use, hit-state and effect dispatch, projectile update and drawing commands | 11 | src/game/c.java |
| f | Saucer-specific drift/scrolling, reticle movement, nearby-target selection, shared shield/damage, timed update and drawing | 11 | src/game/f.java |
| GameMidlet | Application creation, shared controller/display references and start/pause/destroy forwarding | 5 | src/game/GameMidlet.java |

The saucer still inherits from the unrecovered **j** actor. GameMidlet forwards
into the unrecovered **k** controller. Recovering those callers does not imply
that the actor AI, complete controller, main loop or interactive game now exists.
All previous fourteen source records and their hashes are unchanged.

## Source-only component build and integration

`tools/weapon_recovery.py` pins source, original-class and selected resource
hashes in `config/weapon_recovery.json`. All seventeen sources and the expressly
selected test signatures are jointly compiled using **javac 21.0.11**,
`--release 8 -g:none -implicit:none`, and empty compiler classpath/sourcepath.
The runner checks the full emitted class roster and separates the outputs.

`rebuilt-components.jar` contains exactly the seventeen newly compiled recovered
classes, without test support or original compiled classes. Its candidate JVM
classpath contains this artifact, test support and resource fixtures, never the
original game JAR. A separate reference JVM runs a reference-only JAR containing
the original seventeen classes. No original game class is rewritten.

The new runner uses actual recovered **c and f**, not the weapon and saucer test
records used by older runners. It also uses the real recovered entity collection
**n** for reticle queries, along with the real base entities, building sections,
pickups, effects, arithmetic, resource tables, audio controller and text helpers.
Previous runners retain their narrower historical boundaries for regressions.

Remaining dependencies are openly identified test infrastructure:

- **b** supplies controlled world/camera/grid values, scripted ray interception
  and area-damage callbacks; it is not the recovered world or full raycast system.
- **j** supplies base-actor fields and records scripted state/transform/tick/draw
  callbacks. Its actor AI, ordinary movement, animation and damage implementation
  are not recovered. The real f specialization executes on this test base.
- **k** supplies controlled clock/randomness, scripted controller lifecycle and
  drawing forwarding; it is not the recovered main loop or real input system.
- Display, Displayable and MIDlet test signatures record lifecycle calls/failures.
  They provide neither a phone UI nor a Windows application implementation.
- Image/Graphics use the shared, limited headless 176-by-208 adapter, extended for
  stroke/line/rectangle commands. Pixel/command agreement on that adapter does
  not establish original MIDP/handset rasterization. Media remains scripted,
  without actual sound playback or asynchronous device scheduling.

Test support is kept outside the component JAR. Only independently authored
reference b/j/k test classes have symbol-name constants adjusted to supply the
original bytecode's descriptor-distinguished members. Original classes and
resources remain unchanged and off the public repository.

## Identifier handling and original quirks

Mappings preserve original owner, name and descriptor in the configuration.
All **151 original method entries and declaration order** are checked after the
explicit method aliases already recorded in the project. The new sources are
Java source, not bytecode embedded in an interpreter or copied-class fallback.

The original j.a(II)V test signature becomes `transform(II)V` on the candidate
side: Java source cannot express that void method alongside the inherited final
base-entity a(II)Z method. Its reference test signature is exposed through the
same explicitly recorded adapter technique. This is not a recovered body for j.
Base integer coordinates are explicitly selected where the actor has a shadowing
byte field. Source-level type/name disambiguation does not create a controller
instance or implement missing services.

Several original details were retained rather than silently improved:

- Weapon mode selection does not generally clear a previously set special flag.
- Ammunition remains signed-byte state, including negative unlimited values,
  zero-ammo fallback ordering, and positive decrements.
- Saucer collection hits set the original high flag, not a generic removal bit.
- Lightning point counts narrow to signed byte before allocation; invalid sizes
  retain their original exception behavior rather than being clamped.
- Reticle movement above the top edge rolls back the move instead of clamping.
- Neighbor scanning uses its original asymmetric horizontal range, clamping and
  selection order. A rewritten symmetric search would change behavior.
- Application counters increment before forwarded controller calls, including
  failure paths; multiple application instances share static controller state.

## Actual comparisons

[Machine-readable observations](weapon-pass-005.json) record source/support/tool
hashes, the artifact hash, group digests and method-level outcome counts. All
recorded original/recovered digests and direct-call counts matched.

| Group | Direct calls per side to newly recovered classes |
| --- | ---: |
| Weapon setup, modes and retained state | 2,117 |
| Aiming, positions, target variants and numeric edges | 2,026 |
| Firing gates, target states, ammo/disguise and failures | 12,121 |
| Projectile update, hit flags, effects and boundaries | 4,555 |
| Weapon drawing commands, pixels and failure ordering | 1,056 |
| Saucer initialization, drift, scrolling and shield/damage | 701 |
| Reticle movement and bounds | 1,010 |
| Real collection queries, distinct grid cells and selection | 460 |
| Saucer update/drawing with scripted base-actor callbacks | 311 |
| Application lifecycle, failures and shared state | 300 |
| **Total** | **24,657** |

The direct-call outcome register covers **25 callable methods/constructors**,
all with normal-return observations; the two other new inventory entries are
class initializers observed through loading. Counts exclude calls to older
fixture classes and nested calls. They are not source-line or branch coverage.
Exceptions are compared by type, not message/stack trace; GC timing is excluded.

Cases include signed byte/integer extrema, zero speeds, retained projectile
state, player/nonplayer/saucer modes, invalid modes and references, state gates,
positive/zero/negative ammunition, repeated firing, ray callback failures,
real pickup/effect interactions, shared shield exhaustion and overflow, reticle
clamps/rollback, distinct grid-cell placement and first-target order, injected
drawing failures, and lifecycle failures before/after counter/reference writes.
Original resource bytes are hash-verified local inputs, not publication content.
No complete original level, mission, save/load sequence or device is exercised.

## Repeatability, negative controls and regressions

Accepted runs **local/weapon-pass-005** and **local/weapon-pass-006** produced
byte-identical component JARs and byte-identical observation JSON on the recorded
installed toolchain.

Seventeen-class JAR SHA-256:

`fe2a3af65e2dae81a65aea7eb8d7f64310cb8ccdb629259b9b44aa9c586c153d`

Observation report SHA-256:

`c30da6215d801b8bd5fbe9f34f76097dbc1a8730422d0e1051e702be0980d699`

Seven separately compiled, deliberately incorrect source copies were detected:

| Mutation | Detecting group |
| --- | --- |
| Clear special state on every weapon-mode selection | weapon-selection |
| Decrement ammunition by two instead of one | weapon-firing |
| Replace the saucer pickup-hit high flag with a low bit | weapon-update |
| Remove signed-byte narrowing from lightning point count | weapon-drawing |
| Clamp instead of roll back upward reticle movement | saucer-reticle |
| Add an extra horizontal neighbor column | saucer-targeting |
| Increment the start counter only after controller success | midlet-lifecycle |

None of these variants replaces an accepted source or appears as recovery
progress. Negative-control commands, wrong-source hashes and changed traces are
preserved privately. These controls are representative, not an exhaustive proof.

All four historical runners completed again with matching observations:

| Historical scope | Calls per side |
| --- | ---: |
| Arithmetic, packed data and object tables | 299,377 |
| Audio, bitmap text and navigation | 172,170 |
| Effects, base entities and pickups | 107,750 |
| Collections and composite buildings | 68,152 |

Their run directories are under `local/pass005/regression-runs/`. All **75
available local recovery-tool tests** passed, including 15 new tests of roster
isolation, field/method aliases, lifecycle outcome accounting and probe compilation
without game sources. The separate public map/audit/matcher suite was not present
in the restored private checkpoint and was not run locally. No hosted test result
at the time of the initial local recovery is claimed; publication checks are
recorded separately in Actions.

```console
python tools/weapon_recovery.py --run-dir local/weapon-pass-005
python tools/weapon_recovery.py --run-dir local/weapon-pass-006
python tools/component_recovery.py --run-dir local/pass005/regression-runs/component
python tools/subsystem_recovery.py --run-dir local/pass005/regression-runs/subsystem
python tools/entity_recovery.py --run-dir local/pass005/regression-runs/entity
python tools/collection_recovery.py --run-dir local/pass005/regression-runs/collection
python -m unittest discover -s tests -p 'test_*recovery.py' -v
```

Run 003 stopped on an incorrectly constructed test fixture: a plain base entity
was used where the scenario required the recovered m subtype. The fixture was
corrected rather than changing game semantics. Run 004 passed the earlier test
scope; 005/006 add ammunition boundaries, distinct grid-cell selection and initial
lifecycle state. Initial foreground attempts were interrupted by workstation time
limits and are not accepted completed evidence. A first regression command also
refused an already-used output directory; completed regressions use fresh paths.

## What remains

There is no complete playable source-only game, native Windows executable or
unconditional accuracy claim. All seventeen rebuilt class files differ from the
originals, including original version 45.3 versus emitted 52.0 and mapped names.
No matching policy was weakened and no exact/normalized whole-class result is
claimed. The game-wide comparison-report pointer remains null.

The intended map advances only c/f/GameMidlet recovery, component-build and
scoped-behavior records. The existing dashboard workflow regenerates the maps from those
records after publication. The next substantive integration targets are the
real **j** actor, **b** world, **k** controller/main loop and **p** remaining
systems, replacing test boundaries under the five preserved probe suites.
A full automated decompiler pass remains unavailable; these sources were recovered
manually. Tool-acquisition attempts did not upload or execute the game elsewhere.
