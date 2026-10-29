"""W2-57, KPI line 2: the doctor probes get limits a loaded machine meets, and a probe exception keeps its text.

I4 finding 5, I2 F12, row W2-L409. Today ``gov doctor`` gives a tool's version probe 5 s, a venv's freeze-hash probe
10 s and Claude Code's version probe 3 s; a tool that answers later is read as not answering. And ``gov doctor``
catches only its own errors: an exception a probe raises (I4 F5 names a decode error from a git call that reads
text) ends it with a bare traceback and no envelope, so a close keeps no cause.

- A probed tool that answers well past today's limit is still read as answering (each probe kind once).
- A tool that never answers is still read as not answering, and ``gov doctor`` still ends.
- A probe exception ends ``gov doctor`` with an API-0002 envelope: ``ok`` false, an error code, and a message
  that names the exception and where it came from. The cause is built through ordinary means in a repository made
  from scratch: git's setting for names that are not ASCII, and a file whose name is Latin-1, renamed.

Every repository is a small one made from scratch under ``tmp_path``; the stand-in tools are first on the
``PATH`` ``gov`` runs with. ``gov doctor`` runs from this worktree's ``src/``.
"""

from __future__ import annotations

import pytest

import w2_57_support as support

VENV_PACKAGE = "w2-57-stand-in==1.0"


def _late_probe(kind, stand_ins, sandbox):
    """``(registry tools, what to read from the answer)`` for one probe kind, its stand-in answering late."""
    late = support.DOCTOR_PROBES[kind]["late_s"]
    if kind == "tool-version":            # the probe's plain form: ``<tool> --version``
        support.late_tool(stand_ins, "gitleaks", late, "8.30.0")
        return [{"name": "gitleaks", "version": "8.30.0"}], ("tool", "gitleaks")
    if kind == "tool-own-version-command":  # a tool with a version command of its own form
        support.late_tool(stand_ins, "node", late, "v22.23.3")
        return [{"name": "node", "version": "22.23.3"}], ("tool", "node")
    if kind == "venv-freeze-hash":        # the hash of ``uv pip freeze`` of a registered venv
        python = sandbox.home / ".local" / "share" / "gov-os" / "reranker-venv" / "bin" / "python"
        python.parent.mkdir(parents=True)
        python.write_text("a stand-in interpreter: only its place is read\n", encoding="utf-8")
        support.late_tool(stand_ins, "uv", late, VENV_PACKAGE)
        return [{"name": "reranker-venv", "version": "w2-57-stand-in 1.0",
                 "sha256": support.sha256_text(VENV_PACKAGE + "\n")}], ("hash", "reranker-venv")
    support.late_tool(stand_ins, "claude", late, "2.1.300 (Claude Code)")
    return [], ("claude", None)


@pytest.mark.parametrize("kind", sorted(support.DOCTOR_PROBES))
def test_a_probed_tool_that_answers_well_past_today_s_limit_is_read_as_answering(
    tmp_path, sandbox, stand_ins, monkeypatch, kind,
):
    """The stand-in answers after 15 s (25 s for the 10-second freeze probe): ``gov doctor`` reads its answer.
    About 16 to 26 s each."""
    tools, (what, name) = _late_probe(kind, stand_ins, sandbox)
    repo = support.doctor_repository(tmp_path / "repo", tools)
    run = support.run_doctor(repo, sandbox, monkeypatch, stand_ins)
    result = support.doctor_result(run)
    probe = support.DOCTOR_PROBES[kind]
    if what == "tool":
        entry = support.tool_entry(result, name)
        expected = tools[0]["version"]
        assert str(entry.get("found_version") or "").lstrip("v") == expected and entry.get("ok") is True, (
            f"{name} answered after {probe['late_s']} s (today's limit {probe['today_s']} s), but gov doctor "
            f"read it as not answering: {entry}"
        )
    elif what == "hash":
        entry = support.tool_entry(result, name)
        assert entry.get("sha256_match") is True and entry.get("ok") is True, (
            f"uv pip freeze answered after {probe['late_s']} s (today's limit {probe['today_s']} s), but gov "
            f"doctor did not read its hash: {entry}"
        )
    else:
        part = result.get("claude_code") or {}
        assert part.get("cli_version") == "2.1.300", (
            f"claude answered --version after {probe['late_s']} s (today's limit {probe['today_s']} s), but gov "
            f"doctor read no version: {part}"
        )


def test_a_probed_tool_that_never_answers_is_read_as_not_answering_and_doctor_still_ends(
    tmp_path, sandbox, stand_ins, monkeypatch,
):
    """A tool that never answers its version probe: ``gov doctor`` still ends (within the wait W1-07's
    ``[doctor]`` case gives it), and does not read the tool as answering or as the registered version. Takes the
    probe's own limit (about 5 s today)."""
    support.silent_tool(stand_ins, "gitleaks")
    repo = support.doctor_repository(tmp_path / "repo", [{"name": "gitleaks", "version": "8.30.0"}])
    run = support.run_doctor(repo, sandbox, monkeypatch, stand_ins)
    entry = support.tool_entry(support.doctor_result(run), "gitleaks")
    assert entry.get("found_version") is None and entry.get("ok") is False, (
        f"gitleaks never answered, but gov doctor reads it as answering: {entry}"
    )


def test_a_probe_exception_ends_doctor_with_the_envelope_and_its_text(
    tmp_path, sandbox, monkeypatch, interface,
):
    """A file whose name is not UTF-8, renamed, with git's ``core.quotePath`` off: ``gov doctor --json`` ends
    with one API-0002 envelope, ``ok`` false, an error code, and a message naming the exception and the part of
    doctor (or the git call) it came from; never a bare traceback. About 2 s."""
    repo = support.doctor_repository(tmp_path / "repo")
    before = support.run_doctor(repo, sandbox, monkeypatch)   # its parts, as doctor names them, before the cause
    sections = support.section_names(support.doctor_result(before))

    support.write_latin1_rename(repo)
    run = support.run_doctor(repo, sandbox, monkeypatch)
    envelope = support.cli.assert_envelope(run, interface, command="doctor")
    assert envelope["ok"] is False, (
        f"git's output is not UTF-8 and gov doctor reports success without saying so\n{run.describe()}"
    )
    message = envelope["error"]["message"]
    assert "UnicodeDecodeError" in message, (
        f"gov doctor failed, but its message does not name the exception (UnicodeDecodeError): {message!r}"
    )
    assert support.names_any(message, sections | {"git"}), (
        f"gov doctor's message names no part of doctor and no git call the exception came from: {message!r}"
    )
