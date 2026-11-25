"""RR-4: ``Class: Q`` is dropped (plan 2-12; R-8 (b)). A patch needs ``Fix:`` (with a ``Task:`` ticket closed at N)
or ``Class: C``; ``Class: Q`` is a chore nowhere. The same range with ``Class: C`` answering ``patch`` is
``test_w2_209_rule.py::test_s1_a_range_of_fixes_and_chores_only_is_a_patch_and_writes_nothing``. README, "RR-4".
"""

import pytest

import w2_209_support as support


@pytest.mark.parametrize("name", ["q_src", "q_template"])
def test_rr4_a_class_q_commit_without_a_fix_is_not_a_patch_naming_the_commit(base, tmp_path, home, name):
    case = base.cases[name]
    repo = support.make_case(base, tmp_path / "repo", case, authority_on=False)
    before = support.snapshot(repo)
    run = support.release(repo, home.path, case.version, "--check")
    details = support.refusal(run)
    assert details.get("kind") == "bigger" and details.get("failed") == ["P3"], f"{name}: {details}"
    detail = details["rules"]["P3"]["detail"]
    assert case.named in detail, f"{name}: P3's detail does not name the commit {case.named}: {detail!r}"
    assert not support.difference(before, support.snapshot(repo)), "--check wrote something"


def test_rr4_the_cut_of_a_range_with_a_class_q_code_commit_is_refused_at_g1(base, tmp_path, home):
    case = base.cases["q_src"]
    repo = support.make_case(base, tmp_path / "repo", case)
    record = support.good_suite(repo, tmp_path / "records")
    logs = tmp_path / "logs"
    logs.mkdir()
    before = support.snapshot(repo)
    out = support.call(home.path, "gov.release:_patch_test", [support.path_arg(repo), case.version],
                       {"suite": support.path_arg(record),
                        "rehearse": support.standin("rehearse", log=str(logs / "rehearse.jsonl")),
                        "repin": support.standin("repin", log=str(logs / "repin.jsonl"))},
                       role="orchestrator")
    support.assert_gate(out.refused("Class: Q"), "G1", "a Class: Q code commit", rule="P3")
    assert not support.difference(before, support.snapshot(repo)), "a refused cut changed the repository"
    assert not support.read_jsonl(logs / "repin.jsonl"), "the re-pin ran"


def test_rr4_class_q_beside_a_fix_under_a_ticket_closed_at_n_rides_the_fix(base, tmp_path, home):
    """Pins that the ``Fix:`` carries the commit whatever its class (passes on the base)."""
    case = base.cases["q_fix"]
    repo = support.make_case(base, tmp_path / "repo", case, authority_on=False)
    envelope = support.release(repo, home.path, case.version, "--check").envelope()
    assert envelope.get("ok") is True and envelope["result"].get("kind") == "patch", envelope


def test_rr4_note_md_lists_class_c_chores_only(base, tmp_path, home):
    case = base.cases["q_docs"]
    repo = support.make_case(base, tmp_path / "repo", case)
    record = support.good_suite(repo, tmp_path / "records")
    logs = tmp_path / "logs"
    logs.mkdir()
    out = support.call(home.path, "gov.release:_patch_test", [support.path_arg(repo), case.version],
                       {"suite": support.path_arg(record),
                        "rehearse": support.standin("rehearse", log=str(logs / "rehearse.jsonl")),
                        "repin": support.standin("repin", log=str(logs / "repin.jsonl"))},
                       role="orchestrator")
    out.returned("the cut of a patch range with a Class: Q commit outside the code")
    note = support.show(repo, f"v{case.version}:{support.RELEASES_REL}/{case.version}/{support.NOTE}").decode("utf-8")
    assert support.CHORE_SUBJECT in note and "Revise a proposal" in note, f"NOTE.md lacks a Class: C chore:\n{note}"
    assert support.Q_DOCS_SUBJECT not in note, f"NOTE.md lists a Class: Q commit as a chore:\n{note}"
