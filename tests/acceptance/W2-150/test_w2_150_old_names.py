"""W2-150 S3: every moved name stays importable from its old module, with the same behaviour (DAEO-ijf5; DEC-1040 (1)).

Each case runs in a fresh subprocess (``python3 -c``) on this tree's own ``src``, so no module the test process
already holds can hide a broken re-import. The behaviour checks pin today's results of each helper the move touches,
on inputs that need nothing beyond a temporary folder (a temporary git folder for ``of_commit``).

Rewrite-Reason: EMERGENCY-2 6.1 (the guard / the sandbox retired), DAEO-gr7t. The old names of ``gov.guard.*`` and the cases
that ran their behaviour are deleted with the guard; the old names of the other modules stay.
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
    ("gov.tasks.tickets", "TICKETS_REL"),
    ("gov.decisions.register", "leave_out"),
]


@pytest.mark.parametrize("module,name", OLD_NAMES, ids=[f"{m}.{n}" for m, n in OLD_NAMES])
def test_s3_old_name_importable_from_its_old_module(module, name):
    done = run_py(f"from {module} import {name}")
    assert done.returncode == 0, f"`from {module} import {name}` fails in a fresh process:\n{done.stderr}"


def test_s3_leave_out_passes_evidence_without_lines_through(tmp_path):
    evidence = [{"id": "a", "path": "docs/x.md", "text": "x"}]
    got = run_json(textwrap.dedent(f"""
        import json
        from pathlib import Path
        from gov.decisions.register import leave_out
        print(json.dumps(leave_out(Path({str(tmp_path)!r}), {evidence!r})))
    """))
    assert got == [evidence, None]


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
