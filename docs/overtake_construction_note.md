# Building the cyclist-overtake field, and what it revealed

*2026-08-28. Card B.1 of `docs/czb_work_orders.md`. The card asked for a loader, a field
check and a perceived-safety readout, on the assumption that the rear-end field would
carry over "nearly unchanged". The loader and the checks exist; the assumption did not
survive them, and most of this note is about that. Companion documents:
`docs/lane_entry_note.md` (the continuous forms this builds on),
`docs/czb_validation_roadmap.md` §2 (the transfer stage this card serves).*

## 1 What the scenario is, and why it is the right second scenario

The Random design's cyclist overtake gives 2 580 trials from **the same 43 participants**
as the cut-in, on 3 clearances (0.5 / 1 / 1.5 m) × 5 truncation points (C1–C5) = 15
cells. It is the only transfer scenario that shares the cut-in's truncated fixed-clip
structure: LTAP and truck overtake carry no `timepoint` at all (they vary criticality,
and for LTAP a second speed axis, but have no time series). Comparing a *surface* to the
cut-in's surface is therefore possible here and nowhere else, which is why it is first.

## 2 Two conventions that had to be established from the data

Both are recorded because getting either wrong is silent rather than loud.

**The lateral coordinate is `Location_Y`, not `Offset`.** Both columns are populated and
both look reasonable. `Location_Y` reproduces the study's own criticality labels exactly
— edge-to-edge clearance at the passing moment comes out 0.506 / 1.004 / 1.501 m for the
traces labelled 0.5 / 1 / 1.5 m. `Offset` is a *within-lane* coordinate whose reference
changes when the ego crosses the lane boundary, and it gives 0.94 / 0.45 / 0.05 m —
**inverting** the criticality ordering. A field built on it would run the criticality
axis backwards and produce a confident, entirely spurious transfer failure. The label
check is asserted in `replication/czb/overtake_field_check.py` for exactly this reason;
it costs nothing and it is the kind of check that pays for itself once.

**Roles come from the instructed vehicle, not from lateral span.** `load_cutin_trace`
identifies the target as the vehicle that moves sideways. In an overtake that rule is
not merely uninformative but **inverted**: here the *ego* pulls out (lateral span 2.24 m)
while the cyclist holds its line (0.16 m), so the cut-in rule labels the car as target
and the cyclist as ego. That is the mis-assignment recorded as review finding 1.5 in
`handover_2026-08-27.md`, and the mechanism is now identified rather than just observed.
`comfortzone.overtake.load_overtake_trace` assigns by vehicle dimensions instead — the
participant drives the car (1.88 m wide), the cyclist is unambiguous at 0.58 m.

## 3 The onset anchor

The truncation variants Ck need an anchor. The cut-in's convention is Ck = onset +
0.3 (k−1) s with C1 ending exactly at manoeuvre onset, so C1 is a genuine pre-event
baseline. For the overtake the candidate anchors are the ego's lane-change start and the
passing moment, and the data separates them cleanly:

- Under the **onset anchor**, the three clearance conditions are physically *identical*
  at C1 (clearance spread 0.000 m; they only diverge as the ego's lateral trajectory
  develops). Observed C1 intervention rates are 0.221 / 0.203 / 0.169 — nearly flat,
  with a small residual ordering.
- Under a **pass anchor**, C1 would sit 1.2 s before the pass, where the conditions
  already differ by 0.55 m, predicting a strong C1 ordering that the data does not show.

The onset anchor is adopted. The small residual C1 ordering that remains is the same
anticipation signature recorded for the cut-in as query R.1.Q3 — and its appearance here,
in a second scenario, upgrades that from a cut-in quirk to a property of the
repeated-exposure paradigm.

## 4 The finding: the field does not represent this scenario's criticality

`replication/czb/out/overtake_field_check.md`. Over the 15 cells, the field's deficit
orders the human intervention rate at Spearman **+0.402**, while a single geometric
scalar the preference function does not contain — the clearance the manoeuvre will end
with, i.e. the criticality label itself — orders it at **−0.833**.

The reason is structural, and visible in `p_lane` rather than inferred. The lane-entry
weight answers "does the car-following conflict geometry apply?", and in this scenario the
answer is *yes, fully*, for the whole response window in all three conditions: P_lane
never leaves 0.843–1.000. The scenario's manipulated variable is invisible to it.

Two candidate repairs were built and tested, both flag-gated and both defaulting off:

- **`lane_entry_bidirectional`** — the released form and the 2026-08-27 continuous form
  both clamp the lateral projection to *inward* motion, so an object moving laterally
  away is treated as stationary. That is harmless in a cut-in and discards the entire
  signal in an overtake. Projecting symmetrically over-corrects instead: P_lane collapses
  to 0 by C3 in every condition, because linear extrapolation of a still-developing
  lateral move over a ~2.2 s closure says the ego will have cleared comfortably. It ends
  up ordering the cells *negatively* (−0.537). Kept, default off, as a tested-and-rejected
  variant.
- **`lane_entry_shape_k`** — the S-shaped ramp (§5). It changes nothing here, because a
  shape function applied to a saturated input is a no-op.

The honest conclusion is that neither the overlap fraction nor its projection is the
right functional for this scenario. What varies across the conditions is not *whether*
overlap will occur — it will not, in any of them — but the size of the **lateral comfort
margin** at the pass. Passing a cyclist at 0.5 m is uncomfortable precisely while being
uncontroversially collision-free, which is a comfort quantity the preference function's
collision-oriented lateral machinery does not carry. Adding a lateral-clearance comfort
term is a change to the preference function's structure and therefore a review decision,
not one this card takes.

## 5 The S-shaped lane-entry ramp

Jonas's proposal of 2026-08-28: the ramp from no overlap to full overlap is currently
linear, and it should plausibly be a sigmoid — a sliver of predicted overlap does not yet
feel like a rear-end conflict, but once overlap is established the situation becomes one
quickly. Implemented as `lane_entry_shape(u; k)`, a normalized logistic with
g(0) = 0, g(1) = 1 exactly for every k and g(u; 0) = u, so the published linear ramp is
nested at k = 0 and every existing number is untouched by default.

Swept on the cut-in surface, where the overlap fraction actually spans its range
(`replication/czb/out/lane_entry_shape_check.md`):

| k | 0 (linear) | +8 | **+12** | +20 | +100 (≈ step) | −8 |
|---|---|---|---|---|---|---|
| RMSE | 0.1189 | 0.1156 | **0.1154** | 0.1230 | 0.1457 | 0.1211 |

The direction of the proposal is supported: positive k fits better, negative k (the
reflected shape) fits worse, and there is a genuine interior optimum at k ≈ 12. The
improvement is modest — 2.9% of the linear form's error — so the shape is real but not
dramatic on this design. A useful by-product: the k → ∞ limit is a step at half overlap,
which is effectively the released binary gate, and it is clearly the worst of the family.
That independently corroborates the 2026-08-27 decision to make lane entry continuous —
the gain there was not an artifact of choosing a linear ramp in particular.

**Whether to fit k is not settled here.** Fitting it would make k the first fitted
parameter upstream of the boundary, and the stage-0 result draws much of its force from
the field having no fitted constants at all. One shape parameter does not destroy that,
but it must be reported as a field parameter, and for any transfer test it would have to
be frozen at its cut-in value before a transfer scenario is scored. Raised as a query.

## 6 The transfer result, and the baseline correction it depended on

`replication/czb/out/transfer_overtake_summary.md`. Fitting stage 1 on the cut-in
(population median 5 352, between-driver σ 0.209, response sd 970) and scoring the 15
overtake cells:

| model | RMSE |
|---|---|
| frozen — nothing refitted (the roadmap's primary) | 0.176 |
| **free lapse only** — boundary level and spread frozen | **0.129** |
| free lapse + one level shift (the roadmap's secondary) | 0.110 |
| full refit (a ceiling, not a transfer model) | 0.113 |
| *chance — the overtake's grand mean* | *0.158* |

The pre-onset intervention rate is 0.081 in the cut-in and 0.198 in the overtake — 2.4×
higher before either manoeuvre develops. Frozen transfer is therefore worse than chance
for a reason that has nothing to do with the comfort boundary. Freeing **only the lapse**
— which the C1 cells identify on their own, and which by construction carry no boundary
information, since C1 ends where the field is zero — brings the model comfortably past
chance and to within 0.016 of the full-refit ceiling. The boundary level and spread
fitted on the cut-in do most of the work in the overtake, once the paradigm baseline is
matched.

The recommendation for card B.4 follows: the primary transfer analysis should freeze the
boundary and free each scenario's lapse, rather than freeing nothing. This is a weaker
concession than the roadmap's secondary "one uniform shift per scenario", which absorbs
the boundary itself and makes the test close to vacuous — visible above, where the level
shift buys 0.019 more and slightly beats the full refit.

## 7 The field-independent check that bounds all of this

`replication/czb/out/cross_scenario_consistency.md`. Because all 43 participants saw all
four Random scenarios, the one-scalar claim's central prediction can be tested with no
field at all: a driver who sits low in one scenario should sit low in the others.

Per-driver criticality-adjusted propensity, with split-half reliabilities of 0.93–0.98
(so the measure is clean), correlates across scenario pairs at **+0.50 to +0.74**, which
is **0.53 to 0.78 of the reliability ceiling**, mean **0.69**.

About 69% of the reliable per-driver signal is shared across scenarios. That is
substantial positive evidence for a common trait — the strongest non-field evidence
available for the one-scalar framing — and it simultaneously sets an upper bound: roughly
a third of reliable per-driver variation is scenario-specific, so no one-scalar transfer
model can explain everything, and B.4 should be scored against that bound rather than
against perfection.

## 8 What this card did not do

The ordered comfort/dread model is **not** fitted on the overtake. The study's third
question is scenario-dependent, and its Random-design wording for the cyclist overtake is
recorded as undocumented and "to be confirmed" in the dataset's own context file; the
column carries 0/1 here against the cut-in's 0/1/2. The intervention response (`CZB_1`)
is identically defined in both scenarios and is what transfers; the comfort/dread pair
remains cut-in-only until the question wording is confirmed.
