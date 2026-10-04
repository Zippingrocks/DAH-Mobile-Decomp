# Recovery pass 004 — entity collections and composite buildings

Three more complete private sources have been reconstructed manually from the
pinned original bytecode: **n, d and r**, adding **33 method entries**. Together
with the eleven unchanged earlier sources, **14 of 21 classes / 124 of 313
entries** now compile as components. The remaining **7 classes / 189 entries**
are GameMidlet, b, c, f, j, k and p. Counts are not game-completion percentages.

| Class | Established responsibility | Entries | Private source |
| --- | --- | ---: | --- |
| n | Entity bucket, ordered solid/decorative lists, visibility and spatial queries, targeting calls, iteration, migration and disposal | 21 | src/game/n.java |
| d | Composite-building tables, variant selection, section creation/registration, clipped drawing and cleanup | 10 | src/game/d.java |
| r | Building-section entity, dimensions, cached image and drawing | 2 | src/game/r.java |

All earlier source hashes are unchanged. The public repository receives only
original project tooling, independently authored probes/test support, identifier
mappings, hashes and evidence. Original inputs, recovered source bodies and
compiled game components remain in the workstation/private checkpoint.

## Compilation and integration boundary

`tools/collection_recovery.py` verifies input, source, original-class and resource
hashes. It compiles the fourteen recovered sources and explicitly selected test
signatures together with an empty compiler classpath and sourcepath, using
`javac --release 8 -g:none -implicit:none`. Cyclic type dependencies require joint
compilation; output classes are checked against an exact game/support roster and
split before execution. The component JAR contains only the fourteen newly
compiled game classes, no original class and no test substitute.

A separate reference JVM runs the original fourteen classes. The candidate JVM
has no original game class on its classpath. Original game classes are never
rewritten. Only independently authored reference test doubles have name constants
adjusted to expose the bytecode's descriptor-distinguished field names. Aliases
and original/candidate method inventories are recorded and checked explicitly.

This runner replaces the old removal-collection double with recovered **n**.
It exercises recovered collection insertion/removal, real base entities and
pickups, plus the new building loader and section entities. Building registration
passes through an authored world selector which returns a real n instance.
Earlier runners keep their narrower historical boundaries for regression tests.

Still **test infrastructure, not recovered gameplay or production services**:

- b/c/f/j/k provide controlled world selection, actor records, damage callbacks,
  ammo metadata, clock/input/randomness and drawing calls. Their corresponding
  game classes remain unrecovered. Actor AI, real weapon logic and whole-world
  cell selection are not implemented by these doubles.
- ProbeEntity is an authored callback-observation subclass of recovered o, used
  for scripted mutation/failure tests, not a recovered actor. Other lifecycle
  cases use real recovered o and i to test collection integration.
- Graphics/Image provide the same limited 176-by-208 headless raster/command
  adapter used in the earlier entity pass. Media is scripted, with no playback.
  Shared-adapter pixel agreement is not original-handset fidelity.
- BuildingsResourceOwner selects hash-verified or deliberately altered fixture
  streams for resource-failure tests. It is outside the game component artifact.

## Original-versus-recovered observations

[Machine-readable results](collection-pass-004.json) contain input/source/tool
hashes, call counts, method outcomes and observation digests, not bytecode/assets.
All recorded original/candidate digests and counts matched in the accepted runs.

| Probe group | Explicit new-target calls per side |
| --- | ---: |
| Building table loading, partial state and cleanup | 2,083 |
| Building construction, variants and section metadata | 2,236 |
| Building/section drawing and failures | 2,184 |
| Rectangle, visibility and fixed-point ray calculations | 44,008 |
| Collection loading, classification and ordered insertion | 2,950 |
| Picking, nearby and directional queries | 3,965 |
| Actor target/damage dispatch and pickup calls | 5,924 |
| Collection lifecycle, migration, sorting and disposal | 2,714 |
| Collection drawing, iterator state and failures | 2,088 |
| **Total** | **68,152** |

Counts include explicitly invoked constructors/setup in n/d/r, but exclude calls
to old classes/test fixtures and nested calls. All **32 directly callable new
methods/constructors** have recorded normal returns; the additional d static
initializer is reached through loading. These are direct-call observations,
not line/branch coverage or proof for every input. Exceptions are compared by
type, not messages/stack traces, and successful/exceptional outcomes stay separate.

Cases include every truncated prefix of the 330-byte HousePieces, 542-byte
HouseParts and 146-byte Houses tables under both packed-reader states; missing,
negative-length and injected failing streams; repeated load/cleanup/cache state;
variant/random boundaries; valid and invalid building sections; clipped drawing
commands and pixels; ordered insertion/ties/duplicates; malformed entities and
indices; rectangle/ray edges and integer overflow; all byte-valued entity types;
visibility/picking, scripted actor states, real pickups/removal, list mutations,
signed-byte migration/capacity boundaries, two sorting sweeps and failure ordering.
Resources including the original house/barn images are local hash-verified inputs,
not public repository contents. No complete original level or mission is run.

## A reconstruction error that the comparisons caught

The first candidate mismatched targeting. Its `source.k` expression selected a
subclass byte field, while the original field instruction named the base o
integer position field. Explicitly selecting the base field corrected the
reconstruction; the final source snapshot and reports reflect that correction.
The public probe's field lookup also preserves owner and descriptor. An authored
Parent/Child shadowing fixture tests that lookup independently of the game.

Other original quirks are preserved rather than silently improved: collection
sorting performs two sweeps, not an invented full sort; ties and list mutations
retain their order; migration index narrowing/increment ordering survives failed
array writes; the actor-state predicate keeps its original conjunction; building
cleanup leaves cached images, table maxima narrow to signed bytes, and variant
selection uses the original sign-bit behavior. The section constructor's unused
first owner argument is not given an invented purpose.

## Repeatability, negative controls and regressions

Accepted runs **local/collection-pass-003** and **local/collection-pass-005**
produced identical component JARs and byte-identical observation JSON.

Fourteen-class component JAR SHA-256:

`9d15d48c226ccba191e6456386d49cd66b3afc0357c8ad15dd9a88f10425fa1c`

Observation report SHA-256:

`cda164bc87554b48a840464481b28caea02103be8166ebb9cdfe1423458b3eb2`

Seven independently compiled, deliberately broken private variants were detected:

| Mutation | Detecting probe |
| --- | --- |
| Select the hidden actor field instead of base position | collection-targeting |
| Wrong fixed-point ray shift | collection-math |
| Change equal-position insertion order | collection-population |
| Replace the actor-state conjunction with disjunction | collection-targeting |
| Clear images during original cache-preserving cleanup | building-load |
| Select a variant from parity instead of sign bit | building-state |
| Assign section width as section height | building-state |

Wrong copies are stored separately and never replace accepted source snapshots.
These controls demonstrate representative defect detection, not test completeness.
Run 001 is the failed reconstruction diagnostic; run 002 predates eighty added
integration calls. Run 004 and an initial entity regression were interrupted by
the workstation timeout. None is substituted for completed accepted evidence.

All three previous suites passed again in separate fresh runs:

| Historical scope | Run | Calls per side |
| --- | --- | ---: |
| Effects/base entities/pickups | entity-regression-004b | 107,750 |
| Audio/font/navigation | subsystem-regression-004 | 172,170 |
| Arithmetic/data/table helpers | component-regression-004 | 299,377 |

All **60 local recovery-tool tests** passed, including 15 new tests for counts,
source preservation, aliases, output isolation, missing-input refusal and an
independently compiled field-shadowing fixture. Hosted CI also runs the older
map/audit/matcher/treemap tests; consult Actions for that actual result. The
component comparisons above require private inputs and do not run in public CI.

```console
python tools/collection_recovery.py --run-dir local/collection-pass-003
python tools/collection_recovery.py --run-dir local/collection-pass-005
python tools/entity_recovery.py --run-dir local/entity-regression-004b
python tools/subsystem_recovery.py --run-dir local/subsystem-regression-004
python tools/component_recovery.py --run-dir local/component-regression-004
python -m unittest discover -s tests -p 'test_*recovery.py' -v
```

## Remaining fidelity and integration work

There is still no complete playable rebuild or native Windows executable. All
fourteen component class files differ from the originals, including original
version 45.3 versus emitted 52.0 and explicit source-identifier aliases. No exact
or normalized whole-class match is claimed. The matching policy is unchanged;
the game-wide comparison report pointer stays null and its tiles stay unverified.

This pass advances only n/d/r recovery, component-build and scoped-behavior
records. Platform timing, real audio, actor AI/weapon execution, world/controller
logic, full levels, missions and save/load remain outside this evidence boundary.
External decompiler download was retried unsuccessfully; recovery remains manual.
Preserve the fourteen sources and four suites while recovering the seven remaining
classes and replacing the remaining test boundaries with real implementations.
