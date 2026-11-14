"""W2-174 S1: ``gov adopt --verify-list`` names, per open or in-progress ticket, the KPI lines with no verify."""
from __future__ import annotations

from .test_w2_174_support import DONE, REPO, gov, gov_json, repo_with, snapshot, ticket  # noqa: F401

from gov.adopt import verify_pass


def three(tmp_path):
    return repo_with(tmp_path, {
        "DAEO-a1": ticket("DAEO-a1", "open", success=[DONE, DONE], failure=[DONE]),
        "DAEO-b2": ticket("DAEO-b2", "in_progress", success=["plain line one", DONE], failure=["'quoted failure line'"]),
        "DAEO-c3": ticket("DAEO-c3", "closed", success=["a closed ticket's line with no verify"]),
    })


def test_list_gives_exactly_the_second_tickets_two_labels(tmp_path):
    root = three(tmp_path)
    before = snapshot(root)
    code, envelope, _ = gov_json("adopt", "--verify-list", "--root", str(root))
    assert code == 0
    assert envelope["result"]["missing"] == [{"ticket": "DAEO-b2", "labels": ["S1", "F1"]}]
    assert envelope["result"]["text"] == "DAEO-b2 S1 F1"
    assert verify_pass.missing(root) == [{"ticket": "DAEO-b2", "labels": ["S1", "F1"]}]
    assert snapshot(root) == before


def test_list_of_an_all_verified_repository_prints_none_and_exits_0(tmp_path):
    root = repo_with(tmp_path, {"DAEO-a1": ticket("DAEO-a1", success=[DONE, DONE], failure=[DONE]),
                                "DAEO-c3": ticket("DAEO-c3", "closed", success=["no verify, but closed"])})
    code, envelope, _ = gov_json("adopt", "--verify-list", "--root", str(root))
    assert code == 0
    assert envelope["result"] == {"missing": [], "text": "none"}


def test_list_is_sorted_by_id_and_a_line_with_verify_text_in_it_counts_as_verified(tmp_path):
    root = repo_with(tmp_path, {
        "DAEO-z9": ticket("DAEO-z9", success=["one line"]),
        "DAEO-m5": ticket("DAEO-m5", success=["'a line Verify: with its own clause'", "next line", "{line: x, verify: ''}"]),
        "DAEO-k0": ticket("DAEO-k0", "open", success=["'Verify:'"]),
    })
    found = verify_pass.missing(root)
    assert [item["ticket"] for item in found] == ["DAEO-k0", "DAEO-m5", "DAEO-z9"]
    assert found[1]["labels"] == ["S2", "S3"]  # a mapping with an empty verify lacks one, as kpi_rows reads it
    code, out, _ = gov("adopt", "--verify-list", "--root", str(root))
    assert code == 0 and '"text": "DAEO-k0 S1\\nDAEO-m5 S2 S3\\nDAEO-z9 S1"' in out


def test_list_without_a_tickets_folder_is_none(tmp_path):
    (tmp_path / "bare").mkdir()
    code, envelope, _ = gov_json("adopt", "--verify-list", "--root", str(tmp_path / "bare"))
    assert code == 0 and envelope["result"] == {"missing": [], "text": "none"}


def test_the_flags_go_alone(tmp_path):
    root = three(tmp_path)
    for argv in (("--verify-list", "--facts"), ("--verify-list", "--lite", "--stage", "A0")):
        code, _, err = gov("adopt", *argv, "--root", str(root))
        assert code == 2 and "goes alone" in err
