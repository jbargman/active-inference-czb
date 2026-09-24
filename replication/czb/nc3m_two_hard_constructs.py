"""
Card NC.3m -- the two hard-braking constructs within the same participants: the TTC at which
people say THEY would brake hard, against the TTC at which they expect THE CAR to brake hard.

THE PRE-REGISTRATION. Written 2026-09-25, before this was computed.

WHY. Card NC.3j (first study, button design, own action, "would you brake gently or hard?"): half
say "hard" at TTC 3.3 s at the press. Card NC.3l (second study, frozen clips, "what would you expect
your vehicle to do, assuming you do not intervene?"): half expect hard braking at 1.64 s. Jonas,
2026-09-25: *"can we handle this somehow? Explain it specific in a paper?"* The two numbers come
from different studies, participants, stimulus modes and TTC definitions, so as they stand the gap
could be a study artefact. The first study asked BOTH questions of the SAME 43 participants: the
expected-vehicle-action question in its Random sessions (1-2; clips TTC 4, 6, 8 s frozen at six
timepoints 0.0 to 1.5 s after the onset; `random_cutin_trials().braking_expectation`, 0 nothing,
1 gently, 2 hard) and the own-action question in its Button sessions (3-4; card NC.3j). TTC is
computed the same way in both, gap / closing rate from the clip's `looming_field` (bumper to
bumper) at the response moment (Random: `fit_stage1_looming.build_trials`, gap_m / v_rel; Button:
NC.3j's `presses`).

WHAT IS COMPUTED. (1) Expected hard, Random: cell-level binomial probit of share(expect hard) on
log TTC over the 18 cells (3 clips x 6 timepoints), the 50% TTC. (2) Own hard, Button: NC.3j's fit,
recomputed on the participants present in both designs. (3) The difference own - expected in
log TTC and in seconds, with a participant bootstrap (200) resampling participants JOINTLY in both
designs, so the interval is a within-person comparison. (4) Beside it, NC.3l's second-study 1.64 s:
does the expected-hard boundary replicate across studies?

THE RULE. CONSTRUCT DIFFERENCE if the within-participant interval of own - expected excludes zero
(people put their own hard braking at a longer TTC than the car's necessary hard braking);
NO DIFFERENCE WITHIN PEOPLE if it includes zero (the NC.3j/NC.3l gap is then a study artefact).
The expected-hard boundary REPLICATES if study 1's 50% TTC lies within 0.5 s of study 2's 1.64 s.

PREDICTIONS. Expected hard in study 1 at 1.6 to 2.2 s; own hard 3.3 s; the difference 1.1 to 1.7
s, interval excluding zero: CONSTRUCT DIFFERENCE. Replicates.

Output: replication/czb/out/nc3m_two_hard_constructs.md
Run:    python replication/czb/nc3m_two_hard_constructs.py
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
import fit_stage1_looming as F   # noqa: E402
import nc3j_hard_by_clip as J    # noqa: E402

OUT = HERE / "out"
STUDY2_T50 = 1.64


def fit_cells(lt, k, n):
    def nll(th):
        p = np.clip(norm.cdf((th[0] - lt) / np.exp(th[1])), 1e-9, 1 - 1e-9)
        return -float(np.sum(k * np.log(p) + (n - k) * np.log(1 - p)))
    return minimize(nll, np.array([np.log(2.5), np.log(0.4)]), method="L-BFGS-B").x


def expected_cells(r):
    g = r.groupby(["criticality", "timepoint"]).agg(k=("hard", "sum"), n=("hard", "size"),
                                                     ttc=("ttc", "median"))
    return np.log(g.ttc.to_numpy()), g.k.to_numpy(), g.n.to_numpy(), g


def own_cells(b):
    g = b.groupby("criticality").agg(k=("hard", "sum"), n=("hard", "size"), ttc=("ttc", "median"))
    return np.log(g.ttc.to_numpy()), g.k.to_numpy(), g.n.to_numpy(), g


def main() -> None:
    r = F.build_trials()
    r = r[r.braking_expectation.isin([0, 1, 2]) & (r.v_rel > 0)].copy()
    r["ttc"] = r.gap_m / r.v_rel
    r["hard"] = (r.braking_expectation == 2).astype(float)
    r.attrs = {}
    b = J.presses()
    both = sorted(set(r.participant) & set(b.participant))
    r, b = r[r.participant.isin(both)], b[b.participant.isin(both)]
    te = fit_cells(*expected_cells(r)[:3])
    to = fit_cells(*own_cells(b)[:3])
    diff = to[0] - te[0]
    rng = np.random.default_rng(20260925)
    boots = []
    for _ in range(200):
        pick = rng.choice(both, len(both))
        rr = pd.concat([r[r.participant == p] for p in pick])
        bb = pd.concat([b[b.participant == p] for p in pick])
        e_, o_ = fit_cells(*expected_cells(rr)[:3]), fit_cells(*own_cells(bb)[:3])
        boots.append((e_[0], o_[0], o_[0] - e_[0]))
    boots = np.array(boots)
    ci_d = np.percentile(boots[:, 2], [2.5, 97.5])
    t_e, t_o = float(np.exp(te[0])), float(np.exp(to[0]))
    verdict = "CONSTRUCT DIFFERENCE" if (ci_d[0] > 0 or ci_d[1] < 0) else "NO DIFFERENCE WITHIN PEOPLE"
    replic = abs(t_e - STUDY2_T50) <= 0.5
    _, _, _, ge = expected_cells(r)
    L = ["# Card NC.3m -- the two hard-braking constructs within the same participants", "",
         "Generated by `replication/czb/nc3m_two_hard_constructs.py`; pre-stated in its docstring"
         " before the run. Do not edit by hand.", "",
         f"The first study's {len(both)} participants who answered both questions. Expected vehicle"
         f" action (Random sessions, frozen clips): {len(r):,} responses, {r.hard.mean():.1%} \"hard\"."
         f" Own action (Button sessions, at the press): {len(b):,} presses, {b.hard.mean():.1%} \"hard\".", "",
         "Expected vehicle action by cell:", "",
         "| clip | timepoint | responses | share expecting hard | median TTC [s] |", "|---|---|---|---|---|"]
    for (cl, tp), row in ge.sort_values("ttc").iterrows():
        L.append(f"| {cl} | {tp} | {int(row.n)} | {row.k / row.n:.3f} | {row.ttc:.2f} |")
    L += ["", "| construct | 50% TTC [s] | 95% (participant bootstrap) |", "|---|---|---|",
          f"| expect THE CAR to brake hard (Random) | **{t_e:.2f}** |"
          f" [{np.exp(np.percentile(boots[:, 0], 2.5)):.2f}, {np.exp(np.percentile(boots[:, 0], 97.5)):.2f}] |",
          f"| would brake hard THEMSELVES (Button) | **{t_o:.2f}** |"
          f" [{np.exp(np.percentile(boots[:, 1], 2.5)):.2f}, {np.exp(np.percentile(boots[:, 1], 97.5)):.2f}] |",
          f"| second study, expect the car (card NC.3l) | 1.64 | - |", "",
          f"Own minus expected, within the same participants: {t_o - t_e:+.2f} s; in log TTC"
          f" {diff:+.3f} [{ci_d[0]:+.3f}, {ci_d[1]:+.3f}] (ratio {np.exp(diff):.2f}"
          f" [{np.exp(ci_d[0]):.2f}, {np.exp(ci_d[1]):.2f}]).", "",
          f"**{verdict}.** The expected-hard boundary {'REPLICATES' if replic else 'does NOT replicate'}"
          f" across studies ({t_e:.2f} s against 1.64 s; rule: within 0.5 s).", ""]
    (OUT / "nc3m_two_hard_constructs.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
