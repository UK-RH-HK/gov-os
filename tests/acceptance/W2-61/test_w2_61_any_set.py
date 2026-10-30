"""W2-61, KPI success 6 -- the same measure for any declared set, by name.

"The same split for EXAMIN's set, written by a session independent of the adopting team before W2-27; EXP-003's
gold answers (W2-15a, W2-15b) split the same way [DEC-828 item 3]".

Writing those real sets is other sessions' work. What this ticket owes is a measure that takes any set the path
map's ``evaluation_sets`` block declares, by its name: here a second planted set, ``planted-second``, beside
``planted-memory``; a name the block does not declare is refused, naming it, before any retrieval. And the measured
repository need not hold the sets: ``--sets-root`` names the repository whose path map declares the set and which
holds its question files, while ``--root`` is the repository whose stores answer (the baseline measures a clone at
a fixed commit with question files from this worktree).

Red now: ``gov.retrieval.measure`` does not exist.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_61_support as s  # noqa: E402

SECOND_QUESTION = "What does the second set ask about the audit lines?"


def _plant_second(world, repo=None):
    world.question("x01", {"question": SECOND_QUESTION, "gold_answer": "two lines",
                           "sources": [{"path": s.DECISIONS, "heading": "## DEC-5 The audit lines"}]},
                   [[world.section(s.DECISIONS, "## DEC-5 The audit lines")]], set_name=s.SECOND, repo=repo)


@pytest.fixture
def world(tmp_path):
    w = s.make_world(tmp_path, commit=False)
    s.standard_questions(w)
    _plant_second(w)
    w.commit()
    return w


def test_a_second_declared_set_is_measured_by_its_name(world):
    document = world.measure(s.SECOND, "--json").json()
    assert document.get("set") == s.SECOND, f"set: {document.get('set')!r}"
    assert [q.get("id") for q in s.questions(document)] == ["x01"], "the second set's questions are not measured"
    got = s.question(document, "x01")
    assert (got.get("hit_at_5"), got.get("full_evidence")) == (True, True), f"x01: {got}"
    total = document.get("total") or {}
    assert (total.get("hit_at_5") or {}).get("count") == 1 and (total.get("full_evidence") or {}).get("count") == 1
    queries = [s.options(call["argv"])["query"] for call in world.calls()]
    assert queries == [[SECOND_QUESTION]], f"the second set's run retrieved other questions: {queries}"


def test_the_first_set_is_measured_by_its_name_beside_it(world):
    document = world.measure(s.SET, "--json").json()
    assert document.get("set") == s.SET
    assert [q.get("id") for q in s.questions(document)] == ["v01", "v02", "v03", "v04"]


@pytest.mark.parametrize("name", ["planted-absent", "memory-retrieval"])
def test_an_undeclared_set_is_refused_by_name(world, name):
    run = world.measure(name, "--json")
    assert run.returncode != 0, f"the undeclared set {name} was measured\n{run.describe()}"
    assert name in run.output, f"the refusal does not name {name}\n{run.describe()}"
    assert not world.calls(), f"an undeclared set was retrieved: {world.calls()}"


def test_a_path_map_without_an_evaluation_sets_block_declares_no_set(tmp_path):
    world = s.make_world(tmp_path, commit=False)
    s.standard_questions(world)
    world.write(s.PATH_MAP_REL, s.path_map_text(block={}))
    world.commit()
    run = world.measure(s.SET)
    assert run.returncode != 0 and s.SET in run.output, f"a set no block declares was measured\n{run.describe()}"


def test_the_sets_root_holds_the_sets_and_the_root_answers(tmp_path):
    """The measured clone has the documents but no question files and no evaluation_sets block; the sets
    repository has the path map and the questions. Sources are resolved in the measured root."""
    world = s.make_world(tmp_path / "w", commit=False)
    world.write(s.PATH_MAP_REL, s.path_map_text(block={}))
    measured_head = world.commit()
    sets_root = s.make_plain_repo(tmp_path / "sets", {s.PATH_MAP_REL: s.path_map_text(),
                                                      "README.md": "# The sets\n"})
    s.standard_questions(world)  # writes the canned answers; the files land in the measured root, moved below
    for path in sorted((world.repo / "fixtures/evaluation" / s.SET).rglob("*.yaml")):
        rel = path.relative_to(world.repo)
        s.write(sets_root / rel, path.read_text(encoding="utf-8"))
        path.unlink()
    s.git(sets_root, "add", "-A")
    s.git(sets_root, "commit", "-q", "-m", "W2-61 fixture: the questions")
    assert world.head() == measured_head and not s.git(world.repo, "status", "--porcelain").strip()
    document = world.measure(s.SET, "--sets-root", sets_root, "--json").json()
    assert Path(str(document.get("root"))).resolve() == world.repo, f"root: {document.get('root')!r}"
    commit = str(document.get("commit") or "")
    assert len(commit) >= 12 and measured_head.startswith(commit), (
        f"commit {commit!r} is not the measured root's HEAD {measured_head}")
    assert [q.get("id") for q in s.questions(document)] == ["v01", "v02", "v03", "v04"]
    total = document.get("total") or {}
    assert (total.get("hit_at_5") or {}).get("count") == 2 and (total.get("full_evidence") or {}).get("count") == 3, (
        f"total: {total}")
    assert {call["cwd"] for call in world.calls()} == {str(world.repo)}, (
        f"the retrieval did not run in the measured root: {sorted({c['cwd'] for c in world.calls()})}")
