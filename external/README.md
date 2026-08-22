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
