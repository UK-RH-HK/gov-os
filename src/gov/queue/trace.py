"""The impact trace at the landing (W2-206 fix IT-1, IT-2; DEC-1242, DEC-1244): for each candidate, ``gov impact``
on every record file its own change holds, read on the merged tree.

**The records** of a change (``records``): each changed Markdown file with a frontmatter ``id``, ``type`` and
``status`` (a removed one as the change's old side held it), and each entry added, edited or removed in the file the
path map names under ``decision_register``. No source file is traced.

**The graph** is the record graph alone, loaded in a throwaway clone at the traced commit, so the warm clone keeps no
store. That clone holds no code index, so ``gov impact`` loads no code graph.

**It never refuses** (``landing``): the trace runs in a process group of its own, killed at the limit
(``GOV_QUEUE_IMPACT_TIMEOUT``, seconds; 120). Any failure of it makes each ticket's entry the string
``unavailable (<reason>)``. A record ``gov impact`` refuses (a removed one) is that record's ``unavailable`` form.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from gov.cli.errors import GovError
from gov.util.gitenv import git_env

LIMIT_VARIABLE = "GOV_QUEUE_IMPACT_TIMEOUT"
DEFAULT_LIMIT = 120.0
_ASK, _ANSWER, _SAID = "ask.json", "answer.json", "output.txt"


def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), "-c", "core.quotePath=false", *args], capture_output=True,
                          encoding="utf-8", errors="replace", env=git_env(repo))


def _git(repo: Path, *args: str) -> str:
    done = _run_git(repo, *args)
    if done.returncode:
        raise RuntimeError(f"git {' '.join(args[:2])} failed: {' '.join(done.stderr.split())}")
    return done.stdout


def _show(repo: Path, commit: str, path: str) -> str | None:
    """The text of ``path`` at ``commit``; None where the commit holds no such file."""
    done = _run_git(repo, "show", f"{commit}:{path}")
    return None if done.returncode else done.stdout


def _register(repo: Path, commit: str) -> str | None:
    """The path the path map of ``commit`` names under ``decision_register``, or None."""
    import yaml

    from gov.store.loader import PATH_MAP_REL, REGISTER_KEY

    try:
        named = yaml.safe_load(_show(repo, commit, PATH_MAP_REL) or "")
    except yaml.YAMLError:
        return None  # a map that cannot be read fails the load of the graph, which says so
    path = named.get(REGISTER_KEY) if isinstance(named, dict) else None
    return path if isinstance(path, str) else None


def records(repo: Path, commit: str, since: str, tip: str) -> dict[str, str]:
    """``id -> path`` of the records the change ``since...tip`` holds, read on the traced ``commit``."""
    from gov.store.loader import register_entries
    from gov.util import frontmatter

    old = _git(repo, "merge-base", since, tip).strip()
    changed = _git(repo, "diff", "-z", "--no-renames", "--name-only", old, tip).split("\0")
    register = _register(repo, commit)
    gone, held = {}, {}
    for path in sorted(filter(None, changed)):
        if path == register:
            before, after = ({e["id"]: e["content_hash"] for e in register_entries(_show(repo, at, path) or "")[0]}
                             for at in (old, tip))
            held.update({i: path for i in sorted(before.keys() | after.keys()) if before.get(i) != after.get(i)})
        if not path.endswith(".md"):
            continue
        text = _show(repo, commit, path)
        found, text = (gone, _show(repo, old, path)) if text is None else (held, text)
        front = frontmatter.quiet(text or "")
        if front and all(isinstance(front.get(k), str) and front[k] for k in ("id", "type", "status")):
            found[front["id"]] = path
    return {**gone, **held}  # an id the tree still holds (a moved record) is named where it is


def _traced(root: Path, record_id: str, path: str, config: dict) -> dict:
    from gov import impact

    try:
        found = impact.assess(root, [record_id], config)
    except GovError as refused:
        return {"id": record_id, "path": path, "unavailable": _unavailable(f"{refused.code}: {refused.message}"),
                "complete": False}
    named = {kind: [e["id"] for e in found["affected"][kind]] for kind in ("tickets", "tests")}
    return {"id": record_id, "path": path, **named, "complete": found["complete"]}


def _entries(graph: Path, source: str, commit: str, changes: list[dict]) -> dict:
    """In the child process: the throwaway clone of ``source`` made at ``graph``, and each ticket's entry. A ticket
    given twice has one entry, of both changes."""
    _git(graph.parent, "clone", "--quiet", "--shared", "--no-checkout", source, str(graph))
    _git(graph, "checkout", "--quiet", "--detach", commit)
    found: dict[str, dict] = {}
    for change in changes:
        found.setdefault(change["ticket"], {}).update(records(graph, commit, change["since"], change["tip"]))
    config = None
    if any(found.values()):
        from gov.config.loader import load_config
        from gov.store import loader

        loader.load(graph)
        config = load_config(graph)
    entries = {}
    for ticket, held in found.items():
        listed = [_traced(graph, record_id, path, config) for record_id, path in sorted(held.items())]
        entries[ticket] = {"records": listed, "complete": all(r["complete"] for r in listed)}
    return entries


def _unavailable(why: str) -> str:
    return f"unavailable ({' '.join(str(why).split())[:300]})"


def _child(work: Path, limit: float) -> dict:
    """The trace of ``work``'s question run in a process group of its own; the answer it wrote."""
    import gov

    env = git_env(None)
    own = str(Path(gov.__file__).resolve().parents[1])
    env["PYTHONPATH"] = os.pathsep.join(filter(None, (own, env.get("PYTHONPATH"))))
    with open(work / _SAID, "wb") as said:
        child = subprocess.Popen([sys.executable, "-m", "gov.queue.trace", str(work)], cwd=work, env=env,
                                 stdin=subprocess.DEVNULL, stdout=said, stderr=said, start_new_session=True)
        try:
            code = child.wait(limit)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"the trace took longer than its limit of {limit:g} s") from None
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
    try:
        answer = json.loads((work / _ANSWER).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        last = (work / _SAID).read_text(encoding="utf-8", errors="replace").strip().rpartition("\n")[2]
        raise RuntimeError(f"the trace ended with exit {code} and no readable answer: {last}") from None
    if "error" in answer:
        raise RuntimeError(answer["error"])
    return answer["entries"]


def landing(clone: Path, commit: str, candidates: list[dict]) -> dict:
    """``ticket -> entry`` of each candidate's change (``ticket``, ``since``, ``tip``) on ``commit`` of ``clone``;
    the string ``unavailable (<reason>)`` for each where the trace fails or overruns. It never raises for either."""
    tickets = [c["ticket"] for c in candidates]
    work = None
    try:
        given = os.environ.get(LIMIT_VARIABLE, "").strip()
        try:
            limit = float(given) if given else DEFAULT_LIMIT
        except ValueError:
            limit = math.nan
        if not (math.isfinite(limit) and limit > 0):
            raise RuntimeError(f"{LIMIT_VARIABLE} is {given!r}, not a number of seconds above 0")
        work = Path(tempfile.mkdtemp(prefix="gov-impact-"))
        ask = {"source": str(Path(clone).resolve()), "commit": commit,
               "changes": [{k: c[k] for k in ("ticket", "since", "tip")} for c in candidates]}
        (work / _ASK).write_text(json.dumps(ask), encoding="utf-8")
        entries = _child(work, limit)
        return {t: entries[t] for t in tickets}
    except Exception as e:  # noqa: BLE001 - the trace is a notice: whatever fails, the landing goes on
        return dict.fromkeys(tickets, _unavailable(str(e) or type(e).__name__))
    finally:
        if work is not None:
            shutil.rmtree(work, ignore_errors=True)


def main(argv: list[str]) -> int:
    work = Path(argv[0])
    try:
        ask = json.loads((work / _ASK).read_text(encoding="utf-8"))
        answer = {"entries": _entries(work / "graph", ask["source"], ask["commit"], ask["changes"])}
    except GovError as error:
        answer = {"error": f"{error.code}: {error.message}"}
    except Exception as error:  # noqa: BLE001 - said to the landing, which goes on
        answer = {"error": f"{type(error).__name__}: {error}"}
    (work / _ANSWER).write_text(json.dumps(answer), encoding="utf-8")
    return 1 if "error" in answer else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
