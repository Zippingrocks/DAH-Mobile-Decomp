# Destroy All Humans! Mobile — Decompilation

Faithful, understandable source reconstruction of the **first Java-phone game,
version 1.2.0**, followed by a native Windows port. This is not the Xbox game,
Flash game, mobile sequel, or Crypto Does Vegas.

**Current stage: all 21 original classes are repaired and the final all-repaired tree has a repeatable 21-class source-only integration build. The original and rebuild now match through startup, menu→gameplay transition, save/load round-trips, and a 500-frame deterministic gameplay stress run with state, rendering, media-call and RMS checkpoints. A direct-load 13-mission matrix also matches after correcting a hidden actor-field binding bug. The deterministic startup/state/menu→gameplay/save/500-frame regressions and clean-build repeatability have now been independently replayed successfully; the interrupted production-desktop 300-frame rerun has now also been recreated and matched. A reproducible authored desktop runtime and desktop-JAR build path now exist; complete campaign playtesting, subjective audio playtesting and the native Windows AOT port remain ahead.**

[**Latest native-AOT preparation**](docs/evidence/INTEGRATION_PASS_018_NATIVE_AOT_PREP.md) · [**Campaign automation evidence**](docs/evidence/INTEGRATION_PASS_017_CAMPAIGN_AUTOMATION.md) · [**AMR audio evidence**](docs/evidence/INTEGRATION_PASS_016_AMR_AUDIO.md) · [**Desktop build evidence**](docs/evidence/INTEGRATION_PASS_015_DESKTOP_BUILD.md) · [**Desktop runtime build guide**](docs/DESKTOP_RUNTIME.md) · [**Desktop-runtime fidelity evidence**](docs/evidence/INTEGRATION_PASS_014_DESKTOP_RUNTIME.md) · [**Restored regression evidence**](docs/evidence/INTEGRATION_PASS_013_REGRESSION_RESTORE.md) · [**Campaign checkpoint**](docs/evidence/INTEGRATION_PASS_013_CHECKPOINT.md) · [**Latest completed integration evidence**](docs/evidence/INTEGRATION_PASS_012.md) · [**Final class recovery**](docs/evidence/RECOVERY_PASS_010.md)

## Latest integration work

The **final all-repaired 21-class source tree now compiles together** with no copied original classes. Two clean builds are byte-repeatable, all 313 ordered method descriptors match the original, and the candidate packages all 122 original non-code entries byte-for-byte. Original and rebuilt startup, initialization, five ticks, deterministic input/state checkpoints, lifecycle events and the tested rendered frame match under the shared deterministic adapters.

The reproducible integration runner now also validates the game's RMS save/load semantics and a 500-frame deterministic gameplay stress sequence after entering world mode. State checkpoints at 100-frame intervals, final rendering, image/resource calls, media calls and RMS activity all match the original. The RMS adapter is intentionally in-memory test infrastructure, not the production storage backend. Read [integration pass 012](docs/evidence/INTEGRATION_PASS_012.md) and [integration pass 011](docs/evidence/INTEGRATION_PASS_011.md).

## Visual progress

[**Open the visual dashboard**](docs/VISUAL_PROGRESS.md) · [Detailed source map](docs/SOURCE_TREE.md) · [Byte-match policy](docs/BYTE_MATCH.md)

![Source-recovery progress treemap](docs/RECOVERY_TREEMAP.svg)

![Exact-byte and normalized-match treemap](docs/BYTE_MATCH_TREEMAP.svg)

Each rectangle is an original class; its area represents the original method-entry
count. Red in recovery means not recovered. Gray in comparison means unverified,
not failure. Green exact-byte matches and blue normalized matches remain separate
from behavioral accuracy. The dashboard also contains build and behavior views.

**Twenty classes now have repaired source and scoped build/behavior evidence; p
remains raw decompiler output only.** Test support remains separate from rebuilt
artifacts. No whole-class exact/normalized match is claimed, and the global
byte-match report remains unselected.

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

The authored desktop runtime and reproducible desktop-JAR packager are tracked publicly. All four retail AMR effects are converted/routed automatically, and the full 13-mission objective/completion matrix is now a one-command retail-vs-rebuilt regression. The remaining human work is increasingly limited to subjective listening and hands-on play; automated end-to-end mission scripts and desktop polish checks remain active engineering targets; the Windows AOT build commands, direct entry point, tracing-agent pass and native-image invocation are now scripted, but the actual `.exe` still requires execution on a suitable Windows GraalVM/MSVC build host.

Use the new reproducible integration runner to expand deterministic menu→gameplay scripts into longer mission sequences while comparing state, rendering, media calls and persistence. In parallel, replace the authored test adapters with production Java ME/Nokia-compatible services behind the same recovered API boundary, then proceed toward complete-game validation and native Windows compilation.

Read [the project status](docs/STATUS.md),
[the verification contract](docs/VERIFICATION.md), and
[the workstation instructions](AGENTS.md) before changing scope or claiming progress.
