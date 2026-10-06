# Integration pass 024 — automated converted-audio sanity

The desktop audio path now has a machine check for conversion health in addition
to packaging and runtime lookup.

All four actual retail AMR effects were decoded to the embedded WAV companions
and inspected as PCM:

| AMR SHA-256 | Duration | Peak | RMS | Clipped samples |
| --- | ---: | ---: | ---: | ---: |
| 5fdad79f7f4001deab559b240a808e134578bb80640ca5876dea3b5f575f0690 | 0.24 s | 11512 | 3914.27 | 0 |
| 94bb3ab8ae3f01c4f6fc2a780630082b25b8ba68ca0a5edf9e05f8ebb0b1be18 | 0.06 s | 8774 | 2750.78 | 0 |
| ab2e745f7c47589645ffecac648369b06bd165398fac2d18d319beebc5554273 | 0.32 s | 21804 | 8255.05 | 0 |
| aa8f4a0c0e0504314da5229a2e3d2b6d784830b2f2f6a166b08f375d72224700 | 0.92 s | 10952 | 1659.78 | 0 |

Every clip is mono, 8 kHz, 16-bit PCM, non-silent and has zero clipped samples.

The new `tools/audio_sanity.py` validator checks those structural and signal-level
properties directly from a packaged desktop candidate. This does not replace
subjective listening for loudness/mix/timing, but it removes silent/corrupt/clipped
conversion failures from the human checklist.
