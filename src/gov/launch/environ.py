"""The cleaned environment of a launched session (W2-56 S5; DEC-826 Q5, lens E F13, DEC-784, DEC-877 item 4).

What passes is a list, not a filter: of the parent's variables only ``PATH`` (whole), ``HOME``, the locale (``LANG``,
``LC_ALL``) and the identity (``USER``, ``LOGNAME``) reach the session, beside the launcher's own values (``TMPDIR``
and ``CLAUDE_CODE_TMPDIR``, ``GOV_ROLE``, ``GOV_TICKET``, ``GOV_STORE``). Nothing else of the parent passes: none of
its ``CLAUDE*`` and ``GOV*`` variables (its session id, messaging socket and token, child-session mark, effort,
compaction window, subagent model, ``GOV_DEV_TIERS``), no ``PYTHONPATH``, no ``TMPDIR`` of its own.

What the CLI needs to sign in passes to the CLI process only, never into ``--settings`` (whose text other users can
read in the process list): ``ANTHROPIC_API_KEY``, ``ANTHROPIC_AUTH_TOKEN`` and ``CLAUDE_CODE_OAUTH_TOKEN``, the one
``CLAUDE*`` variable that passes (the CIT-E names it). A CLI signed in through ``~/.claude`` needs none of them.
"""

from __future__ import annotations

from collections.abc import Mapping

KEPT = ("PATH", "HOME", "LANG", "LC_ALL", "USER", "LOGNAME")
SIGN_IN = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN")


def _of(parent: Mapping[str, str], names) -> dict[str, str]:
    return {name: parent[name] for name in names if isinstance(parent.get(name), str)}


def settings_env(parent: Mapping[str, str], own: Mapping[str, str]) -> dict[str, str]:
    """The ``env`` block of ``--settings``: the kept variables of ``parent`` and the launcher's ``own`` values."""
    return {**_of(parent, KEPT), **own}


def session_env(parent: Mapping[str, str], own: Mapping[str, str]) -> dict[str, str]:
    """The CLI process's environment: ``settings_env`` and the parent's sign-in variables."""
    return {**_of(parent, SIGN_IN), **settings_env(parent, own)}
