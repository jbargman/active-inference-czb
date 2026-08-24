# The authors' edition of the handbook — one-off

`aif_driver_model_handbook.md` (with generated Word and PDF) is a self-contained edition
of the understanding handbook (`docs/handbook/`), prepared 2026-08-24 to be shared with
the authors of the active-inference papers as a courtesy.

Differences from the internal handbook, by design:

- No comfort-zone-boundary framing or chapters; the CZB program is this project's own
  agenda, not part of the gesture.
- No references to this repository's internal files, notes, re-implementation, or
  review documents; code paths refer to the authors' released repository.
- Our crash-causation proposals (internal chapter 08) are reduced to the inventory of
  what ships in the released code.
- Revision marks removed; code-versus-SI observations are stated neutrally as properties
  of the release, tagged [Code].
- The [Speculation] tag is renamed [Opinion] and used only for readings and judgments.

**This edition is a one-off.** The internal handbook continues to evolve; this file will
not track it. If a second shared edition is ever wanted, regenerate from the then-current
internal chapters rather than editing this one.

Build:

    python docs/build_pdf.py docs/handbook_authors/aif_driver_model_handbook.md
    pandoc docs/handbook_authors/aif_driver_model_handbook.md -o docs/handbook_authors/aif_driver_model_handbook.docx --from markdown --resource-path docs/handbook_authors
