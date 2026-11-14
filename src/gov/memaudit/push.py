"""``python3 -m gov.memaudit push``: the weekly secret scan and push (W2-187 I13; S12, F7; DEC-1182 (2), DEC-1052).

The wrapper's last step, after the audit steps that ran (never ``maintain``, a refresh or a close). A repository that
declares its weekly push, ``GOV_MEMAUDIT_PUSH="<remote> <branch>"`` in its cron line's environment (absent or empty: no
push; Gov OS declares nothing), gets one full secret scan of the repository, then ``git push <remote> <branch>`` only
when that scan is clean. The scan is the only one in the memory audit and the wrapper. It is counted from its report,
which is a 0600 temporary file outside the repository and deleted after the count; ``--redact`` keeps a secret out of
it, and no finding's text (a secret, a match, a line) is read into a message, printed, logged or written anywhere.

One line, counts and reason words only, through ``say``: ``PUSH none: no declaration`` (exit 0), ``PUSH pushed <remote>
<branch> <12 hex>`` (0), ``PUSH blocked: findings <k>`` (1), ``PUSH blocked: scan failed <word>`` (1: ``missing``,
``timeout``, ``exit`` or ``report``) and ``PUSH failed: git push exit <c>`` (2; git's own output goes to a 0600 file
in the key folder, never printed). The same line ends the cycle's latest ``DIGEST.txt`` in the key folder.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from gov.memaudit import layout, schedule
from gov.memaudit.common import UsageError, git

DECLARATION = "GOV_MEMAUDIT_PUSH"
SCAN_TIMEOUT_S, PUSH_TIMEOUT_S = 600.0, 600.0
PUSH_LOG = "PUSH.log"


def add_arguments(sp) -> None:
    sp.add_argument("--sets-root", required=True, metavar="ROOT", help="the sets root (never opened by the push)")
    sp.add_argument("--repo", metavar="DIR", help="the repository (default: the top level)")
    sp.add_argument("--gitleaks", metavar="EXE",
                    help="the scanner (default: $GOV_MEMAUDIT_GITLEAKS, else the one on PATH)")


def declared() -> tuple[str, str] | None:
    """``(remote, branch)`` from ``GOV_MEMAUDIT_PUSH``; ``None`` when absent or empty. A value that is not exactly two
    words, or a word git would read as an option, is usage (exit 4): nothing is scanned or pushed."""
    words = os.environ.get(DECLARATION, "").split()
    if not words:
        return None
    if len(words) != 2 or any(w.startswith("-") for w in words):
        raise UsageError("declaration")
    return words[0], words[1]


def _scan_timeout() -> float:
    try:
        given = float(os.environ.get("GOV_MEMAUDIT_SCAN_TIMEOUT_S") or SCAN_TIMEOUT_S)
    except ValueError:
        return SCAN_TIMEOUT_S
    return given if given > 0 else SCAN_TIMEOUT_S


def _outside(repo, state: Path) -> str | None:
    """A folder for the report that is not inside the repository."""
    for folder in (tempfile.gettempdir(), str(state)):
        if os.path.isdir(folder) and not layout.inside(folder, repo):
            return folder
    return None


def _entries(report: str) -> int | None:
    """The number of entries in the report: 0 for an empty one; ``None`` when it is not a list. Only counted."""
    try:
        text = Path(report).read_text(encoding="utf-8", errors="replace").strip()
        doc = json.loads(text) if text else None
    except (OSError, ValueError):
        return None
    return 0 if doc is None else len(doc) if isinstance(doc, list) else None


def scan(repo, exe: str, state: Path) -> tuple[str, int | str]:
    """One full scan of ``repo``: ``("clean", 0)``, ``("findings", <k>)`` or ``("failed", <reason word>)``. Fails closed:
    a report that cannot be counted is a failure, and a report with entries is a finding whatever the exit."""
    found = shutil.which(exe, path=os.environ.get("PATH"))
    folder = _outside(repo, state)
    if not found:
        return "failed", "missing"
    if folder is None:
        return "failed", "report"
    fd, report = tempfile.mkstemp(prefix="scan-", suffix=".json", dir=folder)
    os.close(fd)
    os.chmod(report, 0o600)
    try:
        try:
            done = subprocess.run([found, "detect", "--source", str(repo), "--no-banner", "--redact",
                                   "--report-format", "json", "--report-path", report],
                                  capture_output=True, stdin=subprocess.DEVNULL, timeout=_scan_timeout())
        except subprocess.TimeoutExpired:
            return "failed", "timeout"
        except OSError:
            return "failed", "missing"
        count = _entries(report)
        if done.returncode == 0:
            return ("failed", "report") if count is None else ("clean", 0) if count == 0 else ("findings", count)
        if done.returncode == 1:
            return ("findings", count) if count else ("failed", "report")
        return "failed", "exit"
    finally:
        try:
            os.unlink(report)
        except OSError:
            pass


def _write_private(path: Path, data: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    os.chmod(path, 0o600)


def push(repo, remote: str, branch: str, state: Path) -> int:
    """``git push <remote> <branch>``: its exit code (124 on a timeout, 127 when git cannot start). git's own output is
    kept whole in ``PUSH.log`` of the key folder, mode 0600, never printed."""
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    try:
        done = subprocess.run(["git", "-C", str(repo), "push", remote, branch], capture_output=True,
                              stdin=subprocess.DEVNULL, timeout=PUSH_TIMEOUT_S, env=env)
        code, out = done.returncode, done.stdout + done.stderr
    except subprocess.TimeoutExpired:
        code, out = 124, b""
    except OSError:
        code, out = 127, b""
    try:
        state.mkdir(mode=0o700, parents=True, exist_ok=True)
        _write_private(state / PUSH_LOG, out)
    except OSError:
        pass
    return code


def _latest_digest(state: Path) -> Path | None:
    """The newest ``DIGEST.txt`` of the key folder: a fresh run's ``<audit>/`` or a standing run's
    ``standing/<set>/<week>/``."""
    found = [*state.glob("*/DIGEST.txt"), *state.glob("standing/*/*/DIGEST.txt")] if state.is_dir() else []
    found = [p for p in found if p.is_file()]
    return max(found, key=lambda p: (p.stat().st_mtime_ns, str(p)), default=None)


def _append_digest(state: Path, line: str) -> None:
    path = _latest_digest(state)
    if path is None:
        return
    text = path.read_text(encoding="utf-8")
    tmp = path.with_name("." + path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text + ("" if not text or text.endswith("\n") else "\n") + line + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.chmod(tmp, path.stat().st_mode & 0o7777)
    os.replace(tmp, path)


def _pushed(repo, branch: str) -> str:
    """The first 12 hex of the commit the branch names (else the checked-out one); the push is done, so a fault here
    never fails the step."""
    for rev in (f"{branch}^{{commit}}", "HEAD"):
        try:
            return git(repo, "rev-parse", "--verify", rev).decode().strip()[:12]
        except Exception:  # noqa: BLE001
            continue
    return "unknown"


def from_args(args, emit) -> str:
    """The subcommand's entry: ``run`` on the parsed ``add_arguments`` flags."""
    return run(args.sets_root, repo=args.repo, gitleaks=args.gitleaks, emit=emit)


def run(sets_root, *, repo=None, gitleaks=None, emit) -> str:
    """The exit word: ``ok`` (no declaration, or pushed), ``refused`` (blocked: exit 1) or ``stopped`` (the push failed:
    exit 2); a usage fault raises ``UsageError`` (exit 4)."""
    root = layout.root_of(sets_root)
    repo = schedule.repo_of(repo)
    exe = str(gitleaks or os.environ.get("GOV_MEMAUDIT_GITLEAKS") or "gitleaks")
    for flag in (repo, exe if "/" in exe else None):
        if flag is not None and layout.inside(flag, root):
            raise UsageError("flag inside the sets root")
    where = declared()
    state = schedule.state_of(repo)
    if where is None:
        line, word = "PUSH none: no declaration", "ok"
    else:
        kind, detail = scan(repo, exe, state)
        if kind == "findings":
            line, word = f"PUSH blocked: findings {detail}", "refused"
        elif kind == "failed":
            line, word = f"PUSH blocked: scan failed {detail}", "refused"
        else:
            code = push(repo, *where, state)
            if code == 0:
                line, word = f"PUSH pushed {where[0]} {where[1]} {_pushed(repo, where[1])}", "ok"
            else:
                line, word = f"PUSH failed: git push exit {code}", "stopped"
    try:
        _append_digest(state, line)
    except OSError:
        pass
    emit(line)
    return word
