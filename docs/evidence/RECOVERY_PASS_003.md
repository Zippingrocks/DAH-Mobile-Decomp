# Recovery pass 003 — effects, base entities and pickups

Five more complete local source files are manually reconstructed from the pinned
original bytecode: **a, o, h, i and m**. They add **33 method entries**, making
**11 of 21 classes / 91 of 313 entries** recovered and compiling as components.
The remaining **10 classes / 222 entries** are unrecovered. This is not a game
completion percentage. The large world/controller/actor systems still remain.

| Class | Established responsibility | Entries | Private source |
| --- | --- | ---: | --- |
| a | Effects atlas metadata, frame timelines, cloning and clipped drawing | 8 | src/game/a.java |
| o | Base entity, type factory, screen picking, drawing and timed removal | 7 | src/game/o.java |
| h | Two clipped-column draw passes and a six-phase update | 3 | src/game/h.java |
| i | Pickup drawing, stat/ammunition changes and collection side effects | 11 | src/game/i.java |
| m | Spawn-type metadata, child association and update/draw delegation | 4 | src/game/m.java |

The earlier e/s/t/g/l/q source hashes are unchanged. Their previous test runners
remain usable. Recovered source bodies, original classes and original resources
are **not published** in this still-public repository. The new public Java files
are independently authored probes and explicit test support, not game recovery.

## Integration and compilation boundary

`tools/entity_recovery.py` compiles all eleven recovered sources with an empty
compiler classpath and sourcepath using `javac --release 8 -g:none -implicit:none`.
The real base entity and the authored actor test signatures refer to each other,
so they are compiled together in staging. The runner then separates outputs:
`rebuilt-components.jar` contains **only a/e/g/h/i/l/m/o/q/s/t.class**. Test
support is outside it. No original class is a compiler input or candidate runtime
fallback. A separate reference-only JAR and separate JVM use the originals.

This pass replaces the old three-field base-entity substitute **in this runner**
with the actual recovered o. The new o/i paths exercise recovered a effects,
e/s tables and arithmetic, g audio logic and l text logic together. Earlier
runners deliberately retain their historical, narrower test boundaries.

Remaining test dependencies are b/c/f/j/k/n world, actor, controller and removal
records; a limited headless Image/Graphics adapter; and scripted media services.
The j/f constructor targets have no AI, navigation or movement implementation.
The collection sink records removal requests, not a working world collection.
The k wrapper supplies controlled clock/input/random values and forwards drawing
calls to the test adapter. These six classes remain unrecovered on the dashboard.
The media adapter does not play sound. Graphics tests compare both command traces
and pixels on a shared 176-by-208 surface, not an original handset renderer.

## Source reconstruction details

Field names are disambiguated by owner, original name and type descriptor in
`config/entity_recovery.json`. Original method inventories and declaration order
are checked against javap, with only recorded method aliases applied. The static
base predicate o.a(I)Z becomes isActorType(I)Z because Java source cannot combine
that static signature with the subclass's instance i.a(I)V rendering method.
No original game binary is rewritten to work around this.

The original position field named k also hides the controller type k in Java
expressions. The new sources use an explicit null expression typed as k to
qualify its **static** members; they do not create or dereference a controller
instance. This source-level disambiguation is documented, not a missing-system
stub. A later consistent naming cleanup can remove it under regression tests.

Observed original quirks are retained:

- Effect-table loading appends to its existing vector, retains partial state,
  and marks loading complete after caught EOF/IO exceptions.
- Effect frame counters narrow to signed bytes. Special kinds retain their
  original loop boundaries and shared frame-vector references.
- Base-entity removal keeps its original shifted flag condition and a shared
  rise counter. Some pickup update paths request removal twice; no deduplication
  has been invented.
- The pickup stat update narrows to short **before** the upper-cap comparison.
- Four spawn-metadata branches consume a random value even though they discard
  its result. Those calls have not been optimized away.
- Drawing preserves clip changes and ordering before exceptions.

## Actual original-versus-recovered results

[Machine-readable observations](entity-pass-003.json) record the exact inputs,
source/support/tool hashes, component artifact hash, outcomes and trace digests.
All original/recovered digests and target-call counts matched.

| Probe group | Direct calls per side to newly recovered classes |
| --- | ---: |
| Effects resource loading and partial state | 1,185 |
| Effect construction, clone sharing and frame state | 61,555 |
| Effect centered/direct drawing and failure paths | 470 |
| Entity construction, factory dispatch and point picking | 18,390 |
| Entity update, flags, expiration and integrated pickup/removal | 18,180 |
| Pickup effects, repetition and scripted failures | 5,770 |
| Pickup/column/base drawing and clip state | 1,547 |
| Attachment metadata, RNG and delegation | 653 |
| **Total** | **107,750** |

Counts include explicitly invoked constructors/setup in the five new classes;
fixture calls to older components and actor support, and nested game calls, are
excluded from this total. The outcome register identifies **31 directly invoked
methods/constructors**; the other two new inventory entries are static class
initializers reached through class loading. This is not branch coverage or
proof that every possible input was exercised.

Tests cover every truncated prefix of the 567-byte effects table under both
packed-reader states, injected read failures, repeated loads, explicit special
frame-loop cases, signed-byte phase values, integer/short overflow boundaries,
factory type/threshold branches, deliberate rectangle-edge contact, shared rise
state across entities, pickups with full/partial/overflowing stats, changed/null
ammo tables, repeated collection, and injected draw/world/media/RNG failures.
Real resources are locally hash-verified from the original, not uploaded.

An early column test selected a type whose cached image was null; it could not
exercise the later drawing operations. The accepted fixture explicitly supplies
the original Beam image and tests signed height values. Successful and exceptional
target outcomes are recorded separately, so a scene failing early is not silently
represented as a successful draw. Exceptions are compared by type, not messages
or stack traces. GC timing, original device services, world scheduling and full
missions/saves are outside this test boundary.

## Repeatability and negative controls

Fresh runs `local/entity-pass-003` and `local/entity-pass-005` produced identical
component JARs and byte-identical observation JSON. Run 004 was interrupted by
the workstation command timeout and is not accepted evidence.

Eleven-class artifact SHA-256:

`6609fa11ad35de4c4c8e0fb56690a6a3000be0e898bc880212bc7d3cfaae9b82`

Five independently compiled, deliberately wrong copies were detected:

| Mutation | Detecting probe |
| --- | --- |
| Wrong effect kind-1 frame-wrap boundary | effects-state |
| Replace shifted entity flag test with a one-bit test | entity-update |
| Change pickup stat increment | pickup-state |
| Wrong clipped-column phase-reset boundary | entity-draw |
| Remove the discarded RNG consumption for type 8 | attachment-state |

None of these wrong sources replaced an accepted source snapshot. Their separate
commands, mutated-source hashes and outputs remain in the private checkpoint.
These negative controls demonstrate detection of representative defects, not
completeness of the tests.

The old e/s/t runner again matched **299,377 calls per side**; the old g/l/q
subsystem runner again matched **172,170 calls per side** under their original
scopes. All **45 locally available recovery-tool tests** passed, including 15
new tests of outcome accounting, aliases, output separation, missing-source
refusal and probe compilation with no game source. Hosted CI additionally runs
the audit/map/comparator/treemap tests; consult Actions for its actual outcome.

```console
python tools/entity_recovery.py --run-dir local/entity-pass-003
python tools/entity_recovery.py --run-dir local/entity-pass-005
python tools/component_recovery.py --run-dir local/component-regression-003next
python tools/subsystem_recovery.py --run-dir local/subsystem-regression-003next
python -m unittest discover -s tests -p 'test_*recovery.py' -v
```

## What is still not claimed

There is no complete source-only game JAR, playable game, native Windows build,
handset-fidelity certification, or unconditional game-equivalence proof. Source
recovery remains manual: external CFR download attempts still failed here.

All eleven rebuilt class files differ from their originals, including original
version 45.3 versus emitted 52.0 and recorded identifier changes. No byte-matching
rule was weakened, no original bytecode copied into the rebuilt artifact, and
no exact/normalized whole-class match is claimed. The game-wide byte-match report
pointer remains null; those tiles stay unverified. Only a/h/i/m/o recovery,
component-build and scoped-behavior states advance in this pass.

Next integration targets are the real entity collection/actor logic and the
remaining controller/main-loop code. Preserve all accepted source hashes and the
three probe suites when replacing the remaining test dependencies.
