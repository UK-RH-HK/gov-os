"""Support code for the W2-158 acceptance tests (standard library only; nothing here imports ``gov``).

W2-158 delivers ``gov check --structural [<base>] [--timeout <s>]``: one cheap, bounded pass over the tree's own declared
check families (and, with a ``<base>``, portability and ``gov links``), printing one line per family and a last line,
exiting 0 whatever it finds and 2 only when it cannot run (the lead's readings L1-L10, in the brief).

How the code under test is chosen: every run is a child process, ``python3 -m gov.cli.main check --structural ...
--root <planted tree>``, with ``PYTHONPATH`` set to the ``src/`` of the working tree this file is in (the first run of a
session checks that ``gov`` imports from there). Nothing is imported at collection, so a missing option makes the suite
red by failing.

What is planted (all under pytest's ``tmp_path``): a git tree (``git init``, commits; no global git configuration, a
planted HOME) holding declarations ``template/governance/kernel/checks/<id>.yaml`` whose commands are one small
stand-in script, ``checks/marker.py``, which records that it ran (its pid, process group, session, start and end
times, its working folder and the environment L4 names) in a file of its own in a folder OUTSIDE the tree (``marks/``),
and then passes, finds a problem, answers not applicable, or sleeps past the bound. Stand-in ``gov`` sources
(``src/gov/...``) stand for the tree's own built-in checks (F3) and for the tree's own ``gov links`` (S4).
"""

from __future__ import annotations

import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"

SAFE_PATH = "/usr/local/bin:/usr/bin:/bin"
COMMAND_TIMEOUT_S = 60.0   # the bound on a test's wait for the command (never a promise of the ticket)
SLACK_S = 8.0              # "within the bound plus a few seconds": generous, for a loaded machine
BOUND = 2                  # the --timeout most planted cases use, in seconds
SLEEP_S = 120              # how long a stand-in sleeps "past the bound" (the teardown kills it anyway)

FAMILIES = ("schema", "graph", "claims", "mutation", "authority", "pathmap", "audit", "skills")
OUTPUT_ORDER = FAMILIES + ("portability", "links")
IDS = {"schema": "core-schema", "graph": "core-graph", "claims": "core-claims", "mutation": "core-mutation",
       "authority": "core-authority", "pathmap": "core-pathmap", "audit": "audit-reproducibility",
       "portability": "adapter-portability"}
SKILL_IDS = ("skill-regression-a", "skill-regression-b1", "skill-regression-orchestration")
FAMILY_FIELD = {"schema": "schema/invariants", "graph": "graph", "claims": "claims", "mutation": "mutation",
                "authority": "authority", "pathmap": "path map", "audit": "audit reproducibility",
                "portability": "adapter portability"}
DECL_DIR = "template/governance/kernel/checks"
ALT_DECL_DIR = "governance/kernel/checks"

# The stand-in check. ``marker.py <marks dir> <name> <mode> [<delay seconds>]``. It first writes ``<name>.start.json``
# (pid, process group, session, start time, working folder, the environment L4 names, whether stdin is empty), then
# acts by its mode, and (if it ends on its own) writes ``<name>.end.json``.
#   ok          sleep <delay>, exit 0
#   find        print a JSON list of {"message": ...} items (from the ``MARKER_MESSAGES`` JSON in the file
#               ``<marks dir>/<name>.messages.json``), exit 1
#   findobj     the same inside {"findings": [...]}, exit 1
#   first       print a first line then a second line on stdout, exit 5
#   stderr      print a line on stderr only, exit 7
#   na          print {"not_applicable": true, "reason": "<reason from the messages file>"}, exit 2
#   sleep       sleep SLEEP_S (past any bound)
#   grandchild  start a grandchild (same group) that sleeps SLEEP_S, record its pid, then sleep SLEEP_S itself
MARKER = r'''
import json, os, subprocess, sys, time
marks, name, mode = sys.argv[1], sys.argv[2], sys.argv[3]
delay = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
SLEEP_S = %(sleep)d
def write(suffix, data):
    tmp = os.path.join(marks, "." + name + suffix + ".tmp")
    with open(tmp, "w") as handle:
        json.dump(data, handle)
    os.replace(tmp, os.path.join(marks, name + suffix))
def messages():
    with open(os.path.join(marks, name + ".messages.json")) as handle:
        return json.load(handle)
import select
try:
    readable, _, _ = select.select([sys.stdin], [], [], 0.3)
    stdin_empty = bool(readable) and sys.stdin.read(1) == ""
except Exception:
    stdin_empty = False
write(".start.json", {
    "pid": os.getpid(), "pgid": os.getpgid(0), "sid": os.getsid(0), "ppid": os.getppid(), "start": time.time(),
    "cwd": os.path.realpath(os.getcwd()), "executable": sys.executable,
    "pythonpath": os.environ.get("PYTHONPATH"), "dontwritebytecode": os.environ.get("PYTHONDONTWRITEBYTECODE"),
    "git_vars": sorted(key for key in os.environ if key.startswith("GIT_")),
    "stdin_empty": stdin_empty, "argv": sys.argv[1:],
})
if mode == "grandchild":
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(%(sleep)d)"], stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    write(".grandchild.json", {"pid": child.pid, "pgid": os.getpgid(child.pid)})
if mode in ("ok", "find", "findobj", "first", "stderr", "na"):
    time.sleep(delay)
code = 0
if mode == "find":
    print(json.dumps([{"message": text} for text in messages()])); code = 1
elif mode == "findobj":
    print(json.dumps({"findings": [{"message": text} for text in messages()]})); code = 1
elif mode == "first":
    print("boom: something broke"); print("second line must not be shown"); code = 5
elif mode == "stderr":
    print("stderr-first-line: it failed", file=sys.stderr); code = 7
elif mode == "na":
    print(json.dumps({"not_applicable": True, "reason": messages()[0]})); code = 2
elif mode in ("sleep", "grandchild"):
    time.sleep(SLEEP_S)
write(".end.json", {"end": time.time(), "code": code})
sys.exit(code)
''' % {"sleep": SLEEP_S}

# The stand-in ``gov links`` of S4: the tree's own ``src/gov/cli/main.py``, run as ``python3 -m gov.cli.main links
# --since <base>``. It records its start and end, its working folder, its environment and arguments, writes the mark the
# real command writes, and answers by the mode in ``<marks dir>/links.mode``: ``clean`` (0 new, 4 standing), ``new``
# (2 new, two finding lines, exit 1), ``sleep`` (past the bound), ``badrev`` (exit 2, the reason on stderr only),
# ``weird`` (exit 0, a first line of another form).
LINKS_MAIN = r'''
import json, os, sys, time
MARKS = %(marks)r
def main():
    started = time.time()
    since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else None
    record = {"pid": os.getpid(), "start": started, "cwd": os.path.realpath(os.getcwd()), "argv": sys.argv[1:],
              "pythonpath": os.environ.get("PYTHONPATH"), "dontwritebytecode": os.environ.get("PYTHONDONTWRITEBYTECODE"),
              "pgid": os.getpgid(0), "git_vars": sorted(key for key in os.environ if key.startswith("GIT_"))}
    with open(os.path.join(MARKS, "links.start.json"), "w") as handle:
        json.dump(record, handle)
    mode = open(os.path.join(MARKS, "links.mode")).read().strip()
    if mode == "sleep":
        time.sleep(%(sleep)d)
    os.makedirs(os.path.join(".gov-runtime", "links"), exist_ok=True)
    with open(os.path.join(".gov-runtime", "links", "mark"), "w") as handle:
        handle.write("stand-in mark")
    code = 0
    if mode == "badrev":
        print("gov links: LINKS_BAD_REV: --since %%s names no commit" %% since, file=sys.stderr); code = 2
    elif mode == "weird":
        print("something else entirely")
    elif mode == "new":
        print("gov links: 2 new since %%s, 4 standing (stand-in)" %% since)
        print("UNLINKED_ID DAEO-aaaa1111 in .tickets/x.md (role engineer)")
        print("UNMARKED_CHANGE DEC-9999 (role product-spec)")
        code = 1
    else:
        print("gov links: 0 new since %%s, 4 standing (stand-in)" %% since)
    with open(os.path.join(MARKS, "links.end.json"), "w") as handle:
        json.dump({"end": time.time(), "code": code}, handle)
    return code
if __name__ == "__main__":
    sys.exit(main())
'''

# A stand-in for one of the reference tool's built-in modules (``python3 -m gov.check.<module>``): F3. If it is ever
# run, it records that in ``<marks dir>/builtin-<module>.json``.
BUILTIN = r'''
import json, os, sys
if __name__ == "__main__":
    with open(os.path.join(%(marks)r, "builtin-" + %(module)r + ".json"), "w") as handle:
        json.dump({"pid": os.getpid(), "argv": sys.argv[1:]}, handle)
    sys.exit(0)
'''
BUILTIN_MODULES = (("gov.check", "schema"), ("gov.check", "graph"), ("gov.check", "claims"), ("gov.check", "mutation"),
                   ("gov.check", "authority"), ("gov.check", "pathmap"), ("gov.check", "audit_validator"),
                   ("gov.check", "skill_validator"), ("gov.adapters", "portability"))


def state_of(pid: int) -> str | None:
    """The process state letter from ``/proc/<pid>/stat`` (``Z`` a zombie), or None when there is no such process."""
    try:
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return None


def gone(pid: int) -> bool:
    return state_of(pid) in (None, "Z", "X")


def wait_gone(pid: int, timeout: float = 6.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if gone(pid):
            return True
        time.sleep(0.05)
    return gone(pid)


@dataclass
class Outcome:
    code: int
    out: str
    err: str
    elapsed: float
    argv: list = field(default_factory=list)

    def text(self) -> str:
        return f"command: {' '.join(self.argv)}\nexit: {self.code}\nstdout:\n{self.out}\nstderr:\n{self.err}"

    def lines(self) -> list[str]:
        """The stdout lines of a pass that ran: exit 0 first (so a missing option fails here, with its message)."""
        assert self.code == 0, f"expected exit 0\n{self.text()}"
        return self.out.splitlines()

    def family(self, name: str) -> str:
        """The one line of family ``name`` (``schema``, ..., ``portability``, ``links``)."""
        found = [line for line in self.lines() if line.startswith(name + ":")]
        assert len(found) == 1, f"expected exactly one {name!r} line, found {found}\n{self.text()}"
        return found[0]

    def last(self) -> str:
        lines = self.lines()
        assert lines, f"nothing on stdout\n{self.text()}"
        return lines[-1]


_SOURCE_CHECKED = False


def snapshot(*folders: Path) -> dict:
    """Every file under the folders: path -> (size, mtime_ns); folders themselves as ``<path>/`` -> None."""
    found = {}
    for top in folders:
        for folder, names, files in os.walk(top):
            found[str(Path(folder)) + "/"] = None
            for name in files:
                path = Path(folder) / name
                stat = path.lstat()
                found[str(path)] = (stat.st_size, stat.st_mtime_ns)
    return found


class Tree:
    """One test's world: a planted git tree, a planted HOME, a folder for the stand-ins' records, a way to run ``gov``."""

    def __init__(self, base: Path):
        self.base = base.resolve()
        self.tree = self.base / "tree"
        self.home = self.base / "home"
        self.marks = self.base / "marks"      # the stand-ins' records, outside the tree and the HOME
        self.tmp = self.base / "tmp"
        self.bin = self.base / "bin"          # a folder first on PATH for the commands that are not python3
        for folder in (self.tree, self.home, self.marks, self.tmp, self.bin):
            folder.mkdir()
        self.declared: dict[str, tuple[str, str]] = {}   # id -> (the folder it is in, its command)
        self.procs: list[subprocess.Popen] = []
        self._git("init", "-q")
        (self.tree / "checks").mkdir()
        (self.tree / "checks" / "marker.py").write_text(MARKER)
        (self.tree / "README.md").write_text("planted tree for the W2-158 acceptance tests\n")

    # ------------------------------------------------------------------ git

    def git_env(self) -> dict:
        return {"PATH": SAFE_PATH, "HOME": str(self.home), "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
                "LC_ALL": "C", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
                "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}

    def _git(self, *args: str, cwd: Path | None = None, check: bool = True) -> str:
        done = subprocess.run(["git", "-C", str(cwd or self.tree), *args], env=self.git_env(), capture_output=True,
                              text=True, timeout=60)
        if check:
            assert done.returncode == 0, f"git {' '.join(args)} failed: {done.stderr}"
        return done.stdout.strip()

    def commit(self, message: str = "planted", files: dict | None = None) -> str:
        """Write ``files`` (relative path -> text), stage everything, commit; the new HEAD's full sha."""
        for rel, text in (files or {}).items():
            path = self.tree / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        self._git("add", "-A")
        self._git("commit", "-q", "--allow-empty", "-m", message)
        return self.head()

    def head(self) -> str:
        return self._git("rev-parse", "HEAD")

    def head12(self) -> str:
        return self.head()[:12]

    # ------------------------------------------------------------------ declarations and stand-ins

    def marker_command(self, name: str, mode: str = "ok", delay: float = 0.0, python: str = "python3") -> str:
        return (f"{python} checks/marker.py {shlex.quote(str(self.marks))} {name} {mode}"
                + (f" {delay}" if delay else ""))

    def declare(self, decl_id: str, command: str, *, family: str = "x", folder: str = DECL_DIR) -> None:
        """Write ``<folder>/<id>.yaml`` with the five fields (the command a JSON string, which YAML reads)."""
        path = self.tree / folder / f"{decl_id}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"id: {json.dumps(decl_id)}\nfamily: {json.dumps(family)}\ntier: \"G1\"\n"
                        f"severity: \"hard-block\"\ncommand: {json.dumps(command)}\n")
        self.declared[decl_id] = (folder, command)

    def declare_family(self, family: str, mode: str = "ok", delay: float = 0.0, messages: list | None = None, *,
                       folder: str = DECL_DIR) -> str:
        """Declare the marker for a family (skills: all three declarations); the marker's name is the declaration id.
        Returns the name of the (first) marker."""
        ids = SKILL_IDS if family == "skills" else (IDS[family],)
        for decl_id in ids:
            self.declare(decl_id, self.marker_command(decl_id, mode, delay),
                         family="skill regression" if family == "skills" else FAMILY_FIELD[family], folder=folder)
            if messages is not None:
                self.set_messages(decl_id, messages)
        return ids[0]

    def declare_all(self, mode: str = "ok", delay: float = 0.0, *, portability: bool = False) -> None:
        """One marker per family: eight (the skills family with its one declaration ``skill-regression-a``), and the
        portability one when asked."""
        for family in FAMILIES + (("portability",) if portability else ()):
            if family == "skills":
                self.declare(SKILL_IDS[0], self.marker_command(SKILL_IDS[0], mode, delay), family="skill regression")
            else:
                self.declare_family(family, mode, delay)

    def set_messages(self, name: str, messages: list) -> None:
        (self.marks / f"{name}.messages.json").write_text(json.dumps(messages))

    def plant_links(self, mode: str = "clean") -> None:
        """The tree's own (stand-in) ``gov links``: ``src/gov/{__init__,cli/__init__,cli/main,links/__init__}.py``."""
        (self.marks / "links.mode").write_text(mode)
        source = LINKS_MAIN % {"marks": str(self.marks), "sleep": SLEEP_S}
        for rel, text in (("src/gov/__init__.py", ""), ("src/gov/cli/__init__.py", ""), ("src/gov/cli/main.py", source),
                          ("src/gov/links/__init__.py", "")):
            path = self.tree / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)

    def plant_builtins(self) -> None:
        """Stand-ins for the built-in ``python3 -m gov.check.<module>`` commands of the reference tool (F3)."""
        for package, module in BUILTIN_MODULES:
            folder = self.tree / "src"
            for part in package.split("."):
                folder = folder / part
                folder.mkdir(parents=True, exist_ok=True)
                (folder / "__init__.py").touch()
            (folder / f"{module}.py").write_text(BUILTIN % {"marks": str(self.marks), "module": module})

    def plant_tool(self, name: str) -> None:
        """A program on PATH, ``<name> <marks dir> <mark name> <mode> [<delay>]``, running the marker."""
        script = self.bin / name
        script.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} {shlex.quote(str(self.tree / 'checks' / 'marker.py'))} \"$@\"\n")
        script.chmod(0o755)

    # ------------------------------------------------------------------ the records

    def record(self, name: str, which: str = "start") -> dict | None:
        path = self.marks / f"{name}.{which}.json"
        return json.loads(path.read_text()) if path.exists() else None

    def ran(self, name: str) -> bool:
        return (self.marks / f"{name}.start.json").exists()

    def started(self) -> list[str]:
        """The names of every check (marker) that started, sorted."""
        return sorted(p.name[: -len(".start.json")] for p in self.marks.glob("*.start.json"))

    def builtins_run(self) -> list[str]:
        return sorted(p.name for p in self.marks.glob("builtin-*.json"))

    # ------------------------------------------------------------------ running gov

    def env(self, **extra) -> dict:
        env = {"PATH": f"{self.bin}:{SAFE_PATH}", "HOME": str(self.home), "TMPDIR": str(self.tmp), "LC_ALL": "C",
               "PYTHONPATH": str(SRC), "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
        # PYTHONDONTWRITEBYTECODE is left out on purpose: the pass itself sets it for its children (L4, L9)
        if os.environ.get("PYTHONUSERBASE"):
            env["PYTHONUSERBASE"] = os.environ["PYTHONUSERBASE"]
        env.update({key: value for key, value in extra.items() if value is not None})
        return env

    def _check_source(self) -> None:
        global _SOURCE_CHECKED
        if _SOURCE_CHECKED:
            return
        done = subprocess.run([sys.executable, "-c", "import gov, sys; sys.stdout.write(gov.__file__)"], env=self.env(),
                              cwd=str(self.base), capture_output=True, text=True, timeout=COMMAND_TIMEOUT_S)
        assert done.returncode == 0, f"gov cannot be imported with PYTHONPATH={SRC}: {done.stderr}"
        where = os.path.realpath(done.stdout)
        assert where.startswith(os.path.realpath(SRC) + os.sep), f"gov would import from {where}, not from {SRC}"
        _SOURCE_CHECKED = True

    def gov(self, *args: str, cwd: Path | None = None, env: dict | None = None,
            timeout: float = COMMAND_TIMEOUT_S) -> Outcome:
        """``python3 -m gov.cli.main <args>`` in a child process; the working folder is outside the tree by default."""
        self._check_source()
        argv = [sys.executable, "-m", "gov.cli.main", *args]
        # gov's own stdin is a pipe that stays open and empty for the whole run, so a check that inherited it (instead of
        # /dev/null, L4) would see no end of file
        read_end, write_end = os.pipe()
        began = time.monotonic()
        try:
            proc = subprocess.Popen(argv, cwd=str(cwd or self.base), env=env if env is not None else self.env(),
                                    stdin=read_end, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                    start_new_session=True)
        finally:
            os.close(read_end)
        self.procs.append(proc)
        try:
            out, err = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._kill_group(proc)
            out, err = proc.communicate()
            raise AssertionError(f"the command did not end within {timeout:.0f} s\nstdout:\n{out}\nstderr:\n{err}") from None
        finally:
            os.close(write_end)
        return Outcome(proc.returncode, out, err, time.monotonic() - began, argv)

    def structural(self, *args: str, root: Path | str | None = None, bound: float | None = BOUND, **kw) -> Outcome:
        """``gov check --structural <args> [--timeout <bound>] --root <the tree>``."""
        extra = ["--timeout", str(bound)] if bound is not None else []
        return self.gov("check", "--structural", *args, *extra, "--root", str(root if root is not None else self.tree),
                        **kw)

    # ------------------------------------------------------------------ teardown

    @staticmethod
    def _kill_group(proc: subprocess.Popen) -> None:
        for sig in (signal.SIGCONT, signal.SIGKILL):
            try:
                os.killpg(proc.pid, sig)
            except OSError:
                pass

    def cleanup(self) -> None:
        """Kill whatever a (red) run left: the gov processes, every recorded check, its group and its grandchild."""
        for proc in self.procs:
            self._kill_group(proc)
        for path in self.marks.glob("*.start.json"):
            self._kill_recorded(path)
        for path in self.marks.glob("*.grandchild.json"):
            self._kill_recorded(path)
        for proc in self.procs:
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass

    @staticmethod
    def _kill_recorded(path: Path) -> None:
        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError):
            return
        pgid = data.get("pgid")
        if isinstance(pgid, int) and pgid > 1 and pgid == data.get("pid"):
            try:
                os.killpg(pgid, signal.SIGKILL)
            except OSError:
                pass
        if isinstance(data.get("pid"), int) and data["pid"] > 1:
            try:
                os.kill(data["pid"], signal.SIGKILL)
            except OSError:
                pass


def family_lines(outcome: Outcome) -> dict[str, str]:
    """family name -> its line, for the ten lines that begin ``<name>:``."""
    return {name: outcome.family(name) for name in OUTPUT_ORDER}


TIME_RE = re.compile(r"\d+(\.\d+)?\s*s\b")


def assert_shape(outcome, tree: Tree, *, notices: tuple[str, ...] = ()) -> list[str]:
    """L2: exit 0, exactly eleven lines (the eight families, portability, links, the last line) in order; the last
    starts ``structural pass at <head12>``. Returns the lines."""
    lines = outcome.lines()
    assert len(lines) == len(OUTPUT_ORDER) + 1, f"expected {len(OUTPUT_ORDER) + 1} lines on stdout\n{outcome.text()}"
    for line, name in zip(lines, OUTPUT_ORDER):
        assert line.startswith(f"{name}: "), f"line for {name} is {line!r}, in this order {OUTPUT_ORDER}\n{outcome.text()}"
    assert lines[-1].startswith(f"structural pass at {tree.head12()}"), f"last line: {lines[-1]!r}\n{outcome.text()}"
    assert not re.match(rf"structural pass at {tree.head12()}[0-9a-f]", lines[-1]), "more than 12 characters of the sha"
    assert TIME_RE.search(lines[-1]), f"the last line gives no time taken: {lines[-1]!r}"
    if notices:
        assert "not a refusal" in lines[-1], f"last line does not say a notice is not a refusal: {lines[-1]!r}"
        for name in notices:
            assert name in lines[-1], f"last line does not name the family {name}: {lines[-1]!r}"
    else:
        assert "NOTICE" not in lines[-1] and "not a refusal" not in lines[-1], lines[-1]
        assert " ok" in lines[-1], f"last line does not say the ran families are ok: {lines[-1]!r}"
    return lines
