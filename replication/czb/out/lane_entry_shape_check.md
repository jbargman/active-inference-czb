# Does the lane-entry ramp want to be S-shaped?

Jonas's proposal of 2026-08-28, tested on the 18-cell Random cut-in surface. `lane_entry_shape` remaps the predicted lateral overlap fraction u by g(u; k), with g(u; 0) = u exactly, so k = 0 is the published linear ramp and the comparison is like-for-like. The stage-0 two-parameter probit is refitted at every k.

| k | correlation | RMSE | threshold c | response sd s |
|---|---|---|---|---|
| -8 | 0.9086 | 0.1211 | 5230 | 1838 |
| -4 | 0.9110 | 0.1199 | 5230 | 1753 |
| -2 | 0.9118 | 0.1192 | 5230 | 1753 |
| +0 *(published)* | 0.9122 | 0.1189 | 5230 | 1753 |
| +1 | 0.9123 | 0.1188 | 5230 | 1753 |
| +2 | 0.9126 | 0.1185 | 5230 | 1753 |
| +4 | 0.9136 | 0.1177 | 5230 | 1753 |
| +6 | 0.9147 | 0.1167 | 5230 | 1753 |
| +8 | 0.9186 | 0.1156 | 5288 | 1668 |
| +12 **(best)** | 0.9193 | 0.1154 | 5288 | 1582 |
| +16 | 0.9160 | 0.1181 | 5345 | 1582 |
| +20 | 0.9077 | 0.1230 | 5345 | 1582 |
| +30 | 0.8879 | 0.1345 | 5403 | 1668 |
| +50 | 0.8680 | 0.1437 | 5403 | 1838 |
| +100 | 0.8642 | 0.1457 | 5403 | 1838 |

Best k = **+12** (RMSE 0.1154) against the linear ramp's 0.1189 — a change of +0.0035, i.e. +2.9% of the linear form's error.

## Where this can and cannot be decided

The sweep is informative only where the overlap fraction spans its range. It does in the cut-in (the target crosses the marking). It does **not** in the cyclist overtake, where P_lane stays within 0.843..1.000 and every k gives the same cell ordering (`out/overtake_field_check.md`). Any conclusion here is therefore a statement about cut-in geometry, not a general one.

## The methodological cost, if k is ever fitted

Fitting k would make it the **first fitted parameter upstream of the boundary**. The stage-0 result derives much of its force from the field having zero fitted constants — a two-parameter probit on a covariate nobody tuned. A fitted k does not destroy that (it is one shape parameter, not a per-scenario coefficient), but it must be reported as a field parameter, and for the transfer test it would have to be frozen at its cut-in value before any transfer scenario is scored. Raised as a query rather than settled.

## What the sweep says about the released binary gate

As k grows the ramp approaches a step at half overlap, which is effectively the released binary lane test. That limit is clearly **worse** than both the optimum and the linear ramp, so the sweep independently corroborates the 2026-08-27 decision to replace the binary gates with a continuous form (`docs/lane_entry_note.md`): the gain there was not an artifact of picking a linear ramp in particular.

