"""
Card JJ.3b -- the cyclist overtake with a collision test sized for the cyclist.

THE PRE-REGISTRATION. Written before the run, on 2026-09-22. Jonas: "I would like you to run
the cyclist sized box version."

WHY. Card JJ.3 scored the overtake's 15 cells with the released collision box, |dy| <= 1.15 x the
EGO's width (1.98 m centre to centre) and |dx| <= 1.15 x its length, applied to a cyclist 0.58 m
wide. The review of 2026-09-22 found that the clean recorded 0.5 m pass sits at about 1.74 m
centre to centre, so 57 to 60% of futures "collide" under continue at every clearance, and the
grading of Delta G by clearance came from that artefact; and that the worklog quoted the SECONDARY
fold scheme (0.1580 against 0.2099) where on the primary folds Delta G scored 0.1865 and lost to
card B.1's clearance rule (0.1465) and to chance (0.1585). This card reruns the overtake with the
collision test that the package already has for the left turn: the ORIENTED POLYGON OVERLAP of
the two bodies (`rollout.efe.polygon_overlap`, `collision_mode="polygon"`), which uses each body's
own length and width. Nothing else changes: JJ.3's scenes, freezes, menu (continue / abort), fan,
folds, metric and comparators, all imported from `jj3_rollout_transfer.overtake` by re-running its
loop with the one argument added. (The reviewer's two other observations, the rotated freeze
frame's keep-clip and the differentiation noise on the recorded path, are NOT addressed here;
one change at a time.)

THE RULES. Card JJ.3's for the overtake, verbatim: rule (d), the predicted share falls with
clearance at every timepoint; and the held-out comparison on the PRIMARY leave-one-timepoint-out
folds against card B.1's clearance rule (0.1465) and chance (0.1585). Rule 0: the released-box
run reproduces JJ.3's 0.1865 (variant A) to 0.0005. Verdict: the parked "lateral factor" is
REINSTATED if variant A on the polygon test beats the clearance rule on the primary folds by 0.01
AND rule (d) holds; RETIRED otherwise.

PREDICTIONS. With the cyclist-sized test, the recorded pass at 0.5 m collides in far fewer
futures (the reviewer's estimate: a handful of exact tests per cell), so G(continue) falls by
tens of thousands of nats at every clearance and Delta G loses most of its variation across
clearance; rule (d) fails at more timepoints than before, and the held-out score lands near
chance (0.15 to 0.17). RETIRED. If instead Delta G improves to below 0.1365, the artefact was
hiding a real ordering and the item is reinstated on its own terms.

Output: replication/czb/out/jj3b_cyclist_box.md, out/jj3b_cyclist_box_cells.csv
Run:    python replication/czb/jj3b_cyclist_box.py
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import jj3_rollout_transfer as J3          # noqa: E402  card JJ.3 (read only)
from rollout.boundary import axis, delta_g  # noqa: E402
from rollout.efe import g_by_policy, variant_params  # noqa: E402

OUT = HERE / "out"
JJ3_A_PRIMARY = 0.1865
_orig_g_by_policy = J3.g_by_policy


def run(mode: str) -> pd.DataFrame:
    """JJ.3's overtake loop with the collision test chosen by `mode`."""
    def patched(b, fut, paths, p, collision_mode="released", weights=None):
        return _orig_g_by_policy(b, fut, paths, p, collision_mode=mode, weights=weights)
    J3.g_by_policy = patched
    try:
        _, df = J3.overtake(variants=("A", "B"))
    finally:
        J3.g_by_policy = _orig_g_by_policy
    return df


def scores(df: pd.DataFrame) -> dict:
    folds_tp = pd.factorize(df.timepoint)[0].astype(float)
    folds_cl = df.clearance_m.to_numpy(float)
    out = {}
    for var in ("A", "B"):
        ax = axis(df[f"dg_{var}"].to_numpy(float))
        r_tp, pred = J3.held_out_1d(df, ax.values, folds_tp)
        r_cl, _ = J3.held_out_1d(df, ax.values, folds_cl)
        _, pred_full = J3.full_predict(df, ax.values)
        graded = []
        for tp in sorted(df.timepoint.unique()):
            s = df[df.timepoint == tp].sort_values("clearance_m")
            pf = pred_full[s.index.to_numpy()]
            graded.append(bool(np.all(np.diff(pf) < 0)))
        out[var] = {"tp": r_tp, "cl": r_cl, "graded": graded, "zeros": ax.n_zero}
    x_clear = -np.log(df.clearance_m.to_numpy(float))
    out["clear"] = J3.held_out_1d(df, x_clear, folds_tp)[0]
    out["chance"] = J3.T.wrmse(df.p.to_numpy(float),
                               np.full(len(df), np.average(df.p, weights=df.n)), df.n.to_numpy(float))
    return out


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    box = run("released")
    poly = run("polygon")
    sb, sp = scores(box), scores(poly)
    rule0 = abs(sb["A"]["tp"] - JJ3_A_PRIMARY) <= 0.0005
    box.assign(test="released box").pipe(lambda d: pd.concat([d, poly.assign(test="polygon")])) \
        .to_csv(OUT / "jj3b_cyclist_box_cells.csv", index=False)
    beats = sp["A"]["tp"] <= sp["clear"] - 0.01
    graded = all(sp["A"]["graded"])
    verdict = "REINSTATED" if beats and graded else "RETIRED"
    L = ["# Card JJ.3b -- the cyclist overtake with a collision test sized for the cyclist", "",
         "Generated by `replication/czb/jj3b_cyclist_box.py`; the change, the rules and the"
         " predictions were pre-stated in its docstring before the run. Do not edit by hand.", "",
         f"Rule 0: the released-box run gives {sb['A']['tp']:.4f} against card JJ.3's"
         f" {JJ3_A_PRIMARY} on the primary folds: **{'PASS' if rule0 else 'FAIL'}**.", "",
         "## 1 G(continue) and Delta G by clearance, variant A (medians over the 5 timepoints)", "",
         "| clearance | released box: G(continue) / Delta G [nats] | polygon: G(continue) /"
         " Delta G [nats] |", "|---|---|---|"]
    for lab in sorted(box.clearance.unique(), key=lambda s: float(s.replace("m", ""))):
        b_, p_ = box[box.clearance == lab], poly[poly.clearance == lab]
        L.append(f"| {lab} | {b_.G_A_continue.median():,.0f} / {b_.dg_A.median():,.0f} |"
                 f" {p_.G_A_continue.median():,.0f} / {p_.dg_A.median():,.0f} |")
    L += ["", "## 2 The scores", "",
          "| model | held out, leave-one-timepoint-out (primary) | leave-one-clearance-out |"
          " rule (d), timepoints graded | zero cells |", "|---|---|---|---|---|"]
    for tag, s in (("released box (card JJ.3)", sb), ("polygon, cyclist-sized", sp)):
        for var in ("A", "B"):
            L.append(f"| Delta G {var}, {tag} | {s[var]['tp']:.4f} | {s[var]['cl']:.4f} |"
                     f" {sum(s[var]['graded'])} of 5 | {s[var]['zeros']} |")
    L += [f"| the clearance rule (card B.1) | {sp['clear']:.4f} | - | - | - |",
          f"| chance | {sp['chance']:.4f} | - | - | - |", "",
          "## 3 The verdict", "",
          f"**The lateral factor is {verdict}.** Variant A on the polygon test: {sp['A']['tp']:.4f}"
          f" against the clearance rule's {sp['clear']:.4f} (needs 0.01 better:"
          f" {'yes' if beats else 'no'}); rule (d) {'holds' if graded else 'fails'} at"
          f" {sum(sp['A']['graded'])} of 5 timepoints.", "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj3b_cyclist_box.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
