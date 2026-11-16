"""W2-60b, KPI success-5, success-6 and failure-3 -- a record that cannot be written changes nothing but one stderr
line; a record is read back by ticket and session id; the CIT-E states its path and keys.

success-5 [DEC-392]: "A record that cannot be written leaves the session's exit code as it is, with one line on stderr
naming it; a record is written whole or not at all." Verify: a planted unwritable record path: the session's exit code
is unchanged, stderr holds one line naming the record, and no part of a record is left on disk.

success-6 [CAP-36.a lite, lens F R6]: "W2-07's close can join it: the record's path and keys are stated in the CIT-E,
and a test reads a record back by ticket and session id; pass or fail and the repair count stay the close's." Verify:
the CIT-E states the record's path and keys; a unit test writes a record and reads it back by ticket and session id
through them.

failure-3: "A changed exit code" -- a planted record-write failure leaves the session's exit code as it was.

Interface: one stderr line in all for the session, naming the record's path (not one per attempt: the start's write
and the end's both fail here); no record and no temporary file left; ``read_record(root, ticket, session_id)`` in
``gov.launch.session_record`` returns the record; the CIT-E is ``docs/changes/W2-60b-CIT-E.md``.
"""

from __future__ import annotations

import importlib
import os

import pytest

import w2_60b_support as t

b = t.b
ENG = t.ENGINEER
T = b.T


def _unwritable(project, how):
    folder = t.sessions(project)
    folder.parent.mkdir(parents=True, exist_ok=True)
    if how == "a-file-in-its-place":
        folder.write_text("not a folder\n", encoding="utf-8")
    else:
        assert os.geteuid() != 0, "this case needs a user that a read-only folder stops (not root)"
        folder.mkdir()
        folder.chmod(0o555)
    return folder


@pytest.mark.parametrize("exit_code", [0, 3])
@pytest.mark.parametrize("how", ["a-file-in-its-place", "a-read-only-folder"])
def test_s5_an_unwritable_record_keeps_the_exit_code_says_one_line_and_leaves_no_part(
        cli, launch, project, how, exit_code):
    folder = _unwritable(project, how)
    try:
        t.set_plan(cli, log=t.rich_log(), exit_code=exit_code)
        result = launch(ENG, T.tk)
        assert len(result.calls) == 1, f"the session was not started\n{result.describe()}"
        sid = result.calls[0]["session_id"]
        assert result.run.returncode == exit_code, (
            f"gov launch ended with {result.run.returncode}, not the session's {exit_code}\n{result.describe()}")
        naming = [line for line in result.run.stderr.splitlines() if t.SESSIONS_REL in line]
        assert len(naming) == 1, (
            f"stderr holds {len(naming)} lines naming the record's path ({t.SESSIONS_REL}), not one\n"
            f"stderr:\n{result.run.stderr}")
        if how == "a-file-in-its-place":
            assert folder.read_text(encoding="utf-8") == "not a folder\n", "the file in the folder's place was changed"
        else:
            assert sorted(os.listdir(folder)) == [], f"part of a record was left in {folder}: {os.listdir(folder)}"
        runtime = folder.parent
        left = [name for name in os.listdir(runtime) if sid in name or name.endswith((".tmp", ".json"))]
        assert not left, f"part of a record was left in {runtime}: {left}"
    finally:
        if folder.is_dir():
            folder.chmod(0o755)


def _reader():
    try:
        module = importlib.import_module("gov.launch.session_record")
    except ModuleNotFoundError as error:
        pytest.fail(f"there is no gov.launch.session_record to read a record back ({error})", pytrace=False)
    reader = getattr(module, "read_record", None)
    assert callable(reader), "gov.launch.session_record has no read_record(root, ticket, session_id)"
    return reader


def test_s6_a_record_a_launch_wrote_is_read_back_by_ticket_and_session_id(cli, launch, project):
    t.set_plan(cli, log=t.rich_log())
    result = launch(ENG, T.tk)
    assert result.run.returncode == 0 and len(result.calls) == 1, result.describe()
    sid = result.calls[0]["session_id"]
    on_disk = t.session_record(project, sid)
    read = _reader()(project, T.tk, sid)
    assert read == on_disk, f"read_record(root, {T.tk!r}, {sid!r}) does not return the record on disk:\n{read!r}"


def test_s6_the_cit_e_states_the_record_s_path_and_every_key():
    path = t.REPO_ROOT / t.CIT_E_REL
    assert path.is_file(), f"there is no CIT-E at {t.CIT_E_REL}"
    text = path.read_text(encoding="utf-8")
    assert t.SESSIONS_REL in text, f"the CIT-E does not state the record's path {t.SESSIONS_REL}/<session id>.json"
    missing = [key for key in (*t.HOUSEKEEPING, *t.MEASURED) if f"`{key}`" not in text and f'"{key}"' not in text]
    assert not missing, f"the CIT-E does not state the keys {missing} (as `key` or \"key\")"
    assert "read_record" in text, "the CIT-E does not name read_record(root, ticket, session_id)"
