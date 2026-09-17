"""
The export rule of `transfer/transfer_policy.yaml` (role `data`), enforced in code so that the
runner cannot write a table the bundle tool would refuse: no identifier columns, no per-person
rows, every row an aggregate over at least `min_n` observations.

The column lists below mirror the policy file's `forbidden_columns` and `person_columns`. If the
policy changes, change both; `tests/test_generative.py` checks that the two agree.
"""
from __future__ import annotations

import datetime as _dt
import subprocess
from pathlib import Path

import pandas as pd

FORBIDDEN_COLUMNS = {
    "event_id", "trip_id", "driver_id", "participant_id", "vin", "vehicle_id", "timestamp",
    "time_utc", "date", "datetime", "lat", "lon", "latitude", "longitude", "x_utm", "y_utm",
    "notes", "comment", "free_text",
}
PERSON_COLUMNS = {"driver", "participant", "subject", "driver_idx", "driver_index"}
COUNT_COLUMNS = ["n", "N", "count", "n_events", "n_drivers", "n_trips", "n_cells", "n_obs"]


class AggregateRuleError(ValueError):
    """A table violates the export rule and must not be written."""


def check_aggregate(df: pd.DataFrame, min_n: int = 5, count_col: str = "n") -> tuple[pd.DataFrame, int]:
    """Refuse identifier or per-person columns; drop rows whose count is below `min_n`.

    Returns the table that may be written and the number of rows dropped. A table without a
    count column is refused, because the rule cannot be checked on it.
    """
    cols = {c.lower() for c in df.columns}
    bad = sorted(cols & (FORBIDDEN_COLUMNS | PERSON_COLUMNS))
    if bad:
        raise AggregateRuleError(f"table carries forbidden column(s) {bad}")
    if count_col not in df.columns:
        raise AggregateRuleError(f"table has no count column {count_col!r}; the rule cannot be checked")
    keep = df[count_col].fillna(0).astype(float) >= min_n
    return df[keep].reset_index(drop=True), int((~keep).sum())


def write_aggregate(df: pd.DataFrame, path: str | Path, min_n: int = 5, count_col: str = "n") -> int:
    """Check, then write as CSV. Returns the number of rows suppressed."""
    kept, dropped = check_aggregate(df, min_n=min_n, count_col=count_col)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    kept.to_csv(path, index=False)
    return dropped


def run_record(script: str, params: dict) -> str:
    """The run record the export rule allows: script, commit, date, parameter values; no paths."""
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                                text=True, check=False).stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001 -- no git at the data site is an expected case
        commit = "unknown"
    date = _dt.date.today().isoformat()
    lines = [f"- script: `{script}`", f"- commit: `{commit}`", f"- date: {date}"]
    for k, v in params.items():
        lines.append(f"- {k}: {v}")
    return "\n".join(lines)
