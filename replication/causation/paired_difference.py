"""The B-versus-C ordering as a paired difference (results doc section 4.3b-ii).

The claim "condition B is closer to the reference than condition C" concerns the
difference theta_C - theta_B, not the two marginal intervals. This script is the
committed source for section 4.3b-ii. It runs three analyses:

* **ref-only** -- resample the reference scenarios (shared draw), hold both synthetic
  sides fixed. This reproduces the numbers first produced in-session on 2026-08-26
  without a script ([0.037, 0.107], P = 1.000). It is NOT a complete uncertainty
  statement under either convention: it omits the synthetic-side sampling variance,
  which is independent between the conditions and does not cancel in the difference.
  Kept to document what the original analysis was.
* **population** -- the project's convention (reference fixed): independent synthetic
  resamples per condition, difference of the two. This is the analysis the settled
  conventions actually call for.
* **cases** -- one shared reference draw plus independent synthetic draws per condition:
  the full paired bootstrap under the sample reading.

Verdict as of 2026-08-27: the ordering has P(theta_C > theta_B) ~ 0.96-0.97 under both
complete analyses, with the 95% HDI grazing zero -- strong but not the "same sign on
every resample" originally reported, which was an artifact of the ref-only scheme.

    python replication/causation/paired_difference.py --tag _fullp_abn --n-draws 1000
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))

from causation.runner import aggregate                                     # noqa: E402
from equivalence.binned import quantile_bin_edges, bin_proportions, theta_Theta, uniform_weights  # noqa: E402
from equivalence.test import _hdi                                          # noqa: E402


def load_cond(tag: str, c: str) -> pd.DataFrame:
    df = pd.read_csv(HERE / "out" / f"cond_{c}{tag}.csv")
    cfg = json.loads((HERE / "out" / f"cond_{c}{tag}.json").read_text())["config"]
    agg = aggregate(df,
                    no_response_share=cfg.get("no_response_share", 0.0) if cfg.get("no_response_on") else 0.0,
                    abnormal_share=cfg.get("abnormal_share", 0.0) if cfg.get("abnormal_on") else 0.0)
    return agg[agg.w_crash > 0]


def theta_of(ref, w_ref, syn, w_syn, n_bins):
    edges = quantile_bin_edges(ref, n_bins, w_ref)
    pr = bin_proportions(ref, edges, w_ref)
    ps = bin_proportions(syn, edges, w_syn)
    th, Th, *_ = theta_Theta(pr, ps, uniform_weights(n_bins))
    return th


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="_fullp_abn")
    ap.add_argument("--metric", default="p_inj")
    ap.add_argument("--n-bins", type=int, default=5)
    ap.add_argument("--n-draws", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    ref = pd.read_csv(HERE / "out" / "reference_all.csv")
    r = ref[args.metric].to_numpy()
    wr = ref.omega.to_numpy()

    conds = {}
    for c in ("B", "C"):
        g = load_cond(args.tag, c)
        conds[c] = (g[args.metric].to_numpy(), g.w_crash.to_numpy())
        print(f"condition {c}: n_syn = {len(g)}", flush=True)
    (sB, wB), (sC, wC) = conds["B"], conds["C"]

    th_pt = {c: theta_of(r, wr, s, w, args.n_bins) for c, (s, w) in conds.items()}
    d_pt = th_pt["C"] - th_pt["B"]
    print(f"point estimates: theta_B = {th_pt['B']:.3f}, theta_C = {th_pt['C']:.3f}, "
          f"difference = {d_pt:.3f}\n", flush=True)

    def run(scheme: str) -> np.ndarray:
        rng = np.random.default_rng(args.seed)
        diffs = np.empty(args.n_draws)
        for i in range(args.n_draws):
            if scheme == "ref-only":
                ri = rng.integers(0, len(r), len(r))
                diffs[i] = (theta_of(r[ri], wr[ri], sC, wC, args.n_bins)
                            - theta_of(r[ri], wr[ri], sB, wB, args.n_bins))
            elif scheme == "population":
                bi = rng.integers(0, len(sB), len(sB))
                ci = rng.integers(0, len(sC), len(sC))
                diffs[i] = (theta_of(r, wr, sC[ci], wC[ci], args.n_bins)
                            - theta_of(r, wr, sB[bi], wB[bi], args.n_bins))
            else:  # cases
                ri = rng.integers(0, len(r), len(r))
                bi = rng.integers(0, len(sB), len(sB))
                ci = rng.integers(0, len(sC), len(sC))
                diffs[i] = (theta_of(r[ri], wr[ri], sC[ci], wC[ci], args.n_bins)
                            - theta_of(r[ri], wr[ri], sB[bi], wB[bi], args.n_bins))
        return diffs

    lines = [f"# theta_C - theta_B, metric {args.metric}, N = {args.n_bins}, "
             f"{args.n_draws} draws\n",
             f"Point estimate {d_pt:.3f} (theta_B {th_pt['B']:.3f}, theta_C {th_pt['C']:.3f}).\n",
             "| scheme | mean | 95% HDI | P(theta_C > theta_B) |", "|---|---|---|---|"]
    for scheme in ("ref-only", "population", "cases"):
        d = run(scheme)
        lo, hi = _hdi(d)
        row = (f"| {scheme} | {d.mean():.3f} | [{lo:.3f}, {hi:.3f}] | {(d > 0).mean():.3f} |")
        lines.append(row)
        print(row, flush=True)
    lines.append("\nThe ref-only scheme reproduces the numbers quoted in the results doc "
                 "before 2026-08-27; it omits the synthetic-side variance and overstates "
                 "the certainty of the ordering. The population scheme is the project's "
                 "convention.")

    dest = HERE / "out" / f"summary_paired_difference{args.tag}.md"
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\nwritten to", dest)


if __name__ == "__main__":
    main()
