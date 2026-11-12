"""Git, tools and the own-repository check for the W2-81 proving ground (standard library only).

Every repository the proving ground needs is built here from scratch: a folder
of its own, ``git init``, then files written and committed one by one, each
commit with an author and a date the builder sets, so that one seed gives one
history (the same commit hashes). Nothing is cloned or copied from this
repository, its worktrees or the dev tiers.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

# The tools the proving ground needs. A missing one fails naming it; it is never a skip (DEC-899 item 7).
TOOLS = ("git", "gitleaks")


class MissingTool(AssertionError):
    """A tool the proving ground needs is not on PATH."""


def require(tool):
    """The tool's path; a missing tool fails naming it (never a skip)."""
    found = shutil.which(tool)
    if not found:
        raise MissingTool(f"the W2-81 proving ground needs `{tool}` on PATH and it is not there")
    return found


def short(commit):
    """A commit as 12 digits (DEC-911): the only form the manifest and the report hold."""
    return commit[:12]


def _inside(path, folder):
    try:
        Path(path).resolve().relative_to(Path(folder).resolve())
        return True
    except ValueError:
        return False


class InsideThisRepository(AssertionError):
    """A W2-81 write aimed inside this repository: refused before anything is written."""


def outside_this_repository(path):
    """``path``, resolved; refused when it lies in this repository (or holds it). Every W2-81 write goes through it."""
    resolved = Path(path).resolve()
    if _inside(resolved, REPO_ROOT) or _inside(REPO_ROOT, resolved):
        raise InsideThisRepository(f"a W2-81 case never writes in this repository: {resolved}")
    return resolved


# The names only a W2-81 case writes: the built repositories, the manifests' folder, a run folder, a stand-in's
# outputs (a self-test holds this list to the builders' names).
ARTEFACTS = ("python-app", "rust-workspace", "typescript-monorepo", "legacy-docs", "secret-history",
             "python-app-clean", "manifests", "w2-81-run", "adopted", "beside", "no-hidden-questions",
             "hidden-stand-in", "repos", "outputs")
_NOT_THE_SUITES = ("__pycache__", ".claude")  # bytecode, and the editing harness's own marker folders


def paths_under(folder):
    """Every file and folder under ``folder``, empty folders included (``git status`` shows no empty folder), as
    paths relative to it; bytecode caches and the editing harness's marker folders aside."""
    found = set()
    for here, dirs, names in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in _NOT_THE_SUITES]
        base = Path(here).relative_to(folder)
        found |= {(base / d).as_posix() for d in dirs} | {(base / n).as_posix() for n in names}
    return found


def top_level_artefacts():
    """The entries at this worktree's top level, files or folders, empty or not, that only a W2-81 case makes."""
    return {p.name for p in REPO_ROOT.iterdir() if p.name in ARTEFACTS}


def porcelain_here(*paths):
    """This repository's ``git status --porcelain`` (of ``paths`` only, when given)."""
    return subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--porcelain", "--untracked-files=all", "--",
                           *paths], capture_output=True, text=True, env=git_env(REPO_ROOT.parent)).stdout


def w2_81_artefacts(porcelain):
    """The untracked paths of a status that only a W2-81 case could have written."""
    return {line[3:] for line in porcelain.splitlines()
            if line.startswith("?? ") and set(Path(line[3:].rstrip("/")).parts) & set(ARTEFACTS)}


def git_env(home, author=None, date=None):
    """A git environment built from scratch: no system or global configuration, a fixed identity and date."""
    name, email = author or ("Proving Ground", "proving-ground@example.invalid")
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "LC_ALL": "C",
        "TZ": "UTC",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": name, "GIT_AUTHOR_EMAIL": email,
        "GIT_COMMITTER_NAME": name, "GIT_COMMITTER_EMAIL": email,
    }
    if date:
        env["GIT_AUTHOR_DATE"] = date
        env["GIT_COMMITTER_DATE"] = date
    return env


def run_git(root, *args, author=None, date=None, check=True, text=True):
    """``git -C root args``; a failure is an assertion naming the command (never its output's secrets)."""
    require("git")
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=text,
                          env=git_env(Path(root).parent, author, date))
    if check and done.returncode != 0:
        raise AssertionError(f"git {args[0]} failed in {root} (exit {done.returncode})")
    return done.stdout


def assert_own_repository(root):
    """A built repository is never this repository, a folder of it, or a worktree of it."""
    root = Path(root).resolve()
    assert not _inside(root, REPO_ROOT) and not _inside(REPO_ROOT, root), \
        f"a W2-81 repository is never built in or around this repository: {root}"
    common = (root / run_git(root, "rev-parse", "--git-common-dir").strip()).resolve()
    assert common == root / ".git", f"{root}'s git common directory is not its own: {common}"
    own = (REPO_ROOT / run_git(REPO_ROOT, "rev-parse", "--git-common-dir").strip()).resolve()
    assert common != own, f"{root} shares this repository's git common directory"


class Repo:
    """A repository being built, file by file and commit by commit."""

    def __init__(self, root):
        self.root = outside_this_repository(root)
        if self.root.exists():
            raise AssertionError(f"a W2-81 repository is built in a new folder only: {self.root} exists")
        self.root.mkdir(parents=True)
        run_git(self.root, "init", "-q", "-b", "main")
        assert_own_repository(self.root)
        self.commits = []  # (full hash, message)

    def write(self, rel, content):
        path = outside_this_repository(self.root / rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def remove(self, rel):
        outside_this_repository(self.root / rel).unlink()

    def commit(self, message, author, date):
        """Commit everything with the author and date given; returns the full hash."""
        run_git(self.root, "add", "-A")
        run_git(self.root, "commit", "-q", "-m", message, author=author, date=date)
        made = run_git(self.root, "rev-parse", "HEAD").strip()
        self.commits.append((made, message))
        return made

    def head(self):
        return run_git(self.root, "rev-parse", "HEAD").strip()


def tree(root, rev="HEAD"):
    """The paths of a commit's tree."""
    return set(filter(None, run_git(root, "ls-tree", "-r", "--name-only", "-z", rev).split("\0")))


def blob(root, rev, rel):
    """A file's content at a commit, or None when it is not in that commit's tree (held in memory only)."""
    require("git")
    done = subprocess.run(["git", "-C", str(root), "show", f"{rev}:{rel}"], capture_output=True,
                          env=git_env(Path(root).parent))
    return done.stdout.decode("utf-8", "replace") if done.returncode == 0 else None


def history_paths(root):
    """Every path any commit of the repository ever touched."""
    out = run_git(root, "log", "--all", "--name-only", "--format=", "-z")
    return set(p.strip("\n") for p in out.split("\0") if p.strip("\n"))


def all_commits(root):
    return run_git(root, "rev-list", "--all").split()


def files_holding(root, text, rev="HEAD"):
    """The paths of a commit's tree whose content holds ``text`` (a fixed string)."""
    done = subprocess.run(["git", "-C", str(root), "grep", "-l", "-F", "-e", text, rev, "--"], capture_output=True,
                          text=True, env=git_env(Path(root).parent))
    if done.returncode not in (0, 1):
        raise AssertionError(f"git grep failed in {root} (exit {done.returncode})")
    return {line.split(":", 1)[1] for line in done.stdout.splitlines() if ":" in line}


def commit_day(root, rev):
    """A commit's committer date as YYYY-MM-DD."""
    return run_git(root, "log", "-1", "--format=%cs", rev).strip()


def blob_size(root, rev, rel):
    return int(run_git(root, "cat-file", "-s", f"{rev}:{rel}").strip())
