"""Shared helpers of the W2-128 acceptance tests (README).

Everything here reads files as the tree holds them: the nine templates, the record templates, ``keys.yaml``,
``governance/project/facts.yaml`` and its schema, the ticket and record schemas, the register. The interface is the
ticket's "Interface and rounds" section (DAEO-t8mp); nothing here reads this ticket's implementation branch.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]

TEMPLATES = REPO / "template/governance/kernel/templates"
SCHEMAS = REPO / "template/governance/kernel/schemas"
ROLES = REPO / "template/governance/kernel/roles"
FACTS = REPO / "governance/project/facts.yaml"
FACTS_SCHEMA = SCHEMAS / "facts.schema.json"
KEYS = TEMPLATES / "keys.yaml"
REGISTER = REPO / "docs/DECISION_REGISTER.md"
CIT_P = REPO / "docs/changes/W2-128-CIT-P.md"
TOOLS = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")

# The nine templates (ticket, "Files"; R3 Appendix T-0 to T-8) and R3 §C's prose budgets.
NINE = {
    "brief": "T-0",
    "ticket": "T-1",
    "role-research": "T-2",
    "role-product-spec": "T-3",
    "role-test-designer": "T-4",
    "role-engineer": "T-5",
    "role-reviewer": "T-6",
    "role-lead": "T-7",
    "role-cto": "T-8",
}
BUDGET = {
    "brief": 4000,
    "ticket": 4000,
    "role-research": 3500,
    "role-product-spec": 3500,
    "role-test-designer": 3500,
    "role-engineer": 3500,
    "role-reviewer": 3500,
    "role-lead": 8000,
    "role-cto": 6000,
}
# The record templates that stay and gain the link lines (ticket, "Files"; LINK-INTEGRITY §5).
RECORDS = ("checkpoint", "decision-record", "decision-package", "failure", "lesson", "research")
OLD_BRIEFS = {
    "brief-engineer.md": "role-engineer.md",
    "brief-test-designer.md": "role-test-designer.md",
    "brief-reviewer.md": "role-reviewer.md",
    "brief-product-spec.md": "role-product-spec.md",
    "brief-lead.md": "role-lead.md",
}
# The commands facts.yaml must hold at least (ticket, "The facts file").
REQUIRED_COMMANDS = ("retrieve", "lead_verify", "launch_worker", "wait_for", "links", "accept", "pytest_folder")
FACTS_TOP = ("paths", "commands", "dod", "steps", "budgets", "harness_allowed")
# The keys the Appendix names, plus {BASE} (LINK-INTEGRITY §5: "{ID}, {IMPL} and {BASE} are the generator's keys").
APPENDIX_KEYS = ("ID", "W2", "PROFILE", "IMPL", "EST", "TREE", "TESTS_TREE", "MAIN", "TOOLS", "STORE_TREE", "BASE")

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
KEY_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")
# Placeholders (ticket, "Placeholders"): {KEY} or {KEY: description}; {CMD:name ...}; {STEP:name}. A brace that a
# shell's $ opens (${HOME}) is no placeholder; lower-case braces are none.
KEY_PLACEHOLDER = re.compile(r"(?<!\$)\{([A-Z][A-Z0-9_]*)(?=[}:])")
CMD_PLACEHOLDER = re.compile(r"(?<!\$)\{CMD:([^\s{}]+)")
STEP_PLACEHOLDER = re.compile(r"(?<!\$)\{STEP:([^\s{}]+)")
# A family is an upper-case name and a colon with no space after it ({FACT:x}); {KEY: description} has the space.
FAMILY_PLACEHOLDER = re.compile(r"(?<!\$)\{([A-Z][A-Z0-9_]*):(?=[^\s}])")
BRACKET = re.compile(r"\[([^\[\]]*)\]")
DEC_ID = re.compile(r"\bDEC-\d{3,}\b")
DEC_IN_BRACKETS = re.compile(r"\[[^\[\]]*\bDEC-\d{3,}\b[^\[\]]*\]")
NEGATION = re.compile(r"\b(no|never|not|nothing|don't|do not|outside)\b", re.I)

CHECK_SECONDS = 5.0  # "each under a few seconds" (the brief)


# --- files ------------------------------------------------------------------------------------------------------

def template_path(stem: str) -> Path:
    return TEMPLATES / f"{stem}.md"


def read(path: Path) -> str:
    assert path.is_file(), f"{path.relative_to(REPO)} does not exist"
    return path.read_text(encoding="utf-8")


def template(stem: str) -> str:
    return read(template_path(stem))


def split(text: str) -> tuple[dict | None, str]:
    """(front matter, body): the front matter between the first line ``---`` and the next line ``---``."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    for number, line in enumerate(lines[1:], 1):
        if line.rstrip() == "---":
            front = yaml.safe_load("\n".join(lines[1:number]))
            return (front if isinstance(front, dict) else None), "\n".join(lines[number + 1:])
    return None, text


def body(stem: str) -> str:
    return split(template(stem))[1]


def prose(text: str) -> str:
    """The prose measure (ticket, "Prose size"): the text less fenced code blocks and table lines."""
    kept, fenced = [], False
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if fenced or stripped.startswith("|"):
            continue
        kept.append(line)
    return "\n".join(kept)


def fenced_blocks(text: str) -> list[tuple[str, str]]:
    """(info string, content) of every fenced block."""
    blocks, info, held, fenced = [], "", [], False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            if fenced:
                blocks.append((info, "\n".join(held)))
                fenced, held = False, []
            else:
                fenced, info = True, stripped.lstrip("`~").strip()
            continue
        if fenced:
            held.append(line)
    return blocks


def code_spans(text: str) -> list[str]:
    """The inline code spans and every fenced block's content."""
    outside = prose_and_tables(text)
    spans = re.findall(r"`([^`\n]+)`", outside)
    return spans + [content for _, content in fenced_blocks(text)]


def prose_and_tables(text: str) -> str:
    kept, fenced = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if not fenced:
            kept.append(line)
    return "\n".join(kept)


LABEL_LINE = re.compile(r"^\**[A-Z][A-Za-z0-9 ,'()/-]{0,40}:\**\s")  # "Start: ...", "**Done when:** ..."
ENDS_CITED = re.compile(r"\[[^\[\]]*\bDEC-\d{3,}\b[^\[\]]*\][.)]*\s*$")  # a rule line ends with its decision id


def units(text: str) -> list[str]:
    """The text as units a rule is stated in: a paragraph or a list item, its wrapped lines joined. A line that
    ends with a bracketed decision id ends its unit, and a line that opens with a label ("Start:") starts one; a
    heading, a table line and each line of a fenced block are units of their own."""
    found, held, fenced = [], [], False

    def flush():
        if held:
            found.append(" ".join(part.strip() for part in held))
            held.clear()

    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            flush()
            fenced = not fenced
            continue
        if fenced:
            if stripped:
                found.append(stripped)
            continue
        if not stripped:
            flush()
        elif stripped.startswith(("#", "|")):
            flush()
            found.append(stripped)
        elif re.match(r"^([-*+]|\d+[.)])\s", stripped) or LABEL_LINE.match(stripped):
            flush()
            held.append(stripped)
        else:
            held.append(stripped)
        if held and ENDS_CITED.search(stripped):
            flush()
    flush()
    return found


def fold(text: str) -> str:
    return " ".join(text.split()).lower()


# --- placeholders and facts --------------------------------------------------------------------------------------

def keys_of(text: str) -> set[str]:
    return {key for key in KEY_PLACEHOLDER.findall(text) if key not in ("CMD", "STEP")}


def cmds_of(text: str) -> set[str]:
    return set(CMD_PLACEHOLDER.findall(text))


def steps_of(text: str) -> set[str]:
    return set(STEP_PLACEHOLDER.findall(text))


def facts() -> dict:
    data = yaml.safe_load(read(FACTS))
    assert isinstance(data, dict), "governance/project/facts.yaml is not a mapping"
    return data


def facts_or_empty() -> dict:
    try:
        data = yaml.safe_load(FACTS.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


def commands(data: dict | None = None) -> dict:
    data = facts() if data is None else data
    found = data.get("commands")
    assert isinstance(found, dict), "facts.yaml has no commands mapping"
    return found


def expanded(unit: str, data: dict) -> str:
    """The unit with each {CMD:name} it names followed by that command's run form, so a line that names a
    command by its key reads as the command."""
    found = data.get("commands") if isinstance(data.get("commands"), dict) else {}
    runs = [str(found[name].get("run", "")) for name in cmds_of(unit)
            if isinstance(found.get(name), dict)]
    return unit + (" " + " ".join(runs) if runs else "")


def units_with(stem: str, *needles: str, any_of: tuple[str, ...] = (), pattern: re.Pattern | None = None) -> list[str]:
    """The units of a template (each {CMD:name} expanded) that hold every needle, case-insensitively and with white
    space folded; with ``any_of``, at least one of those too; with ``pattern``, a match of it."""
    data = facts_or_empty()
    hits = []
    for unit in units(template(stem)):
        text = fold(expanded(unit, data))
        if all(fold(needle) in text for needle in needles) \
                and (not any_of or any(fold(alt) in text for alt in any_of)) \
                and (pattern is None or pattern.search(text)):
            hits.append(unit)
    return hits


def fill(form: str, tree: Path, data: dict) -> str:
    """A check form with its placeholders filled for a run in ``tree`` (README, "The check runner")."""
    paths = data.get("paths") if isinstance(data.get("paths"), dict) else {}
    fixed = {"TREE": str(tree), "WRITE_TREE": str(tree), "TESTS_TREE": str(tree), "ROOT": str(tree),
             "BASE": "HEAD", "ID": "DAEO-t8mp", "W2": "W2-128", "ROLE": "engineer", "PROFILE": "STANDARD"}
    def one(match: re.Match) -> str:
        key = match.group(1)
        if key in fixed:
            return fixed[key]
        if key.lower() in paths:
            return str(paths[key.lower()])
        return match.group(0)

    for _ in range(6):  # a path may itself hold a key ({MAIN}/...)
        filled = re.sub(r"(?<!\$)\{([A-Z][A-Z0-9_]*)\}", one, form)
        if filled == form:
            break
        form = filled
    return form


def git(tree: Path, *args: str) -> None:
    env = dict(os.environ, GIT_AUTHOR_NAME="w2-128", GIT_AUTHOR_EMAIL="w2-128@example.invalid",
               GIT_COMMITTER_NAME="w2-128", GIT_COMMITTER_EMAIL="w2-128@example.invalid")
    done = subprocess.run(["git", "-C", str(tree), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"premise: git {' '.join(args)} failed: {done.stderr.strip()}"


def temporary_repository(tmp_path: Path) -> Path:
    tree = tmp_path / "repo"
    tree.mkdir()
    git(tree, "init", "-q")
    (tree / "README.md").write_text("a temporary repository for the facts' check forms\n", encoding="utf-8")
    git(tree, "add", "-A")
    git(tree, "commit", "-q", "-m", "first")
    git(tree, "commit", "-q", "--allow-empty", "-m", "second")
    return tree


def sealed_env(tmp_path: Path) -> dict:
    """No network (a dead proxy), no GPU, no model server, an empty HOME; the tree's own code first."""
    import site

    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    dead = "http://127.0.0.1:9"
    env = dict(os.environ)
    # the installed tools (pytest, check-jsonschema) stay where they are when HOME moves
    env.setdefault("PYTHONUSERBASE", site.getuserbase())
    env.update({"HOME": str(home), "PYTHONPATH": str(REPO / "src"), "CUDA_VISIBLE_DEVICES": "",
                "OLLAMA_HOST": "127.0.0.1:9", "http_proxy": dead, "https_proxy": dead, "HTTP_PROXY": dead,
                "HTTPS_PROXY": dead, "ALL_PROXY": dead, "all_proxy": dead, "no_proxy": "", "NO_PROXY": ""})
    return env


def run_check(name: str, entry, tree: Path, tmp_path: Path, data: dict) -> str | None:
    """None when the command's check form runs and exits 0 within CHECK_SECONDS in ``tree``; else why not."""
    if not isinstance(entry, dict) or not isinstance(entry.get("check"), str) or not entry["check"].strip():
        return f"{name}: no check form"
    form = fill(entry["check"], tree, data)
    left = sorted(keys_of(form) | {f"CMD:{c}" for c in cmds_of(form)})
    if left:
        return f"{name}: placeholders left in its check form after filling: {left}"
    started = time.monotonic()
    try:
        done = subprocess.run(["bash", "-c", form], cwd=tree, capture_output=True, text=True,
                              env=sealed_env(tmp_path), stdin=subprocess.DEVNULL, timeout=CHECK_SECONDS)
    except subprocess.TimeoutExpired:
        return f"{name}: its check {form!r} ran past {CHECK_SECONDS} s"
    took = time.monotonic() - started
    if done.returncode != 0:
        return (f"{name}: its check {form!r} exited {done.returncode}: "
                f"{(done.stderr or done.stdout).strip()[-300:]}")
    if took > CHECK_SECONDS:
        return f"{name}: its check took {took:.1f} s"
    return None


# --- the register ------------------------------------------------------------------------------------------------

def register_statuses() -> dict[str, str]:
    """``DEC-n -> the first word of its status line`` (``- **Status:** ACCEPTED (...)``), read at test time."""
    statuses: dict[str, str] = {}
    current = None
    for line in read(REGISTER).split("\n"):
        heading = re.match(r"^###\s+(DEC-\d+)\b", line)
        if heading:
            current = heading.group(1)
            continue
        if current:
            status = re.match(r"^\s*-\s*\*\*Status:\*\*\s*([A-Za-z_]+)", line)
            if status:
                statuses.setdefault(current, status.group(1).upper())
                current = None
            elif line.startswith("#"):
                current = None
    return statuses


# --- schemas -----------------------------------------------------------------------------------------------------

def schema_errors(schema_file: str, instance: dict) -> list[str]:
    """The validator's errors for ``instance`` against a kernel schema, ``common.schema.json`` resolved locally."""
    import jsonschema

    schema_path = SCHEMAS / schema_file
    schema = json.loads(read(schema_path))
    store = {}
    for other in SCHEMAS.glob("*.schema.json"):
        try:
            store[other.resolve().as_uri()] = json.loads(other.read_text(encoding="utf-8"))
        except ValueError:
            pass
    resolver = jsonschema.RefResolver(base_uri=schema_path.resolve().as_uri(), referrer=schema, store=store)
    validator = jsonschema.Draft202012Validator(schema, resolver=resolver)
    return [f"{'/'.join(map(str, error.absolute_path)) or '$'}: {error.message}"
            for error in validator.iter_errors(instance)]


def as_instance(front: dict) -> dict:
    """The front matter as JSON would hold it (dates as ISO text), as gov check's schema check writes it."""
    def iso(value):
        if isinstance(value, (datetime.date, datetime.time)):
            return value.isoformat()
        raise TypeError(type(value).__name__)
    return json.loads(json.dumps(front, default=iso))


def record_front(path: Path) -> dict | None:
    from gov.util import frontmatter

    try:
        return frontmatter.parse(path.read_text(encoding="utf-8"), rstrip=path.parts[-2] == ".tickets")
    except (frontmatter.FrontmatterError, OSError, UnicodeDecodeError):
        return None


def records_of(types: tuple[str, ...], folders: tuple[str, ...] = (".tickets", "docs")) -> list[tuple[str, dict]]:
    """(path, front matter) of every record of ``types`` in ``folders``, ``docs/imported`` left out as gov check's
    schema check leaves it out (DEC-844)."""
    found = []
    for folder in folders:
        base = REPO / folder
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            rel = path.relative_to(REPO).as_posix()
            if rel.startswith("docs/imported/"):
                continue
            front = record_front(path)
            if isinstance(front, dict) and front.get("type") in types:
                found.append((rel, front))
    return found
