# The projected-conflict gate: a design note (card PC.1)

*2026-09-16. Authorized by Jonas the same day ("go with 1, and then 2"), which answered query
HS1.Q3 with "go". Written before any code or run, in the pattern of `docs/ltap_construction_note.md`:
the construction, its reduction to what exists, what it computes in each scenario as a prediction
made before the run, the pre-stated tests and rules, and where the reasoning may be wrong. The
worklog entry of the card records what the run then found.*

## 0 What the gate is for, in one paragraph

The project's model of a comfort-zone judgment is share = lapse + (1 − lapse) × GATE × Φ((AXIS −
LEVEL) / spread). The gate says whether the other road user counts yet; the axis and level say how
close is too close. On the cut-in the gate is card G.1's projection of the lateral clearance three
seconds ahead, and it is the part of the model that changes between scenarios. Card HS.1 tested the
obvious scenario-agnostic replacement, surprise as the onset, and found that in the cyclist overtake
and the left turn participants respond before anything surprising has happened; its reading was that
a response starts at *anticipated* conflict, which is what G.1's projection computes for a cut-in.
This card writes that reading down as one construction, computable the same way in every scenario
from the traces, and tests it where HS.1 failed.

## 1 What G.1's gate computes, and what it does not

G.1's gate is w = Φ((m_lat − (l0 + l̇ t_enc)) / s_l): the probability that the edge-to-edge lateral
clearance between the two cars, extrapolated t_enc = 3 s ahead at its current closing rate, has
fallen below m_lat. Fitted on the 288 post-onset cells of the second cut-in study it predicted the
90 pre-onset cells out of sample at 0.032 (m_lat 0.149 m, s_l 0.990 m) and improved the post-onset
score from 0.1137 to 0.1027 (`replication/czb/out/cutin2_gate.md`). It is lateral only. It does not
ask where the ego is going, because the ego drives straight; it does not ask whether the two cars
will be at the same place at the same time, because that is the axis's job (the looming rate carries
gap and closing speed); and it does not ask whether the cut-in car is ahead or beside, because in
that study it is always ahead. Three things are therefore implicit in G.1 that a generalization must
make explicit: the ego's path, what "clearance" is between two paths rather than two positions, and
that conflict means *same space*, not same space and time.

## 2 The construction

### 2.1 Paths

Each road user has a projected path over a horizon [0, t_enc] from the moment of evaluation. The
other road user's path is always its constant-velocity extrapolation in the world frame from its
recent motion, with the velocity taken over a window set by each study's measured position jitter:
0.3 s on the second study's 30 Hz traces and 1.0 s on the first study's 10 Hz traces, exactly HS.1's
settings and for HS.1's reasons (`replication/czb/hs1_situational_surprise.py`, docstring). The
participant cannot know the other road user's plan, so nothing else is defensible there.

The ego's path admits two readings, and the card runs both:

- **K, kinematic.** The ego's path is its own constant-velocity extrapolation, the same predictor.
  This is what a driver reads off the car's current motion.
- **P, planned.** The ego's path is its recorded future trajectory in the trace. The ego is
  automated in these studies and never responds, so its future is on file, and the participant was
  told what the car would do (turn left; overtake the cyclist; follow the lane). This is what a
  driver knows about an automated car's announced manoeuvre.
- **K ∪ P.** Conflict under either reading (the gate is the larger of the two). A driver of an
  automated car monitors both the current motion and the announced manoeuvre.

All three are computed identically in every scenario. No per-scenario geometry enters.

### 2.2 Corridors and clearance

Each body is a rectangle of the trace's width and length, oriented along its heading. A road user's
*corridor* over the horizon is the union of its body's positions along its projected path. The
*clearance* at the moment of evaluation is

> c = min over t in [0, t_enc] of the edge-to-edge distance between one body at time t and the
> other's corridor, taken over both orderings (the other road user entering the ego's corridor, or
> the ego entering theirs).

Same space, not necessarily the same time: this is a path crossing, not a collision prediction.
Whether the two will be there at the same time is what the axis measures. c is zero when the
projected paths overlap within the horizon, positive when they miss, and negative is not needed
(overlap is zero).

[Corrected 2026-09-16, before any run, on the evidence of the property tests. The corridor is the
projected *path* over an extended span (20 s in the implementation, longer than any clip's
remainder), while only the *positions* tested against the other's corridor are limited to the
horizon. As first written, both were bounded by the horizon, and a cut-in car ahead that is not
caught within three seconds then fell outside the ego's corridor, so the reduction of section 2.4
held only for cells with a time to collision under the horizon. G.1's gate has the asymmetry
implicitly: its lane strip is unbounded ahead, and the horizon limits how far the other car's
lateral motion is extrapolated. The horizon is therefore a statement about how far ahead the other
road user's motion is trusted, not about how far the ego's path extends. Section 2.4's premise
"within the corridor's length" is dropped; the reduction now holds for every post-onset cell. The
first bullet of section 7 is closed by the same correction. For the same reason the clearance has
*one ordering, by role*: the other road user's positions within the horizon against the ego's
path. The reverse ordering, the ego's positions against the other's extended path, extrapolates
the other's lateral motion for the whole path span, and the tests showed it opening the gate on a
cut-in car that would reach the ego's lane only after the horizon, which G.1 (rightly) leaves
closed. Consequence for section 2.5, the left turn under P: the gate opens only where the oncoming
car's positions within the horizon reach the ego's planned crossing of its lane, so at the primary
horizon it is open in the low-PET cells and closed where the oncoming car arrives later than three
seconds after the decision moment, and the horizon sweep is where the left turn speaks. The
overtake predictions stand: the cyclist ahead in the lane is on the ego's straight path.]

### 2.3 The gate

> g = Φ((m − c) / s)

with G.1's form and G.1's three constants: the minimum clearance m, its spread s, and the horizon
t_enc. Two further rules, both stated now:

- **Persistence.** The gate at the response moment is the maximum of g over the shown clip up to that
  moment. Once the other road user has counted, it keeps counting for the episode. On the cut-in this
  changes nothing (the clearance closes monotonically after onset and is flat before), and the
  instantaneous gate is reported alongside so the rule's effect is visible where it acts.
- **Only what was shown.** The clip window is the study's own: the video name's start and end stamps
  on the second study, and the ten seconds before the manoeuvre onset (`RANDOM_CLIP_LEAD_S`) up to the
  timepoint on the first study. Nothing outside the window enters the maximum, and the velocity
  window never reaches before the clip start.

### 2.4 Reduction to G.1 on the cut-in

The ego drives straight at v_e, so under K and P alike its corridor over [0, t_enc] is a strip of its
own width, along its lane, from its position to v_e t_enc ahead. The cut-in car is ahead by a gap
smaller than v_e t_enc in every post-onset cell of the second study (gaps at the response moment are
under 35 m; at the study's ego speeds the three-second strip is 60 m or longer), so it lies within the
strip's length throughout the horizon, and the edge-to-edge distance between its body at time t and
the strip is the lateral edge clearance l0 + l̇ t. That is decreasing when the car is cutting in, so
the minimum over the horizon is at t_enc: c = l0 + l̇ t_enc, and g = Φ((m − (l0 + l̇ t_enc)) / s) is
G.1's gate exactly, with m = m_lat and s = s_l. The other ordering (the ego's body entering the cut-in
car's corridor) gives the same lateral clearance and does not change the minimum. Property test 1 of
the implementation checks this reduction numerically on a straight-ego, laterally closing pair.

### 2.5 What it computes in the other two scenarios, predicted before the run

Written from the construction notes' measured geometry, not from any run of this card. If the run
disagrees, either the implementation or this reading is wrong, and the worklog says which.

**The cyclist overtake** (`docs/overtake_construction_note.md`; 3 clearances × 5 timepoints, C1 the
ego's lateral onset and C2 to C5 at 0.3 s steps after it). The cyclist rides steadily near the lane
edge; the ego approaches from behind in the same lane and pulls out to pass at 0.5, 1.0 or 1.5 m
edge-to-edge. Under K, while the ego is still driving straight behind the cyclist, the cyclist is
inside the ego's corridor as soon as it is within the corridor's length, so c = 0 and the gate opens
well before C1; persistence keeps it open through the pull-out, when the instantaneous projected
clearance would grow past m. Under P the ego's recorded future path bends around the cyclist, but
earlier in the clip its next three seconds are still straight and the cyclist within reach, so the
gate opens before C1 by the same route and stays open by persistence. Prediction: **open in all 15
cells under K, P and K ∪ P**, opening before C1. The gate does no work in the overtake; it must do no
harm, and the axis (the clearance at the pass, card B.1) carries the response.

**The left turn across path** (`docs/ltap_construction_note.md`; 18 cells, one decision moment at
13.5 s of trace time). The ego has slowed to 6.5 to 6.9 m/s on its approach and begins its turn at
13.9 to 14.1 s, 0.4 to 0.6 s after the decision moment; it occupies the oncoming lane from about
15.1 to 15.7 s. The oncoming car holds its lane at 13.9 or 19.4 m/s. Under K the ego's projected path
at the decision moment is straight along its own lane, parallel to the oncoming lane and a lane's
offset away, so neither body enters the other's corridor and the gate is **closed in all 18 cells**.
Under P the ego's recorded future crosses the oncoming lane 1.6 to 2.2 s after the decision moment,
within the three-second horizon, so the ego's body enters the oncoming car's corridor and the gate is
**open in all 18 cells** regardless of the oncoming car's distance; the oncoming car's own arrival at
the crossing (2.5 to 6.7 s after turn onset) is what the axis measures, not the gate. Prediction: K
fails the left turn by construction, because a constant-velocity projection cannot know the ego is
about to turn; P and K ∪ P pass, and again the gate does no work there.

These predictions say what the card can and cannot find. It cannot find that the gate carries the
response in the overtake or the left turn; in both, the other road user counts from the outset. What
it can find is (a) whether a projected conflict computed this way, with the cut-in's own constants
frozen, is open wherever people respond and costs nothing where it is open, (b) which reading of the
ego's path is needed, and (c) whether the horizon that the cut-in cannot identify is constrained by
the other scenarios. If K fails the left turn as predicted, the card's substantive result is that the
anticipation participants show there uses knowledge of the ego's manoeuvre that no projection of
current motion carries. That is a finding about what the gate must know, and it is the reason both
readings run.

## 3 The tests and their rules, pre-stated

**Test 1, the cut-in.** G.1's protocol unchanged: the 288 post-onset cells fit the EL.1 linear rule
with the gate's m and s jointly (multi-start as G.1), leave-one-starting-TTC-out held out, the 90 CP1
cells predicted out of sample from the full post-onset fit. The gate value per cell comes from the
construction of section 2 applied to the trace, not from G.1's lateral formula; the reduction of
section 2.4 says the two agree, and the run reports the largest absolute difference between the
construction's c and G.1's l0 + l̇ t_enc over the 378 cells as a check of the implementation (rule:
under 0.05 m, or the card stops and reports). K and P coincide on the cut-in, so one fit serves both.
Criteria, G.1's: **CP1 out of sample below 0.05, and post-onset held out within 0.01 of G.1's gated
score, 0.1027 + 0.01 = 0.1127.** Horizon: primary 3 s, the verdict is stated there; sweep {3, 4, 5,
6} s reported without a verdict, to show what the cut-in tolerates.

**Test 2, the left turn.** The cut-in's fitted m and s frozen. Per cell, g at the decision moment
under K, P and K ∪ P, with and without persistence over the shown window. A reading of the ego's path
is **consistent** with the scenario if the gate is open (g ≥ 0.5) in every *engaged* cell, where an
engaged cell is one whose share intervening exceeds the scenario's lowest cell by 0.2; the margin is a
convention (query PC1.Q3), and the count of engaged cells at margins 0.1 and 0.3 is reported without a
verdict. Cost: B.3.v2's distance rule (leave-one-PET-level-out, distance alone 0.056) refitted with
the gate multiplied in, m and s frozen; the gated score must be **within 0.01 of the ungated one**.
Where the gate is open in every cell the cost is zero by construction and the report says so.

**Test 3, the overtake.** The same constants frozen. Per clearance, the time the gate opens relative
to the ego's lateral onset under each reading, with and without persistence, against the five
timepoints; consistency as in test 2 over the 15 cells. No cost test: the overtake has no fitted
rule on file (query B1.Q1; `out/transfer_overtake_summary.md` scores the old field, not a rule), so
the test is descriptive there.

**Adoption.** A reading credited in test 1 and consistent in tests 2 and 3 at the primary horizon is
adopted as the project's gate, in the order K, P, K ∪ P (the least knowledge first). If a reading is
consistent only at a longer horizon in the sweep, that horizon is reported with the cut-in's score at
it, and adoption is deferred to Jonas (a query, not a verdict). If no reading is credited and
consistent, the finding is stated as such, with the scenario that breaks each reading.

## 4 Traps carried over from HS.1

- **Measure each study's jitter floor before choosing any window.** HS.1's first run took the second
  study's 30 Hz floor to the first study's 10 Hz traces and produced onsets eight seconds early that
  were jitter. The velocity windows above are those measurements; the card re-reads them from HS.1's
  constants rather than choosing again.
- **Only what participants were shown.** Every gate value, maximum and onset time is restricted to
  the clip window of that cell. The persistence rule makes this matter more than it did in HS.1.
- **Roles by the scenario's own rule.** The three loaders identify the ego differently (lateral span
  on the cut-in, width on the overtake, heading change on the left turn) for reasons each documents;
  the card reuses HS.1's scene loaders, which carry those rules, and never assigns roles itself.
- **Body dimensions from the traces.** Widths and lengths are the trace columns, as G.1 and HS.1 used
  them; nothing is assumed.

## 5 Implementation plan

- `src/comfortzone/conflict.py`: oriented rectangles from position, heading, width and length; the
  projected path of a track over a horizon (constant velocity from a window, or the recorded future);
  corridor clearance between two projected bodies as in section 2.2 (the exact distance between
  convex polygons, minimized over the horizon on the trace's own time grid); the gate, the persistence
  maximum, and the cut-in reduction as a function that can be tested against G.1's formula.
- `tests/test_conflict.py`, in the `check()` style: the reduction to G.1 (section 2.4) on a straight
  ego and a laterally closing target; c = 0 when paths cross within the horizon and positive when
  they miss; symmetry of the two orderings on a symmetric pair; persistence never lowers the gate;
  a turning P path opens against a straight oncoming car while K stays closed (the left-turn
  prediction in miniature); the overtake prediction in miniature (a body ahead in the lane gives c =
  0 as soon as it is within the corridor's length).
- `replication/czb/pc1_projected_conflict.py`, pre-stated in its docstring from this note, importing
  HS.1's `scene_tracks` and `study2_scenes`, G.1's fitter and folds, B.3.v2's cells and folds; output
  `replication/czb/out/pc1_projected_conflict.md` and `out/pc1_gates.csv` (one row per cell, reading
  and horizon).

## 6 Queries raised by the design

- @PC1.Q1(judgment, jonas): the P reading uses the ego's recorded future as "what the participant knew
  the automated car would do". Is that an acceptable reading of the study instructions for the three
  scenarios, or did participants only know the scenario type? If the latter, P overstates what they
  knew, and K ∪ P's success on the left turn would be a statement about the instruction, not about
  anticipation.
- @PC1.Q2(judgment, review): persistence (once counted, keeps counting) is a rule added here, not in
  G.1. It is harmless on the cut-in and necessary in the overtake once the ego has pulled out. An
  alternative is a decay; no data on file distinguishes them, so the simplest rule is taken.
- @PC1.Q3(minor, review): the engaged-cell margin of 0.2 above the scenario's floor is a convention
  chosen for the test; both neighbors are reported.

## 7 Where I may be wrong

- The reduction in section 2.4 assumes the ego's corridor is longer than the gap in every post-onset
  cell. The run checks this with the 0.05 m rule; if a few large-gap cells break it, the construction
  and G.1 differ there, and the report says by how much before any fit is read.
- The overtake prediction under P depends on the ego's straight stretch before the pull-out being
  long enough for the cyclist to enter the corridor. If the ego pulls out while the cyclist is still
  beyond the corridor's length, P closes on the overtake and only K opens; that would make K ∪ P the
  only reading that passes all three, which is a weaker result than P alone.
- The left-turn reading under P assumes the ego's body reaches the oncoming lane within 3 s of the
  decision moment; the construction note gives 1.6 to 2.2 s. A slower turn in some traces would close
  the gate at the primary horizon and open it in the sweep.
- Persistence over the shown window could open the gate at C1 in the overtake through a corridor
  contact many seconds earlier. That is the intended behavior, but it means the overtake's gate
  states are not informative about the timing of anticipation; the opening times in test 3 are.
