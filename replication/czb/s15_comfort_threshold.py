"""
Card S1.5 -- the comfort threshold: is the braking-margin quantity a comfort-zone boundary once it
is thresholded at a COMFORTABLE deceleration, "a bit further out"?

THE PRE-REGISTRATION. Everything in this docstring was written before the run, on 2026-09-22.

WHERE THE CARD COMES FROM
-------------------------
Jonas, 2026-09-22, of the released braking-margin term, which thresholds `required_deceleration`
(SI Eq. 51) at the ego's physical maximum a_max = 8 m/s^2:

> *"it makes sense too, but if it was fitted with a different maximum decel and a position a bit
> further out, it could be CZB, or?"*

`handover_2026-09-22.md` §6 turned that into this card: "score the margin on card JJ.2's cells,
folds and metric, sweeping the comfort threshold and the standoff, with the primary fixed in
advance by motivation".

WHAT WRITING THE CARD DOWN SHOWED, BEFORE ANY SCORE -- three things, and they reshape it
------------------------------------------------------------------------------------------
**(1) "A different maximum decel" is not a parameter to sweep. It is the fitted level.** Every axis
in this project is given the three-parameter threshold model

    share who intervene = lapse + (1 - lapse) * Phi((x - c) / sigma),

so with x = log(demanded deceleration) the level c IS the population's median threshold
deceleration, exp(c), in m/s^2. Card S1.1 therefore already fitted Jonas's "different maximum
decel" -- it never REPORTED it. What is testable, and new, is whether that fitted level is a
deceleration anyone would call comfortable. That is rule 2 below, and it is the heart of the card.

**(2) On this study the assumed lead braking and the standoff are the same parameter.** The lead's
speed is the same in every one of the 378 cells (section 0 of the report measures it), and in the
released formula the assumed lead braking a_OV enters only through the lead's stopping distance
v_lead^2 / (2 |a_OV|) -- one constant per study. A standoff subtracts another constant from the same
available distance. So card S1.1's exploratory sweep over a_OV WAS a sweep over the standoff: its
winning -10 m/s^2 is the released -6 with the ego stopping about 20.8 m further out
(`comfortzone.margin.equivalent_standoff`; property-tested in `tests/test_margin.py`). This matters
for Jonas's ruling S11.Q2 (-6 primary, -10 sensitivity): at -6 card S1.1's own table gives 0.2230,
which does NOT beat the gap's 0.1522; the 0.1409 that does is the -10 row. The report's section 1
reproduces both and tests the identity numerically.

**(3) The level can be read as a comfortable deceleration only under a counterfactual a driver
would hold in ordinary driving.** "The lead brakes at 6 m/s^2 to a standstill" is a worst case, and
the deceleration it demands of the ego is the price of insuring against it, not the braking the
scene calls for. So the card scores TWO counterfactuals, both in `src/comfortzone/margin.py`:

  **stops**  the released one. The lead brakes at a_lead to a standstill; the ego must stop
             `standoff` short of the released stopping point.
  **holds**  the lead keeps its speed; the ego must only match it, `standoff` short of contact.
             This is the kinematic required deceleration the registered R.2 script scored at 0.2888
             (its "a_req", dv / (2 TTC)) -- but with the reaction time and the standoff that make
             it sensitive to the gap, which that one did not have.

WHAT I HAD SEEN BEFORE WRITING THIS, stated because it bears on what counts as a prediction
-----------------------------------------------------------------------------------------------
Card S1.1's report, including its whole sweep table. And, in an interactive look at the scene
states made to design this card (no score was computed): that the lead speed is 24.98 m/s in every
cell and the ego's runs 26.6 to 36.5 m/s; and that across the 288 post-onset cells the released
`required_deceleration` runs -7.0 to -26.6 m/s^2 at a_OV -6 and -9.0 to -158 m/s^2 at -10. The last
of those is why I expect rule 2 to FAIL for the `stops` counterfactual, and I say so here rather
than discover it in the report. I had not computed the `holds` quantity on these cells, nor any
score of anything with a standoff.

CELLS, FOLDS, METRIC -- card JJ.2's, which are the registered R.2 script's, imported: 378 cells, 288
post-onset and 90 pre-onset (CP1), leave-one-starting-TTC-out (6 folds), weighted RMSE on cell
shares with weights n. Axis x = log(demand), demand capped at DEMAND_CAP before the log (below).
Comparators on file: the gap threshold 0.1522 (`out/cutin2_field_vs_gap.md`), the ungated looming
rule 0.1137 and the gated 0.1027, card G.1's pre-onset 0.0319 (`out/cutin2_gate.md`), chance 0.320,
the noise floor 0.118.

THE PRIMARY ARMS, fixed here by motivation and not by any score
----------------------------------------------------------------
  **P1  stops,  a_lead = -6 m/s^2, t_react = 1.0 s, standoff = 2 m.**
  **P2  holds,                     t_react = 1.0 s, standoff = 2 m.**
  a_lead -6    the released value, and Jonas's ruling S11.Q2.
  t_react 1.0  the released value.
  standoff 2 m the standstill gap s0 of the intelligent driver model (Treiber, Hennecke & Helbing,
               2000, Phys. Rev. E 62, 1805-1824, https://doi.org/10.1103/PhysRevE.62.1805), the
               most widely used value for "how far short of the vehicle ahead a driver stops".
               It is a convention, not a measurement of these participants (query S15.Q2).

THE RULES
---------
  Rule 0  REPRODUCTION. `stops` with standoff 0 must reproduce card S1.1's 0.2230 (a_OV -6) and
          0.1409 (a_OV -10) to within 0.0005, and (-6, the equivalent standoff) must reproduce the
          -10 score to within 0.0005. Otherwise the card stops: its construction is not S1.1's.
  Rule 1  AXIS. An arm is credited as an axis if its post-onset held-out score is at most 0.1422:
          the gap threshold's 0.1522 less the 0.01 margin this project requires of anything that
          claims to improve on a simpler rule (Jonas's standing ruling of 2026-09-03). It is
          "competitive with looming" at 0.1237 or below (the ungated 0.1137 plus the same margin).
  Rule 2  THE COMFORT READING. The fitted median level exp(c), from the full post-onset fit, lies
          in **[1.0, 4.0] m/s^2**. Upper end: the 3.4 m/s^2 that AASHTO's stopping-sight-distance
          model takes as a deceleration most drivers find comfortable, and the 3.0 m/s^2 (10 ft/s^2)
          of the ITE yellow-interval formula, with a margin above them; both from memory and
          UNVERIFIED in this repository (query S15.Q1). Lower end: below about 1 m/s^2 is engine
          braking and ordinary speed regulation, not a braking event. Above 8 m/s^2 is the released
          a_max: a level there is a dread boundary by the model's own definition.
  Rule 3  THE GATE. The full post-onset fit applied to the 90 pre-onset cells scores below 0.05.
          Reported twice: with no gate (does the threshold form contain the gate? -- the handover's
          hope), and with card G.1's gate FROZEN at its fitted values (m_lat 0.149 m, s_l 0.990 m,
          T 3 s; nothing refitted but the axis's own three parameters).
  VERDICT, per arm: **CZB CANDIDATE** if rules 1 and 2 both hold; **AXIS ONLY** if rule 1 holds and
          rule 2 fails -- it orders the cells, but its level is not a comfortable deceleration, so
          it is a proximity rule written in deceleration units; **NOT CREDITED** if rule 1 fails.
          Rule 3 decides whether a credited arm needs G.1's gate; it does not decide the verdict.

THE FITTED ARMS -- Jonas said "if it was FITTED", so the fair version fits them
--------------------------------------------------------------------------------
For each counterfactual, the grid t_react in {0, 0.5, 1, 1.5, 2} s by standoff in
{0, 2, 5, 10, 20, 30, 40} m (35 settings; a_lead stays -6, since by (2) it is the standoff). The
NESTED held-out score chooses the setting inside each fold by its training error, so no test cell
ever informs the choice; rule 1 applies to that score, rule 2 to the level at the setting the full
sample chooses. The whole grid is reported. 40 m is about 1.6 s of headway at the lead's speed, more
than "a bit further out" can mean; the grid stops there on purpose.

PREDICTIONS, written before the run
-----------------------------------
  P1: about 0.22, by the identity (a 2 m standoff at -6 is a_OV -6.24 with none), level about
      12 m/s^2. NOT CREDITED, failing both rules.
  stops, fitted: about 0.13 to 0.14, choosing a large standoff and a short reaction time -- S1.1's
      sweep improves monotonically toward the wall limit -- with a level far above 8 m/s^2. AXIS
      ONLY at best.
  P2 and holds, fitted: I do not know. The level should fall near or inside the comfort band,
      because the quantity is the braking the scene actually calls for; whether it ORDERS the cells
      is the open question. Within a matched-TTC row the plain kinematic version is anti-ordered
      (a smaller gap at the same TTC means a smaller closing speed, hence a smaller demand, while
      the participants respond MORE), and only the reaction time and the standoff can turn that.
  Rule 3 without a gate: fails for every arm. Nothing in either quantity knows the other vehicle is
      still in the next lane, and a threshold cannot supply that; the scoring model already IS a
      threshold.

DEMAND_CAP = 100 m/s^2. Where no room is left the demand is infinite, and card S1.1 dropped every
setting with such a cell (its blank rows). Here the demand is capped instead, so those settings can
be scored: a capped cell is predicted at the ceiling 1 - lapse, which is what "no braking avoids
it" should predict. 100 m/s^2 is about 10 g, beyond any level a fit can reach, and the primary
arms are rerun at 50 and 200 to show the choice does not matter. Capped cells are counted per arm.

Output: replication/czb/out/s15_comfort_threshold.md, out/s15_comfort_threshold_grid.csv,
        out/s15_comfort_threshold_cells.csv
Run:    python replication/czb/s15_comfort_threshold.py
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm, spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import cutin2_field_vs_gap as R            # noqa: E402  registered R.2 script (read only)
import cutin2_gate as CG                   # noqa: E402  card G.1 (read only)
import jj2_rollout_cutin as J2             # noqa: E402  card JJ.2 (read only)
import s11_comfort_margin as S11           # noqa: E402  card S1.1 (read only)
from comfortzone.margin import (           # noqa: E402
    RELEASED_LENGTH_M, demanded_deceleration, equivalent_standoff,
)

OUT = HERE / "out"

# --- comparators and criteria, all on file ---------------------------------------------
GAP_RULE = 0.1522            # out/cutin2_field_vs_gap.md
LOOMING_UNGATED = 0.1137     # out/cutin2_gate.md section 1, model c
LOOMING_GATED = 0.1027       # ibid., model k
G1_CP1 = 0.0319              # ibid., section 2
CHANCE, NOISE_FLOOR = 0.320, 0.118
MARGIN = 0.01                # Jonas's standing ruling of 2026-09-03
RULE1 = GAP_RULE - MARGIN
RULE1_LOOMING = LOOMING_UNGATED + MARGIN
COMFORT_BAND = (1.0, 4.0)    # m/s^2, rule 2; motivation in the docstring, query S15.Q1
A_MAX_RELEASED = 8.0         # m/s^2, `PreferenceParams.a_max`
CP1_CRIT = 0.05              # card JJ.2's rule (b)
S11_AT_6, S11_AT_10 = 0.2230, 0.1409     # out/s11_comfort_margin.md section 2
REPRO_TOL = 0.0005
G1_M_LAT, G1_S_L = 0.149, 0.990          # out/cutin2_gate.md, the fitted gate

A_LEAD = -6.0                # released; ruling S11.Q2
T_PRIMARY, STANDOFF_PRIMARY = 1.0, 2.0
T_GRID = (0.0, 0.5, 1.0, 1.5, 2.0)
STANDOFF_GRID = (0.0, 2.0, 5.0, 10.0, 20.0, 30.0, 40.0)
DEMAND_CAP = 100.0
CAP_SENSITIVITY = (50.0, 200.0)
FLOOR = 1e-6


# ---------------------------------------------------------------------------------
# 1. the axis
# ---------------------------------------------------------------------------------
def demand(d: pd.DataFrame, lead: str, t_react: float, standoff: float,
           a_lead: float = A_LEAD) -> np.ndarray:
    return np.asarray(demanded_deceleration(
        d.x_rel.to_numpy(float), d.v_ego.to_numpy(float), d.v_oth.to_numpy(float),
        lead=lead, a_lead=a_lead, t_react=t_react, standoff=standoff), float)


def log_axis(dem: np.ndarray, cap: float = DEMAND_CAP) -> np.ndarray:
    return np.log(np.clip(dem, FLOOR, cap))


# ---------------------------------------------------------------------------------
# 2. scoring: the registered three-parameter model, with and without G.1's frozen gate
# ---------------------------------------------------------------------------------
def predict_gated(th, x, g):
    b = 1.0 / (1.0 + np.exp(-th[0]))
    return b + (1.0 - b) * g * norm.cdf((x - th[1]) / np.exp(th[2]))


def fit_gated(x, g, y, w):
    """The registered fitter's starts and objective, with a fixed multiplier g on the core."""
    lo, hi = np.quantile(x, [0.1, 0.9])
    spread = max(np.std(x), 1e-6)
    best, best_val = None, np.inf
    for c0 in np.linspace(lo, hi, 5):
        for ls0 in (np.log(spread), np.log(spread / 4 + 1e-9)):
            r = minimize(lambda th: float(np.sum(w * (predict_gated(th, x, g) - y) ** 2)),
                         np.array([-2.0, c0, ls0]), method="L-BFGS-B")
            if r.fun < best_val:
                best, best_val = r.x, r.fun
    return best


def fold_fits(post: pd.DataFrame, x: np.ndarray, g: np.ndarray | None = None):
    """Per fold: the training wRMSE and the test predictions. g = None is the registered model."""
    y, w = post.p.to_numpy(float), post.n.to_numpy(float)
    folds = post.ttc_start.to_numpy(float)
    pred = np.full_like(y, np.nan)
    train_err = {}
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        if g is None:
            th = R.fit(x[tr], y[tr], w[tr], +1.0)
            fit_tr, pred[te] = R.predict(th, x[tr], +1.0), R.predict(th, x[te], +1.0)
        else:
            th = fit_gated(x[tr], g[tr], y[tr], w[tr])
            fit_tr, pred[te] = predict_gated(th, x[tr], g[tr]), predict_gated(th, x[te], g[te])
        train_err[float(f)] = R.wrmse(y[tr], fit_tr, w[tr])
    return R.wrmse(y, pred, w), pred, train_err


def score(d: pd.DataFrame, x: np.ndarray, gate: np.ndarray | None = None) -> dict:
    dd = d.assign(x=x, g=1.0 if gate is None else gate)
    post = dd[dd.cp != "CP1"].reset_index(drop=True)
    cp1 = dd[dd.cp == "CP1"].reset_index(drop=True)
    xp, y, w = post.x.to_numpy(float), post.p.to_numpy(float), post.n.to_numpy(float)
    gp = None if gate is None else post.g.to_numpy(float)
    held, pred, train_err = fold_fits(post, xp, gp)
    if gate is None:
        th = R.fit(xp, y, w, +1.0)
        pred1 = R.predict(th, cp1.x.to_numpy(float), +1.0)
    else:
        th = fit_gated(xp, gp, y, w)
        pred1 = predict_gated(th, cp1.x.to_numpy(float), cp1.g.to_numpy(float))
    agree, nrows, _ = J2.matched_rows(post, xp, +1.0)
    return {"post": held, "cp1": R.wrmse(cp1.p.to_numpy(float), pred1, cp1.n.to_numpy(float)),
            "rows": agree, "n_rows": nrows,
            "rho_p": float(spearmanr(xp, y).statistic),
            "rho_gap": float(spearmanr(xp, post.distance).statistic),
            "level": float(np.exp(th[1])), "sigma": float(np.exp(th[2])),
            "lapse": float(1.0 / (1.0 + np.exp(-th[0]))),
            "pred": pred, "train_err": train_err}


def verdict(post: float, level: float) -> str:
    if post > RULE1:
        return "NOT CREDITED"
    ok2 = COMFORT_BAND[0] <= level <= COMFORT_BAND[1]
    return "CZB CANDIDATE" if ok2 else "AXIS ONLY"


def nested(d: pd.DataFrame, grid: dict) -> tuple[float, dict]:
    """Choose the setting inside each fold by its training error; score the pooled test cells."""
    post = d[d.cp != "CP1"].reset_index(drop=True)
    y, w = post.p.to_numpy(float), post.n.to_numpy(float)
    folds = post.ttc_start.to_numpy(float)
    pred = np.full_like(y, np.nan)
    chosen = {}
    for f in np.unique(folds):
        key = min(grid, key=lambda k: grid[k]["train_err"][float(f)])
        chosen[float(f)] = key
        pred[folds == f] = grid[key]["pred"][folds == f]
    return R.wrmse(y, pred, w), chosen


# ---------------------------------------------------------------------------------
# 3. the run
# ---------------------------------------------------------------------------------
def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    d = S11.scene_states(cells)
    lat = CG.lateral_states(d.video)
    d = d.merge(lat[["video", "l0", "ldot"]], on="video")
    gate = np.asarray(CG.gate(G1_M_LAT, np.log(G1_S_L), d.l0.to_numpy(float),
                              d.ldot.to_numpy(float)), float)
    post_mask = (d.cp != "CP1").to_numpy()
    v_lead = float(d.v_oth.mean())
    s_eq = equivalent_standoff(v_lead, A_LEAD, -10.0)

    # --- rule 0 -----------------------------------------------------------------------
    rep6 = score(d, log_axis(demand(d, "stops", 1.0, 0.0)))
    rep10 = score(d, log_axis(demand(d, "stops", 1.0, 0.0, a_lead=-10.0)))
    rep_eq = score(d, log_axis(demand(d, "stops", 1.0, s_eq)))
    rule0 = (abs(rep6["post"] - S11_AT_6) <= REPRO_TOL and abs(rep10["post"] - S11_AT_10) <= REPRO_TOL
             and abs(rep_eq["post"] - rep10["post"]) <= REPRO_TOL)
    rho_ident = float(spearmanr(demand(d, "stops", 1.0, s_eq),
                                demand(d, "stops", 1.0, 0.0, a_lead=-10.0)).statistic)
    print(f"rule 0: {rep6['post']:.4f} {rep10['post']:.4f} {rep_eq['post']:.4f} -> {rule0}",
          flush=True)

    # --- the primaries, ungated and with the frozen gate --------------------------------
    arms = {"P1": ("stops", T_PRIMARY, STANDOFF_PRIMARY), "P2": ("holds", T_PRIMARY, STANDOFF_PRIMARY)}
    prim, prim_g, capped, cap_sens = {}, {}, {}, {}
    for k, (lead, t, s) in arms.items():
        dem = demand(d, lead, t, s)
        capped[k] = (int(np.sum(dem[post_mask] >= DEMAND_CAP)), int(np.sum(dem[~post_mask] >= DEMAND_CAP)))
        prim[k] = score(d, log_axis(dem))
        prim_g[k] = score(d, log_axis(dem), gate)
        cap_sens[k] = {c: score(d, log_axis(dem, c))["post"] for c in CAP_SENSITIVITY}
        print(f"{k}: {prim[k]['post']:.4f} level {prim[k]['level']:.2f}", flush=True)

    # --- the grids and the nested fits --------------------------------------------------
    grids, nest, best_full, best_g = {}, {}, {}, {}
    rows = []
    for lead in ("stops", "holds"):
        grid = {}
        for t in T_GRID:
            for s in STANDOFF_GRID:
                dem = demand(d, lead, t, s)
                sc = score(d, log_axis(dem))
                sc["n_cap"] = int(np.sum(dem[post_mask] >= DEMAND_CAP))
                grid[(t, s)] = sc
                rows.append({"lead": lead, "t_react": t, "standoff": s,
                             **{k: sc[k] for k in ("post", "cp1", "rows", "n_rows", "rho_p",
                                                   "rho_gap", "level", "sigma", "lapse", "n_cap")},
                             "train_full": float(np.mean(list(sc["train_err"].values())))})
                print(f"{lead} t={t} s={s}: {sc['post']:.4f} level {sc['level']:.2f}", flush=True)
        grids[lead] = grid
        nest[lead] = nested(d, grid)
        # the full sample's choice: the setting with the smallest mean training error
        best_full[lead] = min(grid, key=lambda k: np.mean(list(grid[k]["train_err"].values())))
        t, s = best_full[lead]
        best_g[lead] = score(d, log_axis(demand(d, lead, t, s)), gate)
    pd.DataFrame(rows).to_csv(OUT / "s15_comfort_threshold_grid.csv", index=False)

    # per-cell values of the primaries, so the report's numbers can be recomputed
    cells_out = d[["video", "cp", "p", "n", "ttc_start", "ttc_true", "distance", "dv_kph", "x_rel",
                   "v_ego", "v_oth", "l0", "ldot"]].copy()
    cells_out["gate_g1"] = gate
    cells_out["demand_P1"] = demand(d, "stops", T_PRIMARY, STANDOFF_PRIMARY)
    cells_out["demand_P2"] = demand(d, "holds", T_PRIMARY, STANDOFF_PRIMARY)
    cells_out["demand_released"] = demand(d, "stops", 1.0, 0.0)
    cells_out.to_csv(OUT / "s15_comfort_threshold_cells.csv", index=False)

    # --- steady following, on file (the seven numbers of the 2026-09-22 worklog entry) ------
    v110 = 110.0 / 3.6
    hw = np.arange(0.5, 3.51, 0.5)
    dx_hw = hw * v110 + RELEASED_LENGTH_M          # headway as a bumper gap; dx is centre to centre
    follow = pd.DataFrame({
        "headway": hw,
        "released": demanded_deceleration(dx_hw, v110, v110, lead="stops", standoff=0.0),
        "P1": demanded_deceleration(dx_hw, v110, v110, lead="stops", standoff=STANDOFF_PRIMARY),
        "P2": demanded_deceleration(dx_hw, v110, v110, lead="holds", standoff=STANDOFF_PRIMARY)})

    # ---------------------------------------------------------------------------------
    # the report
    # ---------------------------------------------------------------------------------
    def row(lab, s, extra=""):
        return (f"| {lab} | {s['post']:.4f} | {s['cp1']:.4f} | {s['rows']} of {s['n_rows']} |"
                f" {s['rho_p']:+.3f} | {s['rho_gap']:+.3f} | {s['level']:.2f} | {s['sigma']:.2f} |"
                f" {extra} |")

    def band(level):
        if level > A_MAX_RELEASED:
            return "above a_max = 8: a dread level"
        if level > COMFORT_BAND[1]:
            return "above the comfort band"
        return "inside the comfort band" if level >= COMFORT_BAND[0] else "below the comfort band"

    L = ["# Card S1.5 -- the comfort threshold: the braking-margin quantity, thresholded at a"
         " comfortable deceleration, a bit further out", "",
         "Generated by `replication/czb/s15_comfort_threshold.py`; the arms, the grids, the rules"
         " and the predictions were pre-stated in its docstring before the run. Do not edit by"
         " hand.", "",
         "Jonas, 2026-09-22, of the released braking-margin term: *\"if it was fitted with a"
         " different maximum decel and a position a bit further out, it could be CZB, or?\"* The"
         " card takes that literally. **The \"different maximum decel\" is the fitted level of the"
         " threshold model, in m/s^2**, so it is not swept: it is read off the fit and held against"
         " what a comfortable deceleration is (rule 2). **The \"position a bit further out\" is a"
         " standoff**, added to the released formula with nothing else changed"
         " (`src/comfortzone/margin.py`, 24 property checks). Two counterfactuals about the lead"
         " are scored: **stops** (the released one: the lead brakes at 6 m/s^2 to a standstill)"
         " and **holds** (the lead keeps its speed and the ego must only match it).", "",
         "## 0 The design fact the card rests on, and steady following on file", "",
         f"The lead's speed is **{d.v_oth.mean():.2f} m/s in every cell** (range"
         f" {d.v_oth.min():.3f} to {d.v_oth.max():.3f}); the ego's runs {d.v_ego.min():.1f} to"
         f" {d.v_ego.max():.1f} m/s. In the released formula the assumed lead braking enters only"
         " as the lead's stopping distance v_lead^2 / (2 |a_OV|), which is therefore ONE constant"
         " on this study, and a standoff subtracts another constant from the same available"
         " distance. **So on this study the assumed lead braking and the standoff are the same"
         f" parameter**: a_OV = -10 is a_OV = -6 with the ego stopping **{s_eq:.1f} m** further"
         " out. Card S1.1's exploratory sweep over a_OV was a sweep over the standoff.", "",
         "Steady following at 110 km/h, zero closing speed, the headway read as a bumper gap --"
         " the seven numbers of the 2026-09-22 worklog entry, now from a committed script:", "",
         "| headway [s] | released (stops, no standoff) [m/s^2] | P1 (stops, 2 m) | P2 (holds, 2 m) |",
         "|---|---|---|---|"]
    for _, r in follow.iterrows():
        L.append(f"| {r.headway:.1f} | {r.released:.2f} | {r.P1:.2f} | {r.P2:.2f} |")
    L += ["",
          "The `holds` demand is zero at every headway, because nothing is closing: **under that"
          " counterfactual steady following has no comfort boundary at all, and under `stops` it"
          " has one only because the driver is assumed to insure against the lead braking.** Which"
          " of the two a driver holds is therefore the substantive question, and it is what rule 2"
          " reads.", "",
          "## 1 Rule 0: reproduction, and the identity", "",
          "| check | value | required |", "|---|---|---|",
          f"| stops, a_OV -6, no standoff, against card S1.1 | {rep6['post']:.4f} against"
          f" {S11_AT_6:.4f} | within {REPRO_TOL} |",
          f"| stops, a_OV -10, no standoff, against card S1.1 | {rep10['post']:.4f} against"
          f" {S11_AT_10:.4f} | within {REPRO_TOL} |",
          f"| stops, a_OV -6 with the equivalent standoff {s_eq:.2f} m, against the -10 score |"
          f" {rep_eq['post']:.4f} against {rep10['post']:.4f}; rank correlation of the two demands"
          f" {rho_ident:+.6f} | within {REPRO_TOL} |", "",
          f"**Rule 0 {'PASSES' if rule0 else 'FAILS -- the card stops here'}.**"
          + (" The identity holds numerically: card S1.1's headline 0.1409 is the released"
             f" counterfactual with a {s_eq:.1f} m standoff. And at Jonas's ruled primary (S11.Q2:"
             f" -6) the comfort margin scores {rep6['post']:.4f}, which does **not** beat the gap's"
             f" {GAP_RULE:.4f}; every statement that \"the comfort margin beats the gap\" is a"
             " statement about the -10 row." if rule0 else ""), ""]
    if not rule0:
        (OUT / "s15_comfort_threshold.md").write_text("\n".join(L), encoding="utf-8")
        print("rule 0 failed; stopping")
        return

    hdr = ("| arm | post-onset held out | pre-onset | matched-TTC rows | rho(share) | rho(gap) |"
           " median level [m/s^2] | sigma [log] | verdict |")
    sep = "|---|---|---|---|---|---|---|---|---|"
    L += ["## 2 The primary arms", "",
          f"Rule 1 credits an arm at {RULE1:.4f} or below (the gap's {GAP_RULE:.4f} less the 0.01"
          f" margin); rule 2 asks for a median level inside [{COMFORT_BAND[0]:g},"
          f" {COMFORT_BAND[1]:g}] m/s^2. Comparators: looming {LOOMING_UNGATED:.4f} ungated and"
          f" {LOOMING_GATED:.4f} gated, chance {CHANCE:.3f}, the noise floor {NOISE_FLOOR:.3f}.", "",
          hdr, sep]
    labels = {"P1": "**P1** stops, a_lead -6, t 1.0 s, standoff 2 m",
              "P2": "**P2** holds, t 1.0 s, standoff 2 m"}
    for k in ("P1", "P2"):
        s = prim[k]
        L.append(row(labels[k], s, f"**{verdict(s['post'], s['level'])}** ({band(s['level'])})"))
    L.append(row("reference: the released function (stops, -6, no standoff)", rep6,
                 f"{verdict(rep6['post'], rep6['level'])} ({band(rep6['level'])})"))
    L.append(row(f"reference: card S1.1's -10 row == -6 with {s_eq:.1f} m", rep10,
                 f"{verdict(rep10['post'], rep10['level'])} ({band(rep10['level'])})"))
    L += ["",
          "Capped cells (no room left, demand set to the cap): "
          + "; ".join(f"{k} {capped[k][0]} of 288 post-onset and {capped[k][1]} of 90 pre-onset"
                      for k in ("P1", "P2")) + ". Cap sensitivity, post-onset held out at a cap of "
          + " / ".join(f"{c:g}" for c in CAP_SENSITIVITY) + " m/s^2: "
          + "; ".join(f"{k} " + " / ".join(f"{cap_sens[k][c]:.4f}" for c in CAP_SENSITIVITY)
                      for k in ("P1", "P2")) + ".", ""]

    L += ["## 3 The fitted arms (nested: the setting is chosen inside each fold)", "",
          "| counterfactual | nested held out | settings chosen across the 6 folds (t_react,"
          " standoff) | the full sample's setting | its level [m/s^2] | verdict |",
          "|---|---|---|---|---|---|"]
    for lead in ("stops", "holds"):
        sc, chosen = nest[lead]
        bf = grids[lead][best_full[lead]]
        ch = ", ".join(f"({t:g}, {s:g})" for t, s in chosen.values())
        L.append(f"| {lead} | **{sc:.4f}** | {ch} | ({best_full[lead][0]:g} s,"
                 f" {best_full[lead][1]:g} m) | {bf['level']:.2f} |"
                 f" **{verdict(sc, bf['level'])}** ({band(bf['level'])}) |")
    L.append("")
    for lead in ("stops", "holds"):
        L += [f"### The whole grid, `{lead}`", "",
              "Post-onset held out / median level in m/s^2. Rows are the reaction time, columns"
              " the standoff; * marks settings with capped post-onset cells.", "",
              "| t_react [s] | " + " | ".join(f"{s:g} m" for s in STANDOFF_GRID) + " |",
              "|---|" + "---|" * len(STANDOFF_GRID)]
        for t in T_GRID:
            L.append(f"| {t:g} | " + " | ".join(
                f"{grids[lead][(t, s)]['post']:.4f} / {grids[lead][(t, s)]['level']:.1f}"
                + ("*" if grids[lead][(t, s)]["n_cap"] else "") for s in STANDOFF_GRID) + " |")
        L.append("")

    L += ["## 4 Rule 3: the gate", "",
          f"The full post-onset fit applied to the 90 pre-onset cells; the criterion is {CP1_CRIT}"
          f" and card G.1's gated looming rule scores {G1_CP1:.4f}. \"Frozen gate\" multiplies the"
          f" threshold core by card G.1's gate at its fitted values (m_lat {G1_M_LAT} m, s_l"
          f" {G1_S_L} m, 3 s), refitting only the axis's own three parameters.", "",
          "| arm | no gate: post / pre-onset | frozen G.1 gate: post / pre-onset | level with the"
          " gate [m/s^2] |", "|---|---|---|---|"]
    for k in ("P1", "P2"):
        L.append(f"| {labels[k]} | {prim[k]['post']:.4f} / {prim[k]['cp1']:.4f} |"
                 f" {prim_g[k]['post']:.4f} / {prim_g[k]['cp1']:.4f} | {prim_g[k]['level']:.2f} |")
    for lead in ("stops", "holds"):
        t, s = best_full[lead]
        bf = grids[lead][best_full[lead]]
        L.append(f"| {lead}, the full sample's fitted setting ({t:g} s, {s:g} m) |"
                 f" {bf['post']:.4f} / {bf['cp1']:.4f} | {best_g[lead]['post']:.4f} /"
                 f" {best_g[lead]['cp1']:.4f} | {best_g[lead]['level']:.2f} |")
    L.append("")

    # --- the verdict paragraph, assembled from the numbers and nothing else -------------
    v = {k: verdict(prim[k]["post"], prim[k]["level"]) for k in ("P1", "P2")}
    vn = {lead: verdict(nest[lead][0], grids[lead][best_full[lead]]["level"])
          for lead in ("stops", "holds")}
    any_cand = "CZB CANDIDATE" in list(v.values()) + list(vn.values())
    gate_free = any(prim[k]["cp1"] < CP1_CRIT for k in prim) or any(
        grids[lead][best_full[lead]]["cp1"] < CP1_CRIT for lead in grids)
    L += ["## 5 The verdict on the pre-stated rules", "",
          f"* **P1 (stops, the released counterfactual with a 2 m standoff): {v['P1']}.**"
          f" {prim['P1']['post']:.4f} held out, median level {prim['P1']['level']:.1f} m/s^2"
          f" ({band(prim['P1']['level'])}).",
          f"* **P2 (holds): {v['P2']}.** {prim['P2']['post']:.4f} held out, median level"
          f" {prim['P2']['level']:.1f} m/s^2 ({band(prim['P2']['level'])}).",
          f"* **stops, fitted: {vn['stops']}.** Nested {nest['stops'][0]:.4f}; the full sample"
          f" chooses ({best_full['stops'][0]:g} s, {best_full['stops'][1]:g} m) with a median"
          f" level of {grids['stops'][best_full['stops']]['level']:.1f} m/s^2.",
          f"* **holds, fitted: {vn['holds']}.** Nested {nest['holds'][0]:.4f}; the full sample"
          f" chooses ({best_full['holds'][0]:g} s, {best_full['holds'][1]:g} m) with a median"
          f" level of {grids['holds'][best_full['holds']]['level']:.1f} m/s^2.",
          f"* **Rule 3 without a gate: {'MET by at least one arm' if gate_free else 'fails for every arm'}.**"
          " The threshold form does not supply the gate; the scoring model already is a"
          " threshold, and neither quantity knows the other vehicle is still in the next lane.", "",
          ("**At least one arm is a CZB candidate by the pre-stated rules.** Section 2 and 3 say"
           " which; the next step is the per-driver fit of its two constants."
           if any_cand else
           "**No arm is a CZB candidate by the pre-stated rules.** Where the quantity orders the"
           " cells its level is not a comfortable deceleration, and where its level is comfortable"
           " it does not order the cells. See the worklog entry of this card for the reading."),
          "",
          "## 6 A note on the released formula, recorded and not corrected", "",
          "Comparing final stopping positions, as SI Eq. 51 does, is sufficient only while the ego"
          " brakes no harder than the lead. When the demanded deceleration exceeds the assumed"
          " lead braking, the two speeds equalise before the lead stands still and the smallest"
          " gap occurs then, so the stopping-point criterion understates what is needed. In the"
          f" 288 post-onset cells the released demand runs"
          f" {np.min(cells_out.demand_released[post_mask]):.1f} to"
          f" {np.nanmax(np.where(np.isfinite(cells_out.demand_released[post_mask]), cells_out.demand_released[post_mask], np.nan)):.1f}"
          " m/s^2 against an assumed lead braking of 6, so every one of them is in that regime."
          " The `stops` arms reproduce the released formula regardless, because the card's"
          " question is about that formula (query S15.Q3).", "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "s15_comfort_threshold.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[-20:]))


if __name__ == "__main__":
    main()
