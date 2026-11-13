"""Builder tests for stage A0's coordination ticket and its roster key (W2-113, DEC-971 item 4, DEC-957, DEC-982).

Regression evidence only (DEC-136): each line of the lead's specification through ``stages.run`` in a planted git
repository of its own under ``tmp_path`` (the vendored ``tk`` copied from the template, as an adopted project holds
it), and the guard's rule (``cto_install``) on what A0 wrote.
"""
from __future__ import annotations

import shutil
import stat
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.adopt import project, stages  # noqa: E402
from gov.guard import install  # noqa: E402
from gov.guard.install import cto_install  # noqa: E402
from gov.tasks.tickets import TK_REL  # noqa: E402

ROSTER = "governance/project/roster.yaml"
KEY = "coordination_ticket"
NAME = "acme-app"
OTHER_ROLES = ("engineer", "independent-test-designer", "independent-auditor", "product-spec", "research")
OLD_KEYS = ("baseline_commit", "backup_ref", "tree", "set_up")


def sh(root, *args):
    done = subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)
    return done.stdout.strip()


def write(root, rel, text):
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")


def planted(tmp_path, roster=None, tk=True, name=NAME):
    """A planted repository: a product's files, the vendored tk (when ``tk``) and the roster text (when given)."""
    root = tmp_path / name
    write(root, "README.md", "# p\n")
    write(root, ".gitignore", ".gov-runtime/\n")
    if tk:
        (root / TK_REL).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / "template" / TK_REL, root / TK_REL)
        (root / TK_REL).chmod((root / TK_REL).stat().st_mode | stat.S_IXUSR)
    if roster is not None:
        write(root, ROSTER, roster)
    sh(root, "init", "-q", "-b", "main")
    sh(root, "config", "user.name", "t")
    sh(root, "config", "user.email", "t@example.invalid")
    sh(root, "add", "-A")
    sh(root, "commit", "-q", "-m", "fixture")
    return root.resolve()


def ticket_file(root, ident):
    return root / ".tickets" / f"{ident}.md"


def add_ticket(root, ident, wbs=None):
    wbs_line = f"wbs_id: {wbs}\n" if wbs else ""
    write(root, f".tickets/{ident}.md", f"---\nid: {ident}\nstatus: open\n{wbs_line}---\n# {ident}\n")
    sh(root, "add", "-A")
    sh(root, "commit", "-q", "-m", f"ticket {ident}")


def a0(root, session="adopter"):
    args = SimpleNamespace(lite=True, stage="A0", map=None, verdict=None, session=session)
    return stages.run(root, args, {})


def record(root):
    return project.frontmatter((root / project.record_path("A0")).read_text(encoding="utf-8"))


def roster_of(root):
    return yaml.safe_load((root / ROSTER).read_text(encoding="utf-8"))


def tickets(root):
    folder = root / ".tickets"
    return sorted(p.name for p in folder.glob("*.md")) if folder.is_dir() else []


def refusal(root, role="orchestrator", ticket="x", subagent=None):
    allowed, reason = cto_install(str(root), role, subagent, ticket)
    assert allowed is False
    return reason


# ---------------------------------------------------------------------------------------------------------------
# I1: a planted repository adopted
# ---------------------------------------------------------------------------------------------------------------

def test_a0_creates_the_coordination_ticket_and_names_it_in_a_new_roster(tmp_path):
    root = planted(tmp_path)
    result = a0(root)
    rec = record(root)
    ident = rec[KEY]
    assert ident and tickets(root) == [f"{ident}.md"]
    text = ticket_file(root, ident).read_text(encoding="utf-8")
    front = project.frontmatter(text)
    assert front["class"] == "coordination" and front["id"] == ident
    assert f"\n# {NAME} coordination\n" in text            # the title, exact: the repository's folder name
    assert (root / ROSTER).read_text(encoding="utf-8") == f"{KEY}: {ident}\n"
    assert roster_of(root) == {KEY: ident}
    assert rec["roster"] == ROSTER                           # both are recorded
    assert result["coordination_ticket"] == ident and result["roster"] == ROSTER


def test_the_ticket_and_the_roster_are_in_a0s_own_commit_and_the_tree_is_clean(tmp_path):
    root = planted(tmp_path)
    before = sh(root, "rev-parse", "HEAD")
    a0(root)
    ident = record(root)[KEY]
    assert sh(root, "rev-list", "--count", f"{before}..HEAD") == "1"
    changed = set(sh(root, "show", "--name-only", "--format=", "HEAD").split("\n"))
    assert {f".tickets/{ident}.md", ROSTER, project.record_path("A0"), ".gitleaks.toml"} <= changed
    assert sh(root, "status", "--short") == ""


def test_a0s_old_record_keys_are_kept_and_the_new_ones_added(tmp_path):
    root = planted(tmp_path)
    a0(root)
    rec = record(root)
    assert all(key in rec for key in OLD_KEYS)
    assert rec["tree"] == "clean" and rec["set_up"] == [".gitleaks.toml"]
    assert isinstance(rec["coordination"], str) and rec[KEY] in rec["coordination"]


def test_the_ctos_install_is_asked_and_every_other_session_is_refused(tmp_path):
    root = planted(tmp_path)
    a0(root)
    ident = record(root)[KEY]
    add_ticket(root, "oth-0001", wbs="P-77")
    assert cto_install(str(root), "orchestrator", None, ident) == (True, "")
    for role in OTHER_ROLES:
        assert refusal(root, role, ident)                    # even on the coordination ticket
        assert refusal(root, role, "oth-0001")
    assert refusal(root, "orchestrator", "oth-0001")         # an orchestrator on another ticket
    assert refusal(root, "orchestrator", None)               # a session with no ticket
    assert refusal(root, "", ident)                          # a session with no role


def test_a_second_a0_run_creates_no_second_ticket(tmp_path):
    root = planted(tmp_path)
    a0(root)
    first = tickets(root)
    a0(root)
    assert tickets(root) == first and sh(root, "status", "--short") == ""


# ---------------------------------------------------------------------------------------------------------------
# I2: the three defaults
# ---------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("value, wbs", [("own-0001", None), ("P-12", "P-12")])
def test_a_roster_naming_an_existing_ticket_is_kept_and_nothing_is_created(tmp_path, value, wbs):
    roster = f"# mine\n{KEY}: {value}\nroles: {{}}\n"
    root = planted(tmp_path, roster)
    add_ticket(root, "own-0001", wbs=wbs)
    before = tickets(root)
    a0(root)
    assert tickets(root) == before
    assert (root / ROSTER).read_text(encoding="utf-8") == roster
    rec = record(root)
    assert rec[KEY] == value and rec["roster"] == ROSTER and "kept" in rec["coordination"]
    assert sh(root, "status", "--short") == ""
    assert cto_install(str(root), "orchestrator", None, "own-0001") == (True, "")


def test_a_roster_naming_an_existing_ticket_needs_no_tk(tmp_path):
    root = planted(tmp_path, f"{KEY}: own-0001\n", tk=False)
    add_ticket(root, "own-0001")
    a0(root)
    assert tickets(root) == ["own-0001.md"] and record(root)[KEY] == "own-0001"


@pytest.mark.parametrize("roster", [
    "# The roster.\n\nroles:\n  orchestrator:\n    role_file: a.md   # kept\n\n\n  engineer:\n    role_file: b.md\n",
    "roles: {}",                                              # no final newline
    "# only a comment\n",
    "",
])
def test_a_roster_without_the_key_gets_the_key_and_changes_nothing_else(tmp_path, roster):
    root = planted(tmp_path, roster)
    a0(root)
    ident = record(root)[KEY]
    text = (root / ROSTER).read_text(encoding="utf-8")
    assert text.startswith(roster)                           # comments, blank lines and line order stand
    assert text[len(roster):].strip() == f"{KEY}: {ident}"
    assert roster_of(root) == {**(yaml.safe_load(roster) or {}), KEY: ident}
    assert tickets(root) == [f"{ident}.md"] and sh(root, "status", "--short") == ""
    assert cto_install(str(root), "orchestrator", None, ident) == (True, "")


def test_a_roster_that_cannot_take_a_key_line_is_left_as_it_is(tmp_path):
    root = planted(tmp_path, "{roles: {}}\n")                # a flow mapping: a line after it would not parse
    a0(root)
    assert (root / ROSTER).read_text(encoding="utf-8") == "{roles: {}}\n"
    assert tickets(root) == [] and record(root)[KEY] is None
    assert "no coordination ticket was created" in record(root)["coordination"]


def test_tk_missing_completes_without_a_ticket_or_a_key_and_the_record_says_so(tmp_path):
    root = planted(tmp_path, tk=False)
    result = a0(root)
    rec = record(root)
    assert result["stage"] == "A0" and all(key in rec for key in OLD_KEYS)
    assert not (root / ".tickets").exists() and not (root / ROSTER).exists()
    assert rec[KEY] is None and rec["roster"] is None
    words = rec["coordination"]
    assert "no coordination ticket was created" in words and "no key written" in words and "tk" in words
    assert sh(root, "status", "--short") == ""
    for role, ticket in (("orchestrator", "anything"), ("engineer", "anything")):
        reason = refusal(root, role, ticket)
        assert "GOV_TICKET" in reason and "Set the top-level key" in reason


def test_a_key_naming_no_ticket_is_left_as_it_is_and_the_record_says_so(tmp_path):
    roster = f"{KEY}: gone-0000\nroles: {{}}\n"
    root = planted(tmp_path, roster)
    a0(root)
    assert (root / ROSTER).read_text(encoding="utf-8") == roster and tickets(root) == []
    rec = record(root)
    assert rec[KEY] is None and "gone-0000" in rec["coordination"] and "no coordination ticket was created" in rec["coordination"]
    assert "GOV_TICKET" in refusal(root, "orchestrator", "gone-0000")


@pytest.mark.parametrize("roster", ["- a\n- b\n", "roles: [unclosed\n"])
def test_a_roster_that_is_not_a_readable_mapping_is_left_as_it_is(tmp_path, roster):
    root = planted(tmp_path, roster)
    a0(root)
    assert (root / ROSTER).read_text(encoding="utf-8") == roster and tickets(root) == []
    assert record(root)[KEY] is None


# ---------------------------------------------------------------------------------------------------------------
# S2: the refusal when the rule cannot run
# ---------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("roster", [None, "roles: {}\n", f"{KEY}: gone-0000\n", f"{KEY}:\n", f"{KEY}: ''\n"])
def test_the_refusal_names_gov_ticket_and_how_to_set_the_key_and_claims_no_key_was_set(tmp_path, roster):
    root = planted(tmp_path, roster, tk=False)
    for role, ticket in (("orchestrator", "c-0000"), ("engineer", "c-0000"), (None, None)):
        reason = refusal(root, role, ticket)
        assert "GOV_TICKET" in reason
        assert "Set the top-level key" in reason and ROSTER in reason and KEY in reason
        assert "set at adoption" not in reason.lower()
        assert install.ESCALATE in reason and reason.endswith(install.ESCALATE)
        assert "is not set" in reason                        # what is true: no key names a ticket


def test_the_refusal_is_the_same_decision_as_before_a_refusal_not_an_ask(tmp_path):
    root = planted(tmp_path, None, tk=False)
    assert cto_install(str(root), "orchestrator", None, "c-0000")[0] is False
