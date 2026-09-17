"""
The generative-model framework: the data-fitted parts of the other road user's model.

Designed 2026-09-17 (`docs/generative_model_framework.md`) at Jonas's request: a framework that is
PREPARED on the drone datasets (highD, inD) and RUN, unchanged, on Volvo Cars' naturalistic data
through the split-site interface (`transfer/interface_schema.yaml`), returning only aggregates.

The framework does not learn a trajectory predictor end to end. It estimates the few distributions a
STRUCTURED generative model needs, each from modest data:

    C1  hazard.py        lane-change INITIATION: P(start within dt | context)   (Julian Schumann's point)
    C2  lanechange.py    lane-change EXECUTION: onset, duration, lateral speed; the crossing norm's bounds
    C3  uncertainty.py   how constant-velocity prediction error grows with the horizon (the fan's width)
    C4  population.py    the ego's own normal: following states, accepted clearances (reference B)
        aggregate.py     the export rule of the transfer policy, enforced in code (min_n, no identifiers)
        fit_from_interface.py   the runner: an interface directory in, aggregate tables and a report out

Every function reads arrays or interface events and writes nothing but what it returns; the runner is
the only writer, and it writes aggregates only. The property tests are `tests/test_generative.py`.
"""
