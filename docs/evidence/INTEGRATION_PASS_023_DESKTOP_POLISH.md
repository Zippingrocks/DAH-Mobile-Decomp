# Integration pass 023 — desktop input and presentation polish

The authored desktop Canvas layer now removes more setup work from the eventual
human playtest.

## Deterministic integer scaling

The logical game framebuffer remains exactly **176×208**. Desktop presentation
uses an integer scale selected by `-Ddah.scale=N`, clamped to **1–8** with a
default of **3**.

Swing rendering explicitly uses nearest-neighbor interpolation and disables
antialiasing for the scaled framebuffer. The window is non-resizable so the
display cannot silently drift into arbitrary fractional scaling.

## PC control mapping

The runtime now maps:

- arrows or WASD → mobile 2/4/6/8 movement keys,
- Enter or Space → mobile center/action key 5,
- Z or Q → left soft key (-6),
- X or Escape → right soft key (-7),
- numeric characters → their original mobile numeric key codes.

Unmapped desktop keys are ignored instead of sending key code 0 into recovered
game logic.

## Why this matters

These changes do not alter recovered game behavior. They make the desktop wrapper
less likely to create false negatives during human QA and reduce the final
hands-on checklist to actual game feel/presentation judgment instead of basic
control setup.

Public tests pin the scale bounds, nearest-neighbor path, desktop key mapping and
zero-key filtering.
