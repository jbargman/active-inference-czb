"""
Card NM.3 -- does the published model's brake-response-time relation hold in real highD lead
decelerations?

THE PRE-REGISTRATION. Written 2026-09-25, before any highD lead-deceleration event was scored.

WHERE THE CARD COMES FROM. `docs/naturalistic_data_plan.md` §4, NM.3; the paper's Fig. 3d (brake
response time against the initial time gap, "remarkably consistent" with a meta-analysis of SHRP2
and ANNEXT) is the published model's central timing validation. The authors' deposit
(`replication/osf/seeds.csv`: 896 runs, 28 conditions x 32 seeds, initial speed 10 to 25 m/s, time
gap 0.67 to 3.92 s; `rt_brake` = the first executed deceleration of at least 1 m/s^2 after the lead's
onset; the lead brakes with a -10 m/s^3 jerk, an emergency) gives the model's relation.

WHAT IS COMPUTED ON highD (all 60 recordings, cars following in lane):
  lead onset f: the leader's longitudinal acceleration falls below -1.0 m/s^2 for at least 0.3 s
    (NC.0b's shortest duration), after at least 1 s with |a| < 0.5 m/s^2;
  kept if the follower keeps the same leader and lane from f - 1 s to f + 5 s; censored and
    counted if the follower is already below the detector's threshold at f;
  initial time gap THW0 = bumper gap / follower speed at f; the lead's peak deceleration in
    [f, f + 3 s]; response time RT = the start of the follower's first qualifying episode in
    [f, f + 5 s] minus f; no episode = no response (counted, not given an RT).
DETECTOR, decided by card NC.0b-lat before this card is run: PRIMARY = a_th 1.0 m/s^2, T_min 0.12 s
(the deposit's own definition, 3 frames) IF NC.0b-lat marks it TIMING-VALID; otherwise the first
TIMING-VALID setting in NC.0b-lat's table order; if none is valid, the card reports response
shares only (the plan's stop rule). NC.3's primary (0.5 m/s^2, 0.3 s) is reported beside it.

THE COMPARISON, in the deposit's own range of THW0 (0.67 to 3.92 s). The relation's shape: the
slope b of log RT = a + b log THW0 by least squares, in the deposit (all 896 runs) and in highD's
responding events, stratified by the lead's peak deceleration: mild (1 to 2 m/s^2), moderate (2 to
3), hard (at least 3), with a 95% bootstrap over recordings. The level: median RT at THW0 1 to 2 s.

THE RULE. The relation's SHAPE HOLDS if the deposit's slope lies inside highD's 95% interval in
the hard stratum (the closest to the deposit's emergency); if the hard stratum has fewer than 100
responding events, the moderate one is used and the report says so; if that too, the card is
DESCRIPTIVE ONLY. The LEVEL is reported, not ruled: the deposit's scenario is an emergency and
highD's are not, so real RTs are expected to be longer.

PREDICTIONS. Hard lead decelerations are rare on the motorway: the hard stratum will have fewer
than 100 responses, and the moderate stratum decides. Response shares within 5 s: 20 to 50%
(moderate), higher for hard. Slope positive in both; the deposit about +0.5; highD +0.3 to +0.7,
so the SHAPE HOLDS. Real median RT at THW0 1 to 2 s about 1.5 to 2.5 s against the deposit's
about 1.0 to 1.2 s.

Output: replication/czb/out/nm3_response_time.md (aggregates only)
Run:    python replication/czb/nm3_response_time.py   (after card NC.0b-lat)
"""
from __future__ import annotations

import re
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
import nc3_highd_cutins as N  # noqa: E402

OUT = HERE / "out"
CACHE = Path(r"C:\JonasLocal\D_Data_derived\nm3_events.pkl")
FPS, PRE, WIN, LEADWIN = 25, 25, 125, 75
SETTINGS = ((1.0, 0.12), (0.5, 0.3), (1.5, 0.3), (1.0, 0.3))
THW_RANGE = (0.668, 3.92)


def extract(rec: int):
    tr = pd.read_csv(N.HIGHD / f"{rec:02d}_tracks.csv",
                     usecols=["frame", "id", "x", "width", "xVelocity", "xAcceleration", "precedingId", "laneId"])
    meta = pd.read_csv(N.HIGHD / f"{rec:02d}_tracksMeta.csv", usecols=["id", "drivingDirection", "class"])
    tr = tr.merge(meta, on="id").sort_values(["id", "frame"]).reset_index(drop=True)
    tr["v"] = tr.xVelocity.abs()
    tr["a"] = tr.xAcceleration * np.where(tr.drivingDirection == 1, -1.0, 1.0)
    arr = {k: {c: g[c].to_numpy() for c in ("frame", "x", "width", "v", "a", "precedingId", "laneId",
                                             "drivingDirection")} | {"cls": g["class"].iloc[0]}
           for k, g in tr.groupby("id")}
    follower_of = tr[tr.precedingId > 0].set_index(["precedingId", "frame"]).id
    follower_of = follower_of[~follower_of.index.duplicated()]
    rows = []
    for i, L in arr.items():
        a = L["a"]
        on = N.runs_start(a < -1.0, 8)
        for m in np.flatnonzero(on):
            if m < PRE or np.any(np.abs(a[m - PRE:m]) >= 0.5):
                continue
            f = L["frame"][m]
            j = follower_of.get((i, f))
            if j is None or j not in arr:
                continue
            F = arr[j]
            if F["cls"] != "Car":
                continue
            q = np.searchsorted(F["frame"], f)
            if q < PRE or q + WIN + 8 > len(F["frame"]) or F["frame"][q] != f:
                continue
            if np.any(F["precedingId"][q - PRE:q + WIN] != i) or np.any(F["laneId"][q - PRE:q + WIN] != F["laneId"][q]):
                continue
            gap = (L["x"][m] - (F["x"][q] + F["width"][q])) if F["drivingDirection"][q] == 2 \
                else (F["x"][q] - (L["x"][m] + L["width"][m]))
            if gap <= 0 or F["v"][q] < 5:
                continue
            row = {"rec": rec, "v0": F["v"][q], "thw0": gap / F["v"][q], "gap": gap,
                   "lead_peak": float(-a[m:m + LEADWIN].min()), "dv0": F["v"][q] - L["v"][m]}
            fa = F["a"][q:q + WIN + 8]
            for a_th, tm in SETTINGS:
                tag = f"{a_th}_{tm}"
                row[f"pre_{tag}"] = bool(F["a"][q] < -a_th)
                st = N.runs_start(fa < -a_th, max(3, int(round(tm * FPS))))[:WIN]
                idx = np.flatnonzero(st)
                row[f"rt_{tag}"] = float(idx[0] / FPS) if len(idx) else np.nan
            rows.append(row)
    return rows


def slope(thw, rt):
    x, y = np.log(thw), np.log(rt)
    return float(np.polyfit(x, y, 1)[0]) if len(x) >= 3 else np.nan


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    lat = (OUT / "nc0b_latency.md").read_text(encoding="utf-8")
    valid = [(float(a), float(t)) for a, t in re.findall(r"\| ([\d.]+) \| ([\d.]+) \| [\d.]+ \| [\d.]+ \| [\d.]+ \| TIMING-VALID \|", lat)]
    if not valid:
        primary = None
    elif (1.0, 0.12) in valid:
        primary = (1.0, 0.12)
    else:
        primary = valid[0]
    if CACHE.exists():
        ev = pd.read_pickle(CACHE)
    else:
        with ProcessPoolExecutor(max_workers=12) as ex:
            ev = pd.DataFrame([r for rr in ex.map(extract, range(1, 61)) for r in rr])
        ev.to_pickle(CACHE)
    dep = pd.read_csv(REPO / "replication" / "osf" / "seeds.csv")
    b_dep = slope(dep.thw0, dep.rt_brake)
    med_dep = float(dep[(dep.thw0 >= 1) & (dep.thw0 <= 2)].rt_brake.median())
    L = ["# Card NM.3 -- the brake-response-time relation in real highD lead decelerations", "",
         "Generated by `replication/czb/nm3_response_time.py`; pre-stated in its docstring before the"
         " run. Aggregates only. Do not edit by hand.", "",
         f"Lead-deceleration events (leader below -1 m/s^2 for 0.3 s after 1 s of |a| < 0.5): {len(ev):,}."
         f" Detector: {'none TIMING-VALID (response shares only)' if primary is None else f'primary a_th {primary[0]:g} m/s^2, T_min {primary[1]:g} s (card NC.0b-lat)'}.", "",
         f"The deposit (896 runs): slope of log RT on log THW0 **{b_dep:+.3f}**; median RT at THW0 1-2 s"
         f" {med_dep:.2f} s.", ""]
    rng = np.random.default_rng(20260925)
    decide = None
    for a_th, tm in ([primary] if primary else []) + [s for s in ((0.5, 0.3),) if s != primary]:
        tag = f"{a_th}_{tm}"
        e = ev[~ev[f"pre_{tag}"] & (ev.thw0 >= THW_RANGE[0]) & (ev.thw0 <= THW_RANGE[1])].copy()
        e["stratum"] = pd.cut(e.lead_peak, [1.0, 2.0, 3.0, np.inf], right=False,
                              labels=["mild (1-2)", "moderate (2-3)", "hard (>=3)"])
        L += [f"## Detector a_th {a_th:g} m/s^2, T_min {tm:g} s{' (primary)' if (a_th, tm) == primary else ''}", "",
              "| lead peak deceleration [m/s^2] | events | responded within 5 s | slope of log RT on log THW0"
              " [95% over recordings] | median RT at THW0 1-2 s [s] |", "|---|---|---|---|---|"]
        for st, g in e.groupby("stratum", observed=True):
            r = g.dropna(subset=[f"rt_{tag}"])
            r = r[r[f"rt_{tag}"] > 0]
            b = slope(r.thw0, r[f"rt_{tag}"])
            recs = r.rec.unique()
            bs = []
            for _ in range(200):
                pick = rng.choice(recs, len(recs))
                rr = pd.concat([r[r.rec == p] for p in pick]) if len(recs) else r
                bs.append(slope(rr.thw0, rr[f"rt_{tag}"]))
            ci = np.nanpercentile(bs, [2.5, 97.5]) if len(r) >= 10 else (np.nan, np.nan)
            med = float(r[(r.thw0 >= 1) & (r.thw0 <= 2)][f"rt_{tag}"].median()) if len(r) else np.nan
            L.append(f"| {st} | {len(g):,} | {len(r):,} ({len(r) / max(len(g), 1):.0%}) | {b:+.3f}"
                     f" [{ci[0]:+.3f}, {ci[1]:+.3f}] | {med:.2f} |")
            if (a_th, tm) == primary:
                if st == "hard (>=3)" and len(r) >= 100:
                    decide = ("hard", b, ci)
                elif st == "moderate (2-3)" and len(r) >= 100 and decide is None:
                    decide = ("moderate", b, ci)
        L.append("")
    if primary is None:
        verdict = "NO TIMING CLAIM (the plan's stop rule): response shares only"
    elif decide is None:
        verdict = "DESCRIPTIVE ONLY: neither the hard nor the moderate stratum has 100 responses"
    else:
        holds = decide[2][0] <= b_dep <= decide[2][1]
        verdict = (f"the relation's SHAPE {'HOLDS' if holds else 'does NOT hold'} (decided on the {decide[0]}"
                   f" stratum: highD {decide[1]:+.3f} [{decide[2][0]:+.3f}, {decide[2][1]:+.3f}] against the"
                   f" deposit's {b_dep:+.3f})")
    L += ["## The verdict", "", f"**{verdict}.**", "",
          "The level is not ruled: the deposit's lead brakes as an emergency, highD's mostly do not.", "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "nm3_response_time.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
