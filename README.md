# Destroy All Humans! Mobile — Decompilation

Faithful, understandable source reconstruction of the **first Java-phone game,
version 1.2.0**, followed by a native Windows port. This is not the Xbox game,
Flash game, mobile sequel, or Crypto Does Vegas.

**Current stage: 17 of 21 original classes manually recovered (151 method entries),
compiled as components, and passing their documented comparisons. No complete
game build or native Windows port exists.**

[**Latest source-recovery results and limitations**](docs/evidence/RECOVERY_PASS_005.md)

## Latest recovery pass

Recovered weapon controller c, saucer/reticle specialization f and GameMidlet
lifecycle forwarding. All seventeen private components compile together.
**24,657 direct new-target calls per side matched**, seven deliberate defects
were detected and all four historical comparison suites passed again. Two fresh
runs reproduced identical component JARs and observation reports. Test actor,
world/controller and platform services remain explicit dependencies, not recovered
systems. Read [pass 005](docs/evidence/RECOVERY_PASS_005.md).

**Pass 005 publication:** this update records the seventeen-class component recovery
and its existing evidence. The Progress dashboard workflow regenerates the maps
and runs the full public tooling suite; consult Actions for the actual result.

## Visual progress

[**Open the visual dashboard**](docs/VISUAL_PROGRESS.md) · [Detailed source map](docs/SOURCE_TREE.md) · [Byte-match policy](docs/BYTE_MATCH.md)

![Source-recovery progress treemap](docs/RECOVERY_TREEMAP.svg)

![Exact-byte and normalized-match treemap](docs/BYTE_MATCH_TREEMAP.svg)

Each rectangle is an original class; its area represents the original method-entry
count. Red in recovery means not recovered. Gray in comparison means unverified,
not failure. Green exact-byte matches and blue normalized matches remain separate
from behavioral accuracy. The dashboard also contains build and behavior views.

**The seventeen local classes have component-level passes.** Their tests use explicit media,
graphics and entity-record support outside the rebuilt artifact; those dependencies
are not implemented game systems. No whole-class exact/normalized match is claimed,
and the global byte-match report remains unselected. Read the linked evidence
before treating a build/behavior tile as a full-game claim.

The images are generated from our recorded evidence, not hand-colored. The
`Progress dashboard` workflow refreshes them on `main` after validation; pull
requests check that generated files are current. No game binary is needed by CI.

## Source tree and progress

Open the **[source tree and implementation map](docs/SOURCE_TREE.md)** for the
actual tracked files, all 21 original classes, and separate recovery, build, and
behavior records. Planned systems are kept separate from implemented tooling.

The map is generated and checked locally:

```console
python tools/source_map.py
python tools/source_map.py --check
```

See [the maintenance guide](docs/SOURCE_MAP_GUIDE.md) before updating statuses.

## Working here

Python 3.10 or newer runs the current tools, with no third-party Python packages.
Run commands from the repository root. On Windows, `py -3` can replace `python`.

```console
python -m unittest discover -s tests -v
```

The tests use independently authored synthetic fixtures. Passing them verifies
parts of the tooling, not the complete game. Some tooling tests use an installed
JDK; actual component comparisons are a separate command with local game inputs.

For the real audit, supply your own exact input at:

```text
inputs/original/Destroy-All-Humans_J2ME_EN_v120.jar
```

That directory is ignored by Git. The tool rejects other builds by size and
SHA-256; the identity and expected counts are in `config/target.json`.

```console
python tools/dah1.py verify
python tools/dah1.py audit --output local/audit.json
```

Alternatively pass `--input "path/to/game.jar"`. An existing output file is never
overwritten; choose a new report name for each run. Auditing parses structure
without extracting or executing game code. It is not a complete JVM verifier.

For the seventeen recovered components, restore the reviewed private source snapshots
under `src/game/`, use a JDK supporting `--release 8`, and choose new run directories:

```console
python tools/weapon_recovery.py --run-dir local/weapon-next-run
python tools/collection_recovery.py --run-dir local/collection-next-run
python tools/entity_recovery.py --run-dir local/entity-next-run
python tools/subsystem_recovery.py --run-dir local/subsystem-next-run
python tools/component_recovery.py --run-dir local/component-next-run
```

The first command compiles seventeen components and compares weapon/saucer/lifecycle
integration. The remaining commands preserve the fourteen-class collection/building,
eleven-class effects/entity/pickup,
six-class audio/font/navigation, and three-class helper regression scopes.
None builds the complete game, downloads a decompiler, uploads game data, or
compiles a native executable. See the reports for exact test boundaries.

## Repository boundaries

- `tools/`, `tests/`: original project tooling and synthetic tests.
- `config/`: exact target identity, source-snapshot hashes and progress metadata.
- `docs/`: status, milestones, and the evidence required for a faithful release.
- `inputs/`, `local/`, `recovered/`, `src/game/`, `deps/`, `build/`: local-only,
  ignored paths. Create them as needed; they are not tracked directories.

This repository was public when initialized. Its visibility was not changed.
No original JAR, asset bundle, disassembly, recovered game source, or third-party
binary is committed. Review publication permissions and repository visibility
before tracking recovered source. No blanket license has been applied to game
material or to dependencies that have not yet been introduced.

## The next milestone

Preserve all seventeen source snapshots and all five probe suites, recover
dependencies, and obtain the decompiler for a complete automated pass when tool access permits. Continue
toward a complete source-only game build without copied original classes or
placeholder gameplay. Real platform services and native compilation remain ahead.

Read [the project status](docs/STATUS.md),
[the verification contract](docs/VERIFICATION.md), and
[the workstation instructions](AGENTS.md) before changing scope or claiming progress.
