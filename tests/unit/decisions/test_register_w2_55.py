"""Builder tests for the register's tags, the propagation check and what is in force (W2-55).

Regression evidence only (DEC-136): each case commits a small register in a temporary repository, as the store
reads it from ``HEAD``. They pin the builder's choices the specification leaves open: a ``**Supersedes:**`` that
names a part changes the entry and does not supersede it (DEC-825 item 4), the id named on the old entry's status
segment marks a relation, a kept file needs a reason, and an expanded register chunk that touches a left-out entry
falls back to its own chunk or is left out.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import decisions  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.decisions import register  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
KERNEL = "template/governance/kernel/skills/x.md"
PROMPT = "governance/project/prompts/p.md"
TAGS_K = f"- **Tags:** domain: guard · scope: kernel · lands in: {KERNEL}"
TAGS_R = f"- **Tags:** domain: plan · scope: repository · lands in: {PROMPT}"


def _repo(tmp_path: Path, entries: str, files: dict | None = None) -> Path:
    root = tmp_path / "repo"
    texts = {"governance/project/path-map.yaml": "decision_register: docs/REG.md\n",
             "docs/REG.md": "# Register\n\n" + entries, KERNEL: "x\n", PROMPT: "p\n", **(files or {})}
    for rel, text in texts.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    for args in (("init", "-q"), ("add", "-A"), ("commit", "-q", "-m", "r")):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(root)})
    return root


def _codes(found):
    return sorted((finding["code"], tuple(finding["ids"])) for finding in found)


def test_complete_tags_pass_and_each_defect_is_named(tmp_path):
    root = _repo(tmp_path, f"""### DEC-101 — good
- **Status:** ACCEPTED
{TAGS_K}

### DEC-102 — no tags
- **Status:** ACCEPTED

### DEC-103 — no scope, odd domain
- **Status:** ACCEPTED
- **Tags:** domain: weather · lands in: {KERNEL}

### DEC-104 — misplaced and unknown
- **Status:** ACCEPTED
- **Tags:** domain: plan · scope: kernel · lands in: {PROMPT}, template/governance/kernel/gone.md

### DEC-105 — in force and lands nowhere
- **Status:** ACCEPTED
- **Tags:** domain: plan · scope: galaxy · lands in: none
""")
    assert _codes(decisions.check_tags(root)) == [
        ("TAG_DOMAIN_UNKNOWN", ("DEC-103",)), ("TAG_LANDS_IN_MISPLACED", ("DEC-105",)),
        ("TAG_LANDS_IN_UNKNOWN", ("DEC-104",)), ("TAG_MISSING", ("DEC-102",)), ("TAG_MISSING", ("DEC-103",)),
        ("TAG_SCOPE_UNKNOWN", ("DEC-105",))]
    assert "scope" in next(f["message"] for f in decisions.check_tags(root) if f["ids"] == ["DEC-103"]
                           and f["code"] == "TAG_MISSING")


def test_status_relations_and_successors(tmp_path):
    root = _repo(tmp_path, f"""### DEC-101 — old
- **Status:** ACCEPTED
{TAGS_K}

### DEC-102 — superseded, nobody named
- **Status:** SUPERSEDED (long ago)
- **Tags:** domain: plan · scope: repository · lands in: none

### DEC-103 — new
- **Status:** ACCEPTED · **Supersedes:** DEC-101 · **Corrects:** DEC-104
{TAGS_R}

### DEC-104 — corrected and marked in its status words
- **Status:** ACCEPTED (corrected by DEC-103)
{TAGS_R}
""")
    assert _codes(decisions.check_tags(root)) == [("STATUS_RELATION_UNMARKED", ("DEC-101", "DEC-103")),
                                                  ("STATUS_SUCCESSOR_UNNAMED", ("DEC-102",))]


def test_a_partial_supersedes_changes_and_the_digest_names_it(tmp_path):
    root = _repo(tmp_path, f"""### DEC-101 — partly replaced
- **Status:** ACCEPTED · **Changed by:** DEC-103
{TAGS_K}

### DEC-102 — a one-off
- **Status:** ACCEPTED
- **Tags:** domain: plan · scope: repository · lands in: none · done

### DEC-103 — new
- **Status:** ACCEPTED · **Supersedes:** the last point of DEC-101
{TAGS_R}
""")
    digest = register.in_force(root)
    assert digest["lines"] == ["DEC-101 — partly replaced (changed by DEC-103)", "DEC-103 — new"]
    assert digest["left_out"] == {"count": 1, "superseded": [], "done": ["DEC-102"]}
    assert decisions.check_tags(root) == []


def test_propagation_finds_the_sweep_kinds_and_honours_a_kept_reason(tmp_path):
    root = _repo(tmp_path, f"""### DEC-636 — the 300k window
- **Status:** SUPERSEDED by DEC-838
- **Tags:** domain: launch · scope: kernel · lands in: none
- **Values:** "300000"
- **Kept:** tests/kept.py — a history note

### DEC-605 — the judge imports the project's code
- **Status:** ACCEPTED · **Changed by:** DEC-822, DEC-835
{TAGS_K}
- **Values:** "sys.path.insert(0, str(PROJECT"

### DEC-822 — the judge is pinned
- **Status:** ACCEPTED · **Changes:** DEC-605
{TAGS_K}

### DEC-835 — the canary
- **Status:** ACCEPTED · **Changes:** DEC-605
{TAGS_K}

### DEC-838 — the window per role
- **Status:** ACCEPTED · **Supersedes:** DEC-636
{TAGS_K}
""", {"tests/test_window.py": "WINDOW = 300000  # DEC-636\n",
      "tests/kept.py": "# DEC-636 said 300000\n",
      "tests/cites_both.py": "# DEC-636, superseded by DEC-838\n",
      "tests/judge.py": "x = 1\nsys.path.insert(0, str(PROJECT / 'src'))\n",
      "src/only_id.py": "# DEC-605\n",
      "docs/notes.md": "300000 DEC-636\n",
      ".tickets/T-1.md": "---\nid: T-1\nstatus: closed\n---\n300000\n",
      ".tickets/T-2.md": "---\nid: T-2\nstatus: open\n---\nkpi: 300000\n"})
    found = decisions.check_propagation(root)
    assert [(f["ids"], f["paths"]) for f in found] == [
        (["DEC-605", "DEC-822"], ["tests/judge.py"]), (["DEC-605", "DEC-835"], ["tests/judge.py"]),
        (["DEC-636", "DEC-838"], [".tickets/T-2.md"]), (["DEC-636", "DEC-838"], ["tests/test_window.py"])]
    assert all(f["code"] == "ENFORCES_SUPERSEDED" for f in found)
    assert "tests/judge.py:2" in found[0]["message"] and "DEC-822" in found[0]["message"]


def test_no_register_is_empty_and_a_named_register_missing_refuses(tmp_path):
    root = _repo(tmp_path, "", {"governance/project/path-map.yaml": "other: x\n"})
    assert decisions.check_tags(root) == [] and register.in_force(root)["left_out"]["count"] == 0
    root2 = _repo(tmp_path / "b", "", {"governance/project/path-map.yaml": "decision_register: docs/NONE.md\n"})
    for call in (decisions.check_tags, decisions.check_propagation, register.in_force):
        with pytest.raises(GovError):
            call(root2)


def test_leave_out_drops_a_superseded_entry_and_counts_it(tmp_path):
    from gov.store import load

    root = _repo(tmp_path, f"""### DEC-101 — old
- **Status:** SUPERSEDED by DEC-102
- **Tags:** domain: plan · scope: repository · lands in: none

### DEC-102 — new
- **Status:** ACCEPTED · **Supersedes:** DEC-101
{TAGS_R}
""")
    load(root)
    lines = (root / "docs/REG.md").read_text().split("\n")
    old, new = lines.index("### DEC-101 — old") + 1, lines.index("### DEC-102 — new") + 1
    evidence = [{"path": "docs/REG.md", "start_line": old, "end_line": old + 2, "chunk_id": "a"},
                {"path": "docs/REG.md", "start_line": new, "end_line": new + 2, "chunk_id": "b"},
                {"path": PROMPT, "start_line": 1, "end_line": 1, "chunk_id": "c"}]
    kept, left_out = register.leave_out(root, evidence)
    assert [item["chunk_id"] for item in kept] == ["b", "c"]
    assert left_out == {"count": 1, "superseded": ["DEC-101"], "done": []}
    assert register.leave_out(root, evidence[1:]) == (evidence[1:], None)
