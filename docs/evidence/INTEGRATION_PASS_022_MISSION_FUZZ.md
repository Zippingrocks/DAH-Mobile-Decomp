# Integration pass 022 — multi-seed mission differential fuzzing

The per-mission simulation stress now includes multiple independent deterministic
input/RNG seeds instead of one scripted pattern.

## Matrix

Every one of the 13 missions was executed in a fresh JVM for four seeds:

`1, 3, 13, 34`

Each mission/seed pair ran **150 real controller/world update frames** after
entering world mode through the game's own controller transition.

The input generator independently chooses among press, release, release-all and
no-op operations across movement, action and soft keys. The game RNG is reset from
the same seed on retail and rebuilt sides. Full normalized state checkpoints are
captured every 50 frames, with final state plus resource/image and media side
effects included in the observation.

That is:

- 13 missions
- × 4 seeds
- × 150 frames
- = **7,800 additional mission-specific simulation frames**

Retail and rebuilt complete outputs matched for every mission/seed pair.

## Per-mission aggregate hashes

| Mission | SHA-256 across its four seeded runs |
| ---: | --- |
| 1 | `e12a5b1b252fdc49e6862855c8323e1894dfe8c0f58a9fc995cf549675d9fa6d` |
| 2 | `e37552d1906b42c466143a07190230aeca17002209d11f49597387024e8071c8` |
| 3 | `9e644dd2c649d8b27ea383b732fa1468bc7201ea8048cb93d1ee24057597673e` |
| 4 | `76defe0c415ae5a05c49f2be1df3ff2f87e00390f150f59c62db74b500ba717a` |
| 5 | `60bcca66a54b05b9ef55bd65207c1344c098e2999bdc1dac2f85d24300507396` |
| 6 | `d6c8bee2d157aae60df924be644d02140b5609f8011cd6aaaf6e148156cb7244` |
| 7 | `c9df7ff2e1732659a7df229e2972b859972e217f2136e82d6aa376e92e546d6e` |
| 8 | `d83644715fec0d0f5615df51d90bd4fa3c2fb96067072bf49576a8b94fe60020` |
| 9 | `0f31b4353ff71eaf8ef5bd3cdb9e18882a33a2979c2f8534bf316e93b2821f83` |
| 10 | `090633db3e98cd639fa7051a4311d309a26c762f25bd33117b13dc7139095809` |
| 11 | `804954adde4bcc2dbd44ead4047c76a01c5c8fa36c00b2c76a99c6deeb112326` |
| 12 | `0c0a75d272aac12d92649b9288e3f679a567d81305fd9ea95d8dfcb370f56fdb` |
| 13 | `20ccf4156cdfc2938f50924635b19bf320c482881946338b1b2bb4c7f8a50f44` |

SHA-256 of the concatenated per-mission aggregate hashes:

`521df370f487e06dc1e2064d08ac8390d8d6c7eae9ec03f98ba23a8407af3dc3`

## Purpose and boundary

This substantially increases machine-driven state-space coverage before human
playtesting. It is still deterministic differential fuzzing, not proof that every
possible key schedule, RNG stream, or campaign branch has been explored.

Rendering remains validated through naturally reached controller/UI paths rather
than forced direct-selected mission paint states.
