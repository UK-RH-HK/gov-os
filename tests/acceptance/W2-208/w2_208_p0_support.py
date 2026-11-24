"""Support code for the phase-0 fix P0-3 of W2-208 (DAEO-kt8e): the kit carries the git hook; adopt, adapters and update
install it; the hook refreshes the integration branch's store and reports a failure to the inbox.

Public interfaces only: the kit's file, ``.git/hooks/reference-transaction`` of a repository, the ``gov`` command line,
``governance/updates/<B>.json``, the log file and the inbox under ``$HOME/.gov-os/inbox/``. The runtime cases build the
repository W2-116's tests build (a project with an integration branch, its notes and a store link; stand-in embedder
endpoints, no real embedder), put the kit's hook in it and run it as git does or by hand. Names the interface does not fix,
chosen here (README, "P0-3"): the CTO's address is ``cto``; the hook's log is ``<repo>/.gov-runtime/refresh-hook.log``
(the refresh's own stderr and stdout, appended); ``gov`` is found on ``PATH`` or at ``$HOME/.local/bin/gov``.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-116"))

import w2_116_s2_support as s2  # noqa: E402
import w2_116_support as s116  # noqa: E402
import w2_208_support as support  # noqa: E402

KIT_HOOK = support.REPO_ROOT / "template" / "governance" / "kernel" / "githooks" / "reference-transaction"
HOOK_REL = ".git/hooks/reference-transaction"
LOCAL_REL = ".git/hooks/reference-transaction.local"
LOG_REL = ".gov-runtime/refresh-hook.log"
CTO = "cto"
WAIT_S = 240.0          # the test's own bound for a refresh the hook starts in the background
QUICK_S = 30.0          # a git operation returns in this long even while the refresh it started is held
QUIET_S = 10.0          # how long a case waits to see that nothing happens


def kit_bytes():
    assert KIT_HOOK.is_file(), f"the kit has no {KIT_HOOK.relative_to(support.REPO_ROOT)}"
    return KIT_HOOK.read_bytes()


def installed(project):
    return Path(project) / HOOK_REL


def is_executable(path):
    return path.is_file() and bool(path.stat().st_mode & stat.S_IXUSR) and os.access(path, os.X_OK)


def assert_installed(project, what):
    path = installed(project)
    assert path.is_file(), f"{what}: no {HOOK_REL} in the project"
    assert is_executable(path), f"{what}: {HOOK_REL} is not executable (mode {oct(path.stat().st_mode)})"
    assert path.read_bytes() == kit_bytes(), f"{what}: {HOOK_REL} is not byte-equal to the kit's file"


# --- the runtime rig ------------------------------------------------------------------------------------------------

@dataclass
class Rig:
    box: object
    env: dict
    project: Path
    branch: str
    embedder: object

    @property
    def inbox(self):
        return Path(self.box.home) / ".gov-os" / "inbox"

    @property
    def log(self):
        return self.project / LOG_REL

    def log_text(self):
        return self.log.read_text(encoding="utf-8", errors="replace") if self.log.is_file() else ""

    def messages(self):
        """Every message of every inbox under the fake HOME: ``[(address, message)]``."""
        found = []
        for path in sorted(self.inbox.glob("*/messages.jsonl")) if self.inbox.is_dir() else []:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    found.append((path.parent.name, json.loads(line)))
        return found

    def store_head(self):
        return s116.worktrees(self.project).get(os.path.realpath(self.box.link), {}).get("head")

    def head(self):
        return s116.head(self.project, self.branch)

    def child_env(self, extra=None):
        return {**s116.run_environment(self.env), **(extra or {})}


def _shim(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"#!{sys.executable}\nimport sys\nfrom gov.cli.main import main\nsys.exit(main(sys.argv[1:]))\n",
                    encoding="utf-8")
    path.chmod(0o755)


def make_rig(base, branch, embedder, questions):
    """A project whose integration branch is ``branch`` (configured in its ``rebuild.yaml``), a ``gov`` on ``PATH`` and at ``$HOME/.local/bin/gov``; no store yet."""
    reason = s116.lacking()
    if reason:
        import pytest

        pytest.skip(reason)
    box = s116.make_box(base / "box")
    env = s116.environment(box, embedder.host, questions.host)
    project = s116.make_project(box)
    s116.git(project, "branch", "-m", branch)
    s2.plant_config(box, project, branch=branch)
    _shim(box.tools / "gov")
    _shim(Path(box.home) / ".local" / "bin" / "gov")
    return Rig(box, env, project, branch, embedder)


def install_kit_hook(rig):
    """The kit's file put where git looks for it (a case does this first: with no kit file it fails there, for that)."""
    hook = installed(rig.project)
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_bytes(kit_bytes())
    hook.chmod(0o755)


def build_store(rig):
    s116.built_integration(rig.project, rig.env, rig.branch)
    assert rig.store_head() == rig.head(), "premise: the store was not built at the branch's head"


def git_commit(rig, note_name, env=None, on=None):
    """A real ``git commit`` (hooks on: the project's own ``.git/hooks``) adding a note; returns ``(code, seconds)``.
    Output goes to files, so a refresh the hook leaves running holds no pipe of ours."""
    out = rig.box.base / "git-commit.out"
    git = s116.GIT
    child = {k: v for k, v in rig.child_env(env).items() if not k.startswith("GIT_DIR")}
    if on is not None:
        subprocess.run([git, "-C", str(rig.project), "checkout", "-q", "-B", on], env=child, check=True,
                       stdin=subprocess.DEVNULL, capture_output=True)
    s116.write(rig.project / "docs" / note_name, s116.note(note_name.split(".")[0].replace("-", "")))
    subprocess.run([git, "-C", str(rig.project), "add", "-A"], env=child, check=True, stdin=subprocess.DEVNULL,
                   capture_output=True)
    began = time.monotonic()
    with open(out, "ab") as sink:
        done = subprocess.run([git, "-C", str(rig.project), "commit", "-q", "-m", f"P0-3: {note_name}"], env=child,
                              stdin=subprocess.DEVNULL, stdout=sink, stderr=sink, timeout=QUICK_S * 6)
    return done.returncode, time.monotonic() - began


def run_hook(rig, state, stdin, env=None, timeout=60):
    """The hook run by hand, as git runs it: in the project, ``<state>`` its argument, ``stdin`` its lines."""
    out = rig.box.base / "hook-direct.out"
    child = {k: v for k, v in (env if env is not None else rig.child_env()).items() if not k.startswith("GIT_DIR")}
    with open(out, "ab") as sink:
        done = subprocess.run([str(installed(rig.project)), state], cwd=str(rig.project), env=child, input=stdin,
                              text=True, stdout=sink, stderr=sink, timeout=timeout)
    return done.returncode


def ref_line(branch, old="0" * 40, new="1" * 40):
    return f"{old} {new} refs/heads/{branch}\n"


def wait_for(predicate, bound=WAIT_S, every=0.5):
    end = time.monotonic() + bound
    while time.monotonic() < end:
        if predicate():
            return True
        time.sleep(every)
    return bool(predicate())


def stays_false(predicate, seconds=QUIET_S, every=0.5):
    """True when ``predicate`` is false for the whole of ``seconds``."""
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if predicate():
            return False
        time.sleep(every)
    return not predicate()


def no_store_built(rig):
    return not os.path.lexists(rig.box.link) and s116.worktrees(rig.project) == {}
