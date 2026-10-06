# Integration pass 026 — machine release-readiness audit

The project now has a dedicated release-readiness auditor rather than relying on
a prose checklist that can become stale.

## Auditor

`tools/release_readiness.py` checks:

- the current 21-class source map,
- all 313 original method entries,
- repaired/build/scoped-behavior records for every class,
- presence of the current recovery/integration/campaign/runtime/audio/native-prep
  evidence chain,
- whether a Windows native executable has actually been built according to the
  native-AOT evidence.

It separates:

1. **machine-checkable readiness**,
2. **human-only subjective validation**,
3. **environment-only Windows native compilation/validation**.

It deliberately cannot report project gold.

## Current audit result

The current repository satisfies the machine-checkable source/evidence gates:

- 21 / 21 classes repaired,
- 313 / 313 method entries accounted for,
- 21 / 21 class build records passed in documented scope,
- 21 / 21 class behavior records passed in documented scope,
- all required evidence documents through the mission soak are present.

Therefore the auditor reports **machine release readiness = true** for the
currently defined objective repository gates.

It still reports:

- **native Windows executable built = false**
- **gold = false**

Remaining human-only items are:

- interactive full-campaign playtest for control feel and unscripted edge cases,
- subjective audio loudness/mix/timing judgment,
- subjective desktop presentation/window-scaling judgment.

The remaining environment-only item is producing and validating the native
Windows executable on a Windows GraalVM/MSVC/Windows-SDK host.

## Verification contract refresh

`docs/VERIFICATION.md` has also been updated. Its old statement that
deterministic replay/image comparison/original-vs-rebuilt harnesses did not yet
exist was obsolete. The document now distinguishes the many implemented
comparison systems from the still-open human/native gates.

This pass does not weaken the finish line. It makes the finish line auditable.
