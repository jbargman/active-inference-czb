"""
Check a directory of interface files against `transfer/interface_schema.yaml`.

Run at the data site on the adapter's output before any shared script touches it, and at the
home site on the synthetic fixture. Reports every problem it finds and exits 2 if any is a
hard failure. It reads the files; it never copies or prints data rows.

    python transfer/validate_interface.py <dir> [--schema transfer/interface_schema.yaml]
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bundle import load_yaml  # noqa: E402


def _float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def validate(d: Path, schema: dict):
    hard, soft = [], []
    ids = schema["identifiers"]
    ev_rx = re.compile(re.search(r"\^.*\$", ids["event_id"]).group(0))
    dr_rx = re.compile(re.search(r"\^.*\$", ids["driver_id"]).group(0))
    meta_path = d / "events.csv"
    if not meta_path.exists():
        return [f"{meta_path.name} missing"], soft
    with meta_path.open(encoding="utf-8", newline="") as f:
        meta = list(csv.DictReader(f))
    mcols = schema["metadata"]["columns"]
    if meta:
        missing = [c for c, spec in mcols.items() if spec.get("required") and c not in meta[0]]
        if missing:
            hard.append(f"events.csv lacks required columns {missing}")
    ts_cols = schema["time_series"]["columns"]
    required_ts = [c for c, spec in ts_cols.items() if spec.get("required")]
    seen_events = set()
    for row in meta:
        eid = row.get("event_id", "")
        if not ev_rx.match(eid):
            hard.append(f"event_id {eid!r} does not match {ev_rx.pattern}")
        if not dr_rx.match(row.get("driver_id", "")):
            hard.append(f"{eid}: driver_id {row.get('driver_id')!r} does not match {dr_rx.pattern}")
        if eid in seen_events:
            hard.append(f"{eid}: duplicate event_id")
        seen_events.add(eid)
        for c, spec in mcols.items():
            if "values" in spec and row.get(c) not in (None, "", "NaN") and row.get(c) not in [str(v) for v in spec["values"]]:
                soft.append(f"{eid}: {c} = {row.get(c)!r} not in {spec['values']}")
        tb = row.get("t_brake_onset", "")
        if tb == "0" or tb == "0.0" or tb == "0.00":
            hard.append(f"{eid}: t_brake_onset is 0; use NaN for an absent response")
        p = d / f"{eid}.csv"
        if not p.exists():
            hard.append(f"{eid}: time-series file missing")
            continue
        with p.open(encoding="utf-8", newline="") as f:
            r = csv.reader(f)
            header = next(r, [])
            miss = [c for c in required_ts if c not in header]
            if miss:
                hard.append(f"{eid}: time series lacks {miss}")
                continue
            it = header.index("t")
            iv = header.index("valid")
            icls = header.index("oth_class")
            t_prev, n, steps, n_valid = None, 0, set(), 0
            classes = set(ts_cols["oth_class"]["values"])
            for line in r:
                n += 1
                t = _float(line[it])
                if t is None:
                    hard.append(f"{eid}: non-numeric t at row {n}")
                    break
                if t_prev is not None:
                    if t <= t_prev:
                        hard.append(f"{eid}: t not monotonic at row {n}")
                        break
                    steps.add(round(t - t_prev, 4))
                t_prev = t
                n_valid += line[iv].strip() == "1"
                if line[icls] not in classes:
                    soft.append(f"{eid}: oth_class {line[icls]!r} not in {sorted(classes)}")
                    break
            if n == 0:
                hard.append(f"{eid}: empty time series")
                continue
            if len(steps) > 1 and (max(steps) - min(steps)) > 1e-3:
                soft.append(f"{eid}: non-uniform time step ({min(steps)} to {max(steps)} s)")
            if steps and max(steps) > 0.1 + 1e-6:
                hard.append(f"{eid}: sampling slower than 10 Hz (step {max(steps)} s)")
            if n_valid < 0.5 * n:
                soft.append(f"{eid}: partner track valid in only {n_valid}/{n} rows")
            tc = _float(row.get("t_conflict_onset"))
            if tc is not None and t_prev is not None and not (0 <= tc <= t_prev):
                hard.append(f"{eid}: t_conflict_onset {tc} outside the time series")
            tb_f = _float(tb)
            if tb_f is not None and not math.isnan(tb_f) and t_prev is not None and not (0 <= tb_f <= t_prev):
                hard.append(f"{eid}: t_brake_onset {tb_f} outside the time series")
    stray = [p.name for p in d.glob("*.csv") if p.name != "events.csv" and p.name != "drivers.csv"
             and p.stem not in seen_events]
    if stray:
        soft.append(f"time-series files with no metadata row: {stray[:5]}{'...' if len(stray) > 5 else ''}")
    return hard, soft


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir")
    ap.add_argument("--schema", default=str(Path(__file__).resolve().parent / "interface_schema.yaml"))
    a = ap.parse_args(argv)
    schema = load_yaml(a.schema)
    hard, soft = validate(Path(a.dir), schema)
    for h in hard:
        print("FAIL ", h)
    for s in soft:
        print("warn ", s)
    n_ev = len([p for p in Path(a.dir).glob("*.csv") if p.name not in ("events.csv", "drivers.csv")])
    print(f"{n_ev} event files; {len(hard)} failures, {len(soft)} warnings")
    return 2 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
