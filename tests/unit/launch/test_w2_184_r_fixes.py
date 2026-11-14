"""W2-184 (DAEO-6f0s), reopened for R1-R3: the narrow independent check's F1-F3 (DEC-1180 (4)).

Written by the independent test designer (batch td-7) from the ticket's KPI lines R1, R2 and R3 and the interface's
section 10, as described behaviour (DEC-136); the engineer's work in ``src/gov/launch/`` was not read. Every case drives
a public interface: ``gov launch`` through its console-script entry point, ``gov.launch.launcher.launch(...)`` in a
child process with the environment ``gov launch`` gets, and ``gov.launch.record.write(records, record)``. The fixtures
are the W2-184 acceptance folder's (``tests/acceptance/W2-184/w2_184_support.py``, imported unchanged): a sandbox HOME
with an open resource gate, a stand-in CLI that starts no session and no model, a fixture project with role files, a
``criticality.yaml`` and tickets.

- **R1** (interface 10.1): a lead launch (``orchestrator`` or ``lead``) given ``--reason``, ``--trial`` or
  ``--owner-named`` before ``--`` is refused by the CLI with exit 2, before the launcher: nothing starts, no launch
  record, the gate not consulted; the message names the options and says a lead takes none of them. The direct call
  with a lead role and any of the three refuses with LAUNCH_REFUSED. A lead without them, the same words after ``--``,
  and a worker with them are unchanged.
- **R2** (interface 10.2): the launch record's bytes go to ``.<session_id>.<unique>.tmp`` in the same folder, are
  fsynced, then hard-linked to ``<session_id>.json`` (never over a file of that name), then the temporary file goes. A
  write killed or failing at any point leaves no final-name file, or a whole one. A leftover temporary file is not a
  record; a final-name record that is not JSON still refuses.
- **R3** (interface 10.3): one root-relative probe-record path found under several roots is read from every root
  (identical bytes are one copy); it is still one review: it holds a fail-open finding if any copy does, and is one
  failed record if any copy failed.
"""

from __future__ import annotations

import json
import multiprocessing
import os
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

import pytest

ACCEPTANCE = Path(__file__).resolve().parents[2] / "acceptance" / "W2-184"
sys.path.insert(0, str(ACCEPTANCE))

import w2_184_support as s  # noqa: E402

b = s.b
ENG, TD, AUD = s.ENGINEER, s.TEST_DESIGNER, s.AUDITOR
LEADS = ("orchestrator", "lead")
OPTION_NAMES = ("--reason", "--trial", "--owner-named")
READY_REL = "governance/project/orchestration/ready.txt"


# --------------------------------------------------------------------------
# Fixtures (the W2-184 acceptance folder's, restated: that folder's conftest is not loaded here)
# --------------------------------------------------------------------------

@pytest.fixture()
def sandbox(tmp_path):
    return b.make_sandbox(tmp_path / "w2-184")


@pytest.fixture()
def project(sandbox):
    return s.make_project(sandbox)


@pytest.fixture()
def cli(sandbox):
    return b.install_stand_in_cli(sandbox)


@pytest.fixture()
def launch(sandbox, project, cli):
    """``launch(role, ticket_id, *cli_args, reason=, trial=, owner_named=, cwd=)``: the keyword call when an option is
    given (``w2_184_support.launch``), else ``gov launch``."""

    def _launch(role, tk, *cli_args, **options):
        return s.launch(sandbox, cli, role, tk, *cli_args, **options)

    return _launch


@pytest.fixture()
def gov(sandbox, project, cli):
    """``gov(role, ticket, *cli_args, options=(...))``: ``gov launch <role> <ticket> <options> [-- <cli_args>]``."""

    def _gov(role, tk, *cli_args, options=()):
        return s.cli_launch(sandbox, cli, role, tk, *cli_args, options=options)

    return _gov


# ==========================================================================
# R1: a lead takes none of the three options
# ==========================================================================

LEAD_TK = "DAEO-ld01"


@pytest.fixture()
def lead_tk(project):
    """A ticket a lead may be launched on: in progress, on the approved ready list in the main tree (batch 1, no
    waits), as W2-136 and W2-56 admit a lead."""
    tk = s.ticket(project, ENG, "C2", tk=LEAD_TK)
    wbs = f"W2-184-{tk}"
    b.write(project / READY_REL, "# the approved ready list (planted for the W2-184 R1 cases)\n# batch 1\n"
                                 f"{wbs} {tk} {wbs}-A5-plan.md {wbs}-A5-plan.json\n")
    return tk


LEAD_OPTIONS = {
    "reason": ("--reason", "x"),
    "trial": ("--trial", "t1"),
    "owner-named": ("--owner-named", "DEC-1"),
    "all-three": ("--reason", "x", "--trial", "t1", "--owner-named", "DEC-1"),
    "empty-reason": ("--reason", ""),
}


def _lead_refused(result, options):
    """R1's refusal: exit 2, nothing started, no launch record, and a message on stderr that says a lead takes none of
    ``--reason``, ``--trial`` and ``--owner-named`` (each option given among the names)."""
    text = result.run.stderr.lower()
    assert result.run.returncode == 2, f"the lead launch was not refused with exit code 2\n{result.describe()}"
    assert not result.calls, f"the refused lead launch started the CLI\n{result.describe()}"
    assert not result.new_records, f"the refused lead launch left a launch record\n{result.describe()}"
    given = [word for word in options if word.startswith("--")]
    missing = [name for name in (*given, *OPTION_NAMES) if name not in text]
    assert not missing, f"the refusal on stderr does not name {sorted(set(missing))}\n{result.describe()}"
    assert "a lead" in text, f"the refusal on stderr does not say 'a lead'\n{result.describe()}"


@pytest.mark.parametrize("case", sorted(LEAD_OPTIONS))
@pytest.mark.parametrize("role", LEADS)
def test_r1_a_lead_given_an_option_is_refused_with_exit_2_and_nothing_starts(gov, lead_tk, role, case):
    _lead_refused(gov(role, lead_tk, options=LEAD_OPTIONS[case]), LEAD_OPTIONS[case])


@pytest.mark.parametrize("case", ["reason", "all-three"])
def test_r1_a_lead_given_an_option_is_refused_before_the_resource_gate_is_consulted(sandbox, gov, lead_tk, case):
    """The gate is shut (its configuration removed, W2-20 S8): a lead launch without the options is refused by the
    gate (exit 1, naming ``gate.json``); with an option the CLI refuses first (exit 2), and the gate's refusal is not
    what is said."""
    b.base_environment(sandbox)  # plants the open gate once
    (sandbox.home / ".gov-os" / "machine" / "gate.json").unlink()
    plain = gov("orchestrator", lead_tk)
    assert plain.run.returncode == 1 and not plain.calls and "gate.json" in plain.run.stderr, (
        f"premise: the shut gate does not refuse a plain lead launch\n{plain.describe()}")
    given = gov("orchestrator", lead_tk, options=LEAD_OPTIONS[case])
    _lead_refused(given, LEAD_OPTIONS[case])
    assert "gate.json" not in b.said(given), f"the resource gate was consulted\n{given.describe()}"


@pytest.mark.parametrize("role", LEADS)
def test_r1_a_lead_without_the_options_starts_as_before(gov, lead_tk, role):
    """Unchanged (green at the head): one session, no launch record."""
    result = b.assert_launched(gov(role, lead_tk))
    assert not result.new_records, f"a lead launch left a launch record\n{result.describe()}"


def test_r1_the_three_words_after_the_double_dash_of_a_lead_launch_are_passed_through_as_before(gov, lead_tk):
    """Unchanged (green at the head): after ``--`` they are CLI arguments, judged by the passthrough checks; the lead
    starts and the words reach the CLI once, unchanged and in order, just before the lead's appended template pair (a
    lead's line carries no ``--session-id``, so W2-60a's worker form of this check does not apply)."""
    passed = ["--reason", "x", "--trial", "t1", "--owner-named", "DEC-1"]
    result = b.assert_launched(gov("orchestrator", lead_tk, *passed))
    args, n = list(result.args), len(passed)
    assert args[-2] == b.APPEND_FLAG and args[-n - 2:-2] == passed, (
        f"the words after -- did not reach the CLI unchanged before the appended pair: {args}")
    assert sum(1 for i in range(len(args) - n + 1) if args[i:i + n] == passed) == 1, f"passed more than once: {args}"


@pytest.mark.parametrize("option", ["reason", "trial", "owner_named"])
@pytest.mark.parametrize("role", LEADS)
def test_r1_the_launcher_called_directly_with_a_lead_role_and_an_option_refuses(launch, lead_tk, role, option):
    """The second fence: ``launcher.launch(root, <lead>, tk, [], <option>=...)`` refuses with LAUNCH_REFUSED (exit 1)
    before anything starts."""
    value = {"reason": "x", "trial": "t1", "owner_named": "DEC-1"}[option]
    s.refused(launch(role, lead_tk, **{option: value}))


WORKER_TK = "DAEO-wk01"
ENG_C2 = s.TABLES[ENG]["C2"]  # Sonnet, high


@pytest.mark.parametrize("option", ["reason", "trial", "owner-named"])
def test_r1_a_worker_launch_with_each_option_is_unchanged(project, gov, option):
    """Unchanged (green at the head): an engineer's launch takes each option as interface 7.2a says."""
    tk = s.ticket(project, ENG, "C2", tk=WORKER_TK)
    if option == "trial":
        s.plant_trial(project, "t1", tk=tk)  # Haiku 5, high
        s.assert_session(gov(ENG, tk, options=("--trial", "t1")), s.HAIKU5, "high", criticality="C2",
                         model_source="trial", effort_source="trial", trial="t1")
        return
    word, key, value = {"reason": ("--reason", "effort_reason", "x"),
                        "owner-named": ("--owner-named", "owner_named", "DEC-1")}[option]
    s.assert_session(gov(ENG, tk, options=(word, value)), *ENG_C2, criticality="C2", model_source="by criticality",
                     effort_source="by criticality", **{key: value})


# ==========================================================================
# R2: the launch record is written atomically
# ==========================================================================

def _record(sid, pad=4000, mark="a"):
    return {"record": "gov-launch", "session_id": sid, "role": ENG, "ticket": "DAEO-r2aa", "pad": mark * pad}


def _final(folder, sid):
    return Path(folder) / f"{sid}.json"


def _temporaries(folder):
    """The files a reader of ``*.json`` never takes: names that begin with ``.`` and end with ``.tmp``."""
    return sorted(p.name for p in Path(folder).iterdir() if p.name.startswith(".") and p.name.endswith(".tmp"))


# A child that calls record.write and is stopped inside it. ``kill-at-first-byte``: the file size limit is 0 and
# SIGXFSZ kills the process at the first byte written to a regular file (after the create, before the bytes).
# ``kill-at-fsync``: the first os.fsync (or os.fdatasync) ends the process (after the bytes, before they are synced).
# ``oserror-at-first-byte``: the same limit with SIGXFSZ ignored, so the write raises OSError (EFBIG).
# ``oserror-at-fsync``: the first fsync raises OSError. Prints one JSON line: the outcome.
CHILD = r'''
import json, os, resource, signal, sys
from pathlib import Path
from gov.cli.errors import GovError
from gov.launch import record

folder, mode, data = Path(sys.argv[1]), sys.argv[2], json.loads(sys.argv[3])

def stop(*args):
    os._exit(9)

def fail(*args):
    raise OSError(5, "planted: the fsync failed")

if mode.endswith("at-fsync"):
    os.fsync = os.fdatasync = stop if mode.startswith("kill") else fail
if mode.endswith("at-first-byte"):
    signal.signal(signal.SIGXFSZ, signal.SIG_DFL if mode.startswith("kill") else signal.SIG_IGN)
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, resource.getrlimit(resource.RLIMIT_FSIZE)[1]))
try:
    record.write(folder, data)
except GovError as error:
    print(json.dumps({"refused": error.code, "message": error.message}))
    sys.exit(0)
print(json.dumps({"wrote": True}))
'''


def _child_write(folder, mode, data):
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": b.python_path()}
    return subprocess.run([sys.executable, "-c", CHILD, str(folder), mode, json.dumps(data)], capture_output=True,
                          text=True, timeout=b.COMMAND_TIMEOUT_S, env=env, stdin=subprocess.DEVNULL)


def _outcome(done):
    lines = done.stdout.strip().splitlines()
    return json.loads(lines[-1]) if lines else None


@pytest.mark.parametrize("mode", ["kill-at-first-byte", "kill-at-fsync"])
def test_r2_a_write_killed_after_the_create_leaves_no_final_name_file(tmp_path, mode):
    folder = tmp_path / "launches"
    folder.mkdir()
    sid = str(uuid.uuid4())
    done = _child_write(folder, mode, _record(sid))
    assert done.returncode != 0 and _outcome(done) is None, (
        f"the write was not stopped inside record.write ({mode}): exit {done.returncode}, said {done.stdout!r} "
        f"{done.stderr[-500:]!r}; a record written before its bytes are fsynced is not interface 10.2's")
    final = _final(folder, sid)
    assert not final.exists(), (
        f"a write killed inside record.write ({mode}) left the final-name file {final.name} "
        f"({final.stat().st_size} bytes): a launch killed at any point must leave no record or a whole one")
    left = sorted(p.name for p in folder.iterdir())
    assert left == _temporaries(folder), f"the killed write left a file a reader of *.json may take: {left}"


@pytest.mark.parametrize("mode", ["oserror-at-first-byte", "oserror-at-fsync"])
def test_r2_a_write_that_fails_refuses_and_leaves_neither_a_final_nor_a_temporary_file(tmp_path, mode):
    """Pins behaviour that must stay (green at the head): the refusal is today's, and nothing is left."""
    folder = tmp_path / "launches"
    folder.mkdir()
    sid = str(uuid.uuid4())
    done = _child_write(folder, mode, _record(sid))
    outcome = _outcome(done)
    assert done.returncode == 0 and outcome and outcome.get("refused") == "LAUNCH_REFUSED", (
        f"a failing write did not refuse with LAUNCH_REFUSED ({mode}): exit {done.returncode}, {done.stdout!r} "
        f"{done.stderr[-500:]!r}")
    assert "cannot be written" in outcome["message"] and str(folder) in outcome["message"], outcome
    assert sorted(p.name for p in folder.iterdir()) == [], f"the failed write left {sorted(folder.iterdir())}"


def test_r2_a_normal_write_leaves_the_whole_record_under_its_final_name_and_no_temporary_file(tmp_path):
    """Pins behaviour that must stay (green at the head)."""
    from gov.launch import record

    sid = str(uuid.uuid4())
    data = _record(sid)
    record.write(tmp_path, data)
    assert sorted(p.name for p in tmp_path.iterdir()) == [f"{sid}.json"]
    assert json.loads(_final(tmp_path, sid).read_text(encoding="utf-8")) == data


def test_r2_a_leftover_temporary_file_does_not_refuse_a_later_write_of_the_same_session_id(tmp_path):
    """Pins behaviour that must stay (green at the head)."""
    from gov.launch import record

    sid = str(uuid.uuid4())
    planted = {f".{sid}.leftover.tmp": "", f".{sid}.x1y2z3.tmp": '{"record": "gov-launch", "sess'}
    for name, text in planted.items():
        (tmp_path / name).write_text(text, encoding="utf-8")
    data = _record(sid)
    record.write(tmp_path, data)
    assert json.loads(_final(tmp_path, sid).read_text(encoding="utf-8")) == data
    assert _temporaries(tmp_path) == sorted(planted), (
        f"the write left a temporary file of its own: {_temporaries(tmp_path)}")


@pytest.mark.parametrize("existing", ["another-record", "not-json", "empty"])
def test_r2_an_existing_final_name_file_is_never_overwritten(tmp_path, existing):
    """Pins behaviour that must stay (green at the head): refused as already there, the file's bytes kept, the
    write's temporary file removed."""
    from gov.cli.errors import GovError
    from gov.launch import record

    sid = str(uuid.uuid4())
    text = {"another-record": json.dumps(_record(sid, mark="z")), "not-json": "keep these bytes\n",
            "empty": ""}[existing]
    final = _final(tmp_path, sid)
    final.write_text(text, encoding="utf-8")
    with pytest.raises(GovError) as raised:
        record.write(tmp_path, _record(sid))
    assert raised.value.code == "LAUNCH_REFUSED" and "already there" in raised.value.message, raised.value.message
    assert final.read_text(encoding="utf-8") == text, "the existing final-name file was overwritten"
    assert sorted(p.name for p in tmp_path.iterdir()) == [final.name], sorted(tmp_path.iterdir())


def test_r2_a_second_write_of_the_same_session_id_is_refused_as_already_there(tmp_path):
    """Pins behaviour that must stay (green at the head)."""
    from gov.cli.errors import GovError
    from gov.launch import record

    sid = str(uuid.uuid4())
    first = _record(sid, mark="a")
    record.write(tmp_path, first)
    with pytest.raises(GovError) as raised:
        record.write(tmp_path, _record(sid, mark="b"))
    assert raised.value.code == "LAUNCH_REFUSED" and "already there" in raised.value.message, raised.value.message
    assert json.loads(_final(tmp_path, sid).read_text(encoding="utf-8")) == first
    assert sorted(p.name for p in tmp_path.iterdir()) == [f"{sid}.json"]


ROUNDS = 12
PAD = 400_000  # bytes per record: a write long enough that two writers overlap


def _racer(folder, sid, mark, barrier, results):
    from gov.cli.errors import GovError
    from gov.launch import record

    barrier.wait()
    try:
        record.write(Path(folder), _record(sid, pad=PAD, mark=mark))
        results.put((mark, "wrote", ""))
    except GovError as error:
        results.put((mark, error.code, error.message))
    except BaseException as error:  # noqa: BLE001 -- reported, never swallowed
        results.put((mark, type(error).__name__, str(error)))


def test_r2_two_writers_of_one_session_id_leave_one_whole_record_and_the_other_is_refused(tmp_path):
    """Pins behaviour that must stay (green at the head): two processes released together write the same session id,
    ``ROUNDS`` times; each time one writes, the other is refused as already there, and the final file is the winner's
    whole record."""
    import gov.launch.record  # noqa: F401 -- loaded before the fork

    context = multiprocessing.get_context("fork")
    for round_ in range(ROUNDS):
        folder = tmp_path / f"round-{round_}"
        folder.mkdir()
        sid = str(uuid.uuid4())
        barrier, results = context.Barrier(2), context.Queue()
        racers = [context.Process(target=_racer, args=(str(folder), sid, mark, barrier, results)) for mark in "ab"]
        for racer in racers:
            racer.start()
        got = sorted(results.get(timeout=b.COMMAND_TIMEOUT_S) for _ in racers)
        for racer in racers:
            racer.join(timeout=b.COMMAND_TIMEOUT_S)
        outcomes = sorted(outcome for _, outcome, _ in got)
        assert outcomes == ["LAUNCH_REFUSED", "wrote"], f"round {round_}: {got}"
        winner = next(mark for mark, outcome, _ in got if outcome == "wrote")
        loser = next(message for _, outcome, message in got if outcome != "wrote")
        assert "already there" in loser, f"round {round_}: the loser was not refused as already there: {loser}"
        assert json.loads(_final(folder, sid).read_text(encoding="utf-8")) == _record(sid, pad=PAD, mark=winner), (
            f"round {round_}: the final record is not the winner's whole record")
        assert sorted(p.name for p in folder.iterdir()) == [f"{sid}.json"], (
            f"round {round_}: {sorted(p.name for p in folder.iterdir())}")


# A worker launch that reads the record folder: an engineer on a C2 ticket in a project with a criticality.yaml
# (interface 5.1a, P-td5-1: every such launch reads the folder).

R2_TK = "DAEO-r2ab"


def test_r2_a_launch_killed_inside_its_record_write_does_not_refuse_the_next_worker_launch(project, sandbox, gov):
    tk = s.ticket(project, ENG, "C2", tk=R2_TK)
    b.assert_launched(gov(ENG, tk))  # the record folder exists, holding one whole record
    sid = str(uuid.uuid4())
    done = _child_write(sandbox.records, "kill-at-first-byte", _record(sid))
    assert done.returncode != 0, f"premise: the write was not killed\n{done.stdout}{done.stderr[-500:]}"
    result = gov(ENG, tk)
    assert result.run.returncode == 0 and len(result.calls) == 1, (
        f"the killed write's leftover refused the next launch\n{result.describe()}")
    s.assert_session(result, *ENG_C2, criticality="C2", model_source="by criticality", effort_source="by criticality")


@pytest.mark.parametrize("leftover", ["empty", "partial"])
def test_r2_a_leftover_temporary_file_does_not_refuse_a_worker_launch(project, sandbox, gov, leftover):
    """Pins behaviour that must stay (green at the head): a file that does not match ``*.json`` is not a record."""
    tk = s.ticket(project, ENG, "C2", tk=R2_TK)
    b.assert_launched(gov(ENG, tk))
    sid = str(uuid.uuid4())
    b.write(Path(sandbox.records) / f".{sid}.k3j9.tmp", "" if leftover == "empty" else '{"record": "gov-la')
    s.assert_session(gov(ENG, tk), *ENG_C2, criticality="C2", model_source="by criticality",
                     effort_source="by criticality")


@pytest.mark.parametrize("planted", ["empty", "partial", "not-json"])
def test_r2_a_final_name_record_that_is_not_json_still_refuses_a_worker_launch_naming_it(
        project, sandbox, gov, planted):
    """Pins behaviour that must stay (green at the head): P-td5-1, 5.1a, 6.1 unchanged."""
    tk = s.ticket(project, ENG, "C2", tk=R2_TK)
    b.assert_launched(gov(ENG, tk))
    name = f"{uuid.uuid4()}.json"
    b.write(Path(sandbox.records) / name, {"empty": "", "partial": '{"record": "gov-launch", "sess',
                                           "not-json": "not json at all\n"}[planted])
    s.refused(gov(ENG, tk), name)


# ==========================================================================
# R3: every root's copy of a probe record is read
# ==========================================================================

R3_TK, R3_OTHER = "DAEO-r3aa", "DAEO-r3ab"
TD_C2 = s.TABLES[TD]["C2"]  # Sonnet, xhigh
FAIL_OPEN, TWO_FAILED = "a fail-open finding", "two failed reviews"


@dataclass(frozen=True)
class Repo:
    sandbox: object
    project: Path  # the main checkout
    ticket: Path   # the ticket's worktree, branch w2/W2-r3aa
    tests: Path    # the tests' worktree, branch w2/W2-r3aa-tests

    def tree(self, name):
        return s.add_worktree(self.project, self.sandbox.home / "work" / name, f"w2/{name}")


@pytest.fixture()
def repo(sandbox, project):
    """As ``test_w2_184_f1_tests_worktree.py`` builds it: the tickets committed in the main checkout, then the
    ticket's and the tests' linked worktrees, sharing the main checkout's launch record folder."""
    s.ticket(project, ENG, "C2", "STANDARD", tk=R3_TK)
    s.ticket(project, ENG, "C2", "STANDARD", tk=R3_OTHER)
    s.commit_all(project, "the fixture tickets")
    return Repo(sandbox, project, s.add_worktree(project, sandbox.home / "work" / "W2-r3aa", "w2/W2-r3aa"),
                s.add_worktree(project, sandbox.home / "work" / "W2-r3aa-tests", "w2/W2-r3aa-tests"))


def _probe(tree, name, judgement="pass", *, fail_open=False, note=""):
    """``docs/probes/<ticket>/<name>`` in ``tree``: front matter ``type: probe`` and ``judgement``, a body line
    ``note`` (so two copies can differ in bytes alone), and a verdict block with a fail-open finding if asked."""
    verdict = s.verdict_block("other", "fails open") if fail_open else ""
    raw = f"---\ntype: probe\ntask: {R3_TK}\njudgement: {judgement}\n---\n\n# Probe record\n\n{note}\n\n{verdict}"
    return s.plant_probe(tree, R3_TK, name, raw=raw)


def _bring(repo, source_branch="w2/W2-r3aa"):
    """The stop-gap (c): the ticket branch's records brought into the tests branch (fast-forward)."""
    b.git(repo.tests, "merge", "-q", "--ff-only", source_branch)


def _promoted(result, table, reason, record):
    return s.assert_session(result, s.OPUS, table[1], criticality="C2", model_source="promotion",
                            effort_source="by criticality", promotion={"reason": reason, "record": record})


def _on_table(result, table=TD_C2):
    return s.assert_session(result, *table, criticality="C2", model_source="by criticality",
                            effort_source="by criticality", promotion=None)


def test_r3_a_stale_launch_root_copy_and_a_newer_ticket_copy_with_the_finding_promote_the_test_designer(
        repo, launch):
    """F3's case: the record is brought into the tests branch, then edited in place on the ticket branch to add a
    fail-open finding; the test designer launched from the tests worktree is promoted, naming the root-relative
    path."""
    rel = _probe(repo.ticket, "01-review.md", "pass")
    s.commit_all(repo.ticket, "the review record")
    _bring(repo)
    _probe(repo.ticket, "01-review.md", "pass", fail_open=True)
    s.commit_all(repo.ticket, "the same record, edited in place to add a fail-open finding")
    assert (repo.tests / rel).read_bytes() != (repo.ticket / rel).read_bytes(), "premise: the copies do not differ"
    b.assert_launched(launch(ENG, R3_TK, cwd=repo.ticket))
    _promoted(launch(TD, R3_TK, cwd=repo.tests), TD_C2, FAIL_OPEN, rel)
    s.refused(launch(TD, R3_TK, "--model", TD_C2[0], cwd=repo.tests), TD_C2[0], s.OPUS)


def test_r3_the_reverse_a_launch_root_copy_with_the_finding_and_another_root_s_copy_without_it_promote(repo, launch):
    """The tests branch's copy holds the finding, the ticket branch's not. The test designer launched from the tests
    worktree is promoted (its own copy: green at the head); then the engineer launched from the ticket worktree, whose
    own copy lacks it, is promoted too (the tests root is named by the test designer's launch record)."""
    rel = _probe(repo.ticket, "01-review.md", "pass")
    s.commit_all(repo.ticket, "the review record")
    _bring(repo)
    _probe(repo.tests, "01-review.md", "pass", fail_open=True)
    s.commit_all(repo.tests, "the tests branch's copy, with a fail-open finding")
    _promoted(launch(TD, R3_TK, cwd=repo.tests), TD_C2, FAIL_OPEN, rel)
    _promoted(launch(ENG, R3_TK, cwd=repo.ticket), ENG_C2, FAIL_OPEN, rel)


def test_r3_identical_copies_of_one_failed_record_under_three_roots_count_once(repo, launch):
    """Pins behaviour that must stay (green at the head): one failed record, brought into the tests branch and present
    in a review worktree too, is one failed review; a second failed record then promotes, naming it."""
    _probe(repo.ticket, "01-review.md", "fail")
    s.commit_all(repo.ticket, "the first review record")
    _bring(repo)
    review = repo.tree("W2-r3aa-review")
    b.git(review, "merge", "-q", "--ff-only", "w2/W2-r3aa")
    b.assert_launched(launch(ENG, R3_TK, cwd=repo.ticket))
    b.assert_launched(launch(AUD, R3_TK, cwd=review))
    _on_table(launch(TD, R3_TK, cwd=repo.tests))
    second = _probe(repo.ticket, "02-review.md", "fail")
    s.commit_all(repo.ticket, "the second review record")
    _promoted(launch(TD, R3_TK, cwd=repo.tests), TD_C2, TWO_FAILED, second)


def test_r3_two_differing_copies_of_one_failed_record_are_one_failed_review(repo, launch):
    """Pins behaviour that must stay (green at the head; interface 10.3 (b)): the two copies differ in bytes and both
    fail; the path is still one failed review, so the launch is on the table; a second failed path then promotes."""
    rel = _probe(repo.ticket, "01-review.md", "fail", note="the ticket branch's wording")
    s.commit_all(repo.ticket, "the first review record")
    _probe(repo.tests, "01-review.md", "failed", note="the tests branch's wording")
    s.commit_all(repo.tests, "another copy of the first review record")
    assert (repo.tests / rel).read_bytes() != (repo.ticket / rel).read_bytes(), "premise: the copies do not differ"
    b.assert_launched(launch(ENG, R3_TK, cwd=repo.ticket))
    _on_table(launch(TD, R3_TK, cwd=repo.tests))
    second = _probe(repo.ticket, "02-review.md", "fail")
    s.commit_all(repo.ticket, "the second review record")
    _promoted(launch(TD, R3_TK, cwd=repo.tests), TD_C2, TWO_FAILED, second)


def test_r3_a_path_is_a_failed_review_when_any_copy_failed(repo, launch):
    """The launch root's copy of ``01`` passes, the ticket worktree's copy fails; ``02`` fails on the ticket branch:
    two failed reviews, naming ``02``."""
    rel = _probe(repo.tests, "01-review.md", "pass")
    s.commit_all(repo.tests, "the tests branch's copy, passing")
    _probe(repo.ticket, "01-review.md", "fail")
    second = _probe(repo.ticket, "02-review.md", "fail")
    s.commit_all(repo.ticket, "the ticket branch's copy, failing, and a second failed record")
    assert (repo.tests / rel).read_bytes() != (repo.ticket / rel).read_bytes(), "premise: the copies do not differ"
    b.assert_launched(launch(ENG, R3_TK, cwd=repo.ticket))
    _promoted(launch(TD, R3_TK, cwd=repo.tests), TD_C2, TWO_FAILED, second)


UNREADABLE = {
    "a-front-matter-that-is-not-yaml": "---\ntype: probe\njudgement: [fail\n---\n\n# Probe\n",
    "a-verdict-block-that-is-not-json": "---\ntype: probe\njudgement: pass\n---\n\n```verdict\nnot json at all\n```\n",
}


@pytest.mark.parametrize("case", sorted(UNREADABLE))
def test_r3_another_root_s_unreadable_copy_of_a_path_the_launch_root_also_holds_refuses_naming_the_file(
        repo, launch, case):
    """The launch root's copy of ``01-review.md`` is well formed; the ticket worktree's copy of the same path is
    not: that copy is read too, so the test designer's launch from the tests worktree is refused, naming the file."""
    b.assert_launched(launch(ENG, R3_TK, cwd=repo.ticket))  # a launch record names the ticket worktree
    _probe(repo.tests, "01-review.md", "pass")
    s.commit_all(repo.tests, "the tests branch's copy, well formed")
    s.plant_probe(repo.ticket, R3_TK, "01-review.md", raw=UNREADABLE[case])
    s.commit_all(repo.ticket, "the ticket branch's copy, unreadable, after the engineer's launch")
    s.refused(launch(TD, R3_TK, cwd=repo.tests), "01-review.md")
