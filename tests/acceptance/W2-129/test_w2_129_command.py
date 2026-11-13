"""W2-129 S1 (one read-only command), S9 (every finding's fields and the fixed role table), S11 (the output, --json
and the exit codes) and S14 (any repository): ``gov links`` run as a child process on the planted repositories."""

from __future__ import annotations

import collections
import json
import subprocess
import sys
from pathlib import Path

import pytest
import w2_129_support as support
from w2_129_support import CODES, MARK, PATH_MAP, ROLES

HERE = Path(__file__).resolve().parent


# --------------------------------------------------------------------------------- S1 one read-only command

def test_s1_runs_with_no_store_reading_head_as_the_loader_does(since_root):
    shas, done = since_root
    out = support.Output(done)
    assert out.code == 1 and out.new is not None, out.text()
    assert not (shas["repo"] / ".gov-runtime" / "store.db").exists()


def test_s1_reads_head_never_the_working_tree(fresh):
    repo = fresh["repo"]
    before = support.links(repo, "--since", fresh["root"])
    ticket = repo / ".tickets/DAEO-t005.md"
    ticket.write_text(ticket.read_text().replace("- DEC-100\n", "- DEC-100\n- DEC-996\n", 1))
    support.write(repo, ".tickets/DAEO-t006.md", support.ticket("DAEO-t006", "W2-906", "in_progress",
                                                                 "sources:\n- DEC-989\n"))
    after = support.links(repo, "--since", fresh["root"])
    assert not [f for f in after.findings if f.names("DEC-996") or f.names("DEC-989") or f.names("DAEO-t006")]
    assert sorted(f.raw for f in after.findings) == sorted(f.raw for f in before.findings)


def test_s1_writes_nothing_but_its_mark_the_head_it_judged(fresh):
    repo = fresh["repo"]
    files, state = support.tree_digest(repo), support.git_state(repo)
    support.run_links(repo, "--since", fresh["root"])
    assert support.tree_digest(repo) == files
    assert support.git_state(repo) == state
    written = sorted(p.relative_to(repo).as_posix() for p in (repo / ".gov-runtime").rglob("*") if p.is_file())
    assert written == [MARK], written
    mark = (repo / MARK).read_text().strip()
    assert len(mark) >= 7 and support.git(repo, "rev-parse", "HEAD").startswith(mark), mark


def probe(repo: Path, *args: str, report: Path) -> dict:
    done = subprocess.run([sys.executable, str(HERE / "w2_129_probe.py"), str(report), "links", "--root", str(repo),
                           *args], cwd=repo, capture_output=True, text=True, timeout=300, env=support.child_env())
    support.require(done)
    return json.loads(report.read_text())


FORBIDDEN_MODULES = ("torch", "ollama", "requests", "httpx", "urllib3", "sentence_transformers", "transformers",
                     "onnxruntime", "gov.retrieval.ollama", "gov.retrieval.semantic", "gov.retrieval.rerank",
                     "gov.retrieval.rerank_service", "gov.retrieval.rerank_worker")


def test_s1_starts_only_git_opens_no_socket_and_writes_only_the_mark(fresh, tmp_path):
    repo = fresh["repo"]
    seen = probe(repo, "--since", fresh["root"], report=tmp_path / "report.json")
    assert seen["code"] in (0, 1), seen["code"]
    assert seen["sockets"] == [], seen["sockets"]
    assert all(Path(executable).name == "git" or Path(argv[0]).name == "git"
               for executable, argv in seen["processes"]), seen["processes"]
    own, runtime = (repo / ".gov-runtime" / "links").resolve(), (repo / ".gov-runtime").resolve()
    stray = [path for path in seen["writes"] if path != "/dev/null" and not Path(path).resolve().is_relative_to(own)
             and Path(path).resolve() != runtime]
    assert stray == [], stray
    assert not [m for m in seen["modules"] if m.split(".")[0] in FORBIDDEN_MODULES or m in FORBIDDEN_MODULES]


# ---------------------------------------------------------------------- S9 what every finding carries

def test_s9_every_finding_carries_its_code_ids_path_line_role_and_fix(every):
    shas, done = every
    out, files = support.Output(done), support.tracked(shas["repo"])
    assert out.findings, out.text()
    for f in out.findings:
        assert f.code in CODES and f.head[len(f.code):].strip(), f
        assert f.path, f
        assert f.path not in files or (f.line is not None and f.line >= 1), f
        roles = [word.strip() for word in f.role.replace(",", " ").split()]
        assert roles and all(role in ROLES for role in roles), f
        assert f.fix.strip(), f


def test_s9_the_role_comes_from_the_one_fixed_table_by_path(every):
    shas, done = every
    out, files = support.Output(done), support.tracked(shas["repo"])
    placed = [f for f in out.findings if f.path in files]
    assert placed, out.text()
    wrong = [(f.path, f.role, support.role_of(f.path)) for f in placed if f.role != support.role_of(f.path)]
    assert wrong == []
    assert {"orchestrator", "product-spec", "engineer", "independent-test-designer"} <= {f.role for f in placed}


@pytest.mark.parametrize("named, path, role", [("DAEO-aaaa", "docs/audit/CL-A-0001.md", "independent-auditor"),
                                               ("DAEO-rrrr", "docs/research/CP-R-0001.md", "research")],
                         ids=["docs-audit", "docs-research"])
def test_s9_a_record_under_docs_audit_or_docs_research_names_that_role(every, named, path, role):
    out = support.Output(every[1])
    found = out.of("UNKNOWN_ID", named, path=path)
    assert found and all(f.role == role for f in found), found


def test_s9_a_commit_s_finding_names_the_role_its_trailer_names(since_root):
    shas, done = since_root
    out = support.Output(done)
    research = out.of("UNKNOWN_ID", "DAEO-zzzz")
    assert research and all("research" in f.role for f in research), research
    designer = [f for f in out.of("NOT_IN_FORCE_AS_RULE", "DEC-120")
                if shas["c3"][:7] in f.raw or "Implements" in f.raw]
    assert designer and all("independent-test-designer" in f.role for f in designer), designer


def test_s9_a_free_text_finding_is_marked_text_and_a_label_finding_is_not(since_root):
    out = support.Output(since_root[1])
    text = out.of("UNMARKED_CHANGE", "DEC-111", "DEC-112")
    assert text and all("(text)" in f.raw for f in text), text
    for changed, changer in (("DEC-101", "DEC-102"), ("DEC-103", "DEC-104"), ("DEC-109", "DEC-110")):
        found = out.of("UNMARKED_CHANGE", changed, changer)
        assert found and not [f for f in found if "(text)" in f.raw], found


# ---------------------------------------------------------------------------- S11 the output and exit codes

def test_s11_the_first_line_counts_new_and_standing_since_the_rev(since_root):
    shas, done = since_root
    out = support.Output(done)
    assert out.new is not None, f"first line: {out.first!r}"
    assert len(out.since) >= 7 and shas["root"].startswith(out.since), out.first
    assert out.new == len(out.findings) and out.standing == 0, out.text()


def test_s11_one_line_per_new_finding_code_ids_path_line_role_fix(since_root):
    out = support.Output(since_root[1])
    body = [line for line in out.lines[1:] if line.strip()]
    assert body and len(body) == len(out.findings), body
    assert all(len(f.parts) >= 4 for f in out.findings), out.findings


def test_s11_json_gives_the_same_findings_in_gov_s_shared_envelope(as_json, since_root):
    shas, done = as_json
    support.require(done)
    envelope = json.loads(done.stdout)
    assert {"ok", "command", "result", "session"} <= set(envelope) and envelope["command"] == "links", envelope
    assert envelope["ok"] is True and done.returncode == 1
    found = support.json_findings(envelope["result"])
    text = support.Output(since_root[1])
    assert collections.Counter(f["code"] for f in found) == collections.Counter(f.code for f in text.findings)
    files = support.tracked(shas["repo"])
    assert {(f["code"], f["path"], f["line"]) for f in found if f.get("path") in files} == \
           {(f.code, f.path, f.line) for f in text.findings if f.path in files}
    for f in found:
        assert {"code", "ids", "path", "line", "role", "fix"} <= set(f) and f["role"] and f["fix"], f
    free = [f for f in found if f["code"] == "UNMARKED_CHANGE" and "DEC-111" in json.dumps(f)]
    assert free and all(f.get("text") is True or "(text)" in json.dumps(f) for f in free), free


def test_s11_exit_code_1_with_new_findings(since_root):
    assert support.Output(since_root[1]).code == 1


def test_s11_exit_code_0_with_no_new_finding(fresh):
    out = support.links(fresh["repo"], "--since", "HEAD")
    assert out.code == 0 and out.new == 0 and out.findings == [], out.text()
    assert out.standing and out.standing > 0, out.first


def test_s11_exit_code_2_named_when_the_register_cannot_be_read(fresh):
    repo = fresh["repo"]
    path_map = repo / PATH_MAP
    path_map.write_text(path_map.read_text().replace("docs/DECISION_REGISTER.md", "docs/GONE.md"))
    support.commit(repo, "the path map names a register HEAD does not hold", None, 9, [PATH_MAP])
    done = support.run_links(repo, "--since", fresh["root"])
    said = (done.stdout + done.stderr).lower()
    assert done.returncode == 2 and "register" in said and "traceback" not in said, done


def test_s11_exit_code_2_named_outside_a_git_work_tree(tmp_path):
    plain = tmp_path / "plain"
    support.write(plain, PATH_MAP, "namespaces:\n  all:\n    paths: [\"**\"]\n")
    done = support.run_links(plain, "--since", "HEAD")
    said = (done.stdout + done.stderr).lower()
    assert done.returncode == 2 and "git" in said and "traceback" not in said, done


# ------------------------------------------------------------------------------------- S14 any repository

def test_s14_a_repository_with_no_register_tickets_or_contract_is_not_applicable(bare, tmp_path):
    shas = support.clone(bare, tmp_path / "repo")
    out = support.links(shas["repo"], "--since", shas["root"])
    said = out.text().lower().replace("_", " ")
    assert out.code == 0 and out.new == 0 and "traceback" not in said, out.text()
    assert "not applicable" in said and all(kind in said for kind in ("register", "tickets", "contract")), said


def test_s14_json_reports_not_applicable_never_an_error(bare, tmp_path):
    shas = support.clone(bare, tmp_path / "repo")
    done = support.run_links(shas["repo"], "--since", shas["root"], "--json")
    envelope = json.loads(done.stdout)
    assert done.returncode == 0 and envelope["ok"] is True and "error" not in envelope, envelope
    assert "not applicable" in json.dumps(envelope["result"]).lower().replace("_", " "), envelope
