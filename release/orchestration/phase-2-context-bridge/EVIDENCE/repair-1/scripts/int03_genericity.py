"""BR-AR-0028 check 3 (OC-BR-02 genericity audit). Run from the domain with $PY.

Two greps:
  (1) the DAG's own grep, verbatim: grep -rnE 'P2-AR-0097|Review[- ]?8|REVIEW-8' govbridge config tests
      --include=*.py --include=*.yaml, excluding fixture data (tests/fixtures/**);
  (2) a broader audit over the same trees and file types: F-findings (F1..F6 as tokens), Phase-2 files and ids
      (orchestration/phase-2/, PHASE_LEDGER, P2-L-, P2-AR-, OD-P2-, P2-ADJ, product_identity) and every Review-8
      chain symbol extracted mechanically from EVIDENCE/review-8/P2-AR-0097-return.verbatim.md (backticked
      identifiers containing '_' or '::', split on '::', length >= 6).
Every hit is classified by an explicit rule table (below) and git-blamed: the introducing commit is tested for
ancestry against the REPAIR-1 base f85d5f3 (the commit that introduced REPAIR_DAG.yaml), so a hit is labelled
PRE_REPAIR_1 or REPAIR_1.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

DOMAIN = Path(__file__).resolve().parents[3]
REPAIR1_BASE = "f85d5f3"


def sh(args, cwd=DOMAIN):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def grep(pattern, extra=()):
    r = sh(["grep", "-rnE", pattern, "govbridge", "config", "tests", "--include=*.py", "--include=*.yaml", *extra])
    out = []
    for line in r.stdout.splitlines():
        path, lineno, text = line.split(":", 2)
        if path.startswith("tests/fixtures/"):
            continue
        out.append((path, int(lineno), text))
    return out


def blame_commit(path, lineno):
    r = sh(["git", "blame", "-L", f"{lineno},{lineno}", "--porcelain", "HEAD", "--", path])
    return r.stdout.split()[0] if r.returncode == 0 and r.stdout else None


def is_pre_repair1(commit):
    if not commit:
        return None
    return sh(["git", "merge-base", "--is-ancestor", commit, REPAIR1_BASE]).returncode == 0


RULE_TEXT = re.compile(r"OC-BR-02|[Nn]othing here|never (a|an|name|names|special)|unrelated to|no (class|facet|"
                       r"Review|Review-8|F-finding)|names no |not a Review-8|never Review-8|Generic")

SYNTH_LOCAL = re.compile(r"\b(CX|EX|RA|MF|RV|CS|FX|T)-[A-Z]+-?\d*#F\d|^## F\d$|^## F\d\b")
GRAMMAR_EXAMPLE = re.compile(r"bare (short|local) token|bare local id|DR-MD-HEADING-LOCAL's bare tokens|\(F1, C1")


def classify(path, text, sym=None):
    if not sym and SYNTH_LOCAL.search(text.strip()):
        return "SYNTHETIC_LOCAL_ID", "a synthetic fixture record's local token (#F1 on a CX-/EX- id); not the Review-8 F1"
    if not sym and path in ("config/id-grammar.yaml", "govbridge/authority/records.py") and GRAMMAR_EXAMPLE.search(text):
        return "GENERIC_GRAMMAR_EXAMPLE", "F1/C1 given as examples of the generic bare-local-token SHAPE"
    if path.startswith("tests/integration/test_demo_grade") and "F1 direct" in text:
        return "GRADER_RULE_LABEL", "asserts the grader's G3 rule label (DEMONSTRATION_DESIGN.md section 4)"
    if RULE_TEXT.search(text) and not sym:
        return "RULE_TEXT", "the line states the genericity rule itself (a negative/rule statement), not a use"
    if path == "config/authority-registry.yaml":
        return "INSTANCE_REGISTRY_DATA", ("the owner-record registry is instance DATA by design (ARCHITECTURE.md "
                                          "section 5.2: classes are assigned by the cited registry); not code")
    if path in ("config/state-aliases.yaml", "config/canonical-view.yaml"):
        return "INSTANCE_VIEW_DATA", "the canonical view / state alias is instance data by design (section 1.2)"
    if path == "tests/compile/test_compile_real_view_mandatory_in_a.py":
        return "MANDATED_REAL_VIEW_TEST", ("ARCHITECTURE.md section 5.3 names this test "
                                           "(test_mandatory_bridge_inputs_classes) over the real ids, as data")
    if path == "govbridge/demo/grade.py":
        return "GRADER_RULE_LABEL", ("a gate-rule label copied from DEMONSTRATION_DESIGN.md section 4 (G3/G6); the "
                                     "logic reads the oracle's own rows, no id hard-coded")
    if path in ("govbridge/compile/bootstrap.py", "govbridge/demo/extract_reads.py"):
        return "ADAPT_PROVENANCE_OR_CANON_TEXT", ("ARCHITECTURE.md section 7.5 ADAPT provenance / verbatim canon "
                                                  "bootstrap text; not retrieval logic")
    if sym and path.startswith("tests/"):
        return "VIOLATION_LETTER_TEST_CODE", ("test CODE names a Review-8 chain symbol as its query literal "
                                              "(fixture data carries it; the test code itself is not data)")
    if sym:
        return "VIOLATION_LETTER_CODE_COMMENT", "a code docstring/comment names a Review-8 chain symbol as an example"
    if path.startswith("tests/"):
        return "VIOLATION_LETTER_TEST_DATA_STRING", "a test names a real Phase-2 path/id as an inline string"
    return "VIOLATION_LETTER_CODE_COMMENT", "a code docstring/comment/config description uses a real id as an example"


def main():
    report = {"repair1_base": REPAIR1_BASE, "head": sh(["git", "rev-parse", "HEAD"]).stdout.strip(),
              "python": sys.executable, "python_version": sys.version.split()[0]}
    dag = grep(r"P2-AR-0097|Review[- ]?8|REVIEW-8")
    report["dag_grep"] = {"cmd": "grep -rnE 'P2-AR-0097|Review[- ]?8|REVIEW-8' govbridge config tests --include=*.py "
                                 "--include=*.yaml | grep -v '^tests/fixtures/'", "hit_count": len(dag)}
    broad_patterns = {
        "F_FINDING": r"\bF[1-6]\b|F1-F6|F2/F3|F2-F3",
        "PHASE2_FILE_OR_ID": r"orchestration/phase-2/|phase-2/(GATES|tools|telemetry|probes)|PHASE_LEDGER|P2-L-00|"
                             r"P2-AR-00|OD-P2-|P2-ADJ|product_identity",
    }
    ev = (DOMAIN / "EVIDENCE/review-8/P2-AR-0097-return.verbatim.md").read_text(encoding="utf-8")
    syms = set()
    for m in re.findall(r"`([A-Za-z_][A-Za-z0-9_:]*[a-z_][A-Za-z0-9_:]*)`", ev):
        if "_" in m or "::" in m:
            for part in m.split("::"):
                # a chain SYMBOL, not an English word: snake_case (contains '_') or CamelCase with >= 2 capitals
                # (FloorIdentity, PolicySet). Plain words (policy, reconcile, Project, brownfield) are excluded --
                # they are generic English and would only produce false positives.
                if len(part) >= 6 and ("_" in part.strip("_") or len(re.findall(r"[A-Z]", part)) >= 2
                                       and not part.isupper()):
                    syms.add(part)
    report["review8_chain_symbols_extracted"] = sorted(syms)
    rows = {}
    for (p, n, t) in dag:
        rows.setdefault((p, n), {"path": p, "line": n, "text": t.strip()[:200], "matched": set()})["matched"].add("DAG_GREP")
    for label, pat in broad_patterns.items():
        for (p, n, t) in grep(pat):
            rows.setdefault((p, n), {"path": p, "line": n, "text": t.strip()[:200], "matched": set()})["matched"].add(label)
    for s in sorted(syms):
        r = sh(["grep", "-rnwF", s, "govbridge", "config", "tests", "--include=*.py", "--include=*.yaml",
                "--include=*.rs", "--include=*.toml"])
        for line in r.stdout.splitlines():
            p, n, t = line.split(":", 2)
            if p.startswith("tests/fixtures/"):
                continue
            rows.setdefault((p, int(n)), {"path": p, "line": int(n), "text": t.strip()[:200], "matched": set()})[
                "matched"].add(f"R8_SYMBOL:{s}")
    out_rows = []
    for key in sorted(rows):
        row = rows[key]
        sym = next((m for m in row["matched"] if m.startswith("R8_SYMBOL:")), None)
        cls, why = classify(row["path"], row["text"], sym=sym)
        c = blame_commit(row["path"], row["line"])
        pre = is_pre_repair1(c)
        out_rows.append({**row, "matched": sorted(row["matched"]), "class": cls, "why": why,
                         "introduced_by": c[:10] if c else None,
                         "era": "PRE_REPAIR_1" if pre else ("REPAIR_1" if pre is False else "UNKNOWN")})
    report["hits"] = out_rows
    summary = {}
    for r in out_rows:
        summary.setdefault(r["class"], {"total": 0, "REPAIR_1": 0, "PRE_REPAIR_1": 0})
        summary[r["class"]]["total"] += 1
        summary[r["class"]][r["era"]] = summary[r["class"]].get(r["era"], 0) + 1
    report["summary_by_class"] = summary
    print(json.dumps(report, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
