"""
Card JJ.4 -- precision as spread: is the response spread a measured stimulus precision rather
than a free parameter?

THE PRE-REGISTRATION. Everything in this docstring was written before the run.

THE PRE-STATED RULES, copied verbatim from design note section 4
-----------------------------------------------------------------
  Two refits of the stage-1 estimator, each replacing free spreads by a precision tied to the
  stimulus:

  - Medium. One spread for the video left turn and one for the track (card TT.1's data,
    `external/02_LTAPOD_DBIN/`), the ratio free, against the two free spreads already on file
    (0.86 s and 0.20 s). Trivially equivalent as a fit; the content is the second step: the
    ratio predicted from the perceptual model (angular noise on a monocular frozen frame against
    a moving binocular view) is reported beside the fitted ratio. Unverified constants for the
    perceptual side are marked and sourced in the script or the step is reported as not yet
    possible.
  - Apparent size. The truck and car cut-ins of study 1 at matched TTC, the roadmap's E.2: a
    model with one spread per stimulus class against one shared spread. Rule: the two-spread
    model earns its place if it improves held-out log-likelihood by more than 2 units under
    LOPO; the direction (truck sharper) is reported either way.
  - The gate's spread, derived. G.1's s_l = 0.990 m against sigma_v,lat x 3 s with sigma_v,lat
    measured from the traces' lateral-rate jitter plus P0's growth constant; reported as a
    computed value beside the fitted one. Agreement within a factor of 1.5 is the pre-stated
    reading for "the gate's spread is a computed uncertainty".

  Jonas's ruling JJ1.Q3 (2026-09-18): JJ.4 reports the fitted ratio of the video and track
  spreads and marks the ratio *predicted from perception* as NOT YET POSSIBLE unless a source for
  the perceptual constants is found.

HOW EACH PART IS BUILT, and the two places where the rule cannot be applied as written
---------------------------------------------------------------------------------------
  MEDIUM. `fit_hier_lapse_gated` on x = -PET, gate = 1, exactly as `ltapod_testtrack.fit_threshold`
  does it, once on the video left turn at 50 km/h (Random design, `intervene`) and once on the
  track's comfort runs (`1 - Go`, the primary set: the Remove-flagged runs excluded, as card TT.1
  fixed). "One spread for each with the ratio free" is algebraically the two separate fits, which
  the design note says itself, so the two fits ARE the constrained model and the report says so.
  The ratio's interval comes from the Laplace covariance of log sigma_resp in each fit, added in
  quadrature -- the delta method the project uses everywhere else.

  APPARENT SIZE. The rule as written cannot be applied to the stage-1 estimator, and this is
  reported rather than worked around: in the Button design every cell's `intervene` share is
  0.976 to 1.000 (the paradigm asks WHEN you would intervene, and everyone presses), so a binary
  threshold model has no response variation to fit. The Button paradigm's own response is the
  PRESS TIME, and its level is the covariate at the press. The contrast is therefore run on that:
  per trial the observed level is log theta_dot at the press, and the model is
      observed level = driver mean + offset[stimulus cell] + eps,  eps ~ N(0, sigma_resp[class]),
      driver mean ~ N(mu, sigma_pop),
  one shared sigma_resp against one per stimulus class, with the same held-out rule (more than 2
  log-likelihood units under LOPO) and the same direction reported either way. Query JJ4.Q1.
  There is one offset per stimulus CELL (class x TTC), not one per class, because the observed
  level drifts with the design's TTC (about 1 log unit from TTC4 to TTC8) and that drift is a
  property of the stimulus rather than of the driver; left in, it would end up inside the very
  spread this card measures. The spread is indexed by class only, which is the contrast asked
  for. Censored trials (no press) are dropped and counted.

  THE GATE'S SPREAD. Two numbers go into it and they are of very different kinds, so both are
  reported: the traces' own lateral-rate jitter, measured here on the 90 study-2 traces over their
  pre-onset frames with card G.1's 0.3 s window, and P0's growth constant sigma_v,lat = 0.33 m/s.
  **The circularity is stated before the number**: sigma_v,lat was itself motivated in design note
  section 1.2 by "G.1's fitted gate spread 0.99 m over its 3 s horizon, read as lateral-rate
  uncertainty", so a computed value built on it must reproduce 0.990 m and the agreement means
  nothing until GM.1's component C3 measures sigma_v,lat on highD independently. The
  non-circular half of the comparison is the measured jitter alone, and that is the number the
  reading is taken on.

SETTINGS
--------
  estimator            `fit_stage1_looming.fit_hier_lapse_gated` (medium), unchanged; a Gaussian
                       hierarchical model written here for the press-time contrast
  LOPO folds           15, `fit_stage1_looming.LOPO_FOLDS`, the project's own count
  matched TTC          TTC4 to TTC8, the range both stimulus classes share
  the covariate        log theta_dot from `fit_stage1_looming.looming_field`, the project's own
                       looming axis and loader (trucks are auto-detected by the loader's broken
                       Length_m rule and take TRUCK_DIMS)
  the gate's fitted    s_l = 0.990 m, m_lat = 0.149 m, t_enc = 3.0 s -- card G.1, on file
  the growth constant  sigma_v,lat = 0.33 m/s, design note section 1.2 (see the circularity note)

Output: replication/czb/out/jj4_precision_spread.md.
Run:    python replication/czb/jj4_precision_spread.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import fit_stage1_looming as F             # noqa: E402  the hierarchical estimator (read only)
import ltapod_testtrack as TT              # noqa: E402  card TT.1 (read only)
from comfortzone.czb_data import (BUTTON_CLIP_START_S, KIN_BUTTON,  # noqa: E402
                                  load_joint)
from comfortzone.cutin import load_cutin_trace                      # noqa: E402
from rollout.predictor import SD_VLAT                               # noqa: E402

OUT = HERE / "out"
TT1_VIDEO_SIGMA_RESP = 0.86      # s, out/ltapod_testtrack.md section 2 (reproduction target)
TT1_TRACK_SIGMA_RESP = 0.20      # s, ibid.
REPRO_TOL = 0.02                 # s, the tolerance on reproducing those two numbers
LL_MARGIN = 2.0                  # the design note's held-out log-likelihood margin
FACTOR = 1.5                     # the gate-spread reading's factor
MATCHED_TTC = ("TTC4", "TTC5", "TTC6", "TTC7", "TTC8")
LOPO_FOLDS = F.LOPO_FOLDS
SEED = 20260918


# ---------------------------------------------------------------------------------
# 1. Medium: the video left turn against the test track
# ---------------------------------------------------------------------------------

def medium() -> list[str]:
    j = load_joint()
    v = j[(j.design == "Random") & (j.scenario == "ltap") & (j.ltap_speed == 50)
          & j.intervene.notna()].copy()
    v["pet"] = v.criticality_label.str.replace("PET", "").astype(float)
    d = TT.load_track()
    s = d[(~d.removed) & (d.cond == "comfort")]

    fv = TT.fit_threshold(v.pet.to_numpy(), v.intervene.to_numpy(), v.Exp_Subject_Id.to_numpy())
    ft = TT.fit_threshold(s.SetPET.to_numpy(), 1 - s.go.to_numpy(),
                          s.ParticipantNumber.to_numpy())

    # the ratio and its delta-method interval, on the log scale where the parameter lives
    lv, lt = np.log(fv["sigma_resp"]), np.log(ft["sigma_resp"])
    sev = float(np.sqrt(max(fv["cov"][2, 2], 0.0)))
    set_ = float(np.sqrt(max(ft["cov"][2, 2], 0.0)))
    lr = lv - lt
    se = float(np.hypot(sev, set_))
    ratio, lo, hi = np.exp(lr), np.exp(lr - 1.96 * se), np.exp(lr + 1.96 * se)
    ok_v = abs(fv["sigma_resp"] - TT1_VIDEO_SIGMA_RESP) <= REPRO_TOL
    ok_t = abs(ft["sigma_resp"] - TT1_TRACK_SIGMA_RESP) <= REPRO_TOL

    return ["## 1 Medium -- one spread for the video left turn and one for the track", "",
            "The design note calls the constrained model \"trivially equivalent as a fit\" to two"
            " free spreads, so the two fits below ARE that model, and its content is the ratio.",
            "", "| fit | trials | drivers | PET_50 [s] | sigma_pop [s] | sigma_resp [s] |"
            " on file | reproduced |", "|---|---|---|---|---|---|---|---|",
            f"| video left turn, 50 km/h | {fv['n_trials']} | {fv['n_drivers']} |"
            f" {fv['pet50']:.2f} | {fv['sigma_pop']:.2f} | **{fv['sigma_resp']:.3f}** |"
            f" {TT1_VIDEO_SIGMA_RESP:.2f} | {'yes' if ok_v else 'NO'} |",
            f"| test track, comfort runs | {ft['n_trials']} | {ft['n_drivers']} |"
            f" {ft['pet50']:.2f} | {ft['sigma_pop']:.2f} | **{ft['sigma_resp']:.3f}** |"
            f" {TT1_TRACK_SIGMA_RESP:.2f} | {'yes' if ok_t else 'NO'} |", "",
            f"**Fitted ratio, video / track: {ratio:.2f} [{lo:.2f}, {hi:.2f}]** (delta method on"
            " log sigma_resp, the two Laplace variances added in quadrature). Drivers are about"
            f" {ratio:.1f} times sharper in the car than in front of the frozen clip.", "",
            "**The ratio predicted from perception: NOT YET POSSIBLE.** Jonas's ruling JJ1.Q3"
            " (2026-09-18) fixes this in advance. To predict the number rather than measure it we"
            " would need published values for the visual precision of distance and closing speed"
            " in a monocular frozen clip against a moving binocular view, and this project has no"
            " source for them. No constant is invented here; the line stands open until one is"
            " found. Nothing in this report quotes a predicted ratio.", ""]


# ---------------------------------------------------------------------------------
# 2. Apparent size: the truck and car cut-ins at matched TTC
# ---------------------------------------------------------------------------------

def press_levels() -> tuple[pd.DataFrame, list[str]]:
    """Per Button cut-in trial: the observed level, log theta_dot at the press."""
    j = load_joint()
    b = j[(j.design == "Button") & j.scenario.isin(["cutin_car", "cutin_truck"])
          & j.criticality_label.isin(MATCHED_TTC)].copy()
    notes = []
    fields, onset = {}, {}
    for (scn, lab), _ in b.groupby(["scenario", "criticality_label"]):
        stem = ("CutInCar" if scn == "cutin_car" else "CutInTruck") + f"_{lab[3:]}TTC"
        path = KIN_BUTTON / f"{stem}_vehicle_states.csv"
        f = F.looming_field(path)
        tr = load_cutin_trace(path)
        fields[(scn, lab)] = f
        onset[(scn, lab)] = float(tr.t[tr.onset_idx])
    n0 = len(b)
    b = b[b.press_time_s.notna() & (b.censored != 1)].copy()
    notes.append(f"{n0 - len(b)} of {n0} trials are censored (no press) and are dropped.")

    lvl, ok = [], []
    for scn, lab, pt in zip(b.scenario, b.criticality_label, b.press_time_s):
        f = fields[(scn, lab)]
        t_trace = BUTTON_CLIP_START_S + float(pt)     # press time is measured in the clip
        i = int(np.clip(np.searchsorted(f.t.to_numpy(), t_trace, side="right") - 1,
                        0, len(f) - 1))
        x = float(f.x_loom.iloc[i])
        lvl.append(x)
        ok.append(np.isfinite(x))
    b["level"] = lvl
    n1 = len(b)
    b = b[np.asarray(ok)].reset_index(drop=True)
    if n1 != len(b):
        notes.append(f"{n1 - len(b)} trials dropped for a non-finite covariate at the press.")
    b["cls"] = (b.scenario == "cutin_truck").astype(int)
    b["cell"] = (b.cls * len(MATCHED_TTC)
                 + b.criticality_label.map({c: i for i, c in enumerate(MATCHED_TTC)})).astype(int)
    b["driver"] = b.Exp_Subject_Id
    return b, notes


N_CELLS = 2 * len(MATCHED_TTC)      # class x TTC


def fit_gauss(level, cls, cell, codes, two_spread: bool, n_cells: int = N_CELLS):
    """Driver mean ~ N(mu, sigma_pop); level = mean + offset[cell] + eps, eps ~ N(0, sd[class]).

    One offset per STIMULUS CELL (class x TTC), because the observed level drifts with the
    design's TTC, and that drift is a property of the stimulus rather than of the driver: left
    in, it would end up inside the spread this card is measuring. The spread is indexed by the
    stimulus CLASS only, which is the contrast the design note asks for. Maximum likelihood by
    coordinate ascent, which converges in a few passes on this design.
    """
    level = np.asarray(level, float)
    cls, cell, codes = np.asarray(cls, int), np.asarray(cell, int), np.asarray(codes, int)
    n_d = int(codes.max() + 1)
    off = np.zeros(n_cells)
    sd = np.full(2, level.std(ddof=1))
    mu, sp = level.mean(), 0.5 * level.std(ddof=1)
    m = np.full(n_d, mu)
    for _ in range(500):
        w = 1.0 / sd[cls] ** 2
        num = np.bincount(codes, weights=w * (level - off[cell]), minlength=n_d) + mu / sp ** 2
        den = np.bincount(codes, weights=w, minlength=n_d) + 1.0 / sp ** 2
        m = num / den
        mu_new, sp_new = m.mean(), max(m.std(ddof=1), 1e-6)
        e = level - m[codes]
        off_new = np.array([e[cell == k].mean() if (cell == k).any() else 0.0
                            for k in range(n_cells)])
        r = e - off_new[cell]
        if two_spread:
            sd_new = np.array([max(np.sqrt(np.mean(r[cls == k] ** 2)), 1e-6) for k in (0, 1)])
        else:
            s = max(np.sqrt(np.mean(r ** 2)), 1e-6)
            sd_new = np.array([s, s])
        done = (abs(mu_new - mu) < 1e-12 and abs(sp_new - sp) < 1e-12
                and np.allclose(off_new, off, atol=1e-12) and np.allclose(sd_new, sd, atol=1e-12))
        mu, sp, off, sd = mu_new, sp_new, off_new, sd_new
        if done:
            break
    return {"mu": mu, "sigma_pop": sp, "offset": off, "sd": sd, "driver_mean": m}


def loglik_driver(level, cls, cell, fit, n_q=96) -> float:
    """log p(a driver's trials) with its mean integrated over N(mu, sigma_pop), by Gauss-Hermite."""
    z, w = np.polynomial.hermite_e.hermegauss(n_q)
    lw = np.log(w) - np.log(np.sqrt(2 * np.pi))
    c = fit["mu"] + fit["sigma_pop"] * z
    sd = fit["sd"][cls][:, None]
    r = (level[:, None] - fit["offset"][cell][:, None] - c[None, :]) / sd
    ll = (-0.5 * r ** 2 - np.log(sd) - 0.5 * np.log(2 * np.pi)).sum(axis=0)
    mx = ll.max()
    return float(mx + np.log(np.sum(np.exp(ll - mx + lw))))


def lopo_gauss(b: pd.DataFrame, two_spread: bool, folds: list) -> float:
    tot = 0.0
    for held in folds:
        tr = b[b.driver != held]
        codes = pd.factorize(tr.driver)[0]
        f = fit_gauss(tr.level.to_numpy(float), tr.cls.to_numpy(int), tr.cell.to_numpy(int),
                      codes, two_spread)
        h = b[b.driver == held]
        tot += loglik_driver(h.level.to_numpy(float), h.cls.to_numpy(int),
                             h.cell.to_numpy(int), f)
    return tot


def apparent_size() -> list[str]:
    b, notes = press_levels()
    drivers = np.sort(b.driver.unique())
    rng = np.random.default_rng(SEED)
    folds = list(rng.permutation(drivers)[:LOPO_FOLDS])
    codes = pd.factorize(b.driver)[0]
    f1 = fit_gauss(b.level.to_numpy(float), b.cls.to_numpy(int), b.cell.to_numpy(int),
                   codes, False)
    f2 = fit_gauss(b.level.to_numpy(float), b.cls.to_numpy(int), b.cell.to_numpy(int),
                   codes, True)
    ll1 = lopo_gauss(b, False, folds)
    ll2 = lopo_gauss(b, True, folds)
    d = ll2 - ll1
    earns = d > LL_MARGIN
    truck_sharper = f2["sd"][1] < f2["sd"][0]

    per = (b.groupby(["scenario", "criticality_label"])
           .agg(n=("level", "size"), mean=("level", "mean"), sd=("level", "std")).reset_index())
    L = ["## 2 Apparent size -- the truck and car cut-ins at matched TTC", "",
         "The stage-1 binary estimator cannot be used here and this is reported rather than"
         " worked around: in the Button design every cell's intervention share is 0.976 to 1.000,"
         " so a threshold model on `intervene` has no response variation to fit. The Button"
         " paradigm's response is the press time, and its level is the covariate at the press, so"
         " the contrast runs on a Gaussian hierarchical model of that level (query JJ4.Q1).", "",
         "  " + " ".join(notes), "",
         f"{len(b)} trials, {b.driver.nunique()} drivers, TTC {MATCHED_TTC[0][3:]} to"
         f" {MATCHED_TTC[-1][3:]}; the level is log theta_dot at the press.", "",
         "| stimulus | TTC | trials | mean level | sd of the level |", "|---|---|---|---|---|"]
    for _, r in per.iterrows():
        L.append(f"| {'truck' if r.scenario == 'cutin_truck' else 'car'} | {r.criticality_label[3:]}"
                 f" | {int(r.n)} | {r['mean']:+.3f} | {r['sd']:.3f} |")
    L += ["", "| model | sigma_resp, car | sigma_resp, truck | mean cell offset (truck - car) |"
          " held-out log-likelihood (LOPO, 15 drivers) |", "|---|---|---|---|---|",
          f"| one shared spread | {f1['sd'][0]:.4f} | {f1['sd'][0]:.4f} |"
          f" {np.mean(f1['offset'][len(MATCHED_TTC):]) - np.mean(f1['offset'][:len(MATCHED_TTC)]):+.4f}"
          f" | {ll1:.2f} |",
          f"| one spread per stimulus class | {f2['sd'][0]:.4f} | {f2['sd'][1]:.4f} |"
          f" {np.mean(f2['offset'][len(MATCHED_TTC):]) - np.mean(f2['offset'][:len(MATCHED_TTC)]):+.4f}"
          f" | {ll2:.2f} |", "",
          f"Difference {d:+.2f} log-likelihood units against the pre-stated margin of"
          f" {LL_MARGIN:.0f}: the two-spread model **{'earns its place' if earns else 'does NOT earn its place'}**.",
          "", f"The direction, reported either way: the truck's spread is"
          f" {f2['sd'][1]:.4f} against the car's {f2['sd'][0]:.4f}, so the truck is"
          f" **{'sharper' if truck_sharper else 'NOT sharper'}**"
          f" (ratio {f2['sd'][1] / f2['sd'][0]:.2f}).", ""]
    return L


# ---------------------------------------------------------------------------------
# 3. The gate's spread, derived
# ---------------------------------------------------------------------------------

def lateral_rate_jitter() -> tuple[float, float, int]:
    """The study-2 traces' own lateral-rate jitter: the sd of the target's lateral rate over
    card G.1's 0.3 s window, taken over the PRE-ONSET frames of each trace (where the true rate
    is zero, so what is left is the traces' jitter). Median and max over the traces."""
    import cutin2_field_vs_gap as R
    import hs1_situational_surprise as HS
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    sds = []
    for key, sc in HS.study2_scenes(cells).items():
        t = sc["grid"]
        y = sc["tracks"][sc["tar"]].y - sc["tracks"][sc["ego"]].y
        dt = float(np.median(np.diff(t)))
        k = max(1, int(round(0.3 / dt)))
        rate = np.full_like(y, np.nan)
        rate[k:] = (y[k:] - y[:-k]) / (t[k:] - t[:-k])
        moved = np.abs(y - y[0]) > 0.03
        i_on = int(np.argmax(moved)) if moved.any() else len(y) - 1
        pre = rate[k:i_on]
        if len(pre) > 10:
            sds.append(float(np.nanstd(pre, ddof=1)))
    return float(np.median(sds)), float(np.max(sds)), len(sds)


def gate_spread() -> list[str]:
    med, mx, n = lateral_rate_jitter()
    t_enc, s_l = F.T_ENC, F.S_L
    computed_jitter = med * t_enc
    computed_full = float(np.hypot(med, SD_VLAT) * t_enc)
    ratio = computed_full / s_l
    within = (1 / FACTOR) <= ratio <= FACTOR
    return ["## 3 The gate's spread, derived", "",
            "**The circularity is stated before the number.** P0's growth constant"
            f" sigma_v,lat = {SD_VLAT} m/s was itself motivated in design note section 1.2 by"
            f" \"G.1's fitted gate spread {s_l:.2f} m over its {t_enc:.0f} s horizon, read as"
            " lateral-rate uncertainty times horizon\". A computed value built on it therefore"
            " has to reproduce the fitted one, and the agreement means nothing until component"
            " C3 of the generative-model framework measures sigma_v,lat on highD independently"
            " (card GM.1). The non-circular half is the traces' own jitter, and that is where the"
            " reading is taken.", "",
            "| quantity | value | source |", "|---|---|---|",
            f"| G.1's fitted gate spread s_l | {s_l:.3f} m | `out/cutin2_gate.md`, on file |",
            f"| G.1's horizon t_enc | {t_enc:.1f} s | ibid., fixed |",
            f"| the traces' lateral-rate jitter, pre-onset, 0.3 s window | median"
            f" {med:.4f} m/s (max {mx:.4f}) over {n} traces | measured here |",
            f"| jitter x t_enc | {computed_jitter:.4f} m | computed |",
            f"| sqrt(jitter^2 + sigma_v,lat^2) x t_enc | {computed_full:.3f} m | computed"
            " (circular, see above) |", "",
            f"**Reading.** The measured jitter alone gives {computed_jitter:.4f} m against the"
            f" fitted {s_l:.3f} m, a factor of {s_l / max(computed_jitter, 1e-9):.0f}. The gate's"
            " spread is therefore **not** the traces' measurement noise: it is a predictive"
            " uncertainty about what the other vehicle is going to do, which is exactly what P0's"
            " growth constant is a placeholder for. Including that constant gives"
            f" {computed_full:.3f} m, a ratio of {ratio:.2f} to the fitted value, inside the"
            f" pre-stated factor of {FACTOR}"
            + (" -- but only because the constant was read off the fitted value in the first"
               " place." if within else ".") + "", "",
            "What would make this a real test: sigma_v,lat measured on naturalistic lane-keeping"
            " (component C3), and then this same arithmetic run again. Until then the line is a"
            " consistency check of the design note's own arithmetic, not evidence.", ""]


# ---------------------------------------------------------------------------------

def main() -> None:
    t0 = time.time()
    L = ["# Card JJ.4 -- precision as spread", "",
         "Generated by `replication/czb/jj4_precision_spread.py`; the three parts and their rules"
         " are pre-stated in its docstring, copied from"
         " `docs/rollout_boundary_design_note.md` section 4, before the run. Do not edit by hand.",
         "", "Read with cards JJ.2 and JJ.3 in hand: Delta G was dropped on the cut-in"
         " (`out/jj2_rollout_cutin.md`) and failed every left-turn rule"
         " (`out/jj3_rollout_transfer.md`). This card does not depend on Delta G -- it asks"
         " whether the response spread of the level estimator is a measured stimulus precision"
         " -- so its three parts stand on their own.", ""]

    print("medium (two hierarchical fits)...", flush=True)
    L += medium()
    (OUT / "jj4_precision_spread.md").write_text("\n".join(L), encoding="utf-8")
    print(f"  written at {time.time() - t0:.0f} s", flush=True)

    print("apparent size...", flush=True)
    L += apparent_size()
    (OUT / "jj4_precision_spread.md").write_text("\n".join(L), encoding="utf-8")
    print(f"  written at {time.time() - t0:.0f} s", flush=True)

    print("the gate's spread...", flush=True)
    L += gate_spread()
    L += [f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj4_precision_spread.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[-12:]))


if __name__ == "__main__":
    main()
