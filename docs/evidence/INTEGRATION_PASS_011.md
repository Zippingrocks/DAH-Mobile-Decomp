# Integration pass 011 — first all-repaired 21-class rebuild and startup/state match

This pass moves beyond per-class recovery. The final repaired private source
snapshots for **all 21 game classes** now compile together from Java source with
no copied original `.class` fallback. The integrated source tree accounts for all
**313 original method entries**.

## Whole-tree build

Two clean compiles of the final repaired source tree produced byte-identical
output for every one of the 21 game classes. The deterministic candidate JAR
SHA-256 is:

`b3e5466c3cb7e0f3e4d3264d612d37cb56418efb4dff745e7bc6f06bad10a381`

The candidate contains exactly **21 rebuilt game classes** plus the original
**122 non-class entries**. Every non-class entry was compared by name and
SHA-256 and is byte-identical to the original archive. No original game class is
present in the candidate.

`javap -p -s` comparisons show that the ordered field-descriptor and
method-descriptor sequences match the original for all 21 classes. The method
total is **313**. Explicit source aliases remain necessary because the obfuscated
binary contains descriptor-distinguished names that Java source cannot express
directly.

## Integration defect caught and corrected

The first integrated render did **not** match the original. Startup, resource
loading, five controller ticks and lifecycle traces matched, but the candidate
produced no drawing calls during the tested paint.

The defect was a source-linkage/shadowing error in `k.paint(Graphics)`: an
earlier naming bridge had produced `graphics = graphics`, while the original
bytecode assigns the incoming argument to the controller's static graphics field.
CFR's unrenamed output and Vineflower both confirmed the intended assignment.
The integrated source was corrected to the explicit equivalent
`k.graphics = graphics`.

After that correction, the original and rebuilt paint traces and pixel digest
matched. This failed pre-fix run is retained as diagnostic evidence rather than
hidden or counted as a pass.

## Original-versus-rebuilt integrated probes

Both sides ran against the same authored deterministic Java ME/Nokia test
adapters. The adapters expose API calls and headless raster results; they are
**not** production platform implementations.

The accepted integration probe performs application construction, controller
private initialization, five controller ticks, an initial paint, lifecycle
start/pause/destroy (with uncontrolled run-thread start deliberately guarded),
and records resource/media/display/lifecycle/paint observations. Its complete
output is byte-identical between original and rebuilt; SHA-256:

`a2a621363ac695d516ff21efa1e43d4c4f05dc4b3c8cd6c270817298751df2ec`

A second state probe deterministically seeds the game RNG, serializes the
game-class state graph by declaration/descriptor order rather than renamed field
names, normalizes only documented wall-clock timestamp fields, exercises five
ticks and a multi-key input sequence, and compares a rendered frame. Original
and rebuilt hashes match at every checkpoint:

| Checkpoint | Matching state/render SHA-256 |
| --- | --- |
| After full initialization | `d56c3777a006dfc19d3bc0813ffb181ac5e11c8aaf162ce3c036722351b9d48f` |
| After five controller ticks | `959ee402f4c9398959c9816dcd5fb8472ff056d2c618d72c0548d6aa32e35e83` |
| After deterministic key sequence | `3dc89f97702325023e6210e795495aa72fbb1686a274459998e84263503ffc32` |
| Headless rendered-frame snapshot | `c1b6c60f888a0a1b5ccd175b305f693049b491037af64ed3b0657b0973dbf52b` |

The state probe's complete four-line output SHA-256 is
`dc01b54d0e53dbb6df2b91ff0c6863e5e9b564ad468e6f005eea38eaaa1a1049`.

Two fresh full runner executions reproduced the same candidate JAR, all 21 class
hashes and both probe outputs.

## Platform boundary discovered during reference execution

Running the original retail classes on the authored desktop test adapters exposed
API-shape gaps that the rebuilt source alone did not: the original bytecode
resolves `Canvas`, `Displayable.isShown()`, and the exact RMS
`enumerateRecords(RecordFilter, RecordComparator, boolean)` descriptor. The
integration adapters were corrected to model those signatures. These are
compatibility-contract fixes, not claims of a complete MIDP implementation.

## What this establishes

This is the first accepted build from the **final all-repaired 21-class source
set**, rather than pass 007's mechanical tree that still contained raw b/k/p
reconstructions. It establishes repeatable compilation, complete class/resource
packaging, descriptor-inventory preservation, and scoped
startup/controller/input/render/lifecycle equivalence under the documented
deterministic adapters.

It does **not** establish complete game equivalence. The real main thread is not
allowed to run freely in these probes, complete missions and save progression
are not replayed, actual handset audio/timing/rendering is not certified, and
the Java ME/Nokia adapters are not production services. Exact/normalized
whole-class byte matching remains separate. Native Windows compilation has not
begun.

## Next integration target

Drive deeper menu-to-game transitions with a controlled frame scheduler and
deterministic input script while recording state, rendering, resource, audio and
persistence events. In parallel, production-grade platform services can begin
behind the same game API boundary without changing recovered game logic.
