"""
Card NM.1 -- does the published model hold real car following that real drivers hold?

THE PRE-REGISTRATION. Written 2026-09-25, before any episode was simulated.

WHERE THE CARD COMES FROM. `docs/naturalistic_data_plan.md` §4, NM.1: "the authors' model,
unmodified, on replayed lead trajectories (the tier-2 adapter already used by GZ.1 and GZ.2), a
stratified sample by speed and THW; rate of spontaneous re-plans and braking against the human
follower in the same episode." Cards GZ.1 and GZ.2 found the released configuration brakes by itself
after about 2.6 s of steady following behind a SCRIPTED constant-speed lead; card P.1 found the
released planner braking from the first step on the video study's cells. This card uses REAL
leads.

EPISODES. highD steady following, cars behind cars: 5 s (125 frames) with the same leader and lane
and the leader's |longitudinal acceleration| below 0.5 m/s^2 throughout -- episodes in which nothing
happens. Stratified by the follower's speed, 60-80 / 80-95 / 95-108 km/h (the model's following
calibration, `find_parameters`, is tabulated to 30 m/s; 108 km/h = 30 m/s), and time headway
0.8-1.2 / 1.2-1.8 / 1.8-2.5 s: 9 strata, 2 episodes each drawn at random (seed 20260925) from
recordings 1-60. The replayed lead: the leader's recorded acceleration every 0.2 s
(`tier2_rear_end.DynamicsLeadReplay`); initial state: the follower's speed, the leader's speed, the
centre distance gap + lf + lr; the model's desired speed and assumed lead deceleration from the
authors' own `find_parameters` at the leader's speed and headway, exactly as card GZ.2 staged them.
T = 25 steps (5 s), 4 runs per episode (the authors' batch), torch seed 0.

MEASURED. Model: the share of runs that execute a deceleration of at least 1 m/s^2 at any step
(the deposit's brake definition), the first such time, the share of steps re-planned, the minimum
acceleration. Human: the same follower in the same 5 s, a qualifying episode at 1.0 m/s^2 / 0.12 s
(card NC.0b-lat, timing-valid) and its minimum acceleration.

THE RULE. The released model HOLDS real following if its braking share over all runs lies within
0.10 of the human followers' braking share over the same episodes; otherwise it does NOT HOLD, and
the report gives the direction.

PREDICTIONS. The model brakes in 50 to 90% of runs, typically 2 to 4 s in (GZ.1/GZ.2); the human
followers in under 10% (the episodes are steady by construction). DOES NOT HOLD, the model braking
far more. The share is higher at short headways.

Output: replication/czb/out/nm1_replayed_following.md (aggregates only)
Run:    python replication/czb/nm1_replayed_following.py   (machine time: tens of minutes)
"""
from __future__ import annotations

import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
HIGHD = Path(r"C:\JonasLocal\D_Data\highD-dataset-v1.0\data")
EPIS = Path(r"C:\JonasLocal\D_Data_derived\nm1_episodes.pkl")
RUNS = Path(r"C:\JonasLocal\D_Data_derived\nm1_runs")
OUT = HERE / "out"
FPS, EP, STEP = 25, 125, 5
T_STEPS, BATCH = 25, 4
V_BANDS = [(60, 80), (80, 95), (95, 108)]
THW_BANDS = [(0.8, 1.2), (1.2, 1.8), (1.8, 2.5)]


def candidates(rec: int) -> list[dict]:
    tr = pd.read_csv(HIGHD / f"{rec:02d}_tracks.csv",
                     usecols=["frame", "id", "x", "width", "xVelocity", "xAcceleration", "precedingId", "laneId"])
    meta = pd.read_csv(HIGHD / f"{rec:02d}_tracksMeta.csv", usecols=["id", "drivingDirection", "class"])
    tr = tr.merge(meta, on="id").sort_values(["id", "frame"])
    tr["v"] = tr.xVelocity.abs()
    tr["a"] = tr.xAcceleration * np.where(tr.drivingDirection == 1, -1.0, 1.0)
    arr = {k: {c: g[c].to_numpy() for c in ("frame", "x", "width", "v", "a", "precedingId", "laneId",
                                             "drivingDirection")} | {"cls": g["class"].iloc[0]}
           for k, g in tr.groupby("id")}
    out = []
    for j, g in arr.items():
        if g["cls"] != "Car":
            continue
        fr, p = g["frame"], g["precedingId"]
        for q in range(0, len(fr) - EP - 1, FPS):
            i = p[q]
            if i <= 0 or i not in arr or arr[i]["cls"] != "Car":
                continue
            if np.any(p[q:q + EP + 1] != i) or np.any(g["laneId"][q:q + EP + 1] != g["laneId"][q]):
                continue
            L = arr[i]
            m = np.searchsorted(L["frame"], fr[q])
            if m + EP + 1 > len(L["frame"]) or L["frame"][m] != fr[q]:
                continue
            la = L["a"][m:m + EP + 1]
            if np.any(np.abs(la) >= 0.5):
                continue
            gap = (L["x"][m] - (g["x"][q] + g["width"][q])) if g["drivingDirection"][q] == 2 \
                else (g["x"][q] - (L["x"][m] + L["width"][m]))
            if gap <= 0:
                continue
            fa = g["a"][q:q + EP + 1]
            below = fa < -1.0
            human_brake = any(below[k:k + 3].all() for k in range(0, EP - 2))
            out.append({"rec": rec, "v": g["v"][q], "v_lead": L["v"][m], "gap": gap, "thw": gap / g["v"][q],
                        "a_lead": la[::STEP][:T_STEPS + 1].tolist(), "human_brake": bool(human_brake),
                        "human_amin": float(fa.min())})
    return out


def run_episode(args):
    idx, ep = args
    import torch
    torch.set_num_threads(2)
    out_path = RUNS / f"ep{idx:02d}.pkl"
    if out_path.exists():
        return pd.read_pickle(out_path)
    sys.path.insert(0, str(REPO / "replication" / "causation"))
    sys.path.insert(0, str(REPO / "src"))
    sys.path.insert(0, str(REPO / "replication"))
    import tier2_rear_end as T2                                                  # noqa: E402 (chdirs)
    from run_rear_end_single import build_model_params, build_initial_state    # noqa: E402
    from src.utils.simulation import find_parameters                           # noqa: E402
    model_params = build_model_params()
    init = build_initial_state()
    x_tar = ep["gap"] + init["lf"] + init["lr"]
    init.update(v_ego=float(ep["v"]), v_tar=float(ep["v_lead"]), x_tar=float(x_tar))
    v_diff, a_tar_min = find_parameters(float(ep["v_lead"]), model_params["EA_fac"], model_params["noise_pred_fac"],
                                        model_params["H"], model_params["d_phi_thres"], x_tar / float(ep["v"]))
    model_params["v_diff"] = v_diff
    model_params["a_tar_min_intensity"] = -a_tar_min / init["a_max"]
    torch.manual_seed(0)
    sim = T2.sim_rear_end
    Config, config = sim.set_config(init, model_params, a_tar_brake=6.0)
    Config["v_ego_des"] = float(ep["v_lead"]) + v_diff
    config["reward"]["v_mu"] = Config["v_ego_des"]
    config["T"] = Config["T"] = T_STEPS
    config["rollout_batch_size"] = BATCH
    config["init_state"]["t_brake"] = 1e6
    config["init_state"]["j_brake"] = 0.0
    a_lead = np.asarray(ep["a_lead"], float)
    rec = {"acc": [], "replanned": []}
    saved_dyn, saved_run = sim.Dynamics_true, sim.run_simulation

    def run_simulation(cfg, agent, env, eta, b, w):
        agent.reset(b, w)
        o = env.reset(eta)
        env.dynamics.reset_clock()
        pl = agent.planner
        for _ in range(cfg["T"]):
            with torch.no_grad():
                a_disc, a_cont = agent.choose_action(o, verbose=False)
            rec["replanned"].append(~np.all(np.isclose(a_cont.detach().cpu().numpy(),
                                                       pl.a_cont_initial.detach().cpu().numpy()), axis=(0, 2)))
            rec["acc"].append(a_cont[0, :, 0].detach().cpu().numpy())
            o = env.step(a_disc[0], a_cont[0])
        return {k: np.stack(v, axis=1) for k, v in rec.items()}

    sim.Dynamics_true = lambda **kw: T2.DynamicsLeadReplay(a_lead, **kw)
    sim.run_simulation = run_simulation
    try:
        sim.simulate(config, torch.device("cpu"))
    finally:
        sim.Dynamics_true, sim.run_simulation = saved_dyn, saved_run
    acc = np.stack(rec["acc"], axis=1)          # [batch, T]
    rp = np.stack(rec["replanned"], axis=1)
    brake = (acc <= -1.0).any(axis=1)
    first = [float((np.argmax(r <= -1.0) + 1) * 0.2) if r.min() <= -1.0 else np.nan for r in acc]
    res = {"idx": idx, "model_brake_share": float(brake.mean()), "model_first_brake_s": float(np.nanmedian(first))
           if np.isfinite(first).any() else np.nan, "model_replan_share": float(rp.mean()),
           "model_amin": float(acc.min()), **{k: ep[k] for k in ("v", "thw", "human_brake", "human_amin", "v_lead")}}
    RUNS.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(res, out_path)
    return res


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    if EPIS.exists():
        eps = pd.read_pickle(EPIS)
    else:
        with ProcessPoolExecutor(max_workers=12) as ex:
            allc = pd.DataFrame([c for cc in ex.map(candidates, range(1, 61)) for c in cc])
        rng = np.random.default_rng(20260925)
        picks = []
        for vb in V_BANDS:
            for tb in THW_BANDS:
                s = allc[(allc.v * 3.6 >= vb[0]) & (allc.v * 3.6 < vb[1]) & (allc.thw >= tb[0]) & (allc.thw < tb[1])]
                if len(s):
                    for k in rng.choice(len(s), min(2, len(s)), replace=False):
                        picks.append(s.iloc[k].to_dict() | {"v_band": f"{vb[0]}-{vb[1]}", "thw_band": f"{tb[0]}-{tb[1]}"})
        eps = pd.DataFrame(picks)
        eps.to_pickle(EPIS)
        print(f"{len(allc):,} candidate episodes; picked {len(eps)}", flush=True)
    with ProcessPoolExecutor(max_workers=6) as ex:
        res = pd.DataFrame(list(ex.map(run_episode, [(i, r.to_dict()) for i, r in eps.iterrows()])))
    res = res.merge(eps[["v_band", "thw_band"]], left_on="idx", right_index=True)
    m_share, h_share = res.model_brake_share.mean(), res.human_brake.mean()
    holds = abs(m_share - h_share) <= 0.10
    L = ["# Card NM.1 -- the published model behind replayed real highD leads", "",
         "Generated by `replication/czb/nm1_replayed_following.py`; pre-stated in its docstring before"
         " the run. Aggregates only. Do not edit by hand.", "",
         f"{len(res)} steady-following episodes of 5 s (leader |a| < 0.5 m/s^2 throughout), 4 model runs each.", "",
         "| speed band [km/h] | THW band [s] | episodes | model: runs braking >= 1 m/s^2 | model: median first"
         " brake [s] | model: steps re-planned | model: min a [m/s^2] | human: braking | human: min a |",
         "|---|---|---|---|---|---|---|---|---|"]
    for (vb, tb), g in res.groupby(["v_band", "thw_band"]):
        L.append(f"| {vb} | {tb} | {len(g)} | {g.model_brake_share.mean():.2f} | {g.model_first_brake_s.median():.1f} |"
                 f" {g.model_replan_share.mean():.2f} | {g.model_amin.mean():.2f} | {g.human_brake.mean():.2f} |"
                 f" {g.human_amin.mean():.2f} |")
    L += ["", f"Overall: the model brakes in **{m_share:.0%}** of runs, the human followers in **{h_share:.0%}** of"
          f" the same episodes. **The released model {'HOLDS' if holds else 'does NOT hold'} real following**"
          f" (rule: within 0.10){'' if holds else (', braking more' if m_share > h_share else ', braking less')}.", "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "nm1_replayed_following.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
