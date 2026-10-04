# Recovery pass 006 — shared actor and state-machine integration

The complete private source for class j has been manually reconstructed from the
hash-pinned original bytecode. Its 31 method entries bring the reviewed component
set to 18 of 21 classes / 182 of 313 original entries. The previous seventeen
reviewed source snapshots are unchanged.

Class j implements shared actor construction, sprite/pose selection, weapon
cycling, threat/state decisions, navigation and movement, damage, effect-driven
state transitions, disguise/hypnosis/following, abduction/death processing,
timed updates, actor drawing and directional input. Numeric states and type codes
were preserved rather than replaced by a redesigned AI system.

The accepted eighteen-class component JAR contains only newly compiled recovered
game classes. Original classes run only in a separate reference JVM. World class
b and controller class k remain explicit authored test support in this pass; p is
absent. The candidate has no original game class as a compiler or runtime fallback.

Original-versus-recovered comparisons matched 25,818 direct j calls per side
across ten groups: construction/cache, animation, decisions/weapon cycling,
navigation/collision response, damage, state setup/followers, timed transitions,
drawing, directional input, and weapon/collection/saucer integration. All 30
directly callable j methods/constructors have normal-return observations; the
additional class initializer is exercised through class loading. This is scoped
testing, not exhaustive branch coverage or a whole-game equivalence claim.

A real reconstruction error was found by the comparisons: an expression intended
to invoke the collection insertion overload instead selected a more-specific query
overload in Java source. Both compiled. Explicitly selecting the base-entity
signature restored the original invocation behavior, and an independent overload
fixture now guards that failure mode.

Two clean final runs produced byte-identical eighteen-class component JARs and
observation reports. Component JAR SHA-256:
38febebd5de556e4adac7d54946c865d708eb53779926482d165f0290938d8a4

Seven deliberately incorrect variants were detected, including wrong collection
overload selection, player damage, weapon-state gating, follower count,
navigation-node exchange, health-bar color, and movement during firing.

All five earlier comparison suites passed again under their historical scopes.
Ninety-one local recovery-tool tests passed, including sixteen new actor-recovery
tests. The complete local logs, source bodies, original input and machine report
remain in checkpoint 006 rather than this public repository.

No complete playable game, platform implementation, exact/normalized whole-class
match, or native Windows executable is claimed by this pass.
