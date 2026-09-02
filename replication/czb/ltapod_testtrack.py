"""The 2013 LTAP/OD test-track study against the video LTAP study: the same boundary model on
real turns (card TT.1, 2026-09-02).

THE PRE-REGISTRATION. Written before the run.

The data
--------
`external/02_LTAPOD_DBIN/DigitalRunProtocol_V2_121126resave_FULL.xlsx`, sheet
`InVehProtocols_795` (header on row 10): the run protocol of Bärgman, Smith & Werneke (2015,
TRF 35, `papers/comfort-zone-boundaries/`). Twenty-six participants (the paper reports 22 with
usable data), an instrumented Volvo V50 turning left across the path of a self-propelled
balloon car at a constant 50 km/h on the Vårgårda airfield, October 2013. Column meanings from
Jonas (2026-09-02): `ParticipantNumber`; `RunNumber` (sequential); `Training` = 1 → do not use;
`Broader_B_CZ` = 1 and `Finer_F_CZ` = 1 are the comfort-condition runs (preset SetPETs 4/3/2/1 s,
then the method-of-adjustment iterations), where drivers were asked to turn in front of the
balloon car when they felt safe; `DreadZone_DZ_F` = 1 are the hurried-condition runs (pushed
beyond the comfort boundary); `SetPET` is the manipulated post-encroachment time the
normative reference trajectory would produce; `TurnedBefore` / `TurnedAfter` are the Go / No-Go
decisions; `HowComfortable` and `HowRisky` (1..15) are self-reports after a Go; the
`IfTurn...` and `...After` items after a No-Go. Some SetPETs are negative on Go runs (drivers
accelerated, or the value is wrong): handled with care, see below. `Remove` = 1 flags runs the
experimenters repeated (35 rows; their comments say why) and is excluded in the primary
analysis. Old data, reused; the `Cognitive`, `WithOutBarrier`, `Stop` and `AutoBrake`
conditions are ignored here.

The comparison
--------------
The video LTAP study (study 1, Random design; `external/01_studies/...`, loaded with
`czb_data.load_joint`) shows the same manoeuvre on video at 50 and 70 km/h and asks "would you
intervene" (brake / yield) at a frozen moment; the test track asks the driver to actually
turn or wait. The mapping assumed here: **Go on the test track = not intervening on video**,
so P(intervene | PET) on video is compared with 1 − P(Go | SetPET) on the track, at 50 km/h.
Both are functions of PET (design PET on video; SetPET on the track); at a constant oncoming
speed PET, arrival time and distance are one axis, so this study cannot separate them (the
video study at two speeds can, card B.3.v2).

Model, both datasets, identical code path (`fit_stage1_looming.fit_hier_lapse_gated` with the
gate fixed at 1): per-driver level c_i = mu + sigma_pop z_i on x = −PET (larger = more
critical), P(intervene) = b_i + (1 − b_i) Φ((x − c_i)/sigma_resp), hierarchical lapse, 48-node
product quadrature, priors `priors_log_scale(x)` (centred on the covariate's median). The
population's median comfort boundary is then PET_50 = −mu: the PET at which half the drivers
switch from Go to No-Go. Standard errors by the Laplace route of the same function.

Tests, pre-stated
-----------------
T1  Comfort boundary, track vs video (50 km/h). PET_50 on the track (comfort runs) against
    PET_50 on video (43 drivers, 9 PET levels at 50 km/h). Rule: if the two agree within
    0.5 s (the video design's PET step), the video paradigm reproduces the test-track
    comfort boundary and the paradigm offset is reported as their difference with its SE;
    if not, the offset is the result, reported with its sign and SE. No margin games: the
    0.5 s is the design resolution.
T2  Between-driver spread. sigma_pop on the track against sigma_pop on video, same units
    (seconds of PET). Reported with SEs; no decision, because the two populations differ
    (22 Volvo/Autoliv employees, 2013; 43 crowdsourced participants, 2026).
T3  The dread boundary. The same fit on the hurried runs; PET_50(dread) / PET_50(comfort)
    against the paper's 0.69 (observed PET at the last Go). Reported; no decision.
T4  The graded signal. HowComfortable (1 = very comfortable .. 15 = very uncomfortable) on track
    Go runs against the video's PS rating (0..10; in the joint file higher = LESS safe: 8.2 at
    PET 0, 3.5 at PET 4) at 50 km/h, each z-scored within its dataset and regressed on PET
    with driver-clustered SEs. Both ratings therefore rise with discomfort, so both slopes
    should be negative. Reported: the two slopes per second of PET and whether their 95%
    intervals overlap. Descriptive.
T5  Replication of the paper's own statistics from the protocol (the project's rule when a
    published result is reused): per driver, in run order, the last Go and the last No-Go of
    each condition bracket the switch; the paper's boundary is the observed PET at the last Go
    (medians 2.26 s comfortable, 1.50 s hurried, ratio 0.69 on 20 drivers). Reported: the
    same medians here, on observed PET and on SetPET, and the bracket midpoint on SetPET as a
    model-free per-driver threshold, with the dread/comfort ratio of the midpoints.
T4b The rating comparison in T4 uses Go runs only, which selects the turns drivers were
    willing to make; the video rates every clip. So T4b repeats T4 with a rating on every
    track run: HowComfortable after a Go, IfTurnHowComfortable after a No-Go ("if you had
    turned, how comfortable would you have been"), the closest the track comes to the
    video's question. Descriptive, added after the first run showed T4's selection problem.
Sensitivities: (a) include the `Remove` = 1 runs; (b) exclude SetPET < 0; (c) the observed
PET column in place of SetPET on Go runs (No-Go runs have no observed PET, so (c) can only
be a check of how far drivers departed from the reference trajectory).

Run: python replication/czb/ltapod_testtrack.py     Output: out/ltapod_testtrack.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))
import fit_stage1_looming as F                   # noqa: E402  (the hierarchical fit)
from comfortzone.czb_data import load_joint      # noqa: E402

XLSX = REPO / "external/02_LTAPOD_DBIN/DigitalRunProtocol_V2_121126resave_FULL.xlsx"
OUT = HERE / "out"


def load_track() -> pd.DataFrame:
    d = pd.read_excel(XLSX, sheet_name="InVehProtocols_795", header=9)
    d = d.loc[:, ~d.columns.astype(str).str.startswith("Unnamed")]
    d = d[d.ParticipantNumber.notna()].copy()
    d = d[d.Training != 1]
    d["cond"] = np.where(d.DreadZone_DZ_F == 1, "dread",
                         np.where((d.Broader_B_CZ == 1) | (d.Finer_F_CZ == 1), "comfort", "other"))
    d = d[d.cond.isin(["comfort", "dread"]) & d.SetPET.notna() & d.TurnedBefore.notna()].copy()
    d["go"] = d.TurnedBefore.astype(int)
    d["removed"] = d.Remove == 1
    return d


def fit_threshold(pet: np.ndarray, intervene: np.ndarray, driver: np.ndarray) -> dict:
    """Hierarchical per-driver level on x = -PET, gate = 1. Returns PET_50 = -mu and the rest."""
    x = -pet.astype(float)
    codes, _ = pd.factorize(driver)
    pr = F.priors_log_scale(x)
    f = F.fit_hier_lapse_gated(x, np.ones_like(x), intervene.astype(float), codes, pr)
    f["pet50"], f["se_pet50"] = -f["mu"], f["se_mu"]
    f["n_drivers"], f["n_trials"] = int(codes.max() + 1), len(x)
    return f


def slope_clustered(x, y, cluster):
    """OLS slope of z-scored y on x with cluster-robust SE (drivers)."""
    z = (y - y.mean()) / y.std()
    X = np.column_stack([np.ones_like(x), x])
    beta = np.linalg.lstsq(X, z, rcond=None)[0]
    res = z - X @ beta
    XtX_inv = np.linalg.inv(X.T @ X)
    meat = np.zeros((2, 2))
    for c in np.unique(cluster):
        m = cluster == c
        u = X[m].T @ res[m]
        meat += np.outer(u, u)
    V = XtX_inv @ meat @ XtX_inv
    return float(beta[1]), float(np.sqrt(V[1, 1]))


def fmt(f):
    return (f"PET_50 {f['pet50']:.2f} s (SE {f['se_pet50']:.2f}); sigma_pop {f['sigma_pop']:.2f} s "
            f"(SE {f['se_sigma_pop']:.2f}); sigma_resp {f['sigma_resp']:.2f} s; lapse {f['b']:.3f} "
            f"(sd {f['sigma_b']:.2f}); drivers {f['n_drivers']}, trials {f['n_trials']}; SEs {'ok' if f['se_ok'] else 'NOT ok'}")


def main() -> None:
    d = load_track()
    j = load_joint()
    v = j[(j.design == "Random") & (j.scenario == "ltap") & (j.ltap_speed == 50) & j.intervene.notna()].copy()
    v["pet"] = v.criticality_label.str.replace("PET", "").astype(float)

    L = ["# The 2013 LTAP/OD test-track study against the video LTAP study (card TT.1)", "",
         "Generated by `replication/czb/ltapod_testtrack.py`; data handling, model and tests pre-stated in"
         " its docstring. Do not edit by hand.", ""]

    # --- 0 the data ------------------------------------------------------------------
    prim = d[~d.removed]
    L += ["## 0 The runs used", "",
          "| condition | runs (primary) | of which Go | drivers | runs flagged Remove | SetPET range | SetPET < 0 (Go) |",
          "|---|---|---|---|---|---|---|"]
    for c in ("comfort", "dread"):
        s = prim[prim.cond == c]; r = d[(d.cond == c) & d.removed]
        L.append(f"| {c} | {len(s)} | {int(s.go.sum())} | {s.ParticipantNumber.nunique()} | {len(r)} | "
                 f"{s.SetPET.min():.1f} to {s.SetPET.max():.1f} s | {int((s.SetPET < 0).sum())} ({int(s[s.SetPET < 0].go.sum())}) |")
    L += ["", f"Video LTAP at 50 km/h: {len(v)} trials, {v.Exp_Subject_Id.nunique()} drivers, PET levels "
          f"{sorted(v.pet.unique())}.", ""]

    # --- 1 the Go / intervene curves, cell means -----------------------------------------
    L += ["## 1 What the two paradigms show, model-free", "",
          "Track: share of Go decisions per SetPET (comfort runs, primary). Video: share who would intervene per design PET, "
          "and its complement.", "",
          "| SetPET / PET [s] | track P(Go) (n) | video 1 − P(intervene) (n) |", "|---|---|---|"]
    vt = v.groupby("pet").intervene.agg(["mean", "count"])
    ct = prim[prim.cond == "comfort"].groupby("SetPET").go.agg(["mean", "count"])
    levels = sorted(set(ct.index.round(1)) | set(vt.index))
    for lv in levels:
        a = ct.loc[[i for i in ct.index if round(i, 1) == lv]]
        b = vt.loc[[lv]] if lv in vt.index else None
        sa = f"{a['mean'].mean():.2f} ({int(a['count'].sum())})" if len(a) else "–"
        sb = f"{1 - b['mean'].iloc[0]:.2f} ({int(b['count'].iloc[0])})" if b is not None else "–"
        L.append(f"| {lv:.1f} | {sa} | {sb} |")
    L.append("")

    # --- 2 the fits ------------------------------------------------------------------------
    fits = {}
    s = prim[prim.cond == "comfort"]
    fits["track comfort"] = fit_threshold(s.SetPET.to_numpy(), 1 - s.go.to_numpy(), s.ParticipantNumber.to_numpy())
    fits["video 50 km/h"] = fit_threshold(v.pet.to_numpy(), v.intervene.to_numpy(), v.Exp_Subject_Id.to_numpy())
    s2 = prim[prim.cond == "dread"]
    fits["track dread"] = fit_threshold(s2.SetPET.to_numpy(), 1 - s2.go.to_numpy(), s2.ParticipantNumber.to_numpy())
    # sensitivities
    sa = d[d.cond == "comfort"]
    fits["track comfort, Remove runs included"] = fit_threshold(sa.SetPET.to_numpy(), 1 - sa.go.to_numpy(), sa.ParticipantNumber.to_numpy())
    sb = s[s.SetPET >= 0]
    fits["track comfort, SetPET >= 0 only"] = fit_threshold(sb.SetPET.to_numpy(), 1 - sb.go.to_numpy(), sb.ParticipantNumber.to_numpy())
    L += ["## 2 The same hierarchical threshold model on both paradigms", "",
          "Level c_i = mu + sigma_pop z_i on x = −PET; P(intervene) = b_i + (1 − b_i) Φ((x − c_i)/sigma_resp); "
          "PET_50 = −mu is the PET at which the median driver switches. Track responses are 1 − Go.", "",
          "| fit | result |", "|---|---|"]
    for k, f in fits.items():
        L.append(f"| {k} | {fmt(f)} |")
    L.append("")

    # --- T1 --------------------------------------------------------------------------------
    ft, fv = fits["track comfort"], fits["video 50 km/h"]
    diff = fv["pet50"] - ft["pet50"]
    se = float(np.sqrt(fv["se_pet50"] ** 2 + ft["se_pet50"] ** 2))
    verdict = ("the video paradigm REPRODUCES the test-track comfort boundary within the design resolution"
               if abs(diff) <= 0.5 else
               f"the video paradigm places the boundary {'LATER (shorter PET)' if diff < 0 else 'EARLIER (longer PET)'} than the test track")
    L += ["## T1 The comfort boundary: video against test track (50 km/h)", "",
          f"PET_50 track {ft['pet50']:.2f} s (SE {ft['se_pet50']:.2f}); PET_50 video {fv['pet50']:.2f} s (SE {fv['se_pet50']:.2f}); "
          f"video minus track {diff:+.2f} s (SE {se:.2f}).", "",
          f"**Pre-stated reading:** {verdict}. The paper's own comfort boundary, the observed PET at each driver's last Go, "
          f"had median 2.26 s (mean 2.22) on 20 drivers.", ""]
    # --- T2 --------------------------------------------------------------------------------
    L += ["## T2 Between-driver spread", "",
          f"sigma_pop track {ft['sigma_pop']:.2f} s (SE {ft['se_sigma_pop']:.2f}); video {fv['sigma_pop']:.2f} s "
          f"(SE {fv['se_sigma_pop']:.2f}). Within-driver spread sigma_resp: track {ft['sigma_resp']:.2f} s, video "
          f"{fv['sigma_resp']:.2f} s. Reported without a decision (different populations and paradigms).", ""]
    # --- T3 --------------------------------------------------------------------------------
    fd = fits["track dread"]
    ratio = fd["pet50"] / ft["pet50"] if ft["pet50"] > 0 else float("nan")
    L += ["## T3 The dread boundary (hurried runs)", "",
          f"PET_50 dread {fd['pet50']:.2f} s (SE {fd['se_pet50']:.2f}); ratio dread / comfort {ratio:.2f} against the paper's 0.69 "
          f"(observed PET at the last Go, medians 1.50 / 2.26 s). sigma_pop dread {fd['sigma_pop']:.2f} s.", ""]
    # --- T4 --------------------------------------------------------------------------------
    g = s[(s.go == 1) & s.HowComfortable.notna()]
    bt, set_ = slope_clustered(g.SetPET.to_numpy(float), g.HowComfortable.to_numpy(float), g.ParticipantNumber.to_numpy())
    vv = v[v.PS.notna()]
    bv, sev = slope_clustered(vv.pet.to_numpy(float), vv.PS.to_numpy(float), vv.Exp_Subject_Id.to_numpy())
    L += ["## T4 The graded signal: comfort rating (track, Go runs) and perceived safety (video)", "",
          "Ratings z-scored within dataset; slope per second of PET with driver-clustered SEs. On the track 1 = very comfortable and "
          "15 = very uncomfortable; on video PS is 0..10 with higher = less safe (8.2 at PET 0, 3.5 at PET 4). In both, a NEGATIVE "
          "slope means the situation feels better at longer PET, so the two slopes are directly comparable.", "",
          f"| dataset | n | slope of z-rating per s of PET | SE | 95% |", "|---|---|---|---|---|",
          f"| track HowComfortable (Go runs) | {len(g)} | {bt:+.3f} | {set_:.3f} | {bt - 1.96 * set_:+.2f} to {bt + 1.96 * set_:+.2f} |",
          f"| video PS (50 km/h) | {len(vv)} | {bv:+.3f} | {sev:.3f} | {bv - 1.96 * sev:+.2f} to {bv + 1.96 * sev:+.2f} |",
          "", f"Track {bt:+.2f} z per s, video {bv:+.2f} z per s; the 95% intervals "
          f"{'overlap' if (bt - 1.96 * set_ <= bv + 1.96 * sev) and (bv - 1.96 * sev <= bt + 1.96 * set_) else 'do not overlap'}.", ""]
    # --- T4b: a rating on every run --------------------------------------------------------
    s_all = s.copy()
    s_all["rating"] = np.where(s_all.go == 1, s_all.HowComfortable, s_all.IfTurnHowComfortable)
    ga = s_all[s_all.rating.notna()]
    bta, seta = slope_clustered(ga.SetPET.to_numpy(float), ga.rating.to_numpy(float), ga.ParticipantNumber.to_numpy())
    L += ["## T4b The graded signal on every track run (HowComfortable after a Go, IfTurnHowComfortable after a No-Go)", "",
          f"| dataset | n | slope of z-rating per s of PET | SE | 95% |", "|---|---|---|---|---|",
          f"| track, all comfort runs | {len(ga)} | {bta:+.3f} | {seta:.3f} | {bta - 1.96 * seta:+.2f} to {bta + 1.96 * seta:+.2f} |",
          f"| video PS (50 km/h) | {len(vv)} | {bv:+.3f} | {sev:.3f} | {bv - 1.96 * sev:+.2f} to {bv + 1.96 * sev:+.2f} |",
          "", f"With every run rated, the intervals {'overlap' if (bta - 1.96 * seta <= bv + 1.96 * sev) and (bv - 1.96 * sev <= bta + 1.96 * seta) else 'do not overlap'}. "
          "T4 (Go runs only) conditions on the driver having judged the turn acceptable, which removes most of the PET dependence by selection.", ""]

    # --- T5: the paper's own statistics from the protocol -----------------------------------
    L += ["## T5 Replication of the paper's boundary statistics from the protocol", "",
          "Per driver and condition, runs in `RunNumber` order; the last Go and the last No-Go bracket the switch. The paper's boundary is the "
          "observed PET at the last Go. The bracket midpoint on SetPET is a model-free per-driver threshold.", "",
          "| condition | drivers with a bracket | median observed PET at last Go (paper) | median SetPET at last Go | median bracket midpoint (SetPET) | mean midpoint (SD) |",
          "|---|---|---|---|---|---|"]
    mids = {}
    paper = {"comfort": "2.26 (mean 2.22), n = 20", "dread": "1.50 (mean 1.47), n = 20"}
    for c in ("comfort", "dread"):
        rows = []
        for pid, gdr in prim[prim.cond == c].sort_values("RunNumber").groupby("ParticipantNumber"):
            go_runs, nogo_runs = gdr[gdr.go == 1], gdr[gdr.go == 0]
            if len(go_runs) and len(nogo_runs):
                lg, ln = go_runs.iloc[-1], nogo_runs.iloc[-1]
                rows.append(dict(pid=pid, pet_lastgo=lg.PET, set_lastgo=lg.SetPET, mid=0.5 * (lg.SetPET + ln.SetPET)))
        b = pd.DataFrame(rows); mids[c] = b
        L.append(f"| {c} | {len(b)} | {b.pet_lastgo.median():.2f} s (paper {paper[c]}) | {b.set_lastgo.median():.2f} s | "
                 f"{b.mid.median():.2f} s | {b.mid.mean():.2f} ({b.mid.std():.2f}) |")
    both = mids["comfort"].merge(mids["dread"], on="pid", suffixes=("_c", "_d"))
    L += ["", f"Dread / comfort on the bracket midpoints (SetPET), {len(both)} drivers with both: median ratio "
          f"{(both.mid_d / both.mid_c).median():.2f}; on observed PET at the last Go: {(both.pet_lastgo_d / both.pet_lastgo_c).median():.2f} "
          f"(paper: 0.69 from the regression, medians 1.50 / 2.26). Every driver shorter when hurried on the midpoints: "
          f"{int((both.mid_d < both.mid_c).sum())} of {len(both)}.", ""]

    # --- T6: transfer with nothing refitted --------------------------------------------------
    # (added 2026-09-02 after Jonas asked how the video parameters work on the track; pre-stated
    # here before running: the population curve of one dataset's fit is scored on the other's
    # cells against chance and against that dataset's own fit; a transfer within 0.02 wRMSE of
    # the own fit is "carries over", within 0.05 "carries over with an offset", else "does not".)
    def pop_curve(f, x):
        zz, ww = F._gh_nodes(48)
        z1 = np.repeat(zz, 48); z2 = np.tile(zz, 48); lw = np.outer(ww, ww).ravel()
        c = f["mu"] + f["sigma_pop"] * z1
        b = 1.0 / (1.0 + np.exp(-(f["phi"][3] + f["sigma_b"] * z2)))
        from scipy.stats import norm as _n
        P = b[None, :] + (1 - b[None, :]) * _n.cdf((x[:, None] - c[None, :]) / f["sigma_resp"])
        return (P * lw[None, :]).sum(axis=1) / lw.sum()

    def cells_of(pet, resp, weights=None):
        t = pd.DataFrame({"pet": np.round(pet, 1), "y": resp})
        g = t.groupby("pet").y.agg(["mean", "count"]).reset_index()
        return g.pet.to_numpy(float), g["mean"].to_numpy(float), g["count"].to_numpy(float)

    def wr(y, p, w):
        return float(np.sqrt(np.average((p - y) ** 2, weights=w)))

    track_pet, track_y, track_n = cells_of(s.SetPET.to_numpy(), 1 - s.go.to_numpy())
    video_pet, video_y, video_n = cells_of(v.pet.to_numpy(), v.intervene.to_numpy())
    rows = []
    for name, (pet, yy, nn) in (("track cells", (track_pet, track_y, track_n)), ("video cells", (video_pet, video_y, video_n))):
        own = ft if name.startswith("track") else fv
        other = fv if name.startswith("track") else ft
        chance = wr(yy, np.full_like(yy, np.average(yy, weights=nn)), nn)
        rows.append((name, chance, wr(yy, pop_curve(own, -pet), nn), wr(yy, pop_curve(other, -pet), nn)))
    # the sampling-noise floor of each cell set, from the own fit's predicted rate (many track cells
    # hold one to five runs, where the observed 0/1 mean would give a floor of zero)
    floors = {}
    for name, (pet, yy, nn), own in (("track cells", (track_pet, track_y, track_n), ft), ("video cells", (video_pet, video_y, video_n), fv)):
        ph = np.clip(pop_curve(own, -pet), 1e-6, 1 - 1e-6)
        floors[name] = float(np.sqrt(np.average(ph * (1 - ph) / nn, weights=nn)))
    L += ["## T6 Transfer with nothing refitted: one paradigm's fitted population applied to the other", "",
          "The population curve (driver effects integrated out) of each fit, scored on the other dataset's cell means "
          "(weighted RMSE, weights = trials per cell) against chance, that dataset's own fit, and the sampling-noise floor of "
          "its cells (from the own fit's predicted rate; the track's cells hold 1 to 32 runs, so its floor is high).", "",
          "| scored on | chance | own fit (in sample) | the OTHER paradigm's fit, nothing refitted | noise floor |", "|---|---|---|---|---|"]
    for name, ch, own_e, oth_e in rows:
        L.append(f"| {name} | {ch:.3f} | {own_e:.3f} | {oth_e:.3f} | {floors[name]:.3f} |")
    t_ch, t_own, t_oth = rows[0][1:]
    vt = "carries over" if t_oth - t_own <= 0.02 else "carries over with an offset" if t_oth - t_own <= 0.05 else "does not carry over"
    L += ["", f"**Video → track:** the video-fitted population predicts the track's Go/No-Go cells at {t_oth:.3f} against the track's own "
          f"fit {t_own:.3f} and chance {t_ch:.3f}: **the video model {vt}** (pre-stated margins 0.02 / 0.05). "
          f"Track → video: {rows[1][3]:.3f} against the video's own {rows[1][2]:.3f} and chance {rows[1][1]:.3f}.", ""]

    # --- T7: the track model's own held-out performance and per-driver reliability ----------
    # (pre-stated here: LOPO over 13 evenly spaced drivers with fit_stage1_looming.lopo_loglik_gated;
    # the per-driver posterior-mean level against the model-free bracket midpoint of T5, Pearson r.)
    x_t = -s.SetPET.to_numpy(float); y_t = (1 - s.go.to_numpy()).astype(float)
    codes_t, uniq_t = pd.factorize(s.ParticipantNumber.to_numpy())
    pr_t = F.priors_log_scale(x_t)
    folds = list(np.linspace(0, codes_t.max(), 13).astype(int))
    lopo = F.lopo_loglik_gated(x_t, np.ones_like(x_t), y_t, codes_t, pr_t, folds)
    n_lopo = int(np.isin(codes_t, folds).sum())
    # chance log-lik on the same held-out trials: the training mean
    ll_chance = 0.0
    for fdr in folds:
        m = codes_t == fdr; pbar = float(np.clip(y_t[~m].mean(), 1e-6, 1 - 1e-6))
        ll_chance += float((y_t[m] * np.log(pbar) + (1 - y_t[m]) * np.log(1 - pbar)).sum())
    # per-driver posterior mean level
    zz, ww = F._gh_nodes(48); z1 = np.repeat(zz, 48); z2 = np.tile(zz, 48); lw = np.log(np.outer(ww, ww).ravel())
    from scipy.stats import norm as _n
    c_nodes = ft["mu"] + ft["sigma_pop"] * z1
    b_nodes = 1.0 / (1.0 + np.exp(-(ft["phi"][3] + ft["sigma_b"] * z2)))
    lev = {}
    for k, pid in enumerate(uniq_t):
        m = codes_t == k
        P = b_nodes[None, :] + (1 - b_nodes[None, :]) * _n.cdf((x_t[m][:, None] - c_nodes[None, :]) / ft["sigma_resp"])
        P = np.clip(P, 1e-12, 1 - 1e-12)
        ll = (y_t[m][:, None] * np.log(P) + (1 - y_t[m][:, None]) * np.log(1 - P)).sum(axis=0) + lw
        wgt = np.exp(ll - ll.max()); wgt /= wgt.sum()
        lev[pid] = -float((wgt * c_nodes).sum())        # PET units
    mids_c = mids["comfort"].set_index("pid")
    common = [p for p in mids_c.index if p in lev]
    a = np.array([lev[p] for p in common]); bmid = mids_c.loc[common, "mid"].to_numpy(float); bpet = mids_c.loc[common, "pet_lastgo"].to_numpy(float)
    r_mid = float(np.corrcoef(a, bmid)[0, 1])
    ok = np.isfinite(bpet); r_pet = float(np.corrcoef(a[ok], bpet[ok])[0, 1]); n_pet = int(ok.sum())
    L += ["## T7 The track model on its own terms: held-out drivers and per-driver reliability", "",
          f"Leave-one-driver-out over {len(folds)} drivers ({n_lopo} held-out runs): log-likelihood {lopo:.1f} against chance "
          f"{ll_chance:.1f} (the training mean), i.e. {(lopo - ll_chance) / n_lopo:+.3f} per held-out run.", "",
          f"Per-driver level (posterior mean, PET units) against the model-free bracket midpoint on SetPET (T5): Pearson r = {r_mid:.2f} "
          f"over {len(common)} drivers; against the observed PET at the last Go (the paper's boundary): r = {r_pet:.2f} over the {n_pet} drivers with a PET. "
          f"Range of per-driver levels {a.min():.2f} to {a.max():.2f} s (median {np.median(a):.2f}).", ""]

    # --- observed PET vs SetPET -------------------------------------------------------------
    go = prim[(prim.go == 1) & prim.PET.notna()]
    L += ["## 3 Observed PET against SetPET on Go runs (how far drivers left the reference trajectory)", "",
          "| condition | Go runs with observed PET | median PET − SetPET [s] | IQR | corr(SetPET, PET) |", "|---|---|---|---|---|"]
    for c in ("comfort", "dread"):
        gg = go[go.cond == c]; dd = gg.PET - gg.SetPET
        L.append(f"| {c} | {len(gg)} | {dd.median():+.2f} | {dd.quantile(.25):+.2f} to {dd.quantile(.75):+.2f} | "
                 f"{gg[['SetPET', 'PET']].corr().iloc[0, 1]:+.2f} |")
    L += ["", "A negative median means drivers turned more slowly than the reference (a smaller realized PET); a positive one "
          "that they accelerated. SetPET remains the stimulus in every fit above, as design PET is on video.", ""]
    (OUT / "ltapod_testtrack.md").write_text("\n".join(L), encoding="utf-8")
    prim.to_csv(OUT / "ltapod_runs.csv", index=False)
    print("\n".join(L))


if __name__ == "__main__":
    main()
