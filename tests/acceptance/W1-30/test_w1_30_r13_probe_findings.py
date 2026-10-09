"""Round 13, piece 4: five findings of the probe of the parallel run (DEC-555).

DEC-555 names them: "**Finding 1.** A run of the declared cases that ends with exit code 0 and no result (a
case that ends its own process with 0) is accepted, because the parallel run's passes cover it. **Finding 2.**
A file in the project named like the close's own plugin replaces it [...], so a ticket's own commit can keep a
failing case out of every run. [...] **finding 3** (parallel workers outlive a run cut at the time limit and
can still write into the project), **finding 4** (a list entry that names an existing file without a case
refuses nothing, against DEC-549's fourth point) and the first shape of **finding 7** (a byte in the list that
is not UTF-8 ends in a traceback)."

What each becomes (README, round 13, piece 4):

1. A run of the declared cases that ends with exit code 0 and states no result refuses the close with a
   finding, whatever the parallel run passed.
2. A file of the project named like the close's own plugin does not replace it: the close's own plugin is
   loaded, or the close refuses. A failing case such a file keeps out of every run still fails the close.
3. After ``gov close`` has returned from a run cut at the time limit, no process of that run is alive and
   nothing of that run writes into the project.
4. A list entry that names an existing file with no case in it refuses the close with a finding that names
   the entry (DEC-549, fourth point).
5. A list with a byte that is not UTF-8 is a refusal with a finding of its own that names the list
   (``SERIAL_ONLY_LIST_UNREADABLE``, proposed), not a traceback.
"""

import json
import os
import time
from pathlib import Path

import pytest

import w1_30_support as support

TICKET = "PROJ-prfd"
WBS = "W1-prfd"
ACCEPTANCE = f"tests/acceptance/{WBS}"
FEATURE = "src/example/feature.py"

# Proposed: the code of the finding for a list that cannot be read as text (settlement 28).
LIST_UNREADABLE = "SERIAL_ONLY_LIST_UNREADABLE"


def _build(project, files, declared=(), allowed_paths=None, more_work=None, list_bytes=None):
    """A ticket ready for its close: the project's serial-only list with ``declared`` entries (the
    orchestrator's commit, before the ticket; ``list_bytes`` writes the list as these bytes), the acceptance
    files ``files`` (``{name: text}``, the test designer's) and the engineer's work (``more_work``:
    ``{path: text}`` beside the feature)."""
    if list_bytes is not None:
        path = project.root / support.SERIAL_ONLY_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(list_bytes)
    elif declared:
        project.write(support.SERIAL_ONLY_REL, "".join(f"{entry}  # latency: planted\n" for entry in declared))
    if list_bytes is not None or declared:
        project.commit("the serial-only list", who=support.ORCHESTRATOR)
    project.add_ticket(TICKET, WBS, allowed_paths=allowed_paths)
    for name, text in files.items():
        project.write(f"{ACCEPTANCE}/{name}", text)
    project.write(FEATURE, "# feature\n")
    for rel, text in (more_work or {}).items():
        project.write(rel, text)
    project.commit("implement", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))
    support.checkpointed(project, TICKET)


PASSING = "def test_pass():\n    assert True\n"
FAILING = "def test_fail():\n    assert False, 'planted failure'\n"


def _refused_with_a_finding(project, run, interface, *named):
    """Exit code 3, each of ``named`` in the answer, counted once, nothing closed. Returns the answer's text."""
    text = support.error_text(support.refused(run, interface, support.EXIT_CHECK_FAILED))
    for name in named:
        assert name in text, f"the refusal does not name {name}\n{run.describe()}"
    assert support.iteration_count(project.root, TICKET) == 1, f"the refusal is not counted once\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    return text


# --------------------------------------------------------------------------
# 1. A run of the declared cases with exit code 0 and no result
# --------------------------------------------------------------------------

ENDS_ITSELF = "import os\n\n\ndef test_a_ends_the_process():\n    os._exit(0)\n"
APART = f"{ACCEPTANCE}/test_apart.py"


@pytest.mark.parametrize("after_it", ["", "\n\ndef test_b_fails():\n    assert False, 'planted failure'\n"],
                         ids=["the only declared case", "a failing declared case follows it"])
def test_a_run_of_the_declared_cases_with_exit_code_0_and_no_result_refuses(after_it, project, sandbox, interface):
    """A declared case ends its own process with exit code 0: the run afterwards states no result. The
    parallel run has a passing case. In the second form a failing case of the same file never ran."""
    _build(project, {"test_pass.py": PASSING, "test_apart.py": ENDS_ITSELF + after_it}, declared=[APART])

    run = support.run_close(project, sandbox, TICKET)

    _refused_with_a_finding(project, run, interface, ACCEPTANCE)


# --------------------------------------------------------------------------
# 2. A file of the project named like the close's own plugin
# --------------------------------------------------------------------------

# The name of the plugin the close gives its parallel run today. The case also asks a close which names it
# gives (``_plugin_names``), so that it follows a plugin that is renamed.
PLUGIN_TODAY = "gov_close_serial_only"

# What a file of the project that took the plugin's place could do: keep the failing case out of the run.
REPLACEMENT = (
    "def pytest_collection_modifyitems(config, items):\n"
    "    out = [item for item in items if 'test_fail' in item.nodeid]\n"
    "    if out:\n"
    "        config.hook.pytest_deselected(items=out)\n"
    "        items[:] = [item for item in items if item not in out]\n"
)


def _plugin_names(base, sandbox, interface):
    """The names of the plugins a close gives the test runner of a project that declares a case, read by that
    project's own tests from the runner's arguments and environment; with today's name."""
    seen = base / "seen"
    seen.mkdir(parents=True)
    scout = support.Project(base / "scout")
    conftest = (
        "import json\nimport os\n\n\n"
        "def pytest_configure(config):\n"
        f"    with open(os.path.join({str(seen)!r}, str(os.getpid())), 'w', encoding='utf-8') as told:\n"
        "        json.dump({'args': [str(a) for a in config.invocation_params.args],\n"
        "                   'env': os.environ.get('PYTEST_PLUGINS', '')}, told)\n"
    )
    _build(scout, {"conftest.py": conftest, "test_pass.py": PASSING,
                   "test_apart.py": "def test_apart():\n    assert True\n"}, declared=[APART])
    support.result_of(support.run_close(scout, sandbox, TICKET), interface)
    names = {PLUGIN_TODAY}
    for path in seen.iterdir():
        told = json.loads(path.read_text(encoding="utf-8"))
        args = told["args"]
        names.update(args[at + 1] for at, arg in enumerate(args[:-1]) if arg == "-p")
        names.update(arg[2:] for arg in args if arg.startswith("-p") and len(arg) > 2)
        names.update(name for name in told["env"].split(",") if name)
    return sorted(name for name in names if not name.startswith("no:"))


def _files_named_like(names, folder):
    """A module for each plugin name under ``folder`` of the project (``""`` is the root), with the packages a
    dotted name needs."""
    files = {}
    for name in names:
        parts = name.split(".")
        for depth in range(1, len(parts)):
            files[folder + "/".join(parts[:depth]) + "/__init__.py"] = ""
        files[folder + "/".join(parts) + ".py"] = REPLACEMENT
    return files


@pytest.mark.parametrize("folder", ["", "src/"], ids=["at the project's root", "under src/"])
def test_a_project_file_named_like_the_closes_plugin_keeps_no_failing_case_out(folder, project, sandbox, interface,
                                                                              tmp_path):
    """The ticket's own commit adds the file; the ticket has a failing acceptance case and declares another
    case, so the close gives its plugin to the parallel run. The close does not close the ticket: it ran the
    failing case, or it refused for the file."""
    planted = _files_named_like(_plugin_names(tmp_path / "names", sandbox, interface), folder)
    _build(project, {"test_pass.py": PASSING, "test_fail.py": FAILING,
                     "test_apart.py": "def test_apart():\n    assert True\n"},
           declared=[APART], allowed_paths=["src/**", *sorted(planted)], more_work=planted)
    assert support.judged_by_w1_50(project, sandbox, support.ticket_commits(project.root, TICKET)) == [], \
        "the fixture is wrong: W1-50's judgement has a finding, so the planted file is not the only way out"

    run = support.run_close(project, sandbox, TICKET)

    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False and run.returncode in (support.EXIT_CHECK_FAILED, support.EXIT_GOV_ERROR), \
        f"the ticket closed although its acceptance case test_fail fails\n{run.describe()}"
    text = support.error_text(envelope["error"])
    assert "test_fail" in text or any(rel in text for rel in planted if rel.endswith(".py") and planted[rel]), \
        f"the refusal names neither the failing case nor the planted file\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


# --------------------------------------------------------------------------
# 3. A run cut at the time limit leaves no process and writes nothing afterwards
# --------------------------------------------------------------------------

LIMIT_S = 5
SLEEP_S = 14
MARKER = "written-after-the-limit.txt"


def _alive(pid):
    """Whether a process is alive: it exists and is no zombie waiting to be reaped."""
    try:
        state = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8", errors="replace").rpartition(")")[2].split()[0]
    except OSError:
        return False
    return state != "Z"


def test_after_a_run_cut_at_the_time_limit_no_process_of_it_lives_or_writes_into_the_project(project, sandbox,
                                                                                            interface, tmp_path):
    """An acceptance case of the parallel run tells its process and its parent, sleeps beyond the limit and
    would then write a marker file into the project."""
    told = tmp_path / "told"
    marker = project.root / MARKER
    late = (
        "import os\nimport time\n\n\n"
        "def test_late():\n"
        f"    with open({str(told)!r}, 'w', encoding='utf-8') as told:\n"
        "        told.write(f'{os.getpid()} {os.getppid()} {time.time()!r}')\n"
        f"    time.sleep({SLEEP_S})\n"
        f"    with open({str(marker)!r}, 'w', encoding='utf-8') as marker:\n"
        "        marker.write('written after the limit\\n')\n"
    )
    _build(project, {"test_late.py": late})

    run = support.run_close(project, sandbox, TICKET, "--timeout", str(LIMIT_S))
    returned = time.time()

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert "time limit" in support.error_text(error), \
        f"the fixture is wrong: the close was not refused for the time limit\n{run.describe()}"
    assert told.is_file(), "the fixture is wrong: the case had not begun when the run was cut"
    case, parent, began = told.read_text(encoding="utf-8").split()
    assert returned < float(began) + SLEEP_S - 2, "the fixture is wrong: the close returned after the case's sleep"

    # A process that was ended is reaped by whoever inherits it: two seconds are given for that, no more.
    deadline = time.time() + 2
    while time.time() < deadline and (_alive(case) or _alive(parent)):
        time.sleep(0.1)
    alive = [name for name, pid in (("the case's process", case), ("its parent", parent)) if _alive(pid)]
    # Both are asked before either is asserted: the case waits until the sleep would have ended.
    time.sleep(max(0.0, float(began) + SLEEP_S + 2 - time.time()))
    wrote = marker.exists()
    assert not alive, (f"after gov close returned from the run cut at the limit, still alive: {alive}"
                       + ("; and the case wrote into the project afterwards" if wrote else ""))
    assert not wrote, "a case of the run cut at the limit wrote into the project after gov close returned"
    assert MARKER not in support.untracked_paths(project)


# --------------------------------------------------------------------------
# 4. A list entry that names an existing file with no case in it
# --------------------------------------------------------------------------

NO_CASE = {
    "a test file without a test function": ("test_empty.py", "VALUE = 1\n"),
    "a helper module": ("helpers.py", "def helper():\n    return 1\n"),
}


@pytest.mark.parametrize("which", sorted(NO_CASE))
def test_a_list_entry_that_names_a_file_without_a_case_refuses_the_close(which, project, sandbox, interface):
    name, text = NO_CASE[which]
    entry = f"{ACCEPTANCE}/{name}"
    _build(project, {"test_pass.py": PASSING, name: text}, declared=[entry])
    assert (project.root / entry).is_file()

    run = support.run_close(project, sandbox, TICKET)

    _refused_with_a_finding(project, run, interface, entry)


# --------------------------------------------------------------------------
# 5. A byte in the list that is not UTF-8
# --------------------------------------------------------------------------

NOT_UTF8 = {
    "in a comment": b"# caf\xe9 cases\n" + f"{ACCEPTANCE}/test_pass.py\n".encode(),
    "in an entry": f"{ACCEPTANCE}/test_".encode() + b"\xff\xfe.py  # latency: planted\n",
}


@pytest.mark.parametrize("where", sorted(NOT_UTF8))
def test_a_byte_in_the_list_that_is_not_utf8_is_a_finding_that_names_the_list(where, project, sandbox, interface):
    _build(project, {"test_pass.py": PASSING}, list_bytes=NOT_UTF8[where])

    run = support.run_close(project, sandbox, TICKET)

    assert "Traceback" not in run.stdout + run.stderr, f"the close ended in a traceback\n{run.describe()}"
    _refused_with_a_finding(project, run, interface, LIST_UNREADABLE, support.SERIAL_ONLY_REL)
