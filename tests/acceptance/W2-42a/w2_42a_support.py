"""W2-42a's acceptance support: the tree under test, the five-rule hook run as Claude Code runs it, the product's
write parser and read judge, and the fixtures (DEC-1040 item 2, DEC-1028 item 4, DEC-958).

Every case judges this worktree's own code: the tests run with ``PYTHONPATH=<this tree>/src`` (the README's command),
and the hook's subprocess is given the same ``PYTHONPATH``, as the pinned judge gives it after re-pin window 2.
"""
from __future__ import annotations

import contextlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
HOOK = os.path.join(HERE, "fixtures", "hook", "pretooluse.py")
REFUSALS = os.path.join(HERE, "fixtures", "refusals.json")
PLANTED = os.path.join(HERE, "fixtures", "planted.json")
MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
EVIDENCE = os.path.join(REPO, "docs", "changes", "W2-42a-evidence.md")

UNRESOLVABLE = "/<guard-unresolvable>"  # gov.guard.decide._UNRESOLVABLE, the parser's sentinel today
SUFFIX = " (DEC-953 item 2)"
REVIEWERS = ("independent-auditor", "independent-reviewer", "reviewer", "auditor")
REVIEW_PATHS = ("docs/probes/", "docs/audit/", "docs/assessment/", ".gov-runtime/scratch/review/",
                ".gov-runtime/scratch/audit/")
# The reasons of the hook's two write rules (rule 1, acceptance tests; rule 5, reviewers), without the suffix.
RULE1 = ("a command that may write the acceptance tests, which only the independent test designer writes",
         "only the independent test designer writes the acceptance tests (MR-3)")
RULE5 = ("a reviewer or auditor runs only commands whose writes can be read, and writes only its own review or "
         "audit record",
         "a reviewer or auditor writes only its own review or audit record (docs/probes/, docs/audit/, "
         "docs/assessment/), its own scratch, or /tmp")
CODE = re.compile(r"(?<![\w/.-])(python[\d.]*|perl|node|ruby|uv|runpy)(?![\w-])")
_SESSION = ("TMPDIR", "GOV_ROLE", "GOV_TICKET", "CLAUDE_PROJECT_DIR", "GOV_HEAVY_SLOT")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def refusals():
    return load(REFUSALS)["refusals"]


def planted():
    rows = load(PLANTED)["planted"]
    return [dict(r, input=rooted(r["input"], REPO)) for r in rows]


def rooted(value, root):
    if isinstance(value, str):
        return value.replace("{ROOT}", root)
    if isinstance(value, dict):
        return {k: rooted(v, root) for k, v in value.items()}
    return value


# -- the five-rule hook, as Claude Code runs it ------------------------------------------------------------------------

def run_hook(tool, tool_input, cwd, root, role, agent_type=None, tmpdir=None, ticket=None):
    """The hook's answer: ``(decision, reason, exit code)``. Event JSON on stdin; the session's role, ticket, project
    folder and TMPDIR in its environment; this tree's ``src`` on ``PYTHONPATH``. No output and exit 0 is "allow";
    exit 2 is a refusal by an error (the hook fails closed), reason its standard error."""
    env = {k: v for k, v in os.environ.items() if k not in _SESSION and k != "PYTHONPATH"}
    env.update(PYTHONPATH=SRC, GOV_ROLE=role, CLAUDE_PROJECT_DIR=root, PYTHONDONTWRITEBYTECODE="1")
    if ticket:
        env["GOV_TICKET"] = ticket
    if tmpdir:
        env["TMPDIR"] = tmpdir
    event = {"session_id": "w2-42a-acceptance", "hook_event_name": "PreToolUse", "tool_name": tool,
             "tool_input": tool_input, "cwd": cwd, "agent_type": agent_type}
    p = subprocess.run(["python3", HOOK], input=json.dumps(event), capture_output=True, text=True, env=env,
                       cwd=cwd if os.path.isdir(cwd) else root, timeout=120)
    if p.returncode == 2:
        return "deny", "ERROR: " + p.stderr[-1500:], 2
    if p.returncode != 0:
        return "error", f"exit {p.returncode}: " + p.stderr[-1500:], p.returncode
    if not p.stdout.strip():
        return "allow", "", 0
    out = json.loads(p.stdout)["hookSpecificOutput"]
    return out["permissionDecision"], out["permissionDecisionReason"], 0


def write_rule_reasons(role):
    """The reasons a planted write of this role is refused by: rule 5 for a reviewer, rule 1 otherwise."""
    return tuple(r + SUFFIX for r in (RULE5 if role in REVIEWERS else RULE1))


# -- the product's write parser and read judge ---------------------------------------------------------------------

@contextlib.contextmanager
def session_env(tmpdir=None, **values):
    """The process environment as a session's: its TMPDIR (or none) and the given variables; the rest unset."""
    saved = {k: os.environ.get(k) for k in set(_SESSION) | set(values)}
    try:
        for k in _SESSION:
            os.environ.pop(k, None)
        if tmpdir:
            os.environ["TMPDIR"] = tmpdir
        for k, v in values.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def parse(command, cwd):
    """The product's write parser as gov.guard exposes it today: the targets, or None for a read-only command."""
    from gov.guard.decide import _extract_bash_write_targets
    return _extract_bash_write_targets(command, cwd)


def real(*parts):
    return os.path.realpath(os.path.join(*parts))


def parser_caught(row, root):
    """Whether the product's parser catches a planted Bash write (as for the five-rule hook's rules 1 and 5): a
    target it cannot resolve, a target in an acceptance folder (rule 1), or, for a reviewer, a target outside /tmp and
    its record paths (rule 5). Judged with no session variables and the main tree's path as ``root``."""
    command = rooted(row["input"]["command"], root)
    with session_env():
        got = parse(command, root)
    if not got:
        return False
    if UNRESOLVABLE in got:
        return True
    if row["role"] in REVIEWERS:
        def recorded(t):
            rel = os.path.relpath(t, os.path.realpath(root))
            inside = not rel.startswith("..")
            return (inside and any(rel.startswith(p) for p in REVIEW_PATHS)) or (
                not inside and (t == "/tmp" or t.startswith("/tmp/")))
        return not all(recorded(t) for t in got)
    return any("/tests/acceptance/" in t + "/" for t in got)


def shell_only(row):
    """A planted Bash case that holds no inline or file code of another language: the parser's own ground."""
    return row["tool"] == "Bash" and not CODE.search(row["input"]["command"])


def project(tmp_path, roles=("research", "engineer")):
    """A project with one evaluation set measuring ``roles``, whose hidden part holds a file; returns its root."""
    root = tmp_path / "proj"
    (root / "governance" / "project").mkdir(parents=True)
    (root / "governance" / "project" / "path-map.yaml").write_text(
        "evaluation_sets:\n  w242a:\n    visible: [\"docs/visible.md\"]\n"
        "    hidden: [\"fixtures/evaluation/w242a/hidden/**\"]\n"
        f"    measures:\n      roles: [{', '.join(roles)}]\n")
    (root / "fixtures" / "evaluation" / "w242a" / "hidden").mkdir(parents=True)
    (root / "fixtures" / "evaluation" / "w242a" / "hidden" / "q01.txt").write_text("hidden\n")
    (root / "docs").mkdir()
    (root / "docs" / "DECISION_REGISTER.md").write_text("".join(f"line {i}\n" for i in range(1, 40)))
    (root / "docs" / "visible.md").write_text("visible\n")
    return str(root)


def judge(command, root, cwd=None, role="research"):
    """The product's read judge as gov.guard exposes it today (``policy_refusal``): why a Bash call is refused to a
    session of ``role`` that the project's evaluation set measures, or ``""``."""
    from gov.guard.reads import policy_refusal
    return policy_refusal("Bash", {"command": command}, root, cwd or root, role, None)


def refusal_texts():
    from gov.guard import reads
    return reads.RUNTIME_REFUSAL, reads.SECRET_REFUSAL, reads.HIDDEN_REFUSAL


if __name__ == "__main__":  # a quick look: python3 w2_42a_support.py
    print(REPO, SRC, HOOK, file=sys.stderr)
