"""Unit tests of ``gov links`` (W2-129) on planted repositories: no model, no network, no GPU, no store.

Each case commits a small repository in a temporary folder and runs ``gov links`` on it through ``gov.cli.main``,
as a user would; the engineer's own regression evidence (the acceptance tests are the test designer's).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.main import main  # noqa: E402
from gov.links import check  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
REG = "docs/DECISION_REGISTER.md"


def _path_map(register: str = REG, comment: str = "") -> str:
    """A path map that gov's configuration check accepts (every top-level key), naming ``register``."""
    from gov.config.path_map_schema import SYSTEM_KEYS

    namespace = ("    memory_class: governance\n    sensitivity: internal\n    permitted_roles: [engineer]\n"
                 "    retention: r\n    export_policy: e\n    embedding_policy: n\n    provenance: p\n"
                 "    deletion_rebuild: d\n")
    policies = "".join(f"  {name}: hard-block\n" for name in ("security", "authority", "test", "change",
                                                                 "human_gate", "tool"))
    policies += "".join(f"  {name}: warning\n" for name in ("memory", "context", "checkpoint", "model_routing",
                                                             "budget", "learning", "archive"))
    systems = "".join(f"  {name}:\n    status: absent\n    reason: r\n" for name in SYSTEM_KEYS)
    return (f"{comment}state_class: AUTHORITATIVE\nnamespaces:\n  all:\n    paths: [\"**\"]\n" + namespace
            + "capabilities:\n  code_intelligence:\n    enabled: false\n  research_corpus:\n    enabled: false\n"
            + "policies:\n" + policies + "systems:\n" + systems + f"decision_register: {register}\n")


PATH_MAP = _path_map()

ENTRIES = """\
### DEC-100: The first rule
**Status:** ACCEPTED

The first rule's text.

### DEC-101: A rule changed in part
**Status:** ACCEPTED

Its text.

### DEC-102: A change to the rule
**Status:** ACCEPTED · **Changes:** DEC-101 (item 2)

It changes DEC-101.

### DEC-103: A rule superseded whole
**Status:** ACCEPTED

Old text.

### DEC-104: The rule that supersedes
**Status:** ACCEPTED · **Supersedes:** DEC-103
- Its text.

### DEC-105: A marked change
**Status:** ACCEPTED · **Changed by:** DEC-106

Text.

### DEC-106: It changes DEC-105
**Status:** ACCEPTED · **Changes:** DEC-105

Text.

### DEC-107: A rule amended in free text
**Status:** ACCEPTED

Text.

### DEC-108: The amender
**Status:** ACCEPTED

DEC-107 is amended by DEC-108 for its first point.

### DEC-109: A proposal
**Status:** PROPOSED

Not decided.

### DEC-110: A rejected one
**Status:** REJECTED

No.

### DEC-111: Under a proposal
**Status:** ACCEPTED · **Under:** DEC-109

Text.
"""


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True,
                          env={**_ENV, "HOME": str(root)}).stdout


def _write(root: Path, files: dict) -> None:
    for rel, text in files.items():
        if text is None:
            (root / rel).unlink()
            continue
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")


def _commit(root: Path, files: dict, message: str = "r\n\nTask: decision-record\nRole: orchestrator") -> str:
    _write(root, files)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "--allow-empty", "-m", message)
    return _git(root, "rev-parse", "HEAD").strip()


def _plant(tmp_path: Path, files: dict | None = None, register: str = ENTRIES) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    base = {"governance/project/path-map.yaml": PATH_MAP, REG: "# Register\n\n" + register}
    _commit(root, {**base, **(files or {})})
    return root


def _ticket(record_id: str, status: str, sources: list[str], kpi: str = "", extra: str = "") -> str:
    lines = ["---", f"id: {record_id}", f"status: {status}", "type: task"]
    lines += ["sources:"] + [f"- {s}" for s in sources] if sources else []
    if kpi:
        lines += ["kpis:", "  success:", f"  - '{kpi}'"]
    return "\n".join(lines + ([extra] if extra else []) + ["---", "# body", ""])


def _run(root: Path, *args: str, capsys) -> tuple[int, str, str]:
    code = main(["links", "--root", str(root), *args])
    out, err = capsys.readouterr()
    return code, out, err


def _lines(out: str, code: str) -> list[str]:
    return [line for line in out.splitlines()[1:] if line.startswith(code + " ")]


# ---------------------------------------------------------------- UNMARKED_CHANGE

def test_unmarked_change_names_both_ids_the_form_and_part_or_whole(tmp_path, capsys):
    root = _plant(tmp_path)
    code, out, _ = _run(root, "--all", capsys=capsys)
    found = _lines(out, "UNMARKED_CHANGE")
    part = next(line for line in found if line.startswith("UNMARKED_CHANGE DEC-101 <- DEC-102"))
    assert "**Changes:**" in part and "part" in part and "(text)" not in part
    assert "orchestrator" in part.split(" | ")[2] and '"**Changed by:** DEC-102 (item 2)"' in part
    whole = next(line for line in found if line.startswith("UNMARKED_CHANGE DEC-103 <- DEC-104"))
    assert "whole" in whole and "SUPERSEDED by DEC-104" in whole
    free = next(line for line in found if line.startswith("UNMARKED_CHANGE DEC-107 <- DEC-108"))
    assert free.split(" | ")[0].endswith("(text)")
    assert not any(line.startswith("UNMARKED_CHANGE DEC-105 ") for line in found)  # its status line names DEC-106
    assert code == 1


def test_a_supersedes_followed_by_plain_text_is_a_part_as_register_statements_reads_it(tmp_path, capsys):
    """The CTO's point (3): the one pattern set decides, though the loader's SUPERSEDES edge reads ids alone."""
    extra = ("\n### DEC-112: Old\n**Status:** ACCEPTED\n\nx\n\n### DEC-113: New\n**Status:** ACCEPTED · "
             "**Supersedes:** DEC-112\n\nPlain text after the label.\n")
    root = _plant(tmp_path, register=ENTRIES + extra)
    _, out, _ = _run(root, "--all", capsys=capsys)
    line = next(line for line in _lines(out, "UNMARKED_CHANGE") if line.startswith("UNMARKED_CHANGE DEC-112 <- DEC-113"))
    assert "(**Supersedes:**; part)" in line and '"**Changed by:** DEC-113"' in line


def test_the_status_line_is_the_findings_line(tmp_path, capsys):
    root = _plant(tmp_path)
    _, out, _ = _run(root, "--all", capsys=capsys)
    line = next(line for line in _lines(out, "UNMARKED_CHANGE") if " DEC-101 <- " in line)
    number = int(line.split(" | ")[1].rpartition(":")[2])
    text = (root / REG).read_text().split("\n")
    assert text[number - 1].startswith("**Status:** ACCEPTED") and text[number - 2].startswith("### DEC-101:")


def test_archive_section_a_states_a_change(tmp_path, capsys):
    archive = "# Archive\n\n## A. Superseded\n- DEC-100: amended by DEC-104 (its scope).\n\n## B. Spent\n"
    root = _plant(tmp_path, {check.ARCHIVE_REL: archive})
    _, out, _ = _run(root, "--all", capsys=capsys)
    line = next(line for line in _lines(out, "UNMARKED_CHANGE") if line.startswith("UNMARKED_CHANGE DEC-100 <- DEC-104"))
    assert "ARCHIVE-SUPERSEDED §A" in line and "(text)" in line


# ---------------------------------------------------------------- UNKNOWN_ID, UNLINKED_ID, NOT_IN_FORCE_AS_RULE

def test_the_typed_places_of_tickets(tmp_path, capsys):
    root = _plant(tmp_path, {
        ".tickets/T-aaaa.md": _ticket("T-aaaa", "in_progress", ["DEC-100", "DEC-999", "DEC-109", "Free text source"],
                                      "One line [DEC-104, DEC-998]",
                                      "acceptance_tests:\n  path: tests/acceptance/W2-01/"),
        ".tickets/T-bbbb.md": _ticket("T-bbbb", "closed", ["DEC-109"], "",
                                      "acceptance_tests:\n  path: tests/acceptance/W2-02/"),
        ".tickets/T-cccc.md": _ticket("T-cccc", "open", [], "", "acceptance_tests:\n  path: tests/acceptance/W2-03/"),
    })
    _, out, _ = _run(root, "--all", capsys=capsys)
    unknown = _lines(out, "UNKNOWN_ID")
    assert any(line.startswith("UNKNOWN_ID DEC-999 in T-aaaa's sources") for line in unknown)
    assert any(line.startswith("UNKNOWN_ID DEC-998 in T-aaaa's KPI brackets") for line in unknown)
    assert not any("Free" in line for line in unknown)
    paths = [line for line in unknown if "acceptance_tests.path" in line]
    assert {line.split(" ")[1] for line in paths} == {"tests/acceptance/W2-01", "tests/acceptance/W2-02"}
    unlinked = _lines(out, "UNLINKED_ID")
    assert any(line.startswith("UNLINKED_ID DEC-104 in T-aaaa's KPI brackets") for line in unlinked)
    ruled = _lines(out, "NOT_IN_FORCE_AS_RULE")
    assert any(line.startswith("NOT_IN_FORCE_AS_RULE DEC-109 (PROPOSED) in T-aaaa's sources") for line in ruled)
    assert not any("T-bbbb" in line for line in ruled)  # a closed ticket bears no rule now
    for line in unknown + unlinked + ruled:
        if ".tickets/" in line:
            assert line.split(" | ")[2] == "orchestrator"


def test_the_register_labels_and_under(tmp_path, capsys):
    extra = "\n### DEC-112: A label to nothing\n**Status:** ACCEPTED · **Refines:** DEC-950\n\nText.\n"
    root = _plant(tmp_path, register=ENTRIES + extra)
    _, out, _ = _run(root, "--all", capsys=capsys)
    assert any(line.startswith("UNKNOWN_ID DEC-950 in DEC-112's **Refines:**") for line in _lines(out, "UNKNOWN_ID"))
    assert any(line.startswith("NOT_IN_FORCE_AS_RULE DEC-109 (PROPOSED) in DEC-111's **Under:**")
               for line in _lines(out, "NOT_IN_FORCE_AS_RULE"))


def test_records_contract_kernel_and_list_rows(tmp_path, capsys):
    contract = ("id: CONTRACT-v4\nstatus: ACCEPTED\nmaster_rules:\n- id: MR-1\n  provider: [W1-01]\n"
                "  sources: [DEC-100]\ncapabilities:\n- id: CAP-01\n  provider: [W1-01, 'MADR tool', W1-77]\n"
                "  sources: [DEC-100, DEC-997]\n")
    root = _plant(tmp_path, {
        check.CONTRACT_REL: contract,
        ".tickets/T-dddd.md": _ticket("T-dddd", "closed", ["W2-L001"], "", "wbs_id: W1-01"),
        "docs/plan/LIST.md": "| Row | What |\n|---|---|\n| W2-L001 | a row |\n",
        "docs/lessons/L-0001.md": "---\nid: L-0001\ntype: lesson\nstatus: ACTIVE\nconstrains: [T-zzzz]\n---\nx\n",
        "docs/contract/master-rules/MR-1.md": "---\nid: MR-1\ntype: specification\nstatus: PROPOSED\n---\nx\n",
        "template/governance/kernel/skills/s/SKILL.md": "A line (DEC-100, DEC-996).\nA rule from DEC-109.\n",
        "governance/project/prompts/p.md": "Follow DEC-110.\n",
        "governance/project/path-map.yaml": _path_map(comment="# the register's place (DEC-109)\n"),
    })
    _, out, _ = _run(root, "--all", capsys=capsys)
    unknown = _lines(out, "UNKNOWN_ID")
    assert any(line.startswith("UNKNOWN_ID W1-77 in CAP-01's provider") and "product-spec" in line for line in unknown)
    assert any(line.startswith("UNKNOWN_ID DEC-997 in CAP-01's sources") for line in unknown)
    assert not any("MADR" in line or line.startswith("UNKNOWN_ID W2-L001") for line in unknown)  # free text; a row
    assert any(line.startswith("UNKNOWN_ID T-zzzz in L-0001's constrains") for line in unknown)
    assert any(line.startswith("UNKNOWN_ID DEC-996 in a kernel line") for line in unknown)
    ruled = _lines(out, "NOT_IN_FORCE_AS_RULE")
    assert any(line.startswith("NOT_IN_FORCE_AS_RULE DEC-109 (PROPOSED) in a kernel line") and " | product-spec | "
               in line for line in ruled)
    assert any(line.startswith("NOT_IN_FORCE_AS_RULE DEC-110 (REJECTED) in a brief or prompt line") for line in ruled)
    assert any(line.startswith("NOT_IN_FORCE_AS_RULE DEC-109 (PROPOSED) in a path-map comment") for line in ruled)
    conflict = _lines(out, "STATUS_CONFLICT")
    assert any(line.startswith("STATUS_CONFLICT MR-1 PROPOSED against contract.yaml ACCEPTED") for line in conflict)


def test_commit_trailers(tmp_path, capsys):
    root = _plant(tmp_path, {".tickets/T-eeee.md": _ticket("T-eeee", "in_progress", ["DEC-100"], "", "wbs_id: W2-77")})
    worker = _commit(root, {"src/a.py": "x = 1\n"},
                     "w\n\nTask: W2-77\nImplements: DEC-104, DEC-109, DEC-995\nRole: engineer")
    landing = _commit(root, {"src/b.py": "y = 1\n"}, "land\n\nTask: T-eeee\nImplements: DEC-101\nRole: orchestrator")
    stray = _commit(root, {"src/c.py": "z = 1\n"}, "s\n\nTask: T-nope\nRole: engineer")
    _, out, _ = _run(root, "--all", capsys=capsys)
    assert any(line.startswith("UNKNOWN_ID DEC-995 in") and f"| {worker}:" in line and " | engineer | " in line
               for line in _lines(out, "UNKNOWN_ID"))
    assert any(line.startswith("UNKNOWN_ID T-nope in") and f"| {stray}:" in line for line in _lines(out, "UNKNOWN_ID"))
    unlinked = _lines(out, "UNLINKED_ID")
    assert any(line.startswith("UNLINKED_ID DEC-104 in") and worker[:12] in line for line in unlinked)
    assert not any(landing[:12] in line for line in unlinked)  # a landing commit's ids are not the ticket's
    assert any(line.startswith("NOT_IN_FORCE_AS_RULE DEC-109 (PROPOSED) in") for line in _lines(out, "NOT_IN_FORCE_AS_RULE"))
    assert not any("decision-record" in line for line in out.splitlines())


def test_a_commits_finding_names_its_role_then_the_lead_once_landed(tmp_path, capsys):
    """S9: the role field is the commit's ``Role:``; landed, the lead is the JSON ``lead``; no ``Role:``, the
    orchestrator."""
    root = _plant(tmp_path)
    main_branch = _git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    direct = _commit(root, {"src/a.py": "x\n"}, "d\n\nTask: T-one\nRole: engineer")
    bare = _commit(root, {"src/b.py": "x\n"}, "b\n\nTask: T-two")
    _git(root, "checkout", "-q", "-b", "side")
    landed = _commit(root, {"tests/t.py": "x\n"}, "t\n\nTask: T-three\nRole: independent-test-designer")
    _git(root, "checkout", "-q", main_branch)
    _git(root, "merge", "-q", "--no-ff", "-m", "land\n\nTask: decision-record\nRole: orchestrator", "side")
    _, out, _ = _run(root, "--all", capsys=capsys)
    roles = {line.split(" | ")[1].rpartition(":")[0]: line.split(" | ")[2] for line in _lines(out, "UNKNOWN_ID")}
    assert roles[direct] == "engineer"
    assert roles[bare] == "orchestrator"
    assert roles[landed] == "independent-test-designer"
    assert not any("Role:" in line.split(" | ")[3] for line in _lines(out, "UNKNOWN_ID"))  # not in the fix
    (root / check.MARK_REL).unlink()
    _, out, _ = _run(root, "--all", "--json", capsys=capsys)
    leads = {f["commit"]: f.get("lead") for f in json.loads(out)["result"]["findings"] if f["code"] == "UNKNOWN_ID"}
    assert leads[landed] == "orchestrator" and leads[direct] is None and leads[bare] is None


# ---------------------------------------------------------------- S16: ticket changes

_SCOPED = "title: A ticket\nassignee: engineer\nlinks: []\nallowed_paths:\n- src/a/**\n"


def _s16(tmp_path, status: str = "open") -> Path:
    return _plant(tmp_path, {".tickets/T-mmmm.md": _ticket("T-mmmm", status, ["DEC-100"], "A line", _SCOPED)})


def _edit(root: Path, old: str, new: str, message: str = "e\n\nTask: decision-record\nRole: orchestrator") -> str:
    text = (root / ".tickets/T-mmmm.md").read_text()
    assert old in text
    return _commit(root, {".tickets/T-mmmm.md": text.replace(old, new)}, message)


def test_a_closed_tickets_file_edited_is_a_finding_a_decision_does_not_excuse(tmp_path, capsys):
    root = _s16(tmp_path, "closed")
    sha = _edit(root, "# body", "# body\n\nA note added after the close (DEC-100).",
                "e\n\nTask: decision-record\nImplements: DEC-100\nRole: orchestrator")
    _, out, _ = _run(root, "--all", capsys=capsys)
    found = _lines(out, "CLOSED_TICKET_EDITED")
    assert len(found) == 1 and found[0].startswith(f"CLOSED_TICKET_EDITED T-mmmm {sha[:12]} body")
    assert found[0].split(" | ")[2] == "orchestrator" and found[0].split(" | ")[1].startswith(".tickets/T-mmmm.md:")


def test_reopening_a_closed_ticket_is_an_edit_of_it(tmp_path, capsys):
    root = _s16(tmp_path, "closed")
    sha = _edit(root, "status: closed", "status: open")
    _, out, _ = _run(root, "--all", capsys=capsys)
    assert [line.split(" | ")[0] for line in _lines(out, "CLOSED_TICKET_EDITED")] == [
        f"CLOSED_TICKET_EDITED T-mmmm {sha[:12]} status: closed before the commit"]


@pytest.mark.parametrize("old, new, field", [
    ("A line", "Another line", "kpis"),
    ("- src/a/**", "- src/a/**\n- src/b/**", "allowed_paths"),
    ("title: A ticket", "title: A wider ticket", "title"),
    ("---\n# body", "depends_on: [T-mmmm]\n---\n# body", "depends_on"),
])
def test_an_open_tickets_scope_changed_unmarked_names_ticket_commit_and_field(tmp_path, capsys, old, new, field):
    root = _s16(tmp_path)
    sha = _edit(root, old, new)
    _, out, _ = _run(root, "--all", capsys=capsys)
    found = _lines(out, "TICKET_CHANGE_UNMARKED")
    assert [line.split(" | ")[0].split(":")[0] for line in found] == [f"TICKET_CHANGE_UNMARKED T-mmmm {sha[:12]} {field}"]
    assert found[0].split(" | ")[2] == "orchestrator"


@pytest.mark.parametrize("old, new, message", [
    ("A line", "A line (DEC-100)", None),  # the decision in an added line
    ("A line", "Another line", "e\n\nTask: decision-record\nImplements: DEC-100\nRole: orchestrator"),
    ("A line", "Another line", "e\n\nTask: decision-record\nDecided-by: DEC-100\nRole: orchestrator"),
    ("status: open", "status: in_progress", None),  # status, assignee and links alone are none
    ("assignee: engineer", "assignee: research", None),
    ("links: []", "links: [T-zzzz]", None),
    ("status: open\n", "status: closed\n", None),  # the closing commit itself
])
def test_marked_or_unwatched_ticket_changes_are_not_findings(tmp_path, capsys, old, new, message):
    root = _s16(tmp_path)
    if old == "status: open\n":  # a closing commit that also edits a KPI
        text = (root / ".tickets/T-mmmm.md").read_text().replace(old, new).replace("A line", "Done line")
        _commit(root, {".tickets/T-mmmm.md": text})
    else:
        _edit(root, old, new, *([message] if message else []))
    _, out, _ = _run(root, "--all", capsys=capsys)
    assert _lines(out, "TICKET_CHANGE_UNMARKED") == [] and _lines(out, "CLOSED_TICKET_EDITED") == []


def test_a_decision_in_a_removed_line_marks_the_change(tmp_path, capsys):
    root = _plant(tmp_path, {".tickets/T-mmmm.md": _ticket("T-mmmm", "open", [], "A line [DEC-100]", _SCOPED)})
    _edit(root, "A line [DEC-100]", "A line")
    _, out, _ = _run(root, "--all", capsys=capsys)
    assert _lines(out, "TICKET_CHANGE_UNMARKED") == []


def test_a_ticket_change_is_listed_only_when_its_commit_is_in_the_range(tmp_path, capsys):
    root = _s16(tmp_path)
    old = _edit(root, "A line", "Another line")
    head = _git(root, "rev-parse", "HEAD").strip()
    new = _edit(root, "- src/a/**", "- src/c/**")
    code, out, _ = _run(root, "--since", head, capsys=capsys)
    listed = out.splitlines()[1:]
    assert code == 1 and len(listed) == 1 and listed[0].startswith(f"TICKET_CHANGE_UNMARKED T-mmmm {new[:12]} ")
    assert "TICKET_CHANGE_UNMARKED orchestrator 1" in out.splitlines()[0]  # the older one, standing
    _, out, _ = _run(root, "--all", capsys=capsys)
    assert any(line.startswith(f"TICKET_CHANGE_UNMARKED T-mmmm {old[:12]} kpis") for line in out.splitlines())


# ---------------------------------------------------------------- STATUS_CONFLICT and ENFORCES_SUPERSEDED

def test_status_conflicts(tmp_path, capsys):
    archive = "# Archive\n\n## A. Superseded\n\n## B. Spent\n- DEC-100: a run. Spent.\n- DEC-109: Spent.\n"
    in_force = ("# In force\n\n## Rules\n- DEC-103: still listed.\n- DEC-100: fine.\n\n## Lifted (was x)\n"
                "- DEC-103: lifted.\n")
    root = _plant(tmp_path, {
        check.ARCHIVE_REL: archive, check.IN_FORCE_REL: in_force,
        ".tickets/T-ffff.md": _ticket("T-ffff", "in_progress", []),
        "docs/close/T-ffff/CL-T-ffff.md": "---\nid: CL-T-ffff\ntype: close\nstatus: ACTIVE\ntask: T-ffff\n---\nx\n",
    })
    _, out, _ = _run(root, "--all", capsys=capsys)
    conflict = _lines(out, "STATUS_CONFLICT")
    assert any(line.startswith("STATUS_CONFLICT DEC-100 ACCEPTED in the register, spent") for line in conflict)
    assert not any(line.startswith("STATUS_CONFLICT DEC-109 ") for line in conflict)  # PROPOSED is never current
    listed = [line for line in conflict if "DECISIONS-IN-FORCE" in line]
    assert len(listed) == 1 and listed[0].startswith("STATUS_CONFLICT DEC-103 superseded in the register")
    assert any(line.startswith("STATUS_CONFLICT T-ffff in_progress against its close record") for line in conflict)


def test_enforces_superseded_is_propagations(tmp_path, capsys):
    root = _plant(tmp_path, {"src/rule.py": "# DEC-103 says so\n"})
    _, out, _ = _run(root, "--all", capsys=capsys)
    found = _lines(out, "ENFORCES_SUPERSEDED")
    assert len(found) == 1 and "| src/rule.py:1 | engineer |" in found[0]


def test_never_a_gate_nothing_outside_the_package_calls_it():
    """No close, landing, launch, claim, readiness check or hook calls it: no code outside ``src/gov/links`` names
    the package or the command."""
    import re

    call = re.compile(r"(from|import)\s+gov\.links|gov\.links\.|^[^#]*\bgov\s+links\b", re.MULTILINE)
    callers = []
    for base in ("src", "template/governance/kernel/hooks", "template/governance/kernel/checks"):
        for path in (REPO / base).rglob("*"):
            if path.is_file() and path.suffix in (".py", ".sh", ".yaml", ".json") and "links" not in path.parts:
                text = path.read_text(encoding="utf-8", errors="replace")
                found = call.search(text) if path.suffix == ".sh" else re.search(r"(from|import)\s+gov\.links", text)
                if found:
                    callers.append(str(path.relative_to(REPO)))
    assert callers == []


# ---------------------------------------------------------------- the role table

@pytest.mark.parametrize("path, role", [
    (".tickets/T-a.md", "orchestrator"), ("docs/plan/x.md", "orchestrator"), ("docs/lessons/L-1.md", "orchestrator"),
    ("governance/project/briefs/b.md", "orchestrator"), ("governance/project/orchestration/X.md", "orchestrator"),
    ("template/governance/kernel/roles/r.md", "product-spec"), ("docs/contract/contract.yaml", "product-spec"),
    ("src/gov/x.py", "engineer"), ("tests/unit/x.py", "independent-test-designer"),
    ("docs/audit/a.md", "independent-auditor"), ("docs/research/r.md", "research"), ("README.md", "orchestrator"),
    (REG, "orchestrator"), ("governance/project/path-map.yaml", "orchestrator"),
])
def test_role_table(path, role):
    assert check.role_of(path) == role


# ---------------------------------------------------------------- incremental, the mark and the exit codes

def test_no_mark_and_no_since_refuses_naming_since(tmp_path, capsys):
    root = _plant(tmp_path)
    code, out, err = _run(root, capsys=capsys)
    assert code == 2 and "--since" in err and not (root / check.MARK_REL).exists()


def test_the_mark_holds_heads_sha_alone_and_nothing_else_is_written(tmp_path, capsys):
    root = _plant(tmp_path)
    before = _git(root, "status", "--porcelain", "--ignored", "--untracked-files=all")
    code, out, _ = _run(root, "--since", "HEAD", capsys=capsys)
    after = _git(root, "status", "--porcelain", "--ignored", "--untracked-files=all")
    assert code == 0 and out.startswith("gov links: 0 new since HEAD, ")
    assert (root / check.MARK_REL).read_text() == _git(root, "rev-parse", "HEAD").strip()
    assert set(after.splitlines()) - set(before.splitlines()) == {"?? .gov-runtime/links/mark"}


def test_a_mark_it_cannot_write_is_named_and_the_findings_stand(tmp_path, capsys):
    root = _plant(tmp_path, {".tickets/T-nnnn.md": _ticket("T-nnnn", "open", ["DEC-999"])})
    (root / ".gov-runtime").mkdir()
    (root / ".gov-runtime/links").write_text("not a folder")  # the mark's folder cannot be made
    code, out, err = _run(root, "--all", capsys=capsys)
    assert code == 1 and "LINKS_MARK_UNWRITTEN" in err and "Traceback" not in err
    assert any(line.startswith("UNKNOWN_ID DEC-999 in T-nnnn's sources") for line in out.splitlines())


def test_findings_older_than_the_mark_are_counted_and_listed_with_all(tmp_path, capsys):
    root = _plant(tmp_path, {".tickets/T-gggg.md": _ticket("T-gggg", "open", ["DEC-999"])})
    _run(root, "--all", capsys=capsys)  # sets the mark
    _commit(root, {".tickets/T-hhhh.md": _ticket("T-hhhh", "open", ["DEC-994"])})
    code, out, _ = _run(root, capsys=capsys)
    first, *rest = out.splitlines()
    assert code == 1 and first.startswith("gov links: 1 new since ") and " standing (" in first
    assert "UNKNOWN_ID orchestrator 1" in first  # T-gggg's, standing, counted by code and role
    assert len(rest) == 1 and rest[0].startswith("UNKNOWN_ID DEC-994 in T-hhhh's sources")
    code, out, _ = _run(root, capsys=capsys)  # the mark moved to HEAD: nothing new
    assert code == 0 and out.startswith("gov links: 0 new since ")
    code, out, _ = _run(root, "--all", capsys=capsys)  # the standing ones listed
    assert code == 0 and out.startswith("gov links: 0 new since ")
    assert any(line.startswith("UNKNOWN_ID DEC-999 in T-gggg's sources") for line in out.splitlines())
    assert any(line.startswith("UNKNOWN_ID DEC-994 in T-hhhh's sources") for line in out.splitlines())


def test_a_changed_entry_makes_the_findings_naming_it_new(tmp_path, capsys):
    root = _plant(tmp_path)
    head = _git(root, "rev-parse", "HEAD").strip()
    text = (root / REG).read_text() + "\n### DEC-113: Amends the first\n**Status:** ACCEPTED · **Amends:** DEC-100\n"
    _commit(root, {REG: text})
    code, out, _ = _run(root, "--since", head, capsys=capsys)
    new = out.splitlines()[1:]
    assert code == 1 and [line.split(" | ")[0] for line in new] == ["UNMARKED_CHANGE DEC-100 <- DEC-113 (**Amends:**; part)"]


def test_a_change_stated_only_in_the_archive_is_new_when_the_archive_changes(tmp_path, capsys):
    """A hand list is judged by line: the §B conflict already there stays standing."""
    archive = "# Archive\n\n## A. Superseded\n\n## B. Spent\n- DEC-100: a run. Spent.\n"
    root = _plant(tmp_path, {check.ARCHIVE_REL: archive})
    head = _git(root, "rev-parse", "HEAD").strip()
    _commit(root, {check.ARCHIVE_REL: archive.replace("## B.", "- DEC-100: amended by DEC-104.\n\n## B.")})
    _, out, _ = _run(root, "--since", head, capsys=capsys)
    assert [line.split(" | ")[0] for line in out.splitlines()[1:]] == [
        "UNMARKED_CHANGE DEC-100 <- DEC-104 (ARCHIVE-SUPERSEDED §A: amended by; part) (text)"]


def test_an_entry_a_changed_entry_names_lists_its_own_findings_only(tmp_path, capsys):
    root = _plant(tmp_path, {".tickets/T-kkkk.md": _ticket("T-kkkk", "open", [], "A line [DEC-101]")})
    head = _git(root, "rev-parse", "HEAD").strip()
    text = (root / REG).read_text() + "\n### DEC-113: Amends again\n**Status:** ACCEPTED · **Amends:** DEC-101\n"
    _commit(root, {REG: text})
    _, out, _ = _run(root, "--since", head, capsys=capsys)
    new = [line.split(" | ")[0] for line in out.splitlines()[1:]]
    # the named entry's new pair only: its older pair and T-kkkk's UNLINKED DEC-101 stand
    assert new == ["UNMARKED_CHANGE DEC-101 <- DEC-113 (**Amends:**; part)"]


def test_a_status_changed_in_the_range_makes_a_finding_in_an_unchanged_file_new(tmp_path, capsys):
    root = _plant(tmp_path, {".tickets/T-llll.md": _ticket("T-llll", "open", ["DEC-100"])})
    head = _git(root, "rev-parse", "HEAD").strip()
    _commit(root, {REG: (root / REG).read_text().replace("### DEC-100: The first rule\n**Status:** ACCEPTED",
                                                         "### DEC-100: The first rule\n**Status:** PROPOSED")})
    _, out, _ = _run(root, "--since", head, capsys=capsys)
    assert [line.split(" | ")[0] for line in out.splitlines()[1:]] == [
        "NOT_IN_FORCE_AS_RULE DEC-100 (PROPOSED) in T-llll's sources"]


def test_an_older_commits_finding_is_counted_standing(tmp_path, capsys):
    root = _plant(tmp_path)
    _commit(root, {"src/a.py": "x\n"}, "w\n\nTask: decision-record\nImplements: DEC-109\nRole: engineer")
    _run(root, "--since", "HEAD", capsys=capsys)  # the mark at HEAD
    _commit(root, {"src/b.py": "y\n"})
    _, out, _ = _run(root, capsys=capsys)
    assert "NOT_IN_FORCE_AS_RULE engineer 1" in out.splitlines()[0]


def test_cannot_run_exits_2_named(tmp_path, capsys):
    plain = tmp_path / "plain"
    plain.mkdir()
    code, _, err = _run(plain, "--all", capsys=capsys)
    assert code == 2 and "LINKS_NOT_A_WORK_TREE" in err
    root = _plant(tmp_path)
    _commit(root, {"governance/project/path-map.yaml": _path_map("docs/GONE.md")})
    code, out, _ = _run(root, "--all", "--json", capsys=capsys)
    envelope = json.loads(out)
    assert code == 2 and envelope["ok"] is False and envelope["error"]["code"] == "STORE_REGISTER_UNREADABLE"


def test_a_repository_without_the_kinds_is_not_applicable(tmp_path, capsys):
    root = tmp_path / "bare"
    root.mkdir()
    _git(root, "init", "-q")
    _commit(root, {"README.md": "x\n"})
    code, out, _ = _run(root, "--all", capsys=capsys)
    assert code == 0 and "not applicable: path map, register, ARCHIVE-SUPERSEDED, DECISIONS-IN-FORCE, " \
                          "contract.yaml, .tickets" in out.splitlines()[0]


def test_json_is_the_shared_envelope_with_the_same_findings(tmp_path, capsys):
    root = _plant(tmp_path)
    _, text, _ = _run(root, "--all", capsys=capsys)
    (root / check.MARK_REL).unlink()
    code, out, _ = _run(root, "--all", "--json", capsys=capsys)
    envelope = json.loads(out)
    assert code == 1 and envelope["ok"] and envelope["command"] == "links"
    findings = envelope["result"]["findings"]
    assert [check.render(f) for f in findings] == text.splitlines()[1:]
    assert all({"code", "ids", "path", "line", "role", "fix", "text", "new"} <= set(f) for f in findings)


# ---------------------------------------------------------------- the patches

def test_propose_marks_applies_and_clears_the_findings(tmp_path, capsys):
    root = _plant(tmp_path)
    code, out, _ = _run(root, "--propose-marks", capsys=capsys)
    assert code == 0 and not (root / check.MARK_REL).exists()
    (tmp_path / "marks.patch").write_text(out)
    _git(root, "apply", "--check", str(tmp_path / "marks.patch"))
    assert "+**Status:** ACCEPTED · SUPERSEDED by DEC-104" in out
    assert "+**Status:** ACCEPTED · **Changed by:** DEC-102 (item 2)" in out
    _git(root, "apply", str(tmp_path / "marks.patch"))
    _commit(root, {})
    _, out, _ = _run(root, "--all", capsys=capsys)
    assert _lines(out, "UNMARKED_CHANGE") == []


def test_propose_sources_applies_and_clears_the_findings(tmp_path, capsys):
    root = _plant(tmp_path, {
        ".tickets/T-iiii.md": _ticket("T-iiii", "open", ["DEC-100"], "A line [DEC-104, DEC-102]"),
        ".tickets/T-jjjj.md": _ticket("T-jjjj", "open", [], "A line [DEC-100]"),
    })
    code, out, _ = _run(root, "--propose-sources", capsys=capsys)
    assert code == 0 and not (root / check.MARK_REL).exists()
    (tmp_path / "sources.patch").write_text(out)
    _git(root, "apply", str(tmp_path / "sources.patch"))
    _commit(root, {})
    _, out, _ = _run(root, "--all", capsys=capsys)
    assert _lines(out, "UNLINKED_ID") == []
    assert "- DEC-100\n- DEC-102\n- DEC-104\nkpis:" in (root / ".tickets/T-iiii.md").read_text()
    assert "sources:\n- DEC-100\n---" in (root / ".tickets/T-jjjj.md").read_text()
