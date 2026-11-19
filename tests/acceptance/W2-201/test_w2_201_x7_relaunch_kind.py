"""W2-201 fix X7 (DEC-1219 (5)): the relaunch keeps the kind.

The launch's ``kind`` and ``kind_line`` are carried in its registry entry (a feature's: ``feature`` and null, or
neither key), and the watch pass's relaunch of a dead entry (``gov.dispatch.relaunch``) starts the same kind: a fix
entry ``gov launch <role> <ticket> --fix "<line>" --root <repository> -- --resume <session id> "<text>"``, a chore entry
``gov launch <role> --chore "<line>" --root <repository> -- --resume ...`` with no ticket (its entry's ``ticket`` is
its ``chore-<8 hex>`` label), for a worker and for a lead; a feature entry, or an entry from before the change, as
today.

Three ways in: dead registry entries planted on W2-205's fixture machine, relaunched by ``gov dispatch watch`` into a
stand-in ``gov`` that records its argv (``w2_201_x7_support``); real launches through ``gov launch`` on W2-121c's
``LaunchKit``, whose stand-in CLI captures the registry entry at the session's start; and W2-205's relaunch fixture,
where the relaunch is a real ``gov launch`` that runs to the recording stand-in CLI.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import w2_201_x7_support as x7
import w2_201_x_support as x
from w2_201_x7_support import base, rt

TK = "DAEO-x7fx"
KINDS = {"fix": x7.FIX_LINE, "chore": x7.CHORE_LINE}


@pytest.fixture()
def machine(tmp_path):
    made = x7.Machine(tmp_path / "w2-201-x7")
    try:
        yield made
    finally:
        made.cleanup()


def _one_spawn(machine, entry, session_id):
    """What holds on the base already: the pass relaunched the dead entry once, as ``launch <role> ...`` resuming its
    session with the resume text."""
    machine.home.run_pass()
    spawned = machine.spawned()
    assert len(spawned) == 1, f"the pass started {len(spawned)} relaunches of one dead entry, not one: {spawned}"
    argv = spawned[0]["argv"]
    before, after = x7.split(argv)
    assert before[:2] == ["launch", entry["role"]], f"the relaunch is not gov launch {entry['role']}: {argv}"
    assert after[:2] == ["--resume", session_id], f"the relaunch does not resume the session {session_id}: {argv}"
    assert any(rt.RESUME_PART in word for word in after[2:]), f"no resume text after --resume: {argv}"
    return before


def _root_is_repository(values, machine, argv):
    roots = values["--root"]
    assert len(roots) == 1 and Path(roots[0]).resolve() == machine.repository.resolve(), (
        f"the relaunch's --root is {roots}, not the entry's repository {machine.repository}: {argv}")


@pytest.mark.parametrize("role", [x7.WORKER, x7.LEAD])
@pytest.mark.parametrize("kind", ["fix", "chore"])
def test_x7_the_pass_relaunches_a_fix_or_chore_entry_as_the_same_kind(machine, role, kind):
    ticket = TK if kind == "fix" else x7.CHORE_LABEL
    entry, session_id = machine.died(role, ticket, kind=kind, kind_line=KINDS[kind])
    before = _one_spawn(machine, entry, session_id)
    left, values = x7.without_pairs(before, "--fix", "--chore", "--root")
    _root_is_repository(values, machine, before)
    flag, other = ("--fix", "--chore") if kind == "fix" else ("--chore", "--fix")
    assert values[flag] == [KINDS[kind]] and values[other] == [], (
        f"the {role}'s {kind} entry was relaunched without {flag} \"<its line>\" (or with {other}): {before}")
    want = ["launch", role, TK] if kind == "fix" else ["launch", role]
    assert left == want, f"the relaunch's words before -- are {left} (less the options), not {want}"
    if kind == "chore":
        assert x7.CHORE_LABEL not in before, f"the chore's label {x7.CHORE_LABEL} was passed as a ticket: {before}"


@pytest.mark.parametrize("role", [x7.WORKER, x7.LEAD])
@pytest.mark.parametrize("form", ["feature", "old-form"])
def test_x7_a_feature_entry_or_one_from_before_the_change_is_relaunched_as_today(machine, role, form):
    """Guard on the base: ``feature`` holds ``kind: feature`` and ``kind_line: null``; ``old-form`` neither key."""
    kind = {"kind": "feature", "kind_line": None} if form == "feature" else {}
    entry, session_id = machine.died(role, TK, **kind)
    before = _one_spawn(machine, entry, session_id)
    left, values = x7.without_pairs(before, "--root")
    _root_is_repository(values, machine, before)
    assert left == ["launch", role, TK], f"the {form} entry was not relaunched as today: {before}"


# -- the registry entry carries the kind ------------------------------------------------------------------------------

@pytest.fixture()
def kit(tmp_path):
    return base.LaunchKit(tmp_path / "w2-201-x7-kit", rubric=True)


def _entry_of(kit, *words):
    result = x.launch(kit.sandbox, kit.cli, *words)
    x.launched(result)
    seen = kit.registry_entries()
    assert len(seen) == 1 and isinstance(seen[0].get("entry"), dict), (
        f"the session's registry entry was not seen at its start: {seen}\n{result.describe()}")
    return seen[0]["entry"]


@pytest.mark.parametrize("role", [x.ENGINEER, "orchestrator"])
@pytest.mark.parametrize("kind", ["fix", "chore"])
def test_x7_a_fix_or_chore_launch_s_registry_entry_holds_its_kind_and_line(kit, role, kind):
    if kind == "fix":
        x.ticket(kit.project, x.ENGINEER, "C2", "closed", tk=TK)
        entry = _entry_of(kit, role, TK, "--fix", x7.FIX_LINE)
    else:
        entry = _entry_of(kit, role, "--chore", x7.CHORE_LINE)
    got = {key: entry.get(key, "<missing>") for key in ("kind", "kind_line")}
    assert got == {"kind": kind, "kind_line": KINDS[kind]}, f"the {role}'s {kind} registry entry holds {got}: {entry}"


def test_x7_a_feature_launch_s_registry_entry_holds_feature_or_neither_key(kit):
    """Guard on the base (neither key)."""
    entry = _entry_of(kit, x.ENGINEER, kit.ticket)
    got = {key: entry.get(key, "<missing>") for key in ("kind", "kind_line")}
    assert got in ({"kind": "feature", "kind_line": None}, {"kind": "<missing>", "kind_line": "<missing>"}), (
        f"a feature launch's registry entry holds {got}: {entry}")


# -- the relaunched fix, through gov launch on the stand-in CLI -------------------------------------------------------

def test_x7_a_relaunched_fix_launch_is_not_refused_and_records_kind_fix_and_the_same_line(tmp_path):
    """A real engineer session on an in_progress ticket; the ticket then closes; its dead entry, a fix's, is
    relaunched by the pass into ``gov launch``, which runs to the stand-in CLI."""
    rig = rt.Rig(tmp_path / "w2-201-x7-rig", x7.LEAD_ADDRESS)
    try:
        session_id = rig.session(TK)
        path = Path(rig.project) / ".tickets" / f"{TK}.md"
        text = path.read_text(encoding="utf-8")
        assert "status: in_progress\n" in text, "fixture: the ticket has no in_progress status line"
        path.write_text(text.replace("status: in_progress\n", "status: closed\n", 1), encoding="utf-8")
        rig.died(TK, session_id, kind="fix", kind_line=x7.FIX_LINE)
        rig.home.config(x7.ON)
        rig.home.run_pass()
        assert len(rig.home.events("relaunched")) == 1, f"the pass did not relaunch: {rig.home.events('relaunched')}"
        resumed = rig.resumed(wait_for=1)
        log = rig.home.runtime / "relaunch.log"
        said = log.read_text(encoding="utf-8", errors="replace")[-2000:] if log.is_file() else ""
        assert len(resumed) == 1, f"the relaunched fix launch did not start a session (refused?):\n{said}"
        args = resumed[0]["args"]
        new_id = args[args.index("--session-id") + 1]
        record = json.loads((Path(rig.kit.sandbox.records) / f"{new_id}.json").read_text(encoding="utf-8"))
        got = {key: record.get(key) for key in ("kind", "kind_line", "ticket", "resumes")}
        want = {"kind": "fix", "kind_line": x7.FIX_LINE, "ticket": TK, "resumes": session_id}
        assert got == want, f"the relaunched launch's record holds {got}, not {want}"
    finally:
        rig.cleanup()
