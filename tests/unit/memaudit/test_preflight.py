"""S1, S5, F1: the pre-flight's ten checks on a planted set, counts only."""

from __future__ import annotations

import hashlib
import json

import pytest

from gov.memaudit import preflight

from .conftest import AUDIT, UNIQUE

CODES = list(preflight.CODES)


def codes_of(stdout: str) -> dict:
    return {line.split()[0]: line for line in stdout.splitlines() if line.startswith("PF-")}


def refused_only(stdout: str, code: str) -> bool:
    seen = codes_of(stdout)
    return seen[code].startswith(f"{code} refused") and all(
        seen[c] == f"{c} ok" for c in CODES if c != code)


def test_a_clean_set_ends_every_check_as_expected(plant):
    done = plant.cli(*plant.preflight_args())
    assert done.returncode == 0, done.stdout
    out = done.stdout.splitlines()
    assert out[-1] == "PRE-FLIGHT: every check as expected"
    assert [line.split()[0] for line in out[:-1]] == CODES
    doc = json.loads((plant.run_dir / "PREFLIGHT.json").read_text())
    assert doc["ok"] is True and doc["n"] == 40 and doc["selection"] == "file"
    assert oct(plant.run_dir.stat().st_mode & 0o777) == "0o700"
    assert done.stderr == ""


def test_fewer_than_36_files_is_pf_count(plant):
    for i in range(36, 41):
        (plant.hidden / f"q{i:02d}.yaml").unlink()
    done = plant.cli(*plant.preflight_args())
    assert done.returncode == 1
    assert codes_of(done.stdout)["PF-COUNT"] == "PF-COUNT refused 1"
    assert done.stdout.splitlines()[-1] == "PRE-FLIGHT: NOT as expected: stop, fix before any search"


def test_a_stray_entry_in_the_set_is_pf_count(plant):
    (plant.hidden / "notes.txt").write_text("x")
    done = plant.cli(*plant.preflight_args())
    assert refused_only(done.stdout, "PF-COUNT")


@pytest.mark.parametrize("change", ["missing_key", "extra_key", "wrong_id", "bad_lines", "bad_category"])
def test_a_file_out_of_form_is_pf_form(plant, change):
    q = dict(plant.questions["q05"])
    if change == "missing_key":
        del q["drawn"]
    elif change == "extra_key":
        q["note"] = "x"
    elif change == "wrong_id":
        q["id"] = "q99"
    elif change == "bad_lines":
        q["sources"] = [{"path": q["sources"][0]["path"], "lines": [5, 2]}]
    else:
        q["category"] = "other"
    plant.put(q, "q05.yaml")
    done = plant.cli(*plant.preflight_args())
    assert done.returncode == 1
    line = codes_of(done.stdout)["PF-FORM"]
    assert line == "PF-FORM refused 1 q05"


def test_a_form_refused_file_counts_in_n_only(plant):
    (plant.hidden / "q05.yaml").write_text("not: [valid")
    done = plant.cli(*plant.preflight_args())
    seen = codes_of(done.stdout)
    assert seen["PF-FORM"] == "PF-FORM refused 1 q05" and seen["PF-COUNT"] == "PF-COUNT ok"
    doc = json.loads((plant.run_dir / "PREFLIGHT.json").read_text())
    assert doc["n"] == 40 and doc["in_form"] == 39


def test_another_commit_is_pf_commit(plant):
    plant.put({**plant.questions["q03"], "commit": plant.repo["earlier"]})
    done = plant.cli(*plant.preflight_args())
    assert refused_only(done.stdout, "PF-COMMIT")
    assert codes_of(done.stdout)["PF-COMMIT"] == "PF-COMMIT refused 1 q03"


def test_a_category_off_its_quota_is_pf_quota_with_names_not_ids(plant):
    plant.put({**plant.questions["q01"], "category": "contract"})  # decision 5, contract 5
    done = plant.cli(*plant.preflight_args())
    assert refused_only(done.stdout, "PF-QUOTA")
    assert codes_of(done.stdout)["PF-QUOTA"] == "PF-QUOTA refused 2 decision 5 contract 5"


def test_quotas_with_fewer_than_40_read_as_at_most(plant):
    for i in (36, 37, 38):  # three multi-file and failure-memory questions gone, none over
        (plant.hidden / f"q{i:02d}.yaml").unlink()
    done = plant.cli(*plant.preflight_args())
    assert codes_of(done.stdout)["PF-QUOTA"] == "PF-QUOTA ok"


def test_a_thin_domain_is_pf_spread(plant):
    for qid in ("q03", "q08", "q13", "q18", "q23"):  # five plan questions moved to an operations file
        q = plant.questions[qid]
        plant.put({**q, "sources": [{"path": "README.md"}]})
    done = plant.cli(*plant.preflight_args())
    assert refused_only(done.stdout, "PF-SPREAD")
    assert codes_of(done.stdout)["PF-SPREAD"] == "PF-SPREAD refused 1 domain plan 3"


def test_a_heavy_subsystem_is_pf_spread(plant):
    for i in range(1, 12):
        q = plant.questions[f"q{i:02d}"]
        plant.put({**q, "sources": [{"path": "src/gov/close/c.py", "heading": f"## H{i:02d} of c"}]})
    done = plant.cli(*plant.preflight_args())
    assert "subsystem close 11" in codes_of(done.stdout)["PF-SPREAD"]


def test_a_drawn_question_outside_its_list_is_pf_drawn(plant):
    q1, q2 = plant.questions["q01"], plant.questions["q02"]
    plant.put({**q1, "drawn": "changed"})
    plant.put({**q2, "drawn": "sample"})
    plant.selection(changed=[q1["sources"][0]["path"]], sample=["README.md"])
    done = plant.cli(*plant.preflight_args())
    assert refused_only(done.stdout, "PF-DRAWN")
    assert codes_of(done.stdout)["PF-DRAWN"] == "PF-DRAWN refused 1 q02"


def _seed_line(seed, audit=AUDIT, **over):
    row = {"time": "t", "kind": "writer", "run": "r", "commit": "c", "seed": seed,
           "seed_sha256": hashlib.sha256(f"{seed}\n".encode()).hexdigest(), "set": audit, "round": 1, "dry": False}
    row.update(over)
    return json.dumps(row)


def test_the_lists_are_derived_by_the_launch_script_rule_when_no_selection(plant):
    (plant.set_dir / "selection.json").unlink()
    q1 = plant.questions["q01"]
    plant.put({**q1, "drawn": "changed"})  # docs/DECISION_REGISTER.md changed since the earlier commit
    (plant.runs / "indep/AUDITS.log").write_text(json.dumps({"commit": plant.repo["earlier"]}) + "\n")
    (plant.runs / "indep/SEEDS.log").write_text(_seed_line(7) + "\n" + _seed_line(8, round=2) + "\n")
    done = plant.cli(*plant.preflight_args())
    assert codes_of(done.stdout)["PF-DRAWN"] == "PF-DRAWN ok", done.stdout
    assert json.loads((plant.run_dir / "PREFLIGHT.json").read_text())["selection"] == "derived"
    lists = preflight.derive_lists(plant.repo["path"], plant.repo["head"], plant.runs, AUDIT)
    assert "README.md" not in lists["changed"]
    assert not any(p.startswith("docs/research/") for p in lists["changed"] + lists["sample"])


@pytest.mark.parametrize("seeds", ["", "two", "bad_hash"])
def test_lists_that_cannot_be_had_name_every_drawn_question(plant, seeds):
    (plant.set_dir / "selection.json").unlink()
    plant.put({**plant.questions["q01"], "drawn": "changed"})
    lines = {"": "", "two": _seed_line(7) + "\n" + _seed_line(9) + "\n",
             "bad_hash": _seed_line(7, seed_sha256="0" * 64) + "\n"}[seeds]
    (plant.runs / "indep/SEEDS.log").write_text(lines)
    done = plant.cli(*plant.preflight_args())
    assert codes_of(done.stdout)["PF-DRAWN"] == "PF-DRAWN refused 1 q01"


def test_a_missing_source_or_a_lost_anchor_is_pf_source(plant):
    q4, q6 = plant.questions["q04"], plant.questions["q06"]
    plant.put({**q4, "sources": [{"path": "docs/contract/gone.md", "lines": [1, 2]}]})
    plant.put({**q6, "sources": [{"path": "docs/DECISION_REGISTER.md", "heading": "## not there",
                                  "lines": [1, 900]}]})
    done = plant.cli(*plant.preflight_args())
    assert codes_of(done.stdout)["PF-SOURCE"] == "PF-SOURCE refused 2 q04 q06"


def test_a_heading_not_found_with_lines_inside_is_re_anchored_not_refused(plant):
    q = plant.questions["q06"]
    plant.put({**q, "sources": [{"path": "docs/DECISION_REGISTER.md", "heading": "## not there", "lines": [1, 3]}]})
    done = plant.cli(*plant.preflight_args())
    assert done.returncode == 0
    assert json.loads((plant.run_dir / "PREFLIGHT.json").read_text())["re_anchored"] == 1


def test_a_source_in_an_evaluation_namespace_is_pf_evalns(plant):
    q = plant.questions["q09"]
    alt = [{"path": "docs/research/memory-measure-audit/q.md", "heading": "## H01 of q"}, q["sources"][0]]
    plant.put({**q, "sources": [q["sources"][0], alt]})
    done = plant.cli(*plant.preflight_args())
    assert refused_only(done.stdout, "PF-EVALNS")
    assert codes_of(done.stdout)["PF-EVALNS"] == "PF-EVALNS refused 1 q09"


def test_a_gold_source_set_equal_to_a_pool_question_is_pf_duppool(plant):
    import yaml
    q = plant.questions["q11"]
    pool = {**q, "id": "q01"}
    (plant.root / "fixtures/evaluation/memory-pool/hidden/memory-audit-20261104-q01.yaml").write_text(
        yaml.safe_dump(pool))
    done = plant.cli(*plant.preflight_args())
    assert refused_only(done.stdout, "PF-DUPPOOL")
    assert codes_of(done.stdout)["PF-DUPPOOL"] == "PF-DUPPOOL refused 1 q11"


def test_a_nonexistent_id_that_exists_is_pf_idexists(plant):
    plant.put({**plant.questions["q40"], "question": "Which record is KNOWN-77 about?"})
    done = plant.cli(*plant.preflight_args())
    assert refused_only(done.stdout, "PF-IDEXISTS")
    assert codes_of(done.stdout)["PF-IDEXISTS"] == "PF-IDEXISTS refused 1 q40"


def test_a_nonexistent_id_question_with_no_token_is_counted_not_refused(plant):
    plant.put({**plant.questions["q40"], "question": "Which ticket is about nothing at all?"})
    done = plant.cli(*plant.preflight_args())
    assert done.returncode == 0
    assert json.loads((plant.run_dir / "PREFLIGHT.json").read_text())["no_token"] == 1


def test_an_id_held_only_inside_a_longer_token_does_not_exist(plant):
    plant.put({**plant.questions["q40"], "question": "Which record is KNOWN-7 about?"})
    assert plant.cli(*plant.preflight_args()).returncode == 0


def test_a_path_map_unreadable_at_the_commit_is_error_exit_4(plant, repo, tmp_path):
    import shutil
    import subprocess
    broken = tmp_path / "broken"
    shutil.copytree(repo["path"], broken)
    (broken / "governance/project/path-map.yaml").write_text("namespaces: [unclosed\n")
    subprocess.run(["git", "commit", "-q", "-am", "broken map"], cwd=broken, env=repo["env"], check=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=broken, capture_output=True, text=True).stdout.strip()
    for i in range(1, 41):
        plant.put({**plant.questions[f"q{i:02d}"], "commit": head})
    args = plant.preflight_args(head)
    args[args.index("--repo") + 1] = str(broken)
    done = plant.cli(*args)
    assert done.returncode == 4
    assert done.stdout == "ERROR: YAMLError\n" or done.stdout.startswith("ERROR: ")
    assert done.stdout.strip() == done.stderr.strip()
    assert not (plant.run_dir / "PREFLIGHT.json").exists()


def test_with_used_present_preflight_writes_nothing_and_exits_3(plant):
    plant.run_dir.mkdir(parents=True)
    (plant.run_dir / "USED").write_text("x\n")
    done = plant.cli(*plant.preflight_args())
    assert done.returncode == 3 and done.stdout == "USED\n"
    assert sorted(p.name for p in plant.run_dir.iterdir()) == ["USED"]


def test_no_question_text_gold_answer_path_or_heading_leaves_the_tool(plant):
    q = plant.questions["q03"]
    plant.put({**q, "question": f"What is the {UNIQUE['question']} rule?", "gold_answer": f"The {UNIQUE['gold']}.",
               "sources": [{"path": UNIQUE["path"], "heading": UNIQUE["heading"]}], "commit": "f" * 40})
    plant.put({**plant.questions["q04"], "sources": [{"path": "docs/plan/nowhere-" + UNIQUE["question"] + ".md"}]})
    done = plant.cli(*plant.preflight_args())
    assert done.returncode == 1
    texts = [done.stdout, done.stderr] + [p.read_text() for p in plant.run_dir.iterdir()]
    for word in (UNIQUE["question"], UNIQUE["gold"], "fjordnarwhal", "quillbadger", "docs/"):
        assert all(word not in t for t in texts), word
    for t in (done.stdout, done.stderr):
        assert "fixtures/" not in t and "runs/" not in t and str(plant.root) not in t
