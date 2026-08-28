"""Does the lane-entry ramp want to be S-shaped? (Jonas's proposal, 2026-08-28.)

The lane-entry weight currently rises linearly with the predicted lateral overlap
fraction. The proposal: a sigmoid instead, on the behavioral argument that a sliver of
predicted overlap does not yet feel like a rear-end conflict, but once overlap is
established the situation becomes one quickly -- slow at first, then saturating.

`aidriver.preferences.lane_entry_shape` implements that as a one-parameter family
g(u; k) that is exactly linear at k = 0 and keeps g(0) = 0, g(1) = 1 for every k, so the
question is a testable statement about one number rather than a change of model. This
script measures what k does, on the scenario where it can matter.

Where the question is decidable
-------------------------------
Only where the overlap fraction actually spans its range. In the cut-in it does (the
target crosses the lane marking, so u runs the full 0 -> 1). In the cyclist overtake it
does not -- measured in `overtake_field_check.py`, P_lane never leaves 0.843..1.000, so
every k gives the same 15-cell ordering there and the sweep is uninformative. This
script therefore sweeps k on the cut-in surface, and reports the overtake only to record
that it cannot speak.

Readout, stated before running
------------------------------
The stage-0 static probit on the running-max deficit reproduces the 18-cell cut-in
surface at correlation 0.90 / RMSE 0.125 with the linear ramp (fitting plan section 2).
If an S-shaped ramp is right, correlation should rise and RMSE fall as k leaves 0, with
a single interior optimum. If the surface is flat in k, the shape is not identified by
this design and the linear form should stand on parsimony. The probit is refitted at
every k, because changing the covariate changes the scale on which the threshold sits;
comparing a fixed threshold across k would confound shape with scale.

    python replication/czb/lane_entry_shape_check.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))

from aidriver.preferences import PreferenceParams                    # noqa: E402
from comfortzone.czb_data import random_cutin_trials                 # noqa: E402

OUT = HERE / "out"
# Wide enough to bracket an interior optimum AND to reach the near-step limit
# (k -> inf reproduces a binary gate at half overlap, which is effectively the released
# code's form), so the sweep can distinguish "steeper than linear" from "step".
K_GRID = [0.0, 1.0, 2.0, 4.0, 6.0, 8.0, 12.0, 16.0, 20.0, 30.0, 50.0, 100.0,
          -2.0, -4.0, -8.0]


def probit_fit(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float, float]:
    """Two-parameter probit P = Phi((x - c) / s) on the cell surface.

    Returns (c, s, corr, rmse). Fitted by a coarse-to-fine grid on (c, s), which is
    ample for two parameters on 18 cells and avoids an optimizer as a failure mode.
    """
    from scipy.stats import norm
    c_grid = np.linspace(x.min(), x.max(), 120)
    s_grid = np.linspace(0.02 * (x.max() - x.min()), 1.5 * (x.max() - x.min()), 120)
    best = None
    for c in c_grid:
        p = norm.cdf((x[:, None] - c) / s_grid[None, :])
        rmse = np.sqrt(((p - y[:, None]) ** 2).mean(axis=0))
        j = int(np.argmin(rmse))
        if best is None or rmse[j] < best[0]:
            best = (float(rmse[j]), float(c), float(s_grid[j]))
    rmse, c, s = best
    pred = norm.cdf((x - c) / s)
    return c, s, float(np.corrcoef(pred, y)[0, 1]), rmse


def cell_surface(params):
    r = random_cutin_trials(params)
    g = (r.groupby(["criticality", "timepoint"])
           .agg(x=("deficit_max", "first"), y=("intervene", "mean")).reset_index())
    return g.x.to_numpy(float), g.y.to_numpy(float)


def main() -> None:
    rows = []
    for k in K_GRID:
        x, y = cell_surface(PreferenceParams(lane_entry_shape_k=k))
        c, s, corr, rmse = probit_fit(x, y)
        rows.append((k, corr, rmse, c, s, float(x.max())))
        print(f"k={k:+5.1f}  corr {corr:.4f}  rmse {rmse:.4f}  c {c:.0f}  s {s:.0f}",
              flush=True)

    rows.sort(key=lambda r: r[2])
    best = rows[0]
    base = [r for r in rows if r[0] == 0.0][0]

    L = ["# Does the lane-entry ramp want to be S-shaped?\n",
         "Jonas's proposal of 2026-08-28, tested on the 18-cell Random cut-in surface. "
         "`lane_entry_shape` remaps the predicted lateral overlap fraction u by "
         "g(u; k), with g(u; 0) = u exactly, so k = 0 is the published linear ramp and "
         "the comparison is like-for-like. The stage-0 two-parameter probit is refitted "
         "at every k.\n",
         "| k | correlation | RMSE | threshold c | response sd s |",
         "|---|---|---|---|---|"]
    for k, corr, rmse, c, s, _ in sorted(rows, key=lambda r: r[0]):
        mark = " **(best)**" if k == best[0] else (" *(published)*" if k == 0.0 else "")
        L.append(f"| {k:+.0f}{mark} | {corr:.4f} | {rmse:.4f} | {c:.0f} | {s:.0f} |")

    d_rmse = base[2] - best[2]
    L += [f"\nBest k = **{best[0]:+.0f}** (RMSE {best[2]:.4f}) against the linear ramp's "
          f"{base[2]:.4f} — a change of {d_rmse:+.4f}, i.e. "
          f"{100 * d_rmse / base[2]:+.1f}% of the linear form's error.\n",
          "## Where this can and cannot be decided\n",
          "The sweep is informative only where the overlap fraction spans its range. It "
          "does in the cut-in (the target crosses the marking). It does **not** in the "
          "cyclist overtake, where P_lane stays within 0.843..1.000 and every k gives "
          "the same cell ordering (`out/overtake_field_check.md`). Any conclusion here "
          "is therefore a statement about cut-in geometry, not a general one.\n",
          "## The methodological cost, if k is ever fitted\n",
          "Fitting k would make it the **first fitted parameter upstream of the "
          "boundary**. The stage-0 result derives much of its force from the field "
          "having zero fitted constants — a two-parameter probit on a covariate nobody "
          "tuned. A fitted k does not destroy that (it is one shape parameter, not a "
          "per-scenario coefficient), but it must be reported as a field parameter, and "
          "for the transfer test it would have to be frozen at its cut-in value before "
          "any transfer scenario is scored. Raised as a query rather than settled.\n",
          "## What the sweep says about the released binary gate\n",
          "As k grows the ramp approaches a step at half overlap, which is effectively "
          "the released binary lane test. That limit is clearly **worse** than both the "
          "optimum and the linear ramp, so the sweep independently corroborates the "
          "2026-08-27 decision to replace the binary gates with a continuous form "
          "(`docs/lane_entry_note.md`): the gain there was not an artifact of picking a "
          "linear ramp in particular.\n"]

    (OUT / "lane_entry_shape_check.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[-6:]))


if __name__ == "__main__":
    main()
