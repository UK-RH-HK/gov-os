"""W2-61, KPI success 2 and failure 1 -- the hidden half is refused to the roles the set measures.

KPI 2: "A hidden measurement half ... stored under fixtures/evaluation/memory-retrieval/hidden/, where the path
map's evaluation_sets block (memory-retrieval) refuses it to the measured roles [DEC-828 item 3, DEC-820 (d),
DEC-845 item 2]". Failure 1: "A measured role can read the hidden half by a route an honest agent takes in
ordinary work."

Two refusals, on a planted set (``planted-memory``, measured: the roles engineer and research, and the tickets
DAEO-zz61 and W2-195) in a temporary repository, never the real hidden half:

- **the guard** (W2-58's (d), driven as W2-58's tests drive it): a session of a measured role is refused the
  planted hidden part by the Read tool, Grep and Glob over its folder, and a Bash ``cat``, ``head`` and ``grep``;
  an unmeasured role reads it. These cases test W2-58's merged guard and may already hold before W2-61's code;
- **the measure**: a session the set measures (by role, by ticket id, by WBS id) is refused ``--part hidden`` and
  ``--part all`` with a non-zero exit naming the set, before any hidden question is retrieved, and nothing
  hidden is shown; the same session measures the visible part. Red now: the measure does not exist.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_61_support as s  # noqa: E402

HIDDEN_DIR = f"fixtures/evaluation/{s.SET}/hidden"
HIDDEN_FILE = f"{HIDDEN_DIR}/h01.yaml"


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    w = s.make_world(tmp_path_factory.mktemp("w2-61-refused"), commit=False)
    s.standard_questions(w)
    s.hidden_questions(w)
    w.commit()
    return w


def _honest_routes(world):
    return {
        "Read-file": s.read_call(world.repo / HIDDEN_FILE),
        "Grep-folder": s.grep_call(world.repo / HIDDEN_DIR),
        "Grep-file": s.grep_call(world.repo / HIDDEN_FILE),
        "Glob-pattern": s.glob_call(f"{HIDDEN_DIR}/*"),
        "Glob-in-folder": s.glob_call("*", world.repo / HIDDEN_DIR),
        "cat": s.bash_call(f"cat {HIDDEN_FILE}"),
        "head": s.bash_call(f"head -n 3 {HIDDEN_FILE}"),
        "grep-file": s.bash_call(f"grep -n question {HIDDEN_FILE}"),
        "grep-r-folder": s.bash_call(f"grep -rn question {HIDDEN_DIR}/"),
        "grep-r-evaluation": s.bash_call("grep -rn question fixtures/evaluation/"),
    }


ROUTES = ("Read-file", "Grep-folder", "Grep-file", "Glob-pattern", "Glob-in-folder", "cat", "head", "grep-file",
          "grep-r-folder", "grep-r-evaluation")
MEASURED = {"engineer": ("engineer", s.OTHER_TICKET), "research": ("research", "DAEO-zz63"),
            "ticket-lead-of-a-measured-ticket": ("orchestrator", s.MEASURED_TICKET)}


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("session", sorted(MEASURED))
def test_the_guard_refuses_a_measured_session_the_planted_hidden_part(world, session, route):
    role, ticket = MEASURED[session]
    call = _honest_routes(world)[route]
    decision, reason = s.ask_guard(world, call, role, ticket)
    assert decision == "deny" and reason, f"{session}: {call} was not refused: {decision} {reason[:300]!r}"


@pytest.mark.parametrize("role,ticket", [("orchestrator", s.OTHER_TICKET), ("product-spec", "DAEO-zz64")])
def test_the_guard_lets_an_unmeasured_session_read_the_planted_hidden_part(world, role, ticket):
    for call in (s.read_call(world.repo / HIDDEN_FILE), s.bash_call(f"cat {HIDDEN_FILE}")):
        decision, reason = s.ask_guard(world, call, role, ticket)
        assert decision == "allow", f"{role}: {call} was not allowed: {decision} {reason[:300]!r}"


# --------------------------------------------------------------------------
# The measure refuses the hidden part to a measured session
# --------------------------------------------------------------------------

MEASURED_SESSIONS = {
    "role-engineer": ("engineer", s.OTHER_TICKET),
    "role-research": ("research", "DAEO-zz63"),
    "ticket-id": ("orchestrator", s.MEASURED_TICKET),
    "ticket-by-its-wbs-id": ("orchestrator", s.MEASURED_WBS_TICKET),
    "wbs-id-as-ticket": ("orchestrator", s.MEASURED_WBS),
}


@pytest.mark.parametrize("part", ["hidden", "all"])
@pytest.mark.parametrize("session", sorted(MEASURED_SESSIONS))
def test_the_measure_refuses_the_hidden_part_to_a_measured_session(tmp_path, session, part):
    world = s.make_world(tmp_path, commit=False)
    s.standard_questions(world)
    s.hidden_questions(world)
    world.commit()
    role, ticket = MEASURED_SESSIONS[session]
    before = world.snapshot()
    run = world.measure(s.SET, "--part", part, "--json", role=role, ticket=ticket)
    assert run.returncode != 0, f"{session}: the measure did not refuse --part {part}\n{run.describe()}"
    assert s.SET in run.output, f"{session}: the refusal does not name the set\n{run.describe()}"
    retrieved = [c["argv"] for c in world.calls()]
    hidden_calls = [argv for argv in retrieved if any(s.HIDDEN_QUESTION in word for word in argv)]
    assert not hidden_calls, f"{session}: a hidden question was retrieved before the refusal: {hidden_calls}"
    for word in s.HIDDEN_WORDS:
        assert word not in run.output, f"{session}: the refusal shows {word}\n{run.describe()}"
    for path in world.written_since(before):
        assert b"zqxw61hidden" not in path.read_bytes(), f"{session}: {path} holds a hidden word"


def test_a_measured_session_measures_the_visible_part(tmp_path):
    world = s.make_world(tmp_path, commit=False)
    s.standard_questions(world)
    s.hidden_questions(world)
    world.commit()
    run = world.measure(s.SET, "--json", role="engineer", ticket=s.MEASURED_TICKET)
    document = run.json()
    assert document.get("part") == "visible", f"the default part is not visible: {document.get('part')!r}"
    assert [q.get("id") for q in s.questions(document)] == ["v01", "v02", "v03", "v04"]


def test_a_hidden_folder_the_set_s_hidden_globs_do_not_cover_is_refused(tmp_path):
    """Fail closed: planted-uncovered declares ``elsewhere/hidden/**``, but its questions lie under
    ``fixtures/evaluation/planted-uncovered/hidden/``, where the guard would not refuse them."""
    world = s.make_world(tmp_path, commit=False)
    s.hidden_questions(world, set_name=s.UNCOVERED)
    world.commit()
    run = world.measure(s.UNCOVERED, "--part", "hidden", role="orchestrator")
    assert run.returncode != 0, f"a hidden part outside the set's hidden globs was measured\n{run.describe()}"
    assert s.UNCOVERED in run.output, f"the refusal does not name the set\n{run.describe()}"
    assert not world.calls(), f"the uncovered hidden part was retrieved: {world.calls()}"
    for word in s.HIDDEN_WORDS:
        assert word not in run.output, f"the refusal shows {word}\n{run.describe()}"
