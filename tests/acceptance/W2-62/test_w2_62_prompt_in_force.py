"""W2-62 -- the hook names the prompt in force, read from the roster (W2-M373, DEC-837 item 1).

KPI success 4: "The hook names the prompt of the wave in progress, read from the project's
configuration, not a constant; with no such setting it names none rather than a wrong one".

The setting, this ticket's public interface: ``governance/project/roster.yaml``, under
``roles:`` -> ``orchestrator:``, the key ``prompt:`` with a path relative to the project.
Every fixture project also holds ``governance/project/prompts/w1-orchestrator.md`` as a
file, so a hook that falls back to the Wave 1 prompt would find it there.
"""

from __future__ import annotations

import re

import pytest

import w2_62_support as support

ORCH = support.ORCH
LEAD = support.LEAD
PROMPTS = (
    "governance/project/prompts/w2-orchestrator.md",
    "governance/project/prompts/zephyr-wave-7.md",
    "docs/runbooks/orchestrator-of-the-wave.md",
)
LEAD_TICKET = "LD-4242"


def _project(tmp_path, roster_text, prompts=PROMPTS):
    return support.make_project(tmp_path / "repo", roster_text, prompts=prompts)


def _section(tree, rel):
    cp = support.checkpoint(support.section_text(2_000, "TOKEN-PROMPT"))
    support.write_checkpoint(tree, rel, cp)
    return cp


@pytest.mark.parametrize("prompt", PROMPTS)
def test_the_main_tree_names_the_rosters_prompt(tmp_path, sandbox, prompt):
    """Success 4, item 7: the roster's prompt, read now with the checkpoint; no other prompt, never Wave 1's."""
    project = _project(tmp_path, support.roster(prompt))
    cp = _section(project, ORCH)
    run = support.run_sessionstart(project, sandbox, "resume")
    support.assert_well_formed(run)
    injection = run.injection
    assert prompt in injection, f"the injection does not name the roster's prompt {prompt}: {injection[:400]!r}"
    others = [other for other in (*PROMPTS, support.W1_PROMPT) if other != prompt and other in injection]
    assert not others, f"the injection names a prompt the roster does not: {others}"
    lowered = injection.lower()
    assert re.search(r"\bread\b", lowered) and re.search(r"\bnow\b", lowered) and ORCH in injection, (
        f"the injection does not tell the session to read the prompt and the checkpoint now: {injection[:400]!r}")
    support.assert_instruction(injection, cp, ORCH)


@pytest.mark.parametrize("prompt", PROMPTS[:2])
def test_in_a_worktree_the_lead_is_sent_to_appendix_a5_of_the_rosters_prompt(tmp_path, sandbox, prompt):
    """Success 4, item 7 in a linked worktree: the ticket-lead sentence, appendix A5 of the roster's prompt, the
    lead checkpoint."""
    project = _project(tmp_path, support.roster(prompt))
    worktree = support.add_worktree(project, tmp_path / "worktrees" / "lead-fixture")
    cp = _section(worktree, LEAD)
    run = support.run_sessionstart(worktree, sandbox, "resume", ticket=LEAD_TICKET)
    support.assert_well_formed(run)
    injection = run.injection
    lowered = injection.lower()
    assert f"ticket lead for {LEAD_TICKET}".lower() in lowered and "appendix a5" in lowered, (
        f"the injection does not say `ticket lead for {LEAD_TICKET}` and `appendix A5`: {injection[:400]!r}")
    assert prompt in injection and support.W1_PROMPT not in injection, (
        f"the lead is not sent to appendix A5 of the roster's prompt {prompt}: {injection[:400]!r}")
    support.assert_instruction(injection, cp, LEAD)


def test_two_projects_with_two_prompts_get_two_paths(tmp_path, sandbox):
    """Success 4, item 7: the prompt is never a constant."""
    named = []
    for n, prompt in enumerate(PROMPTS[:2]):
        project = support.make_project(tmp_path / f"repo-{n}", support.roster(prompt), prompts=PROMPTS)
        _section(project, ORCH)
        injection = support.run_sessionstart(project, sandbox, "resume").injection
        named.append([candidate for candidate in (*PROMPTS, support.W1_PROMPT) if candidate in injection])
    assert named == [[PROMPTS[0]], [PROMPTS[1]]], f"the prompts named in the two projects: {named}"


ABSENT = {
    "no roster file": None,
    "no prompt key": support.roster(None),
    "a prompt key under another role only": support.roster(None, other_role_prompt=PROMPTS[1]),
    "a roster that is not valid YAML": "roles:\n  orchestrator: [unclosed\n    prompt: governance/project/prompts/w2-orchestrator.md\n  : :\n",
}


@pytest.mark.parametrize("case", tuple(ABSENT))
def test_with_no_setting_the_main_tree_names_no_prompt(tmp_path, sandbox, case):
    """Success 4, item 7: no prompt at all, in particular not Wave 1's; the checkpoint and its instruction stay."""
    project = _project(tmp_path, ABSENT[case])
    cp = _section(project, ORCH)
    run = support.run_sessionstart(project, sandbox, "compact")
    support.assert_well_formed(run)
    support.assert_names_no_prompt(run.injection)
    assert not [prompt for prompt in PROMPTS if prompt in run.injection], "a prompt the roster does not name is named"
    support.assert_instruction(run.injection, cp, ORCH)


def test_with_no_setting_the_worktree_names_no_prompt(tmp_path, sandbox):
    """Success 4, item 7 in a linked worktree: no prompt, the lead checkpoint and its instruction stay."""
    project = _project(tmp_path, None)
    worktree = support.add_worktree(project, tmp_path / "worktrees" / "lead-fixture")
    cp = _section(worktree, LEAD)
    run = support.run_sessionstart(worktree, sandbox, "resume", ticket=LEAD_TICKET)
    support.assert_well_formed(run)
    support.assert_names_no_prompt(run.injection)
    support.assert_instruction(run.injection, cp, LEAD)


def test_with_no_setting_and_no_checkpoint_the_path_and_the_gap_are_still_named(tmp_path, sandbox):
    """Items 6 and 7 together: no prompt named, the checkpoint's path named and said to be missing."""
    project = _project(tmp_path, support.roster(None))
    run = support.run_sessionstart(project, sandbox, "resume")
    support.assert_well_formed(run)
    support.assert_names_no_prompt(run.injection)
    assert ORCH in run.injection and any(phrase in run.injection.lower() for phrase in support.SAYS_SO), (
        f"the injection does not name the missing checkpoint: {run.injection[:400]!r}")
