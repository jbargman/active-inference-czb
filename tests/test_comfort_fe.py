"""
Property tests for the comfort-zone boundary as a free energy of the present observation
(src/rollout/comfort_fe.py, card JJ.10).

Claims: the excess is zero at and below the level and quadratic in log looming above it; P(lead)
is card G.1's gate with s_l = sigma T (identity with `cutin2_gate.gate` at G.1's values) and is 0
for a vehicle moving away and 1 for one already in the path; F is the product and is zero when
either factor is; the mixture response is the gated looming rule of card G.1 (identity with its
`predict_gated` at the same parameters); the expected-looming response is a different function
that agrees with the mixture where the gate is 1 and is lower where the gate is open partway;
both responses lie in [lapse, 1].

Run: python tests/test_comfort_fe.py
"""
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "replication" / "czb"))

from rollout.comfort_fe import (SIGMA_LAT, T_ANTICIPATION, comfort_free_energy,  # noqa: E402
                                expected_looming, looming_excess, p_lead,
                                p_respond_expected, p_respond_mixture)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS  " if cond else "FAIL  ") + name + (f"  -- {detail}" if detail else ""))


def main():
    td = np.array([0.005, 0.03, 0.05, 0.2, 1.0])
    ex = looming_excess(td, 0.05, 0.5)
    check("the excess is zero at and below the level and quadratic in log looming above it",
          np.all(ex[:3] == 0.0) and np.isclose(ex[3], 0.5 * (np.log(4.0) / 0.5) ** 2))

    import cutin2_gate as CG
    l0 = np.array([1.6, 1.2, 0.3, -0.5, 1.6])
    ldot = np.array([0.0, -0.4, -0.8, -1.2, +0.5])
    g = p_lead(l0, ldot, SIGMA_LAT, T_ANTICIPATION, margin_m=0.149)
    g1 = CG.gate(0.149, np.log(0.99), l0, ldot)
    check("P(lead) with the margin is card G.1's gate exactly (s_l = sigma T)",
          np.allclose(g, g1, atol=1e-12), f"max diff {np.max(np.abs(g - g1)):.1e}")
    check("a vehicle moving away is (almost) never a lead; one already in the path always is",
          p_lead(1.6, +0.5) < 1e-3 and p_lead(-0.5, -1.2) > 0.999)

    F = comfort_free_energy(td, np.full(5, 0.5), np.full(5, -0.6), 0.05, 0.5)
    check("F is zero below the level and equals P(lead) times the excess above it",
          np.all(F[:3] == 0.0) and np.isclose(F[3], p_lead(0.5, -0.6) * ex[3]))
    check("F is a small fraction of the excess when the other is almost surely not a lead,"
          " however fast it looms",
          comfort_free_energy(1.0, 1.6, +0.5, 0.05, 0.5) < 0.01 * looming_excess(1.0, 0.05, 0.5))

    m, s, b = np.log(0.03), 1.0, 0.02
    pm = p_respond_mixture(td, l0, ldot, m, s, lapse=b, sigma_lat=SIGMA_LAT)
    th = np.array([np.log(b / (1 - b)), m, np.log(s)])
    import s15_comfort_threshold as S15
    ref = S15.predict_gated(th, np.log(td), p_lead(l0, ldot))
    check("the mixture response is the gated looming rule (identity with the fixed-gate fitter's"
          " prediction)", np.allclose(pm, ref, atol=1e-12))
    pe = p_respond_expected(td, l0, ldot, m, s, lapse=b)
    check("where the gate is 1 the two responses agree; where it is open partway the expected"
          " form is lower", np.isclose(pe[3], pm[3], atol=1e-4) and pe[1] < pm[1],
          f"gate {p_lead(l0[1], ldot[1]):.2f}: mixture {pm[1]:.3f}, expected {pe[1]:.3f}")
    check("both responses lie in [lapse, 1]",
          np.all(pm >= b - 1e-12) and np.all(pm <= 1) and np.all(pe >= b - 1e-12) and np.all(pe <= 1))
    check("the expected looming is P(lead) times the looming",
          np.allclose(expected_looming(td, l0, ldot), p_lead(l0, ldot) * td))

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
