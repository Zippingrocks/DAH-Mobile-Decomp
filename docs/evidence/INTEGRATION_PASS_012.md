# Integration pass 012 — RMS round-trip and 500-frame gameplay stress

This pass extends the final all-repaired 21-class integration suite in two directions: persistent save-data semantics and a substantially longer controlled gameplay run.

## Stateful RMS comparison

The authored integration RMS adapter now implements the record-store operations actually used by the game: create/open, delete, add/set/get, enumerate and close. It is deterministic in-memory test infrastructure, **not** the production storage backend planned for the desktop port.

A new `PersistenceProbe` drives the original and rebuilt `k` save/load helpers against this same adapter. Both sides save the complete 82-byte game buffer, restore a deliberately changed buffer byte-for-byte, preserve representative bytes at offsets 0, 17, 80 and 81, reproduce the same RMS call sequence, and produce the same absent-save default initialization with byte 80 = 1.

Complete probe output SHA-256: `91e083590d3838bbf7a3717eeefd96135b1dcef5829410ca5aedb45d9b686ef0`

Saved/restored buffer SHA-256: `f4bcab4c01aaae4d0802ca87e1588374f6d37f2441594aea99ccc7c505829e8a`

Default-buffer SHA-256: `74c3fd89427e31d1f3d11e9ce6ade6f728241a395ebf01834a90835119ce7b19`

## 500-frame controlled gameplay stress

A new `LongRunProbe` performs the established deterministic initialization and default menu-to-world transition, then runs **500 additional gameplay frames**. It applies a deterministic repeating input script covering movement, action/fire and auxiliary keys, invokes the recovered controller/world/actor/weapon update paths, and paints every frame through the shared headless graphics adapter.

Original and rebuilt outputs are byte-identical. Complete ten-line output SHA-256: `38ded5fab464972f8822076a2b71bafe4cf16baa73d98318b6607c8f711ccafc`

| Checkpoint | SHA-256 |
| --- | --- |
| Gameplay start | `d5bf60f4bf9d7d7453efcadb9f71a68be031a79e14034fca3368feefb434d438` |
| Frame 100 | `40d71dde56a046b9767b7a4f2f40502e0611317b85267f0e9db17c4c9b29d4e2` |
| Frame 200 | `47c43fc24a8d63ed0737f10cd9d78830b369860fbab6febafba5f5cfff1946d3` |
| Frame 300 | `ab475d780b11ed0768410584b690effe29647ce34bf65e647444c4fb10c39eb7` |
| Frame 400 | `86603abe4682715da59da9abebc0021f6bc8f4d47e821e07f79e8e3094e75eb1` |
| Frame 500 | `db732881da172068ee71f6892a90443ad6e14c9abcbf9e8932ecb49084e6fb10` |

Final shared-adapter digests also match:

- rendered frame: `e22dca1f5cd4bc5a3049c8bdc3cee5e03cac4f41fcc36c11f63ceffe0132398a`
- image/resource call trace: `367b50307146fcf0c66133c4ae8992764355e8f47677d8a6e904ea7cfbdf3128`
- media call/state trace: `97061b739a95ba9ff9aaee39e3c2c7526d1c23dea2d106f7737962c7493930a7`
- RMS trace: `1e900996cfcba6d65225422a8f0a5d43636ee46e71c90a639daa44c68aefea98`

## Regression and build status

The candidate JAR is unchanged from integration pass 011: `b3e5466c3cb7e0f3e4d3264d612d37cb56418efb4dff745e7bc6f06bad10a381`.

It still contains 21 rebuilt classes and 122 byte-identical non-class entries, with all 313 method descriptors accounted for. The pre-existing startup, state and deep menu-to-gameplay probes continue to match.

## Limits

Five hundred deterministic gameplay frames are stronger than a single-frame smoke test, but they are not a campaign playthrough or branch-coverage claim. The scripted path does not prove every mission, enemy, weapon, save slot, failure mode or UI branch. The RMS implementation here is memory-backed and the media adapter records calls instead of playing audio.

Next work should extend the scripted campaign path across mission transitions and turn the proven API contracts into production desktop storage/audio/window/input services without changing recovered game logic.
