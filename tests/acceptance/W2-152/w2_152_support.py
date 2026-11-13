"""Shared helpers of the W2-152 acceptance tests (README).

Every case builds a small repository of its own under ``tmp_path`` (a ``.tickets/`` with planted tickets, a
``governance/project/facts.yaml`` and the kernel templates: copied from this tree, or a planted set from
``fixtures/planted/`` where the case needs control) and runs ``python3 -m gov.cli.main brief ... --root <tmp>`` as a
subprocess, the public interface. The interface is the ticket's body, "Interface" (DAEO-o5x1), and W2-128's
"Interface and rounds" (DAEO-t8mp); nothing here reads this ticket's implementation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import site
import stat
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SRC = REPO / "src"
TEMPLATES = REPO / "template/governance/kernel/templates"
FACTS = REPO / "governance/project/facts.yaml"
FACTS_SCHEMA = REPO / "template/governance/kernel/schemas/facts.schema.json"
PLANTED = HERE / "fixtures/planted"
GOLDEN = HERE / "fixtures/golden"
SPY = HERE / "w2_152_spy.py"

TEMPLATES_REL = "template/governance/kernel/templates"
FALLBACK_TEMPLATES_REL = "governance/kernel/templates"
FACTS_REL = "governance/project/facts.yaml"

# The ticket's role -> template map ("Interface").
WORKER_ROLES = {
    "engineer": "role-engineer",
    "independent-test-designer": "role-test-designer",
    "independent-auditor": "role-reviewer",
    "product-spec": "role-product-spec",
    "research": "role-research",
}
RUN_KINDS = ("tests", "build", "review", "resume", "land")

# The date the fixtures' facts carry as ready.new_since (S9), and creation times either side of it.
NEW_SINCE = "2026-11-10"
CREATED_BEFORE = "2026-11-09T23:59:59Z"
CREATED_ON = "2026-11-10T00:00:00Z"
CREATED_AFTER = "2026-11-11T08:00:00Z"

TICKET_ID = "DAEO-fx01"
TICKET_W2 = "W2-901"
TITLE = "Build the widget"
TIMEOUT = 60


# --- tickets --------------------------------------------------------------------------------------------------------

def ready_front(ticket_id: str = TICKET_ID, w2: str = TICKET_W2) -> dict:
    """A ticket's front matter that is READY on every count: every required field, both advisory items satisfied,
    and the three dependency fields set (it is created after ``NEW_SINCE``). Two KPI lines carry their verify in
    each form: ``{line, verify}`` and a string holding ``Verify:`` and text."""
    return {
        "id": ticket_id,
        "status": "in_progress",
        "deps": [],
        "links": [],
        "created": CREATED_AFTER,
        "type": "task",
        "priority": 1,
        "assignee": "engineer",
        "external-ref": w2,
        "tags": ["fixture"],
        "wbs_id": w2,
        "title": TITLE,
        "class": "tool",
        "state_class": "AUTHORITATIVE",
        "role": "engineer",
        "depends_on": [],
        "allowed_paths": ["src/widget/**", "tests/unit/widget/**"],
        "reads": ["src/widget/**"],
        "needs": [],
        "waits_on": [],
        "kpis": {
            "success": [
                {"line": "S1 The widget prints its name [DEC-1].",
                 "verify": "a unit test runs the widget and reads its name"},
                "S2 The widget refuses an empty name [DEC-1]. Verify: a unit test with an empty name",
            ],
            "failure": [
                {"line": "The widget prints nothing.", "verify": "the unit test of S1 fails"},
            ],
        },
        "non_goals": ["No graphical interface."],
        "done_when": ["DOD-1", "DOD-2", "DOD-3", "DOD-5", "DOD-6"],
        "profile": "STANDARD",
        "sources": ["DEC-1"],
        "est_loc": 120,
        "acceptance_tests": {"path": f"tests/acceptance/{w2}/"},
        "track": "A",
    }


def ticket_text(front: dict, body: str | None = None) -> str:
    """The ticket file as tk writes it: front matter between ``---`` lines (``created`` unquoted, tk's form), then
    the body."""
    front = dict(front)
    created = front.pop("created", None)
    dumped = yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=1000, default_flow_style=False)
    lines = dumped.rstrip("\n").split("\n")
    if created is not None:
        lines.insert(3 if len(lines) >= 3 else len(lines), f"created: {created}")
    title = front.get("title", "")
    if body is None:
        body = f"# {front.get('wbs_id', '')} {title}\n\nThe widget prints its name when asked, and refuses an empty one.\n"
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def closed_ticket(ticket_id: str, w2: str, status: str = "closed") -> dict:
    front = ready_front(ticket_id, w2)
    front["status"] = status
    front["title"] = f"Fixture ticket {w2}"
    return front


# --- facts ----------------------------------------------------------------------------------------------------------

def planted_facts() -> dict:
    """A small facts file under the case's control (``facts.schema.json``'s shape, plus ``ready.new_since``)."""
    return {
        "paths": {
            "main": "/fx/main",
            "tree": "/fx/wt/{W2}",
            "tests_tree": "/fx/wt/{W2}-tests",
            "store_tree": "/fx/store",
            "tools": "/fx/tools",
            "ticket_file": "{MAIN}/.tickets/{ID}.md",
        },
        "commands": {
            "identity": {"run": "printenv GOV_ROLE GOV_TICKET", "check": "printenv --version"},
            "accept": {"run": "gov accept {W2} --root {WRITE_TREE}", "check": "gov accept --help"},
            "retrieve": {"run": "gov retrieve --root {STORE_TREE} --help", "check": "gov retrieve --help"},
            "lead_verify": {"run": "bash {TOOLS}/lead_verify.sh {TREE} {W2} {ID}", "check": "true"},
            "launch_worker": {"run": "bash {TOOLS}/launch_worker.sh", "check": "true"},
            "wait_for": {"run": "bash {TOOLS}/wait_for.sh", "check": "true"},
            "links": {"run": "gov links --help", "check": "gov links --help"},
            "pytest_folder": {"run": "python3 -m pytest --version", "check": "python3 -m pytest --version"},
        },
        "dod": [{"id": "DOD-1", "line": "The acceptance suite passes."}],
        "steps": {
            "alpha": {"on": True, "line": "Alpha step: run {CMD:identity} [DEC-1].", "match": "alpha"},
            "beta": {"on": True, "line": "Beta step line.", "match": "beta"},
            "gamma": {"on": True, "line": "Gamma step line.", "match": "gamma"},
        },
        "budgets": {
            "brief": 4321,
            "role-engineer": 3500,
            "role-test-designer": 3500,
            "role-reviewer": 3500,
            "role-product-spec": 3500,
            "role-research": 3500,
            "role-lead": 8000,
        },
        "harness_allowed": ["Bash", "Read"],
        "ready": {"new_since": NEW_SINCE},
    }


def real_facts() -> dict:
    """This tree's facts file, with ``ready.new_since`` set to the fixtures' date (it may not hold one yet)."""
    data = yaml.safe_load(FACTS.read_text(encoding="utf-8"))
    data = copy.deepcopy(data)
    data["ready"] = {"new_since": NEW_SINCE}
    return data


# --- the fixture repository -----------------------------------------------------------------------------------------

class Repo:
    """A temporary repository a case builds: tickets, facts and templates; ``run`` calls ``gov brief`` on it."""

    def __init__(self, root: Path, templates: str = "planted", facts: dict | None = None,
                 templates_rel: str = TEMPLATES_REL):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / ".tickets").mkdir(exist_ok=True)
        self.templates_dir = self.root / templates_rel
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        if templates == "real":
            for path in sorted(TEMPLATES.iterdir()):
                if path.is_file():
                    shutil.copyfile(path, self.templates_dir / path.name)
            self.write_facts(facts if facts is not None else real_facts())
        else:
            for path in sorted(PLANTED.iterdir()):
                if path.is_file():
                    shutil.copyfile(path, self.templates_dir / path.name)
            shutil.copyfile(TEMPLATES / "keys.yaml", self.templates_dir / "keys.yaml")
            self.write_facts(facts if facts is not None else planted_facts())
        self.ticket(ready_front())

    # inputs
    def write_facts(self, data: dict) -> None:
        path = self.root / FACTS_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000), encoding="utf-8")

    def facts(self) -> dict:
        return yaml.safe_load((self.root / FACTS_REL).read_text(encoding="utf-8"))

    def ticket(self, front: dict, body: str | None = None) -> Path:
        path = self.root / ".tickets" / f"{front['id']}.md"
        path.write_text(ticket_text(front, body), encoding="utf-8")
        return path

    def edit_ticket(self, ticket_id: str = TICKET_ID, **changes) -> Path:
        """The READY ticket with fields changed; a value ``DROP`` removes the field."""
        front = ready_front(ticket_id)
        for key, value in changes.items():
            if value is DROP:
                front.pop(key, None)
            else:
                front[key] = value
        return self.ticket(front)

    def template(self, name: str) -> Path:
        return self.templates_dir / name

    def append_template_line(self, name: str, line: str) -> None:
        path = self.template(name)
        text = path.read_text(encoding="utf-8")
        path.write_text(text.rstrip("\n") + "\n" + line + "\n", encoding="utf-8")

    def file(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    # the run
    def run(self, *args: str, json_out: bool = False, cwd: Path | None = None, env: dict | None = None,
            spy_log: Path | None = None) -> subprocess.CompletedProcess:
        argv = ["brief", *args, "--root", str(self.root)]
        if json_out:
            argv.append("--json")
        if spy_log is not None:
            command = [sys.executable, "-B", str(SPY), str(spy_log), *argv]
        else:
            command = [sys.executable, "-B", "-m", "gov.cli.main", *argv]
        return subprocess.run(command, capture_output=True, text=True, timeout=TIMEOUT,
                              cwd=str(cwd or self.root.parent), env=child_env(self.root.parent, env),
                              stdin=subprocess.DEVNULL)


class _Drop:
    def __repr__(self) -> str:
        return "DROP"


DROP = _Drop()


def child_env(scratch: Path, extra: dict | None = None) -> dict:
    """The child's environment: this tree's ``src`` first, an empty ``HOME``, no bytecode written, no network."""
    home = scratch / "empty-home"
    home.mkdir(exist_ok=True)
    env = {key: value for key, value in os.environ.items() if not key.startswith(("PYTEST_", "GOV_"))}
    env.setdefault("PYTHONUSERBASE", site.getuserbase())
    dead = "http://127.0.0.1:9"
    env.update({"PYTHONPATH": str(SRC), "HOME": str(home), "PYTHONDONTWRITEBYTECODE": "1",
                "http_proxy": dead, "https_proxy": dead, "HTTP_PROXY": dead, "HTTPS_PROXY": dead,
                "OLLAMA_HOST": "127.0.0.1:9", "CUDA_VISIBLE_DEVICES": ""})
    if extra:
        env.update(extra)
    return env


def accept_env(scratch: Path) -> dict:
    """The environment for a nested ``gov accept``: its runner drops every ``PYTHON*`` variable, so the scratch
    ``HOME``'s ``.local`` links to the real user site (where pytest is installed); nothing else of the real home."""
    env = child_env(scratch)
    local = Path(env["HOME"]) / ".local"
    if not local.exists():
        local.symlink_to(site.getuserbase(), target_is_directory=True)
    return env


# --- reading what came back -----------------------------------------------------------------------------------------

def missing_command(done: subprocess.CompletedProcess) -> str:
    """A note for an assertion message when the CLI has no ``brief`` command (integrate before the ticket)."""
    if done.returncode == 2 and "invalid choice: 'brief'" in done.stderr:
        return " [gov has no brief command: argparse 'invalid choice']"
    return ""


def describe(done: subprocess.CompletedProcess) -> str:
    return (f"exit {done.returncode}{missing_command(done)}\n--- stdout ---\n{done.stdout[-3000:]}"
            f"\n--- stderr ---\n{done.stderr[-3000:]}")


def ok(done: subprocess.CompletedProcess) -> str:
    """The brief text of a run that must succeed (exit 0, something on stdout)."""
    assert done.returncode == 0, f"gov brief did not succeed: {describe(done)}"
    assert done.stdout.strip(), f"gov brief printed no brief: {describe(done)}"
    return done.stdout


def envelope(done: subprocess.CompletedProcess) -> dict:
    """The API-0002 envelope of a ``--json`` run."""
    try:
        data = json.loads(done.stdout)
    except ValueError:
        raise AssertionError(f"--json printed no JSON envelope: {describe(done)}") from None
    assert isinstance(data, dict) and "ok" in data, f"not an API-0002 envelope: {done.stdout[:500]}"
    return data


def refusal(done: subprocess.CompletedProcess) -> list[tuple[str, str]]:
    """The findings of a ``--json`` refusal: ``GovError("BRIEF_NOT_READY")``, non-zero exit, ``details.findings``
    a list of ``{code, detail}``."""
    assert done.returncode != 0, f"gov brief did not refuse: {describe(done)}"
    data = envelope(done)
    assert data.get("ok") is False, f"the envelope is not a refusal: {data}"
    error = data.get("error") or {}
    assert error.get("code") == "BRIEF_NOT_READY", f"the error is not BRIEF_NOT_READY: {error}"
    findings = (error.get("details") or {}).get("findings")
    assert isinstance(findings, list) and findings, f"details.findings is not a non-empty list: {error}"
    pairs = []
    for item in findings:
        assert isinstance(item, dict) and "code" in item and "detail" in item, \
            f"a finding is not {{code, detail}}: {item!r}"
        pairs.append((str(item["code"]), str(item["detail"])))
    return pairs


def has(pairs: list[tuple[str, str]], code: str, needle: str | None = None,
        exact_first: bool = False) -> bool:
    """Whether a finding (or warning) with ``code`` names ``needle``: in its detail, or as the detail's first word
    when ``exact_first``."""
    for found, detail in pairs:
        if found != code:
            continue
        if needle is None:
            return True
        if exact_first and re.match(rf"^\s*{re.escape(needle)}(?![\w-])", detail):
            return True
        if not exact_first and needle in detail:
            return True
    return False


def plain_refusal(done: subprocess.CompletedProcess, *expected: tuple[str, str]) -> None:
    """Without ``--json``: non-zero exit, nothing on stdout, and stderr names BRIEF_NOT_READY and each
    ``(code, detail)`` on one line."""
    assert done.returncode != 0, f"gov brief did not refuse: {describe(done)}"
    assert done.stdout == "", f"a refusal printed something on stdout: {describe(done)}"
    assert "BRIEF_NOT_READY" in done.stderr, f"stderr does not name BRIEF_NOT_READY: {describe(done)}"
    lines = done.stderr.splitlines()
    for code, needle in expected:
        assert any(code in line and needle in line for line in lines), \
            f"no stderr line names {code} {needle}: {describe(done)}"


def warning_codes(items) -> list[tuple[str, str]]:
    """``result.warnings`` as ``(code, detail)`` pairs: items that are ``{code, detail}`` or ``"<CODE> <detail>"``."""
    assert isinstance(items, list), f"result.warnings is not a list: {items!r}"
    pairs = []
    for item in items:
        if isinstance(item, dict):
            pairs.append((str(item.get("code", "")), str(item.get("detail", ""))))
        else:
            text = str(item).removeprefix("gov brief:").strip()
            code, _, detail = text.partition(" ")
            pairs.append((code, detail))
    return pairs


def stderr_warning(done: subprocess.CompletedProcess, code: str) -> list[str]:
    """The stderr lines in the form ``gov brief: <CODE> <detail>`` for ``code``."""
    return [line for line in done.stderr.splitlines() if re.match(rf"^gov brief: {code}(\s|$)", line)]


# --- text -----------------------------------------------------------------------------------------------------------

def strip_front_matter(text: str) -> str:
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for number, line in enumerate(lines[1:], 1):
            if line.rstrip() == "---":
                return "\n".join(lines[number + 1:])
    return text


def normal(text: str) -> str:
    """The comparison form of a brief (README): a leading front-matter block dropped, trailing white space dropped
    from each line, and leading and trailing blank lines dropped."""
    text = strip_front_matter(text)
    return "\n".join(line.rstrip() for line in text.split("\n")).strip("\n")


def golden(name: str) -> str:
    return normal((GOLDEN / name).read_text(encoding="utf-8"))


def contains_block(text: str, block: str) -> bool:
    """Whether the lines of ``block`` occur in ``text`` as one contiguous run of lines (trailing space ignored)."""
    lines = [line.rstrip() for line in text.split("\n")]
    want = [line.rstrip() for line in block.strip("\n").split("\n")]
    return any(lines[i:i + len(want)] == want for i in range(len(lines) - len(want) + 1))


PLACEHOLDER = re.compile(r"\{[^{}]*\}")


def fragments(line: str, minimum: int = 25) -> list[str]:
    """The placeholder-free pieces of a template line, ``minimum`` characters or longer, white space trimmed."""
    return [piece.strip() for piece in PLACEHOLDER.split(line) if len(piece.strip()) >= minimum]


def role_fragments(stem: str, exclude_lines: set[str] = frozenset(), templates: Path = TEMPLATES) -> list[str]:
    """Distinctive text of a role template's body: fragments of its lines that occur neither in T-0 nor in the facts
    file (so their presence in a brief can only come from the role template)."""
    shared = (templates / "brief.md").read_text(encoding="utf-8") + "\n" + FACTS.read_text(encoding="utf-8")
    body = strip_front_matter((templates / f"{stem}.md").read_text(encoding="utf-8"))
    found = []
    for line in body.split("\n"):
        if line.strip() in exclude_lines:
            continue
        for piece in fragments(line):
            if piece not in shared:
                found.append(piece)
    return found


def lead_blocks(text: str) -> dict[str, list[str]]:
    """role-lead.md's run blocks as the ticket defines them (S6): in the section ``## Your run: {RUN_KIND}``, each
    kind's block begins with a line ``**<kind>**:`` and runs to the next such line or the section's first
    ``{STEP:`` line."""
    lines = strip_front_matter(text).split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith("## Your run: {RUN_KIND}"))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    blocks: dict[str, list[str]] = {}
    current = None
    for line in lines[start + 1:end]:
        if line.lstrip().startswith("{STEP:"):
            break
        marker = re.match(r"^\*\*(\w+)\*\*:", line)
        if marker:
            current = marker.group(1)
            blocks[current] = []
        if current is not None:
            blocks[current].append(line)
    for kind in blocks:
        while blocks[kind] and not blocks[kind][-1].strip():
            blocks[kind].pop()
    return blocks


# --- the tree as it stands ------------------------------------------------------------------------------------------

def snapshot(root: Path) -> dict[str, tuple]:
    """Every entry under ``root``: its kind, mode, size, modification time and content hash."""
    found = {}
    for path in sorted(root.rglob("*")):
        info = path.lstat()
        rel = str(path.relative_to(root))
        if stat.S_ISDIR(info.st_mode):
            found[rel] = ("dir", stat.S_IMODE(info.st_mode), info.st_mtime_ns)
        else:
            try:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
            except PermissionError:
                digest = "unreadable"
            found[rel] = ("file", stat.S_IMODE(info.st_mode), info.st_size, info.st_mtime_ns, digest)
    return found


def spy_events(log: Path) -> list[dict]:
    if not log.is_file():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]
