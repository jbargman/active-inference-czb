"""
Property tests for the split-site transfer tooling (transfer/bundle.py,
transfer/validate_interface.py, transfer/make_synthetic_fixture.py) and for the project's
own policy file.

The bundle tool's end-to-end behavior (make, check, apply, conflicts, refusals, override,
tampering) is its built-in selftest, run here in a temporary directory. The checks added
on top are about THIS project's policy: that the real file parses identically with and
without PyYAML, that the paths which must never leave either site are classified 'never',
that the shared layer is allowed at both sites, and that the synthetic fixture passes the
interface validator.

Run: python tests/test_transfer.py
"""
import io
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "transfer"))

import bundle  # noqa: E402
import make_synthetic_fixture  # noqa: E402
import validate_interface  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS  " if cond else "FAIL  ") + name + (f"  -- {detail}" if detail else ""))


def main():
    # 1 the tool's own end-to-end selftest
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = bundle.cmd_selftest(None)
    tail = buf.getvalue().strip().splitlines()[-1]
    check("bundle.py selftest passes", rc == 0, tail)

    # 2 the project's policy file
    pol_path = ROOT / "transfer" / "transfer_policy.yaml"
    text = pol_path.read_text(encoding="utf-8")
    mini = bundle.mini_yaml(text)
    try:
        import yaml
        check("policy parses identically with PyYAML and the built-in reader", mini == yaml.safe_load(text))
    except ImportError:
        check("policy parses with the built-in reader", isinstance(mini, dict))
    pol = bundle.Policy(pol_path)
    check("policy names a home site and a data site",
          sorted(pol.role_of(s) for s in pol.sites) == ["data", "home"])

    never_both = ["external/gs4bu-osfstorage-archive/x.pkl", "OthersWork/a.md", "site/ingest/load.py",
                  "papers/x.pdf", "replication/czb/out/run.log", "transfer/outbox/X.zip"]
    for site in pol.sites:
        check(f"{site}: paths that must never leave are 'never'",
              all(pol.classify(p, site) == "never" for p in never_both),
              str([p for p in never_both if pol.classify(p, site) != "never"]))
        check(f"{site}: the shared layer is allowed",
              all(pol.classify(p, site) == "allowed" for p in
                  ["src/comfortzone/cutin.py", "tests/test_cutin.py", "transfer/bundle.py",
                   "transfer/transfer_policy.yaml", "docs/split_site_protocol.md", "README.md"]))
    check("CTH: private correspondence is never bundled, whatever its file type",
          all(pol.classify(p, "CTH") == "never" for p in
              ["correspondence/2026-09-11_authors_reply_to_method_review.md",
               "correspondence/any/depth/letter.pdf"]))
    data_only_never = ["site/data/E0001.csv", "src/site/preprocess/x.py", "notes/data/raw/x.csv",
                       "docs/x.pdf", "replication/czb/out/driver_levels.csv"]
    check("VCC: data-shaped paths and documents that could embed data are refused",
          all(pol.classify(p, "VCC") in ("never", "unlisted") for p in data_only_never),
          str([(p, pol.classify(p, "VCC")) for p in data_only_never]))
    check("VCC: results are allowed only under results/aggregate",
          pol.classify("results/aggregate/levels.csv", "VCC") == "allowed"
          and pol.classify("results/levels.csv", "VCC") == "unlisted")

    # content rules at the data site
    v, w = pol.check_content("results/aggregate/cells.csv", b"cell,n,mean\nc1,12,0.4\n", "VCC")
    check("VCC: an aggregate table with n >= min_n passes", not v, str(v))
    v, w = pol.check_content("results/aggregate/cells.csv", b"cell,n,mean\nc1,4,0.4\n", "VCC")
    check("VCC: n below min_n is a violation", any("min_n" in x for x in v))
    v, w = pol.check_content("results/aggregate/cells.csv", b"event_id,n,mean\nE1,12,0.4\n", "VCC")
    check("VCC: an event_id column is a violation", any("forbidden column" in x for x in v))
    v, w = pol.check_content("docs/notes_from_VCC.md", "path D:\\\\nds\\\\raw\\\\trip.csv\n".encode(), "VCC")
    check("VCC: a Windows data path in a document is a violation", any("windows_or_unc_path" in x for x in v))
    v, w = pol.check_content("docs/notes_from_VCC.md", b"logged 2026-09-03 14:05 in the trip\n", "VCC")
    check("VCC: a wall-clock timestamp in a document is a violation", any("iso_timestamp" in x for x in v))
    v, w = pol.check_content("docs/x.md", b"contact jonas.bargman@chalmers.se\n", "CTH")
    check("CTH: documents with e-mail addresses pass at the home site", not v and not w)

    # 3 the synthetic fixture validates against the interface schema
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "synthetic"
        with redirect_stdout(io.StringIO()):
            make_synthetic_fixture.main(out)
        schema = bundle.load_yaml(ROOT / "transfer" / "interface_schema.yaml")
        hard, soft = validate_interface.validate(out, schema)
        check("synthetic fixture passes the interface validator", not hard, str(hard[:3]))
        check("synthetic fixture has 12 events and a metadata table",
              len([p for p in out.glob("*.csv") if p.name != "events.csv"]) == 12 and (out / "events.csv").exists())
        # a broken fixture is caught
        bad = out / "E0001.csv"
        bad.write_text(bad.read_text(encoding="utf-8").replace("\n0.05,", "\n0.03,", 1), encoding="utf-8")
        hard, soft = validate_interface.validate(out, schema)
        check("validator: a broken time axis is reported", any("monotonic" in h or "step" in h for h in hard) or soft)
        meta = out / "events.csv"
        meta.write_text(meta.read_text(encoding="utf-8").replace("E0002", "TRIP_2026_01_01_0002"), encoding="utf-8")
        hard, soft = validate_interface.validate(out, schema)
        check("validator: a non-pseudonymous event_id is a failure", any("event_id" in h for h in hard))

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
