# Integration pass 016 — automatic AMR desktop audio packaging

The retail game contains four AMR sound effects:

- `Sound/pickup.amr`
- `Sound/select.amr`
- `Sound/shoot.amr`
- `Sound/transition.amr`

Standard Java Sound does not decode these AMR-NB assets directly. This pass removes
manual audio conversion from the desktop-port workflow.

## Automatic build-time conversion

`tools/desktop_build.py` now requires an external FFmpeg executable when packaging
the retail game. For each original AMR resource it:

1. preserves the exact original AMR in the desktop JAR,
2. computes SHA-256 of the original AMR bytes,
3. invokes FFmpeg to decode the AMR to mono 8 kHz WAV,
4. embeds the converted WAV as
   `META-INF/dah-audio/<original-amr-sha256>.wav`,
5. records source and converted hashes/sizes in the build report.

FFmpeg itself is **not** redistributed.

## Runtime lookup

The authored desktop media manager keeps the Java ME-facing `audio/amr` contract.
When the recovered game supplies AMR bytes, the runtime hashes those bytes and
loads the matching embedded WAV companion. Java Sound then handles the converted
PCM clip.

No recovered game source or resource path needs to be changed.

## Validation on the actual retail assets

The implementation was applied to the accepted pass-015 desktop JAR and all four
real AMR effects were converted and resolved successfully.

Observed FFmpeg:
`7.1.5-0+deb13u1`

| Original resource | AMR SHA-256 | WAV bytes | WAV SHA-256 |
| --- | --- | ---: | --- |
| `Sound/pickup.amr` | `5fdad79f7f4001deab559b240a808e134578bb80640ca5876dea3b5f575f0690` | 3,918 | `827687e527f4abdc9d302582c822b58348078db8e8bd527128eadf7ee4a65997` |
| `Sound/select.amr` | `94bb3ab8ae3f01c4f6fc2a780630082b25b8ba68ca0a5edf9e05f8ebb0b1be18` | 1,038 | `a448a2fdc377f338f492dbe530a1b5d0c08fb410be211fd1e407ecce0fe92b11` |
| `Sound/shoot.amr` | `ab2e745f7c47589645ffecac648369b06bd165398fac2d18d319beebc5554273` | 5,198 | `792b1c95dffa23882a4969aca17609fd90045cd7e356a9f260bfc140c4f8d9df` |
| `Sound/transition.amr` | `aa8f4a0c0e0504314da5229a2e3d2b6d784830b2f2f6a166b08f375d72224700` | 14,798 | `3da6bf17e34747414dd19af4827b13ebee7b18a0b6e052277c3e8da197c088a1` |

A packaged-resource probe verified that every SHA-addressed WAV exists, begins
with a valid RIFF/WAVE header, and that `Manager.createPlayer(..., "audio/amr")`
can realize, prefetch and enter started state for all four actual retail clips.

The local patched desktop-JAR validation artifact SHA-256 was:

`90c540a8e28dd6bbd746f1684b9676d68a035b300f8237af36cd568cfcf05ca9`

That patched validation artifact is not committed because it contains original
game resources. The reproducible builder/runtime source is the project artifact.

## Remaining human/audio boundary

A human still needs to judge subjective loudness/mix/timing on a real desktop
audio device. The mechanical work—locating, decoding, packaging and routing all
retail AMR effects—is now automated.
