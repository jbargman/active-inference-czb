"""
Card RE.3 -- the apparent-size discriminator: is the comfort-zone boundary PERCEPTUAL or
CONFIGURATIONAL?

PRE-STATED before any run (2026-09-18, on Jonas's question: "is this not a lot about the normative
model? If people are expecting and accepting for example the cut-in to have a closing relative
speed, as long as it is far away").

THE QUESTION
------------
Every card so far has asked whether some function of the scene orders the cells. Jonas's question
is prior to all of them: is the comfort-zone boundary a fact about **what the driver sees** (a
perceptual threshold) or about **what the driver expects other road users to do** (a norm over
configurations)? The two accounts are observationally identical on the second cut-in study --
both produce a curve in the (gap, closing speed) plane -- so that study cannot separate them.

One design in this project can, and the data are already in hand: **the truck and car cut-ins of
study 1 at matched TTC**. A truck is 2.55 m wide against a car's 1.88 m, so at the SAME
configuration (same bumper-to-bumper gap, same closing speed) a truck subtends a larger angle and
expands faster. The optical expansion rate is

    theta_dot = W dv / (gap^2 + W^2/4)   ~   W dv / gap^2   for gap >> W,

so the two accounts make quantitatively different predictions about where the truck's boundary
sits when both are expressed on the SAME measured axis, log theta_dot:

  **PERCEPTUAL.** The criterion is a threshold on what the eye receives, theta_dot. Then the truck
  and the car boundaries coincide on that axis and the class offset is **0**.
  **CONFIGURATIONAL.** The criterion is a threshold on the configuration -- "that closing speed is
  fine as long as it is far away" -- and the object's width does not enter it. Then, measured on
  log theta_dot, the truck's boundary sits **log(W_truck / W_car)** HIGHER, because the same
  configuration produces more expansion for a wider body.

Writing the criterion as a constant value of `W^a dv / gap^2`, the class offset measured on
log theta_dot is exactly **(1 - a) log(W_truck / W_car)**, so the contrast estimates the width
exponent **a** directly: a = 1 is perceptual, a = 0 is configurational, and anything else is
neither.

WHY THE BUTTON DESIGN, AND WHY THE LEVEL AT THE PRESS. Card JJ.4 established that the stage-1
binary estimator cannot be fitted on the Button cut-in (every cell's intervention share is 0.976
to 1.000, because that paradigm asks WHEN you would intervene and everyone presses), and that its
own response -- the press time -- gives a level per trial: the covariate at the moment of the
press. This card reuses `jj4_precision_spread.press_levels()` unchanged, so the level, the trials,
the censoring rule and the matched TTC range are card JJ.4's and not re-derived here.

THE ESTIMATE. Two routes, both reported, the first primary because it assumes least:

  **(1) The driver-clustered difference (primary).** Per driver, the mean level in each
  (class, TTC) cell; then d_i = mean over TTC of (truck - car) for driver i; the estimate is the
  mean of d_i and the interval is a bootstrap over DRIVERS (N_BOOT = 2000, the project's number).
  Per-TTC means before differencing, so an unbalanced trial count per cell cannot tilt it.
  **(2) Card JJ.4's hierarchical model**, `fit_gauss` with one offset per stimulus cell, from which
  the class main effect is the mean over TTC of the truck-minus-car cell offsets. Reported for
  continuity with JJ.4, whose own table gives -0.1265 with no interval.

THE DECISION RULE, PRE-STATED
-----------------------------
  (P) If the 95% interval on the class offset covers 0 and excludes log(W_t/W_c), the boundary is
      **perceptual** on this contrast.
  (C) If it covers log(W_t/W_c) and excludes 0, the boundary is **configurational**.
  (N) If it excludes both, it is **neither**, and the report gives the implied width exponent a
      with its interval, which is then the finding.
  (U) If it covers both, the contrast is **uninformative** at this sample size and the report says
      so rather than reading a direction into it.

WHAT THIS CARD DOES NOT SETTLE, stated in advance so the report cannot overclaim. A truck differs
from a car in more than width: it is 16.5 m long against about 5 m, it may be braked and driven
differently, and the study's own lane-change kinematics for the two classes are not identical. The
gap used throughout is bumper-to-bumper (`cutin_predictors`), which removes the length from the
gap but not from everything else. So a result of "neither" is evidence that something beyond
optical expansion enters the criterion, not proof that it is the width specifically. That caveat
is in the report's own words too.

THE SECOND PART, which needs no run: the shape the naturalistic data will have to reproduce.
Card EL.1's full-sample fit gives w = 0.497 on the linear rule x = w(-log gap) + (1-w)(-log TTC)
(`out/cutin2_two_axis.md`). The level set x = c is log dv = (log gap + c) / (1 - w), so the
comfort boundary's slope in the (log gap, log dv) plane is **1 / (1 - w) = 1.988**. Constant
looming predicts exactly 2; constant TTC predicts 1; constant gap predicts infinity. **So the
pre-registered prediction for the naturalistic cut-in data, when they arrive, is that the
iso-density contours of p(gap, dv | a lane change into my lane) have a slope of 1.99 in that
plane.** If they do, the normative and perceptual accounts coincide on this scenario and the
project should stop trying to separate them there; if they do not, the difference between the two
slopes is the size of the normative contribution. This is registered here so that the naturalistic
request becomes a test rather than an exploration.

Output: replication/czb/out/re3_apparent_size.md and out/re3_apparent_size.csv.
Run:    python replication/czb/re3_apparent_size_discriminator.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import jj4_precision_spread as J4          # noqa: E402  card JJ.4 (read only)
from comfortzone.czb_data import KIN_BUTTON                      # noqa: E402
from comfortzone.cutin import load_cutin_trace                   # noqa: E402

OUT = HERE / "out"
N_BOOT = 2000
SEED = 20260918
JJ4_OFFSET = -0.1265        # out/jj4_precision_spread.md section 2, no interval given there


def measured_widths() -> tuple[float, float, dict]:
    """The two classes' target widths, read from the traces rather than assumed."""
    w = {}
    for cls, stem in (("car", "CutInCar"), ("truck", "CutInTruck")):
        vals = []
        for lab in J4.MATCHED_TTC:
            tr = load_cutin_trace(KIN_BUTTON / f"{stem}_{lab[3:]}TTC_vehicle_states.csv")
            vals.append(float(tr.tar_wid))
        w[cls] = vals
    return float(np.median(w["car"])), float(np.median(w["truck"])), w


def per_driver_difference(b: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """d_i = mean over TTC of (truck - car) mean level, per driver; drivers with both classes."""
    cell = b.groupby(["driver", "cls", "criticality_label"])["level"].mean().reset_index()
    piv = cell.pivot_table(index=["driver", "criticality_label"], columns="cls",
                           values="level")
    piv = piv.dropna()
    diff = (piv[1] - piv[0]).groupby("driver").mean()
    return diff.index.to_numpy(), diff.to_numpy(float)


def main() -> None:
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    b, notes = J4.press_levels()
    w_car, w_truck, w_all = measured_widths()
    log_ratio = float(np.log(w_truck / w_car))

    drivers, d = per_driver_difference(b)
    est = float(np.mean(d))
    boot = np.array([np.mean(d[rng.integers(0, len(d), len(d))]) for _ in range(N_BOOT)])
    lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))

    # route 2: card JJ.4's hierarchical model
    codes = pd.factorize(b.driver)[0]
    f = J4.fit_gauss(b.level.to_numpy(float), b.cls.to_numpy(int), b.cell.to_numpy(int),
                     codes, two_spread=True)
    n_ttc = len(J4.MATCHED_TTC)
    hier = float(np.mean(f["offset"][n_ttc:]) - np.mean(f["offset"][:n_ttc]))

    # the implied width exponent, a = 1 - offset / log(W_t/W_c)
    a_est = 1.0 - est / log_ratio
    a_lo, a_hi = sorted((1.0 - hi / log_ratio, 1.0 - lo / log_ratio))

    covers_0 = lo <= 0.0 <= hi
    covers_cfg = lo <= log_ratio <= hi
    if covers_0 and not covers_cfg:
        verdict, tag = "**PERCEPTUAL** on this contrast (rule P)", "P"
    elif covers_cfg and not covers_0:
        verdict, tag = "**CONFIGURATIONAL** on this contrast (rule C)", "C"
    elif not covers_0 and not covers_cfg:
        verdict, tag = "**NEITHER** (rule N)", "N"
    else:
        verdict, tag = "**UNINFORMATIVE** at this sample size (rule U)", "U"

    L = ["# Card RE.3 -- the apparent-size discriminator: perceptual boundary or configurational?",
         "", "Generated by `replication/czb/re3_apparent_size_discriminator.py`; the question, the"
         " two predictions, the estimator and the decision rule were pre-stated in its docstring"
         " before the run. Do not edit by hand.", "",
         "Jonas, 2026-09-18: *is this not a lot about the normative model? If people are expecting"
         " and accepting for example the cut-in to have a closing relative speed, as long as it is"
         " far away.*", "",
         "## 1 The contrast", "",
         "At the SAME configuration a wider body expands faster, so the two accounts predict"
         " different class offsets when both boundaries are measured on the same axis,"
         " log theta_dot. Writing the criterion as a constant value of `W^a dv / gap^2`, the"
         " offset is (1 - a) log(W_truck / W_car).", "",
         "| quantity | value | source |", "|---|---|---|",
         f"| car target width | {w_car:.3f} m | measured from the traces |",
         f"| truck target width | {w_truck:.3f} m | measured from the traces (the loader's"
         " TRUCK_DIMS, because Length_m is broken for trucks) |",
         f"| log(W_truck / W_car) | **{log_ratio:+.4f}** | = the CONFIGURATIONAL prediction |",
         f"| the PERCEPTUAL prediction | **0** | a threshold on theta_dot itself |",
         f"| trials / drivers | {len(b)} / {b.driver.nunique()} | card JJ.4's press levels,"
         f" TTC {J4.MATCHED_TTC[0][3:]} to {J4.MATCHED_TTC[-1][3:]} |", "",
         "  " + " ".join(notes), "",
         "## 2 The estimate", "",
         "| route | class offset (truck - car) on log theta_dot | 95% interval |",
         "|---|---|---|",
         f"| **driver-clustered difference (primary)** | **{est:+.4f}** |"
         f" [{lo:+.4f}, {hi:+.4f}] |",
         f"| card JJ.4's hierarchical model | {hier:+.4f} | not estimated there |",
         f"| card JJ.4's own reported figure | {JJ4_OFFSET:+.4f} | ibid., for continuity |", "",
         f"Bootstrap over {len(d)} drivers, {N_BOOT} resamples, the project's number.", "",
         "| prediction | value | covered by the interval |", "|---|---|---|",
         f"| perceptual (a = 1) | 0 | {'**yes**' if covers_0 else 'no'} |",
         f"| configurational (a = 0) | {log_ratio:+.4f} |"
         f" {'**yes**' if covers_cfg else 'no'} |", "",
         f"Implied width exponent **a = {a_est:.2f}** [{a_lo:.2f}, {a_hi:.2f}].", "",
         "## 3 The verdict on the pre-stated rule", "", verdict, ""]

    if tag == "N":
        L += [f"The offset is on the far side of the perceptual prediction from the"
              " configurational one: the truck's boundary sits LOWER on log theta_dot than a pure"
              " looming threshold would put it, so the criterion weights apparent size MORE"
              f" heavily than optical expansion alone (a = {a_est:.2f} against 1). Read plainly:"
              " a driver treats a wide vehicle as closer to their boundary than its expansion rate"
              " says, and treats the configuration as mattering less than its optics.", ""]
    elif tag == "P":
        L += ["On this contrast the boundary is where the optics say it is, and the"
              " configurational account has to explain why the width enters at exactly the rate"
              " the optics predict.", ""]
    elif tag == "C":
        L += ["On this contrast the boundary is where the configuration says it is, and the"
              " width's effect on the optics does not move it -- which is what an expectation"
              " about how other road users behave, rather than a perceptual threshold, predicts.",
              ""]

    L += ["## 4 What this does not settle", "",
          "A truck differs from a car in more than width: it is 16.5 m long against about 5 m, it"
          " may be braked and driven differently, and the two classes' lane-change kinematics in"
          " this study are not identical. The gap is bumper-to-bumper throughout"
          " (`cutin_predictors`), which removes the length from the gap but not from everything"
          " else. So this contrast bounds how much of the criterion is optical; it does not prove"
          " that what remains is width specifically.", "",
          "It also does not speak to the SECOND study, where the normative and perceptual accounts"
          " are observationally identical. For that one the discriminating number is registered"
          " and not yet testable: card EL.1's full-sample w = 0.497 puts the comfort boundary's"
          " slope in the (log gap, log dv) plane at **1.988**, against 2 for constant looming and"
          " 1 for constant TTC. **When naturalistic cut-in data arrive, the prediction is that the"
          " iso-density contours of p(gap, dv | a lane change into my lane) have that slope.**"
          " If they do, the two accounts coincide on that scenario; if they do not, the gap"
          " between the slopes is the size of the normative contribution.", "",
          f"Run time {time.time() - t0:.0f} s.", ""]

    pd.DataFrame({"driver": drivers, "diff_log_theta_dot": d}).to_csv(
        OUT / "re3_apparent_size.csv", index=False)
    (OUT / "re3_apparent_size.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[-16:]))


if __name__ == "__main__":
    main()
