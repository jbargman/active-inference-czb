"""
Card NM.2 -- is the published model's calibrated following preference where real drivers follow?

THE PRE-REGISTRATION. Written 2026-09-25, before any highD following state was scored.

WHERE THE CARD COMES FROM. `docs/naturalistic_data_plan.md` §4, NM.2: "the preference function
(`src/aidriver/preferences.py`, verified against the code) evaluated on real following states: the
share of real following that the collision-and-safety term scores as a shortfall, which is what
feeds the accumulator in NM.1." Jonas, 2026-09-25: run the paper-assessment cards overnight.

WHAT IS COMPUTED. highD, all 60 recordings, cars following a car or truck: every whole second at
which the follower has a preceding vehicle in its own lane. Per sample: follower speed v and
longitudinal acceleration a (along its direction of travel), the leader's v_o and a_o, the bumper
gap g (from x, the box length and the driving direction), the centre-to-centre distance
dx = g + (L_follower + L_leader)/2, the time headway THW = g / v. STEADY FOLLOWING, the subset the
card is about: the same leader and lane for the next 3 s and the leader's |a_o| below 0.3 m/s^2
throughout (NC.0b's definition). The RELEASED preference (`PreferenceParams(v_desired=v)`, released
flags, no project staging) is evaluated at each sample with dy = 0: `log_collision_pref` (its
tau^-1 part fires when closing faster than 1/5 s) and `log_safety_pref` (the braking margin: fires
when the counterfactual "the lead brakes at 6 m/s^2, I react after 1 s" needs more than a_max =
8 m/s^2). Shares of samples with each term below zero, and the mean nats per step.

THE BOUNDARY IN CLOSED FORM. At equal speeds the braking-margin term fires when
dx < v + 1.15 x 4.2 - v^2 / 48 (from SI Eq. 51 with the released constants), i.e. a time headway
below about 0.3 to 0.6 s at motorway speeds. Reported per speed band beside the real THW
percentiles.

THE RULE. The calibrated preference is WHERE REAL DRIVERS FOLLOW if, in the steady-following
subset, the real median THW lies within 0.3 s of the preference's boundary THW in most speed bands;
TOLERANT if the boundary THW lies below the real 5th percentile THW in every band with at least
500 samples (the preference is silent over nearly all of real following); INTOLERANT if the
boundary lies above the real median in most bands.

PREDICTIONS. TOLERANT: the boundary at 0.3 to 0.6 s, real medians 1.2 to 2 s, real 5th percentiles
0.5 to 0.8 s. The braking-margin term fires in 1 to 3% of steady following, the tau^-1 term in
under 1%. So the preference as calibrated does not explain where drivers choose to follow; that is
the comfort zone's job, and it also says the accumulator's non-zero level in ordinary following
(method review §4.2) does not come from these terms.

Output: replication/czb/out/nm2_following_preference.md (aggregates only)
Run:    python replication/czb/nm2_following_preference.py
"""
from __future__ import annotations

import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

HIGHD = Path(r"C:\JonasLocal\D_Data\highD-dataset-v1.0\data")
CACHE = Path(r"C:\JonasLocal\D_Data_derived\nm2_following.pkl")
OUT = HERE / "out"
FPS, STEP, AHEAD = 25, 25, 75
LEAD_STEADY = 0.3
BANDS_KMH = [40, 70, 90, 110, 130, 200]


def extract(rec: int) -> pd.DataFrame:
    tr = pd.read_csv(HIGHD / f"{rec:02d}_tracks.csv",
                     usecols=["frame", "id", "x", "width", "xVelocity", "xAcceleration",
                              "precedingId", "laneId"])
    meta = pd.read_csv(HIGHD / f"{rec:02d}_tracksMeta.csv", usecols=["id", "drivingDirection", "class"])
    tr = tr.merge(meta, on="id")
    tr["v"] = tr.xVelocity.abs()
    tr["a"] = tr.xAcceleration * np.where(tr.drivingDirection == 1, -1.0, 1.0)
    key = tr.set_index(["id", "frame"])
    s = tr[(tr.frame % STEP == 0) & (tr.precedingId > 0) & (tr["class"] == "Car")].copy()
    idx_lead = pd.MultiIndex.from_arrays([s.precedingId, s.frame])
    for c in ("x", "width", "v", "a", "laneId"):
        s[f"{c}_o"] = key[c].reindex(idx_lead).to_numpy()
    s = s[np.isfinite(s.x_o) & (s.laneId_o == s.laneId)]
    s["gap"] = np.where(s.drivingDirection == 2, s.x_o - (s.x + s.width), s.x - (s.x_o + s.width_o))
    s = s[s.gap > 0].copy()
    s["dx"] = s.gap + (s.width + s.width_o) / 2.0
    # steady: same leader and lane for the next 3 s, leader |a| < 0.3 throughout
    fut = pd.MultiIndex.from_arrays([s.id, s.frame + AHEAD])
    same = (key.precedingId.reindex(fut).to_numpy() == s.precedingId.to_numpy()) & \
           (key.laneId.reindex(fut).to_numpy() == s.laneId.to_numpy())
    steady = same.copy()
    for k in range(0, AHEAD + 1, 5):
        a_o = key.a.reindex(pd.MultiIndex.from_arrays([s.precedingId, s.frame + k])).to_numpy()
        steady &= np.abs(np.nan_to_num(a_o, nan=99.0)) < LEAD_STEADY
    s["steady"] = steady
    s["rec"] = rec
    return s[["rec", "v", "a", "v_o", "a_o", "gap", "dx", "steady"]]


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    from aidriver.preferences import PreferenceParams, log_collision_pref, log_safety_pref
    if CACHE.exists():
        d = pd.read_pickle(CACHE)
    else:
        recs = sorted(int(p.name[:2]) for p in HIGHD.glob("*_tracks.csv"))
        with ProcessPoolExecutor(max_workers=12) as ex:
            d = pd.concat(list(ex.map(extract, recs)), ignore_index=True)
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        d.to_pickle(CACHE)
    d = d[(d.v > 5)].reset_index(drop=True)
    d["thw"] = d.gap / d.v
    p = PreferenceParams()
    obs = {"v": d.v.to_numpy(), "a": d.a.to_numpy(), "dx": d.dx.to_numpy(), "dy": np.zeros(len(d)),
           "v_other": d.v_o.to_numpy(), "a_other": d.a_o.to_numpy()}
    from aidriver.preferences import inverse_tau
    obs["tau_inv"] = inverse_tau(obs["dx"], obs["v"], obs["v_other"], p)
    d["coll"] = np.asarray(log_collision_pref(obs, p), float)
    d["safe"] = np.asarray(log_safety_pref(obs, p), float)
    kmh = d.v * 3.6
    d["band"] = pd.cut(kmh, BANDS_KMH)
    L = ["# Card NM.2 -- the published model's following preference against real highD following", "",
         "Generated by `replication/czb/nm2_following_preference.py`; pre-stated in its docstring"
         " before the run. Aggregates only (highD licence). Do not edit by hand.", "",
         f"{len(d):,} car-following samples (one a second), {int(d.steady.sum()):,} of them steady"
         " (same leader and lane for 3 s, leader |a| < 0.3 m/s^2).", "",
         "| speed band [km/h] | steady samples | real THW 1st / 5th / 50th pct [s] | the braking margin's"
         " boundary THW at equal speed [s] | braking margin fires | tau^-1 term fires | mean nats"
         " per step (both terms) |", "|---|---|---|---|---|---|---|"]
    verdicts = []
    for band, g in d[d.steady].groupby("band", observed=True):
        if len(g) < 500:
            continue
        v = (band.left + band.right) / 2 / 3.6
        dx_b = v + 1.15 * 4.2 - v ** 2 / 48.0
        thw_b = max(dx_b - 4.5, 0.0) / v
        q1, q5, q50 = np.percentile(g.thw, [1, 5, 50])
        verdicts.append((thw_b, q5, q50))
        L.append(f"| {band} | {len(g):,} | {q1:.2f} / {q5:.2f} / {q50:.2f} | {thw_b:.2f} |"
                 f" {np.mean(g.safe < 0):.3%} | {np.mean(g.coll < 0):.3%} |"
                 f" {-(g.safe + g.coll).mean():.2f} |")
    allg = d[d.steady]
    L += [f"| all steady | {len(allg):,} | {np.percentile(allg.thw, 1):.2f} /"
          f" {np.percentile(allg.thw, 5):.2f} / {np.percentile(allg.thw, 50):.2f} | - |"
          f" {np.mean(allg.safe < 0):.3%} | {np.mean(allg.coll < 0):.3%} | {-(allg.safe + allg.coll).mean():.2f} |",
          f"| all following (not only steady) | {len(d):,} | - | - | {np.mean(d.safe < 0):.3%} |"
          f" {np.mean(d.coll < 0):.3%} | {-(d.safe + d.coll).mean():.2f} |", ""]
    tolerant = all(b < q5 for b, q5, _ in verdicts)
    near = sum(abs(b - q50) <= 0.3 for b, _, q50 in verdicts) > len(verdicts) / 2
    intolerant = sum(b > q50 for b, _, q50 in verdicts) > len(verdicts) / 2
    verdict = ("WHERE REAL DRIVERS FOLLOW" if near else "TOLERANT" if tolerant
               else "INTOLERANT" if intolerant else "MIXED")
    L += ["## Verdict on the pre-stated rule", "",
          f"**{verdict}.** The braking margin's boundary headway (equal speeds, released constants)"
          " against the real 5th percentile and median THW, band by band, in the table.", "",
          "The boundary is computed at equal speeds and a leader of 4.5 m; the per-sample shares use"
          " each sample's own speeds and lengths.", "", f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "nm2_following_preference.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
