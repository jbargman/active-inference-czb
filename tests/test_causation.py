"""
Property tests for src/causation, src/quadris, src/equivalence.

Run: python tests/test_causation.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from quadris.load import Seed                                       # noqa: E402
from quadris.metrics import no_return_time, p_inj_mais2             # noqa: E402
from causation import CausationConfig, run_seed                      # noqa: E402
from causation.glances import (standin_shrp2_glances, overshot_distribution,
                               GlanceSchedule, anchored_schedules, process_schedules)  # noqa: E402
from causation.simulate import pre_response, execute_braking         # noqa: E402
from causation.runner import aggregate                               # noqa: E402
from equivalence import theta_Theta, quantile_bin_edges, bin_proportions, equivalence_test  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if bool(cond) else FAIL).append(name)
    print("{}  {}{}".format("PASS" if cond else "FAIL", name, ("  -- " + str(detail)) if detail else ""))


def toy_seed(v_f0=15.0, d0=25.0, v_l0=15.0, brake_at=1.0, a_lead=-6.0, T=6.0):
    t = np.arange(0.0, T + 1e-9, 0.05)
    v_l = np.maximum(v_l0 + np.where(t > brake_at, a_lead * (t - brake_at), 0.0), 0.0)
    x_l = d0 + np.concatenate([[0], np.cumsum(0.5 * (v_l[1:] + v_l[:-1]) * 0.05)])
    # follower constant speed until the file ends (original profile = constant)
    v_f = np.full_like(t, v_f0)
    gap = x_l - v_f0 * t
    return Seed(seed_id=999, weight=1.0, t=t, v_lead=v_l, v_f0=v_f0, d0=d0,
                v_f_orig=v_f, d_orig=gap, lead_delta_v_orig=1.0)


# ------------------------------------------------------------------ glances
def test_glances():
    g = standin_shrp2_glances()
    check("glance distribution sums to 1 (point mass + off-road bins)",
          abs(g.on_road + g.probability.sum() - 1.0) < 1e-9)
    d, o, p = overshot_distribution(g)
    check("overshot joint distribution sums to the off-road mass",
          abs(p.sum() - (1 - g.on_road)) < 1e-9, f"{p.sum():.3f}")
    check("overshoot never exceeds its glance duration", np.all(o <= d + 1e-9))
    # Bärgman App. C: a glance of duration d yields overshoots 0.1..d with equal probability
    m = np.isclose(d, 0.3)
    check("0.3 s glance splits its probability equally over 3 overshoots",
          m.sum() == 3 and np.allclose(p[m], p[m][0]))
    sch = anchored_schedules(g, t_anchor=3.0)
    check("anchored schedules' probabilities sum to 1",
          abs(sum(x.probability for x in sch) - 1.0) < 1e-9)
    s1 = GlanceSchedule([(1.0, 2.0)])
    t = np.arange(0, 3, 0.05)
    check("off-road mask covers exactly the glance", s1.off_road(t).sum() == 20)
    check("evidence gate is 0 during the glance, 1 outside",
          s1.evidence_weight(np.array([1.5]), 0.0)[0] == 0.0 and s1.evidence_weight(np.array([0.5]), 0.0)[0] == 1.0)
    rng = np.random.default_rng(0)
    ps = process_schedules(g, 60.0, 200, None, rng)
    off_share = np.mean([s2.off_road(np.arange(0, 60, 0.05)).mean() for s2 in ps])
    check("renewal process reproduces the off-road time share within 3 points",
          abs(off_share - (1 - g.on_road)) < 0.03, f"{off_share:.3f} vs {1-g.on_road:.3f}")


# ------------------------------------------------------------------ simulation
def test_simulation():
    s = toy_seed()
    pre = pre_response(s, 0.05, 5.0, "constant")
    check("lead onset detected", abs(pre.t_lead_onset - 1.0) < 0.11, pre.t_lead_onset)
    out_none = execute_braking(pre, None, 5.0, -23.0, 0.05)
    check("no response ends in a crash on a braking-lead seed", out_none.crashed)
    out_early = execute_braking(pre, 1.5, 8.0, -23.0, 0.05)
    check("an early hard-braking response avoids the crash", not out_early.crashed,
          f"min gap {out_early.min_gap:.2f}")
    out_late = execute_braking(pre, 3.0, 2.25, -23.0, 0.05)
    check("a late weak response crashes with a lower impact speed than no response",
          out_late.crashed and out_late.v_rel_impact < out_none.v_rel_impact,
          f"{out_late.v_rel_impact:.2f} < {out_none.v_rel_impact:.2f}")
    check("t_nr is negative and finite on the no-response crash",
          no_return_time(out_none.t[:int(out_none.t_impact/0.05)+1],
                         out_none.gap[:int(out_none.t_impact/0.05)+1],
                         out_none.v_f[:int(out_none.t_impact/0.05)+1],
                         pre.v_l[:int(out_none.t_impact/0.05)+1]) < 0)


# ------------------------------------------------------------------ config discipline
def test_config_discipline():
    s = toy_seed()
    base = run_seed(s, CausationConfig())                          # all components at defaults, no glances
    check("all-off config produces one schedule ('attentive')",
          set(r["schedule"] for r in base) == {"attentive"})
    a = run_seed(s, CausationConfig.condition("A"))
    check("condition A equals the all-off config",
          [r["t_onset"] for r in a] == [r["t_onset"] for r in base])
    b = run_seed(s, CausationConfig.condition("B"))
    onsets_b = {r["schedule"]: r["t_onset"] for r in b if r["d_max"] == b[0]["d_max"]}
    check("glances only delay, never advance, the response",
          all(np.isnan(v) or v >= onsets_b.get("no glance", -1) - 1e-9 for k, v in onsets_b.items() if k != "no response"))
    check("longer overshoot -> weakly later onset", all(
        (np.isnan(x) or np.isnan(y) or x <= y + 1e-9) for x, y in zip(
            [v for k, v in sorted(onsets_b.items()) if k.startswith("o=")][:-1],
            [v for k, v in sorted(onsets_b.items()) if k.startswith("o=")][1:])))
    check("condition B carries a no-response record", any(r["no_response"] for r in b))


# ------------------------------------------------------------------ aggregation
def test_aggregation():
    import pandas as pd
    s = toy_seed()
    df = pd.DataFrame(run_seed(s, CausationConfig.condition("B")))
    agg = aggregate(df, no_response_share=0.10)
    resp = agg[(~agg.no_response) & agg.crashed]
    if len(resp):
        check("a seed's responding crash weights sum to its omega",
              abs(resp.w_crash.sum() - s.weight) < 1e-6, resp.w_crash.sum())
    nr = agg[agg.no_response & agg.crashed]
    tot = agg.w_crash.sum()
    if len(nr) and tot > 0:
        check("no-response crashes make up the configured share of total crash weight",
              abs(nr.w_crash.sum() / tot - 0.10) < 1e-6, nr.w_crash.sum() / tot)


# ------------------------------------------------------------------ equivalence
def test_equivalence():
    # the worked example of Wu et al. (2026) Fig. 3
    p_ref = np.array([.20, .20, .20, .20, .20])
    p_syn = np.array([.22, .18, .16, .18, .26])
    omega = np.array([2.0, 0.2, 0.2, 0.5, 0.8])
    th, Th, rel, ab = theta_Theta(p_ref, p_syn, omega)
    check("theta reproduces the paper's worked example (0.24)", abs(th - 0.24) < 1e-9, th)
    check("Theta is the weighted absolute deviation sum", abs(Th - (0.02*2 + 0.02*0.2 + 0.04*0.2 + 0.02*0.5 + 0.06*0.8)) < 1e-9)
    rng = np.random.default_rng(1)
    x = rng.normal(0, 1, 4000)
    edges = quantile_bin_edges(x, 5)
    check("quantile bins hold equal shares", np.allclose(bin_proportions(x, edges), 0.2, atol=0.01))
    same = equivalence_test(x, rng.normal(0, 1, 4000), metric="same", n_bins=5, n_boot=300, rng=2)
    check("identical distributions: theta point estimate is well inside the ROPE",
          same.theta_point < 0.10, f"theta {same.theta_point:.3f}")
    check("bootstrap HDI of the max statistic is conservative (documented, not asserted equivalent)",
          same.theta_hdi[1] > same.theta_point)
    diff = equivalence_test(x, rng.normal(1.0, 1, 4000), metric="shifted", n_bins=5, n_boot=300, rng=3)
    check("a one-sigma shift fails the ROPE", not diff.equivalent)
    check("P_inj is monotone in delta-v and zero for no crash",
          p_inj_mais2(0) == 0 and p_inj_mais2(5) < p_inj_mais2(10))


if __name__ == "__main__":
    for fn in [test_glances, test_simulation, test_config_discipline, test_aggregation, test_equivalence]:
        print("\n--- {} ---".format(fn.__name__))
        fn()
    print("\n{} passed, {} failed".format(len(PASS), len(FAIL)))
    if FAIL:
        print("FAILED:", FAIL)
        sys.exit(1)
