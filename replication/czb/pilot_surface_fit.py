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

from comfortzone.czb_data import (RANDOM_CUTIN_TRACES, random_cutin_trials,
                                  stimulus_field)       # noqa: E402


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
    # Jonas's proposed state-based rule (2026-08-27): lateral offset at clip end, from
    # the traces -- a running minimum, mirroring the running-max convention
    fields = {c: stimulus_field(p) for c, p in RANDOM_CUTIN_TRACES.items()}
    for f in fields.values():
        f["dy_min"] = np.minimum.accumulate(np.abs(f.y_rel.to_numpy()))

    def at_time(f, t):
        i = np.searchsorted(f.t_since_onset.to_numpy(), t, side="right") - 1
        return float(f.dy_min.iloc[int(np.clip(i, 0, len(f) - 1))])

    cells["dy_min"] = [at_time(fields[c], t) for c, t in zip(cells.criticality, cells.t_end)]
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
        "2D state: 1/TTC_end + dy (Jonas)": [1 / cells.ttc_end.to_numpy(),
                                             cells.dy_min.to_numpy()],
        "TTC_nom + exposure time": [cells.ttc_nom.to_numpy(), cells.t_end.to_numpy()],
        "1/TTC_end + exposure time": [1 / cells.ttc_end.to_numpy(), cells.t_end.to_numpy()],
    }
    print(f"{'baseline comparison':34s} {'params':>6s} {'RMSE':>6s} {'corr':>6s}")
    for name, d in models.items():
        rmse, corr, npar = fit_glm(d)
        print(f"{name:34s} {npar:6d} {rmse:6.3f} {corr:6.3f}")

    crossval(cells, k, n, obs)


def crossval(cells, k, n, obs) -> None:
    """Held-out versions of the comparison (assessment section 3 addendum): the
    within-scenario advantage of the design regressions is NOT an in-sample artifact."""
    designs = {
        "field deficit": lambda c: [c.deficit_max.to_numpy() / 1000],
        "2D state: 1/TTC_end + dy": lambda c: [1 / c.ttc_end.to_numpy(), c.dy_min.to_numpy()],
        "TTC_nom + exposure time": lambda c: [c.ttc_nom.to_numpy(), c.t_end.to_numpy()],
        "1/TTC_end + exposure time": lambda c: [1 / c.ttc_end.to_numpy(), c.t_end.to_numpy()],
    }

    def fit_predict(train, test, make):
        Xtr = np.column_stack([np.ones(len(train))] + make(train))
        Xte = np.column_stack([np.ones(len(test))] + make(test))
        ktr = (train.p * train.n).to_numpy()
        ntr = train.n.to_numpy()

        def nll(b):
            p = np.clip(norm.cdf(Xtr @ b), 1e-9, 1 - 1e-9)
            return -(ktr * np.log(p) + (ntr - ktr) * np.log(1 - p)).sum()

        best = None
        for seed in range(5):
            rng = np.random.default_rng(seed)
            res = minimize(nll, rng.normal(0, 0.5, Xtr.shape[1]), method="Nelder-Mead",
                           options={"maxiter": 20000, "xatol": 1e-8, "fatol": 1e-8})
            if best is None or res.fun < best.fun:
                best = res
        return norm.cdf(Xte @ best.x)

    for scheme, key in [("leave-one-criticality-out", "criticality"),
                        ("leave-one-timepoint-out", "timepoint")]:
        print(f"\n{scheme}:")
        for name, make in designs.items():
            preds, obss = [], []
            for held in cells[key].unique():
                tr, te = cells[cells[key] != held], cells[cells[key] == held]
                preds += list(fit_predict(tr, te, make))
                obss += list(te.p)
            preds, obss = np.array(preds), np.array(obss)
            print(f"  {name:28s} RMSE={np.sqrt(np.mean((preds - obss) ** 2)):.3f} "
                  f"corr={np.corrcoef(preds, obss)[0, 1]:.3f}")


if __name__ == "__main__":
    main()
