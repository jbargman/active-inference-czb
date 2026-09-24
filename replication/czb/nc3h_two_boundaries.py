"""
Card NC.3h -- two boundaries (gentle and hard), and the deceleration at which real highD
followers' responses match each.

THE PRE-REGISTRATION. Written 2026-09-24, before any quantity below was computed.

WHERE THE CARD COMES FROM. Jonas, 2026-09-24, on query NC3G.Q1: *"OK, go for two boundaries
then"*; and, of the transfer at 0.5-1.0 m/s^2: *"Can you estimate the deceleration that would
make them match?"*; and, of the colleague's 2.5 m/s^2 (Malin Svärd, ITSC; Jonas now thinks it
was an average over speeds, lower at higher speeds): *"what speeds should I ask for?"*

PART 1, THE HARD BOUNDARY (the first study's button design). Every participant who pressed during
a cut-in answered "brake gently or hard?" (card NC.3g: 41% hard, graded by the clip). From
`jj4_precision_spread.press_levels` (car clips, the TTC 4-8 s labels; the looming at the press,
log theta_dot, card EL.1b's axis), fit P(hard | press at looming x) = Phi((x - c_h) / s_h) by
maximum likelihood, pooled over participants, with a participant bootstrap (200). The hard
boundary's median looming is exp(c_h). The two boundaries on the looming axis are then:
  gentle (the intervention itself)  P_int(x) = Phi((x - log 0.0320) / 1.293)   (card JJ.10, study 2)
  hard                              P_hard(x) = P_int(x) * Phi((x - c_h) / s_h)
The lapse of JJ.10's fit (0.037) is left out of both in part 2: it was fitted on cells whose
looming never falls below 0.0036 rad/s and is not identified at highD's looming, most of which is
far lower; the with-lapse numbers are reported beside it.

PART 2, THE MATCHING DECELERATION. highD closing cut-ins exactly as card NC.3 defines them,
re-extracted with, per event, the deepest deceleration sustained for 8 frames (0.32 s, NC.0b's
T_min 0.3 rounded to frames) with its onset within 3 s of the lane switch (a_resp), and the
deceleration at the switch (a_now). At a threshold a, an event is censored if a_now > a (already
braking that hard) and responds if a_resp >= a. The MATCHING DECELERATION for a boundary is the a
at which the observed number of responses equals the number the boundary's curve expects
(calibration in the large), found on a grid 0.20 to 4.00 m/s^2 in steps of 0.05 with linear
interpolation, with a 95% interval from a bootstrap over recordings (200). The a that minimises
the binned weighted RMSE (deciles of looming) is reported beside it. Primary set: all closing
cut-ins; secondary: inside the video's looming range (>= 0.0036 rad/s).

PART 3, WHICH SPEED TO ASK ABOUT. The follower speed at the lane switch in highD's closing cut-ins
(median, quartiles), the video study's ego speeds (26.6 to 36.5 m/s, median 31.6), and highD's own
99th and 99.9th percentiles of longitudinal deceleration over car frames by speed band (70-90,
90-110, 110-130, >130 km/h), from per-recording histograms.

NO VERDICT RULE: the card estimates. The predictions are written so they can be checked.

PREDICTIONS. Hard boundary: median looming 0.05 to 0.1 rad/s (above the intervention level
0.032), i.e. the hard boundary sits about one spread above the gentle one. Matching deceleration
for the intervention (gentle) boundary: 0.9 to 1.2 m/s^2 (NC.3: the observed rate crosses the
expected 128 of 2,771 between the 1.0 and 1.5 grid points), interval about +-0.15. For the hard
boundary: 1.5 to 2.2 m/s^2 -- above the gentle one, below 2.5. Speeds: highD's cut-in followers
median about 27 m/s (97 km/h); highD's 99th percentile lower at higher speed.

Output: replication/czb/out/nc3h_two_boundaries.md (aggregates only)
Run:    python replication/czb/nc3h_two_boundaries.py
"""
from __future__ import annotations

import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nc3_highd_cutins as N  # noqa: E402

OUT = HERE / "out"
CACHE = Path(r"C:\JonasLocal\D_Data_derived\nc3h_events.pkl")
FPS, WIN, PRE, RUN = 25, 75, 25, 8
INT_LEVEL, INT_SPREAD, INT_LAPSE = 0.0320, 1.293, 0.037
GRID = np.round(np.arange(0.20, 4.0001, 0.05), 2)
SPEED_BANDS_KMH = [70, 90, 110, 130, 200]
HIST_EDGES = np.arange(-15.0, 15.0001, 0.05)


def extract(rec: int):
    tr = pd.read_csv(N.HIGHD / f"{rec:02d}_tracks.csv",
                     usecols=["frame", "id", "x", "width", "height", "xVelocity", "xAcceleration",
                              "precedingId", "laneId"])
    meta = pd.read_csv(N.HIGHD / f"{rec:02d}_tracksMeta.csv", usecols=["id", "drivingDirection", "class"])
    tr = tr.merge(meta, on="id").sort_values(["id", "frame"]).reset_index(drop=True)
    tr["v"] = tr.xVelocity.abs()
    tr["a"] = tr.xAcceleration * np.where(tr.drivingDirection == 1, -1.0, 1.0)
    cars = tr[tr["class"] == "Car"]
    hists = {}
    kmh = cars.v * 3.6
    for lo, hi in zip(SPEED_BANDS_KMH[:-1], SPEED_BANDS_KMH[1:]):
        m = (kmh >= lo) & (kmh < hi)
        hists[(lo, hi)] = np.histogram(cars.a[m], HIST_EDGES)[0]
    arr = {k: {c: g[c].to_numpy() for c in ("frame", "x", "width", "height", "v", "a", "precedingId",
                                             "laneId", "drivingDirection")}
           for k, g in tr.groupby("id")}
    rows = []
    for j, g in arr.items():
        fr, p, lane, a = g["frame"], g["precedingId"], g["laneId"], g["a"]
        n = len(fr)
        for q in range(PRE, n - WIN - RUN):
            i = p[q]
            if i <= 0 or i == p[q - 1] or i not in arr or lane[q - PRE] != lane[q]:
                continue
            I = arr[i]
            m = np.searchsorted(I["frame"], fr[q])
            if m >= len(I["frame"]) or I["frame"][m] != fr[q] or m < PRE:
                continue
            if I["laneId"][m] != lane[q] or I["laneId"][m - PRE] == lane[q]:
                continue
            if g["drivingDirection"][q] == 2:
                gap = I["x"][m] - (g["x"][q] + g["width"][q])
            else:
                gap = g["x"][q] - (I["x"][m] + I["width"][m])
            if gap <= 0:
                continue
            seg = -a[q:q + WIN + RUN]
            sustained = np.array([seg[s:s + RUN].min() for s in range(WIN)])
            rows.append({"rec": rec, "gap": gap, "dv": g["v"][q] - I["v"][m], "W": I["height"][m],
                         "v": g["v"][q], "lc": bool(np.any(lane[q:q + WIN] != lane[q])),
                         "a_now": float(-a[q]), "a_resp": float(sustained.max())})
    return rows, hists


def hard_boundary():
    import jj4_precision_spread as J4
    b, _ = J4.press_levels()
    b = b[(b.scenario == "cutin_car") & b.followup_code.isin([1, 2])].copy()
    x = b.level.to_numpy(float)
    y = (b.followup_code == 2).to_numpy(float)
    drv = b.driver.to_numpy()

    def fit(xx, yy):
        def nll(th):
            pp = np.clip(norm.cdf((xx - th[0]) / np.exp(th[1])), 1e-9, 1 - 1e-9)
            return -float(np.sum(yy * np.log(pp) + (1 - yy) * np.log(1 - pp)))
        return minimize(nll, np.array([np.median(xx), 0.0]), method="L-BFGS-B").x

    th = fit(x, y)
    rng = np.random.default_rng(20260924)
    ud = np.unique(drv)
    boots = []
    for _ in range(200):
        idx = np.concatenate([np.flatnonzero(drv == d) for d in rng.choice(ud, len(ud))])
        boots.append(fit(x[idx], y[idx]))
    boots = np.array(boots)
    return {"c": th[0], "s": float(np.exp(th[1])), "n": len(b), "drivers": len(ud),
            "share": float(y.mean()), "c_ci": np.percentile(boots[:, 0], [2.5, 97.5]),
            "s_ci": np.exp(np.percentile(boots[:, 1], [2.5, 97.5]))}


def expected_curves(x, hb, lapse):
    p_int = lapse + (1 - lapse) * norm.cdf((x - np.log(INT_LEVEL)) / INT_SPREAD)
    p_hard = p_int * norm.cdf((x - hb["c"]) / hb["s"])
    return p_int, p_hard


def matching(ev, pred_col, lapse, hb):
    """The a at which observed responses equal the expected count; and the wRMSE minimiser."""
    x = np.log((ev.W * ev.dv / (ev.gap ** 2 + ev.W ** 2 / 4)).to_numpy(float))
    p_int, p_hard = expected_curves(x, hb, lapse)
    pred = p_int if pred_col == "int" else p_hard
    diff, wr = [], []
    bins = pd.qcut(x, 10, labels=False, duplicates="drop")
    for a in GRID:
        keep = ev.a_now.to_numpy() <= a
        y = ev.a_resp.to_numpy()[keep] >= a
        diff.append(y.sum() - pred[keep].sum())
        wr.append(N.binned_wrmse(pred[keep], y, bins[keep])[0])
    diff = np.array(diff)
    k = np.flatnonzero(np.diff(np.sign(diff)) != 0)
    if len(k) == 0:
        a_match = np.nan
    else:
        k = k[0]
        a_match = float(GRID[k] + (GRID[k + 1] - GRID[k]) * diff[k] / (diff[k] - diff[k + 1]))
    return a_match, float(GRID[int(np.argmin(wr))])


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    if CACHE.exists():
        ev, hists = pd.read_pickle(CACHE)
    else:
        recs = sorted(int(p.name[:2]) for p in N.HIGHD.glob("*_tracks.csv"))
        with ProcessPoolExecutor(max_workers=12) as ex:
            res = list(ex.map(extract, recs))
        ev = pd.DataFrame([r for rr in res for r in rr[0]])
        hists = {k: np.sum([rr[1][k] for rr in res], axis=0) for k in res[0][1]}
        pd.to_pickle((ev, hists), CACHE)
    c = ev[~ev.lc & (ev.dv > 0)].reset_index(drop=True)
    print(f"{len(c)} closing cut-ins [{time.time() - t0:.0f} s]", flush=True)
    hb = hard_boundary()
    print("hard boundary fitted", flush=True)
    loom = c.W * c.dv / (c.gap ** 2 + c.W ** 2 / 4)
    sets = {"all closing cut-ins": c, "inside the video's looming range": c[loom >= 0.0036].reset_index(drop=True)}
    rows = {}
    for sname, s in sets.items():
        for curve in ("int", "hard"):
            for lapse, ltag in ((0.0, "no lapse (primary)"), (INT_LAPSE, "with lapse")):
                a_m, a_w = matching(s, curve, lapse, hb)
                ci = [np.nan, np.nan]
                if sname == "all closing cut-ins" and lapse == 0.0:
                    rng = np.random.default_rng(20260924)
                    ur = s.rec.unique()
                    bs = []
                    for _ in range(200):
                        idx = np.concatenate([np.flatnonzero(s.rec.to_numpy() == r) for r in rng.choice(ur, len(ur))])
                        bs.append(matching(s.iloc[idx].reset_index(drop=True), curve, lapse, hb)[0])
                    ci = np.nanpercentile(bs, [2.5, 97.5])
                rows[(sname, curve, ltag)] = (a_m, ci, a_w)
        print(f"{sname} done [{time.time() - t0:.0f} s]", flush=True)

    centres = 0.5 * (HIST_EDGES[:-1] + HIST_EDGES[1:])
    L = ["# Card NC.3h -- two boundaries, and the deceleration at which real followers match each", "",
         "Generated by `replication/czb/nc3h_two_boundaries.py`; pre-stated in its docstring before"
         " the run. Aggregates only. Do not edit by hand.", "",
         "## 1 The hard boundary (the first study's button design, car clips)", "",
         f"{hb['n']:,} presses by {hb['drivers']} participants, {hb['share']:.1%} answered \"hard\"."
         f" P(hard | press at looming x) = Phi((x - c_h) / s_h): median looming of the hard boundary"
         f" **{np.exp(hb['c']):.4f} rad/s** [{np.exp(hb['c_ci'][0]):.4f}, {np.exp(hb['c_ci'][1]):.4f}],"
         f" spread {hb['s']:.2f} [{hb['s_ci'][0]:.2f}, {hb['s_ci'][1]:.2f}] log units (participant"
         f" bootstrap). The intervention (gentle) boundary: {INT_LEVEL} rad/s, spread {INT_SPREAD}"
         f" (card JJ.10). **The hard boundary sits {np.exp(hb['c']) / INT_LEVEL:.1f} times higher in"
         " looming.**", "",
         "## 2 The deceleration at which real highD followers match each boundary", "",
         "| set | boundary | lapse | matching deceleration [m/s^2] (count) | 95% over recordings |"
         " wRMSE-minimising [m/s^2] |", "|---|---|---|---|---|---|"]
    for (sname, curve, ltag), (a_m, ci, a_w) in rows.items():
        lab = "intervention (gentle)" if curve == "int" else "hard"
        ci_s = f"[{ci[0]:.2f}, {ci[1]:.2f}]" if np.isfinite(ci[0]) else "-"
        L.append(f"| {sname} | {lab} | {ltag} | **{a_m:.2f}** | {ci_s} | {a_w:.2f} |")
    kmh = c.v * 3.6
    L += ["", "## 3 Which speed to ask about", "",
          f"highD's closing cut-ins: follower speed median **{kmh.median():.0f} km/h** (quartiles"
          f" {kmh.quantile(0.25):.0f} to {kmh.quantile(0.75):.0f}); inside the video's looming range"
          f" {(loom >= 0.0036).sum()} events, median {kmh[loom >= 0.0036].median():.0f} km/h. The video"
          " study's ego: 96 to 131 km/h, median 114 km/h (the lead at 90 km/h).", "",
          "highD's own deceleration percentiles, car frames, by speed band:", "",
          "| speed band [km/h] | car frames | 99th percentile [m/s^2] | 99.9th [m/s^2] |", "|---|---|---|---|"]
    for (lo, hi), h in hists.items():
        cdf = np.cumsum(h) / max(h.sum(), 1)
        p99 = -centres[np.searchsorted(cdf, 0.01)]
        p999 = -centres[np.searchsorted(cdf, 0.001)]
        L.append(f"| {lo}-{hi} | {int(h.sum()):,} | {p99:.2f} | {p999:.2f} |")
    L += ["", f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "nc3h_two_boundaries.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
