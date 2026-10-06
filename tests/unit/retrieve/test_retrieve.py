"""Builder tests for ``gov retrieve`` (W1-21).

Regression evidence only (DEC-136). They cover what the acceptance tests leave to the builder while DP-2 is open
(DEC-419): one batch that does not hold everything has no ``continuation`` key, names the rest as gaps and never
says that nothing is left; and two chunks of one parent expand it once. The store is built in a temporary
repository (DEC-322); the semantic route is replaced, so no endpoint is asked.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import store  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.retrieval import lexical, semantic  # noqa: E402
from gov.retrieval.retrieve import retrieve  # noqa: E402

pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")
PHRASE = "heron ledger"


@pytest.fixture()
def root(tmp_path, monkeypatch):
    """A temporary repository, indexed and loaded: three notes hold the phrase, and one long section holds it in
    its first and its last chunk."""
    git = ["git", "-C", str(tmp_path), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid"]
    subprocess.run([*git, "init", "-q"], check=True)
    (tmp_path / "governance/project").mkdir(parents=True)
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    (tmp_path / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")
    shutil.copy2(REPO / "template/.gitleaks.toml", tmp_path / ".gitleaks.toml")
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    for number in (1, 2, 3):
        (tmp_path / f"note{number}.md").write_text(f"# Note {number}\n\nThe {PHRASE} of pier {number}.\n", encoding="utf-8")
    filler = "".join(f"Line {number:03d} of a long section, kept to fill several chunks of text.\n" for number in range(60))
    (tmp_path / "long.md").write_text(f"# Long\n\nThe {PHRASE} opens.\n{filler}The {PHRASE} closes.\n", encoding="utf-8")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "fixture"], check=True)
    lexical.refresh(tmp_path)
    store.load(tmp_path)
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    return tmp_path


def test_one_batch_that_holds_everything_says_so(root):
    bundle = retrieve(root, PHRASE, bundle_budget=0, reranker=lambda: None)
    assert bundle["stopping_reason"] == "SATURATED" and bundle["continuation"] is None and bundle["gaps"] == []
    assert bundle["merge"]["candidates"] == bundle["batches"][0]["size"] == len(bundle["evidence"]) == 5
    assert "rounds" not in bundle["budget"]


def test_a_batch_size_limit_is_listed_as_gaps_and_never_as_completeness(root):
    whole = retrieve(root, PHRASE, bundle_budget=0, reranker=lambda: None)
    bundle = retrieve(root, PHRASE, batch_size=2, bundle_budget=0, reranker=lambda: None)
    assert "continuation" not in bundle and bundle["stopping_reason"] == "BUDGET_EXHAUSTED_WITH_GAPS"
    assert bundle["batches"] == [{"size": 2}] and len(bundle["evidence"]) == 2
    cited = {item["chunk_id"] for item in bundle["evidence"]}
    assert {gap["chunk_id"] for gap in bundle["gaps"]} == {item["chunk_id"] for item in whole["evidence"]} - cited


def test_two_chunks_of_one_parent_expand_it_once(root):
    bundle = retrieve(root, PHRASE, bundle_budget=1_000_000, reranker=lambda: None)
    long = [item for item in bundle["evidence"] if item["path"] == "long.md"]
    assert len(long) == 2 and [entry["path"] for entry in bundle["expansions"]].count("long.md") == 1
    assert len({(item["start_line"], item["end_line"]) for item in long}) == 2


def test_a_continuation_is_refused_while_no_token_exists(root):
    with pytest.raises(GovError) as refused:
        retrieve(root, PHRASE, continuation="anything")
    assert refused.value.code == "CONTINUATION_INVALID"
