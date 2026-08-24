# Crash causation with an active-inference response process: method and first results

Results document, 2026-08-24. Prepared by Claude at the request of Jonas Bärgman. Markdown
is the source; Word and PDF are generated from it. This document reports what has been
*found*; the design, the reading notes on the source papers, and the protocol live in
`docs/crash_causation_plan.md` and are only summarized here. Provenance tags as elsewhere:
[B24] Bärgman, Svärd, Lundell & Hartelius (2024), [W25a] [W26] the Wu et al. papers,
[Code] the Schumann et al. released code, [OSF] their deposit, [Repo] this repository,
[Opinion] a judgment.

---

## 1 The method in one page

The question: can the active-inference driver model serve as the *response process* inside
a crash-causation model — and what does it add or cost relative to the fixed-delay response
of the crash-causation model (CBM) of [B24]?

The construction, following the plan:

- **Seeds.** 100 rear-end pre-crash scenarios sampled weight-proportionally (stratified by
  initial speed) from the 5 000 synthetic QUADRIS scenarios of [W25a]; every seed carries
  its real-world weight ω.
- **Causation components** ([B24]'s four mechanisms, each switchable): off-road glances
  (duration distribution + a placement rule), too-close following (inherent in the seed),
  a maximum-deceleration cap, and a post-hoc no-response mixture (10% of crashes).
- **Two response processes** behind one interface: the CBM's (respond 0.5 s after eyes
  return to the road; ramp to the drawn deceleration) and a tier-1 surrogate of the active
  inference driver (the model's own preference function evaluated on the seed kinematics,
  fed through its evidence accumulator with the drift rate calibrated on the authors' 896
  deposited trials — the calibration reproduces 69% of the closed-loop brake onsets within
  ±0.2 s [Repo]).
- **Conditions.** A: attentive active inference, no glances (the benchmark). B: active
  inference + all components. C: CBM response + all components (the control — a
  near-relative of the QUADRIS generator). D: active inference + glances only.
- **Per-seed bin sweep** instead of Monte Carlo (the [B24] design): each seed is run
  through every glance bin and every deceleration bin; outcomes carry the bin
  probabilities, so each seed yields a crash *probability*, and avoided outcomes are
  first-class results.
- **Comparison** against the full 5 000-scenario reference with the practical-equivalence
  framework of [W26]: quantile-binned statistics θ (worst bin) and Θ (aggregate), ROPEs
  0.10 and 0.05, bootstrap HDIs; crashes weighted by [W26] Eq. 10, plus an exposure-weight
  variant that divides out each seed's crash probability (plan §6b).

Everything below uses the **digitized real distributions** of section 2, not the earlier
parametric stand-ins; the stand-in results are kept in `replication/causation/out/`
(untagged files) for comparison.

## 2 Input distributions, digitized from the published figures

The SHRP2 data behind [B24] are not shareable, so the two input distributions were
digitized from the published figures (`replication/causation/digitize_b24.py`; outputs in
`replication/causation/data/`):

- **Off-road glance durations** ([B24] Fig. 1, SHRP2 baseline): the figure is vector art,
  so bar geometry is exact. Two independent calibrations of the value axis — tick-label
  geometry and the requirement that the drawn (off-road-conditional) distribution sum
  to 1 — agree within 0.9%. The drawn bins extend to 3.75 s; the published longest glance
  is 6.7 s, so a small tail (below the figure's resolution, < 0.001 per bin) is truncated.
  The on-road point mass is 0.80 (the figure's broken-axis tick; the caption states the
  CDF "would start at that value").
- **Maximum decelerations** ([B24] Fig. 3, 45 SHRP2 crashes, 1.5 m/s² bins): digitized
  from pixels and forced to integer counts — 6, 11, 12, 11, 4, 1 across bins from 3 to
  12 m/s², which sum to exactly the paper's n = 45.

![Digitized input distributions against the earlier stand-ins](causation_figures/fig_inputs.png)

The figure shows both against the stand-ins used before today. The glance stand-in was
close (its mode sits ~0.2 s early); the deceleration stand-in was not — the real
distribution has substantially more mass at hard braking (24% at 7.5 m/s² and above,
where the stand-in had almost none). This matters below.

## 3 Crash generation

| condition | response | components | seeds crashing (any bin) | weighted crash prob | avoided seeds |
|---|---|---|---|---|---|
| A | active inference | decel. cap | 23/100 | 0.008 | 77 |
| B | active inference | glances, decel. cap, no-response | 100/100 | 0.012 | 0 |
| C | CBM (control) | glances, decel. cap, no-response | 85/100 | 0.003 | 15 |
| D | active inference | glances, decel. cap | 100/100 | 0.012 | 0 |

With the renewal-process glance placement (plan §6c; the default for the active-inference
conditions): C 0.003 (51/100 seeds), D 0.021 (96/100).

Findings:

1. **An attentive active-inference driver avoids 77 of 100 QUADRIS crash seeds** across
   the full real deceleration sweep (up from 51 with the stand-in distribution — the real
   distribution's harder decelerations avoid more). The 23 that still crash in some bin
   are the kinematically hard core.
2. **The response process drives a factor ~4 in crash probability**: B (active inference)
   0.012 versus C (CBM) 0.003 with identical causation components. The mechanism is
   timing: the active-inference accumulator responds at a median of 1.25 s after the
   τ⁻¹ = 0.2 s⁻¹ anchor (IQR 0.55–1.90 s), where the CBM responds at a fixed 0.50 s
   (section 5).
3. The no-response mixture (B versus D) barely moves the aggregates at its 10% share, as
   expected from its post-hoc construction.

## 4 Comparison with the original data

### 4.1 Summary statistics

Weighted medians (weighted mean for P_inj); reference weighted by ω, conditions by the
Eq. 10 crash weights:

| | lead delta-v [m/s] | mean P_inj (MAIS2+) | t_nr [s] | follower a_min [m/s²] |
|---|---|---|---|---|
| QUADRIS reference (n = 5 000) | 1.77 | 0.0062 | −0.15 | −1.03 |
| B: active inference | 0.75 | 0.0036 | −0.10 | −3.46 |
| C: CBM control | 1.05 | 0.0040 | −0.15 | −3.75 |

### 4.2 Distributions

![Weighted metric distributions: reference vs conditions B and C](causation_figures/fig_metrics.png)

The three panels carry the substance:

- **Severity (lead delta-v, left).** Both response models over-produce mild crashes
  (density 0.55–0.70 in the lowest bins against the reference's 0.24) and under-produce
  the moderate 1–5 m/s range. The bin sweep generates many marginal crashes — a glance
  just long enough, a deceleration just too weak — whose delta-v is small.
- **Urgency (t_nr, middle).** The distributions essentially coincide — the time of no
  return is a property of the seeds more than of the follower, and both models inherit it
  correctly.
- **Braking (follower minimum acceleration, right).** The structural mismatch. The
  reference's crashing followers concentrate at **zero braking** (the [W25a] generator's
  non-responding and abnormal-acceleration followers) with a smooth spread of moderate
  braking; the generated crashes instead brake hard at the discrete cap values (the
  spikes at the [B24] bin centers). In words: **QUADRIS crashes are mostly drivers who
  barely braked; the CBM-style construction generates drivers who braked hard but too
  late.** Both routes end in a crash; they are different kinds of crash.

### 4.3 Equivalence statistics

No condition is practically equivalent to the reference on any metric (ROPE 0.10 for θ,
0.05 for Θ; full tables in `replication/causation/out/summary_real.md` and
`summary_real_process.md`). Headline θ with 95% bootstrap HDIs, Eq. 10 weights:

| condition | glance placement | P_inj | t_nr | a_f,min |
|---|---|---|---|---|
| A | — | 0.62 [0.47, 1.07] | 0.42 [0.26, 1.00] | 2.42 [1.85, 2.96] |
| B | anchored overshot | 1.44 [1.39, 1.58] | 0.66 [0.58, 0.75] | 1.00 [1.00, 1.04] |
| C | anchored overshot | 0.81 [0.74, 0.89] | **0.36 [0.26, 0.44]** | 1.96 [1.90, 2.05] |
| C | renewal process | **0.40 [0.34, 0.50]** | 0.37 [0.27, 0.52] | 2.03 [1.92, 2.15] |
| D | renewal process | 1.19 [1.10, 1.39] | 0.60 [0.52, 0.70] | 1.08 [1.00, 1.18] |

How to read this:

- **t_nr comes closest to equivalence** (θ 0.26–0.75 against a ROPE of 0.10) for every
  condition — consistent with panel 2: the seeds carry this metric.
- **The best severity match is the CBM control with process glances** (P_inj θ = 0.40),
  which is expected — it is the nearest relative of the generator — and useful: it
  calibrates how much of the remaining distance is attributable to the framework
  (seeds, weighting, digitized inputs) rather than to the response model. The active
  inference conditions sit at θ 1.2–1.5, roughly three times the control's distance.
- **a_f,min fails structurally for every condition** (θ 1.0–2.4). This is the panel-3
  mismatch, and no response-timing change can fix it: it comes from generating crashes
  through the low-deceleration mechanism while the reference generates them mostly
  through non-response. Under the exposure weighting (plan §6b) every θ roughly doubles,
  as the crash-conditioned seed set is up-weighted toward its rarely-crashing members.

One methodological note carried over from the stand-in runs and confirmed here: the
choice of glance placement moves the equivalence result more than the choice of duration
distribution — crash-anchored placement inflates crash probability about four-fold for
the CBM without degrading θ, so the equivalence test alone would not catch that bias
(plan §11.3).

## 5 Response timing: the two models differ exactly where it matters

![Attentive brake onsets relative to the anchor](causation_figures/fig_timing.png)

The CBM's response rule is a fixed 0.5 s after the τ⁻¹ = 0.2 s⁻¹ anchor [B24, from
Markkula et al. 2016]. The active-inference accumulator, calibrated only on the authors'
own closed-loop trials and never on QUADRIS, produces onsets at a median 1.25 s after
that same anchor with a wide spread (IQR 0.55–1.90 s) — later and far more variable. The
distribution is stable across glance placements and across the stand-in versus real
distributions, because attentive timing does not involve the glance machinery at all.
Which rule is right for human drivers is an empirical question the two models now pose
crisply; the CBM's 0.5 s is itself empirically anchored, so the active-inference
surrogate's later median is a genuine, testable disagreement, not an error [Opinion].

## 6 The closed loop is not the CBM with extra steps: the glance-gate finding

The tier-2 adapter (plan §11.4) runs the authors' full closed-loop model on QUADRIS seeds
with the lead replaced by a replay of the seed's speed profile, and can force off-road
glances through the code's own observation gate (`I_factor`, the mechanism of the
Engström et al. 2024 visual time-sharing model).

**Forcing a 1.0–3.0 s off-road glance during the conflict did not delay the response.**
On the test seed the driver braked at 2.4–2.6 s — inside the glance — and it did so both
under the shipped observation-noise factor (3) and under an effectively total gate
(factor 1000). The reason is architectural: the lead's braking had been registered before
the glance began, and during the glance the belief cloud coasts forward on its own
norm-shaped prediction, so the evidence accumulator keeps filling from *remembered and
extrapolated* evidence. Looking away blocks new observations; it does not stop inference.

The CBM assumes the opposite: no information accumulates while the eyes are away, and no
response can begin until 0.5 s after they return [B24]. The two architectures therefore
make **divergent, testable predictions** that depend on glance timing:

- glance covering the conflict onset → both models delay the response until (or beyond)
  eyes-return; they roughly agree;
- glance beginning *after* the onset has been registered → the CBM still waits for
  eyes-return + 0.5 s, while the active-inference driver responds mid-glance on
  extrapolated evidence.

Naturalistic glance-conditional response data could separate these — drivers who brake
while still looking away (or within less than 0.5 s of looking back) in late-glance
conflicts would favor the active-inference account. To our knowledge the existing
glance-response literature conditions on eyes-off at onset and does not isolate the
late-glance case [Opinion]. The tier-1 pipeline mirrors this distinction explicitly: its
evidence gate at weight 0 reproduces the CBM assumption, the Svärd et al. partial
looming weight is an intermediate, and the tier-2 precision gate is the full
active-inference behavior.

An incidental observation from the same runs, on four repeats only: the hard gate
produced *fewer* crashes than the mild one (0/4 versus 2/4) — a warning against assuming
that gate strength maps monotonically onto risk, not a result.

## 7 What we conclude so far

1. The pipeline delivers what it was designed to deliver: switchable causation
   components, two response processes behind one interface, per-seed crash
   probabilities, and the full [W26] equivalence readout against the 5 000-scenario
   reference — now with digitized real input distributions.
2. Substantively, the active-inference response is slower and more variable than the
   CBM's fixed rule, quadrupling the generated crash probability under identical
   causation components; and the whole CBM-style construction — under either response
   model — produces a crash *population* that differs in kind from QUADRIS's, whose
   crashes come predominantly from non-braking followers rather than late-but-hard
   brakers. Equivalence in the [W26] sense is not close for any condition; the
   near-generator control (θ 0.40 at best) bounds how much of that distance the
   framework itself accounts for.
3. The architecturally interesting result is section 6: evidence gating versus
   inference gating during off-road glances is a real, behaviorally testable difference
   between the CBM and active inference, discovered by running both — it was not
   visible in either paper alone.

## 8 Limitations and next steps

- The glance and deceleration distributions are digitized from published figures; the
  actual SHRP2 bins would remove the (small) digitization error and restore the
  truncated glance tail. The deceleration distribution's provenance caveat from [B24]
  stands: it comes from 45 low-severity SHRP2 crashes.
- The QUADRIS reference is itself model-generated; equivalence with it is equivalence
  with that generator ([W25a]), and the exposure critique (plan §6b) is only mitigated,
  not resolved, by the reweighting. The pre-filter scenario set remains the most
  valuable single ask.
- Tier-1 timing is a surrogate; the tier-2 smoke test supports it within 0.1–0.9 s in
  the calibrated speed range, but the 20-seed tier-2 comparison (plan step 7) has not
  run yet, and the low-speed third of QUADRIS needs the desired-speed convention
  decision before tier 2 covers it.
- n = 100 seeds; the tier-1 cost (~5 s per seed) permits the full 5 000 whenever the
  tier-2 gate is passed.

Regeneration: `replication/causation/run_quadris.py --n-seeds 100 --conditions A B C D
--tag real --glance-csv replication/causation/data/b24_fig1_glances_shrp2.csv
--decel-csv replication/causation/data/b24_fig3_decel.csv`, then
`replication/causation/make_results_figures.py --tag real`, then
`docs/build_pdf.py docs/crash_causation_results.md`.
