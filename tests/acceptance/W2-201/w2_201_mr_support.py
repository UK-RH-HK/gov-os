"""Support for the MR-1..MR-3 cases (fix under W2-201, DEC-1246 (3)(b)): the role table, scripts and the git ranges.

Everything goes through public interfaces: ``gov launch`` on W2-184's fixture project and the stand-in CLI, the module
``gov.launch.role_table`` as a function and as ``python3 -m`` (cwd the planted root), and ``gov.launch.criticality.load``.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import yaml

import w2_201_support as k

s, b = k.s, k.b
REPO = k.REPO_ROOT
TABLE_REL = "governance/project/role-table.yaml"
KIT_TABLE_REL = "template/governance/project/role-table.yaml"
OPUS, SONNET = k.OPUS, k.SONNET
ROLES = ("orchestrator", "senior-engineer", "lead", "engineer", "independent-test-designer", "product-spec", "research",
         "independent-auditor", "qa-engineer", "audit-wide")
H, M = "high", "medium"
# The values that stand today and do not change (DEC-1236 (3)).
VALUES = {
    "orchestrator": (OPUS, H), "senior-engineer": (OPUS, H), "lead": (SONNET, M), "engineer": (SONNET, H),
    "independent-test-designer": (SONNET, H), "product-spec": (SONNET, H), "research": (SONNET, H),
    "independent-auditor": (SONNET, H), "qa-engineer": (SONNET, H), "audit-wide": (OPUS, H),
}
DECIDED = "DEC-1242 R-4"


def table_data(**changes):
    """The table as a map; ``changes`` is ``role=(model, effort)`` (underscores in role names written as ``__``)."""
    values = dict(VALUES)
    # Rewrite-Reason: DEC-1246 (3)(b): MR-1: a keyword `qa_engineer` (one underscore) never matched the `qa-engineer` row.
    def _role(name):
        return name.replace("__", "-") if name.replace("__", "-") in ROLES else name.replace("_", "-")
    values.update({_role(name): v for name, v in changes.items()})
    assert set(values) == set(ROLES), f"unknown role in {sorted(changes)}"
    rows = [{"role": r, "model": values[r][0], "effort": values[r][1], "decided": DECIDED} for r in ROLES]
    return {"version": 1, "rows": rows}


def table_text(**changes):
    return yaml.safe_dump(table_data(**changes), sort_keys=False)


def write_table(root, text=None, **changes):
    return b.write(Path(root) / TABLE_REL, table_text(**changes) if text is None else text)


def crit_without_opus(project, default="C0"):
    """The criticality file in its new form (``version``, ``default``, ``rules``)."""
    data = {"version": 1, "default": default, "rules": s.RULES}
    return b.write(Path(project) / s.CRITICALITY_REL, yaml.safe_dump(data, sort_keys=False))


def python_m(args, cwd):
    """``python3 -m gov.launch.role_table <args>`` with cwd the root and this worktree's ``src`` on the path."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(Path(cwd) / ".home"), "LANG": "C.UTF-8",
           "PYTHONPATH": str(REPO / "src")}
    return subprocess.run([sys.executable, "-m", "gov.launch.role_table", *map(str, args)], cwd=str(cwd), env=env,
                          capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)


def said(done):
    return (done.stdout + "\n" + done.stderr)


def git(cwd, *args):
    done = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=60,
                          env={**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"})
    assert done.returncode == 0, f"git {' '.join(args)}: {done.stderr}"
    return done.stdout.strip()


def repo_with_table(tmp_path):
    """A repository whose first commit holds the table; returns its path."""
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "t")
    git(root, "config", "user.email", "t@example.invalid")
    write_table(root)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "the table")
    return root


def edit_row(root, role, field, value, *, trailer=None):
    """Change one row's field and commit it (with the trailer paragraph when given); returns nothing."""
    path = Path(root) / TABLE_REL
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for row in data["rows"]:
        if row["role"] == role:
            row[field] = value
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    git(root, "add", "-A")
    message = ["commit", "-q", "-m", f"change {role} {field}"]
    if trailer:
        message += ["-m", trailer]
    git(root, *message)


def roles_tree(tmp_path, *, engineer_line=None):
    """A root holding the standard table and this repository's kernel role files (where the role reader reads them)."""
    base = tmp_path / "roles-root"
    for name in ("orchestrator", "senior-engineer", "ticket-lead", "engineer", "independent-test-designer",
                 "product-spec", "research", "independent-auditor", "qa-engineer"):
        tree = k.plant_role_copy(base, k.ROLES_REL, name)
    write_table(tree)
    if engineer_line:
        path = tree / k.ROLES_REL / "engineer.md"
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        lines = [engineer_line + "\n" if l.startswith("- **Launch default:**") else l for l in lines]
        path.write_text("".join(lines), encoding="utf-8")
    return tree


# --------------------------------------------------------------------------------------------------------------------
# The start scripts (copies in the forms the CTO's three scripts have; the lines that carry the model and the effort)
# --------------------------------------------------------------------------------------------------------------------

LEAD = ('#!/usr/bin/env bash\nEFFORT=${EFFORT:-medium}; export EFFORT; n=$1; b=$2\n'
        'setsid nohup env EFFORT=$EFFORT bash -c \'\n'
        '  env -u CLAUDECODE GOV_ROLE=orchestrator "$HOME/.local/bin/claude" -p --model claude-sonnet-5-5 '
        '--effort "${EFFORT:-medium}" --permission-mode bypassPermissions --strict-mcp-config "$b"\' >/dev/null 2>&1 &\n')
CTO = ('#!/usr/bin/env bash\nR=/tmp/x; S=cto-1\n'
       'tmux new-session -d -s "$S" -c "$R" "env -u CLAUDECODE GOV_ROLE=orchestrator $HOME/.local/bin/claude '
       '--remote-control \'Gov OS CTO\' --model claude-opus-5-5 --effort high --permission-mode bypassPermissions"\n')
AUDIT = ('#!/usr/bin/env bash\nn=$1\n'
         'cd "$4" && env -u CLAUDECODE GOV_ROLE=independent-auditor "$HOME/.local/bin/claude" -p '
         '--model claude-opus-5-5 --effort high --permission-mode bypassPermissions --strict-mcp-config "$2"\n')
SCRIPTS = {"start_lead.sh": LEAD, "start_cto.sh": CTO, "start_audit.sh": AUDIT}


def plant_scripts(folder, **changes):
    """The three scripts in ``folder``; ``changes`` is ``name=(old, new)`` (a replacement) or ``name=text``."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for name, text in SCRIPTS.items():
        key = name.replace(".sh", "")
        change = changes.get(key)
        if isinstance(change, tuple):
            assert change[0] in text, f"{change[0]!r} not in {name}"
            text = text.replace(*change)
        elif change is not None:
            text = change
        (folder / name).write_text(text, encoding="utf-8")
    return folder
