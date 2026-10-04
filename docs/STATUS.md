# Project status

## Established in the initial repository setup

- Target: the first mobile game, English v1.2.0.
- Exact input: 201,816 bytes; SHA-256 is pinned in `config/target.json`.
- A new structural audit run reproduced: 21 classes; 313 method entries,
  including 23 constructors and 12 class initializers; 119,140 class-file bytes;
  54,035 method-bytecode bytes; zero native methods in the game's own classes.
- Python input verification and structural auditing are implemented.
- All 13 synthetic unit tests passed locally; they require no original game files.
- Two successive real-input audits produced byte-identical JSON reports.
- Original inputs and the full local audit remain outside Git.

These numbers are counts, not decompilation completion or accuracy percentages.
The bytecode count excludes assets, metadata, and external runtime services.

## Source-tree map implemented

- `docs/SOURCE_TREE.md` is a generated map of every tracked file, with a purpose
  register and the 21 original classes tracked separately from project tooling.
- `config/source_map.json` records recovery, source-only build, and behavior
  independently. All game-class states remain not started/not tested.
- `tools/source_map.py --check` checks file coverage, safe paths, stage/evidence
  consistency, configured counts, and generated-document freshness. Evidence
  metadata is not a proof of the underlying claim.
- The optional audit comparison matched every class and method-entry count to a
  fresh audit of the hash-verified original: 21 classes and 313 method entries.
- All **37 local tooling tests** passed: the original 13 plus 24 map tests.
  These require no original game files. They cover stale output, missing file
  metadata, unsupported status claims, stage ordering, evidence requirements,
  inventory mismatches, deterministic rendering, and exclusion of ignored inputs.
- The README links directly to the map. `docs/SOURCE_MAP_GUIDE.md` and `AGENTS.md`
  explain how to keep it current. No hosted automation was configured.

```console
python tools/dah1.py audit --output local/audit-source-map.json
python tools/source_map.py
python tools/source_map.py --check --audit local/audit-source-map.json
python -m unittest discover -s tests -v
```

The source tree and class register are progress reporting, not new recovered
game code. No original binary, asset, disassembly or recovered source is published.

## Visual dashboard and byte comparison implemented

- The README now embeds real SVG recovery and byte-match treemaps; the visual
  dashboard includes source-only build and behavior views as well.
- Each rectangle corresponds to an original class and has area proportional to
  its original method-entry count. Recovery remains 0/21, build passes 0/21,
  behavior passes 0/21, and byte comparisons unverified 21/21.
- A conservative actual JAR comparison tool distinguishes entire-class exact
  bytes, normalized structure, known structural differences and unverified data.
  No DAH rebuilt JAR or gameplay comparison is claimed.
- The generator reads the repository's existing nested evidence schema. It
  validates the source map, gates positive matches on source-only build records,
  and marks comparison reports stale when their recorded context changes.
- The workflow definition checks pull requests and refreshes generated dashboard
  files on main. A workflow definition is not evidence of a hosted passing run;
  consult Actions for the actual result. It never uploads or fetches game data.

- All **68 local tooling tests** passed in this change: the original 37, plus
  19 comparison and 12 treemap tests. The installed-JDK fixture test ran, not
  skipped. SVGs were rendered and visually inspected for label/legend overlap.
- All 21 original class structures were accepted by the normalizer in a local
  diagnostic. Original-vs-original byte equality was checked only as a tool
  diagnostic and is NOT selected as progress evidence. The report pointer
  remains null; no recovered game code or rebuilt game is claimed.

```console
python tools/source_map.py
python tools/treemap_dashboard.py
python tools/source_map.py --check
python tools/treemap_dashboard.py --check
python -m unittest discover -s tests -v
```

## Not established

- A successful decompiler pass over the complete game.
- Compilable recovered game source or a reproduced JAR.
- Full method-level semantic recovery or readable name mappings.
- Working Java ME/Nokia platform implementations for this project.
- Original-versus-rebuilt execution comparisons, controlled timing, or RNG replay.
- A native compiler proof of concept, Windows executable, or Windows playtest.
- Any unconditional 100% fidelity claim.

## Commands exercised on the supplied input

```console
python tools/dah1.py verify
python tools/dah1.py audit --output local/audit-initial.json
python -m unittest discover -s tests -v
```

The audit is read-only with respect to the JAR and does not execute game code.
The parser is deliberately a bounded structural auditor, not a complete bytecode
verifier. Unit fixtures do not establish that every class-file format is supported.

## Next concrete work

1. Pin and obtain a Java decompiler and the required Java ME/Nokia definitions.
   Earlier attempts to obtain CFR failed; no download success is assumed here.
2. Generate raw recovered source in a local-only directory and save tool logs.
3. Compile without substituting original game classes. Inventory every error.
4. Establish original/rebuilt test runs before refactoring or porting.

Native compiler selection is deferred until compatibility is demonstrated.
Keep the public repository tooling-only until source publication is addressed.
