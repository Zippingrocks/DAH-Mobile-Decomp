# Byte-match and normalized-match policy

The visual dashboard has a dedicated **byte-match** view. It does not combine
recovery, compilation, binary comparison, and game accuracy into one score.

| Color | State | Exact meaning |
| --- | --- | --- |
| Green | Exact class-file bytes | The entire original and candidate `.class` byte strings are equal. |
| Blue | Normalized structure | Both supported class representations match under the policy below. This is not exact-byte equality. |
| Red | Known structural differences | The supported normalized representations differ. This is not automatically a gameplay defect. |
| Gray | Unverified | No comparison, missing candidate, unsupported normalization, stale report, or no source-only build evidence for a positive result. |

Each rectangle currently represents **one original class**, weighted by its
method-entry count. It is not line coverage, a method-by-method heatmap, or an
estimate of percentage game accuracy. Detailed method results are included in
supported non-exact class comparison reports, but the SVG aggregates by class.

## Real comparison command

Supply the pinned original JAR locally and a candidate JAR built from recovered
source. The tool does not decompile, build, run, or upload them:

```console
python tools/byte_match.py --rebuilt build/rebuilt.jar --output local/match-001.json
```

`--original path/to/game.jar` optionally selects a different local path to the
**same hash-pinned input**. Existing report files are never overwritten. The
original and candidate archives are structurally audited, bounded in size, and
read without extracting their contents to disk. Reports contain identifiers,
hashes, counts, states and explanations, not bytecode or asset contents.

For a public dashboard, review the report, copy its metadata to a tracked path
such as `docs/evidence/match-001.json`, add that path to the `files` register in
`config/source_map.json`, and set `config/byte_match.json`'s `report` field to it.
Do not commit the JARs, game assets, or disassembly. Record source-only rebuild
and recovery evidence **before** generating the comparison report.

The configuration initially selects **no report**. The first real game's
source-only rebuild does not exist yet, so all its match tiles are unverified.
A self-comparison or a synthetic fixture run must never be selected as game
recovery evidence.

## Normalization v1: intentionally conservative

`tools/classfile.py` implements `dah-class-normalization-v1` for the supported
subset of class-file versions 45 through 52. It:

- Resolves constant-pool references to their typed values and referenced symbols,
  including field/method descriptors. Pool reordering is not mistaken for a code
  difference, and changed referenced constants are not mistaken for a match.
- Ignores only the named debug attributes `SourceFile`, `SourceDebugExtension`,
  `LineNumberTable`, `LocalVariableTable`, and `LocalVariableTypeTable`, plus
  unused constant-pool entries. Debugging metadata is outside the match scope.
- Normalizes `ldc`/`ldc_w` and wide jump encodings and represents branch, switch,
  exception-handler and stack-map addresses as instruction ordinals. Exception
  table order, ranges, handler targets and catch types remain significant.
- Preserves class versions, identifiers, descriptors, flags, declarations and
  their order, field constants, declared exceptions, stack/local limits,
  supported inner-class metadata and stack-map contents.

Unknown constant-pool forms, attributes or instructions prevent a normalized
match; they return **unverified**, not green. A whole-class exact-byte comparison
can still establish literal equality without interpreting unsupported features.

This first policy does **not** infer renamed symbols, reorder declarations,
prove equivalence of different algorithms, or silently discard unknown metadata.
Consistent Java source renaming may therefore show differences or missing classes
until a separately reviewed mapping policy is added. The parser is a bounded
comparison implementation, not a substitute for JVM verification.

Normalized method results describe that member's structure and references only.
They do not establish equivalence of its callees, class initialization, assets,
phone APIs, thread timing, save files, or the complete game. The class treemap
uses the **full class result**, not a majority vote of matching methods.

## Freshness and provenance

Reports record both input SHA-256 values, the normalization policy and a digest
of comparator code, target configuration, class-stage records, and their linked
evidence files. Changes to that context make the displayed report **stale** and
turn all its match tiles gray until rerun. A positive artifact result is also
withheld unless its class has recorded repaired source and a successful
source-only build.

These guards do not authenticate human-written evidence. They do not inspect
ignored recovered sources on GitHub, detect all changes to an untracked local
build, or prove that a candidate was compiled instead of copied. Reports are
snapshots of named artifacts, not continuous tests. Build provenance, exact
commands, dependency hashes, source-revision information and semantic review
still belong in the accompanying evidence report.

`whole_jar_exact` is a separate archive-level result. Class matches alone do not
imply identical JAR packaging or assets. A native Windows executable is not a
candidate Java JAR; native-port validation remains a separate milestone.

## Tests and reference specifications

Synthetic class files exercise byte equality, constant-pool relocation, changed
constants/instructions, debug attributes, unsupported data, missing candidates,
stale reports, source-evidence gating and safe failures. An optional installed
JDK test independently compiles a small authored Java fixture with/without debug
metadata, switches, exception handlers and changed field constants. These are
tool tests, not DAH gameplay tests.

Primary format references: [JVMS 8 class files](https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-4.html)
and [JVMS 8 instructions](https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-6.html).
