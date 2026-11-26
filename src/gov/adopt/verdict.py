"""The lite adoption verdict stage of ``gov adopt --lite`` (W2-210; CAP-44.h; DEC-1227 D1 (a), DEC-741 F, DEC-722).

``gov adopt --lite --stage VERDICT`` computes every lite condition of CAP-44.h by code, from the repository alone, and
commits ``governance/adoption/VERDICT-lite.md``, a record of type ``adoption-verdict`` (W2-02): ``verdict``, each
condition ``met``, ``not met`` or ``accepted`` with its evidence (the command run and its exit code, or the record
read and its path), ``lite: true``, the ten ADOPTED_HEALTHY conditions with their markings and lite parts, and the
conditions the verdict does not check. No model and no session's word enters it. The independence CAP-44.h asks for
is carried by the three Independent Auditor records A5, A7 and A10 stand on, which the stage re-reads by code (the A5
rule of ``stages._verdict``, the gates' rule of ``lite_gates._auditor``) and lists under ``auditors``.

- ADOPTED_HEALTHY: every condition is met. ADOPTED_WITH_ACCEPTED_EXCEPTIONS: every condition not met is accepted by
  name in the owner's file (``governance/project/adoption-exceptions.yaml``), read only when the last commit that
  touched it carries ``Role: owner`` and no other Role and the file is as committed. Otherwise NOT_ADOPTED_HEALTHY,
  which is committed as a record and then refused (``ADOPT_NOT_ADOPTED``), as the lite gates are. Nobody but the owner
  accepts an exception: a file that is not the owner's refuses the stage before anything is computed.
- The record carries ``produced_by``, the digest of its text without that line. ``check_record`` refuses a record the
  stage did not produce, one that stands on another A10 record than the committed one, one that no commit of the
  stage's brought, and one whose verdict its conditions do not give.
- The live tools (``gov doctor``, ``gov check``) run as child ``gov`` processes of this interpreter at the repository
  root. ``compute``'s ``tools=`` is the self-tests' seam; the command line never takes a stand-in.

What lies beyond the lite form stays for Wave 3 (CAP-44.k), and the record says so.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from gov.adopt import lite_gates, project
from gov.adopt.project import FOLDER, git, refuse
from gov.cli.errors import GovError

RECORD = f"{FOLDER}/VERDICT-lite.md"
EXCEPTIONS = "governance/project/adoption-exceptions.yaml"
SUBJECT = "gov adopt --lite VERDICT: lite adoption verdict"
SOURCE = "CAP-44.h"
OWNER = "owner"
VERDICTS = ("ADOPTED_HEALTHY", "ADOPTED_WITH_ACCEPTED_EXCEPTIONS", "NOT_ADOPTED_HEALTHY")
STATES = ("met", "not met", "accepted")
STAGE_CONDITIONS = ("A0", "A1", "A2", "A3", "A4", "A5", "A6", "A8")  # each stage's record, in the chain's order
A5_REVIEW, NATIVE, LITE_A7, LITE_A10 = "A5 review holds", "native layout kept", "lite A7 gate", "lite A10 gate"
RELEASE, DOCTOR, CHECK, TICKET = ("release pinned and hash-verified", "gov doctor green", "gov check no RED family",
                                  "one ticket closed")
CONDITIONS = (*STAGE_CONDITIONS, A5_REVIEW, NATIVE, LITE_A7, LITE_A10, RELEASE, DOCTOR, CHECK, TICKET)
DECISION = re.compile(r"^(ADR|DEC)-[0-9]{3,}$")  # common.schema.json's decision_id: what ``owner_entry`` takes
TOOL_TIMEOUT = 900  # seconds; a tool that does not answer in time leaves its conditions not met

# The ten ADOPTED_HEALTHY conditions of Adoption Protocol v3.0 section 20 as CAP-44.h numbers them: the number, the
# name, the wave marking and the lite conditions that check it (none: no lite part).
HEALTHY_TEN = (
    (1, "certified kernel pinned", "W3", (RELEASE,)),
    (2, "project overlay separate", "W3", ()),
    (3, "path mapping, with the A5 independent review passed", "W2", ("A3", A5_REVIEW, NATIVE)),
    (4, "migration independently verified", "W3", (LITE_A7,)),
    (5, "legacy authority retired", "W3", ("A8",)),
    (6, "memory independently verified", "W3", (LITE_A10,)),
    (7, "comprehensive v4 audit completed", "W3", ()),
    (8, "critical/high unaccepted findings resolved", "W3", ()),
    (9, "runtime rebuildable", "W3", (LITE_A10,)),
    (10, "clean-machine reconstruction demonstrated", "W3", ()),
)
NOT_CHECKED = (
    "(2) project overlay separate: W3, no lite part",
    "(7) comprehensive v4 audit completed (A11, CAP-44.k): W3, no lite part",
    "(8) critical/high unaccepted findings resolved (CAP-44.g, and the A11 audit): W3, no lite part",
    "(10) clean-machine reconstruction demonstrated: W3, no lite part",
    "the W3 part of (1), (4), (5), (6) and (9): the certification of the kernel by qualification (CAP-43.c), a "
    "separate verifier role (CAP-47.a), the A9 knowledge fabric and CAP-49's memory checks",
    "A9, the memory fabric as a condition (CAP-44.k)",
    "A11, the comprehensive v4 audit (CAP-44.k)",
)


# --------------------------------------------------------------------------
# The verdict rule, the digest
# --------------------------------------------------------------------------

def derive(states) -> str:
    """The verdict the states give (V2): every one ``met``; every one ``met`` or ``accepted``; otherwise not."""
    states = list(states)
    if states and all(state == "met" for state in states):
        return "ADOPTED_HEALTHY"
    if states and all(state in ("met", "accepted") for state in states):
        return "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"
    return "NOT_ADOPTED_HEALTHY"


def digest(text: str) -> str:
    """The sha256 of ``text`` with its ``produced_by:`` line (and that line's newline) removed (F1)."""
    return hashlib.sha256("\n".join(line for line in text.split("\n") if not line.startswith("produced_by:"))
                          .encode("utf-8")).hexdigest()


def with_digest(text: str) -> str:
    """``text`` with the one ``produced_by`` line, the last of its frontmatter."""
    lines = [line for line in text.split("\n") if not line.startswith("produced_by:")]
    end = lines.index("---", 1)
    return "\n".join([*lines[:end], f"produced_by: {digest(text)}", *lines[end:]])


# --------------------------------------------------------------------------
# The owner's exceptions file (V2, F2)
# --------------------------------------------------------------------------

def read_exceptions(root: Path) -> list[dict]:
    """The owner's entries, ``[{condition, decision}]``; ``[]`` where there is no file. A file whose last commit does not
    carry ``Role: owner`` alone, or that is not as committed, is no exceptions file: ``ADOPT_EXCEPTIONS_NOT_OWNERS``."""
    path = root / EXCEPTIONS
    tracked = git(root, "--literal-pathspecs", "ls-files", "-z", "--", EXCEPTIONS).strip("\0")
    if not tracked and not os.path.lexists(path):
        return []
    commit = git(root, "log", "-1", "--format=%H", "--", EXCEPTIONS).strip()
    roles = git(root, "log", "-1", "--format=%(trailers:key=Role,valueonly)", commit).split() if commit else []
    named = f"{EXCEPTIONS} (last commit {commit[:12] or 'none'}, Role {roles or 'none'})"
    why = None
    if not tracked:
        why = "it was never committed"
    elif project.dirty(root) and EXCEPTIONS in project.dirty(root):
        why = "it is modified and not committed"
    elif roles != [OWNER]:
        why = f"its last commit carries the Role trailer {roles}, not {OWNER} alone"
    if why:
        raise refuse("EXCEPTIONS_NOT_OWNERS", f"{named} is not the owner's: {why}; only the owner accepts an exception "
                     "(CAP-44.h)", file=EXCEPTIONS, commit=commit or None, roles=roles)
    try:
        entries = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise refuse("EXCEPTIONS_UNREADABLE", f"{EXCEPTIONS} cannot be read: {exc!r}", file=EXCEPTIONS) from None
    entries = [] if entries is None else entries
    if not isinstance(entries, list) or not all(
            isinstance(item, dict) and isinstance(item.get("condition"), str) and item["condition"]
            and isinstance(item.get("decision"), str) and DECISION.match(item["decision"]) for item in entries):
        raise refuse("EXCEPTIONS_UNREADABLE", f"{EXCEPTIONS} is not a list of {{condition: <name>, decision: DEC-n}}",
                     file=EXCEPTIONS)
    return [{"condition": item["condition"], "decision": item["decision"]} for item in entries]


# --------------------------------------------------------------------------
# The live tools: child ``gov`` processes of this interpreter, at the repository root, with --json
# --------------------------------------------------------------------------

def _live(tool: str):
    def run(root: Path) -> tuple[int, str]:
        import gov

        source = str(Path(gov.__file__).resolve().parents[1])
        env = {**os.environ, "PYTHONPATH": os.pathsep.join([source, *filter(None, [os.environ.get("PYTHONPATH")])])}
        try:
            done = subprocess.run([sys.executable, "-m", "gov.cli.main", tool, "--json"], cwd=root, env=env,
                                  capture_output=True, text=True, timeout=TOOL_TIMEOUT)
        except (OSError, subprocess.SubprocessError) as exc:
            return -1, json.dumps({"ok": False, "error": {"code": "TOOL_NOT_RUN", "message": repr(exc)}})
        return done.returncode, done.stdout
    return run


LIVE = {"doctor": _live("doctor"), "check": _live("check")}


def _parts(out: str, key: str):
    """What the ``--json`` envelope holds under ``key``: in ``result`` at exit 0, in ``error.details`` otherwise."""
    text = out.strip()
    try:
        envelope = json.loads(text)
    except ValueError:
        envelope = json.loads(text[text.rindex("\n{") + 1:])
    for where in (envelope.get("result"), (envelope.get("error") or {}).get("details")):
        if isinstance(where, dict) and key in where:
            return where[key]
    raise ValueError(f"the envelope holds no {key!r}")


# --------------------------------------------------------------------------
# The conditions
# --------------------------------------------------------------------------

def _head(root: Path, tracked: dict, rel: str):
    """``(frontmatter, sha256, problem)`` of the committed ``rel``: the hash is that of the bytes, whatever they hold."""
    if rel not in tracked:
        return None, None, f"{rel} is not a committed file of the project"
    data = project.blob(root, tracked[rel])
    try:
        return project.read_record(root, tracked, rel)[0], project.sha256(data), None
    except GovError as exc:
        return None, project.sha256(data), exc.message


def _roles(root: Path, rel: str) -> tuple[str | None, list[str]]:
    commit = git(root, "log", "-1", "--format=%H", "--", rel).strip()
    return (commit or None), (git(root, "log", "-1", "--format=%(trailers:key=Role,valueonly)", commit).split()
                              if commit else [])


def _auditor_entry(root: Path, tracked: dict, rel) -> dict:
    """The auditor record as it stands: path, sha256, the commit that last touched it, its session, its role."""
    entry = {"path": rel if isinstance(rel, str) else None, "sha256": None, "commit": None, "session": None,
             "role": None}
    if not isinstance(rel, str) or rel not in tracked:
        return entry
    head, entry["sha256"], _ = _head(root, tracked, rel)
    entry["commit"], roles = _roles(root, rel)
    entry["role"] = lite_gates.AUDITOR if roles == [lite_gates.AUDITOR] else (",".join(roles) or "none")
    session = (head or {}).get("auditor_session")
    entry["session"] = session if isinstance(session, str) and session else None
    return entry


def _chain_checks(checks: list, evidence: dict, root: Path, tracked: dict):
    """The stage records A0 to A6 and A8: each committed, readable, naming its stage and standing on the record before
    it as that record now is (a record before it that is not committed is not compared: its own condition names it).
    Returns the records and their hashes."""
    records, hashes, problems, previous = {}, {}, {}, ("none", None)
    for stage in STAGE_CONDITIONS:
        rel = project.record_path(stage)
        evidence[stage] = {"command": None, "exit": None, "path": rel}
        head, sha, problem = _head(root, tracked, rel)
        if head is not None:
            records[stage] = head
        if sha is not None:
            hashes[stage] = sha

        def find(stage=stage, rel=rel, head=head, problem=problem, before=previous):
            if problem:
                return [problem], None
            failed = [] if head.get("stage") == stage else [f"{rel} names the stage {head.get('stage')!r}, not {stage}"]
            expected = before[1]
            if before[0] != "missing" and head.get("stands_on") != expected:
                failed.append(f"{rel} does not stand on the record of the stage before it as that record now is "
                              f"(it stands on {head.get('stands_on')!r}, that record is {expected!r})")
            return failed, None
        lite_gates._check(checks, stage, find)
        previous = ("missing", None) if sha is None else ("there", sha)
    return records, hashes


def _a5_review(checks, evidence, run):
    from gov.adopt import stages

    a5 = run.records.get("A5")
    rel = (a5 or {}).get("verdict")
    evidence[A5_REVIEW] = {"command": None, "exit": None, "path": rel if isinstance(rel, str) else
                           project.record_path("A5")}

    def find():
        if a5 is None:
            raise GovError("ADOPT_RECORD_MISSING", f"{project.record_path('A5')} is not a readable committed record")
        held = stages._verdict(run, rel)  # the A5 rule: pass, this path map, the auditor's commit and session
        if held["verdict_sha256"] != a5.get("verdict_sha256"):
            return [f"{rel} is not the verdict A5 accepted (its sha256 is {held['verdict_sha256']}, A5 recorded "
                    f"{a5.get('verdict_sha256')!r})"], None
        return [], None
    lite_gates._check(checks, A5_REVIEW, find)
    return _auditor_entry(run.root, run.tracked, rel)


def _native(checks, evidence, run):
    from gov.adopt import stages

    a3 = run.records.get("A3")
    evidence[NATIVE] = {"command": None, "exit": None, "path": project.record_path("A3")}

    def find():
        if a3 is None:
            raise GovError("ADOPT_RECORD_MISSING", f"{project.record_path('A3')} is not a readable committed record")
        entries = {item["path"]: item for item in a3["artefacts"]}
        held = {**run.tracked, **{rel: "" for rel in entries}}  # what was tracked when A3 was written, and now
        a6 = run.records.get("A6") or {}
        executed = [item for batch in a6.get("batches") or [] for item in batch.get("artefacts") or []]
        failed = []
        moving = {path for path, item in entries.items() if item.get("action") in project.MOVING}
        moving |= {item["path"] for item in executed if item.get("action") in project.MOVING}
        for rel in sorted(moving):
            manifest = stages._native(rel, held)
            grounds = (entries.get(rel) or {}).get("justification")
            if manifest and not (isinstance(grounds, dict) and all(
                    isinstance(grounds.get(key), str) and grounds[key].strip()
                    for key in ("materially_better", "migration_risk"))):
                failed.append(f"{rel} is moved out of the native package layout of {manifest} without both grounds "
                              "(justification.materially_better and justification.migration_risk, CAP-44.j)")
        return failed, None
    lite_gates._check(checks, NATIVE, find)


def _gate(checks, evidence, run, gate: str, name: str):
    """The lite gate ``gate``: its record committed, readable, ``result: pass`` and standing on the record it stands
    on as that record now is; the auditor it names passes the re-read (V4) and says ``pass``."""
    rel = lite_gates.record_path(gate)
    evidence[name] = {"command": None, "exit": None, "path": rel}
    head, _, problem = _head(run.root, run.tracked, rel)
    standing = lite_gates.STANDS_ON[gate]

    def find():
        if problem:
            return [problem], None
        failed = []
        if head.get("result") != "pass":
            failed.append(f"{rel} says result {head.get('result')!r}, not 'pass'")
        if head.get("stands_on") != run.hashes.get(standing):
            failed.append(f"{rel} does not stand on the {standing} record as it now is")
        named = (head.get("auditor") or {}).get("record")
        found = lite_gates._auditor(
            SimpleNamespace(**{**run.__dict__, "args": SimpleNamespace(verdict=named, session=run.args.session)}), gate)
        if found["verdict"] != "pass":
            failed.append(f"the auditor's record {named} says {found['verdict']!r}, not 'pass'")
        return failed, None
    lite_gates._check(checks, name, find)
    auditor = (head or {}).get("auditor")
    return _auditor_entry(run.root, run.tracked, auditor.get("record") if isinstance(auditor, dict) else None)


def _tools(checks, evidence, root: Path, tools):
    """``gov doctor`` and ``gov check`` once each: the release's pin, the doctor's exit, the check's families."""
    ran = {}
    for tool in ("doctor", "check"):
        run = (tools or {}).get(tool) or LIVE[tool]
        try:
            code, out = run(root)
        except Exception as exc:  # whatever stops the tool: it gave no answer
            code, out = -1, json.dumps({"ok": False, "error": {"code": "TOOL_NOT_RUN", "message": repr(exc)}})
        ran[tool] = (code if isinstance(code, int) else -1, out if isinstance(out, str) else "")
    for name, tool in ((RELEASE, "doctor"), (DOCTOR, "doctor"), (CHECK, "check")):
        evidence[name] = {"command": f"gov {tool} --json", "exit": ran[tool][0], "path": None}
    code, out = ran["doctor"]

    def release():
        lock = _parts(out, "framework_lock")
        match = lock.get("match") if isinstance(lock, dict) else None
        return ([] if match == "MATCH" else [f"gov doctor's framework_lock part says {match!r}, not MATCH"]), None

    def doctor():
        return ([] if code == 0 else [f"gov doctor exits {code}, not 0"]), None

    def check():
        families = _parts(ran["check"][1], "families")
        if not isinstance(families, dict) or not families:
            raise ValueError("gov check reports no families")
        red = sorted(name for name, family in families.items()
                     if not isinstance(family, dict) or family.get("status") == "RED")
        return ([f"gov check reports RED: {', '.join(red)}"] if red else []), None
    lite_gates._check(checks, RELEASE, release)
    lite_gates._check(checks, DOCTOR, doctor)
    lite_gates._check(checks, CHECK, check)


def _ticket(checks, evidence, root: Path, tracked: dict):
    """One ticket ``closed`` whose close record is of type ``close`` with no test failed or in error and one passed."""
    seen = []

    def find():
        failed = []
        for rel in sorted(path for path in tracked if re.fullmatch(r"\.tickets/[^/]+\.md", path)):
            head, _, problem = _head(root, tracked, rel)
            if problem or head.get("status") != "closed":
                continue
            ticket = head.get("id") if isinstance(head.get("id"), str) and head.get("id") else Path(rel).stem
            close = f"docs/close/{ticket}/CL-{ticket}.md"
            seen.append(close)
            record, _, problem = _head(root, tracked, close)
            run = (record or {}).get("tests_run")
            if problem:
                failed.append(f"{rel} is closed: {problem}")
            elif record.get("type") != "close":
                failed.append(f"{close} is not a record of type close")
            elif not isinstance(run, dict) or any(type(run.get(key)) is not int for key in ("failed", "errors", "passed")):
                failed.append(f"{close} gives no counts of tests run")
            elif run["failed"] or run["errors"] or run["passed"] < 1:
                failed.append(f"{close}: {run['passed']} passed, {run['failed']} failed, {run['errors']} in error")
            else:
                evidence[TICKET]["path"] = close
                return [], None
        return failed or ["no ticket in .tickets/ is closed"], None
    evidence[TICKET] = {"command": None, "exit": None, "path": ".tickets"}
    lite_gates._check(checks, TICKET, find)
    if checks[-1]["result"] != "met" and seen:
        evidence[TICKET]["path"] = seen[0]


def compute(root: Path, session: str, tools: dict | None = None) -> dict:
    """The record's frontmatter as the stage would commit it, without ``produced_by``. Reads only. A condition that
    fails is ``not met``; an exceptions file that is not the owner's raises ``ADOPT_EXCEPTIONS_NOT_OWNERS``."""
    return _compute(Path(root).resolve(), session, tools, read_exceptions(Path(root).resolve()))


def _compute(root: Path, session: str, tools, entries: list) -> dict:
    from gov.adopt.stages import Run

    head = project.resolve(root, "HEAD")
    tracked = project.tree(root)
    checks, evidence = [], {}
    records, hashes = _chain_checks(checks, evidence, root, tracked)
    gates = {}
    for gate, name in (("A7", LITE_A7), ("A10", LITE_A10)):
        gates[gate] = _head(root, tracked, lite_gates.record_path(gate))
        if gates[gate][0] is not None:
            records[gate] = gates[gate][0]  # the sessions of the gates count with the stages' (V4)
    run = Run(root, SimpleNamespace(session=session), {}, "VERDICT", tracked, records, hashes)
    auditors = [_a5_review(checks, evidence, run)]
    _native(checks, evidence, run)
    auditors += [_gate(checks, evidence, run, gate, name) for gate, name in (("A7", LITE_A7), ("A10", LITE_A10))]
    _tools(checks, evidence, root, tools)
    _ticket(checks, evidence, root, tracked)

    by_name = {item["check"]: item for item in checks}
    conditions = [{"name": name, "source": SOURCE, "state": by_name[name]["result"], "evidence": evidence[name],
                   "detail": by_name[name]["detail"]} for name in CONDITIONS]
    accepted, unused = {}, []
    for entry in entries:
        found = next((item for item in conditions if item["name"] == entry["condition"]), None)
        if found and found["state"] == "not met" and found["name"] not in accepted:
            accepted[found["name"]] = entry["decision"]
        else:
            unused.append(entry)
    for item in conditions:
        if item["name"] in accepted:
            item["state"], item["owner_entry"] = "accepted", accepted[item["name"]]
    a10 = hashes_of(root, tracked, "A10")
    front = {"id": "ADOPT-VERDICT", "type": "adoption-verdict", "status": "RECORDED", "state_class": "EVIDENCE",
             "verdict": derive(item["state"] for item in conditions), "lite": True, "session": session,
             "stands_on": a10, "commit": head, "conditions": conditions,
             "adopted_healthy_conditions": [{"number": number, "name": title, "wave": wave, "lite_part": list(part)}
                                            for number, title, wave, part in HEALTHY_TEN],
             "conditions_not_checked": list(NOT_CHECKED),
             "auditors": auditors,
             "unused_exceptions": unused}
    if RECORD in tracked:
        front["supersedes"] = [project.sha256(project.blob(root, tracked[RECORD]))]
    return front


def hashes_of(root: Path, tracked: dict, gate: str):
    rel = lite_gates.record_path(gate)
    return project.sha256(project.blob(root, tracked[rel])) if rel in tracked else None


# --------------------------------------------------------------------------
# check_record (F1, F2)
# --------------------------------------------------------------------------

def check_record(root: Path) -> dict:
    """The committed record's frontmatter when it is a verdict the stage produced; else a refusal naming the cause."""
    root = Path(root).resolve()
    tracked = project.tree(root)
    head, data = project.read_record(root, tracked, RECORD)
    text = data.decode("utf-8")
    given = head.get("produced_by")
    if not isinstance(given, str) or given != digest(text):
        raise refuse("VERDICT_NOT_PRODUCED", f"{RECORD} was not produced by the stage: its produced_by "
                     f"({given!r}) is " + ("missing" if given is None else "not the digest of the record's text"),
                     record=RECORD)
    a10 = hashes_of(root, tracked, "A10")
    if a10 is None or head.get("stands_on") != a10:
        raise refuse("VERDICT_STALE", f"{RECORD} stands on {head.get('stands_on')!r}, not on the A10 record now "
                     f"committed ({a10!r})", record=RECORD)
    commit = git(root, "log", "-1", "--format=%H", "--", RECORD).strip()
    subject = git(root, "log", "-1", "--format=%s", commit).strip()
    wrote = [path for path in git(root, "show", "--name-only", "--format=", commit).split("\n") if path]
    if not subject.startswith("gov adopt --lite VERDICT:") or wrote != [RECORD]:
        raise refuse("VERDICT_NOT_THE_STAGES", f"{RECORD} was not committed by the stage: the commit {commit[:12]} is "
                     f"{subject!r} and touches {wrote}, not {RECORD} alone", record=RECORD, commit=commit)
    conditions = head.get("conditions")
    if not isinstance(conditions, list) or not all(
            isinstance(item, dict) and item.get("state") in STATES
            and (item["state"] != "accepted" or isinstance(item.get("owner_entry"), str)) for item in conditions):
        raise refuse("VERDICT_DISAGREES", f"{RECORD}: its conditions are not a list of named states", record=RECORD)
    expected = derive(item["state"] for item in conditions)
    if head.get("verdict") != expected:
        raise refuse("VERDICT_DISAGREES", f"{RECORD} says {head.get('verdict')!r}, its conditions give {expected}",
                     record=RECORD)
    return head


# --------------------------------------------------------------------------
# The stage
# --------------------------------------------------------------------------

def _text(front: dict) -> str:
    lines = []
    for item in front["conditions"]:
        lines.append(f"- **{item['state']}**: {item['name']}: {item['detail']}"
                     + (f" (accepted by {item['owner_entry']})" if item["state"] == "accepted" else ""))
    return ("---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=120)
            + f"---\n\n# ADOPT-VERDICT: lite adoption verdict\n\nWritten by `gov adopt --lite --stage VERDICT` (session "
            f"`{front['session']}`) at commit `{front['commit']}`: **{front['verdict']}**.\n\n" + "\n".join(lines)
            + "\n\nThis verdict is lite (CAP-44.h): it does not check "
            + "; ".join(front["conditions_not_checked"]) + ".\n")


def stage(run) -> dict:
    root = run.root
    entries = read_exceptions(root)  # first: a file that is not the owner's is refused whatever else is wrong
    project.require_repository(root)
    if RECORD in project.tree(root):
        check_record(root)  # a record the stage did not produce is not replaced
    front = _compute(root, run.args.session, None, entries)
    text = with_digest(_text(front))
    project.commit(root, SUBJECT, {RECORD: text})
    result = {"stage": "VERDICT", "record": RECORD, "verdict": front["verdict"], "conditions": front["conditions"]}
    if front["verdict"] == "NOT_ADOPTED_HEALTHY":
        failed = [item for item in front["conditions"] if item["state"] == "not met"]
        raise refuse("NOT_ADOPTED", f"the verdict is NOT_ADOPTED_HEALTHY, recorded in {RECORD}; not met: "
                     + "; ".join(f"{item['name']}: {item['detail']}" for item in failed), record=RECORD,
                     verdict=front["verdict"], conditions=front["conditions"], not_met=[item["name"] for item in failed])
    return result
