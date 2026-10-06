# Integration pass 021 — automated 13-mission simulation stress

The campaign automation now includes deterministic simulation stress for every
mission, not just objective setup/completion and save progression.

## Scope

Each mission runs in a fresh JVM. The probe initializes the real game, selects
the mission, enters world mode through the game's own controller transition, and
then executes **300 real controller/world update frames**.

A deterministic repeating input sequence covers movement and action keys. Every
100 frames the probe records a normalized full game-state hash. It also records
final normalized state plus resource/image and media side-effect hashes.

Retail and rebuilt code run against the exact same authored deterministic Java ME
adapters. Their complete stdout must be byte-identical.

Rendering is deliberately excluded from this direct-selected mission stress path.
The retail renderer expects an interstitial UI state that direct mission selection
does not establish; forcing paint in that invalid state fails on retail too.
Naturally reached rendering remains covered by the accepted startup/menu/gameplay
and production-runtime passes.

## Accepted result

All **13 / 13 missions** matched for **300 frames each**:

**3,900 mission-specific simulation frames total.**

| Mission | Matching output SHA-256 |
| ---: | --- |
| 1 | `60ad39a58131a02b9f2ca66b41121de33cf6e7449b9e9163e157efad91472f7c` |
| 2 | `b944a74aff5ccfbf589dd2d7f217a2184d85eea5b1239df6554b787be9009dfb` |
| 3 | `8a34c226b84e81394978a1cc83b0b4eee0f70db750661947410c6871e8d323c7` |
| 4 | `9b0985287ca5bf0bbca936fe2cc197a62463eac58b5a192ff2da15e69e8af492` |
| 5 | `42588c498817b27b8aebe39936875d9ef41a18dc885a0c1d3300258720603bec` |
| 6 | `a3b5e776383b06d26d691aa5ff491d4075c699a5997634df2bb2365543966c79` |
| 7 | `5e33a75dc66d71d776414b0d9ecc4ef742353659c1afdf8a8266c37b48855516` |
| 8 | `99f7ba0b76aa06c8261799fd85b7b183f233c8ee785cb9bfe82407f61812d09b` |
| 9 | `f6be317359ee3be2e708236ccc35d7997fa8f8a07ab86ac23973466bf4606a82` |
| 10 | `b5d1409415d6668d1ebb7a79561d4e23a52ea60afe45057869729627b224dddf` |
| 11 | `7cb9a2eead10552736b38953be5124297d9922b44d91935032fd6775e049c3b1` |
| 12 | `1d25b76bf6d4e172948237191752fb10c3cfac003a23e8c63f692798ea44239a` |
| 13 | `a35fdeaf81d6904c2c3f34d46424d57881b7cdeac57a2c6b8b8f92d36b4ee458` |

Aggregate concatenated stdout SHA-256:

`aba5560012594e11f19d563f5601d58f40f879bd72cb6dc39c02867613edbca6`

## What this replaces

A human no longer needs to manually poke every mission just to learn whether
routine movement/action simulation immediately diverges, crashes, or mutates game
state differently from retail.

This is still not a substitute for subjective playtesting or for autonomous
navigation from each briefing to objective completion.
