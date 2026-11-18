"""Support code for the W2-198 acceptance tests (standard library only).

Every case drives a public interface of ticket DAEO-o5wi as a child process: ``python3 -m gov.cli.main`` on this
worktree's ``src`` (the runner's ``PYTHONPATH`` when it has one), with a fixture ``HOME`` under the test's
``tmp_path``. It reads what the ticket names: exit codes, stdout and stderr, the ``--json`` envelope, ``git`` and the
files. Nothing of the implementation is imported. Never the real ``~/.gov-os``, ``~/.claude/projects`` or eval root.
"""

from __future__ import annotations

import json
import os
import pwd
import re
import shutil
import itertools
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TIMEOUT_S = 120.0
REAL_GIT = shutil.which("git")
_UUIDS = itertools.count(1)


def python_path() -> str:
    return os.environ.get("PYTHONPATH") or str(REPO_ROOT / "src")


def user_base() -> str:
    return os.environ.get("PYTHONUSERBASE") or str(Path(pwd.getpwuid(os.getuid()).pw_dir) / ".local")


def write(path, text: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def epoch(stamp: str) -> float:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()


def make_home(base: Path) -> Path:
    """A fixture HOME with a git identity and ``main`` as the default branch."""
    home = Path(base).resolve() / "home"
    home.mkdir(parents=True, exist_ok=True)
    write(home / ".gitconfig",
          "[user]\n\tname = Fixture\n\temail = fixture@example.invalid\n"
          "[init]\n\tdefaultBranch = main\n[commit]\n\tgpgsign = false\n[tag]\n\tgpgsign = false\n")
    return home


def make_env(home: Path, **extra: str) -> dict:
    """The child's environment: the caller's, less every GIT_* and GOV_* variable, with the fixture HOME."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_"))}
    env.update(HOME=str(home), TZ="UTC", PYTHONPATH=python_path(), PYTHONUSERBASE=user_base(),
               PYTHONDONTWRITEBYTECODE="1", GIT_CONFIG_NOSYSTEM="1", LC_ALL="C.UTF-8")
    env.update(extra)
    return env


@dataclass
class Run:
    code: int
    out: str
    err: str

    @property
    def both(self) -> str:
        return self.out + self.err

    def envelope(self) -> dict:
        text = self.out.strip()
        assert text, f"no JSON envelope on stdout (exit {self.code}); stderr: {self.err[-600:]}"
        try:
            data = json.loads(text)
        except ValueError:
            raise AssertionError(f"stdout is not one JSON envelope (exit {self.code}): {text[-600:]}") from None
        assert isinstance(data, dict) and ("result" in data or "error" in data), f"not an envelope: {text[-600:]}"
        return data

    def text_lines(self) -> list[str]:
        """The text form's lines: stdout's, or stderr's when stdout is empty."""
        source = self.out if self.out.strip() else self.err
        return [line for line in source.splitlines() if line.strip()]


def gov(args, *, env: dict, cwd, timeout: float = TIMEOUT_S) -> Run:
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", *[str(a) for a in args]], cwd=str(cwd), env=env,
                          capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    return Run(done.returncode, done.stdout, done.stderr)


def git(*args, cwd, env: dict, date: str | None = None) -> str:
    env = dict(env)
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    done = subprocess.run([REAL_GIT, *[str(a) for a in args]], cwd=str(cwd), env=env, capture_output=True,
                          text=True, timeout=60)
    assert done.returncode == 0, f"fixture git {args} failed: {done.stderr}"
    return done.stdout.strip()


def commit(repo: Path, env: dict, message: str, files: dict | None = None, date: str | None = None) -> str:
    for rel, text in (files or {}).items():
        write(repo / rel, text)
    git("add", "-A", cwd=repo, env=env)
    git("commit", "-q", "--allow-empty", "-m", message, cwd=repo, env=env, date=date)
    return git("rev-parse", "HEAD", cwd=repo, env=env)


def listing(folder: Path) -> dict:
    """Every file under ``folder`` (relative name -> bytes)."""
    folder = Path(folder)
    return {str(p.relative_to(folder)): p.read_bytes() for p in sorted(folder.rglob("*")) if p.is_file()}


# --------------------------------------------------------------------------
# gov backup
# --------------------------------------------------------------------------

def name_form(name: str) -> re.Pattern:
    return re.compile(rf"^{re.escape(name)}-(\d{{8}}T\d{{6}}Z)\.bundle$")


def stamp_of(when: datetime) -> str:
    return when.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def simple_repo(base: Path, env: dict, name: str = "proj") -> Path:
    repo = Path(base) / name
    repo.mkdir(parents=True)
    git("init", "-q", cwd=repo, env=env)
    commit(repo, env, "first", {"a.txt": "one\n"})
    return repo


def backup_world(base: Path, env: dict) -> dict:
    """The S1 repository: two branches, a tag, a stash, a linked worktree on its own branch with a commit of its own,
    a detached worktree with a commit of its own. The main worktree's folder is ``proj``."""
    base = Path(base)
    main = simple_repo(base, env, "proj")
    git("checkout", "-q", "-b", "dev", cwd=main, env=env)
    dev = commit(main, env, "dev work", {"dev.txt": "dev\n"})
    git("checkout", "-q", "main", cwd=main, env=env)
    commit(main, env, "main work", {"b.txt": "two\n"})
    git("tag", "-a", "v1", "-m", "release v1", cwd=main, env=env)
    git("tag", "light", cwd=main, env=env)
    linked = base / "proj-feature"
    git("worktree", "add", "-q", "-b", "feature", str(linked), cwd=main, env=env)
    feature = commit(linked, env, "feature work", {"feature.txt": "feature\n"})
    detached = base / "proj-detached"
    git("worktree", "add", "-q", "--detach", str(detached), "main", cwd=main, env=env)
    loose = commit(detached, env, "detached work", {"loose.txt": "loose\n"})
    write(main / "a.txt", "one, edited\n")
    git("stash", "-q", cwd=main, env=env)
    return {"main": main, "linked": linked, "detached": detached, "dev": dev, "feature": feature, "loose": loose}


def for_each_ref(repo: Path, env: dict) -> set:
    out = git("for-each-ref", "--format=%(objectname) %(refname)", cwd=repo, env=env)
    return {tuple(line.split(" ", 1)) for line in out.splitlines() if line.strip()}


def list_heads(bundle: Path, env: dict) -> set:
    out = git("bundle", "list-heads", str(bundle), cwd=Path(bundle).parent, env=env)
    return {tuple(line.split(" ", 1)) for line in out.splitlines() if line.strip()}


GIT_STUB = """#!/bin/sh
# git stand-in (W2-198 F1): every call goes to the real git except `git bundle verify`, which fails.
case " $* " in
    *" bundle verify "*) echo "error: stand-in: the bundle does not verify" >&2; exit 1 ;;
esac
exec "@GIT@" "$@"
"""


def git_stub_env(base: Path, env: dict) -> dict:
    stubs = Path(base) / "stubs"
    stub = write(stubs / "git", GIT_STUB.replace("@GIT@", REAL_GIT))
    stub.chmod(0o755)
    env = dict(env)
    env["PATH"] = f"{stubs}{os.pathsep}{env.get('PATH', '')}"
    return env


# --------------------------------------------------------------------------
# gov memaudit scan
# --------------------------------------------------------------------------

SET_NAME = "memory-audit-20261101"
SEGMENT = f"fixtures/evaluation/{SET_NAME}"


def make_set(home: Path, ids=("q01", "q02", "q03"), texts: dict | None = None) -> Path:
    """The fixture set ``<home>/eval/fixtures/evaluation/memory-audit-20261101/hidden/<id>.yaml``."""
    root = Path(home) / "eval" / SEGMENT
    for qid in ids:
        body = (texts or {}).get(qid) or f"id: {qid}\nquestion: placeholder question\ngold: placeholder gold\n"
        write(root / "hidden" / f"{qid}.yaml", body)
    return root


def path_forms(home: Path, set_root: Path) -> dict:
    real = Path(set_root).resolve()
    rel = real.relative_to(Path(home).resolve())
    return {"abs": str(real), "tilde": f"~/{rel}", "dollar": f"$HOME/{rel}", "segment": SEGMENT}


def entry(kind: str, stamp: str | None, session: str, content, cwd: str = "/home/fixture/work/proj") -> dict:
    line = {"type": kind, "sessionId": session, "cwd": cwd, "uuid": f"00000000-0000-4000-8000-{next(_UUIDS):012d}",
            "message": {"role": kind, "content": content}}
    if stamp is not None:
        line["timestamp"] = stamp
    return line


def user(stamp, session, text):
    return entry("user", stamp, session, text)


def say(stamp, session, text):
    return entry("assistant", stamp, session, [{"type": "text", "text": text}])


def bash(stamp, session, command):
    return entry("assistant", stamp, session,
                 [{"type": "tool_use", "id": "toolu_fixture", "name": "Bash", "input": {"command": command}}])


def transcript(path: Path, lines, mtime: str) -> Path:
    """A JSONL transcript: dict lines as JSON, str lines written as they are; its mtime planted."""
    text = "".join((json.dumps(x) if isinstance(x, dict) else x) + "\n" for x in lines)
    path = write(path, text)
    stamp = epoch(mtime)
    os.utime(path, (stamp, stamp))
    return path


def finding_key(item: dict, projects: Path) -> tuple:
    path = Path(item["file"])
    if not path.is_absolute():
        path = Path(projects) / path
    return (str(path.resolve()), item["session"], int(item["line"]), item["role"], item["kind"], item["match"])


# --------------------------------------------------------------------------
# gov decisions basis
# --------------------------------------------------------------------------

REGISTER_HEAD = "# Decision register\n\nThe owner's decisions, newest last.\n\n## Entries\n\n"


def dec(number: int, title: str, *body: str, dash: str = "—") -> str:
    lines = [f"### DEC-{number} {dash} {title}", "- **Status:** ACCEPTED (owner)"]
    lines.extend(body)
    return "\n".join(lines) + "\n\n"


def entry_has_date(item: dict, day: str) -> bool:
    return any(isinstance(v, str) and day in v for v in item.values())


def squash(text: str) -> str:
    return " ".join(str(text).split())
