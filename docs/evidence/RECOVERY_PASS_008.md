# Recovery pass 008 — world manager and mission-state core

Class **b** has been promoted from raw decompiler output to a repaired private
source snapshot. It contributes **46 method/constructor/class-initializer entries**,
bringing the reviewed set to **19 of 21 classes / 228 of 313 original entries**.
Classes **k** and **p** remain raw decompiler output and are not counted as repaired.

The repaired b snapshot is based on the pinned CFR pass, cross-checked against
Vineflower and the original javap disassembly. All 93 field declarations and all
46 method entries remain accounted for in original declaration order. The
existing pass-007 descriptor audit still matches every b method and field descriptor.

## Real decompiler defect corrected

CFR duplicated construction in two actor-spawn branches inside the private alert
update routine: it assigned the newly constructed actor to a local variable, then
constructed a second actor solely to set its boolean state. Original bytecode uses
DUP/ASTORE and PUTFIELD on the same instance. Vineflower reconstructed this
correctly. The repaired source now sets the flag on the actor subsequently
inserted into the collection.

## Source-only build boundary

The repaired b compiles in the complete 21-class source-only tree from pass 007.
No original class file is a compiler input or copied into the candidate artifact.
The remaining k/p dependencies in that mechanical whole-tree build are still raw
sources, so this result does not promote either class or establish a playable game.

Two clean compiles produced byte-identical rebuilt class files. Rebuilt b.class
SHA-256: 628df20e948c52ca8146394e587de43b66fe56ad243965d2c9e5be11fe3fd080

Private repaired b.java SHA-256:
9ac9be3553e862b0b046e1732d31d872ee725d81bc7936bda35f11c38dd6aeb8

Original b.class SHA-256:
3373fc290412c49650a9314a970aa92dd15f7dfb89afbb582d0ba867d40e8f3e

The rebuilt class is not byte-identical to the original and no normalized
whole-class match is claimed.

## Differential observations

A reflection-driven probe runs unchanged against the original game classes and
the rebuilt source tree, using the same authored Java ME adapter. Field-layout
guards require all 93 b fields to retain the expected ordered descriptor sequence.

All recorded digests matched across **400,002 observations per side**:

| Group | Calls/observations per side | Scope |
| --- | ---: | --- |
| Static mission table initializer | 2 | Full 52-byte objective table and length |
| Mission success/failure state | 120,000 | Randomized kill/abduction/special counters, objective kinds, thresholds, derived counters |
| Alert transition helper | 100,000 | Prior alert levels, requested levels, timers, signed-byte deltas |
| Visible-cell bounds | 100,000 | Camera offsets, cell sizes and clamped visible grid ranges |
| Cell/collision lookup on empty grids | 80,000 | Coordinate-to-cell mapping, entity-cell mapping and empty collision/ray-query outcomes |

The probe output SHA-256 on both original and rebuilt runs is:
947138b2a0ed19cbdbaa18b47d76e550b7c63bfea49dfdc482e3337171e17fd1

These tests emphasize deterministic world/mission calculations that can be
isolated before the real controller k and script/UI class p are repaired. They do
not claim coverage of full level loading, HUD rendering, mission loop, spawn
scheduling, save integration, or complete world execution.

Three separately compiled negative controls in directly tested paths were
detected: forcing alert deltas to zero, changing the visible-grid lower clamp,
and using the wrong cell dimension in coordinate lookup. A fourth attempted
mission-threshold mutation did not alter the randomized digest and is therefore
**not counted** as a successful negative control.

## What remains

b is now repaired and has a successful source-only build plus a scoped behavior
pass. k and p remain raw. Full level loading and main-loop integration still
depend on repairing those two classes and production Java ME/Nokia services.
There is no playable complete rebuild, exact/normalized whole-class match, or
native Windows executable yet.
