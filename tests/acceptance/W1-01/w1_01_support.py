"""Support code for the W1-01 acceptance tests (standard library only).

Two things live here:

1. A small model of how the harness evaluates ``permissions.deny`` rules in
   ``.claude/settings.json``. The tests make one "attempt" per KPI path class or
   install command against the rule set and expect the model to answer "denied".
   The model is deliberately the *strict* reading of the rule syntax, so a rule
   set that passes here denies under every reading:

   - ``Edit(<glob>)`` covers every file-editing tool (Edit, Write, NotebookEdit);
     ``Write(<glob>)`` covers Write only; ``Read(<glob>)`` covers Read only.
     A bare tool name (``Edit``) covers every use of that tool.
   - Path globs: ``//x`` is absolute, ``~/x`` is under the home directory, and
     ``/x``, ``./x`` and ``x`` are relative to the repository root (sessions
     start there). ``*`` and ``?`` never cross a ``/``; ``**`` does. A pattern
     without a slash is NOT floated to every depth: ``*.pem`` covers the root
     only, ``**/*.pem`` covers every depth.
   - ``Bash(<prefix>:*)`` and ``Bash(<prefix> *)`` match the bare prefix and the
     prefix followed by arguments; any other ``*`` matches any run of
     characters; a rule without ``*`` matches the exact command. A compound
     command is denied when any of its parts is denied.

2. Readers for the records the ticket names: git history and ticket frontmatter.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SETTINGS_REL = ".claude/settings.json"
BOOTSTRAP_REL = "governance/project/bootstrap.md"
TOOL_REGISTRY_REL = "governance/project/tool-registry.yaml"
TEST_DESIGNER_ROLE = "independent-test-designer"

FILE_EDIT_TOOLS = ("Edit", "Write", "NotebookEdit")

_RULE = re.compile(r"^\s*([A-Za-z_][\w-]*)\s*(?:\((.*)\))?\s*$", re.S)


# --------------------------------------------------------------------------
# Rule model
# --------------------------------------------------------------------------

def parse_rule(rule):
    """Return (tool, specifier or None), or None for a string that is no rule."""
    match = _RULE.match(rule) if isinstance(rule, str) else None
    if not match:
        return None
    return match.group(1), match.group(2)


def _glob_regex(glob):
    out = []
    i, n = 0, len(glob)
    while i < n:
        char = glob[i]
        at_segment_start = i == 0 or glob[i - 1] == "/"
        if char == "*":
            if glob.startswith("**/", i) and at_segment_start:
                out.append("(?:[^/]+/)*")
                i += 3
                continue
            if glob.startswith("**", i) and at_segment_start and i + 2 == n:
                out.append(".*")
                i += 2
                continue
            while i < n and glob[i] == "*":
                i += 1
            out.append("[^/]*")
            continue
        if char == "?":
            out.append("[^/]")
        elif char == "[":
            end = glob.find("]", i + 2)
            if end == -1:
                out.append(re.escape(char))
            else:
                body = glob[i + 1:end]
                if body[0] in "!^":
                    body = "^" + body[1:]
                out.append("[" + body.replace("\\", "\\\\") + "]")
                i = end
        else:
            out.append(re.escape(char))
        i += 1
    return "".join(out)


def _path_rule_matches(spec, relpath, root):
    target = (Path(root) / relpath).as_posix()
    if spec.startswith("//"):
        prefix, glob = "", spec[1:]
    elif spec.startswith("~/"):
        prefix, glob = Path.home().as_posix(), spec[1:]
    else:
        if spec.startswith("./"):
            spec = spec[2:]
        prefix, glob = Path(root).as_posix(), "/" + spec.lstrip("/")
    if glob.endswith("/"):
        glob += "**"
    return re.fullmatch(re.escape(prefix) + _glob_regex(glob), target) is not None


def _file_rule_covers(rule_tool, tool):
    return rule_tool == tool or (rule_tool == "Edit" and tool in FILE_EDIT_TOOLS)


def _bash_parts(command):
    parts = [p.strip() for p in re.split(r"&&|\|\||[;|\n]", command)]
    return [command.strip()] + [p for p in parts if p]


def _bash_rule_matches(spec, command):
    if spec.endswith(":*"):
        prefix = spec[:-2].rstrip()
        return command == prefix or command.startswith(prefix + " ")
    if "*" not in spec:
        return command == spec.strip()
    if spec.endswith(" *") and command == spec[:-2].rstrip():
        return True
    pattern = ".*".join(re.escape(piece) for piece in spec.split("*"))
    return re.fullmatch(pattern, command, re.S) is not None


def denying_rules(rules, tool, target, root=REPO_ROOT):
    """Rules in ``rules`` that deny ``tool`` on ``target``.

    ``target`` is a repository-relative path for file tools and a command line
    for Bash. An empty result means the attempt is not denied.
    """
    hits = []
    for rule in rules:
        parsed = parse_rule(rule)
        if parsed is None:
            continue
        rule_tool, spec = parsed
        if tool == "Bash":
            if rule_tool != "Bash":
                continue
            if spec is None or any(_bash_rule_matches(spec, part) for part in _bash_parts(target)):
                hits.append(rule)
        elif _file_rule_covers(rule_tool, tool):
            if spec is None or _path_rule_matches(spec.strip(), target, root):
                hits.append(rule)
    return hits


def deny_rules_from_text(text):
    """The ``permissions.deny`` list of a settings file; raises on bad JSON."""
    data = json.loads(text)
    deny = data.get("permissions", {}).get("deny", []) if isinstance(data, dict) else []
    return [rule for rule in deny if isinstance(rule, str)]


def working_tree_deny_rules(root=REPO_ROOT):
    return deny_rules_from_text((Path(root) / SETTINGS_REL).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Git history
# --------------------------------------------------------------------------

def git(*args, root=REPO_ROOT):
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def settings_states(root=REPO_ROOT):
    """Deny-rule sets of ``.claude/settings.json`` over time, oldest first.

    One entry per commit on HEAD's history that changed the file, then the
    working tree as the last entry. Each entry is (label, rules); a state that
    cannot be read or parsed has no rules.
    """
    states = []
    shas = git("log", "--reverse", "--format=%H", "--", SETTINGS_REL, root=root).split()
    for sha in shas:
        proc = subprocess.run(
            ["git", "-C", str(root), "show", f"{sha}:{SETTINGS_REL}"],
            capture_output=True,
            text=True,
            check=False,
        )
        try:
            rules = deny_rules_from_text(proc.stdout) if proc.returncode == 0 else []
        except ValueError:
            rules = []
        states.append((sha[:12], rules))
    try:
        rules = working_tree_deny_rules(root)
    except (OSError, ValueError):
        rules = []
    states.append(("working tree", rules))
    return states


def commit_roles(sha, root=REPO_ROOT):
    """Values of the ``Role:`` trailer lines of a commit message."""
    body = git("show", "-s", "--format=%B", sha, root=root)
    return [m.group(1).strip() for m in re.finditer(r"(?mi)^Role:[ \t]*(.+)$", body)]


def commits_touching(path, root=REPO_ROOT):
    return git("rev-list", "--full-history", "HEAD", "--", path, root=root).split()


def changed_paths(sha, root=REPO_ROOT):
    """Repository-relative paths a commit adds, changes or deletes."""
    out = git(
        "-c", "core.quotePath=false",
        "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", sha,
        root=root,
    )
    return [line for line in out.splitlines() if line]


def path_in_globs(relpath, globs):
    """True when ``relpath`` matches one of a ticket's ``allowed_paths`` globs."""
    for glob in globs:
        glob = glob.strip().strip("'\"")
        if glob.startswith("./"):
            glob = glob[2:]
        if glob.endswith("/"):
            glob += "**"
        if re.fullmatch(_glob_regex(glob.lstrip("/")), relpath):
            return True
    return False


# --------------------------------------------------------------------------
# Ticket frontmatter
# --------------------------------------------------------------------------

def _frontmatter(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields, key = {}, None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        top = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if top:
            key, value = top.group(1), top.group(2).strip()
            if value.startswith("[") and value.endswith("]"):
                fields[key] = [v.strip() for v in value[1:-1].split(",") if v.strip()]
            elif value:
                fields[key] = value
            else:
                fields[key] = []
        elif key and isinstance(fields.get(key), list):
            item = re.match(r"^\s*-\s+(.*)$", line)
            if item:
                fields[key].append(item.group(1).strip())
    return fields


def ticket_file(ref, root=REPO_ROOT):
    """(repository-relative path, frontmatter) of the ticket named by a W1 id or ticket id."""
    for path in sorted((Path(root) / ".tickets").glob("*.md")):
        fields = _frontmatter(path)
        if ref in (fields.get("wbs_id"), fields.get("id")):
            return path.relative_to(root).as_posix(), fields
    return None


def ticket(wbs_id, root=REPO_ROOT):
    """Frontmatter of the ticket whose ``wbs_id`` is ``wbs_id``, or None."""
    found = ticket_file(wbs_id, root)
    return found[1] if found else None


def w1_05_has_landed(root=REPO_ROOT):
    """W1-05 (dogfood switch-over) retires the interim guardrails when it closes."""
    fields = ticket("W1-05", root)
    return bool(fields) and fields.get("status") == "closed"


def w1_05_landing_commit(root=REPO_ROOT):
    """The first commit in which the W1-05 ticket is closed, or None."""
    found = ticket_file("W1-05", root)
    if not found:
        return None
    relpath = found[0]
    for sha in git("log", "--reverse", "--format=%H", "--", relpath, root=root).split():
        proc = subprocess.run(
            ["git", "-C", str(root), "show", f"{sha}:{relpath}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and re.search(r"(?m)^status:\s*closed\s*$", proc.stdout):
            return sha
    return None


def trailer_values(message, key):
    """Values of the ``<key>:`` trailer lines of a commit message."""
    return [
        m.group(1).strip()
        for m in re.finditer(rf"(?mi)^{re.escape(key)}:[ \t]*(.+)$", message)
    ]


def interim_commits(root=REPO_ROOT):
    """(sha, message) of each commit on HEAD's history up to the one that lands W1-05.

    While W1-05 is open that is every commit reachable from HEAD.
    """
    tip = w1_05_landing_commit(root) or "HEAD"
    out = git("log", "--format=%H%x1f%B%x1e", tip, root=root)
    commits = []
    for record in out.split("\x1e"):
        if "\x1f" in record:
            sha, message = record.strip("\n").split("\x1f", 1)
            commits.append((sha, message))
    return commits
