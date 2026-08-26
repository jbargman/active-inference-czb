"""Tabular summary of equivalence results (markdown)."""
from __future__ import annotations

from .test import EquivalenceResult


def results_table(results: dict[str, EquivalenceResult], title: str = "") -> str:
    lines = []
    if title:
        lines.append("**{}**\n".format(title))
    lines.append("| metric | stat | ROPE | point | 95% HDI | equivalent | n_ref / n_syn | bins |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for name, r in results.items():
        lines.append("| {} | θ | [0, {:.3f}] | {:.3f} | [{:.3f}, {:.3f}] | {} | {} / {} | {} |".format(
            name, r.rope_theta, r.theta_point, *r.theta_hdi, "yes" if r.theta_equivalent else "no",
            r.n_ref, r.n_syn, r.n_bins))
        lines.append("| | Θ | [0, {:.3f}] | {:.3f} | [{:.3f}, {:.3f}] | {} | | |".format(
            r.rope_Theta, r.Theta_point, *r.Theta_hdi, "yes" if r.Theta_equivalent else "no"))
    anyr = next(iter(results.values()), None)
    if anyr is not None:
        lines.append("\nUncertainty: {}.".format(anyr.uncertainty))
    return "\n".join(lines)


def aggregate_table(results: dict[str, EquivalenceResult], title: str = "") -> str:
    """Weighted aggregates reported alongside the equivalence verdict.

    theta and Theta constrain only the between-bin allocation. They cannot bound the error
    in a weighted aggregate, because a model can match every bin proportion exactly and
    still differ within bins -- and the outer bins are open-ended, so the top bin is
    unbounded above. The "binned" column is the bin-constant approximation, which is the
    only quantity Theta actually controls; where it diverges from the actual column, the
    difference is within-bin and invisible to both statistics.
    """
    lines = []
    if title:
        lines.append("**Weighted aggregates — {}**\n".format(title))
    lines.append("| metric | reference mean | synthetic mean | rel. error | binned approx. | rel. error (binned) |")
    lines.append("|---|---|---|---|---|---|")
    for name, r in results.items():
        lines.append("| {} | {:.5g} | {:.5g} | {:+.1%} | {:.5g} | {:+.1%} |".format(
            name, r.mean_ref, r.mean_syn, r.mean_rel_error,
            r.mean_syn_binned, r.mean_rel_error_binned))
    lines.append("\nθ and Θ bound only the between-bin allocation; a gap between the two "
                 "relative-error columns is within-bin and is invisible to them.")
    return "\n".join(lines)


def per_bin_table(r: EquivalenceResult) -> str:
    lines = ["| bin | edges | P_ref | P_syn | ω | \\|ΔP/P_ref\\|·ω | \\|ΔP\\|·ω |", "|---|---|---|---|---|---|---|"]
    for i in range(r.n_bins):
        lo, hi = r.edges[i], r.edges[i + 1]
        lines.append("| {} | {:.3g} – {:.3g} | {:.3f} | {:.3f} | {:.2f} | {:.3f} | {:.3f} |".format(
            i + 1, lo, hi, r.p_ref[i], r.p_syn[i], r.omega[i], r.per_bin_rel[i], r.per_bin_abs[i]))
    return "\n".join(lines)
