# Handover: implementing card JJ.1, for a less expensive model

*Written 2026-09-18 by the session that designed the card, at Jonas's instruction that the
implementation be done by a cheaper model with everything documented for it. This file is the
implementer's brief. It is self-contained: every file, function, constant, rule and stop condition you
need is here or pointed to by exact path. You do not need to read the argument behind the design
(`docs/active_inference_program.md`) to do the work; you do need to read
`docs/rollout_boundary_design_note.md` once, because the pre-stated rules you will copy into script
docstrings live there and must be copied verbatim. Where this file and the design note disagree, the
design note wins and you say so in the worklog.*

## 0 Before anything

1. Read `handover.md` §0 and §2 (the session start procedure and the ten standing rules), then
   `docs/czb_work_orders.md` §2, then `docs/rollout_boundary_design_note.md` in full, then this file.
   Do not read the papers, the handbook, `OthersWork/` or the handovers older than 2026-09-13.
2. Run the eleven-file suite exactly as `handover.md` §0 step 2 lists it and confirm
   31/33/40/96/62/20/28/27/16/30/28. Run `git status`; the tree is clean apart from
   `docs/handout_schumann_2026-09.docx`, which you never stage.
3. The colleague whose ideas this card tests is referred to as **JJ** everywhere. Never write the
   colleague's name or company in any file, commit message or report. If you find either in a file you
   are editing, do not remove it; write a query.
4. Everything you compute and quote comes from a committed script with a tracked output. No numbers
   from an interactive session, ever.

## 1 The task in one paragraph

Build a package `src/rollout/` that, for one frozen moment of one stimulus clip, (i) reads the scene
into a belief, (ii) samples a fan of the other road user's futures under a constant-velocity Gaussian
predictor with a latent lane-change intention, (iii) rolls out a small menu of the ego's policies,
(iv) scores every policy on every sampled future with the released preference function, in its
residual-information form, and (v) returns ΔG = G(continue) − min over the menu, in nats, with its
Monte Carlo standard error. Then write three scripts that put ΔG on the second cut-in study's cells
(JJ.2), on the first study's left turn and cyclist overtake (JJ.3), and refit the estimator's spread as a
precision (JJ.4), each scored by the rules the design note fixed in advance. The verdicts are written
before the runs; you do not reinterpret them.

**Deliverables:** `src/rollout/{__init__,belief,predictor,policies,efe,boundary}.py`;
`tests/test_rollout.py` in the `check()` style with the tests of §6; `replication/czb/jj2_rollout_cutin.py`
→ `replication/czb/out/jj2_rollout_cutin.md` (+ per-cell CSV); `jj3_rollout_transfer.py` →
`out/jj3_rollout_transfer.md`; `jj4_precision_spread.py` → `out/jj4_precision_spread.md`; worklog entries
with queries; `handover.md` §0 step 2 extended by `python tests/test_rollout.py`; one commit per step.

## 2 Order of work, and what "done" means for each step

| step | do | done when | stop and query if |
|---|---|---|---|
| 1 | `src/rollout/` and `tests/test_rollout.py` | every test in §6 passes; the suite is green; commit | any test in §6 cannot be made to pass without changing a definition in §3 |
| 2 | `jj2_rollout_cutin.py`: docstring with the rules of design note §2 copied verbatim, then the run, then the report | `out/jj2_rollout_cutin.md` states each rule with its number and PASS/FAIL, the sweep tables, the Monte Carlo check; worklog entry; commit | the jitter floor makes the intention update uninformative (design note §2, last paragraph); any cell's trace ends before its freeze; ΔG = 0 in more than 10% of cells |
| 3 | `jj3_rollout_transfer.py`: design note §3 | report with rules (a) to (d) and the trait table; commit | the left-turn "proceed" path cannot be built from the recorded ego (see §4.6); the overtake traces lack a lateral trace of the ego |
| 4 | `jj4_precision_spread.py`: design note §4 | report with the two contrasts and the derived gate spread; commit | you would need a perceptual constant with no source: report "not yet possible" for that line, per JJ1.Q3, and continue |

After step 4: a worklog entry summarizing the three verdicts in the design note's own words, and a
short section appended to this file, "§9 What the implementer found", listing the numbers a reader must
not re-derive and the queries raised. Do not update `handover.md` §1 or §4 beyond the suite list; the
reviewing session does that.

## 3 The construction, as code

All constants below are in the design note with their motivation. Put every one in a module-level
constant with a one-line comment naming its motivation, exactly as `src/comfortzone/interface.py` does.

### 3.1 Belief at the freeze (`belief.py`)

```python
@dataclass
class Belief:
    x_rel: float      # other's longitudinal position relative to the ego, centre to centre [m], + ahead
    y_rel: float      # other's lateral position relative to the ego [m]
    v_ego: float; v_oth: float           # speeds along the road [m/s]
    vy_oth: float                         # other's lateral rate [m/s], backward difference over `window_s`
    sd_pos: float; sd_vy: float           # measurement sd of positions and of the lateral rate (the jitter floors)
    p_change: float                       # P(other is changing lanes into the ego's lane)
    ego_len: float; ego_wid: float; oth_len: float; oth_wid: float
```

`belief_at(scene, t0, window_s, floors) -> Belief`. The lateral rate is the backward difference over
`window_s` = 0.3 s (second study, 30 Hz traces) or 1.0 s (first study, 10 Hz traces); these are card G.1's
and card PC.1's windows and are not tuned. The jitter floors are the ones card HS.1 measured: read them
from the docstring of `replication/czb/hs1_situational_surprise.py` (its "sigma0" discussion gives the
per-study, per-axis floors and the reason for the two windows) and cite the line in your module
docstring; do not type a floor from memory.

`update_intention(p0, vy_obs, sd_vy, v_lc=1.2, sd_lc=0.4) -> float`: one Bayesian update from the
lateral rate observed over the window, likelihoods N(vy_obs | 0, sd_vy) for "keeping" and
N(vy_obs | −v_lc·sign, sd_lc) for "changing" (sign such that the change is toward the ego's lane). Return
the posterior. `p0` = 0.07 first value, sweep {0.02, 0.07, 0.20}.

### 3.2 The fan (`predictor.py`)

`sample_futures(belief, horizon_s=6.0, dt=0.2, n=200, sd_vlat=0.33, sd_a=0.5, seed) -> Futures` with
`Futures.x[n, T]`, `Futures.y[n, T]`, `Futures.v[n, T]` for the other road user in the ego's frame at the
freeze (a fixed frame moving with the ego's position at t0, not with the ego's later motion: the ego's
policies move the ego, and the relative position is formed in `efe.py`). Per sample: draw the intention
(Bernoulli p_change); draw a lateral velocity perturbation ~ N(0, sd_vlat) and a longitudinal acceleration
perturbation ~ N(0, sd_a), both constant over the sample's horizon (that is what "growth linear in τ for
position sd, in τ² for acceleration" means in the design note); under "changing", the lateral rate is
−v_lc·sign toward the ego's lane until the lane centre is reached, then zero; under "keeping" the lateral
rate is the observed one plus the perturbation, clipped so the vehicle never crosses into the ego's lane.
Use one `numpy.random.default_rng(seed)` and return the same `Futures` object to every policy: common
random numbers are a design requirement, not an optimization.

`P1` (the released norm tournament) is optional for JJ.2 and only if step 2 has otherwise passed: a
wrapper on `src/common/dynamics.py::forward_tar_agent` run open loop for 30 steps. If the released
code's interface makes this more than a day of work, write a query and skip it; it is a secondary.

### 3.3 The policy menu (`policies.py`)

`ego_rollout(belief, policy, horizon_s, dt) -> EgoPath` with `x[T], v[T], a[T]` along the road and `y[T]`
= 0 (no steering; Jonas's ruling JJ1.Q1). Policies are constant-acceleration segments from the freeze:

| scenario | policies | acceleration [m/s²] |
|---|---|---|
| cut-in, both studies | `continue`, `ease_off`, `brake`, `brake_hard` | 0, −1, −3, −6 |
| left turn | `proceed`, `wait` | proceed = the recorded ego path (see §4.6); wait = −3 until stopped before the crossing |
| cyclist overtake | `continue`, `abort` | continue = the recorded ego path at the shown clearance; abort = −2 until behind the cyclist, lateral return to lane centre over 2 s |

Speeds are clipped at zero. A policy's rollout is deterministic.

### 3.4 Scoring (`efe.py`)

For each policy and each sampled future, build the observation dict the preference function expects
(`src/aidriver/preferences.py::log_preference_terms`, whose docstring lists the keys: `v, a, omega,
a_lat, y, dx, dy, v_other, a_other, theta, theta_other`; also pass `vy_other` and `w_other`, which the
continuous lane-entry weight reads, exactly as `src/comfortzone/cutin.py::cutin_obs` does). `dx` and
`dy` are the other's position relative to the ego *along the policy's own rollout*. Then

```
terms   = log_preference_terms(obs, p)              # dict of six arrays [n, T]
logp    = sum(terms.values())                        # [n, T]
logp    = apply_running_min on the collision term only, along T (preferences.apply_running_min)
G(pi)   = sum over T of ( p.max_log_preference() - mean over n of logp )    # nats, >= 0 by construction
```

Variant A: `PreferenceParams` as `cutin_params(trace)` returns it for the cut-in (desired speed = the
clip's ego speed, continuous lane-entry forms on); for the left turn and the overtake use the same
constructor pattern with the scenario's lane geometry (§4.6, §4.7). Variant B: the same with the safety
term switched off. **Add one flag to `PreferenceParams`, `safety_term_enabled: bool = True`**, read in
`log_preference_terms` so that `terms["safety"]` is zero when False. That is the only change to
`src/aidriver/preferences.py`, it defaults to the released behavior, and it must leave every existing
test untouched. Epistemic value: not in this card (α = 0); leave a hook, do not implement.

### 3.5 ΔG and its axis (`boundary.py`)

`delta_g(G_by_policy) -> float` = G["continue"] − min(G.values()), ≥ 0. `axis(dG_by_cell)` = log ΔG, with
the zero rule of design note §1.5: if any cell has ΔG = 0, use log(ΔG + ΔG_min/2) with ΔG_min the
smallest positive value across cells, and report the count. `mc_standard_error(belief, policy_menu,
seeds)`: ΔG across at least 5 seeds, reported per cell; rule (e) of design note §2 compares its median
with 5% of the between-cell spread of log ΔG.

## 4 The code you reuse, with what it gives you

Import; do not copy and do not modify. Every path below exists today.

### 4.1 The preference function

`src/aidriver/preferences.py`. `PreferenceParams` (dataclass; the released constants; flags
`lane_entry_continuous`, `counterfactual_residual_severity`, `lane_entry_shape_k`,
`lane_entry_bidirectional`, `lane_entry_horizon_s`, all defaulting to released behavior).
`log_preference_terms(obs, p) -> dict` of six arrays broadcast to a common shape; `log_preference`;
`apply_running_min(log_coll, axis=-1)`; `pragmatic_deficit`; `PreferenceParams.max_log_preference()`.
Rule 3 of the standing rules: **never change a default**; your one new flag defaults to True.

### 4.2 The second cut-in study: cells, folds, metric, gate

`replication/czb/cutin2_field_vs_gap.py` is **pre-registered: never modify it; import from it.**
`cell_table() -> (cells, per_participant)`: one row per video with `p` (share who intervene), `n`,
`distance`, `ttc_true`, `dv_kph`, `cp` (the timepoint; CP1 is pre-onset), `lcd` (lane-change duration),
`ttc_start` (the design's starting TTC; **the fold id**), `gap_trace`, `vrel_trace`. The three-parameter
threshold model is `predict(theta, x, sign)` and `fit(x, y, w, sign)`; `wrmse(y, pred, w)`; the fold loop is
`held_out(...)` (read `main()` for how the fold ids are formed from `ttc_start` and how the 288 post-onset
cells are selected by `cp`; reproduce that selection exactly and assert the counts 288 and 90).
`replication/czb/cutin2_gate.py` (also pre-registered, import only): `lateral_states(videos)` gives `l0`
and `ldot` per video at the response moment, `T_ENC = 3.0`, `gate(m_lat, log_s, l0, ldot)`,
`held_out_gated(cells, folds)`; its report `out/cutin2_gate.md` holds the comparators 0.1137 (ungated),
0.1027 (gated), 0.0319 (CP1 gated), 0.4832 (CP1 ungated). The matched-TTC row construction of design note
rule (c) is in `replication/czb/cutin2_lane_gate_diagnostic.py`; import its row grouping rather than
rewriting it.

### 4.3 The second study's traces (the scene at the freeze)

`replication/czb/hs1_situational_surprise.py`: `study2_scenes(cells)` returns, per trace key, `grid`
(times), `tracks` (`Track` objects with `.x`, `.y` in world frame), `meta` (per vehicle: `width`,
`length`, `speed[T]`, `heading[T]`), `ego` and `tar` ids; `scene_tracks(path)` does the loading and the
teardown trimming; `theta_state(sc, t_at)` shows how the gap and looming are read at a moment and is the
convention for `x_rel` (centre to centre along world x; the road is aligned with x to under 0.1°). The
freeze time per cell is the response moment `e_t` that `cutin2_gate.lateral_states` uses; read how it is
formed there. Trace files: `R.KIN / f"{key}_vehicle_states.csv"` with `R` the registered script;
`R.VIDEO_RE` parses video names into `dv`, `tlc`, `ttc`.

### 4.4 The first study's cut-in and the estimator

`src/comfortzone/cutin.py`: `load_cutin_trace(path, is_truck)` → `CutInTrace` (fields `t, v_ego, a_ego,
y_ego, x_tar, y_tar, v_tar, a_tar, tar_len, tar_wid, onset_idx, complete_idx`); `cutin_params(trace, p)`
sets the desired speed from the clip and the continuous forms; `cutin_obs(trace, p)` is the obs-dict
pattern. `LANE_WIDTH_STUDY = 3.5`; lane centres at y = −1.85 and −5.35 in the traces.
`replication/czb/fit_stage1_looming.py` (the stage-1 hierarchical estimator on the gated looming rule):
`build_trials()` (study 1's 3 096 Random cut-in trials with driver ids), `priors_log_scale(x)`,
`fit_hier_lapse_gated(x, g, y, pid, pr)` (pass `g = 1` everywhere: **no gate**), `lopo_loglik_gated`,
`percentiles_log(f)`. `replication/czb/driver_levels.py`: `posterior_mean_levels(x, g, y, codes, fit)`,
`boot_spearman(a, b)`; its report `out/driver_levels.md` has the +0.647 comparator and the 43-driver set.
`replication/czb/ex2_first_exposure_levels.py` shows the session term; JJ.3's trait table is at first
exposure, as card EX.2 made primary.

### 4.5 The left turn

`src/comfortzone/ltap.py`: `ltap_traces()` → `LtapTrace` objects (fields include `ego_id, onc_id, t_dec,
d_onc, v_onc, tta, t_sep, w_onc, t_onset, t_in, t_out, x_conf`), `ltap_cells()` (18 rows with `p` and the
geometry at the decision moment), `T_DECISION_S = 13.5`, `NOMINAL_ONC_SPEED_MPS = {50: 13.9, 70: 19.4}`,
`looming_rate(width, closing, range)`. The comparator 0.0558 (distance alone, leave-one-PET-out) is in
`out/ltap_two_axis.md`; `replication/czb/ltap_two_axis.py` shows the fold construction. The raw tracks
for the "proceed" path: `replication/czb/pc1_projected_conflict.py::ltap(frozen)` shows how the ego's
recorded future is read into a `Body` and a `planned_path` (§4.6).

### 4.6 Paths and bodies

`src/comfortzone/conflict.py`: `Body(t, x, y, heading, length, width)`; `kinematic_path(body, t_at,
v_window, dt)` (reading K) and `planned_path(body, t_at, dt)` (reading P: the recorded future, continued
at the last-window velocity); `body_polygon`, `polygon_distance`, `corridor_clearance`. For the left turn,
"proceed" is `planned_path` of the ego body at `T_DECISION_S`; for "wait", a stop before the crossing
point `x_conf` from `LtapTrace`. Collision in a sampled future = polygon overlap of the ego at its policy
position and the other at its sampled position at the same τ (`polygon_distance <= 0`); use the
preference function's collision term on `dx, dy` where the released geometry applies (straight roads) and
the polygon test where the paths cross (the left turn); say which in the report.

### 4.7 The cyclist overtake

`src/comfortzone/overtake.py`: `load_overtake_trace(path)` → `CutInTrace` with the cyclist as the target;
`RANDOM_OVERTAKE_TRACES`, `NOMINAL_CLEARANCE_M = {"0.5m": 0.5, "1m": 1.0, "1.5m": 1.5}`,
`edge_clearance(trace, ego_width)`. The 15 cells with responses: `replication/czb/transfer_cutin_to_overtake.py::cells(df)`
and its report `out/transfer_overtake_summary.md`; the field's failure to grade clearance is
`out/overtake_field_check.md`.

### 4.8 The test track (JJ.4 only)

`replication/czb/ltapod_testtrack.py` and `out/ltapod_testtrack.md`; `external/README.md` for the file's
columns. **Never use the observed PET column as the stimulus; SetPET is the stimulus** (`handover.md` §5).

## 5 The scripts

Each script: a docstring that begins "THE PRE-REGISTRATION. Everything in this docstring was written
before the run." and copies the relevant rules from the design note verbatim (§2 for JJ.2, §3 for JJ.3,
§4 for JJ.4), then the settings table with each constant and its motivation, then the run. Write the
main report **before** any bootstrap or seed sweep (rule 10 of `handover.md` §2), so that the verdict
never waits on the slow part. Launch in the background with output redirected to
`replication/czb/out/log_jj2.txt` (and `jj3`, `jj4`); before calling a run stuck, check its CPU time.
Reports are generated files ("Do not edit by hand" in their first lines) in the style of
`out/pc1_projected_conflict.md`: settings, implementation checks, one section per rule with the number
and PASS/FAIL, the sweep tables, the verdict in the design note's words. Per-cell CSVs carry no
participant ids.

Cost expectations: JJ.2's rollouts (378 cells × 4 policies × 200 futures × 30 steps) run in seconds to a
minute in NumPy; the fits and folds in minutes; the seed sweep for rule (e) in minutes. JJ.3's
hierarchical fits take 5 to 35 minutes each (`handover.md` §7); the trait table needs two. JJ.4's
refits are of the same kind.

## 6 Property tests (`tests/test_rollout.py`, `check()` style, run as a script)

Belief: (1) with the lateral rate at the jitter floor the posterior equals the prior to 1e-3; (2) a
sustained rate of −v_lc toward the ego drives the posterior above 0.95; (3) mirroring the scene's lateral
sign leaves the posterior unchanged.
Predictor: (4) with `sd_vlat = sd_a = 0`, `p_change = 0` and a straight other, every sample equals the
constant-velocity projection (the G.1 limit); (5) the sample mean of `y` at τ = 3 s matches the analytic
mean within 3 standard errors; (6) the same seed gives bit-identical `Futures` for two calls; (7) under
"changing" the lateral position stops at the ego's lane centre.
Policies: (8) `continue` holds speed to 1e-12; (9) `brake_hard` from v reaches zero at v/6 s within one
step; (10) the left-turn `proceed` path reproduces `planned_path` of the ego body to 1e-9.
Scoring: (11) G ≥ 0 for every policy on every scene; (12) two identical policies give identical G;
(13) with `p_change = 0`, a lane-keeping other and no perturbation, ΔG = 0 exactly; (14) a certain
collision under `continue` and none under `brake` gives ΔG > 0, and ΔG at a 10 m gap exceeds ΔG at a
30 m gap; (15) variant B differs from variant A only in the safety term (all other five terms
bit-identical); (16) the new flag at its default leaves `log_preference_terms` bit-identical to the
committed behavior on `cutin_obs` of one study-1 trace.
Boundary: (17) the zero rule is applied only when a zero exists; (18) the Monte Carlo standard error
falls as 1/√n across n ∈ {50, 200, 800} within a factor of 1.5.
Then extend `handover.md` §0 step 2 with `python tests/test_rollout.py` and its count.

## 7 What you must not do, and when to stop

- Never modify a script whose docstring says pre-registered (`cutin2_field_vs_gap.py`, `cutin2_gate.py`,
  the cards of 2026-09-02, `hs1_situational_surprise.py`, `pc1_projected_conflict.py`); import from them.
- Never change a default in `src/aidriver/preferences.py`; the one new flag defaults to the released
  behavior.
- Never choose a constant by its held-out score. If a sweep value looks better, report it; the primary is
  the motivated one.
- Never reinterpret a rule to reach a verdict. If a rule cannot be applied as written (a comparator
  number is missing, a count differs, a trace is shorter than the window), stop, write the query, and
  continue with what does not depend on it.
- Never quote a number that is not in a tracked output; never edit a generated report by hand.
- Never stage `docs/handout_schumann_2026-09.docx`; never push.
- Edit files with the Edit and Write tools, never with shell heredocs (rule 9 of `handover.md` §2; the
  designing session hit the `\n` trap itself on 2026-09-17).
- Queries go in `replication/czb/out/worklog.md` as `@JJ2.Q<n>(<severity>, <who>): ...` (`JJ3`, `JJ4`
  for the other cards), then `python replication/czb/collect_queries.py`. Blockers end the step; judgment
  calls do not block what is independent of them.

## 8 Where the designing session may have left you a trap

- The desired speed must be the clip's ego speed (`cutin_params` does this); the default 15 m/s puts a
  constant −483 into every frame (the 2026-08-26 staging error).
- The released collision cost is −10 000 and the road-edge cost −15 000; G will be in the thousands of
  nats and log ΔG's spread across cells is driven by how many sampled futures collide. That is the
  mechanism; check rule (e) rather than assuming it holds.
- The second study's traces jitter at about 0.1 m at 30 Hz and the first study's at 0.2 m lateral and
  1.75 m longitudinal at 10 Hz (HS.1's docstring gives the measured values and the three-times rule);
  a one-sample velocity is unusable, which is why the windows are 0.3 s and 1.0 s.
- The lateral frame: in the second study the ego and the cut-in vehicle are in adjacent lanes 3.5 m
  apart and the cut-in is toward the ego's lane; the sign of "toward the ego" must be read from the
  scene (`study2_scenes` identifies `ego` and `tar` by geometry), never assumed.
- Study 1's left-turn ego turns; `dx, dy` in the ego frame rotate with its heading. Use the polygon test
  for collision there and say so.
- On the overtake the ego moves laterally and the cyclist does not; the fan is nearly a point and the
  grading in clearance must come from the lateral term and the polygon test. If the released lateral term
  cannot see the clearance (it could not in `out/overtake_field_check.md`), rule 3(d) fails for that
  reason, and the report says which term was blind.

## 9 What the implementer found

*Appended 2026-09-18 (overnight) by the session that executed this brief. All four steps are done and
committed; the suite is green at 31/33/40/96/62/20/28/27/16/30/28/27 (twelve files) before and after.
The dated record is the worklog's four entries of 2026-09-18.*

### The verdicts, in the design note's own words

- **JJ.2: DROP.** "Drop if (a) fails." Rule (a) fails at both variants — post-onset held-out **0.3202**
  (released) and **0.2976** (no p_safe) against the gated looming rule's 0.1027 + 0.01. 0.3202 *is*
  chance (0.320 on file): the threshold model collapses to the training mean because log ΔG is
  anti-ordered with the response. Rule (b) 0.5381, rule (c) 0 of 24 rows (variant B 3 of 24), rule (e)
  passes. Rule (d)'s sweep moves nothing.
- **JJ.3, left turn: every rule fails.** (a) 0.2632 against 0.0558 + 0.01; (b) the 70 km/h predicted
  share is below the 50 km/h one at **0 of 9** matched PETs; (c) no sampled future collides under
  "proceed" at PET 4 s within the released 6 s, so — as rule (c) says in advance — "the emergence claim
  fails on the left turn at that PET rather than extending the horizon". The horizon was not extended.
- **JJ.3, overtake: rule (d) holds at C1–C4 and fails at C5.** ΔG held out (leave-one-timepoint-out)
  0.1580 against the clearance rule's 0.2099 and chance 0.1626.
- **JJ.3, the trait: "ΔG loses per-driver signal that the scenario-specific axes keep"** (+0.261
  [−0.106, +0.575] against TR.1's +0.647 [+0.407, +0.798]) — **with the caveat stated before the
  reading** that the left turn's ΔG axis takes two distinct values over nine cells. EL.Q4 is not
  answered by this card.
- **JJ.4: the two-spread model earns its place** (+60.6 held-out log-likelihood units under LOPO
  against the margin of 2) and **the truck is sharper** (0.273 against 0.424). The video/track ratio is
  **4.34 [2.38, 7.93]**; the ratio predicted from perception is **not yet possible**, per ruling JJ1.Q3.
  The gate's spread is **not** measurement noise: the traces' own lateral-rate jitter is 156 times too
  small.

### The numbers a reader must not re-derive

| number | what it is | file |
|---|---|---|
| 0.3202 / 0.2976 | ΔG post-onset held out, variants A / B, second cut-in study | `replication/czb/out/jj2_rollout_cutin.md` |
| 0.5381 / 0.2495 | the same fits' pre-onset out-of-sample | ibid. |
| 0 of 24 / 3 of 24 | matched-TTC rows ΔG orders like the data, A / B | ibid. |
| 0.0052 against 0.0574 | rule (e): median per-cell SE of log ΔG against 5% of its spread | ibid. |
| −0.648 / +0.848 | Spearman of ΔG with the share / with the gap, post-onset | ibid. §1b |
| +0.927 | Spearman of G(continue) with dv — the speed ordering, inside the rollouts | ibid. §1b |
| 20 308 nats | the fixed control-effort cost of −3 m/s² over the horizon | ibid. §1b |
| 0.2632 | ΔG held out on the left turn, leave-one-PET-out | `out/jj3_rollout_transfer.md` |
| 16 of 18 | left-turn cells with ΔG = 0 | ibid. |
| 0.1580 / 0.2099 / 0.1626 | overtake: ΔG / the clearance rule / chance, leave-one-timepoint-out | ibid. |
| +0.261 [−0.106, +0.575] | the trait on one scale, 43 drivers, first exposure | ibid., `out/jj3_driver_levels.csv` |
| 0.858 s / 0.198 s | σ_resp video / track (card TT.1's 0.86 and 0.20, reproduced) | `out/jj4_precision_spread.md` |
| 4.34 [2.38, 7.93] | the fitted video/track spread ratio | ibid. |
| 0.4239 / 0.2732, +60.6 | σ_resp car / truck and the LOPO gain | ibid. |
| 0.0021 m/s, 0.0064 m, ×156 | the traces' lateral-rate jitter against G.1's s_l = 0.990 m | ibid. |

Per-cell data, no participant ids: `out/jj2_rollout_cutin_cells.csv`, `out/jj3_rollout_cells.csv`,
`out/jj3_driver_levels.csv`. Run logs: `out/log_jj2.txt`, `log_jj3.txt`, `log_jj4.txt`.

### The one mechanism behind three of the four failures

ΔG is a **value-of-action** quantity. It is large where an alternative would avert something that
continuing would cause, and it must be small both where nothing is going to happen and where nothing in
the menu helps any more. It therefore cannot be monotone in criticality, and on the cut-in it is
*anti*-ordered with the gap. The menu's own price is the other half: at the released σ_a = 0.1 m/s² a
−3 m/s² alternative costs a fixed 20 308 nats over the horizon whatever the scene is doing, so the
minimum over the menu is floored, and on the left turn waiting costs more than proceeding in 16 of 18
cells. Separately and independently, the released magnitude still grades by **speed** rather than by
**gap** inside the rollouts — G(continue) alone correlates +0.927 with Δv and scores 0.3202 too — which
is the R.2 pipeline review's finding reappearing. The policy comparison and the preference function
are therefore not to be blamed for one another, and JJ2.Q2 puts the choice to Jonas.

### Queries raised

`JJ1.Q6` (the one-sided intention update, for Jonas — property test (1) cannot pass otherwise);
`JJ2.Q1`–`JJ2.Q4`; `JJ3.Q1`–`JJ3.Q6`; `JJ4.Q1`–`JJ4.Q4`. Fourteen in all, in
`replication/czb/out/worklog.md` and compiled into `out/query_register.md`. The three that decide what
happens next are **JJ2.Q2** (is there a repair of ΔG worth designing, or does the preference
magnitude have to be fixed first?), **JJ2.Q3** (should an evasive policy be priced with the released
free-driving σ_a?) and **JJ3.Q2** (the left turn's "wait" cannot be both −3 m/s² and clear of the
crossing). `JJ1.Q4` and `JJ1.Q5` from the designing session are still open; the brief directed the
flag JJ1.Q4 asks about, so it was added, and P1 (the released norm tournament, JJ1.Q5) was not built —
JJ.2's verdict makes a secondary predictor moot until the primary is settled.

### What this session may have got wrong

1. **The one-sided intention update** (JJ1.Q6) is a construction choice, not a transcription. With the
   plain likelihood ratio the pre-onset cells would carry P(changing) ≈ 1e-40 rather than 0.07. It
   changes the pre-onset cells' ΔG and therefore rule (b); it does not touch rule (a), which is what
   decides the verdict.
2. **The left turn's "wait" deceleration** was raised per cell (3.6 to 4.7 m/s²) so that the policy
   stops clear of the conflict band. With the design note's literal −3 m/s² the ego stops *on* the
   crossing and is struck there, and ΔG would be larger in every cell for a reason that has nothing to
   do with comfort. Both readings are in JJ3.Q2; the report carries the per-cell value.
3. **The ego's lane offset is zero on the left turn** for both policies (JJ3.Q1), so the released
   lane-keeping term never fires there. Passing the real offset charges "proceed" −15 000 per step for
   turning out of a straight lane by design.
4. **The overtake's fold scheme** was not fixed by the design note; both are reported and the choice is
   argued rather than scored, but both were computed after the run (JJ3.Q5).
5. **The apparent-size contrast is not the stage-1 estimator** (JJ4.Q1), because that estimator cannot
   be fitted where the intervention share is 0.976 to 1.000.
6. **P1, the released norm tournament**, was skipped (JJ1.Q5 allows it); §3.2 calls it a secondary.
7. The scripts are named `jj2/jj3/jj4_*` after this brief, not `je2/je3/je4_*` as design note §5 has
   them (JJ2.Q4).
