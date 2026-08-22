"""Validate against the paper's own simulation output (OSF deposit gs4bu).

    python replication/validate_osf.py

Three things, in increasing order of novelty:

1. Outcome rates: the 28 baseline rear-end conditions from Analysis_rear_end.xlsx
   against our Track B sweep (replication/sweep_aidriver.csv) - collision and
   maneuver-choice rates, distribution level rather than figure-read numbers.
2. Response-time distributions: extracted per seed from the 28 baseline pickles,
   with two onset definitions (first re-plan; first executed braking), compared
   against Track A (2 conditions) and Track B (140 runs).
3. The comfort-zone calibration pipeline run end to end on the authors' own
   trajectories: eps(t) from recorded kinematics alone, their model's onsets as
   labels, one level c fitted, plus a within-scenario transfer check (fit on
   half the speed conditions, evaluate on the other half).

Everything is written incrementally and the script skips work already done, so
it can be restarted with the same command after a kill (this environment
terminates long background jobs; see HANDOFF.md section 3).

Outputs (all under replication/osf/):
    baseline_conditions.csv     the 28 baseline conditions with outcome rates
    outcome_comparison.csv      theirs vs Track B per condition
    seeds.csv                   one row per (experiment, seed): onsets, RTs, eps stats
    eps/Exp_<i>.npz             eps(t) series per seed, for the calibration step
    calibration.json            fitted level, F1, onset errors, transfer check
    fig_rt_distributions.png    response-time distributions, theirs vs ours
    fig_calibration.png         eps exceedance vs model onset
    report.md                   the findings, readable
"""

from __future__ import annotations

import json
import os
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "src"))

from comfortzone import calibrate  # noqa: E402
from aidriver import PreferenceParams, BicycleParams  # noqa: E402

OSF = REPO / "external" / "gs4bu-osfstorage-archive" / "Results_rear_end" / "Results_rear_end"
OUT = HERE / "osf"
EPS_DIR = OUT / "eps"
OUT.mkdir(exist_ok=True)
EPS_DIR.mkdir(exist_ok=True)

DT = 0.2
CAR_LEN = 4.2          # lf + lr = 2.1 + 2.1 from the setups
CAR_WID = 1.72         # d from the setups
BRAKE_THRESHOLD = -1.0  # m/s^2 executed accel that counts as a braking response
LEAD_THRESHOLD = -0.1   # m/s^2 lead accel that marks the lead braking onset


def log(msg: str) -> None:
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# Phase 0: identify the baseline conditions
# ---------------------------------------------------------------------------

def baseline_table() -> pd.DataFrame:
    out_csv = OUT / "baseline_conditions.csv"
    setups = pd.read_excel(OSF / "Setups_rear_end.xlsx")
    analysis = pd.read_excel(OSF / "Analysis_rear_end.xlsx")
    base = (
        (setups["EA_mode"] == "Surprise")
        & (setups["noise_pred_fac"] == 0.2)
        & (setups["use_pedals"] == 1)
        & (setups["use_looming_perception"] == 1)
        & (setups["looming_threshold"] > 0.001)
        & (setups["N_norm"] == 32)
        & (setups["alpha"] == 1)
    )
    idx = setups.index[base].tolist()
    df = analysis.loc[idx, ["Unnamed: 0", "v_ego_des", "Initial THW", "x_tar",
                            "leave_road", "collision", "braking_pre",
                            "overtaking_post", "braking_post", "brake_steer_post"]].copy()
    df = df.rename(columns={"Unnamed: 0": "exp", "v_ego_des": "v0",
                            "Initial THW": "thw0"})
    df.to_csv(out_csv, index=False)
    log("phase 0: {} baseline conditions -> {}".format(len(df), out_csv.name))
    return df


# ---------------------------------------------------------------------------
# Phase 1: outcome comparison against Track B
# ---------------------------------------------------------------------------

def outcome_comparison(base: pd.DataFrame) -> pd.DataFrame:
    out_csv = OUT / "outcome_comparison.csv"
    sweep = pd.read_csv(HERE / "sweep_aidriver.csv")
    ours = sweep.groupby(["v0", "time_gap"]).agg(
        ours_n=("collided", "size"),
        ours_collision=("collided", "mean"),
        ours_brake_only=("maneuver", lambda m: (m == "brake").mean()),
        ours_steer_any=("maneuver", lambda m: m.isin(["steer", "brake+steer"]).mean()),
    ).reset_index()
    theirs = base.copy()
    # Their initial THW is measured; our sweep's time_gap is nominal. Match on
    # the nearest nominal gap in the sweep grid.
    gaps = np.array(sorted(sweep["time_gap"].unique()))
    theirs["time_gap"] = [gaps[np.argmin(np.abs(gaps - t))] for t in theirs["thw0"]]
    theirs = theirs.rename(columns={"collision": "theirs_collision",
                                    "braking_post": "theirs_brake_only",
                                    "overtaking_post": "theirs_overtake",
                                    "brake_steer_post": "theirs_brake_steer"})
    merged = theirs.merge(ours, on=["v0", "time_gap"], how="left")
    merged.to_csv(out_csv, index=False)
    log("phase 1: outcome comparison -> {} ({} matched conditions)".format(
        out_csv.name, merged["ours_n"].notna().sum()))
    return merged


# ---------------------------------------------------------------------------
# Phase 2: per-seed extraction from the pickles (incremental, restartable)
# ---------------------------------------------------------------------------

def first_index(mask: np.ndarray) -> int:
    hits = np.flatnonzero(mask)
    return int(hits[0]) if hits.size else -1


def extract_seeds(base: pd.DataFrame) -> pd.DataFrame:
    out_csv = OUT / "seeds.csv"
    done: set[int] = set()
    if out_csv.exists():
        done = set(pd.read_csv(out_csv)["exp"].unique().tolist())
    header_needed = not out_csv.exists()

    for _, row in base.iterrows():
        exp = int(row["exp"])
        if exp in done:
            continue
        pkl = OSF / "Exp_{}".format(exp) / "Exp_{}.pkl".format(exp)
        with open(pkl, "rb") as f:
            d = pickle.load(f)
        eta = d["eta"].astype(np.float64)          # (S, T, 12+)
        # a_cont is (H, T, S, 2) in the deposit - the OSF README's axis order
        # (H, S, T, 2) does not match the arrays; eta fixes S=32, T=60.
        a_exec = d["a_cont"][0, :, :, 0].astype(np.float64).T   # -> (S, T)
        replan = (np.abs(d["a_cont"] - d["a_cont_init"]) > 1e-5).any(axis=(0, 3)).T
        # replan: (S, T) True where the executed policy departs from the reference

        p = PreferenceParams(v_desired=float(row["v0"]), vehicle=BicycleParams())
        records = []
        eps_store = {}
        n_seeds, n_t = eta.shape[0], eta.shape[1]
        for s in range(n_seeds):
            lead_on = first_index(eta[s, :, 10] < LEAD_THRESHOLD)
            if lead_on < 0:
                continue
            brake_on = first_index((a_exec[s] <= BRAKE_THRESHOLD)
                                   & (np.arange(n_t) >= lead_on))
            replan_on = first_index(replan[s] & (np.arange(n_t) >= lead_on))
            dx = eta[s, :, 5] - eta[s, :, 0]
            dy = eta[s, :, 6] - eta[s, :, 1]
            overlap = (np.abs(dx) < CAR_LEN) & (np.abs(dy) < CAR_WID)
            gap = dx - CAR_LEN
            ego = eta[s, :, 0:5]
            other = eta[s, :, 5:10]
            eps = calibrate.deficit_along_trajectory(ego, other, p)
            eps_store[str(s)] = eps
            records.append({
                "exp": exp, "seed": s, "v0": float(row["v0"]),
                "thw0": float(row["thw0"]), "lead_onset_t": lead_on * DT,
                "rt_brake": (brake_on - lead_on) * DT if brake_on >= 0 else np.nan,
                "rt_replan": (replan_on - lead_on) * DT if replan_on >= 0 else np.nan,
                "brake_onset_idx": brake_on, "replan_onset_idx": replan_on,
                "lead_onset_idx": lead_on,
                "min_gap": float(gap.min()),
                "collided": int(overlap.any()),
                "eps_pre_median": float(np.median(eps[:lead_on])) if lead_on > 0 else np.nan,
                "eps_max": float(np.nanmax(eps)),
            })
        np.savez_compressed(EPS_DIR / "Exp_{}.npz".format(exp), **eps_store)
        chunk = pd.DataFrame.from_records(records)
        chunk.to_csv(out_csv, mode="a", header=header_needed, index=False)
        header_needed = False
        with open(out_csv, "a") as f:
            f.flush()
            os.fsync(f.fileno())
        log("phase 2: Exp_{} ({} seeds) appended".format(exp, len(records)))

    return pd.read_csv(out_csv)


# ---------------------------------------------------------------------------
# Phase 3: the comfort-zone calibration pipeline on their trajectories
# ---------------------------------------------------------------------------

def run_calibration(seeds: pd.DataFrame) -> dict:
    out_json = OUT / "calibration.json"

    series, onsets, keys = [], [], []
    for exp in sorted(seeds["exp"].unique()):
        npz = np.load(EPS_DIR / "Exp_{}.npz".format(int(exp)))
        sub = seeds[seeds["exp"] == exp]
        for _, r in sub.iterrows():
            sid = str(int(r["seed"]))
            if sid not in npz.files:
                continue
            onset = int(r["brake_onset_idx"])
            series.append(npz[sid])
            onsets.append(onset if onset >= 0 else None)
            keys.append((int(exp), int(r["seed"]), float(r["v0"])))

    result = calibrate.calibrate_level(series, onsets, tolerance=3)
    fitted = {
        "n_trials": len(series),
        "n_with_onset": sum(1 for o in onsets if o is not None),
        "level": float(result.level),
        "score": float(result.score),
    }

    # Onset-timing errors at the fitted level
    errors = []
    for eps, onset in zip(series, onsets):
        if onset is None:
            continue
        ev = calibrate.exceedance_events(eps, fitted["level"])
        if len(ev):
            errors.append((int(ev[0]) - onset) * DT)
    fitted["onset_error_median_s"] = float(np.median(errors)) if errors else None
    fitted["onset_error_iqr_s"] = (
        float(np.percentile(errors, 75) - np.percentile(errors, 25)) if errors else None)
    fitted["n_matched"] = len(errors)

    # Within-scenario transfer: fit on low speeds, evaluate on high, and reverse
    speeds = np.array([k[2] for k in keys])
    med = np.median(np.unique(speeds))
    transfer = {}
    for name, fit_mask in [("fit_low_eval_high", speeds <= med),
                           ("fit_high_eval_low", speeds > med)]:
        fit_s = [s for s, m in zip(series, fit_mask) if m]
        fit_o = [o for o, m in zip(onsets, fit_mask) if m]
        ev_s = [s for s, m in zip(series, fit_mask) if not m]
        ev_o = [o for o, m in zip(onsets, fit_mask) if not m]
        r_fit = calibrate.calibrate_level(fit_s, fit_o, tolerance=3)
        # score the fitted level on the held-out half against a locally refit one
        r_local = calibrate.calibrate_level(ev_s, ev_o, tolerance=3)
        r_eval = calibrate.calibrate_level(ev_s, ev_o, levels=[r_fit.level], tolerance=3)
        transfer[name] = {
            "fitted_level": float(r_fit.level),
            "heldout_score_at_fitted": float(r_eval.score),
            "heldout_score_at_local_best": float(r_local.score),
            "heldout_local_best_level": float(r_local.level),
        }
    fitted["transfer"] = transfer

    with open(out_json, "w") as f:
        json.dump(fitted, f, indent=2)
    log("phase 3: calibration -> {}".format(out_json.name))
    return fitted


# ---------------------------------------------------------------------------
# Phase 4: figures and report
# ---------------------------------------------------------------------------

def figures_and_report(base, merged, seeds, calib) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sweep = pd.read_csv(HERE / "sweep_aidriver.csv")

    # -- fig 1: response-time distributions --------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    ax = axes[0]
    theirs_rt = seeds["rt_brake"].dropna()
    ours_rt = sweep["response_time"].dropna()
    bins = np.arange(-0.5, 4.6, 0.2)
    ax.hist(theirs_rt, bins=bins, density=True, alpha=0.6,
            label="authors' runs (OSF), n={}".format(len(theirs_rt)))
    ax.hist(ours_rt, bins=bins, density=True, alpha=0.5,
            label="our Track B sweep, n={}".format(len(ours_rt)))
    for x, lab in [(0.80, "Track A @ Fig 3b"), (0.92, "Track A @ Fig 3a")]:
        ax.axvline(x, color="k", ls=":", lw=1)
        ax.text(x, ax.get_ylim()[1] * 0.95, lab, rotation=90, fontsize=7,
                ha="right", va="top")
    ax.set_xlabel("brake response time after lead onset [s]")
    ax.set_ylabel("density")
    ax.set_title("Response-time distributions")
    ax.legend(fontsize=8)

    ax = axes[1]
    grp = seeds.dropna(subset=["rt_brake"]).groupby("v0")["rt_brake"]
    stats = grp.agg(["median", "std"]).reset_index()
    ax.errorbar(stats["v0"], stats["median"], yerr=stats["std"], marker="o",
                capsize=3, label="authors' runs (median ± sd)")
    g2 = sweep.dropna(subset=["response_time"]).groupby("v0")["response_time"]
    s2 = g2.agg(["median", "std"]).reset_index()
    ax.errorbar(s2["v0"], s2["median"], yerr=s2["std"], marker="s",
                capsize=3, label="our Track B (median ± sd)")
    ax.set_xlabel("initial speed [m/s]")
    ax.set_ylabel("brake response time [s]")
    ax.set_title("Response time vs speed")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig_rt_distributions.png", dpi=150)
    plt.close(fig)

    # -- fig 2: calibration ---------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    ax = axes[0]
    level = calib["level"]
    xs, ys = [], []
    for exp in sorted(seeds["exp"].unique()):
        npz = np.load(EPS_DIR / "Exp_{}.npz".format(int(exp)))
        sub = seeds[(seeds["exp"] == exp) & (seeds["brake_onset_idx"] >= 0)]
        for _, r in sub.iterrows():
            sid = str(int(r["seed"]))
            if sid not in npz.files:
                continue
            ev = calibrate.exceedance_events(npz[sid], level)
            if len(ev):
                xs.append(r["brake_onset_idx"] * DT)
                ys.append(ev[0] * DT)
    xs, ys = np.array(xs), np.array(ys)
    ax.scatter(xs, ys, s=12, alpha=0.5)
    lim = [0, max(xs.max(), ys.max()) * 1.05] if len(xs) else [0, 1]
    ax.plot(lim, lim, "k:", lw=1)
    ax.set_xlabel("model brake onset [s]")
    ax.set_ylabel("first comfort-zone exceedance [s]")
    ax.set_title("CZB exceedance vs model onset (c = {:.3g})".format(level))

    ax = axes[1]
    npz = np.load(EPS_DIR / "Exp_{}.npz".format(int(seeds['exp'].iloc[0])))
    sub = seeds[seeds["exp"] == seeds["exp"].iloc[0]]
    for _, r in sub.head(6).iterrows():
        sid = str(int(r["seed"]))
        if sid in npz.files:
            t = np.arange(len(npz[sid])) * DT
            ax.semilogy(t, np.maximum(npz[sid], 1e-3), lw=0.8, alpha=0.7)
    ax.axhline(level, color="r", ls="--", lw=1, label="fitted c")
    ax.axvline(sub["lead_onset_idx"].iloc[0] * DT, color="k", ls=":",
               lw=1, label="lead brake onset")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("eps(t)")
    ax.set_title("Comfort-zone deficit along their trajectories")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig_calibration.png", dpi=150)
    plt.close(fig)

    # -- report -----------------------------------------------------------
    n_cond = len(base)
    both = merged.dropna(subset=["ours_n"])
    coll_corr = both["theirs_collision"].corr(both["ours_collision"]) if len(both) > 2 else np.nan
    rt = seeds["rt_brake"].dropna()
    rr = seeds["rt_replan"].dropna()
    lines = [
        "# Validation against the OSF deposit (rear-end scenario)",
        "",
        "Generated by `replication/validate_osf.py` from",
        "`external/gs4bu-osfstorage-archive/`. All numbers are the authors' own",
        "simulation output unless marked ours.",
        "",
        "## Scope",
        "",
        "- {} baseline conditions (ablations excluded), {} seed-level trials".format(
            n_cond, len(seeds)),
        "- Onset definitions: re-plan (policy departs from reference) and executed",
        "  braking below {} m/s2, both relative to lead braking onset".format(BRAKE_THRESHOLD),
        "",
        "## Response times (their runs, distribution level)",
        "",
        "| statistic | brake onset | re-plan onset |",
        "|---|---|---|",
        "| n with onset | {} | {} |".format(len(rt), len(rr)),
        "| median | {:.2f} s | {:.2f} s |".format(rt.median(), rr.median()),
        "| sd | {:.2f} s | {:.2f} s |".format(rt.std(), rr.std()),
        "| IQR | {:.2f}-{:.2f} s | {:.2f}-{:.2f} s |".format(
            rt.quantile(0.25), rt.quantile(0.75), rr.quantile(0.25), rr.quantile(0.75)),
        "",
        "Our Track B sweep: median {:.2f} s, sd {:.2f} s (the dispersion defect".format(
            sweep["response_time"].median(), sweep["response_time"].std()),
        "diagnosed in notes/03).",
        "",
        "## Outcomes vs our Track B ({} matched conditions)".format(len(both)),
        "",
        "- their overall collision rate across baseline conditions: {:.1%}".format(
            base["collision"].mean()),
        "- ours: {:.1%}".format(sweep["collided"].mean()),
        "- per-condition collision-rate correlation (theirs vs ours): {:.2f}".format(coll_corr),
        "",
        "## Comfort-zone calibration on their trajectories",
        "",
        "- fitted level c = {:.4g}, onset-matching score {:.3f} (n = {})".format(
            calib["level"], calib["score"], calib["n_trials"]),
        "- onset error at fitted c: median {} s, IQR {} s (n matched = {})".format(
            calib["onset_error_median_s"], calib["onset_error_iqr_s"], calib["n_matched"]),
        "",
        "### Within-scenario transfer (speed split)",
        "",
        "| direction | fitted c | held-out score at fitted c | held-out best score | held-out best c |",
        "|---|---|---|---|---|",
    ]
    for name, tr in calib["transfer"].items():
        lines.append("| {} | {:.4g} | {:.3f} | {:.3f} | {:.4g} |".format(
            name, tr["fitted_level"], tr["heldout_score_at_fitted"],
            tr["heldout_score_at_local_best"], tr["heldout_local_best_level"]))
    lines += [
        "",
        "## Caveats",
        "",
        "- The onsets used as labels are the *model's* responses, not human data;",
        "  this validates the pipeline and the field's behavior on reference",
        "  trajectories, not the method's empirical claim.",
        "- eps uses our PreferenceParams defaults with v_desired set per condition;",
        "  a_other_min = -6, t_react = 1 s. Boundary values inherit those.",
        "- Their collision definition may differ from min-gap <= 0 used here for",
        "  the seed-level flag; the xlsx rates are authoritative.",
        "",
        "Figures: `fig_rt_distributions.png`, `fig_calibration.png`.",
    ]
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")
    log("phase 4: report -> report.md")


def main() -> None:
    base = baseline_table()
    merged = outcome_comparison(base)
    seeds = extract_seeds(base)
    calib = run_calibration(seeds)
    figures_and_report(base, merged, seeds, calib)
    log("ALL DONE")


if __name__ == "__main__":
    main()
