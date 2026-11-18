"""W2-199, success line 10 (RT-3, a drop-in for the scratch script).

``governance/project/orchestration/tools/heavy_slot.sh`` (this branch's text) is a wrapper of at most 60 lines over
``gov resources --slot test`` (``--held <list>`` passes through): it keeps the callers' forms and exit codes (the command's
own code, 0 included; the run's own failure to start is a code of the product's, never 213), maps ``GOV_HEAVY_SLOTS``,
``GOV_HEAVY_WORKERS``, ``GOV_HEAVY_START_BELOW``, ``GOV_HEAVY_PRIORITY``, ``GOV_HEAVY_PRIO_CAP`` to the product's, runs
``python3 -m gov.cli.main`` when ``PYTHONPATH`` names a source tree else ``gov``, and reads no ``heavy_slots.conf``; the
command it runs sees ``PYTEST_XDIST_AUTO_NUM_WORKERS``, ``GOV_HEAVY_SLOT``, ``GOV_HEAVY_CPUS`` and ``GOV_HEAVY_ADMITTED``.

The wrapper runs under a fixture HOME with ``PYTHONPATH`` this worktree's ``src`` (the machine's ``python3`` on the fixture
``PATH`` is a stand-in for the test's own interpreter).
"""

from __future__ import annotations

import shutil
import subprocess

import w2_199_support as s

SCRIPT = s.REPO_ROOT / "governance" / "project" / "orchestration" / "tools" / "heavy_slot.sh"


def wrapper(box, *args, script=SCRIPT, extra_env=None, timeout=20) -> subprocess.CompletedProcess:
    assert script.is_file(), f"the wrapper {script} does not exist"
    try:
        return subprocess.run(["bash", str(script), *map(str, args)], cwd=str(box.work), env=box.env(extra_env),
                              capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"heavy_slot.sh {' '.join(map(str, args))} did not end within {timeout} s") from None


def test_s10_the_wrapper_is_60_lines_or_fewer(box):
    assert SCRIPT.is_file(), f"the wrapper {SCRIPT} does not exist"
    lines = len(SCRIPT.read_text(encoding="utf-8").splitlines())
    assert lines <= 60, f"heavy_slot.sh is {lines} lines, over 60"


def test_s10_the_commands_own_exit_code_comes_back_0_included(box):
    done = wrapper(box, "sh", "-c", "exit 7")
    assert done.returncode == 7, f"exit {done.returncode}, not 7\n{s.said(done)}"
    done = wrapper(box, "true")
    assert done.returncode == 0, f"`true`: exit {done.returncode}\n{s.said(done)}"
    done = wrapper(box, "sh", "-c", "exit 213")
    assert done.returncode == 213, "the command's own 213 is the command's"


def test_s10_a_command_that_cannot_start_ends_with_the_products_code_never_213(box):
    done = wrapper(box, "/nonexistent/command-for-w2-199")
    assert done.returncode not in (0, 213), f"exit {done.returncode}\n{s.said(done)}"


def test_s10_the_command_sees_its_workers_slot_cpus_and_the_admitted_mark(box):
    done = wrapper(box, "sh", "-c", 'echo "${PYTEST_XDIST_AUTO_NUM_WORKERS-UNSET}|${GOV_HEAVY_SLOT-UNSET}|'
                                    '${GOV_HEAVY_CPUS-UNSET}|${GOV_HEAVY_ADMITTED-UNSET}"')
    assert done.returncode == 0, s.said(done)
    workers, slot, cpus, admitted = done.stdout.strip().split("|")
    assert workers == "4", f"PYTEST_XDIST_AUTO_NUM_WORKERS is {workers!r}: the 20-CPU profile gives 4"
    assert slot in ("1", "2"), f"GOV_HEAVY_SLOT is {slot!r}"
    assert cpus != "UNSET", "GOV_HEAVY_CPUS is not set"
    assert admitted == "1", f"GOV_HEAVY_ADMITTED is {admitted!r}, not 1"


def test_s10_held_1_passes_through_and_prints_the_per_slot_workers(box):
    done = wrapper(box, "--held", "1", "sh", "-c", "echo $PYTEST_XDIST_AUTO_NUM_WORKERS")
    assert done.returncode == 0, s.said(done)
    assert done.stdout.strip() == "4", f"--held 1 printed {done.stdout.strip()!r}, not the per-slot workers 4"
    done = wrapper(box, "--held", "1,2", "sh", "-c", "echo $PYTEST_XDIST_AUTO_NUM_WORKERS")
    assert done.stdout.strip() == "8", f"--held 1,2 printed {done.stdout.strip()!r}, not twice the per-slot workers"


def test_s10_the_gov_heavy_variables_map_to_the_products(box):
    done = wrapper(box, "sh", "-c", "echo $PYTEST_XDIST_AUTO_NUM_WORKERS", extra_env={"GOV_HEAVY_WORKERS": "3"})
    assert done.stdout.strip() == "3", f"GOV_HEAVY_WORKERS=3 gives {done.stdout.strip()!r}\n{s.said(done)}"
    box.load(6.0)
    held = subprocess.Popen(["bash", str(SCRIPT), "true"], cwd=str(box.work), stdin=subprocess.DEVNULL,
                            env=box.env({"GOV_HEAVY_START_BELOW": "5"}), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    box.processes.append(held)
    try:
        held.wait(timeout=2.0)
        raise AssertionError("GOV_HEAVY_START_BELOW=5 with a load of 6: the wrapper's run was not held")
    except subprocess.TimeoutExpired:
        pass
    box.load(2.0)
    assert held.wait(timeout=5.0) == 0
    # GOV_HEAVY_SLOTS=1: a second run waits for the first
    box.load(3.0)
    first = box.start("first", extra_env={"GOV_HEAVY_SLOTS": "1"})
    first.must_start(5.0)
    second = subprocess.Popen(["bash", str(SCRIPT), "true"], cwd=str(box.work), stdin=subprocess.DEVNULL,
                              env=box.env({"GOV_HEAVY_SLOTS": "1"}), stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    box.processes.append(second)
    try:
        second.wait(timeout=1.5)
        raise AssertionError("GOV_HEAVY_SLOTS=1 through the wrapper: a second run did not wait for the first")
    except subprocess.TimeoutExpired:
        pass
    first.release_and_finish()
    assert second.wait(timeout=6.0) == 0


def test_s10_a_heavy_slots_conf_beside_the_script_is_not_read(box, tmp_path):
    folder = tmp_path / "copy"
    folder.mkdir()
    shutil.copy(SCRIPT, folder / "heavy_slot.sh")
    (folder / "heavy_slots.conf").write_text("SLOTS=1\nWORKERS=9\nSTART_BELOW=1\n")
    box.load(3.0)  # over the conf's START_BELOW of 1, under the machine's 12
    done = wrapper(box, "sh", "-c", "echo $PYTEST_XDIST_AUTO_NUM_WORKERS", script=folder / "heavy_slot.sh", timeout=8)
    assert done.returncode == 0, s.said(done)
    assert done.stdout.strip() == "4", f"the conf's WORKERS=9 was read: {done.stdout.strip()!r}"
