# The authors' edition of the handbook

`aif_driver_model_handbook.md` (with generated Word and PDF) is a self-contained edition
of the understanding handbook (`docs/handbook/`), prepared 2026-08-24 to be shared with
the authors of the active-inference papers as a courtesy, and **revised 2026-09-03** after
a review of what had been learned about the published model since (the brief for that
review is `docs/authors_handbook_review_brief.md`; the review itself is recorded in the
worklog entry of that date).

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
- Since the 2026-09-03 revision, a sixth tag **[Study]** marks findings from this
  project's own analyses (human video-rating data; the released model run outside its
  three scenarios), stated as properties of the model without the CZB framing they were
  found in. Every revision is dated in place in the text.

What the 2026-09-03 revision changed, in short: the planner's elite set (half, not a
tenth) and iteration counts (10 patch / 20 full re-plan); the collision severity factor
(0.2 + 0.8·Δv/10, not max(Δv/10, 0.2)) and the indicator form and lateral gating of the
safety-margin term; a line-by-line account of the three scenario files; the coasting of
beliefs through a forced occlusion; the looming variable's performance on human data with
the Xue et al. (2018) caveat, verified against the paper's abstract; the near-conflict
consequence of pre-conflict accumulator drift; the λ·g_C identifiability note.

**Version of 2026-09-28 (not sent).** `aif_driver_model_handbook_2026-09-28.md` (with Word and
PDF) is a newer version made from the 2026-09-03 edition, which is what the authors received and is
left untouched. A notice at the top says it goes beyond their copy. Each of the five additions
(items 1-5 of `review_2026-09-28.md`: sustained following, the response-time relation on highD, how
often the preference terms act in real traffic, the naturalistic looming-vs-inverse-tau check, a softer
reading of the 25 m/s road departures) is labeled "New in this version, 28 September 2026: not in the
edition you received" and colored. The one reworded passage quotes the wording they received. Built by
`make_version_2026_09_28.py`: regenerate with it, and do not edit the output by hand. Before sending,
see "Before any addendum is sent" in the review note (Julian's reply on item 1; the authors'
announced correction).

**This edition does not track the internal handbook.** The internal handbook continues
to evolve; this file is revised only when a review of the published model warrants it. If
a wholly new shared edition is ever wanted, regenerate from the then-current internal
chapters rather than editing this one.

Build:

    python docs/build_pdf.py docs/handbook_authors/aif_driver_model_handbook.md
    pandoc docs/handbook_authors/aif_driver_model_handbook.md -o docs/handbook_authors/aif_driver_model_handbook.docx --from markdown --resource-path docs/handbook_authors
