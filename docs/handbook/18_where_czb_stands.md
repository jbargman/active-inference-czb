# Chapter 18 (status): where the comfort-zone work stands, September 2026

*Part of the WaymoActiveInference handbook. Added 2026-09-28 (round 8). Chapters 00–17 describe
the model and the program as of 2026-09-03. This chapter reports what happened after that, in the
order a reader needs it. It is the chapter to read before quoting anything from chapter 11 or
appendix 17. Every number comes from a committed script with a tracked output under
`replication/czb/out/`; the cards are named so each result can be traced (the worklog,
`replication/czb/out/worklog.md`, has the full record, and `handover.md` §1 the running summary).
Readings, as opposed to results, are marked [Speculation] as elsewhere in the handbook.*

## 18.1 The short version

{{R8}}Six things changed between 3 and 28 September.

{{R8}}1. **The comfort-zone boundary has a working measurement model**: a threshold on the looming
(optical expansion rate) of the other vehicle, opened by a gate that says whether the vehicle is
about to be in the driver's path. It fits the second cut-in study far better than the gap or TTC,
and each driver's level is the same person's across scenarios.

{{R8}}2. **Each part of that model has an active-inference reading, and each reading was tested
rather than assumed.** The boundary is a prior over the looming of a lead vehicle. The gate is the
generative model's uncertainty about whether the other vehicle will become one. What the released
model computes, an expected free energy summed over a planning horizon, is a collision-avoidance
quantity, not a comfort-zone one.

{{R8}}3. **A review on 22 September withdrew several claims** made in the preceding days. Since then
every analysis is pre-stated in its own commit before it runs.

{{R8}}4. **The first study's Sequence and Button designs are not primary sources** (strong
dependence between successive answers). The second study is the trusted one.

{{R8}}5. **Naturalistic data arrived** (highD, inD, 24 September). The gate's key parameter was
measured on real traffic and predicts the video data. The video's intervention curve transfers to
real cut-ins in level. But real braking follows inverse TTC slightly better than looming, and the
released model does not hold real steady following.

{{R8}}6. **The participants watched on desktop monitors that shrank the picture.** Taken literally,
this lowers every looming level by 0.42 and reverses three comparisons with real data. The left
turn, checked against the 2013 test track, suggests the participants were not affected: they
judged as if the scene had not been shrunk. This is unsettled and has a clear test.

## 18.2 The measurement model

{{R8}}On the second cut-in study (378 clips, 288 after the lane change has begun, rated by 10–26
people each), the share who say they would intervene is described by

> share = lapse + (1 − lapse) × GATE × Φ((log θ̇ − log θ̇₀) / σ)

{{R8}}with θ̇ the cut-in vehicle's looming at the driver's eye (card EL.1b), θ̇₀ a level, σ a spread,
and the GATE the probability that the vehicle's sideways clearance, projected 3 s ahead, falls below
a minimum (card G.1). Scored out of sample (each starting-TTC level held out in turn), the gated
looming rule scores 0.103, looming without the gate 0.113, the gap 0.152, TTC 0.168, chance 0.320;
the sampling-noise floor is 0.118. Before the lane change begins, where only the gate can say "not
yet", it scores 0.032. The fitted intervention curve (card JJ.10): lapse 0.037, level 0.0320 rad/s,
spread 1.29 log units.

{{R8}}**The per-driver level is a trait.** A driver's level on the cut-in ranks drivers the same way
as their level on another scenario (Spearman +0.65, card TR.1; +0.64 [+0.40, +0.80] as a prior
carried from one scenario to the other, card JJ.7). The population median prior on the cut-in is
0.031 rad/s.

## 18.3 The free-energy reading, and what the released model's machinery does not do

{{R8}}The aim, in Jonas's words, was not to assume the framework fits but to probe whether a looming
threshold can be *explained* in free-energy terms. Where it stands (cards JJ.6 to JJ.12,
`docs/looming_as_free_energy.md`):

{{R8}}- **The boundary is a prior over the looming of a lead:** a one-sided penalty on log looming
above the driver's level. Additive sensory noise (a spread in looming rather than in log looming) is
rejected (+0.023 held out, card JJ.8), so the spread is a spread of *levels* across moments and
people, not of perception.
{{R8}}- **The gate is the generative model's predictive uncertainty about the other's sideways
motion.** Card G.1's fitted gate is, to machine precision, a Gaussian-rate predictor's probability
that the other's body reaches the driver's lane within 3 s, with the sideways-speed uncertainty σ as
its one parameter (card JJ.6e). A latent lane-change *intention* is not needed; the human gate grades
on how soon the body arrives, not on whether it intends to (JJ.6 to JJ.6d).
{{R8}}- **The two combine as the free energy of the present observation:** F = P(lead) × excess. Whether
the gate multiplies the probability of responding or the looming judged cannot be told on this
design (difference +0.003, card JJ.10). Nor can a reflex and a one-step decision reading (−0.0002,
JJ.8); only the reflex reading gives the level a meaning.
{{R8}}- **The one circularity is gone.** σ was first set from the fitted gate. Measured on real
lane-keeping in highD it is 0.125 m/s. With that value and nothing fitted from the video, the gate
still predicts the second study (0.112 held out, 0.034 before the lane change; card JJ.9). The lab
participants' σ is 0.33, so they anticipate cut-ins far more than real motorway traffic warrants.
{{R8}}- **What the released machinery does not do.** Any quantity that sums a one-sided preference
over the planning horizon of a policy that drives on through the lead is ordered *against* the
participants. A sum to contact of a cost that grows near contact is dominated by its value at
contact, which scales with the closing speed; at equal TTC the nearer car closes more slowly, so the
sum rates the farther, faster car as worse, where participants rate the nearer one as worse (cards
JJ.2 to JJ.5b; JJ.12: the sum of inverse tau to contact correlates −0.86 with the share and +0.999
with the gap). Removing
the sum removes the inversion but leaves the released terms, which are braking and TTC quantities,
not looming. A Farewell-style accumulator over the *past* goes the human way but scores worse than
the instantaneous rule (0.128–0.133 against 0.113); its graded form is open (JJ12.Q1). The corrected
released planner, rerun on the video cells, brakes and steers from the first step almost everywhere
(card P.1, DROP). The "lateral factor" was retired: with a cyclist-sized collision box it scores 0.29
against the clearance rule's 0.15 (card JJ.3b).

{{R8}}**In one sentence** [Speculation]: the comfort-zone boundary is a prior over the looming of a
lead, gated by the generative model's uncertainty about whether the object is one. The
active-inference machinery supplies the gate and the words; the looming threshold supplies the fit.

## 18.4 The review of 22 September, and the rule it left

{{R8}}A review of the 18–22 September work (`docs/review_2026-09-22.md`) found that its central
diagnosis, that the released model's safety probability is "inverted", did not follow from the
evidence. Three cards (RE.4, JJ.2b, RE.1) were invalid as run. What stood is listed in that document.
The standing rule since: **every analysis is pre-stated (models, folds, decision rule, predictions)
in its own commit before it runs**, and anything changed afterwards is dated in the script. The note
to JJ (`docs/note_for_jj_horizon_sum.md`, one page) is written but not sent, and carries a banner
saying it should not be sent as it stands.

## 18.5 Which video data to trust

{{R8}}Serial dependence, measured as the lag-1 correlation of residuals within a participant (card
AC.1), is +0.40 in the first study's Sequence design (excluded since August), +0.32 in its Button
design within a scenario, +0.12 in its Random design within a scenario (+0.03 overall), and +0.05 in
the second study. **The Button design is not a primary source**; results that rested on it (the hard
boundary per clip, card NC.3j; part of NC.3m and NC.3n) are downgraded. How far to trust the Random
design is Jonas's query AC1.Q1. The second study is the reference.

## 18.6 Naturalistic data: highD and inD

{{R8}}The two datasets (levelXdata; highD v1.0, 60 motorway recordings; inD v1.1, 33 intersection
recordings) are at `C:\JonasLocal\D_Data`, outside the repository. Per-sample caches are in
`C:\JonasLocal\D_Data_derived`; under the licence only aggregates are committed. Appendix 15 lists
them.

{{R8}}**The braking detector.** A response is a qualifying deceleration episode. At 0.5 m/s² for
0.3 s the false-positive rate on steady following is 2.6% (card NC.0b). Timing claims are valid only
at thresholds of 1.0 m/s² or more (latency 0.24 s, false positives 1.1%; card NC.0b-lat).

{{R8}}**Cut-ins at the lane switch** (card NC.3; 2,208 closing cut-ins, 11.6% respond within 3 s).
The video's intervention curve, with nothing refitted, predicts better than chance (binned error 0.065
against 0.083). A refit on highD puts the level at 0.039 rad/s, 1.21 times the video's. But the
*axis* does not carry over: whether a real follower brakes is predicted slightly better by inverse
TTC than by looming (area under the curve 0.739 against 0.713; difference −0.026 [−0.043, −0.006]),
at every detector setting and at short and long gaps alike (NC.3c). Query **NC3C.Q1** is the question
this raises: is the video's button press or real braking the operationalisation of the comfort-zone
boundary?

{{R8}}**Hard braking is rare on the motorway.** Of 2,771 real closing cut-ins, 4 drew braking of
2.5 m/s² or more. highD's own 99th percentile of deceleration is 1.07 m/s² (0.87 at 110–130 km/h).
The released model's inverse-tau preference costs nothing at a TTC of 5 s or more, where 99.5% of
real closing cut-ins sit (card NC.5-tau). Jonas's question for Malin Svärd (query NC3H.Q1): the 99th
percentile of deceleration at 110–130 km/h, over all driving samples, with sampling rate and filter.

{{R8}}**Two boundaries on one axis.** The second study also asked what participants expect *the car*
to do (nothing, brake gently, brake hard). Gently and hard are two levels on the same looming axis
with one spread (card NC.3o, supported: 0.113 against two free boundaries' 0.115; on TTC 0.162): expect
gentle braking from about 0.012 rad/s, hard from 0.124, with the intervention level (0.032) between
them. Half expect hard braking at a TTC of 1.64 s (card NC.3l). Real followers match the gentle
(intervention) curve at braking of 1.08 m/s² [0.97, 1.22], about highD's own 99th percentile (card
NC.3h). The kept sentence, Jonas's: *the hard-braking judgment does not depend on whether participants
judge their own action or the vehicle's; the gentle (intervention) boundary replicates across
studies, the hard boundary does not* (the first half rests on the Button design, NC.3m).

{{R8}}**Before the lane switch** (cards NC.4 to NC.4c). Real followers sometimes start braking 2–3 s
before the cutter reaches their lane. Looming to the cutter predicts which ones (0.856, with the
follower's own leader ruled out), and the lateral gate of card JJ.9 does not help; it makes
prediction worse (−0.093 [−0.146, −0.046]). Real drivers anticipate from something other than the
cutter's sideways motion. The cutter closing on a slower car in its own lane is the cheap candidate
(query NC4C.Q1).

{{R8}}**Left turns in inD** (card NC.1): 93 gap decisions, 7 accepted; descriptive only. The
extraction lost most accepted gaps, because the oncoming car was often not yet in view at the
decision moment. A redesign timing gaps at the conflict point is query NC1.Q1.

## 18.7 The released model on real traffic

{{R8}}Three checks of the authors' model, unmodified, against highD (these also belong in chapters 05
and 10, which carry short notes):

{{R8}}- **Sustained following** (cards GZ.1, GZ.2, NM.1). Behind a lead at constant speed the released
configuration starts braking after 3.2 s at a 1.5 s headway (4.6 s at 2.0 s), sometimes to a
standstill; with perception noise × 100 it follows steadily. Behind real highD leads in 18
five-second episodes where nothing happens, it brakes by at least 1 m/s² in 56% of runs, often at −6
to −7 m/s², while the human followers in the same episodes never brake. The authors' calibration
returns the same values for every episode, so it does not explain why braking is more frequent at
low speed (NM.1b; figure `figures/nm1b_released_model_following.png`).
{{R8}}- **The calibrated following preference** (card NM.2). The braking-margin term fires in 1.7% of
steady real following. Its boundary headway lies at or below the real fifth percentile in four of
five speed bands. It is silent over about 98% of real following and does not say where people choose
to follow.
{{R8}}- **The response-time relation** (card NM.3; descriptive only for want of hard events). On 1,033
real lead-braking events the log response time rises with log headway, more steeply for harder lead
braking (+0.23, +0.40, +0.45 against the model's +0.59). Real responses are about three times slower
(2.2–3.1 s against 0.8 s), mostly because the data hold few emergencies.

{{R8}}A draft email to Julian Schumann with these results is in
`correspondence/2026-09-25_draft_email_julian.md`, **not sent**. Suggested changes to the authors'
edition of this handbook are in `docs/handbook_authors/review_2026-09-28.md`.

## 18.8 The monitor, and the left turn against the test track

{{R8}}The crowd-sourced participants watched the clips on their own monitors: typically a 23-inch
screen at about 60 cm, showing a rendering with a 90° field of view. The monitor fills only 46° of
the viewer's field, so the picture is shrunk by k = 0.42. What reached the eye is exactly what a
driver would see with every distance along the line of sight 2.36 times longer. **TTC is unchanged;
looming shrinks by 0.42.** The transform is specified in `docs/display_transform.md` (parameters in a
machine-readable block, code `src/comfortzone/display.py`, switch `CZB_DISPLAY_TRANSFORM=on`) and
explained with figures and a video in `docs/display_transform_explained.md`.

{{R8}}**If the participants judged the looming at their eye** (card DT.1), nothing within the video
studies changes except the looming levels (the intervention level 0.032 → 0.0136 rad/s). Three
comparisons with real data reverse: the boundary falls below Farewell's emergency-braking level (0.64
times it, not 1.5); highD's level is 2.9 times the video's (not 1.21); and real followers match the
gentle curve at 0.66 m/s², not 1.08. Over plausible displays (50–70 cm, the video filling 60–100% of
the screen) the gain runs 0.22–0.51 and the reversals hold throughout (DT.1b).

{{R8}}**But the left turn says they probably did not** (card DT.2). On video the left-turn answers
follow the oncoming car's distance or looming, not its time. The 2013 test track, with real optics,
agrees with the video (PET 2.45 against 2.42 s). A shared perceived distance or looming criterion
would put the video boundary outside the design (−1.4 to 0.4 s). The display gain that reconciles
track and video is 0.99 [0.84, 1.05], not 0.42. And on the monitor the oncoming car's looming near the
boundary was at the edge of visibility, yet the answers kept varying. Reading [Speculation]: the
participants judged distance *relative to the scene* (the intersection, the road, familiar car
sizes), which a uniform shrinking leaves intact. If that holds for the cut-in too, DT.1
over-corrects and the uncorrected comparisons stand. **Until it is tested, cross-domain looming
numbers are reported both ways.**

{{R8}}**The test** (query DT2.Q1). For participants whose screen or window size is known, compute each
one's display gain and their own level. A slope of −1 of log level on log gain means the display
acted on them; a slope of 0 means it did not. Jonas has display data for a subset of participants.

## 18.9 What is open, and what the deliverable is waiting for

{{R8}}The comfort-zone deliverable (a population distribution of boundary levels, card EL.2) is
still blocked by query EL.Q4. The questions that decide the most, in the order I would take them:

| query | the question | what it decides |
|---|---|---|
| DT2.Q1 | the per-participant display data | whether video looming levels can be put next to real-world ones |
| NC3C.Q1 | the video button press or real braking as the operationalisation | whether the boundary is on looming or on TTC in real traffic |
| AC1.Q1 | how far to trust the first study's Random design | which first-study results stand beside the second study |
| NC3H.Q1 | Malin Svärd's 99th percentile of deceleration at 110–130 km/h | the anchor for "hard" braking |
| EL.Q4 | (blocks the deliverable since 2026-09-03) | card EL.2 |
| NC4C.Q1, NC1.Q1, NM1.Q1, JJ12.Q1 | the smaller follow-ups of 18.3, 18.6 and 18.7 | one card each |

{{R8}}The register of all open questions is `replication/czb/out/query_register.md`; the next
session's instructions are in `handover.md`.

## Notes for the mathematically curious

{{R8}}**The gate as a predictive probability.** With the other's edge-to-edge clearance l₀, its rate
l̇ and a Gaussian sideways-speed uncertainty σ over the anticipation horizon T, P(lead) =
Φ((−l₀ − l̇T)/(σT)); G.1's fitted gate is this with s_l = σT (JJ.6e). The free energy of the present
observation under a one-sided log-looming prior is F = P(lead) × ½((log θ̇ − log θ̇₀)/σ_c)²₊ (JJ.10,
`src/rollout/comfort_fe.py`).

{{R8}}**The display.** A pinhole rendering with horizontal field of view HFOV, shown W cm wide at
distance d, maps a direction α to a seen direction β with tan β = k tan α, k = (W/2)/(d tan(HFOV/2)).
That is the optics of the scene with depth divided by k: range and closing speed × 1/k, looming
k(r² + W²/4)/(r² + k²W²/4) ≈ k, TTC and inverse tau unchanged.

{{R8}}**The horizon sum.** For a policy that holds speed toward a lead at gap g and closing speed v,
the sum over steps of a one-sided cost c(τ⁻¹) up to contact is Σ_k c(v/(g − kvΔt)). Within a row
of equal TTC, inverse tau is one number, so it cannot order the row; the sum is dominated by its last
terms near contact, where the cost scales with the closing speed v, and at equal TTC the nearer car
has the smaller v. So the sum ranks cells by gap within a row, the opposite of the participants. The
closed forms are in card JJ.12 (`replication/czb/out/jj12_sums_future_past.md`).
