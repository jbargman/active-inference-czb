"""Is the boundary level a stable per-driver trait across scenarios? (2026-08-28.)

The one-scalar claim says a driver carries a single comfort-zone level that the field
converts into behavior in any scenario. That claim makes a prediction which can be tested
**without building a field for any scenario at all**: a driver who sits low in one
scenario should sit low in the others. If per-driver position is not stable across
scenarios, no field construction can rescue the claim; if it is stable, that is positive
evidence for transfer which survives whatever the field constructions turn out to be.

This matters because the four Random scenarios do not share a design. Cut-in and cyclist
overtake have truncation series (C1-C6, C1-C5); LTAP has 9 PET levels x 2 speeds and no
time axis; truck overtake has 5 lateral offsets and no time axis. There is therefore no
common covariate on which to compare them directly -- but every one of the 43
participants saw all four, so the *driver* is the common axis, and that is the axis the
one-scalar claim is actually about.

Method, and the control that makes it readable
----------------------------------------------
Per driver and scenario, the criticality-adjusted intervention propensity: the residual
from each cell's mean, averaged over that driver's trials. Removing the cell mean is what
makes scenarios with different difficulty comparable -- otherwise the correlation would
partly reflect that everyone intervenes more in LTAP than in the overtake.

The number that makes the correlations interpretable is the **split-half reliability**
within each scenario (odd against even trials, Spearman-Brown corrected). A
cross-scenario correlation cannot exceed the geometric mean of the two scenarios' own
reliabilities, so that bound is reported alongside, and the ratio of the observed
correlation to it is the quantity worth reading: it is what fraction of the reliable
per-driver signal is shared between scenarios.

Deliberately not done here: any claim about *where* a driver's boundary sits. This tests
consistency of ordering, not the level, and a strong result is a necessary but not a
sufficient condition for the one-scalar claim.

    python replication/czb/cross_scenario_consistency.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))

from comfortzone.czb_data import load_joint                       # noqa: E402

OUT = HERE / "out"
SCENARIOS = ["cutin_car", "cyclist_overtake", "ltap", "truck_overtake"]
SHORT = {"cutin_car": "cut-in", "cyclist_overtake": "cyclist", "ltap": "LTAP",
         "truck_overtake": "truck"}
SEED = 0


def cell_key(d: pd.DataFrame) -> pd.Series:
    """The design cell, per scenario: whatever axes that scenario actually varies."""
    parts = [d.criticality_label.astype(str)]
    if d.timepoint.notna().any():
        parts.append(d.timepoint.astype(str))
    if d.ltap_speed.notna().any():
        parts.append(d.ltap_speed.astype(str))
    out = parts[0]
    for p in parts[1:]:
        out = out + "|" + p
    return out


def driver_propensity(d: pd.DataFrame) -> pd.Series:
    """Per-driver mean residual from the cell mean (criticality-adjusted propensity)."""
    d = d.copy()
    d["cell"] = cell_key(d)
    d["resid"] = d.intervene - d.groupby("cell").intervene.transform("mean")
    return d.groupby("Exp_Subject_Id").resid.mean()


def split_half(d: pd.DataFrame, rng) -> float:
    """Spearman-Brown corrected odd/even split-half reliability of the propensity."""
    d = d.copy()
    d["cell"] = cell_key(d)
    d["resid"] = d.intervene - d.groupby("cell").intervene.transform("mean")
    d = d.sample(frac=1.0, random_state=rng).reset_index(drop=True)
    d["half"] = d.groupby("Exp_Subject_Id").cumcount() % 2
    a = d[d.half == 0].groupby("Exp_Subject_Id").resid.mean()
    b = d[d.half == 1].groupby("Exp_Subject_Id").resid.mean()
    common = a.index.intersection(b.index)
    if len(common) < 10:
        return float("nan")
    r = float(np.corrcoef(a[common], b[common])[0, 1])
    return 2 * r / (1 + r) if r > -1 else float("nan")


def main() -> None:
    j = load_joint()
    r = j[(j.design == "Random") & (j.scenario.isin(SCENARIOS))].copy()

    prop, rel, ntr = {}, {}, {}
    for sc in SCENARIOS:
        d = r[(r.scenario == sc) & r.intervene.notna()]
        prop[sc] = driver_propensity(d)
        rel[sc] = np.mean([split_half(d, s) for s in range(SEED, SEED + 20)])
        ntr[sc] = len(d)

    P = pd.DataFrame(prop)
    P = P.dropna()
    C = P.corr(method="pearson")

    L = ["# Is the boundary level a stable per-driver trait across scenarios?\n",
         f"{len(P)} participants seen in all four Random scenarios. Per driver and "
         "scenario: mean residual intervention propensity after removing each design "
         "cell's mean, so scenarios of different difficulty are comparable. No field is "
         "used anywhere in this script -- the test is deliberately independent of every "
         "field construction.\n",
         "## Per-scenario reliability (the ceiling any correlation is read against)\n",
         "| scenario | trials | design cells | split-half reliability |",
         "|---|---|---|---|"]
    for sc in SCENARIOS:
        d = r[(r.scenario == sc) & r.intervene.notna()]
        L.append(f"| {SHORT[sc]} | {ntr[sc]} | {cell_key(d).nunique()} | {rel[sc]:.3f} |")

    L += ["\n## Cross-scenario correlation of per-driver propensity\n",
          "Observed Pearson r below the diagonal; the reliability ceiling "
          "sqrt(rel_a x rel_b) above it.\n",
          "| | " + " | ".join(SHORT[s] for s in SCENARIOS) + " |",
          "|---" * 5 + "|"]
    for a in SCENARIOS:
        row = [SHORT[a]]
        for b in SCENARIOS:
            if a == b:
                row.append("—")
            elif SCENARIOS.index(a) > SCENARIOS.index(b):
                row.append(f"{C.loc[a, b]:+.3f}")
            else:
                row.append(f"*{np.sqrt(max(rel[a] * rel[b], 0)):.3f}*")
        L.append("| " + " | ".join(row) + " |")

    L += ["\n## Shared fraction of the reliable signal\n",
          "Observed correlation divided by the reliability ceiling — how much of the "
          "per-driver signal that *could* be shared actually is.\n",
          "| pair | observed r | ceiling | ratio |", "|---|---|---|---|"]
    ratios = []
    for i, a in enumerate(SCENARIOS):
        for b in SCENARIOS[i + 1:]:
            ceil = np.sqrt(max(rel[a] * rel[b], 0))
            ratio = C.loc[a, b] / ceil if ceil > 0 else np.nan
            ratios.append(ratio)
            L.append(f"| {SHORT[a]} vs {SHORT[b]} | {C.loc[a, b]:+.3f} | {ceil:.3f} "
                     f"| {ratio:+.2f} |")

    L += [f"\nMean ratio across the six pairs: **{np.nanmean(ratios):+.2f}**.\n",
          "## How to read this\n",
          "A ratio near 1 would mean per-driver position is essentially the same trait "
          "in every scenario — the strongest possible non-field evidence for the "
          "one-scalar claim. A ratio near 0 would mean the scenarios rank drivers "
          "independently, in which case no field construction can make a single fitted "
          "level transfer, and the elliptical per-scenario fallback is the honest route. "
          "Intermediate values say a common trait exists but does not exhaust the "
          "per-driver variation, which would put an upper bound on how well any "
          "one-scalar transfer test can possibly do — a bound worth knowing before "
          "B.4 is scored.\n"]

    txt = "\n".join(L) + "\n"
    (OUT / "cross_scenario_consistency.md").write_text(txt, encoding="utf-8")
    print(txt)


if __name__ == "__main__":
    main()
