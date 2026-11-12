"""The lite A7 and A10 gates of ``gov adopt --lite`` (W2-52; CAP-44.f, CAP-44.h, CAP-44.k; DEC-741, DEC-722).

Each gate is a stage of its own, run by the session that ran the stages on the committed record of a fresh
Independent Auditor session (``--verdict <path>``, the A5 precedent). It checks the project itself beyond the
auditor's word and commits a record of its own in the adoption run's folder, which gives the conditions a lite
verdict carries in W2-02's form (``name``, ``source``, ``state``):

- **A7** stands on A6. It checks the A6 migration against the A3 path map and the A4 plan reviewed at A5.
- **A10** stands on A8. It checks A8's extraction and retirement, the derived state rebuilt from git (CAP-20) and
  the canary of each index (CAP-55).

A record the gate stands on that is missing or cannot be read, and an auditor's record that is not a committed,
readable record of this gate by the Independent Auditor covering every record it checks, refuse: nothing is
written. A check that fails, or an auditor's verdict that is not ``pass`` (DEC-490), commits a failing record whose
conditions are ``not met``. A gate never accepts a condition: only the owner does (CAP-44.h, DEC-741 F). What lies
beyond the lite form stays for Wave 3 (CAP-44.k), and each record says so.
"""

from __future__ import annotations

import dataclasses
import os

import yaml

from gov.adopt import project
from gov.adopt.project import FOLDER, git, refuse
from gov.cli.errors import GovError

GATES = ("A7", "A10")
STANDS_ON = {"A7": "A6", "A10": "A8"}
CHECKED = {"A7": ("A3", "A4", "A5", "A6"), "A10": ("A8",)}  # the records the auditor's pass must cover (CAP-44.f)
TITLES = {"A7": "independent migration verification", "A10": "independent memory verification"}
AUDITOR = "independent-auditor"
# The conditions each record gives (CAP-44.h (4), (6), (9), lite parts), and the checks each one stands on (None: all).
CONDITIONS = {
    "A7": [("lite A7 gate: the migration independently verified (CAP-44.h condition 4, lite part)", "CAP-44.f", None)],
    "A10": [("lite A10 gate: the memory independently verified (CAP-44.h condition 6, lite part)", "CAP-44.f", None),
            ("lite A10 gate: the derived state rebuilt from git (CAP-44.h condition 9, lite part)", "CAP-44.h",
             ("the auditor's verdict", "the derived state rebuilt from git"))],
}
WAVE_3 = {
    "A7": "Stays for Wave 3 (CAP-44.k): A7 beyond its lite form, by a separate verifier role (CAP-47.a), and "
          "condition (4) of CAP-44.h in full.",
    "A10": "Stays for Wave 3 (CAP-44.k): A10 over the A9 knowledge fabric, CAP-49's memory checks, and a separate "
           "verifier role (CAP-47.a); conditions (6) and (9) of CAP-44.h in full.",
}


def record_path(gate: str) -> str:
    return f"{FOLDER}/{gate}-{TITLES[gate].replace(' ', '-')}.md"


def _stood_on(run, gate: str) -> tuple[dict, dict]:
    """The records of A0 up to the stage the gate stands on, and their hashes. Missing or unreadable refuses."""
    records, hashes = {}, {}
    for stage in project.STAGES[:project.STAGES.index(STANDS_ON[gate]) + 1]:
        rel = project.record_path(stage)
        if rel not in run.tracked:
            raise refuse("STAGE_MISSING", f"gate {gate} stands on stage {stage}, which left no committed record ({rel}): "
                                          f"a missing record is a named failure, never healthy", stage=stage)
        records[stage], data = project.read_record(run.root, run.tracked, rel)
        hashes[stage] = project.sha256(data)
    return records, hashes


def _auditor(run, gate: str) -> dict:
    """The auditor's record for ``gate``, held to the A5 rule for each record it checks; a refusal otherwise."""
    rel = run.args.verdict
    if not rel:
        raise refuse("NO_VERDICT", f"gate {gate} needs --verdict <path>: the Independent Auditor's committed record")
    head, data = project.read_record(run.root, run.tracked, rel)
    if head.get("stage") != gate:
        raise refuse("VERDICT_OTHER_STAGE", f"{rel}: its stage is {head.get('stage')!r}, not {gate}: another stage's "
                                            "verdict is no verdict of this gate", verdict=rel)
    if not isinstance(head.get("verdict"), str) or not head["verdict"]:
        raise refuse("RECORD_UNREADABLE", f"{rel} states no verdict: a partial record is no pass", record=rel)
    brought = git(run.root, "log", "-1", "--format=%H", "--", rel).strip()
    roles = git(run.root, "log", "-1", "--format=%(trailers:key=Role,valueonly)", brought).split()
    wrote = [path for path in git(run.root, "show", "--name-only", "--format=", brought).split("\n")
             if path.startswith(FOLDER + "/")]
    if roles != [AUDITOR] or wrote:
        raise refuse("VERDICT_NOT_INDEPENDENT", f"{rel}: the commit that brought it ({brought[:12]}) carries the Role "
                     f"trailer {roles}, not {AUDITOR} alone" + (f", and wrote {wrote}" if wrote else ""), verdict=rel)
    sessions = {stage: record.get("session") for stage, record in run.records.items()}
    session = head.get("auditor_session")
    if not isinstance(session, str) or not session or session in (*sessions.values(), run.args.session):
        raise refuse("VERDICT_NOT_INDEPENDENT", f"{rel}: its auditor_session ({session!r}) must be named and differ "
                     f"from the sessions that ran the stages ({sessions}, now {run.args.session!r}): a fresh "
                     "Independent Auditor session (CAP-44.f)", verdict=rel)
    listed = head.get("checked")
    if not isinstance(listed, list) or not all(isinstance(item, dict) for item in listed):
        raise refuse("RECORD_UNREADABLE", f"{rel} has no list 'checked' of the records the auditor checked", record=rel)
    given = {item.get("record"): item.get("sha256") for item in listed}
    for stage in CHECKED[gate]:
        checked = project.record_path(stage)
        if checked not in given:
            raise refuse("VERDICT_INCOMPLETE", f"{rel} does not cover the {stage} record {checked}, which gate {gate} "
                                               "checks: a pass that leaves one out is no pass", verdict=rel, stage=stage)
        if given[checked] != run.hashes[stage]:
            raise refuse("VERDICT_OTHER_RECORD", f"{rel}: the sha256 it gives for the {stage} record {checked} "
                         f"({given[checked]!r}) is not that record's as it stands ({run.hashes[stage]})", verdict=rel,
                         stage=stage)
    return {"record": rel, "sha256": project.sha256(data), "commit": brought, "session": session,
            "verdict": head["verdict"]}


def _check(checks: list, name: str, find) -> object:
    """Run one check: ``find()`` gives what fails (a list of texts) and what it read. What cannot be read fails."""
    try:
        failed, read = find()
    except (GovError, KeyError, TypeError, AttributeError, ValueError, OSError) as exc:
        failed, read = [f"it cannot be established: {getattr(exc, 'message', None) or exc!r}"], None
    checks.append({"check": name, "result": "not met" if failed else "met",
                   "detail": "; ".join(failed) if failed else "as recorded"})
    return read


def _chain(run) -> tuple[list, None]:
    """Each stage record names its stage and stands on the record before it as that record now is."""
    failed, previous = [], None
    for stage, head in run.records.items():
        if head.get("stage") != stage or head.get("stands_on") != previous:
            failed.append(f"{project.record_path(stage)} does not stand on the record of the stage before it as that "
                          "record now is")
        previous = run.hashes[stage]
    return failed, None


def _moves(batches: list) -> list:
    return [(batch["batch"], [(item["path"], item["action"], item.get("target")) for item in batch["artefacts"]])
            for batch in batches]


def _a7_checks(run, checks: list) -> dict:
    from gov.adopt.stages import _plan

    a4, a5, a6 = (run.records[stage] for stage in ("A4", "A5", "A6"))
    plan, path_map = project.record_path("A4"), project.record_path("A3")

    def reviewed():
        return ([] if a5.get("path_map_hash") == run.hashes["A3"] else
                [f"the path map {path_map} is not the one A5 reviewed: {project.record_path('A5')} gives path_map_hash "
                 f"{a5.get('path_map_hash')!r}, the path map is {run.hashes['A3']}"]), None

    def planned():
        differs = [key for key, value in _plan(run).items() if a4.get(key) != value]
        return ([f"the plan {plan} is not the plan of the path map {path_map}: its {', '.join(differs)} differ"]
                if differs else []), None

    def executed():
        failed = [] if a6.get("path_map_hash") == run.hashes["A3"] else [
            f"{project.record_path('A6')} executed another path map than {path_map}"]
        if _moves(a6["batches"]) != _moves(a4["batches"]):
            failed.append(f"the batches {project.record_path('A6')} executed are not the plan {plan}: "
                          f"{_moves(a6['batches'])} against {_moves(a4['batches'])}")
        return failed, None

    def in_project():
        failed = []
        for batch in a4["batches"]:
            for item in batch["artefacts"]:
                if item.get("target") and item["target"] not in run.tracked:
                    failed.append(f"the target {item['target']} of {item['path']} is not in the project")
                if item["path"] in run.tracked:
                    failed.append(f"{item['path']} is still at its origin ({item['action']} to {item.get('target')})")
        return failed, None

    _check(checks, "the path map reviewed at A5", reviewed)
    _check(checks, "the plan of the path map", planned)
    _check(checks, "the plan executed at A6", executed)
    _check(checks, "the migration in the project", in_project)
    return {}


def _a10_checks(run, checks: list) -> dict:
    from gov.adopt import legacy
    from gov.rebuild import command

    retired = run.records["A8"].get("retired")  # what is not a list of retirements fails each check that reads it

    def retirement():
        failed = []
        for item in retired:
            rel, ref = item["path"], item["reachable_at"]
            if rel in run.tracked or os.path.lexists(run.root / rel):
                failed.append(f"{rel} ({item['kind']}), retired by A8, is back in the active tree")
            if project._run(run.root, ("cat-file", "-e", f"{ref}:{rel}"), (0, 128))[0]:
                failed.append(f"{rel} is not reachable at {ref}")
        return failed, [{key: item[key] for key in ("path", "kind", "reachable_at")} for item in retired]

    def extraction():
        chats = {item["path"]: project._run(run.root, ("cat-file", "blob", f"{item['reachable_at']}:{item['path']}"),
                                            (0,))[1] for item in retired if item["kind"] == "chat-database"}
        try:
            legacy._extractions(run, chats, {item["path"] for item in retired})
        except GovError as exc:
            said = [item["disposition"] for item in retired if item["kind"] == "chat-database"]
            return [f"{exc.message}; A8 recorded: {' | '.join(said)}"], None
        return [], None

    def rebuilt():
        done = command.run(run.root, run.args, run.config)
        stores = done["stores"]
        failed = [f"the {name} index was not recreated: {store.get('reason')}" for name, store in stores.items()
                  if name in ("lexical", "semantic") and store.get("status") != "recreated"]
        return failed, {"digest": done["digest"], "stores": stores}

    out = _check(checks, "the A8 retirement", retirement)
    _check(checks, "the A8 extraction", extraction)
    derived = _check(checks, "the derived state rebuilt from git", rebuilt)
    try:
        from gov.retrieval.canary import run_canaries
        found = run_canaries(run.root)
    except Exception as exc:  # whatever stops the canaries: none of them hit
        found = {index: {"passed": False, "status": "FACET_UNAVAILABLE", "reason": repr(exc)}
                 for index in ("lexical", "semantic")}
    for index in ("lexical", "semantic"):
        result, store = found.get(index) or {}, ((derived or {}).get("stores") or {}).get(index) or {}
        ok = result.get("passed") is True and store.get("status") == "recreated"
        checks.append({"check": f"the canary of the {index} index", "result": "met" if ok else "not met",
                       "detail": f"{result.get('status', 'FACET_UNAVAILABLE')}" + ("" if ok else
                                 f": misses {result.get('misses')}, {result.get('reason') or 'no reason given'}; "
                                 f"the {index} index is {store.get('status', 'not rebuilt')}")})
    return {"retired": out, "rebuild": derived, "canaries": found}


def gate(run) -> dict:
    gate = run.stage
    rel = record_path(gate)
    if rel in run.tracked or os.path.lexists(run.root / rel):
        raise refuse("GATE_RECORDED", f"{rel} is already there: a gate writes over no record", record=rel)
    records, hashes = _stood_on(run, gate)
    run = dataclasses.replace(run, records=records, hashes=hashes)
    auditor = _auditor(run, gate)
    checks = [{"check": "the auditor's verdict", "result": "met" if auditor["verdict"] == "pass" else "not met",
               "detail": f"{auditor['record']} by {auditor['session']}: {auditor['verdict']!r}; only 'pass' passes"}]
    _check(checks, "the stage records", lambda: _chain(run))
    found = (_a7_checks if gate == "A7" else _a10_checks)(run, checks)
    failed = [item for item in checks if item["result"] != "met"]
    conditions = [{"name": name, "source": source,
                   "state": "met" if not [item for item in failed if only is None or item["check"] in only]
                   else "not met"} for name, source, only in CONDITIONS[gate]]
    head = {"id": f"ADOPT-{gate}", "type": "evidence", "status": "RECORDED", "state_class": "EVIDENCE",
            "stage": gate, "session": run.args.session, "stands_on": hashes[STANDS_ON[gate]],
            "result": "fail" if failed else "pass", "commit": project.resolve(run.root, "HEAD"),
            "records": [{"stage": stage, "record": project.record_path(stage), "sha256": hashes[stage]}
                        for stage in CHECKED[gate]],
            "auditor": auditor, **found, "checks": checks, "conditions": conditions, "wave_3": WAVE_3[gate]}
    text = ("---\n" + yaml.safe_dump(head, sort_keys=False, allow_unicode=True, width=120)
            + f"---\n\n# ADOPT-{gate}: {TITLES[gate]} (lite)\n\nWritten by `gov adopt --lite --stage {gate}` on the "
            f"Independent Auditor's record `{auditor['record']}` (session `{auditor['session']}`).\n\n"
            + "".join(f"- **{item['result']}**: {item['check']}: {item['detail']}\n" for item in checks)
            + f"\n{WAVE_3[gate]}\n")
    project.commit(run.root, f"gov adopt --lite {gate}: {TITLES[gate]} (lite)", {rel: text})
    if failed:
        raise refuse("GATE_NOT_PASSED", f"gate {gate} did not pass, recorded in {rel}: "
                     + "; ".join(f"{item['check']}: {item['detail']}" for item in failed),
                     record=rel, conditions=conditions)
    return {"stage": gate, "record": rel, "conditions": conditions,
            **({"digest": found["rebuild"]["digest"]} if found.get("rebuild") else {})}
