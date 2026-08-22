"""Generate reference.js: ground-truth boundary values from src/comfortzone.

    python tools/czb_explorer/generate_reference.py

The explorer page re-implements the closed form in JavaScript; this file gives
it something authoritative to be checked against (in-page badge and
test_node.mjs). Regenerate whenever src/comfortzone/field.py changes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "src"))

from aidriver import BicycleParams, PreferenceParams  # noqa: E402
from comfortzone.field import critical_gap, critical_thw  # noqa: E402

SPEEDS = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0]
A_OV_MIN = [-9.0, -6.0, -4.5, -3.0, -1.5]
T_REACT = [0.4, 0.6, 1.0, 1.4, 2.0]
A_REQ = [2.0, 4.0, 6.0, 8.0]


def main() -> None:
    vehicle = BicycleParams()
    cases = []
    for v in SPEEDS:
        for a_ov in A_OV_MIN:
            for t in T_REACT:
                for a_req in A_REQ:
                    p = PreferenceParams(v_desired=v, a_other_min=a_ov,
                                         response_time=t, vehicle=vehicle)
                    dx = float(critical_gap(v, v, p, a_required=a_req))
                    thw = float(critical_thw(v, v, p, a_required=a_req))
                    cases.append({"v": v, "aOvMin": a_ov, "tReact": t,
                                  "aReq": a_req, "dx": round(dx, 6),
                                  "thw": round(thw, 6)})

    payload = {
        "L": vehicle.length,
        "generated_by": "tools/czb_explorer/generate_reference.py",
        "source": "src/comfortzone/field.py (critical_gap, critical_thw)",
        "cases": cases,
    }
    out = HERE / "reference.js"
    body = json.dumps(payload)
    out.write_text(
        "/* Generated file - do not edit. Regenerate with generate_reference.py */\n"
        "const CZB_REFERENCE = " + body + ";\n"
        "if (typeof module !== 'undefined') module.exports = CZB_REFERENCE;\n"
        "if (typeof window !== 'undefined') window.CZB_REFERENCE = CZB_REFERENCE;\n",
        encoding="utf-8")
    print("wrote", out.name, "with", len(cases), "cases")


if __name__ == "__main__":
    main()
