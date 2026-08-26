"""Why severity matches while timing and braking do not.

Produces the numbers and figures behind docs/severity_vs_timing.md: per-bin diagnostics
for every metric, the atom structure of the braking distribution, and the sensitivity of
impact severity to response timing.

    python replication/causation/severity_vs_timing.py --tag _fullp_abn

Writes PNGs to docs/causation_figures/ and prints a markdown-ready numbers block.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
from causation.runner import aggregate                                     # noqa: E402
from equivalence.binned import quantile_bin_edges, bin_proportions, theta_Theta, uniform_weights  # noqa: E402

OUT = HERE / "out"
FIGS = REPO / "docs" / "causation_figures"

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, MUTED = "#0b0b0b", "#52514e"
plt.rcParams.update({
    "font.size": 9.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#e4e4e0", "grid.linewidth": 0.6,
    "figure.facecolor": "white", "axes.facecolor": "white", "legend.frameon": False,
})


def load_cond(tag: str, c: str) -> pd.DataFrame:
    df = pd.read_csv(OUT / f"cond_{c}{tag}.csv")
    cfg = json.loads((OUT / f"cond_{c}{tag}.json").read_text())["config"]
    agg = aggregate(df,
                    no_response_share=cfg.get("no_response_share", 0.0) if cfg.get("no_response_on") else 0.0,
                    abnormal_share=cfg.get("abnormal_share", 0.0) if cfg.get("abnormal_on") else 0.0)
    return agg[agg.w_crash > 0]


def wq(x, w, q):
    o = np.argsort(x); x, w = np.asarray(x)[o], np.asarray(w)[o]
    cw = np.cumsum(w) - 0.5 * w
    return np.interp(q, cw / w.sum(), x)


def per_bin(ref, w_ref, syn, w_syn, n_bins):
    e = quantile_bin_edges(ref, n_bins, w_ref)
    pr = bin_proportions(ref, e, w_ref)
    ps = bin_proportions(syn, e, w_syn)
    th, Th, rel, ab = theta_Theta(pr, ps, uniform_weights(n_bins))
    return e, pr, ps, th, Th, rel


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="_fullp_abn")
    ap.add_argument("--bins", type=int, default=5)
    args = ap.parse_args()
    FIGS.mkdir(parents=True, exist_ok=True)

    ref = pd.read_csv(OUT / "reference_all.csv")
    B = load_cond(args.tag, "B")
    wr = ref.omega.to_numpy()
    wb = B.w_crash.to_numpy()

    print("## Structure of the metric set\n")
    # the reference's v_rel is 2*dv_lead by construction and P_inj is a monotone
    # function of dv_lead -- so the three "severity" metrics are one metric.
    from quadris import p_inj_mais2
    recomputed = np.array([p_inj_mais2(v) for v in ref.dv_lead])
    chk = float(np.abs(ref.p_inj.to_numpy() - recomputed).max())
    print(f"reference P_inj vs logistic(dv_lead): max abs difference = {chk:.2e} (identical by construction)")
    print("reference v_rel is defined as 2*dv_lead (equal-mass assumption), so P_inj, v_rel")
    print("and dv_lead are three monotone transforms of ONE number and share every bin.\n")

    metrics = {
        "severity: v_rel [m/s]": (2.0 * ref.dv_lead.to_numpy(), B.v_rel_impact.to_numpy()),
        "urgency: t_nr [s]":     (ref.t_nr.to_numpy(), B.t_nr.to_numpy()),
        "lead brake: a_l,min":   (ref.a_l_min.to_numpy(), B.a_l_min.to_numpy()),
        "follower brake: a_f,min": (ref.a_f_min.to_numpy(), B.a_f_min.to_numpy()),
    }

    print("## Per-bin diagnostics (N = %d, Eq. 10 weights)\n" % args.bins)
    store = {}
    for name, (r, s) in metrics.items():
        m = np.isfinite(r); r2, w2 = r[m], wr[m]
        m2 = np.isfinite(s); s2, ws2 = s[m2], wb[m2]
        e, pr, ps, th, Th, rel = per_bin(r2, w2, s2, ws2, args.bins)
        store[name] = (e, pr, ps, th, Th, r2, w2, s2, ws2)
        print(f"### {name}:  theta = {th:.3f}, Theta = {Th:.3f}")
        print("| bin | edges | P_ref | P_syn | |dP|/P_ref |")
        print("|---|---|---|---|---|")
        for i in range(args.bins):
            lo = "-inf" if not np.isfinite(e[i]) else f"{e[i]:.3g}"
            hi = "+inf" if not np.isfinite(e[i + 1]) else f"{e[i + 1]:.3g}"
            print(f"| {i+1} | {lo} .. {hi} | {pr[i]:.3f} | {ps[i]:.3f} | {rel[i]:.3f} |")
        print()

    # ---- the braking atom -------------------------------------------------
    print("## The braking distribution is an atom plus a tail\n")
    for lbl, x, w in (("QUADRIS reference", ref.a_f_min.to_numpy(), wr),
                      ("condition B", B.a_f_min.to_numpy(), wb)):
        m = np.isfinite(x); x, w = x[m], w[m]
        share = float(w[x > -0.5].sum() / w.sum())
        print(f"{lbl:20s}: weighted share with a_f,min > -0.5 m/s2 (essentially no braking) = {share:.3f}")
    e = store["follower brake: a_f,min"][0]
    print(f"\nquantile bin edges for a_f,min: {[('-inf' if not np.isfinite(v) else round(float(v),3)) for v in e]}")
    dup = len(set(np.round(e[1:-1].astype(float), 6))) < len(e[1:-1])
    print(f"inner edges collapse onto repeated values: {dup}")
    print("  (a large atom cannot be split by quantiles, so bins straddling it are degenerate)\n")

    # ---- does timing move severity? ---------------------------------------
    print("## Sensitivity of severity to response timing (condition B)\n")
    r = B[np.isfinite(B.rt_vs_anchor) & np.isfinite(B.v_rel_impact)]
    qs = np.arange(0, 1.01, 0.2)
    cut = wq(r.rt_vs_anchor.to_numpy(), r.w_crash.to_numpy(), qs)
    print("| onset delay vs anchor [s] | weighted median v_rel [m/s] | mean P_inj |")
    print("|---|---|---|")
    for i in range(len(cut) - 1):
        m = (r.rt_vs_anchor >= cut[i]) & (r.rt_vs_anchor < cut[i + 1] if i < len(cut) - 2 else r.rt_vs_anchor <= cut[i + 1])
        if m.sum() < 10:
            continue
        g = r[m]
        print(f"| {cut[i]:.2f} .. {cut[i+1]:.2f} | {wq(g.v_rel_impact.to_numpy(), g.w_crash.to_numpy(), [0.5])[0]:.2f} "
              f"| {float((g.p_inj*g.w_crash).sum()/g.w_crash.sum()):.4f} |")
    # how much of v_rel variance is seed vs timing
    grp = r.groupby("seed_id").v_rel_impact
    between = grp.mean().var()
    within = r.v_rel_impact.var() - between
    print(f"\nvariance of v_rel_impact: between-seed {between:.3f}, within-seed (timing/draws) {within:.3f}"
          f"  -> between-seed share {between/(between+within):.3f}")

    # ---- figures ----------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(9.6, 6.4))
    for ax, (name, (e, pr, ps, th, Th, r2, w2, s2, ws2)) in zip(axes.ravel(), store.items()):
        lo = np.nanpercentile(np.concatenate([r2, s2]), 1)
        hi = np.nanpercentile(np.concatenate([r2, s2]), 99)
        bins = np.linspace(lo, hi, 60)
        ax.hist(r2, bins=bins, weights=w2 / w2.sum(), color=MUTED, alpha=.45, label="QUADRIS reference")
        ax.hist(s2, bins=bins, weights=ws2 / ws2.sum(),
                histtype="step", lw=1.8, color=BLUE, label="condition B")
        for v in e[1:-1]:
            ax.axvline(float(v), color=ORANGE, lw=.8, ls=":")
        ax.set_title(f"{name}   $\\theta$={th:.3f}", fontsize=9.5)
        ax.set_ylabel("weighted share")
    axes[0, 0].legend(fontsize=8.5)
    fig.suptitle("Weighted distributions with the reference's quantile bin edges (dotted)", fontsize=10.5)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_severity_vs_timing.png", dpi=170)
    print("\nwrote", FIGS / "fig_severity_vs_timing.png")


if __name__ == "__main__":
    main()
