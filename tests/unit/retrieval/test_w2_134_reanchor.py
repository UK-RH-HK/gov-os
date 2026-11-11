"""Builder tests of W2-134 in ``gov.retrieval.measure``: line-cited gold re-anchored in memory for the measured commit
(S1 to S4), the family floor and token edges (S5) and the families line (S6). A planted git repository with two
commits, a planted sets root and a planted ``gov``; no store, no embedder, no model, never the real sets."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys

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

SETS = {"s": {"visible": ["docs/report.md"], "hidden": ["fixtures/evaluation/s/hidden/**"],
              "measures": {"roles": ["engineer"]}}}
FAMILIES = {"notes": ["docs/notes.md", "docs/copy.md", "docs/more/*.md"], "pair": ["a.md", "b.md"]}
BLOCK = ["The cited rule: every change carries one ticket", "and every ticket names its tests."]
NOTES_1 = ["# Notes", "", *BLOCK, "", "## Tail", "end"]
NOTES_2 = ["# Notes", "", "inserted one", "inserted two", "inserted three", "inserted four", "inserted five", "",
           *BLOCK, "", "## Tail", "end"]
SECRET = "secret-gold-text"


def item(path, first, last, text="x" * 40):
    return {"path": path, "start_line": first, "end_line": last, "text": text}


def write(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def tree_hash(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob("*")) if p.is_file()}


@pytest.fixture
def planted(tmp_path, monkeypatch):
    """A repository with two commits (the cited block moves down by five lines in the second), a sets root of its
    own, a stand-in ``gov`` and helpers."""
    repo, sets = tmp_path / "repo", tmp_path / "sets"
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
    write(repo / "docs/report.md", ["quote"])
    write(repo / "docs/notes.md", NOTES_1)
    write(repo / "docs/gone.md", ["keep", f"the {SECRET} that the second commit deletes", "keep"])
    write(repo / "docs/twice.md", ["one", "dup line here", "two"])
    write(repo / "governance/project/path-map.yaml", ["{}"])
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "one"], check=True)
    c1 = subprocess.run([*git, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    write(repo / "docs/notes.md", NOTES_2)
    write(repo / "docs/gone.md", ["keep", "keep"])
    write(repo / "docs/twice.md", ["one", "two", "dup line here", "dup line here"])  # moved, and found twice
    subprocess.run([*git, "commit", "-q", "-am", "two"], check=True)
    c2 = subprocess.run([*git, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gov = bin_dir / "gov"
    gov.write_text(GOV.format(python=sys.executable))
    gov.chmod(0o755)
    monkeypatch.setenv("GOV_ROLE", "orchestrator")
    monkeypatch.delenv("GOV_TICKET", raising=False)
    monkeypatch.delenv("GOV_KEEP", raising=False)

    def path_map(families=None):
        doc = {"evaluation_sets": SETS, **({"evaluation_families": families} if families is not None else {})}
        write(sets / "governance/project/path-map.yaml", [yaml.safe_dump(doc)])

    def ask(part, name, plan, **question):
        folder = sets / "fixtures/evaluation/s" / part
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{name}.yaml").write_text(yaml.safe_dump({"gold_answer": f"the {SECRET}", **question}))
        old = json.loads((bin_dir / "plan.json").read_text()) if (bin_dir / "plan.json").exists() else {}
        (bin_dir / "plan.json").write_text(json.dumps({**old, question["question"]: plan}))

    def run(*argv, capsys, root=repo, json_out=True):
        code = measure.main(["s", "--root", str(root), "--sets-root", str(sets), "--gov", str(gov),
                             *(["--json"] if json_out else []), *argv])
        out, err = capsys.readouterr()
        return code, (json.loads(out) if json_out and code == 0 else out), err

    path_map()
    return {"repo": repo, "sets": sets, "c1": c1, "c2": c2, "git": git, "ask": ask, "run": run,
            "path_map": path_map, "tmp": tmp_path}


def at_commit(p, commit):
    """A second root: a clone of the planted repository checked out at ``commit``."""
    clone = p["tmp"] / f"clone-{commit[:7]}"
    subprocess.run(["git", "clone", "-q", str(p["repo"]), str(clone)], check=True)
    subprocess.run(["git", "-C", str(clone), "checkout", "-q", commit], check=True)
    return clone


def test_s1_a_moved_block_is_scored_at_its_new_lines(planted, capsys):
    p = planted
    cited = {"path": "docs/notes.md", "lines": [3, 4], "commit": p["c1"]}
    p["ask"]("visible", "q1", [[item("docs/notes.md", 9, 10)]], question="moved", sources=[cited])
    p["ask"]("visible", "q2", [[item("docs/notes.md", 3, 4)]], question="old lines", sources=[cited])
    # the question's own commit stands in for a source that names none
    p["ask"]("visible", "q3", [[item("docs/notes.md", 10, 10)]], question="by the question", commit=p["c1"][:12],
             sources=[{"path": "docs/notes.md", "lines": [3, 4]}])
    code, doc, _ = p["run"](capsys=capsys)
    q1, q2, q3 = doc["questions"]
    assert code == 0
    assert (q1["hit_at_5"], q1["full_evidence"], q1["first_gold_rank"]) == (True, True, 1)
    assert not q2["hit_at_5"] and q2["first_gold_rank"] is None  # the first commit's lines are not the second's
    assert q3["hit_at_5"] and "unresolved" not in q1 and "unresolved" not in q3


def test_s1_an_unmoved_block_keeps_its_lines_and_the_cache_reads_git_once(planted, monkeypatch):
    p = planted
    calls = []
    real = subprocess.run

    def counted(cmd, *a, **k):
        if cmd[:1] == ["git"] and "show" in cmd:
            calls.append(cmd)
        return real(cmd, *a, **k)

    monkeypatch.setattr(measure.subprocess, "run", counted)
    cache = {}
    tail = {"path": "docs/notes.md", "lines": [12, 13], "commit": p["c2"]}
    assert measure._span(tail, p["repo"], "visible", "q", None, cache) == (12, 13)
    moved = {"path": "docs/notes.md", "lines": [3, 4], "commit": p["c1"]}
    assert measure._span(moved, p["repo"], "visible", "q", None, cache) == (9, 10)
    assert measure._span(moved, p["repo"], "visible", "q", None, cache) == (9, 10)
    assert len(calls) == 2
    # a heading found at the root governs: no git read
    assert measure._span({**moved, "heading": "## Tail"}, p["repo"], "visible", "q", None, cache) == (12, 13)
    assert len(calls) == 2


def test_s1_family_text_uses_the_found_lines_live_and_kept(planted, capsys, monkeypatch):
    p = planted
    p["path_map"](FAMILIES)
    copy = item("docs/copy.md", 1, 2, "- " + "\n- ".join(BLOCK))
    p["ask"]("visible", "q1", [[copy]], question="family",
             sources=[{"path": "docs/notes.md", "lines": [3, 4], "commit": p["c1"]}])
    keep = p["tmp"] / "kept"
    keep.mkdir()
    (keep / ".n").write_text("")
    monkeypatch.setenv("GOV_KEEP", str(keep))
    _, live, _ = p["run"](capsys=capsys)
    monkeypatch.delenv("GOV_KEEP")
    assert live["questions"][0]["family_hits"] == ["docs/copy.md"] and live["questions"][0]["hit_at_5"]
    code, kept, _ = p["run"]("--kept", str(keep), capsys=capsys)
    assert code == 0 and [{k: q[k] for k in measure.FIGURES} for q in kept["questions"]] == [
        {k: q[k] for k in measure.FIGURES} for q in live["questions"]]
    # stated lines (3, 4) at the second commit are filler: without re-anchoring the copy would not be held
    assert measure._normal("\n".join(NOTES_2[2:4])) not in measure._normal(copy["text"])


def test_s2_two_commits_each_scored_on_its_own_lines_and_the_sets_root_unwritten(planted, capsys):
    p = planted
    cited = {"path": "docs/notes.md", "lines": [3, 4], "commit": p["c1"]}
    p["ask"]("visible", "q1", [[item("docs/notes.md", 3, 4)]], question="old", sources=[cited])
    p["ask"]("visible", "q2", [[item("docs/notes.md", 9, 10)]], question="new", sources=[cited])
    before = tree_hash(p["sets"])
    old_root = at_commit(p, p["c1"])
    _, first, _ = p["run"](capsys=capsys, root=old_root)
    _, second, _ = p["run"](capsys=capsys)
    _, third, _ = p["run"](capsys=capsys, root=old_root)
    assert [q["hit_at_5"] for q in first["questions"]] == [True, False]
    assert [q["hit_at_5"] for q in second["questions"]] == [False, True]
    assert third["questions"] == first["questions"]  # nothing carried from one run to the next
    assert tree_hash(p["sets"]) == before
    assert not list(p["sets"].rglob("REANCHOR-LOG*")) and not list(p["sets"].rglob("backup-*"))


def test_s3_a_deleted_or_doubled_block_is_named_by_id_and_entry_only(planted, capsys):
    p = planted
    keep = {"path": "docs/notes.md", "lines": [3, 4], "commit": p["c1"]}
    gone = {"path": "docs/gone.md", "lines": [2, 2], "commit": p["c1"]}
    twice = {"path": "docs/twice.md", "lines": [2, 2], "commit": p["c1"]}
    p["ask"]("visible", "q1", [[item("docs/notes.md", 9, 10), item("docs/gone.md", 1, 2),
                                 item("docs/twice.md", 1, 4)]], question="gone", sources=[keep, gone, [twice, keep]])
    code, out, err = p["run"](capsys=capsys, json_out=False)
    assert code == 0
    lines = out.splitlines()
    named = [x for x in lines if "unresolved" in x]
    assert len(named) == 2 and named[0].startswith("q1 (visible): entry 2 unresolved")
    assert named[1].startswith("q1 (visible): entry 3.1 unresolved")
    assert "full evidence no (2 of 3 pieces)" in next(x for x in lines if x.startswith("q1 (visible): hit@5"))
    for word in (SECRET, "gone.md", "twice.md", "dup line", "[2, 2]", "lines 2"):
        assert word not in out + err
    code, doc, err = p["run"](capsys=capsys)  # with --json, standard output stays one document
    q = doc["questions"][0]
    assert code == 0 and q["unresolved"] == ["entry 2", "entry 3.1"] and q["pieces_found"] == 2
    assert "q1 (visible): entry 2 unresolved" in err and SECRET not in err


def test_s3_hidden_unknown_commit_and_vanished_file_are_unresolved_by_number(planted, capsys):
    p = planted
    sources = [{"path": "docs/gone.md", "lines": [2, 2], "commit": "0" * 12},
               {"path": "docs/secret-vanished.md", "lines": [1, 1], "commit": p["c1"]},
               {"path": "docs/notes.md", "lines": [3, 4], "commit": "--output=x"}]
    p["ask"]("hidden", "h1", [[item("docs/notes.md", 3, 4)]], question="hidden words", sources=sources)
    code, out, err = p["run"]("--part", "hidden", capsys=capsys, json_out=False)
    assert code == 0
    assert [x.split(" unresolved")[0] for x in out.splitlines() if "unresolved" in x] == [
        "h1 (hidden): entry 1", "h1 (hidden): entry 2", "h1 (hidden): entry 3"]
    for word in ("hidden words", SECRET, "gone.md", "secret-vanished", "notes.md"):
        assert word not in out + err
    assert not (p["repo"] / "x").exists()


def test_s4_unmoved_and_uncommitted_sources_score_as_today(planted, capsys):
    p = planted
    plan = [[item("f.md", 1, 1), item("docs/notes.md", 12, 13)], [item("docs/report.md", 1, 1)]]
    tail = {"path": "docs/notes.md", "lines": [12, 13]}
    p["ask"]("visible", "q1", plan, question="unmoved", sources=[tail, {"path": "docs/report.md"}])
    p["ask"]("visible", "q2", [[item("docs/notes.md", 3, 4)]], question="no commit",
             sources=[{"path": "docs/notes.md", "lines": [3, 4]}])
    _, today, _ = p["run"](capsys=capsys, json_out=False)
    p["ask"]("visible", "q1", plan, question="unmoved", sources=[{**tail, "commit": p["c2"]}, {"path": "docs/report.md"}])
    _, now, _ = p["run"](capsys=capsys, json_out=False)
    assert now == today
    assert "q2 (visible): hit@5 yes (first gold rank 1)" in now  # no commit: the stated lines, as today
    assert not any("unresolved" in x for x in now.splitlines())


def test_s5_family_floor_and_token_edges(planted):
    p = planted
    repo = p["repo"]
    declared = [measure._Part("/f", ["gold/*", "copy/*"], "f")]
    rows = [  # (gold line, the member's text, a family hit?)
        ("    floor: 85", "DEC-850 set the review at 1985 lines.", False),
        ("  - id: CAP-1", "# CAP-10 Retrieval", False),
        ("status: open", "owner: open", False),
        ("DEC-1078: the owner accepts option A.", "DEC-1079: the owner accepts option A.", False),
        ("DEC-1078: the owner accepts option A.", "- DEC-1078: the owner accepts option A.", True),
        ("the floor is set for CAP-1", "so the floor is set for CAP-10 here", False),
        ("85 lines of the review plan", "1985 lines of the review plan", False),
        ("85 lines of the review plan", "it was 0.85 lines of the review plan", False),
        ("the floor is set for CAP-1", "so the floor is set for CAP-1, here", True),
        ("alpha beta gamma deltaZZ", "> alpha beta gamma deltaZZ", True),  # 4 words, 24 characters: the floor
        ("alpha beta gamma deltaZ", "alpha beta gamma deltaZ", False),  # 23 characters
        ("alphabetical betamaxes gammarays", "alphabetical betamaxes gammarays", False),  # 3 words
    ]
    got = []
    for n, (gold, held, _) in enumerate(rows):
        write(repo / f"gold/g{n}.md", [gold])
        alt = measure._alternative({"path": f"gold/g{n}.md", "lines": [1, 1]}, repo, "visible", "q", declared)
        got.append(measure._match(("copy/c.md", 1, 1, held), [alt]) == "family")
        # below the floor a gold still counts in its own path
        assert measure._match((f"gold/g{n}.md", 1, 1, ""), [alt]) == "direct"
    assert got == [want for *_, want in rows]


def test_s6_the_first_line_names_the_families_in_force(planted, capsys):
    p = planted
    p["ask"]("visible", "q1", [[item("docs/notes.md", 9, 10)]], question="q one",
             sources=[{"path": "docs/notes.md", "lines": [3, 4], "commit": p["c1"]}])
    _, out, _ = p["run"](capsys=capsys, json_out=False)
    assert out.splitlines()[:2] == ["families: none", "measure: set s, part visible"]
    p["path_map"](FAMILIES)  # declared only in the sets root's path map, not the measured root's
    _, out, _ = p["run"](capsys=capsys, json_out=False)
    assert out.splitlines()[0] == "families: notes (3 members), pair (2 members)"
    code, doc, _ = p["run"](capsys=capsys)
    assert code == 0 and doc["families"] == [{"name": "notes", "members": 3}, {"name": "pair", "members": 2}]
    keep = p["tmp"] / "kept"
    keep.mkdir()
    (keep / "00001.json").write_text(json.dumps({"ok": True, "result": {"evidence": [], "continuation": None}}))
    code = measure.main(["s", "--root", str(p["repo"]), "--sets-root", str(p["sets"]), "--kept", str(keep)])
    out = capsys.readouterr()[0]
    assert code == 0 and out.splitlines()[0] == "families: notes (3 members), pair (2 members)"
