"""W2-201 S5: the helper hook lets Opus through for a test designer, engineer, independent auditor or QA engineer only
for C3 work.

The hook (``python3 -I .claude/hooks/agent_model.py``) as a subprocess on one PreToolUse event, ``CLAUDE_PROJECT_DIR``
a planted project: the fixture tickets of ``w2_201_support.TICKETS``, a fixture rubric (C3 ``src/critical``, C2 the rest
of ``src``, C1 ``docs``, FULL at least C2) and an exceptions file listing the four roles with ``model: opus`` and
``class: C3``. The ticket is the one the prompt's ``Task: <id>`` line names. A refusal exits 2 with its reason on
stderr; a spawn let through exits 0.

The last cases are on this repository's own files: the exceptions file's four entries, and the hook's outcome against
``gov.launch.criticality.ticket_criticality`` over the real rubric on a table of ``allowed_paths``.
"""

from __future__ import annotations

import pytest
import yaml

import w2_201_support as k

ENG = k.ENGINEER


@pytest.fixture()
def project(hook_base):
    return k.hook_project(hook_base)


def _run(project, **spawn):
    return k.run_hook(project, k.spawn(**spawn))


# --------------------------------------------------------------------------
# Let through, refused by class
# --------------------------------------------------------------------------

@pytest.mark.parametrize("kind", k.FOUR)
def test_s5_an_opus_spawn_for_a_c3_ticket_is_let_through_for_each_of_the_four_roles(project, kind):
    k.let_through(_run(project, kind=kind, model="opus", tasks=(k.C3_TICKET,)))


@pytest.mark.parametrize("kind", k.FOUR)
def test_s5_an_opus_spawn_for_a_c2_ticket_is_refused_naming_the_ticket_its_class_and_c3_work_only(project, kind):
    """Red on the base: the hook lets every listed type and model through, whatever the ticket."""
    k.refused(_run(project, kind=kind, model="opus", tasks=(k.C2_TICKET,)), k.C2_TICKET, "C2", "C3 work only")


def test_s5_a_claude_opus_model_id_is_judged_as_opus(project):
    """``opus`` in an entry matches every ``claude-opus-*`` id: through on C3, refused on C2."""
    k.let_through(_run(project, model=k.OPUS, tasks=(k.C3_TICKET,)))
    k.refused(_run(project, model=k.OPUS, tasks=(k.C2_TICKET,)), k.C2_TICKET, "C2")


@pytest.mark.parametrize("tk", ["DAEO-c1c1", "DAEO-fdoc"], ids=["c1-docs", "full-docs-is-c2"])
def test_s5_an_opus_spawn_for_a_c1_or_full_docs_ticket_is_refused(project, tk):
    want = k.TICKETS[tk][3]
    k.refused(_run(project, model="opus", tasks=(tk,)), tk, want)


def test_s5_the_ticket_s_class_key_is_never_read(project):
    """DAEO-c2k3's ``class: C3`` is its kind; its paths make it C2."""
    k.refused(_run(project, model="opus", tasks=("DAEO-c2k3",)), "DAEO-c2k3", "C2")


def test_s5_the_highest_matching_rule_gives_the_class(project):
    """``docs/**`` (C1) beside a ``src/critical`` file (C3): C3."""
    k.let_through(_run(project, model="opus", tasks=("DAEO-mixd",)))


def test_s5_an_entry_without_a_class_is_not_limited_to_c3(hook_base):
    project = k.hook_project(hook_base, exceptions={"exceptions": [
        {"subagent_type": ENG, "model": "opus", "decided": k.DECIDED}]})
    k.let_through(_run(project, model="opus", tasks=(k.C2_TICKET,)))


def test_s5_the_task_tool_name_is_judged_as_the_agent_tool(project):
    k.refused(_run(project, tool="Task", model="opus", tasks=(k.C2_TICKET,)), k.C2_TICKET, "C2")
    k.let_through(_run(project, tool="Task", model="opus", tasks=(k.C3_TICKET,)))


# --------------------------------------------------------------------------
# The ticket cannot be told: Sonnet
# --------------------------------------------------------------------------

def test_s5_an_opus_spawn_with_no_task_line_is_refused_naming_the_task_line(project):
    k.refused(_run(project, model="opus", tasks=()), "Task:")


def test_s5_an_opus_spawn_with_two_task_lines_naming_different_ids_is_refused(project):
    k.refused(_run(project, model="opus", tasks=(k.C3_TICKET, "DAEO-mixd")), "Task:")


def test_s5_two_task_lines_naming_the_same_id_are_one_ticket(project):
    k.let_through(_run(project, model="opus", tasks=(k.C3_TICKET, k.C3_TICKET)))


def test_s5_an_opus_spawn_naming_a_ticket_with_no_file_is_refused(project):
    run = _run(project, model="opus", tasks=("DAEO-gone1",))
    k.refused(run)


def test_s5_an_opus_spawn_for_a_type_with_no_exception_is_refused(project):
    """Guard on the base (the base refuses an unlisted type too): ``research`` is not in the exceptions file."""
    k.refused(_run(project, kind=k.RESEARCH, model="opus", tasks=(k.C3_TICKET,)))
    k.refused(_run(project, kind="general-purpose", model="opus", tasks=(k.C3_TICKET,)))


# --------------------------------------------------------------------------
# Sonnet or no model: let through whatever the ticket
# --------------------------------------------------------------------------

@pytest.mark.parametrize("model", ["sonnet", k.SONNET, k.NO_MODEL], ids=["sonnet", "sonnet-id", "no-model"])
@pytest.mark.parametrize("tasks", [(k.C2_TICKET,), (), ("DAEO-gone1",), (k.C3_TICKET, k.C2_TICKET)],
                         ids=["c2-ticket", "no-task-line", "missing-ticket", "two-ids"])
def test_s5_a_sonnet_or_no_model_spawn_is_let_through_whatever_the_ticket(project, model, tasks):
    """Guard on the base."""
    k.let_through(_run(project, model=model, tasks=tasks))


# --------------------------------------------------------------------------
# This repository's own files
# --------------------------------------------------------------------------

def test_s5_the_real_exceptions_file_lists_the_four_roles_on_opus_for_c3_by_dec_1214_k1():
    data = yaml.safe_load((k.REPO_ROOT / k.EXCEPTIONS_REL).read_text(encoding="utf-8"))
    assert isinstance(data, dict) and isinstance(data.get("exceptions"), list), (
        f"{k.EXCEPTIONS_REL} is not a map with an exceptions list: {data!r}")
    entries = data["exceptions"]
    kinds = sorted(str(e.get("subagent_type")) for e in entries if isinstance(e, dict))
    assert kinds == sorted(k.FOUR) and len(entries) == 4, (
        f"{k.EXCEPTIONS_REL} lists {kinds}; S5 names {sorted(k.FOUR)}, one entry each")
    for entry in entries:
        model = str(entry.get("model"))
        assert model == "opus" or model.startswith("claude-opus-"), f"the entry {entry} is not for Opus"
        assert entry.get("class") == "C3", f"the entry {entry} does not carry class: C3"
        assert "DEC-1214 K1" in str(entry.get("decided", "")), f"the entry {entry}'s decided text does not name DEC-1214 K1"


ROWS = {
    "close": (["src/gov/close/x.py"], "STANDARD"),
    "kernel-role": (["template/governance/kernel/roles/engineer.md"], "STANDARD"),
    "contract-beside-docs": (["docs/contract/x.md", "docs/notes.md"], "STANDARD"),
    "hidden-set": (["fixtures/evaluation/examin/hidden/q.json"], "STANDARD"),
    "path-map": (["governance/project/path-map.yaml"], "FULL"),
    "health": (["src/gov/health/x.py"], "STANDARD"),
    "launch-full-with-probe": (["src/gov/launch/**", "docs/probes/DAEO-k1us/**  # the probe record"], "FULL"),
    "guard": (["src/gov/guard/x.py"], "STANDARD"),
    "hook": ([".claude/hooks/agent_model.py"], "STANDARD"),
    "settings": ([".claude/settings.json"], "STANDARD"),
    "docs": (["docs/x.md"], "STANDARD"),
    "docs-full": (["docs/x.md"], "FULL"),
    "no-paths": ([], "STANDARD"),
}


@pytest.mark.parametrize("row", sorted(ROWS))
@pytest.mark.parametrize("kind", [ENG, k.QA])
def test_s5_the_hook_and_ticket_criticality_give_the_same_class_on_the_real_rubric(hook_base, row, kind):
    """The real criticality and exceptions files copied into the project; the ticket's class by
    ``ticket_criticality`` on this repository: an Opus spawn is let through when it is C3, else refused naming that
    class. Red on the base for every row that is not C3 there (the hook lets the listed types through)."""
    allowed, profile = ROWS[row]
    want = k.real_criticality(allowed, profile)
    tk = "DAEO-row1"
    tickets = {tk: k.ticket_file_text(k.front_matter(allowed, profile, tk=tk))}
    project = k.hook_project(hook_base, rubric="real", exceptions="real", tickets=tickets)
    run = k.run_hook(project, k.spawn(kind=kind, model="opus", tasks=(tk,)))
    if want == "C3":
        k.let_through(run)
    else:
        k.refused(run, tk, want)
