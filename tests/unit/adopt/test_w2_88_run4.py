"""W2-88 run 4: review round 1's findings (RV1-1 to RV1-8) and the decided package P-W2-88-B-1 (B-1.1 to B-1.5), as
the engineer's own unit tests (stand-ins for the embedder, the keyword index and the code graph)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import time
from pathlib import Path

import pytest
import yaml

from gov.adopt import assess, fabric, refactor_plan, stages
from gov.cli.errors import GovError
from gov.store import STORE_REL

from .test_w2_88_fabric import CONFIG, ENV, SHIPPED, git, planted, stand_ins  # noqa: F401  (stand_ins is a fixture)

GOV_OS = Path(fabric.__file__).resolve().parents[3]
TOKEN = "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8"
SHIPPED_POOL = fabric.STANDARD["pool"]
WITH_GRAPH = {"path-map.yaml": {**CONFIG["path-map.yaml"], "capabilities": {"code_intelligence": {"enabled": True}}}}


def run_a9(root, out, decision=(), questions=None, budget_ms=None, with_code_graph=False):
    args = argparse.Namespace(session="s", out=str(out), decision=list(decision), questions=questions,
                              budget_ms=budget_ms)
    tracked = {line.split("\t")[1]: line.split()[2] for line in subprocess.run(
        ["git", "-C", str(root), "ls-tree", "-r", "HEAD"], capture_output=True, text=True, env=ENV).stdout.splitlines()}
    return fabric.a9(stages.Run(root, args, WITH_GRAPH if with_code_graph else CONFIG, "A9", tracked, {}, {}))


def stage_code_files(monkeypatch):
    """A code graph stand-in that copies every code-looking tracked file to its staging folder, as the tool does."""
    from gov import codeintel

    def index(root):
        listed = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, env=ENV).stdout.split()
        for rel in listed:
            if Path(rel).suffix in (".py", ".cob"):
                target = root / codeintel.BASE_REL / "files" / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((root / rel).read_text())

    monkeypatch.setattr(codeintel, "index", index)


def tree_status(root):
    """``git status --porcelain`` but for the store's own folder (the planted repositories have no .gitignore)."""
    lines = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
                           capture_output=True, text=True).stdout.splitlines()
    return "\n".join(line for line in lines if ".gov-runtime/" not in line)


def head_of(root, result):
    return yaml.safe_load((root / result["record"]).read_text().split("---\n")[1])


# ---- RV1-1 / B-1.4: the pool is the whole block as Gov OS ships it

def test_a_pool_block_that_differs_in_any_key_is_a_departure_with_its_value():
    assert fabric.departures({"pool": dict(SHIPPED_POOL)}) == []
    for change in ({"route_depth": 5}, {"drop_nested": False}, {"extra_key": 1}):
        block = {**SHIPPED_POOL, **change}
        assert fabric.departures({"pool": block}) == [{"setting": "pool", "value": block}]
    missing = {key: value for key, value in SHIPPED_POOL.items() if key != "rerank_depth"}
    assert fabric.departures({"pool": missing}) == [{"setting": "pool", "value": missing}]
    assert fabric.departures({"pool": {"meaning_uncut": True}})[0]["setting"] == "pool"
    assert fabric.departures({}) == [{"setting": "pool", "value": False}]
    assert fabric.departures({"pool": {**SHIPPED_POOL, "meaning_uncut": False}}) == [{"setting": "pool", "value": False}]


def test_a_tuned_pool_is_not_ok_without_a_decision_through_a9(tmp_path, stand_ins):
    tuned = yaml.safe_load(SHIPPED)
    tuned["pool"]["route_depth"] = 5
    root = planted(tmp_path, retrieval=yaml.safe_dump(tuned))
    with pytest.raises(GovError) as raised:
        run_a9(root, tmp_path / "out")
    assert raised.value.code == "STANDARD_DEPARTURE" and raised.value.details["settings"] == ["pool"]
    done = run_a9(root, tmp_path / "out", decision=["DEC-1:pool"])
    assert head_of(root, done)["standard"]["departures"][0]["decision"] == "DEC-1"


# ---- B-1.2: the reranker and the bundle are the pin's constants

def test_settings_are_read_from_the_pins_constants(monkeypatch):
    from gov.retrieval import rerank, retrieve

    held = fabric.settings_of({"pool": dict(SHIPPED_POOL)})
    assert held == {"reranker": "Qwen3-Reranker-0.6B", "reranker_service": "shared", "pool": SHIPPED_POOL,
                    "bundle_tokens": retrieve.BUNDLE_BUDGET, "widen": "sections"}
    assert fabric.departures({"pool": dict(SHIPPED_POOL)}) == []
    monkeypatch.setattr(rerank, "MODEL", "Org/Other-Reranker")
    monkeypatch.setattr(rerank, "SOCKET", "private.sock")
    monkeypatch.setattr(retrieve, "BUNDLE_BUDGET", 4000)
    found = {item["setting"]: item["value"] for item in fabric.departures({"pool": dict(SHIPPED_POOL)})}
    assert found == {"reranker": "Other-Reranker", "reranker_service": f"{rerank.CACHE_REL}/private.sock",
                     "bundle_tokens": 4000}


def test_a_changed_constant_is_a_departure_that_a_decision_names(tmp_path, monkeypatch):
    from gov.retrieval import rerank, retrieve

    root = planted(tmp_path)
    for attr, value, setting in (("MODEL", "Org/Other-Reranker", "reranker"), ("SOCKET", "private.sock", "reranker_service"),
                                 ("BUNDLE_BUDGET", 4000, "bundle_tokens")):
        with monkeypatch.context() as patch:
            patch.setattr(retrieve if attr == "BUNDLE_BUDGET" else rerank, attr, value)
            with pytest.raises(GovError) as raised:
                fabric.read_standard(root, [])
            assert raised.value.code == "STANDARD_DEPARTURE" and raised.value.details["settings"] == [setting]
            for decision in (["DEC-1"], [f"DEC-1:{setting}"]):
                block = fabric.read_standard(root, decision)
                assert [item["decision"] for item in block["departures"]] == ["DEC-1"]


def test_a_retrieval_yaml_with_a_rerank_or_bundle_key_is_refused_even_with_a_decision(tmp_path, stand_ins):
    for key in ("rerank", "bundle"):
        doc = {**yaml.safe_load(SHIPPED), key: {"model": "x", "tokens": 1}}
        root = planted(tmp_path / key, retrieval=yaml.safe_dump(doc))
        for decisions in ([], ["DEC-1099"]):
            with pytest.raises(GovError) as raised:
                run_a9(root, tmp_path / "out", decision=decisions)
            assert raised.value.code == "CONFIG_INVALID" and raised.value.details["keys"] == [key]
            assert key in raised.value.message
        assert not (root / STORE_REL).exists()  # refused before any store is built


# ---- RV1-2: a vector scan that did not run

def test_an_unavailable_or_failed_vector_scan_is_null_with_its_reason_and_no_proposal(tmp_path, stand_ins, monkeypatch):
    for number, reply in enumerate(({"available": False, "reason": "FACET_UNAVAILABLE: planted"}, {}, RuntimeError("down"))):
        def scan(root, question, reply=reply):
            if isinstance(reply, Exception):
                raise reply
            time.sleep(0.02)
            return reply

        with monkeypatch.context() as patch:
            patch.setattr(fabric, "vector_scan", scan)
            root, out = planted(tmp_path / str(number)), tmp_path / f"out{number}"
            done = run_a9(root, out, budget_ms=1)
        found = head_of(root, done)["scale"]
        assert found["vector_scan_ms"] is None and found["vector_scan_reason"]
        if isinstance(reply, Exception):
            assert "RuntimeError" in found["vector_scan_reason"]
        elif reply:
            assert "planted" in found["vector_scan_reason"]
        assert not (out / "SCALE-PROPOSAL.md").exists() and done["over"] == []


def test_an_available_vector_scan_over_the_budget_is_a_figure_and_a_proposal(tmp_path, stand_ins, monkeypatch):
    def scan(root, question):
        time.sleep(0.02)
        return {"available": True, "reason": None, "hits": []}

    monkeypatch.setattr(fabric, "vector_scan", scan)
    root, out = planted(tmp_path), tmp_path / "out"
    done = run_a9(root, out, budget_ms=1)
    found = head_of(root, done)["scale"]
    assert found["vector_scan_ms"] >= 20 and found["vector_scan_reason"] is None
    assert (out / "SCALE-PROPOSAL.md").is_file() and any("vector scan" in line for line in done["over"])


def test_only_the_vector_scan_is_compared_with_the_budget_and_the_envelope_still_writes_a_proposal():
    envelope = {**assess.ENVELOPE, "nodes_found": 0, "edges_found": 0, "peak_rss_bytes_found": 0}
    routes = {"lexical": 5000.0, "semantic": 5000.0, "retrieve": 9000.0}
    assert fabric.over({"routes": routes, "vector_scan_ms": None, "budget_ms": 1, "envelope": envelope}) == []
    over = fabric.over({"routes": routes, "vector_scan_ms": None, "budget_ms": 1,
                        "envelope": {**envelope, "nodes_found": assess.ENVELOPE["nodes"] + 1}})
    assert len(over) == 1 and "nodes" in over[0]


# ---- B-1.5 / RV1-3: the secrets scan did not run

def secret_repo(tmp_path):
    repo = tmp_path / "secret"
    repo.mkdir()
    git(repo, "init", "-q")
    (repo / "cfg.env").write_text("TOKEN=" + TOKEN + "\n")
    (repo / "main.py").write_text("print('hi')\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "init")
    return repo


def ma(repo, out, config=None):
    args = argparse.Namespace(stage="MA", out=str(out), session="s")
    return stages.run(repo, args, config or {})


def test_without_gitleaks_ma_writes_the_plan_but_never_nothing_to_refactor(tmp_path, monkeypatch):
    repo, out = secret_repo(tmp_path), tmp_path / "out"
    before = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True).stdout
    monkeypatch.setenv("PATH", "/usr/bin:/bin")  # git, and no gitleaks
    with pytest.raises(GovError) as raised:
        stages.run(repo, argparse.Namespace(stage="MA", out=str(out), session="s"), {})
    assert raised.value.code == "SECRETS_UNSCANNED"
    assert set(raised.value.details) >= {"reason", "unscanned"} and "gitleaks" in raised.value.details["reason"]
    assert (out / "memory-assessment.json").is_file()
    assert not (out / "refactor-plan/NOTHING-TO-REFACTOR.md").exists()
    plan = (out / "refactor-plan/PLAN.md").read_text()
    assert "secrets: not scanned (" in plan and "all 2 tracked files" in plan
    everything = "".join(path.read_text(errors="ignore") for path in out.rglob("*") if path.is_file())
    assert TOKEN not in everything
    assert subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True).stdout == before


def test_blobs_over_the_scan_limit_make_the_plan_name_them_unscanned(tmp_path, monkeypatch):
    repo, out = secret_repo(tmp_path), tmp_path / "out"
    (repo / "long.txt").write_text("y" * 200)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "more")
    monkeypatch.setattr(assess, "SCAN_LIMIT_BYTES", 100)
    with pytest.raises(GovError) as raised:
        ma(repo, out)
    assert raised.value.code == "SECRETS_UNSCANNED" and raised.value.details["unscanned"] == ["long.txt"]
    plan = (out / "refactor-plan/PLAN.md").read_text()
    assert "secrets: not scanned (" in plan and "long.txt" in plan
    assert not (out / "refactor-plan/NOTHING-TO-REFACTOR.md").exists()


def test_a_scanned_clean_repository_still_says_nothing_to_refactor(tmp_path):
    repo = tmp_path / "clean"
    repo.mkdir()
    git(repo, "init", "-q")
    (repo / "a.py").write_text("x = 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "clean")
    result = ma(repo, tmp_path / "out")
    assert result["proposals"] == 0 and (tmp_path / "out/refactor-plan/NOTHING-TO-REFACTOR.md").is_file()


def test_the_plan_alone_never_calls_an_unscanned_assessment_clean(tmp_path):
    made = refactor_plan.plan({"secrets_scanned": False, "secrets": [], "secrets_unscanned": [],
                               "paths": ["a", "b"], "secrets_unscanned_reason": "planted"}, None, tmp_path)
    assert not (tmp_path / "refactor-plan/NOTHING-TO-REFACTOR.md").exists() and made["nothing"] is False
    assert "secrets: not scanned (planted)" in (tmp_path / "refactor-plan/PLAN.md").read_text()


# ---- RV1-8: the no-route rule

def test_a_code_suffix_the_graph_does_not_read_is_no_route_unsupported_language(tmp_path):
    repo = tmp_path / "other"
    repo.mkdir()
    git(repo, "init", "-q")
    for name in ("a.vue", "b.ps1", "c.proto", "d.svelte", "e.cob", "f.py"):
        (repo / name).write_text("x\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "init")
    held = assess.assess(repo, tmp_path / "out")["no_route"]
    assert {item["path"] for item in held if item["reason"] == "unsupported-language"} == {
        "a.vue", "b.ps1", "c.proto", "d.svelte", "e.cob"}
    assert {".vue", ".ps1", ".proto", ".svelte", ".cob"} <= assess.OTHER_CODE_SUFFIXES
    assert not assess.OTHER_CODE_SUFFIXES & assess.CODE_GRAPH_SUFFIXES


# ---- RV1-4: binaries the store holds

def test_a_binary_the_lexical_store_chunked_is_indexed_and_named_held_never_refused(tmp_path, stand_ins, monkeypatch):
    def lexical(root):  # this index chunks the binary as text (as the real one does) and refuses only the secret
        db = sqlite3.connect(root / STORE_REL)
        db.executescript("CREATE TABLE IF NOT EXISTS lexical_file (path TEXT PRIMARY KEY, blob TEXT NOT NULL, indexed INTEGER NOT NULL);"
                         "CREATE TABLE IF NOT EXISTS lexical_chunk (id INTEGER PRIMARY KEY, chunk_id TEXT NOT NULL UNIQUE, "
                         "path TEXT NOT NULL, start_line INTEGER NOT NULL, end_line INTEGER NOT NULL, parent_id TEXT NOT NULL);"
                         "DELETE FROM lexical_file; DELETE FROM lexical_chunk;")
        for rel in subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, env=ENV).stdout.split():
            if rel.startswith("governance/adoption/"):
                continue
            state = 0 if rel == "cfg.env" else 1
            db.execute("INSERT INTO lexical_file VALUES (?, 'b', ?)", (rel, state))
            if state:
                db.execute("INSERT INTO lexical_chunk (chunk_id, path, start_line, end_line, parent_id) VALUES (?, ?, 1, 1, 'p')",
                           (f"c-{rel}", rel))
        db.commit()
        db.close()
        return {"digest": "x", "indexed": []}

    monkeypatch.setattr("gov.retrieval.lexical.refresh", lexical)
    root = planted(tmp_path)
    head = head_of(root, run_a9(root, tmp_path / "out"))
    for store in ("lexical", "vectors"):
        block = head["stores"][store]
        assert "blob.bin" in block["indexed"] and block["binary_held"] == ["blob.bin"]
        assert "blob.bin" not in {item["path"] for item in block["refused"]}
    assert {item["path"]: item["reason"] for item in head["stores"]["lexical"]["refused"]} == {"cfg.env": "secrets"}


def test_a_binary_the_store_did_not_take_stays_refused_binary(tmp_path, stand_ins):
    root = planted(tmp_path)
    block = head_of(root, run_a9(root, tmp_path / "out"))["stores"]["lexical"]
    assert {"path": "blob.bin", "reason": "binary"} in block["refused"] and block["binary_held"] == []


# ---- RV1-5: the code graph

def test_a_code_graph_that_cannot_be_read_is_not_built_and_the_stage_not_ok(tmp_path, stand_ins, monkeypatch):
    from gov import codeintel

    def broken(root):
        raise RuntimeError("the graph tool is gone")

    stage_code_files(monkeypatch)
    monkeypatch.setattr(codeintel, "_graph", broken)
    root = planted(tmp_path)
    with pytest.raises(GovError) as raised:
        run_a9(root, tmp_path / "out", with_code_graph=True)
    assert raised.value.code == "FABRIC_INCOMPLETE" and "codegraph" in raised.value.details["not_built"]
    assert "the graph tool is gone" in raised.value.message


def test_check_coverage_names_a_codegraph_that_was_not_built():
    off = {"requested": False}
    lexical = {"indexed": ["a"], "refused": []}
    with pytest.raises(GovError) as raised:
        fabric.check_coverage({"stores": {"lexical": lexical, "vectors": off,
                                          "codegraph": {"built": False, "error": "x", "judged": 0, "indexed": [],
                                                        "refused": []}}}, ["a"])
    assert raised.value.code == "FABRIC_INCOMPLETE" and raised.value.details["not_built"] == ["codegraph"]


def test_a_file_the_graph_does_not_read_is_refused_unsupported_language_never_indexed(tmp_path, stand_ins, monkeypatch):
    from gov import codeintel

    root = planted(tmp_path)
    (root / "old.cob").write_text("IDENTIFICATION DIVISION.\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "cobol")
    stage_code_files(monkeypatch)
    monkeypatch.setattr(codeintel, "_graph", lambda r: ({"a": 1, "b": 2}, {"a": [("b", "calls")]}))
    stage = head_of(root, run_a9(root, tmp_path / "out", with_code_graph=True))["stores"]["codegraph"]
    assert {"path": "old.cob", "reason": "unsupported-language"} in stage["refused"]
    assert "old.cob" not in stage["indexed"] and "main.py" in stage["indexed"]
    assert stage["nodes"] == 2 and stage["edges"] == 1


# ---- B-1.1 / B-1.3: the copy step

KERNEL = (("template/governance/kernel/skills/retrieval", ".claude/skills/retrieval"),
          ("template/governance/kernel/skills/discovery", ".claude/skills/discovery"))
TEMPLATES = (("template/governance/kernel/templates/brief.md", "governance/kernel/templates/brief.md"),
             ("template/governance/kernel/templates/role-cto.md", "governance/kernel/templates/role-cto.md"))


def expected_copies():
    found = {}
    for source, target in KERNEL:
        for file in sorted((GOV_OS / source).rglob("*")):
            if file.is_file():
                found[f"{target}/{file.relative_to(GOV_OS / source).as_posix()}"] = file
    for source, target in TEMPLATES:
        found[target] = GOV_OS / source
    return found


def test_a9_installs_the_kernel_files_byte_for_byte_in_its_own_commit_and_records_them(tmp_path, stand_ins):
    root = planted(tmp_path, retrieval=SHIPPED)
    (root / "governance/project/retrieval.yaml").unlink()
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "no retrieval.yaml")
    before = subprocess.run(["git", "-C", str(root), "rev-list", "--count", "HEAD"], capture_output=True, text=True).stdout
    done = run_a9(root, tmp_path / "out")  # a fresh adoption: no retrieval.yaml and no decision is ok
    assert done["ok"] is True
    after = subprocess.run(["git", "-C", str(root), "rev-list", "--count", "HEAD"], capture_output=True, text=True).stdout
    assert int(after) == int(before) + 1  # one commit holds the copies and the record
    wanted = expected_copies()
    for rel, source in wanted.items():
        assert (root / rel).read_bytes() == source.read_bytes()
    assert (root / "governance/project/retrieval.yaml").read_bytes() == (GOV_OS / "governance/project/retrieval.yaml").read_bytes()
    head = head_of(root, done)
    paths = {item["path"]: item for item in head["installed"]}
    assert set(paths) == {*wanted, "governance/project/retrieval.yaml"} and head["kept"] == []
    for rel, item in paths.items():
        source = wanted.get(rel) or GOV_OS / "governance/project/retrieval.yaml"
        assert item["sha256"] == hashlib.sha256((root / rel).read_bytes()).hexdigest()
        assert item["from"] == source.relative_to(GOV_OS).as_posix()
    assert done["installed"] == head["installed"]
    changed = subprocess.run(["git", "-C", str(root), "show", "--name-only", "--format=", "HEAD"], capture_output=True,
                             text=True).stdout.split()
    assert set(changed) == {*paths, done["record"]}
    assert head["standard"]["departures"] == [] and head["standard"]["retrieval_yaml_sha256"]
    assert tree_status(root) == ""


def test_a_repositorys_own_retrieval_yaml_is_kept_and_judged(tmp_path, stand_ins):
    own = yaml.safe_load(SHIPPED)
    own["pool"]["rerank_depth"] = 10
    root = planted(tmp_path, retrieval=yaml.safe_dump(own))
    own_bytes = (root / "governance/project/retrieval.yaml").read_bytes()
    with pytest.raises(GovError) as raised:
        run_a9(root, tmp_path / "out")
    assert raised.value.code == "STANDARD_DEPARTURE"
    done = run_a9(root, tmp_path / "out", decision=["DEC-1099"])
    assert (root / "governance/project/retrieval.yaml").read_bytes() == own_bytes
    head = head_of(root, done)
    assert head["kept"] == [{"path": "governance/project/retrieval.yaml", "sha256": hashlib.sha256(own_bytes).hexdigest()}]
    assert "governance/project/retrieval.yaml" not in {item["path"] for item in head["installed"]}


def test_a_refusal_leaves_no_copy_in_the_tree(tmp_path, stand_ins):
    root = planted(tmp_path)
    stand_ins.append("main.py")  # the keyword index leaves it out: FABRIC_INCOMPLETE after the copies were written
    with pytest.raises(GovError) as raised:
        run_a9(root, tmp_path / "out")
    assert raised.value.code == "FABRIC_INCOMPLETE"
    for rel in expected_copies():
        assert not (root / rel).exists()
    assert not (root / ".claude").exists() and not (root / "governance/kernel").exists()
    assert tree_status(root) == ""
    assert not (root / "governance/adoption").exists()


def test_the_copies_are_in_place_before_the_build(tmp_path, stand_ins, monkeypatch):
    seen = []
    original = stand_ins  # the fixture patched lexical.refresh: wrap it
    import gov.retrieval.lexical as lexical

    inner = lexical.refresh

    def watching(root):
        seen.append(all((root / rel).is_file() for rel in expected_copies()))
        return inner(root)

    monkeypatch.setattr(lexical, "refresh", watching)
    root = planted(tmp_path)
    run_a9(root, tmp_path / "out")
    assert seen == [True]


# ---- run 4 after the designer's revision: a route that raised has a time, a stale proposal goes, held records are listed

def test_a_raising_route_still_has_its_time_and_a_stale_proposal_is_not_this_runs(tmp_path, stand_ins, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    (out / "SCALE-PROPOSAL.md").write_text("an earlier run's proposal\n")

    def down(root, question):
        raise RuntimeError("down")

    monkeypatch.setattr(fabric, "vector_scan", down)
    root = planted(tmp_path)
    done = run_a9(root, out, budget_ms=1)
    found = head_of(root, done)["scale"]
    assert all(isinstance(value, float) for value in found["routes"].values()) and found["vector_scan_ms"] is None
    assert not (out / "SCALE-PROPOSAL.md").exists()


def test_a_file_the_store_holds_outside_the_path_map_is_listed_indexed(tmp_path, stand_ins):
    root = planted(tmp_path)
    run_a9(root, tmp_path / "out")  # the first run's record is a tracked file the second run's store holds
    import gov.retrieval.lexical as lexical

    def with_records(where):  # a keyword index that holds the adoption's own records too
        db = sqlite3.connect(where / STORE_REL)
        db.executescript("CREATE TABLE IF NOT EXISTS lexical_file (path TEXT PRIMARY KEY, blob TEXT NOT NULL, indexed INTEGER NOT NULL);"
                         "CREATE TABLE IF NOT EXISTS lexical_chunk (id INTEGER PRIMARY KEY, chunk_id TEXT NOT NULL UNIQUE, "
                         "path TEXT NOT NULL, start_line INTEGER NOT NULL, end_line INTEGER NOT NULL, parent_id TEXT NOT NULL);"
                         "DELETE FROM lexical_file; DELETE FROM lexical_chunk;")
        for rel in subprocess.run(["git", "-C", str(where), "ls-files"], capture_output=True, text=True, env=ENV).stdout.split():
            state = 0 if rel in ("blob.bin", "cfg.env") else 1
            db.execute("INSERT INTO lexical_file VALUES (?, 'b', ?)", (rel, state))
            if state:
                db.execute("INSERT INTO lexical_chunk (chunk_id, path, start_line, end_line, parent_id) VALUES (?, ?, 1, 1, 'p')",
                           (f"c-{rel}", rel))
        db.commit()
        db.close()
        return {"digest": "x", "indexed": []}

    import pytest as _pytest
    patch = _pytest.MonkeyPatch()
    patch.setattr(lexical, "refresh", with_records)
    try:
        done = run_a9(root, tmp_path / "out2")
    finally:
        patch.undo()
    block = head_of(root, done)["stores"]["lexical"]
    assert "governance/adoption/A9-memory-fabric.md" in block["indexed"]
