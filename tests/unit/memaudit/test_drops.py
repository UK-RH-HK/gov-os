"""S2, F4: the drop and void rule after the checker's last pass."""

from __future__ import annotations

import json

from gov.memaudit import drops, ledger


def drops_doc(plant):
    return json.loads((plant.run_dir / "DROPS.json").read_text())


def test_three_drops_go_on_with_37_kept_and_the_scales_recomputed(plant):
    plant.notes({"q01": "revise", "q02": "reject", "q03": None})
    done = plant.cli(*plant.void_args())
    assert done.returncode == 0, done.stdout
    assert done.stdout.splitlines()[-1] == "DROPS: kept 37 dropped 3"
    assert sorted(p.name for p in (plant.hidden / "dropped").iterdir()) == ["q01.yaml", "q02.yaml", "q03.yaml"]
    doc = drops_doc(plant)
    assert doc["kept"] == 37 and doc["dropped"] == 3 and doc["void"] is None and doc["notes_round"] == 2
    assert doc["by_code"] == {"NOLINE": 1, "R6-SPAN-MISSES": 2}
    assert doc["domains"]["decisions"] == 7 and doc["domains"]["tickets"] == 7 and doc["domains"]["plan"] == 7
    assert doc["domain_min"] == 4 and doc["subsystem_max"] == 9
    assert [e["event"] for e in ledger.read(plant.run_dir)] == ["drop"]


def test_five_drops_void_the_audit_with_no_used_and_no_declaration(plant):
    plant.notes({f"q{i:02d}": "reject" for i in (1, 2, 3, 4, 5)})
    done = plant.cli(*plant.void_args())
    assert done.returncode == 2
    assert done.stdout.splitlines()[-1] == "VOID VOID-COUNT kept 35 dropped 5"
    assert len(list((plant.hidden / "dropped").iterdir())) == 5
    assert drops_doc(plant)["void"] == "VOID-COUNT"
    assert not (plant.run_dir / "USED").exists() and not (plant.run_dir / "DECLARATION.json").exists()
    assert [e["event"] for e in ledger.read(plant.run_dir)] == ["drop", "void"]
    # and declare refuses a void audit
    assert plant.cli(*plant.declare_args()).returncode == 1


def test_a_drop_that_leaves_a_domain_at_three_is_void_domain(plant):
    # plan holds q03 q08 ... q38 (8): one moved to an operations file, four dropped: plan 3 of 36 kept
    plant.put({**plant.questions["q03"], "sources": [{"path": "README.md"}]})
    plant.notes({"q08": "revise", "q13": "revise", "q18": "reject", "q23": "reject"})
    done = plant.cli(*plant.void_args())
    assert done.returncode == 2
    assert "VOID VOID-DOMAIN kept 36 dropped 4" in done.stdout
    assert "domain plan 3 under 4" in done.stdout


def test_a_line_that_does_not_fit_is_dropped_as_unfit(plant):
    rows = [f"q{i:02d} | accept | - | also: none | fine" for i in range(2, 41)]
    plant.notes(text="## Questions\nq01 accept\n" + "\n".join(rows) + "\n")
    done = plant.cli(*plant.void_args())
    assert done.returncode == 0
    assert drops_doc(plant)["by_code"] == {"UNFIT": 1}


def test_no_notes_or_no_questions_section_is_dr_notes_and_nothing_moves(plant):
    done = plant.cli(*plant.void_args())
    assert done.returncode == 1 and done.stdout == "DR-NOTES\n"
    plant.notes(text="# Cross-check notes\n## The set\n")
    done = plant.cli(*plant.void_args())
    assert done.returncode == 1 and done.stdout == "DR-NOTES\n"
    assert not (plant.hidden / "dropped").exists()
    assert not (plant.run_dir / "DROPS.json").exists()


def test_the_highest_round_of_notes_is_read(plant):
    plant.notes({"q01": "reject", "q02": "reject", "q03": "reject", "q04": "reject", "q05": "reject"}, rnd=1)
    plant.notes({"q01": "revise"}, rnd=2)
    done = plant.cli(*plant.void_args())
    assert done.returncode == 0 and drops_doc(plant)["kept"] == 39


def test_a_second_void_is_dr_done(plant):
    plant.notes()
    assert plant.cli(*plant.void_args()).returncode == 0
    done = plant.cli(*plant.void_args())
    assert done.returncode == 1 and done.stdout == "DR-DONE\n"


def test_a_subsystem_over_its_max_after_drops_is_recorded_not_void(plant):
    for i in range(1, 11):
        q = plant.questions[f"q{i:02d}"]
        plant.put({**q, "sources": [{"path": "src/gov/close/c.py", "heading": f"## H{i:02d} of c"}]})
    plant.notes({"q40": "reject"})
    done = plant.cli(*plant.void_args())
    assert done.returncode == 0
    assert drops_doc(plant)["subsystem_over"] == ["close"]
    assert "subsystem close 10 over 9" in done.stdout


def test_a_dropped_file_already_in_dropped_is_never_overwritten(plant):
    (plant.hidden / "dropped").mkdir()
    (plant.hidden / "dropped/q01.yaml").write_text("earlier\n")
    plant.notes({"q01": "reject"})
    done = plant.cli(*plant.void_args())
    assert done.returncode == 4 and done.stdout == "ERROR: FileExistsError\n"
    assert (plant.hidden / "dropped/q01.yaml").read_text() == "earlier\n"
    assert (plant.hidden / "q01.yaml").exists()


def test_read_notes_splits_the_checker_form():
    rows = drops.read_notes("x\n## Questions\nq01 | accept | - | also: a#b | s | with a bar\n\n## The set\nq02 | x\n")
    assert list(rows) == ["q01"] and rows["q01"][0][4] == "s | with a bar"
    assert drops.verdict(rows["q01"]) == (True, [])
    assert drops.verdict(None) == (False, ["NOLINE"])
    assert drops.verdict([["q01", "revise", "-", "also: none", "s"]]) == (False, ["UNFIT"])
    assert drops.verdict([["q01", "reject", "R1-WRONG, R8-EVAL", "also: none", "s"]]) == (False, ["R1-WRONG", "R8-EVAL"])
