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

## Not established

- A successful decompiler pass over the complete game.
- Compilable recovered game source or a reproduced JAR.
- Full method-level semantic recovery or readable name mappings.
- Working Java ME/Nokia platform implementations for this project.
- Original-versus-rebuilt execution comparisons, controlled timing, or RNG replay.
- A native compiler proof of concept, Windows executable, or Windows playtest.
- A configured CI workflow. Local tooling tests are not GitHub-hosted CI.
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
