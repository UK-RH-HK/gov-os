"""The checks bite: each judging function of this suite is fed one input that behaves as the line says (it passes) and one
that does not (it fails). These cases test the suite's own checks, never the product, so they are GREEN on the base by design
(README names the folder: "bite checks"). Covered: S2's ticket form, S19's diff test, S20's AST check, S7/S8's record
sections, the byte-identical comparison (S1/F1), the category lookup of S1, and S9's examin-run judge (its own file).
The end-to-end bites (a stand-in stage for S1's record and the secret grep, a stand-in layout for S10) are in
``standin/`` and run as README "Bite checks" says.
"""

from __future__ import annotations

import hashlib

import pytest

import test_w2_88_s7_s9_proofs as proofs
import w2_88_plan_support as P
import w2_88_sets_support as T
import w2_88_support as W

DIGEST = hashlib.sha256(b"assessment").hexdigest()
GOOD = f"""---
title: Move the vendored copy of acme into a folder of its own
class: C2
allowed_paths:
  - src/app/lib_copy.py
  - vendor/**
kpis:
  success:
    - 'The vendored copy lives in vendor/acme. Verify: git ls-files vendor/acme lists it'
  failure:
    - 'A file of the copy stays in src/. Verify: git ls-files src | grep lib_copy finds none'
profile: STANDARD
sources:
  - memory-assessment sha256:{DIGEST}
---

# a proposed ticket
"""


def test_the_ticket_form_check_passes_a_good_ticket():
    assert P.ticket_problems(GOOD, DIGEST) == []


@pytest.mark.parametrize("mutant, expected", [
    (lambda t: t.replace(" Verify: git ls-files vendor/acme lists it", ""), "Verify"),
    (lambda t: t.replace(DIGEST, "0" * 64), "sources"),
    (lambda t: t.replace("  failure:\n    - 'A file of the copy stays in src/. Verify: git ls-files src | grep lib_copy finds none'\n", ""),
     "kpis.failure"),
    (lambda t: t.replace("profile: STANDARD", "profile: HUGE"), "profile"),
    (lambda t: t.replace("allowed_paths:\n  - src/app/lib_copy.py\n  - vendor/**\n", ""), "allowed_paths"),
    (lambda t: t.replace("title: Move the vendored copy of acme into a folder of its own\n", ""), "title"),
    (lambda t: t.split("---\n", 2)[2], "frontmatter"),
])
def test_the_ticket_form_check_fails_each_defect(mutant, expected):
    problems = P.ticket_problems(mutant(GOOD), DIGEST)
    assert any(expected in p for p in problems), (expected, problems)


@pytest.mark.parametrize("kind", T.KINDS)
def test_the_diff_check_passes_a_variant_that_changes_only_the_blind_list_and_the_domain_table(kind):
    base = T.gov_brief(kind)
    lines = base.splitlines()
    blind = next(i for i, l in enumerate(lines) if l.startswith("## 4.") and "never read" in l)
    lines.insert(blind + 3, "| The repository's own ledger: `ops/ledger/**` | the audit stays blind to it | this brief only |")
    if kind == "writer":
        row = next(i for i, l in enumerate(lines) if l.startswith("   | Count |"))
        lines[row] = "   | Count | 6 | 4 | 4 | 4 | 4 | 4 | 3 | 3 | 3 | 3 | 1 | 1 |"
    if kind == "checker":
        five_a = next(i for i, l in enumerate(lines) if l.startswith("### 5a"))
        lines.insert(five_a + 2, "(the repository's own twelve domains, mapped)")
    assert T.diff_outside(kind, base, "\n".join(lines) + "\n") == []


@pytest.mark.parametrize("kind", T.KINDS)
def test_the_diff_check_fails_a_variant_that_changes_anything_else(kind):
    base = T.gov_brief(kind)
    lines = base.splitlines()
    first = next(i for i, l in enumerate(lines) if l.startswith("## 1."))
    lines.insert(first + 2, "An extra sentence of the repository's own about the job.")
    assert T.diff_outside(kind, base, "\n".join(lines) + "\n"), "a change in section 1 was let through"


@pytest.mark.parametrize("source, flagged", [
    ("def run_preflight(x):\n    return x\n", True),
    ("USED = 'used.marker'\n", True),
    ("def compute_figures(n):\n    return n\n", True),
    ("class Preflight:\n    pass\n", True),
    ("from gov.memaudit import preflight, figures\n\ndef audit_record(x):\n    return preflight.run(x)\n", False),
    ("import gov.memaudit.declare as declare\n\ndef cost(n):\n    return {}\n", False),
])
def test_the_ast_check_flags_a_second_copy_and_lets_an_import_pass(source, flagged):
    assert bool(T.second_copies(source, "memory_sets.py")) is flagged


def test_the_ast_check_finds_the_import_from_gov_memaudit():
    assert T.imports_from_memaudit("from gov.memaudit import preflight\n")
    assert T.imports_from_memaudit("import gov.memaudit.declare\n")
    assert not T.imports_from_memaudit("from gov.rebuild import command\n")


RECORD = """# W2-88 evidence

## Proof (a): W2-81's five synthetic repositories

Built under ~/gov-os-runs/W2-88/proving-ground/. The largest, legacy-docs: 412 files, peak_rss_bytes 91234567.

### Python with drifted specs

commit 0123456789ab; size 90 files; the assessment found 3 blockers; the plan's proposals: 3 (secret, over-limit, no-namespace);
per-store figures: record, lexical, vectors, codegraph; the measure: right 0.8.

### Rust workspace

commit 123456789abc.

## Proof (d): EXAMIN's copy

No adoption run on EXAMIN's copy; W2-27 runs it at adoption.
"""


def test_the_record_parser_finds_each_proof_section(monkeypatch):
    assert "legacy-docs" in proofs.proof(RECORD, "a") and "W2-27" in proofs.proof(RECORD, "d")
    assert "W2-27" not in proofs.proof(RECORD, "a")
    assert proofs.proof(RECORD.replace("## Proof (d)", "## Notes"), "d").strip() == ""


def test_the_repository_state_comparison_sees_each_kind_of_change(tmp_path):
    root = tmp_path / "r"
    root.mkdir()
    W.write(root, "a.txt", "one\n")
    W.git(root, "init", "-q", "-b", "main")
    W.commit_all(root, "one")
    W.settle(root)
    before = W.repo_state(root)
    W.assert_state_equal(before, W.repo_state(root), "nothing done")
    (root / "a.txt").write_text("two\n", encoding="utf-8")
    with pytest.raises(AssertionError):
        W.assert_state_equal(before, W.repo_state(root), "a file edited")
    (root / "a.txt").write_text("one\n", encoding="utf-8")
    W.write(root, "b.txt", "new\n")
    with pytest.raises(AssertionError):
        W.assert_state_equal(before, W.repo_state(root), "an untracked file")
    (root / "b.txt").unlink()
    W.git(root, "commit", "-q", "--allow-empty", "-m", "an empty commit")
    with pytest.raises(AssertionError):
        W.assert_state_equal(before, W.repo_state(root), "a commit")


def test_the_category_lookup_reads_a_file_or_a_folder_and_its_by():
    items = [{"path": "vendor/acme", "by": "folder"}, {"path": "gen/tables.py", "by": "header"}, "assets/logo.png"]
    assert W.holds(items, "vendor/acme/lib.py", "folder") and not W.holds(items, "vendor/acme/lib.py", "name")
    assert W.holds(items, "gen/tables.py", "header") and W.holds(items, "assets/logo.png")
    assert not W.holds(items, "src/app/main.py") and not W.holds(items, "vendor/acmeX/lib.py")
    assert W.holds([{"path": "data/big.txt", "reason": "over-limit"}], "data/big.txt", reason="over-limit")
    assert not W.holds([{"path": "data/big.txt", "reason": "over-limit"}], "data/big.txt", reason="binary")
