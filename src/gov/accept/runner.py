"""The opaque acceptance runner behind ``gov accept`` (W2-96, DEC-959 item 6, DEC-820 (c)).

It runs a ticket's acceptance folder with pytest in a child process whose output goes to the null device, reads
only each case's file, function name and outcome from the child's JUnit file, and reports pass or fail per KPI
line of the folder's README map, with counts. Nothing of the tests' content (a name, a message, a traceback, a
captured output, a path inside the folder) reaches the caller: a run that goes wrong is reported by its kind
alone, and any exception of the runner's own is a ``crash`` with no message. It fails closed: a line no test
proves fails, and a README with no map refuses rather than falling back to raw output.
"""

from __future__ import annotations

import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import NamedTuple

from gov.cli.errors import GovError

NAME = re.compile(r"(success|failure|kpi|s|f|k)[ \t-]*(\d+)(?!\w)", re.I)
NAMING = re.compile(r"(success|failure|kpi)\b", re.I)  # a heading that means to name lines
JOIN = re.compile(r"\s*(?:/|,|;|\band\b)\s*", re.I)
ITEM = re.compile(r"`([^`]+)`")
WORD = re.compile(r"\w+")
SEPARATOR = re.compile(r":?-+:?")
SAFE_TICKET = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
OUTCOMES = ("passed", "failed", "skipped")
EXIT_FAIL, EXIT_ERROR = 3, 4


class Case(NamedTuple):
    file: str     # relative to the project root, as pytest names it
    name: str     # the function name, with any parameter id
    outcome: str  # passed, failed or skipped


class Unreadable(Exception):
    """A map row (or a naming heading) whose line names the reader does not take: the run is refused."""


class Stopped(BaseException):
    """SIGINT, SIGTERM or SIGHUP during the run: it is stopped and cleaned up, and ``gov`` exits 128 plus the signal."""


# --- the README map -------------------------------------------------------------------------------------------------

def line_names(text: str) -> list[str]:
    """The KPI lines named at the start of ``text``, in the normal form ``success-N`` / ``failure-N``."""
    text = text.replace("*", "").strip()
    names, found = [], NAME.match(text)
    while found:
        kind = "failure" if found.group(1).lower() in ("failure", "f") else "success"
        names.append(f"{kind}-{int(found.group(2))}")
        joined = JOIN.match(text, found.end())
        found = NAME.match(text, joined.end()) if joined else None
    return names


def _cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def parse_map(text: str) -> dict[str, list[str]]:
    """``{line: [item, ...]}`` from the README's tables, in row form (a KPI column) or heading form.

    Raises ``Unreadable`` for a row with items whose KPI cell names no line, or a table under a heading that
    begins with ``success``, ``failure`` or ``KPI`` but names no line.
    """
    mapping: dict[str, list[str]] = {}
    heading: list[str] = []
    naming = False  # the nearest heading means to name lines
    fenced, table = False, None  # table: None before a header row, False when ignored, else (kpi, test, names)
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith(("```", "~~~")):
            fenced, table = not fenced, None
            continue
        if fenced:
            continue
        if not line.startswith("|"):
            table = None
            if line.startswith("#"):
                title = line.lstrip("#").replace("*", "").strip()
                heading, naming = line_names(title), bool(NAMING.match(title))
            continue
        cells = _cells(line)
        if table is None:
            titles = [cell.lower() for cell in cells]
            kpi = next((i for i, title in enumerate(titles) if title.startswith("kpi")), None)
            test = next((i for i, title in enumerate(titles) if title.startswith(("test", "file"))), None)
            table = False if test is None else (kpi, test, heading)
            continue
        if not table or all(SEPARATOR.fullmatch(cell) for cell in cells):
            continue
        kpi, test, names = table
        if kpi is not None:
            names = line_names(cells[kpi]) if kpi < len(cells) else []
        items = ITEM.findall(cells[test]) if test < len(cells) else []
        if items and not names and (kpi is not None or naming):
            raise Unreadable
        for name in names if items else []:
            mapping.setdefault(name, []).extend(items)
    return mapping


def ordered(mapping: dict) -> list[str]:
    """The lines in order: ``success-1…``, then ``failure-1…``."""
    return sorted(mapping, key=lambda name: (name.startswith("failure"), int(name.split("-")[1])))


def _same_file(item: str, file: str) -> bool:
    item, file = item.removeprefix("./"), file.removeprefix("./")
    return item == file or file.endswith("/" + item) or item.endswith("/" + file)


def matches(item: str, case: Case) -> bool:
    """Whether the README item (``name.py``, ``name.py::test_x`` or a bare word) names the case."""
    item, function = item.strip(), case.name.split("[")[0]
    if "::" in item:
        path, *rest = item.split("::")
        test = rest[-1]
        same = case.name == test if "[" in test else function == test
        return same and (_same_file(path, case.file) if path.endswith(".py") else True)
    if item.endswith(".py"):
        return _same_file(item, case.file)
    return bool(WORD.fullmatch(item)) and function in (item, "test_" + item)


def names_a_test(item: str) -> bool:
    """Whether the item names a test, so that matching no collected case fails its line."""
    item = item.strip()
    return "::" in item or item.rsplit("/", 1)[-1].startswith("test_")


# --- the child run --------------------------------------------------------------------------------------------------

def read_cases(report: Path) -> tuple[list[Case], bool]:
    """Each case's file, name and outcome, and whether any is a collection error; no element's text is read."""
    from xml.etree import ElementTree

    cases, collection = [], False
    for element in ElementTree.parse(report).iter("testcase"):
        tags = {child.tag for child in element}
        collection = collection or ("error" in tags and element.get("line") is None)
        outcome = "failed" if tags & {"failure", "error"} else "skipped" if "skipped" in tags else "passed"
        cases.append(Case(element.get("file") or "", element.get("name") or "", outcome))
    return cases, collection


def _kill(process: subprocess.Popen) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)  # the whole group: the child and whatever it started
    except OSError:
        pass
    process.wait()


PR_SET_CHILD_SUBREAPER, PR_GET_CHILD_SUBREAPER = 36, 37
REAP_SECONDS = 5.0  # the bound on stopping and reaping the run's processes, after which the clean-up goes on


def _subreaper(on: int) -> int | None:
    """Make ``gov`` the reaper of its descendants' orphans, or not (Linux); the setting it had, None where it cannot."""
    if not sys.platform.startswith("linux"):
        return None
    try:
        import ctypes
        libc, was = ctypes.CDLL(None, use_errno=True), ctypes.c_int()
        if libc.prctl(PR_GET_CHILD_SUBREAPER, ctypes.byref(was), 0, 0, 0) or libc.prctl(
                PR_SET_CHILD_SUBREAPER, on, 0, 0, 0):
            return None
        return was.value
    except Exception:
        return None


def _children(pid: int) -> set[int]:
    """The process's children, from the kernel (each of its threads' own); empty where it cannot read them."""
    found: set[int] = set()
    try:
        for task in os.listdir(f"/proc/{pid}/task"):
            with open(f"/proc/{pid}/task/{task}/children") as file:
                found.update(int(child) for child in file.read().split())
    except (OSError, ValueError):
        pass
    return found


def _reap(before: set[int]) -> None:
    """Stop and reap every process the run started, whatever its session: ``gov``'s children that were not there
    before the run. Only its own children are signalled, by a pid it alone can free, so no other process is ever
    hit; as each one ends, its own children come to ``gov`` (the subreaper) and are stopped in turn. It repeats
    until no such child is left, or the bound; it never raises.
    """
    deadline = time.monotonic() + REAP_SECONDS
    while time.monotonic() < deadline:
        mine = _children(os.getpid()) - before
        if not mine:
            return
        for pid in mine:
            try:
                os.kill(pid, signal.SIGKILL)
                os.waitpid(pid, os.WNOHANG)
            except OSError:
                pass
        time.sleep(0.002)


FOLDER =os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
PASSES = 20  # removal passes before whatever error remains is passed over


class _Moved(Exception):
    """The folder above is no longer the one the removal came down from: this pass ends, the next starts again."""


def _same(fd: int, known: os.stat_result) -> bool:
    now = os.fstat(fd)
    return (now.st_dev, now.st_ino) == (known.st_dev, known.st_ino)


def _remove_pass(folder: str) -> None:
    """One pass over the folder: every entry it can remove is removed, any single entry's error is passed over.

    No recursion and no long path: one folder is open at a time, every name is taken relative to it, each folder
    is listed once (its names still to do kept in a list, so the pass is linear in the entries), and a link is
    removed, never followed. Going up is checked against the folder it came down from, so that a folder another
    process moves away never takes the removal outside the private folder.
    """
    try:
        os.chmod(folder, 0o700)
    except OSError:
        pass
    try:
        fd = os.open(folder, FOLDER)
    except FileNotFoundError:
        return
    above: list[tuple[str, list[str], os.stat_result]] = []  # (the folder's name, its parent's names to do, parent)
    try:
        names = os.listdir(fd)
        while True:
            if names:
                name = names.pop()
                try:
                    mode = os.stat(name, dir_fd=fd, follow_symlinks=False).st_mode
                    if mode & 0o170000 != 0o040000:
                        os.unlink(name, dir_fd=fd)
                        continue
                    os.chmod(name, 0o700, dir_fd=fd)  # down into a folder, after giving it back its permissions
                    parent = os.fstat(fd)
                    inner = os.open(name, FOLDER, dir_fd=fd)
                except OSError:  # gone already, or changed meanwhile: the next pass sees what is left
                    continue
                fd, old = inner, fd
                os.close(old)
                above.append((name, names, parent))
                names = os.listdir(fd)
            elif above:  # up, removing the folder just emptied
                name, names, parent = above.pop()
                fd, old = os.open("..", FOLDER, dir_fd=fd), fd
                os.close(old)
                if not _same(fd, parent):
                    raise _Moved
                try:
                    os.rmdir(name, dir_fd=fd)
                except OSError:  # gone already, or refilled meanwhile: the next pass empties it again
                    pass
            else:
                break
    except (OSError, _Moved):
        pass
    finally:
        os.close(fd)
    try:
        os.rmdir(folder)
    except FileNotFoundError:
        pass


def _remove(folder: str) -> None:
    """Remove the folder and all it holds, whatever its depth, whatever permissions a test took away, and whatever
    a process the run cannot stop changes in it meanwhile; it never raises.

    Passes are repeated, with a short wait between them, until the folder is gone; after a bounded number of
    passes whatever error remains is passed over.
    """
    for attempt in range(PASSES):
        try:
            _remove_pass(folder)
        except OSError:
            pass
        if not os.path.lexists(folder):
            return
        time.sleep(min(0.01 * 2 ** attempt, 0.25))


def _stop(signum, _frame):
    raise Stopped(signum)


STOPS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)


def _run(root: Path, folder: Path, timeout: float) -> tuple[str | None, list[Case]]:
    """(error kind or None, cases): pytest in a child process, all its files in one private folder removed after.

    SIGINT, SIGTERM and SIGHUP stop the run; one that arrives before the private folder is in the try's hands, or
    during the clean-up, is held back and acted on once the clean-up is done. A signal the caller set to be
    ignored stays ignored. Before the folder is removed, every process the run started, in whatever session, is
    stopped and reaped (on Linux, through the subreaper; elsewhere only the child's process group is stopped).
    """
    stops = [signum for signum in STOPS if signal.getsignal(signum) is not signal.SIG_IGN]
    held: list[int] = []

    def hold(signum, _frame):
        held.append(signum)

    previous = {signum: signal.signal(signum, hold) for signum in stops}
    private = process = stopped = subreaper = None
    try:
        private = Path(tempfile.mkdtemp(prefix="gov-accept-"))
        for signum in stops:
            signal.signal(signum, _stop)
        if held:
            raise Stopped(held[0])
        report, temp = private / "report.xml", private / "tmp"
        temp.mkdir()
        env = {key: value for key, value in os.environ.items() if not key.startswith(("PYTEST_", "PYTHON"))}
        env.update(PYTHONPATH=str(root / "src"), PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(temp))
        command = [sys.executable, "-B", "-m", "pytest", str(folder), f"--rootdir={root}", "-p", "no:cacheprovider",
                   f"--junitxml={report}", "-o", "junit_family=xunit1", "-o", "junit_logging=no",
                   "-o", "junit_log_passing_tests=false", f"--log-file={os.devnull}"]
        before, subreaper = _children(os.getpid()), _subreaper(1)  # an orphan of the run comes to gov, not to init
        process = subprocess.Popen(command, cwd=root, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return "timeout", []
        if code in (2, 5):
            return "collection", []
        if code not in (0, 1):  # 3, 4, killed by a signal, anything else
            return "crash", []
        cases, collection = read_cases(report)
        if collection:
            return "collection", []
        if code == 1 and all(case.outcome != "failed" for case in cases):  # "tests failed" with none failed
            return "crash", []
        return None, cases
    except Stopped as error:
        stopped = error
        raise
    finally:
        for signum in stops:
            signal.signal(signum, hold)  # a signal during the clean-up is held back, never cuts it short
        try:
            if process is not None:
                _kill(process)  # the child's own status is taken here, before any reaping
            if subreaper is not None:  # every process of the run, whatever its session, ends before the removal
                try:
                    _reap(before)
                finally:
                    _subreaper(subreaper)
            if private is not None:
                _remove(str(private))
        finally:
            ending = bool(held) or stopped is not None
            for signum, handler in previous.items():  # gov is ending: a later signal changes nothing, never kills it
                signal.signal(signum, signal.SIG_IGN if ending else handler)
        if held and stopped is None:  # held back during the clean-up: now it ends the run
            raise Stopped(held[0])


# --- the command ----------------------------------------------------------------------------------------------------

def _ticket(root: Path, ticket: str) -> tuple[str, dict]:
    """The ticket's id and front matter, by its file name or its WBS id."""
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    folder = root / TICKETS_REL
    if SAFE_TICKET.fullmatch(ticket or ""):
        front = frontmatter(folder / f"{ticket}.md")
        if front is not None:
            return ticket, front
        for path in sorted(folder.glob("*.md")):
            try:
                if ticket not in path.read_text(encoding="utf-8", errors="replace"):
                    continue
            except OSError:
                continue
            front = frontmatter(path)
            if front is not None and str(front.get("wbs_id")) == ticket:
                return path.stem, front
    raise GovError("ACCEPT_UNKNOWN_TICKET", f"no ticket {ticket}", {"ticket": ticket})


def _folder(root: Path, ticket: str, front: dict) -> tuple[Path, str]:
    """The ticket's acceptance folder, a folder strictly inside the root, and its declared path."""
    tests = front.get("acceptance_tests")
    declared = tests.get("path") if isinstance(tests, dict) else None
    if isinstance(declared, str) and declared.strip():
        try:
            folder = (root / declared).resolve()
            if folder != root and folder.is_relative_to(root) and folder.is_dir():
                return folder, declared
        except (OSError, ValueError):
            pass
    raise GovError("ACCEPT_NO_TESTS", f"ticket {ticket} has no acceptance folder inside the project "
                   f"(declared: {declared})", {"ticket": ticket, "path": declared})


def _zero() -> dict:
    return dict.fromkeys(OUTCOMES, 0)


def _result(ticket: str, outcome: str, kind: str | None, lines: list, unmapped: dict, totals: dict) -> dict:
    return {"ticket": ticket, "outcome": outcome, "error_kind": kind, "lines": lines, "unmapped": unmapped,
            "totals": totals}


def _report(ticket: str, mapping: dict, cases: list[Case]) -> tuple[dict, int]:
    counts, unmapped, totals = {name: _zero() for name in mapping}, _zero(), _zero()
    for case in cases:
        totals[case.outcome] += 1
        hits = [name for name, items in mapping.items() if any(matches(item, case) for item in items)]
        for name in hits:
            counts[name][case.outcome] += 1
        if not hits:
            unmapped[case.outcome] += 1
    missing = {name for name, items in mapping.items()  # a named test no case matches fails its line, unnamed;
               if any(names_a_test(item) and not any(matches(item, case) for case in cases) for item in items)}
    lines = [{"kpi": name, "outcome": "pass" if counts[name]["passed"] and not counts[name]["failed"]
              and name not in missing else "fail", **counts[name]} for name in ordered(mapping)]  # counts: tests run
    passed = all(line["outcome"] == "pass" for line in lines) and not totals["failed"]  # any failed case, mapped or not
    return _result(ticket, "pass" if passed else "fail", None, lines, unmapped, totals), 0 if passed else EXIT_FAIL


def accept(root: Path, ticket: str, timeout: float) -> tuple[dict, int]:
    """``gov accept``'s result and exit code; a refusal is a ``GovError`` naming only the ticket and its path."""
    root = Path(root).resolve()
    ticket, front = _ticket(root, ticket)
    folder, declared = _folder(root, ticket, front)
    error = _result(ticket, "error", "crash", [], _zero(), _zero()), EXIT_ERROR
    try:
        readme = folder / "README.md"
        mapping = parse_map(readme.read_text(encoding="utf-8")) if readme.is_file() else {}
    except Unreadable:
        mapping = None
    except Exception:  # a README it cannot read or decode: never its message
        return error
    if mapping is None:
        raise GovError("ACCEPT_MAP_UNREADABLE", f"ticket {ticket}: the README of {declared} has a map row "
                       "naming no KPI line it can read", {"ticket": ticket, "path": declared})
    if not mapping:
        raise GovError("ACCEPT_NO_MAP", f"ticket {ticket}: the README of {declared} maps no KPI line",
                       {"ticket": ticket, "path": declared})
    try:
        kind, cases = _run(root, folder, timeout)
        if kind is None:
            return _report(ticket, mapping, cases)
        error[0]["error_kind"] = kind
    except Stopped as stopped:  # the run is stopped and cleaned up: gov ends as the signal asked
        raise SystemExit(128 + stopped.args[0]) from None
    except Exception:  # any exception of the runner's own is a crash, with no message
        pass
    return error
