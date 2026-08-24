# The active-inference driver model — a handbook. Chapter 0: reading guide

*Part of the WaymoActiveInference understanding pack. Markdown is the source of truth;
the Word and PDF versions are generated from it (`docs/handbook/build_handbook.py`).
Draft for comment, 2026-08-22; revised 2026-08-23.*

{{R1}}**Revision marks.** Passages in dark red were changed on 2026-08-23, after a review of the
published method against its released code and data (`docs/method_review.md`). The review
found that the authors' code differs from the Supplementary Information in several
places (the inverse-tau term is one-sided, the off-road cost is −15000, the
control-effort term has a different form), that the surprise signal is far from zero
during ordinary following in the authors' own runs, and that the paper's worked example for
the rear-end scenario does not represent the authors' deposited data. The handbook's
text has been corrected where it relied on the SI or on that example; the corrections are
marked so that a reader of the 2026-08-22 draft can see what moved.

{{R2}}**Revision round 2.** Passages in dark blue were added on 2026-08-25, after the
crash-causation study (`docs/crash_causation_plan.md`, `docs/crash_causation_results.md`)
turned several of chapter 08's proposals into built and tested machinery. The main
lessons folded back in: the dormant gaze system has now been exercised in the closed loop,
and it gates *evidence*, not *inference* — a driver who has registered the conflict keeps
accumulating toward a response during an off-road glance (chapters 06 and 08); the model
can be dropped into externally defined scenarios by replaying a recorded lead vehicle
(chapter 04); a cheap open-loop surrogate of the response timing has been validated
against the closed loop across 23 scenarios (chapters 09 and 12); and the practical cost
figures are revised (chapter 03).

## What this handbook is

This handbook explains the active-inference driver model of Schumann et al. (2026, Nature
Communications) — the model this project replicates and builds on — well enough that a reader
can (1) understand how it works, (2) change it deliberately, and (3) follow the argument for
extending it into comfort-zone boundary (CZB) research. It is written for a mixed audience of
traffic-safety analysts and human-factors researchers. The main text of every chapter avoids
mathematics; each chapter ends with layered notes for readers who want the equations.

The handbook is grounded in four kinds of sources, and every substantive claim is tagged with
its provenance:

- **[Paper]** — the published article
- **[SI]** — its Supplementary Information (where most of the actual definitions live)
- **[Code]** — the authors' released code (`external/aica/`), which is the ground truth when
  the paper is ambiguous — {{R1}}and, as it turned out, also when the paper and the SI are
  unambiguous but do not match what the code does (`docs/method_review.md` §5 lists the
  differences)
- **[OSF]** — the authors' own simulation output (`external/gs4bu-osfstorage-archive/`),
  which lets us show real numbers rather than sketches
- **[Speculation]** — our own ideas and proposals, which are ours and not the authors'

## The chapters

| Part | Chapter | One line |
|---|---|---|
| I Getting oriented | 01 Where this comes from | The lineage of the idea, what "free energy" actually means, how it relates to models you already know, and the debate around it |
| | 02 One event through the model's eyes | A single rear-end conflict, told moment by moment with real numbers |
| II The machinery | 03 What the model is | Every component, its inputs and outputs, and the loop that connects them |
| | 04 Scenario playbook | Exactly what changes between scenarios, and the checklist for adding a new one |
| | 05 Normal versus critical | Why the same machinery covers everyday driving and emergencies |
| | 06 Other agents and beliefs | What the other vehicle actually does, versus what the driver model believes it might do |
| | 07 Normative driving | What defines "normal" behavior, and every knob that moves it |
| | 08 Crash causation | What exists today for glances and impairment, and our proposals (marked as such) |
| III Building on it | 09 Modify and validate | Recipes for changing the model, each with its validation ladder |
| | 10 Calibration and parameter fitting | Where every number came from, how to set new ones, identifiability, and the dos and don'ts |
| | 11 The path to comfort-zone boundaries | What exists, what has been tested, what human data would add |
| IV Reference | 12 Code map | From concept to file, class, and parameter — with five first exercises |
| | 13 Glossary | The same idea in three vocabularies, plus common misconceptions |
| | 14 Appendix: the deep end | The material deliberately kept out of the main text — the free-energy principle proper, variational inference, Markov blankets, the debate literature, the discrete-state formulation — for reference |

## Reading paths

- **Thirty minutes, any background:** chapter 02, then the first half of chapter 01.
- **Human-factors readers:** 01 → 02 → 05 → 07 → 08 → 11. Chapter 03 on demand.
- **Analytics / modeling readers:** 02 → 03 → 04 → 06 → 09 → 10 → 12, with the
  chapter-end notes.
- **"I want to change the code":** 03 → 04 → 12 → 09 → 10, keeping 13 open in a second
  window.
- **"I care about comfort zones":** 01 → 02 → 07 → 11, then 10 before fitting anything.

## How the math is layered

Each chapter's main text is **Level 0**: components, inputs, outputs, and behavior, no
equations. At the end of a chapter:

- **Level 1** states the same content with light notation — enough to read the paper's
  figures and follow its argument.
- **Level 2** gives the actual equations with their Supplementary Information numbers, so a
  reader can go from this handbook straight into the SI or the code.

Nothing in a later chapter depends on having read the notes of an earlier one.

## One warning before you start

Two words in this literature do not mean what they usually mean, and misreading them is the
most common way to get lost. **Surprise** is not an emotion here: it is a number measuring
how far what is happening departs from what the model expected. **Preference** is not a
choice: it is a description of the futures a driver treats as normal, encoded so that
wanting something and expecting it become the same quantity. Chapter 13 collects the rest of
these false friends.
