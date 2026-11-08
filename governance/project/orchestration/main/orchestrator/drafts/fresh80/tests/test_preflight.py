"""preflight.py on the planted set: items 1, 2, 5, 6, 12; counts only; no hidden path, question or category-id pair."""
import json
import os
import subprocess

import f80lib as L
import preflight


def run(planted, capsys, monkeypatch, *extra):
    monkeypatch.setattr(L, "COMMIT", planted["head"])
    monkeypatch.setattr(L, "R", planted["main"])
    monkeypatch.delenv("GOV_ROLE", raising=False)
    rc = L.run_tool("preflight", preflight.main,
                    ["--sets-root", str(planted["root"]), "--clone", str(planted["clone"]), *extra])
    out = capsys.readouterr().out
    for line in out.splitlines():
        assert str(planted["root"]) + "/" not in line and "memory-verdict-2/" not in line
        assert "planted question" not in line and "gold v" not in line
        assert not ("nonexistent-id" in line and "v80" in line)
    return rc, out


def test_all_as_expected(planted, capsys, monkeypatch):
    rc, out = run(planted, capsys, monkeypatch)
    assert rc == 0, out
    assert "item 1: files 80 (80 expected); other entries 0; folder mode 700; modified after DEC-1078's close 0" in out
    assert "found once 80; found more than once 0; missing, re-anchored by its commit 0; missing, lines unchecked 0; unresolved 0" in out
    assert "item 5: families: contract (4 members), kernel (3 members), agents (2 members) (as required: yes)" in out
    assert "item 6: questions of category nonexistent-id 1 (1 expected)" in out
    assert "exist nowhere in the clone: yes" in out
    d = json.loads((planted["root"] / "runs/fresh-80/preflight.json").read_text())
    assert d["all_ok"] and d["item6"]["nowhere"] is True


def test_digest_is_sha256sum_form(planted, capsys, monkeypatch):
    rc, out = run(planted, capsys, monkeypatch)
    want = subprocess.run("sha256sum *.yaml | sha256sum", shell=True, cwd=planted["hidden"], capture_output=True,
                          text=True).stdout.split()[0]
    assert f"combined sha256 {want}" in out
    rc, out = run(planted, capsys, monkeypatch, "--expect-sha256", "0" * 64)
    assert rc == 1 and "the checker's digest matches: no" in out


def test_anchor_classes_and_changed_files(planted, capsys, monkeypatch):
    h = planted["hidden"]
    f = h / "v12.yaml"
    f.write_text(f.read_text().replace("# Topic v12", "# Topic gone"))  # heading missing: re-anchored by its commit
    f = h / "v13.yaml"
    f.write_text(f.read_text().replace(', "commit": "' + planted["head"][:12] + '"', ""))
    f.write_text(f.read_text().replace("# Topic v13", "# Topic none"))  # missing, no commit: lines unchecked
    (planted["clone"] / "docs/q/v14.md").write_text("# Topic v14\nfact\n# Topic v14\n")  # found more than once
    rc, out = run(planted, capsys, monkeypatch)
    assert rc == 1
    assert "found once 77; found more than once 1; missing, re-anchored by its commit 1; missing, lines unchecked 1" in out
    assert "not found once: v12 entry 1: missing, re-anchored by its commit" in out
    assert "not found once: v14 entry 1: found more than once" in out
    assert "modified after DEC-1078's close 2 (0 expected)" in out


def test_unresolved_counted(planted, capsys, monkeypatch):
    f = planted["hidden"] / "v20.yaml"
    f.write_text(f.read_text().replace("# Topic v20", "# Topic moved"))
    (planted["clone"] / "docs/q/v20.md").write_text("rewritten\nall\nof it\n")  # the block is found nowhere now
    rc, out = run(planted, capsys, monkeypatch)
    assert "unresolved 1" in out and "agrees with the classes: yes" in out and rc == 1


def test_nonexistent_id_now_exists(planted, capsys, monkeypatch):
    (planted["clone"] / "docs/q/v01.md").write_text("# Topic v01\nfact v01, see DEC-99999.\nmore\n")
    import conftest
    conftest.git(planted["clone"], "commit", "-q", "-am", "the id now exists")  # a clean clone at its new head
    planted["head"] = conftest.git(planted["clone"], "rev-parse", "HEAD")
    rc, out = run(planted, capsys, monkeypatch)
    # the declared drop, not a stop (readiness-7 F2, code review R2)
    assert "exist nowhere in the clone: no" in out and "dropped from every figure (declared)" in out and rc == 0
    d = json.loads((planted["root"] / "runs/fresh-80/preflight.json").read_text())
    assert d["item6"]["nowhere"] is False and d["item6"]["dropped"] is True and d["all_ok"] is True


def test_whole_token_only(planted, capsys, monkeypatch):
    (planted["clone"] / "docs/q/v01.md").write_text("# Topic v01\nDEC-999990 and XDEC-99999 only\nmore\n")
    rc, out = run(planted, capsys, monkeypatch)
    assert "exist nowhere in the clone: yes" in out


def test_families_line_wrong(planted, capsys, monkeypatch):
    m = planted["clone"] / "governance/project/path-map.yaml"
    m.write_text(m.read_text().replace('  agents: ["AGENTS.md", "CLAUDE.md"]\n', ""))
    rc, out = run(planted, capsys, monkeypatch)
    assert rc == 1 and "(as required: no)" in out


def test_nothing_written_once_used(planted, capsys, monkeypatch):
    runs = planted["root"] / "runs/fresh-80"
    runs.mkdir(parents=True)
    (runs / "USED").write_text("x")
    rc, out = run(planted, capsys, monkeypatch)
    assert "nothing written" in out and not (runs / "preflight.json").exists()


def test_measured_role_refused(planted, monkeypatch, capsys):
    monkeypatch.setenv("GOV_ROLE", "research")
    monkeypatch.setattr(L, "R", planted["main"])
    rc = L.run_tool("preflight", preflight.main, ["--sets-root", str(planted["root"]), "--clone", str(planted["clone"])])
    assert rc == 2 and "refused" in capsys.readouterr().out


def test_refused_without_the_act_nothing_written(planted, monkeypatch, capsys):  # readiness-7 F1
    m = planted["main"] / "governance/project/path-map.yaml"
    m.write_text(m.read_text().replace(', "runs/fresh-80/**"', ""))
    monkeypatch.setattr(L, "COMMIT", planted["head"])
    monkeypatch.setattr(L, "R", planted["main"])
    rc = L.run_tool("preflight", preflight.main, ["--sets-root", str(planted["root"]), "--clone", str(planted["clone"])])
    out = capsys.readouterr().out
    assert rc == 2 and "ACT-GUARD-SETS-1 is not applied" in out and "lacks the run folder's glob" in out
    assert not (planted["root"] / "runs").exists()
