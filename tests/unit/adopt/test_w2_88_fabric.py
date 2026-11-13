"""W2-88 S3 to S6, S10, F2, F7: A9 lite on a planted repository, with stand-ins for the embedder, the keyword index
and the code graph (the real ones are the CTO's, outside the sandbox)."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import time
from pathlib import Path

import pytest
import yaml

from gov.adopt import fabric, stages
from gov.cli.errors import GovError
from gov.store import STORE_REL

ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t"}
SHIPPED = (Path(fabric.__file__).resolve().parents[3] / "governance/project/retrieval.yaml").read_text()
CONFIG = {"path-map.yaml": {"namespaces": {"all": {"paths": ["**"], "embedding_policy": "embedded",
                                                   "memory_class": "governance"}}}}


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=ENV)


def planted(tmp_path, retrieval=SHIPPED):
    root = tmp_path / "repo"
    (root / "governance/project").mkdir(parents=True)
    git(root, "init", "-q")
    git(root, "config", "user.name", "t")
    git(root, "config", "user.email", "t@t")
    (root / "governance/project/retrieval.yaml").write_text(retrieval)
    (root / "a.md").write_text("---\nid: R-1\ntype: note\nstatus: ACTIVE\n---\n\nthe answer is forty two\n")
    (root / "main.py").write_text("print('hi')\n")
    (root / "blob.bin").write_bytes(b"\0\1\2" * 50)
    (root / "cfg.env").write_text("a secret the filter refuses\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "init")
    return root


@pytest.fixture()
def stand_ins(monkeypatch):
    """The keyword index judges every file but the binary and the 'secret'; the embedder embeds every chunk."""
    left_out = []

    def lexical(root):
        db = sqlite3.connect(root / STORE_REL)
        db.executescript("CREATE TABLE IF NOT EXISTS lexical_file (path TEXT PRIMARY KEY, blob TEXT NOT NULL, indexed INTEGER NOT NULL);"
                         "CREATE TABLE IF NOT EXISTS lexical_chunk (id INTEGER PRIMARY KEY, chunk_id TEXT NOT NULL UNIQUE, "
                         "path TEXT NOT NULL, start_line INTEGER NOT NULL, end_line INTEGER NOT NULL, parent_id TEXT NOT NULL);"
                         "DELETE FROM lexical_file; DELETE FROM lexical_chunk;")
        listing = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, env=ENV).stdout.split()
        for rel in listing:
            if rel in left_out or rel.startswith("governance/adoption/"):
                continue
            state = 0 if rel in ("blob.bin", "cfg.env") else 1
            db.execute("INSERT INTO lexical_file VALUES (?, 'b', ?)", (rel, state))
            if state:
                db.execute("INSERT INTO lexical_chunk (chunk_id, path, start_line, end_line, parent_id) VALUES (?, ?, 1, 1, 'p')",
                           (f"c-{rel}", rel))
        db.commit()
        db.close()
        return {"digest": "x", "indexed": []}

    def semantic(root):
        db = sqlite3.connect(root / STORE_REL)
        db.executescript("CREATE TABLE IF NOT EXISTS semantic_vector (chunk_id TEXT PRIMARY KEY, embedding BLOB NOT NULL);"
                         "DELETE FROM semantic_vector;")
        db.execute("INSERT INTO semantic_vector SELECT chunk_id, x'00' FROM lexical_chunk")
        db.commit()
        db.close()
        return {"available": True}

    monkeypatch.setattr("gov.retrieval.lexical.refresh", lexical)
    monkeypatch.setattr("gov.retrieval.semantic.refresh", semantic)
    monkeypatch.setattr("gov.codeintel.index", lambda root: None)
    monkeypatch.setattr(fabric, "search", lambda root, question: {"evidence": [{"path": "a.md"}, {"path": "main.py"}]})
    return left_out


def run_a9(root, out, decision=(), questions=None, budget_ms=None):
    args = argparse.Namespace(session="s", out=str(out), decision=list(decision), questions=questions,
                              budget_ms=budget_ms)
    tracked = {line.split("\t")[1]: line.split()[2] for line in subprocess.run(
        ["git", "-C", str(root), "ls-tree", "-r", "HEAD"], capture_output=True, text=True, env=ENV).stdout.splitlines()}
    return fabric.a9(stages.Run(root, args, CONFIG, "A9", tracked, {}, {}))


def test_the_record_holds_each_store_the_four_digests_the_standard_and_the_audit_records(tmp_path, stand_ins):
    root, out = planted(tmp_path), tmp_path / "out"
    asked = tmp_path / "questions.yaml"
    asked.write_text(yaml.safe_dump({"form": "w2-88-questions/1", "questions": [
        {"id": "q1", "question": "what is the answer", "gold": ["a.md"]},
        {"id": "q2", "question": "where is the thing", "gold": ["nowhere.md"], "forbidden": ["main.py"]}]}))
    result = run_a9(root, out, questions=str(asked))
    tracked = set(subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True,
                                 env=ENV).stdout.split())
    assert result["ok"] is True and result["record"] == "governance/adoption/A9-memory-fabric.md"
    head = yaml.safe_load((root / result["record"]).read_text().split("---\n")[1])
    assert set(head["stores"]) == {"record", "lexical", "vectors", "codegraph"}
    for store in ("lexical", "vectors"):
        assert {"judged", "indexed", "refused", "chunks", "vectors", "nodes", "edges", "seconds",
                "peak_rss_bytes"} <= set(head["stores"][store])
    lexical = head["stores"]["lexical"]
    named = set(lexical["indexed"]) | {item["path"] for item in lexical["refused"]}
    assert named == {rel for rel in tracked if not rel.startswith("governance/adoption/")}  # indexed or named
    assert {item["path"]: item["reason"] for item in lexical["refused"]} == {"blob.bin": "binary", "cfg.env": "secrets"}
    assert set(head["digests"]) == {"record", "lexical", "vectors", "codegraph_bytes"}
    standard = head["standard"]
    assert {"reranker", "reranker_service", "pool", "bundle_tokens", "widen", "gov_pin", "embedder",
            "retrieval_yaml_sha256", "departures"} <= set(standard) and standard["departures"] == []
    assert head["scale"]["budget_ms"] == fabric.RETRIEVE_BUDGET_MS and "routes" in head["scale"]
    measure = head["measure"]
    assert measure["hit_at_5"] == 50.0 and measure["right_e2e"] == 50.0 and measure["wrong_claims"] == 1
    assert {"name": "q2", "cause": "forbidden path in the first five"} in measure["residuals"]
    assert head["refresh"]["command"].startswith("gov rebuild --integration")
    audit = out / "memory-audit"
    assert (audit / "AUDIT-RECORD.json").is_file() and (audit / "ACT-WALLS/ACT.md").is_file()
    assert sorted(p.stem for p in (audit / "briefs").iterdir()) == ["auditor", "checker", "writer"]
    assert json.loads((audit / "AUDIT-RECORD.json").read_text())["due"] == "not due: no verdict set used"
    assert set(head["cost"]) >= {"tokens", "usd", "gpu_minutes", "owner_minutes", "replace_after"}
    assert not (out / "SCALE-PROPOSAL.md").exists()


def test_a_tracked_file_in_neither_list_makes_the_stage_not_ok(tmp_path, stand_ins):
    root, out = planted(tmp_path), tmp_path / "out"
    stand_ins.append("main.py")  # the keyword index leaves it out of both lists
    with pytest.raises(GovError) as raised:
        run_a9(root, out)
    assert raised.value.code == "FABRIC_INCOMPLETE" and raised.value.details["missing"] == ["main.py"]
    assert not (root / "governance/adoption").exists()  # a refusal writes no record


def test_check_coverage_names_the_missing_file_and_digests_are_checked():
    off = {"requested": False}
    record = {"stores": {"lexical": {"indexed": ["a"], "refused": [{"path": "b", "reason": "binary"}]},
                         "vectors": off, "codegraph": off}}
    fabric.check_coverage(record, ["a", "b"])
    with pytest.raises(GovError) as raised:
        fabric.check_coverage(record, ["a", "b", "c"])
    assert raised.value.code == "FABRIC_INCOMPLETE" and raised.value.details["missing"] == ["c"]
    with pytest.raises(GovError) as unbuilt:  # a store the path map calls for, absent from the record
        fabric.check_coverage({"stores": {"lexical": record["stores"]["lexical"], "codegraph": off}}, ["a", "b"])
    assert unbuilt.value.code == "FABRIC_INCOMPLETE" and unbuilt.value.details["not_built"] == ["vectors"]
    with pytest.raises(GovError) as only:
        fabric.check_digests({"digest": "abc"})
    assert only.value.code == "DIGESTS_INCOMPLETE"
    fabric.check_digests({"digests": {"record": "r", "lexical": "l", "vectors": "v", "codegraph_bytes": 0}})


def test_a_setting_other_than_the_standard_is_named_and_not_ok_without_a_decision(tmp_path, stand_ins):
    pool_off = yaml.safe_load(SHIPPED)
    pool_off["pool"]["meaning_uncut"] = False
    bad = yaml.safe_dump({**pool_off, "rerank": {"service": "private"}, "bundle": {"tokens": 8000}})
    root = planted(tmp_path, retrieval=bad)
    with pytest.raises(GovError) as raised:
        run_a9(root, tmp_path / "out")
    assert raised.value.code == "STANDARD_DEPARTURE"
    assert set(raised.value.details["settings"]) == {"pool", "reranker_service", "bundle_tokens"}
    done = run_a9(root, tmp_path / "out", decision=["DEC-1099"])
    head = yaml.safe_load((root / done["record"]).read_text().split("---\n")[1])
    assert {item["setting"]: item["decision"] for item in head["standard"]["departures"]} == {
        "pool": "DEC-1099", "reranker_service": "DEC-1099", "bundle_tokens": "DEC-1099"}


def test_a_figure_over_the_budget_writes_a_proposal_and_changes_no_store_file(tmp_path, stand_ins, monkeypatch):
    root, out = planted(tmp_path), tmp_path / "out"

    def slow(where, question, refresh=False, top_k=None):
        time.sleep(0.02)
        return {}

    monkeypatch.setattr("gov.retrieval.semantic.search", slow)
    done = run_a9(root, out, budget_ms=1)
    assert (out / "SCALE-PROPOSAL.md").is_file() and done["over"]
    before = (root / STORE_REL).read_bytes()
    fabric.proposal(out, done["over"], {"x": 1})
    assert (root / STORE_REL).read_bytes() == before
    head = yaml.safe_load((root / done["record"]).read_text().split("---\n")[1])
    assert head["measure"]["hit_at_5"] is None and head["measure"]["residuals"][0]["name"] == "questions"
