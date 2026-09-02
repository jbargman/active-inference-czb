"""Card B.3.v2: the left-turn-across-path comparison -- one axis or two, and which (2026-09-02).

THE PRE-REGISTRATION. Written before the run, per `docs/ltap_construction_note.md` section 2.

Data: the 18 Random-design LTAP cells (9 design PET levels x 2 oncoming speeds, 172 trials
each), P(intervene) and n from `Random_Button_Joint.csv` exactly as `ltap_geometry.py`
builds them, joined to the trace geometry from `src/comfortzone/ltap.py` (roles by yaw span;
decision moment t = 13.5 s of trace time, query B3.Q1 resolved by assumption; the loader's
cross-check against `out/ltap_geometry.md` agrees to 1e-14).

Observables at the decision moment, each oriented so that larger means more critical:
    D      the oncoming's distance to the conflict point [m]          x = -log D
    t_sep  arrival-time separation = oncoming arrival - ego exit [s]  x = -log t_sep
           (t_sep is the design PET plus a near-constant 0.7-1.2 s; TTA = D / v_onc is
           its proxy and would give the same folds; t_sep is used because it is the
           note's definition and is measured on the trace)
    theta_dot  the oncoming's looming rate W v / (D^2 + W^2/4) [rad/s]   x = log theta_dot

Fitter, folds, metric: the registered R.2 fitter (`cutin2_two_axis.fit_reg`: three-parameter
lapse + probit threshold, weighted least squares on cell means, multi-start L-BFGS-B),
leave-one-PET-level-out folds (9 folds; each holds out both speeds at one PET), held-out
weighted RMSE pooled over folds, chance (training mean) and the binomial sampling-noise
floor as in R.2 and EL.1.

Models:
    (a) 1D -log D                          [distance]
    (b) 1D -log t_sep                      [time]
    (c) linear 2D rule w(-log D) + (1-w)(-log t_sep), w in [0,1] fitted per fold
    (d) quadratic form in the same two axes, q0 the mildest cell (largest D, largest t_sep)
    (e) 1D log theta_dot                   [the cut-in's axis, on the oncoming vehicle]
Note on (e): at matched design PET the time-to-arrival is matched and D differs by the
speed ratio, so theta_dot = W / (TTA * D) is SMALLER for the faster oncoming; looming
therefore predicts less intervention at 70 km/h at matched PET, the observed direction
(`out/ltap_geometry.md` section "Time or distance?"). The note's section 1 expected looming
not to be the LTAP cue; that expectation was wrong in sign and is superseded by this test.

DECISION RULE (pre-stated), margin 0.01 as in EL.1:
    * a second axis earns its place if (c) or (d) beats (a) by more than 0.01;
    * the quadratic form is preferred over the linear rule only if it wins by more than 0.01;
    * (e) is reported against (a): better by more than 0.01, worse by more than 0.01, or
      within 0.01 (indistinguishable);
    * with 18 cells, a cell bootstrap (200 resamples with replacement, refit inside) gives a
      95% interval on (a) minus (c) and on (a) minus (e); a verdict whose interval includes
      zero is reported as "not resolved on 18 cells".

Resource note, 2026-09-02 evening: the 200-resample bootstrap did not complete in 2.7 CPU-hours
(the joint linear-rule fit with seven starts per fold is the cost); the run was stopped and the
bootstrap reduced to 50 resamples, with the main comparison written to the report BEFORE the
bootstrap so that the pre-stated decision does not wait on it. Models, folds, fitter and rule
are unchanged; the bootstrap's interval is correspondingly coarser and says so.

Run: python replication/czb/ltap_two_axis.py    Output: out/ltap_two_axis.md, out/ltap_cells.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))
import cutin2_two_axis as T                    # noqa: E402
import cutin2_field_vs_gap as R                # noqa: E402
from comfortzone.ltap import ltap_cells       # noqa: E402

OUT = HERE / "out"
N_BOOT = 50


def axes(c):
    return (-np.log(c.d_onc.to_numpy(float)), -np.log(c.t_sep.to_numpy(float)),
            np.log(c.theta_dot.to_numpy(float)))


def held_out(c, folds, model):
    y, w = c.p.to_numpy(float), c.n.to_numpy(float)
    pred = np.full_like(y, np.nan)
    params = []
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        ctr, cte = c[tr].reset_index(drop=True), c[te].reset_index(drop=True)
        u, v, l = axes(ctr)
        u2, v2, l2 = axes(cte)
        if model in ("dist", "time", "loom"):
            xtr, xte = {"dist": (u, u2), "time": (v, v2), "loom": (l, l2)}[model]
            th = T.fit_reg(xtr, y[tr], w[tr])
            pred[te] = R.predict(th, xte, +1.0)
            params.append(th)
        elif model == "linear":
            p, _ = T.fit_linear(u, v, y[tr], w[tr])
            wt = 1.0 / (1.0 + np.exp(-p[0]))
            pred[te] = R.predict(p[1:], wt * u2 + (1 - wt) * v2, +1.0)
            params.append(np.concatenate([[wt], p[1:]]))
        elif model == "quad":
            q0 = (u.min(), v.min())
            p, _ = T.fit_quad(u, v, y[tr], w[tr], q0)
            l21, l22 = p[0], np.exp(p[1])
            qu, qv = u2 - q0[0], v2 - q0[1]
            pred[te] = R.predict(p[2:], np.sqrt(qu * qu + (l21 * qu + l22 * qv) ** 2 + 1e-12), +1.0)
            params.append(np.concatenate([[l21, l22], p[2:]]))
    return pred, params


def score(c, model):
    folds = c.pet.to_numpy(float)
    pred, params = held_out(c, folds, model)
    return T.wrmse(c.p.to_numpy(float), pred, c.n.to_numpy(float)), pred, params


def main() -> None:
    c = ltap_cells().sort_values(["speed_kph", "pet"]).reset_index(drop=True)
    c.to_csv(OUT / "ltap_cells.csv", index=False)
    y, w = c.p.to_numpy(float), c.n.to_numpy(float)
    folds = c.pet.to_numpy(float)
    noise = float(np.sqrt(np.average(y * (1 - y) / np.maximum(w, 1), weights=w)))
    _, chance = R.held_out(c.assign(distance=c.d_onc), folds, "gap", False)

    L = ["# Card B.3.v2 -- the left turn across path: one axis or two, and which", "",
         "Generated by `replication/czb/ltap_two_axis.py`; models, folds and decision rule pre-stated"
         " in its docstring. 18 Random-design cells, the registered R.2 fitter, leave-one-PET-level-out"
         " folds. Do not edit by hand.", "",
         "## The cells (decision moment t = 13.5 s; query B3.Q1 resolved by assumption)", "",
         "| PET | speed | D [m] | TTA [s] | t_sep [s] | theta_dot [rad/s] | P(intervene) | n |", "|---|---|---|---|---|---|---|---|"]
    for _, r in c.iterrows():
        L.append(f"| {r.pet:.1f} | {r.speed_kph:.0f} | {r.d_onc:.1f} | {r.tta:.2f} | {r.t_sep:.2f} | "
                 f"{r.theta_dot:.4f} | {r.p:.3f} | {int(r.n)} |")
    L += ["", "## Held-out comparison", "",
          "| model | free parameters | held-out wRMSE | Spearman(pred, P) |", "|---|---|---|---|"]
    names = {"dist": "(a) 1D -log D  [distance]", "time": "(b) 1D -log t_sep  [time]",
             "linear": "(c) linear 2D rule in -log D and -log t_sep", "quad": "(d) quadratic form in the same axes",
             "loom": "(e) 1D log theta_dot  [the oncoming's looming rate]"}
    nfree = {"dist": 3, "time": 3, "linear": 4, "quad": 5, "loom": 3}
    S, preds, params = {}, {}, {}
    for m in names:
        S[m], preds[m], params[m] = score(c, m)
        L.append(f"| {names[m]} | {nfree[m]} | {S[m]:.4f} | {float(spearmanr(preds[m], y).statistic):+.3f} |")
    L += [f"| chance (train mean) | - | {T.wrmse(y, chance, w):.4f} | - |",
          f"| sampling-noise floor | - | {noise:.4f} | - |", ""]

    d_lin, d_quad, d_qc, d_loom = S["dist"] - S["linear"], S["dist"] - S["quad"], S["linear"] - S["quad"], S["dist"] - S["loom"]
    if max(d_lin, d_quad) > 0.01:
        v1 = "a second axis EARNS its place on the left turn"
        v2 = ("the quadratic form is preferred (curved trade-off)" if d_qc > 0.01 else
              "the linear rule beats the quadratic form" if d_qc < -0.01 else
              "linear and quadratic within 0.01: parsimony keeps the linear rule")
    else:
        v1 = "neither 2D model beats distance alone by 0.01: one axis suffices on this data"
        v2 = "-"
    v3 = ("looming BEATS distance" if d_loom > 0.01 else "looming is WORSE than distance" if d_loom < -0.01
          else "looming and distance are indistinguishable (within 0.01)")
    L += [f"**Pre-stated decision.** distance minus linear = {d_lin:+.4f}; distance minus quadratic = "
          f"{d_quad:+.4f}; linear minus quadratic = {d_qc:+.4f}; distance minus looming = {d_loom:+.4f}. "
          f"**{v1}**; {v2}; **{v3}**.", ""]

    L += ["## Fitted inner parameters per held-out PET level", "",
          "| held-out PET | linear w on -log D | quad l21 | quad l22 |", "|---|---|---|---|"]
    for f, pl, pq in zip(sorted(np.unique(folds)), params["linear"], params["quad"]):
        L.append(f"| {f:.1f} | {pl[0]:.3f} | {pq[0]:+.3f} | {pq[1]:.3f} |")
    L += ["", "w = 1 is a pure distance threshold, w = 0 pure arrival-time separation.", ""]

    (OUT / "ltap_two_axis.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L)); print("main comparison written; bootstrap follows", flush=True)

    # cell bootstrap
    rng = np.random.default_rng(0)
    diffs_lin, diffs_loom = [], []
    for _ in range(N_BOOT):
        idx = rng.integers(0, len(c), len(c))
        cb = c.iloc[idx].reset_index(drop=True)
        if cb.pet.nunique() < 4:
            continue
        sa, _, _ = score(cb, "dist")
        sc_, _, _ = score(cb, "linear")
        se, _, _ = score(cb, "loom")
        diffs_lin.append(sa - sc_)
        diffs_loom.append(sa - se)
    dl, dlo = np.array(diffs_lin), np.array(diffs_loom)
    L += [f"## Cell bootstrap ({N_BOOT} resamples of the 18 cells, refit inside)", "",
          f"distance minus linear: mean {dl.mean():+.4f}, 95% {np.percentile(dl, 2.5):+.4f} to {np.percentile(dl, 97.5):+.4f}"
          f" ({(dl > 0).mean() * 100:.0f}% of resamples favour the linear rule)",
          "",
          f"distance minus looming: mean {dlo.mean():+.4f}, 95% {np.percentile(dlo, 2.5):+.4f} to {np.percentile(dlo, 97.5):+.4f}"
          f" ({(dlo > 0).mean() * 100:.0f}% of resamples favour looming)", "",
          "A verdict whose interval includes zero is not resolved on 18 cells. (50 resamples: the interval is coarse, see the docstring.)", ""]
    (OUT / "ltap_two_axis.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
