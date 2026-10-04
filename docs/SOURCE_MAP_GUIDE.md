# Maintaining the source map

Start at [the source tree and implementation map](SOURCE_TREE.md). It is generated
from `config/source_map.json`; do not edit the generated Markdown directly.

## What this tracks

The actual Git index supplies the file list. Every tracked file needs one manifest
entry describing its purpose and kind. The tool rejects missing entries, duplicate
paths, nonexistent mapped files, and unsupported statuses. It does not discover or
upload ignored game material. New files must be staged before coverage checks.

Original classes have independent **recovery**, **source-only build**, and
**behavior** records. Method entries are structural inventory counts, including
constructors and class initializers; they are not recovered-method counts.
No whole-project completion percentage is calculated.

## Routine update

1. Implement and test the change; update `docs/STATUS.md` with actual results.
2. Update `config/source_map.json`: add new file descriptions, adjust class
   records, and add evidence when any stage advances or a failure is recorded.
3. Stage only the intended tooling/documentation files. Never force-add original
   game files, assets, raw decompiler output, or repaired game source.
4. Regenerate, check, and test from the repository root:

```console
python tools/source_map.py
python tools/source_map.py --check
python -m unittest discover -s tests -v
```

Stage the updated `docs/SOURCE_TREE.md`, then inspect `git diff --cached` before
committing. The generator uses Python 3.10+ and Git with no additional packages.
The `Progress dashboard` workflow checks pull requests and regenerates source-map
and treemap documentation on main, then runs the tooling tests. Only fixed
allowlisted generated documentation paths can be committed by its update step.
It does not change branch protection, upload ignored inputs, compare game builds,
or bypass a rejected non-fast-forward push. Repository policies can prevent a
bot push; regenerate and commit locally in that case.

## Class record rules

| Field | Allowed states | Meaning |
| --- | --- | --- |
| recovery | not_started / raw_output / repaired | No source yet; raw decompiler output; or repaired source. |
| build | not_tested / failed / passed | Result of a source-only build that includes this class. |
| behavior | not_tested / differences / passed_scoped | Comparison against the original under explicitly recorded conditions. |

Every non-default stage needs its own evidence list. Each evidence item contains
`path` (an existing mapped report file) and `scope` (what was actually tested or
reviewed). Do not use the existence of a method or a passing tooling test as game
fidelity evidence. A source path is required after recovery starts. A successful
build requires repaired source, and behavior testing requires a successful
source-only build.

A class source path is a pointer; the generator deliberately does not open it.
This lets local-only work be tracked without exposing recovered code. Evidence
summaries can be tracked, but inspect them for game material before publishing.
Record exact commands, input/tool hashes, coverage, failures, and limitations in
those reports. A link and a scope statement are necessary metadata, not proof.
The validator cannot determine whether a human-entered claim is truthful or
whether the evidence is sufficient; review is still required.

Do not promote a partly reconstructed class to `repaired`, or a partly tested
class to an unqualified accuracy claim. `passed_scoped` means only that the
recorded comparisons passed within the report's declared coverage. Use evidence
reports to itemize unresolved methods until a method-level tracker is needed.
Do not guess semantic names for obfuscated classes.

The planned-only list is for work that has not started. Once an area starts,
replace its planned entry with the actual tracked files and/or class records and
explain the remaining work in `docs/STATUS.md`. Planned entries do not create
folders and never count as implementations.

## Rechecking the inventory against the original

The initial register was populated from a fresh run of `tools/dah1.py` against
the exact JAR identified in `config/target.json`. Only original class identifiers
and their method-entry counts are stored in the manifest. No bytecode or assets
are stored there.

With your original input present locally:

```console
python tools/dah1.py audit --output local/audit-source-map.json
python tools/source_map.py --check --audit local/audit-source-map.json
```

Choose a new audit filename when that report already exists: the audit tool will
not overwrite it. The optional comparison checks the report's input hash/size
and every class's method count. Without `--audit`, checks verify the configured
target, totals, metadata consistency, file coverage, and generated-document
freshness, not the binary again. Neither command runs the game.

## Visual treemaps and byte-match results

The README embeds the recovery and byte-match maps. `docs/VISUAL_PROGRESS.md`
embeds all four views. After editing the class records, refresh both generators:

```console
python tools/source_map.py
python tools/treemap_dashboard.py
python tools/source_map.py --check
python tools/treemap_dashboard.py --check
python -m unittest discover -s tests -v
```

Treemaps consume the actual nested state/evidence records, not a second set of
hand-edited statuses. Byte comparison uses a separate artifact report selected
by `config/byte_match.json`. See `docs/BYTE_MATCH.md` for supported normalization,
report freshness, publication review, and the source-evidence gate. Unknown or
missing results stay unverified. These are class-level visualizations, not
method coverage or an overall accuracy percentage.

The workflow pins `actions/checkout` to commit
`11d5960a326750d5838078e36cf38b85af677262`, resolved from the publisher's v4 ref.
The optional JDK fixture test reports a skip when javac is absent. No dependency
binary or original game data is fetched by the workflow.
