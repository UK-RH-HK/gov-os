"""W2-88 run 4, L-1: a binary over the chunker's limit has no route (S2's blocker) and the estimate counts the chunks the
keyword index will make, binaries included (S1's estimated index time). The engineer's own tests, on planted repositories."""

import math
import os
import subprocess

from gov.adopt import assess, refactor_plan
from gov.retrieval import chunking

ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t"}
MIB = 1 << 20


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, env=ENV).stdout


def repo_with_binary(tmp_path, name, size):
    """One tracked binary of ``size`` bytes (a NUL byte in its first 8,000) and one small clean source file."""
    repo = tmp_path / name
    (repo / "assets").mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "main.py").write_text("print('hi')\n")
    (repo / "assets/big.bin").write_bytes(b"\0" + b"\x01\x02\x03\x04" * ((size - 1) // 4) + b"\x05" * ((size - 1) % 4))
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "init")
    return repo


def test_a_binary_over_the_limit_is_in_binary_and_no_route_and_the_plan_proposes_over_limit(tmp_path):
    repo = repo_with_binary(tmp_path, "big", 2 * MIB)
    result = assess.assess(repo, tmp_path / "out")
    assert [item["path"] for item in result["binary"]] == ["assets/big.bin"]
    assert {"path": "assets/big.bin", "reason": "over-limit"} in result["no_route"]
    made = refactor_plan.plan(result, None, tmp_path / "plan")
    assert [item["kind"] for item in made["proposals"]] == ["over-limit"]
    ticket = (tmp_path / "plan/refactor-plan" / made["proposals"][0]["file"].rsplit("/", 1)[-1]).read_text()
    assert "assets/big.bin" in ticket
    assert not (tmp_path / "plan/refactor-plan/NOTHING-TO-REFACTOR.md").exists() and made["nothing"] is False


def test_a_binary_at_or_under_the_limit_is_only_in_binary_and_gets_no_proposal(tmp_path):
    for name, size in (("small", 4096), ("edge", assess.FILE_LIMIT_BYTES)):
        repo = repo_with_binary(tmp_path, name, size)
        result = assess.assess(repo, tmp_path / f"out-{name}")
        assert [item["path"] for item in result["binary"]] == ["assets/big.bin"]
        assert all(item["path"] != "assets/big.bin" for item in result["no_route"])
        assert refactor_plan.plan(result, None, tmp_path / f"plan-{name}")["proposals"] == []


def test_a_text_file_over_the_limit_or_with_a_long_line_stays_over_limit(tmp_path):
    repo = repo_with_binary(tmp_path, "text", 4096)
    (repo / "huge.txt").write_text("x\n" * (assess.FILE_LIMIT_BYTES // 2 + 1))
    (repo / "long.txt").write_text("y" * (assess.LINE_LIMIT + 1) + "\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "more")
    result = assess.assess(repo, tmp_path / "out")
    over = {item["path"] for item in result["no_route"] if item["reason"] == "over-limit"}
    assert over == {"huge.txt", "long.txt"}


def test_a_link_is_no_file_over_the_limit_and_makes_no_chunks(tmp_path):
    repo = repo_with_binary(tmp_path, "link", 4096)
    os.symlink("x" * 2000, repo / "ln")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "link")
    result = assess.assess(repo, tmp_path / "out")
    assert all(item["path"] != "ln" for item in result["no_route"])
    sizes = [(repo / "main.py").stat().st_size, (repo / "assets/big.bin").stat().st_size]
    assert result["estimate"]["chunks"] == sum(math.ceil(size / assess.CHUNK_STEP) for size in sizes)


def test_the_estimate_counts_the_chunks_binaries_included(tmp_path):
    assert assess.CHUNK_STEP == chunking.MAX_CHARS - chunking.OVERLAP_CHARS == 1080
    assert assess.EMBED_S_PER_CHUNK == 0.04
    big = assess.assess(repo_with_binary(tmp_path, "big", 2 * MIB), tmp_path / "out-big")
    small = assess.assess(repo_with_binary(tmp_path, "small", 4096), tmp_path / "out-small")
    assert big["estimate"]["chunks"] - small["estimate"]["chunks"] >= 2 * MIB / 1200
    assert big["estimate"]["chunks"] == math.ceil(2 * MIB / 1080) + 1
    assert big["estimate"]["index_seconds"] > small["estimate"]["index_seconds"]
    code_files = 1  # main.py
    assert big["estimate"]["index_seconds"] == round(big["estimate"]["chunks"] * assess.EMBED_S_PER_CHUNK
                                                     + code_files * assess.GRAPH_S_PER_FILE)
