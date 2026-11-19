"""KPI 7: the digest of the decisions in force (S5), now ``gov decisions in-force --json`` (DEC-1214 M1, W2-200).

One line per entry in force, in the register's order, each beginning with its id, then its title; a changed entry
names what changed it; superseded and done entries left out, with their count; generated from the register at
``HEAD`` (the store's copy), never from a hand-made file. No register named: an empty digest; a named register that
cannot be read: a refusal. ``gov decisions`` with no action is refused by the parser.

Rewrite-Reason: DEC-1214 M1 (W2-200): the context command is retired and its ``--in-force`` digest moves to
``gov decisions in-force``; every case asks the new command, and what each asserts of the digest is unchanged.
"""

from __future__ import annotations

import pytest

import w2_55_support as s
from test_w2_55_left_out import LEFT_OUT, REGISTER_TEXT

IN_FORCE = [("DEC-102", "The beacon rule, restated"), ("DEC-104", "The beacon colour"),
            ("DEC-105", "The beacon height"), ("DEC-107", "The beacon keepers, pooled"), ("DEC-108", "The tide gauge")]
HAND_MADE = "governance/project/orchestration/DECISIONS-IN-FORCE.md"
HAND_MADE_TEXT = "# Decisions in force\n\n- DEC-999 — a line written by hand\n- DEC-101 — The first beacon rule\n"


IN_FORCE_ARGS = ("decisions", "in-force")   # DEC-1214 M1: the digest's command (W2-200 S2)


def digest(api, root):
    result = api.gov(root, *IN_FORCE_ARGS).result
    for key in ("lines", "left_out", "register"):
        assert key in result, f"the digest has no `{key}`: {sorted(result)}"
    assert isinstance(result["lines"], list) and all(isinstance(line, str) for line in result["lines"]), \
        f"the digest's lines are not a list of strings: {result['lines']!r}"
    return result


def leading_ids(lines):
    return [line.split()[0].rstrip(":—-·,") if line.split() else "" for line in lines]


@pytest.fixture(scope="module")
def harbour(api, tmp_path_factory):
    project = s.build_project(tmp_path_factory.mktemp("w2-55-in-force") / "repo", REGISTER_TEXT,
                              {HAND_MADE: HAND_MADE_TEXT})
    assert api.load(project.root) is None, "gov.store.load refused the planted harbour"
    return project


def test_one_line_per_entry_in_force_in_register_order_beginning_with_its_id(api, harbour):
    """One line per entry in force, in the register's order, each beginning with its id and carrying its title.

    Rewrite-Reason: DEC-1214 M1 (W2-200): asks ``gov decisions in-force``, where the digest moved with the context
    command's retirement; the assertions are unchanged."""
    result = digest(api, harbour.root)
    assert leading_ids(result["lines"]) == [entry_id for entry_id, _ in IN_FORCE], \
        f"the digest's lines are not the entries in force, in order:\n" + "\n".join(result["lines"])
    for line, (entry_id, title) in zip(result["lines"], IN_FORCE):
        assert title in line, f"the line of {entry_id} does not carry its title {title!r}: {line!r}"


def test_superseded_and_done_entries_are_left_out_with_their_count(api, harbour):
    """Superseded and done entries are left out, with their count; the digest names the register.

    Rewrite-Reason: DEC-1214 M1 (W2-200): asks ``gov decisions in-force``, where the digest moved with the context
    command's retirement; the assertions are unchanged."""
    result = digest(api, harbour.root)
    assert result["left_out"] == LEFT_OUT, f"left_out is {result['left_out']!r}, not {LEFT_OUT}"
    assert result["register"] == s.REGISTER, f"the digest names the register {result['register']!r}"


def test_a_changed_entrys_line_names_what_changed_it(api, harbour):
    """A changed entry's line names the entry that changed it.

    Rewrite-Reason: DEC-1214 M1 (W2-200): asks ``gov decisions in-force``, where the digest moved with the context
    command's retirement; the assertions are unchanged."""
    result = digest(api, harbour.root)
    line = next((line for line in result["lines"] if line.startswith("DEC-104")), None)
    assert line is not None and "DEC-105" in line, f"DEC-104's line does not name DEC-105, which changed it: {line!r}"


def test_the_digest_is_generated_from_the_register_not_a_hand_made_file(api, tmp_path):
    """The digest follows the register at HEAD, never a hand-made file.

    Rewrite-Reason: DEC-1214 M1 (W2-200): asks ``gov decisions in-force``, where the digest moved with the context
    command's retirement; the assertions are unchanged."""
    project = s.build_project(tmp_path / "repo", REGISTER_TEXT, {HAND_MADE: HAND_MADE_TEXT})
    assert api.load(project.root) is None
    before = digest(api, project.root)
    assert not any("DEC-999" in line for line in before["lines"]), "the digest holds a line of the hand-made file"
    changed = REGISTER_TEXT.replace(
        "### DEC-108 — The tide gauge\n- **Status:** ACCEPTED · **Basis:** OWNER",
        "### DEC-108 — The tide gauge\n- **Status:** SUPERSEDED by DEC-109 · **Basis:** OWNER")
    assert changed != REGISTER_TEXT, "the fixture is wrong: DEC-108's status line was not found"
    changed += "\n" + s.entry("DEC-109", "The tide gauge, read twice",
                              "ACCEPTED · **Basis:** OWNER · **Supersedes:** DEC-108",
                              s.tags("records", "kernel", s.KERNEL_PLACE), "The tide gauge is read at dawn and dusk.")
    project.write(s.REGISTER, changed)
    project.commit("DEC-109 supersedes DEC-108")
    assert api.load(project.root) is None
    after = digest(api, project.root)
    ids = leading_ids(after["lines"])
    assert "DEC-108" not in ids and ids[-1] == "DEC-109", \
        f"the digest did not follow the register's change:\n" + "\n".join(after["lines"])
    assert "DEC-108" in after["left_out"]["superseded"] and after["left_out"]["count"] == 4, after["left_out"]


def test_no_register_named_gives_an_empty_digest(api, tmp_path):
    """A project whose path map names no register gives an empty digest.

    Rewrite-Reason: DEC-1214 M1 (W2-200): asks ``gov decisions in-force``, where the digest moved with the context
    command's retirement; the assertions are unchanged."""
    project = s.build_project(tmp_path / "repo", REGISTER_TEXT, register_rel=None)
    assert api.load(project.root) is None
    result = api.gov(project.root, *IN_FORCE_ARGS).result
    assert result.get("lines") == [] and (result.get("left_out") or {}).get("count") == 0, \
        f"a project naming no register gave a digest that is not empty: {result!r}"


def test_a_named_register_that_cannot_be_read_refuses(api, tmp_path):
    """A named register HEAD does not hold is refused, never read as an empty digest.

    Rewrite-Reason: DEC-1214 M1 (W2-200): asks ``gov decisions in-force``, where the digest moved with the context
    command's retirement; the assertions are unchanged."""
    project = s.build_project(tmp_path / "repo", None, register_rel="docs/NO_SUCH_REGISTER.md")
    api.load(project.root)   # refuses too; the digest must not be built from nothing
    answer = api.gov(project.root, *IN_FORCE_ARGS)
    assert answer.returncode != 0 and answer.envelope["ok"] is False, \
        f"a named register HEAD does not hold gave a digest instead of a refusal\n{answer.describe()}"


def test_decisions_with_no_action_is_refused_by_the_parser(api, harbour):
    """Rewrite-Reason: DEC-1214 M1 (W2-200): was ``test_context_with_neither_a_ticket_nor_in_force_is_refused_by_the_
    parser``; the digest's command is now ``gov decisions in-force``, so the parser's refusal is asked of ``gov
    decisions`` with no action (exit 2), as it was of the retired command with neither a ticket nor the flag."""
    answer = api.gov(harbour.root, "decisions")
    assert answer.returncode == 2, f"`gov decisions` with no action was not refused\n{answer.describe()}"
