"""Helpers for the W1-38 acceptance tests (rulesync adapters and .claude ownership).

Every test builds a temporary project under pytest's ``tmp_path``, copies
sources from the kernel template, and checks the generated output. Nothing is
written in this worktree.
"""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]

RULESYNC_BIN = Path(os.environ.get("RULESYNC_BIN", "/home/usain/.local/bin/rulesync"))
RULESYNC_VERSION = "24.0.0"
TOKEN_CHARS = 4
AGENTS_MD_TOKEN_LIMIT = 1500

TEMPLATE_RULESYNC_REL = "template/.rulesync"
KERNEL_ROLES_REL = "template/governance/kernel/roles"
KERNEL_HOOKS_REL = "template/governance/kernel/hooks"
KERNEL_SKILLS_REL = "template/governance/kernel/skills"
KERNEL_CHECKS_REL = "template/governance/kernel/checks"
SUPERPOWERS_REL = "template/governance/kernel/skills/superpowers"
CHECK_DECL_REL = "template/governance/kernel/checks/adapter-portability.yaml"

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

PORTABILITY_FAMILY = "adapter/model portability"
PORTABILITY_FAMILY_NORMALISED = "adapter-model-portability"
ALL_FEATURES = "rules,hooks,permissions,subagents,commands,skills"

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


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def build_project_from_template(project_dir: Path) -> None:
    """Copy template/.rulesync/ sources and kernel hooks into a temp project.

    Each file is copied individually (never a folder as a unit).
    """
    src_root = REPO_ROOT / TEMPLATE_RULESYNC_REL
    dst_root = project_dir / ".rulesync"
    for src_file in sorted(src_root.rglob("*")):
        if src_file.is_file():
            rel = src_file.relative_to(src_root)
            _copy_file(src_file, dst_root / rel)

    hooks_src = REPO_ROOT / KERNEL_HOOKS_REL
    hooks_dst = project_dir / "governance" / "kernel" / "hooks"
    for script_name in HOOK_SCRIPTS:
        src_file = hooks_src / script_name
        if src_file.is_file():
            _copy_file(src_file, hooks_dst / script_name)


def place_openspec_commands(project_dir: Path) -> list[str]:
    """Simulate ``openspec init``: place commands in .claude/commands/opsx/.

    These are NOT rulesync source files (DEC-074 Q7).
    """
    opsx_dir = project_dir / ".claude" / "commands" / "opsx"
    opsx_dir.mkdir(parents=True, exist_ok=True)
    names = []
    for cmd_name in ("propose", "close", "status"):
        fname = f"{cmd_name}.md"
        (opsx_dir / fname).write_text(
            f'---\ndescription: "OpenSpec {cmd_name} command"\n---\n\n'
            f"Run the openspec {cmd_name} workflow.\n",
            encoding="utf-8",
        )
        names.append(fname)
    return names


def write_rulesync_config(project_dir: Path, *, version: str = RULESYNC_VERSION) -> Path:
    path = project_dir / "rulesync.jsonc"
    path.write_text(json.dumps({"version": version}, indent=2), encoding="utf-8")
    return path


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


# ---------------------------------------------------------------------------
# Settings inspection
# ---------------------------------------------------------------------------

def load_settings(project_dir: Path) -> dict:
    path = project_dir / ".claude" / "settings.json"
    assert path.is_file(), f".claude/settings.json does not exist in {project_dir}"
    return json.loads(path.read_text(encoding="utf-8"))


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
# Check declaration
# ---------------------------------------------------------------------------

def load_check_declaration() -> dict | None:
    import yaml
    path = REPO_ROOT / CHECK_DECL_REL
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Portability check
# ---------------------------------------------------------------------------

def portability_module_exists() -> bool:
    adapters = REPO_ROOT / "src" / "gov" / "adapters"
    if not adapters.is_dir():
        return False
    return (adapters / "portability.py").is_file() or (adapters / "__main__.py").is_file()


def run_portability_check(
    project_dir: Path,
    *,
    env_override: dict[str, str] | None = None,
    timeout: int = 30,
) -> subprocess.CompletedProcess:
    env = {**os.environ}
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    if env_override:
        env.update(env_override)
    return subprocess.run(
        ["python3", "-m", "gov.adapters.portability"],
        capture_output=True, text=True, timeout=timeout,
        cwd=str(project_dir), env=env,
    )


# ---------------------------------------------------------------------------
# Kernel file readers
# ---------------------------------------------------------------------------

def read_kernel_role(role: str) -> str:
    path = REPO_ROOT / KERNEL_ROLES_REL / f"{role}.md"
    assert path.is_file(), f"{KERNEL_ROLES_REL}/{role}.md does not exist"
    return path.read_text(encoding="utf-8")


def read_kernel_skill_body(skill: str) -> str:
    path = REPO_ROOT / KERNEL_SKILLS_REL / skill / "SKILL.md"
    assert path.is_file(), f"{KERNEL_SKILLS_REL}/{skill}/SKILL.md does not exist"
    return body(path.read_text(encoding="utf-8"))


def write_mock_rulesync(project_dir: Path, script_body: str) -> Path:
    mock = project_dir / "mock-rulesync.sh"
    mock.write_text(f"#!/bin/bash\n{script_body}\n", encoding="utf-8")
    mock.chmod(0o755)
    return mock
