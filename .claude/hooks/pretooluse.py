#!/usr/bin/env python3
"""This repository's own PreToolUse guard while the Gov OS is being built (owner, DEC-953 item 2).

It keeps exactly five rules and nothing else (DEC-953 item 2, DEC-954):
  1. the implementer never writes acceptance tests: only the independent test designer writes tests/acceptance/**
     (MR-3, DEC-906);
  2. no reads of the hidden half of an evaluation set (by the sessions it measures, DEC-820 (d)), in this tree and
     in every other worktree and run clone of this repository (W2-84's fix, DEC-954 Q9b), or of the held-out
     material (every role, DEC-820 (b));
  5. independent reviewers and auditors write only their own outcomes: review and audit records under docs/probes/,
     docs/audit/ and docs/assessment/, their own scratch under .gov-runtime/scratch/review/ or /audit/, and /tmp;
     never code, tests, tickets, records, handovers or anything else (DEC-954);
  3. no reads of secrets or keys (every role, DEC-820 (a));
  4. no installs without the owner: an install asks the owner only in the CTO's own session (the orchestrator on the
     coordination ticket W2-00) and is refused in every other, leads included, which escalate it (DEC-957); sudo is
     refused.
It reuses the product's own checks (gov.guard.reads, heldout, install, decide), imported from the pinned judge that
runs this file. The product's full guard (template/governance/kernel/hooks/pretooluse.py, src/gov/guard/) stays built
and tested; it is not wired here until the Gov OS is whole. Fail closed: an error or the 20-second deadline refuses.
"""
import json
import os
import signal
import sys

import glob
import re
import subprocess

ACCEPTANCE = "tests/acceptance/"
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
TEST_DESIGNER = "independent-test-designer"
REVIEWERS = ("independent-auditor", "independent-reviewer", "reviewer", "auditor")
REVIEW_PATHS = ("docs/probes/", "docs/audit/", "docs/assessment/", ".gov-runtime/scratch/review/",
                ".gov-runtime/scratch/audit/")
RUNS = os.path.expanduser("~/gov-os-runs")
CTO_WBS = "W2-00"  # the coordination ticket whose orchestrator session is the CTO
# Inline interpreter code, which the write parser cannot see into (python -c, perl -e/-i, node -e, ruby -e).
INLINE_CODE = re.compile(r"\b(python3?|perl|node|ruby)\s+(-\w*\s+)*-[cei]\b")


def tree_roots(root):
    """This tree, every worktree of its repository, and the run clones under ~/gov-os-runs (W2-84's every tree)."""
    roots = [os.path.realpath(root)]

    def worktrees(repo):
        try:
            out = subprocess.run(["git", "-C", repo, "worktree", "list", "--porcelain"], capture_output=True,
                                 text=True, timeout=5).stdout
            return [os.path.realpath(line[9:]) for line in out.splitlines() if line.startswith("worktree ")]
        except Exception:
            return []

    roots += worktrees(root)
    # a run clone's origin, when it is a local repository, and that repository's worktrees
    try:
        origin = subprocess.run(["git", "-C", root, "remote", "get-url", "origin"], capture_output=True, text=True,
                                timeout=5).stdout.strip()
        if origin.startswith("file://"):
            origin = origin[7:]
        if origin.startswith("/") and os.path.isdir(origin):
            roots += [os.path.realpath(origin)] + worktrees(origin)
    except Exception:
        pass
    for pattern in ("*/.git", "*/*/.git", "*/*/*/.git", "*/*/*/*/.git"):
        roots += [os.path.realpath(os.path.dirname(g)) for g in glob.glob(os.path.join(RUNS, pattern))]
    return list(dict.fromkeys(roots))


def review_may_write(path, root, cwd):
    """Rule 5: a reviewer's or auditor's write lands only in its record paths, its own scratch, or /tmp."""
    if not isinstance(path, str) or not path:
        return False
    full = os.path.realpath(os.path.join(cwd, os.path.expanduser(path)))
    for tree in tree_roots(root):  # inside any tree of this repository: only the record paths
        rel = os.path.relpath(full, tree)
        if rel == "." or not rel.startswith(".."):
            return any(rel.startswith(p) for p in REVIEW_PATHS)
    return full == "/tmp" or full.startswith("/tmp/")


def answer(decision, reason):
    out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision,
                                  "permissionDecisionReason": reason + " (DEC-953 item 2)"}}
    sys.stdout.write(json.dumps(out))
    sys.exit(0)


def deadline(signum, frame):
    answer("deny", "the guard could not decide in 20 seconds, so the call is refused")


def under_acceptance(path, root, cwd):
    if not isinstance(path, str) or not path:
        return False
    full = os.path.realpath(os.path.join(cwd, os.path.expanduser(path)))
    rel = os.path.relpath(full, os.path.realpath(root))
    return rel == ACCEPTANCE.rstrip("/") or rel.startswith(ACCEPTANCE)


def main():
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(20)
    data = json.loads(sys.stdin.read() or "{}")
    tool = data.get("tool_name") or ""
    tin = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    cwd = data.get("cwd") or root
    role = (os.environ.get("GOV_ROLE") or "").strip()
    ticket = os.environ.get("GOV_TICKET")
    from gov.guard import reads
    from gov.guard.heldout import load_held_out, names_held_out
    acting = reads.acting_role(role, data.get("agent_type"))

    # Rule 2, the held-out material: every role, any tool that names or reaches it.
    if names_held_out(tool, tin, root, cwd, load_held_out(root)):
        answer("deny", "the call names or reaches the held-out material")

    # Rules 2 and 3, the hidden half and secrets: the product's read judge with only these parts.
    hidden = []
    for r in dict.fromkeys((role, acting)):
        hidden += reads._hidden(root, r, ticket)
    parts = [reads._Part(t, hidden, reads.HIDDEN_REFUSAL) for t in tree_roots(root)] if hidden else []
    why = reads._Judge(root, parts).tool(tool, tin, cwd)
    if why:
        answer("deny", why)

    # Rule 5, reviewers and auditors write only their own outcomes.
    if acting in REVIEWERS or role in REVIEWERS:
        targets = None
        if tool in WRITE_TOOLS:
            targets = [tin.get("file_path") or tin.get("notebook_path")]
        elif tool == "Bash":
            from gov.guard.decide import _UNRESOLVABLE, _extract_bash_write_targets
            # The parser answers None for a read-only command, and a list of targets (the sentinel among them
            # for a write it cannot resolve) otherwise (DEC-958 fix: None was read as "cannot read").
            targets = _extract_bash_write_targets(tin.get("command") or "", cwd)
            if targets and _UNRESOLVABLE in targets:
                answer("deny", "a reviewer or auditor runs only commands whose writes can be read, and writes only "
                               "its own review or audit record")
        if targets and not all(review_may_write(t, root, cwd) for t in targets):
            answer("deny", "a reviewer or auditor writes only its own review or audit record (docs/probes/, "
                           "docs/audit/, docs/assessment/), its own scratch, or /tmp")

    # Rule 1, acceptance tests: written only by the independent test designer.
    if acting != TEST_DESIGNER and role != TEST_DESIGNER:
        targets = []
        if tool in WRITE_TOOLS:
            targets = [tin.get("file_path") or tin.get("notebook_path")]
        elif tool == "Bash":
            from gov.guard.decide import _UNRESOLVABLE, _extract_bash_write_targets
            command = tin.get("command") or ""
            found = _extract_bash_write_targets(command, cwd)
            # None is a read-only command (running or reading the tests is open, DEC-820); a write the parser
            # cannot resolve, or inline interpreter code, is refused only when it names the acceptance tests.
            unreadable = (found is not None and _UNRESOLVABLE in found) or INLINE_CODE.search(command)
            if unreadable and ACCEPTANCE in command:
                answer("deny", "a command that may write the acceptance tests, which only the "
                               "independent test designer writes")
            targets = [t for t in (found or []) if t != _UNRESOLVABLE]
        if any(under_acceptance(t, root, cwd) for t in targets):
            answer("deny", "only the independent test designer writes the acceptance tests (MR-3)")

    # Rule 4, installs.
    if tool == "Bash":
        from gov.guard.install import has_install, has_sudo
        command = tin.get("command") or ""
        if has_sudo(command):
            answer("deny", "sudo is refused to every session")
        if has_install(command):
            # Only the CTO's own session asks the owner: the orchestrator role on the coordination ticket (W2-00).
            # Every other session, leads (orchestrator on a ticket of their own) included, is refused (DEC-957).
            cto = role == "orchestrator" and acting == "orchestrator" and reads._ticket(root, ticket)[1] == CTO_WBS
            if cto:
                answer("ask", "an install needs the owner's approval")
            answer("deny", "installs are refused here: raise the install as a P1 escalation to the CTO, who asks "
                           "the owner")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # fail closed
        sys.stderr.write(f"guard (DEC-953): could not decide: {exc}; refused\n")
        sys.exit(2)
