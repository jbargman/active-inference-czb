"""
Card GZ.1 -- can the released model CHOOSE its glances, and could that choice be fitted to
real-world glance data? A feasibility probe, not a fit.

PRE-STATED before the run (2026-09-13).

THE QUESTION (Jonas, 2026-09-12): the released code carries a complete gaze system -- a
two-state gaze variable, an off-road noise multiplier I_factor = 3, a gaze preference
`road_pref` -- but the planner overrides the gaze choice to "always on road"
(`mpc_discrete.py:43`, "Avoid off gaze right now (hardcoded)"), in every scenario of the
repository, including the one named "epistemic". Could we switch that off and fit the gaze
parameters so that the model's own glances match the SHRP2 baseline glance distribution we
already use in the crash-causation study?

WHAT "FIT" WOULD MEAN. The model is not trained; nothing in it learns. Its glances would
come out of expected-free-energy planning: gaze is a discrete action, scored by the gaze
preference (pragmatic) and by how much looking reduces uncertainty (epistemic). Fitting means
choosing `road_pref`, `I_factor` and the perception noise so that simulated glance statistics
match the data -- simulation-based parameter estimation, every evaluation a closed-loop run.
Before costing that, two things must be known, and this probe finds them out:

  (1) does the planner, freed to choose, ever look away at all, and does it look back?
  (2) does the perception-noise level decide the answer? The released perception noise
      above the looming threshold is 1e-5 (0.001 x perc_noise_factor 0.01); with the gaze
      multiplier it becomes 3e-5, so looking away may cost almost no information, leaving
      the epistemic term no reason to bring the eyes back (worked out 2026-09-12).

WHAT IS RUN. Steady car following with no conflict: ego and lead both at 15 m/s, bumper
gap 30 m (time headway 2.0 s), the lead replayed at constant speed through the tier-2
adapter's replay class. The authors' files are not edited: the planner's discrete-action
proposal is replaced on the constructed agent (`agent.planner.pi`), the same monkeypatch
pattern the tier-2 adapter uses. T = 75 steps (15 s), batch 4 repeats, two conditions:

  G0  released perception noise (perc_noise_factor 0.01), I_factor 3
  G1  perception noise 100x larger (perc_noise_factor 1.0), I_factor 3
  G2  released perception noise, I_factor 1000 -- looking away is close to blindness
      (1e-5 x 1000 = 1e-2 rad/s, about five times the looming threshold). Added before any
      run, after a two-step smoke test, to separate the two things G0/G1 confound: how noisy
      perception is, and how much a glance costs.

Both with gaze choice enabled:
  road_pref = log(0.8) -- motivated, not tuned: the SHRP2 baseline epochs behind the
    crash-causation glance distribution are ~80% on-road (src/causation/glances.py:6), and
    the model's gaze preference is literally a Bernoulli prior over on-road gaze, so this
    encodes "I expect to look at the road 80% of the time".
  planner proposal pi = [0.8, 0.2] -- only the CEM's starting proposal over the two gaze
    actions (it is refitted from the elite plans each iteration). Not 0.5/0.5: the code builds
    its first reference plan with `pi > 0.5`, which is not one-hot at exactly one half.
  I_factor = 3 (the code's default), p = 1 (the rear-end configuration: a chosen look-away
    takes effect in the next step), alpha = 1 (epistemic value on).
Everything else is `run_rear_end_single.build_model_params()`, the paper's configuration.

PRE-STATED READINGS (what each outcome would mean; not predictions):
  R1  No condition ever looks away  -> with the published scale of the other preference terms
      (collision and safety costs of order 1e3-1e4 per step) the gaze preference of about
      -1.4 per step is invisible; fitting to SHRP2 would first need the gaze preference
      re-scaled against them, and that scale becomes the first free parameter of any fit.
  R2  G0 looks away and does not look back, G1 looks back -> supports the 2026-09-12 reading
      that the released noise makes a glance informationally free; any fit must free the
      perception noise too.
  R3  Both look away and back, with similar statistics -> noise does not govern gaze here;
      the preference does, and a fit is a direct, if slow, search over road_pref and I_factor.
  G2 is read against G0: if G0 looks away freely and G2 does not, the glance's information
      cost is what the planner responds to, and I_factor is identifiable from glance data.
  R4  Anything else -> reported as found.
In every case the probe reports the runtime per step, which is what costs a real fit.

[Added after the first run, 2026-09-13: a CONTROL condition G0c. In G0 and G2 the ego did not
stay in steady following: after about 4 s it began taking glances and, within a few steps,
braked all the way to a standstill while the lead held 15 m/s (gap to 133 m). G1 followed
normally. That was not among the pre-stated readings, and it makes the glance statistics of G0
and G2 statistics of a car stopping. G0c is the released configuration exactly -- gaze choice
left OFF (the planner's hard-coded proposal kept), road_pref = 0 -- in the same scenario, to
separate "enabling gaze choice makes the model brake" from "this setup makes the released model
brake anyway, and glances merely appear at the same re-plan". G0c changes nothing about G0-G2.]

[Part b, pre-stated 2026-09-13 after the control: the control G0c also braked (median first step
below 14 m/s: 23, the same as G0 and G2), so the braking is not caused by gaze choice. Part b reruns
all four conditions at a 1.5 s headway, the desired headway the authors pass to their calibration
lookup in `simulation_benign.py` (thw_des = 1.5) and inside the range the lookup can hold at 15 m/s,
with the same readings and one added VALIDITY RULE: glance statistics are read only for a condition
in which no repeat drops below 14 m/s; a condition that brakes is reported, and its glances are not
interpreted.

CORRECTION, same night, while part b ran: the first version of this note called 1.5 s "the
authors' own benign-following value" and blamed part a's braking on a 2.0 s headway beyond the
calibration table. Both were wrong. `simulation_benign.py` stages an ONCOMING vehicle passing in the
adjacent lane at 150 m, not car following; its 1.5 s only feeds the calibration lookup. And part b's
G0 braked to a stop at 1.5 s as well, so the saturated-calibration explanation is withdrawn; the cause
is open. As far as can be found, the released repository never simulates sustained car following
(the rear-end runs brake the lead 0.6 s in).]

[ADAPTER CHECK G0x, pre-stated 2026-09-13 before it runs: the braking could come from this probe's
lead-replay class rather than from the model. G0x removes that class: the authors' own scripted lead
from `simulation_rear_end`, with its brake countdown set beyond the run (t_brake = 1e6), released
configuration, gaze choice off, 1.5 s headway. If G0x brakes like G0c, the braking belongs to the
released model in sustained following; if it does not, the replay adapter is implicated and every
glance result above is suspect.]

Output: replication/causation/gz1/gz1_gaze_choice_probe.md (+ pickles, log); part b under gz1/thw1.5/.
Run:    python replication/causation/gz1_gaze_choice_probe.py            (both conditions)
        python replication/causation/gz1_gaze_choice_probe.py --report   (report from pickles)
"""
from __future__ import annotations

import argparse
import math
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "replication"))

import tier2_rear_end as T2                                                 # noqa: E402
from run_rear_end_single import build_model_params, build_initial_state   # noqa: E402
from src.utils.simulation import find_parameters                          # noqa: E402

OUT = HERE / "gz1"
DT = 0.2
V = 15.0            # m/s, both vehicles: the lowest speed of the authors' calibration table
GAP = 30.0          # m bumper-to-bumper, 2.0 s headway: ordinary following, no conflict
T_STEPS = 75        # 15 s
BATCH = 4
ROAD_PREF = math.log(0.8)
PI_INIT = [0.8, 0.2]
CONDITIONS = {"G0": (0.01, 3.0), "G1": (1.0, 3.0), "G2": (0.01, 1000.0),   # perc_noise_factor, I_factor
              "G0c": (0.01, 3.0),                                          # control: gaze choice OFF
              "G0x": (0.01, 3.0)}                                          # adapter check: no replay class
GAZE_CHOICE = {"G0": True, "G1": True, "G2": True, "G0c": False, "G0x": False}
USE_REPLAY = {"G0x": False}                                                # default True


def run_condition(tag: str, perc_noise_factor: float, device, i_factor: float = 3.0) -> dict:
    out_path = OUT / f"{tag}.pkl"
    if out_path.exists():
        with open(out_path, "rb") as f:
            return pickle.load(f)

    gaze_choice = GAZE_CHOICE.get(tag, True)
    model_params = build_model_params()
    model_params["perc_noise_factor"] = perc_noise_factor
    model_params["road_pref"] = ROAD_PREF if gaze_choice else 0.0
    initial_state = build_initial_state()
    x_tar = GAP + initial_state["lf"] + initial_state["lr"]
    initial_state.update(v_ego=V, v_tar=V, x_tar=x_tar)
    v_diff, a_tar_min = find_parameters(V, model_params["EA_fac"], model_params["noise_pred_fac"],
                                        model_params["H"], model_params["d_phi_thres"], x_tar / V)
    model_params["v_diff"] = v_diff
    model_params["a_tar_min_intensity"] = -a_tar_min / initial_state["a_max"]

    torch.manual_seed(0)
    sim = T2.sim_rear_end
    Config, config = sim.set_config(initial_state, model_params, a_tar_brake=6.0)
    Config["v_ego_des"] = V + v_diff
    config["reward"]["v_mu"] = Config["v_ego_des"]
    config["T"] = Config["T"] = T_STEPS
    config["rollout_batch_size"] = BATCH
    config["init_state"]["t_brake"] = 1e6
    config["init_state"]["j_brake"] = 0.0
    config["decoder"]["I_factor"] = i_factor

    a_lead = np.zeros(T_STEPS + 1)
    saved_dyn, saved_run = sim.Dynamics_true, sim.run_simulation
    step_times: list[float] = []

    def replay_factory(**kw):
        return T2.DynamicsLeadReplay(a_lead, **kw)

    def run_simulation(cfg, agent, env, eta, b, w):
        # the one intervention: let the planner propose off-road gaze (not in the control)
        if gaze_choice:
            agent.planner.pi = torch.tensor(PI_INIT, device=agent.planner.device)
        agent.reset(b, w)
        o = env.reset(eta)
        env.dynamics.reset_clock()
        eta = env.state.clone()
        # a_disc from the planner is the whole planned sequence [H, batch, 2]; index 0 is the
        # gaze executed now. The share of off-road steps over the rest of the horizon is kept
        # too: a planner can plan a later glance without taking one yet.
        data = {k: [] for k in ("eta", "gaze_exec", "gaze_planned_off", "a_cont", "b_gaze")}
        for t in range(1, cfg["T"] + 1):
            t0 = time.time()
            with torch.no_grad():
                a_disc, a_cont = agent.choose_action(o, verbose=False)
            o = env.step(a_disc[0], a_cont[0])
            step_times.append(time.time() - t0)
            data["eta"].append(eta)
            data["gaze_exec"].append(a_disc[0])
            data["gaze_planned_off"].append(a_disc[..., 1].float().mean(0))
            data["a_cont"].append(a_cont[0])
            bw = agent.w / agent.w.sum(-1, keepdim=True)
            data["b_gaze"].append((agent.b[..., :2] * bw.unsqueeze(-1)).sum(-2))
            eta = env.state.clone()
            print(f"{tag} step {t}/{cfg['T']}  {step_times[-1]:.1f} s  gaze-off executed: "
                  f"{int(a_disc[0][..., 1].sum().item())}/{a_disc.shape[1]}  planned off share: "
                  f"{float(a_disc[..., 1].float().mean()):.2f}", flush=True)
            if t % 5 == 0 or t == cfg["T"]:
                with open(str(out_path) + ".partial", "wb") as f:
                    pickle.dump({k: torch.stack(v, 1).cpu().numpy() for k, v in data.items()},
                                f)
        return {k: torch.stack(v, 1).cpu().numpy() for k, v in data.items()}

    use_replay = USE_REPLAY.get(tag, True)
    if not use_replay:
        # the authors' own scripted lead: it cruises until t_brake, set beyond the run above
        env_reset_clock = lambda self: None                                     # noqa: E731
        if not hasattr(sim.Dynamics_true, "reset_clock"):
            sim.Dynamics_true.reset_clock = env_reset_clock
    sim.Dynamics_true = replay_factory if use_replay else saved_dyn
    sim.run_simulation = run_simulation
    try:
        t_start = time.time()
        data = sim.simulate(config, torch.device("cpu"))
        runtime = time.time() - t_start
    finally:
        sim.Dynamics_true, sim.run_simulation = saved_dyn, saved_run

    result = {"tag": tag, "perc_noise_factor": perc_noise_factor, "i_factor": i_factor,
              "road_pref": model_params["road_pref"], "gaze_choice": gaze_choice,
              "pi_init": PI_INIT, "T": T_STEPS, "batch": BATCH, "runtime_s": runtime,
              "step_times": step_times, "data": data}
    with open(out_path, "wb") as f:
        pickle.dump(result, f)
    p = Path(str(out_path) + ".partial")
    if p.exists():
        p.unlink()
    return result


def glance_stats(gaze_off: np.ndarray) -> dict:
    """gaze_off: [batch, T] booleans. Off-road share and completed/censored glance durations."""
    durations, censored = [], 0
    for row in gaze_off:
        run = 0
        for g in row:
            if g:
                run += 1
            elif run:
                durations.append(run * DT)
                run = 0
        if run:
            censored += 1
            durations.append(run * DT)
    return {"share_off": float(gaze_off.mean()), "n_glances": len(durations),
            "censored_at_end": censored,
            "median_s": float(np.median(durations)) if durations else float("nan"),
            "max_s": float(max(durations)) if durations else float("nan")}


def shrp2_reference() -> dict:
    import pandas as pd
    d = pd.read_csv(REPO / "replication/causation/data/b24_fig1_glances_shrp2.csv")
    off = d[d.duration_s > 0]
    p = off.probability / off.probability.sum()
    cdf = np.cumsum(p.to_numpy())
    med = float(off.duration_s.to_numpy()[np.searchsorted(cdf, 0.5)])
    return {"median_off_s": med, "max_off_s": float(off.duration_s.max())}


def report(results: dict) -> str:
    L = ["# Card GZ.1 -- can the released model choose its glances? (feasibility probe)", "",
         "Generated by `replication/causation/gz1_gaze_choice_probe.py`; setup and readings "
         "pre-stated in its docstring before the run. Do not edit by hand.", "",
         f"Steady following at {V} m/s, bumper gap {GAP:g} m ({GAP / V:g} s headway), lead at constant speed, "
         f"T = {T_STEPS} steps ({T_STEPS * DT:.0f} s), batch {BATCH}. Gaze choice enabled "
         f"(planner proposal {PI_INIT}), road_pref = log(0.8) = {ROAD_PREF:.3f}.", "",
         "| condition | gaze choice | perc_noise_factor | I_factor | steps done | off-road share (executed) | "
         "glances | censored at end | median glance [s] | longest [s] | "
         "planned off share (mean over horizon) | ego speed min [m/s] | repeats that stopped | "
         "first step below 14 m/s (median) | s per step (median) |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for tag, r in results.items():
        a = r["data"]["gaze_exec"]                   # [batch, T, 2] one-hot, executed gaze
        off = a[..., 1] > 0.5
        s = glance_stats(off)
        plan = float(np.mean(r["data"]["gaze_planned_off"]))
        st = np.median(r["step_times"]) if r.get("step_times") else float("nan")
        v = r["data"]["eta"][..., 4]                 # [batch, T]
        stopped = int((v.min(axis=1) < 0.5).sum())
        first_slow = [int(np.flatnonzero(row < 14.0)[0]) for row in v if (row < 14.0).any()]
        fs = f"{np.median(first_slow):.0f}" if first_slow else "never"
        L.append(f"| {tag} | {'on' if r.get('gaze_choice', True) else 'OFF (released)'} | "
                 f"{r['perc_noise_factor']} | {r.get('i_factor', '')} | {off.shape[1]} | "
                 f"{s['share_off']:.3f} | {s['n_glances']} | {s['censored_at_end']} | "
                 f"{s['median_s']:.2f} | {s['max_s']:.2f} | {plan:.3f} | {float(v.min()):.2f} | "
                 f"{stopped}/{v.shape[0]} | {fs} | {st:.1f} |")
    ref = shrp2_reference()
    L += ["", f"SHRP2 baseline reference (digitized, `replication/causation/data/"
          f"b24_fig1_glances_shrp2.csv`): about 80% on-road; median off-road glance "
          f"{ref['median_off_s']:.2f} s; longest bin {ref['max_off_s']:.1f} s.", ""]
    return "\n".join(L)


def main():
    global OUT, GAP
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--only", choices=list(CONDITIONS), default=None)
    ap.add_argument("--thw", type=float, default=2.0, help="time headway [s]; part b uses 1.5")
    args = ap.parse_args()
    GAP = args.thw * V
    if abs(args.thw - 2.0) > 1e-9:
        OUT = OUT / f"thw{args.thw:g}"
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    for tag, (pnf, ifac) in CONDITIONS.items():
        if args.only and tag != args.only:
            continue
        if args.report:
            p = OUT / f"{tag}.pkl"
            pp = Path(str(p) + ".partial")
            if p.exists():
                results[tag] = pickle.load(open(p, "rb"))
            elif pp.exists():
                results[tag] = {"perc_noise_factor": pnf, "i_factor": ifac,
                                "gaze_choice": GAZE_CHOICE.get(tag, True),
                                "data": pickle.load(open(pp, "rb")), "step_times": []}
            continue
        print(f"=== {tag}: perc_noise_factor {pnf}, I_factor {ifac}", flush=True)
        results[tag] = run_condition(tag, pnf, torch.device("cpu"), i_factor=ifac)
        print(f"=== {tag} done in {results[tag]['runtime_s']:.0f} s", flush=True)
    text = report(results)
    (OUT / "gz1_gaze_choice_probe.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
