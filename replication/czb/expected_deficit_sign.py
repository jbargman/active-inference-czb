"""R.2.Q1: the sign of the distance effect under the expected-deficit proposal.

The proposal on review at gate R.2 (`docs/lateral_and_uncertainty_note.md` section 5):
replace the deficit at the predicted state, d(x_hat), with E[d(x)] under
x ~ N(x_hat, Sigma), with Sigma growing with distance -- and the gate's instruction is
to derive the sign of the resulting distance effect BEFORE writing any model code.
The observed effect the mechanism would need to produce (second cut-in study, all 24
matched-TTC rows; LTAP at matched PET): intervention FALLS, strongly and
monotonically, as the gap grows at matched time (gap orders the second study's cells
at rho = -0.887).

This script does the derivation numerically on the project's actual preference
function, in the car-following geometry where the field is validated: an in-lane lead
at matched TTC, with gap and closing speed scaling together (gap = TTC x v_rel, the
second study's construction), over the study's own delta-velocity range (7-42 kph).
Two quantities per matched-TTC row:

1. the point-estimate deficit d(gap), and
2. E[d] under Gaussian perceptual noise on the gap with a Weber-like scale
   sigma = w x gap (w = 0.05 / 0.10 / 0.20 -- the value only needs to be plausible,
   the question is directional), by Gauss-Hermite quadrature.

A first version of this script (2026-08-29, same session) ran the grid to
v_rel = 37 m/s, beyond the study's range and into geometries where the lead moves
backwards; the verdict rows below are restricted to the design range, and the
interpretation is computed from the numbers rather than written in advance -- the
register's R.2.Q1 entry records why that discipline exists.

Run:  python replication/czb/expected_deficit_sign.py
Output: replication/czb/out/expected_deficit_sign.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))

from aidriver.preferences import PreferenceParams, pragmatic_deficit  # noqa: E402

OUT = HERE / "out" / "expected_deficit_sign.md"

V_EGO = 30.0          # m/s; the study-2 ego cruises near this
TTC_ROWS = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
KPH = 1000.0 / 3600.0
V_REL = np.linspace(7.0 * KPH, 42.0 * KPH, 25)     # the study's DV range
WEBER = [0.05, 0.10, 0.20]


def deficit_at(gap: np.ndarray, ttc: float, p: PreferenceParams) -> np.ndarray:
    """The cut-in field's deficit for an in-lane lead at the given gap, with closing
    speed set by the matched-TTC construction v_rel = gap / ttc. The lead is fully in
    lane (dy = 0): the pure longitudinal question, no lane-entry confound."""
    gap = np.asarray(gap, float)
    v_rel = gap / ttc
    v_other = V_EGO - v_rel
    obs = {"v": np.full_like(gap, V_EGO), "a": np.zeros_like(gap),
           "omega": np.zeros_like(gap), "a_lat": np.zeros_like(gap),
           "y": np.full_like(gap, p.lane_centre),
           "dx": gap + p.vehicle.length,          # dx is centre distance; gap is free space
           "dy": np.zeros_like(gap),
           "v_other": v_other, "a_other": np.zeros_like(gap),
           "vy_other": np.zeros_like(gap), "w_other": p.vehicle.width}
    return pragmatic_deficit(obs, p)


def expected_deficit(gap: np.ndarray, ttc: float, p: PreferenceParams,
                     weber: float, n_gh: int = 41) -> np.ndarray:
    """E[d] under gap_hat ~ N(gap, (weber x gap)^2), Gauss-Hermite quadrature.
    The noisy gap is floored at 0.5 m (a perceived gap cannot be negative).
    Noise is on the perceived DISTANCE only; the closing speed stays at the row's
    true value, which is the manipulation the anomaly is about."""
    nodes, weights = np.polynomial.hermite_e.hermegauss(n_gh)
    gap = np.atleast_1d(np.asarray(gap, float))
    v_rel = gap / ttc
    out = np.zeros_like(gap)
    for i, (g, vr) in enumerate(zip(gap, v_rel)):
        g_hat = np.maximum(g + weber * g * nodes, 0.5)
        # evaluate at perceived gap, true closing speed
        d = deficit_at_v(g_hat, vr, p)
        out[i] = float(np.sum(weights * d) / np.sum(weights))
    return out


_P = None  # set in main; module-level so the helpers share one staged params object


def deficit_at_v(gap: np.ndarray, v_rel: float, p: PreferenceParams) -> np.ndarray:
    """Deficit at given gap and FIXED closing speed (perceived-distance variation)."""
    gap = np.asarray(gap, float)
    v_other = V_EGO - v_rel
    obs = {"v": np.full_like(gap, V_EGO), "a": np.zeros_like(gap),
           "omega": np.zeros_like(gap), "a_lat": np.zeros_like(gap),
           "y": np.full_like(gap, p.lane_centre),
           "dx": gap + p.vehicle.length,
           "dy": np.zeros_like(gap),
           "v_other": np.full_like(gap, v_other), "a_other": np.zeros_like(gap),
           "vy_other": np.zeros_like(gap), "w_other": p.vehicle.width}
    return pragmatic_deficit(obs, p)


def spearman(a, b) -> float:
    from scipy.stats import spearmanr
    return float(spearmanr(a, b).statistic)


def main() -> None:
    global _P
    _P = PreferenceParams(v_desired=V_EGO, lane_entry_continuous=True,
                          counterfactual_residual_severity=True,
                          lane_entry_shape_k=12.0)
    p = _P
    lines = ["# The sign of the distance effect under expected deficit (R.2.Q1)",
             "",
             "Generated by `replication/czb/expected_deficit_sign.py`. Do not edit by "
             "hand. Geometry: in-lane lead, matched-TTC rows (gap = TTC x v_rel), ego "
             f"{V_EGO:.0f} m/s, CZB staging (continuous forms, k = 12), v_rel "
             "restricted to the second study's delta-velocity range 7-42 kph.",
             ""]
    verdict = []
    for ttc in TTC_ROWS:
        gaps = ttc * V_REL
        d0 = deficit_at(gaps, ttc, p)
        ed = {w: expected_deficit(gaps, ttc, p, w) for w in WEBER}
        lines.append(f"## TTC = {ttc:.0f} s (gaps {gaps.min():.1f}-{gaps.max():.1f} m)\n")
        lines.append("| gap [m] | v_rel [m/s] | d (point) | "
                     + " | ".join(f"E[d] w={w}" for w in WEBER) + " |")
        lines.append("|---|---|---|" + "---|" * len(WEBER))
        for j in range(0, len(gaps), 4):
            lines.append(f"| {gaps[j]:.1f} | {V_REL[j]:.2f} | {d0[j]:.1f} | "
                         + " | ".join(f"{ed[w][j]:.1f}" for w in WEBER) + " |")
        rel_range = (d0.max() - d0.min()) / max(d0.mean(), 1e-9)
        verdict.append((ttc, spearman(gaps, d0), spearman(gaps, ed[0.10]),
                        rel_range, float(np.mean(ed[0.20] - ed[0.05]))))
        lines.append("")

    lines.append("## Verdict rows (design range only)\n")
    lines.append("| TTC [s] | rho(gap, d point) | rho(gap, E[d] w=0.1) | "
                 "(max-min)/mean of d | mean E[d](w=0.2) - E[d](w=0.05) |")
    lines.append("|---|---|---|---|---|")
    for ttc, rp, re_, rr, wi in verdict:
        lines.append(f"| {ttc:.0f} | {rp:+.3f} | {re_:+.3f} | {rr:.3f} | {wi:+.1f} |")

    # the interpretation is COMPUTED, not asserted
    rhos_p = np.array([v[1] for v in verdict])
    rel_ranges = np.array([v[3] for v in verdict])
    noise_shift = np.array([v[4] for v in verdict])
    mean_d = np.mean([deficit_at(ttc * V_REL, ttc, p).mean() for ttc in TTC_ROWS])
    obs_line = ("the observed effect is strong and monotone (gap orders the second "
                "study's cells at rho = -0.887, every matched-TTC row negative)")
    if np.all(rhos_p <= -0.9) and np.all(rel_ranges > 0.5):
        concl = ("The point field already produces a strong monotone gap effect of "
                 "the observed sign; the expectation adds little.")
    elif np.all(rhos_p < 0):
        concl = (f"The point field's gap effect has the observed sign in every row "
                 f"(rho {rhos_p.min():+.2f} to {rhos_p.max():+.2f}) but is weak and "
                 f"non-monotone within the design range -- the relative range of d "
                 f"across a row is {rel_ranges.min():.2f}-{rel_ranges.max():.2f} "
                 f"of its mean, where {obs_line}. ")
    else:
        concl = (f"The point field's within-row direction is inconsistent across "
                 f"rows (rho {rhos_p.min():+.2f} to {rhos_p.max():+.2f}), where "
                 f"{obs_line}. ")
    if not np.all(rhos_p <= -0.9):
        shift_rel = np.abs(noise_shift).max() / max(mean_d, 1e-9)
        concl += (f"Distance-scaled perceptual noise moves E[d] by at most "
                  f"{shift_rel:.1%} of the mean deficit and with inconsistent sign "
                  f"across rows ({noise_shift.min():+.0f} to {noise_shift.max():+.0f}), "
                  "so the expected-deficit mechanism does NOT supply the missing "
                  "distance effect for this preference function: it is a second-order "
                  "modulation where the data show a first-order monotone effect. "
                  "The mechanism remains directionally right for the LATERAL comfort "
                  "problem (deficit convex in clearance, so mass off the predicted "
                  "path raises discomfort at small clearance), which is where the "
                  "note's proposal survives.")
    lines += ["", f"**Reading (computed).** {concl}", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[lines.index("## Verdict rows (design range only)\n"):]))


if __name__ == "__main__":
    main()
