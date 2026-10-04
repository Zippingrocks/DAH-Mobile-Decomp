# Workstation instructions

## Scope and source of truth

Only `dah1-j2me-en-v1.2.0` is in scope. Verify its hash using `config/target.json`.
The original input is the behavioral reference; plans and AI explanations are
not proof. Inspect current files and Git history before resuming work.

## Work rules

1. Preserve original inputs unchanged and never commit them. Keep decompiler
   downloads, assets, disassembly, generated recovery output, and local logs in
   ignored directories. Do not upload game files to an external service.
2. This repository is currently a tooling-only public repository. Do not publish
   recovered game source without an explicit publication/visibility decision.
3. Record exact dependency versions, hashes, provenance, and license boundaries
   when adding them. No silent tool upgrades and no unpinned remote execution.
4. Keep raw decompiler output separate from repaired source. Preserve a mapping
   from original class/method/field descriptors to renamed source identifiers.
5. Never fill unknown gameplay with plausible inventions. A stub must be marked
   and must not count toward recovered or verified behavior.
6. Never use original compiled game classes to hide missing recovered source.
7. Update `docs/STATUS.md` with exact commands, evidence, limitations, and the
   next concrete task. Do not invent completion percentages or accuracy claims.
8. Separate tooling tests, source rebuilds, behavior tests, and native port tests.
   Passing one category does not establish another.
9. No unrelated games, game redesign, native compiler selection, public release,
   or repository visibility changes without revisiting scope with the owner.

## Before committing

Run `python -m unittest discover -s tests -v` and inspect `git diff --cached`.
Use `git status --ignored` to confirm private inputs remain excluded. Never use
`git add -f` for ignored game material. Inspect logs before copying them into
tracked documentation. Do not introduce secrets, tokens, or original assets.

## Keep the implementation map current

Update `config/source_map.json` when adding tracked files or changing a class
recovery/build/behavior record. Every non-default stage needs scoped evidence;
never equate structural inventory, source recovery, compilation, or fidelity.
Stage intended new tooling/docs first, run `python tools/source_map.py`, then
`python tools/source_map.py --check` and the full tests. Stage the generated
`docs/SOURCE_TREE.md` before committing. See `docs/SOURCE_MAP_GUIDE.md`.
