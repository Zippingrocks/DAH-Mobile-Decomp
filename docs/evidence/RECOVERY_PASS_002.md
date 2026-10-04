# Source recovery pass 002 — audio, bitmap text and navigation components

This pass adds complete local source for **g (11 method entries), l (14), and q
(14)**, manually reconstructed against the exact original bytecode. Combined
with unchanged e/s/t, **6 of 21 classes / 58 of 313 method entries** now have
compiling component sources. The other 15 classes / 255 entries remain
unrecovered. These counts are not a percentage of game accuracy or completion.

## What was recovered

| Class | Established responsibility | Local source |
| --- | --- | --- |
| g | Sound-resource loading, format fallback, player lifecycle and event handling | src/game/g.java |
| l | Bitmap-font metrics, encoded text tables, width/number formatting and text layout/draw calls | src/game/l.java |
| q | Coordinate/link navigation tables, neighbor selection, spatial queries and viewport filtering | src/game/q.java |

Numeric direction encodings in q remain numeric; no new pathfinding algorithm
has been substituted. Source names and original descriptors are mapped in
`config/subsystem_recovery.json`. In addition to field collisions, l has two
return-type-only method overloads not legal in Java source: a(II)B becomes
encodedByte(II)B, and b(II)B becomes glyphOffsetByte(II)B. Their integer-returning
counterparts retain their original names. The runner compares all 58 method
entries in declaration order after applying only those explicit method aliases.

The e/s/t sources retain the exact source hashes from pass 001. Public files are
new tools, probes, test adapters, source hashes and reports. **The original JAR,
resources, disassembly and recovered game source are not publicly committed.**

## Real compilation, limited component boundary

`tools/subsystem_recovery.py` verifies the original input, six source snapshot
hashes, original class hashes and an allowlist of resource hashes. It compiles
public test support separately, then uses `javac --release 8 -g:none
-implicit:none` with an empty sourcepath to compile the six actual sources.
The recovered compiler classpath contains test support, never the original JAR.

The deterministic output `rebuilt-components.jar` contains exactly e.class,
s.class, t.class, g.class, l.class and q.class. It contains **no test double and
no original compiled class**. Original classes are loaded only by the separate
reference JVM from reference-only.jar. Both sides execute on the same installed
OpenJDK/javac 21.0.11 Linux environment, with headless graphics.

The following remain test infrastructure, NOT recovered platform/game systems:

- The media interfaces/Manager record calls, provide scripted player states and
  inject one-shot failures. They do not decode or play sound, model asynchronous
  device scheduling, or establish Java ME audio compatibility.
- The Image/Graphics test adapter decodes the original font PNG using ImageIO
  and rasterizes only the exercised TOP|LEFT font draws on a 176-by-208 test
  surface. Command sequences, resulting clip state and pixel digests are compared.
  This is not a full MIDP graphics implementation or a native Windows renderer.
- b/k/j/f/o are authored test records supplying controlled viewport values,
  positions, actor references and random input. Those classes stay unrecovered.
  The reference b/k doubles need duplicate field names with different descriptors;
  the runner rewrites only name constants in those **authored doubles**, never
  in an original game class. Candidate doubles use the mapped field names.

## Comparison results

Machine-readable results: [subsystem-pass-002.json](subsystem-pass-002.json).
All listed original/recovered observation digests and call counts matched.

| Observation group | Calls per side |
| --- | ---: |
| Audio resource fallback, direct reads and resize/partial-state behavior | 63 |
| Scripted audio lifecycle sequences | 14,160 |
| Audio fault/state matrix | 1,355 |
| Font construction and partial resource reads | 381 |
| Encoded text-table loading and failures | 84 |
| Number formatting and shared scratch-buffer behavior | 14,281 |
| Text measurement and token access | 13,540 |
| Original English text raster and drawing-command comparisons | 404 |
| Text layout boundaries and exceptions | 1,303 |
| Navigation loading and retained partial state | 1,486 |
| Packed links and supplied random-selection inputs | 100,025 |
| Spatial queries, viewport edges and fallback selection | 25,088 |
| **Total for new subsystem probes** | **172,170** |

The font raster group includes 402 draw invocations (three entry points for each
of 134 text entries), plus construction and table loading. The count is calls,
not pixels, source coverage or independent gameplay scenarios. Font probes also
exercise every truncated prefix of the 356-byte metric file, signed length
failures, character-map bounds, multiline early returns, invalid glyphs and
injected drawing errors. Exceptions are compared by type, not message/stack.

Audio probes cover AMR/WAV/MIDI fallback, resize shrink failures, loop settings,
stop/reset sequences, literal versus newly allocated error-event strings, null
players and one-shot faults. They do not establish real sound output, lock
scheduling or behavior under permanently failing player implementations.

Navigation probes use independently constructed tables, not a parsed original
level. They cover partial stream reads/decoder state, all byte values in packed
link slots, supplied random integer boundaries, tie/order behavior, camera
boundaries, null actors, invalid links and the signed-byte iteration limit.
Traversal tables are deliberately acyclic; arbitrary cycles and nontermination
have not been exhaustively tested. No original control-flow guard was added to
make such cases look successful.

## Preserved quirks and negative controls

These details were retained rather than silently fixed:

- Audio error events use reference equality against the literal error string.
- A font multiline early-return path does not restore the prior clip rectangle.
- Navigation selection preserves its original rejection order, signed byte
  conversions and remainder-based random choice; it is not replaced by a modern
  library random-choice or distance/pathfinding function.

Three independently compiled, deliberately broken private copies were rejected:

| Mutation | Groups detecting the difference |
| --- | --- |
| Change audio event reference equality to String.equals | Scripted audio lifecycle |
| Restore the clip on the original font early-return path | Original text raster/commands; layout boundaries |
| Change navigation reverse-direction rejection | Packed-link/random selection |

None of these mutated sources replaced a recovered source or became evidence of
recovery. Their logs remain in the private checkpoint. These controls test that
our comparisons can detect representative changes, not all possible defects.

## Reproducibility and existing regressions

Fresh runs `local/subsystem-pass-001` and `local/subsystem-pass-002` produced
byte-identical component JARs and observation JSON. The six-class JAR SHA-256 is:

`5305b3346e7bd204aaf867d733543a6eb5cdb85387ffe87f221452ff7ef0a57c`

The earlier e/s/t probe suite was rerun separately as
`local/component-regression-005`: **299,377 calls per side again matched**.
The two suites have different scopes; do not portray either as a whole-game test.

The 15 existing component-tool tests plus 15 new subsystem-tool tests passed
locally (30 total). The new tests cover explicit method aliases, authored-double
name rewriting, malformed constants, resource allowlists, deterministic fixture
creation and compilation of all public probes without game files. Hosted CI
also runs the pre-existing dashboard/audit/matcher tests; its actual result is
recorded in Actions, not inferred from the local subset.

```console
python tools/subsystem_recovery.py --run-dir local/subsystem-pass-001
python tools/subsystem_recovery.py --run-dir local/subsystem-pass-002
python tools/component_recovery.py --run-dir local/component-regression-005
python -m unittest discover -s tests -p 'test_*recovery.py' -v
```

## Fidelity and remaining work

All six rebuilt class files differ from the originals: the original headers are
45.3 and these component outputs are 52.0, with explicit identifier changes and
compiler differences. No exact or normalized whole-class match is claimed. The
existing matching policy is unchanged and the game-wide report pointer remains
null. Byte-match tiles therefore remain unverified, not artificially green.

This pass advances g/l/q to repaired-source, component-build and scoped-behavior
states, backed by this report. **There is still no playable rebuilt game, no
whole-game comparison, no native Windows port and no unconditional fidelity
claim.** The unavailable external decompiler download was retried and still
failed; no automated decompiler output has been invented. Manual recovery is the
actual approach used so far.

Next priorities are the real base entity/dependent actors and main loop, actual
platform services, larger integration tests, a complete source-only JAR and only
then native compilation/whole-game validation. Retain these six sources and both
probe suites as regression baselines while doing that work.

API shape references for the independently authored test support:
[Oracle MIDP Player](https://docs.oracle.com/javame/config/cldc/ref-impl/midp2.0/jsr118/javax/microedition/media/Player.html)
and [Oracle MIDP Graphics](https://docs.oracle.com/javame/config/cldc/ref-impl/midp2.0/jsr118/javax/microedition/lcdui/Graphics.html).
These references do not certify our partial adapters as compliant implementations.
