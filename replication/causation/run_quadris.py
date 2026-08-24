"""
Tier-1 crash generation on QUADRIS seeds, conditions A-D, and the equivalence assessment.

    python replication/causation/run_quadris.py --n-seeds 100 --conditions A B C D
    python replication/causation/run_quadris.py --n-seeds 100 --assess-only

Outputs in replication/causation/out/:
    seeds_<n>.csv                the sampled seeds (id, weight, v_f0, d0)
    cond_<X>.csv / .json         per-record outcomes and the full configuration
    summary.md                   crash rates, avoided shares, equivalence tables
Restartable: conditions append per seed and skip seeds already done.

Assessment (src/equivalence): reference = the sampled seeds' own QUADRIS outcomes
(delta-v of the lead as in the CSV -> P_inj; t_nr, a_l,min, a_f,min from the time series);
synthetic = the generated crashes weighted by Wu et al. (2026) Eq. 10, and, as a second
variant, by the exposure weights of docs/crash_causation_plan.md section 6b (omega_i divided
by the seed's crash probability under condition C).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from quadris import load_synthetic, sample_seeds, p_inj_mais2, no_return_time, min_accel   # noqa: E402
from causation import CausationConfig, run_condition                                      # noqa: E402
from causation.runner import aggregate                                                    # noqa: E402
from equivalence import MetricSpec, run_metric_suite, results_table                       # noqa: E402
from equivalence.report import per_bin_table                                              # noqa: E402

OUT = REPO / "replication" / "causation" / "out"


def reference_metrics(seeds) -> pd.DataFrame:
    rows = []
    for s in seeds:
        dv = s.lead_delta_v_orig
        rows.append(dict(seed_id=s.seed_id, omega=s.weight, v_f0=s.v_f0, dv_lead=dv, p_inj=p_inj_mais2(dv),
                         t_nr=no_return_time(s.t, s.d_orig, s.v_f_orig, s.v_lead),
                         a_l_min=min_accel(s.t, s.v_lead), a_f_min=min_accel(s.t, s.v_f_orig)))
    return pd.DataFrame(rows)


def assess(ref: pd.DataFrame, gen: pd.DataFrame, label: str, n_bins: int = 5) -> str:
    g = gen[gen.w_crash > 0]
    specs = [MetricSpec("P_inj", ref.p_inj.to_numpy(), g.p_inj.to_numpy(), ref.omega.to_numpy(), g.w_crash.to_numpy()),
             MetricSpec("dv_lead [m/s]", ref.dv_lead.to_numpy(), g.dv_lead.to_numpy(), ref.omega.to_numpy(), g.w_crash.to_numpy()),
             MetricSpec("t_nr [s]", ref.t_nr.to_numpy(), g.t_nr.to_numpy(), ref.omega.to_numpy(), g.w_crash.to_numpy()),
             MetricSpec("a_l,min [m/s^2]", ref.a_l_min.to_numpy(), g.a_l_min.to_numpy(), ref.omega.to_numpy(), g.w_crash.to_numpy()),
             MetricSpec("a_f,min [m/s^2]", ref.a_f_min.to_numpy(), g.a_f_min.to_numpy(), ref.omega.to_numpy(), g.w_crash.to_numpy())]
    res = run_metric_suite(specs, n_bins=n_bins, n_boot=1000)
    txt = results_table(res, label)
    txt += "\n\nPer-bin diagnostics, P_inj:\n\n" + per_bin_table(res["P_inj"])
    return txt


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-seeds", type=int, default=100)
    ap.add_argument("--conditions", nargs="*", default=list("ABCD"))
    ap.add_argument("--assess-only", action="store_true")
    ap.add_argument("--pre-response", default="original", choices=["original", "constant"])
    ap.add_argument("--rng", type=int, default=0)
    ap.add_argument("--ref", default="all", choices=["all", "sample"])
    # glance-anchor sensitivity (docs/crash_causation_plan.md section 6c): rerun a condition
    # with the glance placement changed; outputs get "_<tag>" appended so the default runs
    # are never overwritten
    ap.add_argument("--glance-anchor", default=None, choices=["tau_inv", "lead_onset", "crash", "process"])
    ap.add_argument("--tag", default="", help="suffix for cond_<X> output files and summary.md")
    # real distributions digitized from Bärgman et al. (2024) Figs. 1 and 3
    # (replication/causation/digitize_b24.py); default remains the labelled stand-ins
    ap.add_argument("--glance-csv", default=None, help="CSV for GlanceDistribution.from_csv")
    ap.add_argument("--decel-csv", default=None, help="CSV for DecelerationDistribution.from_csv")
    args = ap.parse_args()
    tag = ("_" + args.tag) if args.tag else ""
    OUT.mkdir(parents=True, exist_ok=True)

    all_seeds = load_synthetic()
    seeds = sample_seeds(all_seeds, args.n_seeds, rng=args.rng)
    pd.DataFrame([dict(seed_id=s.seed_id, omega=s.weight, v_f0=s.v_f0, d0=s.d0, t_crash=s.t_crash_orig,
                       dv_lead_orig=s.lead_delta_v_orig) for s in seeds]).to_csv(OUT / "seeds_{}.csv".format(args.n_seeds), index=False)
    # the reference costs no simulation: use every QUADRIS scenario unless told otherwise
    ref_path = OUT / "reference_all.csv"
    if args.ref == "all":
        if ref_path.exists():
            ref = pd.read_csv(ref_path)
        else:
            print("computing reference metrics for all {} scenarios ...".format(len(all_seeds)), flush=True)
            ref = reference_metrics(all_seeds)
            ref.to_csv(ref_path, index=False)
    else:
        ref = reference_metrics(seeds)

    results = {}
    for c in args.conditions:
        overrides = dict(pre_response_speed=args.pre_response, seed=args.rng)
        if args.glance_anchor is not None:
            overrides["glance_anchor"] = args.glance_anchor
        if args.glance_csv is not None:
            overrides["glance_distribution"] = args.glance_csv
        if args.decel_csv is not None:
            overrides["decel_distribution"] = args.decel_csv
        cfg = CausationConfig.condition(c, **overrides)
        path = OUT / "cond_{}{}.csv".format(c, tag)
        if not args.assess_only:
            print("condition", c, "...", flush=True)
            df = run_condition(seeds, cfg, path, label="condition {}".format(c))
        else:
            df = pd.read_csv(path)
        results[c] = (cfg, df)

    lines = ["# Tier-1 results: {} seeds, pre-response = {}{}\n".format(
                 args.n_seeds, args.pre_response,
                 ", glance anchor = {}".format(args.glance_anchor) if args.glance_anchor else ""),
             "Generated {}. Distributions: glances and decelerations are STAND-INS unless the .json says otherwise.\n".format(pd.Timestamp.now().date())]
    # exposure: crash probability per seed under condition C if available
    pc_C = None
    if "C" in results:
        dC = aggregate(results["C"][1], 0.0)
        pc_C = dC.groupby("seed_id").p_crash_seed.first()
    lines.append("| condition | response | components | seeds crashing (any bin) | weighted crash prob | avoided seeds | mean P_inj (Eq.10 weights) | mean P_inj reference |")
    lines.append("|---|---|---|---|---|---|---|---|")
    ref_pinj = float((ref.p_inj * ref.omega).sum() / ref.omega.sum())
    for c, (cfg, df) in results.items():
        agg = aggregate(df, cfg.no_response_share if cfg.no_response_on else 0.0)
        pc = agg.groupby("seed_id").p_crash_seed.first()
        resp = agg[~agg.no_response]
        w_pinj = float((agg.p_inj * agg.w_crash).sum() / max(agg.w_crash.sum(), 1e-12))
        lines.append("| {} | {} | {} | {}/{} | {:.3f} | {} | {:.3f} | {:.3f} |".format(
            c, cfg.response_model, ",".join(cfg.describe()["components_enabled"]) or "none",
            int((pc > 0).sum()), len(pc), float((pc * ref.set_index("seed_id").omega.reindex(pc.index)).sum() / ref.omega.sum()),
            int((pc == 0).sum()), w_pinj, ref_pinj))
        # attentive response-time summary
        att = resp[resp.schedule.str.startswith("attentive") | (resp.schedule == "no glance")]
        if len(att):
            lines.append("\n  condition {}: attentive onset relative to the tau^-1 = 0.2 anchor, median {:.2f} s (IQR {:.2f}–{:.2f}); seeds with no attentive response: {}".format(
                c, att.rt_vs_anchor.median(), att.rt_vs_anchor.quantile(.25), att.rt_vs_anchor.quantile(.75), int(att.groupby("seed_id").t_onset.first().isna().sum())))
    lines.append("")
    for c, (cfg, df) in results.items():
        agg = aggregate(df, cfg.no_response_share if cfg.no_response_on else 0.0)
        if (agg.w_crash > 0).sum() < 10:
            lines.append("\nCondition {}: fewer than 10 crash records; no equivalence test.\n".format(c)); continue
        lines.append("\n" + assess(ref, agg, "Condition {} vs reference (Wu Eq. 10 weights)".format(c)))
        if pc_C is not None and c != "C":
            agg_e = aggregate(df, cfg.no_response_share if cfg.no_response_on else 0.0, exposure_pc=pc_C)
            if (agg_e.w_crash > 0).sum() >= 10:
                lines.append("\n" + assess(ref, agg_e, "Condition {} vs reference (exposure weights, omega / p_c under C)".format(c)))
    (OUT / "summary{}.md".format(tag)).write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
