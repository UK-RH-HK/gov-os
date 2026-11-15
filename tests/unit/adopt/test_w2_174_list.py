"""W2-174 S1: ``gov adopt --verify-list`` names, per open or in-progress ticket, the KPI lines with no verify."""
from __future__ import annotations

from .test_w2_174_support import DONE, REPO, gov, gov_json, repo_with, snapshot, ticket  # noqa: F401

from gov.adopt import verify_pass


def three(tmp_path):
    return repo_with(tmp_path, {
        "DAEO-aa11": ticket("DAEO-aa11", "open", success=[DONE, DONE], failure=[DONE]),
        "DAEO-bb22": ticket("DAEO-bb22", "in_progress", success=["plain line one", DONE], failure=["'quoted failure line'"]),
        "DAEO-cc33": ticket("DAEO-cc33", "closed", success=["a closed ticket's line with no verify"]),
    })


def test_list_gives_exactly_the_second_tickets_two_labels(tmp_path):
    root = three(tmp_path)
    before = snapshot(root)
    code, envelope, _ = gov_json("adopt", "--verify-list", "--root", str(root))
    assert code == 0
    assert envelope["result"]["missing"] == [{"ticket": "DAEO-bb22", "labels": ["S1", "F1"], "fields": []}]
    assert envelope["result"]["text"] == "DAEO-bb22 S1 F1"
    assert verify_pass.missing(root) == [{"ticket": "DAEO-bb22", "labels": ["S1", "F1"], "fields": []}]
    assert snapshot(root) == before


def test_list_of_an_all_verified_repository_prints_none_and_exits_0(tmp_path):
    root = repo_with(tmp_path, {"DAEO-aa11": ticket("DAEO-aa11", success=[DONE, DONE], failure=[DONE]),
                                "DAEO-cc33": ticket("DAEO-cc33", "closed", success=["no verify, but closed"])})
    code, envelope, _ = gov_json("adopt", "--verify-list", "--root", str(root))
    assert code == 0
    assert envelope["result"] == {"missing": [], "text": "none"}


def test_list_is_sorted_by_id_and_a_line_with_verify_text_in_it_counts_as_verified(tmp_path):
    root = repo_with(tmp_path, {
        "DAEO-zz99": ticket("DAEO-zz99", success=["one line"]),
        "DAEO-mm55": ticket("DAEO-mm55", success=["'a line Verify: with its own clause'", "next line", "{line: x, verify: ''}"]),
        "DAEO-kk00": ticket("DAEO-kk00", "open", success=["'Verify:'"]),
    })
    found = verify_pass.missing(root)
    assert [item["ticket"] for item in found] == ["DAEO-kk00", "DAEO-mm55", "DAEO-zz99"]
    assert found[1]["labels"] == ["S2", "S3"]  # a mapping with an empty verify lacks one, as kpi_rows reads it
    code, out, _ = gov("adopt", "--verify-list", "--root", str(root))
    assert code == 0 and '"text": "DAEO-kk00 S1\\nDAEO-mm55 S2 S3\\nDAEO-zz99 S1"' in out


def test_list_without_a_tickets_folder_is_none(tmp_path):
    (tmp_path / "bare").mkdir()
    code, envelope, _ = gov_json("adopt", "--verify-list", "--root", str(tmp_path / "bare"))
    assert code == 0 and envelope["result"] == {"missing": [], "text": "none"}


def test_the_flags_go_alone(tmp_path):
    root = three(tmp_path)
    for argv in (("--verify-list", "--facts"), ("--verify-list", "--lite", "--stage", "A0")):
        code, _, err = gov("adopt", *argv, "--root", str(root))
        assert code == 2 and "goes alone" in err
