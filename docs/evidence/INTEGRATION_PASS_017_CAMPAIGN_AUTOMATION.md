# Integration pass 017 — automated 13-mission campaign matrix

The direct-load mission matrix is now a repeatable public validation workflow
instead of a one-off private investigation.

## Validator design

`tools/campaign_validation.py` compiles an authored reflection probe against the
public desktop runtime, then launches **a fresh JVM for every mission and every
side**. Fresh processes prevent static game state from leaking from one mission
into another.

For each of the 13 missions, the probe:

1. constructs the real game/controller,
2. performs deterministic resource initialization,
3. seeds the game RNG deterministically,
4. selects and loads the real mission/map resources,
5. records the authored objective tuple,
6. records the runtime objective target and dynamic entity total,
7. records the initial completion gate,
8. fulfills the objective through the corresponding runtime counter,
9. verifies the resulting completion state and progress counter,
10. hashes the complete observation line.

The Python runner executes the same probe against the retail JAR and rebuilt
desktop JAR, requires byte-identical output, and checks the retail output against
the pinned expected matrix in `config/campaign_matrix.json`.

## Accepted real-game run

All **13 / 13 missions** matched retail vs rebuilt. Aggregate concatenated probe
output SHA-256:

`36e32e9d96cabbb894d9090904b21f5053ef0c02a83271d849e499e100afb3b9`

The matrix preserves several non-obvious runtime facts:

- Mission 4's counter gate is initially satisfied by its zero authored target.
- Mission 7's authored threshold is 20 but its runtime objective target is the
  dynamically loaded total **29**.
- Mission 12's authored threshold is 15 but its runtime target is the dynamically
  loaded total **30**.
- Missions 8, 9 and 13 remain pinned as regressions for the previously discovered
  actor-byte field binding defect.

Every mission reached the expected completion result after the probe fulfilled
its actual objective counter.

## Usage

With private reviewed source available, the validator can build its own desktop
candidate:

```console
python tools/campaign_validation.py \
  --input inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar \
  --source-dir src/game \
  --report local/campaign-matrix.json
```

Or validate an already-built desktop JAR:

```console
python tools/campaign_validation.py \
  --input inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar \
  --candidate dist/DAH-Mobile-Desktop.jar
```

This automates the campaign-definition/objective regression. It is not a claim
that an AI has physically navigated every mission from briefing to ending without
direct state setup. Longer end-to-end play scripts remain a separate target.
