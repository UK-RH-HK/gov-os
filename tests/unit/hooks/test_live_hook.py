"""This repository's live five-rule hook, ``.claude/hooks/pretooluse.py`` (DEC-953 item 2), in the full suite
(D-4, DEC-1061 decision 5; G-9). Until this file its cases lived only in the CTO's scratch:
``drafts/act-guard-fix-4/test_guard_fix_4.py`` (ACT-GUARD-FIX-4: rules 1 and 5 judge only the writes that resolve,
G-1 and G-2; ``rm`` free but for the catastrophic, DEC-1050 (8)), ``drafts/g14/test_g14.py`` (G-14's ``role_paths``,
live since ``4edd196c``, DEC-1052, DEC-1059) and ``tools/guard4_check.py`` (the two-minute check). Cut to
representative cases: every rule and every form class those files name stays, with one or a few forms each.

The hook under test is this tree's own (``<tree>/.claude/hooks/pretooluse.py``) and the product code it imports is
this tree's ``src`` (``PYTHONPATH``), run as Claude Code runs it: event JSON on standard input, ``GOV_ROLE``,
``GOV_TICKET`` and ``CLAUDE_PROJECT_DIR`` in the environment, a refusal as exit 2 or a ``deny`` decision.
``GOV_LIVE_HOOK_PY`` names another interpreter to run it with ``-E``, as the registered line runs the pin.

Most cases run in planted projects under the run's temp folder (a path map with an evaluation set, a held-out list
and the ``role_paths:`` section, tickets, a worktree). The engineer's tree ``~/gov-os-worktrees/W2-G14T`` is only
named, never made or read. The cases of a ``.git`` and of a removed worktree's fallback use this tree itself; the
hook only judges each call, it runs none.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

TREE = Path(__file__).resolve().parents[3]
HOOKS = TREE / ".claude" / "hooks"
HOOK = HOOKS / "pretooluse.py"
SRC = TREE / "src"
PIN = os.environ.get("GOV_LIVE_HOOK_PY")
WORKTREES = os.path.realpath(os.path.expanduser("~/gov-os-worktrees"))
ENG = WORKTREES + "/W2-G14T"  # named only
E, TD, O, A = "engineer", "independent-test-designer", "orchestrator", "independent-auditor"
T = "tests/acceptance/W2-G14T/test_a.py"
HIDDEN = "fixtures/evaluation/x/hidden/q01.yaml"
REVIEWS = ".gov-runtime/scratch/orchestrator/reviews"
P = "<project>"  # the planted project's path, filled in per case
UNSET = "GOV_LIVE_HOOK_UNSET"

PATCHED = """role_paths:
  engineer:
    reads_denied: ["{ticket_tests}"]
  independent-test-designer:
    reads_denied: ["{ticket_impl}"]
"""
MALFORMED = """role_paths:
  engineer: ["tests/acceptance/**"]
"""
CONFLICTED = PATCHED + """<<<<<<< HEAD
decision_register: docs/DECISION_REGISTER.md
=======
decision_register: docs/OTHER.md
>>>>>>> w2/other
"""
CONFLICT_IN_BLOCK = """<<<<<<< HEAD
role_paths:
  engineer:
    reads_denied: ["tests/acceptance/**"]
=======
role_paths:
  engineer:
    reads_denied: ["{ticket_tests}"]
>>>>>>> w2/other
"""
EVALUATION_SETS = """evaluation_sets:
  x:
    visible: ["docs/x-visible.md"]
    hidden: ["fixtures/evaluation/x/hidden/**"]
    measures:
      roles: [engineer]
"""


def _ticket(ident, wbs, role, status="in_progress", paths=("src/gov/other.py",)):
    lines = "".join(f"- {p}\n" for p in paths)
    return f"---\nid: {ident}\nstatus: {status}\nwbs_id: {wbs}\nrole: {role}\nallowed_paths:\n{lines}---\n# {wbs}\n"


TICKETS = {
    "DAEO-g14t": _ticket("DAEO-g14t", "W2-G14T", E, paths=(
        "src/gov/g14/impl.py", "template/g14/*.yaml", "tests/unit/test_g14t*", "tests/unit/g14t_support.py",
        "tests/unit/__init__.py", "tests/conftest.py", "tests/unit/g14/conftest.py", "docs/changes/W2-G14T-evidence.md")),
    "DAEO-g14u": _ticket("DAEO-g14u", "W2-G14U", E, status="closed", paths=("src/gov/g14u.py",)),
    "DAEO-g14w": _ticket("DAEO-g14w", "W2-G14W", E, status="closed", paths=("src/gov/g14w.py",)),
    "DAEO-cto0": _ticket("DAEO-cto0", "W2-00", O, paths=("governance/**",)),
    "DAEO-lead": _ticket("DAEO-lead", "W2-L1", O, paths=("src/gov/lead.py",)),
}


def _git_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_AUTHOR_NAME="live-hook", GIT_AUTHOR_EMAIL="live-hook@x", GIT_COMMITTER_NAME="live-hook",
               GIT_COMMITTER_EMAIL="live-hook@x", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
    return env


def _plant(path: Path, section: str, *, held_out: str | None = None, worktree: bool = False) -> str:
    """A planted project: the path map (an evaluation set and ``section``), a held-out list naming a folder outside
    it, the tickets, and the link sources of G-14's engineer rule: W2-G14U's case revised for W2-G14T under its
    ``Task:`` (i), and one revised in W2-G14T's tests branch under W2-G14U's own (ii), merged ``--no-ff``."""
    root = str(path)
    held = held_out if held_out is not None else f"held_out_paths:\n  - {path.parent / (path.name + '-held')}\n"
    files = {
        "governance/project/path-map.yaml": "state_class: AUTHORITATIVE\nnamespaces: {}\n" + EVALUATION_SETS + section,
        "governance/project/held-out.yaml": held,
        "README.md": "planted\n", "docs/x-visible.md": "visible\n", HIDDEN: "q: hidden\n",
        ".env": "TOKEN=planted\n", "deploy/server.key": "planted\n",
        T: "x = 1\n", "src/gov/g14/impl.py": "x = 1\n", "tests/acceptance/W1-01/test_x.py": "x = 1\n",
        "tests/acceptance/W2-G14U/test_u.py": "x = 1\n", "tests/acceptance/W2-G14U/test_v.py": "x = 1\n",
        "tests/acceptance/W2-G14U/test_w.py": "x = 1\n",
    }
    files.update({f".tickets/{k}.md": v for k, v in TICKETS.items()})
    for rel, text in files.items():
        (path / rel).parent.mkdir(parents=True, exist_ok=True)
        (path / rel).write_text(text, encoding="utf-8")
    env = _git_env()

    def git(*args):
        subprocess.run(["git", "-C", root, *args], check=True, env=env, capture_output=True)
    subprocess.run(["git", "init", "-q", "-b", "w2/integrate", root], check=True, env=env)
    git("add", "-A", "--", ".", ":!tests/acceptance/W2-G14U/test_u.py", ":!tests/acceptance/W2-G14U/test_v.py")
    git("commit", "-q", "-m", "base", "--trailer", "Task: DAEO-sdxk", "--trailer", "Role: orchestrator")
    git("add", "tests/acceptance/W2-G14U/test_u.py")
    git("commit", "-q", "-m", "W2-G14T: W2-G14U's case revised", "--trailer", "Task: DAEO-g14t",
        "--trailer", "Role: independent-test-designer", "--trailer", "Rewrite-Reason: W2-G14T KPI 1")
    git("checkout", "-q", "-b", "w2/W2-G14T-tests")
    git("add", "tests/acceptance/W2-G14U/test_v.py")
    git("commit", "-q", "-m", "W2-G14U: a case revised to W2-G14T's cache", "--trailer", "Task: DAEO-g14u",
        "--trailer", "Role: independent-test-designer")
    git("checkout", "-q", "w2/integrate")
    git("merge", "-q", "--no-ff", "--no-edit", "w2/W2-G14T-tests")
    if worktree:
        git("worktree", "add", "-q", "-b", "w2/live-hook-wt", root + "-wt")
    return os.path.realpath(root)


@pytest.fixture(scope="module")
def projects(tmp_path_factory):
    base = tmp_path_factory.mktemp("live-hook")
    held = base / "patched-held"
    held.mkdir()
    (held / "answers.txt").write_text("planted\n", encoding="utf-8")
    return {
        "patched": _plant(base / "patched", PATCHED, worktree=True),
        "absent": _plant(base / "absent", ""),
        "malformed": _plant(base / "malformed", MALFORMED),
        "conflicted": _plant(base / "conflicted", CONFLICTED),
        "conflict_in_block": _plant(base / "conflict_in_block", CONFLICT_IN_BLOCK),
        "broken_held_out": _plant(base / "broken_held_out", "", held_out="held_out_paths: not-a-list\n"),
    }


def _env(extra=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    if not PIN:
        env["PYTHONPATH"] = str(SRC)
    env.update(extra or {})
    return env


def _py():
    return [PIN, "-E"] if PIN else [sys.executable]


def hook(root, role, tool, tin, *, cwd=None, agent=None, ticket="DAEO-g14t"):
    """The hook's decision on one call: ("deny" | "ask" | "allow", reason)."""
    event = {"tool_name": tool, "tool_input": tin, "cwd": cwd or root, "session_id": "live-hook",
             "hook_event_name": "PreToolUse"}
    if agent:
        event["agent_type"] = agent
    env = _env({"GOV_ROLE": role, "GOV_TICKET": ticket, "CLAUDE_PROJECT_DIR": root})
    env.pop(UNSET, None)
    p = subprocess.run(_py() + [str(HOOK)], input=json.dumps(event), capture_output=True, text=True, env=env,
                       timeout=60)
    if p.returncode == 2:
        return "deny", p.stderr
    assert p.returncode == 0, p.stderr
    if not p.stdout.strip():
        return "allow", ""
    out = json.loads(p.stdout)["hookSpecificOutput"]
    return out["permissionDecision"], out["permissionDecisionReason"]


def b(command):
    return {"command": command}


def _fill(value, root):
    if isinstance(value, str):
        return value.replace(P, root)
    if isinstance(value, dict):
        return {k: _fill(v, root) for k, v in value.items()}
    return value


def check(root, cases):
    """Each (name, role, tool, input, want[, agent[, ticket]]) on ``root``; every mismatch named at once."""
    wrong = []
    for name, role, tool, tin, want, *more in cases:
        agent = more[0] if more else None
        ticket = more[1] if len(more) > 1 else "DAEO-g14t"
        got, why = hook(root, role, tool, _fill(tin, root), agent=agent, ticket=ticket)
        if got != want:
            wrong.append(f"{name}: want {want}, got {got} ({why.strip()[:300]})")
    assert not wrong, "\n".join(wrong)


# ---------------------------------------------------------------------------------------------------------------
# Rule 1: only the independent test designer writes the acceptance tests; what resolves is judged (G-1)
# ---------------------------------------------------------------------------------------------------------------

RULE_1 = {
    "file tools": [
        ("Write", E, "Write", {"file_path": f"{P}/{T}", "content": "x"}, "deny"),
        ("Edit by the orchestrator", O, "Edit", {"file_path": f"{P}/{T}", "old_string": "a", "new_string": "b"},
         "deny"),
        ("NotebookEdit", E, "NotebookEdit", {"notebook_path": f"{P}/tests/acceptance/W2-G14T/n.ipynb",
                                             "new_source": "x"}, "deny"),
    ],
    "the shell's own writes": [
        ("redirect", E, "Bash", b(f"echo x > {T}"), "deny"),
        ("tee", E, "Bash", b(f"echo x | tee {T}"), "deny"),
        ("sed -i", E, "Bash", b(f"sed -i s/a/b/ {T}"), "deny"),
        ("cp", E, "Bash", b(f"cp /tmp/x.py {T}"), "deny"),
        ("a heredoc into the tests", E, "Bash", b(f"cat > {T} <<'EOF'\nx\nEOF"), "deny"),
    ],
    "targets that resolve": [
        ("the command's own variable", E, "Bash", b("D=tests/acceptance/W2-G14T; cp /tmp/x $D/t.py"), "deny"),
        ("a literal loop", E, "Bash", b("for f in a b; do touch tests/acceptance/W2-G14T/$f.py; done"), "deny"),
        ("cd into the tests, then a relative write", E, "Bash", b("cd tests/acceptance/W2-G14T && touch t.py"),
         "deny"),
        ("inline Python with a literal path", E, "Bash", b(f"python3 -c \"open('{T}', 'w').write('x')\""), "deny"),
    ],
    "the test designer": [
        ("its Write", TD, "Write", {"file_path": f"{P}/{T}", "content": "x"}, "allow"),
        ("its redirect", TD, "Bash", b(f"echo x > {T}"), "allow"),
        ("the orchestrator acting as the test designer (a subagent)", O, "Write", {"file_path": f"{P}/{T}",
                                                                                  "content": "x"}, "allow", TD),
    ],
    "G-1: what does not resolve is let through": [
        ("a write through a substitution", E, "Bash", b("touch $(pwd)/tests/acceptance/W2-G14T/t.py"), "allow"),
        ("a variable the guard cannot resolve", E, "Bash", b("read D <<< tests; touch $D/acceptance/W2-G14T/t.py"),
         "allow"),
        ("perl is not read", E, "Bash", b(f"perl -i -pe s/a/b/ {T}"), "allow"),
        ("an unreadable command naming the tests", E, "Bash", b("python3 -c 'open(\"tests/acceptance/x\" ; ls"),
         "allow"),
    ],
    "code's writes into a tree of this repository": [
        ("inline Python into the project's worktree's tests", E, "Bash",
         b(f"python3 -c \"open('{P}-wt/{T}', 'w')\""), "deny"),
        ("inline Python into a scratch repository's tests in /tmp (row 81)", E, "Bash",
         b("python3 -c \"import os; os.makedirs('/tmp/gov-live-hook-repo/tests/acceptance/W1', exist_ok=True)\""),
         "allow"),
        ("a write after cd /tmp resolves outside every tree", E, "Bash",
         b(f"cd /tmp && python3 -c 'open(\"{T}\", \"w\")'"), "allow"),
    ],
}


@pytest.mark.parametrize("form", list(RULE_1))
def test_rule_1_only_the_test_designer_writes_the_acceptance_tests(projects, form):
    check(projects["patched"], RULE_1[form])


# ---------------------------------------------------------------------------------------------------------------
# Rule 5: reviewers and auditors write only their own records (G-2: what does not resolve is let through)
# ---------------------------------------------------------------------------------------------------------------

RULE_5 = {
    "code, tests and tickets refused": [
        ("Write to code", A, "Write", {"file_path": f"{P}/src/gov/x.py", "content": "x"}, "deny"),
        ("Write a unit test", A, "Write", {"file_path": f"{P}/tests/unit/test_x.py", "content": "x"}, "deny"),
        ("Edit a ticket", A, "Edit", {"file_path": f"{P}/.tickets/DAEO-g14t.md", "old_string": "a",
                                      "new_string": "b"}, "deny"),
        ("a lead's handover", A, "Write", {"file_path": f"{P}/.gov-runtime/scratch/lead/CHECKPOINT.md",
                                           "content": "x"}, "deny"),
    ],
    "the shell's writes that resolve into code": [
        ("redirect into code", A, "Bash", b("echo x > src/gov/x.py"), "deny"),
        ("its own variable resolving into code", A, "Bash", b("D=src/gov; touch $D/x.py"), "deny"),
    ],
    "its records allowed": [
        ("docs/probes", A, "Write", {"file_path": f"{P}/docs/probes/DAEO-x/PR-x.md", "content": "x"}, "allow"),
        ("docs/audit by Bash", A, "Bash", b("echo x > docs/audit/wave-2/report.md"), "allow"),
        ("/tmp", A, "Write", {"file_path": "/tmp/gov-live-hook-a.txt", "content": "x"}, "allow"),
    ],
    "the CTO's reviews folder": [
        ("its record", A, "Write", {"file_path": f"{P}/{REVIEWS}/e9-review.md", "content": "x"}, "allow"),
        ("makes the folder and writes its record", A, "Bash",
         b(f"mkdir -p {REVIEWS} && cat > {REVIEWS}/e9-review.md <<'EOF'\n# r\nEOF"), "allow"),
        ("deletes the folder", A, "Bash", b(f"rm -rf {REVIEWS}"), "deny"),
        ("out of it by ..", A, "Write", {"file_path": f"{P}/{REVIEWS}/../briefs/x.md", "content": "x"}, "deny"),
        ("a folder whose name starts with reviews", A, "Write", {"file_path": f"{P}/{REVIEWS}x/a.md",
                                                                 "content": "x"}, "deny"),
    ],
    "G-2 and the acting role": [
        ("a write through mktemp is let through", A, "Bash", b("B=$(mktemp -d); mkdir $B/r && echo x > $B/r/o"),
         "allow"),
        ("the subagent form into code", O, "Write", {"file_path": f"{P}/src/gov/x.py", "content": "x"}, "deny", A),
        ("the subagent form into reviews/", O, "Write", {"file_path": f"{P}/{REVIEWS}/e9.md", "content": "x"},
         "allow", A),
        ("an engineer's write into reviews/ is not rule 5's", E, "Write", {"file_path": f"{P}/{REVIEWS}/x.md",
                                                                          "content": "x"}, "allow"),
        ("an auditor reads code", A, "Read", {"file_path": f"{P}/src/gov/g14/impl.py"}, "allow"),
    ],
}


@pytest.mark.parametrize("form", list(RULE_5))
def test_rule_5_reviewers_write_only_their_records(projects, form):
    check(projects["patched"], RULE_5[form])


# ---------------------------------------------------------------------------------------------------------------
# Rules 2 and 3: the hidden half and the held-out material; secrets
# ---------------------------------------------------------------------------------------------------------------

RULES_2_AND_3 = {
    "the hidden half, to the role it measures": [
        ("Read in the project", E, "Read", {"file_path": f"{P}/{HIDDEN}"}, "deny"),
        ("cat in the project's worktree", E, "Bash", b(f"cat {P}-wt/{HIDDEN}"), "deny"),
        ("a role it does not measure", O, "Read", {"file_path": f"{P}/{HIDDEN}"}, "allow"),
        ("the visible half", E, "Read", {"file_path": f"{P}/docs/x-visible.md"}, "allow"),
    ],
    "the held-out material, to every role": [
        ("named by ls", O, "Bash", b(f"ls {P}-held"), "deny"),
        ("read by the test designer", TD, "Read", {"file_path": f"{P}-held/answers.txt"}, "deny"),
    ],
    "secrets, to every role": [
        ("Read .env", E, "Read", {"file_path": f"{P}/.env"}, "deny"),
        ("cat a key", O, "Bash", b("cat deploy/server.key"), "deny"),
    ],
}


@pytest.mark.parametrize("form", list(RULES_2_AND_3))
def test_rules_2_and_3_the_hidden_half_the_held_out_material_and_secrets(projects, form):
    check(projects["patched"], RULES_2_AND_3[form])


# ---------------------------------------------------------------------------------------------------------------
# Rule 4: installs ask only in the CTO's session; sudo refused
# ---------------------------------------------------------------------------------------------------------------

RULE_4 = [
    ("an engineer's pip install", E, "Bash", b("pip install requests"), "deny"),
    ("the CTO's (the orchestrator on W2-00)", O, "Bash", b("pip install requests"), "ask", None, "DAEO-cto0"),
    ("a lead's (the orchestrator on its ticket)", O, "Bash", b("npm install left-pad"), "deny", None, "DAEO-lead"),
    ("the CTO's engineer subagent", O, "Bash", b("pip install requests"), "deny", E, "DAEO-cto0"),
    ("sudo", O, "Bash", b("sudo ls"), "deny", None, "DAEO-cto0"),
]


@pytest.mark.parametrize("case", RULE_4, ids=[c[0] for c in RULE_4])
def test_rule_4_installs_and_sudo(projects, case):
    check(projects["patched"], [case])


# ---------------------------------------------------------------------------------------------------------------
# rm: free but for the catastrophic, refused to every role (DEC-1050 (8))
# ---------------------------------------------------------------------------------------------------------------

CATASTROPHIC = {  # each class: (role, command) forms; both roles across the classes
    "the filesystem's root and the home folder": [(O, "rm -rf /"), (E, "rm -rf ~"), (O, "rm -rf $HOME")],
    "the project's root and its tracked files": [(E, f"rm -rf {P}"), (O, "rm README.md")],
    "the folders that hold the trees and the scratch": [(E, "rm -rf ~/gov-os-worktrees/"), (O, "rm -rf /tmp")],
    "outside the project": [(E, "rm -f ~/.bashrc")],
    "a variable the guard cannot resolve, if it is empty": [(O, f"rm -rf \"${UNSET}\"/")],
    "inside another shell, a loop, or by its path": [
        (E, "bash -c 'rm -rf ~'"), (O, "for d in /tmp/gov-live-hook-a ~; do rm -rf $d; done"), (E, "/bin/rm -rf /")],
    "a command the scan cannot read (the crude reading)": [(O, "rm -rf / \"unclosed")],
}


@pytest.mark.parametrize("form", list(CATASTROPHIC))
def test_a_catastrophic_rm_is_refused(projects, form):
    root = projects["patched"]
    wrong = []
    for role, command in CATASTROPHIC[form]:
        got, why = hook(root, role, "Bash", b(_fill(command, root)))
        if not (got == "deny" and "catastrophic delete" in why):
            wrong.append(f"{command!r} as {role}: {got} ({why})")
    assert not wrong, "\n".join(wrong)


def test_a_repository_s_git_is_refused_outside_the_scratch_folders():
    if str(TREE).startswith("/tmp/"):
        pytest.skip("this tree is in /tmp, where a .git is scratch")
    for command in ("rm -rf .git", f"rm -rf {TREE}/.git/objects"):
        got, why = hook(str(TREE), E, "Bash", b(command))
        assert got == "deny" and ".git" in why, f"{command!r}: {got} ({why})"


HONEST = [
    "rm -f /tmp/gov-live-hook-x.json",
    "d=$(mktemp -d); echo x > $d/a; rm -rf \"$d\"",
    f"rm -rf \"${{{UNSET}:?}}\"/",
    "echo 'rm -rf /'; grep -rn 'rm -rf' docs | head -3; git rm --cached -n README.md",
    "rm -rf .gov-runtime/scratch/lead/none /tmp/gov-live-hook-repo/.git",
]


@pytest.mark.parametrize("command", HONEST)
def test_an_honest_rm_passes(projects, command):
    got, why = hook(projects["patched"], O, "Bash", b(command))
    assert got == "allow", f"{command!r}: {got} ({why})"


def test_rm_through_a_link_removes_the_link(projects, tmp_path):
    root = projects["patched"]
    link = tmp_path / "to-project"
    link.symlink_to(root)
    assert hook(root, O, "Bash", b(f"rm -f {link}"))[0] == "allow"
    got, why = hook(root, O, "Bash", b(f"rm -rf {link}/"))
    assert got == "deny" and "catastrophic delete" in why, why
    got, why = hook(root, O, "Bash", b(f"rm -f {link}/README.md"))
    assert got == "deny" and "tracked" in why, why


def test_a_removed_worktree_falls_back_to_the_hook_s_own_tree():
    """A session whose tree git cannot read: its scratch rm passes; the main tree is the hook file's tree's."""
    common = subprocess.run(["git", "-C", str(TREE), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            capture_output=True, text=True, check=True).stdout.strip()
    main = os.path.dirname(common.rstrip("/"))
    gone = WORKTREES + "/EMG-live-hook-removed"
    assert not os.path.exists(gone)
    for command in (f"rm -rf {gone}/pytest-of-x", "rm -f .gov-runtime/scratch/lead/x.exit"):
        got, why = hook(gone, E, "Bash", b(command), cwd=gone)
        assert got == "allow", f"{command!r}: {got} ({why})"
    got, why = hook(gone, E, "Bash", b(f"rm -f {main}/README.md"), cwd=gone)
    assert got == "deny" and "tracked" in why, why


def test_the_reason_is_plain(projects):
    root = projects["patched"]
    got, why = hook(root, O, "Bash", b(f"rm -rf \"${UNSET}\"/"))
    assert got == "deny" and "if a variable in it that the guard cannot resolve is empty" in why and ":?" in why
    got, why = hook(root, O, "Bash", b("rm README.md"))
    assert "main tree's tracked files" in why and "git rm" in why, why
    got, why = hook(root, O, "Bash", b("rm -f ~/.bashrc"))
    assert "outside the project" in why, why


# ---------------------------------------------------------------------------------------------------------------
# What the five rules lifted passes; the hook fails closed
# ---------------------------------------------------------------------------------------------------------------

LIFTED = [
    ("an engineer writes outside its ticket's paths", E, "Write", {"file_path": f"{P}/src/gov/other.py",
                                                                    "content": "x"}, "allow"),
    ("an engineer runs the acceptance tests", E, "Bash", b("PYTHONPATH=src python3 -m pytest -q tests/acceptance"),
     "allow"),
    ("a tool the guard does not know", O, "CronCreate", {"cron": "0 7 * * *", "prompt": "x"}, "allow"),
    ("a heredoc to /tmp whose text holds a redirect", E, "Bash",
     b("cat > /tmp/gov-live-hook-x.txt <<EOF\nif a > 1:\nEOF"), "allow"),
]


def test_what_the_five_rules_lifted_passes(projects):
    check(projects["patched"], LIFTED)


def test_an_unreadable_held_out_list_fails_closed(projects):
    root = projects["broken_held_out"]
    got, why = hook(root, O, "Read", {"file_path": root + "/README.md"})
    assert got == "deny", why


# ---------------------------------------------------------------------------------------------------------------
# G-14: role separation from the path map's role_paths: (DEC-1052, DEC-1059)
# ---------------------------------------------------------------------------------------------------------------

G14_REFUSED = [
    ("the engineer Reads its own test", E, "Read", {"file_path": f"{P}/{T}"}, "deny"),
    ("the engineer cats it", E, "Bash", b(f"cat {T}"), "deny"),
    ("the engineer Greps its folder", E, "Grep", {"pattern": "x", "path": f"{P}/tests/acceptance/W2-G14T"}, "deny"),
    ("the engineer reads it from git", E, "Bash", b(f"git show w2/W2-G14T-tests:{T}"), "deny"),
    ("the engineer reads it after a cd", E, "Bash", b("cd tests/acceptance && sed -n 1,9p W2-G14T/test_a.py"),
     "deny"),
    ("a lead's subagent acting as the engineer", O, "Read", {"file_path": f"{P}/{T}"}, "deny", E),
    ("the test designer Reads the engineer's code", TD, "Read", {"file_path": ENG + "/src/gov/g14/impl.py"}, "deny"),
    ("the test designer reads the engineer's branch", TD, "Bash", b("git show w2/W2-G14T:src/gov/g14/impl.py"),
     "deny"),
    ("the test designer reads the engineer's new unit test ((c3))", TD, "Bash",
     b(f"grep -n def {ENG}/tests/unit/test_g14t_x.py"), "deny"),
    ("an orchestrator acting as the test designer", O, "Read", {"file_path": ENG + "/src/gov/g14/impl.py"}, "deny",
     TD),
]
G14_PASSED = {
    "the engineer's near misses": [
        ("another ticket's test", E, "Read", {"file_path": f"{P}/tests/acceptance/W1-01/test_x.py"}, "allow"),
        ("it lists and runs its tests", E, "Bash", b("ls tests/acceptance/W2-G14T && pytest -q "
                                                     "tests/acceptance/W2-G14T"), "allow"),
        ("a pattern naming the tests, a search from above", E, "Bash",
         b("grep -rn tests/acceptance/W2-G14T src/; grep -r foo tests/"), "allow"),
        ("inline code is not guessed at", E, "Bash", b(f"python3 -c \"print(open('{T}').read())\""), "allow"),
    ],
    "the test designer's near misses and the other roles": [
        ("the integrated code", TD, "Bash", b("git show w2/integrate:src/gov/g14/impl.py; cat src/gov/g14/impl.py"),
         "allow"),
        ("the shared conftest ((c3))", TD, "Read", {"file_path": ENG + "/tests/conftest.py"}, "allow"),
        ("its own acceptance tests", TD, "Read", {"file_path": f"{P}/{T}"}, "allow"),
        ("the orchestrator reads the tests", O, "Read", {"file_path": f"{P}/{T}"}, "allow"),
        ("an auditor reads the tests", A, "Bash", b(f"cat {T}"), "allow"),
    ],
}


@pytest.mark.parametrize("case", G14_REFUSED, ids=[c[0] for c in G14_REFUSED])
def test_role_paths_refuses_a_true_read(projects, case):
    root = projects["patched"]
    name, role, tool, tin, _want, *more = case
    agent = more[0] if more else None
    got, why = hook(root, role, tool, _fill(tin, root), agent=agent)
    want = "engineer" if (agent or role) == E else TD
    assert got == "deny", (name, why)
    assert f"role_paths.{want}.reads_denied" in why and "DEC-1052 G-14" in why and ENG not in why, why


@pytest.mark.parametrize("form", list(G14_PASSED))
def test_role_paths_lets_a_near_miss_through(projects, form):
    check(projects["patched"], G14_PASSED[form])


def test_with_no_role_paths_section_there_is_no_check(projects):
    check(projects["absent"], [G14_REFUSED[0][:4] + ("allow",), G14_REFUSED[6][:4] + ("allow",)])


LINKED = [  # (name, ticket, file, want): the revised cases go with the ticket they test
    ("the case revised for it by Task:", "DAEO-g14t", "tests/acceptance/W2-G14U/test_u.py", "deny"),
    ("the case revised in its tests branch", "DAEO-g14t", "tests/acceptance/W2-G14U/test_v.py", "deny"),
    ("the other ticket's unrevised case", "DAEO-g14t", "tests/acceptance/W2-G14U/test_w.py", "allow"),
    ("W2-G14U's engineer, its own folder however revised", "DAEO-g14u", "tests/acceptance/W2-G14U/test_u.py", "deny"),
    ("a third ticket's engineer, the revised case", "DAEO-g14w", "tests/acceptance/W2-G14U/test_v.py", "allow"),
]


@pytest.mark.parametrize("name,ticket,rel,want", LINKED, ids=[c[0] for c in LINKED])
def test_the_link_sources_send_a_revised_case_with_its_ticket(projects, name, ticket, rel, want):
    root = projects["patched"]
    got, why = hook(root, E, "Read", {"file_path": f"{root}/{rel}"}, ticket=ticket)
    assert got == want, (name, why)
    if want == "deny":
        assert "role_paths.engineer.reads_denied" in why and "could not be worked out" not in why, why


def test_a_malformed_section_fails_closed_for_reads_only(projects):
    root = projects["malformed"]
    got, why = hook(root, O, "Bash", b("true"))
    assert got == "deny" and "role_paths" in why, why
    assert hook(root, O, "Write", {"file_path": root + "/src/gov/x.py", "content": "x"})[0] == "allow"


def test_a_conflict_inside_the_block_fails_closed_and_one_elsewhere_does_not(projects):
    got, why = hook(projects["conflict_in_block"], O, "Bash", b("true"))
    assert got == "deny" and "role_paths" in why, why
    root = projects["conflicted"]
    got, why = hook(root, E, "Read", {"file_path": f"{root}/{T}"})
    assert got == "deny" and "role_paths.engineer.reads_denied" in why, why
    assert hook(root, O, "Bash", b("git merge --abort"))[0] == "allow"


def _in_process(code, *args, cwd=None):
    p = subprocess.run(_py() + ["-c", code, str(HOOKS), *map(str, args)], capture_output=True, text=True,
                       timeout=60, env=_env(), cwd=cwd)
    assert p.stdout.strip().endswith("OK"), (p.stdout, p.stderr[-2000:])


UNREADABLE_LINKS = """
import sys
sys.path.insert(0, sys.argv[1])
import role_reads as rr
d = rr.expand(["{ticket_tests}"], "W2-G14T", [], "/x", main="/x", names={"DAEO-g14t"},
              links=lambda m, n, w: None)
j = rr.Judge("engineer", d, ["/x"])
own = j.hit("/x/tests/acceptance/W2-G14T/test_a.py")
assert own and "could not be worked out from git" in j.reason(own), j.reason(own) if own else None
assert not j.hit("/x/tests/acceptance/W2-G14U/test_u.py")  # the fallback: its own folder only
print("OK")
"""


def test_an_unreadable_link_source_falls_back_to_the_own_folder_and_says_so(tmp_path):
    _in_process(UNREADABLE_LINKS, cwd=str(tmp_path))


STALE_CACHE = """
import sys, os, json, glob, tempfile
os.environ["TMPDIR"] = sys.argv[3]
tempfile.tempdir = None
sys.path.insert(0, sys.argv[1])
import role_reads as rr
main = sys.argv[2]
first = rr.linked_tests(main, {"DAEO-g14t", "W2-G14T"}, "W2-G14T")
assert first == {"tests/acceptance/W2-G14U/test_u.py", "tests/acceptance/W2-G14U/test_v.py"}, first
(cached,) = glob.glob(rr.LINK_CACHE + "/*.json")
data = json.load(open(cached))
rr._LINKS.clear()
rr._METHOD[:] = ["an-older-method"]
open(cached, "w").write(json.dumps({"key": data["key"], "files": []}))
assert rr.linked_tests(main, {"DAEO-g14t", "W2-G14T"}, "W2-G14T") == first
print("OK")
"""


def test_a_link_list_cached_by_an_older_method_is_never_read(projects, tmp_path):
    _in_process(STALE_CACHE, projects["patched"], tmp_path)


OWN_AND_TESTS_TREE = """
import sys
sys.path.insert(0, sys.argv[1])
import role_reads as rr
TD, ENG = "independent-test-designer", sys.argv[2]
allowed = ["src/gov/g14/impl.py", "src/gov/g14/two.py", "tests/unit/test_g14t*", "tests/conftest.py",
           "tests/acceptance/W2-G14T/test_a.py"]
# the engineer's own tree: only the files its branch changes are its new work
j = rr.Judge(TD, rr.expand(["{ticket_impl}"], "W2-G14T", allowed, ENG, changes=lambda own: {"src/gov/g14/impl.py"}), [])
assert j.hit(ENG + "/src/gov/g14/impl.py") and not j.hit(ENG + "/src/gov/g14/two.py")
assert not j.hit(ENG + "/src/gov/g14/impl.py", plain=True)  # another revision's version
unknown = rr.Judge(TD, rr.expand(["{ticket_impl}"], "W2-G14T", allowed, ENG, changes=lambda own: None), [])
assert not unknown.hit(ENG + "/src/gov/g14/impl.py")  # git cannot say: let through
# the designer's tests tree, forked from the ticket's head: the engineer's carried files
carried = {"src/gov/g14/impl.py", "tests/unit/test_g14t_a.py", "tests/conftest.py", "tests/acceptance/W2-G14T/test_a.py"}
t = rr.Judge(TD, rr.expand(["{ticket_impl}"], "W2-G14T", allowed, ENG + "-tests", changes=lambda own: set(),
                           tests_changes=lambda tree, wbs: carried), [])
W = ENG + "-tests/"
assert t.hit(W + "src/gov/g14/impl.py") and t.hit(W + "tests/unit/test_g14t_a.py")
assert not t.hit(W + "src/gov/g14/two.py") and not t.hit(W + "tests/conftest.py")
assert not t.hit(W + "tests/acceptance/W2-G14T/test_a.py")  # its own acceptance tests: never refused
print("OK")
"""


def test_the_designer_is_refused_only_the_engineer_s_changed_or_carried_files():
    _in_process(OWN_AND_TESTS_TREE, ENG)


READER_WORDS = """
import sys
sys.path.insert(0, sys.argv[1])
import role_reads as rr
ra = rr.Bash.reader_args
assert ra("grep", ["-rn", "pat", "a", "b"]) == ["a", "b"]
assert ra("grep", ["-f", "pats.txt", "a"]) == ["a", "pats.txt"]
assert ra("sed", ["-n", "1,5p", "f"]) == ["f"]
assert ra("cp", ["-t", "dest", "a"]) == ["a"]
assert ra("jq", ["--arg", "k", "v", ".", "f.json"]) == ["f.json"]
assert ra("cat", ["--", "-odd"]) == ["-odd"]
print("OK")
"""


def test_the_readers_words():
    _in_process(READER_WORDS)


# ---------------------------------------------------------------------------------------------------------------
# bash_writes.py beside the hook: what a command deletes and makes; the emptied word; the fallback
# ---------------------------------------------------------------------------------------------------------------

MODULE = """
import json, os, sys
sys.path.insert(0, sys.argv[1])
import bash_writes as bw
from gov.guard.decide import _expand_token, _extract_bash_write_targets
os.environ.pop("GOV_LIVE_HOOK_UNSET", None)
os.environ["GOV_LIVE_HOOK_SET"] = "/tmp/s"
assert bw.emptied("$GOV_LIVE_HOOK_UNSET/") == "/"
assert bw.emptied("${GOV_LIVE_HOOK_UNSET:-/tmp/d}/x") == "/tmp/d/x"
assert bw.emptied("$GOV_LIVE_HOOK_SET/$GOV_LIVE_HOOK_UNSET") == "/tmp/s/"
assert bw.emptied("${GOV_LIVE_HOOK_UNSET:?}/") is None
def judge(c):
    return bw.judge(c, "/r", _extract_bash_write_targets, _expand_token)
assert [tuple(x) for x in judge("rm -rf a /b").deletes] == [("a", "/r/a", "names"), ("/b", "/b", "names")]
assert [tuple(x) for x in judge("for d in x y; do rm -r /t/$d; done").deletes] == [
    ("/t/$d", "/t/x", "names"), ("/t/$d", "/t/y", "names")]
assert judge("cat <<'EOF' > /tmp/x\\nrm -rf /\\nEOF").deletes == [] and judge("echo rm -rf /").deletes == []
assert tuple(judge("rm -rf $(pwd)/").deletes[0])[1:] == ("/", "if-empty")
assert judge("mkdir -p a /b").made == ["/r/a", "/b"] and judge("D=/q; mkdir -p $D/e").made == ["/q/e"]
assert judge("mkdir $(pwd)/f").made == [] and judge("bash -c 'mkdir /h'").made == ["/h"]
text, bodies = bw.heredocs("cat > /tmp/x <<'EOF'\\nrm -rf /\\nEOF\\necho done")
assert "rm -rf" not in text and "echo done" in text and bodies[0]["text"] == "rm -rf /" and bodies[0]["quoted"]
for unreadable in ("cat <<EOF\\nx", "echo 'x"):
    try:
        bw.lift(bw.heredocs(unreadable)[0])
    except bw.Unreadable:
        continue
    raise AssertionError("read for certain: " + unreadable)
print("OK")
"""


def test_bash_writes_lists_deletes_and_folders_and_falls_back_when_unreadable():
    _in_process(MODULE)


# ---------------------------------------------------------------------------------------------------------------
# The logged refusals (guard-refusals.jsonl), replayed from the CTO's rebuilt corpus when it is here
# ---------------------------------------------------------------------------------------------------------------

def _main_tree():
    common = subprocess.run(["git", "-C", str(TREE), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            capture_output=True, text=True).stdout.strip()
    return os.path.dirname(common.rstrip("/")) if common else str(TREE)


CORPUS = os.environ.get("GOV_LIVE_HOOK_CORPUS") or os.path.join(
    _main_tree(), ".gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/work/corpus4.json")
# Rows 50-53 carry no tool_use id: replayed as their twins. Still refused since ACT-D8: row 64 (rule 4, a heredoc
# whose text holds "sudo") and row 80 (the hidden folder named by its path).
TWIN = {50: 54, 51: 55, 52: 58, 53: 59}
ROLE = {**{i: O for i in (61, 62, 63, 70, 71, 72)}, **{i: A for i in (64, 67, 68, 69, 75, 76)},
        **{i: E for i in (65, 66, 73, 74, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86)}}
STILL_REFUSED = [64, 80]


@pytest.mark.skipif(not os.path.exists(CORPUS), reason="the rebuilt corpus is not here (GOV_LIVE_HOOK_CORPUS)")
def test_the_logged_refusals_replay_as_decided():
    import re
    rows = json.load(open(CORPUS))
    main = _main_tree()
    refused = []
    for row in rows:
        src = rows[TWIN.get(row["i"], row["i"])]
        role = (src.get("launch_role") if src.get("from") == "fix-3 corpus" else ROLE.get(src["i"])) or O
        cwd = src.get("cwd") or main
        m = re.match(re.escape(WORKTREES) + r"/[^/]+", cwd)
        event = {"tool_name": src["tool"], "tool_input": src["input"], "cwd": cwd, "session_id": "live-hook",
                 "agent_type": src.get("agent_type")}
        env = _env({"GOV_ROLE": role, "GOV_TICKET": "DAEO-sdxk", "CLAUDE_PROJECT_DIR": m.group(0) if m else main})
        tmpdir = src.get("tmpdir")
        if tmpdir is None and src.get("from") != "fix-3 corpus":
            t = re.search(r"/tmp/gov-launch-[a-z-]+-[a-z0-9]{8}", json.dumps(src.get("input")))
            tmpdir = t.group(0) if t else None
        env.pop("TMPDIR", None)
        if tmpdir:
            env["TMPDIR"] = tmpdir
        p = subprocess.run(_py() + [str(HOOK)], input=json.dumps(event), capture_output=True, text=True, env=env,
                           timeout=90)
        decision = "deny" if p.returncode == 2 else (
            json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"] if p.stdout.strip() else "allow")
        if decision != "allow":
            refused.append(row["i"])
    assert sorted(refused) == STILL_REFUSED, refused
