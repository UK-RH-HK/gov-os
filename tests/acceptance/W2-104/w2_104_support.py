"""Support code for the W2-104 acceptance tests: the skill evaluation harness, ``gov skilleval``.

The tests use the harness only through the public contract the lead set (README, "The contract"):
the ``gov skilleval`` command, its arguments, its envelope and exit codes, the record file it writes
beside the skill, ``governance/project/skill-imports.yaml``, and the ``claude`` executable it runs.

- **The code under test** is the ``gov`` package of the repository this file sits in:
  ``<repository>/src``, found from this file's own location (``REPO_ROOT``), on ``PYTHONPATH``, run as
  ``python3 -m gov.cli.main``. Nothing installed is used, and no fixed path.
- **The project** is a temporary one built from scratch under pytest's ``tmp_path``, with planted skills.
- **The model** is a stub: a small Python script named ``claude`` in a folder of the test's, first on a
  ``PATH`` that holds only it and the system folders (``/usr/bin``, ``/bin``). It decides its reply from
  marker words planted in a scenario's Situation (the session) and Pass line (the judgement), and it logs
  each call (arguments, working folder, standard input, what the session's folder holds) to a log folder
  of the test's. No test reaches the network or starts the real ``claude``.
- **The environment is built from scratch:** ``PATH``, an empty temporary ``HOME``, ``TMPDIR``, locale,
  ``PYTHONPATH`` and ``PYTHONPYCACHEPREFIX``, plus a planted fake value where a test asks for one. Nothing
  of the session that runs the tests is passed on.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"

COMMAND = "skilleval"
SYSTEM_PATH = ("/usr/bin", "/bin")
COMMAND_TIMEOUT_S = 240.0   # a wait under parallel load, not a time the ticket promises

DEFAULT_MODEL = "claude-opus-5-5"   # DEC-839's worker defaults, as the contract states them
DEFAULT_EFFORT = "high"

RECORD_FILE = "scenario-records.yaml"
IMPORTS_REL = "governance/project/skill-imports.yaml"

VERDICTS = ("pass", "fail", "not-run")
RECORD_FIELDS = ("skill", "skill_version", "scenario", "title", "verdict", "cause", "cost_usd", "seconds",
                 "model", "effort", "run_at")
SCENARIO_FIELDS = ("scenario", "title", "verdict", "cause", "cost_usd", "seconds")
RESULT_FIELDS = ("skill", "skill_version", "scenarios", "record", "adopted")

# Exit codes of the contract.
EXIT_ALL_PASSED = 0
EXIT_ANY_FAILED = 3
EXIT_ANY_NOT_RUN = 4
EXIT_NOT_EVALUABLE = 5
EXIT_ADOPTED = 0
EXIT_ADOPTION_REFUSED = 6

# --------------------------------------------------------------------------
# Marker words the stub acts on
# --------------------------------------------------------------------------

# In a scenario's Situation: what the session's process does. Without one it answers.
SESSION_EXIT_NONZERO = "SESSIONW2104_EXITNONZERO"
SESSION_BAD_JSON = "SESSIONW2104_BADJSON"
SESSION_IS_ERROR = "SESSIONW2104_ISERROR"
SESSION_SLEEP = "SESSIONW2104_SLEEP"
SESSION_SAYS_PASS = "SESSIONW2104_SAYSPASS"            # its own reply ends with a verdict line
SESSION_LEAK_STDERR = "SESSIONW2104_LEAKSTDERR"        # the planted values on its stderr, exit 1
SESSION_LEAK_STDOUT = "SESSIONW2104_LEAKSTDOUT"        # the planted values as non-JSON stdout
SESSION_LEAK_ERROR = "SESSIONW2104_LEAKERROR"          # the planted values in an is_error reply

# In a scenario's Pass line: what the judgement's process does. Without one it answers PASS.
JUDGE_FAIL = "JUDGEW2104_FAIL"
JUDGE_NO_VERDICT = "JUDGEW2104_NOVERDICT"
JUDGE_LAST_FAIL = "JUDGEW2104_PASSTHENFAIL"            # PASS on one line, FAIL on the last
JUDGE_LAST_PASS = "JUDGEW2104_FAILTHENPASS"            # FAIL on one line, PASS on the last
JUDGE_EXIT_NONZERO = "JUDGEW2104_EXITNONZERO"

REPLY_TOKEN = "".join(("STUB", "REPLY", "W2104"))   # in every session reply; a prompt that holds it is a judgement's
TAG_RE = r"TAGW2104s[0-9]+"
SESSION_SLEEP_S = 30
SESSION_COST = 0.25
JUDGE_COST = 0.05


def planted_values():
    """Two obviously fake values, made at run time: one for the environment, one for a secrets-like file."""
    return ("-".join(("w2104", "planted", "env", "value", "not", "real", "qx7k")),
            "-".join(("w2104", "planted", "file", "value", "not", "real", "zp4m")))


_STUB = r'''#!@PYTHON@ -I
"""A stand-in for the claude program (W2-104's acceptance tests). It never reaches a network."""
import json, os, re, sys, time

LOG = @LOG@
REPLY_TOKEN = @REPLY_TOKEN@
LEAKS = @LEAKS@
M = @MARKERS@

prompt = sys.stdin.read()
cwd = os.getcwd()
judge = REPLY_TOKEN in prompt
entry = {"t": time.time(), "pid": os.getpid(), "argv": sys.argv[1:], "cwd": cwd, "stdin": prompt,
         "role": "judge" if judge else "session"}
if not judge:
    skills = os.path.join(cwd, ".claude", "skills")
    listing, contents = {}, {}
    if os.path.isdir(skills):
        for name in sorted(os.listdir(skills)):
            path = os.path.join(skills, name)
            listing[name] = sorted(os.listdir(path)) if os.path.isdir(path) else None
            md = os.path.join(path, "SKILL.md")
            if os.path.isfile(md):
                with open(md, encoding="utf-8") as handle:
                    contents[name] = handle.read()
    entry["skills"] = listing
    entry["skill_md"] = contents
    entry["scenarios_md"] = sorted(os.path.join(folder, name) for folder, _, names in os.walk(cwd)
                                   for name in names if name == "scenarios.md")
os.makedirs(LOG, exist_ok=True)
with open(os.path.join(LOG, "%.6f-%d.json" % (entry["t"], entry["pid"])), "w", encoding="utf-8") as handle:
    json.dump(entry, handle)


def answer(text, cost, is_error=False):
    print(json.dumps({"type": "result", "result": text, "is_error": is_error, "total_cost_usd": cost}))
    sys.exit(0)


if judge:
    if M["JUDGE_EXIT_NONZERO"] in prompt:
        sys.stderr.write("stub judgement: failing on purpose\n")
        sys.exit(9)
    if M["JUDGE_LAST_FAIL"] in prompt:
        answer("VERDICT: PASS\nOn a second reading the pass line does not hold.\nVERDICT: FAIL", @JUDGE_COST@)
    if M["JUDGE_LAST_PASS"] in prompt:
        answer("VERDICT: FAIL\nOn a second reading the pass line holds.\nVERDICT: PASS", @JUDGE_COST@)
    if M["JUDGE_NO_VERDICT"] in prompt:
        answer("I cannot tell whether the pass line holds.", @JUDGE_COST@)
    if M["JUDGE_FAIL"] in prompt:
        answer("The pass line does not hold.\nVERDICT: FAIL", @JUDGE_COST@)
    answer("The pass line holds.\nVERDICT: PASS", @JUDGE_COST@)

if M["SESSION_EXIT_NONZERO"] in prompt:
    sys.stderr.write("stub session: failing on purpose\n")
    sys.exit(7)
if M["SESSION_BAD_JSON"] in prompt:
    print("this is not the JSON object the harness asks for")
    sys.exit(0)
if M["SESSION_IS_ERROR"] in prompt:
    answer("the stub reports an error", 0.0, is_error=True)
if M["SESSION_LEAK_STDERR"] in prompt:
    sys.stderr.write("stub session: credentials " + " ".join(LEAKS) + "\n")
    sys.exit(1)
if M["SESSION_LEAK_STDOUT"] in prompt:
    print("not json: " + " ".join(LEAKS))
    sys.exit(0)
if M["SESSION_LEAK_ERROR"] in prompt:
    answer("error with " + " ".join(LEAKS), 0.0, is_error=True)
if M["SESSION_SLEEP"] in prompt:
    time.sleep(@SLEEP@)
found = re.search(@TAG_RE@, prompt)
reply = REPLY_TOKEN + " " + (found.group(0) if found else "notag") + " done as the skill says."
if M["SESSION_SAYS_PASS"] in prompt:
    reply += "\nVERDICT: PASS"
answer(reply, @SESSION_COST@)
'''


@dataclass(frozen=True)
class Stub:
    folder: Path   # the folder put first on PATH
    path: Path     # the executable ``claude``
    log: Path      # one JSON file per call

    def calls(self):
        """Every call made so far, oldest first."""
        if not self.log.is_dir():
            return []
        entries = [json.loads(path.read_text(encoding="utf-8")) for path in self.log.glob("*.json")]
        return sorted(entries, key=lambda entry: (entry["t"], entry["pid"]))

    def sessions(self):
        return [entry for entry in self.calls() if entry["role"] == "session"]

    def judgements(self):
        return [entry for entry in self.calls() if entry["role"] == "judge"]


def install_stub(base):
    """Write the stub ``claude`` into ``<base>/bin`` and return it."""
    base = Path(base)
    folder = base / "bin"
    folder.mkdir(parents=True, exist_ok=True)
    markers = {name: value for name, value in globals().items()
               if name.startswith(("SESSION_", "JUDGE_")) and isinstance(value, str)}
    text = (_STUB.replace("@PYTHON@", sys.executable)
            .replace("@LOG@", repr(str(base / "log")))
            .replace("@REPLY_TOKEN@", repr(REPLY_TOKEN))
            .replace("@LEAKS@", repr(list(planted_values())))
            .replace("@MARKERS@", repr(markers))
            .replace("@TAG_RE@", repr(TAG_RE))
            .replace("@SLEEP@", str(SESSION_SLEEP_S))
            .replace("@SESSION_COST@", repr(SESSION_COST))
            .replace("@JUDGE_COST@", repr(JUDGE_COST)))
    path = folder / "claude"
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return Stub(folder=folder, path=path, log=base / "log")


def assert_no_real_claude_on_system_path():
    """No test may start the real program: the system folders on the test's PATH hold no ``claude``."""
    found = shutil.which("claude", path=os.pathsep.join(SYSTEM_PATH))
    assert found is None, f"a claude program is in the system folders ({found}); the tests would reach it"


# --------------------------------------------------------------------------
# The temporary project and its planted skills
# --------------------------------------------------------------------------

def git(project, *args):
    env = {"PATH": os.pathsep.join(SYSTEM_PATH), "HOME": str(project), "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "W2-104 tests", "GIT_AUTHOR_EMAIL": "w2-104@example.invalid",
           "GIT_COMMITTER_NAME": "W2-104 tests", "GIT_COMMITTER_EMAIL": "w2-104@example.invalid"}
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done.stdout


def make_project(path):
    """A small committed project: a gitignore and a readme, nothing of this repository."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    (path / ".gitignore").write_text(".gov-runtime/\n__pycache__/\n.env\n", encoding="utf-8")
    (path / "README.md").write_text("A temporary project for W2-104's acceptance tests.\n", encoding="utf-8")
    git(path, "init", "-q", "-b", "main")
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "temporary project")
    return path


@dataclass(frozen=True)
class Scenario:
    title: str
    situation: str
    expected: str
    pass_line: str


def scenario(n, session="", judge=""):
    """Scenario ``n``: its Situation carries the tag and the session marker, its Pass line the judge marker."""
    return Scenario(
        title=f"Planted case {n}",
        situation=f"TAGW2104s{n} a planted request arrives. The session is asked to carry out planted task {n}. "
                  f"{session}".strip(),
        expected=f"The session carries out planted task {n} as the skill says. EXPECTW2104e{n}",
        pass_line=f"The reply shows planted task {n} carried out. PASSLINEW2104p{n} {judge}".strip(),
    )


def skill_md(name, version="1.4.0"):
    lines = ["---", f"name: {name}"]
    if version is not None:
        lines.append(f'version: "{version}"')
    lines += ['description: "Plants a skill for the acceptance tests of the skill evaluation harness."',
              "metadata:"]
    if version is not None:
        lines.append(f'  version: "{version}"')
    lines += ["  planted: true", "---", "", f"# {name}", "",
              "A planted skill. It states a method and grants nothing.", "",
              "## Steps", "", "- Carry out the planted task named in the situation.", ""]
    return "\n".join(lines)


def scenarios_md(name, scenarios, wrap_situation=False, drop_pass_line=None):
    """The scenarios in the form of W2-11's ``scenarios.md`` files: ``## <n>. <title>`` and three bullets.

    ``wrap_situation`` puts the second half of each Situation on a continuation line, as W2-11's files wrap.
    ``drop_pass_line`` names a scenario (1-based) written without its Pass line.
    """
    lines = [f"# {name}: the three scenarios", "",
             "Written before the skill's text. Each is run on a fresh session with only this skill loaded.", ""]
    for n, item in enumerate(scenarios, start=1):
        situation = item.situation
        if wrap_situation and ". " in situation:
            head, _, tail = situation.partition(". ")
            situation = f"{head}.\n  {tail}"
        lines += [f"## {n}. {item.title}", "", f"- **Situation:** {situation}", f"- **Expected:** {item.expected}"]
        if drop_pass_line != n:
            lines.append(f"- **Pass line:** {item.pass_line}")
        lines.append("")
    return "\n".join(lines)


def plant_skill(project, rel, name, scenarios, version="1.4.0", wrap_situation=False):
    """A skill folder ``rel`` in the project with ``SKILL.md`` and ``scenarios.md``. Returns its path."""
    folder = Path(project) / rel
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "SKILL.md").write_text(skill_md(name, version), encoding="utf-8")
    (folder / "scenarios.md").write_text(scenarios_md(name, scenarios, wrap_situation=wrap_situation),
                                         encoding="utf-8")
    return folder


def three(session=("", "", ""), judge=("", "", "")):
    return [scenario(n, session[n - 1], judge[n - 1]) for n in (1, 2, 3)]


# --------------------------------------------------------------------------
# YAML files: the record beside the skill, and the import record
# --------------------------------------------------------------------------

class _PlainLoader(yaml.SafeLoader):
    """A safe loader that keeps timestamps as the strings written, so ``run_at`` is read as written."""


_PlainLoader.yaml_implicit_resolvers = {
    key: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml(path):
    return yaml.load(Path(path).read_text(encoding="utf-8"), Loader=_PlainLoader)


def records(skill_folder):
    """The ``records`` list of the skill's record file."""
    path = Path(skill_folder) / RECORD_FILE
    assert path.is_file(), f"no {RECORD_FILE} beside the skill in {skill_folder}"
    data = load_yaml(path)
    assert isinstance(data, dict) and isinstance(data.get("records"), list), \
        f"{path} is not a YAML map with a list under 'records': {data!r}"
    return data["records"]


def write_imports(project, entries):
    path = Path(project) / IMPORTS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"imports": entries}, sort_keys=False), encoding="utf-8")
    return path


def read_imports(project):
    data = load_yaml(Path(project) / IMPORTS_REL)
    assert isinstance(data, dict) and isinstance(data.get("imports"), list), \
        f"{IMPORTS_REL} is not a YAML map with a list under 'imports': {data!r}"
    return data["imports"]


def import_entry(name, **changes):
    entry = {"name": name, "source": "https://example.invalid/skills-collection", "version": "2.3.1",
             "licence": "Apache-2.0", "licence_verdict": "allowed", "adopted": False}
    entry.update(changes)
    return {key: value for key, value in entry.items() if value is not _DROP}


_DROP = object()
DROP = _DROP   # ``import_entry(name, licence_verdict=DROP)`` leaves the key out


# --------------------------------------------------------------------------
# Running gov
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    home: Path
    tmpdir: Path
    pycache: Path
    elsewhere: Path


def make_sandbox(base):
    base = Path(base)
    names = ("home", "tmp", "pycache", "elsewhere")
    for name in names:
        (base / name).mkdir(parents=True, exist_ok=True)
    return Sandbox(*(base / name for name in names))


@dataclass(frozen=True)
class Run:
    args: tuple
    returncode: int
    stdout: str
    stderr: str
    started: float   # UTC epoch seconds
    ended: float

    def describe(self):
        return (f"gov {' '.join(self.args)}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-4000:]}\n"
                f"stderr:\n{self.stderr[-4000:]}")

    def envelope(self):
        try:
            data = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"gov skilleval gave no API-0002 envelope on stdout\n{self.describe()}") from None
        assert isinstance(data, dict), f"stdout is not a JSON object\n{self.describe()}"
        return data

    def result(self):
        """The envelope's ``result``, with the fields the contract names."""
        envelope = self.envelope()
        assert envelope.get("command") == COMMAND, f"the envelope does not name {COMMAND}\n{self.describe()}"
        result = envelope.get("result")
        assert isinstance(result, dict), f"the envelope has no result map\n{self.describe()}"
        missing = [field for field in RESULT_FIELDS if field not in result]
        assert not missing, f"the result lacks {missing}\n{self.describe()}"
        return result

    def verdicts(self):
        """``{scenario number: verdict}`` from the envelope."""
        scenarios = self.result()["scenarios"]
        assert isinstance(scenarios, list) and len(scenarios) == 3, \
            f"the result does not list three scenarios\n{self.describe()}"
        found = {item.get("scenario"): item.get("verdict") for item in scenarios}
        assert sorted(found) == [1, 2, 3], f"the scenarios are not numbered 1 to 3: {found}\n{self.describe()}"
        return found

    def scenario(self, n):
        return next(item for item in self.result()["scenarios"] if item.get("scenario") == n)


def gov_env(sandbox, stub=None, extra_env=None):
    path = ([str(stub.folder)] if stub is not None else []) + list(SYSTEM_PATH)
    env = {
        "PATH": os.pathsep.join(path),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(SRC),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
    }
    env.update(extra_env or {})
    return env


def run_gov(project, sandbox, *args, stub=None, extra_env=None, cwd=None, root=True):
    """``python3 -m gov.cli.main <args> [--root <project>]`` with this repository's ``src/``."""
    assert_no_real_claude_on_system_path()
    full = list(args) + (["--root", str(project)] if root else [])
    started = time.time()
    try:
        done = subprocess.run([sys.executable, "-m", "gov.cli.main", *full], cwd=str(cwd or project),
                              env=gov_env(sandbox, stub, extra_env), capture_output=True, text=True,
                              timeout=COMMAND_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired as exc:
        raise AssertionError(f"gov {' '.join(full)} did not end within {COMMAND_TIMEOUT_S:.0f} s\n"
                             f"stdout: {exc.stdout!r}\nstderr: {exc.stderr!r}") from None
    return Run(tuple(full), done.returncode, done.stdout, done.stderr, started, time.time())


def skilleval(project, sandbox, skill, *options, stub=None, extra_env=None, cwd=None, json_mode=True):
    args = [COMMAND, str(skill), *options] + (["--json"] if json_mode else [])
    return run_gov(project, sandbox, *args, stub=stub, extra_env=extra_env, cwd=cwd)


# --------------------------------------------------------------------------
# Checks shared by the cases
# --------------------------------------------------------------------------

def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def squash(text):
    return re.sub(r"\s+", " ", text or "").strip()


def parse_utc(value):
    """``run_at`` as written: an ISO 8601 UTC time. Returns epoch seconds."""
    assert isinstance(value, str), f"run_at is not written as an ISO 8601 string: {value!r}"
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    moment = datetime.datetime.fromisoformat(text)
    assert moment.tzinfo is not None and moment.utcoffset() == datetime.timedelta(0), \
        f"run_at is not UTC: {value!r}"
    return moment.timestamp()


def assert_entry_shape(entry, run, skill_name, version, model=DEFAULT_MODEL, effort=DEFAULT_EFFORT):
    """A record entry has the contract's fields with the contract's types; returns it."""
    missing = [field for field in RECORD_FIELDS if field not in entry]
    assert not missing, f"a record entry lacks {missing}: {entry}"
    assert entry["skill"] == skill_name, entry
    assert str(entry["skill_version"]) == version, entry
    assert entry["scenario"] in (1, 2, 3), entry
    assert entry["title"] == f"Planted case {entry['scenario']}", entry
    assert entry["verdict"] in VERDICTS, entry
    assert entry["model"] == model and entry["effort"] == effort, entry
    assert is_number(entry["seconds"]) and entry["seconds"] >= 0, entry
    at = parse_utc(entry["run_at"])
    assert run.started - 2 <= at <= run.ended + 2, f"run_at is not the time of this run: {entry}"
    assert_verdict_fields(entry)
    return entry


def assert_verdict_fields(item):
    """``cause`` and ``cost_usd`` agree with the verdict (record entry or envelope scenario)."""
    verdict = item["verdict"]
    if verdict == "pass":
        assert item["cause"] is None, f"a pass carries a cause: {item}"
        assert is_number(item["cost_usd"]), f"a pass has no cost: {item}"
    elif verdict == "fail":
        assert isinstance(item["cause"], str), f"a fail carries no cause string: {item}"
        assert is_number(item["cost_usd"]), f"a fail has no cost: {item}"
    else:
        cause = item["cause"]
        assert isinstance(cause, str) and cause.strip() and "\n" not in cause.strip(), \
            f"a not-run scenario has no one-line cause: {item}"
        assert item["cost_usd"] is None, f"a not-run scenario carries a cost: {item}"


def last_entries(skill_folder, count=3):
    """The last ``count`` record entries, by scenario number."""
    entries = records(skill_folder)[-count:]
    by_number = {entry.get("scenario"): entry for entry in entries}
    assert sorted(by_number) == [1, 2, 3][:count], f"the last {count} entries are not one per scenario: {entries}"
    return by_number


def resolve_record(run, project):
    record = Path(run.result()["record"])
    return (record if record.is_absolute() else Path(project) / record).resolve()


def every_file_text(root, skip=()):
    """``{relative path: text}`` of every regular file under ``root`` (``.git`` left out)."""
    found = {}
    for folder, dirs, names in os.walk(root):
        dirs[:] = [name for name in dirs if name != ".git"]
        for name in names:
            path = Path(folder) / name
            rel = str(path.relative_to(root))
            if rel in skip or path.is_symlink() or not path.is_file():
                continue
            try:
                found[rel] = path.read_bytes().decode("utf-8", errors="replace")
            except PermissionError:
                continue
    return found
