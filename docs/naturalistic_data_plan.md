# Using highD and inD: a plan for the comfort-zone work and for assessing the published model

*2026-09-17. Written after Jonas requested access to both datasets. A plan, not a result: nothing
here has touched the data, and every count, rate and feasibility statement below is to be verified
on download. Cards are numbered NC (comfort-zone boundaries) and NM (the published model); none is
authorized until Jonas says so.*

## 0 The short version

The two datasets can do more than `docs/data_requirements.md` §9 allowed them in August ("good for
distributional calibration only; no driver state and no onsets"). That verdict was right for the
question then asked, a per-driver onset label. Since then the model became gate × axis × level with a
population percentile as the deliverable, and three things changed what drone data can offer:

1. **The left turn needs no onset.** A turning driver's decision is binary and observable: the gap was
   accepted or rejected. inD gives that directly, and it is the same kind of response as the video
   study's "intervene or not" and the test track's Go/No-Go.
2. **The deliverable is a population percentile, not a per-driver level.** Neither dataset identifies
   drivers across recordings, so per-driver levels and the trait (TR.1) are out of reach; the
   population level is not.
3. **Two of the project's open questions are naturalistic by nature.** Card EX.2 made first exposure
   the primary setting, which predicts which fitted level should match unrehearsed drivers. And the
   method review's finding that the released model is unstable in plain car following (§4.2, cards
   GZ.1 and GZ.2) can only be judged against how real drivers follow.

So the plan has two programs sharing one ingest step. The comfort-zone program's strongest card is the
inD left turn; the paper-assessment program's strongest card is sustained following on highD.

## 1 What each dataset gives, and what it does not

| | highD | inD |
|---|---|---|
| Setting | German highways, drone, same-direction traffic only | four German urban intersections, drone |
| Road users (website) | about 110 500 vehicles, cars and trucks | about 8 200 vehicles and 5 300 pedestrians and cyclists |
| Per track | position, velocity, acceleration, size, lane, preceding and following ids, THW, TTC, lane-change annotation | position, heading, velocity, acceleration, bounding box, class |
| Maps | lane markings | OpenDRIVE and Lanelet2 maps of each intersection |
| Driver identity across recordings | none | none |
| Brake lights, pedal, gaze | none | none |
| To verify on download | the position reference point (box corner or centre), driving direction per lane, frame rate, the observation window per vehicle | frame rate, whether each intersection is signalized, which turning relations have oncoming or priority traffic, how many decisions each turning relation yields |

Consequences that shape every card:

- **Responses are revealed behavior, not judgments.** A video participant says "I would intervene"; a
  highD follower either decelerates or not. Mapping one onto the other is an assumption to state, as
  card TT.1 stated "Go on the track = not intervening on video".
- **An onset has to be derived from kinematics.** Deceleration onset from 25 Hz tracks is feasible but
  has a detection latency and a false-positive rate that must be measured before any timing claim.
- **The observation window is short.** A highD vehicle is in view for the length of the recorded road
  segment only, so events whose run-up or response falls outside it are censored.
- **The license:** non-commercial research, no redistribution, citation required. Raw data stays in
  `external/` (untracked); only aggregate results enter the repository. No data or per-track derived
  data goes to anyone else, the authors of the published model included.

## 2 Step zero, shared by both programs

**NC.0 — ingest, conventions and the jitter floor** (a few days; gate for everything else).
Loaders `src/comfortzone/highd.py` and `ind.py` with property tests that check the claims (a track's
integrated velocity reproduces its positions; THW recomputed from positions matches the provided THW;
lane changes counted from lane ids match the annotation). Establish the conventions from the data, not
from documentation, as the overtake and left-turn loaders did: the reference point, the driving
direction, heading. Measure the position and velocity jitter floor on steady driving, per dataset,
before any spread or window is chosen (the trap card HS.1 fell into). Decide the route of the adapter
(query NAT.Q2).

**NC.0b — a validated deceleration-onset detector.** Onset as the start of a sustained deceleration
beyond the vehicle's own baseline, by the piecewise-linear fit to the speed trace that
`docs/data_requirements.md` §7.4 specifies (its attribution to Markkula et al. is marked unverified
there and stays so here). Validated on synthetic traces with known onsets plus the measured jitter:
report latency and false-positive rate. Stop rule: if the median latency exceeds 0.3 s or the
false-positive rate on steady following exceeds 5%, no timing claim is made from highD and the cards
below fall back to "responded within the window, yes or no".

**NC.0c — the census.** Counts, before any hypothesis is tested: highD cut-ins by gap and relative
speed, steady-following episodes by speed and THW, lead-deceleration events by magnitude; inD turning
decisions by relation and conflicting road-user class. Each card below has a minimum count, stated in
its pre-registration; a card whose count is not met is not run.

## 3 The comfort-zone program

| card | question | data | response | why it matters | cost |
|---|---|---|---|---|---|
| **NC.1** | Do real drivers accepting a left turn across oncoming traffic show the boundary the video and the track found? | inD | gap accepted or rejected | a third anchor after video (2.42 s at first exposure, 2.18 pooled) and track (2.45 s), with no onset needed | days |
| NC.2 | Is distance, not time, the left-turn axis when speed varies naturally? | inD | same | card B.3.v2 chose distance on a design with one speed per cell; naturalistic speeds break that confound | hours, after NC.1 |
| **NC.3** | Does the video-fitted cut-in level predict when real followers respond? | highD | deceleration onset or response yes/no | the out-of-sample test of gate × looming × level on real traffic; and a direct test of EX.2's choice | days |
| NC.4 | How far ahead do real drivers anticipate, per scenario? | both | onset relative to the lane change's lateral onset; the turning driver's slowing relative to the oncoming arrival | answers PC1.Q4 empirically: the scenario-specific anticipation horizon | days |
| NC.5 | Where does free car following sit relative to the comfort-zone field's boundary? | highD | chosen THW by speed | the static field's closed-form boundary (README table) against revealed behavior; shares its computation with NM.2 | hours |
| NC.6 | Do real cut-ins fall inside the video study's design space? | highD | none, descriptive | tells whether study 2's stimuli are representative, and what share of real cut-ins cross each percentile | hours, part of NC.0c |

**NC.1 in more detail**, since it is the recommended first test. For each left turn with an oncoming or
priority road user, the decision moment is when the turning vehicle commits or stops. At that moment
read the conflicting road user's distance to the conflict point and its time to arrival, and whether
the gap was accepted. Rejected gaps before an accepted one belong to the same driver, so the unit of
resampling is the turning track. Fit the population psychometric on the distance axis (no per-driver
term; there is one decision-maker per track). Pre-stated comparisons: the naturalistic median against
the video's first-exposure and pooled medians and the track's, as differences with intervals; and
which of the two video settings the naturalistic median is closer to, which is EX.2's prediction put to
data. Two known gaps must be addressed in the pre-registration: the video and track boundaries are in
post-encroachment time, which a gap-acceptance decision does not produce directly, so the comparison is
made on distance at the decision moment (B.3.v2's axis); and inD's speeds are urban and may not cover
the video's 50 km/h.

**NC.3 in more detail.** For each cut-in, compute the G.1 gate and the looming rate along the
follower's view, exactly as the video pipeline does (`src/comfortzone/interface.py` already does this
for the Volvo Cars interface). Predict, with the video-fitted population and nothing refitted, the
probability that the follower responds within the window, and its timing. Score against chance and
against a refit on highD, as TT.1 scored the video population on the track. Report the prediction at
both EX.2 settings and pre-state that the first-exposure setting is expected to score better.
Confounds to state in advance: the follower may already be decelerating, may change lane instead, and
trucks follow at other gaps.

**Deferred:** the cross-scenario generalization test (fit on one scenario, predict another) needs the
common scale of EL.2 and query EL.Q4; the per-driver trait is out of reach in both datasets.

## 4 The paper-assessment program

The published model was compared against a meta-analysis of SHRP2 and ANNEXT response times (rear-end),
a UK simulator study (opposite-direction lateral incursion) and a Canadian simulator study (the held-out
intersection). None of those is free naturalistic driving. The method review
(`docs/method_review.md`) found two things that only naturalistic data can settle: the accumulator is
far from zero in ordinary following (§4.2), and, since cards GZ.1 and GZ.2, the released configuration
brakes by itself after about 2.6 s of steady following.

| card | question | data | method | cost |
|---|---|---|---|---|
| **NM.1** | Does the released model hold real car following that real drivers hold? | highD steady-following episodes | the authors' model, unmodified, on replayed lead trajectories (the tier-2 adapter already used by GZ.1 and GZ.2), a stratified sample by speed and THW; rate of spontaneous re-plans and braking against the human follower in the same episode | overnight runs: 5 to 100 s of CPU per simulated step |
| **NM.2** | Is the model's calibrated following preference where real drivers follow? | highD following distributions | the preference function (`src/aidriver/preferences.py`, verified against the code) evaluated on real following states: the share of real following that the collision-and-safety term scores as a shortfall, which is what feeds the accumulator in NM.1 | hours; same computation as NC.5 |
| NM.3 | Does the response-time-to-urgency relation hold in naturalistic lead decelerations? | highD lead-deceleration events | onset from NC.0b, urgency as inverse tau at the lead's deceleration onset; the relation compared with the deposit's and with the paper's regression | days; stop rule if hard decelerations are too few |
| NM.4 | Before the conflict, do priority-road drivers behave as the model's intersection scenario assumes? | inD straight-through drivers meeting vehicles entering from a minor road | approach speed and slowing when a vehicle waits or creeps, against the deposit's pre-event behavior in the intersection scenario | days; a feasibility check first, since failures to yield will be rare and the deposit's scenario geometry may not match any inD relation |
| — | the opposite-direction lateral incursion | not testable | highD has no opposing traffic; inD speeds are too low | — |

What these cards can and cannot claim. They test the model on behavior it was not built to reproduce
(sustained naturalistic following, free gap choice), which is a fair test of a model presented as a
general account of driving but not a test of the paper's own comparisons. The write-up should say so
in those words. The paper's own fit metrics (Jensen–Shannon for outcomes, Wasserstein for response-time
distributions) can be applied where the naturalistic reference is a distribution of the same quantity,
which is NM.3 and, for braking onsets, NM.1.

## 5 Order

1. **On access:** NC.0, NC.0b, NC.0c. The census decides which of the cards below have the events they
   need.
2. **Cheap and decisive:** NC.5 with NM.2 (one computation, two readings), NC.6, then **NC.1** (the
   strongest comfort-zone test, no onset) and NC.2.
3. **The onset-dependent cards:** NC.3, NC.4, NM.3.
4. **The expensive one:** NM.1, pre-registered and run overnight, possibly over several nights.
5. **Feasibility-gated:** NM.4.

Each card follows the standing rules: a pre-registered script, a generated report, a worklog entry,
queries, the suite green, one commit.

## 6 Decisions for Jonas

- **NAT.Q1** (judgment): the mapping from video to naturalistic responses. Proposed: "would intervene"
  on video corresponds to a deceleration onset beyond baseline for highD, and to rejecting the gap for
  inD. Both are assumptions the reports will state.
- **NAT.Q2** (judgment): route highD cut-ins through the split-site interface schema
  (`transfer/interface_schema.yaml`, card NDS.1) as a dry run of the Volvo Cars pipeline on real data?
  It would exercise the five schema gaps found by NDS.1 without sending anything to Volvo Cars. The VCC
  track is paused, so this needs your word.
- **NAT.Q3** (judgment): results about the published model (NM cards) are outward-sensitive, given the
  authors' reply of 2026-09-11 and the meeting with Julian Schumann. Who sees them, and when, is yours
  to decide; nothing is shared by a session.
- **NAT.Q4** (judgment): priority if time is short. My recommendation is NC.1 first for the comfort-zone
  work and NM.1 first for the paper; NM.1 costs the most machine time and the least of yours.

## 7 Where I may be wrong

- The dataset facts in §1 come from the dataset pages, not from the data. inD in particular may have
  few left turns with oncoming traffic, in which case NC.1 moves to turns yielding to priority traffic
  from the side, a different geometry from the video study.
- A deceleration onset may be a poor proxy for "uncomfortable": followers can release the throttle and
  coast, which drone kinematics show only as a small deceleration. NC.0b's stop rule protects the
  timing claims, not the mapping.
- NM.1 replays a recorded lead into a closed-loop model whose own speed diverges from the human
  follower's; comparing the two after divergence compares different situations. The report must compare
  the first spontaneous re-plan and braking onset, before divergence, not whole trajectories.
- The first-exposure prediction for NC.1 and NC.3 assumes naturalistic drivers correspond to the
  first-session state of a video participant. EX1.Q3 applies: session and exposure are confounded in
  study 1, so a better match to first exposure could also reflect session-day effects.
