# Destroy All Humans! Mobile — Decompilation

Faithful, understandable source reconstruction of the **first Java-phone game,
version 1.2.0**, followed by a native Windows port. This is not the Xbox game,
Flash game, mobile sequel, or Crypto Does Vegas.

**Current stage: verified input and structural-audit tooling. No recovered game
source has been compiled. No game behavior or native port is verified.**

## Visual progress

[**Open the visual dashboard**](docs/VISUAL_PROGRESS.md) · [Detailed source map](docs/SOURCE_TREE.md) · [Byte-match policy](docs/BYTE_MATCH.md)

![Source-recovery progress treemap](docs/RECOVERY_TREEMAP.svg)

![Exact-byte and normalized-match treemap](docs/BYTE_MATCH_TREEMAP.svg)

Each rectangle is an original class; its area represents the original method-entry
count. Red in recovery means not recovered. Gray in comparison means unverified,
not failure. Green exact-byte matches and blue normalized matches remain separate
from behavioral accuracy. The dashboard also contains build and behavior views.

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
parts of the audit tool, not the original game or a decompilation.

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

## Repository boundaries

- `tools/`, `tests/`: original project tooling and synthetic tests.
- `config/`: exact target identity and baseline structural counts.
- `docs/`: status, milestones, and the evidence required for a faithful release.
- `inputs/`, `local/`, `recovered/`, `src/game/`, `deps/`, `build/`: local-only,
  ignored paths. Create them as needed; they are not tracked directories.

This repository was public when initialized. Its visibility was not changed.
No original JAR, asset bundle, disassembly, recovered game source, or third-party
binary is committed. Review publication permissions and repository visibility
before tracking recovered source. No blanket license has been applied to game
material or to dependencies that have not yet been introduced.

## The next milestone

Obtain and pin the decompiler and Java ME library definitions, recover source
locally, then attempt a clean rebuild. Record compiler errors rather than hiding
them behind copied original classes or placeholder gameplay.

Read [the project status](docs/STATUS.md),
[the verification contract](docs/VERIFICATION.md), and
[the workstation instructions](AGENTS.md) before changing scope or claiming progress.
