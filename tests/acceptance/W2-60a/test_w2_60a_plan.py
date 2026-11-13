"""W2-60a, S12 (routed from W2-33's S2, DEC-1156 (3)) -- the launcher's plan prints the role's default model and effort.

KPI [DEC-954, DEC-957, DEC-1156 (3)]: "the launcher's plan for a planted ticket prints the model and effort of the
role file's ``- **Launch default:**`` line (W2-33's line form). Verify: a planted ticket whose role file says
``model claude-sonnet-5-5, effort high``: the plan prints that model and effort; a role file without the line fails
the plan naming the file".

The interface (the ticket, the CTO at claim; DEC-1167 (2) narrows it to the default line only):
``gov launch --plan <role> <ticket>`` prints one line ``model <id>, effort <e>``, read from the role file's
``- **Launch default:**`` line, and exits 0. It starts nothing: no session, no launch record, no CLI run. A role file
without the line, or with a malformed one, refuses with ``LAUNCH_REFUSED`` naming the role file's path, exit 1
(P-6 (a), the CTO, recorded in the ticket: like every ``LAUNCH_REFUSED`` through ``gov``; 2 is kept for usage
errors). Nothing here reads a ``Launch by criticality`` line (W2-184's).

Each case plants its own project (``w2_60a_support.make_project``) with the role file it names committed, and the
role's template copies under ``.claude/templates/`` (every launch needs its role's copy since the W2-153 merge), so a
plan is never refused for a reason that is not its own. The stand-in CLI is installed, so a plan that started a
session or ran the CLI at all would be seen in its log.
"""

from __future__ import annotations

import pytest

import w2_60a_support as s

PLAN_ROLES_REL = s.ROLES_REL  # template/governance/kernel/roles, the fixture project's layout

# The role template copies a launch hands the session (W2-153 S1): all eight, any bytes.
TEMPLATE_STEMS = ("brief", "role-research", "role-product-spec", "role-test-designer", "role-engineer",
                  "role-reviewer", "role-lead", "role-cto")
TEMPLATE_FILES = {f".claude/templates/{stem}.md": f"---\nname: {stem}\n---\n# W2-60a plan fixture template {stem}\n"
                  for stem in TEMPLATE_STEMS}


@pytest.fixture
def planted(sandbox):
    """``planted({role: default line or ""})``: the fixture project with each named role's role file carrying that
    default line (``""`` for none), committed with the template copies; returns ``(project, cli)``."""

    def _planted(defaults):
        extra = dict(TEMPLATE_FILES)
        for role, line in defaults.items():
            extra[f"{PLAN_ROLES_REL}/{role}.md"] = s.role_text(role, default=line)
        project = s.make_project(sandbox, extra=extra)
        return project, s.install_stand_in_cli(sandbox)

    return _planted


def _plan(sandbox, project, role, ticket=None):
    tk = (ticket or s.TICKET_OF[role]).tk
    return s.run_gov(sandbox, project, "launch", "--plan", role, tk)


def _launch_temp_folders(sandbox):
    return sorted(path.name for path in sandbox.tmpdir.iterdir() if path.name.startswith("gov-launch-"))


def _assert_nothing_started(sandbox, cli, run):
    assert s.calls(cli) == [], f"the plan ran the CLI ({len(s.calls(cli))} call(s))\n{run.describe()}"
    records = s._listing(sandbox.records)
    assert records == {}, f"the plan wrote launch records {sorted(records)}\n{run.describe()}"
    left = _launch_temp_folders(sandbox)
    assert left == [], f"the plan left session temp folders {left} under {sandbox.tmpdir}\n{run.describe()}"


def _printed_lines(run):
    return [line for line in run.stdout.splitlines() if line.strip()]


# --------------------------------------------------------------------------
# The plan prints the role file's default line
# --------------------------------------------------------------------------

def test_s12_the_plan_prints_the_role_file_s_sonnet_high_and_starts_nothing(sandbox, planted):
    """The KPI's own example: the engineer's role file says ``model claude-sonnet-5-5, effort high`` (the fixture
    engineer's usual default is Opus, so the value is seen to come from this file)."""
    project, cli = planted({s.ENGINEER: s.default_line(s.SONNET, "high")})
    run = _plan(sandbox, project, s.ENGINEER)
    assert run.returncode == 0, f"the plan did not exit 0\n{run.describe()}"
    assert _printed_lines(run) == ["model claude-sonnet-5-5, effort high"], (
        f"the plan did not print the one line 'model claude-sonnet-5-5, effort high'\n{run.describe()}")
    _assert_nothing_started(sandbox, cli, run)


PAIRS = {
    "research-haiku-max": (s.RESEARCH, s.HAIKU, "max"),
    "product-spec-opus-low": (s.PRODUCT_SPEC, s.OPUS, "low"),
    "test-designer-sonnet-xhigh": (s.TEST_DESIGNER, s.SONNET, "xhigh"),
    "auditor-opus-medium": (s.AUDITOR, s.OPUS, "medium"),
}


@pytest.mark.parametrize("case", sorted(PAIRS))
def test_s12_the_plan_prints_another_role_s_model_and_effort_from_its_file(sandbox, planted, case):
    """Other roles, models and efforts (none the fixture role's usual pair): what is printed is what the file says."""
    role, model, effort = PAIRS[case]
    project, cli = planted({role: s.default_line(model, effort)})
    run = _plan(sandbox, project, role)
    assert run.returncode == 0, f"the plan for {role} did not exit 0\n{run.describe()}"
    assert _printed_lines(run) == [f"model {model}, effort {effort}"], (
        f"the plan for {role} did not print the one line 'model {model}, effort {effort}'\n{run.describe()}")
    _assert_nothing_started(sandbox, cli, run)


def test_s12_the_plan_reads_the_role_file_as_it_is_now(sandbox, planted):
    """The same role and ticket planned twice, the role file's line changed between: the second plan prints the new
    pair, so the value is read from the file at each plan, not kept from before."""
    project, cli = planted({s.ENGINEER: s.default_line(s.SONNET, "high")})
    first = _plan(sandbox, project, s.ENGINEER)
    assert first.returncode == 0 and _printed_lines(first) == [f"model {s.SONNET}, effort high"], first.describe()
    s.write_role(project, s.ENGINEER, default=s.default_line(s.OPUS, "max"))
    second = _plan(sandbox, project, s.ENGINEER)
    assert second.returncode == 0, f"the second plan did not exit 0\n{second.describe()}"
    assert _printed_lines(second) == [f"model {s.OPUS}, effort max"], (
        f"the second plan did not print the role file's new line\n{second.describe()}")
    _assert_nothing_started(sandbox, cli, second)


# --------------------------------------------------------------------------
# A role file without the line fails the plan, naming the file
# --------------------------------------------------------------------------

def _assert_plan_refused(sandbox, cli, run, role, why):
    """P-6 (a): the plan's refusal is ``LAUNCH_REFUSED`` naming the role file's path, exit 1, no model line, nothing
    started."""
    said = run.stderr + "\n" + run.stdout
    rel = f"{PLAN_ROLES_REL}/{role}.md"
    assert run.returncode == 1, f"the plan {why} did not exit 1 (P-6 (a))\n{run.describe()}"
    assert "LAUNCH_REFUSED" in said, f"the plan's refusal does not say LAUNCH_REFUSED\n{run.describe()}"
    assert rel in said, f"the plan's refusal does not name the role file {rel}\n{run.describe()}"
    assert not any(line.startswith("model ") for line in run.stdout.splitlines()), (
        f"the refused plan still printed a model line\n{run.describe()}")
    _assert_nothing_started(sandbox, cli, run)


@pytest.mark.parametrize("role", (s.ENGINEER, s.RESEARCH))
def test_s12_a_role_file_without_the_default_line_fails_the_plan_naming_the_file(sandbox, planted, role):
    project, cli = planted({role: ""})
    _assert_plan_refused(sandbox, cli, _plan(sandbox, project, role), role, "without a default line")


def test_s12_a_malformed_default_line_fails_the_plan_naming_the_file(sandbox, planted):
    """The interface: a malformed default line fails the plan as a missing one does. ``model sonnet, effort high``:
    an alias, not a ``claude-`` model id (W2-33's line form; the launch refuses it too)."""
    project, cli = planted({s.ENGINEER: "- **Launch default:** model sonnet, effort high"})
    _assert_plan_refused(sandbox, cli, _plan(sandbox, project, s.ENGINEER), s.ENGINEER, "with a malformed default line")
