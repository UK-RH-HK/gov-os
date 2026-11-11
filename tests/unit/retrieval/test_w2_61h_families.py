"""Builder tests of S7, the source families in ``gov.retrieval.measure`` (W2-61h; DEC-1078 (4), DEC-1079): a planted
``gov`` and planted sets in ``tmp_path``; no store, no embedder, no network, never the real hidden half."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from gov.retrieval import measure

GOV = """#!{python}
import json, os, pathlib, sys
here = pathlib.Path(__file__).parent
args = sys.argv[1:]
if args == ["--version"]:
    print("gov 0.0 (commit planted)")
    sys.exit(0)
batches = json.loads((here / "plan.json").read_text())[args[-2]]
n = int(args[args.index("--continue") + 1]) if "--continue" in args else 0
more = str(n + 1) if n + 1 < len(batches) else None
out = json.dumps({{"ok": True, "result": {{"evidence": batches[n], "continuation": more}}}})
keep = os.environ.get("GOV_KEEP")
if keep:
    k = int((pathlib.Path(keep) / ".n").read_text() or 0) + 1
    (pathlib.Path(keep) / ".n").write_text(str(k))
    (pathlib.Path(keep) / f"{{k:05d}}.json").write_text(out)
print(out)
"""

FAMILIES = {"contract": ["docs/contract/CONTRACT.md", "docs/contract/contract.yaml", "docs/contract/caps/*.md"],
            "agents": ["AGENTS.md", "CLAUDE.md"]}
SETS = {"s": {"visible": ["docs/report.md"], "hidden": ["fixtures/evaluation/s/hidden/**"],
              "measures": {"roles": ["engineer"]}}}

CONTRACT_MD = """# Contract

### CAP-10 — Semantic memory

- **Outcome:** An agent can find a record
  from a paraphrased question.
- **Wave:** W1

### CAP-11 — Lexical memory
"""
CONTRACT_YAML = """- id: CAP-10
  title: Semantic memory
  outcome: "An agent can find a record from a paraphrased question."
  wave: W1
"""


def item(path, first, last, text="x" * 40):
    return {"path": path, "start_line": first, "end_line": last, "text": text}


@pytest.fixture
def planted(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / "governance/project").mkdir(parents=True)
    (repo / "docs/contract/caps").mkdir(parents=True)
    (repo / "docs/report.md").write_text("quote\n")
    (repo / "docs/contract/CONTRACT.md").write_text(CONTRACT_MD)
    (repo / "docs/contract/contract.yaml").write_text(CONTRACT_YAML)
    (repo / "docs/other.md").write_text(CONTRACT_YAML)
    (repo / "AGENTS.md").write_text("# Agents\n\nRule one: every change has a ticket.\n")
    (repo / "CLAUDE.md").write_text("# Claude\n\n- Rule one: every change has a ticket.\n")

    def path_map(families=FAMILIES):
        doc = {"evaluation_sets": SETS, **({"evaluation_families": families} if families is not None else {})}
        (repo / "governance/project/path-map.yaml").write_text(yaml.safe_dump(doc))

    path_map()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "planted"], check=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gov = bin_dir / "gov"
    gov.write_text(GOV.format(python=sys.executable))
    gov.chmod(0o755)
    monkeypatch.setenv("GOV_ROLE", "orchestrator")
    monkeypatch.delenv("GOV_TICKET", raising=False)
    monkeypatch.delenv("GOV_KEEP", raising=False)

    def ask(part, name, plan, **question):
        folder = repo / "fixtures/evaluation/s" / part
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{name}.yaml").write_text(yaml.safe_dump({"gold_answer": "the answer", **question}))
        old = json.loads((bin_dir / "plan.json").read_text()) if (bin_dir / "plan.json").exists() else {}
        (bin_dir / "plan.json").write_text(json.dumps({**old, question["question"]: plan}))

    def run(*argv, capsys, json_out=True):
        code = measure.main(["s", "--root", str(repo), "--gov", str(gov), *(["--json"] if json_out else []), *argv])
        out, err = capsys.readouterr()
        return code, (json.loads(out) if json_out and code == 0 else out), err

    return repo, bin_dir, ask, run, path_map


OUTCOME = {"path": "docs/contract/CONTRACT.md", "lines": [5, 6]}
YAML_ITEM = item("docs/contract/contract.yaml", 1, 4, CONTRACT_YAML)


def test_a_copy_holding_the_gold_text_is_a_family_hit_and_named(planted, capsys):
    _, _, ask, run, _ = planted
    ask("visible", "q1", [[item("f.md", 1, 1), YAML_ITEM]], question="q one", sources=[OUTCOME])
    code, doc, _ = run(capsys=capsys)
    q = doc["questions"][0]
    assert code == 0
    assert (q["hit_at_5"], q["in_bundle"], q["full_evidence"], q["first_gold_rank"]) == (True, True, True, 2)
    assert q["family_hits"] == ["docs/contract/contract.yaml"] and q["family_hit_count"] == 1
    code, out, _ = run(capsys=capsys, json_out=False)
    line = next(x for x in out.splitlines() if x.startswith("q1 (visible): hit@5 yes (first gold rank 2)"))
    assert line.endswith("; family hit: docs/contract/contract.yaml")


def test_a_member_whose_text_does_not_hold_the_gold_text_is_never_a_hit(planted, capsys):
    _, _, ask, run, _ = planted
    partial = item("docs/contract/contract.yaml", 1, 2, "- id: CAP-10\n  outcome: An agent can find a record\n")
    ask("visible", "q1", [[partial, item("docs/contract/contract.yaml", 3, 4, "")]], question="q one",
        sources=[OUTCOME])
    _, doc, _ = run(capsys=capsys)
    q = doc["questions"][0]
    assert not q["hit_at_5"] and q["first_gold_rank"] is None and q["family_hits"] == []


def test_a_path_outside_the_family_is_never_a_hit_even_with_the_text(planted, capsys):
    _, _, ask, run, _ = planted
    ask("visible", "q1", [[item("docs/other.md", 1, 4, CONTRACT_YAML)]], question="q one", sources=[OUTCOME])
    _, doc, _ = run(capsys=capsys)
    assert not doc["questions"][0]["hit_at_5"] and doc["questions"][0]["family_hits"] == []


def test_a_direct_hit_stays_direct_and_is_not_named(planted, capsys):
    _, _, ask, run, _ = planted
    ask("visible", "q1", [[item("docs/contract/CONTRACT.md", 3, 7, "x")]], question="q one", sources=[OUTCOME])
    _, doc, _ = run(capsys=capsys)
    q = doc["questions"][0]
    assert q["hit_at_5"] and q["family_hits"] == [] and q["family_hit_count"] == 0


def test_with_no_family_declared_every_figure_and_line_is_as_today(planted, capsys):
    repo, _, ask, run, path_map = planted
    path_map(None)
    ask("visible", "q1", [[YAML_ITEM, item("docs/contract/CONTRACT.md", 5, 5)]], question="q one",
        sources=[OUTCOME])
    _, doc, _ = run(capsys=capsys)
    q = doc["questions"][0]
    assert (q["hit_at_5"], q["first_gold_rank"]) == (True, 2)
    assert "family_hits" not in q and "family_hit_count" not in q
    _, out, _ = run(capsys=capsys, json_out=False)
    assert ("q1 (visible): hit@5 yes (first gold rank 2), in the bundle yes; full evidence yes (1 of 1 pieces); "
            "1 calls") in out.splitlines()


def test_the_agents_family_matches_through_list_marks(planted, capsys):
    _, _, ask, run, _ = planted
    ask("visible", "q1", [[item("CLAUDE.md", 1, 3, "# Claude\n\n- Rule one: every change has a ticket.\n")]],
        question="q one", sources=[{"path": "AGENTS.md", "lines": [3, 3]}])
    _, doc, _ = run(capsys=capsys)
    assert doc["questions"][0]["hit_at_5"] and doc["questions"][0]["family_hits"] == ["CLAUDE.md"]


def test_the_hidden_part_names_a_family_hit_by_its_count_only(planted, capsys):
    _, _, ask, run, _ = planted
    ask("hidden", "h1", [[YAML_ITEM]], question="hidden words", sources=[OUTCOME])
    code, out, _ = run("--part", "hidden", capsys=capsys, json_out=False)
    assert code == 0
    line = next(x for x in out.splitlines() if x.startswith("h1 (hidden)"))
    assert line.endswith("; family hits: 1") and "contract.yaml" not in out
    _, doc, _ = run("--part", "hidden", capsys=capsys)
    assert doc["questions"][0]["family_hit_count"] == 1 and "family_hits" not in doc["questions"][0]


def test_malformed_families_refuse_the_run(planted, capsys):
    _, _, ask, run, path_map = planted
    ask("visible", "q1", [[YAML_ITEM]], question="q one", sources=[OUTCOME])
    path_map({"contract": "docs/contract/*"})
    code, _, err = run(capsys=capsys)
    assert code != 0 and "evaluation_families" in err


def test_kept_outputs_are_re_scored_with_families_without_a_retriever(planted, capsys, tmp_path, monkeypatch):
    repo, _, ask, run, path_map = planted
    filler = [item(f"f{n}.md", 1, 1) for n in range(3)]
    ask("visible", "q1", [filler, [YAML_ITEM]], question="q one", sources=[OUTCOME])
    ask("visible", "q2", [[item("CLAUDE.md", 1, 3, "- Rule one: every change has a ticket.")]], question="q two",
        sources=[{"path": "AGENTS.md", "lines": [3, 3]}])
    keep = tmp_path / "kept"
    keep.mkdir()
    (keep / ".n").write_text("")
    (keep / ".n.lock").write_text("")
    path_map(None)
    monkeypatch.setenv("GOV_KEEP", str(keep))
    _, before, _ = run(capsys=capsys)  # the kept run, without families
    monkeypatch.delenv("GOV_KEEP")
    assert sorted(p.name for p in keep.glob("*.json")) == ["00001.json", "00002.json", "00003.json"]
    assert [q["hit_at_5"] for q in before["questions"]] == [False, False]
    path_map()
    code = measure.main(["s", "--root", str(repo), "--gov", "/no/such/gov", "--kept", str(keep), "--json"])
    after = json.loads(capsys.readouterr()[0])
    assert code == 0 and after["retriever"]["kept"] == str(keep.resolve())
    assert [(q["hit_at_5"], q["full_evidence"], q["calls"]) for q in after["questions"]] == [(True, True, 2),
                                                                                           (True, True, 1)]
    assert after["questions"][0]["stacked_digest"] == before["questions"][0]["stacked_digest"]
    path_map(None)  # without families, the kept outputs give the kept run's figures
    measure.main(["s", "--root", str(repo), "--kept", str(keep), "--json"])
    again = json.loads(capsys.readouterr()[0])
    assert [{k: q[k] for k in measure.FIGURES} for q in again["questions"]] == [
        {k: q[k] for k in measure.FIGURES} for q in before["questions"]]


def test_kept_outputs_that_do_not_match_the_run_are_refused(planted, capsys, tmp_path):
    repo, _, ask, _, _ = planted
    ask("visible", "q1", [[YAML_ITEM], [YAML_ITEM]], question="q one", sources=[OUTCOME])
    keep = tmp_path / "kept"
    keep.mkdir()
    one = json.dumps({"ok": True, "result": {"evidence": [YAML_ITEM], "continuation": "1"}})
    (keep / "00001.json").write_text(one)
    assert measure.main(["s", "--root", str(repo), "--kept", str(keep)]) == 1
    assert "kept outputs end" in capsys.readouterr()[1]
    last = json.dumps({"ok": True, "result": {"evidence": [], "continuation": None}})
    (keep / "00002.json").write_text(last)
    (keep / "00003.json").write_text(last)
    assert measure.main(["s", "--root", str(repo), "--kept", str(keep)]) == 1
    assert "do not match" in capsys.readouterr()[1]


def test_normalising_drops_markdown_and_yaml_formatting():
    # one test, not parametrised: the suite's conftest runs only a parametrised function's first row by default
    pairs = [("### CAP-10 — Semantic memory", "title: CAP-10 — Semantic memory"),
             ("- **Outcome:** An agent\n  can find it.", 'outcome: "An agent can find it."'),
             ("> quoted `code` *here*", "quoted code here"),
             ("1. first\n2. second", "- first\n- second"),
             ("statement: >-\n  folded\n  text", "folded text"),
             ('key: "say \\"x\\""', "say x")]
    assert [measure._normal(a) for a, _ in pairs] == [measure._normal(b) for _, b in pairs]
    assert all(measure._normal(a) for a, _ in pairs)


def test_normalising_keeps_the_words():
    assert measure._normal("An agent can find a record") != measure._normal("An agent can find a file")
    assert measure._normal("# \n\n  ") == ""


def test_this_repository_declares_its_families():
    root = Path(__file__).resolve().parents[3]
    declared = {f.reason: f for f in measure.families(root, root)}
    assert set(declared) >= {"contract", "kernel", "agents"}
    for name, paths in {"contract": ["docs/contract/CONTRACT_v4.md", "docs/contract/contract.yaml",
                                     "docs/contract/capabilities/CAP-10.a.md", "docs/contract/master-rules/MR-1.md"],
                        "kernel": ["template/governance/kernel/roles/engineer.md", ".claude/agents/engineer.md",
                                   ".rulesync/subagents/engineer.md"],
                        "agents": ["AGENTS.md", "CLAUDE.md"]}.items():
        assert all(declared[name].match(p) for p in paths), name
    assert not declared["contract"].match("docs/contract/SOURCE_MAP.csv")
    lines = (root / "governance/project/path-map.yaml").read_text().splitlines()
    at = lines.index("evaluation_families:")
    comment = []
    while lines[at - 1 - len(comment)].startswith("#"):
        comment.append(lines[at - 1 - len(comment)])
    assert "DEC-1078 (4)" in " ".join(comment)
