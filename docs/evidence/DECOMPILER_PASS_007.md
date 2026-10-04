# Decompiler pass 007 — complete raw source inventory and first all-class source-only compile

A pinned automated decompiler pass is now available in the private workstation.
This is not a claim that every class is repaired, understood, behavior-tested, or
byte-matched. It is a mechanical recovery milestone that materially changes the
remaining work.

The hash-pinned English v1.2.0 JAR was processed independently with CFR 0.152 and
Vineflower 1.12.0. CFR used duplicate/illegal-member renaming and small-member
renaming so bytecode-legal duplicate identifiers could be represented in Java
source. Both decompiler binaries are hash-pinned in the machine-readable report.

CFR's whole-JAR pass emitted 20 Java files; r was omitted after an internal
whole-class-analysis failure, so the exact original r.class was decompiled
separately. The untouched raw outputs are retained privately.

A small reviewed local repair layer was required before javac accepted the
complete raw tree: one unresolved GOTO-shaped state method in j was replaced with
the already-reviewed pass-006 structure; definite-assignment artifacts in j and
f were corrected; a b tile-loop local was moved to the scope represented by the
bytecode; and r uses its separate CFR output. Compile-only Java ME/Nokia/RMS
definitions provide external API signatures and are not packaged as game code.

After those repairs, javac --release 8 -g:none -implicit:none compiled all 21 game
classes from Java source in one build. No original .class file was used as a
compiler input or copied into the candidate artifact.

Static inventory checks found 21/21 classes, 313/313 method/constructor/class-
initializer entries, identical ordered JVM method-descriptor sequences for every
class, and identical ordered field-descriptor sequences for every class (378
fields total). A second clean compile produced byte-identical rebuilt class files.

A local candidate JAR contains the 21 rebuilt classes plus the original 122
non-class resource entries copied byte-for-byte. It contains zero original class
bytes. Candidate JAR SHA-256:
8c887599181955f3f1fc305699aebceeddf2ad5f71192f268bfcbef0a3f1974f

None of its 21 rebuilt class entries is byte-identical to the corresponding
original class. No exact or normalized whole-class match is claimed.

Pass 006 repaired j, bringing the reviewed set to 18 classes / 182 original
method entries. This automated pass gives b, k and p complete local raw decompiler
output, so the source-recovery inventory can now show 21/21 classes with some
source recovered. b/k/p remain raw_output with build and behavior untested on the
evidence map. The successful all-class raw compile is a pipeline result, not a
shortcut around reviewed class-level recovery.

Still not established: repaired/understood b/k/p, a behaviorally validated
complete game, handset/platform fidelity, full missions/save/load comparisons,
exact/normalized matching, or a native Windows executable.
