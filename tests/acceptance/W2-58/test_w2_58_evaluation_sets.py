"""W2-58, item 5 -- (d) the hidden half of an evaluation set.

KPI success 3: "An evaluation set declared in the path map with a visible and a
hidden part, a session measured by it is refused reads of the hidden part, and
the measurement script scores it without showing the answers [DEC-820 (d)]".
KPI failure: "(d) still refuses, by every read route an honest agent takes in
ordinary work (DEC-801)". DEC-845 item 2: "The path map gains the
evaluation_sets block that W2-58 enforces and W2-61 uses: each set with its
visible part and its hidden part."

The block, as the brief states it: ``evaluation_sets`` maps a set's name to
``visible`` (a list of project-relative paths or globs in the path map's glob
language: ``*`` stays in one folder, ``**`` crosses folders), ``hidden`` (the
same) and ``measures`` (a map with ``roles`` and/or ``tickets``). A session is
measured by a set when its role is in ``measures.roles`` or its ticket in
``measures.tickets``.

The fixture set (``w2_58_support.evaluation_block``): visible
``eval/memory/visible/**``; hidden ``eval/memory/hidden/**`` and
``eval/memory/answers-*.yaml``; measured: the role ``research`` and the ticket
``DAEO-zz63``. The scorer ``eval/score.py`` is a throwaway (W2-61 writes the
real one): it reads the hidden part and prints only a score.
"""

from __future__ import annotations

import copy

import pytest
import yaml

import w2_58_support as s

HIDDEN = sorted(s.HIDDEN_FILES)
HIDDEN_FILE = "eval/memory/hidden/answers.yaml"
VISIBLE_FILE = sorted(s.VISIBLE_FILES)[0]
BESIDE = sorted(s.BESIDE_HIDDEN)[0]

MEASURED_SESSIONS = {"by-role": (s.RESEARCH, s.EXPERIMENT), "by-ticket": (s.ENGINEER, s.MEASURED)}
UNMEASURED_SESSIONS = {
    "product-spec": (s.PRODUCT_SPEC, s.SPEC),
    "engineer-other-ticket": (s.ENGINEER, s.OTHER),
    "auditor-not-listed": (s.AUDITOR, s.T),
    "test-designer": (s.TEST_DESIGNER, s.T),
    "ticket-lead": (s.ORCHESTRATOR, s.T),
}


def _refused_calls(world):
    copy_target = world.sandbox.tmpdir / "copy-of-the-answers"
    return [
        s.read(world.path(HIDDEN_FILE)),
        s.read(world.path("eval/memory/answers-extra.yaml")),
        s.grep(path=world.path(HIDDEN_FILE), pattern="q1"),
        s.bash(f"cat {HIDDEN_FILE}"),
        s.bash("cat eval/memory/answers-extra.yaml"),
        s.bash(f"head -n 1 {HIDDEN_FILE}"),
        s.bash(f"grep q1 {HIDDEN_FILE}"),
        s.bash(f"git show HEAD:{HIDDEN_FILE}"),
        s.bash(f"cp {HIDDEN_FILE} {s.q(copy_target)}"),
        s.grep(path=world.path("eval/memory/hidden")),
        s.glob_call("eval/memory/hidden/*"),
        s.glob_call("*", path=world.path("eval/memory/hidden")),
        s.bash("ls eval/memory/hidden"),
        s.grep(path=world.path("eval")),
        s.grep(),
        s.bash("grep -rn q1 eval/"),
        s.bash("grep -r q1 ."),
        s.bash("git grep -n q1"),
    ]


REFUSED_IDS = ("Read-hidden", "Read-hidden-single-folder-glob", "Grep-file", "cat", "cat-single-folder-glob",
               "head", "grep-file", "git-show-HEAD-path", "cp", "Grep-hidden-folder", "Glob-pattern", "Glob-path",
               "ls", "Grep-above", "Grep-no-path", "grep-r-above", "grep-r-dot", "git-grep")


def _measured_allowed(world):
    return [
        s.read(world.path(VISIBLE_FILE)),
        s.bash(f"cat {VISIBLE_FILE}"),
        s.bash(f"grep -rn {s.WORD} eval/memory/visible/"),
        s.read(world.path(BESIDE)),
        s.bash(f"python3 {s.SCORER_REL}"),
    ]


MEASURED_ALLOWED_IDS = ("Read-visible", "cat-visible", "grep-r-visible", "Read-beside-single-folder-glob",
                        "run-the-scorer")


@pytest.mark.parametrize("index", range(len(REFUSED_IDS)), ids=REFUSED_IDS)
@pytest.mark.parametrize("session", sorted(MEASURED_SESSIONS))
def test_a_measured_session_is_refused_the_hidden_part(eval_world, session, index):
    role, ticket = MEASURED_SESSIONS[session]
    call = _refused_calls(eval_world)[index]
    s.assert_refused(eval_world.ask(call, role, ticket), call, f"{session}: ")


@pytest.mark.parametrize("index", range(len(MEASURED_ALLOWED_IDS)), ids=MEASURED_ALLOWED_IDS)
@pytest.mark.parametrize("session", sorted(MEASURED_SESSIONS))
def test_a_measured_session_reads_the_visible_part_and_runs_the_measurement(eval_world, session, index):
    role, ticket = MEASURED_SESSIONS[session]
    call = _measured_allowed(eval_world)[index]
    s.assert_allowed(eval_world.ask(call, role, ticket), call, f"{session}: ")


@pytest.mark.parametrize("session", sorted(UNMEASURED_SESSIONS))
def test_a_session_the_set_does_not_measure_reads_the_hidden_part(eval_world, session):
    role, ticket = UNMEASURED_SESSIONS[session]
    for call in (s.read(eval_world.path(HIDDEN_FILE)), s.bash(f"cat {HIDDEN_FILE}"),
                 s.bash("grep -rn q1 eval/")):
        s.assert_allowed(eval_world.ask(call, role, ticket), call, f"{session}: ")


def test_the_scorer_reads_the_hidden_part_and_prints_only_a_score(eval_world):
    run = s.run_in_project(eval_world.sandbox, eval_world.project, ["python3", s.SCORER_REL], s.RESEARCH,
                           s.EXPERIMENT.tk)
    assert run.returncode == 0 and "score: 1/2" in run.stdout, run.describe()
    assert s.HIDDEN_WORD not in run.stdout + run.stderr, f"the scorer showed an answer\n{run.describe()}"


# --------------------------------------------------------------------------
# By its sandbox
# --------------------------------------------------------------------------

def test_the_launch_of_a_measured_session_denies_the_read_tool_the_hidden_part(sandbox, cli):
    project = s.make_eval_project(sandbox)
    settings = s.launch(sandbox, cli, s.ENGINEER, s.MEASURED).settings()
    faults = s.read_tool_denial_faults(settings, project, sandbox.home, HIDDEN)
    assert not faults, f"the launched measured session's settings: {faults}; Read rules: {s.read_deny_specs(settings)}"
    for rel in (VISIBLE_FILE, BESIDE, s.SCORER_REL):
        covering = s.covering_read_rules(settings, project, sandbox.home, project / rel)
        assert not covering, f"a Read deny rule of the measured session covers {rel}: {covering}"


def test_the_launch_of_an_unmeasured_session_leaves_the_hidden_part_to_the_read_tool(sandbox, cli):
    project = s.make_eval_project(sandbox)
    settings = s.launch(sandbox, cli, s.ENGINEER, s.OTHER).settings()
    for rel in HIDDEN:
        covering = s.covering_read_rules(settings, project, sandbox.home, project / rel)
        assert not covering, f"a Read deny rule of an unmeasured session covers {rel}: {covering}"


# --------------------------------------------------------------------------
# The schema declares the block
# --------------------------------------------------------------------------

def _document(block):
    document = yaml.safe_load(s.REPO_PATH_MAP.read_text(encoding="utf-8"))
    document["evaluation_sets"] = block
    return document


def _errors(document):
    return [error.message for error in s.schema_validator().iter_errors(document)]


def test_the_schema_names_the_block():
    schema = s.schema_validator().schema
    assert "evaluation_sets" in (schema.get("properties") or {}), (
        f"{s.PATH_MAP_SCHEMA.relative_to(s.REPO_ROOT)} does not declare evaluation_sets")


def test_a_valid_block_validates():
    errors = _errors(_document(s.evaluation_block()))
    assert not errors, f"a valid evaluation_sets block does not validate: {errors}"


def _without_hidden():
    block = copy.deepcopy(s.evaluation_block())
    del block[s.EVAL_SET]["hidden"]
    return block


def _path_not_a_string(part):
    block = copy.deepcopy(s.evaluation_block())
    block[s.EVAL_SET][part] = ["eval/memory/hidden/**", 42]
    return block


INVALID = {
    "set-without-hidden": _without_hidden,
    "hidden-path-not-a-string": lambda: _path_not_a_string("hidden"),
    "visible-path-not-a-string": lambda: _path_not_a_string("visible"),
    "hidden-not-a-list": lambda: {s.EVAL_SET: {**s.evaluation_block()[s.EVAL_SET], "hidden": "eval/memory/hidden/**"}},
}


@pytest.mark.parametrize("name", sorted(INVALID))
def test_an_invalid_block_does_not_validate(name):
    assert _errors(_document(INVALID[name]())), f"the schema accepts an evaluation_sets block with {name}"


# --------------------------------------------------------------------------
# This repository's own path map declares W2-61's set
# --------------------------------------------------------------------------

ASSESSMENT_B = "docs/assessment/2026-10/B-memory-retrieval.md"


def _repo_sets():
    document = yaml.safe_load(s.REPO_PATH_MAP.read_text(encoding="utf-8"))
    sets = document.get("evaluation_sets") if isinstance(document, dict) else None
    assert isinstance(sets, dict) and sets, f"{s.PATH_MAP_REL} declares no evaluation_sets block"
    return document, sets


def test_this_repository_declares_a_set_for_w2_61():
    document, sets = _repo_sets()
    found = [name for name, entry in sets.items()
             if isinstance(entry, dict) and ASSESSMENT_B in (entry.get("visible") or [])]
    assert found, f"no evaluation set of {s.PATH_MAP_REL} holds {ASSESSMENT_B} in its visible part"
    for name in found:
        entry = sets[name]
        hidden = entry.get("hidden")
        assert isinstance(hidden, list) and hidden and all(isinstance(p, str) and p for p in hidden), (
            f"set {name}: its hidden part is empty or not a list of paths")
        visible = entry.get("visible")
        for pattern in hidden:
            assert pattern not in visible, f"set {name}: the hidden part names the visible path {pattern}"
            regex = s._regex(pattern)
            named = [path for path in visible if "*" not in path and regex.fullmatch(path)]
            assert not named, f"set {name}: the hidden pattern {pattern} takes in visible paths {named}"
        measures = entry.get("measures")
        assert isinstance(measures, dict) and (measures.get("roles") or measures.get("tickets")), (
            f"set {name}: measures names no role and no ticket")
    errors = _errors(document)
    assert not errors, f"{s.PATH_MAP_REL} does not validate against the schema: {errors}"
