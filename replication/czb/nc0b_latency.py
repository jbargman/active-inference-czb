"""
Card NC.0b-lat -- the deceleration-onset detector's latency and hit rate, on real highD noise with
synthetic braking of known onset.

THE PRE-REGISTRATION. Written 2026-09-25, before this was computed.

WHY. `docs/naturalistic_data_plan.md` §2, NC.0b: the detector must be "validated on synthetic
traces with known onsets plus the measured jitter, reporting the detection latency (crossing time
minus the true start of deceleration) and the false-positive rate", with the STOP RULE: "if no
setting in the grid keeps the false-positive rate under 5% with a median latency under 0.5 s, no
timing claim is made from highD". Card NC.3 used the detector without this step and made no timing
claim. Card NM.3 (response time against the time gap) needs timing; this card comes first.

WHAT IS COMPUTED. Backgrounds: real follower longitudinal acceleration (highD's xAcceleration,
along the direction of travel, 25 Hz as provided) in 4 s windows of steady following (same leader
and lane throughout, leader |a| < 0.3 m/s^2), from the first 20 recordings, up to 4 000 windows.
Using the recorded signal as the noise keeps highD's own smoothing and jitter. Synthetic braking
added at t0 = 1.0 s into each window: a(t) = a_bg(t) - min(J (t - t0), A) for t >= t0, with peak
A in {1, 2, 3, 5} m/s^2 and jerk J in {2, 5, 10} m/s^3 (from gentle to emergency-like onsets).
Detector grid: a_th in {0.5, 1.0, 1.5, 2.0} m/s^2 x T_min in {0.12, 0.3, 0.5, 1.0} s (0.12 s =
3 frames, the closest to the deposit's "first executed a <= -1 m/s^2" at its 0.2 s step). A hit
is the first qualifying episode starting at or after t0 - 0.2 s; latency = its start - t0. The
false-positive rate here = the share of BACKGROUND windows (no synthetic braking) with a
qualifying episode anywhere in the 4 s.

NOT covered, stated: highD's own processing of positions into accelerations may add a lag before
the signal we read; that lag is invisible here and applies to every event alike.

THE RULE, per setting: TIMING-VALID if the false-positive rate is under 5% and the median latency
over the profiles with A >= a_th + 0.5 is under 0.5 s. The plan's stop rule: if no setting is
TIMING-VALID, no timing claim is made from highD (cards NM.3 and NC.4 then report yes/no only).

PREDICTIONS. The latency is dominated by the threshold crossing, about a_th / J: at a_th 1.0 and
J 5, 0.2 s plus T_min's effect none (the run's START is the crossing). Hit rates near 1 for A well
above a_th. FP rates at 4 s windows somewhat above NC.0b's 3 s windows (2.6% at a_th 0.5, T 0.3).
TIMING-VALID: every a_th >= 1.0 setting and a_th 0.5 at T_min >= 0.3.

Output: replication/czb/out/nc0b_latency.md
Run:    python replication/czb/nc0b_latency.py
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
sys.path.insert(0, str(HERE))
import nc3_highd_cutins as N  # noqa: E402

OUT = HERE / "out"
FPS, WIN, T0 = 25, 100, 25
A_TH = (0.5, 1.0, 1.5, 2.0)
T_MIN = (0.12, 0.3, 0.5, 1.0)
PEAKS = (1.0, 2.0, 3.0, 5.0)
JERKS = (2.0, 5.0, 10.0)
MAX_WIN = 4000


def backgrounds(rec: int):
    tr = pd.read_csv(N.HIGHD / f"{rec:02d}_tracks.csv",
                     usecols=["frame", "id", "xAcceleration", "precedingId", "laneId"])
    meta = pd.read_csv(N.HIGHD / f"{rec:02d}_tracksMeta.csv", usecols=["id", "drivingDirection", "class"])
    tr = tr.merge(meta, on="id").sort_values(["id", "frame"])
    tr["a"] = tr.xAcceleration * np.where(tr.drivingDirection == 1, -1.0, 1.0)
    arr = {k: (g.frame.to_numpy(), g.a.to_numpy(), g.precedingId.to_numpy(), g.laneId.to_numpy(),
               g["class"].iloc[0]) for k, g in tr.groupby("id")}
    out = []
    for j, (fr, a, p, lane, cls) in arr.items():
        if cls != "Car":
            continue
        k = 0
        while k + WIN <= len(fr):
            lead = p[k]
            if lead > 0 and lead in arr and np.all(p[k:k + WIN] == lead) and np.all(lane[k:k + WIN] == lane[k]):
                lf, la = arr[lead][0], arr[lead][1]
                m = np.searchsorted(lf, fr[k])
                if m + WIN <= len(lf) and lf[m] == fr[k] and np.all(np.abs(la[m:m + WIN]) < 0.3):
                    out.append(a[k:k + WIN].copy())
                    k += WIN
                    continue
            k += FPS
    return out


def first_start(a, a_th, t_min, from_idx):
    st = N.runs_start(a < -a_th, max(3, int(round(t_min * FPS))))
    idx = np.flatnonzero(st[from_idx:])
    return (idx[0] + from_idx) if len(idx) else None


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=12) as ex:
        bg = [w for ws in ex.map(backgrounds, range(1, 21)) for w in ws]
    rng = np.random.default_rng(20260925)
    if len(bg) > MAX_WIN:
        bg = [bg[i] for i in rng.choice(len(bg), MAX_WIN, replace=False)]
    bg = np.array(bg)
    tt = np.arange(WIN) / FPS
    rows = []
    for a_th in A_TH:
        for tm in T_MIN:
            fp = np.mean([first_start(w, a_th, tm, 0) is not None for w in bg])
            for A in PEAKS:
                for J in JERKS:
                    ramp = np.where(tt >= T0 / FPS, np.minimum(J * (tt - T0 / FPS), A), 0.0)
                    lat = []
                    for w in bg:
                        s = first_start(w - ramp, a_th, tm, T0 - 5)
                        lat.append(np.nan if s is None else (s - T0) / FPS)
                    lat = np.array(lat)
                    rows.append({"a_th": a_th, "t_min": tm, "fp": fp, "A": A, "J": J,
                                 "hit": float(np.mean(np.isfinite(lat))),
                                 "lat_med": float(np.nanmedian(lat)) if np.isfinite(lat).any() else np.nan})
        print(f"a_th {a_th} done [{time.time() - t0:.0f} s]", flush=True)
    r = pd.DataFrame(rows)
    L = ["# Card NC.0b-lat -- the detector's latency and hit rate on real highD noise", "",
         "Generated by `replication/czb/nc0b_latency.py`; pre-stated in its docstring before the run."
         " Do not edit by hand.", "",
         f"{len(bg):,} real 4 s steady-following acceleration windows (recordings 1-20) as background;"
         " synthetic braking of known onset added at 1.0 s.", "",
         "| a_th [m/s^2] | T_min [s] | false positives (4 s) | median latency, profiles with A >= a_th + 0.5 [s] |"
         " mean hit rate, same profiles | verdict |", "|---|---|---|---|---|---|"]
    valid = []
    for (a_th, tm), g in r.groupby(["a_th", "t_min"]):
        gg = g[g.A >= a_th + 0.5]
        lm, hit, fp = float(np.nanmedian(gg.lat_med)), float(gg.hit.mean()), float(g.fp.iloc[0])
        ok = fp < 0.05 and lm < 0.5
        if ok:
            valid.append((a_th, tm))
        L.append(f"| {a_th:g} | {tm:g} | {fp:.3f} | {lm:.2f} | {hit:.3f} | {'TIMING-VALID' if ok else 'not valid'} |")
    L += ["", "Latency by profile at the two settings used downstream (deposit-like 1.0 m/s^2 / 0.12 s;"
          " NC.3's primary 0.5 / 0.3):", "",
          "| setting | A [m/s^2] | J [m/s^3] | hit rate | median latency [s] |", "|---|---|---|---|---|"]
    for a_th, tm in ((1.0, 0.12), (0.5, 0.3)):
        for _, x in r[(r.a_th == a_th) & (r.t_min == tm)].iterrows():
            L.append(f"| {a_th:g} / {tm:g} | {x.A:g} | {x.J:g} | {x.hit:.3f} | {x.lat_med:.2f} |")
    L += ["", ("**Stop rule: at least one setting is TIMING-VALID; timing claims may be made at those"
               " settings.**" if valid else "**Stop rule: NO setting is TIMING-VALID; no timing claim"
               " is made from highD.**"), "",
          "Not covered: any lag in highD's own derivation of accelerations from positions.", "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "nc0b_latency.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
