"""KPI S9, the owner's answers to packages P-1 and P-2 (DEC-473, DEC-474).

DEC-473: "A decision is recorded either as a decision file, or as an entry of a
register file that the project names in one line of configuration under
``governance/project/``. With no register file named, decision files alone
count. No path of this repository goes into the kernel." Heading grammar: "a
level-3 heading ``### DEC-<digits>`` at the start of a line, followed by a
space, a colon or a dash and the title. A heading inside a fenced code block
does not count."

DEC-474: "A base commit is recorded in the project's configuration: the commits
after it are judged. With no base recorded, the whole history is judged."

What the cases fix (the README's section "The register file and the base
commit" gives the source of each point):

- The configuration is ``governance/project/path-map.yaml``, the file that
  holds the project's other configuration for checks (its ``policies``). The
  two entries are top-level keys: ``decision_register`` (a path from the
  project's root) and ``decision_citations_base`` (a commit id, full or
  abbreviated). Both are optional.
- The register file is read as it is in the tree of the citing commit; which
  file is the register is read from the project's present configuration.
- The commits judged are those reachable from ``HEAD`` and not from the base.
- A named register that is absent or cannot be read at a citing commit: exit 1
  and the register's path in the output. A base that is not a commit of the
  repository or not an ancestor of ``HEAD``, and a base with no commit after
  it: the unmeasured answer.

The interface (the declared command, its JSON, its findings and exit codes) is
that of ``test_w1_26_decision_citations.py``; its helpers are used here.

Every case is red until the check knows the two entries. A case whose expected
findings a check that knows neither entry would give as well either holds a
decision recorded by a well-formed heading and cited (the control, ``DEC-200``),
or stops at a fixture that shows the entry is known.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_26_support as support  # noqa: E402
import test_w1_26_decision_citations as citations  # noqa: E402
from test_w1_26_decision_citations import declaration, history  # noqa: E402,F401  (fixtures)

REPO_ROOT = support.REPO_ROOT
PATH_MAP_REL = support.PATH_MAP_REL
PATH_MAP_SCHEMA = REPO_ROOT / "template" / "governance" / "kernel" / "schemas" / "path-map.schema.json"

REGISTER_KEY = "decision_register"
BASE_KEY = "decision_citations_base"

# The register of these projects. No file of this repository has this path.
REGISTER = "records/decision-log.md"
# A file with the form of a register that no configuration names.
NOT_NAMED = "docs/DECISION_REGISTER.md"

OWNER = citations.OWNER
WITNESS = citations.WITNESS       # DEC-900: recorded nowhere
SUBJECT = "DEC-101"               # the id whose record the case is about
CONTROL = "DEC-200"               # recorded by a well-formed heading wherever a register is named
BEFORE = "DEC-801"                # cited at or before the base, recorded nowhere
CONTROL_HEADING = f"### {CONTROL} — A recorded decision"

EXIT_CLEAN, EXIT_NOT_CLEAN = citations.EXIT_CLEAN, citations.EXIT_NOT_CLEAN

run_declared = citations.run_declared
assert_flagged = citations.assert_flagged
assert_unmeasured = citations.assert_unmeasured


# --------------------------------------------------------------------------
# The project's configuration and its register file
# --------------------------------------------------------------------------

def path_map(**entries):
    """A path map that is valid under the kernel's schema (its required systems are read from the
    schema), with ``entries`` as further top-level keys."""
    schema = json.loads(PATH_MAP_SCHEMA.read_text(encoding="utf-8"))
    document = {
        "state_class": "AUTHORITATIVE",
        "namespaces": {"all": {
            "paths": ["**"], "memory_class": "governance", "sensitivity": "internal",
            "permitted_roles": ["engineer"], "retention": "permanent", "export_policy": "allowed",
            "embedding_policy": "not embedded", "provenance": "fixture", "deletion_rebuild": "from git"}},
        "capabilities": {"code_intelligence": {"enabled": False}, "research_corpus": {"enabled": False}},
        "policies": dict(support.POLICIES),
        "systems": {name: {"status": "absent", "reason": "a fixture"}
                    for name in schema["properties"]["systems"]["required"]},
    }
    document.update(entries)
    return yaml.safe_dump(document, sort_keys=False)


def register(*headings):
    """A register file: one entry under each heading line, as it is given."""
    parts = ["# Decisions\n"]
    for heading in headings:
        parts.append(f"{heading}\n- **Status:** ACCEPTED\n- **Decision:** A fixture.\n")
    return "\n".join(parts)


def into_the_first_commit(history):
    """Put the working tree into the project's first commit, so every commit of the history holds it."""
    history.git("add", "-A")
    history.git("commit", "--amend", "-q", "--no-edit", "--no-gpg-sign")


def name_register(history, text, path=REGISTER):
    """The project names ``path`` as its register, and holds it with ``text`` from its first commit on.
    ``text`` None: the register is named and the file is not written."""
    history.write(PATH_MAP_REL, path_map(**{REGISTER_KEY: path}))
    if text is not None:
        history.write(path, text)
    into_the_first_commit(history)


def record_base(history, base):
    """The owner records ``base`` in the project's configuration, in a commit that cites nothing."""
    history.write(PATH_MAP_REL, path_map(**{BASE_KEY: base}))
    return history.commit("Record the base commit of the citations check", who=OWNER)


def judged_with(declaration, history, text, flagged_ids):
    """Name a register with ``text``, cite the subject, the control and the witness in one commit,
    and expect exactly ``flagged_ids`` of that commit to be flagged."""
    name_register(history, text)
    commit = history.commit(f"Change the parser ({SUBJECT}, {CONTROL}, {WITNESS})")
    assert_flagged(run_declared(declaration, history.root), [(commit, an_id) for an_id in flagged_ids])


@pytest.fixture(scope="session")
def register_is_read(declaration, tmp_path_factory):
    """The check reads a register file the project names. Until it does, a case that expects a file
    not to be read would pass for the wrong reason, and fails here instead."""
    past = citations.History(tmp_path_factory.mktemp("w1-26-register-known") / "project")
    name_register(past, register(f"### {SUBJECT} — A decision"))
    past.commit(f"Change the parser ({SUBJECT})")
    answer = run_declared(declaration, past.root)
    if answer.returncode != EXIT_CLEAN or answer.flagged:
        pytest.fail(f"the check does not read the register file that {PATH_MAP_REL} names under "
                    f"{REGISTER_KEY!r} (DEC-473): a decision recorded by a heading of it is flagged",
                    pytrace=False)
    return True


@pytest.fixture(scope="session")
def base_is_honoured(declaration, tmp_path_factory):
    """The check honours a recorded base commit. Until it does, a case that expects the whole history
    to be judged would pass for the wrong reason, and fails here instead."""
    past = citations.History(tmp_path_factory.mktemp("w1-26-base-known") / "project")
    past.commit(f"Change the parser ({BEFORE})")
    record_base(past, past.commit("The base"))
    answer = run_declared(declaration, past.root)
    if answer.returncode != EXIT_CLEAN or answer.flagged:
        pytest.fail(f"the check does not honour the base commit that {PATH_MAP_REL} records under "
                    f"{BASE_KEY!r} (DEC-474): a commit before the base is flagged", pytrace=False)
    return True


# ==========================================================================
# The register file (DEC-473): the heading grammar
# ==========================================================================

SEPARATORS = {
    "space": f"### {SUBJECT} The parser changes",
    "colon": f"### {SUBJECT}: The parser changes",
    "dash": f"### {SUBJECT} — The parser changes",
}


@pytest.mark.parametrize("separator", sorted(SEPARATORS))
def test_a_register_heading_records_its_id(declaration, history, separator):
    """A level-3 heading at the start of a line, the id, then a space, a colon or a dash and the title:
    the decision is recorded. The dash is written as the owner's own headings write it."""
    judged_with(declaration, history, register(CONTROL_HEADING, SEPARATORS[separator]), [WITNESS])


@pytest.mark.parametrize("marks", ["#", "##", "####"])
def test_a_heading_of_another_level_records_nothing(declaration, history, marks):
    """Only a level-3 heading is an entry of the register."""
    text = register(CONTROL_HEADING, f"{marks} {SUBJECT} — The parser changes")
    judged_with(declaration, history, text, [SUBJECT, WITNESS])


NOT_AT_THE_START = {
    "indented": f" ### {SUBJECT} — The parser changes",
    "after-other-text": f"Decided as ### {SUBJECT} — The parser changes",
}


@pytest.mark.parametrize("form", sorted(NOT_AT_THE_START))
def test_a_heading_not_at_the_start_of_a_line_records_nothing(declaration, history, form):
    """The heading's marks open the line: one space before them, or text before them, and it is no entry."""
    judged_with(declaration, history, register(CONTROL_HEADING, NOT_AT_THE_START[form]), [SUBJECT, WITNESS])


def test_a_heading_with_nothing_after_the_id_records_nothing(declaration, history):
    """The grammar asks for a separator and the title after the id: the id alone is no entry."""
    judged_with(declaration, history, register(CONTROL_HEADING, f"### {SUBJECT}"), [SUBJECT, WITNESS])


def test_a_heading_of_a_longer_id_does_not_record_the_shorter_one(declaration, history):
    """``DEC-<digits>`` and then the separator: the heading of DEC-1010 does not record DEC-101."""
    text = register(CONTROL_HEADING, f"### {SUBJECT}0 — Another decision")
    judged_with(declaration, history, text, [SUBJECT, WITNESS])


def test_a_heading_inside_a_fenced_code_block_records_nothing(declaration, history):
    """A heading line shown as an example inside a fence is not an entry."""
    text = register(CONTROL_HEADING) + (
        f"\nHow an entry is written:\n\n```\n### {SUBJECT} — The parser changes\n```\n")
    judged_with(declaration, history, text, [SUBJECT, WITNESS])


def test_a_heading_after_a_closed_fence_records_its_id(declaration, history):
    """The fence ends where it is closed: a heading after it is an entry again."""
    text = register(CONTROL_HEADING) + (
        "\nHow an entry is written:\n\n```\n### DEC-nnn — The title\n```\n\n"
        f"### {SUBJECT} — The parser changes\n- **Decision:** A fixture.\n")
    judged_with(declaration, history, text, [WITNESS])


# ==========================================================================
# The register file (DEC-473): both forms, and the file the project names
# ==========================================================================

def test_a_decision_file_records_its_id_beside_a_named_register(declaration, history):
    """Both forms: with a register named, a decision recorded only as a decision file is recorded."""
    name_register(history, register(CONTROL_HEADING))
    history.owner_records(SUBJECT)
    commit = history.commit(f"Change the parser ({SUBJECT}, {CONTROL}, {WITNESS})")
    assert_flagged(run_declared(declaration, history.root), [(commit, WITNESS)])


@pytest.mark.parametrize("configuration", ["no-configuration-file", "configuration-without-the-entry"])
def test_without_a_register_named_a_register_like_file_is_not_read(declaration, register_is_read, history,
                                                                   configuration):
    """No register named: decision files alone count. A file of headed entries in the project, whatever
    its path, records nothing."""
    if configuration == "configuration-without-the-entry":
        history.write(PATH_MAP_REL, path_map())
    history.write(NOT_NAMED, register(f"### {SUBJECT} — The parser changes"))
    into_the_first_commit(history)
    commit = history.commit(f"Change the parser ({SUBJECT})")
    assert_flagged(run_declared(declaration, history.root), [(commit, SUBJECT)])


def test_only_the_file_the_project_names_is_the_register(declaration, history):
    """The register's path comes from the project's configuration alone: a second file of headed
    entries, which the configuration does not name, records nothing."""
    history.write(NOT_NAMED, register(f"### {SUBJECT} — The parser changes"))
    name_register(history, register(CONTROL_HEADING))
    commit = history.commit(f"Change the parser ({SUBJECT}, {CONTROL})")
    assert_flagged(run_declared(declaration, history.root), [(commit, SUBJECT)])


def test_a_register_named_later_serves_the_commits_made_before_it_was_named(declaration, history):
    """Which file is the register is read from the project's present configuration: a commit that
    cited an entry of the file before the configuration named it is not flagged."""
    history.write(REGISTER, register(f"### {SUBJECT} — The parser changes"))
    into_the_first_commit(history)
    history.commit(f"Change the parser ({SUBJECT})")
    history.write(PATH_MAP_REL, path_map(**{REGISTER_KEY: REGISTER}))
    history.commit("Name the register of this project", who=OWNER)
    witness = history.commit(f"Another change ({WITNESS})")
    assert_flagged(run_declared(declaration, history.root), [(witness, WITNESS)])


# ==========================================================================
# The register file (DEC-473): "at that commit"
# ==========================================================================

def test_an_entry_added_by_a_later_commit_does_not_record_for_the_earlier_one(declaration, history):
    """Recorded late in the register: the citing commit stays flagged although HEAD's register holds
    the entry."""
    name_register(history, register(CONTROL_HEADING))
    early = history.commit(f"Change the parser ({SUBJECT}, {CONTROL})")
    history.write(REGISTER, register(CONTROL_HEADING, f"### {SUBJECT} — The parser changes"))
    history.commit("Add an entry to the register", who=OWNER)
    assert_flagged(run_declared(declaration, history.root), [(early, SUBJECT)])


def test_an_entry_and_its_citation_in_one_commit_are_not_flagged(declaration, history):
    """The commit that adds the entry holds it in its own tree."""
    name_register(history, register(CONTROL_HEADING))
    history.write(REGISTER, register(CONTROL_HEADING, f"### {SUBJECT} — The parser changes"))
    history.commit(f"Record {SUBJECT} and change the parser under it", who=OWNER)
    witness = history.commit(f"Another change ({WITNESS})")
    assert_flagged(run_declared(declaration, history.root), [(witness, WITNESS)])


def test_an_entry_removed_later_does_not_flag_the_commit_that_cited_it(declaration, history):
    """Present in the register of the citing commit, gone from HEAD's: judged by its own tree."""
    name_register(history, register(CONTROL_HEADING, f"### {SUBJECT} — The parser changes"))
    history.commit(f"Change the parser ({SUBJECT})")
    history.write(REGISTER, register(CONTROL_HEADING))
    history.commit("Remove an entry from the register", who=OWNER)
    witness = history.commit(f"Another change ({WITNESS})")
    assert_flagged(run_declared(declaration, history.root), [(witness, WITNESS)])


# ==========================================================================
# The register file (DEC-473): named, and absent or unreadable at a citing commit
# ==========================================================================

@pytest.mark.parametrize("state", ["absent-at-the-citing-commit", "a-directory", "not-text"])
def test_a_named_register_that_cannot_be_read_is_never_clean(declaration, history, state):
    """The citing commit's tree does not hold the named register as a file that can be read. The
    decision it cites is recorded as a decision file, so a check that passed over the register would
    call this history clean. Not clean, and the register is named in the output."""
    if state == "a-directory":
        history.write(f"{REGISTER}/part-1.md", register(CONTROL_HEADING))
    elif state == "not-text":
        (history.root / REGISTER).parent.mkdir(parents=True, exist_ok=True)
        (history.root / REGISTER).write_bytes(register(CONTROL_HEADING).encode("utf-8") + b"\xff\xfe\xfa\x00\xc3\n")
    name_register(history, None)
    history.owner_records(SUBJECT)
    if state == "absent-at-the-citing-commit":
        history.write(REGISTER, register(CONTROL_HEADING))
        history.commit("Start the register", who=OWNER)
    answer = run_declared(declaration, history.root)
    assert answer.returncode == EXIT_NOT_CLEAN and REGISTER in answer.stdout, (
        f"expected exit {EXIT_NOT_CLEAN} and the register {REGISTER} named in the output\n{answer.describe()}")


# ==========================================================================
# The base commit (DEC-474)
# ==========================================================================

@pytest.mark.parametrize("written", ["full-id", "first-eight-characters"])
def test_a_commit_before_the_base_is_not_judged(declaration, history, written):
    """A commit made before the base cites an unrecorded decision: not flagged. The base is written
    as its full id, or abbreviated as DEC-474 writes this repository's."""
    history.commit(f"Change the parser ({BEFORE})")
    base = history.commit("The base")
    after = history.commit(f"Another change ({WITNESS})")
    record_base(history, base if written == "full-id" else base[:8])
    assert_flagged(run_declared(declaration, history.root), [(after, WITNESS)])


def test_the_base_commit_itself_is_not_judged(declaration, history):
    """The commits after the base are judged: the base is not one of them."""
    base = history.commit(f"Change the parser ({BEFORE})")
    after = history.commit(f"Another change ({WITNESS})")
    record_base(history, base)
    assert_flagged(run_declared(declaration, history.root), [(after, WITNESS)])


def test_every_commit_after_the_base_is_judged(declaration, history):
    """Each commit after the base, not the first or the last alone."""
    history.commit(f"Change the parser ({BEFORE})")
    base = history.commit("The base")
    first = history.commit(f"Start the work ({WITNESS})")
    history.commit("A commit that cites nothing")
    third = history.commit("Finish the work (DEC-901)")
    record_base(history, base)
    assert_flagged(run_declared(declaration, history.root), [(first, WITNESS), (third, "DEC-901")])


def test_a_branch_that_left_before_the_base_and_is_merged_after_it_is_judged(declaration, history):
    """The commits judged are those reachable from HEAD and not from the base (package P-2, option
    (a)): a side commit made before the base and merged after it is not behind the base."""
    history.git("checkout", "-q", "-b", "side")
    history.write("src/side.txt", "side work\n")
    side = history.commit("Side work (DEC-802)")
    history.git("checkout", "-q", "main")
    history.commit(f"Change the parser ({BEFORE})")
    base = history.commit("The base")
    history.git("merge", "-q", "--no-ff", "--no-gpg-sign", "-m", "Merge side into main", "side")
    record_base(history, base)
    assert_flagged(run_declared(declaration, history.root), [(side, "DEC-802")])


def test_without_a_base_recorded_the_whole_history_is_judged(declaration, base_is_honoured, history):
    """A configuration that records no base: the first citing commit is judged like the last."""
    first = history.commit(f"Change the parser ({BEFORE})")
    history.write(PATH_MAP_REL, path_map())
    history.commit("Write the path map", who=OWNER)
    last = history.commit(f"Another change ({WITNESS})")
    assert_flagged(run_declared(declaration, history.root), [(first, BEFORE), (last, WITNESS)])


def test_a_register_and_a_base_hold_together(declaration, history):
    """Both entries in one configuration: before the base nothing is judged, after it the register's
    entries are recorded decisions."""
    history.write(REGISTER, register(CONTROL_HEADING))
    into_the_first_commit(history)
    history.commit(f"Change the parser ({BEFORE})")
    base = history.commit("The base")
    after = history.commit(f"Another change ({CONTROL}, {WITNESS})")
    history.write(PATH_MAP_REL, path_map(**{REGISTER_KEY: REGISTER, BASE_KEY: base}))
    history.commit("Record the register and the base", who=OWNER)
    assert_flagged(run_declared(declaration, history.root), [(after, WITNESS)])


# ==========================================================================
# The base commit (DEC-474): a base that gives nothing to judge
# ==========================================================================

def _clean_history(history):
    history.owner_records(SUBJECT)
    return history.commit(f"Change the parser ({SUBJECT})")


def test_a_base_that_is_not_a_commit_of_the_repository_is_unmeasured(declaration, history):
    """The recorded id names no commit here: nothing can be said to lie after it. The history itself
    is clean, so a check that judged all of it, or none of it, would exit 0."""
    _clean_history(history)
    record_base(history, "0123456789abcdef0123456789abcdef01234567")
    assert_unmeasured(run_declared(declaration, history.root))


def test_a_base_that_is_not_an_ancestor_of_head_is_unmeasured(declaration, history):
    """The recorded base is a commit of a branch that HEAD does not hold."""
    history.git("checkout", "-q", "-b", "aside")
    history.write("src/aside.txt", "work that is not merged\n")
    aside = history.commit("Work that is not merged")
    history.git("checkout", "-q", "main")
    _clean_history(history)
    record_base(history, aside)
    assert_unmeasured(run_declared(declaration, history.root))


def test_no_commit_after_the_base_is_unmeasured(declaration, history):
    """The base is HEAD: no commit is judged, and "no commit to judge is not a clean history" (this
    suite's answer for a repository without a commit). A commit cannot hold its own id, so the base is
    HEAD only while the configuration that records it is not committed."""
    head = _clean_history(history)
    history.write(PATH_MAP_REL, path_map(**{BASE_KEY: head}))
    assert_unmeasured(run_declared(declaration, history.root))


# ==========================================================================
# Through ``gov check``
# ==========================================================================

def _status(history, sandbox, interface):
    entry, _, run = citations._entry(history, sandbox, interface)
    return entry.get("status"), run


def test_gov_check_shows_a_citation_of_a_register_entry_as_green(built, history, sandbox, interface):
    """A decision recorded as an entry of the named register and cited afterwards: GREEN."""
    name_register(history, register(f"### {SUBJECT} — The parser changes"))
    history.commit(f"Change the parser ({SUBJECT})")
    status, run = _status(history, sandbox, interface)
    assert status == support.GREEN, f"the check is {status!r}, expected GREEN\n{run.describe()}"


def test_gov_check_never_shows_an_absent_named_register_as_green(built, history, sandbox, interface):
    """Through the runner as well: the named register is not in the tree of the citing commit."""
    name_register(history, None)
    history.owner_records(SUBJECT)
    status, run = _status(history, sandbox, interface)
    assert status != support.GREEN, (
        f"the check is GREEN although the register {REGISTER} it is told to read is absent (DEC-425)\n"
        f"{run.describe()}")


def test_gov_check_shows_a_history_flagged_only_before_the_base_as_green(built, history, sandbox, interface):
    """What the base is for: the commits made before the rule do not keep the check yellow."""
    history.commit(f"Change the parser ({BEFORE})")
    record_base(history, history.commit("The base"))
    status, run = _status(history, sandbox, interface)
    assert status == support.GREEN, f"the check is {status!r}, expected GREEN\n{run.describe()}"


def test_gov_check_never_shows_an_unknown_base_as_green(built, history, sandbox, interface):
    """Through the runner as well: a base that is not a commit of the repository is not GREEN."""
    _clean_history(history)
    record_base(history, "0123456789abcdef0123456789abcdef01234567")
    status, run = _status(history, sandbox, interface)
    assert status != support.GREEN, (
        f"the check is GREEN over a base that is not a commit of the repository (DEC-425)\n{run.describe()}")
