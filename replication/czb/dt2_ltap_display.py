"""
Card DT.2 -- the display transform on the left turn (LTAP/OD): does the video-track agreement survive,
and what does it say about which quantity the video participants judged?

THE PRE-REGISTRATION. Written 2026-09-26, before any number below was computed.

WHY. Jonas, 2026-09-26: "assess the same for the LTAP/OD scenario -- how does this change the
comparison between the test track (which is correct perception for the driver) and the crowd-source
experiment(s)." Card TT.1 found the video's left-turn boundary reproduces the 2013 test track's
(PET_50 2.18 s pooled, 2.42 s first exposure (card EX.2), against 2.45 s on the track). Card B.3.v2
found that on video the left-turn responses follow the oncoming car's DISTANCE or LOOMING (held-out
0.0558 / 0.0540), not its arrival-time separation (0.1121). The display transform
(`docs/display_transform.md`, k = 0.4243 at the defaults) leaves times unchanged but makes the
oncoming car look 1/k = 2.36 times farther and loom k times slower. So the track (real optics) and
the video (minified optics) can only agree if the participants' criterion is display-invariant.

WHAT IS COMPUTED. The 50 km/h video stimuli at the decision moment (card B.3.v2's cells,
`out/ltap_cells.csv`): per design PET, the egocentric range to the oncoming car r, its range rate,
width, distance to the conflict point D, time to arrival TTA, the looming at the ego's eye
theta_dot = W rdot / (r^2 + W^2/4). The track is mapped onto the same stimulus geometry (assumption,
stated: the video reproduces the track scenario at 50 km/h, same PET definition; the protocol has no
decision-moment kinematics). For each candidate criterion X -- TIME (TTA, equivalently PET),
egocentric DISTANCE r, conflict-point distance D, LOOMING theta_dot, ANGULAR SIZE theta -- assume
video and track drivers share one boundary in PERCEIVED X. The track's boundary is X at the track's
PET_50 (real optics). The transform-predicted video PET_50 is the design PET at which the video's
PERCEIVED X (transform on) equals it; the untransformed prediction (transform off) is the track's
PET_50 for every X. Interpolation of log X on PET over the nine 50 km/h cells, linear extrapolation
beyond. Also: the EFFECTIVE GAIN k_eff that would make each criterion consistent with the observed
video PET_50 (k_eff = 1: no display effect; k_eff = 0.42: the full geometric minification), with
the interval from the observed PET_50 +/- 1.96 SE.
Observed values read from the tracked outputs of TT.1 (`out/ltapod_testtrack.md`: track PET_50,
video pooled PET_50 and SE) and EX.2 (`out/ex2_first_exposure_levels.md`: first exposure, SE).

THE RULE. Primary: the first-exposure video PET_50 (EX.2, the level comparable to the track's
single-session drivers). A criterion is CONSISTENT with the display transform if its
transform-predicted video PET_50 lies within 0.5 s of the observed (TT.1's design-resolution
tolerance); otherwise INCONSISTENT.

PREDICTIONS. TIME: consistent (display-invariant; 2.45 against 2.42). DISTANCE (r and D), LOOMING and
ANGULAR SIZE: INCONSISTENT -- the predicted video PET_50 lies below 1 s (the oncoming must be
k-times closer on screen to look as close); k_eff for distance and looming between 0.7 and 1.4,
i.e. the participants behave as if the display had NOT minified the scene. Reading, if so: the
video participants judged a distance-like quantity that the display does not distort (scene-relative
distance, e.g. the oncoming's position against the intersection's own layout), or the track drivers
judged time and the 50 km/h agreement is a coincidence -- the track's single speed cannot tell.

FIXED AFTER THE FIRST RUN, 2026-09-26 (dated per standing rule 4): the first run read the
first-exposure PET_50 from the wrong section of EX.2's output (the cut-in's session-term row, -3.38
log rad/s, came first), so the observed value printed as 3.38 s. The reader now takes the left-turn
section's row (2.42 s). Nothing else changes; the first run's output was not committed.

Output: replication/czb/out/dt2_ltap_display.md
Run:    python replication/czb/dt2_ltap_display.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
from comfortzone import display as D  # noqa: E402

OUT = HERE / "out"
TOL = 0.5


def read_observed() -> dict:
    tt = (OUT / "ltapod_testtrack.md").read_text(encoding="utf-8")
    m = re.search(r"PET_50 track ([\d.]+) s \(SE ([\d.]+)\); PET_50 video ([\d.]+) s \(SE ([\d.]+)\)", tt)
    ex = (OUT / "ex2_first_exposure_levels.md").read_text(encoding="utf-8")
    ex = ex[ex.index("### The left turn at 50 km/h"):]          # the left-turn section (fix, see docstring)
    m2 = re.search(r"session term \(primary\) \| -([\d.]+) \(([\d.]+)\)", ex)
    return {"track": float(m[1]), "track_se": float(m[2]), "pooled": float(m[3]), "pooled_se": float(m[4]),
            "first": float(m2[1]), "first_se": float(m2[2])}


def interp_pet(pet, logx, target):
    """PET at which log X equals target: piecewise linear, extrapolated from the end segments."""
    order = np.argsort(logx)
    xs, ps = logx[order], pet[order]
    if target < xs[0]:
        return float(ps[0] + (target - xs[0]) * (ps[1] - ps[0]) / (xs[1] - xs[0]))
    if target > xs[-1]:
        return float(ps[-1] + (target - xs[-1]) * (ps[-1] - ps[-2]) / (xs[-1] - xs[-2]))
    return float(np.interp(target, xs, ps))


def at_pet(pet, logx, p):
    """log X at design PET p (piecewise linear in PET, extrapolated)."""
    if p < pet[0]:
        return float(logx[0] + (p - pet[0]) * (logx[1] - logx[0]) / (pet[1] - pet[0]))
    if p > pet[-1]:
        return float(logx[-1] + (p - pet[-1]) * (logx[-1] - logx[-2]) / (pet[-1] - pet[-2]))
    return float(np.interp(p, pet, logx))


def main() -> None:
    g = D.load_geometry()
    k = D.gain(g)
    obs = read_observed()
    c = pd.read_csv(OUT / "ltap_cells.csv")
    c = c[c.speed_kph == 50].sort_values("pet").reset_index(drop=True)
    pet = c.pet.to_numpy(float)
    r, rdot, W = c.range_ego_onc.to_numpy(float), c.range_rate.to_numpy(float), c.w_onc.to_numpy(float)
    rendered = {"time (TTA)": c.tta.to_numpy(float), "egocentric distance r": r,
                "conflict-point distance D": c.d_onc.to_numpy(float),
                "looming at the eye": D.looming(r, rdot, W, None),
                "angular size": D.perceived(r, rdot, W, None)["theta"]}
    pp = D.perceived(r, rdot, W, g)
    perceived = {"time (TTA)": c.tta.to_numpy(float), "egocentric distance r": pp["r"],
                 "conflict-point distance D": c.d_onc.to_numpy(float) / k,
                 "looming at the eye": pp["theta_dot"], "angular size": pp["theta"]}
    L = ["# Card DT.2 -- the display transform on the left turn (LTAP/OD): video against test track", "",
         "Generated by `replication/czb/dt2_ltap_display.py`; pre-stated in its docstring before the run."
         " Do not edit by hand.", "",
         f"Gain k = {k:.4f} (spec defaults). Observed PET_50: track **{obs['track']:.2f} s** (SE {obs['track_se']:.2f},"
         f" TT.1); video first exposure **{obs['first']:.2f} s** (SE {obs['first_se']:.2f}, EX.2, primary);"
         f" video pooled {obs['pooled']:.2f} s (SE {obs['pooled_se']:.2f}, TT.1).", "",
         "The 50 km/h video stimuli at the decision moment:", "",
         "| design PET [s] | TTA [s] | range r [m] | D [m] | looming, rendered [rad/s] | looming, perceived | angular size, rendered [deg] | perceived [deg] |",
         "|---|---|---|---|---|---|---|---|"]
    for i in range(len(c)):
        L.append(f"| {pet[i]:.1f} | {c.tta[i]:.2f} | {r[i]:.1f} | {c.d_onc[i]:.1f} | {rendered['looming at the eye'][i]:.4f} |"
                 f" {perceived['looming at the eye'][i]:.4f} | {np.degrees(rendered['angular size'][i]):.2f} |"
                 f" {np.degrees(perceived['angular size'][i]):.2f} |")
    L += ["", "## Same perceived boundary on track and video: the video PET_50 each criterion predicts", "",
          "| criterion | track boundary (real optics) | predicted video PET_50, transform OFF | predicted, transform ON |"
          " observed (first exposure) | ON: verdict | effective gain k_eff [95%] |", "|---|---|---|---|---|---|---|"]
    lo_p, hi_p = obs["first"] - 1.96 * obs["first_se"], obs["first"] + 1.96 * obs["first_se"]
    verdicts = {}
    for name in rendered:
        lr, lp = np.log(rendered[name]), np.log(perceived[name])
        target = at_pet(pet, lr, obs["track"])
        pred_on = interp_pet(pet, lp, target)
        v = "CONSISTENT" if abs(pred_on - obs["first"]) <= TOL else "INCONSISTENT"
        verdicts[name] = v
        if name == "time (TTA)":
            keff = "- (invariant)"
        else:
            # perceived = rendered x gain^e (e = -1 distance, +1 looming and size); solve at the observed PET
            e = -1.0 if "distance" in name else 1.0
            ke = [np.exp((target - at_pet(pet, lr, p)) / e) for p in (obs["first"], lo_p, hi_p)]
            keff = f"{ke[0]:.2f} [{min(ke[1:]):.2f}, {max(ke[1:]):.2f}]"
        unit = {"time (TTA)": "s", "angular size": "rad"}.get(name, "m" if "distance" in name else "rad/s")
        L.append(f"| {name} | {np.exp(target):.4g} {unit} | {obs['track']:.2f} | **{pred_on:.2f}** | {obs['first']:.2f} |"
                 f" **{v}** | {keff} |")
    L += ["", f"Rule: CONSISTENT if the transform-ON prediction lies within {TOL} s of the observed first-exposure"
          " PET_50. With the transform OFF every criterion predicts the track's PET_50 by construction (the same"
          " stimulus mapping), which is TT.1's agreement.", "",
          "Reading the effective gain: k_eff = 1 means the participants' boundary behaves as if the display had"
          " not minified the scene; k_eff = k means the full geometric minification acted on their criterion.",
          ""]
    (OUT / "dt2_ltap_display.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
