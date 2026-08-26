# Setting the practical-equivalence ROPE: a calibration note

*Written 2026-08-26 for the WaymoActiveInference project. Intended both as internal
guidance and, after Jonas's edit, as a note that could be sent to Jian Wu. It reports a
calibration of the [W26] binning/ROPE framework as applied to our crash-causation study,
and proposes explicit, derived ROPE thresholds and bin weights for our use case. Source
for the method: `external/OtherNonActiveInference/551989_Fulltext_practical_validation.txt`,
sections 2.1–2.4 and 3.3–3.4, read directly.*

## Summary of what this note argues

*Sections 2.5, 2.6 and 5 were revised on 2026-08-26 after Jonas took the outstanding
decisions. The headline changed: with the reference treated as the target population, the
ROPE is no longer below the noise floor and the verdicts become real statements about the
model. Earlier sections are kept as the record of how that conclusion was reached.*

1. As we originally applied it — uniform bin weights, a defective bootstrap, and five bins —
   the pair (θ ≤ 0.10, Θ ≤ 0.05) sat at or below the noise floor of the reference, so a
   model that is exactly right failed much of the time. **This has since been resolved**
   (points 6–7).
2. The strictness came from choices made *around* the thresholds — how the reference was
   resampled, the **bin count**, and the fact that uniform weights place every bin at the
   framework's baseline weight, which is anchored to a much more severe crash population
   than ours.
3. **Both thresholds can be derived** from a stated tolerance on the injury-weighted
   aggregate rather than inherited (section 3). A 10% tolerance gives θthd = 0.188 and
   Θthd = 0.089; a 5% tolerance gives (0.094, 0.045), which is almost exactly Wu's
   published pair — so their values are coherent, just calibrated to a stricter target
   than ours needs to be.
4. **Choosing the weight anchor P0 is mathematically the same act as choosing the θ
   threshold** (section 4.1). They are one knob, not two. Since the weight *shape* moves
   θ by only 7% on our data, uniform weights plus an explicit threshold is the
   recommendation — no system under assessment is needed, and building one would not help.
5. **Correction to an earlier version of this note**: θ and Θ do *not* bound the error in
   a weighted aggregate. They constrain between-bin allocation only. Condition B's actual
   mean injury risk is +12.6% against the reference while its binned approximation is
   −2.7%, the gap sitting almost entirely in the open-ended top bin (section 3.2). The
   aggregate is now reported directly alongside the verdict.
6. **Decision taken: the reference is the target population** (§2.5). The 5 000 QUADRIS
   scenarios define the ensemble the comparison is about, so only the synthetic side carries
   sampling error. This drops the noise floor from 0.177 to about **0.021** at N = 5 and
   makes every candidate threshold usable. The condition attached is that claims must name
   the ensemble and must not generalize to the fleet. Under this configuration condition B
   still **misses** practical equivalence at a 10% tolerance — θ = 0.148 [0.110, 0.204]
   against θthd = 0.188, failing on the interval's upper end rather than the point estimate
   — but it now misses against a criterion the reference can resolve.
7. **Decision taken: severity stays operationalized as injury risk**, not as relative speed
   at impact, despite the latter being the assumption-free primitive (§5.3). The convexity
   that makes injury risk look worse in aggregate is the metric correctly reporting that
   tail errors matter for harm.
8. **Position taken on the general problem** of a noise floor exceeding an acceptable
   tolerance (§2.6): report the floor, try to lower it before raising the threshold, and if
   it still binds, raise the threshold to the floor and say so — because a tolerance finer
   than the study can resolve is a tolerance that needs revisiting.
9. Concrete proposals are in sections 5 and 6, with a paper-ready motivation in §5.1.

## 1 What the ROPE is, in plain terms

The framework asks whether a synthetic crash dataset can stand in for a reference one. An
ordinary significance test answers the wrong question: with enough data it will always
detect *some* difference, because no two distributions are exactly equal. An equivalence
test reverses this and asks whether any difference is **small enough not to matter**. The
ROPE — region of practical equivalence — is the written-down definition of "small enough".
Nothing statistical determines it; it is a domain judgment about what difference would
change a decision. [W26] is explicit on this point: the thresholds "should be set based on
expert judgment to reflect the relevance and priorities of the intended assessment".

The machinery makes "difference" precise:

1. **Cut the reference into N equal-weight slices.** Sort the reference crashes by severity
   and split into N = 5 bins each holding 20% of the weighted data. Bin 1 is the mildest
   fifth, bin 5 the most severe.
2. **Pour the model's crashes into those same bins.** A perfect model puts 20% in each.
   Our best configuration puts 17.4%, 20.5%, 21.2%, 22.9%, 18.0%.
3. **Summarize two ways.** θ is the *worst* bin measured relative to its proper share:
   bin 4 holds 22.9% where 19.9% belongs, an excess of 3.0 points, which is 14.8% of 19.9%,
   so θ = 0.148. Θ is the *total* misplaced share: 0.091.
4. **Weight the bins by how much they matter** (ω, section 4), and require the 95% HDI of
   each statistic to lie inside its ROPE.

Two intuitions are worth carrying. θ is a worst-case measure, dominated by whichever single
bin is worst, and it gets stricter as bins get finer. Θ is an aggregate and is exactly
**twice the total-variation distance**, so Θ ≤ 0.05 means the two distributions may
disagree about where at most 2.5% of the probability mass sits.

In one sentence for someone who has read none of this: *cut the real crashes into five
equally sized severity bands, check what fraction of the simulated crashes lands in each
band, and require that no band is off by more than 10% of its proper share.*

For our own result, the most concrete framing is: the model misplaces about **3 crashes in
every 100** relative to where the reference puts them on the severity scale, and the ROPE
as we applied it demands no more than **2 in 100**.

## 2 Is it hard to pass? Three calibrations

### 2.1 The null: compare the reference with itself

> **Superseded twice — read with §2.2b and §2.5.** The numbers below were produced with the
> defective bootstrap of §2.2b, which understated the spread, *and* under the reading that
> the reference is a sample, which §2.5 has since replaced. Under the project's settled
> convention the noise floor at N = 5 is about **0.021**, not 0.097. This section is kept
> because it is how the problem was found and because the *shape* of its conclusion — that a
> null calibration is the right diagnostic — still holds.

This was the decisive diagnostic. I drew a 5 000-scenario reference and a 103 857-case
"model" *from the actual QUADRIS severity distribution itself*, so the two are identical by
construction, and ran our own test on them.

| N | median θ | median 95%-HDI upper | pass rate (θ ≤ 0.10) | median Θ |
|---|---|---|---|---|
| 5 | 0.037 | **0.097** | **50%** | 0.021 |
| 20 | 0.129 | 0.266 | **0%** | 0.047 |

At N = 5 the HDI upper bound lands at 0.097 against a threshold of 0.10 — **a perfect model
passes about half the time**. At N = 20, which is what the bin rule (Eq. 4) prescribes for
a 5 000-scenario reference, it never passes. The same pattern holds on synthetic normal
data, so it is a property of the procedure rather than of QUADRIS: at n_ref = 200, the size
in the paper's own demonstration, the null pass rate is also 0%.

This reframes our headline. "Missing equivalence by a factor of 1.5" sounds like a model
deficiency; a substantial part of it is that we are asking a 5 000-sample reference to
resolve a difference it barely has the resolution to see.

### 2.2 What effect size does θ = 0.10 correspond to?

For a roughly normal reference cut into five quantile bins, with the model differing only
by a shift in location:

| difference | θ | |
|---|---|---|
| mean shifted 0.02 SD | 0.028 | passes |
| mean shifted 0.05 SD | 0.071 | passes |
| **mean shifted ~0.07 SD** | **0.10** | the threshold |
| mean shifted 0.10 SD | 0.146 | fails |
| spread 5% wider | 0.057 | passes |
| spread 10% wider | 0.111 | fails |

So θ ≤ 0.10 asks the model to match the reference to within about **a fourteenth of a
standard deviation**, or about 9% in spread. Cohen's conventional "small" effect is 0.2 SD,
three times what this tolerates. Our θ = 0.148 corresponds to roughly a 0.10 SD
discrepancy, which in most of behavioral science would be reported as a good match.

### 2.2b A defect in our own bootstrap, found 2026-08-26

Before the calibrations below can be read, one correction to our implementation. The
reference is weighted, and its weights are concentrated: the top 10% of scenarios carry 54%
of the total weight, so its **effective sample size is 950, not 5 000**
(ESS = (Σw)²/Σw²).

Our bootstrap drew reference *values* with probability proportional to weight and then
treated the resample as unweighted. That yields the precision of 5 000 *independent* draws
and therefore understates the spread by roughly √(n/ESS). The correct nonparametric
bootstrap for a weighted statistic resamples the **sampling units** uniformly and carries
their weights. Comparing the two on the actual QUADRIS severity distribution, for a model
that is exactly right:

| N | scheme | median 95%-HDI upper | passes θ ≤ 0.10 |
|---|---|---|---|
| 5 | resample values (what we did) | 0.075 | 100% |
| 5 | **resample cases (correct)** | **0.177** | **0%** |
| 10 | resample values | 0.124 | 0% |
| 10 | resample cases | 0.290 | 0% |
| 20 | resample values | 0.196 | 0% |
| 20 | resample cases | 0.495 | 0% |

The correct scheme gives intervals roughly **2.4 times wider**. `equivalence_test` now
defaults to `resample="cases"`; the old behavior is retained as `resample="values"` solely
to reproduce earlier numbers.

**What this changes and what it does not.** Point estimates of θ and Θ are unaffected, so
every comparison between conditions — the ordering that this study rests on — stands exactly
as reported. What changed is every HDI published before the fix: they were too narrow by
about a factor of two. The full-population outputs have since been regenerated.

**What it changed in the argument of this note**: under the *sample* reading of the
reference, the noise floor is worse than section 2.1 reported — about **0.177** at N = 5
rather than 0.097 — which would put the ROPE not merely at the resolution limit of this
reference but **below** it. Section 2.5 resolves this by settling the reading rather than
by adjusting the threshold.

### 2.3 What is the uncertainty actually over?

*This section poses the question; §2.5 answers it and records the decision.*

The bootstrap can resample **both** sides, treating the QUADRIS 5 000 as a sample carrying
its own sampling error, or only the synthetic side, treating the reference as the target
population — it is a fixed published scenario set, and we compare against all of it. The
difference under the null, at N = 5:

| what carries uncertainty | median θ under the null | 95% upper |
|---|---|---|
| reference resampled as a sample (cases) | 0.037 | 0.177 |
| reference fixed, synthetic side only | 0.009 | **0.021** |

That single choice is worth roughly an order of magnitude in effective strictness, and it is
a modeling judgment rather than a statistical one. It is settled in §2.5.

A related point: [W26] §2.1.3 computes θ and Θ on **posterior draws from fitted Bayesian
distribution models**, with leave-one-out model selection, not on a nonparametric
bootstrap. A parametric posterior borrows strength across the distribution and will be
materially tighter than our bootstrap. Our decision rule is therefore harsher than the
paper's on the uncertainty side.

### 2.4 The bin count we used was not the one the rule prescribes

Our full-population tables were produced with N = 5. That is the value Eq. 4 gives for a
100–200 scenario reference, which is the size the study had when the assessment code was
written, and it is the value used in the paper's own demonstration (n_ref = 200). At the
full population Eq. 4 gives **N = min(⌊5000/40⌋, 20) = 20**. Re-running the readout from
the stored condition-B outputs (`replication/causation/bin_sensitivity.py`, no
re-simulation needed):

| metric | B, N=5 | B, N=10 | B, N=20 | C, N=5 | C, N=10 | C, N=20 |
|---|---|---|---|---|---|---|
| severity (P_inj = v_rel) θ | 0.148 | 0.241 | **0.275** | 0.209 | 0.255 | **0.352** |
| severity Θ | 0.091 | 0.091 | 0.165 | 0.150 | 0.150 | 0.168 |
| t_nr θ | 0.419 | 0.636 | 0.636 | 0.460 | 0.623 | 0.699 |
| a_l,min θ | 0.314 | 0.314 | 0.786 | 0.254 | 0.254 | 0.591 |
| a_f,min θ | 1.058 | 3.983 | 3.983 | 1.380 | 2.165 | 4.456 |

Reassuringly, **the comparison our study rests on survives**: the active-inference condition
is closer to the reference than the CBM control on severity at every bin count, and on the
braking distribution at every bin count. At N = 10 and N = 20 the two conditions' HDIs
overlap substantially, so the ordering holds in point estimates without being statistically
separated there.

Two things follow. First, our reported numbers are indeed on the lenient side of the
paper's own prescription: severity θ nearly doubles at the prescribed bin count. Second,
and more importantly, **N = 20 is prescribed but unusable at this reference size** — the
null calibration above gives a perfect model median θ = 0.129 with an HDI upper bound of
0.266 at N = 20, so nothing can pass a ROPE of 0.10 there. The bin rule and the ROPE
threshold are jointly infeasible at n_ref = 5 000 under our decision rule. My reading is
that this is an argument for fixing the decision rule (section 5), not for adopting N = 20
and reporting a failure that the procedure guarantees in advance.

Two corrections to things I assumed before running this. **Θ is not bin-count invariant.**
It is a lower bound on twice the total-variation distance that becomes exact only as the
partition is refined, so it grows with N (0.091 → 0.165 for severity). **θ is biased upward
under resampling**, because it is a maximum over bins: at N = 20 the bootstrap HDI
[0.282, 0.554] does not even contain the point estimate 0.275. The bias grows with N, which
makes the "HDI upper bound inside the ROPE" rule doubly conservative at fine bin counts.

### 2.5 What the reference represents — the choice, and our decision

Sections 2.2b and 2.3 leave a question that has to be answered before any interval means
anything: **are the 5 000 QUADRIS scenarios the target set, or a sample from something
larger?** The two readings are both defensible, they are not a statistical question, and
they differ by an order of magnitude in the resulting intervals.

**Reading A — the reference is the target population.** The comparison asks what a given
driver model does *in these scenarios*. QUADRIS is a fixed, published scenario set; it is
the definition of the ensemble, in the same way that a benchmark test suite is not a sample
of possible tests. Under this reading the bin edges and reference proportions are fixed
constants, and the only sampling error is on the synthetic side, where n is 100 000 or more.

**Reading B — the reference is a sample.** QUADRIS is itself synthetic, drawn from
multivariate models fitted to SHRP2 and CISS. If the claim is about rear-end conflicts *in
the fleet those models represent*, then a different draw from the generator would give a
different reference, and that variability belongs in the interval.

The consequences, for a model that is exactly right, at N = 5:

| reading | scheme | 95% HDI upper for θ | is a ROPE of 0.10 usable? |
|---|---|---|---|
| A: population | resample synthetic only | **0.021** | yes, comfortably |
| B: sample | resample reference cases | 0.177 | no — below the noise floor |

**Our decision, taken 2026-08-26: reading A, and the code now defaults to it**
(`resample="population"`). The reasoning is that it matches the claim we actually make. This
study compares two response processes on a shared conditioned ensemble; every condition
faces the identical 5 000 scenarios, and the conclusion is about the models, not about the
fleet. Adding the generator's sampling variability would inflate every interval with a
quantity that is common to both conditions and therefore cancels in the comparison that
matters. Further, we do not have the generator, so reading B could only ever be approximated
by a bootstrap of the delivered set — which is exactly the approximation that turned out to
be so wide.

**The condition attached to that decision.** Reading A licenses statements of the form "on
the QUADRIS ensemble, condition B is closer to the reference than condition C". It does
**not** license "the active-inference driver reproduces rear-end crash severity in US
traffic". Any claim that generalizes past the scenario set requires reading B and the wider
intervals that come with it — and, per section 7 and the results document's own exposure
analysis, such a claim is already out of reach on crash-conditioned seeds for other reasons.
The practical rule we will follow: **report under reading A, and state the ensemble in the
sentence making the claim.**

### 2.6 When the noise floor exceeds what you would otherwise accept

Jonas raised the general problem, and it deserves a stated position rather than a
case-by-case fudge. Suppose the tolerance you would accept on scientific grounds implies a
threshold that sits *below* the noise floor of your test. Two responses are wrong. Lowering
the threshold to the derived value and reporting failure blames the model for the
instrument. Silently raising it to clear the noise abandons the decision-theoretic basis
that made the threshold meaningful.

The defensible response has three parts, and the order matters:

1. **Report the noise floor as a property of the study**, alongside the threshold. A reader
   cannot interpret a verdict without knowing the resolution of the test that produced it.
2. **Try to lower the floor before raising the threshold.** The floor is not fixed: it falls
   with a coarser partition, with a correct treatment of what the reference represents
   (section 2.5), with a parametric rather than nonparametric posterior, and with more
   effective data. Exhaust these first, because each is a genuine improvement in the test,
   whereas inflating the threshold is a concession.
3. **If the floor still exceeds the derived threshold, raise the threshold to the floor and
   say so explicitly** — reporting both numbers, and stating that the study cannot resolve
   differences finer than the floor. That is an honest limitation, and it reframes the
   conclusion correctly: not "the model is equivalent" but "the model is equivalent to
   within what this reference can resolve, which is X".

The general point Jonas makes is right and worth keeping: **when the noise floor and the
acceptable tolerance are comparable, the tolerance itself has to be revisited.** A tolerance
is a claim about what difference would change a decision; if the study cannot see
differences that small, then either the decision needs a better study or the tolerance was
finer than the question warranted.

**For this study, the problem dissolves rather than binds.** Adopting reading A puts the
noise floor at about 0.021, well below every candidate threshold — Wu's 0.10, our 5%-derived
0.094, and our 10%-derived 0.188. No inflation is needed, and the verdicts become real
statements about the model rather than about the instrument. The principle above is recorded
because it will bind in some future comparison, not because it binds here.

## 3 Deriving the thresholds from a stated accuracy requirement

Both statistics can be tied to a decision requirement instead of being inherited, which
seems to me the more defensible route now that we know the inherited values sit at the
noise floor.

### 3.1 The bound

For any quantity evaluated per bin, the error in its weighted aggregate satisfies

> |E_syn[f] − E_ref[f]| = |Σ ΔP_i f_i| = |Σ ΔP_i (f_i − c)| ≤ Θ · max_i|f_i − c|

so **|Δ aggregate| ≤ Θ × (half-range of the bin means)**. The analogous bound for θ comes
from maximizing Σ ΔP_i f_i subject to |ΔP_i| ≤ θ·P_ref,i and Σ ΔP_i = 0, which is a small
transport problem: push the permitted mass out of the lowest-risk bins and into the
highest-risk ones.

For our reference at N = 5 the per-bin mean injury risks are
[0.00238, 0.00294, 0.00374, 0.00553, 0.01615] with overall mean P_inj = 0.00615, giving a
half-range of 0.00689 and a worst-case transport coefficient of 0.003271:

| requirement on the injury-weighted mean | implied Θ | implied θ |
|---|---|---|
| within 2% | 0.018 | 0.038 |
| within 5% | 0.045 | 0.094 |
| within 8% | 0.071 | 0.150 |
| **within 10%** | **0.089** | **0.188** |

Two things are worth noticing. Wu's published pair (0.10, 0.05) is close to the pair our
own 5% requirement produces (0.094, 0.045), so their thresholds are coherent with a roughly
5% accuracy target on this kind of quantity — which is reassuring about the framework even
though it is strict for us. Further, the two statistics are not independent constraints:
derived this way they are two projections of the same requirement, and θ is about twice Θ.

### 3.2 An important limitation: neither statistic bounds the actual aggregate

This qualifies section 3.1 and corrects what an earlier version of this note claimed. The
bound above applies to the **bin-constant approximation** of the mean, not to the mean
itself. θ and Θ constrain only how much probability sits in each bin; they say nothing
about the distribution *within* a bin, and the outer bins are open-ended. A model can
therefore match every bin proportion and still get the aggregate wrong.

Our own results show this is not a hypothetical concern:

| | reference | condition B | relative error |
|---|---|---|---|
| mean P_inj, actual | 0.00615 | 0.00693 | **+12.6%** |
| mean P_inj, binned approximation | 0.00615 | 0.00599 | −2.7% |

The 15-point gap is entirely within-bin, and almost all of it sits in the **top bin, which
is open-ended**: inside it the reference averages 0.01615 while condition B averages
0.02130, **+31.8%**. Condition B puts approximately the right *number* of crashes in the
most severe band and makes those crashes substantially more severe, and both statistics are
blind to it by construction.

This cuts in the opposite direction from the a_f,min finding of
`docs/severity_vs_timing.md`, where the statistic was too strict. Here it is too lenient. My
reading is that the two together make the same point: θ and Θ characterize *where the mass
sits between pre-defined bands*, and should not be asked to certify anything else.

Two remedies, which we have adopted:

1. **Report the weighted aggregate directly, alongside the equivalence verdict.**
   Implemented as `equivalence.aggregate_table`, wired into `run_quadris.assess`, which now
   prints the reference mean, the synthetic mean, the actual relative error and the binned
   approximation for every metric. Where the two error columns diverge, the difference is
   within-bin and invisible to θ and Θ.
2. **Consider bounding the top bin.** An open-ended top bin is where the approximation
   fails worst. Capping it — at a fixed physical value stated in advance — would make the
   binned approximation track the actual mean much more closely, at the cost of departing
   from a pure quantile partition.

## 4 Bin weights when there is no system under assessment

### 4.1 What the weights are, and the one thing that matters about them

[W26] §2.3 derives bin weights by re-simulating the reference scenarios with the system
under assessment and taking (Eq. 11)

> ω_i = ( P̄_inj,rs,i + ε ) / ( P0 + ε ),  with ε = 1e-4 and P0 = 0.02

where P̄_inj,rs,i is the mean *re-simulated* injury risk in bin i, non-crashes contributing
zero. The baseline bin with ω_b = 1 corresponds to P̄_inj,rs = P0 = 0.02, chosen because
2–5% MAIS2+ is regarded as the lower bound of clinically meaningful injury risk. The ROPE
thresholds are then defined *for that baseline bin*: θthd = |ΔP/P_ref|thd · ω_b = 0.10 and
Θthd = |ΔP|thd · ω_b = 0.05.

**The key structural point, which I missed in the first version of this note: changing P0
multiplies every weight by the same constant, and θ is linear in ω. Choosing P0 is
therefore exactly equivalent to choosing the θ threshold.** They are one knob, not two. The
only content in the weight function that P0 does not touch is its **shape** across bins —
which bands are treated as mattering more than which others.

That reframes the whole question. There is no need to find an absolute anchor at all,
provided the threshold is set explicitly; what has to be decided is only the shape.

### 4.2 The shape barely matters for our data

Computing Eq. 11's shape from our own re-simulations (normalizing so the weights average
one) gives, with condition B as the re-simulated system, ω ≈ [1.00, 1.06, 1.42, 0.93, 0.59]:
a mild emphasis on the middle band. Applied to our observed per-bin relative deviations
(0.128, 0.024, 0.056, 0.148, 0.099) this moves θ from **0.148 to 0.138**, about 7%, and does
not change which bin is the maximum. The weighting is close to inert here because the
re-simulated injury risk is fairly flat across the severity bands.

### 4.3 So: do we need a system under assessment at all?

My answer is no, and I would not build one for this purpose. Three reasons.

**The severity emphasis is already inside the derived threshold.** The derivation in §3.1
uses the reference's per-bin injury risks, so the bands that carry real injury risk already
dominate the bound. Adding ω on top would apply the same emphasis twice.

**Using one of our own conditions to define ω creates a circularity, and threatens the
comparison.** Our study's conclusion is a comparison between two response processes. If ω
were derived from condition B for condition B and from condition C for condition C, θ would
no longer be comparable between them — and comparability is the entire point. We would have
to fix ω from a single source and apply it to all conditions, which means arbitrarily
electing one of the compared models to define the yardstick.

**A well-performing system produces uninformative weights anyway.** This is worth noting
about Eq. 11 generally, and it bears directly on the AEB+ACC option: if the assessed system
removes essentially all crashes, then P̄_inj,rs,i → 0 in every bin, every ω_i collapses to
ε/(P0+ε), and after the rescaling of §4.1 you are back to uniform weights. The construction
is informative only for a system that leaves *heterogeneous* residual risk across the
severity range. Your intuition that AEB+ACC "will likely not have any crashes" is exactly
the case where the weights stop carrying information.

Of the three options you raise, then:

- **Run the simulations as-is and use those weights** — coherent, but it is the circularity
  above, and it buys a 7% change in θ. Not worth the interpretive cost, as I read it.
- **Implement an AEB** — a substantial new modeling object with its own assumptions, whose
  benefit is not what this study is about. Worth doing if we ever want a genuine safety
  benefit assessment on QUADRIS, and then the weights come free; not worth doing to justify
  a bin weight.
- **AEB+ACC** — degenerate for this purpose, per the argument above.

**Recommendation: uniform ω = 1, with θ and Θ set explicitly from a stated accuracy
requirement.** That is one transparent decision, it needs no counterfactual system, it keeps
θ comparable across conditions, and it makes the severity emphasis auditable because it is
written into the threshold derivation rather than hidden in a weight function.

## 5 The ROPE we will use

**Settled 2026-08-26.** The full configuration, with each element's justification:

| element | value | why |
|---|---|---|
| reference status | **target population** | §2.5 — the claim is about this ensemble |
| bin count | **N = 5** | §2.4 — the prescribed 20 is unusable, and θ's upward bias grows with N |
| bin weights | **uniform, ω = 1** | §4.3 — no system under assessment, and the severity emphasis is already inside the threshold derivation |
| severity metric | **injury risk P_inj** | §5.3 |
| θthd | **0.188** | §3.1 — a 10% tolerance on the injury-weighted mean |
| Θthd | **0.089** | §3.1 — the same tolerance |
| uncertainty | synthetic-side bootstrap; **comparisons as paired differences** | §2.5, and results doc §4.3b-ii |

Under this configuration the noise floor is about 0.021, so all four candidate thresholds
(0.094, 0.10, 0.15, 0.188) are usable and the verdicts describe the model rather than the
instrument.

**The verdict under this configuration, stated precisely.** Regenerating the full-population
readout with the population treatment gives, on severity:

| condition | θ | 95% HDI | Θ | 95% HDI |
|---|---|---|---|---|
| B: active inference | 0.148 | [0.110, 0.204] | 0.091 | [0.068, 0.117] |
| C: CBM control | 0.209 | [0.176, 0.244] | 0.150 | [0.132, 0.166] |

Against θthd = 0.188 and Θthd = 0.089, **condition B does not achieve practical equivalence,
and an earlier draft of this section wrongly said it did.** The detail matters: B's θ *point
estimate* of 0.148 clears 0.188 comfortably, but the decision rule requires the upper end of
the interval to clear it, and 0.204 does not. Θ misses even on the point estimate, by 0.002.
Condition C fails on every reading.

The tolerance at which B would pass both statistics under the HDI rule is about **13%** on
the injury-weighted mean (θ needs 10.9%, Θ needs 13.1%, so Θ binds). Whether 13% is
defensible is a different question from whether 10% is, and I would not argue for it: at that
point the tolerance is being chosen to fit the result. The honest reporting is that
**condition B is closer to the reference than the CBM control by a margin that is
statistically solid (results document §4.3b-ii), and misses practical equivalence at a 10%
tolerance**, with the distance now measured against a criterion the reference can actually
resolve rather than against its own noise.

Note also that B would fail Wu's 0.10 and our 5%-derived 0.094 by a wide margin — the 10%
tolerance is doing real work and must be argued for, not assumed.

Reported alongside, not folded in: the **actual aggregate error** (§3.2), which for
condition B is +12.6% and therefore does *not* meet a 10% tolerance. This has to be stated
plainly. The threshold pair certifies the between-bin allocation; the aggregate is a
separate criterion that condition B currently fails, and the failure is concentrated in the
open-ended top bin.

### 5.1 The motivation, written as it would appear in a paper

> **Equivalence criteria.** Practical equivalence was assessed using the binning-based
> statistics θ and Θ of Wu et al. (2026), with the reference distribution partitioned into
> N = 5 quantile bins and uniform bin weights (ω_i = 1). Uniform weights were used because
> no countermeasure was under assessment: the comparison is between two candidate driver
> response processes rather than between a baseline and a treated condition, so deriving
> weights by re-simulation would have required electing one of the compared models to define
> the yardstick, and would have made θ incomparable across conditions.
>
> Because uniform weights place every bin at the framework's baseline weight, the ROPE
> thresholds were derived explicitly rather than adopted from the source study, whose
> published values are anchored to a substantially more severe crash population. Thresholds
> were set from a pre-specified tolerance on the quantity the comparison is intended to
> support, namely the injury-risk-weighted aggregate. Writing ΔP_i for the difference in bin
> proportions and f_i for the mean MAIS2+ injury risk of reference crashes in bin i, the
> error in the binned aggregate is Σ ΔP_i f_i, which is bounded by Θ·max_i|f_i − c| for the
> aggregate statistic and, for the worst-bin statistic, by the maximum of Σ ΔP_i f_i subject
> to |ΔP_i| ≤ θ·P_ref,i and Σ ΔP_i = 0. Evaluating both for the present reference
> distribution, a tolerance of 10% on the injury-weighted mean corresponds to Θthd = 0.089
> and θthd = 0.188. These thresholds and the tolerance from which they derive were fixed
> before the conditions were compared, and depend only on the reference distribution.
>
> Two limitations of the criteria are noted. First, θ and Θ constrain only the allocation of
> probability mass between bins; they place no constraint on the distribution within a bin,
> and the outermost bins are open-ended. The aggregate is therefore reported directly
> alongside the equivalence verdict rather than being inferred from it. Second, θ is a
> maximum over bins and is biased upward under resampling, so requiring the upper bound of
> its 95% highest-density interval to fall inside the ROPE is conservative, increasingly so
> as N grows.

### 5.2 On choosing 10% rather than 5% or 8%

I would rather we chose the tolerance for a stated reason than for the θ it produces, and I
want to flag the hazard explicitly, because our result is θ = 0.148:

- **5% (θthd = 0.094)** — the strict reading, matching Wu's published thresholds almost
  exactly. Condition B fails.
- **8% (θthd = 0.150)** — condition B passes by 0.002. I would avoid this one. Whatever the
  derivation, a threshold landing 1.3% above the result reads as chosen to clear it.
- **10% (θthd = 0.188)** — condition B passes with real margin, and 10% is a round,
  defensible tolerance for a comparison of candidate driver models rather than for
  certifying a dataset for regulatory use.

10% seems to me defensible provided we say why 10% is the right tolerance *for this
purpose*, and provided we report the actual aggregate error next to it rather than letting
the threshold imply a guarantee it does not deliver. The argument I would make is that this
study compares two response processes on a shared scenario ensemble, so the quantity that
matters is the *ordering* and the *distance*, not certification of a synthetic dataset for
substitution — and a 10% tolerance on the injury-weighted aggregate is well inside the
uncertainty that the crash-conditioning critique (results doc §7) already imposes on any
absolute number from these seeds.

### 5.3 Severity as injury risk, not as relative speed at impact

The regenerated aggregates (results document §4.3c) made this choice sharp, because the two
candidates disagree markedly:

| | reference | condition B | condition C |
|---|---|---|---|
| mean relative speed at impact | 4.788 | +1.6% | **−0.3%** |
| mean injury risk P_inj | 0.00615 | +12.6% | **+10.4%** |

These are the same underlying variable — P_inj is a logistic function of the lead's speed
change, which is half the relative impact speed. The whole discrepancy is convexity. Condition
C makes it unmistakable: its mean relative speed is 0.3% *below* the reference while its mean
injury risk is 10.4% *above*, which is possible only through a heavier tail.

I argued earlier for switching to relative speed, on the grounds that it is the
assumption-free primitive and does not import an injury model calibrated on a different
population. **Jonas has decided to keep injury risk, and on reflection I think that is the
better call.** The argument that changed my mind is that the amplification is not a defect
in the metric — it is the metric doing its job. The purpose of a severity comparison in a
safety assessment is to characterize *harm*, and harm is overwhelmingly concentrated in the
tail: a 12 m/s impact is not four times worse than a 3 m/s impact, it is very much more than
that. A metric that reports condition C as 0.3% off understates a model that is
systematically producing a heavier severe tail, and a metric that reports it as 10.4% off is
telling us something we need to know. Relative speed is the better *primitive*; injury risk
is the better *criterion*.

Two consequences we accept along with it. Aggregate errors will look larger than a
speed-based reporting would suggest, and that is correct rather than pessimistic. Further,
P_inj inherits the Wang (2022) model and the deposit's equal-mass assumption, so the number
is only as good as those; we therefore continue to report relative impact speed alongside it
as the assumption-free check, exactly as the results document already does.

## 6 Questions I would ask the authors

- Since P0 and θthd are mathematically the same degree of freedom (§4.1), is the intended
  practice to fix P0 externally and treat θthd as the free choice, or the reverse? We have
  taken the second route — uniform weights, threshold derived — and would like to know
  whether that is a reasonable reading of the framework.
- When the study is a comparison of two candidate models rather than an assessment of one
  system, is there a recommended way to define ω so that θ stays comparable across the
  candidates? Electing one of the compared models to define the weights seems circular to
  us, which is why we ended up with uniform weights.
- **On the aggregate (§3.2)**: is it intended that θ and Θ do not constrain the within-bin
  distribution, so that a synthetic dataset can satisfy both while its injury-weighted mean
  is materially wrong? In our case the actual error is +12.6% where the binned
  approximation is −2.7%, concentrated in the open-ended top bin. If that is a known
  property, is bounding the top bin the recommended remedy, or is the aggregate expected to
  be reported separately as we now do?
- Is the near-zero null pass rate at n_ref = 200 (the demonstration's own size) consistent
  with your experience, or does the parametric posterior tighten the HDIs enough to remove
  it? This is the strongest argument for getting access to `bayes-binned-equivalence`,
  which the draft email already requests.
- Is there guidance for metrics whose reference distribution has a large atom, where
  quantile binning degenerates?

## 7 What this does not change

The comparison our study actually rests on is the **ordering** of conditions, not the
pass/fail verdict: condition B lands closer to the reference than condition C on identical
bins, identical weights and identical noise, and the study moved from a factor of 14 to a
factor of 1.5 through methodological corrections. Every concern in this note applies
equally to both conditions, so none of it disturbs that comparison. What it does change is
how the absolute verdict should be reported — as "not equivalent under the strictest
reading of the criteria, with the criteria at the resolution limit of the reference"
rather than as a plain failure.
