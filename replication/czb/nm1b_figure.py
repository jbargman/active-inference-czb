"""
Card NM.1b -- a figure for card NM.1, and the first look at its speed gradient (query NM1.Q1).

THE PRE-REGISTRATION. Written 2026-09-25, after card NM.1, before any of this was computed.

WHY. Jonas asked for a figure to understand NM.1 and NM1.Q1. NM.1 found the released model braking
in 56% of runs behind real steady leads (humans 0%), more at 60-80 km/h (0.92) than at 95-108 km/h
(0.21). NM1.Q1 asked whether that gradient follows the authors' calibration: `find_parameters`
gives, for the lead's speed and the wanted headway, the desired-speed offset v_diff (the model is
told to want v_lead + v_diff) and the assumed lead deceleration a_tar_min.

WHAT IS COMPUTED. (A) For NM.1's 18 episodes, from NM.1's cached per-episode results (no new
simulation): v_diff and a_tar_min from `find_parameters`, exactly as NM.1 staged them; Spearman
correlations of the model's braking share with speed, headway, v_diff and a_tar_min (18 episodes,
reported as description, no verdict). (B) Four episodes re-simulated exactly as NM.1 (same seed,
same staging), now recording per-step traces: model acceleration (4 runs), model speed and gap,
against the human follower's and the lead's recorded acceleration and gap in the same 5 s.
Episodes: NM.1 idx 0 (68 km/h, THW 1.1 s), 4 (77 km/h, 1.9 s), 14 (107 km/h, 1.6 s), 16 (103 km/h,
2.2 s) -- two low-speed, two high-speed, one high-speed one where NM.1's model did not brake.

EXPECTATION (stated, not a rule). The model's gap shrinks before it brakes (it wants to go faster
than the lead and closes in), and the braking share rises with v_diff; if the braking share does
not follow v_diff or a_tar_min, the calibration does not localise the gradient.

Output: figures/nm1b_released_model_following.png, replication/czb/out/nm1b_figure.md
Run:    python replication/czb/nm1b_figure.py
"""
from __future__ import annotations

import glob
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import nm1_replayed_following as N1  # noqa: E402

OUT = HERE / "out"
FIG = REPO / "figures" / "nm1b_released_model_following.png"
TRACES = Path(r"C:\JonasLocal\D_Data_derived\nm1b_traces")
PICK = (0, 4, 14, 16)


def human_traces(ep: dict) -> dict:
    """The human follower's and the lead's recorded 5 s, matched to the NM.1 episode by speed and gap."""
    rec = int(ep["rec"])
    tr = pd.read_csv(N1.HIGHD / f"{rec:02d}_tracks.csv",
                     usecols=["frame", "id", "x", "width", "xVelocity", "xAcceleration", "precedingId", "laneId"])
    meta = pd.read_csv(N1.HIGHD / f"{rec:02d}_tracksMeta.csv", usecols=["id", "drivingDirection"])
    tr = tr.merge(meta, on="id").sort_values(["id", "frame"])
    tr["v"] = tr.xVelocity.abs()
    tr["a"] = tr.xAcceleration * np.where(tr.drivingDirection == 1, -1.0, 1.0)
    for j, g in tr.groupby("id"):
        hit = np.flatnonzero(np.isclose(g.v.to_numpy(), ep["v"], atol=1e-6))
        for q in hit:
            i = g.precedingId.iloc[q]
            L = tr[(tr.id == i) & (tr.frame >= g.frame.iloc[q]) & (tr.frame <= g.frame.iloc[q] + N1.EP)]
            if len(L) != N1.EP + 1 or q + N1.EP + 1 > len(g):
                continue
            if not np.isclose(L.v.iloc[0], ep["v_lead"], atol=1e-6):
                continue
            F = g.iloc[q:q + N1.EP + 1]
            d2 = F.drivingDirection.iloc[0] == 2
            gap = (L.x.to_numpy() - (F.x.to_numpy() + F.width.to_numpy())) if d2 \
                else (F.x.to_numpy() - (L.x.to_numpy() + L.width.to_numpy()))
            if not np.isclose(gap[0], ep["gap"], atol=1e-6):
                continue
            return {"t": np.arange(N1.EP + 1) / N1.FPS, "a_h": F.a.to_numpy(), "a_l": L.a.to_numpy(),
                    "gap_h": gap, "v_h": F.v.to_numpy()}
    raise RuntimeError(f"episode not found in recording {rec}")


def model_traces(args):
    idx, ep = args
    import torch
    torch.set_num_threads(2)
    path = TRACES / f"ep{idx:02d}.pkl"
    if path.exists():
        return pd.read_pickle(path)
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
    config["T"] = Config["T"] = N1.T_STEPS
    config["rollout_batch_size"] = N1.BATCH
    config["init_state"]["t_brake"] = 1e6
    config["init_state"]["j_brake"] = 0.0
    a_lead = np.asarray(ep["a_lead"], float)
    rec = {"acc": [], "speed": [], "gap": []}
    saved_dyn, saved_run = sim.Dynamics_true, sim.run_simulation

    def run_simulation(cfg, agent, env, eta, b, w):
        agent.reset(b, w)
        o = env.reset(eta)
        env.dynamics.reset_clock()
        for _ in range(cfg["T"]):
            with torch.no_grad():
                a_disc, a_cont = agent.choose_action(o, verbose=False)
            rec["acc"].append(a_cont[0, :, 0].detach().cpu().numpy())
            o = env.step(a_disc[0], a_cont[0])
            s = env.state.clone()
            rec["speed"].append(s[:, 4].detach().cpu().numpy())
            rec["gap"].append((s[:, 5] - s[:, 0]).detach().cpu().numpy() - init["lf"] - init["lr"])
        return {k: np.stack(v, axis=1) for k, v in rec.items()}

    sim.Dynamics_true = lambda **kw: T2.DynamicsLeadReplay(a_lead, **kw)
    sim.run_simulation = run_simulation
    try:
        sim.simulate(config, torch.device("cpu"))
    finally:
        sim.Dynamics_true, sim.run_simulation = saved_dyn, saved_run
    res = {k: np.stack(v, axis=1) for k, v in rec.items()} | {"idx": idx, "v_diff": float(v_diff),
                                                                "a_tar_min": float(a_tar_min)}
    TRACES.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(res, path)
    return res


def calibration(ep: dict) -> tuple[float, float]:
    import os
    cwd = os.getcwd()
    sys.path.insert(0, str(REPO / "external" / "aica"))
    from src.utils.simulation import find_parameters  # noqa: E402
    sys.path.insert(0, str(REPO / "replication"))
    from run_rear_end_single import build_model_params, build_initial_state  # noqa: E402
    mp, init = build_model_params(), build_initial_state()
    os.chdir(REPO / "external" / "aica")
    try:
        x_tar = ep["gap"] + init["lf"] + init["lr"]
        return find_parameters(float(ep["v_lead"]), mp["EA_fac"], mp["noise_pred_fac"], mp["H"], mp["d_phi_thres"],
                               x_tar / float(ep["v"]))
    finally:
        os.chdir(cwd)


def main() -> None:
    warnings.filterwarnings("ignore")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.stats import spearmanr
    eps = pd.read_pickle(N1.EPIS)
    res = pd.DataFrame([pd.read_pickle(f) for f in glob.glob(str(N1.RUNS / "*.pkl"))]).set_index("idx").sort_index()
    cal = pd.DataFrame([calibration(eps.loc[i].to_dict()) for i in res.index], index=res.index,
                       columns=["v_diff", "a_tar_min"])
    res = res.join(cal)
    res["kmh"] = res.v * 3.6
    with ProcessPoolExecutor(max_workers=4) as ex:
        mt = {r["idx"]: r for r in ex.map(model_traces, [(i, eps.loc[i].to_dict()) for i in PICK])}
    ht = {i: human_traces(eps.loc[i].to_dict()) for i in PICK}

    fig = plt.figure(figsize=(13, 9.5))
    gs = fig.add_gridspec(3, 4, height_ratios=[1, 1, 1.05], hspace=0.55, wspace=0.35)
    tm = (np.arange(N1.T_STEPS) + 1) * 0.2
    for c, i in enumerate(PICK):
        e, m, h = eps.loc[i], mt[i], ht[i]
        ax = fig.add_subplot(gs[0, c])
        for b in range(m["acc"].shape[0]):
            ax.plot(tm, m["acc"][b], color="tab:red", lw=1, alpha=0.7, label="model (4 runs)" if b == 0 else None)
        ax.plot(h["t"], h["a_h"], color="k", lw=2, label="human follower")
        ax.plot(h["t"], h["a_l"], color="tab:blue", lw=1, ls="--", label="lead (replayed)")
        ax.axhline(-1, color="grey", lw=0.8, ls=":")
        ax.set_ylim(-8.5, 2)
        ax.set_title(f"{e.v * 3.6:.0f} km/h, THW {e.thw:.1f} s\nv_diff {m['v_diff']:+.1f} m/s", fontsize=9)
        ax.set_xlabel("time [s]")
        if c == 0:
            ax.set_ylabel("acceleration [m/s²]")
            ax.legend(fontsize=7, loc="lower left")
        ax = fig.add_subplot(gs[1, c])
        for b in range(m["gap"].shape[0]):
            ax.plot(tm, m["gap"][b], color="tab:red", lw=1, alpha=0.7)
        ax.plot(h["t"], h["gap_h"], color="k", lw=2)
        ax.set_xlabel("time [s]")
        if c == 0:
            ax.set_ylabel("gap to lead [m]")
    ax = fig.add_subplot(gs[2, :2])
    sc = ax.scatter(res.kmh, res.model_brake_share + np.random.default_rng(0).uniform(-0.02, 0.02, len(res)),
                    c=res.thw, cmap="viridis", s=50, edgecolor="k")
    ax.scatter(res.kmh, res.human_brake.astype(float), marker="x", color="k", label="human (same episode)")
    fig.colorbar(sc, ax=ax, label="time headway [s]")
    ax.set_xlabel("follower speed [km/h]")
    ax.set_ylabel("share of model runs braking ≥ 1 m/s²")
    ax.set_title("18 steady-following episodes: model (dots) vs human (x)", fontsize=9)
    ax.legend(fontsize=7, loc="center left")
    ax = fig.add_subplot(gs[2, 2:])
    ax.scatter(res.v_diff, res.model_brake_share, c=res.thw, cmap="viridis", s=50, edgecolor="k")
    ax.set_xlabel("calibrated desired-speed offset v_diff [m/s]  (model wants v_lead + v_diff)")
    ax.set_ylabel("share of model runs braking")
    ax.set_title("does the braking follow the calibration?", fontsize=9)
    fig.suptitle("Card NM.1: the released model behind replayed real highD leads (nothing happens in these 5 s)",
                 fontsize=11)
    FIG.parent.mkdir(exist_ok=True)
    fig.savefig(FIG, dpi=130, bbox_inches="tight")

    rho = {k: spearmanr(res[k], res.model_brake_share) for k in ("kmh", "thw", "v_diff", "a_tar_min")}
    L = ["# Card NM.1b -- figure and calibration look for card NM.1", "",
         "Generated by `replication/czb/nm1b_figure.py`; pre-stated in its docstring before the run."
         " Aggregates only. Do not edit by hand.", "",
         f"Figure: `figures/{FIG.name}`.", "",
         "Spearman correlation of the model's braking share with (18 episodes, description only):", "",
         "| variable | rho | p |", "|---|---|---|"]
    for k, r in rho.items():
        L.append(f"| {k} | {r.statistic:+.3f} | {r.pvalue:.3f} |")
    L += ["", "Calibration by episode (sorted by speed):", "",
          "| km/h | THW [s] | v_diff [m/s] | a_tar_min [m/s^2] | model braking share |", "|---|---|---|---|---|"]
    for _, r in res.sort_values("kmh").iterrows():
        L.append(f"| {r.kmh:.0f} | {r.thw:.2f} | {r.v_diff:+.2f} | {r.a_tar_min:.2f} | {r.model_brake_share:.2f} |")
    L += ["", "Traced episodes: model gap at 5 s (mean of 4 runs) against the human's:", ""]
    for i in PICK:
        L.append(f"- idx {i}: model gap {mt[i]['gap'][:, -1].mean():.1f} m (start {eps.loc[i].gap:.1f} m), human"
                 f" {ht[i]['gap_h'][-1]:.1f} m; model min speed {mt[i]['speed'].min() * 3.6:.0f} km/h")
    L.append("")
    (OUT / "nm1b_figure.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
