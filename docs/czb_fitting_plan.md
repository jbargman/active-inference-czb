# Fitting the comfort-zone boundary to the study-1 data: plan and methods

*2026-08-27. Prepared after the continuous lane-entry forms were settled
(`docs/lane_entry_note.md`) and the desired-speed staging fixed — the two prerequisites
named in `handover_2026-08-26.md` §7. The data pipeline is built
(`src/comfortzone/czb_data.py`), a feasibility fit has been run, and this note records
the model, the method, and the decisions that remain. It extends, and where concrete
supersedes, section (b) of `docs/czb_study1_data_plan.md`.*

## 1 How many parameters this actually is

Jonas asked whether we have good methods for fitting "with so many parameters". The
answer we would give: the fitting is not high-dimensional in the way that question
fears, and the reason is worth stating because it is a design property, not luck.

**Everything upstream of the boundary is frozen.** The preference function keeps the
released parameters (the two structural changes are parameter-free); the desired speed is
staged from the clip; the field along each stimulus is therefore a fixed, precomputed
curve. Nothing in the perception, preference, or scenario layers is fitted. What is
fitted is the *response* layer:

| block | parameters | count |
|---|---|---|
| population boundary level | mean and sd of c (or of log c) | 2 |
| per-driver levels c_i | random effects, shrunk to the population | 43 (80 with Button) |
| response bias b_i | per-driver false-alarm propensity, identified by C1 | 43 (or 1 group-level) |
| ordered comfort/dread | one offset Δ between the two nested levels | 1–2 |
| accumulator (stage 2) | gain and noise (threshold fixed by c's scale) | 2 |
| paradigm shift δ (stage 3) | one level-or-rate shift for Button | 1 |

Roughly 5–8 population parameters plus ~90–170 random effects. That is a **generalized
linear mixed model**, not a black-box search: random effects of this kind are shrunk,
not searched over, and every standard tool handles thousands of them. The methods
question dissolves once the covariate is precomputed.

**Why the likelihood is cheap.** The stimulus field is deterministic and shared: all
3 096 Random cut-in trials take one of 18 covariate values (3 criticality levels × 6
truncation points), computed once. A full likelihood evaluation is vectorized
arithmetic over 3 096 rows; a complete MAP fit takes seconds on this machine. Nothing
here needs the simulator, GPUs, CMA-ES, or approximate Bayesian computation — methods
one reaches for when the likelihood itself requires simulation, which it does not here
precisely because the ego never responds in the clips.

## 2 The model, in three stages

**Stage 0 — static threshold, population level (run, as feasibility).** Intervention iff
the running-max deficit exceeds a threshold, Gaussian variability:
P(intervene) = Φ((x − c)/σ) with x = deficit_max at clip end. Two parameters against the
18-cell surface: **correlation 0.90, RMSE 0.125** (c ≈ 5 200, σ ≈ 2 200). For a field
with zero fitted constants upstream, our reading is that this is strong feasibility
evidence. The residual structure is informative: the fit is too flat *in time* within
each criticality level (for TTC4 it predicts 0.70 → 0.78 across C3–C6 where the humans
go 0.73 → 0.92), which is exactly what a static threshold cannot express and an
evidence accumulator can — probability of having crossed grows with exposure time even
at a constant covariate. The time gradient the static model misses is the accumulator's
signature, visible before fitting one.

**Stage 1 — hierarchical, ordered, per driver.** The real fit:

- c_i ~ population distribution (fit on log scale; the deficit is positive and the
  level multiplicative);
- per-driver bias b_i as a lapse/guess floor: P = b_i + (1 − b_i) Φ((x − c_i)/σ),
  identified by the C1 cells (4 trials per participant per criticality level, so 12
  pre-onset-equivalent trials per driver; thin, so b_i gets strong shrinkage or one
  group level — decision 2 of the handbook ch. 11 list);
- the ordered braking-expectation response (nothing / gentle / hard: 1 180 / 1 287 /
  629 trials) as two nested thresholds c_i and c_i + Δ on the same field — the dread
  level well identified, the comfort level latent with a wider posterior, per the
  agreed framing.

**Stage 2 — the accumulator, and the Button data as held-out validation.** Replace the
static threshold with the existing preference-relative accumulator (`src/surprise/`):
evidence = the deficit series, crossing = response, giving P(crossed by T) for the
fixed-clip cells and a full press-time density for Button. Fit gain and noise on the
Random surface only; predict the Button press-time distributions (2 396 trials, only
0.5% censored — participants essentially always press eventually, so the density is
well populated) allowing the single paradigm shift δ, which per the cross-paradigm
check should absorb the known excess of early pressing at intermediate criticality
(+0.26 at TTC6). Whether δ acts on the level or on the rate is decision 3 of the ch. 11
list; the press-time *shape* distinguishes them, which is why it should be fitted both
ways and compared rather than assumed.

**Then transfer.** Fit on cut-in, predict LTAP, cyclist overtake and truck overtake with
every parameter unchanged. That is the falsifiable claim; the elliptical formulation is
the tracked fallback. The transfer scenarios need their own field construction first
(the cut-in loader mis-assigns roles outside its scenario — section 5).

## 3 Method recommendation

- **Estimation: MAP plus Laplace, in torch.** Write the joint log posterior as a torch
  scalar (the covariates are 18 numbers; the random effects are two vectors), optimize
  with L-BFGS, and take the Laplace covariance at the mode for intervals. CPU-torch on
  this machine handles this size trivially. No PyMC or Stan is installed, and nothing
  here needs them; if full posteriors are ever wanted, a hand-rolled NUTS is not worth
  it — the honest upgrade is installing numpyro, and the model is small enough that
  the choice can be deferred.
- **Validate the machinery on synthetic data first**: simulate responses from known
  c_i, b_i, σ, refit, and confirm recovery — the property-test discipline applied to
  the fitting code. This also calibrates how much the C1 cells actually constrain b.
- **Uncertainty conventions carry over** from the equivalence work: report intervals,
  compare conditions as differences with all variance sources resampled, and state
  what is fixed.
- **Identifiability, stated up front**: the pair (c, σ) is identified only relative to
  the field's scale, which depends on the structural flags — levels are comparable
  only between runs with the same flags. Motor latency is not identified by this
  design at all (fix at a literature 0.2–0.3 s or absorb; ch. 11). The paradigm term
  δ is a combined modality-plus-order effect and must be named as such.

## 4 Which axis the boundary lives on: deficit level or allowed deceleration

Two covariates are carried side by side (`czb_data`):

- `deficit_max` — the level-on-the-field reading: one scalar c per driver on the
  preference field. Pilot: correlation 0.90 on the surface.
- `a_req_max` — the allowed-deceleration reading: a driver intervenes when the
  situation demands more braking than they accept. Pilot: correlation 0.73 as
  currently gated (the lane gate at the C1 boundary frame leaks for TTC8, visible in
  the cell table), so presently second — but it has a property the deficit lacks: the
  mild truck cut-ins produce **zero dread-field deficit through most of the response
  window** (`docs/lane_entry_note.md` §5) while a_req grades smoothly there. If truck
  participants press at rates a bias term cannot absorb, the deficit-level model fails
  on trucks and the deceleration axis (equivalently, the comfort field at a lower
  allowed deceleration) becomes necessary rather than optional.

Our recommendation: fit stage 1 on `deficit_max` as the primary (it is the scalar the
CZB claim is about), run the truck cells as the internal check, and keep the
deficit-family-over-allowed-deceleration refinement in reserve. This is a place where
the data should be allowed to overrule the framing, and the check is cheap.

## 5 What is built, and what remains before the fit

Built and verified today: trace loading with corrected onset detection, the continuous
field, `random_cutin_trials()` (3 096 trials, 43 participants, covariates verified
monotone across C2–C6), `button_cutin_trials()` (2 396 trials, press times on the
time-since-onset axis, medians ordered by criticality: TTC4 0.36 s → TTC8 1.8 s), and
the stage-0 pilot. The response surface reproduces the study's documented table.

Remaining, in order: (1) the synthetic-recovery harness; (2) the stage-1 torch model;
(3) truck cut-in trials added to the table (loader handles them; they were left out of
the pilot to keep it to the documented 3 × 6 surface); (4) the accumulator layer;
(5) field constructions for the three transfer scenarios — LTAP needs a crossing
geometry (the cut-in x_tar convention is meaningless there), and the overtake/
truck-lateral traces need role assignment by instructed-vehicle rather than by lateral
span, which mis-assigns both (review finding, 2026-08-27).

## 6 Questions for Jonas before stage 1 runs

1. Bias per driver with shrinkage, or one group-level bias? (We lean hierarchical with
   strong shrinkage; the C1 data is thin either way.)
2. Is the braking-expectation question (`CZB_2`) confirmed as *expected required
   braking* — the reading under which it identifies the dread level — rather than the
   participant's own intended action? The two designs word it differently and the
   fitting treats only the Random version as ordered.
3. Any objection to fixing motor latency at a literature value rather than absorbing
   it into c? It changes nothing for percentiles, only for absolute levels.
4. The Sequence design stays excluded (autocorrelation), per decision 8 — confirm this
   still stands now that it would add three more cut-in stimuli.
