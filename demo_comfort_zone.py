"""
Comfort-zone boundaries from an active-inference preference function.

Produces:
  figures/czb_field.png        the comfort-zone scalar field in (speed, gap) space, with the
                               comfort and dread boundaries overlaid
  figures/czb_thw.png          the boundary expressed as critical time headway vs speed, for
                               several assumed braking limits and "extra motive" settings
  figures/czb_trajectory.png   the field evaluated along a rear-end trajectory, with the
                               exceedance point marked

Run:  python demo_comfort_zone.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from aidriver import PreferenceParams, RearEndScenario  # noqa: E402
from comfortzone import (  # noqa: E402
    INTERACTION_TERMS, boundary_curve, comfort_field, critical_gap, critical_thw,
    dread_zone_boundary,
)
from comfortzone.calibrate import deficit_along_trajectory, exceedance_events  # noqa: E402

FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(FIG, exist_ok=True)

BLUE, RED, GREY = "#2B6CB0", "#C53030", "#4A5568"


def fig_field():
    """Comfort-zone field over (ego speed, longitudinal gap), steady following."""
    p = PreferenceParams(v_desired=15.0, a_other_min=-6.0)
    v = np.linspace(5, 35, 160)
    dx = np.linspace(5, 140, 200)
    # only the interaction terms: including the speed preference would paint a bright
    # band at v_desired and hide the gap structure entirely
    f = comfort_field(p, "v", v, "dx", dx, couple={"v_other": "v"},
                      terms=INTERACTION_TERMS)

    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    # Background: the *required deceleration* to avoid a hard-braking lead after a 1 s
    # response. The comfort-zone field itself is a step here, because the SI defines p_safe
    # as an indicator on this quantity -- so plotting a_req shows the continuous structure
    # that the boundaries are level sets of, rather than a two-tone image.
    a_req = f.margin - p.a_max
    im = ax.pcolormesh(f.x, f.y, np.clip(a_req, -12, 0), shading="auto", cmap="magma")
    cb = fig.colorbar(im, ax=ax)
    cb.set_label(r"required deceleration $a_{\rm ego,req}$ [m/s$^2$]")


    dread = dread_zone_boundary(f)
    ax.plot(dread[:, 0], dread[:, 1], color=RED, lw=2.4,
            label=r"dread-zone boundary  ($a_{\rm req}=-a_{\max}$, 8 m/s$^2$)")

    for lim, ls, lab in [(4.0, "--", r"comfort boundary ($a_{\rm req}=-4$ m/s$^2$)"),
                         (2.0, ":", r"comfort boundary ($a_{\rm req}=-2$ m/s$^2$)")]:
        ax.plot(v, critical_gap(v, v, p, a_required=lim), color=BLUE, ls=ls, lw=2.0,
                label=lab)

    ax.set_xlabel("ego speed [m/s]  (lead vehicle at the same speed)")
    ax.set_ylabel("longitudinal separation $\\Delta x$ [m]")
    ax.set_title("Comfort-zone field and boundaries, car following")
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    ax.set_ylim(dx.min(), dx.max())
    fig.tight_layout()
    out = os.path.join(FIG, "czb_field.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print("wrote", out)
    return f


def fig_thw():
    """The same boundary as a critical time headway -- comparable to CZB literature."""
    v = np.linspace(5, 35, 200)
    fig, ax = plt.subplots(figsize=(8.4, 5.0))

    base = PreferenceParams(v_desired=15.0, a_other_min=-6.0)
    for lim, ls in [(8.0, "-"), (6.0, "--"), (4.0, "-."), (2.0, ":")]:
        ax.plot(v, critical_thw(v, v, base, a_required=lim), color=BLUE, ls=ls, lw=2.0,
                label=f"$|a_{{\\rm req}}|$ = {lim:.0f} m/s$^2$")

    hurried = PreferenceParams(v_desired=15.0, a_other_min=-6.0, response_time=0.6)
    ax.plot(v, critical_thw(v, v, hurried, a_required=4.0), color=RED, lw=2.0,
            label=r'"extra motive": $t_{\rm react}$ 1.0 $\to$ 0.6 s, $|a_{\rm req}|$=4')

    ax.axhspan(1.0, 2.0, color=GREY, alpha=0.12)
    ax.text(5.6, 1.85, "typical observed following THW", fontsize=9, color=GREY)

    ax.set_xlabel("speed [m/s]")
    ax.set_ylabel("critical time headway THW* [s]")
    ax.set_title("Comfort-zone boundary expressed as time headway")
    ax.legend(fontsize=9)
    ax.set_ylim(0, 6)
    fig.tight_layout()
    out = os.path.join(FIG, "czb_thw.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print("wrote", out)


def fig_trajectory():
    """
    Evaluate the field along a rear-end trajectory (kinematics only, no model roll-out) and
    show where the comfort zone is exceeded.
    """
    p = PreferenceParams(v_desired=15.0, a_other_min=-6.0)
    sc = RearEndScenario(v0=15.0, time_gap=1.5, t_brake=2.0)

    # a simple driver: constant speed, then brakes 1.2 s after the lead does
    dt = sc.veh.dt
    T = 60
    ego = np.zeros((T, 5))
    other = np.zeros((T, 5))
    e, o = sc.initial_states()
    a_ego = np.zeros(T)
    sc._a_other = 0.0
    for t in range(T):
        ego[t], other[t] = e, o
        if t * dt >= sc.t_brake + 1.2 and e[4] > 0.1:
            a_ego[t] = -5.0
        from aidriver import bicycle as bk
        e = bk.step(e, np.array([a_ego[t], 0.0]), sc.veh)
        o = bk.step(o, sc.other_action(t, o), sc.veh)

    eps = deficit_along_trajectory(ego, other, p, actions=np.stack([a_ego, np.zeros(T)], 1))
    tt = np.arange(T) * dt

    level = 100.0
    ex = exceedance_events(eps, level)

    fig, axes = plt.subplots(3, 1, figsize=(8.4, 7.4), sharex=True)
    axes[0].plot(tt, ego[:, 4], color=BLUE, lw=2, label="ego")
    axes[0].plot(tt, other[:, 4], color=GREY, lw=2, ls="--", label="lead")
    axes[0].set_ylabel("speed [m/s]"); axes[0].legend(fontsize=9)

    axes[1].plot(tt, other[:, 0] - ego[:, 0] - sc.veh.length, color=BLUE, lw=2)
    axes[1].set_ylabel("gap [m]")

    axes[2].semilogy(tt, np.maximum(eps, 1e-3), color=RED, lw=2)
    axes[2].axhline(level, color=GREY, ls=":", lw=1.5)
    axes[2].text(tt[-1], level, "  boundary c", va="center", fontsize=9, color=GREY)
    axes[2].set_ylabel(r"$\varepsilon$  (comfort-zone field)")
    axes[2].set_xlabel("time [s]")

    for ax in axes:
        ax.axvline(sc.t_brake, color=GREY, lw=1, alpha=0.6)
        if len(ex):
            ax.axvline(ex[0] * dt, color=RED, lw=1.4, ls="--", alpha=0.8)
    axes[0].set_title("Comfort-zone exceedance along a rear-end trajectory\n"
                      "grey = lead brakes, red dashed = comfort-zone boundary crossed")
    fig.tight_layout()
    out = os.path.join(FIG, "czb_trajectory.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print("wrote", out)

    if len(ex):
        print(f"  lead brakes at {sc.t_brake:.1f}s; comfort zone exceeded at "
              f"{ex[0]*dt:.1f}s (lead time before ego brakes: "
              f"{sc.t_brake + 1.2 - ex[0]*dt:.1f}s)")
    return eps


def summary_table():
    p = PreferenceParams(v_desired=15.0, a_other_min=-6.0)
    print("\nCritical time headway THW* [s] (steady following, lead may brake at 6 m/s^2)")
    print(f"{'v [m/s]':>8} " + " ".join(f"{f'|a|={a:.0f}':>9}" for a in [8, 6, 4, 2]))
    for v in [10, 15, 20, 25, 30]:
        row = " ".join(f"{float(critical_thw(v, v, p, a_required=a)):9.2f}"
                       for a in [8, 6, 4, 2])
        print(f"{v:8.0f} {row}")


if __name__ == "__main__":
    fig_field()
    fig_thw()
    fig_trajectory()
    summary_table()
