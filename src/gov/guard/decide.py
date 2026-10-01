"""Core decision logic for the PreToolUse default-deny guard (W1-02)."""

from __future__ import annotations

import os
import re
import shlex
import tempfile
from pathlib import Path

KNOWN_ROLES = frozenset({
    "orchestrator", "product-spec", "independent-test-designer",
    "engineer", "independent-auditor",
})
WRITE_TOOLS = frozenset({"Edit", "Write", "NotebookEdit"})
READ_TOOLS = frozenset({"Read", "Grep", "Glob"})
FREEZE_FLAG = ".gov-runtime/freeze"
ACCEPTANCE = "tests/acceptance"
_PUNCT = frozenset("();<>|&\n")
_WRITE_CMDS = frozenset({"touch", "rm", "mv", "cp", "mkdir"})
_ASSIGN_RE = re.compile(r"^[A-Za-z_]\w*=")


# -- frontmatter --------------------------------------------------------------

def _parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    result: dict = {}
    paths: list[str] = []
    in_paths = False
    for line in text[4:end].splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if re.match(r"^[a-zA-Z_][\w-]*:", line) and not line[0].isspace():
            in_paths = False
            key, _, val = line.partition(":")
            if key.strip() == "allowed_paths":
                in_paths = True
                continue
            result[key.strip()] = val.strip()
        elif in_paths and s.startswith("- "):
            e = s[2:].strip()
            if len(e) >= 2 and e[0] == e[-1] and e[0] in ("'", '"'):
                e = e[1:-1]
            paths.append(e)
        elif in_paths and not s.startswith("-"):
            in_paths = False
    result["allowed_paths"] = paths
    return result


# -- pattern matching ----------------------------------------------------------

def _match_pattern(relpath: str, pattern: str) -> bool:
    parts = pattern.split("**")
    segs = [re.escape(p).replace(r"\*", "[^/]*") for p in parts]
    rx = "^" + ".*".join(segs)
    if pattern.endswith("**"):
        rx += ".*"
    return bool(re.match(rx + "$", relpath))


# -- ticket loading ------------------------------------------------------------

def _load_ticket(root: str, tid: str) -> dict | None:
    if not tid or "/" in tid or os.sep in tid:
        return None
    d = Path(root) / ".tickets"
    if not d.is_dir():
        return None
    p = d / f"{tid}.md"
    if p.is_file():
        try:
            return _parse_frontmatter(p.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            return None
    try:
        for p in sorted(d.glob("*.md")):
            if not p.is_file():
                continue
            try:
                fm = _parse_frontmatter(p.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                continue
            if fm and fm.get("wbs_id") == tid:
                return fm
    except OSError:
        pass
    return None


def _get_allowed_paths(role: str, tid: str | None, root: str) -> list[str]:
    if role not in KNOWN_ROLES or not tid:
        return []
    t = _load_ticket(root, tid)
    if not t or t.get("status") != "in_progress":
        return []
    if role == "independent-test-designer":
        return [ACCEPTANCE + "/**"]
    if t.get("role") != role:
        return []
    return [p for p in t.get("allowed_paths", [])
            if not _is_under_acceptance(p.rstrip("*/ "))]


# -- path helpers --------------------------------------------------------------

def _is_under_acceptance(relpath: str) -> bool:
    return relpath == ACCEPTANCE or relpath.startswith(ACCEPTANCE + "/")


def _is_in_scratch(path: str, root: str) -> bool:
    real = os.path.realpath(path)
    rr = os.path.realpath(root)
    scratch = os.path.join(rr, ".gov-runtime", "scratch")
    if real == scratch or real.startswith(scratch + "/"):
        return True
    tmp = os.path.realpath(tempfile.gettempdir())
    if rr == tmp or rr.startswith(tmp + "/"):
        return False
    return real == tmp or real.startswith(tmp + "/")


def _path_allowed(path: str, root: str, patterns: list[str], role: str) -> bool:
    real = os.path.realpath(path)
    if real == "/dev/null":
        return True
    if role not in KNOWN_ROLES:
        return False
    if role == "independent-test-designer" and not patterns:
        return False
    if _is_in_scratch(real, root):
        return True
    rr = os.path.realpath(root)
    if not real.startswith(rr + "/") and real != rr:
        return False
    rel = real[len(rr) + 1:]
    if role != "independent-test-designer" and _is_under_acceptance(rel):
        return False
    return any(_match_pattern(rel, p) for p in patterns)


# -- Bash write analysis -------------------------------------------------------

def _is_punct(tok: str) -> bool:
    return bool(tok) and all(c in _PUNCT for c in tok)


def _extract_bash_write_targets(command: str, cwd: str) -> list[str] | None:
    """Return absolute write-target paths, or None when the command is read-only.

    Tokenises with shlex (newline as punctuation, ``#`` not a comment),
    splits on non-redirect punctuation, then inspects each simple command
    for redirects and the plain write commands (DEC-111).
    """
    try:
        lex = shlex.shlex(command, posix=True, punctuation_chars="();<>|&\n")
        lex.whitespace_split = True
        lex.whitespace = " \t\r"
        lex.commenters = ""
        tokens = list(lex)
    except ValueError:
        return ["<unparseable>"]

    ecwd = cwd
    targets: list[str] = []

    def res(p: str) -> str:
        return os.path.realpath(p if os.path.isabs(p) else os.path.join(ecwd, p))

    def redir(p: str) -> None:
        if os.path.isabs(p) and os.path.realpath(p) == "/dev/null":
            return
        targets.append(res(p))

    # Split on non-redirect punctuation into simple commands.
    # A punctuation token containing '>' stays with its command (redirect).
    # '<' stays too (input redirect, not a write).
    cmds: list[list[str]] = []
    cur: list[str] = []
    for tok in tokens:
        if _is_punct(tok) and ">" not in tok and tok != "<":
            if cur:
                cmds.append(cur)
                cur = []
        else:
            cur.append(tok)
    if cur:
        cmds.append(cur)

    for scmd in cmds:
        words: list[str] = []
        i = 0
        while i < len(scmd):
            t = scmd[i]
            if _is_punct(t) and ">" in t:
                # A bare digit just before a redirect is the fd number.
                if words and words[-1].isdigit():
                    words.pop()
                # >& followed by a digit or '-' is fd duplication.
                if t == ">&" and i + 1 < len(scmd) and (
                    scmd[i + 1].isdigit() or scmd[i + 1] == "-"
                ):
                    i += 2
                    continue
                # Otherwise the next word-token is the target file.
                if i + 1 < len(scmd) and not _is_punct(scmd[i + 1]):
                    redir(scmd[i + 1])
                    i += 2
                    continue
                i += 1
                continue
            if t == "<":
                i += 2  # skip input redirect and its target
                continue
            words.append(t)
            i += 1

        if not words:
            continue

        # Skip leading NAME=value environment assignments.
        idx = 0
        while idx < len(words) and _ASSIGN_RE.match(words[idx]):
            idx += 1
        if idx >= len(words):
            continue

        name = os.path.basename(words[idx])
        args = words[idx + 1:]

        if name == "cd" and args:
            d = args[0]
            ecwd = d if os.path.isabs(d) else os.path.join(ecwd, d)
            continue
        if name == "tee":
            for a in args:
                if not a.startswith("-"):
                    redir(a)
            continue
        if name == "sed":
            if any(a in ("-i", "--in-place")
                   or (a.startswith("-i") and len(a) > 2)
                   or a.startswith("--in-place=")
                   for a in args):
                seen_expr = False
                for a in args:
                    if a.startswith("-"):
                        continue
                    if not seen_expr:
                        seen_expr = True
                        continue
                    targets.append(res(a))
            continue
        if name in ("touch", "rm", "mkdir"):
            for a in args:
                if not a.startswith("-"):
                    targets.append(res(a))
            continue
        if name == "mv":
            for a in args:
                if not a.startswith("-"):
                    targets.append(res(a))
            continue
        if name == "cp":
            nf = [a for a in args if not a.startswith("-")]
            if len(nf) >= 2:
                targets.append(res(nf[-1]))

    return targets or None


# -- main decision -------------------------------------------------------------

def decide(
    tool_name: str,
    tool_input: dict,
    project_root: str,
    role: str | None,
    ticket_id: str | None,
    subagent_type: str | None = None,
    cwd: str | None = None,
) -> tuple[str, str]:
    """Return ``("allow", "")`` or ``("deny", "<reason>")``."""
    frozen = os.path.exists(os.path.join(project_root, FREEZE_FLAG))
    erole = (role or "").strip() or ""

    if tool_name in READ_TOOLS:
        return "allow", ""

    # Collect write targets.
    if tool_name == "Bash":
        wt = _extract_bash_write_targets(
            tool_input.get("command", ""), cwd or project_root)
        if wt is None:
            return "allow", ""
        write_targets = wt
    elif tool_name in WRITE_TOOLS:
        pk = "notebook_path" if tool_name == "NotebookEdit" else "file_path"
        ps = tool_input.get(pk, "")
        if not ps:
            return "deny", f"{tool_name}: no file path"
        if not os.path.isabs(ps):
            ps = os.path.join(cwd or project_root, ps)
        ap = os.path.realpath(ps)
        if ap == "/dev/null":
            return "allow", ""
        write_targets = [ap]
    else:
        return "allow", ""

    # Frozen: deny all writes.
    if frozen:
        return "deny", "frozen: all writes denied"
    if erole not in KNOWN_ROLES:
        return "deny", f"role '{erole}' is not a known role"
    if subagent_type is not None and subagent_type not in KNOWN_ROLES:
        return "deny", f"subagent type '{subagent_type}' is not a known role"

    roles = [erole]
    if subagent_type is not None and subagent_type != erole:
        roles.append(subagent_type)

    for r in roles:
        pats = _get_allowed_paths(r, ticket_id, project_root)
        for tgt in write_targets:
            if not _path_allowed(tgt, project_root, pats, r):
                lbl = "Bash write" if tool_name == "Bash" else tool_name
                return "deny", f"{lbl} to '{tgt}' denied for role '{r}'"

    return "allow", ""
