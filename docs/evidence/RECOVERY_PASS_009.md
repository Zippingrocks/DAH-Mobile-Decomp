# Recovery pass 009 — controller input, timing and persistence primitives

Class **k** is promoted from raw decompiler output to a repaired private source
snapshot. Its **31 entries** bring the reviewed set to **20 of 21 classes / 259
of 313 original method entries**. Only **p (54 entries)** remains raw.

The source is the pinned CFR reconstruction cross-checked against Vineflower and
original javap disassembly. No additional semantic decompiler defect was found in
the reviewed controller methods. Several oddities are intentionally preserved,
including repeated timestamp writes in resume paths and the original busy-wait
frame limiter.

k compiles in the complete source-only tree with no copied original class files.
Its private source SHA-256 is
2d8123e9e45bbf84563a4be3ffaa4f6a8e8bfbefa475dd6e407f84e243e614f2.
The rebuilt class SHA-256 is
b75ac7aa5ae87ea9112883e1288c439da7bd2f6c97c9ce543d2ab0ee08e58c4f,
while the original class SHA-256 is
b13005813e9821ffb5dd2d9a5ca454c47334bc7e7800b3b4067bfdf675382085.
No byte-identical or normalized whole-class match is claimed.

## Differential scope

An unchanged reflection probe ran against original and rebuilt classes with the
same authored Java ME graphics adapter. All **434,002 observations per side**
matched:

| Group | Observations per side | Scope |
| --- | ---: | --- |
| Static initialization | 2 | save-buffer length/defaults, frame-delay default, RNG presence |
| Key press/release and frame-state transitions | 160,000 | numeric/soft/game-action key masks, held/not-held/edge queries |
| Little-endian save helpers | 120,000 | randomized offsets and integer values, short round trips and byte layout |
| Edge-mask transition algebra | 150,000 | randomized pending/previous bitfields and query masks |
| Image draw helper | 4,000 | draw-count increments plus shared-adapter command/pixel snapshots |

Original and rebuilt probe output SHA-256:
5ab6b8c9a01665443908c55a0a726bd2694195d244e6b6923cc912c74e96f668

Four separately compiled negative controls were detected: wrong numeric-key bit,
wrong save-byte order, altered edge-mask formula and doubled draw-count increment.

This scoped pass does **not** validate the full run loop, menu state machine,
record-store behavior, pause/resume scheduling, frame timing on a handset, or
production Java ME services. Those areas remain integration targets even though
the source is now repaired.

With k promoted, p is the final class still at raw-output status. There is still
no complete behavior-validated playable game or native Windows executable.
