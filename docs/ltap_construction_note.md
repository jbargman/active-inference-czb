# The left-turn-across-path scenario: construction note (card B.3.v2)

*2026-09-02, tier-1 session, queue item (1) of the standing handover. Per Jonas's ruling
of 2026-08-29 (R2.Q4) the scenario is built as a **comparator-class construction**, with
the field alternative documented alongside and the pros and cons of both routes written
down. This is the note to review before any code; it follows the lane-entry note's
pattern. Every number comes from `replication/czb/out/ltap_geometry.md` (script
`replication/czb/ltap_geometry.py`, written for this note) or from the tracked outputs
named at the point of quotation. Opinions are marked as such.*

## 0 The scenario in one paragraph, from the traces

The ego approaches a T-junction at 12.7 m/s, slows to 6.5–6.9 m/s, and begins a left
turn at 13.9–14.1 s of trace time; it is inside the oncoming lane from about 15.1 to
15.7 s. The oncoming vehicle travels straight at a constant 13.9 m/s (50 km/h) or
19.4 m/s (70 km/h). The ego's script is identical in all 18 traces; only the oncoming's
start position (one per PET level, 0 to 4 s in 0.5 s steps) and its speed vary. So at a
given design PET the oncoming's *time to the conflict point* at turn onset is matched
across the two speeds (2.5 to 6.7 s across PET levels, equal to within 0.2 s between
speeds), while its *distance* differs by the speed ratio (34 to 91 m at 50 km/h, 48 to
130 m at 70 km/h). That is the design's whole value: it separates time from distance by
construction, which the first cut-in study could not do and the second had to be built
to do. The Random design's response surface is 9 PET levels × 2 speeds, 172 trials per
cell, P(intervene) from 0.88 down to 0.11, with intervention *lower* at 70 km/h at every
PET level. The Button design (50 km/h only) shows clips of 0–13.5 s of trace time, which
end before the turn begins; its presses cluster at 12.6–12.9 s regardless of PET, so the
Button decision is "would I yield", made on the approach, and the press rate rather than
the press time carries the criticality.

## 1 What the response surface already says: distance, with a speed residual

The cleanest fact in the project's data on the time-versus-distance question is here,
and it needs no model. If the response depended on time to the conflict only, the two
speeds would agree at matched PET; they do not, and the time-only prediction errs by
−0.20 on average (RMS 0.21: the 70 km/h cells intervene far less than their 50 km/h
partners). If it depended on the oncoming's distance only, the 70 km/h cell at PET p
should match the 50 km/h cell at the PET with the same distance; interpolating on the
50 km/h distance–response curve gets within RMS 0.08, but with a signed error of
+0.06: the 70 km/h cells still intervene *less* than a pure-distance reading predicts,
consistently across the five PET levels where the interpolation is in range.

So the LTAP response is mostly a distance judgment, with a residual in the direction
"same distance, faster oncoming, less intervention" that a single scalar in either
distance or time cannot carry. The way I read it, that residual is the second axis the
ellipse design note was looking for, and LTAP is the scenario where a two-observable
form will earn its place if it does anywhere. It is also the same pattern the pipeline
review found in the cut-in (gap orders matched-TTC cells; speed enters with the opposite
sign to a worst-case counterfactual), now in a crossing geometry.

## 2 The comparator-class construction (the route being built)

**Roles.** The ego is the vehicle whose heading changes; the oncoming is the one with
constant heading. Vehicle IDs differ per file, so the loader assigns roles by yaw span.
This is a third role rule, after the cut-in's lateral-span rule and the overtake's
vehicle-dimension rule, and for the same reason in each case: the instructed vehicle is
the one performing the manoeuvre, and what identifies it differs by scenario. The
overtake note's warning applies unchanged: do not reuse the cut-in loader, whose
lateral-span rule would pick the turning ego as the "target".

**The decision moment.** For the Random design the clip's end time is not recorded in
the joint file (`video_clip_name` is Button-only) and is treated here as an assumption
to verify (query B3.Q1): the natural candidate is the same 13.5 s window as the Button
clips, which ends 0.4–0.6 s before turn onset. All covariates are read at the clip end.
There is no timepoint series, so the scenario yields a criticality × speed surface and
not a criticality × time surface; cross-scenario comparison is on criticality or per
driver, as the B.3.v2 card already says.

**The two observables**, both read at the decision moment:

1. **Arrival-time separation** t_sep: the oncoming's time to the conflict point minus
   the ego's time to clear it under the scripted turn. Since the ego's script is fixed,
   t_sep is the design PET plus a constant, and the oncoming's time-to-arrival at onset
   (2.5–6.7 s) is its measurable proxy; either is a *time* axis.
2. **Oncoming distance** D to the conflict point at the decision moment (34–130 m
   across the design), or equivalently, at fixed t_sep, the oncoming speed; a *distance*
   axis.

Their criticality orientations are −log t_sep and −log D (smaller is more critical, as
the data dictionary's gotcha 2 records for LTAP).

**The rules to fit**, in the order of the ellipse note's card EL.1, on the 18 cells with
the registered R.2 fit (lapse + probit, weighted least squares), folds
leave-one-PET-level-out (nine folds; grouped, so the fit must transfer across the
design's main axis):

- (a) 1D −log D and (b) 1D −log t_sep, for the record; section 1 predicts (a) beats (b);
- (c) the linear 2D rule w(−log D) + (1 − w)(−log t_sep), one extra parameter;
- (d) the quadratic form in the same two axes (the ellipse; scale fixed by convention,
  two extra parameters).

Decision rule, pre-stated as in EL.1: a second axis earns its place if (c) or (d) beats
(a) by more than 0.01 held-out wRMSE; the quadratic form is preferred over the linear
rule only if it wins by more than 0.01. With 18 cells the noise floor and the chance
reference are to be reported as in R.2, and a bootstrap over cells alongside, because
the margins will be closer to the floor than on the 288-cell cut-in surface.

**The per-driver level.** The stage-1 estimator on the chosen covariate's value at the
decision moment (no running maximum is needed: one moment per clip), hierarchical lapse,
then the B.4 transfer as amended: level population frozen from the cut-in, LTAP lapse
free, scored against chance, the LTAP refit ceiling, and the 0.69 field-free bound. The
scale-confound convention of the ellipse note (§5) applies if (d) is the chosen form.

**Property tests** (the `tests/test_cutin.py` style): roles assigned correctly on all 18
traces (the ego's yaw span exceeds 200°, the oncoming's is under 5°); turn onset within
0.2 s across traces; measured PET monotone in design PET at each speed; distance at
onset at 70 km/h equals distance at 50 km/h times 19.4/13.9 to within 5% at each PET.

## 3 The field alternative (documented, not built)

The released model's intersection scenario is the mirror image of this one: its ego
drives *straight* through the junction and the *other* vehicle turns across its path
(handbook chapter 04; the scenario's norms in `external/aica/src/intersection/reward.py`
penalize the other vehicle for ignoring the light, cutting the corner arc, and leaving
the paved area). Here the ego turns. Two things follow for a field construction.

The **safety term does not apply as released**: it is a car-following counterfactual
(lead ahead, same direction, lead brakes hard) and the oncoming vehicle is neither ahead
in the ego's lane nor same-direction until the ego has entered the oncoming lane, by
which time the decision is over. The **collision term** applies only at overlap. So a
field route would need a new term, which the original B.3 card sketched: gate the
conflict terms by predicted *co-occupancy* of the conflict zone (the lane-entry weight's
idea with lateral overlap replaced by zone co-occupancy), and give the magnitude a
counterfactual severity (the relative speed at the conflict point if the two occupancy
intervals overlap under "ego continues its scripted turn, oncoming holds speed").

Pros of that route: it stays in one family with the cut-in field; the co-occupancy gate
is a genuine physical statement; the counterfactual makes "how bad" explicit. Cons, and
in my opinion they are decisive after R.2: the released model never exercised a turning
ego, so the term is ours from the ground up, with at least two new assumptions (the
turn-completion profile and the counterfactual's speed assumptions) that nothing
upstream calibrates; the gate would reproduce the cut-in's failure mode, since
co-occupancy at closure depends on the ego's turn pace in the same way the lane-entry
projection depended on the target's lateral pace, and the data here (section 1) point
at distance, not at a projected overlap; and the counterfactual magnitude would scale
with the oncoming's speed at matched time in the direction the data reject (faster
oncoming, *more* severity in the counterfactual, *less* intervention in the data). A
version of it could be scored as a fifth model in the section-2 comparison if anyone
wants the sentence "the field alternative was tried on LTAP"; I would not build it
first.

## 4 Two things the construction should record about the data

- **The Button LTAP labels.** Nine criticality labels map to five distinct videos on the
  Button side (data dictionary, gotcha 3); `criticality_from_video` is the truth there,
  `criticality_label` on the Random side. The Button design has the 50 km/h speed only,
  and PET 0 and 0.5 exist only in the Random design.
- **The measured PET offset.** With the conflict band defined as ±1 m around the
  oncoming's lateral position, measured PET exceeds the design value by 0.7 to 1.2 s
  (mean 0.96 s). The design's conflict-zone extent is not documented; the offset is
  near-constant and does not affect any ordering, but any *absolute* statement about
  PET should quote the design value and say how the zone was defined.

## 5 Cards

- **B.3.v2 (this note's construction).** The loader `src/comfortzone/ltap.py` (roles by
  yaw span, turn onset, conflict point, t_sep and D at the decision moment), the
  property tests above, and `replication/czb/ltap_two_axis.py` running the section-2
  comparison with its pre-stated rule; output `out/ltap_two_axis.md`. Query B3.Q1 (the
  Random clip end) is to be resolved before the covariates are read.
- **Then EL.2** as specified in the ellipse note, with LTAP as the scenario on which the
  second axis is expected to matter most.

## 5b Result (added 2026-09-02, same day)

*Card B.3.v2 ran (`replication/czb/ltap_two_axis.py` → `out/ltap_two_axis.md`; loader
`src/comfortzone/ltap.py`, 62 property checks in `tests/test_ltap.py`; query B3.Q1 resolved
by assumption at a 13.5 s decision moment). Held out over leave-one-PET-level-out folds on
the 18 cells: distance alone 0.056, arrival-time separation alone 0.112, the linear 2D rule
0.054 (weight 0.81–0.90 on distance in every fold), the quadratic form 0.063, the oncoming's
looming rate 0.054; chance 0.288, sampling-noise floor 0.033. The pre-stated rule: neither
two-axis model beats distance alone by 0.01, so one axis suffices on the left turn, and that
axis is distance (or the oncoming's looming rate, which at one speed per cell is a monotone
function of distance and scores the same). Time alone is far worse. Section 1's "speed
residual" is real but small: the linear rule puts about 12% of its weight on arrival time,
not enough to earn the second axis by the rule. Section 1's remark that looming would
predict the wrong sign was wrong and is withdrawn: at matched arrival time the faster
oncoming vehicle is farther and looms less, which is the observed direction; the test
settles it. One caveat: the 50-resample cell bootstrap in the report (reduced from the
pre-stated 200 after 2.7 CPU-hours without completing) is the uncertainty statement, and
with 18 cells it is coarse.*

## 6 Where I may be wrong

- The "distance with a speed residual" reading rests on interpolating the 50 km/h
  distance–response curve at five PET levels; the residual is consistent in sign but
  0.06 in size, against cell standard errors of roughly 0.03–0.04 (172 trials at
  P ≈ 0.5). It is suggestive, and the section-2 comparison is the test.
- The Random clip's end time is assumed equal to the Button window's. If Random clips
  run past turn onset, the decision moment moves and the covariates change; the ordering
  arguments survive, the absolute distances do not.
- The measured geometry uses a ±1 m band; a wider or narrower band shifts every t_in and
  t_out by the same amount and leaves the between-condition differences alone.
- Section 3's judgment that the field route would fail for the cut-in's reasons is an
  inference from the pipeline review, not a result on this scenario.
