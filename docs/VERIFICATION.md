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

## Milestones (all except input/tooling setup are pending)

| Gate | Evidence required |
| --- | --- |
| Input/tooling setup | Exact hash verification, reproducible structural audit, synthetic tooling tests. |
| Initial recovery | Complete decompiler outputs and logs; every original method accounted for. |
| Source rebuild | Clean build from recovered source and documented dependencies, without copying original game classes. |
| Behavior baseline | Controlled original/rebuilt runs, explained bytecode differences, regression records. |
| Understandable source | Identifier mappings, system documentation, resolved unknowns, independently checked explanations. |
| Native proof | Original game logic compiled ahead of time; platform services implemented, not an interpreter bundle. |
| Gold candidate | Full progression and persistence checks; no unexplained mismatches or gameplay stubs; reproducible build and documented limitations. |

## Required comparisons

Compare both implementations under the same initial state and recorded inputs.
Control or record time, randomness, and scheduling. Record state transitions,
entity movement and collision, combat and damage, mission objectives, failure
and retry, menus, pause/resume, audio events, and saved-state behavior. Compare
images at the original internal resolution before desktop scaling.

Use method-level bytecode review where execution alone is insufficient. Any
normalization for identifier changes or constant-pool ordering must preserve
meaningful instructions, exception handling, and reference identity.

A deterministic replay system, automated image comparison, and an original/
rebuilt harness do NOT exist yet. This document specifies requirements rather
than claiming implementations.

## No hidden substitutes

A compiling placeholder is not recovered gameplay. Retaining the original JAR
as an asset/reference input does not permit silently loading its game classes
to hide incomplete source. Every unresolved method and native dependency must
be visible in status records.

Preserve a faithful baseline before optional bug fixes or improvements. A
successful Java rebuild is not a verified native Windows port; track those
separately. Original assets must be traced to the pinned input and handled
separately from original project tooling and third-party code.
