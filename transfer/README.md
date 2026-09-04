# transfer/ — working with Volvo Cars without moving data

This folder holds everything the split-site protocol needs at either site. The protocol
itself is explained in `docs/split_site_protocol.md` (PDF beside it, for sign-off); the
rules the tooling enforces are `transfer_policy.yaml`; the generic method is the
`split-site-collaboration` skill (mirrored in `docs/skills/`).

| file | what it is |
|---|---|
| `transfer_policy.yaml` | the machine-readable rule set: sites, roles, what may cross, content checks, aggregation rule; travels inside every bundle |
| `bundle.py` | makes, checks and applies bundles; `python transfer/bundle.py -h` |
| `interface_schema.yaml` | the only data shape the shared code reads; VCC's adapter produces it, CTH's fixture imitates it |
| `validate_interface.py` | checks a directory of interface files against the schema, without printing data |
| `make_synthetic_fixture.py` | writes `fixtures/synthetic/`, twelve made-up events, so the pipeline runs where there is no data |
| `SITE_LLM_BRIEF.md` | the brief for whichever LLM assistant works at either site; read it before touching the repository there |
| `TRANSFER_LOG.md`, `manifests/` | this site's own record of every bundle sent and received (created by the tool; never bundled) |
| `outbox/`, `inbox/` | bundles made here and bundles received here (gitignored; never bundled) |

Round trip in four commands:

```bash
python transfer/bundle.py make --site CTH --to VCC --purpose "first shipment of the shared layer" --all
python transfer/bundle.py check transfer/inbox/CTH-2026-09-03-001.zip
python transfer/bundle.py apply transfer/inbox/CTH-2026-09-03-001.zip --commit
python transfer/bundle.py make --site VCC --to CTH --purpose "held-out scores on the rear-end events" --since CTH-2026-09-03-001
```

Before any bundle leaves VCC: `python transfer/bundle.py scan --site VCC`, then the steward
completes the review sheet the tool writes beside the zip. Tests: `python tests/test_transfer.py`.
