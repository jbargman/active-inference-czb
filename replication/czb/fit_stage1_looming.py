"""Card G1.Q1: the stage-1 hierarchical fit re-run on the GATED LOOMING rule.

THE PRE-REGISTRATION. Everything in this docstring was written before the run.

Why
---
Stage 1 (`fit_stage1.py` -> `out/stage1_summary.md`) estimates the per-driver comfort-zone
LEVEL on study 1's Random cut-in trials with the covariate `deficit_max`, the
active-inference field. Since then, on the SECOND cut-in study, the field was ruled
against as a criticality axis (`out/cutin2_field_vs_gap.md`), the best axis was found to
be the optical expansion rate (`cutin2_looming.py` -> `out/cutin2_looming.md`)

    theta_dot = W * v_rel / (gap^2 + W^2 / 4),      W the cut-in vehicle's width,

and an anticipatory lateral binding GATE in front of it was CREDITED
(`cutin2_gate.py` -> `out/cutin2_gate.md`). Jonas has ruled (query G1.Q1) that the
stage-1 estimator be re-run on that gated looming rule for the cut-in. This script does
exactly that, and nothing else: it adds files, it changes no existing script.

The models (four, all on the same 3 096 Random cut-in trials and the same code path)
-----------------------------------------------------------------------------------
Per-driver level with a hierarchical lapse, driver effects integrated out by
Gauss-Hermite quadrature (48 nodes per dimension, product grid, chunked) and Laplace
applied to the hyperparameters only -- the estimator card A.1 validated:

    c_i = mu + sigma_pop * z_i,          z_i ~ Normal(0, 1)     [LEVEL ON THE LOG SCALE]
    b_i = sigmoid(b_loc + sigma_b * z2_i)
    P(intervene) = b_i + (1 - b_i) * w_gate * Phi((x - c_i) / sigma_resp)

The level is LINEAR in the log-scale parameterisation here, not `exp(mu + sigma_pop z)`
as in `fit_stage1`, because the covariate is itself a log (`log theta_dot`) and takes
negative values: a positivity-constrained level would be meaningless on it. This is the
one structural change to the estimator; everything else -- quadrature, optimizer, prior
family, folds -- is `fit_stage1`'s.

    (L-gated)   x = log(theta_dot),           w_gate as below      <- the candidate primary
    (L-ungated) x = log(theta_dot),           w_gate := 1
    (D-gated)   x = log(deficit_max + 1),     w_gate as below
    (D-ungated) x = log(deficit_max + 1),     w_gate := 1          <- the deficit axis,
                                                                      same code path

The deficit rows exist ONLY so that the axis comparison is like-for-like: the same level
parameterisation, the same priors-for-this-covariate rule, the same folds, the same
optimizer. `+1` inside the log keeps the pre-onset zeros finite; it shifts the axis, it
does not reorder it.

The gate, with its parameters FIXED
-----------------------------------
    w_gate = Phi( (m_lat - (l0 + ldot * t_enc)) / s_l )
    l0(t)  = |y_rel(t)| - (W_tar + W_ego) / 2        edge-to-edge lateral clearance [m]
    ldot(t)= backward difference of l0 over 0.3 s
    m_lat  = 0.149 m,   s_l = 0.990 m,   t_enc = 3.0 s

m_lat and s_l are read from `out/cutin2_gate.md` section 3, column "(k) gated" (the full
post-onset fit on study 2), and are held FIXED here: study 1's design does not vary
lateral clearance across its cells, so it cannot identify them. t_enc = 3.0 s was fixed
on study 2 too. Nothing about the gate is fitted in this script.

The covariate, and where it is read
-----------------------------------
Per trial, mirroring `comfortzone.czb_data.random_cutin_trials` exactly: the three Random
cut-in stimulus traces are loaded with the same loader, `cutin_predictors` supplies
t, gap_m, v_rel, y_rel; the covariate is read at the trial's covariate time with
czb_data's own `_cov_end` (clip end = onset + 0.3(k-1) s, except C1, which reads at
C1_COV_END_S = -0.15 s) and `_at_time` (last frame at or before).

theta_dot is the INSTANTANEOUS value at the covariate time, NOT a running maximum. This
is deliberate and is the substantive difference from `deficit_max`: the looming rule is a
STATE threshold -- the driver acts when the current expansion rate exceeds their level --
whereas the field covariate was a running maximum (an "ever exceeded" rule). w_gate is
likewise instantaneous. Consequently the shown-clip accumulation window
(RANDOM_CLIP_LEAD_S = 10 s) has no effect on the looming covariate and is not applied to
it; it is still applied to `deficit_max`, whose running maximum needs it.

Priors (the A.1 family, re-centred on each covariate)
-----------------------------------------------------
    mu         ~ Normal(median(x), 1.0)             [median x, NOT log median x: the
                                                     level lives on the covariate's own
                                                     log scale]
    sigma_pop  ~ HalfNormal(0.5)
    sigma_resp ~ LogNormal(log(IQR(x)/2), 0.5)
    b_loc      ~ the weak location prior of `fit_stage1._nlp_2d`, unchanged
    sigma_b    ~ HalfNormal(1.0) on the logit scale, unchanged

Held-out likelihood, percentiles, predictive check
--------------------------------------------------
* LOPO: leave-one-participant-out, summed held-out log-likelihood, on the SAME folds
  `fit_stage1.main` uses -- `np.linspace(0, n_drivers - 1, 15).astype(int)`, 15 evenly
  spaced participants. `fit_stage1.lopo_loglik` cannot be reused (it hard-codes the
  exponential level and has no gate), so it is RE-IMPLEMENTED here line-for-line with
  those two changes and nothing else; this is stated in the report.
* Percentiles: 5, 20, 50, 80, 95, by the same Laplace route as
  `fit_stage1.percentiles_with_ci` -- the delta method on the Laplace covariance of
  (mu, log sigma_pop). On the log scale the percentile is mu + sigma_pop * z_q, so the
  Jacobian is [1, z_q * sigma_pop] instead of that function's [val, val z_q sigma_pop];
  the bounds are then exponentiated (a monotone map, so the interval carries over).
* C1 predictive check: population-averaged P(intervene) at the three pre-onset cells,
  integrating BOTH driver effects over the fitted population (the R.1 fix), against
  observed -- for the gated and the ungated looming fits.
* Card C translation (`percentile_sensitivity.py`): its `onset_time` crosses a level
  against the running-max deficit along each stimulus. The same logic on the looming
  level is a first-crossing of the level by theta_dot(t), which is a few lines, so it is
  redone here rather than deferred.

THE DECISION RULE (pre-stated)
------------------------------
The gated looming axis REPLACES the deficit axis as the stage-1 primary iff
  (a) its LOPO log-likelihood exceeds the deficit axis's by more than 10 units -- the
      magnitude `fit_stage1` itself treated as decisive between its own variants -- where
      the deficit comparator is the better-LOPO of (D-gated, D-ungated), i.e. the same
      code path; AND
  (b) its C1 predictive check is at least as good, measured as the mean absolute
      difference between predicted and observed pre-onset rates over the three C1 cells,
      against the same deficit comparator.
Otherwise: report, and leave the stage-1 primary unchanged. This script does not edit
`out/stage1_summary.md`, the worklog, the README or the handover under any outcome.

ASSUMPTIONS (stated before the run, not revisited after seeing the numbers)
--------------------------------------------------------------------------
1. `gap_m` from `cutin_predictors` (bumper-to-bumper longitudinal gap) is the `g` of the
   looming formula, the study-2 analogue of that script's `cells.distance`; `v_rel`
   (= v_ego - v_tar, positive when closing) is its `dv`. Frames with v_rel <= 0 or
   gap <= 0 would make log(theta_dot) undefined; the covariate times are checked for this
   and the run reports rather than silently clipping.
2. W in theta_dot is the TARGET's width `tr.tar_wid` (study 2's convention: the cut-in
   vehicle's own width). The gate's half-width correction uses (W_tar + W_ego) / 2, with
   W_ego read from the trace CSV's `Width_m` for the ego vehicle, identified exactly as
   `cutin2_gate.ego_width` does it (that function is imported, not re-implemented).
3. `y_rel` is already ego-relative (`load_cutin_trace` returns `tg.Location_Y -
   e.Location_Y`), so centre-to-centre lateral separation is |y_rel| -- assumption 1 of
   `cutin2_gate.py`, which its `lateral_dist` validation passed on study 2.
4. ldot: study 2 divided the 0.3 s backward difference by a fixed 0.3 s, its traces
   running at ~30 Hz so the sampled span is within ~3% of 0.3 s. Study 1's traces run at
   10 Hz, where the last sample at or before t - 0.3 s can be up to 0.1 s further back --
   a 33% error in the divisor. The PRIMARY ldot here therefore divides by the ACTUAL
   sampled span (t_i - t_j), the quantity study 2 was approximating; the fixed-0.3
   variant is computed too and its gate values are reported alongside, so the choice is
   visible rather than buried.
5. The response is the same binary `intervene` on the same trials as `fit_stage1`; the
   ordered braking-expectation model is NOT refitted here (G1.Q1 asks for the level).

Run:     python replication/czb/fit_stage1_looming.py
         python replication/czb/fit_stage1_looming.py --covariates-only
Outputs: replication/czb/out/stage1_looming.md
         replication/czb/out/stage1_looming_cells.csv
         replication/czb/out/log_stage1_looming.txt
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))

from comfortzone.czb_data import (RANDOM_CUTIN_TRACES, _at_time, _cov_end,  # noqa: E402
                                  load_joint, TIMEPOINT_OFFSET_S)
from comfortzone.cutin import cutin_predictors, load_cutin_trace          # noqa: E402
from fit_recovery import NORMAL, Priors, _gh_nodes                        # noqa: E402
from fit_stage1 import NODE_CHUNK, N_GH_2D, _logsumexp, _ncdf             # noqa: E402
from cutin2_gate import ego_width                                         # noqa: E402

OUT = HERE / "out"
torch.set_default_dtype(torch.float64)
sys.stdout.reconfigure(errors="replace")

# --- the gate, fixed. Source: out/cutin2_gate.md section 3, column "(k) gated". -------
M_LAT = 0.149          # m
S_L = 0.990            # m
T_ENC = 3.0            # s (fixed on study 2 as well)

PERCENTILES = [5, 20, 50, 80, 95]
STEP_PCTS = list(range(50, 100, 5))     # for the card-C 5-point-step translation
LOPO_FOLDS = 15
RAD2DEG = 180.0 / np.pi


# ----------------------------------------------------------------------------------
# 1. covariates
# ----------------------------------------------------------------------------------
def looming_field(path: Path) -> pd.DataFrame:
    """theta_dot, log theta_dot, l0, ldot and w_gate along one Random cut-in stimulus.

    Same loader and same predictor code as `czb_data.stimulus_field`; the difference is
    that nothing here is accumulated -- these are instantaneous states.
    """
    tr = load_cutin_trace(path)
    df = cutin_predictors(tr)
    df["t_since_onset"] = df.t - df.t.iloc[tr.onset_idx]

    w_tar = float(tr.tar_wid)
    w_ego = ego_width(Path(path), tr)
    gap = df.gap_m.to_numpy(float)
    dv = df.v_rel.to_numpy(float)
    theta_dot = w_tar * dv / (gap ** 2 + w_tar ** 2 / 4.0)
    df["theta_dot"] = theta_dot
    with np.errstate(divide="ignore", invalid="ignore"):
        df["x_loom"] = np.log(theta_dot)

    l0 = np.abs(df.y_rel.to_numpy(float)) - (w_tar + w_ego) / 2.0
    t = df.t.to_numpy(float)
    j = np.searchsorted(t, t - 0.3, side="right") - 1
    j = np.clip(j, 0, len(t) - 1)
    span = t - t[j]
    ldot = np.where(span > 1e-9, (l0 - l0[j]) / np.where(span > 1e-9, span, 1.0), 0.0)
    ldot_fixed = (l0 - l0[j]) / 0.3
    df["l0"] = l0
    df["ldot"] = ldot
    df["ldot_fixed03"] = ldot_fixed
    df["w_gate"] = _gate(l0, ldot)
    df["w_gate_fixed03"] = _gate(l0, ldot_fixed)
    df.attrs["w_tar"], df.attrs["w_ego"] = w_tar, w_ego
    return df


def _gate(l0: np.ndarray, ldot: np.ndarray) -> np.ndarray:
    from scipy.stats import norm
    return norm.cdf((M_LAT - (l0 + ldot * T_ENC)) / S_L)


def build_trials() -> pd.DataFrame:
    """One row per Random cut-in trial, with the looming covariates and the gate.

    Mirrors `czb_data.random_cutin_trials`: same joint table, same filter, same
    timepoint offsets, same `_cov_end` / `_at_time` reading rule. The deficit columns
    come from `random_cutin_trials` itself so nothing is re-implemented there.
    """
    from comfortzone.czb_data import random_cutin_trials
    base = random_cutin_trials()

    j = load_joint()
    r = j[(j.design == "Random") & (j.scenario == "cutin_car")].copy()
    fields = {c: looming_field(p) for c, p in RANDOM_CUTIN_TRACES.items()}
    r["t_end"] = r.timepoint.map(TIMEPOINT_OFFSET_S)
    t_cov = _cov_end(r.t_end, r.timepoint, False)
    cols = {}
    for col in ("theta_dot", "x_loom", "w_gate", "w_gate_fixed03", "l0", "ldot", "gap_m",
                "v_rel"):
        cols[col] = [_at_time(fields[c], t, col)
                     for c, t in zip(r.criticality_label, t_cov)]
    out = base.copy()
    for col, vals in cols.items():
        out[col] = vals
    out.attrs["fields"] = fields
    return out


# ----------------------------------------------------------------------------------
# 2. the fit: fit_stage1's hierarchical-lapse estimator with a gate and a linear level
# ----------------------------------------------------------------------------------
def priors_log_scale(x: np.ndarray) -> Priors:
    """`fit_recovery.priors_for`, re-centred for a level that lives on the log scale.

    `priors_for` sets mu_loc = log(median x) because there the level is exp(mu). Here
    the level IS on the covariate's scale, so mu_loc = median(x). sigma_resp is
    unchanged: LogNormal(log(IQR(x)/2), 0.5).
    """
    med = float(np.median(x))
    iqr = float(np.percentile(x, 75) - np.percentile(x, 25))
    return Priors(mu_loc=med, sigma_resp_loc=float(np.log(max(iqr / 2.0, 1e-6))))


def _marginal_2d_gated(phi, xt, gt, yt, pidt, n_drivers, z1, z2, lw):
    """`fit_stage1._marginal_2d` with (a) a per-trial gate multiplier and (b) a level
    that is linear rather than exponential in (mu, sigma_pop)."""
    mu, sigma_pop = phi[0], torch.exp(phi[1])
    sigma_resp, b_loc, sigma_b = torch.exp(phi[2]), phi[3], torch.exp(phi[4])
    acc = torch.full((n_drivers, len(z1)), -np.inf)
    for s in range(0, len(z1), NODE_CHUNK):
        e = min(s + NODE_CHUNK, len(z1))
        c = mu + sigma_pop * z1[s:e]                      # LOG-SCALE level, no exp
        b = torch.sigmoid(b_loc + sigma_b * z2[s:e])
        p = b + (1.0 - b) * gt[:, None] * NORMAL.cdf(
            (xt[:, None] - c[None, :]) / sigma_resp)
        p = p.clamp(1e-12, 1.0 - 1e-12)
        ll = yt[:, None] * torch.log(p) + (1.0 - yt[:, None]) * torch.log1p(-p)
        acc[:, s:e] = torch.zeros(n_drivers, e - s).index_add(0, pidt, ll)
    return torch.logsumexp(acc + lw[None, :], dim=1)


def _nlp_2d_gated(phi, xt, gt, yt, pidt, n_drivers, pr, z1, z2, lw):
    """`fit_stage1._nlp_2d`, unchanged except for the marginal it calls and that the mu
    prior is Normal(median x, 1) on the level's own (log) scale."""
    sigma_pop, sigma_b = torch.exp(phi[1]), torch.exp(phi[4])
    ll = _marginal_2d_gated(phi, xt, gt, yt, pidt, n_drivers, z1, z2, lw).sum()
    lp = -0.5 * ((phi[0] - pr.mu_loc) / pr.mu_scale) ** 2
    lp = lp - 0.5 * (sigma_pop / pr.sigma_pop_scale) ** 2 + phi[1]
    lp = lp - 0.5 * ((phi[2] - pr.sigma_resp_loc) / pr.sigma_resp_scale) ** 2
    lp = lp - 0.5 * (torch.sigmoid(phi[3]) / 0.3) ** 2
    lp = lp - 0.5 * (sigma_b / 1.0) ** 2 + phi[4]
    return -(ll + lp)


def fit_hier_lapse_gated(x, g, y, pid, pr, n_gh=N_GH_2D) -> dict:
    """`fit_stage1.fit_hier_lapse` with the gate and the linear level. Same quadrature
    (48 nodes/dim, product grid, chunked), same L-BFGS settings, same init."""
    xt, gt = torch.as_tensor(x.copy()), torch.as_tensor(g.copy())
    yt = torch.as_tensor(y.copy())
    pidt = torch.as_tensor(pid, dtype=torch.long)
    n_drivers = int(pid.max() + 1)
    zz, ww = _gh_nodes(n_gh)
    z1 = torch.as_tensor(np.repeat(zz, n_gh))
    z2 = torch.as_tensor(np.tile(zz, n_gh))
    lw = torch.as_tensor(np.log(np.outer(ww, ww).ravel()))

    init = np.array([pr.mu_loc, np.log(0.4), pr.sigma_resp_loc,
                     np.log(0.09 / 0.91), np.log(0.5)])
    phi = torch.tensor(init, requires_grad=True)
    opt = torch.optim.LBFGS([phi], max_iter=250, tolerance_grad=1e-9,
                            tolerance_change=1e-13, history_size=40,
                            line_search_fn="strong_wolfe")

    def closure():
        opt.zero_grad()
        loss = _nlp_2d_gated(phi, xt, gt, yt, pidt, n_drivers, pr, z1, z2, lw)
        loss.backward()
        return loss

    opt.step(closure)
    with torch.no_grad():
        val = float(_nlp_2d_gated(phi, xt, gt, yt, pidt, n_drivers, pr, z1, z2, lw))
    H = torch.autograd.functional.hessian(
        lambda t: _nlp_2d_gated(t, xt, gt, yt, pidt, n_drivers, pr, z1, z2, lw), phi)
    try:
        cov = torch.linalg.inv(H).numpy()
        se = np.sqrt(np.clip(np.diag(cov), 0.0, None))
        ok = bool(np.all(np.isfinite(se)))
    except Exception:
        cov, se, ok = np.full((5, 5), np.nan), np.full(5, np.nan), False
    t = phi.detach().numpy()
    return {"mu": t[0], "se_mu": se[0], "sigma_pop": np.exp(t[1]),
            "se_sigma_pop": np.exp(t[1]) * se[1], "sigma_resp": np.exp(t[2]),
            "b": float(torch.sigmoid(phi[3]).detach()), "sigma_b": np.exp(t[4]),
            "neg_log_post": val, "se_ok": ok, "cov": cov, "phi": t}


def lopo_loglik_gated(x, g, y, pid, pr, folds) -> float:
    """`fit_stage1.lopo_loglik`, hierarchical branch, re-implemented with the gate and
    the linear level. Identical otherwise: the same product Gauss-Hermite grid at the
    same node count as the fit, the held-out driver's two effects integrated over the
    fitted population."""
    zz2, ww2 = _gh_nodes(N_GH_2D)
    tot = 0.0
    for held in folds:
        tr = pid != held
        pid_tr = np.unique(pid[tr], return_inverse=True)[1]
        f = fit_hier_lapse_gated(x[tr], g[tr], y[tr], pid_tr, pr)
        xh, yh, gh = x[~tr], y[~tr], g[~tr]
        c = f["mu"] + f["sigma_pop"] * zz2
        bb = 1 / (1 + np.exp(-(f["phi"][3] + f["sigma_b"] * zz2)))
        p = bb[None, None, :] + (1 - bb[None, None, :]) * gh[:, None, None] * _ncdf(
            (xh[:, None, None] - c[None, :, None]) / f["sigma_resp"])
        p = np.clip(p, 1e-12, 1 - 1e-12)
        ll = (yh[:, None, None] * np.log(p)
              + (1 - yh[:, None, None]) * np.log1p(-p)).sum(axis=0)
        lw = np.log(ww2)[:, None] + np.log(ww2)[None, :]
        tot += float(_logsumexp((ll + lw).ravel()))
    return tot


def percentiles_log(f: dict) -> list[tuple[int, float, float, float]]:
    """Population percentiles of the LOG-SCALE level, delta-method 95% CIs.

    The same Laplace route as `fit_stage1.percentiles_with_ci`: the delta method on the
    Laplace covariance of (mu, log sigma_pop). Here level = mu + sigma_pop * z_q, so
    J = [1, z_q * sigma_pop].
    """
    from scipy.stats import norm
    cov, mu, sp = f["cov"], f["mu"], f["sigma_pop"]
    out = []
    for q in PERCENTILES + [p for p in STEP_PCTS if p not in PERCENTILES]:
        zq = norm.ppf(q / 100.0)
        val = mu + sp * zq
        J = np.array([1.0, zq * sp])
        var = float(J @ cov[np.ix_([0, 1], [0, 1])] @ J)
        se = np.sqrt(max(var, 0.0))
        out.append((q, val, val - 1.96 * se, val + 1.96 * se))
    return sorted(out)


def c1_predictive_gated(x, g, y, r, f: dict) -> list[tuple[str, float, float]]:
    """`fit_stage1.c1_predictive` for this model: population-averaged P(intervene) at
    the three pre-onset cells, integrating BOTH driver effects (the R.1 fix)."""
    zz, ww = _gh_nodes(150)
    c = f["mu"] + f["sigma_pop"] * zz
    bb = 1 / (1 + np.exp(-(f["phi"][3] + f["sigma_b"] * zz)))
    rows = []
    for crit in ("TTC4", "TTC6", "TTC8"):
        m = (r.timepoint == "C1").to_numpy() & (r.criticality == crit).to_numpy()
        if not m.any():
            continue
        xv, gv = float(x[m][0]), float(g[m][0])
        p = bb[None, :] + (1 - bb[None, :]) * gv * _ncdf((xv - c[:, None]) / f["sigma_resp"])
        pred = float((ww[:, None] * ww[None, :] * p).sum())
        rows.append((crit, float(y[m].mean()), pred))
    return rows


def onset_time_theta(field: pd.DataFrame, level_log: float) -> float:
    """Card C's `onset_time`, on the looming axis: the first time since manoeuvre onset
    at which theta_dot crosses exp(level_log), linearly interpolated. NaN if never."""
    t = field.t_since_onset.to_numpy()
    d = field.theta_dot.to_numpy()
    lev = float(np.exp(level_log))
    m = t >= -10.0                       # the shown clip, as RANDOM_CLIP_LEAD_S defines it
    t, d = t[m], d[m]
    above = d >= lev
    if not above.any():
        return float("nan")
    i = int(np.argmax(above))
    if i == 0:
        return float(t[0])
    t0, t1, d0, d1 = t[i - 1], t[i], d[i - 1], d[i]
    return float(t0 + (lev - d0) / max(d1 - d0, 1e-9) * (t1 - t0))


# ----------------------------------------------------------------------------------
# 3. the run
# ----------------------------------------------------------------------------------
def cell_table(r: pd.DataFrame) -> pd.DataFrame:
    return (r.groupby(["criticality", "timepoint"])
             .agg(n=("intervene", "size"), p=("intervene", "mean"),
                  theta_dot=("theta_dot", "mean"), x_loom=("x_loom", "mean"),
                  w_gate=("w_gate", "mean"), w_gate_f=("w_gate_fixed03", "mean"),
                  l0=("l0", "mean"), ldot=("ldot", "mean"),
                  deficit=("deficit_max", "mean"))
             .reset_index())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--covariates-only", action="store_true")
    ap.add_argument("--lopo-folds", type=int, default=LOPO_FOLDS)
    args = ap.parse_args()
    t0 = time.time()

    r = build_trials()
    fields = r.attrs["fields"]
    pid = r.participant.factorize()[0].astype(int)
    y = r.intervene.to_numpy(float)
    n_drivers = int(pid.max() + 1)
    print(f"{len(r)} trials, {n_drivers} drivers", flush=True)

    cells = cell_table(r)
    cells.to_csv(OUT / "stage1_looming_cells.csv", index=False)
    print(cells.to_string(index=False), flush=True)

    bad = (~np.isfinite(r.x_loom.to_numpy(float))).sum()
    print(f"non-finite log(theta_dot) at covariate times: {bad}", flush=True)
    g_c1 = r.w_gate[r.timepoint == "C1"]
    g_post = r.w_gate[r.timepoint != "C1"]
    print(f"w_gate  C1 {g_c1.min():.4f}-{g_c1.max():.4f}; "
          f"post {g_post.min():.4f}-{g_post.max():.4f}", flush=True)
    if args.covariates_only:
        return
    if bad:
        raise RuntimeError(f"{bad} trials have non-finite log(theta_dot)")

    x_loom = r.x_loom.to_numpy(float)
    x_def = np.log(r.deficit_max.to_numpy(float) + 1.0)
    gate = r.w_gate.to_numpy(float)
    ones = np.ones_like(gate)
    folds = np.linspace(0, n_drivers - 1,
                        min(args.lopo_folds, n_drivers)).astype(int).tolist()

    variants = {
        "L-gated": (x_loom, gate, "log(theta_dot)", "gated"),
        "L-ungated": (x_loom, ones, "log(theta_dot)", "ungated"),
        "D-gated": (x_def, gate, "log(deficit_max + 1)", "gated"),
        "D-ungated": (x_def, ones, "log(deficit_max + 1)", "ungated"),
    }
    fits, lopo, priors = {}, {}, {}
    for name, (xv, gv, _, _) in variants.items():
        pr = priors_log_scale(xv)
        priors[name] = pr
        print(f"fitting {name} ...", flush=True)
        fits[name] = fit_hier_lapse_gated(xv, gv, y, pid, pr)
        print(f"  mu {fits[name]['mu']:.4f}, sigma_pop {fits[name]['sigma_pop']:.4f}, "
              f"sigma_resp {fits[name]['sigma_resp']:.4f}, se_ok {fits[name]['se_ok']}",
              flush=True)
        print(f"  LOPO over {len(folds)} folds ...", flush=True)
        lopo[name] = lopo_loglik_gated(xv, gv, y, pid, pr, folds)
        print(f"  LOPO {lopo[name]:.2f}   ({(time.time() - t0) / 60:.1f} min)", flush=True)

    # ------------------------------------------------------------------ report -----
    L = ["# Card G1.Q1 — stage 1 re-fitted on the gated looming rule", "",
         "Generated by `replication/czb/fit_stage1_looming.py`; models, fixed gate "
         "values, priors, folds, decision rule and assumptions pre-stated in its "
         "docstring before the run. Do not edit by hand.", "",
         "**Specification.** Hierarchical-lapse estimator of `fit_stage1` (48-node "
         "product Gauss-Hermite quadrature over the two driver effects, Laplace on the "
         "hyperparameters only, L-BFGS), with two changes: the level is LINEAR on the "
         "covariate's log scale (`c_i = mu + sigma_pop z_i`, not `exp(...)`), and the "
         "response carries a fixed per-trial gate multiplier "
         "`P = b_i + (1 - b_i) * w_gate * Phi((x - c_i)/sigma_resp)`. Gate parameters "
         f"m_lat = {M_LAT:.3f} m, s_l = {S_L:.3f} m, t_enc = {T_ENC:.1f} s, all FIXED, "
         "from `out/cutin2_gate.md` section 3 (study 2's full post-onset fit); study "
         "1's design cannot identify them. theta_dot is the INSTANTANEOUS optical "
         "expansion rate at the covariate time, not a running maximum: the looming rule "
         "is a state threshold.", "",
         f"{len(r)} Random cut-in trials, {n_drivers} drivers, {len(cells)} cells.", "",
         "## 1 The covariates, per cell", "",
         "Covariate times exactly as `czb_data.random_cutin_trials` reads them: clip end "
         "= onset + 0.3(k-1) s, except C1 at -0.15 s.", "",
         "| criticality | timepoint | n | observed P | theta_dot [rad/s] | "
         "x = log(theta_dot) | w_gate | l0 [m] | ldot [m/s] | deficit_max |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for _, c in cells.iterrows():
        L.append(f"| {c.criticality} | {c.timepoint} | {int(c.n)} | {c.p:.3f} | "
                 f"{c.theta_dot:.4f} | {c.x_loom:+.3f} | {c.w_gate:.4f} | {c.l0:.3f} | "
                 f"{c.ldot:+.3f} | {c.deficit:.0f} |")
    L += ["",
          f"Widths used: target {fields['TTC4'].attrs['w_tar']:.3f} m, ego "
          f"{fields['TTC4'].attrs['w_ego']:.3f} m (TTC4 trace; the three traces agree "
          f"to "
          f"{max(abs(fields[c].attrs['w_tar'] - fields['TTC4'].attrs['w_tar']) for c in fields):.3f}"
          " m on the target width).", "",
          "**Gate validation against study 2.** There, w_gate was 0.063-0.070 at the "
          "pre-onset cells and 0.55-1.00 post-onset.", "",
          "| set | w_gate min | max | mean | (fixed-0.3 divisor) min | max | mean |",
          "|---|---|---|---|---|---|---|"]
    for lab, sub in (("C1 (pre-onset)", r[r.timepoint == "C1"]),
                     ("C2-C6 (post-onset)", r[r.timepoint != "C1"])):
        L.append(f"| {lab} | {sub.w_gate.min():.4f} | {sub.w_gate.max():.4f} | "
                 f"{sub.w_gate.mean():.4f} | {sub.w_gate_fixed03.min():.4f} | "
                 f"{sub.w_gate_fixed03.max():.4f} | {sub.w_gate_fixed03.mean():.4f} |")

    L += ["", "## 2 Fitted hyperparameters", "",
          "| variant | covariate | gate | mu (level median, log scale) | sigma_pop | "
          "sigma_resp | lapse b (sd) | LOPO log-lik | SEs |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, (xv, gv, lab, gl) in variants.items():
        f = fits[name]
        L.append(f"| {name} | `{lab}` | {gl} | {f['mu']:+.4f} (SE {f['se_mu']:.4f}) | "
                 f"{f['sigma_pop']:.4f} (SE {f['se_sigma_pop']:.4f}) | "
                 f"{f['sigma_resp']:.4f} | {f['b']:.4f} (sd {f['sigma_b']:.2f}) | "
                 f"{lopo[name]:.2f} | {'ok' if f['se_ok'] else 'FAILED'} |")
    L += ["",
          f"LOPO: leave-one-participant-out over the {len(folds)} evenly spaced "
          f"participants `fit_stage1.main` uses (`np.linspace(0, {n_drivers - 1}, "
          f"{len(folds)}).astype(int)`), the same folds for every variant. "
          "`fit_stage1.lopo_loglik` could NOT be reused -- it hard-codes the "
          "exponential level and has no gate -- so it is re-implemented here with those "
          "two changes and nothing else (same product grid, same node count, held-out "
          "driver's effects integrated over the fitted population).", ""]

    # ---- percentiles ----
    pl = {n: percentiles_log(fits[n]) for n in ("L-gated", "L-ungated")}
    L += ["## 3 Population percentiles of the looming level", "",
          "Level on the log(theta_dot) scale with delta-method 95% CIs (the Laplace "
          "route of `fit_stage1.percentiles_with_ci`, Jacobian adapted to the linear "
          "level), exponentiated to theta_dot.", "",
          "| variant | percentile | level (log theta_dot) | 95% CI (log) | "
          "theta_dot [rad/s] | 95% CI [rad/s] | theta_dot [deg/s] |",
          "|---|---|---|---|---|---|---|"]
    for name in ("L-gated", "L-ungated"):
        for q, val, lo, hi in pl[name]:
            if q not in PERCENTILES:
                continue
            L.append(f"| {name} | {q}th | {val:+.4f} | [{lo:+.4f}, {hi:+.4f}] | "
                     f"{np.exp(val):.4f} | [{np.exp(lo):.4f}, {np.exp(hi):.4f}] | "
                     f"{np.exp(val) * RAD2DEG:.3f} |")
    pd_ = {n: percentiles_log(fits[n]) for n in ("D-gated", "D-ungated")}
    L += ["", "For reference, the deficit axis on the identical code path "
          "(level on the log(deficit_max + 1) scale, back-transformed to deficit "
          "units):", "",
          "| variant | percentile | level (log units) | deficit units | 95% CI "
          "(deficit units) |", "|---|---|---|---|---|"]
    for name in ("D-gated", "D-ungated"):
        for q, val, lo, hi in pd_[name]:
            if q not in PERCENTILES:
                continue
            L.append(f"| {name} | {q}th | {val:+.4f} | {np.exp(val) - 1:.0f} | "
                     f"[{np.exp(lo) - 1:.0f}, {np.exp(hi) - 1:.0f}] |")

    # ---- C1 predictive ----
    c1 = {n: c1_predictive_gated(variants[n][0], variants[n][1], y, r, fits[n])
          for n in ("L-gated", "L-ungated", "D-gated", "D-ungated")}
    L += ["", "## 4 Pre-onset (C1) posterior predictive", "",
          "| variant | criticality | observed P | predicted | difference |",
          "|---|---|---|---|---|"]
    for name in ("L-gated", "L-ungated"):
        for crit, obs, pred in c1[name]:
            L.append(f"| {name} | {crit} | {obs:.3f} | {pred:.3f} | {pred - obs:+.3f} |")
    mad = {n: float(np.mean([abs(p - o) for _, o, p in c1[n]])) for n in c1}
    L += ["",
          "Mean |predicted - observed| over the three C1 cells: "
          + ", ".join(f"{n} {mad[n]:.4f}" for n in ("L-gated", "L-ungated",
                                                    "D-gated", "D-ungated")) + ".", ""]

    # ---- card C translation ----
    crits = list(fields)
    L += ["## 5 Card C translation: what a 5-point percentile step costs, in seconds",
          "",
          "Card C (`percentile_sensitivity.py`) crosses each percentile level against "
          "the running-max deficit along the three Random stimuli. Its logic transfers "
          "directly: here the implied trigger onset is the first time theta_dot(t) "
          "crosses the level. (The gate is NOT applied to this crossing -- it is a "
          "property of the level, and the gate would only delay the onset further.)", "",
          "| percentile | level theta_dot [rad/s] | "
          + " | ".join(f"onset {c} [s]" for c in crits) + " | "
          + " | ".join(f"{c} CI width [s]" for c in crits) + " |",
          "|---|---|" + "---|" * (2 * len(crits))]
    rows = []
    for q, val, lo, hi in pl["L-gated"]:
        if q not in STEP_PCTS:
            continue
        on = {c: onset_time_theta(fields[c], val) for c in crits}
        ci = {c: onset_time_theta(fields[c], hi) - onset_time_theta(fields[c], lo)
              for c in crits}
        rows.append((q, val, on, ci))
        L.append(f"| {q}th | {np.exp(val):.4f} | "
                 + " | ".join(f"{on[c]:.2f}" for c in crits) + " | "
                 + " | ".join(f"{abs(ci[c]):.2f}" for c in crits) + " |")
    L += ["", "| stimulus | mean |d(onset)| per 5 pct pts [s] | max [s] | "
          "mean onset shift across the 95% CI [s] |", "|---|---|---|---|"]
    bits = []
    for c in crits:
        o = np.array([rw[2][c] for rw in rows])
        st = np.abs(np.diff(o))
        cw = np.abs(np.array([rw[3][c] for rw in rows]))
        m_step = float(np.nanmean(st)) if np.isfinite(st).any() else float("nan")
        mx = float(np.nanmax(st)) if np.isfinite(st).any() else float("nan")
        m_ci = float(np.nanmean(cw))
        L.append(f"| {c} | {m_step:.3f} | {mx:.3f} | {m_ci:.3f} |")
        bits.append((m_step, m_ci))
    ratio = float(np.nanmean([b[0] / max(b[1], 1e-9) for b in bits]))
    L += ["",
          f"**Reading (computed).** Averaged over the three stimuli, one 5-point step of "
          f"the percentile choice moves the implied trigger onset by "
          f"{np.nanmean([b[0] for b in bits]):.3f} s, against "
          f"{np.nanmean([b[1] for b in bits]):.3f} s implied by the percentile's own "
          f"95% CI -- a ratio of {ratio:.1f}. "
          + ("The choice of percentile dominates the estimation error on this axis too, "
             "as card C found on the deficit axis." if ratio > 2 else
             "On this axis the two are of comparable size, unlike card C's finding on "
             "the deficit axis."), ""]

    # ---- the pre-stated decision ----
    d_ref = max(("D-gated", "D-ungated"), key=lambda n: lopo[n])
    d_lopo = lopo["L-gated"] - lopo[d_ref]
    cond_a = d_lopo > 10.0
    cond_b = mad["L-gated"] <= mad[d_ref]
    L += ["## 6 The pre-stated decision", "",
          f"Deficit comparator: **{d_ref}** (the better-LOPO deficit variant on the "
          f"identical code path).", "",
          "| criterion | value | threshold | met |", "|---|---|---|---|",
          f"| (a) LOPO(L-gated) - LOPO({d_ref}) | {d_lopo:+.2f} | > +10 | "
          f"{'YES' if cond_a else 'NO'} |",
          f"| (b) C1 mean abs. error, L-gated vs {d_ref} | {mad['L-gated']:.4f} vs "
          f"{mad[d_ref]:.4f} | <= | {'YES' if cond_b else 'NO'} |", "",
          "**Decision: "
          + ("the gated looming axis REPLACES the deficit axis as the stage-1 primary — "
             "both pre-stated conditions are met."
             if (cond_a and cond_b) else
             "the stage-1 primary is LEFT UNCHANGED — "
             + ("condition (a) is not met" if not cond_a else "")
             + ("; " if (not cond_a and not cond_b) else "")
             + ("condition (b) is not met" if not cond_b else "")
             + ". This run is reported, and `out/stage1_summary.md` is not touched.")
          + "**", "",
          "Secondary, no decision attached: the gate is worth "
          f"{lopo['L-gated'] - lopo['L-ungated']:+.2f} LOPO units on the looming axis "
          f"and {lopo['D-gated'] - lopo['D-ungated']:+.2f} on the deficit axis.", "",
          "## 7 Why no cross-scenario transfer test here (card B.4)", "",
          "The transfer test is deliberately NOT attempted on this axis: the "
          "cyclist-overtake stimuli hold the looming rate essentially constant across "
          "their clearance conditions, which are varied laterally, so a looming axis has "
          "nothing to order them by and a null result would measure the stimulus design "
          "rather than the rule. Transfer on a per-scenario form of the boundary is card "
          "EL.2's job, and this run neither anticipates nor pre-empts it.", ""]

    elapsed = time.time() - t0
    L.append(f"Runtime {elapsed / 60:.1f} min.")
    txt = "\n".join(L) + "\n"
    (OUT / "stage1_looming.md").write_text(txt, encoding="utf-8")
    print("\n" + txt)
    print(f"written to {OUT / 'stage1_looming.md'}  ({elapsed / 60:.1f} min)")


if __name__ == "__main__":
    main()
