"""sync_context.py's gitleaks scans follow the repository's switch (DEC-1045): on (absent file or key) today's
behaviour, off no gitleaks call and named, any other value refused before anything is copied.

A stand-in `gitleaks` first on PATH logs each call and finds nothing; the record worktree is a git repository made in
tmp_path. Run: python3 -m pytest -q -p no:cacheprovider governance/project/orchestration/test_sync_context.py"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


@pytest.fixture
def sc(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location("sync_context_under_test", HERE / "sync_context.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    root, record = tmp_path / "root", tmp_path / "record"
    root.mkdir()
    (root / ".gitleaks.toml").write_text("[extend]\nuseDefault = true\n")
    subprocess.run(["git", "init", "-q", str(record)], check=True)
    (record / "governance/project/orchestration").mkdir(parents=True)
    monkeypatch.setattr(mod, "ROOT", root)
    monkeypatch.setattr(mod, "RECORD", record)
    monkeypatch.setattr(mod, "DEST", record / "governance/project/orchestration")
    for k, v in {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                 "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null"}.items():
        monkeypatch.setenv(k, v)
    bindir, log = tmp_path / "bin", tmp_path / "gitleaks-calls.log"
    bindir.mkdir()
    fake = bindir / "gitleaks"
    fake.write_text(f"#!/bin/sh\necho \"$@\" >> '{log}'\nexit 0\n")
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bindir}:" + __import__("os").environ["PATH"])
    mod.calls = lambda: log.read_text().splitlines() if log.exists() else []
    return mod


def switch(sc, text):
    path = sc.ROOT / "governance/project/secrets.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.mark.parametrize("text, on", [(None, True), ("", True), ("other: 1\n", True), ("scan: on\n", True),
                                      ("scan: off\n", False), ("scan: 'off'\n", False), ("scan: \"on\"\n", True),
                                      ("# DEC-1045\nscan: off\n", False)])
def test_the_switch_reads_on_and_off_and_absent_is_on(sc, text, on):
    if text is not None:
        switch(sc, text)
    assert sc.scan_on(sc.ROOT) is on


@pytest.mark.parametrize("text", ["scan: maybe\n", "scan: 0\n", "scan: [\n", "- scan\n", "scan: null\n"])
def test_any_other_value_or_an_unreadable_file_raises(sc, text):
    switch(sc, text)
    with pytest.raises(ValueError):
        sc.scan_on(sc.ROOT)


def test_on_the_record_is_scanned_by_gitleaks(sc):
    sc.SCAN = True
    assert sc.scan(sc.DEST) == []
    assert [c.split()[0] for c in sc.calls()] == ["dir"]


def test_off_no_gitleaks_call_and_the_skip_is_named(sc, capsys):
    sc.SCAN = False
    assert sc.scan(sc.DEST) == []
    assert sc.calls() == []
    assert "gitleaks: off by configuration (DEC-1045)" in capsys.readouterr().err


def _change(sc, name="a.md"):
    (sc.DEST / name).write_text("a record line\n")


def test_commit_on_scans_the_staged_set_then_commits(sc):
    sc.SCAN = True
    _change(sc)
    assert sc.commit("s") == 0
    assert [c.split()[:2] for c in sc.calls()] == [["git", "--staged"]]
    assert subprocess.run(["git", "-C", str(sc.RECORD), "log", "--oneline"], capture_output=True, text=True).stdout


def test_commit_off_commits_without_a_gitleaks_call_and_names_it(sc, capsys):
    sc.SCAN = False
    _change(sc)
    assert sc.commit("s") == 0
    assert sc.calls() == []
    assert "off by configuration (DEC-1045)" in capsys.readouterr().err
    assert subprocess.run(["git", "-C", str(sc.RECORD), "log", "--oneline"], capture_output=True, text=True).stdout


def _main(sc, monkeypatch, tmp_path, *args):
    src = tmp_path / "scratch"
    src.mkdir(exist_ok=True)
    (src / "CHECKPOINT.md").write_text("the checkpoint\n")
    monkeypatch.setattr(sc, "sources", lambda: iter([(src, sc.DEST / "main")]))
    monkeypatch.setattr(sys, "argv", ["sync_context.py", *args])
    return sc.main()


def test_main_absent_switch_scans_record_and_staged_set(sc, monkeypatch, tmp_path):
    assert _main(sc, monkeypatch, tmp_path, "--commit", "s") == 0
    assert [c.split()[0] for c in sc.calls()] == ["dir", "git"]
    assert (sc.DEST / "main/CHECKPOINT.md").is_file()


def test_main_off_copies_and_commits_with_no_gitleaks_call(sc, monkeypatch, tmp_path, capsys):
    switch(sc, "scan: off\n")
    assert _main(sc, monkeypatch, tmp_path, "--commit", "s") == 0
    assert sc.calls() == []
    out = capsys.readouterr()
    assert "not scanned: gitleaks: off by configuration (DEC-1045)" in out.out
    assert out.err.count("off by configuration (DEC-1045)") == 2  # the record's scan and the staged set's
    assert (sc.DEST / "main/CHECKPOINT.md").is_file()


def test_main_bad_value_refuses_before_anything_is_copied(sc, monkeypatch, tmp_path, capsys):
    switch(sc, "scan: maybe\n")
    assert _main(sc, monkeypatch, tmp_path, "--commit", "s") == 2
    assert sc.calls() == []
    assert not (sc.DEST / "main").exists()
    assert "cannot be read" in capsys.readouterr().err
