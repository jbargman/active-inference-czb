# Validation: our results against the published results

A side-by-side comparison of every quantitative claim in Schumann et al. (2026) that we are in
a position to check, against:

- **Track A** — the authors' own code, run here (`replication/run_rear_end_single.py`)
- **Track B** — the independent NumPy re-implementation (`src/aidriver/`)

Regenerate everything with `python replication/validate.py`
(figure: `figures/validation_rear_end.png`).

> **Status.** Track B: full 28-condition sweep complete, 5 repeats each (140 runs, 33 min).
> Track A: two conditions complete — v0 = 15 m/s / gap 1.5 s (Fig. 3a) and v0 = 25 m/s /
> gap 1.0 s (Fig. 3b). Neither track has been run on the lateral incursion or intersection
> scenarios; see §5 for why.

---

## 1. The headline case — front-to-rear, v₀ = 15 m/s, time gap 1.5 s

This is the paper's Fig. 3a, for which it gives a full timing decomposition.

| quantity | **paper** | **Track A** (authors' code) | **Track B** (ours) |
|---|---|---|---|
| lead vehicle brakes at | 0.8 s | 0.8 s | (by construction) |
| model perceives braking | 1.4 s (delay **0.6 s**) | ~1.0 s (delay ~0.2 s) | ~0.2 s |
| evidence threshold reached | 2.0 s (**+0.6 s**) | 1.6–1.8 s | ~immediate |
| first deceleration | 2.2 s (**+0.2 s** pedal) | 1.6–1.8 s | 3.2 s (t_brake 3.0) |
| **brake response time** | **1.4 s** | **0.92 s** (0.80–1.04) | **1.00 s** (0.2–1.4, n = 5) |
| deceleration | −3 to −5 m/s² | −3.85 m/s² | −7.16 m/s² (−6.0 to −7.9) |
| maneuver | **brake only** | brake + swerve (3 of 4 runs) | brake + swerve (4 of 5 runs) |
| collision | no | no | 3 of 5 runs |

**Reading.** Track A reproduces the *structure* — a delayed response, then coordinated
avoidance — with a response time about 0.5 s short of the published value, and it swerves
where the paper brakes.

Track B's response time at this particular condition is closer to the published value than
Track A's, but that is not evidence that Track B is the better implementation. Its response
times are wildly dispersed across the sweep (median 0.20 s, mean 0.81 s, sd 1.23 s, range 0
to 7.0 s over 136 runs that braked at all), so matching at one condition is close to
coincidence. It also brakes much harder than the paper reports and collides in 34% of all
runs. Dispersion, not central tendency, is what is wrong with it.

The two discrepancies in Track A have a common and identified cause: `find_parameters`
saturates for this condition and returns `a_tar_min = −8 m/s²`, the most pessimistic possible
assumption about how hard the lead vehicle might brake (details in `03_replication.md` §Track
A). A more pessimistic assumption makes the model react earlier *and* prefer swerving, which
is exactly the pattern observed. This is a limitation of the released calibration table, not
of the model.

## 1b. The second case — front-to-rear, v0 = 25 m/s, time gap 1.0 s (Fig. 3b)

This is the paper's *brake-and-swerve* case, and it is the sharper test: at Fig. 3a the paper
brakes only, so Track A's swerving looked like a discrepancy. Here the paper swerves too, so
agreement or disagreement is informative rather than confounded.

| quantity | **paper (Fig. 3b)** | **Track A** (2 runs) |
|---|---|---|
| lead vehicle brakes at | 0.8 s | 0.8 s |
| model perceives braking | ~1.0 s (delay ~0.2 s) | — (not directly observable) |
| first re-plan | 1.4 s | — |
| first observable response | ~1.4–1.6 s | **1.6 s** |
| **response time** | **~0.6–0.8 s** | **0.80 s and 0.83 s** |
| maneuver | **brake + steer into adjacent lane** | **brake + swerve**, lateral 3.16 m and 4.22 m |
| braking | present | light (−1.1 and −0.9 m/s² over the first second) |

**Track A reproduces this case well.** The response time matches, and the maneuver is the
lane-change-plus-braking the paper describes; a lateral displacement of 3.2–4.2 m against a
3.65 m lane width is a completed lane change. The braking component is weaker than the paper's,
though the run was truncated at 3.4 s to fit the compute budget, so later braking is not
captured.

**Why this matters for the Fig. 3a discrepancy.** Track A responds early and swerves at *both*
conditions. At Fig. 3b that is correct behavior; at Fig. 3a it is not, because the paper brakes
only there. That asymmetry is exactly what the saturated `a_tar_min = −8 m/s²` calibration
predicts: a model that assumes the lead vehicle might brake maximally is biased toward earlier
and more evasive responses, which is harmless when swerving is the right answer and wrong when
it is not. It is evidence for the diagnosis in `03_replication.md` rather than a second,
separate discrepancy.

Cost note: 644 s for 18 timesteps at batch 2, i.e. roughly 18 s per simulated step per run.

## 2. Relations across the sweep (Track B)

The paper's Figs. 3c-3e assert *relations* rather than point values, and those are the more
meaningful test of whether an implementation behaves like the original. Track B was run over
the paper's own grid — 7 time gaps x 4 speeds x 5 repeats = 140 simulations, 33 min on CPU
(`replication/sweep_aidriver.csv`, figure `figures/validation_rear_end.png`).

| claim in the paper | our result | verdict |
|---|---|---|
| braking preferred at low speeds, swerving at high speeds | P(brake only) = 60-100% at 10 and 15 m/s, 0-20% at 25 and 35 m/s | **reproduced** |
| deceleration magnitude increases with inverse TTC at brake onset | r = -0.271, slope -0.81 m/s^2 per s^-1 | **reproduced in direction** |
| response time increases approximately linearly with time gap | r = +0.159; mean 0.60 s for gaps <= 1.5 s, 0.87 s for gaps >= 3.0 s | **direction only** — weak and non-monotone |
| response time ~1 s and roughly flat for gaps 0.5-1.5 s | ours 0.60 s, and not flat | **not reproduced** |
| at 15 m/s, P(brake only) increases with time gap | 80, 60, 20, 80, 60, 80, 80% — no trend | **not reproduced** |
| collisions occur only at the shortest time gap (0.5 s) | 10-65% at *every* gap; 50% at 0.5 s, 65% at 1.0 s, 30% at 3.5 s | **not reproduced** |

Mean brake response time [s], rows = initial time gap, columns = v0:

| gap | 10 m/s | 15 m/s | 25 m/s | 35 m/s |
|---|---|---|---|---|
| 0.5 s | 0.10 | 0.52 | 0.05 | 0.88 |
| 1.0 s | 0.40 | 0.32 | 0.50 | 0.24 |
| 1.5 s | 0.84 | 1.00 | 0.85 | 1.32 |
| 2.0 s | 0.32 | 0.64 | 1.64 | 0.92 |
| 2.5 s | 0.12 | 0.36 | 1.04 | 3.48 |
| 3.0 s | 0.12 | 0.48 | 0.60 | 1.44 |
| 3.5 s | 1.04 | 0.48 | 1.16 | 1.60 |

**Reading.** Two of the six relations come out of the model, and they are the two that rest on
the *preference function* rather than on response timing. Maneuver choice follows speed because
harsh braking becomes expensive relative to a lane change as speed rises, and braking magnitude
scales with urgency because the collision term grows faster than the control-effort term. Both
parts were verified against the Supplementary Information, which is consistent with them
working.

The four that fail all depend on the *evidence-accumulation timing*, which is exactly the stage
diagnosed as defective in `03_replication.md`. The collision rate is the clearest symptom:
10-65% across all conditions against the paper's "only at 0.5 s". Note that a model responding
within 0.0-0.4 s should collide *less* often than one that waits 1.4 s, so the high collision
rate is not caused by responding late. It is caused by responding to the wrong thing, under a
policy that the inflated surprise signal keeps forcing the model to re-plan.

One detail visible in panel (c) of the figure is worth recording: most brake onsets occur at an
inverse TTC of approximately zero, meaning the model brakes before any closing speed has
developed. In the paper the same plot spans a range of inverse TTC values. This is the
premature-response problem seen from another angle.

## 2b. Validation of the surprise measures (Dinparastdjadid et al. 2023)

The collision-avoidance model is not the only published claim this repository can check. The
two measures introduced in *Measuring surprise in the wild* are claimed to have properties that
surprisal and Bayesian surprise lack, and those claims are testable directly.

**Property tests** (`tests/test_surprise.py`, 31 assertions, all passing) confirm the claims
analytically:

| claim | test result |
|---|---|
| residual information is zero at the mode | 0.000 exactly, Gaussian and categorical |
| surprisal is *not* zero at the mode | 1.27 at the mode of N(0, 2) — the zero-floor problem |
| residual information is invariant to bin size | identical to 12 decimal places for eps from 1e-1 to 1e-4 |
| surprisal diverges as bin size goes to zero | 4.35 → 11.25 over the same range |
| S8 collapses as bin size goes to zero | 0.0384 → 0.000039 |
| S_SPE = 1 − exp(−S_Shannon) (Modirshanechi Prop. 3) | holds exactly |
| antithesis silences mode-narrowing | 0.0000 against KL 0.3167 |
| antithesis silences mode-removal | 0.2216 against KL 0.6926 |
| antithesis fires on genuine surprise | 6.40, i.e. > 10^9 times its mode-narrowing value, where KL separates the two cases by a factor of only 20 |

**On a simulated prediction stream** (`demo_surprise.py`, a lateral cut-in with a two-component
GMM predictor) the practical consequence is visible in how often each measure is silent:

| measure | min | max | fraction exactly zero |
|---|---|---|---|
| surprisal | 0.003 | 12.87 | **0.00** |
| residual information | 0.000 | 12.86 | **0.24** |
| Bayesian surprise (KL) | 0.511 | 16.11 | **0.00** |
| antithesis | 0.000 | 16.13 | **0.79** |

Bayesian surprise never falls below 0.511 even during entirely uneventful driving, which is
exactly the objection the paper raises against it: the posterior is formed with extra
information, so uncertainty shrinks and KL stays positive whether or not anything surprising
happened. Antithesis is silent 79% of the time on the same stream. That is the discriminative
power the measure exists to provide, and it is reproduced here.

One implementation caveat found while doing this: residual information needs `max_x p(x)`, and
for a Gaussian *mixture* the mode is not available in closed form. Taking the best component
mean under-estimates the true maximum for overlapping components, which made residual
information dip slightly *below* zero — breaking the very property it exists to provide. The
`GaussianMixture` class therefore refines the mode on a local grid by default in one and two
dimensions (`mode_refine`), after which the minimum over the stream is 0.000 as it should be.

## 3. What the comparison can and cannot establish

**Can.** Whether the mechanisms produce the *qualitative dependencies* the paper claims —
kinematics-dependent response timing, urgency-dependent braking magnitude, speed-dependent
maneuver choice. These are the model's substantive predictions and they do not depend on
exact parameter values.

**Cannot, without more work.** Whether the model matches *human* data. The paper's own
comparisons are against a meta-analysis of brake response times (its ref. 57) and the SHRP2 /
ANNEXT deceleration analysis (ref. 14), for which we have neither the underlying data nor the
regression coefficients. What we can check is our results against *the paper's model results*,
which is a replication check, not a validation against humans. That distinction is worth
keeping sharp: nothing in this repository has been compared with human behavior.

## 4. Fit metrics used by the paper, and why we do not report them

The paper quantifies fit with mean absolute error via Bayesian linear regression on residuals
(response times, decelerations), Jensen–Shannon divergence for categorical outcome
distributions, Wasserstein distance for response-time distributions, bootstrap with 10 000
resamples, and a signal-to-noise ratio > 3 as the significance heuristic.

We do not reproduce these because they compare model output against *human* datasets we do
not have. They become available the moment the human data does. What *was* available is the
OSF deposit (`osf.io/gs4bu`) with the paper's own simulation output; §4b compares against it
at the distribution level, replacing the figure-read numbers this section previously had to
lean on.

## 4b. Distribution-level comparison against the OSF deposit (added 2026-08-20)

The deposit (`external/gs4bu-osfstorage-archive/`) holds per-run output for all three
scenarios: setups, outcome analysis, and per-timestep pickles (states, observations, beliefs,
particle weights, planned policies, pragmatic-value components). The rear-end scenario has
224 runs of 32 seeds each — 28 baseline conditions plus seven ablations of the same grid.
`replication/validate_osf.py` extracts the 28 baseline conditions (896 trials); outputs are
under `replication/osf/`. One erratum worth recording: the deposit README gives the policy
arrays as (H, seeds, timesteps, 2), but the arrays are (H, timesteps, seeds, 2) — `eta`
fixes seeds = 32 and timesteps = 60, which disambiguates.

**Their response-time distribution, finally at distribution level.** Executed-braking onset
(first planned-and-executed deceleration ≤ −1 m/s² after lead onset): median **1.20 s**,
sd **0.66 s**, IQR 0.80–1.80 s. Re-plan onset (policy departs from the reference policy,
i.e. the model's own E ≥ 1 event): median 0.80 s, sd 0.47 s. Response time rises with speed
(median 1.0 s at 10 m/s to 1.8 s at 25 m/s). Against that target:

| | median RT | sd | overall collision rate |
|---|---|---|---|
| authors' runs (OSF, 28 conditions × 32 seeds) | 1.20 s | 0.66 s | 7.3% |
| Track A (2 conditions) | 0.80 / 0.92 s | — | 0% |
| Track B sweep (140 runs) | 0.20 s | 1.23 s | 33.6% |

Track A's two response times sit inside the authors' IQR. Track B's defect is now quantified
against the real target rather than against figure-read values: the median is 1.0 s too
early, the dispersion roughly double, and the collision rate 4.6× theirs (per-condition
collision-rate correlation 0.40). This sharpens, but does not change, the diagnosis in
`03_replication.md`.

**The comfort-zone calibration pipeline runs end to end on their trajectories.** Using only
the recorded kinematics (`eta`) and the preference function — no model roll-out — `eps(t)`
was computed for all 896 trials and `calibrate_level` fitted the boundary level to the
model's own brake onsets: onset-matching score **0.855**, and at the fitted level the onset
error is **median 0.0 s, IQR 0.2 s** (771 of 896 trials matched within the ±0.6 s
tolerance). The reference model's decisions to act are recoverable from a level set of the
field evaluated on what happened — which is precisely the mechanism the method in
`04_comfort_zone_method.md` claims, demonstrated on the reference implementation rather than
on our own agent.

Two qualifications. First, these onsets are the *model's*, not humans'; this validates the
pipeline and the field's behavior on reference trajectories, not the empirical claim. Second,
the fitted level is weakly identified: a within-scenario transfer check (fit on low speeds,
evaluate on high, and reverse) transfers well in one direction (score 0.916, identical to the
held-out optimum) but the two directions prefer levels of 0.87 and 64 with similar scores —
the field rises so steeply at the boundary (the safety-term step) that the score curve is
flat in `c` over orders of magnitude. For the rear-end scenario the *location* of the
boundary is robust and the *level* is not a sensitive quantity; whether that holds in
scenarios where the field rises gradually (lateral clearance) is exactly what the
cross-scenario test will show.

Incidental but pleasing: the shortest-gap condition (25 m/s, THW 0.668 s) starts 11 cm
inside the closed-form dread boundary (THW* = 0.672 s), and in the authors' own runs the
model refuses the condition — 72% of seeds leave the road before the lead ever brakes, and
9.4% collide. The static boundary and the reference implementation agree that the state is
untenable.

Not yet used from the deposit: the `Results_oncoming` and `Results_intersection` folders
(the faithful scenario definitions our `LateralIncursionScenario` lacks are implicit in
their `eta` histories), the seven ablation grids, and the per-timestep pragmatic-value
components `v` (comparing them term-by-term against our preference function requires
reproducing their belief roll-out, not just the kinematics).

## 5. Scenarios not attempted

**Lateral incursion.** The paper reports collision rates of **82.3%** (medium incursion) and
**6.3%** (shallow), dropping to 51.6% / 3.1% when the number of evaluated policies is
increased tenfold; and human response times of **3.5–4.5 s**. We have a
`LateralIncursionScenario` implemented but it is not set up faithfully — the paper uses a
300 m initial separation, v₀ = 17.88 m/s (40 mph), a turn triggered when TTC falls below
5.15 s, lasting 3.3 s, in three variants (steep / medium / shallow, defined by the oncoming
vehicle's final lateral position). Running our version and reporting a collision rate against
82.3% would mostly measure the difference between the two scenario definitions plus Track B's
known closed-loop problems, which would be misleading rather than informative.

**Intersection (right-turn-into-path).** Not attempted. This is the paper's *held-out*
generalization test, and it is the most interesting one to reproduce precisely because the
parameters were not tuned on it — but it needs a third scenario implementation and the
Ziraldo et al. human data for comparison.

## 6. Honest summary

| | reproduced | partially | not reproduced / not attempted |
|---|---|---|---|
| **Track A** | architecture runs end to end; **Fig. 3b case in full** (response time 0.80 s vs ~0.6–0.8 s, brake + swerve) | Fig. 3a case: response time 0.92 s vs 1.4 s, swerves where the paper brakes | full sweep; lateral incursion; intersection; ablations |
| **Track B** | preference function (verified against SI); belief tracking; surprise zero-floor; static comfort-zone boundary; **maneuver choice vs speed**; **braking magnitude vs urgency** | response time vs time gap (direction only) | response time magnitude; collision rates; maneuver choice vs time gap; lateral incursion; intersection |

Two numbers to carry forward. **Track A reproduces the Fig. 3b case (0.80 s against ~0.6–0.8 s,
with the correct brake-and-swerve maneuver) but gives 0.92 s against 1.4 s at Fig. 3a, where it
also swerves though the paper brakes.** Reproducing one condition and not the other, in the
direction a more pessimistic `a_tar_min` predicts, is stronger support for the calibration
diagnosis than either result alone would be, and it is fixable by regenerating the
free-following calibration over the paper's actual parameter range. **Track B reproduces 2 of the 6 published relations** — the two that rest on the
preference function rather than on response timing — which localizes its remaining defect to
the evidence-accumulation stage instead of leaving it as a general "does not work".

That split matters for the comfort-zone work: the method in `04_comfort_zone_method.md` depends
on the preference function and the static field, both of which fall in the reproduced column.
