"""S1: a project setting chooses the close (``close: scoped``, the default of a new project, or ``close: strict``);
this repository runs scoped.

The strict half (today's verdicts, every lifted gate still built) is in ``test_w2_115_strict.py``; the scoped
project's selection-only run in ``test_w2_115_selection.py``.

Red on today's code: no ``close.yaml`` exists in the template or in this repository, and today's close ignores the
setting (it neither records ``close: scoped`` nor refuses an unreadable value).
"""

import pytest
import yaml

import w2_115_support as support


def _setting(path):
    assert path.is_file(), f"{path} does not exist"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path} holds no mapping: {data!r}"
    return data.get("close")


def test_a_new_project_s_config_holds_close_scoped():
    """S1: the template's copy (what a new project gets) holds ``close: scoped``."""
    assert _setting(support.REPO_ROOT / support.TEMPLATE_CLOSE_YAML_REL) == support.SCOPED


def test_this_repository_s_config_reads_close_scoped():
    """S1: this repository's own ``governance/project/close.yaml`` reads ``close: scoped``."""
    assert _setting(support.REPO_ROOT / support.CLOSE_YAML_REL) == support.SCOPED


def test_a_scoped_project_s_close_is_recorded_scoped(make_project, sandbox):
    """S1: a planted project with ``close: scoped`` closes scoped: its record says ``close: scoped``."""
    project = make_project(close=support.SCOPED)
    project.work({support.WIDGET: "# the widget, CHANGED\n"})
    project.ready(sandbox)
    support.passed(project.close(sandbox))
    assert project.record().get("close") == support.SCOPED
    assert not project.ran(support.case_of("W2-dd")), "the scoped close ran a suite nothing reaches"


@pytest.mark.parametrize("text", ["close: fast\n", "close: [scoped\n", "close:\n  - scoped\n"],
                         ids=["another_value", "unreadable", "not_a_word"])
def test_an_unreadable_or_other_setting_is_refused(make_project, sandbox, text):
    """S1: an unreadable ``close.yaml`` or another value is refused (fail closed): the ticket does not close and the
    refusal names the file."""
    project = make_project(close=text)
    project.work({support.WIDGET: "# the widget, CHANGED\n"})
    project.ready(sandbox)
    run = project.close(sandbox)
    said = support.assert_refused(run)
    assert "close.yaml" in said, f"the refusal does not name close.yaml\n{run.describe()}"
    assert project.ticket_status() == "in_progress", "the ticket closed on an unreadable setting"
