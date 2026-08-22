# Local modifications to `external/aica`

The upstream repository (`github.com/tud-hri/Active-Inference-Collision-Avoidance`,
Zenodo `10.5281/zenodo.20049511`) is kept as close to pristine as possible. Exactly **one**
file is modified.

## 1. `src/common/bicycle.py:42` — hardcoded CUDA device

**Upstream:**

```python
self.delta_max = torch.tensor(torch.pi / 4, device = 'cuda')
```

**Problem:** unconditional `device='cuda'`. On a CPU-only machine this raises
`AssertionError: Torch not compiled with CUDA enabled` during `Dynamics.__init__`, before any
simulation can start. It also would not match the `device` argument threaded through the rest
of the constructor even on a GPU machine with a non-zero device index.

**Patch:**

```python
self.delta_max = torch.tensor(
    torch.pi / 4,
    device='cuda' if torch.cuda.is_available() else 'cpu')
```

Behavior on a CUDA machine is unchanged.

## Not patched, worked around instead

- **`simulation_*.py` module-level imports.** Each simulation script ends with
  `import Analysis_<name>` and `import visualization_<name>` at module scope, *outside* the
  `if __name__ == "__main__"` guard. Importing the module therefore immediately tries to read
  `Results_<name>/Setups_<name>.xlsx`, which does not exist until a full sweep has been run,
  and raises `FileNotFoundError`. Rather than edit the file, `run_rear_end_single.py` reads
  the source, truncates it at the `__main__` guard, and `exec`s that — giving `set_config`
  and `simulate` from the unmodified source.

- **`Results_following/Analysis_following.xlsx` coverage.** The shipped calibration table
  does not span the parameter values used in the paper's main experiments; `find_parameters`
  silently clips out-of-range inputs. This is a data limitation, not a code bug, and is
  discussed in `notes/03_replication.md`.

## Requirements note

The repo pins `numpy==1.26.3`, `torch==2.2.0`, `pandas==2.2.0` etc. This environment runs
Python 3.14 with numpy 2.4.3, torch 2.13.0+cpu, pandas 3.0.5 and the code runs unmodified
apart from the patch above. `openpyxl` is additionally required to read the calibration
tables and is not listed in `requirements.txt`.
