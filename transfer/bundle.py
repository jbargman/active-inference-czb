#!/usr/bin/env python
"""
bundle.py -- move code, documents and aggregate results between two sites that share
neither a repository nor data, as reviewable bundles governed by a policy file.

The protocol is described in the split-site collaboration skill and in the project's
`docs/split_site_protocol.md`. In one paragraph: each site keeps its own git repository.
The "shared layer" (model code, analysis scripts, documents, synthetic fixtures, aggregate
results) may cross sites; the "site layer" (raw data, per-trip derived data, ingestion and
preprocessing scripts, paths, credentials) never does. A bundle is a zip of changed
shared-layer files plus a manifest with hashes and a review sheet. The policy file
(`transfer/transfer_policy.yaml`) says, per site role, which paths may be bundled, which
never may, and what content checks apply. This script enforces it on both sides.

Commands (run from the repository root):

    python transfer/bundle.py make  --site CTH --to VCC --purpose "..." --all
    python transfer/bundle.py make  --site VCC --to CTH --purpose "..." --since CTH-2026-09-03-001
    python transfer/bundle.py check transfer/inbox/VCC-2026-09-10-001.zip
    python transfer/bundle.py apply transfer/inbox/VCC-2026-09-10-001.zip [--commit] [--apply-deletions]
    python transfer/bundle.py scan  --site VCC        # what in the working tree would be blocked
    python transfer/bundle.py selftest

Exit codes: 0 ok, 1 usage or I/O error, 2 policy violation (bundle refused), 3 conflict on
apply (local edits would be overwritten; re-run with --force after merging by hand).

Requires Python 3.9+. Uses PyYAML if installed; otherwise a built-in reader handles the
policy file's subset of YAML (maps, lists, scalars, inline lists, comments).
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

PROTOCOL_VERSION = 1
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".ipynb_checkpoints",
             ".pytest_cache", ".mypy_cache", ".ruff_cache", ".idea", ".vscode"}


# ----------------------------------------------------------------------------- YAML

def load_yaml(path):
    text = Path(path).read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except ImportError:
        return mini_yaml(text)


def _scalar(s: str):
    s = s.strip()
    if s == "":
        return None
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    low = s.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~"):
        return None
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        return [] if not inner else [_scalar(x) for x in _split_top(inner)]
    if s.startswith("{") and s.endswith("}"):
        inner = s[1:-1].strip()
        out = {}
        for part in ([] if not inner else _split_top(inner)):
            k, _, v = part.partition(":")
            out[k.strip()] = _scalar(v)
        return out
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def _split_top(s: str):
    """Split on commas that are not inside brackets or quotes."""
    parts, depth, quote, cur = [], 0, None, []
    for ch in s:
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            cur.append(ch)
        elif ch in "[{":
            depth += 1
            cur.append(ch)
        elif ch in "]}":
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return parts


def _strip_comment(line: str) -> str:
    out, quote = [], None
    for i, ch in enumerate(line):
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def mini_yaml(text: str):
    """A reader for the subset of YAML the policy files use. Not a general YAML parser."""
    lines = []
    for raw in text.splitlines():
        line = _strip_comment(raw)
        if not line.strip():
            continue
        lines.append((len(line) - len(line.lstrip(" ")), line.strip()))
    if not lines:
        return {}

    def split_kv(s):
        # first ": " or trailing ":" outside quotes
        quote = None
        for i, ch in enumerate(s):
            if quote:
                if ch == quote:
                    quote = None
            elif ch in "\"'":
                quote = ch
            elif ch == ":" and (i == len(s) - 1 or s[i + 1] == " "):
                return s[:i].strip(), s[i + 1:].strip()
        return None, None

    def block(i, indent):
        if lines[i][1].startswith("- "):
            out = []
            while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("- "):
                item = lines[i][1][2:].strip()
                k, v = split_kv(item)
                if k is not None and not item.startswith(("[", "'", '"')):
                    d = {}
                    if v == "" and i + 1 < len(lines) and lines[i + 1][0] > indent + 2:
                        child, i = block(i + 1, lines[i + 1][0])
                        d[k] = child
                    else:
                        d[k] = _scalar(v)
                        i += 1
                    while i < len(lines) and lines[i][0] == indent + 2 and not lines[i][1].startswith("- "):
                        k2, v2 = split_kv(lines[i][1])
                        if v2 == "" and i + 1 < len(lines) and lines[i + 1][0] > indent + 2:
                            child, i = block(i + 1, lines[i + 1][0])
                            d[k2] = child
                        else:
                            d[k2] = _scalar(v2)
                            i += 1
                    out.append(d)
                else:
                    out.append(_scalar(item))
                    i += 1
            return out, i
        out = {}
        while i < len(lines) and lines[i][0] == indent:
            k, v = split_kv(lines[i][1])
            if k is None:
                raise ValueError(f"mini-YAML: cannot read line: {lines[i][1]!r}")
            if v == "":
                if i + 1 < len(lines) and lines[i + 1][0] > indent:
                    child, i = block(i + 1, lines[i + 1][0])
                    out[k] = child
                else:
                    out[k] = None
                    i += 1
            else:
                out[k] = _scalar(v)
                i += 1
        return out, i

    obj, nxt = block(0, lines[0][0])
    if nxt < len(lines):
        raise ValueError(f"mini-YAML: could not parse from line: {lines[nxt][1]!r}")
    return obj


# ----------------------------------------------------------------------------- globs

_glob_cache: dict = {}


def glob_regex(pat: str):
    if pat in _glob_cache:
        return _glob_cache[pat]
    i, out = 0, ""
    while i < len(pat):
        if pat.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pat.startswith("**", i):
            out += ".*"
            i += 2
        elif pat[i] == "*":
            out += "[^/]*"
            i += 1
        elif pat[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(pat[i])
            i += 1
    rx = re.compile("^" + out + "$")
    _glob_cache[pat] = rx
    return rx


def matches(path: str, patterns) -> bool:
    """A pattern without '/' matches the basename; one with '/' matches the whole posix path."""
    if not patterns:
        return False
    base = path.rsplit("/", 1)[-1]
    for p in patterns:
        p = str(p)
        target = path if "/" in p else base
        if glob_regex(p).match(target):
            return True
    return False


# ----------------------------------------------------------------------------- policy

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Policy:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.raw = load_yaml(self.path)
        self.sha = sha256(self.path.read_bytes())
        if int(self.raw.get("protocol_version", 0)) != PROTOCOL_VERSION:
            raise SystemExit(f"policy protocol_version {self.raw.get('protocol_version')} "
                             f"!= tool version {PROTOCOL_VERSION}")
        self.sites = self.raw.get("sites", {}) or {}
        self.transfer = self.raw.get("transfer", {}) or {}
        self.roles = self.raw.get("roles", {}) or {}

    def role_of(self, site: str) -> str:
        if site not in self.sites:
            raise SystemExit(f"site {site!r} is not in the policy's sites: {list(self.sites)}")
        return self.sites[site].get("role", "home")

    def rules(self, site: str) -> dict:
        role = self.role_of(site)
        if role not in self.roles:
            raise SystemExit(f"policy has no rules for role {role!r}")
        return self.roles[role]

    def classify(self, relpath: str, site: str) -> str:
        """'never' | 'allowed' | 'unlisted'"""
        r = self.rules(site)
        if matches(relpath, r.get("never") or []):
            return "never"
        if matches(relpath, r.get("allow") or []):
            return "allowed"
        return "unlisted"

    def check_content(self, relpath: str, data: bytes, site: str):
        """Returns (violations, warnings): lists of strings."""
        r = self.rules(site)
        t = self.transfer
        viol, warn = [], []
        max_bytes = int(t.get("max_file_bytes", 2_000_000))
        if len(data) > max_bytes:
            viol.append(f"size {len(data)} B exceeds max_file_bytes {max_bytes}")
        base = relpath.rsplit("/", 1)[-1]
        ext = os.path.splitext(base)[1].lower()
        if not ext and base.startswith("."):
            ext = base.lower()          # dotfiles such as .gitignore: the name is the extension
        text_ext = [str(e).lower() for e in (t.get("text_extensions") or [])]
        bin_ext = [str(e).lower() for e in (t.get("binary_extensions_allowed") or [])]
        is_text = ext in text_ext
        if is_text:
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                viol.append("text extension but not UTF-8 text")
                return viol, warn
            for name, rx in (r.get("forbidden_patterns") or {}).items():
                m = re.search(str(rx), text)
                if m:
                    viol.append(f"forbidden pattern '{name}' matched: {m.group(0)[:40]!r}")
            for name, rx in (r.get("warn_patterns") or {}).items():
                m = re.search(str(rx), text)
                if m:
                    warn.append(f"pattern '{name}' matched: {m.group(0)[:40]!r} (steward to confirm)")
            if ext == ".csv":
                self._check_table(relpath, text, r, viol, warn)
        elif ext in bin_ext:
            warn.append("binary file: content cannot be scanned; steward to confirm it carries no data")
        else:
            viol.append(f"extension {ext or '(none)'} is neither a text nor an allowed binary type")
        return viol, warn

    def _check_table(self, relpath, text, r, viol, warn):
        if not matches(relpath, r.get("aggregate_tables") or []):
            viol.append("CSV outside the aggregate_tables paths")
            return
        rows = list(csv.reader(io.StringIO(text)))
        if not rows:
            warn.append("empty CSV")
            return
        header = [h.strip() for h in rows[0]]
        body = rows[1:]
        forbidden = [str(c).lower() for c in (r.get("forbidden_columns") or [])]
        bad = [h for h in header if h.lower() in forbidden]
        if bad:
            viol.append(f"forbidden column(s): {bad}")
        max_rows = int(r.get("max_rows", 10_000))
        if len(body) > max_rows:
            viol.append(f"{len(body)} rows exceed max_rows {max_rows}")
        count_cols = [str(c) for c in (r.get("count_columns") or [])]
        idx = [i for i, h in enumerate(header) if h in count_cols]
        min_n = int(r.get("min_n", 1))
        if idx:
            for i in idx:
                for rnum, row in enumerate(body, start=2):
                    if i >= len(row):
                        continue
                    try:
                        n = float(row[i])
                    except ValueError:
                        warn.append(f"count column {header[i]!r} non-numeric at row {rnum}")
                        break
                    if n < min_n:
                        viol.append(f"count column {header[i]!r} = {row[i]} < min_n {min_n} at row {rnum}")
                        break
        else:
            warn.append("no count column found: steward must confirm every row is an aggregate "
                        f"over at least min_n = {min_n} units")
        if not r.get("per_person_rows_allowed", False):
            person_cols = [str(c).lower() for c in (r.get("person_columns") or [])]
            hit = [h for h in header if h.lower() in person_cols]
            if hit:
                viol.append(f"per-person column(s) {hit}: per-person rows are not allowed "
                            "without a recorded steward exception (--override)")


# ----------------------------------------------------------------------------- tree

def repo_root_from(policy_path: Path) -> Path:
    return policy_path.resolve().parent.parent


def walk_tree(root: Path, policy: Policy, site: str):
    """Yield (relpath, absolute path) for every allowed file; count the others."""
    allowed, never, unlisted = [], 0, 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            ap = Path(dirpath) / fn
            rel = ap.relative_to(root).as_posix()
            if rel.startswith(("transfer/outbox/", "transfer/inbox/", "transfer/manifests/")) \
                    or rel in ("transfer/TRANSFER_LOG.md", "transfer/revoked.json"):
                continue  # each site's own bundles, manifests, log and revocations are its
                          # own records of the exchange, never re-bundled
            c = policy.classify(rel, site)
            if c == "allowed":
                allowed.append((rel, ap))
            elif c == "never":
                never += 1
            else:
                unlisted += 1
    allowed.sort()
    return allowed, never, unlisted


def file_kind(rel: str, policy: Policy) -> str:
    ext = os.path.splitext(rel)[1].lower()
    if rel.startswith("transfer/"):
        return "protocol"
    if ext in (".py", ".ps1", ".sh", ".bat", ".cmd", ".r", ".jl", ".m"):
        return "code"
    if ext in (".md", ".docx", ".pdf", ".tex", ".bib", ".txt"):
        return "doc"
    if ext in (".png", ".svg", ".jpg", ".gif", ".pptx", ".mp4"):
        return "figure"
    if ext in (".csv", ".json"):
        return "result"
    return "other"


def manifests_dir(root: Path) -> Path:
    d = root / "transfer" / "manifests"
    d.mkdir(parents=True, exist_ok=True)
    return d


# --- what the peer already holds ----------------------------------------------------
#
# There is no shared history, so "what does the other site already have?" cannot be asked
# of git. It is DERIVED by replaying this site's manifests: every bundle we sent and every
# bundle we received leaves both sites holding the same content for the files it carried.
# Deriving it (rather than keeping a mutable state file) means the manifests remain the
# single record, and a bundle that was made but never released can simply be revoked.

BUNDLE_ID_RX = re.compile(r"^(?P<site>[A-Za-z0-9_]+)-(?P<date>\d{4}-\d{2}-\d{2})-(?P<seq>\d+)$")


def _bundle_sort_key(man: dict):
    m = BUNDLE_ID_RX.match(man.get("bundle_id", ""))
    if m:
        return (m.group("date"), int(m.group("seq")), m.group("site"))
    return (man.get("created", ""), 0, "")


def revoked_ids(root: Path) -> set:
    p = root / "transfer" / "revoked.json"
    if not p.exists():
        return set()
    try:
        return {e["bundle_id"] for e in json.loads(p.read_text(encoding="utf-8"))}
    except Exception:
        return set()


def load_manifests(root: Path, include_revoked=False):
    out, skip = [], revoked_ids(root)
    for p in sorted(manifests_dir(root).glob("*.json")):
        try:
            man = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not include_revoked and man.get("bundle_id") in skip:
            continue
        out.append(man)
    out.sort(key=_bundle_sort_key)
    return out


def peer_state(root: Path, site: str, peer: str):
    """path -> sha256 of the content we believe `peer` holds. Also returns the bundles used."""
    state, used = {}, []
    for man in load_manifests(root):
        pair = {man.get("from_site"), man.get("to_site")}
        if pair != {site, peer}:
            continue
        for f in man.get("files", []):
            state[f["path"]] = f["sha256"]
        for d in man.get("deleted", []):
            state.pop(d, None)
        used.append(man["bundle_id"])
    return state, used


def next_bundle_id(root: Path, site: str, date: str) -> str:
    prefix = f"{site}-{date}-"
    seq = 0
    for p in manifests_dir(root).glob(prefix + "*.json"):
        try:
            seq = max(seq, int(p.stem[len(prefix):]))
        except ValueError:
            pass
    for p in (root / "transfer" / "outbox").glob(prefix + "*.zip") if (root / "transfer" / "outbox").exists() else []:
        try:
            seq = max(seq, int(p.stem[len(prefix):]))
        except ValueError:
            pass
    return f"{prefix}{seq + 1:03d}"


def git_head(root: Path):
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root,
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None
    except Exception:
        return None


def append_log(root: Path, line: str):
    log = root / "transfer" / "TRANSFER_LOG.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    if not log.exists():
        log.write_text("# Transfer log\n\nOne line per bundle sent or received; the manifests in "
                       "`transfer/manifests/` carry the detail.\n\n| date | direction | bundle | "
                       "files | purpose | local commit |\n|---|---|---|---|---|---|\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# ----------------------------------------------------------------------------- review sheet

def review_sheet(man: dict, policy: Policy) -> str:
    L = []
    L.append(f"# Review sheet for bundle {man['bundle_id']}")
    L.append("")
    L.append(f"- From **{man['from_site']}** ({policy.sites.get(man['from_site'], {}).get('name', '')}) "
             f"to **{man['to_site']}** ({policy.sites.get(man['to_site'], {}).get('name', '')})")
    L.append(f"- Created {man['created']}; sender role **{man['from_role']}**; "
             f"local commit `{man.get('local_commit') or 'n/a'}`")
    L.append(f"- Purpose: {man['purpose']}")
    L.append(f"- In reply to: {man.get('in_reply_to') or 'none'}; changes relative to: {man['base']['description']}")
    L.append(f"- Policy: `{man['policy_path']}` version {man['policy_version']}, sha256 {man['policy_sha256'][:12]}")
    L.append(f"- Files: {len(man['files'])} included, {len(man.get('deleted', []))} deletions listed; "
             f"{man['excluded']['never']} paths refused by 'never' rules and {man['excluded']['unlisted']} "
             f"not on the allow list were not even considered")
    L.append(f"- Unchanged since the peer last had them, so not re-sent: "
             f"{man.get('unchanged_count', 0)} file(s)")
    L.append("")
    L.append("| path | status | kind | bytes | sha256 | checks |")
    L.append("|---|---|---|---|---|---|")
    for f in man["files"]:
        checks = "ok"
        if f.get("violations"):
            checks = "VIOLATION: " + "; ".join(f["violations"])
        elif f.get("warnings"):
            checks = "warn: " + "; ".join(f["warnings"])
        L.append(f"| `{f['path']}` | {f['status']} | {f['kind']} | {f['bytes']} | {f['sha256'][:12]} | {checks} |")
    for d in man.get("deleted", []):
        L.append(f"| `{d}` | deleted | - | - | - | applied only with --apply-deletions |")
    L.append("")
    if man.get("override"):
        L.append(f"**Override recorded by the sender:** {man['override']}")
        L.append("")
    L.append("## Steward review (required for every bundle leaving the data site)")
    L.append("")
    L.append("- [ ] No raw data, no per-trip or per-driver rows, no ingestion or preprocessing code, "
             "no site paths or credentials, no screenshots or excerpts of data")
    L.append("- [ ] Every table is an aggregate over at least the policy's minimum count, or carries a "
             "recorded exception")
    L.append("- [ ] Every figure shows aggregates only")
    L.append("- [ ] Every warning above has been looked at")
    L.append("")
    L.append("Reviewed by: ______________________   Date: ____________   Decision: approved / rejected")
    L.append("")
    L.append("Notes:")
    L.append("")
    return "\n".join(L)


# ----------------------------------------------------------------------------- make

def cmd_make(a):
    policy = Policy(a.policy)
    root = Path(a.root).resolve() if a.root else repo_root_from(Path(a.policy))
    site = a.site
    to = a.to
    if to not in policy.sites:
        raise SystemExit(f"--to {to!r} is not a site in the policy")
    role = policy.role_of(site)
    allowed, n_never, n_unlisted = walk_tree(root, policy, site)
    tree = {}
    for rel, ap in allowed:
        tree[rel] = sha256(ap.read_bytes())

    # The baseline is what we believe the peer already holds. By default that is derived from
    # every bundle exchanged with this peer (see peer_state); --since pins it to one bundle's
    # tree, and --all ignores it. Never use one bundle's tree as the default: a tree is what
    # its SENDER could export under its own role, so files only the other role may export
    # would be re-sent every round trip and would look deleted coming back.
    if a.all:
        base_tree, base_desc = {}, "everything (--all)"
    elif a.since:
        mp = manifests_dir(root) / f"{a.since}.json"
        if not mp.exists():
            raise SystemExit(f"no manifest {mp}; --since must name a bundle sent or received here")
        base_tree = json.loads(mp.read_text(encoding="utf-8")).get("tree") or {}
        base_desc = f"the tree of bundle {a.since} (--since)"
    else:
        base_tree, used = peer_state(root, site, to)
        if not used:
            raise SystemExit(f"no bundles exchanged with {to} yet, so there is no baseline: "
                             f"use --all for the first bundle (or --since <id>)")
        base_desc = (f"what {to} already holds, from {len(used)} bundle(s) "
                     f"{used[0]}..{used[-1]}" if len(used) > 1 else f"what {to} already holds, from {used[0]}")

    changed = [rel for rel in tree if tree[rel] != base_tree.get(rel)]
    # A file counts as deleted only if it is genuinely gone from disk here. A file that
    # merely cannot be exported under this site's role is not a deletion.
    deleted = [rel for rel in base_tree if rel not in tree and not (root / rel).exists()]
    if a.only:
        wanted = set(a.only)
        changed = [r for r in changed if r in wanted or any(r.startswith(w.rstrip("/") + "/") for w in wanted)]
    if not changed and not deleted:
        print("nothing changed relative to", base_desc)
        return 0

    files, n_viol = [], 0
    for rel in changed:
        data = (root / rel).read_bytes()
        viol, warn = policy.check_content(rel, data, site)
        n_viol += len(viol)
        files.append({
            "path": rel, "status": "modified" if rel in base_tree else "added",
            "kind": file_kind(rel, policy), "bytes": len(data), "sha256": tree[rel],
            "base_sha256": base_tree.get(rel), "violations": viol, "warnings": warn,
        })

    date = dt.date.today().isoformat()
    bundle_id = a.bundle_id or next_bundle_id(root, site, date)
    man = {
        "bundle_id": bundle_id, "protocol_version": PROTOCOL_VERSION,
        "project": policy.raw.get("project"), "from_site": site, "from_role": role, "to_site": to,
        "created": dt.datetime.now().isoformat(timespec="seconds"), "purpose": a.purpose,
        "in_reply_to": a.in_reply_to, "base": {"description": base_desc, "bundle_id": a.since},
        "local_commit": git_head(root), "policy_path": Path(a.policy).as_posix() if not Path(a.policy).is_absolute() else Path(a.policy).relative_to(root).as_posix(),
        "policy_version": policy.raw.get("policy_version"), "policy_sha256": policy.sha,
        "excluded": {"never": n_never, "unlisted": n_unlisted},
        "unchanged_count": len(tree) - len(changed),
        "files": files, "deleted": deleted, "override": a.override,
        "review": {"steward": None, "decision": None, "date": None, "notes": None},
        "tree": tree,
    }
    sheet = review_sheet(man, policy)

    if n_viol and not a.override:
        print(sheet)
        print(f"\nREFUSED: {n_viol} policy violation(s). Fix the files, or record a steward-approved "
              f"exception with --override \"<who approved what, and why>\".", file=sys.stderr)
        return 2
    total = sum(f["bytes"] for f in files)
    max_bundle = int(policy.transfer.get("max_bundle_bytes", 25_000_000))

    outbox = root / "transfer" / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    zpath = outbox / f"{bundle_id}.zip"
    man_public = dict(man)  # the manifest inside the bundle carries the tree too: the receiver needs it
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{bundle_id}/MANIFEST.json", json.dumps(man_public, indent=1))
        z.writestr(f"{bundle_id}/REVIEW.md", sheet)
        for f in files:
            z.write(root / f["path"], f"{bundle_id}/files/{f['path']}")
    zsize = zpath.stat().st_size
    if zsize > max_bundle:
        zpath.unlink()
        print(f"REFUSED: the zip would be {zsize} B, over max_bundle_bytes {max_bundle} (the e-mail ceiling); "
              f"split it with --only <paths>, or tighten the policy's allow list", file=sys.stderr)
        return 2
    (manifests_dir(root) / f"{bundle_id}.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    (outbox / f"{bundle_id}.REVIEW.md").write_text(sheet, encoding="utf-8")
    append_log(root, f"| {date} | sent to {to} | {bundle_id} | {len(files)} (+{len(deleted)} del) | "
                     f"{a.purpose} | {man['local_commit'] or ''} |")
    print(sheet)
    print(f"\nwrote {zpath}  ({zsize} B zipped, {total} B in {len(files)} files, "
          f"{man['unchanged_count']} unchanged file(s) not re-sent); review sheet beside it; "
          f"manifest saved to transfer/manifests/{bundle_id}.json")
    if role == "data":
        print("This bundle leaves the DATA site: the steward must complete the review sheet before it is sent.")
    print(f"If this bundle is NOT released (the steward rejects it, or it is never e-mailed), run\n"
          f"    python transfer/bundle.py revoke {bundle_id} --reason \"...\"\n"
          f"so the next bundle does not assume {to} received these files.")
    return 0


# ----------------------------------------------------------------------------- check / apply

def read_bundle(zpath: Path):
    z = zipfile.ZipFile(zpath)
    names = z.namelist()
    tops = {n.split("/", 1)[0] for n in names}
    if len(tops) != 1:
        raise SystemExit(f"bundle must contain exactly one top-level folder; found {tops}")
    top = tops.pop()
    man = json.loads(z.read(f"{top}/MANIFEST.json").decode("utf-8"))
    if man["bundle_id"] != top:
        raise SystemExit("bundle folder name and manifest bundle_id differ")
    return z, top, man


def bundle_policy(z, top, man, local_policy_path):
    """Prefer the policy inside the bundle; fall back to the local one; warn if they differ."""
    inner = f"{top}/files/{man['policy_path']}"
    notes = []
    if inner in z.namelist():
        tmp = Path(tempfile.mkdtemp()) / "transfer" / "transfer_policy.yaml"
        tmp.parent.mkdir(parents=True)
        tmp.write_bytes(z.read(inner))
        pol = Policy(tmp)
        if local_policy_path and Path(local_policy_path).exists():
            if Policy(Path(local_policy_path)).sha != pol.sha:
                notes.append("the policy inside the bundle differs from the local policy; "
                             "both sides must agree on one policy version before applying")
    else:
        if not local_policy_path or not Path(local_policy_path).exists():
            raise SystemExit("no policy inside the bundle and no local policy found")
        pol = Policy(Path(local_policy_path))
    if pol.sha != man["policy_sha256"]:
        notes.append("the manifest's policy sha256 differs from the policy being used to check")
    return pol, notes


def cmd_check(a, quiet=False):
    zpath = Path(a.bundle)
    z, top, man = read_bundle(zpath)
    pol, notes = bundle_policy(z, top, man, a.policy)
    site = man["from_site"]
    problems = []
    for f in man["files"]:
        inner = f"{top}/files/{f['path']}"
        if inner not in z.namelist():
            problems.append(f"{f['path']}: listed but missing from the bundle")
            continue
        data = z.read(inner)
        if sha256(data) != f["sha256"]:
            problems.append(f"{f['path']}: sha256 does not match the manifest")
        c = pol.classify(f["path"], site)
        if c != "allowed":
            problems.append(f"{f['path']}: path is '{c}' under the {pol.role_of(site)} rules")
        viol, warn = pol.check_content(f["path"], data, site)
        f["violations"], f["warnings"] = viol, warn
        for v in viol:
            problems.append(f"{f['path']}: {v}")
    extra = [n for n in z.namelist() if n.startswith(f"{top}/files/")
             and n[len(top) + 7:] not in {f["path"] for f in man["files"]}]
    for n in extra:
        problems.append(f"{n}: present in the bundle but not in the manifest")
    if not quiet:
        print(review_sheet(man, pol))
        for n in notes:
            print("NOTE:", n)
    if problems and man.get("override"):
        if not quiet:
            print(f"\n{len(problems)} problem(s), covered by the sender's recorded override: {man['override']}")
            for p in problems:
                print("  -", p)
        return 0, man, pol, z, top, problems
    if problems:
        if not quiet:
            print(f"\nREFUSED: {len(problems)} problem(s):", file=sys.stderr)
            for p in problems:
                print("  -", p, file=sys.stderr)
        return 2, man, pol, z, top, problems
    if not quiet:
        print("\nOK: hashes verified, every file allowed under the sender's role, no content violations.")
    return 0, man, pol, z, top, problems


def cmd_apply(a):
    code, man, pol, z, top, problems = cmd_check(a, quiet=a.quiet)
    if code and not a.force:
        return code
    root = Path(a.root).resolve() if a.root else Path.cwd()
    conflicts, plan = [], []
    for f in man["files"]:
        target = root / f["path"]
        if target.exists():
            local = sha256(target.read_bytes())
            if local == f["sha256"]:
                plan.append((f["path"], "identical"))
                continue
            if f.get("base_sha256") and local != f["base_sha256"]:
                conflicts.append(f["path"])
                plan.append((f["path"], "CONFLICT"))
                continue
            plan.append((f["path"], "update"))
        else:
            plan.append((f["path"], "create"))
    for d in man.get("deleted", []):
        plan.append((d, "delete" if a.apply_deletions else "delete (skipped; --apply-deletions)"))
    for p, act in plan:
        print(f"  {act:<40} {p}")
    if conflicts and not a.force:
        print(f"\nCONFLICT: {len(conflicts)} file(s) were edited here since the sender's base; merge by hand "
              f"(the bundle's copy is in the zip) and re-run with --force to overwrite.", file=sys.stderr)
        return 3
    if a.dry_run:
        print("\ndry run: nothing written")
        return 0
    written = 0
    for f in man["files"]:
        target = root / f["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(z.read(f"{top}/files/{f['path']}"))
        written += 1
    if a.apply_deletions:
        for d in man.get("deleted", []):
            t = root / d
            if t.exists():
                t.unlink()
    man["review"]["applied_at"] = dt.datetime.now().isoformat(timespec="seconds")
    (manifests_dir(root) / f"{man['bundle_id']}.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    inbox = root / "transfer" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    (inbox / f"{man['bundle_id']}.REVIEW.md").write_text(review_sheet(man, pol), encoding="utf-8")
    append_log(root, f"| {dt.date.today().isoformat()} | received from {man['from_site']} | {man['bundle_id']} | "
                     f"{written} | {man['purpose']} | {git_head(root) or ''} |")
    print(f"\napplied {written} file(s) from {man['bundle_id']}; manifest and review sheet recorded")
    report_drift(root, man)
    if a.commit:
        msg = f"Apply bundle {man['bundle_id']} from {man['from_site']}: {man['purpose']}"
        subprocess.run(["git", "add", "-A"], cwd=root, check=False)
        r = subprocess.run(["git", "commit", "-q", "-m", msg], cwd=root, check=False)
        print("committed" if r.returncode == 0 else "git commit failed or nothing to commit")
    return 0


# ----------------------------------------------------------------------------- drift

def report_drift(root: Path, man: dict, limit=10):
    """
    The manifest carries the sender's whole exportable tree, not only what it sent. Comparing
    it against this site tells us whether the incremental baseline has slipped: a file the
    sender holds that never arrived here would otherwise be a silent under-send.
    """
    tree = man.get("tree") or {}
    missing, differing = [], []
    for rel, sha in tree.items():
        p = root / rel
        if not p.exists():
            missing.append(rel)
        elif sha256(p.read_bytes()) != sha:
            differing.append(rel)
    if not missing and not differing:
        print(f"drift check: this site matches all {len(tree)} file(s) of {man['from_site']}'s "
              f"shared layer.")
        return [], []
    print(f"drift check against {man['from_site']}'s shared layer ({len(tree)} files): "
          f"{len(missing)} missing here, {len(differing)} differing.")
    for rel in missing[:limit]:
        print(f"  missing   {rel}")
    for rel in differing[:limit]:
        print(f"  differs   {rel}")
    if len(missing) + len(differing) > limit:
        print("  ...")
    print("  Differences are expected where this site has edited a file or holds a newer version. "
          "Anything MISSING that you expected to have should be requested with --all or --since.")
    return missing, differing


def cmd_drift(a):
    z, top, man = read_bundle(Path(a.bundle))
    root = Path(a.root).resolve() if a.root else Path.cwd()
    report_drift(root, man, limit=a.limit)
    return 0


# ----------------------------------------------------------------------------- peers / revoke

def cmd_peers(a):
    policy = Policy(a.policy)
    root = Path(a.root).resolve() if a.root else repo_root_from(Path(a.policy))
    site = a.site
    for peer in policy.sites:
        if peer == site:
            continue
        state, used = peer_state(root, site, peer)
        print(f"{peer}: believed to hold {len(state)} file(s) of the shared layer, "
              f"from {len(used)} bundle(s)" + (f" [{used[0]}..{used[-1]}]" if used else " (none yet)"))
        allowed, _, _ = walk_tree(root, policy, site)
        tree = {rel: sha256(ap.read_bytes()) for rel, ap in allowed}
        changed = [r for r in tree if tree[r] != state.get(r)]
        gone = [r for r in state if r not in tree and not (root / r).exists()]
        print(f"    a bundle now would carry {len(changed)} changed file(s) and "
              f"{len(gone)} deletion(s)")
        if a.verbose:
            for r in sorted(changed)[:20]:
                print(f"      {'new ' if r not in state else 'chg '} {r}")
    rev = revoked_ids(root)
    if rev:
        print(f"revoked bundles (excluded from the baseline): {sorted(rev)}")
    return 0


def cmd_revoke(a):
    root = Path(a.root).resolve() if a.root else Path.cwd()
    mp = manifests_dir(root) / f"{a.bundle_id}.json"
    if not mp.exists():
        raise SystemExit(f"no manifest for {a.bundle_id}")
    p = root / "transfer" / "revoked.json"
    entries = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    if any(e["bundle_id"] == a.bundle_id for e in entries):
        print(f"{a.bundle_id} is already revoked")
        return 0
    entries.append({"bundle_id": a.bundle_id, "reason": a.reason,
                    "at": dt.datetime.now().isoformat(timespec="seconds")})
    p.write_text(json.dumps(entries, indent=1), encoding="utf-8")
    append_log(root, f"| {dt.date.today().isoformat()} | REVOKED | {a.bundle_id} | - | {a.reason} | "
                     f"{git_head(root) or ''} |")
    print(f"revoked {a.bundle_id}: its files are no longer assumed to be at the peer, so the next "
          f"bundle will carry them again.")
    return 0


# ----------------------------------------------------------------------------- scan

def cmd_scan(a):
    policy = Policy(a.policy)
    root = Path(a.root).resolve() if a.root else repo_root_from(Path(a.policy))
    site = a.site
    allowed, n_never, n_unlisted = walk_tree(root, policy, site)
    print(f"site {site} (role {policy.role_of(site)}): {len(allowed)} files exportable by path, "
          f"{n_never} refused by 'never', {n_unlisted} not on the allow list")
    bad = 0
    for rel, ap in allowed:
        viol, warn = policy.check_content(rel, ap.read_bytes(), site)
        if viol:
            bad += 1
            print(f"  VIOLATION {rel}: " + "; ".join(viol))
        elif warn and a.verbose:
            print(f"  warn      {rel}: " + "; ".join(warn))
    print(f"{bad} exportable file(s) would be refused on content")
    return 2 if bad else 0


# ----------------------------------------------------------------------------- selftest

SELFTEST_POLICY = """
protocol_version: 1
project: selftest
policy_version: 1
sites:
  A:
    name: Home
    role: home
  B:
    name: Data
    role: data
transfer:
  max_file_bytes: 100000
  max_bundle_bytes: 1000000
  text_extensions: [.py, .md, .yaml, .csv, .json]
  binary_extensions_allowed: [.png, .pdf]
roles:
  home:
    allow: ["src/**", "docs/**/*.md", "docs/**/*.pdf", "transfer/**", "results/aggregate/**"]
    never: ["site/**", "*.pkl"]
    aggregate_tables: ["results/aggregate/**/*.csv"]
    forbidden_columns: [event_id, driver_id]
    count_columns: [n]
    min_n: 5
    max_rows: 100
    person_columns: [driver]
  data:
    allow: ["src/**", "docs/**/*.md", "transfer/**", "results/aggregate/**"]
    never: ["site/**", "*.pkl", "*.pdf", "**/ingest/**"]
    forbidden_patterns:
      vin: '\\b[A-HJ-NPR-Z0-9]{17}\\b'
      site_path: '[A-Za-z]:\\\\|\\\\\\\\[A-Za-z0-9_.$-]+\\\\'
    warn_patterns:
      email: '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}'
    aggregate_tables: ["results/aggregate/**/*.csv"]
    forbidden_columns: [event_id, driver_id, timestamp]
    count_columns: [n]
    min_n: 5
    max_rows: 100
    person_columns: [driver]
"""


def _mk(root: Path, rel: str, text: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class _Args:
    def __init__(self, **kw):
        defaults = dict(policy=None, root=None, site=None, to=None, purpose="t", since=None, all=False,
                        only=None, bundle_id=None, in_reply_to=None, override=None, bundle=None,
                        force=False, dry_run=False, apply_deletions=False, commit=False, quiet=True,
                        verbose=False, limit=10, reason="not released")
        defaults.update(kw)
        self.__dict__.update(defaults)


def cmd_selftest(a):
    from contextlib import redirect_stdout  # noqa: F401  (used below to keep the log readable)
    results = []

    def check(name, cond, detail=""):
        results.append(cond)
        print(("PASS  " if cond else "FAIL  ") + name + (f"  -- {detail}" if detail else ""))

    # the mini reader agrees with PyYAML when both are available
    try:
        import yaml  # type: ignore
        check("mini_yaml matches PyYAML on the selftest policy",
              mini_yaml(SELFTEST_POLICY) == yaml.safe_load(SELFTEST_POLICY))
    except ImportError:
        check("mini_yaml parses the selftest policy", isinstance(mini_yaml(SELFTEST_POLICY), dict))

    check("glob: **/ prefix optional", matches("a.py", ["**/*.py"]) and matches("x/y/a.py", ["**/*.py"]))
    check("glob: basename pattern matches at depth", matches("x/y/z.pkl", ["*.pkl"]))
    check("glob: dir pattern", matches("site/ingest/load.py", ["site/**"]) and not matches("src/site.py", ["site/**"]))

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        A, B = td / "A", td / "B"
        for r in (A, B):
            _mk(r, "transfer/transfer_policy.yaml", SELFTEST_POLICY)
        _mk(A, "src/model.py", "x = 1\n")
        _mk(A, "docs/note.md", "# note\n")
        _mk(A, "site/ingest/load.py", "SECRET = 'C:\\\\data\\\\raw'\n")
        _mk(A, "src/blob.pkl", "binary")
        # a file only the HOME role may export: the asymmetry that broke incremental transfer
        (A / "docs").mkdir(parents=True, exist_ok=True)
        (A / "docs" / "report.pdf").write_bytes(b"%PDF-1.4 fake\n")
        ra = cmd_make(_Args(policy=str(A / "transfer/transfer_policy.yaml"), site="A", to="B",
                            purpose="first", all=True))
        z1 = A / "transfer" / "outbox" / f"A-{dt.date.today().isoformat()}-001.zip"
        check("make --all from home succeeds", ra == 0 and z1.exists())
        names = zipfile.ZipFile(z1).namelist()
        check("site layer and pkl are not in the bundle",
              not any("site/ingest" in n or n.endswith(".pkl") for n in names))
        check("policy and code are in the bundle",
              any(n.endswith("transfer/transfer_policy.yaml") for n in names) and any(n.endswith("src/model.py") for n in names))
        rc = cmd_check(_Args(bundle=str(z1), policy=str(B / "transfer/transfer_policy.yaml")), quiet=True)[0]
        check("check passes at the receiver", rc == 0)
        rapp = cmd_apply(_Args(bundle=str(z1), policy=str(B / "transfer/transfer_policy.yaml"), root=str(B)))
        check("apply writes the files", rapp == 0 and (B / "src/model.py").read_text() == "x = 1\n")
        check("apply records the manifest and the log",
              (B / "transfer/manifests" / z1.stem.replace(".zip", "")).with_suffix(".json").exists()
              and "received from A" in (B / "transfer/TRANSFER_LOG.md").read_text())

        # data site changes code, adds an aggregate table, and a forbidden per-event table
        _mk(B, "src/model.py", "x = 2\n")
        _mk(B, "results/aggregate/levels.csv", "cell,n,mean\nc1,12,0.4\nc2,7,0.6\n")
        _mk(B, "results/aggregate/events.csv", "event_id,n,mean\ne1,1,0.4\n")
        pb = str(B / "transfer/transfer_policy.yaml")
        r_bad = cmd_make(_Args(policy=pb, site="B", to="A", purpose="results", since=z1.stem))
        check("data-site bundle refused on a per-event table", r_bad == 2)
        (B / "results/aggregate/events.csv").unlink()
        _mk(B, "results/aggregate/small.csv", "cell,n,mean\nc1,3,0.4\n")
        check("min_n violation refused", cmd_make(_Args(policy=pb, site="B", to="A", purpose="r", since=z1.stem)) == 2)
        (B / "results/aggregate/small.csv").unlink()
        _mk(B, "docs/note.md", "# note\nsee \\\\\\\\vccserver\\\\share\\\\x\n")
        check("site path pattern refused", cmd_make(_Args(policy=pb, site="B", to="A", purpose="r", since=z1.stem)) == 2)
        _mk(B, "docs/note.md", "# note\nchanged at B\n")
        # the default baseline is the derived peer state, not one bundle's tree
        r_ok = cmd_make(_Args(policy=pb, site="B", to="A", purpose="results"))
        z2 = B / "transfer" / "outbox" / f"B-{dt.date.today().isoformat()}-001.zip"
        check("data-site bundle with aggregate table succeeds", r_ok == 0 and z2.exists())
        man2 = json.loads(zipfile.ZipFile(z2).read(f"{z2.stem}/MANIFEST.json"))
        check("only changed files are bundled",
              sorted(f["path"] for f in man2["files"]) == ["docs/note.md", "results/aggregate/levels.csv", "src/model.py"])
        check("base hashes recorded for modified files",
              all(f["base_sha256"] for f in man2["files"] if f["status"] == "modified"))
        # regression: the home-only file exists at B but B may not export it -- not a deletion
        check("a file the sender's role cannot export is NOT reported as deleted",
              man2["deleted"] == [] and (B / "docs/report.pdf").exists(), str(man2["deleted"]))
        check("peer state counts what is NOT re-sent", man2["unchanged_count"] >= 1)

        # home edited model.py meanwhile -> conflict
        _mk(A, "src/model.py", "x = 3\n")
        pa = str(A / "transfer/transfer_policy.yaml")
        check("conflict detected when the receiver edited the same file",
              cmd_apply(_Args(bundle=str(z2), policy=pa, root=str(A))) == 3)
        check("--force applies over the conflict",
              cmd_apply(_Args(bundle=str(z2), policy=pa, root=str(A), force=True)) == 0
              and (A / "src/model.py").read_text() == "x = 2\n")

        # regression: the return leg must not re-send what the peer already holds
        _mk(A, "docs/note.md", "# note, revised at A\n")
        check("home bundle after a round trip succeeds",
              cmd_make(_Args(policy=pa, site="A", to="B", purpose="doc fix")) == 0)
        z3 = A / "transfer" / "outbox" / f"A-{dt.date.today().isoformat()}-002.zip"
        man3 = json.loads(zipfile.ZipFile(z3).read(f"{z3.stem}/MANIFEST.json"))
        sent3 = sorted(f["path"] for f in man3["files"])
        check("only the edited file is re-sent after a round trip", sent3 == ["docs/note.md"], str(sent3))
        check("the home-only file is not re-sent every round trip", "docs/report.pdf" not in sent3)

        # a bundle that is never released is revoked, and its files go again
        state_before, _ = peer_state(A, "A", "B")
        check("peer state includes the file just bundled", bool(state_before.get("docs/note.md")))
        cmd_revoke(_Args(bundle_id=z3.stem, root=str(A), reason="steward rejected it"))
        state_after, _ = peer_state(A, "A", "B")
        check("revoke removes the bundle from the baseline",
              state_after.get("docs/note.md") != state_before.get("docs/note.md"))
        check("the next bundle carries the revoked file again",
              cmd_make(_Args(policy=pa, site="A", to="B", purpose="resend")) == 0
              and "docs/note.md" in [f["path"] for f in json.loads(
                  (manifests_dir(A) / f"A-{dt.date.today().isoformat()}-003.json").read_text())["files"]])

        # a genuine deletion IS reported, and drift is detected
        (A / "docs/note.md").unlink()
        cmd_make(_Args(policy=pa, site="A", to="B", purpose="removal"))
        man5 = json.loads((manifests_dir(A) / f"A-{dt.date.today().isoformat()}-004.json").read_text())
        check("a file genuinely removed from disk IS reported as deleted",
              man5["deleted"] == ["docs/note.md"], str(man5["deleted"]))
        buf = io.StringIO()
        with redirect_stdout(buf):
            missing, differing = report_drift(B, man5)
        check("drift is silent when the two sites match", not missing and not differing,
              f"missing={missing[:3]} differing={differing[:3]}")
        (B / "src/model.py").unlink()          # simulate a file that never arrived
        _mk(B, "results/aggregate/levels.csv", "cell,n,mean\nc1,12,0.9\n")   # and one that diverged
        with redirect_stdout(buf):
            missing, differing = report_drift(B, man5)
        check("drift reports a file the sender holds that the receiver lacks",
              missing == ["src/model.py"], f"missing={missing}")
        check("drift reports a file that differs between the sites",
              differing == ["results/aggregate/levels.csv"], f"differing={differing}")

        # tampering is detected
        z3 = td / "tampered.zip"
        with zipfile.ZipFile(z2) as zin, zipfile.ZipFile(z3, "w") as zout:
            for n in zin.namelist():
                data = zin.read(n)
                if n.endswith("src/model.py"):
                    data = b"x = 99\n"
                zout.writestr(n, data)
        check("hash mismatch refused", cmd_check(_Args(bundle=str(z3), policy=pa), quiet=True)[0] == 2)

        # override records an exception and lets a flagged bundle through
        _mk(B, "results/aggregate/per_driver.csv", "driver,n,level\nd1,20,0.3\n")
        r_ov = cmd_make(_Args(policy=pb, site="B", to="A", purpose="per-driver levels", since=z1.stem,
                              override="steward NN approved per-driver fitted levels on 2026-09-03"))
        check("override lets a steward-approved exception through", r_ov == 0)

    n_pass = sum(results)
    print(f"\n{n_pass} passed, {len(results) - n_pass} failed")
    return 0 if n_pass == len(results) else 1


# ----------------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    default_policy = "transfer/transfer_policy.yaml"

    m = sub.add_parser("make", help="build a bundle from this site's shared layer")
    m.add_argument("--policy", default=default_policy)
    m.add_argument("--root", default=None, help="repository root (default: the policy's parent's parent)")
    m.add_argument("--site", default=os.environ.get("TRANSFER_SITE"), required="TRANSFER_SITE" not in os.environ)
    m.add_argument("--to", required=True)
    m.add_argument("--purpose", required=True)
    m.add_argument("--since", default=None,
                   help="pin the baseline to one bundle's tree instead of the derived peer state")
    m.add_argument("--all", action="store_true", help="bundle the whole shared layer (first bundle)")
    m.add_argument("--only", nargs="*", default=None, help="restrict to these paths or folders")
    m.add_argument("--bundle-id", default=None)
    m.add_argument("--in-reply-to", default=None)
    m.add_argument("--override", default=None, help="record a steward-approved exception and proceed despite violations")

    c = sub.add_parser("check", help="verify a received bundle against the policy")
    c.add_argument("bundle")
    c.add_argument("--policy", default=default_policy)

    p = sub.add_parser("apply", help="check, then write a bundle's files into this repository")
    p.add_argument("bundle")
    p.add_argument("--policy", default=default_policy)
    p.add_argument("--root", default=None)
    p.add_argument("--force", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--apply-deletions", action="store_true")
    p.add_argument("--commit", action="store_true")
    p.add_argument("--quiet", action="store_true")

    s = sub.add_parser("scan", help="report what in the working tree would be refused for export")
    s.add_argument("--policy", default=default_policy)
    s.add_argument("--root", default=None)
    s.add_argument("--site", default=os.environ.get("TRANSFER_SITE"), required="TRANSFER_SITE" not in os.environ)
    s.add_argument("--verbose", action="store_true")

    pe = sub.add_parser("peers", help="what each peer is believed to hold, and what a bundle would carry")
    pe.add_argument("--policy", default=default_policy)
    pe.add_argument("--root", default=None)
    pe.add_argument("--site", default=os.environ.get("TRANSFER_SITE"), required="TRANSFER_SITE" not in os.environ)
    pe.add_argument("--verbose", action="store_true")

    rv = sub.add_parser("revoke", help="mark a bundle as never released, so its files are sent again")
    rv.add_argument("bundle_id")
    rv.add_argument("--reason", required=True)
    rv.add_argument("--root", default=None)

    dr = sub.add_parser("drift", help="compare this site against the sender's tree in a bundle")
    dr.add_argument("bundle")
    dr.add_argument("--root", default=None)
    dr.add_argument("--limit", type=int, default=10)

    sub.add_parser("selftest", help="run the built-in end-to-end test in a temporary directory")

    a = ap.parse_args(argv)
    if a.cmd == "make":
        return cmd_make(a)
    if a.cmd == "check":
        return cmd_check(a)[0]
    if a.cmd == "apply":
        return cmd_apply(a)
    if a.cmd == "scan":
        return cmd_scan(a)
    if a.cmd == "peers":
        return cmd_peers(a)
    if a.cmd == "revoke":
        return cmd_revoke(a)
    if a.cmd == "drift":
        return cmd_drift(a)
    if a.cmd == "selftest":
        return cmd_selftest(a)
    return 1


if __name__ == "__main__":
    sys.exit(main())
