"""S6: every command and hook works in a repository whose path contains a space (``~/EXAMIN APP``).

Interface item 7: "every name in ``gov.cli.main`` COMMANDS plus the discovered command modules, each with ``--help``
and with one real read invocation (status, doctor, retrieve, context --dry-run, adopt --lite --stage A0 on a clean
fixture), and the six hooks of ``template/governance/kernel/hooks/`` fed a minimal event JSON, through the settings'
own hook command lines, with ``CLAUDE_PROJECT_DIR`` holding a space."

The same repository is planted twice: in a folder named ``EXAMIN APP`` under ``tmp_path`` and at a path without a
space. Each run must end with the same exit code in both, and print no word-splitting or path error the run without
a space does not print. ``retrieve`` and ``context --dry-run`` are run only outside the launch sandbox (``local_only``,
DEC-1065: no ``gov retrieve`` or ``gov context`` there).
"""

from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest

import w2_23_support as support


def _pair(tmp_path):
    """(the repository at ``EXAMIN APP``, its box), (the same at a path without a space, its box)."""
    made = []
    for folder, box_name in (("EXAMIN APP", "box-spaced"), ("examin-plain", "box-plain")):
        root = support.plant_project(tmp_path / folder, ignored=False)
        support.plant_kernel_hooks(root)
        support.commit_all(root, "the kernel hooks")
        box = support.make_box(tmp_path / box_name)
        support.plant_pinned_gov(box)
        made.append((root, box))
    assert " " in str(made[0][0]) and " " not in str(made[1][0])
    return made


def _command_names():
    done = subprocess.run([sys.executable, "-c", "import json; from gov.cli.main import COMMANDS; "
                           "print(json.dumps([c.name for c in COMMANDS]))"], capture_output=True, text=True,
                          env={"PYTHONPATH": str(support.SRC), "PATH": "/usr/bin:/bin"}, timeout=60)
    assert done.returncode == 0, f"gov.cli.main's COMMANDS cannot be read:\n{done.stderr}"
    reserved = json.loads(done.stdout)
    discovered = sorted(path.parent.name for path in (support.SRC / "gov").glob("*/command.py"))
    return list(dict.fromkeys([*reserved, *discovered]))


def _compare(runs, space_root):
    """runs: label -> (the run at the path with a space, the run without). The differences, named."""
    problems = []
    for label, (spaced, plain) in runs.items():
        if spaced.returncode != plain.returncode:
            problems.append(f"{label}: exit {spaced.returncode} at the path with a space, {plain.returncode} "
                            f"without\n{spaced.describe()}")
        for found in support.path_errors(spaced.stdout + spaced.stderr, plain.stdout + plain.stderr, space_root):
            problems.append(f"{label}: {found}\n{spaced.describe()}")
    return problems


def _both(pair, *args):
    return tuple(support.run_gov(root, box, *args) for root, box in pair)


def test_s6_every_command_answers_help_alike_at_a_path_with_a_space(tmp_path):
    pair = _pair(tmp_path)
    names = _command_names()
    assert "adopt" in names and "status" in names, f"the command list is not read: {names}"
    with ThreadPoolExecutor(max_workers=8) as pool:
        runs = dict(zip(names, pool.map(lambda name: _both(pair, name, "--help"), names)))
    problems = _compare({f"gov {name} --help": run for name, run in runs.items()}, pair[0][0])
    assert not problems, "\n\n".join(problems)


def test_s6_the_read_invocations_exit_alike_at_a_path_with_a_space(tmp_path):
    pair = _pair(tmp_path)
    invocations = (("status", "--json"), ("doctor", "--json"), ("adopt", "--lite", "--stage", "A0", "--json"))
    runs = {f"gov {' '.join(args)}": _both(pair, *args) for args in invocations}
    problems = _compare(runs, pair[0][0])
    assert not problems, "\n\n".join(problems)


@pytest.mark.local_only
def test_s6_retrieve_and_context_exit_alike_at_a_path_with_a_space(tmp_path):
    """Outside the launch sandbox only (DEC-1065); no model is reachable from the planted HOME."""
    pair = _pair(tmp_path)
    invocations = (("retrieve", "where is the guide", "--json"), ("context", "HARB-0001", "--dry-run", "--json"))
    runs = {f"gov {' '.join(args)}": _both(pair, *args) for args in invocations}
    problems = _compare(runs, pair[0][0])
    assert not problems, "\n\n".join(problems)


def test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir(tmp_path):
    pair = _pair(tmp_path)
    events = support.kernel_hook_events()
    scripts = {path.name for path in support.KERNEL_HOOKS.glob("*.py")}
    reached = {name for name in scripts if any(name in command for _, command in events)}
    assert reached == scripts and len(scripts) == 6, \
        f"the settings' hook command lines do not reach the six kernel hooks: {sorted(scripts - reached)}"
    runs = {f"the {event} hook": tuple(support.run_hook(root, box, command, event) for root, box in pair)
            for event, command in events}
    problems = _compare(runs, pair[0][0])
    assert not problems, "\n\n".join(problems)
