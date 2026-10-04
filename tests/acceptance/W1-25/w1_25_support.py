"""Support code for the W1-25 acceptance tests (``gov checkpoint``).

The tests use the command only through its public interface: ``gov checkpoint``
with its arguments, its output and exit code, and the files it leaves in the
project. The ``gov`` console script, the temporary copy of the working tree and
the envelope assertions are W1-07's (``w1_07_support``).

The argument names, the frontmatter keys and the error codes below are those of
the recommended options of the decision packages in ``README.md`` (DP-2 to
DP-6). They are named once, here, so that another answer changes this file and
the one test file the package names.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

_W1_07 = str(Path(__file__).resolve().parents[1] / "W1-07")
if _W1_07 not in sys.path:
    sys.path.insert(0, _W1_07)

import w1_07_support as cli_support  # noqa: E402  the ``gov`` console script, without an install

NOT_IMPLEMENTED = cli_support.NOT_IMPLEMENTED
CHECKS_REL = cli_support.CHECKS_REL
SCHEMA_REL = "template/governance/kernel/schemas/checkpoint.schema.json"
FAMILY = "fresh-agent-reconstruction"
VALIDATOR = "check-jsonschema"

# The tickets the tests checkpoint: fixtures written into the temporary copy, never real tickets.
TICKET = "DAEO-zq25"
OTHER_TICKET = "DAEO-zq26"
INPUT_REL = "docs/w1-25-fixture-input.md"

# DP-2 (recommended option): the command's arguments and the record's frontmatter keys.
TRIGGERS = ("ticket-transition", "compaction", "stop")
KEY_TICKET, KEY_TRIGGER, KEY_NEXT, KEY_INPUTS, KEY_CREATED = "task", "trigger", "next_action", "inputs", "created"

# DP-5 (recommended option): the watchdog's error codes, exit code and reasons.
STALE, MISSING, EXIT_UNHEALTHY = "CHECKPOINT_STALE", "CHECKPOINT_MISSING", 3
REASON_AGE, REASON_COMMITS, REASON_CONTEXT, REASON_TRANSITION = "age", "commits", "context", "ticket-transition"
# Thresholds no test of another reason can reach.
LOOSE = ("--max-age-minutes", "600", "--max-commits", "50")

NEXT_STEP = "Run the W1-25 suite, then do step ZQ-7731"


def ticket_text(ticket, status="in_progress"):
    return (
        "---\n"
        f"id: {ticket}\n"
        f"status: {status}\n"
        "deps: []\n"
        "links: []\n"
        "created: 2026-10-04T00:00:00Z\n"
        "type: task\n"
        "priority: 2\n"
        "title: W1-25 acceptance fixture\n"
        "class: implementation\n"
        "state_class: AUTHORITATIVE\n"
        "role: engineer\n"
        "allowed_paths:\n"
        "- docs/w1-25-fixture/**\n"
        "kpis:\n"
        "  success:\n"
        "  - The fixture exists\n"
        "  failure:\n"
        "  - The fixture is missing\n"
        "profile: LITE\n"
        "---\n"
        "# W1-25 acceptance fixture\n"
    )


def ticket_path(project, ticket=TICKET):
    return Path(project) / ".tickets" / f"{ticket}.md"


def add_fixtures(project):
    """Two fixture tickets in progress and one input file, committed."""
    for ticket in (TICKET, OTHER_TICKET):
        path = ticket_path(project, ticket)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ticket_text(ticket), encoding="utf-8")
    (Path(project) / INPUT_REL).write_text("# An input of the fixture ticket\n", encoding="utf-8")
    cli_support.commit_all(project, "W1-25 fixtures")


def set_ticket_status(project, status, ticket=TICKET):
    """A ticket transition as tk makes it: the ticket's status changes, in a commit."""
    ticket_path(project, ticket).write_text(ticket_text(ticket, status), encoding="utf-8")
    cli_support.commit_all(project, f"{ticket} -> {status}")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# Envelopes
# --------------------------------------------------------------------------

def succeeded(run, interface):
    """The run succeeded with the API-0002 envelope; returns its ``result``."""
    envelope = cli_support.assert_envelope(run, interface, command="checkpoint")
    assert envelope["ok"] is True and run.returncode == 0, f"gov checkpoint did not succeed\n{run.describe()}"
    return envelope["result"]


def refused(run, interface, exit_codes=(1,)):
    """The run failed with a GovError envelope and one of ``exit_codes``; returns the error object."""
    envelope = cli_support.assert_envelope(run, interface, command="checkpoint")
    assert envelope["ok"] is False, f"gov checkpoint was expected to refuse\n{run.describe()}"
    assert envelope["error"]["code"] != NOT_IMPLEMENTED, f"gov checkpoint is not built yet\n{run.describe()}"
    assert run.returncode in exit_codes, f"expected an exit code in {exit_codes}\n{run.describe()}"
    return envelope["error"]


def reasons(error):
    found = error["details"].get("reasons")
    assert isinstance(found, list), f"error.details.reasons is not a list: {error}"
    return found


# --------------------------------------------------------------------------
# Writing and reading a checkpoint
# --------------------------------------------------------------------------

def write_args(ticket=TICKET, trigger="stop", next_step=NEXT_STEP, inputs=()):
    args = ["checkpoint", "--ticket", ticket, "--trigger", trigger, "--next", next_step]
    for rel in inputs:
        args += ["--input", rel]
    return (*args, "--json")


def checkpoint_path(project, result):
    """The file a write reported as ``result.path``, relative to the project."""
    rel = result.get("path")
    assert isinstance(rel, str) and rel, f"the result does not give the checkpoint's path: {result}"
    assert not os.path.isabs(rel), f"result.path is not relative to the project: {rel}"
    path = Path(project) / rel
    assert path.is_file(), f"the checkpoint {rel} was not written"
    return path


def split_record(path):
    """``(frontmatter text, body)`` of a record file."""
    lines = Path(path).read_text(encoding="utf-8").splitlines(keepends=True)
    assert lines and lines[0].strip() == "---", f"{path.name} does not open with frontmatter"
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "".join(lines[1:index]), "".join(lines[index + 1:])
    raise AssertionError(f"{path.name}: the frontmatter is never closed")


def frontmatter(path):
    text, _ = split_record(path)
    document = yaml.safe_load(text)
    assert isinstance(document, dict), f"{Path(path).name}: the frontmatter is not a map"
    return document


def rewrite_frontmatter(path, change):
    """Apply ``change(document)`` to a record's frontmatter and write the record back (a hand edit)."""
    text, body = split_record(path)
    document = yaml.safe_load(text)
    change(document)
    Path(path).write_text("---\n" + yaml.safe_dump(document, sort_keys=False) + "---\n" + body, encoding="utf-8")


def backdate(path, stamp="2020-01-01T00:00:00Z"):
    """Give a checkpoint an old ``created`` time (a hand edit of that one line)."""
    text = Path(path).read_text(encoding="utf-8")
    changed, count = re.subn(rf"(?m)^{KEY_CREATED}:.*$", f"{KEY_CREATED}: '{stamp}'", text, count=1)
    assert count == 1, f"{Path(path).name} has no '{KEY_CREATED}' line in its frontmatter"
    Path(path).write_text(changed, encoding="utf-8")


def inputs_of(document):
    found = document.get(KEY_INPUTS)
    assert isinstance(found, list) and found, f"the checkpoint has no '{KEY_INPUTS}' list: {document}"
    for item in found:
        assert isinstance(item, dict), f"an input is not a map: {item!r}"
    return found


def validate(project, document, workdir):
    """Validate a frontmatter document against W1-08's checkpoint schema in the project, with ``check-jsonschema``."""
    instance = Path(workdir) / "checkpoint-frontmatter.json"
    instance.write_text(json.dumps(document, indent=2, default=str), encoding="utf-8")
    done = subprocess.run([VALIDATOR, "--no-cache", "--schemafile", str(Path(project) / SCHEMA_REL), str(instance)],
                          capture_output=True, text=True, timeout=60, cwd=str(workdir))
    assert done.returncode == 0, f"{SCHEMA_REL} refuses the checkpoint:\n{(done.stdout + done.stderr).strip()}"


def state(project):
    """What a command that only reads leaves alone: the files, ``git status`` and the refs."""
    return (cli_support.snapshot(project), cli_support.porcelain(project), cli_support.git_state(project))


# --------------------------------------------------------------------------
# The family check's declared command
# --------------------------------------------------------------------------

def declaration(run, interface):
    """The fresh-agent-reconstruction declaration in the result of ``gov check --list --json``."""
    envelope = cli_support.assert_envelope(run, interface, command="check")
    assert envelope["ok"] is True, f"gov check --list did not succeed\n{run.describe()}"
    found = [item for item in cli_support.find_records(envelope["result"])
             if str(item.get("family", "")).strip().lower().replace(" ", "-") == FAMILY]
    assert len(found) == 1, (f"gov check --list names {len(found)} checks of the family {FAMILY}; the ticket "
                             f"registers one under {CHECKS_REL}/\n{run.describe()}")
    return found[0]


def run_declared_command(project, sandbox, command):
    """Run a check's ``command`` at the project root, with ``gov`` on PATH (DP-6: how W1-26 is assumed to run it)."""
    launcher = cli_support.write_launcher(project, sandbox)
    tools = sandbox.elsewhere / "path"
    tools.mkdir(exist_ok=True)
    wrapper = tools / "gov"
    wrapper.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{launcher}" "$@"\n', encoding="utf-8")
    wrapper.chmod(0o755)
    env = {
        "PATH": f"{tools}:{os.environ.get('PATH', '/usr/bin:/bin')}",
        "HOME": str(sandbox.home), "TMPDIR": str(sandbox.tmpdir), "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(Path(project) / "src"), "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
    }
    return subprocess.run(command, shell=True, cwd=str(project), env=env, capture_output=True, text=True,
                          timeout=cli_support.COMMAND_TIMEOUT_S, stdin=subprocess.DEVNULL)
