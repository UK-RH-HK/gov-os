"""Support code for the W2-153 acceptance tests (standard library and PyYAML only).

W2-153 delivers the role template at launch (W2-128 TPL-4): ``gov launch`` and the dispatcher's lead line pass
``--append-system-prompt-file <root>/.claude/templates/<stem>.md`` and refuse without the file; the rulesync role
sources are composed (S3 amended, DEC-1112 (3): the rulesync front matter with ``claudecode.skills``, the kernel role
template's body, one blank line, the kernel role file's body; ``gov.adapters.portability.compose(root, role)``); the
``.claude/templates/`` copies are checked byte for byte and written by ``python3 -m gov.adapters.portability
--write-templates <dir>``.

How the code under test is chosen (DEC-732): every command runs with ``PYTHONPATH`` set to the ``src/`` folder of the
working tree this file is in. The baseline for the failure line F2 is integrate's code at ``BASELINE_COMMIT``, read
from git (``git archive`` / ``git cat-file``) into a temporary folder after checking its blob ids.

What is never touched: no real Claude session starts. ``gov launch`` runs with ``HOME`` set to a temporary folder whose
``.local/bin/claude`` is a stand-in that records its arguments and ends; the machine-wide folder, the gate's readings
and the registry all live in that home. The dispatcher's script runs as a copy whose absolute paths are rewritten into
a temporary folder (its CLI, the orchestrator folder and the worktrees folder), so it can reach no real path.
"""

from __future__ import annotations

import datetime
import io
import json
import os
import re
import subprocess
import sys
import tarfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SRC = REPO / "src"
HARNESS = HERE / "w2_153_launch_harness.py"

COMMAND_TIMEOUT_S = 120.0  # a wait under parallel load, not a time the ticket promises
SAFE_PATH = "/usr/local/bin:/usr/bin:/bin"
GIB = 1024 ** 3

FLAG = "--append-system-prompt-file"
REFUSAL = "LAUNCH_NO_TEMPLATE"

# The ticket's Interface (D5 row 9): the role -> template map, one constant in launcher.py.
ROLE_TEMPLATE = {
    "engineer": "role-engineer",
    "independent-test-designer": "role-test-designer",
    "independent-auditor": "role-reviewer",
    "product-spec": "role-product-spec",
    "research": "role-research",
    "lead": "role-lead",
    "orchestrator": "role-lead",
}
WORKER_ROLES = ("engineer", "independent-test-designer", "independent-auditor", "product-spec", "research")
LEAD_ROLES = ("lead", "orchestrator")
ALL_ROLES = WORKER_ROLES + LEAD_ROLES

# The ticket's Interface: the skills list of each rulesync role source (kernel role file name -> skills).
SKILLS = {
    "engineer": ["test-driven-development"],
    "independent-test-designer": ["test-design"],
    "independent-auditor": ["audit"],
    "product-spec": ["change"],
    "research": ["discovery"],
    "orchestrator": ["orchestration"],
}
# The kernel role file -> its template, for the six kernel roles (the orchestrator's is the lead's).
KERNEL_ROLE_TEMPLATE = {role: ROLE_TEMPLATE[role] for role in SKILLS}

# S4: the eight copies under .claude/templates/ (ticket.md and the rest of the kernel's templates are not copied).
TEMPLATE_STEMS = ("brief", "role-research", "role-product-spec", "role-test-designer", "role-engineer",
                  "role-reviewer", "role-lead", "role-cto")

KERNEL = REPO / "template" / "governance" / "kernel"
KERNEL_TEMPLATES = KERNEL / "templates"
TEST_DESIGN_SKILL = KERNEL / "skills" / "test-design" / "SKILL.md"
DISPATCH_REL = "governance/project/orchestration/tools/dispatch/launch_now.sh"

# F2's baseline (DEC-1112 (3)): the integrate commit W2-153 is built on, `git merge-base w2/W2-153 w2/integrate`
# (2026-11-10). Its launcher is integrate's as of the W2-56 merge (cf23e9f8dc1f: S5's cleaned env, the runs-folder and
# reranker sandbox entries). Moved from 1ef1a7a48c53 (launcher 5ecd20c0d252), which predates W2-56.
BASELINE_COMMIT = "f73e72d4a43b14ba598bac4829ced555842907ea"
BASELINE_BLOBS = {
    "src/gov/launch/launcher.py": "91033723374d9dff0d97e4a36934cc09fa00d16b",
    DISPATCH_REL: "bd8f45b9d3dd9d5071e1be7b0e74b7627e76ba0b",
}


# --- git ---------------------------------------------------------------------------------------------------------------

def git(*args: str, text: bool = True):
    done = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=text,
                          timeout=COMMAND_TIMEOUT_S, env={**os.environ, "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1"})
    if done.returncode != 0:
        err = done.stderr if text else done.stderr.decode(errors="replace")
        raise AssertionError(f"git {' '.join(args)} failed (exit {done.returncode}): {err.strip()}\n"
                             f"The baseline commit {BASELINE_COMMIT[:12]} must be in this repository's history.")
    return done.stdout


def check_baseline_blobs() -> None:
    for rel, blob in BASELINE_BLOBS.items():
        found = git("rev-parse", f"{BASELINE_COMMIT}:{rel}").strip()
        assert found == blob, f"{rel} at {BASELINE_COMMIT[:12]} is blob {found}, not {blob}"


def extract_baseline_src(target: Path) -> Path:
    """integrate's ``src/gov`` at the baseline commit, unpacked under ``target``; returns its ``src`` folder."""
    check_baseline_blobs()
    data = git("archive", "--format=tar", BASELINE_COMMIT, "src/gov", text=False)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        if hasattr(tarfile, "data_filter"):
            archive.extractall(target, filter="data")
        else:
            archive.extractall(target)
    return target / "src"


def baseline_dispatch_script() -> str:
    check_baseline_blobs()
    return git("cat-file", "blob", BASELINE_BLOBS[DISPATCH_REL])


# --- small helpers -----------------------------------------------------------------------------------------------------

def write(path: Path, text: str | bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8")
    return path


def split_front(text: str):
    """``(front matter, body)`` of a Markdown text as ``gov.adapters.portability._split`` reads it on integrate: the
    blank lines between the front matter and the body are dropped; no front matter gives ``(None, text)``."""
    end = text.find("\n---", 3) if text.startswith("---") else -1
    if end < 0:
        return None, text.lstrip("\n")
    return yaml.safe_load(text[3:end]), text[end + 4:].partition("\n")[2].lstrip("\n")


def record_pointer(stub: Path) -> Path:
    """The file beside a stand-in ``claude`` that names where it records (``<stub>.record``)."""
    return stub.with_name(stub.name + ".record")


def point_record(stub: Path, record: Path) -> None:
    """From now on the stand-in at ``stub`` appends its calls to ``record``."""
    write(record_pointer(stub), str(record))


def stub_cli(path: Path) -> Path:
    """A stand-in ``claude``: appends one JSON line (its arguments, its working folder, its TMPDIR) to the file
    named in ``<its own path>.record`` (``point_record``), and ends with 0. It reads nothing else and starts nothing.

    The record's path sits in a file beside the stand-in, not in the environment: the launcher passes the session a
    cleaned environment (W2-56 S5, ``gov.launch.environ``: ``PATH``, ``HOME``, the locale and the identity, beside
    its own values), so a variable of the test's would never reach it."""
    write(path, (
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        f"with open({str(record_pointer(path))!r}, encoding='utf-8') as pointer:\n"
        "    record = pointer.read().strip()\n"
        "with open(record, 'a', encoding='utf-8') as f:\n"
        "    f.write(json.dumps({'argv': sys.argv[1:], 'cwd': os.getcwd(),\n"
        "                        'tmpdir': os.environ.get('TMPDIR')}) + '\\n')\n"
    ))
    path.chmod(0o755)
    return path


def read_calls(record: Path) -> list[dict]:
    if not record.exists():
        return []
    return [json.loads(line) for line in record.read_text(encoding="utf-8").splitlines() if line.strip()]


def without_flag(argv: list[str]) -> list[str]:
    """``argv`` with each ``--append-system-prompt-file <value>`` pair (or ``--flag=value``) taken out."""
    out, skip = [], False
    for arg in argv:
        if skip:
            skip = False
            continue
        if arg == FLAG:
            skip = True
            continue
        if arg.startswith(FLAG + "="):
            continue
        out.append(arg)
    return out


def shown(argv: list[str]) -> list[str]:
    """``argv`` for a failure message: the ``--settings`` value cut to its first characters."""
    return [arg if len(arg) < 120 else arg[:60] + f"...<{len(arg)} characters>" for arg in argv]


def flag_values(argv: list[str]) -> list[str]:
    values = [argv[i + 1] for i, arg in enumerate(argv[:-1]) if arg == FLAG]
    values += [arg.split("=", 1)[1] for arg in argv if arg.startswith(FLAG + "=")]
    return values


def template_text(stem: str) -> str:
    return f"---\nname: {stem}\nversion: 1.0.0\n---\n# W2-153 fixture template {stem}\n"


def composed_body(template_body: str, role_body: str) -> str:
    """S3 amended (DEC-1112 (3), 2026-11-10): the composed source's body is the role template's body, then one
    blank line, then the kernel role file's body. Each body is read by ``split_front`` (portability's ``_split``
    rule: front matter, if any, stripped, and the blank lines after it dropped). The templates end with one newline,
    so the blank line is one more newline; a template body that does not end so fails here, not in the case."""
    assert template_body.endswith("\n") and not template_body.endswith("\n\n"), (
        "the fixture's premise: a role template body ends with exactly one newline")
    return template_body + "\n" + role_body


# --- W1-33's labelled fields (MR-5, DEC-066), reproduced from tests/acceptance/W1-33/w1_33_support.py ---------------

_LABELLED = re.compile(r"^[-*]\s+\*\*(?P<label>[^*]+?):?\*\*:?\s*(?P<rest>.*)$")


def _w1_33_body(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0:
            rest = text[end + 4:]
            return rest.split("\n", 1)[1] if "\n" in rest else ""
    return text


def fields(text: str) -> dict:
    """``{label in lower case: text}`` for every labelled list item of a Markdown text (front matter left out),
    as W1-33's ``fields()`` reads a role file or an agent definition: a field is a list item that starts with a bold
    label, up to the next labelled item, a heading, or a blank line followed by text that is not indented; its text
    is whitespace-collapsed."""
    lines = _w1_33_body(text).splitlines()
    spans, start, label = [], None, None

    def close(end):
        if start is not None:
            first = _LABELLED.match(lines[start]).group("rest")
            spans.append((label, " ".join("\n".join([first, *lines[start + 1:end]]).split())))

    for index, line in enumerate(lines):
        match = _LABELLED.match(line)
        ends = False
        if match or line.startswith("#"):
            ends = True
        elif start is not None and line.strip() and not line[0].isspace():
            ends = index > 0 and not lines[index - 1].strip()
        if ends:
            end = index
            while end > 0 and start is not None and end - 1 > start and not lines[end - 1].strip():
                end -= 1
            close(end)
            start, label = (index, match.group("label").strip()) if match else (None, None)
    end = len(lines)
    while start is not None and end - 1 > start and not lines[end - 1].strip():
        end -= 1
    close(end)
    return {name.lower(): value for name, value in spans}


# --- the launch bed (S1, F1, F2) ---------------------------------------------------------------------------------------

TICKETS = {
    # id: (role written in the ticket, external-ref, allowed_paths)
    "W153-ENG": ("engineer", "W2-9531", ["src/w2_153_probe.py"]),
    "W153-PS": ("product-spec", "W2-9532", ["docs/w2-153-probe.md"]),
    "W153-RES": ("research", "W2-9533", ["experiments/w2-153-probe/**"]),
    "W153-LEAD": ("orchestrator", "W2-9534", ["src/w2_153_lead.py"]),
}
TICKET_OF = {"engineer": "W153-ENG", "independent-test-designer": "W153-ENG", "independent-auditor": "W153-ENG",
             "product-spec": "W153-PS", "research": "W153-RES", "lead": "W153-LEAD", "orchestrator": "W153-LEAD"}

GUARD_SETTINGS = {"hooks": {"PreToolUse": [{"matcher": "Write|Edit|Bash", "hooks": [
    {"type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/pretooluse.py"}]}]}}


class LaunchBed:
    """One test's launch: a temporary home with the stand-in CLI and an open gate, and a fixture repository with
    the tickets, the guard's settings and the eight ``.claude/templates/`` copies."""

    def __init__(self, base: Path):
        self.base = Path(os.path.realpath(base))
        self.home = self.base / "home"
        self.tmp = self.base / "tmp"
        self.tmp.mkdir(parents=True)
        self.readings = self.base / "readings"
        self.readings.mkdir()
        self.root = self.base / "repo"
        self.cli = stub_cli(self.home / ".local" / "bin" / "claude")
        self._runs = 0
        self._plant_gate()
        self._plant_repo()

    def _plant_gate(self) -> None:
        """An open resource gate (W2-20's README, "The configuration file"), as W2-136's launcher cases plant it."""
        today = datetime.date.today().isoformat()

        def dated(value):
            return {"value": value, "date": today, "source": "planted for the W2-153 launcher cases (W2-20 README)"}

        cpu = str(max(os.sched_getaffinity(0)))
        values = {
            "memory_floor_bytes": dated(3 * GIB), "verification_peak_bytes": dated(4 * GIB),
            "working_size_bytes": dated(1 * GIB), "rebuild_peak_bytes": dated(2 * GIB),
            "disk_floor_bytes": dated(100 * GIB), "inode_floor": dated(10_000_000),
            "verification_lock": dated(str(self.readings / "verification.lock")), "gpu_margin": dated(0.10),
            "oom_floor_bytes": dated(1 * GIB), "heavy_slots": dated(2),
            "gpu_shares": dated({"embedder_mib": 0, "reranker_mib": 0}),
            "embedding_servers": {
                "shared": {"cpus": cpu, "nice": 10, "date": today, "source": "planted"},
                "query": {"cpus": cpu, "nice": 10, "date": today, "source": "planted"},
            },
        }
        write(self.home / ".gov-os" / "machine" / "gate.json", json.dumps(values, indent=1))
        files = {
            "GOV_RESOURCES_MEMINFO": ("meminfo", f"MemTotal: {80 * GIB // 1024} kB\nMemAvailable: {64 * GIB // 1024} kB\n"),
            "GOV_RESOURCES_LOADAVG": ("loadavg", "0.00 0.00 0.00 1/321 54321\n"),
            "GOV_RESOURCES_BUSY_CORES": ("busy", "0\n"),
            "GOV_RESOURCES_EMBEDDING_CPU": ("embedding-cpu.json", json.dumps({"shared": 0, "query": 0})),
            "GOV_RESOURCES_EMBEDDING_CPU_NOW": ("embedding-cpu-now.json", json.dumps({"shared": 0, "query": 0})),
            "GOV_RESOURCES_DISK": ("disk.json", json.dumps({"free_bytes": 1024 * GIB, "free_inodes": 100_000_000})),
        }
        self.gate_env = {"GOV_RESOURCES_NPROC": "64"}
        for variable, (name, text) in files.items():
            self.gate_env[variable] = str(write(self.readings / name, text))

    def _plant_repo(self) -> None:
        root = self.root
        root.mkdir()
        subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True, timeout=COMMAND_TIMEOUT_S,
                       env={"PATH": SAFE_PATH, "HOME": str(self.home), "GIT_CONFIG_NOSYSTEM": "1"})
        write(root / "README.md", "W2-153 launch fixture\n")
        write(root / ".claude" / "settings.json", json.dumps(GUARD_SETTINGS, indent=2) + "\n")
        for tid, (role, ref, paths) in TICKETS.items():
            listed = "".join(f"- {p}\n" for p in paths)
            write(root / ".tickets" / f"{tid}.md",
                  f"---\nid: {tid}\nstatus: in_progress\nrole: {role}\nexternal-ref: {ref}\n"
                  f"allowed_paths:\n{listed}---\n# {tid}\n")
        (root / "experiments" / "w2-153-probe").mkdir(parents=True)
        write(root / "template/governance/kernel/launch/research-allowlist.yaml", "hosts:\n  - example.org\n")
        for stem in TEMPLATE_STEMS:
            write(self.template(stem), template_text(stem))

    def template(self, stem: str) -> Path:
        return self.root / ".claude" / "templates" / f"{stem}.md"

    def expected_path(self, role: str) -> str:
        return str(self.root / ".claude" / "templates" / f"{ROLE_TEMPLATE[role]}.md")

    def launch(self, role: str, cli_args: list[str], *, src: Path = SRC, ticket: str | None = None) -> dict:
        """Run ``gov.launch.launcher.launch`` in a child process on the code under ``src``. Returns
        ``{"result": {...}, "calls": [...], "stderr": str}``: the result is ``{"exit": n}`` or
        ``{"error": {"code", "message"}}``; the calls are the stand-in CLI's records of this run."""
        self._runs += 1
        record = self.base / f"calls-{self._runs}.jsonl"
        out = self.base / f"result-{self._runs}.json"
        spec = self.base / f"spec-{self._runs}.json"
        write(spec, json.dumps({"root": str(self.root), "role": role, "ticket": ticket or TICKET_OF[role],
                                "cli_args": list(cli_args), "out": str(out)}))
        point_record(self.cli, record)
        env = {"PATH": SAFE_PATH, "HOME": str(self.home), "TMPDIR": str(self.tmp), "LC_ALL": "C",
               "PYTHONPATH": str(src), "PYTHONDONTWRITEBYTECODE": "1", "GIT_CONFIG_NOSYSTEM": "1",
               **self.gate_env}
        done = subprocess.run([sys.executable, str(HARNESS), str(spec)], cwd=str(self.base), env=env,
                              capture_output=True, text=True, timeout=COMMAND_TIMEOUT_S, stdin=subprocess.DEVNULL)
        assert out.exists(), (f"the launch harness wrote no result (exit {done.returncode})\n"
                              f"stdout: {done.stdout}\nstderr: {done.stderr}")
        return {"result": json.loads(out.read_text(encoding="utf-8")), "calls": read_calls(record),
                "stderr": done.stderr}

    def normalised(self, call: dict) -> list[str]:
        """A call's arguments with its session temp folder and the home replaced by fixed words (they differ
        from run to run and are not what F2 compares)."""
        tmpdir = call.get("tmpdir") or "\0"
        return [arg.replace(tmpdir, "<SESSION-TMPDIR>").replace(str(self.home), "<HOME>") for arg in call["argv"]]


# --- the dispatcher bed (S2, F1, F2) -----------------------------------------------------------------------------------

DISPATCH_W2 = "W2-9534"
DISPATCH_TICKET = "W153-LEAD"


class DispatchBed:
    """The dispatcher's lead line run as a copy whose absolute paths point into a temporary folder: the orchestrator
    folder (with a disk gate that passes, the brief and the log folder), the worktrees folder (with the lead's tree)
    and the CLI (the stand-in, also first on PATH and at ``$HOME/.local/bin/claude``)."""

    REAL_ORCH = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator"
    REAL_MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
    REAL_TREES = "/home/usain/gov-os-worktrees"
    REAL_CLI = "/home/usain/.local/bin/claude"
    REAL_HOME = "/home/usain"

    def __init__(self, base: Path):
        self.base = Path(os.path.realpath(base))
        self.orch = self.base / "main" / ".gov-runtime" / "scratch" / "orchestrator"
        self.main = self.base / "main"
        self.trees = self.base / "worktrees"
        self.home = self.base / "home"
        self.bin = self.base / "bin"
        self.tree = self.trees / DISPATCH_W2
        write(self.orch / "tools" / "disk_gate.sh", "#!/usr/bin/env bash\nexit 0\n")
        write(self.orch / "briefs" / "brief.md", "W2-153 fixture brief\n")
        (self.orch / "log").mkdir(parents=True)
        write(self.tree / "README.md", "W2-153 lead tree\n")
        for stem in TEMPLATE_STEMS:
            write(self.tree / ".claude" / "templates" / f"{stem}.md", template_text(stem))
        self.cli = stub_cli(self.bin / "claude")
        self.home_cli = stub_cli(self.home / ".local" / "bin" / "claude")
        # DEC-1133 (3): the lead line checks the resource gate and registers the lead with gov; here the gate is open
        write(self.home / ".local" / "bin" / "gov", "#!/usr/bin/env bash\nexit 0\n").chmod(0o755)
        self._runs = 0

    def expected_path(self) -> str:
        return str(self.tree / ".claude" / "templates" / "role-lead.md")

    def rewrite(self, text: str) -> str:
        """The script's text with its real paths pointed into this bed, in one pass (longest first)."""
        table = {self.REAL_ORCH: str(self.orch), self.REAL_CLI: str(self.cli), self.REAL_MAIN: str(self.main),
                 self.REAL_TREES: str(self.trees), self.REAL_HOME: str(self.home)}
        pattern = re.compile("|".join(re.escape(key) for key in sorted(table, key=len, reverse=True)))
        rewritten = pattern.sub(lambda m: table[m.group(0)], text)
        assert "/home/usain" not in rewritten.replace(str(self.base), ""), "a real path is left in the script copy"
        return rewritten

    def run(self, script_text: str) -> dict:
        self._runs += 1
        script = write(self.base / f"launch_now-{self._runs}.sh", self.rewrite(script_text))
        record = self.base / f"calls-{self._runs}.jsonl"
        for stub in (self.cli, self.home_cli):
            point_record(stub, record)
        env = {"PATH": f"{self.bin}:{SAFE_PATH}", "HOME": str(self.home), "TMPDIR": str(self.base), "LC_ALL": "C"}
        done = subprocess.run(["bash", str(script), DISPATCH_W2, DISPATCH_TICKET, "brief.md", f"out-{self._runs}.json"],
                              cwd=str(self.base), env=env, capture_output=True, text=True,
                              timeout=COMMAND_TIMEOUT_S, stdin=subprocess.DEVNULL)
        return {"exit": done.returncode, "stderr": done.stderr, "calls": read_calls(record)}


def current_dispatch_script() -> str:
    return (REPO / DISPATCH_REL).read_text(encoding="utf-8")


# --- the portability bed (S3, S4) --------------------------------------------------------------------------------------

ROLE_BODY = ("# Engineer role (fixture)\n\n- **Purpose:** build one ticket.\n- **Tools:** Read, Grep and\n  Bash. "
             "No installs.\n- **Network:** none.\n")
RULESYNC_FRONT = ('---\nname: engineer\ntargets: ["claudecode"]\ndescription: "Engineer role (fixture)."\n'
                  'claudecode:\n  tools: ["Read", "Grep", "Bash"]\n')
ENGINEER_TEMPLATE_BODY = "# You are the engineer (fixture)\nYou build the code to fulfil the spec and its KPIs.\n"
SKILL_TEXT = "---\nname: test-driven-development\ndescription: fixture skill\n---\n\n# TDD\n\nA method.\n"
GENERATED = {"CLAUDE.md": "# Rules\n", ".claude/settings.json": '{\n  "permissions": {"deny": ["Bash(sudo *)"]}\n}\n',
             ".claude/agents/engineer.md": "an engineer\n",
             ".claude/skills/test-driven-development/SKILL.md": "a method\n"}


def kernel_template_text(stem: str) -> str:
    """Distinct bytes for each fixture template: a CRLF line and no newline at the end for one of them, so a copy
    is judged byte for byte, never line by line."""
    if stem == "role-engineer":
        return ("---\nname: role-engineer\nversion: 1.0.0\nrole: engineer\n"
                "skills: [test-driven-development]\n---\n" + ENGINEER_TEMPLATE_BODY)
    if stem == "role-cto":
        return "---\nname: role-cto\nversion: 1.0.0\n---\n# CTO (fixture)\r\nno newline at the end"
    return f"---\nname: {stem}\nversion: 1.0.0\n---\n# {stem} (fixture)\n"


ENGINEER_COMPOSED_BODY = composed_body(ENGINEER_TEMPLATE_BODY, ROLE_BODY)


def composed_source(*, skills: list[str] | None = ("test-driven-development",), body: str = ENGINEER_COMPOSED_BODY,
                    top_level: bool = False) -> str:
    """S3's source: the list sits under ``claudecode: skills:`` (DEC-1112 (3): rulesync 24.0.0 drops a top-level
    ``skills``). ``top_level=True`` plants it at the top level instead, with none under ``claudecode``. Its body is
    S3 amended's (the template's body, a blank line, the role file's body) unless ``body`` names another."""
    front = RULESYNC_FRONT
    if skills is not None:
        listed = f"skills: [{', '.join(skills)}]\n"
        front += listed if top_level else "  " + listed
    return front + "---\n\n" + body


class PortabilityBed:
    """A project in this repository's layout (``template/governance/kernel``) with one kernel role (engineer), its
    template and the other seven, the one kernel skill it lists, the rulesync sources composed as S3 states, the
    eight ``.claude/templates/`` copies, and a stand-in rulesync that writes the generated files the project holds."""

    def __init__(self, base: Path):
        self.base = Path(os.path.realpath(base))
        self.root = root = self.base / "project"
        write(root / "governance/project/tool-registry.yaml", 'tools:\n  - name: rulesync\n    version: "24.0.0"\n')
        write(root / ".rulesync/rules/governance.md", "---\nroot: true\n---\n\n# Rules\n")
        kernel = root / "template/governance/kernel"
        write(kernel / "roles/engineer.md", ROLE_BODY)
        for stem in (*TEMPLATE_STEMS, "ticket"):
            write(kernel / "templates" / f"{stem}.md", kernel_template_text(stem))
        write(kernel / "skills/superpowers/test-driven-development/SKILL.md", SKILL_TEXT)
        write(root / ".rulesync/skills/test-driven-development/SKILL.md", SKILL_TEXT)
        for tree in (".rulesync", "template/.rulesync"):
            write(root / tree / "subagents/engineer.md", composed_source())
        for stem in TEMPLATE_STEMS:
            write(self.copy(stem), kernel_template_text(stem).encode("utf-8"))
        for rel, text in GENERATED.items():
            write(root / rel, text)
        made = self.base / "made"
        for rel, text in GENERATED.items():
            write(made / rel, text)
        self.rulesync = write(self.base / "bin" / "rulesync", (
            "#!/bin/bash\n"
            'if [[ "$1" == "--version" ]]; then echo "24.0.0"; exit 0; fi\n'
            f'cp -r "{made}/." .\n'
        ))
        self.rulesync.chmod(0o755)
        (self.base / "home").mkdir()

    def copy(self, stem: str) -> Path:
        return self.root / ".claude" / "templates" / f"{stem}.md"

    def source(self) -> Path:
        return self.root / ".rulesync/subagents/engineer.md"

    def compose(self, role: str = "engineer") -> dict:
        """``gov.adapters.portability.compose(<project root as a Path>, role)`` in a child process on this tree's
        code: ``{"exit": n, "text": str | None, "stderr": str}``."""
        program = ("import json, sys\nfrom pathlib import Path\nfrom gov.adapters.portability import compose\n"
                   "text = compose(Path(sys.argv[1]), sys.argv[2])\n"
                   "sys.stdout.write(json.dumps({'type': type(text).__name__, 'text': text}))\n")
        done = subprocess.run([sys.executable, "-c", program, str(self.root), role], cwd=str(self.base),
                              env=portability_env(self.base, RULESYNC_BIN=str(self.rulesync)),
                              capture_output=True, text=True, timeout=COMMAND_TIMEOUT_S, stdin=subprocess.DEVNULL)
        printed = json.loads(done.stdout) if done.returncode == 0 and done.stdout.strip() else {}
        return {"exit": done.returncode, "type": printed.get("type"), "text": printed.get("text"),
                "stderr": done.stderr}

    def check(self) -> tuple[int, dict, str]:
        """``python3 -m gov.adapters.portability`` in the project: ``(exit code, printed JSON, stderr)``."""
        done = subprocess.run([sys.executable, "-m", "gov.adapters.portability"], cwd=str(self.root),
                              env=portability_env(self.base, RULESYNC_BIN=str(self.rulesync)),
                              capture_output=True, text=True, timeout=COMMAND_TIMEOUT_S, stdin=subprocess.DEVNULL)
        try:
            printed = json.loads(done.stdout)
        except ValueError:
            raise AssertionError(f"the check printed no JSON (exit {done.returncode})\nstdout: {done.stdout}\n"
                                 f"stderr: {done.stderr}") from None
        return done.returncode, printed, done.stderr


def portability_env(base: Path, **extra) -> dict:
    home = base / "home"
    home.mkdir(exist_ok=True)
    return {"PATH": SAFE_PATH, "HOME": str(home), "TMPDIR": str(base), "LC_ALL": "C", "PYTHONPATH": str(SRC),
            "PYTHONDONTWRITEBYTECODE": "1", **extra}


def naming(findings: list[dict], rel: str) -> list[dict]:
    """The findings that name ``rel``, in their file or their message."""
    return [f for f in findings if f.get("file") == rel or rel in str(f.get("message", ""))]


def design_skill_reconciled() -> bool:
    """Whether W2-128 has reconciled the kernel test-design skill with DEC-963 (review F7): until then the test
    designer's skills list leaves ``test-design`` out (the ticket's Interface)."""
    return "DEC-963" in TEST_DESIGN_SKILL.read_text(encoding="utf-8")
