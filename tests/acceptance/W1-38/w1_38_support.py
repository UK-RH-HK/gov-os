"""Helpers for the W1-38 acceptance tests (rulesync adapters and .claude ownership).

Every test builds a temporary project under pytest's ``tmp_path``, populates a
``.rulesync/`` source tree, and runs ``rulesync generate`` there. Nothing is
written in this worktree, the main repository, or any other worktree.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

RULESYNC_BIN = Path(os.environ.get("RULESYNC_BIN", "/home/usain/.local/bin/rulesync"))
RULESYNC_VERSION = "24.0.0"
TOKEN_CHARS = 4
AGENTS_MD_TOKEN_LIMIT = 1500

ALL_FEATURES = "rules,hooks,permissions,subagents,commands,skills"

KERNEL_ROLES_REL = "template/governance/kernel/roles"
KERNEL_HOOKS_REL = "template/governance/kernel/hooks"
KERNEL_SKILLS_REL = "template/governance/kernel/skills"
KERNEL_CHECKS_REL = "template/governance/kernel/checks"
SUPERPOWERS_REL = "template/governance/kernel/skills/superpowers"

ROLE_NAMES = (
    "engineer",
    "independent-auditor",
    "independent-test-designer",
    "orchestrator",
    "product-spec",
    "research",
)

HOOK_NAMES = (
    "posttooluse",
    "precompact",
    "pretooluse",
    "sessionstart",
    "stop",
    "subagentstop",
)

SUPERPOWERS_SKILLS = (
    "systematic-debugging",
    "test-driven-development",
    "verification-before-completion",
)

CHECK_DECL_PATTERN = re.compile(r"^adapter-portability")
PORTABILITY_FAMILY = "adapter/model portability"
PORTABILITY_FAMILY_NORMALISED = "adapter-model-portability"


class Missing(AssertionError):
    """A required file or directory is missing."""


def _tokens(text: str) -> int:
    """Ceiling division: ceil(len(text) / TOKEN_CHARS)."""
    return -(-len(text) // TOKEN_CHARS)


def rulesync_version() -> str | None:
    """Return the installed rulesync version string, or None if not found."""
    if not RULESYNC_BIN.is_file():
        return None
    result = subprocess.run(
        [str(RULESYNC_BIN), "--version"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def run_rulesync_generate(
    project_dir: Path,
    *,
    targets: str = "claudecode",
    features: str = ALL_FEATURES,
    extra_args: tuple[str, ...] = (),
    input_roots: tuple[str, ...] | None = None,
) -> subprocess.CompletedProcess:
    """Run ``rulesync generate`` inside *project_dir*, return the result."""
    cmd = [str(RULESYNC_BIN), "generate",
           "--targets", targets, "--features", features]
    if input_roots is not None:
        cmd.extend(["--input-roots", *input_roots])
    cmd.extend(extra_args)
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=30, cwd=str(project_dir),
    )


def run_rulesync_generate_check(
    project_dir: Path,
    *,
    targets: str = "claudecode",
    features: str = ALL_FEATURES,
    input_roots: tuple[str, ...] | None = None,
) -> subprocess.CompletedProcess:
    """Run ``rulesync generate --check`` and return the result."""
    return run_rulesync_generate(
        project_dir, targets=targets, features=features,
        extra_args=("--check",), input_roots=input_roots,
    )


def run_rulesync_generate_delete(
    project_dir: Path,
    *,
    targets: str = "claudecode",
    features: str = ALL_FEATURES,
    input_roots: tuple[str, ...] | None = None,
) -> subprocess.CompletedProcess:
    """Run ``rulesync generate --delete`` and return the result."""
    return run_rulesync_generate(
        project_dir, targets=targets, features=features,
        extra_args=("--delete",), input_roots=input_roots,
    )


def build_minimal_rulesync_tree(project_dir: Path) -> None:
    """Create a minimal ``.rulesync/`` tree in *project_dir*.

    The tree has:
    - A root rule file
    - A non-root rule file (simulating a kernel role)
    - hooks.jsonc with hooks pointing to scripts under governance/kernel/hooks/
    - permissions.jsonc with deny rules
    - A skill with a SKILL.md (with valid frontmatter)
    - A subagent definition
    """
    rs = project_dir / ".rulesync"
    rs.mkdir(parents=True, exist_ok=True)

    # Root rule
    rules = rs / "rules"
    rules.mkdir(exist_ok=True)
    (rules / "overview.md").write_text(
        '---\nroot: true\ntargets: ["claudecode", "agentsmd"]\n'
        'description: "Gov OS project"\n---\n\n# Gov OS\n\nMinimal test project.\n',
        encoding="utf-8",
    )
    (rules / "guard.md").write_text(
        '---\nroot: false\ntargets: ["claudecode", "agentsmd"]\n'
        'description: "Guard rules"\n---\n\n## Guard\n\nThe guard checks every tool call.\n',
        encoding="utf-8",
    )

    # Hooks
    hook_script_dir = project_dir / "governance" / "kernel" / "hooks"
    hook_script_dir.mkdir(parents=True, exist_ok=True)
    hooks_map = {}
    for event, script_name in [
        ("preToolUse", "pretooluse.py"),
        ("postToolUse", "posttooluse.py"),
        ("sessionStart", "sessionstart.py"),
        ("stop", "stop.py"),
        ("preCompact", "precompact.py"),
        ("subagentStop", "subagentstop.py"),
    ]:
        script_path = hook_script_dir / script_name
        script_path.write_text(
            f"#!/usr/bin/env python3\n# stub for {event}\n",
            encoding="utf-8",
        )
        script_path.chmod(0o755)
        hooks_map[event] = [
            {"type": "command",
             "command": f"./governance/kernel/hooks/{script_name}"}
        ]

    (rs / "hooks.jsonc").write_text(
        json.dumps({"version": 1, "hooks": hooks_map}, indent=2),
        encoding="utf-8",
    )

    # Permissions (deny rules)
    (rs / "permissions.jsonc").write_text(
        json.dumps({
            "permission": {
                "edit": {
                    ".tickets/**": "deny",
                    "tests/acceptance/**": "deny",
                },
                "bash": {
                    "npm install*": "deny",
                    "pip install*": "deny",
                },
            },
        }, indent=2),
        encoding="utf-8",
    )

    # Skill (with required name in frontmatter)
    skill_dir = rs / "skills" / "planning"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        '---\nname: planning\ntargets: ["claudecode"]\n'
        'description: "Planning skill"\n---\n\n# Planning\n\nHelps plan implementations.\n',
        encoding="utf-8",
    )

    # Subagent
    subagents = rs / "subagents"
    subagents.mkdir(exist_ok=True)
    (subagents / "engineer.md").write_text(
        '---\nname: engineer\ntargets: ["claudecode"]\n'
        'description: "Engineer role"\n'
        "claudecode:\n  model: sonnet\n"
        '  tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]\n'
        "---\n\nYou are an engineer.\n",
        encoding="utf-8",
    )


def add_openspec_commands(project_dir: Path) -> list[str]:
    """Add OpenSpec command files to ``.rulesync/commands/`` and return their names."""
    commands_dir = project_dir / ".rulesync" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    names = []
    for name in ("propose.md", "close.md"):
        (commands_dir / name).write_text(
            f'---\ndescription: "OpenSpec {name.replace(".md", "")} command"\n'
            f'targets: ["claudecode"]\n---\n\n'
            f'Run the openspec {name.replace(".md", "")} workflow.\n',
            encoding="utf-8",
        )
        names.append(name)
    return names


def add_vendored_skills(project_dir: Path) -> list[str]:
    """Add the three vendored superpowers skills to ``.rulesync/skills/``.

    Returns folder names.
    """
    skills_dir = project_dir / ".rulesync" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    folders = []
    for skill_name in SUPERPOWERS_SKILLS:
        skill_dir = skills_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f'---\nname: {skill_name}\ntargets: ["claudecode"]\n'
            f'description: "{skill_name} skill"\n---\n\n'
            f"# {skill_name}\n\nVendored superpowers skill.\n",
            encoding="utf-8",
        )
        folders.append(skill_name)
    return folders


def init_git(project_dir: Path) -> None:
    """Initialize a git repo in *project_dir* for rulesync to work."""
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


def load_generated_settings(project_dir: Path) -> dict:
    """Load ``.claude/settings.json`` from the generated project."""
    settings_path = project_dir / ".claude" / "settings.json"
    if not settings_path.is_file():
        raise Missing(f".claude/settings.json does not exist in {project_dir}")
    return json.loads(settings_path.read_text(encoding="utf-8"))


def extract_hook_commands(settings: dict) -> list[str]:
    """Extract all hook command paths from a Claude Code settings dict.

    Claude Code hooks use a nested structure:
    ``{event: [{hooks: [{type, command}]}]}``
    """
    commands = []
    hooks = settings.get("hooks", {})
    for _event, matchers in hooks.items():
        if not isinstance(matchers, list):
            continue
        for matcher in matchers:
            if not isinstance(matcher, dict):
                continue
            inner = matcher.get("hooks", [])
            if not isinstance(inner, list):
                continue
            for entry in inner:
                if isinstance(entry, dict) and "command" in entry:
                    cmd = entry["command"]
                    cmd = cmd.replace('"$CLAUDE_PROJECT_DIR"/', "./")
                    cmd = cmd.replace("$CLAUDE_PROJECT_DIR/", "./")
                    parts = cmd.split()
                    if parts:
                        path_part = parts[0]
                        if path_part.startswith(("./", "../")):
                            commands.append(path_part)
    return commands


def normalise_family(name: str) -> str:
    """Normalise a check family name the way gov.check.runner does."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_check_declarations(checks_dir: Path) -> list[dict]:
    """Load all YAML check declarations from *checks_dir*."""
    import yaml
    declarations = []
    if not checks_dir.is_dir():
        return declarations
    for path in sorted(checks_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            declarations.append(data)
    return declarations


def find_adapter_portability_check(checks_dir: Path) -> dict | None:
    """Find the adapter-portability check declaration, if any."""
    for decl in load_check_declarations(checks_dir):
        if decl.get("id", "").startswith("adapter-portability"):
            return decl
        family = decl.get("family", "")
        if normalise_family(family) == PORTABILITY_FAMILY_NORMALISED:
            return decl
    return None


def portability_module_exists() -> bool:
    """Return True if ``src/gov/adapters/portability`` is importable."""
    adapters_dir = REPO_ROOT / "src" / "gov" / "adapters"
    if not adapters_dir.is_dir():
        return False
    init_file = adapters_dir / "__init__.py"
    if not init_file.is_file():
        return False
    portability = adapters_dir / "portability.py"
    main = adapters_dir / "__main__.py"
    return portability.is_file() or main.is_file()


def run_portability_check(
    project_dir: Path,
    *,
    env_override: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Run the portability check command from the project directory."""
    env = {**os.environ}
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    if env_override:
        env.update(env_override)
    return subprocess.run(
        ["python3", "-m", "gov.adapters.portability"],
        capture_output=True, text=True, timeout=30,
        cwd=str(project_dir), env=env,
    )
