"""Round 3 (DEC-772 item 1): `gov release <version>` is the owner's alone, from a plain terminal, with a typed code.

KPI success 2: "The owner tags the release commit (agents never tag)". DEC-772 item 1, word for word: "`gov release`
is owner-only, from a plain terminal, like `gov approve` and the freeze lift: it refuses with a Claude Code process
among its ancestors, with `GOV_ROLE` or `GOV_TICKET` set, or without a terminal, and asks for a typed one-time
code." It replaces DEC-761 item 1's line "`gov release` refuses unless the role is orchestrator, or the owner in a
plain terminal" for the build form; `gov release --lock-from` (the template's Copier task) keeps its caller check
(the lead's reading; the last round's role cases hold it, unchanged).

Written from the KPI line, DEC-772 and the lead's specification for this round (DEC-136), without reading the
implementation. Two ways in, as W1-50 tests the freeze lift (DEC-409):

- **the seam** ``gov.release.command._release_test(root, version, ancestry=None, terminal=None)``, called in a new
  process with a planted chain and a planted terminal (``w2_16_support.drive_release``). A refusal raises
  ``GovError`` with code ``RELEASE_REFUSED`` and ``details["reason"]`` one of ``session``, ``ancestry``, ``role``,
  ``ticket``, ``terminal``, ``code``; it writes nothing (the suite's whole snapshot: every file and folder, refs,
  HEAD, index) and shows no code when it comes before the code is asked for. In each refusal case one cause alone
  holds: the rest is the owner's (a plain terminal's chain, a pseudo-terminal, the shown code typed back, GOV_ROLE
  and GOV_TICKET absent);
- **the real command**, ``python3 -m gov.cli.main release <version>``, with the ancestry the suite really has:
  refused, nothing written, no traceback, wherever the suite runs. Which reason is not asserted.

Every repository is a temporary stand-in (``w2_16_support``); nothing is tagged.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import w2_16_support as support

VERSION = support.FIRST_VERSION
SAYS = {
    "session": re.compile(r"claude|session", re.IGNORECASE),
    "ancestry": re.compile(r"ancest|process|cannot be read|unreadable|not readable", re.IGNORECASE),
    "role": re.compile(r"GOV_ROLE|role", re.IGNORECASE),
    "ticket": re.compile(r"GOV_TICKET|ticket", re.IGNORECASE),
    "terminal": re.compile(r"terminal|tty", re.IGNORECASE),
    "code": re.compile(r"code", re.IGNORECASE),
}
RUNS = 12


def _refused(repo, sandbox, reason, what, **planted):
    """One call of the seam with ``planted``: refused with ``reason``, said in words, nothing written."""
    before = support.snapshot(repo)
    run = support.release_through_the_seam(repo, sandbox, VERSION, limit=support.REFUSAL_LIMIT_S, **planted)
    assert run.status == support.REFUSED, f"{what}: `gov release {VERSION}` was not refused: {run.describe()}"
    assert run.error.get("code") == support.RELEASE_REFUSED, \
        f"{what}: the refusal's code is not {support.RELEASE_REFUSED}: {run.describe()}"
    assert run.reason == reason, f"{what}: the refusal's reason is {run.reason!r}, not {reason!r}: {run.describe()}"
    assert SAYS[reason].search(run.message), \
        f"{what}: the refusal's message does not say its reason ({reason}) in words: {run.message!r}"
    changed = support.snapshot_difference(before, support.snapshot(repo))
    assert not changed, f"{what}: a refused release wrote or changed: {changed[:10]}\n{run.describe()}"
    if reason != "code":
        assert not support.RELEASE_CODE.search(run.shown), \
            f"{what}: a code was shown on a call refused before the code is asked for: {run.shown!r}"
    return run


# --------------------------------------------------------------------------
# The positive control: the owner in person
# --------------------------------------------------------------------------

@pytest.mark.parametrize("ancestry", (support.PLAIN_TERMINAL, support.EDITOR_TERMINAL),
                         ids=("plain-terminal-to-init", "editor-terminal-to-systemd"))
def test_the_owner_in_person_builds_the_release(repo, sandbox, ancestry):
    """A planted chain that reaches process 1 (`init`, `systemd`) with no Claude Code session in it, a
    pseudo-terminal, the one code `RELEASE-<4 digits>` it shows typed back, GOV_ROLE and GOV_TICKET absent: the build
    is what it was before this round. The record under `docs/releases/<version>/`, nothing else changed, no commit,
    no tag; the result `{"version": <version>, "record": <the record's folder>}`."""
    before_head, before_refs = support.head(repo), support.git(repo, "for-each-ref")
    run = support.release_through_the_seam(repo, sandbox, VERSION, ancestry=ancestry)
    assert run.status == support.RELEASED, \
        f"as the owner in person, with the shown code typed back, `gov release {VERSION}` did not build: " \
        f"{run.describe()}"
    codes = set(run.codes)
    assert len(codes) == 1, f"the terminal did not show exactly one code RELEASE-<4 digits>: {run.shown!r}"
    code = codes.pop()
    assert run.typed == code + "\n"
    assert isinstance(run.result, dict) and run.result.get("version") == VERSION, \
        f"the result does not name the version {VERSION}: {run.result!r}"
    folder = support.RELEASES_REL + "/" + VERSION
    record = Path(str(run.result.get("record", "")))
    record = record if record.is_absolute() else repo / record
    assert record.resolve() == (repo / folder).resolve(), \
        f"the result's record is not the folder {folder}/: {run.result!r}"
    written = support.porcelain_paths(repo)
    assert written and all(support.under(rel, folder) for rel in written), \
        f"the build did not write its record under {folder}/ alone: {written[:10]}"
    assert support.head(repo) == before_head and support.git(repo, "for-each-ref") == before_refs, \
        f"the build made a commit, a tag or another ref\n{run.describe()}"
    assert code not in str(run.result), f"the code {code} is in the result: {run.result!r}"


# --------------------------------------------------------------------------
# Refused through the seam: each cause alone
# --------------------------------------------------------------------------

@pytest.mark.parametrize("shape", sorted(support.SESSION_ANCESTRIES))
def test_a_claude_code_session_among_the_ancestors_refuses_the_build(repo, sandbox, shape):
    """Reason `session`: the freeze lift's signs (DEC-409), with a terminal and the code typed back if shown."""
    _refused(repo, sandbox, "session", shape, ancestry=support.SESSION_ANCESTRIES[shape])


@pytest.mark.parametrize("shape", sorted(support.UNREADABLE_ANCESTRIES))
def test_a_chain_that_does_not_reach_process_1_refuses_the_build(repo, sandbox, shape):
    """Reason `ancestry`: the chain cannot be read whole up to the system's first process (`init` or `systemd`)."""
    _refused(repo, sandbox, "ancestry", shape, ancestry=support.UNREADABLE_ANCESTRIES[shape])


@pytest.mark.parametrize("role", ("orchestrator", "owner", "engineer", ""),
                         ids=lambda role: f"GOV_ROLE={role}" if role else "GOV_ROLE set and empty")
def test_gov_role_set_to_any_value_refuses_the_build(repo, sandbox, role):
    """Reason `role`: GOV_ROLE in the environment, whatever its value (`orchestrator`, `owner`, the empty value)."""
    _refused(repo, sandbox, "role", f"GOV_ROLE={role!r}", role=role)


@pytest.mark.parametrize("ticket", ("DAEO-49o5", ""),
                         ids=lambda ticket: f"GOV_TICKET={ticket}" if ticket else "GOV_TICKET set and empty")
def test_gov_ticket_set_to_any_value_refuses_the_build(repo, sandbox, ticket):
    """Reason `ticket`: GOV_TICKET in the environment, whatever its value (the empty value included)."""
    _refused(repo, sandbox, "ticket", f"GOV_TICKET={ticket!r}", ticket=ticket)


@pytest.mark.parametrize("terminal", (support.PIPE_IN, support.PIPE_OUT, support.PIPES, support.NO_TERMINAL))
def test_without_a_terminal_on_both_sides_the_build_refuses(repo, sandbox, terminal):
    """Reason `terminal`: piped input, an output that is no terminal, both pipes, or `/dev/null`. Whatever is shown
    would be typed back right: the product asks `os.isatty` itself, so the seam is no way round it."""
    _refused(repo, sandbox, "terminal", terminal, terminal=terminal)


@pytest.mark.parametrize("reply", (support.WRONG, support.EMPTY_LINE, support.END_OF_INPUT))
def test_anything_but_the_shown_code_refuses_the_build(repo, sandbox, reply):
    """Reason `code`: once every other check passed, one code is shown and one line read; a wrong code, an empty
    line or the end of input refuses at once (no second prompt, no wait)."""
    run = _refused(repo, sandbox, "code", reply, reply=reply)
    codes = set(run.codes)
    assert len(codes) == 1, f"{reply}: the terminal did not show exactly one code RELEASE-<4 digits>: {run.shown!r}"
    typed = (run.typed or "").strip()
    after_the_reply = run.shown[len(run.shown_before_reply):]
    assert not [code for code in support.RELEASE_CODE.findall(after_the_reply) if code != typed], \
        f"{reply}: a code was shown again after the reply: {after_the_reply!r}"


def test_the_code_comes_from_the_system_s_random_source(repo, sandbox):
    """Twelve calls in one process, Python's `random` seeded with 0 before each, a wrong code typed back: a code
    drawn from that generator would be the same twelve times; from the system's source, more than one."""
    before = support.snapshot(repo)
    runs = support.drive_release(repo, sandbox, VERSION, reply=support.WRONG, runs=RUNS, seed=0,
                                 limit=support.REFUSAL_LIMIT_S)
    support.seam_built(runs[0])
    assert len(runs) == RUNS and all(run.status == support.REFUSED and run.reason == "code" for run in runs), \
        f"not every call with a wrong code was refused for its code: {[run.describe() for run in runs]}"
    codes = [run.codes[0] if len(set(run.codes)) == 1 else None for run in runs]
    assert all(codes), f"a call did not show exactly one code: {[run.shown for run in runs]}"
    assert len(set(codes)) > 1, f"the code is the same on every call: {codes}"
    assert not support.snapshot_difference(before, support.snapshot(repo))


# --------------------------------------------------------------------------
# The real command, with the ancestry this suite runs under
# --------------------------------------------------------------------------

def _assert_the_command_refused(repo, before, run, what):
    assert run.returncode != 0, f"{what}: `gov release {VERSION}` was not refused\n{run.describe()}"
    assert "Traceback" not in run.output, f"{what}: the refusal ended in a traceback\n{run.describe()}"
    assert support.RELEASE_REFUSED in run.output, \
        f"{what}: the refusal does not give the code {support.RELEASE_REFUSED}\n{run.describe()}"
    assert not support.RELEASE_CODE.search(run.stdout), \
        f"{what}: a code was shown although a check before the code refused\n{run.describe()}"
    changed = support.snapshot_difference(before, support.snapshot(repo))
    assert not changed, f"{what}: a refused release wrote or changed: {changed[:10]}\n{run.describe()}"


def test_the_command_refuses_with_standard_input_from_dev_null(repo, sandbox):
    """`gov release 1.4.0` as the suite runs it (GOV_ROLE and GOV_TICKET absent, standard input `/dev/null`, its
    output a pipe): no terminal, so refused wherever the suite runs."""
    before = support.snapshot(repo)
    run = support.run_gov(repo, sandbox, "release", VERSION)
    _assert_the_command_refused(repo, before, run, "standard input from /dev/null")


def test_the_command_refuses_on_a_terminal_under_this_suite_s_ancestry(repo, sandbox):
    """`gov release 1.4.0` on a pseudo-terminal, the code typed back if one is shown, GOV_ROLE and GOV_TICKET
    absent. Run from an agent's session the chain holds a Claude Code session (or, inside a sandbox, cannot be read
    up to process 1): refused, nothing written. Where this suite's own chain has neither (a plain terminal, a
    nightly run), the owner's build would be right, and the case is skipped with that reason, never passed."""
    why = support.why_this_suite_s_ancestry_refuses()
    if why is None:
        pytest.skip("this suite's own chain reaches process 1 with no Claude Code session in it: from here "
                    "`gov release` on a terminal with the code typed back is the owner's build, so no refusal can "
                    "be asserted (DEC-772 item 1)")
    before = support.snapshot(repo)
    run = support.run_gov_on_a_terminal(repo, sandbox, "release", VERSION)
    _assert_the_command_refused(repo, before, run, f"on a terminal, this suite's chain refusing ({why})")
