# Recovery pass 010 — final UI/state class p repaired

Class **p**, the last raw-output class, has been promoted to a reviewed/repaired
private Java source snapshot. Its **54 method entries** complete the class-recovery
milestone: **21 of 21 original classes / 313 of 313 method entries now have
repaired source records**.

This is a source-recovery milestone, **not** a claim that the complete game has
been behavior-validated, is playable on a production Java ME/Windows platform, or
is byte-identical to the original.

## Reconstruction and review

The accepted source began from hash-pinned **CFR 0.152** output and was
cross-checked against **Vineflower 1.12.0** plus the original class disassembly.
The concrete source repairs in p were Java-representation issues caused by the
obfuscated binary: descriptor-distinguished duplicate field names and image fields
whose names shadow class or method identifiers. Those fields were given explicit
neutral aliases. No new menu, mission, input, rendering, timing or gameplay
algorithm was invented.

The repaired source SHA-256 is:

`3b2455012313a9dbc4b1087c30317d4d84b86508603347b94eba19c1488909ad`

Rebuilt p.class SHA-256:

`b0b0890a8cff3d72205ad79b4f6d19fc90365a5e90cc86245a0ba8e7a702afc5`

Original p.class SHA-256:

`656f3caaab76a056b9810950b4ac7fd51fdd6f0c79026222680cf0f8e4f0e199`

The rebuilt class is **not** byte-identical to the original, and no normalized
whole-class match is claimed. The repository-wide byte-match report remains
unselected.

## Structural build boundary

The isolated rebuilt p preserves **46 fields** and **54 method entries** with the
same descriptor sequences as the original class. It is compiled with authored
Java ME/game support classes outside the rebuilt class under test. A separate
reference runtime loads the original p.class against descriptor-compatible
versions of the same authored support. The candidate runtime contains no original
p.class fallback.

Pass 007 previously established a mechanical all-21-class source-only compile
using raw/repaired decompiler sources. This pass establishes the final p repair in
isolation. A fresh all-21-class compile from the final set of all repaired private
snapshots is still an integration task; this report does not silently substitute
the older raw p or copied original classes for that step.

## Original-versus-repaired observations

Fresh accepted reruns produced identical candidate/reference results in every
recorded group:

| Probe group | Observation records per side | Matching digest |
| --- | ---: | --- |
| Resource/image load and initialization paths | 192 | `98bcccc6d3097cf37d8c8c2b916b4d3852ed74d4ae2fc6c4ff161ffd52c66786` |
| Static helpers and state primitives | 143 | `e18ce89f9612141e7a1989129afa539d3ac4c9616ae67e8ff58e1328ae774116` |
| Private helper methods across representative screen states | 155 | `744995851f82f9aacdc3e346f06cfb58cdc49ee4db11ae924ebcab81665f912f` |
| Public state/screen methods across states 0–25 | 416 | `8572095d0d243703cf0d111b18621853fa85c0d19c95faeaf167dc2cf1cb8014` |
| Randomized navigation/input scenarios | 10,000 | `00359967197e19696a833f8031ac49396bbe9dfba9198fc0aa157743cc289055` |
| **Total** | **10,906** | all groups matched |

Absolute wall-clock timestamps are normalized to relative test-clock values before
comparison. Counts are observation records, not source-line/branch coverage or a
percentage of game accuracy. All callable p methods are directly exercised across
the accepted groups, with the class initializer exercised through loading.

## Negative controls

Seven separately compiled deliberate defects changed the recorded observations:
state-stack increment, transition shift, forced sound toggle, inverted mission gate,
broken navigation wrap, changed starfield modulo width, and a one-pixel prompt
position change.

An earlier repeat-timer mutation was **not** detected by an older navigation
fixture because that fixture did not reach the intended path; it is explicitly
excluded rather than counted. The navigation fixture was strengthened before the
accepted navigation-wrap control was run.

## Remaining integration work

The class-recovery ledger is now **21/21 repaired** and covers all **313 original
method entries**. This closes the per-class source-reconstruction phase.

Still outstanding are a final all-repaired whole-tree integration build,
production Java ME/Nokia platform services, complete original-versus-rebuilt game
execution comparisons, progression/save/audio/rendering validation, native
Windows compilation and a gold-release playtest. Exact/normalized byte matching
remains a separate metric and is not inferred from these behavior probes.
