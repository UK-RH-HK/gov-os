"""W2-17 fix S6 (DEC-1223 (6)): the SessionStart hook's one critical line when an update is pending. Builder evidence.

The hook is a child process (``HOME`` under ``tmp_path``) with a fake ``tk`` first on ``PATH`` that prints nothing,
and a planted source with releases 0.9.0 and 0.9.1 (``gov.update.pending`` reads it; no copier, no network).
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK = REPO_ROOT / "template" / "governance" / "kernel" / "hooks" / "sessionstart.py"
PATCH_LINE = "Gov OS update pending: this repository holds 0.9.0, 0.9.1 is the newest (patch): at the next quiet point."
BIGGER_LINE = ("Gov OS update pending: this repository holds 0.9.0, 0.9.1 is the newest (bigger): "
               "the owner decides, gov update 0.9.1.")


def git(repo: Path, *args: str) -> None:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env=env)


def release(source: Path, version: str, kind: dict | None = None) -> None:
    folder = source / "docs" / "releases" / version
    folder.mkdir(parents=True)
    data = json.dumps({"version": version, "files": {"a": "0" * 64}, "wheel": {"name": "w.whl"}}).encode()
    (folder / "manifest.json").write_bytes(data)
    (folder / "manifest.sha256").write_text(hashlib.sha256(data).hexdigest() + "  manifest.json\n")
    if kind is not None:
        (folder / "kind.json").write_text(json.dumps(kind))
    git(source, "add", "-A")
    git(source, "commit", "-q", "-m", f"release {version}")
    git(source, "tag", f"v{version}")


def plant(tmp_path: Path, kind: dict | None = {"kind": "patch"}, held: str = "0.9.0",
          src_path: str | None = None) -> Path:
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init", "-q", "-b", "main")
    release(source, "0.9.0")
    release(source, "0.9.1", kind)
    project = tmp_path / "project"
    (project / "governance").mkdir(parents=True)
    (project / ".copier-answers.yml").write_text(f"_src_path: {src_path or source}\n")
    (project / "governance/framework.lock").write_text(f"release:\n  version: {held}\n")
    return project


def run_hook(tmp_path: Path, project: Path, *, pythonpath: bool = True, role: str = "", tk_lines: int = 0):
    fake = tmp_path / "fakebin"
    fake.mkdir(exist_ok=True)
    (fake / "tk").write_text("#!/bin/sh\n" + "".join(f"echo ticket line {n}\n" for n in range(tk_lines)))
    (fake / "tk").chmod(0o755)
    env = {"PATH": f"{fake}:{os.environ.get('PATH', '/usr/bin:/bin')}", "HOME": str(tmp_path),
           "CLAUDE_PROJECT_DIR": str(project)}
    if pythonpath:
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
    if role:
        env["GOV_ROLE"] = role
    done = subprocess.run([sys.executable, str(HOOK)], input="{}", capture_output=True, text=True, env=env,
                          cwd=str(project))
    assert done.returncode == 0, done.stderr
    return done


def context(done) -> str:
    return json.loads(done.stdout)["hookSpecificOutput"]["additionalContext"] if done.stdout.strip() else ""


def test_a_pending_patch_prints_the_line_with_no_ticket_and_no_role(tmp_path):
    done = run_hook(tmp_path, plant(tmp_path))
    assert PATCH_LINE in context(done).splitlines()


def test_a_bigger_release_names_the_owner_step_without_the_leading_bigger(tmp_path):
    done = run_hook(tmp_path, plant(tmp_path, kind=None))
    assert BIGGER_LINE in context(done).splitlines()


def test_up_to_date_prints_nothing(tmp_path):
    done = run_hook(tmp_path, plant(tmp_path, held="0.9.1"))
    assert done.stdout == "" and done.stderr == ""


def test_an_unreadable_source_prints_nothing(tmp_path):
    done = run_hook(tmp_path, plant(tmp_path, src_path=str(tmp_path / "nowhere")))
    assert done.stdout == "" and done.stderr == ""


def test_a_rolled_back_update_prints_nothing(tmp_path):
    project = plant(tmp_path)
    (project / "governance/updates").mkdir()
    (project / "governance/updates/0.9.1.rolled-back.json").write_text("{}")
    assert run_hook(tmp_path, project).stdout == ""


def test_without_gov_importable_it_prints_nothing_and_exits_zero(tmp_path):
    probe = subprocess.run([sys.executable, "-c", "import gov"], capture_output=True, env={"PATH": "/usr/bin:/bin"})
    if probe.returncode == 0:  # gov is installed for this interpreter: nothing to prove
        return
    done = run_hook(tmp_path, plant(tmp_path), pythonpath=False)
    assert done.stdout == "" and done.stderr == ""


def test_the_line_stays_whole_beside_a_tk_ready_output_longer_than_the_cap(tmp_path):
    done = run_hook(tmp_path, plant(tmp_path), tk_lines=1500)
    text = context(done)
    assert PATCH_LINE in text.splitlines() and len(text) <= 10_000 and "ticket line 0" in text


def test_the_orchestrator_has_the_line_beside_its_parts(tmp_path):
    project = plant(tmp_path)
    done = run_hook(tmp_path, project, role="orchestrator", tk_lines=2)
    text = context(done)
    assert PATCH_LINE in text.splitlines() and "Read now, before anything else" in text and "ticket line 1" in text
