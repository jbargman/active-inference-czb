# external — third-party material (not tracked in git)

Two things live here; both are restored rather than versioned:

- **`aica/`** — the authors' released code for Schumann et al. (2026), cloned from
  <https://github.com/tud-hri/Active-Inference-Collision-Avoidance> (non-commercial
  license permitting research use and benchmarking). It carries exactly one local
  patch, documented in `replication/PATCHES.md` — re-apply it after cloning.
- **`gs4bu-osfstorage-archive/`** — the paper's OSF data deposit (osf.io/gs4bu,
  3.1 GB): per-run setups, outcome analyses, and per-timestep pickles for all three
  scenarios including ablations. Download the archive from OSF and unzip here.
  Beware: the deposit README's stated axis order for the policy arrays is wrong;
  see `notes/05_validation.md` §4b.
- **`02_LTAPOD_DBIN/`** — the run protocol of the 2013 LTAP/OD test-track study
  (Bärgman, Smith & Werneke, 2015, TRF 35; `papers/comfort-zone-boundaries/`), placed here
  by Jonas on 2026-09-02: `DigitalRunProtocol_V2_121126resave_FULL.xlsx`, one row per run,
  26 participants. Column meanings as given by Jonas: `Training` = 1 is not to be used;
  `Broader_B_CZ` = 1 and `Finer_F_CZ` = 1 are the comfort-condition runs; `DreadZone_DZ_F` = 1
  the hurried runs; `SetPET` the manipulated post-encroachment time of the reference
  trajectory (a few are negative on Go runs: drivers accelerated, or the value is wrong;
  handle with care); `TurnedBefore` / `TurnedAfter` the Go / No-Go decision;
  `HowComfortable`, `HowRisky` (1..15) the self-reports after a Go; `IfTurn...` and
  `...After` after a No-Go; `Remove` = 1 flags repeated runs. The remaining columns are
  undocumented and unused. Analysis: `replication/czb/ltapod_testtrack.py`.
