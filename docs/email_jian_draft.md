# Draft email to Jian Wu — the pre-filter scenario set

Drafted 2026-08-25 for Jonas to edit and send. Context: resolves the crash-conditioning
(exposure) critique of re-simulating QUADRIS crash seeds; the quantitative case is
`docs/crash_causation_results.md` §7 (exposure ESS 44.7 of 5 000, 295 unreachable seeds).

---

Subject: QUADRIS — request for the pre-filter scenario set (or the fitted scenario-generation models)

Hi Jian,

We are running a study that re-simulates the QUADRIS rear-end scenarios with alternative
follower models — the crash-causation mechanisms from our 2024 TRF paper wrapped around
two response processes (the CBM's own, and an active-inference driver model as used by
Schumann et al.), evaluated against the 5,000-scenario reference with the
practical-equivalence framework from your validation paper, following the SCM comparison
in its section 3.

One limitation dominates everything we can conclude: the 5,000 scenarios are conditioned
on crashing under the original generator, so re-simulation can only answer "what does a
different driver do in situations that crashed for the original one". We correct the
weighting by dividing out per-seed crash probabilities, but the effective sample size
collapses (to roughly 45 of the full 5,000 in our runs, with about 300 scenarios
unreachable entirely), and scenarios the original driver never crashes are absent at any
sample size.

The clean fix would come from your side, in either form:

1. the sampled-but-not-crashed scenarios from the generation step (the runs discarded by
   the crash filter), or
2. the fitted multivariate models for the lead-vehicle profiles and initial conditions,
   so we can sample conflict exposure ourselves.

Either would let us apply the causation models to unconditioned conflict exposure and
make the comparison at the level the criticism of crash-only re-simulation is aimed at.
Two smaller items, if they are easy: access to the bayes-binned-equivalence code (so we
can match your posterior computation exactly rather than our bootstrap approximation),
and the fitted onset-time distribution of the abnormal-acceleration mode, which the
paper describes but does not parameterize.

Happy to share our comparison document and results so far, of course.

Best regards,
Jonas
