"""
Card EX.1 -- where does repeated exposure act, and is it a learned anticipation?

PRE-STATED before the run (2026-09-17). Nothing in this docstring was changed after the first run
unless a dated note says so.

WHY. Jonas, 2026-09-17: participants shown critical clips over and over may learn an "unnatural"
anticipation; if it is a separate component indexed by exposure, it would be off in naturalistic
data. The assessment on file (worklog, 2026-09-17) said the component is sound if indexed by
within-study exposure and estimated where exposure varies independently of the stimulus, and that
where it enters the model depends on a split never made: whether the repetition effect sits before
the manoeuvre starts (the gate opens earlier: anticipation) or across all onset times (a criterion
shift: the level or the lapse). This card makes that split, plus the three checks that decide
whether a component is worth building.

WHAT IS ALREADY ON FILE, and one correction to how it was read. `out/cutin2_scope.md` section 4
reports P(intervene) 0.547 -> 0.575 (+0.027, SE 0.007) over 3 456 first/second-showing pairs. Its
script built the pairs from `post = d[d.CP != "CP1"]`, so that number is POST-ONSET ONLY. The
worklog of 2026-08-28 and 2026-09-17 read it as the overall exposure effect. The pre-onset (CP1)
repetition effect has never been computed. This card computes both.

DATA
  Study 2, the cut-in (`cutin2_field_vs_gap.TRIALS`): 144 participants, one session, every
    non-filler clip shown exactly twice, the two showings interleaved (median 21 trials apart;
    correlation of showing index with trial position 0.58). Response `CZB_1` (0/1). Onset timepoint
    `CP` (CP1 ends before the lateral manoeuvre starts; card G.1: lateral clearance flat, rate 0).
    Filler (dummy) trials excluded. The unit of a pair is participant x video.
  Study 1, the left turn (`Random_Button_Joint.csv`, scenario "ltap", design "Random"): 43
    participants, 18 cells (9 design PET levels x 2 oncoming speeds), every cell shown four times,
    two in each of two sessions (showing index by session, then `Trial_Nr`, per dictionary gotcha
    4). Response `intervene` (0/1). Cell geometry from `comfortzone.ltap.ltap_cells`.

UNCERTAINTY. Everything is resampled by participant (cluster bootstrap), 2 000 resamples, seed
20260917; 1 000 for the parts that refit a model (B2). 95% percentile intervals. A contrast is
"reliable" when its interval excludes zero.

PART A -- THE CUT-IN

A1 Where does repetition act? Per onset timepoint and pooled post-onset (CP2-CP5): P(intervene) on
   the first and second showing, the difference, and the within-pair conditional odds ratio from
   the discordant pairs, OR = (second yes, first no + 0.5) / (first yes, second no + 0.5). The
   primary contrast is log OR(CP1) - log OR(post-onset), which compares the two on a scale that does
   not favor the post-onset cells' mid-range base rate. READINGS, applied in order:
     R1 exposure acts on the GATE (learned anticipation): CP1 difference reliable > 0 AND the log-OR
        contrast reliable > 0.
     R2 exposure acts UNIFORMLY (a criterion shift, on the level or lapse): post-onset difference
        reliable > 0 AND the log-OR contrast not reliable.
     R3 exposure acts POST-ONSET ONLY: post-onset difference reliable > 0, CP1 difference not
        reliable, and the log-OR contrast reliable < 0.
     R4 NO RELIABLE EXPOSURE EFFECT: neither the CP1 nor the post-onset difference is reliable.
     otherwise: MIXED, reported as found.
   The number of discordant CP1 pairs is reported first, because at a CP1 base rate of a few
   percent R1 may be unidentifiable; if fewer than 30, R1 is declared unidentifiable rather than
   rejected.

A2 Clip familiarity or general practice? For each pair, d = y(second) - y(first) and lag = the
   distance between the two showings as a fraction of the participant's session. Least squares
   d = a + g * lag, pooled over post-onset pairs and separately for CP1. The intercept a is the
   repetition effect at zero lag (recognition of that clip); the slope g is what elapsed trials add.
   READINGS: a reliable > 0 -> clip-specific familiarity; g reliable > 0 -> general practice (the
   later showing is later in the session); g reliable < 0 -> familiarity that decays with lag. The
   distinction matters for Jonas's proposal: only clip-specific familiarity is certain to be zero
   in naturalistic data; general practice with the scenario type is closer to legitimate experience.

A3 Is it a per-driver property? Per participant, the mean pair difference over post-onset pairs.
   Split-half reliability over 200 random splits of that participant's clips into halves,
   Spearman-Brown corrected. READING: a per-driver exposure parameter is supportable if the
   corrected reliability is at least 0.5 (a convention, query EX1.Q1); below that, a
   population-level exposure term only. Reported without a verdict: Spearman correlation of the
   per-driver effect with the driver's first-showing post-onset rate and first-showing CP1 rate.

A4 How big is it in model units? Card G.1's gated rule (`cutin2_gate.fit_gated`, its starts and
   bounds, lateral states from `out/cutin2_gate_states.csv`) fitted on the 288 post-onset cells
   built from first showings only and, separately, from second showings only; the CP1 cells of
   each predicted out of sample. Reported: weight w, lapse, threshold c, sigma, m_lat, s_l, and the
   CP1 predicted and observed mean for each. The shift is c(second) - c(first) on the rule's axis,
   negative = responding at a less critical scene, and as a fraction of sigma. No interval (a
   refit per resample is too slow here); the inferential statement is A1's. Since w is near 0.5 on
   this data, 2 x delta c is the shift in log looming rate; that conversion is stated only if both
   fitted w lie in [0.45, 0.55].

PART B -- THE LEFT TURN

B1 Does responding change over four showings, and where? P(intervene) by showing (1-4) and by PET
   band: near (PET 0-1.0 s), mid (1.5-2.5 s), far (3.0-4.0 s); differences last - first per band,
   and within session 1 (2 - 1), across the session boundary (3 - 2), within session 2 (4 - 3).
B2 The distance rule (card B.3.v2: `cutin2_two_axis.fit_reg` on -log oncoming distance) fitted on
   the 18 cells of the first showing and of the last; reported as the boundary distance
   D* = exp(-c) in metres, its equivalent time at 50 and 70 km/h (D* / speed), sigma and lapse; the
   log ratio of D* (last / first) and of sigma with 1 000-resample intervals.
   READINGS, applied in order:
     L1 LEARNED ANTICIPATION: far-band difference reliable > 0 (responding rises where the oncoming
        car is far and the turn is least critical).
     L2 DISCRIMINATION LEARNING: sigma ratio reliable < 1, or far-band difference reliable < 0
        while the near-band difference is not reliable < 0 (drivers get sharper, not jumpier).
     L3 A GENERAL CRITERION SHIFT: all three bands' differences reliable with the same sign and the
        sigma ratio not reliable.
     L4 NONE: no band's difference reliable and the sigma ratio not reliable.
     otherwise: MIXED, reported as found.
B3 Clip familiarity or practice, as A2, on the within-session pairs (showings 1-2, 3-4), pooled.
B4 Per-driver reliability, as A3, on the per-driver mean of (showings 3-4) - (showings 1-2) over the
   18 cells, split by cells.

CONTEXT, reported without a verdict: card TT.1 puts the video left-turn boundary 0.27 s more
cautious than the test track and the video drivers four times less sharp. L1 would read toward a
learned lab anticipation; L2 would read the other way.

Output: replication/czb/out/ex1_exposure_split.md, out/ex1_driver_exposure.csv
Run:    python replication/czb/ex1_exposure_split.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import cutin2_field_vs_gap as R            # noqa: E402  registered R.2 script (read only)
import cutin2_two_axis as T                # noqa: E402  card EL.1
import cutin2_gate as G                    # noqa: E402  card G.1
from comfortzone.ltap import JOINT, ltap_cells   # noqa: E402

OUT = HERE / "out"
SEED = 20260917
N_BOOT = 2000
N_BOOT_FIT = 1000
N_SPLITS = 200
MIN_DISCORDANT = 30
REL_MIN = 0.5
BANDS = {"near": (0.0, 1.0), "mid": (1.5, 2.5), "far": (3.0, 4.0)}


def boot_counts(n_subj, n_boot, rng):
    """Multinomial resample counts, one row per resample: how often each participant is drawn."""
    idx = rng.integers(0, n_subj, size=(n_boot, n_subj))
    counts = np.zeros((n_boot, n_subj))
    np.add.at(counts, (np.repeat(np.arange(n_boot), n_subj), idx.ravel()), 1.0)
    return counts


def ci(x):
    lo, hi = np.nanpercentile(x, [2.5, 97.5])
    return float(lo), float(hi)


def fmt_ci(est, lo, hi, nd=3):
    return f"{est:+.{nd}f} [{lo:+.{nd}f}, {hi:+.{nd}f}]"


def reliable(lo, hi):
    return lo > 0 or hi < 0


# ---------------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------------

def cutin_pairs():
    d = pd.read_csv(R.TRIALS, low_memory=False)
    d = d[d.block != "Filler"].copy()
    d = d.sort_values(["Exp_Subject_Id", "Trial_Nr"])
    d["pass_idx"] = d.groupby(["Exp_Subject_Id", "video"]).cumcount()
    d["pos"] = d.groupby("Exp_Subject_Id").cumcount()
    d["pos01"] = d.pos / d.groupby("Exp_Subject_Id").pos.transform("max")
    two = d[d.pass_idx < 2]
    y = two.pivot_table(index=["Exp_Subject_Id", "video"], columns="pass_idx", values="CZB_1")
    o = two.pivot_table(index=["Exp_Subject_Id", "video"], columns="pass_idx", values="pos01")
    cp = two.groupby(["Exp_Subject_Id", "video"]).CP.first()
    pairs = pd.DataFrame({"y0": y[0], "y1": y[1], "lag": o[1] - o[0], "cp": cp}).dropna().reset_index()
    return d, pairs


def ltap_trials():
    j = pd.read_csv(JOINT, low_memory=False)
    r = j[(j.scenario == "ltap") & (j.design == "Random")].copy()
    r["pet"] = r.criticality_label.str.replace("PET", "").astype(float)
    r = r.rename(columns={"ltap_speed": "speed_kph"})
    r = r.sort_values(["Exp_Subject_Id", "Session_Nr", "Trial_Nr"])
    r["show"] = r.groupby(["Exp_Subject_Id", "pet", "speed_kph"]).cumcount()
    r["pos"] = r.groupby(["Exp_Subject_Id", "Session_Nr"]).cumcount()
    r["pos01"] = r.pos / r.groupby(["Exp_Subject_Id", "Session_Nr"]).pos.transform("max")
    return r


# ---------------------------------------------------------------------------------
# shared estimators
# ---------------------------------------------------------------------------------

def pair_stats(pairs, subjects):
    """Per-subject sums [n, y0, y1, n10, n01] for a set of pairs."""
    g = pairs.assign(n=1.0, n10=((pairs.y1 == 1) & (pairs.y0 == 0)).astype(float),
                     n01=((pairs.y0 == 1) & (pairs.y1 == 0)).astype(float))
    s = g.groupby("Exp_Subject_Id")[["n", "y0", "y1", "n10", "n01"]].sum()
    return s.reindex(subjects).fillna(0.0).to_numpy()


def pair_summary(S, counts):
    """Point estimates and bootstrap arrays of p0, p1, diff, log OR from per-subject sums."""
    def est(tot):
        n, y0, y1, n10, n01 = tot.T if tot.ndim == 2 else tot
        p0, p1 = y0 / n, y1 / n
        return p0, p1, p1 - p0, np.log((n10 + 0.5) / (n01 + 0.5))
    point = est(S.sum(0))
    boot = est(counts @ S)
    return point, boot


def lag_regression(pairs, subjects, counts):
    """d = a + g lag by least squares, with per-subject sums so resamples are closed form."""
    g = pairs.assign(d=pairs.y1 - pairs.y0, one=1.0)
    g = g.assign(l=g.lag, ll=g.lag ** 2, dl=g.lag * (g.y1 - g.y0))
    s = g.groupby("Exp_Subject_Id")[["one", "l", "ll", "d", "dl"]].sum().reindex(subjects).fillna(0.0).to_numpy()

    def solve(t):
        n, sl, sll, sd, sdl = t.T if t.ndim == 2 else t
        det = n * sll - sl ** 2
        slope = (n * sdl - sl * sd) / det
        return (sd - slope * sl) / n, slope
    return solve(s.sum(0)), solve(counts @ s)


def split_half(per_unit: pd.DataFrame, subj_col: str, unit_col: str, val_col: str, rng):
    """Mean Spearman-Brown corrected split-half reliability of the per-subject mean of val_col,
    over random splits of units within each subject."""
    rs = []
    for _ in range(N_SPLITS):
        g = per_unit.assign(half=rng.integers(0, 2, len(per_unit)))
        m = g.groupby([subj_col, "half"])[val_col].mean().unstack("half").dropna()
        if len(m) < 5 or m[0].std() == 0 or m[1].std() == 0:
            continue
        r = np.corrcoef(m[0], m[1])[0, 1]
        rs.append(2 * r / (1 + r))
    return float(np.mean(rs)), len(rs)


# ---------------------------------------------------------------------------------
# part A
# ---------------------------------------------------------------------------------

def part_a(rng):
    d, pairs = cutin_pairs()
    subjects = np.sort(pairs.Exp_Subject_Id.unique())
    counts = boot_counts(len(subjects), N_BOOT, rng)
    L = ["## Part A -- the cut-in, second study", "",
         f"{len(subjects)} participants, {len(pairs)} first/second-showing pairs (participant x video), "
         f"filler trials excluded. Pairs by onset timepoint: "
         + ", ".join(f"{cp} {n}" for cp, n in pairs.cp.value_counts().sort_index().items()) + ".", "",
         "### A0 Reproduction of the number on file", ""]
    post = pairs[pairs.cp != "CP1"]
    (p0, p1, dd, _), _ = pair_summary(pair_stats(post, subjects), counts)
    L += [f"Post-onset pairs only, as `cutin2_scope.py` built them: {len(post)} pairs, {p0:.3f} -> {p1:.3f}, "
          f"difference {dd:+.3f} (`out/cutin2_scope.md`: 3 456 pairs, 0.547 -> 0.575, +0.027). That number "
          "is post-onset only; the pre-onset effect is new here.", "",
          "### A1 Where does repetition act?", "",
          "| onset | pairs | discordant (2nd yes / 1st yes) | P first | P second | difference [95% CI] | log OR [95% CI] |",
          "|---|---|---|---|---|---|---|"]
    res = {}
    groups = [(cp, pairs[pairs.cp == cp]) for cp in sorted(pairs.cp.unique())] + [("post-onset", post)]
    for name, sub in groups:
        S = pair_stats(sub, subjects)
        (p0, p1, dd, lor), (b0, b1, bd, blor) = pair_summary(S, counts)
        n10, n01 = S[:, 3].sum(), S[:, 4].sum()
        res[name] = {"diff": dd, "diff_ci": ci(bd), "lor": lor, "lor_boot": blor, "n10": n10, "n01": n01}
        L.append(f"| {name} | {int(S[:, 0].sum())} | {int(n10)} / {int(n01)} | {p0:.3f} | {p1:.3f} | "
                 f"{fmt_ci(dd, *ci(bd))} | {fmt_ci(lor, *ci(blor), nd=2)} |")
    contrast = res["CP1"]["lor"] - res["post-onset"]["lor"]
    c_lo, c_hi = ci(res["CP1"]["lor_boot"] - res["post-onset"]["lor_boot"])
    n_disc = res["CP1"]["n10"] + res["CP1"]["n01"]
    L += ["", f"Primary contrast, log OR(CP1) - log OR(post-onset): **{fmt_ci(contrast, c_lo, c_hi, nd=2)}**. "
          f"Discordant CP1 pairs: {int(n_disc)} (minimum for R1 to be identifiable: {MIN_DISCORDANT}).", ""]
    cp1_lo, cp1_hi = res["CP1"]["diff_ci"]
    po_lo, po_hi = res["post-onset"]["diff_ci"]
    cp1_rel_pos = cp1_lo > 0
    post_rel_pos = po_lo > 0
    if n_disc < MIN_DISCORDANT:
        verdict = "R1 UNIDENTIFIABLE (too few discordant CP1 pairs); the remaining readings are applied below"
    elif cp1_rel_pos and c_lo > 0:
        verdict = "R1 -- exposure acts on the GATE (learned anticipation)"
    else:
        verdict = None
    if verdict is None or verdict.startswith("R1 UNIDENTIFIABLE"):
        if post_rel_pos and not reliable(c_lo, c_hi):
            v2 = "R2 -- exposure acts UNIFORMLY (a criterion shift on the level or lapse)"
        elif post_rel_pos and not reliable(cp1_lo, cp1_hi) and c_hi < 0:
            v2 = "R3 -- exposure acts POST-ONSET ONLY"
        elif not reliable(cp1_lo, cp1_hi) and not reliable(po_lo, po_hi):
            v2 = "R4 -- NO RELIABLE EXPOSURE EFFECT"
        else:
            v2 = "MIXED, reported as found"
        verdict = v2 if verdict is None else verdict + "; " + v2
    L += [f"**A1 (pre-stated readings): {verdict}.**", ""]

    # A2
    L += ["### A2 Clip familiarity or general practice?", "",
          "Least squares d = a + g x lag, d = second minus first response, lag = distance between the showings "
          "as a fraction of the session.", "",
          "| pairs | median lag | a, effect at zero lag [95% CI] | g, per session [95% CI] |", "|---|---|---|---|"]
    a2 = {}
    for name, sub in (("CP1", pairs[pairs.cp == "CP1"]), ("post-onset", post)):
        (a, g), (ba, bg) = lag_regression(sub, subjects, counts)
        a2[name] = (a, ci(ba), g, ci(bg))
        L.append(f"| {name} | {sub.lag.median():.2f} | {fmt_ci(a, *ci(ba))} | {fmt_ci(g, *ci(bg))} |")
    a, (alo, ahi), g, (glo, ghi) = a2["post-onset"]
    reads = []
    if alo > 0:
        reads.append("clip-specific familiarity (a > 0)")
    if glo > 0:
        reads.append("general practice (g > 0)")
    if ghi < 0:
        reads.append("familiarity that decays with lag (g < 0)")
    L += ["", "**A2 (pre-stated readings, post-onset pairs): "
          + ("; ".join(reads) if reads else "neither familiarity nor practice is reliable") + ".**", ""]

    # A3
    per = post.assign(dd=post.y1 - post.y0)
    drv = per.groupby("Exp_Subject_Id").dd.mean()
    rel, n_ok = split_half(per, "Exp_Subject_Id", "video", "dd", rng)
    first = d[d.pass_idx == 0]
    f_post = first[first.CP != "CP1"].groupby("Exp_Subject_Id").CZB_1.mean()
    f_cp1 = first[first.CP == "CP1"].groupby("Exp_Subject_Id").CZB_1.mean()
    rho_post = spearmanr(drv, f_post.reindex(drv.index)).correlation
    rho_cp1 = spearmanr(drv, f_cp1.reindex(drv.index)).correlation
    L += ["### A3 Is it a per-driver property?", "",
          "| quantity | value |", "|---|---|",
          f"| per-driver repetition effect, post-onset: mean (sd across drivers) | {drv.mean():+.3f} ({drv.std():.3f}) |",
          f"| split-half reliability, Spearman-Brown, mean of {n_ok} splits | {rel:.3f} |",
          f"| Spearman with the driver's first-showing post-onset rate | {rho_post:+.3f} |",
          f"| Spearman with the driver's first-showing CP1 rate | {rho_cp1:+.3f} |", "",
          f"**A3 (pre-stated rule, reliability >= {REL_MIN}): "
          + ("a per-driver exposure parameter is supportable" if rel >= REL_MIN
             else "a population-level exposure term only; the per-driver effect is not reliable") + ".**", ""]

    # A4
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    st = pd.read_csv(OUT / "cutin2_gate_states.csv")[["video", "l0", "ldot"]]
    base = cells.drop(columns=["p", "n"]).merge(st, on="video")
    L += ["### A4 How big is it in model units? (card G.1's gated rule, refitted per showing)", "",
          "| showing | w | lapse | threshold c | sigma | m_lat [m] | s_l [m] | CP1 predicted | CP1 observed |",
          "|---|---|---|---|---|---|---|---|---|"]
    fits = {}
    two = d[d.pass_idx < 2]
    for k in (0, 1):
        agg = two[two.pass_idx == k].groupby("video").CZB_1.agg(p="mean", n="count").reset_index()
        c = base.merge(agg, on="video")
        po, c1 = c[c.cp != "CP1"].reset_index(drop=True), c[c.cp == "CP1"].reset_index(drop=True)
        u, v = G.axes(po)
        p = G.fit_gated(u, v, po.l0.to_numpy(float), po.ldot.to_numpy(float), po.p.to_numpy(float), po.n.to_numpy(float))
        u1, v1 = G.axes(c1)
        pred1 = G.predict_gated(p, u1, v1, c1.l0.to_numpy(float), c1.ldot.to_numpy(float))
        w = 1 / (1 + np.exp(-p[0]))
        fits[k] = (w, p)
        L.append(f"| {'first' if k == 0 else 'second'} | {w:.3f} | {1 / (1 + np.exp(-p[1])):.4f} | {p[2]:.3f} | "
                 f"{np.exp(p[3]):.3f} | {p[4]:.3f} | {np.exp(p[5]):.3f} | "
                 f"{np.average(pred1, weights=c1.n):.3f} | {np.average(c1.p, weights=c1.n):.3f} |")
    dc = fits[1][1][2] - fits[0][1][2]
    sig = 0.5 * (np.exp(fits[0][1][3]) + np.exp(fits[1][1][3]))
    L += ["", f"Shift in threshold, second minus first: {dc:+.3f} axis units ({dc / sig:+.2f} of the mean sigma); "
          "negative = responding at a less critical scene."]
    if all(0.45 <= fits[k][0] <= 0.55 for k in (0, 1)):
        L.append(f"Both weights lie in [0.45, 0.55], so this is {2 * dc:+.3f} in log looming rate, a factor of "
                 f"{np.exp(2 * dc):.2f} on the looming rate at which the median response occurs.")
    else:
        L.append("A fitted weight lies outside [0.45, 0.55]; the looming-rate conversion is not stated.")
    L.append("")
    return L, {"A1": verdict, "drv": drv}


# ---------------------------------------------------------------------------------
# part B
# ---------------------------------------------------------------------------------

def band_of(pet):
    for name, (lo, hi) in BANDS.items():
        if lo - 1e-9 <= pet <= hi + 1e-9:
            return name
    raise ValueError(pet)


def part_b(rng):
    r = ltap_trials()
    r["band"] = r.pet.map(band_of)
    subjects = np.sort(r.Exp_Subject_Id.unique())
    counts = boot_counts(len(subjects), N_BOOT, rng)
    L = ["## Part B -- the left turn across path, first study", "",
         f"{len(subjects)} participants, {len(r)} trials, 18 cells x 4 showings each (showings 1-2 in session 1, "
         f"3-4 in session 2). Replays on {100 * (r.Replay > 0).mean():.1f}% of trials.", "",
         "### B1 P(intervene) by showing and PET band", "",
         "| band | showing 1 | showing 2 | showing 3 | showing 4 | last - first [95% CI] | 2 - 1 | 3 - 2 (session boundary) | 4 - 3 |",
         "|---|---|---|---|---|---|---|---|---|"]

    def subj_sums(sub):
        s = sub.groupby(["Exp_Subject_Id", "show"]).intervene.agg(["sum", "count"]).unstack("show")
        return s.reindex(subjects).fillna(0.0)

    diffs = {}
    for band in list(BANDS) + ["all"]:
        sub = r if band == "all" else r[r.band == band]
        s = subj_sums(sub)
        ys, ns = s["sum"].to_numpy(), s["count"].to_numpy()
        p = ys.sum(0) / ns.sum(0)
        bp = (counts @ ys) / (counts @ ns)
        d_last = p[3] - p[0]
        diffs[band] = (d_last, ci(bp[:, 3] - bp[:, 0]))
        steps = [fmt_ci(p[k + 1] - p[k], *ci(bp[:, k + 1] - bp[:, k])) for k in range(3)]
        L.append(f"| {band} | " + " | ".join(f"{x:.3f}" for x in p) + f" | {fmt_ci(d_last, *ci(bp[:, 3] - bp[:, 0]))} | "
                 + " | ".join(steps) + " |")
    L.append("")

    # B2 distance rule per showing, with refit bootstrap for first vs last
    cells = ltap_cells(with_responses=False)[["pet", "speed_kph", "d_onc"]]
    key = ["pet", "speed_kph"]
    cell_index = cells.set_index(key).index
    x = -np.log(cells.d_onc.to_numpy(float))

    def per_subject_cell(show):
        s = (r[r.show == show].groupby(["Exp_Subject_Id"] + key).intervene.agg(["sum", "count"])
             .unstack(key))
        ys = s["sum"].reindex(columns=cell_index).reindex(subjects).fillna(0.0).to_numpy()
        ns = s["count"].reindex(columns=cell_index).reindex(subjects).fillna(0.0).to_numpy()
        return ys, ns

    def fit_cells(y, n):
        ok = n > 0
        return T.fit_reg(x[ok], y[ok] / n[ok], n[ok])

    L += ["### B2 The distance rule, refitted per showing", "",
          "| showing | lapse | boundary distance D* [m] | at 50 km/h [s] | at 70 km/h [s] | sigma (log distance) |",
          "|---|---|---|---|---|---|"]
    th = {}
    sc = {}
    for show in range(4):
        ys, ns = per_subject_cell(show)
        sc[show] = (ys, ns)
        t = fit_cells(ys.sum(0), ns.sum(0))
        th[show] = t
        dstar = float(np.exp(-t[1]))
        L.append(f"| {show + 1} | {1 / (1 + np.exp(-t[0])):.3f} | {dstar:.1f} | {dstar / (50 / 3.6):.2f} | "
                 f"{dstar / (70 / 3.6):.2f} | {np.exp(t[2]):.3f} |")
    lr_d = float(-(th[3][1] - th[0][1]))          # log(D*_last / D*_first)
    lr_s = float(th[3][2] - th[0][2])             # log(sigma_last / sigma_first)
    cb = counts[:N_BOOT_FIT]
    bd, bs = np.empty(N_BOOT_FIT), np.empty(N_BOOT_FIT)
    t0 = time.time()
    for b in range(N_BOOT_FIT):
        f0 = fit_cells(cb[b] @ sc[0][0], cb[b] @ sc[0][1])
        f3 = fit_cells(cb[b] @ sc[3][0], cb[b] @ sc[3][1])
        bd[b], bs[b] = -(f3[1] - f0[1]), f3[2] - f0[2]
        if b % 200 == 0:
            print(f"B2 bootstrap {b}/{N_BOOT_FIT} {time.time() - t0:.0f} s", flush=True)
    d_lo, d_hi = ci(bd)
    s_lo, s_hi = ci(bs)
    L += ["", f"Last against first showing: D* ratio **{np.exp(lr_d):.3f}** [{np.exp(d_lo):.3f}, {np.exp(d_hi):.3f}] "
          f"(above 1 = responding at a farther oncoming car); sigma ratio **{np.exp(lr_s):.3f}** "
          f"[{np.exp(s_lo):.3f}, {np.exp(s_hi):.3f}] (below 1 = sharper).", ""]

    far, (f_lo, f_hi) = diffs["far"]
    near, (n_lo, n_hi) = diffs["near"]
    band_rel = [reliable(*diffs[b][1]) for b in BANDS]
    band_sign = [np.sign(diffs[b][0]) for b in BANDS]
    if f_lo > 0:
        verdict = "L1 -- LEARNED ANTICIPATION"
    elif s_hi < 0 or (f_hi < 0 and not n_hi < 0):
        verdict = "L2 -- DISCRIMINATION LEARNING"
    elif all(band_rel) and len(set(band_sign)) == 1 and not reliable(s_lo, s_hi):
        verdict = "L3 -- A GENERAL CRITERION SHIFT"
    elif not any(band_rel) and not reliable(s_lo, s_hi):
        verdict = "L4 -- NONE"
    else:
        verdict = "MIXED, reported as found"
    L += [f"**B1-B2 (pre-stated readings): {verdict}.**", ""]

    # B3 familiarity or practice, within-session pairs
    rows = []
    for (s0, s1) in ((0, 1), (2, 3)):
        a = r[r.show == s0].set_index(["Exp_Subject_Id"] + key)
        b_ = r[r.show == s1].set_index(["Exp_Subject_Id"] + key)
        j = a[["intervene", "pos01"]].join(b_[["intervene", "pos01"]], rsuffix="_2").dropna()
        rows.append(pd.DataFrame({"Exp_Subject_Id": j.index.get_level_values(0), "y0": j.intervene.to_numpy(),
                                  "y1": j.intervene_2.to_numpy(), "lag": (j.pos01_2 - j.pos01).to_numpy()}))
    wp = pd.concat(rows, ignore_index=True)
    (a, g), (ba, bg) = lag_regression(wp, subjects, counts)
    L += ["### B3 Clip familiarity or practice (within-session pairs)", "",
          f"{len(wp)} pairs, median lag {wp.lag.median():.2f} of a session (negative lags occur where the second "
          "showing's position is earlier in its standardized session index, which cannot happen within one "
          f"session; minimum lag here {wp.lag.min():.2f}).", "",
          "| a, effect at zero lag [95% CI] | g, per session [95% CI] |", "|---|---|",
          f"| {fmt_ci(a, *ci(ba))} | {fmt_ci(g, *ci(bg))} |", ""]

    # B4 per-driver reliability
    early = r[r.show <= 1].groupby(["Exp_Subject_Id"] + key).intervene.mean()
    late = r[r.show >= 2].groupby(["Exp_Subject_Id"] + key).intervene.mean()
    pc = (late - early).rename("dd").reset_index()
    pc["cell"] = pc.pet.astype(str) + "_" + pc.speed_kph.astype(str)
    drv = pc.groupby("Exp_Subject_Id").dd.mean()
    rel, n_ok = split_half(pc, "Exp_Subject_Id", "cell", "dd", rng)
    L += ["### B4 Is it a per-driver property?", "",
          "| quantity | value |", "|---|---|",
          f"| per-driver change, showings 3-4 minus 1-2: mean (sd across drivers) | {drv.mean():+.3f} ({drv.std():.3f}) |",
          f"| split-half reliability, Spearman-Brown, mean of {n_ok} splits | {rel:.3f} |", "",
          f"**B4 (pre-stated rule, reliability >= {REL_MIN}): "
          + ("a per-driver exposure parameter is supportable" if rel >= REL_MIN
             else "a population-level exposure term only; the per-driver change is not reliable") + ".**", ""]
    return L, {"B": verdict, "drv": drv}


def main() -> None:
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    head = ["# Card EX.1 -- where does repeated exposure act, and is it a learned anticipation?", "",
            "Generated by `replication/czb/ex1_exposure_split.py`; questions, readings and rules pre-stated in its "
            "docstring before the run. Do not edit by hand.", "",
            f"Cluster bootstrap by participant, {N_BOOT} resamples ({N_BOOT_FIT} where a model is refitted), seed "
            f"{SEED}; 95% percentile intervals.", ""]
    LA, ra = part_a(rng)
    print("part A done", flush=True)
    LB, rb = part_b(rng)
    drv = pd.concat([ra["drv"].rename("cutin_post_onset_repetition_effect"),
                     rb["drv"].rename("ltap_late_minus_early")], axis=1)
    drv.index.name = "Exp_Subject_Id"
    drv.to_csv(OUT / "ex1_driver_exposure.csv")
    both = drv.dropna()
    tail = ["## Summary of the pre-stated readings", "",
            f"- Cut-in, where repetition acts (A1): {ra['A1']}.",
            f"- Left turn, what four showings do (B1-B2): {rb['B']}.",
            f"- Drivers with a value in both scenarios: {len(both)}"
            + (f"; Spearman between the two per-driver effects {spearmanr(both.iloc[:, 0], both.iloc[:, 1]).correlation:+.3f} "
               "(no verdict attached)." if len(both) >= 5 else " (fewer than five: no correlation)."), "",
            f"Runtime {(time.time() - t0) / 60:.1f} min."]
    text = "\n".join(head + LA + LB + tail)
    (OUT / "ex1_exposure_split.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
