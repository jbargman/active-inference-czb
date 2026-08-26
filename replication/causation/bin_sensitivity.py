"""Bin-count sensitivity for the Wu et al. (2026) equivalence readout.

The full-population assessment was run with N = 5 quantile bins, which is the value the
bin rule (Eq. 4) gives for a 100-200 seed reference -- the size the study had when
`run_quadris.assess` was written. At the full population (n_ref = 5 000) the same rule
gives N = min(floor(5000/40), 20) = 20. theta is a worst-bin statistic and therefore gets
strictly harsher as bins get finer, so the reported numbers sit on the lenient side of the
paper's own prescription. This script re-runs the readout at N in {5, 10, 20} from the
stored condition CSVs (no re-simulation) so the choice can be stated with a number.

The result is that N = 20 is prescribed but unusable at this reference size: the null
calibration in docs/equivalence_rope_note.md section 2.1 shows that a model which is
exactly right has median theta 0.129 and a 95% HDI upper bound of 0.266 at N = 20, so no
model can pass a ROPE of 0.10 there.

Usage:
    python replication/causation/bin_sensitivity.py --tag _fullp_abn --conditions B C
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from causation import CausationConfig                      # noqa: E402
from causation.runner import aggregate                     # noqa: E402
from equivalence import MetricSpec, run_metric_suite       # noqa: E402
from equivalence.binned import n_bins_rule                 # noqa: E402

OUT = REPO / "replication" / "causation" / "out"

METRICS = ["P_inj", "v_rel [m/s]", "t_nr [s]", "a_l,min [m/s^2]", "a_f,min [m/s^2]"]


def specs_for(ref: pd.DataFrame, g: pd.DataFrame) -> list[MetricSpec]:
    wr, ws = ref.omega.to_numpy(), g.w_crash.to_numpy()
    return [MetricSpec("P_inj", ref.p_inj.to_numpy(), g.p_inj.to_numpy(), wr, ws),
            MetricSpec("v_rel [m/s]", 2.0 * ref.dv_lead.to_numpy(), g.v_rel_impact.to_numpy(), wr, ws),
            MetricSpec("t_nr [s]", ref.t_nr.to_numpy(), g.t_nr.to_numpy(), wr, ws),
            MetricSpec("a_l,min [m/s^2]", ref.a_l_min.to_numpy(), g.a_l_min.to_numpy(), wr, ws),
            MetricSpec("a_f,min [m/s^2]", ref.a_f_min.to_numpy(), g.a_f_min.to_numpy(), wr, ws)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="_fullp_abn")
    ap.add_argument("--conditions", nargs="*", default=["B", "C"])
    ap.add_argument("--bins", nargs="*", type=int, default=[5, 10, 20])
    ap.add_argument("--abnormal", action="store_true", default=True)
    ap.add_argument("--n-boot", type=int, default=1000)
    args = ap.parse_args()

    ref = pd.read_csv(OUT / "reference_all.csv")
    print("reference: {} scenarios; Wu Eq. 4 bin rule gives N = {}".format(
        len(ref), n_bins_rule(len(ref))), flush=True)

    lines = ["# Bin-count sensitivity of the equivalence readout\n",
             "Reference n = {}. Wu et al. (2026) Eq. 4 gives N = {} at this size; the".format(
                 len(ref), n_bins_rule(len(ref))),
             "full-population tables were produced with N = 5. Both statistics tighten with",
             "finer bins: theta because it is a worst-bin maximum, Theta because it is a",
             "lower bound on twice the total-variation distance that becomes exact only as",
             "the partition is refined. Note also that theta is a maximum over bins and is",
             "therefore biased upward under resampling, so its bootstrap HDI can sit above",
             "the point estimate; the bias grows with N.\n"]

    for c in args.conditions:
        path = OUT / "cond_{}{}.csv".format(c, args.tag)
        if not path.exists():
            print("missing {} -- skipping".format(path.name), flush=True)
            continue
        print("loading {} ...".format(path.name), flush=True)
        df = pd.read_csv(path)
        cfg = CausationConfig.condition(c, abnormal_on=args.abnormal)
        agg = aggregate(df, no_response_share=cfg.no_response_share if cfg.no_response_on else 0.0,
                        abnormal_share=cfg.abnormal_share if cfg.abnormal_on else 0.0)
        g = agg[agg.w_crash > 0]

        lines.append("\n## Condition {} ({}), n_syn = {}\n".format(c, cfg.response_model, len(g)))
        lines.append("| metric | " + " | ".join("N={} theta".format(n) for n in args.bins)
                     + " | " + " | ".join("N={} Theta".format(n) for n in args.bins) + " |")
        lines.append("|---" * (1 + 2 * len(args.bins)) + "|")

        per_bin: dict[int, object] = {}
        for n in args.bins:
            print("  condition {}: N = {} ...".format(c, n), flush=True)
            res = run_metric_suite(specs_for(ref, g), n_bins=n, n_boot=args.n_boot)
            per_bin[n] = res

        for m in METRICS:
            th = ["{:.3f} [{:.3f}, {:.3f}]".format(per_bin[n][m].theta_point,
                                                   *per_bin[n][m].theta_hdi) for n in args.bins]
            Th = ["{:.3f}".format(per_bin[n][m].Theta_point) for n in args.bins]
            lines.append("| {} | {} | {} |".format(m, " | ".join(th), " | ".join(Th)))

    txt = "\n".join(lines) + "\n"
    dest = OUT / "summary_bin_sensitivity{}.md".format(args.tag)
    dest.write_text(txt, encoding="utf-8")
    print("\n" + txt)
    print("written to", dest)


if __name__ == "__main__":
    main()
