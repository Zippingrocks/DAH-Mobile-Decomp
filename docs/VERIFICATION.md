# Faithful reconstruction: evidence required

## Reference and claim boundaries

Pin one original JAR by SHA-256. Pin platform assumptions separately: screen
size, input mappings, Java ME/Nokia behavior, clock, random sequence, scheduling,
rendering, media, and persistent storage. Matching a particular emulator does
not by itself prove equivalence to every original handset.

The release objective is a reproducible, understandable source tree and native
build with no known fidelity defects against a documented reference. Tests
support that claim only within their documented coverage. Do not promise
unconditional equivalence for every possible input based on playtesting.

## Milestones and current evidence state

| Gate | Evidence required | Current state |
| --- | --- | --- |
| Input/tooling setup | Exact hash verification, reproducible structural audit, synthetic tooling tests. | Established and continuously checked. |
| Initial recovery | Complete decompiler outputs and logs; every original method accounted for. | Established: 21/21 classes, 313/313 method entries. |
| Source rebuild | Clean build from recovered source and documented dependencies, without copying original game classes. | Established in the all-repaired whole-tree build and desktop packager. |
| Behavior baseline | Controlled original/rebuilt runs, explained reconstruction defects, regression records. | Established in scoped component/integration/campaign/stress/fuzz/soak comparisons. |
| Understandable source | Identifier mappings, system documentation, resolved unknowns, independently checked explanations. | Substantially established; documentation remains a maintenance task rather than a missing source phase. |
| Native proof | Original game logic compiled ahead of time; platform services implemented, not an interpreter bundle. | Build automation and tracing-agent/native-image preparation are established; a Windows native executable is not yet built on a suitable Windows host. |
| Gold candidate | Full progression and persistence checks; no unexplained mismatches or gameplay stubs; reproducible build and documented limitations. | Machine-checkable progression/persistence/runtime gates are established; human subjective playtest/judgment and validated native Windows output remain open. |

## Required comparisons

Compare both implementations under the same initial state and recorded inputs.
Control or record time, randomness, and scheduling. Record state transitions,
entity movement and collision, combat and damage, mission objectives, failure
and retry, menus, pause/resume, audio events, and saved-state behavior. Compare
images at the original internal resolution before desktop scaling.

Use method-level bytecode review where execution alone is insufficient. Any
normalization for identifier changes or constant-pool ordering must preserve
meaningful instructions, exception handling, and reference identity.

The project now has implemented deterministic original-versus-rebuilt harnesses,
state-graph comparison, headless framebuffer comparison, mission objective and
completion comparison, mission-to-mission file-backed RMS progression, fixed-
pattern mission stress, multi-seed differential fuzzing, long-duration mission
soak testing, audio packaging/sanity checks, and a production desktop-runtime
comparison.

These mechanisms still prove only their documented scopes. They do not remove the
need for human subjective playtesting, nor do they constitute a Windows native
executable by themselves.

## Machine release-readiness audit

Run:

```console
python tools/release_readiness.py --check
```

The auditor checks the current source map and required evidence files, reports the
machine-checkable gates, and lists remaining human-only/environment-only work. It
deliberately reports `gold: false` until the project has a validated native
Windows executable plus the remaining subjective human validation.

## No hidden substitutes

A compiling placeholder is not recovered gameplay. Retaining the original JAR
as an asset/reference input does not permit silently loading its game classes
to hide incomplete source. Every unresolved method and native dependency must
be visible in status records.

Preserve a faithful baseline before optional bug fixes or improvements. A
successful Java rebuild is not a verified native Windows port; track those
separately. Original assets must be traced to the pinned input and handled
separately from original project tooling and third-party code.
