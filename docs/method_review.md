# Review of the active inference collision-avoidance model: method, claims, and released artifacts

Schumann, Engström, Johnson, O'Kelly, Messias, Kober & Zgonnikov, *Active inference as a model of collision avoidance behavior in human drivers*, Nature Communications 17:5009 (2026), with its Supplementary Information, the code release at github.com/tud-hri/Active-Inference-Collision-Avoidance, and the OSF data deposit (osf.io/gs4bu)

Prepared by Claude (Anthropic's AI assistant) at the request of Jonas Bärgman, Chalmers University of Technology, 2026-08-23. The review was carried out in a working repository in which the published model has been run, independently re-implemented, and compared against the deposited simulation output. Every statement below is tagged with its source: [Paper] the article, [SI] the Supplementary Information, [Code] the released code, [OSF] the data deposit, [Repo] our own replication work, [Opinion] a judgment rather than a verified fact.

---

## 1 Summary

The mechanism the paper describes — looming perception with a detection threshold, a norm-biased particle prediction, surprise-based evidence accumulation, and re-planning by expected free energy minimization — is implemented in the released code and does what the paper says it does. I was able to verify the looming-threshold mechanism to the timestep across all 896 deposited front-to-rear runs. The paper's central qualitative claims about response timing hold in the deposited data.

Three things did not hold up as well, in my reading:

1. **Road departures at 25 m/s.** In the deposited front-to-rear runs at 25 m/s, the model drives off the road in 44–72% of seeds at *every* initial time gap, including 3.5 s. The departures occur after the lead vehicle brakes, mostly to the left, beyond the adjacent lane. Neither the paper nor the SI mentions this, and the paper's description of the model "favoring swerving at higher velocities" reads differently once one knows that most of those swerves end off the road.
2. **The accumulator is far from zero in ordinary following.** The surprise signal in the deposited runs is 50 000–100 000 log units per step during steady-state following at the shorter initial gaps, entirely from the collision/safety term. Between 18% and 44% of the evidence that triggers the response at gaps of 1.5 s or less is accumulated before the lead vehicle brakes, and at gaps of 2.0 s or less the model would re-plan spontaneously within 2–7 s of nothing happening. The reported response-time/gap relation is therefore partly a product of the 0.8 s pre-roll before the lead brakes, which the SI gives as 5 s and the code as 0.6 s.
3. **The worked examples in Fig. 3 do not represent the deposit.** For the Fig. 3a condition, all 32 deposited seeds perceive the braking 0.2 s after onset (the paper says 0.6 s), re-plan 0.6 s after onset (the paper says 1.2 s), and 31 of 32 brake with a response time of 0.8 s (the paper says 1.4 s). Six percent of seeds brake only, which the paper calls the typical outcome. The explanation given for the shorter perception delay in Fig. 3b ("the smaller initial distance") is reversed: Fig. 3b starts farther from the lead than Fig. 3a.

In addition, the released code differs from the paper and SI in at least ten places (section 5), some of which act directly on the brake-versus-swerve trade-off the paper presents as a model prediction; and several methodological points (section 6) seem to me worth raising, chiefly the identifiability of the timing parameters and the number of parameters that were set but not listed.

For the replication question that prompted this review: the authors' code, run on our hardware, reproduces the authors' deposited results to the timestep. The earlier conclusion in our notes that a discrepancy at the Fig. 3a condition "traces to a calibration-table limitation" was wrong; the discrepancy is between the paper's worked example and the authors' own deposit, not between our run and theirs.

---

## 2 What was reviewed, and how

### 2.1 Materials

| item | version used | how obtained |
|---|---|---|
| Article | Nat. Commun. 17:5009, doi 10.1038/s41467-026-73345-0, received 2 June 2025, accepted 6 May 2026 | publisher PDF, text extracted to `notes/paper_text/` |
| Supplementary Information | MOESM1 (17 pages, 7 sections) and MOESM2 (movie descriptions) | publisher PDFs, text extracted |
| Code | `tud-hri/Active-Inference-Collision-Avoidance`, commit `5b47bf60a13310b41679ea0eae0de9378dc98505` (2026-07-27), Zenodo 10.5281/zenodo.20049511 | cloned to `external/aica/`; one local patch (CPU fallback for a hardcoded CUDA device in `src/common/bicycle.py`), documented in `replication/PATCHES.md` |
| Data deposit | osf.io/gs4bu, 3.1 GB, all three scenarios, 32 seeds per run | downloaded 2026-08-20 to `external/gs4bu-osfstorage-archive/` |

### 2.2 Procedure

1. I read the article and the SI in full, and listed every quantitative claim, every equation, and every parameter value in each.
2. I compared the equations and parameter values against the released code, reading `simulation_rear_end.py`, `simulation_oncoming.py`, `simulation_side.py`, `src/rear_end_test/reward.py`, `src/common/mpc_discrete.py`, `src/common/encoder.py`, `src/common/decoder.py`, `src/utils/simulation.py`, and `Analysis_rear_end.py`, and the calibration table `Results_following/Analysis_following.xlsx` that the code reads at run time. Line numbers cited below refer to the commit above.
3. I analyzed the 28 baseline front-to-rear runs in the deposit (896 trials) directly from the per-run pickles, using the true-state array `eta`, the belief particles `b`, and the per-step pragmatic-value components `v`. The script that produces every deposit-derived number in this document is `replication/review_osf.py`; its outputs are in `replication/osf/review/`. Outcome categories follow the authors' own definitions in `Analysis_rear_end.py`.
4. I used the results of the earlier replication work in this repository where relevant: the authors' code run on CPU at two conditions (`replication/run_rear_end_single.py`, "Track A"), an independent NumPy re-implementation built from the article and the SI (`src/aidriver/`, "Track B"), and a distribution-level comparison against the deposit (`replication/validate_osf.py`).

### 2.3 What was not done

- The oncoming and intersection folders of the deposit were not analyzed beyond the authors' outcome tables; all deposit-level findings below concern the front-to-rear scenario.
- No simulations were re-run for this review. The compute cost of the model on CPU (about 18 s per simulated step per parallel run) makes the full sweep impractical here.
- No human data were used. Nothing in this review bears on how well the model matches humans, only on whether the reported model results are supported by the released artifacts and whether the method is described accurately.
- The reading was done without contact with the authors. Where a difference between documents could be an intentional choice that was simply not written down, I have tried to say so.

---

## 3 Replication status

### 3.1 The authors' code reproduces the authors' deposit

Two conditions were run with the authors' code on CPU before this review (Track A, [Repo]). Comparing them with the deposited runs of the same conditions [OSF]:

| quantity | Fig. 3a condition, 15 m/s, 1.5 s gap (deposit `Exp_10`, 32 seeds) | Track A, 4 runs |
|---|---|---|
| perception delay (belief mean of lead acceleration below −0.5 m/s²) | 0.2 s in all 32 seeds | about 0.2 s |
| re-plan after lead onset | 0.6 s in all 32 seeds | 0.8–1.0 s |
| brake response time (first executed a ≤ −1 m/s²) | 0.8 s in 31 seeds, 1.0 s in 1 | 0.80, 0.80, 1.04, 1.04 s |
| maneuver | lane change 78%, brake and steer 16%, brake only 6% | lane change in 3 of 4 |

| quantity | Fig. 3b condition, 25 m/s, 1.0 s gap (deposit `Exp_4`, 32 seeds) | Track A, 2 runs |
|---|---|---|
| first observable response after lead onset | 0.6 s re-plan in all 32 seeds | 0.8 s |
| brake response time | median 1.4 s, IQR 1.0–2.0, minimum 0.8 | 0.80, 0.83 s |
| maneuver | leave road 69%, lane change 22%, brake and steer 9% | brake and steer (lane change completed) in both |

Track A sits inside the deposit on every row of the first table; for the second, two runs at the deposit's minimum are not informative either way. Within a condition, the deposit's re-plan timing is identical across all 32 seeds, and the brake response time is identical in 31 of 32 at 15 m/s. The stochasticity the paper cites as the reason for running 32 seeds [Paper, Results] affects the maneuver outcome, not the timing, at least at the lower speeds. A correct replication should therefore match to the timestep, and it does.

The earlier diagnosis in our notes — that Track A's 0.92 s at the Fig. 3a condition versus the paper's 1.4 s was caused by the shipped calibration table saturating at a_OV,min = −8 m/s² — is withdrawn. The table does saturate at that condition (section 6.2), but `simulation_rear_end.py` calls the same lookup on the same table, so the deposit carries the same value. Track A and the deposit agree; it is the paper's worked example that differs from both (section 4.3).

### 3.2 The independent re-implementation was built from a description that does not match the code

Track B [Repo] reproduces the preference function as written in the SI, and two of the six published relations in Fig. 3 (maneuver choice versus speed; braking magnitude versus urgency). Its closed-loop timing is not quantitative. Part of the reason is now clear: the SI and article differ from the code in the items listed in section 5, and Track B followed the documents. The most consequential for Track B are the symmetric τ⁻¹ preference (which in Track B pulls the agent toward the lead vehicle; the code's one-sided version does not), the off-road cost (−5000 in the SI, −15 000 in the code), and the speed grid (35 m/s in the SI, 20 m/s in the code, so Track B's sweep ran a condition the authors never ran).

A second part of the reason is worth stating because it bears on the paper: Track B's surprise signal in ordinary driving sits around 10⁵ per step, and our notes treated that as a defect. The authors' own signal in the same situation is 5–10 × 10⁴ per step (section 4.2). Track B's level is not the defect; the difference lies in which preference term produces it and in how the accumulator then behaves.

---

## 4 Findings on the reported results

### 4.1 Road departures at 25 m/s, undocumented

The deposit's outcome classification [OSF, `Analysis_rear_end.xlsx`; definitions in `Analysis_rear_end.py:843`] labels a run "leave road" when the vehicle body crosses either the right road edge (y < −(w − d)/2) or the far edge of the adjacent lane (y > w + (w − d)/2) at any time in the 12 s run, before any collision. For the 28 baseline conditions:

| initial time gap (s) | 0.5 | 1.0 | 1.5 | 2.0 | 2.5 | 3.0 | 3.5 |
|---|---|---|---|---|---|---|---|
| 25 m/s: fraction leaving the road | 0.72 | 0.69 | 0.69 | 0.56 | 0.47 | 0.44 | 0.53 |
| 20 m/s | 0.09 | 0 | 0.03 | 0 | 0 | 0.03 | 0 |
| 15 m/s and 10 m/s | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

From the per-run true states [OSF, `review_osf.py`]: in all 28 conditions the maximum lateral deviation before the lead brakes is 0.000 m and the maximum speed change is 0.0 m/s, so none of the departures is a pre-conflict event. The median departure time is 3.2–6.0 s into the run, after the lead's onset at 0.8 s. Counting every seed whose body crosses a road edge at any time (132 at 25 m/s; one more than the authors' classification, which gives precedence to a collision that happened first), 100 are to the left (through and beyond the adjacent lane) and 32 to the right shoulder.

The paper states that the model "favors combined swerving-and-braking or swerving only responses at higher velocities, regardless of the time gap" [Paper, Fig. 3 discussion] and that Fig. 3c gives the probability of a brake-only response. It does not mention that at 25 m/s the majority of runs end off the road, including at a 3.5 s gap where a lead braking at −6 m/s² leaves ample room to brake, and it does not say whether these runs are in the denominator of Fig. 3c or excluded from the response-time panels. At 20 m/s and below the behavior is unremarkable, so the issue is confined to the top speed, but that speed is a quarter of the reported grid. [Opinion] A reader would, I think, want to know this, and a human driver facing the 25 m/s, 3.5 s gap condition would not leave the road in half of the trials.

The mechanism is not something I can establish from the deposit alone. [Speculation] With σ_v = 0.5 m/s, losing 10 m/s of speed costs 200 log units per step against a lane-change cost of 1000 at the lane line and zero at the adjacent lane center, so at 25 m/s a lane change is the cheap option, and the lateral control the CEM finds at that speed overshoots. The lane-change bookkeeping terms in the code (section 5, items 6 and 7), which penalize lingering on the lane line and returning to the original lane, may push the overshoot through rather than back.

### 4.2 The accumulator is not near zero in ordinary following

The deposit stores, for every executed time step, the eight components of the pragmatic value summed over the 30-step horizon [OSF, array `v`; order from `reward.forward_sep`: velocity, acceleration, steering rate, lateral position, heading, gaze, collision/safety, epistemic]. Since each component is normalized so that its maximum is zero, the surprise ε_t of Eq. 13 is the negative sum of the first seven. Over the four steps before the lead vehicle brakes (steps 0–3; the lead's first nonzero deceleration is at step 4, t = 0.8 s):

| condition | ε per step before onset (median over seeds) | share from the collision/safety term | evidence E accumulated before onset (threshold = 1) | steps to spontaneous re-plan at that rate |
|---|---|---|---|---|
| 15 m/s, 0.5 s gap | 98 800 | 1.00 | 0.44 | 9 (1.8 s) |
| 20 m/s, 0.5 s gap | 94 400 | 1.00 | 0.43 | 9 |
| 15 m/s, 1.0 s gap | 88 700 | 1.00 | 0.40 | 10 |
| 15 m/s, 1.5 s gap (Fig. 3a condition) | 68 100 | 1.00 | 0.31 | 13 (2.6 s) |
| 25 m/s, 1.0 s gap (Fig. 3b condition) | 59 000 | 1.00 | 0.27 | 15 |
| 15 m/s, 2.5 s gap | 27 900 | 1.00 | 0.13 | 32 |
| 15 m/s, 3.5 s gap | 6 200 | 0.99 | 0.03 | 136 |

All 28 conditions are in `replication/osf/review/benign_eps.csv`. The collision/safety term accounts for essentially all of it; the velocity and control-effort terms contribute −0.003 and −2 to −6 per step.

Three consequences follow, as I read them:

- The paper's account of the accumulator — "if a policy would result in the most preferred observation, the agent would not accumulate any additional evidence" [Paper, Methods] — does not describe the model in its own baseline state. With predicted futures that collide or violate the safety margin in a fraction of particles (the same over-pessimism the paper discusses for the lateral non-conflict case in SI section 5), steady following at a 1.5 s gap accumulates a third of the re-plan threshold per 0.8 s. At gaps up to 2.0 s the model re-plans within 2–7 s (9–35 steps) of nothing happening. The main simulations do not show this only because they start 0.6 s before the lead brakes.
- The response-time/gap relation in Fig. 3d, which the paper describes as "remarkably consistent" with the meta-analysis, receives a head start of 30–44% of the threshold at the short gaps and 2–6% at the long gaps. Part of the slope is contributed by the pre-roll, not by the event. I cannot quantify the part without re-running, but the head start is of the same order as the evidence accumulated during the event itself at the short gaps.
- The time at which the lead vehicle begins to brake is therefore a consequential parameter. The code sets it to 0.6 s (`simulation_rear_end.py:209`, `t_brake`; with a −10 m/s³ jerk the first nonzero deceleration appears at 0.8 s, which is the value in the article's figures); the SI says the lead drives "for exactly 5 s" before braking [SI 3.1]. With 5 s (25 steps), every condition with a gap of 1.5 s or less, and most with a gap of 2.0 s, would have re-planned at least once before the event, resetting E to zero at a phase unrelated to the event.

[Opinion] This seems to me the most important methodological point in the review. It is also, from the perspective of comfort-zone modeling, an encouraging one: the reference model's residual surprise in steady following is large and grades smoothly with the gap (from 99 000 to 5 400 across the sweep), which is a comfort-zone field by another name.

### 4.3 The worked examples in Fig. 3 do not represent the deposit

**Fig. 3a** (15 m/s, 1.5 s gap). The paper describes a perception delay of 0.6 s, a further 0.6 s to reach the threshold, a re-plan at t = 2.0 s, first deceleration at 2.2 s, a brake response time of 1.4 s, and a brake-only maneuver, and calls this "a representative simulation" and the behavior "typical" for lower speeds and larger gaps [Paper, Results]. The deposited runs of this condition [OSF, `Exp_10`] give a perception delay of 0.2 s in all 32 seeds, a re-plan at t = 1.4 s in all 32 seeds, a brake response time of 0.8 s in 31 seeds and 1.0 s in one, and a lane change in 78% of seeds with brake-only in 6% (two seeds). The same is true of the authors' code run here (section 3.1). [Speculation] The figure may come from an earlier model version or parameter set; whatever the cause, the published figure and text do not describe the published data.

**Fig. 3b** (25 m/s, 1.0 s gap). The paper attributes the shorter perception delay (0.2 s) to "the smaller initial distance" [Paper, Results]. The bumper-to-bumper gap is 25 m/s × 1.0 s = 25 m in Fig. 3b and 15 m/s × 1.5 s = 22.5 m in Fig. 3a; Fig. 3b starts farther away. In the deposit both conditions have a 0.2 s delay.

**The looming-threshold mechanism itself is correct.** Across all 28 conditions, the step at which the belief mean of the lead's acceleration first drops below −0.5 m/s² is, in every seed, the first step at which the closing speed exceeds φ̇₀(Δx² + d²/4)/d evaluated at the initial distance [OSF, `review_osf.py`; table in `perception.csv`]. The delay rises from 0.0 s at 9–17 m to 1.0–1.2 s at 67–79 m, as the mechanism predicts. At the longest 25 m/s gap (92 m), where the threshold would predict a 1.6 s delay, most seeds instead show the belief drifting below −0.5 m/s² before the event: the sub-threshold observation is so uninformative at that range (an observation standard deviation of 2φ̇₀ in angular rate corresponds to about 21 m/s in closing speed) that the 3 m/s² process noise dominates the belief.

**Collisions.** "Collisions observed in the model (only at the shortest time gap of 0.5 s)" [Paper] is true, but at that gap the collision rate is 88% at 15 m/s and 100% at 10 m/s [OSF], which the text does not convey.

### 4.4 Response timing is nearly deterministic within a condition

In the deposit [OSF, `seeds.csv`], the re-plan time after lead onset is identical across all 32 seeds in both figure conditions, and the brake response time is identical in 31 of 32 seeds at the Fig. 3a condition. The 896-point scatter of Fig. 3d is, as far as timing goes, 28 tight clusters. The paper acknowledges that "the variances of the model's reaction times are smaller compared to the human data" for the other two scenarios [Paper, intersection results]; for the front-to-rear scenario the within-condition variance is close to zero, and the comparison with the meta-analysis is between a regression line and a regression line (section 6.6). [Opinion] This is not a fault of the model, but the "32 repetitions because of stochasticity" framing may give a reader the wrong impression of what the repetitions vary.

---

## 5 Where the released code differs from the paper and the SI

These are differences between what the documents say the full model is and what `simulation_rear_end.py` (and, where stated, the other two scenario scripts) configures at commit `5b47bf6`. Items 1–4 change which preference function the deposited results were generated with; items 5–7 are behaviors with no counterpart in the documents; the rest are documentation errors.

| # | item | article / SI | code | where |
|---|---|---|---|---|
| 1 | off-road cost g_LL | −5000 [SI 2.4]; −15 000 [Paper, Table 1] | −15 000 | `simulation_rear_end.py:335` |
| 2 | inverse-tau preference in p_coll | symmetric Gaussian N(τ⁻¹ \| 0.2, 0.125) [SI Eq. 48] | one-sided: τ⁻¹ is clamped to max(τ⁻¹, 0.2) before the Gaussian, so steady following and opening gaps cost nothing | `reward.py:272` |
| 3 | control-effort term | N(a_long \| 0, σ_a) [SI Eq. 44] | total acceleration √(a_lat² + a_long²), with positive longitudinal acceleration doubled first | `reward.py:166, 173` |
| 4 | lead steering-rate noise σ_ω,0 during belief update | 0.4575 (unit given as ms⁻²) [Paper, Table 1; SI Eq. 22], "same parameter values" across scenarios | 0.0045 in the front-to-rear scenario (an extra factor 0.01); 0.4575 in the oncoming and intersection scenarios | `simulation_rear_end.py:38` versus `simulation_oncoming.py:38`, `simulation_side.py:38` |
| 5 | heading preference | none | triangular penalty on heading beyond 45° up to g_LL at 90° (inert in practice) | `reward.py:108` |
| 6 | aborted lane change | none | additional 3·g_LC if the vehicle returns to its original lane after more than 1.5 steps straddling the line | `reward.py:221` |
| 7 | lingering on the lane line | none | additional 2·g_LC per step beyond 9 consecutive steps straddling the line | `reward.py:231` |
| 8 | CEM iterations K | 20 [SI 1.2]; 10 [Paper, Table 1; SI 4] | 10 when extending the policy, doubled to 20 on a full re-plan | `simulation_rear_end.py:172`; `mpc_discrete.py:374, 425` |
| 9 | speed grid | {10, 15, 25, 35} m/s [SI 3.1]; 10–25 m/s [Paper, Fig. 3c caption] | {10, 15, 20, 25} m/s | `simulation_rear_end.py:496` |
| 10 | lead braking onset | 5 s [SI 3.1]; 0.8 s [Paper, Fig. 3] | jerk starts at 0.6 s, first nonzero deceleration at 0.8 s | `simulation_rear_end.py:209` |
| 11 | looming applicability C_loom | longitudinal condition only [SI Eq. 31] | also requires lateral offset below 3d (perception) or 1.15d (preference) | `decoder.py:121–128` |
| 12 | oncoming initial distance | 300 m [SI 3.2] | 4.2 + (5.15 + 0.4) × 17.88 × 2 ≈ 203 m | `simulation_oncoming.py:439` |
| 13 | no-evidence-accumulation ablation | "fully re-plans its policy at every time step" [Paper] | re-plans every step only after a scenario-specific, hand-coded event detector fires; the scenario selector is hardcoded to `'intersection'` | `mpc_discrete.py:346–370` |

Items 6 and 7 deserve a comment beyond the table. They depend on the history of the ego vehicle's lateral position within the rollout, so the preference p(o) of Eq. 6 is not a function of the observation at a time step. [Opinion] That is a reasonable engineering device, but it sits uneasily with the paper's statement that the model "does not reduce to a combination of" engineering methods and with the formal definition of the pragmatic value, and the terms act directly on the brake-versus-swerve decision that Fig. 3c reports as a model prediction.

Item 13: for the front-to-rear and oncoming scenarios the intersection detector happens to be satisfied from the first step, so the ablation there is what the paper says. For the intersection scenario the ablated model extends its plan until the other vehicle is within a hand-coded stopping distance of the intersection, then re-plans every step. The ablation result for that scenario (Fig. 6b, bottom rows) is therefore not the "re-plan at every time step" variant the text describes.

---

## 6 Methodological points

### 6.1 Parameters: count, identifiability, and what the sensitivity analysis covered

The paper lists 26 parameters, of which 13 are described as free and hand-tuned [Paper, Table 1]. Parameters that were set by the authors but do not appear in Table 1 include: σ_τ⁻¹ = 0.125 and the τ⁻¹ mean of 0.2 [SI 2.4]; t_react = 1 s [SI 2.4]; a_OV,min, set per condition by lookup (section 6.2); M_n = 32 [SI 2.1]; the observation-noise vectors of Eqs. 36–39 (about 28 numbers); the three jerk limits [SI Eq. 42]; the norm-probability levels 1, 10⁻³, 10⁻⁵ [SI Fig. 1]; the 1.15 factor on the collision box; the pedal-neutral deceleration a₀; the lead onset time; and the factor 0.01 in item 4 above. Several of these (t_react, a_OV,min, the observation-noise vector, the onset time) act directly on response timing, and none were varied in the sensitivity analysis of Figs. 7–8.

Of the timing parameters that were varied, λ and g_C are not separately identified by response times: the accumulator reaches its threshold when λ·Σε exceeds 1, and ε is dominated by terms proportional to g_C, so only the product λ·g_C (together with H and the fixed threshold) sets the timing. The paper reports both λ and g_C as the most consequential parameters [Paper, Model parameters], which is consistent with this, but does not note that they are one degree of freedom for that metric. g_C is separately identified through the maneuver trade-offs, λ is not.

### 6.2 The a_OV,min calibration

The SI states that a_OV,min is chosen per simulation "so that the given initial distance and speed would result in stable car following" [SI 2.4], by interpolating in a table of steady-state following distances from a separate free-following study. The released table [Code, `Results_following/Analysis_following.xlsx`, 324 rows] has speeds {10, 20, 30} m/s, looming threshold {0.002}, prediction-noise factor {0.02, 0.05}, λ exponents {−6.0, −5.8, −5.6}, horizons {20, 30}, and a_OV,min {−4, −6, −8} m/s². The lookup [`simulation.py:263–392`] clips the main experiments' looming threshold (0.00215) and prediction-noise factor (0.2) to the table's range, subtracts 0.1 s from the desired headway, and applies a running maximum before interpolating.

At the most pessimistic value the table allows (−8 m/s²), the steady-state headway the model reaches is at most 2.12 s at 10 m/s, 1.25 s at 20 m/s, and 0.98 s at 30 m/s. For the larger gaps in the sweep (up to 3.7 s center-to-center) no value in the table produces stable following, and the lookup saturates at −8 m/s². So the calibration claim cannot be met for most of the 28 conditions. In practice this matters less than it sounds: with `EA_init = False` the agent follows a zero-control reference plan from the start, the first full re-plan is triggered by the event, and the pre-roll is 0.6 s, so steady-state following is never exercised in the main runs. [Opinion] The SI's description of the calibration and what it achieves would benefit from saying this.

[Speculation] The short steady-state headways in the calibration table may have a different cause than a_OV,min. With the one-sided τ⁻¹ preference there is no pull toward the lead from p_coll, but the epistemic term is not small (section 6.4) and rewards proximity, because observation precision in angular coordinates improves as distance shrinks. I have not tested this.

### 6.3 Looming: a detection threshold, not distance-dependent uncertainty

The article motivates looming-based perception with increasing uncertainty about the lead vehicle's state at increasing distance [Paper, Results; Methods]. In the released configuration the observation noise on φ̇ above threshold is 10⁻⁵ rad/s and on φ 10⁻⁵ rad [SI Eq. 37; `simulation_rear_end.py`, `perc_noise_factor = 0.01`], which makes perception effectively exact once the threshold is crossed. The deposit confirms it: the perception delay is identical in every seed of a condition, and in the short-range conditions the belief mean tracks the true lead acceleration to two decimals from the first above-threshold step. All of the perceptual work is done by the threshold, which acts as a deterministic detector on closing speed scaled by distance squared. The paper's own ablation shows this (Fig. 6e and 6f are described as very similar). [Opinion] I would describe the mechanism as a distance-dependent detection threshold rather than as distance-dependent uncertainty; the two give different predictions for, for instance, the variability of response times across drivers.

### 6.4 Epistemic value is not negligible in the baseline

The article expects behavior to be "driven mainly by pragmatic, rather than epistemic, value" in these scenarios [Paper, Results], and the ablation without epistemic value differs from the full model only in front-to-rear response times [Paper, ablations]. In the deposit, the epistemic component is about +1750 to +1940 per step (summed over the horizon) during ordinary following, against −0.003 for the velocity preference and −2 for control effort [OSF, `benign_eps.csv`]. Only differences between policies matter for selection, so the level alone does not decide anything, but the scale suggests that in the benign regime the epistemic term can outweigh the terms that are supposed to shape following. The effect on front-to-rear response times that the ablation found is consistent with an approach incentive. [Opinion] The "mainly pragmatic" statement holds during the conflict, where the collision term is 10⁴–10⁵; I do not think it holds for the pre-conflict driving that sets up the conflict, and the paper does not separate the two.

### 6.5 The norm-conditioned particle filter

During prediction, the procedure of SI 2.1 draws M_n = 32 candidate successor states per particle per step and keeps one with probability proportional to p̆_n [SI Eq. 26]. This is a forward sampler with a per-particle, per-step bias; it does not maintain weights and the resulting particle set is not a sample from p ∝ p̆_n·p₀ in the sense of Eq. 23, because the normalization is local to each particle's 32 candidates. [Opinion] It is a sensible heuristic and the paper's description of its behavior is accurate; "particle filter" oversells what it is during prediction, where there is nothing to filter.

### 6.6 The fit metric for the front-to-rear scenario

Goodness of fit for response times and decelerations is the mean absolute error between the model's posterior regression line and the human regression line over a support interval [Paper, Metrics]. This compares two lines. It is blind to dispersion, which in the model is near zero within a condition (section 4.4) and in humans is large; and the human line from the meta-analysis aggregates studies with a range of lead decelerations and expectancy conditions, against a model run at a single lead deceleration of −6 m/s². [Opinion] The comparison supports the claim that the model's mean response time rises with the time gap at about the right rate, and not more than that.

### 6.7 Scenario-specific code

Each scenario has its own preference module, true-dynamics module, and decoder (`src/rear_end_test/`, `src/oncoming/`, `src/intersection/`, about 400 lines each), plus the hardcoded scenario selector in the planner (item 13). The generalization claim — the intersection scenario run "with the same parameter settings" and "without any parameter tuning" [Paper] — is true of the 13 listed parameters. A reader of the paper alone would not know how much scenario-specific engineering sits beside them, or that the lead vehicle's lateral prediction noise differs by a factor of 100 between scenarios (item 4). The paper does say that norms were implemented per scenario [Paper, Methods], so the point is one of degree.

---

## 7 What stands up well

It would be unbalanced to list only problems. In my reading the following claims are supported by the released artifacts:

- The architecture runs end to end, and the mechanisms operate as described: the threshold delays perception by an amount set by distance; evidence accumulates and triggers a full re-plan; the pedal constraint adds about 0.2 s; the re-plan produces a coordinated maneuver.
- The looming-threshold mechanism is verifiable to the timestep across all 896 deposited runs (section 4.3).
- The qualitative relations claimed in Fig. 3 hold in the deposit: brake response time rises with time gap (median 0.6–0.9 s at the shortest gap to 1.8–2.4 s at the longest); at 15 m/s the brake-only probability rises with gap (0, 3, 6, 34, 56, 69, 66%); braking dominates at 10 m/s (100% brake only at every gap above 0.5 s).
- The authors' code is released in a form that can be run and that reproduces the deposit, which is more than most modeling papers offer, and the deposit includes beliefs and pragmatic-value components per step, which is what made this review possible.
- The discussion volunteers most of the conceptual limitations (non-reactive other agents, one-dimensional perception, hand tuning, no accumulation noise, cultural specificity).

---

## 8 Smaller errata

- Table 1: σ_ω,0 and σ_ω are given in ms⁻²; they are steering rates (s⁻¹).
- SI Eq. 48: the severity factor 0.2 + 0.8(v_ego − v_ν cos(θ_ego − θ_ν))/10 is not floored and would reward a "collision" with a faster lead; the code uses the absolute longitudinal speed difference (`reward.py`), so this is a transcription issue in the SI.
- SI Eq. 14 writes the preference as p(o_τ, a_τ−1); the article's Eq. 13 writes p(o). The code evaluates the preference on observations and actions jointly, so the SI form is the accurate one.
- The deposit README gives the policy arrays as (H, seeds, timesteps, 2); they are (H, timesteps, seeds, 2).
- The paper's count "26 most essential parameters ... 12 from the literature ... 13 free" does not add up to the 25 rows of Table 1 under any reading I could find.
- Fig. 3c caption: "This data includes those samples where the agent is only steering" leaves open whether the leave-road runs are included.

---

## 9 Questions the authors might be able to answer quickly

These are the points on which a short reply would resolve most of the uncertainty in this document.

1. Are the leave-road runs at 25 m/s included in the denominators of Fig. 3c, and were they excluded from Figs. 3d–e? Was this behavior known?
2. Was the Fig. 3a example generated with the released code and parameters? The deposited runs of that condition do not reproduce its timing or maneuver.
3. Is the 0.6 s lead onset a deliberate choice, and was the dependence of the response time on the pre-roll (section 4.2) considered?
4. Is the factor 0.01 on the lead's steering-rate noise in the front-to-rear scenario intentional, and why is it absent in the other two scenarios?
5. Which of the preference-function terms in section 5 (items 2, 3, 6, 7) should be regarded as part of the model, and which as implementation scaffolding?

---

## Appendix A: Definitions and reproduction

All deposit-derived numbers come from `python replication/review_osf.py`, which reads `replication/osf/baseline_conditions.csv` and `seeds.csv` (produced by `replication/validate_osf.py`) and the 28 pickles `Results_rear_end/Exp_{0..27}/Exp_{i}.pkl`. Definitions:

- **Lead onset:** first step at which the true lead acceleration (`eta[..., 10]`) is below −0.1 m/s². This is step 4 (t = 0.8 s) in every run.
- **Perception delay:** steps from lead onset to the first step at which the mean over the 75 belief particles of the lead's acceleration (`b[..., 12]`) is below −0.5 m/s².
- **Re-plan:** first step after onset at which the executed policy differs from the extended reference policy (`a_cont` versus `a_cont_init`).
- **Brake response time:** first executed longitudinal acceleration ≤ −1 m/s² after onset. The paper uses a piecewise-linear fit to velocity for the front-to-rear scenario; the two definitions can differ by about one time step.
- **Leave road, collision, overtaking, brake only, brake and steer:** the authors' categories in `Analysis_rear_end.py` (lines 836–883), read from the deposit's `Analysis_rear_end.xlsx`.
- **ε per step:** −Σ of the first seven components of `v` (the epistemic component, index 7, is excluded, as in `mpc_discrete.py:405–407`).
- **Threshold-predicted closing speed:** φ̇₀(Δx² + d²/4)/d with φ̇₀ = 0.00215 rad/s, d = 1.72 m, Δx the center-to-center distance at onset.

## Appendix B: Per-condition table of the deposit

Columns: condition; fraction of seeds leaving the road (authors' classification) and median time of departure; perception delay (identical across seeds unless noted); surprise per step before onset; evidence accumulated before onset; median brake response time.

| v₀ (m/s) | gap (s) | Δx₀ (m) | leave road | t_off (s) | delay (s) | ε pre-onset | E at onset | RT median (s) |
|---|---|---|---|---|---|---|---|---|
| 25 | 0.5 | 16.7 | 0.72 | 3.2 | 0.0 | 67 500 | 0.30 | 0.9 |
| 20 | 0.5 | 14.2 | 0.09 | 3.6 | 0.0 | 94 400 | 0.43 | 0.6 |
| 15 | 0.5 | 11.7 | 0 | – | 0.0 | 98 800 | 0.44 | 0.6 |
| 10 | 0.5 | 9.2 | 0 | – | 0.0 | 75 700 | 0.34 | 0.8 |
| 25 | 1.0 | 29.2 | 0.69 | 4.2 | 0.2 | 59 000 | 0.27 | 1.4 |
| 20 | 1.0 | 24.2 | 0 | – | 0.2 | 85 800 | 0.38 | 0.6 |
| 15 | 1.0 | 19.2 | 0 | – | 0.2 | 88 700 | 0.40 | 0.6 |
| 10 | 1.0 | 14.2 | 0 | – | 0.0 | 65 100 | 0.29 | 0.8 |
| 25 | 1.5 | 41.7 | 0.69 | 4.3 | 0.4 | 39 500 | 0.18 | 1.4 |
| 20 | 1.5 | 34.2 | 0.03 | 5.0 | 0.4 | 61 500 | 0.28 | 0.8 |
| 15 | 1.5 | 26.7 | 0 | – | 0.2 | 68 100 | 0.31 | 0.8 |
| 10 | 1.5 | 19.2 | 0 | – | 0.2 | 50 100 | 0.22 | 0.8 |
| 25 | 2.0 | 54.2 | 0.56 | 4.4 | 0.6 | 25 200 | 0.11 | 1.4 |
| 20 | 2.0 | 44.2 | 0 | – | 0.4 | 43 000 | 0.19 | 1.1 |
| 15 | 2.0 | 34.2 | 0 | – | 0.4 | 47 400 | 0.21 | 1.0 |
| 10 | 2.0 | 24.2 | 0 | – | 0.2 | 34 200 | 0.15 | 1.0 |
| 25 | 2.5 | 66.7 | 0.47 | 5.0 | 1.0 | 18 500 | 0.08 | 1.8 |
| 20 | 2.5 | 54.2 | 0 | – | 0.6 | 26 600 | 0.12 | 1.2 |
| 15 | 2.5 | 41.7 | 0 | – | 0.4 | 27 900 | 0.13 | 1.2 |
| 10 | 2.5 | 29.2 | 0 | – | 0.2 | 20 900 | 0.09 | 1.2 |
| 25 | 3.0 | 79.2 | 0.44 | 5.3 | 1.2 (26 seeds; 6 seeds 0.0) | 12 200 | 0.05 | 2.2 |
| 20 | 3.0 | 64.2 | 0.03 | 6.4 | 1.0 | 14 400 | 0.06 | 1.8 |
| 15 | 3.0 | 49.2 | 0 | – | 0.6 | 13 900 | 0.06 | 1.4 |
| 10 | 3.0 | 34.2 | 0 | – | 0.4 | 10 900 | 0.05 | 1.6 |
| 25 | 3.5 | 91.7 | 0.53 | 6.0 | 0.0 (18 seeds) to 1.6; belief drifts | 7 600 | 0.03 | 2.4 |
| 20 | 3.5 | 74.2 | 0 | – | 1.2 (31 seeds; 1 seed 0.0) | 6 700 | 0.03 | 2.0 |
| 15 | 3.5 | 56.7 | 0 | – | 0.8 | 6 200 | 0.03 | 1.8 |
| 10 | 3.5 | 39.2 | 0 | – | 0.4 | 5 400 | 0.02 | 1.8 |

Gap is bumper-to-bumper; Δx₀ is center-to-center (gap × v₀ + 4.2 m).
