# Chapter 10: calibration and parameter fitting — how the numbers get their values

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-23. Provenance tags
as in chapter 0. Added after review discussion: chapters 07 and 09 say the model's
"normal" can be changed; this chapter covers the discipline behind setting or changing any
number in it — where the published values came from, how new values should be obtained,
and the dos and don'ts of fitting a model with this much flexibility.*

## Three ways a number gets into the model — fitting is only one of them

A natural first assumption is that a model like this is "fitted to data" the way a
regression is. It is not, and the distinction matters for anyone planning to change it.
Every number in the model arrived by one of three routes, and each route carries its own
obligations when you replace the number:

1. **Specified** — taken from physics, geometry, or an independent literature. Vehicle
   dimensions, maximum braking, the timestep; the looming detection threshold comes from
   the psychophysics literature, not from fitting [SI]. Obligation when changing:
   cite the independent source, or admit the number has become a fitted one.
2. **Calibrated on normal driving** — set so that *everyday* behavior comes out right,
   then left alone when conflicts are simulated. The flagship example is below.
   Obligation: the calibration data must be separate from the evaluation data, and the
   calibration must *cover* the conditions you will run.
3. **Tuned** — thirteen parameters were adjusted by hand until behavior looked human at
   the qualitative level [Paper]. Honest, but the route with the least protection
   against fooling yourself. Obligation: whatever was tuned must face validation it was
   not tuned toward — which is exactly the role of the held-out intersection scenario.

To answer the direct question this chapter exists for: changing the normative part is
**not** only a matter of data fitting. The preference structure and norm geometry can be
changed by hypothesis (a trusting driver, a wider normal region) with the boundary
consequences computed rather than fitted (chapter 07); they can be re-calibrated on
normal-driving data; or — the [Speculation] route we develop below — they can be learned
from observed traffic. What they cannot credibly be is tuned freely against the same
critical events one then claims the model explains (chapter 01's flexibility worry, made
operational).

## The calibration exemplar, worth copying: the free-following lookup

The single most consequential preference parameter — the assumed worst-case deceleration
of the other vehicle, which sets where the safety margin sits (chapter 07) — is neither
specified nor tuned. It is calibrated, and the mechanism deserves to be understood
because it is the pattern any extension should copy [Code, `find_parameters` in
`src/utils/simulation.py`; SI]:

1. Run (once) a large grid of *free-following* simulations — no conflict, just steady
   car-following — across speeds, accumulator rates, and candidate worst-case
   assumptions, recording the steady headway each combination settles into.
2. Invert the table: given a speed and a desired everyday headway, look up (with
   interpolation) the worst-case assumption that *produces* it.
3. Use that value, unchanged, when simulating conflicts.

The logic is quietly elegant: the paranoia parameter is disciplined by ordinary
behavior. A driver who assumed worse would follow further back *all the time*; observed
comfortable headways therefore pin down the assumption without touching any conflict
data. Calibrate on the quiet regime, predict the loud one — the same separation chapter
05 describes behaviorally, used as an inference principle.

{{R2}}Two further provenance routes earned their place in the crash-causation study
(2026-08-25). **Digitized** — a distribution extracted from a published figure when the
underlying data are unshareable; legitimate only with an independent cross-check, and the
study's two are the pattern: the glance histogram's value axis was calibrated by tick
geometry *and* by the requirement that the drawn distribution sum to one (they agreed
within 0.9%), and the deceleration counts had to sum to the paper's stated n = 45
exactly, or the extraction script fails (`replication/causation/digitize_b24.py`).
**Arbitrated** — a *convention* (not a parameter) that the model itself can decide when
the full implementation is consulted: the accumulator's starting level was resolved by
running the closed loop rather than by fitting or by argument, and the losing convention
stays in the outputs as a tested sensitivity. Conventions resolved by arbitration should
be so labeled, with the arbitration's scope stated — this one holds for windows opening
near the conflict, and says nothing about long run-ins.

{{R1}}The cautionary half of the story is ours: the shipped lookup table covers steady-state
headways only up to about 1.0–2.1 s depending on speed, and outside that range the
interpolation clamps to the table edge — the parameter silently saturates at its most
pessimistic value, −8 m/s², for most of the paper's own rear-end conditions
(`docs/method_review.md` §6.2). The authors' published runs carry the same saturation;
an earlier draft of this chapter blamed it for a replication discrepancy that turned out
not to exist. The lesson still generalizes: **a calibration is only as good as its
coverage**, and coverage failures do not announce themselves — the model still runs, just
not the way its documentation says. Checking that a calibration table brackets every
condition you intend to simulate is a one-line assertion. A second lesson from the same
episode: **the calibration is only exercised if the simulation gives it time** — with the
lead braking 0.6 s into the run and the driver following a fixed reference plan until its
first re-plan, the "stable following" the table was built to produce never occurs in the
published runs.

## Identifiability: the central danger of fitting this model

The model's parameters do not map one-to-one onto observables. Several knobs move the
same behavioral output, which means a good fit does not tell you which knob was
responsible — and a fitted value can be badly wrong while the fit looks fine:

| Observable | Moved by (at least) |
|---|---|
| Response time | accumulator rate λ, looming threshold, perception noise, prediction noise, norm trust |
| Boundary location / accepted headway | assumed worst-case braking **and** reaction-time budget (chapter 07 shows both, with numbers) |
| Maneuver choice vs speed | steering-effort tolerance, lane costs, collision severity scaling |
| "Cautiousness" overall | collision cost, severity floor, safety-margin assumptions — jointly |

This project has a live demonstration of the phenomenon: fitting the comfort-zone level
c to the reference model's own onsets gave a boundary whose *location* was recovered
with zero median error while the *level itself* was indeterminate over orders of
magnitude, because the field rises so steeply that many levels tell the same story
(`notes/05_validation.md` §4b). The fit succeeded; the parameter was still not
identified. Expect the same everywhere in this model.

The defenses are standard but non-optional:

- **Fix everything you can by routes 1 and 2** before fitting anything by route 3; every
  parameter removed from the fit is a confound removed from the interpretation.
- **Fit the smallest subset that your hypothesis is about**, holding the rest at
  reference values — and say so.
- **Probe the objective around the optimum.** If a parameter can move substantially with
  little cost to the fit (as c above), report the range, not the point; a flat direction
  is a finding about the model, not an inconvenience.
- **Prefer observables that separate the knobs.** Response time alone cannot distinguish
  λ from perception noise; response time *as a function of condition* (urgency, speed,
  visibility) begins to, because the knobs bend that curve differently. Distributions
  beat means for the same reason.

## The mechanics: how fitting actually proceeds here

There is no formula linking parameters to data — the model is a simulator, so fitting
means comparing simulated and observed behavior and searching. Three practical
consequences [Paper] [OSF]:

- **Fit summaries, not trajectories.** The paper's own comparisons use response-time
  distributions per condition, maneuver-choice proportions, and deceleration profiles,
  with distribution distances (Jensen–Shannon, Wasserstein) and regression-based error
  bands as the yardsticks. Any refit should use the same summaries first, so results
  stay comparable.
- **Respect the noise floor.** Each condition was run with 32 random seeds, and
  seed-to-seed spread is substantial; a fit that chases differences smaller than the
  seed spread is fitting noise. Simulate enough seeds to know the model's own
  variability before crediting a parameter change with an improvement.
- **Be static wherever possible.** Closed-loop simulation costs ~18 s of CPU per
  timestep here, which makes naive search infeasible. The division of labor from
  chapter 09 applies to fitting too: preference and boundary parameters can be fitted
  *statically* against recorded kinematics in milliseconds (`calibrate_level` is exactly
  such a fit); only timing-and-prediction parameters (λ, noise scales, norm trust)
  genuinely require the loop — and for those, the deposit's precomputed grids [OSF] and
  coarse-to-fine searches are the difference between a week and a year.

## Learning the norms from data

*This section is [Speculation]: our proposed procedure, not published work.*

The norm geometries of chapters 06–07 are hand-drawn. Nothing prevents estimating them
instead, and the structure of the code makes the replacement surgical (one function per
scenario). The procedure we would try:

1. **Collect** the other-agent states observed in ordinary traffic for the scenario —
   lateral positions and speeds of leads, of oncoming vehicles, of turners at the
   junction type in question. Drone datasets are well suited: large N, exact kinematics,
   no interaction with an instrumented vehicle.
2. **Estimate the density** of those states, per context, and **map density to
   compliance weight**: full weight in the high-density core, dropping toward the
   observed tails — while *keeping a hard floor* like the code's existing small factors.
   The floor is not a technicality: it is what keeps physically possible but never-yet-
   observed behavior inside the prediction fan, and deleting it would rebuild the
   oblivious-driver failure the norms exist to prevent.
3. **Validate by coverage, not by fit.** A norm set is good if the prediction fans it
   produces are *calibrated*: actual next-seconds behavior of other agents should look
   statistically like draws from the fan — rare events falling outside at about the
   advertised rate. This can be checked on held-out trajectories without running the
   full driver model, which keeps the exercise cheap.

Done this way, "normative driving" for a new scenario becomes an estimation problem with
a defined data requirement, rather than an act of judgment — with the judgment surviving
only in the floor factors and the context definition, where it belongs and can be
argued about explicitly.

## Fitting individuals

The parameters were designed as one driver; the research value for this audience is in
letting them vary. Two disciplines from the general fitting literature transfer directly
[Speculation as applied here]: fit *few* parameters per person (one or two preference
knobs; everything else population-level), and pool across drivers (a hierarchical
structure, even informally: individual estimates shrunk toward the population) so that
ten-ish events per driver — the realistic naturalistic budget
(`docs/data_requirements.pdf`) — yield stable estimates. The sharpest question this
opens is the one chapter 11's transfer test asks at the population level, asked per
person: is a driver's fitted comfort level *theirs* — stable across scenarios — or a
property of the situation? Either answer is a result.

## Dos and don'ts, collected

**Do**

- Fix by physics and literature first; calibrate on normal driving second; fit last,
  and least.
- Check calibration coverage against every condition you will run, mechanically.
- Fit distributions per condition, never grand means; simulate enough seeds to know the
  model's own spread first.
- Keep the fitted-on data and the validated-on data disjoint, and keep one scenario
  untouched end to end — the held-out discipline is the model line's own best habit.
- Re-run the ablation for any mechanism whose parameters you refit (chapter 09, rung 2):
  a refit can quietly transfer a job from one mechanism to another.
- Record complete parameter sets with every result, the way the `Setups` tables do —
  including which route (specified / calibrated / tuned / fitted) each value came by.
- Report flat directions and ranges; treat weak identification as a finding.

**Don't**

- Don't hand-tune against the data you will call validation — with this many degrees of
  freedom the fit will succeed and mean nothing.
- Don't fit λ and perception noise jointly from response times alone; they are not
  separable there (use condition structure, or fix one independently).
- Don't quote absolute boundary or headway values without the assumptions they inherit
  (chapter 07; `HANDOFF.md` §7).
- Don't delete the norm floors when estimating norms from data — the tail is the safety
  case.
- Don't let calibration tables or fitted values live outside version control and the
  parameter record; a number whose provenance is lost reverts to "tuned".

---

## Notes for the mathematically curious

**Level 1 — the fitting problem stated.** With simulator M(θ) mapping parameters to
behavior distributions and observed summaries s_obs, fitting is
argmin_θ D(s(M(θ)), s_obs) for a chosen distance D over chosen summaries s — a
simulation-based (likelihood-free) inference problem. Identifiability is the geometry of
D around the optimum: flat valleys are unidentified parameter combinations. The static
shortcut works whenever s depends on θ only through the preference field ε(·; θ)
evaluated on fixed kinematics — then the simulator drops out and the search is direct.

**Level 2 — specifics.** The free-following lookup: `find_parameters(v_tar, EA_fac,
noise_pred_fac, H, d_phi_thres, THW_des)` multi-linearly interpolates a pre-run grid
(`Analysis_following.xlsx`) to return the `a_tar_min` (and residual speed offset)
consistent with the desired steady headway; the returned value is clamped at the grid
edge — the coverage failure mode above [Code]. The paper's comparison metrics: MAE with
bootstrapped uncertainty via Bayesian linear regression on residuals,
Jensen–Shannon divergence for categorical outcomes, Wasserstein distance for
response-time distributions, with a signal-to-noise criterion for reporting [Paper]
(`notes/05_validation.md` §4). The comfort-zone level fit (`calibrate_level`) maximizes
an F1-style onset-matching score over c with a timing tolerance; its flat-maximum
behavior on steep fields is documented in `notes/05_validation.md` §4b. For norm
estimation, the coverage check in step 3 is a probability-integral-transform-style
calibration test of the prediction fan on held-out segments.
