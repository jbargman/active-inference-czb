# Perceptual uncertainty, the distance–time anomaly, and the missing lateral term

*2026-08-28. Written after two findings that the current field cannot explain — the
LTAP speed effect at matched PET, and the cyclist overtake's lateral criticality — and
after reading five papers Jonas pointed toward or that the search turned up. The claim
of this note is that these are **one problem, not two**, and that the fix is already
native to active inference. Companion documents: `docs/overtake_construction_note.md`
(where both findings came from), `docs/lane_entry_note.md` (the lateral machinery as it
stands), `docs/active_inference_for_czb_assessment.md` (the framework argument).*

## 1 The two things the field cannot currently do

**The LTAP speed effect.** In the Random LTAP design, intervention is *lower* at 70 km/h
than at 50 km/h at every one of the nine PET levels (at PET2: 0.360 against 0.605). PET
is a pure time measure, so at matched PET the higher speed simply means a larger distance
gap. Our field is built from time-like quantities — inverse tau, TTC, required
deceleration — and at matched PET those are close to identical between the two speeds.
The field therefore predicts almost no speed effect, and a large one is there.

**The cyclist-overtake lateral effect.** Passing a cyclist at 0.5 m rather than 1.5 m
roughly quadruples the intervention rate, while in *all* conditions the pass is
collision-free. The field's lateral machinery only asks whether a collision geometry
applies; it answers "yes, fully" throughout, and so cannot see the manipulation
(`overtake_construction_note.md` §4).

These look unrelated. Section 5 argues they are the same missing ingredient.

## 2 What the literature says about the distance–time anomaly

**Zgonnikov, Abbink and Markkula (2024)** modelled left-turn gap acceptance — our LTAP
scenario — with a generalized drift-diffusion model, and found that the probability of
going increases with **both** time-to-arrival **and** distance gap. Their model needs a
*generalized gap measure* combining the two; pure time-to-arrival does not suffice.
Response time increased with time-to-arrival, and there was an additional effect of
distance on "wait" responses. So the phenomenon we observe is documented, in our
scenario, by this group.

**Wang, Srinivasan, Jokinen, Oulasvirta and Markkula (2024)** supply the mechanism Jonas
remembered, in the pedestrian-crossing version of the same problem. Their model is
bounded-optimal decision-making under *noisy visual perception*: the agent estimates
distance and speed through a visual system whose angular noise translates into
distance-dependent uncertainty, so estimates of time-to-arrival become more dispersed in
some conditions than others. Because the cost of a misjudgement is asymmetric, the
rational response to a noisier estimate is a more conservative decision. Their model
reproduces four phenomena, of which the second is exactly ours: **greater gap acceptance
at higher speed for the same time-to-arrival**. Their framing is worth quoting for the
project's own argument: on this account speed-dependent gap acceptance "is an entirely
rational behaviour" given the visual system's constraints, not a bias to be corrected.

**Mohammad, Farah and Zgonnikov** (overtaking gap acceptance) tried the same family on a
third scenario and concluded that the model needs an **initial decision bias that depends
on the initial velocity** — a speed-dependent starting point, rather than a speed-
dependent drift or boundary. That is a third independent report that a speed or distance
term has to enter *somewhere* beyond the time-to-collision variable, and it is a useful
warning that where it enters is not obvious: the same qualitative effect can be produced
by a starting bias, a drift term, or a boundary.

**Bontje, van Waveren, van Maanen, Nallapu, Markkula and Zgonnikov (2026)** is a
semi-systematic review of 28 evidence-accumulation studies in traffic (2014–2026). Two
things in it bear on us directly. It confirms that in driving applications the drift is
conventionally driven by **looming (optical expansion) or TTC** — not, as in our card A.3
accumulator, by a comfort-zone deficit; and it lists **leaky accumulation** and
**urgency/collapsing boundaries** as the standard architectures for exactly the failure
modes we hit. Our A.3 accumulator used none of these. That does not overturn the FAIL —
which was pre-registered and stands — but it does say the FAIL was of one specific
accumulator, not of the accumulator family, and the reserve remedy we held back (leaky
accumulation) is the field's standard first move.

## 3 What the literature offers for the lateral problem

**Kolekar, de Winter and Abbink (2020)** propose the **Driver's Risk Field** (DRF), and it
is close enough to our construction to be worth taking seriously as a donor rather than a
rival. The DRF is a two-dimensional field around the car representing the driver's belief
about the probability of an event at each point; multiplied by the *consequence* assigned
to what is at that point and summed, it gives a scalar perceived risk. Human-like
behaviour then emerges from a controller that **keeps that scalar below a threshold**.

Two features matter for us. First, the shape: the field is a torus with a Gaussian
cross-section along the predicted path, whose height grows as a parabola out to a
look-ahead distance that scales with speed, and whose **width grows with arc length and
with the absolute steering angle** — the latter justified as signal-dependent noise in the
sensorimotor system. Width at the vehicle is set to car-width/4, so ±2σ spans the car.
Second, the standing: it is parameterized by six constants (p, t_la, m, c, k1, k2) that
depend only on the driver's state and not on the environment, and it was shown to
reproduce behaviour across seven scenarios including obstacle avoidance, car-following
and **overtaking** — the two scenarios we are currently failing to unify.

The structural point: "keep a scalar risk below a threshold" *is* a comfort-zone boundary
on a scalar, which is our claim exactly. The DRF is, in effect, an independently
validated instance of the framing this project is testing — with the lateral dimension
already built in, and validated on overtaking.

## 4 Why our field lacks both, structurally

Our preference field evaluates the deficit **along a single predicted trajectory**: the
ego's actual motion, with the other vehicle's motion projected forward. Everything is a
point estimate. The lane-entry weight is the one place where a distribution appears, and
even there the "overlap fraction" is a geometric overlap of two rigid width intervals, not
a probability.

A point-estimate field has two unavoidable consequences, and they are precisely our two
failures. It cannot express that a *clear* pass is uncomfortable, because on the predicted
trajectory nothing happens — you need probability mass off the predicted path for a 0.5 m
clearance to cost more than a 1.5 m one. And it cannot express that a distant vehicle is
less certain than a near one, because a point estimate has no width — you need the
estimate's dispersion to grow with distance for the speed effect at matched PET to appear.

## 5 One proposal that addresses both, and is native to active inference

**Give the predicted trajectory a distribution, and take the deficit in expectation over
it.** Concretely: replace the deficit evaluated at the predicted relative state,
`d(x̂)`, with `E[d(x)]` where `x ~ N(x̂, Σ(t))` and Σ grows with prediction horizon and
with distance.

This is not a bolt-on. Expected free energy is *already* an expectation of a preference
term under a predictive distribution — the released model simply collapses that
distribution to its mean for the scenarios it was built for, which are longitudinal and
where the collapse is harmless. Restoring the width is a return to the framework's own
form, and it is the same move as our lane-entry work (§3 of the lane-entry note argued the
continuous form is the closed-form of an expectation the closed loop already computes by
rollout). Ours would be a second such closed form.

What it buys, in one mechanism:

- **The lateral comfort term.** With lateral variance on the ego's predicted path, a
  0.5 m clearance puts real probability mass on the cyclist while a 1.5 m clearance does
  not, so the expected deficit grades smoothly with clearance even though every mean
  trajectory clears. This is precisely the DRF's Gaussian cross-section, arrived at from
  our own side, and it inherits the DRF's empirical support on overtaking.
- **The distance–time effect.** With prediction variance growing with horizon (and hence
  with distance at matched time), a far-but-time-matched conflict has a more dispersed
  predicted state. Under an asymmetric cost — which the preference function already has,
  since collisions cost far more than near-misses — expected deficit is *higher* for the
  more dispersed estimate. At matched PET the 50 km/h case is the nearer, and the 70 km/h
  case the more distant one; the sign of the resulting effect is exactly what needs
  checking against our data, and is the test proposed in §6.
- **A principled place for the epistemic half of the gaze machinery.** Uncertainty
  becomes a first-class quantity in the field rather than an unexercised branch.

**Two honest caveats.** First, adding predictive variance introduces at least one new
parameter (how Σ scales), which erodes the "nothing upstream of the boundary is fitted"
property — the same cost as the k decision in §5 of the overtake note, but larger. It
should therefore be calibrated once, on one scenario, and frozen for the transfer test.
Second, the *direction* of the distance effect under an expected-deficit model is a
derivation I have sketched and not done; if the asymmetry runs the other way, the
mechanism predicts the opposite of what we observe and the proposal fails. That
derivation is the first task in §6, and it should be done before any code is written.

## 6 What should be checked, in order

1. **Derive the sign.** For our preference function's actual cost asymmetry, does
   E[d(x)] under a wider Σ rise or fall? Analytic where possible, numeric otherwise. If
   the sign is wrong, stop; the mechanism is not the explanation.
2. **Test on LTAP, which is built for it.** The two-speed design separates time from
   distance by construction. Predicted: at matched PET, the expected-deficit field shows
   a speed effect of the observed sign and roughly the observed size, while the
   point-estimate field shows almost none.
3. **Test on the cyclist overtake.** Predicted: the expected-deficit field orders the 15
   cells materially better than the current +0.402, approaching the clearance label's
   0.833 without being given the clearance.
4. **Only then** consider whether the DRF's specific functional form (parabolic height,
   width linear in arc length and steering) should be adopted wholesale rather than
   re-derived, and whether its six constants can be inherited rather than refitted.

## 7 References

Bontje, F., van Waveren, F., van Maanen, L., Nallapu, B., Markkula, G., & Zgonnikov, A.
(2026). *Knowing when to move: Evidence accumulation models of human behavior in
traffic* (arXiv:2606.00727). arXiv. https://arxiv.org/abs/2606.00727

Kolekar, S., de Winter, J., & Abbink, D. (2020). Human-like driving behaviour emerges
from a risk-based driver model. *Nature Communications, 11*, Article 4850.
https://doi.org/10.1038/s41467-020-18353-4

Mohammad, S. H. A., Farah, H., & Zgonnikov, A. (2024). *A cognitive process approach to
modeling gap acceptance in overtaking* (arXiv:2306.05203). arXiv.
https://arxiv.org/abs/2306.05203

Wang, Y., Srinivasan, A. R., Jokinen, J. P. P., Oulasvirta, A., & Markkula, G. (2024).
*Pedestrian crossing decisions can be explained by bounded optimal decision-making under
noisy visual perception* (arXiv:2402.04370). arXiv. https://arxiv.org/abs/2402.04370

Zgonnikov, A., Abbink, D., & Markkula, G. (2024). Should I stay or should I go?
Cognitive modeling of left-turn gap acceptance decisions in human drivers. *Human
Factors, 66*(5), 1399–1413. https://doi.org/10.1177/00187208221144561

**Verification status**, per the project's provenance rule. Kolekar et al. (2020),
Bontje et al. (2026) and Mohammad et al. were read as full text (PDFs extracted locally);
the DRF equations, parameter list and validated-scenario list in §3 are taken from the
paper itself. Zgonnikov et al. (2024) and Wang et al. (2024) were read at
publisher-page and abstract-plus-extract level respectively — their headline findings as
quoted here are reliable, but the detailed noise-scaling argument attributed to Wang et
al. in §2 has **not** been checked against their equations, and the year and venue of
Mohammad et al. (arXiv preprint, also an IEEE conference paper) should be confirmed
before any manuscript cites it.
