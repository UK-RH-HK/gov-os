"""REPAIR_DAG.yaml node R1-INT (run BR-AR-0028, handoff BR-HO-0028): the integration audit's HERMETIC checks,
encoded as tests. Real-view checks stay as evidence runs under ``EVIDENCE/repair-1/``; everything here runs on
self-contained synthetic fixture repositories and a private, per-test store.

Audit-only: this file never fixes anything. A check whose CORRECT behaviour the integrated tree does not have is
encoded as ``pytest.mark.xfail(strict=True)`` naming the defect id recorded in ``EVIDENCE/repair-1/INT-VERDICT.yaml``
-- the suite stays green, the defect stays visible, and the day an owner node repairs it the strict xfail turns
into an XPASS failure, forcing whoever repairs it to remove the marker and keep the assertion as a regression test.

Every id below is synthetic (``HR-*``, ``QA-*``, ``SYN-*``) and unrelated to Review-8/Phase-2 (OC-BR-02). The
synthetic oracle for check 6 is built here from the PUBLIC schema/checker only (ARCHITECTURE/schemas/oracle.yaml,
DEMONSTRATION/oracle-tools/check_oracle.py -- BR-HO-0028's one secrecy exception); it is passed its own synthetic
``--queries`` and ``--state``, so no public demonstration query text is ever read.

Hermeticity (template amendment R1-T1): every test passes ``repo=`` explicitly, never chdirs, pins its own view,
and runs against its own ``GOVBRIDGE_STORE`` (set, never only deleted -- check 11's own rule).
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import pytest
import yaml

DOMAIN = Path(__file__).resolve().parents[2]
FIXTURES_COMPILE = DOMAIN / "tests" / "fixtures" / "compile"
if str(FIXTURES_COMPILE) not in sys.path:
    sys.path.insert(0, str(FIXTURES_COMPILE))

import compile_repobuilder as cxrb  # noqa: E402  (tests/fixtures/compile/compile_repobuilder.py)

from govbridge.compile import packet as packetmod  # noqa: E402
from govbridge.compile import supplementary as suppmod  # noqa: E402
from govbridge.compile import validate as validatemod  # noqa: E402
from govbridge.core import taskctx as taskctxmod  # noqa: E402
from govbridge.route.router import FAKE_ROUTES  # noqa: E402

BRIDGE_STATE_PATH = "release/orchestration/phase-2-context-bridge/ORCHESTRATOR_STATE.yaml"


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    """Check 11's own rule, applied to this file: SET a private store (never only delenv), and a private telemetry
    home, so nothing here can read or write the machine-wide default store."""
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "isolated-store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "isolated-home"))
    monkeypatch.delenv("GOVBRIDGE_TASK", raising=False)


# ---------------------------------------------------------------------------------------------------------------
# helpers: a tiny git fixture repository with a primary ref, an optional product ref and history refs
# ---------------------------------------------------------------------------------------------------------------

def _git(root: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")
    return r.stdout.strip()


def _commit(root: Path, msg: str) -> str:
    _git(root, "add", "-A")
    _git(root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", msg)
    return _git(root, "rev-parse", "HEAD")


def _write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _state(items: list) -> str:
    out = ["schema: bridge-orchestrator-state/1\n", "mandatory_bridge_inputs:\n", "  items:\n"]
    for item_id, path in items:
        out += [f"  - id: {item_id}\n", "    class: OWNER_DECISION\n", f"    path: {path}\n"]
    return "".join(out)


REGISTRY = ("schema: govbridge-authority-registry/1\npurpose: minimal synthetic registry (R1-INT)\n"
            "section_anchors: []\nunanchored_lines_rule: []\nsupersessions: []\nlifecycle_overrides: []\n"
            "class_rules:\n  - {glob: '**', class: UNCLASSIFIED}\n")


def _task_spec(view_path: str, **extra) -> dict:
    ts = {"schema": "govbridge-task-spec/1", "task_id": "T-R1INT", "role": "test", "objective": "R1-INT audit",
          "view": view_path,
          "required_inputs": [{"state_ref": "state:bridge#mandatory_bridge_inputs.items[*]", "reason": "test"}],
          "seeds": [], "queries": [], "mutation_scope": [], "prohibitions": [], "required_checks": [],
          "completion_vocabulary": ["ANSWERED", "PARTIAL", "BLOCKED"], "budget_profile": "bounded-builder"}
    ts.update(extra)
    return ts


def _history_repo(tmp_path: Path, mandatory_on_history: bool, product_partition: bool = True):
    """records (primary) + product (a DISTINCT commit) + history refs refs/heads/hist/*. When
    ``mandatory_on_history``, a second mandatory owner record lives ONLY on the history ref, under a path whose
    partition's fallback chain ends in ``history`` -- the ARCHITECTURE.md section 1.2 shape ("a path found only
    there is HISTORY_ONLY")."""
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "records")
    _write(root, "config/corpus-rules.yaml",
           "schema: govbridge-corpus-rules/1\nrules:\n- {id: INCLUDED, effect: INCLUDE, match: {}}\n")
    _write(root, "spec/hr/HR-0001.md", "# HR-0001 -- a record on the primary ref\n\nbody\n")
    hist_path = "prod/HR-0002.md" if product_partition else "spec/hist/HR-0002.md"
    items = [("HR-0001", "spec/hr/HR-0001.md")] + ([("HR-0002", hist_path)] if mandatory_on_history else [])
    _write(root, BRIDGE_STATE_PATH, _state(items))
    _commit(root, "records")
    _git(root, "checkout", "-q", "-b", "product")
    _write(root, "prod/other.md", "a product-only file\n")
    _commit(root, "product")
    _git(root, "checkout", "-q", "-b", "hist/one", "records")
    _write(root, hist_path, "# HR-0002 -- present ONLY on a history ref\n\nv1\n")
    _commit(root, "history v1")
    _git(root, "checkout", "-q", "records")
    view = tmp_path / "view.yaml"
    if product_partition:
        parts = ("partitions:\n"
                 "  - {name: prod, paths: ['prod/**'], owner: product, fallback: [history]}\n"
                 "  - {name: records, paths: ['**'], owner: records, fallback: [product, history]}\n")
    else:
        parts = "partitions:\n  - {name: records, paths: ['**'], owner: records, fallback: [product, history]}\n"
    view.write_text("schema: govbridge-canonical-view/1\nview_id: r1int-hist\nrefs:\n"
                    "  - {name: records, ref: refs/heads/records, follow: tip, role: primary}\n"
                    "  - {name: product, ref: refs/heads/product, follow: tip, role: product}\n"
                    "  - {name: history, ref_glob: refs/heads/hist/*, follow: tip, role: history}\n" + parts,
                    encoding="utf-8")
    reg = tmp_path / "reg.yaml"
    reg.write_text(REGISTRY, encoding="utf-8")
    return root, str(view), str(reg), hist_path


def _move_history_ref(root: Path, hist_path: str) -> None:
    _git(root, "checkout", "-q", "hist/one")
    _write(root, hist_path, "# HR-0002 -- present ONLY on a history ref\n\nv2 CHANGED after the compile\n")
    _commit(root, "history v2")
    _git(root, "checkout", "-q", "records")


# ---------------------------------------------------------------------------------------------------------------
# Check 12: history refs in `packet verify` (R1-RM's open issue: pinned_view_from_manifest does not pin history)
# ---------------------------------------------------------------------------------------------------------------

def test_c12_verify_survives_a_history_ref_move_when_section_a_does_not_use_history(tmp_path):
    root, view, reg, hist_path = _history_repo(tmp_path, mandatory_on_history=False)
    ts = _task_spec(view)
    res = packetmod.compile_packet(ts, routes=FAKE_ROUTES, repo=str(root), registry_path=reg)
    assert res["status"] == packetmod.STATUS_OK
    assert validatemod.verify_packet(res["manifest"], ts, repo=str(root), registry_path=reg,
                                     rendered=res["rendered"]) == []
    _move_history_ref(root, hist_path)
    assert validatemod.verify_packet(res["manifest"], ts, repo=str(root), registry_path=reg,
                                     rendered=res["rendered"]) == []


def test_c12_a_history_fallback_mandatory_item_compiles_into_section_a(tmp_path):
    """The premise of the next test: the resolver DOES reach a history ref through a partition's fallback chain,
    so a compiled packet's section A can depend on a history commit."""
    root, view, reg, _ = _history_repo(tmp_path, mandatory_on_history=True)
    ts = _task_spec(view)
    res = packetmod.compile_packet(ts, routes=FAKE_ROUTES, repo=str(root), registry_path=reg)
    assert res["status"] == packetmod.STATUS_OK
    a = {r["unit"]["id"]: r["source"]["commit"] for r in res["manifest"]["sections"]["A"]["items"]}
    hist_commit = _git(root, "rev-parse", "refs/heads/hist/one")
    assert a.get("HR-0002") == hist_commit
    # ...and the manifest's recorded view names NO history commit an independent verifier could pin:
    assert hist_commit not in {row["commit"] for row in res["manifest"]["view"]}


@pytest.mark.xfail(strict=True, reason="INT-D05: validate.pinned_view_from_manifest rebuilds the view with "
                   "history=[] and the manifest records no history commits, so a packet whose section A resolved "
                   "through a history fallback FAILS packet verify even before any ref moves (owner R1-RM)")
def test_c12_a_history_fallback_packet_is_reverifiable_before_and_after_the_history_ref_moves(tmp_path):
    root, view, reg, hist_path = _history_repo(tmp_path, mandatory_on_history=True)
    ts = _task_spec(view)
    res = packetmod.compile_packet(ts, routes=FAKE_ROUTES, repo=str(root), registry_path=reg)
    assert res["status"] == packetmod.STATUS_OK
    assert validatemod.verify_packet(res["manifest"], ts, repo=str(root), registry_path=reg,
                                     rendered=res["rendered"]) == []
    _move_history_ref(root, hist_path)
    assert validatemod.verify_packet(res["manifest"], ts, repo=str(root), registry_path=reg,
                                     rendered=res["rendered"]) == []


@pytest.mark.xfail(strict=True, reason="INT-D06: view.ResolvedView.classify_occurrence returns CANONICAL (with "
                   "canonical_blob=None) for a path ABSENT at the owner whenever the queried commit IS the owner "
                   "commit, so the resolver (which always queries the records commit) never walks the records "
                   "partition's own fallback chain [product, evidence, history] (owner R1-RM/R1-XC; view.py)")
def test_c12_records_partition_fallback_reaches_history_for_a_mandatory_input(tmp_path):
    root, view, reg, _ = _history_repo(tmp_path, mandatory_on_history=True, product_partition=False)
    res = packetmod.compile_packet(_task_spec(view), routes=FAKE_ROUTES, repo=str(root), registry_path=reg)
    assert res["status"] == packetmod.STATUS_OK, res["resolve_result"].blocked_reasons


# ---------------------------------------------------------------------------------------------------------------
# Check 6: a SYNTHETIC bound-mode oracle, `govbridge demo grade`, and GD-7
# ---------------------------------------------------------------------------------------------------------------

SYN_STAGES = [f"stage_{i:02d}" for i in range(1, 12)]  # 11 synthetic stage names (the checker reads them from --queries)


def _syn_queries_doc() -> dict:
    return {"schema": "govbridge-demonstration-queries/1", "chain_stages": SYN_STAGES, "queries": [
        {"id": "SYN-CHAIN-1", "kind": "chain", "text": "synthetic chain one"},
        {"id": "SYN-CHAIN-2", "kind": "chain", "text": "synthetic chain two"},
        {"id": "SYN-SBS", "kind": "side_by_side", "text": "synthetic side by side"},
        {"id": "SYN-BW", "kind": "both_ways", "text": "synthetic both ways"},
        {"id": "SYN-Q1", "kind": "query_class", "class": "QC-A", "subject": "S1", "text": "synthetic query"},
        {"id": "SYN-CTL", "kind": "control", "text": "synthetic control"},
    ]}


def _anchor(record_id: str, commit: str, path: str, **extra) -> dict:
    return {"kind": "record", "commit": commit, "path": path, "record_id": record_id, **extra}


def _syn_oracle(commit: str) -> dict:
    """A bound-mode oracle over the compile fixture's own records (CX-*): every must_state entry is a
    ``{fact, binding}`` mapping -- stage facts bound to their own stage, query facts bound to ``query``."""
    disp = cxrb.DISPOSITION_PATH
    a_rec = _anchor("CX-0010A", commit, disp)
    b_rec = _anchor("CX-0010B", commit, disp)
    trap = _anchor("CX-0001", commit, cxrb.DECISION_A_PATH, why="an upstream representation (synthetic)")

    def chain(qid: str) -> dict:
        stages = []
        for i, name in enumerate(SYN_STAGES):
            enforcement = (i == 5)
            stages.append({
                "stage": name, "required": i < 2 or enforcement, "is_enforcement_point": enforcement,
                "anchors": {"any_of": [a_rec]},
                "must_state": [{"fact": f"fact bound to {name}", "binding": name}],
                "traps": [trap] if enforcement else [], "wrong": [],
            })
        return {"query_id": qid, "stages": stages, "acceptable_alternative_enforcement_points": [],
                "effective_behaviour": {"subject": "s", "attribute": "a", "before": "b", "after": "c",
                                        "evidence": a_rec}}

    return {
        "schema": "govbridge-oracle/1", "oracle_id": "SYN-ORACLE-R1INT",
        "author": {"run_id": "BR-AR-0028", "role": "test-author", "model_observed": "synthetic"},
        "commits": {"product": commit, "records": commit, "evidence": commit},
        "written_from": [a_rec], "line_tolerance": 3,
        "chains": [chain("SYN-CHAIN-1"), chain("SYN-CHAIN-2")],
        "side_by_side": {"query_id": "SYN-SBS", "shared_points": [a_rec], "differing_points": [b_rec]},
        "f1_both_ways": {"query_id": "SYN-BW", "purpose_anchors": [a_rec],
                         "consumer_anchors": [dict(b_rec, process="in", production=True)]},
        "queries": [{"query_id": "SYN-Q1", "required": ["CX-0010A"], "forbidden": [],
                     "must_state": [{"fact": "a query-level fact", "binding": "query"}]}],
        "authority_expectations": [
            {"item": "CX-0010A", "sections": ["A"], "class": "OWNER_DECISION"},
            {"item": "CX-0010B", "sections": ["A"], "class": "OWNER_DECISION"},
        ],
        "controls": [{"query_id": "SYN-CTL", "required": ["CX-0010B"], "forbidden": [],
                      "must_state": [{"fact": "a control fact", "binding": "query"}]}],
    }


def _syn_state() -> dict:
    return {"mandatory_bridge_inputs": {"authority_classes": {"OWNER_DECISION": "binding"},
                                        "items": [{"id": "CX-0010A", "class": "OWNER_DECISION"},
                                                  {"id": "CX-0010B", "class": "OWNER_DECISION"}]}}


def _syn_answers() -> dict:
    """Stage_01's claim states stage_01's fact; stage_02's claim states stage_03's fact (so D-2 scoping must judge
    stage_03's fact ABSENT from stage_03's own claim, even though the chain as a whole contains the text)."""
    def chain(qid):
        stages = []
        for name in SYN_STAGES:
            claim = {"stage_01": "fact bound to stage_01 is here",
                     "stage_02": "this claim carries the fact bound to stage_03 text"}.get(name, "")
            stages.append({"stage": name, "claim": claim, "citations": [{"item_id": "CX-0010A"}]})
        return {"query_id": qid, "status": "ANSWERED", "stages": stages, "answer_text": ""}
    return {"run_id": "SYN-RUN", "packets_used": [], "answers": [
        chain("SYN-CHAIN-1"), chain("SYN-CHAIN-2"),
        {"query_id": "SYN-SBS", "shared_points": [{"item_id": "CX-0010A"}],
         "differing_points": [{"item_id": "CX-0010B"}], "classification": "NOT_DETERMINED_BY_BRIDGE"},
        {"query_id": "SYN-BW", "citations": [{"item_id": "CX-0010A"}, {"item_id": "CX-0010B"}],
         "disposition": "NONE_STATED"},
        {"query_id": "SYN-Q1", "status": "ANSWERED", "answer_text": "a query-level fact",
         "citations": [{"item_id": "CX-0010A"}]},
        {"query_id": "SYN-CTL", "status": "ANSWERED", "answer_text": "x", "citations": [{"item_id": "CX-0010B"}]},
    ]}


def _compile_fixture_packet(tmp_path: Path):
    repo = cxrb.build(tmp_path / "cxrepo")
    view = tmp_path / "cx-view.yaml"
    cxrb.write_canonical_view(view, repo)
    reg = tmp_path / "cx-reg.yaml"
    cxrb.write_registry(reg)
    ts = _task_spec(str(view))
    ts_path = tmp_path / "cx-task.yaml"
    ts_path.write_text(yaml.safe_dump(ts, sort_keys=False), encoding="utf-8")
    out = tmp_path / "main-packet"
    from govbridge import cli
    with contextlib.redirect_stdout(io.StringIO()):
        rc = cli.main(["compile", str(ts_path), "--fake-routes", "--registry", str(reg), "--repo", str(repo.root),
                       "--out", str(out)])
    assert rc == 0
    return repo, ts, out, reg


def _write_synthetic_grading_inputs(tmp_path: Path, commit: str) -> dict:
    paths = {}
    for name, doc in (("oracle", _syn_oracle(commit)), ("queries", _syn_queries_doc()), ("state", _syn_state()),
                      ("answers", _syn_answers())):
        p = tmp_path / f"syn-{name}.yaml"
        p.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
        paths[name] = str(p)
    return paths


def _check_oracle(paths: dict) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(DOMAIN / "DEMONSTRATION" / "oracle-tools" / "check_oracle.py"),
                           paths["oracle"], "--queries", paths["queries"], "--state", paths["state"],
                           "--require-binding"], capture_output=True, text=True)


def test_c6_synthetic_bound_oracle_passes_check_oracle_require_binding(tmp_path):
    repo = cxrb.build(tmp_path / "cxrepo")
    paths = _write_synthetic_grading_inputs(tmp_path, repo.c2)
    r = _check_oracle(paths)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "binding mode: BOUND" in r.stdout and "RESULT: VALID" in r.stdout
    assert "unbound 0" in r.stdout


def test_c6_demo_grade_scopes_stage_facts_per_d2_and_leaves_query_facts_pending(tmp_path):
    repo, ts, out, reg = _compile_fixture_packet(tmp_path)
    paths = _write_synthetic_grading_inputs(tmp_path, repo.c2)
    assert _check_oracle(paths).returncode == 0
    from govbridge.demo import grade as grademod
    report = grademod.grade(paths["oracle"], paths["answers"], None, [str(out)], queries_path=paths["queries"],
                            repo=str(repo.root))
    chain = report["gates"]["G4_chains"]["chains"][0]
    by_stage = {s["stage"]: s for s in chain["stages"]}
    # D-2: a stage-bound fact is judged against ITS OWN stage's claim only.
    assert by_stage["stage_01"]["must_state"][0]["present"] is True
    assert by_stage["stage_03"]["must_state"][0]["present"] is False  # the text sits in stage_02's claim
    assert by_stage["stage_03"]["must_state"][0]["binding"] == "stage_03"
    assert all(m["must_state_ok"] == grademod.PENDING_RUBRIC for s in chain["stages"] for m in s["must_state"])
    # query-bound facts: PENDING_RUBRIC (never a silent PASS/FAIL without the rubric).
    q = report["gates"]["G5_query_classes"]["per_query"][0]
    assert q["must_state_ok"] == grademod.PENDING_RUBRIC
    assert report["gates"]["G1_packet_validity"]["result"] == "PASS"


def test_c6_demo_grade_cli_runs_end_to_end_without_crashing(tmp_path):
    repo, ts, out, reg = _compile_fixture_packet(tmp_path)
    paths = _write_synthetic_grading_inputs(tmp_path, repo.c2)
    from govbridge import cli
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cli.main(["demo", "grade", "--oracle", paths["oracle"], "--answers", paths["answers"],
                       "--packet", str(out), "--queries", paths["queries"], "--repo", str(repo.root)])
    report = json.loads(buf.getvalue())
    assert rc in (0, 1, 3) and report["verdict"].startswith("DEMONSTRATION_")


def _supplementary_packet(tmp_path: Path, ts: dict, commit: str) -> Path:
    hit = {"unit_id": "SUPP-REC-1", "unit_kind": "record", "route": "lexical", "rank": 1, "delivery": "RETRIEVED",
           "occurrences": [{"ref": "records", "commit": commit, "path": cxrb.LEDGER_PATH,
                            "version_status": "CANONICAL", "line_start": 1, "line_end": 2}],
           "text": "a retrieved line", "authority_class": "EVIDENCE", "lifecycle": "ACTIVE", "edge_path": [],
           "tier": None, "resolution": None}
    result = {"text": "q", "routes": ["lexical"], "hits_by_route": {"lexical": [hit]}, "fused": [],
              "excluded_hits": 0}
    built = suppmod.build_supplementary_packet("search", result, ts)
    d = tmp_path / "supp-packet"
    suppmod.write_supplementary_packet(str(d), built, ts)
    return d


def test_c6_cli_packet_verify_accepts_the_supplementary_packet(tmp_path):
    """Control for the next test: the supplementary packet itself IS valid by the CLI's own verifier."""
    repo, ts, out, reg = _compile_fixture_packet(tmp_path)
    supp = _supplementary_packet(tmp_path, ts, repo.c2)
    from govbridge import cli
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cli.main(["packet", "verify", str(supp), "--repo", str(repo.root)])
    assert rc == 0 and json.loads(buf.getvalue())["verify"] == "PASS"


@pytest.mark.xfail(strict=True, reason="INT-D01: govbridge.demo.grade.grade_g1/grade_g2 run the MAIN-packet "
                   "validator (validate.verify_packet / receipt.check) on every --packet, ignoring meta.json's "
                   "packet_kind; on a supplementary packet (no recorded view) this raises ValueError (\"canonical-view "
                   "has no ref named 'records'\") -- the grader crashes on exactly the input D-5/G1 require it to "
                   "grade (owner R1-RG)")
def test_c6_demo_grade_handles_a_supplementary_packet(tmp_path):
    repo, ts, out, reg = _compile_fixture_packet(tmp_path)
    supp = _supplementary_packet(tmp_path, ts, repo.c2)
    paths = _write_synthetic_grading_inputs(tmp_path, repo.c2)
    from govbridge.demo import grade as grademod
    report = grademod.grade(paths["oracle"], paths["answers"], None, [str(out), str(supp)],
                            queries_path=paths["queries"], repo=str(repo.root))
    assert report["gates"]["G1_packet_validity"]["result"] == "PASS"


@pytest.mark.xfail(strict=True, reason="INT-D02: grade_g7 sums packet.md only for the --packet directories it is "
                   "given; the overflow supplementary packets `compile --out` writes under DIR/supplementary/<qid>/ "
                   "(BR-DAG-AMEND-R1-20) are never discovered, so G7 under-counts D-5 packet bytes unless each is "
                   "passed explicitly -- which INT-D01 makes crash (owner R1-RG)")
def test_c6_g7_counts_the_overflow_supplementary_packets_of_a_main_packet_dir(tmp_path):
    repo, ts, out, reg = _compile_fixture_packet(tmp_path)
    supp_root = out / "supplementary" / "SYN-Q"
    supp_root.parent.mkdir(parents=True, exist_ok=True)
    real = _supplementary_packet(tmp_path, ts, repo.c2)
    supp_root.mkdir()
    for f in real.iterdir():
        (supp_root / f.name).write_bytes(f.read_bytes())
    from govbridge.demo import grade as grademod
    packets = [grademod._load_packet_dir(str(out))]
    g7 = grademod.grade_g7(packets, {}, corpus_bytes=10 ** 9, budget_bytes=None, reads=None, repo=str(repo.root))
    main_bytes = (out / "packet.md").stat().st_size
    supp_bytes = (supp_root / "packet.md").stat().st_size
    reported = next((v for k, v in g7.items() if k in ("packet_bytes", "packet_bytes_total")), None)
    assert reported == main_bytes + supp_bytes, g7


def test_c6_gd7_windowed_external_read_is_charged_as_its_window(tmp_path):
    repo = cxrb.build(tmp_path / "cxrepo")
    from govbridge.demo import grade as grademod
    raw = (repo.root / cxrb.LEDGER_PATH).read_bytes()
    receipt_window = {"external_reads": [{"path": cxrb.LEDGER_PATH, "commit": repo.c2, "lines": [1, 2]}]}
    receipt_whole = {"external_reads": [{"path": cxrb.LEDGER_PATH, "commit": repo.c2}]}
    g_w = grademod.grade_g7([], receipt_window, corpus_bytes=10 ** 9, budget_bytes=None, reads=None, repo=str(repo.root))
    g_all = grademod.grade_g7([], receipt_whole, corpus_bytes=10 ** 9, budget_bytes=None, reads=None, repo=str(repo.root))
    window_bytes = sum(len(line) + 1 for line in raw.split(b"\n")[0:2])
    assert g_w["external_read_bytes"] == window_bytes
    assert g_all["external_read_bytes"] == len(raw)


@pytest.mark.xfail(strict=True, reason="INT-D13: grade_g7 enforces 'packet bytes <= 1% of corpus' only `if "
                   "corpus_bytes`; a grading run without --corpus-bytes reports G7 PASS with the 1% check silently "
                   "skipped -- the OBS-BR-05 class of defect (a silently disabled G7 condition), still reachable "
                   "(owner R1-RG)")
def test_c6_g7_never_passes_silently_when_corpus_bytes_is_unknown(tmp_path):
    repo, ts, out, reg = _compile_fixture_packet(tmp_path)
    from govbridge.demo import grade as grademod
    g7 = grademod.grade_g7([grademod._load_packet_dir(str(out))], {}, corpus_bytes=None, budget_bytes=None,
                           reads=None, repo=str(repo.root))
    assert g7["result"] != "PASS" or any("corpus" in p for p in g7["problems"]), g7


# ---------------------------------------------------------------------------------------------------------------
# Check 11: test hermeticity -- every conftest SETS GOVBRIDGE_STORE; no test body drops it
# ---------------------------------------------------------------------------------------------------------------

def _autouse_sets_store(text: str) -> bool:
    """True iff an AUTOUSE fixture in this conftest source calls ``setenv("GOVBRIDGE_STORE", ...)`` -- a setenv
    inside an opt-in fixture (tests/semantic's ``built``) isolates only the tests that request it."""
    import ast
    for fn in ast.walk(ast.parse(text)):
        if not isinstance(fn, ast.FunctionDef):
            continue
        autouse = any(isinstance(d, ast.Call) and any(k.arg == "autouse" and getattr(k.value, "value", False)
                                                      for k in d.keywords) for d in fn.decorator_list)
        if not autouse:
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "setenv" \
                    and node.args and isinstance(node.args[0], ast.Constant) \
                    and node.args[0].value == "GOVBRIDGE_STORE":
                return True
    return False


@pytest.mark.xfail(strict=True, reason="INT-D08: the autouse fixture of tests/authority, tests/core, tests/notes and "
                   "tests/semantic conftest.py only delenv GOVBRIDGE_STORE (never setenv a tmp store); tests/answers, "
                   "tests/gather, tests/integration and tests/route have no conftest at all (owner R1-XC, routed from "
                   "its pass 3)")
def test_c11_every_test_package_sets_a_private_store():
    offenders = []
    for d in sorted(p for p in (DOMAIN / "tests").iterdir() if p.is_dir() and p.name not in ("fixtures", "__pycache__")):
        c = d / "conftest.py"
        if not c.exists() or not _autouse_sets_store(c.read_text(encoding="utf-8")):
            offenders.append(str(c.relative_to(DOMAIN)))
    assert offenders == []


def _store_isolation_breaks() -> list:
    """Every test FUNCTION that calls ``monkeypatch.delenv("GOVBRIDGE_STORE")`` without, in the same function,
    re-pointing the store (``setenv("GOVBRIDGE_STORE", ...)``) or the gov-bridge home (``setenv("GOV_BRIDGE_HOME",
    ...)``, which moves the default store under tmp) -- such a test falls through to the machine-wide default store
    $HOME/.cache/gov-bridge/store/default. Parsed with ``ast`` (a docstring mentioning delenv is not a call)."""
    import ast
    out = []
    for f in sorted((DOMAIN / "tests").rglob("test_*.py")):
        if f.name == Path(__file__).name:
            continue
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            dels, sets = [], set()
            for node in ast.walk(fn):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.args \
                        and isinstance(node.args[0], ast.Constant):
                    if node.func.attr == "delenv" and node.args[0].value == "GOVBRIDGE_STORE":
                        dels.append(node.lineno)
                    if node.func.attr == "setenv":
                        sets.add(node.args[0].value)
            if dels and not ({"GOVBRIDGE_STORE", "GOV_BRIDGE_HOME"} & sets):
                out.append(f"{f.relative_to(DOMAIN)}::{fn.name}:{dels[0]}")
    return out


@pytest.mark.xfail(strict=True, reason="INT-D07: test functions that delenv GOVBRIDGE_STORE in their own body and "
                   "re-point nothing, undoing tests/compile/conftest.py's private store -- three of them "
                   "(test_section_i_and_bootstrap.py x2, test_verify_rendered_body.py x1, all R1-RS) were observed by "
                   "an audit hook opening $HOME/.cache/gov-bridge/store/default/store.db, and on a clean HOME they "
                   "CREATE it; a fourth (test_supplementary.py) is latent (owner R1-RS)")
def test_c11_no_test_body_drops_the_private_store():
    assert _store_isolation_breaks() == []


# ---------------------------------------------------------------------------------------------------------------
# Check 13: the cross-cutting fixes, hermetically
# ---------------------------------------------------------------------------------------------------------------

def test_c13_exclusion_counter_is_exact_under_16_threads():
    counter = taskctxmod.ExclusionCounter()
    per_thread, threads = 20000, 16
    barrier = threading.Barrier(threads)

    def work():
        barrier.wait()
        for _ in range(per_thread):
            counter.bump()

    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)  # force frequent thread switches: the read-modify-write race window, if any
    try:
        ts = [threading.Thread(target=work) for _ in range(threads)]
        for t in ts:
            t.start()
        for t in ts:
            t.join(timeout=120)
    finally:
        sys.setswitchinterval(old)
    assert counter.count == per_thread * threads


def test_c13_repo_root_follows_the_resolved_cwd_in_one_process(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    for r in (a, b):
        r.mkdir()
        _git(r, "init", "-q")
    code = ("import os, sys; from govbridge.core import gitobj; out=[]\n"
            "for d in sys.argv[1:]:\n    os.chdir(d); out.append(gitobj.repo_root())\nprint('|'.join(out))")
    r = subprocess.run([sys.executable, "-c", code, str(a), str(b)], capture_output=True, text=True,
                       cwd=str(DOMAIN), env={**os.environ, "PYTHONPATH": str(DOMAIN)})
    assert r.returncode == 0, r.stderr
    ra, rb = r.stdout.strip().split("|")
    assert Path(ra).resolve() == a.resolve() and Path(rb).resolve() == b.resolve()


@pytest.mark.xfail(strict=True, reason="INT-D10: gather_with_followup discloses a degraded (retry-exhausted) git read "
                   "as telemetry.degraded_git_reads + deterministic:false (BR-DAG-AMEND-R1-22), but compile_packet "
                   "records only stop_reason/followup_rounds per query -- the compiled packet (manifest and rendered "
                   "text) carries no notice, so a non-reproducible packet is indistinguishable from a reproducible one "
                   "(owner R1-GA3)")
def test_c13_compile_discloses_a_non_deterministic_gather(tmp_path, monkeypatch):
    repo = cxrb.build(tmp_path / "cxrepo")
    view = tmp_path / "cx-view.yaml"
    cxrb.write_canonical_view(view, repo)
    reg = tmp_path / "cx-reg.yaml"
    cxrb.write_registry(reg)
    orig = packetmod.gather_with_followup

    def degraded_gather(*a, **k):
        r = orig(*a, **k)
        r["deterministic"] = False
        r.setdefault("telemetry", {})["degraded_git_reads"] = [
            {"call": "read_path", "error": "synthetic transient failure", "commit": repo.c2, "path": "x"}]
        return r

    monkeypatch.setattr(packetmod, "gather_with_followup", degraded_gather)
    ts = _task_spec(str(view), required_inputs=[],
                    queries=[{"id": "Q1", "text": "a fixture decision about supersession"}])
    res = packetmod.compile_packet(ts, routes=FAKE_ROUTES, repo=str(repo.root), registry_path=str(reg))
    assert res["status"] == packetmod.STATUS_OK
    manifest_text = json.dumps(res["manifest"])
    assert "synthetic transient failure" in manifest_text or '"deterministic": false' in manifest_text


@pytest.mark.xfail(strict=True, reason="INT-D11: freshness._config_sha256 fingerprints the VIEW FILE'S OWN "
                   "DIRECTORY; with a view outside config/ (the pinned view every independent verifier writes) the "
                   "fingerprint omits config/id-grammar.yaml, authority-registry.yaml, embed-profile.yaml, "
                   "model-pin.yaml and state-aliases.yaml, which the layer builders read from GOV_BRIDGE_DOMAIN/config "
                   "-- so `freshness` reports NOOP after any of them changes (owner R1-XC, core/freshness.py)")
def test_c13_freshness_fingerprint_covers_the_config_the_builders_read_for_any_view_path(tmp_path):
    from govbridge.core import freshness
    repo = cxrb.build(tmp_path / "cxrepo")
    elsewhere = tmp_path / "pinned"
    elsewhere.mkdir()
    view = elsewhere / "pinned-view.yaml"
    cxrb.write_canonical_view(view, repo)
    fp, _ = freshness.compute_fingerprint(str(view), str(DOMAIN / "config" / "corpus-rules.yaml"),
                                          repo=str(repo.root))
    read_by_builders = {"id-grammar.yaml", "authority-registry.yaml", "embed-profile.yaml", "model-pin.yaml",
                        "state-aliases.yaml"}
    assert read_by_builders <= set(fp["config_sha256"]), sorted(fp["config_sha256"])


@pytest.mark.xfail(strict=True, reason="INT-D12: a code-comment citation of the form <file>:<L1>/<L2> (two lines, "
                   "the shape the real product uses at runtime/src/paths.rs:326 and tests/certification/p2ho56_floor.rs:3 "
                   "at the product pin) yields neither a CITES_REQUIREMENT edge nor a lineage_unresolved row -- "
                   "PATH_CITE_RE's lookahead rejects the '/', the match falls back to a line-less path, which is "
                   "skipped: a silent drop Gap 1 forbids; the real-view count of path:line citations is a FALSE zero "
                   "(owner R1-RL, graph/derive.py)")
def test_c7_two_line_path_citation_in_a_code_comment_is_never_silently_dropped(tmp_path):
    from govbridge.graph import derive as derivemod
    root = tmp_path / "citerepo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "records")
    _write(root, "runtime/src/target.rs", "fn a() {}\nfn b() {}\nfn c() {}\n")
    _write(root, "runtime/src/citing.rs", "/// verified at `target.rs:1/3` (two lines)\nfn x() {}\n")
    c = _commit(root, "c1")
    text = (root / "runtime/src/citing.rs").read_text(encoding="utf-8")
    edges, unresolved = derivemod.cites_requirement_edges_in_text(text, "runtime/src/citing.rs", c, repo=str(root))
    single, _ = derivemod.cites_requirement_edges_in_text("/// see `target.rs:1`", "runtime/src/citing.rs", c,
                                                          repo=str(root))
    assert single, "control: the single-line form IS recognised"
    assert edges or unresolved, "the two-line form produced neither an edge nor an unresolved record"


@pytest.mark.xfail(strict=True, reason="INT-D17: compile_packet looks up a facet's MISSING reason in "
                   "gather_with_followup's telemetry.per_round, which holds only FOLLOW-UP rounds (the base round's "
                   "per-facet rows, and every base item's provenance facet, are dropped), so every FACET_MISSING notice "
                   "falls back to 'gather found candidates for this facet, but none were placed ... dropped by budget' "
                   "-- false when gather found NO candidates (CONTROL-A's code facets: 'no matching evidence found in "
                   "this facet's scope'); no notice carries a handle (owner R1-GA3; telemetry shape R1-GA2)")
def test_c4_facet_missing_reason_is_true_when_gather_found_nothing(tmp_path):
    repo = cxrb.build(tmp_path / "cxrepo")
    view = tmp_path / "cx-view.yaml"
    cxrb.write_canonical_view(view, repo)
    reg = tmp_path / "cx-reg.yaml"
    cxrb.write_registry(reg)
    ts = _task_spec(str(view), required_inputs=[], queries=[{"id": "Q1", "text": "a query no route can answer"}])
    res = packetmod.compile_packet(ts, routes=FAKE_ROUTES, repo=str(repo.root), registry_path=str(reg))
    reasons = [n["reason"] for n in res["manifest"]["notices"] if n.get("type") == "FACET_MISSING"]
    assert reasons, "premise: with no route able to answer, every facet is reported missing"
    assert not any("gather found candidates" in r for r in reasons), reasons[:2]


@pytest.mark.xfail(strict=True, reason="INT-D18: for a natural-language query (no id/path/symbol token) compile_packet "
                   "hands gather_with_followup a RouteSet whose exact AND code routes are router.empty_route (per-query "
                   "select_routes -> lexical+semantic), although the query's facets include the code-route facets "
                   "(dependencies/dependents/tests) and the follow-up resolves identifiers ONLY through exact/code -- so "
                   "inside every compile the follow-up is inert (CONTROL-A: 1 round, MARGINAL_GAIN_ONLY_DUPLICATES, all 5 "
                   "queries) and the code facets are empty (owner R1-GA3; with R1-GA1/R1-GA2, see INT-VERDICT)")
def test_c4_compile_gather_keeps_the_routes_its_facets_and_followup_need(tmp_path, monkeypatch):
    from govbridge.route import router as routermod
    repo = cxrb.build(tmp_path / "cxrepo")
    view = tmp_path / "cx-view.yaml"
    cxrb.write_canonical_view(view, repo)
    reg = tmp_path / "cx-reg.yaml"
    cxrb.write_registry(reg)
    seen = []
    orig = packetmod.gather_with_followup

    def spy(q, routes, *a, **k):
        seen.append({"exact": routes.exact is routermod.empty_route, "code": routes.code is routermod.empty_route})
        return orig(q, routes, *a, **k)

    monkeypatch.setattr(packetmod, "gather_with_followup", spy)
    sentinel = lambda **kw: []  # noqa: E731 -- a real (non-empty) route object, so emptiness is decided by compile alone
    routes = routermod.RouteSet(exact=sentinel, lexical=sentinel, semantic=sentinel, code=sentinel)
    ts = _task_spec(str(view), required_inputs=[],
                    queries=[{"id": "Q1", "text": "which tests prove that the evidence map owner check fails"}])
    packetmod.compile_packet(ts, routes=routes, repo=str(repo.root), registry_path=str(reg))
    assert seen, "premise: compile ran the query through gather_with_followup"
    assert not any(x["exact"] or x["code"] for x in seen), seen


# ---------------------------------------------------------------------------------------------------------------
# Check 10: one resolved view per operation, on a fixture view, by a dynamic resolution count
# ---------------------------------------------------------------------------------------------------------------

@pytest.fixture
def _count_resolutions(monkeypatch):
    from govbridge.core import view as viewmod
    calls = []
    orig = viewmod.resolve_view

    def counting(config, repo=None):
        rv = orig(config, repo=repo)
        calls.append({n: r.commit for n, r in rv.named.items()})
        return rv

    monkeypatch.setattr(viewmod, "resolve_view", counting)
    return calls


def test_c10_why_and_history_resolve_once_and_record_the_commits_used(tmp_path, _count_resolutions):
    repo = cxrb.build(tmp_path / "cxrepo")
    view = tmp_path / "cx-view.yaml"
    cxrb.write_canonical_view(view, repo)
    reg = tmp_path / "cx-reg.yaml"
    cxrb.write_registry(reg)
    from govbridge.graph import history as historymod
    from govbridge.graph import why as whymod
    for fn in (lambda: whymod.why("CX-0002", repo=str(repo.root), view_path=str(view), registry_path=str(reg)),
               lambda: historymod.history("CX-0002", repo=str(repo.root), view_path=str(view),
                                          registry_path=str(reg))):
        _count_resolutions.clear()
        out = fn()
        assert len(_count_resolutions) == 1, _count_resolutions
        recorded = {r["name"]: r["commit"] for r in out["resolved_refs"]}
        assert recorded == _count_resolutions[0]


@pytest.mark.xfail(strict=True, reason="INT-D09: `govbridge why` and `govbridge history` accept no --view (every other "
                   "query command does), and why()/history() ignore the task spec's `view`, so a recorded operation can "
                   "never be re-run at its recorded commits -- they always resolve config/canonical-view.yaml at the "
                   "live tip (owner R1-RS, CLI surface; BR-DAG-AMEND-R1-23 reproducibility)")
def test_c10_why_and_history_cli_accept_a_view(tmp_path):
    repo = cxrb.build(tmp_path / "cxrepo")
    view = tmp_path / "cx-view.yaml"
    cxrb.write_canonical_view(view, repo)
    from govbridge import cli
    for cmd in ("why", "history"):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            try:
                rc = cli.main([cmd, "CX-0002", "--view", str(view)])
            except SystemExit as e:
                rc = e.code
        assert rc == 0, f"{cmd} --view rejected"


def _renamed_ref_repo(tmp_path: Path):
    """A view whose ref NAMES differ from the git branch names (records -> refs/heads/rec-line, product ->
    refs/heads/prod-line), exactly like the real canonical view (product -> refs/heads/phase2/approved-delta)."""
    root = tmp_path / "rnrepo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "rec-line")
    _write(root, "config/corpus-rules.yaml",
           "schema: govbridge-corpus-rules/1\nrules:\n- {id: INCLUDED, effect: INCLUDE, match: {}}\n")
    _write(root, "runtime/src/lib.rs", "pub fn renamed_ref_probe_fn() {}\n")
    _commit(root, "c1")
    _git(root, "branch", "prod-line")
    view = tmp_path / "rn-view.yaml"
    view.write_text("schema: govbridge-canonical-view/1\nview_id: r1int-renamed\nrefs:\n"
                    "  - {name: records, ref: refs/heads/rec-line, follow: tip, role: primary}\n"
                    "  - {name: product, ref: refs/heads/prod-line, follow: tip, role: product}\n"
                    "partitions:\n  - {name: records, paths: ['**'], owner: records, fallback: [product]}\n",
                    encoding="utf-8")
    return root, str(view)


def test_c13_exact_path_and_id_accept_a_view_ref_name(tmp_path):
    """Control for the next test: `exact path --ref <view ref name>` maps the NAME through the view."""
    from govbridge.core import exact as exactmod
    root, view = _renamed_ref_repo(tmp_path)
    r = exactmod.path_resolve("lib.rs", ref="product", view_path=view, repo=str(root))
    assert r["resolved"] == "runtime/src/lib.rs"


@pytest.mark.xfail(strict=True, reason="INT-D14: `exact grep --ref <view ref name>` (and `exact id --ref`, which calls "
                   "it) passes the NAME straight to git -- `--ref product` on the real view raises an unhandled GitError "
                   "('unable to resolve revision: product', int-08) while `exact path --ref product` maps it through the "
                   "view; a git branch passed instead resolves its LIVE tip, outside the one resolved view (owner R1-XC, "
                   "core/exact.py)")
def test_c13_exact_grep_accepts_a_view_ref_name(tmp_path):
    from govbridge.core import exact as exactmod
    root, view = _renamed_ref_repo(tmp_path)
    r = exactmod.grep("renamed_ref_probe_fn", ref="product", view_path=view, repo=str(root))
    assert [h["path"] for h in r["hits"]] == ["runtime/src/lib.rs"]


@pytest.mark.xfail(strict=True, reason="INT-D15: BR-DAG-AMEND-R1-23 requires every query operation's OUTPUT to record the "
                   "view it resolved; `impact` records none (nor does `search`, and every supplementary packet manifest "
                   "carries view: []), so an independent verifier cannot tell which records commit answered it (owner "
                   "R1-XC)")
def test_c10_impact_and_supplementary_packets_record_the_resolved_view(tmp_path, monkeypatch):
    from govbridge.core import freshness
    from govbridge.graph import impact as impactmod
    root, view = _renamed_ref_repo(tmp_path)
    monkeypatch.delenv("GOV_BRIDGE_HOME", raising=False)  # the shared, read-only model cache (semantic layer)
    assert freshness.run(view_path=view, rules_path=str(root / "config" / "corpus-rules.yaml"), repo=str(root),
                         from_clean=True)["trigger"] == "FULL"
    out = impactmod.impact("renamed_ref_probe_fn", repo=str(root), view_path=view)
    ts = _task_spec(view)
    built = suppmod.build_supplementary_packet("search", {"text": "q", "routes": [], "hits_by_route": {},
                                                          "fused": [], "excluded_hits": 0}, ts)
    assert out.get("resolved_refs") and built["manifest"].get("view")


@pytest.mark.xfail(strict=True, reason="INT-D16: graph/code_bridge.build_shaped_code_connection builds every "
                   "resolve.Definition with path=\"\", so Index.by_path never matches a call's own path and "
                   "HEURISTIC_SAME_FILE can never fire on the shaped connection the code route's callers/TESTS use; at "
                   "the product pin 6,380 bare calls have exactly one same-file fn, of which 2,479 come out "
                   "HEURISTIC_AMBIGUOUS (16,159 candidate rows) -- a false zero for HEURISTIC_SAME_FILE (int-07) "
                   "(owner R1-XC, last editor of graph/code_bridge.py; code from I1)")
def test_c7_same_file_bare_call_resolves_heuristic_same_file_on_the_shaped_connection(tmp_path, monkeypatch):
    from govbridge.core import freshness
    from govbridge.graph import code_bridge
    root = tmp_path / "sfrepo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _write(root, "config/corpus-rules.yaml",
           "schema: govbridge-corpus-rules/1\nrules:\n- {id: INCLUDED, effect: INCLUDE, match: {}}\n")
    _write(root, "runtime/src/a.rs", "fn helper() -> u8 { 1 }\npub fn user_a() -> u8 { helper() }\n")
    _write(root, "runtime/src/b.rs", "fn helper() -> u8 { 2 }\npub fn user_b() -> u8 { helper() }\n")
    c = _commit(root, "c1")
    view = tmp_path / "sf-view.yaml"
    view.write_text("schema: govbridge-canonical-view/1\nview_id: r1int-samefile\nrefs:\n"
                    "  - {name: records, ref: refs/heads/main, follow: tip, role: primary}\n"
                    "partitions:\n  - {name: records, paths: ['**'], owner: records, fallback: []}\n", encoding="utf-8")
    monkeypatch.delenv("GOV_BRIDGE_HOME", raising=False)  # the shared, read-only model cache (semantic layer)
    assert freshness.run(view_path=str(view), rules_path=str(root / "config" / "corpus-rules.yaml"), repo=str(root),
                         from_clean=True)["trigger"] == "FULL"
    conn = code_bridge.build_shaped_code_connection(c, repo=str(root))
    labels = conn.execute("SELECT r.label FROM call_site cs JOIN resolution r ON r.call_site = cs.rowid "
                          "WHERE cs.callee_name = 'helper'").fetchall()
    assert labels and {lab for (lab,) in labels} == {"HEURISTIC_SAME_FILE"}, labels


@pytest.mark.xfail(strict=True, reason="INT-D19: `govbridge why` (cli.cmd_why) calls graph.why.why(seed, task=ctx) "
                   "with no code_conn, so derive.callers_of/callees_of/tests_of get None and the `dependency` and "
                   "`tests` stages are ALWAYS 'MISSING: ...' through the CLI -- on the real view `why embedded_model` "
                   "reports dependency MISSING while `impact embedded_model` finds 20 CALLS edges (int-07); only the "
                   "compiler wires code_conn (owner R1-RS, last cmd_why editor; wiring left undone since I1)")
def test_c7_why_cli_path_reports_code_dependencies_that_exist(tmp_path, monkeypatch):
    from govbridge.core import freshness
    from govbridge.graph import impact as impactmod
    from govbridge.graph import why as whymod
    root = tmp_path / "whyrepo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _write(root, "config/corpus-rules.yaml",
           "schema: govbridge-corpus-rules/1\nrules:\n- {id: INCLUDED, effect: INCLUDE, match: {}}\n")
    _write(root, "runtime/src/w.rs", "pub fn why_target_fn() -> u8 { 1 }\npub fn why_caller_fn() -> u8 { why_target_fn() }\n")
    _write(root, BRIDGE_STATE_PATH, "schema: bridge-orchestrator-state/1\nmandatory_bridge_inputs:\n"
                                    "  authority_classes: {}\n  items: []\n")
    _commit(root, "c1")
    view = tmp_path / "why-view.yaml"
    view.write_text("schema: govbridge-canonical-view/1\nview_id: r1int-why\nrefs:\n"
                    "  - {name: records, ref: refs/heads/main, follow: tip, role: primary}\n"
                    "  - {name: product, ref: refs/heads/main, follow: tip, role: product}\n"
                    "partitions:\n  - {name: records, paths: ['**'], owner: records, fallback: []}\n", encoding="utf-8")
    reg = tmp_path / "why-reg.yaml"
    reg.write_text(REGISTRY, encoding="utf-8")
    monkeypatch.delenv("GOV_BRIDGE_HOME", raising=False)
    assert freshness.run(view_path=str(view), rules_path=str(root / "config" / "corpus-rules.yaml"), repo=str(root),
                         from_clean=True)["trigger"] == "FULL"
    calls = impactmod.impact("why_target_fn", repo=str(root), view_path=str(view))["code"]
    assert calls, "premise: the code layer HAS a caller for this symbol"
    # exactly the call cmd_why makes (seed + task context), plus view/repo/registry for hermeticity
    out = whymod.why("why_target_fn", repo=str(root), view_path=str(view), registry_path=str(reg))
    assert out["stages"]["dependency"]["status"] == "PRESENT", out["stages"]["dependency"]


# ---------------------------------------------------------------------------------------------------------------
# Check 8: a seeded compile must be byte-identical on a file+directory read-only store (BR-DAG-AMEND-R1-15)
# ---------------------------------------------------------------------------------------------------------------

def _build_fixture_store(tmp_path: Path, monkeypatch):
    from govbridge.core import freshness
    monkeypatch.delenv("GOV_BRIDGE_HOME", raising=False)  # the shared, read-only model cache (semantic layer)
    repo = cxrb.build(tmp_path / "cxrepo")
    view = tmp_path / "cx-view.yaml"
    cxrb.write_canonical_view(view, repo)
    reg = tmp_path / "cx-reg.yaml"
    cxrb.write_registry(reg)
    rules = str(DOMAIN / "config" / "corpus-rules.yaml")
    r = freshness.run(view_path=str(view), rules_path=rules, repo=str(repo.root), from_clean=True)
    assert r["trigger"] == "FULL"
    return repo, str(view), str(reg)


def _seed_with_persisted_edges(repo) -> str:
    """The authority layer builder loads the DOMAIN's registry (config/authority-registry.yaml, whose cited quotes
    cannot verify against a synthetic repo), so on a fixture view it records a skipped_reason and persists no
    edges. The premise of check 8 only needs ONE persisted edge from the seed: it is inserted here, while the
    store is still writable, exactly in authority_edge's own schema (govbridge.authority.layer.put_edge)."""
    from govbridge.core import store as storemod
    conn = storemod.open_db()
    try:
        conn.execute("INSERT OR REPLACE INTO authority_edge(src, type, dst, derivation, evidence_occurrence, "
                     "evidence_line, note) VALUES (?,?,?,?,?,?,?)",
                     ("CX-0002", "SUPERSEDES", "CX-0001", "REGISTRY_CITED",
                      f"{cxrb.DECISION_B_PATH}@{repo.c2}:1", 1, "synthetic premise edge (R1-INT check 8)"))
        conn.commit()
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()
    return "CX-0002"


_COMPILE_C_SCRIPT = """
import json, sys
from govbridge.compile import packet as packetmod
from govbridge.route import real_routes
ts = json.loads(sys.argv[1]); repo = sys.argv[2]; view = sys.argv[3]; reg = sys.argv[4]
routes = real_routes.build_real_routes(view_path=view, repo=repo, registry_path=reg)
res = packetmod.compile_packet(ts, routes=routes, repo=repo, registry_path=reg)
print(json.dumps({"status": res["status"], "C": [i["unit"]["id"] for i in res["manifest"]["sections"]["C"]["items"]],
                  "manifest_sha256": res["manifest_sha256"]}))
"""


def _compile_in_fresh_process(ts: dict, repo, view: str, reg: str) -> dict:
    """A FRESH process, like a demonstration agent's own `govbridge compile`: no connection left open by an
    earlier compile in this test process can keep the store's -wal/-shm files alive (which would let a
    read-write open succeed on a read-only directory and mask the defect)."""
    r = subprocess.run([sys.executable, "-c", _COMPILE_C_SCRIPT, json.dumps(ts), str(repo.root), view, reg],
                       capture_output=True, text=True, cwd=str(DOMAIN),
                       env={**os.environ, "PYTHONPATH": str(DOMAIN)}, timeout=600)
    assert r.returncode == 0, r.stderr[-2000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


@pytest.mark.xfail(strict=True, reason="INT-D03: compile_packet's seed pass opens the store READ-WRITE "
                   "(compile/packet.py storemod.open_db()) and graph/traverse.py calls authority.layer.ensure_schema() "
                   "at query time; on a file+directory read-only store (no -wal/-shm left, the state a finished build "
                   "leaves) open_db raises and `except Exception: neighbours = {}` silently drops every section-C graph "
                   "neighbour (owner R1-XC, BR-DAG-AMEND-R1-15/-17)")
def test_c8_seeded_compile_is_identical_on_a_read_only_store(tmp_path, monkeypatch):
    from govbridge.core import store as storemod
    repo, view, reg = _build_fixture_store(tmp_path, monkeypatch)
    seed = _seed_with_persisted_edges(repo)
    ts = _task_spec(view, seeds=[seed])
    store_dir = storemod.store_root()
    db = storemod.db_path(store_dir)
    assert not (store_dir / "store.db-wal").exists() and not (store_dir / "store.db-shm").exists(), \
        "premise: a closed, finished store (no live WAL/SHM), exactly as a from-clean build leaves it"

    rw = _compile_in_fresh_process(ts, repo, view, reg)
    assert rw["status"] == packetmod.STATUS_OK
    assert rw["C"], "premise: on a writable store the seeded compile places the persisted graph neighbour in C"
    before = hashlib.sha256(db.read_bytes()).hexdigest()
    os.chmod(db, 0o444)
    os.chmod(store_dir, 0o555)
    try:
        ro = _compile_in_fresh_process(ts, repo, view, reg)
    finally:
        os.chmod(store_dir, 0o755)
        os.chmod(db, 0o644)
    assert hashlib.sha256(db.read_bytes()).hexdigest() == before
    assert ro["status"] == packetmod.STATUS_OK
    assert ro["C"] == rw["C"]
    assert ro["manifest_sha256"] == rw["manifest_sha256"]
