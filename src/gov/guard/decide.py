"""Core decision logic for the PreToolUse default-deny guard (W1-02)."""

from __future__ import annotations

import glob
import os
import re
import shlex
import tempfile
from pathlib import Path

KNOWN_ROLES = frozenset({
    "orchestrator", "product-spec", "independent-test-designer",
    "engineer", "independent-auditor",
    "research",  # DEC-163: held to its ticket's allowed_paths, like engineer
})
WRITE_TOOLS = frozenset({"Edit", "Write", "NotebookEdit"})
READ_TOOLS = frozenset({"Read", "Grep", "Glob"})
FREEZE_FLAG = ".gov-runtime/freeze"
ACCEPTANCE = "tests/acceptance"
_GOV_RUNTIME = ".gov-runtime"
_PUNCT = frozenset("();<>|&\n")
_WRITE_CMDS = frozenset({"touch", "rm", "mv", "cp", "mkdir"})
_ASSIGN_RE = re.compile(r"^[A-Za-z_]\w*=")
_UNRESOLVABLE = "/<guard-unresolvable>"


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


def _get_allowed_paths(role: str, tid: str | None, root: str,
                       *, session_role: str | None = None) -> list[str]:
    if role == "orchestrator":
        # DEC-156: the wide scope applies only in an orchestrator session.
        # An orchestrator subagent in a non-orchestrator session falls
        # through to the ticket-path rule (DEC-136 batch 3).  A missing
        # session role gives no wide scope (DEC-179).
        if session_role == "orchestrator":
            return ["**"]
        # Fall through: use the ticket's allowed_paths when the ticket's
        # role is orchestrator; otherwise the orchestrator subagent gets
        # nothing beyond the scratch set.
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


def _is_gov_runtime_protected(relpath: str) -> bool:
    """True when *relpath* is under ``.gov-runtime/`` but NOT under ``scratch/``.

    DEC-176: the freeze flag, snapshots, findings and records are denied
    to the orchestrator.  ``scratch/**`` stays writable.
    """
    if relpath != _GOV_RUNTIME and not relpath.startswith(_GOV_RUNTIME + "/"):
        return False
    scratch = _GOV_RUNTIME + "/scratch"
    return relpath != scratch and not relpath.startswith(scratch + "/")


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
    # DEC-176, DEC-180: .gov-runtime/ other than scratch/** is denied to
    # every role (the freeze flag, snapshots, findings and records), also
    # on a ticket that names it.
    if _is_gov_runtime_protected(rel):
        return False
    return any(_match_pattern(rel, p) for p in patterns)


# -- Bash target resolution (DEC-115) -----------------------------------------

def _expand_token(token: str) -> str | None:
    """Expand ``~`` and environment variables in a Bash write target.

    Returns the expanded string, or ``None`` when the target is unresolvable.
    Uses ``os.environ`` (the hook process's own environment).
    """
    if not token:
        return None
    if '`' in token:
        return None
    if '$(' in token:
        return None
    if token.endswith('$'):
        return None

    # Tilde at the start.
    if token.startswith('~'):
        expanded = os.path.expanduser(token)
        if expanded.startswith('~'):
            return None
        token = expanded

    # Environment variables.
    if '$' not in token:
        return token

    parts: list[str] = []
    i = 0
    while i < len(token):
        if token[i] != '$':
            parts.append(token[i])
            i += 1
            continue
        if i + 1 >= len(token):
            return None
        nxt = token[i + 1]
        if nxt == '{':
            close = token.find('}', i + 2)
            if close == -1:
                return None
            name = token[i + 2:close]
            if (not name
                    or not all(c.isalnum() or c == '_' for c in name)
                    or name[0].isdigit()):
                return None
            val = os.environ.get(name)
            if val is None:
                return None
            parts.append(val)
            i = close + 1
        elif nxt.isalpha() or nxt == '_':
            j = i + 1
            while j < len(token) and (token[j].isalnum() or token[j] == '_'):
                j += 1
            name = token[i + 1:j]
            val = os.environ.get(name)
            if val is None:
                return None
            parts.append(val)
            i = j
        else:
            return None

    return ''.join(parts)


def _has_glob(s: str) -> bool:
    """True when *s* contains shell glob characters."""
    return '*' in s or '?' in s or '[' in s


# -- Bash write analysis -------------------------------------------------------

def _is_punct(tok: str) -> bool:
    return bool(tok) and all(c in _PUNCT for c in tok)


def _cp_operands(args: list[str]) -> tuple[list[str], list[str]] | None:
    """Split the arguments of ``cp`` into operands and target directories.

    The directories are the values of ``-t`` and ``--target-directory``, in
    their four spellings.  ``None`` when an option cannot be read.
    """
    operands: list[str] = []
    dirs: list[str] = []
    i = 0
    while i < len(args):
        a = args[i]
        i += 1
        if a.startswith("--t"):
            opt, eq, val = a.partition("=")
            if not "--target-directory".startswith(opt):
                return None
        elif a.startswith("-") and not a.startswith("--") and "t" in a:
            val = a[a.index("t") + 1:]
            eq = val
        elif a.startswith("-"):
            continue
        else:
            operands.append(a)
            continue
        if not eq:
            if i >= len(args):
                return None
            val = args[i]
            i += 1
        dirs.append(val)
    return operands, dirs


def _extract_bash_write_targets(command: str, cwd: str) -> list[str] | None:
    """Return absolute write-target paths, or None when the command is read-only.

    Tokenises with shlex (newline as punctuation, ``#`` not a comment),
    splits on non-redirect punctuation, then inspects each simple command
    for redirects and the plain write commands (DEC-111).  Each write target
    is resolved first (DEC-115): ``~``, ``~user`` and environment variables
    are expanded from the hook's own environment; globs are matched against
    the file system; anything still unresolvable maps to a sentinel that
    fails every allow-list check.
    """
    try:
        lex = shlex.shlex(command, posix=True, punctuation_chars="();<>|&\n")
        lex.whitespace_split = True
        lex.whitespace = " \t\r"
        lex.commenters = ""
        tokens = list(lex)
    except ValueError:
        return [_UNRESOLVABLE]

    ecwd = cwd
    ecwd_ok = True
    targets: list[str] = []
    link_sources: list[str] = []  # what the links made by this command name
    link_dests = 0                # how many of *targets* are their destinations

    def _resolve(raw: str, targets: list[str] = targets) -> None:
        """Expand, glob-expand and resolve *raw* into *targets*."""
        exp = _expand_token(raw)
        if exp is None:
            targets.append(_UNRESOLVABLE)
            return
        if '{' in exp or '}' in exp:
            targets.append(_UNRESOLVABLE)
            return
        if os.path.isabs(exp) and os.path.realpath(exp) == "/dev/null":
            return
        if not os.path.isabs(exp) and not ecwd_ok:
            targets.append(_UNRESOLVABLE)
            return
        if _has_glob(exp):
            pat = exp if os.path.isabs(exp) else os.path.join(ecwd, exp)
            matches = glob.glob(pat)
            if not matches:
                targets.append(_UNRESOLVABLE)
                return
            for m in matches:
                targets.append(os.path.realpath(m))
            return
        p = exp if os.path.isabs(exp) else os.path.join(ecwd, exp)
        targets.append(os.path.realpath(p))

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
                    _resolve(scmd[i + 1])
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

        if name in ("pushd", "popd"):
            ecwd_ok = False
            continue
        if name == "cd":
            if not args:
                h = os.environ.get("HOME")
                if h is None:
                    ecwd_ok = False
                else:
                    ecwd = h
                    ecwd_ok = True
                continue
            d = args[0]
            if d.startswith("-"):
                ecwd_ok = False
                continue
            exp = _expand_token(d)
            if exp is None or _has_glob(exp) or '{' in exp or '}' in exp:
                ecwd_ok = False
            elif not os.path.isabs(exp) and not ecwd_ok:
                pass  # ecwd stays invalid
            else:
                ecwd = exp if os.path.isabs(exp) else os.path.join(ecwd, exp)
                ecwd_ok = True
            continue
        if name == "tee":
            for a in args:
                if not a.startswith("-"):
                    _resolve(a)
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
                    _resolve(a)
            continue
        if name in ("touch", "rm", "mkdir"):
            for a in args:
                if not a.startswith("-"):
                    _resolve(a)
            continue
        if name == "mv":
            for a in args:
                if not a.startswith("-"):
                    _resolve(a)
            continue
        if name == "cp":
            parsed = _cp_operands(args)
            if parsed is None:
                targets.append(_UNRESOLVABLE)
                continue
            nf, dirs = parsed
            # -t, --target-directory: every operand is a source, and the
            # copy lands in the directory under the operand's own name.
            for d in dirs:
                for a in nf:
                    base = os.path.basename(a.rstrip("/"))
                    if base in ("", ".", ".."):
                        targets.append(_UNRESOLVABLE)
                    else:
                        _resolve(os.path.join(d, base) if d else d)
            if not dirs and len(nf) >= 2:
                _resolve(nf[-1])
            continue
        if name == "ln":
            # DEC-311: the destination of a symbolic or a hard link is a
            # write target.  A form whose destination is not the last
            # operand (-t, --target-directory, "--") is refused.
            if any(a == "--" or a.startswith("--t")
                   or (a.startswith("-") and not a.startswith("--")
                       and "t" in a)
                   for a in args):
                targets.append(_UNRESOLVABLE)
                continue
            nf = [a for a in args if not a.startswith("-")]
            before = len(targets)
            if len(nf) >= 2:
                _resolve(nf[-1])
            elif nf:
                # "ln <target>" links under the target's name, here.
                _resolve(os.path.basename(nf[0].rstrip("/")) or ".")
            link_dests += len(targets) - before
            # What the link names, for a write through it in this command.
            # A relative name of a symbolic link is read from the link's
            # directory, which is not resolved here: it is refused.
            symbolic = any(a.startswith("--s")
                           or (a.startswith("-") and not a.startswith("--")
                               and "s" in a)
                           for a in args)
            for a in (nf[:-1] if len(nf) >= 2 else nf):
                if symbolic and not os.path.isabs(_expand_token(a) or ""):
                    link_sources.append(_UNRESOLVABLE)
                else:
                    _resolve(a, link_sources)

    # A command that makes a link and writes anything else may write through
    # the link: what the link names is judged as a write target too.
    if len(targets) > link_dests:
        targets.extend(link_sources)

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

    # CAP-62.a: no Bash call leaves the sandbox, whatever the role.
    if tool_name == "Bash" and tool_input.get("dangerouslyDisableSandbox"):
        return "deny", "dangerouslyDisableSandbox is denied to every role"

    # DEC-162, DEC-215: no call names a held-out path, whatever the tool
    # and the role.  A broken held-out.yaml stops every call (DEC-218).
    from gov.guard.heldout import HeldOutError, load_held_out, names_held_out
    try:
        held_out = load_held_out(project_root)
    except HeldOutError as exc:
        return "deny", f"{exc}: every call is denied until the owner repairs it"
    if held_out and names_held_out(tool_name, tool_input, project_root,
                                   cwd or project_root, held_out):
        return "deny", "the call names a held-out path"

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

    # Determine the acting role (DEC-117, DEC-125, DEC-113).
    if subagent_type is not None:
        if subagent_type not in KNOWN_ROLES:
            return "deny", f"subagent type '{subagent_type}' is not a known role"
        if erole not in KNOWN_ROLES:
            return "deny", f"role '{erole}' is not a known role"
        acting_role = subagent_type
    else:
        if erole not in KNOWN_ROLES:
            return "deny", f"role '{erole}' is not a known role"
        acting_role = erole

    pats = _get_allowed_paths(acting_role, ticket_id, project_root,
                              session_role=erole)
    for tgt in write_targets:
        if not _path_allowed(tgt, project_root, pats, acting_role):
            lbl = "Bash write" if tool_name == "Bash" else tool_name
            return "deny", f"{lbl} to '{tgt}' denied for role '{acting_role}'"

    return "allow", ""
