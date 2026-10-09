"""Support code for the DEC-557 round of W1-02: a search from the root, a name filter, bounded time, a NUL byte.

Everything here is a stand-in in a temporary folder, as in
``w1_02_folders_support``, whose world this module uses unchanged: no file of
this repository is opened, and the held-out file's path is never spelled (it
comes from the guard's own module through ``w1_02_protected_support.HELD_REL``).

**Starts.** A search is asked from a *start*: the session's project root
(``root``), or the folder ``<P>`` a copy lies under: a sibling checkout outside
the session's project (``sibling``), a folder below the root that is not the
root (``nested``), the stand-in home folder (``home``, the settings file only).

**Forms.** A form is ``(tool, template, where)``. The template is a shell
command or a tool input; ``{abs}`` is the start (absolute), ``{rel}`` the start
as a relative path from the session's project, ``{f}`` a name filter. ``where``
is the working folder of the hook input: the session's project (``None``), the
start (``"start"``), or a source folder of the session's project (``"below"``).

A case's id and a failure message name a form and a start by a label, never by
a path, a filter or a command: a filter may be a protected file's own name.
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

import w1_02_copies_support as batch
import w1_02_folders_support as folders
import w1_02_protected_support as protected
import w1_02_support as support

SETTINGS = folders.SETTINGS
HELD = folders.HELD
FILES = folders.FILES
ACTORS = folders.ACTORS
WIDEST = folders.ORCHESTRATOR
# "Every role": the orchestrator asks every case; these three ask a share of them.
OTHER_ROLES = (folders.NOT_A_WRITER, "test-designer", folders.NO_ROLE)

ROOT = "root"
SITES = ("sibling", "nested", "home")
STARTS = (ROOT,) + SITES
# The copies under each <P>: the home folder holds a settings file only.
COPIES = [("sibling", name) for name in FILES] + [("nested", name) for name in FILES] + [("home", SETTINGS)]
COPY_IDS = [f"{site}-{name}" for site, name in COPIES]
BELOW_REL = folders.SOURCE_REL

# The read rule's decisions a refusal may name: those the earlier batches accept, and the two that order this round.
RULE_RE = re.compile(r"\bDEC-(508|525|548|553|557|562)\b")

make_world = folders.make_world


def start_of(world, start):
    """The folder a search starts from: the session's project root, or the ``<P>`` of a site."""
    return world.project if start == ROOT else world.site(start).root


def site_of(start):
    """The site whose files lie under the start (``own`` for the session's root)."""
    return "own" if start == ROOT else start


def files_under(start):
    """The protected files that lie under the start."""
    return (SETTINGS,) if start == "home" else tuple(FILES)


def ask_form(world, form, start, who=WIDEST, **values):
    """One call in ``form`` from ``start`` by ``who``; ``values`` fill further fields of the template."""
    tool_name, template, where = form
    at = start_of(world, start)
    values.update(abs=str(at), rel=folders.rel_from_project(world, at))
    cwd = {None: None, "start": at, "below": world.project / BELOW_REL}[where]
    if tool_name == "Bash":
        return folders.ask_bash(world, template.format(**values), who, cwd)
    return folders.ask(world, tool_name, {key: value.format(**values) for key, value in template.items()}, who, cwd)


def assert_refused_by_the_rule(result, what):
    """The read rule's own decision: ``deny``, exit code 0, a reason that names one of the rule's decisions.

    Exit code 2 (the guard's report of its own failure, DEC-110) and a denial by
    the allow-list (it names no decision of the rule) do not pass.
    """
    protected.assert_refused_by_rule(result, what)
    assert RULE_RE.search(protected.reason_of(result)), (
        f"{what} was denied, but not as a read of the two files: the reason names none of DEC-508, DEC-525, "
        f"DEC-548, DEC-553, DEC-557, DEC-562"
    )


def assert_names_a_rule_and_a_decision(result, what):
    """A refusal names a decision of the register, and words beside it."""
    reason = protected.reason_of(result)
    assert re.search(r"\bDEC-\d+\b", reason), f"the refusal of {what} names no decision"
    assert re.sub(r"\bDEC-\d+\b", "", reason).strip(" .:;()[],"), f"the refusal of {what} names a decision and no rule"


def assert_carries_none_of(result, values, what):
    """Nothing of ``values`` (paths, a filter, a piece of the command) appears in anything the hook wrote."""
    said = protected.output_of(result)
    shown = [index for index, value in enumerate(values) if str(value) and str(value) in said]
    # Positions only: a failure must not print what a refusal must not print.
    assert not shown, f"the refusal of {what} carries {len(shown)} value(s) of the call (positions {shown})"


def assert_says_nothing(result, world, start, name, what, more=()):
    """A refusal names the rule and the decision: no path, no folder, not the start, no value of the file.

    ``more`` are further things the refusal must not carry (the command's own words).
    """
    batch.assert_says_nothing_of_the_file(result, world, site_of(start), name, what)
    assert_carries_none_of(result, (start_of(world, start),) + tuple(more), what)


# --------------------------------------------------------------------------
# An answer in bounded time (DEC-562, probe finding 7)
# --------------------------------------------------------------------------

# The bound on the hook's own time, start to exit, for one decision. Generous: an ordinary decision takes well under
# a second on a busy machine; this is not the latency KPI.
BOUND_S = 5.0
# The test's own limit on the hook process, so that a run cannot hang. A hook that is still running then has no answer.
PROCESS_LIMIT_S = 8.0


def ask_timed(world, tool_name, tool_input, who=WIDEST, cwd=None):
    """One decision of the hook, run as a process, with the test's own limit on the process."""
    role, ticket, subagent = ACTORS[who]
    project = Path(world.project)
    data = support.payload(project, tool_name, tool_input, world.sandbox, subagent)
    if cwd is not None:
        data["cwd"] = str(cwd)
    argv = support._argv(project / support.installed_hook_rel())
    started = time.perf_counter()
    try:
        proc = subprocess.run(argv, input=json.dumps(data), capture_output=True, text=True, cwd=str(project),
                              env=support.hook_environment(project, world.sandbox, role, ticket),
                              timeout=PROCESS_LIMIT_S, check=False)
    except subprocess.TimeoutExpired:
        return support.HookResult("timeout", None, "", "", time.perf_counter() - started)
    seconds = time.perf_counter() - started
    return support.HookResult(support.classify(proc.returncode, proc.stdout), proc.returncode, proc.stdout,
                              proc.stderr, seconds)


def assert_answered_in_time(result, what):
    assert result.decision != "timeout", (
        f"{what}: no answer within the bound: the hook was still running after {PROCESS_LIMIT_S:.0f} s "
        f"(the bound is {BOUND_S:.0f} s)"
    )
    assert result.seconds <= BOUND_S, (
        f"{what}: no answer within the bound: the hook took {result.seconds:.1f} s (the bound is {BOUND_S:.0f} s)"
    )


def assert_refused_in_time(result, what):
    """Within the bound, and a refusal: by a rule (exit code 0) or as an input the rule gives up on (exit code 2)."""
    assert_answered_in_time(result, what)
    assert result.decision == "deny", (
        f"{what} was not refused: decision={result.decision} exit={result.returncode} in {result.seconds:.1f} s"
    )


def assert_decided_in_time(result, what):
    """Within the bound, and a decision: an allow (the input takes neither file in) or a refusal; never a hook error."""
    assert_answered_in_time(result, what)
    assert result.decision in ("allow", "deny"), (
        f"{what} got no decision: decision={result.decision} exit={result.returncode} in {result.seconds:.1f} s"
    )


def assert_allowed_in_time(result, what):
    assert_answered_in_time(result, what)
    protected.assert_allowed(result, what)
