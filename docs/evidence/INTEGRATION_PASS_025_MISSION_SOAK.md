# Integration pass 025 — 65,000-frame all-mission soak

A long-duration deterministic soak now covers every mission.

Each of the 13 missions runs in a fresh JVM through the same real controller/world
update path used by the accepted mission-stress validator, but for **5,000 frames**
per mission instead of 300.

Total coverage in this pass:

**13 × 5,000 = 65,000 mission-specific update frames per side.**

Retail and rebuilt complete outputs are byte-identical for all thirteen mission
processes. Aggregate concatenated output SHA-256:

`318f4f57708cf7eb34175e33fceb50f9253e78e011227c41d8f4268bc21c21fa`

This soak is intended to expose slow state drift, timer/counter divergence and
long-duration instability that shorter smoke/stress passes could miss. It is not
exhaustive input exploration and remains complementary to the four-seed mission
fuzz pass.
