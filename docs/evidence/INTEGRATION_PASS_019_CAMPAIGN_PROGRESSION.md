# Integration pass 019 — automated mission-to-mission save progression

The campaign validator now goes beyond direct mission loading. This pass exercises
the game's **actual mission-complete and RMS persistence path** across the entire
13-mission campaign.

## Test shape

A single-process attempt was rejected because the real game deliberately enters an
intermission/UI state after mission completion. Forcing the next mission load in
that same frame context was not representative.

The accepted automation therefore uses a more faithful save/resume model:

1. launch a fresh JVM for mission 1,
2. initialize the real game/controller,
3. load the mission selected by the current save state,
4. mechanically fulfill that mission's actual runtime objective,
5. require the real completion predicate,
6. call the real mission-complete routine,
7. let the game update and persist its 82-byte save state through file-backed RMS,
8. exit,
9. launch a fresh JVM for the next mission using the same RMS directory.

Retail and rebuilt code use separate RMS directories, but after **every mission**
their concrete RMS files must be byte-identical.

## Accepted 1 → 13 progression

All thirteen retail/rebuilt step outputs match exactly, and the disk-backed RMS
files match after every step.

| Mission | Runtime target | Mission after completion | Save-buffer SHA-256 |
| ---: | ---: | ---: | --- |
| 1 | 10 | 2 | `7d85c01bab4347ea691abe236d194a2a90e8aa0e98c032103b8e12e27516b552` |
| 2 | 10 | 3 | `c81403ce0dd67c0601c07eba980cf2b7ac743bd339ca01ccf90d1bcf359e0a68` |
| 3 | 10 | 4 | `3b96a547b0e91a33fdd7bb699501639fe27fb0e6a4d1910d9af57642ca7ccca2` |
| 4 | 0 | 5 | `8d22c319ad241caf7f782cf76c5e09585ec4b09d05af40c42e65b8d0c5c94e5d` |
| 5 | 8 | 6 | `0e293d989f8a3b4711f6f81f82f4e809ec69b34e997ba6e64e582e892e0e1a32` |
| 6 | 15 | 7 | `9a9e5e7e9e0e6802abef2fdd3affb7bde4e9cb7eabeccce3bfce662f52833c5d` |
| 7 | 29 | 8 | `e7f71ca92c125fcd34dc56d5103845cf1ead9bdc86f0cfa5b7befbc16c7aa4b4` |
| 8 | 6 | 9 | `6fb792cfc6da0042de042a4306001f60c0776fb924b3fed728892f3d236b21ed` |
| 9 | 8 | 10 | `12c87b4856d80bfd85c57ec3603318e0306097bd34415f02119c9dd9227dd0d5` |
| 10 | 10 | 11 | `cd00109dd881d928673bebe1b35d0685e6af7cf4fcfb765fc0247b60ed8c7748` |
| 11 | 15 | 12 | `efc234b1f1bfacae191bf7f549714f07ffd0052a5f6947c7e67e7e4d923928f9` |
| 12 | 30 | 13 | `3fae88353e6c15915e598ef0694101e0860a024a909dc60ff420a1c9f364fd71` |
| 13 | 1 | 13 | `3fae88353e6c15915e598ef0694101e0860a024a909dc60ff420a1c9f364fd71` |

Aggregate concatenated stdout SHA-256:

`02a4d6dab556e8fca05eb56bee3959a88a58b062c2d19bcfd65652d840449286`

Final actual `DAH.rms` file:

- bytes: **90**
- SHA-256: `b4fbb6743d71916be57ab6fc879306f9421cbb2747de296b1c8400e657339f23`

Mission 13 intentionally remains at mission index 13: the final completion enters
the ending path rather than persisting a nonexistent mission 14.

## Automation

`tools/campaign_progression.py` can either build its own desktop candidate or
accept an existing one. It launches a fresh JVM per mission, keeps RMS persistent
across steps, compares retail/rebuilt stdout and concrete save files after every
mission, checks all pinned rows, and verifies the aggregate/final hashes.

This removes manual save-chain verification from the human checklist.

## Limits

This verifies real mission progression and persistence but still fulfills mission
objectives mechanically rather than navigating Crypto through every map. Human
playtesting is still valuable for subjective controls/presentation and discovering
issues outside the scripted objective path.
