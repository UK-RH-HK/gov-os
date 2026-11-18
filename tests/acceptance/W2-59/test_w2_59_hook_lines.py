"""W2-59 KPI success 2: the hook command lines call the pin's environment (DEC-822 step 2).

Every command line of this repository's ``.rulesync/hooks.jsonc`` starts a governance program; each must start it
with the pin's interpreter and package: not with the project's ``src`` on the import path, not with whichever
``python3`` is first on ``PATH``, and with no versioned pin path written in the line (the pin's path names a
version and moves with each re-pin).

The stand-in pin is reachable the way the owner's pin is: a link at ``<HOME>/.local/bin/gov`` to its ``bin/gov``,
with that ``.local/bin`` folder first on ``PATH`` and ``HOME`` a temporary folder, so the case does not fix which of
the two the line uses. A decoy ``python3`` comes next on ``PATH``. Each line is run through ``sh -c`` in a temporary
project that holds the kernel's hook programs, with ``CLAUDE_PROJECT_DIR`` set to it.

(Retired with the guard, EMERGENCY-2 6.1, DAEO-gr7t: the never-fail-open cases, for the preToolUse line and the
after-call lines of the containment check, and the editable-install rollback case of the preToolUse line.)
Never fail open, as it was: with no pin to be found, the preToolUse line must block the call (Claude Code blocks on exit 2 or
a deny decision; any other non-zero exit lets the call proceed), and the after-call lines must not end silently.

Rewrite-Reason: DEC-953 item 2 (W2-90, DEC-957, DEC-906). Since ACT 1 this repository's source holds five lines, its
preToolUse line running its own five-rule hook. The case that counted the seven governance lines now counts them in
the hook source of a project generated from the template, where the kernel's lines are (``.rulesync/hooks.jsonc`` as
Copier puts it there). The cases on the pin's interpreter and package stay on this repository's lines: the kernel's
lines start ``python3`` and carry no pin (``tests/acceptance/W2-90/README.md``).

Rewrite-Reason: DEC-953 item 2 (W2-90b, DEC-965 item 4, DEC-999 item 1). Since W2-106 the template's three guard lines
(preToolUse, postToolUse, postToolUseFailure) take the pinned form. Those three events' ids are parametrized over the
template's lines (``template/.rulesync/hooks.jsonc``, the kernel's wiring), each run in a project holding the kernel's
programs where a product has them (``governance/kernel/hooks/``): the preToolUse ids no longer run this repository's
five-rule line, and the postToolUse and postToolUseFailure ids ACT 1 removed exist again, so the after-call case's
parameter list is no longer empty. The four lifecycle lines' ids stay on this repository's lines: the template's
lifecycle lines keep DEC-608's plain form by DEC-917, so the same verdict has no kernel line to judge
(``tests/acceptance/W2-90b/README.md``).

Rewrite-Reason: DEC-1167 (4), DEC-1156 (7) (W2-185 run 2). The template's ``postToolUse`` holds two entries, the
guard's (``posttooluse.py``) and the context watch's (``context_watch.py``), so the generated project's source holds
eight command lines for the kernel's seven hook programs. The seven-lines case counts the programs the lines start;
the case that the program imports the pin's package is judged for a program that imports it, and for the context
watch (standard library only) by the pin's interpreter and the project's ``src`` staying out of the import path.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import w2_59_support as support

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "W2-90"))

import w2_90_kernel_wiring as kernel_wiring  # noqa: E402

# W2-90b: the guard and containment lines are the template's (W2-106 pinned them); the lifecycle lines this
# repository's (the template's keep DEC-608's plain form, DEC-917).
ENTRIES = kernel_wiring.template_hook_entries() + [
    entry for entry in support.hook_entries() if entry[0] not in kernel_wiring.KERNEL_GUARD_EVENTS]
IDS = [f"{event}[{index}]" for event, index, _ in ENTRIES]

# The events whose program imports the governance package for an engineer's call with a ticket. The subagentStop
# program imports none: only its interpreter is measured.
IMPORTS_GOV = {"preToolUse", "postToolUse", "postToolUseFailure", "preCompact", "sessionStart", "stop"}
# The programs that put the project's ``src`` on their own import path when the folder exists (outside this ticket's
# allowed paths: package P-W2-59-1). Their line is measured in a project without ``src/``.
PROGRAM_ADDS_SRC = {"preCompact", "sessionStart"}
VERSIONED_PIN = re.compile(r"pin-[0-9a-f]{7,40}")


# Rewrite-Reason: DEC-1167 (4), DEC-1156 (7) (W2-185 run 2). The template's ``postToolUse`` holds a second entry beside
# the guard's: the context watch (``context_watch.py``), whose program imports only the standard library. Which
# programs import the governance package is read from the program itself, not from its event.
def _program_of(command):
    found = re.search(r"/hooks/([A-Za-z_]+\.py)", command)
    return found.group(1) if found else None


def imports_only_the_standard_library(command):
    """Whether the kernel program the line starts imports no package but the standard library and the kernel's own
    hooks (read from its syntax tree). ``context_watch`` reads ``precompact`` when an orchestrator's session needs its
    CHECKPOINT's path; that is the kernel's own module, so the program imports no governance package for any
    other session."""
    folder = Path(__file__).resolve().parents[3] / "template" / "governance" / "kernel" / "hooks"
    name = _program_of(command)
    if not name or not (folder / name).is_file():
        return False
    roots = set()
    for node in ast.walk(ast.parse((folder / name).read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            roots |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return all(root in sys.stdlib_module_names or (folder / f"{root}.py").is_file() for root in roots)


@pytest.mark.parametrize("event,index,entry", ENTRIES, ids=IDS)
def test_the_line_names_no_versioned_pin_path_and_puts_no_project_src_on_the_import_path(event, index, entry):
    command = entry["command"]
    assert not VERSIONED_PIN.search(command), (
        f"{event}[{index}] writes a versioned pin path, which moves with each re-pin: {command!r}")
    assert "/.local/share/gov-os/pin-" not in command, f"{event}[{index}] names a pin by its version: {command!r}"
    assert not re.search(r"PYTHONPATH=[^ ]*(\$CLAUDE_PROJECT_DIR|\$\{CLAUDE_PROJECT_DIR\}|\bsrc\b)", command), (
        f"{event}[{index}] puts the project's src on the import path: {command!r}")


@pytest.mark.parametrize("event,index,entry", ENTRIES, ids=IDS)
def test_the_line_starts_its_program_with_the_pin_s_interpreter(event, index, entry, pin_markers, tmp_path):
    """The pin's interpreter starts (its instrumentation leaves a marker); the ``python3`` first on ``PATH`` does
    not."""
    box = support.make_box(tmp_path / "box", pin_markers)
    project = kernel_wiring.w2_59_hook_project(entry, tmp_path / "project", box.markers,
                                               with_src=event not in PROGRAM_ADDS_SRC)
    done = support.run_hook_line(entry["command"], event, project, box)
    assert not box.marks("path-python3-"), (
        f"{event}[{index}] started the python3 first on PATH ({box.decoy_bin / 'python3'})\n{done.describe()}")
    assert pin_markers.marks("pin-python-"), (
        f"{event}[{index}] did not start the pin's interpreter ({pin_markers.python}, reached through "
        f"{box.local_bin / 'gov'})\n{done.describe()}")


@pytest.mark.parametrize("event,index,entry", [e for e in ENTRIES if e[0] in IMPORTS_GOV],
                         ids=[i for i, e in zip(IDS, ENTRIES) if e[0] in IMPORTS_GOV])
def test_the_line_s_program_imports_the_pin_s_package_not_the_project_s_src(
        event, index, entry, pin_markers, tmp_path):
    """The program's governance code is the pin's installed package; the project's own ``src/gov`` is not imported
    (preCompact and sessionStart are measured in a project without ``src/``: package P-W2-59-1). A program that
    imports only the standard library (the context watch) imports no package: the pin's interpreter starts it, and
    the project's ``src/gov`` is still not imported."""
    box = support.make_box(tmp_path / "box", pin_markers)
    project = kernel_wiring.w2_59_hook_project(entry, tmp_path / "project", box.markers,
                                               with_src=event not in PROGRAM_ADDS_SRC)
    done = support.run_hook_line(entry["command"], event, project, box)
    assert not box.marks("tree-gov-"), (
        f"{event}[{index}] imported the project's own {project}/src/gov\n{done.describe()}")
    if imports_only_the_standard_library(entry["command"]):
        assert pin_markers.marks("pin-python-"), (
            f"{event}[{index}] did not start the pin's interpreter ({pin_markers.python})\n{done.describe()}")
        return
    assert pin_markers.marks("pin-gov-"), (
        f"{event}[{index}]'s program did not import the pin's installed package ({pin_markers.site / 'gov'})\n"
        f"{done.describe()}")

