"""What the trailer gates judge (W2-01): the trailers base, the owner-accepted history (DEC-734), a merge with
nothing of its own (DEC-436's merge form) and a move of the base (W2-M266). Builder tests: regression evidence
only (MR-3)."""
from __future__ import annotations

import subprocess

import pytest

from gov.close import history

PATH_MAP = history.PATH_MAP_REL
REGISTER = "docs/DECISION_REGISTER.md"


def _register(repo, *entries):
    text = "# Decision register\n\n" + "".join(f"### {dec} — A decision\n- **Status:** {status}\n- **Decision:** {body}\n\n"
                                             for dec, status, body in entries)
    (repo.root / "docs").mkdir(exist_ok=True)
    (repo.root / REGISTER).write_text(text, encoding="utf-8")


def _entries(repo, commit, decision="DEC-900"):
    return {history.REGISTER_KEY: REGISTER, history.ACCEPTED_KEY: [{"commit": commit, "decision": decision}]}


def test_an_entry_the_owner_accepted_takes_its_commit_out_and_lists_it(repo):
    old = repo.commit("old work", "Task: T-0001")
    _register(repo, ("DEC-900", "ACCEPTED (owner, 2026-10-16)", f"commit `{old[:8]}` is history"))
    accepted, refused = history.accepted_history(repo.root, _entries(repo, old[:8]))
    assert accepted == {old: "DEC-900"} and refused == []


@pytest.mark.parametrize("status, body, words", [
    (None, "", "no entry"),
    ("PROPOSED", "commit `{c}`", "not accepted"),
    ("ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-16)", "commit `{c}`", "not the owner"),
    ("ACCEPTED (delegated, DEC-102; recorded by the orchestrator)", "commit `{c}`", "not the owner"),
    ("ACCEPTED (owner, 2026-10-16)", "commit `0000000a`", "does not name"),
    ("ACCEPTED (owner-delegated to the orchestrator)", "commit `{c}`", "not the owner"),
    ("ACCEPTED (owner's delegate, the orchestrator)", "commit `{c}`", "not the owner"),
    ("ACCEPTED (owner, 2026-10-16) · superseded by DEC-911", "commit `{c}`", "superseded"),
    ("ACCEPTED (owner, 2026-10-16); revoked by DEC-912", "commit `{c}`", "revoked"),
    ("ACCEPTED (owner, 2026-10-16)", "commit `{c}ffff0000`", "does not name"),  # inside a longer id
])
def test_any_other_entry_is_refused_and_says_why(repo, status, body, words):
    old = repo.commit("old work", "Task: T-0001")
    _register(repo, *([("DEC-900", status, body.format(c=old[:8]))] if status else [("DEC-111", "PROPOSED", "x")]))
    accepted, refused = history.accepted_history(repo.root, _entries(repo, old))
    assert accepted == {} and len(refused) == 1
    assert refused[0]["code"] == history.REFUSED and words in refused[0]["message"]
    assert old[:12] in refused[0]["message"] and "DEC-900" in refused[0]["message"]


def test_only_the_entrys_own_status_line_is_its_status(repo):
    old = repo.commit("old work", "Task: T-0001")
    (repo.root / "docs").mkdir(exist_ok=True)
    (repo.root / REGISTER).write_text(f"### DEC-900 — A decision\n> quoted: **Status:** ACCEPTED (owner, 2026-10-16)\n"
                                      f"- **Status:** PROPOSED\n- **Decision:** commit `{old[:8]}`\n", encoding="utf-8")
    accepted, refused = history.accepted_history(repo.root, _entries(repo, old))
    assert accepted == {} and "not accepted" in refused[0]["message"]


def test_an_entry_refuses_without_a_register_or_a_commit(repo):
    old = repo.commit("old work")
    _, refused = history.accepted_history(repo.root, {history.ACCEPTED_KEY: [{"commit": old, "decision": "DEC-900"}]})
    assert "names no decision register" in refused[0]["message"]
    _register(repo, ("DEC-900", "ACCEPTED (owner, 2026-10-16)", "commit `abcdef12`"))
    _, refused = history.accepted_history(repo.root, _entries(repo, "abcdef12"))
    assert "names no commit" in refused[0]["message"]


def test_the_base_must_be_a_commit_head_descends_from(repo):
    first = repo.commit("first")
    repo.commit("second")
    base, after = history.trailers_base(repo.root, {history.BASE_KEY: first[:8]})
    assert base == first and first not in after and len(after) == 1
    assert history.trailers_base(repo.root, {}) == (None, None)
    with pytest.raises(ValueError):
        history.trailers_base(repo.root, {history.BASE_KEY: "main"})


def test_a_merge_with_nothing_of_its_own_adds_nothing(repo):
    repo.commit("start", files={"a.txt": "a\n"})
    repo.git("checkout", "-q", "-b", "side")
    repo.commit("side", files={"b.txt": "b\n"})
    repo.git("checkout", "-q", "main")
    repo.commit("main", files={"c.txt": "c\n"})
    repo.git("merge", "-q", "--no-ff", "--no-edit", "side")
    assert history.adds_nothing(repo.root, repo.git("rev-parse", "HEAD").strip())
    assert not history.adds_nothing(repo.root, repo.git("rev-parse", "HEAD^1").strip())  # no merge
    repo.git("checkout", "-q", "-b", "side2", "side")
    repo.commit("side2", files={"d.txt": "d\n"})
    repo.git("checkout", "-q", "main")
    repo.git("merge", "-q", "--no-ff", "--no-commit", "side2")
    repo.commit("merge with its own change", files={"a.txt": "changed in the merge\n"})
    assert not history.adds_nothing(repo.root, repo.git("rev-parse", "HEAD").strip())


def _two_sides_of_one_file(repo, side_line, main_line):
    repo.commit("start", files={"f.txt": "a\nb\nc\nd\ne\n"})
    repo.git("checkout", "-q", "-b", "side")
    repo.commit("side", files={"f.txt": side_line})
    repo.git("checkout", "-q", "main")
    repo.commit("main", files={"f.txt": main_line})


def test_a_conflict_free_merge_of_one_file_both_sides_changed_adds_nothing(repo):
    _two_sides_of_one_file(repo, "A\nb\nc\nd\ne\n", "a\nb\nc\nd\nE\n")
    repo.git("merge", "-q", "--no-ff", "--no-edit", "side")
    assert history.adds_nothing(repo.root, repo.git("rev-parse", "HEAD").strip())


def test_a_merge_keeping_one_sides_whole_file_or_resolving_a_conflict_has_its_own_change(repo):
    _two_sides_of_one_file(repo, "A\nb\nc\nd\ne\n", "a\nb\nc\nd\nE\n")
    repo.git("merge", "-q", "--no-ff", "--no-commit", "-s", "ours", "side")
    repo.commit("merge keeping main's whole file")
    assert not history.adds_nothing(repo.root, repo.git("rev-parse", "HEAD").strip())
    repo.git("checkout", "-q", "-b", "conflict", "side")
    repo.commit("side again", files={"f.txt": "Z\nb\nc\nd\ne\n"})
    repo.git("checkout", "-q", "main")
    repo.commit("main again", files={"f.txt": "Y\nb\nc\nd\nE\n"})
    with pytest.raises(subprocess.CalledProcessError):  # the merge stops on the conflict
        repo.git("merge", "-q", "--no-ff", "--no-commit", "conflict")
    repo.git("checkout", "--ours", "--", "f.txt")
    repo.commit("conflict resolved to main's side")
    assert not history.adds_nothing(repo.root, repo.git("rev-parse", "HEAD").strip())


def test_a_move_of_the_base_is_reported_with_its_count(repo):
    repo.commit("the path map", files={PATH_MAP: "namespaces: {}\n"})
    old = repo.commit("old boundary")
    repo.commit("the base", files={PATH_MAP: f'namespaces: {{}}\ntrailers_base: "{old}"\n'})
    repo.commit("between")
    new = repo.commit("new boundary")
    assert history.base_move(repo.root, old) == {"from": None, "to": old, history.MOVED_COUNT: 2}
    repo.commit("the base moved", files={PATH_MAP: f'namespaces: {{}}\ntrailers_base: "{new[:8]}"\n'})
    assert history.base_move(repo.root, new) == {"from": old, "to": new, history.MOVED_COUNT: 3}
    assert history.base_move(repo.root, None) is None


def test_a_base_recorded_with_the_path_map_itself_is_no_move(repo):
    first = repo.commit("first")
    repo.commit("the path map", files={PATH_MAP: f'namespaces: {{}}\ntrailers_base: "{first}"\n'})
    assert history.base_move(repo.root, first) is None
