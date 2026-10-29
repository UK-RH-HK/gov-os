"""Builder tests of ``gov.retrieval.measure`` (W2-61): a planted ``gov`` and a planted set in ``tmp_path``; no store,
no embedder, no network, never the real hidden half."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest
import yaml

from gov.retrieval import measure

GOV = """#!{python}
import json, pathlib, sys
here = pathlib.Path(__file__).parent
args = sys.argv[1:]
if args == ["--version"]:
    print("gov 0.0 (commit planted)")
    sys.exit(0)
with open(here / "calls.log", "a") as log:
    log.write(json.dumps(args) + "\\n")
batches = json.loads((here / "plan.json").read_text())[args[-2]]
n = int(args[args.index("--continue") + 1]) if "--continue" in args else 0
more = str(n + 1) if n + 1 < len(batches) else None
print(json.dumps({{"ok": True, "result": {{"evidence": batches[n], "continuation": more}}}}))
"""

PATH_MAP = {"evaluation_sets": {"s": {"visible": ["docs/report.md"], "hidden": ["fixtures/evaluation/s/hidden/**"],
                                      "measures": {"roles": ["engineer"], "tickets": ["W9-01"]}}}}


def item(path, first, last, text="x" * 40):
    return {"path": path, "start_line": first, "end_line": last, "text": text}


@pytest.fixture
def planted(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / "governance/project").mkdir(parents=True)
    (repo / "governance/project/path-map.yaml").write_text(yaml.safe_dump(PATH_MAP))
    (repo / "docs").mkdir()
    (repo / "docs/report.md").write_text("quote\n")
    (repo / "docs/a.md").write_text("intro\n# A\nbody\n## A.1\nmore\n# B\nend\n")
    (repo / "src.py").write_text("\n".join(f"line {n}" for n in range(1, 21)) + "\n")
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "planted"], check=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gov = bin_dir / "gov"
    gov.write_text(GOV.format(python=sys.executable))
    gov.chmod(0o755)
    monkeypatch.setenv("GOV_ROLE", "orchestrator")
    monkeypatch.delenv("GOV_TICKET", raising=False)

    def ask(part, name, plan, **question):
        folder = repo / "fixtures/evaluation/s" / part
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{name}.yaml").write_text(yaml.safe_dump({"gold_answer": "the secret answer", **question}))
        old = json.loads((bin_dir / "plan.json").read_text()) if (bin_dir / "plan.json").exists() else {}
        (bin_dir / "plan.json").write_text(json.dumps({**old, question["question"]: plan}))

    def run(*argv, capsys):
        code = measure.main(["s", "--root", str(repo), "--gov", str(gov), *argv])
        out, err = capsys.readouterr()
        return code, out, err

    return repo, bin_dir, ask, run


def test_hit_at_5_in_bundle_and_full_evidence_across_batches(planted, capsys):
    repo, bin_dir, ask, run = planted
    filler = [item(f"f{n}.md", 1, 1) for n in range(5)]
    ask("visible", "q1", [filler + [item("src.py", 3, 4)], [item("docs/a.md", 2, 2)]], question="q one",
        sources=[{"path": "src.py", "lines": [4, 6]}, {"path": "docs/a.md", "heading": "# A"}])
    code, out, _ = run("--json", capsys=capsys)
    assert code == 0
    q = json.loads(out)["questions"][0]
    assert (q["hit_at_5"], q["in_bundle"], q["full_evidence"], q["first_gold_rank"], q["calls"]) == (
        False, True, True, 6, 2)
    calls = [json.loads(line) for line in (bin_dir / "calls.log").read_text().splitlines()]
    assert calls[0][:4] == ["retrieve", "--batch-size", "10", "--bundle-budget"] and "--continue" in calls[1]


def test_a_heading_governs_over_stale_lines(planted):
    repo = planted[0]
    assert measure._span({"path": "docs/a.md", "heading": "# A", "lines": [9, 9]}, repo, "visible", "q") == (2, 5)
    assert measure._span({"path": "docs/a.md", "heading": "## A.1"}, repo, "visible", "q") == (4, 5)
    assert measure._span({"path": "src.py", "heading": "line 7", "lines": [1, 3]}, repo, "visible", "q") == (7, 9)
    assert measure._span({"path": "src.py", "heading": "gone", "lines": [2, 3]}, repo, "visible", "q") == (2, 3)
    with pytest.raises(measure.MeasureError):
        measure._span({"path": "src.py", "heading": "gone"}, repo, "visible", "q")


def test_the_stack_budget_stops_the_stacking(planted, capsys):
    _, bin_dir, ask, run = planted
    ask("visible", "q1", [[item("a", 1, 1, "y" * 40), item("src.py", 1, 1, "z" * 40)], [item("src.py", 2, 2)]],
        question="q one", sources=[{"path": "src.py"}])
    code, out, _ = run("--json", "--stack-budget", "15", capsys=capsys)
    q = json.loads(out)["questions"][0]
    assert code == 0 and q["calls"] == 1 and not q["hit_at_5"] and q["in_bundle"]


def test_a_quoting_path_is_never_a_hit(planted, capsys):
    _, _, ask, run = planted
    ask("visible", "q1", [[item("docs/report.md", 1, 1), item("fixtures/evaluation/s/visible/q1.yaml", 1, 2)]],
        question="q one", sources=[[{"path": "docs/report.md"}, {"path": "src.py", "lines": [1, 1]}]])
    code, out, _ = run("--json", capsys=capsys)
    q = json.loads(out)["questions"][0]
    assert code == 0 and not q["hit_at_5"] and not q["full_evidence"] and q["first_gold_rank"] is None


def test_the_hidden_part_is_refused_to_a_measured_session(planted, capsys, monkeypatch):
    _, _, ask, run = planted
    ask("hidden", "h1", [[]], question="hidden words", sources=[{"path": "src.py"}])
    monkeypatch.setenv("GOV_ROLE", "engineer")
    assert run("--part", "hidden", capsys=capsys)[0] != 0
    monkeypatch.setenv("GOV_ROLE", "orchestrator")
    monkeypatch.setenv("GOV_TICKET", "W9-01")
    code, _, err = run("--part", "all", capsys=capsys)
    assert code != 0 and "s" in err


def test_the_hidden_part_prints_scores_only(planted, capsys, tmp_path):
    _, _, ask, run = planted
    ask("hidden", "h1", [[item("src.py", 1, 2, "retrieved hidden text")]], question="hidden words",
        sources=[{"path": "src.py", "heading": "line 2"}])
    code, out, err = run("--part", "hidden", "--out", str(tmp_path / "rec"), capsys=capsys)
    record = next((tmp_path / "rec").iterdir()).read_text()
    assert code == 0 and "hit@5 yes" in out and "full evidence yes" in out
    for word in ("hidden words", "secret answer", "src.py", "line 2", "retrieved hidden text"):
        assert word not in out + err + record


def test_an_error_on_a_hidden_question_names_its_id_only(planted, capsys):
    _, _, ask, run = planted
    ask("hidden", "h1", [[]], question="hidden words", sources=[{"path": "missing/secret-path.md"}])
    code, out, err = run("--part", "hidden", capsys=capsys)
    assert code != 0 and "h1" in err and "secret-path" not in out + err and "hidden words" not in out + err


def test_undeclared_set_and_uncovered_hidden_folder_are_refused(planted, capsys):
    repo, _, ask, run = planted
    assert measure.main(["absent", "--root", str(repo)]) != 0
    ask("hidden", "h1", [[]], question="hidden words", sources=[{"path": "src.py"}])
    sets = {"evaluation_sets": {"s": {**PATH_MAP["evaluation_sets"]["s"], "hidden": ["elsewhere/**"]}}}
    (repo / "governance/project/path-map.yaml").write_text(yaml.safe_dump(sets))
    code, _, err = run("--part", "hidden", capsys=capsys)
    assert code != 0 and "hidden" in err


def test_compare_names_what_differs(planted, capsys, tmp_path):
    _, bin_dir, ask, run = planted
    ask("visible", "q1", [[item("src.py", 1, 1)]], question="q one", sources=[{"path": "src.py"}])
    run("--out", str(tmp_path / "rec"), capsys=capsys)
    record = str(next((tmp_path / "rec").iterdir()))
    ask("visible", "q1", [[item("other", 1, 1), item("src.py", 1, 1)]], question="q one", sources=[{"path": "src.py"}])
    code, out, _ = run("--json", "--compare", record, "--compare", record, capsys=capsys)
    compare = json.loads(out)["questions"][0]["compare"]
    assert code == 0 and compare[0] == compare[1] == {"same": False, "differs": ["first_gold_rank", "stacked_digest"]}
