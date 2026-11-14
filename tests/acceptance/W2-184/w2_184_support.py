"""Support code for the W2-184 acceptance tests (standard library and PyYAML only).

W2-184 (DAEO-6f0s) makes ``gov launch`` choose a worker's model and effort by RUBRIC-2: the ticket's criticality
(``governance/project/criticality.yaml``, never the ticket's ``class``), the role file's ``Launch by criticality`` line,
an effort floor, ``--reason``, ``--trial``, a promotion from the ticket's probe records, and a FULL ticket's two reviews
(``--owner-named``). The tests drive the public interface: ``gov launch`` through its console-script entry point, and,
for the three options the CLI does not carry yet (interface 7.2), ``gov.launch.launcher.launch(...)`` with its keyword
arguments in a child Python process that has the environment ``gov launch`` gets. They read what the stand-in CLI is
handed and what the launch record folder holds.

The launch machinery (sandbox HOME, stand-in CLI at ``~/.local/bin/claude``, open resource gate, fixture project, run of
``gov``) is W2-60a's own support module, imported as ``b``; nothing of it is changed here. This module adds the
RUBRIC-2 fixtures: role files with tables, tickets of chosen profile and paths, ``criticality.yaml``, trial and probe
records, one launch function, and one assertion that states a whole launch (the line, the record, the subagent model).
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "W2-60a"))
import w2_60a_support as b  # noqa: E402

OPUS = "claude-opus-5-5"
SONNET = "claude-sonnet-5-5"
HAIKU5 = "claude-haiku-5-5"
HAIKU_DATED = "claude-haiku-4-5-20251001"

ENGINEER, TEST_DESIGNER, AUDITOR = b.ENGINEER, b.TEST_DESIGNER, b.AUDITOR
RESEARCH, PRODUCT_SPEC = b.RESEARCH, b.PRODUCT_SPEC
WORKER_ROLES = b.WORKER_ROLES
CLASSES = ("C3", "C2", "C1", "C0")

CRITICALITY_REL = "governance/project/criticality.yaml"
TRIALS_REL = "governance/project/trials"
PROBES_REL = "docs/probes"
HEAD = "- **Launch by criticality:**"

# Every role file's default line differs from every table entry below, so a value seen on the line is seen to come from
# the line the launcher chose.
DEFAULT = (SONNET, "medium")

# The fixture role files' tables: (model, effort) for C3, C2, C1, C0. Research and product-spec are launched on a ticket
# whose own folder or kind the role needs; the others on any in_progress ticket.
TABLES = {
    ENGINEER: {"C3": (OPUS, "high"), "C2": (SONNET, "high"), "C1": (SONNET, "xhigh"), "C0": (HAIKU5, "low")},
    TEST_DESIGNER: {"C3": (OPUS, "max"), "C2": (SONNET, "xhigh"), "C1": (HAIKU5, "high"), "C0": (HAIKU5, "low")},
    AUDITOR: {"C3": (OPUS, "high"), "C2": (OPUS, "high"), "C1": (SONNET, "high"), "C0": (HAIKU_DATED, "medium")},
    PRODUCT_SPEC: {"C3": (OPUS, "xhigh"), "C2": (SONNET, "xhigh"), "C1": (HAIKU5, "medium"),
                   "C0": (HAIKU_DATED, "low")},
    RESEARCH: {"C3": (OPUS, "xhigh"), "C2": (OPUS, "high"), "C1": (SONNET, "high"), "C0": (HAIKU5, "low")},
}

# Where each class's ticket works: the fixture criticality file's rules match these folders; C0 is the default.
AREA = {"C3": "src/critical/core", "C2": "src/product/app", "C1": "docs/guides", "C0": "notes/misc"}
EXP_AREA = {cls: f"experiments/{cls.lower()}/exp-1" for cls in CLASSES}
RULES = [
    {"class": "C3", "paths": ["src/critical/*", "experiments/c3/*"]},
    {"class": "C2", "paths": ["src/product/*", "experiments/c2/*"]},
    {"class": "C1", "paths": ["docs/*", "experiments/c1/*"]},
]
CODE = {ENGINEER: "eng", TEST_DESIGNER: "td", AUDITOR: "aud", PRODUCT_SPEC: "ps", RESEARCH: "res"}

NEW_KEYS = ("tier", "criticality", "model_source", "effort_source", "trial", "promotion", "effort_reason",
            "owner_named", "review_round")
MISSING = "<<missing>>"


def tier_of(model):
    return model.split("-")[1]


# --------------------------------------------------------------------------
# Role files, criticality.yaml, tickets
# --------------------------------------------------------------------------

def table_line(table, full=None, classes=CLASSES):
    """The ``Launch by criticality`` line: one entry per class; ``full[cls] = ((model, effort), (model, effort))`` writes
    that entry in the FULL form (first pair on FULL, second otherwise)."""
    full = full or {}
    entries = []
    for cls in classes:
        if cls in full:
            (m1, e1), (m2, e2) = full[cls]
            entries.append(f"{cls} model {m1}, effort {e1} on FULL, model {m2}, effort {e2} otherwise")
        else:
            model, effort = table[cls]
            entries.append(f"{cls} model {model}, effort {effort}")
    return f"{HEAD} " + "; ".join(entries)


def role_file(role, table=None, full=None, lines=(), default=DEFAULT):
    """A fixture role file: W2-60a's, with this ticket's lines after the default line. ``lines`` are written as given."""
    dline = b.default_line(*default)
    text = b.role_text(role, default=dline)
    extra = ([table_line(table, full)] if table is not None else []) + list(lines)
    if extra:
        text = text.replace(dline + "\n", dline + "\n" + "\n".join(extra) + "\n", 1)
    return text


def write_role(project, role, table="own", full=None, lines=(), default=DEFAULT):
    """Rewrite one role file; ``table="own"`` is the role's fixture table, ``None`` writes no table line."""
    table = TABLES[role] if table == "own" else table
    return b.write(b.role_path(project, role), role_file(role, table, full, lines, default))


def crit_text(default="C0", opus=OPUS, rules="own", version=1):
    data = {"version": version, "default": default, "opus": opus, "rules": RULES if rules == "own" else rules}
    return yaml.safe_dump(data, sort_keys=False)


def write_criticality(project, text=None):
    return b.write(Path(project) / CRITICALITY_REL, crit_text() if text is None else text)


def drop_criticality(project):
    (Path(project) / CRITICALITY_REL).unlink()


def ticket_text(tk, role, allowed, profile, kind):
    base = b.Ticket(tk, role, f"W2-184-{tk}", tuple(allowed), cls=kind)
    return b.ticket_text(base).replace("profile: FULL\n", f"profile: {profile}\n", 1)


def ticket(project, role, cls="C2", profile="STANDARD", *, tk=None, allowed=None, kind="implementation"):
    """Plant an in_progress ticket (not committed) whose profile and allowed paths put it in ``cls``; returns its id.
    A research ticket works in one experiment folder; the roles the guard ties to their own ticket (engineer, research,
    product-spec) get a ticket of their own role, the others one of the engineer's."""
    tk = tk or f"DAEO-{CODE[role]}{cls.lower()}{profile[0].lower()}"
    if allowed is None:
        area = EXP_AREA[cls] if role == RESEARCH else AREA[cls]
        allowed = [f"{area}/**"]
    owner = role if role in (ENGINEER, RESEARCH, PRODUCT_SPEC) else ENGINEER
    b.write(Path(project) / ".tickets" / f"{tk}.md", ticket_text(tk, owner, allowed, profile, kind))
    return tk


def make_project(sandbox, tables=True, criticality=True):
    """The fixture project: W2-60a's, with a role file per worker role (a table each), a ``criticality.yaml`` and the
    experiment folders the research tickets work in."""
    extra = {f"{b.ROLES_REL}/{role}.md": role_file(role, TABLES[role] if tables else None) for role in WORKER_ROLES}
    if criticality:
        extra[CRITICALITY_REL] = crit_text()
    for area in EXP_AREA.values():
        extra[f"{area}/README.md"] = "# an experiment\n"
    return b.make_project(sandbox, extra=extra)


# --------------------------------------------------------------------------
# Trial and probe records
# --------------------------------------------------------------------------

def trial_data(tk, role=ENGINEER, criticality="C2", model=HAIKU5, effort="high", tickets=None, reviewer=OPUS):
    return {"role": role, "criticality": criticality, "model": model, "effort": effort,
            "tickets": tickets if tickets is not None else ["DAEO-aaaa", tk], "reviewer": {"model": reviewer}}


def plant_trial(project, trial_id, data=None, raw=None, **kwargs):
    """``governance/project/trials/<id>.yaml``: ``data`` (or ``trial_data(**kwargs)``) as YAML, or ``raw`` text."""
    text = raw if raw is not None else yaml.safe_dump(data if data is not None else trial_data(**kwargs),
                                                      sort_keys=False)
    return b.write(Path(project) / TRIALS_REL / f"{trial_id}.yaml", text)


def verdict_block(*consequences):
    """JUDGEMENT.md's fenced ``verdict`` block (JSON), one finding per consequence."""
    findings = [{"id": f"F{n}", "scope": "in", "ordinary_work": "yes", "consequence": consequence}
                for n, consequence in enumerate(consequences, 1)]
    data = {"kpis": [{"kpi": "success-1", "verdict": "fail" if findings else "pass", "findings": findings}]}
    return "```verdict\n" + json.dumps(data, indent=2) + "\n```\n"


def plant_probe(project, tk, name, judgement="pass", *, kind="probe", verdict=None, raw=None, folder=None):
    """A probe record ``docs/probes/<ticket>/<name>`` with front matter ``type: <kind>`` and ``judgement``, and, when
    ``verdict`` (a block's text) is given, that block in its body; ``raw`` is the whole file's text instead."""
    rel = f"{PROBES_REL}/{folder or tk}/{name}"
    if raw is None:
        raw = f"---\ntype: {kind}\ntask: {tk}\njudgement: {judgement}\n---\n\n# Probe record\n\n{verdict or ''}"
    b.write(Path(project) / rel, raw)
    return rel


def promote_two_failed(project, tk):
    """Two failed reviews: the second, in sorted path order, is ``02-failed.md``."""
    plant_probe(project, tk, "01-failed.md", "fail")
    return plant_probe(project, tk, "02-failed.md", "failed")


# --------------------------------------------------------------------------
# Linked worktrees and launch records (batch td-5: interface 5.1a)
# --------------------------------------------------------------------------

def commit_all(tree, message):
    """Commit everything in ``tree`` (the main checkout or a linked worktree) on its own branch."""
    b.git(tree, "add", "-A")
    b.git(tree, "commit", "-q", "-m", message)


def add_worktree(project, path, branch):
    """A linked worktree of the fixture project at ``path`` on a new ``branch`` from the main checkout's HEAD: it shares
    the main checkout and its launch record folder."""
    b.git(project, "worktree", "add", "-q", "-b", branch, str(path))
    return Path(path)


def remove_worktree(project, path):
    b.git(project, "worktree", "remove", "--force", str(path))


def plant_launch_record(sandbox, template, **changes):
    """A launch record in the shared folder: ``template`` (a real launch's record) with ``changes`` and a new session
    id, as ``<session id>.json``. Returns the session id."""
    data = dict(template)
    data.update(changes)
    sid = str(uuid.uuid4())
    data["session_id"] = sid
    b.write(Path(sandbox.records) / f"{sid}.json", json.dumps(data, indent=2) + "\n")
    return sid


# --------------------------------------------------------------------------
# Launching
# --------------------------------------------------------------------------

NOT_GIVEN = object()

# The CLI has no --reason, --trial or --owner-named yet (interface 7.2): the launcher is called with its keyword
# arguments, in a child process with the environment ``gov launch`` gets, and ends as the CLI does: a refusal on
# standard error, ``gov launch: <code>: <message>``, exit code 1. A launch() that does not take an option ends 97.
DRIVER = r'''
import inspect, json, sys
from pathlib import Path
from gov.cli.errors import GovError
from gov.launch import launcher

spec = json.loads(sys.argv[1])
missing = [name for name in spec["kw"] if name not in inspect.signature(launcher.launch).parameters]
if missing:
    print("driver: launcher.launch() does not take the keyword argument(s): " + ", ".join(missing), file=sys.stderr)
    sys.exit(97)
try:
    code = launcher.launch(Path(spec["root"]), spec["role"], spec["ticket"], spec["cli_args"], **spec["kw"])
except GovError as error:
    print(f"gov launch: {error.code}: {error.message}", file=sys.stderr)
    sys.exit(error.exit_code)
sys.exit(code)
'''


def launch(sandbox, cli, role, tk, *cli_args, reason=NOT_GIVEN, trial=NOT_GIVEN, owner_named=NOT_GIVEN, cwd=None):
    """``gov launch <role> <ticket> [-- <cli_args>]``; with ``reason``, ``trial`` or ``owner_named`` the launcher's
    function is called with that keyword argument instead (interface 7.2). ``cwd``: the tree launched from (a linked
    worktree of the fixture project; its records go to the main checkout's folder), else the project. Returns W2-60a's
    ``Launch``."""
    options = {name: value for name, value in (("reason", reason), ("trial", trial), ("owner_named", owner_named))
               if value is not NOT_GIVEN}
    root = Path(cwd) if cwd is not None else Path(sandbox.project)
    records = Path(sandbox.records)
    before_calls, before = len(b.calls(cli)), b._listing(records)
    started = time.time()
    if not options:
        run = b.run_gov(sandbox, root, "launch", role, tk, *(("--", *cli_args) if cli_args else ()))
    else:
        spec = {"root": str(root), "role": role, "ticket": tk, "cli_args": list(cli_args), "kw": options}
        done = subprocess.run([sys.executable, "-c", DRIVER, json.dumps(spec)], cwd=str(root),
                              env=b.base_environment(sandbox), capture_output=True, text=True,
                              timeout=b.COMMAND_TIMEOUT_S, stdin=subprocess.DEVNULL)
        shown = ("gov", "launch", role, tk, *(f"--{k.replace('_', '-')}={v!r}" for k, v in options.items()),
                 *(("--", *cli_args) if cli_args else ()))
        run = b.Run(shown, done.returncode, done.stdout, done.stderr)
    return b.Launch(run, tuple(b.calls(cli)[before_calls:]), records, before, b._listing(records), started,
                    time.time(), tuple(cli_args))


# --------------------------------------------------------------------------
# Assertions
# --------------------------------------------------------------------------

def refused(result, *words):
    """A refusal: exit code 1 with LAUNCH_REFUSED, no session started, no new launch record, and every word in what
    ``gov launch`` said (case-insensitive)."""
    text = b.said(result)
    assert result.run.returncode == 1, f"the launch was not refused with exit code 1\n{result.describe()}"
    assert "LAUNCH_REFUSED" in text, f"the refusal is not LAUNCH_REFUSED\n{result.describe()}"
    b.assert_refused(result, *words)


ANY = object()  # for ``model_source``: the case does not pin it (a reading the interface leaves open)


def assert_session(result, model, effort, *, criticality, model_source, effort_source, trial=None, promotion=None,
                   effort_reason=None, owner_named=None, review_round=None):
    """One launch, stated whole: one session started; ``--model`` and ``--effort`` on its line once each; the record's
    ``model``, ``effort``, ``tier`` and the eight keys of interface section 8; the subagent model the final model."""
    b.assert_launched(result)
    got_line = {"--model": result.values("--model"), "--effort": result.values("--effort")}
    assert got_line == {"--model": [model], "--effort": [effort]}, (
        f"the launch line does not carry --model {model} and --effort {effort} once each: {got_line}\n{result.args}")
    record = result.record()
    expect = {"model": model, "effort": effort, "tier": tier_of(model), "criticality": criticality,
              "model_source": model_source, "effort_source": effort_source, "trial": trial, "promotion": promotion,
              "effort_reason": effort_reason, "owner_named": owner_named, "review_round": review_round,
              "subagent_model": model}
    if model_source is ANY:
        del expect["model_source"]
    got = {key: record.get(key, MISSING) for key in expect}
    assert got == expect, f"the launch record differs from what RUBRIC-2 states:\nexpected {expect}\ngot      {got}"
    assert result.env_block().get("CLAUDE_CODE_SUBAGENT_MODEL") == model, (
        f"the settings' CLAUDE_CODE_SUBAGENT_MODEL is not the final model {model}: {result.env_block()}")
    return record
