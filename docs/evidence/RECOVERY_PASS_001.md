# Source recovery pass 001 — component recovery, not a game release

## What actually changed

The first source recovery is real **manual reconstruction from the pinned original
bytecode**, not an automatic CFR/Vineflower pass and not a remake. Three complete
class source files now exist locally and compile: `e`, `s`, and `t`. Their method
inventory is **19 entries** (13 + 5 + 1), including constructors and static
initializers. The other **18 classes / 294 method entries remain unrecovered**.

| Original | Recovered responsibility | Method entries | Local source |
| --- | --- | ---: | --- |
| e | Fixed-point/integer arithmetic, rectangle tests, packed-data reading, image-load call handling | 13 | src/game/e.java |
| s | Object-table loading, table initialization and image-cache management | 5 | src/game/s.java |
| t | Four-integer data holder; field meanings not yet established | 1 | src/game/t.java |

All method names/descriptors remain present and in original declaration order.
Seven field renames are explicit in `config/component_recovery.json`; they resolve
bytecode-legal name collisions and a Java source field/type shadowing conflict.
No unreviewed semantic name has been assigned to the four fields in `t`.

The repository remains public. **Recovered game source, original classes, assets,
and compiled components have not been committed.** The checked-in source hashes
identify the local snapshots without publishing their bodies. Public Java files
under `tests/java/` are independently authored probes and explicit test doubles,
not recovered game implementations.

## Build boundary

The compilation produces **rebuilt-components.jar containing only e.class,
s.class, and t.class**. No original compiled class is copied into that artifact.
The original JAR is absent from the recovered compiler classpath and the recovered
probe classpath. A separate reference-only JAR supplies the original versions to
a separate JVM process solely for comparison.

The public runner is `tools/component_recovery.py`. It pins the source snapshots,
verifies the original JAR and object-resource hashes, disallows implicit source
compilation, restricts emitted classes, retains logs, and refuses to overwrite a
previous run. It uses `javac --release 8 -g:none -implicit:none`, not a native
compiler. The observed toolchain was OpenJDK/javac **21.0.11** on Linux.

Two test dependencies are deliberately **not implementations of missing systems**:

- `javax.microedition.lcdui.Image` records calls and returns scripted results; it
  does not decode PNGs, draw pixels, or implement a phone/Windows graphics layer.
- `o` is a three-field test record for geometry inputs; it does not implement the
  unrecovered game class, construct real entities, or provide AI.

Both sides use the same doubles. The doubles are compiled into a separate support
directory and are **not in rebuilt-components.jar**. Class `o` stays unrecovered
on the progress map. These are component compilation and scoped test passes,
not a full-game source-only build or a native Windows port.

## Original-versus-recovered observations

Machine-readable evidence: [component-pass-001.json](component-pass-001.json).
The complete logs and commands remain in the local workstation/checkpoint.

| Probe group | Calls on each side | Compared observations |
| --- | ---: | --- |
| Constructors and initial state | 5,010 | Four-field assignments, integer boundaries, static initial values |
| Arithmetic | 122,482 | Fixed-point shifts/multiply/divide, zero denominator, overflow, integer algorithm, distance/scaling |
| Packed reader and failures | 131,114 | Alternating 12-bit results, decoder state, EOF/null failures, cross-stream continuation |
| Image call contract with test double | 84 | Paths, null retries, checked/unchecked exceptions, Errors, call sequences |
| Inclusive geometry with test records | 36,007 | Boundary contact, degenerate/negative ranges, signed dimensions, padding, invalid indices/nulls |
| Object-table load/cache/failures | 4,680 | 18 resource scenarios, including the real 1,016-byte table, missing data and truncated prefixes |
| **Total** | **299,377** | **All recorded observation digests and call counts matched** |

The packed-reader probe uses 65,536 header/low-byte combinations, tests both
outputs in each pair, and separately checks failure-state persistence. This is
not all possible byte sequences or stream interleavings. The table probe compares
all resulting arrays, cached image path tokens, call sequences, and decoder state,
then repeats loading without resetting state. Exceptions are compared by type,
not message text or stack traces. Garbage-collection timing is not compared.

No assertion here means every possible input has been tested. In particular,
these probes do not validate real rendering/audio, handset behavior, gameplay,
entity lifecycle, missions, timing, networking, or saves.

## Repeatability and negative controls

Fresh runs `local/component-pass-003` and `local/component-pass-004` produced
**byte-identical component JARs and byte-identical JSON observation reports**.
The JAR SHA-256 is:

`a7a9424c12f4e21c1ee66147c8c2ef613abac2fdb5ab572a2a1d9237386e110f`

Three separate deliberately broken copies were compiled and probed locally.
None replaced the recovered source or was selected as progress evidence:

| Deliberate mutation | Probe detected a difference |
| --- | --- |
| Wrong first-field constructor assignment | Constructors and initial state |
| Wrong fixed-point shift amount | Arithmetic |
| Removed image-cache warming call | Object-table/cache observations |

The public runner also has **15 synthetic/tooling unit tests**, which passed
locally. One compiles the probe and doubles without any game source or binary.
A signature-reader bug encountered in run 001 was fixed before the successful
runs; its regression test covers object-return descriptors ending in semicolons.
These 15 tooling tests are separate from the 299,377 component calls.

## Byte matching and dashboard interpretation

**None of these three whole class files is byte-identical to the original.** The
originals are class-file version 45.3; this component compiler emits version 52.0.
Constant-pool layout, renamed fields and compiler-generated metadata also differ.
The existing normalizer deliberately preserves class versions and identifiers.
No normalization rule was weakened, no original bytecode was copied into a
candidate, and no exact or normalized match is claimed.

The repository-wide byte-match report pointer remains null: this pass reports a
partial component artifact, not a rebuilt game. Consequently byte-match tiles
remain unverified. Recovery tiles for e/s/t can advance to repaired; build tiles
mean the scoped component compilation above; behavior tiles mean only these
recorded component probes. See this report before interpreting a green tile.

## Remaining work

The workstation could not resolve external download hosts or download CFR 0.152;
no decompiler JAR was obtained or executed in this pass. Manual work continued
rather than substituting a pretend successful automated run. A complete automated
pass remains pending, as do the other 18 classes, real platform services, whole-
game rebuilding/comparison, native compilation and gold-release validation.

Preserve these tested snapshots as a regression baseline. Recover the next
components against their original bytecode and connect real dependencies only
when they are implemented. Do not count the test doubles as recovered gameplay.
