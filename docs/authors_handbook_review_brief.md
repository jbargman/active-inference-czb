# Brief: what to revise in the authors' edition of the handbook

*Written 2026-09-03 as a starting point for a more capable session. This is a PARTIAL scan, not
a finished review — it names the delta I had established and the places I had not yet checked.
Treat the "candidates" as leads to verify, not as findings to transcribe.*

## The question Jonas asked

> "Verify if there is something we should revise in the handbook for the authors given what we
> have learned. I am not after adding anything about CZB, but if we have learned something about
> the original model that we may want to revise in the Nature Communications author handbook."

So: **findings about the published model**, not about comfort-zone boundaries. The CZB
programme is our agenda and stays out, per `docs/handbook_authors/README.md`.

## Why there is a delta at all

- `docs/method_review.md` is dated **2026-08-23**.
- `docs/handbook_authors/aif_driver_model_handbook.md` was prepared **2026-08-24**.
- Gate R.2, `docs/r2_pipeline_review.md`, cards EL.1/EL.1b/G.1/B.3.v2/TT.1 and handbook
  appendix 16 all came **after**.

Everything learned in that window is absent from both documents. Note the README's standing
decision: the authors' edition is a **one-off** and "will not track" the internal handbook. So
the output here is probably a short dated addendum or a note to the authors, not a rewrite —
confirm with Jonas which he wants before drafting.

## Candidate 1 (strongest, verified) — the safety term inverts its own ordering at speed

**Source:** `docs/r2_pipeline_review.md` §3.2, and §3.3 for the scope statement.

The safety-margin term scores a state by a counterfactual: if the lead braked at an assumed
worst case and I responded after an assumed reaction time, would ordinary braking suffice? In
the regime of the second cut-in study — ego 110–130 km/h, gaps 4–80 m — **the counterfactual is
violated in nearly every cell**, so the term stops measuring the current gap and instead
measures how bad the worst case would be, which the absolute speeds set far more than the gap
does. Quantified at those cells: the magnitude moves about **0.33 (m/s) per metre of gap**
against **1.5–2.0 (m/s) per (m/s) of either vehicle's speed**.

Consequence, and this is the part worth telling the authors: within a matched-TTC row the term
ranks cells by how fast the vehicles are going, while participants rank them by how far apart
they are. At matched TTC 0.8 s the 42 km/h cell scores 30.7 against the 21 km/h cell's 23.1
*despite having the larger gap*; holding both speeds fixed, the larger gap alone would give
21.5 — the direction the data take.

**What the authors' edition currently says** (§ "The safety-margin term is a counterfactual",
around line 1024): that the term is a what-if, that its assumptions are parameters, and that any
absolute number derived from it inherits them. Correct as far as it goes. It does **not** say
that in a violated-counterfactual regime the term's sensitivity is dominated by absolute speeds,
which is a stronger and more actionable statement.

**Scope discipline — do not overstate.** §3.3 is explicit that this is "a verdict on the
published safety term's counterfactual **as a comfort criterion**". A collision genuinely does
depend on absolute speeds, so this may be exactly right for collision avoidance and wrong only
for the use we put it to. Any wording must keep that distinction.

## Candidate 2 (positive, and probably the most welcome) — the looming perception stage is vindicated

The axis comparison was run for our own purposes and had no stake in the authors' choices. Among
the candidates tested — gap, TTC, optical size, required deceleration, the model's own
preference-field deficit, and two-dimensional rules — the winner on human judgments was the
**optical expansion rate**, θ̇ ≈ W Δv / gap² (`out/cutin2_looming.md`, `out/cutin2_two_axis.md`).
That is precisely the quantity the released model's perception stage computes
(`bicycle.py::looming_rate`, `agent.py` `use_looming`, `looming_threshold = 0.00215 rad/s`).

Two independent corroborations: the fitted weight on the two logs came out at 0.497 (0.474–0.512
across folds), which *is* the looming identity rather than an approximation of it; and a
separate analysis by Sarang, with a different cue and a different fitter, landed on a speed
exponent of 0.39–0.42 where a looming threshold implies 0.5 (handbook appendix 16.3).

So: the model's **preference field** lost a pre-registered comparison, and its **perceptual
front end** independently won one. The authors' edition currently presents looming as an
implementation choice and an anchor to visual-control models (lines ~170, ~423, ~1154). It could
fairly be strengthened to "independently selected, on human data, from a field of candidates".

**Caveat that must travel with it:** the counter-finding is Xue et al. (2018), who reportedly
found inverse tau better for brake onset in a simulator; on this video paradigm the order
reverses (θ̇ 0.113 against 1/TTC 0.168). **That citation is UNVERIFIED** — it reaches us only
through Sarang's note, whose references handbook appendix 16.5 records as being from memory.
This is open query DECK.Q1. Verify it or state the point generically before it goes anywhere
outward-facing.

## Candidate 3 (a question for the authors, NOT a finding)

`docs/r2_pipeline_review.md` §3.1 shows that a lane-entry gate computing "will the target be in
my lane when the gap closes" suppresses exactly the cells where participants respond most — 64
of 288 cells sit below 0.9, all at short starting TTC with slow lane changes, and their mean
response is 0.75 against 0.51 elsewhere.

**But that gate is our construction, not theirs.** §3.3 says so plainly: this is a verdict on
our own 2026-08-27 lane-entry note. The *released* binary gate (a target is "in lane" only
within 1.15 vehicle widths) was never run on this study; the review's opinion is that its
geometry "would suppress the same slow-lane-change cells at least as hard", and calls a check
"cheap". Until someone runs it this is a hypothesis. Put it to the authors as a question, or run
the check first — do not report it as a property of the published model.

## Also worth a look, not yet checked

- **Non-monotonicity of the field in starting TTC** (`r2_pipeline_review.md` §3.1): median
  deficit 3208 at 2 s against 7179 at 3 s, while the human response is monotone. Is this a
  property of the field as specified, or of our continuous rendering of it? Not established.
- **`docs/r2_pipeline_review.md` §4** — optimizer sensitivity (wRMSE moves up to 0.005 under row
  permutation, a flat objective with multi-start L-BFGS-B). This is about *our* fitting of their
  field, not their code, but it may be worth a line to anyone refitting.
- **Chapter 10 (calibration) and chapter 13 (deep end)** of the authors' edition were not read
  against the new findings at all. Neither was `docs/r2_gate_decisions.md` in full.
- **Handbook appendix 16 in the internal edition** is the reading of Sarang's analysis; anything
  taken from it into an authors-facing document must respect that his note's references are
  unverified and that the two analyses are not blind on the fold design (16.4, "Independence").

## Method suggestion

Work from the delta, not from the whole handbook: read `docs/r2_pipeline_review.md`,
`docs/r2_gate_decisions.md`, `out/cutin2_looming.md`, `out/cutin2_two_axis.md`,
`out/cutin2_field_horizon_gate.md` and handbook appendix 16, then grep the authors' edition for
each claim to see whether it is already there, contradicted, or absent. Tag every proposed change
with its source in the authors' edition's own scheme ([Paper] [SI] [Code] [OSF] [Opinion]).
