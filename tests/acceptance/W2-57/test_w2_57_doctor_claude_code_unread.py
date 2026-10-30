"""W2-57, run 2 (DEC-925 item 3, R1; DEC-802): an unread Claude Code version is never a pass.

``gov doctor --json`` has a ``claude_code`` part. When a ``claude`` CLI is found (first on the ``PATH``) but its
version is not read, the part must not read "pass": it reads "unmeasured" or "fail" and says that the CLI's version
was not read, and ``gov doctor`` still ends with its envelope. The reviewer of run 1 found the opposite (F1): three
registered tools whose ``--version`` never answers spent doctor's time for its probes, the Claude Code probe got none,
and the part read "pass" with no CLI version, doctor ending with ``ok`` true and ``healthy`` true after about 90 s.

Two routes, each once:
- (a) a ``claude`` whose ``--version`` never answers;
- (b) the reviewer's construction: three tools pinned by the sha256 of their binaries, each silent on ``--version``,
  and a ``claude`` that answers at once with a version below doctor's minimum. Either its version is read and the
  part fails on the minimum, or it is not read and the part says so; never ``ok`` true with the part "pass". The
  same ``claude`` beside tools that answer at once is the control: the part fails on the minimum.

Out of scope: a machine with no ``claude`` CLI at all. Every repository is a small one made from scratch under
``tmp_path``; ``gov doctor`` runs from this worktree's ``src/`` with ``HOME`` in the case's folder, which is where it
looks for an editor extension (none is there), and the stand-ins first on the ``PATH``.
"""

from __future__ import annotations

import hashlib
import re
import shlex

import w2_57_support as support

BELOW_MINIMUM = "2.0.0"                      # an answer below doctor's minimum Claude Code version
SILENT_TOOLS = {"gitleaks": "8.30.0", "openspec": "1.0.0", "copier": "9.4.1"}   # name -> the version pinned
VERSION_NUMBER = re.compile(r"\d+\.\d+\.\d+")
NOT_READ = re.compile(
    r"not (?:been )?read|unread|could not|cannot|no answer|did not answer|not answer|gave no|timed? ?out|"
    r"time ?limit|deadline|budget|skipped|unknown", re.IGNORECASE)


def _texts(value) -> list[str]:
    """Every string in ``value``, at any depth."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _texts(item)]
    if isinstance(value, list):
        return [text for item in value for text in _texts(item)]
    return []


def _says_the_version_was_not_read(part: dict) -> list[str]:
    """What the part says of the CLI's version not being read: a text naming the CLI and its version, and that it
    was not read."""
    return [text for text in _texts(part) if re.search(r"\bcli\b|claude", text, re.IGNORECASE)
            and "version" in text.lower() and NOT_READ.search(text)]


def _claude_code(run, interface) -> tuple[dict, dict]:
    """``(envelope, claude_code part)``: ``gov doctor`` ended with its API-0002 envelope and reported the part."""
    envelope = support.cli.assert_envelope(run, interface, command="doctor")
    part = support.doctor_result(run).get("claude_code")
    assert isinstance(part, dict), f"gov doctor reported no claude_code part\n{run.describe()}"
    return envelope, part


def _version_read(part: dict) -> str | None:
    found = VERSION_NUMBER.search(str(part.get("cli_version") or ""))
    return found.group(0) if found else None


def _pinned_silent_tools(stand_ins) -> list[dict]:
    """Three tools that never answer ``--version``, each pinned in the registry by the sha256 of its stand-in."""
    tools = []
    for name, version in SILENT_TOOLS.items():
        binary = support.silent_tool(stand_ins, name)
        tools.append({"name": name, "version": version, "sha256": hashlib.sha256(binary.read_bytes()).hexdigest()})
    return tools


def _prompt_claude(stand_ins) -> None:
    """A ``claude`` that answers ``--version`` at once, below the minimum."""
    stand_ins.write("claude", f"printf '%s\\n' {shlex.quote(BELOW_MINIMUM + ' (Claude Code)')}")


def test_a_claude_whose_version_never_answers_is_not_a_pass_and_doctor_says_its_version_was_not_read(
    tmp_path, sandbox, stand_ins, monkeypatch, interface,
):
    """Route (a). ``claude`` is first on the ``PATH`` and never answers ``--version``: the part reads "unmeasured"
    or "fail", says the CLI's version was not read, and reads no version. Takes doctor's own limit for the probe."""
    support.silent_tool(stand_ins, "claude")
    repo = support.doctor_repository(tmp_path / "repo")
    run = support.run_doctor(repo, sandbox, monkeypatch, stand_ins)
    _envelope, part = _claude_code(run, interface)
    assert part.get("status") in ("unmeasured", "fail"), (
        f"claude never answered --version, but gov doctor's claude_code part reads {part.get('status')!r} "
        f"(after {run.seconds:.0f} s): {part}"
    )
    assert _says_the_version_was_not_read(part), (
        f"claude never answered --version; the claude_code part reads {part.get('status')!r} but does not say "
        f"that the CLI's version was not read: {part}"
    )
    assert _version_read(part) is None, f"claude never answered --version, but the part reads a version: {part}"


def test_probes_that_spend_doctor_s_time_never_leave_an_unread_claude_code_version_as_a_pass(
    tmp_path, sandbox, stand_ins, monkeypatch, interface,
):
    """Route (b), the reviewer's construction (F1). The control first: the ``claude`` that answers 2.0.0 at once,
    beside tools that answer at once, fails on the minimum. Then the same ``claude`` beside three silent tools
    pinned by hash: never ``ok`` true with the part "pass". Takes the three tools' probes (about 90 s on run 1's
    head)."""
    prompt = support.StandIns(tmp_path / "prompt-tools")
    for name, version in SILENT_TOOLS.items():
        prompt.write(name, f"printf '%s\\n' {shlex.quote(version)}")
    _prompt_claude(prompt)
    pinned = [{"name": name, "version": version} for name, version in SILENT_TOOLS.items()]
    control = support.run_doctor(support.doctor_repository(tmp_path / "control", pinned), sandbox, monkeypatch, prompt)
    _envelope, part = _claude_code(control, interface)
    assert part.get("status") == "fail" and _version_read(part) == BELOW_MINIMUM, (
        f"the control does not hold: claude answers {BELOW_MINIMUM} at once beside tools that answer at once, and "
        f"the claude_code part is not a failure on the minimum: {part}"
    )

    _prompt_claude(stand_ins)
    repo = support.doctor_repository(tmp_path / "repo", _pinned_silent_tools(stand_ins))
    run = support.run_doctor(repo, sandbox, monkeypatch, stand_ins)
    envelope, part = _claude_code(run, interface)
    status, read = part.get("status"), _version_read(part)
    assert status != "pass", (
        f"three tools that never answer --version took gov doctor {run.seconds:.0f} s, and its claude_code part "
        f"reads 'pass' (ok {envelope['ok']}) with the CLI's version {part.get('cli_version')!r}; claude answers "
        f"{BELOW_MINIMUM} at once, below the minimum: {part}"
    )
    if read is not None:
        assert read == BELOW_MINIMUM, f"claude answers {BELOW_MINIMUM}, but the part reads {read}: {part}"
        failures = [text for text in _texts(part) if BELOW_MINIMUM in text and "minimum" in text.lower()]
        assert status == "fail" and failures and envelope["ok"] is False, (
            f"the CLI's version {read} was read and is below the minimum, but the part reads {status!r} (ok "
            f"{envelope['ok']}) and names no failure on the minimum: {part}"
        )
    else:
        assert status in ("unmeasured", "fail") and _says_the_version_was_not_read(part), (
            f"the CLI's version was not read after {run.seconds:.0f} s of probes; the claude_code part reads "
            f"{status!r} and does not say that the version was not read: {part}"
        )
