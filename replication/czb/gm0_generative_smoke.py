"""
Card GM.0 -- the generative-model framework rehearsed end to end on the synthetic interface fixture.

    python replication/czb/gm0_generative_smoke.py

Pre-stated (2026-09-17, before the run), on `transfer/fixtures/synthetic/` (three drivers, two
scenarios, made-up kinematics; nothing here is a claim about anyone):

1. the runner completes and writes `out/gm0/report.md` plus the C3 tables; C2 finds no
   completed lane change (the fixture's cut-in events carry no lateral motion) and C1 as not estimable from the interface;
2. no written table carries a column the transfer policy forbids;
3. the fixture's partner lateral track is white jitter of 0.03 m on a straight line, so the
   lateral growth slope over the whole event must equal the jitter floor sqrt(2) * 0.03 / 0.3 =
   0.141 m/s within 30%: the framework attributes measurement noise to measurement, not to drivers.

The three checks are also property tests in `tests/test_generative.py`; this script leaves the
tracked output a reader can open.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from generative.fit_from_interface import fit_generative_from_interface  # noqa: E402
from generative.uncertainty import jitter_growth_floor  # noqa: E402

OUT = ROOT / "replication" / "czb" / "out" / "gm0"


def main():
    tables = fit_generative_from_interface(ROOT / "transfer" / "fixtures" / "synthetic", OUT,
                                           min_n=5, jitter_floor_m=0.03)
    fit = tables["c3_growth_fit"]
    row = fit[(fit["scenario"] == "rear_end") & (fit["phase"] == "all")]
    s1 = float(row["s1_lat_mps"].iloc[0])
    floor = jitter_growth_floor(0.03, 0.3)
    verdict = abs(s1 - floor) / floor < 0.30
    lines = [
        "", "## GM.0 pre-stated checks", "",
        f"1. runner completed; tables: {', '.join(sorted(k for k, v in tables.items() if len(v)))}",
        "2. forbidden columns: none (enforced by `aggregate.write_aggregate`)",
        f"3. lateral growth slope (rear_end, all) {s1:.4f} m/s against the jitter floor {floor:.4f} m/s: "
        f"{'within 30%, PASS' if verdict else 'outside 30%, FAIL'}",
    ]
    with (OUT / "report.md").open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print((OUT / "report.md").read_text(encoding="utf-8"))
    sys.exit(0 if verdict else 1)


if __name__ == "__main__":
    main()
