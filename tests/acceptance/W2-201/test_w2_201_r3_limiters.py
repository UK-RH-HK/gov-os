"""W2-201 R3 (DEC-1225): an exceptions entry that names Opus lifts the refusal only with a limiter the spawn or the
launch meets; Fable is refused by both; DEC-1215's substitution is gone.

Replaces S9's cases (``test_w2_201_s9_substitution.py``, deleted: they tested DEC-1215's substitution, which R3 removes;
the one that stays true is "Fable is refused", below, now for every case).

The limiters of an entry (the keys are R3's): ``class: C3``, ``task: <id or list>`` (the spawn prompt's one line ``Task:
<id>``, or the launch's ticket), ``decision: <DEC-id or list>`` (a prompt line ``Decision: <DEC-id>``, or the launch's
``--owner-named <DEC-id>``). Every limiter an entry carries must be met; an entry that names Opus and carries none lifts
nothing. A refusal says which limiter is not met: the words ``class``, ``task`` or ``decision`` (case-insensitive).

* **The hook** (``python3 -I .claude/hooks/agent_model.py``, a PreToolUse event on stdin, a planted project) and **the
  launcher** (``gov launch ... --owner-named <DEC-id> -- --model claude-opus-5-5`` on the stand-in CLI) are run on the
  same table of scenarios, ``SCENARIOS``: one rule, two readers.
* **The real exceptions file** (one entry: ``independent-auditor``, ``opus``, ``decision: [DEC-1230]``) is copied into a
  hook project for the cases named in R3's Verify.
* **Fable** (``fable``, ``claude-fable-5-2``) is refused by the hook for every type with an entry naming it and with a
  planted DEC-1215 file active; the refusals carry no ``substitut`` text and the Opus refusals no Fable hint.
* **Gone:** ``governance/project/model-substitution.yaml``, ``substitute`` and ``substitution_active`` of
  ``gov.launch.role``, every ``substitut`` of ``src/gov/launch/``, the hook and ``start_cto.sh`` (which starts the CTO on
  ``claude-opus-5-5``).

Readings (R3 leaves them open, the simplest chosen): with several ``Decision:`` lines in a prompt one of them in the
entry's list is enough, but no case here plants two; a ``decision`` or ``task`` given as one string is the same as a
list of one; a hook spawn whose entry carries no ``class`` and no ``task`` needs no ``Task:`` line.
"""

from __future__ import annotations

import pytest

import w2_201_support as k

s = k.s
ENG, AUD, QA, TD = k.ENGINEER, k.AUDITOR, k.QA, k.TEST_DESIGNER
DECIDED = "the owner (W2-201 R3 fixture)"
TK = {"C2": "DAEO-c2c2", "C3": "DAEO-c3c3"}   # the hook fixture's tickets; the launcher's tickets use the same ids
OTHER_TK = "DAEO-zzzz"
OPUS_NAMES = (("opus", "alias-opus"), (k.OPUS, "opus-id"))

# id -> (the entry's limiters, the ticket's class, the DEC id given (or None), lifted?, the limiter a refusal names)
SCENARIOS = {
    "no-limiter": ({}, "C2", None, False, None),
    "no-limiter-and-a-decision-given": ({}, "C2", "DEC-1230", False, None),
    "class-met": ({"class": "C3"}, "C3", None, True, None),
    "class-unmet": ({"class": "C3"}, "C2", None, False, "class"),
    "task-met-in-a-list": ({"task": [TK["C2"], OTHER_TK]}, "C2", None, True, None),
    "task-met-as-one-id": ({"task": TK["C2"]}, "C2", None, True, None),
    "task-unmet": ({"task": [OTHER_TK]}, "C2", None, False, "task"),
    "decision-met-in-a-list": ({"decision": ["DEC-1230", "DEC-1231"]}, "C2", "DEC-1231", True, None),
    "decision-met-as-one-id": ({"decision": "DEC-1230"}, "C2", "DEC-1230", True, None),
    "decision-unmet-none-given": ({"decision": ["DEC-1230"]}, "C2", None, False, "decision"),
    "decision-unmet-another-given": ({"decision": ["DEC-1230"]}, "C2", "DEC-1299", False, "decision"),
    "all-three-met": ({"class": "C3", "task": [TK["C3"]], "decision": ["DEC-1230"]}, "C3", "DEC-1230", True, None),
    "three-the-decision-unmet": ({"class": "C3", "task": [TK["C3"]], "decision": ["DEC-1230"]}, "C3", None, False,
                                 "decision"),
    "three-the-class-unmet": ({"class": "C3", "task": [TK["C2"]], "decision": ["DEC-1230"]}, "C2", "DEC-1230", False,
                              "class"),
    "three-the-task-unmet": ({"class": "C3", "task": [OTHER_TK], "decision": ["DEC-1230"]}, "C3", "DEC-1230", False,
                             "task"),
}


def _entry(role, limiters, model="opus"):
    return {"subagent_type": role, "model": model, **limiters, "decided": DECIDED}


# the words a refusal may use for the limiter it names (a limiter's key, or what the owner or the spawn gives for it)
WORDS = {"class": ("class", "c3"), "task": ("task",), "decision": ("decision", "owner-named")}


def _names(said, limiter):
    low = said.lower()
    assert any(word in low for word in WORDS[limiter]), (
        f"the refusal does not say which limiter is not met ({limiter}: one of {WORDS[limiter]}):\n{said}")


def _prompt(*, task=None, decision=None):
    lines = ["Do the work the brief names; return the commit.", ""]
    lines += [f"Task: {task}"] if task else []
    lines += [f"Decision: {decision}"] if decision else []
    return "\n".join([*lines, "", "Read the ticket first."])


# --------------------------------------------------------------------------
# The real exceptions file, through the hook: the comprehensive audit the owner asks for
# --------------------------------------------------------------------------

@pytest.fixture()
def real(hook_base):
    return k.hook_project(hook_base, exceptions="real")


@pytest.mark.parametrize("model", [m for m, _ in OPUS_NAMES], ids=[i for _, i in OPUS_NAMES])
def test_r3_an_auditor_spawn_carrying_decision_dec_1230_is_let_through(real, model):
    k.let_through(k.run_hook(real, k.spawn(kind=AUD, model=model, text=_prompt(decision="DEC-1230"))))


@pytest.mark.parametrize("model", [m for m, _ in OPUS_NAMES], ids=[i for _, i in OPUS_NAMES])
def test_r3_an_auditor_spawn_with_no_decision_line_is_refused_naming_the_limiter(real, model):
    run = k.run_hook(real, k.spawn(kind=AUD, model=model, text=_prompt()))
    k.refused(run)
    _names(run.stderr, "decision")


@pytest.mark.parametrize("model", [m for m, _ in OPUS_NAMES], ids=[i for _, i in OPUS_NAMES])
def test_r3_an_auditor_spawn_naming_another_decision_is_refused(real, model):
    run = k.run_hook(real, k.spawn(kind=AUD, model=model, text=_prompt(decision="DEC-1299")))
    k.refused(run)
    _names(run.stderr, "decision")


@pytest.mark.parametrize("task", [k.C3_TICKET, k.C2_TICKET], ids=["c3-ticket", "c2-ticket"])
def test_r3_an_auditor_spawn_with_a_task_line_only_is_refused(real, task):
    """A C3 ticket or not, a ``Task:`` line is not the ``decision`` limiter."""
    run = k.run_hook(real, k.spawn(kind=AUD, model="opus", text=_prompt(task=task)))
    k.refused(run)
    _names(run.stderr, "decision")


@pytest.mark.parametrize("kind", [ENG, QA, TD, "general-purpose"])
def test_r3_any_other_type_naming_opus_is_refused_whatever_it_carries(real, kind):
    """The real file has an entry for the auditor alone."""
    k.refused(k.run_hook(real, k.spawn(kind=kind, model="opus",
                                       text=_prompt(task=k.C3_TICKET, decision="DEC-1230"))))


def test_r3_the_opus_refusal_carries_no_fable_hint_and_no_substitution_reading(real):
    run = k.run_hook(real, k.spawn(kind=ENG, model="opus", text=_prompt(task=k.C3_TICKET)))
    k.refused(run)
    said = run.stderr.lower()
    assert not [w for w in ("fable", "substitut", "dec-1215") if w in said], (
        f"the refusal of an Opus spawn still speaks of Fable or the substitution\n{run.describe()}")


# --------------------------------------------------------------------------
# The same table, the hook and the launcher
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_r3_the_hook_lifts_or_refuses_by_the_entry_s_limiters(hook_base, name):
    limiters, cls, decision, lifted, says = SCENARIOS[name]
    project = k.hook_project(hook_base, exceptions={"exceptions": [_entry(ENG, limiters)]})
    carries_task = "class" in limiters or "task" in limiters or name.startswith("no-limiter")
    run = k.run_hook(project, k.spawn(kind=ENG, model="opus",
                                      text=_prompt(task=TK[cls] if carries_task else None, decision=decision)))
    if lifted:
        k.let_through(run)
    else:
        k.refused(run)
        if says:
            _names(run.stderr, says)


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_r3_the_launcher_lifts_or_refuses_by_the_entry_s_limiters(sandbox, project, cli, name):
    limiters, cls, decision, lifted, says = SCENARIOS[name]
    s.write_role(project, ENG, table=None, default=(k.SONNET, "high"))
    k.write_exceptions(project, {"exceptions": [_entry(ENG, limiters)]})
    tk = s.ticket(project, ENG, cls, tk=TK[cls])
    options = ("--owner-named", decision) if decision else ()
    result = s.cli_launch(sandbox, cli, ENG, tk, "--model", k.OPUS, options=options)
    if lifted:
        s.b.assert_launched(result)
        assert result.values("--model") == [k.OPUS], f"the stand-in did not receive --model {k.OPUS} once\n{result.args}"
        got = k.record_values(result, "model", "model_source", "exception")
        assert got == {"model": k.OPUS, "model_source": "exception", "exception": DECIDED}, got
    else:
        s.refused(result, k.EXCEPTIONS_REL)
        if says:
            _names(s.b.said(result), says)


def test_r3_a_chore_has_no_ticket_so_a_task_limiter_is_unmet(sandbox, project, cli):
    s.write_role(project, ENG, table=None, default=(k.SONNET, "high"))
    k.write_exceptions(project, {"exceptions": [_entry(ENG, {"task": [TK["C2"]]})]})
    result = x_chore(sandbox, cli)
    s.refused(result, k.EXCEPTIONS_REL)
    _names(s.b.said(result), "task")


def x_chore(sandbox, cli):
    import w2_201_x_support as x
    return x.launch(sandbox, cli, ENG, "--chore", x.CHORE_LINE, "--", "--model", k.OPUS,
                    extra_env={"GOV_TICKET": x.CALLER_TICKET})


# --------------------------------------------------------------------------
# The auditor's comprehensive audit through the launcher
# --------------------------------------------------------------------------

AUDITOR_ENTRY = _entry(AUD, {"decision": ["DEC-1230"]})


def test_r3_an_auditor_with_owner_named_dec_1230_starts_on_opus_and_records_the_exception(sandbox, project, cli):
    k.plant_real_role(project, AUD)
    k.write_exceptions(project, {"exceptions": [AUDITOR_ENTRY]})
    tk = s.ticket(project, ENG, "C2", tk="DAEO-ad01")
    result = s.cli_launch(sandbox, cli, AUD, tk, "--model", k.OPUS, options=("--owner-named", "DEC-1230"))
    s.b.assert_launched(result)
    assert result.values("--model") == [k.OPUS], f"the stand-in did not receive --model {k.OPUS} once\n{result.args}"
    got = k.record_values(result, "model", "model_source", "exception", "owner_named")
    assert got == {"model": k.OPUS, "model_source": "exception", "exception": DECIDED, "owner_named": "DEC-1230"}, got


@pytest.mark.parametrize("options", [(), ("--owner-named", "DEC-1299")], ids=["no-owner-named", "another-decision"])
def test_r3_an_auditor_asking_opus_without_the_decision_is_refused_naming_the_limiter(sandbox, project, cli, options):
    k.plant_real_role(project, AUD)
    k.write_exceptions(project, {"exceptions": [AUDITOR_ENTRY]})
    tk = s.ticket(project, ENG, "C2", tk="DAEO-ad01")
    result = s.cli_launch(sandbox, cli, AUD, tk, "--model", k.OPUS, options=options)
    s.refused(result, k.EXCEPTIONS_REL)
    _names(s.b.said(result), "decision")


@pytest.mark.parametrize("role", [ENG, TD])
def test_r3_another_role_with_owner_named_dec_1230_is_refused_no_entry_names_it(sandbox, project, cli, role):
    k.plant_real_role(project, role)
    k.write_exceptions(project, {"exceptions": [AUDITOR_ENTRY]})
    tk = s.ticket(project, role, "C3")
    s.refused(s.cli_launch(sandbox, cli, role, tk, "--model", k.OPUS, options=("--owner-named", "DEC-1230")),
              k.EXCEPTIONS_REL)


# --------------------------------------------------------------------------
# Fable: refused, with no Fable hint and no substitution reading
# --------------------------------------------------------------------------

FABLE_TYPES = [ENG, AUD, TD, QA, "general-purpose"]


@pytest.mark.parametrize("model", k.FABLE_NAMES, ids=["alias-fable", "fable-id"])
@pytest.mark.parametrize("kind", FABLE_TYPES)
def test_r3_a_fable_spawn_is_refused_for_every_type_with_an_entry_naming_it(hook_base, kind, model):
    """Entries naming Fable (both names) for the type and for every type, and an Opus entry for it whose limiters the
    spawn meets: none covers Fable. The reason carries no word ``substitut``."""
    entries = [_entry(who, {}, name) for who in (kind, "*") for name in k.FABLE_NAMES]
    entries.append(_entry(kind, {"class": "C3", "decision": ["DEC-1230"]}))
    project = k.hook_project(hook_base, exceptions={"exceptions": entries})
    run = k.run_hook(project, k.spawn(kind=kind, model=model, text=_prompt(task=k.C3_TICKET, decision="DEC-1230")))
    k.refused(run)
    assert "substitut" not in run.stderr.lower(), f"the refusal speaks of a substitution\n{run.describe()}"


@pytest.mark.parametrize("model", k.FABLE_NAMES, ids=["alias-fable", "fable-id"])
def test_r3_a_planted_dec_1215_file_is_read_by_no_one(hook_base, model):
    """DEC-1215's file, active, in the project: Fable is refused as without it (it was let through on a C3 ticket), and
    the engineer's Opus spawn on a C3 ticket is judged by its entry's limiter alone (let through, not turned into a
    Fable spawn)."""
    project = k.plant_substitution_file(k.hook_project(hook_base))
    run = k.run_hook(project, k.spawn(kind=ENG, model=model, tasks=(k.C3_TICKET,)))
    k.refused(run)
    run = k.run_hook(project, k.spawn(kind=ENG, model="opus", tasks=(k.C3_TICKET,)))
    k.let_through(run)  # the fixture's C3 entry for the engineer, class met: Opus is judged by its limiter alone


@pytest.mark.parametrize("model", k.FABLE_NAMES, ids=["alias-fable", "fable-id"])
def test_r3_a_fable_spawn_with_no_exceptions_file_is_refused_with_no_substitution_text(hook_base, model):
    project = k.hook_project(hook_base, exceptions=None)
    run = k.run_hook(project, k.spawn(kind=ENG, model=model, tasks=(k.C3_TICKET,)))
    k.refused(run)
    assert "substitut" not in run.stderr.lower(), run.describe()


@pytest.mark.parametrize("model", k.FABLE_NAMES, ids=["alias-fable", "fable-id"])
def test_r3_a_launch_asking_fable_is_refused_with_an_opus_entry_whose_limiters_it_meets(sandbox, project, cli, model):
    k.plant_real_role(project, AUD)
    k.write_exceptions(project, {"exceptions": [AUDITOR_ENTRY]})
    tk = s.ticket(project, ENG, "C2", tk="DAEO-ad01")
    result = s.cli_launch(sandbox, cli, AUD, tk, "--model", model, options=("--owner-named", "DEC-1230"))
    s.refused(result)
    assert "substitut" not in s.b.said(result).lower(), result.describe()


# --------------------------------------------------------------------------
# The substitution and its readers are gone
# --------------------------------------------------------------------------

def test_r3_the_substitution_file_is_deleted():
    assert not (k.REPO_ROOT / k.SUBSTITUTION_REL).exists(), f"{k.SUBSTITUTION_REL} still exists"


def test_r3_the_role_reader_has_no_substitution_function():
    from gov.launch import role

    left = [name for name in ("substitute", "substitution_active", "SUBSTITUTION_REL") if hasattr(role, name)]
    assert not left, f"gov.launch.role still has {left}"


@pytest.mark.parametrize("path", ["src/gov/launch/launcher.py", "src/gov/launch/role.py",
                                  "src/gov/launch/model_exceptions.py", ".claude/hooks/agent_model.py",
                                  "governance/project/orchestration/tools/start_cto.sh"])
def test_r3_no_substitut_is_left_in_the_launcher_the_hook_or_the_cto_start_script(path):
    text = (k.REPO_ROOT / path).read_text(encoding="utf-8")
    hits = [line.strip() for line in text.splitlines() if "substitut" in line.lower()]
    assert not hits, f"{path} still speaks of a substitution: {hits[:3]}"


def test_r3_no_file_of_src_gov_launch_names_a_substitution():
    hits = [f"{p.name}: {line.strip()}" for p in sorted((k.REPO_ROOT / "src/gov/launch").rglob("*.py"))
            for line in p.read_text(encoding="utf-8").splitlines() if "substitut" in line.lower()]
    assert not hits, f"src/gov/launch still names a substitution: {hits[:3]}"


def test_r3_the_cto_start_script_starts_the_cto_on_claude_opus_5_5():
    text = (k.REPO_ROOT / "governance/project/orchestration/tools/start_cto.sh").read_text(encoding="utf-8")
    assert "claude-opus-5-5" in text and "gov.launch.role" not in text, (
        "start_cto.sh must name claude-opus-5-5 and no longer ask gov.launch.role for the model")
