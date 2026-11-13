"""Helpers of the W2-120 acceptance tests: a planted project, the skills check run as a process, and file-and-key reading.

Every case plants a small project in ``tmp_path`` and runs the validator as a process with that project as the working
folder, the way ``gov check`` runs a skill-regression check file (``command:`` read from the check file, run from the
project's root). The code judged is the ``src`` of the repository this folder lies in; so merged into the ticket's
worktree the cases judge that worktree's validator.

The switch (README, "Checking the checks"): ``W2_120_VALIDATOR_MODULE`` names the module run as ``python3 -m <module>``
(default: the real ``gov.check.skill_validator``) and ``W2_120_STANDIN_DIR`` a folder put first on ``PYTHONPATH``. They
exist so the designer can show the cases bite against a stand-in; unset, nothing here changes.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "src"
CHECKS = REPO / "template" / "governance" / "kernel" / "checks"
CHECK_IDS = ("skill-regression-a", "skill-regression-b1", "skill-regression-orchestration")

MODULE = os.environ.get("W2_120_VALIDATOR_MODULE") or "gov.check.skill_validator"
STANDIN_DIR = os.environ.get("W2_120_STANDIN_DIR") or ""
REAL = MODULE == "gov.check.skill_validator" and not STANDIN_DIR

KERNEL = "template/governance/kernel/skills"
RULESYNC = ".rulesync/skills"
TEMPLATE_RULESYNC = "template/.rulesync/skills"
CLAUDE = ".claude/skills"
GENERATED = (RULESYNC, TEMPLATE_RULESYNC, CLAUDE)
VENDORED_CODE = "SKILL_VENDORED_KEY"

# I2: the permission keys the ticket lists
PERMISSION_KEYS = {
    "allowed-tools": "Bash(git:*)",
    "permissions": ["read", "write"],
    "paths": ["src/**"],
    "sandbox": True,
    "network": "none",
    "model": "opus",
    "effort": "high",
}

BODY = "A short method for a planted skill. It states steps and grants nothing.\n"
DESCRIPTION = "Method for a planted skill, used when an acceptance test needs one."


# --- the planted project ----------------------------------------------------------------------------------------------

def kernel_front(name: str) -> dict:
    """The skill template's closed list: name, version, description, output and metadata.version."""
    return {"name": name, "version": "1.0.0", "description": DESCRIPTION, "output": "none",
            "metadata": {"version": "1.0.0"}}


def rulesync_front(name: str) -> dict:
    """A rulesync source copy as the live tree holds it: name, version, metadata, description (no output)."""
    return {"name": name, "version": "1.0.0", "metadata": {"version": "1.0.0"}, "description": DESCRIPTION}


def claude_front(name: str) -> dict:
    """A generated ``.claude/skills`` copy: name, description and metadata only (I2)."""
    return {"name": name, "description": DESCRIPTION, "metadata": {"version": "1.0.0"}}


def front_for(folder: str, name: str) -> dict:
    leaf = name.rsplit("/", 1)[-1]
    if folder == KERNEL:
        return kernel_front(leaf)
    if folder == CLAUDE:
        return claude_front(leaf)
    return rulesync_front(leaf)


def write_skill(project: Path, folder: str, name: str, front: dict, body: str = BODY) -> Path:
    """``<project>/<folder>/<name>/SKILL.md`` with ``front`` as its front matter."""
    path = project / folder / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(front, sort_keys=False, default_flow_style=False, allow_unicode=True)
    path.write_text(f"---\n{text}---\n\n# {name.rsplit('/', 1)[-1]}\n\n{body}", encoding="utf-8")
    return path


def plant_clean(project: Path, name: str, folders: tuple[str, ...] = (KERNEL, *GENERATED)) -> dict[str, Path]:
    """The skill ``name`` clean in each of ``folders`` (by default the kernel and the three generated folders)."""
    return {folder: write_skill(project, folder, name, front_for(folder, name)) for folder in folders}


def plant_with(project: Path, folder: str, name: str, extra: dict) -> Path:
    """The skill ``name`` in ``folder`` as its clean front matter is, plus the keys in ``extra``."""
    return write_skill(project, folder, name, {**front_for(folder, name), **extra})


# --- running the check ------------------------------------------------------------------------------------------------

def check_command(check_id: str) -> list[str]:
    """The ``command:`` of a skill-regression check file, as ``gov check`` reads it, split into words."""
    declared = yaml.safe_load((CHECKS / f"{check_id}.yaml").read_text(encoding="utf-8"))
    return shlex.split(declared["command"])


CHECK_HEAD = ["python3", "-m", "gov.check.skill_validator", "--both-layouts"]


def argv_for(folders: list[str]) -> list[str]:
    """The command of ``skill-regression-a`` with its folder list swapped for ``folders``: the check file's words
    (``python3 -m gov.check.skill_validator --both-layouts <kernel skill folders>``) run by this interpreter, with
    ``-P`` as ``gov check`` runs it, and the switch's module in place of the real one when it is set."""
    head = check_command("skill-regression-a")[:4]
    assert head == CHECK_HEAD, f"skill-regression-a no longer runs the validator in its --both-layouts form: {head}"
    return [sys.executable, "-P", "-m", MODULE, "--both-layouts", *folders]


def env_for() -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(part for part in (STANDIN_DIR, str(SRC)) if part)
    env.pop("PYTHONSTARTUP", None)
    return env


@dataclass
class Run:
    code: int
    out: str
    err: str
    data: dict | None

    @property
    def findings(self) -> list:
        data = self.data or {}
        return data.get("findings") if isinstance(data.get("findings"), list) else []

    def text(self) -> str:
        return f"exit {self.code}\nstdout: {self.out}\nstderr: {self.err}"


def run_validator(project: Path, folders: list[str]) -> Run:
    """The validator as a process, working folder ``project``, over the kernel folders ``folders``."""
    done = subprocess.run(argv_for(folders), cwd=project, env=env_for(), capture_output=True, text=True,
                          timeout=120, check=False)
    data = None
    for line in reversed(done.stdout.strip().splitlines()):
        try:
            parsed = json.loads(line)
        except ValueError:
            continue
        if isinstance(parsed, dict):
            data = parsed
            break
    return Run(done.returncode, done.stdout, done.stderr, data)


def run_on(project: Path, *names: str) -> Run:
    """The check as ``skill-regression-a`` runs it, over the kernel skill folder(s) ``names``."""
    return run_validator(project, [f"{KERNEL}/{name}" for name in names])


def run_on_root(project: Path) -> Run:
    """The check over the kernel skills root (where I4's vendored skills lie)."""
    return run_validator(project, [KERNEL])


# --- reading what it printed -------------------------------------------------------------------------------------------

def same_file(project: Path, reported, planted: Path) -> bool:
    """Whether the finding's ``file`` is the planted file: both resolved against the project, compared as paths."""
    if not isinstance(reported, str) or not reported:
        return False
    try:
        return (project / reported).resolve() == planted.resolve()
    except OSError:
        return False


def about(run: Run, project: Path, planted: Path, key: str | None = None) -> list[dict]:
    """The findings whose ``file`` is ``planted`` and, when ``key`` is given, whose ``key`` is ``key``."""
    return [f for f in run.findings if isinstance(f, dict) and same_file(project, f.get("file"), planted)
            and (key is None or f.get("key") == key)]


def refusing(findings: list) -> list[dict]:
    """The findings that refuse: every one but the named-only ``SKILL_VENDORED_KEY`` (I1, I4)."""
    return [f for f in findings if isinstance(f, dict) and f.get("code") != VENDORED_CODE]


def files_named(run: Run, project: Path) -> set[Path]:
    return {(project / f["file"]).resolve() for f in run.findings
            if isinstance(f, dict) and isinstance(f.get("file"), str) and f["file"]}


def assert_refused(run: Run, project: Path, planted: Path, key: str) -> dict:
    """Exit 1 and a refusing finding of four fields (I1) naming ``planted`` and ``key``; returns that finding."""
    assert run.code == 1, f"expected exit 1 (a refusal): {run.text()}"
    found = refusing(about(run, project, planted, key))
    assert found, f"no refusing finding names file {planted.relative_to(project)} and key {key!r}: {run.out}"
    finding = found[0]
    for field in ("code", "file", "key", "message"):
        assert field in finding, f"finding lacks {field!r}: {finding}"
    assert isinstance(finding["code"], str) and finding["code"], finding
    assert isinstance(finding["message"], str) and finding["message"], finding
    return finding


def assert_passes(run: Run) -> None:
    assert run.code == 0, f"expected exit 0: {run.text()}"
    assert run.data is not None and run.data.get("findings") == [], f"expected no findings: {run.out}"
