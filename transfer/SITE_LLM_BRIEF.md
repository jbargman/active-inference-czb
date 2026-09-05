# Brief for the LLM assistant at either site

*Read this before doing anything in this repository at a site that is not your own, and
before every export. It applies to Claude at Chalmers and to whichever assistant Volvo Cars
uses. The full protocol is `docs/split_site_protocol.md`; the rules the tool enforces are
`transfer/transfer_policy.yaml`. When this brief and the policy file disagree, the policy
file wins.*

## Which site you are at

Ask, or read the environment: `TRANSFER_SITE` is `CTH` (home site, Chalmers: owns the model
and the methods, holds no Volvo data) or `VCC` (data site, Volvo Cars: holds the naturalistic
data, runs the shared code, exports aggregate results after a steward's review). If you cannot
tell, stop and ask; nothing else in this brief can be applied without knowing.

## The two layers

- **Shared layer**: `src/`, `tests/`, `transfer/`, `docs/*.md`, `replication/**/*.py` and
  `*.md`, and at the data site `results/aggregate/`. It may cross sites, in bundles, after
  the checks. The shared code reads data only in the shape of `transfer/interface_schema.yaml`.
- **Site layer**: everything under `site/` and anything matching the policy's `never`
  patterns: raw data, per-event or per-trip derived data, ingestion and preprocessing code,
  data paths, credentials, logs, notebooks. It never crosses, and the tool refuses it. At
  the data site this is where the adapter lives that turns Volvo's data into the interface.

## Eleven rules

1. **Never copy from the site layer into the shared layer.** Not a path, not a row, not a
   screenshot, not a column of real values pasted as an example. If shared code needs an
   example, use `transfer/fixtures/synthetic/`.
2. **Never put data content in chat, in a document, in a commit message or in a query.**
   Describe data by its shape and its counts ("312 rear-end events from 41 drivers"), never
   by its rows. Wall-clock timestamps, positions and identifiers are content.
3. **Results leave only through scripts that write into `results/aggregate/`**, and only
   as aggregates: at least `min_n` drivers and `min_n` events behind every row, no per-event
   rows, no per-driver rows unless the steward has recorded an exception. Figures follow the
   same rule.
4. **Every result carries its run record**: script name, commit id, parameter values, date,
   the interface directory's validator report, never the data path. A number without a run
   record is not quoted anywhere.
5. **Run `python transfer/bundle.py scan --site <SITE>` before making a bundle** and fix
   what it refuses. Do not weaken a rule to get a file through; ask the steward for a
   recorded exception (`--override "<who approved what, when>"`) if the export is right.
6. **Bundle small and often**, each with a purpose line that says what changed and why. Do
   not reformat, rename or reorder shared files you are not changing; it creates conflicts
   for the other site.
7. **Notes to the other site go in your own site's notes file** (`docs/notes_from_CTH.md`
   or `docs/notes_from_VCC.md`), append-only, dated, numbered. Never edit the other site's
   file. Questions that need the other site's answer are numbered there; do not stop the
   work while waiting, do what does not depend on the answer.
8. **Apply received bundles with the tool, never by copying files by hand**, so that the
   manifest, the review sheet and the log are recorded and conflicts are detected. On a
   conflict, merge by hand and re-apply with `--force`; say so in the log.
9. **Commit at your own site after every make and every apply**, with the bundle id in the
   commit message. Each site keeps its own git history; the bundle ids are the shared
   timeline.
10. **When unsure whether something may leave, it may not.** Write it into the site layer,
    record the question in your notes file, and continue.
11. **If a bundle you made is not actually sent** — the steward rejects it, or it is
    superseded before it goes — run `python transfer/bundle.py revoke <bundle-id> --reason
    "..."`. Making a bundle records that the other site now holds those files, so an
    unrevoked dead bundle makes the next one skip them. The tool prints this reminder after
    every `make`; do not ignore it.

## What you may expect from the other site

- The home site sends model code, analysis scripts, tests, documents and synthetic fixtures,
  all runnable against the interface with no data present.
- The data site sends aggregate results with run records, code fixes that the data forced,
  and notes; each bundle reviewed and signed by the steward before it is sent.
- Both sites keep `transfer/TRANSFER_LOG.md`; if the logs disagree about a bundle, the
  manifests inside the bundles settle it.

## Before you export, in order

```bash
python transfer/validate_interface.py <interface dir>        # data site only, once per dataset build
python tests/test_transfer.py                                # the tooling is intact
python transfer/bundle.py scan --site <SITE>                 # nothing in the shared layer would be refused
python transfer/bundle.py peers --site <SITE>                 # what the other site already has
python transfer/bundle.py make --site <SITE> --to <OTHER> --purpose "..."
```

Then the review sheet in `transfer/outbox/<id>.REVIEW.md` is completed and signed (data
site: by the steward; home site: by the sender), and the zip goes by e-mail with the sheet.

Only the very first bundle takes `--all`. After that `make` works out by content hash what
the other site does not yet have and carries only that; you do not name a baseline.
