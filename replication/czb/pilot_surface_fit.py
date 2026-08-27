"""Stage-0 feasibility fit: population probit on the Random cut-in response surface.

The committed source of the numbers in docs/czb_fitting_plan.md sections 2 and 4 and in
docs/active_inference_for_czb_assessment.md section 3: a two-parameter
threshold-plus-noise model, P(intervene) = Phi((x - c)/sigma), fitted to the 18-cell
criticality-by-timepoint surface for each candidate covariate (everything upstream of
(c, sigma) is the zero-fitted-parameter field), followed by the kinematic baseline
comparison at matched or nearly matched parameter counts -- including the
scenario-specific design-variable regression that OUTPERFORMS the field within this
scenario (corr 0.96 vs 0.90), which is why the field's case rests on transfer and on
the accumulator, not on within-scenario fit.

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

    baselines(cells)


def baselines(cells) -> None:
    """Kinematic baselines for the assessment's section-3 comparison."""
    cells = cells.copy()
    cells["t_end"] = [0.3 * (int(tp[1]) - 1) for tp in cells.timepoint]
    cells["ttc_nom"] = cells.criticality.str.replace("TTC", "").astype(float)
    cells["ttc_end"] = cells.ttc_nom - cells.t_end       # the dataset's design relation
    k = (cells.p * cells.n).to_numpy()
    n = cells.n.to_numpy()
    obs = cells.p.to_numpy()

    def fit_glm(design):
        X = np.column_stack([np.ones(len(cells))] + design)

        def nll(b):
            p = np.clip(norm.cdf(X @ b), 1e-9, 1 - 1e-9)
            return -(k * np.log(p) + (n - k) * np.log(1 - p)).sum()

        best = None
        for seed in range(5):
            rng = np.random.default_rng(seed)
            res = minimize(nll, rng.normal(0, 0.5, X.shape[1]), method="Nelder-Mead",
                           options={"maxiter": 20000, "xatol": 1e-8, "fatol": 1e-8})
            if best is None or res.fun < best.fun:
                best = res
        p = norm.cdf(X @ best.x)
        return (float(np.sqrt(np.mean((p - obs) ** 2))),
                float(np.corrcoef(p, obs)[0, 1]), X.shape[1])

    models = {
        "field deficit (running max)": [cells.deficit_max.to_numpy() / 1000],
        "TTC at clip end (design)": [cells.ttc_end.to_numpy()],
        "1/TTC at clip end": [1 / cells.ttc_end.to_numpy()],
        "gated a_req (running max)": [cells.a_req_max.to_numpy()],
        "TTC_nom + exposure time": [cells.ttc_nom.to_numpy(), cells.t_end.to_numpy()],
        "1/TTC_end + exposure time": [1 / cells.ttc_end.to_numpy(), cells.t_end.to_numpy()],
    }
    print(f"{'baseline comparison':34s} {'params':>6s} {'RMSE':>6s} {'corr':>6s}")
    for name, d in models.items():
        rmse, corr, npar = fit_glm(d)
        print(f"{name:34s} {npar:6d} {rmse:6.3f} {corr:6.3f}")


if __name__ == "__main__":
    main()
