"""
Card NC.1 -- real left turns across oncoming traffic in inD: where is the boundary, does it match
the video and the test track, and does the cut-in's looming level carry to it?

THE PRE-REGISTRATION. Written 2026-09-25, before any inD left turn was scored.

WHERE THE CARD COMES FROM. `docs/naturalistic_data_plan.md` §3, NC.1 (the recommended first
comfort-zone test on naturalistic data); Jonas, 2026-09-25: "can we run LTAP/OD? Possibly with real
data?" The video left turn at 50 km/h has PET_50 = 2.42 s at first exposure (card EX.2; 2.18
pooled) and the test track 2.45 s (card TT.1): the PET at which half the drivers would not accept
the turn.

WHAT IS COMPUTED (inD v1.1, all 33 recordings; cars, vans, trucks and buses; positions in metres,
heading in degrees counter-clockwise, so a left turn is a heading change of about +90 degrees):
  TURNERS: net unwrapped heading change between +60 and +120 degrees.
  ONCOMING: tracks whose net heading change is within 20 degrees of zero and whose initial heading
    differs from the turner's initial heading by 150 to 210 degrees, overlapping it in time.
  CONFLICT: the closest approach in SPACE between the two paths (every other frame), kept if under
    2.0 m; the conflict point is the turner's point there. t_T and t_O: the times each passes it.
    Pairs with |t_O - t_T| > 15 s are not interactions and are dropped.
  THE DECISION MOMENT: the turner 10 m (path length) before the conflict point. At that moment the
    oncoming vehicle's path distance to the conflict point D_O, its speed v_O (> 1 m/s), its
    time to arrival TTA_O = D_O / v_O, and its looming for the turner, theta_dot = W_O x
    (closing rate of the Euclidean distance) / distance^2 (card EL.1b's form). Pairs where the
    oncoming has already passed the conflict point at that moment are not gap decisions and are
    dropped. OUTCOME: accepted (the turner passes the conflict point first).
  THE BOUNDARY: P(accept | x) = Phi((x - c)/s) by maximum likelihood on x = log TTA_O (primary),
    log D_O and log theta_dot; 95% intervals by a bootstrap over recordings (200). PET-EQUIVALENT
    of the TTA boundary: TTA_50 minus the median time the ACCEPTING turners take from the decision
    moment to the conflict point (a PET is measured from the turner's clearing, the TTA from the
    decision); reported with the accepted crossings' own PET distribution.

THE RULES.
  (1) The video/track boundary is REPRODUCED on real turns if the PET-equivalent boundary lies
      within 0.5 s of 2.42 s (the video at first exposure; the track is 2.45 s).
  (2) The cut-in's looming level CARRIES if the left turn's 50% looming level lies within a factor
      of 2 of the cut-in intervention level 0.032 rad/s (card JJ.10) -- the population-level form of
      "one driver's prior carried to another scenario"; the per-driver form is not possible on inD.
  Rule 0: at least 100 gap decisions with at least 20 of each outcome, else DESCRIPTIVE ONLY.

PREDICTIONS. A few hundred gap decisions, mostly at one or two of the four locations. TTA_50 about
4 to 5 s; PET-equivalent about 2.5 to 3.5 s, so REPRODUCED or narrowly not (real drivers accepting
somewhat more conservatively than a video judgment says). Looming: NOT CARRIED -- the oncoming car
is approached at an angle and the task differs; I expect a level several times the cut-in's.

Output: replication/czb/out/nc1_ind_left_turns.md (aggregates only)
Run:    python replication/czb/nc1_ind_left_turns.py
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
from scipy.spatial import cKDTree
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
IND = Path(r"C:\JonasLocal\D_Data\inD-dataset-v1.1\data")
CACHE = Path(r"C:\JonasLocal\D_Data_derived\nc1_pairs.pkl")
OUT = HERE / "out"
FPS = 25
D_DEC, D_CONF, MAX_DT = 10.0, 2.0, 15.0
VIDEO_PET50, TRACK_PET50, CUTIN_LEVEL = 2.42, 2.45, 0.032
VEH = {"car", "van", "truck_bus", "truck", "bus"}


def unwrap_deg(h):
    return np.degrees(np.unwrap(np.radians(h)))


def process(rec: int):
    tr = pd.read_csv(IND / f"{rec:02d}_tracks.csv",
                     usecols=["trackId", "frame", "xCenter", "yCenter", "heading", "width", "lonVelocity"])
    meta = pd.read_csv(IND / f"{rec:02d}_tracksMeta.csv", usecols=["trackId", "class"])
    loc = int(pd.read_csv(IND / f"{rec:02d}_recordingMeta.csv").locationId.iloc[0])
    tr = tr.merge(meta, on="trackId")
    tr = tr[tr["class"].isin(VEH)]
    T = {}
    for k, g in tr.groupby("trackId"):
        g = g.sort_values("frame")
        h = unwrap_deg(g.heading.to_numpy())
        xy = g[["xCenter", "yCenter"]].to_numpy()
        s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(xy, axis=0).T))])
        T[k] = {"f": g.frame.to_numpy(), "xy": xy, "h0": h[:10].mean(), "dh": h[-10:].mean() - h[:10].mean(),
                "s": s, "v": np.abs(g.lonVelocity.to_numpy()), "w": float(g.width.iloc[0])}
    turners = [k for k, t in T.items() if 60 <= t["dh"] <= 120 and len(t["f"]) > 50]
    straight = [k for k, t in T.items() if abs(t["dh"]) <= 20 and len(t["f"]) > 50]
    rows = []
    for a in turners:
        A = T[a]
        for b in straight:
            B = T[b]
            dh0 = (B["h0"] - A["h0"]) % 360
            if not 150 <= dh0 <= 210:
                continue
            if B["f"][0] > A["f"][-1] or B["f"][-1] < A["f"][0]:
                continue
            tree = cKDTree(B["xy"][::2])
            dist, j = tree.query(A["xy"][::2])
            ia = int(np.argmin(dist)) * 2
            if dist.min() > D_CONF:
                continue
            ib = int(j[ia // 2]) * 2
            tA, tB = A["f"][ia] / FPS, B["f"][ib] / FPS
            if abs(tB - tA) > MAX_DT:
                continue
            dec = np.flatnonzero(A["s"][ia] - A["s"][:ia + 1] <= D_DEC)
            if len(dec) == 0 or A["s"][ia] - A["s"][0] < D_DEC:
                continue
            kd = int(dec[0])
            fd = A["f"][kd]
            mb = np.searchsorted(B["f"], fd)
            if mb >= len(B["f"]) or B["f"][mb] != fd or mb + 1 >= len(B["f"]):
                continue
            D_O = B["s"][ib] - B["s"][mb]
            v_O = B["v"][mb]
            if D_O <= 0 or v_O <= 1.0:
                continue
            d_now = np.hypot(*(B["xy"][mb] - A["xy"][kd]))
            d_next = np.hypot(*(B["xy"][mb + 1] - A["xy"][min(kd + 1, len(A["f"]) - 1)]))
            closing = (d_now - d_next) * FPS
            rows.append({"rec": rec, "loc": loc, "turner": a, "tta": D_O / v_O, "D_O": D_O, "v_O": v_O,
                         "loom": B["w"] * closing / d_now ** 2 if closing > 0 else np.nan,
                         "accepted": bool(tA < tB), "pet": tB - tA, "t_to_conf": tA - fd / FPS})
    return rows


def fit(x, y):
    def nll(th):
        p = np.clip(norm.cdf((x - th[0]) / np.exp(th[1])), 1e-9, 1 - 1e-9)
        return -float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))
    return minimize(nll, np.array([np.median(x), 0.0]), method="L-BFGS-B").x


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    if CACHE.exists():
        d = pd.read_pickle(CACHE)
    else:
        recs = sorted(int(p.name[:2]) for p in IND.glob("*_tracks.csv"))
        with ProcessPoolExecutor(max_workers=12) as ex:
            d = pd.DataFrame([r for rr in ex.map(process, recs) for r in rr])
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        d.to_pickle(CACHE)
    y = d.accepted.to_numpy(float)
    L = ["# Card NC.1 -- real left turns across oncoming traffic (inD)", "",
         "Generated by `replication/czb/nc1_ind_left_turns.py`; pre-stated in its docstring before the"
         " run. Aggregates only (inD licence). Do not edit by hand.", "",
         f"Gap decisions (turner 10 m before the conflict point, oncoming not yet past it): **{len(d):,}**,"
         f" {int(y.sum())} accepted, {int(len(y) - y.sum())} rejected; {d.turner.nunique()} turning"
         f" vehicles; by location: {d.groupby('loc').size().to_dict()}.", ""]
    if len(d) < 100 or y.sum() < 20 or (len(y) - y.sum()) < 20:
        L += ["**Rule 0: DESCRIPTIVE ONLY** (fewer than 100 decisions or 20 of an outcome).", ""]
        (OUT / "nc1_ind_left_turns.md").write_text("\n".join(L), encoding="utf-8")
        print("\n".join(L))
        return
    rng = np.random.default_rng(20260925)
    recs = d.rec.unique()
    res = {}
    for lab, col, sign in (("TTA [s]", "tta", -1), ("distance [m]", "D_O", -1), ("looming [rad/s]", "loom", +1)):
        e = d.dropna(subset=[col])
        e = e[e[col] > 0]
        yy = e.accepted.to_numpy(float)
        # P(accept) rises with log TTA and log distance (sign -1 marks "far means accept"); for
        # looming it falls, so looming is fitted on -log and its 50% point sign-flipped back
        th = fit(np.log(e[col].to_numpy(float)) * (1 if sign == -1 else -1), yy)
        c = th[0] if sign == -1 else -th[0]
        bs = []
        for _ in range(200):
            pick = rng.choice(recs, len(recs))
            ee = pd.concat([e[e.rec == r] for r in pick])
            t_ = fit(np.log(ee[col].to_numpy(float)) * (1 if sign == -1 else -1), ee.accepted.to_numpy(float))
            bs.append(t_[0] if sign == -1 else -t_[0])
        res[lab] = (float(np.exp(c)), np.exp(np.percentile(bs, [2.5, 97.5])), float(np.exp(th[1])), len(e))
    acc = d[d.accepted]
    t_conf = float(acc.t_to_conf.median())
    tta50, tta_ci = res["TTA [s]"][0], res["TTA [s]"][1]
    pet_eq, pet_ci = tta50 - t_conf, (tta_ci[0] - t_conf, tta_ci[1] - t_conf)
    L += ["| axis | 50% point (P(accept) = 0.5) | 95% over recordings | spread [log] | decisions |", "|---|---|---|---|---|"]
    for lab, (m, ci, s, n) in res.items():
        L.append(f"| {lab} | **{m:.3f}** | [{ci[0]:.3f}, {ci[1]:.3f}] | {s:.2f} | {n} |")
    loom50 = res["looming [rad/s]"][0]
    rep = abs(pet_eq - VIDEO_PET50) <= 0.5
    carries = 0.5 <= loom50 / CUTIN_LEVEL <= 2.0
    L += ["", f"Accepting turners take a median {t_conf:.2f} s from the decision moment to the conflict point."
          f" **PET-equivalent boundary: {pet_eq:.2f} s** [{pet_ci[0]:.2f}, {pet_ci[1]:.2f}] (TTA_50 minus that"
          f" time). Accepted crossings' PET: median {acc.pet.median():.2f} s, 5th percentile"
          f" {acc.pet.quantile(0.05):.2f} s.", "",
          "## The verdicts on the pre-stated rules", "",
          f"* (1) Against the video's 2.42 s (first exposure) and the track's 2.45 s: {pet_eq:.2f} s,"
          f" **{'REPRODUCED' if rep else 'NOT reproduced'}** (rule: within 0.5 s).",
          f"* (2) The left turn's 50% looming level {loom50:.4f} rad/s against the cut-in's 0.032:"
          f" ratio {loom50 / CUTIN_LEVEL:.2f}, **{'CARRIES' if carries else 'does NOT carry'}** (rule: within a"
          " factor of 2).", "",
          "Caveats stated in advance: a real gap decision is not a video judgment (the plan's §6); the"
          " decision moment is a fixed 10 m before the conflict point, not the driver's own; repeated"
          " decisions by one turner are not independent (the bootstrap is over recordings).", "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "nc1_ind_left_turns.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
