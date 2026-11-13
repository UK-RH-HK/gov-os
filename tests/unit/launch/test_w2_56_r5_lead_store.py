"""W2-56 R5 (S5) unit tests: a lead gets the launcher's own ``GOV_STORE``, as a worker does (W2-116 S3).

Regression evidence only (MR-3). ``gov launch orchestrator|lead <ticket>`` sets ``GOV_STORE`` in the lead's
``--settings`` env and its process environment from the main repository's ``integration_store``, as written; a
setting that cannot be used refuses the lead before anything starts; the parent's ``GOV_STORE``, ``TERM`` and
``TMPDIR`` never pass.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from gov.cli.errors import GovError
from gov.launch import launcher, plan_check, store

from .test_w2_136_plan_check import _plant, _ready, _sessions, _settings


def _lead_project(root: Path, rebuild: str | None) -> Path:
    _plant(root, {"id": "T-4", "wbs_id": "W9-4"})
    for stem in set(launcher.ROLE_TEMPLATES.values()):  # W2-153 S1 (DEC-1112 (3)): any content will do
        path = root / launcher.TEMPLATES_REL / f"{stem}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {stem}\n", encoding="utf-8")
    (root / "governance/project").mkdir(parents=True, exist_ok=True)
    if rebuild is not None:
        (root / "governance/project/rebuild.yaml").write_text(rebuild, encoding="utf-8")
    return root


@pytest.fixture()
def parent(monkeypatch):
    """The parent's own values, none of which may reach a lead."""
    for name, value in ((store.ENV, "/tmp/zqxw56parent-store"), ("TERM", "zqxw56parent-term"),
                        ("TMPDIR", "/tmp/zqxw56parent-tmp"), ("PYTHONPATH", "/zqxw56parent/src")):
        monkeypatch.setenv(name, value)


def _launch(root: Path, role: str, monkeypatch, tmp_path) -> tuple[dict, dict]:
    started = _sessions(monkeypatch, tmp_path)
    monkeypatch.setenv(plan_check.READY_ENV, str(_ready(root, "W9-4 T-4 a.md a.json")))
    assert launcher.launch(root, role, "T-4", ["-p", "go"]) == 0
    [(argv, _cwd, env)] = started
    return _settings(argv)["env"], env


@pytest.mark.parametrize("role", ["orchestrator", "lead"])
def test_a_lead_gets_the_configured_link_as_written_and_never_the_parents(tmp_path, monkeypatch, parent, role):
    target = tmp_path / "stores" / "store-a"
    target.mkdir(parents=True)
    link = tmp_path / "stores" / "store"
    link.symlink_to(target)
    root = _lead_project(tmp_path / "project", f"embed_headers: true\nintegration_store: {link}\n")
    settings_env, env = _launch(root, role, monkeypatch, tmp_path)
    assert settings_env == {"GOV_ROLE": "orchestrator", "GOV_TICKET": "T-4", store.ENV: str(link)}
    assert env[store.ENV] == str(link)  # the link itself, not its target
    for name in ("TERM", "TMPDIR", "PYTHONPATH"):
        assert name not in env and name not in settings_env
    assert not any("zqxw56parent" in value for value in (*env.values(), *settings_env.values()))


@pytest.mark.parametrize("rebuild", [None, "embed_headers: true\n", ""])
def test_no_place_configured_gives_a_lead_no_store_at_all(tmp_path, monkeypatch, parent, rebuild):
    root = _lead_project(tmp_path / "project", rebuild)
    settings_env, env = _launch(root, "lead", monkeypatch, tmp_path)
    assert settings_env == {"GOV_ROLE": "orchestrator", "GOV_TICKET": "T-4"}
    assert store.ENV not in env


@pytest.mark.parametrize("role", ["orchestrator", "lead"])
@pytest.mark.parametrize("rebuild", ["integration_store: relative/store\n", "- a\n", "integration_store: [\n"])
def test_a_place_that_cannot_be_used_refuses_the_lead_before_anything_starts(tmp_path, monkeypatch, role, rebuild):
    root = _lead_project(tmp_path / "project", rebuild)
    started = _sessions(monkeypatch, tmp_path)
    monkeypatch.setenv(plan_check.READY_ENV, str(_ready(root, "W9-4 T-4 a.md a.json")))
    gated = []
    monkeypatch.setattr(launcher, "_admit_start", lambda *args: gated.append(args))
    with pytest.raises(GovError) as raised:
        launcher.launch(root, role, "T-4", ["-p", "go"])
    assert raised.value.code == "LAUNCH_REFUSED"
    assert "rebuild.yaml" in raised.value.message
    assert started == [] and gated == []  # refused before the gate, as a worker's settings refuse it


def _git(root: Path, *args: str) -> None:
    env = {"PATH": "/usr/bin:/bin", "HOME": str(root), "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t",
           "GIT_AUTHOR_EMAIL": "t@t.invalid", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True, env=env)


def test_a_lead_in_a_worktree_gets_the_main_repositorys_place_as_a_worker_does(tmp_path, monkeypatch, parent):
    main_repo = _lead_project(tmp_path / "main", "embed_headers: true\n")
    _git(main_repo, "init", "-q", "-b", "integrate")
    _git(main_repo, "add", "-A")
    _git(main_repo, "commit", "-q", "-m", "before the line")
    worktree = tmp_path / "W9-4"
    _git(main_repo, "worktree", "add", "-q", "-b", "w9/W9-4", str(worktree))
    link = tmp_path / "stores" / "store"
    (main_repo / "governance/project/rebuild.yaml").write_text(f"integration_store: {link}\n")  # uncommitted
    settings_env, env = _launch(worktree, "lead", monkeypatch, tmp_path)
    assert settings_env[store.ENV] == env[store.ENV] == str(link)
    assert launcher.build_settings(worktree.resolve(), "engineer", "T-4")["env"][store.ENV] == str(link)
