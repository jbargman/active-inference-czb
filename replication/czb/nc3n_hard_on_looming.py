"""
Card NC.3n -- do the two studies' hard boundaries agree once expressed in LOOMING instead of TTC?

THE PRE-REGISTRATION. Written 2026-09-25, after card NC.3m, before this was computed.

WHY. Card NC.3m: within the first study's 43 participants, "expect the car to brake hard" (3.04 s)
and "I would brake hard" (3.29 s) do not differ; but the second study's "expect hard" sits at
1.64 s. So the gap is between studies, not constructs. Card NC.3l found the second study's
"expect hard" judgment follows looming (0.104) far better than TTC (0.168); if the judgment is a
looming threshold, its TTC equivalent depends on the closing speeds and gaps of each design, and a
TTC boundary will not transfer between designs while a looming boundary should.

WHAT IS COMPUTED. The 50% LOOMING of a cell-level binomial probit on log looming (card EL.1b's
axis), for: (A) study 1, expected vehicle action, Random, 18 cells (NC.3m's cells; looming from
`build_trials`' theta_dot); (B) study 1, own action, Button, 7 clips (NC.3j's presses; the looming
at the press from `press_levels`-style reading of `looming_field`, median per clip); (C) study 2,
expected vehicle action, 288 post-onset cells (NC.3l's cells; `jj6_belief_gate.looming_axis`).
Participant bootstraps (200) for A and B; for C a bootstrap over participants of study 2.

THE RULE. The hard boundary REPLICATES ON LOOMING if A and C, the same question in two studies,
lie within 30% of each other (|log ratio| < 0.26); the TTC boundaries of the same two (3.04 and
1.64 s) differ by 85%. B is reported beside them.

PREDICTIONS. A and C within 30%: REPLICATES, at about 0.10 to 0.2 rad/s, three to six times the
intervention level of 0.032 rad/s. B close to A (NC.3m).

Output: replication/czb/out/nc3n_hard_on_looming.md
Run:    python replication/czb/nc3n_hard_on_looming.py
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
import cutin2_field_vs_gap as R   # noqa: E402
import fit_stage1_looming as F   # noqa: E402
import jj6_belief_gate as J6      # noqa: E402
from comfortzone.cutin import load_cutin_trace  # noqa: E402
from comfortzone.czb_data import KIN_BUTTON, button_cutin_trials  # noqa: E402

OUT = HERE / "out"
INT_LEVEL = 0.0320


def fit(lx, k, n):
    def nll(th):
        p = np.clip(norm.cdf((lx - th[0]) / np.exp(th[1])), 1e-9, 1 - 1e-9)
        return -float(np.sum(k * np.log(p) + (n - k) * np.log(1 - p)))
    return minimize(nll, np.array([np.log(0.1), 0.0]), method="L-BFGS-B").x


def cells(df, keys):
    g = df.groupby(keys).agg(k=("hard", "sum"), n=("hard", "size"), lx=("lx", "median"))
    return g.lx.to_numpy(), g.k.to_numpy(), g.n.to_numpy()


def boot(df, keys, pid, rng, B=200):
    ids = df[pid].unique()
    out = []
    for _ in range(B):
        pick = rng.choice(ids, len(ids))
        out.append(fit(*cells(pd.concat([df[df[pid] == p] for p in pick]), keys))[0])
    return np.exp(np.percentile(out, [2.5, 97.5]))


def main() -> None:
    rng = np.random.default_rng(20260925)
    # A: study 1, expected vehicle action
    a = F.build_trials()
    a = a[a.braking_expectation.isin([0, 1, 2]) & (a.theta_dot > 0)].copy()
    a.attrs = {}
    a["hard"] = (a.braking_expectation == 2).astype(float)
    a["lx"] = np.log(a.theta_dot)
    # B: study 1, own action at the press
    b = button_cutin_trials()
    b = b[(b.censored == 0) & b.own_braking.isin([1, 2])].copy()
    fields = {}
    lx = []
    for lab, ps in zip(b.criticality, b.press_since_onset):
        if lab not in fields:
            path = KIN_BUTTON / f"CutInCar_{lab[3:]}TTC_vehicle_states.csv"
            tr = load_cutin_trace(path)
            fields[lab] = (F.looming_field(path), float(tr.t[tr.onset_idx]))
        f, t_on = fields[lab]
        i = int(np.clip(np.searchsorted(f.t.to_numpy(), t_on + float(ps), side="right") - 1, 0, len(f) - 1))
        lx.append(float(f.x_loom.iloc[i]))
    b["lx"] = lx
    b = b[np.isfinite(b.lx)]
    b["hard"] = (b.own_braking == 2).astype(float)
    # C: study 2, expected vehicle action
    tr2 = pd.read_csv(R.TRIALS, low_memory=False)
    tr2 = tr2[~tr2.video.str.contains("dummy") & tr2.TTC_true.notna() & tr2.CZB_2.isin([0, 1, 2])]
    c2 = pd.read_csv(OUT / "cutin2_cells.csv")
    c2["lx"] = J6.looming_axis(c2)
    c = tr2.merge(c2[["video", "lx", "cp"]], on="video")
    c = c[c.cp != "CP1"].copy()
    c["hard"] = (c.CZB_2 == 2).astype(float)

    res = {}
    for lab, df, keys, pid in (("A", a, ["criticality", "timepoint"], "participant"),
                               ("B", b, ["criticality"], "participant"),
                               ("C", c, ["video"], "Exp_Subject_Id")):
        th = fit(*cells(df, keys))
        res[lab] = (float(np.exp(th[0])), float(np.exp(th[1])), boot(df, keys, pid, rng))
    ratio = np.log(res["A"][0] / res["C"][0])
    verdict = "REPLICATES ON LOOMING" if abs(ratio) < 0.26 else "does NOT replicate on looming"
    L = ["# Card NC.3n -- the hard boundaries in looming", "",
         "Generated by `replication/czb/nc3n_hard_on_looming.py`; pre-stated in its docstring before"
         " the run. Do not edit by hand.", "",
         "| boundary | 50% looming [rad/s] | 95% (participant bootstrap) | spread [log] | times the"
         " intervention level (0.032) | on TTC (cards NC.3m, NC.3l) |", "|---|---|---|---|---|---|"]
    names = {"A": ("study 1, expect THE CAR to brake hard", "3.04 s"),
             "B": ("study 1, would brake hard THEMSELVES (at the press)", "3.29 s"),
             "C": ("study 2, expect THE CAR to brake hard", "1.64 s")}
    for k in ("A", "B", "C"):
        m, s, ci = res[k]
        L.append(f"| {names[k][0]} | **{m:.3f}** | [{ci[0]:.3f}, {ci[1]:.3f}] | {s:.2f} |"
                 f" {m / INT_LEVEL:.1f} | {names[k][1]} |")
    L += ["", f"Study 1 against study 2, the same question: ratio {np.exp(ratio):.2f} (|log ratio|"
          f" {abs(ratio):.2f}; rule 0.26). **{verdict}.** On TTC the same two differ by a ratio of"
          f" {3.04 / 1.64:.2f}.", ""]
    (OUT / "nc3n_hard_on_looming.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
