"""
Property tests for the generative-model framework (src/generative/, 2026-09-17).

The claims under test, rather than "the code runs":

* a constant-velocity prediction of a constant-velocity track has zero error at every horizon, and
  a change of velocity produces an error that grows with the horizon; the growth fit recovers its
  own parameters; pure position jitter produces a growth slope that the floor formula predicts;
* the lane-change detector recovers a scripted onset, duration and peak lateral speed, and reports
  no lane change where there is none; the sign convention points toward the ego;
* the person-period expansion has the right number of rows and events; the logistic hazard
  recovers a constant hazard exactly and a scripted slope within its standard error; its
  log-likelihood is never below the constant-hazard one; calibration bins are suppressed below min_n;
* the binned summary suppresses small bins but keeps their counts; the Gaussian reference's
  Mahalanobis distance is zero at the mean and one at one standard deviation;
* the export rule REFUSES identifier columns and drops small rows, and agrees with the policy file;
* the runner works end to end on the synthetic fixture and writes nothing the policy forbids.

Run: python tests/test_generative.py
"""
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from generative.aggregate import (  # noqa: E402
    FORBIDDEN_COLUMNS, PERSON_COLUMNS, AggregateRuleError, check_aggregate,
)
from generative.fit_from_interface import fit_generative_from_interface  # noqa: E402
from generative.hazard import (  # noqa: E402
    calibration_table, fit_logistic_hazard, person_period, predict_hazard,
)
from generative.lanechange import (  # noqa: E402
    crossing_speed_bounds, lane_change_metrics, relative_lateral,
)
from generative.population import binned_summary, gaussian_reference, mahalanobis2  # noqa: E402
from generative.uncertainty import (  # noqa: E402
    backward_velocity, cv_prediction_errors, fit_growth, growth_table, jitter_growth_floor,
    pool_errors,
)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS " if cond else "FAIL ") + name + (f"  -- {detail}" if detail else ""))


def main():
    rng = np.random.default_rng(11)
    dt = 0.05
    t = np.arange(0.0, 10.0, dt)

    # ---- C3 uncertainty --------------------------------------------------------------------------
    v = backward_velocity(t, 3.0 * t, 0.3)
    check("backward velocity of x = 3t is 3 wherever the window exists",
          np.allclose(v[np.isfinite(v)], 3.0) and np.isnan(v[0]))
    errs = cv_prediction_errors(t, 20.0 + 15.0 * t, 1.0 + 0.2 * t, (1.0, 3.0, 6.0), 0.3)
    check("CV prediction of a CV track has zero error at every horizon",
          all(np.allclose(ex, 0) and np.allclose(ey, 0) for ex, ey in errs.values()))
    y_step = np.where(t < 5.0, 0.0, -1.0 * (t - 5.0))       # lateral velocity step at 5 s
    errs = cv_prediction_errors(t, 15.0 * t, y_step, (1.0, 2.0, 4.0), 0.3)
    sds = [np.std(errs[h][1]) for h in (1.0, 2.0, 4.0)]
    check("a velocity change makes the lateral error grow with the horizon",
          sds[0] < sds[1] < sds[2], f"{sds[0]:.3f} < {sds[1]:.3f} < {sds[2]:.3f}")
    h = np.array([0.5, 1, 2, 3, 4, 6])
    s0, s1 = fit_growth(h, np.sqrt(0.1 ** 2 + (0.4 * h) ** 2))
    check("growth fit recovers s0 = 0.10 and s1 = 0.40", abs(s0 - 0.1) < 1e-6 and abs(s1 - 0.4) < 1e-6,
          f"{s0:.4f}, {s1:.4f}")
    g = growth_table(errs, n_tracks=1)
    check("growth table counts one row per horizon with n > 0",
          list(g["horizon_s"]) == [1.0, 2.0, 4.0] and (g["n"] > 0).all())
    # pure jitter: many CV tracks with white noise; the fitted s1 is near the floor formula
    sigma = 0.03
    per = []
    for _ in range(60):
        per.append(cv_prediction_errors(t, 15.0 * t + rng.normal(0, sigma, len(t)),
                                        rng.normal(0, sigma, len(t)), (1.0, 2.0, 3.0, 4.0), 0.3))
    gj = growth_table(pool_errors(per), n_tracks=60)
    _, s1_lat = fit_growth(gj["horizon_s"], gj["sd_lat_m"])
    floor = jitter_growth_floor(sigma, 0.3)
    check("pure position jitter produces the growth slope the floor formula predicts (within 15%)",
          abs(s1_lat - floor) / floor < 0.15, f"fitted {s1_lat:.4f} m/s, floor {floor:.4f} m/s")

    # ---- C2 lane change --------------------------------------------------------------------------
    W, D, t0 = 3.65, 3.0, 2.0
    s = np.clip((t - t0) / D, 0, 1)
    y = W * (3 * s ** 2 - 2 * s ** 3)                        # smooth lane change over D seconds
    m = lane_change_metrics(t, y, W, oth_wid=1.85, band_m=0.3, window_s=0.3)
    # analytic band crossings: solve W(3s^2 - 2s^3) = 0.3 and = W - 0.3
    ss = np.linspace(0, 1, 200001)
    yy = W * (3 * ss ** 2 - 2 * ss ** 3)
    t_on = t0 + D * ss[np.argmax(yy > 0.3)]
    t_dn = t0 + D * ss[np.argmax(yy >= W - 0.3)]
    check("lane-change onset recovered within two samples of the analytic band crossing",
          abs(m["t_onset_s"] - t_on) <= 2 * dt + 1e-9, f"{m['t_onset_s']:.3f} vs {t_on:.3f}")
    check("lane-change duration recovered within two samples",
          abs(m["duration_s"] - (t_dn - t_on)) <= 2 * dt + 1e-9,
          f"{m['duration_s']:.3f} vs {t_dn - t_on:.3f}")
    check("peak lateral speed within 10% of 1.5 W / D",
          abs(m["peak_v_lat_mps"] - 1.5 * W / D) / (1.5 * W / D) < 0.10,
          f"{m['peak_v_lat_mps']:.3f} vs {1.5 * W / D:.3f}")
    check("straddling time is positive and shorter than the duration",
          0 < m["straddle_s"] < m["duration_s"], f"{m['straddle_s']:.2f} s")
    m0 = lane_change_metrics(t, rng.normal(0, 0.03, len(t)), W)
    check("no lane change: completed False and onset NaN", (not m0["completed"]) and np.isnan(m0["t_onset_s"]))
    y_rel = relative_lateral(t, 3.65 - y, np.zeros_like(t))   # partner starts one lane to the left, moves toward ego
    check("relative lateral is positive toward the ego and ends near the lane width",
          y_rel[-1] > 3.0 and np.all(np.diff(y_rel[(t > t0) & (t < t0 + D)]) >= -1e-9))
    b = crossing_speed_bounds([m, m, m])
    check("crossing speed bounds bracket the peak speed", b["v_lo_mps"] <= m["peak_v_lat_mps"] <= b["v_hi_mps"])

    # ---- C1 hazard -------------------------------------------------------------------------------
    ep_t = np.arange(0.0, 5.0, 0.1)
    pp = person_period([{"t": ep_t, "X": np.ones((len(ep_t), 1)), "t_event": 3.2},
                        {"t": ep_t, "X": np.ones((len(ep_t), 1)), "t_event": None}], dt_bin=0.5)
    n_ev_rows = int((pp["episode"] == 0).sum())
    n_cens_rows = int((pp["episode"] == 1).sum())
    check("person-period: the event episode stops at its event bin (7 rows for 3.2 s at 0.5 s bins)",
          n_ev_rows == 7 and pp.loc[pp["episode"] == 0, "event"].iloc[-1] == 1, f"{n_ev_rows} rows")
    check("person-period: the censored episode keeps every bin with no event",
          n_cens_rows == 10 and pp.loc[pp["episode"] == 1, "event"].sum() == 0, f"{n_cens_rows} rows")
    yb = (rng.random(2000) < 0.08).astype(float)
    fit0 = fit_logistic_hazard(np.zeros((2000, 0)), yb)
    check("intercept-only hazard recovers logit(mean)",
          abs(fit0["coef"][0] - np.log(yb.mean() / (1 - yb.mean()))) < 1e-6)
    # scripted logistic hazard on a scalar feature, many episodes
    X = rng.normal(0, 1, 6000)
    p = 1 / (1 + np.exp(-(-2.5 + 1.2 * X)))
    yv = (rng.random(6000) < p).astype(float)
    fit = fit_logistic_hazard(X, yv)
    check("hazard slope recovered within 3 SE of 1.2",
          abs(fit["coef"][1] - 1.2) < 3 * fit["se"][1], f"{fit['coef'][1]:.3f} +- {fit['se'][1]:.3f}")
    check("hazard fit log-likelihood is not below the constant-hazard one", fit["loglik"] >= fit["loglik_const"] - 1e-9)
    ph = predict_hazard(fit["coef"], X)
    cal = calibration_table(ph, yv, n_bins=10, min_n=5)
    check("calibration: predicted and observed rates agree within 0.03 on average",
          np.nanmean(np.abs(cal["mean_pred"] - cal["mean_obs"])) < 0.03)
    cal_small = calibration_table(ph[:30], yv[:30], n_bins=10, min_n=5)
    check("calibration bins below min_n are suppressed but keep their count",
          cal_small["mean_pred"].isna().all() and (cal_small["n"] == 3).all())

    # ---- C4 population -----------------------------------------------------------------------------
    vals = np.concatenate([rng.normal(1.5, 0.3, 200), rng.normal(2.0, 0.3, 3)])
    by = np.concatenate([np.full(200, 12.0), np.full(3, 27.0)])
    bs = binned_summary(vals, by, np.arange(5, 45, 5), min_n=5)
    big = bs[(bs["bin_lo"] == 10.0)].iloc[0]
    small = bs[(bs["bin_lo"] == 25.0)].iloc[0]
    check("binned summary: the large bin has quantiles, the small bin keeps n = 3 and NaN quantiles",
          abs(big["q50"] - 1.5) < 0.1 and small["n"] == 3 and np.isnan(small["q50"]))
    ref = gaussian_reference(rng.normal(0, 1, (5000, 2)))
    d2 = mahalanobis2(ref, np.vstack([ref["mean"], ref["mean"] + np.sqrt(np.diag(ref["cov"])) * [1, 0]]))
    check("Mahalanobis: 0 at the mean, about 1 at one standard deviation",
          abs(d2[0]) < 1e-12 and abs(d2[1] - 1.0) < 0.1, f"{d2[1]:.3f}")

    # ---- export rule -------------------------------------------------------------------------------
    try:
        check_aggregate(pd.DataFrame({"driver_id": ["D01"], "n": [10]}))
        check("export rule refuses an identifier column", False)
    except AggregateRuleError:
        check("export rule refuses an identifier column", True)
    kept, dropped = check_aggregate(pd.DataFrame({"bin": [1, 2, 3], "n": [10, 4, 7]}), min_n=5)
    check("export rule drops rows below min_n and counts them", len(kept) == 2 and dropped == 1)
    policy = (ROOT / "transfer" / "transfer_policy.yaml").read_text(encoding="utf-8")
    fc = re.search(r"forbidden_columns:\s*\[([^\]]*)\]", policy.split("data:")[-1]).group(1)
    pc = re.search(r"person_columns:\s*\[([^\]]*)\]", policy.split("data:")[-1]).group(1)
    pol_f = {c.strip() for c in fc.split(",")}
    pol_p = {c.strip() for c in pc.split(",")}
    check("the code's forbidden and person columns match the policy file",
          pol_f == FORBIDDEN_COLUMNS and pol_p == PERSON_COLUMNS,
          f"missing in code: {sorted((pol_f | pol_p) - (FORBIDDEN_COLUMNS | PERSON_COLUMNS))}")

    # ---- the runner on the synthetic fixture --------------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        tables = fit_generative_from_interface(ROOT / "transfer" / "fixtures" / "synthetic", td, min_n=5)
        out = Path(td)
        check("runner writes report.md and the C3 tables on the synthetic fixture",
              (out / "report.md").exists() and (out / "c3_growth_fit.csv").exists())
        bad = []
        for f in out.glob("*.csv"):
            cols = {c.lower() for c in pd.read_csv(f).columns}
            bad += sorted(cols & (FORBIDDEN_COLUMNS | PERSON_COLUMNS))
        check("no written table carries a forbidden column", not bad, str(bad))
        fitc3 = tables["c3_growth_fit"]
        # the fixture's oth_y is white jitter of 0.03 m on a straight line: the lateral growth slope
        # over the WHOLE event must sit near the jitter floor sqrt(2)*0.03/0.3 = 0.141 m/s
        row = fitc3[(fitc3["scenario"] == "rear_end") & (fitc3["phase"] == "all")]
        s1 = float(row["s1_lat_mps"].iloc[0]) if len(row) else np.nan
        check("fixture: the lateral growth slope is the jitter floor, not behavior (within 30%)",
              np.isfinite(s1) and abs(s1 - jitter_growth_floor(0.03, 0.3)) / jitter_growth_floor(0.03, 0.3) < 0.30,
              f"s1 = {s1:.4f} m/s against floor {jitter_growth_floor(0.03, 0.3):.4f}")

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        sys.exit(1)


if __name__ == "__main__":
    main()
