"""Support code for the W2-210 acceptance tests: the lite adoption verdict stage, ``gov adopt --lite --stage VERDICT``
(CAP-44.h; DEC-1227 D1 (a); DEC-1231).

The cases run on W1-41's "harbour" project, adopted through A0 to A8 and both lite gates by W2-52's support (the A5,
A7 and A10 records are the Independent Auditor's: committed with ``Role: independent-auditor``), plus one closed
ticket and its close record. The adoption is built ONCE per pytest run (a lock file shares it between the xdist
workers) and each case copies it into its own temporary folder, as W2-52's cases do.

- **The code under test** is this worktree's ``gov``: the command line through W1-07's launcher with ``src/`` of this
  worktree on the child's ``PYTHONPATH`` (W1-41's ``environment``), and, in process, ``gov.adopt.verdict`` (``src/``
  of this worktree is first on ``sys.path`` in ``conftest.py``).
- **No model, no network.** The semantic index of the build goes through W2-52's loopback stand-in endpoint.
- **The live tools** (``gov doctor``, ``gov check``) are run by the command line as child ``gov`` processes. On the
  harbour they are not green (doctor: path_compliance and framework_lock fail; check: RED families), and cannot be
  made so cheaply, so the cases that need them green call ``gov.adopt.verdict.compute(root, session, tools=...)``
  with the stand-ins below. The command line never takes a stand-in.

The interface the cases hold (names the ticket leaves open) is in ``README.md``, "Interface".
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

_HERE = Path(__file__).resolve().parent
for _folder in (_HERE.parent / "W1-07", _HERE.parent / "W1-41", _HERE.parent / "W2-52", _HERE.parent / "W2-81"):
    if str(_folder) not in sys.path:
        sys.path.insert(0, str(_folder))

import w2_52_support as gates  # noqa: E402

support = gates.support
base = gates.base
REPO_ROOT = gates.REPO_ROOT
if str(REPO_ROOT / "src") not in sys.path:  # the in-process gov is this worktree's
    sys.path.insert(0, str(REPO_ROOT / "src"))

# --- what the ticket and the README fix ------------------------------------------------------------------------
FOLDER = "governance/adoption"
VERDICT_REL = f"{FOLDER}/VERDICT-lite.md"
EXCEPTIONS_REL = "governance/project/adoption-exceptions.yaml"
STAGE_SUBJECT = "gov adopt --lite VERDICT: lite adoption verdict"
VERDICTS = gates.VERDICTS
SESSION = "verdict-001"                      # the verdict stage's own session: not the adopter's, not an auditor's
OWNER_DECISION = "DEC-9001"

# The conditions, in the order of the record (README, "Interface": verdict.CONDITIONS).
STAGE_CONDITIONS = ("A0", "A1", "A2", "A3", "A4", "A5", "A6", "A8")
A5_REVIEW, NATIVE, LITE_A7, LITE_A10 = "A5 review holds", "native layout kept", "lite A7 gate", "lite A10 gate"
RELEASE, DOCTOR, CHECK, TICKET_COND = ("release pinned and hash-verified", "gov doctor green",
                                       "gov check no RED family", "one ticket closed")
CONDITIONS = (*STAGE_CONDITIONS, A5_REVIEW, NATIVE, LITE_A7, LITE_A10, RELEASE, DOCTOR, CHECK, TICKET_COND)
TOOL_CONDITIONS = (RELEASE, DOCTOR, CHECK)

RECORD = {                                   # gov.adopt.project.record_path, and lite_gates.record_path
    "A0": f"{FOLDER}/A0-safety-baseline.md", "A1": f"{FOLDER}/A1-inventory.md",
    "A2": f"{FOLDER}/A2-classification.md", "A3": f"{FOLDER}/A3-target-path-map.md",
    "A4": f"{FOLDER}/A4-batched-plan.md", "A5": f"{FOLDER}/A5-independent-review-of-the-path-map.md",
    "A6": f"{FOLDER}/A6-controlled-migration.md", "A8": f"{FOLDER}/A8-legacy-import-and-retirement.md",
    "A7": f"{FOLDER}/A7-independent-migration-verification.md",
    "A10": f"{FOLDER}/A10-independent-memory-verification.md",
}
AUDITOR = {"A5": support.VERDICT_REL, "A7": gates.GATE_VERDICT_REL["A7"], "A10": gates.GATE_VERDICT_REL["A10"]}
AUDITOR_OF = {A5_REVIEW: "A5", LITE_A7: "A7", LITE_A10: "A10"}
AUDITOR_ROLE = support.AUDITOR_ROLE
TICKET = "HARB-d1aa"
TICKET_REL = f".tickets/{TICKET}.md"
CLOSE_REL = f"docs/close/{TICKET}/CL-{TICKET}.md"
NATIVE_FILE = support.NATIVE_FILE
GROUNDS = {"materially_better": "the module belongs with the other shared modules",
           "migration_risk": "one importer, covered by the project's tests"}

# CAP-44.h: the ten ADOPTED_HEALTHY conditions of Adoption Protocol v3.0 section 20, their markings, their lite parts.
HEALTHY_TEN = {1: "W3", 2: "W3", 3: "W2", 4: "W3", 5: "W3", 6: "W3", 7: "W3", 8: "W3", 9: "W3", 10: "W3"}
LITE_PART_HAS = {1: {RELEASE}, 3: {"A3", A5_REVIEW, NATIVE}, 4: {LITE_A7}, 5: {"A8"}, 6: {LITE_A10}, 9: {LITE_A10}}
NO_LITE_PART = (2, 7, 8, 10)


# --------------------------------------------------------------------------
# The code under test, in process
# --------------------------------------------------------------------------

def verdict_module():
    """``gov.adopt.verdict``; an assertion error (the red reason before W2-210) where it does not exist."""
    import importlib

    try:
        return importlib.import_module("gov.adopt.verdict")
    except ModuleNotFoundError as exc:
        if exc.name in ("gov.adopt.verdict", "gov.adopt"):
            raise AssertionError("gov.adopt.verdict does not exist: the lite verdict stage is not built") from None
        raise


def compute(project, session=SESSION, tools=None):
    """``gov.adopt.verdict.compute(root, session, tools=tools)``: the record's frontmatter as the stage would write
    it (without ``produced_by``); nothing is written or committed."""
    before = (support.git(project, "rev-parse", "HEAD"), support.git(project, "status", "--porcelain"))
    result = verdict_module().compute(Path(project), session, tools=tools)
    assert (support.git(project, "rev-parse", "HEAD"), support.git(project, "status", "--porcelain")) == before, \
        "compute wrote or committed something: it only reads"
    assert isinstance(result, dict), f"compute returns the record's frontmatter as a mapping, not {type(result)}"
    return result


def check_record(project):
    return verdict_module().check_record(Path(project))


def states(result):
    """Condition name -> state, in the record's order."""
    return {item["name"]: item["state"] for item in result["conditions"]}


def not_met(result):
    return [name for name, state in states(result).items() if state == "not met"]


def condition(result, name):
    found = [item for item in result["conditions"] if item["name"] == name]
    assert len(found) == 1, f"the record gives {len(found)} conditions named {name!r}: {list(states(result))}"
    return found[0]


# --------------------------------------------------------------------------
# The live tools, stood in (gov.adopt.verdict.compute's ``tools=`` seam): each is ``tool(root) -> (exit, stdout)``,
# the exit code and the standard output of ``gov <tool> --json`` run at the repository root.
# --------------------------------------------------------------------------

def _envelope(command, code, parts, error_code):
    if code == 0:
        return {"ok": True, "command": command, "result": parts, "session": "", "error": None}
    return {"ok": False, "command": command, "result": {}, "session": "",
            "error": {"code": error_code, "message": f"gov {command} is not green", "details": parts}}


def doctor(lock="MATCH", exit_code=0, failing_part=None):
    """A ``gov doctor --json``: its ``framework_lock`` part says ``lock`` (MATCH, or DRIFT...); the exit code is
    ``exit_code`` (3 with ``failing_part`` failing, as an unhealthy doctor ends). The envelope is the real one's: the
    parts in ``result`` at exit 0, in ``error.details`` otherwise."""
    parts = {"healthy": exit_code == 0, "tools": {"status": "pass"}, "canaries": {"status": "pass"},
             "framework_lock": {"status": "pass" if lock == "MATCH" else "fail", "match": lock}}
    if failing_part:
        parts[failing_part] = {"status": "fail", "reason": "planted by the case"}
    text = json.dumps(_envelope("doctor", exit_code, parts, "DOCTOR_UNHEALTHY"))
    return lambda root: (exit_code, text)


def check(red=(), exit_code=None):
    """A ``gov check --json``: every family GREEN or YELLOW, those in ``red`` RED (exit 3, as the real check ends)."""
    code = (3 if red else 0) if exit_code is None else exit_code
    families = {name: {"status": "GREEN", "family": name, "check_count": 1}
                for name in ("schema/invariants", "security", "test", "authority")}
    families["memory"] = {"status": "YELLOW", "family": "memory", "check_count": 1}
    for name in red:
        families[name] = {"status": "RED", "family": name, "check_count": 1}
    text = json.dumps(_envelope("check", code, {"families": families}, "CHECK_FAILED"))
    return lambda root: (code, text)


def healthy_tools(**replace):
    """Both tools green; ``replace`` swaps one (``doctor=...``, ``check=...``)."""
    return {"doctor": doctor(), "check": check(), **replace}


# --------------------------------------------------------------------------
# Building the adopted project, once per run
# --------------------------------------------------------------------------

def native_proposal():
    """Three move batches, every legacy file retired (W2-52's proposal), and a fourth batch that moves a file out of
    the native package layout (CAP-44.j) with both grounds."""
    return gates.proposal() + [support.entry(NATIVE_FILE, "MOVE", support.NATIVE_TARGET, batch=4,
                                             justification=dict(GROUNDS))]


def write_front(project, rel, mutate, message, *trailers):
    """Change the frontmatter of the committed record ``rel`` with ``mutate(front)`` and commit it (the body stays)."""
    path = Path(project) / rel
    text = path.read_text(encoding="utf-8")
    front = support.frontmatter(text, rel)
    mutate(front)
    path.write_text(support.with_frontmatter(text, front), encoding="utf-8")
    return support.commit(project, message, *trailers)


def write_ticket(project, status="closed"):
    front = {"id": TICKET, "type": "task", "status": status, "state_class": "AUTHORITATIVE", "deps": [],
             "role": "engineer", "allowed_paths": ["src/**"], "kpis": {"success": ["The harbour builds."]},
             "title": "A ticket of the harbour project"}
    support.write(project, TICKET_REL, "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n# A ticket\n")


def write_close(project, passed=3, failed=0, errors=0, skipped=0, extra=None):
    """The close record as ``gov close`` writes it: ``tests_run`` (and ``test_runs``) hold the counts."""
    front = {"id": f"CL-{TICKET}", "type": "close", "status": "ACTIVE", "state_class": "AUTHORITATIVE",
             "task": TICKET, "created": "2026-11-22T10:00:00Z", "outputs": [TICKET_REL, CLOSE_REL],
             "tests_run": {"passed": passed, "failed": failed, "errors": errors, "skipped": skipped},
             "test_runs": [{"run": "regression", "form": "serial", "seconds": 1.5, "passed": passed,
                            "failed": failed, "errors": errors, "skipped": skipped, "workers": 1}], **(extra or {})}
    support.write(project, CLOSE_REL, "---\n" + yaml.safe_dump(front, sort_keys=False)
                  + f"---\n\n# CL-{TICKET}: Close record for {TICKET}\n")


def build_adopted(folder, interface, endpoint, site, native_without_grounds=False):
    """The harbour adopted through A0 to A8 with the Independent Auditor's A5, A7 and A10 records and both gates
    passed, then one closed ticket with its close record. With ``native_without_grounds`` the A3 record's entry for
    the native file loses its justification before A4 stands on it (what A3 itself refuses to write): the repository
    holds a move out of a native layout without both grounds."""
    project = gates.build_harbour(Path(folder) / "harbour")
    ad = gates.GateAdoption(project, support.make_sandbox(Path(folder) / "sandbox"), interface, endpoint=endpoint,
                            site=site)
    for stage in ("A0", "A1", "A2"):
        ad.ok(stage)
    ad.ok("A3", *ad.map_argument(native_proposal()))
    if native_without_grounds:
        def strip(front):
            for item in front["artefacts"]:
                if item["path"] == NATIVE_FILE:
                    item.pop("justification")
        write_front(project, ad.stages["A3"].record, strip, "the native move loses its grounds")
    ad.ok("A4")
    support.write_verdict(project, ad.stages["A3"].record)
    ad.ok("A5", "--verdict", support.VERDICT_REL)
    ad.ok("A6")
    gates.write_gate_verdict(ad, "A7")
    gates.assert_passed(gates.run_gate(ad, "A7"))
    ad.ok("A8")
    gates.write_gate_verdict(ad, "A10")
    gates.assert_passed(gates.run_gate(ad, "A10"))
    write_ticket(project)
    write_close(project)
    support.commit(project, "a ticket closed through the landing", f"Task: {TICKET}")
    return gates.snapshot(ad)


def with_code_graph(path):
    """``path`` with the folders that held the code-graph tool (``codebase-memory-mcp``) when the outermost run
    started put back at its end. ``tests/conftest.py`` takes the tool off ``PATH`` for every suite but those of
    ``_CBM_SUITES``; A3 and A6 of the build need it (W1-41, W2-52 are on that list). Appended, never put first: a folder
    that also holds another program (an installed ``gov``) does not shadow the case's own."""
    off = [part for part in os.environ.get("CODEINTEL_OFF_PATH", "").split(os.pathsep) if part]
    return os.pathsep.join([part for part in (path, *off) if part])


def shared_build(tmp_path_factory, name, builder):
    """Build once for the whole run, whichever xdist worker comes first (a lock file); the build stands under that
    worker's own temp base (the code-graph daemon folder of the run is found from there), and a marker in the folder
    the workers share names it. Returns the snapshot every case copies."""
    own = Path(tmp_path_factory.getbasetemp())
    shared = own.parent if os.environ.get("PYTEST_XDIST_WORKER") else own
    marker = shared / f"w2-210-{name}.json"
    with open(shared / f"w2-210-{name}.lock", "w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        if not marker.exists():
            folder = own / f"w2-210-{name}"
            shutil.rmtree(folder, ignore_errors=True)
            kept = builder(folder)
            marker.write_text(json.dumps({"root": str(kept.root), "records": {
                stage: item.record for stage, item in kept.stages.items()}}), encoding="utf-8")
        made = json.loads(marker.read_text(encoding="utf-8"))
    return gates.Snapshot(Path(made["root"]), {stage: support.Stage(stage, None, {}, rel, {})
                                               for stage, rel in made["records"].items()})


# --------------------------------------------------------------------------
# Planting: each is one commit in the case's own copy (ordinary, or with the Role the case gives)
# --------------------------------------------------------------------------

def commit(project, message, *roles):
    return support.commit(project, message, f"Task: {TICKET}", *[f"Role: {role}" for role in roles])


def remove_record(project, rel):
    support.git(project, "rm", "-q", rel)
    return commit(project, f"{rel} is gone")


def append_to(project, rel, text="\nA line added later by hand.\n", *roles):
    path = Path(project) / rel
    path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")
    return commit(project, f"a hand edit of {rel}", *roles)


def restore_by(project, rel, roles, also=None):
    """Change ``rel`` and put it back, byte for byte, in two commits by ``roles``: the content is as it was, and the
    last commit that touched it carries these roles (and also wrote ``also``, a path, where it is given)."""
    path = Path(project) / rel
    original = path.read_bytes()
    path.write_bytes(original + b"\nchanged\n")
    commit(project, f"a hand edit of {rel}", *roles)
    path.write_bytes(original)
    if also:
        support.write(project, also, "written beside it\n")
    return commit(project, f"{rel} as it was", *roles)


def set_result(project, stage, result):
    return write_front(project, RECORD[stage], lambda front: front.__setitem__("result", result),
                       f"the {stage} gate's record says {result}", f"Task: {TICKET}")


def write_exceptions(project, entries, *roles, subject="the owner's exceptions", commit_it=True):
    """The owner's file: a list of ``{condition, decision}``; committed with one ``Role`` trailer per role."""
    support.write(project, EXCEPTIONS_REL, yaml.safe_dump([dict(item) for item in entries], sort_keys=False))
    return commit(project, subject, *roles) if commit_it else None


def accept(*names, decision=OWNER_DECISION):
    return [{"condition": name, "decision": decision} for name in names]


def last_commit(project, rel):
    return support.git(project, "log", "-1", "--format=%H", "--", rel).strip()


def head_subject(project):
    return support.git(project, "log", "-1", "--format=%s").strip()


def head_files(project):
    return [line for line in support.git(project, "show", "--name-only", "--format=", "HEAD").split("\n") if line]


# --------------------------------------------------------------------------
# Running the command line
# --------------------------------------------------------------------------

def assert_taken(run):
    """The red reason before W2-210: ``--stage`` does not offer VERDICT (argparse, exit 2), or says it is not built."""
    assert not ("invalid choice" in run.stderr or (run.returncode == 2 and not run.stdout.strip())), \
        f"gov adopt --lite does not take --stage VERDICT\n{run.describe()}"
    assert not support.not_built(run), f"gov adopt --lite answers that stage VERDICT is not built\n{run.describe()}"


def run_stage(ad, session=SESSION, *extra):
    """``gov adopt --lite --stage VERDICT`` in the case's project; what it answered and what it left. Asserts nothing
    (a fixture may run it): a case calls ``taken(outcome)`` first."""
    before = SimpleNamespace(tree=support.tree(ad.project), state=support.git_state(ad.project),
                             porcelain=support.porcelain(ad.project))
    run = ad.run("VERDICT", *extra, session=session)
    after = SimpleNamespace(tree=support.tree(ad.project), state=support.git_state(ad.project),
                            porcelain=support.porcelain(ad.project))
    return SimpleNamespace(run=run, before=before, after=after, project=ad.project, ad=ad)


def taken(outcome):
    """The stage is offered and built: the outcome, or the red reason before W2-210."""
    assert_taken(outcome.run)
    return outcome


def envelope(outcome):
    done = base.assert_envelope(outcome.run, support.base.load_interface(REPO_ROOT), command="adopt")
    return done


def assert_nothing_written(outcome):
    """A refusal: HEAD, every ref, the tree of HEAD and the working tree as they were."""
    assert outcome.before.state == outcome.after.state, f"a refusal moved HEAD or a ref\n{outcome.run.describe()}"
    assert outcome.before.tree == outcome.after.tree, f"a refusal changed the tree at HEAD\n{outcome.run.describe()}"
    assert outcome.before.porcelain == outcome.after.porcelain, \
        f"a refusal changed the working tree\n{outcome.run.describe()}"
    assert VERDICT_REL not in outcome.after.tree or VERDICT_REL in outcome.before.tree, \
        f"a refusal wrote {VERDICT_REL}"


def assert_refused(outcome, code):
    done = envelope(outcome)
    assert done["ok"] is False, f"expected a refusal\n{outcome.run.describe()}"
    assert outcome.run.returncode in support.REFUSAL_EXIT_CODES, \
        f"a refusal ends with one of {support.REFUSAL_EXIT_CODES}\n{outcome.run.describe()}"
    assert done["error"]["code"] == code, f"expected {code}, got {done['error']['code']}\n{outcome.run.describe()}"
    return done["error"]


def record_at_head(project):
    """The committed lite verdict record: (frontmatter, text)."""
    data = support.at_head(project, VERDICT_REL)
    assert data is not None, f"{VERDICT_REL} is not committed at HEAD"
    text = data.decode("utf-8")
    return support.frontmatter(text, VERDICT_REL), text


def record_states(front):
    return {item["name"]: item["state"] for item in front["conditions"]}


# --------------------------------------------------------------------------
# produced_by (README, "Interface": the digest) and the records a case writes by hand
# --------------------------------------------------------------------------

def digest_of(text):
    """The README's ``produced_by``: sha256 (hex) of the record's text with its one ``produced_by:`` line removed."""
    kept = [line for line in text.split("\n") if not line.startswith("produced_by:")]
    return hashlib.sha256("\n".join(kept).encode("utf-8")).hexdigest()


def with_digest(text):
    """``text`` with a ``produced_by`` line, as the stage writes it (placed last in the frontmatter)."""
    lines = [line for line in text.split("\n") if not line.startswith("produced_by:")]
    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    end = lines.index("---", 1)
    return "\n".join([*lines[:end], f"produced_by: {digest}", *lines[end:]])


def without_digest(text):
    return "\n".join(line for line in text.split("\n") if not line.startswith("produced_by:"))


def changed_record(text, mutate):
    """The record ``text`` with its frontmatter changed by ``mutate(front)`` and no digest line."""
    front = support.frontmatter(without_digest(text), VERDICT_REL)
    mutate(front)
    return support.with_frontmatter(without_digest(text), front)


def commit_record(project, text, subject=STAGE_SUBJECT, roles=()):
    """Write ``text`` as the record and commit it with ``subject`` (the stage's, by default) touching it alone."""
    support.write(project, VERDICT_REL, text)
    return commit(project, subject, *roles)


def schema_errors(front):
    """The errors of ``front`` under the kernel's ``adoption-verdict`` schema (W2-02), as text; [] where valid."""
    import jsonschema

    folder = REPO_ROOT / "template/governance/kernel/schemas"
    schema = json.loads((folder / "adoption-verdict.schema.json").read_text(encoding="utf-8"))
    resolver = jsonschema.RefResolver(base_uri=(folder / "adoption-verdict.schema.json").as_uri(), referrer=schema)
    data = json.loads(json.dumps(front, default=str))
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message}"
            for e in jsonschema.Draft202012Validator(schema, resolver=resolver).iter_errors(data)]


def sha256_at_head(project, rel):
    return hashlib.sha256(support.at_head(project, rel)).hexdigest()


def git_parent(project):
    """The commit before HEAD."""
    return support.git(project, "rev-parse", "HEAD~1").strip()


def git_reset_back(project, count=1):
    """Put the case's own copy back ``count`` commits (the stage's commit undone, to compute at the commit it ran at)."""
    support.git(project, "reset", "-q", "--hard", f"HEAD~{count}")


def states_of(front):
    return {item["name"]: item["state"] for item in front["conditions"]}
