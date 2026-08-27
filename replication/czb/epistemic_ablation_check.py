"""What does epistemic value actually contribute? The authors' own ablation, quantified.

Jonas's question (2026-08-27): our validated configuration sets alpha = 0 (epistemic
value off) because looming perception improves as distance closes, which in principle
rewards approach; is that an issue in the original too, and should the term be
reconsidered rather than dropped for convenience?

The OSF deposit answers the first half directly: the per-scenario Analysis_*.xlsx
tables contain runs at alpha = 1 AND alpha = 0 with otherwise matched configurations.
This script pairs them and reports the outcome differences.

Result: rear-end (28 matched configurations) -- collision difference exactly 0.000,
every other outcome within 0.005; intersection (6 matched) -- within 0.005 throughout;
oncoming (3 matched) -- collisions 5.7 points LOWER with epistemic value on, a thin but
non-trivial hint that information-seeking helps in the lateral scenario. So: in the
longitudinal scenarios our alpha = 0 choice reproduces an ablation the authors
themselves ran and is behaviorally equivalent; in the lateral scenario the term may
matter, which supports reconsidering it for the lateral transfer scenarios rather than
dropping it everywhere (docs/czb_validation_roadmap.md, stage E). The perverse-approach
gradient exists in the formulation but does not express at their noise settings.

    python replication/czb/epistemic_ablation_check.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
DEPOSIT = REPO / "external" / "gs4bu-osfstorage-archive"

MATCH = ["dd_LA_sd_perc", "noise_pred_fac", "use_pedals", "use_looming_perception",
         "looming_threshold", "a_tar_min_intensity", "N_norm", "EA_mode", "x_tar",
         "v_ego_des", "ttc_trigger", "rel_target",
         "x_ego", "y_tar", "theta_tar", "v_tar"]          # intersection staging
OUTCOMES = ["leave_road", "collision", "Collision", "braking_pre", "overtaking_post",
            "braking_post", "brake_steer_post", "steered", "braked"]


def main() -> None:
    for scen in ("rear_end", "oncoming", "intersection"):
        path = DEPOSIT / f"Results_{scen}" / f"Results_{scen}" / f"Analysis_{scen}.xlsx"
        if not path.exists():
            print(f"{scen}: no analysis table at {path}")
            continue
        df = pd.read_excel(path)
        if "alpha" not in df.columns:
            print(f"{scen}: no alpha column")
            continue
        counts = df.alpha.value_counts().to_dict()
        print(f"\n== {scen}: {len(df)} runs, alpha counts {counts}")
        if len(counts) < 2:
            print("   only one alpha level present -- no ablation contrast here")
            continue
        match = [c for c in MATCH if c in df.columns]
        outs = [c for c in OUTCOMES if c in df.columns]
        a1 = df[df.alpha == 1].groupby(match)[outs].mean()
        a0 = df[df.alpha == 0].groupby(match)[outs].mean()
        common = a1.index.intersection(a0.index)
        print(f"   matched configurations: {len(common)}")
        if len(common):
            d = (a1.loc[common] - a0.loc[common]).mean()
            print("   mean (alpha=1 minus alpha=0) outcome shares:")
            for k, v in d.items():
                print(f"     {k:18s} {v:+.4f}")


if __name__ == "__main__":
    main()
