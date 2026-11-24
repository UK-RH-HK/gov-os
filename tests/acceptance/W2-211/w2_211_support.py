"""Support code for the W2-211 acceptance tests (standard library plus PyYAML-free text building).

Every case drives public interfaces as child processes: ``python3 -m gov.cli.main decisions ...`` on this worktree's
``src`` (the runner's ``PYTHONPATH``), ``git``, ``node`` and files, in repositories built under ``tmp_path`` with a
fixture ``HOME``. Nothing of the real register, the real tree or the network is touched.

Where the ticket leaves a place open, the cases fix it here and the README says so: packages live under
``docs/decisions/packages/<id>.md``; a batch is made by ``gov decisions page --batches docs/decisions/batches`` and read
back through its manifest (``<batch>.manifest.json``: key ``hash``, key ``cards`` in order, each card an id or an object
with ``id``).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REAL_GIT = shutil.which("git")
PKG_DIR = "docs/decisions/packages"
BATCH_DIR = "docs/decisions/batches"
REGISTER = "docs/DECISION_REGISTER.md"


def python_path() -> str:
    return os.environ.get("PYTHONPATH") or str(REPO_ROOT / "src")


def write(path, text: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")
    return path


def make_home(base: Path) -> Path:
    home = Path(base).resolve() / "home"
    home.mkdir(parents=True, exist_ok=True)
    write(home / ".gitconfig", "[user]\n\tname = Fixture\n\temail = fixture@example.invalid\n"
          "[init]\n\tdefaultBranch = main\n[commit]\n\tgpgsign = false\n")
    return home


def make_env(home: Path, role: str = "orchestrator") -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_"))}
    env.update(HOME=str(home), TZ="UTC", PYTHONPATH=python_path(), PYTHONDONTWRITEBYTECODE="1",
               GIT_CONFIG_NOSYSTEM="1", LC_ALL="C.UTF-8")
    if role:
        env["GOV_ROLE"] = role
    return env


@dataclass
class Run:
    code: int
    out: str
    err: str

    @property
    def both(self) -> str:
        return self.out + self.err


def gov(args, *, env: dict, cwd, stdin: str | None = None) -> Run:
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", *[str(a) for a in args]], cwd=str(cwd), env=env,
                          capture_output=True, text=True, timeout=120, input=stdin if stdin is not None else None,
                          stdin=None if stdin is not None else subprocess.DEVNULL)
    return Run(done.returncode, done.stdout, done.stderr)


def git(*args, cwd, env: dict) -> str:
    done = subprocess.run([REAL_GIT, *[str(a) for a in args]], cwd=str(cwd), env=env, capture_output=True, text=True,
                          timeout=60)
    assert done.returncode == 0, f"fixture git {args} failed: {done.stderr}"
    return done.stdout.strip()


def commit(repo: Path, env: dict, message: str) -> str:
    git("add", "-A", cwd=repo, env=env)
    git("commit", "-q", "--allow-empty", "-m", message, cwd=repo, env=env)
    return git("rev-parse", "HEAD", cwd=repo, env=env)


def snapshot(repo: Path) -> dict:
    """Every file outside ``.git`` (name -> bytes)."""
    return {str(p.relative_to(repo)): p.read_bytes() for p in sorted(repo.rglob("*"))
            if p.is_file() and ".git" not in p.relative_to(repo).parts}


# --- packages and the register ------------------------------------------------------------------------------------

def option(key: str, label: str, changes: str | None = None) -> dict:
    out = {"key": key, "label": label, "cost": f"cost of {label}: low, can be undone",
           "consequence": f"{label} goes ahead and the next step starts"}
    if changes:
        out["changes"] = changes
    return out


def package_text(pid: str, *, options=None, drop=(), over=None, **extra) -> str:
    """A clean, page-ready package, with the named fields dropped or replaced."""
    options = options or [option("a", "Keep it"), option("b", "Change it"), option("c", "Drop it")]
    front = {"id": pid, "type": "decision-package", "status": "PROPOSED", "state_class": "AUTHORITATIVE",
             "title": f"Question {pid}", "rank": "P1", "constrains": [],
             "question": f"Should {pid} go ahead?", "found": f"What was found for {pid}: the old way is slow.",
             "options": options,
             "recommendation": {"option": options[0]["key"], "reason": "It is the cheapest.", "confidence": "medium"},
             "sources": ["docs/spec.md", "DEC-1225"], "blocks": "nothing", "rubric": "P1.1",
             "touches": ["spec"], "reversible": "yes", "inside": "repository",
             "raised": {"by": "CTO", "ticket": "W2-211", "date": "2026-11-24"}}
    front.update(extra)
    for name in drop:
        front.pop(name, None)
    lines = ["---"] + [f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in front.items()] + ["---", "",
             f"# {pid} — {front.get('title', '')}", "", "## Answer", "", "- Option chosen:", "- Decision record:", ""]
    return "\n".join(lines)


def register_text(top: int = 1250) -> str:
    entries = []
    for n in (1225, 1230, top):
        entries.append(
            f"### DEC-{n} — An earlier choice {n}\n"
            f"- **Status:** ACCEPTED (owner, 2026-11-20, in the chat; recorded by the CTO; done)\n"
            f"- **Decision:** go ahead with {n}.\n"
            f"- **Adds:** no rule\n"
            f"- **Basis:** the owner's message of 2026-11-20; docs/spec.md\n"
            f"- **Governing sources:** docs/spec.md\n")
    return "# Decision register\n\n" + "\n".join(entries)


def init_repo(base: Path, env: dict, name: str = "repo", packages: dict | None = None, top: int = 1250) -> Path:
    repo = Path(base) / name
    repo.mkdir(parents=True)
    git("init", "-q", cwd=repo, env=env)
    write(repo / "docs/spec.md", "# spec\n")
    write(repo / REGISTER, register_text(top))
    for pid, text in (packages or {}).items():
        write(repo / PKG_DIR / f"{pid}.md", text)
    commit(repo, env, "base")
    return repo


def read_manifest(repo: Path) -> tuple[str, dict, list[str]]:
    files = sorted((repo / BATCH_DIR).glob("*.manifest.json"))
    assert len(files) == 1, f"expected one manifest, found {[f.name for f in files]}"
    data = json.loads(files[0].read_text(encoding="utf-8"))
    cards = [c["id"] if isinstance(c, dict) else c for c in data["cards"]]
    return files[0].name[: -len(".manifest.json")], data, cards


def make_batch(repo: Path, env: dict) -> tuple[str, str, list[str]]:
    """Publish a batch with ``gov decisions page`` and commit it: ``(batch, hash, card ids in order)``."""
    done = gov(["decisions", "page", "--batches", BATCH_DIR, "--root", repo], env=env, cwd=repo)
    assert done.code == 0, f"page failed ({done.code}): {done.both[-800:]}"
    batch, data, cards = read_manifest(repo)
    commit(repo, env, f"batch {batch}")
    digest = str(data["hash"])
    return batch, digest.split(":", 1)[-1], cards


def now_stamp(delta: timedelta = timedelta(0)) -> str:
    return (datetime.now(timezone.utc) + delta).strftime("%Y-%m-%dT%H:%M:%SZ")


def sheet_text(batch: str, digest: str, picks, *, answered: str | None = None, count=None, first="GOV-ANSWERS 1",
               eol="\n") -> str:
    """A sheet written here, by hand (never by the code under test)."""
    lines = [first, f"batch: {batch}", f"hash: sha256:{digest}", f"answered: {answered or now_stamp()}",
             f"count: {len(picks) if count is None else count}"]
    for pid, letter, note in picks:
        lines.append(f"{pid}: {letter}" + (f" | note: {note}" if note is not None else ""))
    lines.append("END")
    return eol.join(lines) + eol


def answer(repo: Path, env: dict, sheet: str, *extra) -> Run:
    return gov(["decisions", "answer", "-", "--batches", BATCH_DIR, "--register", REGISTER, "--root", repo, *extra],
               env=env, cwd=repo, stdin=sheet)


def head(repo: Path, env: dict) -> str:
    return git("rev-parse", "HEAD", cwd=repo, env=env)


def count_commits(repo: Path, env: dict) -> int:
    return int(git("rev-list", "--count", "HEAD", cwd=repo, env=env))


def entries(text: str) -> list[tuple[str, str]]:
    parts = re.split(r"(?m)^(?=### DEC-\d+ )", text)
    return [(re.match(r"### (DEC-\d+)", p).group(1), p) for p in parts if p.startswith("### DEC-")]
