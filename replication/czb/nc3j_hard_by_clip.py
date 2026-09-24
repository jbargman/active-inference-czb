"""
Card NC.3j -- the hard boundary at the clip level, and its matching deceleration.

THE PRE-REGISTRATION. Written 2026-09-24, after cards NC.3h and NC.3i, before this fit.

WHY. Per press, P(hard | press) is not identified on looming (NC.3h) or on TTC at the press
(NC.3i): within a clip, the moment of pressing does not predict hard against gentle. Between clips
it is strongly graded (NC.3g: 88% hard at the TTC 2 s clip to 7% at 8 s). So participants judge
hard or gentle per scenario, and the hard boundary is fitted at that level: one point per clip.

WHAT IS COMPUTED. `button_cutin_trials()` (the first study's button design, car cut-ins, all seven
clips TTC 2 to 8 s), presses with a gentle/hard answer. Per clip: presses, share hard, and the
median TTC at the press (gap / closing rate from the clip's `looming_field` at onset +
`press_since_onset`; onset from `load_cutin_trace`). Binomial maximum likelihood on the seven
clips: share hard = Phi((c_T - log TTC_clip) / s_T); participant bootstrap (200) for intervals.
The two-boundary model on highD (NC.3h's cache, closing cut-ins, no lapse):
P_hard(event) = P_int(looming) * Phi((c_T - log TTC_event) / s_T), TTC_event at the lane switch
(the cutter entering, comparable to the press moment of the clips, which is after the onset).
The matching deceleration and its interval over recordings as in NC.3h.

PREDICTIONS. Median TTC of the hard boundary 3.5 to 4.5 s, spread 0.2 to 0.4 log units (seven
well-separated points). Expected hard interventions on highD far fewer than NC.3h's 21 (most
highD cut-ins have TTC above 10 s, where the clip-level curve is near zero), so the matching
deceleration rises: 2.0 to 2.6 m/s^2, with a wide interval (few events).

Output: replication/czb/out/nc3j_hard_by_clip.md
Run:    python replication/czb/nc3j_hard_by_clip.py   (needs card NC.3h's cache)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))
import nc3h_two_boundaries as H  # noqa: E402
import fit_stage1_looming as F   # noqa: E402
from comfortzone.cutin import load_cutin_trace  # noqa: E402
from comfortzone.czb_data import KIN_BUTTON, button_cutin_trials  # noqa: E402

OUT = HERE / "out"


def presses():
    b = button_cutin_trials()
    b = b[(b.censored == 0) & b.own_braking.isin([1, 2])].copy()
    ttc = []
    cache = {}
    for lab, ps in zip(b.criticality, b.press_since_onset):
        if lab not in cache:
            path = KIN_BUTTON / f"CutInCar_{lab[3:]}TTC_vehicle_states.csv"
            tr = load_cutin_trace(path)
            cache[lab] = (F.looming_field(path), float(tr.t[tr.onset_idx]))
        f, t_on = cache[lab]
        i = int(np.clip(np.searchsorted(f.t.to_numpy(), t_on + float(ps), side="right") - 1, 0, len(f) - 1))
        g, v = float(f.gap_m.iloc[i]), float(f.v_rel.iloc[i])
        ttc.append(g / v if v > 0 else np.nan)
    b["ttc"] = ttc
    b["hard"] = (b.own_braking == 2).astype(float)
    return b[np.isfinite(b.ttc) & (b.ttc > 0)]


def fit_clips(b):
    g = b.groupby("criticality").agg(k=("hard", "sum"), n=("hard", "size"), ttc=("ttc", "median"))
    lt, k, n = np.log(g.ttc.to_numpy()), g.k.to_numpy(), g.n.to_numpy()

    def nll(th):
        p = np.clip(norm.cdf((th[0] - lt) / np.exp(th[1])), 1e-9, 1 - 1e-9)
        return -float(np.sum(k * np.log(p) + (n - k) * np.log(1 - p)))
    return minimize(nll, np.array([np.log(4.0), np.log(0.3)]), method="L-BFGS-B").x, g


def main() -> None:
    b = presses()
    th, g = fit_clips(b)
    rng = np.random.default_rng(20260924)
    ud = b.participant.unique()
    boots = []
    for _ in range(200):
        idx = np.concatenate([np.flatnonzero(b.participant.to_numpy() == d) for d in rng.choice(ud, len(ud))])
        boots.append(fit_clips(b.iloc[idx])[0])
    boots = np.array(boots)
    cT, sT = th[0], float(np.exp(th[1]))

    ev, _ = pd.read_pickle(H.CACHE)
    c = ev[~ev.lc & (ev.dv > 0)].reset_index(drop=True)

    def match(s):
        x = np.log((s.W * s.dv / (s.gap ** 2 + s.W ** 2 / 4)).to_numpy(float))
        ltt = np.log((s.gap / s.dv).to_numpy(float))
        pred = norm.cdf((x - np.log(H.INT_LEVEL)) / H.INT_SPREAD) * norm.cdf((cT - ltt) / sT)
        diff = []
        for a in H.GRID:
            keep = s.a_now.to_numpy() <= a
            diff.append((s.a_resp.to_numpy()[keep] >= a).sum() - pred[keep].sum())
        diff = np.array(diff)
        k = np.flatnonzero(np.diff(np.sign(diff)) != 0)
        if len(k) == 0:
            return np.nan, pred.sum()
        k = k[0]
        return float(H.GRID[k] + (H.GRID[k + 1] - H.GRID[k]) * diff[k] / (diff[k] - diff[k + 1])), pred.sum()

    a_m, expected = match(c)
    ur = c.rec.unique()
    bs = [match(c.iloc[np.concatenate([np.flatnonzero(c.rec.to_numpy() == r) for r in rng.choice(ur, len(ur))])]
                .reset_index(drop=True))[0] for _ in range(200)]
    ci = np.nanpercentile(bs, [2.5, 97.5])
    L = ["# Card NC.3j -- the hard boundary at the clip level", "",
         "Generated by `replication/czb/nc3j_hard_by_clip.py`; pre-stated in its docstring before the"
         " run. Do not edit by hand.", "",
         "| clip | presses | share hard | median TTC at the press [s] |", "|---|---|---|---|"]
    for lab, r in g.sort_values("ttc").iterrows():
        L.append(f"| {lab} | {int(r.n)} | {r.k / r.n:.3f} | {r.ttc:.2f} |")
    L += ["", f"Share hard = Phi((c_T - log TTC) / s_T) over the seven clips: **the hard boundary's"
          f" median TTC {np.exp(cT):.2f} s** [{np.exp(np.percentile(boots[:, 0], 2.5)):.2f},"
          f" {np.exp(np.percentile(boots[:, 0], 97.5)):.2f}], spread {sT:.2f}"
          f" [{np.exp(np.percentile(boots[:, 1], 2.5)):.2f}, {np.exp(np.percentile(boots[:, 1], 97.5)):.2f}]"
          " (participant bootstrap).", "",
          f"On highD's {len(c):,} closing cut-ins the two-boundary model expects {expected:.1f} hard"
          f" interventions; the matching deceleration is **{a_m:.2f} m/s^2** [{ci[0]:.2f}, {ci[1]:.2f}]"
          " (bootstrap over recordings).", ""]
    (OUT / "nc3j_hard_by_clip.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
