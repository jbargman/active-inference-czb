---
name: split-site-collaboration
description: Protocol and tooling for research collaborations where the data cannot leave a partner (a company, a hospital, an agency) and the two sides share neither a git repository nor a drive, so code, documents and aggregate results move as reviewed bundles by e-mail while raw data, per-record derived data and ingestion scripts never move. Covers the two-layer repository layout, the data-interface contract with synthetic fixtures, the machine-readable transfer policy the bundle tool enforces at both sites, the steward review sheet and sign-off document, conflict detection without a shared history, and the brief for an LLM assistant at either site. Use when Jonas says data is held at a partner and cannot be moved (Volvo Cars, VCC, naturalistic data, hospital data, "we cannot move the data", "no common repo", "send files by e-mail"), when a data-handling agreement or sign-off document is needed, when a bundle must be made, checked or applied, or when setting a new project up to work this way.
---

# Split-site collaboration: code moves, data does not

**Status: active. Written 2026-09-03 for the Chalmers–Volvo Cars phase of the
WaymoActiveInference project; approved by Jonas pending VCC sign-off of that instance.**
The live copy is `~/.claude/skills/split-site-collaboration/`; a tracked mirror of this
file sits at `docs/skills/split-site-collaboration.SKILL.md` in the project repository,
under the same mirror rule as `performing-research` (update both in one commit when the
repository is at hand; otherwise the next session with the repository reconciles).

The skill ships the tooling and the templates:

```
scripts/bundle.py                 make / check / apply / scan / selftest
templates/transfer_policy.yaml    the rule set, with placeholders
templates/interface_schema.yaml   the data-interface contract, skeleton
templates/split_site_protocol.md  the sign-off document, with placeholders
templates/SITE_LLM_BRIEF.md       the brief for the assistant at either site
```

The worked instance is `transfer/` and `docs/split_site_protocol.md` in WaymoActiveInference.

## 1 The problem this solves

A partner holds data that may not leave; there is no shared repository; files move by
e-mail. Without a protocol, three things go wrong: something that should not leave does
(a path, a row, a notebook with outputs); the two code bases drift with no way to tell
what changed; and a quoted number cannot be traced to the code and the data build that
produced it. The protocol makes each of those a mechanical check rather than a judgment.

## 2 The protocol, in one page

**Sites and roles.** A *home site* owns the model, code and documents and holds no partner
data. A *data site* holds the data, adapts it to the interface, runs the shared code, and
exports aggregate results. A named *data steward* at the data site signs every outbound
bundle. Each site keeps its own git repository; the bundles are the shared timeline.

**Two layers.** The *shared layer* may cross: code, tests, documents, the transfer tooling,
synthetic fixtures, and (from the data site) `results/aggregate/`. The *site layer* never
crosses: raw and per-record derived data, ingestion and preprocessing scripts, data paths,
credentials, logs, notebooks. Convention: the site layer lives under `site/`; the policy
also refuses data-shaped patterns wherever they sit.

**One interface.** The shared code reads only files of the shape in
`transfer/interface_schema.yaml`: pseudonymous ids generated at the data site, kinematic
columns with units, no timestamps, no positions, no identifiers, no free text. The data site
writes an adapter in its site layer; the home site develops against a synthetic fixture of
the same shape, so everything runs end to end where there is no data. A validator checks an
interface directory without printing a row.

**The policy file** (`transfer/transfer_policy.yaml`) is the rule set: per role, `allow`
globs (a file must match one), `never` globs (a match refuses it regardless), size limits,
which extensions are scanned text and which binaries are permitted, `forbidden_patterns`
(regexes that refuse: share and drive paths, VINs, coordinate pairs, timestamps),
`warn_patterns` (flag for the steward), and the table rules for the data site: aggregate
paths, forbidden columns, count columns, `min_n`, row limit, per-person rows. It carries a
version and a sign-off block, travels inside every bundle, and its hash is in every manifest.

**Bundles.** `bundle.py make` lists what changed since a named earlier bundle (or
everything, `--all`, for the first shipment), keeps only allowed files, runs the content
checks, and writes a zip with `MANIFEST.json` (hashes, base hashes, policy hash, purpose,
in-reply-to) and `REVIEW.md` (one row per file with its check result, the warnings, the
steward's tick list and signature line). A violation means no bundle; a steward-approved
exception is recorded with `--override "<who approved what, when>"` and shown on the sheet.
`bundle.py check` re-verifies at either end. `bundle.py apply` checks, detects files edited
locally since the sender's base (three-way, by hash) and stops on conflict, writes the files,
records manifest and sheet, appends to `transfer/TRANSFER_LOG.md`, and commits with the
bundle id. `bundle.py scan` says what in the working tree would be refused. Each site's own
outbox, inbox, manifests and log are never re-bundled.

**Traceability.** Every exported result carries a run record (script, commit id at the data
site, parameters, date, validator report), never a data path. The chain from a quoted number
is: document, bundle id, manifest hash, run record, commit at the data site.

**Notes across sites** go in each site's own append-only notes file
(`docs/notes_from_<SITE>.md`), numbered and dated; neither site edits the other's, so notes
never conflict. Questions do not stop the work; the numbered-query habit of
`performing-research` applies.

## 3 Setting a project up (the instantiation steps)

1. Create `transfer/` in the project and copy in `scripts/bundle.py` as
   `transfer/bundle.py`, plus the four templates. Fill the placeholders (`{{PROJECT}}`,
   `{{HOME}}`, `{{HOME_NAME}}`, `{{DATA}}`, `{{DATA_NAME}}`, `{{DATE}}`); the policy's
   `allow`/`never` lists must be rewritten for the project's actual layout. Add
   `transfer/outbox/` and `transfer/inbox/` to `.gitignore`.
2. Write `interface_schema.yaml` from the project's data specification (what the analysis
   needs, nothing more), then a fixture generator and a validator for that shape. If a data
   request document exists, derive the schema from it and say so in the file.
3. Run `python transfer/bundle.py selftest`, then write `tests/test_<transfer>.py` in the
   project's check style: the selftest, the real policy parsing identically with and
   without PyYAML, the paths that must never leave classified `never` for both roles, the
   shared layer allowed for both, the fixture passing the validator.
4. Build `docs/split_site_protocol.md` from the template, then Word and PDF
   (`pandoc`, `docs/build_pdf.py`), with the partner's open decisions listed explicitly
   (`min_n`, per-person exceptions, figures, names, extra patterns, schema review,
   retention). It is a sign-off document: status DRAFT until both sides sign, and the
   policy's `policy_status` says the same.
5. Add a row to the project's handover and a line to its README pointing at `transfer/`,
   and record the open sign-off as a query for Jonas.
6. First shipment: `make --site <HOME> --to <DATA> --purpose "..." --all`; every later
   bundle names `--since` the last one exchanged.

## 4 Rules for the assistant at either site (the brief, in short)

Know which site you are at (`TRANSFER_SITE`). Never move anything from the site layer to the
shared layer; never put data content in chat, documents, commit messages or questions;
results leave only through scripts writing aggregates with run records; `scan` before every
`make`; apply with the tool, never by hand; commit after every make and apply with the
bundle id; when unsure whether something may leave, it may not. The full brief is
`templates/SITE_LLM_BRIEF.md`; copy it into the project and hand it to the partner's
assistant with the first bundle.

## 5 Design decisions worth knowing

- **Policy travels in the bundle.** The receiver checks with the sender's policy and warns
  if it differs from the local one; both sides must hold one version before applying.
- **No shared history, so conflicts are detected by hash.** The manifest carries the
  sender's base hash for every modified file; if the receiver's copy matches neither the
  base nor the new hash, the receiver edited it and apply stops. `--force` after a manual
  merge, said so in the log.
- **The steward sheet is generated, not written.** It lists exactly what the tool checked,
  so the signature covers a known object; the sheet is saved beside the zip and again at
  the receiver.
- **Text is scanned, binaries are gated.** Only listed binary types may cross (images,
  PDFs); everything else binary is refused, which is what keeps pickles, parquet and
  spreadsheets out even when a path rule would let them through.
- **Documents can embed data too.** At the data site, PDFs and Word files are refused;
  markdown is scanned for paths, timestamps and identifiers. Notebooks are refused at both
  sites because their outputs embed data.
- **PyYAML is optional.** The tool has a built-in reader for the policy's YAML subset (maps,
  lists, scalars, inline lists and maps, comments) so the partner's locked-down Python can
  run it; the selftest checks that the two readers agree.

## 6 Revision history

- 2026-09-03: written, with the WaymoActiveInference instance (`transfer/`,
  `docs/split_site_protocol.md`, `tests/test_transfer.py`) as the worked example.
