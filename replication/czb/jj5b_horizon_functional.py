"""
Card JJ.5b -- the functional over the horizon: is the horizon SUM what makes every rollout
quantity anti-ordered, and does another reading of the same looming preference order the cells?

THE PRE-REGISTRATION. Everything in this docstring was written before the run, on 2026-09-22,
after card JJ.5's result was seen (0.3156, rho(gap) +0.662, NOT CREDITED).

WHY. Card JJ.5 read the released looming preference alone and it was anti-ordered with the
response exactly as the braking-margin term (RE.2) and the price of safety (S1.6) were. All three
sum a pre-contact cost over the horizon of a `continue` policy that drives through the lead, and
such a sum counts the STEPS BEFORE CONTACT: the review's checks (section 1) showed the summed
braking-margin term correlates +0.920 with the TTC. If that is the mechanism, it is the
functional and not the term that fails, and the same per-step profile read differently should
order the cells. This card tests that on JJ.5's own construction, primary reading (in_path,
corrected fan, seed 0), with nothing else changed.

THE FOUR FUNCTIONALS of the per-step expected excess e_t (`rollout.looming_pref.eps_tau_profile`)
  **sum**     sum_t e_t                     card JJ.5's quantity, the reproduction check
  **rate**    sum_t e_t / n_pre              per step before contact, n_pre = the number of steps at
                                             which at least half the futures are still before
                                             contact (the review's "divided by min(TTC, 6)" made
                                             exact on the fan)
  **max**     max_t e_t                      the worst moment in the horizon
  **first**   e_1                            the looming excess at the first step, 0.2 s after the
                                             freeze: what the model sees NOW, gated by P(in path now)
Under `rate`, `max` and `first` the number of pre-contact steps no longer enters.

THE RULES -- card JJ.5's, verbatim, for each functional: (a) within 0.01 of the gated looming rule's
0.1027, (b) pre-onset below 0.05 with no gate term, (c) at least 12 of 24 matched-TTC rows. Verdict
per functional as in JJ.5 (ADOPT / AXIS / GATE / NOT CREDITED). Rule 0: `sum` reproduces JJ.5's
0.3156 within 0.0005. Sign +1 is the rule's; sign -1 is reported and credits nothing.

WHAT THE `first` READING IS, said before the run so that a pass is not over-read: post-onset the
intention posterior is 1.0 and the other is already entering, so e_1 is a monotone transform of
tau^-1 at the freeze, i.e. Delta v / gap, which the registered R.2 script scored as its "ttc" model.
Pre-onset the other is not yet in the path at step 1 in most futures, so e_1 is near zero and rule
(b) can hold by construction: that would be a STEP gate ("is the other in my path now"), not card
G.1's anticipatory one, and the report says so if it happens. The `max` reading is the one that
carries anticipation, and it is the reading I expect to matter.

PREDICTIONS
  sum:   0.3156 (reproduction).
  rate:  0.20 to 0.28, rho(gap) near zero; not credited.
  max:   0.13 to 0.20 post-onset -- the worst moment is dominated by the steps just before contact,
         whose excess is capped only by the mask, so it may be nearly constant across cells; if so
         it fails. Pre-onset 0.10 to 0.40. This is the reading whose result I cannot call.
  first: post-onset near the TTC threshold's own score (0.18 to 0.22); pre-onset below 0.05 by
         construction (step gate); rule (c) fails (tau^-1 is the same within a matched row).
  None reaches (a). If `first` is credited on (b) alone the verdict is GATE, and the honest reading
  is that the gate is trivial there.

Output: replication/czb/out/jj5b_horizon_functional.md, out/jj5b_horizon_functional_cells.csv
Run:    python replication/czb/jj5b_horizon_functional.py
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import jj5_looming_preference as J5        # noqa: E402  card JJ.5 (read only)
from aidriver.preferences import PreferenceParams  # noqa: E402
from rollout.looming_pref import eps_tau_profile  # noqa: E402
from rollout.policies import ego_rollout  # noqa: E402
from rollout.predictor import DT_S, HORIZON_S, N_SAMPLES, SD_A, SD_VLAT, sample_futures  # noqa: E402

OUT = HERE / "out"
JJ5_SUM, REPRO_TOL = 0.3156, 0.0005
FUNCTIONALS = ("sum", "rate", "max", "first")


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    bel = J5.beliefs(cells)
    rows = []
    for v, (b, cp) in bel.items():
        fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES, sd_vlat=SD_VLAT,
                             sd_a=SD_A, seed=0, keep_body_in_lane=True)
        e, n_pre = eps_tau_profile(b, ego_rollout(b, "continue", HORIZON_S, DT_S), fut,
                                   PreferenceParams(v_desired=b.v_ego), "in_path")
        rows.append({"video": v, "cp": cp, "n_pre": n_pre, "sum": float(e.sum()),
                     "rate": float(e.sum() / max(n_pre, 1)), "max": float(e.max()),
                     "first": float(e[0]), "t_max": float((np.argmax(e) + 1) * DT_S)})
    df = pd.DataFrame(rows)
    df.merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance", "dv_kph"]],
             on="video").to_csv(OUT / "jj5b_horizon_functional_cells.csv", index=False)
    res = {f: J5.score(df, cells, f) for f in FUNCTIONALS}
    repro = abs(res["sum"]["post"] - JJ5_SUM) <= REPRO_TOL
    is_cp1 = (df.cp == "CP1").to_numpy()

    def verdict(s):
        if s is None:
            return "every cell at zero"
        a = s["post"] <= J5.G1_GATED + J5.MARGIN_A
        b = s["cp1"] < J5.CP1_CRIT
        return "ADOPT" if a and b else ("AXIS" if a else ("GATE" if b else "NOT CREDITED"))

    L = ["# Card JJ.5b -- the functional over the horizon", "",
         "Generated by `replication/czb/jj5b_horizon_functional.py`; the functionals, the rules and"
         " the predictions were pre-stated in its docstring before the run. Do not edit by hand.",
         "",
         "Card JJ.5's construction, primary reading, with the per-step expected excess of the"
         " released looming preference read four ways instead of summed.", "",
         "## 0 Reproduction and the profile", "",
         f"`sum` scores {res['sum']['post']:.4f} against card JJ.5's {JJ5_SUM}:"
         f" **{'PASS' if repro else 'FAIL'}**. Steps before contact (median): pre-onset"
         f" {np.median(df.n_pre[is_cp1]):.0f}, post-onset {np.median(df.n_pre[~is_cp1]):.0f} of 30;"
         f" the worst moment sits at {np.median(df.t_max[~is_cp1]):.1f} s (median, post-onset).", "",
         "## 1 The four functionals", "",
         "| functional | post-onset held out, sign +1 | sign -1 | pre-onset, no gate term |"
         " matched-TTC rows | rho(share) | rho(gap) | verdict |", "|---|---|---|---|---|---|---|---|"]
    for f in FUNCTIONALS:
        L.append(f"| **{f}** " + J5.fmt(res[f]) + f" **{verdict(res[f])}** |")
    L += ["", f"Comparators: gated looming rule {J5.G1_GATED} (pre-onset {J5.G1_CP1}), ungated"
          f" {J5.G1_UNGATED}, gap {J5.GAP_RULE}, chance {J5.CHANCE}.", "",
          "## 2 Reading", "",
          ("**The horizon sum is what inverts the quantity**: `sum` has rho(gap)"
           f" {res['sum']['rho_gap']:+.3f} and the per-step `rate` has"
           f" {res['rate']['rho_gap']:+.3f}." if res["rate"] else ""),
          (" `first` is a step gate by construction (see the docstring) and its pre-onset score"
           f" of {res['first']['cp1']:.4f} should not be read as anticipation." if res["first"] else ""),
          "", f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj5b_horizon_functional.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
