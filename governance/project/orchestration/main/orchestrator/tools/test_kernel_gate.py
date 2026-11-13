"""Unit tests for kernel_gate.py (owner, 2026-11-12, "item 5 (a)"): a throwaway git repository under tmp_path."""
import hashlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

GATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kernel_gate.py")
X = "template/governance/kernel/x.md"
V1, V2, NEW = "kernel v1\n", "kernel v2\n", "new\n"


def g(repo, *args):
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@localhost",
                    "-c", "commit.gpgsign=false", *args], check=True, capture_output=True, env=env)


def write(repo, rel, text):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode())


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    g(r, "init", "-q", "-b", "base")
    write(r, X, "kernel v1\n")
    write(r, "src/a.py", "a = 1\n")
    g(r, "add", "-A")
    g(r, "commit", "-q", "-m", "base")
    g(r, "checkout", "-q", "-b", "feature")
    return r


def commit(repo, msg="change"):
    g(repo, "add", "-A")
    g(repo, "commit", "-q", "--allow-empty", "-m", msg)


def gate(repo, tmp_path, lines=None, branch="feature", list_path=None):
    if list_path is None:
        list_path = tmp_path / "approved.txt"
        list_path.write_text("# approvals\n\n" + "".join(l + "\n" for l in (lines or [])))
    r = subprocess.run([sys.executable, GATE, "--repo", str(repo), "--branch", branch, "--base", "base",
                        "--list", str(list_path)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def test_unchanged_kernel_passes(repo, tmp_path):
    commit(repo)
    rc, out = gate(repo, tmp_path)
    assert rc == 0, out
    assert "kernel_gate: no kernel path changed" in out


def test_listed_new_bytes_pass(repo, tmp_path):
    write(repo, X, "kernel v2\n")
    commit(repo)
    rc, out = gate(repo, tmp_path, [f"{sha(V2)} {X} DEC-1 approved at abc"])
    assert rc == 0, out
    assert f"ok {X} {sha(V2)[:12]} DEC-1" in out


def test_listed_path_other_hash_refused(repo, tmp_path):
    write(repo, X, "kernel v2\n")
    commit(repo)
    rc, out = gate(repo, tmp_path, [f"{sha(V1)} {X} DEC-1 old bytes"])
    assert rc == 1, out
    assert f"REFUSED {X} {sha(V2)}: no owner approval for these bytes" in out


def test_hash_listed_for_other_path_refused(repo, tmp_path):
    write(repo, X, "kernel v2\n")
    commit(repo)
    rc, out = gate(repo, tmp_path, [f"{sha(V2)} template/governance/kernel/y.md DEC-1 other path"])
    assert rc == 1, out
    assert "REFUSED" in out


def test_unlisted_new_file_refused(repo, tmp_path):
    write(repo, "template/governance/kernel/new.md", "new\n")
    commit(repo)
    rc, out = gate(repo, tmp_path)
    assert rc == 1, out
    assert f"REFUSED template/governance/kernel/new.md {sha(NEW)}" in out


def test_listed_deletion_passes(repo, tmp_path):
    g(repo, "rm", "-q", X)
    commit(repo)
    rc, out = gate(repo, tmp_path, [f"DELETED {X} DEC-2 removed"])
    assert rc == 0, out
    assert f"ok {X} DELETED DEC-2" in out


def test_unlisted_deletion_refused(repo, tmp_path):
    g(repo, "rm", "-q", X)
    commit(repo)
    rc, out = gate(repo, tmp_path)
    assert rc == 1, out
    assert f"REFUSED {X} DELETED" in out


def test_rename_is_delete_plus_add(repo, tmp_path):
    g(repo, "mv", X, "template/governance/kernel/z.md")
    commit(repo)
    rc, out = gate(repo, tmp_path, [f"{sha(V1)} template/governance/kernel/z.md DEC-3 added"])
    assert rc == 1, out  # the delete half is not approved
    assert f"REFUSED {X} DELETED" in out
    rc, out = gate(repo, tmp_path, [f"{sha(V1)} template/governance/kernel/z.md DEC-3 added",
                                    f"DELETED {X} DEC-3 removed"])
    assert rc == 0, out


def test_change_outside_kernel_ignored(repo, tmp_path):
    write(repo, "src/a.py", "a = 2\n")
    write(repo, "template/governance/project/p.md", "not kernel\n")
    commit(repo)
    rc, out = gate(repo, tmp_path)
    assert rc == 0, out
    assert "kernel_gate: no kernel path changed" in out


def test_base_moving_on_does_not_count(repo, tmp_path):
    # a kernel change on the base after the fork is not the branch's change (merge-base, not base)
    commit(repo)
    g(repo, "checkout", "-q", "base")
    write(repo, X, "kernel on base\n")
    commit(repo)
    rc, out = gate(repo, tmp_path)
    assert rc == 0, out


def test_missing_list_exit_2(repo, tmp_path):
    commit(repo)
    rc, out = gate(repo, tmp_path, list_path=tmp_path / "nope.txt")
    assert rc == 2, out
    assert "missing or unreadable" in out


def test_malformed_line_exit_2_names_line(repo, tmp_path):
    commit(repo)
    rc, out = gate(repo, tmp_path, [f"{sha('x')} {X} DEC-1 ok", "notahash template/governance/kernel/x.md DEC-1"])
    assert rc == 2, out
    assert "line 4" in out  # two header lines, then the entries


@pytest.mark.parametrize("bad", [f"{'a' * 64} {X}", f"{'a' * 63} {X} DEC-1 n", f"{'a' * 64} {X} 1141 n",
                                 f"{'a' * 64} /abs/path DEC-1 n"])
def test_malformed_variants_exit_2(repo, tmp_path, bad):
    commit(repo)
    rc, out = gate(repo, tmp_path, [bad])
    assert rc == 2, out


def test_malformed_line_is_exit_2_even_with_no_change(repo, tmp_path):
    commit(repo)
    rc, out = gate(repo, tmp_path, ["garbage"])
    assert rc == 2, out


def test_unknown_branch_exit_2(repo, tmp_path):
    commit(repo)
    rc, out = gate(repo, tmp_path, branch="refs/heads/no-such")
    assert rc == 2, out
    assert "does not resolve" in out


def test_not_a_repo_exit_2(tmp_path):
    (tmp_path / "plain").mkdir()
    lp = tmp_path / "approved.txt"
    lp.write_text("")
    r = subprocess.run([sys.executable, GATE, "--repo", str(tmp_path / "plain"), "--branch", "feature",
                        "--list", str(lp)], capture_output=True, text=True)
    assert r.returncode == 2, r.stdout + r.stderr


def test_bad_arguments_exit_2():
    r = subprocess.run([sys.executable, GATE], capture_output=True, text=True)
    assert r.returncode == 2


# land.py's call (never land.py's queue: every command but the gate is faked)
HERE = Path(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def land():
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location("land_under_test_kgate", HERE / "land.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def integ(tmp_path):
    """A repository with w2/integrate and w2/W2-1 (forked from it)."""
    r = tmp_path / "integ"
    r.mkdir()
    g(r, "init", "-q", "-b", "w2/integrate")
    write(r, X, V1)
    g(r, "add", "-A")
    g(r, "commit", "-q", "-m", "base")
    g(r, "checkout", "-q", "-b", "w2/W2-1")
    return r


def head(repo):
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def test_land_gate_passes_an_unchanged_kernel(land, integ):
    commit(integ)
    rc, out = land.kernel_gate(head(integ), root=integ)
    assert rc == 0 and "no kernel path changed" in out, out


def test_land_gate_refuses_unapproved_kernel_bytes(land, integ):
    write(integ, X, "kernel not approved by anyone\n")
    commit(integ)
    rc, out = land.kernel_gate(head(integ), root=integ)
    assert rc == 1 and f"REFUSED {X}" in out, out


def test_land_gate_that_cannot_run_fails_closed(land, integ, monkeypatch):
    commit(integ)
    monkeypatch.setattr(land, "KERNEL_GATE", HERE / "no-such-kernel-gate.py")
    rc, out = land.kernel_gate(head(integ), root=integ)
    assert rc == 2, out
    monkeypatch.setattr(land, "sh", lambda *a, **k: (_ for _ in ()).throw(OSError("boom")))
    rc, out = land.kernel_gate(head(integ), root=integ)
    assert rc == 2 and "could not run" in out


@pytest.mark.parametrize("gate_rc", [1, 2])
def test_land_main_stops_before_any_enqueue(land, tmp_path, monkeypatch, capsys, gate_rc):
    calls, C = [], "c" * 40

    def fake(cmd, **kw):
        calls.append([str(c) for c in cmd])
        return SimpleNamespace(returncode=0, stdout="", stderr="")
    seen = []
    monkeypatch.setattr(land, "ROOT", tmp_path)
    monkeypatch.setattr(land, "QUEUE", tmp_path / "q")
    ls = tmp_path / "ls.txt"
    ls.write_text("")
    monkeypatch.setattr(land, "LOAD_SENSITIVE", ls)
    monkeypatch.setattr(land, "scan_on", lambda root: False)
    monkeypatch.setattr(land, "sh", fake)
    monkeypatch.setattr(land, "subprocess", SimpleNamespace(run=fake))
    monkeypatch.setattr(land, "git", lambda *a: C)
    monkeypatch.setattr(land, "ticket_of", lambda w2: ("DAEO-x", "STANDARD"))
    monkeypatch.setattr(land, "precheck", lambda *a: ([], "r"))
    monkeypatch.setattr(land, "kernel_gate", lambda c, root=None: (seen.append(c), (gate_rc, f"REFUSED {X} abc"))[1])
    monkeypatch.setattr(sys, "argv", ["land.py", "W2-1"])
    with pytest.raises(SystemExit) as e:
        land.main()
    out = capsys.readouterr().out
    assert seen == [C]
    assert "W2-1: kernel gate refused" in str(e.value.code) and e.value.code != 0
    assert f"REFUSED {X} abc" in out
    assert not any("enqueue" in c or "approve" in c or "run" in c[2:4] for c in calls), calls


def test_land_main_goes_on_when_the_gate_passes(land, tmp_path, monkeypatch, capsys):
    calls, C = [], "c" * 40

    def fake(cmd, **kw):
        calls.append([str(c) for c in cmd])
        return SimpleNamespace(returncode=0, stdout="", stderr="")
    monkeypatch.setattr(land, "ROOT", tmp_path)
    monkeypatch.setattr(land, "QUEUE", tmp_path / "q")
    ls = tmp_path / "ls.txt"
    ls.write_text("")
    monkeypatch.setattr(land, "LOAD_SENSITIVE", ls)
    monkeypatch.setattr(land, "scan_on", lambda root: False)
    monkeypatch.setattr(land, "sh", fake)
    monkeypatch.setattr(land, "subprocess", SimpleNamespace(run=fake))
    monkeypatch.setattr(land, "git", lambda *a: C)
    monkeypatch.setattr(land, "ticket_of", lambda w2: ("DAEO-x", "STANDARD"))
    monkeypatch.setattr(land, "precheck", lambda *a: ([], "r"))
    monkeypatch.setattr(land, "kernel_gate", lambda c, root=None: (0, "kernel_gate: no kernel path changed"))
    monkeypatch.setattr(sys, "argv", ["land.py", "W2-1"])
    with pytest.raises(SystemExit):
        land.main()
    assert any("enqueue" in c for c in calls), calls


def test_real_list_holds_one_approval_per_path():
    """Review F1 (2026-11-12): a later approval for a path replaces the earlier line, so a branch that restores
    replaced bytes is refused. The CTO's list therefore holds at most one hash per path."""
    real = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kernel-approved.txt")
    seen = {}
    for n, line in enumerate(open(real, encoding="utf-8"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        path = line.split()[1]
        assert path not in seen, f"{path} listed twice (lines {seen[path]} and {n}): keep only the current approval"
        seen[path] = n
