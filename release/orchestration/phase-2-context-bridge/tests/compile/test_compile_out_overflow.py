"""BR-DAG-AMEND-R1-20 (REPAIR-1 node R1-RA's second pass, after R1-GA3 merged): ``govbridge compile --out DIR``
now PERSISTS the overflow artifacts R1-GA3's own ``compile_packet`` already returns --
``result["supplementary_packets"]``/``result["evidence_notes"]``, both keyed by query id -- under
``DIR/supplementary/<query_id>/`` (R1-RS's own on-disk packet shape: manifest.json/packet.md/task_spec.yaml/
meta.json) and ``DIR/notes/<query_id>.yaml``. ``govbridge packet verify DIR`` covers them (missing, extra or
mismatched -> FAIL); ``govbridge receipt check`` requires the receipt to acknowledge them, reusing R1-RS's own
supplementary coverage.

This is a REAL-RETRIEVAL test (a from-clean-built store, real lexical route), not a re-test of
``compile_packet``'s own return value -- ``tests/compile/test_overflow_notes.py`` (R1-GA3) already proves that
with a fake route; this file proves the CLI actually WRITES what compile_packet hands it. Every id/term here is
``RAOV-*``/``raoverflowterm``, unrelated to Review-8/Phase-2 (OC-BR-02).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from govbridge import cli
from govbridge.core import freshness as freshnessmod
from govbridge.core import store as storemod

OVERFLOW_PATH = "src/raov_overflow_fixture.txt"
OVERFLOW_TERM = "raoverflowterm"
N_PARAGRAPHS = 16


def _git(root: Path, *args: str) -> None:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")


def _commit_overflow_fixture(fixture_repo) -> str:
    """Enough real, chunkable text (govbridge.core.chunking's own 1200-char chunks) that a byte-tiny H budget
    genuinely cannot hold it all -- every paragraph repeats the SAME distinctive term so a real lexical (FTS5)
    search ranks every chunk similarly and a generous target_items retrieves all of them."""
    paragraphs = [
        f"Paragraph {i} of the {OVERFLOW_TERM} fixture: " + ("filler content word " * 20)
        for i in range(N_PARAGRAPHS)
    ]
    text = "\n\n".join(paragraphs) + "\n"
    path = fixture_repo.root / OVERFLOW_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    _git(fixture_repo.root, "add", "-A")
    _git(fixture_repo.root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q",
         "-m", "RAOV overflow fixture: many chunkable paragraphs")
    _git(fixture_repo.root, "branch", "-f", "product", "HEAD")
    _git(fixture_repo.root, "branch", "-f", "evidence", "HEAD")
    return text


def _write_facets(tmp_path: Path, target_items: int) -> str:
    p = tmp_path / "raov-facets.yaml"
    p.write_text(f"""schema: govbridge-facets/1
default_batch_size: {target_items}
default_target_items: {target_items}
default_max_rounds: 3
default_threads: 1
facets:
  raov:
    routes: [lexical]
    scope_classes: null
    lifecycle_scope: null
    extra_terms: []
    min_share: 0.1
    target_items: {target_items}
class_facets: {{}}
""", encoding="utf-8")
    return str(p)


def _write_budgets(tmp_path: Path, h_cap_bytes: int, name: str = "raov-tiny") -> str:
    h_cap_kb = max(h_cap_bytes / 1024, 0.01)
    p = tmp_path / f"{name}.yaml"
    p.write_text(f"""schema: govbridge-budgets/1
rrf_k: 60
graph_neighbour_depth: 1
parent_expansion_top_n: 3
max_slice_chars: 1600
per_item_cap_kb: 24
section_header_bytes: 64
profiles:
  {name}:
    total_kb: 50
    section_caps_kb: {{A: null, B: 1, C: 1, D: 1, E: 1, F: 1, G: 1, H: {h_cap_kb}, I: 3, J: 3}}
    g_fanout: {{}}
gather:
  max_items_per_query: 5000
  max_bytes_per_query: 20000000
  wall_time_budget_seconds: 60
""", encoding="utf-8")
    return str(p)


def _task_spec_path(tmp_path: Path, view_path: str, budget_profile: str) -> str:
    spec = {
        "schema": "govbridge-task-spec/1", "task_id": "T-RAOV", "role": "test",
        "objective": "BR-DAG-AMEND-R1-20 fixture: force an evidence overflow through real retrieval",
        "view": view_path, "required_inputs": [], "seeds": [],
        "queries": [{"id": "RAOV-Q1", "text": f"{OVERFLOW_TERM} filler content", "routes": ["lexical"]}],
        "mutation_scope": [], "prohibitions": [], "required_checks": [],
        "completion_vocabulary": ["ANSWERED"], "budget_profile": budget_profile,
    }
    p = tmp_path / "raov-task-spec.yaml"
    p.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return str(p)


@pytest.fixture()
def raov_built(fixture_repo, view_path, registry_path, tmp_path):
    """A real, from-clean-built store over the shared fixture repo PLUS the RAOV overflow content, and a tiny
    facets/budgets pair that makes a real lexical retrieval of it genuinely overflow. Returns
    ``{fixture_repo, view_path, registry_path, task_spec_path, facets_path, budgets_path, rules_path}``."""
    _commit_overflow_fixture(fixture_repo)
    rules_path = str(fixture_repo.root / "config" / "corpus-rules.yaml")
    r = freshnessmod.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root), from_clean=True)
    assert r["trigger"] == "FULL"

    facets_path = _write_facets(tmp_path, target_items=N_PARAGRAPHS + 5)
    budgets_path = _write_budgets(tmp_path, h_cap_bytes=1200)
    task_spec_path = _task_spec_path(tmp_path, view_path, "raov-tiny")
    return {
        "fixture_repo": fixture_repo, "view_path": view_path, "registry_path": registry_path,
        "task_spec_path": task_spec_path, "facets_path": facets_path, "budgets_path": budgets_path,
        "rules_path": rules_path,
    }


def _compile_argv(rb: dict, out_dir: Path) -> list:
    return [
        "compile", rb["task_spec_path"], "--out", str(out_dir), "--repo", str(rb["fixture_repo"].root),
        "--registry", rb["registry_path"], "--budgets", rb["budgets_path"], "--facets-path", rb["facets_path"],
    ]


def _packet_verify_argv(rb: dict, out_dir: Path) -> list:
    return ["packet", "verify", str(out_dir), "--repo", str(rb["fixture_repo"].root),
            "--registry", rb["registry_path"], "--budgets", rb["budgets_path"]]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_compile(rb: dict, out_dir: Path) -> dict:
    rc = cli.main(_compile_argv(rb, out_dir))
    assert rc in (0, 1)  # STATUS_BLOCKED_BUDGET (a tiny H cap may legitimately block) is not this test's concern
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    return meta


def test_overflow_actually_happens_in_this_fixture(raov_built, tmp_path):
    """Sanity precondition, checked directly (R1-T2 rule 3: an independent, second-method confirmation) before
    trusting any test below that assumes it: the tiny H budget really did drop some, but not all, of the real
    lexically-retrieved chunks for RAOV-Q1."""
    out_dir = tmp_path / "precondition"
    meta = _run_compile(raov_built, out_dir)
    assert meta["overflow_query_ids"] == ["RAOV-Q1"], meta
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    overflow_notices = [n for n in manifest["notices"] if n["type"] == "EVIDENCE_OVERFLOW"]
    assert len(overflow_notices) == 1
    assert overflow_notices[0]["overflow_item_count"] > 0, "the fixture never actually overflowed -- tune it"
    # second, independent confirmation: grep the rendered packet.md for RAOV chunk markers directly, rather than
    # trusting only the code under test's own notices list.
    rendered = (out_dir / "packet.md").read_text(encoding="utf-8")
    kept_mentions = rendered.count(OVERFLOW_TERM)
    assert kept_mentions < N_PARAGRAPHS, (
        f"packet.md mentions {OVERFLOW_TERM!r} {kept_mentions} times -- expected fewer than the {N_PARAGRAPHS} "
        f"paragraphs that exist, i.e. some were genuinely dropped, not merely absent from a bad query"
    )


def test_compile_out_writes_supplementary_and_notes(raov_built, tmp_path):
    out_dir = tmp_path / "written"
    meta = _run_compile(raov_built, out_dir)
    qids = meta["overflow_query_ids"]
    assert qids, "no overflow at all -- nothing to test"

    for qid in qids:
        supp_dir = out_dir / "supplementary" / qid
        assert (supp_dir / "manifest.json").is_file()
        assert (supp_dir / "packet.md").is_file()
        assert (supp_dir / "task_spec.yaml").is_file()
        supp_meta = json.loads((supp_dir / "meta.json").read_text(encoding="utf-8"))
        assert supp_meta["packet_kind"] == "supplementary"

        manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
        notice = next(n for n in manifest["notices"] if n["type"] == "EVIDENCE_OVERFLOW" and n["query_id"] == qid)
        if notice.get("note_id"):
            note_path = out_dir / "notes" / f"{qid}.yaml"
            assert note_path.is_file()
            note = yaml.safe_load(note_path.read_text(encoding="utf-8"))
            assert note["note_id"] == notice["note_id"]
            assert note["claims"] or note["unresolved"]


def test_packet_verify_passes_on_a_freshly_written_overflow_packet(raov_built, tmp_path):
    out_dir = tmp_path / "verify_pass"
    _run_compile(raov_built, out_dir)
    rc = cli.main(_packet_verify_argv(raov_built, out_dir))
    assert rc == 0


def test_packet_verify_fails_when_a_supplementary_packet_is_tampered(raov_built, tmp_path):
    out_dir = tmp_path / "verify_tamper_supp"
    meta = _run_compile(raov_built, out_dir)
    qid = meta["overflow_query_ids"][0]
    packet_md = out_dir / "supplementary" / qid / "packet.md"
    original = packet_md.read_text(encoding="utf-8")
    packet_md.write_text(original + "\ntampered line, never part of the original render\n", encoding="utf-8")

    rc = cli.main(_packet_verify_argv(raov_built, out_dir))
    assert rc == 1


def test_packet_verify_fails_when_a_note_is_deleted(raov_built, tmp_path):
    out_dir = tmp_path / "verify_delete_note"
    meta = _run_compile(raov_built, out_dir)
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    noted_qids = [n["query_id"] for n in manifest["notices"]
                  if n["type"] == "EVIDENCE_OVERFLOW" and n.get("note_id")]
    assert noted_qids, "the fixture never produced a note -- tune it (a groundable overflow item is needed)"
    note_path = out_dir / "notes" / f"{noted_qids[0]}.yaml"
    assert note_path.is_file()
    note_path.replace(out_dir / "notes" / f"{noted_qids[0]}.yaml.moved-aside")  # never rm; move aside instead

    rc = cli.main(_packet_verify_argv(raov_built, out_dir))
    assert rc == 1


def test_packet_verify_fails_when_a_supplementary_packet_is_extra(raov_built, tmp_path):
    out_dir = tmp_path / "verify_extra_supp"
    meta = _run_compile(raov_built, out_dir)
    qid = meta["overflow_query_ids"][0]
    extra_dir = out_dir / "supplementary" / f"{qid}-NOT-A-REAL-QUERY"
    src = out_dir / "supplementary" / qid
    extra_dir.mkdir(parents=True)
    for name in ("manifest.json", "packet.md", "task_spec.yaml", "meta.json"):
        extra_dir.joinpath(name).write_text((src / name).read_text(encoding="utf-8"), encoding="utf-8")

    rc = cli.main(_packet_verify_argv(raov_built, out_dir))
    assert rc == 1


def test_receipt_check_requires_overflow_supplementary_acknowledgement(raov_built, tmp_path):
    out_dir = tmp_path / "receipt"
    meta = _run_compile(raov_built, out_dir)
    qids = meta["overflow_query_ids"]
    assert qids

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    a_rows = manifest["sections"]["A"]["items"]

    def _receipt_doc(include_overflow: bool) -> dict:
        supp_hashes, supp_manifest_hashes = [], []
        if include_overflow:
            for qid in qids:
                supp_meta = json.loads((out_dir / "supplementary" / qid / "meta.json").read_text(encoding="utf-8"))
                supp_hashes.append(supp_meta["packet_sha256"])
                supp_manifest_hashes.append(supp_meta["manifest_sha256"])
        return {
            "context_packet_hash": [manifest["packet_sha256"], *supp_hashes],
            "manifest_sha256": [manifest["manifest_sha256"], *supp_manifest_hashes],
            "read_tokens": {}, "inputs_consumed": [f"{r['unit']['id']}@{r['content_sha256']}" for r in a_rows],
            "items_relied_on": [], "external_reads": [], "outputs_produced": "x", "decisions_applied": [],
            "acceptance_evidence": [], "deviations": [], "unresolved": [],
        }

    receipt_path = tmp_path / "receipt-without-overflow.yaml"
    receipt_path.write_text(yaml.safe_dump(_receipt_doc(include_overflow=False), sort_keys=False), encoding="utf-8")
    rc = cli.main(["receipt", "check", "--packet", str(out_dir), "--receipt", str(receipt_path),
                    "--repo", str(raov_built["fixture_repo"].root), "--registry", raov_built["registry_path"],
                    "--budgets", raov_built["budgets_path"]])
    assert rc == 1, "a receipt that never acknowledges the overflow supplementary packet must fail"

    receipt_path2 = tmp_path / "receipt-with-overflow.yaml"
    receipt_path2.write_text(yaml.safe_dump(_receipt_doc(include_overflow=True), sort_keys=False), encoding="utf-8")
    rc2 = cli.main(["receipt", "check", "--packet", str(out_dir), "--receipt", str(receipt_path2),
                     "--repo", str(raov_built["fixture_repo"].root), "--registry", raov_built["registry_path"],
                     "--budgets", raov_built["budgets_path"]])
    assert rc2 == 0, "a receipt that DOES acknowledge every overflow supplementary packet must pass"


def test_compiling_twice_gives_byte_identical_directories(raov_built, tmp_path):
    out_dir_1 = tmp_path / "twice_1"
    out_dir_2 = tmp_path / "twice_2"
    _run_compile(raov_built, out_dir_1)
    _run_compile(raov_built, out_dir_2)

    files_1 = sorted(p.relative_to(out_dir_1).as_posix() for p in out_dir_1.rglob("*") if p.is_file())
    files_2 = sorted(p.relative_to(out_dir_2).as_posix() for p in out_dir_2.rglob("*") if p.is_file())
    assert files_1 == files_2
    assert files_1, "nothing was written at all"

    for rel in files_1:
        b1 = (out_dir_1 / rel).read_bytes()
        b2 = (out_dir_2 / rel).read_bytes()
        assert b1 == b2, f"{rel} differs between two compiles of the same inputs"


def test_compile_and_verify_leave_a_read_only_store_unchanged(raov_built, tmp_path):
    store_dir = storemod.store_root()
    db_path = storemod.db_path(store_dir)
    before_sha = _sha256_file(db_path)

    out_dir = tmp_path / "readonly"
    import os
    os.chmod(db_path, 0o444)
    os.chmod(store_dir, 0o555)
    try:
        meta = _run_compile(raov_built, out_dir)
        assert meta["overflow_query_ids"]
        rc = cli.main(_packet_verify_argv(raov_built, out_dir))
        assert rc == 0
    finally:
        os.chmod(store_dir, 0o755)
        os.chmod(db_path, 0o644)

    after_sha = _sha256_file(db_path)
    assert after_sha == before_sha, "compile --out or packet verify wrote to the store file"
