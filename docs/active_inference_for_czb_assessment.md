# An honest assessment: active inference as the basis for CZB quantification

*2026-08-27, written at Jonas's request, ahead of discussing the fitting-plan questions.
This is an opinion document; where it states judgments they are mine and hedged as such.
Numbers are from this repository's committed analyses
(`replication/czb/pilot_surface_fit.py` and the comparison run recorded in section 3;
`replication/causation/`; `notes/05_validation.md`).*

## 0 The verdict in one paragraph

As I read the evidence, the active-inference route is a **well-posed, falsifiable, and
currently promising research program** for quantifying comfort-zone boundaries — the
first human-data contact (a two-parameter threshold on the zero-refit field reproducing
the 18-cell cut-in response surface with correlation 0.90) is genuinely encouraging —
but its distinctive value is **not yet demonstrated**, because that value lives entirely
in the cross-scenario transfer claim, which is untested. Within a single scenario the
field is beaten by a trivial scenario-specific regression (section 3), so the method
must stand or fall on what the regression cannot do: carry one interpretable number per
driver across scenarios. For the ADAS-triggering purpose specifically, my feeling is
that the framework is the right *shape* for the problem (one dial, percentile semantics,
decomposable triggers, cheap online evaluation) while being some distance from a
deployable recipe: the fitted level absorbs paradigm and latency offsets that matter for
absolute trigger timing, the field's location depends on stated conventions, and the
population behind any percentile is presently 43 crowdsourced participants. The honest
unique selling point is not "active inference" as a brand — most of that machinery is
switched off in our use — but the **dual role of one quantity**: the same scalar whose
accumulation explains *when* drivers act is the scalar whose level set *defines* the
boundary. No conventional indicator has that property, and it is testable.

## 1 What is actually being used, against what the label suggests

"Active inference" names a large theoretical stack. The CZB method deliberately uses a
thin slice of it, and it seems to me important to be plain about which slice, because it
determines what a skeptical reviewer can and cannot attack.

| component of the full framework | used for CZB? | role in our method |
|---|---|---|
| preference distribution p(o) | **yes — central** | the comfort-zone field is its pointwise residual information; the boundary is a level set |
| residual information (surprise family) | **yes** | turns log-preference into a non-negative scalar with a true zero ("comfortable" = 0) |
| evidence accumulation on pragmatic value | **yes (stage 2)** | links the field to response *timing*; Markkula-style, not uniquely active-inference |
| expected free energy planning, policy search | no | the field method is deliberately rollout-free; that is what makes it cheap |
| epistemic value / information seeking | no | α = 0 in the validated configuration; the gaze half is unexercised |
| belief updating, state estimation | no | the field is evaluated on observed kinematics directly |

Two consequences. First, a fair description of our method is "a satisficing preference
field with an accumulator, inherited from a validated active-inference driver model" —
the theory supplies the *specific calibrated form* and the connection to a model that
also produces closed-loop behavior, not the day-to-day machinery. Second, the criticism
"you could do this with a hand-designed cost function" is, as I read it, technically
true and practically empty: we would then have to invent the cost function, and the
whole point is that this one arrives pre-shaped and pre-calibrated by someone else's
behavioral validation, with its parameters documented and its response-timing
predictions testable on the same data. The convergence with the QUADRARUM document's
definition of the CZB — the point where the satisficing condition is violated — is
real: a preference distribution *is* a specification of acceptable outcomes.

## 2 The evidence ledger, as it stands today

| claim | evidence | my reading of its strength |
|---|---|---|
| the field recovers response onsets from kinematics alone | median onset error 0.0 s against the authors' OSF deposit (n = 896, score 0.855) | strong, but model-recovering-model — no human in the loop |
| the field explains a human response surface | stage-0 pilot: 2-parameter probit, corr 0.90 / RMSE 0.125 on the 18-cell cut-in surface | encouraging first human contact; see section 3 for the honest context |
| the response process is behaviorally right | crash-causation study: active-inference conditions closer to the QUADRIS reference than the CBM control (severity θ 0.148 vs 0.209, P ≈ 0.97; braking aggregate 0.3% vs 35%) | moderate; supports the *response model*, and severity constrains timing only weakly (severity-vs-timing dissociation) |
| one scalar transfers across scenarios | — | **untested; this is the load question** |
| the field expresses graded caution in mild events | mild truck cut-ins: dread-field deficit exactly zero through the response window | **negative** as it stands; the comfort level (allowed deceleration below capability) is required to fix it |
| the paradigms measure one latent process | fixed-clip CDF vs button density agree within 0.06 at high criticality; +0.26 excess early pressing at intermediate | mixed; consistent with one process plus a shift, but the shift is real and confounded with order |

## 3 The uncomfortable comparison, run rather than assumed

If the field is only a repackaging of kinematics, a kinematic baseline should match it.
I fitted probit models to the same 18-cell surface (3 096 trials) at matched or nearly
matched parameter counts:

| model | parameters | RMSE | corr |
|---|---|---|---|
| **comfort-zone field (running max), threshold + noise** | 2 | **0.125** | **0.903** |
| TTC at clip end | 2 | 0.185 | 0.764 |
| 1/TTC at clip end | 2 | 0.175 | 0.792 |
| gated required deceleration (running max) | 2 | 0.203 | 0.727 |
| nominal TTC + exposure time (design variables) | 3 | 0.081 | 0.960 |
| 1/TTC at end + exposure time | 3 | 0.073 | 0.968 |

*(Addendum, same evening: Jonas asked whether this comparison is in-sample. The table
above is; the check has now been run held-out, and the conclusion survives. Under
leave-one-criticality-out cross-validation — fit on two criticality levels, predict the
third — the field gives out-of-sample corr 0.864 / RMSE 0.147 against the design
regressions' 0.934–0.949 / 0.097–0.108, and leave-one-timepoint-out gives the same
picture. The regressions genuinely generalize better within this scenario; overfitting
is not what made them win. Committed in `replication/czb/pilot_surface_fit.py`.)*

Three readings, in decreasing comfort:

1. **The field beats every single kinematic scalar at equal parameter count.** Plain
   end-TTC cannot explain the surface (it thinks a C1 clip at TTC 4.0 is more dangerous
   than a C6 clip at TTC 4.5, and drivers say the opposite), because the response
   depends on the developing lateral geometry — which is exactly what the field's
   lane-entry structure integrates. To rescue TTC one must gate it by lane relevance,
   and by then one has rebuilt the field's safety term by hand.
2. **A scenario-specific regression on the design variables beats the field.** One extra
   parameter and an explicit time term give 0.96. This is not embarrassing — a
   regression fit to *this* scenario's design axes cannot transfer, predicts nothing
   outside its grid, and its coefficients mean nothing — but it disciplines the claim:
   the field cannot be sold on within-scenario fit. Its case is that its *threshold* is
   one portable, interpretable number, where the regression's coefficients are neither.

   *[Sharpened 2026-08-28. This was understated. In the study-1 cut-in design relative
   speed is constant across all 18 cells, so correlation(gap, TTC) = 1.0000 — the
   longitudinal dimension has one degree of freedom, and the field's 0.90 is equally
   consistent with a driver thresholding the gap. The second cut-in study breaks the
   collinearity over a six-fold range of gap and rules against the field's kinematic
   core: gap orders the response at ρ −0.887, TTC at −0.807, required deceleration at
   +0.238 (`replication/czb/out/cutin2_scope.md`). So the field cannot be sold on
   within-scenario fit for a stronger reason than this paragraph gave — it has not yet
   been shown to beat the simplest alternative on a design that could tell them apart.
   That test is task 1 of review gate R.2. What is *not* affected is the portability
   claim, which has independent support: about 69% of the reliable per-driver signal is
   shared across all four scenarios, measured without any field
   (`out/cross_scenario_consistency.md`).]*
3. **The gap is the accumulator's signature.** Most of the baseline's advantage comes
   from the exposure-time term (TTC alone 0.76 → 0.96 with time added). The static
   threshold cannot express "probability of having responded grows with time at a
   given criticality"; the accumulator exists to express exactly that, without adding
   per-scenario parameters. My expectation — falsifiable, stage 2 — is that field +
   accumulator closes most of this gap; if it does not, that is evidence against the
   framework worth taking seriously.

   *[Decided 2026-08-27 at review gate R.1: the expectation was wrong — the verdict is
   FAIL, and it is quotable. Three structurally-argued accumulator variants (noise from
   clip start; noise gated at onset; gated with a free trial-level threshold spread)
   all fit worse in sample than the stage-0 static probit (best 0.178 vs 0.125), and
   the final variant's held-out RMSE 0.267 fails the pre-registered ≤ 0.11 rule
   (`replication/czb/out/stage2_summary.md`; v1/v2 records in `out/log_stage2*.txt`).
   The named structural reason: criticality-graded responding already at C1–C2, where
   at most 0.05–0.15 s of post-onset evidence exists under any plausible motor latency
   — anticipation from repeated stimulus exposure, inexpressible by any evidence-gated
   integrator — plus a late-cell criticality gradient shallower than integrated
   evidence implies. Time-integration of the deficit does not close the within-scenario
   gap on this stimulus set; the framework's remaining case is portability (the stage-B
   transfer gate) and threshold interpretability, exactly as §3.2 anticipated.]*

## 4 What the route genuinely buys, if the transfer test passes

- **A one-dimensional population.** The percentile question ("trigger where 80% of
  drivers would already be uncomfortable") becomes well-posed without an ellipse,
  because the field has already absorbed speed, gap, closing rate and lateral position
  into one number. The multivariate conjunction problem the QUADRARUM document works
  through is dissolved rather than solved.
- **The dual role.** The same scalar defines the boundary (level set) and predicts
  response timing (accumulation). A TTC threshold does not predict *when* in a
  developing event a driver acts; this does, and the button data tests it.
- **Decomposable triggers.** Exceedance attributes to named terms (speed, clearance,
  counterfactual braking), which matters for explaining an ADAS intervention to an
  engineer, a regulator, or a driver.
- **Cheap online evaluation.** The field is closed-form in observables; no rollouts. It
  could run in a vehicle at trivial cost, unlike the full closed-loop model (~18 s CPU
  per simulated step).
- **A benefit-estimation synergy.** The crash-causation machinery in this repository
  can, in principle, estimate the *safety* consequence of any candidate trigger placed
  on the field — the two workstreams compose into "set the trigger by comfort
  percentile, audit it by counterfactual crash outcome", which neither piece does
  alone. To me this composition is one of the strongest practical arguments for
  keeping both on the same scalar.

## 5 The case against, stated as risks with severities

1. **The transfer claim may simply be false** (severity: decisive; probability: real).
   Drivers may not carry one level across scenario types — the instruction differs by
   scenario in our own data (intervene / abort / yield), and handbook ch. 04 already
   flags that pooling these under one scalar is the likeliest way to manufacture a
   false negative. The fallback (elliptical joint percentile on conventional
   observables) is tracked, which is the right structure: failure would be a finding,
   not a dead end.
2. **What transfers is the threshold, not the work** (severity: moderate, chronic).
   Every new scenario needs its field construction — geometry, norms, observation
   conventions. The very first new scenario (cut-in) required a structural
   modification to the preference function, argued but still a modification made
   before any fitting; LTAP will need a crossing geometry; the overtake traces need
   role assignment rebuilt. "One scalar, no per-scenario engineering" is not the true
   position; the true position is "bounded, principled, parameter-free per-scenario
   construction with a shared threshold", and it should be stated that way.
3. **The fitted level is not the boundary** (severity: moderate for percentiles, high
   for absolute triggers). c_obs = c_true + bias + paradigm + latency. The design
   identifies some components (C1 for bias, framing contrast) and not others (motor
   latency, unidentified; the paradigm term is confounded with order). Percentiles
   largely survive because the offsets are shared; an absolute trigger time does not
   — 0.2 s of unmodeled latency is 6 m at highway speed.
4. **The field's location rests on stated conventions** (severity: moderate,
   manageable). The assumed worst case a_OV,min, the reaction budget t_react, and the
   capability a_max move the boundary substantially — at 20 m/s the comfort-to-dread
   span (allowed deceleration 4 vs 8 m/s²) is a time-headway range of 1.86 s down to
   0.61 s, a factor of three. The project's standing rule (never quote absolute
   boundaries without stating them) applies to any deployed threshold verbatim.
   Freezing them across scenarios is part of the claim under test; tuning them per
   scenario would readmit the multivariate problem through the back door.
5. **Hard zeros below the counterfactual threshold** (severity: high if unaddressed;
   fix identified). The dread field is exactly silent for the mild truck cut-ins while
   humans plausibly still respond. An ADAS triggered on that field would never fire on
   mild-but-uncomfortable events. The comfort-level formulation (allowed deceleration
   below capability) exists precisely for this; the fitting plan's section 4 makes the
   truck cells the internal check. If drivers' responses there turn out to need a
   different *shape*, not just a lower level, that would be structural evidence
   against the field.
6. **Provenance** (severity: low-moderate, documented). The preference function follows
   the authors' released code, which deviates from its own supplementary information
   in 13 documented ways, and the paper's worked example does not match its deposit.
   We build on the implementation that generated the validated results — the right
   choice, I think — but a safety-adjacent application inherits that provenance and
   should say so.
7. **Population and paradigm** (severity: high for deployment, low for the research
   question). Any percentile from this data describes 43 crowdsourced participants
   watching clips, with a demonstrated satisficing excess (+0.26 at intermediate
   criticality) in one paradigm. This supports method development, comparisons and
   contrasts; it does not support setting a fleet trigger.

## 6 Specifically as a way to place an ADAS trigger

The end-to-end pipeline would be: fit c per driver → population distribution of c →
choose a percentile → the trigger surface is that level set of the field, evaluated
online. Where I would concentrate skepticism, in order:

1. **The percentile choice dominates.** Moving the percentile moves the trigger far
   more than most estimation errors will; the sensitivity of the implied trigger
   timing to the percentile (and to the comfort-versus-dread level choice) should be
   quantified *before* investing further in estimator refinement, because it may show
   that a cruder estimate suffices — or that no defensible percentile gives a usable
   trigger. This is cheap to run once stage 1 exists.
2. **Comfort is an acceptance criterion, not a safety criterion.** A CZB-percentile
   trigger answers "when would most drivers already want regulation", which is the
   right question for nuisance and trust, and only indirectly a safety question. The
   QUADRARUM document's observation that measured thresholds and CZB-based ones may
   differ by only ~0.1 s suggests the two may nearly coincide in practice, but that
   is a hypothesis to check — and the causation machinery here can check it, by
   scoring candidate triggers against counterfactual crash outcomes on the QUADRIS
   ensemble.
3. **Absolute timing inherits every offset in risk 3.** For a comparative use (rank
   situations, adapt sensitivity between drivers) the route is already fairly solid;
   for an absolute "fire now" threshold the latency and paradigm terms must be fixed
   externally, and the honest statement is that this design cannot identify them.

## 7 Bottom line, and what would change my mind

My overall position: **worth pursuing, with the transfer test as the gate, and worth
describing more modestly than "active inference for CZB"**. The within-scenario
evidence says the field is a good — not the best — single predictor, distinguished by
interpretability, portability claims, and its link to response timing rather than by
raw fit. The framework earns its keep if and only if (a) the accumulator closes most
of the within-scenario gap without per-scenario parameters, and (b) a level fitted on
cut-in predicts the other three scenarios better than chance and comparably to
per-scenario refits. If both hold, this is, to my knowledge, the first
one-dimensional, testable, driver-population CZB — a real contribution. If (b) fails,
the elliptical formulation on conventional indicators is the honest fallback and the
field reverts to being one indicator among several. Concretely decidable, on data we
already hold, within the current fitting plan — which is, I think, the strongest thing
that can be said for it.
