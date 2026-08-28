"""Card B.1: the cyclist-overtake field, and whether the cut-in field represents it.

Card B.1 assumed the rear-end field would carry over "nearly unchanged" to the cyclist
overtake. This script tests that assumption before any fitting, and the answer is the
card's acceptance readout.

What is checked, in order
-------------------------
1. **Loader validation against the study's own labels.** The edge-to-edge clearance at
   the passing moment must reproduce the 0.5 / 1 / 1.5 m criticality labels. This is a
   free two-route check on the covariate and it guards a specific trap: the `Offset`
   column, which looks like the natural lateral coordinate, *inverts* the ordering.
2. **Does the field order the conditions the way the humans do?** The 15-cell surface
   (3 clearances x C1-C5) against observed intervention rate and perceived unsafety,
   under the lane-entry variants: the released-style unidirectional projection, the
   symmetric bidirectional one (`lane_entry_bidirectional`, added for this card), and
   the S-shaped ramp (`lane_entry_shape_k`).
3. **A comparator the field has to beat**: the raw lateral clearance margin. If a single
   geometric scalar the preference function does not contain outperforms the field, that
   is a statement about the field, and the transfer claim has to answer it.

Parameter motivations
---------------------
* `lane_entry_max_dy_m = 3.5` m is the study lane width, already used as
  `cutin.LANE_WIDTH_STUDY` and read off the cut-in traces' lane centres (-1.85, -5.35).
* The shape sweep k in {0, 4, 8} spans linear to a near-step at half overlap; k is not
  fitted here, because fitting a field parameter would break the "nothing upstream of
  the boundary is fitted" property that the stage-0 result rests on. Whether to fit it
  is raised as a query rather than settled here.

    python replication/czb/overtake_field_check.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))

from aidriver.preferences import PreferenceParams                               # noqa: E402
from comfortzone.czb_data import (TIMEPOINT_OFFSET_S, overtake_stimulus_field,  # noqa: E402
                                  random_overtake_trials)
from comfortzone.overtake import (NOMINAL_CLEARANCE_M, RANDOM_OVERTAKE_TRACES,  # noqa: E402
                                  clearance_at_pass, edge_clearance,
                                  load_overtake_trace)

OUT = HERE / "out"
TPS = [f"C{k}" for k in range(1, 6)]

VARIANTS = {
    "unidirectional (published form)": PreferenceParams(),
    "bidirectional": PreferenceParams(lane_entry_bidirectional=True),
    "unidirectional + S-ramp k=4": PreferenceParams(lane_entry_shape_k=4.0),
    "unidirectional + S-ramp k=8": PreferenceParams(lane_entry_shape_k=8.0),
    "bidirectional + S-ramp k=8": PreferenceParams(lane_entry_bidirectional=True,
                                                   lane_entry_shape_k=8.0),
}


def spearman(a, b) -> float:
    from scipy.stats import spearmanr
    return float(spearmanr(a, b).statistic)


def cell_table(params) -> pd.DataFrame:
    """The 15 cells with the field covariate under one parameter set."""
    fields = {c: overtake_stimulus_field(p, params)
              for c, p in RANDOM_OVERTAKE_TRACES.items()}
    rows = []
    for crit, f in fields.items():
        t = f.t_since_onset.to_numpy()
        dmax = np.maximum.accumulate(f.deficit.to_numpy())
        for tp in TPS:
            off = TIMEPOINT_OFFSET_S[tp]
            i = max(int(np.searchsorted(t, off, side="right")) - 1, 0)
            rows.append({"criticality": crit, "timepoint": tp,
                         "deficit_max": float(dmax[i]), "p_lane": float(f.p_lane.iloc[i])})
    return pd.DataFrame(rows)


def main() -> None:
    L = ["# Card B.1 - the cyclist-overtake field\n",
         "3 clearances x C1-C5 = 15 cells, 2 580 Random trials, the same 43 participants "
         "as the cut-in. The field is computed by the cut-in's own predictor code; only "
         "role assignment and the onset definition differ (`comfortzone.overtake`).\n"]

    # ---- 1. loader validation -------------------------------------------------------
    L += ["## 1 Loader validation against the study's clearance labels\n",
          "| label | edge-to-edge clearance at the pass [m] | onset t [s] | pass t [s] |",
          "|---|---|---|---|"]
    ok = True
    for lab, path in RANDOM_OVERTAKE_TRACES.items():
        tr = load_overtake_trace(path)
        c = clearance_at_pass(tr)
        ok &= abs(c - NOMINAL_CLEARANCE_M[lab]) < 0.02
        L.append(f"| {lab} | {c:.3f} | {tr.t[tr.onset_idx]:.2f} | "
                 f"{tr.t[tr.complete_idx]:.2f} |")
    L.append(f"\nAll three within 0.02 m of the label - **{'PASS' if ok else 'FAIL'}**. "
             "The `Offset` column, by contrast, gives 0.94 / 0.45 / 0.05 m and inverts "
             "the criticality ordering; it must not be used as the lateral coordinate.\n")

    # ---- 2. observed surface --------------------------------------------------------
    r = random_overtake_trials()
    obs = (r.groupby(["criticality", "timepoint"])
             .agg(intervene=("intervene", "mean"), ps=("ps", "mean"),
                  n=("intervene", "size"))
             .reset_index())
    L += ["## 2 The observed surface\n",
          "| clearance | " + " | ".join(TPS) + " |", "|---" * 6 + "|"]
    for crit in ("0.5m", "1m", "1.5m"):
        vals = [obs[(obs.criticality == crit) & (obs.timepoint == tp)].intervene.iloc[0]
                for tp in TPS]
        L.append(f"| {crit} | " + " | ".join(f"{v:.3f}" for v in vals) + " |")
    L.append("")

    # ---- 3. field variants against it ------------------------------------------------
    L += ["## 3 Does the field order the cells the way the humans do?\n",
          "Spearman rho over the 15 cells, field deficit against observed intervention "
          "rate and against perceived unsafety. The `p_lane` range shows how much of the "
          "lane-entry weight's dynamic range the scenario actually uses.\n",
          "| lane-entry variant | rho vs intervene | rho vs PS | p_lane min..max |",
          "|---|---|---|---|"]
    results = {}
    for name, params in VARIANTS.items():
        ct = cell_table(params)
        m = obs.merge(ct, on=["criticality", "timepoint"])
        rho_i = spearman(m.deficit_max, m.intervene)
        rho_p = spearman(m.deficit_max, m.ps)
        results[name] = (rho_i, rho_p)
        L.append(f"| {name} | {rho_i:+.3f} | {rho_p:+.3f} | "
                 f"{ct.p_lane.min():.3f}..{ct.p_lane.max():.3f} |")

    # ---- 4. the geometric comparator -------------------------------------------------
    clear_rows = []
    for crit, path in RANDOM_OVERTAKE_TRACES.items():
        tr = load_overtake_trace(path)
        f = overtake_stimulus_field(path)
        t = f.t_since_onset.to_numpy()
        ec = edge_clearance(tr)
        for tp in TPS:
            i = max(int(np.searchsorted(t, TIMEPOINT_OFFSET_S[tp], side="right")) - 1, 0)
            clear_rows.append({"criticality": crit, "timepoint": tp,
                               "clearance_now": float(ec[i]),
                               "clearance_final": float(ec[tr.complete_idx])})
    cl = pd.DataFrame(clear_rows)
    mc = obs.merge(cl, on=["criticality", "timepoint"])
    rho_now = spearman(mc.clearance_now, mc.intervene)
    rho_fin = spearman(mc.clearance_final, mc.intervene)
    best_field = max(results, key=lambda k: abs(results[k][0]))
    L += ["\n## 4 The comparator the field has to beat\n",
          "| predictor | rho vs intervene |", "|---|---|",
          f"| current edge clearance (negative = bodies overlap) | {rho_now:+.3f} |",
          f"| clearance the manoeuvre will end at (the label) | {rho_fin:+.3f} |",
          f"| best field variant ({best_field}) | {results[best_field][0]:+.3f} |",
          "\nSign convention: less clearance means more intervention, so a *negative* "
          "rho for a clearance predictor and a *positive* rho for the field both mean "
          "the cells are ordered correctly.\n"]

    txt = "\n".join(L) + "\n"
    (OUT / "overtake_field_check.md").write_text(txt, encoding="utf-8")
    print(txt)


if __name__ == "__main__":
    main()
