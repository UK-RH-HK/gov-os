"""Builder tests for DEC-1045: the secrets scan switched off by configuration (``governance/project/secrets.yaml``).

Regression evidence only (DEC-136). No real gitleaks runs here: the scan is stood in by a recorder, so each test says
whether gitleaks would have been given content. Absent file or key: on, as before. ``scan: off``: nothing is given to
gitleaks and each place names it. Any other value, or a file that cannot be read: CONFIG_INVALID, never off.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import secrets  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.config import loader  # noqa: E402

SWITCH = "governance/project/secrets.yaml"
MAP = ("namespaces:\n"
       "  everything: {paths: ['**'], memory_class: governance}\n"
       "  exports: {paths: ['exports/**'], memory_class: product}\n")
DECLARATION = "template/governance/kernel/checks/secrets-indexing.yaml"


def _write(root: Path, rel: str, text: str) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return rel


@pytest.fixture()
def project(tmp_path):
    root = tmp_path / "project"
    _write(root, "governance/project/path-map.yaml", MAP)
    _write(root, ".gitleaks.toml", (REPO / "template/.gitleaks.toml").read_text(encoding="utf-8"))
    return root


@pytest.fixture()
def scans(monkeypatch):
    """Every text the filter or the check would give to gitleaks, recorded instead; each judged clean."""
    given = []

    def holds(rules, content, root=None, kind=None):
        given.append((kind, content))
        return False

    def scan(rules, chunks, root=None, found=None):
        given.append(("store", list(chunks)))
        return False

    monkeypatch.setattr(secrets, "_holds_secret", holds)
    monkeypatch.setattr(secrets, "_scan", scan)
    return given


def _off(root: Path, value: str = "off") -> None:
    _write(root, SWITCH, f"# DEC-1045\nscan: {value}\n")


# -- the switch as the loader reads it ------------------------------------------------------------------------------

def test_absent_file_or_key_is_on(project):
    assert loader.secrets_scan_on(project) is True
    assert "secrets.yaml" not in loader.load_config(project)
    _write(project, SWITCH, "# nothing switched\n")
    assert loader.secrets_scan_on(project) is True
    _write(project, SWITCH, "{}\n")
    assert loader.secrets_scan_on(project) is True


@pytest.mark.parametrize("written, on", [("off", False), ("'off'", False), ("on", True), ('"on"', True)])
def test_on_and_off_as_written(project, written, on):
    _off(project, written)
    assert loader.secrets_scan_on(project) is on
    assert secrets.scan_on(project) is on
    assert loader.load_config(project)["secrets.yaml"] == {"scan": "on" if on else "off"}


@pytest.mark.parametrize("text", ["scan: maybe\n", "scan: no\n", "scan: false\n", "scan: [off]\n", "scan:\n",
                                  "scan: off\nskip: true\n", "- off\n", "scan: [unclosed\n"])
def test_any_other_value_is_config_invalid_never_off(project, text):
    _write(project, SWITCH, text)
    for read in (loader.secrets_scan_on, loader.load_config, secrets.scan_on):
        with pytest.raises(GovError) as raised:
            read(project)
        assert raised.value.code == "CONFIG_INVALID" and SWITCH in raised.value.message


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads any file")
def test_a_switch_that_cannot_be_read_is_config_invalid(project):
    _off(project)
    (project / SWITCH).chmod(0)
    try:
        with pytest.raises(GovError) as raised:
            loader.secrets_scan_on(project)
        assert raised.value.code == "CONFIG_INVALID"
    finally:
        (project / SWITCH).chmod(0o644)


def test_the_switch_alone_is_read_a_bad_path_map_does_not_stop_it(project):
    _write(project, "governance/project/path-map.yaml", "namespaces: [not, a, map]\n")
    _off(project)
    assert loader.secrets_scan_on(project) is False


# -- the filter -----------------------------------------------------------------------------------------------------

def test_on_the_filter_gives_every_governance_file_to_gitleaks(project, scans):
    rels = [_write(project, "notes/a.md", "Ordinary text.\n"), _write(project, "exports/b.md", "Product.\n")]
    assert secrets.indexable(project, rels) == ["notes/a.md"]
    assert scans == [("content", b"Ordinary text.\n")]
    assert secrets.path_holds_secret(project, "notes/a.md") is False
    assert [kind for kind, _ in scans] == ["content", "path"]


def test_off_the_namespace_filter_stands_and_nothing_is_given_to_gitleaks(project, scans):
    _off(project)
    (project / ".gitleaks.toml").unlink()  # no rules are read either
    rels = [_write(project, "notes/a.md", "Ordinary text.\n"), _write(project, "exports/b.md", "Product.\n")]
    assert secrets.indexable(project, [*rels, "notes/absent.md"]) == ["notes/a.md"]
    assert secrets.path_holds_secret(project, "notes/a.md") is False
    assert scans == []


def test_off_no_store_is_scanned_and_no_record_written(project, scans):
    _write(project, ".gov-runtime/store.json", "{}\n")
    assert secrets.stores_with_secrets(project) == [] and len(scans) == 1  # on: the store was scanned
    (project / secrets.RECORD_REL).unlink(missing_ok=True)
    scans.clear()
    _off(project)
    assert secrets.stores_with_secrets(project) == []
    assert scans == [] and not (project / secrets.RECORD_REL).exists()


def test_off_with_a_bad_switch_the_filter_refuses(project, scans):
    _off(project, "maybe")
    for call in (lambda: secrets.indexable(project, []), lambda: secrets.path_holds_secret(project, "a"),
                 lambda: secrets.stores_with_secrets(project)):
        with pytest.raises(GovError):
            call()
    assert scans == []


# -- the check, as gov check runs it ----------------------------------------------------------------------------------

def _check_env(monkeypatch):
    monkeypatch.setenv("PYTHONPATH", str(REPO / "src"))


def _module(root: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": str(REPO / "src")}
    return subprocess.run([sys.executable, "-P", "-m", "gov.secrets"], cwd=root, capture_output=True, text=True,
                          env=env, timeout=120)


def test_the_check_off_answers_not_applicable_naming_the_switch(project):
    _off(project)
    done = _module(project)
    assert done.returncode == 2 and json.loads(done.stdout) == {"not_applicable": True, "reason": secrets.SCAN_OFF}


def test_the_check_with_a_bad_switch_fails(project):
    _off(project, "maybe")
    done = _module(project)
    assert done.returncode == 1 and done.stdout.startswith("CONFIG_INVALID")


def _declared(root: Path, monkeypatch):
    from gov.check import runner
    from gov.cli.checks import load_declarations

    _write(root, DECLARATION, (REPO / DECLARATION).read_text(encoding="utf-8"))
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    _check_env(monkeypatch)
    declarations = [each for each in load_declarations(root) if each["id"] == "secrets-indexing"]
    runner._augment_declarations(declarations, root)
    return runner._run_declared_check(declarations[0], root, "c0ffee")


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not on PATH")
def test_gov_check_off_names_the_switch_yellow_never_red_nor_silent_green(project, monkeypatch):
    _off(project)
    _write(project, ".gov-runtime/store.json", "{}\n")
    result = _declared(project, monkeypatch)
    assert result["status"] == "YELLOW" and result["reason"] == secrets.SCAN_OFF, result
    assert result["severity"] == "hard-block"


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not on PATH")
def test_gov_check_on_still_scans_a_scan_that_cannot_decide_is_red(project, monkeypatch):
    (project / ".gitleaks.toml").unlink()  # on, the rules are read: without them nothing is decided
    result = _declared(project, monkeypatch)
    assert result["status"] == "RED", result


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not on PATH")
def test_gov_check_with_a_bad_switch_is_red(project, monkeypatch):
    _off(project, "maybe")
    result = _declared(project, monkeypatch)
    assert result["status"] == "RED" and "CONFIG_INVALID" in json.dumps(result["findings"]), result


# -- gov ci staged-secrets --------------------------------------------------------------------------------------------

@pytest.fixture()
def gitleaks_runs(monkeypatch):
    from gov.ci import command

    started = []

    def run(argv, **kwargs):
        started.append(argv)
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(command.subprocess, "run", run)
    monkeypatch.setattr(command, "foreign_index", lambda root: None)
    monkeypatch.setattr(command, "git_env", lambda root: dict(os.environ))
    return command, started


def test_staged_secrets_on_runs_gitleaks_twice(project, gitleaks_runs):
    command, started = gitleaks_runs
    assert command._staged_secrets(project) == {"scans": 2, "secrets": 0}
    assert [argv[0] for argv in started] == ["gitleaks", "gitleaks"]


def test_staged_secrets_off_exits_0_saying_so(project, gitleaks_runs, capsys):
    command, started = gitleaks_runs
    _off(project)
    assert command._staged_secrets(project) == {"scans": 0, "scan": "off", "reason": secrets.SCAN_OFF}
    assert started == [] and secrets.SCAN_OFF in capsys.readouterr().err


def test_staged_secrets_with_a_bad_switch_refuses(project, gitleaks_runs):
    command, started = gitleaks_runs
    _off(project, "maybe")
    with pytest.raises(GovError) as raised:
        command._staged_secrets(project)
    assert raised.value.code == "CONFIG_INVALID" and started == []


# -- the rebuild's report, gov doctor, the lexical index and the retrieval check -------------------------------------

@pytest.mark.skipif(shutil.which("git") is None, reason="git is not on PATH")
@pytest.mark.parametrize("off", [False, True], ids=["on", "off"])
def test_the_rebuild_report_names_the_switch_only_when_off(project, scans, monkeypatch, tmp_path, capsys, off):
    from gov.rebuild.command import add_arguments, run

    _write(project, "notes/a.md", "Ordinary text.\n")
    _write(project, ".gitignore", ".gov-runtime/\n")
    if off:
        _off(project)
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        monkeypatch.delenv(name, raising=False)
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    subprocess.run(["git", "-C", str(project), "add", "-A"], check=True)
    monkeypatch.setenv("GOV_REBUILD_LOCK", str(tmp_path / "rebuild.lock"))
    monkeypatch.setattr("gov.store.load", lambda root: {"digest": "d"})
    monkeypatch.setattr("gov.retrieval.semantic.refresh", lambda root: {"available": False, "reason": "stood in"})
    monkeypatch.setattr("gov.codeintel._tool", lambda *given, **named: {})
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    result = run(project, parser.parse_args([]), loader.load_config(project))
    assert result["stores"]["lexical"] == {"status": "recreated"}
    if off:
        assert scans == []
        assert result["secrets_scan"] == result["secrets_counts"]["scan"] == secrets.SCAN_OFF
        assert secrets.SCAN_OFF in capsys.readouterr().err
    else:
        assert scans and "secrets_scan" not in result and set(result["secrets_counts"]) == {"content", "path"}


@pytest.mark.parametrize("off", [False, True], ids=["on", "off"])
def test_doctor_says_so_only_when_off(project, monkeypatch, off):
    from gov.doctor import command

    for name in ("_check_tools", "_check_hooks", "_check_path_map", "_check_path_compliance",
                 "_check_index_freshness", "_check_canaries", "_check_framework_lock", "_check_isolation",
                 "_check_claude_code", "_check_held_out"):
        monkeypatch.setattr(command, name, lambda *args: {"status": "pass"})
    if off:
        _off(project)
    result = command.run(project, argparse.Namespace(), loader.load_config(project))
    assert result["healthy"] is True
    if off:
        assert result["secrets_scan"] == {"status": "report", "scan": "off", "reason": secrets.SCAN_OFF}
    else:
        assert "secrets_scan" not in result


def test_the_lexical_index_judges_every_file_again_when_the_switch_changes():
    from gov.retrieval import lexical

    assert SWITCH in lexical.JUDGES


def test_a_retrieval_tier_follows_the_projects_switch(project, tmp_path):
    from gov.retrieval.retrieve_check import _adopt

    tier = tmp_path / "tier"
    (tier / ".git" / "info").mkdir(parents=True)
    _adopt(tier, project)
    assert not (tier / SWITCH).exists()
    _off(project)
    _adopt(tier, project)
    assert (tier / SWITCH).read_bytes() == (project / SWITCH).read_bytes()


def test_this_repository_is_switched_off_naming_dec_1045():
    text = (REPO / SWITCH).read_text(encoding="utf-8")
    assert "DEC-1045" in text and loader.secrets_scan_on(REPO) is False
