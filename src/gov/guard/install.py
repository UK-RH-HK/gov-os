"""Install-command classifier and rule (W1-04, DEC-120).

Classifies plain Bash commands as installs (package managers, downloads
piped to a shell, binary downloads into a PATH directory) and as sudo.
Only plain spellings (CAP-25.c).
"""
from __future__ import annotations

import os
import shlex

from gov.guard.decide import KNOWN_ROLES

_PKG = frozenset({
    "pip", "pip3", "npm", "cargo", "apt", "apt-get",
    "pipx", "pnpm", "yarn", "snap", "brew", "go", "gem", "conda", "dnf", "yum",
})
_SH = frozenset({"sh", "bash"})
_PUNCT = frozenset("();<>|&\n")


def _is_sep(t):
    """Command separator: non-redirect, non-pipe punctuation."""
    return bool(t) and all(c in _PUNCT for c in t) \
        and ">" not in t and t != "<" \
        and ("|" not in t or t.startswith("||"))


def _is_pipe(t):
    """Pipeline separator: ``|`` or ``|&`` (not ``||``)."""
    return bool(t) and all(c in _PUNCT for c in t) \
        and t[0] == "|" and not t.startswith("||")


def _split(tokens, pred):
    """Split *tokens* on any token where *pred*(t) is true."""
    groups, cur = [], []
    for t in tokens:
        if pred(t):
            if cur:
                groups.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        groups.append(cur)
    return groups


def _segments(command):
    """Tokenise *command* and split on command separators."""
    try:
        lex = shlex.shlex(command, posix=True, punctuation_chars="();<>|&\n")
        lex.whitespace_split = True
        lex.whitespace = " \t\r"
        lex.commenters = ""
        return _split(list(lex), _is_sep)
    except ValueError:
        return []


def _head(tokens):
    """(command basename, remaining args), skipping leading VAR=val."""
    i = 0
    while i < len(tokens):
        eq = tokens[i].find("=")
        if eq > 0 and tokens[i][:eq].replace("_", "A").isalnum() \
                and tokens[i][0] != "-":
            i += 1
            continue
        break
    if i >= len(tokens):
        return "", []
    return os.path.basename(tokens[i]), tokens[i + 1:]


def has_sudo(command):
    """True when *command* invokes ``sudo``."""
    return any(
        _head(c)[0] == "sudo"
        for seg in _segments(command) for c in _split(seg, _is_pipe)
    )


def _download_target(nm, args):
    """Return the output path from curl/wget arguments, or None."""
    sf, lf = ("-o", "--output") if nm == "curl" \
        else ("-O", "--output-document")
    for i, a in enumerate(args):
        if a in (sf, lf):
            return args[i + 1] if i + 1 < len(args) else None
        if a.startswith(lf + "="):
            return a[len(lf) + 1:]
        if len(a) > 2 and a[0] == "-" and a[1] != "-":
            if a.startswith(sf):
                return a[len(sf):]
            if a[-1] == sf[1]:
                return args[i + 1] if i + 1 < len(args) else None
    return None


def has_install(command):
    """True when *command* is a package-manager install, a download piped
    to a shell, or a binary download into a ``PATH`` directory."""
    pd = {os.path.realpath(d)
          for d in os.environ.get("PATH", "").split(":") if d}
    for seg in _segments(command):
        cs = _split(seg, _is_pipe)
        # Pipe to shell: curl/wget ... | sh/bash
        if len(cs) >= 2:
            ln, _ = _head(cs[-1])
            if ln in _SH and any(
                    _head(c)[0] in ("curl", "wget") for c in cs[:-1]):
                return True
        for pcmd in cs:
            nm, args = _head(pcmd)
            # Strip version suffix (pip3.11 -> pip, pip2 -> pip,
            # python2.7 -> python): any trailing digits-and-dots.
            j = len(nm)
            while j > 0 and (nm[j - 1].isdigit() or nm[j - 1] == '.'):
                j -= 1
            if 0 < j < len(nm) and nm[j].isdigit():
                nm = nm[:j]
            # Package-manager install
            if nm in _PKG:
                if "install" in args:
                    return True
                if nm == "npm":
                    nopt = next((a for a in args if a[:1] != "-"), "")
                    if nopt == "i":
                        return True
            elif nm in ("python", "python3"):
                if (len(args) >= 3 and args[0] == "-m"
                        and args[1] == "pip" and "install" in args[2:]):
                    return True
            elif nm == "uv":
                nopt = [a for a in args if not a.startswith("-")]
                if (len(nopt) >= 2 and nopt[0] in ("pip", "tool")
                        and nopt[1] == "install"):
                    return True
            # Binary download into a PATH directory
            if nm in ("curl", "wget"):
                t = _download_target(nm, args)
                if t is not None:
                    t = os.path.expanduser(t)
                    if os.path.isabs(t) \
                            and os.path.realpath(
                                os.path.dirname(t)) in pd:
                        return True
    return False


def acting_role(session_role, subagent_type):
    """The acting role (DEC-107/117/125/113): session role on the main
    thread, subagent role when the session has a declared role, else None.
    """
    sr = (session_role or "").strip()
    if subagent_type is not None:
        if subagent_type in KNOWN_ROLES and sr in KNOWN_ROLES:
            return subagent_type
        return None
    return sr if sr in KNOWN_ROLES else None
