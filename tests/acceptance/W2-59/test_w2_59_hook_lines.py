"""W2-59 KPI success 2: the hook command lines call the pin's environment (DEC-822 step 2).

Every command line of this repository's ``.rulesync/hooks.jsonc`` starts a governance program; each must start it
with the pin's interpreter and package: not with the project's ``src`` on the import path, not with whichever
``python3`` is first on ``PATH``, and with no versioned pin path written in the line (the pin's path names a
version and moves with each re-pin).

The stand-in pin is reachable the way the owner's pin is: a link at ``<HOME>/.local/bin/gov`` to its ``bin/gov``,
with that ``.local/bin`` folder first on ``PATH`` and ``HOME`` a temporary folder, so the case does not fix which of
the two the line uses. A decoy ``python3`` comes next on ``PATH``. Each line is run through ``sh -c`` in a temporary
project that holds the kernel's hook programs, with ``CLAUDE_PROJECT_DIR`` set to it.

Never fail open: with no pin to be found, the preToolUse line must block the call (Claude Code blocks on exit 2 or
a deny decision; any other non-zero exit lets the call proceed), and the after-call lines must not end silently.

Rewrite-Reason: DEC-953 item 2 (W2-90, DEC-957, DEC-906). Since ACT 1 this repository's source holds five lines, its
preToolUse line running its own five-rule hook. The case that counted the seven governance lines now counts them in
the hook source of a project generated from the template, where the kernel's lines are (``.rulesync/hooks.jsonc`` as
Copier puts it there). The cases on the pin's interpreter and package stay on this repository's lines: the kernel's
lines start ``python3`` and carry no pin (``tests/acceptance/W2-90/README.md``).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import w2_59_support as support

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "W2-90"))

import w2_90_kernel_wiring as kernel_wiring  # noqa: E402

ENTRIES = support.hook_entries()
IDS = [f"{event}[{index}]" for event, index, _ in ENTRIES]

# The events whose program imports the governance package for an engineer's call with a ticket. The subagentStop
# program imports none: only its interpreter is measured.
IMPORTS_GOV = {"preToolUse", "postToolUse", "postToolUseFailure", "preCompact", "sessionStart", "stop"}
# The programs that put the project's ``src`` on their own import path when the folder exists (outside this ticket's
# allowed paths: package P-W2-59-1). Their line is measured in a project without ``src/``.
PROGRAM_ADDS_SRC = {"preCompact", "sessionStart"}
VERSIONED_PIN = re.compile(r"pin-[0-9a-f]{7,40}")


@pytest.fixture(scope="module")
def kernel_entries(tmp_path_factory):
    """(event, index, entry) for every command entry of a generated project's rulesync hooks source (W2-90)."""
    try:
        project = kernel_wiring.generate_project(tmp_path_factory.mktemp("w2-90-w2-59-kernel"))
    except kernel_wiring.GenerationFailed as exc:
        pytest.fail(str(exc), pytrace=False)
    source = support.load_jsonc(project / kernel_wiring.HOOK_SOURCE_REL)
    return [(event, index, entry) for event, entries in (source.get("hooks") or {}).items()
            for index, entry in enumerate(entries or []) if isinstance(entry, dict) and entry.get("type") == "command"]


def test_the_source_holds_the_seven_governance_hook_lines(kernel_entries):
    """The cases below cover every command line of the source; each starts a kernel hook program.

    The source is the generated project's (W2-90): the kernel's seven lines."""
    ENTRIES = kernel_entries
    assert len(ENTRIES) == 7, f"{support.HOOK_SOURCE_REL} holds {len(ENTRIES)} command entries; seven are expected"
    for event, index, entry in ENTRIES:
        assert "governance/kernel/hooks/" in entry["command"], (
            f"{event}[{index}] starts no kernel hook program: {entry['command']!r}")


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
    project = support.hook_project(tmp_path / "project", box.markers, with_src=event not in PROGRAM_ADDS_SRC)
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
    (preCompact and sessionStart are measured in a project without ``src/``: package P-W2-59-1)."""
    box = support.make_box(tmp_path / "box", pin_markers)
    project = support.hook_project(tmp_path / "project", box.markers, with_src=event not in PROGRAM_ADDS_SRC)
    done = support.run_hook_line(entry["command"], event, project, box)
    assert not box.marks("tree-gov-"), (
        f"{event}[{index}] imported the project's own {project}/src/gov\n{done.describe()}")
    assert pin_markers.marks("pin-gov-"), (
        f"{event}[{index}]'s program did not import the pin's installed package ({pin_markers.site / 'gov'})\n"
        f"{done.describe()}")


def _without_pin(tmp_path):
    box = support.make_box(tmp_path / "box", None)
    path = f"{box.local_bin}:{box.decoy_bin}:{support.SYSTEM_PATH}"
    check = subprocess.run(["sh", "-c", "command -v gov"], env={"PATH": path, "HOME": str(box.home)},
                           capture_output=True, text=True)
    assert check.returncode != 0, f"a gov is on the case's PATH although no pin is installed: {check.stdout}"
    project = support.hook_project(tmp_path / "project", box.markers, with_src=True)
    return box, project, path


@pytest.mark.parametrize("event,index,entry", [e for e in ENTRIES if e[0] == "preToolUse"],
                         ids=[i for i, e in zip(IDS, ENTRIES) if e[0] == "preToolUse"])
def test_without_a_pin_the_pretooluse_line_blocks_the_call(event, index, entry, tmp_path):
    """No ``gov`` link and no ``gov`` on ``PATH``: the call is blocked (exit 2 or a deny decision), and neither the
    project's ``src`` nor the ``python3`` first on ``PATH`` stands in for the pin."""
    box, project, path = _without_pin(tmp_path)
    done = support.run_hook_line(entry["command"], event, project, box, path=path)
    assert support.denies(done), (
        f"with no pin to be found, {event}[{index}] lets the call through (exit {done.returncode}; only exit 2 or "
        f"a deny decision blocks)\n{done.describe()}")
    assert not box.marks("tree-gov-"), (
        f"with no pin, {event}[{index}] fell back to the project's own src/gov\n{done.describe()}")
    assert not box.marks("path-python3-"), (
        f"with no pin, {event}[{index}] fell back to the python3 first on PATH\n{done.describe()}")


@pytest.mark.parametrize("event,index,entry", [e for e in ENTRIES if e[0] in ("postToolUse", "postToolUseFailure")],
                         ids=[i for i, e in zip(IDS, ENTRIES) if e[0] in ("postToolUse", "postToolUseFailure")])
def test_without_a_pin_the_after_call_lines_do_not_end_silently(event, index, entry, tmp_path):
    """The containment check cannot run without the pin: the line ends with an error (non-zero), never as a
    silent success, and no other install stands in for the pin."""
    box, project, path = _without_pin(tmp_path)
    done = support.run_hook_line(entry["command"], event, project, box, path=path)
    assert done.returncode not in (0, None), (
        f"with no pin to be found, {event}[{index}] ends as a silent success\n{done.describe()}")
    assert not box.marks("tree-gov-"), (
        f"with no pin, {event}[{index}] fell back to the project's own src/gov\n{done.describe()}")
    assert not box.marks("path-python3-"), (
        f"with no pin, {event}[{index}] fell back to the python3 first on PATH\n{done.describe()}")


@pytest.mark.parametrize("event,index,entry", [e for e in ENTRIES if e[0] == "preToolUse"],
                         ids=[i for i, e in zip(IDS, ENTRIES) if e[0] == "preToolUse"])
def test_the_line_follows_the_owner_s_rollback_to_an_editable_install(event, index, entry, tmp_path):
    """The owner's documented rollback replaces the link by an editable install's own ``gov`` script (DEC-605:
    ``pip install --user -e``: a script at ``~/.local/bin/gov`` whose first line names the system interpreter, the
    package found through the user site folder). The line then starts that install's interpreter, not the
    ``python3`` first on ``PATH``, and not with the project's ``src``."""
    box = support.make_box(tmp_path / "box", None)
    rollback = box.local_bin / "gov"
    rollback.write_text(f"#!{support.REAL_PYTHON}\nimport sys\nfrom gov.cli.main import main\nsys.exit(main())\n",
                        encoding="utf-8")
    rollback.chmod(0o755)
    env = support.base_env(box.home, support.SYSTEM_PATH)
    site = subprocess.run([support.REAL_PYTHON, "-c", "import site; print(site.getusersitepackages())"],
                          env=env, capture_output=True, text=True, check=True).stdout.strip()
    assert site.startswith(str(box.home) + os.sep), f"the user site folder {site} is not under the case's home"
    os.makedirs(site, exist_ok=True)
    with open(os.path.join(site, "w259_rollback.pth"), "w", encoding="utf-8") as pth:
        pth.write(f"{support.SRC}\n")
        pth.write(f"import os; open(os.path.join({str(box.markers)!r}, 'rollback-python-%d' % os.getpid()), "
                  f"'w').close()\n")
    project = support.hook_project(tmp_path / "project", box.markers, with_src=True)
    done = support.run_hook_line(entry["command"], event, project, box)
    assert not box.marks("path-python3-"), (
        f"after the rollback, {event}[{index}] started the python3 first on PATH\n{done.describe()}")
    assert not box.marks("tree-gov-"), (
        f"after the rollback, {event}[{index}] imported the project's own src/gov\n{done.describe()}")
    assert box.marks("rollback-python-"), (
        f"after the rollback, {event}[{index}] did not start the editable install's interpreter "
        f"({support.REAL_PYTHON}, named by {rollback})\n{done.describe()}")
