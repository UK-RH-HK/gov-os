"""W1-02 — ``MultiEdit`` is judged exactly like ``Edit``, by its file path, for every role (DEC-685).

DEC-685: "``MultiEdit`` is not a deliberate shape. It is an ordinary Claude
Code tool that writes files ... ``MultiEdit`` is judged exactly like ``Edit``,
by its file path, for every role."

Each case asks the guard twice, through the hook run as a process: the
``Edit`` of a file by an actor, and the ``MultiEdit`` of the same file by the
same actor. It holds that ``Edit`` gets the answer the case names (the case's
premise: the round changes nothing for ``Edit``) and that ``MultiEdit`` gets
the same answer.

Held: inside and outside the ticket's allowed paths; under the acceptance-test
folder (the independent test designer alone, a ticket that names the folder
included); the scratch set; the freeze; no path; a path longer than the guard
resolves; a held-out path as the target and in the text; a session with no
role and with an unknown role; a role subagent and a subagent that is no role.

**Red today**: the guard answers allow for ``MultiEdit`` wherever ``Edit`` is
refused, and it refuses a ``MultiEdit`` of one of the two files that hold the
held-out path where it lets the orchestrator's ``Edit`` through (DEC-215's
exception is for the file tools it knows). Green today: wherever ``Edit`` is
allowed otherwise, and where the held-out rule refuses whatever the tool.

No id and no failure message carries a held-out path.
"""

from __future__ import annotations

import os

import pytest

import w1_02_protected_support as protected
import w1_02_support as support
import w1_02_tools_support as tools

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
PRODUCT_SPEC = support.PRODUCT_SPEC
DESIGNER = support.TEST_DESIGNER
AUDITOR = support.AUDITOR
TICKET = support.TICKET_ID
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID

# The bound of this revision's time cases on one decision (README, fifth batch).
BOUND_S = 5.0


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    """One project with its stand-in files for the module: the cases only ask the guard for decisions."""
    return tools.make_world(tmp_path_factory.mktemp("multiedit"))


# --------------------------------------------------------------------------
# Every actor, inside and outside what it may write
# --------------------------------------------------------------------------

# target -> builder(world) -> path
TARGETS = {
    "a-source-file-the-engineer-s-ticket-names": lambda w: w.path(tools.SOURCE_REL),
    "a-file-no-ticket-names": lambda w: w.path(tools.OUTSIDE_REL),
    "an-acceptance-test": lambda w: w.path(tools.ACCEPTANCE_REL),
    "an-acceptance-test-through-a-link-in-the-ticket-s-folder": lambda w: w.path(tools.ACCEPTANCE_BY_LINK_REL),
    "a-file-of-the-scratch-folder": lambda w: w.path(tools.SCRATCH_REL),
    "a-file-outside-the-repository": lambda w: w.sandbox.elsewhere / "module.py",
}
SOURCE, OUTSIDE, ACCEPTANCE, BY_LINK, SCRATCH, ELSEWHERE = TARGETS

# actor -> the targets ``Edit`` is allowed on today (each actor on the ticket ``tools.ACTORS`` gives it).
EDIT_ALLOWED = {
    "no-role": (),
    "unknown-role": (),
    "orchestrator": (SOURCE, OUTSIDE, SCRATCH),
    "engineer": (SOURCE, SCRATCH),
    "product-spec": (SCRATCH,),
    "test-designer": (ACCEPTANCE, BY_LINK, SCRATCH),
    "auditor": (SCRATCH,),
    "research": (SCRATCH,),
    "ticket-lead": (SCRATCH,),
    "engineer-subagent-of-the-orchestrator": (SCRATCH,),     # on the orchestrator's ticket: no ticket paths
    "untyped-subagent-of-the-engineer": (),
}


def _expected(allowed):
    return "allow" if allowed else "deny"


@pytest.mark.parametrize("target", list(TARGETS))
@pytest.mark.parametrize("who", tools.EVERY_ACTOR)
def test_multiedit_gets_the_answer_edit_gets_for_every_actor(world, who, target):
    """Line 1: inside and outside the allowed paths, the acceptance tests, the scratch folder, by every role."""
    edit, multi = tools.ask_both(world, TARGETS[target](world), who)
    tools.assert_as_edit(edit, multi, _expected(target in EDIT_ALLOWED[who]), f"of {target} by {who}")


# name -> ((GOV_ROLE, GOV_TICKET, subagent type), repository-relative path, allowed for Edit today)
ON_OTHER_TICKETS = {
    "product-spec-on-its-own-ticket-inside-it": ((PRODUCT_SPEC, support.PRODUCT_SPEC_TICKET_ID, None),
                                                 tools.SPEC_REL, True),
    "product-spec-on-its-own-ticket-outside-it": ((PRODUCT_SPEC, support.PRODUCT_SPEC_TICKET_ID, None),
                                                  tools.SOURCE_REL, False),
    "engineer-on-the-docs-ticket-inside-it": ((ENGINEER, support.DOCS_TICKET_ID, None), "docs/notes.md", True),
    "engineer-on-the-docs-ticket-outside-it": ((ENGINEER, support.DOCS_TICKET_ID, None), tools.SOURCE_REL, False),
    "engineer-on-the-orchestrator-s-ticket": ((ENGINEER, ORCHESTRATOR_TICKET, None), tools.SOURCE_REL, False),
    "engineer-without-a-ticket": ((ENGINEER, None, None), tools.SOURCE_REL, False),
    "engineer-on-a-ticket-that-does-not-exist": ((ENGINEER, "DAEO-none", None), tools.SOURCE_REL, False),
    "orchestrator-without-a-ticket": ((ORCHESTRATOR, None, None), tools.OUTSIDE_REL, True),
    "engineer-on-the-installed-guard-s-file": ((ENGINEER, TICKET, None), support.installed_hook_rel, False),
    "engineer-on-the-freeze-flag": ((ENGINEER, TICKET, None), support.FREEZE_FLAG_REL, False),
    "orchestrator-on-the-freeze-flag": ((ORCHESTRATOR, ORCHESTRATOR_TICKET, None), support.FREEZE_FLAG_REL, False),
    "engineer-on-the-rest-of-the-runtime-folder": ((ENGINEER, TICKET, None), ".gov-runtime/other.txt", False),
    "engineer-on-a-path-that-leaves-the-ticket-s-folder-by-dot-dot":
        ((ENGINEER, TICKET, None), "src/gov/guard/../../../README.md", False),
}


@pytest.mark.parametrize("case", sorted(ON_OTHER_TICKETS))
def test_multiedit_follows_the_active_ticket_as_edit_does(world, case):
    """Line 1: the allow-list is the role's and the ticket's; no ticket, another role's ticket, the guard's own file."""
    actor, rel, allowed = ON_OTHER_TICKETS[case]
    rel = rel() if callable(rel) else rel
    edit, multi = tools.ask_both(world, world.path(rel), actor)
    tools.assert_as_edit(edit, multi, _expected(allowed), f"in the case '{case}'")


RELATIVE = {
    "a-relative-path-inside-the-ticket-s-paths": (tools.SOURCE_REL, True),
    "a-relative-path-outside-them": (tools.OUTSIDE_REL, False),
    "a-relative-path-to-an-acceptance-test": (tools.ACCEPTANCE_REL, False),
}


@pytest.mark.parametrize("form", sorted(RELATIVE))
def test_multiedit_with_a_relative_path_is_judged_as_edit_is(world, form):
    """Line 1: "by its file path": the path as the call gives it, from the session's folder."""
    rel, allowed = RELATIVE[form]
    edit, multi = tools.ask_both(world, rel, "engineer")
    tools.assert_as_edit(edit, multi, _expected(allowed), f"with {form} by the engineer")


# --------------------------------------------------------------------------
# The acceptance-test folder
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", sorted(tools.NAMING_TICKETS))
def test_a_ticket_that_names_the_acceptance_tests_gives_no_multiedit_there(world, role):
    """Line 1, MR-3: ``allowed_paths`` cannot hand the folder to a role that is not the test designer."""
    actor = (role, tools.NAMING_TICKETS[role], None)
    edit, multi = tools.ask_both(world, world.path(tools.UNIT_REL), actor)
    tools.assert_as_edit(edit, multi, "allow", f"of a unit test by {role}, on a ticket that names tests/**,")
    for rel in (tools.ACCEPTANCE_REL, f"tests/acceptance/{tools.WBS}/test_new.py", "tests/acceptance/conftest.py",
                tools.ACCEPTANCE_BY_LINK_REL):
        edit, multi = tools.ask_both(world, world.path(rel), actor)
        tools.assert_as_edit(edit, multi, "deny", f"of {rel} by {role}, on a ticket that names the folder,")


DESIGNER_TARGETS = {
    "an-existing-acceptance-test": (tools.ACCEPTANCE_REL, True),
    "a-new-acceptance-test-of-another-ticket": ("tests/acceptance/W1-91/test_new.py", True),
    "a-unit-test": (tools.UNIT_REL, False),
    "a-source-file": (tools.SOURCE_REL, False),
    "a-ticket-file": (f".tickets/{TICKET}.md", False),
}


@pytest.mark.parametrize("target", sorted(DESIGNER_TARGETS))
def test_the_test_designer_s_multiedit_is_allowed_under_the_acceptance_tests_only(world, target):
    """Line 1, CAP-38.c: the independent test designer alone, and nowhere else in the repository."""
    rel, allowed = DESIGNER_TARGETS[target]
    edit, multi = tools.ask_both(world, world.path(rel), "test-designer")
    tools.assert_as_edit(edit, multi, _expected(allowed), f"of {target} by the test designer")


# --------------------------------------------------------------------------
# The scratch set
# --------------------------------------------------------------------------

@pytest.mark.parametrize("who", ("engineer", "auditor", "no-role", "untyped-subagent-of-the-engineer"))
def test_multiedit_in_the_system_s_temporary_folder_is_judged_as_edit_is(world, who):
    """Line 1: the scratch set is the scratch folder and the temporary folder itself; closed without a role."""
    allowed = who in ("engineer", "auditor")
    edit, multi = tools.ask_both(world, world.sandbox.tmpdir / "note.txt", who)
    tools.assert_as_edit(edit, multi, _expected(allowed), f"of a file of the temporary folder by {who}")


# --------------------------------------------------------------------------
# No role, an unknown role
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.UNKNOWN_ROLES)
@pytest.mark.parametrize("target", (SOURCE, SCRATCH))
def test_an_unknown_role_s_multiedit_is_refused(world, target, role):
    """KPI success 4 [CAP-58.c]: read-only, whatever ticket it names; the scratch set included."""
    edit, multi = tools.ask_both(world, TARGETS[target](world), (role, TICKET, None))
    tools.assert_as_edit(edit, multi, "deny", f"of {target} by a session whose role is not one of the roles")


@pytest.mark.parametrize("ticket", (None, TICKET, ORCHESTRATOR_TICKET))
def test_a_session_with_no_role_gets_no_multiedit_from_any_ticket(world, ticket):
    """KPI success 4, failure 3: a ticket alone declares no role."""
    for rel in (tools.SOURCE_REL, tools.OUTSIDE_REL, tools.SCRATCH_REL):
        edit, multi = tools.ask_both(world, world.path(rel), (None, ticket, None))
        tools.assert_as_edit(edit, multi, "deny", f"of {rel} by a session with no role")


# --------------------------------------------------------------------------
# Inside a subagent
# --------------------------------------------------------------------------

# name -> ((GOV_ROLE, GOV_TICKET, subagent type), repository-relative path, allowed for Edit today)
SUBAGENTS = {
    # DEC-117: the role subagent's role governs.
    "engineer-subagent-in-an-orchestrator-session-source": ((ORCHESTRATOR, TICKET, ENGINEER), tools.SOURCE_REL, True),
    "engineer-subagent-in-a-designer-session-source": ((DESIGNER, TICKET, ENGINEER), tools.SOURCE_REL, True),
    "engineer-subagent-in-a-designer-session-acceptance-test":
        ((DESIGNER, TICKET, ENGINEER), tools.ACCEPTANCE_REL, False),
    "engineer-subagent-in-an-engineer-session-outside-the-ticket":
        ((ENGINEER, TICKET, ENGINEER), tools.OUTSIDE_REL, False),
    "designer-subagent-in-an-engineer-session-acceptance-test":
        ((ENGINEER, TICKET, DESIGNER), tools.ACCEPTANCE_REL, True),
    "designer-subagent-in-an-engineer-session-source": ((ENGINEER, TICKET, DESIGNER), tools.SOURCE_REL, False),
    "designer-subagent-in-an-orchestrator-session-acceptance-test":
        ((ORCHESTRATOR, TICKET, DESIGNER), tools.ACCEPTANCE_REL, True),
    "auditor-subagent-in-an-engineer-session-source": ((ENGINEER, TICKET, AUDITOR), tools.SOURCE_REL, False),
    "auditor-subagent-in-an-engineer-session-scratch": ((ENGINEER, TICKET, AUDITOR), tools.SCRATCH_REL, True),
    "orchestrator-subagent-in-an-engineer-session-on-the-engineer-s-ticket":
        ((ENGINEER, TICKET, ORCHESTRATOR), tools.SOURCE_REL, False),
    # DEC-113: a subagent that is not a role is read-only, the scratch set included.
    "general-purpose-subagent-in-an-engineer-session-source":
        ((ENGINEER, TICKET, "general-purpose"), tools.SOURCE_REL, False),
    "general-purpose-subagent-in-an-engineer-session-scratch":
        ((ENGINEER, TICKET, "general-purpose"), tools.SCRATCH_REL, False),
    "Explore-subagent-in-an-orchestrator-session": ((ORCHESTRATOR, ORCHESTRATOR_TICKET, "Explore"),
                                                    tools.OUTSIDE_REL, False),
    "a-subagent-named-like-a-role-in-an-engineer-session": ((ENGINEER, TICKET, "Engineer"), tools.SOURCE_REL, False),
    "general-purpose-subagent-in-a-designer-session-acceptance-test":
        ((DESIGNER, TICKET, "general-purpose"), tools.ACCEPTANCE_REL, False),
    # DEC-125: a role subagent's role applies only in a session with a declared role.
    "engineer-subagent-in-a-session-with-no-role": ((None, TICKET, ENGINEER), tools.SOURCE_REL, False),
    "engineer-subagent-in-a-session-with-an-unknown-role": (("developer", TICKET, ENGINEER), tools.SOURCE_REL, False),
}


@pytest.mark.parametrize("case", sorted(SUBAGENTS))
def test_multiedit_inside_a_subagent_is_judged_as_edit_is(world, case):
    """Line 1: a role subagent's role governs (DEC-117, DEC-125); a subagent that is not a role is read-only."""
    actor, rel, allowed = SUBAGENTS[case]
    edit, multi = tools.ask_both(world, world.path(rel), actor)
    tools.assert_as_edit(edit, multi, _expected(allowed), f"in the case '{case}'")


# --------------------------------------------------------------------------
# The freeze
# --------------------------------------------------------------------------

# role -> (ticket, a write the role may make when nothing is frozen)
NORMAL_WRITE = {
    ENGINEER: (TICKET, tools.SOURCE_REL),
    ORCHESTRATOR: (ORCHESTRATOR_TICKET, tools.OUTSIDE_REL),
    PRODUCT_SPEC: (support.PRODUCT_SPEC_TICKET_ID, tools.SPEC_REL),
    DESIGNER: (TICKET, tools.ACCEPTANCE_REL),
    AUDITOR: (TICKET, tools.SCRATCH_REL),
}


def _both(call, project, path, role, ticket):
    edit = call(project, "Edit", tools.edit_input(path), role=role, ticket=ticket)
    multi = call(project, "MultiEdit", tools.multiedit_input(path), role=role, ticket=ticket)
    return edit, multi


@pytest.mark.parametrize("role", sorted(NORMAL_WRITE))
def test_the_freeze_refuses_the_multiedit_each_role_could_otherwise_make(project, call, role):
    """KPI success 3a: the flag denies every write; ``MultiEdit`` is refused as ``Edit`` is, and allowed again after."""
    ticket, rel = NORMAL_WRITE[role]
    edit, multi = _both(call, project, project / rel, role, ticket)
    tools.assert_as_edit(edit, multi, "allow", f"of {rel} by {role} before the freeze")

    flag = support.set_freeze(project)
    edit, multi = _both(call, project, project / rel, role, ticket)
    tools.assert_as_edit(edit, multi, "deny", f"of {rel} by {role} while frozen")

    flag.unlink()
    edit, multi = _both(call, project, project / rel, role, ticket)
    tools.assert_as_edit(edit, multi, "allow", f"of {rel} by {role} after the flag was removed")


def test_the_freeze_closes_the_scratch_set_to_multiedit(project, call, sandbox):
    support.set_freeze(project)
    for path in (project / tools.SCRATCH_REL, sandbox.tmpdir / "note.txt"):
        edit, multi = _both(call, project, path, ENGINEER, TICKET)
        tools.assert_as_edit(edit, multi, "deny", "of a scratch file by the engineer while frozen")


def test_no_multiedit_lifts_the_freeze(project, call):
    """The flag is outside every allow-list, frozen or not."""
    support.set_freeze(project)
    for role in sorted(NORMAL_WRITE):
        edit, multi = _both(call, project, project / support.FREEZE_FLAG_REL, role, NORMAL_WRITE[role][0])
        tools.assert_as_edit(edit, multi, "deny", f"of the freeze flag by {role} while frozen")


# --------------------------------------------------------------------------
# No path, and a path longer than the guard resolves
# --------------------------------------------------------------------------

# form -> (leave the path out or keep the key, the value kept)
NO_PATH = {
    "no-file-path-at-all": (False, None),
    "an-empty-file-path": (True, ""),
    "a-file-path-that-is-null": (True, None),
    "a-file-path-that-is-a-list": (True, ["src/gov/guard/decide.py"]),
    "a-file-path-that-is-a-number": (True, 5),
}


@pytest.mark.parametrize("who", ("orchestrator", "engineer"))
@pytest.mark.parametrize("form", sorted(NO_PATH))
def test_multiedit_with_no_usable_path_is_refused(world, form, who):
    """Line 1: "with no path (refused)"; a refusal by a rule or the guard's report of its own failure, as for Edit."""
    keep, value = NO_PATH[form]
    source = world.path(tools.SOURCE_REL)
    edit = tools.ask(world, "Edit", tools.without_path(tools.edit_input(source), value, keep), who)
    multi = tools.ask(world, "MultiEdit", tools.without_path(tools.multiedit_input(source), value, keep), who)
    tools.assert_as_edit(edit, multi, "deny", f"with {form} by {who}")


def test_a_path_inside_an_edit_of_the_list_is_no_file_path(world):
    """Line 1: "by its ``file_path``": a path given only inside the list of edits names no file to judge."""
    source = str(world.path(tools.SOURCE_REL))
    multi = tools.ask(world, "MultiEdit", {"edits": [
        {"file_path": source, "old_string": "VALUE = 1", "new_string": "VALUE = 2"}]}, "engineer")
    support.assert_denied(multi, "MultiEdit with no file path of its own and a path inside one of its edits")


LONG = {"just-over-the-system-path-limit": os.pathconf("/", "PC_PATH_MAX") + 1, "a-megabyte": 1024 * 1024}


@pytest.mark.parametrize("who", ("orchestrator", "engineer"))
@pytest.mark.parametrize("size", sorted(LONG))
def test_multiedit_with_a_path_longer_than_the_guard_resolves_is_refused(world, size, who):
    """Line 1, DEC-562: a file tool's path past the bound is refused to every role, in time."""
    start = str(world.path("src/gov/guard")) + "/"
    path = start + "a/" * ((LONG[size] - len(start) - len("module.py")) // 2 + 1) + "module.py"
    assert len(path) > LONG[size] - 2, "the fixture path is shorter than asked for"
    edit, multi = tools.ask_both(world, path, who)
    tools.assert_as_edit(edit, multi, "deny", f"with a path {size} by {who}")
    assert multi.seconds <= BOUND_S, f"MultiEdit with a path {size} was answered after {multi.seconds:.1f} s"


# --------------------------------------------------------------------------
# The held-out rule
# --------------------------------------------------------------------------

# form -> builder(world) -> the file path of the call: each reaches the stand-in held-out folder
HELD_OUT_TARGETS = {
    "a-file-of-the-held-out-folder": lambda w: w.listed / tools.FILE_NAME,
    "a-new-file-of-the-held-out-folder": lambda w: w.listed / "new.md",
    "a-file-of-it-through-a-symbolic-link": lambda w: w.link / tools.FILE_NAME,
    "a-file-of-it-by-a-relative-path": lambda w: f"{w.relative}/{tools.FILE_NAME}",
}


@pytest.mark.parametrize("who", tools.SOME)
@pytest.mark.parametrize("form", sorted(HELD_OUT_TARGETS))
def test_multiedit_on_a_path_the_held_out_rule_refuses_is_refused(world, form, who):
    """Line 1: refused for every role, and the refusal discloses nothing of the path."""
    edit, multi = tools.ask_both(world, HELD_OUT_TARGETS[form](world), who)
    tools.assert_as_edit(edit, multi, "deny", f"of {form} by {who}")
    tools.assert_carries_none_of(multi, (str(world.listed), protected.HELD_REL), f"MultiEdit of {form} by {who}")


# form -> builder(world) -> (old string, new string) of an edit of a source file
HELD_OUT_TEXT = {
    "the-held-out-path-in-a-new-string": lambda w: ("VALUE = 2", f"ANSWERS = '{w.listed}/{tools.FILE_NAME}'"),
    "the-held-out-path-in-an-old-string": lambda w: (f"{w.listed}", "VALUE = 3"),
}


@pytest.mark.parametrize("who", tools.SOME)
@pytest.mark.parametrize("form", sorted(HELD_OUT_TEXT))
def test_multiedit_that_carries_a_held_out_path_in_its_text_is_refused(world, form, who):
    """Line 1: the path in the text of an edit of another file, the last of several edits included."""
    edit, multi = tools.ask_both(world, world.path(tools.SOURCE_REL), who, HELD_OUT_TEXT[form](world))
    tools.assert_as_edit(edit, multi, "deny", f"of a source file with {form} by {who}")
    tools.assert_carries_none_of(multi, world.secrets(), f"MultiEdit of a source file with {form} by {who}")


HOLDERS = sorted(protected.PROTECTED)
# who -> whether the role's rules allow an Edit of either file that holds the held-out path
HOLDER_WRITERS = {"orchestrator": True, "engineer": False, "no-role": False}


@pytest.mark.parametrize("who", sorted(HOLDER_WRITERS))
@pytest.mark.parametrize("holder", HOLDERS)
def test_multiedit_of_a_file_that_holds_the_held_out_path_is_decided_as_edit_is(world, holder, who):
    """Line 1, DEC-215's exception: an edit of the two files that hold the path is not refused for carrying it.

    The orchestrator, whose role rules allow the edit, can make it with either
    tool; every other actor is refused by its own rules, with either tool. Red
    today for the orchestrator (``MultiEdit`` is refused for carrying the path)
    and for the others (``MultiEdit`` is allowed).
    """
    text = (f"- {world.listed}", "- /another/stand-in/folder")
    edit, multi = tools.ask_both(world, world.guarded.path(holder), who, text)
    tools.assert_as_edit(edit, multi, _expected(HOLDER_WRITERS[who]),
                         f"of the stand-in {holder}, carrying the stand-in held-out path, by {who}")


@pytest.mark.parametrize("who", sorted(HOLDER_WRITERS))
@pytest.mark.parametrize("holder", HOLDERS)
def test_a_plain_multiedit_of_a_file_that_holds_the_held_out_path_is_decided_as_edit_is(world, holder, who):
    """Line 1: who may write the two protected files does not change with the tool."""
    edit, multi = tools.ask_both(world, world.guarded.path(holder), who)
    tools.assert_as_edit(edit, multi, _expected(HOLDER_WRITERS[who]), f"of the stand-in {holder} by {who}")


# --------------------------------------------------------------------------
# Nothing on disk changes by a decision
# --------------------------------------------------------------------------

def test_decisions_on_multiedit_change_nothing_on_disk(project, call):
    """The guard decides; it edits nothing, allowed or refused."""
    before = tools.tree_state(project)
    assert before[0] == "", "the fixture project must start clean"
    attempts = [
        (ENGINEER, TICKET, tools.SOURCE_REL), (ENGINEER, TICKET, tools.OUTSIDE_REL),
        (ENGINEER, TICKET, tools.ACCEPTANCE_REL), (DESIGNER, TICKET, tools.ACCEPTANCE_REL),
        (ORCHESTRATOR, ORCHESTRATOR_TICKET, tools.OUTSIDE_REL), (None, None, tools.SOURCE_REL),
    ]
    for role, ticket, rel in attempts:
        result = call(project, "MultiEdit", tools.multiedit_input(project / rel), role=role, ticket=ticket)
        assert result.decision in ("allow", "deny"), f"the guard gave no decision on a MultiEdit of {rel}"
    tools.assert_tree_unchanged(project, before, "the guard's decisions on MultiEdit")
