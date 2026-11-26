"""Support code for W2-206's fix lines IT-1 and IT-2, the impact trace at the landing (README, "Fix: the impact trace
at the landing").

It stands on W2-206's support (and through it on W2-202's and W2-115b's planted project kit). Added here:

- planted records with real links (a decision register named by the path map, specifications, tickets, test records)
  and the branches that change, add and remove them;
- the oracle: ``gov impact <id> --json`` on a scratch clone at a revision, its record store loaded from that ``HEAD``;
- the planted runs, each built once per test session under a lock, each checking itself (``fixture: ...``).
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import subprocess
import sys
import traceback

import yaml

import w2_206_support as support
from w2_206_support import A, B, CHANGED, kit, module_rel

LIMIT_VARIABLE = "GOV_QUEUE_IMPACT_TIMEOUT"
REGISTER_REL = "docs/DECISIONS.md"
NO_REGISTER_REL = "docs/NO_SUCH_REGISTER.md"
SPEC1, SPEC2, SPEC3 = "docs/specs/SPEC-001.md", "docs/specs/SPEC-002.md", "docs/specs/SPEC-003.md"
REC_TICKET = ".tickets/PROJ-rec3.md"     # a ticket record the branch changes
PLAIN_NOTE, NO_ID_NOTE = "docs/notes/plain.md", "docs/notes/no-id.md"    # Markdown that is no record
# every record file A's branch holds: id -> path
PRESENT = {"DEC-001": REGISTER_REL, "DEC-004": REGISTER_REL, "SPEC-001": SPEC1, "SPEC-002": SPEC2,
           "PROJ-rec3": REC_TICKET}
REMOVED = {"DEC-003": REGISTER_REL, "SPEC-003": SPEC3}
FIX_LINE = "the specification states the wrong limit"


def entry_text(number, body):
    return (f"### DEC-{number} A planted decision {number}\n"
            "- **Status:** ACCEPTED (owner, 2026-11-01)\n"
            f"- **Decision:** {body}\n\n")


def register(*entries):
    return "# Decision register\n\n" + "".join(entry_text(number, body) for number, body in entries)


def record(record_id, kind, body="Text.", status="ACTIVE", **keys):
    front = {"id": record_id, "type": kind, "status": status, "state_class": "AUTHORITATIVE",
             "title": f"Record {record_id}", **keys}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + f"---\n\n# {record_id}\n\n{body}\n"


def path_map(register_rel=REGISTER_REL):
    return yaml.safe_dump({**kit.PATH_MAP, "decision_register": register_rel}, sort_keys=False)


BASE_REGISTER = register(("001", "The first."), ("003", "The one the branch removes."), ("002", "Untouched."))
BRANCH_REGISTER = register(("001", "The first, changed by the branch."), ("002", "Untouched."),
                           ("004", "New in the branch."))


def base_records(register_rel=REGISTER_REL):
    return {
        kit.PATH_MAP_REL: path_map(register_rel),
        REGISTER_REL: BASE_REGISTER,
        SPEC1: record("SPEC-001", "specification"),
        SPEC3: record("SPEC-003", "specification"),
        REC_TICKET: record("PROJ-rec3", "task", status="open"),
        ".tickets/PROJ-rec1.md": record("PROJ-rec1", "task", status="open",
                                        implements=["DEC-001", "SPEC-001"]),
        ".tickets/PROJ-rec2.md": record("PROJ-rec2", "task", status="open", implements=["DEC-004", "SPEC-002"],
                                        depends_on=["PROJ-rec3", "DEC-002"]),
        "docs/evidence/TR-0001.md": record("TR-0001", "evidence", tests=["DEC-001", "SPEC-001"]),
        "docs/evidence/TR-0002.md": record("TR-0002", "evidence",
                                           tests=["DEC-004", "SPEC-002", "PROJ-rec3", "DEC-002"]),
        PLAIN_NOTE: "# A note\n\nNo frontmatter.\n",
        NO_ID_NOTE: "---\ntitle: A note\n---\n\n# A note\n",
    }


def record_branch(p, ticket, name, trailers=(), files=None, delete=()):
    """``name`` from the base, one commit of ``ticket``'s."""
    p.branch_from(name)
    for rel in delete:
        (p.root / rel).unlink()
    tip = p.commit(f"work on {ticket.id}", kit.ENGINEER, [f"Task: {ticket.id}", *trailers, "Role: engineer"],
                   dict(files or {}))
    p.home()
    p.tips[ticket.id], p.branches[ticket.id] = tip, name
    return tip


MAIN_CHANGE = {
    REGISTER_REL: BRANCH_REGISTER,
    SPEC1: record("SPEC-001", "specification", body="Changed by the branch."),
    SPEC2: record("SPEC-002", "specification", body="New in the branch."),
    REC_TICKET: record("PROJ-rec3", "task", status="open", body="Changed by the branch."),
    PLAIN_NOTE: "# A note\n\nChanged.\n",
    NO_ID_NOTE: "---\ntitle: A note\n---\n\n# A note, changed\n",
    module_rel("widget"): CHANGED,
}


# --------------------------------------------------------------------------
# The oracle: gov impact on a scratch clone
# --------------------------------------------------------------------------

def loaded_clone(p, revision, name):
    """A scratch clone at ``revision`` whose record store is loaded from that ``HEAD``."""
    scratch = support.base.scratch_at(p, revision, name)
    return _load(p, scratch)


def _load(p, scratch):
    done = subprocess.run([sys.executable, "-c", "import sys\nfrom gov.store import loader\nloader.load(sys.argv[1])",
                           str(scratch)], cwd=str(scratch), env=support.env_of(p), capture_output=True, text=True,
                          timeout=300)
    assert done.returncode == 0, f"fixture: the record store does not load in {scratch}:\n{done.stderr[-3000:]}"
    return scratch


def impact_of(p, scratch, record_id):
    """``gov impact <id> --json``: ``{"tickets", "tests", "complete"}``, or ``{"refused": <code>}``."""
    done = support.gov(scratch, "impact", record_id, "--json", "--root", str(scratch), env=support.env_of(p))
    answer = support.one_object(done["stdout"])
    assert answer is not None, f"fixture: gov impact {record_id} printed no envelope\n{support.said(done)}"
    if not answer.get("ok"):
        return {"refused": (answer.get("error") or {}).get("code")}
    result = answer["result"]
    affected = result["affected"]
    return {"tickets": sorted(item["id"] for item in affected["tickets"]),
            "tests": sorted(item["id"] for item in affected["tests"]), "complete": result["complete"]}


def oracle(p, scratch):
    """What ``gov impact`` says of every planted record of A's change in ``scratch``; checks the fixture."""
    found = {record_id: impact_of(p, scratch, record_id) for record_id in (*PRESENT, *REMOVED)}
    for record_id in PRESENT:
        said = found[record_id]
        assert said.get("tickets") and said.get("tests"), \
            f"fixture: gov impact {record_id} names no affected ticket or no test: {said}"
    for record_id in REMOVED:
        assert found[record_id].get("refused") == "IMPACT_CHANGE_UNKNOWN", \
            f"fixture: gov impact {record_id} still knows the removed record: {found[record_id]}"
    return found


def merged_oracle(p, tips):
    """The oracle on a scratch merge of ``tips`` onto the base (before the queue runs: the fixture's own check)."""
    scratch = support.base.scratch_at(p, p.base, "premerge")
    for tip in tips:
        kit.git(scratch, "merge", "-q", "--no-ff", "--no-edit", tip)
    found = oracle(p, _load(p, scratch))
    shutil.rmtree(scratch, ignore_errors=True)
    return found


# --------------------------------------------------------------------------
# Building
# --------------------------------------------------------------------------

def shared(factory, name, build):
    root = factory.getbasetemp()
    if os.environ.get("PYTEST_XDIST_WORKER"):
        root = root.parent
    folder = root / f"w2-206-impact-{name}"
    with open(root / f"w2-206-impact-{name}.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        done, broken = folder / "data.json", folder / "broken.txt"
        if broken.is_file():
            raise AssertionError(f"the planted run {name} could not be built:\n{broken.read_text()}")
        if done.is_file():
            return json.loads(done.read_text(encoding="utf-8"))
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        try:
            data = build(folder)
        except BaseException:
            broken.write_text(traceback.format_exc(), encoding="utf-8")
            raise
        done.write_text(json.dumps(data, default=str), encoding="utf-8")
        return data


def _held(p, taken):
    """``queue.json``'s result of a step's run (None where the answer names no record)."""
    answer = support.one_object(taken["run"]["stdout"]) or {}
    rel = (answer.get("result") or {}).get("record")
    path = p.root / rel if rel else None
    if not (path and path.is_file()):
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("result") if isinstance(data.get("result"), dict) else data


def _close_front(p, ticket, revision="main"):
    text = kit.show(p.root, revision, f"docs/close/{ticket.id}/CL-{ticket.id}.md")
    return None if text is None else kit.front_matter(text)


def build_main(folder):
    """A changes, adds and removes records (and the widget); B changes only the gadget. ``--select A B``, then
    ``A B --dry-run --out``, then the landing ``A B``."""
    p = kit.Planted(folder / "project", folder / "told", extra=base_records())
    a = record_branch(p, A, "topic/aa", files=MAIN_CHANGE, delete=[SPEC3])
    b = record_branch(p, B, "topic/bb", files={module_rel("gadget"): CHANGED})
    kit.self_check(p, {a: {A.node: "passed", kit.USES_WIDGET_NODE: "passed"}, b: {B.node: "passed"}})
    before = merged_oracle(p, [a, b])
    args = (f"{A.id}=topic/aa", f"{B.id}=topic/bb")
    select = support.step(p, *args, "--select", plain=True)
    out = folder / "out"
    dry = support.step(p, *args, "--dry-run", "--out", str(out))
    chosen = out / "select.json"
    dry["select_json"] = chosen.read_text(encoding="utf-8") if chosen.is_file() else None
    old_head = kit.rev(p.root, "main")
    land = support.step(p, *args)
    land["old_head"] = old_head
    answer = (support.one_object(land["run"]["stdout"]) or {}).get("result") or {}
    assert answer.get("landed") == [A.id, B.id], f"fixture: the landing did not land both\n{kit.describe(land['run'])}"
    scratch = loaded_clone(p, kit.rev(p.root, "main"), "oracle")
    after = oracle(p, scratch)
    assert after == before, f"fixture: gov impact on the landed head differs from the merged tree: {after} != {before}"
    land.update(held=_held(p, land), close={t.id: _close_front(p, t) for t in (A, B)})
    return {"root": str(p.root), "oracle": after, "select": select, "dry": dry, "land": land}


def build_fix(folder):
    """A is closed (no close record yet); a fix branch of A's changes SPEC-001. The landing."""
    extra = {**base_records(), A.ticket_rel: kit.ticket_text(A, "closed")}
    p = kit.Planted(folder / "project", folder / "told", extra=extra)
    tip = record_branch(p, A, "topic/aa-fix", [f"Fix: {FIX_LINE}"],
                        files={SPEC1: MAIN_CHANGE[SPEC1], module_rel("widget"): CHANGED})
    kit.self_check(p, {tip: {A.node: "passed", kit.USES_WIDGET_NODE: "passed"}})
    land = support.step(p, f"{A.id}=topic/aa-fix")
    answer = (support.one_object(land["run"]["stdout"]) or {}).get("result") or {}
    assert answer.get("landed") == [A.id], f"fixture: the fix did not land\n{kit.describe(land['run'])}"
    scratch = loaded_clone(p, kit.rev(p.root, "main"), "oracle")
    said = impact_of(p, scratch, "SPEC-001")
    assert said.get("tickets") and said.get("tests"), f"fixture: {said}"
    land.update(held=_held(p, land), close=_close_front(p, A))
    return {"oracle": {"SPEC-001": said}, "land": land}


def _failing(folder, register_rel, more_env):
    """A changes SPEC-001, B the gadget. ``--select A B``, then the landing ``A B``, both under ``more_env``."""
    p = kit.Planted(folder / "project", folder / "told", extra=base_records(register_rel))
    a = record_branch(p, A, "topic/aa", files={SPEC1: MAIN_CHANGE[SPEC1], module_rel("widget"): CHANGED})
    b = record_branch(p, B, "topic/bb", files={module_rel("gadget"): CHANGED})
    kit.self_check(p, {a: {A.node: "passed", kit.USES_WIDGET_NODE: "passed"}, b: {B.node: "passed"}})
    if register_rel == REGISTER_REL:
        loaded_clone(p, a, "loads")
    else:
        scratch = support.base.scratch_at(p, a, "noload")
        done = subprocess.run([sys.executable, "-c", "import sys\nfrom gov.store import loader\n"
                               "loader.load(sys.argv[1])", str(scratch)], cwd=str(scratch), env=support.env_of(p),
                              capture_output=True, text=True, timeout=300)
        assert done.returncode != 0 and f"{register_rel}: HEAD does not hold the register" in done.stderr, \
            f"fixture: the store loads under a register HEAD does not hold:\n{done.stderr[-2000:]}"
    args = (f"{A.id}=topic/aa", f"{B.id}=topic/bb")
    env = support.env_of(p, more_env)
    select = support.step(p, *args, "--select", plain=True, env=env)
    land = support.step(p, *args, env=env)
    land.update(held=_held(p, land), close={t.id: _close_front(p, t) for t in (A, B)},
                status={t.id: kit.status_at(p.root, "main", t.id) for t in (A, B)})
    return {"select": select, "land": land}


def build_no_register(folder):
    return _failing(folder, NO_REGISTER_REL, {})


def build_limit(folder):
    return _failing(folder, REGISTER_REL, {LIMIT_VARIABLE: "0.001"})


BUILDS = {"main": build_main, "fix": build_fix, "no_register": build_no_register, "limit": build_limit}


# --------------------------------------------------------------------------
# Reading
# --------------------------------------------------------------------------

def answer(taken, code=0):
    return kit.answer(taken["run"], code)


def impact_mapping(holder, where):
    assert isinstance(holder, dict), f"{where} is not there: {holder!r}"
    mapping = holder.get("impact")
    assert isinstance(mapping, dict), f"{where} holds no impact mapping: impact {mapping!r}; keys {sorted(holder)}"
    return mapping


def selected(taken):
    run = taken["run"]
    assert run["code"] == 0, f"gov queue --select exited {run['code']}, not 0\n{kit.describe(run)}"
    chosen = support.one_object(run["stdout"])
    assert chosen is not None, f"stdout is not one JSON object\n{kit.describe(run)}"
    return chosen


def records_by_id(entry):
    assert isinstance(entry, dict) and set(entry) == {"records", "complete"}, f"the entry is {entry!r}"
    records = entry["records"]
    assert isinstance(records, list) and all(isinstance(r, dict) for r in records), f"records: {records!r}"
    found = {r.get("id"): r for r in records}
    assert len(found) == len(records), f"a record is listed twice: {[r.get('id') for r in records]}"
    return found


def normal(value):
    """An ``impact`` mapping with every list in one order, for comparing two of them."""
    if isinstance(value, dict):
        return {key: normal(item) for key, item in value.items()}
    if isinstance(value, list):
        return sorted((normal(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True))
    return value


def is_unavailable(value):
    return isinstance(value, str) and value.startswith("unavailable (") and value.endswith(")") \
        and len(value) > len("unavailable ()")
