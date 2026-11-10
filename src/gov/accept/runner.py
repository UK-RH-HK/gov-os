"""The opaque acceptance runner behind ``gov accept`` (W2-96, DEC-959 item 6, DEC-820 (c)).

It runs a ticket's acceptance folder with pytest in a child process whose output goes to the null device, reads
only each case's file, function name and outcome from the child's JUnit file, and reports pass or fail per KPI
line of the folder's README map, with counts. Nothing of the tests' content (a name, a message, a traceback, a
captured output, a path inside the folder) reaches the caller: a run that goes wrong is reported by its kind
alone, and any exception of the runner's own is a ``crash`` with no message. It fails closed: a line no test
proves fails, and a README with no map refuses rather than falling back to raw output.
"""

from __future__ import annotations

import json
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

KIND = r"(successes|success|failures|failure|kpis|kpi|s|f|k)"
NAME = re.compile(KIND + r"[ \t-]*(\d+)(?!\w)", re.I)
NAMING = re.compile(r"(success|failure|kpi)\b", re.I)  # a heading that means to name lines
JOINED = r"\s*(?:[/,;&+]\s*(?:(?:and|or)\b)?|\b(?:and|or)\b)\s*"  # S1 / S2, S1, and S2, S1 and S2, S1 or F2
JOIN = re.compile(JOINED, re.I)
NUMBER = re.compile(r"(\d+)(?!\w)(?![ \t]+(?!and\b)[a-z])", re.I)  # a bare number after a join: one more line of
#                                                                   the kind before it ("failures 4, 5"), not a count
UPTO = re.compile(r"(?:–|\.\.|-)(?:" + KIND + r"[ \t]*)?(\d+)(?!\w)"  # a range: Success 3–7, S3-7, F1..3, S2-S4
                  r"|[ \t]+to[ \t]+(?:" + KIND + r"[ \t]*)?(\d+)(?!\w)(?![ \t]+(?!and\b)[a-z])", re.I)  # S1 to 3
NOTE = re.compile(r"\s*(?:\[[^\]\n]*\]|\([^)\n]*\))")  # a bracketed note between lines: [CAP-61.c], (R3)
MORE = re.compile(JOINED + r"(?:(?:successes|success|failures|failure|kpis|kpi)\b|[sfk]?[ \t-]*\d)"
                  r"|(?:–|\.\.|-)\d", re.I)  # what still lists a line the reader did not read: the cell is refused
FURTHER = re.compile(r"(?<![\w'’-])" + KIND + r"[ \t-]*(\d+)(?!\w)", re.I)  # a line named anywhere after the list
LEADS = re.compile(r"(?:[/,;&+(\[]|\b(?:and|or|with)\b)[ \t]*$", re.I)  # what before a further name lists it
POSSESSIVE = re.compile(r"['’]s\b", re.I)  # "F1's fixture": a reference to something of the line's, not a listing
CODE = re.compile(r"`[^`\n]*`")  # a test or file name in the cell: never read for line names
RANGE_MAX = 50  # the widest range read as lines; a wider one is refused
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

class Unlisted(Unreadable):
    """A cell that lists a KPI line the reader cannot read (S-D10b): the map is refused, naming the cell."""


def line_names(text: str) -> list[str]:
    """Every KPI line named at the start of ``text``, in the normal form ``success-N`` / ``failure-N`` (S-D10b).

    A cell lists lines as kinds and numbers joined by ``/``, ``,``, ``;``, ``&``, ``+`` or ``and``: ``Success 4
    [CAP-61.c], failures 4, 5`` is success-4, failure-4 and failure-5 (a bare number is one more line of the kind
    before it; a bracketed note between lines is passed over), and ``Success 3–7`` is the five lines of the range.
    What follows the lines is the cell's prose. Every further line name in it, notes included (test and file names
    in backticks aside), is read or refused, never dropped: one a join leads (``, and failure 1``, ``with success
    4``, ``(and failure 2)``, ``— and F2``, ``(S1)``) is read, with any list it starts; one that names only lines
    already read (``KPI 1 (S1; …)``) changes nothing; any other (``item F2``, ``F1's fixture``) refuses the cell.
    Raises ``Unlisted`` when the cell lists a line the reader cannot read, so that no line is ever dropped silently.
    """
    text = text.replace("*", "").strip()
    if not NAME.match(text):
        return []
    names: list[str] = []
    spans: list[tuple[int, int]] = []  # the stretches of the cell its line names were read from
    _read_list(text, 0, names, spans)
    scan = CODE.sub(lambda code: " " * len(code.group()), text)
    for further in FURTHER.finditer(scan, spans[0][1]):
        if any(start <= further.start() < stop for start, stop in spans):
            continue
        if LEADS.search(scan, 0, further.start()) and not POSSESSIVE.match(scan, further.end()):
            _read_list(text, further.start(), names, spans)
        elif not set(_read_name(text, further, "success")[1]) <= set(names):
            raise Unlisted(text)
    return list(dict.fromkeys(names))


def _read_name(text: str, found: re.Match, kind: str) -> tuple[str, list[str], int]:
    """A name (or a bare number of the kind before it) and any range after it: its kind, lines and end."""
    if found.re is not NUMBER:
        kind = "failure" if found.group(1).lower().startswith("f") else "success"
    first = last = int(found.group(found.re.groups))
    upto = UPTO.match(text, found.end())
    if upto:
        again, number = (upto.group(1), upto.group(2)) if upto.group(2) else (upto.group(3), upto.group(4))
        if again and ("failure" if again.lower().startswith("f") else "success") != kind:
            raise Unlisted(text)  # S1-F3: a range across kinds
        last = int(number)
        if not first < last <= first + RANGE_MAX:
            raise Unlisted(text)
    return kind, [f"{kind}-{number}" for number in range(first, last + 1)], (upto or found).end()


def _read_list(text: str, at: int, names: list[str], spans: list[tuple[int, int]]) -> None:
    """Read the list of lines that starts with the name at ``at`` into ``names``, and its stretch into ``spans``;
    raises ``Unlisted`` when what follows it still lists a line it cannot read."""
    found, kind, end = NAME.match(text, at), "success", at
    while found:
        kind, lines, stop = _read_name(text, found, kind)
        names += lines
        spans.append((found.start(), stop))
        end = stop
        while note := NOTE.match(text, end):
            end = note.end()
        joined = JOIN.match(text, end)
        found = joined and (NAME.match(text, joined.end()) or NUMBER.match(text, joined.end()))
    if MORE.match(text, end):
        raise Unlisted(text)


def _cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def parse_map(text: str) -> dict[str, list[str]]:
    """``{line: [item, ...]}`` from the README's tables, in row form (a KPI column) or heading form.

    Raises ``Unreadable`` for a row with items whose KPI cell names no line, or a table under a heading that
    begins with ``success``, ``failure`` or ``KPI`` but names no line; and ``Unlisted``, carrying the README's line
    number and the cell, for a row with items whose KPI cell (or heading) lists a line it cannot read (S-D10b).
    """
    mapping: dict[str, list[str]] = {}
    heading: list[str] = []
    unlisted = None  # the nearest heading's refusal, raised only if a row under it maps items
    naming = False  # the nearest heading means to name lines
    fenced, table = False, None  # table: None before a header row, False when ignored, else (kpi, test, names)
    for number, raw in enumerate(text.splitlines(), 1):
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
                try:
                    heading, unlisted = line_names(title), None
                except Unlisted:
                    heading, unlisted = [], Unlisted(number, title)
                naming = bool(NAMING.match(title))
            continue
        cells = _cells(line)
        if table is None:
            titles = [cell.lower() for cell in cells]
            kpi = next((i for i, title in enumerate(titles) if title.startswith("kpi")), None)
            test = next((i for i, title in enumerate(titles) if title.startswith(("test", "file"))), None)
            table = False if test is None else (kpi, test, heading, unlisted)
            continue
        if not table or all(SEPARATOR.fullmatch(cell) for cell in cells):
            continue
        kpi, test, names, refusal = table
        items = ITEM.findall(cells[test]) if test < len(cells) else []
        if not items:
            continue
        if kpi is not None:
            try:
                names = line_names(cells[kpi]) if kpi < len(cells) else []
            except Unlisted:
                raise Unlisted(number, cells[kpi]) from None
        elif refusal is not None:
            raise refusal
        if not names and (kpi is not None or naming):
            raise Unreadable
        for name in names:
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


# --- the opt-in suites the map's cases need (S-D10a, DEC-1112 (3), DEC-1061) -----------------------------------------

OPTIN_ENV = "GOV_TESTS_OPTIN"  # tests/conftest.py's variable: the suites a run opts in to, comma-separated
OPTIN_GLOB = "optin-lifted*.txt"


def optin_name(listing: str) -> str:
    """The suite a list belongs to, as ``tests/conftest.py`` names it: ``breadth`` for every
    ``optin-lifted*breadth*.txt``, ``lifted`` for every other ``optin-lifted*.txt``."""
    return "breadth" if "breadth" in listing else "lifted"


def optin_entries(tests: Path) -> list[tuple[str, str]]:
    """``(suite, target)`` for every entry of the project's opt-in lists, read as ``tests/conftest.py`` reads them
    (a ``rep:`` entry's target too: its rows past the first are the suite's). A list it cannot read gives none."""
    entries = []
    for listing in sorted(tests.glob(OPTIN_GLOB)):
        try:
            text = listing.read_text(encoding="utf-8")
        except (OSError, ValueError):
            continue
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if line.startswith("rep:"):
                line = line[len("rep:"):].strip()
            if line:
                entries.append((optin_name(listing.name), line))
    return entries


def _item_parts(item: str) -> tuple[str | None, str | None, bool] | None:
    """A map item as ``(file, function, bare word)`` (``None`` for any), as ``matches`` reads it; ``None`` for an
    item that names no case."""
    item = item.strip()
    if "::" in item:
        path, *rest = item.split("::")
        return (path if path.endswith(".py") else None), rest[-1], False
    if item.endswith(".py"):
        return item, None, False
    return (None, item, True) if WORD.fullmatch(item) else None


def _files_under(root: Path, target: Path, file: str) -> bool:
    """Whether a test file under the folder ``target`` is one the item's ``file`` names."""
    try:
        return any(_same_file(file, path.relative_to(root).as_posix()) for path in target.rglob("*.py"))
    except (OSError, ValueError):
        return True  # cannot tell: the suite is taken, which only runs more of the ticket's own cases


def _needs(root: Path, item: str, target: Path, part: str) -> bool:
    """Whether the entry (its path ``target``, its node part ``part``) may leave out a case the item names."""
    parts = _item_parts(item)
    if parts is None:
        return False
    file, function, word = parts
    if file is not None:
        relative = target.relative_to(root).as_posix()
        if target.suffix == ".py" or part:
            if not _same_file(file, relative):
                return False
        elif not _files_under(root, target, file):
            return False
    if not part or function is None:
        return True
    last = part.split("::")[-1]
    if "::" not in part and not last.startswith("test"):
        return True  # a class: any of its functions
    entry = last.split("[")[0]
    if word:
        return entry in (function, "test_" + function)
    if entry != function.split("[")[0]:
        return False
    return "[" not in last or "[" not in function or last == function


def needed_optins(root: Path, folder: Path, mapping: dict) -> list[str]:
    """The opt-in suites whose lists leave out of a default run a case the map names (S-D10a): an entry that is the
    ticket's folder or a folder above it leaves out every case; one inside it, the cases it names. Only the ticket's
    folder is run with them, so they reach no other ticket's cases. Wider, never narrower: a suite taken that
    leaves out none of the named cases only runs more of the ticket's own."""
    items = {item for listed in mapping.values() for item in listed}
    suites: set[str] = set()
    for suite, entry in optin_entries(root / "tests"):
        if suite in suites:
            continue
        path, _, part = entry.partition("::")
        try:
            target = (root / path.rstrip("/")).resolve()
        except (OSError, RuntimeError, ValueError):
            continue
        if not part and (target == folder or folder.is_relative_to(target)):
            if any(_item_parts(item) is not None for item in items):
                suites.add(suite)
        elif target != folder and target.is_relative_to(folder):
            if any(_needs(root, item, target, part) for item in items):
                suites.add(suite)
    return sorted(suites)


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


LEFT_OUT_PLUGIN = "gov_accept_left_out"  # the child's plugin that records the cases a list leaves out of the run
LEFT_OUT_SOURCE = '''import json


def pytest_deselected(items):
    with open({path!r}, "a", encoding="utf-8") as out:
        for item in items:
            out.write(json.dumps([item.nodeid.split("::")[0], item.name]) + "\\n")
'''


def _left_out(path: Path) -> list[Case]:
    """The cases the child left out of the run, by file and name, as its plugin recorded them."""
    if not path.is_file():
        return []
    return [Case(str(file), str(name), "left out")
            for file, name in (json.loads(row) for row in path.read_text(encoding="utf-8").splitlines() if row)]


def _run(root: Path, folder: Path, timeout: float, optins: list[str] = (),
         left_out: list | None = None) -> tuple[str | None, list[Case]]:
    """(error kind or None, cases): pytest in a child process, all its files in one private folder removed after.

    With a ``left_out`` list, the cases the run leaves out (an opt-in list's, as ``pytest_deselected`` names them)
    are added to it by file and name, read like the cases themselves: never their content.

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
        env.pop(OPTIN_ENV, None)  # exactly the suites the map's cases need, none of the caller's (S-D10a)
        if optins:
            env[OPTIN_ENV] = ",".join(optins)
        command = [sys.executable, "-B", "-m", "pytest", str(folder), f"--rootdir={root}", "-p", "no:cacheprovider",
                   f"--junitxml={report}", "-o", "junit_family=xunit1", "-o", "junit_logging=no",
                   "-o", "junit_log_passing_tests=false", f"--log-file={os.devnull}"]
        if left_out is not None:  # the plugin sits in the private folder, removed with it
            plugins, recorded = private / "plugins", private / "left-out.jsonl"
            plugins.mkdir()
            (plugins / f"{LEFT_OUT_PLUGIN}.py").write_text(LEFT_OUT_SOURCE.format(path=str(recorded)),
                                                           encoding="utf-8")
            env["PYTHONPATH"] += os.pathsep + str(plugins)
            command += ["-p", LEFT_OUT_PLUGIN]
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
        if left_out is not None:
            left_out.extend(_left_out(recorded))
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


REPORT_ONLY = "lifted"  # the suite a formal accept never enables: its cases are report-only (DEC-1061 (2), DEC-1112 (3))


def _result(ticket: str, outcome: str, kind: str | None, lines: list, unmapped: dict, totals: dict,
            optins: list[str] = (), report_only: list[str] = ()) -> dict:
    result = {"ticket": ticket, "outcome": outcome, "error_kind": kind, "lines": lines, "unmapped": unmapped,
              "totals": totals}
    if optins:  # the opt-in suites the run enabled for the map's cases, by name (S-D10a)
        result["optin"] = list(optins)
    if report_only:  # the suites the map's cases need that the run leaves out, their lines report-only (scope (b))
        result["report_only"] = list(report_only)
    return result


def _report(ticket: str, mapping: dict, cases: list[Case], optins: list[str] = (), left_out: list[Case] = (),
            report_only: list[str] = ()) -> tuple[dict, int]:
    """The result: per line, pass or fail on the cases that ran; ``report-only`` for a line that ran none and whose
    every item names a case the ``lifted`` list left out (``left_out``), which fails nothing by itself. A line
    with cases left out and others run is measured on those that ran; a line that ran none otherwise fails."""
    counts, unmapped, totals = {name: _zero() for name in mapping}, _zero(), _zero()
    for case in cases:
        totals[case.outcome] += 1
        hits = [name for name, items in mapping.items() if any(matches(item, case) for item in items)]
        for name in hits:
            counts[name][case.outcome] += 1
        if not hits:
            unmapped[case.outcome] += 1

    def held(item: str) -> bool:  # the item names a case the run left out
        return any(matches(item, case) for case in left_out)

    missing = {name for name, items in mapping.items()  # a named test no case matches fails its line, unnamed;
               if any(names_a_test(item) and not held(item) and not any(matches(item, case) for case in cases)
                      for item in items)}
    lines = []
    for name in ordered(mapping):  # counts: tests run
        count = counts[name]
        if not any(count.values()) and mapping[name] and all(held(item) for item in mapping[name]):
            lines.append({"kpi": name, "outcome": "report-only", "note": f"report-only ({REPORT_ONLY})", **count})
            continue
        good = count["passed"] and not count["failed"] and name not in missing
        lines.append({"kpi": name, "outcome": "pass" if good else "fail", **count})
    measured = [line for line in lines if line["outcome"] != "report-only"]
    passed = (bool(measured) and all(line["outcome"] == "pass" for line in measured)  # a run measuring no line fails
              and not totals["failed"])  # any failed case, mapped or not
    return (_result(ticket, "pass" if passed else "fail", None, lines, unmapped, totals, optins, report_only),
            0 if passed else EXIT_FAIL)


TEST_NAME = re.compile(r"`[^`]*`|[^\s,;]*(?:\.py\b|::)[^\s,;]*|\btest_\w*")
CELL_MAX = 120


def _masked(cell: str) -> str:
    """The refused cell as named to the caller: its KPI lines and prose, never a test or file name it holds."""
    cell = TEST_NAME.sub("…", cell)
    return cell if len(cell) <= CELL_MAX else cell[:CELL_MAX - 1] + "…"


def accept(root: Path, ticket: str, timeout: float) -> tuple[dict, int]:
    """``gov accept``'s result and exit code; a refusal is a ``GovError`` naming only the ticket and its path (and,
    for a map cell listing a line it cannot read, the README's line number and the cell, test names masked)."""
    root = Path(root).resolve()
    ticket, front = _ticket(root, ticket)
    folder, declared = _folder(root, ticket, front)
    error = _result(ticket, "error", "crash", [], _zero(), _zero()), EXIT_ERROR
    try:
        readme = folder / "README.md"
        mapping = parse_map(readme.read_text(encoding="utf-8")) if readme.is_file() else {}
    except Unlisted as refusal:
        number, cell = refusal.args
        cell = _masked(cell)
        raise GovError("ACCEPT_MAP_UNREADABLE", f"ticket {ticket}: the README of {declared} has a map cell listing "
                       f"a KPI line it cannot read (README line {number}: {cell!r})",
                       {"ticket": ticket, "path": declared, "line": number, "cell": cell}) from None
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
        needed = needed_optins(root, folder, mapping)
        optins = [suite for suite in needed if suite != REPORT_ONLY]  # breadth only, never lifted (scope (b))
        report_only = [REPORT_ONLY] if REPORT_ONLY in needed else []
        error = _result(ticket, "error", "crash", [], _zero(), _zero(), optins, report_only), EXIT_ERROR  # F3
        left_out: list[Case] | None = [] if report_only else None
        kind, cases = _run(root, folder, timeout, optins, left_out)
        if kind is None:
            return _report(ticket, mapping, cases, optins, left_out or [], report_only)
        error = _result(ticket, "error", kind, [], _zero(), _zero(), optins, report_only), EXIT_ERROR
    except Stopped as stopped:  # the run is stopped and cleaned up: gov ends as the signal asked
        raise SystemExit(128 + stopped.args[0]) from None
    except Exception:  # any exception of the runner's own is a crash, with no message
        pass
    return error
