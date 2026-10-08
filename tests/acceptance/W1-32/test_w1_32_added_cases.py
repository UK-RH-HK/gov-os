"""Cases added after implementation: four behaviours a reading of the work found uncovered.

"A result is measured or it is refused" (DEC-449, DEC-454), held to three more
sources of ``gov status``, and DEC-392's exit code held when the launcher
cannot write its line:

1. the freeze flag's path holds a placeholder device (what a session's sandbox
   puts there whether or not a flag exists, DEC-402, DEC-311): the flag was not
   read, so the status gives no plain "not paused" and does not report the
   path as it would an empty file;
2. a record file committed in the project that the store's load cannot take as
   a record (DEC-239; W1-10 lists it in ``invalid``) may be an open decision
   package (DEC-308): the list of packages is then not a clean one, and the
   part names the file;
3. a store that answers for its commits and not for its records or edges: the
   ready and blocked tickets are not read, as they are without a store;
4. the removal of the launcher's temp folder fails and its stderr cannot be
   written: ``gov launch`` still ends with the session's exit code.

Every case builds its own temporary project. The placeholder is stood in
without privileges: a symbolic link to the null device, which reads as a
character device. No case touches this repository's flag, and the launcher
cases start this suite's stand-in session program and send no signal.
"""

from __future__ import annotations

import os
import sqlite3
import stat
import subprocess
import sys

import pytest

import w1_32_support as support

tasks_support = support.tasks_support
pause_support = support.pause_support

BROKEN_PACKAGE = "DP-9198"
BROKEN_PACKAGE_REL = f"{support.GATES_REL}/{BROKEN_PACKAGE}.md"
NO_YAML = "---\nid: [unclosed\ntype: decision-package\nstatus: PROPOSED\n---\n\n# A package nobody can load\n"
NO_STATUS = (f"---\nid: {BROKEN_PACKAGE}\ntype: {support.PACKAGE_TYPE}\nstate_class: AUTHORITATIVE\n"
             f"constrains: [{support.T_READY}]\n---\n\n# A package without its status\n")
RECORDS_TABLE, EDGES_TABLE = "records", "edges"   # the two tables of the store the READY rule reads (W1-10)


# --------------------------------------------------------------------------
# 1. A flag path that holds a placeholder
# --------------------------------------------------------------------------

def _flag(project):
    return project.root / support.FREEZE_FLAG_REL


def _placeholder(project):
    """Stand a character device in at the flag's path, as a session's sandbox does, without privileges."""
    flag = _flag(project)
    flag.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(flag):
        flag.unlink()
    os.symlink(os.devnull, flag)
    assert stat.S_ISCHR(os.stat(flag).st_mode), f"{flag} does not read as a character device on this machine"
    return flag


def test_a_placeholder_device_at_the_flags_path_is_never_a_plain_not_paused(project, status, interface):
    """Behind the placeholder a flag may or may not exist: the status has not read it. The pause part, or the
    flag inside it, says so with a reason, or the project is reported paused."""
    _placeholder(project)
    answer = support.parts(status(), interface)
    part = answer[support.PAUSE]
    assert support.paused(answer) is not False or support.unread_entries(part), (
        "a placeholder device is at the flag's path, the flag was not read, and the status says not paused with "
        f"nothing marked as not read: {support.text_of(part)}"
    )


def test_a_placeholder_device_is_not_reported_as_an_empty_file_is(project, status, interface):
    """An empty file was read and holds no marker (DEC-402); a device was not read. The two are not one answer."""
    flag = _flag(project)
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_bytes(b"")
    empty = support.answered(status(), interface)[support.PAUSE]
    _placeholder(project)
    placeholder = support.parts(status(), interface)[support.PAUSE]
    assert placeholder != empty, (
        "the pause part for a placeholder device at the flag's path is the one given for an empty file: "
        f"{support.text_of(placeholder)}"
    )


def test_the_mirror_still_answers_beside_a_placeholder(project, sandbox, status, interface):
    """DEC-429: the mirror is a second source. A paused project whose flag path shows a placeholder is paused."""
    pause_support.succeeded(pause_support.pause(project.root, sandbox, role=pause_support.OWNER), interface)
    _placeholder(project)
    answer = support.parts(status(), interface)
    assert support.paused(answer) is not False, (
        "the mirror freezes the tree, a placeholder is at the flag's path, and the status says not paused: "
        f"{support.text_of(answer[support.PAUSE])}"
    )


# --------------------------------------------------------------------------
# 2. A decision-package record that cannot be loaded
# --------------------------------------------------------------------------

def _invalid(project):
    """What the store's load says it could not load (W1-10: ``invalid``, by path); the store is loaded by it."""
    return [entry["path"] for entry in project.driver.call("gov.store", "load", project.root)["invalid"]]


@pytest.mark.parametrize("text", (NO_YAML, NO_STATUS), ids=("frontmatter-that-does-not-parse", "no-status"))
def test_a_record_the_load_cannot_take_is_not_hidden_behind_a_clean_list_of_packages(project, sandbox, interface, text):
    """The file is committed, the store is loaded at that commit, and the load could not take it as a record.
    It may be an open gate: the part shows that something was not read, and names the file."""
    tasks_support.write(project.root, BROKEN_PACKAGE_REL, text)
    support.settle(project)
    assert BROKEN_PACKAGE_REL in _invalid(project), "the fixture's record was loaded: nothing to report"
    packages = support.parts(support.status(project, sandbox), interface)[support.PACKAGES]
    said = support.text_of(packages)
    assert support.unread_entries(packages), (
        f"{BROKEN_PACKAGE_REL} could not be loaded as a record and the decision packages are given as a clean "
        f"list: nothing in the part says read: false with a reason: {said[:600]}"
    )
    assert BROKEN_PACKAGE_REL in said, (
        f"the decision packages part does not name {BROKEN_PACKAGE_REL}, the file that was not read: {said[:600]}"
    )


def test_a_project_whose_records_all_load_keeps_its_clean_list_of_packages(project, status, interface):
    assert _invalid(project) == [], "the fixture holds a record that cannot be loaded"
    packages = support.answered(status(), interface)[support.PACKAGES]
    assert support.unread_entries(packages) == [], \
        f"every record loads and the decision packages say something was not read: {support.text_of(packages)}"
    assert support.ids(packages) == [support.DP_OPEN, support.DP_OTHER_OPEN]


# --------------------------------------------------------------------------
# 3. A store whose commits read and whose records do not
# --------------------------------------------------------------------------

def _drop(project, table):
    """Take one table out of the project's store; its commits stay and still answer."""
    connection = sqlite3.connect(project.root / support.STORE_REL)
    try:
        names = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
        assert table in names, f"the store holds no table {table!r} (it holds {names}): the fixture no longer fits"
        connection.execute(f"DROP TABLE {table}")
        connection.commit()
    finally:
        connection.close()
    head = tasks_support.git(project.root, "rev-parse", "HEAD").strip()
    loaded = [commit["commit"] for commit in project.driver.call("gov.records", "commits", project.root)]
    assert head in loaded, "the store no longer answers for its commits: this is the case of a store that is absent"


@pytest.mark.parametrize("table", (RECORDS_TABLE, EDGES_TABLE))
def test_a_store_without_its_records_or_edges_leaves_the_ready_and_blocked_tickets_not_read(project, sandbox,
                                                                                             interface, table):
    """The READY rule reads the records and their edges (an open package holds a ticket through one, DEC-308).
    Without them it has no answer: never an empty ready list, never a blocked list without its reasons."""
    _drop(project, table)
    tickets = support.parts(support.status(project, sandbox), interface)[support.TICKETS]
    support.assert_not_read(tickets, f"the store's {table} cannot be read and the ready tickets",
                            within=(support.READY,))
    support.assert_not_read(tickets, f"the store's {table} cannot be read and the blocked tickets",
                            within=(support.BLOCKED,))


# --------------------------------------------------------------------------
# 4. The launcher's exit code when stderr cannot be written
# --------------------------------------------------------------------------

def _close_stderr():
    """Runs in the child before ``gov`` starts: the launcher has no stderr at all."""
    os.close(2)


def _launch_without_stderr(launch_support, project, sandbox, cli, way):
    """``gov launch`` to its end, with a stderr that cannot be written. Returns W1-46's ``Launch``."""
    w46 = launch_support.w46
    before = len(w46.calls(cli))
    script = launch_support.cli_support.write_launcher(project, sandbox)
    out_path = sandbox.elsewhere / "launch-stdout.txt"
    options = {}
    if way == "closed":
        options["preexec_fn"] = _close_stderr
    else:  # a pipe nobody reads any more: every write to it fails
        reader, writer = os.pipe()
        os.close(reader)
        options["stderr"] = writer
    try:
        with open(out_path, "w", encoding="utf-8") as out_file:
            done = subprocess.run([sys.executable, str(script), "launch", launch_support.ENGINEER,
                                   launch_support.ENGINEER_TICKET], cwd=str(project),
                                  env=w46.gov_environment(project, sandbox, cli), stdin=subprocess.DEVNULL,
                                  stdout=out_file, timeout=launch_support.WAIT_S * 2, **options)
    finally:
        if "stderr" in options:
            os.close(options["stderr"])
    run = launch_support.cli_support.Run(("launch", launch_support.ENGINEER, launch_support.ENGINEER_TICKET),
                                         done.returncode, out_path.read_text(encoding="utf-8"), "", 0.0)
    return w46.Launch(run, tuple(w46.calls(cli)[before:]))


@pytest.mark.parametrize("way, code", (("closed", 7), ("reader-gone", 7), ("reader-gone", 0)),
                         ids=("stderr-closed-7", "stderr-reader-gone-7", "stderr-reader-gone-0"))
def test_a_failed_removal_keeps_the_sessions_exit_code_when_stderr_cannot_be_written(launch_project, sandbox, cli,
                                                                                    way, code):
    """DEC-392 puts the exit code first: the line that names the folder is lost with the stream, the code is not."""
    import w1_32_launch_support as launch_support

    if os.geteuid() == 0:
        pytest.skip("a read-only folder does not stop the removal for the superuser")
    launch_support.plan(cli, files=launch_support.LEFT, sealed=("sealed",), exit_code=code)
    try:
        result = _launch_without_stderr(launch_support, launch_project, sandbox, cli, way)
        folder = launch_support.w28.temp_folder(result)
        assert (folder / "sealed" / "kept.txt").is_file(), \
            "the fixture's folder was removed: the removal did not fail"
        assert result.run.returncode == code, (
            f"the session ended with exit code {code}, its temp folder could not be removed, stderr could not be "
            f"written ({way}), and gov launch ended with {result.run.returncode}\n{result.describe()}"
        )
    finally:
        launch_support.unseal(sandbox.tmpdir)
