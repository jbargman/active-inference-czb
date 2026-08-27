"""Stage-0 feasibility fit: population probit on the Random cut-in response surface.

The committed source of the numbers in docs/czb_fitting_plan.md section 2 (stage 0) and
section 4: a two-parameter threshold-plus-noise model, P(intervene) = Phi((x - c)/sigma),
fitted to the 18-cell criticality-by-timepoint surface for each candidate covariate.
Everything upstream of (c, sigma) is the zero-fitted-parameter field.

    python replication/czb/pilot_surface_fit.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from comfortzone.czb_data import random_cutin_trials    # noqa: E402


def fit_probit(x: np.ndarray, k: np.ndarray, n: np.ndarray) -> tuple[float, float]:
    def nll(params):
        c, s = params
        p = np.clip(norm.cdf((x - c) / max(s, 1e-6)), 1e-9, 1 - 1e-9)
        return -(k * np.log(p) + (n - k) * np.log(1 - p)).sum()
    res = minimize(nll, [np.median(x), np.std(x)], method="Nelder-Mead")
    return float(res.x[0]), float(res.x[1])


def main() -> None:
    r = random_cutin_trials()
    cells = (r.groupby(["criticality", "timepoint"])
              .agg(p=("intervene", "mean"), n=("intervene", "size"),
                   deficit_max=("deficit_max", "first"), a_req_max=("a_req_max", "first"))
              .reset_index())
    print(f"{len(r)} trials, {r.participant.nunique()} participants, {len(cells)} cells\n")
    print("Observed P(intervene):")
    print(cells.pivot_table(index="criticality", columns="timepoint", values="p").round(3), "\n")

    for cov in ("deficit_max", "a_req_max"):
        x = cells[cov].to_numpy()
        k = (cells.p * cells.n).to_numpy()
        c, s = fit_probit(x, k, cells.n.to_numpy())
        pred = norm.cdf((x - c) / s)
        obs = cells.p.to_numpy()
        rmse = float(np.sqrt(np.mean((pred - obs) ** 2)))
        corr = float(np.corrcoef(pred, obs)[0, 1])
        print(f"{cov}: c = {c:.4g}, sigma = {s:.4g}, RMSE = {rmse:.3f}, corr = {corr:.3f}")
        print(cells.assign(pred=pred).pivot_table(
            index="criticality", columns="timepoint", values="pred").round(2), "\n")


if __name__ == "__main__":
    main()
