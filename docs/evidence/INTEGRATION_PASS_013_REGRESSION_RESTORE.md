# Integration pass 013 — restored regression replay

The pass-013 campaign checkpoint was preserved on GitHub, but the private working directory used for the pending regression reruns was interrupted. This pass reconstructs an independent private verification tree from the exact pinned retail JAR and the same pinned CFR/Vineflower toolchain, applies the documented pass-007 compile repairs and reviewed world-manager construction correction, and replays the previously accepted integration probes.

This restored tree is a verification reconstruction, not a claim that its Java text is byte-for-byte identical to the interrupted renamed/private source snapshot. The purpose is to independently verify the recovered game semantics against the retail bytecode after the campaign field-binding discovery.

## Clean source-only rebuild

The restored tree compiles **21 game classes** from Java source with no original class fallback. Two clean compiles produced identical SHA-256 hashes for every rebuilt class.

`javap -p -s` comparison against the original JAR confirms identical ordered field/method descriptor sequences for all 21 classes and **313 original method entries**.

The reconstructed world-manager source uses the original actor-byte field binding for objective counting (`j.n:B` in original naming / the corresponding renamed byte field in the decompiler tree), rather than inherited static `o.n`.

## Replayed original-versus-rebuilt regressions

Each probe was compiled once and then run unchanged against the original retail classes and the restored rebuilt classes using the same deterministic authored Java ME/Nokia adapters.

| Probe | Scope | Matching output SHA-256 |
| --- | --- | --- |
| IntegrationProbe | startup, init, five ticks, lifecycle, first paint | `a2a621363ac695d516ff21efa1e43d4c4f05dc4b3c8cd6c270817298751df2ec` |
| StateProbe | init, five ticks, multi-key state graph, render | `dc01b54d0e53dbb6df2b91ff0c6863e5e9b564ad468e6f005eea38eaaa1a1049` |
| DeepIntegrationProbe | controlled default menu to gameplay/world path, movement/weapon/render | `ec8952277a2e04c6fb4f348522f964314cb62841f0bf49265ecc9316bbcceeda` |
| PersistenceProbe | real game 82-byte RMS save/load semantics on deterministic adapter | `91e083590d3838bbf7a3717eeefd96135b1dcef5829410ca5aedb45d9b686ef0` |
| LongRunProbe | menu to world plus 500 gameplay frames and periodic state/render/media/RMS observations | `38ded5fab464972f8822076a2b71bafe4cf16baa73d98318b6607c8f711ccafc` |

For every probe above, the complete original and rebuilt stdout files were byte-identical.

## Relationship to the campaign checkpoint

The earlier pass-013 checkpoint remains the evidence for the direct-load **13-mission campaign matrix** and the source-binding defect it exposed in missions 8, 9 and 13. That checkpoint records all thirteen missions matching after the `j.n:B` correction, including dynamic kill totals of 29 and 30 for missions 7 and 12.

This restored regression replay closes four of the five explicitly pending post-fix verification categories:

1. 500-frame deterministic stress comparison — passed again
2. RMS save/load round-trip — passed again
3. startup/menu-to-gameplay probes — passed again
4. final 21-class clean-build repeatability — passed again
5. 300-frame production-desktop comparison — still awaiting recreation/rerun of the interrupted production desktop runtime workspace

The production desktop result recorded before interruption is still preserved in the campaign checkpoint, but it is not promoted to a new rerun result here.

## Limits and next step

This is strong independent regression evidence, not a complete campaign playthrough, native Windows executable, production audio certification or gold release. The next concrete task is to recreate the production desktop runtime workspace from its proven API contracts and rerun the 300-frame original-vs-rebuilt desktop comparison, then extend that runtime across longer mission progression.
