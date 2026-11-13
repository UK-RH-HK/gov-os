"""Support code for W2-141's hook-side acceptance tests, round 2 (standard library only, plus the tree's own code).

The gap W2-138 hit is in the live hook ``.claude/hooks/role_reads.py`` (G-14), which lets an engineer's search from a
folder above its own acceptance folder through. These cases drive that hook module the way the live PreToolUse hook
(``.claude/hooks/pretooluse.py``) calls it::

    role_reads.refusal(main, os.path.realpath(root), tool, seen, cwd,
                       [r for r in dict.fromkeys((role, acting)) if r], ticket,
                       lambda: tree_roots(root), _expand_token)

with ``seen`` the tool input (for Bash, the command as ``bash_writes.reads_view`` gives it), ``acting`` the role
``gov.guard.reads.acting_role(role, agent_type)`` gives, and ``_expand_token`` from ``gov.guard.decide``. A refusal is
the reason string; None lets the call through.

**Which hook file** (the ticket's "The hook side"; DEC-315): a launched engineer cannot edit ``.claude/``, so it builds
the changed hook as a whole-file copy at ``docs/changes/W2-141-hook/role_reads.py``; the operator copies it to
``.claude/hooks/role_reads.py`` at the lift's re-pin. ``hook_file`` takes the staged copy when it exists in the tree
under test, else the live hook, and loads it by file path (importlib) under a module name of its own. ``bash_writes``
is imported from the tree's ``.claude/hooks/`` (the staged copy has no copy of it beside it).

**The tree under test** is the parent of the ``src`` folder ``PYTHONPATH`` names first when that tree holds the hook,
else the worktree that holds this file.

**The planted project** is round 1's (``w2_141_support.make_project``), made a git repository of its own with no
commits (so the hook's git questions, the link source of other folders' revised cases, answer from it alone). The
path map holds the ``role_paths:`` section (never the main tree's); ``main`` is the planted project; ``HOME`` is the
module's temporary folder, so ``~/gov-os-worktrees`` names nothing real.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import w2_141_support as support

STAGED_REL = "docs/changes/W2-141-hook/role_reads.py"
LIVE_REL = ".claude/hooks/role_reads.py"


def tree_under_test():
    """The tree whose hook and src are tested: PYTHONPATH's first src's parent when it holds the hook, else this
    worktree."""
    for entry in (os.environ.get("PYTHONPATH") or "").split(os.pathsep):
        if entry and os.path.basename(os.path.normpath(entry)) == "src":
            parent = Path(entry).resolve().parent
            if (parent / LIVE_REL).is_file() or (parent / STAGED_REL).is_file():
                return parent
    return support.REPO_ROOT


def hook_file(tree):
    """The staged copy when it exists in ``tree``, else the live hook."""
    staged = Path(tree) / STAGED_REL
    return staged if staged.is_file() else Path(tree) / LIVE_REL


def load_hook(tree):
    """The hook module from its file, and the helpers pretooluse.py passes it. Call with HOME already set: the module
    reads ~/gov-os-worktrees when it loads."""
    tree = Path(tree)
    src = str(tree / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    hooks = str(tree / ".claude" / "hooks")
    if hooks not in sys.path:
        sys.path.insert(0, hooks)
    import bash_writes  # noqa: F401  (role_reads imports it by name when it reads a command)
    from gov.guard import reads
    from gov.guard.decide import _expand_token
    path = hook_file(tree)
    spec = importlib.util.spec_from_file_location("w2_141_role_reads_under_test", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path, reads.acting_role, _expand_token, bash_writes.reads_view


def git_init(root):
    """The planted project as a git repository with no commits (the hook's git questions answer from it)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
    subprocess.run(["git", "init", "-q", str(root)], check=True, env=env, capture_output=True, timeout=30)


class HookGuard:
    """role_reads.refusal over one planted project, the session's cwd its root, as pretooluse.py calls it."""

    def __init__(self, project, loaded):
        self.project = project
        self.module, self.path, self._acting, self._expand, self._reads_view = loaded

    @property
    def root(self):
        return str(self.project.root)

    def ask(self, call, role=support.ENGINEER, ticket=support.TICKET, agent=None):
        """The hook's answer as a support.Decision; ``{root}`` in a field or a command is the project's path."""
        data = {k: v.replace("{root}", self.root) if isinstance(v, str) else v for k, v in call.input.items()}
        if call.tool == "Bash":
            data = dict(data, command=self._reads_view(data["command"]))
        acting = self._acting(role, agent)
        roles = [r for r in dict.fromkeys((role, acting)) if r]
        root = os.path.realpath(self.root)
        why = self.module.refusal(root, root, call.tool, data, self.root, roles, ticket, lambda: [root],
                                  self._expand)
        if why:
            return support.Decision("deny", str(why))
        return support.Decision("allow", "")

    def label(self):
        return f"[hook {self.path}] "
