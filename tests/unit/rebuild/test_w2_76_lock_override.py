"""Builder tests for the rebuild lock's override and the test harness's own lock (W2-76, DEC-956 item 2).

Regression evidence only (MR-3). ``GOV_REBUILD_LOCK`` replaces the machine default, a tree's ``rebuild.yaml`` ``lock:``
still wins over it, and a value that is not an absolute path refuses the rebuild before anything is built. The root
conftest gives each process of a run a lock file of its own in the session's temp folder. Every lock here is a
temporary file, never the machine's.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from gov.cli.errors import GovError
from gov.rebuild import watch
from gov.rebuild.command import add_arguments, run

ROOT = Path(__file__).resolve().parents[3]
CONFTEST = ROOT / "tests" / "conftest.py"
MACHINE = "/tmp/gov-os-rebuild.lock"


def _settings(root, text):
    path = root / watch.SETTINGS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _rebuild(root, monkeypatch):
    monkeypatch.setattr("gov.store.load", lambda root: {"digest": "d"})
    monkeypatch.setattr("gov.retrieval.lexical.refresh", lambda root: None)
    monkeypatch.setattr("gov.codeintel.index", lambda root: None)
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    return run(root, parser.parse_args(["--no-embeddings"]), {"path-map.yaml": {}})


def test_without_the_variable_the_machine_default_is_used(tmp_path, monkeypatch):
    monkeypatch.delenv(watch.ENV_LOCK, raising=False)
    assert watch.settings(tmp_path) == (1800, MACHINE, "default")
    _settings(tmp_path, "slow_after_s: 60\n")
    assert watch.settings(tmp_path) == (60, MACHINE, "default")


def test_the_variable_replaces_the_machine_default(tmp_path, monkeypatch):
    lock = str(tmp_path / "session.lock")
    monkeypatch.setenv(watch.ENV_LOCK, lock)
    assert watch.settings(tmp_path) == (1800, lock, "GOV_REBUILD_LOCK")
    _settings(tmp_path, "slow_after_s: 60\n")
    assert watch.settings(tmp_path) == (60, lock, "GOV_REBUILD_LOCK")


def test_a_tree_s_rebuild_yaml_lock_beats_the_variable(tmp_path, monkeypatch):
    monkeypatch.setenv(watch.ENV_LOCK, str(tmp_path / "session.lock"))
    _settings(tmp_path, f"lock: {tmp_path / 'tree.lock'}\n")
    assert watch.settings(tmp_path) == (1800, str(tmp_path / "tree.lock"), "rebuild.yaml")


@pytest.mark.parametrize("value, reason", [("", "is empty"), ("locks/x.lock", "not an absolute path"),
                                           ("./x.lock", "not an absolute path")])
def test_a_value_that_is_not_an_absolute_path_refuses_and_nothing_is_built(tmp_path, monkeypatch, value, reason):
    monkeypatch.setenv(watch.ENV_LOCK, value)
    with pytest.raises(GovError) as raised:
        _rebuild(tmp_path, monkeypatch)
    assert raised.value.code == "REBUILD_FAILED"
    assert "GOV_REBUILD_LOCK" in raised.value.message and reason in raised.value.message
    assert raised.value.details == {"variable": "GOV_REBUILD_LOCK", "value": value}
    assert not (tmp_path / ".gov-runtime").exists() and not (value and Path(value).exists())


def test_a_wrong_value_refuses_even_where_rebuild_yaml_names_the_lock(tmp_path, monkeypatch):
    monkeypatch.setenv(watch.ENV_LOCK, "relative.lock")
    _settings(tmp_path, f"lock: {tmp_path / 'tree.lock'}\n")
    with pytest.raises(GovError) as raised:
        watch.settings(tmp_path)
    assert raised.value.details == {"variable": "GOV_REBUILD_LOCK", "value": "relative.lock"}


@pytest.mark.parametrize("given, source", [("env", "GOV_REBUILD_LOCK"), ("yaml", "rebuild.yaml")])
def test_the_result_and_the_record_name_the_lock_and_its_source(tmp_path, monkeypatch, given, source):
    lock = tmp_path / "chosen.lock"
    monkeypatch.setenv(watch.ENV_LOCK, str(lock) if given == "env" else str(tmp_path / "other.lock"))
    if given == "yaml":
        _settings(tmp_path, f"lock: {lock}\n")
    result = _rebuild(tmp_path, monkeypatch)
    assert result["lock"]["path"] == str(lock) and result["lock"]["source"] == source and lock.is_file()
    assert list(result["lock"]) == ["path", "source", "wait_s", "holder", "held_by_caller", "taken_at", "released_at"]
    record = (tmp_path / result["record"]).read_text()
    assert f'"source": "{source}"' in record


def test_the_default_source_is_named_in_the_result(tmp_path, monkeypatch):
    monkeypatch.delenv(watch.ENV_LOCK, raising=False)
    monkeypatch.setattr(watch, "LOCK", str(tmp_path / "machine.lock"))  # never the machine's own lock
    result = _rebuild(tmp_path, monkeypatch)
    assert result["lock"]["path"] == str(tmp_path / "machine.lock") and result["lock"]["source"] == "default"


def test_a_lock_named_by_the_variable_that_cannot_be_opened_refuses(tmp_path, monkeypatch):
    lock = str(tmp_path / "missing" / "rebuild.lock")
    monkeypatch.setenv(watch.ENV_LOCK, lock)
    with pytest.raises(GovError) as raised:
        _rebuild(tmp_path, monkeypatch)
    assert raised.value.code == "REBUILD_FAILED" and lock in raised.value.message
    assert not (tmp_path / ".gov-runtime").exists()


# The root conftest's rule.

def test_this_session_has_a_lock_of_its_own_in_its_temp_folder():
    lock = os.environ.get("GOV_REBUILD_LOCK")
    assert lock and lock != MACHINE and os.path.isabs(lock)
    assert Path(lock).parent == Path(tempfile.gettempdir()) and Path(lock).is_file()


def _conftest():
    spec = importlib.util.spec_from_file_location("w2_76_root_conftest", CONFTEST)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("former", [None, "/somewhere/former.lock"])
def test_the_variable_s_former_state_comes_back_and_the_file_goes(monkeypatch, former):
    if former is None:
        monkeypatch.delenv("GOV_REBUILD_LOCK", raising=False)
    else:
        monkeypatch.setenv("GOV_REBUILD_LOCK", former)
    conftest = _conftest()
    path, kept = conftest._own_rebuild_lock()
    assert kept == former and os.environ["GOV_REBUILD_LOCK"] == path and Path(path).is_file()
    conftest._drop_rebuild_lock(path, kept)
    assert os.environ.get("GOV_REBUILD_LOCK") == former and not Path(path).exists()


_RECORDER = '''
import os, pathlib

def pytest_sessionstart(session):
    if not hasattr(session.config, "workerinput"):
        pathlib.Path(os.environ["W2_76_OUT"], "controller").write_text(os.environ.get("GOV_REBUILD_LOCK", ""))
'''

_TEST = '''
import os, pathlib, pytest

@pytest.mark.parametrize("n", range(8))
def test_record(n):
    lock = os.environ["GOV_REBUILD_LOCK"]
    assert pathlib.Path(lock).is_file()
    pathlib.Path(os.environ["W2_76_OUT"], os.environ["PYTEST_XDIST_WORKER"]).write_text(lock)
'''


def test_each_process_of_an_xdist_run_has_its_own_file_and_none_is_left(tmp_path):
    pytest.importorskip("xdist")
    run_dir, out, temproot = tmp_path / "run", tmp_path / "out", tmp_path / "temproot"
    for folder in (run_dir, out, temproot):
        folder.mkdir()
    (run_dir / "conftest.py").write_text(CONFTEST.read_text(encoding="utf-8"), encoding="utf-8")
    (run_dir / "w2_76_recorder.py").write_text(_RECORDER, encoding="utf-8")
    (run_dir / "test_record.py").write_text(_TEST, encoding="utf-8")
    env = dict(os.environ, W2_76_OUT=str(out), PYTEST_DEBUG_TEMPROOT=str(temproot), PYTHONPATH=str(run_dir))
    env.pop("GOV_REBUILD_LOCK", None)
    done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "w2_76_recorder",
                           "-n", "2", str(run_dir)], cwd=run_dir, env=env, capture_output=True, text=True,
                          timeout=300)
    assert done.returncode == 0, done.stdout + done.stderr
    seen = {path.name: path.read_text() for path in out.iterdir()}
    assert set(seen) == {"controller", "gw0", "gw1"}
    assert len(set(seen.values())) == 3 and MACHINE not in seen.values()
    for lock in seen.values():
        assert Path(lock).parent == Path(tempfile.gettempdir()) and not Path(lock).exists()
