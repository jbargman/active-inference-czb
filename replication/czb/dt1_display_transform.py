"""
Card DT.1 -- the video studies' analyses with and without the display transform.

THE PRE-REGISTRATION. Written 2026-09-25 (night), before any analysis below was run with the
transform on.

WHERE THE CARD COMES FROM. Jonas, 2026-09-25: the crowd-sourced participants watched the clips on a
desktop monitor (about 60 cm away, a 23-inch screen) while the rendering camera had a 90 degree
horizontal field of view, so what they saw was not the optics of the virtual world. "Create a way
to transform the data ... so that we can transform the data from the studies into what the actual
perception was ... and run a comparison study where you compare the results with the transform
with the original." The transform is specified in `docs/display_transform.md` (parameters in its
YAML block) and implemented in `src/comfortzone/display.py` (18 property checks). Its geometry is
exact: the viewer's optical array is that of an equivalent world in which distances along the line
of sight are divided by k = 0.4243 (defaults); closing speeds too; lateral quantities unchanged;
TTC invariant; looming x ~k.

WHAT IS COMPUTED, each twice -- "off" (the rendered world, every result so far) and "on" (the
perceived world, convention (a) of the spec, default parameters). Nothing refitted beyond what each
original card fitted; the pre-registered scripts are imported, not modified.
  A  The transform on the stimuli. Study 2's 378 cells and study 1's cut-in traces (Random and
     Button designs): the perceived/rendered looming ratio (median, range) and the largest change
     in TTC.
  B  Within the second study (288 post-onset cells, registered folds, weights n):
     B1 the 1D thresholds of card EL.1b on log looming, -log gap and -log TTC: held-out wRMSE and
        the full-sample level;
     B2 card JJ.10's mixture (the gated intervention curve: lapse, level, spread; post-onset held
        out and pre-onset), the curve every later card calls "the video curve";
     B3 card NC.3o's ordered model (gentle and hard on one looming axis) against two separate
        boundaries: held-out scores, levels, verdict.
  C  Against real traffic (highD not transformed -- its optics are real):
     C1 card NC.3's rule (a): the video curve (B2's fit, off and on) on highD's closing cut-ins at
        NC.3's primary detector, binned wRMSE against chance, predicted and observed rates, and the
        highD refit's level as a ratio of the video level;
     C2 card NC.3h's matching deceleration for the gentle (intervention) curve, no lapse, all
        closing cut-ins, with its 95% interval over recordings;
     C3 card PT.1's comparison with Farewell's emergency-braking level (0.02 rad/s): the video
        curve's 50% looming level (gate open) as a multiple of it, and the curve's share at it;
     C4 convention (b) of the spec: the TTC at which a real driver closing at each of the second
        study's six closing speeds receives the curve's 50% looming, off and on.
  D  Statements checked numerically, not refitted: every TTC-based result (the hard boundary on
     TTC, cards NC.3i/NC.3j/NC.3l; the TTC comparators) is unchanged because TTC is invariant;
     per-driver rank results (card TR.1) and AUCs on highD (NC.3 rule (b), NC.4c) are unchanged
     because the transform is monotone and highD is not transformed.

THE LABELS, per qualitative conclusion: UNCHANGED (held-out scores within 0.005 and the same
verdict), SHIFTED (the verdict stands, a level moves), REVERSED (the verdict flips). The
conclusions checked: (1) NC.3 "the video curve transfers" (beats chance); (2) NC.3 "highD's level
within 21% of the video's" (ratio in [0.8, 1.25]); (3) PT.1 "the comfort boundary lies above
Farewell's emergency level"; (4) NC.3h "real followers match the gentle curve at about highD's
99th percentile of deceleration" (matching deceleration in [0.87, 1.22] m/s^2); (5) the second
study's axis ranking, looming < TTC < gap (held-out); (6) NC.3o SUPPORTED; (7) the TTC boundaries.

PREDICTIONS. A: ratio 0.424 to 0.46 (above k only at the shortest gaps); TTC change 0. B: every
held-out score within 0.002 of off; looming levels x ~0.43 (JJ.10's 0.0320 -> about 0.014),
gap levels x 2.36; spreads, lapse and the NC.3o verdict unchanged. C1: the transformed curve
over-predicts real responses (predicted rate about double), its binned wRMSE is worse than off and
does NOT beat chance -> (1) REVERSED; highD's level is about 2.8 times the video's -> (2) REVERSED.
C2: the matching deceleration falls to about 0.5 to 0.7 m/s^2 -> (4) SHIFTED out of the range,
i.e. REVERSED as stated. C3: the 50% level falls below Farewell's (ratio about 0.7) -> (3)
REVERSED: the comfort boundary is reached BEFORE (at lower looming than) the emergency level, the
order one would expect. C4: TTC_b about 1.54 x the rendered TTC at the same level. (5), (6), (7)
UNCHANGED.

Output: replication/czb/out/dt1_display_transform.md
Run:    python replication/czb/dt1_display_transform.py
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

from comfortzone import display as D                         # noqa: E402
from comfortzone import czb_data                              # noqa: E402
from comfortzone.cutin import cutin_predictors, load_cutin_trace  # noqa: E402
import cutin2_field_vs_gap as R                               # noqa: E402
import cutin2_looming as CL                                   # noqa: E402
import cutin2_two_axis as T                                   # noqa: E402
import jj10_gate_as_free_energy as J10                        # noqa: E402
import jj6_belief_gate as J6                                  # noqa: E402
import nc3_highd_cutins as N                                  # noqa: E402
import nc3h_two_boundaries as H                               # noqa: E402
import nc3o_two_levels_one_observation as O                   # noqa: E402
import pt1_farewell_thresholds as P1                          # noqa: E402
from rollout.comfort_fe import SIGMA_LAT, T_ANTICIPATION, p_lead  # noqa: E402

OUT = HERE / "out"
KPH = 1000.0 / 3600.0
MODES = ("off", "on")


def label(off_ok: bool, on_ok: bool, moved: bool) -> str:
    if off_ok != on_ok:
        return "REVERSED"
    return "SHIFTED" if moved else "UNCHANGED"


def study1_ratios(g):
    rows = []
    for design, d in (("Random", czb_data.KIN_RANDOM), ("Button", czb_data.KIN_BUTTON)):
        r_all, dt_all = [], []
        for f in sorted(d.glob("CutIn*_vehicle_states.csv")):
            if "Example" in f.name:
                continue
            try:
                tr = load_cutin_trace(f, is_truck="Truck" in f.name)
            except Exception:
                continue
            p = cutin_predictors(tr)
            gap, dv = p.gap_m.to_numpy(float), p.v_rel.to_numpy(float)
            m = (gap > 0) & (dv > 0)
            if not m.any():
                continue
            W = float(tr.tar_wid)
            r_all.append(D.looming(gap[m], dv[m], W, g) / D.looming(gap[m], dv[m], W))
            dt_all.append(np.abs(D.perceived(gap[m], dv[m], W, g)["ttc"] - gap[m] / dv[m]))
        r = np.concatenate(r_all)
        rows.append((design, len(r_all), np.median(r), r.min(), r.max(), float(np.concatenate(dt_all).max())))
    return rows


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    g = D.load_geometry()
    geo = {"off": None, "on": g}
    k = D.gain(g)
    L = ["# Card DT.1 -- the video studies with and without the display transform", "",
         "Generated by `replication/czb/dt1_display_transform.py`; pre-stated in its docstring before"
         " the run. The transform: `docs/display_transform.md`, `src/comfortzone/display.py`. Do not"
         " edit by hand.", "",
         f"Geometry: {g.screen_diagonal_in:g}-inch {g.screen_aspect_w:g}:{g.screen_aspect_h:g} screen,"
         f" {g.viewing_distance_cm:g} cm away, image width fraction {g.image_width_fraction:g}, rendering"
         f" HFOV {g.virtual_hfov_deg:g} deg; the image fills {D.display_hfov_deg(g):.1f} deg; **gain k ="
         f" {k:.4f}** (distances and closing speeds x {1 / k:.2f}; lateral unchanged; TTC invariant).", ""]

    # ---- A: the stimuli -------------------------------------------------------------------
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    W, _ = CL.widths_for(cells)
    gap = cells.distance.to_numpy(float)
    dv = cells.dv_kph.to_numpy(float) * KPH
    td = {m: D.looming(gap, dv, W, geo[m]) for m in MODES}
    repro = float(np.max(np.abs(np.log(td["off"]) - J6.looming_axis(cells))))
    ratio = td["on"] / td["off"]
    dttc = float(np.max(np.abs(D.perceived(gap, dv, W, g)["ttc"] - cells.distance / (cells.dv_kph * KPH))))
    L += ["## A The transform on the stimuli", "",
          "| stimuli | clips/cells | perceived/rendered looming, median | min | max | largest TTC change [s] |",
          "|---|---|---|---|---|---|",
          f"| study 2 cells | {len(cells)} | {np.median(ratio):.4f} | {ratio.min():.4f} | {ratio.max():.4f} | {dttc:.1e} |"]
    for design, n, med, lo, hi, dt in study1_ratios(g):
        L.append(f"| study 1, {design} cut-in traces (all samples closing) | {n} | {med:.4f} | {lo:.4f} | {hi:.4f} | {dt:.1e} |")
    L += ["", f"Reproduction: 'off' equals card EL.1b's looming axis to {repro:.1e} (log units).", ""]
    print(f"A done [{time.time() - t0:.0f} s]", flush=True)

    # ---- B1: 1D thresholds on study 2 ---------------------------------------------------
    post = cells[cells.cp != "CP1"].reset_index(drop=True)
    pm = (cells.cp != "CP1").to_numpy()
    y, w, folds = post.p.to_numpy(float), post.n.to_numpy(float), post.ttc_start.to_numpy(float)
    b1 = {}
    for m in MODES:
        pp = D.perceived(gap[pm], dv[pm], W[pm], geo[m])
        axes = {"log looming": np.log(pp["theta_dot"]), "-log gap": -np.log(pp["r"]), "-log TTC": -np.log(pp["ttc"])}
        for a, x in axes.items():
            s = T.wrmse(y, CL.held_out_1d(x, y, w, folds), w)
            c = T.fit_reg(x, y, w)[1]
            b1[(a, m)] = (s, np.exp(c) if a == "log looming" else np.exp(-c))
    L += ["## B Within the second study (288 post-onset cells, registered folds)", "",
          "### B1 One-dimensional thresholds (card EL.1b)", "",
          "| axis | held out, off | held out, on | level, off | level, on | level on/off |", "|---|---|---|---|---|---|"]
    units = {"log looming": "rad/s", "-log gap": "m", "-log TTC": "s"}
    for a in ("log looming", "-log TTC", "-log gap"):
        (s0, l0), (s1, l1) = b1[(a, "off")], b1[(a, "on")]
        L.append(f"| {a} | {s0:.4f} | {s1:.4f} | {l0:.4g} {units[a]} | {l1:.4g} {units[a]} | {l1 / l0:.3f} |")
    rank = {m: [a for a, _ in sorted(((a, b1[(a, m)][0]) for a in units), key=lambda t: t[1])] for m in MODES}
    L += ["", f"Ranking (best first): off {rank['off']}; on {rank['on']}.", ""]

    # ---- B2: JJ.10 mixture ------------------------------------------------------------------
    lat = J6.CG.lateral_states(cells.video)
    base = cells[["video", "cp", "p", "n", "ttc_start", "ttc_true", "distance", "dv_kph"]].copy()
    base["p_lead"] = p_lead(lat.l0.to_numpy(float), lat.ldot.to_numpy(float), SIGMA_LAT, T_ANTICIPATION)
    curve = {}
    L += ["### B2 The gated intervention curve (card JJ.10's mixture; \"the video curve\")", "",
          "| | post-onset held out | pre-onset | lapse | level [rad/s] | spread |", "|---|---|---|---|---|---|"]
    for m in MODES:
        d = base.copy()
        d["theta_dot"] = td[m]
        r = J10.score("mixture", d)
        th = r["theta"]
        curve[m] = (float(expit(th[0])), float(np.exp(th[1])), float(np.exp(th[2])))
        L.append(f"| {m} | {r['post']:.4f} | {r['cp1']:.4f} | {curve[m][0]:.3f} | {curve[m][1]:.4f} | {curve[m][2]:.3f} |")
    L += ["", f"Level on/off: {curve['on'][1] / curve['off'][1]:.3f}.", ""]
    print(f"B2 done [{time.time() - t0:.0f} s]", flush=True)

    # ---- B3: NC.3o ------------------------------------------------------------------------
    tr = pd.read_csv(R.TRIALS, low_memory=False)
    tr = tr[~tr.video.str.contains("dummy") & tr.CZB_2.isin([0, 1, 2])]
    gg = tr.groupby("video").agg(n2=("CZB_2", "size"), k1=("CZB_2", lambda v: int(np.sum(v >= 1))),
                                 k2=("CZB_2", lambda v: int(np.sum(v == 2)))).reset_index()
    dd = cells.assign(td_off=td["off"], td_on=td["on"]).merge(gg, on="video")
    dd = dd[dd.cp != "CP1"].reset_index(drop=True)
    k1, k2, n2, f2 = (dd[c].to_numpy(float) for c in ("k1", "k2", "n2", "ttc_start"))
    L += ["### B3 Gentle and hard on one looming axis (card NC.3o)", "",
          "| | ordered O held out | separate S held out | verdict | gentle [rad/s] | hard [rad/s] | spread |",
          "|---|---|---|---|---|---|---|"]
    b3 = {}
    for m in MODES:
        x = np.log(dd[f"td_{m}"].to_numpy(float))
        rO, rS = O.held_out(x, k1, k2, n2, f2, "O"), O.held_out(x, k1, k2, n2, f2, "S")
        th = O.fit(x, k1, k2, n2, "O")
        b3[m] = (rO, rS, "SUPPORTED" if rO <= rS + 0.005 else "NOT SUPPORTED")
        L.append(f"| {m} | {rO:.4f} | {rS:.4f} | {b3[m][2]} | {np.exp(th[0]):.4f} |"
                 f" {np.exp(th[0] + np.exp(th[1])):.4f} | {np.exp(th[2]):.2f} |")
    L.append("")
    print(f"B3 done [{time.time() - t0:.0f} s]", flush=True)

    # ---- C1: NC.3 rule (a) ------------------------------------------------------------------
    fp_all, ev = pd.read_pickle(N.CACHE)
    pre, resp = "pre_0.5_0.3", "resp_0.5_0.3"
    e = ev[~ev[pre] & ~ev.lc]
    c = e[e.dv > 0].copy()
    c["theta_dot"] = c.W * c.dv / (c.gap ** 2 + c.W ** 2 / 4)
    yh = c[resp].to_numpy(bool)
    xh = np.log(c.theta_dot.to_numpy(float))
    bins = pd.qcut(xh, 10, labels=False, duplicates="drop")
    r_chance, _ = N.binned_wrmse(np.full(len(yh), yh.mean()), yh, bins)
    th_h = N.fit_curve(xh, yh)
    lvl_h = float(np.exp(th_h[1]))
    L += ["## C Against real traffic (highD is not transformed)", "",
          f"### C1 Card NC.3 rule (a): the video curve on {len(c):,} real closing cut-ins (detector 0.5 m/s^2, 0.3 s)", "",
          "| video curve | binned wRMSE | chance | beats chance | predicted rate | observed rate | highD refit level / video level |",
          "|---|---|---|---|---|---|---|"]
    c1 = {}
    for m in MODES:
        lap, lv, sp = curve[m]
        pr = lap + (1 - lap) * norm.cdf((xh - np.log(lv)) / sp)
        r, _ = N.binned_wrmse(pr, yh, bins)
        c1[m] = (r, r < r_chance, lvl_h / lv)
        L.append(f"| {m} | {r:.4f} | {r_chance:.4f} | {'yes' if r < r_chance else 'NO'} | {pr.mean():.3f} |"
                 f" {yh.mean():.3f} | {lvl_h / lv:.2f} |")
    L += ["", f"highD refit level {lvl_h:.4f} rad/s (all events; NC.3 reports the same curve).", ""]
    print(f"C1 done [{time.time() - t0:.0f} s]", flush=True)

    # ---- C2: NC.3h matching -------------------------------------------------------------------
    ev3, _ = pd.read_pickle(H.CACHE)
    c3 = ev3[~ev3.lc & (ev3.dv > 0)].reset_index(drop=True)
    dummy_hb = {"c": 0.0, "s": 1.0}
    c2 = {}
    L += ["### C2 Card NC.3h: the deceleration at which real followers match the gentle curve", "",
          "| video curve | matching deceleration [m/s^2] | 95% over recordings | wRMSE-minimising |", "|---|---|---|---|"]
    for m in MODES:
        H.INT_LEVEL, H.INT_SPREAD = curve[m][1], curve[m][2]
        a_m, a_w = H.matching(c3, "int", 0.0, dummy_hb)
        rng = np.random.default_rng(20260924)
        ur = c3.rec.unique()
        bs = []
        for _ in range(200):
            idx = np.concatenate([np.flatnonzero(c3.rec.to_numpy() == r) for r in rng.choice(ur, len(ur))])
            bs.append(H.matching(c3.iloc[idx].reset_index(drop=True), "int", 0.0, dummy_hb)[0])
        ci = np.nanpercentile(bs, [2.5, 97.5])
        c2[m] = a_m
        L.append(f"| {m} (level {curve[m][1]:.4f}, spread {curve[m][2]:.3f}) | **{a_m:.2f}** | [{ci[0]:.2f}, {ci[1]:.2f}] | {a_w:.2f} |")
        print(f"C2 {m} done [{time.time() - t0:.0f} s]", flush=True)
    L.append("")

    # ---- C3 and C4 ------------------------------------------------------------------------
    L += ["### C3 Card PT.1: against Farewell's emergency-braking level", "",
          f"| video curve | 50% looming (gate open) [rad/s] | / Farewell's {P1.FAREWELL_THETA_DOT} | share at Farewell's level |",
          "|---|---|---|---|"]
    fifty = {}
    for m in MODES:
        lap, lv, sp = curve[m]
        fifty[m] = float(np.exp(np.log(lv) + sp * norm.ppf((0.5 - lap) / (1 - lap))))
        share = lap + (1 - lap) * norm.cdf((np.log(P1.FAREWELL_THETA_DOT) - np.log(lv)) / sp)
        L.append(f"| {m} | {fifty[m]:.4f} | {fifty[m] / P1.FAREWELL_THETA_DOT:.2f} | {share:.2f} |")
    Wm = float(np.median(W))
    L += ["", "### C4 Convention (b): the real-world TTC at the video curve's 50% looming, at the study's own closing speeds", "",
          f"(target width {Wm:.2f} m)", "",
          "| closing speed [km/h] | TTC, off [s] | TTC, on [s] | on/off |", "|---|---|---|---|"]
    for kph in sorted(cells.dv_kph.unique()):
        t_off = float(D.ttc_at_true_speed(fifty["off"], kph * KPH, Wm))
        t_on = float(D.ttc_at_true_speed(fifty["on"], kph * KPH, Wm))
        L.append(f"| {kph:g} | {t_off:.2f} | {t_on:.2f} | {t_on / t_off:.2f} |")
    L.append("")

    # ---- the labels ---------------------------------------------------------------------------
    s_moved = any(abs(b1[(a, "on")][0] - b1[(a, "off")][0]) >= 0.005 for a in units)
    lab = [
        ("(1) NC.3: the video curve transfers (beats chance)", label(c1["off"][1], c1["on"][1], True)),
        ("(2) NC.3: highD's level within 21% of the video's",
         label(0.8 <= c1["off"][2] <= 1.25, 0.8 <= c1["on"][2] <= 1.25, True)),
        ("(3) PT.1: the comfort boundary lies above Farewell's emergency level",
         label(fifty["off"] > P1.FAREWELL_THETA_DOT, fifty["on"] > P1.FAREWELL_THETA_DOT, True)),
        ("(4) NC.3h: gentle match at about highD's 99th percentile (0.87-1.22 m/s^2)",
         label(0.87 <= c2["off"] <= 1.22, 0.87 <= c2["on"] <= 1.22, True)),
        ("(5) study 2 axis ranking looming < TTC < gap",
         label(rank["off"] == ["log looming", "-log TTC", "-log gap"], rank["on"] == ["log looming", "-log TTC", "-log gap"], s_moved)),
        ("(6) NC.3o: two levels on one observation SUPPORTED",
         label(b3["off"][2] == "SUPPORTED", b3["on"][2] == "SUPPORTED", abs(b3["on"][0] - b3["off"][0]) >= 0.005)),
        ("(7) the TTC boundaries (NC.3i, NC.3j, NC.3l)", "UNCHANGED" if dttc < 1e-9 else "SHIFTED"),
    ]
    L += ["## The labels", "", "| conclusion | with the display transform |", "|---|---|"]
    L += [f"| {a} | **{b}** |" for a, b in lab]
    L += ["", "D (by construction, checked in A): TTC is unchanged, so every TTC-based boundary stands; the"
          " transform is monotone in looming and highD is not transformed, so AUCs on highD (NC.3 rule (b),"
          " NC.4c) and per-driver rank results (TR.1) are unchanged.", "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "dt1_display_transform.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
