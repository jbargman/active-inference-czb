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
python transfer/bundle.py check transfer/inbox/CTH-2026-09-04-001.zip
python transfer/bundle.py apply transfer/inbox/CTH-2026-09-04-001.zip --commit
python transfer/bundle.py make --site VCC --to CTH --purpose "held-out scores on the rear-end events"
```

Only the first bundle needs `--all`. After that, `make` carries only what the peer does not
already have, decided by SHA-256, not by git — see below.

Before any bundle leaves VCC: `python transfer/bundle.py scan --site VCC`, then the steward
completes the review sheet the tool writes beside the zip. Tests: `python tests/test_transfer.py`.

## Only changed files move, and how that is decided

Git cannot answer "what does the other site already have?", because there is no shared
history: each site's commits describe only itself. So the tool tracks it by content hash.

Every manifest records the SHA-256 of each file it carried *and* of the sender's whole
exportable shared layer. `make` replays the manifests of all bundles exchanged with that peer
— sent and received alike, since both leave the two sites holding the same content — to derive
what the peer holds, and bundles only files whose hash differs, plus files genuinely deleted
from disk here. The review sheet states how many files were unchanged and therefore not
re-sent. `python transfer/bundle.py peers --site CTH` shows the current picture and what a
bundle would carry right now.

Three consequences worth knowing:

- **A bundle that is made but never released must be revoked**, or the next bundle will assume
  the peer received it: `python transfer/bundle.py revoke <bundle-id> --reason "steward
  rejected it"`. The tool prints this reminder after every `make`.
- **`apply` runs a drift check.** The manifest carries the sender's full tree, so the receiver
  can list files the sender holds that are missing or different here. A file that should have
  arrived but never did shows up instead of staying silent. `bundle.py drift <zip>` re-runs it.
- **`--since <bundle-id>` pins the baseline to one bundle's tree** and `--all` ignores the
  baseline entirely. Use them for recovery; the default is right for normal work. Do not use
  `--since` as a habit: a bundle's tree is what its *sender* could export under its own role,
  so files only the other role may export would be re-sent every round trip and would look
  deleted coming back.
