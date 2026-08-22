# A method for establishing driver comfort-zone boundaries from active inference

This is the proposed method, what it rests on, what is implemented, and what would be needed
to validate it against data.

---

## 1. The problem with the current way of doing it

Comfort-zone boundaries (CZBs) are normally quantified **per scenario, per indicator**: a
distribution of accepted minimum TTC in LTAP/OD, of lateral clearance when overtaking a
cyclist, of THW in following. Each study picks the kinematic variable that seems to matter in
that scenario and reports a quantile of what drivers accept.

That works, but it has three costs:

1. **Boundaries are not comparable across scenarios.** A THW boundary and a lateral-clearance
   boundary are different objects; there is no principled way to say whether a driver is
   "equally close to their comfort zone boundary" in the two.
2. **The choice of indicator is a modeling assumption in disguise.** Nothing tells you
   whether min-TTC or required deceleration or PET is the variable the driver is actually
   regulating.
3. **No mechanism.** A quantile of accepted TTC describes behavior; it does not explain why
   drivers act when they do, and it cannot predict the boundary in a scenario not yet
   measured.

## 2. The proposal

Use the driver's **preference function** as the primitive, and define the comfort zone as a
level set of a single scalar field derived from it.

The active-inference driver model already contains a preference prior `p(o)` — a distribution
over observations in which the observations the driver *wants* are the ones assigned highest
probability. Define the **comfort-zone field**

```
    eps(x) = max_o log p(o)  -  log p(o(x))     >= 0
```

the *residual information* of the pragmatic value (Dinparastdjadid et al. 2023) evaluated at
state `x`. Then

| construct | definition |
|---|---|
| comfort zone | `{ x : eps(x) <= c }` |
| comfort-zone boundary | `{ x : eps(x) = c }` — a level set |
| dread-zone boundary | where no policy can restore preferred observations |
| extra motives | a change to `p(o)`, hence to the field, hence to the boundary |
| CZB exceedance → action | accumulated evidence `E_t = E_{t-1} + λ·eps_t` crosses threshold |

Three properties make `eps` the right scalar rather than an arbitrary one:

- **Zero floor.** `eps` is exactly 0 at the preferred observation and only there. Inside the
  comfort zone it is genuinely quiet, so exceedance is a well-defined event rather than a
  threshold on a always-positive signal. (Surprisal does *not* have this property; see
  `tests/test_surprise.py`, where surprisal returns 1.27 at the mode of a Gaussian.)
- **Parameterless on continuous distributions.** No bin width to choose, unlike surprisal
  or Macedo's S8, and the value is invariant to discretization — verified in the tests.
- **It is the same quantity the model uses to decide when to act.** `eps` is literally the
  evidence the driver accumulates toward re-planning (Schumann et al. Eq. 13). So the
  comfort-zone boundary and the response-onset mechanism are not two theories glued together;
  they are one object viewed statically and dynamically.

**The kinematic indicators become projections.** Because `log p(o)` is a sum of independent
terms (speed, control effort, lane keeping, inverse-tau, collision, safety margin), the field
decomposes additively and you can ask *which* term is responsible for a given exceedance.
Classical per-scenario indicators are then slices through one surface, which explains why they
differ between scenarios without requiring a new theory for each.

## 3. What the model already gives you for free

Schumann et al.'s preference function contains a term that *is* a comfort-zone boundary,
though the paper does not call it that. `p_safe` (SI Eq. 49–51) penalizes exactly those states
in which, *if the lead vehicle braked hard and the driver responded after 1 s*, the required
deceleration would exceed what is achievable:

```
    a_ego,req = -0.5 * v_react^2 / ( d_react - 1.15 L )
    v_react   = v_ego + min(a_ego,0) * t_react
    d_react   = [ dx - v_other^2 / (2 a_test) ] - [ v_ego t_react + 0.5 min(a_ego,0) t_react^2 ]
    a_test    = min(a_other, a_OV,min)
```

Setting `a_ego,req = -a_limit` and solving for the gap gives a **closed-form boundary**:

```
    dx* = 1.15 L + 0.5 v_react^2 / a_limit
          - v_other^2 / (2 |a_test|) + v_ego t_react + 0.5 min(a_ego,0) t_react^2
```

implemented as `comfortzone.critical_gap` / `critical_thw`, and cross-checked against the
numeric level set of the field (agreement to 0.000 m over 45 speeds).

That cross-check is worth keeping rather than treating as a formality. The closed form and the
numeric contour are two independent routes to the same surface, and when they were first
compared they disagreed: a sign error on the `v_other^2 / 2|a_test|` term — the lead vehicle's
own stopping distance *reduces* the separation you need, because it travels that far before
stopping — had inflated the critical time headway from about 0.7 s to about 3.2 s. A value of
3.2 s is not obviously absurd for a safety margin, so the error would plausibly have survived
inspection. It is `tests/test_comfortzone.py::test_closed_form_matches_field` that caught it.

This is a counterfactual, escape-route definition of safety margin, and it is much closer to
what the traffic-psychology literature means by a comfort zone than a bare TTC threshold is.

## 4. Comfort boundary vs dread boundary

The single free choice in the closed form is `a_limit`, the deceleration that defines "no
longer acceptable". This maps cleanly onto the two boundaries of the CZB literature:

- `a_limit = a_max` (8 m/s²) — **dread-zone boundary**: beyond it no achievable braking avoids
  the collision. The limit drivers will not cross *even with extra motives*, because physics
  will not let them.
- `a_limit ≈ 3–4 m/s²` — **comfort-zone boundary**: the limit beyond which the driver would
  have to brake harder than they are willing to. Drivers do not voluntarily plan around
  emergency braking.

Computed values (steady following, lead assumed capable of −6 m/s², `t_react` = 1 s):

| speed | THW* at 8 m/s² (dread) | at 6 | at 4 (comfort) | at 2 |
|---|---|---|---|---|
| 10 m/s | 0.85 s | 1.06 | 1.48 | 2.73 |
| 15 m/s | 0.73 s | 1.04 | 1.67 | 3.54 |
| 20 m/s | 0.61 s | 1.03 | 1.86 | 4.36 |
| 25 m/s | 0.50 s | 1.03 | 2.07 | 5.19 |
| 30 m/s | 0.40 s | 1.02 | 2.27 | 6.02 |

Two things worth noticing. The comfort boundary at ~1.5–2.3 s sits right in the range of
observed following headways, which is a mild sanity check that the construction is not absurd.
And when the assumed lead deceleration equals the braking limit, `THW* → t_react`, essentially
independent of speed — a clean interpretable special case, and a good target for empirical
comparison, since a speed-invariant THW boundary is a strong and falsifiable prediction.

## 5. Extra motives

In Näätänen and Summala's framing, "extra motives" are what make a driver accept normally
unacceptable discomfort. In this construction they are **not** a separate mechanism: they are
a reshaping of `p(o)`, and the boundary moves as a consequence. Implemented and tested:

| motive | parameter change | effect on THW* at 15 m/s, `a_limit`=4 |
|---|---|---|
| baseline | — | 1.67 s |
| hurried / alert | `t_react` 1.0 → 0.6 s | 1.27 s |
| trusting the lead | `a_OV,min` −6 → −3 m/s² | 0.42 s |

This is the part of the proposal with the most research value: it turns "extra motives" from a
verbal construct into a small number of interpretable parameters, each of which is separately
measurable, and it predicts *how much* the boundary should move rather than just that it does.

## 6. What is implemented

```
src/comfortzone/
  field.py      comfort_field()      -- eps over any 2-D slice of the observation space
                critical_gap/thw()   -- closed-form boundary, car following
                ComfortField         -- grid + deficit + margin + per-term decomposition
  boundary.py   boundary_level_set() -- contour of the field at level c
                boundary_curve()     -- single-valued boundary y(x)
                dread_zone_boundary()-- the margin = 0 surface
  calibrate.py  deficit_along_trajectory() -- eps(t) from recorded kinematics, no model run
                exceedance_events()  -- upward crossings of the boundary
                calibrate_level()    -- fit c to observed response onsets (F1 with tolerance)
```

`demo_comfort_zone.py` produces `figures/czb_field.png` (the field with comfort and dread
boundaries), `figures/czb_thw.png` (boundaries as THW vs speed, including an extra-motive
case), and `figures/czb_trajectory.png` (the field along a rear-end trajectory, with the
exceedance marked ~0.2 s before the driver brakes).

Note that `calibrate.deficit_along_trajectory` needs **only recorded kinematics and a
preference function** — no model roll-out, no particle filter, no GPU. That is what makes this
applicable to naturalistic data at scale.

## 7. How to validate it — the study I would actually run

The claim to test is that **one level `c`, fitted once, predicts response onsets across
scenarios**. That is falsifiable and is exactly what per-scenario indicator thresholds cannot
do.

1. Take a dataset with response onsets already extracted in several scenario types — the
   Chalmers LTAP/OD comfort-zone data and the pedestrian-overtaking data are the obvious
   candidates, ideally with a rear-end set for contrast.
2. Compute `eps(t)` along every trajectory with `deficit_along_trajectory`.
3. Fit `c` on **one** scenario with `calibrate_level` (maximizing agreement between the first
   exceedance and the observed onset, within a timing tolerance).
4. **Apply the same `c` to the held-out scenarios.** Compare against per-scenario indicator
   thresholds (min TTC, THW, required deceleration) fitted the same way.
5. Report the additive decomposition of `eps` at each exceedance, to check that the term the
   model blames matches the scenario (safety margin in following, lateral in overtaking).

The generalization step is the whole experiment. If a single `c` transfers, the level-set
formulation is doing real work; if it does not, the honest conclusion is that the preference
function is scenario-specific — which the SI itself concedes ("the preference function might
require adjustments between scenarios") and which would be worth knowing precisely.

## 7b. What data is required

`calibrate.deficit_along_trajectory` needs **only recorded kinematics plus a preference
function** -- no model roll-out, no particle filter, no GPU. That is what makes the method
applicable to naturalistic data at scale. The full requirement:

### Per conflict event, a time series at >= 10 Hz

| Field | Why it is needed | Which term uses it |
|---|---|---|
| ego `x, y, heading, speed` | the observation vector | all |
| ego longitudinal acceleration | control-effort term, and `a_ego` enters `a_req` | accel, safety |
| ego steering (wheel angle or yaw rate) | control-effort term | steer |
| partner `x, y, heading, speed, acceleration`, **same frame as ego** | `dx`, `dy`, `v_other`, `a_other` | collision, safety, tau^-1 |
| both vehicles' length and width | collision box; the `1.15 L` term in `a_req` | collision, safety |
| lane geometry: width, centerline, road edges, and which lanes are same- vs opposite-direction | `y_rel` is defined relative to lane structure (SI Eq. 52) | lateral |
| **response onset** (brake and/or steer), or raw pedal/steering traces to extract it | this is the *label* that the boundary level `c` is fitted to | `calibrate_level` |
| scenario type label | the cross-scenario generalization test in §7 | validation |

### Example: one event as a flat file

```
t,     ego_x,  ego_y, ego_psi, ego_v, ego_ax, ego_delta, oth_x,  oth_y, oth_psi, oth_v, oth_ax
0.00,  0.00,   0.02,  0.001,   15.2,  0.05,   0.002,     26.90,  0.01,  0.000,   15.1,  0.0
0.10,  1.52,   0.02,  0.001,   15.2,  0.03,   0.001,     28.41,  0.01,  0.000,   15.1,  0.0
...
```

plus per-event metadata: `lane_width=3.65, ego_len=4.6, ego_wid=1.8, oth_len=4.4,
oth_wid=1.8, brake_onset_t=3.4, steer_onset_t=NaN, scenario="rear_end"`.

### Three things that commonly go wrong

1. **Frame consistency.** The partner's position must be in the ego frame or a common map
   frame. Radar-only naturalistic data often has good range and range-rate but poor lateral
   position, which makes `dy` and the lateral term unusable.
2. **`a_other`.** The lead's acceleration enters `a_test = min(a_other, a_OV,min)` and hence
   the boundary location. Differentiating speed at 10 Hz with light filtering is usually
   adequate, but it must be checked rather than assumed.
3. **Response onsets.** These are the labels. Extract them the same way the paper does
   (Markkula et al.'s piecewise-linear fit to the speed trace) so the onsets are comparable
   with published values and with the model's own.

### Candidate datasets

| Dataset | Strength | Limitation |
|---|---|---|
| Chalmers LTAP/OD comfort-zone data | boundaries already quantified conventionally -- direct check of whether the level set reproduces them | one scenario type |
| Pedestrian-overtaking field test + UDRIVE | *different geometry* (lateral clearance, not longitudinal margin) -- exactly what the generalization test needs | onsets may need re-extraction |
| SHRP2 NDS | rear-end near-crashes with response onsets; underpins the paper's own deceleration comparison | access; lateral position quality |
| Drone data (highD, exiD, pNEUMA) | excellent kinematics and lane geometry, large N | no driver state, no onset labels -- suits distributional calibration (§7 method 2) only |
| Driving simulator | perfect kinematics, controlled scenarios, and extra motives can be *manipulated* rather than inferred | ecological validity |

### How much

- Fitting a single level `c` by onset-matching: **~30-50 events per scenario type** gives a
  stable estimate; the F1-vs-`c` curve is fairly flat near its optimum.
- The generalization claim: **>= 2 scenario types, ideally 3, with >= 30 events each.**
- Individual differences (do drivers have different `c`, or different preference parameters?):
  repeated events per driver, **10+ each**.

The simulator route deserves emphasis because it tests the one prediction that nothing else
does: that "extra motives" move the boundary by a *predictable amount*. Manipulate time
pressure, measure the shift in accepted margin, and compare with the shift the model predicts
from a change in `t_react` or `a_OV,min`.

## 8. Limitations to be honest about

- **`p_safe` is an indicator, so the field has a step at the boundary.** Good for defining a
  boundary crisply; it means `eps` is not smooth there, so gradient-based analysis of the
  field needs care. A softened variant is easy to add but is a deviation from the paper.
- **The preference function is partly scenario-specific.** `y_rel` is defined per scenario in
  the SI. A map-based general formulation is possible but was not attempted by the authors
  and is not attempted here.
- **`a_OV,min` must be calibrated.** It is the single most consequential parameter for the
  boundary's location, and the paper calibrates it per scenario via a free-following study.
  Any absolute boundary value quoted from this code inherits that assumption.
- **The closed-loop model is not yet validated** (see `03_replication.md`). The comfort-zone
  method deliberately does not depend on it — it needs only the preference function and
  recorded kinematics — but claims that couple boundaries to *predicted response times* do
  depend on it, and should wait.
- **No human data has been used here.** Every number in this note is a property of the model,
  not a measurement. Step 7 is the part that turns this from a construction into a finding.
