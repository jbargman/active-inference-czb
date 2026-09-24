"""
Card JJ.9 -- the gate's lateral uncertainty measured on highD: is the derived gate a PREDICTION?

THE PRE-REGISTRATION. Written before the run, on 2026-09-24, before any highD file was opened
beyond its header lines.

WHY. Card JJ.6e showed that card G.1's fitted gate is exactly a Gaussian-rate predictor's
P(the other's body reaches mine within T), Phi((m - l0 - ldot T) / (sigma T)), with m = 0 scoring
0.1028 / 0.0462 on the second cut-in study. It was circular: sigma = 0.33 m/s was set from G.1's
fitted spread. Jonas's decision 4 (2026-09-22): measure it on naturalistic data when it comes. It
came on 2026-09-24 (`C:\\JonasLocal\\D_Data\\highD-dataset-v1.0`, 60 recordings, 25 Hz).

WHAT IS MEASURED. The quantity the gate needs, unconditioned on the future (the review's lesson
from card GM.1a): for every vehicle i at every whole second of its track, and for each vehicle j
that highD lists as i's leftFollowing or rightFollowing at that frame (j is BEHIND i in an
ADJACENT lane: the cut-in geometry, i playing the cut-in vehicle and j the ego), the error of the
constant-rate lateral projection of i over T = 3 s, signed TOWARD j's lane:
    vy   = (yc_i(t) - yc_i(t - 0.32 s)) / 0.32 s          8 frames; the video cards' 0.3 s window
    e    = s * ( yc_i(t + 3 s) - yc_i(t) - vy * 3 s ),    s = sign(yc_j(t) - yc_i(t))
with yc the bounding-box centre (highD's y is the box's upper-left corner; y + height/2). e > 0
means i moved toward j's lane more than its current rate predicted. Also recorded: the edge-to-edge
lateral clearance l0 = |yc_j - yc_i| - (h_i + h_j)/2, s*vy, and whether i's lane at t + 3 s differs
from its lane at t. Samples need both t - 0.32 s and t + 3 s inside i's track. Per-sample values
are cached OUTSIDE the repository (`C:\\JonasLocal\\D_Data_derived\\jj9_samples.npz`; the highD
licence); the repository gets aggregates only.

THE GATES, on the second cut-in study's 378 cells (lateral states from `cutin2_gate.lateral_states`,
edge-to-edge clearance l0 and its rate ldot at the response moment; axis card EL.1b's looming rate;
response model the fixed-gate fitter of card JJ.6, only lapse, level and spread fitted):
  (E)  **the empirical gate, primary**: P_highD(e > l0 + ldot T) with T = 3 s, m = 0, the empirical
       survival function of e over all samples. NOTHING in it comes from the video data.
  (G)  the Gaussian gate with the measured sigma = sd(e) / T.
  (R)  the Gaussian gate with the robust sigma = 1.4826 MAD(e) / T (the lane-keeping core).
  Beside them: G.1's gate and JJ.6e's (m = 0, sigma 0.33) for reference.

THE RULES. Card JJ.6's, on (E): (a) post-onset held out within 0.01 of the gated looming rule's
0.1027; (b) pre-onset below 0.05. Verdict **PREDICTED** if both hold (the gate is a prediction of a
generative model estimated on naturalistic driving, and the circularity is gone); **LEVEL ONLY** if
(b) holds and (a) fails; **NOT PREDICTED** otherwise, with the failing rule named. Rule 0: at least
100 000 samples, and the frame rate is 25 Hz in every recording.

PREDICTIONS. sd(e) about 0.4 to 0.6 m (sigma 0.13 to 0.2 m/s, below JJ.6e's 0.33), with a narrow
core (robust sigma 0.03 to 0.08 m/s) and a heavy tail from lane changes; P(e > 1.6 m), the
pre-onset gate, about 0.01 to 0.03, well below G.1's 0.067: real traffic changes lanes less often
than the participants of a cut-in study, who know a cut-in is coming, anticipate. So (b) holds (a
smaller gate predicts the pre-onset cells' 0.023 at least as well) and (a) is uncertain; my
central guess 0.105 to 0.12, i.e. LEVEL ONLY or a narrow PREDICTED. The robust Gaussian (R) will
fail (a): with the core alone the gate opens too late.

Output: replication/czb/out/jj9_highd_lateral.md, out/jj9_highd_lateral_tail.csv (aggregate)
Run:    python replication/czb/jj9_highd_lateral.py
"""
from __future__ import annotations

import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

HIGHD = Path(r"C:\JonasLocal\D_Data\highD-dataset-v1.0\data")
CACHE = Path(r"C:\JonasLocal\D_Data_derived\jj9_samples.npz")
OUT = HERE / "out"
FPS = 25
BACK, AHEAD, STEP = 8, 75, 25            # 0.32 s window, 3 s horizon, one sample a second
T = AHEAD / FPS
G1_GATED, MARGIN_A, CP1_CRIT = 0.1027, 0.01, 0.05


def extract(rec: int) -> dict:
    meta = pd.read_csv(HIGHD / f"{rec:02d}_recordingMeta.csv")
    tr = pd.read_csv(HIGHD / f"{rec:02d}_tracks.csv",
                     usecols=["frame", "id", "y", "height", "laneId", "leftFollowingId",
                              "rightFollowingId"])
    tr["yc"] = tr.y + tr.height / 2.0
    key = tr.set_index(["id", "frame"])
    yc, lane, h = key.yc, key.laneId, key.height
    s = tr[tr.frame % STEP == 0]
    out = []
    for col in ("leftFollowingId", "rightFollowingId"):
        q = s[s[col] > 0]
        idx_now = pd.MultiIndex.from_arrays([q.id, q.frame])
        idx_back = pd.MultiIndex.from_arrays([q.id, q.frame - BACK])
        idx_ahead = pd.MultiIndex.from_arrays([q.id, q.frame + AHEAD])
        idx_ego = pd.MultiIndex.from_arrays([q[col], q.frame])
        y0 = yc.reindex(idx_now).to_numpy()
        yb = yc.reindex(idx_back).to_numpy()
        ya = yc.reindex(idx_ahead).to_numpy()
        ye = yc.reindex(idx_ego).to_numpy()
        he = h.reindex(idx_ego).to_numpy()
        la = lane.reindex(idx_ahead).to_numpy()
        ok = np.isfinite(y0) & np.isfinite(yb) & np.isfinite(ya) & np.isfinite(ye)
        sgn = np.sign(ye - y0)
        vy = (y0 - yb) / (BACK / FPS)
        e = sgn * ((ya - y0) - vy * T)
        l0 = np.abs(ye - y0) - (q.height.to_numpy() + he) / 2.0
        lc = la != q.laneId.to_numpy()
        ok &= sgn != 0
        out.append(np.column_stack([e[ok], (sgn * vy)[ok], l0[ok], lc[ok].astype(float)]))
    return {"rec": rec, "fps": int(meta.frameRate.iloc[0]), "data": np.vstack(out)}


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    recs = sorted(int(p.name[:2]) for p in HIGHD.glob("*_tracks.csv"))
    if CACHE.exists():
        z = np.load(CACHE)
        X, fps_ok, n_rec = z["X"], bool(z["fps_ok"]), int(z["n_rec"])
    else:
        with ProcessPoolExecutor(max_workers=12) as ex:
            res = list(ex.map(extract, recs))
        X = np.vstack([r["data"] for r in res])
        fps_ok = all(r["fps"] == FPS for r in res)
        n_rec = len(res)
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(CACHE, X=X, fps_ok=fps_ok, n_rec=n_rec)
    print(f"{len(X)} samples from {n_rec} recordings [{time.time() - t0:.0f} s]", flush=True)
    e, vy_t, l0_hd, lc = X[:, 0], X[:, 1], X[:, 2], X[:, 3].astype(bool)
    rule0 = len(X) >= 100_000 and fps_ok

    sd = float(np.std(e))
    mad_sd = float(1.4826 * np.median(np.abs(e - np.median(e))))
    sig_g, sig_r = sd / T, mad_sd / T
    e_sorted = np.sort(e)

    def surv(x):
        """P_highD(e > x), the empirical survival function."""
        return 1.0 - np.searchsorted(e_sorted, np.asarray(x, float), side="right") / len(e_sorted)

    grid = np.array([0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.25, 1.5, 1.6, 1.75, 2.0, 2.5, 3.0])
    tail = pd.DataFrame({"x_m": grid, "P_e_gt_x": surv(grid),
                         "gaussian_sd": 1 - norm.cdf(grid / sd),
                         "gaussian_robust": 1 - norm.cdf(grid / mad_sd)})
    tail["n"] = len(e)
    tail.to_csv(OUT / "jj9_highd_lateral_tail.csv", index=False)

    import cutin2_gate as CG
    import jj6_belief_gate as J6
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    x = J6.looming_axis(cells)
    lat = CG.lateral_states(cells.video)
    l0, ldot = lat.l0.to_numpy(float), lat.ldot.to_numpy(float)
    gates = {"E": surv(l0 + ldot * T),
             "G": norm.cdf((-l0 - ldot * T) / (sig_g * T)),
             "R": norm.cdf((-l0 - ldot * T) / (sig_r * T)),
             "G.1": np.asarray(CG.gate(0.149, np.log(0.990), l0, ldot), float),
             "JJ.6e": norm.cdf((-l0 - ldot * T) / (0.33 * T))}
    d = cells[["video", "cp", "p", "n", "ttc_start", "ttc_true", "distance", "lcd"]].copy()
    for k, g in gates.items():
        d[f"gate_{k}"] = g
    res = {k: J6.score_gated(d, x, g) for k, g in gates.items()}
    is_cp1 = (d.cp == "CP1").to_numpy()
    E = res["E"]
    a, b = E["post"] <= G1_GATED + MARGIN_A, E["cp1"] < CP1_CRIT
    verdict = "PREDICTED" if a and b else ("LEVEL ONLY" if b else "NOT PREDICTED")

    # the conditional check: does the error depend on the observed rate toward the ego?
    bins = [-np.inf, -0.2, -0.05, 0.05, 0.2, 0.5, np.inf]
    cond = pd.DataFrame({"e": e, "vy": vy_t}).assign(bin=pd.cut(vy_t, bins))
    cond = cond.groupby("bin", observed=True).e.agg(
        n="size", sd="std", p_gt_1=lambda v: float(np.mean(v > 1.0)))

    L = ["# Card JJ.9 -- the gate's lateral uncertainty measured on highD", "",
         "Generated by `replication/czb/jj9_highd_lateral.py`; the measurement, the gates, the rules"
         " and the predictions were pre-stated in its docstring before the run. Aggregates only;"
         " per-sample values stay outside the repository (highD licence). Do not edit by hand.", "",
         "## 0 The measurement", "",
         f"{len(X):,} samples from {n_rec} highD recordings (rule 0: at least 100 000 and 25 Hz"
         f" throughout: **{'PASS' if rule0 else 'FAIL'}**): every vehicle, every whole second, with"
         " a vehicle behind it in an adjacent lane; e is the error of its constant-rate lateral"
         " projection over 3 s, toward that follower's lane, unconditioned on whether it then"
         f" changes lanes. {lc.mean():.3%} of samples change lane within the 3 s. Median edge-to-edge"
         f" clearance to the follower {np.median(l0_hd):.2f} m (the video's pre-onset cells: about"
         " 1.6 m).", "",
         "| statistic | value |", "|---|---|",
         f"| sd(e) over 3 s | {sd:.3f} m, i.e. sigma = {sig_g:.3f} m/s (JJ.6e assumed 0.33) |",
         f"| robust sd (1.4826 MAD) | {mad_sd:.3f} m, i.e. {sig_r:.3f} m/s |",
         f"| P(e > 1.6 m), the pre-onset gate at the video's clearance | {surv(1.6):.4f} (G.1's gate"
         f" there: 0.063 to 0.070) |", "",
         "The tail, empirical against the two Gaussians (`out/jj9_highd_lateral_tail.csv`):", "",
         "| x [m] | P_highD(e > x) | Gaussian, sd | Gaussian, robust |", "|---|---|---|---|"]
    for _, r in tail.iterrows():
        L.append(f"| {r.x_m:g} | {r.P_e_gt_x:.4f} | {r.gaussian_sd:.4f} | {r.gaussian_robust:.2e} |")
    L += ["", "Conditional on the observed rate toward the follower (a check on the Gaussian-rate"
          " predictor's assumption that the error does not depend on it):", "",
          "| rate toward the follower [m/s] | samples | sd(e) [m] | P(e > 1 m) |", "|---|---|---|---|"]
    for b_, r in cond.iterrows():
        L.append(f"| {b_} | {int(r.n):,} | {r.sd:.3f} | {r.p_gt_1:.4f} |")
    L += ["", "## 1 The gates on the second cut-in study", "",
          "| gate | pre-onset mean | post-onset mean | post-onset held out | pre-onset, out of"
          " sample | median level [rad/s] |", "|---|---|---|---|---|---|"]
    labels = {"E": "**(E) empirical highD gate, nothing from the video (primary)**",
              "G": f"(G) Gaussian, measured sigma {sig_g:.3f} m/s",
              "R": f"(R) Gaussian, robust sigma {sig_r:.3f} m/s",
              "G.1": "card G.1's fitted gate (reference)",
              "JJ.6e": "JJ.6e's gate, sigma 0.33 from G.1 (reference)"}
    for k in ("E", "G", "R", "G.1", "JJ.6e"):
        g = gates[k]
        L.append(f"| {labels[k]} | {g[is_cp1].mean():.3f} | {g[~is_cp1].mean():.3f} |"
                 f" {res[k]['post']:.4f} | {res[k]['cp1']:.4f} | {res[k]['level']:.4f} |")
    L += ["", "## 2 The verdict on the pre-stated rules", "",
          f"**{verdict}.** Rule (a) {E['post']:.4f} against {G1_GATED + MARGIN_A:.4f}"
          f" ({'holds' if a else 'fails'}); rule (b) {E['cp1']:.4f} against {CP1_CRIT}"
          f" ({'holds' if b else 'fails'}).", "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj9_highd_lateral.md").write_text("\n".join(L), encoding="utf-8")
    d.drop(columns=["video"]).to_csv(OUT / "jj9_highd_lateral_cells.csv", index=False)
    print("\n".join(L))


if __name__ == "__main__":
    main()
