# Replication of Schumann et al. (2026) — status report

Two independent tracks were run:

**Track A — the authors' own code.** Cloned, patched to run on CPU, executed on the
front-to-rear scenario. This is the actual replication.
**Track B — an independent NumPy re-implementation** (`src/aidriver/`), written to make each
mechanism inspectable and to support the comfort-zone work.

Bottom line: Track A runs and reproduces the qualitative result with a brake response time
of **0.92 s** against the paper's **1.4 s** for the same condition; the discrepancy traces to
a calibration table shipped with the code that does not cover the paper's operating range.
Track B reproduces the mechanisms and the static preference function faithfully (verified
against the Supplementary Information) but its closed-loop response timing is **not** yet
quantitative — diagnosis below.

---

## Track A — running the authors' code

**Source.** `github.com/tud-hri/Active-Inference-Collision-Avoidance`
(Zenodo `10.5281/zenodo.20049511`), cloned to `external/aica/`. Non-commercial license that
explicitly permits research use and benchmarking. ~22 kLOC, PyTorch, written for GPU.

**Three obstacles, and what was done about them:**

1. **Hardcoded CUDA device.** `src/common/bicycle.py:42` created a tensor with
   `device='cuda'` unconditionally, so the model cannot start on a CPU-only machine. Patched
   to fall back to CPU when CUDA is absent; GPU behavior is unchanged. This is the only
   modification made to the authors' code — see `replication/PATCHES.md`.
2. **Unguarded module-level imports.** `simulation_rear_end.py` ends with
   `import Analysis_rear_end` / `import visualization_rear_end` *outside* the
   `if __name__ == "__main__"` guard, and those modules immediately read result files that do
   not exist until after a full sweep. `replication/run_rear_end_single.py` therefore loads
   the authors' source up to the `__main__` guard and executes only that, giving access to
   `set_config` and `simulate` with the code otherwise untouched.
3. **Scale.** The shipped script sweeps 7 time gaps × 4 speeds × 128 ablation combinations ×
   32 repeats. `run_rear_end_single.py` runs one initial condition, which is what makes the
   model tractable here at all: **117 minutes for 50 timesteps × 4 parallel runs on CPU.**

**Result** (`v0 = 15 m/s`, 1.5 s time gap — the paper's Fig. 3a condition;
`figures/replication_rear_end.png`):

| run | lead brakes | ego brake onset | response time | decel | max lateral | outcome |
|---|---|---|---|---|---|---|
| 0 | 0.8 s | 1.8 s | **1.04 s** | −3.4 m/s² | 3.68 m | swerve + brake |
| 1 | 0.8 s | 1.6 s | **0.80 s** | −4.5 m/s² | 4.30 m | swerve + brake |
| 2 | 0.8 s | 1.8 s | **1.04 s** | −3.1 m/s² | 4.11 m | swerve + brake |
| 3 | 0.8 s | 1.6 s | **0.80 s** | −4.7 m/s² | 0.28 m | brake only |
| | | | mean **0.92 s** | | | |

The paper reports 1.4 s for this condition, and Fig. 3a shows braking-*only* avoidance.

A second condition was subsequently run — **v0 = 25 m/s, 1.0 s time gap, the paper's Fig. 3b
brake-and-swerve case** (18 timesteps, batch 2, 644 s):

| run | lead brakes | first response | response time | maneuver | lateral |
|---|---|---|---|---|---|
| 0 | 0.8 s | 1.6 s | **0.80 s** | brake + swerve | 3.16 m |
| 1 | 0.8 s | 1.6 s | **0.83 s** | brake + swerve | 4.22 m |

The paper's Fig. 3b has the model perceiving the braking at ~1.0 s and re-planning at 1.4 s,
so its response time is roughly 0.6–0.8 s. **Track A matches this condition**, in both timing
and maneuver. Since Track A responds early and swerves at *both* conditions, and swerving is
correct at Fig. 3b but not at Fig. 3a, the pattern is what a saturated (over-pessimistic)
`a_tar_min` predicts — which strengthens the diagnosis below rather than adding a second,
independent discrepancy.

**What is reproduced:** the architecture runs end to end; the model perceives the braking with
a delay, accumulates evidence, re-plans, and executes a coordinated avoidance maneuver. The
response is clearly *not* instantaneous, which is the mechanism the paper is arguing for.

**What is not, and why.** Two related causes, both traceable to the released artifacts:

- **The shipped calibration table does not cover the paper's operating range.**
  `Results_following/Analysis_following.xlsx` is a coarse grid: speeds {10, 20, 30} m/s,
  `EA_fac` {−6.0, −5.8, −5.6}, `looming_threshold` {0.002}, `noise_pred_fac` {0.02, 0.05},
  `H` {20, 30}. The main experiments use `looming_threshold = 0.00215` and
  `noise_pred_fac = 0.2`, both of which `find_parameters` silently **clips** to the table's
  range. More importantly the table's THW values top out around 1.3 s, while the paper's
  sweep runs to 3.5 s, so for our condition (THW ≈ 1.78 s) the interpolation saturates and
  returns `a_tar_min = −8 m/s²` — the most pessimistic possible assumption about the lead
  vehicle's braking.
- **A more pessimistic `a_tar_min` makes the model react earlier and swerve.** That is
  consistent with what we see: shorter response time than the paper and lateral avoidance in
  3 of 4 runs. Regenerating the free-following calibration (`simulation_*` in the repo)
  across the paper's actual parameter range would be the way to close this, and is a
  multi-day GPU job rather than something achievable here.

Also worth recording: `find_parameters` **always returns `v_diff = 0`** (it is hardcoded in
the `return` statement), so the `v_diff` interpolation machinery above it is dead code.

### Practical notes for re-running Track A

Cost is the binding constraint: roughly **18 s of CPU per simulated timestep per parallel run**
(644 s for 18 steps at batch 2; 117 min for 50 steps at batch 4). A 10-second scenario is
therefore a two-hour job, and long background jobs in this environment were repeatedly
terminated before finishing — three attempts died at 29/50, 2/32 and 2/18 steps.

Two changes make that survivable, and both are worth keeping:

- **Checkpointing.** `run_rear_end_single.py` substitutes a version of the authors'
  `run_simulation` that writes a `.partial` pickle every N steps (`--checkpoint-every`, default
  5). The authors' own loop accumulates everything in memory and returns only at the end, so an
  interrupted run leaves nothing — one attempt reached 29/50 steps and saved nothing, even
  though the brake response being measured had already occurred by step 15. The substitution is
  made at runtime through the module namespace, so their code is still unmodified.
  `replication/validate.py` reads `.partial` files when no completed run exists for that
  condition.
- **Size the run to the question.** Response times are measured relative to the lead vehicle's
  braking onset, so the scenario does not need to play out to completion. 18 timesteps (3.6 s)
  is enough to capture brake onset and the start of a lane change, which is what the Fig. 3b
  comparison needs, and it completes in 11 minutes instead of two hours.

The equivalent for Track B (`sweep_rear_end_aidriver.py`) appends and fsyncs each row as it
completes and skips conditions already present in the output, so an interrupted sweep can be
restarted with the same command.

---

## Track B — independent re-implementation (`src/aidriver/`)

Written from the article plus the Supplementary Information, in NumPy, ~700 lines total.
Purpose: make every mechanism a single readable function, so it can be ablated and so the
preference function can be reused for comfort-zone work without carrying a GPU dependency.

**Getting the Supplementary Information mattered enormously.** The article's Eq. 11 lists the
preference factors by name only. SI §2.4 (Eqs. 44–52) gives the functional forms, and two of
them are impossible to guess:

- `p_lat` is a **triangular** function — log-linear from 0 at the lane center down to `g_LC`
  at the lane edge, then flat at `g_LL` — and `y_rel` is *lane structured*, so the center of
  the adjacent lane is also cost-free in a same-direction two-lane scenario.
- `p_coll` is not only a collision cost. With no collision and a vehicle ahead it is a
  Gaussian preference over **inverse tau** (`tau⁻¹ = φ̇/φ ~ N(0.2, 0.125) s⁻¹`, i.e. a
  preferred TTC of about 5 s). This is the term that shapes ordinary car following. Before
  adding it, the model had no gradient pulling it toward a comfortable following distance
  and only reacted once a collision was actually predicted.
- `p_coll` is also a **running minimum** over the horizon (SI Eq. 47), so a collision keeps
  being punished for the rest of the rollout.
- `p_safe` is an **indicator**, not a smooth penalty: it fires exactly when the required
  deceleration `a_ego,req` exceeds `a_max`.

Note a discrepancy between the two documents: the SI gives `g_LL = −5000`, Table 1 of the
article gives `−15000`. We follow the SI.

### What Track B reproduces

- Looming perception with the `φ̇₀ = 0.00215 rad/s` threshold, giving distance-dependent
  uncertainty for free.
- A particle filter that **tracks the lead vehicle correctly**: inferred acceleration settles
  within ~0.3 m/s² of the true −6 m/s² about one timestep after braking begins.
- Norm-conditioned prediction with the current-compliance upper bound.
- Surprise accumulation with the correct zero floor, pedal constraints, CEM planning.
- The preference function, verified against the SI: cost exactly 0 at the lane center and at
  the adjacent lane center, `g_LC` at the lane edge, `g_LL` off-road; deficit exactly 0 in
  free driving; a constant `τ⁻¹` residual of 1.28 when a vehicle is ahead; the safety
  indicator switching at THW ≈ 0.73 s for 15 m/s.
- **26/26 tests pass** (`tests/test_comfortzone.py`), including an independent cross-check
  that the closed-form comfort-zone boundary equals the numeric level set of the field
  (agreement to 0.000 m over 45 speeds).

### What Track B does *not* reproduce, and the diagnosis

**Response timing is far too variable**, and collision rates are far too high. Over the full
28-condition sweep (140 runs) the brake response time has median 0.20 s, mean 0.81 s and
standard deviation 1.23 s, spanning 0 to 7.0 s; the model collides in 34% of runs, at every
time gap, against the paper's "only at the shortest time gap". At the single reference
condition (v0 = 15 m/s, gap 1.5 s) the mean response time is 1.00 s, which is close to the
published 1.4 s — but with that dispersion, agreement at one condition carries little weight.
An earlier note in this file described the timing as uniformly "far too fast"; the sweep shows
the real problem is dispersion rather than a constant bias.

The cause is that the surprise signal `ε_t` in the *closed loop* sits around 10⁵ during
ostensibly comfortable driving, so accumulated evidence is always near threshold and the
delay mechanism never gets to do its job. Note that this is specifically a closed-loop
effect: evaluated on a *fixed* coasting policy at the same state, `ε` is about **41**, which
is small and correct. The gap between those two numbers is the whole problem, and it is
dominated by the control-effort term (`σ_a = 0.1 m/s²` means a sampled acceleration of
1.5 m/s² costs ~112 log units per timestep) applied to CEM policies that are not smooth.

Things tried that did **not** fix it: raising the CEM budget from 100×8 to 300×20 (behavior
stayed seed-dependent, so this is not a search-budget problem); warm-starting the re-plan
from the shifted previous policy. Things that produced large genuine improvements along the
way, each of which was a real bug:

| symptom | cause | fix |
|---|---|---|
| belief collapsed to one particle with a wrong acceleration | observation noise set to 2e-5 rad, making the likelihood a delta | realistic values (3e-4 rad, 1e-3 rad/s), ESS-triggered resampling, roughening |
| belief systematically inferred deceleration | particles propagated *then* weighted against the *current* observation — a one-step lag | skip propagation on the first update |
| model preferred a gentle crash to hard braking | collision cost applied for one timestep, severity scaled quadratically to near zero at low speed | running minimum over the horizon; SI's linear severity with a 0.2 floor |
| 15% of futures were collisions during ordinary following | initial belief about the lead's acceleration as wide as the process noise (±3 m/s²) | separate `sigma_a_init = 0.5 m/s²` |
| predicted lead speed spread ±6 m/s over 4 s | transition noise made persistent across the horizon rather than per-step | per-step noise, as the paper specifies |
| pragmatic deficit ≈ −330 even mid-lane | logistic lane boundary of width 0.25 m against a −15000 cost leaks ~2% everywhere | SI's triangular `p_lat` |

The remaining gap is a calibration problem of the same kind as Track A's: the paper tunes 13
free parameters and calibrates `a_OV,min` per scenario through a separate free-following
study. Closing it is a tractable but non-trivial piece of work — see "next steps".

### Honest summary

If the goal is *using* the published model, Track A is the route and it works. If the goal is
*understanding and extending* it — which is what the comfort-zone work needs — Track B's
preference function and surprise machinery are correct and tested, and its closed-loop
controller needs the parameter-calibration step before it can be trusted for response-timing
claims. The comfort-zone method in `04_comfort_zone_method.md` deliberately depends only on
the parts that are verified.

---

## Next steps to close the gap (in order of expected value)

1. **Re-run the free-following calibration** for the actual operating range, in both tracks.
   For Track A this means regenerating `Analysis_following.xlsx` with the paper's
   `looming_threshold`/`noise_pred_fac`/speeds and THW up to 3.5 s. For Track B it means
   choosing `a_OV,min` so that steady following at the target THW leaves `p_safe` inactive
   across the predicted particle distribution — the check is already written
   (see the sweep in `notes/03_replication.md` history: `a_OV,min ≥ −6` gives a safety term of
   exactly 0 at THW 1.5 s).
2. **Smooth the CEM output.** Penalising jerk between consecutive planned actions, or fitting
   the elite set with a smoothness prior, would cut the control-effort contribution to `ε`
   that currently swamps the closed-loop surprise signal.
3. **Ablate against the paper's Fig. 6.** Once timing is right, the ablations (no evidence
   accumulation, no looming, no norms, no pedal constraints) are cheap and are the strongest
   available check that the mechanisms are doing what they do in the original.
4. **Get the OSF simulation data** (`osf.io/gs4bu`) and compare distributions directly rather
   than against numbers read off figures.
