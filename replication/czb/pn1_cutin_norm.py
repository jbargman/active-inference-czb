"""
Card PN.1 -- a norm for a vehicle legitimately changing into our lane: the released positional
form against a crossing norm, on the second cut-in study's 90 recorded lane changes.

PRE-STATED before the run (2026-09-13). The proposal itself is `docs/cutin_norm_proposal.md`;
the norms are `src/comfortzone/norms.py` (tests in `tests/test_norms.py`).

WHAT IS COMPUTED, per trace, from the kinematics only:
  offset    the cutting-in vehicle's lateral offset from its own lane centre toward ours:
            lane_width - |y_target - y_ego|, on a 0.3 s backward moving average (the ego is
            centred in the destination lane; the road's slight angle to world x cancels in the
            difference). lane_width = 3.5 m, the study's lane spacing; d = the vehicle's width.
  v_toward  d(offset)/dt over a 0.3 s backward window (the same window as cards G.1 and HS.1).

D1 (diagnostic) -- when would each norm withdraw trust?
  own_lane_norm   first time the weight falls below 0.5 (it jumps from 1 to 0.001 when the body
                  leaves its lane). Reported as latency after card HS.1's joint surprise onset
                  (sigma0 0.1 m, out/hs1_onsets.csv), by lane-change duration.
                  EXPECTED: the latency grows with duration -- trust is withdrawn later for a
                  slower lane change -- which is the pace dependence the pipeline review found
                  participants do not show.
  crossing_norm   the minimum weight while the vehicle straddles the boundary.
                  EXPECTED: at or near 1 on every trace. This checks that the proposal's
                  lateral-speed band covers the study's own lane changes; it is a check of a
                  parameter choice against kinematics, never against responses.

[Corrected after the first run, 2026-09-13: D1's crossing-norm minimum was taken over every
trace sample after the clip start, including the simulator's last seconds after the final clip
of a trace had ended. Those frames were never shown, and at short starting TTC they carry
stalled frames and a drift back as the ego catches the target (e.g. LC_dv14_Tlc4p0_TTC02,
18-20 s). The minimum is now taken over the shown window only (up to the trace's latest clip
end); the whole-trace value is still reported beside it. First run: 0.032 at 3 s and 4 s
durations, with straddling lateral speeds down to -1.05 m/s. Nothing else changed.]

S1 (secondary, pre-stated rule) -- does the released-style norm's withdrawal moment work as the
onset gate? The EL.1 axis with a step gate g = 1 once own_lane_norm has withdrawn trust by the clip
end, no gate parameter fitted: exactly card HS.1's surprise-gate model with a different onset,
scored with HS.1's code, folds and criteria. CREDITED iff CP1 out-of-sample wRMSE < 0.05 AND
post-onset held-out wRMSE <= card G.1's gated score + 0.01. EXPECTED: not credited on the second
condition, because the withdrawal comes late for slow lane changes.

Output: replication/czb/out/pn1_cutin_norm.md
Run:    python replication/czb/pn1_cutin_norm.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import cutin2_field_vs_gap as R           # noqa: E402
import cutin2_two_axis as T               # noqa: E402
import cutin2_gate as G                   # noqa: E402
import hs1_situational_surprise as HS     # noqa: E402
from comfortzone.norms import crossing_norm, own_lane_norm  # noqa: E402

OUT = HERE / "out"
LW = 3.5
WINDOW = 0.3


def lane_change_series(sc):
    t = sc["grid"]
    dt = float(np.median(np.diff(t)))
    k = max(1, int(round(WINDOW / dt)))
    yrel = sc["tracks"][sc["tar"]].y - sc["tracks"][sc["ego"]].y
    yrel_s = pd.Series(yrel).rolling(k, min_periods=1).mean().to_numpy()
    offset = LW - np.abs(yrel_s)
    v = np.zeros_like(offset)
    v[k:] = (offset[k:] - offset[:-k]) / (t[k:] - t[:-k])
    v[:k] = v[k]
    return t, offset, v


def main() -> None:
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    ons = pd.read_csv(OUT / "hs1_onsets.csv")
    scenes = HS.study2_scenes(cells)

    rows = []
    trace_w = {}
    for key, sc in scenes.items():
        t, offset, v = lane_change_series(sc)
        d = sc["meta"][sc["tar"]]["width"]
        w_own = own_lane_norm(offset, LW, d)
        w_cross = crossing_norm(offset, v, LW, d)
        alw = 0.5 * (LW - d)
        straddle = (offset >= alw) & (offset <= LW - alw)
        sub = ons[ons.trace == key]
        s_first = float(sub.s_t.min())
        e_last = float(sub.e_t.max())
        after = t >= s_first + 1.0
        shown = after & (t <= e_last)
        hit = np.flatnonzero(after & (w_own < 0.5))
        t_withdraw = float(t[hit[0]]) if len(hit) else np.nan
        t_surprise = float(sub["on_joint_0.1"].dropna().min()) if sub["on_joint_0.1"].notna().any() else np.nan
        lcd = float(sub.lcd.iloc[0])

        def stat(mask, arr, fn):
            sel = straddle & mask
            return float(fn(arr[sel])) if sel.any() else np.nan
        rows.append({"trace": key, "lcd": lcd, "t_withdraw_own": t_withdraw,
                     "t_surprise": t_surprise, "latency_own": t_withdraw - t_surprise,
                     "min_cross_straddle": stat(shown, w_cross, np.min),
                     "v_straddle_min": stat(shown, v, np.min),
                     "v_straddle_max": stat(shown, v, np.max),
                     "min_cross_straddle_whole_trace": stat(after, w_cross, np.min),
                     "straddle_shown_s": float((straddle & shown).sum() * np.median(np.diff(t)))})
        trace_w[key] = (t, w_own)
    diag = pd.DataFrame(rows)

    L = ["# Card PN.1 -- a norm for a vehicle changing into our lane", "",
         "Generated by `replication/czb/pn1_cutin_norm.py`; computations, expectations and the "
         "secondary rule pre-stated in its docstring. The proposal is `docs/cutin_norm_proposal.md`. "
         "Do not edit by hand.", "",
         "## D1 When each norm withdraws trust, on the 90 recorded lane changes", "",
         "| lane-change duration | traces | own-lane norm: withdrawal after the surprise onset, median (range) [s] | "
         "crossing norm: lowest weight while straddling, shown window | straddling time shown, median [s] | "
         "lateral speed while straddling, shown [m/s] | crossing norm lowest, whole trace (not shown) |",
         "|---|---|---|---|---|---|---|"]
    for lcd, g in diag.groupby("lcd"):
        L.append(f"| {lcd:.0f} s | {len(g)} | {g.latency_own.median():+.2f} "
                 f"({g.latency_own.min():+.2f} to {g.latency_own.max():+.2f}) | "
                 f"{g.min_cross_straddle.min():.3f} | {g.straddle_shown_s.median():.2f} | "
                 f"{g.v_straddle_min.min():.2f}-{g.v_straddle_max.max():.2f} | "
                 f"{g.min_cross_straddle_whole_trace.min():.3f} |")
    by = diag.groupby("lcd").latency_own.median()
    grows = bool(by.is_monotonic_increasing and by.iloc[-1] - by.iloc[0] > 0.1)
    L += ["", f"Own-lane withdrawal latency {'GROWS' if grows else 'does NOT grow'} with lane-change "
          f"duration (median {by.iloc[0]:+.2f} s at {by.index[0]:.0f} s to {by.iloc[-1]:+.2f} s at "
          f"{by.index[-1]:.0f} s). Crossing norm's lowest weight over every straddling sample shown "
          f"to participants: {diag.min_cross_straddle.min():.3f}.", ""]

    # ------------------------------------------------------------------ S1: withdrawal as a gate
    post = cells[cells.cp != "CP1"].reset_index(drop=True)
    cpo = cells[cells.cp == "CP1"].reset_index(drop=True)
    st = G.lateral_states(cells.video)
    post = post.merge(st[["video", "l0", "ldot"]], on="video", how="left")
    cpo = cpo.merge(st[["video", "l0", "ldot"]], on="video", how="left")

    def withdraw_gate(df):
        g = []
        for vid in df.video:
            m = R.VIDEO_RE.match(vid)
            key = f"LC_dv{m['dv']}_Tlc{m['tlc']}_TTC{int(m['ttc']):02d}"
            e_t = R._f(m["e"])
            tw = float(diag.loc[diag.trace == key, "t_withdraw_own"].iloc[0])
            g.append(1.0 if np.isfinite(tw) and tw <= e_t else 0.0)
        return np.array(g)

    y, w = post.p.to_numpy(float), post.n.to_numpy(float)
    y1, w1 = cpo.p.to_numpy(float), cpo.n.to_numpy(float)
    folds = post.ttc_start.to_numpy(float)
    g, g1 = withdraw_gate(post), withdraw_gate(cpo)
    pred = np.full_like(y, np.nan)
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        ut, vt = G.axes(post[tr])
        p = HS.fit_sgated(ut, vt, g[tr], y[tr], w[tr])
        ue, ve = G.axes(post[te])
        pred[te] = HS.predict_sgated(p, ue, ve, g[te])
    ho = G.wrmse(y, pred, w)
    u, v = G.axes(post)
    u1, v1 = G.axes(cpo)
    c1 = G.wrmse(y1, HS.predict_sgated(HS.fit_sgated(u, v, g, y, w), u1, v1, g1), w1)
    # card G.1's gated score, read from its tracked report rather than refitted (the multi-start
    # gated fit is the slow part, and HS.1 reproduces it in the same session)
    import re
    rep = (OUT / "cutin2_gate.md").read_text(encoding="utf-8")
    r_k = float(re.search(r"\(k\) same rule with the binding gate \| 6 \| ([0-9.]+)", rep).group(1))
    ok1, ok2 = c1 < 0.05, ho <= r_k + 0.01
    verdict = ("CREDITED" if ok1 and ok2 else "NOT CREDITED: failed " + ", ".join(
        n for n, ok in (("CP1 < 0.05", ok1), (f"post-onset <= {r_k + 0.01:.4f}", ok2)) if not ok))
    open_by_cp = post.assign(g=g).groupby("cp").g.mean()
    L += ["## S1 The released-style norm's withdrawal moment as the onset gate", "",
          "| gate | gate parameters fitted | post-onset held-out wRMSE | CP1 out of sample |",
          "|---|---|---|---|",
          f"| card G.1 clearance gate (`out/cutin2_gate.md`) | 2 | {r_k:.4f} | 0.0319 |",
          f"| own-lane norm withdrawal | 0 | {ho:.4f} | {c1:.4f} |", "",
          "Share of cells with the gate open, by clip point: "
          + ", ".join(f"{cp} {val:.2f}" for cp, val in open_by_cp.items())
          + f"; CP1 {g1.mean():.2f}.", "",
          f"**S1 (pre-stated rule): {verdict}** (CP1 {c1:.4f}, post-onset {ho:.4f}).", ""]

    diag.to_csv(OUT / "pn1_cutin_norm_traces.csv", index=False)
    (OUT / "pn1_cutin_norm.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
