"""W2-50, one option reader in the guard's read rule (DEC-778), as described behaviour (DEC-136): tests added after implementation.

Rewritten by W2-58's test designer (the lead's reading of P-W2-58-TD-2 (i);
DEC-821 item 3, DEC-857 item 3, item 4): every second name below stays refused,
for every role, now on the write side (a writable alias of a file the role may
not write). Each case now asks only a rule's refusal (exit code 0) whose message
names no path or folder of the file and carries nothing of it; the read rule's
decisions in the reason (and "as the plain form's") are no longer asked. The
paragraphs below describe the cases as first written.

The guard refuses every role a call that reads the protected pair (the
project's settings file and its held-out file), and counts as a read a command
that gives such a file, or a folder that holds one, a second name: the sources
of ``mv`` and of ``cp -l`` (``--link``) (DEC-548, DEC-553). The owner ruled
(DEC-778, 2026-10-18) that the guard reads every copy-like command one way, for
writes and for reads: ``mv`` and ``cp -l`` with value-taking options whose
value holds a ``t`` (joined and separate), and with ``--`` before and after the
source and the destination, are judged as the reads they are. Ordinary ``mv``
and ``cp -l`` of unprotected files still pass. Each case is tested through the
interface the suite already drives: the guard's PreToolUse hook with the call
on stdin.

**The stand-in for the protected file** is the fixture project's own
``.claude/settings.json``, written by the suite's ``make_project`` in the
test's temporary project (DEC-778 names it as a public means). The held-out
file is never named, typed or read. Its folder ``.claude/`` is the folder
that holds a protected file.

**Second names.** Each form was run with the tool (GNU coreutils 9.4) in a
temporary folder of the designer's own, on a stand-in file of the same name:
after it ran, the file's content was reachable at the new name (see the
README). Every case is asked of the guard only; nothing is run.

**The role.** The orchestrator on DAEO-zz90 may write the settings file and
the temp folder (its write rules let it write the new name and remove the old
one: ``mv -S.t <settings file> <temp>/…`` is allowed today), so its refusal is
the read rule's alone. A few forms are asked of the engineer too (the read rule
is for every role): it is refused today by its write rules, naming the file,
which is not the read refusal.

**"Refused as a read".** The plain form ``mv <settings file> <new name>`` is
refused today with the read rule's reason, which names the rule's decisions
(DEC-508, DEC-525) and no path. Each case asks the guard for that plain form
first (by the same role, from the same working folder; a premise), and asks
that its own refusal be a ``deny`` with exit code 0 whose reason names the same
decisions as the plain form's, at least one of DEC-508, DEC-525, DEC-548 and
DEC-553, and names neither the file's path nor its folder's. A refusal by the
allow-list (``Bash write to '…' denied for role …``) does not pass. The wording
is not prescribed.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

import w2_50_support as support

q = support.q
MAIN = support.MAIN
ORCHESTRATOR, ENGINEER = support.ORCHESTRATOR, support.ENGINEER

RULE_RE = re.compile(r"\bDEC-(508|525|548|553)\b")
DECISION_RE = re.compile(r"\bDEC-\d+\b")
PLAIN = "mv {F} {N}"          # the plain second name the guard refuses today as a read


# --------------------------------------------------------------------------
# The layout, one project for the module (the cases only ask the guard)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class World:
    sandbox: support.Sandbox
    project: Path
    paths: dict

    def cwd(self, name):
        return {"project": self.project, "temp": self.sandbox.tmpdir, "app-d": self.project / "src/app/d"}[name]


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    """The fixture project with its own settings file; the places by name.

    - ``F``: ``<project>/.claude/settings.json`` (the stand-in protected file); ``D``: ``<project>/.claude``;
    - ``N``, ``DD``: new names in the temp folder (a file, a folder); ``T``: a folder in the temp folder;
    - ``U``: ``src/app/data.json`` and ``UD``: ``src/app/cfg/`` (holding ``data.json``), unprotected files of the
      project in the engineer's paths; ``AN``: ``src/app/d/new.json``, ``AD``: ``src/app/d/``, allowed places.
    """
    sandbox = support.make_sandbox(tmp_path_factory.mktemp("one-reader") / "w2-50")
    project = support.make_project(sandbox, {"src/app/data.json": "{}\n", "src/app/cfg/data.json": "{}\n",
                                             "src/app/d/.keep": ""})
    temp = sandbox.tmpdir
    (temp / "w2-50-into").mkdir()
    paths = {
        "F": project / ".claude/settings.json", "D": project / ".claude",
        "N": temp / "w2-50-second-name", "DD": temp / "w2-50-moved", "T": temp / "w2-50-into",
        "U": project / "src/app/data.json", "UD": project / "src/app/cfg",
        "AN": project / "src/app/d/new.json", "AD": project / "src/app/d", "P": project,
    }
    assert paths["F"].is_file() and paths["D"].is_dir(), "premise: the fixture project has its own settings file"
    return World(sandbox, project, paths)


def _ask(world, command, role, cwd="project"):
    """The guard's decision on a Bash call made from a working folder, as the harness runs it."""
    folder = world.cwd(cwd)
    data = {
        "session_id": "w2-50-acceptance-session",
        "transcript_path": str(world.sandbox.elsewhere / "transcript.jsonl"),
        "cwd": str(folder),
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": support.tool_input("Bash", command),
        "tool_use_id": "toolu_w2_50_one_reader",
    }
    try:
        proc = subprocess.run([sys.executable, str(world.project / support.GUARD_REL)], input=json.dumps(data),
                              capture_output=True, text=True, cwd=str(folder),
                              env=support.base_environment(world.sandbox, role, MAIN.tk, world.project),
                              timeout=support.COMMAND_TIMEOUT_S)
        returncode, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        returncode, stdout, stderr = None, "", "timed out"
    decision, reason = support._decision(returncode, stdout, stderr)
    return support.Decision(decision, reason, returncode, stdout, stderr)


def _fill(world, template):
    return template.format(**{name: q(path) for name, path in world.paths.items()})


def _no_path_of_the_file(world, reason):
    """The forms of the file's path and its folder's that a read refusal does not name."""
    names = set()
    for key in ("F", "D"):
        path = str(world.paths[key])
        names |= {path, os.path.realpath(path)}
    names |= {".claude/settings.json"}
    return sorted(name for name in names if name in reason)


def _says_nothing_of_the_file(world, result, what):
    """No path or folder of the file in the refusal, and nothing of the file's contents (its one hook command)."""
    said = result.reason + "\n" + result.stdout + "\n" + result.stderr
    named = _no_path_of_the_file(world, said)
    assert not named, f"{what}: the refusal names the file's path or folder {named}: {result.reason[:400]!r}"
    assert support.GUARD_COMMAND not in said, f"{what}: the refusal carries the file's contents"


def _plain(world, role, cwd):
    """The plain second name's refusal (a premise): a rule's refusal that names no path and nothing of the file.

    Rewritten by W2-58 (the lead's reading of P-W2-58-TD-2 (i); DEC-548, DEC-553, DEC-778, DEC-821 item 4): a second
    name stays refused, now on the write side; the read rule's wording (DEC-508, DEC-525) is no longer asked.
    """
    command = _fill(world, PLAIN)
    result = _ask(world, command, role, cwd)
    what = f"premise: Bash `{command}` by the {role} (the plain second name)"
    assert result.decision == "deny" and result.returncode == 0, f"{what} was not refused: {result.describe()}"
    _says_nothing_of_the_file(world, result, what)
    return result


def assert_refused_as_a_read(world, result, plain, what):
    """Refused by a rule (exit code 0), with no path, no folder and nothing of the file in the message.

    Rewritten by W2-58 (TD-2 (i)): which rule refuses it, and which decisions its reason names, is no longer asked
    (before W2-58: the read rule's, with the plain form's decisions). ``plain`` is kept for the callers' premise.
    """
    assert result.decision == "deny", f"{what} was not refused: {result.describe()}"
    assert result.returncode == 0, f"{what} was refused, but not by a decision (exit {result.returncode}): " \
                                   f"{result.describe()}"
    _says_nothing_of_the_file(world, result, what)


# --------------------------------------------------------------------------
# The premise: the plain second names are refused as reads today
# --------------------------------------------------------------------------

PLAIN_FORMS = ("mv {F} {N}", "cp -l {F} {N}", "cp --link {F} {N}", "mv {D} {DD}", "cp -rl {D} {DD}")


@pytest.mark.parametrize("role", (ORCHESTRATOR, ENGINEER))
def test_the_plain_second_names_are_refused_as_reads(world, role):
    """The premise of every case below (held already by W1-02's suite for its own stand-ins)."""
    plain = _plain(world, role, "project")
    for template in PLAIN_FORMS:
        command = _fill(world, template)
        assert_refused_as_a_read(world, _ask(world, command, role), plain, f"Bash `{command}` by the {role}")


# --------------------------------------------------------------------------
# 1. A second name for the protected file is refused as a read, however the options are written (DEC-778)
# --------------------------------------------------------------------------

# id: (command, working folder). Each a second name, seen with the tool (README). ``-t`` as a new name lands in
# the working folder (the temp folder), as the tool puts it there.
SECOND_NAMES = {
    # mv: -S / --suffix / --backup with a value holding a t, joined, after =, as the next word, in clusters.
    "mv-S-joined": ("mv -S.t {F} {N}", "project"),
    "mv-S-joined-bare-t": ("mv -St {F} {N}", "project"),
    "mv-bS-joined-cluster": ("mv -bS.t {F} {N}", "project"),
    "mv-bSt-joined-cluster": ("mv -bSt {F} {N}", "project"),
    "mv-TS-joined-cluster": ("mv -TS.t {F} {N}", "project"),
    "mv-S-separate": ("mv -S .t {F} {N}", "project"),
    "mv-bS-separate-cluster": ("mv -bS .t {F} {N}", "project"),
    "mv-S-separate-value-dash-t": ("mv -S -t {F} {N}", "project"),
    "mv-suffix-equals": ("mv --suffix=.t {F} {N}", "project"),
    "mv-suffix-separate": ("mv --suffix .t {F} {N}", "project"),
    "mv-suffix-separate-value-dash-t": ("mv --suffix -t {F} {N}", "project"),
    "mv-backup-equals-t": ("mv --backup=t {F} {N}", "project"),
    "mv-S-joined-after-the-operands": ("mv {F} {N} -S.t", "project"),
    "mv-S-joined-relative": ("mv -S.t .claude/settings.json {N}", "project"),
    # mv: --, before the source, between, after both; a new name that starts with a dash after it.
    "mv-dashdash-before-the-source": ("mv -- {F} {N}", "project"),
    "mv-dashdash-between": ("mv {F} -- {N}", "project"),
    "mv-dashdash-after-both": ("mv {F} {N} --", "project"),
    "mv-S-joined-then-dashdash": ("mv -S.t -- {F} {N}", "project"),
    "mv-dashdash-then-a-new-name-dash-t": ("mv -- {F} -t", "temp"),
    "mv-dashdash-between-a-new-name-dash-t": ("mv {F} -- -t", "temp"),
    "mv-dashdash-between-a-new-name-dash-S-t": ("mv {F} -- -S.t", "temp"),
    "mv-backup-t-dashdash-a-new-name-dash-t": ("mv --backup=t -- {F} -t", "temp"),
    "mv-T-dashdash-a-new-name-dash-t": ("mv -T {F} -- -t", "temp"),
    # mv: -t, --target-directory, -T.
    "mv-t": ("mv -t {T} {F}", "project"),
    "mv-t-dashdash": ("mv -t {T} -- {F}", "project"),
    "mv-t-then-S-joined": ("mv -t {T} -S.t {F}", "project"),
    "mv-S-joined-then-t": ("mv -S.t -t {T} {F}", "project"),
    "mv-St-then-t": ("mv -St -t {T} {F}", "project"),
    "mv-target-directory-equals": ("mv --target-directory={T} {F}", "project"),
    "mv-target-directory-separate": ("mv --target-directory {T} {F}", "project"),
    "mv-T": ("mv -T {F} {N}", "project"),
    # cp -l / --link: -S / --suffix / --backup with a value holding a t.
    "cp-lS-joined-cluster": ("cp -lS.t {F} {N}", "project"),
    "cp-l-S-joined": ("cp -l -S.t {F} {N}", "project"),
    "cp-lbS-joined-cluster": ("cp -lbS.t {F} {N}", "project"),
    "cp-alS-joined-cluster": ("cp -alS.t {F} {N}", "project"),
    "cp-lTS-joined-cluster": ("cp -lTS.t {F} {N}", "project"),
    "cp-link-S-joined": ("cp --link -S.t {F} {N}", "project"),
    "cp-lS-separate-cluster": ("cp -lS .t {F} {N}", "project"),
    "cp-l-S-separate-value-dash-t": ("cp -l -S -t {F} {N}", "project"),
    "cp-lS-separate-value-dash-t-cluster": ("cp -lS -t {F} {N}", "project"),
    "cp-l-suffix-equals": ("cp -l --suffix=.t {F} {N}", "project"),
    "cp-l-suffix-separate": ("cp -l --suffix .t {F} {N}", "project"),
    "cp-l-suffix-separate-value-dash-t": ("cp -l --suffix -t {F} {N}", "project"),
    "cp-l-backup-equals-t": ("cp -l --backup=t {F} {N}", "project"),
    "cp-l-S-joined-after-the-operands": ("cp -l {F} {N} -S.t", "project"),
    "cp-lS-joined-relative": ("cp -lS.t .claude/settings.json {N}", "project"),
    # cp -l: the other value-taking options of cp --help, with a value holding a t.
    "cp-l-sparse-equals-auto": ("cp -l --sparse=auto {F} {N}", "project"),
    "cp-l-sparse-separate-always": ("cp -l --sparse always {F} {N}", "project"),
    "cp-l-reflink-equals-auto": ("cp -l --reflink=auto {F} {N}", "project"),
    "cp-l-preserve-equals-timestamps": ("cp -l --preserve=timestamps {F} {N}", "project"),
    "cp-l-no-preserve-equals-timestamps": ("cp -l --no-preserve=timestamps {F} {N}", "project"),
    "cp-l-no-preserve-separate-timestamps": ("cp -l --no-preserve timestamps {F} {N}", "project"),
    "cp-l-context-equals-t": ("cp -l --context=t {F} {N}", "project"),
    # cp -l: --.
    "cp-l-dashdash-before-the-source": ("cp -l -- {F} {N}", "project"),
    "cp-l-dashdash-between": ("cp -l {F} -- {N}", "project"),
    "cp-l-dashdash-after-both": ("cp -l {F} {N} --", "project"),
    "cp-l-S-joined-then-dashdash": ("cp -l -S.t -- {F} {N}", "project"),
    "cp-l-dashdash-then-a-new-name-dash-t": ("cp -l -- {F} -t", "temp"),
    "cp-l-dashdash-between-a-new-name-dash-t": ("cp -l {F} -- -t", "temp"),
    "cp-l-dashdash-then-a-new-name-dash-S-t": ("cp -l -- {F} -S.t", "temp"),
    "cp-l-sparse-auto-dashdash-a-new-name-dash-t": ("cp -l --sparse=auto -- {F} -t", "temp"),
    "cp-l-reflink-auto-dashdash-between-a-new-name-dash-t": ("cp -l --reflink=auto {F} -- -t", "temp"),
    # cp -l: -t, --target-directory, -T.
    "cp-lt-cluster": ("cp -lt {T} {F}", "project"),
    "cp-l-t-dashdash": ("cp -l -t {T} -- {F}", "project"),
    "cp-l-t-then-S-joined": ("cp -l -t {T} -S.t {F}", "project"),
    "cp-lS-joined-then-t": ("cp -lS.t -t {T} {F}", "project"),
    "cp-l-target-directory-equals": ("cp -l --target-directory={T} {F}", "project"),
    "cp-lT-cluster": ("cp -lT {F} {N}", "project"),
    # The folder that holds the file as the source.
    "folder-mv-S-joined": ("mv -S.t {D} {DD}", "project"),
    "folder-mv-St": ("mv -St {D} {DD}", "project"),
    "folder-mv-S-joined-then-dashdash": ("mv -S.t -- {D} {DD}", "project"),
    "folder-mv-dashdash-between-a-new-name-dash-t": ("mv {D} -- -t", "temp"),
    "folder-mv-S-joined-then-t": ("mv -S.t -t {T} {D}", "project"),
    "folder-mv-S-joined-then-T": ("mv -S.t -T {D} {DD}", "project"),
    "folder-mv-S-joined-relative": ("mv -S.t .claude {DD}", "project"),
    "folder-cp-rlS-joined-cluster": ("cp -rlS.t {D} {DD}", "project"),
    "folder-cp-rlS-joined-then-dashdash": ("cp -rlS.t -- {D} {DD}", "project"),
    "folder-cp-rl-S-joined-then-t": ("cp -rl -S.t -t {T} {D}", "project"),
    "folder-cp-rl-dashdash-between-a-new-name-dash-t": ("cp -rl {D} -- -t", "temp"),
}


@pytest.mark.parametrize("case", sorted(SECOND_NAMES))
def test_a_second_name_for_the_protected_file_is_refused_as_a_read_however_the_options_are_written(world, case):
    template, cwd = SECOND_NAMES[case]
    plain = _plain(world, ORCHESTRATOR, cwd)
    command = _fill(world, template)
    what = (f"Bash `{command}` from the {cwd} folder by the {ORCHESTRATOR} ({case}; a second name for the settings "
            f"file or its folder)")
    assert_refused_as_a_read(world, _ask(world, command, ORCHESTRATOR, cwd), plain, what)


# For every role: a few forms asked of the engineer, whom its write rules refuse today, naming the file.
FOR_EVERY_ROLE = ("mv-S-joined", "mv-S-separate-value-dash-t", "mv-S-joined-after-the-operands",
                  "mv-dashdash-then-a-new-name-dash-t", "cp-lS-joined-cluster", "cp-l-dashdash-between-a-new-name-dash-t",
                  "folder-mv-S-joined", "folder-cp-rlS-joined-cluster", "mv-dashdash-before-the-source", "cp-l-t-dashdash")


@pytest.mark.parametrize("case", FOR_EVERY_ROLE)
def test_a_second_name_is_refused_as_a_read_also_for_a_role_that_may_not_write_the_file(world, case):
    template, cwd = SECOND_NAMES[case]
    plain = _plain(world, ENGINEER, cwd)
    command = _fill(world, template)
    what = (f"Bash `{command}` from the {cwd} folder by the {ENGINEER} ({case}; a second name for the settings "
            f"file or its folder)")
    assert_refused_as_a_read(world, _ask(world, command, ENGINEER, cwd), plain, what)


# --------------------------------------------------------------------------
# 2. Controls: the same forms of unprotected files stay allowed
# --------------------------------------------------------------------------

# id: (command, working folder). The source an unprotected file (or folder) of src/app/, the destination in
# src/app/d/ (or src/app/), which both roles may write. ``-t`` as a new name lands in src/app/d/.
UNPROTECTED = {
    "mv-S-joined": ("mv -S.t {U} {AN}", "project"),
    "mv-St": ("mv -St {U} {AN}", "project"),
    "mv-S-separate-value-dash-t": ("mv -S -t {U} {AN}", "project"),
    "mv-suffix-separate-value-dash-t": ("mv --suffix -t {U} {AN}", "project"),
    "mv-backup-equals-t": ("mv --backup=t {U} {AN}", "project"),
    "mv-S-joined-after-the-operands": ("mv {U} {AN} -S.t", "project"),
    "mv-dashdash-before-the-source": ("mv -- {U} {AN}", "project"),
    "mv-dashdash-between": ("mv {U} -- {AN}", "project"),
    "mv-dashdash-after-both": ("mv {U} {AN} --", "project"),
    "mv-dashdash-then-a-new-name-dash-t": ("mv -- {U} -t", "app-d"),
    "mv-t-then-S-joined": ("mv -t {AD} -S.t {U}", "project"),
    "mv-t-dashdash": ("mv -t {AD} -- {U}", "project"),
    "mv-target-directory-equals": ("mv --target-directory={AD} {U}", "project"),
    "mv-T": ("mv -T {U} {AN}", "project"),
    "mv-S-joined-T": ("mv -S.t -T {U} {AN}", "project"),
    "folder-mv-S-joined": ("mv -S.t {UD} {P}/src/app/moved", "project"),
    "cp-lS-joined-cluster": ("cp -lS.t {U} {AN}", "project"),
    "cp-l-S-separate-value-dash-t": ("cp -l -S -t {U} {AN}", "project"),
    "cp-l-S-joined-after-the-operands": ("cp -l {U} {AN} -S.t", "project"),
    "cp-l-backup-equals-t": ("cp -l --backup=t {U} {AN}", "project"),
    "cp-l-sparse-equals-auto": ("cp -l --sparse=auto {U} {AN}", "project"),
    "cp-l-reflink-equals-auto": ("cp -l --reflink=auto {U} {AN}", "project"),
    "cp-l-preserve-equals-timestamps": ("cp -l --preserve=timestamps {U} {AN}", "project"),
    "cp-l-no-preserve-equals-timestamps": ("cp -l --no-preserve=timestamps {U} {AN}", "project"),
    "cp-l-dashdash-before-the-source": ("cp -l -- {U} {AN}", "project"),
    "cp-l-dashdash-then-a-new-name-dash-t": ("cp -l -- {U} -t", "app-d"),
    "cp-l-t-dashdash": ("cp -l -t {AD} -- {U}", "project"),
    "cp-lt-cluster": ("cp -lt {AD} {U}", "project"),
    "cp-lT-cluster": ("cp -lT {U} {AN}", "project"),
    "folder-cp-rlS-joined-cluster": ("cp -rlS.t {UD} {P}/src/app/linked", "project"),
}


@pytest.mark.parametrize("role", (ORCHESTRATOR, ENGINEER))
@pytest.mark.parametrize("case", sorted(UNPROTECTED))
def test_the_same_forms_of_an_unprotected_file_stay_allowed(world, case, role):
    template, cwd = UNPROTECTED[case]
    command = _fill(world, template)
    support.assert_allowed(_ask(world, command, role, cwd),
                           f"Bash `{command}` from the {cwd} folder by the {role} ({case}; an unprotected file into "
                           f"an allowed place)")


# A plain cp (no -l) of an unprotected file with such options is a copy, not a read of the pair.
PLAIN_COPIES = {
    "cp-S-joined": ("cp -S.t {U} {AN}", "project"),
    "cp-S-separate-value-dash-t": ("cp -S -t {U} {AN}", "project"),
    "cp-S-joined-after-the-operands": ("cp {U} {AN} -S.t", "project"),
    "cp-t-then-S-joined": ("cp -t {AD} -S.t {U}", "project"),
    "cp-preserve-equals-timestamps": ("cp --preserve=timestamps {U} {AN}", "project"),
    "cp-sparse-equals-auto": ("cp --sparse=auto {U} {AN}", "project"),
    "cp-dashdash-then-a-new-name-dash-t": ("cp -- {U} -t", "app-d"),
    "cp-rS-joined-folder": ("cp -rS.t {UD} {P}/src/app/copied", "project"),
}


@pytest.mark.parametrize("role", (ORCHESTRATOR, ENGINEER))
@pytest.mark.parametrize("case", sorted(PLAIN_COPIES))
def test_a_plain_copy_of_an_unprotected_file_with_such_options_is_not_refused_as_a_read(world, case, role):
    template, cwd = PLAIN_COPIES[case]
    command = _fill(world, template)
    support.assert_allowed(_ask(world, command, role, cwd),
                           f"Bash `{command}` from the {cwd} folder by the {role} ({case}; a plain copy of an "
                           f"unprotected file into an allowed place)")
