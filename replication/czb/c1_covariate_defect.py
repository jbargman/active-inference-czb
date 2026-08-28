"""The C1 covariate defect (blocker B2.Q1): diagnosis, fix, and old-versus-new tables.

Card B.2.v2's first item. The finding being diagnosed (out/response_style_and_
anticipation.md, Test C): at C1 the three cut-in conditions differ two-fold in gap and
behaviour is ordered accordingly, but the field covariate ranked them BACKWARDS
(deficit 1 / 1509 / 2907 for gaps 10.5 / 16.0 / 21.5 m), so the fitted lapse was
absorbing real boundary signal with a wrong-signed covariate.

What this script establishes, all reproduced in out/c1_covariate_defect.md:

1. **The inversion is a single frame.** The whole C1 spread comes from the
   manoeuvre-onset frame (t_since_onset = 0.00), which the C1 covariate lookup
   included. At that frame the target has moved <= 6 cm, but the lane-entry
   projection's lever arm is the longitudinal TTC, so the same sliver of lateral
   motion projects to near-full overlap at the LARGEST gap: p_lane 0.000 / 0.318 /
   0.997 for TTC4 / TTC6 / TTC8. The p_safe magnitude it gates is correctly ordered
   (larger for tighter gaps); the backwards p_lane inverts the product. The frame
   before onset is also contaminated, because the central-difference lateral-velocity
   estimate at -0.1 s uses the onset frame.

2. **Covariates also inherited trace-start artifacts.** The running max accumulated
   from the trace start, ~15-17 s before onset, while the shown clips are ~10 s long
   (study context file: "a T2 clip of ~10 s shows ~9.7 s of normal driving"). A
   2 m/s^2 differentiation blip at t = 1.2 s in the 1.5 m overtake trace -- 16 s
   before onset, never shown to any participant -- put a floor of 230.9 deficit units
   under every cell of that condition.

3. **The fix is a covariate-window correction, not a field change.** The preference
   function is untouched. `comfortzone.czb_data` now accumulates the running maxima
   only over the shown window (RANDOM_CLIP_LEAD_S = 10 s before onset; the Button
   design's documented clip start), and C1's covariate window ends at
   C1_COV_END_S = -0.15 s so the pre-onset covariate cannot depend on manoeuvre
   frames -- which is the study's own C1 semantics ("pre-onset: nothing has happened
   yet").

4. **Decision (review gate R.2, 2026-08-29): C1 stays in the fit.** Under the
   corrected window the C1 covariates are 0.98 / 1.57 / 1.35 -- noise-level
   speed/accel jitter in the depicted normal driving, 0.03% of the boundary level
   and no longer ordered by criticality -- so C1 identifies the lapse exactly as
   the model assumes. The residual condition ordering in C1 behaviour
   (0.122 / 0.070 / 0.052) is real and is NOT captured by the field -- the lane gate
   zeroes the adjacent-lane longitudinal proximity signal by construction. That is
   recorded as a structural limitation of the field (it bears on R.2's larger
   question), not patched here.

Run:  python replication/czb/c1_covariate_defect.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from comfortzone.czb_data import (C1_COV_END_S, RANDOM_CLIP_LEAD_S,  # noqa: E402
                                  RANDOM_CUTIN_TRACES, random_cutin_trials,
                                  random_overtake_trials, stimulus_field)
from comfortzone.overtake import RANDOM_OVERTAKE_TRACES  # noqa: E402
from comfortzone.czb_data import overtake_stimulus_field  # noqa: E402

OUT = REPO / "replication/czb/out/c1_covariate_defect.md"


def frame_table(lines: list[str]) -> None:
    """Section 1: the frames around cut-in onset, whole-trace field (the defect)."""
    lines.append("## 1 The frames around cut-in manoeuvre onset (whole-trace field)\n")
    lines.append("The C1 covariate lookup included the onset frame (t_so = 0.00). "
                 "p_lane at that frame is ordered backwards in criticality because the "
                 "projection's lever arm is the longitudinal TTC.\n")
    lines.append("| condition | t_so [s] | deficit | p_lane | dy [m] | vy [m/s] |")
    lines.append("|---|---|---|---|---|---|")
    for c, path in RANDOM_CUTIN_TRACES.items():
        f = stimulus_field(path)          # whole-trace: the defective convention
        win = f[(f.t_since_onset >= -0.25) & (f.t_since_onset <= 0.05)]
        for _, r in win.iterrows():
            lines.append(f"| {c} | {r['t_since_onset']:+.2f} | {r['deficit']:.2f} | "
                         f"{r['p_lane']:.4f} | {r['y_rel']:.3f} | {r['dy_rel_dt']:.3f} |")
    lines.append("")


def cell_tables(lines: list[str]) -> None:
    """Sections 2-3: old-versus-new covariates for every cell, both scenarios."""
    for name, loader in (("cut-in", random_cutin_trials),
                         ("cyclist overtake", random_overtake_trials)):
        old = loader(legacy_covariates=True)
        new = loader()
        go = old.groupby(["criticality", "timepoint"], observed=True)
        gn = new.groupby(["criticality", "timepoint"], observed=True)
        do, dn = go.deficit_max.first(), gn.deficit_max.first()
        po = go.intervene.mean()
        lines.append(f"## {'2' if name == 'cut-in' else '3'} Old versus new covariates: "
                     f"{name}\n")
        lines.append("| criticality | timepoint | deficit_max (old) | deficit_max (new) "
                     "| observed P(intervene) |")
        lines.append("|---|---|---|---|---|")
        for key in do.index:
            lines.append(f"| {key[0]} | {key[1]} | {do[key]:.2f} | {dn[key]:.2f} | "
                         f"{po[key]:.3f} |")
        lines.append("")
        c1o = do.xs("C1", level="timepoint")
        c1n = dn.xs("C1", level="timepoint")
        lines.append(f"C1 covariates, old: {', '.join(f'{v:.2f}' for v in c1o)}; "
                     f"new: {', '.join(f'{v:.2f}' for v in c1n)}.\n")


def sensitivity(lines: list[str]) -> None:
    """Section 4: how the covariates depend on the assumed clip lead time."""
    lines.append("## 4 Sensitivity to the assumed clip length\n")
    lines.append("The context file gives the Random clip length as approximately 10 s. "
                 "Deficits during depicted normal driving are ~0, so the covariates "
                 "barely depend on the exact lead:\n")
    lines.append("| scenario | condition | lead 8 s | lead 10 s | lead 12 s |")
    lines.append("|---|---|---|---|---|")
    for c, path in RANDOM_CUTIN_TRACES.items():
        row = []
        for lead in (8.0, 10.0, 12.0):
            f = stimulus_field(path, accum_lead_s=lead)
            pre = f[f.t_since_onset <= C1_COV_END_S]
            row.append(pre.deficit_max.iloc[-1])
        lines.append(f"| cut-in | {c} (C1) | " + " | ".join(f"{v:.2f}" for v in row) + " |")
    for c, path in RANDOM_OVERTAKE_TRACES.items():
        row = []
        for lead in (8.0, 10.0, 12.0):
            f = overtake_stimulus_field(path, accum_lead_s=lead)
            pre = f[f.t_since_onset <= C1_COV_END_S]
            row.append(pre.deficit_max.iloc[-1])
        lines.append(f"| overtake | {c} (C1) | " + " | ".join(f"{v:.2f}" for v in row) + " |")
    lines.append("")


def main() -> None:
    lines = [
        "# The C1 covariate defect (B2.Q1): diagnosis and fix",
        "",
        f"Generated by `replication/czb/c1_covariate_defect.py`; conventions: "
        f"RANDOM_CLIP_LEAD_S = {RANDOM_CLIP_LEAD_S:.0f} s, C1_COV_END_S = "
        f"{C1_COV_END_S:+.2f} s. Do not edit by hand.",
        "",
        "**Summary.** The C1 inversion was a covariate-window error, not a data or "
        "preference-function error: the C1 lookup included the manoeuvre-onset frame, "
        "where the lane-entry projection converts <= 6 cm of lateral motion into "
        "near-full predicted overlap at the largest gap (the projection's lever arm "
        "is the longitudinal TTC), and the running max also accumulated trace-start "
        "artifacts from frames never shown to participants. With the covariate "
        "window matched to the shown clip, the C1 covariates drop to ~1 deficit "
        "unit (noise-level speed/accel jitter in the depicted normal driving, 0.03% "
        "of the boundary level, not ordered by criticality) and the inversion is "
        "gone. Decision: C1 stays in the fit and identifies the lapse; "
        "the real condition ordering in C1 behaviour is a response to adjacent-lane "
        "longitudinal proximity that the field structurally cannot see (lane gate), "
        "recorded as a limitation, not patched.",
        "",
    ]
    frame_table(lines)
    cell_tables(lines)
    sensitivity(lines)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")
    # Console check: the inversion is gone
    new = random_cutin_trials()
    c1 = (new[new.timepoint == "C1"].groupby("criticality", observed=True)
          .deficit_max.first())
    print("cut-in C1 covariates (new):", dict(c1.round(3)))


if __name__ == "__main__":
    main()
