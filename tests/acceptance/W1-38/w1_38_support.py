"""Helpers for the W1-38 acceptance tests (rulesync adapters and .claude ownership).

Every test builds a temporary project under pytest's ``tmp_path``, copies
sources from the kernel template, and checks the generated output. Nothing is
written in this worktree.
"""

from __future__ import annotations

import math
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_W1_07 = str(_HERE.parent / "W1-07")
if _W1_07 not in sys.path:
    sys.path.insert(0, _W1_07)

import w1_07_support as cli_support  # noqa: E402  (the gov command line, as W1-26's suite runs it)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]

RULESYNC_BIN = Path(os.environ.get("RULESYNC_BIN", "/home/usain/.local/bin/rulesync"))
TOKEN_CHARS = 4
AGENTS_MD_TOKEN_LIMIT = 1500

TEMPLATE_RULESYNC_REL = "template/.rulesync"
KERNEL_ROLES_REL = "template/governance/kernel/roles"
KERNEL_HOOKS_REL = "template/governance/kernel/hooks"
KERNEL_SKILLS_REL = "template/governance/kernel/skills"
SUPERPOWERS_REL = "template/governance/kernel/skills/superpowers"
CHECK_DECL_REL = "template/governance/kernel/checks/adapter-portability.yaml"
TOOL_REGISTRY_REL = "governance/project/tool-registry.yaml"   # DEC-127: per-repository project data

# Where an adopted project holds the kernel (ADR-0002 section 5) and where
# ``gov check`` reads check declarations (DEC-186).
PROJECT_KERNEL_REL = "governance/kernel"
PROJECT_CHECKS_REL = cli_support.CHECKS_REL

# The commands ``openspec init --tools claude`` of the registered OpenSpec
# version writes under ``.claude/commands/opsx/`` with its default profile.
OPENSPEC_COMMANDS = ("apply", "archive", "explore", "propose", "sync", "update")
OPSX_REL = ".claude/commands/opsx"

# The skills the same command writes under ``.claude/skills/`` (DEC-468).
OPENSPEC_SKILLS = (
    "openspec-apply-change",
    "openspec-archive-change",
    "openspec-explore",
    "openspec-propose",
    "openspec-sync-specs",
    "openspec-update-change",
)
OPENSPEC_SKILL_PREFIX = "openspec-"
SKILLS_REL = ".claude/skills"

ROLE_NAMES = (
    "engineer",
    "independent-auditor",
    "independent-test-designer",
    "orchestrator",
    "product-spec",
    "research",
)

HOOK_SCRIPTS = (
    "posttooluse.py",
    "precompact.py",
    "pretooluse.py",
    "sessionstart.py",
    "stop.py",
    "subagentstop.py",
)

KERNEL_METHOD_SKILLS = (
    "adopt",
    "audit",
    "change",
    "checkpoint",
    "discovery",
    "planning",
    "retrieval",
    "test-design",
)

SUPERPOWERS_SKILLS = (
    "systematic-debugging",
    "test-driven-development",
    "verification-before-completion",
)

# Round 4. ADR-0002 section 5 and DEC-074 Q7: rulesync owns ``.claude/``, and
# OpenSpec's files and the vendored skills are rulesync sources. Every file
# under these three folders therefore has a rulesync source.
GENERATED_FOLDERS = (".claude/agents", ".claude/skills", ".claude/commands")
SETTINGS_REL = ".claude/settings.json"
# Paths under ``.claude/`` the sources give to another owner: the per-user
# settings Claude Code writes (DEC-063) and the gitignored worktrees (DEC-050).
OTHER_OWNERS = (".claude/settings.local.json", ".claude/worktrees/by-hand/.claude/agents/by-hand.md")

# The Claude Code tool names a kernel role's Tools field is read for.
CLAUDE_CODE_TOOLS = (
    "Agent", "Bash", "Edit", "Glob", "Grep", "NotebookEdit", "Read", "Skill",
    "Task", "TodoWrite", "WebFetch", "WebSearch", "Write",
)

PORTABILITY_FAMILY = "adapter/model portability"
PORTABILITY_FAMILY_NORMALISED = "adapter-model-portability"
ALL_FEATURES = "rules,hooks,permissions,subagents,commands,skills"
RED, GREEN = "RED", "GREEN"

# W1-33 labelled-field regex
_LABELLED = re.compile(r"^[-*]\s+\*\*(?P<label>[^*]+?):?\*\*:?\s*(?P<rest>.*)$")


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def tokens(text: str) -> int:
    return math.ceil(len(text) / TOKEN_CHARS)


def body(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0:
            rest = text[end + 4:]
            return rest.split("\n", 1)[1] if "\n" in rest else ""
    return text


def frontmatter(text: str) -> dict:
    """The YAML frontmatter of a Markdown file, as a mapping."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    data = yaml.safe_load(text[3:end])
    return data if isinstance(data, dict) else {}


def generated_body(text: str) -> str:
    """The body as rulesync writes it: the blank lines between the closing
    ``---`` of the frontmatter and the first line of the body are dropped.

    This is the one difference the suite tolerates between a source file and
    the file generated from it; everything after it is compared byte for byte.
    """
    return body(text).lstrip("\n")


def normalise(text: str) -> str:
    return " ".join(text.split())


def parse_fields(text: str) -> dict[str, str]:
    """Parse labelled fields from markdown (W1-33 whitespace-collapsed comparison).

    Returns ``{label_lower: whitespace_collapsed_value}``.
    """
    lines = body(text).splitlines()
    spans: list[tuple[str, str]] = []
    start: int | None = None
    label: str | None = None

    def close(end: int) -> None:
        nonlocal start, label
        if start is not None:
            first = _LABELLED.match(lines[start]).group("rest")
            value = normalise("\n".join([first, *lines[start + 1:end]]))
            spans.append((label, value))

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
    return {lab.lower(): val for lab, val in spans}


def normalise_family(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# ---------------------------------------------------------------------------
# Rulesync binary
# ---------------------------------------------------------------------------

def rulesync_version() -> str | None:
    if not RULESYNC_BIN.is_file():
        return None
    try:
        result = subprocess.run(
            [str(RULESYNC_BIN), "--version"],
            capture_output=True, text=True, timeout=10,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def write_mock_rulesync(folder: Path, script_body: str) -> Path:
    """A stand-in for the rulesync *binary* (never for a source text), written
    outside the project. ``$REAL`` is the installed rulesync."""
    folder.mkdir(parents=True, exist_ok=True)
    mock = folder / "rulesync"
    mock.write_text(
        f"#!/bin/bash\nREAL={shlex.quote(str(RULESYNC_BIN))}\n{script_body}\n",
        encoding="utf-8",
    )
    mock.chmod(0o755)
    return mock


# ---------------------------------------------------------------------------
# The tool registry (DEC-127): where a project records the versions it expects
# ---------------------------------------------------------------------------

def registry_entry(name: str) -> dict:
    """The entry of one tool in this repository's tool registry."""
    data = yaml.safe_load((REPO_ROOT / TOOL_REGISTRY_REL).read_text(encoding="utf-8"))
    for entry in data.get("tools", []):
        if entry.get("name") == name:
            return dict(entry)
    raise AssertionError(f"{TOOL_REGISTRY_REL} has no entry for {name}")


def registered_rulesync_version() -> str:
    return str(registry_entry("rulesync")["version"])


def write_tool_registry(
    project_dir: Path,
    *,
    names: tuple[str, ...] = ("rulesync",),
    rulesync_version: str | None = None,
) -> Path:
    """Write the project's tool registry from this repository's own entries.

    Nothing is invented: each entry is the registered one. ``rulesync_version``
    replaces the version of the rulesync entry, for the case where the project
    expects another version than the installed one.
    """
    entries = []
    for name in names:
        entry = registry_entry(name)
        if name == "rulesync" and rulesync_version is not None:
            entry["version"] = rulesync_version
        entries.append(entry)
    path = project_dir / TOOL_REGISTRY_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"tools": entries}, sort_keys=False), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Project building
# ---------------------------------------------------------------------------

def init_git(project_dir: Path) -> None:
    subprocess.run(
        ["git", "init", "--initial-branch=main"],
        cwd=str(project_dir), capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "-C", str(project_dir), "config", "user.email", "test@test.local"],
        capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "-C", str(project_dir), "config", "user.name", "Test"],
        capture_output=True, check=True,
    )


def commit_all(project_dir: Path, message: str = "fixture") -> None:
    subprocess.run(["git", "-C", str(project_dir), "add", "-A"], capture_output=True, check=True)
    subprocess.run(
        ["git", "-C", str(project_dir), "commit", "-q", "--allow-empty", "-m", message],
        capture_output=True, check=True,
    )


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_files(src_root: Path, dst_root: Path) -> None:
    """Copy each file individually (never a folder as a unit)."""
    for src_file in sorted(src_root.rglob("*")):
        if src_file.is_file():
            _copy_file(src_file, dst_root / src_file.relative_to(src_root))


def build_project_from_template(project_dir: Path) -> None:
    """Build an adopted project in a temporary folder, file by file.

    - ``.rulesync/`` from ``template/.rulesync/``;
    - ``governance/kernel/{hooks,roles,skills}`` from the kernel template
      (ADR-0002 section 5: the kernel of a product repository);
    - ``governance/project/tool-registry.yaml`` with this repository's
      registered rulesync entry (DEC-127), where a project records the
      rulesync version it expects;
    - the declaration of the check, at the path ``gov check`` reads (DEC-186).
    """
    _copy_files(REPO_ROOT / TEMPLATE_RULESYNC_REL, project_dir / ".rulesync")

    hooks_src = REPO_ROOT / KERNEL_HOOKS_REL
    for script_name in HOOK_SCRIPTS:
        src_file = hooks_src / script_name
        if src_file.is_file():
            _copy_file(src_file, project_dir / PROJECT_KERNEL_REL / "hooks" / script_name)

    _copy_files(REPO_ROOT / KERNEL_ROLES_REL, project_dir / PROJECT_KERNEL_REL / "roles")
    _copy_files(REPO_ROOT / KERNEL_SKILLS_REL, project_dir / PROJECT_KERNEL_REL / "skills")
    write_tool_registry(project_dir)

    decl = REPO_ROOT / CHECK_DECL_REL
    if decl.is_file():
        _copy_file(decl, project_dir / PROJECT_CHECKS_REL / decl.name)


def project_files(project_dir: Path) -> list[str]:
    """Every file of the project, as a path relative to it (``.git`` left out)."""
    return sorted(
        str(path.relative_to(project_dir)) for path in project_dir.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(project_dir).parts
    )


def named_files(project_dir: Path, text: str) -> set[str]:
    """The files of the project that ``text`` names, by relative or absolute path."""
    for root in {str(project_dir), str(project_dir.resolve())}:
        text = text.replace(root + "/", "")
    return {
        rel for rel in project_files(project_dir)
        if re.search(r"(?<![\w./-])" + re.escape(rel) + r"(?![\w/-])", text)
    }


def root_rule_body(project_dir: Path) -> str:
    """The body of the one rule source marked ``root: true``."""
    roots = [
        path for path in sorted((project_dir / ".rulesync" / "rules").glob("*.md"))
        if frontmatter(path.read_text(encoding="utf-8")).get("root") is True
    ]
    assert len(roots) == 1, (
        f".rulesync/rules/ holds {len(roots)} rules marked root: true; one is expected"
    )
    return generated_body(roots[0].read_text(encoding="utf-8"))


def change_first_labelled_field(path: Path) -> None:
    """Change the text of the first labelled field of a role file."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    for index, line in enumerate(lines):
        if _LABELLED.match(line.rstrip("\n")):
            lines[index] = line.rstrip("\n") + " A sentence added by the case.\n"
            path.write_text("".join(lines), encoding="utf-8")
            return
    raise AssertionError(f"{path} has no labelled field to change")


def append_line(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(text.rstrip("\n") + "\n\nA line added by the case.\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# A role's tools: the kernel role's Tools field and the adapter source
# ---------------------------------------------------------------------------

def kernel_role_tools(text: str) -> set[str]:
    """The Claude Code tool names the Tools field of a kernel role file names
    (whole words, case as written)."""
    field = parse_fields(text).get("tools")
    assert field, "the kernel role file has no Tools field"
    return {word for word in re.findall(r"[A-Za-z]+", field) if word in CLAUDE_CODE_TOOLS}


def source_role_tools(text: str) -> list[str] | None:
    """``claudecode.tools`` of a role's rulesync source, or None when the
    source states no tools (the role would then inherit every tool)."""
    tools = (frontmatter(text).get("claudecode") or {}).get("tools")
    return [str(tool) for tool in tools] if isinstance(tools, list) else None


def write_source_role_tools(path: Path, tools: list[str]) -> None:
    """Replace ``claudecode.tools`` in a role's rulesync source. Every other
    frontmatter value and every byte of the body stay as they were."""
    text = path.read_text(encoding="utf-8")
    data = frontmatter(text)
    assert isinstance(data.get("claudecode"), dict) and "tools" in data["claudecode"], (
        f"{path.name} states no claudecode.tools"
    )
    data["claudecode"]["tools"] = list(tools)
    head = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000)
    changed = f"---\n{head}---\n{body(text)}"
    assert body(changed) == body(text) and frontmatter(changed) == data
    path.write_text(changed, encoding="utf-8")


# ---------------------------------------------------------------------------
# What OpenSpec ships
# ---------------------------------------------------------------------------

def openspec_environment(home: Path) -> tuple[str, dict]:
    """The registered ``openspec`` and the environment to run it in.

    The registry's own note: tools under the registered Node are not on the
    default PATH; they run with that Node's ``bin`` folder first on PATH.
    """
    node_bin = Path.home() / ".nvm" / "versions" / "node" / registry_entry("node")["version"] / "bin"
    path = f"{node_bin}:{os.environ.get('PATH', '/usr/bin:/bin')}"
    binary = os.environ.get("OPENSPEC_BIN") or shutil.which("openspec", path=path)
    assert binary, (
        "openspec is not installed: the OpenSpec command cases compare against what the "
        f"registered OpenSpec ({registry_entry('openspec')['version']}) writes"
    )
    env = {
        "PATH": path, "HOME": str(home), "XDG_CONFIG_HOME": str(home / ".config"),
        "LC_ALL": "C.UTF-8", "DO_NOT_TRACK": "1", "OPENSPEC_TELEMETRY": "0", "CI": "1",
    }
    return binary, env


def openspec_init(work: Path) -> Path:
    """Run ``openspec init --tools claude`` of the registered version in a
    fresh folder under ``work`` and return that folder."""
    home = work / "home"
    target = work / "openspec-project"
    home.mkdir(parents=True)
    target.mkdir(parents=True)
    binary, env = openspec_environment(home)
    version = subprocess.run(
        [binary, "--version"], capture_output=True, text=True,
        env=env, timeout=60, stdin=subprocess.DEVNULL,
    )
    expected = str(registry_entry("openspec")["version"])
    assert version.returncode == 0 and version.stdout.strip() == expected, (
        f"the installed openspec reports {version.stdout.strip()!r}; the registry expects {expected}"
    )
    done = subprocess.run(
        [binary, "init", "--tools", "claude", "."], capture_output=True, text=True,
        env=env, cwd=str(target), timeout=120, stdin=subprocess.DEVNULL,
    )
    assert done.returncode == 0, f"openspec init failed: {done.stdout}\n{done.stderr}"
    return target


def openspec_shipped_commands(target: Path) -> dict[str, str]:
    """The command files ``openspec init`` wrote in ``target``: ``{name: text}``
    for ``.claude/commands/opsx/<name>.md``."""
    shipped = {
        path.stem: path.read_text(encoding="utf-8")
        for path in sorted((target / OPSX_REL).glob("*.md"))
    }
    assert set(shipped) == set(OPENSPEC_COMMANDS), (
        f"openspec init wrote the commands {sorted(shipped)}; "
        f"this suite lists {sorted(OPENSPEC_COMMANDS)}"
    )
    return shipped


def openspec_shipped_skills(target: Path) -> dict[str, dict[str, str]]:
    """The skills ``openspec init`` wrote in ``target``:
    ``{skill: {path inside the skill folder: text}}`` for ``.claude/skills/<skill>/``."""
    shipped = {
        folder.name: {
            str(path.relative_to(folder)): path.read_text(encoding="utf-8")
            for path in sorted(folder.rglob("*")) if path.is_file()
        }
        for folder in sorted((target / SKILLS_REL).iterdir()) if folder.is_dir()
    }
    assert set(shipped) == set(OPENSPEC_SKILLS), (
        f"openspec init wrote the skills {sorted(shipped)}; "
        f"this suite lists {sorted(OPENSPEC_SKILLS)}"
    )
    return shipped


def differing_openspec_skill_files(project_dir: Path, skill: str, shipped: dict[str, str]) -> list[str]:
    """The files of one skill OpenSpec ships that the project does not hold as
    shipped under ``.claude/skills/<skill>/``. SKILL.md is compared by body
    (byte for byte) and by frontmatter (as a mapping); any other file by text."""
    differing = []
    for rel, text in sorted(shipped.items()):
        path = project_dir / SKILLS_REL / skill / rel
        if not path.is_file():
            differing.append(f"{rel}: not there")
            continue
        found = path.read_text(encoding="utf-8")
        if Path(rel).name != "SKILL.md":
            if found != text:
                differing.append(f"{rel}: differs")
        elif generated_body(found) != generated_body(text):
            differing.append(f"{rel}: body differs")
        elif frontmatter(found) != frontmatter(text):
            differing.append(f"{rel}: frontmatter differs")
    return differing


# ---------------------------------------------------------------------------
# Rulesync commands
# ---------------------------------------------------------------------------

def run_rulesync_generate(
    project_dir: Path,
    *,
    targets: str = "claudecode,agentsmd",
    features: str = ALL_FEATURES,
    extra_args: tuple[str, ...] = (),
    input_roots: tuple[str, ...] | None = None,
) -> subprocess.CompletedProcess:
    cmd = [str(RULESYNC_BIN), "generate",
           "--targets", targets, "--features", features]
    if input_roots is not None:
        cmd.extend(["--input-roots", *input_roots])
    cmd.extend(extra_args)
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=30, cwd=str(project_dir),
    )


def run_rulesync_check(
    project_dir: Path,
    *,
    targets: str = "claudecode,agentsmd",
    features: str = ALL_FEATURES,
    input_roots: tuple[str, ...] | None = None,
) -> subprocess.CompletedProcess:
    return run_rulesync_generate(
        project_dir, targets=targets, features=features,
        extra_args=("--check",), input_roots=input_roots,
    )


def run_rulesync_delete(
    project_dir: Path,
    *,
    targets: str = "claudecode,agentsmd",
    features: str = ALL_FEATURES,
    input_roots: tuple[str, ...] | None = None,
) -> subprocess.CompletedProcess:
    return run_rulesync_generate(
        project_dir, targets=targets, features=features,
        extra_args=("--delete",), input_roots=input_roots,
    )


def regenerate(project_dir: Path) -> None:
    """Generate again after a source change, so rulesync's own comparison is clean."""
    result = run_rulesync_generate(project_dir)
    assert result.returncode == 0, f"rulesync generate failed: {result.stderr}"
    check = run_rulesync_check(project_dir)
    assert check.returncode == 0, f"rulesync generate --check is not clean: {check.stdout}"


# ---------------------------------------------------------------------------
# Settings inspection
# ---------------------------------------------------------------------------

def load_settings(project_dir: Path) -> dict:
    import json
    path = project_dir / ".claude" / "settings.json"
    assert path.is_file(), f".claude/settings.json does not exist in {project_dir}"
    return json.loads(path.read_text(encoding="utf-8"))


def edit_settings(project_dir: Path, change) -> None:
    """Apply ``change`` to the parsed ``.claude/settings.json`` and write it
    back in the form rulesync writes it, so that the change is the only
    difference from the generated file."""
    import json
    path = project_dir / SETTINGS_REL
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)

    def dump(value: dict) -> str:
        return json.dumps(value, indent=2, ensure_ascii=False) + "\n"

    assert dump(data) == text, (
        f"{SETTINGS_REL} is not written as two-space JSON with a final newline: "
        f"writing it back would itself be a change"
    )
    before = dump(data)
    change(data)
    assert dump(data) != before, "the case changed nothing in the settings"
    path.write_text(dump(data), encoding="utf-8")


def _find_commands_recursive(obj: object) -> list[str]:
    commands: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "command" and isinstance(value, str):
                commands.append(value)
            else:
                commands.extend(_find_commands_recursive(value))
    elif isinstance(obj, list):
        for item in obj:
            commands.extend(_find_commands_recursive(item))
    return commands


def extract_hook_script_paths(settings: dict) -> list[str]:
    """Extract script file paths from hook commands in settings.

    Returns relative paths (e.g. ``governance/kernel/hooks/pretooluse.py``).
    """
    hooks = settings.get("hooks", {})
    commands = _find_commands_recursive(hooks)
    paths: list[str] = []
    for cmd in commands:
        normalized = cmd.replace('"$CLAUDE_PROJECT_DIR"/', "")
        normalized = normalized.replace("$CLAUDE_PROJECT_DIR/", "")
        for token in normalized.split():
            token = token.strip("'\"")
            if token.endswith(".py") and "/" in token and not token.startswith("-"):
                paths.append(token.lstrip("./"))
    return paths


# ---------------------------------------------------------------------------
# The adapter/model-portability check
# ---------------------------------------------------------------------------

def declared_command() -> list[str]:
    """The command of the check this ticket declares, from its declaration."""
    path = REPO_ROOT / CHECK_DECL_REL
    assert path.is_file(), (
        f"{CHECK_DECL_REL} does not exist: the adapter/model portability check is not declared"
    )
    return shlex.split(yaml.safe_load(path.read_text(encoding="utf-8"))["command"])


def run_portability_check(
    project_dir: Path,
    *,
    env_override: dict[str, str] | None = None,
    timeout: int = 60,
) -> subprocess.CompletedProcess:
    """Run the declared command in the project, as ``gov check`` does."""
    env = {**os.environ}
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    env.pop("RULESYNC_EXPECTED_VERSION", None)   # the expected version is the project's, never the caller's
    if env_override:
        env.update(env_override)
    return subprocess.run(
        declared_command(),
        capture_output=True, text=True, timeout=timeout,
        cwd=str(project_dir), env=env, stdin=subprocess.DEVNULL,
    )


def output_of(result) -> str:
    return result.stdout + result.stderr


def run_gov(project_dir: Path, sandbox, *args: str):
    """Commit the project and run ``gov <args>`` in it with this worktree's code."""
    commit_all(project_dir)
    return cli_support.run_gov_with_code(REPO_ROOT, project_dir, sandbox, *args)


def check_result(run) -> dict:
    """The result of ``gov check --json``: under ``result``, or under
    ``error.details`` when a hard-block check failed (API-0002)."""
    envelope = run.envelope()
    result = envelope.get("result") or (envelope.get("error") or {}).get("details") or {}
    assert "checks" in result and "families" in result, (
        f"gov check gave no per-check and per-family result\n{run.describe()}"
    )
    return result


def listed_portability_checks(run) -> list[dict]:
    """The checks ``gov check --list --json`` lists under the family."""
    envelope = run.envelope()
    assert envelope.get("ok") is True, run.describe()
    return [
        record for record in cli_support.find_records(envelope["result"])
        if normalise_family(str(record.get("family", ""))) == PORTABILITY_FAMILY_NORMALISED
    ]


def portability_entries(result: dict) -> tuple[dict, dict]:
    """``(check entry, family entry)`` of the adapter/model-portability family."""
    checks = [
        entry for entry in result["checks"] if isinstance(entry, dict)
        and normalise_family(str(entry.get("family", ""))) == PORTABILITY_FAMILY_NORMALISED
    ]
    assert len(checks) == 1, (
        f"gov check ran {len(checks)} checks of the family {PORTABILITY_FAMILY!r}; one is expected"
    )
    families = result["families"]
    if isinstance(families, list):
        families = {entry["family"]: entry for entry in families}
    family = [
        entry for name, entry in families.items()
        if normalise_family(name) == PORTABILITY_FAMILY_NORMALISED
    ]
    assert len(family) == 1, f"gov check names no family {PORTABILITY_FAMILY!r}: {sorted(families)}"
    return checks[0], family[0] if isinstance(family[0], dict) else {"status": family[0]}


# ---------------------------------------------------------------------------
# Kernel file readers
# ---------------------------------------------------------------------------

def read_kernel_role(role: str) -> str:
    path = REPO_ROOT / KERNEL_ROLES_REL / f"{role}.md"
    assert path.is_file(), f"{KERNEL_ROLES_REL}/{role}.md does not exist"
    return path.read_text(encoding="utf-8")


def read_kernel_skill(skill: str) -> str:
    path = REPO_ROOT / KERNEL_SKILLS_REL / skill / "SKILL.md"
    assert path.is_file(), f"{KERNEL_SKILLS_REL}/{skill}/SKILL.md does not exist"
    return path.read_text(encoding="utf-8")
