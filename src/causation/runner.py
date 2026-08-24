"""
Run one seed (all glance schedules × deceleration bins) and whole conditions, restartably.

Output: one record per (seed, schedule, decel bin) with its probability within the seed,
the outcome, and the scenario metrics. Crash weighting for the equivalence test follows
Wu et al. (2026) Eq. (10): a seed's crash records share the seed's QUADRIS weight in
proportion to their probability, so each seed's crashes sum to omega_i. Exposure weighting
(docs/crash_causation_plan.md §6b) divides omega_i by the seed's crash probability under
the reference response model and is applied in `aggregate`, not here.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from quadris import Seed, delta_v_lead, p_inj_mais2, no_return_time
from .config import CausationConfig
from .decel import DecelerationDistribution, standin_shrp2_max_decel, fixed_decel
from .glances import (GlanceDistribution, GlanceSchedule, standin_shrp2_glances,
                      anchored_schedules, marginal_overshot_schedules, process_schedules)
from .response import make_response, anchor_time
from .simulate import pre_response, execute_braking, execute_abnormal


def _t_nr(out, v_l, dt) -> float:
    """t_nr on the re-simulated trajectories, truncated at the impact sample."""
    if not out.crashed:
        return np.nan
    k = int(round(out.t_impact / dt)) + 1
    return no_return_time(out.t[:k], out.gap[:k], out.v_f[:k], v_l[:k])


def _glance_dist(cfg: CausationConfig) -> GlanceDistribution:
    g = standin_shrp2_glances() if cfg.glance_distribution == "standin" else GlanceDistribution.from_csv(cfg.glance_distribution)
    if cfg.glance_point_mass_on_road is not None:
        g = g.with_on_road(cfg.glance_point_mass_on_road)
    return g


def _decel_dist(cfg: CausationConfig) -> DecelerationDistribution:
    if not cfg.decel_cap_on:
        return fixed_decel(cfg.a_max)
    return standin_shrp2_max_decel() if cfg.decel_distribution == "standin" else DecelerationDistribution.from_csv(cfg.decel_distribution)


def schedules_for(seed: Seed, pre, cfg: CausationConfig, g: GlanceDistribution,
                  rng: np.random.Generator) -> list[GlanceSchedule]:
    if not cfg.glances_on:
        return [GlanceSchedule([], 1.0, "attentive")]
    if cfg.glance_anchor == "process":
        return process_schedules(g, float(pre.t[-1]), cfg.glance_process_draws,
                                 cfg.glance_process_on_road_mean, rng)
    t_anchor = {"tau_inv": lambda: pre.first_time(pre.tau_inv >= cfg.glance_anchor_tau_inv),
                "lead_onset": lambda: pre.t_lead_onset,
                "crash": lambda: seed.t_crash_orig}[cfg.glance_anchor]()
    if not np.isfinite(t_anchor):
        # no anchor instant on the pre-response path (e.g. lead never closes): the glance
        # cannot be placed; treat as attentive and record it
        return [GlanceSchedule([], 1.0, "attentive (no anchor)")]
    return anchored_schedules(g, t_anchor) if cfg.glance_sweep == "joint" else marginal_overshot_schedules(g, t_anchor)


def run_seed(seed: Seed, cfg: CausationConfig, g: GlanceDistribution | None = None,
             dd: DecelerationDistribution | None = None, rng: np.random.Generator | None = None) -> list[dict]:
    g = g or _glance_dist(cfg); dd = dd or _decel_dist(cfg)
    rng = rng or np.random.default_rng(cfg.seed + seed.seed_id)
    pre = pre_response(seed, cfg.dt, cfg.t_extra, cfg.pre_response_speed)
    model = make_response(cfg)
    model.prepare(pre, cfg)
    t_anchor = anchor_time(pre, cfg)
    records = []
    for sch in schedules_for(seed, pre, cfg, g, rng):
        t_on = model.onset(pre, sch, cfg)
        for d_max, p_d in zip(dd.decel, dd.probability):
            out = execute_braking(pre, t_on, float(d_max), cfg.jerk, cfg.dt)
            dv = delta_v_lead(out.v_rel_impact) if out.crashed else 0.0
            rec = dict(
                seed_id=seed.seed_id, omega=seed.weight, v_f0=seed.v_f0, d0=seed.d0,
                thw0=seed.d0 / max(seed.v_f0, 0.1), t_crash_orig=seed.t_crash_orig,
                t_lead_onset=pre.t_lead_onset, t_anchor=t_anchor,
                schedule=sch.label, glance_end=max([e for _, e in sch.intervals], default=np.nan),
                d_max=float(d_max), prob=float(sch.probability * p_d),
                no_response=False, abnormal=False, crashed=bool(out.crashed), t_onset=out.t_onset,
                rt_vs_anchor=(out.t_onset - t_anchor) if np.isfinite(t_anchor) else np.nan,
                t_impact=out.t_impact, v_rel_impact=out.v_rel_impact, dv_lead=dv,
                p_inj=p_inj_mais2(dv), a_f_min=out.a_f_min, min_gap=out.min_gap,
                a_l_min=float(np.min(np.gradient(pre.v_l, cfg.dt))),
                t_nr=_t_nr(out, pre.v_l, cfg.dt),
            )
            records.append(rec)
    def _posthoc(schedule_label, out, no_response, abnormal):
        dv = delta_v_lead(out.v_rel_impact) if out.crashed else 0.0
        return dict(seed_id=seed.seed_id, omega=seed.weight, v_f0=seed.v_f0, d0=seed.d0,
                    thw0=seed.d0 / max(seed.v_f0, 0.1), t_crash_orig=seed.t_crash_orig,
                    t_lead_onset=pre.t_lead_onset, t_anchor=t_anchor, schedule=schedule_label,
                    glance_end=np.nan, d_max=np.nan, prob=np.nan, no_response=no_response,
                    abnormal=abnormal, crashed=bool(out.crashed), t_onset=np.nan,
                    rt_vs_anchor=np.nan, t_impact=out.t_impact,
                    v_rel_impact=out.v_rel_impact, dv_lead=dv,
                    p_inj=p_inj_mais2(dv), a_f_min=out.a_f_min if abnormal else 0.0,
                    min_gap=out.min_gap,
                    a_l_min=float(np.min(np.gradient(pre.v_l, cfg.dt))),
                    t_nr=_t_nr(out, pre.v_l, cfg.dt))

    if cfg.no_response_on:
        out = execute_braking(pre, None, 1.0, cfg.jerk, cfg.dt)
        records.append(_posthoc("no response", out, True, False))
    if cfg.abnormal_on:
        t_a = pre.t_lead_onset if (cfg.abnormal_from == "lead_onset"
                                   and np.isfinite(pre.t_lead_onset)) else 0.0
        out = execute_abnormal(pre, t_a, cfg.abnormal_accel, cfg.dt)
        records.append(_posthoc("abnormal acceleration", out, False, True))
    return records


def run_condition(seeds: list[Seed], cfg: CausationConfig, out_csv: Path, label: str = "") -> pd.DataFrame:
    """Restartable: appends per seed, fsyncs, skips seeds already in the file. Writes a
    sidecar .json with the full configuration and component descriptions."""
    out_csv = Path(out_csv); out_csv.parent.mkdir(parents=True, exist_ok=True)
    g, dd = _glance_dist(cfg), _decel_dist(cfg)
    meta = dict(label=label, config=cfg.describe(), glances=g.describe() if cfg.glances_on else None,
                decel=dd.describe(), response=make_response(cfg).describe(), n_seeds=len(seeds))
    out_csv.with_suffix(".json").write_text(json.dumps(meta, indent=2, default=str))
    done = set()
    if out_csv.exists():
        done = set(pd.read_csv(out_csv, usecols=["seed_id"]).seed_id.unique().tolist())
    header = not out_csv.exists()
    for s in seeds:
        if s.seed_id in done:
            continue
        recs = run_seed(s, cfg, g, dd)
        pd.DataFrame.from_records(recs).to_csv(out_csv, mode="a", header=header, index=False)
        header = False
        with open(out_csv, "a") as f:
            f.flush(); os.fsync(f.fileno())
    return pd.read_csv(out_csv)


def aggregate(df: pd.DataFrame, no_response_share: float = 0.0,
              exposure_pc: pd.Series | None = None, abnormal_share: float = 0.0) -> pd.DataFrame:
    """
    Per-seed crash probability and per-record crash weights.

    p_c,i = sum of prob over crashed records (responding runs). Crash weight (Wu 2026 Eq. 10):
    omega_i * prob / p_c,i. If `exposure_pc` (a Series seed_id -> crash probability under the
    reference response model) is given, omega_i is first divided by it, which converts the
    QUADRIS crash weight back to an exposure weight (plan §6b). The post-hoc classes are then
    mixed in at the crash level: no-response crashes make up `no_response_share` of the total
    crash weight (Bärgman 2024) and abnormal-acceleration crashes `abnormal_share`
    (Wu 2025a: 9.2%), so responding crashes carry 1 - no_response_share - abnormal_share.
    """
    df = df.copy()
    if "abnormal" not in df.columns:                      # outputs from before 2026-08-24
        df["abnormal"] = False
    resp = df[~df.no_response & ~df.abnormal]
    pc = resp[resp.crashed].groupby("seed_id").prob.sum().reindex(df.seed_id.unique()).fillna(0.0)
    df["p_crash_seed"] = df.seed_id.map(pc)
    omega = df.omega.copy()
    if exposure_pc is not None:
        omega = omega / df.seed_id.map(exposure_pc).clip(lower=1e-6)
    df["w_crash"] = 0.0
    m = (~df.no_response) & (~df.abnormal) & df.crashed
    df.loc[m, "w_crash"] = omega[m] * df.prob[m] / df.p_crash_seed[m].clip(lower=1e-12)
    w_resp = df.loc[m, "w_crash"].sum()
    s_rest = 1.0 - no_response_share - abnormal_share
    for share, mask in ((no_response_share, df.no_response & df.crashed),
                        (abnormal_share, df.abnormal & df.crashed)):
        if share > 0 and mask.any() and w_resp > 0:
            df.loc[mask, "w_crash"] = (share / s_rest) * w_resp * (omega[mask] / omega[mask].sum())
    return df
