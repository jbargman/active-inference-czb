# A note for JJ: what we found when we put the full active-inference stack on the cut-in data

*Draft, 2026-09-22, for Jonas to send when he chooses (his decision 2). One page. The colleague
is JJ in every project document; this note names no one and no company. Every number is from a
committed script with a tracked output in the project repository; the pointers are in brackets
for Jonas and can be removed before sending.*

**What we did.** After our conversation we built the construction you argued for: at the response
moment of each stimulus clip, a belief over the cut-in vehicle's state with a latent lane-change
intention, a fan of its futures under a Gaussian predictive model, the ego's policies rolled out
against that fan, each scored with the released preference function in its residual-information
form, and ΔG = G(continue) − min over the menu as the criticality axis. We tested it on the
second cut-in study (378 cells, 288 after the lane change starts and 90 before, held out by
starting TTC), against the model that fits those data: a looming threshold with an anticipatory
gate (held-out weighted RMSE 0.103; chance 0.32). We then varied everything we could think of:
the preference constants (648 vectors), the functional of the expected free energy, the policy
menu with and without steering, the released planner itself, strand 1's preference structure
and an admissibility reading of its absolute conflict preference, the released model's own
τ⁻¹ looming preference, and four functionals over the horizon.

**What we found.** Every one of these quantities scores at chance on the cut-in (0.30 to 0.32),
and for one structural reason, which we think is worth your attention. A one-sided preference
(collision, braking margin, or looming) summed over the planning horizon of a `continue` policy
that drives through the lead counts *the number of steps before contact*, which grows with the
time to collision. The summed quantity therefore correlates +0.92 with TTC and is ordered
*against* the participants, who respond to proximity and looming; read pointwise at the response
moment, the same quantities are ordered *with* them (the required deceleration of SI Eq. 51:
+0.63 with the share who intervene, +0.74 to +0.94 within each closing speed). Removing the sum
(per-step rate, maximum over the horizon, first step) removes the inversion but produces no axis,
because the released looming term is a TTC quantity (Δv/gap), and these participants respond to
optical expansion (Δv/gap²). [cards JJ.2 to JJ.5b; `docs/review_2026-09-22.md` checks §1]

**What did come out of the framework.** Two things, and they are the reason we are still working
inside it. First, the *gate* of our measurement model, the probability that the other vehicle
counts yet, turns out to be exactly the predictive uncertainty of a Gaussian model of the other's
lateral motion: P(its body reaches mine within 3 s) = Φ((−l₀ − l̇T)/(σT)), which reproduces the
fitted gate to machine precision with s_l = σT, and scores 0.1028 / 0.046 with nothing fitted but
the response model. The latent intention variable is not needed for it, and as we had built it
(changers at a fixed lateral speed, keepers clipped at the lane edge) it prevented the belief
from grading. [card JJ.6e] Second, the boundary itself reads as a driver's one-sided prior over
the looming of a *lead*, with "is it a lead" predicted rather than observed: F = P(lead) × excess,
the free energy of the present observation. The data cannot tell the reflex reading of that from a
one-step expected-free-energy decision, but they reject an additive-noise spread (+0.023): the
spread is a spread of levels across drivers, which is the comfort-zone deliverable. [JJ.8, JJ.10]

**The one circularity, and the question for you.** The lateral-rate uncertainty σ = 0.33 m/s was
itself set from the fitted gate's spread, so the gate is a restatement, not a prediction, until σ
is measured on lane-keeping vehicles in naturalistic data; that is our next card when highD
arrives. The question: is there, in your group's generative models of lateral motion, a value for
that quantity we could use as an independent prediction, and does the horizon-sum observation
match your own experience of using expected free energy as a criticality measure on human
response data?
