"""
Card NC.3i -- the hard boundary on TTC at the press, and its matching deceleration.

THE PRE-REGISTRATION. Written 2026-09-24, after card NC.3h, before this fit was computed.

WHY. Card NC.3h fitted P(hard | press) on the LOOMING at the press (car clips, TTC 4-8 s labels) and
the fit was not identified: median 0.81 rad/s with a bootstrap interval open to infinity, spread
4.5 log units -- P(hard) barely depends on looming at the press. Card NC.3g showed it depends
strongly on the clip's TTC (88% hard at 2 s to 7% at 8 s), and on real highD cut-ins TTC, not
looming, orders the responses (NC.3, NC.3c). So the hard boundary is fitted here on log TTC at the
press, with the intervention boundary kept on looming (card JJ.10) as in NC.3h:
    P_hard(event) = P_int(looming) * Phi((c_T - log TTC) / s_T)
TTC at the press = gap / closing rate from the clip's own looming field (`fit_stage1_looming.
looming_field`, columns gap_m and v_rel), press time as in `jj4_precision_spread.press_levels`.
Car clips only, as NC.3h; the TTC 2 and 3 s clips are not in `press_levels` (its MATCHED_TTC), which
removes the most hard-dominated clips and is stated. Participant bootstrap (200). The matching
deceleration for this hard boundary on highD's closing cut-ins: NC.3h's `matching` with the new
curve, primary without the lapse, 95% interval over recordings (200).

PREDICTIONS. Hard boundary identified: median TTC 3 to 4.5 s (the clip labels where hard falls
through 50% are 4 to 5 s, and the press comes after the label's moment), spread 0.2 to 0.5 log
units. Matching deceleration for it: 1.5 to 2.2 m/s^2, with a narrower interval than NC.3h's hard
row only if the hard curve is steep; highD's hard responses are few, so the interval will be wide.

Output: replication/czb/out/nc3i_hard_on_ttc.md
Run:    python replication/czb/nc3i_hard_on_ttc.py   (needs card NC.3h's cache)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nc3h_two_boundaries as H  # noqa: E402
import nc3_highd_cutins as N     # noqa: E402

OUT = HERE / "out"


def ttc_at_press():
    import jj4_precision_spread as J4
    import fit_stage1_looming as F
    from comfortzone.czb_data import BUTTON_CLIP_START_S, KIN_BUTTON
    b, _ = J4.press_levels()
    b = b[(b.scenario == "cutin_car") & b.followup_code.isin([1, 2])].copy()
    fields = {}
    ttc = []
    for lab, pt in zip(b.criticality_label, b.press_time_s):
        if lab not in fields:
            fields[lab] = F.looming_field(KIN_BUTTON / f"CutInCar_{lab[3:]}TTC_vehicle_states.csv")
        f = fields[lab]
        i = int(np.clip(np.searchsorted(f.t.to_numpy(), BUTTON_CLIP_START_S + float(pt), side="right") - 1,
                        0, len(f) - 1))
        g, v = float(f.gap_m.iloc[i]), float(f.v_rel.iloc[i])
        ttc.append(g / v if v > 0 else np.nan)
    b["ttc"] = ttc
    return b[np.isfinite(b.ttc) & (b.ttc > 0)]


def fit(lt, y):
    def nll(th):
        pp = np.clip(norm.cdf((th[0] - lt) / np.exp(th[1])), 1e-9, 1 - 1e-9)
        return -float(np.sum(y * np.log(pp) + (1 - y) * np.log(1 - pp)))
    return minimize(nll, np.array([np.median(lt), np.log(0.3)]), method="L-BFGS-B").x


def main() -> None:
    b = ttc_at_press()
    lt, y, drv = np.log(b.ttc.to_numpy(float)), (b.followup_code == 2).to_numpy(float), b.driver.to_numpy()
    th = fit(lt, y)
    rng = np.random.default_rng(20260924)
    ud = np.unique(drv)
    boots = np.array([fit(lt[idx], y[idx]) for idx in
                      (np.concatenate([np.flatnonzero(drv == d) for d in rng.choice(ud, len(ud))])
                       for _ in range(200))])
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
    bs = []
    for _ in range(200):
        idx = np.concatenate([np.flatnonzero(c.rec.to_numpy() == r) for r in rng.choice(ur, len(ur))])
        bs.append(match(c.iloc[idx].reset_index(drop=True))[0])
    ci = np.nanpercentile(bs, [2.5, 97.5])
    by = b.assign(hard=y).groupby("criticality_label").agg(n=("hard", "size"), share=("hard", "mean"),
                                                            ttc=("ttc", "median"))
    L = ["# Card NC.3i -- the hard boundary on TTC at the press", "",
         "Generated by `replication/czb/nc3i_hard_on_ttc.py`; pre-stated in its docstring before the"
         " run. Do not edit by hand.", "",
         f"{len(b):,} car-clip presses (TTC 4-8 s labels), {len(ud)} participants, {y.mean():.1%} hard.", "",
         "| clip label | presses | share hard | median TTC at the press [s] |", "|---|---|---|---|"]
    for lab, r in by.iterrows():
        L.append(f"| {lab} | {int(r.n)} | {r.share:.3f} | {r.ttc:.2f} |")
    L += ["", f"P(hard | press at TTC t) = Phi((c_T - log t) / s_T): **median TTC of the hard boundary"
          f" {np.exp(cT):.2f} s** [{np.exp(np.percentile(boots[:, 0], 2.5)):.2f},"
          f" {np.exp(np.percentile(boots[:, 0], 97.5)):.2f}], spread {sT:.2f}"
          f" [{np.exp(np.percentile(boots[:, 1], 2.5)):.2f}, {np.exp(np.percentile(boots[:, 1], 97.5)):.2f}]"
          " log units (participant bootstrap).", "",
          f"On highD's {len(c):,} closing cut-ins the two-boundary model (intervention on looming,"
          f" hard on TTC) expects {expected:.1f} hard interventions; the deceleration at which the"
          f" observed count matches it is **{a_m:.2f} m/s^2** [{ci[0]:.2f}, {ci[1]:.2f}] (bootstrap"
          " over recordings).", ""]
    (OUT / "nc3i_hard_on_ttc.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
