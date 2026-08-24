# Crash causation in the active inference driver: a plan for generating rear-end crashes and testing them against the QUADRIS scenarios

Proposal, 2026-08-23. Prepared by Claude at the request of Jonas Bärgman. Markdown is the source; Word and PDF are generated from it. Provenance tags as elsewhere in this repository: [Paper] Schumann et al. (2026), [Code] their released code, [B24] Bärgman, Svärd, Lundell & Hartelius (2024), [W25a] Wu, Flannagan, Sander & Bärgman (2025, IEEE T-ITS, arXiv 2406.15538), [W25b] Wu, Sander, Flannagan, Zhao & Bärgman (2025, IAVVC), [W26] Wu, Sander, Flannagan & Bärgman (2026, preprint, "Practical validation of synthetic pre-crash scenarios"), [Repo] this repository, [Opinion] a judgment.

---

## 1 The question, and why it is well posed

The active inference model describes an attentive driver's *response* to a conflict. It has no account of why the conflict becomes a crash: no off-road glances, no drowsiness, no habitual tailgating beyond what its preference function happens to produce. The crash-causation model of [B24] (the "CBM") has exactly those accounts, but its response process is a fixed 0.5 s delay after the eyes return to the road and a sampled maximum deceleration. The proposal is to put the two together: keep the CBM's four causation mechanisms as separable, switchable components, replace its response process with the active inference driver, generate rear-end crashes from the QUADRIS seed scenarios, and test the result against the QUADRIS reference with the practical-equivalence framework of [W25b, W26].

Three things make this well posed rather than speculative:

1. **There is a template.** Section 3.1.3 of [W26] does precisely this with BMW's Stochastic Cognitive Model: each of the 5 000 QUADRIS seeds is re-simulated with the lead vehicle's behavior and the initial following distance fixed and the follower governed by the SCM; the crashes are weighted by Eq. (10) of that paper and tested for equivalence against a 200-seed reference. The SCM failed every metric, and the authors attribute most of that to finite sampling. The proposed study is the same design with a different follower, and it can learn from what went wrong there.
2. **The mechanisms map cleanly onto the model.** Each CBM sub-model has a natural counterpart in the active inference machinery (section 4), and the authors' code already contains the hook that an off-road glance needs: a gaze state that multiplies observation precision by a factor when the eyes are off the road [Code: `decoder.py:250`, `I_factor`], inherited from the Engström et al. (2024) visual time-sharing model and switched off in the published collision-avoidance runs.
3. **The comparison separates the two halves of the question.** An attentive active inference driver with no causation component should avoid most QUADRIS crashes — that is the benchmark result, and it says which crashes are kinematically unavoidable. The same driver with the CBM components switched on should reproduce the QUADRIS crash population — that tests whether active inference is an adequate *response* model inside a causation model, against the Svärd et al. (2021) looming accumulator that generated QUADRIS in the first place. Running both, plus the CBM's own response process as a control, isolates what the active inference driver adds.

One caveat to state up front: the QUADRIS synthetic scenarios are themselves model-generated (modified IDM plus the Svärd accumulator plus SHRP2 glances, [W25a]), so equivalence with them is equivalence with that generator, not with the world. Their real-world validity is inherited from [W25a]'s own validation against CISS and SHRP2. The 132 real incidents in `Combined_incidents.csv` carry only lead-vehicle profile parameters and cannot be simulated as shipped.

---

## 2 What the three papers provide

### 2.1 Bärgman et al. (2024): the crash-causation model [B24]

Four sub-models, applied to 103 GIDAS pre-crash-matrix rear-end crashes with the follower's evasive maneuver removed:

| sub-model | mechanism | operationalization | parameters |
|---|---|---|---|
| 1 Off-road glance | the driver is not looking when the conflict develops | an off-road glance drawn from the SHRP2 baseline distribution (1 791 epochs, 4 604 glances, 0.1 s bins, longest 6.7 s, ~80% point mass at zero) is anchored at τ⁻¹ = 0.2 s⁻¹ via the "overshot" transform (App. C); no information is accumulated while looking away; a fixed 0.5 s delay from eyes-back-on-road to brake onset | anchor 0.2 s⁻¹ (from Markkula et al. 2016); delay 0.5 s (sensitivity: 0.8 s) |
| 2 Too-close | attentive driver, short gap | the point mass at zero glance duration; the crash follows from the seed kinematics and the sampled deceleration | none |
| 3 Low-deceleration | drivers do not brake as hard as possible | maximum deceleration drawn from 45 SHRP2 crashes with a braking plateau (Fig. 3), 1.5 m/s² bins; ramp at −23.04 m/s³ (sd 0.74) | the empirical distribution |
| 4 No-response | sleepy or otherwise non-responding | no braking at all; added post hoc as 10% of all generated crashes (the max-Δv outcome per seed) | 10% (6.6–20% in the literature) |

Sub-models 1 and 3 are assumed independent. Generated crashes are prevalence-weighted so that each seed contributes equally (weights trimmed at the 5th/95th percentiles). Validation is against GIDAS delta-v after a selection-bias transform (Eq. 2) that is *not* needed here, because the QUADRIS reference already spans the full severity range. The paper's own limitations list includes: no context dependence of glances (drivers at short headways look away less), the 10% no-response share being weakly anchored, the deceleration distribution coming from low-severity SHRP2 crashes, and the no-response sub-model not integrating into continuous simulation.

### 2.2 Wu et al. (2025a): the QUADRIS scenarios [W25a]

The 5 000 synthetic scenarios (20 Hz, both vehicles' speeds and the gap, median 5 s, every one ending in a collision) were produced by sampling lead-vehicle profiles and initial conditions from multivariate models fitted to SHRP2 and CISS, and simulating the follower with a modified IDM (T ~ N(1.5, 0.16) s) combined with the Svärd et al. (2021) brake-response model (looming prediction-error accumulation, an off-road glance anchored at τ⁻¹ = 0.2 s⁻¹ with duration from SHRP2 normal-driving glances, and a partial "looming weight" during glances), plus an "abnormal acceleration" mode for followers who ignore the lead. Each scenario carries a weight proportional to its real-world frequency times the human crash probability in that scenario. Median initial follower speed is 8.3 m/s and median initial THW 2.2 s; about a third of the seeds start below 10 m/s.

### 2.3 Wu et al. (2025b, 2026): the comparison method [W25b, W26]

A Bayesian region-of-practical-equivalence test on a small set of metrics. The 2026 paper fixes the statistics: the reference distribution of each metric is cut into N quantile bins (N = min(⌊n/m⌋, 20), m = 30–50; N = 5 for a 200-seed reference), the same boundaries are applied to the synthetic distribution, and two statistics are formed from the per-bin proportion differences with bin weights ω: θ = max_i |ΔP_i / P_ref,i|·ω_i (worst bin) and Θ = Σ_i |ΔP_i|·ω_i (aggregate). Bayesian distribution models are fitted to both datasets (weighted likelihoods if the data are weighted), θ and Θ are computed for paired posterior draws, and equivalence holds when the 95% HDI of each lies inside its ROPE; the paper uses θ_thd = 0.10 and Θ_thd = 0.05 for a baseline bin of weight 1. Metrics in the demonstration: the lead driver's MAIS2+ injury risk P_inj (logistic in the lead's delta-v, Wang 2022), the no-return time t_nr (last instant at which −9 m/s² would still avoid the crash), and the minimum accelerations of lead and follower. Bin weights come from re-simulating the reference with the system under assessment (an AEB); uniform weights are a legitimate fallback when no system is being assessed. Code: the `bayes-binned-equivalence` repository (Wu, 2026). The 2026 paper also specifies how to weight re-simulated crashes per seed, Eq. (10): ω_sim,i ∝ ω_i / n_crash,i, under the assumption that the model's crash probability per seed approximates the human one.

---

## 3 Mapping the CBM onto the active inference driver

| CBM sub-model | what the active inference driver already does | proposed component | default when disabled |
|---|---|---|---|
| 1 Off-road glance | nothing; eyes are always on the road. The code has the hook: the discrete gaze action I ∈ {on, off} scales observation sd by `I_factor` [Code]; the SI §6 fog experiment uses the same precision-reduction idea | `GlanceSchedule` (a list of off-road intervals per run, sampled from a glance distribution and anchored at τ⁻¹ = 0.2 s⁻¹ by the overshot construction) + `ObservationGate` (during a glance, observation precision on the lead's state is divided by a large factor, so the belief propagates on process noise alone) + `EvidenceGate` (a weight w ∈ [0, 1] on ε during the glance; 0 reproduces the CBM's "no accumulation", the Svärd partial weight is an alternative) | no glances |
| 2 Too-close | inherent: the driver starts at the seed's gap and speed; at short gaps its own accumulator drifts (method review §4.2) and it may re-plan before the lead does anything | none needed; but the **pre-roll** must be handled (section 6) | — |
| 3 Low-deceleration | inherent in the preference trade-off: σ_a = 0.1 m/s² against g_C makes the planner brake "no harder than necessary" [Paper]. Whether its chosen decelerations match the SHRP2 plateau distribution is itself a test (a_f,min is a [W26] metric) | `DecelerationCap` (optional): draw d_max from the SHRP2 distribution and clamp the planner's action space to [−d_max, a_max] instead of [−8, 8] — the literal CBM mechanism, for comparison with the endogenous one | endogenous braking, a_max = 8 m/s² |
| 4 No-response | nothing | `NoResponse`: the run is executed with the follower at constant speed (no agent needed); mixed in post hoc at a fixed share of crashes, as [B24] does, or sampled per seed at a rate that yields that share | no such drivers |
| response process | **the thing under test**: looming threshold → belief → surprise accumulation → re-plan → CEM-planned braking with pedal and jerk constraints | `ResponseModel` interface with two implementations: `ActiveInferenceResponse` and `CBMResponse` (0.5 s delay after eyes-on, ramp at −23 m/s³ to d_max) — the latter is the control | — |

All components sit behind a single `CausationConfig` dataclass of booleans and parameters, so any subset can be switched on, and the configuration is written into every output file.

---

## 4 Two execution tiers

The authors' code costs about 18 s of CPU per simulated step per run [Repo]. A QUADRIS scenario is about 25 steps at Δt = 0.2 s. That makes the study's size a real design variable, and I propose two tiers that answer the same question at different fidelity.

**Tier 1 — hybrid, open-loop timing (cheap; hours for 100 seeds).** Use the verified half of the active inference driver only: the preference function evaluated on the seed's kinematics gives ε(t) pointwise; the accumulator with the OSF-calibrated level (notes/05 §4b: score 0.855, onset error median 0.0 s on the authors' own runs) gives the response onset; the glance components act on that accumulator; the execution is the CBM's (ramp to d_max). This runs in seconds per scenario in NumPy, so all 5 000 seeds are within reach, and the glance distribution can be swept bin by bin as [B24] does instead of sampled. What it cannot capture: the closed-loop planner's choice of deceleration, swerving, and the imagined-future spread that makes the authors' accumulator drift before an event.

**Tier 2 — full closed loop with the authors' code (expensive; about one CPU-day per 20 seeds).** Replace the scripted lead vehicle with a trajectory replay of the seed's lead profile, run the agent with `GlanceSchedule`/`ObservationGate` acting through the existing gaze state, batch the glance variants of one seed as one parallel run (their batching handles identical configurations; a per-batch-element gaze schedule is a small change in our wrapper, not in their code), and checkpoint every few steps as `run_rear_end_single.py` already does. Twelve glance bins × 25 steps × ~30 s per batched step ≈ 2.5 h per seed on CPU; 20 seeds is a weekend, 100 seeds is a GPU job.

**Recommendation.** Tier 1 on a weighted random sample of 100 seeds first (the sample you suggested; stratified by speed so the sub-10 m/s third is represented), then Tier 2 on 20 of those seeds to check that the closed-loop driver's onsets and decelerations agree with the hybrid's. If they do, Tier 1 carries the equivalence test on the full 5 000; if they do not, the disagreement is itself the finding, and Tier 2 is scaled up on a GPU.

---

## 5 Comparison protocol

Following [W26] section 3, with the SCM-based dataset as the template:

1. **Seeds and weights.** Sample 100 seeds from the 5 000 with probability proportional to the QUADRIS weight, stratified into three initial-speed bands (< 10, 10–15, > 15 m/s). Keep every seed's weight ω_i.
2. **Conditions.** Four follower models on the same seeds: (A) attentive active inference, no causation components — the benchmark; (B) active inference + CBM components (glances, optional deceleration cap, no-response mixture); (C) CBM response process + CBM components — the control, which should reproduce QUADRIS closely because it is a near-relative of its generator; (D) active inference + glances only, to attribute differences between A and B.
3. **Per-seed sweep instead of Monte Carlo.** For each seed, run one simulation per glance bin (overshot distribution, 0.1 s bins) and, if the cap is on, per deceleration bin, and weight outcomes by the bin probabilities — the [B24] design, which the authors note reduced simulations thirty-fold relative to sampling, and which avoids the finite-sample problem that [W26] blames for the SCM result.
4. **Crash weighting.** Per seed, crash probability p_c,i = Σ_bins P(bin)·1[crash]; each crash outcome carries ω_i · P(bin) / p_c,i, following [W26] Eq. (10), so a seed's crashes sum to its QUADRIS weight. Seeds with p_c,i = 0 are reported as avoided, not dropped silently.
5. **Metrics.** P_inj of the lead driver (Wang 2022 logistic on the lead's delta-v; the delta-v convention of [W25a] §III-F), t_nr, a_l,min (fixed by the seed, so it only moves through which seeds crash), a_f,min, and — added for this study — the follower's brake response time relative to the τ⁻¹ = 0.2 s⁻¹ anchor, because that is the quantity the two response models differ on.
6. **Statistics.** θ and Θ with quantile bins from the reference (N = 5 for 100–200 reference seeds), uniform bin weights in the first pass (no system under assessment; [W26] §2.3 allows this), a severity-based weight function as a sensitivity check, ROPE thresholds 0.10 and 0.05, 95% HDIs from Bayesian fits as in [W26] or, if the `bayes-binned-equivalence` code is unavailable, from weighted bootstrap.
7. **Sanity and plausibility checks before any test** ([W26] §4.2): crash rate per condition, share of seeds avoided, decelerations and jerks within physical ranges, no road departures (the 25 m/s failure mode of the published model is a live risk here and must be counted, not filtered).
8. **Read-out.** Condition A: fraction of QUADRIS crashes an attentive active inference driver avoids, by speed band and by t_nr. Condition B versus reference: equivalence per metric and the per-bin diagnostics. B versus C: what the active inference response adds or costs relative to the CBM's fixed delay. B versus D: how much the deceleration cap matters.

---

## 6b Exposure: what re-simulating crashes does and does not capture

*Added 2026-08-23 in response to a criticism of the SCM approach in [W26]: applying glances
(or any new follower) to crash scenarios only captures half of the causation, because the
exposure — the everyday situations that would become crashes in combination with a glance —
is not in the seed set.*

The criticism is real and it applies here. The 5 000 QUADRIS scenarios are conditioned on
crashing under the generator's own causation (IDM + Svärd accumulator + SHRP2 glances +
abnormal acceleration). Re-simulating them with a different follower therefore answers
"what does this driver do in situations that crashed for that driver", not "what crashes
does this driver produce in traffic". Two consequences: condition A's "fraction avoided" is
a fraction of *generator crashes*, not of conflict exposure; and situations that the
generator's driver survived but the new driver would not are absent from the seed set
entirely.

What can be done about it, in increasing order of completeness:

1. **Count non-crashes.** The bin sweep runs every seed through the full glance and
   deceleration distributions, including the ~80% on-road point mass, so each seed yields a
   crash *probability* p_c,i, not just crashes. Avoided outcomes are first-class results.
2. **Undo the crash conditioning in the weights.** The QUADRIS weight is
   ω_i ∝ f_i · p_c,human,i ([W25a] Eq. 6): exposure frequency times the human crash
   probability. Dividing ω_i by a per-seed crash probability recovers an exposure weight
   f_i. We estimate that probability by running the seed through the *generator-like*
   response model (condition C, CBM response with the full glance sweep): p_c,C,i ≈
   p_c,human,i as the generator models it. The runner implements this as the "exposure
   weights" variant (`aggregate(..., exposure_pc=...)`); results are reported under both
   weightings. This corrects the weighting but not the support: seeds the generator would
   never crash are still missing.
3. **Get the pre-filter scenario set.** The cleanest fix is upstream: the [W25a] generator
   sampled lead profiles and initial conditions from fitted multivariate models and kept
   the runs that crashed. The sampled-but-not-crashed scenarios (or the fitted distribution
   models themselves) would be a true conflict-exposure seed set. This is a concrete ask to
   Jian Wu — arguably the most valuable single item on the request list.
4. **Use the near-crashes.** `Combined_incidents.csv` contains 82 SHRP2 *near-crashes*
   (weights included) alongside the 132 crashes — conflicts that did not crash, i.e.
   exposure the crash-only critique says is missing. They carry only lead-profile
   parameters [W24: v_c, a_1, a_2, τ_s, τ_1, τ_2], so a follower initial state must be
   sampled (the [W25a] models describe how), but `quadris.load.lead_profile_from_params`
   already reconstructs their lead profiles.

Framing for any write-up: with option 2 the study estimates "the crash population this
response model produces from (a reweighted approximation of) rear-end conflict exposure",
and the residual conditioning (option 2's support limitation) is stated as the main
threat to validity until option 3 is available.

## 6c The anchor: is τ⁻¹ = 0.2 s⁻¹ the right timing reference

Three distinct roles of the anchor should be kept apart:

1. **As glance placement** (where the causal glance sits): the CBM's overshot construction
   at τ⁻¹ = 0.2 s⁻¹ encodes two empirical claims from Markkula et al. (2016) — drivers who
   look back after that point respond immediately, and drivers do not begin new off-road
   glances beyond it. Anchoring at the *crash* instead would condition glance placement on
   the outcome (the glance must overlap the impact), which is the crash-only bias again in
   miniature; it is implemented (`glance_anchor="crash"`) so its effect can be shown, but
   it is not recommended. The assumption-free alternative is the **renewal process**
   (`glance_anchor="process"`): on/off glancing over the whole scenario with off-road
   durations from the distribution and glance starts independent of the event by
   construction. The overshot-at-anchor construction is exactly the analytic shortcut for
   this process *given* the two Markkula claims; the process needs no such claims and is
   cheap in tier 1. Recommendation: process as the reference implementation, anchored
   overshot as the fast approximation, and report both.
2. **As the response trigger** (the CBM's "respond at anchor + 0.5 s"): the active
   inference driver does not need it — it has its own trigger — and the first tier-1 runs
   show it responding at a median of about 1.2 s *after* the anchor with a wide spread
   (IQR roughly 0.5–1.9 s), where the CBM responds at a fixed 0.5 s. Whether the 0.2 s⁻¹
   rule is "right" is therefore itself a testable difference between the two response
   models rather than a shared assumption, and the response-time-versus-anchor metric is
   in the outputs for exactly this comparison.
3. **As a reporting reference** (what response times are measured from): here the anchor is
   as good as any fixed, kinematically defined instant, and better than the crash (which
   moves with the response). Keep it.

## 6 Things that will bite, and what to do about them

- **Pre-roll accumulation.** In the authors' own runs the accumulator reaches 18–44% of threshold before the lead brakes at gaps ≤ 1.5 s (method review §4.2), and would re-plan spontaneously within 2–7 s at gaps ≤ 2 s. QUADRIS seeds run ~5 s with a median initial THW of 2.2 s, so some seeds will re-plan before the lead profile starts. Options: start the accumulator at its benign stationary value rather than zero (honest: that is what a driver who has been following for a while has), or begin each seed with a short settling period. Either way the choice must be a config parameter and reported. For Tier 1 this does not arise (the pointwise field is zero in steady following).
- **Low speeds.** A third of the seeds start below 10 m/s, under the range the model was tuned and calibrated for (10–25 m/s; the a_OV,min table starts at 10 m/s). Tier 1 is speed-agnostic in form; Tier 2 will extrapolate. Report results by speed band and do not pool before looking.
- **Glance data.** The SHRP2 off-road glance distribution ([B24] Fig. 1) and the maximum-deceleration distribution (Fig. 3) are not in this repository. You are an author on both; the "Extra Material" of [B24] has the overshot-transform code. Without the real distributions I would use a digitized Fig. 1 and say so — but the real data are much better.
- **Deterministic timing.** The published driver's response timing is identical across seeds within a condition (method review §4.4). The variability of the generated crashes will therefore come almost entirely from the glance draw and the deceleration draw, which is also true of the CBM. That is fine for the comparison but should be stated, and it argues for the bin sweep over Monte Carlo.
- **No-response share.** [B24] adds 10% no-response crashes post hoc. Adding them to a forward simulation at 10% of *drivers* gives a different crash share. Follow [B24]: mix at the crash level, and treat the share as a sensitivity parameter (6.6–20%).
- **The reference is a model.** Equivalence with QUADRIS is equivalence with IDM + Svärd + SHRP2 glances. Condition C is there to make this explicit; if C is not equivalent to QUADRIS either, the framework's own diagnostics (per-bin contributions) will show whether the gap is in the seeds we sampled or in the response process.
- **Road departures.** The published model leaves the road in half of its 25 m/s runs. QUADRIS seeds are mostly slower, but the mechanism is still there. Count them as a separate outcome class from the start.

---

## 7 Software architecture

*As built, 2026-08-23 (tier 1 complete; tier 2 pending).* Three packages with a deliberate
separation: the **assessment is its own package** (`src/equivalence/`) with no knowledge of
driving, seeds, or causation, so it can be reused for any synthetic-versus-reference
comparison; the seed handling is its own package (`src/quadris/`); and the causation layer
(`src/causation/`) is the only place that knows about driver models.

```
src/equivalence/         REUSABLE: Wu et al. (2026) binning/ROPE equivalence testing
    binned.py            quantile bins, bin proportions, theta/Theta (Eq. 1-2), N rule (Eq. 4)
    test.py              equivalence_test(ref, syn, weights, ...) -> EquivalenceResult;
                         weighted-bootstrap HDIs by default, hook for the paper's posterior
                         draws; MetricSpec / run_metric_suite for a set of metrics
    report.py            markdown tables incl. the per-bin diagnostics
src/quadris/
    load.py              Seed (lead profile + follower initial state + weight); synthetic CSV
                         loader; the 214 real incidents; lead profiles from the [W24] parameters
    sample.py            weight-proportional sampling, stratified by initial speed band
    metrics.py           lead delta-v (equal-mass ASSUMPTION), P_inj (Wang 2022), t_nr, a_min
src/causation/
    config.py            CausationConfig — every switch and parameter; named conditions A-D;
                         describe() written into every output
    glances.py           GlanceDistribution (CSV or labelled stand-in), overshot transform
                         (App. C of [B24]), anchored / marginal-overshot / renewal-process
                         schedules, evidence and precision gates
    decel.py             DecelerationDistribution (CSV or labelled stand-in)
    no_response.py       (folded into runner: constant-speed roll-out + post-hoc mixture)
    response.py          ResponseModel protocol; ActiveInferenceResponse (tier 1: pointwise
                         code-form field + zero-noise constant-acceleration prediction channel,
                         accumulator with the OSF-calibrated drift rate); CBMResponse
    simulate.py          pre-response kinematics ("original" IDM profile or "constant"), braking
                         execution (jerk ramp to d_max), crash detection
    runner.py            per-seed bin sweep, restartable condition runs (append+fsync+skip),
                         aggregate() with Wu Eq. 10 crash weights and the exposure-weight variant
replication/causation/
    calibrate_accumulator.py   fits the tier-1 drift rate on the 896 deposited trials
    run_quadris.py             CLI: seeds, conditions A-D, assessment, summary.md
tests/test_causation.py        27 property tests (all passing), including the worked theta
                               example of [W26] Fig. 3 and the config-discipline checks
```

Two tier-1 design points found during implementation, both documented in the code:

- **The prediction channel is necessary.** The pointwise field alone cannot respond to a
  stationary or creeping lead (the safety-margin term needs speed; the collision term needs
  contact), which is exactly the low-speed third of QUADRIS. `predicted_collision_deficit`
  adds the mean of the model's prediction ensemble: a constant-acceleration rollout over the
  6 s horizon with the collision cost and the running minimum of SI Eq. 47.
- **The accumulator calibrates onto the paper's own drift rate.** Fitting the tier-1 drift on
  the 896 deposited closed-loop trials gives lambda = 5.6e-6 per second of epsilon — exactly
  the paper's 10^-5.95 per 0.2 s step — and reproduces 69% of the closed-loop brake onsets
  within +-0.2 s (86% within +-0.6 s, median error -0.2 s). The closed-loop model and the
  tier-1 surrogate are, to that accuracy, the same accumulator fed by the same quantity.

## 8 Inputs needed

1. SHRP2 baseline off-road glance distribution (0.1 s bins with the point mass at zero) and the overshot-transform code from [B24]'s Extra Material. *Status 2026-08-23: not publicly obtainable — the paper's data statement reads "The authors do not have permission to share data", and the NAP copy of the S08A report is login-gated. The pipeline therefore runs on a clearly labelled parametric stand-in (`causation.glances.standin_shrp2_glances`: lognormal, on-road share 0.80, truncated at the published longest glance 6.7 s) and accepts the real bins via `GlanceDistribution.from_csv` the moment you provide them.*
2. SHRP2 maximum-deceleration distribution (45 crashes, Fig. 3 of [B24]) — or the raw values.
3. The delta-v convention used for QUADRIS (vehicle masses are not in the CSV; [W25a] §III-F describes the estimate). *Implemented meanwhile with an equal-mass assumption (lead delta-v = half the relative impact speed), marked ASSUMPTION in `quadris.metrics`.*
3b. The pre-filter scenario set or the fitted scenario-generation models of [W25a] (section 6b, option 3) — the request that would resolve the exposure critique properly.
4. Access to the `bayes-binned-equivalence` repository, or permission to reimplement θ/Θ with bootstrap HDIs.
5. A decision on the accumulator initialization for Tier 2 (section 6, first bullet).

---

## 9 Work plan

| step | what | status |
|---|---|---|
| 1 | `src/quadris/`: loader, sampler, metrics | **done 2026-08-23** |
| 2 | `src/causation/` with all components, both response models, config discipline, property tests | **done** (27 tests passing; distributions are stand-ins) |
| 3 | Tier 1, conditions A–D, 100 seeds; sanity checks; first tables | **done** (section 11) |
| 4 | Equivalence module (`src/equivalence/`, reusable), ROPE decisions, per-bin diagnostics | **done** (bootstrap HDIs; the paper's parametric posterior draws remain an open hook) |
| 5 | Real glance and deceleration distributions plugged in, results regenerated | **done 2026-08-24** — digitized from [B24] Figs. 1 and 3 (`replication/causation/digitize_b24.py`; two-route calibration agrees within 0.9%, deceleration counts sum to exactly n = 45); the actual SHRP2 bins would still be better |
| 6 | Tier 2 adapter: lead replay, gaze schedule through `I_factor`, per-seed batching, checkpointing; 5-seed smoke test | **done 2026-08-24** (section 11.4; glance gate exercised on one seed, both mild and hard) |
| 7 | Tier 2 on 20 seeds; per-seed comparison with tier 1; decide who carries the 5 000 | next; multi-day restartable CPU job or a short GPU one (section 11.4 point 4); needs the desired-speed convention decision for low-speed seeds |
| 8 | Results document alongside this plan | **done 2026-08-24** — `docs/crash_causation_results.md`: method summary, digitized inputs, real-distribution results, statistics and figures against the QUADRIS reference, the anchor study, and the glance-gate finding |

Steps 1–4 give a complete, defensible first result without touching the expensive model. Step 5 is where the active inference driver proper enters, and it is the step most likely to surface surprises.

---

## 10 Where this should be documented

This plan is a separate document because the method review is a review of a published paper and should stay that. I suggest the same pattern for the results: `docs/crash_causation_results.md` when there are results, with the reading notes of the three papers staying here (section 2) rather than in `notes/01`, which is reserved for the active inference papers. The handbook's chapter 08 (crash causation) should get a pointer to this plan and, later, to the results; its current proposals were written before these three papers were in the repository and largely anticipate section 3.

---

## 11 Tier-1 first results (100 seeds, stand-in distributions)

*Superseded 2026-08-24: `docs/crash_causation_results.md` carries the current results —
digitized real distributions, the no-brake counterfactual, process glance placement, the
abnormal-acceleration fifth component, and the sensitivity ladder. This section remains as
the record of the first pass and of what each later correction changed.*

*Added 2026-08-23, from the completed conditions A–D run (`replication/causation/out/`; full
tables in `out/summary.md`, configurations in the per-condition .json files). One warning governs
everything in this section: the glance and maximum-deceleration distributions are the labelled
parametric STAND-INS of section 8, not the SHRP2 data. The numbers show that the pipeline
works end to end and what kind of answer it produces; they are not yet the study's answer.*

### 11.1 Crash generation

| condition | response | components | seeds crashing (any bin) | weighted crash prob | avoided seeds | mean P_inj (Eq. 10 weights) | reference |
|---|---|---|---|---|---|---|---|
| A | active inference | decel. cap | 49/100 | 0.011 | 51 | 0.005 | 0.006 |
| B | active inference | glances, decel. cap, no-response | 100/100 | 0.015 | 0 | 0.004 | 0.006 |
| C | CBM (control) | glances, decel. cap, no-response | 100/100 | 0.006 | 0 | 0.004 | 0.006 |
| D | active inference | glances, decel. cap | 100/100 | 0.015 | 0 | 0.004 | 0.006 |

Three observations:

1. **The attentive active inference driver avoids about half of the QUADRIS crash seeds
   outright** (51/100 across the entire deceleration sweep), and its weighted crash
   probability in the rest is 0.011. This is the section 5 read-out for condition A: roughly
   half of the generator's crashes are kinematically escapable for an attentive driver with
   this response process, and half are not.
2. **The response models differ exactly where section 6c predicted.** Across all 100 seeds
   the active inference onset sits at a median of 1.25 s after the τ⁻¹ = 0.2 s⁻¹ anchor with
   a wide spread (IQR 0.55–1.90 s); the CBM control responds at its fixed 0.50 s. The
   consequence is a factor ~2.5 in weighted crash probability between B (0.015) and C
   (0.006) with identical causation components — the response model, not the glance model,
   drives the difference between the two.
3. Adding the no-response mixture (B versus D) barely moves the aggregate numbers at this
   share (10% of crashes), as expected from its post-hoc construction.

### 11.2 Equivalence against the 5 000-scenario reference

No condition is practically equivalent to the QUADRIS reference on any metric, under either
weighting. Headline θ (worst bin, ROPE [0, 0.10]) for P_inj, with 95% bootstrap HDIs:

| condition | Eq. 10 weights | exposure weights (§6b) |
|---|---|---|
| A | 0.30 [0.18, 0.73] | 3.75 [3.57, 3.96] |
| B | 1.17 [1.12, 1.29] | 2.83 [2.79, 2.97] |
| C | 0.89 [0.85, 1.03] | — (defines the weights) |
| D | 1.20 [1.15, 1.31] | 2.94 [2.90, 3.08] |

How to read this, in order of importance:

- **The control fails too.** Condition C — the CBM response process that is a near-relative
  of the QUADRIS generator — misses equivalence on every metric (P_inj θ = 0.89 against a
  ROPE of 0.10). Section 6 anticipated this possibility; the per-bin diagnostics say the
  synthetic crash population over-produces the lowest-severity bin (P_syn = 0.38 versus
  0.20 in C, 0.43 in B) and under-produces the highest (0.10 versus 0.20). With stand-in
  glance and deceleration distributions this is the expected signature — the stand-ins put
  too much mass on short glances and moderate decelerations — so the failure cannot yet be
  attributed to any response model. Step 5 of the work plan (real distributions) is the
  gate before any such attribution. This also mirrors the SCM result in [W26], where the
  authors attribute the failures largely to sampling and distributional issues rather than
  the driver model.
- **B sits close to C, and both sit far from the reference.** On t_nr and a_l,min the two
  are statistically indistinguishable (θ = 0.66 versus 0.62, and 0.687 for both); the gap
  between them is concentrated in the severity metrics (P_inj, dv_lead), where B's later
  onsets shift crashes into the extreme bins. The B-versus-C comparison — the study's
  actual question — is therefore already informative in shape even though both fail the
  absolute test.
- **The exposure weighting (§6b option 2) sharpens rather than flatters.** Dividing out the
  per-seed crash probability concentrates nearly all synthetic mass in the lowest-severity
  bin (P_syn = 0.77–0.95), pushing θ to 2.8–3.8. That is the expected behavior — exposure
  weighting up-weights the seeds that rarely crash, whose crashes are marginal and mild —
  and it quantifies how strongly the crash-conditioned seed set shapes the answer. Both
  weightings should continue to be reported.
- Two technical notes. P_inj and dv_lead produce identical tables because P_inj is a
  monotone transform of dv_lead, so the quantile bins coincide; one of them can be dropped
  from future tables. Condition A's equivalence test rests on only 104 crash records and
  its HDIs are correspondingly wide; A's purpose is the avoided-fraction read-out, not the
  equivalence test.

### 11.3 The glance anchor, tested across all 100 seeds

Section 6c argued the anchor question from construction; the three placements are now run
on the same 100 seeds (conditions C and D; `out/summary_process.md`, `out/summary_crash.md`;
runner flag `--glance-anchor`). Weighted crash probability and the P_inj equivalence
statistic θ (Eq. 10 weights):

| glance placement | crash prob, C (CBM) | crash prob, D (act. inf.) | P_inj θ, C | P_inj θ, D |
|---|---|---|---|---|
| overshot at τ⁻¹ = 0.2 s⁻¹ | 0.006 | 0.015 | 0.89 | 1.20 |
| renewal process (assumption-free) | 0.007 | 0.026 | **0.31** | 1.04 |
| crash-anchored | 0.023 | 0.028 | 0.84 | 0.87 |

Three conclusions:

1. **Crash-anchoring inflates crash probability roughly four-fold for the CBM** (0.006 →
   0.023) and about 1.9-fold for the active inference driver — the conditioning-on-outcome
   bias of section 6c point 1, now quantified at population level rather than on the single
   illustrative seed. Its θ values look no worse, which is itself the warning: the bias
   inflates *how often* crashes happen more than it distorts *which* crashes happen, so the
   equivalence test alone would not catch it.
2. **For the CBM, the overshot-at-anchor construction reproduces the renewal process's
   crash probability almost exactly** (0.006 versus 0.007) — the Markkula-claims shortcut
   works as advertised for a response model that reacts at a fixed delay. For the active
   inference driver it does not transfer as cleanly (0.015 versus 0.026): glances placed
   anywhere in the scenario interact with its evidence accumulation, which the
   anchor-locked placement cannot represent. For condition D the process implementation
   should be the default, as section 6c recommended.
3. **Process glances move the CBM control markedly closer to the reference** (P_inj θ 0.89
   → 0.31, Θ 0.48 → 0.12) — consistent with QUADRIS having been generated with
   renewal-style glance behavior, and a hint that part of the section 11.2 failures is the
   glance *placement* model rather than the stand-in *duration* distribution. Still not
   equivalent, and stand-ins still apply.

The response-onset metric is unaffected by the anchor choice (D's median stays 1.25 s
after the reporting anchor under all three placements), confirming that the anchor's
reporting role (section 6c point 3) is separable from its placement role.

### 11.4 Tier-2 smoke test: the closed-loop driver on five QUADRIS seeds

*Added 2026-08-24. The tier-2 adapter (work-plan step 6) is built —
`replication/causation/tier2_rear_end.py`: the authors' closed-loop model with the
scripted lead replaced by a replay of the seed's lead-speed profile, a forcible gaze
schedule acting through the code's own `I_factor` observation gate, checkpointing, and
seed-level restart. The authors' files are untouched; the replay dynamics and run loop are
swapped into the loaded module namespace. Lead replay was verified against the seed
profiles step by step. Run: the five v_f0-quintile seeds of the tier-1 sample, attentive,
four repeats each (`tier2/smoke_results.csv`).*

| seed | v_f0 [m/s] | tier-1 onset [s] | tier-2 onset [s] | tier-1 outcome | tier-2 outcome (4 repeats) |
|---|---|---|---|---|---|
| 3456 | 0.0 | 3.65 | no response | avoided | trivially avoided — the agent never moves |
| 2387 | 1.7 | 3.60 | 5.2–5.4 | avoided | avoided (brakes to a stop) |
| 1722 | 6.7 | 4.05 | 3.2 | crashed (some bins) | avoided, min gaps 0.9–1.7 m |
| 4799 | 14.0 | 2.30 | 2.4 | crashed | 3/4 avoided with a lane change, 1/4 crash |
| 871 | 35.5 | 1.65 | 1.4–2.2 | crashed | 4/4 crash, high impact speeds, all leave the road |

Findings, in decreasing order of consequence:

1. **Onsets agree where the model is in its element.** For the seeds inside or near the
   calibrated speed range the closed-loop onsets sit within 0.1–0.9 s of the tier-1
   surrogate (2.4 vs 2.3 s; 1.4–2.2 vs 1.65 s; 3.2 vs 4.05 s), responding slightly
   earlier and avoiding more — the closed loop can brake harder than the sampled
   deceleration caps and can swerve, which tier 1 cannot represent. This is the step-7
   comparison in miniature, and it supports letting tier 1 carry the statistics while
   tier 2 spot-checks.
2. **The two out-of-range seeds fail in instructive, distinct ways.** The stopped
   follower (v_f0 = 0) never moves: its desired speed is initialized to its initial
   speed, so a creeping-queue seed has no motive to accelerate into the conflict the way
   the generator's follower did — tier 2 needs a desired-speed convention for QUADRIS
   seeds before those seeds mean anything (a config decision, now flagged in the
   adapter). The 35.5 m/s seed — far above the model's 10–25 m/s design range — crashes
   in all repeats with 15–19 m/s relative impact speed and leaves the road laterally by
   6–15 m, the documented high-speed lane-change failure mode; road departure must be a
   separate outcome class in any tier-2 batch (section 5, sanity check 7).
3. **The glance gate is not the CBM's glance gate, demonstrably.** Forcing a 1.0–3.0 s
   off-road glance on seed 4799 delays the response by at most one step — onset 2.4–2.6 s,
   inside the glance — under the authors' default observation-noise factor (3) and under
   a hard gate (factor 1000) alike. The lead's braking had been registered before the
   glance began, and the belief then coasts forward on its own norm-shaped prediction, so
   the accumulator keeps filling from remembered evidence; eyes-off blocks new evidence,
   not inference. The CBM instead forbids any response until eyes return plus 0.5 s.
   The two mechanisms therefore diverge exactly when a glance begins after conflict
   onset — and coincide when the glance covers the onset — which is a testable behavioral
   distinction between the architectures, and the reason tier 1 carries an explicit
   evidence gate (weight 0 = CBM) separate from the precision gate. Incidentally, the
   hard gate produced fewer crashes than the mild one (0/4 versus 2/4) — with four
   repeats this is anecdote, not result, but it warns against assuming the gate strength
   maps monotonically onto risk.
4. **Cost is highly variable and dominated by a few seeds:** 3 minutes to 4 hours per
   seed (median roughly one hour) on this CPU, with no obvious predictor. The 20-seed
   step 7 is a multi-day restartable CPU job or a short GPU one.

### 11.5 What this changes in the plan

Nothing structural. The pipeline runs end to end (crash generation, both weightings, θ/Θ
with per-bin diagnostics), restarts cleanly after interruption, and produces the comparisons
the protocol calls for. One protocol default changes: the renewal-process glance placement
becomes the reference implementation for the active inference conditions (section 11.3
point 2), with the anchored overshot kept as the CBM-compatible approximation. The two
actions it sharpens: step 5 (real SHRP2 glance and
deceleration distributions) is now clearly the binding step, since the stand-ins plausibly
dominate every equivalence failure; and the section 6b request for the pre-filter scenario
set gains urgency, since the exposure-weighting results show how much the crash-conditioned
seeds constrain what any follower model can reproduce.
