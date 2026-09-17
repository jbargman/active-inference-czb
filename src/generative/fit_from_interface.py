"""
The runner: an interface directory in (`transfer/interface_schema.yaml`), aggregate tables and a
report out. Runs unchanged at the home site on the synthetic fixture or on drone data written to
the interface shape, and at the data site on Volvo Cars' events; writes only what the export rule
allows (`aggregate.py`).

What it estimates from what the interface carries today:

    C3  constant-velocity prediction error of the PARTNER's motion against the horizon, pooled by
        scenario, in two phases: before the conflict onset (ordinary driving) and over the whole
        event; the growth fit (s0, s1) per axis, and the jitter floor to compare s1 with
    C2  lane-change execution metrics for `cut_in` events (the partner's lateral trace relative to
        its start), summarized, plus the crossing norm's speed band
    C4  the following population: time headway by ego speed before the onset, `rear_end` events

What it cannot estimate from the interface as it stands, and says so in the report: the lane-change
initiation hazard (C1), which needs exposure episodes and the partner's own context
(`docs/generative_model_framework.md` section 4).

    from generative.fit_from_interface import fit_generative_from_interface
    fit_generative_from_interface("transfer/fixtures/synthetic", "replication/czb/out/gm0")
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from comfortzone.interface import InterfaceGapError, load_interface_dir, longitudinal_gap

from .aggregate import run_record, write_aggregate
from .lanechange import (crossing_speed_bounds, lane_change_metrics, lane_change_summary,
                         relative_lateral)
from .population import binned_summary
from .uncertainty import cv_prediction_errors, fit_growth, growth_table, jitter_growth_floor, pool_errors

HORIZONS_S = (0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0)   # the released model's 6 s horizon, in steps
WINDOW_S = 0.3                                    # card G.1's rate window, kept for the same reason
SPEED_EDGES = np.arange(5.0, 45.0, 5.0)           # ego speed bins [m/s] for the following population
BAND_M = 0.3                                      # lane-change onset band, section 1 of lanechange.py


def _md_table(df: pd.DataFrame, fmt: str = ".3f") -> str:
    """A pipe table without the optional `tabulate` dependency, which a data site may not have."""
    cols = list(df.columns)

    def cell(v):
        if isinstance(v, float):
            return "nan" if not np.isfinite(v) else format(v, fmt)
        return str(v)

    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(cell(r[c]) for c in cols) + " |")
    return "\n".join(lines)


def _pre_onset(ev):
    t_on = ev.meta.get("t_conflict_onset")
    t = ev.t
    if t_on is None or not np.isfinite(t_on):
        return np.ones(len(t), bool)
    return t < float(t_on)


def fit_generative_from_interface(interface_dir: str | Path, out_dir: str | Path,
                                  min_n: int = 5, jitter_floor_m: float | None = None) -> dict:
    """Estimate C2, C3 and C4 from an interface directory; write aggregates and a report."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    meta, events = load_interface_dir(interface_dir)
    tables: dict[str, pd.DataFrame] = {}
    notes: list[str] = []

    # ---- C3: prediction-error growth of the partner's motion, by scenario and phase ------------
    rows_growth, rows_fit = [], []
    for scen in sorted(meta["scenario"].unique()):
        evs = [e for e in events.values() if e.scenario == scen]
        for phase in ("pre_onset", "all"):
            per_track = []
            for ev in evs:
                m = _pre_onset(ev) if phase == "pre_onset" else np.ones(len(ev.t), bool)
                if m.sum() < 3:
                    continue
                ts = ev.ts.loc[m]
                per_track.append(cv_prediction_errors(ts["t"], ts["oth_x"], ts["oth_y"],
                                                      HORIZONS_S, WINDOW_S))
            pooled = pool_errors(per_track)
            g = growth_table(pooled, n_tracks=len(per_track))
            g.insert(0, "phase", phase)
            g.insert(0, "scenario", scen)
            rows_growth.append(g)
            ok = g["n"] >= min_n
            s0_lon, s1_lon = fit_growth(g.loc[ok, "horizon_s"], g.loc[ok, "sd_lon_m"])
            s0_lat, s1_lat = fit_growth(g.loc[ok, "horizon_s"], g.loc[ok, "sd_lat_m"])
            rows_fit.append({"scenario": scen, "phase": phase, "n": int(g["n"].sum()),
                             "n_tracks": len(per_track), "s0_lon_m": s0_lon, "s1_lon_mps": s1_lon,
                             "s0_lat_m": s0_lat, "s1_lat_mps": s1_lat,
                             "jitter_floor_s1_mps": (jitter_growth_floor(jitter_floor_m, WINDOW_S)
                                                     if jitter_floor_m else np.nan)})
    tables["c3_uncertainty_growth"] = pd.concat(rows_growth, ignore_index=True) if rows_growth else pd.DataFrame()
    tables["c3_growth_fit"] = pd.DataFrame(rows_fit)

    # ---- C2: lane-change execution, cut_in events ----------------------------------------------
    metrics = []
    for ev in events.values():
        if ev.scenario != "cut_in":
            continue
        y_rel = relative_lateral(ev.t, ev.ts["oth_y"], ev.ts["ego_y"])
        metrics.append(lane_change_metrics(ev.t, y_rel, float(ev.meta["lane_width"]),
                                           oth_wid=float(ev.meta["oth_wid"]), band_m=BAND_M,
                                           window_s=WINDOW_S))
    summ = lane_change_summary(metrics)
    bounds = crossing_speed_bounds(metrics)
    summ["crossing_v_lo_mps"] = bounds["v_lo_mps"]
    summ["crossing_v_hi_mps"] = bounds["v_hi_mps"]
    tables["c2_lane_change_summary"] = summ
    if not metrics:
        notes.append("C2: no `cut_in` events in this interface directory; the lane-change table is empty.")
    elif int(summ["n_completed"].iloc[0]) == 0:
        notes.append(f"C2: {len(metrics)} `cut_in` event(s), none with a completed lane change within the "
                     f"trace under the {BAND_M} m band; the execution quantiles are undefined.")

    # ---- C4: the following population, rear_end events, before the onset -----------------------
    thw, spd, skipped = [], [], 0
    for ev in events.values():
        if ev.scenario != "rear_end":
            continue
        try:
            gap = longitudinal_gap(ev)
        except InterfaceGapError:
            skipped += 1
            continue
        m = _pre_onset(ev)
        v = ev.ts["ego_v"].to_numpy(float)
        ok = m & (v > 0.5) & np.isfinite(gap)
        thw.append(gap[ok] / v[ok])
        spd.append(v[ok])
    if thw:
        tables["c4_following_thw"] = binned_summary(np.concatenate(thw), np.concatenate(spd),
                                                    SPEED_EDGES, min_n=min_n)
    else:
        tables["c4_following_thw"] = pd.DataFrame(columns=["bin_lo", "bin_hi", "n", "q10", "q50", "q90"])
        notes.append("C4: no `rear_end` events with a resolvable gap; the following table is empty.")
    if skipped:
        notes.append(f"C4: {skipped} event(s) skipped because `ref_point` cannot be resolved (NDS.Q2).")
    notes.append("C1: the lane-change initiation hazard cannot be estimated from this interface: it "
                 "needs exposure episodes (adjacent-lane vehicles that did not cut in) and the "
                 "partner's own context columns. See docs/generative_model_framework.md section 4.")

    # ---- write ---------------------------------------------------------------------------------
    suppressed = {}
    for name, df in list(tables.items()):
        if len(df) == 0:
            continue
        suppressed[name] = write_aggregate(df, out / f"{name}.csv", min_n=min_n)
        tables[name] = pd.read_csv(out / f"{name}.csv")   # the report shows what was written
    report = [
        "# Generative-model framework: aggregates from an interface directory", "",
        "Generated by `generative.fit_from_interface`. Aggregates only; rows with fewer than "
        f"{min_n} observations are suppressed. Do not edit by hand.", "",
        "## Run record", "",
        run_record("src/generative/fit_from_interface.py",
                   {"horizons_s": list(HORIZONS_S), "window_s": WINDOW_S, "band_m": BAND_M,
                    "min_n": min_n, "n_events": len(events),
                    "scenarios": sorted(meta["scenario"].unique().tolist())}), "",
        "## Tables written", "",
    ]
    for name in tables:
        if len(tables[name]):
            report.append(f"- `{name}.csv` ({len(tables[name])} rows; {suppressed.get(name, 0)} suppressed)")
    if len(tables["c3_growth_fit"]):
        report += ["", "## C3: growth fit per scenario and phase", "",
                   _md_table(tables["c3_growth_fit"])]
    if len(tables["c2_lane_change_summary"]) and tables["c2_lane_change_summary"]["n"].iloc[0] > 0:
        report += ["", "## C2: lane-change execution", "",
                   _md_table(tables["c2_lane_change_summary"])]
    if len(tables["c4_following_thw"]):
        report += ["", "## C4: following time headway by ego speed (pre-onset)", "",
                   _md_table(tables["c4_following_thw"])]
    if notes:
        report += ["", "## Notes", ""] + [f"- {n}" for n in notes]
    (out / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return tables
