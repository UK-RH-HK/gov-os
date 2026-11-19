"""Support code for W2-202's acceptance tests: ``gov queue`` as the landing-and-close, part 1 (README).

It stands on W2-115b's support (``tests/acceptance/W2-115b/w2_115b_support.py``, imported as ``kit``): the planted
project, its git helpers, ``run_queue``, the answer and refusal readers and the fixtures' own checks. What is added
here is what W2-202's lines need:

- tickets judged on a record (research, audit, coordination, specification) and a feature ticket whose acceptance
  folder holds no test;
- ``gov pause``, the lifting of a freeze as ``gov pause --off`` does it, ``gov accept`` and ``gov adopt --facts``,
  each through ``python3 -m gov.cli.main``;
- the fixtures' own checks of those (the freeze flag as ``gov.util.freeze.freeze_state`` reads it; the close's own
  gates ``check_evidence`` and ``check_specification`` on a planted record), so a broken fixture fails as
  ``fixture: ...``, never as a red.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-115b"))

import w2_115b_support as kit  # noqa: E402
from w2_115b_support import A, B, module_rel  # noqa: E402,F401

REPO_ROOT = kit.REPO_ROOT
CHANGED = "# CHANGED by the ticket\nVALUE = 2\n"
BROKEN = "# BROKEN by the ticket\nVALUE = 0\n"

QUEUE_YAML_REL = kit.QUEUE_YAML_REL
CLOSE_YAML_REL = "governance/project/close.yaml"
FACTS_REL = "governance/project/facts.yaml"
FREEZE_REL = ".gov-runtime/freeze"
NEVER_MATCH = ("timeout", "unknown", "absent")

# --------------------------------------------------------------------------
# Planted tests beside W2-115b's
# --------------------------------------------------------------------------

USES_GADGET = ("tests/unit/test_uses_gadget.py", "gadget")
USES_GADGET_NODE = kit.node(USES_GADGET[0])
BOTH = "tests/unit/test_both.py"                 # imports the widget and the gadget; red when either says CHANGED
BOTH_NODE = kit.node(BOTH)
RECORDS = "tests/records/test_records.py"        # the planted record-reading set
RECORDS_NODE = kit.node(RECORDS)

NEITHER_CHANGED = ("    ok = not any('CHANGED' in (text or '') for text in _seen().values())\n"
                   "    _tell(ok)\n    assert ok, 'the widget or the gadget changed'\n")
GIZMO_NOT_BROKEN = (f"    ok = 'BROKEN' not in (_seen()[{module_rel('gizmo')!r}] or '')\n"
                    "    _tell(ok)\n    assert ok, 'the gizmo is broken'\n")
# red on the base (a bare assert) and red another way once the widget is changed
RED_ANOTHER_WAY = (f"    _tell(False)\n    if 'CHANGED' in (_seen()[{module_rel('widget')!r}] or ''):\n"
                   "        raise ValueError('another failure, with the change')\n"
                   "    assert False, 'red on the base too'\n")

# --------------------------------------------------------------------------
# Tickets beside W2-115b's
# --------------------------------------------------------------------------

N = kit.Ticket("PROJ-nnnn", "F-nn", ["mod_nn"])   # a feature ticket whose acceptance folder holds no test
USES_MOD_NN = ("tests/unit/test_uses_mod_nn.py", "mod_nn")
C = kit.C


class RecordTicket:
    """A ticket judged on a record: ``kind`` its class, ``evidence`` the paths its file names under
    ``acceptance_tests.evidence``, ``specification`` the id it names. It has no acceptance folder."""

    def __init__(self, tid, wbs, kind, evidence=(), specification=None, allowed=()):
        self.id, self.wbs, self.kind = tid, wbs, kind
        self.evidence, self.specification = list(evidence), specification
        self.allowed = list(allowed) or list(evidence)

    @property
    def ticket_rel(self):
        return f".tickets/{self.id}.md"


R = RecordTicket("PROJ-rrrr", "R-rr", "research", ["docs/research/R-rr.md"])
U = RecordTicket("PROJ-uuuu", "U-uu", "audit", ["docs/audits/U-uu.md"])
O = RecordTicket("PROJ-oooo", "O-oo", "coordination", ["docs/coordination/O-oo.md"])  # noqa: E741
S = RecordTicket("PROJ-ssss", "S-ss", "specification", specification="SPEC-ss", allowed=["openspec/changes/first/**"])
X = RecordTicket("PROJ-xxxx", "R-xx", "research", ["docs/research/R-xx.md"])   # its record is no research record
RECORD_TICKETS = (R, U, O, S)

SPEC_SCHEMA_REL = "openspec/schemas/feature-readiness/schema.yaml"
SPEC_SCHEMA = REPO_ROOT / "template" / SPEC_SCHEMA_REL
PROPOSAL_REL, READINESS_REL = "openspec/changes/first/proposal.md", "openspec/changes/first/readiness.yaml"
MANDATORY_ROWS = (1, 2, 4, 5, 6, 9, 16, 23, 24, 25)

RECORDS_TEST_MAP = dict(kit.TEST_MAP,
                        record_only=[*kit.TEST_MAP["record_only"], "docs/research/**", "docs/audits/**",
                                     "docs/coordination/**", "openspec/**"],
                        record_reading=["tests/records/"])


def record_ticket_text(ticket, status="open"):
    lines = [f"id: {ticket.id}", f"status: {status}", "deps: []", "links: []", "created: 2026-11-01T12:00:00Z",
             "type: task", "priority: 2", "assignee: engineer", f"external-ref: {ticket.wbs}",
             f"wbs_id: {ticket.wbs}", f"title: Ticket {ticket.wbs}", f"class: {ticket.kind}",
             "state_class: AUTHORITATIVE", "role: engineer", "profile: STANDARD"]
    if ticket.specification:
        lines.append(f"specification: {ticket.specification}")
    lines += ["allowed_paths:", *[f"- {p}" for p in ticket.allowed]]
    lines += ["kpis:", "  success:", "  - Its record is accepted", "  failure:", "  - Its record is refused",
              "sources: []", "acceptance_tests:"]
    if ticket.evidence:
        lines += ["  evidence:", *[f"  - {p}" for p in ticket.evidence]]
    lines.append("  author: independent-test-designer")
    return "---\n" + "\n".join(lines) + f"\n---\n# {ticket.wbs} a planted {ticket.kind} ticket\n\nBody.\n"


def record_files(ticket, base):
    """What ``ticket``'s work branch adds: a record the close's own gate for its class accepts (``base``: a commit
    of the project, which the audit report names)."""
    if ticket.kind == "research":
        return {ticket.evidence[0]: f"---\ntype: research\nid: {ticket.wbs}\n---\n# What was found\n\nA finding.\n"}
    if ticket.kind == "audit":
        return {ticket.evidence[0]: (f"---\nmilestone: M1\ncommit: '{base}'\npack_sha256: {'a' * 64}\n---\n"
                                     "# The audit\n\n| item | class | evidence |\n|---|---|---|\n"
                                     "| The project's README | OK | README.md |\n")}
    if ticket.kind == "coordination":
        return {ticket.evidence[0]: "# The coordination record\n\nWhat was agreed.\n"}
    rows = [{"n": n, "state": "PRESENT", "evidence": ["README.md"]} if n in MANDATORY_ROWS
            else {"n": n, "state": "N/A_WITH_REASON", "reason": "not in a LITE specification"} for n in range(1, 27)]
    return {PROPOSAL_REL: (f"---\ntype: specification\nid: {ticket.specification}\nprofile: LITE\nspine: false\n"
                           "capability_types: []\n---\n# The specification\n\nWhat is to be built.\n"),
            READINESS_REL: yaml.safe_dump({"rows": rows}, sort_keys=False)}


def records_project(folder, more_extra=None):
    """A planted project (A and B, as W2-115b's) that also holds: the four tickets judged on a record and X (a
    research ticket), none with an acceptance folder; N, a feature ticket whose acceptance folder holds a README
    and no test; the readiness schema; a record-reading set and a test map that places the record folders."""
    told = folder / "told"
    extra = {t.ticket_rel: record_ticket_text(t) for t in (*RECORD_TICKETS, X)}
    extra.update({N.ticket_rel: kit.ticket_text(N), N.acceptance + "README.md": kit.readme_text(N),
                  SPEC_SCHEMA_REL: SPEC_SCHEMA.read_text(encoding="utf-8"),
                  kit.TEST_MAP_REL: yaml.safe_dump(RECORDS_TEST_MAP, sort_keys=False),
                  RECORDS: kit.telling(RECORDS, told, ["gizmo"])})
    extra.update(more_extra or {})
    project = kit.Planted(folder / "project", told, unit=(*kit.UNIT_TESTS, USES_MOD_NN), extra=extra)
    for ticket in (*RECORD_TICKETS, X, N):
        project.tickets[ticket.id] = ticket
    return project


# --------------------------------------------------------------------------
# gov, beside the queue
# --------------------------------------------------------------------------

def env_folder(project):
    return project.root.parent / f"{project.root.name}-env"


def run_gov(root, *args, env=None, timeout=600):
    """``python3 -m gov.cli.main <args> --root <root> --json``: ``{"args", "code", "stdout", "stderr"}``."""
    cmd = [sys.executable, "-m", "gov.cli.main", *args, "--root", str(root), "--json"]
    done = subprocess.run(cmd, cwd=str(root), env=env, capture_output=True, text=True, timeout=timeout,
                          stdin=subprocess.DEVNULL)
    return {"args": list(args), "code": done.returncode, "stdout": done.stdout, "stderr": done.stderr}


def said(run):
    return f"gov {' '.join(run['args'])}: exit {run['code']}\n--- stdout\n{run['stdout'][-3000:]}\n--- stderr\n" \
           f"{run['stderr'][-3000:]}"


def freeze_state(project):
    """The freeze flag as ``gov.util.freeze.freeze_state`` reads it for the planted project."""
    done = subprocess.run([sys.executable, "-c", "import sys\nfrom gov.util.freeze import freeze_state\n"
                           "print(freeze_state(sys.argv[1]))", str(project.root)],
                          env=kit.base_env(env_folder(project)), capture_output=True, text=True, timeout=120)
    return done.stdout.strip() or f"unread: {done.stderr.strip()[-300:]}"


def pause(project):
    """``gov pause`` in the planted project (no ``GOV_ROLE``: the owner); the flag must then read as a freeze."""
    done = run_gov(project.root, "pause", env=kit.base_env(env_folder(project)))
    assert done["code"] == 0, f"fixture: gov pause did not freeze the planted project\n{said(done)}"
    state = freeze_state(project)
    assert state == "frozen", f"fixture: after gov pause the freeze flag reads {state!r}, not frozen"
    return done


def lift(project):
    """The freeze lifted as ``gov pause --off`` lifts it: the flag ``.gov-runtime/freeze`` and its mirror under the
    home's ``.local/state/gov-os/`` removed. ``--off`` itself asks for the owner in person at a terminal (DEC-409),
    which no test run has (README, readings)."""
    (project.root / FREEZE_REL).unlink(missing_ok=True)
    shutil.rmtree(env_folder(project) / "home" / ".local" / "state" / "gov-os", ignore_errors=True)
    state = freeze_state(project)
    assert state == "absent", f"fixture: after the lift the freeze flag reads {state!r}, not absent"


def scratch_at(project, revision, name):
    """A scratch clone of the project at ``revision`` (detached), beside the project."""
    scratch = project.root.parent / f"{project.root.name}-{name}"
    if scratch.exists():
        shutil.rmtree(scratch)
    kit.git(project.root.parent, "clone", "-q", "--no-checkout", str(project.root), str(scratch))
    kit.git(scratch, "checkout", "-q", "--detach", revision)
    return scratch


def accept_at(project, revision, tid):
    """``gov accept <tid> --root <a scratch clone at revision> --json``: its run (the telling tests keep quiet
    there, so the project's run logs stay the queue's alone)."""
    scratch = scratch_at(project, revision, "accept")
    env = {**kit.base_env(scratch.parent / f"{scratch.name}-env"), kit.SELF_CHECK: "1"}
    done = run_gov(scratch, "accept", tid, env=env)
    shutil.rmtree(scratch, ignore_errors=True)
    return done


GATE = '''import sys
from pathlib import Path
from gov.close import gates
from gov.tasks.tickets import frontmatter
root, ticket = Path(sys.argv[1]), sys.argv[2]
front = frontmatter(root / ".tickets" / (ticket + ".md"))
try:
    if gates.ticket_class(front) == gates.SPECIFICATION_CLASS:
        gates.check_specification(root, ticket)
    else:
        gates.check_evidence(root, ticket, front)
    print("ACCEPTED")
except Exception as refused:
    print("REFUSED", getattr(refused, "code", type(refused).__name__), refused)
'''


def gate_says(project, revision, tid):
    """What the close's own gate for the ticket's class (``check_evidence``, ``check_specification``) says of the
    ticket's record in a scratch clone at ``revision``: a line starting ``ACCEPTED`` or ``REFUSED``."""
    scratch = scratch_at(project, revision, "gate")
    done = subprocess.run([sys.executable, "-c", GATE, str(scratch), tid], cwd=str(scratch),
                          env=kit.base_env(scratch.parent / f"{scratch.name}-env"), capture_output=True, text=True,
                          timeout=300)
    shutil.rmtree(scratch, ignore_errors=True)
    return done.stdout.strip() or f"unread: {done.stderr.strip()[-600:]}"


def check_gates(project, accepted=(), refused=()):
    for ticket in accepted:
        says = gate_says(project, project.tips[ticket.id], ticket.id)
        assert says.startswith("ACCEPTED"), f"fixture: the close's gate does not accept {ticket.id}'s record: {says}"
    for ticket in refused:
        says = gate_says(project, project.tips[ticket.id], ticket.id)
        assert says.startswith("REFUSED"), f"fixture: the close's gate does not refuse {ticket.id}'s record: {says}"


# --------------------------------------------------------------------------
# Reading what a landing left
# --------------------------------------------------------------------------

def ids(listed):
    """The test ids of a ``base_reds`` list (ids, or entries holding ``test``)."""
    return [item if isinstance(item, str) else (item or {}).get("test") for item in listed or []]


def entries(front, node):
    """The close record's ``reds`` entries for ``node``."""
    return [r for r in front.get("reds") or [] if isinstance(r, dict) and r.get("test") == node]


def assert_base_red_recorded(landing, result, tid, node, base, failure_type="AssertionError"):
    """A1 S1: the landed ticket's close record lists ``node`` once in ``reds`` (``verdict: base``, its failure type
    and the base commit) and in ``base_reds``."""
    front = kit.close_record(landing, result["head"], tid)
    found = entries(front, node)
    assert len(found) == 1, f"{tid}'s close record holds {len(found)} reds entries for {node}: {front.get('reds')!r}"
    entry = found[0]
    assert entry.get("verdict") == "base", f"the red's verdict is {entry.get('verdict')!r}, not base: {entry}"
    assert entry.get("failure_type") == failure_type, f"failure_type {entry.get('failure_type')!r}: {entry}"
    assert entry.get("base") == base, f"the entry's base {entry.get('base')!r} is not the base commit {base}"
    assert front.get("base_reds") == [node], f"{tid}'s base_reds: {front.get('base_reds')!r}"
    return front


def queue_record(landing, result):
    """The result ``.gov-runtime/queue/<stamp>/queue.json`` holds."""
    path = landing.root / (result.get("record") or "no-record")
    assert path.is_file(), f"no queue record at {result.get('record')!r}"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("result") if isinstance(data.get("result"), dict) else data


def changed_between(root, old, new):
    """``[(status letter, path)]`` of the tree diff ``old..new``."""
    out = kit.git(root, "diff", "--no-renames", "--name-status", old, new)
    return [tuple(line.split("\t", 1)) for line in out.splitlines() if line.strip()]


def stray_record_paths(paths):
    """Of ``paths``: those under ``docs/`` outside ``docs/close/`` and ``docs/checkpoints/``."""
    return [p for p in paths if p.startswith("docs/") and not p.startswith(("docs/close/", "docs/checkpoints/"))]


def status_paths(porcelain):
    return [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]


def not_moved(landing, before=None, after=None):
    """Every branch as it was (``before``: the state before the run; ``after``: the state to compare, else now)."""
    was, now = kit.heads(before or landing.before), kit.heads(after or landing.state())
    assert now == was, f"a branch moved: {was} -> {now}"


def unchanged(before, after):
    """A refusal that writes nothing: every ref, what HEAD is, the status and every tracked file as before."""
    for key in ("refs", "head", "status", "files"):
        assert after[key] == before[key], f"the project's {key} changed"
