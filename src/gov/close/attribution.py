"""The scoped close's runs and the attribution of its reds (W2-115 S4, S5, S10; DEC-988, DEC-989, DEC-1001 (b) (c),
DEC-1003, INVESTIGATION-1 Q-1).

- **The warm clone** (S10): ``.gov-runtime/close/clone/`` in the project, kept between closes. Each use fetches the
  project's commits, resets the clone to the commit asked for and cleans it, keeping its ``.gov-runtime/`` (its
  stores). A clone that cannot be so reset (no repository there, a fetch or a reset that fails) is removed and
  cloned fresh; the answer says so (``replaced``: the reason).
- **The runs**: ``pytest`` in the clone, its JUnit XML (``junit_family=xunit1``) the only reading of a run; each run
  in a heavy-job slot (``gov.resources.slots``) where the machine's configuration names the slots, and named as
  run without one where it does not. A run that ends by its time limit is ``timed_out``.
- **A red** (S4): every failing test is run again alone in the clone at the commit closed; one green alone is a
  flaky candidate, named, never the change's. A red alone is judged against the head without the change (the
  tested code, the same clone reset to it), one run each way, three rounds each way only for a load-sensitive case
  (an entry of the serial phase's own list whose comment's kind is ``latency``; no accepted-reds or
  ``load_sensitive`` list, no marker). It is not the change's only if the head without the change has it red with the same failure type; a
  timeout, an unknown type and a case the head without the change cannot run (``absent``) never match. The
  nightly's recorded result is read first, and stands for the run without the change when that night ran on that
  very commit; no clone is built for a nightly baseline.

No accepted-reds or load-sensitive list is read or written here (S5; ``gov.close.ratchet`` stays the strict
close's).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from gov.util.gitenv import git_env

CLONE_REL = ".gov-runtime/close/clone"
KEEP = ".gov-runtime/"  # the clone's stores, kept by every reset
TIMEOUT, UNKNOWN, ABSENT = "timeout", "unknown", "absent"
NEVER_MATCH = (TIMEOUT, UNKNOWN, ABSENT)
LATENCY = "latency"  # the serial-only list's comment kind that makes an entry load-sensitive
LOAD_SENSITIVE_ROUNDS = 3
TIMED_OUT_EXITS = (124, 137)  # timeout(1): the limit reached, and the kill after it
_LAUNCH = ("import subprocess, sys\n"
           "with open(sys.argv[1], 'w') as log:\n"
           "    sys.exit(subprocess.run(sys.argv[3:], cwd=sys.argv[2], stdout=log, stderr=subprocess.STDOUT)"
           ".returncode)\n")


class CloneError(Exception):
    """The clone cannot be brought to a commit."""


# ---------------------------------------------------------------------------
# The warm clone (S10)
# ---------------------------------------------------------------------------

def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env=git_env(cwd))


def _fetch(root: Path, clone: Path) -> None:
    done = _git(clone, "fetch", "--quiet", "--no-tags", "--force", str(Path(root).resolve()),
                "+HEAD:refs/gov-close/head", "+refs/heads/*:refs/gov-close/heads/*")
    if done.returncode != 0:
        raise CloneError(f"git fetch from the project failed: {' '.join(done.stderr.split())[:300]}")


def checkout(clone: Path, commit: str) -> None:
    """Reset the clone to ``commit`` and clean it, its ``.gov-runtime/`` kept; ``CloneError`` where it cannot."""
    for args in (("reset", "--quiet", "--hard", commit), ("clean", "-ffdxq", "-e", KEEP)):
        done = _git(clone, *args)
        if done.returncode != 0:
            raise CloneError(f"git {args[0]} in the clone failed: {' '.join(done.stderr.split())[:300]}")
    head = _git(clone, "rev-parse", "HEAD").stdout.strip()
    want = _git(clone, "rev-parse", f"{commit}^{{commit}}").stdout.strip()
    if not head or head != want:
        raise CloneError(f"the clone is at {head or 'no commit'}, not {commit}")


def prepare(root: Path, commit: str) -> dict:
    """The warm clone at ``commit``: ``{"path", "reused", "replaced"}`` (``path`` relative to the project)."""
    root = Path(root)
    clone = root / CLONE_REL
    replaced = None
    if (clone / ".git").exists():
        try:
            if _git(clone, "rev-parse", "--is-inside-work-tree").stdout.strip() != "true" \
                    or Path(_git(clone, "rev-parse", "--show-toplevel").stdout.strip() or "/").resolve() \
                    != clone.resolve():
                raise CloneError("the folder is not a repository of its own")
            _fetch(root, clone)
            checkout(clone, commit)
            return {"path": CLONE_REL, "reused": True, "replaced": None}
        except CloneError as e:
            replaced = f"the warm clone could not be reset ({e}); replaced by a fresh clone"
    elif clone.exists():
        replaced = "the warm clone's folder held no repository; replaced by a fresh clone"
    if clone.exists() or clone.is_symlink():
        if clone.is_symlink() or clone.is_file():
            clone.unlink()
        else:
            shutil.rmtree(clone)
    clone.parent.mkdir(parents=True, exist_ok=True)
    done = subprocess.run(["git", "clone", "--quiet", "--no-checkout", str(root.resolve()), str(clone)],
                          capture_output=True, text=True, env=git_env(root))
    if done.returncode != 0:
        raise CloneError(f"git clone failed: {' '.join(done.stderr.split())[:300]}")
    _fetch(root, clone)
    checkout(clone, commit)
    return {"path": CLONE_REL, "reused": False, "replaced": replaced}


# ---------------------------------------------------------------------------
# The runs
# ---------------------------------------------------------------------------

def test_env(clone: Path) -> dict:
    """The environment of a run in the clone, as the close gives its runs (DEC-500): no test-runner or interpreter
    switch of the caller's; the clone's own ``src/`` first where it has one."""
    from gov.close import command as _close

    env = {key: value for key, value in os.environ.items()
           if key not in _close._TEST_RUNNER_VARIABLES and not key.startswith("GIT_")
           and (not key.startswith(_close._INTERPRETER_VARIABLES) or key in _close._INTERPRETER_PLACES
                or key == "PYTHONPATH")}
    if (Path(clone) / "src").is_dir():
        env["PYTHONPATH"] = str(Path(clone) / "src")
    return env


def slot_configured() -> str | None:
    """None where the machine names its heavy-job slots; else why a run takes none."""
    try:
        from gov.resources import config as configuration
        conf = configuration.load()
    except Exception as e:  # noqa: BLE001 - a configuration that cannot be read gives no slot, named
        return f"the machine's configuration cannot be read ({type(e).__name__})"
    if "heavy_slots" in conf.get("values", {}):
        return None
    return "no heavy-job slots are configured (heavy_slots); the run took no slot"


def run_pytest(clone: Path, targets: list[str], options: list[str], junit: Path, log: Path, timeout: float,
               env: dict | None = None, workers: int | None = None) -> dict:
    """One ``pytest`` run of ``targets`` in the clone: ``{"exit", "timed_out", "slot", "junit", "log"}``."""
    clone, junit, log = Path(clone), Path(junit), Path(log)
    junit.parent.mkdir(parents=True, exist_ok=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    if junit.exists():
        junit.unlink()
    pytest = [sys.executable, "-m", "pytest", *targets, *options, f"--junitxml={junit}", "--rootdir", str(clone),
              "-q", "--no-header"]
    limited = ["timeout", "-k", "10", str(int(max(1, timeout))), *pytest] if shutil.which("timeout") else pytest
    command = [sys.executable, "-c", _LAUNCH, str(log), str(clone), *limited]
    env = test_env(clone) if env is None else env
    no_slot = slot_configured()
    if no_slot is None:
        from gov.resources.slots import run as in_slot
        try:
            code = in_slot("test", command, workers=workers or 1, tree=str(clone), env=env)
            slot = "test"
        except Exception as e:  # noqa: BLE001 - a slot refused: the run did not happen, named
            return {"exit": None, "timed_out": False, "slot": f"refused: {e}", "junit": str(junit), "log": str(log)}
    else:
        code = subprocess.run(command, env=env).returncode
        slot = no_slot
    return {"exit": code, "timed_out": code in TIMED_OUT_EXITS, "slot": slot, "junit": str(junit), "log": str(log)}


def failure_type(message: str | None, text: str | None) -> str:
    """The failure's type: the exception named (``AssertionError`` for a bare assert), ``timeout`` for a time
    limit, ``unknown`` where none is named."""
    message, text = (message or "").strip(), text or ""
    if re.search(r"\bTimeout\b", message) or re.search(r"Failed: Timeout|\+\+\+ Timeout \+\+\+", text):
        return TIMEOUT
    quoted = re.match(r'failed on (?:setup|teardown|call) with "(.*)"', message, re.S)
    if quoted:
        message = quoted.group(1).strip()
    if message.startswith("assert"):
        return "AssertionError"
    head = message.split(":", 1)[0].strip()
    if re.fullmatch(r"[A-Za-z_][\w.]*", head) and (head[0].isupper() or "." in head):
        return head.rsplit(".", 1)[-1]
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("E "):
            continue
        body = line[1:].strip()
        if body.startswith("assert"):
            return "AssertionError"
        named = re.match(r"([A-Za-z_][\w.]*(?:Error|Exception|Exit|Interrupt|Failed|Failure))\b", body)
        if named:
            return named.group(1).rsplit(".", 1)[-1]
    return UNKNOWN


def _node(clone: Path, case) -> str:
    file = case.get("file") or ""
    classname, name = case.get("classname") or "", case.get("name") or ""
    if not file:  # a collection error names the module in ``name``, dotted
        return name.replace(".", "/") + ".py" if not classname else f"{classname.replace('.', '/')}.py::{name}"
    module = file[:-3].replace("/", ".") if file.endswith(".py") else ""
    classes = classname[len(module):].strip(".") if module and classname.startswith(module) else ""
    return "::".join([file] + [c for c in classes.split(".") if c] + [name])


def read_results(junit: Path, clone: Path) -> dict | None:
    """What a JUnit file states: the counts and each failing test with its type; None where it is missing or broken."""
    try:
        tree = ET.parse(junit)
    except (OSError, ET.ParseError):
        return None
    counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    failures = []
    for case in tree.iter("testcase"):
        node = _node(Path(clone), case)
        bad = case.findall("failure") + case.findall("error")
        if bad:
            counts["failed" if case.findall("failure") else "errors"] += 1
            element = bad[0]
            failures.append({"test": node, "failure_type": failure_type(element.get("message"), element.text),
                             "text": ((element.text or "").strip() or element.get("message") or "")[:2000]})
        elif case.findall("skipped"):
            counts["skipped"] += 1
        else:
            counts["passed"] += 1
    return {**counts, "failures": failures}


def run_alone(clone: Path, test: str, options: list[str], folder: Path, timeout: float, tag: str) -> str | None:
    """``test`` run alone in its own process: None green; its failure type red; ``absent`` where it cannot be run
    (not collected, a usage error); ``timeout`` at the limit."""
    safe = re.sub(r"[^\w.-]+", "_", f"{tag}-{test}")[-150:]
    done = run_pytest(clone, [test], [o for o in options if not o.startswith("-n")], folder / f"{safe}.xml",
                      folder / f"{safe}.log", timeout)
    if done["exit"] is None:
        return UNKNOWN
    if done["timed_out"]:
        return TIMEOUT
    if done["exit"] in (4, 5):
        return ABSENT
    results = read_results(Path(done["junit"]), clone)
    if results is None:
        return UNKNOWN
    if done["exit"] == 0 and not results["failures"]:
        return None
    if results["failures"]:
        return results["failures"][0]["failure_type"]
    return UNKNOWN


# ---------------------------------------------------------------------------
# The judgement of a red (S4)
# ---------------------------------------------------------------------------

def judge(with_change: list[str | None], without: list[str | None]) -> tuple[bool, str, str]:
    """``(caused, failure_type, reason)`` of one red from its runs alone with the change and without it (one each
    way, or the load-sensitive rounds). Not the change's only if the head without the change has it red with the
    same failure type, in as many rounds as decide it; a timeout, an unknown type or an absent case never match."""
    reds = [t for t in with_change if t is not None]
    if not reds:
        return False, UNKNOWN, (f"green when run alone ({len(with_change)} of {len(with_change)} rounds): a flaky "
                                "candidate, not a red of the change")
    kind = max(dict.fromkeys(reds), key=reds.count)
    rounds = max(len(with_change), 1)
    same = sum(1 for t in without if t == kind and kind not in NEVER_MATCH)
    seen = ", ".join(sorted({"green" if t is None else t for t in without})) or "not run"
    if kind in NEVER_MATCH:
        return True, kind, f"red alone with {kind}, which never matches the head without the change ({seen} there)"
    if same == 0 or 2 * (len(reds) - same) >= rounds:
        return True, kind, (f"red alone with {kind} ({len(reds)}/{rounds}); the head without the change: {seen} "
                            f"(same failure type in {same}/{len(without)})")
    return False, kind, (f"red alone with {kind} ({len(reds)}/{rounds}) and red with the same failure type on the "
                         f"head without the change ({same}/{len(without)}): not caused by the change")


def load_sensitive(clone: Path, test: str) -> bool:
    """Whether the test is load-sensitive: an entry of the serial phase's own list
    (``gov.close.pytest_plugin.gov_close_serial_only.LIST_REL``) names it and that entry's comment's kind is
    ``latency`` (``<entry>  # serial: latency: <reason>``), in the tested code. The serial phase's own reading; no
    accepted-reds or ``load_sensitive`` list is read (F2), and no pytest marker counts."""
    from gov.close.pytest_plugin.gov_close_serial_only import LIST_REL, declares

    try:
        text = (Path(clone) / LIST_REL).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    node = _plain(test)
    for line in text.lstrip("\ufeff").splitlines():
        entry, _, comment = (" " + line.replace("\t", " ")).partition(" #")
        entry = _plain(entry.strip())
        if entry and _kind(comment) == LATENCY and (declares(entry, node) or declares(entry.rstrip("/"), node)):
            return True
    return False


def _plain(node: str) -> str:
    """A node id or list entry in one spelling: ``/`` separators, no leading ``./``."""
    node = node.replace("\\", "/")
    while node.startswith("./"):
        node = node[2:]
    return node


def _kind(comment: str) -> str | None:
    """The kind of an entry's comment ``<route>: <kind>: <reason>``: the word after the route, lower case, whatever
    follows it (a reason, a parenthesis, nothing); a comment whose first word is itself a kind of the list's (the
    route left out, which the serial phase keeps in the close) gives that word. None where there is no comment."""
    words = [w.strip().lower() for w in comment.split(":")]
    first = re.match(r"[\w-]+", words[0]) if words else None
    if first is None:
        return None
    if first.group(0) == LATENCY:
        return LATENCY
    second = re.match(r"[\w-]+", words[1]) if len(words) > 1 else None
    return second.group(0) if second else None


def nightly_reading(root: Path) -> dict:
    """The newest nightly record (``docs/close/nightly/*.json``): ``{"read", "record", "head", "failures"}``,
    read first (S4); ``read`` False where there is none that can be read."""
    from gov.close.select import NIGHTLY_REL

    for path in sorted((Path(root) / NIGHTLY_REL).glob("*.json"), reverse=True):
        try:
            night = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(night, dict) or not isinstance(night.get("head"), str):
            continue
        failures = {}
        for f in night.get("failures") or []:
            if isinstance(f, dict) and isinstance(f.get("test"), str):
                red = f.get("class", "red") == "red"
                failures[f["test"]] = failure_type(f.get("failure_type") or "", f.get("text") or "") if red else None
        return {"read": True, "record": path.relative_to(root).as_posix(), "head": night["head"],
                "scope": night.get("scope"), "failures": failures}
    return {"read": False, "record": None, "head": None, "scope": None, "failures": {}}


def _same_commit(clone: Path, a: str | None, b: str | None) -> bool:
    if not a or not b:
        return False
    one = _git(clone, "rev-parse", "--verify", "--quiet", f"{a}^{{commit}}").stdout.strip()
    two = _git(clone, "rev-parse", "--verify", "--quiet", f"{b}^{{commit}}").stdout.strip()
    return bool(one) and one == two


def attribute(root: Path, clone: Path, commit: str, base: str | None, failing: list[dict], options: list[str],
              folder: Path, timeout: float) -> tuple[list[dict], dict]:
    """Each failing test of a run judged (S4): ``(reds, nightly)``. ``reds``: ``{test, failure_type, caused,
    reason}``; ``nightly``: ``{read, record}``. The clone is left at ``commit``."""
    night = nightly_reading(root)
    tests = list(dict.fromkeys(f["test"] for f in failing))
    rounds = {t: LOAD_SENSITIVE_ROUNDS if load_sensitive(clone, t) else 1 for t in tests}
    with_change = {t: [run_alone(clone, t, options, folder, timeout, f"with-{n}") for n in range(rounds[t])]
                   for t in tests}
    without: dict[str, list[str | None]] = {}
    free = night["read"] and night.get("scope") == "full" and _same_commit(clone, night["head"], base)
    to_run, from_night = [], set()
    for t in tests:
        if not any(r is not None for r in with_change[t]):
            continue  # green alone: nothing to compare
        # the night ran the full suite on the head without the change: its result stands for that run, free, only
        # where it excuses the red (red there with the same failure type); else the red is run there once, as every
        # other red is; a load-sensitive red still gets its rounds run
        if free and rounds[t] == 1 and not judge(with_change[t], [night["failures"].get(t)])[0]:
            without[t] = [night["failures"].get(t)]
            from_night.add(t)
        else:
            to_run.append(t)
    if to_run:
        if base is None:
            for t in to_run:
                without[t] = [ABSENT] * rounds[t]
        else:
            try:
                checkout(clone, base)
                for t in to_run:
                    without[t] = [run_alone(clone, t, options, folder, timeout, f"without-{n}")
                                  for n in range(rounds[t])]
            except CloneError:
                for t in to_run:
                    without.setdefault(t, [UNKNOWN] * rounds[t])
            finally:
                checkout(clone, commit)
    reds = []
    for t in tests:
        caused, kind, reason = judge(with_change[t], without.get(t, []))
        if base is None and any(r is not None for r in with_change[t]):
            reason += "; no head without the change is known (the ticket has no commit of its own)"
        if t in from_night:
            reason += f"; the head without the change read from the nightly record {night['record']}"
        if kind == UNKNOWN:
            kind = next((f["failure_type"] for f in failing if f["test"] == t), UNKNOWN)
        reds.append({"test": t, "failure_type": kind, "caused": caused, "reason": reason,
                     "rounds": rounds[t]})
    return reds, {"read": night["read"], "record": night["record"]}
