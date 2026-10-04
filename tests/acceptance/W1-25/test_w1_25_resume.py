"""W1-25 -- resuming from the checkpoint alone, and what the family check's command does.

- KPI success 2 [CAP-20.a, CAP-37.f]: "A fresh session resumes the ticket at
  the recorded next step from the checkpoint alone".
- KPI success 4 [CAP-38.b]: "a session with only the latest checkpoint and the
  SessionStart output states the ticket, its inputs and the next step".

Recommended option of DP-6, its deterministic part: ``gov checkpoint --resume``
prints, from the latest checkpoint of a ticket and nothing else, the resume
brief a session needs (the ticket, its inputs with their hashes, the next
step); the SessionStart hook (W1-49, W1-29) injects that text later. The family
check's declared command passes when the brief can be built and fails when it
cannot. The real session is in ``test_w1_25_live_session.py``. Another answer
to DP-6 changes these two files only.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

import w1_25_support as support

cli_support = support.cli_support

DEV_TIERS = Path(os.environ.get("GOV_DEV_TIERS", "~/gov-os-workbench/synthetic")).expanduser()
DEV_TIER = "a-dev"


def _resume(gov, ticket=support.TICKET, json=True):
    return gov("checkpoint", "--resume", "--ticket", ticket, *(("--json",) if json else ()))


def _assert_brief(result, project, path):
    assert result.get("ticket") == support.TICKET, result
    assert result.get("next_action") == support.NEXT_STEP, result
    assert result.get("path") == path.relative_to(project).as_posix(), result
    inputs = result.get("inputs")
    assert isinstance(inputs, list) and inputs, f"the brief names no input: {result}"
    digest = support.sha256(project / support.INPUT_REL)
    assert any(digest in str(item.get("hash", "")) for item in inputs), f"the brief lacks the input's hash: {inputs}"
    assert any(item.get("id") == support.TICKET for item in inputs), f"the brief lacks the ticket input: {inputs}"


def test_resume_states_the_ticket_its_inputs_and_the_next_step(project, gov, interface, checkpoint):
    path = checkpoint(inputs=(support.INPUT_REL,))
    _assert_brief(support.succeeded(_resume(gov), interface), project, path)


def test_resume_reads_the_latest_checkpoint_of_the_ticket(gov, interface, checkpoint):
    checkpoint(next_step="an earlier step")
    checkpoint(ticket=support.OTHER_TICKET, next_step="the other ticket's step")
    checkpoint(next_step="the latest step")
    assert support.succeeded(_resume(gov), interface).get("next_action") == "the latest step"
    other = support.succeeded(_resume(gov, support.OTHER_TICKET), interface)
    assert other.get("next_action") == "the other ticket's step", other


def test_the_brief_as_text_names_the_ticket_each_input_and_the_next_step(gov, checkpoint):
    """What a hook injects: plain text, without ``--json``."""
    path = checkpoint(inputs=(support.INPUT_REL,))
    run = _resume(gov, json=False)
    assert run.returncode == 0, run.describe()
    for expected in (support.TICKET, support.NEXT_STEP,
                     *(str(item["id"]) for item in support.inputs_of(support.frontmatter(path)))):
        assert expected in run.stdout, f"the brief does not state {expected!r}\n{run.describe()}"


def test_resume_only_reads(project, gov, checkpoint):
    checkpoint()
    before = support.state(project)
    run = _resume(gov)
    assert run.returncode == 0 and support.state(project) == before, run.describe()


def test_resume_without_a_checkpoint_is_refused(gov, interface):
    error = support.refused(_resume(gov), interface, exit_codes=(1, support.EXIT_UNHEALTHY))
    assert error["code"] == support.MISSING, error


def test_a_fresh_clone_resumes_from_the_committed_checkpoint(project, sandbox, tmp_path, interface, checkpoint):
    """[CAP-20.a, CAP-37.f] after a crash nothing is left but git: no ``.gov-runtime/``, no session."""
    path = checkpoint(inputs=(support.INPUT_REL,))
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(project), str(clone)], check=True,
                   capture_output=True)
    assert not (clone / ".gov-runtime").exists()
    run = cli_support.run_gov(clone, sandbox, "checkpoint", "--resume", "--ticket", support.TICKET, "--json")
    result = support.succeeded(run, interface)
    assert result.get("path") == path.relative_to(project).as_posix(), result
    _assert_brief(result, clone, clone / result["path"])


@pytest.mark.local_only
def test_a_fresh_clone_of_a_dev_tier_resumes(built, sandbox, tmp_path, interface):
    """The same on a project that is not the Gov OS (CHAOS-A-01): a clone of a dev tier, never the tier itself."""
    tier = DEV_TIERS / DEV_TIER
    if not (tier / ".git").exists():
        pytest.skip(f"no dev tier at {tier} (GOV_DEV_TIERS)")
    work = tmp_path / "tier"
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(tier), str(work)], check=True, capture_output=True)
    support.add_fixtures(work)
    run = cli_support.run_gov_with_code(built, work, sandbox, *support.write_args(inputs=(support.INPUT_REL,)))
    path = support.checkpoint_path(work, support.succeeded(run, interface))
    cli_support.commit_all(work, "checkpoint")
    fresh = tmp_path / "fresh"
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(work), str(fresh)], check=True, capture_output=True)
    run = cli_support.run_gov_with_code(built, fresh, sandbox, "checkpoint", "--resume", "--ticket", support.TICKET,
                                        "--json")
    _assert_brief(support.succeeded(run, interface), fresh, fresh / path.relative_to(work))


# --------------------------------------------------------------------------
# The family check's declared command (KPI success 4)
# --------------------------------------------------------------------------

def _declared_command(gov, interface):
    return support.declaration(gov("check", "--list", "--json"), interface)["command"]


def test_the_family_check_passes_when_the_latest_checkpoint_gives_the_brief(project, sandbox, gov, interface,
                                                                           checkpoint):
    checkpoint(inputs=(support.INPUT_REL,))
    done = support.run_declared_command(project, sandbox, _declared_command(gov, interface))
    assert done.returncode == 0, f"the family check fails on a good checkpoint:\n{done.stdout}\n{done.stderr}"


def test_the_family_check_fails_when_the_latest_checkpoint_has_no_next_step(project, sandbox, gov, interface,
                                                                            checkpoint):
    path = checkpoint(commit=False)
    support.rewrite_frontmatter(path, lambda document: document.pop(support.KEY_NEXT))
    cli_support.commit_all(project, "a checkpoint without its next step")
    done = support.run_declared_command(project, sandbox, _declared_command(gov, interface))
    assert done.returncode != 0, f"the family check passes without a next step:\n{done.stdout}\n{done.stderr}"


def test_the_family_check_fails_when_an_input_has_no_hash(project, sandbox, gov, interface, checkpoint):
    path = checkpoint(commit=False)

    def drop_hashes(document):
        for item in document[support.KEY_INPUTS]:
            item.pop("hash", None)

    support.rewrite_frontmatter(path, drop_hashes)
    cli_support.commit_all(project, "a checkpoint without hashes")
    done = support.run_declared_command(project, sandbox, _declared_command(gov, interface))
    assert done.returncode != 0, f"the family check passes an input without its hash:\n{done.stdout}\n{done.stderr}"


def test_the_family_check_changes_nothing(project, sandbox, gov, interface, checkpoint):
    checkpoint()
    command = _declared_command(gov, interface)
    before = support.state(project)
    support.run_declared_command(project, sandbox, command)
    assert support.state(project) == before, "the family check changed the project"
