"""W2-106 KPI success 3 and 4, in a project generated from the template.

KPI success 3: "A session's PYTHONPATH cannot change which guard code runs: in a generated project, a planted
PYTHONPATH pointing at an edited copy of gov that would allow a refused write, the hook still refuses it (the
measurement of P-W2-90-1 P1-B, now refused) [DEC-966 item 2, DEC-957]". Failure: "An edited gov on PYTHONPATH lets a
refused write through."

KPI success 4: "A generated project's hook lines equal the template's source after ``rulesync generate`` (the two
sources stay in step), and the template's own suites (W1-38, W1-39) pass [DEC-966 item 2, DEC-616]". Failure: "The
settings and the rulesync source out of step, or W1-38 or W1-39 red." (W1-38 and W1-39 are run as suites of their
own; README.)

**The generated project** (W2-90's ``generate_project``): ``copier.yml`` and ``template/`` assembled file by file into
a temporary template source (W1-39's ``assemble_source``), ``copier copy --defaults --trust`` (W1-39's
``create_project_and_run``), then ``rulesync generate`` (W1-38's ``run_rulesync_generate``) writes its
``.claude/settings.json``. The kernel's real hook programs are at ``governance/kernel/hooks/``.

**The planted PYTHONPATH** (P-W2-90-1 P1-B's measurement, the shape of a ticket worktree): the project's ``src/``
holds an edited ``gov`` whose guard allows every call (W2-59's ``worker_import_path_files``): importing it leaves
``tree-gov-<pid>``, and a ``sitecustomize.py`` beside it leaves ``tree-site-<pid>`` whenever an interpreter starts
with the folder on its import path. The session's ``PYTHONPATH`` names that folder. The refused write is an
engineer's ``Write`` outside the ticket's paths (W2-59's ``refused_write``), which the pin's guard denies.
"""

from __future__ import annotations

import pytest

import w2_106_support as support

import w2_90_kernel_wiring as kernel_wiring  # noqa: E402  (on the path through w2_106_support)


@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    """A project generated from the template, its ``.claude/settings.json`` written by rulesync, with an edited
    ``gov`` planted in its ``src/`` (committed), and the folder its markers go to."""
    base = tmp_path_factory.mktemp("w2106-generated")
    try:
        project = kernel_wiring.generate_project(base)
    except kernel_wiring.GenerationFailed as exc:
        pytest.fail(str(exc), pytrace=False)
    markers = base / "edited-gov-markers"
    markers.mkdir()
    kernel_wiring.plant(project, support.pin_support.worker_import_path_files(markers),
                        "an edited copy of gov under src/ (P-W2-90-1 P1-B)")
    return project, markers


@pytest.fixture
def edited(generated):
    project, markers = generated
    for path in markers.iterdir():
        path.unlink()
    return project, markers


def _generated_line(project, event):
    settings = kernel_wiring.load_settings(project)
    commands = support.settings_commands(settings, event, support.PROGRAM_OF[event])
    assert len(commands) == 1, (f"the generated {kernel_wiring.SETTINGS_REL} registers {len(commands)} {event} lines "
                                f"running {support.PROGRAM_OF[event]}; one is expected: {commands}")
    return commands[0]


def _home_with_the_pin(box, pin):
    support.link_gov(pin.gov, box.home_gov)
    return support.path_of(box.decoy_bin)


def _tree_marks(markers):
    return sorted(path.name for path in markers.iterdir())


def test_a_planted_pythonpath_to_an_edited_gov_does_not_let_a_refused_write_through(edited, box, pin):
    """The generated PreToolUse line, an engineer's Write outside the ticket's paths, the session's ``PYTHONPATH``
    naming the project's ``src/`` with the edited gov: the call is refused (exit 2, or a deny decision with exit 0),
    the pin's guard decided, and the edited gov was never imported."""
    project, markers = edited
    line = _generated_line(project, "PreToolUse")
    path = _home_with_the_pin(box, pin)
    done = support.run_line(line, box, path=path, project=project, payload=support.pin_support.refused_write(project),
                            inherited={"PYTHONPATH": str(project / "src")})
    assert support.denies(done), (
        f"fail-open: with PYTHONPATH naming an edited gov, the generated PreToolUse line let a refused write through "
        f"(P-W2-90-1 P1-B)\n{done.describe()}\nedited gov's markers: {_tree_marks(markers)}")
    assert not _tree_marks(markers), (
        f"the planted PYTHONPATH reached the guard's interpreter: {_tree_marks(markers)}\n{done.describe()}")
    assert pin.marks("pin-gov-"), f"the pin's guard did not decide (its package was never imported)\n{done.describe()}"


def test_without_the_planted_pythonpath_the_pin_s_guard_refuses_the_same_write(edited, box, pin):
    """The control: the same line and write with no ``PYTHONPATH``. The pin's guard refuses it, so the case above
    measures the variable and nothing else."""
    project, markers = edited
    line = _generated_line(project, "PreToolUse")
    path = _home_with_the_pin(box, pin)
    done = support.run_line(line, box, path=path, project=project, payload=support.pin_support.refused_write(project))
    assert support.denies(done), f"the pin's guard did not refuse the write\n{done.describe()}"
    assert pin.marks("pin-gov-"), f"the pin's guard did not decide (its package was never imported)\n{done.describe()}"
    assert not _tree_marks(markers), f"the edited gov was imported: {_tree_marks(markers)}\n{done.describe()}"


@pytest.mark.parametrize("event", ["PostToolUse", "PostToolUseFailure"])
def test_a_planted_pythonpath_does_not_reach_the_containment_program(event, edited, box, pin):
    """The generated post-tool line (on Bash), the session's ``PYTHONPATH`` naming the edited gov: the containment
    program runs the pin's package, and no interpreter it starts has the planted folder on its import path."""
    project, markers = edited
    line = _generated_line(project, event)
    path = _home_with_the_pin(box, pin)
    done = support.run_line(line, box, path=path, project=project, event=event,
                            payload=support.hook_input(event, project), inherited={"PYTHONPATH": str(project / "src")})
    assert not _tree_marks(markers), (
        f"{event}: the planted PYTHONPATH changed the containment program's code: {_tree_marks(markers)}\n"
        f"{done.describe()}")
    assert pin.marks("pin-gov-"), f"{event}: the containment program did not run the pin's package\n{done.describe()}"
    assert not box.marks("path-python"), f"{event}: the line started the decoy python3 first on PATH\n" \
                                         f"{done.describe()}"


@pytest.mark.parametrize("event", support.EVENTS)
def test_the_generated_settings_hold_the_template_s_guard_line(event, generated):
    """After ``rulesync generate``, the generated ``.claude/settings.json`` registers under each guard event the
    template's line, the same string as the template's rulesync source and the kernel template's settings."""
    project, _markers = generated
    generated_line = _generated_line(project, event)
    source = support.template_line("source", event)
    settings = support.template_line("settings", event)
    assert generated_line == source == settings, (
        f"{event}: out of step after rulesync generate\ngenerated: {generated_line}\n"
        f"{support.TEMPLATE_SOURCE_REL}: {source}\n{support.TEMPLATE_SETTINGS_REL}: {settings}")
