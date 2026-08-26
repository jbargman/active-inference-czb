# Using the Study 1/2 clip-rating and button-press data for comfort-zone boundaries

*Written 2026-08-26 after going through `external/01_studies/` and its two documentation
files. This is a proposal for discussion, not a plan of record, and it deliberately argues
with parts of the sketch Jonas gave. No implementation has been started.*

## 0 The one-paragraph version

This dataset fits the comfort-zone boundary work better than I expected, and the reason is
structural: **the two paradigms observe the same latent quantity in complementary ways.**
The fixed-clip designs stop a clip at a known time and ask whether the participant would
intervene, which samples the **cumulative** response-time distribution at six points per
criticality level; the button design lets the participant choose the moment, which samples
the **density**. The accumulator model predicts both from one parameter set. Further, **the
ego vehicle never responds** in any clip, so the comfort-zone field along each clip is a
fixed, computable function of time rather than something that has to be inferred jointly
with the parameters — which is what makes our existing method, needing only the preference
function and recorded kinematics, applicable almost directly.

Section 2(b) is the substantive part and has been revised after Jonas's clarification: the
**fixed-clip binary is the primary fitting target**, with accumulation running only to the
clip's end time, and the button press times are held back for validation. I checked the
identity that this framing implies — P(intervene | clip ends at T) should equal P(press
time ≤ T) — and it holds well at high criticality while showing a systematic excess of
early pressing elsewhere, consistent with the documented order confound. My judgment is
that the fit is feasible; §2(b2) sets out what it would and would not establish.

## 1 What is actually in the folder

`external/01_studies/01_Studies/` holds three directories. **`02_Cut-in` and `03_CAMP` are
empty**; only `01_Sequence_Random_ButtonPress` has content (16 MB, 71 files).

**Two analysis-ready tables.**

| file | shape | contents |
|---|---|---|
| `Sequence_Random_Combined_Data.csv` | 15 868 × 38 | Sequence + Random fixed-clip designs, 80 participants (33 + 47) |
| `Random_Button_Joint.csv` | 20 640 × 43 | Random + Button designs stacked, 43 participants who completed all four sessions |

**67 kinematic trace files** under `Kinematics/`, one per stimulus clip, holding the
simulator's full vehicle-state time series at 10 Hz: position, speed, acceleration,
heading, lane, bumper positions and bounding boxes for every vehicle in the scene.

**Scenarios and criticality levels.** Cut-in by car (TTC2–TTC8) and by truck (TTC4–TTC8);
LTAP left turn across path (PET 0–4 s, at 50 and 70 km/h); cyclist overtake (0.5/1/1.5 m
lateral clearance); truck overtake (0–1 m truck lateral offset); plus cyclist-following and
truck-lateral-movement variants present only in the Button design.

**Three paradigms.** Sequence (33 participants, Aug 2025, clips shown in temporal order),
Random (47 participants, Jan–Feb 2026, clips shuffled), and Button (the same 47, sessions
3–4, one session framed as supervising an L2 system and one as driving manually). The
fixed-clip designs yield a 0–10 perceived-safety rating plus a binary "would you intervene";
the Button design yields a **timed, right-censored intervention moment**.

### 1.1 Two documentation discrepancies worth resolving before any work starts

- The data dictionary describes a file called
  `Combined_Study_Design_criticality_coded_common_support.csv`; what is present is
  `Sequence_Random_Combined_Data.csv`. The row and column counts match the dictionary
  (15 868 × 38), so I believe it is the same file renamed, but that should be confirmed.
- The dictionary's Part 2 filter recipe requires a framing column derived from
  `Button_Study_Design_with_Kinematics.csv`, which is **not in the folder**. Without it the
  ADAS-versus-manual factor can only be recovered from `Block_Name`
  (`Trigger_Trials_ADAS` / `Trigger_Trials_HDV`), which the dictionary says is possible.
  Worth asking for the missing file anyway.

### 1.2 Three data-quality findings that are not in the documentation

I checked these directly against the trace files; all three matter for any use of the
kinematics.

1. **`Acceleration_mps2` is unsigned, and I could not determine what it represents.** It is
   never negative in any of the 67 files. Jonas's suggestion that it is simply *deceleration*
   is close but does not fit: it is also positive while a vehicle accelerates, and it is
   non-zero (0.04–0.43 m/s²) while the cut-in vehicle holds a rigorously constant speed
   through its lane change. My next hypothesis, that it is the magnitude of the total
   acceleration vector including the lateral component, does not fit either — over the
   manoeuvre it correlates only 0.16 with √(a_lat² + a_lon²) and is several times smaller
   than the lateral acceleration implied by the trajectory. Over a whole clip it correlates
   0.89 with |d(speed)/dt| once the teardown frames are removed, so it tracks acceleration
   magnitude at gross scale without matching any candidate definition at fine scale.
   **Practical consequence, which is unaffected by the ambiguity: do not use the column.
   Differentiate `Speed_mps` instead, which is clean.** Worth asking the data owner what the
   column is, since it may indicate how the traces were exported.
2. **The first and last frames are teardown artifacts.** At t = 0 every vehicle reports a
   near-zero speed before jumping to its true value, and the final frames collapse toward
   zero as the simulation is torn down. Roughly 8.5% of rows are affected, all at the head
   and tail. Dropping them is straightforward but must be done, otherwise every derived
   acceleration carries spikes of 100–250 m/s².
3. **Truck assets have a broken bounding box**: `Length_m = 0.00` and `Width_m = 1.48` for
   every truck, against 5.01 × 1.88 for cars and 1.66 × 0.58 for cyclists. Any
   bumper-to-bumper or looming-angle computation involving a truck needs dimensions supplied
   externally. This probably also explains the constant offset the dictionary reports
   between `TTC_true` and `kin_TTC_s`.

### 1.3 The two findings that make this dataset valuable

**The ego vehicle does not respond.** In the cut-in clips the ego holds exactly
30.547 m/s for the entire clip; the only deviation is the final teardown frame. The truck-
and cyclist-overtake clips are likewise constant-speed, and the LTAP ego follows a scripted
turn profile that is the same across PET levels. This is unusual and valuable. In
naturalistic data the driver's own response truncates the *trajectory* — the vehicle slows,
so the state that would have followed is never observed, and the calibration has to work
backward from an onset. Here the participant's press truncates only their *viewing*: the
underlying trajectory is scripted, identical for everyone, and fully recorded in the trace
files. The comfort-zone field along each clip is therefore a fixed function of time that can
be computed once per stimulus and reused for every participant and every repetition, with
each person's press or clip-end time simply indexing into it.

**The press timing carries the criticality signal even where the binary response does not.**
The documentation warns that cut-in press rates saturate (99.5%), which makes the binary
outcome uninformative, and recommends a windowing fix. Checking the traces against the
press times shows the situation is better than that warning implies. The lane change begins
at trace **t = 15.32 s in every cut-in clip**, and every clip starts at trace t = 5.0 s, so
the manoeuvre onset falls at video time 10.32 s throughout. Median press times are:

| level | TTC2 | TTC3 | TTC4 | TTC5 | TTC6 | TTC7 | TTC8 |
|---|---|---|---|---|---|---|---|
| median press, s after onset | 0.10 | 0.36 | 0.36 | 0.33 | 0.61 | 1.01 | 1.80 |

Monotone in criticality, tightly locked to the manoeuvre, and all within the lane-change
window (which closes at 2.4–2.6 s after onset). The timing is a clean dose-response even
though the binary is saturated. The tail of late presses does fall into the car-following
phase and does need the windowing the documentation recommends, but the central mass does
not.

One caution follows immediately: a median press 0.10 s after onset at TTC2 is faster than a
simple keypress reaction time. Participants had seen every clip about four times in the
earlier Random sessions, so the fastest presses are **anticipatory rather than reactive**.
That is a limitation for a pure accumulator account — though it may be an opportunity for an
active-inference one, since a forward-simulating model produces anticipation naturally where
a stimulus-driven accumulator does not.

## 2 Reacting to the proposed steps

### (a) "Create a cut-in use-case implementation fully, and test it on synthetic data"

Agreed in direction, but I would split it, because most of the cost is in a part we do not
need yet.

Per `HANDOFF.md` §7, the comfort-zone method depends only on the preference function and
recorded kinematics, not on the closed-loop agent. For everything in steps (b) and (c) we
therefore need only:

- **(a1) the cut-in preference function**: extending the lateral/lane geometry and the
  collision term to a vehicle that is *between* lanes and closing laterally. This is
  cheap — the preference function is already implemented in `src/aidriver/preferences.py`
  following the released code — and it unlocks the entire fitting and transfer programme.

The full closed-loop cut-in agent is a different and much more expensive object:

- **(a2) the closed-loop cut-in scenario**: a scripted cut-in target, a decoder that sees
  it, norms for a lane-changing other vehicle, and the CEM planner in the loop, at roughly
  18 s of CPU per simulated timestep.

My recommendation is to do (a1) first and treat (a2) as optional. (a2) earns its cost only
if we want the model to *predict* what a driver would do after the boundary is crossed, or
if we want the scenario-switching argument of handbook chapter 04 demonstrated on a fourth
scenario. Neither is needed to establish the boundary itself. Testing on synthetic data, as
Jonas suggests, is right for both, and for (a1) the natural synthetic test is the
property-based one we already use: the closed-form boundary against the numeric level set.

### (b) "Parameter fitting of the accumulation model, with hard braking responses as the proxy for the CZB"

*Revised 2026-08-26 after Jonas clarified the intended use of each paradigm. The revision
changes the recommendation substantially, and in his direction.*

**The corrected picture of what each paradigm gives us.** The two designs are not two ways
of measuring the same observable; they are two observations of the same latent process:

| paradigm | what the participant does | what we get | what the model predicts |
|---|---|---|---|
| Sequence / Random (fixed clip) | watches a clip that **stops at a fixed timepoint**, then answers | binary "would you intervene" (`CZB_1`), a 0–10 perceived-safety rating, and a braking-level question | P(boundary crossed by time T) — the **CDF** of the response-time distribution, evaluated at the clip's end time |
| Button press | watches continuously, presses when they would intervene; **the video ends at the press** | a right-censored press time | the response-time distribution itself — the **density** |

That is the key structural insight, and it is Jonas's framing rather than mine. The
fixed-clip binary is not an inferior substitute for timing: it is the *cumulative*
observation of exactly the quantity the accumulator predicts. Because each temporal variant
C1–C6 is the same event truncated at onset + 0, 0.3, 0.6, 0.9, 1.2 and 1.5 s, the
fixed-clip design directly samples the response-time CDF at six points, for each of three
criticality levels. Accumulation runs from clip start to the clip's end time and no further
— exactly as Jonas puts it, "you only have accumulation until the first brake onset".

**So the primary fitting target should be the fixed-clip binary**, not the button times. The
observable is the 3 × 6 surface of P(intervene), which the study's own documentation
reports and which is monotone in both dimensions:

| P(intervene) | C1 (pre) | C2 (0.3 s) | C3 (0.6 s) | C4 (0.9 s) | C5 (1.2 s) | C6 (1.5 s) |
|---|---|---|---|---|---|---|
| TTC4 | 0.117 | 0.296 | 0.745 | 0.770 | 0.867 | 0.918 |
| TTC6 | 0.071 | 0.092 | 0.306 | 0.444 | 0.495 | 0.786 |
| TTC8 | 0.046 | 0.071 | 0.204 | 0.270 | 0.347 | 0.357 |

Eighteen cells with a clean dose-response along both axes is a well-posed target for a
threshold-crossing model with a participant-level threshold distribution. C1 is a genuine
pre-event baseline and measures response bias, which the model needs anyway.

**On "hard braking as the right one to go for", one caution.** The braking-level question
means different things in the two designs, and the study documentation is emphatic that
they should not be pooled. In the **fixed-clip** designs, `CZB_2` for cut-in asks what the
participant expects the *vehicle* to do if they do not intervene (nothing / brake gently /
brake hard) — an expectation about the automation. In the **button** design the cut-in
follow-up asks whether the *participant* would brake gently or hard — their own action. If
the intended construct is "the situation demands hard braking", the fixed-clip version may
actually be the better of the two, because an expectation about required braking is a
fairly direct read-out of perceived kinematic urgency and is less contaminated by trust in
the automation or by willingness to intervene. My suggestion is to use it, but to describe
it as *expected required braking* rather than as the participant's own action, and to keep
it separate from the button follow-up. I may have misread which question Jonas has in mind,
and it is worth confirming before it drives the modeling.

The graded structure is still available and still valuable: "expect nothing" / "expect gentle
braking" / "expect hard braking" is an ordered three-level response on the same clips, which
maps naturally onto two nested boundary levels rather than one — our comfort and dread
levels, which the method already expresses as a single choice of allowed deceleration.

**What the button data is for.** Validation rather than fitting, and it is well suited to
it, because it observes the density where the fixed-clip design observes the CDF. If the two
paradigms measure the same latent process, then

> P(intervene | clip ends at T)  should equal  P(press time ≤ T)

for the same stimulus and the same participants. That identity is directly checkable, and
I checked it. Converting button press times to time-since-onset (the lane change begins at
trace t = 15.32 s, clips start at trace t = 5.0 s, so onset falls at video time 10.32 s):

| | C2 (0.3 s) | C3 (0.6 s) | C4 (0.9 s) | C5 (1.2 s) | C6 (1.5 s) |
|---|---|---|---|---|---|
| TTC4 fixed-clip / button | 0.302 / 0.416 | 0.733 / 0.677 | 0.767 / 0.785 | 0.866 / 0.875 | 0.919 / 0.922 |
| TTC6 fixed-clip / button | 0.093 / 0.355 | 0.308 / 0.494 | 0.453 / 0.605 | 0.512 / 0.672 | 0.797 / 0.759 |
| TTC8 fixed-clip / button | 0.070 / 0.203 | 0.215 / 0.291 | 0.273 / 0.378 | 0.366 / 0.407 | 0.366 / 0.453 |

The identity holds well at high criticality and late timepoints (TTC4 from C3 on, agreement
within 0.06) and shows a systematic **excess of early pressing** in the button paradigm
elsewhere, largest at intermediate criticality (TTC6, up to +0.26). The direction is exactly
what the order confound and the four prior viewings predict: by the button sessions
participants knew what was coming. To me this is encouraging rather than discouraging — the
*shape* is shared and the discrepancy looks like a threshold shift rather than a different
process, which means one accumulator with a paradigm-level shift parameter should fit both.
It also happens to be a quantitative contribution to the study's own Stage 2 question.

**The revised proposal for (b), then**: fit the boundary level *c* and the accumulator
parameters to the fixed-clip binary surface, with a participant-level random effect on *c*;
predict the button press-time distribution as a held-out test, allowing one paradigm-level
shift; and use the ordered braking-level response to estimate two nested boundary levels
rather than one.

### (b2) Is this feasible, and what would it mean?

**Feasible, in my judgment, and for concrete reasons.** The stimulus kinematics are known
exactly and are identical across participants, because the ego never responds — so the
comfort-zone field along each clip is a fixed, computable function of time that does not
have to be inferred jointly with the parameters. The design gives 18 cells per vehicle type
on the cut-in alone, with 47 participants and roughly four repetitions each, which is ample
for a threshold model with a random effect. The response-time CDF is observed at six points
and the density independently, so the model is over-identified rather than under-identified.
Further, three more scenarios exist for transfer.

The parameters to estimate are few: the boundary level *c* (per participant), an
accumulation gain, a decision threshold, and a noise scale — with the accumulator already
implemented and validated against the authors' deposit at median 0.0 s onset error. The
substantive new work is the cut-in preference function (a1), not the fitting machinery.

**What it would mean, stated carefully.** A successful fit would establish that a single
scalar field derived from the active-inference preference function, with one boundary level
per person, reproduces when observers judge intervention to be warranted across
criticality and time. If the same *c* then transfers unchanged to LTAP and the two overtake
scenarios, that is evidence for the central claim of the method: that comfort-zone
boundaries are one scalar level set rather than a family of per-scenario kinematic
thresholds.

What it would **not** establish is equally important and should be written into any
abstract. This is an observer's judgment about video, under an imagined control authority,
from a crowdsourced sample who had seen each clip several times. It measures a *perceived*
or *stated* boundary. Whether that coincides with the boundary a driver's own behavior
reveals is exactly the question the project ultimately wants answered, and this dataset
cannot settle it — it can only show that the method's structure holds up where the
construct is measured directly. My reading is that this is still a substantial step,
because the transfer test is a test of the method rather than of the population, and a
method that fails to transfer across four scenarios in *judgment* data would be unlikely to
transfer in behavioral data either.

### (c) "Validation against the original data, or a leave-X-out setup"

Agreed, and I think this is stronger than the sketch suggests, because the dataset supports
the *cross-scenario transfer test* that `docs/data_requirements.pdf` was written to request
— with the same participants on both sides, which the original plan could not assume.

The decisive design, as I see it:

1. **Fit *c* on one scenario** (cut-in, which has the most levels and the cleanest timing).
2. **Apply that same *c*, unchanged, to the other three** (LTAP, cyclist overtake, truck
   overtake) and predict their press times and censoring rates.
3. **Report the transfer error**, not the fit error.

That is exactly the experiment §7 of `notes/04_comfort_zone_method.md` specifies, and it
is the step that would turn the method from a construction into a finding. Three points
about it:

- The four scenarios are *behaviorally* very different — a longitudinal conflict, an
  intersection gap acceptance, and two lateral-clearance overtakes — so transfer across them
  is a strong test, not a weak one.
- Leave-one-participant-out is worth running as well, but it answers a different and easier
  question (individual differences), so I would report it as a secondary result.
- LTAP is also the authors' own **held-out generalization scenario**, and its scenario code
  already exists in `external/aica/src/intersection/`. Transfer to LTAP therefore doubles as
  a partial replication of the paper's held-out test, on human data rather than model output.

## 3 What I would add that is not in the sketch

**Use the perceived-safety ratings as a graded target.** The Random design gives a 0–10
perceived-safety rating on the same clips, from the same 47 people. Our comfort-zone field
is a continuous scalar, and the boundary is a level set of it. Testing whether the field is
monotone in perceived safety — across scenarios, at matched criticality — is a considerably
richer validation than predicting a binary or a single onset, and it uses data that the
timing analysis discards. If the field orders perceived safety correctly across four
scenarios with one parameter set, that is a strong result; if it does not, it localizes the
failure to specific preference terms.

**Exploit the fixed-clip versus button contrast.** The same participants judged the same
clips retrospectively at frozen timepoints and prospectively in continuous time. The
fixed-clip design cannot identify a continuous boundary because instantaneous TTC and
manoeuvre progress are perfectly collinear within it (the documentation makes this point
well); the button design breaks that collinearity. Fitting the same boundary to both and
comparing is a way to separate *where the boundary is* from *how the response is elicited*.

**Treat the press semantics as a modeling constraint, not a nuisance.** The instruction
differs by scenario: intervene/brake for cut-in, abort the overtake for cyclist and truck,
yield rather than turn for LTAP. These are different actions, so the preference terms that
should drive the crossing differ per scenario — longitudinal safety for cut-in, lateral
clearance for the overtakes, a gap-acceptance term for LTAP. Pooling them under one scalar
without accounting for this would, I think, be the most likely way to get a misleading
negative result.

## 4 A proposed order of work

| phase | what | why first |
|---|---|---|
| 0 | Data conditioning: trace cleaning per §1.2, press-time to trace-time mapping, reproduce the documented descriptives (the 3 × 6 cut-in table, the truck monotonicity) | derisks everything; confirms our reading of the files matches the authors' |
| 1 | (a1) cut-in preference function and its property tests | the minimal object that unlocks fitting |
| 2 | (b) boundary fitting on censored cut-in press times; per-participant *c*; comfort and dread levels from the follow-up | the core estimate |
| 3 | (c) cross-scenario transfer, fit on cut-in and predict the other three | the decisive test |
| 4 | graded validation against perceived safety; ADAS/manual as a preference-parameter contrast | uses the discarded data; tests the parameter story |
| 5 | (a2) closed-loop cut-in agent, only if a predictive claim needs it | expensive; not required by 1–4 |

## 5 Limitations I would state up front

- **This is judgment about video, not driving.** It measures a perceived or stated boundary
  under an imagined control authority. Whether that coincides with the behavioral boundary
  is exactly what the project ultimately wants to know, and this data cannot settle it. It
  should be described as a comfort-zone boundary *as judged by an observer*, and the
  transfer test is a test of the method's structure rather than of drivers' behavior.
- **Design order is perfectly confounded** with response modality in Study 2: Random always
  preceded Button, never counterbalanced. Any Random-versus-Button difference could be
  practice or fatigue. Rank and agreement statistics are less vulnerable than mean shifts.
- **Anticipation.** Four prior viewings per clip; the fastest presses precede any plausible
  reaction time.
- **A keypress carries motor and decision latency** of roughly 0.2–0.3 s that the model does
  not represent. It is a constant offset, absorbed into *c* if not modeled explicitly, which
  is acceptable for transfer but not for absolute onset claims.
- **The cut-in becomes car-following** partway through each clip, so late presses answer a
  different question. Window-based censoring is required, as the documentation says.
- **Crowdsourced online sample**, EU/EEA, recruited through Prolific, with attention checks
  in the Random design only — there are none in the Button design.

## 6 What I would want from Jonas before starting

1. Confirmation that the file-naming discrepancies in §1.1 are benign, and whether
   `Button_Study_Design_with_Kinematics.csv` can be obtained.
2. A decision on scope: is the goal the transfer test (phases 0–3), or the fuller programme
   including the perceived-safety and framing analyses (phases 4)?
3. Whether the cut-in closed-loop implementation (a2) is wanted for its own sake — for the
   handbook's scenario-switching argument, say — independently of the CZB work, since that
   changes its priority substantially.
