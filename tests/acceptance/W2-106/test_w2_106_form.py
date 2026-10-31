"""W2-106 KPI success 1 (the form) and its failure line; KPI success 4 (the two template files in step).

KPI success 1: "Each of the template's hook lines (pre-tool and the two post-tool lines, in
``template/governance/kernel/settings.json`` and their rulesync source ``template/.rulesync/hooks.jsonc``) takes this
repository's pinned form (DEC-822, W2-59): it finds the installed gov (``$HOME/.local/bin/gov``, else ``gov`` on
PATH), reads the interpreter its first line names, and runs the hook with that interpreter and ``-E``; the line's exit
codes are kept (0 and 2 pass through; any other ends in a refusal) [DEC-966 item 2, DEC-822]".
Failure: "A template hook line that runs a bare ``python3``, or one without ``-E``."

KPI success 4 (first half): "A generated project's hook lines equal the template's source after ``rulesync
generate`` (the two sources stay in step)". Failure: "The settings and the rulesync source out of step".

These cases read the files; the behaviour of the lines is run in ``test_w2_106_interpreter.py``,
``test_w2_106_fail_closed.py`` and ``test_w2_106_generated_project.py``.
"""

from __future__ import annotations

import pytest

import w2_106_support as support


@pytest.mark.parametrize(("name", "event"), support.LINE_PARAMS, ids=support.LINE_IDS)
def test_the_line_takes_this_repository_s_pinned_form(name, event):
    """The pinned form is given by reference (the KPI names it; DEC-822, W2-59): this repository's own guard line,
    ``.rulesync/hooks.jsonc``'s ``preToolUse`` entry. The template's line is that line exactly, with the program the
    template's line runs, at ``$CLAUDE_PROJECT_DIR/governance/kernel/hooks/<program>`` (where Copier puts it), in the
    place of this repository's program path."""
    line = support.template_line(name, event)
    rel = support.FILES[name]
    paths = sorted(set(support.program_paths(line)))
    assert paths == [support.expected_program_path(event)], (
        f"{rel}, {event}: the line runs {paths or 'no hook program'}; it must run "
        f"{support.expected_program_path(event)} (where Copier puts the kernel's hook programs)\nline: {line}")
    reference = support.reference_line()
    assert support.form_of(line) == support.form_of(reference), (
        f"{rel}, {event}: the line is not this repository's pinned form (DEC-822, W2-59), the program path aside.\n"
        f"line:      {support.form_of(line)}\n"
        f"reference: {support.form_of(reference)}  ({support.REFERENCE_SOURCE_REL}, {support.REFERENCE_EVENT})")


@pytest.mark.parametrize(("name", "event"), support.LINE_PARAMS, ids=support.LINE_IDS)
def test_the_line_runs_no_bare_python3_and_passes_minus_e_to_its_interpreter(name, event):
    """The failure line in words: no line runs a bare ``python3`` (or ``python``) found on ``PATH``, and each passes
    ``-E`` to the interpreter it starts. (That the interpreter started is the installed gov's, and that ``-E`` is in
    force in it, is run in ``test_w2_106_interpreter.py``.)"""
    line = support.template_line(name, event)
    rel = support.FILES[name]
    bare = support.BARE_PYTHON.findall(line)
    assert not bare, f"{rel}, {event}: the line runs a bare {bare[0]!r} found on PATH (DEC-966 item 2)\nline: {line}"
    assert support.MINUS_E.search(line), f"{rel}, {event}: the line passes no -E to its interpreter\nline: {line}"


@pytest.mark.parametrize("event", support.EVENTS)
def test_the_settings_and_the_rulesync_source_hold_the_same_guard_line(event):
    """The kernel template's settings and the template's rulesync source hold the same line under each guard event,
    the same string (DEC-913 item 1, DEC-917): the two files stay in step."""
    settings = support.template_line("settings", event)
    source = support.template_line("source", event)
    assert settings == source, (
        f"{event}: the two template files are out of step\n{support.TEMPLATE_SETTINGS_REL}: {settings}\n"
        f"{support.TEMPLATE_SOURCE_REL}: {source}")
