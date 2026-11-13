"""W2-150 S3: every moved name stays importable from its old module, with the same behaviour (DAEO-ijf5; DEC-1040 (1)).

Each case runs in a fresh subprocess (``python3 -c``) on this tree's own ``src``, so no module the test process
already holds can hide a broken re-import. The behaviour checks pin today's results of each helper the move touches,
on inputs that need nothing beyond a temporary folder (a temporary git folder for ``of_commit``).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import textwrap

import pytest

from w2_150_run import run_json, run_py

OLD_NAMES = [
    ("gov.close.fingerprint", "of_commit"),
    ("gov.guard.decide", "_match_pattern"),
    ("gov.tasks.tickets", "TICKETS_REL"),
    ("gov.guard.runs", "root"),
    ("gov.decisions.register", "leave_out"),
    ("gov.guard.reads", "evaluation_sets"),
    ("gov.guard.reads", "PolicyError"),
    ("gov.guard.reads", "PATH_MAP_REL"),
    ("gov.guard.reads", "SETS_KEY"),
    ("gov.guard.reads", "set_fault"),
    # the other names retrieval/measure.py imports from gov.guard.reads today (measure.py:74)
    ("gov.guard.reads", "_Part"),
    ("gov.guard.reads", "_ticket"),
]


@pytest.mark.parametrize("module,name", OLD_NAMES, ids=[f"{m}.{n}" for m, n in OLD_NAMES])
def test_s3_old_name_importable_from_its_old_module(module, name):
    done = run_py(f"from {module} import {name}")
    assert done.returncode == 0, f"`from {module} import {name}` fails in a fresh process:\n{done.stderr}"


def test_s3_constants_keep_their_values():
    got = run_json(textwrap.dedent("""
        import json
        from gov.tasks.tickets import TICKETS_REL
        from gov.guard.reads import PATH_MAP_REL, SETS_KEY, PolicyError
        print(json.dumps([TICKETS_REL, PATH_MAP_REL, SETS_KEY, issubclass(PolicyError, Exception)]))
    """))
    assert got == [".tickets", "governance/project/path-map.yaml", "evaluation_sets", True]


MATCH_CASES = [
    ("src/gov/a/b.py", "src/gov/**", True),
    ("src/gov", "src/gov/**", False),
    ("src/a.py", "src/*.py", True),
    ("src/a/b.py", "src/*.py", False),
    ("docs/x/y/z.md", "docs/**/z.md", True),
    ("docs/z.md", "docs/**/z.md", False),
    ("a.b", "a.b", True),
    ("axb", "a.b", False),
    ("tests/unit/util/test_x.py", "tests/unit/util/**", True),
]


def test_s3_match_pattern_behaves_as_today():
    got = run_json(textwrap.dedent(f"""
        import json
        from gov.guard.decide import _match_pattern
        print(json.dumps([_match_pattern(p, g) for p, g, _ in {MATCH_CASES!r}]))
    """))
    assert got == [want for _, _, want in MATCH_CASES]


def test_s3_runs_root_behaves_as_today(tmp_path):
    import os

    home = tmp_path / "home"
    home.mkdir()
    code = "import json\nfrom gov.guard.runs import root\nprint(json.dumps(root()))"
    assert run_json(code, home=home) == os.path.join(os.path.realpath(home), "gov-os-runs")
    assert run_json(code, home="relative-home") is None


def test_s3_leave_out_passes_evidence_without_lines_through(tmp_path):
    evidence = [{"id": "a", "path": "docs/x.md", "text": "x"}]
    got = run_json(textwrap.dedent(f"""
        import json
        from pathlib import Path
        from gov.decisions.register import leave_out
        print(json.dumps(leave_out(Path({str(tmp_path)!r}), {evidence!r})))
    """))
    assert got == [evidence, None]


def test_s3_evaluation_sets_and_set_fault_behave_as_today(tmp_path):
    none = tmp_path / "none"
    good = tmp_path / "good"
    bad = tmp_path / "bad"
    for root, text in ((good, "other: 1\nevaluation_sets:\n  s1:\n    hidden: [a/b.json]\n"
                                "    measures: {roles: [research]}\nlater: 2\n"),
                       (bad, "evaluation_sets:\n  - x\n")):
        (root / "governance/project").mkdir(parents=True)
        (root / "governance/project/path-map.yaml").write_text(text, encoding="utf-8")
    none.mkdir()
    got = run_json(textwrap.dedent(f"""
        import json
        from gov.guard.reads import PolicyError, evaluation_sets, set_fault
        out = [evaluation_sets({str(none)!r}), evaluation_sets({str(good)!r})]
        try:
            evaluation_sets({str(bad)!r})
            out.append("no error")
        except PolicyError:
            out.append("PolicyError")
        out += [set_fault([]), set_fault({{"hidden": ["a/b.json"], "measures": {{"roles": ["research"]}}}}),
                set_fault({{"hidden": []}}), set_fault({{"hidden": ["/abs"]}}),
                set_fault({{"hidden": ["a.json"], "measures": {{}}}})]
        print(json.dumps(out))
    """))
    assert got == [
        {},
        {"s1": {"hidden": ["a/b.json"], "measures": {"roles": ["research"]}}},
        "PolicyError",
        "a set is not a map",
        None,
        "a set's hidden part is not a non-empty list of project-relative paths",
        "a set's hidden part is not a non-empty list of project-relative paths",
        "a set's measures name no role and no ticket",
    ]


def _git(repo, *args) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                           "-c", "commit.gpgsign=false", *args],
                          check=True, capture_output=True, text=True).stdout


def _digest(lines) -> str:
    return "sha256:" + hashlib.sha256("".join(line + "\n" for line in sorted(lines)).encode("utf-8")).hexdigest()


def _of_commit(repo, commit="HEAD"):
    return run_json(textwrap.dedent(f"""
        import json
        from pathlib import Path
        from gov.close.fingerprint import of_commit
        print(json.dumps(of_commit(Path({str(repo)!r}), {commit!r})))
    """))


def test_s3_of_commit_classifies_paths_as_today(tmp_path):
    """The code fingerprint covers every entry but the ``record_only`` matches; the records fingerprint exactly
    those; the test map itself is always code; no test map, or a commit git cannot read, gives None."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    files = {
        "src/x.py": "x = 1\n",
        "docs/a.md": "a\n",
        "docs/sub/b.md": "b\n",
        "README.md": "r\n",
    }
    for rel, text in files.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "no test map")
    assert _of_commit(repo) is None

    (repo / "governance/project").mkdir(parents=True)
    (repo / "governance/project/test-map.yaml").write_text(
        "version: 1\nshared_core:\n  - 'src/**'\nrecord_only:\n  - 'docs/**'\n  - 'governance/project/**'\n",
        encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "test map")
    tree = {}
    for line in _git(repo, "-c", "core.quotePath=false", "ls-tree", "-r", "-z", "--full-tree", "HEAD").split("\0"):
        if line:
            tree[line.partition("\t")[2]] = line
    records = {p for p in tree if p.startswith("docs/")}
    assert _of_commit(repo) == {"code": _digest(tree[p] for p in tree if p not in records),
                                "records": _digest(tree[p] for p in records)}
    assert _of_commit(repo, "0" * 40) is None
    assert json.dumps(_of_commit(repo, "HEAD~1")) == "null"
